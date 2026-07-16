#!/bin/bash
set -e
export HF_ENDPOINT=https://hf-mirror.com
export CUDA_VISIBLE_DEVICES=6
cd /data/chenhang/pixgen_work
source /data/chenhang/miniconda3/etc/profile.d/conda.sh
conda activate pixgen
echo "=== P1 AnimateDiff $(date +%T) ==="; python vfx/p1_animatediff.py
echo "=== P2 FLUX+procedural $(date +%T) ==="; python vfx/p2_flux_procedural.py
echo "=== P3 SDXL ctrl $(date +%T) ==="; python vfx/p3_sdxl_ctrl.py
echo "=== COMPARE $(date +%T) ==="; python vfx/compare_vfx.py
echo "=== ALL DONE $(date +%T) ==="
