# GAT knowledge wiki — the self-evolving memory

This is the toolkit's long-term, cross-project memory. Every GAT skill **reads** the relevant
file here *before* real work and **writes** lessons back *after* (via `/gat-evolve`). Over many
games it compounds: the tenth game starts far ahead of the first.

> **Recently updated:** 2026-07-16 — seeded from game-skill-vfx, game-unpack, skill-design, and
> the game-architect knowledge base.

## Files

| File | Holds |
|---|---|
| [`pitfalls.md`](./pitfalls.md) | symptom → root cause → fix → how to catch it earlier |
| [`methods.md`](./methods.md) | reusable, copy-pasteable recipes + when they apply |
| [`patterns.md`](./patterns.md) | design / art-prompt / architecture patterns that worked |
| [`formats.md`](./formats.md) | data / asset / engine format notes |
| [`cases.md`](./cases.md) | one paragraph per finished game or milestone |

## Rules for writing here (from `/gat-evolve`)

- Append, date, give enough context that a *different* session on a *different* game can reuse it.
- Terse and searchable beats prose. Sharpen duplicates instead of adding near-copies. Delete
  entries proven wrong.
- Save the non-obvious; skip what's already clear from code/git history.
- Project-specific lessons go to that game's `.gat/journal.md`, not here.

## Scope split

- **Here (`knowledge/wiki/`)** = every game, forever.
- **`.gat/journal.md`** (in each game repo) = this game only.
