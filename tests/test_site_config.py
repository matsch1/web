from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SiteConfigurationTests(unittest.TestCase):
    def test_robots_allows_crawling_and_advertises_sitemap(self):
        robots = (ROOT / "layouts" / "robots.txt").read_text()
        self.assertIn("Allow: /", robots)
        self.assertIn("Sitemap: https://blog.matschcode.de/sitemap.xml", robots)
        self.assertNotIn("range .Pages", robots)
        self.assertNotIn("Disallow:", robots)

    def test_publish_runs_translation_then_build_then_deploy(self):
        workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        self.assertIn("python scripts/translate_markdown.py", workflow)
        self.assertIn("hugo-version: '0.146.0'", workflow)
        self.assertIn("python scripts/prepare_root_artifacts.py public", workflow)
        self.assertIn("python scripts/verify_site.py public", workflow)
        self.assertIn("contents: write", workflow)

    def test_publish_translation_gate_fails_loudly_and_is_reproducible(self):
        workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        self.assertIn("actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97", workflow)
        self.assertIn("pip install -r requirements.txt", workflow)
        self.assertNotIn("continue-on-error", workflow)
        self.assertNotIn("workflow_run", workflow)
        self.assertIn("contents: write", workflow)

    def test_root_redirect_uses_the_preferred_browser_language(self):
        from scripts.prepare_root_artifacts import ROOT_REDIRECT

        self.assertIn("navigator.languages", ROOT_REDIRECT)
        self.assertIn('startsWith("de")', ROOT_REDIRECT)
        self.assertIn("window.location.replace", ROOT_REDIRECT)
        self.assertNotIn('http-equiv="refresh"', ROOT_REDIRECT)
        self.assertIn('href="de/"', ROOT_REDIRECT)
        self.assertIn('href="en/"', ROOT_REDIRECT)

    def test_open_street_map_shortcode_accepts_coordinates_without_zoom(self):
        shortcode = (ROOT / "layouts" / "shortcodes" / "open-street-map.html").read_text()
        self.assertIn("if gt (len $lonParts) 1", shortcode)
        self.assertIn('$zoom := "15"', shortcode)
        self.assertIn('{{ $geoLink := replace $geoLink "geo:" "" }}', shortcode)


if __name__ == "__main__":
    unittest.main()
