# Design Specification: ctf-skills Claude Code Plugin Migration

**Date:** 2026-09-08  
**Topic:** Claude Code Plugin Migration for `ctf-skills`  
**Status:** Validated / Ready for Planning  

---

## 1. Overview & Motivation

The `ctf-skills` repository is a comprehensive collection of offensive security techniques and Agent Skills for solving Capture The Flag (CTF) challenges across multiple categories (Web, Pwn, Crypto, Reverse Engineering, Forensics, OSINT, Malware, AI/ML, and Misc).

To provide first-class integration with [Claude Code](https://code.claude.com/docs/en/plugins), this specification outlines restructuring the repository into a fully compliant Claude Code Plugin. The plugin enables automatic contextual skill invocation, direct command execution (e.g. `/ctf-skills:solve-challenge`), and dispatching a dedicated autonomous subagent (`@ctf-skills:ctf-solver`).

---

## 2. Architecture & Directory Layout

The repository is restructured to adhere to the canonical Claude Code plugin directory structure:

```text
ctf-skills/
├── .claude-plugin/
│   └── plugin.json                    # Plugin manifest metadata
├── skills/                            # Relocated skill directories
│   ├── ctf-ai-ml/
│   │   ├── SKILL.md
│   │   ├── adversarial-ml.md
│   │   ├── llm-attacks.md
│   │   └── model-attacks.md
│   ├── ctf-crypto/
│   │   ├── SKILL.md
│   │   └── ... (.md technique files)
│   ├── ctf-forensics/
│   ├── ctf-malware/
│   ├── ctf-misc/
│   ├── ctf-osint/
│   ├── ctf-pwn/
│   ├── ctf-reverse/
│   ├── ctf-web/
│   ├── ctf-writeup/
│   └── solve-challenge/
├── agents/                            # Claude Code custom subagents
│   └── ctf-solver.md
├── scripts/                           # Tooling and audit scripts
│   ├── generate_catalog.py
│   ├── install_ctf_tools.sh
│   └── skill_security_auditor.py
├── tests/                             # Python pytest suite
│   ├── test_cross_references.py
│   ├── test_skill_discoverability.py
│   ├── test_skill_frontmatter.py
│   └── test_skill_security_auditor.py
├── .github/workflows/                 # CI workflows
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

---

## 3. Plugin Manifest: `.claude-plugin/plugin.json`

Create `.claude-plugin/plugin.json` adhering to the official Claude Code manifest schema:

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

*Note:* Because components are placed in the default `skills/` and `agents/` directories at the plugin root, no explicit path overrides are required in the manifest.

---

## 4. Custom Subagent: `agents/ctf-solver.md`

Add a specialized subagent definition in `agents/ctf-solver.md` to support autonomous CTF challenge solving when invoked via `@ctf-skills:ctf-solver` or dispatched by Claude Code:

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

---

## 5. Test Suite & Scripts Compatibility Updates

### 5.1 `tests/test_skill_frontmatter.py`
Update `_discover_skills()` to search in `skills/*/SKILL.md` while maintaining fallback support:
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

### 5.2 `tests/test_cross_references.py`
Update `SKILL_DIRS` discovery to look under `skills/*/SKILL.md`. Ensure that relative links between technique files (which are internal to `skills/<skill_name>/`) continue to resolve without issue.

### 5.3 `tests/test_skill_discoverability.py`
Update `_load_descriptions()` to load `SKILL.md` from `skills/` first, ensuring discovery scoring algorithms continue to pass.

### 5.4 `scripts/generate_catalog.py`
Update `discover_skills()` to check `skills/*/SKILL.md` first, so GitHub Pages generation continues to function seamlessly.

### 5.5 `scripts/skill_security_auditor.py`
Ensure path arguments like `skills/ctf-web` or full paths are correctly scanned.

---

## 6. CI Workflow Updates

In `.github/workflows/skill-security-audit.yml`:
Update the step that parses changed files into skill directory names. When files are in `skills/<skill_name>/...`, extract the skill name from the 2nd path segment rather than the 1st segment:
```bash
if echo "$file" | grep -q "^skills/"; then
  skill_name=$(echo "$file" | cut -d/ -f2)
else
  skill_name=$(echo "$file" | cut -d/ -f1)
fi
```

---

## 7. Documentation Updates

### 7.1 `README.md`
- Add a new dedicated **Claude Code Plugin** section:
  - Local loading: `claude --plugin-dir ./`
  - Skills-directory loading: clone to `~/.claude/skills/ctf-skills`
  - Calling skills: `/ctf-skills:solve-challenge <prompt>`, `/ctf-skills:ctf-web`, etc.
  - Calling subagent: `@ctf-skills:ctf-solver`
- Update the repository structure documentation to reflect `skills/`.
- Preserve existing Friday Studio and Agent Skills instructions.

### 7.2 `CONTRIBUTING.md`
- Update instructions for creating new skills: create in `skills/<new-category>/SKILL.md`.
- Update test commands and directory references.

---

## 8. Verification & Success Criteria

1. **Manifest Validation:**
   - `.claude-plugin/plugin.json` is syntactically valid JSON and adheres to the Claude Code plugin manifest schema.
2. **Directory Integrity:**
   - Exactly 11 skill directories are present under `skills/`, containing all 92+ technique markdown files intact.
   - `agents/ctf-solver.md` exists and contains valid frontmatter (`name`, `description`, `effort`, `tools`).
3. **Automated Testing:**
   - Run `pytest tests/ -v` and achieve 100% passing tests across all test modules (`test_skill_frontmatter.py`, `test_cross_references.py`, `test_skill_discoverability.py`, `test_skill_security_auditor.py`).
4. **Security Audit:**
   - Run `python scripts/skill_security_auditor.py skills/ctf-web` to confirm security scanning works against the new path layout.
