"""Rendered Hugo contracts for responsive delivery; original assets stay untouched."""
import os
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get('HUGO_BIN') or shutil.which('hugo')

class Elements(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.nodes = []; self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))
    def select(self, tag, cls=None):
        return [a for t, a in self.nodes if t == tag and (cls is None or cls in a.get('class', '').split())]

def png(path, width, height):
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind + data))
    path.parent.mkdir(parents=True, exist_ok=True)
    pixels = b''.join(b'\0' + bytes([y % 256, 90, 140]) * width for y in range(height))
    path.write_bytes(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', width, height, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b''))

@unittest.skipUnless(HUGO, 'Set HUGO_BIN to the production Hugo Extended binary')
class ResponsiveImages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert HUGO is not None
        cls.temp = tempfile.TemporaryDirectory(); cls.site = Path(cls.temp.name)
        for directory in ('layouts/_partials', 'layouts/_shortcodes'):
            shutil.copytree(ROOT / directory, cls.site / directory)
        (cls.site / 'hugo.toml').write_text('baseURL="https://example.test/"\n[params.masthead]\nimage="images/masthead.png"\n')
        (cls.site / 'layouts/home.html').write_text('''<!doctype html><html><body>
{{ partial "header.html" . }}
{{ with site.GetPage "article" }}
<div id="single">{{ partial "cover.html" (dict "cxt" . "IsSingle" true "isHidden" false) }}</div>
<div id="card">{{ partial "cover.html" (dict "cxt" . "IsSingle" false "isHidden" false "sizes" "(min-width: 768px) 341px, calc(100vw - 58px)") }}</div>
{{ .Content }}{{ end }}</body></html>''')
        (cls.site / 'layouts/single.html').write_text('{{ .Content }}')
        png(cls.site / 'assets/images/masthead.png', 2400, 913)
        png(cls.site / 'content/article/photo.png', 1200, 800)
        png(cls.site / 'content/article/tiny.png', 100, 50)
        (cls.site / 'content/article/index.md').write_text('''---
title: Test
cover:
  image: photo.png
  alt: Original photo
---
{{< galleries >}}
{{< gallery src="photo.png" title="Hero" >}}
{{< gallery src="photo.png" title="Thumbnail" >}}
{{< /galleries >}}
{{< galleries >}}
{{< gallery src="photo.png" title="Second hero" >}}
{{< gallery src="tiny.png" title="Small" >}}
{{< /galleries >}}
{{< figure src="./photo.png" width="700" alt="Figure alt" class="right" link="https://example.org/" target="_blank" caption="A caption" >}}
{{< figure src="https://example.org/external.svg" width="200" alt="External" >}}
''')
        cls.build = subprocess.run([HUGO, '--source', str(cls.site), '--environment', 'production'], capture_output=True, text=True)
        cls.html = (cls.site / 'public/index.html').read_text() if cls.build.returncode == 0 else ''
        cls.dom = Elements(cls.html)
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()
    def setUp(self):
        self.assertEqual(self.build.returncode, 0, self.build.stdout + self.build.stderr)
    def test_masthead_is_prioritized_responsive_and_mobile_art_directed(self):
        img = self.dom.select('img', 'site-masthead__image')[0]
        self.assertEqual(img.get('fetchpriority'), 'high')
        self.assertEqual(img.get('loading'), 'eager')
        self.assertTrue(img.get('srcset')); self.assertEqual(img.get('sizes'), '100vw')
        self.assertTrue(img.get('width')); self.assertTrue(img.get('height'))
        mobile = self.dom.select('source')
        self.assertTrue(any('768px' in a.get('media', '') and '.webp ' in a.get('srcset', '') for a in mobile))
    def test_covers_use_webp_without_originals_in_srcset(self):
        images = [a for a in self.dom.select('img') if a.get('alt') == 'Original photo']
        self.assertEqual(len(images), 2)
        for a in images:
            self.assertTrue(a['src'].endswith('.webp'), a)
            self.assertNotIn('photo.png ', a.get('srcset', ''))
        self.assertEqual(images[1]['sizes'], '(min-width: 768px) 341px, calc(100vw - 58px)')
        self.assertTrue(any(a.get('href', '').endswith('/photo.png') for a in self.dom.select('a')))
    def test_each_gallery_has_large_lead_and_small_thumbnails(self):
        images = {a.get('alt'): a for a in self.dom.select('img')}
        for title in ('Hero', 'Second hero'):
            self.assertIn('720w', images[title].get('srcset', ''))
        for title in ('Thumbnail', 'Small'):
            self.assertNotIn('720w', images[title].get('srcset', ''))
            self.assertTrue(images[title]['src'].endswith('.webp'))
        self.assertIn('960w', images['Thumbnail'].get('srcset', ''))
        self.assertIn('(scripting: none)', images['Thumbnail'].get('sizes', ''))
        self.assertIn('15.00vw', images['Thumbnail'].get('sizes', ''))
        self.assertIn('100w', images['Small'].get('srcset', ''))
        links = self.dom.select('a', 'image-gallery__link')
        self.assertTrue(all(a['href'] in ('photo.png', 'tiny.png') for a in links))
    def test_local_figures_are_responsive_and_preserve_link_and_caption(self):
        img = next(a for a in self.dom.select('img') if a.get('alt') == 'Figure alt')
        self.assertTrue(img['src'].endswith('.webp'))
        self.assertTrue(img.get('srcset')); self.assertTrue(img.get('height'))
        self.assertIn('right', self.dom.select('figure')[-2].get('class', ''))
        self.assertIn('A caption', self.html)
        link = next(a for a in self.dom.select('a') if a.get('href') == 'https://example.org/')
        self.assertEqual(link.get('target'), '_blank')
        self.assertIn('noopener', link.get('rel', ''))
        external = next(a for a in self.dom.select('img') if a.get('alt') == 'External')
        self.assertEqual(external['src'], 'https://example.org/external.svg')
    def test_delivered_assets_exist_and_sources_are_preserved(self):
        for img in self.dom.select('img'):
            if img.get('src', '').startswith('/'):
                self.assertTrue((self.site / 'public' / img['src'].lstrip('/')).exists(), img)
        self.assertTrue((self.site / 'content/article/photo.png').exists())

if __name__ == '__main__': unittest.main()
