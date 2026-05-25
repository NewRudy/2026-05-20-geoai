# Daily Continuation Plan

Date: 2026-05-25

## Daily Check

At 11:20 America/Los_Angeles each day, check whether there is available
Codex/Colab quota for this project.

If quota is available, continue the GeoAI paper route until the manuscript is
complete. The immediate priority is the OMBRIA follow-up matrix:

```bash
git pull
bash scripts/run_ombria_followup_matrix.sh
```

## Priority Order

1. Run or resume `scripts/run_ombria_followup_matrix.sh` on Colab/T4.
2. Download and import `results/ombria_followup_artifacts.zip`.
3. Check whether `modality_dropout_light` reduces clean IoU loss while keeping
   missing-S2 gains.
4. Check whether `modality_dropout_balanced` keeps the smaller clean penalty
   while recovering the noisy-S2 gain.
5. Check whether `modality_dropout_patch` fixes or improves `patch_after`.
6. Update the feasibility decision and final experiment plan.
7. Once the follow-up is strong enough, freeze the claim and start drafting the
   paper around a robustness-tradeoff contribution.

## Guardrail

Do not claim universal robustness unless the follow-up matrix supports it.
The currently defensible claim is that S2 degradation training improves
missing/corrupted optical-input robustness with a measurable clean-performance
tradeoff.

## Automation Note

The requested recurring task is:

> Every day at 11:20 America/Los_Angeles, check whether there is available
> quota. If quota is available, continue advancing
> `/Users/rudy/Documents/Codex/2026-05-20-geoai` toward a complete SCI paper.

Create this as a Codex automation as soon as the automation tool is available.
