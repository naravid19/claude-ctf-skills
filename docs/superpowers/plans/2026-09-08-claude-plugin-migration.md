# Claude Code Plugin Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure `ctf-skills` into a canonical Claude Code plugin with `.claude-plugin/plugin.json`, relocations into `skills/`, a dedicated `agents/ctf-solver.md` subagent, and updated tests/tooling/docs.

**Architecture:** Relocate all 11 skill categories to `skills/<category>/`, declare metadata in `.claude-plugin/plugin.json`, create an autonomous CTF triage subagent in `agents/ctf-solver.md`, and update test discovery and CI workflow paths to maintain 100% test pass rates.

**Tech Stack:** Claude Code Plugin spec, Python 3.12+, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-08-claude-plugin-migration-design.md`

## Global Constraints

- Valid JSON schema for `.claude-plugin/plugin.json`.
- All 11 skill folders must be located under `skills/` preserving all technique files and git content.
- Python tests in `tests/` must pass cleanly (`pytest tests/ -v`).
- Frequent atomic git commits per task.

---

### Task 1: Create Claude Plugin Manifest

**Files:**
- Create: `.claude-plugin/plugin.json`

**Interfaces:**
- Produces: Official plugin metadata recognized by Claude Code CLI and `/plugin` loader.

- [ ] **Step 1: Create `.claude-plugin/plugin.json`**

Write the following configuration to `.claude-plugin/plugin.json`:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-plugin-manifest.json",
  "name": "ctf-skills",
  "displayName": "CTF Skills",
  "version": "1.0.0",
  "description": "Comprehensive Agent Skills and autonomous CTF solver agent for solving Capture The Flag challenges across Web, Pwn, Crypto, Reverse, Forensics, OSINT, AI/ML, Malware, and Misc.",
  "author": {
    "name": "Lukasz Jagiello",
    "url": "https://github.com/ljagiello"
  },
  "homepage": "https://github.com/ljagiello/ctf-skills",
  "repository": "https://github.com/ljagiello/ctf-skills",
  "license": "MIT",
  "keywords": [
    "ctf",
    "security",
    "cybersecurity",
    "reverse-engineering",
    "binary-exploitation",
    "pwn",
    "cryptography",
    "forensics",
    "web-exploitation",
    "osint",
    "agent-skills"
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run:
```bash
python -c "import json; json.load(open('.claude-plugin/plugin.json'))"
```
Expected: Exit code 0 (valid JSON).

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -m "feat: add .claude-plugin/plugin.json manifest"
```

---

### Task 2: Relocate Skill Folders into `skills/`

**Files:**
- Move: `ctf-ai-ml` -> `skills/ctf-ai-ml`
- Move: `ctf-crypto` -> `skills/ctf-crypto`
- Move: `ctf-forensics` -> `skills/ctf-forensics`
- Move: `ctf-malware` -> `skills/ctf-malware`
- Move: `ctf-misc` -> `skills/ctf-misc`
- Move: `ctf-osint` -> `skills/ctf-osint`
- Move: `ctf-pwn` -> `skills/ctf-pwn`
- Move: `ctf-reverse` -> `skills/ctf-reverse`
- Move: `ctf-web` -> `skills/ctf-web`
- Move: `ctf-writeup` -> `skills/ctf-writeup`
- Move: `solve-challenge` -> `skills/solve-challenge`

**Interfaces:**
- Produces: Directory layout `skills/<category>/SKILL.md` expected by Claude Code.

- [ ] **Step 1: Create `skills/` and move directories using `git mv`**

Run:
```bash
mkdir skills
git mv ctf-ai-ml skills/ctf-ai-ml
git mv ctf-crypto skills/ctf-crypto
git mv ctf-forensics skills/ctf-forensics
git mv ctf-malware skills/ctf-malware
git mv ctf-misc skills/ctf-misc
git mv ctf-osint skills/ctf-osint
git mv ctf-pwn skills/ctf-pwn
git mv ctf-reverse skills/ctf-reverse
git mv ctf-web skills/ctf-web
git mv ctf-writeup skills/ctf-writeup
git mv solve-challenge skills/solve-challenge
```

- [ ] **Step 2: Verify git status and file counts**

