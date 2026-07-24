import sys
from pathlib import Path
from xml.etree import ElementTree


def fail(message):
    raise SystemExit(message)


def main(output):
    public = Path(output)
    required = ["CNAME", "robots.txt", "sitemap.xml", "de/index.html", "en/index.html"]
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


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) == 2 else "public")
