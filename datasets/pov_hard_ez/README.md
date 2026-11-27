# pov_hard_ez (YOLO-seg)

Bộ 100 ảnh giao thông Việt Nam (50 `ez`, 50 `hard`) từ nguồn **Vietnam Traffic Signs - v1** (Roboflow, `CC BY 4.0`), đã chuyển đổi sang nhãn `yolo-seg` chuẩn 11 lớp (0–10) theo [docs/labeling-guideline-v1.md](../../docs/labeling-guideline-v1.md).

## Thống kê hiện tại

- **Số ảnh**: 100 (`640x640`, ban ngày, 41 nhóm cảnh trong `meta.csv`)
- **Tổng đối tượng**: 930 (`Car`: 131, `Bus`: 21, `Truck`: 15, `Other vehicle`: 16, `Motorcycle`: 20, `Motorcyclist`: 425, `Bicycle`: 3, `Cyclist`: 1, `Pedestrian`: 40, `Sign`: 199, `Traffic light`: 59)
- **Trạng thái duyệt**: 25 ảnh `REVIEWED_PENDING_FINAL_QA` (22 ảnh đã sửa chi tiết ở lượt `review_v2`), 75 ảnh còn lại ở mức `PENDING` (nhãn nháp đã kiểm tra cú pháp/hình học).
- **Lưu ý cho team train**:
  - `Cyclist` hiện có **1** mẫu và `Bicycle` có **3** mẫu — cần gộp thêm dữ liệu có `Cyclist`, `Bicycle`, và ảnh đêm/mưa trước khi train bản nộp cuối.
  - Mọi đa giác đã vượt qua `tools/check_labels.py` (0 lỗi), `verify_image_label` của Ultralytics (0 lỗi) và kiểm tra của `colab/shared.ipynb` (0 đa giác tự cắt, 0 đối tượng `< 64 px`).

## Cách kiểm tra, chia tập và đóng gói cho Colab

```bash
python tools/check_labels.py --images datasets/pov_hard_ez/images --labels datasets/pov_hard_ez/labels
python tools/split_dataset.py --images datasets/pov_hard_ez/images --labels datasets/pov_hard_ez/labels --meta datasets/pov_hard_ez/meta.csv --out splits/pov_hard_ez --seed 48
python tools/make_split_zip.py --split splits/pov_hard_ez --out du_lieu.zip
```

## Rà soát ngày 28/11/2026

Xem [báo cáo rà soát](../../docs/label-audit-2026-11-28.md) và danh sách ảnh/dòng nhãn cần kiểm tra. Đúng cú pháp YOLO-seg chưa đồng nghĩa đủ đối tượng hoặc đúng biên mask. Lượt này kiểm tra định dạng toàn bộ, xem crop theo rủi ro; không nâng trạng thái duyệt nội dung.
