# GAT workflow — from idea to verified build

Run these in order. At any point, `/gat-workflow-start` inspects the repo and tells you the next
step. Every skill works the same under Claude Code (`/gat-x`) and Codex (`gat-x` prompt).

## 0. Install into your game repo
```bash
bash install.sh --runtime both --target /path/to/my-game   # or install.ps1 on Windows
cd /path/to/my-game
```

## 1. Design (pre-production)
```
/gat-brainstorm  <hint>     → design/gdd/game.md, systems-index.md, design/art/art-direction.md
/gat-story       [hint]     → design/narrative/* (skip for abstract/non-narrative games)
/gat-design      [system]   → per-system GDDs + design/content/*-data.md + design/art/*-art.md
/gat-milestone              → production/milestone.md (ordered handoff slices)
```
One-question-at-a-time interviews; the docs are concise and implementation-facing.

## 2. Style-lock (freeze the look) ⭐
```
/gat-style-lock             → design/art/style-contract.yaml  (locked)
```
Do this **before** generating any asset. From now on every asset skill is bound to it. Change it
only on purpose with `/gat-style-lock --relock`. See `docs/style-lock.md`.

## 3. Assets (style-locked)
```
/gat-asset  "8 fire-school skill icons"  --category icon      → assets/icons/*  (audited)
/gat-vfx    "a crescent sword-beam, blue energy"              → res://vfx/*  + .tres  (audited)
```
Subjects only — the style comes from the contract. Off-style output is regenerated, never
shipped. VFX needs a GPU env (see `docs/deployment/vfx-gpu-server.md`).

## 4. Implement (Godot) ⭐
```
/gat-scaffold               → Godot project skeleton, data/*.json, autoloads, save-slot discipline
/gat-implement  "M1: ..."   → build ONE milestone: GDScript + scenes (live via Hastur) + wiring
```
Needs Godot + the Hastur broker for live editor control (`docs/deployment/godot-hastur.md`);
without it, scenes are written as files and a live pass is flagged pending.

## 5. Verify (the honesty gate)
```
/gat-verify  "M1: ..."      → smoke + balance sim + asset/style audit + coverage → evidence report
```
"Done" means it ran, the numbers hold, assets exist and match the style, and the design is
covered — with evidence.

## 6. Evolve (close the loop) ⭐
```
/gat-evolve                 → harvest lessons → knowledge/wiki/* + .gat/journal.md
/gat-learn-from-ref <game>  → distil design lessons from a game you may study (learning-only)
```
Run `/gat-evolve` at the end of substantial work. The next game starts smarter.

## Loop
Iterate 3→4→5 per milestone. Re-run `/gat-design` to add a system, `/gat-style-lock --relock`
to change the look on purpose. `/gat-workflow-start` keeps you oriented.

```
brainstorm → story → design → milestone
                 └─► style-lock ─► [ asset/vfx → scaffold → implement → verify ] × milestones
                                     └────────────── evolve ──────────────┘
```
