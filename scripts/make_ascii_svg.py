#!/usr/bin/env python3
"""Turn a prepared portrait image into a self-typing monochrome ASCII SVG."""

from __future__ import annotations

import argparse
import html
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


RAMP = " .`:-=+*cs#%@"


def row_to_ascii(row: list[int]) -> str:
    chars = []
    for value in row:
        index = round((255 - value) / 255 * (len(RAMP) - 1))
        chars.append(RAMP[index])
    return "".join(chars).rstrip()


def image_to_rows(path: Path, columns: int, rows: int) -> list[str]:
    image = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", image.size, "white")
    image = Image.alpha_composite(background, image).convert("RGB")
    image = ImageOps.fit(image, (columns, rows), method=Image.Resampling.LANCZOS)
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image, cutoff=2)
    image = ImageEnhance.Contrast(image).enhance(1.45)
    pixels = list(image.getdata())
    return [
        row_to_ascii(pixels[row * columns : (row + 1) * columns])
        for row in range(rows)
    ]


def build_svg(rows: list[str], output: Path) -> None:
    width = 370
    height = 340
    x = 18
    y = 30
    font_size = 6.7
    line_height = 6.0
    text_width = width - 36
    duration = 0.28

    clip_defs = []
    text_rows = []
    cursors = []
    for index, row in enumerate(rows):
        delay = index * 0.035
        row_y = y + index * line_height
        clip_defs.append(
            f'<clipPath id="row-{index}">'
            f'<rect x="{x}" y="{row_y - 6}" width="0" height="{line_height + 1}">'
            f'<animate attributeName="width" begin="{delay:.3f}s" dur="{duration:.2f}s" '
            f'from="0" to="{text_width}" fill="freeze" />'
            "</rect></clipPath>"
        )
        text_rows.append(
            f'<text x="{x}" y="{row_y:.1f}" clip-path="url(#row-{index})">'
            f"{html.escape(row) or ' '}</text>"
        )
        cursors.append(
            f'<rect x="{x}" y="{row_y - 5:.1f}" width="4" height="5.5" class="cursor" '
            f'opacity="0"><animate attributeName="opacity" begin="{delay:.3f}s" '
            f'dur="{duration:.2f}s" values="1;1;0" fill="freeze" />'
            f'<animate attributeName="x" begin="{delay:.3f}s" dur="{duration:.2f}s" '
            f'from="{x}" to="{x + text_width}" fill="freeze" /></rect>'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="ASCII portrait of Dipen Bhuva">
  <defs>
    <style>
      .frame {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
      text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: {font_size}px; fill: #c9d1d9; white-space: pre; }}
      .cursor {{ fill: #39d353; }}
      .title {{ fill: #7ee787; font-size: 11px; font-weight: 700; }}
      .muted {{ fill: #8b949e; font-size: 10px; }}
    </style>
    {''.join(clip_defs)}
  </defs>
  <rect class="frame" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" />
  <circle cx="18" cy="15" r="4" fill="#ff5f56" />
  <circle cx="32" cy="15" r="4" fill="#ffbd2e" />
  <circle cx="46" cy="15" r="4" fill="#27c93f" />
  <text class="title" x="62" y="19">dipen-ascii.svg</text>
  <text class="muted" x="270" y="19">typing portrait</text>
  <g xml:space="preserve">
    {''.join(text_rows)}
  </g>
  <g>{''.join(cursors)}</g>
</svg>
"""
    output.write_text(svg, encoding="utf-8")
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="assets/avatar.png")
    parser.add_argument("--output", default="dipen-ascii.svg")
    parser.add_argument("--columns", type=int, default=92)
    parser.add_argument("--rows", type=int, default=49)
    args = parser.parse_args()

    rows = image_to_rows(Path(args.input), args.columns, args.rows)
    build_svg(rows, Path(args.output))


if __name__ == "__main__":
    main()
