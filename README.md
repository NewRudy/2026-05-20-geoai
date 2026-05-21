# Fast GeoAI SCI Paper Project

This repository is for a fast, reproducible GeoAI manuscript based on public
data, public models, and auditable experiment logs.

## Working Direction

Tentative title:

> How Robust Is Multitemporal Sentinel-1/Sentinel-2 Fusion for Flood Mapping
> under Optical Modality Degradation?

Core idea: build on the public OMBRIA dataset and OmbriaNet codebase to test
whether the clean-split advantage of multitemporal S1/S2 fusion survives
controlled Sentinel-2 degradation at inference time.

## Why This Direction

- Fast: OMBRIA is public, compact, and already cloned locally under ignored
  `external/OMBRIA`.
- Rigorous: the data, splits, model checkpoints, metrics, and logs can be made
  reproducible.
- Scientifically grounded: flood events often limit optical observations, while
  SAR remains available under cloud cover.
- Publishable if the cloud U-Net pilot confirms a consistent clean-vs-degraded
  sensitivity pattern.

## Initial Milestones

1. Confirm target journal and paper scope.
2. Validate OMBRIA data pairing and reference metrics.
3. Run clean S1/S2/bitemporal/multimodal U-Net variants on cloud GPU.
4. Evaluate the same multimodal checkpoint under S2 degradation.
5. Aggregate metrics and decide manuscript go/no-go.
6. Add qualitative maps and per-chip failure analysis if results are coherent.
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
