# Hướng dẫn gán nhãn ANTCO v1

**Phiên bản 1.0.0 · Đội 43**

Dùng hướng dẫn này khi gán, chuyển đổi và duyệt mask cho bài phân đoạn giao thông RoboTaxi. [Danh mục JSON](../configs/antco-labels-v1.json) chứa 11 lớp cố định và các giá trị tag ảnh của đội. Lấy ID và tên tiếng Anh theo đúng thứ tự `0–10` khi ánh xạ nhãn. Khi cần phân xử một ca khó, dùng quy ước của ban tổ chức. [Hướng dẫn chính thức của ANTCO](https://competition.antco.ai/data/labeling_guideline.md)

## Danh mục lớp

| ID | Lớp | Đối tượng |
|---:|---|---|
| 0 | `Car` | Ô tô con, bán tải, taxi, van chở khách, xe cứu thương dạng van và xe du lịch 9–15 chỗ. |
| 1 | `Bus` | Xe buýt và xe khách từ 16 chỗ trở lên. |
| 2 | `Truck` | Xe tải, xe ben, xe bồn, xe cứu hỏa và phần cabin cùng thân đầu kéo. |
| 3 | `Other vehicle` | Ba gác máy, xích lô, xe lam, xe công trình, xe máy cày, rơ-moóc, sơ-mi rơ-moóc và các phương tiện đủ điều kiện gán còn lại. |
| 4 | `Motorcycle` | Xe máy, tay ga hoặc xe điện kiểu xe máy không có người ngồi, kể cả xe đang được dắt. |
| 5 | `Motorcyclist` | Một mask cho xe máy và toàn bộ người đang ngồi trên xe. |
| 6 | `Bicycle` | Xe đạp hoặc xe đạp điện kiểu xe đạp không có người trên xe, kể cả xe đang được dắt. |
| 7 | `Cyclist` | Một mask cho xe đạp và người đi trên xe. |
| 8 | `Pedestrian` | Người đi, đứng, ngồi ngoài phương tiện hoặc đang dắt xe. |
| 9 | `Sign` | Mỗi tấm biển báo, biển chỉ dẫn hoặc biển tạm công trường là một mask. |
| 10 | `Traffic light` | Mỗi hộp đèn tín hiệu là một mask, gồm khung và các bóng. |

## Vẽ mask trên phần nhìn thấy

1. Gán đủ các đối tượng nhận dạng được và đạt ngưỡng kích thước. Dùng cạnh ngắn của hộp bao **phần nhìn thấy** để ước lượng. Bỏ qua vật nhỏ hơn khoảng **1,25% cạnh dài của ảnh**, tương đương 16 px trên ảnh có cạnh dài 1280 px. Với vật sát ngưỡng và khó nhận dạng, chuyển người duyệt xác nhận. [Quy ước kích thước của ANTCO](https://competition.antco.ai/data/labeling_guideline.md)
2. Bám theo viền phần nhìn thấy, kể cả đối tượng bị cắt ở mép ảnh. Khi hai vật che nhau, gán pixel cho vật ở phía trước và vẽ phần còn thấy của vật phía sau. Giữ đường viền trong phạm vi đối tượng, bỏ qua bóng đổ, phản chiếu, quầng sáng và vùng nền.
3. Nếu cột, dây hoặc lan can chia vật thể thành nhiều mảnh nhìn thấy, nhóm các mảnh cùng một instance trong công cụ gán nhãn. Kiểm tra lại mask sau khi xuất YOLO-seg. Chuyển ca sang duyệt nếu công cụ xuất làm mất mảnh hoặc tô qua vật che khuất.
4. Bỏ qua vật phía sau kính cửa hàng, người nhìn thấy bên trong ô tô, hình trên áp phích hoặc màn hình, động vật và xe đẩy tay. Vẫn gán `Pedestrian` cho người đang đẩy xe nếu người đó đạt điều kiện.

## Xử lý ca dễ nhầm

| Ca | Cách quyết định |
|---|---|
| Xe máy có người ngồi, kể cả khi dừng đèn đỏ | Gán `5` cho xe cùng tất cả người đang ngồi, gồm người ngồi sau và trẻ em. Phủ cả áo mưa trùm xe và hàng đã buộc chắc vào xe. |
| Người đứng cạnh, dắt hoặc đẩy xe | Gán `8` cho người và `4` cho xe máy hoặc `6` cho xe đạp. Khi người đã ngồi trên yên, chuyển sang nhóm xe có người. |
| Xe đạp có người đi | Gán `7` cho xe và người trong một instance. Xe đạp không người dùng `6`. |
| Xe điện hai bánh | Dựa vào kiểu dáng. Xe kiểu xe tay ga dùng `4/5`. Xe kiểu xe đạp dùng `6/7`. Chọn ID theo việc có người trên xe. |
| Nhiều xe máy sát nhau | Mỗi xe nhận dạng riêng là một instance. Giữ đúng viền nhìn thấy của từng xe. |
| Đầu kéo chở container | Gán `2` cho phần đầu kéo và `3` cho rơ-moóc cùng container. Ba gác hoặc xích lô có người ngồi hay đạp được gán chung một mask `3`. |
| Nhiều biển hoặc hộp đèn trên cùng trụ | Gán mỗi tấm biển `9`, chỉ phần tấm biển và bỏ cột, giá đỡ. Gán mỗi hộp đèn `10` cho cả hộp. Áp dụng cả khi thấy mặt sau. |
| Biển cửa hàng, đèn xe hoặc vật thể chỉ thấy quầng sáng | Bỏ qua biển quảng cáo và đèn xe. Gán phương tiện khi hình thể còn đủ rõ để nhận dạng. |

## Cây quyết định khi phân vân

1. Với xe hai bánh, nhận diện kiểu xe máy hay xe đạp rồi kiểm tra có người đang ngồi trên xe. Chọn `4/5` cho xe máy hoặc `6/7` cho xe đạp.
2. Với phương tiện còn lại, phân theo kiểu thân xe và công dụng. Ô tô con và xe du lịch 9–15 chỗ dùng `0`. Xe buýt hoặc xe khách từ 16 chỗ dùng `1`. Xe tải và đầu kéo dùng `2`. Ba gác, xích lô, rơ-moóc, xe công trình và phương tiện đủ điều kiện còn lại dùng `3`.
3. Với biển và đèn tín hiệu, `9` ứng với một tấm biển và `10` ứng với một hộp đèn. Khi vẫn phân vân, ghi tên ảnh, lớp dự kiến và lý do để người duyệt thống nhất quyết định cho cả đội. [Ca đặc biệt của ANTCO](https://competition.antco.ai/data/labeling_guideline.md)

## Phối hợp thu thập và gán nhãn bằng SAM 3

1. **Thống nhất cách gán trên một lô nhỏ.** Cho các thành viên gán thử cùng một số ảnh có người ngồi xe, người dắt xe, vật thể bị che và nhiều đối tượng sát nhau. So sánh số instance, ID và biên mask, rồi thống nhất cách xử lý trước khi chia lô lớn.
2. **Chia việc theo nguồn quay.** Mỗi lô có người phụ trách và người duyệt. Khi gom ảnh, dùng tên tệp duy nhất và `group` nhất quán cho cùng video gốc hoặc camera. Rà ảnh trùng và các khung gần giống trước khi chia train và validation.
3. **Tạo mask nháp bằng SAM 3.** Thử cụm từ ngắn như `motorcycle`, `person` hoặc `traffic light`, hoặc dùng box và điểm để sửa ca cụ thể. Khi gán ID, dựa vào hình ảnh và quy ước ANTCO. Prompt `motorcycle` có thể chỉ trả về phần xe. Ghép mask người đang ngồi với mask đúng xe để tạo một instance `5`. Với người dắt xe, giữ hai instance riêng. [SAM 3 của Meta](https://github.com/facebookresearch/sam3)
4. **Duyệt ảnh và nhãn sau khi xuất.** Người duyệt kiểm tra overlay, bổ sung vật thể đủ ngưỡng bị SAM 3 bỏ sót và sửa mask nhầm lớp, gộp sai instance hoặc tràn nền. Giữ nhóm cảnh dành cho validation cố định để so sánh các vòng huấn luyện.

## Tag thời điểm theo ảnh

Ghi một giá trị `time_of_day` cho mỗi ảnh. Tra tag trong `image_tags` của [danh mục JSON](../configs/antco-labels-v1.json). Lưu tag trong `meta.csv` để [công cụ chia tập](../tools/split_dataset.py) cân bằng thời điểm quay và ghi số ảnh theo tag vào `split_report.json`. File nhãn YOLO-seg chỉ chứa ID đối tượng và tọa độ polygon.

| Cột | Tag | Khi nào chọn |
|---|---|---|
| `time_of_day` | `day` | Cảnh có ánh sáng ban ngày. |
| `time_of_day` | `dawn` | Cảnh gần lúc mặt trời mọc, có căn cứ từ ảnh hoặc thời điểm quay của clip. |
| `time_of_day` | `dusk` | Cảnh lúc hoàng hôn hoặc chạng vạng chiều tối. |
| `time_of_day` | `night` | Cảnh ban đêm, thường dựa vào đèn đường, đèn xe hoặc nguồn sáng nhân tạo. |
| `time_of_day` | `unknown` | Góc quay hoặc ánh sáng chưa đủ để xác định thời điểm, chẳng hạn cảnh trong hầm. |

Chọn tag theo dấu hiệu nhìn thấy và thông tin của clip. Với cảnh tối do hầm hoặc thiếu sáng, dùng thời điểm quay nếu có. Dùng `unknown` khi vẫn thiếu căn cứ.

Lưu `datasets/v1/meta.csv` dưới dạng UTF-8. Cột `file` là tên ảnh gồm phần mở rộng, duy nhất trong tập. Dùng cùng `group` cho các ảnh cùng video gốc hoặc cùng camera khi có thông tin. Các dòng dưới đây minh họa định dạng metadata.

```csv
file,group,time_of_day,source
route01_000024.jpg,route01,day,dashcam
route01_000072.jpg,route01,day,dashcam
route02_000015.jpg,route02,dusk,dashcam
route03_000031.jpg,route03,night,dashcam
```

```bash
python tools/split_dataset.py --images datasets/v1/images --labels datasets/v1/labels --meta datasets/v1/meta.csv --out splits/v1
```

Các cảnh tổng hợp trên cổng thi dùng để xem cách phân biệt xe có người, xe không người, rơ-moóc, biển và hộp đèn. Khi thực hành đặt tag, dựa vào mô tả đi kèm nếu hình minh họa dùng màu trời cách điệu. [Mẫu trên cổng ANTCO](https://competition.antco.ai/)

## Chuẩn bị nhãn từ dữ liệu nguồn

- **RoadBuddy hoặc dashcam của đội.** Chọn khung rõ biên và đa dạng theo clip. Dùng nội dung câu hỏi RoadBuddy để tìm cảnh cần gán bằng SAM 3. [RoadBuddy](https://huggingface.co/datasets/OpenHay/zalo-ai-2025-training-data-v2)
- **Roboflow Vietnam Traffic 5Classes.** Duyệt từng ca `Motorbike` để chọn `4` hoặc `5`, và từng ca `Bicycle` để chọn `6` hoặc `7`. Chuyển `Person` sang `8` khi người đủ điều kiện và đứng riêng với xe. Bổ sung nhãn cho các lớp ANTCO có mặt trong ảnh mà bộ gốc chưa gán. [Dữ liệu Roboflow](https://universe.roboflow.com/jose-89vn1/vietnam-traffic-5classes-xthnt/dataset/1)
- **India Driving Dataset.** Duyệt cặp `rider` và xe tương ứng trước khi gộp về `5` hoặc `7`. Đối chiếu từng lớp và phạm vi mask với quy ước ANTCO, đặc biệt ở biển báo, hộp đèn và xe ba bánh. [Danh mục lớp IDD](https://github.com/AutoNUE/public-code)

Với mỗi nguồn, lưu tên, URL, giấy phép, số ảnh thực dùng và bảng ánh xạ sang 11 lớp. Chia train và validation theo camera hoặc video gốc khi xác định được. Với ảnh trích video, giữ toàn bộ khung từ cùng clip trong một tập. [Yêu cầu báo cáo của ANTCO](https://competition.antco.ai/)

## Xuất YOLO-seg và kiểm tra trước khi train

Mỗi ảnh có một tệp `.txt` cùng tên gốc. Mỗi dòng là một instance, bắt đầu bằng ID lớp rồi đến ít nhất ba cặp tọa độ. Chuẩn hóa `x` theo chiều rộng, `y` theo chiều cao ảnh, trong khoảng `[0, 1]`. Dòng mẫu dùng ID `5` cho `Motorcyclist`.

```text
5 0.42 0.31 0.47 0.29 0.51 0.54 0.43 0.57
```

Với tập đã chia sẵn, lưu ảnh trong `images/train` và `images/val`, nhãn tương ứng trong `labels/train` và `labels/val`. Nếu người duyệt xác nhận ảnh không có đối tượng đủ điều kiện, giữ tệp nhãn rỗng. Dùng `names` trong [cấu hình dữ liệu của repo](../configs/data.yaml) theo thứ tự của [danh mục JSON](../configs/antco-labels-v1.json). [Định dạng YOLO-seg](https://docs.ultralytics.com/datasets/segment/) · [Notebook ANTCO](https://competition.antco.ai/downloads/train_and_export.ipynb)

- [ ] Mỗi ảnh ghép đúng tệp nhãn. ID nằm trong `0–10` và tên tiếng Anh khớp cấu hình huấn luyện.
- [ ] Tọa độ hợp lệ và mỗi polygon có ít nhất ba đỉnh phân biệt, có diện tích và đường biên hợp lệ.
- [ ] Overlay sau khi xuất cho thấy đủ đối tượng, đúng lớp, đúng số instance và biên mask khớp phần nhìn thấy.
- [ ] Kiểm tra lại các ảnh khó như xe có người, người dắt xe, vật thể bị che và các lớp hiếm.
- [ ] Mỗi ảnh có một dòng metadata với tên tệp đúng, tag hợp lệ và `group` nhất quán theo nguồn quay.
- [ ] Rà ảnh trùng hoặc gần trùng giữa train và validation, rồi thống kê số instance theo lớp.
