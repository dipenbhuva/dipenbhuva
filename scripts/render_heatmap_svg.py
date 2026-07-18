#!/usr/bin/env python3
"""Render contribution data as an animated SVG heatmap."""

from __future__ import annotations

import calendar
import json
from datetime import date, datetime, timedelta
from pathlib import Path


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]


def sunday_index(day: date) -> int:
    return (day.weekday() + 1) % 7


def svg_text(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def level_for_count(count: int, raw_level: int) -> int:
    if count <= 0:
        return 0
    return max(1, min(5, raw_level + 1))


def main() -> None:
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    days = {
        datetime.strptime(day["date"], "%Y-%m-%d").date(): day
        for day in payload.get("days", [])
    }
    end = max(days) if days else date.today()
    start = end - timedelta(days=52 * 7 + sunday_index(end))

    width = 860
    height = 204
    cell = 10
    gap = 4
    x0 = 58
    y0 = 54

    rects = []
    month_labels = []
    seen_months = set()
    for week in range(53):
        week_start = start + timedelta(days=week * 7)
        if week_start.month not in seen_months and week_start.day <= 7:
            seen_months.add(week_start.month)
            month_labels.append(
                f'<text class="month" x="{x0 + week * (cell + gap)}" y="40">'
                f"{calendar.month_abbr[week_start.month]}</text>"
            )
        for weekday in range(7):
            current = week_start + timedelta(days=weekday)
            data = days.get(current, {"count": 0, "level": 0})
            count = int(data.get("count", 0))
            level = level_for_count(count, int(data.get("level", 0)))
            delay = (week + weekday) * 0.011
            x = x0 + week * (cell + gap)
            y = y0 + weekday * (cell + gap)
            label = f"{count:,} contributions on {current.isoformat()}"
            rects.append(
                f'<rect class="day" x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'rx="2.5" fill="{PALETTE[level]}" data-date="{current.isoformat()}" '
                f'aria-label="{svg_text(label)}" style="animation-delay: {delay:.3f}s" />'
            )

    weekdays = [
        '<text class="axis" x="18" y="76">Mon</text>',
        '<text class="axis" x="18" y="104">Wed</text>',
        '<text class="axis" x="18" y="132">Fri</text>',
    ]
    legend_x = 662
    legend = [f'<text class="axis" x="{legend_x}" y="171">Less</text>']
    for index, color in enumerate(PALETTE):
        legend.append(
            f'<rect x="{legend_x + 42 + index * 17}" y="160" width="11" height="11" '
            f'rx="2.5" fill="{color}" />'
        )
    legend.append(f'<text class="axis" x="{legend_x + 150}" y="171">More</text>')

    total = int(payload.get("total_last_year", 0))
    current_streak = int(payload.get("current_streak", 0))
    longest_streak = int(payload.get("longest_streak", 0))
    generated_at = str(payload.get("generated_at", ""))
    footer = (
        f"{total:,} contributions in the last year"
        f"  |  current streak {current_streak}d"
        f"  |  longest {longest_streak}d"
    )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="GitHub contribution heatmap for Dipen Bhuva">
  <defs>
    <style>
      .frame {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
      text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .title {{ fill: #7ee787; font-size: 13px; font-weight: 700; }}
      .axis, .month, .footer {{ fill: #8b949e; font-size: 10px; }}
      .footer {{ font-size: 11px; }}
      .day {{ opacity: 0; transform-box: fill-box; transform-origin: center; animation: reveal 0.42s ease-out forwards; }}
      @keyframes reveal {{
        from {{ opacity: 0; transform: translate(-7px, -7px) scale(0.72); }}
        to {{ opacity: 1; transform: translate(0, 0) scale(1); }}
      }}
    </style>
  </defs>
  <rect class="frame" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" />
  <text class="title" x="22" y="24">dipen@github ~ $ ./contributions.sh</text>
  {''.join(month_labels)}
  {''.join(weekdays)}
  <g>{''.join(rects)}</g>
  <g>{''.join(legend)}</g>
  <text class="footer" x="22" y="186">{svg_text(footer)}</text>
  <text class="axis" x="660" y="186">updated {svg_text(generated_at[:10])}</text>
</svg>
"""
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
