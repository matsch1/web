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

    def test_deploy_only_runs_after_a_successful_translation(self):
        workflow = (ROOT / ".github" / "workflows" / "deploy.yml").read_text()
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow)
        self.assertIn("hugo-version: '0.146.0'", workflow)
        self.assertIn("cp ./public/de/robots.txt ./public/robots.txt", workflow)
        self.assertIn("contents: write", workflow)

    def test_translation_workflow_fails_loudly_and_is_reproducible(self):
        workflow = (ROOT / ".github" / "workflows" / "translate.yml").read_text()
        self.assertIn("actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97", workflow)
        self.assertIn("pip install -r requirements.txt", workflow)
        self.assertNotIn("continue-on-error", workflow)
        self.assertNotIn("staging", workflow)
        self.assertIn("contents: write", workflow)

    def test_open_street_map_shortcode_accepts_coordinates_without_zoom(self):
        shortcode = (ROOT / "layouts" / "shortcodes" / "open-street-map.html").read_text()
        self.assertIn("if gt (len $lonParts) 1", shortcode)
        self.assertIn('$zoom := "15"', shortcode)
        self.assertIn('{{ $geoLink := replace $geoLink "geo:" "" }}', shortcode)


if __name__ == "__main__":
    unittest.main()
