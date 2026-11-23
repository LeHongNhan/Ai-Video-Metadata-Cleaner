# Kết quả kiểm thử

Kiểm thử trên Windows với Python 3.12.10, PySide6 6.8.3 và FFmpeg Windows Essentials thực tế. PySide6 được cố định phiên bản để bản build tái lập ổn định.

`python -m pytest -q`: 7 bài kiểm thử đạt.

| Yêu cầu | Bằng chứng |
|---|---|
| Một/nhiều video | FFmpeg tạo clip thật, core và GUI chuyển đổi thành công |
| Mặc định / để trống / tên mới | Kiểm tra `-clean`, trường rỗng, tên tiếng Việt và `.mp4` |
| Trùng tên / tên Windows lỗi / file có sẵn | Chặn trước khi xử lý; kiểm tra cả file được chương trình khác tạo giữa lượt chuyển đổi |
| Một video hỏng không dừng lượt | Chạy file tốt và file hỏng qua Worker/GUI, kết quả độc lập |
| ZIP chỉ chứa kết quả thành công, đúng tên | Đọc ZIP, kiểm CRC, so sánh từng byte với file xuất |
| Video phát/âm thanh | Giải mã toàn bộ kết quả không lỗi; hai luồng audio; so thời điểm bắt đầu audio/video sai lệch dưới 50 ms với mẫu thử |
| File gốc không đổi | SHA-256 trước và sau |
| Giao diện không treo | QTimer vẫn phát sự kiện khi worker chuyển đổi; video raw 1080p trên 150 MB; hủy khi đang chạy |
| Dọn file tạm | Kiểm tra sau hủy chuyển đổi, hủy ZIP giữa chừng và xung đột đầu ra |
| Dark/Light | Chụp giao diện thực tế trong `tests/ui-dark.png`, `tests/ui-light.png` |

Phạm vi: mẫu thử ngắn, không thay thế thử nghiệm bằng toàn bộ kho video thực tế. Chưa xác minh nghe/nhìn thủ công từng codec, HDR, nguồn quay điện thoại hoặc video dài nhiều giờ. Các kiểm tra timestamp và giải mã xác nhận tính kỹ thuật trên mẫu; không khẳng định đồng bộ tuyệt đối với mọi file nguồn bị lỗi.

Kiểm tra bản đóng gói: chạy EXE với `--self-test <đường-dẫn-json>`; mở giao diện, tìm FFmpeg/FFprobe được bundle, tạo video thật, chuyển đổi, tạo/đọc ZIP, ghi báo cáo JSON và thoát. Chế độ này chỉ chạy khi truyền tham số rõ ràng.

Bản EXE cuối cùng đã vượt qua kiểm tra trên, thoát với mã 0. Báo cáo: `tests/packaged-final-report.json`. Trong môi trường kiểm thử bị giới hạn quyền ghi, LOCALAPPDATA được chuyển sang `tests/runtime`; khi mở ứng dụng bình thường, thư mục dữ liệu dùng LocalAppData của người dùng Windows.
