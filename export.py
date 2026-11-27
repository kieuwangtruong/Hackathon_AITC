"""Xuất ONNX và đóng zip để thử nhanh, cùng tham số với BTC.

Bản nộp thật phải tạo bằng Bước 4 của notebook chính thức (colab/shared.ipynb).

    python export.py --weights runs/segment/baseline/weights/best.pt
"""

from __future__ import annotations

import argparse
import shutil
import zipfile
from pathlib import Path

import numpy as np
from ultralytics import YOLO

IMGSZ = 640
MAX_ZIP_MB = 42


def check_onnx(path: Path) -> None:
    import onnx
    import onnxruntime as ort

    onnx.checker.check_model(str(path))
    sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inp = sess.get_inputs()[0]
    print(f"input  {inp.name} {inp.shape} {inp.type}")
    if inp.type != "tensor(float)":
        raise SystemExit("Model input is not fp32.")
    if list(inp.shape[2:]) != [IMGSZ, IMGSZ]:
        raise SystemExit(f"Model input is not {IMGSZ}x{IMGSZ}.")
    outs = sess.run(None, {inp.name: np.zeros((1, 3, IMGSZ, IMGSZ), np.float32)})
    for meta, arr in zip(sess.get_outputs(), outs):
        print(f"output {meta.name} {list(arr.shape)} {arr.dtype}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--weights", required=True, type=Path, help="best.pt from train.py")
    ap.add_argument("--out", type=Path, default=Path("submission"), help="folder for model.onnx and the zip")
    ap.add_argument("--zip-name", default=None, help="default: <run name>.zip")
    args = ap.parse_args()

    model = YOLO(str(args.weights))
    if model.task != "segment":
        raise SystemExit(f"{args.weights} is a {model.task} model, expected segment.")
    # Exact call from the organizers' EXPORT_CONTRACT. Never pass nms (True or False changes the output head).
    exported = Path(model.export(format="onnx", imgsz=IMGSZ, opset=17, simplify=True, dynamic=False, half=False, batch=1))

    args.out.mkdir(parents=True, exist_ok=True)
    onnx_path = args.out / "model.onnx"
    shutil.copy2(exported, onnx_path)
    check_onnx(onnx_path)

    run_name = args.weights.resolve().parent.parent.name
    zip_path = args.out / (args.zip_name or f"{run_name}.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(onnx_path, arcname="model.onnx")

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    size_mb = zip_path.stat().st_size / 1024**2
    if names != ["model.onnx"]:
        raise SystemExit(f"Zip should hold only model.onnx, has {names}")
    if size_mb > MAX_ZIP_MB:
        raise SystemExit(f"Zip is {size_mb:.1f} MB, over the {MAX_ZIP_MB} MB limit.")
    print(f"\nSubmission ready: {zip_path} ({size_mb:.1f} MB, contains {names})")


if __name__ == "__main__":
    main()
