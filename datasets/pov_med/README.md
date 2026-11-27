# pov_med (YOLO-seg)

Bộ 50 ảnh giao thông Việt Nam (tầng `med`) từ nguồn **Vietnam Traffic Signs - v1** (Roboflow, `CC BY 4.0`), đã gán nhãn `yolo-seg` chuẩn 11 lớp (0–10) theo [docs/labeling-guideline-v1.md](../../docs/labeling-guideline-v1.md).

## Thống kê hiện tại

- **Số ảnh**: 50 (`640x640`, ban ngày, 25 nhóm cảnh trong `meta.csv`)
- **Tổng đối tượng**: 844 (`Car`: 130, `Bus`: 12, `Truck`: 21, `Other vehicle`: 20, `Motorcycle`: 17, `Motorcyclist`: 321, `Bicycle`: 1, `Cyclist`: 0, `Pedestrian`: 21, `Sign`: 275, `Traffic light`: 26)
- **Trạng thái duyệt**: 50 ảnh ở mức nhãn nháp thủ công (`PENDING_CVAT_QA`), có 82 đối tượng gắn cờ cần kiểm tra lại trên CVAT (biên polygon cần tinh chỉnh thêm nếu dùng trực tiếp cho bản nộp cuối).
- **Lưu ý cho team train**:
  - `Cyclist` hiện có **0** mẫu và `Bicycle` có **1** mẫu — nên gộp chung với `pov_hard_ez` và bổ sung thêm dữ liệu có `Cyclist`, `Bicycle`, ảnh đêm/mưa.
  - Đã bỏ qua các mảnh không nhận diện được / phần xe của người quay ở mép ảnh và các bảng tuyên truyền ven đường.
  - Mọi đa giác đã vượt qua `tools/check_labels.py` (**0 lỗi, 0 cảnh báo**).

## Cách kiểm tra, chia tập và đóng gói cho Colab

```bash
python tools/check_labels.py --images datasets/pov_med/images --labels datasets/pov_med/labels
python tools/split_dataset.py --images datasets/pov_med/images --labels datasets/pov_med/labels --meta datasets/pov_med/meta.csv --out splits/pov_med --seed 48
python tools/make_split_zip.py --split splits/pov_med --out du_lieu.zip
```
