"""Chạy model trên ảnh, lưu ảnh có mask và nhãn YOLO-seg để làm nhãn nháp.

    python predict.py --model runs/segment/baseline/weights/best.pt --source anh/
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO

IMGSZ = 640


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help=".pt or .onnx")
    ap.add_argument("--source", required=True, help="image, folder, video or glob")
    ap.add_argument("--conf", type=float, default=0.25)
    ap.add_argument("--iou", type=float, default=0.7)
    ap.add_argument("--device", default=None)
    ap.add_argument("--project", default="runs/predict")
    ap.add_argument("--name", default="pred")
    ap.add_argument("--no-images", action="store_true", help="only write label files")
    args = ap.parse_args()

    model = YOLO(args.model, task="segment")
    n = 0
    for _ in model.predict(
        source=args.source,
        imgsz=IMGSZ,
        conf=args.conf,
        iou=args.iou,
        device=args.device,
        project=str(Path(args.project).resolve()),  # relative paths get nested under runs_dir otherwise
        name=args.name,
        save=not args.no_images,
        save_txt=True,
        save_conf=False,  # keep label files in plain training format
        stream=True,
        verbose=False,
    ):
        n += 1
    print(f"Predicted {n} images. Results in {args.project}/{args.name}/")


if __name__ == "__main__":
    main()
