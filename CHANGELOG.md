# Changelog

Định dạng theo [Keep a Changelog](https://keepachangelog.com/vi/1.0.0/).
Phiên bản theo [Semantic Versioning](https://semver.org/lang/vi/).

## [Unreleased]

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

[Unreleased]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/YOUR_GITHUB_USERNAME/lichtuan_dut/releases/tag/v1.0.0
