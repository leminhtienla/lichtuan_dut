"""Calendar entity: hiển thị các mục lịch tuần đã khớp từ khóa dưới
dạng sự kiện lịch thật (có ngày/giờ bắt đầu-kết thúc), để xem trực
quan trên Lovelace Calendar card thay vì chỉ đọc số đếm trên sensor.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import homeassistant.util.dt as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LichTuanDutCoordinator
from .parser import parse_event_datetime


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LichTuanDutCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LichTuanDutCalendar(coordinator, entry)])


def _end_as_datetime(value: Any) -> datetime:
    """Chuẩn hóa end (date hoặc datetime) về datetime để so sánh/sắp xếp."""
    if isinstance(value, datetime):
        return value
    return dt_util.start_of_local_day(value) + timedelta(days=1)


def _start_as_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return dt_util.start_of_local_day(value)


class LichTuanDutCalendar(CoordinatorEntity[LichTuanDutCoordinator], CalendarEntity):
    """Lịch gồm mọi mục đang khớp bất kỳ nhóm từ khóa nào đã cấu hình.

    Lưu ý: chỉ hiển thị trong phạm vi các tuần đang được quét (tuần
    hiện tại + số 'tuần kiểm tra thêm' đã cấu hình trong Options),
    không phải toàn bộ lịch sử/tương lai của trường.
    """

    _attr_has_entity_name = True
    _attr_name = "Lịch cảnh báo từ khóa"
    _attr_icon = "mdi:calendar-text"

    def __init__(self, coordinator: LichTuanDutCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_calendar"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lịch Tuần DUT",
            manufacturer="lichtuan.dut.udn.vn (không chính thức)",
            model="Cảnh báo từ khóa",
        )

    def _build_events(self) -> list[CalendarEvent]:
        data = self.coordinator.data or {}
        tzinfo = dt_util.DEFAULT_TIME_ZONE
        events: list[CalendarEvent] = []

        for m in data.get("matches", []):
            start, end, all_day = parse_event_datetime(
                m.get("date", ""), m.get("time", "")
            )
            if start is None:
                continue

            if not all_day:
                start = start.replace(tzinfo=tzinfo)
                end = end.replace(tzinfo=tzinfo)

            kw = ", ".join(m.get("matched_keywords", []))
            variants = ", ".join(m.get("matched_variants", []))
            desc_lines = [f"Từ khóa khớp: {kw} ({variants})"]
            if m.get("participants"):
                desc_lines.append(f"Thành phần: {m['participants']}")
            if m.get("host"):
                desc_lines.append(f"Chủ trì: {m['host']}")
            if m.get("week_label"):
                desc_lines.append(f"Tuần: {m['week_label']}")

            events.append(
                CalendarEvent(
                    start=start,
                    end=end,
                    summary=m.get("content") or "(không có nội dung)",
                    description="\n".join(desc_lines),
                    location=m.get("location") or "",
                    uid=m.get("id"),
                )
            )

        events.sort(key=lambda e: _start_as_datetime(e.start))
        return events

    @property
    def event(self) -> CalendarEvent | None:
        """Sự kiện đang diễn ra hoặc sắp diễn ra gần nhất."""
        now = dt_util.now()
        upcoming = [e for e in self._build_events() if _end_as_datetime(e.end) >= now]
        return upcoming[0] if upcoming else None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Trả về các sự kiện nằm trong khoảng [start_date, end_date]."""
        result = []
        for e in self._build_events():
            e_start = _start_as_datetime(e.start)
            e_end = _end_as_datetime(e.end)
            if e_end >= start_date and e_start <= end_date:
                result.append(e)
        return result