Run:
```bash
python -c "from pathlib import Path; skills = list(Path('skills').glob('*/SKILL.md')); assert len(skills) == 11, f'Expected 11, got {len(skills)}'"
```
Expected: Exit code 0.

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor: relocate skills into skills/ directory"
```

---

### Task 3: Update Test Discovery

**Files:**
- Modify: `tests/test_skill_frontmatter.py`
- Modify: `tests/test_cross_references.py`
- Modify: `tests/test_skill_discoverability.py`

**Interfaces:**
- Consumes: `skills/*/SKILL.md`
- Produces: Passing test suite across all frontmatter and cross-reference tests.

- [ ] **Step 1: Update `tests/test_skill_frontmatter.py`**

Replace `_discover_skills()`:
```python
def _discover_skills() -> list[Path]:
    """Find all directories containing a SKILL.md file."""
    skills_dir = REPO_ROOT / "skills"
    if skills_dir.is_dir():
        skills = sorted(p.parent for p in skills_dir.glob("*/SKILL.md"))
        if skills:
            return skills
    return sorted(p.parent for p in REPO_ROOT.glob("*/SKILL.md"))
```

- [ ] **Step 2: Update `tests/test_cross_references.py`**

Replace lines defining `SKILL_DIRS`:
```python
def _discover_skills() -> list[Path]:
    skills_dir = REPO_ROOT / "skills"
    if skills_dir.is_dir():
        skills = sorted(p.parent for p in skills_dir.glob("*/SKILL.md"))
        if skills:
            return skills
    return sorted(p.parent for p in REPO_ROOT.glob("*/SKILL.md"))

SKILL_DIRS = _discover_skills()
```

- [ ] **Step 3: Update `tests/test_skill_discoverability.py`**

In `_load_descriptions()`:
```python
def _load_descriptions() -> dict[str, dict[str, set[str]]]:
    """Load positive and negative tokens from each core skill description."""
    descriptions: dict[str, dict[str, set[str]]] = {}
    skills_dir = REPO_ROOT / "skills"
    pattern = "*/SKILL.md"
    search_paths = sorted(skills_dir.glob(pattern)) if skills_dir.is_dir() else sorted(REPO_ROOT.glob(pattern))
    for skill_path in search_paths:
        name = skill_path.parent.name
        if name not in CORE_SKILLS:
            continue
        text = skill_path.read_text(encoding="utf-8")
        fm = _parse_frontmatter(text)
        if fm is None:
            continue
        desc = fm["description"]
        positive_text, _, negative_text = desc.partition("Do not use")
        descriptions[name] = {
            "positive": _tokenize(positive_text),
            "negative": _tokenize(negative_text),
        }
    return descriptions
```

- [ ] **Step 4: Run pytest to verify**

Run:
```bash
python -m pytest tests/ -v
```
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/
git commit -m "test: update skill discovery paths to support skills/ directory"
```

---

### Task 4: Update Tool Scripts

**Files:**
- Modify: `scripts/generate_catalog.py`
- Verify: `scripts/skill_security_auditor.py`

**Interfaces:**
- Consumes: `skills/*/SKILL.md`
- Produces: Working HTML skill catalog generation and security auditor.

- [ ] **Step 1: Update `discover_skills()` in `scripts/generate_catalog.py`**

```python
def discover_skills() -> list[Path]:
    """Find all directories containing a SKILL.md."""
    skills_dir = REPO_ROOT / "skills"
    if skills_dir.is_dir():
        skills = sorted(p.parent for p in skills_dir.glob("*/SKILL.md"))
        if skills:
            return skills
    return sorted(p.parent for p in REPO_ROOT.glob("*/SKILL.md"))
```

- [ ] **Step 2: Verify `scripts/generate_catalog.py` runs**

Run:
```bash
python scripts/generate_catalog.py
```
Expected: Exit code 0, `_site/index.html` successfully generated.

- [ ] **Step 3: Test `scripts/skill_security_auditor.py`**

Run:
```bash
python scripts/skill_security_auditor.py skills/ctf-web --json
```
Expected: JSON output with scan findings and summary.

- [ ] **Step 4: Commit**

```bash
git add scripts/generate_catalog.py
git commit -m "chore: update catalog generator for skills/ directory"
```

---

### Task 5: Add Custom Subagent `agents/ctf-solver.md`

**Files:**
- Create: `agents/ctf-solver.md`

**Interfaces:**
- Produces: Claude Code custom subagent accessible via `@ctf-skills:ctf-solver`.

- [ ] **Step 1: Create `agents/ctf-solver.md`**

