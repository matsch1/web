"""Atomically generate localized Hugo content from canonical Markdown sources."""
import argparse
import hashlib
import os
import re
import shutil
import tempfile
from pathlib import Path

import frontmatter
from dotenv import load_dotenv

LANGS = {"de", "en"}
TRANSLATABLE_METADATA = ("title", "description", "summary")
PLACEHOLDER_RE = re.compile(r"\[\[000001100000\d+\]\]")


class TranslationError(RuntimeError):
    pass


def hash_post(post):
    payload = frontmatter.dumps(post).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def mask_placeholders(text):
    placeholders = {}

    def replace(match):
        token = f"[[000001100000{len(placeholders)}]]"
        placeholders[token] = match.group(0)
        return token

    patterns = [
        (r"```.*?```", re.DOTALL),
        (r"`[^`]+`", 0),
        (r"!\[[^\]]*\]\([^)]+\)", 0),
        (r"\[[^\]]+\]\([^)]+\)", 0),
        (r"\{\{\s*[<%].*?[>%]\s*\}\}", re.DOTALL),
    ]
    for pattern, flags in patterns:
        text = re.sub(pattern, replace, text, flags=flags)
    return text, placeholders


def translate_text(client, text, source, target):
    if not text:
        return text
    try:
        result = client.translate_text(
            text,
            source_lang=source.upper(),
            target_lang="EN-US" if target == "en" else target.upper(),
            context="Personal blog about software engineering, homelab, travel and cycling.",
        )
    except Exception as exc:
        raise TranslationError(f"{source}->{target} translation failed: {exc}") from exc
    return result.text


def translate_value(client, value, source, target):
    masked, placeholders = mask_placeholders(str(value))
    translated = translate_text(client, masked, source, target)
    for token, original in placeholders.items():
        translated = translated.replace(token, original)
    if PLACEHOLDER_RE.search(translated):
        raise TranslationError("translation left protected placeholders behind")
    return translated


def source_language(post):
    explicit = post.get("source_lang")
    if explicit not in LANGS:
        raise TranslationError("source_lang must be explicitly set to de or en")
    return explicit


def translated_post(client, post, source, target):
    content = translate_value(client, post.content, source, target)
    metadata = dict(post.metadata)
    metadata.pop("source_lang", None)
    for key in TRANSLATABLE_METADATA:
        if metadata.get(key):
            metadata[key] = translate_value(client, metadata[key], source, target)
    metadata["base_hash"] = hash_post(post)
    return frontmatter.Post(content, **metadata)


def translate_tree(content_root, client):
    content_root = Path(content_root)
    staged = []
    for source_file in sorted(content_root.rglob("*.md")):
        if source_file.name.endswith((".de.md", ".en.md")):
            continue
        post = frontmatter.load(source_file)
        source = source_language(post)
        target = "en" if source == "de" else "de"
        source_variant = source_file.with_name(f"{source_file.stem}.{source}.md")
        target_variant = source_file.with_name(f"{source_file.stem}.{target}.md")
        if post.get("translation_lock") is True:
            if not source_variant.exists():
                staged.append((source_variant, frontmatter.dumps(post)))
            if not target_variant.exists():
                staged.append((target_variant, frontmatter.dumps(translated_post(client, post, source, target))))
            continue
        expected_hash = hash_post(post)
        current = frontmatter.load(target_variant) if target_variant.exists() else None
        if current and current.get("base_hash") == expected_hash:
            if not source_variant.exists():
                staged.append((source_variant, frontmatter.dumps(post)))
            continue
        staged.append((source_variant, frontmatter.dumps(post)))
        staged.append((target_variant, frontmatter.dumps(translated_post(client, post, source, target))))

    with tempfile.TemporaryDirectory(prefix="translations-") as tmp:
        temp = Path(tmp)
        prepared = []
        for destination, payload in staged:
            candidate = temp / destination.relative_to(content_root)
            candidate.parent.mkdir(parents=True, exist_ok=True)
            candidate.write_text(payload, encoding="utf-8")
            frontmatter.load(candidate)
            prepared.append((candidate, destination))
        for candidate, destination in prepared:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(candidate, destination)
    return len(staged)


def main():
    import deepl

    parser = argparse.ArgumentParser()
    parser.add_argument("--content", default="content")
    args = parser.parse_args()
    if os.path.exists(".env.secrets"):
        load_dotenv(".env.secrets")
    key = os.getenv("DEEPL_API_KEY")
    if not key:
        raise TranslationError("DEEPL_API_KEY is not set")
    changed = translate_tree(args.content, deepl.DeepLClient(key))
    print(f"Prepared {changed} localized file(s).")


if __name__ == "__main__":
    main()
