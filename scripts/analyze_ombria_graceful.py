from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


DEGRADED_MODES = (
    "patch_after",
    "cloud_after_10",
    "cloud_after_30",
    "cloud_after_50",
    "cloud_after_70",
    "noise_after",
    "zero_after",
    "zero_all",
)
TRAIN_ORDER = (
    "none",
    "modality_dropout_light",
    "quality_dropout_light",
    "sar_anchor_light",
    "sar_anchor_severe_w010",
    "sar_anchor_severe_w020",
    "sar_anchor_severe_w025",
    "quality_sar_anchor_severe_w025",
)


def as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def fmt(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.4f}"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def training_label(row: dict[str, str]) -> str:
    train_mode = row.get("train_degrade_s2", "none") or "none"
    s2_quality = row.get("s2_quality", "none") or "none"
    if s2_quality != "none" and train_mode.startswith("sar_anchor"):
        return f"quality_{train_mode}"
    return train_mode


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    eval_rows = [row for row in rows if row.get("record_type") == "eval"]
    train_rows = [row for row in rows if row.get("record_type") == "train"]

    s1_values = [
        as_float(row.get("test_iou"))
        for row in train_rows
        if row.get("variant") == "s1_bitemporal"
    ]
    s1_baseline = mean([value for value in s1_values if value is not None])

    multimodal: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in eval_rows:
        if row.get("variant") != "multimodal":
            continue
        key = (
            training_label(row),
            row.get("degrade_s2", "none") or "none",
        )
        value = as_float(row.get("test_iou"))
        if value is not None:
            multimodal[key].append(value)

    clean_reference = mean(multimodal.get(("none", "none"), []))
    records: list[dict[str, str]] = []
    for train_mode in TRAIN_ORDER:
        if not any(key[0] == train_mode for key in multimodal):
            continue
        clean_iou = mean(multimodal.get((train_mode, "none"), []))
        degraded_values = [
            value
            for mode in DEGRADED_MODES
            for value in multimodal.get((train_mode, mode), [])
        ]
        zero_all_iou = mean(multimodal.get((train_mode, "zero_all"), []))
        worst_degraded = min(degraded_values) if degraded_values else None
        degraded_mean = mean(degraded_values)
        records.append(
            {
                "train_degrade_s2": train_mode,
                "clean_iou": fmt(clean_iou),
                "clean_delta_vs_clean_train": fmt(
                    None
                    if clean_iou is None or clean_reference is None
                    else clean_iou - clean_reference
                ),
                "degraded_mean_iou": fmt(degraded_mean),
                "worst_degraded_iou": fmt(worst_degraded),
                "zero_all_iou": fmt(zero_all_iou),
                "s1_bitemporal_iou": fmt(s1_baseline),
                "zero_all_gap_vs_s1": fmt(
                    None
                    if zero_all_iou is None or s1_baseline is None
                    else zero_all_iou - s1_baseline
                ),
            }
        )
    return records


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "train_degrade_s2",
        "clean_iou",
        "clean_delta_vs_clean_train",
        "degraded_mean_iou",
        "worst_degraded_iou",
        "zero_all_iou",
        "s1_bitemporal_iou",
        "zero_all_gap_vs_s1",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| Training | Clean IoU | Clean delta | Mean degraded IoU | Worst degraded IoU | Zero-all IoU | S1 IoU | Zero-all gap vs S1 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["train_degrade_s2"],
                    row["clean_iou"],
                    row["clean_delta_vs_clean_train"],
                    row["degraded_mean_iou"],
                    row["worst_degraded_iou"],
                    row["zero_all_iou"],
                    row["s1_bitemporal_iou"],
                    row["zero_all_gap_vs_s1"],
                ]
            )
            + " |"
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--out-md", type=Path, required=True)
    args = parser.parse_args()

    rows = summarize(read_rows(args.summary))
    write_csv(rows, args.out_csv)
    write_markdown(rows, args.out_md)
    print(f"wrote {len(rows)} graceful records")


if __name__ == "__main__":
    main()
