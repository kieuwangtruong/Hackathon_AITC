# Kế hoạch dữ liệu

Cách gán nhãn: xem [hướng dẫn gán nhãn](labeling-guideline-v1.md). Mục **(đoán)** là giả định chưa được BTC xác nhận.

## Chia train/val

- Val **chỉ có ảnh Việt Nam**. Dữ liệu nước ngoài chỉ cho vào train (`--force-train`).
- Tách **theo camera/video**, không tách từng frame, để val không có ảnh gần giống train.
- Khoảng 20% ảnh vào val, cân bằng ngày/đêm. Nên có 300-600 ảnh val từ 8-10 nhóm trở lên **(đoán)**.
- **Giữ nguyên tập val** giữa các vòng để điểm so sánh được. Dữ liệu mới chỉ cho vào train.

```bash
python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels \
    --meta datasets/v1/meta.csv --out splits/v1 --force-train mapillary,idd,bdd,coco
python tools/make_split_zip.py --split splits/v1 --out du_lieu.zip
```

Không có `meta.csv` thì script đoán nhóm theo tên file và đoán ngày/đêm theo độ sáng.

## Dữ liệu công khai

Kiểm tra giấy phép trên trang gốc trước khi dùng.

| Bộ | Giấy phép (cần xác nhận) | Dùng để |
|---|---|---|
| [Mapillary Vistas v2](https://www.mapillary.com/dataset/vistas) | CC BY-NC-SA 4.0 | mask biển báo, hộp đèn |
| [IDD Segmentation](https://idd.insaan.iiit.ac.in) | nghiên cứu | đường đông xe hai bánh, gần VN nhất |
| [BDD100K](https://bdd-data.berkeley.edu) | nghiên cứu | cảnh đêm, mưa |
| [COCO 2017](https://cocodataset.org) | CC BY 4.0 (nhãn) | người, xe máy |
| [Zalo AI 2020 Traffic Sign](https://datasetninja.com/zalo-traffic-sign) | chưa rõ | biển báo VN (chỉ có box, dùng SAM 3 tạo mask) |
| [VN Vehicle Tracking](https://zenodo.org/records/18195750) | CC BY 4.0 | mật độ xe máy VN (chỉ có box) |

Xe nước ngoài trông khác xe VN và không có ba gác, xe lam. Thêm từng phần, chỉ giữ phần làm tăng điểm val.

## Ưu tiên

Cảnh khó (đêm, mưa, đông xe máy, bị che, chói sáng) và lớp hiếm (ba gác, xích lô, xe lam, xe công trình, xe đạp).

## Còn cần hỏi BTC

- Có được dùng bộ dữ liệu giấy phép nghiên cứu (Vistas, IDD, BDD) không?
- Tập test quay từ dashcam, camera giao thông hay cả hai?
