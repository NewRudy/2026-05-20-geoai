from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from geoai_quickpaper.ombria import (  # noqa: E402
    VARIANTS,
    collect_ombria_samples,
    load_sample,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("external/OMBRIA"))
    parser.add_argument("--out", type=Path, default=Path("results/tables/ombria_pixel_baseline.csv"))
    parser.add_argument("--variant", choices=VARIANTS, default="multimodal")
    parser.add_argument("--degrade-s2", default="none")
    parser.add_argument("--train-pixels", type=int, default=200000)
    parser.add_argument("--eval-pixels-per-chip", type=int, default=0)
    parser.add_argument("--epochs", type=int, default=200, help="Ignored for ridge baseline.")
    parser.add_argument("--lr", type=float, default=0.05, help="Ignored for ridge baseline.")
    parser.add_argument("--l2", type=float, default=1e-2)
    parser.add_argument("--seed", type=int, default=7)
    return parser.parse_args()


def sample_training_pixels(root: Path, variant: str, n_pixels: int, seed: int):
    rng = np.random.default_rng(seed)
    samples = collect_ombria_samples(root, "train")
    per_chip = max(1, int(np.ceil(n_pixels / len(samples))))
    xs = []
    ys = []
    for idx, sample in enumerate(samples):
        image, mask = load_sample(sample, variant, "none", np.random.default_rng(seed + idx))
        flat_x = image.reshape(-1, image.shape[-1])
        flat_y = mask.reshape(-1)
        take = min(per_chip, len(flat_y))
        choice = rng.choice(len(flat_y), size=take, replace=False)
        xs.append(flat_x[choice])
        ys.append(flat_y[choice])
    x = np.concatenate(xs, axis=0)[:n_pixels]
    y = np.concatenate(ys, axis=0)[:n_pixels]
    return x, y


def standardize_train(x: np.ndarray):
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True)
    std[std < 1e-6] = 1.0
    x = (x - mean) / std
    x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
    return np.clip(x, -10.0, 10.0), mean, std


def fit_ridge_classifier(x: np.ndarray, y: np.ndarray, l2: float):
    x_aug = np.concatenate([x, np.ones((x.shape[0], 1), dtype=x.dtype)], axis=1)
    x_aug = x_aug.astype(np.float64)
    y = y.astype(np.float64)
    eye = np.eye(x_aug.shape[1], dtype=np.float64)
    eye[-1, -1] = 0.0
    return np.linalg.solve(x_aug.T @ x_aug + l2 * eye, x_aug.T @ y)


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
        "accuracy": float((tp + tn) / (tp + fp + fn + tn + eps)),
    }


def evaluate(root: Path, variant: str, degrade_s2: str, w, mean, std, seed: int, max_pixels: int):
    rng = np.random.default_rng(seed)
    rows = []
    for idx, sample in enumerate(collect_ombria_samples(root, "test")):
        image, mask = load_sample(sample, variant, degrade_s2, np.random.default_rng(seed + idx))
        x = image.reshape(-1, image.shape[-1])
        y = mask.reshape(-1)
        if max_pixels > 0 and max_pixels < len(y):
            choice = rng.choice(len(y), size=max_pixels, replace=False)
            x = x[choice]
            y = y[choice]
        x = (x - mean) / std
        x = np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0)
        x = np.clip(x, -10.0, 10.0)
        x_aug = np.concatenate([x, np.ones((x.shape[0], 1), dtype=x.dtype)], axis=1)
        pred = (x_aug @ w) > 0.5
        row = {"chip_id": sample.chip_id, "variant": variant, "degrade_s2": degrade_s2}
        row.update(binary_metrics(pred, y))
        rows.append(row)
    return rows


def main() -> None:
    args = parse_args()
    x, y = sample_training_pixels(args.root, args.variant, args.train_pixels, args.seed)
    x, mean, std = standardize_train(x)
    w = fit_ridge_classifier(x, y, args.l2)
    rows = evaluate(
        args.root,
        args.variant,
        args.degrade_s2,
        w,
        mean,
        std,
        args.seed,
        args.eval_pixels_per_chip,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "chip_id",
        "variant",
        "degrade_s2",
        "iou",
        "f1",
        "precision",
        "recall",
        "accuracy",
    ]
    write_header = not args.out.exists()
    with args.out.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(rows)
    print(
        f"variant={args.variant} degrade_s2={args.degrade_s2} "
        f"mean_iou={np.mean([row['iou'] for row in rows]):.4f} "
        f"mean_f1={np.mean([row['f1'] for row in rows]):.4f} out={args.out}"
    )


if __name__ == "__main__":
    main()
