# GeoAI Project Context

## Canonical Project

- Local path: `/Users/rudy/Documents/Codex/2026-05-20-geoai`
- GitHub remote: `git@github.com:NewRudy/2026-05-20-geoai.git`
- Main branch: `main`
- Purpose: fast, reproducible GeoAI manuscript work using public data, public models, and auditable experiment logs.

## Current Working Direction

The active route is the OMBRIA flood-mapping pilot:

- Dataset/code base: public OMBRIA repository, mounted locally or cloned under ignored `external/OMBRIA`.
- Core question: whether multitemporal Sentinel-1/Sentinel-2 fusion remains robust when Sentinel-2 optical inputs are degraded at inference time.
- Current claim framing: clean S1/S2 fusion can improve benchmark flood mapping, but its advantage may be sensitive to optical modality availability.
- Near-term goal: complete cloud U-Net pilot runs, evaluate S2 degradation modes, and decide manuscript go/no-go from logged metrics.

## Latest Pilot Signal

The first Colab/T4 pilot completed one short run set with 9 summary records:

- Clean multimodal was the strongest visible run, with test IoU around 0.633 and F1 around 0.765.
- Synthetic S2 degradation caused systematic drops: patch masking was milder, while noise, zero-after, and zero-all were substantially worse.
- This supports continuing the direction as a robustness/sensitivity paper, not as a new state-of-the-art flood mapper.

The next minimal contribution is to train one additional multimodal checkpoint using `--train-degrade-s2 modality_dropout` and compare clean-vs-degraded performance against the standard clean-trained multimodal checkpoint.

Earlier planning also considered Sen1Floods11 and foundation-model PEFT. Keep those notes as fallback or expansion material, but do not treat them as the active route unless the project direction is changed explicitly.

## Important Files

- `README.md`: high-level repository overview and guardrails.
- `docs/00_direction.md`: earlier direction decision around Sen1Floods11/foundation-model adaptation.
- `docs/04_open_source_direction_survey.md`: open-source direction survey.
- `docs/05_ombria_pilot.md`: OMBRIA pilot notes.
- `docs/06_cloud_pilot_commands.md`: Colab/Kaggle run commands.
- `docs/08_feasibility_decision.md`: current OMBRIA feasibility decision.
- `notebooks/ombria_cloud_pilot.ipynb`: cloud pilot notebook.
- `scripts/train_ombria_unet.py`: main OMBRIA U-Net training/evaluation script.
- `scripts/run_ombria_cloud_pilot.sh`: one-command cloud pilot runner.

## Guardrails

- Do not fabricate data, experiments, citations, or results.
- Do not report a metric unless it is backed by committed code/configs and an auditable log or table.
- Do not commit downloaded datasets, checkpoints, private keys, tokens, cloud credentials, or large raw outputs.
- Treat journal rankings, indexing, and venue details as time-sensitive and verify them immediately before submission.

## Next Tasks

- Run the modality-dropout robust multimodal baseline from `docs/06_cloud_pilot_commands.md`.
- Export or copy back `results/tables/ombria_run_summary.csv` and `results/tables/ombria_results_table.md` from Colab.
- Decide whether results support the OMBRIA manuscript route.
- If continuing, add qualitative maps and per-chip failure analysis.
- If not, switch to a smaller fallback or return to the Sen1Floods11/foundation-model route.
