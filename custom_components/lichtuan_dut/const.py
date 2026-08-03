"""Hằng số cho tích hợp Lịch Tuần DUT - Cảnh báo từ khóa."""
from __future__ import annotations

DOMAIN = "lichtuan_dut"

# ---- Cấu hình do người dùng nhập ----
CONF_KEYWORDS = "keywords"
CONF_SCAN_INTERVAL = "scan_interval"  # phút
CONF_WEEKS_AHEAD = "weeks_ahead"  # 0 = chỉ tuần này, 1 = +1 tuần, ...
CONF_NOTIFY_SERVICE = "notify_service"  # vd: notify.mobile_app_xxx (để trống nếu không dùng)

DEFAULT_SCAN_INTERVAL = 60  # phút
DEFAULT_WEEKS_AHEAD = 0
MIN_SCAN_INTERVAL = 15
MAX_SCAN_INTERVAL = 1440
MAX_WEEKS_AHEAD = 3

BASE_URL = "https://lichtuan.dut.udn.vn/home"

# Sự kiện HA bắn ra khi có mục lịch mới khớp từ khóa (dùng cho automation nâng cao)
EVENT_MATCH_FOUND = f"{DOMAIN}_match_found"

# Giới hạn số mục lưu trong storage để tránh phình to theo thời gian
MAX_STORED_HASHES = 1000

STORAGE_VERSION = 1
STORAGE_KEY_TEMPLATE = f"{DOMAIN}_{{entry_id}}_seen"
