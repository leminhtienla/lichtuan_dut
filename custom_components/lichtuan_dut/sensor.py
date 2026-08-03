"""Sensor hiển thị kết quả lọc từ khóa lịch tuần DUT."""
from __future__ import annotations

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
    async_add_entities([LichTuanDutSensor(coordinator, entry)])


class LichTuanDutSensor(CoordinatorEntity[LichTuanDutCoordinator], SensorEntity):
    """Sensor: số mục lịch tuần hiện đang khớp từ khóa."""

    _attr_has_entity_name = True
    _attr_name = "Cảnh báo lịch tuần"
    _attr_icon = "mdi:calendar-alert"

    def __init__(self, coordinator: LichTuanDutCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_matches"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Lịch Tuần DUT",
            manufacturer="lichtuan.dut.udn.vn (không chính thức)",
            model="Cảnh báo từ khóa",
        )

    @property
    def native_value(self) -> int:
        data = self.coordinator.data or {}
        return len(data.get("matches", []))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        matches = data.get("matches", [])[:MAX_ATTR_ENTRIES]
        new_matches = data.get("new_matches", [])

        simplified = [
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
            for m in matches
        ]

        return {
            "keywords": self.coordinator.keywords,
            "total_entries_scanned": data.get("total_entries", 0),
            "matches_count": len(data.get("matches", [])),
            "new_matches_last_update": len(new_matches),
            "matches": simplified,
            "last_checked": datetime.now().isoformat(timespec="seconds"),
        }
