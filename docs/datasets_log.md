# Nhật ký dữ liệu (cho báo cáo)

| Bộ dữ liệu | Link | Giấy phép | Số ảnh dùng | Ánh xạ về 11 lớp |
| --- | --- | --- | --- | --- |
| Vietnam Traffic Signs v1 (Roboflow) | https://universe.roboflow.com/machinelearning-dddne/vietnam-traffic-signs-chsxr | CC BY 4.0 | 150 (117 train, 33 val), gán lại nhãn tay | Gán mới theo hướng dẫn gán nhãn |
| COCO 2017 (train+val) | https://cocodataset.org | Nhãn CC BY 4.0; ảnh theo giấy phép Flickr | 1000 (chỉ train) | Xem `tools/coco/README.md` |

## Các vòng

| Vòng | Train | Val | Điểm public |
| --- | --- | --- | --- |
| 1 | 117 ảnh VN | 33 ảnh VN | 39.44 |
| 2 | 117 ảnh VN ×3 + 1000 COCO = 1351 | 33 ảnh VN (giữ nguyên) | bỏ qua, thay bằng v3 |
| 3 | Như vòng 2, ảnh VN trả về 640×360 | 33 ảnh VN, 640×360 | chưa có |

Số đối tượng COCO đã thêm: Car 2743, Bus 247, Truck 470, Motorcycle 418, Motorcyclist 269, Bicycle 429, Cyclist 222, Pedestrian 2524, Sign 120, Traffic light 841.

Ảnh Roboflow bị ép từ 16:9 thành 640×640 (biển báo rộng/cao trung vị 0.59). Ảnh test khoảng 1280×720, nên từ v3 ảnh VN được đưa về 640×360. Nhãn giữ nguyên vì tọa độ đã chuẩn hóa.
