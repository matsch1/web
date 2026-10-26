"""Compact homepage regression checks; run against a fresh local Hugo build.

EDITORIAL_BASE_URL and BROWSER_EXECUTABLE enable the optional browser cases.
"""
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = os.environ.get('EDITORIAL_BASE_URL')
BROWSER = os.environ.get('BROWSER_EXECUTABLE')


class HomepageStructure(unittest.TestCase):
    def test_sections_keep_discovery_hooks_without_redundant_intros(self):
        template = (ROOT / 'layouts/_partials/homepage_sections.html').read_text()
        self.assertNotIn('<p>', template)
        for section in ('active', 'featured', 'engineering', 'outdoors', 'articles', 'archive'):
            self.assertIn(f'data-home-section="{section}"', template)
        self.assertLess(template.index('data-home-section="active"'),
                        template.index('data-home-section="featured"'))
        self.assertIn('relref $ "/projects/"', template)
        self.assertIn('"notes/" | relLangURL', template)


@unittest.skipUnless(BASE_URL and BROWSER, 'Set EDITORIAL_BASE_URL and BROWSER_EXECUTABLE')
class UsabilityLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise unittest.SkipTest('Playwright is not installed') from exc
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=BROWSER, args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_compact_mobile_homepage_and_ergonomic_cards(self):
        for lang in ('de', 'en'):
            for width in (320, 390, 768, 1280):
                for scheme in ('light', 'dark'):
                    with self.subTest(lang=lang, width=width, scheme=scheme):
                        page = self.browser.new_page(viewport={'width': width, 'height': 844}, color_scheme=scheme)
                        try:
                            page.goto(f'{BASE_URL}/{lang}/', wait_until='networkidle')
                            page.evaluate('document.fonts.ready')
                            self.assertFalse(page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                            self.assertEqual(page.locator('.homepage-section__header p').count(), 0)
                            if page.locator('[data-home-section="active"]').count():
                                self.assertEqual(page.locator('[data-home-section]').first.get_attribute('data-home-section'), 'active')
                            self.assertEqual(page.locator('.editorial-lead').count(), 1)
                            if width == 390:
                                title_y = page.locator('.homepage-project-card[data-content-kind="project"] .entry-header h3').first.bounding_box()['y']
                                self.assertLessEqual(title_y, 650, f'First project title at {title_y}px')
                            controls = page.locator('.logo-switches .theme-toggle, .logo-switches .rss-feed-link, .logo-switches .lang-menu a')
                            for control in controls.all():
                                box = control.bounding_box()
                                self.assertGreaterEqual(box['width'], 43)
                                self.assertGreaterEqual(box['height'], 43)
                            # Brand and utility controls stay in one row, even at 320px.
                            brand = page.locator('.logo > a').bounding_box()
                            switches = page.locator('.logo-switches').bounding_box()
                            self.assertLess(abs((brand['y'] + brand['height'] / 2) -
                                                (switches['y'] + switches['height'] / 2)), 2)
                            for kind in ('project', 'article'):
                                cards = page.locator(f'.homepage-project-card[data-content-kind="{kind}"]')
                                self.assertGreater(cards.count(), 0)
                                for card in cards.all():
                                    for selector, minimum in (('.entry-content', 15), ('.entry-footer', 13), ('.content-kind', 13)):
                                        for node in card.locator(selector).all():
                                            self.assertGreaterEqual(node.evaluate('(e) => parseFloat(getComputedStyle(e).fontSize)'), minimum)
                                    cover = card.locator('.entry-cover')
                                    if not cover.count():
                                        continue
                                    image_box, card_box = cover.bounding_box(), card.bounding_box()
                                    self.assertGreater(image_box['width'] / card_box['width'], .85 if width < 700 else .35)
                                    if width < 700:
                                        self.assertGreaterEqual(card.locator('.entry-header').bounding_box()['y'], image_box['y'] + image_box['height'])
                                    if 'homepage-project-card--graphic' in card.get_attribute('class'):
                                        image = cover.locator('img')
                                        self.assertEqual(image.evaluate('(e) => getComputedStyle(e).objectFit'), 'contain')
                                        ratio_error = image.evaluate('(e) => Math.abs((e.clientWidth / e.clientHeight) / (e.naturalWidth / e.naturalHeight) - 1)')
                                        self.assertLess(ratio_error, .02, 'Technical artwork must keep its natural proportions without padded bars')
                        finally:
                            page.close()


if __name__ == '__main__':
    unittest.main()
