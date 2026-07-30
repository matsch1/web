import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "translate_markdown.py"


def load_module():
    spec = importlib.util.spec_from_file_location("translate_markdown", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TranslationTests(unittest.TestCase):
    def test_translation_requires_explicit_source_language(self):
        module = load_module()
        post = module.frontmatter.loads("---\ntitle: Hallo\n---\n\nHallo Welt")

        with self.assertRaisesRegex(module.TranslationError, "source_lang"):
            module.source_language(post)

    def test_every_canonical_content_file_declares_a_valid_source_language(self):
        module = load_module()
        canonical = [
            path
            for path in (ROOT / "content").rglob("*.md")
            if not path.name.endswith((".de.md", ".en.md"))
        ]
        self.assertTrue(canonical)
        missing_or_invalid = []
        for path in canonical:
            post = module.frontmatter.load(path)
            if post.get("source_lang") not in {"de", "en"}:
                missing_or_invalid.append(str(path.relative_to(ROOT)))
        self.assertEqual(missing_or_invalid, [])

    def test_every_canonical_content_file_has_de_and_en_variants(self):
        canonical = [
            path
            for path in (ROOT / "content").rglob("*.md")
            if not path.name.endswith((".de.md", ".en.md"))
        ]
        missing_variants = [
            str(path.relative_to(ROOT))
            for path in canonical
            if any(not path.with_name(f"{path.stem}.{language}.md").is_file() for language in ("de", "en"))
        ]
        self.assertEqual(missing_variants, [])

    def test_translation_failure_does_not_write_partial_language_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            bundle = content / "post"
            bundle.mkdir(parents=True)
            (bundle / "index.md").write_text("---\ntitle: Hallo\ndescription: Beschreibung\nsource_lang: de\n---\n\nHallo Welt", encoding="utf-8")

            class FailingClient:
                def translate_text(self, *args, **kwargs):
                    raise RuntimeError("DeepL unavailable")

            with self.assertRaises(module.TranslationError):
                module.translate_tree(content, FailingClient())
            self.assertFalse((bundle / "index.de.md").exists())
            self.assertFalse((bundle / "index.en.md").exists())

    def test_translation_lock_generates_missing_language_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            bundle = content / "home"
            bundle.mkdir(parents=True)
            (bundle / "index.md").write_text(
                "---\ntitle: Source\nsource_lang: en\ntranslation_lock: true\n---\n\nSource heading",
                encoding="utf-8",
            )

            class Client:
                def translate_text(self, text, **kwargs):
                    return type("Result", (), {"text": f"DE: {text}"})()

            self.assertEqual(module.translate_tree(content, Client()), 2)
            self.assertTrue((bundle / "index.en.md").exists())
            translated = (bundle / "index.de.md").read_text(encoding="utf-8")
            self.assertIn("title: 'DE: Source'", translated)
            self.assertIn("DE: Source heading", translated)

    def test_translation_lock_preserves_manually_localized_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            bundle = content / "home"
            bundle.mkdir(parents=True)
            (bundle / "index.md").write_text(
                "---\ntitle: Source\nsource_lang: en\ntranslation_lock: true\n---\n\nSource heading",
                encoding="utf-8",
            )
            de = bundle / "index.de.md"
            en = bundle / "index.en.md"
            de.write_text("---\ntitle: Benutzerdefinierter Titel\n---\n\nBenutzerdefinierte Überschrift", encoding="utf-8")
            en.write_text("---\ntitle: Source\n---\n\nSource heading", encoding="utf-8")

            class FailingClient:
                def translate_text(self, *args, **kwargs):
                    raise AssertionError("locked content must not be sent to DeepL")

            self.assertEqual(module.translate_tree(content, FailingClient()), 0)
            self.assertIn("Benutzerdefinierter Titel", de.read_text(encoding="utf-8"))

    def test_gallery_title_and_alt_are_translated_while_its_source_is_preserved(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            bundle = content / "post"
            bundle.mkdir(parents=True)
            (bundle / "index.md").write_text(
                "---\ntitle: Bergtour\nsource_lang: de\n---\n\n{{< gallery src=\"bergsee.jpg\" title=\"Bergsee am Pass\" alt=\"Beladenes Fahrrad am Bergsee\" >}}",
                encoding="utf-8",
            )

            class Client:
                inputs = []

                def translate_text(self, text, **kwargs):
                    self.inputs.append(text)
                    return type("Result", (), {"text": f"EN: {text}"})()

            client = Client()
            module.translate_tree(content, client)
            translated = (bundle / "index.en.md").read_text(encoding="utf-8")
            self.assertFalse(any("bergsee.jpg" in text for text in client.inputs))
            self.assertIn('src="bergsee.jpg"', translated)
            self.assertIn('title="EN: Bergsee am Pass"', translated)
            self.assertIn('alt="EN: Beladenes Fahrrad am Bergsee"', translated)

    def test_translation_updates_title_and_description_atomically(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            content = Path(tmp) / "content"
            bundle = content / "post"
            bundle.mkdir(parents=True)
            (bundle / "index.md").write_text("---\ntitle: Hallo\ndescription: Kurze Beschreibung\nsource_lang: de\n---\n\nHallo Welt", encoding="utf-8")

            class Client:
                def translate_text(self, text, **kwargs):
                    return type("Result", (), {"text": f"EN: {text}"})()

            module.translate_tree(content, Client())
            translated = (bundle / "index.en.md").read_text(encoding="utf-8")
            self.assertIn("title: 'EN: Hallo'", translated)
            self.assertIn("description: 'EN: Kurze Beschreibung'", translated)
            self.assertIn("EN: Hallo Welt", translated)
            self.assertTrue((bundle / "index.de.md").exists())


if __name__ == "__main__":
    unittest.main()
