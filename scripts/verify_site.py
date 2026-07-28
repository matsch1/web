import sys
import zlib
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOCIAL_CARD_DIMENSIONS = (1200, 630)
SVG_ROOT_TAG = "{http://www.w3.org/2000/svg}svg"
VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
GOOGLE_SITE_VERIFICATION_FILE = "google84170ae546b74eba.html"
GOOGLE_SITE_VERIFICATION_CONTENT = f"google-site-verification: {GOOGLE_SITE_VERIFICATION_FILE}"


class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.opengraph = []

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return
        attributes = dict(attrs)
        if (attributes.get("property") or "").startswith("og:"):
            self.opengraph.append((attributes.get("property"), attributes.get("content")))


class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.galleries = []
        self.active_galleries = []
        self.active_items = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set((attributes.get("class") or "").split())
        if tag == "div" and "image-gallery" in classes:
            gallery = {"depth": len(self.tags), "items": []}
            self.galleries.append(gallery)
            self.active_galleries.append(gallery)
        if tag in {"a", "figure"} and "image-gallery__item" in classes and self.active_galleries:
            item = {
                "tag": tag,
                "depth": len(self.tags),
                "has_image": False,
                "has_descriptive_alt": False,
            }
            self.active_galleries[-1]["items"].append(item)
            self.active_items.append(item)
        if tag == "img" and self.active_items:
            self.active_items[-1]["has_image"] = True
            self.active_items[-1]["has_descriptive_alt"] = bool((attributes.get("alt") or "").strip())
        if tag not in VOID_ELEMENTS:
            self.tags.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if (
            self.active_items
            and tag == self.active_items[-1]["tag"]
            and self.active_items[-1]["depth"] == len(self.tags) - 1
        ):
            self.active_items.pop()
        if self.tags:
            self.tags.pop()
        if tag == "div" and self.active_galleries and self.active_galleries[-1]["depth"] == len(self.tags):
            self.active_galleries.pop()


def fail(message):
    raise SystemExit(message)


class SeoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.links = []
        self.assets = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "meta":
            key = attributes.get("property") or attributes.get("name")
            if key:
                self.meta.setdefault(key, attributes.get("content", ""))
        if tag == "link":
            self.links.append(attributes)
        if tag in {"img", "script", "source"}:
            self.assets.append(attributes.get("src", ""))
        if tag == "link":
            self.assets.append(attributes.get("href", ""))


def validate_html_page(path, public, sitemap_locations):
    html = path.read_text()
    if path.name == GOOGLE_SITE_VERIFICATION_FILE:
        if html != GOOGLE_SITE_VERIFICATION_CONTENT:
            fail(f"invalid Google Search Console verification file: {path}")
        return
    if "http-equiv=refresh" in html:
        return
    parser = SeoParser()
    parser.feed(html)
    if path in {public / "index.html", public / "de" / "404.html", public / "en" / "404.html"}:
        return
    canonical = [link.get("href", "") for link in parser.links if link.get("rel") == "canonical"]
    if len(canonical) != 1 or not canonical[0].startswith("https://blog.matschcode.de/"):
        fail(f"missing or invalid canonical in {path}")
    for key in ("description", "og:title", "og:description", "og:url", "twitter:card", "twitter:title", "twitter:description"):
        if not parser.meta.get(key):
            fail(f"missing {key} metadata in {path}")
    alternates = {link.get("hreflang") for link in parser.links if link.get("rel") == "alternate" and link.get("hreflang")}
    page_language = path.relative_to(public).parts[0] if path.relative_to(public).parts else None
    if page_language in {"de", "en"} and page_language not in alternates:
        fail(f"missing self-referential hreflang in {path}")
    robots = parser.meta.get("robots", "")
    if "noindex" in robots and canonical[0] in sitemap_locations:
        fail(f"noindex page is listed in a sitemap: {path}")
    for asset in parser.assets:
        if asset.startswith("/") and not (public / asset.lstrip("/")).is_file():
            fail(f"missing local asset {asset} in {path}")


