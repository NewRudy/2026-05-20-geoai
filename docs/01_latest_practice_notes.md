# Latest Practice Notes

Date checked: 2026-05-21

## GeoAI Foundation Models

Recent surveys emphasize remote sensing foundation models moving from vision-only
models toward multimodal settings that include optical, radar, LiDAR, text, and
geographic metadata. The common bottlenecks are data alignment, cross-modal
transfer, large annotation needs, compute cost, and scalability.

Source:

- https://arxiv.org/abs/2503.22081

## Prithvi-EO

The Prithvi-EO Hugging Face model card states that Prithvi accepts EO data in
`(B, C, T, H, W)` format and has examples for burn scars, flood mapping, and
multi-temporal crop classification. The model card links to fine-tuning examples
and Sen1Floods11 instructions.

Source:

- https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M

## TerraTorch

TerraTorch is a PyTorch Lightning and TorchGeo-based toolkit for fine-tuning
geospatial foundation models. It supports segmentation/classification/regression
tasks, model factories, CLI/config-driven training, and GEO-Bench integration.
The current GitHub page shows release `v1.2.5` as of 2026-03-23.

Sources:

- https://github.com/torchgeo/terratorch
- https://arxiv.org/abs/2503.20563

## PEFT for Geospatial Foundation Models

IBM Research's 2025 ECML PKDD paper reports that PEFT can match or exceed full
fine-tuning while reducing training time and memory, and can improve
generalization to unseen geographic regions. This strongly supports using PEFT
as the paper's practical-method axis.

Source:

- https://researcher.ibm.com/publications/fine-tune-smarter-not-harder-parameter-efficient-fine-tuning-for-geospatial-foundation-models

## Dataset Practice

The official Sen1Floods11 repository says the v1.1 data moved to the
`sen1floods11` GCS bucket. It includes STAC-compatible structure, hand labels,
Sentinel-1, Sentinel-2, metadata, and examples. The full dataset is about 14 GB,
which is manageable on Google Cloud or local disk.

Source:

- https://github.com/cloudtostreet/Sen1Floods11

## Responsible GeoAI

Recent responsible GeoAI work argues that disaster mapping should consider
representativeness, explainability, sustainability, and ethics. For this project,
the practical version is to report cross-region performance, error maps, invalid
mask handling, uncertainty/failure cases, and compute cost.

Sources:

- https://arxiv.org/abs/2605.00315
- https://www.nature.com/articles/s42256-025-01106-7

## Zotero and Citation Workflow

Zotero is suitable. For LaTeX, the safest workflow is:

1. Keep a shared Zotero collection for this paper.
2. Use Better BibTeX to generate stable citation keys.
3. Export a project-specific `references/paper.bib`.
4. Avoid switching between Overleaf's Zotero API import and manual BibTeX export
   unless citekeys are checked, because Overleaf warns that keys can differ
   between API import and manual export.

Sources:

- https://docs.overleaf.com/integrations-and-add-ons/reference-manager-integrations/zotero
- https://docs.overleaf.com/citing-and-references/working-with-.bib-files

## Google Cloud / Earth Engine Practice

For Earth Engine Python scripts, Google recommends `ee.Authenticate()` and
`ee.Initialize(project='my-project')`. Colab can use `auth_mode=colab`; unattended
jobs should use service accounts. This project will use GCS/Colab first, and
only use Earth Engine if additional Sentinel composites or masks are needed.

Source:

- https://developers.google.com/earth-engine/guides/auth

