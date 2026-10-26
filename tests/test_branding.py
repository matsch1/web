"""Narrow contracts for the approved route-derived brand, independent of webfonts."""
from pathlib import Path
import struct
import tomllib
import unittest
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = '{http://www.w3.org/2000/svg}'


class BrandingTests(unittest.TestCase):
    def setUp(self):
        self.config = tomllib.loads((ROOT / 'hugo.toml').read_text())['params']
        self.directory = ROOT / 'static/branding'

    def test_exact_wordmark_is_decorative_and_contains_outlines_not_text(self):
        tree = ET.parse(ROOT / 'static' / self.config['label']['wordmark']).getroot()
        self.assertEqual(tree.get('aria-hidden'), 'true')
        self.assertEqual(tree.get('focusable'), 'false')
        self.assertEqual(tree.get('viewBox'), '0 0 796 156')
        self.assertEqual(len(tree.findall(f'.//{SVG}text')), 0)
        self.assertEqual(len(tree.findall(f'.//{SVG}image')), 0)
        self.assertEqual(len(tree.findall(f'.//{SVG}script')), 0)
        self.assertEqual(len(tree.findall(f'{SVG}g')[1].findall(f'{SVG}path')), 10)

    def test_route_keeps_thirteen_independent_days_and_local_quadratic_smoothing(self):
        root = ET.parse(self.directory / 'matschcode-jutland.svg').getroot()
        route = root.find(f'{SVG}g')
        assert route is not None
        self.assertEqual(route.get('stroke'), 'currentColor')
        self.assertEqual(route.get('stroke-width'), '8')
        paths = route.findall(f'{SVG}path')
        self.assertEqual(len(paths), 13)
        self.assertTrue(any('Q' in path.get('d', '') for path in paths))
        self.assertTrue(all(path.get('d', '').startswith('M') for path in paths))
        self.assertFalse(any('Z' in path.get('d', '') for path in paths))

    def test_wordmark_route_moves_four_pixels_at_desktop_header_size(self):
        root = ET.parse(self.directory / 'matschcode-jutland.svg').getroot()
        route = root.find(f'{SVG}g')
        self.assertEqual(route.get('transform'), 'translate(13.724 0)')

    def test_standalone_route_is_centered_in_its_viewbox(self):
        root = ET.parse(self.directory / 'jutland-route.svg').getroot()
        self.assertEqual(root.find(f'{SVG}g').get('transform'),
                         'translate(16.113 -0.7025)')

    def test_square_icon_svg_centers_the_visible_route(self):
        root = ET.parse(self.directory / 'jutland-favicon.svg').getroot()
        self.assertEqual(root.find(f'{SVG}g').get('transform'),
                         'translate(48.113 17.2975)')

    def test_raster_icon_visible_bounds_are_centered(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest('Pillow is required for raster geometry checks')
        for size in [16, 32, 48, 180, 192]:
            with self.subTest(size=size):
                image = Image.open(self.directory / f'jutland-icon-{size}.png').convert('RGB')
                # Select the green route, not antialiased warm background edges.
                pixels = image.load()
                points = [(x, y) for y in range(size) for x in range(size)
                          if pixels[x, y][0] < 170 and
                          pixels[x, y][1] - pixels[x, y][0] > 10]
                self.assertTrue(points)
                for axis in [0, 1]:
                    center = (min(p[axis] for p in points) +
                              max(p[axis] for p in points) + 1) / 2
                    self.assertLessEqual(abs(center - size / 2), 0.5)

    def test_accessible_link_uses_brand_name_without_duplicate_visible_label(self):
        header = (ROOT / 'layouts/_partials/header.html').read_text()
        self.assertIn('aria-label="{{ $label_text }}"', header)
        self.assertIn('if site.Params.label.wordmark', header)
        self.assertIn('os.ReadFile (printf "static/%s" site.Params.label.wordmark) | safeHTML', header)
        self.assertNotIn('icon', self.config['label'])

    def test_all_configured_brand_icons_exist_and_png_dimensions_match(self):
        for key in ['favicon', 'favicon16x16', 'favicon32x32', 'apple_touch_icon', 'safari_pinned_tab']:
            self.assertTrue((ROOT / 'static' / self.config['assets'][key]).is_file(), key)
        for size in [16, 32, 180]:
            raw = (self.directory / f'jutland-icon-{size}.png').read_bytes()
            self.assertEqual(raw[:8], b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II', raw[16:24]), (size, size))

    def test_social_fallback_is_new_and_legacy_originals_are_retained(self):
        image = ROOT / 'static' / self.config['brandSocialImage']
        self.assertEqual(image.read_bytes()[8:12], b'WEBP')
        self.assertTrue((ROOT / 'static/home-logo-300.webp').is_file())
        self.assertTrue((ROOT / 'static/home-logo-600.webp').is_file())
        self.assertIn('SIL OPEN FONT LICENSE', (self.directory / 'Manrope-OFL.txt').read_text())


if __name__ == '__main__':
    unittest.main()
