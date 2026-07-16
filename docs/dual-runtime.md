# Dual runtime — Claude Code and Codex

GAT is portable: agents, skills, knowledge, and templates are plain Markdown + Python with no
runtime-specific magic. One installer wires a **game repo** to run GAT under Claude Code, Codex,
or both. The GAT toolkit itself is cloned once (e.g. `~/gat`) and shared by all your games.

## What "install" does

`install.sh` / `install.ps1` takes `--runtime {claude|codex|both}` and `--target <game-repo>`
and wires that repo:

### Claude Code
- Links `~/gat/skills/*` → `<game>/.claude/skills/*` (skills are portable folders).
- Links `~/gat/agents/*` → `<game>/.claude/agents/*`.
- Writes/updates `<game>/CLAUDE.md` to `@`-include the GAT working rules + knowledge index.
- Skills are then invoked as slash commands: `/gat-brainstorm`, `/gat-style-lock`, …

### Codex
- Writes `<game>/AGENTS.md` from `runtimes/codex/AGENTS.md.template` — the working rules, the
  role/skill map, and the knowledge index Codex reads on every session.
- Generates `~/.codex/prompts/gat-*.md` — one custom prompt per skill. Each is a thin shim:
  *"Read `<gat>/skills/<name>/SKILL.md` and execute it with `$ARGUMENTS`."* Invoked as
  `/gat-brainstorm` (Codex custom prompts) or by asking Codex to run the skill.
- Points `CODEX`/config at the shared knowledge base.

### Both
Does both of the above so you can switch runtimes on the same repo without reconfiguring.

## Why a shim, not a fork

The **source of truth is one set of SKILL.md files.** Claude Code loads them natively; Codex
loads them through a generated prompt that says "read this file and follow it." Neither runtime
gets a diverging copy, so a fix to a skill benefits both. The self-evolving loop
(`docs/self-evolving.md`) writes to the same `knowledge/wiki/` regardless of runtime.

## Capability differences to know

| | Claude Code | Codex |
|---|---|---|
| Skill invocation | native slash commands | generated `~/.codex/prompts/gat-*.md` |
| Subagents | `agents/*.md` (Task/Agent) | AGENTS.md role sections; run sequentially |
| MCP (Godot, etc.) | native MCP | native MCP / tool config |
| Knowledge `@`-includes | `CLAUDE.md` | `AGENTS.md` |

The skills are written to degrade gracefully: if a runtime lacks a capability (e.g. parallel
subagents), the skill still runs the same steps sequentially.

## Manual install (no installer)

Point your runtime at the toolkit by hand:
- **Claude:** symlink `skills/` and `agents/` into the repo's `.claude/`, add a `CLAUDE.md`
  `@import` of `runtimes/claude/RULES.md`.
- **Codex:** copy `runtimes/codex/AGENTS.md.template` to `AGENTS.md`, copy
  `runtimes/codex/prompts/*` to `~/.codex/prompts/`.
