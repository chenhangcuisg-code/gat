# Style Contract — schema & law

The **Style Contract** is GAT's answer to a hard problem in AI-assisted game art:
> *"I generated one hero in a papercut-ink style. Now every icon, every VFX, every
> tileset the agent produces for the next six months must look like it came from the
> same artist — or the game looks like an asset-flip."*

A Style Contract is a **frozen, machine-readable specification** that **every** asset-
generating skill (`gat-asset`, `gat-vfx`, `gat-icon`, …) MUST load and obey. It turns a
loose art-direction document into an enforceable constraint on prompts, parameters, and
outputs.

It lives at **`design/art/style-contract.yaml`** in the game project and is produced by
**`/gat-style-lock`** from `design/art/art-direction.md`.

## The three laws

1. **Load-or-refuse.** No asset skill may generate anything unless a `style-contract.yaml`
   exists and `locked: true`. If it is missing, run `/gat-style-lock` first.
2. **Compose, never freehand.** The final prompt sent to any image/VFX backend is
   *always* `positive_prefix + <subject> + positive_suffix`, with the contract's `negative`
   and `params`/`seed_strategy` applied verbatim. Skills describe only the **subject**;
   the style comes from the contract. A skill that writes its own full prompt is a bug.
3. **Audit-or-discard.** Every generated asset passes `tools/art_audit.py` against the
   contract before it is saved into the project. Off-style output is regenerated, never
   shipped. Silent truncation of the audit ("close enough") is forbidden — log what failed.

Changing a locked contract requires a **re-lock**: `/gat-style-lock --relock`, which bumps
`version`, records a rationale in `revisions:`, and (optionally) triggers a re-audit sweep
of existing assets. This is deliberately heavyweight — style drift should be a decision,
not an accident.

## Schema

```yaml
version: 1                        # bump on every re-lock
locked: true                      # asset skills refuse to run unless true
project: "Ember and Ink"
established_from: "design/art/art-direction.md"   # provenance
established_at: "2026-07-16"      # date string (agents cannot call Date.now)

# ---- what the world looks like (human-readable anchors) ----
identity:
  one_liner: "Papercut wuxia — flat ink silhouettes on warm rice-paper, single vermilion accent."
  mood: ["quiet", "elegant", "restrained"]
  era_culture: "Song-dynasty ink painting, minimalist"

palette:
  primary:   ["#1A1712", "#F2E9D8"]        # ink black, rice paper
  accent:    ["#C1332B"]                    # the ONE allowed pop color (vermilion)
  secondary: ["#6B7C6E", "#8A6D3B"]         # muted sage, aged bronze
  forbidden: ["neon", "pure #0000FF", "gradients >3 stops", "photoreal skin"]
  tolerance_deltaE: 18                       # audit: mean color must sit within this of palette

rendering:
  resolution: "512x512"                      # audit enforces exactly
  view: "3/4 top-down"                       # 3/4 | side | iso | portrait
  outline: "none"                            # none | "1px #1A1712" | "2px dark"
  shading: "flat 2-tone, hard cut shadow"
  linework: "torn-paper edges, no anti-alias fuzz"
  background: "transparent"                   # transparent | "pure black (luminance-key)" | "rice-paper #F2E9D8"

# ---- the prompt law (the part that gets glued around every subject) ----
prompt_contract:
  positive_prefix: >
    flat papercut illustration, Song-dynasty ink-painting aesthetic,
  positive_suffix: >
    , torn rice-paper texture, single vermilion accent, hard 2-tone flat shading,
    no gradient, no photorealism, centered, clean silhouette, game asset
  style_anchor_phrases:                       # non-negotiable; must all survive prompt edits
    - "flat papercut illustration"
    - "Song-dynasty ink"
    - "single vermilion accent"
  negative: >
    3d render, photorealistic, glossy, neon, lens flare, drop shadow, watermark,
    text, signature, extra colors, gradient background, blurry, jpeg artifacts
  reference_images:                           # img2img / IP-adapter / style-anchor
    - "design/art/refs/hero_master.png"

# ---- how it is generated (reproducibility) ----
model:
  backend: "gpt-image-2"                      # gpt-image-2 | flux | sdxl | animatediff
  size: "1024x1024"                           # backend-native; downscaled to rendering.resolution
  params: { quality: "high", n: 1 }
  seed_strategy: "fixed-per-family"           # fixed | fixed-per-family | free
  base_seed: 73019                            # family reproducibility anchor

# ---- per-category tweaks that still inherit everything above ----
categories:
  icon:      { rendering: { resolution: "256x256", view: "flat front" } }
  character: { rendering: { view: "side", resolution: "512x768" } }
  vfx:       { rendering: { background: "pure black (luminance-key)" }, model: { backend: "flux" } }
  tileset:   { rendering: { resolution: "128x128" }, prompt_contract: { positive_suffix: ", seamless tileable" } }

# ---- enforcement ----
enforcement:
  audit_script: "tools/art_audit.py"
  checks: [resolution_exact, palette_within_tolerance, background_correct, family_resemblance]
  family_resemblance_ref: "design/art/refs/hero_master.png"
  on_fail: "regenerate"                        # regenerate | quarantine | halt

# ---- history (append-only) ----
revisions:
  - version: 1
    at: "2026-07-16"
    by: "gat-style-lock"
    rationale: "Initial lock from art-direction.md after brainstorm."
```

## Why fixed seeds + reference anchors matter

Prompt text alone drifts: the same words produce different palettes across runs and
across models. The contract pins style three ways, strongest last:

1. **Text law** — prefix/suffix/negative make the *words* consistent.
2. **Parameter law** — fixed sampler/steps/cfg and a `base_seed` make *randomness*
   consistent (a per-family seed keeps a whole icon set coherent while letting subjects vary).
3. **Reference law** — `reference_images` feed img2img / IP-adapter / gpt-image edit so new
   assets are conditioned on an *actual pixel exemplar*, not just a description. This is the
   single most effective anti-drift lever; always seed a family from its master image.

See `tools/style_prompt.py` (composes the final prompt) and `tools/art_audit.py` (the gate).
