# Methods — reusable recipes

Copy-pasteable, with *when it applies*. Append, dated.

---

## Compose a style-locked prompt
```bash
python tools/style_prompt.py --contract design/art/style-contract.yaml \
    --subject "<subject only, no style words>" --category icon|character|vfx|tileset
```
Returns JSON: positive/negative/params/seed/backend/size/reference_images. Use verbatim.
*When:* every asset generation, always.

## Audit an asset against the contract
```bash
python tools/art_audit.py <file> --contract design/art/style-contract.yaml --category <cat>
# exit 0 PASS, 1 FAIL(+reasons). Checks: resolution, palette ΔE, background, family resemblance.
```
*When:* after every generation; in CI over `assets/`.

## Generate skill VFX (P2, production default)
```bash
# on a CUDA box with diffusers env; see docs/deployment/vfx-gpu-server.md
export HF_ENDPOINT=https://hf-mirror.com   # if HF blocked
export CUDA_VISIBLE_DEVICES=0
python pipelines/vfx/scripts/vfx_batch.py       # FLUX texture + procedural motion archetypes
python pipelines/vfx/scripts/vfx_inkglow.py     # 国风水墨 glowing-ink variant
```
Output: `pipelines/vfx/godot_package/vfx/<set>/<effect>/` → frames + `<effect>.tres`.
*When:* `/gat-vfx`. Pick P1 (`p1b_animatediff.py`) only for organic/chaotic motion.

## Drive a running Godot editor (Hastur)
```bash
python skills/godot-editor-control/scripts/gop.py open_scene res://scenes/main.tscn
python skills/godot-editor-control/scripts/gop.py add_node --parent . --type Node2D --name Foo
python skills/godot-editor-control/scripts/gop.py attach_script --node Foo --path res://src/foo.gd
python skills/godot-editor-control/scripts/gop.py play        # run; then get debug output
```
Offline self-test without an editor: `python skills/godot-editor-control/scripts/mock_broker.py`.
*When:* `/gat-implement`, `/gat-verify` runtime smoke. Respect an open editor (no headless import).

## Install into a game repo (dual runtime)
```bash
bash install.sh --runtime both --target /path/to/game     # Claude + Codex
# or:  pwsh -File install.ps1 -Runtime claude -Target C:\path\to\game
```
*When:* wiring a new game project to the toolkit.

<!-- Append new methods above this line. -->
