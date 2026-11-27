"""Train nhanh trên máy: yolo26n-seg, imgsz 640, seed 48.

    python train.py --data splits/v1/data.yaml --epochs 100
    python train.py --data splits/v1/data.yaml --hyp configs/hyp.yaml --name aug
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ultralytics import YOLO
from ultralytics.utils import YAML

MODEL = "yolo26n-seg.pt"  # pretrained COCO weights, fixed by the competition
IMGSZ = 640  # fixed by the competition


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="path to data.yaml")
    ap.add_argument("--epochs", type=int, default=100)
    ap.add_argument("--batch", type=int, default=16, help="-1 picks the largest batch that fits on the GPU")
    ap.add_argument("--device", default=None, help="0, 0,1, cpu or mps; default picks automatically")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--patience", type=int, default=30, help="stop after this many epochs without improvement")
    ap.add_argument("--seed", type=int, default=48, help="our TEAM_ID from the organizers")
    ap.add_argument("--project", default="runs/segment")
    ap.add_argument("--name", default="baseline")
    ap.add_argument("--hyp", type=Path, help="YAML of extra Ultralytics train args (augmentation, lr, ...)")
    ap.add_argument("--cache", default=False, help="ram or disk to cache images")
    ap.add_argument("--fraction", type=float, default=1.0, help="train on this share of the train split")
    ap.add_argument("--resume", type=Path, help="last.pt of an interrupted run")
    args = ap.parse_args()

    if args.resume:
        YOLO(str(args.resume)).train(resume=True)
        return

    extra = YAML.load(args.hyp) if args.hyp else {}
    for fixed in ("model", "imgsz", "data"):
        if fixed in (extra or {}):
            raise SystemExit(f"--hyp may not set '{fixed}'.")

    model = YOLO(MODEL)
    model.train(
        data=args.data,
        imgsz=IMGSZ,
        epochs=args.epochs,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        patience=args.patience,
        seed=args.seed,
        deterministic=True,
        project=str(Path(args.project).resolve()),  # relative paths get nested under runs_dir otherwise
        name=args.name,
        exist_ok=False,
        cache=args.cache,
        fraction=args.fraction,
        plots=True,
        **(extra or {}),
    )

    save_dir = Path(model.trainer.save_dir)
    best = save_dir / "weights" / "best.pt"
    # Square inputs, same as the exported ONNX, so this matches evaluate.py on model.onnx.
    metrics = YOLO(str(best)).val(data=args.data, imgsz=IMGSZ, rect=False, device=args.device, plots=False)
    summary = {
        "weights": str(best),
        "mask_mAP50-95": float(metrics.seg.map),
        "mask_mAP50": float(metrics.seg.map50),
        "box_mAP50-95": float(metrics.box.map),
        "per_class_mask_mAP50-95": {metrics.names[int(c)]: float(metrics.seg.maps[int(c)]) for c in metrics.ap_class_index},
    }
    (save_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"\nNext: python export.py --weights {best}")


if __name__ == "__main__":
    main()
