# ADR 0001: Claude Code Plugin Layout & Upstream Synchronization Architecture

## Status
Accepted

## Date
2026-09-27

## Context
The upstream project (`ljagiello/ctf-skills`) maintains all CTF skills at the root of the repository (`ctf-crypto/`, `ctf-pwn/`, etc.). 

To distribute these skills seamlessly as a Claude Code plugin with its own marketplace registration (`/plugin marketplace add naravid19/claude-ctf-skills` and `/plugin install ctf-skills@claude-ctf-skills`), the repository requires:
1. Manifests under `.claude-plugin/` (`plugin.json`, `marketplace.json`).
2. Skills organized inside a standard `skills/` subdirectory (`skills/<skill-name>/`).
3. Autonomous subagents under `agents/` (`agents/ctf-solver.md`).
4. Skill-specific exploit scripts placed inside `skills/<skill-name>/scripts/` rather than polluting repo-level tooling.

## Decision
1. Standardize on the `skills/<skill-name>/` directory layout for all CTF skill categories.
2. Colocate skill-specific exploitation and helper scripts in `skills/<skill-name>/scripts/` (e.g. `skills/ctf-pwn/scripts/` and `skills/ctf-web/scripts/`).
3. Keep repository developer tooling in the root `scripts/` directory (`generate_catalog.py`, `install_ctf_tools.sh`, `skill_security_auditor.py`).
4. Maintain `skills/`-aware discovery in tests (`tests/test_skill_discoverability.py`, `tests/test_skill_frontmatter.py`, `tests/test_cross_references.py`, `tests/test_catalog_links.py`) and catalog generation.
5. In upstream synchronization cycles, sync documentation and skill-scoped scripts directly into `skills/`, leaving plugin infrastructure and custom tests untouched.

## Consequences
- **Positive**: Enables 1-click marketplace installation and subagent invocation in Claude Code.
- **Positive**: Skills are modular, clean, and self-contained with their own scripts.
- **Trade-off**: Direct git merges from upstream root will not match paths automatically; syncs must translate paths from `<skill>/` to `skills/<skill>/`.
