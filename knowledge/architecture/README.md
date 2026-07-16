# knowledge/architecture — game-architect knowledge base

Domain knowledge for game system architecture (paradigms + per-system design), from the
`game-architect` reference set. **Loaded on demand, not all at once.**

## Layout

```
_ARCHITECT-INDEX.md   ← the master index + activation model (read this)
catalog.yaml          ← activation rules: what's core vs. added by system/flag
core/                 ← 10 universal references — ALWAYS active
modules/              ← 23 system-specific & multiplayer references — added ON DEMAND
```

## Why on-demand

A pixel platformer never needs the 9 multiplayer references; a single-player idle game never
needs PCG or netcode. Carrying all 34 references for every game is dead weight that dilutes the
agent's attention. So GAT ships a small universal **core** and pulls in **modules** only when the
game's design actually calls for them.

## How a game gets its set

`/gat-scaffold` reads the game's `systems-index.md` + `gat.config.yaml` flags and runs:

```bash
python tools/arch_init.py --systems skill,combat,narrative --flags shipping \
    --multiplayer none --out .gat/architecture.md
```

That writes **`.gat/architecture.md`** in the game repo — the *active index* every skill reads.
A typical single-player RPG activates ~20 of 34 references; a bare prototype (`--minimal`) just
the 10 core. When `/gat-design` adds a new system later:

```bash
python tools/arch_init.py --add modules/system-mod.md --out .gat/architecture.md
```

## Editing

Add or re-tag references by editing `catalog.yaml` (the source of truth) and, for humans, the
tables in `_ARCHITECT-INDEX.md`. Keep `core/` genuinely universal — if something only some games
need, it belongs in `modules/`.
