"""Validate that generated Pages-catalog links point to files that exist.

Regression guard for the migration into skills/: the catalog once built
GitHub blob links from the leaf folder name only (blob/main/ctf-web/...),
which 404 after the skills moved to skills/ctf-web/.... This regenerates
the catalog and asserts every blob/main/<path> (including technique docs
and exploit automation scripts) resolves to a real file.
"""

import importlib.util
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "generate_catalog", REPO_ROOT / "scripts" / "generate_catalog.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CatalogLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = _load_generator()
        cls.skills = cls.gen.collect_skills()
        cls.html = cls.gen.build_html(cls.skills)

    def test_all_blob_links_resolve(self):
        paths = re.findall(r"blob/main/([^\"]+)", self.html)
        self.assertTrue(paths, "catalog produced no links")
        script_links = [p for p in paths if "/scripts/" in p]
        self.assertGreaterEqual(
            len(script_links), 10, "catalog must include exploit script links"
        )
        missing = [p for p in paths if not (REPO_ROOT / p).is_file()]
        self.assertEqual(missing, [], f"catalog links to missing files: {missing}")

    def test_all_categories_have_explicit_color_and_icon(self):
        for skill in self.skills:
            name = skill["dir_name"]
            self.assertIn(name, self.gen.CATEGORY_COLORS)
            self.assertIn(name, self.gen.CATEGORY_ICONS)

    def test_json_ld_and_author_meta_present(self):
        self.assertIn("application/ld+json", self.html)
        self.assertIn('"@type": "SoftwareSourceCode"', self.html)
        self.assertIn("Lukasz Jagiello", self.html)
        self.assertIn('<meta name="author" content="Lukasz Jagiello">', self.html)


if __name__ == "__main__":
    unittest.main()
