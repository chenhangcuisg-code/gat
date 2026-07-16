# Deploying the VFX pipeline on a GPU server

The `gat-vfx` skill and `pipelines/vfx/` run open diffusion models (FLUX.1-schnell · AnimateDiff
· SDXL · DreamShaper-8) to generate skill-effect sprite sheets. That needs a CUDA GPU — the
reference setup is a **single A100-80GB**, and **no paid APIs** are used (all models are cached
open weights). This guide covers running it locally, on a rented box, or from your workstation
over SSH.

> Static art (`gat-asset` via `gpt-image-2`) does *not* need this — only the VFX pipelines do.

## 1. Provision a GPU box

Any CUDA GPU with enough VRAM works; FLUX + SDXL comfortably want **24 GB+**, the full suite
wants **40–80 GB**. Options: a cloud A100/L40S/4090 instance, a lab server, or your own
workstation. Note the SSH alias — GAT's `WORKSPACE.md` convention records it under `## Servers`.

## 2. Environment

```bash
# CUDA + a recent PyTorch matching the driver, then:
python -m venv .venv && source .venv/bin/activate
pip install "torch --index-url https://download.pytorch.org/whl/cu121"   # match your CUDA
pip install diffusers transformers accelerate safetensors pillow numpy imageio pyyaml
# GAT style tools also want:
pip install pillow numpy pyyaml
```

## 3. Model cache (first run pulls weights)

```bash
export HF_ENDPOINT=https://hf-mirror.com     # only if HuggingFace is blocked in your region
export HF_HOME=/data/hf                       # put the cache on a big disk
export CUDA_VISIBLE_DEVICES=0
```
Models fetched on first run: `black-forest-labs/FLUX.1-schnell`,
`guoyww/animatediff-motion-adapter-v1-5-2`, `Lykon/dreamshaper-8`,
`stabilityai/stable-diffusion-xl-base-1.0`, `madebyollin/sdxl-vae-fp16-fix`.

## 4. Generate

```bash
cd pipelines/vfx
# production default (FLUX texture + procedural motion, controllable, perfect-loop):
python scripts/vfx_batch.py
# 国风水墨 glowing-ink energy:
python scripts/vfx_inkglow.py && python scripts/vfx_inkglow_adiff.py
# organic/chaotic motion (fire, ink flow) via AnimateDiff:
python scripts/p1b_animatediff.py
```
Output lands in `pipelines/vfx/godot_package/vfx/<set>/<effect>/` as RGBA frames + `<effect>.tres`.
Read `pipelines/vfx/REPORT.md` for the full method, every parameter, and pitfalls.

## 5. Style-lock still applies

Even on the GPU box, compose the texture prompt through the contract and audit key frames:
```bash
python tools/style_prompt.py --contract design/art/style-contract.yaml --subject "<effect>" --category vfx
python tools/art_audit.py <effect>_08.png --contract design/art/style-contract.yaml --category vfx
```

## 6. Remote-from-workstation pattern

If you drive the agent on a laptop but generate on a server:
1. Record the server SSH alias + remote workspace dir in the game's `WORKSPACE.md` (`## Servers`).
2. Sync the game repo (or just `design/art/style-contract.yaml` + subject list) to the box.
3. Run the pipeline over SSH; pull back `godot_package/vfx/`.
4. `/gat-implement` wires the returned `.tres` into `res://vfx/` in the (local) Godot editor.

## 7. Reproducibility

The Style Contract's `model.base_seed` + fixed params make an effect family reproducible. Pin
your `diffusers`/`torch` versions in the server's `requirements.txt` so a re-run months later
still matches — record the working versions in `knowledge/wiki/methods.md`.

## Troubleshooting

- **OOM** — lower resolution/batch, enable attention slicing / model-cpu-offload in the script,
  or use a smaller model (DreamShaper-8 instead of SDXL-base).
- **Slow first run** — that's the weight download; warm the cache once.
- **HF blocked** — set `HF_ENDPOINT=https://hf-mirror.com`.
- **Key/transparency wrong** — see `knowledge/wiki/pitfalls.md#vfx-key` (energy vs. ink invert).
