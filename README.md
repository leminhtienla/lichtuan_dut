# Lịch Tuần DUT - Cảnh báo từ khóa (Home Assistant custom integration)

<p align="center">
  <img src="custom_components/lichtuan_dut/brand/logo.png" alt="Logo Trường Đại học Bách khoa - Đại học Đà Nẵng" width="180">
</p>

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
6. Nhập các nhóm từ khóa (mỗi dòng 1 nhóm, xem mục "Cấu hình từ khóa" bên dưới để biết cách gộp biến thể/viết tắt), ví dụ:
   ```
   Lê Minh Tiến: Lê Minh Tiến, LMT, Thầy Tiến
   Khoa Cơ khí Giao thông: Khoa Cơ khí Giao thông, CKGT
   Bộ môn Kỹ thuật Ô tô: Kỹ thuật Ô tô, KTOT
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

## Xem nội dung / ngày giờ chi tiết để lên kế hoạch

Sensor chỉ hiện **số lượng** mục khớp làm state chính (để dễ dùng
trong automation/điều kiện), nhưng chi tiết đầy đủ (ngày, giờ, nội
dung, địa điểm, chủ trì) luôn có sẵn ở 3 nơi:

1. **Tin nhắn cảnh báo** (`persistent_notification` / notify service):
   liệt kê thẳng ngày, giờ, nội dung, địa điểm cho từng mục mới.
2. **Attribute `matches` của sensor** (cả sensor tổng lẫn sensor theo
   từng nhóm từ khóa): danh sách đầy đủ, dùng được trong template,
   Markdown card, hoặc automation.
3. **Entity `calendar.lich_canh_bao_tu_khoa`** (mới từ v1.3.0): mỗi
   mục khớp trở thành **1 sự kiện lịch thật** (có giờ bắt đầu/kết
   thúc), xem trực tiếp trên Lovelace bằng Calendar card — đây là
   cách trực quan nhất để biết "việc gì, lúc nào" mà lên kế hoạch:

   ```yaml
   type: calendar
   entities:
     - calendar.lich_canh_bao_tu_khoa
   ```

   Quy tắc suy ra giờ: nếu cột "THỜI GIAN" có 2 mốc (vd `08:00 -
   10:00`) thì lấy đúng khoảng đó; nếu chỉ có 1 mốc (vd `07:00`) thì
   mặc định kéo dài 1 tiếng; nếu không có giờ nào thì coi là sự kiện
   **cả ngày**.

   > Lưu ý: lịch chỉ hiển thị trong phạm vi các tuần đang được quét
   > (tuần hiện tại + "Số tuần kiểm tra thêm" trong Options), không
   > phải toàn bộ lịch sử/tương lai của trường.

## Cấu hình từ khóa (hỗ trợ viết tắt / biến thể)

Mỗi **dòng** trong ô "Danh sách nhóm từ khóa" là **một nhóm**, và mỗi
nhóm sẽ có **đúng 1 sensor riêng**. Cú pháp mỗi dòng:

```
Nhãn hiển thị: biến thể 1, biến thể 2, biến thể 3
```

Gộp tên đầy đủ + các cách viết tắt/gọi khác vào cùng 1 nhóm để không bị
tạo tràn lan nhiều sensor cho cùng một đối tượng. Ví dụ thực tế:

```
Lê Minh Tiến: Lê Minh Tiến, LMT, Thầy Tiến
Khoa Cơ khí Giao thông: Khoa Cơ khí Giao thông, CKGT, Khoa CKGT
Bộ môn Kỹ thuật Ô tô: Kỹ thuật Ô tô, KTOT, Bộ môn Ô tô
```

→ Tạo ra 3 sensor: `Cảnh báo: Lê Minh Tiến`, `Cảnh báo: Khoa Cơ khí Giao thông`, `Cảnh báo: Bộ môn Kỹ thuật Ô tô`, cộng thêm 1 sensor tổng `Cảnh báo lịch tuần (tổng)`.

Nếu một dòng không có dấu `:`, cả dòng được hiểu là 1 từ khóa đơn
(không có biến thể riêng) — vẫn hợp lệ, ví dụ:
```
Đảng ủy
```

**Cách so khớp:**
- Biến thể dài / có dấu cách (tên đầy đủ, cụm từ...): so khớp kiểu
  "chuỗi con", không phân biệt hoa/thường — như tìm kiếm thông thường.
- Biến thể là **viết tắt toàn chữ HOA ngắn** (2–8 ký tự, vd `CKGT`,
  `LMT`, `KTOT`): so khớp có **ranh giới từ** + phân biệt hoa/thường,
  để tránh khớp nhầm khi các chữ đó vô tình dính liền trong một từ
  khác không liên quan. Vì vậy nên viết đúng dạng VIẾT HOA cho các
  biến thể viết tắt để được áp dụng quy tắc an toàn này.

## Có sensor riêng cho từng nhóm không? Đổi cấu hình có tự áp dụng không?

- Có — mỗi nhóm/dòng cấu hình sẽ có 1 sensor riêng, cộng 1 sensor tổng.
- Có — mỗi khi bạn sửa Options (từ khóa, tần suất, notify service...),
  Home Assistant tự **reload toàn bộ** integration (qua
  `add_update_listener`), nên danh sách sensor theo nhóm tự động
  thêm/bớt đúng theo cấu hình mới ngay sau khi lưu, không cần khởi
  động lại HA hay thao tác gì thêm.

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

- File logo được lưu tại `custom_components/lichtuan_dut/brand/logo.png`
  (+ `icon.png`, bản `@2x`, nền đã xử lý trong suốt) theo đúng kích
  thước chuẩn của
  [home-assistant/brands](https://github.com/home-assistant/brands)
  (icon 256×256, có bản 512×512 cho màn hình nét cao).
- **Quan trọng:** logo **sẽ hiển thị trên GitHub/README** ngay, nhưng
  **sẽ KHÔNG tự hiển thị** trong HACS hay trang Thiết bị & Dịch vụ của
  Home Assistant — cả hai lấy icon từ CDN `home-assistant/brands`,
  không đọc file trong repo này. Xem hướng dẫn từng bước để submit PR
  vào repo đó tại **[`BRANDS_SUBMISSION.md`](./BRANDS_SUBMISSION.md)**
  (đã chuẩn bị sẵn thư mục đúng cấu trúc trong `brands_submission/`).
  Với dùng cá nhân không public, có thể bỏ qua — không ảnh hưởng chức năng.
- Nguồn dữ liệu là trang HTML công khai, không phải API chính thức —
  nếu trường thay đổi giao diện trang web, phần phân tích HTML
  (`parser.py`) có thể cần cập nhật lại.
- Trạng thái "đã cảnh báo" được lưu trong storage riêng của entry
  (`.storage/lichtuan_dut_<entry_id>_seen`) để không báo trùng sau khi
  khởi động lại HA.
- Yêu cầu thư viện `beautifulsoup4` (tự cài khi HA tải integration).
