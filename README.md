# Hackathon_AITC

Cuộc thi RoboTaxi data-centric: mô hình cố định `yolo26n-seg`, `imgsz=640`. Nhóm chỉ cải thiện **dữ liệu**.

## Bắt đầu nhanh

**Trên Colab (khuyên dùng):** mở [notebook dùng chung](https://colab.research.google.com/github/kieuwangtruong/Hackathon_AITC/blob/main/colab/shared.ipynb), chọn GPU, rồi chạy lần lượt các ô. Xem [colab/README.md](colab/README.md).

**Trên máy:**

```bash
pip install -r requirements.txt
python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels --out splits/v1
python train.py --data splits/v1/data.yaml --epochs 100
python export.py --weights runs/segment/baseline/weights/best.pt       # -> submission/*.zip
python evaluate.py --model submission/model.onnx --data splits/v1/data.yaml
```

## Trong repo có gì

| File | Dùng để |
| --- | --- |
| `tools/check_labels.py` | Kiểm tra nhãn đúng định dạng YOLO-seg |
| `tools/split_dataset.py` | Chia train/val theo camera/địa điểm |
| `train.py` | Train (thêm augmentation qua `--hyp configs/hyp.yaml`) |
| `export.py` | Tạo file zip nộp bài (`model.onnx` fp32, tối đa 42 MB) |
| `evaluate.py` | Chấm `.pt`/`.onnx` trên val trước khi tốn lượt nộp |
| `predict.py` | Tạo nhãn nháp từ model để người sửa lại |
| `scripts/prepare_data.py` | Chia ngẫu nhiên nhanh (chỉ khi không có thông tin camera) |
| [docs/dataset_plan.md](docs/dataset_plan.md) | Quy tắc gán nhãn, cách chia val, dữ liệu công khai |

Không commit dữ liệu, `runs/`, `.pt`, `.onnx`, `.zip` (đã có trong `.gitignore`).

## Quy trình làm việc

1. Tạo nhánh từ `main`: `git switch -c feat/<tên>/<việc> origin/main`.
2. Commit, `git push -u origin feat/<tên>/<việc>`, mở PR vào `main`.
3. Đợi check **Validate pull request** xanh rồi merge. Notebook Colab tự cập nhật theo `main`.

Chốt phiên bản: `git tag -a v0.1.0 -m "v0.1.0" origin/main && git push origin v0.1.0` (bản zip mã nguồn xuất hiện ở **Releases**).

**Chủ repo cần làm một lần:** Settings → Rules → Rulesets → Import a ruleset → chọn [.github/rulesets/protect-main.json](.github/rulesets/protect-main.json). Sau đó không ai push thẳng vào `main` được.

## Lưu ý

- `export.py` đang dùng tham số mặc định. Khi có notebook mẫu của BTC, chép đúng lời gọi `model.export(...)` của họ vào.
- Điểm val chỉ để so sánh các phiên bản dữ liệu với nhau, không phải điểm private.
- Mỗi bộ dữ liệu công khai đã dùng phải ghi vào báo cáo: tên, link, giấy phép, số ảnh, cách ánh xạ 11 lớp.
