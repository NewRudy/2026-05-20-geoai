# Google Cloud Workflow

This plan keeps expensive work in Google services and local work focused on
code, small validations, writing, and result checks.

## Preferred Compute Path

1. Google Cloud Storage hosts/mirrors the dataset.
2. Colab Pro or a Google Cloud GPU VM runs training.
3. Experiment configs are committed in Git.
4. Raw logs/checkpoints stay in cloud storage.
5. Curated tables/figures and small metadata summaries are committed locally.

## Data

Primary source:

```text
gs://sen1floods11/
```

Local mirror command, if `gsutil` is available:

```bash
gsutil -m rsync -r gs://sen1floods11 data/raw/sen1floods11
```

Do not commit downloaded data.

## Credentials

Do not commit:

- Google service account JSON files.
- Earth Engine credentials.
- `application_default_credentials.json`.
- Any API token or private key.

For Earth Engine, use:

```python
import ee
ee.Authenticate()
ee.Initialize(project="YOUR_GCP_PROJECT")
```

For unattended jobs, use a service account registered for Earth Engine.

## Experiment Logging

Each run should produce:

- Config file path and git commit hash.
- Dataset version/source.
- Train/validation/test split identifiers.
- Model checkpoint identifier.
- GPU type, wall time, peak memory if available.
- Metrics: IoU, F1/Dice, precision, recall, per-event metrics.
- Qualitative output maps for a fixed set of test chips.

## Local Verification

Local Mac should be used for:

- Linting and unit tests.
- Dataset manifest sanity checks.
- Reading metrics CSV files.
- Generating final tables and figures.
- Building the LaTeX manuscript.

