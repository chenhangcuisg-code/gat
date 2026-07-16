# Licensing, commercial use & attributions

## Copyright

Copyright © 2026 chenhangcui (`chenhangcuisg-code`). All rights reserved except as granted below.

## The short version

- **Personal, learning, research, evaluation, and other non-commercial use** — free, under
  [PolyForm Noncommercial License 1.0.0](LICENSE).
- **Commercial use** (shipping a game made with GAT for money, using GAT inside a for-profit
  studio's pipeline, offering GAT as a paid service, etc.) — **requires prior written approval
  and a separate agreement.** This is negotiable — reach out.

> `Required Notice: Copyright © 2026 chenhangcui — https://github.com/chenhangcuisg-code/gat`

### What counts as "noncommercial"

Per PolyForm Noncommercial 1.0.0: use for a **noncommercial purpose** — personal use, or use by
a noncommercial organization, or evaluation/research. Using GAT to build or ship a product for
commercial advantage or monetary compensation is **not** covered by the free grant.

### Getting a commercial license

Open an issue titled `commercial licensing` or contact the author via the GitHub profile
[`chenhangcuisg-code`](https://github.com/chenhangcuisg-code). Terms are flexible for
indie/small studios — the intent is to keep GAT open for creators while asking commercial users
to check in.

## The reference-study / reverse-engineering module

`gat-learn-from-ref` and `pipelines/unpack/` exist **for learning only**:

- Study only games you have the **legal right to inspect** (open-source games, games you own for
  personal study, your own past projects). Respect each game's license and terms of service.
- **Never** redistribute extracted third-party assets, code, story, or data. They are for local
  study and must be deleted or git-ignored.
- This public module ships **no DRM-circumvention, key-extraction, or packer-bypass tooling**.
  Those capabilities are intentionally kept out of this repository.
- **Commercial use of this module in particular requires prior approval** (as above).

If a use would cross these lines, it is not permitted under this project.

## Attributions

GAT integrates and builds on prior work; thanks to all of it:

| Component | Source | Notes |
|---|---|---|
| Design pipeline (`gat-*` design skills, role agents, templates) | simplified from **Claude-Code-Game-Studios** (Donchitos) | stripped to a document-driven pre-production flow, then extended to full-cycle |
| `game-architect` knowledge base (`knowledge/architecture/*`) | author's game-architecture references | paradigm + per-system design docs |
| VFX pipeline (`pipelines/vfx/*`) | **[game-skill-vfx](https://github.com/chenhangcuisg-code/game-skill-vfx)** | FLUX.1-schnell · AnimateDiff · SDXL · DreamShaper-8, all open weights |
| Live editor control (`skills/godot-editor-control/*`) | **Hastur Operation Plugin** for Godot | HTTP/TCP broker + GDScript ops; client is original |
| `gpt-image` skill lineage | adapted from **[gpt_image_2_skill](https://github.com/wuyoscar/gpt_image_2_skill)** | image generation |
| Reference-study lessons (`gat-learn-from-ref`) | author's `game-unpack` skill | learning-only distillation; no tooling vendored |

### Model weights (used by the VFX pipeline, downloaded at runtime)

`black-forest-labs/FLUX.1-schnell`, `guoyww/animatediff-motion-adapter-v1-5-2`,
`Lykon/dreamshaper-8`, `stabilityai/stable-diffusion-xl-base-1.0`,
`madebyollin/sdxl-vae-fp16-fix`. Each is governed by **its own license** — review and comply
with them independently before any commercial use of generated VFX.

Third-party components remain under their own licenses; the PolyForm terms here apply to GAT's
original code, skills, agents, docs, and knowledge base.
