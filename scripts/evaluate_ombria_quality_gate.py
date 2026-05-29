from __future__ import annotations

import argparse
import csv
from pathlib import Path


METHOD = "quality_sar_anchor_severe_w025"
BASELINES = ("modality_dropout_light", "quality_dropout_light")


def as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def fmt(value: float | None) -> str:
    if value is None:
        return "missing"
    return f"{value:.4f}"


def read_rows(path: Path) -> dict[str, dict[str, str]]:
    with path.open() as f:
        rows = list(csv.DictReader(f))
    return {row["train_degrade_s2"]: row for row in rows}


def check(
    name: str,
    passed: bool,
    observed: str,
    threshold: str,
) -> dict[str, str]:
    return {
        "criterion": name,
        "status": "pass" if passed else "fail",
        "observed": observed,
        "threshold": threshold,
    }


def evaluate(
    rows: dict[str, dict[str, str]],
    *,
    clean_delta_floor: float,
    degraded_gain_floor: float,
    worst_floor: float,
    zero_all_gap_floor: float,
) -> tuple[str, list[dict[str, str]]]:
    method = rows.get(METHOD)
    if method is None:
        return "NO-GO", [
            check(
                "method row present",
                False,
                METHOD,
                "quality-gated SAR anchor result must exist",
            )
        ]

    baseline_rows = [rows.get(name) for name in BASELINES if rows.get(name)]
    degraded_mean = as_float(method.get("degraded_mean_iou"))
    worst = as_float(method.get("worst_degraded_iou"))
    zero_all = as_float(method.get("zero_all_iou"))
    clean_delta = as_float(method.get("clean_delta_vs_clean_train"))
    zero_all_gap = as_float(method.get("zero_all_gap_vs_s1"))

    baseline_degraded = [
        value
        for row in baseline_rows
        for value in [as_float(row.get("degraded_mean_iou"))]
        if value is not None
    ]
    baseline_worst = [
        value
        for row in baseline_rows
        for value in [as_float(row.get("worst_degraded_iou"))]
        if value is not None
    ]
    baseline_zero_all = [
        value
        for row in baseline_rows
        for value in [as_float(row.get("zero_all_iou"))]
        if value is not None
    ]

    best_baseline_degraded = max(baseline_degraded) if baseline_degraded else None
    best_baseline_worst = max(baseline_worst) if baseline_worst else None
    best_baseline_zero_all = max(baseline_zero_all) if baseline_zero_all else None

    checks = [
        check(
            "clean IoU penalty controlled",
            clean_delta is not None and clean_delta >= clean_delta_floor,
            fmt(clean_delta),
            f">= {clean_delta_floor:.4f}",
        ),
        check(
            "mean degraded IoU beats baselines",
            degraded_mean is not None
            and best_baseline_degraded is not None
            and degraded_mean >= best_baseline_degraded + degraded_gain_floor,
            f"{fmt(degraded_mean)} vs best baseline {fmt(best_baseline_degraded)}",
            f">= best baseline + {degraded_gain_floor:.4f}",
        ),
        check(
            "worst degraded IoU is usable",
            worst is not None and worst >= worst_floor,
            fmt(worst),
            f">= {worst_floor:.4f}",
        ),
        check(
            "worst degraded IoU beats baselines",
            worst is not None
            and best_baseline_worst is not None
            and worst >= best_baseline_worst,
            f"{fmt(worst)} vs best baseline {fmt(best_baseline_worst)}",
            ">= best baseline",
        ),
        check(
            "all-S2-missing IoU beats baselines",
            zero_all is not None
            and best_baseline_zero_all is not None
            and zero_all >= best_baseline_zero_all + degraded_gain_floor,
            f"{fmt(zero_all)} vs best baseline {fmt(best_baseline_zero_all)}",
            f">= best baseline + {degraded_gain_floor:.4f}",
        ),
        check(
            "all-S2-missing remains close to SAR fallback",
            zero_all_gap is not None and zero_all_gap >= zero_all_gap_floor,
            fmt(zero_all_gap),
            f">= {zero_all_gap_floor:.4f}",
        ),
    ]

    passed = sum(row["status"] == "pass" for row in checks)
    if passed == len(checks):
        verdict = "PASS"
    elif passed >= 4:
        verdict = "BORDERLINE"
    else:
        verdict = "NO-GO"
    return verdict, checks


def write_markdown(verdict: str, checks: list[dict[str, str]], path: Path) -> None:
    lines = [
        f"# Quality-Gated SAR Anchor Gate: {verdict}",
        "",
        "| Criterion | Status | Observed | Threshold |",
        "|---|---|---:|---:|",
    ]
    for row in checks:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["criterion"],
                    row["status"],
                    row["observed"],
                    row["threshold"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- PASS: extend to seeds 13 and 21 before writing.",
            "- BORDERLINE: inspect per-degradation rows and consider one more tuning run.",
            "- NO-GO: do not build the manuscript around this method.",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metrics",
        type=Path,
        default=Path("results/tables/ombria_quality_anchor_graceful_metrics.csv"),
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=Path("results/tables/ombria_quality_anchor_gate.md"),
    )
    parser.add_argument("--clean-delta-floor", type=float, default=-0.03)
    parser.add_argument("--degraded-gain-floor", type=float, default=0.01)
    parser.add_argument("--worst-floor", type=float, default=0.35)
    parser.add_argument("--zero-all-gap-floor", type=float, default=-0.05)
    args = parser.parse_args()

    verdict, checks = evaluate(
        read_rows(args.metrics),
        clean_delta_floor=args.clean_delta_floor,
        degraded_gain_floor=args.degraded_gain_floor,
        worst_floor=args.worst_floor,
        zero_all_gap_floor=args.zero_all_gap_floor,
    )
    write_markdown(verdict, checks, args.out_md)
    print(verdict)
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
