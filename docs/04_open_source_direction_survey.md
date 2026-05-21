# Open-Source Direction Survey

Date: 2026-05-21

Goal: find a direction that can be built on a high-quality open-source paper
repository, modified modestly, and turned into a publishable general SCI paper
without fabricating data or requiring local heavy computation.

## Candidate A: AnyDisasterMapping

Repository:

- https://github.com/ChenHongruixuan/AnyDisasterMapping

Paper:

- Earth Observation for Disaster Mapping: Benchmarks, Methods, Challenges and
  Future Perspectives
- https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6725082

What it provides:

- Unified benchmark/review code for EO disaster mapping.
- Domains include infrastructure damage, flood mapping, landslide segmentation,
  and wildfire analysis.
- Provides training/evaluation pipeline, task handlers, dataset adapters,
  model wrappers, configs, and pretrained weight guidance.
- Model families include SegFormer, HRNet, SAM/SAM2, DINOv3, HyperSigma,
  SkySense, SpectralGPT, and ChangeMamba.

Why it is attractive:

- Very current: 2026 disaster mapping benchmark direction.
- Strong author/institution mix and open code.
- The paper's stated gap is fragmentation of disaster mapping benchmarks and
  inconsistent evaluation, which is a real scientific-methodology gap.
- We could contribute a narrower flood-focused evaluation extension without
  inventing a brand-new model.

Risks:

- Engineering stack is heavy and includes optional CUDA/C++ kernels.
- Full reproduction may exceed free GPU capacity.
- As a broad benchmark repo, a small modification must be carefully scoped to
  avoid looking like a trivial re-run.

Potential publishable angle:

> Event-wise generalization and modality stress-testing for flood mapping within
> a unified EO disaster benchmark.

Minimum modification:

- Use the flood subset/configs only.
- Add leave-one-event-out or cross-dataset evaluation if not already present.
- Add modality ablations: S1-only, S2-only, S1+S2 where supported.
- Add calibrated uncertainty/error stratification by cloud/invalid ratio,
  flood fraction, and event geography.

## Candidate B: ML4Floods / WorldFloods

Repository:

- https://github.com/spaceml-org/ml4floods

Papers:

- Towards global flood mapping onboard low cost satellites with machine learning
  (Scientific Reports, 2021)
- Global flood extent segmentation in optical satellite images (Scientific
  Reports, 2023)

What it provides:

- End-to-end flood extent estimation pipeline.
- WorldFloodsV2 dataset, pretrained models, docs, and Colab tutorials.
- Pipeline covers preprocessing, training, evaluation, deployment, and
  visualization.

Why it is attractive:

- Mature flood-specific codebase.
- Strong paper trail and operational framing.
- Scientific Reports papers are conventional, understandable targets for a
  general flood-mapping paper.

Risks:

- WorldFloods dataset is approximately 76GB, too large for a free-cloud-first
  workflow.
- Optical-only framing may be weaker for all-weather disaster mapping.
- Existing work already covers global dataset extension and robust validation.

Potential publishable angle:

> Lightweight cross-dataset validation of WorldFloods-trained models on
> Sen1Floods11 or other public flood datasets.

Minimum modification:

- Do not download full WorldFloods locally.
- Use pretrained WorldFloods model for inference on a smaller external dataset.
- Evaluate cross-dataset degradation and failure modes.

## Candidate C: TerraTorch / PEFT-GeoFM / Prithvi-EO

Repositories:

- https://github.com/torchgeo/terratorch
- https://github.com/IBM/peft-geofm
- https://github.com/NASA-IMPACT/Prithvi-EO-2.0

What it provides:

- TerraTorch is a current toolkit for fine-tuning geospatial foundation models.
- PEFT-GeoFM provides LoRA, VPT, and ViT-Adapter experiments with GeoFMs.
- Prithvi-EO-2.0 provides sample configs for flood detection, wildfire scars,
  landslides, crops, and biomass.

Why it is attractive:

- Most "GeoAI foundation model" aligned.
- Current and credible.
- Ready-made configs reduce engineering burden.

Risks:

- Compute burden is real even with PEFT.
- Several obvious experiments have already been done by IBM/NASA.
- A small extension must answer a sharply defined scientific question, not just
  rerun configs.

Potential publishable angle:

> When does a geospatial foundation model help flood mapping under event-level
> domain shift?

Minimum modification:

- Compare existing Prithvi/TerraTorch flood config against a lightweight baseline
  under event-holdout splits.
- Avoid full-scale model sweeps.

## Candidate D: GEO-Bench / GEO-Bench-2

Repositories:

- https://github.com/servicenow/geo-bench
- https://github.com/The-AI-Alliance/GEO-Bench-2

What it provides:

- GEO-Bench evaluates pretrained models on Earth monitoring tasks.
- GEO-Bench-2 adds capability-aware evaluation across modalities, temporal
  contexts, and downstream applications.

Why it is attractive:

- Strong benchmark framing.
- Reproducibility and capability evaluation are directly aligned with current
  GeoAI foundation model practice.

Risks:

- Broad benchmark extension is hard to complete quickly.
- Downloading all benchmark datasets is not realistic under free-cloud
  constraints.
- Less flood-specific unless we deliberately select flood/disaster tasks.

Potential publishable angle:

> Capability-aware evaluation of disaster/flood tasks within existing GeoFM
> benchmarks.

## Objective Ranking Under Current Constraints

Criteria:

- Uses high-quality open-source code.
- Supports flood/disaster mapping.
- Can be modified modestly.
- Does not require full local data storage.
- Can produce a credible general SCI paper.

Ranking:

1. AnyDisasterMapping flood-focused extension.
2. ML4Floods pretrained-model external validation.
3. TerraTorch/PEFT-GeoFM event-holdout flood adaptation.
4. GEO-Bench-2 capability benchmark extension.

## Recommended Direction

Use **AnyDisasterMapping** as the base code direction, not the old custom project
as the main experimental codebase.

Working title:

> Event-Level Generalization of Deep Learning Flood Mapping Models in a Unified
> Earth Observation Disaster Benchmark

Scientific question:

> Do flood mapping models that perform well under standard benchmark splits
> remain reliable under event-level domain shift, and which modality/model
> families are most robust?

Why this is stronger than the previous idea:

- It is anchored in a fresh 2026 disaster-mapping benchmark repository.
- The scientific problem is benchmark reliability and event-level generalization,
  not "resource constraints".
- The modification is plausible: add or emphasize event-wise flood evaluation,
  modality ablation, and failure analysis.
- It can still cite Prithvi/TerraTorch/GeoFM as related work, but the paper does
  not depend on expensive foundation-model fine-tuning.

Minimum viable paper:

- Reproduce one or two flood baselines from AnyDisasterMapping.
- Add event-holdout splits for the flood dataset(s).
- Compare one CNN baseline and one transformer/foundation-inspired baseline if
  compute permits.
- Add error stratification by event, flood fraction, invalid/cloud pixels, and
  sensor modality.
- Release configs, split files, metrics, and scripts.

Fallback:

- If AnyDisasterMapping is too heavy, switch to ML4Floods pretrained inference
  and external validation on Sen1Floods11.

