# Colab Robustness Readout

Date: 2026-05-24

## Status

The Colab/T4 notebook completed the clean OMBRIA pilot and the additional
modality-dropout robustness baseline. The visible notebook output reported:

- `wrote 14 records to results/tables/ombria_run_summary.csv`
- clean single-modality and multimodal baselines
- clean-trained multimodal degradation evaluations
- modality-dropout-trained multimodal degradation evaluations

The exact CSV artifact still needs to be exported from the Colab runtime into
this repository. The values below are rounded from the visible Colab fullscreen
output and should be treated as readout evidence, not the final committed result
table.

## Key Multimodal Comparison

| Test S2 condition | Clean-trained IoU | Robust-trained IoU | Delta IoU | Clean-trained F1 | Robust-trained F1 | Delta F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| none | 0.631 | 0.606 | -0.025 | 0.763 | 0.744 | -0.019 |
| patch_after | 0.502 | 0.538 | +0.035 | 0.648 | 0.691 | +0.043 |
| noise_after | 0.308 | 0.384 | +0.076 | 0.467 | 0.548 | +0.081 |
| zero_after | 0.398 | 0.416 | +0.018 | 0.544 | 0.581 | +0.037 |
| zero_all | 0.211 | 0.335 | +0.123 | 0.321 | 0.476 | +0.155 |

## Interpretation

The direction is viable. The clean-trained multimodal model performs best under
clean S1/S2 inputs, but it is brittle when the S2 optical channels are degraded.
The lightweight modality-dropout training baseline sacrifices only a small
amount of clean performance while improving every tested degradation condition.

This supports a modest but defensible paper claim:

> Standard clean-split S1/S2 fusion overstates reliability under degraded or
> missing optical observations; lightweight modality-dropout training improves
> degradation robustness with limited clean-accuracy cost.

## Decision

Continue the OMBRIA route.

This is stronger than a pure stress-test paper because the project now has a
method-extension baseline. It is still not a full manuscript result set until
the following are completed:

1. Export the exact `ombria_run_summary.csv` and `ombria_results_table.md` from
   Colab.
2. Repeat the pilot with at least three seeds.
3. Run a longer final setting, likely 20-30 epochs with the same small U-Net, if
   Colab runtime permits.
4. Add qualitative flood-map examples for clean, degraded, and robust-trained
   predictions.
5. Fix all result metadata so eval-only degradation rows inherit the actual
   checkpoint training settings.
