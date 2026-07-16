# Self-evolving — the toolkit that compounds

GAT is built to get better every time it makes a game. The mechanism is deliberately simple and
borrowed from the `game-unpack` skill's self-accumulating wiki, generalized to the whole
game-dev workflow: **every skill reads the knowledge base before real work, and writes lessons
back after.**

## Two memories

| | Where | Holds | Lifetime |
|---|---|---|---|
| **Toolkit KB** | `knowledge/wiki/{pitfalls,methods,patterns,formats,cases}.md` | cross-project, game-agnostic lessons | forever |
| **Project journal** | `.gat/journal.md`, `.gat/decisions.md` (in the game repo) | this game's paradigm, bands, conventions | one game |

## The loop

```
   read ─►  do the work  ─►  write-back  ─►  (next session reads a smarter KB)
    ▲                                                     │
    └─────────────────────────────────────────────────────┘
```

- **Read-side:** each skill opens the relevant `knowledge/wiki/*` and `.gat/journal.md` before
  starting (e.g. `gat-implement` reads Godot/Hastur pitfalls; `gat-asset` reads art patterns).
- **Write-side:** `/gat-evolve` harvests what was learned — a negative-prompt term that killed a
  recurring artifact, a balance band, a Godot gotcha — and appends it, dated and searchable, to
  the right file. Project-specific lessons go to the journal; generalizable ones to the wiki.

## Three levels of evolution

1. **Per-project** — the game's `.gat/journal.md` accumulates its own conventions; later
   milestones on the same game start informed.
2. **Cross-project** — `knowledge/wiki/*` accumulates lessons that transfer to the *next* game.
   Game #10 starts far ahead of game #1.
3. **Self-modification (guarded)** — when a lesson should change GAT's own behavior,
   `/gat-evolve --propose-skill-changes` drafts a concrete diff to a SKILL.md / template /
   knowledge doc and **surfaces it for review**. GAT never silently rewrites its executable
   behavior — knowledge edits are free, behavior edits go through a PR. This keeps a
   self-improving agent auditable.

## Learning from reference games

`/gat-learn-from-ref` extends the read-side outward: study a game you may legally inspect (an
open-source game, a game you own, your own past project) and distil *design/economy/art
conventions* into the wiki — never copied content. It sharpens your original game's baseline.
Strict boundaries (study-only, respect licences, no redistribution, commercial-use-needs-
approval, no DRM circumvention) live in that skill and in `LICENSING.md`.

## Why this beats a static prompt library

A static toolkit is as good on day 100 as day 1. A self-evolving one encodes every hard-won
lesson so it is never re-learned. The cost is discipline: write-backs must be concrete, dated,
deduplicated, and honest — write for the next reader, who is a different session on a different
game.
