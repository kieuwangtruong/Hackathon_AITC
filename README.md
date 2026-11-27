# Hackathon_AITC

Cuộc thi RoboTaxi data-centric: mô hình cố định `yolo26n-seg`, `imgsz=640`. Nhóm chỉ cải thiện **dữ liệu**.

- **Hạn nộp: 10:30 ngày 28/11.** Bảng private công bố 11:00, thuyết trình từ 11:30. Hàng đợi chấm chạy lần lượt, nên đừng nộp sát giờ.
- **TEAM_ID (seed) của đội: 48.** Điểm = 100 × mask mAP@[.5:.95].
- Bài nộp chính thức phải tạo bằng **notebook mẫu của BTC** (Bước 4: xuất ONNX, kiểm tra, đóng zip). Giữ lại notebook, dữ liệu và `run_report.json`.

## Bắt đầu nhanh

1. Gán nhãn, rồi kiểm tra và chia train/val theo camera:
   ```bash
   pip install -r requirements.txt
   python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
   python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels --out splits/v1
   python tools/make_split_zip.py --split splits/v1 --out du_lieu.zip
   ```
2. Tải `du_lieu.zip` lên Drive: `MyDrive/Hackathon_AITC/datasets/du_lieu.zip`.
3. Mở [notebook chính thức của đội](https://colab.research.google.com/github/kieuwangtruong/Hackathon_AITC/blob/main/colab/shared.ipynb) (đã điền TEAM_ID 48), chọn GPU T4, **Run all**.
4. Nộp `submission.zip` trong `MyDrive/Hackathon_AITC/ket_qua/`. Giữ lại `run_report.json`.

## Trong repo có gì

| File | Dùng để |
| --- | --- |
| `tools/check_labels.py` | Kiểm tra nhãn đúng định dạng YOLO-seg |
| `tools/split_dataset.py` | Chia train/val theo camera/địa điểm |
| `tools/make_split_zip.py` | Đóng zip train/val để notebook chính thức dùng nguyên cách chia |
| `train.py` | Train nhanh trên máy (thêm augmentation qua `--hyp configs/hyp.yaml`) |
| `export.py` | Xuất ONNX để thử nhanh, cùng tham số với BTC |
| `evaluate.py` | Chấm nhanh `.pt`/`.onnx` trên val |
| `predict.py` | Tạo nhãn nháp từ model để người sửa lại |
| `scripts/prepare_data.py` | Chia ngẫu nhiên nhanh (chỉ khi không có thông tin camera) |
| [docs/dataset_plan.md](docs/dataset_plan.md) | Quy tắc gán nhãn, cách chia val, dữ liệu công khai |

Không commit dữ liệu, `runs/`, `.pt`, `.onnx`, `.zip` (đã có trong `.gitignore`).

## Quy trình làm việc

1. Tạo nhánh từ `main`: `git switch -c feat/<tên>/<việc> origin/main`.
2. Commit, `git push -u origin feat/<tên>/<việc>`, mở PR vào `main`.
3. Đợi check **Validate pull request** xanh rồi merge. Notebook Colab tự cập nhật theo `main`.

Chốt phiên bản: `git tag -a v0.1.0 -m "v0.1.0" origin/main && git push origin v0.1.0` (bản zip mã nguồn xuất hiện ở **Releases**).

`main` đã được bảo vệ bằng [ruleset](.github/rulesets/protect-main.json): không ai push thẳng được, mọi thay đổi phải qua PR.

## Lưu ý

- `export.py` chỉ để thử nhanh. Bản nộp thật phải làm bằng notebook mẫu của BTC.
- Điểm val chỉ để so sánh các phiên bản dữ liệu với nhau, không phải điểm private.
- Mỗi bộ dữ liệu công khai đã dùng phải ghi vào báo cáo: tên, link, giấy phép, số ảnh, cách ánh xạ 11 lớp.
