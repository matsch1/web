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
        self.assertIn("hugo-version: '0.164.0'", workflow)
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
        shortcode = (ROOT / "layouts" / "_shortcodes" / "open-street-map.html").read_text()
        self.assertIn("if gt (len $lonParts) 1", shortcode)
        self.assertIn('$zoom := "15"', shortcode)
        self.assertIn('{{ $geoLink := replace $geoLink "geo:" "" }}', shortcode)
        self.assertIn('{{ $zoom = replaceRE "^z=" "" (index $lonParts 1) }}', shortcode)
        self.assertNotIn('$zoom = index $lonParts 1 | replace "z=" ""', shortcode)

    def test_open_street_map_requires_explicit_activation_before_interaction(self):
        shortcode = (ROOT / "layouts" / "_shortcodes" / "open-street-map.html").read_text()
        css = (ROOT / "assets" / "css" / "extended" / "custom.css").read_text()

        self.assertIn('class="container my-4 map-embed"', shortcode)
        self.assertIn('class="map-embed__activate"', shortcode)
        self.assertIn('map.classList.add("map-embed--active")', shortcode)
        self.assertIn('.map-embed iframe', css)
        self.assertIn('pointer-events: none;', css)
        self.assertIn('.map-embed--active iframe', css)
        self.assertIn('pointer-events: auto;', css)

    def test_open_street_map_exposes_localized_copy_and_open_actions(self):
        shortcode = (ROOT / "layouts" / "_shortcodes" / "open-street-map.html").read_text()
        css = (ROOT / "assets" / "css" / "extended" / "custom.css").read_text()

        self.assertNotIn("View Larger Map", shortcode)
        self.assertIn('$copyCoordinatesLabel := "Copy coordinates"', shortcode)
        self.assertIn('$copyCoordinatesLabel = "Koordinaten kopieren"', shortcode)
        self.assertIn('$coordinatesCopiedLabel := "Coordinates copied"', shortcode)
        self.assertIn('$coordinatesCopiedLabel = "Koordinaten kopiert"', shortcode)
        self.assertIn('$coordinatesNotCopiedLabel := "Unable to copy coordinates"', shortcode)
        self.assertIn('$coordinatesNotCopiedLabel = "Koordinaten konnten nicht kopiert werden"', shortcode)
        self.assertIn('$openMapLabel := "Open in OpenStreetMap"', shortcode)
        self.assertIn('$openMapLabel = "In OpenStreetMap öffnen"', shortcode)
        self.assertIn('class="map-embed__actions"', shortcode)
        self.assertIn('class="map-embed__copy map-embed__action"', shortcode)
        self.assertIn('class="map-embed__open map-embed__action"', shortcode)
        self.assertIn('data-coordinates="{{ $coordinates }}"', shortcode)
        self.assertIn('navigator.clipboard.writeText', shortcode)
        self.assertIn('target="_blank" rel="noopener noreferrer"', shortcode)
        self.assertIn("<noscript>", shortcode)
        self.assertIn('class="map-embed__fallback"', shortcode)
        self.assertIn('class="map-embed__viewport"', shortcode)
        self.assertIn('class="map-embed__frame"', shortcode)
        self.assertNotIn('style="border: 1px solid #ccc;"', shortcode)
        self.assertIn(".map-embed__frame", css)
        self.assertIn("height: clamp(280px, 55vw, 450px);", css)
        self.assertIn(".map-embed__actions", css)
        self.assertIn(".map-embed__action", css)
        self.assertIn("@media screen and (max-width: 520px)", css)

    def test_single_article_content_uses_papermod_markdown_container(self):
        single = (ROOT / "layouts" / "single.html").read_text()
        self.assertIn('<div class="post-content md-content">', single)

    def test_external_markdown_links_open_in_a_new_tab_without_affecting_internal_links(self):
        render_link = (ROOT / "layouts" / "_markup" / "render-link.html").read_text()

        self.assertIn("urls.Parse", render_link)
        self.assertIn("site.BaseURL", render_link)
        self.assertIn('target="_blank"', render_link)
        self.assertIn('rel="noopener noreferrer"', render_link)

    def test_main_content_width_matches_listing_cards_on_desktop(self):
        css = (ROOT / "assets" / "css" / "extended" / "custom.css").read_text()
        aligned_width = "max-width: calc(var(--main-width) + var(--gap) * 10);"

        self.assertIn(".main {\n    " + aligned_width, css)
        self.assertIn(".post-entry {\n    " + aligned_width, css)
        self.assertNotIn("max-width: calc(var(--main-width) + var(--gap) * 30);", css)

    def test_strava_activity_images_are_compact_but_remain_responsive(self):
        shortcode = (ROOT / "layouts" / "_shortcodes" / "strava-activity-image.html").read_text()
        css = (ROOT / "assets" / "css" / "extended" / "custom.css").read_text()

        self.assertIn('class="strava-activity-image"', shortcode)
        self.assertIn(".strava-activity-image", css)
        self.assertIn("width: min(100%, 320px);", css)
        self.assertIn("display: block;", css)

    def test_masthead_preserves_the_current_papermod_navigation_contract(self):
        header = (ROOT / "layouts" / "_partials" / "header.html").read_text()
        css = (ROOT / "assets" / "css" / "extended" / "custom.css").read_text()
        config = (ROOT / "hugo.toml").read_text()

        self.assertIn('class="header-nav site-masthead__nav"', header)
        self.assertIn('id="menu" class="menu"', header)
        self.assertIn('class="site-masthead__image"', header)
        self.assertIn('site.Params.masthead.image', header)
        self.assertIn('Resize "2400x webp q78"', header)
        self.assertIn('image = "images/masthead.webp"', config)
        self.assertIn("title = 'Zwischen Terminal und Trampelpfad'", config)
        self.assertIn("title = 'Between terminals and trails'", config)
        self.assertIn('text = "matschcode"', config)
        self.assertIn('icon = "home-logo-300.webp"', config)
        self.assertIn("iconHeight = 24", config)
        self.assertTrue((ROOT / "assets" / "images" / "masthead.webp").is_file())
        self.assertTrue((ROOT / "static" / "home-logo-300.webp").is_file())
        self.assertIn(".site-masthead .site-masthead__nav", css)
        self.assertIn("min-height: 286px;", css)
        self.assertIn("min-height: 244px;", css)
        self.assertIn(".site-masthead .menu .active::after", css)


if __name__ == "__main__":
    unittest.main()
