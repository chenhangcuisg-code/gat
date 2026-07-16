---
name: gat-evolve
description: "The self-evolving loop. Harvest what was learned this session — pitfalls, working methods, reusable patterns, style-prompt fixes, balance recipes — and write it back into the knowledge base (knowledge/wiki/ for cross-project, .gat/journal.md for this game). Optionally proposes concrete improvements to GAT's own skills/templates/knowledge as a diff/PR. Run at the end of any substantial task, or when the user says the agent should 'learn from this'. Triggers: 复盘, evolve, self-improve, 记录经验, learn from this, update the wiki, retro."
argument-hint: "[--scope project|toolkit|both] [--propose-skill-changes]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell
---

# gat-evolve — read-before, write-after: the loop that makes GAT get better

Request: $ARGUMENTS

GAT is designed to compound. Every skill reads the knowledge base *before* work and every
task feeds lessons *back* after — the same self-accumulation that `game-unpack`'s wiki uses,
generalized to the whole game-dev workflow. This skill is the explicit "write-after" step and
the place the toolkit improves itself.

## Two memories, two scopes

| Scope | Location | Holds | Lifetime |
|---|---|---|---|
| **Project** | `.gat/journal.md` (+ `.gat/decisions.md`) in the game repo | this game's paradigm choices, balance bands, asset conventions, open questions | one game |
| **Toolkit** | `knowledge/wiki/*` in the GAT install | cross-project pitfalls, methods, patterns, formats, cases | forever, all games |

`knowledge/wiki/` files (seeded, append-only, dated):
- `pitfalls.md` — symptom + root cause + fix + "how to catch it earlier"
- `methods.md` — reusable, copy-pasteable command/recipe + when it applies
- `patterns.md` — design/art/prompt/architecture patterns that worked
- `formats.md` — data/asset/engine format notes
- `cases.md` — one paragraph per finished game/milestone (what/paradigm/hard part/result)

## Procedure

1. **Gather** this session's deltas: what broke, what fixed it, what you'd do differently, any
   prompt/negative term that killed a recurring art artifact, any balance recipe, any Godot/
   Hastur gotcha, any architecture decision.
2. **Write-back, scoped:**
   - Project-specific → `.gat/journal.md` (append, dated). Decisions → `.gat/decisions.md`.
   - Generalizable → the right `knowledge/wiki/*.md` (append, dated, with enough context that a
     *different* session on a *different* game can reuse it). Be terse and searchable.
   - Update the "Recently updated" line at the top of `knowledge/wiki/README.md`.
3. **Deduplicate:** if an entry already exists, sharpen it rather than adding a near-duplicate.
   Delete entries proven wrong.
4. **Propose toolkit improvements** (`--propose-skill-changes`): if a lesson should change a
   SKILL.md, template, or knowledge doc, draft the concrete edit and show it as a diff. Do
   **not** silently rewrite skills — surface it so the user (or a PR) approves. This is how GAT
   evolves its own behavior, safely.
5. **Report** what you recorded and where, and any proposed skill/template changes.

## What counts as worth saving (and what doesn't)

Save: non-obvious lessons, reusable recipes, style-prompt fixes, balance bands, gotchas.
Don't save: things obvious from the code/git history, one-off trivia, or restating a GDD.
(If asked to "remember" something obvious, capture instead what was *non-obvious* about it.)

## The read-side (every other skill's obligation)

Before starting real work, skills read the relevant `knowledge/wiki/*` and `.gat/journal.md`.
`gat-evolve` is only useful if the write-backs are good — so write for the next reader:
concrete, dated, and honest about what you're unsure of.

## Guardrail on self-modification

`gat-evolve` may freely edit the **knowledge base** (`knowledge/wiki/`, `.gat/*`). It may only
**propose** edits to executable behavior (`skills/*/SKILL.md`, `agents/*`, `tools/*`,
`templates/*`) — those land through review/PR, never as a silent side effect.
