"""Score a .pt or exported .onnx model on our validation split.

Use this to compare dataset versions locally before spending one of the 20
submissions, and to confirm the ONNX scores the same as the .pt it came from.
Our val split is not the private test set, so treat the number as a relative
signal between our own runs.

Example:
    python evaluate.py --model runs/segment/baseline/weights/best.pt --data datasets/robotaxi/data.yaml
    python evaluate.py --model submission/model.onnx --data datasets/robotaxi/data.yaml
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
