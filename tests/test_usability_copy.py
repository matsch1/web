"""Reviewed listing copy and localized editorial source contracts (no API calls)."""
from pathlib import Path
import sys
import unittest

import frontmatter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from translate_markdown import hash_post


def canonical_files():
    return [p for p in (ROOT / 'content').rglob('*.md')
            if not p.name.endswith(('.de.md', '.en.md'))]


class UsabilityCopy(unittest.TestCase):
    def test_every_published_listing_has_reviewed_localized_copy(self):
        pages = []
        for path in canonical_files():
            post = frontmatter.load(path)
            relative = path.relative_to(ROOT / 'content')
            if post.get('draft'):
                continue
            if post.get('project') or (relative.parts[0] == 'notes' and path.name == 'index.md'):
                pages.append(path)
                self.assertIs(post.get('translation_lock'), True, str(relative))
                for lang in ('de', 'en'):
                    with self.subTest(page=str(relative), lang=lang):
                        localized = frontmatter.load(path.with_name(f'{path.stem}.{lang}.md'))
                        copy = localized.get('homepage', {})
                        self.assertTrue(copy.get('title'))
                        self.assertTrue(copy.get('teaser'))
                        self.assertLessEqual(len(copy['title']), 65)
                        self.assertLessEqual(len(copy['teaser']), 180)
                        self.assertNotRegex(copy['teaser'], r'^(Warning|Info|Einleitung|Introduction)\b')
                        self.assertNotIn('{{', copy['teaser'])
        self.assertTrue(pages)

    def test_reviewed_sources_and_translation_hashes_are_current(self):
        for path in canonical_files():
            post = frontmatter.load(path)
            relative = path.relative_to(ROOT / 'content')
            reviewed = (post.get('project') or
                        (relative.parts[0] == 'notes' and path.name == 'index.md' and not post.get('draft')) or
                        str(relative) in {'_index.md', 'about/_index.md', 'notes/_index.md', 'projects/_index.md'})
            if not reviewed:
                continue
            with self.subTest(page=str(path.relative_to(ROOT))):
                source = post['source_lang']
                source_post = frontmatter.load(path.with_name(f'{path.stem}.{source}.md'))
                # Existing article bodies can contain historic formatting differences;
                # a card-copy update must not silently replace those bodies.
                for key in ('title', 'description', 'homepage', 'translation_lock'):
                    self.assertEqual(source_post.get(key), post.get(key), key)
                target = 'en' if source == 'de' else 'de'
                translated = frontmatter.load(path.with_name(f'{path.stem}.{target}.md'))
                self.assertEqual(translated.get('base_hash'), hash_post(post))
                self.assertIs(translated.get('translation_lock'), True)

    def test_home_and_section_intros_are_compact(self):
        for lang in ('de', 'en'):
            home = frontmatter.load(ROOT / f'content/_index.{lang}.md')
            self.assertEqual(len(home.content.split('\n\n')), 1)
            self.assertLess(len(home.content), 180)
            self.assertNotIn(home['homepageTitle'], home.content)
            notes = frontmatter.load(ROOT / f'content/notes/_index.{lang}.md')
            self.assertTrue(notes.content)
            self.assertNotIn(notes['description'], notes.content)
            self.assertLess(len(notes.content), 150)
            projects = frontmatter.load(ROOT / f'content/projects/_index.{lang}.md')
            self.assertNotIn('chronolog', projects['description'].lower())

    def test_about_preserves_portrait_contacts_and_personal_connection(self):
        for lang in ('de', 'en'):
            post = frontmatter.load(ROOT / f'content/about/_index.{lang}.md')
            self.assertEqual(post['title'], 'Über mich' if lang == 'de' else 'About me')
            self.assertIn('src="./me.jpg"', post.content)
            for kind in ('linkedin', 'github', 'instagram', 'strava', 'email'):
                self.assertIn(f'type="{kind}"', post.content)
            self.assertIn('Bikepacking' if lang == 'de' else 'bikepacking', post.content)
            if lang == 'de':
                self.assertIn('zuverlässig', post.content)
                self.assertIn('lässt', post.content)
                self.assertNotIn('zuverlaessig', post.content)


if __name__ == '__main__':
    unittest.main()
