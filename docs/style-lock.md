# Style-lock — keep the whole game in one style, forever

> *"I generated one hero in a papercut-ink style. Now every icon, every VFX, every tileset for
> the next six months must look like the same artist made it — or it's an asset-flip."*

This is the requirement style-lock solves. It is GAT's mechanism for **strict prompt
constraint**: once you commit to a look, every future asset is forced through it.

## The problem with plain prompting

Text prompts drift. The same words ("ink wash, minimalist") produce different palettes, line
weights, and framing across runs, across models, and across whoever is writing the prompt that
day. Multiply by hundreds of assets over months and the game loses its visual identity.

## The mechanism: a frozen, enforced contract

`/gat-style-lock` reads your `design/art/art-direction.md` and writes a machine-enforceable
**`design/art/style-contract.yaml`**. Three laws bind every asset skill to it:

1. **Load-or-refuse** — no locked contract, no generation.
2. **Compose, never freehand** — the prompt is *always*
   `positive_prefix + <subject> + positive_suffix`, with the frozen negative + params + seed.
   Skills supply only the **subject**; style lives in the contract.
3. **Audit-or-discard** — every output passes `tools/art_audit.py`; off-style is regenerated.

Style pinned three ways, strongest last:
- **Text law** — prefix/suffix/negative make the *words* consistent.
- **Parameter law** — fixed sampler/steps/cfg + a `base_seed` make *randomness* consistent
  (per-family seed keeps a set coherent while subjects vary).
- **Reference law** — `reference_images` feed img2img / IP-adapter / gpt-image edit, conditioning
  new assets on a real pixel exemplar. This is the strongest anti-drift lever — always anchor a
  family to its master image.

## Try it (runs today)
```bash
C=examples/ember-and-ink/design/art/style-contract.yaml
# compose the ONE legal prompt for a subject:
python tools/style_prompt.py --contract $C --subject "a wandering swordsman" --category character
# gate any generated file:
python tools/art_audit.py my_asset.png --contract $C --category icon
```
`art_audit.py` checks resolution, palette ΔE, background, and family resemblance, and exits
non-zero on drift with reasons — droppable into CI over `assets/`.

## Changing the style on purpose
```bash
/gat-style-lock --relock    # bumps version, logs a rationale in revisions:, offers a re-audit sweep
```
Deliberately heavyweight. A locked contract is never changed as a side effect of another task.

## Files
- Schema + full law: `knowledge/style/style-contract.schema.md`
- Composer: `tools/style_prompt.py` · Gate: `tools/art_audit.py`
- Skills bound to it: `gat-style-lock`, `gat-asset`, `gat-vfx`
- Art reasoning lenses (for the artist): `knowledge/style/style-lenses.md`
