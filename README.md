# eMAG Seller Skills

A growing suite of Muse skills for running an eMAG Marketplace store
(coffee + outdoor supplies, RO/BG/HU). Each skill is self-contained in its
own directory.

| Skill | What it does |
|---|---|
| [emag-campaign-filler](emag-campaign-filler) | Fill eMAG campaign proposal files from the origin spreadsheet and pricing rules |
| [emag-product-label](emag-product-label) | Generate EU-compliant 100×100mm product labels (vector EAN-13, CE mark, QR to hosted EU Declaration of Conformity) + build the declaration itself |
| [emag-product-publish](emag-product-publish) | Take a product from the user's images to a priced eMAG backend draft: localize images to Romanian and host them, write the Romanian listing, create the product (draft only, never submitted) |

## Conventions shared across skills

- **Draft only, never submit.** Backend products are built and saved as
  drafts; the user submits for review himself. Review is slow and
  submission locks the product from editing.
- **Verify on the platform.** Seller-code and EAN occupancy are checked
  against eMAG itself, never trusted from memory.
- **RockRiver is the shop name, not a registered brand.** No brand words
  in listings.
- **Priced with campaign headroom.** The everyday price must survive the
  standard 20% campaign discount with ~30% margin left; bare-formula
  prices are not used.

## Roadmap

Planned additions (ideas welcome):

- Profit calculator — per-SKU margin math from cost, freight, commission
  and campaign discounts.

## Layout

```
emag-skills/
├── README.md
├── emag-campaign-filler/
├── emag-product-label/
└── emag-product-publish/
```
