# Kế hoạch dữ liệu

Mục **(đoán)** là giả định của nhóm, cần kiểm tra lại với dữ liệu mẫu của BTC.

## 1. Gán nhãn 11 lớp (id cố định)

| id | Lớp | Gồm | Lưu ý |
|---|---|---|---|
| 0 | Car | sedan, SUV, 7 chỗ, bán tải, taxi, van, xe 9-15 chỗ | |
| 1 | Bus | xe buýt, xe khách từ 16 chỗ | |
| 2 | Truck | mọi loại xe tải, xe bồn, cứu hỏa | đầu kéo: chỉ cabin + thân đầu kéo, rơ-moóc là lớp 3 |
| 3 | Other vehicle | ba gác, xích lô, xe lam, xe công trình, máy cày, rơ-moóc | |
| 4 | Motorcycle | xe máy **không người ngồi** (đỗ, dắt) | |
| 5 | Motorcyclist | **một** mask gồm xe + mọi người + hàng trên xe | không tách người thành Pedestrian |
| 6 | Bicycle | xe đạp không người | |
| 7 | Cyclist | **một** mask gồm xe đạp + người | |
| 8 | Pedestrian | mọi người không ngồi trên xe, kể cả người dắt xe | người dắt xe = Pedestrian + Motorcycle/Bicycle |
| 9 | Sign | phần tấm biển nhìn thấy, kể cả mặt sau nếu nhận diện được | bỏ cột và giá đỡ |
| 10 | Traffic light | **cả hộp đèn** | không chỉ bóng đang sáng |

Dùng [guideline v1](labeling-guideline-v1.md) cho ngưỡng kích thước, mask bị che khuất và cách gộp người với xe. Tra ID và tag ảnh trong [danh mục JSON](../configs/antco-labels-v1.json).

Giữ file `.txt` rỗng khi đã xác nhận ảnh không có đối tượng đủ điều kiện. Vẽ đa giác bám biên và chạy `check_labels.py` để kiểm tra định dạng.

## 2. Chia train/val

- Val **chỉ có ảnh Việt Nam**. Dữ liệu nước ngoài chỉ đưa vào train (`--force-train`).
- Tách **theo nhóm** (camera, video, địa điểm), không tách từng frame. Frame cùng video gần như giống hệt nhau.
- Nhắm khoảng 20% ảnh validation theo `time_of_day` khi có đủ nhóm quay. Nên có 300-600 ảnh val từ ít nhất 8-10 nhóm **(đoán)**.
- **Giữ nguyên tập val** giữa các vòng để điểm so sánh được. Dữ liệu mới thì cho vào train.

```bash
python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels \
    --meta datasets/v1/meta.csv --out splits/v1 --force-train mapillary,idd,bdd,coco
```

Dùng `file,group,time_of_day,source` theo [mẫu `meta.csv`](labeling-guideline-v1.md#tag-thời-điểm-theo-ảnh). Chọn `unknown` nếu khó xác định thời điểm. Khi thiếu metadata, script suy ra nhóm từ tên tệp và ngày hoặc đêm từ độ sáng.

## 3. Dữ liệu công khai

Kiểm tra giấy phép trên trang chính thức trước khi dùng, và ghi vào báo cáo: tên, link, giấy phép, số ảnh, ánh xạ lớp.

| Bộ | Giấy phép (cần xác nhận) | Vì sao dùng |
|---|---|---|
| [Mapillary Vistas v2](https://www.mapillary.com/dataset/vistas) | CC BY-NC-SA 4.0 | Có mask mặt biển và hộp đèn |
| [IDD Segmentation](https://idd.insaan.iiit.ac.in) | Nghiên cứu | Đường Ấn Độ, nhiều xe hai bánh, gần VN nhất |
| [BDD100K](https://bdd-data.berkeley.edu) | Nghiên cứu | Cảnh đêm, mưa |
| [COCO 2017](https://cocodataset.org) | CC BY 4.0 (nhãn) | Nhiều người và xe máy |
| [Zalo AI 2020 Traffic Sign](https://datasetninja.com/zalo-traffic-sign) | Chưa rõ | Biển báo VN có box để tạo mask nháp với SAM 3 |
| [VN Vehicle Tracking](https://zenodo.org/records/18195750) | CC BY 4.0 | Mật độ xe máy VN thật (chỉ có box) |

Ghép đúng người đang ngồi với xe tương ứng trước khi gán `5` hoặc `7`. Xe không người dùng `4` hoặc `6`. Người dắt xe có mask `8` riêng. Ưu tiên tự gán thêm ba gác và xe lam trong ảnh Việt Nam.

Rủi ro: xe ở nước ngoài trông khác xe VN. Thêm từng phần và chỉ giữ lại phần làm tăng điểm val VN.

## 4. Gán nhãn nháp bằng SAM 3 rồi duyệt tay

1. Gán thử một lô chung theo [guideline v1](labeling-guideline-v1.md#phối-hợp-thu-thập-và-gán-nhãn-bằng-sam-3), rồi chia các lô thu thập theo nguồn quay. Chọn các khung khác nhau từ mỗi video.
2. Tạo mask nháp bằng SAM 3, sau đó duyệt lớp, đường viền, cặp người–xe và vật thể bị bỏ sót.
3. Xuất YOLO-seg, chạy `check_labels.py` và dùng lỗi trên tập val để chọn lô tiếp theo.

Ưu tiên cảnh khó: đêm, mưa, đông xe máy, bị che, chói sáng, và lớp hiếm (ba gác, xích lô, xe lam, xe công trình, xe đạp).

## 5. Còn cần hỏi BTC

- BTC có cho dữ liệu train không, có kèm thông tin camera/thời gian không?
- Có được dùng bộ dữ liệu giấy phép nghiên cứu (Vistas, IDD, BDD) không?
- Tập private quay từ dashcam, camera giao thông hay cả hai?
