# Graceful Degradation Experiment

Date: 2026-05-26

## Revised Claim

The paper should not claim that quality channels or ordinary modality dropout
are novel. The stronger and narrower claim is:

> A flood-mapping S1/S2 fusion model should degrade gracefully as optical
> observations become unreliable, approaching the SAR-only fallback under severe
> S2 loss instead of collapsing.

## Method

The next method is `sar_anchor_light`.

It trains a multimodal U-Net under synthetic S2 degradation, but adds a
SAR-anchor consistency term when the optical input is severely degraded. The
anchor is a frozen `s1_bitemporal` U-Net trained on the same split.

The supervised flood loss remains the main objective. The anchor term is
weighted by degradation severity:

- clean: 0.00
- patch/cloud 30 percent: 0.35
- cloud 50 percent/noise: 0.55
- cloud 70 percent/zero-after: 0.75
- zero-all: 1.00

This keeps the method small enough for Colab while making the claim different
from standard modality dropout.

## Baselines

Run `scripts/run_ombria_graceful_matrix.sh`.

The seed-7 pilot trains:

1. `s1_bitemporal`: SAR-only fallback.
2. clean `multimodal`: standard fusion.
3. `multimodal + modality_dropout_light`: strongest current baseline.
4. `multimodal + sar_anchor_light`: proposed graceful-degradation method.

The test matrix evaluates clean, cloud-like degradation at 10/30/50/70 percent,
patch masking, after-S2 missing, all-S2 missing, and noisy after-S2.

## Decision Rule

Proceed to three seeds only if `sar_anchor_light` satisfies most of:

- clean IoU penalty is no worse than 0.03 to 0.05;
- mean degraded IoU exceeds `modality_dropout_light`;
- worst degraded IoU exceeds `modality_dropout_light`;
- `zero_all` is close to or better than the S1 fallback;
- the cloud degradation curve is smoother than clean fusion and ordinary
  dropout.

If it fails, the project should not continue with this method as the main SCI
contribution.
