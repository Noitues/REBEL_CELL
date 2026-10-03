# Round 27: the Cell's district (painted roofs + the Tokyo canyon), no fist streets

## What changed (from the designer's review of round 26)
1. **The fist streets are gone.** `scripts/grid27.py` patches the game layout in memory; the file
   `round6_city_restyle/city_layout.json` itself is not changed. It drops the fist roads and fills in the district's
   regular street grid. The grid uses the same i/j street lines as the rest of the map: i 26/32/36/40/46…,
   j 24/31/36/43/49…. It adds 216 street cells and copies lane colours from neighbouring cells. Buildings that stood
   on the new streets are removed. The empty strips the roads left are filled with copies of the district's own
   small buildings (196 lots).
2. **No standout HQ.** The base is not a single building any more. It is a block of low, level, city-coloured
   tenements (one per lot) next to one ordinary grid street. The street's shophouses are only 7–19 BU tall, smaller
   than the towers around them.
3. **Map: painted roofs only** (`map_painted_roofs_home.jpg`, `map_painted_roofs_dispatch.jpg`).
   - **The stencil.** The fist crest is laid over the rooftops as a stencil, in the map's own projection
     (`cfg27.py`). Each roof is painted only where it falls inside the crest, so the fist is broken up by the roof
     edges and seams.
   - **The same test everywhere.** Blender clips the roof polygons with the same rule (`pieces_lot`) as the map
     (`pieces_screen`).
   - **Home:** crude red roller paint with a ragged edge, lime and pink graffiti strokes, and drips down the walls.
   - **DISPATCH:** the paint glows harsh red. Glitch bars are torn sideways past the roof edges, and black
     corruption blocks sit on top. Hijacked screens and signs turn red, and some go dark.
4. **Combat backdrop: the Tokyo canyon** (`canyon_close_night_home.jpg`, `canyon_close_night_dispatch.jpg`).
   - **The street.** The canyon is the real grid street j = 36, from i 27 to 46, at the city's own street width
     (1 lot). The cross streets at i 32/36/40 stay open.
   - **Dressing.** Stacked blade signs, wires, lantern strings, vending machines and hijacked billboards. Scanline
   hologram fists float over each crossing, with a fist billboard at the head of the street.
   - **Consistency.** The painted block sits beside the canyon: its red roofs show on the left of the close-up and
     on the map. The map sprite is the same Blender model as the close-up.
   - **Camera.** An elevated telephoto looks down the street (the round 25/26 combat zoom). The nearest shophouses
     are kept low, so the street is the focus and the wheels overlap its sides.
5. **`combat_rebel_cell.png`:** the DISPATCH canyon behind the round 25 composite. It has the locked D4 player
   wheel, the round 18 DISPATCH boss wheel, sticker cards and SEND IT.

## Weakest parts / open
- **The fist reads as a red patch more than a crisp fist.** The fingers are readable, but the wrist is half hidden
  by the tower in front.
- **The DISPATCH canyon has fewer signs.** About a fifth of them go dark, and the rest are red, so it is less rich
  than home.
- **The glyphs are still blocky placeholders.**
- **The level roof field can look like a single slab.** On the map, the painted tenements are a little more
  regular than the city around them.

## Build (from `scripts/`)
1. `python layout27.py`
2. `python run27.py canyon:close canyon:close:dispatch canyon:map canyon:map:dispatch`
3. `python post26.py rc27_canyon rc27_canyon_dispatch`
4. `python map27.py`
5. Render the wheels:
   - `python wheels_r18/render_bosses24.py rebel_cell`
   - `python wheels_r18/dump_boss_slots24.py`
   - `python combat_r23/render_player24.py`
6. `python make_out27.py`

The environment variable `CAM27="x,y,z,tx,ty,tz,lens"` overrides the camera for reframing. `CREST_DEBUG=1` outlines
the stencil on the map.
