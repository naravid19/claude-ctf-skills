# ADR 0003: Multi-Subagent Specialist Architecture

## Status
Accepted

## Date
2026-11-07

## Context
Upstream (`ljagiello/ctf-skills`) introduced `.opencode/agents/` containing a team leader (`ctf-leader.md`) and category-specific agents for the OpenCode agent platform.

In `claude-ctf-skills`, we previously maintained a single monolithic subagent (`agents/ctf-solver.md`) under ADR 0001. As CTF challenges grow in domain depth (e.g. heap feng shui, lattice CVP reduction, Unicorn emulation), a single context prompt leads to prompt dilution, broad tool allowance bloat, and higher token usage.

Claude Code plugins natively support multiple subagents defined as Markdown files under `agents/`.

## Decision
1. Retain `agents/ctf-solver.md` as the primary user-facing orchestrator (`mode: primary`), responsible for initial challenge triage, category determination, and team coordination.
2. Introduce 8 specialized category subagents under `agents/`:
   - `agents/ctf-pwn.md` (low-level binary exploitation, ROP, heap, format strings)
   - `agents/ctf-web.md` (web security, auth bypass, injection, fuzzing)
   - `agents/ctf-crypto.md` (mathematical cryptanalysis, RSA, ECC, lattices)
   - `agents/ctf-reverse.md` (decompilation, emulation, MBA simplification)
   - `agents/ctf-forensics.md` (PCAP, memory analysis, disk images, stego)
   - `agents/ctf-malware.md` (script deobfuscation, shellcode, YARA rules)
   - `agents/ctf-misc.md` (pyjail/bashjail sandbox escapes, esoteric ciphers)
   - `agents/ctf-osint.md` (geolocation, identity correlation, DNS recon)
3. Each specialist subagent links directly to its respective skill docs under `skills/ctf-*/` and exploit automation scripts under `skills/ctf-*/scripts/`.
4. Validate all agent definitions via `tests/test_agents.py`.

## Consequences
- **Positive**: Clean context isolation during deep multi-stage CTF solving; users can directly invoke specialists (e.g. `@ctf-skills:ctf-pwn`) or use `@ctf-skills:ctf-solver` for automatic orchestration.
- **Positive**: Complies with Claude Code plugin specifications without requiring an external agent runner like OpenCode.
- **Trade-off**: Requires maintaining 9 agent definitions in sync with skill additions.
