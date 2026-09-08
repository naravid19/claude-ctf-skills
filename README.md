# CTF Skills

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2.svg)](https://docs.anthropic.com/en/docs/claude-code)
![Skills](https://img.shields.io/badge/skills-9%20categories%20%2B%20solver-blue.svg)

A **Claude Code plugin** that turns your agent into a CTF competitor — 9 category skills, 107 battle-tested technique files, and an autonomous `ctf-solver` subagent. Not vibe hacking: every technique is distilled from real CTFTime writeups.

> Built on [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills) (MIT). This project packages it as a Claude Code plugin and adds the autonomous `ctf-solver` subagent.

Works with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and any tool that supports the [Agent Skills](https://agentskills.io) spec.

## How it works

Skills are **model-invoked**: Claude reads the challenge, recognizes the category, and pulls in the matching skill automatically — you don't pick it. Each skill's `SKILL.md` carries a dense `description` so the model routes correctly (a web target loads `ctf-web`, a heap bug loads `ctf-pwn`), then loads only the technique files it needs for the challenge in front of it.

Two entry points you drive yourself:

- **`/ctf-skills:solve-challenge`** — first-pass triage that routes to the right category skill.
- **`@ctf-skills:ctf-solver`** — a dedicated subagent that triages, exploits, and captures the flag end to end in its own context.

## Installation (30 seconds)

<details open>
<summary><b>Claude Code — skills-directory plugin (recommended, auto-loads everywhere)</b></summary>

```bash
git clone https://github.com/naravid19/claude-ctf-skills ~/.claude/skills/ctf-skills
```

Loads on your next session as `ctf-skills`. Run `/reload-plugins` to pick it up now.
</details>

<details>
<summary><b>Claude Code — run locally without installing</b></summary>

```bash
claude --plugin-dir /path/to/claude-ctf-skills
```
</details>

<details>
<summary><b>Other agents — Agent Skills CLI</b></summary>

```bash
npx skills add naravid19/claude-ctf-skills
```
</details>

<details>
<summary><b>Friday Studio</b></summary>

Install [Friday](https://hellofriday.ai/) (macOS), open **Skills → + Add**, and import by reference (e.g. `naravid19/claude-ctf-skills/ctf-web`) or upload this repo as a folder. Reference them from any `workspace.yml`, or let agents load them by description.
</details>

## What's inside

**Category skills** — model-invoked, Claude selects them by challenge context:

| Skill | Files | Coverage |
|-------|:-----:|----------|
| **ctf-web** | 20 | XSS, SQLi, SSTI, SSRF, XXE, JWT, auth bypass, prototype pollution, file-upload RCE, Web3/Solidity |
| **ctf-pwn** | 18 | Buffer overflows, format strings, heap, ROP/ret2libc, shellcode, kernel, seccomp/sandbox escape |
| **ctf-reverse** | 18 | Binaries, APK, WASM, firmware, custom VMs, bytecode, anti-debug and anti-analysis |
| **ctf-crypto** | 16 | RSA, AES, ECC, lattices/LWE/CVP, PRNG, padding oracle, signatures, ZKP, number theory |
| **ctf-forensics** | 14 | Disk/memory images, PCAP, steganography, registry, Volatility, side-channel, audio/RF |
| **ctf-misc** | 12 | Encoding puzzles, pyjails, RF/SDR, esoteric langs, QR/audio, constraint solving |
| **ctf-ai-ml** | 3 | Adversarial examples, prompt injection, model extraction, membership inference, LoRA, LLM jailbreak |
| **ctf-malware** | 3 | Obfuscated scripts, C2 traffic, PE/.NET, shellcode, YARA, anti-analysis, IOC extraction |
| **ctf-osint** | 3 | Geolocation, DNS, username enumeration, reverse image search, Google dorking, Wayback |

**Orchestrators** — user-invoked, you run them directly:

| Skill | Invoke | What it does |
|-------|--------|--------------|
| **solve-challenge** | `/ctf-skills:solve-challenge <target>` | Triage an unknown challenge and route to the right skill |
| **ctf-writeup** | `/ctf-skills:ctf-writeup` | Turn a solved challenge into a clean writeup |
| **ctf-solver** | `@ctf-skills:ctf-solver <target>` | Autonomous subagent — triage → exploit → flag, end to end |

Every category skill's `SKILL.md` lists its full technique index and a **Prerequisites** section naming only the tools it needs.

## The basic workflow

Point it at a challenge and let it drive:

```text
/ctf-skills:solve-challenge ./chal            # a downloaded binary or archive
/ctf-skills:solve-challenge https://ctf.example.com/web/42   # a live target
```

It triages the challenge, loads the matching category skill, works the attack, and reports the flag. For a fully autonomous run in its own context, hand it to the subagent instead:

```text
@ctf-skills:ctf-solver ./chal
```

You never pick a category — the model recognizes it and pulls the right skill in on its own.

## Environment setup

Skills work out of the box; tooling is installed on demand. Before a competition you can pre-install everything:

```bash
bash scripts/install_ctf_tools.sh all
```

Scoped installs (`python`, `apt`, `brew`, `gems`, `go`, `manual`), `--dry-run`, `--verify`, and `--force` are all supported. Logs land in `~/.ctf-tools/`. See [scripts/install_ctf_tools.sh](scripts/install_ctf_tools.sh) for the full package lists.

## Philosophy

- **Model-invoked, not menu-driven.** The agent should recognize the challenge and reach for the right technique itself — you shouldn't have to.
- **Real writeups, not theory.** Techniques come from solved CTFTime challenges, with the specific bypass or oracle behavior that made them work.
- **Progressive disclosure.** A skill loads its index first and pulls detailed technique files only when the challenge calls for them.

## Credits

Category skills and technique library by [Lukasz Jagiello](https://github.com/ljagiello) — [ljagiello/ctf-skills](https://github.com/ljagiello/ctf-skills), MIT. This repo repackages that work as a Claude Code plugin and adds the `ctf-solver` subagent.

## Updating

If you installed into your skills directory, pull the latest and reload:

```bash
cd ~/.claude/skills/ctf-skills && git pull
```

Then run `/reload-plugins` in Claude Code to pick up the changes without restarting.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## License

MIT
