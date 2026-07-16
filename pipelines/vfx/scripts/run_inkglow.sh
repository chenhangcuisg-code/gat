#!/bin/bash
export HF_ENDPOINT=https://hf-mirror.com
export CUDA_VISIBLE_DEVICES=6
cd /data/chenhang/pixgen_work
source /data/chenhang/miniconda3/etc/profile.d/conda.sh
conda activate pixgen
echo "=== INKGLOW FLUX $(date +%T) ==="; python vfx/vfx_inkglow.py
echo "=== INKGLOW ADIFF $(date +%T) ==="; python vfx/vfx_inkglow_adiff.py
echo "=== INKGLOW COMPARE $(date +%T) ==="; python vfx/inkglow_compare.py
echo "=== INKGLOW ALL DONE $(date +%T) ==="
