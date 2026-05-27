# SCI Direction Plan

Date: 2026-05-25

## Working Expert Prompt

Act as a remote-sensing and GeoAI reviewer designing a modest but credible SCI
paper from a small-compute OMBRIA flood-mapping project. The paper must be
incremental enough to implement on Colab, but rigorous enough that its claim is
not just "we tried data augmentation." Prioritize controlled comparisons,
missing-modality robustness, and honest limits. Do not claim broad cloud or
noise robustness unless the evidence supports it.

## Current Readout

The earlier three-seed Colab follow-up supported one narrow result:

- `modality_dropout_light` improves all tested degraded Sentinel-2 settings.
- The largest gain is all-S2-missing (`zero_all`), where clean multimodal
  fusion collapses and light dropout recovers much of the lost performance.
- The gains for `patch_after` and `noise_after` are small, so the current claim
  is not broad optical-corruption robustness.
- `modality_dropout_balanced` is not consistent enough to be the main method.

The newer seed-7 SAR-anchor pilot is more promising: `sar_anchor_severe_w020`
kept clean IoU almost unchanged while improving mean degraded IoU, worst
degraded IoU, and `zero_all` beyond `modality_dropout_light`. See
`docs/15_anchor_tuning_readout.md`.

This is still not yet strong enough as a finished SCI contribution. It is a
promising direction, but the paper needs weight ablation and multi-seed
validation before manuscript drafting.

## Revised Paper Story

Tentative title:

> Degradation-aware Sentinel-1/Sentinel-2 fusion for robust flood mapping under
> missing or unreliable optical observations

Core claim:

> Standard S1/S2 fusion can overstate robustness when optical observations are
> clean in benchmark training and testing. A lightweight degradation-aware
> fusion strategy can preserve clean performance while reducing failure under
> missing or cloud-like Sentinel-2 inputs.

This should be framed as a reliability study plus a small method, not as a
large new architecture.

## Method Upgrade

The current main candidate is `sar_anchor_severe`.

It trains a multimodal U-Net under severe synthetic Sentinel-2 degradation and
adds a SAR-anchor consistency loss against a frozen `s1_bitemporal` model when
optical inputs become unreliable. This makes the claim narrower and more
defensible than ordinary modality dropout:

> A multimodal flood mapper should retain clean S1/S2 performance while
> degrading toward the SAR-only fallback as optical reliability collapses.

The alternative method `quality_dropout_light` remains a backup if the
SAR-anchor weight ablation or multi-seed validation fails.

## Backup Method

It adds two Sentinel-2 quality channels to the existing multimodal U-Net:

- before-event S2 reliability
- after-event S2 reliability

The quality channels are `1` where S2 is available/trusted and `0` where S2 is
missing or masked. For cloud-like and patch-like masks, the after-event quality
channel is spatial, so the model can learn where to rely more on Sentinel-1.

Training still uses a lightweight degradation schedule, but it now includes
cloud-like masks:

- clean samples
- after-event S2 missing
- all S2 missing
- noisy after-event S2
- patch-masked after-event S2
- cloud-like 30 percent after-event masking
- cloud-like 50 percent after-event masking

## Required Next Experiments

The seed-7 SAR-anchor weight ablation selected `sar_anchor_severe_w020` as the
current best setting. Next run it on additional seeds:

```bash
EPOCHS=25 BATCH_SIZE=8 BASE_CHANNELS=16 SEEDS="13 21" \
ANCHOR_MODES="sar_anchor_severe_w020" \
bash scripts/run_ombria_anchor_tuning_matrix.sh
```

If seed `13` and seed `21` preserve the seed-7 trend, proceed to
manuscript-oriented figures, qualitative panels, and LaTeX drafting.

If the anchor route fails, run `scripts/run_ombria_sci_matrix.sh` for the
quality-channel backup.

Backup default settings:

```bash
EPOCHS=25 BATCH_SIZE=8 BASE_CHANNELS=16 SEEDS="7 13 21" \
bash scripts/run_ombria_sci_matrix.sh
```

The matrix trains:

1. `s1_bitemporal`: strong SAR-only fallback baseline.
2. `multimodal` clean training: standard S1/S2 fusion baseline.
3. `multimodal + modality_dropout_light`: current best augmentation baseline.
4. `multimodal + binary S2 quality + quality_dropout_light`: proposed method.

The matrix evaluates multimodal checkpoints under:

- clean
- patch-like after-event masking
- cloud-like after-event masking at 10, 30, 50, and 70 percent
- after-event S2 missing
- all S2 missing
- noisy after-event S2

## Go/No-Go Criteria

Proceed to manuscript drafting only if the proposed method satisfies most of:

- Clean IoU penalty vs clean multimodal is no worse than about `0.03-0.05`.
- Cloud-like degradation curves degrade more slowly than clean training and
  plain light dropout.
- `zero_all` and `zero_after` remain clearly improved.
- Performance under severe optical loss is comparable to or better than the
  `s1_bitemporal` fallback.
- Gains are consistent across all three seeds, not driven by one seed.

If those criteria fail, the project should pivot from "new method" to a more
modest robustness audit paper, or switch to another idea.
