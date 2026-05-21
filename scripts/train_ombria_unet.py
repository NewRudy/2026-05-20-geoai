from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from dataclasses import asdict
from pathlib import Path
from time import time

import numpy as np

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from geoai_quickpaper.ombria import (  # noqa: E402
    VARIANTS,
    OmbriaSample,
    collect_ombria_samples,
    load_sample,
    summarize_samples,
    variant_channels,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("external/OMBRIA"))
    parser.add_argument("--variant", choices=VARIANTS, default="s2_after")
    parser.add_argument("--degrade-s2", default="none")
    parser.add_argument("--out-dir", type=Path, default=Path("results/runs/ombria"))
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--base-channels", type=int, default=24)
    parser.add_argument("--val-fraction", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-train-samples", type=int, default=0)
    parser.add_argument("--eval-checkpoint", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-checkpoint", action="store_true")
    return parser.parse_args()


class OmbriaTorchDataset:
    def __init__(
        self,
        samples: list[OmbriaSample],
        variant: str,
        degrade_s2: str = "none",
        seed: int = 7,
    ) -> None:
        import torch
        from torch.utils.data import Dataset

        class _Dataset(Dataset):
            def __len__(self_inner) -> int:
                return len(samples)

            def __getitem__(self_inner, idx: int):
                rng = np.random.default_rng(seed + idx)
                image, mask = load_sample(samples[idx], variant, degrade_s2, rng)
                x = torch.from_numpy(np.moveaxis(image, 2, 0))
                y = torch.from_numpy(mask[None, :, :])
                return x, y

        self.dataset = _Dataset()


def split_train_val(
    samples: list[OmbriaSample],
    val_fraction: float,
    seed: int,
    max_train_samples: int,
) -> tuple[list[OmbriaSample], list[OmbriaSample]]:
    shuffled = samples[:]
    random.Random(seed).shuffle(shuffled)
    val_count = max(1, int(round(len(shuffled) * val_fraction)))
    val_samples = sorted(shuffled[:val_count], key=lambda sample: sample.chip_id)
    train_samples = sorted(shuffled[val_count:], key=lambda sample: sample.chip_id)
    if max_train_samples > 0:
        train_samples = train_samples[:max_train_samples]
    return train_samples, val_samples


def build_model(in_channels: int, base_channels: int):
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    class DoubleConv(nn.Module):
        def __init__(self, in_ch: int, out_ch: int) -> None:
            super().__init__()
            self.net = nn.Sequential(
                nn.Conv2d(in_ch, out_ch, 3, padding=1),
                nn.BatchNorm2d(out_ch),
                nn.LeakyReLU(0.1, inplace=True),
                nn.Conv2d(out_ch, out_ch, 3, padding=1),
                nn.BatchNorm2d(out_ch),
                nn.LeakyReLU(0.1, inplace=True),
            )

        def forward(self, x):
            return self.net(x)

    class SmallUNet(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            c = base_channels
            self.enc1 = DoubleConv(in_channels, c)
            self.enc2 = DoubleConv(c, c * 2)
            self.enc3 = DoubleConv(c * 2, c * 4)
            self.pool = nn.MaxPool2d(2)
            self.bottleneck = DoubleConv(c * 4, c * 8)
            self.up3 = nn.ConvTranspose2d(c * 8, c * 4, 2, stride=2)
            self.dec3 = DoubleConv(c * 8, c * 4)
            self.up2 = nn.ConvTranspose2d(c * 4, c * 2, 2, stride=2)
            self.dec2 = DoubleConv(c * 4, c * 2)
            self.up1 = nn.ConvTranspose2d(c * 2, c, 2, stride=2)
            self.dec1 = DoubleConv(c * 2, c)
            self.out = nn.Conv2d(c, 1, 1)

        def forward(self, x):
            e1 = self.enc1(x)
            e2 = self.enc2(self.pool(e1))
            e3 = self.enc3(self.pool(e2))
            b = self.bottleneck(self.pool(e3))
            d3 = self.up3(b)
            d3 = self.dec3(torch.cat([d3, e3], dim=1))
            d2 = self.up2(d3)
            d2 = self.dec2(torch.cat([d2, e2], dim=1))
            d1 = self.up1(d2)
            if d1.shape[-2:] != e1.shape[-2:]:
                d1 = F.interpolate(d1, size=e1.shape[-2:], mode="bilinear")
            d1 = self.dec1(torch.cat([d1, e1], dim=1))
            return self.out(d1)

    return SmallUNet()


def binary_metrics(logits, target) -> dict[str, float]:
    import torch

    pred = torch.sigmoid(logits) > 0.5
    truth = target > 0.5
    tp = torch.logical_and(pred, truth).sum().item()
    fp = torch.logical_and(pred, ~truth).sum().item()
    fn = torch.logical_and(~pred, truth).sum().item()
    tn = torch.logical_and(~pred, ~truth).sum().item()
    eps = 1e-9
    return {
        "iou": tp / (tp + fp + fn + eps),
        "f1": (2 * tp) / (2 * tp + fp + fn + eps),
        "precision": tp / (tp + fp + eps),
        "recall": tp / (tp + fn + eps),
        "accuracy": (tp + tn) / (tp + fp + fn + tn + eps),
    }


def evaluate(model, loader, device) -> dict[str, float]:
    import torch
    import torch.nn.functional as F

    model.eval()
    loss_total = 0.0
    metrics_total = {"iou": 0.0, "f1": 0.0, "precision": 0.0, "recall": 0.0, "accuracy": 0.0}
    batches = 0
    with torch.no_grad():
        for x, y in loader:
            x = x.to(device)
            y = y.to(device)
            logits = model(x)
            loss_total += float(F.binary_cross_entropy_with_logits(logits, y).item())
            metrics = binary_metrics(logits, y)
            for key in metrics_total:
                metrics_total[key] += metrics[key]
            batches += 1
    if batches == 0:
        raise RuntimeError("Evaluation loader is empty")
    return {
        "loss": loss_total / batches,
        **{key: value / batches for key, value in metrics_total.items()},
    }


def main() -> None:
    args = parse_args()
    train_all = collect_ombria_samples(args.root, "train")
    test_samples = collect_ombria_samples(args.root, "test")
    train_samples, val_samples = split_train_val(
        train_all, args.val_fraction, args.seed, args.max_train_samples
    )

    print("variant", args.variant, "channels", variant_channels(args.variant))
    print("train", summarize_samples(train_samples))
    print("val", summarize_samples(val_samples))
    print("test", summarize_samples(test_samples))

    if args.dry_run:
        image, mask = load_sample(train_samples[0], args.variant, args.degrade_s2)
        print("sample_image_shape", image.shape, "sample_mask_shape", mask.shape)
        return

    import torch
    import torch.nn.functional as F
    from torch.utils.data import DataLoader

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = build_model(variant_channels(args.variant), args.base_channels).to(device)
    run_dir = args.out_dir / f"{args.variant}_{args.degrade_s2}_seed{args.seed}"
    run_dir.mkdir(parents=True, exist_ok=True)
    with (run_dir / "config.json").open("w") as f:
        json.dump(vars(args), f, indent=2, default=str)

    test_ds = OmbriaTorchDataset(
        test_samples, args.variant, args.degrade_s2, args.seed
    ).dataset
    test_loader = DataLoader(
        test_ds, batch_size=args.batch_size, shuffle=False, num_workers=2
    )

    if args.eval_checkpoint is not None:
        model.load_state_dict(torch.load(args.eval_checkpoint, map_location=device))
        test = evaluate(model, test_loader, device)
        out = {
            "checkpoint": str(args.eval_checkpoint),
            "variant": args.variant,
            "degrade_s2": args.degrade_s2,
            **{f"test_{key}": value for key, value in test.items()},
        }
        with (run_dir / "eval_metrics.json").open("w") as f:
            json.dump(out, f, indent=2)
        print(json.dumps(out, sort_keys=True))
        return

    train_ds = OmbriaTorchDataset(train_samples, args.variant, "none", args.seed).dataset
    val_ds = OmbriaTorchDataset(val_samples, args.variant, "none", args.seed).dataset

    train_loader = DataLoader(
        train_ds, batch_size=args.batch_size, shuffle=True, num_workers=2
    )
    val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, num_workers=2)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    with (run_dir / "splits.json").open("w") as f:
        json.dump(
            {
                "train": [asdict(sample) for sample in train_samples],
                "val": [asdict(sample) for sample in val_samples],
                "test": [asdict(sample) for sample in test_samples],
            },
            f,
            indent=2,
            default=str,
        )

    metrics_path = run_dir / "metrics.csv"
    best_val_iou = -1.0
    start = time()
    with metrics_path.open("w", newline="") as f:
        fieldnames = [
            "epoch",
            "train_loss",
            "val_loss",
            "val_iou",
            "val_f1",
            "val_precision",
            "val_recall",
            "val_accuracy",
            "test_loss",
            "test_iou",
            "test_f1",
            "test_precision",
            "test_recall",
            "test_accuracy",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for epoch in range(1, args.epochs + 1):
            model.train()
            train_loss = 0.0
            train_batches = 0
            for x, y in train_loader:
                x = x.to(device)
                y = y.to(device)
                optimizer.zero_grad(set_to_none=True)
                logits = model(x)
                loss = F.binary_cross_entropy_with_logits(logits, y)
                loss.backward()
                optimizer.step()
                train_loss += float(loss.item())
                train_batches += 1

            val = evaluate(model, val_loader, device)
            test = evaluate(model, test_loader, device)
            row = {
                "epoch": epoch,
                "train_loss": train_loss / max(train_batches, 1),
                "val_loss": val["loss"],
                "val_iou": val["iou"],
                "val_f1": val["f1"],
                "val_precision": val["precision"],
                "val_recall": val["recall"],
                "val_accuracy": val["accuracy"],
                "test_loss": test["loss"],
                "test_iou": test["iou"],
                "test_f1": test["f1"],
                "test_precision": test["precision"],
                "test_recall": test["recall"],
                "test_accuracy": test["accuracy"],
            }
            writer.writerow(row)
            f.flush()
            print(json.dumps(row, sort_keys=True))

            if val["iou"] > best_val_iou and not args.no_checkpoint:
                best_val_iou = val["iou"]
                torch.save(model.state_dict(), run_dir / "best_model.pt")

    elapsed = time() - start
    print(f"finished run_dir={run_dir} elapsed_seconds={elapsed:.1f}")


if __name__ == "__main__":
    main()
