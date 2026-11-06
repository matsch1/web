"""Homepage hierarchy and chronology regressions against real Hugo output."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from test_editorial_design import DOM

ROOT = Path(__file__).resolve().parents[1]
HUGO = os.environ.get('HUGO_BIN') or shutil.which('hugo')

@unittest.skipUnless(HUGO, 'Hugo required')
class NewsFirst(unittest.TestCase):
    def test_all_active_projects_without_count_limit(self):
        assert HUGO is not None
        with tempfile.TemporaryDirectory(prefix='active-home-fixture-') as directory:
            site = Path(directory)
            for name in ['layouts', 'assets', 'static', 'themes', 'i18n']:
                (site / name).symlink_to(ROOT / name, target_is_directory=True)
            shutil.copy(ROOT / 'hugo.toml', site / 'hugo.toml')
            for lang in ['de', 'en']:
                sources = {
                    f'_index.{lang}.md': 'title: Home',
                    f'projects/_index.{lang}.md': 'title: Projects',
                    f'notes/_index.{lang}.md': 'title: Articles',
                    f'notes/new/index.{lang}.md': 'title: Latest article\ndate: 2026-01-01',
                    f'projects/old-active/index.{lang}.md': 'title: Old active\ndate: 2020-01-01\nproject:\n  status: active',
                    f'projects/new-active/index.{lang}.md': 'title: New active\ndate: 2025-01-01\nproject:\n  status: active',
                    f'projects/third-active/index.{lang}.md': 'title: Third active\ndate: 2024-01-01\nproject:\n  status: active',
                    f'projects/travel/active/_index.{lang}.md': 'title: Active travel\ndate: 2023-01-01\nlistAsProject: true\nproject:\n  status: active',
                    f'projects/completed/index.{lang}.md': 'title: Completed project\ndate: 2026-01-01\nproject:\n  status: completed',
                    f'projects/hidden/index.{lang}.md': 'title: Hidden active\ndate: 2026-02-01\nhiddenInProjectList: true\nproject:\n  status: active',
                }
                for route, metadata in sources.items():
                    target = site / 'content' / route
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(f'---\n{metadata}\n---\nFixture body.')
            subprocess.run([HUGO, '--source', str(site), '--environment', 'production'], check=True, capture_output=True)
            for lang in ['de', 'en']:
                main = DOM((site / f'public/{lang}/index.html').read_text()).root.select('main')[0]
                sections = main.select('section')
                self.assertEqual([s.attrs.get('data-home-section') for s in sections], ['articles', 'featured'])
                self.assertEqual([c.select('h3')[0].text.strip() for c in sections[1].select('article')],
                                 ['New active', 'Third active', 'Active travel', 'Old active'])
                self.assertNotIn('Completed project', main.text)
                self.assertNotIn('Hidden active', main.text)

    def test_homepage_hierarchy_and_complete_listings(self):
        assert HUGO is not None
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run([HUGO, '--destination', directory, '--environment', 'production'], cwd=ROOT, check=True, capture_output=True)
            def page(route):
                return DOM((Path(directory)/route/'index.html').read_text()).root
            for lang, title in [('de', 'Neu im Blog'), ('en', 'New on the blog')]:
                sections = page(lang).select('main')[0].select('section')
                self.assertEqual([s.attrs.get('data-home-section') for s in sections], ['articles', 'featured'])
                self.assertEqual(sections[0].select('h2')[0].text.strip(), title)
                articles = sections[0].select('article')
                self.assertEqual(len(articles), 3)
                self.assertIn('editorial-lead', articles[0].attrs['class'])
                listing = page(f'{lang}/notes').select('article')[:3]
                self.assertEqual([c.select('a', 'entry-link')[0].attrs['href'] for c in articles],
                                 [urlsplit(c.select('a', 'entry-link')[0].attrs['href']).path for c in listing])
                focus = sections[1].select('article')
                self.assertEqual(len(focus), 1)
                self.assertNotIn('editorial-lead', focus[0].attrs['class'])
                self.assertIn('hermes-agent', focus[0].select('a', 'entry-link')[0].attrs['href'])
                self.assertEqual(sections[1].select('header')[0].select('a')[0].attrs['href'], f'/{lang}/projects/')
                self.assertEqual(articles[0].select('a', 'entry-link')[0].attrs['href'], urlsplit(page(f'{lang}/notes').select('article')[0].select('a', 'entry-link')[0].attrs['href']).path)
                self.assertGreater(len(page(f'{lang}/projects').select('article')), len(focus))
