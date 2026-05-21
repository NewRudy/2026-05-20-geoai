# Direction Decision

Date: 2026-05-21

## Selected Direction

Use public flood mapping benchmark data and public geospatial foundation models
to write a reproducible GeoAI paper:

**Parameter-efficient adaptation of geospatial foundation models for flood
inundation mapping under spatial distribution shift.**

## Research Question

Can parameter-efficient adaptation of a geospatial foundation model improve
flood inundation segmentation under cross-event or cross-region distribution
shift, compared with conventional segmentation baselines and full fine-tuning?

## Main Hypotheses

H1. A geospatial foundation model adapted with PEFT can match or exceed common
segmentation baselines on held-out flood events.

H2. PEFT can reduce trainable parameters, memory, and training time while
preserving cross-region performance.

H3. Error patterns will not be spatially uniform; they should be analyzed by
event, region, land-cover/context, and invalid/no-data masks instead of only
global IoU/F1.

## Dataset

Primary dataset: Sen1Floods11.

Reasons:

- Public benchmark for flood inundation mapping.
- Hosted on Google Cloud Storage at `gs://sen1floods11/`.
- Includes Sentinel-1, Sentinel-2, hand labels, metadata, and predefined splits.
- Prior GeoAI foundation model work has used it, which gives us defensible
  baselines and citation anchors.

## Model Stack

Baseline tier:

- Water threshold baseline on Sentinel-1 VH/VV where applicable.
- U-Net or DeepLab-style CNN segmentation.
- SegFormer or ViT-style supervised baseline if compute allows.

Foundation-model tier:

- Prithvi-EO via Hugging Face / NASA-IBM examples.
- TerraTorch if installation and data-module integration are reliable.
- PEFT variants such as linear probing, frozen encoder + decoder, adapters, or
  LoRA if supported by the chosen implementation.

## Minimum Publishable Experiment Set

The first valid manuscript should include:

- One public dataset, with exact version and download procedure.
- At least three baselines.
- At least one foundation-model adaptation.
- Cross-event or cross-region holdout evaluation.
- Low-label experiment, for example 1%, 5%, 10%, 100% training labels.
- Compute cost table: GPU type, wall time, peak memory, trainable parameters.
- Failure-mode analysis with qualitative maps, not just aggregate metrics.

## Novelty Framing

This is not pitched as a new foundation model. The contribution is a
reproducible, resource-aware adaptation and evaluation protocol for practical
GeoAI flood mapping, with an emphasis on spatial transfer and responsible
reporting.

## Risks

- If TerraTorch/Prithvi integration is slow, fall back to frozen embeddings or
  the official Prithvi fine-tuning examples.
- If results do not beat baselines, frame the paper around when foundation-model
  adaptation helps or fails, with rigorous negative findings.
- If the experiment is too narrow for a higher journal, extend to an additional
  public flood dataset or add stronger explainability/uncertainty analysis.

