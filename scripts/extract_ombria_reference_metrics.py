from __future__ import annotations

import argparse
import ast
import csv
import json
import re
from pathlib import Path
from statistics import mean


ASSIGNMENT_RE = re.compile(
    r"(?P<name>S2acc|S2iou|S1acc|S1iou|acc_bi|iou_bi|acc_mult|iou_mult|svm_acc|svm_iou)\s*=\s*(?P<value>\[[^\]]+\])",
    re.DOTALL,
)

NAME_MAP = {
    "S2acc": ("s2_unet", "accuracy"),
    "S2iou": ("s2_unet", "iou"),
    "S1acc": ("s1_unet", "accuracy"),
    "S1iou": ("s1_unet", "iou"),
    "acc_bi": ("bitemporal", "accuracy"),
    "iou_bi": ("bitemporal", "iou"),
    "acc_mult": ("multimodal", "accuracy"),
    "iou_mult": ("multimodal", "iou"),
    "svm_acc": ("svm", "accuracy"),
    "svm_iou": ("svm", "iou"),
}


def load_notebook_source(path: Path) -> str:
    data = json.loads(path.read_text())
    return "\n".join(
        "".join(cell.get("source", [])) for cell in data.get("cells", [])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--notebook", type=Path, default=Path("external/OMBRIA/Evaluation.ipynb")
    )
    parser.add_argument(
        "--out", type=Path, default=Path("results/tables/ombria_reference_metrics.csv")
    )
    args = parser.parse_args()

    source = load_notebook_source(args.notebook)
    raw = {}
    for match in ASSIGNMENT_RE.finditer(source):
        raw[match.group("name")] = ast.literal_eval(match.group("value"))

    records = {}
    for name, values in raw.items():
        model, metric = NAME_MAP[name]
        records.setdefault(model, {})[metric] = values

    rows = []
    for model, metrics in sorted(records.items()):
        row = {"model": model}
        for metric, values in metrics.items():
            row[f"{metric}_n"] = len(values)
            row[f"{metric}_mean"] = mean(values)
            row[f"{metric}_min"] = min(values)
            row[f"{metric}_max"] = max(values)
        rows.append(row)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} records to {args.out}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()

