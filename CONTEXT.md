# Domain Glossary

Glossary of domain concepts and terminology for `claude-ctf-skills`.

## Terms

### Plugin Layout
A packaged bundle of agent skills, configuration, and subagents conforming to the Claude Code plugin specification (`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`), installable via the `/plugin` command. The key structural divergence from upstream is that skills live under `skills/<name>/` instead of the repo root, and subagents live under `agents/`.

### Claude Code Plugin
Synonym for Plugin Layout. See above.

### CTF Solver Subagent
An autonomous primary subagent definition (`agents/ctf-solver.md`, `mode: primary`) invoked within Claude Code to act as team leader, orchestrating challenge analysis, triage, and delegation to specialist subagents.

### Specialist Subagents
Domain-focused subagents defined under `agents/` (`ctf-pwn`, `ctf-web`, `ctf-crypto`, `ctf-reverse`, `ctf-forensics`, `ctf-malware`, `ctf-misc`, `ctf-osint`) providing deep expertise, scoped tooling, and direct integration with corresponding category skills.

### Multi-Subagent Hierarchy
The cooperative architecture where `ctf-solver` conducts initial triage and delegates category-specific deep work to one or more specialist subagents without polluting the parent conversation context.

### Skill-Scoped Scripts
Self-contained helper, exploit, or fuzzing scripts stored directly within an individual skill's folder (`skills/<category>/scripts/`), allowing the skill to function as an independent portable toolkit.

### Repo Tooling
Infrastructure and developer tools stored in the repository root `scripts/` directory (e.g., catalog generation, security auditing, and system tool installation).

### Upstream Mirroring
The process of synchronizing updated CTF attack techniques, reference guides, and algorithmic implementations from the upstream repository (`ljagiello/ctf-skills`) into this plugin repository while preserving plugin directory structure.

### Catalog Generator
The static website generator script (`scripts/generate_catalog.py`) that compiles skill frontmatter, technique docs, and exploit scripts into an interactive, zero-dependency search dashboard deployed to GitHub Pages (`_site/`).

### Exploit Automation Suite
The collection of verified, ready-to-run Python exploitation templates (e.g. format strings, two-stage ret2libc, SROP, seccomp ORW, async HTTP fuzzers, CBC padding oracle, and multi-vector RSA solvers) colocated in skill `scripts/` directories.

### Triage Roles
The five canonical roles used to classify incoming tasks, issues, and pull requests:
- `needs-triage`: Awaiting evaluation by maintainers.
- `needs-info`: Blocked awaiting additional details from reporter.
- `ready-for-agent`: Fully specified and ready for autonomous agent execution.
- `ready-for-human`: Requires manual human implementation or review.
- `wontfix`: Out of scope or will not be addressed.
