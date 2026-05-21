from __future__ import annotations

import argparse
import csv
from pathlib import Path

from geoai_quickpaper.manifest import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    chips = build_manifest(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    with args.out.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["event", "chip_id", "layer", "path"]
        )
        writer.writeheader()
        for chip in chips:
            writer.writerow(
                {
                    "event": chip.event,
                    "chip_id": chip.chip_id,
                    "layer": chip.layer,
                    "path": str(chip.path),
                }
            )

    print(f"Wrote {len(chips)} records to {args.out}")


if __name__ == "__main__":
    main()

