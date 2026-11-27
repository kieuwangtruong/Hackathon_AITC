#!/usr/bin/env python3
"""Pack a split from tools/split_dataset.py into a zip the official notebook accepts.

The official notebook (colab/shared.ipynb) uses a pre-made split as is when the
zip holds images/train, images/val, labels/train and labels/val. Without that it
shuffles images randomly by seed, which leaks frames of the same video into val.

Usage:
    python tools/make_split_zip.py --split splits/v1 --out du_lieu_v1.zip
Then upload the zip to Drive and set DATASET_PATH in the notebook to it.
"""
import argparse
import pathlib
import sys
import zipfile


def label_of(img):
    """images/.../x.jpg -> labels/.../x.txt (same rule as Ultralytics and the notebook)."""
    parts = list(img.parts)
    if "images" not in parts:
        return img.with_suffix(".txt")
    i = len(parts) - 1 - parts[::-1].index("images")
    parts[i] = "labels"
    return pathlib.Path(*parts).with_suffix(".txt")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, type=pathlib.Path, help="folder with train.txt and val.txt")
    ap.add_argument("--out", required=True, type=pathlib.Path, help="zip to write")
    args = ap.parse_args()

    seen = set()
    counts = {}
    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in ("train", "val"):
            lst = args.split / f"{name}.txt"
            if not lst.exists():
                sys.exit(f"Missing {lst}. Run tools/split_dataset.py first.")
            imgs = [pathlib.Path(line.strip()) for line in lst.read_text().splitlines() if line.strip()]
            for img in imgs:
                stem = img.stem
                while (name, stem) in seen:  # same file name from different folders
                    stem += "_1"
                seen.add((name, stem))
                zf.write(img, f"images/{name}/{stem}{img.suffix.lower()}")
                lbl = label_of(img)
                zf.writestr(f"labels/{name}/{stem}.txt", lbl.read_text() if lbl.exists() else "")
            counts[name] = len(imgs)
    size_mb = args.out.stat().st_size / 1024**2
    print(f"Wrote {args.out} ({size_mb:.1f} MB): train {counts['train']} images, val {counts['val']} images")


if __name__ == "__main__":
    main()
