# Round 4: settle the wheel (spinner) and the card set

## Context
- **Locked base:** Cv2. That's gritty triangulated low-poly vector: flat facets, no outlines, a dirty palette, harsh sparse neon and rain.
- **Locked overlay:** vinyl stickers for all words and objects, plus grease pencil for plans.
- **Designer's view:** neither the wheels nor the cards are final. Spinners have "not been reading" in any style so far.
- **This round:** settle both, with several clearly different versions of each.

## What the wheel must communicate (from `docs/art_asset.md` §E1–E4; read that file in the main checkout, `C:\Users\noitu\Documents\Godot\rebel_cell\docs\art_asset.md`)
- **Layout:** 30 ticks around the rim. Slices span ticks and are coloured by type, with a glyph and a value.
- **Pointer:** a pointer/needle at the top marks the slice that fires. This is the most important read: **which slice is under the pointer, and its value.**
- **Inner ring (hub ring):** an optional rotating ring of segments.
- **Hub:** shows the name/core.
- **HP:** an HP bar or arc.
- **Status marks on slices:** CORRUPTED, OVERCLOCKED, ENCRYPTED, PARASITE.
- **Ownership:** player vs enemy wheel (enemy in corp colour/pattern), plus a boss variant.
- **Size:** it must read at the combat size (radius about 160–220 px at 1080p) and at a small size (radius 60 px, e.g. multi-enemy).
- **Accessibility:** readable in greyscale, so slice type shows by glyph and shape, not colour alone.

Slice colours (keep these): attack/crit pink #FF3DA8, defend/shield cyan #5CE1FF, evade/heal green #7BE07B, afflict violet #C85AFF, deploy lavender #B08CFF, miss grey #6A6A6A.

## Wheel versions (render all four)
- **W-A, "Salvaged faceted"** (refine the current Cv2 wheel). Faceted slices with a hazard-striped, rusty rim and tick teeth.
  - Fixes: much bigger, bolder value numbers and glyphs on a calm (less faceted) slice fill.
  - The pointer becomes a large notched blade.
  - The active slice is lifted and outlined.
- **W-B, "Instrument dial"**: a precise gauge, not a prize wheel.
  - Dark faceted bezel with printed tick marks and numerals around the rim.
  - Slices are thin coloured bands at the outer edge, with big glyph+value badges set inward, like a watch dial.
  - The pointer is a long instrument needle from the centre.
  - The hub is a small screen.
  - Most readable, least toy-like.
- **W-C, "Layered physical stack"** (from the spinner depth study, combination 8, in Cv2 facets).
  - Machined bezel, then slice disc set lower, then a glass dome sheen, then a physical needle with counterweight, with shadows between layers.
  - Values are on raised chips.
- **W-D, "Segmented ring + sticker values".**
  - The wheel is just a thick segmented ring (no pie slices), so the centre is open for the hub and status.
  - Each slice's value and glyph is a small **vinyl sticker** stuck on its segment, tying the wheel to the overlay language.
  - The pointer is a sticker-arrow tab.

For each wheel version, show:
- (1) the player wheel at hero size;
- (2) an enemy wheel in Meridian orange with container-stripe pattern;
- (3) a small size (r = 60);
- (4) a greyscale copy;
- (5) one slice with a status mark (CORRUPTED);
- (6) the "slice under pointer" highlight state.

## What a card must communicate (§E5)
- **Basic info:** title, RAM cost, type (WHEEL / SYSTEM / HACK), rarity (Common / Uncommon / Rare / Boss).
- **Effect:** an illustration, a pictogram row for what it does (e.g. spin 9 counter-clockwise, 3 damage to all, gain 12 block), and short text.
- **States:** in hand, hover/focus, can't afford (RAM), disabled.
- **Sizes:** hand size (about 112×148 at 1080p, so the key info must survive that size), detail size, and a card back.

Use these sample cards (from the Appendix): **Backspin** (Common, WHEEL), **Arc Flash** (Uncommon, HACK), **Bulwark** (Uncommon, SYSTEM), and one **Rare** of your choice.

## Card versions (render all four)
- **C-A, "Faceted print"** (refine the current Cv2 card). A triangulated illustration, paper border, cost gem.
  - Fixes: a clear type band and rarity edge, and a pictogram row large enough at hand size.
- **C-B, "Data chip".** The card is a physical cartridge or chip: a faceted plastic shell with a contact edge, a label window with the illustration, a cost LED, and type as shell colour.
  - Rarity: matte, then translucent, then holo shell.
- **C-C, "Sticker card".** The card IS a die-cut vinyl sticker: thick white border, gloss, holo for rare. This unifies cards with the overlay language.
  - Hand cards look stuck on the screen. Playing one peels it off and slaps it on the wheel.
- **C-D, "Terminal card".** A dark glass panel card with a neon edge in its type colour, a faceted illustration, monospace text and crisp pictograms. The most "system" option.
  - Rarity is shown by edge treatment.

For each card version, show:
- (1) the 4 sample cards at detail size;
- (2) the same 4 at hand size in a fanned hand;
- (3) the states: hover, can't-afford and disabled, on one card;
- (4) the card back;
- (5) a greyscale copy.

## Also
Make two **combat mockups** using the Cv2 combat base (`docs/concepts/round2/r2c_geo_vector_gritty/stills/04_combat.png`) with the wheels and hand replaced:
- **Mockup 1:** your best wheel and your best card.
- **Mockup 2:** the second-best pairing.

## Deliverables (`docs/concepts/round4_wheel_card/`)
- Wheel sheets: `wheel_A.png`, `wheel_B.png`, `wheel_C.png`, `wheel_D.png` (1920×1080 each).
- Card sheets: `card_A.png`, `card_B.png`, `card_C.png`, `card_D.png`.
- `wheels_compare.jpg` (the 4 hero wheels side by side) and `cards_compare.jpg` (the 4 detail Arc Flash cards side by side).
- `mockup_1.png`, `mockup_2.png`.
- `NOTES.md`: per version, its strengths, its readability at small size, how to build it in Godot, and your recommendation.
- `scripts/`.

Write `.py` files and run them; **never `python -`**. Keep the folder under 30 MB.
