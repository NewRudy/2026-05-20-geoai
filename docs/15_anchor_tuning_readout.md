# SAR Anchor Tuning Readout

Date: 2026-05-27

## Current Result

The seed-7 Colab weight-ablation run completed successfully. It initially
selected `sar_anchor_severe_w020`, but the later seed-13 and seed-21 validation
showed that `w020` is not stable enough to be the manuscript method without
further tuning.

The current accumulated Colab summary after running `w020` on seeds 7, 13, and
21 is:

| Training | Clean IoU | Clean delta | Mean degraded IoU | Worst degraded IoU | Zero-all IoU | S1 IoU | Zero-all gap vs S1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| none | 0.6798 | 0.0000 | 0.4471 | 0.0049 | 0.0790 | 0.4372 | -0.3582 |
| modality_dropout_light | 0.6459 | -0.0339 | 0.5024 | 0.2986 | 0.3547 | 0.4372 | -0.0824 |
| sar_anchor_severe_w010 | 0.6607 | -0.0191 | 0.5174 | 0.3428 | 0.3428 | 0.4372 | -0.0943 |
| sar_anchor_severe_w020 | 0.6513 | -0.0284 | 0.5134 | 0.3429 | 0.3749 | 0.4372 | -0.0623 |
| sar_anchor_severe_w025 | 0.6781 | -0.0016 | 0.5392 | 0.3884 | 0.3884 | 0.4372 | -0.0488 |

Important caveat: `w025` in this accumulated table is still seed-7-only. It
cannot be claimed as a multi-seed result yet. It is the next candidate to test
because it preserved clean IoU better than `w020` in the available table.

## Interpretation

This is a meaningful result, but not yet a manuscript-ready claim.

The positive signal is still real: SAR anchoring improves mean degraded IoU and
worst degraded IoU over ordinary modality dropout in the accumulated summary.
That is a better paper story than plain random modality dropout because the
method explicitly encourages the multimodal model to approach the SAR-only
fallback when optical reliability collapses.

The limitation is now clearer. `w020` drops clean IoU by about `0.0284` in the
accumulated summary and does not improve enough over `modality_dropout_light`
to be a strong manuscript method. It should not be written up as the final
method unless additional evidence changes this conclusion.

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

Run `sar_anchor_severe_w025` across additional seeds:

```bash
EPOCHS=25 BATCH_SIZE=8 BASE_CHANNELS=16 SEEDS="13 21" \
ANCHOR_MODES="sar_anchor_severe_w025" \
bash scripts/run_ombria_anchor_tuning_matrix.sh
```

This is the current manuscript gate. If `w025` preserves the clean-performance
advantage while keeping degraded IoU above `modality_dropout_light`, the anchor
route remains viable. If it fails, switch to the quality-channel backup instead
of forcing a weak method story.

## Decision Rule

Proceed to manuscript-oriented result preparation if the selected anchor weight
satisfies these
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
