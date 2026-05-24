# Final Experiment Plan

Date: 2026-05-24

## Go/No-Go Judgment

Current judgment: go, with caution.

The direction is worth continuing because the visible Colab/T4 readout showed
the right pattern for a publishable modest paper: clean S1/S2 fusion performs
well, synthetic Sentinel-2 degradation exposes a reliability boundary, and the
lightweight modality-dropout baseline improves all tested degraded conditions
with only a small clean-condition penalty.

This is not yet a final manuscript result. It is enough to justify running the
final matrix.

## Final Claim to Test

Standard clean-split multimodal flood mapping can overstate practical
reliability when optical Sentinel-2 inputs are missing or degraded. A lightweight
training-time modality-dropout strategy improves degraded-condition robustness
without substantially sacrificing clean-condition performance.

## Required Evidence

The manuscript route remains strong if the final matrix shows:

1. Positive mean IoU/F1 gain from modality dropout under most or all degraded
   Sentinel-2 conditions.
2. Clean-condition IoU loss no worse than about 0.05.
3. Repeated-seed variance that does not erase the robustness trend.
4. Qualitative panels where robust predictions visibly remain more coherent
   under missing/noisy/patch-masked Sentinel-2 inputs.

The route becomes weak if:

1. Multi-seed results show inconsistent degraded-condition gains.
2. Clean-condition performance collapses.
3. Qualitative maps reveal that both models fail in the same way.
4. The effect depends on only one seed or one degradation type.

## Execution

Run on Colab/T4 or Kaggle GPU:

```bash
bash scripts/run_ombria_final_matrix.sh
```

The script trains clean and modality-dropout multimodal checkpoints for seeds
`7`, `13`, and `21`, evaluates each checkpoint under the same Sentinel-2
degradation modes, writes summary tables, plots the robustness curve, exports
qualitative panels, and packages final artifacts into a zip.

## Discussion Start Point

If the final matrix keeps the pilot pattern, start the paper around this
structure:

1. Introduction: flood mapping needs robust multimodal evaluation, not only
   clean benchmark accuracy.
2. Related work: OMBRIA/OmbriaNet, SAR-optical flood mapping, incomplete
   multimodal remote sensing.
3. Method: controlled Sentinel-2 degradation and lightweight modality dropout.
4. Results: clean accuracy, degradation sensitivity, robustness tradeoff,
   qualitative panels.
5. Limitations: synthetic degradation, small dataset, no claim of operational
   cloud detection.
