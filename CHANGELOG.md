# claude-ctf-skills

All notable changes to this project are documented here. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.0 — 2026-09-08

First release of **claude-ctf-skills** as a Claude Code plugin, built on [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) (MIT).

### Added

- **Claude Code plugin manifest** (`.claude-plugin/plugin.json`) — installs as the `ctf-skills` plugin.
- **Self-marketplace** (`.claude-plugin/marketplace.json`) — the repo is its own marketplace, so `/plugin marketplace add naravid19/claude-ctf-skills` then `/plugin install ctf-skills@claude-ctf-skills` works.
- **`ctf-solver` subagent** — autonomous end-to-end challenge triage and solving in its own context (`@ctf-skills:ctf-solver`).
- **9 category skills** — `ctf-web`, `ctf-pwn`, `ctf-reverse`, `ctf-crypto`, `ctf-forensics`, `ctf-misc`, `ctf-ai-ml`, `ctf-malware`, `ctf-osint` — model-invoked, selected automatically by challenge context.
- **2 orchestrator skills** — `/ctf-skills:solve-challenge` (triage and route) and `/ctf-skills:ctf-writeup` (submission-style writeup).
- **GitHub Pages skill catalog** — generated from `SKILL.md` frontmatter, deployed on push to `main`.

### Changed

- Relocated all skills into `skills/<name>/SKILL.md` per the Claude Code plugin layout; skill discovery, the catalog generator, and CI updated to match.
- Rewrote the README around the plugin (install paths, model-invoked vs user-invoked skills, workflow, updating) and credited the upstream project.
- Dual-attributed the MIT `LICENSE` — original author retained, plugin packaging added.

### Fixed

- GitHub Pages catalog links now use the repo-relative `skills/…` path, so technique and `SKILL.md` links resolve instead of 404ing. Guarded by `tests/test_catalog_links.py`.