def validate_social_card(path):
    data = path.read_bytes()
    if data[:8] != PNG_SIGNATURE:
        fail(f"social card is not a PNG: {path}")
    offset = len(PNG_SIGNATURE)
    dimensions = None
    saw_idat = False
    saw_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            fail(f"truncated PNG chunk in {path}")
        length = int.from_bytes(data[offset : offset + 4], "big")
        chunk_type = data[offset + 4 : offset + 8]
        data_start = offset + 8
        data_end = data_start + length
        if data_end + 4 > len(data):
            fail(f"truncated PNG chunk data in {path}")
        chunk_data = data[data_start:data_end]
        crc = int.from_bytes(data[data_end : data_end + 4], "big")
        if (zlib.crc32(chunk_type + chunk_data) & 0xFFFFFFFF) != crc:
            fail(f"invalid PNG chunk checksum in {path}")
        if chunk_type == b"IHDR":
            if dimensions is not None or length != 13:
                fail(f"invalid PNG header in {path}")
            dimensions = tuple(int.from_bytes(chunk_data[index : index + 4], "big") for index in (0, 4))
        elif chunk_type == b"IDAT":
            saw_idat = True
        elif chunk_type == b"IEND":
            if length != 0 or data_end + 4 != len(data):
                fail(f"invalid PNG end chunk in {path}")
            saw_iend = True
        offset = data_end + 4
    if dimensions != SOCIAL_CARD_DIMENSIONS:
        actual = "missing" if dimensions is None else f"{dimensions[0]}x{dimensions[1]}"
        fail(f"unexpected social card dimensions for {path}: {actual}")
    if not saw_idat or not saw_iend:
        fail(f"incomplete PNG data in {path}")


def validate_svg(path):
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as error:
        fail(f"invalid SVG {path}: {error}")
        return
    if root.tag != SVG_ROOT_TAG:
        fail(f"not an SVG document: {path}")


def validate_default_social_metadata(path, expected_url):
    parser = MetadataParser()
    parser.feed(path.read_text())
    expected_metadata = [
        ("og:image", expected_url),
        ("og:image:type", "image/png"),
        ("og:image:width", "1200"),
        ("og:image:height", "630"),
    ]
    for index in range(len(parser.opengraph) - len(expected_metadata) + 1):
        if parser.opengraph[index : index + len(expected_metadata)] == expected_metadata:
            return
    fail(f"missing complete localized social-card metadata in {path}")


def validate_projects_redirects(public):
    for language in ("de", "en"):
        path = public / language / "projects" / "index.html"
        if not path.is_file():
            fail(f"missing {language} projects redirect")
        html = path.read_text()
        parser = SeoParser()
        parser.feed(html)
        if parser.meta.get("robots") != "noindex,follow":
            fail(f"projects redirect is indexable: {path}")
        if f'window.location.replace("/{language}/")' not in html:
            fail(f"projects redirect does not target the localized homepage: {path}")


def validate_gallery(path):
    parser = GalleryParser()
    parser.feed(path.read_text())
    if not parser.galleries:
        fail(f"missing gallery container in {path}")
    for gallery in parser.galleries:
        if not gallery["items"] or any(
            not item["has_image"] or not item["has_descriptive_alt"] for item in gallery["items"]
        ):
            fail(f"gallery contains an image without descriptive alt text in {path}")
    html = path.read_text()
    if "nanogallery2" in html or "jquery@3.7.1" in html:
        fail(f"gallery still depends on third-party JavaScript in {path}")


def main(output):
    public = Path(output)
    required = [
        "CNAME",
        "robots.txt",
        "sitemap.xml",
        GOOGLE_SITE_VERIFICATION_FILE,
        "de/index.html",
        "en/index.html",
        "de/social-de.png",
        "en/social-en.png",
        "de/safari-pinned-tab.svg",
        "en/safari-pinned-tab.svg",
    ]
    missing = [item for item in required if not (public / item).is_file()]
    if missing:
        fail(f"missing generated artifacts: {', '.join(missing)}")
    if (public / "CNAME").read_text().strip() != "blog.matschcode.de":
        fail("unexpected CNAME")
    robots = (public / "robots.txt").read_text()
    if "Sitemap: https://blog.matschcode.de/sitemap.xml" not in robots:
        fail("robots.txt does not advertise root sitemap")
    root = ElementTree.parse(public / "sitemap.xml").getroot()
    locations = {node.text for node in root.iter() if node.tag.endswith("loc")}
    expected = {"https://blog.matschcode.de/de/sitemap.xml", "https://blog.matschcode.de/en/sitemap.xml"}
    if locations != expected:
        fail("root sitemap does not list both locale sitemaps")
    sitemap_locations = set()
    for language in ("de", "en"):
        sitemap = public / language / "sitemap.xml"
        if not sitemap.is_file():
            fail(f"missing {language} sitemap")
        sitemap_locations.update(node.text for node in ElementTree.parse(sitemap).getroot().iter() if node.tag.endswith("loc"))
        validate_social_card(public / language / f"social-{language}.png")
        validate_svg(public / language / "safari-pinned-tab.svg")
        validate_default_social_metadata(
            public / language / "index.html",
            f"https://blog.matschcode.de/{language}/social-{language}.png",
        )
    validate_projects_redirects(public)
    for page in public.rglob("*.html"):
        validate_html_page(page, public, sitemap_locations)
        if "image-gallery" in page.read_text():
            validate_gallery(page)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) == 2 else "public")
