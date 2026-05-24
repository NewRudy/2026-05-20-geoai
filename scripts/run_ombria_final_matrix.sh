#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-external/OMBRIA}"
EPOCHS="${EPOCHS:-25}"
BATCH_SIZE="${BATCH_SIZE:-8}"
BASE_CHANNELS="${BASE_CHANNELS:-16}"
SEEDS="${SEEDS:-7 13 21}"
RUNS_DIR="${RUNS_DIR:-results/runs/ombria_final}"

mkdir -p external
if [ ! -d "$ROOT" ]; then
  git clone --depth 1 https://github.com/geodrak/OMBRIA.git "$ROOT"
fi

python scripts/train_ombria_unet.py --root "$ROOT" --variant multimodal --dry-run

for seed in $SEEDS; do
  python scripts/train_ombria_unet.py \
    --root "$ROOT" \
    --out-dir "$RUNS_DIR" \
    --variant multimodal \
    --epochs "$EPOCHS" \
    --batch-size "$BATCH_SIZE" \
    --base-channels "$BASE_CHANNELS" \
    --seed "$seed"

  python scripts/train_ombria_unet.py \
    --root "$ROOT" \
    --out-dir "$RUNS_DIR" \
    --variant multimodal \
    --train-degrade-s2 modality_dropout \
    --epochs "$EPOCHS" \
    --batch-size "$BATCH_SIZE" \
    --base-channels "$BASE_CHANNELS" \
    --seed "$seed"

  for mode in none zero_after zero_all noise_after patch_after; do
    python scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --degrade-s2 "$mode" \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed" \
      --eval-checkpoint "$RUNS_DIR/multimodal_none_seed${seed}/best_model.pt"

    python scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --degrade-s2 "$mode" \
      --train-degrade-s2 modality_dropout \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed" \
      --eval-checkpoint "$RUNS_DIR/multimodal_none_train-modality_dropout_seed${seed}/best_model.pt"
  done
done

python scripts/summarize_ombria_runs.py \
  --runs-dir "$RUNS_DIR" \
  --out results/tables/ombria_final_run_summary.csv

python scripts/plot_ombria_results.py \
  --summary results/tables/ombria_final_run_summary.csv \
  --out-md results/tables/ombria_final_results_table.md

python scripts/analyze_ombria_robustness.py \
  --summary results/tables/ombria_final_run_summary.csv \
  --out-csv results/tables/ombria_final_robustness_summary.csv \
  --out-md results/tables/ombria_final_robustness_summary.md

python scripts/plot_ombria_robustness.py \
  --summary results/tables/ombria_final_robustness_summary.csv \
  --out results/figures/ombria_final_robustness.png

python scripts/export_ombria_prediction_panels.py \
  --root "$ROOT" \
  --clean-checkpoint "$RUNS_DIR/multimodal_none_seed7/best_model.pt" \
  --robust-checkpoint "$RUNS_DIR/multimodal_none_train-modality_dropout_seed7/best_model.pt" \
  --out-dir results/figures/ombria_final_qualitative

python - <<'PY'
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

out = Path("results/ombria_final_artifacts.zip")
paths = [
    *Path("results/tables").glob("ombria_final*"),
    *Path("results/figures").glob("ombria_final*"),
]
with ZipFile(out, "w", ZIP_DEFLATED) as zf:
    for path in paths:
        if path.is_file():
            zf.write(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file():
                    zf.write(child)
print(f"wrote {out}")
PY

cat results/tables/ombria_final_robustness_summary.md
