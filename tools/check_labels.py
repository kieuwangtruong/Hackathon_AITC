#!/usr/bin/env python3
"""Kiểm tra nhãn YOLO-seg: id 0-10, tọa độ trong [0, 1], mỗi ảnh có một .txt.

    python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
"""
import argparse
import collections
import json
import math
import pathlib
import sys

NUM_CLASSES = 11
NAMES = ["Car", "Bus", "Truck", "Other vehicle", "Motorcycle", "Motorcyclist",
         "Bicycle", "Cyclist", "Pedestrian", "Sign", "Traffic light"]
IMG_EXTS = {".jpg", ".jpeg", ".png"}


def polygon_area(xs, ys):
    return 0.5 * abs(sum(xs[i] * ys[i - 1] - xs[i - 1] * ys[i] for i in range(len(xs))))


def polygon_crosses(points):
    """Proper edge crossings, as in the official notebook, without its 400-point skip.

    A retraced bridge connecting mask islands is not a proper crossing. Such paths
    are reported separately; do not silently replace masks by their convex hull.
    """
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    n = len(points)
    for i, a in enumerate(points):
        b = points[(i + 1) % n]
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            c, d = points[j], points[(j + 1) % n]
            if (max(a[0], b[0]) < min(c[0], d[0]) or max(c[0], d[0]) < min(a[0], b[0])
                    or max(a[1], b[1]) < min(c[1], d[1]) or max(c[1], d[1]) < min(a[1], b[1])):
                continue
            if orient(a, b, c) * orient(a, b, d) < 0 and orient(c, d, a) * orient(c, d, b) < 0:
                return True
    return False


def check_file(path):
    errors, warnings, classes = [], [], []
    for n, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
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
        if not all(math.isfinite(c) for c in coords):
            errors.append(f"{where}: non-finite coordinate (NaN/Inf)")
            continue
        if any(c < 0 or c > 1 for c in coords):
            errors.append(f"{where}: coordinate outside [0, 1]")
            continue
        xs, ys = coords[0::2], coords[1::2]
        points = list(zip(xs, ys))
        if len(set(points)) < 3:
            errors.append(f"{where}: fewer than 3 distinct points")
            continue
        if polygon_crosses(points):
            errors.append(f"{where}: polygon edges cross (self-intersection)")
            continue
        ring = points[:-1] if points[0] == points[-1] else points
        if len(set(ring)) != len(ring):
            warnings.append(f"{where}: repeated vertices / retraced mask bridge; inspect topology")
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
    ap.add_argument("--report", type=pathlib.Path, help="write validation details as JSON")
    args = ap.parse_args()

    images = {p.relative_to(args.images).with_suffix("").as_posix(): p
              for p in args.images.rglob("*") if p.is_file() and p.suffix.lower() in IMG_EXTS}
    labels = {p.relative_to(args.labels).with_suffix("").as_posix(): p for p in args.labels.rglob("*.txt")}
    errors, warnings = [], []
    if not images:
        errors.append(f"no images under {args.images}")
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
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(dict(images=len(images), labels=len(labels), empty=empty,
            instances={name: counts[i] for i, name in enumerate(NAMES)}, errors=errors,
            warnings=warnings), indent=2), encoding="utf-8")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
