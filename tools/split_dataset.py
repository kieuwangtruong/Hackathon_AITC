#!/usr/bin/env python3
"""Make a train/val split that holds out whole cameras/locations, balanced by time of day.

The private test set is presumably shot on cameras, streets and times we never see. A random
split leaks near-identical neighbouring frames into val and overstates the score, so this
script splits by *group* instead:

  1. Group key per image, first match wins:
       a. `group` column in --meta, else `camera`, else `location`
       b. filename prefix with the trailing frame number removed
          (e.g. `hcm_cam03_000123.jpg` -> `hcm_cam03`)
     Groups that contain near-duplicate images (perceptual hash) are then merged, so the same
     scene cannot sit on both sides.
  2. Condition per image: `time_of_day` / `weather` columns from --meta, else a brightness
     guess (dark -> night, otherwise day). Weather is never guessed.
  3. Whole groups go to val, picked per condition stratum until each stratum holds about
     --val-frac of its images.

Outputs in --out: train.txt, val.txt (absolute image paths), data.yaml, split_report.json.
Ultralytics reads the .txt lists directly and finds labels by swapping /images/ for /labels/.

Usage:
    python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels \
        --out splits/v1 [--meta datasets/v1/meta.csv] [--val-frac 0.2] [--seed 0]

--meta is an optional CSV with a `file` column (image file name) plus any of:
group, camera, location, time_of_day (day/dusk/night), weather (clear/rain/...), source.
"""
import argparse
import collections
import csv
import json
import pathlib
import random
import re

import numpy as np
from PIL import Image

NAMES = ["Car", "Bus", "Truck", "Other vehicle", "Motorcycle", "Motorcyclist",
         "Bicycle", "Cyclist", "Pedestrian", "Sign", "Traffic light"]
IMG_EXTS = {".jpg", ".jpeg", ".png"}
NIGHT_BRIGHTNESS = 70  # GUESS: mean grey level below this counts as night; tune on real data


def load_meta(path):
    if not path:
        return {}
    with open(path, newline="", encoding="utf-8") as f:
        return {pathlib.Path(r["file"]).name: r for r in csv.DictReader(f)}


def prefix_group(stem):
    group = re.sub(r"[_\-. ]*(frame)?\d+$", "", stem, flags=re.I)
    return group or stem


def image_stats(path):
    """Return (64-bit difference hash, mean brightness) from a small greyscale thumbnail."""
    with Image.open(path) as im:
        grey = im.convert("L")
        brightness = float(np.asarray(grey.resize((64, 64))).mean())
        px = np.asarray(grey.resize((9, 8)), dtype=np.int16)
    bits = (px[:, 1:] > px[:, :-1]).flatten()
    return int("".join("1" if b else "0" for b in bits), 2), brightness


class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        self.parent[self.find(a)] = self.find(b)


def merge_near_duplicates(hashes, group_of, max_dist):
    """Merge groups that share images whose dHash differs by <= max_dist bits."""
    uf = UnionFind()
    for g in set(group_of.values()):
        uf.find(g)
    if max_dist < 0:
        return {k: uf.find(g) for k, g in group_of.items()}
    keys = list(hashes)
    arr = np.array([hashes[k] for k in keys], dtype=np.uint64)
    for i in range(len(keys)):
        x = np.bitwise_xor(arr[i + 1:], arr[i])
        dist = np.unpackbits(x.view(np.uint8).reshape(-1, 8), axis=1).sum(axis=1)
        for j in np.nonzero(dist <= max_dist)[0]:
            uf.union(group_of[keys[i]], group_of[keys[i + 1 + j]])
    return {k: uf.find(g) for k, g in group_of.items()}