Write the subagent definition to `agents/ctf-solver.md`:

```markdown
---
name: ctf-solver
description: Autonomous CTF challenge triage and solver specialist. Use when given a Capture The Flag challenge, suspicious binary, web service, memory dump, PCAP, cipher, or CTF archive to analyze and solve.
effort: high
tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch, WebSearch
---

You are a world-class Capture The Flag (CTF) competitor and offensive security researcher.
Your mission is to analyze challenges, identify the vulnerability category, develop reliable exploits or decoding scripts, and capture the flag.

### Methodology:
1. **Initial Triage:**
   - Inspect challenge files (file format, architecture, security mitigations via `checksec`, entropy, strings).
   - Identify the dominant category: Web, Pwn, Crypto, Reverse, Forensics, OSINT, Malware, AI/ML, or Misc.
   - For ambiguous challenges, apply first-pass triage using the `solve-challenge` methodology.

2. **Hypothesis & Recon:**
   - Review relevant techniques from the bundled category skills (`skills/ctf-*`).
   - Identify specific attack vectors, constraint bypasses, or oracle behaviors.

3. **Exploitation & Automation:**
   - Write clean, standalone Python solver scripts using standard tools (`pwntools`, `z3-solver`, `requests`, `cryptography`, etc.).
   - Test locally first if binaries or docker containers are provided before sending payloads to remote targets.

4. **Flag Capture & Reporting:**
   - Locate and verify the flag format (e.g., `flag{...}`, `CTF{...}`).
   - Document the solution clearly with reproducible steps.
```

- [ ] **Step 2: Commit**

```bash
git add agents/ctf-solver.md
git commit -m "feat: add ctf-solver custom subagent for Claude Code"
```

---

### Task 6: Update CI Workflows

**Files:**
- Modify: `.github/workflows/skill-security-audit.yml`

**Interfaces:**
- Consumes: Git diff paths
- Produces: Correct skill directory identification on pull requests and pushes.

- [ ] **Step 1: Update skill name extraction in `.github/workflows/skill-security-audit.yml`**

Locate lines where skill name is parsed:
```bash
skill_name=$(echo "$file" | cut -d/ -f1)
```
Update to handle `skills/` path:
```bash
if echo "$file" | grep -q "^skills/"; then
  skill_name=$(echo "$file" | cut -d/ -f2)
else
  skill_name=$(echo "$file" | cut -d/ -f1)
fi
```
And ensure checking `[ -d "skills/$skill_name" ]` or `[ -d "$skill_name" ]`.

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/skill-security-audit.yml
git commit -m "ci: update skill detection to support skills/ directory in security audit workflow"
```

---

### Task 7: Update Documentation (`README.md` & `CONTRIBUTING.md`)

**Files:**
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`

**Interfaces:**
- Produces: Comprehensive user guides for Claude Code plugin installation, usage, commands, and subagents.

- [ ] **Step 1: Update `README.md`**

Add a dedicated **Claude Code Plugin** section right under Installation:
- Explaining `--plugin-dir ./` for local development
- Explaining `~/.claude/skills/ctf-skills/` auto-load
- Explaining `/ctf-skills:solve-challenge` and `/ctf-skills:<category>`
- Explaining `@ctf-skills:ctf-solver` subagent
- Updating file structure references to `skills/`

- [ ] **Step 2: Update `CONTRIBUTING.md`**

Update the section on adding techniques and creating new categories to reflect the `skills/` path.

- [ ] **Step 3: Commit**

```bash
git add README.md CONTRIBUTING.md
git commit -m "docs: document Claude Code plugin setup, commands, and subagent"
```

---

### Task 8: Verification & Final Audit

**Files:**
- All touched files

**Interfaces:**
- Verifies: Everything works end-to-end.

- [ ] **Step 1: Run full pytest suite**
```bash
python -m pytest tests/ -v
```
Expected: 100% pass rate.

- [ ] **Step 2: Run catalog generator**
```bash
python scripts/generate_catalog.py
```
Expected: Exit code 0.

- [ ] **Step 3: Run security audit on skills**
```bash
python scripts/skill_security_auditor.py skills/ctf-web --strict --json
```
Expected: PASS or WARN (no unexpected CRITICAL failure).

- [ ] **Step 4: Verify git working directory is clean**
```bash
git status
```
Expected: Clean working tree.
