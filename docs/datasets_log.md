# Nhật ký dữ liệu (cho báo cáo)

| Bộ dữ liệu | Link | Giấy phép | Số ảnh dùng | Ánh xạ về 11 lớp |
| --- | --- | --- | --- | --- |
| Vietnam Traffic Signs v1 (Roboflow) | https://universe.roboflow.com/machinelearning-dddne/vietnam-traffic-signs-chsxr | CC BY 4.0 | 150 (117 train, 33 val), gán lại nhãn tay | Gán mới theo hướng dẫn gán nhãn |
| COCO 2017 (train+val) | https://cocodataset.org | Nhãn CC BY 4.0; ảnh theo giấy phép Flickr | tới ~4000 (v5/v7); 300 ảnh val cố định | Xem `tools/coco/README.md` |

## Các vòng

| Vòng | Train | Val | Điểm public |
| --- | --- | --- | --- |
| 1 | 117 ảnh VN | 33 ảnh VN | 39.44 |
| 2 | 117 ảnh VN ×3 + 1000 COCO = 1351 | 33 ảnh VN (giữ nguyên) | bỏ qua, thay bằng v3 |
| 3 | Như vòng 2, ảnh VN trả về 640×360 | 33 ảnh VN, 640×360 | 47.00 |
| 4 | VN ×5 + ~2200 COCO, nhãn Sign giả từ v3; 50 epoch (Colab) | 33 VN + 300 COCO | 52.75 |
| 5 | VN ×6 + ảnh có Other vehicle/Sign lặp thêm + ~3650 COCO; 22 epoch (Kaggle) | như v4 | 52.23 |
| 6 | Dữ liệu v4 + lặp thêm, không nhãn Sign giả; 22 epoch | như v4 | 51.70 |
| 7 | Dữ liệu v5; 40 epoch (Kaggle) | như v4 | **53.04** |
| 8 | Dữ liệu v4, không nhãn Sign giả; 40 epoch | như v4 | 51.74 |

Số đối tượng COCO đã thêm: Car 2743, Bus 247, Truck 470, Motorcycle 418, Motorcyclist 269, Bicycle 429, Cyclist 222, Pedestrian 2524, Sign 120, Traffic light 841.

Ảnh Roboflow bị ép từ 16:9 thành 640×640 (biển báo rộng/cao trung vị 0.59). Ảnh test khoảng 1280×720, nên từ v3 ảnh VN được đưa về 640×360. Nhãn giữ nguyên vì tọa độ đã chuẩn hóa.
