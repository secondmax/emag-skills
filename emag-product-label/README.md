# emag-product-label

Muse skill: generate EU-compliant **100x100mm product labels** for eMAG
marketplace products. Part of an eMAG seller-operations skill set
(sibling: [emag-campaign-filler](../emag-campaign-filler)).

Each label contains:

- Trilingual product info (Romanian / Bulgarian / Hungarian) for the RO/BG/HU storefronts
- Manufacturer block and EU Responsible Person block (GPSR Art. 16)
- Product-specific trilingual safety warnings
- **Vector-drawn EAN-13 barcode** generated from your EAN (scans reliably;
  raster barcodes scaled in PDFs do not)
- Official **CE mark**
- **QR code** linking to a hosted EU Declaration of Conformity

## Quickstart

```bash
pip install reportlab qrcode pillow

# 1. Fill in your product data
cp scripts/product.example.json my-product.json
#    edit: names/materials/usage/safety in ro/bg/hu, EANs per variant,
#    manufacturer, EU REP, declaration signatory

# 2. Generate the EU Declaration of Conformity (8-point template)
python3 scripts/make_declaration.py --product my-product.json --out declaration.pdf

# 3. Host declaration.pdf somewhere with a long-lasting public URL
#    (e.g. Google Drive "anyone with the link"), copy the URL

# 4. Build one label PDF per variant
python3 scripts/build_labels.py --product my-product.json \
    --qr-url "https://your-hosted-declaration-url" \
    --ce assets/ce-mark.png --outdir ./out
```

`--ce` takes the official CE mark PNG (one is bundled in `assets/`). Omit it only for drafts (a text
fallback is used).

For food-contact products, set `"food_contact": true` in your product JSON
(or pass `--food-contact <symbol.png>`); the food-contact symbol is placed
in the bottom row next to the CE mark. A symbol is bundled in
`assets/food-contact.png`.

## Updating the declaration later

Update the **same** hosted file in place instead of uploading a new one.
The URL (and therefore every printed QR code) stays valid, and scans
always show the latest version.

## Layout

See [references/label-spec.md](references/label-spec.md) for the exact
100x100mm section layout, typography and barcode spec.

## Files

```
emag-product-label/
├── SKILL.md                  # skill instructions for Muse
├── skill.yaml                # skill metadata
├── README.md                 # this file
├── scripts/
│   ├── build_labels.py       # label PDF builder (vector EAN-13 + QR)
│   ├── make_declaration.py   # EU Declaration of Conformity builder
│   └── product.example.json  # input schema example (retractable keychain)
└── references/
    └── label-spec.md         # layout specification
```

## Requirements

- Python 3.8+
- `reportlab`, `qrcode`, `pillow`
- A font covering RO/BG/HU diacritics (DejaVu Sans default;
  override with `--font` / `--font-bold`)
