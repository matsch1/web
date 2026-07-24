import sys
import zlib
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
SOCIAL_CARD_DIMENSIONS = (1200, 630)
SVG_ROOT_TAG = "{http://www.w3.org/2000/svg}svg"
VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


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
        if tag == "a" and "image-gallery__item" in classes and self.active_galleries:
            item = {"depth": len(self.tags), "has_image": False}
            self.active_galleries[-1]["items"].append(item)
            self.active_items.append(item)
        if tag == "img" and self.active_items:
            self.active_items[-1]["has_image"] = True
        if tag not in VOID_ELEMENTS:
            self.tags.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        if tag == "a" and self.active_items and self.active_items[-1]["depth"] == len(self.tags) - 1:
            self.active_items.pop()
        if self.tags:
            self.tags.pop()
        if tag == "div" and self.active_galleries and self.active_galleries[-1]["depth"] == len(self.tags):
            self.active_galleries.pop()


def fail(message):
    raise SystemExit(message)


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


def validate_gallery(path):
    parser = GalleryParser()
    parser.feed(path.read_text())
    if not parser.galleries:
        fail(f"missing gallery container in {path}")
    for gallery in parser.galleries:
        if not gallery["items"] or any(not item["has_image"] for item in gallery["items"]):
            fail(f"gallery contains no static images in {path}")
    html = path.read_text()
    if "nanogallery2" in html or "jquery@3.7.1" in html:
        fail(f"gallery still depends on third-party JavaScript in {path}")


def main(output):
    public = Path(output)
    required = [
        "CNAME",
        "robots.txt",
        "sitemap.xml",
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
    for language in ("de", "en"):
        if not (public / language / "sitemap.xml").is_file():
            fail(f"missing {language} sitemap")
        validate_social_card(public / language / f"social-{language}.png")
        validate_svg(public / language / "safari-pinned-tab.svg")
        validate_default_social_metadata(
            public / language / "index.html",
            f"https://blog.matschcode.de/{language}/social-{language}.png",
        )
    for page in public.rglob("*.html"):
        if "image-gallery" in page.read_text():
            validate_gallery(page)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) == 2 else "public")
