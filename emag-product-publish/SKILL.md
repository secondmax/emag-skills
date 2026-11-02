# eMAG Product Publishing

Take a product from the user's images to a priced, fully-filled eMAG
Marketplace draft: localize images to Romanian, upload them to the image
host, write the Romanian listing, create the backend product. Three stages,
in order. Never submit for review; always save as draft and let the user
submit.

## Stage 1: Localize and host the images

- The user sends product images (often with Chinese text overlays). Replace
  the overlay text with Romanian; leave the product photos themselves
  pixel-untouched. See `references/image-localization.md` for the method.

- Give the user the Romanian search term when they must check something on
  eMAG themselves; never make them translate.

- Upload finished images to postimages.org via a browser task: original
  size, no expiry, files unedited. Record every direct (`i.postimg.cc`)
  link plus the gallery link in a dated links file.

- Pick the main image with the user when it is ambiguous. The main image
  leads both the gallery and the description.

## Stage 2: Write the listing

- Write the Romanian title first and confirm it when the wording is
  non-obvious. Never put brand words in the title or description:
  RockRiver is the shop name, not a registered brand.

- Deliver the description as HTML straight in chat: black-white-gray
  styling, no emoji, every image `width:100%`. Structure: intro paragraph,
  benefit bullets, spec table, package contents. Keep one copy per
  variant (colour word swapped).

- Price with the user's campaign playbook, not the bare formula. The
  formula gives a floor; the everyday price must survive the standard 20%
  campaign discount with around 30% margin left. Cross-check against the
  user's existing similar SKUs before proposing a number.

- Net backend price = front-end / 1.21 (VAT 21%). Commission is charged on
  the VAT-inclusive price, so the formula uses commission x 1.21.

## Stage 3: Create the backend draft

- Run the creation as a `browser.browse` task with a self-contained
  assignment: outcome, exact titles, codes, prices, image URLs, compliance
  texts, and the hard rule below. The browser signs in with the saved
  login by itself.

- **Verify before assigning**: check the seller code (RockRiver + number)
  is free on the platform, and check each EAN is unused in the eMAG
  catalog and the seller's products. The user's numbering memory is
  unreliable; the platform is the source of truth. Outdoor = 10xx,
  coffee/household = 20xx.

- Category: search the Romanian term on the platform and pick the closest
  fit; report the chosen path.

- Per variant: net price, VAT 21%, stock 0, offer switch OFF, gallery
  images in order (main first), pasted description HTML, characteristics
  (colour/material/dimensions/weight as the category allows). Leave
  `Tip produs`/product-type empty when no option fits; never force a
  wrong value. For volume fields the platform requires, use measured
  values or mark placeholders clearly for the user to confirm.

- The Images tab accepts local files only, not URLs. Download the images
  from their URLs first, then grant them to the browser task through the
  `files` parameter. The description editor takes HTML through its Source
  mode; if the browser cannot read a granted file, paste the full HTML
  into the answer text instead.

- Variants use eMAG's Product Family mechanism: one product record per
  variant, grouped in a family with the colour dimension. Each variant
  gets its own EAN and seller code.

- Compliance block, every new product: the user's EU Responsible Person
  and manufacturer defaults, plus a Romanian Safety Information text you
  generate from the product's characteristics. See
  `references/backend-field-guide.md`.

- **Save as draft only. Never click submit-for-review, publish or approve.**
  The "validation pending" state after saving is automatic, not a
  submission.

- Report back: internal product IDs, family ID, final codes and EANs,
  category, confirmed prices, image counts per variant, every field left
  blank and why, and the final draft status.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
