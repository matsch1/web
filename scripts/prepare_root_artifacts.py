"""Create root-level publish artifacts for a multilingual Hugo site."""
from pathlib import Path
import sys


ROOT_REDIRECT = """<!doctype html>
<html lang=\"de\"><head>
<meta charset=\"utf-8\">
<meta name=\"robots\" content=\"noindex,follow\">
<meta name=\"description\" content=\"matschcode — Zwischen Terminal und Trampelpfad\">
<link rel=\"canonical\" href=\"https://blog.matschcode.de/\">
<meta property=\"og:title\" content=\"matschcode\">
<meta property=\"og:description\" content=\"Zwischen Terminal und Trampelpfad\">
<meta property=\"og:url\" content=\"https://blog.matschcode.de/\">
<meta property=\"og:type\" content=\"website\">
<meta property=\"og:image\" content=\"https://blog.matschcode.de/de/home-logo-600.webp\">
<meta property=\"og:image:type\" content=\"image/webp\">
<meta property=\"og:image:width\" content=\"600\">
<meta property=\"og:image:height\" content=\"606\">
<meta name=\"twitter:card\" content=\"summary_large_image\">
<meta name=\"twitter:title\" content=\"matschcode\">
<meta name=\"twitter:description\" content=\"Zwischen Terminal und Trampelpfad\">
<meta name=\"twitter:image\" content=\"https://blog.matschcode.de/de/home-logo-600.webp\">
<title>matschcode</title>
<script>const language=(navigator.languages&&navigator.languages[0])||navigator.language||\"de\";window.location.replace(language.toLowerCase().startsWith(\"de\")?\"de/\":\"en/\");</script>
</head><body><p><a href=\"de/\">Deutsch</a> / <a href=\"en/\">English</a></p></body></html>
"""


def main(output="public"):
    public = Path(output)
    static = Path("static")
    public.mkdir(parents=True, exist_ok=True)
    for filename in ("CNAME", "sitemap.xml", "google84170ae546b74eba.html"):
        source = static / filename
        if not source.is_file():
            raise SystemExit(f"missing source artifact: {source}")
        (public / filename).write_bytes(source.read_bytes())
    robots = public / "de" / "robots.txt"
    if not robots.is_file():
        raise SystemExit("missing generated German robots.txt")
    (public / "robots.txt").write_bytes(robots.read_bytes())
    (public / "index.html").write_text(ROOT_REDIRECT, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) == 2 else "public")
