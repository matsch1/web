"""Render parallel analytics: preserve counter.dev, add production-only Umami."""
import os
from pathlib import Path
import subprocess
import tempfile
from html.parser import HTMLParser
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = 'https://analytics.matschcode.de/script.js'
WEBSITE_ID = '1736536a-5b2c-4200-9491-c95f339ca4b2'
COUNTER_SCRIPT = 'https://cdn.counter.dev/script.js'
COUNTER_ID = 'ad3d8a1d-120c-4f64-a5cf-2ae40ee7113b'


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.nodes = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


@unittest.skipUnless(os.environ.get('HUGO_BIN'), 'Set HUGO_BIN for rendered analytics checks')
class AnalyticsContract(unittest.TestCase):
    def render(self, environment='production', override=''):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        destination = Path(temporary.name) / 'public'
        command = [os.environ['HUGO_BIN'], '--source', str(ROOT),
                   '--destination', str(destination), '--environment', environment, '--minify']
        if override:
            config = Path(temporary.name) / 'override.toml'
            config.write_text(override)
            command += ['--config', f'{ROOT / "hugo.toml"},{config}']
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return destination

    def pages(self, destination):
        for language in ('de', 'en'):
            yield destination / language / 'index.html'
            # Stable translated article; exercise the single-page template too.
            yield destination / language / 'projects/development/obsidian-http-mcp/index.html'

    def test_production_has_one_script_per_provider(self):
        destination = self.render()
        for page in self.pages(destination):
            with self.subTest(page=page.relative_to(destination)):
                text = page.read_text()
                scripts = [a for t, a in Tags(text).nodes if t == 'script' and a.get('src') == SCRIPT]
                self.assertEqual(len(scripts), 1)
                self.assertIn('defer', scripts[0])
                self.assertEqual(scripts[0]['data-website-id'], WEBSITE_ID)
                self.assertEqual(scripts[0]['data-domains'], 'blog.matschcode.de')
                self.assert_counter_preserved(text)

    def test_development_preserves_counter_without_umami(self):
        self.assert_only_counter(self.render('development'))

    def test_disabled_production_preserves_counter_without_umami(self):
        self.assert_only_counter(self.render(override='[params.analytics.umami]\nenabled=false\n'))

    def test_missing_configuration_preserves_counter_without_umami(self):
        for field in ('scriptURL', 'websiteID'):
            with self.subTest(field=field):
                self.assert_only_counter(self.render(override=f'[params.analytics.umami]\n{field}=""\n'))

    def test_search_console_verification_remains_independent(self):
        destination = self.render(override='[params.analytics.umami]\nenabled=false\n[params.analytics.google]\nSiteVerificationTag="regression-verification"\n')
        for page in self.pages(destination):
            verification = [a['content'] for t, a in Tags(page.read_text()).nodes
                            if t == 'meta' and a.get('name') == 'google-site-verification']
            self.assertEqual(verification, ['regression-verification'])
        self.assertEqual((destination / 'de/google84170ae546b74eba.html').read_text().strip(),
                         'google-site-verification: google84170ae546b74eba.html')

    def assert_counter_preserved(self, text):
        scripts = [a for t, a in Tags(text).nodes
                   if t == 'script' and a.get('src') == COUNTER_SCRIPT]
        self.assertEqual(len(scripts), 1, 'Existing counter.dev script must be preserved exactly once')
        self.assertEqual(scripts[0], {'defer': None, 'src': COUNTER_SCRIPT,
                                     'data-id': COUNTER_ID, 'data-utcoffset': '2'})

    def assert_only_counter(self, destination):
        for page in self.pages(destination):
            with self.subTest(page=page.relative_to(destination)):
                text = page.read_text()
                self.assertNotIn(SCRIPT, text)
                self.assertNotIn('data-website-id', text)
                self.assert_counter_preserved(text)
