#!/usr/bin/env python3
"""Generate a neofetch-style profile info card."""

from __future__ import annotations

import html
import os
from pathlib import Path


ROWS = [
    ("Name", "Dipen Bhuva"),
    ("Role", "Co-founder & CRO at newline"),
    ("Focus", "AI/ML, LLMs, RAG, cybersecurity"),
    ("Stack", "Python, TypeScript, Rust, SQL, vector DBs"),
    ("Builds", "AI products, evals, agents, dashboards"),
    ("Research", "Ph.D. CS | 16 publications | 200+ citations"),
    ("Now", "Research-to-production AI systems"),
    ("Location", "Miami"),
    ("Web", "bhuva-ai-portfolio.lovable.app"),
]


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    output = Path("info-card.svg")
    width = 490
    height = 340
    y_start = 70
    line_gap = 24

    rows_svg = []
    for index, (key, value) in enumerate(ROWS):
        y = y_start + index * line_gap
        delay = index * 0.09
        style = "" if static else f' style="animation-delay: {delay:.2f}s"'
        rows_svg.append(
            f'<g class="line"{style}>'
            f'<text class="key" x="34" y="{y}">{html.escape(key)}</text>'
            f'<text class="sep" x="126" y="{y}">:</text>'
            f'<text class="value" x="148" y="{y}">{html.escape(value)}</text>'
            "</g>"
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Neofetch-style profile card for Dipen Bhuva">
  <defs>
    <style>
      .frame {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
      .bar {{ fill: #161b22; }}
      text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .prompt {{ fill: #7ee787; font-size: 13px; font-weight: 700; }}
      .muted {{ fill: #8b949e; font-size: 12px; }}
      .key {{ fill: #58a6ff; font-size: 13px; font-weight: 700; }}
      .sep {{ fill: #8b949e; font-size: 13px; }}
      .value {{ fill: #c9d1d9; font-size: 13px; }}
      .line {{ opacity: 0; transform: translateY(8px); animation: line-in 0.42s ease-out forwards; }}
      .chip {{ fill: #1f6feb; opacity: 0.2; }}
      @keyframes line-in {{
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
  </defs>
  <rect class="frame" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" />
  <rect class="bar" x="1" y="1" width="{width - 2}" height="38" rx="8" />
  <circle cx="20" cy="20" r="4.5" fill="#ff5f56" />
  <circle cx="36" cy="20" r="4.5" fill="#ffbd2e" />
  <circle cx="52" cy="20" r="4.5" fill="#27c93f" />
  <text class="prompt" x="30" y="55">dipen@github</text>
  <text class="muted" x="132" y="55">~ $ neofetch</text>
  <rect class="chip" x="326" y="45" width="128" height="18" rx="9" />
  <text class="muted" x="338" y="58">applied-ai.dev</text>
  {''.join(rows_svg)}
</svg>
"""
    output.write_text(svg, encoding="utf-8")
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
