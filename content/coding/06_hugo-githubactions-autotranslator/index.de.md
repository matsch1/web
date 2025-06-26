---
ShowToc: true
TocOpen: true
base_hash: fa81f441a3d81d393d8e1635fa349a05efc40836bdff5228e0bda06855d86d5f
date: 2025-06-26
description: Automatically translate your Hugo website and deploy it to Github Pages
draft: true
img: img1.png
title: Kostenloser Hugo -Autotranslator für Github -Seiten
---

![header-image](img1.png)

## Das Problem und die Idee
Ich möchte einen Blog -Beitrag in Englisch oder Deutsch schreiben, und ich möchte ihn nicht übersetzen
jedes Mal manuell.Dies ist viel einfacher zu pflegen und offensichtlich viel weniger
nervig.

Die Idee ist also, diesen Übersetzungsprozess zu automatisieren.Deshalb sollte es
Erkennen Sie automatisch, ob der Beitrag in Deutsch oder Englisch geschrieben ist und übersetzen
es zur anderen Sprache.

Ich mag es, Github -Aktionen vor der Bereitstellung zu übersetzen.
Dazu möchte ich kostenlosen Übersetzungsdienst verwenden.

## Die Übersetzungsmöglichkeiten
Es gibt viele Möglichkeiten, Text mit Code zu übersetzen.
Die meisten von ihnen sind nicht frei oder haben eine begrenzte Länge von Zeichen.
Zum Beispiel die API -Schnittstelle bekannte Übersetzungsdienste wie die [DeepL API](https://www.deepl.com/en/pro#developer),
oder AI -Dienste vergleichbar OpenAI (für die ein ausgezahlter API -Schlüssel erforderlich ist).

### googletrans
Für den ersten Start möchte ich mit einer kostenlosen Version gehen.Um dies zu tun, fand ich das
Kostenloses Python -Paket googletrans.Es ist tatsächlich veraltet, funktioniert aber immer noch
mit Python 3.12.Dies ist in meinem Fall in Ordnung, weil ich es in Github -Aktionen ausführen kann
mit einer alten Umgebung.

## Hugo Multlinger Modus
Um eine mehrsprachige Website zu erkennen, muss Hugo in mehrsprachigen Einrichtungen vorbereitet werden
Modus.
Das Hauptaufbau erfolgt in der `hugo.toml`.
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

Die Markdown -Dateien werden so generiert:

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

## Wie man übersetzt
Realisierung der automatischen Übersetzung mit Github -Aktionen und Python

### Einrichtung der Übersetzungsumgebung in GitHub -Aktionen Workflow
Der erste Teil des Jobs von Github Actions ist die Erhöhung einer Python 3.12 -Umgebung
und installieren Sie die erforderlichen Abhängigkeiten.
Im zweiten Teil geht es darum, das tatsächliche Übersetzungsskript in Python und auszuführen und
Beiten Sie die neuen, generierten Markdown -Dateien.

Der zweite Job ist der Einsatz für das öffentliche Verzeichnis (das die enthält
Hugo-HTML-Dateien) in den GH-Seiten-Zweig, der in Github-Seiten verwendet werden kann.

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

### Autoübersetzung
Das Übersetzungsskript besteht aus den folgenden Hauptteilen:

- Markdown -Dateien finden
- Überprüfen Sie, ob sich die Dateien geändert haben (Hash -Check)
- Identifizieren Sie die Sprache der Markdown -Datei
- Ersetzen Sie Codeblöcke, Shortcodes, URLs, ... durch Platzhalter (Maskierung)
- Übersetzung
- Platzhalter entlarven
- Übersetzte Text in neue Dateien speichern

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
    text = re.sub(r"```.*? [0000011000004]]

Nachdem die neuen Dateien begangen wurden.Der Vorstoß zum Hauptverkehr löst einen neuen Hugo -Build aus.