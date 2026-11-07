# Domain Glossary

Glossary of domain concepts and terminology for `claude-ctf-skills`.

## Terms

### Plugin Layout
A packaged bundle of agent skills, configuration, and subagents conforming to the Claude Code plugin specification, installable via the `/plugin` command.

### Claude Code Plugin
Synonym for Plugin Layout. See above.

### CTF Solver Subagent
An autonomous primary subagent invoked within Claude Code to act as team leader, orchestrating challenge analysis, triage, and delegation to specialist subagents.

### Specialist Subagents
Domain-focused subagents providing deep category expertise, scoped tooling, and direct integration with corresponding category skills and exploit automation scripts.

### Multi-Subagent Hierarchy
The cooperative architecture where the primary CTF Solver Subagent conducts initial triage and delegates category-specific deep work to one or more Specialist Subagents without polluting the parent conversation context.

### Skill-Scoped Scripts
Self-contained helper, exploit, or fuzzing scripts stored directly within an individual skill's folder, allowing the skill to function as an independent portable toolkit.

### Repo Tooling
Infrastructure and developer tools stored in the repository root for catalog generation, security auditing, and environment setup.

### Upstream Mirroring
The process of synchronizing updated CTF attack techniques, reference guides, and algorithmic implementations from the upstream knowledge base into this plugin repository while preserving plugin structure.

### Upstream Content Parity
The invariant where skill reference documents and frontmatter match upstream content verbatim, preventing merge conflicts during Upstream Mirroring.

### Fork-Owned Overlay
Capabilities, subagents, exploit generators, and plugin manifests maintained exclusively by this repository that extend upstream knowledge without modifying upstream-mirrored markdown files.

### Catalog Generator
The static website generator that compiles skill metadata, technique docs, and exploit scripts into an interactive, zero-dependency search dashboard.

### Exploit Automation Suite
The collection of verified, ready-to-run exploitation and cryptanalysis templates colocated in skill script directories.

### Triage Roles
The five canonical roles used to classify incoming tasks, issues, and pull requests:
- `needs-triage`: Awaiting evaluation by maintainers.
- `needs-info`: Blocked awaiting additional details from reporter.
- `ready-for-agent`: Fully specified and ready for autonomous agent execution.
- `ready-for-human`: Requires manual human implementation or review.
- `wontfix`: Out of scope or will not be addressed.
