# OMBRIA Experiment Protocol

Date: 2026-05-21

## Research Question

How sensitive are multitemporal Sentinel-1/Sentinel-2 flood mapping models to
sensor modality availability and degradation?

This is intentionally narrower than "global flood mapping" or "cloud-robust
operational disaster response." The goal is to quantify whether fusion models
remain reliable when optical inputs are missing or degraded, using the compact
public OMBRIA dataset.

## Literature Rationale

The original OmbriaNet paper introduced a CNN-based multitemporal Sentinel-1 and
Sentinel-2 fusion architecture for supervised flood mapping. Its results support
the value of multi-temporal and multi-modal inputs under the original benchmark
split.

Recent flood-mapping work gives the robustness motivation. Cross-modal
distillation studies note that Sentinel-2 can provide richer optical water
signals but cannot penetrate cloud cover, while Sentinel-1 SAR can image through
clouds and is therefore useful during flood events. Remote-sensing multimodal
learning work also warns that models trained with complete modalities can
degrade when modalities are incomplete during inference.

This makes the proposed extension scientifically narrower and defensible:
evaluate whether the OMBRIA fusion advantage survives controlled missing or
degraded Sentinel-2 inputs.

## Hypotheses

H1. Multitemporal inputs improve flood segmentation over after-event-only inputs
under clean test conditions.

H2. Sentinel-1 models are less accurate than clean Sentinel-2 or multimodal
models in some cases, but are less sensitive to optical degradation because they
do not depend on Sentinel-2.

H3. A multimodal model trained on clean S1/S2 inputs loses performance when
Sentinel-2 after-event input is zeroed, noised, or patch-masked at inference
time.

H4. The performance gap between clean and degraded multimodal inference is
larger for chips with higher flood fraction or visually heterogeneous scenes.

## Data

Primary data:

- OMBRIA processed PNG dataset from `geodrak/OMBRIA`.
- 624 training chips and 70 test chips for both S1 and S2.
- Each chip has before, after, and binary flood mask images.

Optional stress-test data:

- `2021/ALBANIA`, `2021/FRANCE`, `2021/GUYANA`, `2021/TIMOR` folders.
- These are small country-organized samples and should be used only as
  qualitative or supplementary checks unless a rigorous split can be documented.

## Models

Pilot baseline:

- Small U-Net implemented in `scripts/train_ombria_unet.py`.

Method-extension baseline:

- The same multimodal U-Net trained with `--train-degrade-s2 modality_dropout`.
- Each training sample is randomly left clean or given zeroed, noisy, or
  patch-masked S2 inputs while S1 remains available.
- This is intentionally lightweight: it tests whether a simple training-time
  modality stressor improves inference-time robustness without introducing a
  large architecture or a new dataset.

Input variants:

- `s1_after`: S1 after-event only, 1 channel.
- `s1_bitemporal`: S1 before + after, 2 channels.
- `s2_after`: S2 after-event only, 3 channels.
- `s2_bitemporal`: S2 before + after, 6 channels.
- `multimodal`: S2 before + after + S1 before + after, 8 channels.

This is not a faithful OmbriaNet reproduction yet. It is a controlled, modern
baseline for deciding whether the manuscript direction has a measurable signal.

## Degradation Tests

Train the multimodal model with clean inputs. Reuse the same checkpoint and
evaluate on:

- `none`: clean test input.
- `zero_after`: S2 after-event image is set to zero.
- `zero_all`: S2 before and after are set to zero.
- `noise_after`: S2 after-event image is random noise.
- `patch_after`: S2 after-event image has repeated zero patches.

Interpretation:

- These tests measure sensitivity to synthetic optical degradation.
- They do not prove real cloud robustness without cloud masks or external cloudy
  events.

## Metrics

Primary:

- Water/flood IoU.
- F1/Dice.

Secondary:

- Precision.
- Recall.
- Pixel accuracy.
- Training time.
- Number of trainable parameters.

Reporting rule:

- Mean metrics are acceptable for pilot decisions.
- Manuscript metrics should include per-chip distributions and confidence
  intervals or repeated seeds if runtime allows.

## Minimum Viable Evidence

The direction is viable if:

1. All five clean input variants run on free Colab/Kaggle without repeated
   runtime failure.
2. Clean multimodal or bitemporal models improve over at least one corresponding
   after-only model by a meaningful margin.
3. Inference-time S2 degradation causes a consistent and interpretable change in
   multimodal performance.
4. Results can be regenerated from committed configs and logs.
5. The modality-dropout multimodal baseline improves degraded-mode performance
   without destroying clean performance.

The direction is weak if:

1. Training is unstable even for the small U-Net.
2. Metrics are indistinguishable across input variants and degradation modes.
3. The result is merely "multimodal is slightly better" with no robustness or
   sensitivity insight.
4. The old OMBRIA split prevents defensible scientific interpretation.

## One-Week Pilot Schedule

Day 1:

- Confirm data loading, train/test split, and minimal training run.

Day 2:

- Run clean input variants with short epochs.

Day 3:

- Run multimodal checkpoint degradation evaluation.

Day 4:

- Aggregate metrics and plot clean vs degraded performance.

Day 5:

- Decide go/no-go for manuscript.

Day 6-7 if go:

- Run repeated seeds or longer training.
- Draft methods and results.
