| Test S2 degradation | Training | n | IoU mean | IoU std | F1 mean | F1 std | Delta IoU vs clean-train | Delta F1 vs clean-train |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| none | none | 1 | 0.6307 |  | 0.7631 |  |  |  |
| none | modality_dropout_light | 1 | 0.6229 |  | 0.7575 |  | -0.0078 | -0.0056 |
| none | modality_dropout_balanced | 1 | 0.6045 |  | 0.7429 |  | -0.0262 | -0.0202 |
| none | modality_dropout_patch | 1 | 0.5886 |  | 0.7269 |  | -0.0421 | -0.0362 |
| patch_after | none | 1 | 0.5014 |  | 0.6472 |  |  |  |
| patch_after | modality_dropout_light | 1 | 0.5179 |  | 0.6656 |  | 0.0165 | 0.0184 |
| patch_after | modality_dropout_balanced | 1 | 0.5127 |  | 0.6645 |  | 0.0113 | 0.0173 |
| patch_after | modality_dropout_patch | 1 | 0.4972 |  | 0.6449 |  | -0.0042 | -0.0023 |
| noise_after | none | 1 | 0.3087 |  | 0.4671 |  |  |  |
| noise_after | modality_dropout_light | 1 | 0.2867 |  | 0.4353 |  | -0.0220 | -0.0318 |
| noise_after | modality_dropout_balanced | 1 | 0.2848 |  | 0.4338 |  | -0.0239 | -0.0333 |
| noise_after | modality_dropout_patch | 1 | 0.2900 |  | 0.4396 |  | -0.0187 | -0.0275 |
| zero_after | none | 1 | 0.3975 |  | 0.5435 |  |  |  |
| zero_after | modality_dropout_light | 1 | 0.4194 |  | 0.5703 |  | 0.0219 | 0.0268 |
| zero_after | modality_dropout_balanced | 1 | 0.4126 |  | 0.5702 |  | 0.0151 | 0.0267 |
| zero_after | modality_dropout_patch | 1 | 0.4132 |  | 0.5619 |  | 0.0157 | 0.0184 |
| zero_all | none | 1 | 0.2245 |  | 0.3371 |  |  |  |
| zero_all | modality_dropout_light | 1 | 0.3505 |  | 0.5079 |  | 0.1260 | 0.1708 |
| zero_all | modality_dropout_balanced | 1 | 0.3911 |  | 0.5478 |  | 0.1666 | 0.2107 |
| zero_all | modality_dropout_patch | 1 | 0.3876 |  | 0.5406 |  | 0.1631 | 0.2035 |

## Robustness Decision

- Borderline for modality_dropout_light: most degraded conditions improve, but at least one failure case needs inspection before this is a manuscript claim.
- Borderline for modality_dropout_balanced: most degraded conditions improve, but at least one failure case needs inspection before this is a manuscript claim.
- No-go for modality_dropout_patch: the robust training signal is not consistent enough yet.
