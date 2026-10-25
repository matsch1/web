"""Optional real-artifact mobile card contract and unchanged desktop baseline.

Set EDITORIAL_BASE_URL, BROWSER_EXECUTABLE and optionally CARD_BASELINE_URL
and CARD_SCREENSHOT_DIR. Uses no production requests.
"""
import os
from pathlib import Path
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise unittest.SkipTest('Playwright is optional') from exc

BASE = os.environ.get('EDITORIAL_BASE_URL')
BROWSER = os.environ.get('BROWSER_EXECUTABLE')
BASELINE = os.environ.get('CARD_BASELINE_URL')
METRICS = """e => {
 const box = n => { const r = n.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height}; };
 const cover = e.querySelector('.entry-cover'), img = cover?.querySelector('img');
 const style = getComputedStyle(e);
 return {card:box(e), inner:e.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight),
   header:box(e.querySelector('.entry-header')), content:box(e.querySelector('.entry-content')),
   footer:e.querySelector('.entry-footer') ? box(e.querySelector('.entry-footer')) : null,
   cover:cover ? box(cover) : null, image:img ? box(img) : null,
   natural:img ? img.naturalWidth/img.naturalHeight : null,
   sizes:img?.sizes, fit:img ? getComputedStyle(img).objectFit : null};
}"""


@unittest.skipUnless(BASE and BROWSER, 'Set local URL and browser executable')
class MobileCardBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(executable_path=BROWSER, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def prepare(self, page, url):
        self.assertEqual(page.goto(url, wait_until='networkidle').status, 200)
        page.evaluate('document.fonts.ready')
        for img in page.locator('.post-entry .entry-cover img').all():
            img.scroll_into_view_if_needed()
            img.evaluate('e => e.decode()')
        page.evaluate('scrollTo(0,0)')

    def test_overview_cards_and_desktop_baseline(self):
        for lang in ('de', 'en'):
            for width in (320, 390, 768, 1280):
                for scheme in ('light', 'dark'):
                    page = self.browser.new_page(viewport={'width': width, 'height': 1000}, color_scheme=scheme,
                                                 is_mobile=width < 700, device_scale_factor=1)
                    try:
                        for route in ('/', '/projects/', '/notes/'):
                            # Each route needs an isolated resource cache, just like the
                            # baseline page. Chromium may reuse a larger cached srcset
                            # variant from the homepage, whose rounded ratio differs.
                            page.close()
                            page = self.browser.new_page(viewport={'width': width, 'height': 1000}, color_scheme=scheme,
                                                         is_mobile=width < 700, device_scale_factor=1)
                            with self.subTest(lang=lang, width=width, scheme=scheme, route=route):
                                path = '/' + lang + route
                                self.prepare(page, BASE + path)
                                self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                                self.assertEqual(page.locator('html').get_attribute('data-theme'), scheme)
                                cards = page.locator('article.post-entry')
                                self.assertGreater(cards.count(), 0)
                                actual = cards.evaluate_all('(cards) => cards.map(' + METRICS + ')')
                                if width < 700:
                                    for m in actual:
                                        if m['cover']:
                                            self.assertAlmostEqual(m['cover']['w'] / m['inner'], .7, delta=.005)
                                            self.assertAlmostEqual(m['cover']['x'] + m['cover']['w']/2,
                                                                   m['card']['x'] + m['card']['w']/2, delta=1)
                                            self.assertGreaterEqual(m['cover']['y'] + .1, m['header']['y'] + m['header']['h'])
                                            self.assertGreaterEqual(m['content']['y'] + .1, m['cover']['y'] + m['cover']['h'])
                                            self.assertAlmostEqual(m['image']['w']/m['image']['h']/m['natural'], 1, delta=.01)
                                            self.assertAlmostEqual(m['cover']['h'], m['image']['h'], delta=1)
                                            self.assertEqual(m['fit'], 'contain')
                                            if m['sizes']:
                                                self.assertIn('70vw', m['sizes'])
                                        else:
                                            self.assertAlmostEqual(m['header']['x'], m['content']['x'], delta=1)
                                        if m['footer']:
                                            self.assertGreaterEqual(m['footer']['y'] + .1, m['content']['y'] + m['content']['h'])
                                elif BASELINE:
                                    reference = self.browser.new_page(viewport={'width':width,'height':1000}, color_scheme=scheme)
                                    try:
                                        self.prepare(reference, BASELINE + path)
                                        expected = reference.locator('article.post-entry').evaluate_all('(cards) => cards.map(' + METRICS + ')')
                                        # Resource hints differ, desktop rendering must not.
                                        for m in actual + expected:
                                            m.pop('sizes')
                                        self.assertEqual(actual, expected, 'Desktop card geometry must equal origin/main')
                                        self.assertEqual(page.locator('.site-masthead').bounding_box(), reference.locator('.site-masthead').bounding_box())
                                    finally:
                                        reference.close()
                                screenshots = os.environ.get('CARD_SCREENSHOT_DIR')
                                if screenshots:
                                    dest = Path(screenshots)
                                    dest.mkdir(parents=True, exist_ok=True)
                                    page.screenshot(path=str(dest / f'{lang}-{route.strip("/") or "home"}-{width}-{scheme}.png'), full_page=True)
                                if width < 700:
                                    # Exercise coverless fallback for every list type, including featured cards.
                                    cards.first.locator('.entry-cover').evaluate_all('nodes => nodes.forEach(e => e.remove())')
                                    m = cards.first.evaluate(METRICS)
                                    self.assertAlmostEqual(m['header']['x'], m['content']['x'], delta=1)
                                    self.assertGreaterEqual(m['content']['y'], m['header']['y'] + m['header']['h'])
                    finally:
                        page.close()


if __name__ == '__main__':
    unittest.main()
