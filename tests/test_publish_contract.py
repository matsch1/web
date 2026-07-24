import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PublishContractTests(unittest.TestCase):
    @staticmethod
    def verifier_module():
        path = ROOT / "scripts" / "verify_site.py"
        spec = importlib.util.spec_from_file_location("verify_site", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

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

    def test_homepage_identity_is_visible_in_title_and_heading(self):
        head = (ROOT / "layouts" / "partials" / "head.html").read_text()
        de_home = (ROOT / "content" / "_index.de.md").read_text()
        self.assertIn('<title>{{ if .Title }}{{ .Title }} | {{ end }}{{ site.Title }}</title>', head)
        self.assertIn('title: Zwischen Terminal und Trampelpfad', de_home)
        self.assertIn('# Zwischen Terminal und Trampelpfad', de_home)
        self.assertNotIn('ohne Schnickschnack', de_home)

    def test_social_metadata_uses_correct_mime_types_and_localized_cards(self):
        head = (ROOT / "layouts" / "partials" / "head.html").read_text()
        self.assertIn('{{ $img.MediaType.Type }}', head)
        self.assertNotIn('{{ $img.MediaType.Type }}/{{ $img.MediaType.SubType }}', head)
        self.assertIn('social-de.png', head)
        self.assertIn('social-en.png', head)

    def test_search_pages_are_not_indexable(self):
        head = (ROOT / "layouts" / "partials" / "head.html").read_text()
        self.assertIn('or (eq .Layout "search")', head)

    def test_search_pages_are_excluded_from_language_sitemaps(self):
        for language in ("de", "en"):
            search = ROOT / "content" / f"search.{language}.md"
            self.assertIn("sitemap:\n  disable: true", search.read_text())

    def test_raw_html_warning_sources_use_markdown_code_spans(self):
        expectations = {
            "content/blog/08_Giscus_comments/index.de.md": "Giscus-Tag `<script>` darin",
            "content/blog/08_Giscus_comments/index.en.md": "Giscus `<script>` tag inside",
            "content/projects/03_vps-coolify/index.de.md": "Dateien erstellt: `<ssh-key>` und `<ssh-key.pub>`.",
            "content/projects/03_vps-coolify/index.en.md": "files: `<ssh-key>` and `<ssh-key.pub>`.",
        }
        for relative_path, expected in expectations.items():
            self.assertIn(expected, (ROOT / relative_path).read_text())

    def test_third_party_gallery_assets_are_not_global(self):
        base = (ROOT / "layouts" / "_default" / "baseof.html").read_text()
        gallery = (ROOT / "layouts" / "shortcodes" / "galleries.html").read_text()
        self.assertNotIn("nanogallery2", base)
        self.assertNotIn("jquery@3.7.1", base)
        self.assertNotIn("nanogallery2", gallery)
        self.assertNotIn("jquery@3.7.1", gallery)

    def test_default_social_cards_exist_with_declared_png_dimensions(self):
        for filename in ("social-de.png", "social-en.png"):
            card = ROOT / "static" / filename
            self.assertTrue(card.is_file(), f"missing social card: {filename}")
            header = card.read_bytes()[:24]
            self.assertEqual(header[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", header[16:24]), (1200, 630))

    def test_default_social_card_metadata_is_png(self):
        head = (ROOT / "layouts" / "partials" / "head.html").read_text()
        self.assertIn(
            '{{ else }}\n  <meta property="og:image" content="{{ $defaultOGImage }}">\n'
            '  <meta property="og:image:type" content="image/png">',
            head,
        )

    def test_default_social_cards_use_the_active_language_base_url(self):
        head = (ROOT / "layouts" / "partials" / "head.html").read_text()
        self.assertIn('"social-de.png" "social-en.png"', head)
        self.assertIn("| absURL", head)

    def test_safari_pinned_tab_icon_exists(self):
        icon = ROOT / "static" / "safari-pinned-tab.svg"
        self.assertTrue(icon.is_file())
        self.assertIn("<svg", icon.read_text())

    def test_artifact_validator_checks_p0_assets(self):
        verifier = (ROOT / "scripts" / "verify_site.py").read_text()
        self.assertIn('"de/social-de.png"', verifier)
        self.assertIn('"en/social-en.png"', verifier)
        self.assertIn("safari-pinned-tab.svg", verifier)

    def test_artifact_validator_rejects_html_without_required_seo_metadata(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "missing.html"
            page.write_text("<html><head></head><body></body></html>")
            with self.assertRaises(SystemExit):
                verifier.validate_html_page(page, Path(directory), set())

    def test_artifact_validator_rejects_wrong_social_card_dimensions(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            card = Path(directory) / "social.png"
            card.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", 1, 1))
            with self.assertRaises(SystemExit):
                verifier.validate_social_card(card)

    def test_artifact_validator_rejects_truncated_social_card(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            card = Path(directory) / "social.png"
            card.write_bytes(
                b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x0dIHDR" + struct.pack(">II", 1200, 630)
            )
            with self.assertRaises(SystemExit):
                verifier.validate_social_card(card)

    def test_artifact_validator_rejects_wrong_social_metadata(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text('<meta property="og:image" content="https://blog.matschcode.de/en/social-en.png">')
            with self.assertRaises(SystemExit):
                verifier.validate_default_social_metadata(
                    page, "https://blog.matschcode.de/de/social-de.png"
                )

    def test_artifact_validator_rejects_empty_gallery_markup(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text('<div class="image-gallery"></div>')
            with self.assertRaises(SystemExit):
                verifier.validate_gallery(page)

    def test_artifact_validator_rejects_unpaired_social_metadata(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text(
                '<meta property="og:image" content="https://blog.matschcode.de/de/social-de.png">'
                '<meta property="og:image:type" content="image/jpeg">'
                '<meta property="og:image" content="https://example.test/other.png">'
                '<meta property="og:image:type" content="image/png">'
            )
            with self.assertRaises(SystemExit):
                verifier.validate_default_social_metadata(
                    page, "https://blog.matschcode.de/de/social-de.png"
                )

    def test_artifact_validator_rejects_empty_gallery_with_unrelated_item(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text(
                '<div class=image-gallery></div>'
                '<a class=image-gallery__item href=x><img src=x></a>'
            )
            with self.assertRaises(SystemExit):
                verifier.validate_gallery(page)

    def test_artifact_validator_rejects_gallery_item_without_own_image(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text(
                '<div class=image-gallery><a class=image-gallery__item href=x></a><span><img src=x></span></div>'
            )
            with self.assertRaises(SystemExit):
                verifier.validate_gallery(page)

    def test_artifact_validator_rejects_non_svg_xml_root(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            icon = Path(directory) / "safari-pinned-tab.svg"
            icon.write_text("<notsvg />")
            with self.assertRaises(SystemExit):
                verifier.validate_svg(icon)

    def test_artifact_validator_accepts_hugo_minified_gallery_markup(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text('<div class=image-gallery><a class=image-gallery__item href=x><img src=x alt="A loaded touring bike beside a canal"></a></div>')
            verifier.validate_gallery(page)

    def test_artifact_validator_rejects_gallery_image_without_alt_text(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "index.html"
            page.write_text('<div class=image-gallery><a class=image-gallery__item href=x><img src=x></a></div>')
            with self.assertRaises(SystemExit):
                verifier.validate_gallery(page)

    def test_artifact_validator_rejects_invalid_pinned_tab_svg(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            icon = Path(directory) / "safari-pinned-tab.svg"
            icon.write_text("not an svg")
            with self.assertRaises(SystemExit):
                verifier.validate_svg(icon)

    def test_gallery_shortcodes_render_images_without_javascript(self):
        galleries = (ROOT / "layouts" / "shortcodes" / "galleries.html").read_text()
        gallery = (ROOT / "layouts" / "shortcodes" / "gallery.html").read_text()
        self.assertIn('class="image-gallery"', galleries)
        self.assertIn('<figure', gallery)
        self.assertIn('<figcaption>', gallery)
        self.assertIn('Get "alt"', gallery)
        self.assertIn('<img', gallery)
        self.assertNotIn("data-ngthumb", gallery)

    def test_n8n_gallery_uses_localized_descriptive_alt_text(self):
        de = (ROOT / "content" / "projects" / "07_n8n_personal_assistant" / "index.de.md").read_text()
        en = (ROOT / "content" / "projects" / "07_n8n_personal_assistant" / "index.en.md").read_text()
        self.assertIn(
            'alt="n8n-Switch im Rules-Modus mit Regeln für voice.file_id, photo[3].file_id und message.text; die Ausgänge heißen Audio, Image und Text"',
            de,
        )
        self.assertIn(
            'alt="n8n Switch node in Rules mode with checks for voice.file_id, photo[3].file_id, and message.text; its outputs are named Audio, Image, and Text"',
            en,
        )
        self.assertNotIn('title="telegram_switch_settings"', de)
        self.assertNotIn('title="telegram_switch_settings"', en)


if __name__ == "__main__":
    unittest.main()
