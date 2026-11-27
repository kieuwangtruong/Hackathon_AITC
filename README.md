# Hackathon_AITC

## Google Colab

Notebook dùng chung có thể tải code mới nhất từ nhánh `main` mỗi khi chạy. Xem [hướng dẫn sử dụng](colab/README.md) hoặc [mở notebook trong Colab](https://colab.research.google.com/github/kieuwangtruong/Hackathon_AITC/blob/main/colab/shared.ipynb).

## Huấn luyện baseline (yolo26n-seg, imgsz=640)

Mô hình và kích thước ảnh do BTC cố định, nên các script chỉ cho đổi dữ liệu và công thức huấn luyện. Dữ liệu, `runs/`, trọng số và file `.onnx` đều nằm trong `.gitignore` vì CI đóng gói mọi file được Git theo dõi.

| File | Việc |
| --- | --- |
| [requirements.txt](requirements.txt) | Ghim `ultralytics==8.4.220` để cả nhóm train và export giống nhau. |
| [configs/data.yaml](configs/data.yaml) | Mẫu data.yaml với 11 lớp cố định của BTC. |
| [scripts/prepare_data.py](scripts/prepare_data.py) | Nhận một hoặc nhiều thư mục/zip dạng `images/` + `labels/`, kiểm tra nhãn, chia train/val với seed cố định, in số instance mỗi lớp và ghi data.yaml. |
| [train.py](train.py) | Train từ `yolo26n-seg.pt` pretrained, seed cố định, ghi `summary.json` với mask mAP từng lớp. |
| [configs/hyp.yaml](configs/hyp.yaml) | Ví dụ tham số augmentation truyền qua `--hyp`. |
| [export.py](export.py) | Xuất `model.onnx` fp32 640, kiểm tra bằng onnxruntime, đóng zip chỉ chứa `model.onnx` và chặn nếu quá 42 MB. |
| [evaluate.py](evaluate.py) | Chấm `.pt` hoặc `.onnx` trên tập val của mình trước khi dùng lượt nộp. |
| [predict.py](predict.py) | Chạy suy luận, lưu ảnh có mask và nhãn YOLO-seg để làm nhãn nháp. |

```bash
pip install -r requirements.txt
python scripts/prepare_data.py --src du_lieu.zip --out datasets/robotaxi
python train.py --data datasets/robotaxi/data.yaml --epochs 100 --batch 16
python export.py --weights runs/segment/baseline/weights/best.pt
python evaluate.py --model submission/model.onnx --data datasets/robotaxi/data.yaml
```

Lưu ý:
- `export.py` đang dùng tham số mặc định của Ultralytics. Khi có notebook mẫu của BTC, chép đúng lời gọi `model.export(...)` của notebook vào đây.
- Điểm val nội bộ chỉ để so sánh các phiên bản dữ liệu với nhau, không phải điểm private.
- Nếu dữ liệu là các frame cắt từ cùng video, chia ngẫu nhiên sẽ làm điểm val cao giả. Khi đó nên tách theo video.
- Mỗi bộ dữ liệu công khai đưa vào cần ghi lại tên, link, giấy phép, số ảnh và cách ánh xạ về 11 lớp cho báo cáo.

## CI/CD cho nhóm

Workflow kiểm tra cấu hình GitHub Actions và lỗi khoảng trắng trong phần thay đổi, sau đó tạo và kiểm tra gói ZIP từ commit đang chạy. [Xem workflow](.github/workflows/ci-cd.yml)

| Sự kiện | Kết quả |
| --- | --- |
| Push lên nhánh làm việc như `feat/truong/demo-api` | Chạy CI trên commit của nhánh. |
| Mở hoặc cập nhật pull request vào `main` | Chạy check **Validate pull request** trên kết quả merge thử. |
| Push vào `main` | Chạy lại CI và lưu gói mã nguồn ở **Actions → Artifacts** trong lần chạy tương ứng. |
| Push tag dạng `vX.Y.Z` | Kiểm tra commit thuộc lịch sử của `main`, chạy CI rồi phát hành gói ZIP và checksum ở **Releases**. |

### Đẩy code lên nhánh riêng

Mỗi người tạo một nhánh từ `origin/main`. Đặt tên theo công việc, ví dụ `feat/truong/demo-api`.

```bash
git fetch origin
git switch -c feat/truong/demo-api origin/main
```

Sau khi commit các thay đổi trên nhánh riêng, push đúng tên nhánh để GitHub chạy CI.

```bash
git push -u origin feat/truong/demo-api
```

Khi sẵn sàng đưa code vào `main`, mở PR với nhánh đích là `main`, nhờ một thành viên review và đợi **Validate pull request** thành công. Nếu PR cần đồng bộ với `main`, dùng **Update branch** để chạy lại CI.

### Bảo vệ `main` trên GitHub

1. Push nhánh chứa pipeline và mở PR vào `main` để GitHub ghi nhận check **Validate pull request**.
2. Sau khi check chạy thành công, quản trị viên mở **Settings → Rules → Rulesets → New ruleset → Import a ruleset** và chọn [protect-main.json](.github/rulesets/protect-main.json).
3. Xác nhận ruleset đang ở trạng thái **Active** và chỉ nhắm vào `main`, rồi lưu. GitHub sẽ yêu cầu PR và CI đạt trước khi merge vào `main`.

### Chốt bản demo

Sau khi CI trên `main` thành công, gắn tag vào commit đã chốt. Ví dụ dưới đây dùng commit mới nhất trên `origin/main`.

```bash
git fetch origin main
git tag -a v0.1.0 -m "Hackathon v0.1.0" origin/main
git push origin v0.1.0
```

Mở **Releases** để tải `Hackathon_AITC-source.zip` và `SHA256SUMS.txt`. Gói chỉ chứa file đã được Git theo dõi tại commit đó. Dùng tag mới cho mỗi phiên bản.

Khi nhóm đưa ứng dụng vào repo, thêm bước cài dependency, lint và test trong job `ci` trước bước đóng gói. Hiện đích phát hành là GitHub Releases.
