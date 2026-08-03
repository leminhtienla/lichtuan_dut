# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/).
Phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

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

[Unreleased]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.2.0
[1.1.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.1.0
[1.0.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.0.0
