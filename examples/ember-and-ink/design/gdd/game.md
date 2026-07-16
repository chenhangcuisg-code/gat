# Game Overview — Ember and Ink (烬与墨)

> Example output of `/gat-brainstorm`. Concise, implementation-facing.

## One-liner
A quiet papercut-wuxia **idle-RPG**: a wandering swordsman cultivates between towns; time passes
whether you watch or not, and returning reveals what your discipline earned.

## Pillars
1. **Restraint as aesthetic** — minimal ink-and-paper visuals; one vermilion accent carries all
   emphasis. Calm, not busy.
2. **Idle with intent** — progress accrues offline, but *choices* (which technique to drill,
   which road to walk) shape it. Not a number-go-up treadmill.
3. **Legible mastery** — every skill reads at a glance; power comes from understanding, not UI
   archaeology.

## Core loop
`choose a discipline → travel/train (idle) → return → allocate gains → face a road trial → repeat`

## Systems (see systems-index.md)
- **Cultivation** — offline progression along a chosen technique tree.
- **Skills** — a small set of legible martial techniques (data-driven).
- **Road trials** — periodic scripted encounters gating progression.
- **Economy** — spirit-stones + materials; tight sources/sinks, no premium currency.

## Scope guardrails
- Single-player, offline-first. No multiplayer, no live-service.
- Content is data-driven (`data/*.json`) so techniques/trials expand without engine changes.

## Art & style
Direction in `design/art/art-direction.md`; **frozen** in `design/art/style-contract.yaml`
("flat papercut, Song-dynasty ink, single vermilion accent"). All assets obey it.
