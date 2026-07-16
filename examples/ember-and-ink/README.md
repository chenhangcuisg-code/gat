# Example — "Ember and Ink" (烬与墨)

A worked GAT example: a **papercut-wuxia idle-RPG**, taken from a one-line idea through the
**design → style-lock** hand-off. It shows what the GAT skills produce and, crucially, a **real,
runnable Style Contract**.

## What's here

```
design/
  gdd/game.md                  ← from /gat-brainstorm (game overview)
  art/art-direction.md         ← from /gat-brainstorm (art bible)
  art/style-contract.yaml      ← from /gat-style-lock  ⭐ the frozen, enforceable style
  art/refs/README.md           ← where the master image goes
production/milestone.md        ← from /gat-milestone (ordered slices)
```

## The point: the Style Contract is executable

The contract isn't a doc — it's enforced. From the repo root:

```bash
C=examples/ember-and-ink/design/art/style-contract.yaml

# Compose the ONE legal prompt for a new asset (you give only the subject):
python tools/style_prompt.py --contract $C --subject "a healing gourd" --category icon

# Gate any generated file against the style (exits non-zero + reasons on drift):
python tools/art_audit.py my_icon.png --contract $C --category icon
```

Try auditing one of the bundled VFX frames as an *icon* — it fails on palette and resolution,
exactly as an off-style asset should:

```bash
python tools/art_audit.py pipelines/vfx/samples/fireball/fireball_08.png --contract $C --category icon
# FAIL: resolution 768x512 != 256x256; palette mean ΔE off; -> regenerate
```

## Continue it yourself

Downstream implementation is left as an exercise — the pipeline continues:

```
/gat-scaffold           → Godot skeleton + data/*.json from the GDD
/gat-implement "M1: …"  → build the first milestone live in Godot
/gat-verify   "M1: …"   → smoke + balance sim + style audit + coverage
/gat-evolve             → write the lessons back
```

See [`../../docs/workflow.md`](../../docs/workflow.md).
