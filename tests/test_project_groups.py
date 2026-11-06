"""Rendered DE/EN project groups; dates, lifecycle and eligibility stay independent."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
from test_editorial_design import DOM

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get('HUGO_BIN') or shutil.which('hugo')
BROWSER = os.environ.get('BROWSER_EXECUTABLE') or os.environ.get('AGENT_BROWSER_EXECUTABLE_PATH')

@unittest.skipUnless(HUGO, 'Set HUGO_BIN to production Hugo')
class ProjectGroups(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HUGO is not None
        cls.temp = tempfile.TemporaryDirectory(prefix='project-groups-')
        cls.source = Path(cls.temp.name) / 'source'
        cls.source.mkdir()
        for name in ('layouts', 'assets', 'static', 'themes', 'i18n'):
            (cls.source / name).symlink_to(ROOT / name, target_is_directory=True)
        (cls.source / 'hugo.toml').write_text((ROOT / 'hugo.toml').read_text() + '\n[pagination]\npagerSize = 2\n')
        fixtures = {
            'projects/_index': 'title: Projects',
            'projects/development/old/index': 'title: Old active\ndate: 2010-01-01\nproject:\n  status: active',
            'projects/self-hosting/new/index': 'title: New discontinued\ndate: 2024-01-01\nproject:\n  status: discontinued\nhomepage:\n  section: outdoors',
            'projects/hardware/middle/index': 'title: Middle paused\ndate: 2020-01-01\nproject:\n  status: paused',
            'projects/development/additive/index': 'title: Additive hosting\ndate: 2019-01-01\nfilter_categories: [self-hosting]',
            'projects/other/fallback/index': 'title: Unclassified fallback\ndate: 2018-01-01',
            'projects/travel/trip/_index': 'title: Trip overview\ndate: 2023-01-01\nlistAsProject: true\ncascade:\n  hiddenInProjectList: true\nproject:\n  status: completed',
            'projects/travel/trip/day/index': 'title: Hidden day\ndate: 2025-01-01',
            'projects/development/hidden/index': 'title: Hidden regular\ndate: 2025-01-01\nhiddenInProjectList: true',
            'projects/travel/older/index': 'title: Older trip\ndate: 2021-01-01\nhomepage:\n  section: engineering',
            'projects/sports/ride/index': 'title: Sports ride\ndate: 2022-01-01',
        }
        for lang in ('de', 'en'):
            for route, metadata in fixtures.items():
                path = cls.source / 'content' / f'{route}.{lang}.md'
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f'---\n{metadata}\n---\nFixture body.')
        cls.public = Path(cls.temp.name) / 'fixture-public'
        cls.real = Path(cls.temp.name) / 'real-public'
        for source, destination in ((cls.source, cls.public), (ROOT, cls.real)):
            subprocess.run([HUGO, '--source', str(source), '--destination', str(destination), '--environment', 'production', '--minify'], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def groups(self, public, lang):
        root = DOM((public / lang / 'projects/index.html').read_text()).root
        groups = root.select('section', **{'data-project-group': 'engineering'}) + root.select('section', **{'data-project-group': 'outdoors'})
        self.assertEqual(len(groups), 2, 'Both thematic groups must render on the first overview')
        self.assertEqual([g.select('h2')[0].text.strip() for g in groups],
                         ['Engineering & Systeme', 'Sport & Abenteuer'] if lang == 'de' else ['Engineering & Systems', 'Sport & Adventure'])
        for group in groups:
            self.assertEqual(group.attrs['aria-labelledby'], group.select('h2')[0].attrs['id'])
            self.assertTrue(all(len(c.select('h3')) == 1 and not c.select('h2') for c in group.select('article')))
        self.assertFalse(root.select(cls='pagination'))
        self.assertFalse((public / lang / 'projects/page/2/index.html').exists())
        return groups

    def test_fixture_complete_groups_sorted_by_date_without_global_pagination(self):
        for lang in ('de', 'en'):
            groups = self.groups(self.public, lang)
            self.assertEqual([[c.select('h3')[0].text.strip() for c in g.select('article')] for g in groups], [
                ['New discontinued', 'Middle paused', 'Additive hosting', 'Unclassified fallback', 'Old active'],
                ['Trip overview', 'Sports ride', 'Older trip']])
            cards = [c for g in groups for c in g.select('article')]
            self.assertEqual(len(cards), 8)
            self.assertNotIn('Hidden day', ''.join(g.text for g in groups))
            self.assertNotIn('Hidden regular', ''.join(g.text for g in groups))
            self.assertEqual(groups[0].select('article')[2].attrs['data-categories'], 'development self-hosting')
            for card in cards:
                self.assertTrue(urlsplit(card.select('a', 'entry-link')[0].attrs['href']).path.startswith(f'/{lang}/projects/'))
            self.assertIn('discontinued', groups[0].select('article')[0].select(cls='project-status')[0].attrs['class'])
            # Nested travel listing remains paginated and retains its h2 cards.
            nested = DOM((self.public / lang / 'projects/travel/trip/index.html').read_text()).root
            self.assertFalse(nested.select('section', **{'data-project-group': 'outdoors'}))
            self.assertTrue(nested.select('article')[0].select('h2'))

    def test_real_content_exact_membership_and_order(self):
        for lang in ('de', 'en'):
            groups = self.groups(self.real, lang)
            slugs = [[urlsplit(c.select('a', 'entry-link')[0].attrs['href']).path.rstrip('/').split('/')[-1] for c in g.select('article')] for g in groups]
            self.assertEqual(slugs, [
                ['hermes-agent', 'n8n-ai-assistant', 'obsidian-http-mcp', 'split-keyboard-ianmaclarty', 'coolify-vps-setup', 'building-shellmaster', 'goalpacer-pace-estimator'],
                ['2025-sweden', '2023-denmark', '2018-iceland']])

    @unittest.skipUnless(BROWSER, 'Set BROWSER_EXECUTABLE for real browser checks')
    def test_actual_controller_responsive_real_pages_and_sports_fixture(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise unittest.SkipTest('Playwright is not installed') from exc
        evidence = os.environ.get('PROJECT_GROUP_SCREENSHOTS')
        if evidence:
            Path(evidence).mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=BROWSER, args=['--no-sandbox'])
            try:
                for public, fixture in ((self.real, False), (self.public, True)):
                    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(public)))
                    thread = threading.Thread(target=server.serve_forever, daemon=True)
                    thread.start()
                    try:
                        for lang in ('de', 'en'):
                            for width in ((390,) if fixture else (320, 390, 768, 1280)):
                                for scheme in (('light',) if fixture else ('light', 'dark')):
                                    page = browser.new_page(viewport={'width': width, 'height': 900}, color_scheme=scheme)
                                    errors = []
                                    page.on('pageerror', lambda error: errors.append(str(error)))
                                    page.route('**/*', lambda route: route.continue_() if urlsplit(route.request.url).hostname == '127.0.0.1' else route.abort())
                                    page.goto(f'http://127.0.0.1:{server.server_port}/{lang}/projects/', wait_until='networkidle')
                                    page.evaluate("document.querySelectorAll('img').forEach(img => img.loading = 'eager')")
                                    page.evaluate("Promise.all([...document.images].map(img => img.decode().catch(() => {})))")
                                    page.evaluate('document.fonts.ready')
                                    self.assertEqual(page.locator('[data-project-group]:visible').count(), 2)
                                    self.assertEqual(page.locator('article:visible').count(), 8 if fixture else 10)
                                    self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (lang, width, scheme))
                                    # Preserve mobile title -> centered 70% cover -> teaser -> metadata.
                                    if not fixture and width < 700:
                                        for card in page.locator('article').all():
                                            header, cover, teaser, footer = [card.locator(selector).bounding_box() for selector in ('.entry-header', '.entry-cover', '.entry-content', '.entry-footer')]
                                            self.assertTrue(header and cover and teaser and footer)
                                            assert header and cover and teaser and footer
                                            self.assertLessEqual(header['y'] + header['height'], cover['y'] + 1)
                                            self.assertLessEqual(cover['y'] + cover['height'], teaser['y'] + 1)
                                            self.assertLessEqual(teaser['y'] + teaser['height'], footer['y'] + 1)
                                    if evidence and not fixture and width in (390, 1280):
                                        page.screenshot(path=str(Path(evidence) / f'{lang}-projects-{width}-{scheme}.png'), full_page=True)
                                    expected = {'development': 2, 'self-hosting': 2, 'hardware': 1, 'travel': 2, 'sports': 1} if fixture else {'development': 5, 'self-hosting': 2, 'hardware': 1, 'travel': 3}
                                    for category, count in expected.items():
                                        button = page.locator(f'[data-filter="{category}"]')
                                        button.focus()
                                        page.keyboard.press('Enter')
                                        self.assertEqual(button.get_attribute('aria-pressed'), 'true')
                                        self.assertEqual(page.locator('article:visible').count(), count)
                                        self.assertEqual(page.locator('[data-project-group]:visible').get_attribute('data-project-group'), 'outdoors' if category in ('travel', 'sports') else 'engineering')
                                        self.assertFalse(page.locator('.content-filter-empty').is_visible())
                                    page.locator('[data-filter="all"]').click()
                                    self.assertEqual(page.locator('[data-project-group]:visible').count(), 2)
                                    self.assertEqual(page.locator('article:visible').count(), 8 if fixture else 10)
                                    self.assertEqual(errors, [])
                                    page.close()
                    finally:
                        server.shutdown()
                        server.server_close()
                        thread.join()
            finally:
                browser.close()
