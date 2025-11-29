---
ShowToc: true
TocOpen: true
base_hash: 5a1cb1962f71d8a0a82c58649e8694bf95e1899cc2e106131a6d99da8dd03802
cover:
  alt: hugo-autotranslator
  caption: ''
  image: img1.png
  relative: true
date: 2025-06-26
description: Automatically translate your Hugo website and deploy it to Github Pages
draft: false
params:
  ShowPostNavLinks: true
title: Kostenloser Hugo-Autotranslator für Github-Seiten
---

## Das Problem und die Idee
Ich möchte einen Blog-Beitrag auf Deutsch oder Englisch schreiben und ihn nicht jedes Mal manuell übersetzen.
jedes Mal manuell übersetzen. Das ist viel einfacher zu pflegen und natürlich viel weniger
lästig.

Die Idee ist also, diesen Übersetzungsprozess zu automatisieren. Es soll also
automatisch erkannt werden, ob der Beitrag in Deutsch oder Englisch verfasst ist und
in die andere Sprache übersetzen.

Ich möchte Github Actions verwenden, um vor der Bereitstellung zu übersetzen.
Hierfür möchte ich einen kostenlosen Übersetzungsdienst nutzen.

## Die Übersetzungsmöglichkeiten
Es gibt viele Möglichkeiten, Text mit Code zu übersetzen.
Die meisten von ihnen sind nicht kostenlos oder haben eine begrenzte Länge an Zeichen.
Zum Beispiel die API-Schnittstelle von bekannten Übersetzungsdiensten wie [DeepL API](https://www.deepl.com/en/pro#developer),
oder KI-Dienste wie OpenAI (die einen kostenpflichtigen API-Schlüssel erfordern).

### Googletrans
Für den ersten Start möchte ich mit einer kostenlosen Version arbeiten. Zu diesem Zweck habe ich das
freie Python-Paket googletrans. Es ist eigentlich veraltet, aber es funktioniert noch
mit Python 3.12. Das ist in meinem Fall in Ordnung, denn ich kann es in Github Actions
unter Verwendung einer alten Umgebung ausführen kann.

## Hugo mehrsprachiger Modus
Um eine mehrsprachige Website zu realisieren, muss Hugo im mehrsprachigen
Modus vorbereitet werden.
Die Haupteinstellung wird in der `hugo.toml` vorgenommen.
In meinem Fall funktioniert es am besten wie folgt:

``` toml
title = 'Website title'
theme = 'PaperMod'
defaultContentLanguage = "de"
defaultContentLanguageInSubdir = true
enableMissingTranslationPlaceholders = true

[languages]

[languages.de]
baseURL = 'https://<githubUsername>.github.io/<reponame>/de'
languageName = "Deutsch"
weight = 1
contentDir = "content"

[languages.en]
baseURL = 'https://<githubUsername>.github.io/<reponame>/en'
languageName = "English"
weight = 2
contentDir = "content"
```

Die Markdown-Dateien werden wie folgt erzeugt:

```
content
- post1
-- index.md (original file)
-- index.en.md
-- index.de.md
- post2
-- index.md (original file)
-- index.en.md
-- index.de.md
```

## So wird übersetzt
Realisierung der automatischen Übersetzung mit Github Actions und Python

### Einrichtung der Übersetzungsumgebung im Github Actions Workflow
Der erste Teil der Arbeit mit Github Actions besteht darin, eine Python 3.12-Umgebung einzurichten
und die Installation der erforderlichen Abhängigkeiten.
Der zweite Teil besteht darin, das eigentliche Übersetzungsskript in Python auszuführen und
die Übergabe der neuen, generierten Markdown-Dateien.

Der zweite Job ist das Deployment in das öffentliche Verzeichnis (in dem sich die
hugo html-Dateien) in den gh-pages-Zweig, der in Github Pages verwendet werden kann.

``` yaml
jobs:
  translate:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install requests python-frontmatter langdetect googletrans==4.0.0-rc1

      - name: Translate Markdown files
        run: python scripts/translate_markdown.py

      - name: Commit translated files
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@users.noreply.github.com"
          git add content/
          git diff --cached --quiet || git commit -m "Auto-translated markdown files"
          git push
        continue-on-error: true
  deploy:
    runs-on: ubuntu-22.04
    needs: translate
    env:
      HUGO_CACHEDIR: /tmp/hugo_cache
    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true  # Fetch Hugo themes (true OR recursive)
          fetch-depth: 0    # Fetch all history for .GitInfo and .Lastmod

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v3
        with:
          hugo-version: 'latest'
          extended: true

      - name: Define cache
        uses: actions/cache@v4
        with:
          path: ${{ env.HUGO_CACHEDIR }}
          key: ${{ runner.os }}-hugomod-${{ hashFiles('**/go.sum') }}
          restore-keys: |
            ${{ runner.os }}-hugomod-

      - name: Build
        run: hugo --minify

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        if: github.ref == 'refs/heads/main'
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./public
```

### Automatische Übersetzung
Das Übersetzungsskript besteht aus den folgenden Hauptbestandteilen:

- Finden von Markdown-Dateien
- Prüfen, ob Dateien geändert wurden (Hash-Check)
- Identifizierung der Sprache der Markdown-Datei
- Ersetzen von Codeblöcken, Shortcodes, Urls, ... durch Platzhalter (Maskierung)
- Übersetzen
- Demaskieren von Platzhaltern
- Übersetzten Text in neuen Dateien speichern

``` py
import frontmatter
import hashlib
import re
from langdetect import detect
from pathlib import Path
import shutil
from googletrans import Translator

LANGS = {"de", "en"}
BASE_PATH = Path("content")

translator = Translator()


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def translate(text: str, source: str, target: str) -> str:
    try:
        result = translator.translate(text, src=source, dest=target)
        return result.text
    except Exception as e:
        print(f"Translation failed: {e}")
        return ""


def mask_placeholders(text):
    placeholders = {}
    placeholder_id = 0

    def add_placeholder(match):
        nonlocal placeholder_id
        ph = f"[[000001100000{placeholder_id}]]"
        placeholders[ph] = match.group(0)
        placeholder_id += 1
        return ph

    # Mask code blocks
    text = re.sub(r"```.*?```", add_placeholder, text, flags=re.DOTALL)

    # Mask inline code
    text = re.sub(r"`[^`]+`", add_placeholder, text)

    # Mask full markdown links and images
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", add_placeholder, text)  # images
    text = re.sub(r"\[[^\]]+\]\([^)]+\)", add_placeholder, text)  # links

    # Mask Hugo shortcodes
    text = re.sub(r"\{\{\s*[<%].*?[>%]\s*\}\}", add_placeholder, text, flags=re.DOTALL)

    # Mask **_**
    text = re.sub(r"\*\*(.*?)\*\*", add_placeholder, text, flags=re.DOTALL)

    return text, placeholders


def unmask_placeholders(text, placeholders):
    for ph, original in placeholders.items():
        text = text.replace(ph, original)
    return text


for md_file in BASE_PATH.rglob("*.md"):
    if md_file.suffix != ".md":
        continue
    elif md_file.name.endswith((".de.md", ".en.md")):
        continue  # skip already translated files
    else:
        print(f"file: {md_file}")

    # Load base file
    post = frontmatter.load(md_file)
    content = post.content
    try:
        detected_lang = detect(content)
    except Exception as e:
        print(f"Could not detect language for {md_file}: {e}")
        continue

    if detected_lang not in LANGS:
        print(f"Skipping {md_file}: unsupported language ({detected_lang})")
        continue

    other_lang = "en" if detected_lang == "de" else "de"
    base_name = md_file.stem
    parent_dir = md_file.parent

    source_file = parent_dir / f"{base_name}.{detected_lang}.md"
    target_file = parent_dir / f"{base_name}.{other_lang}.md"

    post_hash = hash_text(content)

    # Skip if translated file exists AND content hash hasn't changed
    if target_file.exists():
        existing_translated = frontmatter.load(target_file)
        if existing_translated.get("base_hash") == post_hash:
            print(f"✅ Skipping {md_file}: translation up-to-date")
            continue
        else:
            print(f"🔁 Updating translation for {md_file} → {target_file}")
    else:
        print(f"🌍 Translating {md_file} → {target_file}")

    # Copy base file to language-specific name if missing
    shutil.copy(md_file, source_file)
    print(f"📄 Copied {md_file} → {source_file}")

    # Mask placeholders before translation
    masked_content, placeholders = mask_placeholders(content)

    # Translate masked content
    translated_masked_content = translate(masked_content, detected_lang, other_lang)
    if not translated_masked_content:
        print(
            f"⚠️ Translation failed for {md_file} from {detected_lang} to {other_lang}, skipping."
        )
        continue

    # Unmask placeholders in translated content
    translated_content = unmask_placeholders(translated_masked_content, placeholders)

    # Prepare translated post with metadata and base_hash
    translated_post = frontmatter.Post(translated_content, **post.metadata)
    translated_post["base_hash"] = post_hash

    # Translate title if exists
    if "title" in post.metadata:
        translated_title = translate(post.metadata["title"], detected_lang, other_lang)
        if translated_title:
            translated_post["title"] = translated_title

    # Save translated file
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(translated_post))
        print(f"✅ Translated and saved {target_file}")
```

Nachdem die neuen Dateien commited wurden. Der Push nach Main löst einen neuen Hugo-Build aus.