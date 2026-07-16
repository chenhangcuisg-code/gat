---
name: gat-style-lock
description: "Freeze the game's art direction into an enforceable Style Contract (design/art/style-contract.yaml) that every asset-generation skill must obey. Produces the locked prompt prefix/suffix, negative prompt, palette, resolution, seed strategy, and reference anchors so all generated art stays in one consistent style forever. Use after art-direction.md exists and before generating any asset. Re-lock with --relock to change a frozen style on purpose. Triggers: 锁定画风, style lock, freeze art style, 统一风格, style contract, 严格约束prompt."
argument-hint: "[--relock] [--from design/art/art-direction.md]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, PowerShell
---

# gat-style-lock — freeze the art style into an enforceable contract

Request: $ARGUMENTS

This is GAT's answer to art-style drift. Once a game commits to a look
("papercut wuxia", "chunky gameboy pixel", "glowing 国风水墨"), **every** future asset —
icons months later, a new boss's VFX, a DLC tileset — must look like the same artist made
it. `gat-style-lock` converts the human-readable `design/art/art-direction.md` into a
**machine-enforceable `design/art/style-contract.yaml`** that `gat-asset`, `gat-vfx`, and
`gat-icon` are *required* to load and obey.

Read `knowledge/style/style-contract.schema.md` first — it is the law this skill enforces.

## When to run

- **First lock:** after `/gat-brainstorm` (which writes `art-direction.md`), before any asset
  is generated. No contract → asset skills refuse to run.
- **Re-lock (`--relock`):** only when the team *decides* to change the style. Bumps `version`,
  appends a `revisions:` entry with a rationale, and offers to re-audit existing assets.

## Procedure

1. **Read the source.** Load `design/art/art-direction.md` (and `game.md` for context). If it
   is missing or vague on palette / resolution / view / rendering, **ask** rather than invent —
   a wrong lock poisons every asset downstream.
2. **Extract the contract fields** into `design/art/style-contract.yaml` following the schema:
   - `palette` (primary / accent / secondary / forbidden + `tolerance_deltaE`)
   - `rendering` (resolution, view, outline, shading, background)
   - `prompt_contract` (positive_prefix, positive_suffix, style_anchor_phrases, negative,
     reference_images)
   - `model` (backend, params, seed_strategy, base_seed)
   - `categories` overrides (icon / character / vfx / tileset) — each inherits everything, then patches
   - `enforcement` (checks, on_fail)
3. **Choose a base seed** and set `seed_strategy: fixed-per-family` unless the user wants
   pure reproducibility (`fixed`) or free variation (`free`).
4. **Establish a master reference image.** The single strongest anti-drift lever is a real
   pixel exemplar. If one exists (e.g. the hero the user already generated), point
   `reference_images` and `enforcement.family_resemblance_ref` at it. If not, generate ONE
   canonical asset now, get the user's sign-off, save it as `design/art/refs/<name>_master.png`,
   and anchor the family to it.
5. **Set `locked: true`** and write the file.
6. **Verify the contract is executable:**
   ```bash
   python tools/style_prompt.py --contract design/art/style-contract.yaml \
       --subject "test subject" --category icon
   ```
   Confirm the composed prompt keeps every `style_anchor_phrases` entry and the params look right.
7. **Report** the locked one-liner, palette, backend, and where the contract lives. Tell the
   user that from now on all asset skills are bound to it, and how to `--relock`.

## Re-lock rules (`--relock`)

1. Read the current contract; do not silently overwrite.
2. Apply the requested change, **bump `version`**, append to `revisions:` with `at`, `by`,
   and a one-line `rationale`.
3. Offer to sweep existing assets through `tools/art_audit.py` against the new contract and
   list which ones now fail (candidates for regeneration).
4. Never change a locked contract as a side effect of another task. Style changes are explicit.

## Hard rules

- Do not generate assets here — this skill only produces the contract. Generation is
  `gat-asset` / `gat-vfx`.
- Do not leave palette / resolution / background unspecified — those are the audit's teeth.
- Keep `style_anchor_phrases` short and non-negotiable (2–4 phrases). They are the invariants
  `style_prompt.py` guarantees survive every prompt.
- After locking, follow the **self-evolving protocol** (see `/gat-evolve`): if you discovered a
  prompt phrasing or negative term that fixed a recurring artifact, record it in
  `knowledge/wiki/patterns.md` so future locks start smarter.
