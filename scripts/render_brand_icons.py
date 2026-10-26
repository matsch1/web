"""Regenerate PNG/ICO variants from the canonical square SVG.

Requires CairoSVG and Pillow: python -m pip install cairosvg pillow
Run from any directory: python scripts/render_brand_icons.py
The standalone route and wordmark have independent alignment transforms.
"""
from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image

DIRECTORY = Path(__file__).resolve().parents[1] / 'static' / 'branding'
SIZES = (16, 32, 48, 180, 192)


def main():
    source = (DIRECTORY / 'jutland-favicon.svg').read_bytes()
    # Supersample all variants identically for consistent small-size edges.
    large = Image.open(BytesIO(cairosvg.svg2png(
        bytestring=source, output_width=768, output_height=768))).convert('RGBA')
    for size in SIZES:
        image = large.resize((size, size), Image.Resampling.LANCZOS)
        image.save(DIRECTORY / f'jutland-icon-{size}.png')
    large.save(DIRECTORY / 'jutland-favicon.ico', format='ICO',
               sizes=[(16, 16), (32, 32), (48, 48)])


if __name__ == '__main__':
    main()
