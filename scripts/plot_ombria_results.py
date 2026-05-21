from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary", type=Path, default=Path("results/tables/ombria_run_summary.csv")
    )
    parser.add_argument(
        "--out-md", type=Path, default=Path("results/tables/ombria_results_table.md")
    )
    args = parser.parse_args()

    rows = read_rows(args.summary)
    args.out_md.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "| Run | Variant | S2 degradation | Test IoU | Test F1 | Test Precision | Test Recall |",
        "|---|---|---|---:|---:|---:|---:|",
    ]
    for row in sorted(rows, key=lambda r: (r.get("variant", ""), r.get("degrade_s2", ""))):
        metrics = [
            as_float(row.get("test_iou")),
            as_float(row.get("test_f1")),
            as_float(row.get("test_precision")),
            as_float(row.get("test_recall")),
        ]
        formatted = ["" if value is None else f"{value:.4f}" for value in metrics]
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("run", ""),
                    row.get("variant", ""),
                    row.get("degrade_s2", ""),
                    *formatted,
                ]
            )
            + " |"
        )

    args.out_md.write_text("\n".join(lines) + "\n")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()

