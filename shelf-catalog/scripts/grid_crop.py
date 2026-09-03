#!/usr/bin/env python3
"""
Split a photo into an overlapping grid of upscaled crops so that small text
(e.g. book/comic spines) becomes legible to a vision model.

Usage:
    python3 grid_crop.py <image_path> [--out-dir DIR] [--x-bands N] [--y-bands N] [--scale S]

Notes for the caller (Claude):
- Phone photos are often stored in landscape pixel dimensions even though they
  display as portrait (EXIF rotation). PIL's `Image.open` + `.crop()` reads
  RAW pixels, ignoring EXIF rotation, so the crop coordinates below are in
  raw-pixel space, NOT the space you see when the image is displayed in chat.
  Always sanity-check the very first crop by viewing it: if the text reads
  sideways, the raw image is rotated ~90 degrees relative to the display, and
  the "x-bands" (grid columns) will correspond to the display's vertical axis
  (e.g. which shelf) while "y-bands" correspond to the display's horizontal
  axis (e.g. position along a shelf) -- or vice versa. Work out the mapping
  from ONE test crop before reading the rest, and note the direction (does
  raw y=0 correspond to the left or right end of the shelf?).
- Bands overlap by ~10% of their size so a spine split across a boundary is
  fully visible in at least one crop. When transcribing, de-duplicate items
  that appear in the overlap of two adjacent crops.
- Default grid is 3 x-bands by 5 y-bands (15 crops) at 2x upscale, tuned for
  a ~4000px-wide bookshelf photo with 3 shelves of paperback-width spines.
  Increase --y-bands for longer shelves / smaller text; increase --scale for
  very dense or blurry spines.
"""
import argparse
import os
from PIL import Image


def make_bands(n, overlap_frac=0.08):
    """Return n (start, end) fractions covering 0..1 with overlap."""
    if n == 1:
        return [(0.0, 1.0)]
    step = 1.0 / n
    overlap = step * overlap_frac * n  # spread overlap proportionally
    bands = []
    for i in range(n):
        start = max(0.0, i * step - overlap / 2)
        end = min(1.0, (i + 1) * step + overlap / 2)
        bands.append((start, end))
    return bands


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image_path")
    ap.add_argument("--out-dir", default=".")
    ap.add_argument("--x-bands", type=int, default=3)
    ap.add_argument("--y-bands", type=int, default=5)
    ap.add_argument("--scale", type=int, default=2)
    args = ap.parse_args()

    img = Image.open(args.image_path)
    w, h = img.size
    os.makedirs(args.out_dir, exist_ok=True)

    xbands = make_bands(args.x_bands)
    ybands = make_bands(args.y_bands)

    paths = []
    for xi, (x0, x1) in enumerate(xbands):
        for yi, (y0, y1) in enumerate(ybands):
            l, r = int(w * x0), int(w * x1)
            t, b = int(h * y0), int(h * y1)
            crop = img.crop((l, t, r, b))
            crop = crop.resize((crop.width * args.scale, crop.height * args.scale), Image.LANCZOS)
            out_path = os.path.join(args.out_dir, f"grid_x{xi}_y{yi}.png")
            crop.save(out_path)
            paths.append(out_path)

    print(f"Wrote {len(paths)} crops ({args.x_bands}x{args.y_bands} grid, {args.scale}x upscale) to {args.out_dir}")
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
