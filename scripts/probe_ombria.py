from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class Pair:
    split: str
    sensor: str
    chip_id: str
    before: Path
    after: Path
    mask: Path


def _chip_id(path: Path) -> str:
    return path.stem.split("_")[-1]


def collect_pairs(root: Path) -> list[Pair]:
    pairs: list[Pair] = []
    for sensor in ("OmbriaS1", "OmbriaS2"):
        for split in ("train", "test"):
            base = root / sensor / split
            before_by_id = {_chip_id(p): p for p in (base / "BEFORE").glob("*.png")}
            after_by_id = {_chip_id(p): p for p in (base / "AFTER").glob("*.png")}
            mask_by_id = {_chip_id(p): p for p in (base / "MASK").glob("*.png")}
            for chip_id in sorted(before_by_id.keys() & after_by_id.keys() & mask_by_id.keys()):
                pairs.append(
                    Pair(
                        split=split,
                        sensor=sensor[-2:],
                        chip_id=chip_id,
                        before=before_by_id[chip_id],
                        after=after_by_id[chip_id],
                        mask=mask_by_id[chip_id],
                    )
                )
    return pairs


def read_gray(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0


def read_mask(path: Path) -> np.ndarray:
    return read_gray(path) > 0.5


def otsu_threshold(image: np.ndarray) -> float:
    hist, bin_edges = np.histogram(image.ravel(), bins=256, range=(0.0, 1.0))
    centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    weight1 = np.cumsum(hist)
    weight2 = np.cumsum(hist[::-1])[::-1]
    mean1 = np.cumsum(hist * centers) / np.maximum(weight1, 1)
    mean2 = (np.cumsum((hist * centers)[::-1]) / np.maximum(weight2[::-1], 1))[::-1]
    variance12 = weight1[:-1] * weight2[1:] * (mean1[:-1] - mean2[1:]) ** 2
    return float(centers[:-1][np.argmax(variance12)])


def binary_metrics(pred: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    pred = pred.astype(bool)
    truth = truth.astype(bool)
    tp = np.logical_and(pred, truth).sum()
    fp = np.logical_and(pred, ~truth).sum()
    fn = np.logical_and(~pred, truth).sum()
    tn = np.logical_and(~pred, ~truth).sum()
    eps = 1e-9
    return {
        "iou": float(tp / (tp + fp + fn + eps)),
        "f1": float((2 * tp) / (2 * tp + fp + fn + eps)),
        "precision": float(tp / (tp + fp + eps)),
        "recall": float(tp / (tp + fn + eps)),
        "flood_fraction": float(truth.mean()),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("external/OMBRIA"))
    parser.add_argument("--out", type=Path, default=Path("results/tables/ombria_probe.csv"))
    args = parser.parse_args()

    pairs = collect_pairs(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    for pair in pairs:
        after = read_gray(pair.after)
        before = read_gray(pair.before)
        mask = read_mask(pair.mask)
        diff = np.clip(after - before, -1.0, 1.0)
        diff_shifted = (diff + 1.0) / 2.0

        candidates = {
            "after_low_otsu": after < otsu_threshold(after),
            "after_high_otsu": after > otsu_threshold(after),
            "diff_low_otsu": diff_shifted < otsu_threshold(diff_shifted),
            "diff_high_otsu": diff_shifted > otsu_threshold(diff_shifted),
        }
        for method, pred in candidates.items():
            row = {
                "split": pair.split,
                "sensor": pair.sensor,
                "chip_id": pair.chip_id,
                "method": method,
            }
            row.update(binary_metrics(pred, mask))
            rows.append(row)

    fieldnames = [
        "split",
        "sensor",
        "chip_id",
        "method",
        "iou",
        "f1",
        "precision",
        "recall",
        "flood_fraction",
        "tp",
        "fp",
        "fn",
        "tn",
    ]
    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"pairs={len(pairs)} rows={len(rows)} out={args.out}")
    for split in ("train", "test"):
        for sensor in ("S1", "S2"):
            subset = [
                row
                for row in rows
                if row["split"] == split and row["sensor"] == sensor
            ]
            chips = {row["chip_id"] for row in subset}
            flood = np.mean([row["flood_fraction"] for row in subset])
            print(f"{split} {sensor}: chips={len(chips)} mean_flood_fraction={flood:.4f}")


if __name__ == "__main__":
    main()

