from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path


METRICS = ("test_iou", "test_f1", "test_precision", "test_recall")
DEGRADATION_ORDER = ("none", "patch_after", "noise_after", "zero_after", "zero_all")
TRAIN_ORDER = ("none", "modality_dropout")


def as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def sample_std(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mu = mean(values)
    assert mu is not None
    return math.sqrt(sum((value - mu) ** 2 for value in values) / (len(values) - 1))


def fmt(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.4f}"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    eval_rows = [row for row in rows if row.get("record_type") == "eval"]
    if eval_rows:
        rows = eval_rows

    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row.get("variant") != "multimodal":
            continue
        train_mode = row.get("train_degrade_s2", "none") or "none"
        test_mode = row.get("degrade_s2", "none") or "none"
        groups[(test_mode, train_mode)].append(row)

    summary: list[dict[str, str]] = []
    for test_mode in DEGRADATION_ORDER:
        for train_mode in TRAIN_ORDER:
            values = groups.get((test_mode, train_mode), [])
            if not values:
                continue
            record: dict[str, str] = {
                "degrade_s2": test_mode,
                "train_degrade_s2": train_mode,
                "n": str(len(values)),
                "seeds": ",".join(sorted({str(row.get("seed", "")) for row in values})),
            }
            for metric in METRICS:
                metric_values = [
                    value
                    for value in (as_float(row.get(metric)) for row in values)
                    if value is not None
                ]
                record[f"{metric}_mean"] = fmt(mean(metric_values))
                record[f"{metric}_std"] = fmt(sample_std(metric_values))
            summary.append(record)
    return summary


def add_deltas(summary: list[dict[str, str]]) -> list[dict[str, str]]:
    by_mode = {
        (row["degrade_s2"], row["train_degrade_s2"]): row
        for row in summary
    }
    output: list[dict[str, str]] = []
    for row in summary:
        record = dict(row)
        if row["train_degrade_s2"] == "modality_dropout":
            clean = by_mode.get((row["degrade_s2"], "none"))
            if clean is not None:
                for metric in METRICS:
                    robust_value = as_float(row.get(f"{metric}_mean"))
                    clean_value = as_float(clean.get(f"{metric}_mean"))
                    delta = None
                    if robust_value is not None and clean_value is not None:
                        delta = robust_value - clean_value
                    record[f"delta_vs_clean_train_{metric}"] = fmt(delta)
        output.append(record)
    return output


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "| Test S2 degradation | Training | n | IoU mean | IoU std | F1 mean | F1 std | Delta IoU vs clean-train | Delta F1 vs clean-train |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row.get("degrade_s2", ""),
                    row.get("train_degrade_s2", ""),
                    row.get("n", ""),
                    row.get("test_iou_mean", ""),
                    row.get("test_iou_std", ""),
                    row.get("test_f1_mean", ""),
                    row.get("test_f1_std", ""),
                    row.get("delta_vs_clean_train_test_iou", ""),
                    row.get("delta_vs_clean_train_test_f1", ""),
                ]
            )
            + " |"
        )

    verdict = robustness_verdict(rows)
    lines.extend(["", "## Robustness Decision", "", verdict])
    path.write_text("\n".join(lines) + "\n")


def robustness_verdict(rows: list[dict[str, str]]) -> str:
    robust_rows = [
        row
        for row in rows
        if row.get("train_degrade_s2") == "modality_dropout"
        and row.get("degrade_s2") != "none"
    ]
    deltas = [
        as_float(row.get("delta_vs_clean_train_test_iou"))
        for row in robust_rows
    ]
    observed = [value for value in deltas if value is not None]
    clean_row = next(
        (
            row
            for row in rows
            if row.get("train_degrade_s2") == "modality_dropout"
            and row.get("degrade_s2") == "none"
        ),
        None,
    )
    clean_delta = as_float(
        clean_row.get("delta_vs_clean_train_test_iou") if clean_row else None
    )

    if observed and all(value > 0 for value in observed):
        if clean_delta is not None and clean_delta >= -0.05:
            return (
                "Go: modality-dropout training improves all tested degraded "
                "Sentinel-2 conditions while keeping the clean IoU penalty within 0.05."
            )
        return (
            "Borderline go: degraded-condition gains are consistent, but the clean "
            "condition penalty should be discussed or reduced."
        )
    if observed and sum(value > 0 for value in observed) >= max(1, len(observed) - 1):
        return (
            "Borderline: most degraded conditions improve, but at least one failure "
            "case needs inspection before this is a manuscript claim."
        )
    return (
        "No-go from current summary: the robust training signal is not consistent "
        "enough yet. Rerun or switch direction."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary", type=Path, default=Path("results/tables/ombria_run_summary.csv")
    )
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("results/tables/ombria_robustness_summary.csv"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("results/tables/ombria_robustness_summary.md"),
    )
    args = parser.parse_args()

    rows = add_deltas(summarize(read_rows(args.summary)))
    write_csv(rows, args.out_csv)
    write_markdown(rows, args.out_md)
    print(f"wrote {len(rows)} rows to {args.out_csv}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
