# Round 28: the Cell's district: map fist v2, darker canyon, motion, street-level combat

The district and the canyon are the round 27 ones: normal street grid, no fist streets, the canyon is grid street
j = 36.

## 1. Map fist (`map_fist_paint_v2_*.jpg`, `map_fist_holo_*.jpg`)
- **Paint v2.** The fist is now drawn with a few thick roller strokes, not filled blocks:
  - the knuckle bumps, three finger splits, the thumb across, both sides, and a wrist band;
  - the strokes are defined in `cfg28.py` (`STROKES`) and clipped to every roof in the map's own projection, so
    Blender and the map agree (`clip_convex`).
  - The painted block is now one level roof field with no parapets, so the strokes run on across roofs.
  - The lime/pink tags are sparse, so the red strokes lead.
  - **DISPATCH:** the strokes are re-lit harsh red, torn by glitch bars and blacked out in places.
- **Hologram (second idea).** A translucent fist hovers just above the painted block's roofs. It has scanlines
  along the street grid, a hot outline, a pink ghost copy, and light cast onto the roofs below (`map28.holo_2d`).
  - **DISPATCH:** red, with bands torn sideways and dropping out, and black corruption blocks.
- **Verdict.** The hologram reads as a fist instantly; the paint reads as a fist when you look for it. Paint is the
  subtle option, hologram the loud one.

## 2. Darker canyon (`canyon_close_night_*.jpg`, `canyon_street_night_*.jpg`)
- **Less sign light.** Signs and holograms are at about 55 % emission. Windows are dimmer and the toon ramp is one
  step darker.
- **Shop fronts.** They are now dark glass with a few lit panes and a lit doorway, not one big glowing panel.
- **Less glow.** The road lane glow is cut to 35 % up close (22 % at street level). The post pass has much less
  bloom (0.36) and spill (0.18): `backdrop28.MODE["canyon"]`.
- **Added street detail.** 34 pedestrians (umbrellas, phone glows) and street lamps.

## 3. Motion (`combat_rebel_cell_motion.gif`)
- 960 × 540, 12 frames at 140 ms, 2.1 MB. It is the DISPATCH boss fight with the locked UI.
- **What moves** (`kit26.anim()`, seeded by sign and frame, so the layout never moves):
  - signs and screens flicker or go dark;
  - every third panel scrolls its glyphs; another third swaps between ad and fist;
  - hologram scanlines crawl;
  - rain is re-seeded per frame.
- **DISPATCH** drops out more and adds row-tearing glitches.
- `combat_rebel_cell.png` is the still.

## 4. Street level (`combat_street_level.png`, `canyon_street_night_home.jpg`)
- **Camera.** Eye height (1.15 BU), 21 mm, looking down the canyon.
- **What's in frame.** Signs stacked overhead, wires and lanterns crossing, people under umbrellas, and vending
  machines. The alley vanishes into violet haze, from a depth-based haze in the post pass (`--street`).
- **Composite.** The wheels and HUD are the round 25 composite, unchanged.

## Weakest parts / open
- **The hologram is screen-aligned on the map.** It does not lie in the iso plane. That reads well, but it looks like
  a decal more than a hovering layer.
- **The paint fist is still only fair at full-map zoom.** The thumb and fingers merge into one red band.
- **Street level is dark.** In `combat_street_level.png` the wheels cover most of the alley, and the lane strokes on
  the floor still dominate the lower third.
- **The gif motion is subtle at 960 wide.** It is mostly flicker and swaps; the scroll steps read only on the big
  boards.

## Build (from `scripts/`)
1. `python layout27.py`
2. `python run28.py canyon:map canyon:map:dispatch`, then `PAINT28=none TAG28=_nopaint python run28.py canyon:map canyon:map:dispatch`
3. `python map28.py`
4. `python render_all28.py stills gif`
5. Render the wheels:
   - `python wheels_r18/render_bosses24.py rebel_cell`
   - `python wheels_r18/dump_boss_slots24.py`
   - `python combat_r23/render_player24.py`
6. `python make_out28.py`
