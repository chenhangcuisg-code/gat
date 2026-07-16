#!/bin/bash
export HF_ENDPOINT=https://hf-mirror.com
export CUDA_VISIBLE_DEVICES=6
cd /data/chenhang/pixgen_work
source /data/chenhang/miniconda3/etc/profile.d/conda.sh
conda activate pixgen
echo "=== FLUX BATCH $(date +%T) ==="; python vfx/vfx_batch.py
echo "=== ADIFF BATCH $(date +%T) ==="; python vfx/vfx_adiff_batch.py
echo "=== TRANSPARENCY DEMO $(date +%T) ==="; python vfx/transparency_demo.py
echo "=== BATCH COMPARE $(date +%T) ==="; python vfx/batch_compare.py
echo "=== ALL BATCH DONE $(date +%T) ==="
