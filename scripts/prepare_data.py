"""Check a YOLO-seg dataset and split it into train/val for Ultralytics.

The competition zip has a flat layout (images/, labels/, optional data.yaml).
This script accepts one or more such folders or zips, checks every label
line, splits images into train/val with a fixed seed, and writes data.yaml.

Example:
    python scripts/prepare_data.py --src du_lieu.zip --out datasets/robotaxi
    python scripts/prepare_data.py --src datasets/raw_a datasets/raw_b --val-frac 0.2
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
import sys
import zipfile
from collections import Counter
from pathlib import Path

CLASS_NAMES = [
    "Car",
    "Bus",
    "Truck",
    "Other vehicle",
    "Motorcycle",
    "Motorcyclist",
    "Bicycle",
    "Cyclist",
    "Pedestrian",
    "Sign",
    "Traffic light",
]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def unpack(src: Path, work: Path) -> Path:
    """Return a folder for src, extracting it first if it is a zip."""
    if src.is_dir():
        return src
    if src.suffix.lower() == ".zip":
        dest = work / src.stem
        if not dest.exists():
            print(f"Extracting {src} -> {dest}")
            with zipfile.ZipFile(src) as zf:
                zf.extractall(dest)
        return dest
    sys.exit(f"Not a folder or .zip: {src}")


def find_root(folder: Path) -> Path:
    """Find the folder that holds images/ and labels/ (zips often add one level)."""
    for cand in [folder, *sorted(p for p in folder.rglob("*") if p.is_dir())]:
        if (cand / "images").is_dir():
            return cand
    sys.exit(f"No images/ folder found under {folder}")


def check_label(path: Path) -> tuple[list[str], list[str]]:
    """Return (valid lines, problems) for one label file."""
    good, problems = [], []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split()
        if not parts:
            continue
        where = f"{path.name}:{n}"
        try:
            cls = int(parts[0])
            coords = [float(v) for v in parts[1:]]
        except ValueError:
            problems.append(f"{where} not numeric")
            continue
        if not 0 <= cls < len(CLASS_NAMES):
            problems.append(f"{where} class id {cls} outside 0-{len(CLASS_NAMES) - 1}")
            continue
        if len(coords) < 6 or len(coords) % 2:
            problems.append(f"{where} needs an even number of coords and at least 3 points")
            continue
        if any(v < 0 or v > 1 for v in coords):
            # Slightly out-of-range points are common after export from labeling tools; clip them.
            if any(v < -0.01 or v > 1.01 for v in coords):
                problems.append(f"{where} coords outside [0, 1]")
                continue
            coords = [min(max(v, 0.0), 1.0) for v in coords]
        good.append(" ".join([str(cls), *(f"{v:.6f}" for v in coords)]))
    return good, problems


def collect(root: Path) -> list[tuple[Path, Path | None]]:
    """Pair each image with its label file (None when the label is missing)."""
    pairs = []
    img_dir, lbl_dir = root / "images", root / "labels"
    for img in sorted(img_dir.rglob("*")):
        if img.suffix.lower() not in IMG_EXTS:
            continue
        rel = img.relative_to(img_dir).with_suffix(".txt")
        lbl = lbl_dir / rel
        pairs.append((img, lbl if lbl.exists() else None))
    return pairs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", nargs="+", required=True, type=Path, help="dataset folders or zips")
    ap.add_argument("--out", type=Path, default=Path("datasets/robotaxi"))
    ap.add_argument("--val-frac", type=float, default=0.15)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--link", action="store_true", help="symlink images instead of copying")
    ap.add_argument("--strict", action="store_true", help="stop on any bad label line")
    args = ap.parse_args()

    out = args.out.resolve()
    if out.exists():
        sys.exit(f"{out} already exists. Remove it or pick another --out.")
    work = out.parent / f"_extract_{out.name}"

    pairs = []
    for src in args.src:
        root = find_root(unpack(src.resolve(), work))
        found = collect(root)
        print(f"{src}: {len(found)} images")
        pairs += [(src.stem, img, lbl) for img, lbl in found]
    if not pairs:
        sys.exit("No images found.")

    rng = random.Random(args.seed)
    order = list(range(len(pairs)))
    rng.shuffle(order)
    n_val = max(1, round(len(pairs) * args.val_frac))
    val_ids = set(order[:n_val])

    counts = {"train": Counter(), "val": Counter()}
    images = Counter()
    missing, problems, seen = 0, [], set()
    for i, (tag, img, lbl) in enumerate(pairs):
        split = "val" if i in val_ids else "train"
        # Prefix with the source name so files from different datasets never collide.
        stem = f"{tag}__{img.stem}" if len(args.src) > 1 else img.stem
        while stem in seen:
            stem += "_dup"
        seen.add(stem)

        if lbl is None:
            missing += 1
            lines = []
        else:
            lines, bad = check_label(lbl)
            problems += bad

        img_out = out / "images" / split / f"{stem}{img.suffix.lower()}"
        lbl_out = out / "labels" / split / f"{stem}.txt"
        img_out.parent.mkdir(parents=True, exist_ok=True)
        lbl_out.parent.mkdir(parents=True, exist_ok=True)
        if args.link:
            os.symlink(img, img_out)
        else:
            shutil.copy2(img, img_out)
        lbl_out.write_text("\n".join(lines) + ("\n" if lines else ""))
        images[split] += 1
        counts[split].update(int(line.split()[0]) for line in lines)

    if problems:
        print(f"\n{len(problems)} bad label lines were dropped. First 20:")
        for p in problems[:20]:
            print("  ", p)
        if args.strict:
            shutil.rmtree(out)
            sys.exit("Stopped because of --strict.")
    if missing:
        print(f"\n{missing} images had no label file; wrote empty labels (treated as background).")

    names = "\n".join(f"  {i}: {n}" for i, n in enumerate(CLASS_NAMES))
    (out / "data.yaml").write_text(
        f"path: {out}\ntrain: images/train\nval: images/val\n\nnames:\n{names}\n"
    )

    print(f"\nImages: train {images['train']}, val {images['val']}")
    print(f"{'id':>3} {'class':<14} {'train':>7} {'val':>7}")
    for i, n in enumerate(CLASS_NAMES):
        print(f"{i:>3} {n:<14} {counts['train'][i]:>7} {counts['val'][i]:>7}")
    print(f"\nWrote {out / 'data.yaml'}")


if __name__ == "__main__":
    main()
