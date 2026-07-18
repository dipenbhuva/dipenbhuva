#!/usr/bin/env python3
"""Fetch public GitHub contribution-calendar data without a token."""

from __future__ import annotations

import json
import os
import re
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup


USERNAME = os.environ.get("GITHUB_USERNAME", "dipenbhuva")
OUTPUT = Path("data/contributions.json")
COUNT_RE = re.compile(r"([0-9][0-9,]*) contributions?")


def count_from_cell(cell, tooltip_text: str = "") -> int:
    for attr in ("data-count", "data-contribution-count"):
        value = cell.get(attr)
        if value and value.isdigit():
            return int(value)

    text = " ".join(
        value
        for value in (
            cell.get("aria-label"),
            cell.get("title"),
            cell.get_text(" ", strip=True),
            tooltip_text,
        )
        if value
    )
    if "No contributions" in text:
        return 0
    match = COUNT_RE.search(text)
    return int(match.group(1).replace(",", "")) if match else 0


def contribution_cells(username: str) -> list[dict[str, object]]:
    url = f"https://github.com/users/{username}/contributions"
    response = requests.get(
        url,
        headers={
            "User-Agent": "profile-readme-contribution-renderer",
            "Accept": "text/html",
        },
        timeout=20,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    days = []
    tooltips = {
        tooltip.get("for"): tooltip.get_text(" ", strip=True)
        for tooltip in soup.select("tool-tip[for]")
    }

    for cell in soup.select("[data-date]"):
        raw_date = cell.get("data-date")
        if not raw_date:
            continue
        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        except ValueError:
            continue
        count = count_from_cell(cell, tooltips.get(cell.get("id"), ""))
        days.append(
            {
                "date": parsed_date.isoformat(),
                "count": count,
                "level": int(cell.get("data-level") or 0),
            }
        )
    return sorted(days, key=lambda day: str(day["date"]))


def streaks(days: list[dict[str, object]]) -> tuple[int, int]:
    counts = {datetime.strptime(str(day["date"]), "%Y-%m-%d").date(): int(day["count"]) for day in days}
    if not counts:
        return 0, 0

    all_dates = [min(counts)]
    while all_dates[-1] < max(counts):
        all_dates.append(all_dates[-1] + timedelta(days=1))

    longest = 0
    running = 0
    for current in all_dates:
        if counts.get(current, 0) > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0

    current = 0
    cursor = max(counts)
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)
    return current, longest


def monthly_totals(days: list[dict[str, object]]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for day in days:
        month = str(day["date"])[:7]
        totals[month] += int(day["count"])
    return dict(sorted(totals.items()))


def main() -> None:
    days = contribution_cells(USERNAME)
    today = date.today()
    cutoff = today - timedelta(days=370)
    days = [
        day
        for day in days
        if cutoff <= datetime.strptime(str(day["date"]), "%Y-%m-%d").date() <= today
    ]
    current_streak, longest_streak = streaks(days)
    best = max(days, key=lambda day: int(day["count"]), default={"date": None, "count": 0})
    total = sum(int(day["count"]) for day in days)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "total_last_year": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best,
        "monthly_totals": monthly_totals(days),
        "days": days,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(days)} days")


if __name__ == "__main__":
    main()
