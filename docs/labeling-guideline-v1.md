# Hướng dẫn gán nhãn v1

Gặp ca khó thì làm theo [hướng dẫn chính thức của BTC](https://competition.antco.ai/data/labeling_guideline.md). Danh sách lớp và tag ở [antco-labels-v1.json](../configs/antco-labels-v1.json).

## 11 lớp (id cố định)

| id | Lớp | Gồm |
|---:|---|---|
| 0 | Car | ô tô con, bán tải, taxi, van, xe 9-15 chỗ |
| 1 | Bus | xe buýt, xe khách từ 16 chỗ |
| 2 | Truck | xe tải, xe ben, xe bồn, cứu hỏa, **chỉ phần đầu kéo** |
| 3 | Other vehicle | ba gác, xích lô, xe lam, xe công trình, máy cày, **rơ-moóc/container** |
| 4 | Motorcycle | xe máy **không người ngồi** (đỗ, đang dắt) |
| 5 | Motorcyclist | **một** mask gồm xe máy + mọi người ngồi trên + hàng buộc trên xe |
| 6 | Bicycle | xe đạp không người |
| 7 | Cyclist | **một** mask gồm xe đạp + người |
| 8 | Pedestrian | mọi người không ngồi trên xe, kể cả người dắt xe |
| 9 | Sign | mỗi tấm biển một mask, **không lấy cột** |
| 10 | Traffic light | mỗi **hộp đèn** một mask |

## Quy tắc vẽ mask

- Chỉ vẽ phần nhìn thấy. Hai vật che nhau thì vật trước giữ pixel, mask **không chồng nhau**.
- Vật bị cột/dây chia thành nhiều mảnh vẫn là **một** instance.
- Không phủ bóng đổ, phản chiếu, quầng đèn.
- Bỏ vật có cạnh ngắn dưới **1,25% cạnh dài ảnh** (16 px với ảnh 1280 px). Máy chấm bỏ qua mask dưới 64 px ở thang 640.
- Đo cạnh ngắn trên hộp bao phần nhìn thấy. Với vật sát ngưỡng, bỏ qua nếu sau khi duyệt vẫn phải đoán.
- Không gán: vật sau kính cửa hàng, người trong ô tô, áp phích, màn hình, biển quảng cáo, đèn xe, động vật, xe đẩy tay.
- Bỏ mô hình, tượng, băng rôn, bảng giá, biển số nhà, đèn đường và đèn trang trí.
- Ảnh không có gì: để `.txt` rỗng. Không dùng hình chữ nhật thay đa giác.

## Ca dễ nhầm

| Ca | Gán |
|---|---|
| Người ngồi trên xe máy (kể cả dừng đèn đỏ, người ngồi sau, trẻ em) | một mask `5` |
| Người dắt hoặc đứng cạnh xe | `8` cho người + `4`/`6` cho xe |
| Xe điện kiểu tay ga / kiểu xe đạp | `4/5` / `6/7` |
| Đầu kéo chở container | `2` cho đầu kéo + `3` cho rơ-moóc |
| Ba gác, xích lô có người | một mask `3` |
| Xe 4 bánh còn phân vân | nhỏ hơn 9 chỗ `0`, kiểu xe buýt `1`, xe tải `2`, còn lại `3` |
| Xe du lịch 9–15 chỗ hoặc xe điện du lịch | Gán `0` theo bảng lớp. |
| Áo mưa trùm cả người ngồi và xe máy | Tính áo mưa vào cùng mask `5`. |
| Người bế hoặc cõng trẻ | Một mask `8` phủ cả hai. |
| Xe lăn có người đẩy | Người ngồi và người đẩy là hai mask `8`. Bỏ phần xe lăn. |
| Xe tải hoặc xe đạp chở hàng | Tính hàng trên thùng xe tải và hàng buộc vào xe đạp vào mask của xe. |
| Xe máy hoặc xe đạp được chở trên xe khác | Gán xe được chở thành instance riêng nếu nhận ra và đủ ngưỡng. Bỏ phần đó khỏi mask xe chở. |
| Lưng biển hoặc hộp đèn nhìn từ sau | Vẫn gán `9` cho từng tấm biển, bỏ cột và giá đỡ. Gán `10` cho từng hộp đèn, gồm phần đếm ngược gắn liền. |

Vẫn phân vân thì ghi tên ảnh, lớp dự kiến, lý do, để người duyệt chốt cho cả đội.

Nếu vật đủ điều kiện và vẫn khó phân lớp sau khi duyệt, chọn lớp hợp lý nhất rồi ghi lại quyết định để cả đội áp dụng nhất quán.

## Quy trình gán bằng SAM 3

1. Cả đội gán thử cùng một lô nhỏ, so sánh rồi thống nhất cách gán.
2. Chia lô theo nguồn quay. Mỗi lô có người gán và người duyệt.
3. Tạo mask nháp bằng [SAM 3](https://github.com/facebookresearch/sam3) (prompt như `motorcycle`, `person`, `traffic light`). Ghép mask người ngồi với đúng xe thành một mask `5`.
4. Người duyệt sửa lớp, viền mask, vật bị sót, rồi xuất YOLO-seg và chạy `tools/check_labels.py`.

## Metadata cho từng ảnh

Ghi `datasets/v1/meta.csv` (UTF-8) để chia val theo camera và thời điểm:

```csv
file,group,time_of_day,source
route01_000024.jpg,route01,day,dashcam
route03_000031.jpg,route03,night,dashcam
```

- `group`: cùng video hoặc camera thì cùng giá trị.
- `time_of_day`: `day`, `dawn`, `dusk`, `night` hoặc `unknown`.

Truyền CSV bằng `--meta datasets/v1/meta.csv` khi chạy `tools/split_dataset.py`.

## Nguồn dữ liệu

| Nguồn | Lưu ý khi chuyển nhãn |
|---|---|
| [RoadBuddy](https://huggingface.co/datasets/OpenHay/zalo-ai-2025-training-data-v2) / dashcam của đội | Chọn khung rõ, khác nhau trong mỗi clip |
| [Roboflow Vietnam Traffic](https://universe.roboflow.com/jose-89vn1/vietnam-traffic-5classes-xthnt/dataset/1) | Tách `Motorbike` thành `4`/`5`, `Bicycle` thành `6`/`7`; gán thêm lớp còn thiếu |
| [IDD](https://github.com/AutoNUE/public-code) | Ghép `rider` với xe thành `5`/`7` |

Mỗi nguồn ghi lại: tên, link, giấy phép, số ảnh dùng, bảng ánh xạ 11 lớp (bắt buộc cho báo cáo).

## Kiểm tra trước khi train

- [ ] Mỗi ảnh có đúng một `.txt` cùng tên, id trong `0-10`, mỗi đa giác ít nhất 3 điểm.
- [ ] Xem overlay: đủ đối tượng, đúng lớp, viền sát.
- [ ] Rà kỹ: người trên xe, người dắt xe, vật bị che, lớp hiếm.
- [ ] Mỗi ảnh có một dòng trong `meta.csv`.

Tọa độ YOLO-seg dùng cặp `x y` chuẩn hóa trong `[0, 1]`. Kiểm tra nhãn đã xuất bằng lệnh dưới đây.

```bash
python tools/check_labels.py --images datasets/v1/images --labels datasets/v1/labels
```
