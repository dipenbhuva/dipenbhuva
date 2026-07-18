#!/usr/bin/env python3
"""Prepare a portrait image for the ASCII SVG generator."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Path to a source portrait image")
    parser.add_argument(
        "--output",
        default="assets/source-prepped.png",
        help="Where to write the prepared grayscale image",
    )
    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(source).convert("RGBA")
    background = Image.new("RGBA", image.size, "white")
    composited = Image.alpha_composite(background, image).convert("RGB")
    cropped = ImageOps.fit(composited, (640, 640), method=Image.Resampling.LANCZOS)
    grayscale = ImageOps.grayscale(cropped)
    grayscale = ImageOps.autocontrast(grayscale, cutoff=2)
    grayscale = ImageEnhance.Contrast(grayscale).enhance(1.45)
    grayscale = ImageEnhance.Sharpness(grayscale).enhance(1.2)
    grayscale.save(output)
    print(f"Wrote {output}")


if __name__ == "__main__":
    main()
