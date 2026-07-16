# Art Direction — Ember and Ink

> Example output of `/gat-brainstorm` (artist). This is the human-readable bible that
> `/gat-style-lock` compiled into the enforceable `style-contract.yaml`.

## Visual one-liner
Flat papercut illustration in a Song-dynasty ink-painting aesthetic: torn-edge ink silhouettes
on warm rice-paper, with a **single vermilion accent** carrying all emphasis.

## Mood
Quiet · elegant · restrained. The screen should feel like a scroll, not a slot machine.

## Palette
- **Ink black** `#1A1712` and **rice paper** `#F2E9D8` — the world.
- **Vermilion** `#C1332B` — the *only* pop color; reserved for the player's focus, active
  skills, and danger. Used sparingly, it means "look here."
- **Muted sage** `#6B7C6E` / **aged bronze** `#8A6D3B` — secondary naturals.
- **Forbidden:** neon, pure blues, multi-stop gradients, photoreal skin. These break the world.

## Rendering rules
- Flat 2-tone shading with a hard cut shadow — no soft gradients.
- Torn rice-paper edges; no anti-alias fuzz. Silhouette-first.
- Transparent backgrounds for assets; VFX render on pure black (luminance-key) or paper.
- 3/4 top-down for the world; side profiles for characters.

## Consistency strategy (→ becomes the contract)
- One **master hero image** anchors the whole family; new assets are conditioned on it
  (img2img / IP-adapter), not just described.
- Every prompt is subject-only; the papercut/ink/vermilion language is applied uniformly by the
  Style Contract, never re-typed per asset.
- Skill icons must read at 32px; VFX color must communicate the technique's element before it
  looks pretty.

## Asset families
- **Skill icons** (256px, flat front) — one per technique.
- **Characters** (side, 512×768) — the swordsman + road-trial foes.
- **Skill VFX** (luminance-keyed sprite sheets) — sword-beam 剑波, etc., in glowing-ink style.
- **UI** — paper-panel frames, vermilion active states.

→ Frozen in [`style-contract.yaml`](./style-contract.yaml). Change only via `/gat-style-lock --relock`.
