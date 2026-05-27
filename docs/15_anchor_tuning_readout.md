# SAR Anchor Tuning Readout

Date: 2026-05-27

## Current Result

The seed-7 Colab run for `sar_anchor_severe_w025` completed successfully.
It is the strongest candidate so far because it preserves clean performance
while improving the degraded Sentinel-2 conditions.

| Training | Clean IoU | Clean delta | Mean degraded IoU | Worst degraded IoU | Zero-all IoU | S1 IoU | Zero-all gap vs S1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| none | 0.6830 | 0.0000 | 0.4392 | 0.1235 | 0.1235 | 0.4081 | -0.2846 |
| modality_dropout_light | 0.6627 | -0.0203 | 0.5052 | 0.3523 | 0.4066 | 0.4081 | -0.0015 |
| sar_anchor_severe_w025 | 0.6781 | -0.0048 | 0.5392 | 0.3884 | 0.3884 | 0.4081 | -0.0197 |

## Interpretation

This is a meaningful result, but not yet a manuscript-ready claim.

The positive signal is that `sar_anchor_severe_w025` improves mean degraded IoU
and worst degraded IoU while nearly matching the clean multimodal baseline.
That is stronger than ordinary modality dropout as a paper story because the
method is not just randomly hiding optical channels; it explicitly encourages
the multimodal model to approach the SAR-only fallback when optical reliability
collapses.

The limitation is that `zero_all` is slightly lower than
`modality_dropout_light`. The best claim should therefore focus on graceful
degradation and clean-performance preservation, not on winning every individual
degradation mode.

## Active Follow-Up

The next Colab run is the weight ablation:

```bash
EPOCHS=25 BATCH_SIZE=8 BASE_CHANNELS=16 SEEDS="7" \
ANCHOR_MODES="sar_anchor_severe_w010 sar_anchor_severe_w020" \
bash scripts/run_ombria_anchor_tuning_matrix.sh
```

This tests whether the `w025` result is a stable SAR-anchor effect or an
overweighted single setting.

## Decision Rule

Proceed to multi-seed validation if one of the anchor settings satisfies:

- clean IoU delta no worse than about `-0.02`;
- mean degraded IoU above `modality_dropout_light`;
- worst degraded IoU at least close to or above `0.38`;
- cloud and noise degradation rows improve over both clean training and light
  modality dropout;
- no obvious collapse under `zero_after` or `zero_all`.

If `w010` or `w020` matches `w025` with better `zero_all`, prefer it for the
main method. If only `w025` works, keep `w025` but describe the anchor strength
as a tuned hyperparameter and verify it across seeds before manuscript writing.
