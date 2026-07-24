from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublishContractTests(unittest.TestCase):
    def test_root_sitemap_index_and_robots_are_consistent(self):
        robots = (ROOT / "layouts" / "robots.txt").read_text()
        sitemap = (ROOT / "static" / "sitemap.xml").read_text()
        self.assertIn("Sitemap: https://blog.matschcode.de/sitemap.xml", robots)
        self.assertIn("https://blog.matschcode.de/de/sitemap.xml", sitemap)
        self.assertIn("https://blog.matschcode.de/en/sitemap.xml", sitemap)

    def test_root_redirect_is_language_aware_and_not_indexable(self):
        workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        root_artifacts = (ROOT / "scripts" / "prepare_root_artifacts.py").read_text()
        self.assertIn("navigator.languages", root_artifacts)
        self.assertIn('startsWith(\\\"de\\\")', root_artifacts)
        self.assertIn('\\\"de/\\\":\\\"en/\\\"', root_artifacts)
        self.assertNotIn("http-equiv=\\\"refresh\\\"", root_artifacts)
        self.assertIn("noindex,follow", root_artifacts)
        self.assertIn("https://blog.matschcode.de/de/", root_artifacts)
        self.assertIn("python scripts/prepare_root_artifacts.py public", workflow)

    def test_publish_is_a_single_atomic_pipeline(self):
        workflow = (ROOT / ".github" / "workflows" / "publish.yml").read_text()
        self.assertIn("python scripts/translate_markdown.py", workflow)
        self.assertIn("python scripts/verify_site.py public", workflow)
        self.assertIn("hugo --gc --minify", workflow)
        self.assertIn("git push origin HEAD:main", workflow)
        self.assertNotIn("workflow_run", workflow)

    def test_pull_requests_run_build_and_artifact_checks(self):
        workflow = (ROOT / ".github" / "workflows" / "seo-check.yml").read_text()
        self.assertIn("pull_request:", workflow)
        self.assertIn("hugo --gc --minify", workflow)
        self.assertIn("python scripts/verify_site.py public", workflow)

    def test_social_metadata_uses_correct_mime_types_and_localized_cards(self):
        head = (ROOT / "layouts" / "partials" / "head.html").read_text()
        self.assertIn('{{ $img.MediaType.Type }}', head)
        self.assertNotIn('{{ $img.MediaType.Type }}/{{ $img.MediaType.SubType }}', head)
        self.assertIn('social-de.png', head)
        self.assertIn('social-en.png', head)

    def test_search_pages_are_not_indexable(self):
        head = (ROOT / "layouts" / "partials" / "head.html").read_text()
        self.assertIn('or (eq .Layout "search")', head)

    def test_third_party_gallery_assets_are_not_global(self):
        base = (ROOT / "layouts" / "_default" / "baseof.html").read_text()
        gallery = (ROOT / "layouts" / "shortcodes" / "galleries.html").read_text()
        self.assertNotIn("nanogallery2", base)
        self.assertNotIn("jquery@3.7.1", base)
        self.assertIn("nanogallery2", gallery)
        self.assertIn("defer", gallery)


if __name__ == "__main__":
    unittest.main()
