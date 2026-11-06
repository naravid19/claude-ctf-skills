"""Validate agent definitions in the agents/ directory."""

import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"

VALID_TOOLS = {
    "Bash",
    "Read",
    "Write",
    "Edit",
    "Glob",
    "Grep",
    "Task",
    "WebFetch",
    "WebSearch",
    "Skill",
}

EXPECTED_AGENTS = {
    "ctf-solver",
    "ctf-pwn",
    "ctf-web",
    "ctf-crypto",
    "ctf-reverse",
    "ctf-forensics",
    "ctf-malware",
    "ctf-misc",
    "ctf-osint",
}


def _parse_agent_frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return None

    result: dict[str, str] = {}
    for line in lines[1:end]:
        stripped = line.strip()
        if not stripped or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        result[key.strip()] = value.strip().strip('"')
    return result


class TestAgentDefinitions(unittest.TestCase):
    def setUp(self):
        self.assertTrue(AGENTS_DIR.is_dir(), "agents directory missing")
        self.agent_files = list(AGENTS_DIR.glob("*.md"))
        self.assertGreater(len(self.agent_files), 0, "No agent files found")

    def test_expected_agents_present(self):
        found_names = {p.stem for p in self.agent_files}
        missing = EXPECTED_AGENTS - found_names
        self.assertEqual(missing, set(), f"Missing agent files: {missing}")

    def test_agent_frontmatter_valid(self):
        for agent_file in self.agent_files:
            text = agent_file.read_text(encoding="utf-8")
            fm = _parse_agent_frontmatter(text)
            with self.subTest(agent=agent_file.name):
                self.assertIsNotNone(fm, f"{agent_file.name} missing frontmatter")
                self.assertIn("name", fm)
                self.assertIn("description", fm)
                self.assertEqual(
                    fm["name"],
                    agent_file.stem,
                    f"Agent name '{fm['name']}' must match file stem '{agent_file.stem}'",
                )
                if "tools" in fm:
                    tools = {t.strip() for t in fm["tools"].split(",")}
                    invalid = tools - VALID_TOOLS
                    self.assertEqual(
                        invalid, set(), f"Invalid tools in {agent_file.name}: {invalid}"
                    )


if __name__ == "__main__":
    unittest.main()
