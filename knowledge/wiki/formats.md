# Formats — data / asset / engine format notes

Field layouts, conventions, gotchas. Append, dated.

---

## VFX package layout (from game-skill-vfx)
```
godot_package/vfx/<set>/<effect>/
  <effect>_00.png .. _NN.png      # RGBA frames, luminance/ink keyed
  <effect>.tres                    # Godot SpriteFrames resource
```
Godot use: `AnimatedSprite2D` ← `.tres` into SpriteFrames; material Blend = **Add** (energy /
glowing ink) or **normal** (dark minimalist ink). Frames are true RGBA (checker shows through).

## Style Contract (`design/art/style-contract.yaml`)
Machine-enforceable art spec. Keys: `locked`, `palette` (+`tolerance_deltaE`), `rendering`
(resolution/view/outline/shading/background), `prompt_contract`
(positive_prefix/suffix/negative/style_anchor_phrases/reference_images), `model`
(backend/params/seed_strategy/base_seed), `categories` (per-type overrides, inherit-then-patch),
`enforcement` (checks/on_fail), `revisions` (append-only). Full schema:
`knowledge/style/style-contract.schema.md`.

## Game content data (`data/<system>.json`)
Data-driven instances per GDD system. Each entity carries an `art:`/`vfx:` key pointing at its
asset so `/gat-verify` can audit coverage and `/gat-asset`/`/gat-vfx` can register outputs.
Keep data and code isolated (`architecture/data-files.md`, `asset-conventions.md`).

## Hastur op protocol (godot-editor-control)
HTTP broker :5302 → TCP :5301 → GDScript op templates in `gdscript/ops/*.gd` (manifest.json
lists them). Client `scripts/gop.py` is pure stdlib. See `references/protocol.md`.

<!-- Append new formats above this line. -->
