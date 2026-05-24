from __future__ import annotations

import argparse
import csv
from pathlib import Path


DEGRADATION_ORDER = ("none", "patch_after", "noise_after", "zero_after", "zero_all")
LABELS = {
    "none": "Clean",
    "patch_after": "Patch mask",
    "noise_after": "Noise",
    "zero_after": "After S2 missing",
    "zero_all": "All S2 missing",
}


def as_float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open() as f:
        return list(csv.DictReader(f))


def metric_series(
    rows: list[dict[str, str]], train_mode: str, metric: str
) -> list[float | None]:
    lookup = {
        (row.get("degrade_s2"), row.get("train_degrade_s2")): row for row in rows
    }
    return [
        as_float(lookup.get((mode, train_mode), {}).get(f"{metric}_mean"))
        for mode in DEGRADATION_ORDER
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/tables/ombria_robustness_summary.csv"),
    )
    parser.add_argument(
        "--out", type=Path, default=Path("results/figures/ombria_robustness.png")
    )
    args = parser.parse_args()

    rows = read_rows(args.summary)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        plot_with_pillow(rows, args.out)
        return

    x = list(range(len(DEGRADATION_ORDER)))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=False)
    for ax, metric, title in [
        (axes[0], "test_iou", "Flood IoU"),
        (axes[1], "test_f1", "Flood F1"),
    ]:
        clean = metric_series(rows, "none", metric)
        robust = metric_series(rows, "modality_dropout", metric)
        ax.plot(x, clean, marker="o", label="Clean training", linewidth=2)
        ax.plot(x, robust, marker="s", label="Modality dropout", linewidth=2)
        ax.set_title(title)
        ax.set_xticks(x)
        ax.set_xticklabels(
            [LABELS[mode] for mode in DEGRADATION_ORDER], rotation=25, ha="right"
        )
        ax.set_ylim(0.0, 1.0)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Score")
    axes[1].legend(loc="lower left")
    fig.tight_layout()
    fig.savefig(args.out, dpi=200)
    print(f"wrote {args.out}")


def plot_with_pillow(rows: list[dict[str, str]], out: Path) -> None:
    from PIL import Image, ImageDraw

    width, height = 1100, 430
    margin_left, margin_right = 70, 30
    margin_top, margin_bottom = 45, 105
    gap = 55
    panel_width = (width - margin_left - margin_right - gap) // 2
    plot_height = height - margin_top - margin_bottom

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    def draw_panel(x0: int, metric: str, title: str) -> None:
        y0 = margin_top
        x1 = x0 + panel_width
        y1 = y0 + plot_height
        draw.rectangle([x0, y0, x1, y1], outline=(210, 210, 210))
        draw.text((x0, 18), title, fill=(20, 20, 20))
        for tick in range(6):
            value = tick / 5
            y = y1 - int(value * plot_height)
            draw.line([x0, y, x1, y], fill=(235, 235, 235))
            draw.text((x0 - 38, y - 7), f"{value:.1f}", fill=(80, 80, 80))

        series = [
            ("Clean training", metric_series(rows, "none", metric), (31, 119, 180)),
            (
                "Modality dropout",
                metric_series(rows, "modality_dropout", metric),
                (214, 39, 40),
            ),
        ]
        step = panel_width / max(len(DEGRADATION_ORDER) - 1, 1)
        for label, values, color in series:
            points = []
            for idx, value in enumerate(values):
                if value is None:
                    continue
                x = x0 + int(idx * step)
                y = y1 - int(max(0.0, min(1.0, value)) * plot_height)
                points.append((x, y))
            if len(points) >= 2:
                draw.line(points, fill=color, width=3)
            for x, y in points:
                draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=color)
            legend_y = y1 + 70 + (0 if label.startswith("Clean") else 18)
            draw.line([x0, legend_y + 6, x0 + 24, legend_y + 6], fill=color, width=3)
            draw.text((x0 + 30, legend_y), label, fill=(30, 30, 30))

        for idx, mode in enumerate(DEGRADATION_ORDER):
            x = x0 + int(idx * step)
            draw.text((x - 38, y1 + 12), LABELS[mode], fill=(70, 70, 70))

    draw_panel(margin_left, "test_iou", "Flood IoU")
    draw_panel(margin_left + panel_width + gap, "test_f1", "Flood F1")
    image.save(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
