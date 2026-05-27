# SAR Anchor Tuning Readout

Date: 2026-05-27

## Current Result

The seed-7 Colab weight-ablation run completed successfully. It initially
selected `sar_anchor_severe_w020`, but the later seed-13 and seed-21 validation
showed that `w020` is not stable enough to be the manuscript method without
further tuning.

The current accumulated Colab summary after running `w020` and `w025` on seeds
7, 13, and 21 is:

| Training | Clean IoU | Clean delta | Mean degraded IoU | Worst degraded IoU | Zero-all IoU | S1 IoU | Zero-all gap vs S1 |
|---|---:|---:|---:|---:|---:|---:|---:|
| none | 0.6798 | 0.0000 | 0.4471 | 0.0049 | 0.0790 | 0.4372 | -0.3582 |
| modality_dropout_light | 0.6459 | -0.0339 | 0.5024 | 0.2986 | 0.3547 | 0.4372 | -0.0824 |
| sar_anchor_severe_w010 | 0.6607 | -0.0191 | 0.5174 | 0.3428 | 0.3428 | 0.4372 | -0.0943 |
| sar_anchor_severe_w020 | 0.6513 | -0.0284 | 0.5134 | 0.3429 | 0.3749 | 0.4372 | -0.0623 |
| sar_anchor_severe_w025 | 0.6602 | -0.0196 | 0.5245 | 0.3690 | 0.3791 | 0.4372 | -0.0581 |

Important caveat: `w010` in this accumulated table is still seed-7-only and
should not be compared as a multi-seed method. The main fair comparison is
between `none`, `modality_dropout_light`, `w020`, and `w025`.

## Interpretation

This is a meaningful result, but not yet a manuscript-ready claim.

The positive signal is still real: `w025` improves mean degraded IoU, worst
degraded IoU, and all-S2-missing IoU over ordinary modality dropout while
keeping the clean-IoU penalty just inside the `-0.02` decision threshold.

The limitation is also clear. `w025` is only a borderline pass, not a strong
manuscript result: the zero-all score remains below the SAR-only fallback, and
the gains over `modality_dropout_light` are useful but modest. This should not
be written as a final SCI method yet.

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

Run a small quality-gated SAR-anchor pilot:

```bash
EPOCHS=25 BATCH_SIZE=8 BASE_CHANNELS=16 SEEDS="7" \
bash scripts/run_ombria_quality_anchor_matrix.sh
```

This tests whether explicit Sentinel-2 quality channels can make the SAR-anchor
idea more defensible. The desired story is: the quality map tells the fusion
model where optical observations are unreliable, while the SAR anchor guides
the prediction toward the SAR-only fallback under severe optical failure.

## Decision Rule

Proceed to manuscript-oriented result preparation only if the selected method
satisfies these
criteria across multiple seeds:

- clean IoU delta no worse than about `-0.02`;
- mean degraded IoU above `modality_dropout_light`;
- worst degraded IoU at least close to or above `0.38`;
- cloud and noise degradation rows improve over both clean training and light
  modality dropout;
- no obvious collapse under `zero_after` or `zero_all`.

If the quality-gated anchor pilot does not clearly beat both
`modality_dropout_light` and quality-only dropout, do not draft the manuscript
around this method. Pivot to a narrower robustness-audit paper or a different
idea.
