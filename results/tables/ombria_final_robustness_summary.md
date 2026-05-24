| Test S2 degradation | Training | n | IoU mean | IoU std | F1 mean | F1 std | Delta IoU vs clean-train | Delta F1 vs clean-train |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| none | none | 3 | 0.6890 | 0.0066 | 0.8092 | 0.0054 |  |  |
| none | modality_dropout | 3 | 0.6338 | 0.0201 | 0.7674 | 0.0170 | -0.0552 | -0.0418 |
| patch_after | none | 3 | 0.5722 | 0.0160 | 0.7141 | 0.0164 |  |  |
| patch_after | modality_dropout | 3 | 0.5616 | 0.0365 | 0.7092 | 0.0325 | -0.0106 | -0.0049 |
| noise_after | none | 3 | 0.3285 | 0.0837 | 0.4804 | 0.0894 |  |  |
| noise_after | modality_dropout | 3 | 0.4065 | 0.0175 | 0.5692 | 0.0195 | 0.0780 | 0.0888 |
| zero_after | none | 3 | 0.4052 | 0.0186 | 0.5601 | 0.0133 |  |  |
| zero_after | modality_dropout | 3 | 0.4383 | 0.0328 | 0.5995 | 0.0322 | 0.0331 | 0.0394 |
| zero_all | none | 3 | 0.0406 | 0.0266 | 0.0725 | 0.0460 |  |  |
| zero_all | modality_dropout | 3 | 0.3104 | 0.0743 | 0.4453 | 0.0935 | 0.2698 | 0.3728 |

## Robustness Decision

Borderline: most degraded conditions improve, but at least one failure case needs inspection before this is a manuscript claim.
