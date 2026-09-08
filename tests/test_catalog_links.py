"""Validate that generated Pages-catalog links point to files that exist.

Regression guard for the migration into skills/: the catalog once built
GitHub blob links from the leaf folder name only (blob/main/ctf-web/...),
which 404 after the skills moved to skills/ctf-web/.... This regenerates
the catalog and asserts every blob/main/<path> resolves to a real file.
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
    def test_all_blob_links_resolve(self):
        gen = _load_generator()
        skills = []
        for skill_dir in gen.discover_skills():
            text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            skills.append(
                {
                    "dir_name": skill_dir.name,
                    "rel_path": skill_dir.relative_to(REPO_ROOT).as_posix(),
                    "description": gen.parse_frontmatter(text).get("description", ""),
                    "techniques": gen.count_techniques(skill_dir),
                }
            )
        html = gen.build_html(skills)
        paths = re.findall(r"blob/main/([^\"]+)", html)
        self.assertTrue(paths, "catalog produced no links")
        missing = [p for p in paths if not (REPO_ROOT / p).is_file()]
        self.assertEqual(missing, [], f"catalog links to missing files: {missing}")


if __name__ == "__main__":
    unittest.main()
