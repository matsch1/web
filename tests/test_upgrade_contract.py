"""Keep the reviewed generator/theme compatibility pair reproducible."""
from pathlib import Path
import subprocess
import os
import tempfile
from html.parser import HTMLParser
import unittest

ROOT = Path(__file__).resolve().parents[1]


class UpgradeContract(unittest.TestCase):
    def test_both_workflows_use_the_reviewed_generator(self):
        for name in ('publish.yml', 'seo-check.yml'):
            with self.subTest(workflow=name):
                workflow = (ROOT / '.github/workflows' / name).read_text()
                self.assertIn("hugo-version: '0.168.0'", workflow)
                self.assertIn('extended: true', workflow)

    def test_pr_runs_rendered_tests_after_installing_hugo(self):
        workflow = (ROOT / '.github/workflows/seo-check.yml').read_text()
        self.assertLess(workflow.index('uses: peaceiris/actions-hugo'), workflow.index('python -m unittest'))
        self.assertIn('HUGO_BIN=$(command -v hugo) python -m unittest', workflow)

    def test_theme_is_the_reviewed_commit(self):
        result = subprocess.run(['git', '-C', str(ROOT / 'themes/PaperMod'), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), '26523e0fd837f965d08e320c9dde83700ad15649')


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


@unittest.skipUnless(os.environ.get('HUGO_BIN'), 'Set HUGO_BIN for rendered upgrade regression checks')
class RenderedUpgradeContract(unittest.TestCase):
    def test_local_header_and_social_overrides_survive_theme_update(self):
        with tempfile.TemporaryDirectory() as directory:
            build = subprocess.run([os.environ['HUGO_BIN'], '--source', str(ROOT), '--destination', directory, '--environment', 'production', '--minify'], text=True, capture_output=True)
            self.assertEqual(build.returncode, 0, build.stdout + build.stderr)
            for lang in ('de', 'en'):
                with self.subTest(language=lang):
                    nodes = Tags((Path(directory) / lang / 'index.html').read_text()).nodes
                    images = [a for t, a in nodes if t == 'img' and 'site-masthead__image' in a.get('class', '').split()]
                    self.assertEqual(len(images), 1)
                    self.assertEqual(images[0]['fetchpriority'], 'high')
                    self.assertTrue(images[0].get('srcset'))
                    self.assertEqual(len([a for t, a in nodes if t == 'ul' and a.get('id') == 'menu']), 1)
                    for key in ('og:title', 'og:url', 'og:image'):
                        values = [a['content'] for t, a in nodes if t == 'meta' and a.get('property') == key]
                        self.assertEqual(len(values), 1, (key, values))
                        self.assertTrue(values[0])
                    urls = [a['content'] for t, a in nodes if t == 'meta' and a.get('property') == 'og:url']
                    self.assertEqual(urls, [f'https://blog.matschcode.de/{lang}/'])
                    self.assertTrue((Path(directory) / lang / 'index.json').stat().st_size)

