---
name: gat-vfx
description: "Generate 2D skill/spell VFX animations (sword-beam 剑波, fireball, frost nova, ink-wash energy, …) as luminance-keyed transparent sprite sheets + Godot .tres, using the game-skill-vfx pipelines (FLUX texture + procedural / AnimateDiff / SDXL-controlled), all bound to the game's Style Contract. Produces drop-in AnimatedSprite2D effects. Triggers: 技能特效, skill vfx, sword beam, 剑波, spell effect, particle effect, animated sprite sheet, godot vfx."
argument-hint: "<effect, e.g. 'a crescent sword-beam, blue energy'> [--pipeline p2|p1|p3] [--archetype projectile|burst|bolt|aura|spin]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell
---

# gat-vfx — style-locked skill VFX generation

Request: $ARGUMENTS

Turns a text description of a skill effect into a **transparent animated sprite sheet + a
Godot `.tres`** you can drop onto an `AnimatedSprite2D`. Wraps the `pipelines/vfx` code
(vendored from `game-skill-vfx`) and binds it to the game's **Style Contract** so effects
match the game's art (energy vs. 国风水墨 vs. pixel).

Read `pipelines/vfx/README.md` and `pipelines/vfx/REPORT.md` for the full method; read
`knowledge/style/style-contract.schema.md` for the style law.

## The core trick (why VFX are different from static art)

VFX are rendered on **pure black**, then `alpha = brightness` turns black → transparent; drop
onto any scene with **additive** blending for a glow. Ink-wash **inverts** this
(`alpha = darkness`, normal blend). The Style Contract's `vfx` category encodes which:
`background: "pure black (luminance-key)"` for energy, or a paper background for ink.

## Pick a pipeline (from the report)

| Pipeline | Motion | Control | Best for |
|---|---|---|---|
| **P2** (FLUX texture + procedural) 🏆 default | code (deterministic, perfect-loop) | exact shape | production; controllable projectiles/bursts |
| **P1** (AnimateDiff txt2vid) | 100% AI | no silhouette control | organic chaos (fire, ink flow) |
| **P3** (SDXL controlled img2img) | procedural init | AI re-paint | engine-controllable + AI texture |

Default to **P2** unless the user wants organic/chaotic motion (then P1).

## Procedure

1. **Require a locked contract.** Read `design/art/style-contract.yaml`. If missing/unlocked →
   run `/gat-style-lock`. Read its `categories.vfx` (backend, background, palette).
2. **Compose the texture prompt** through the contract (VFX still obeys palette + anchors):
   ```bash
   python tools/style_prompt.py --contract design/art/style-contract.yaml \
       --subject "<effect subject, e.g. crescent sword-beam, blue energy>" --category vfx
   ```
3. **Choose the motion archetype** (projectile / burst / bolt / aura / spin) — this is the
   procedural motion, independent of texture. See `pipelines/vfx/scripts/vfx_batch.py`.
4. **Generate** on the GPU env (see `docs/deployment/vfx-gpu-server.md`):
   - P2: `python pipelines/vfx/scripts/vfx_batch.py` (edit the effect entry / archetype), or
     the ink variants `vfx_inkglow.py` / `vfx_ink.py` for 国风水墨.
   - Post-processing (`vfx_util.py`) does luminance/ink key → RGBA frames → sprite sheet →
     GIF preview → Godot `.tres`.
5. **Audit** the key frames against the contract (palette + background):
   ```bash
   python tools/art_audit.py <effect>_08.png --contract design/art/style-contract.yaml --category vfx
   ```
6. **Package for Godot:** copy `godot_package/vfx/<set>/<effect>/` into the game's
   `res://vfx/`. Effect `.tres` → `SpriteFrames`; set material Blend = **Add** (energy/glowing
   ink) or **normal** (dark minimalist ink).
7. **Wire it in** (optional): with `/gat-implement`, attach the effect to the skill that fires
   it in the running Godot editor.
8. **Report** the effect id, preview GIF, frame count, and Godot blend mode.

## Notes

- The pipeline runs from cached open models on a single A100-80GB — **no paid APIs**. If you
  have no GPU, `docs/deployment/vfx-gpu-server.md` covers remote execution on a rented box.
- Keep effect names and archetypes in the game's data (`data/skills.json` `vfx:` field) so
  `/gat-implement` and `/gat-verify` can find them.

## Self-evolving

Record new effect recipes (subject + archetype + pipeline + blend mode that looked good) in
`knowledge/wiki/patterns.md`, and any pipeline pitfalls (model download, VRAM, key mode) in
`knowledge/wiki/pitfalls.md`.
