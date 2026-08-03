"""Logic tải & phân tích trang lichtuan.dut.udn.vn.

Tách riêng khỏi coordinator.py để có thể unit-test độc lập, không phụ
thuộc Home Assistant (chỉ cần beautifulsoup4).
"""
from __future__ import annotations

import hashlib
import re
from datetime import date, timedelta
from typing import Any

from bs4 import BeautifulSoup

from .const import BASE_URL


def get_academic_year(d: date) -> str:
    """Trả về năm học dạng '2025-2026'.

    Quy ước: năm học bắt đầu từ tháng 9. Vậy tháng 1-8 thuộc năm học
    (year-1)-(year), tháng 9-12 thuộc năm học (year)-(year+1).
    """
    if d.month >= 9:
        return f"{d.year}-{d.year + 1}"
    return f"{d.year - 1}-{d.year}"


def get_week_monday(d: date) -> date:
    """Trả về ngày Thứ Hai của tuần chứa ngày d."""
    return d - timedelta(days=d.weekday())


def build_week_url(monday: date) -> str:
    """Dựng URL lịch tuần cho ngày Thứ Hai đã cho."""
    year_str = get_academic_year(monday)
    return f"{BASE_URL}?week={monday.isoformat()}&year={year_str}"


def entry_hash(entry: dict[str, Any]) -> str:
    """Tạo mã băm ổn định cho một mục lịch, dùng để chống báo trùng."""
    raw = "|".join(
        [
            entry.get("date", ""),
            entry.get("time", ""),
            entry.get("content", ""),
            entry.get("host", ""),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_schedule(html: str, week_label: str = "") -> list[dict[str, Any]]:
    """Phân tích HTML trang lịch tuần, trả về danh sách các mục.

    Mỗi mục gồm: day (Thứ), date (ngày), time, content, participants,
    location, host, extra, week_label.
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="table")
    if table is None:
        return []
    tbody = table.find("tbody")
    if tbody is None:
        return []

    entries: list[dict[str, Any]] = []
    current_day = ""
    current_date = ""

    for tr in tbody.find_all("tr", recursive=False):
        tds = tr.find_all("td", recursive=False)
        if not tds:
            continue

        first_classes = tds[0].get("class", []) or []
        if "week" in first_classes:
            raw_parts = tds[0].get_text(separator="\n", strip=True).split("\n")
            parts = [_clean_text(p) for p in raw_parts if _clean_text(p)]
            current_day = parts[0] if parts else ""
            current_date = parts[1] if len(parts) > 1 else ""
            rest = tds[1:]
        else:
            rest = tds

        if len(rest) < 5:
            # Dòng không đủ cột dữ liệu (thời gian/nội dung/thành phần/địa điểm/chủ trì)
            continue

        time_txt = _clean_text(rest[0].get_text(separator=" ", strip=True))
        content_txt = _clean_text(rest[1].get_text(separator=" ", strip=True))
        participants_txt = _clean_text(rest[2].get_text(separator=" ", strip=True))
        location_txt = _clean_text(rest[3].get_text(separator=" ", strip=True))
        host_txt = _clean_text(rest[4].get_text(separator=" ", strip=True))
        extra_txt = _clean_text(rest[5].get_text(separator=" ", strip=True)) if len(rest) > 5 else ""

        if not any([time_txt, content_txt, participants_txt, location_txt, host_txt]):
            continue

        entries.append(
            {
                "day": current_day,
                "date": current_date,
                "time": time_txt,
                "content": content_txt,
                "participants": participants_txt,
                "location": location_txt,
                "host": host_txt,
                "extra": extra_txt,
                "week_label": week_label,
            }
        )

    return entries


def filter_by_keywords(
    entries: list[dict[str, Any]], keywords: list[str]
) -> list[dict[str, Any]]:
    """Lọc các mục có chứa (không phân biệt hoa/thường) ít nhất 1 từ khóa.

    Tìm trong các trường: content, participants, host, location.
    Trả về bản sao mỗi mục kèm trường 'matched_keywords'.
    """
    if not keywords:
        return []

    lowered_keywords = [(kw, kw.lower()) for kw in keywords if kw.strip()]
    results: list[dict[str, Any]] = []

    for entry in entries:
        haystack = " ".join(
            [
                entry.get("content", ""),
                entry.get("participants", ""),
                entry.get("host", ""),
                entry.get("location", ""),
            ]
        ).lower()

        matched = [kw for kw, kw_lower in lowered_keywords if kw_lower in haystack]
        if matched:
            new_entry = dict(entry)
            new_entry["matched_keywords"] = matched
            new_entry["id"] = entry_hash(entry)
            results.append(new_entry)

    return results
