# Feasibility Decision

Date: 2026-05-24

## Current Decision

Proceed with the OMBRIA route, but keep the claim narrow.

This is a borderline-go decision rather than a clean final-results decision.
The Colab/T4 multi-seed matrix shows a strong signal for missing/corrupted S2
robustness, but also shows a clean-condition penalty and a slight patch-masking
failure. The project remains worth continuing because the failure is specific,
diagnosable, and can be tested with a small follow-up schedule ablation.

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
- A final Colab/T4 matrix completed clean and modality-dropout multimodal
  checkpoints for seeds `7`, `13`, and `21`.
- The artifacts were copied back into `results/tables` and `results/figures`.
- Modality dropout strongly improves all-S2-missing evaluation (`zero_all`:
  IoU `+0.2698`, F1 `+0.3728`) and improves noisy S2 evaluation
  (`noise_after`: IoU `+0.0780`, F1 `+0.0888`).
- The same strategy slightly hurts patch-masked S2 evaluation
  (`patch_after`: IoU `-0.0106`, F1 `-0.0049`) and reduces clean IoU by
  `0.0552`.
- This supports a robustness-tradeoff paper, not a universal robustness claim.

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

More precise current claim:

> Lightweight S2 degradation during training improves OMBRIA flood mapping
> robustness when optical inputs are absent or corrupted, but the benefit is
> degradation-specific and trades off against clean optical performance.

## What Must Still Be Proven

Before writing the results section:

1. Inspect the qualitative panels for the patch-masking failure.
2. Run `scripts/run_ombria_followup_matrix.sh` to test lighter dropout and
   patch-aware dropout schedules.
3. Confirm whether either schedule reduces the clean IoU penalty below about
   `0.05` while preserving missing/noisy-S2 gains.
4. Only then freeze the method section and start the results narrative.

## Current Blockers

GitHub:

- SSH authentication works for `NewRudy`.
- `NewRudy/2026-05-20-geoai` exists and `main` has been pushed.
- Current `origin` is `git@github.com:NewRudy/2026-05-20-geoai.git`.

Cloud execution:

- Colab/T4 execution works for this project.
- The Mac mini is not the right place for the U-Net training loop; keep local
  work to code, tables, figures, and manuscript writing.

## If Cloud U-Net Fails

Switch to one of these smaller fallback routes:

1. Keep OMBRIA but use classical/linear models plus OmbriaNet reference analysis,
   framing as a short methodological note rather than a full DL paper.
2. Switch to FLOODPY/FLOMPY and write a Sentinel-1 SAR flood mapping case-study
   paper, accepting more preprocessing complexity.
3. Return to Sen1Floods11 only if paid/guaranteed GPU becomes available.
