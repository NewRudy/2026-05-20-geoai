#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-external/OMBRIA}"
EPOCHS="${EPOCHS:-25}"
BATCH_SIZE="${BATCH_SIZE:-8}"
BASE_CHANNELS="${BASE_CHANNELS:-16}"
SEEDS="${SEEDS:-7}"
RUNS_DIR="${RUNS_DIR:-results/runs/ombria_quality_anchor}"
PYTHON="${PYTHON:-python}"
ANCHOR_WEIGHT="${ANCHOR_WEIGHT:-0.25}"
BACKUP_DIR="${BACKUP_DIR:-}"

TEST_MODES="${TEST_MODES:-none cloud_after_10 cloud_after_30 cloud_after_50 cloud_after_70 patch_after zero_after zero_all noise_after}"

summarize_artifacts() {
  local suffix="$1"

  "$PYTHON" scripts/summarize_ombria_runs.py \
    --runs-dir "$RUNS_DIR" \
    --out "results/tables/ombria_quality_anchor_run_summary${suffix}.csv"

  "$PYTHON" scripts/analyze_ombria_robustness.py \
    --summary "results/tables/ombria_quality_anchor_run_summary${suffix}.csv" \
    --out-csv "results/tables/ombria_quality_anchor_robustness_summary${suffix}.csv" \
    --out-md "results/tables/ombria_quality_anchor_robustness_summary${suffix}.md"

  "$PYTHON" scripts/analyze_ombria_graceful.py \
    --summary "results/tables/ombria_quality_anchor_run_summary${suffix}.csv" \
    --out-csv "results/tables/ombria_quality_anchor_graceful_metrics${suffix}.csv" \
    --out-md "results/tables/ombria_quality_anchor_graceful_metrics${suffix}.md"

  "$PYTHON" scripts/evaluate_ombria_quality_gate.py \
    --metrics "results/tables/ombria_quality_anchor_graceful_metrics${suffix}.csv" \
    --out-md "results/tables/ombria_quality_anchor_gate${suffix}.md"

  "$PYTHON" scripts/plot_ombria_robustness.py \
    --summary "results/tables/ombria_quality_anchor_robustness_summary${suffix}.csv" \
    --out "results/figures/ombria_quality_anchor_robustness${suffix}.png"

  if [ -n "$BACKUP_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    cp "results/tables/ombria_quality_anchor_run_summary${suffix}.csv" "$BACKUP_DIR/"
    cp "results/tables/ombria_quality_anchor_robustness_summary${suffix}.csv" "$BACKUP_DIR/"
    cp "results/tables/ombria_quality_anchor_robustness_summary${suffix}.md" "$BACKUP_DIR/"
    cp "results/tables/ombria_quality_anchor_graceful_metrics${suffix}.csv" "$BACKUP_DIR/"
    cp "results/tables/ombria_quality_anchor_graceful_metrics${suffix}.md" "$BACKUP_DIR/"
    cp "results/tables/ombria_quality_anchor_gate${suffix}.md" "$BACKUP_DIR/"
    cp "results/figures/ombria_quality_anchor_robustness${suffix}.png" "$BACKUP_DIR/"
  fi
}

mkdir -p external
if [ ! -d "$ROOT" ]; then
  git clone --depth 1 https://github.com/geodrak/OMBRIA.git "$ROOT"
fi

"$PYTHON" scripts/train_ombria_unet.py --root "$ROOT" --variant multimodal --dry-run
"$PYTHON" scripts/train_ombria_unet.py \
  --root "$ROOT" \
  --variant multimodal \
  --s2-quality binary \
  --dry-run

for seed in $SEEDS; do
  s1_checkpoint="$RUNS_DIR/s1_bitemporal_none_seed${seed}/best_model.pt"
  if [ ! -f "$s1_checkpoint" ]; then
    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant s1_bitemporal \
      --epochs "$EPOCHS" \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed"
  fi

  clean_checkpoint="$RUNS_DIR/multimodal_none_seed${seed}/best_model.pt"
  if [ ! -f "$clean_checkpoint" ]; then
    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --epochs "$EPOCHS" \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed"
  fi

  light_checkpoint="$RUNS_DIR/multimodal_none_train-modality_dropout_light_seed${seed}/best_model.pt"
  if [ ! -f "$light_checkpoint" ]; then
    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --train-degrade-s2 modality_dropout_light \
      --epochs "$EPOCHS" \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed"
  fi

  quality_checkpoint="$RUNS_DIR/multimodal_quality-binary_none_train-quality_dropout_light_seed${seed}/best_model.pt"
  if [ ! -f "$quality_checkpoint" ]; then
    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --s2-quality binary \
      --train-degrade-s2 quality_dropout_light \
      --epochs "$EPOCHS" \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed"
  fi

  quality_anchor_checkpoint="$RUNS_DIR/multimodal_quality-binary_none_train-sar_anchor_severe_w025_seed${seed}/best_model.pt"
  if [ ! -f "$quality_anchor_checkpoint" ]; then
    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --s2-quality binary \
      --train-degrade-s2 sar_anchor_severe_w025 \
      --anchor-checkpoint "$s1_checkpoint" \
      --anchor-weight "$ANCHOR_WEIGHT" \
      --epochs "$EPOCHS" \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed"
  fi

  for mode in $TEST_MODES; do
    echo "=== evaluating test degradation: seed=${seed} mode=${mode} ==="

    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --degrade-s2 "$mode" \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed" \
      --eval-checkpoint "$clean_checkpoint"

    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --degrade-s2 "$mode" \
      --train-degrade-s2 modality_dropout_light \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed" \
      --eval-checkpoint "$light_checkpoint"

    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --s2-quality binary \
      --degrade-s2 "$mode" \
      --train-degrade-s2 quality_dropout_light \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed" \
      --eval-checkpoint "$quality_checkpoint"

    "$PYTHON" scripts/train_ombria_unet.py \
      --root "$ROOT" \
      --out-dir "$RUNS_DIR" \
      --variant multimodal \
      --s2-quality binary \
      --degrade-s2 "$mode" \
      --train-degrade-s2 sar_anchor_severe_w025 \
      --batch-size "$BATCH_SIZE" \
      --base-channels "$BASE_CHANNELS" \
      --seed "$seed" \
      --eval-checkpoint "$quality_anchor_checkpoint"
  done

  summarize_artifacts "_partial_seed${seed}"
  cat "results/tables/ombria_quality_anchor_robustness_summary_partial_seed${seed}.md"
  cat "results/tables/ombria_quality_anchor_gate_partial_seed${seed}.md"
done

summarize_artifacts ""
cat results/tables/ombria_quality_anchor_robustness_summary.md
cat results/tables/ombria_quality_anchor_gate.md
