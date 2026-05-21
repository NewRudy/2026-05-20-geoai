# Fast GeoAI SCI Paper Project

This repository is for a fast, reproducible GeoAI manuscript based on public
data, public models, and auditable experiment logs.

## Working Direction

Tentative title:

> Parameter-efficient adaptation of geospatial foundation models for flood
> inundation mapping under spatial distribution shift

Core idea: use Sen1Floods11 as a public benchmark, compare conventional
segmentation baselines against Prithvi/TerraTorch-style geospatial foundation
model adaptation, and evaluate whether parameter-efficient tuning improves
cross-region flood mapping with lower compute.

## Why This Direction

- Fast: Sen1Floods11 is public and hosted on Google Cloud Storage.
- Rigorous: the data, splits, model checkpoints, metrics, and logs can be made
  reproducible.
- Current: GeoAI foundation models, PEFT, cross-region transfer, and responsible
  GeoAI are active 2025-2026 topics.
- Publishable: the likely paper contribution is not "new big model"; it is a
  careful, reproducible, resource-aware adaptation study.

## Initial Milestones

1. Confirm target journal and paper scope.
2. Mirror/index Sen1Floods11 from GCS.
3. Establish baselines: simple threshold, U-Net, SegFormer/ViT baseline.
4. Add geospatial foundation model adaptation: Prithvi-EO and/or TerraTorch.
5. Run low-data and cross-event/cross-region experiments.
6. Add responsible GeoAI checks: spatial failure modes, uncertainty/error maps,
   and compute/memory reporting.
7. Write the manuscript in LaTeX with a tracked BibTeX file.
8. Push code, configs, logs, and non-sensitive results to GitHub.

## Repository Layout

- `docs/`: research decisions, latest-practice notes, journal targets, cloud plan.
- `references/`: seed BibTeX and citation notes.
- `paper/`: LaTeX manuscript skeleton.
- `configs/`: experiment configuration drafts.
- `scripts/`: reproducibility utilities.
- `src/geoai_quickpaper/`: local Python package.
- `data/`: ignored data mount/download area.
- `results/`: ignored raw outputs except curated tables/figures.

## Guardrails

- Do not fabricate data, experiments, citations, or results.
- Do not report any metric unless it is backed by a committed config and log.
- Do not commit private keys, Google credentials, tokens, downloaded datasets,
  or large model checkpoints.
- Treat journal quartile and indexing information as time-sensitive; verify
  again immediately before submission.

