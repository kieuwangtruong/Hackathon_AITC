# Hackathon_AITC

Cuộc thi RoboTaxi: phân đoạn 11 lớp trong ảnh giao thông VN. Mô hình cố định (`yolo26n-seg`, 640), đội chỉ cải thiện **dữ liệu**.

- **Hạn nộp: 10:30 ngày 28/11.** Máy chấm xếp hàng, đừng nộp sát giờ.
- **Đội 43. TEAM_ID (seed): 48.** Điểm = 100 × mask mAP@[.5:.95].
- Bài nộp phải tạo bằng notebook chính thức.

## Làm thế nào

1. Gán nhãn theo [hướng dẫn gán nhãn](docs/labeling-guideline-v1.md).
2. Kiểm tra, chia train/val theo camera, đóng zip:
   ```bash
   pip install -r requirements.txt
   python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
   python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels --out splits/v1
   python tools/make_split_zip.py --split splits/v1 --out du_lieu.zip
   ```
3. Tải `du_lieu.zip` lên Drive: `MyDrive/Hackathon_AITC/datasets/du_lieu.zip`.
4. Mở [notebook chung](https://colab.research.google.com/github/kieuwangtruong/Hackathon_AITC/blob/main/colab/shared.ipynb), chọn T4 GPU, **Run all**.
5. Nộp `submission.zip` trong `MyDrive/Hackathon_AITC/ket_qua/`.

## Tài liệu

- [docs/labeling-guideline-v1.md](docs/labeling-guideline-v1.md): 11 lớp, quy tắc vẽ mask, ca dễ nhầm, quy trình SAM 3.
- [docs/dataset_plan.md](docs/dataset_plan.md): cách chia val, dữ liệu công khai.
- [colab/README.md](colab/README.md): cách dùng notebook chung.
- [guide.md](guide.md) hướng dẫn chấm validation sau khi train.
- [Rà soát nhãn 28/11/2026](docs/label-audit-2026-11-28.md): kiểm tra 150 ảnh, danh sách mask cần QA và hạn chế của tập validation.

## Công cụ

| File | Dùng để |
| --- | --- |
| `tools/check_labels.py` | Kiểm tra nhãn |
| `tools/split_dataset.py` | Chia train/val theo camera |
| `tools/make_split_zip.py` | Đóng zip cho notebook |
| `train.py` | Huấn luyện trên máy |
| `predict.py` | Tạo nhãn nháp từ model |
| `export.py` | Xuất ONNX để thử (bản nộp thật dùng notebook) |

## Quy trình Git

1. `git switch -c feat/<tên>/<việc> origin/main`
2. Commit, push, mở PR vào `main`.
3. Check **Validate pull request** xanh thì merge. `main` đã khóa, không push thẳng được.

Không commit dữ liệu, `runs/`, `.pt`, `.onnx`, `.zip`.

## Báo cáo

Ghi lại mọi bộ dữ liệu công khai đã dùng: tên, link, giấy phép, số ảnh, cách ánh xạ về 11 lớp.
