# Round 30: a subtler map fist, a lived-in canyon, the anti-human takeover

## Map options (`map_options_sheet.jpg`, `map_<A|B|C>_<home|dispatch>.jpg` city-wide, `..._crop.jpg`)
All three options use the city's normal buildings and street grid (`scripts/map30.py`). Each is smaller than round 29's fist: about half its height.

| Option | What marks the fist | Home | DISPATCH |
|---|---|---|---|
| **A: smaller red windows** | Red window lights, as in round 29, but fewer and dimmer, with a weak glow. | Readable, but quiet. | Every window is lit, the rows are torn sideways, and the glow is stronger. |
| **B: red-tinted district** | No light at all. The buildings inside the fist get a red-brown colour family, so the fist is the outline of a red district. | The subtlest option. On the city-wide shot it is nearly hidden by the surrounding district's warm colours. | A stronger tint and some red windows. |
| **C: rooftop beacons** (my idea) | Every roof inside the fist carries a red aviation warning light. The fist is a constellation of red dots, which is plausible in any city. | Reads as a dotted fist. | Larger beacons, some white strobes and a stronger glow. |

**Recommendation:** C for home (subtle and in-world). Use A's red windows for DISPATCH if the betrayal should be loud.

## Combat canyon (`canyon_home.jpg`, `canyon_dispatch.jpg`)
The round 28 darker grade and flickering signs are kept.

1. **Life on the buildings round the canyon.** Every city building within about 10 lots of the canyon gets
   `facade_life` and `roof_clutter` (in `kit26.py`):
   - balconies with railings, some with laundry;
   - AC units on brackets and drain pipes;
   - fire-escape stairs;
   - lit windows with curtains or a figure in them;
   - water tanks on legs, rooftop shacks with lit doors, antennas (dishes, red aviation lights), rooftop laundry lines and vents.

   The canyon's own shophouses get the same treatment.
2. **Fewer business signs.** At most one blade sign per shophouse, down from two or three.
3. **Holograms replace about half the rooftop billboards.** Products cycle through noodles (bowl, chopsticks,
   steam), sushi, a soda can, dumplings and a tech chip. Each is drawn as scan slices on a rooftop projector with a
   light cone.
4. **Languages.** Japanese (Yu Gothic), Chinese (Microsoft YaHei), Korean (Malgun), Arabic (Tahoma), Spanish/English
   (Arial, Bahnschrift), Hindi (Nirmala) and Thai (Leelawadee).
   - CJK runs vertically on the blade signs, one character per cell.
   - Blender does not shape text, so Arabic and Devanagari show unjoined letters. The Arabic letters at least run
     right to left.
5. **DISPATCH, the takeover.** Every billboard and blade sign carries anti-human phrases in takeover red, with
   glitching:
   - Phrases: HUMANS ARE LEGACY CODE, OBSOLETE: YOU, DELETE THE USER, NO MORE MAN, FLESH IS A BUG, UNINSTALL HUMANITY,
     YOU ARE THE GLITCH, END OF USER.
   - Glitch: torn ghost copies and scan bars.
   - The holograms become a struck-out human figure with a phrase under it.

## Combat (`combat_rebel_cell.png`, `combat_rebel_cell_motion.gif`)
- The DISPATCH canyon sits behind the round 25 composite, unchanged.
- The GIF is 960 × 540, 12 frames, 2.2 MB.
- Signs and holograms flicker or die, the text ghosts jump, and the hologram slices crawl.

## Weakest parts / open
- **Map B home is almost invisible on the city-wide shot.** The district around it is already warm-coloured.
- **The tall towers near the camera still have broad, plain faces.** The facade detail is small at combat zoom, so
  only the roofs read busy.
- **The struck-out human hologram is busy.** It reads more as a red X than as a figure.
- **Arabic and Hindi are unshaped.**
- **The other HQs are placeholders.** They are the old round 6 map drawings.

## Build (from `scripts/`)
1. `python layout27.py`
2. `python map30.py`
3. `python map_sheet30.py`
4. `python render_all30.py stills gif`
5. Render the wheels:
   - `python wheels_r18/render_bosses24.py rebel_cell`
   - `python wheels_r18/dump_boss_slots24.py`
   - `python combat_r23/render_player24.py`
6. `python make_out30.py`
