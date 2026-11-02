# emag-product-publish

Muse skill: take an eMAG marketplace product from the user's images to a
priced, fully-filled backend **draft**. Part of an eMAG seller-operations
skill set (siblings:
[emag-campaign-filler](https://github.com/secondmax/emag-campaign-filler),
emag-product-label).

## The three stages

1. **Localize and host images** — Replace Chinese text overlays with
   Romanian (product photos stay pixel-untouched), upload to postimages.org
   (original size, no expiry), record direct links. Method:
   [references/image-localization.md](references/image-localization.md).
2. **Write the listing** — Romanian title, black-white-gray HTML
   description (no emoji), spec table, package contents. Priced with the
   seller's campaign playbook: the everyday price must survive the standard
   20% campaign discount with ~30% margin left, cross-checked against
   existing similar SKUs.
3. **Create the backend draft** — Via a browser task in the eMAG seller
   backend: verified seller code and EAN, closest-fit category, net price
   (front-end / 1.21), stock 0, offer OFF, per-variant galleries and
   descriptions, characteristics, and the compliance block (EU Responsible
   Person + manufacturer defaults, generated Romanian safety text).
   Variants use eMAG's Product Family mechanism.

## Hard rules

- **Draft only. Never submit for review, publish, or approve.** The user
  submits.
- RockRiver is the shop name, not a registered brand: no brand words in
  listings.
- Verify seller-code and EAN occupancy on the platform; never trust memory.
- The Images tab accepts local files only: download from URLs, then grant
  files to the browser task. Descriptions paste via the editor's Source mode.

## Files

```
emag-product-publish/
├── SKILL.md                        # skill instructions for Muse
├── skill.yaml                      # skill metadata
├── README.md                       # this file
└── references/
    ├── image-localization.md       # overlay translation method
    └── backend-field-guide.md      # backend fields, variants, done state
```
