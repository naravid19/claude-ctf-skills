# ADR 0002: Upstream Sync Scope — Excluded Infrastructure

## Status
Accepted

## Date
2026-10-24

## Context
The upstream project (`ljagiello/ctf-skills`) has, as of commit `2b396aa`, grown two infrastructure trees that sit outside the `<skill>/` content ADR 0001 already covers syncing:

1. `evals/` — a promptfoo (Node.js) eval suite for grading skill routing and rule adherence, with its own `package.json`/`package-lock.json` (9,851 lines) and binary test fixtures.
2. `.opencode/` — agent definitions (`ctf-leader.md`, per-category agents, `opencode.json`) for the OpenCode agent framework, not Claude Code.

Both are genuinely useful upstream work, but neither maps onto this repo's plugin shape: our tests live in `tests/` as pytest, and our autonomous agent is `agents/ctf-solver.md` in Claude Code's subagent format.

## Decision
Do not port `evals/` or `.opencode/` during upstream sync cycles. Each sync's CHANGELOG entry notes their presence upstream under "Not ported" so future syncs don't re-litigate the same question for the same upstream trees.

If this repo later wants eval-suite parity, that is a separate decision (e.g. a pytest-native eval harness, not a wholesale promptfoo/Node import) and gets its own ADR. If it later wants OpenCode compatibility, that is also a separate decision, not a byproduct of a routine content sync.

## Consequences
- **Positive**: Sync cycles stay scoped to content (`skills/`, skill-scoped `scripts/`, root `scripts/`, `tests/`) and don't drag in a second language runtime or a second agent framework as a side effect.
- **Trade-off**: This repo's own skill-eval coverage (routing accuracy, rule adherence) will lag upstream's `evals/` suite until/unless a native equivalent is built.
