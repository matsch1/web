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
        self.assertIn("https://blog.matschcode.de/", root_artifacts)
        self.assertIn("og:title", root_artifacts)
        self.assertIn("content=\\\"matschcode\\\"", root_artifacts)
        self.assertIn("https://blog.matschcode.de/masthead.webp", root_artifacts)
        self.assertIn("twitter:image", root_artifacts)
        self.assertIn('Path("assets/images/masthead.webp")', root_artifacts)
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

    def test_homepage_is_a_curated_project_entrypoint(self):
        head = (ROOT / "layouts" / "_partials" / "head.html").read_text()
        listing = (ROOT / "layouts" / "list.html").read_text()
        homepage_sections = ROOT / "layouts" / "_partials" / "homepage_sections.html"

        self.assertIn('<title>{{ if and .Title (not .IsHome) }}{{ .Title }} | {{ end }}{{ site.Title }}</title>', head)
        self.assertIn('partial "homepage_sections.html" .', listing)
        self.assertTrue(homepage_sections.is_file())
        rendered = homepage_sections.read_text()
        for section in ("featured", "engineering", "outdoors", "archive"):
            self.assertIn(f'data-home-section="{section}"', rendered)
        self.assertIn('Params.homepage.state', rendered)
        self.assertIn('Params.homepage.section', rendered)
        self.assertIn('Params.homepage.featured', rendered)
        self.assertIn('relref $ "/projects/"', rendered)
        self.assertIn('$activeEngineeringProjects', rendered)
        self.assertIn('$activeOutdoorProjects', rendered)
        self.assertIn('after 3 $activeEngineeringProjects', rendered)
        self.assertIn('after 3 $activeOutdoorProjects', rendered)
        self.assertIn('$staleActiveProjects', rendered)
        self.assertIn('$homepageProjects', rendered)

        for language in ("de", "en"):
            homepage = ROOT / "content" / f"_index.{language}.md"
            projects = ROOT / "content" / "projects" / f"_index.{language}.md"
            self.assertTrue(homepage.is_file())
            self.assertTrue(projects.is_file())
            self.assertNotIn("redirect_to:", projects.read_text())
            self.assertNotIn("layout: redirect", projects.read_text())
            self.assertNotIn("sitemap:\n  disable: true", projects.read_text())

        projects = ROOT / "content" / "projects" / "_index.md"
        self.assertNotIn("redirect_to:", projects.read_text())
        self.assertNotIn("layout: redirect", projects.read_text())

    def test_header_exposes_the_language_local_rss_feed(self):
        header = (ROOT / "layouts" / "_partials" / "header.html").read_text()
        config = (ROOT / "hugo.toml").read_text()

        self.assertIn('home = ["HTML", "RSS", "JSON"]', config)
        self.assertIn('site.Home.OutputFormats.Get "RSS"', header)
        self.assertIn('class="rss-feed-link"', header)
        self.assertIn('href="{{ .RelPermalink }}"', header)

    def test_project_metadata_classifies_homepage_and_lifecycle_statuses(self):
        expected = {
            "content/projects/development/n8n-personal-assistant": ("engineering", "archive", False, "discontinued"),
            "content/projects/hardware/split-keyboard": ("engineering", "evergreen", True, "completed"),
            "content/projects/self-hosting/coolify-vps": ("engineering", "evergreen", False, "paused"),
            "content/projects/travel/2025-sweden/_index": ("outdoors", "evergreen", True, "completed"),
            "content/projects/travel/2018-iceland": ("outdoors", "evergreen", False, "completed"),
            "content/projects/travel/2023-denmark": ("outdoors", "active", False, "completed"),
            "content/projects/development/obsidian-http-mcp": ("engineering", "archive", False, "discontinued"),
            "content/projects/development/shellmaster": ("engineering", "archive", False, "discontinued"),
            "content/projects/development/goalpacer": ("engineering", "archive", False, "discontinued"),
        }
        for base, (section, state, featured, status) in expected.items():
            for suffix in ("", ".de", ".en"):
                path = ROOT / f"{base}/index{suffix}.md" if not base.endswith("_index") else ROOT / f"{base}{suffix}.md"
                content = path.read_text()
                self.assertIn(f"section: {section}", content, path)
                self.assertIn(f"state: {state}", content, path)
                self.assertIn(f"featured: {str(featured).lower()}", content, path)
                self.assertIn(f"project:\n  status: {status}", content, path)

    def test_project_status_is_optional_and_has_localized_rendering(self):
        status_partial = (ROOT / "layouts" / "_partials" / "project_status.html").read_text()
        card = (ROOT / "layouts" / "_partials" / "homepage_project_card.html").read_text()
        listing = (ROOT / "layouts" / "list.html").read_text()
        homepage = (ROOT / "layouts" / "_partials" / "homepage_sections.html").read_text()
        single = (ROOT / "layouts" / "single.html").read_text()
        styles = (ROOT / "assets" / "css" / "extended" / "thumbnail.css").read_text()

        self.assertIn('Param "project.status"', status_partial)
        self.assertIn('"active" "completed" "paused" "discontinued"', status_partial)
        self.assertIn('$activeLifecycleProjects := where $projectPages "Params.project.status" "active"', homepage)
        self.assertLess(homepage.index('data-home-section="active"'), homepage.index('data-home-section="featured"'))
        self.assertIn('Param "project.statusNote"', status_partial)
        self.assertIn('Param "project.successor"', status_partial)
        self.assertIn('project-status__icon', status_partial)
        self.assertIn('project_status_successor_link', status_partial)
        self.assertIn('partial "project_status.html" (dict "page" . "variant" "badge")', card)
        self.assertIn('partial "project_status.html" (dict "page" . "variant" "badge")', listing)
        self.assertIn('or (eq .Section "projects") (.Param "listAsProject")', listing)
        self.assertIn('partial "project_status.html" (dict "page" . "variant" "badge")', homepage)
        banner_call = 'partial "project_status.html" (dict "page" . "variant" "banner")'
        self.assertIn(banner_call, single)
        self.assertLess(single.index(banner_call), single.index('</header>'))
        self.assertIn('--project-status-color', styles)
        self.assertIn('.project-status__icon svg', styles)
        self.assertIn(".project-status--badge", styles)
        self.assertIn(".project-status--banner", styles)

        for language in ("de", "en"):
            translations = (ROOT / "i18n" / f"{language}.yaml").read_text()
            for status in ("active", "completed", "paused", "discontinued"):
                self.assertIn(f"id: project_status_{status}", translations)
            self.assertIn("id: project_status_successor_link", translations)

    def test_homepage_share_title_uses_the_site_name(self):
        expected_titles = {"de": "title: matschcode", "en": 'title: "matschcode"'}
        for language, expected_title in expected_titles.items():
            homepage = ROOT / "content" / f"_index.{language}.md"
            self.assertIn(expected_title, homepage.read_text())

    def test_projects_is_a_real_list_page_and_its_navigation_targets_it(self):
        for suffix in ("", ".de", ".en"):
            projects = ROOT / "content" / "projects" / f"_index{suffix}.md"
            self.assertNotIn("layout: redirect", projects.read_text())
            self.assertNotIn("redirect_to:", projects.read_text())

        self.assertFalse((ROOT / "layouts" / "projects" / "list.html").exists())

        config = (ROOT / "hugo.toml").read_text()
        projects_menu = config.split('identifier = "projects"', 1)[1].split('[[menu.main]]', 1)[0]
        self.assertIn('url = "/projects/"', projects_menu)

    def test_notes_and_projects_lists_can_be_filtered_by_category(self):
        listing = (ROOT / "layouts" / "list.html").read_text()
        filters = (ROOT / "assets" / "js" / "content-filters.js").read_text()

        self.assertIn('slice "development" "self-hosting" "sports"', listing)
        self.assertIn('slice "development" "self-hosting" "hardware" "travel"', listing)
        self.assertIn('data-category="{{ $category }}"', listing)
        self.assertIn('entry.hidden = !visible', filters)

    def test_project_list_cards_use_a_uniform_thumbnail_variant(self):
        listing = (ROOT / "layouts" / "list.html").read_text()
        thumbnails = (ROOT / "assets" / "css" / "extended" / "thumbnail.css").read_text()

        self.assertIn('$class = "post-entry project-entry"', listing)
        self.assertIn(".project-entry .entry-cover", thumbnails)
        self.assertIn("object-fit: cover", thumbnails)

    def test_category_filter_includes_the_homepage_first_entry(self):
        filters = (ROOT / "assets" / "js" / "content-filters.js").read_text()
        self.assertIn('document.querySelectorAll("[data-category]")', filters)

    def test_category_filter_ui_is_localized(self):
        listing = (ROOT / "layouts" / "list.html").read_text()
        self.assertIn('i18n "filter_by_category"', listing)
        self.assertIn('i18n "filter_all"', listing)
        self.assertIn('i18n "filter_empty"', listing)
        for language in ("de", "en"):
            translations = (ROOT / "i18n" / f"{language}.yaml").read_text()
            self.assertIn("id: filter_by_category", translations)
            self.assertIn("id: filter_all", translations)
            self.assertIn("id: filter_empty", translations)

    def test_section_translation_disclaimer_is_localized_and_rendered_after_listings(self):
        listing = (ROOT / "layouts" / "list.html").read_text()
        disclaimer_path = ROOT / "layouts" / "_partials" / "translation_disclaimer.html"
        self.assertTrue(disclaimer_path.exists())
        disclaimer = disclaimer_path.read_text()

        self.assertIn('partial "translation_disclaimer.html" .', listing)
        self.assertGreater(listing.index('partial "translation_disclaimer.html" .'), listing.index('<footer class="page-footer">'))
        self.assertIn('or .IsHome', disclaimer)
        self.assertIn('slice "notes" "about"', disclaimer)
        self.assertIn('i18n "translation_disclaimer"', disclaimer)

        for language, expected in (
            ("de", "Diese Website ist auf Deutsch und Englisch verfügbar."),
            ("en", "This website is available in German and English."),
        ):
            translations = (ROOT / "i18n" / f"{language}.yaml").read_text()
            self.assertIn("id: translation_disclaimer", translations)
            self.assertIn(expected, translations)
            self.assertIn("id: redirecting_to_projects", translations)
            self.assertIn("id: continue_to_projects", translations)

        for section in ("notes", "about"):
            for language_suffix in ("", ".de", ".en"):
                content = (ROOT / "content" / section / f"_index{language_suffix}.md").read_text()
                self.assertNotIn("originally written", content)
                self.assertNotIn("ursprünglich auf", content)

        for language_suffix in ("", ".de", ".en"):
            content = (ROOT / "content" / f"_index{language_suffix}.md").read_text()
            self.assertNotIn("originally written", content)
            self.assertNotIn("ursprünglich auf", content)

    def test_reorganized_content_uses_current_internal_project_urls(self):
        stale_urls = (
            "https://blog.matschcode.de/en/projects/coolify-vps-setup/",
            "https://blog.matschcode.de/en/projects/obsidian-http-mcp/",
        )
        sources = (
            "content/projects/development/n8n-personal-assistant/index.md",
            "content/projects/development/n8n-personal-assistant/index.de.md",
            "content/projects/development/n8n-personal-assistant/index.en.md",
            "content/notes/self-hosting/tailscale-public-domain/index.md",
            "content/notes/self-hosting/tailscale-public-domain/index.de.md",
            "content/notes/self-hosting/tailscale-public-domain/index.en.md",
        )
        for source in sources:
            content = (ROOT / source).read_text()
            for url in stale_urls:
                self.assertNotIn(url, content, source)

    def test_social_metadata_uses_page_image_or_the_site_logo(self):
        head = (ROOT / "layouts" / "_partials" / "head.html").read_text()
        self.assertIn('{{ $img.MediaType.Type }}', head)
        self.assertNotIn('{{ $img.MediaType.Type }}/{{ $img.MediaType.SubType }}', head)
        self.assertIn('$defaultOGImage := "home-logo-600.webp" | absURL', head)
        self.assertNotIn('social-de.png', head)
        self.assertNotIn('social-en.png', head)

    def test_social_metadata_uses_legacy_page_image_when_cover_is_absent(self):
        head = (ROOT / "layouts" / "_partials" / "head.html").read_text()
        self.assertIn('$pageImage := .Params.cover.image | default .Params.img', head)
        self.assertIn('$.Resources.GetMatch $pageImage', head)
        self.assertIn('<meta name="twitter:image" content="{{ $img.Permalink }}">', head)
        self.assertNotIn('partial "templates/opengraph.html" .', head)
        self.assertNotIn('partial "templates/twitter_cards.html" .', head)

    def test_search_pages_are_not_indexable(self):
        head = (ROOT / "layouts" / "_partials" / "head.html").read_text()
        self.assertIn('or (eq .Layout "search")', head)

    def test_search_pages_are_excluded_from_language_sitemaps(self):
        for language in ("de", "en"):
            search = ROOT / "content" / f"search.{language}.md"
            self.assertIn("sitemap:\n  disable: true", search.read_text())

    def test_raw_html_warning_sources_use_markdown_code_spans(self):
        expectations = {
            "content/notes/development/giscus-comments/index.de.md": "Giscus-Tag `<script>` darin",
            "content/notes/development/giscus-comments/index.en.md": "Giscus `<script>` tag inside",
            "content/projects/self-hosting/coolify-vps/index.de.md": "Dateien erstellt: `<ssh-key>` und `<ssh-key.pub>`.",
            "content/projects/self-hosting/coolify-vps/index.en.md": "files: `<ssh-key>` and `<ssh-key.pub>`.",
        }
        for relative_path, expected in expectations.items():
            self.assertIn(expected, (ROOT / relative_path).read_text())

    def test_third_party_gallery_assets_are_not_global(self):
        base = (ROOT / "layouts" / "baseof.html").read_text()
        gallery = (ROOT / "layouts" / "_shortcodes" / "galleries.html").read_text()
        self.assertNotIn("nanogallery2", base)
        self.assertNotIn("jquery@3.7.1", base)
        self.assertNotIn("nanogallery2", gallery)
        self.assertNotIn("jquery@3.7.1", gallery)

    def test_gallery_lightbox_uses_native_dialog_navigation_with_link_fallback(self):
        base = (ROOT / "layouts" / "baseof.html").read_text()
        gallery = (ROOT / "layouts" / "_shortcodes" / "gallery.html").read_text()
        lightbox = (ROOT / "assets" / "js" / "gallery-lightbox.js").read_text()

        self.assertIn('resources.Get "js/gallery-lightbox.js"', base)
        self.assertIn("defer", base)
        self.assertIn('href="{{ .Get "src" }}"', gallery)
        self.assertIn("window.HTMLDialogElement", lightbox)
        self.assertIn("dialog.showModal()", lightbox)
        self.assertIn("gallery-lightbox__previous", lightbox)
        self.assertIn("gallery-lightbox__next", lightbox)
        self.assertIn('event.key === "ArrowLeft"', lightbox)
        self.assertIn('event.key === "ArrowRight"', lightbox)

    def test_single_post_cover_opens_in_the_native_lightbox(self):
        cover = (ROOT / "layouts" / "_partials" / "cover.html").read_text()
        lightbox = (ROOT / "assets" / "js" / "gallery-lightbox.js").read_text()

        self.assertIn('class="post-cover-lightbox"', cover)
        self.assertIn('const cover = item.closest(".post-cover-lightbox")', lightbox)
        self.assertIn('event.target.closest(".post-cover-lightbox")', lightbox)

    def test_default_social_fallback_uses_the_site_logo(self):
        logo = ROOT / "static" / "home-logo-600.webp"
        self.assertTrue(logo.is_file(), "missing social fallback logo")
        self.assertGreater(logo.stat().st_size, 0)

    def test_default_social_logo_metadata_is_webp(self):
        head = (ROOT / "layouts" / "_partials" / "head.html").read_text()
        self.assertIn(
            '{{ else }}\n  <meta property="og:image" content="{{ $defaultOGImage }}">\n'
            '  <meta property="og:image:type" content="image/webp">',
            head,
        )

    def test_default_social_logo_uses_an_absolute_url(self):
        head = (ROOT / "layouts" / "_partials" / "head.html").read_text()
        self.assertIn('"home-logo-600.webp" | absURL', head)

    def test_safari_pinned_tab_icon_exists(self):
        icon = ROOT / "static" / "safari-pinned-tab.svg"
        self.assertTrue(icon.is_file())
        self.assertIn("<svg", icon.read_text())

    def test_artifact_validator_checks_logo_fallback_assets(self):
        verifier = (ROOT / "scripts" / "verify_site.py").read_text()
        self.assertIn('"de/home-logo-600.webp"', verifier)
        self.assertIn('"en/home-logo-600.webp"', verifier)
        self.assertIn("safari-pinned-tab.svg", verifier)

    def test_artifact_validator_rejects_missing_project_archive_page(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            with self.assertRaises(SystemExit):
                verifier.validate_projects_pages(public)

    def test_artifact_validator_rejects_project_archive_without_project_entries(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            for language in ("de", "en"):
                page = public / language / "projects" / "index.html"
                page.parent.mkdir(parents=True, exist_ok=True)
                page.write_text("<html><head></head><body><h1>Projects</h1></body></html>")
            with self.assertRaises(SystemExit):
                verifier.validate_projects_pages(public)

    def test_artifact_validator_accepts_indexable_localized_project_archive_pages(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            for language in ("de", "en"):
                page = public / language / "projects" / "index.html"
                page.parent.mkdir(parents=True, exist_ok=True)
                page.write_text(
                    f'<html><head><link rel="canonical" href="https://blog.matschcode.de/{language}/projects/"></head>'
                    f'<body><h1>Projects</h1><a href="/{language}/projects/example/">Example</a></body></html>'
                )
            verifier.validate_projects_pages(public)

    def test_artifact_validator_rejects_html_without_required_seo_metadata(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            page = Path(directory) / "missing.html"
            page.write_text("<html><head></head><body></body></html>")
            with self.assertRaises(SystemExit):
                verifier.validate_html_page(page, Path(directory), set())

    def test_artifact_validator_accepts_a_locale_only_page(self):
        verifier = self.verifier_module()
        with tempfile.TemporaryDirectory() as directory:
            public = Path(directory)
            page = public / "de" / "tags" / "n8n" / "index.html"
            page.parent.mkdir(parents=True)
            page.write_text(
                '<html><head>'
                '<link rel="canonical" href="https://blog.matschcode.de/de/tags/n8n/">'
                '<link rel="alternate" hreflang="de" href="https://blog.matschcode.de/de/tags/n8n/">'
                '<meta name="description" content="n8n posts">'
                '<meta property="og:title" content="n8n">'
                '<meta property="og:description" content="n8n posts">'
                '<meta property="og:url" content="https://blog.matschcode.de/de/tags/n8n/">'
                '<meta name="twitter:card" content="summary">'
                '<meta name="twitter:title" content="n8n">'
                '<meta name="twitter:description" content="n8n posts">'
                '</head><body></body></html>'
            )
            verifier.validate_html_page(page, public, set())

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
        galleries = (ROOT / "layouts" / "_shortcodes" / "galleries.html").read_text()
        gallery = (ROOT / "layouts" / "_shortcodes" / "gallery.html").read_text()
        self.assertIn('class="image-gallery"', galleries)
        self.assertIn('class="image-gallery__hero"', galleries)
        self.assertIn('class="image-gallery__strip"', galleries)
        self.assertIn('image-gallery-item', galleries)
        self.assertIn('image-gallery-item', gallery)
        self.assertIn('<figure', gallery)
        self.assertIn('<figcaption>', gallery)
        self.assertIn('Get "alt"', gallery)
        self.assertIn('<img', gallery)
        self.assertNotIn("data-ngthumb", gallery)

    def test_n8n_gallery_uses_explicit_descriptive_alt_text(self):
        source = (ROOT / "content" / "projects" / "development" / "n8n-personal-assistant" / "index.md").read_text()
        self.assertIn(
            'alt="n8n Switch node in Rules mode with checks for voice.file_id, photo[3].file_id, and message.text; its outputs are named Audio, Image, and Text"',
            source,
        )
        self.assertNotIn('title="telegram_switch_settings"', source)
        self.assertIn("translation_lock: true", source)

    def test_swedish_day_one_gallery_has_localized_explicit_alt_text(self):
        directory = ROOT / "content" / "projects" / "travel" / "2025-sweden" / "day1"
        expected = {
            "index.de.md": 'alt="Geschwungener Kiesweg durch Bäume neben einem schmalen Strand am blauen Meer."',
            "index.en.md": 'alt="Curving gravel path through trees beside a narrow beach and blue sea."',
            "index.md": 'alt="Geschwungener Kiesweg durch Bäume neben einem schmalen Strand am blauen Meer."',
        }
        for filename, first_alt in expected.items():
            gallery_lines = [line for line in (directory / filename).read_text().splitlines() if "{{< gallery" in line]
            self.assertEqual(len(gallery_lines), 5)
            self.assertTrue(all(' alt="' in line for line in gallery_lines))
            self.assertIn(first_alt, gallery_lines[0])
        source = (directory / "index.md").read_text()
        self.assertIn("translation_lock: true", source)


if __name__ == "__main__":
    unittest.main()
