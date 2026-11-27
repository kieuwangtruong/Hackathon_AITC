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
| 9 | Sign | **chỉ mặt biển** | không lấy cột, không lấy mặt sau **(đoán)** |
| 10 | Traffic light | **cả hộp đèn** | không chỉ bóng đang sáng |

Quy tắc thêm **(đoán)**:
- Bị che: chỉ vẽ phần nhìn thấy. Nếu bị chia làm hai mảnh, vẽ mảnh lớn hơn.
- Bỏ vật nhỏ hơn khoảng 8×8 px, phản chiếu, hình trên biển quảng cáo.
- Ảnh không có vật nào: để file `.txt` rỗng.
- Không dán hình chữ nhật thay cho đa giác (`check_labels.py` sẽ cảnh báo).

## 2. Chia train/val

- Val **chỉ có ảnh Việt Nam**. Dữ liệu nước ngoài chỉ đưa vào train (`--force-train`).
- Tách **theo nhóm** (camera, video, địa điểm), không tách từng frame. Frame cùng video gần như giống hệt nhau.
- Mỗi điều kiện (ngày/đêm, mưa) có khoảng 20% ảnh trong val. Nên có 300-600 ảnh val từ ít nhất 8-10 nhóm **(đoán)**.
- **Giữ nguyên tập val** giữa các vòng để điểm so sánh được. Dữ liệu mới thì cho vào train.

```bash
python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels \
    --meta datasets/v1/meta.csv --out splits/v1 --force-train mapillary,idd,bdd,coco
```

`meta.csv` (không bắt buộc): `file, group, camera, location, time_of_day, weather, source`. Không có file này thì script tự đoán nhóm theo tên file và đoán ngày/đêm theo độ sáng.

## 3. Dữ liệu công khai

Kiểm tra giấy phép trên trang chính thức trước khi dùng, và ghi vào báo cáo: tên, link, giấy phép, số ảnh, ánh xạ lớp.

| Bộ | Giấy phép (cần xác nhận) | Vì sao dùng |
|---|---|---|
| [Mapillary Vistas v2](https://www.mapillary.com/dataset/vistas) | CC BY-NC-SA 4.0 | Có mask mặt biển và hộp đèn |
| [IDD Segmentation](https://idd.insaan.iiit.ac.in) | Nghiên cứu | Đường Ấn Độ, nhiều xe hai bánh, gần VN nhất |
| [BDD100K](https://bdd-data.berkeley.edu) | Nghiên cứu | Cảnh đêm, mưa |
| [COCO 2017](https://cocodataset.org) | CC BY 4.0 (nhãn) | Nhiều người và xe máy |
| [Zalo AI 2020 Traffic Sign](https://datasetninja.com/zalo-traffic-sign) | Chưa rõ | Biển báo VN (chỉ có box, cần SAM 2) |
| [VN Vehicle Tracking](https://zenodo.org/records/18195750) | CC BY 4.0 | Mật độ xe máy VN thật (chỉ có box) |

Ánh xạ chung: người chồng lên xe máy/xe đạp thì gộp mask thành 5/7; xe không người là 4/6; người còn lại là 8. Xe tự chế (ba gác, xe lam) không có trong bộ nào nên phải tự gán.

Rủi ro: xe ở nước ngoài trông khác xe VN. Thêm từng phần và chỉ giữ lại phần làm tăng điểm val VN.

## 4. Gán nhãn nháp rồi sửa tay

1. Lấy frame VN, khoảng 1 frame mỗi 2-3 giây.
2. Tạo nhãn nháp bằng model lớn (`predict.py`, yolo-seg cỡ lớn, hoặc Grounding DINO + SAM 2 cho biển báo, đèn, xích lô, ba gác).
3. Sửa tay trong CVAT hoặc Label Studio. Tập trung vào lớp hiếm, người trên xe, biển báo.
4. Chạy `check_labels.py`, train, xem lỗi trên val, rồi gán thêm loại ảnh model hay sai.

Ưu tiên cảnh khó: đêm, mưa, đông xe máy, bị che, chói sáng, và lớp hiếm (ba gác, xích lô, xe lam, xe công trình, xe đạp).

## 5. Còn cần hỏi BTC

- BTC có cho dữ liệu train không, có kèm thông tin camera/thời gian không?
- Có được dùng bộ dữ liệu giấy phép nghiên cứu (Vistas, IDD, BDD) không?
- Tập private quay từ dashcam, camera giao thông hay cả hai?
