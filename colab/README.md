# Notebook Colab dùng chung

[Mở notebook trong Colab](https://colab.research.google.com/github/kieuwangtruong/Hackathon_AITC/blob/main/colab/shared.ipynb)

Đây là đường link duy nhất cả nhóm dùng. Colab đọc notebook thẳng từ nhánh `main` trên GitHub mỗi lần mở, nên:

- Notebook luôn khớp với `main`: khi một PR được merge, lần mở tiếp theo đã là bản mới. Ô đầu tiên cũng tải code mới nhất từ `main` mỗi lần chạy.
- Không ai sửa được bản dùng chung. Chỉnh sửa trong Colab chỉ nằm trong phiên của người đó. **File → Save a copy in Drive** tạo bản riêng, không ảnh hưởng người khác.
- Muốn đổi notebook hay code thì sửa trên nhánh riêng và mở PR vào `main`, giống mọi thay đổi khác.

Đừng chia sẻ notebook bằng nút **Share** của một bản lưu trên Drive. Bản đó sẽ không tự cập nhật theo `main`, và ai có quyền Editor đều sửa được.

## Chuẩn bị một lần

1. Chủ repo import [ruleset bảo vệ main](../.github/rulesets/protect-main.json) (xem README chính). Khi đó không ai push thẳng vào `main`, kể cả qua **File → Save a copy in GitHub** của Colab; mọi thay đổi phải qua PR và CI.
2. Tạo thư mục `Hackathon_AITC` trên Google Drive, đặt file dữ liệu vào `Hackathon_AITC/datasets/du_lieu.zip`. Nếu dùng chung một thư mục cho cả nhóm, chia sẻ thư mục đó rồi mỗi người **Add shortcut to Drive** vào `MyDrive`, hoặc sửa `DRIVE_DIR` trong ô 2.

## Chạy

1. **Runtime → Change runtime type → GPU**.
2. Chạy lần lượt các ô. Kết quả train nằm trong `DRIVE_DIR/runs/`, file zip nộp bài trong `DRIVE_DIR/submissions/<RUN_NAME>/`.

Repo đang để công khai nên Colab tải code không cần đăng nhập. Nếu chuyển repo sang riêng tư, cần cấu hình quyền truy cập Git trong Colab; không ghi token vào notebook.
