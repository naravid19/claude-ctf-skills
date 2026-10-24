# claude-ctf-skills

All notable changes to this project are documented here. This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.2.0 — 2026-10-24

Upstream sync from [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) (`c332c7b` through `2b396aa`, 13 commits), translating `<skill>/` paths to `skills/<skill>/` per ADR 0001.

### Added

- **New skill**: `ctf-similar-search` — Tavily-API-backed search/extract for similar CTF writeups (needs `TAVILY_API_KEY`); scripts relocated to `skills/ctf-similar-search/scripts/` to match the repo's skill-scoped-script convention.
- **`ctf-pwn/pwnable-tw/`**: 43 solved pwnable.tw challenge writeups plus an index `README.md`, as reference material for `ctf-pwn` and the `ctf-solver` subagent.
- **New technique docs**: `ctf-reverse/mba-simplification.md` (msynth), `ctf-reverse/radare2-r2pipe.md` (r2ghidra, ESIL, r2frida), `ctf-pwn/attack-playbook.md`, `ctf-pwn/static-signals.md`, `ctf-web/auth-infra.md`, `ctf-web/auth-jwt.md`, `ctf-web/client-side.md`, `ctf-misc/audio.md`, `solve-challenge/difficulty-routing.md`.
- **MCP server integration guides** (`tools-mcp.md`) for `ctf-pwn`, `ctf-reverse`, `ctf-web`, `ctf-osint`, `ctf-malware` (IDA/Ghidra/JADX/WinDbg/Playwright/Burp).
- `tests/test_reverse_r2_snippets.py` for the new radare2/r2pipe snippets.

### Changed

- Updated crypto/forensics/osint/misc/pwn/reverse/web technique docs, `scripts/install_ctf_tools.sh`, `tests/test_pwn_scripts.py`, and `skills/ctf-pwn/scripts/shellcraft_asm.py` with upstream fixes and additions.
- README category table and architecture diagram counts refreshed for the categories touched by this sync.
- CONTRIBUTING.md: documented the `TAVILY_API_KEY` external-service requirement for `ctf-similar-search`, next to the existing PayloadsAllTheThings note.

### Fixed

- `tests/test_pwn_scripts.py`: the real-import test pointed `_SCRIPTS_DIR` at the pre-plugin `ctf-pwn/scripts/` path (missed in the ADR 0001 path translation); now `skills/ctf-pwn/scripts/`. The test still skips when `pwntools` is absent.

### Not ported

- Upstream's `evals/` (promptfoo/Node eval suite with its own `package-lock.json` and binary fixtures) — different stack from this repo's pytest `tests/`; not adopted.
- Upstream's `.opencode/` agent definitions — a different agent framework, not the Claude Code plugin shape this repo targets.

### Verification

- `pytest tests/` (minus the pre-existing, unrelated `test_skill_security_auditor.py` import error), `scripts/verify_crypto_examples.py`, and `markdownlint-cli2` ran clean on every phase.
- `lychee` (link checking) was **not** run for this sync — it needs network access this session didn't exercise. Flagging it here rather than leaving it a silent gap; a future sync (or this repo's CI) should run `lychee` over the new/changed files before relying on this entry as a complete verification record.

## 1.1.0 — 2026-09-27

Major upstream sync from [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) (modernization commit `61c2efe` through `c332c7b`), incorporating over 10,000 lines of modern CTF attack techniques, scripts, and test suites.

### Added

- **New CTF reference techniques**:
  - `skills/ctf-crypto/dh-attacks.md`: Classic and modern Diffie-Hellman attacks (confinement, Lim-Lee, small subgroup).
  - `skills/ctf-crypto/modern-ciphers-4.md`: Poly1305 key recovery, ChaCha20/Poly1305 state manipulation.
  - `skills/ctf-crypto/post-quantum.md`: Post-quantum cryptography vulnerabilities and lattice foundations.
  - `skills/ctf-reverse/unicorn-emulation.md`: Comprehensive Unicorn Engine CPU emulation guide for shellcode, custom archs, and crypto routine recovery.
  - `skills/ctf-web/pat-reference.md`: Port Address Translation and advanced network tunneling reference.
  - `skills/ctf-web/python-requests.md`: Robust Python HTTP exploitation patterns and concurrency.
- **Skill-scoped exploit scripts**:
  - `skills/ctf-pwn/scripts/`: `fmtstr_payload_suite.py`, `ret2libc_two_stage.py`, `seccomp_orw_generator.py`, `shellcraft_asm.py`, `srop_execve.py`.
  - `skills/ctf-web/scripts/`: `async_fuzz.py` for high-throughput asynchronous parameter fuzzing.
- **New test suites**:
  - `tests/test_crypto_snippets.py`, `tests/test_misc_snippets.py`, `tests/test_pwn_scripts.py`, `tests/test_web_requests_snippets.py`.
- **Engineering documentation & architecture**:
  - `CONTEXT.md`: Project domain glossary for Claude Code plugin layout and conventions.
  - `docs/adr/0001-claude-plugin-layout.md`: Architectural decision record for plugin directory separation.
  - `docs/adr/0002-catalog-ui-and-documentation-architecture.md`: Architectural decision record for web catalog UI and documentation standards.
  - `docs/agents/`: Configuration for issue tracker, triage labels, and domain doc consumption.
- **Web Catalog (GitHub Pages)**:
  - Redesigned `scripts/generate_catalog.py` with Terminal Cyber Dark aesthetic (Zinc-950/Cyan/Emerald palette).
  - Added zero-dependency, real-time client-side search across skills, techniques, and scripts.
  - Added category filter pills and 1-click clipboard copy widget for `/plugin marketplace add`.
  - Added first-class discovery and tags for skill-scoped exploit scripts.

### Changed

- Complete overhaul of `README.md`: Added Mermaid workflow diagram, comprehensive category and tool matrix (11 categories, 113 technique documents, 6 exploit scripts), detailed exploit template guides, toolchain installation groups, and testing/auditing workflows.
- Modernized `ctf-crypto` techniques away from SageMath reliance toward pure Python, `fpylll`, `gmpy2`, and `sympy`.
- Greatly expanded `ctf-misc/pyjails.md` and `ctf-misc/bashjails.md` with modern audit hook trampolines and BASH_ENV vectors.
- Enhanced `scripts/install_ctf_tools.sh` with installations for `unicorn`, `capstone`, `ropper`, and `fpylll`.
- Updated `CONTRIBUTING.md` with PayloadsAllTheThings external bulk wordlist guidelines and crypto verification testing commands.
- Enhanced `scripts/verify_crypto_examples.py` with automatic `skills/` path detection for plugin directory layouts.

### Fixed

- `scripts/skill_security_auditor.py`: Redacted credentials (`[REDACTED]`) to prevent CodeQL clear-text logging alerts and secret leaks.
- Removed dead `libc.blukat.me` links in format-string documentation.
- Fixed `skill-security-audit-comment.yml` workflow to skip gracefully when report artifacts are absent.

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
