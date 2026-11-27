#!/usr/bin/env python3
"""Kiểm tra nhãn YOLO-seg: id 0-10, tọa độ trong [0, 1], mỗi ảnh có một .txt.

    python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
"""
import argparse
import collections
import pathlib
import sys

NUM_CLASSES = 11
NAMES = ["Car", "Bus", "Truck", "Other vehicle", "Motorcycle", "Motorcyclist",
         "Bicycle", "Cyclist", "Pedestrian", "Sign", "Traffic light"]
IMG_EXTS = {".jpg", ".jpeg", ".png"}


def polygon_area(xs, ys):
    return 0.5 * abs(sum(xs[i] * ys[i - 1] - xs[i - 1] * ys[i] for i in range(len(xs))))


def check_file(path):
    errors, warnings, classes = [], [], []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        parts = line.split()
        if not parts:
            continue
        where = f"{path}:{n}"
        try:
            cls = int(parts[0])
            coords = [float(v) for v in parts[1:]]
        except ValueError:
            errors.append(f"{where}: non-numeric value")
            continue
        if not 0 <= cls < NUM_CLASSES:
            errors.append(f"{where}: class id {cls} outside 0..{NUM_CLASSES - 1}")
            continue
        if len(coords) < 6 or len(coords) % 2:
            errors.append(f"{where}: need an even number of coords and at least 3 points "
                          f"(got {len(coords)}); boxes are not accepted")
            continue
        if any(c < 0 or c > 1 for c in coords):
            errors.append(f"{where}: coordinate outside [0, 1]")
            continue
        xs, ys = coords[0::2], coords[1::2]
        if polygon_area(xs, ys) < 1e-6:
            warnings.append(f"{where}: near-zero polygon area")
        if len(coords) == 8 and len(set(xs)) == 2 and len(set(ys)) == 2:
            warnings.append(f"{where}: polygon is an axis-aligned rectangle (a box, not a mask?)")
        classes.append(cls)
    return errors, warnings, classes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True, type=pathlib.Path)
    ap.add_argument("--labels", required=True, type=pathlib.Path)
    ap.add_argument("--max-print", type=int, default=30)
    args = ap.parse_args()

    images = {p.stem: p for p in args.images.rglob("*") if p.suffix.lower() in IMG_EXTS}
    labels = {p.stem: p for p in args.labels.rglob("*.txt")}
    errors, warnings = [], []
    errors += [f"missing label for image {images[s]} (use an empty .txt for no objects)"
               for s in sorted(images.keys() - labels.keys())]
    warnings += [f"label without image: {labels[s]}" for s in sorted(labels.keys() - images.keys())]

    counts, empty = collections.Counter(), 0
    for stem in sorted(labels.keys() & images.keys()):
        e, w, c = check_file(labels[stem])
        errors += e
        warnings += w
        counts.update(c)
        empty += not c

    print(f"images: {len(images)}  labels: {len(labels)}  empty label files: {empty}")
    print(f"{'id':>3}  {'class':<14}{'instances':>10}")
    for i, name in enumerate(NAMES):
        print(f"{i:>3}  {name:<14}{counts[i]:>10}")
    for title, items in (("WARNINGS", warnings), ("ERRORS", errors)):
        if items:
            print(f"\n{title} ({len(items)}):")
            for msg in items[: args.max_print]:
                print("  " + msg)
            if len(items) > args.max_print:
                print(f"  ... {len(items) - args.max_print} more")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
