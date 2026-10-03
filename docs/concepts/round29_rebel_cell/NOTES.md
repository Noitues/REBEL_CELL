# Round 29: the Cell's fist in red window light, and a canyon that lays low

**Dropped (designer):**
- the holograms;
- the painted roofs;
- the street-level combat view.

## 1. Map: red window lights (`map_redlights_city_*.jpg`, `map_redlights_crop_*.jpg`)
- **The district looks like the rest of the city.** It keeps the city's own buildings and the normal street grid; the
  fist streets are gone (`grid27.patch`). The red district tint on the buildings is removed.
- **The window light is the only mark.** `scripts/map29.py` replaces the restyler's window pass:
  - Outside the crest, windows are exactly as before.
  - Inside the crest, a finer grid of red-lit windows is drawn (80 % lit). "Inside" means the window's position on
    the map falls within a large Cell crest (1500 city px tall) over the district.
  - A soft red glow spills from those windows.
  - Because the test is per window, the fist is drawn across many ordinary buildings, and it reads from the
    city-wide shot.
- **DISPATCH:**
  - every window inside the crest is lit, in a harsher red;
  - the crest's rows are torn sideways (glitch bands);
  - some windows flash white or are dead;
  - the glow is stronger.

## 2. Canyon (`canyon_home.jpg`, `canyon_dispatch.jpg`)
- **Kept from round 28:** the darker grade and the flickering signs.
- **No floating fists or holograms anywhere.**
- **Home (lay low):** only ordinary Tokyo shop signs.
  - Signs: amber, white, cyan, red, green, blue and gold glyph signs and light boxes.
  - Lanterns: paper lanterns.
  - The billboard at the end of the street is an ordinary ad.
  - No Cell colours, fists or tags.
- **DISPATCH (the betrayed Cell):** every sign and billboard shows the fist or a Cell slogan, all in red.
  - Billboards: REBEL_CELL, NO MASTERS, SEND IT, WE ARE THE CELL, CELL-9 LIVES.
  - Blade signs carry vertical REBEL_CELL text.
  - The billboard at the end of the street reads REBEL_CELL.

## 3. Combat (`combat_rebel_cell.png`, `combat_rebel_cell_motion_v2.gif`)
- **The combat image:** the DISPATCH canyon behind the round 25 composite, unchanged (locked D4 wheels, DISPATCH
  boss wheel, sticker cards, SEND IT).
- **The GIF:** 960 × 540, 12 frames, 2.1 MB. Signs flicker, die, scroll, and swap between slogan and fist.
- **Frame resolution:** the frames are rendered at 1440 × 810, so the billboard slogans are a little softer than in
  the still.

## Weakest parts / open
- **Home shows no fist up close.** That is intended (lay low), but the fist only reads from the city map.
- **The DISPATCH glitch bands are subtle** at full-city scale.
- **The other HQs are the round 6 map drawings.** The round 25–30 HQ sprites live in other rounds' scratch folders.

## Build (from `scripts/`)
1. `python layout27.py`
2. `python map29.py`
3. `python render_all29.py stills gif`
4. Render the wheels:
   - `python wheels_r18/render_bosses24.py rebel_cell`
   - `python wheels_r18/dump_boss_slots24.py`
   - `python combat_r23/render_player24.py`
5. `python make_out29.py`
