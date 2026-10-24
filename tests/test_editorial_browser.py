"""Optional real-browser layout checks against a freshly built, locally served site.

Run with EDITORIAL_BASE_URL=http://localhost:8876 and BROWSER_EXECUTABLE set,
after installing Playwright in the test environment. No production requests.
"""
import os
import unittest

BASE_URL = os.environ.get('EDITORIAL_BASE_URL')
BROWSER = os.environ.get('BROWSER_EXECUTABLE')


@unittest.skipUnless(BASE_URL and BROWSER, 'Set EDITORIAL_BASE_URL and BROWSER_EXECUTABLE for browser checks')
class EditorialBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=BROWSER, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_text_only_cards_keep_title_teaser_and_metadata_in_one_column(self):
        for width in (390, 1280):
            with self.subTest(width=width):
                page = self.browser.new_page(viewport={'width': width, 'height': 900})
                try:
                    page.goto(BASE_URL + '/de/', wait_until='networkidle')
                    # Exercise the supported no-cover state without changing editorial sources.
                    page.locator('.homepage-project-card:not(.editorial-lead) .entry-cover').first.evaluate('(e) => e.remove()')
                    cards = page.locator('.homepage-project-card:not(:has(.entry-cover))')
                    self.assertGreater(cards.count(), 0)
                    for card in cards.all():
                        lefts = card.evaluate('(e) => [...e.children].filter(c => !c.matches(".entry-link")).map(c => c.getBoundingClientRect().left)')
                        self.assertLess(max(lefts) - min(lefts), 2, 'Text-only card must not put title and teaser side by side')
                finally:
                    page.close()

    def test_about_portrait_preserves_natural_aspect_ratio(self):
        for lang in ('de', 'en'):
            for width in (320, 390, 768, 1280):
                with self.subTest(lang=lang, width=width):
                    page = self.browser.new_page(viewport={'width': width, 'height': 900})
                    try:
                        page.goto(BASE_URL + '/' + lang + '/about/', wait_until='domcontentloaded')
                        image = page.locator('.post-content figure.right img').first
                        image.scroll_into_view_if_needed()
                        image.evaluate('(e) => e.decode()')
                        ratio_error = image.evaluate('(e) => Math.abs((e.getBoundingClientRect().width / e.getBoundingClientRect().height) / (e.naturalWidth / e.naturalHeight) - 1)')
                        self.assertLess(ratio_error, 0.01, 'Portrait must scale its height with its responsive width')
                    finally:
                        page.close()

    def test_standard_homepage_cards_have_substantial_image_area(self):
        for width in (320, 390, 768, 1280):
            with self.subTest(width=width):
                page = self.browser.new_page(viewport={'width': width, 'height': 900})
                try:
                    page.goto(BASE_URL + '/de/', wait_until='networkidle')
                    cards = page.locator('.homepage-project-card:not(.editorial-lead):has(.entry-cover)')
                    self.assertGreater(cards.count(), 0)
                    for card in cards.all():
                        cover = card.locator('.entry-cover')
                        self.assertGreater(cover.bounding_box()['width'] / card.bounding_box()['width'], .85 if width < 700 else .35)
                        if width < 700:
                            image_box = cover.bounding_box()
                            self.assertGreaterEqual(card.locator('.entry-header').bounding_box()['y'], image_box['y'] + image_box['height'])
                finally:
                    page.close()

    def test_localized_layouts_have_no_overflow_and_fonts_load(self):
        routes = ('/', '/projects/', '/notes/', '/projects/travel/2023-denmark/')
        for lang in ('de', 'en'):
            for width in (320, 390, 768, 1280):
                for scheme in ('light', 'dark'):
                    with self.subTest(lang=lang, width=width, scheme=scheme):
                        page = self.browser.new_page(viewport={'width': width, 'height': 900}, color_scheme=scheme)
                        try:
                            for route in routes:
                                response = page.goto(BASE_URL + '/' + lang + route, wait_until='networkidle')
                                self.assertEqual(response.status, 200)
                                page.evaluate('document.fonts.ready')
                                self.assertTrue(page.evaluate('document.fonts.check("700 20px Manrope")'))
                                self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'), route)
                                if route == '/':
                                    self.assertEqual(page.locator('.editorial-lead').count(), 1)
                                else:
                                    self.assertLess(page.locator('.site-masthead').bounding_box()['height'], 170)
                        finally:
                            page.close()


if __name__ == '__main__':
    unittest.main()
