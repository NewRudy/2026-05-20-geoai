#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-external/OMBRIA}"
EPOCHS="${EPOCHS:-5}"
BATCH_SIZE="${BATCH_SIZE:-8}"
BASE_CHANNELS="${BASE_CHANNELS:-16}"

mkdir -p external
if [ ! -d "$ROOT" ]; then
  git clone --depth 1 https://github.com/geodrak/OMBRIA.git "$ROOT"
fi

python scripts/train_ombria_unet.py --root "$ROOT" --variant multimodal --dry-run

for variant in s1_after s1_bitemporal s2_after s2_bitemporal multimodal; do
  python scripts/train_ombria_unet.py \
    --root "$ROOT" \
    --variant "$variant" \
    --epochs "$EPOCHS" \
    --batch-size "$BATCH_SIZE" \
    --base-channels "$BASE_CHANNELS"
done

for mode in none zero_after zero_all noise_after patch_after; do
  python scripts/train_ombria_unet.py \
    --root "$ROOT" \
    --variant multimodal \
    --degrade-s2 "$mode" \
    --batch-size "$BATCH_SIZE" \
    --base-channels "$BASE_CHANNELS" \
    --eval-checkpoint results/runs/ombria/multimodal_none_seed7/best_model.pt
done

python scripts/summarize_ombria_runs.py \
  --runs-dir results/runs/ombria \
  --out results/tables/ombria_run_summary.csv

python scripts/plot_ombria_results.py \
  --summary results/tables/ombria_run_summary.csv \
  --out-md results/tables/ombria_results_table.md

cat results/tables/ombria_results_table.md

