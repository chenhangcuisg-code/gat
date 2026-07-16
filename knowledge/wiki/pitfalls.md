# Pitfalls — real ones, with the fix

Format: **symptom** → **root cause** → **fix** → *how to catch it earlier*. Append, dated.

---

## 2026-07-16 · VFX: correct AES/luminance key but silent black output {#vfx-key}
**Symptom:** VFX sprite sheet is fully transparent or fully black after keying.
**Root cause:** wrong key direction. Energy VFX use `alpha = brightness` (render on pure black,
black→transparent, **additive** blend). Ink-wash inverts: `alpha = darkness`, fixed ink color,
**normal** blend over paper. Mixing them zeroes the output.
**Fix:** set the Style Contract `categories.vfx.background` correctly — `"pure black
(luminance-key)"` for energy, a paper bg for ink — and let `vfx_util.py` pick the matching key.
*Catch earlier:* eyeball frame 08 over a checkerboard before packing; `art_audit.py` bg check.

## 2026-07-16 · Art: whole game slowly drifts off-style {#style-drift}
**Symptom:** icons made in month 3 don't match the hero made in month 1; game looks like an
asset-flip.
**Root cause:** prompts written fresh each time; style lived in the operator's memory, not in a
spec. Text prompts alone drift across runs and models.
**Fix:** freeze `design/art/style-contract.yaml` (`/gat-style-lock`); every asset composes its
prompt via `tools/style_prompt.py` and passes `tools/art_audit.py`. Anchor families to a real
master image (img2img/IP-adapter), not just words — the strongest lever.
*Catch earlier:* CI/pre-commit that runs `art_audit.py` over `assets/`.

## 2026-07-16 · Godot: editor lock-up during agent import {#godot-import-lock}
**Symptom:** Godot editor hangs / `.godot/imported/` corruption when the agent runs headless
`--import` while the user's editor is open.
**Root cause:** two processes fighting over the import cache.
**Fix:** if the user's editor is open, prefer Hastur `smoke`/targeted ops via `gop.py`; do not
run headless `--import`. Only import headless when no editor is running.
*Catch earlier:* check for a running editor / Hastur broker before any import.

## 2026-07-16 · Saves: test run clobbers player progress {#save-slot}
**Symptom:** verification overwrites a real save.
**Root cause:** tests wrote to slot 1 / autosave.
**Fix:** dedicate a numbered **test slot**; `/gat-verify` and `/gat-implement` only ever write
there. Never touch player progress or the meta pointer without restoring it.
*Catch earlier:* SaveSystem asserts the active slot == test slot during automated runs.

## 2026-07-16 · Balance: "feels fine" ships broken numbers {#balance-feel}
**Symptom:** a skill/economy value is wildly off but passed review.
**Root cause:** tuned by feel, no simulation.
**Fix:** two-headed method — static power/cost index over `data/*.json` **and** a combat/economy
sim with pressure-band calibration. Flag anything ~3× its band.
*Catch earlier:* make the sim part of `/gat-verify`, block "done" without it.

<!-- Append new pitfalls above this line. -->
