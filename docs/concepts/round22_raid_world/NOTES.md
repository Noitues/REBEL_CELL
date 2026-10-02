# Round 22: raid world (Rigger idle, class colours, slow/repair v2, icons v4 + unit health)

Locked from round 21: the R3 station beacons, and the campaign dossier / audit report. The raid UI half is in `round22_raid_ui/`.

## Files
| File | What |
|---|---|
| `operator_rigger.gif` | 25 frames, 1.0 MB. The Rigger beacon idle: cable rings climb the cone, the goggles BLINK, and every so often the face turns ANGRY (scowling brows cut the lenses, the cable smile flips to a frown). Small text in the gif proposes: blink every ~3 s, angry about 1 loop in 6 or when its node takes damage. |
| `class_colours_v2.png` | Phantom and Botnet separated. Phantom is now pale lilac `#DBC1FF` (an afterimage), Botnet is indigo-blue `#6072FF` (a swarm), and Hivemind keeps the violet. The sheet shows the round 21 swatches, the round 22 swatches and the Rigger angry/blink stills. |
| `bonus_slow_v2.gif` | 1.0 MB. The dashed edge carries the effect. **SLOW:** slow blue dashed rings drift inward. **FROZEN** (levelled): blue/white ice crystals grow from the edge inward over a light-blue translucent fill, the edge goes ice-white, and the unit is iced over with the frozen glyph. |
| `bonus_repair_v2.gif` | 0.5 MB. Health goes UP: a column of integrity cells stacks upward beside the socket, and "+" marks and streaks rise straight up. Levelled: CORE repairs too. |
| `station_bonuses.png` | The round 21 sheet with B and E replaced by v2. Same mapping table. |
| `vehicle_icons_v4.png` | 4 types × 5 corps, the health drain stages, status pips on the ring, the heading arrow, and the 30 units at map scale. |
| `vehicle_toggle_v3.png` | On the street, each unit stands in a filled corp-colour health disc that drains top-down, inside a bigger dashed corp ring. Zoomed out, the icon carries both. |
| `unit_health.gif` | 24 frames, 0.5 MB. The Meridian Hauler+ loses HP: the street disc and the icon fill drain top-down. The ring picks up SLOWED, then FROZEN, then BURNING + EXPOSED. The heading arrow shows during the hover frames only. |
| `contact_sheet.jpg`, `scripts/` | |

## Icon v4 rules
- **SHAPE = type:**
  - **FAST:** chevron badge. The `>>` glyph is raised by 0.22 r so it clears the badge notch.
  - **HEAVY:** block.
  - **SPECIAL:** hexagon with its verb glyph. Orbital's special is the old lander, glyph DROP; the separate lander row is gone.
  - **FLYING:** a diamond with a rotor circle at each corner. The glyph is a 2×2 set of black circles: a drone without its body.
- **FILL = corp colour = health:**
  - The fill is full at max HP and drains from the top down. A white drain line marks the level.
  - The drained part is a dark tint of the corp colour.
- **RING = a dashed circle about 1.8× the icon:**
  - It is in the corp colour. REBEL_CELL's red is paled to `#FFAAAC` so the dashes read.
  - Status pips ride the ring clockwise from the top-right: slowed, frozen, burning, exposed, corrupted.
  - The heading arrow (yellow) rides the ring on hover / selection only.
- **UPGRADED:** two white chevrons on top and a double rim.
- **On the street:** the same rule as the icon. A filled disc under the unit drains in screen space from the top. The dashed corp ring carries the same pips and the hover arrow. This replaces the round 19 red segmented HP ring.

## Godot build notes
- **Rigger:** the emblem is two sprites (lenses + mouth) driven by an AnimationPlayer: a lens `scale.y` blink, plus an angry pose (brow sprite, mouth swap).
- **Ice:** the same language as the UI agent's frozen look: crystal triangles in white-blue, a light-blue translucent fill.
  - The slow field's edge is a ground decal shader. Uniforms: radius, dash phase, inward ring phase, freeze 0..1.
  - At freeze 0..1 a crystal spike texture grows inward along the radius.
- **Repair:** a column of cells (a 2D billboard above the socket); particles move straight up.
- **Health disc:**
  - The unit decal shader takes `hp` and fills where the projected screen-v coordinate is below the threshold.
  - The icon shader uses the same uniform with a mask per shape (an atlas of 4 shapes).
  - The ring is a dashed ring texture, scrolled. Status pips are child sprites at fixed angles.

## Rebuild
1. `python scripts/emblems20.py`
2. `python scripts/run_blender21.py roofB bonus bonus_nh wave`
3. `blender -b --factory-startup --python scripts/vehicles20.py -- <abs>/scratch/bl`
4. `python scripts/screens22.py` (all sheets and gifs)

Seeded throughout. The round 21 scripts were copied; `screens21.beacon()` gained an `EMBLEM_OVERRIDE` hook, and `roof20.CLASS_COL` has the new Phantom and Botnet colours.

## Open
- **Phantom's lilac:** it is pale, so its beacon reads almost white. A deeper lilac (`#C9A6FF`) is the fallback if it reads as "neutral".
- **Street health disc vs the model:** the disc partly hides under the vehicle model, so on bulky units the icon is the clearer read.
