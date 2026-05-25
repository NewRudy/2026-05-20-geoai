# Follow-Up Local Pilot

Date: 2026-05-25

## Purpose

This pilot was run locally on the Mac mini to verify that the follow-up
experiment code actually runs end to end before spending more cloud quota. It is
not a final manuscript result because it uses one seed and five epochs.

Command pattern:

```bash
RUNS_DIR=results/runs/ombria_followup_local_pilot \
SEEDS=7 \
EPOCHS=5 \
BATCH_SIZE=8 \
BASE_CHANNELS=16 \
PYTHON=.venv/bin/python \
bash scripts/run_ombria_followup_matrix.sh
```

Additional clean-checkpoint evaluations were run for the same pilot checkpoint
so deltas could be computed against a matched clean baseline.

## Code Issues Fixed

- `torch` and `torchvision` were installed in the local virtual environment.
- `scripts/train_ombria_unet.py` now defaults DataLoader workers to `0`, which
  avoids macOS multiprocessing pickling failures.
- `scripts/run_ombria_final_matrix.sh` and
  `scripts/run_ombria_followup_matrix.sh` now accept `PYTHON=...`, so they work
  locally and on Colab.
- `scripts/run_ombria_followup_matrix.sh` now evaluates the matched clean
  checkpoint under all S2 degradation modes before summarizing deltas.

## One-Seed Pilot Readout

| Test S2 degradation | Training | IoU | F1 | Delta IoU |
|---|---|---:|---:|---:|
| none | clean | 0.6307 | 0.7631 |  |
| none | modality_dropout_light | 0.6229 | 0.7575 | -0.0078 |
| none | modality_dropout_balanced | 0.6045 | 0.7429 | -0.0262 |
| none | modality_dropout_patch | 0.5886 | 0.7269 | -0.0421 |
| patch_after | clean | 0.5014 | 0.6472 |  |
| patch_after | modality_dropout_light | 0.5179 | 0.6656 | +0.0165 |
| patch_after | modality_dropout_balanced | 0.5127 | 0.6645 | +0.0113 |
| patch_after | modality_dropout_patch | 0.4972 | 0.6449 | -0.0042 |
| noise_after | clean | 0.3087 | 0.4671 |  |
| noise_after | modality_dropout_light | 0.2867 | 0.4353 | -0.0220 |
| noise_after | modality_dropout_balanced | 0.2848 | 0.4338 | -0.0239 |
| noise_after | modality_dropout_patch | 0.2900 | 0.4396 | -0.0187 |
| zero_after | clean | 0.3975 | 0.5435 |  |
| zero_after | modality_dropout_light | 0.4194 | 0.5703 | +0.0219 |
| zero_after | modality_dropout_balanced | 0.4126 | 0.5702 | +0.0151 |
| zero_after | modality_dropout_patch | 0.4132 | 0.5619 | +0.0157 |
| zero_all | clean | 0.2245 | 0.3371 |  |
| zero_all | modality_dropout_light | 0.3505 | 0.5079 | +0.1260 |
| zero_all | modality_dropout_balanced | 0.3911 | 0.5478 | +0.1666 |
| zero_all | modality_dropout_patch | 0.3876 | 0.5406 | +0.1631 |

## Interpretation

The pilot supports a narrower innovation point:

> Lightweight S2 degradation training can substantially improve robustness to
> missing optical inputs while keeping clean accuracy loss small if the
> degradation schedule is tuned.

It does not yet support a broad claim of robustness to all optical degradation.
The `noise_after` condition remains weak in this local pilot. The
`modality_dropout_patch` schedule also does not fix the patch-masking case.

Best candidates for a full Colab/T4 follow-up:

1. `modality_dropout_light`: smallest clean penalty and positive gains for
   `patch_after`, `zero_after`, and `zero_all`.
2. `modality_dropout_balanced`: stronger `zero_all` gain, still acceptable
   clean penalty, but no noise recovery.

The next cloud run should use three seeds and 25 epochs before making a final
SCI-paper decision.

The default follow-up script now runs only these two candidates to avoid
spending cloud time on the patch-focused schedule, which did not improve the
patch-masking case in this pilot.
