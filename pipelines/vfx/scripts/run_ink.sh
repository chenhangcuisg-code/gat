#!/bin/bash
export HF_ENDPOINT=https://hf-mirror.com
export CUDA_VISIBLE_DEVICES=6
cd /data/chenhang/pixgen_work
source /data/chenhang/miniconda3/etc/profile.d/conda.sh
conda activate pixgen
echo "=== INK FLUX $(date +%T) ==="; python vfx/vfx_ink.py
echo "=== INK ADIFF $(date +%T) ==="; python vfx/vfx_ink_adiff.py
echo "=== INK COMPARE $(date +%T) ==="; python vfx/ink_compare.py
echo "=== INK ALL DONE $(date +%T) ==="