def class_counts(label_path):
    c = collections.Counter()
    if label_path.exists():
        for line in label_path.read_text().splitlines():
            if line.strip():
                c[int(line.split()[0])] += 1
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--images", required=True, type=pathlib.Path)
    ap.add_argument("--labels", required=True, type=pathlib.Path)
    ap.add_argument("--out", required=True, type=pathlib.Path)
    ap.add_argument("--meta", type=pathlib.Path)
    ap.add_argument("--val-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dup-dist", type=int, default=4,
                    help="max dHash bit distance to treat two images as the same scene; -1 disables")
    ap.add_argument("--force-train", default="",
                    help="comma-separated `source` values from --meta that always go to train "
                         "(e.g. public datasets you only want to train on)")
    args = ap.parse_args()

    meta = load_meta(args.meta)
    force_train = {s for s in args.force_train.split(",") if s}
    images = sorted(p for p in args.images.rglob("*") if p.suffix.lower() in IMG_EXTS)
    if not images:
        raise SystemExit(f"no images under {args.images}")

    group_of, cond_of, hashes, labels_of, pinned = {}, {}, {}, {}, set()
    for p in images:
        m = meta.get(p.name, {})
        h, bright = image_stats(p)
        hashes[p] = h
        group_of[p] = (m.get("group") or m.get("camera") or m.get("location")
                       or prefix_group(p.stem))
        tod = (m.get("time_of_day") or ("night" if bright < NIGHT_BRIGHTNESS else "day")).lower()
        weather = (m.get("weather") or "").lower()
        cond_of[p] = f"{tod}/{weather}" if weather else tod
        rel = p.relative_to(args.images).with_suffix(".txt")
        labels_of[p] = class_counts(args.labels / rel)
        if m.get("source") in force_train:
            pinned.add(p)

    group_of = merge_near_duplicates(hashes, group_of, args.dup_dist)
    groups = collections.defaultdict(list)
    for p, g in group_of.items():
        groups[g].append(p)

    # Each group is assigned to the stratum most of its images fall in.
    stratum_of = {g: collections.Counter(cond_of[p] for p in ps).most_common(1)[0][0]
                  for g, ps in groups.items()}
    rng = random.Random(args.seed)
    val_groups = set()
    for stratum in sorted(set(stratum_of.values())):
        cands = [g for g in groups if stratum_of[g] == stratum
                 and not any(p in pinned for p in groups[g])]
        total = sum(len(groups[g]) for g in groups if stratum_of[g] == stratum)
        target = args.val_frac * total
        rng.shuffle(cands)
        taken = 0
        for g in cands:
            # Stop when adding this group overshoots more than stopping short would.
            if taken >= target or abs(taken + len(groups[g]) - target) > abs(taken - target):
                continue
            val_groups.add(g)
            taken += len(groups[g])

    split = {p: ("val" if group_of[p] in val_groups else "train") for p in images}
    args.out.mkdir(parents=True, exist_ok=True)
    for name in ("train", "val"):
        (args.out / f"{name}.txt").write_text(
            "".join(f"{p.resolve()}\n" for p in images if split[p] == name))

    yaml = (args.out / "data.yaml")
    yaml.write_text(f"path: {args.out.resolve()}\ntrain: train.txt\nval: val.txt\nnames:\n"
                    + "".join(f"  {i}: {n}\n" for i, n in enumerate(NAMES)))

    report = {"seed": args.seed, "val_frac_target": args.val_frac, "splits": {}}
    for name in ("train", "val"):
        ps = [p for p in images if split[p] == name]
        cls = sum((labels_of[p] for p in ps), collections.Counter())
        report["splits"][name] = {
            "images": len(ps),
            "groups": len({group_of[p] for p in ps}),
            "conditions": dict(collections.Counter(cond_of[p] for p in ps)),
            "instances": {NAMES[i]: cls[i] for i in range(len(NAMES))},
        }
    report["val_groups"] = sorted(val_groups)
    (args.out / "split_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))

    for name, r in report["splits"].items():
        print(f"{name}: {r['images']} images in {r['groups']} groups, conditions {r['conditions']}")
    missing = [n for n, c in report["splits"]["val"]["instances"].items() if c == 0]
    if missing:
        print(f"WARNING: no val instances for {missing}; val score for those classes is meaningless")
    print(f"wrote {args.out}/train.txt, val.txt, data.yaml, split_report.json")


if __name__ == "__main__":
    main()
