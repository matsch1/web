"""Removed curation fields must not return to editorial source or templates."""
from pathlib import Path
import unittest
import frontmatter

ROOT = Path(__file__).resolve().parents[1]

class HomepageMetadata(unittest.TestCase):
    def test_removed_curation_fields_are_absent_from_all_content(self):
        for path in (ROOT / 'content').rglob('*.md'):
            homepage = frontmatter.load(path).get('homepage', {})
            if isinstance(homepage, dict):
                with self.subTest(path=str(path.relative_to(ROOT))):
                    self.assertNotIn('state', homepage)
                    self.assertNotIn('featured', homepage)

    def test_templates_do_not_consume_removed_curation_fields(self):
        for directory in ['layouts', 'scripts']:
            for path in (ROOT / directory).rglob('*'):
                if path.is_file() and path.suffix in ['.html', '.py', '.js']:
                    text = path.read_text()
                    self.assertNotIn('homepage.state', text, str(path))
                    self.assertNotIn('homepage.featured', text, str(path))

    def test_section_remains_a_technical_image_hint(self):
        for relative in ['layouts/list.html', 'layouts/_partials/homepage_project_card.html']:
            text = (ROOT / relative).read_text()
            self.assertIn('eq (.Param "homepage.section") "engineering"', text)
        css = (ROOT / 'assets/css/extended/z-editorial.css').read_text()
        self.assertIn('object-fit: contain', css)
