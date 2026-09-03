---
name: shelf-catalog
description: "Transcribe every book, comic, or media spine visible in a photo of a shelf (or multiple shelves) into a structured list, and deliver it as a spreadsheet (or other file) the user can keep. Use this whenever the user uploads a photo of a bookshelf, comic shelf, CD/vinyl rack, or similar and asks for a list, inventory, catalog, or spreadsheet of what's in it — even if they just say 'what books are these' or 'can you list these out.' Also use it if the user asks to catalog, inventory, or organize a shelf/collection from an image, or to turn a shelf photo into an Excel/CSV/Word list. Handles the hard part: reading small, low-resolution, rotated, or partially-obscured spine text by systematically cropping and zooming into the image rather than guessing from a single downscaled view."
---

# Shelf Catalog: photo of spines → structured list

Turns a photo of a shelf (books, comics, games, vinyl, DVDs — anything with
readable spines) into a complete, ordered list, delivered as a spreadsheet
(default) or whatever format the user asks for.

The core challenge is legibility, not formatting: a single shelf photo is
often 4000+ px wide with dozens of thin spines, so a lot of titles are
unreadable at the resolution an image is normally viewed at. Do not try to
transcribe directly from the full-size image. Systematically crop, upscale,
and re-view sections instead.

## Workflow

### 1. Establish the raw-pixel orientation

Check the image's actual pixel dimensions with PIL (`Image.open(path).size`).
Phone photos taken in portrait are frequently stored as landscape pixel data
with an EXIF rotation flag — `crop()` operates on the raw, unrotated pixels,
so raw-image "left/right" and "up/down" often do **not** match what you see
in the chat thumbnail.

Crop one small test region (e.g. top-left 25% x 20%), upscale it 2-3x, and
view it before building the full grid. Check whether the text reads normally
or sideways, and work out which raw axis corresponds to "which shelf" and
which corresponds to "position along a shelf," and which direction (raw 0 →
left or right end of shelf). Get this right once, up front — every later crop
depends on it.

### 2. Grid-crop the image

Use the bundled `scripts/grid_crop.py` to split the image into an overlapping
grid of upscaled crops:

```bash
python3 scripts/grid_crop.py <photo_path> --out-dir <workdir> --x-bands 3 --y-bands 5 --scale 2
```

- One axis of the grid should align with "which shelf" (usually 1 band per
  physical shelf, or however many you found in step 1); the other should
  align with "position along the shelf" (more bands = smaller text becomes
  legible — 4-6 per shelf is typical for a packed shelf).
- Increase `--scale` for blurry or very small spines; increase `--y-bands`
  (or whichever axis is "along the shelf") rather than trying to read more
  per crop.
- Bands overlap on purpose so a spine sitting on a boundary is fully visible
  somewhere. Expect to see the same 1-2 items at the edges of adjacent crops.

### 3. View and transcribe every crop, in order

View each crop with the `view` tool (not just the low-res thumbnail already
in context). For each crop, read spines top-to-bottom or left-to-right as
they appear *in that crop*, then reverse or reorder as needed so the final
list reads in true physical order (e.g. left-to-right along each real
shelf) — work out the mapping once in step 1 and apply it consistently.

Do this **exhaustively**: don't stop once a "reasonable enough" list is
assembled. Go through every crop. It's normal for a dense shelf to yield
40-60+ items per row/shelf and 100+ items for a full bookcase.

De-duplicate items that appear in the overlap of two adjacent crops (same
title, same rough position) — keep one instance.

### 4. Resolve uncertain reads before finalizing

For any title that's ambiguous, stylized, sideways-printed, or only
partially in frame:
- Try a tighter, higher-scale crop of just that spine first.
- If still unclear, a quick, targeted web search on partial/legible text
  (author name, distinctive word, series) often confirms the exact title —
  worth doing for a handful of items, not for the whole list.
- If genuinely illegible, include a clearly-labeled placeholder (e.g.
  "Unidentified title (spine obscured)") rather than guessing or silently
  omitting it — the user should be able to tell what wasn't captured.

Do not fabricate plausible-sounding titles for anything you couldn't
actually read.

### 5. Deliver the output

Default to a spreadsheet unless the user asks for something else (Word list,
plain text, etc.). Follow the xlsx skill's conventions (Arial font, clean
header row/fill, sensible column widths, frozen header row) — see
`/mnt/skills/public/xlsx/SKILL.md`.

A good default column layout:

| # | Shelf / Group | Title | Order on shelf (left→right) |
|---|---|---|---|

- One row per item, in physical shelf order.
- Group by shelf (or case/row) if there's more than one, using a consistent
  label like "Shelf 1 (Top)".
- Add a short italic note at the bottom of the sheet if anything was
  unidentified or best-effort, so the user knows to double check it.

Save to the outputs directory and present the file — don't just describe the
list in chat unless the user explicitly wants it inline instead of a file.

## Notes

- This same crop-and-zoom approach generalizes to any "read lots of small
  text across a large image" task (spice racks, trading card binders, wine
  racks, filing cabinets) — the grid-crop script takes no domain-specific
  assumptions.
- Scale effort to shelf density: a single small shelf might need only 2-4
  crops total; a large, packed bookcase can reasonably need 15-20+ crops and
  several dozen tool calls. That's expected — don't shortcut legibility for
  speed.
