# Combined overlay system (round 3 follow-up)

The designer approved a **layered overlay kit** over the Cv2 base. Each material has one job:

| Job | Material | Taken from |
|---|---|---|
| **Verbs**: SEND IT, BUY, LEAVE, plus the big headline words | **B, stencil and spray**: cut-stencil letters with bridges, overspray, glossy drips. Pink face, white offset, black shadow. The washed-out system word stays readable underneath. | `o_b_stencil_spray/scripts` |
| **Objects**: crew ID, Heat poster, price tags, tactical note card, reward items | **C, premium vinyl stickers**: thick white die-cut borders, gloss, holo foil on the important ones, soft shadows, corner curl | `o_c_vinyl_sticker/scripts` |
| **Planning marks**: target circles, route arrows and waypoints, short handwritten words (HIT IT, OURS, THEM, THIS ONE!), the tactical note text | **A, grease pencil on glass**: waxy china-marker strokes lit by a key light, small cast shadow, crisp printed reticles and range rings | `o_a_tactical_glass/scripts` |
| **Light spill** (base layer, not overlay) | **D's idea**: glowing elements in the base cast coloured light onto nearby facets (neon signs, the MODEM sign, spinner rims) | `o_d_light_pen/scripts` (the spill pass only) |

## Rules
- **Colour roles** across the kit:
  - Pink is the Cell's verbs and spray.
  - Yellow grease pencil is for plans and route.
  - Red grease pencil is for threats and targets.
  - Stickers are white or kraft with holo on the key items.
  - Don't add new colours.
- **Marks per screen:** 4–6 overlay marks in total, and at least one from each of spray, sticker and grease pencil.
- **Layer order, bottom to top:**
  1. the base;
  2. light spill (into the base);
  3. grease pencil;
  4. stickers, which may overlap a pencil mark;
  5. spray verbs on top.
- **Readability:** nothing hides spinner values, node icons, prices or HP.
- **Old base marks:** the base bakes in old marks ("UPGRADE OR DIE!", BUY/SELL/TRADE stickers, taped prices). Cover or replace each with the kit version.
- **System words:** where the base has no system word under a verb, draw a washed-out machine button in the base UI style (EXECUTE, PURCHASE, EXIT) and spray the verb over it, as B did.

## Bases (don't repaint them)
- Combat: `docs/concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png`
- City: `docs/concepts/round2/r2c_geo_vector_gritty/stills/02_city_night.png`
- Shop: `docs/concepts/round2/r2c_v2_modem/modem_shop.png`

## Deliverables
All files go in `docs/concepts/round3_overlay/combined/`.
- `01_combat.png`, `02_city.png`, `03_shop.png` at 1920×1080.
- `04_kit_sheet.png`: the overlay kit on a neutral background, labelled by material and job, with one example of each element type.
- `05_lifecycle.png`: SEND IT spraying on, while a sticker slaps on and a pencil circle draws. Then idle (drips crawl, a sticker corner flutters). Then exit (a solvent wipe, a sticker peel and a palm smear).
- `contact_sheet.jpg`, `KIT.md` (half a page: the rules above as built, and how to build it in Godot), and `scripts/`.

Reuse the three agents' libraries by importing or copying their scripts. Write `.py` files and run them, and never `python -`. Keep the folder under about 25 MB.
