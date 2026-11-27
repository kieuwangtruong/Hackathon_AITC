# Hướng dẫn gán nhãn ANTCO v1

Giữ đúng ID và tên tiếng Anh khi gán hoặc chuyển đổi nhãn. Với ca khó, đối chiếu quy tắc của BTC. [Danh mục JSON](../configs/antco-labels-v1.json) · [Hướng dẫn ANTCO](https://competition.antco.ai/data/labeling_guideline.md)

## 11 lớp (id cố định)

| id | Lớp | Gồm |
|---:|---|---|
| 0 | `Car` | Ô tô con, bán tải, taxi, van cứu thương, xe điện du lịch và xe du lịch 9–15 chỗ. |
| 1 | `Bus` | Xe buýt và xe khách từ 16 chỗ. |
| 2 | `Truck` | Xe tải, xe ben, xe bồn, xe cứu hỏa và phần đầu kéo. |
| 3 | `Other vehicle` | Ba gác, xích lô, xe lam, xe công trình, máy cày, rơ-moóc và phương tiện còn lại. |
| 4 | `Motorcycle` | Xe máy không có người ngồi, kể cả xe đang được dắt. |
| 5 | `Motorcyclist` | Một mask gồm xe máy, mọi người ngồi trên xe và hàng buộc chắc vào xe. |
| 6 | `Bicycle` | Xe đạp không có người ngồi, kể cả xe đang được dắt. |
| 7 | `Cyclist` | Một mask gồm xe đạp và người đang đi trên xe. |
| 8 | `Pedestrian` | Người đi, đứng hoặc ngồi ngoài phương tiện, kể cả người dắt xe. |
| 9 | `Sign` | Mỗi tấm biển giao thông, kể cả lưng biển. Mask dừng ở mép biển, bỏ cột và giá đỡ. |
| 10 | `Traffic light` | Mỗi hộp đèn nhìn từ trước hoặc sau. Mask phủ cả hộp và đèn đếm ngược gắn liền. |

## Quy tắc vẽ mask

- Vẽ phần nhìn thấy, kể cả vật bị cắt ở mép ảnh. Vật ở trước giữ pixel vùng che để các mask không chồng nhau. Bỏ bóng đổ, phản chiếu và quầng đèn.
- Vật bị cột hoặc dây chia thành nhiều mảnh vẫn là **một instance**. Kiểm tra overlay sau khi xuất để phát hiện mất mảnh hoặc tô qua vật che.
- Bỏ vật nếu cạnh ngắn của hộp bao phần nhìn thấy dưới khoảng **1,25% cạnh dài ảnh** (16 px với ảnh có cạnh dài 1280 px). Với vật sát ngưỡng, bỏ qua nếu vẫn phải đoán sau khi duyệt.
- Bỏ vật sau kính cửa hàng, người trong ô tô, hình trên áp phích hoặc màn hình, mô hình, tượng, động vật và xe đẩy tay. Người đẩy xe vẫn có thể được gán `Pedestrian`.
- Bỏ biển quảng cáo, biển cửa hàng, băng rôn, bảng giá, biển số nhà, đèn xe, đèn đường và đèn trang trí.

## Ca dễ nhầm

| Ca | Gán |
|---|---|
| Người ngồi trên xe máy, kể cả khi dừng đèn đỏ | Gán một mask `5` cho xe và mọi người trên xe. Tính cả áo mưa trùm người và xe. |
| Người dắt hoặc đứng cạnh xe | Gán `8` cho người và `4` hoặc `6` cho xe. |
| Xe điện hai bánh | Kiểu tay ga dùng `4/5`, kiểu xe đạp dùng `6/7`. Chọn ID theo việc có người ngồi trên xe. |
| Đầu kéo chở container | Gán `2` cho đầu kéo và `3` cho rơ-moóc cùng container. |
| Ba gác hoặc xích lô có người ngồi hay đạp | Gán chung một mask `3`. |
| Người bế hoặc cõng trẻ | Gán một mask `8` phủ cả hai. |
| Xe lăn có người đẩy | Gán người ngồi và người đẩy thành hai mask `8`. Bỏ phần xe lăn. |
| Xe tải hoặc xe đạp chở hàng | Hàng trên thùng xe tải và hàng buộc vào xe đạp nằm trong mask của xe. |
| Xe máy hoặc xe đạp được chở trên xe khác | Gán xe được chở thành instance riêng nếu nhận ra và đủ ngưỡng. Bỏ phần đó khỏi mask xe chở. |

Nếu vật đủ điều kiện gán và vẫn khó phân lớp sau khi duyệt, chọn lớp hợp lý nhất. Ghi tên ảnh, lớp đã chọn và lý do để cả đội áp dụng nhất quán.

## Phối hợp thu thập và gán nhãn bằng SAM 3

1. Cả đội gán thử cùng một lô nhỏ, so sánh rồi thống nhất cách gán.
2. Chia lô theo nguồn quay. Mỗi lô có người gán và người duyệt.
3. Tạo mask nháp bằng prompt như `motorcycle`, `person` hoặc `traffic light`. Ghép người ngồi với đúng xe theo bảng lớp. [SAM 3](https://github.com/facebookresearch/sam3)
4. Người duyệt kiểm tra lớp, viền mask và vật bị sót. Giữ tập val theo nhóm cảnh để so sánh các vòng train.

## Tag thời điểm theo ảnh

Ghi `datasets/v1/meta.csv` dưới dạng UTF-8 để chia val theo camera và thời điểm. Cột `file` dùng tên ảnh duy nhất, gồm phần mở rộng.

```csv
file,group,time_of_day,source
route01_000024.jpg,route01,day,dashcam
route03_000031.jpg,route03,night,dashcam
```

- Dùng cùng `group` cho ảnh từ cùng video hoặc camera.
- Chọn `time_of_day` trong `day`, `dawn`, `dusk`, `night`, `unknown`. Dùng `unknown` khi ảnh và thông tin clip đều thiếu căn cứ.

```bash
python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels --meta datasets/v1/meta.csv --out splits/v1
```

## Nguồn dữ liệu

| Nguồn | Lưu ý khi chuyển nhãn |
|---|---|
| [RoadBuddy](https://huggingface.co/datasets/OpenHay/zalo-ai-2025-training-data-v2) / dashcam của đội | Chọn khung rõ, khác nhau trong mỗi clip |
| [Roboflow Vietnam Traffic](https://universe.roboflow.com/jose-89vn1/vietnam-traffic-5classes-xthnt/dataset/1) | Tách `Motorbike` thành `4`/`5`, `Bicycle` thành `6`/`7`; gán thêm lớp còn thiếu |
| [IDD](https://github.com/AutoNUE/public-code) | Ghép `rider` với xe thành `5`/`7` |

Ghi tên, URL, giấy phép, số ảnh thực dùng và bảng ánh xạ 11 lớp cho mỗi nguồn để đưa vào báo cáo.

## Kiểm tra trước khi train

Xuất một tệp `.txt` cùng tên gốc cho mỗi ảnh. Mỗi dòng YOLO-seg gồm ID `0–10` và ít nhất ba cặp tọa độ `x y` chuẩn hóa trong `[0, 1]`. Dùng tệp rỗng cho ảnh nền đã duyệt.

```bash
python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
```

- [ ] Xem overlay sau khi xuất để kiểm tra đủ đối tượng, đúng lớp, đúng số instance và viền sát.
- [ ] Rà người trên xe, người dắt xe, vật bị che và lớp hiếm.
- [ ] Đối chiếu dòng `meta.csv` của mỗi ảnh, rà ảnh trùng giữa train và val, rồi đếm instance theo lớp.
