# Rà soát nhãn ngày 28/11/2026 (Asia/Bangkok)

Kiểm tra snapshot `b924659` trên `origin/main`, gồm cả hai bộ đã được merge. **150 ảnh / 150 tệp nhãn / 1.774 instance vượt kiểm tra định dạng YOLO-seg dùng cho YOLO26n-seg. Chưa đủ căn cứ xác nhận toàn bộ nhãn đạt guideline hoặc sẵn sàng nộp.** Lượt này không sửa polygon hay tự nâng trạng thái QA.

## Tiến độ và phân bố lớp

| Bộ | Ảnh | Instance | Trạng thái ghi trong dữ liệu |
| --- | ---: | ---: | --- |
| pov_hard_ez | 100 | 930 | 25 ảnh REVIEWED_PENDING_FINAL_QA, 75 ảnh PENDING |
| pov_med | 50 | 844 | 50 ảnh PENDING_CVAT_QA; nguồn ghi 82 instance chưa chắc chắn |
| Tổng | 150 | 1.774 | 125 ảnh nháp; 25 ảnh đã qua một lượt nhưng còn QA cuối |

| Lớp | Số instance |
| --- | ---: |
| Car | 261 |
| Bus | 33 |
| Truck | 36 |
| Other vehicle | 36 |
| Motorcycle | 37 |
| Motorcyclist | 746 |
| Bicycle | 4 |
| Cyclist | 1 |
| Pedestrian | 61 |
| Sign | 474 |
| Traffic light | 85 |

Đủ 11 id lớp trong tổng dữ liệu; rất thiếu mẫu Bicycle/Cyclist. Bản sửa 0409 từ Bicycle sang Cyclist đã có trên main và được giữ nguyên. Metadata của cả 150 ảnh đều ghi `day`; chưa có mẫu được đánh dấu đêm. Metadata không đủ để kết luận bao nhiêu ảnh mưa. Không suy ra số đối tượng bị sót chỉ từ số lượng lớp.

## Kiểm tra định dạng và toàn vẹn

- Không thiếu/thừa tệp nhãn so với ảnh; không tệp nhãn rỗng, không dòng nhãn trùng hoàn toàn.
- Id 0–10, tọa độ hữu hạn trong [0,1], ít nhất 3 điểm; không đa giác tự cắt theo `tools/check_labels.py`.
- Ultralytics **8.4.214**, đúng phiên bản requirements: `verify_image_label` nhận đủ 150 ảnh và 1.774 segment, không lỗi hoặc mất instance.
- Chạy các hàm kiểm tra đa giác/diện tích trích trực tiếp từ `colab/shared.ipynb`: 0 polygon lỗi, 0 instance diện tích <64 px ở thang 640. Đây là kiểm tra dữ liệu, chưa phải chấm model.
- Metadata đủ đúng một dòng mỗi ảnh: 41 nhóm hard/ez và 25 nhóm med. Không ảnh trùng byte SHA-256. Không cặp dHash khoảng cách ≤4 giữa hai bộ; điều này không chứng minh mọi cảnh/video đã được gom nhóm chính xác.
- 194 cảnh báo đỉnh lặp/cầu nối ở hard/ez, 15 ở med. Cầu nối không bị coi là tự cắt nhưng vẫn phải xem topology. Sửa số thống kê hard/ez cũ 193 thành 194.

Kết quả máy đọc: [summary.json](label-audit-2026-11-28/summary.json).

## Nhãn cần sửa hoặc xác minh

[review_queue.csv](label-audit-2026-11-28/review_queue.csv) ghi đầy đủ tên ảnh và số dòng nhãn (1-based, tại snapshot trên).

