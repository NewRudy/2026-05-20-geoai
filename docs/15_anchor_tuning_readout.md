# SAR Anchor Tuning Readout

Date: 2026-05-27

## Current Result

The seed-7 Colab weight-ablation run completed successfully. The best current
candidate is `sar_anchor_severe_w020` because it preserves clean performance
while improving the degraded Sentinel-2 conditions more strongly than both
ordinary modality dropout and the earlier `w025` anchor setting.

| Training | Clean IoU | Clean delta | Mean degraded IoU | Worst degraded IoU | Zero-all IoU | S1 IoU | Zero-all gap vs S1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| none | 0.6830 | 0.0000 | 0.4392 | 0.1235 | 0.1235 | 0.4081 | -0.2846 |
| modality_dropout_light | 0.6627 | -0.0203 | 0.5052 | 0.3523 | 0.4066 | 0.4081 | -0.0015 |
| sar_anchor_severe_w010 | 0.6607 | -0.0223 | 0.5174 | 0.3428 | 0.3428 | 0.4081 | -0.0653 |
| sar_anchor_severe_w020 | 0.6787 | -0.0043 | 0.5468 | 0.4116 | 0.4116 | 0.4081 | 0.0035 |
| sar_anchor_severe_w025 | 0.6781 | -0.0048 | 0.5392 | 0.3884 | 0.3884 | 0.4081 | -0.0197 |

## Interpretation

This is a meaningful result, but not yet a manuscript-ready claim.

The positive signal is that `sar_anchor_severe_w020` improves mean degraded IoU
and worst degraded IoU while nearly matching the clean multimodal baseline.
That is stronger than ordinary modality dropout as a paper story because the
method is not just randomly hiding optical channels; it explicitly encourages
the multimodal model to approach the SAR-only fallback when optical reliability
collapses.

The important update is that `w020` also fixes the earlier `w025` weakness:
`zero_all` is now slightly above the S1 fallback and above
`modality_dropout_light`. This makes `w020` the current main method candidate.

## Completed Follow-Up

The weight ablation was:

```bash
EPOCHS=25 BATCH_SIZE=8 BASE_CHANNELS=16 SEEDS="7" \
ANCHOR_MODES="sar_anchor_severe_w010 sar_anchor_severe_w020" \
bash scripts/run_ombria_anchor_tuning_matrix.sh
```

It showed that the effect is not a one-off `w025` artifact. `w020` is the best
seed-7 setting.

## Active Follow-Up

Run `sar_anchor_severe_w020` across additional seeds:

```bash
EPOCHS=25 BATCH_SIZE=8 BASE_CHANNELS=16 SEEDS="13 21" \
ANCHOR_MODES="sar_anchor_severe_w020" \
bash scripts/run_ombria_anchor_tuning_matrix.sh
```

This is the key manuscript gate. If the trend survives, the project can move
from idea validation to figure generation and paper drafting.

## Decision Rule

Proceed to manuscript-oriented result preparation if `w020` satisfies these
criteria across multiple seeds:

- clean IoU delta no worse than about `-0.02`;
- mean degraded IoU above `modality_dropout_light`;
- worst degraded IoU at least close to or above `0.38`;
- cloud and noise degradation rows improve over both clean training and light
  modality dropout;
- no obvious collapse under `zero_after` or `zero_all`.

If multi-seed `w020` fails, do not draft the manuscript around this method;
either fall back to a narrower robustness-audit paper or test the quality-channel
backup.
