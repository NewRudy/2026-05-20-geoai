# OMBRIA Cloud Pilot Commands

These commands are intended for Colab or Kaggle, not the local Mac.

## Setup

```bash
git clone https://github.com/NewRudy/2026-05-20-geoai.git
cd 2026-05-20-geoai
mkdir -p external
git clone https://github.com/geodrak/OMBRIA.git external/OMBRIA
pip install torch torchvision pillow numpy
```

From this project repository:

```bash
python scripts/train_ombria_unet.py --root external/OMBRIA --dry-run --variant multimodal
```

## Minimal Training Runs

Start with one quick run:

```bash
python scripts/train_ombria_unet.py \
  --root external/OMBRIA \
  --variant s1_after \
  --epochs 5 \
  --batch-size 8 \
  --base-channels 16
```

Then run the core variants:

```bash
for variant in s1_after s1_bitemporal s2_after s2_bitemporal multimodal; do
  python scripts/train_ombria_unet.py \
    --root external/OMBRIA \
    --variant "$variant" \
    --epochs 30 \
    --batch-size 8 \
    --base-channels 24
done
```

## S2 Degradation Tests

Train multimodal once on clean inputs:

```bash
python scripts/train_ombria_unet.py \
  --root external/OMBRIA \
  --variant multimodal \
  --degrade-s2 none \
  --epochs 30 \
  --batch-size 8 \
  --base-channels 24
```

Then evaluate the same checkpoint under separate S2 degradation modes:

```bash
for mode in none zero_after zero_all noise_after patch_after; do
  python scripts/train_ombria_unet.py \
    --root external/OMBRIA \
    --variant multimodal \
    --degrade-s2 "$mode" \
    --batch-size 8 \
    --base-channels 24 \
    --eval-checkpoint results/runs/ombria/multimodal_none_seed7/best_model.pt
done
```

## Robust Multimodal Baseline

Train one additional clean multimodal checkpoint with lightweight S2 modality
dropout. This is the smallest method-extension baseline: the model still sees
the same OMBRIA data and the same U-Net architecture, but training includes
random clean, zeroed, noisy, and patch-masked S2 inputs.

```bash
python scripts/train_ombria_unet.py \
  --root external/OMBRIA \
  --variant multimodal \
  --train-degrade-s2 modality_dropout \
  --epochs 30 \
  --batch-size 8 \
  --base-channels 24
```

Evaluate that robust checkpoint under the same degradation modes:

```bash
for mode in none zero_after zero_all noise_after patch_after; do
  python scripts/train_ombria_unet.py \
    --root external/OMBRIA \
    --variant multimodal \
    --degrade-s2 "$mode" \
    --train-degrade-s2 modality_dropout \
    --batch-size 8 \
    --base-channels 24 \
    --eval-checkpoint results/runs/ombria/multimodal_none_train-modality_dropout_seed7/best_model.pt
done
```

Expected interpretation:

- If clean performance remains close to the standard multimodal checkpoint and
  degraded performance improves, the paper has a stronger method contribution.
- If clean performance collapses, reduce degradation probability or frame the
  result as a robustness-accuracy tradeoff.

## Interpretation Guardrail

Do not use pilot metrics as final manuscript results. Final results need:

- fixed seeds,
- saved configs,
- consistent clean training,
- checkpoint reload for inference-time degradation,
- repeated runs or a clear reason for single-run reporting.

## Final Multi-Seed Matrix

After the short pilot produces a coherent signal, run the repeatable final
matrix on Colab/T4 or Kaggle GPU:

```bash
bash scripts/run_ombria_final_matrix.sh
```

Default settings:

- three seeds: `7 13 21`
- 25 epochs
- base channels: `16`
- clean multimodal checkpoint and modality-dropout multimodal checkpoint
- five test conditions: clean, patch-masked S2, noisy S2, after-event S2
  missing, and all S2 missing

The command writes:

- `results/tables/ombria_final_run_summary.csv`
- `results/tables/ombria_final_results_table.md`
- `results/tables/ombria_final_robustness_summary.csv`
- `results/tables/ombria_final_robustness_summary.md`
- `results/figures/ombria_final_robustness.png`
- `results/figures/ombria_final_qualitative/*.png`
- `results/ombria_final_artifacts.zip`

If Colab time is tight, reduce only `EPOCHS` first:

```bash
EPOCHS=15 bash scripts/run_ombria_final_matrix.sh
```

Do not reduce to one seed for manuscript results unless the paper explicitly
frames the experiment as a pilot or short communication.
