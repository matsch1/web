"""Regression coverage for localized cover metadata in articles and projects."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location("translate_markdown", ROOT / "scripts/translate_markdown.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Client:
    def __init__(self):
        self.inputs = []

    def translate_text(self, text, **kwargs):
        self.inputs.append(text)
        return type("Result", (), {"text": f"Translated: {text}"})()


class CoverTranslationTests(unittest.TestCase):
    def test_cover_text_is_translated_without_mutating_source_or_image_settings(self):
        module = load_module()
        for source, target in (("de", "en"), ("en", "de")):
            with self.subTest(source=source):
                cover = {"caption": "Meine Infrastruktur", "alt": "Server mit Laufwerken", "image": "./cover.webp", "relative": True, "hidden": False, "responsiveImages": False}
                post = module.frontmatter.Post("Body", source_lang=source, cover=cover)
                before = copy.deepcopy(post.metadata)
                client = Client()
                translated = module.translated_post(client, post, source, target)
                self.assertEqual(translated["cover"]["caption"], "Translated: Meine Infrastruktur")
                self.assertEqual(translated["cover"]["alt"], "Translated: Server mit Laufwerken")
                for key in ("image", "relative", "hidden", "responsiveImages"):
                    self.assertEqual(translated["cover"][key], cover[key])
                self.assertNotIn("./cover.webp", client.inputs)
                self.assertEqual(post.metadata, before)

    def test_empty_or_missing_cover_text_does_not_trigger_translation(self):
        module = load_module()
        for cover in (None, {}, {"caption": "", "alt": None, "image": "cover.webp"}):
            with self.subTest(cover=cover):
                metadata = {} if cover is None else {"cover": cover}
                client = Client()
                translated = module.translated_post(client, module.frontmatter.Post("", **metadata), "de", "en")
                self.assertEqual(client.inputs, [])
                self.assertEqual(translated.metadata.get("cover"), cover)

    def test_existing_unlocked_covers_refresh_once_in_articles_and_projects(self):
        module = load_module()
        for section in ("notes", "projects"):
            with self.subTest(section=section), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                bundle = root / section / "example"
                bundle.mkdir(parents=True)
                post = module.frontmatter.Post("Body", source_lang="de", cover={"caption": "Mein Bild", "alt": "Mein Server", "image": "cover.webp"})
                module.frontmatter.dump(post, bundle / "index.md")
                stale = module.frontmatter.Post("English body", base_hash=module.hash_post(post), cover=copy.deepcopy(post["cover"]))
                module.frontmatter.dump(stale, bundle / "index.en.md")
                self.assertEqual(module.translate_tree(root, Client()), 2)
                localized = module.frontmatter.load(bundle / "index.en.md")
                self.assertEqual(localized["cover"]["caption"], "Translated: Mein Bild")
                self.assertEqual(localized["cover"]["alt"], "Translated: Mein Server")
                client = Client()
                self.assertEqual(module.translate_tree(root, client), 0)
                self.assertEqual(client.inputs, [])

    def test_locked_cover_localizations_remain_untouched(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            post = module.frontmatter.Post("Body", source_lang="de", translation_lock=True, cover={"caption": "Mein Bild"})
            module.frontmatter.dump(post, root / "index.md")
            for language in ("de", "en"):
                module.frontmatter.dump(post, root / f"index.{language}.md")
            before = {p.name: p.read_bytes() for p in root.glob("*.md")}
            client = Client()
            self.assertEqual(module.translate_tree(root, client), 0)
            self.assertEqual(client.inputs, [])
            self.assertEqual({p.name: p.read_bytes() for p in root.glob("*.md")}, before)

    def test_cover_translation_failure_does_not_write_locale_files(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            post = module.frontmatter.Post("Body", source_lang="de", cover={"caption": "Mein Bild"})
            module.frontmatter.dump(post, root / "index.md")

            class FailingClient(Client):
                def translate_text(self, text, **kwargs):
                    if text == "Mein Bild":
                        raise RuntimeError("caption translation failed")
                    return super().translate_text(text, **kwargs)

            with self.assertRaises(module.TranslationError):
                module.translate_tree(root, FailingClient())
            self.assertFalse((root / "index.en.md").exists())
            self.assertFalse((root / "index.de.md").exists())

    def test_reviewed_german_cover_metadata_is_localized(self):
        module = load_module()
        expected = {
            "notes/development/giscus-comments": "Giscus: das auf GitHub Discussions basierende Kommentarsystem für Hugo-Blogs",
            "notes/self-hosting/nextcloud-k3s": "So habe ich Nextcloud per Helm-Chart auf meinem K3s-Cluster bereitgestellt",
            "notes/self-hosting/tailscale-public-domain": "Öffentlicher Datenverkehr über einen VPS und Tailscale in ein privates K3s-Homelab",
            "projects/development/n8n-personal-assistant": "Persönlicher KI-Assistent mit n8n",
        }
        for path, caption in expected.items():
            with self.subTest(path=path):
                bundle = ROOT / "content" / path
                source = module.frontmatter.load(bundle / "index.md")
                de = module.frontmatter.load(bundle / "index.de.md")
                self.assertEqual(de["cover"]["caption"], caption)
                self.assertTrue(de["translation_lock"])
                self.assertEqual(de["cover"]["image"], source["cover"]["image"])
        tailscale = module.frontmatter.load(ROOT / "content/notes/self-hosting/tailscale-public-domain/index.de.md")
        self.assertEqual(tailscale["cover"]["alt"], "Datenfluss vom VPS zum durch Tailscale geschützten K3s-Cluster")

    def test_reviewed_english_travel_cover_alt_is_localized(self):
        module = load_module()
        expected = {
            "2018-iceland": "Loaded hardtail in the Icelandic Highlands",
            "2023-denmark": "Loaded bikepacking bike at a shelter on Jutland's west coast",
        }
        for project, alt in expected.items():
            with self.subTest(project=project):
                post = module.frontmatter.load(ROOT / "content/projects/travel" / project / "index.en.md")
                self.assertEqual(post["cover"]["alt"], alt)

    def test_reviewed_homelab_caption_is_localized(self):
        module = load_module()
        bundle = ROOT / "content/notes/self-hosting/homelab-infrastructure"
        source = module.frontmatter.load(bundle / "index.md")
        de = module.frontmatter.load(bundle / "index.de.md")
        en = module.frontmatter.load(bundle / "index.en.md")
        self.assertEqual(de["cover"]["caption"], "Meine Homelab Infrastruktur")
        self.assertEqual(en["cover"]["caption"], "My Home Lab Infrastructure")
        self.assertEqual(en["base_hash"], module.hash_post(source))
        for post in (source, de, en):
            self.assertTrue(post["translation_lock"])
            self.assertEqual(post["cover"]["image"], "editorial-cover.webp")


if __name__ == "__main__":
    unittest.main()
