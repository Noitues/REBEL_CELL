# Round 31: map A + blackout ring, canyon detail pass

## Map
- `map_A_{home,dispatch}.jpg` (city-wide) and `_crop.jpg`: option A, the smaller red-window fist (chosen in round 30).
- `map_ring_{home,dispatch}.jpg` and `_crop.jpg`: option A plus the **blackout ring**.
  - **What goes dark:** in a rough circle round the fist, the city's own window lights are switched off. Roof trims and the street glow in the ring are also dimmed by up to 55 %.
  - **The effect:** the red fist stands in a dark moat.
  - **What stays lit:** the fist's own buildings.
  - **How it's done:** `map31.py`. The circle is wobbly (a few sine terms on the radius), with a soft outer edge.
- `map_ring_blackout.gif` (720 × 518, 24 frames, 2.8 MB): the ring lights flicker off from the inside out, first home then DISPATCH.
  - **The animation:** each window has its own seeded threshold. Windows near the advancing front flicker on and off between frames, then stay off.

## Canyon
- **No blank tower faces.**
  - **Removed:** the bare spires right in front of the camera.
  - **Added detail (`kit26.tower_skin`):** every tall face round the canyon now gets floor ledges every three floors, pilasters, a lit stair-core light column, and a large vertical wall sign. The sign is in one of the city's languages at home, or an anti-human phrase in DISPATCH.
  - **More lit windows:** the lit-window rate on tall faces is about doubled. The detail range now also covers the towers next to the camera.
- **Fuller signs.**
  - **Language signs:** every one now carries a line of small print, a price strip and a pictogram (bowl and steam, a cup, or a chip) under its name.
  - **Glyph lettering:** 92 % filled, up from 62 %.
- **Microchip holograms.** The chip hologram is now a big MICROCHIP: a translucent package with a hot outline, 7 pins on each side, a glowing die and L-shaped circuit traces. It turns on its projector (30° per animation frame) and is shown at 1.6× the size of the other holograms.
- **Home has no fists, even in motion.** The animated swap now changes a home sign to another language sign, never to a fist.
- `canyon_home.jpg`, `canyon_dispatch.jpg`, `canyon_home_motion.gif` (800 × 450, 2.9 MB; the chips turn).
- `combat_rebel_cell.png` and `combat_rebel_cell_motion.gif` (DISPATCH, 960 × 540, 2.5 MB).

## Weak / open
- **The microchips are at the far end of the canyon.** They are partly cut off by the top of the frame at combat zoom.
- **The blackout ring is clearest in the crops.** On the full-city shot it reads as a darker patch.
- **The DISPATCH canyon looks like round 30's.** The tower signs are there, but their red phrases are small behind the wheels.

## Build (from `scripts/`)
1. `python layout27.py`
2. `python map_all31.py`
3. `python render_all31.py stills gif homegif`
4. `python wheels_r18/render_bosses24.py rebel_cell`
5. `python wheels_r18/dump_boss_slots24.py`
6. `python combat_r23/render_player24.py`
7. `python make_out31.py`
