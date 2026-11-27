# Notebook Colab dùng chung

Đây là **notebook chính thức của BTC** (v3.0.0), đã điền `TEAM_ID = 48`, đường dẫn dữ liệu và thư mục kết quả trên Drive.

**Link duy nhất cả nhóm dùng:** [mở notebook](https://colab.research.google.com/github/kieuwangtruong/Hackathon_AITC/blob/main/colab/shared.ipynb)

- Luôn là bản mới nhất: Colab đọc notebook từ `main` mỗi lần mở.
- Không ai sửa được bản chung: chỉnh sửa chỉ nằm trong phiên của bạn. Muốn đổi thì mở PR.
- Đừng chia sẻ bản lưu trên Drive. Bản đó không tự cập nhật và ai cũng sửa được.

## Chạy

1. Đặt dữ liệu ở `MyDrive/Hackathon_AITC/datasets/du_lieu.zip` (hoặc sửa `DATASET_PATH` ở ô tham số).
2. **Runtime → Change runtime type → T4 GPU**, rồi **Run all**.
3. `best.pt`, `submission.zip` và `run_report.json` được chép vào `MyDrive/Hackathon_AITC/ket_qua/`. Mỗi lần chạy sẽ ghi đè, nên đổi tên file muốn giữ.
4. Không sửa các ô thư viện và Bước 4: đó là phần kiểm tra của hệ thống chấm.
