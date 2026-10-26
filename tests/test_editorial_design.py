"""Editorial contracts against real production Hugo output (no provider calls)."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get('HUGO_BIN') or shutil.which('hugo')


class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []
        self.text = ''

    def select(self, tag=None, cls=None, **attrs):
        found = []
        for child in self.children:
            if ((tag is None or child.tag == tag)
                    and (cls is None or cls in child.attrs.get('class', '').split())
                    and all(child.attrs.get(k.replace('_', '-')) == v for k, v in attrs.items())):
                found.append(child)
            found.extend(child.select(tag, cls, **attrs))
        return found


class DOM(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.root = self.current = Node()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}:
            self.current = node

    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        node = self.current
        while node:
            node.text += data
            node = node.parent


@unittest.skipUnless(HUGO, 'Set HUGO_BIN to production Hugo Extended')
class EditorialDesign(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HUGO is not None
        cls.temp = tempfile.TemporaryDirectory(prefix='editorial-render-')
        cls.public = Path(cls.temp.name) / 'public'
        run = subprocess.run([HUGO, '--source', str(ROOT), '--destination', str(cls.public),
                              '--environment', 'production', '--minify'], capture_output=True, text=True)
        if run.returncode:
            raise RuntimeError(run.stdout + run.stderr)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def page(self, route):
        return DOM((self.public / route / 'index.html').read_text()).root

    def test_home_has_one_meaningful_intro_heading_without_breadcrumb(self):
        for lang, words in [('de', ['Software', 'Homelab', 'Rad']), ('en', ['software', 'homelab', 'cycling'])]:
            main = self.page(lang).select('main')[0]
            self.assertEqual(len(main.select('h1')), 1)
            self.assertNotEqual(main.select('h1')[0].text.strip(), 'matschcode')
            self.assertFalse(main.select(cls='breadcrumbs'))
            intro = main.select(cls='homepage-intro')[0]
            for word in words:
                self.assertIn(word, intro.text)
            self.assertLess(len(intro.text), 330)

    def test_navigation_is_localized_without_new_routes_or_notes_type(self):
        for lang, expected in [('de', ['Projekte', 'Beiträge', 'Über mich', 'Suche']),
                               ('en', ['Projects', 'Articles', 'About', 'Search'])]:
            nav = self.page(lang).select('ul', id='menu')[0]
            self.assertEqual([n.text.strip() for n in nav.select('a')], expected)
            self.assertTrue(nav.select('a')[1].attrs['href'].endswith(f'/{lang}/notes/'))
            listing = self.page(f'{lang}/notes')
            self.assertEqual(listing.select('h1')[0].text.strip(), expected[1])

    def test_home_has_exactly_one_lead_and_compact_mixed_recommendations(self):
        for lang in ['de', 'en']:
            main = self.page(lang).select('main')[0]
            self.assertEqual(len(main.select('article', 'editorial-lead')), 1)
            cards = main.select('article', 'homepage-project-card')
            article_cards = [c for c in cards if c.attrs.get('data-content-kind') == 'article']
            project_cards = [c for c in cards if c.attrs.get('data-content-kind') == 'project']
            self.assertTrue(article_cards)
            self.assertTrue(project_cards)
            links = [c.select('a', 'entry-link')[0].attrs['href'] for c in cards]
            self.assertEqual(len(links), len(set(links)))
            for card in cards:
                label = card.select(cls='content-kind')[0].text.strip()
                self.assertIn(label, ['Projekt', 'Beitrag'] if lang == 'de' else ['Project', 'Article'])
                if card in article_cards:
                    self.assertFalse(card.select(cls='project-status'))
                    self.assertIn(f'/{lang}/notes/', card.select('a', 'entry-link')[0].attrs['href'])
                else:
                    self.assertLessEqual(len(card.select('h3')[0].text.strip()), 65)
                    self.assertLessEqual(len(card.select(cls='entry-content')[0].text.strip()), 180)
            for section in main.select('section'):
                if section.attrs.get('data-home-section') not in ['active', 'archive']:
                    self.assertLessEqual(len(section.select('article')), 3)

    def test_lead_uses_large_image_slot_and_technical_covers_are_not_cropped(self):
        for lang in ['de', 'en']:
            main = self.page(lang).select('main')[0]
            lead = main.select('article', 'editorial-lead')[0]
            self.assertIn('510px', lead.select('img')[0].attrs.get('sizes', ''))
            self.assertIn('homepage-project-card--graphic', lead.attrs.get('class', ''))
            css = (ROOT / 'assets/css/extended/z-editorial.css').read_text()
            self.assertIn('.homepage-project-card--graphic .entry-cover img', css)
            self.assertIn('object-fit: contain', css)

    def test_all_page_types_keep_landscape_header(self):
        for lang in ['de', 'en']:
            routes = [lang, f'{lang}/projects', f'{lang}/notes',
                      f'{lang}/about', f'{lang}/search']
            articles = sorted((self.public / lang / 'notes').rglob('*/index.html'))
            self.assertTrue(articles)
            routes.append(str(articles[0].parent.relative_to(self.public)))
            for route in routes:
                with self.subTest(route=route):
                    header = self.page(route).select('header', 'site-masthead')[0]
                    self.assertTrue(header.select('img', 'site-masthead__image'))
                    self.assertTrue(header.select(cls='site-masthead__overlay'))
                    self.assertFalse(header.select(cls='site-masthead__tagline'))
                    self.assertNotIn('site-masthead--compact', header.attrs['class'])

    def test_active_priority_and_single_status_semantics_with_real_fixture(self):
        assert HUGO is not None
        with tempfile.TemporaryDirectory(prefix='editorial-fixture-') as directory:
            site = Path(directory)
            for name in ['layouts', 'assets', 'static', 'themes', 'i18n']:
                (site / name).symlink_to(ROOT / name, target_is_directory=True)
            shutil.copy(ROOT / 'hugo.toml', site / 'hugo.toml')
            for lang in ['de', 'en']:
                sources = {
                    f'_index.{lang}.md': 'title: Home',
                    f'projects/_index.{lang}.md': 'title: Projects',
                    f'projects/active/index.{lang}.md': 'title: Active project\ndate: 2001-01-01\nhomepage:\n  state: archive\nproject:\n  status: active',
                    f'projects/lead/index.{lang}.md': 'title: Lead\ndate: 2025-01-01\nhomepage:\n  featured: true\n  section: engineering\n  state: evergreen\nproject:\n  status: discontinued\n  statusNote: Reviewed status note\n  successor: /projects/active/',
                    f'projects/lead/child/index.{lang}.md': 'title: Child article\nhiddenInProjectList: true\nproject:\n  status: completed',
                    f'notes/article/index.{lang}.md': 'title: Article\ndate: 2025-01-01\nproject:\n  status: completed',
                }
                for path, frontmatter in sources.items():
                    target = site / 'content' / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(f'---\n{frontmatter}\n---\nFixture body.')
            run = subprocess.run([HUGO, '--source', str(site), '--environment', 'production'], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            for lang in ['de', 'en']:
                main = DOM((site / f'public/{lang}/index.html').read_text()).root.select('main')[0]
                sections = main.select('section')
                self.assertEqual(sections[0].attrs.get('data-home-section'), 'active')
                self.assertIn('Active project', sections[0].text)
                self.assertNotIn('Child article', main.text)
                header = DOM((site / f'public/{lang}/projects/lead/index.html').read_text()).root.select('header', 'post-header')[0]
                self.assertEqual(len(header.select(cls='project-status')), 1)
                self.assertEqual(len(header.select(cls='project-metadata')), 1, 'Status belongs in subdued project metadata')
                status = header.select(cls='project-metadata')[0].select(cls='project-status')[0]
                self.assertIn('Reviewed status note', status.text)
                self.assertTrue(status.select('a')[0].attrs['href'].endswith(f'/{lang}/projects/active/'))
                self.assertFalse(status.select(cls='project-status__icon'))
                article = DOM((site / f'public/{lang}/notes/article/index.html').read_text()).root
                self.assertFalse(article.select(cls='project-status'))

    def test_editorial_tokens_include_both_schemes_and_responsive_card_contract(self):
        path = ROOT / 'assets/css/extended/z-editorial.css'
        self.assertTrue(path.is_file(), 'Editorial design layer is missing')
        css = path.read_text()
        for token in ['--theme: #f3f2ee', '--theme: #161e1b', '--accent: #285a43',
                      '--accent: #99c5a9', 'aspect-ratio: 3 / 2', 'object-fit: cover',
                      '.site-masthead--compact', '.editorial-lead', 'max-width: 70ch', ':focus-visible']:
            self.assertIn(token, css)

    def test_heading_font_is_local_licensed_and_delivered(self):
        css = '\n'.join(p.read_text() for p in self.public.rglob('*.css'))
        self.assertIn('font-family:Manrope', css.replace(' ', ''))
        self.assertIn('font-display:swap', css.replace(' ', ''))
        self.assertTrue((self.public / 'de/fonts/Manrope[wght].ttf').is_file())
        self.assertIn('SIL OPEN FONT LICENSE', (ROOT / 'static/branding/Manrope-OFL.txt').read_text())


if __name__ == '__main__':
    unittest.main()
