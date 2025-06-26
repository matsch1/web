---
title: "Free Hugo Autotranslator for Github Pages"
date: 2025-06-26
img: img1.png
description: "Automatically translate your Hugo website and deploy it to Github Pages"
ShowToc: true
TocOpen: true
draft: false
---
![header-image](img1.png)

## The problem and the idea
I want to write a blog post in english or german, and I don't want translate it
manually every time. This is much easier to maintain and obviously much less
annoying. 

So the idea is to automate this translation process. Therefore it should
automatically detect if the post is written in german or english and translate
it to the other language.

I like to use Github Actions to translate before deployment.
For this I want to use free translation service.

## The translation possibilities
There are many possibilities to translate text using code. 
Most of them aren't free, or have a limited length of characters.
For example the API interface of known translation services like the [DeepL API](https://www.deepl.com/en/pro#developer), 
or AI services liken OpenAI (which require a payed API key).

### Googletrans
For the first start I want to go with a free version. To do this I found the
free python package googletrans. It is actually deprecated, but does still work
with Python 3.12. This is ok in my case, because I can run it in Github Actions
using an old environment.

## Hugo multlingual mode
To realize a multilingual website hugo must be prepared setup in multilingual
mode.
The main setup is done in the `hugo.toml`.
In my case it works best like this:

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

The markdown files are generated like this:

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

## How to translate
Realisation of the auto translation using Github Actions and python

### Setup of translation environment in Github Actions workflow
The first part of the Github Actions job is getting a python 3.12 environment
and install the required dependencies.
The second part is about running the actual translation script in python and
commit the new, generated markdown files.

The second job is the deployment to the public directory (which contains the
hugo html files) to the gh-pages branch which can be used in Github Pages.

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

### Auto translation
The translation script consists of the following main parts:

- Find markdown files
- Check if files changed (hash check)
- Identify language of markdown file
- Replace code blocks, shortcodes, urls, ... with placeholders (masking)
- Translation
- Unmask placeholders
- Save translated text into new files

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

After the new files are commited. The push to main triggers a new hugo build.
