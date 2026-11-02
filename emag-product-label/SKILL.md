# eMAG Product Label Generator

Generate EU-compliant 100x100mm product labels for eMAG marketplace products:
vector-drawn EAN-13 barcode, official CE mark, QR code linking to a hosted
EU Declaration of Conformity, trilingual (Romanian/Bulgarian/Hungarian) text
covering the RO/BG/HU storefronts.

## Collect the product data

- Copy `scripts/product.example.json` to a working file and fill it in. Every
  `ro`/`bg`/`hu` field is required; the label prints all three languages.

- Get one EAN-13 per variant from the user. The script validates the check
  digit and refuses to build on a bad code. Never invent an EAN.

- `batch_number` defaults to the variant EAN when omitted. `seller_ref`
  holds the seller's internal product code (e.g. RockRiver2025).

- The declaration section needs `legislation`, `standards`, `place_date`,
  `signatory_name` and `signatory_function`. The signatory signs for the
  manufacturer; ask the user for the name rather than inventing one.

## Generate the declaration of conformity

- Run `python3 scripts/make_declaration.py --product <file> --out declaration.pdf`.
  It follows the official EU 8-point DoC model.

- Keep the generated PDF. It is the file the label QR code will point to.

## Host the declaration and get a lasting URL

- The QR code is printed on physical labels, so its URL must work for years.
  Upload the declaration to the user's Google Drive and create an
  anyone-with-the-link reader share; use the returned `webViewLink`.

- If the user prefers their own flow (e.g. Tencent Docs), have them upload
  the PDF themselves and send the share link instead.

- When the declaration changes later, update the same Drive file in place
  (`files update`) instead of uploading a new file. The file ID and the QR
  code stay valid, and scans always show the latest version.

## Build the labels

- Run `python3 scripts/build_labels.py --product <file> --qr-url <url> --ce <ce-mark.png> --outdir ./out`.
  One PDF per variant is written to the outdir.

- Install dependencies first: `pip install reportlab qrcode pillow`.
  DejaVu Sans (default) covers Romanian, Bulgarian and Hungarian diacritics;
  override with `--font`/`--font-bold` when needed.

- The barcode is drawn as vector rectangles, never as a scaled raster image.
  Raster barcodes blur when scaled and fail to scan. The script runs an
  encode/decode roundtrip self-test on every EAN before building.

- The three taller bar groups (start, center, end) are EAN-13 guard bars.
  They are part of the symbology, not a defect; do not "fix" them.

- Pass the official CE mark as a PNG via `--ce`. A text "CE" is only a
  fallback and does not meet the mark's proportions.

- For food-contact products (tableware etc.), enable the food-contact
  symbol: set `"food_contact": true` in product.json, or pass
  `--food-contact <symbol.png>` (defaults to the bundled
  `assets/food-contact.png`). The symbol is placed in the bottom row next
  to the CE mark. Do not enable it for non-food-contact products.

## Verify before handing over

- Confirm the roundtrip self-test passed for every EAN in the run output.

- Render each label PDF to PNG and inspect it: no text overflow past any
  section divider, the EU REP name wraps inside its box, the barcode number
  matches the variant EAN, the correct colour words appear per variant.

- Decode the generated `_qr.png` (or scan it) and confirm it opens the
  declaration URL. Confirm the hosted URL loads without sign-in.

- Hand the user the label PDFs. When re-sending a corrected file, use a new
  filename; chat clients cache attachments by path and will show the stale
  copy otherwise.

## Available connectors

- [Google Drive](/opt/hatch/connectors/google_drive/CONNECTOR.md) for hosting the declaration PDF and creating the anyone-with-the-link share the QR code encodes.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
