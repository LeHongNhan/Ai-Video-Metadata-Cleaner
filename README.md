# AI Video Metadata Cleaner

Ứng dụng Windows chuyển đổi nhiều video trên máy tính, không cần tải video lên mạng. Mỗi video có thể được đặt tên riêng trước khi xuất. Các video chuyển đổi thành công có thể được đóng gói vào một file ZIP.

Ứng dụng tạo file MP4 mới bằng cách mã hóa lại video sang H.264 và âm thanh sang AAC. File gốc được giữ nguyên.

## Mở ứng dụng

Với bản portable, bạn giải nén toàn bộ rồi mở `AI Video Metadata Cleaner.exe`. Thư mục `_internal` cần nằm cạnh file EXE. Bản này không cần cài Python hay kết nối mạng khi sử dụng.

Nếu tự build từ mã nguồn, file EXE nằm trong `dist/AI Video Metadata Cleaner/`. Thư mục `dist/` không được đưa vào repository Git.

## Cài và chạy từ mã nguồn

Để chạy từ mã nguồn, bạn cần Windows 10/11 64-bit, Python 3.12 trở lên, FFmpeg và FFprobe. Bản FFmpeg cần hỗ trợ `libx264` và AAC.

1. Tải bản FFmpeg cho Windows từ nhà cung cấp được giới thiệu tại [trang tải FFmpeg](https://ffmpeg.org/download.html), chẳng hạn [Gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2. Đặt `ffmpeg.exe` và `ffprobe.exe` trong thư mục `tools/`, hoặc thêm thư mục chứa hai file vào `PATH`. Ứng dụng cũng nhận cấu trúc `tools/ffmpeg-…/bin/` sau khi giải nén.
3. Mở PowerShell tại thư mục dự án và chạy:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

Lệnh `py -3.12` dùng Python 3.12. Nếu đã cài phiên bản khác từ 3.12 trở lên, bạn có thể thay lệnh này bằng lệnh Python tương ứng trên máy.

Bạn cũng có thể chạy `setup.ps1` để tạo môi trường và cài thư viện, sau đó chạy `run.ps1`. Nếu PowerShell chặn script, bạn có thể dùng các lệnh Python ở trên.

## Chuyển đổi video

1. Nhấn **Thêm video…** hoặc kéo thả video vào cửa sổ. Ứng dụng nhận MP4, MOV, MKV, AVI, WEBM và M4V; mỗi đường dẫn chỉ được thêm một lần.
2. Bạn có thể sửa tên đầu ra trên từng dòng mà không cần nhập đuôi `.mp4`. Nếu để trống, ứng dụng dùng tên gốc kèm `-clean`; ví dụ `video01.mov` thành `video01-clean.mp4`.
3. Chọn thư mục đầu ra và chất lượng CRF. Mặc định là CRF 18; bạn cũng có thể chọn 20, 23 hoặc 26. Giá trị cao hơn thường tạo file nhỏ hơn.
4. Nhấn **Bắt đầu chuyển đổi**. Nếu tên không hợp lệ, trùng tên trong danh sách hoặc đã tồn tại trong thư mục đích, bạn cần sửa tên trước khi chạy. Ứng dụng không ghi đè file cũ.
5. Sau khi chuyển đổi, bạn có thể nhấn **TẢI TẤT CẢ (.ZIP)** và chọn nơi lưu. ZIP chứa những video thành công còn trong danh sách, với tên bạn đã đặt. Nếu ZIP đã tồn tại, bạn cần chọn tên khác.

Một video lỗi không dừng các video còn lại. Bạn có thể di chuột vào trạng thái lỗi để xem chi tiết và dùng nút **Xử lý lại video thất bại** để thử lại. Khi hủy, ứng dụng dọn file đang xử lý dở và giữ các file đã hoàn thành. Việc xóa một dòng khỏi danh sách không xóa file trên ổ đĩa.

Trong lúc xử lý, bạn không thể sửa danh sách, tên hoặc thiết lập, nhưng vẫn có thể dùng giao diện và nút hủy. Nếu đóng cửa sổ khi tác vụ đang chạy, ứng dụng bắt đầu hủy. Sau khi quá trình dọn dẹp kết thúc, bạn có thể đóng cửa sổ lại.

## File đầu ra và giới hạn

Thư mục làm việc mặc định là `%LOCALAPPDATA%\VideoConverter`, gồm `input`, `output`, `temp` và `logs`. Video gốc không được sao chép vào `input`. Bạn có thể chọn thư mục đầu ra khác trong ứng dụng.

Ứng dụng mã hóa một luồng video chính và tất cả luồng âm thanh; phụ đề, file đính kèm và các luồng dữ liệu khác không được xuất. Video không bị cắt khung hình, thay đổi độ phân giải hay ép lại FPS. Mỗi luồng âm thanh được mã hóa AAC ở 192 kbps mà không điều chỉnh âm lượng.

Video có chiều rộng hoặc chiều cao lẻ được xuất ở định dạng màu `yuv444p` để giữ nguyên kích thước. Một số trình phát phần cứng cũ có thể không hỗ trợ định dạng này. Video HDR hoặc 10-bit được chuyển sang 8-bit; ứng dụng không có xử lý HDR tone mapping chuyên dụng và không bảo đảm giữ nguyên các thuộc tính HDR hoặc màu sắc của mọi nguồn.

Sau khi mã hóa, FFprobe kiểm tra kích thước, số luồng âm thanh và thời lượng; FFmpeg giải mã toàn bộ file để phát hiện lỗi trước khi lưu kết quả. Bước này có thể mất thêm thời gian với video lớn.

File tạm nằm trong thư mục `.videoconverter-*` tại nơi lưu video hoặc ZIP và thường được dọn khi hoàn thành hay hủy. Nếu mất điện hoặc ứng dụng bị buộc đóng, thư mục tạm có thể còn lại; bạn có thể xóa khi không còn tác vụ nào đang chạy. ZIP dùng ZIP64 và lưu video mà không nén lại.

## Kiểm thử và build

Sau khi tạo môi trường và cài FFmpeg như hướng dẫn trên, bạn có thể chạy:

```powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m PyInstaller --noconfirm VideoConverter.spec
```

Bạn cũng có thể chạy `build.ps1` để cài các thư viện phát triển, kiểm thử rồi build. File EXE và các thành phần đi kèm nằm trong `dist/AI Video Metadata Cleaner/`. Script build cần tìm thấy cả `ffmpeg.exe` và `ffprobe.exe` trong `tools/`.

`requirements-lock.txt` ghi các phiên bản đã dùng trong môi trường kiểm thử. Các bài kiểm thử tạo video bằng FFmpeg; chi tiết và giới hạn kiểm thử được ghi trong [TESTING.md](TESTING.md).

Nếu phân phối ứng dụng, bạn cần xem giấy phép của PySide6/Qt và bản FFmpeg đang dùng. Bản FFmpeg có libx264 thường áp dụng GPL, với các yêu cầu về thông báo giấy phép và phân phối mã nguồn tùy theo bản build.

## Xử lý lỗi

- **Thiếu FFmpeg hoặc FFprobe:** kiểm tra hai file EXE trong `tools/` hoặc `PATH`, rồi mở lại ứng dụng.
- **Tên đầu ra bị trùng hoặc file đã tồn tại:** đổi tên video hoặc chọn thư mục khác.
- **Không đủ dung lượng hoặc quyền ghi:** giải phóng dung lượng hoặc chọn ổ đĩa khác. Cần đủ chỗ cho file xuất và ZIP; file tạm nằm trên ổ đĩa đích.
- **Không đọc hoặc chuyển đổi được video:** xem chi tiết trạng thái và file log tại `%LOCALAPPDATA%\VideoConverter\logs\app.log`. Thử mở file gốc bằng trình phát để kiểm tra.
- **Không tạo được ZIP:** kiểm tra các video đã hoàn thành còn ở vị trí cũ. Nếu file bị xóa hoặc di chuyển, hãy đưa file trở lại hoặc chuyển đổi lại.

## Cấu trúc mã nguồn

`main.py` khởi chạy ứng dụng; `ui/` chứa giao diện; `workers/` chạy tác vụ nền; `core/` xử lý video, file và ZIP; `utils/` quản lý tiến trình; `config/` chứa cấu hình và cách tìm FFmpeg.
