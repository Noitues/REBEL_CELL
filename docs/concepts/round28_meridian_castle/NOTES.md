# Round 28: texture passes on the Meridian castle

The fortress **shape** is locked: round 27's A, the Container Wall. The Halcyon Court is locked; the sculpted sphinx stays in the library (`round27_hq_targets/site_halcyon_sphinx2_night.jpg`). Earlier rounds are untouched, nothing is committed, and `scratch/` is cleared.

## How the textures are made
**Everything is real geometry, so the cel shading and ink pick it up.** The new `heroes28.py` replaces `obox()`, the function that builds every container in the fortress. Its four variants are switched with `STATE = t1 … t4`. Each container now gets:
- deep corrugation: alternating raised (light) and sunk (dark) ribs;
- top and bottom rails;
- a door end with four lock bars.

Each variant then adds its own options:
- rust streaks running down from the top rails;
- white stencil plates;
- a white Meridian band across the towers;
- lit course seams.

Fortress-level dressing (also per variant):
- big `MRDU` stencil codes on the front towers;
- yellow and black hazard stripes on the gate and tower feet;
- tarps and cargo nets;
- floodlights with light cones.

## Options (`castle_texture_options.png`)
Each variant is shown as a night close-up facing the gate, plus its city-map crop.

| Variant | Look | Verdict |
|---|---|---|
| **A: Raw corrugated steel** | Clean, unified Meridian orange | Reads as new kit; a bit plain. |
| **B: Mixed liveries and rust** | Real mixed container colours (red, blue, teal, white) with an orange band | The most "made of containers", but it loses Meridian orange. |
| **C: Weathered Meridian (recommended)** | Burnt orange with heavy rust and grime streaks, MRDU stencils, hazard stripes, tarps and nets | It reads as both Meridian and a used, owned fortress, and stays calm behind the wheels. |
| **D: Lit fortress** | Charcoal walls, a white tower band, lit seams, floodlight washes | A spectacle, but it is brighter than the wheels. |

## Recommended: C
- `hq_meridian_close_night.jpg`, `hq_meridian_close_day.jpg`
- `hq_meridian_city.jpg`: round 27's map crop with C's map sprite composited at the HQ position. The shape is the same, so it covers the old one.
- `combat_meridian.jpg`: the same zoom as round 26, face-on to the gate.

## Build (from `scripts/`)
1. `python citydata.py`
2. `render_all28.ps1`
3. `python make_round28.py`
4. `wheels_r18/render_bosses24.py meridian`, `wheels_r18/dump_boss_slots24.py`, `combat_r23/render_player24.py`, `combat_r23/make_combat27.py meridian`

## Open
- **The tarps and cargo nets are small at combat zoom.** The rust streaks and stencils carry the weathering.
- **The full city map (`city_night_hq_v5`) has not been re-rendered** with C. Run `city_hq_v5.py` with the round 28 scripts to update it.
