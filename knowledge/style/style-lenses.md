# Style lenses — how the artist reasons

Cite these by name in art docs, prompts, and audits so reasoning is traceable. The full set
(composition, color/light, form/silhouette, character, environment, animation, sprite/2D,
3D/skeletal, VFX, and the complete UI/UX cognition set) lives in the
[`gat-artist`](../../agents/gat-artist.md) agent. This file highlights the lenses most relevant
to **style-lock and AI generation** — the ones that keep a whole game visually one.

## AI prompt craft (the style-lock lenses)

- **Specificity over vagueness** — concrete nouns/materials beat mood words. Put them in the
  contract's `positive_suffix`, not in each call.
- **Style reference anchoring** — condition on a real exemplar (img2img / IP-adapter / edit),
  not description alone. The single strongest anti-drift lever → `reference_images`.
- **Negative prompting** — name what breaks the style (photoreal, gradient, neon, watermark) in
  the contract's `negative`. A good negative is as important as the positive.
- **Seed & parameter discipline** — fix sampler/steps/cfg and a `base_seed`; use
  `fixed-per-family` so a set stays coherent while subjects vary.
- **Iteration over one-shot** — expect 2–3 regenerations gated by `art_audit.py`; nudge the
  *subject*, never the style.
- **Batch variation control** — generate a family in one session anchored to its master.

## Style consistency

- **Style-guide adherence** — the Style Contract *is* the guide; audit against it.
- **Asset-family resemblance** — new assets should read as siblings of the master; the audit's
  `family_resemblance` check is the automated proxy.
- **Cross-asset palette harmony** — one palette, enforced by `tolerance_deltaE`.
- **Mood-board alignment** — the contract's `identity.mood` keeps intent explicit.

## Silhouette & readability (so style never costs clarity)

- **Readable silhouettes** — a skill icon must read at 32px; a VFX must read against a busy scene.
- **Value structure** — hold contrast even within a restrained palette.
- **Color vs. gameplay clarity (VFX)** — an effect's color must communicate its gameplay
  (friendly/hostile, element) before it looks pretty.

## The one rule these serve

Style words live in the **contract**, applied uniformly to every asset. A skill supplies only
the **subject**. That separation — plus reference anchoring and an audit gate — is what turns
"nice individual images" into "a game that looks like one artist made it."
