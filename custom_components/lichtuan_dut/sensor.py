"""Sensor hiển thị kết quả lọc từ khóa lịch tuần DUT.

Tạo 2 loại entity:
- 1 sensor tổng hợp: tổng số mục đang khớp (bất kỳ từ khóa nào).
- 1 sensor cho MỖI từ khóa đã cấu hình: số mục khớp riêng từ khóa đó.

Khi người dùng đổi từ khóa trong Options, config entry được reload toàn
bộ (xem __init__.py) nên danh sách sensor theo từ khóa tự động cập
nhật lại (thêm/bớt) theo cấu hình mới — không cần thao tác gì thêm.
"""
from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LichTuanDutCoordinator

# Số mục tối đa đưa vào attributes để tránh vượt giới hạn state attributes của HA
MAX_ATTR_ENTRIES = 25


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator: LichTuanDutCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [LichTuanDutTotalSensor(coordinator, entry)]
    for label in coordinator.keyword_labels:
        entities.append(LichTuanDutKeywordSensor(coordinator, entry, label))

    async_add_entities(entities)


def _device_info(entry: ConfigEntry) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Lịch Tuần DUT",
        manufacturer="lichtuan.dut.udn.vn (không chính thức)",
        model="Cảnh báo từ khóa",
    )


def _simplify(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "day": m.get("day"),
            "date": m.get("date"),
            "time": m.get("time"),
            "content": m.get("content"),
            "location": m.get("location"),
            "host": m.get("host"),
            "matched_keywords": m.get("matched_keywords"),
            "week": m.get("week_label"),
        }
        for m in matches[:MAX_ATTR_ENTRIES]
    ]


class LichTuanDutTotalSensor(CoordinatorEntity[LichTuanDutCoordinator], SensorEntity):
    """Sensor tổng hợp: tổng số mục đang khớp (mọi từ khóa gộp lại)."""

    _attr_has_entity_name = True
    _attr_name = "Cảnh báo lịch tuần (tổng)"
    _attr_icon = "mdi:calendar-alert"

    def __init__(self, coordinator: LichTuanDutCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_matches_total"
        self._attr_device_info = _device_info(entry)

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        return len(data.get("matches", []))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        matches = data.get("matches", [])
        new_matches = data.get("new_matches", [])

        return {
            "keyword_groups": self.coordinator.keyword_groups,
            "total_entries_scanned": data.get("total_entries", 0),
            "matches_count": len(matches),
            "new_matches_last_update": len(new_matches),
            "matches": _simplify(matches),
            "last_checked": datetime.now().isoformat(timespec="seconds"),
        }


class LichTuanDutKeywordSensor(CoordinatorEntity[LichTuanDutCoordinator], SensorEntity):
    """Sensor riêng cho 1 NHÓM từ khóa (nhãn + các biến thể/viết tắt).

    Ví dụ nhóm "Lê Minh Tiến" gồm biến thể ["Lê Minh Tiến", "LMT", ...]
    -> chỉ 1 sensor duy nhất, khớp bất kỳ biến thể nào trong nhóm.
    """

    _attr_has_entity_name = True
    _attr_icon = "mdi:calendar-search"

    def __init__(
        self, coordinator: LichTuanDutCoordinator, entry: ConfigEntry, label: str
    ) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._label = label
        self._attr_name = f"Cảnh báo: {label}"
        # unique_id ổn định theo NHÃN nhóm (không theo vị trí trong danh sách)
        # để không mất lịch sử/thống kê nếu người dùng thêm/bớt nhóm khác,
        # hoặc chỉ sửa biến thể bên trong nhóm mà giữ nguyên nhãn.
        kw_hash = hashlib.sha1(label.strip().lower().encode("utf-8")).hexdigest()[:12]
        self._attr_unique_id = f"{entry.entry_id}_keyword_{kw_hash}"
        self._attr_device_info = _device_info(entry)

    @property
    def _keyword_matches(self) -> list[dict[str, Any]]:
        data = self.coordinator.data or {}
        matches = data.get("matches", [])
        return [m for m in matches if self._label in m.get("matched_keywords", [])]

    @property
    def native_value(self) -> int:
        return len(self._keyword_matches)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        new_matches = [
            m
            for m in data.get("new_matches", [])
            if self._label in m.get("matched_keywords", [])
        ]
        matches = self._keyword_matches

        # Lấy danh sách biến thể đang cấu hình cho nhóm này (để hiển thị tham khảo)
        variants: list[str] = []
        for g in self.coordinator.keyword_groups:
            if g["label"] == self._label:
                variants = g["variants"]
                break

        return {
            "label": self._label,
            "variants": variants,
            "matches_count": len(matches),
            "new_matches_last_update": len(new_matches),
            "matches": _simplify(matches),
            "last_checked": datetime.now().isoformat(timespec="seconds"),
        }
