"""Chấm nhanh một model .pt hoặc .onnx trên tập val (mask mAP, từng lớp).

    python evaluate.py --model submission/model.onnx --data splits/v1/data.yaml
"""

from __future__ import annotations

import argparse
import json

from ultralytics import YOLO

IMGSZ = 640


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--split", default="val", choices=["train", "val", "test"])
    ap.add_argument("--device", default=None)
    ap.add_argument("--batch", type=int, default=16)
    args = ap.parse_args()

    # ONNX models are exported with a static batch of 1.
    batch = 1 if args.model.endswith(".onnx") else args.batch
    m = YOLO(args.model, task="segment")
    # rect=False feeds square 640x640 inputs like the ONNX model gets, so .pt and
    # .onnx scores of the same weights match (rect batches score differently).
    r = m.val(
        data=args.data, split=args.split, imgsz=IMGSZ, batch=batch, rect=False, device=args.device, plots=False
    )

    per_class = {r.names[int(c)]: round(float(r.seg.maps[int(c)]), 4) for c in r.ap_class_index}
    print(json.dumps({
        "model": args.model,
        "mask_mAP50-95": round(float(r.seg.map), 4),
        "mask_mAP50": round(float(r.seg.map50), 4),
        "box_mAP50-95": round(float(r.box.map), 4),
        "per_class_mask_mAP50-95": per_class,
    }, indent=2))


if __name__ == "__main__":
    main()
