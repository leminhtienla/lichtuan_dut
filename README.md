# Lịch Tuần DUT - Cảnh báo từ khóa (Home Assistant custom integration)

Tích hợp tùy chỉnh cho Home Assistant, tự động kiểm tra định kỳ trang
**lịch công tác tuần** của Trường Đại học Bách khoa - Đại học Đà Nẵng
(`https://lichtuan.dut.udn.vn`) và **cảnh báo** khi có mục lịch chứa
các từ khóa do bạn chọn (tên người, khoa, bộ môn...).

## Tính năng

- Tự động tải trang lịch tuần theo lịch trình (mặc định mỗi 60 phút, có thể chỉnh 15–1440 phút).
- Có thể theo dõi thêm 1–3 tuần tiếp theo (nếu trang đã đăng lịch trước), ngoài tuần hiện tại.
- So khớp từ khóa (không phân biệt hoa/thường, có dấu) trong các cột: **Nội dung, Thành phần, Chủ trì, Địa điểm**.
- Chỉ cảnh báo cho **mục mới** (chưa từng thông báo trước đó) — tránh spam lặp lại mỗi lần quét.
- Gửi cảnh báo qua:
  - `persistent_notification` trong Home Assistant (luôn bật).
  - (Tùy chọn) một `notify` service bất kỳ, ví dụ `notify.mobile_app_dien_thoai_cua_ban`.
  - Bắn sự kiện `lichtuan_dut_match_found` để bạn tự viết automation nâng cao (TTS, đèn nhấp nháy, Telegram...).
- Một sensor `sensor.lich_tuan_dut_canh_bao_lich_tuan` hiển thị **số mục đang khớp**, kèm attribute chi tiết từng mục.

## Cài đặt qua HACS

1. Mở **HACS → góc trên bên phải → Custom repositories**.
2. Thêm URL repo GitHub của bạn (sau khi bạn đẩy code này lên GitHub), chọn loại **Integration**.
3. Tìm "Lịch Tuần DUT - Cảnh báo từ khóa" trong HACS, bấm **Download**.
4. Khởi động lại Home Assistant.
5. Vào **Cài đặt → Thiết bị & Dịch vụ → Thêm tích hợp**, tìm "Lịch Tuần DUT".
6. Nhập từ khóa, ví dụ:
   ```
   Lê Minh Tiến, Khoa Cơ khí Giao thông, Bộ môn: Kỹ thuật Ô tô
   ```
   và (tùy chọn) một `notify` service.

## Cài đặt thủ công (không qua HACS)

Copy toàn bộ thư mục `custom_components/lichtuan_dut/` vào thư mục
`config/custom_components/` của Home Assistant, khởi động lại, rồi làm
theo bước 5–6 ở trên.

## Ví dụ automation nâng cao (dùng sự kiện thay vì notify service)

```yaml
automation:
  - alias: "Cảnh báo lịch tuần DUT bằng loa"
    trigger:
      - platform: event
        event_type: lichtuan_dut_match_found
    action:
      - service: tts.speak
        target:
          entity_id: tts.piper
        data:
          media_player_entity_id: media_player.loa_phong_khach
          message: >
            Lịch tuần có mục mới liên quan tới {{ trigger.event.data.matched_keywords | join(', ') }}:
            {{ trigger.event.data.content }}, lúc {{ trigger.event.data.time }},
            tại {{ trigger.event.data.location }}.
```

## Phát hành phiên bản mới (để HACS hiện thông tin cập nhật)

HACS lấy **version** từ `manifest.json` để biết có bản mới hay không, và
lấy **nội dung "What's new"** từ GitHub Release tương ứng với tag đó.
Muốn người dùng thấy đầy đủ thông tin cập nhật khi bấm "Update" trong
HACS, làm theo đúng 3 bước sau mỗi khi sửa code:

1. Sửa `"version"` trong `custom_components/lichtuan_dut/manifest.json`
   (vd `1.0.0` → `1.1.0`, theo [semver](https://semver.org/lang/vi/):
   tăng số cuối cho bugfix, số giữa cho tính năng mới, số đầu cho thay
   đổi phá vỡ tương thích).
2. Thêm mục mới lên đầu `CHANGELOG.md`, ngay dưới `## [Unreleased]`:
   ```markdown
   ## [1.1.0] - 2026-09-01

   ### Thêm mới
   - Mô tả tính năng mới...

   ### Sửa lỗi
   - Mô tả bug đã fix...
   ```
3. Commit rồi tạo tag **đúng bằng** version (có tiền tố `v`) và đẩy lên:
   ```bash
   git add -A
   git commit -m "Release 1.1.0"
   git tag v1.1.0
   git push origin main --tags
   ```

Workflow `.github/workflows/release.yml` (đã có sẵn trong repo) sẽ tự
động: kiểm tra tag khớp với `manifest.json`, trích đúng đoạn changelog
của phiên bản đó, và tạo GitHub Release kèm nội dung — đây chính là
đoạn HACS sẽ hiển thị cho người dùng khi họ thấy có bản cập nhật.

Workflow `.github/workflows/validate.yml` chạy `hassfest` + `hacs
validate` mỗi lần push, giúp bắt lỗi cấu trúc integration sớm.

> Lưu ý: nếu quên bước 1 (không tăng version trong manifest.json) hoặc
> tag không khớp version, HACS sẽ không nhận ra có bản cập nhật, hoặc
> workflow release sẽ báo lỗi và không tạo release.

## Ghi chú kỹ thuật

- Nguồn dữ liệu là trang HTML công khai, không phải API chính thức —
  nếu trường thay đổi giao diện trang web, phần phân tích HTML
  (`parser.py`) có thể cần cập nhật lại.
- Trạng thái "đã cảnh báo" được lưu trong storage riêng của entry
  (`.storage/lichtuan_dut_<entry_id>_seen`) để không báo trùng sau khi
  khởi động lại HA.
- Yêu cầu thư viện `beautifulsoup4` (tự cài khi HA tải integration).
