# Hackathon_AITC

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
