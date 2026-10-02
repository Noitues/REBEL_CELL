# Round 25: the boss target IS the HQ (one model for the map and the close-up)

## The core rule and how it's met
**A boss fight takes place at the corp's HQ**, and the zoomed-in combat view must match the full city map.

1. **One street layout.** `scripts/citydata.py` reads the game's exported city (`round6_city_restyle/city_layout.json`, read-only) and converts it from the game's iso screen space back to lots. The conversion is `X = ox + (x−y)·34`, `Y = oy + (x+y)·17`, inverted.

   It exports a window around each HQ and Site containing the city's own:
   - street tiles, with their lane colours and traffic;
   - every building (footprint, base, height, taper);
   - plazas, traffic trails and REBEL_CELL's fist roads.

   `hq_scene.py` rebuilds exactly that in Blender: 1 lot = 6 units, and heights are scaled from map pixels. The glowing lanes follow the round 6 restyler's rules, so **the streets round each HQ in the close-up are the map's streets**.
2. **One HQ model.** Each HQ is a single builder in `heroes25.py`, rendered by `hq_scene.py` with two cameras:
   - `close`: the perspective combat close-up;
   - `map`: an orthographic camera in the game's 2:1 iso projection, transparent, with the city buildings set as holdout.

   `city_hq_v3.py` takes the old HQ drawings out of the round 6 map and pastes in the `map` sprite of the same model, inked to match. The other HQs that are in view of a close-up are built too, so the skyline also agrees: for example, the castle stands behind the Civic Core.
3. **Regular fights** take place at smaller Sites. Each Site is a street-free block inside the corp's own district, picked from the layout, and stands on the real roads round it (`site_<corp>_night.jpg`). The Site buildings are the round 24 designs, scaled down to a 6 × 6 lot block.
4. **The fist rule.** City buildings that stood on REBEL_CELL's fist roads are removed on both the map (v3) and in the close-ups, so the fist reads in both views.

## Files
| File | What it shows |
|---|---|
| `hq_<corp>_city.jpg` | City-map crop around each HQ (from `city_night_hq_v3.jpg` at full resolution). |
| `hq_<corp>_close_night.jpg`, `hq_<corp>_close_day.jpg` | Combat close-ups, with the area behind the wheels softened and darkened. |
| `hq_orbital_close_night_open.jpg` | Orbital with the silo open. |
| `hq_rebel_cell_close_night_dispatch.jpg` | The Cell's base after the betrayal (DISPATCH). |
| `combat_<corp>.jpg` | The boss fight on the HQ: locked D4 screen, round 18 boss wheel, sticker cards, SEND IT. Orbital uses the open silo; REBEL_CELL uses the DISPATCH base. |
| `site_<corp>_night.jpg` | The regular Sites. |
| `city_night_hq_v3.jpg` | The full city night view, with the same framing and labels as round 24. |
| `hq_compare.jpg` | One row per corp: map crop, close-up night, day or variant, combat, Site. |

**Build** (from `scripts/`):
1. `python citydata.py`
2. `render_all25.ps1` (17 Blender jobs, about 40 minutes)
3. `python backdrop25.py`
4. `python city_hq_v3.py`
5. Boss wheels and slots: `wheels_r18/render_bosses24.py`, `wheels_r18/dump_boss_slots24.py`, `combat_r23/render_player24.py`
6. `combat_r23/make_combat25.py`
7. `make_compare25.py`

## The HQs
- **Meridian: the Container Castle.** It replaces the ziggurat, which was too close to Halcyon's.
  - Curtain walls of shipping containers in a running bond, three courses high, with container merlons.
  - Four corner towers of crossed container courses with arrow-slit lights and flags.
  - A nine-course keep.
  - A gatehouse with two towers, a portcullis, a container drawbridge on chains over a lit moat, and the MERIDIAN sign.
  - Two gantry cranes at the back corners as siege towers, swinging containers over the walls.
- **Solace: the Double Helix.** There is no central tower now.
  - Two thick strands, one calm teal-white and one calm lime, rise from a podium. Each has a dim glow seam.
  - Thin walkways with railings connect the strands like base-pair rungs all the way up.
  - The bright lime is kept to the rung strips, node lights and pod ring lights.
- **Halcyon: the Civic Core, taller.** Seven colonnaded tiers instead of four, grand stairs, and the amber eye on top. Radar dishes and police cars are kept.
- **Orbital: the Silo Crescent.** The liked mast and dishes now stand in a crescent at the back of the plaza, with a low ops wall.
  - In the middle are flat missile-silo doors with a hazard rim.
  - **Closed:** flat doors with a cyan seam and red corner lights.
  - **Open:** the doors swing up and a white missile nose with cyan and red bands sticks out of the glowing shaft.
- **REBEL_CELL: the Cell's hidden base.**
  - A walled courtyard of old tenements and a converted deck sits in the palm of the fist roads. In the close-up the same glowing red fist road network leads in, matching the map.
  - **Home:** warm windows, a lime and pink courtyard glow, string lights, a sunken entrance ramp, a jury-rigged relay mast, rooftop solar and tarps, and a pink fist mural on the deck roof.
  - **DISPATCH (after the betrayal):** the same base turned red. Red vents and corrupted floor slabs, red cables from the mast into every roof, a DISPATCH sign.

## Meridian assets that should follow the castle
Not changed in this round:
- **Crest** (round 15/17, a crane hook and container): could become a container turret or a crenellated container.
- **Boss wheel crest / emblem** (`EM_MERIDIAN` in d4corp and the round 18 wheels, and the badges on The Manifest's wheel): use the castle crest.
- **Raid and campaign-loss frames, and Meridian threat stickers** (round 19–22 raid work): any frame showing the ziggurat should show the castle.
- **The round 11 combat target, `target_building_*.jpg`**: replaced by `hq_meridian_close_*`.
- **The round 24 Meridian HQ cranes** are superseded; the cranes now stand at the castle's corners.

## Weakest parts / open
- **District colours on the map are still the round 6 palette** (Solace teal, Orbital blue). Only the HQs follow round 17. A territory-colour pass is still needed.
- **The Orbital silo sits low in the frame,** half behind the dishes from the combat camera. The open missile is clear, but small next to the mast.
- **The Cell's base is small in its close-up,** because the camera has to show the whole fist. Its home and DISPATCH states read clearly in the detail crops, less so at thumbnail size.
- **Day close-ups pick up heavy blotchy grime in the sky.** The grime noise from the round 11 style pass is too strong there.
- **The map sprites are lit in Blender**, so they look slightly smoother than the round 6 faceted city round them.

Note: the build scripts write PNGs; every deliverable was saved as a JPG (quality 90) to keep the folder under 45 MB (19 MB).
