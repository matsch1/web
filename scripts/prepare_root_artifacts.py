"""Create root-level publish artifacts for a multilingual Hugo site."""
from pathlib import Path
import sys


ROOT_REDIRECT = """<!doctype html><html lang=\"de\"><head><meta charset=\"utf-8\"><meta name=\"robots\" content=\"noindex,follow\"><link rel=\"canonical\" href=\"https://blog.matschcode.de/de/\"><title>Weiterleitung…</title><script>const language=(navigator.languages&&navigator.languages[0])||navigator.language||\"de\";window.location.replace(language.toLowerCase().startsWith(\"de\")?\"de/\":\"en/\");</script></head><body><p><a href=\"de/\">Deutsch</a> / <a href=\"en/\">English</a></p></body></html>\n"""


def main(output="public"):
    public = Path(output)
    static = Path("static")
    public.mkdir(parents=True, exist_ok=True)
    for filename in ("CNAME", "sitemap.xml"):
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
