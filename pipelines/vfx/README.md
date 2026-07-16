# pipelines/vfx — AI skill-effect VFX (vendored from game-skill-vfx)

Self-hosted, open-model pipelines that generate **2D game skill-effect animations** end-to-end:
text prompt → **transparent sprite sheet + Godot `.tres`**, ready to drop onto an
`AnimatedSprite2D`. Wrapped by the [`gat-vfx`](../../skills/gat-vfx/SKILL.md) skill and bound to
the game's [Style Contract](../../docs/style-lock.md). Everything runs on cached **open models**
(FLUX.1-schnell · AnimateDiff · SDXL · DreamShaper-8) — **no paid APIs**; reference box is a
single A100-80GB.

Full method, every parameter, data sources, and pitfalls: **[REPORT.md](REPORT.md)**.
GPU setup & remote execution: **[../../docs/deployment/vfx-gpu-server.md](../../docs/deployment/vfx-gpu-server.md)**.

## The core trick: luminance keying

VFX are rendered on **pure black**, then `alpha = brightness` turns black → transparent; drop
onto any scene with **additive** blending for a glow. Ink-wash **inverts** it
(`alpha = darkness`, fixed ink color, **normal** blend). The Style Contract's `vfx` category
records which so the audit and packing pick the right key.

## Three pipelines

| | Pipeline | Motion | Control | Best for |
|---|---|---|---|---|
| **P2** 🏆 | FLUX texture + procedural | code (deterministic, perfect-loop) | exact shape | production default |
| **P1** | AnimateDiff txt2vid | 100% AI | none | organic chaos (fire, ink flow) |
| **P3** | SDXL controlled img2img | procedural init | AI re-paint | engine-controllable + AI texture |

Controllability P2 ≈ P3 > P1; organic wow-factor P1 wins. Default to **P2**.

## Effect library

`scripts/vfx_batch.py` scales P2 to any effect via motion archetypes
(**projectile / burst / bolt / aura / spin**): 🔥 fireball · ⚡ lightning · ❄️ frost nova ·
💚 heal aura · 💥 explosion · 🔮 arcane circle — plus AnimateDiff explosion & flame-swirl.
Ink styles: `vfx_inkglow.py` (国风水墨 glowing ink — 剑波/墨爆/光环/墨龙/墨漩) and `vfx_ink.py`
(minimalist sumi-e, inverse key).

## Scripts

```
scripts/
  vfx_util.py               luminance_key / ink_key / sheet / gif / Godot .tres  (shared)
  p1b_animatediff.py p2_flux_procedural.py p3_sdxl_ctrl.py   the 3 core pipelines
  vfx_batch.py vfx_adiff_batch.py         effect library (+ run_batch.sh)
  vfx_ink*.py  vfx_inkglow*.py            ink-wash styles (+ run_ink.sh / run_inkglow.sh)
  *_compare.py transparency_demo.py       contact sheets / proof
```

## Samples (checked in)

`samples/` holds two Godot-ready effects so you can see the output without a GPU:
`ink_jianbo/` (剑波, glowing ink) and `fireball/` (energy), each with RGBA frames + `.tres`, plus
preview GIFs in `samples/previews/`.

## Use in Godot

Copy an effect folder into `res://vfx/`, add an `AnimatedSprite2D`, load the `.tres` into
SpriteFrames. Material Blend = **Add** (energy / glowing ink) or **normal** (dark minimalist
ink). `/gat-implement` can wire it to the skill that fires it in a live editor.

## Reproduce

See [../../docs/deployment/vfx-gpu-server.md](../../docs/deployment/vfx-gpu-server.md). In short:
a diffusers env (`torch diffusers transformers accelerate pillow numpy imageio`), optional
`HF_ENDPOINT=https://hf-mirror.com`, then `python scripts/vfx_inkglow.py`. Model weights are
governed by their own licenses — review them before commercial use (see
[`../../LICENSING.md`](../../LICENSING.md)).
