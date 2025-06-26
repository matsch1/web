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
    text = re.sub("\*\*.*?\*\*", add_placeholder, text, flags=re.DOTALL)

    return text, placeholders


def unmask_placeholders(text, placeholders):
    for ph, original in placeholders.items():
        text = text.replace(ph, original)
    return text


for md_file in BASE_PATH.rglob("*.md"):
    print(f"file: {md_file}")
    if md_file.suffix != ".md":
        continue
    if md_file.name.endswith((".de.md", ".en.md")):
        continue  # skip already translated files

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
    if not source_file.exists():
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
