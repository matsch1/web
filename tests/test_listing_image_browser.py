"""Optional local-artifact regressions for uncropped technical listing artwork.

EDITORIAL_BASE_URL and BROWSER_EXECUTABLE enable real Chromium verification.
LISTING_SCREENSHOT_DIR optionally records representative project/article cards.
"""
import os
from pathlib import Path
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise unittest.SkipTest('Playwright is optional; install it for browser checks') from exc

BASE_URL = os.environ.get('EDITORIAL_BASE_URL')
BROWSER = os.environ.get('BROWSER_EXECUTABLE')


@unittest.skipUnless(BASE_URL and BROWSER, 'Set local EDITORIAL_BASE_URL and BROWSER_EXECUTABLE')
class ListingImageBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=BROWSER, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_listing_covers_preserve_technical_art_and_photographic_crops(self):
        for lang in ('de', 'en'):
            for width in (320, 390, 768, 1280):
                for scheme in ('light', 'dark'):
                    page = self.browser.new_page(viewport={'width': width, 'height': 1000}, color_scheme=scheme)
                    try:
                        for section in ('projects', 'notes'):
                            response = page.goto(f'{BASE_URL}/{lang}/{section}/', wait_until='networkidle')
                            self.assertEqual(response.status, 200)
                            self.assertEqual(page.locator('html').get_attribute('data-theme'), scheme)
                            self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                            technical = travel = 0
                            for card in page.locator('article.post-entry:has(.entry-cover img)').all():
                                category = card.get_attribute('data-category')
                                is_technical = section == 'notes' or category in ('development', 'hardware', 'self-hosting')
                                image = card.locator('.entry-cover img')
                                image.scroll_into_view_if_needed()
                                image.evaluate('(e) => e.decode()')
                                metrics = image.evaluate('''e => {
                                    const r = e.getBoundingClientRect(), c = e.parentElement.getBoundingClientRect();
                                    return {ratio: r.width / r.height, natural: e.naturalWidth / e.naturalHeight,
                                        fit: getComputedStyle(e).objectFit, width: r.width, height: r.height,
                                        coverRatio: c.width / c.height, coverHeight: c.height,
                                        coverWidth: c.width, left: r.left, right: r.right};
                                }''')
                                identity = card.locator('.entry-link').get_attribute('href')
                                with self.subTest(lang=lang, width=width, scheme=scheme, entry=identity):
                                    self.assertGreater(metrics['width'], 0)
                                    self.assertGreater(metrics['natural'], 0)
                                    self.assertGreaterEqual(metrics['left'], 0)
                                    self.assertLessEqual(metrics['right'], width)
                                    if is_technical:
                                        technical += 1
                                        self.assertAlmostEqual(metrics['ratio'] / metrics['natural'], 1, delta=.01,
                                                               msg=f'Artwork must retain its natural ratio: {metrics}')
                                        self.assertEqual(metrics['fit'], 'contain')
                                        self.assertAlmostEqual(metrics['coverHeight'], metrics['height'], delta=1,
                                                               msg='No fixed crop box or artificial letterboxing')
                                        self.assertAlmostEqual(metrics['coverWidth'], metrics['width'], delta=1)
                                    elif category == 'travel':
                                        travel += 1
                                        self.assertAlmostEqual(metrics['coverRatio'], 1.5, delta=.01)
                                        self.assertEqual(metrics['fit'], 'cover')
                                screenshots = os.environ.get('LISTING_SCREENSHOT_DIR')
                                if screenshots and width in (390, 1280) and (identity.endswith('/n8n-ai-assistant/') or identity.endswith('/expose-k3s-services-via-vps/')):
                                    destination = Path(screenshots)
                                    destination.mkdir(parents=True, exist_ok=True)
                                    card.screenshot(path=str(destination / f'{lang}-{section}-{width}-{scheme}.png'))
                            self.assertGreater(technical, 0, 'Must exercise real technical covers, not an empty selector')
                            if section == 'projects':
                                self.assertEqual(technical, 6, 'Includes n8n, Obsidian, keyboard, Coolify, Shellmaster and GoalPacer')
                                self.assertEqual(travel, 3, 'Retain all intentional travel crops')
                    finally:
                        page.close()


if __name__ == '__main__':
    unittest.main()
