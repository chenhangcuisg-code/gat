---
name: gat-asset
description: "Generate 2D game art assets (icons, characters, items, tilesets, UI) that are FORCED through the locked Style Contract so the whole game stays visually consistent. Composes prompts via tools/style_prompt.py, generates with the contract's backend (gpt-image / flux / sdxl), then gates every output through tools/art_audit.py — off-style art is regenerated, never shipped. Use when the user wants icons/sprites/portraits/tilesets for a GAT game. Triggers: 生成素材, make icons, generate sprites, 出图, character art, tileset, game art."
argument-hint: "<what to make, e.g. '8 skill icons for the fire school'> [--category icon|character|tileset|ui]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell, Agent
---

# gat-asset — style-locked asset generation

Request: $ARGUMENTS

You generate game art. You do **not** decide the style — the **Style Contract** does. Your
only creative input is the *subject* of each asset; the look comes from
`design/art/style-contract.yaml`. This is what keeps a game from looking like an asset-flip.

## Law (read `knowledge/style/style-contract.schema.md`)

1. **Load-or-refuse.** If `design/art/style-contract.yaml` is missing or `locked` is not
   `true`, STOP and tell the user to run `/gat-style-lock`. Never generate off-contract.
2. **Compose, never freehand.** For every asset, get the prompt from the contract:
   ```bash
   python tools/style_prompt.py --contract design/art/style-contract.yaml \
       --subject "<subject only, no style words>" --category <cat>
   ```
   Use the returned `positive`, `negative`, `params`, `seed`, `size`, `reference_images`
   **verbatim**. Do not add style adjectives — they belong in the contract.
3. **Audit-or-discard.** After generating, gate each file:
   ```bash
   python tools/art_audit.py <file> --contract design/art/style-contract.yaml --category <cat>
   ```
   On FAIL, follow `enforcement.on_fail` (default: regenerate). Log what failed. Do not ship
   "close enough".

## Procedure

1. **Read** the contract and the relevant system art doc (`design/art/<system>-art.md`) and
   content data (`design/content/<system>-data.md`) so you generate exactly the asset list the
   design calls for — no more, no less.
2. **Build the subject list.** One subject line per asset. Subjects describe *content*
   ("a coiled iron serpent", "a healing gourd") — never style.
3. For each subject: compose the prompt (step above) → generate with the contract's backend.
   - `gpt-image-2` / `gpt-image` → use the `gpt-image` skill or the OpenAI Images API.
   - `flux` / `sdxl` → use the `pipelines/vfx` env (see `docs/deployment/vfx-gpu-server.md`).
   - **Always** pass `reference_images` as the img2img / edit / IP-adapter anchor when the
     backend supports it — this is the strongest consistency lever.
4. **Audit** each output. Regenerate failures (nudge subject wording only, never style). If an
   asset fails audit 3× for the same reason, surface it — the contract may need a `--relock`,
   which is the user's call, not yours.
5. **Place** passing assets by convention (`assets/<category>/<id>.png`) and register them in
   the game's data files if the project uses an art-registry (see
   `knowledge/architecture/asset-conventions.md`).
6. **Report** a contact sheet / list of what passed, and anything quarantined.

## Batch consistency tips

- Generate a whole family in one session with the same `base_seed` family so lighting/line
  weight stay coherent.
- For a set (e.g. 8 skill icons), generate one, get sign-off, make it the family reference,
  then generate the rest anchored to it.
- Prefer one reusable subject template over hand-writing every prompt.

## Self-evolving

When you finish, apply the `/gat-evolve` protocol: if a subject-phrasing trick, a backend
setting, or a regeneration cause recurred, append it to `knowledge/wiki/patterns.md` (art) so
the next batch starts smarter. Record audit-failure causes in `knowledge/wiki/pitfalls.md`.
