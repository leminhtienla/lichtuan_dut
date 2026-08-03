"""Config flow cho Lịch Tuần DUT - Cảnh báo từ khóa."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    CONF_KEYWORDS,
    CONF_NOTIFY_SERVICE,
    CONF_SCAN_INTERVAL,
    CONF_WEEKS_AHEAD,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_WEEKS_AHEAD,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MAX_WEEKS_AHEAD,
    MIN_SCAN_INTERVAL,
)
from .parser import parse_keyword_groups

KEYWORDS_EXAMPLE = (
    "Lê Minh Tiến: Lê Minh Tiến, LMT, Thầy Tiến\n"
    "Khoa Cơ khí Giao thông: Khoa Cơ khí Giao thông, CKGT\n"
    "Bộ môn Kỹ thuật Ô tô: Kỹ thuật Ô tô, KTOT"
)


def _build_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_KEYWORDS, default=defaults.get(CONF_KEYWORDS, "")
            ): TextSelector(
                TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True)
            ),
            vol.Required(
                CONF_SCAN_INTERVAL,
                default=defaults.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    step=5,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="phút",
                )
            ),
            vol.Optional(
                CONF_WEEKS_AHEAD,
                default=defaults.get(CONF_WEEKS_AHEAD, DEFAULT_WEEKS_AHEAD),
            ): NumberSelector(
                NumberSelectorConfig(
                    min=0, max=MAX_WEEKS_AHEAD, step=1, mode=NumberSelectorMode.BOX
                )
            ),
            vol.Optional(
                CONF_NOTIFY_SERVICE, default=defaults.get(CONF_NOTIFY_SERVICE, "")
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.TEXT)),
        }
    )


def _validate_keywords(raw: str) -> list[dict[str, Any]]:
    """Parse & trả về danh sách nhóm; rỗng nếu không có nhóm hợp lệ nào."""
    return parse_keyword_groups(raw)


class LichTuanDutConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow chính (bước thêm mới)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        errors: dict[str, str] = {}

        if user_input is not None:
            groups = _validate_keywords(user_input[CONF_KEYWORDS])
            if not groups:
                errors["base"] = "no_keywords"
            else:
                return self.async_create_entry(
                    title="Lịch Tuần DUT - Cảnh báo từ khóa",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(
                user_input or {CONF_KEYWORDS: KEYWORDS_EXAMPLE}
            ),
            errors=errors,
            description_placeholders={"example": KEYWORDS_EXAMPLE},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return LichTuanDutOptionsFlow(config_entry)


class LichTuanDutOptionsFlow(OptionsFlow):
    """Cho phép sửa từ khóa / tần suất / notify sau khi đã cài."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> Any:
        errors: dict[str, str] = {}
        current = {**self._config_entry.data, **self._config_entry.options}

        if user_input is not None:
            groups = _validate_keywords(user_input[CONF_KEYWORDS])
            if not groups:
                errors["base"] = "no_keywords"
            else:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(user_input or current),
            errors=errors,
            description_placeholders={"example": KEYWORDS_EXAMPLE},
        )
