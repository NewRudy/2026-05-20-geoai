#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-external/OMBRIA}"
EPOCHS="${EPOCHS:-25}"
BATCH_SIZE="${BATCH_SIZE:-8}"
BASE_CHANNELS="${BASE_CHANNELS:-16}"
SEEDS="${SEEDS:-7}"
RUNS_DIR="${RUNS_DIR:-results/runs/ombria_graceful}"
PYTHON="${PYTHON:-python}"

TEST_MODES="${TEST_MODES:-none cloud_after_10 cloud_after_30 cloud_after_50 cloud_after_70 patch_after zero_after zero_all noise_after}"
ANCHOR_MODES="${ANCHOR_MODES:-sar_anchor_severe_w010 sar_anchor_severe_w020 sar_anchor_severe_w025}"

anchor_weight_for_mode() {
  case "$1" in
    sar_anchor_severe_w010) printf "0.10" ;;
    sar_anchor_severe_w020) printf "0.20" ;;
    sar_anchor_severe_w025) printf "0.25" ;;
    *) printf "0.20" ;;
  esac
}

summarize_artifacts() {
  local suffix="$1"

  "$PYTHON" scripts/summarize_ombria_runs.py \
    --runs-dir "$RUNS_DIR" \
    --out "results/tables/ombria_anchor_tuning_run_summary${suffix}.csv"

  "$PYTHON" scripts/analyze_ombria_robustness.py \
    --summary "results/tables/ombria_anchor_tuning_run_summary${suffix}.csv" \
    --out-csv "results/tables/ombria_anchor_tuning_robustness_summary${suffix}.csv" \
    --out-md "results/tables/ombria_anchor_tuning_robustness_summary${suffix}.md"

  "$PYTHON" scripts/analyze_ombria_graceful.py \
    --summary "results/tables/ombria_anchor_tuning_run_summary${suffix}.csv" \
    --out-csv "results/tables/ombria_anchor_tuning_metrics${suffix}.csv" \
    --out-md "results/tables/ombria_anchor_tuning_metrics${suffix}.md"

  "$PYTHON" scripts/plot_ombria_robustness.py \
    --summary "results/tables/ombria_anchor_tuning_robustness_summary${suffix}.csv" \
    --out "results/figures/ombria_anchor_tuning_robustness${suffix}.png"
}

mkdir -p external
if [ ! -d "$ROOT" ]; then
  git clone --depth 1 https://github.com/geodrak/OMBRIA.git "$ROOT"
fi

"$PYTHON" scripts/train_ombria_unet.py --root "$ROOT" --variant multimodal --dry-run

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

  for mode in $ANCHOR_MODES; do
    anchor_checkpoint="$RUNS_DIR/multimodal_none_train-${mode}_seed${seed}/best_model.pt"
    if [ ! -f "$anchor_checkpoint" ]; then
      "$PYTHON" scripts/train_ombria_unet.py \
        --root "$ROOT" \
        --out-dir "$RUNS_DIR" \
        --variant multimodal \
        --train-degrade-s2 "$mode" \
        --anchor-checkpoint "$s1_checkpoint" \
        --anchor-weight "$(anchor_weight_for_mode "$mode")" \
        --epochs "$EPOCHS" \
        --batch-size "$BATCH_SIZE" \
        --base-channels "$BASE_CHANNELS" \
        --seed "$seed"
    fi
  done

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

    for anchor_mode in $ANCHOR_MODES; do
      anchor_checkpoint="$RUNS_DIR/multimodal_none_train-${anchor_mode}_seed${seed}/best_model.pt"
      "$PYTHON" scripts/train_ombria_unet.py \
        --root "$ROOT" \
        --out-dir "$RUNS_DIR" \
        --variant multimodal \
        --degrade-s2 "$mode" \
        --train-degrade-s2 "$anchor_mode" \
        --batch-size "$BATCH_SIZE" \
        --base-channels "$BASE_CHANNELS" \
        --seed "$seed" \
        --eval-checkpoint "$anchor_checkpoint"
    done

    summarize_artifacts "_partial_seed${seed}" || true
    if [ -f "results/tables/ombria_anchor_tuning_metrics_partial_seed${seed}.md" ]; then
      cat "results/tables/ombria_anchor_tuning_metrics_partial_seed${seed}.md"
    fi
  done

  summarize_artifacts "_partial_seed${seed}"
done

summarize_artifacts ""
cat results/tables/ombria_anchor_tuning_metrics.md
