# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/).
Phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

## [1.3.3] - 2026-08-03

### Thay đổi
- Bỏ thư mục `brands_submission/` và `BRANDS_SUBMISSION.md` (không cần thiết cho dùng cá nhân). Logo vẫn giữ ở `custom_components/lichtuan_dut/brand/` để hiển thị trên GitHub/README.

## [1.3.2] - 2026-08-03

### Thay đổi
- Chuyển thư mục logo từ `assets/` (gốc repo) sang `custom_components/lichtuan_dut/brand/`, đồng bộ đúng theo convention của dự án tham khảo `cpc-evn` (cùng tác giả). Cập nhật lại đường dẫn ảnh trong README.

## [1.3.1] - 2026-08-03

### Sửa lỗi / Cải thiện
- Xử lý nền trắng của logo thành **trong suốt** (giữ viền vàng + chữ đỏ/xanh dương), tránh mảng trắng chói khi Home Assistant ở dark mode.
- Thêm `brands_submission/custom_integrations/lichtuan_dut/` — thư mục đã đóng gói sẵn đúng cấu trúc để copy thẳng vào fork của `home-assistant/brands`.
- Thêm `BRANDS_SUBMISSION.md`: hướng dẫn từng bước fork → copy → PR để logo hiển thị thật trong HACS/Home Assistant UI (icon trong `assets/` chỉ hiện trên GitHub, không tự hiện trong app).

## [1.3.0] - 2026-08-03

### Thêm mới
- **Calendar entity** (`calendar.lich_canh_bao_tu_khoa`): mỗi mục lịch khớp từ khóa trở thành 1 sự kiện lịch thật, xem được trực tiếp trên Lovelace bằng Calendar card — cách trực quan nhất để biết nội dung/ngày/giờ mà lên kế hoạch, thay vì chỉ đọc số đếm trên sensor.
  - Suy luận giờ bắt đầu/kết thúc từ cột "THỜI GIAN": có khoảng giờ → dùng đúng khoảng; chỉ 1 mốc giờ → mặc định 1 tiếng; không có giờ → sự kiện cả ngày.
  - Mô tả sự kiện gồm: từ khóa/biến thể đã khớp, thành phần, chủ trì, tuần.
- Hàm `parse_event_datetime()` trong `parser.py` (thuần Python, có thể unit-test độc lập) để chuyển cột ngày/giờ thô thành `start`/`end` chuẩn cho lịch.

## [1.2.1] - 2026-08-03

### Thêm mới
- Bổ sung logo Trường ĐHBK Đà Nẵng vào repo (`assets/logo.png`, `assets/icon.png` + bản `@2x`) và hiển thị trong README.
- Ghi chú rõ trong README: logo chỉ hiện trên GitHub, muốn hiện trong giao diện HACS/Home Assistant cần được duyệt qua repo `home-assistant/brands`.

## [1.2.0] - 2026-08-03

### Thêm mới
- **Nhóm từ khóa có biến thể/viết tắt**: cấu hình dạng nhiều dòng, mỗi dòng là 1 nhóm — `Nhãn: biến thể 1, biến thể 2, ...`. Ví dụ:
  ```
  Lê Minh Tiến: Lê Minh Tiến, LMT, Thầy Tiến
  Khoa Cơ khí Giao thông: Khoa Cơ khí Giao thông, CKGT
  ```
  → Chỉ tạo **1 sensor cho cả nhóm**, khớp nếu bất kỳ biến thể nào xuất hiện.
- Ô nhập từ khóa trong UI đổi sang **nhiều dòng** (multiline) thay vì 1 dòng.
- Với biến thể là **viết tắt toàn chữ HOA ngắn** (2–8 ký tự, vd `CKGT`, `LMT`): so khớp có **ranh giới từ** (word boundary) + phân biệt hoa/thường, để tránh khớp nhầm vào giữa chữ khác (vd không khớp "xCKGTx"). Biến thể dài/thường vẫn so khớp kiểu chuỗi con như cũ.
- Attribute `matched_variants` trên mỗi mục khớp, cho biết chính xác biến thể nào đã khớp (bên cạnh `matched_keywords` là tên nhãn nhóm).

### Thay đổi không tương thích ngược (breaking change)
- Cấu hình từ khóa cũ dạng "kw1, kw2, kw3" (1 dòng, phân tách bằng dấu phẩy) cần chuyển sang **mỗi từ khóa 1 dòng** sau khi cập nhật, nếu không cả chuỗi sẽ bị hiểu thành 1 nhóm duy nhất. Vào Options và định dạng lại là đủ.

## [1.1.0] - 2026-08-03

### Thêm mới
- Tạo 1 sensor riêng cho **mỗi từ khóa** đã cấu hình (`Cảnh báo: <từ khóa>`), bên cạnh sensor tổng hợp cũ (nay đổi tên thành `Cảnh báo lịch tuần (tổng)`).
- `unique_id` của sensor theo từ khóa dựa trên nội dung từ khóa (hash), không theo vị trí — thêm/bớt từ khóa khác không làm mất lịch sử/thống kê của các từ khóa còn lại.

### Xác nhận hành vi
- Khi đổi Options (từ khóa, tần suất, notify service...), config entry **tự reload toàn bộ** (đã có sẵn từ 1.0.0 qua `add_update_listener`) → danh sách sensor theo từ khóa tự động thêm/bớt đúng theo cấu hình mới, không cần thao tác gì thêm.

## [1.0.0] - 2026-08-03

### Thêm mới
- Phát hành lần đầu.
- Tích hợp tự động tải lịch tuần từ `lichtuan.dut.udn.vn` theo chu kỳ cấu hình được (15–1440 phút).
- Lọc theo danh sách từ khóa tùy chỉnh (Nội dung, Thành phần, Chủ trì, Địa điểm).
- Tùy chọn quét thêm 0–3 tuần kế tiếp.
- Chống báo trùng: chỉ cảnh báo mục lịch **mới**, lưu trạng thái qua Home Assistant Storage.
- Gửi cảnh báo qua `persistent_notification` + tùy chọn `notify` service riêng.
- Bắn sự kiện `lichtuan_dut_match_found` để dùng trong automation nâng cao.
- Sensor `Cảnh báo lịch tuần` hiển thị số mục khớp + chi tiết từng mục.
- Cấu hình hoàn toàn qua UI (Config Flow + Options Flow), hỗ trợ tiếng Việt/Anh.

[Unreleased]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/compare/v1.3.3...HEAD
[1.3.3]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.3.3
[1.3.2]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.3.2
[1.3.1]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.3.1
[1.3.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.3.0
[1.2.1]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.2.1
[1.2.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.2.0
[1.1.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.1.0
[1.0.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.0.0