1. **55 cặp mask chồng đáng kể trên 29 ảnh med.** Tiêu chí phát hiện: giao ít nhất 64 pixel raster và chiếm ≥10% mask nhỏ hơn, raster hóa bằng OpenCV ở 640×640. Đây là danh sách ứng viên, không phải 55 instance thừa. Đã xem crop 12 cặp có tỷ lệ cao nhất và xác nhận mask vật phía sau phủ lên vùng bị vật trước che: ví dụ 0259 dòng 1/2 (bus/xe máy), 2621 dòng 4/5 (ô tô/xe máy), 2724 dòng 2/3 (hai xe máy). Cần cắt theo phần nhìn thấy và duyệt lại viền cả hai mask. Không tự trừ mask theo diện tích vì chưa xác định thứ tự che khuất cho mọi cặp. Hard/ez không có cặp vượt ngưỡng phát hiện này; không có nghĩa hoàn toàn không chồng pixel biên.
2. **27 polygon có bbox cạnh ngắn tính liên tục dưới 8 px:** 21 hard/ez và 6 med. Trong đó **18 dưới 7,99 px**, **9 sát 8 px do lượng tử/làm tròn**. Đã xem crop của cả 27. Cần đo phần đối tượng thực sự nhìn thấy: mask bị vẽ thiếu cũng có thể tạo bbox quá nhỏ. Ví dụ 0356 dòng 7 cần xem lại phần hộp đèn thay vì chỉ vùng sáng. Không xóa hàng loạt theo bbox nhãn; chỉ bỏ vật thực sự dưới 1,25% cạnh dài ảnh theo guideline. Ngưỡng cạnh ngắn và ngưỡng diện tích 64 px là hai điều kiện khác nhau.
3. **Chưa kiểm đủ đối tượng bị sót trên toàn bộ ảnh.** Lượt này chỉ kiểm tra tự động toàn bộ và xem crop rủi ro (27 trường hợp kích thước, 12 cặp chồng). Giữ nguyên trạng thái 125 ảnh nháp; chưa xác nhận 25 ảnh còn lại đạt QA cuối. Tiếp tục xem overlay toàn ảnh, ưu tiên med, người trên xe/người dắt xe, tấm biển/hộp đèn và lớp hiếm.

## Validation và điểm theo README

Đã chạy chia theo metadata với seed 48 bằng `tools/split_dataset.py`, riêng từng bộ để kiểm tra hướng dẫn hiện có:

| Bộ | Train | Val | Cyclist trong val |
| --- | ---: | ---: | ---: |
| hard/ez | 80 | 20 | 0 |
| med | 40 | 10 | 0 |

Bộ med còn có 0 Bicycle trong train. Chi tiết: [hard/ez](label-audit-2026-11-28/split_hard_ez.json), [med](label-audit-2026-11-28/split_med.json). Đây là hai phép kiểm tra độc lập, chưa phải một split gộp được phê duyệt; khi gộp phải thống nhất nhóm cảnh/video giữa hai bộ rồi chia một lần. Không lấy cùng một ảnh Cyclist cho cả train và val để lấp thiếu lớp.

**Chưa chấm mAP:** không tìm thấy `best.pt`, `model.onnx` hoặc `run_report.json` trong project local. Model tạo nhãn YOLOE/SAM không thay thế checkpoint YOLO26n-seg đã train. Không gán điểm 0 hoặc lấy tỷ lệ nhãn hợp lệ làm điểm thi. Sau khi có checkpoint và val cố định, chạy Bước 4–6 notebook chung theo `guide.md`; điểm = 100 × mask mAP@[.50:.95]. Điểm private chỉ có từ BTC.

## Cách tái kiểm tra phần định dạng

```bash
python tools/check_labels.py --images datasets/pov_hard_ez/images --labels datasets/pov_hard_ez/labels
python tools/check_labels.py --images datasets/pov_med/images --labels datasets/pov_med/labels
python -m unittest discover -s tools -p test_check_labels.py
```

Cả hai lệnh kiểm nhãn thành công; 6 test checker thành công. Đối chiếu quy tắc với README, `docs/labeling-guideline-v1.md`, `guide.md` và notebook đang có trong repository. URL guideline BTC không truy cập được bằng công cụ web ở lượt này, nên chưa xác minh có thay đổi mới ngoài repository.
