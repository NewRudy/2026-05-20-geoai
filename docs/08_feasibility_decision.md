# Feasibility Decision

Date: 2026-05-21

## Current Decision

Proceed with the OMBRIA route for a robustness-focused cloud U-Net pilot.

This is not yet a full manuscript go decision. It is a go decision for the next
experimental stage because the data, code path, literature rationale, and
sanity-check signal are all present.

## Evidence Collected

Data:

- OMBRIA repository cloned successfully.
- Local size is approximately 392 MB.
- Processed split contains 624 train and 70 test chips for both S1 and S2.
- Image/mask pairing is valid.

Original reference results:

- Extracted from `Evaluation.ipynb`.
- Multimodal reference IoU mean: 0.8207.
- Bitemporal reference IoU mean: 0.7765.
- SVM reference IoU mean: 0.6245.
- S2 U-Net reference IoU mean: 0.5791.
- S1 U-Net reference IoU mean: 0.5507.

Local sanity baselines:

- Otsu sanity baseline confirmed mask/image alignment.
- A lightweight pixel-level ridge baseline showed the expected signal:
  multimodal clean inputs outperform single-modality inputs, while synthetic S2
  degradation reduces multimodal performance.
- These are not manuscript results because they are simplistic and one local run
  produced numerical warnings. They are only route-validation evidence.

Cloud pilot signal:

- A Colab/T4 short run completed the five clean input variants and multimodal S2
  degradation evaluations.
- The visible summary showed clean multimodal as the strongest run and a
  systematic performance drop under synthetic S2 degradation.
- This is enough to continue the route, but not yet enough for manuscript
  results because the exact CSV/log artifacts still need to be copied back and
  committed as curated tables.

Literature rationale:

- OmbriaNet provides the base supervised S1/S2 flood mapping paper.
- Cross-modal flood mapping literature supports the claim that S2 optical data is
  useful but limited by clouds during floods, while S1 SAR can image through
  clouds.
- Incomplete multimodal remote-sensing literature supports testing models under
  missing or degraded modalities.

## Scientific Claim That Can Stand

Potential manuscript claim:

> Multitemporal S1/S2 fusion improves flood mapping under clean benchmark
> conditions, but the advantage is sensitive to optical modality availability;
> controlled inference-time degradation reveals a reliability boundary that is
> not captured by standard clean-split evaluation.

This is modest but defensible.

## What Must Still Be Proven

Before writing the results section:

1. Cloud U-Net runs must complete for all five clean input variants.
2. A clean multimodal checkpoint must be evaluated under S2 degradation without
   retraining.
3. Metrics must be saved from committed scripts and fixed configs.
4. At least one figure/table must show a consistent clean-vs-degraded pattern.
5. A lightweight modality-dropout multimodal checkpoint should be evaluated as a
   robustness baseline.

## Current Blockers

GitHub:

- SSH authentication works for `NewRudy`.
- `NewRudy/2026-05-20-geoai` exists and `main` has been pushed.
- Current `origin` is `git@github.com:NewRudy/2026-05-20-geoai.git`.

Cloud execution:

- No direct Colab/Kaggle execution API is available in the current tool context.
- Browser automation is not currently exposed enough to run Colab unattended.
- A ready-to-run notebook exists at `notebooks/ombria_cloud_pilot.ipynb`.

## If Cloud U-Net Fails

Switch to one of these smaller fallback routes:

1. Keep OMBRIA but use classical/linear models plus OmbriaNet reference analysis,
   framing as a short methodological note rather than a full DL paper.
2. Switch to FLOODPY/FLOMPY and write a Sentinel-1 SAR flood mapping case-study
   paper, accepting more preprocessing complexity.
3. Return to Sen1Floods11 only if paid/guaranteed GPU becomes available.
