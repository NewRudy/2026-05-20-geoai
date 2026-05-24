# Final Experiment Plan

Date: 2026-05-24

## Go/No-Go Judgment

Current judgment: borderline go, continue with a focused follow-up.

The direction is worth continuing because the Colab/T4 final matrix shows a
real robustness signal under missing or corrupted Sentinel-2 inputs. However,
the result is not clean enough to support a broad claim that the current
modality-dropout baseline improves every optical-degradation case.

The manuscript route should be narrowed to a robustness tradeoff paper:
training-time S2 degradation improves missing/corrupted-S2 robustness, but it
can reduce clean-condition performance and does not automatically solve local
patch occlusion.

## Final Claim to Test

Standard clean-split multimodal flood mapping can overstate practical
reliability when optical Sentinel-2 inputs are missing or degraded. Lightweight
training-time S2 degradation can improve robustness to missing/corrupted optical
inputs, with a measurable tradeoff against clean optical performance.

Do not claim universal robustness across all optical degradation types unless a
follow-up run fixes the patch-masking failure case.

## Required Evidence

The manuscript route remains strong if the follow-up matrix shows:

1. Positive mean IoU/F1 gain under missing and noisy Sentinel-2 conditions.
2. Clean-condition IoU loss no worse than about 0.05.
3. Repeated-seed variance that does not erase the robustness trend.
4. Qualitative panels where robust predictions remain more coherent under
   missing or noisy Sentinel-2 inputs.

The route becomes weak if:

1. Multi-seed results show inconsistent degraded-condition gains.
2. Clean-condition performance collapses.
3. Qualitative maps reveal that both models fail in the same way.
4. The effect depends on only one seed or one degradation type.

## Execution

The final matrix has been run on Colab/T4:

```bash
bash scripts/run_ombria_final_matrix.sh
```

Key result:

- `zero_all`: IoU gain `+0.2698`, F1 gain `+0.3728`
- `noise_after`: IoU gain `+0.0780`, F1 gain `+0.0888`
- `zero_after`: IoU gain `+0.0331`, F1 gain `+0.0394`
- `patch_after`: IoU change `-0.0106`, F1 change `-0.0049`
- clean condition: IoU change `-0.0552`, F1 change `-0.0418`

The follow-up run should test two small schedule variants:

```bash
bash scripts/run_ombria_followup_matrix.sh
```

`modality_dropout_light` lowers the total S2 degradation rate to reduce clean
performance loss. `modality_dropout_patch` slightly raises the patch-masking
rate to test whether the patch failure is a training-schedule issue.

## Discussion Start Point

If the follow-up matrix keeps the missing/corrupted-S2 gains and reduces the
clean penalty or patch failure, start the paper around this structure:

1. Introduction: flood mapping needs robust multimodal evaluation, not only
   clean benchmark accuracy.
2. Related work: OMBRIA/OmbriaNet, SAR-optical flood mapping, incomplete
   multimodal remote sensing.
3. Method: controlled Sentinel-2 degradation and lightweight modality dropout.
4. Results: clean accuracy, degradation sensitivity, robustness tradeoff,
   qualitative panels.
5. Limitations: synthetic degradation, small dataset, no claim of operational
   cloud detection.
