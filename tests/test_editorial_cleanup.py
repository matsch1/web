"""Rendered regressions for the editorial/metadata cleanup."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get('HUGO_BIN') or shutil.which('hugo')

class Head(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.meta = {}
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            self.meta[attrs.get('name', attrs.get('property'))] = attrs.get('content', '')

@unittest.skipUnless(HUGO, 'Set HUGO_BIN for rendered cleanup checks')
class EditorialCleanup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HUGO is not None
        cls.temp = tempfile.TemporaryDirectory(prefix='editorial-cleanup-')
        cls.public = Path(cls.temp.name) / 'public'
        subprocess.run([HUGO, '--destination', str(cls.public), '--environment', 'production', '--minify'], cwd=ROOT, check=True, capture_output=True)
    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()
    def html(self, route):
        return (self.public / route / 'index.html').read_text()
    def test_categories_are_noindex_and_not_in_sitemaps(self):
        for lang in ('de', 'en'):
            head = Head(self.html(f'{lang}/categories'))
            self.assertIn('noindex', head.meta['robots'])
            sitemap = (self.public / lang / 'sitemap.xml').read_text()
            self.assertNotIn(f'/{lang}/categories/', sitemap)
    def test_technical_tag_display_names(self):
        for lang in ('de', 'en'):
            for slug, label in [('vps', 'VPS'), ('mcp', 'MCP'), ('github-actions', 'GitHub Actions')]:
                self.assertIn(f'<h1>{label}', self.html(f'{lang}/tags/{slug}'))
    def test_misspelled_tag_redirects_to_merged_obsidian(self):
        for lang in ('de', 'en'):
            alias = self.html(f'{lang}/tags/obsdian')
            self.assertIn('http-equiv=refresh', alias)
            self.assertIn(f'/{lang}/tags/obsidian/', alias)
            self.assertIn('obsidian-cloud-sync-setup', self.html(f'{lang}/tags/obsidian'))
            self.assertNotIn(f'/{lang}/tags/obsdian/', (self.public / lang / 'sitemap.xml').read_text())
    def test_explicit_concise_descriptions(self):
        for lang in ('de', 'en'):
            for route in ('about', 'projects/travel/2025-sweden/day8'):
                with self.subTest(lang=lang, route=route):
                    head = Head(self.html(f'{lang}/{route}'))
                    description = head.meta['description']
                    self.assertGreater(len(description), 50)
                    self.assertLessEqual(len(description), 180)
                    self.assertEqual(description, head.meta['og:description'])
                    self.assertEqual(description, head.meta['twitter:description'])

if __name__ == '__main__':
    unittest.main()
