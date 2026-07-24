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
