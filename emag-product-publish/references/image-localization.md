# Image localization: Chinese overlays to Romanian

Goal: product detail images readable by Romanian buyers, product photos
untouched. Method: detect overlay text, inpaint it away, redraw Romanian
in a matching neutral typeface (DejaVu Sans; Bold for titles, Regular for
body, dark gray ink).

## Workflow

- Copy originals aside first. Work on copies in a dated folder.

- For each image, crop-zoom the text regions and note the exact pixel
  boxes of every Chinese string before writing any code.

- Erase with PIL + numpy inpainting: build a mask of dark pixels inside
  each box, dilate a few px, inpaint iteratively. Prefer erasing the whole
  box on plain backgrounds; it is more reliable than threshold detection.

- Watch for non-black text: gray text needs a higher luminance threshold,
  red text needs a red-channel mask. Verify each region after erasing.

- Redraw Romanian with `ImageFont.truetype` (DejaVuSans-Bold.ttf /
  DejaVuSans.ttf). Romanian lines run longer than the Chinese originals;
  shrink the size or widen the box before drawing, then verify no overlap
  with neighbouring text or product edges.

- QA every image at full size after processing. The known failure modes
  are ghost remnants (incomplete erasure), glyph glitches from partial
  erasure under the new text, and overlapping redrawn lines. Fix by
  widening the erase box and redrawing; never ship a ghost.

- Keep spec numbers truthful: use the user's stated figures (weight,
  dimensions) even when the supplier image prints different ones, and
  tell the user about the discrepancy.

## Upload

- Upload via a `browser.browse` task to postimages.org: original size
  ("do not resize"), no expiry, files unedited.

- Record direct links (`i.postimg.cc/...`) per image plus the gallery
  link in a dated markdown file next to the processed images.
