# OMBRIA Pilot Check

Date: 2026-05-21

Purpose: verify whether the OMBRIA-based flood mapping direction is practically
viable before committing to a full manuscript.

## What Was Downloaded

Repository:

- https://github.com/geodrak/OMBRIA

Local path:

- `external/OMBRIA` (ignored by Git)

Downloaded size:

- Approximately 392 MB after shallow clone.

## Data Structure

Processed dataset:

- `OmbriaS1/train`: 624 before/after/mask triplets.
- `OmbriaS1/test`: 70 before/after/mask triplets.
- `OmbriaS2/train`: 624 before/after/mask triplets.
- `OmbriaS2/test`: 70 before/after/mask triplets.
- S1 images are 256 x 256 8-bit grayscale PNGs.
- S2 images are 256 x 256 8-bit RGB PNGs.
- Masks are binary PNGs with matching chip identifiers.

Additional 2021 country-organized samples:

- Albania: 22 triplets per sensor.
- France: 88 triplets per sensor.
- Guyana: 30 triplets per sensor.
- Timor: 10 triplets per sensor.

This gives a possible small regional stress-test set, but it is too small to
support strong claims about global generalization.

## Original Code Condition

The repository includes notebook implementations:

- `Otsu Threshold.ipynb`
- `SVM.ipynb`
- `UNET.ipynb`
- `OmbriaNet.ipynb`
- `Evaluation.ipynb`

Risks:

- Notebook paths are tied to Google Drive.
- Deep learning code uses older Keras/TensorFlow idioms such as
  `fit_generator`, `keras.layers.advanced_activations.LeakyReLU`, and older
  optimizer arguments.
- `Evaluation.ipynb` contains hard-coded prediction arrays and saved results,
  which are useful for reference but are not a reproducible experiment log.

Conclusion: the data are clean enough to use, but the training code should be
converted into modern scripts or fresh Colab notebooks rather than used
unchanged.

## Local Probe

Added local script:

- `scripts/probe_ombria.py`

The probe verifies image pairing and computes simple Otsu-style sanity
baselines. These results are not manuscript results; they only verify the data
pipeline.

Command:

```bash
.venv/bin/python scripts/probe_ombria.py --root external/OMBRIA --out results/tables/ombria_probe.csv
```

Output:

```text
pairs=1388 rows=5552 out=results/tables/ombria_probe.csv
train S1: chips=624 mean_flood_fraction=0.3307
train S2: chips=624 mean_flood_fraction=0.3307
test S1: chips=70 mean_flood_fraction=0.3337
test S2: chips=70 mean_flood_fraction=0.3337
```

Best simple test sanity baseline observed:

- S1 after-image low-Otsu: mean IoU 0.4884, mean F1 0.6161.
- S2 diff low-Otsu: mean IoU 0.3828, mean F1 0.5146.

These numbers show that the masks and imagery are aligned and that trivial
baselines are meaningful but far below the original deep-learning results.

## Original Notebook Result Signal

`Evaluation.ipynb` includes hard-coded per-chip IoU arrays for S1, S2,
bitemporal, multimodal, and SVM predictions. The multimodal IoU values are often
higher than S1/S2-only values, which supports the original paper's claim that
multi-temporal/multi-modal fusion can help. However, those arrays should be
treated as reference material until regenerated from scripts.

Reference extraction script:

- `scripts/extract_ombria_reference_metrics.py`

Extracted from the original evaluation notebook, not regenerated:

| Model | Mean IoU | Mean Accuracy | n |
|---|---:|---:|---:|
| S1 U-Net | 0.5507 | 0.7781 | 70 |
| S2 U-Net | 0.5791 | 0.8412 | 70 |
| SVM | 0.6245 | 0.8487 | 70 |
| Bitemporal | 0.7765 | 0.8608 | 70 |
| Multimodal | 0.8207 | 0.8900 | 70 |

This gives a credible feasibility signal: the original model family has a clear
multimodal advantage on the original test split. Our manuscript should not
reclaim this as a new result. The possible extension is to test whether that
multimodal advantage survives synthetic optical degradation at inference time.

## Scientific Direction Assessment

The broad direction is feasible, but it should be scoped narrowly:

> Sensitivity of multitemporal Sentinel-1/Sentinel-2 flood mapping to sensor
> modality availability and degradation.

Reasonable claims:

- OMBRIA provides a compact, public flood dataset suitable for rapid
  reproducible experiments.
- A controlled ablation can test whether S1, S2, bitemporal, and multimodal
  inputs differ in robustness.
- Simulated optical degradation can test sensitivity to missing or corrupted
  optical inputs, but cannot alone prove real cloud robustness.

Claims to avoid:

- Global generalization.
- Operational disaster readiness.
- A new state-of-the-art model.
- Real cloud robustness unless real cloud metadata or external cloudy events are
  introduced.

## Go / No-Go

Go for a one-week pilot:

1. Convert the U-Net and OmbriaNet notebooks into modern, path-independent
   scripts.
2. Run S1-only, S2-only, bitemporal, and multimodal baselines on free cloud.
3. Add controlled S2 degradation at inference time.
4. Check whether the performance drop is systematic and publishable.

No-go conditions:

- Modernized training cannot reproduce the original model family on Colab/Kaggle.
- Degradation/ablation results are noisy with no interpretable pattern.
- Review of target journals shows the contribution is too incremental without an
  external validation dataset.
