"""Homepage hierarchy and chronology regressions against real Hugo output."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from test_editorial_design import DOM

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get('HUGO_BIN') or shutil.which('hugo')

@unittest.skipUnless(HUGO, 'Hugo required')
class NewsFirst(unittest.TestCase):
    def test_homepage_hierarchy_and_complete_listings(self):
        assert HUGO is not None
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([HUGO, '--destination', directory, '--environment', 'production'], cwd=ROOT, check=True, capture_output=True)
            def page(route):
                return DOM((Path(directory)/route/'index.html').read_text()).root
            for lang, title in [('de', 'Neu im Blog'), ('en', 'New on the blog')]:
                sections = page(lang).select('main')[0].select('section')
                self.assertEqual([s.attrs.get('data-home-section') for s in sections], ['articles', 'featured'])
                self.assertEqual(sections[0].select('h2')[0].text.strip(), title)
                articles = sections[0].select('article')
                self.assertEqual(len(articles), 3)
                self.assertIn('editorial-lead', articles[0].attrs['class'])
                listing = page(f'{lang}/notes').select('article')[:3]
                self.assertEqual([c.select('a', 'entry-link')[0].attrs['href'] for c in articles],
                                 [urlsplit(c.select('a', 'entry-link')[0].attrs['href']).path for c in listing])
                focus = sections[1].select('article')
                self.assertEqual(len(focus), 1)
                self.assertNotIn('editorial-lead', focus[0].attrs['class'])
                self.assertIn('hermes-agent', focus[0].select('a', 'entry-link')[0].attrs['href'])
                self.assertEqual(sections[1].select('header')[0].select('a')[0].attrs['href'], f'/{lang}/projects/')
                self.assertEqual(articles[0].select('a', 'entry-link')[0].attrs['href'], urlsplit(page(f'{lang}/notes').select('article')[0].select('a', 'entry-link')[0].attrs['href']).path)
                self.assertGreater(len(page(f'{lang}/projects').select('article')), len(focus))
