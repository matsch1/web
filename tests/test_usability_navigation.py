"""Local rendered/real-browser regressions for search and canonical project lists."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import unittest

from test_editorial_design import DOM

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get('HUGO_BIN') or shutil.which('hugo')
BROWSER = os.environ.get('BROWSER_EXECUTABLE') or os.environ.get('AGENT_BROWSER_EXECUTABLE_PATH')


@unittest.skipUnless(HUGO, 'Set HUGO_BIN for rendered navigation checks')
class UsabilityNavigation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HUGO is not None
        cls.temp = tempfile.TemporaryDirectory(prefix='usability-navigation-')
        cls.source = Path(cls.temp.name) / 'source'
        cls.source.mkdir()
        for directory in ('layouts', 'assets', 'i18n', 'themes', 'static'):
            (cls.source / directory).symlink_to(ROOT / directory, target_is_directory=True)
        (cls.source / 'hugo.toml').write_text((ROOT / 'hugo.toml').read_text() + '\n[pagination]\npagerSize = 3\n')
        # Dates must win over lifecycle status and homepage prominence, including
        # archived, paused, and discontinued projects across pagination.
        cls.fixtures = [
            ('active-old', 2010, 'active', 'archive'),
            ('active-new', 2012, 'active', 'active'),
            ('completed', 2020, 'completed', 'active'),
            ('unclassified', 2019, '', ''),
            ('archived', 2024, 'completed', 'archive'),
            ('paused', 2023, 'paused', 'active'),
            ('discontinued', 2022, 'discontinued', 'active'),
        ]
        for lang in ('de', 'en'):
            content = cls.source / 'content'
            content.mkdir(exist_ok=True)
            (content / f'search.{lang}.md').write_text('---\ntitle: Search\nlayout: search\n---\n')
            section = content / 'projects'
            section.mkdir(exist_ok=True)
            (section / f'_index.{lang}.md').write_text('---\ntitle: Projects\n---\n')
            for slug, year, status, state in cls.fixtures:
                directory = section / 'development' / slug
                directory.mkdir(parents=True, exist_ok=True)
                extra = ('homepage:\n  title: Curated title\n  teaser: Clean teaser\n  state: archive\n'
                         if slug == 'active-old' else f'homepage:\n  state: "{state}"\n')
                (directory / f'index.{lang}.md').write_text(
                    f'---\ntitle: {slug}\ndate: {year}-01-01\n'
                    + ('summary: Clean summary fallback\n' if slug == 'unclassified' else f'description: Explicit description {slug}\n') +
                    f'project:\n  status: "{status}"\n{extra}---\nNoisy automatic body excerpt.\n')
            travel = content / 'projects' / 'travel' / 'trip'
            travel.mkdir(parents=True, exist_ok=True)
            (travel / f'_index.{lang}.md').write_text(
                '---\ntitle: Travel overview\ndate: 2018-01-01\nlistAsProject: true\n'
                'description: Travel overview description\n---\n')
        cls.public = Path(cls.temp.name) / 'public'
        run = subprocess.run([HUGO, '--source', str(cls.source), '--destination', str(cls.public),
                              '--environment', 'production', '--minify'], capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def page(self, route):
        return DOM((self.public / route / 'index.html').read_text()).root

    def test_project_dates_preserve_every_item_pagination_and_filters(self):
        for lang in ('de', 'en'):
            cards = []
            for route in (f'{lang}/projects', f'{lang}/projects/page/2', f'{lang}/projects/page/3'):
                page = self.page(route)
                self.assertEqual(len(page.select(cls='content-filters')), 1)
                entries = page.select('article', 'post-entry')
                self.assertTrue(all(c.attrs.get('data-category') in ('development', 'travel') for c in entries))
                cards.extend(entries)
            slugs = [c.select('a', 'entry-link')[0].attrs['href'].rstrip('/').split('/')[-1] for c in cards]
            self.assertEqual(slugs, ['archived', 'paused', 'discontinued', 'completed', 'unclassified', 'trip', 'active-new', 'active-old'])
            self.assertEqual(len(set(slugs)), len(self.fixtures) + 1)
            self.assertEqual(len(self.page(f'{lang}/projects').select('a', 'next')), 1)

    def test_cards_prefer_curated_copy_then_explicit_description_and_localized_link(self):
        for lang in ('de', 'en'):
            cards = [card for route in (f'{lang}/projects', f'{lang}/projects/page/2', f'{lang}/projects/page/3')
                     for card in self.page(route).select('article', 'post-entry')]
            old = next(c for c in cards if c.select('a', 'entry-link')[0].attrs['href'].endswith('/active-old/'))
            self.assertEqual(old.select('h2')[0].text.strip(), 'Curated title')
            self.assertEqual(old.select(cls='entry-content')[0].text.strip(), 'Clean teaser')
            for card in cards:
                self.assertNotIn('Noisy automatic', card.text)
                self.assertNotIn('post link to', card.select('a', 'entry-link')[0].attrs['aria-label'])
            self.assertIn('Explicit description archived', cards[0].text)
            fallback = self.page(f'{lang}/projects/page/2').select('article', 'post-entry')[1]
            self.assertEqual(fallback.select(cls='entry-content')[0].text.strip(), 'Clean summary fallback')

    def test_search_has_localized_label_instructions_and_live_region(self):
        for lang, label in [('de', 'Website durchsuchen'), ('en', 'Search this site')]:
            page = self.page(f'{lang}/search')
            field = page.select('input', id='searchInput')[0]
            self.assertEqual(field.attrs['aria-label'], label)
            status = page.select(id='searchStatus')[0]
            self.assertEqual(status.attrs['role'], 'status')
            self.assertEqual(status.attrs['aria-live'], 'polite')
            self.assertTrue(status.text.strip())
            self.assertEqual(field.attrs['aria-describedby'], 'searchStatus')

    @unittest.skipUnless(BROWSER, 'Set BROWSER_EXECUTABLE for real browser behavior')
    def test_search_states_keyboard_navigation_and_untrusted_titles(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise unittest.SkipTest('Playwright is not installed') from exc
        handler = partial(SimpleHTTPRequestHandler, directory=str(self.public))
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=BROWSER, args=['--no-sandbox'])
                try:
                    for lang, none, count in [('de', 'Keine Ergebnisse', '2 Ergebnisse'), ('en', 'No results', '2 results')]:
                        page = browser.new_page()
                        page.route('**/index.json', lambda route: route.fulfill(json=[
                            {'title': '<img src=x onerror=alert(1)> needle', 'permalink': f'/{lang}/safe-one/'},
                            {'title': 'needle second', 'permalink': f'/{lang}/safe-two/'},
                            {'title': 'needle malicious', 'permalink': 'javascript:alert(1)'}]))
                        page.goto(f'http://127.0.0.1:{server.server_port}/{lang}/search/', wait_until='networkidle')
                        field = page.locator('#searchInput')
                        initial = page.locator('#searchStatus').inner_text()
                        field.fill('zzzzzzzzzzzzzz')
                        page.wait_for_function('(text) => document.querySelector("#searchStatus").textContent.includes(text)', arg=none)
                        self.assertEqual(page.locator('#searchResults li').count(), 0)
                        field.fill('needle')
                        page.wait_for_function('(text) => document.querySelector("#searchStatus").textContent.includes(text)', arg=count)
                        self.assertEqual(page.locator('#searchResults li').count(), 2)
                        self.assertEqual(page.locator('#searchResults img').count(), 0)
                        field.press('ArrowDown')
                        self.assertTrue(page.locator('#searchResults a').nth(0).evaluate('(e) => e === document.activeElement'))
                        page.keyboard.press('ArrowDown')
                        self.assertTrue(page.locator('#searchResults a').nth(1).evaluate('(e) => e === document.activeElement'))
                        page.keyboard.press('ArrowUp')
                        page.keyboard.press('ArrowUp')
                        self.assertTrue(field.evaluate('(e) => e === document.activeElement'))
                        field.press('Escape')
                        self.assertEqual(field.input_value(), '')
                        self.assertEqual(page.locator('#searchStatus').inner_text(), initial)
                        field.fill('   ')
                        page.wait_for_timeout(200)
                        self.assertEqual(page.locator('#searchStatus').inner_text(), initial)
                        field.fill('second')
                        singular = '1 Ergebnis' if lang == 'de' else '1 result'
                        page.wait_for_function('(text) => document.querySelector("#searchStatus").textContent === text', arg=singular)
                        page.route('**/safe-two/', lambda route: route.fulfill(body='Local navigation target'))
                        field.press('ArrowDown')
                        page.keyboard.press('Enter')
                        page.wait_for_url('**/safe-two/')
                        page.goto(f'http://127.0.0.1:{server.server_port}/{lang}/projects/', wait_until='networkidle')
                        page.locator('[data-filter="travel"]').click()
                        self.assertEqual(page.locator('article.post-entry:visible').count(), 0)
                        page.locator('[data-filter="all"]').click()
                        self.assertEqual(page.locator('article.post-entry:visible').count(), 3)
                        page.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
