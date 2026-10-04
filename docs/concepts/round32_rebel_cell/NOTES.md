# Round 32: the fist gets structure; a brighter canyon with full signs

## Map (`map_A_*.jpg`, `map_ring_*.jpg`, `_crop.jpg`, `map_ring_blackout.gif`)
- **A solid red fist.** It is now one silhouette (`map32.Crest.zone`), and its internal details are drawn with **blacked-out buildings**:
  - three finger splits;
  - the thumb's upper edge folded across the fingers;
  - the thumb tip turning down;
  - a knuckle crease on each finger;
  - the palm/wrist line and a cuff band.
- **How the dark lines are made.** On those lines, buildings carry no windows at all. Their facades are darkened about 60 %, and the lines get a slight extra darkening in screen space so they stay crisp.
- **Fist size.** The red-window density is up (home 90 %) and the fist is a little larger than round 31's (880 px tall instead of 760), so the structure reads.
- **The blackout ring** from round 31 still surrounds the fist. The GIF is 640 × 460, 24 frames, 2.7 MB.

## Canyon (`canyon_home.jpg`, `canyon_dispatch.jpg`)
- **Brighter.** Sign emission is 0.72 and windows 0.85, up from 0.55 and 0.62. The toon ramp and grade are lifted, and haze is lower.
- **Every blade sign is filled edge to edge** (`kit26.dense_blade`):
  - a bright logo header with a pictogram (bowl, cup, chip, fish, pharmacy cross or phone);
  - the name: a vertical language text or dense glyphs (CJK runs one character per cell);
  - a column of small print;
  - a three-row menu footer, each row with a bright price tag.

  In DISPATCH the same layout is red, and the name is the anti-human phrase.

## Combat
- `combat_rebel_cell.png` and `combat_rebel_cell_motion.gif` (DISPATCH, 960 × 540, 2.5 MB).

## Weak / open
- **The detail lines look a little grid-like,** like a stencil. A curved thumb would be more organic.
- **On the city-wide shot the REBEL_CELL label covers part of the fist.**
- **In DISPATCH the blade-sign phrases are small** now that the header and footer take space.

## Build (from `scripts/`)
1. `python layout27.py`
2. `python map_all32.py`
3. `python render_all32.py stills gif`
4. `python wheels_r18/render_bosses24.py rebel_cell`
5. `python wheels_r18/dump_boss_slots24.py`
6. `python combat_r23/render_player24.py`
7. `python make_out32.py`
