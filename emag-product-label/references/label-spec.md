# Label layout spec (100x100mm)

Replicates the standard eMAG-seller product label: five stacked sections
inside a 3mm-margin border, bottom row with barcode / CE / QR.

## Sections, top to bottom

1. **Product info**: `Product Name` (trilingual, colour per variant),
   `Product Material` (trilingual), `Batch Number` (= variant EAN),
   `Product Usage` (trilingual).
2. **Manufacturer**: name, address, e-mail.
3. **EU REP**: EU/REP logo boxes plus responsible-person name, address,
   e-mail and tel (defaults follow GPSR Art. 16).
4. **Safety**: trilingual warning text, product-specific (e.g. max load,
   cable limits).
5. **Bottom row**: vector EAN-13 barcode with human-readable number,
   official CE mark image, QR code (18x18mm) encoding the hosted
   declaration URL.

## Typography

- DejaVu Sans / DejaVu Sans Bold, 6.5pt body. Covers Romanian (ș/ț),
  Bulgarian (Cyrillic) and Hungarian (ő/ű).
- The builder asserts on content overflow; shorten texts when it fires.

## Barcode

- EAN-13 drawn as vector rectangles: 95 data modules plus 9-module quiet
  zones each side, 44mm total width, 11mm bars, guards 2.2mm taller.
- Check digit validated before drawing; encode/decode roundtrip self-test
  runs on every EAN.
- The three taller groups are guard bars (start `101`, center `01010`,
  end `101`) required by the symbology.

## QR code

- Encodes the long-lasting URL of the hosted EU Declaration of Conformity.
- Regenerate after any declaration re-upload that changes the file ID;
  in-place updates keep the existing QR valid.

## Food-contact symbol (optional)

- Enabled per product via `"food_contact": true` in product.json or
  `--food-contact <png>` on the command line.
- Placed in the bottom row beside the CE mark; both marks auto-shrink to
  fit and the barcode narrows slightly (module width stays above the
  0.33mm minimum).
- Only enable for products that actually contact food.
