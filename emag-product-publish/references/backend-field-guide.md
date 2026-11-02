# eMAG backend field guide (seller backend, marketplace.emag.ro)

## Identity

- Seller code: `RockRiver` + number. Outdoor products use 10xx,
  coffee/household use 20xx. Always verify the code is free on the
  platform before assigning; do not trust memory.
- EAN-13 per variant, verified unused in the eMAG catalog and the
  seller's own products before assigning.
- PNK is assigned by eMAG later; expect "-" on a fresh draft.

## Price

- Fill the **net** price (front-end / 1.21, VAT 21%). The page shows the
  VAT-inclusive front-end.
- `Prag Maxim` must exceed `Prag Minim`; use net + 0.01 as a placeholder
  when the user has no real value.
- Stock 0, offer switch OFF on a draft.

## Characteristics

- Fill colour (variant dimension), material, dimensions, weight, cable
  length and similar where the category offers fields; merge leftovers
  into a free-text details field.
- Leave `Tip produs` (product type) empty when no dropdown option fits.
  Leave any field empty rather than forcing a wrong value, and report
  each blank with its reason.

## Compliance (every new product)

- EU Responsible Person and manufacturer come from the user's standing
  defaults; do not ask again.
- Generate the Safety Information in Romanian from the product's
  characteristics: eMAG's recommended base text plus category-specific
  warnings (small parts, cable snap-back, max load, heat).

## Variants

- eMAG groups variants as a Product Family: one product record per
  variant, family name without the colour, colour as the visible variant
  dimension. Each variant carries its own EAN, seller code, main image
  and description.

## Done state

- Draft list, "validation pending". That state is automatic after save.
  The task is complete only when nothing was submitted, published or
  approved.
