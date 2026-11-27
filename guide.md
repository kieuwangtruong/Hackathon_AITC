# Chấm validation sau khi train RoboTaxi

## Chấm bằng notebook chung

Sau khi train xong và có `best.pt`, tiếp tục trong [notebook chung của đội](colab/shared.ipynb).

1. Chạy **Bước 4** để xuất ONNX, kiểm tra và tạo `submission.zip`.
2. Chạy **Bước 5** để chấm tập validation bằng mã chấm của BTC. Xem **mask mAP@[.50:.95]**, **AP và số đối tượng từng lớp**. Trong ảnh lỗi, bên trái là nhãn gốc, bên phải là dự đoán.
3. Chạy **Bước 6** để tạo `run_report.json`. Lưu báo cáo cùng `best.pt`, `submission.zip` và zip dữ liệu của vòng train.

## So sánh các vòng train

- Dùng cùng danh sách ảnh val đã tách theo camera hoặc video, cùng phiên bản nhãn, cùng `TEAM_ID = 48` và cùng `SELFCHECK_MAX_IMAGES`. Notebook mặc định chấm tối đa 300 ảnh val.
- Nếu sửa nhãn val, chấm lại cả checkpoint cũ và mới trên cùng phiên bản nhãn đã sửa.
- Dùng điểm val để so các vòng train. BTC tính điểm private trên tập test ẩn.

## Chấm nhanh trên máy

[`evaluate.py`](evaluate.py) chấm checkpoint `.pt` hoặc model `.onnx` và in mask mAP tổng cùng AP từng lớp. Dùng `data.yaml` trỏ tới đúng tập val của vòng đang so sánh.

```bash
python evaluate.py --model runs/segment/baseline/weights/best.pt --data splits/v1/data.yaml --split val
```
