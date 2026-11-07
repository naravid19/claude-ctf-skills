# ADR 0003: Multi-Subagent Specialist Architecture & Fork-Owned Overlay Boundaries

## Status
Accepted

## Date
2026-11-07

## Context
Upstream (`ljagiello/ctf-skills`) introduced `.opencode/agents/` containing a team leader (`ctf-leader.md`) and category-specific agents for the OpenCode agent platform, which are excluded from this repository per ADR 0002.

In `claude-ctf-skills`, we previously maintained a single monolithic subagent (`agents/ctf-solver.md`) under ADR 0001. As CTF challenges grow in domain depth (e.g. heap feng shui, lattice CVP reduction, Bleichenbacher padding oracles, Unicorn emulation), a single context prompt leads to prompt dilution, broad tool allowance bloat, and higher token usage.

Furthermore, as `claude-ctf-skills` adds Fork-Owned Overlay capabilities (such as 9 Claude Code subagents and additional Exploit Automation Suite generators in `skills/<category>/scripts/`), any divergence inside upstream-mirrored `skills/*/*.md` files (especially the tail of `## Additional Resources` in `SKILL.md` where upstream appends new technique files) would cause recurring 3-way merge conflicts during Upstream Mirroring.

## Decision
1. **Primary Orchestrator**: Retain `agents/ctf-solver.md` as the primary user-facing orchestrator (`mode: primary`), responsible for initial challenge triage, category determination, and team coordination (`Task` tool enabled).
2. **Specialist Subagents**: Introduce 8 specialized category subagents under `agents/`:
   - `agents/ctf-pwn.md` (low-level binary exploitation, ROP, heap, format strings)
   - `agents/ctf-web.md` (web security, auth bypass, injection, fuzzing)
   - `agents/ctf-crypto.md` (mathematical cryptanalysis, RSA, ECC, lattices, padding oracles)
   - `agents/ctf-reverse.md` (decompilation, emulation, MBA simplification)
   - `agents/ctf-forensics.md` (PCAP, memory analysis, disk images, stego)
   - `agents/ctf-malware.md` (script deobfuscation, shellcode, YARA rules)
   - `agents/ctf-misc.md` (pyjail/bashjail sandbox escapes, esoteric ciphers)
   - `agents/ctf-osint.md` (geolocation, identity correlation, DNS recon)
3. **Zero-Diff `SKILL.md` Policy (Upstream Content Parity)**:
   - Keep `skills/*/*.md` (including `SKILL.md` frontmatter key order and `## Additional Resources` lists) byte-for-byte identical to upstream `ljagiello/ctf-skills` (except `skills/ctf-similar-search/SKILL.md` which translates `./search.sh` to `./scripts/search.sh` per ADR 0001).
   - Index Fork-Owned Overlay scripts (`skills/<category>/scripts/*.py`) inside `agents/ctf-*.md`, `README.md`, and automatically via `scripts/generate_catalog.py` — never by appending fork-only lines to the tail of `## Additional Resources` in `SKILL.md`.
4. **Script Coexistence Policy**:
   - Fork-Owned Overlay scripts in `skills/<category>/scripts/` coexist additively alongside upstream scripts. If upstream later introduces a script with overlapping functionality, upstream wins or the capabilities are merged into the upstream filename.
5. **Automated Guardrails**:
   - Validate all agent definitions, frontmatter, and target path existence (`skills/.../*.md` and `skills/.../scripts/*.py`) via `tests/test_agents.py`.

## Consequences
- **Positive**: Clean context isolation during deep multi-stage CTF solving; users can directly invoke specialists (e.g. `@ctf-skills:ctf-pwn`) or use `@ctf-skills:ctf-solver` for automatic orchestration.
- **Positive**: 135 out of 136 `.md` files in `skills/` maintain 100% byte-for-byte parity with upstream, eliminating merge conflicts during future upstream syncs.
- **Positive**: If upstream renames a technique `.md` file or adds a new `.py` script in `skills/<category>/scripts/`, `tests/test_agents.py` immediately alerts maintainers to update the corresponding specialist subagent.
