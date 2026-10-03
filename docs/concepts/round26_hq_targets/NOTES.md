# Round 26: HQ targets with closer combat framing

**Locked from round 25:**
- the map = close-up rule;
- the Solace helix form;
- Halcyon's extra levels and stair ramps;
- the Orbital rocket;
- the Meridian regular Site.

REBEL_CELL is explored in `round26_rebel_cell/` and is skipped here. Its round 25 base stays on the city map.

Earlier rounds are untouched. `scratch/` is cleared.

## The rule (unchanged): the boss target IS the HQ, and map = close-up
- **Same roads.** `citydata.py` turns the game's city layout (`round6_city_restyle/city_layout.json`, read-only) back into lots. Every close-up rebuilds the city's own street tiles, lanes, buildings, plazas and fist roads around its HQ or Site.
- **Same model.** Each HQ is one builder (`heroes26.py`), rendered as both the close-up and the map sprite. The map sprite is pasted into `city_night_hq_v4.jpg`.
- **New this round: the view corridor.** A city building standing between a close-up camera and its HQ or Site, and tall enough to hide it, is removed (`citydata.blocks_view`). It is removed from the close-ups **and** from the city map, so both still match. This is what removes the tall tower that stood in front of Orbital's HQ.

## Combat framing (all corps)
The cameras are much closer. The HQ fills the gap between the wheels and the wheels overlap it, as with round 11's ziggurat.
- **Meridian:** the camera looks straight at the drawbridge, along +X.
- **The other HQs:** the camera keeps the map's diagonal.

Camera settings are in `hq_scene.py` under `CAMS`.

## Meridian: container castle
**`meridian_castle_options.png`** compares four silhouettes, each built only from containers, at night and from the combat camera, with its map sprite at two sizes:
- A: concentric (Beaumaris);
- B: motte and bailey;
- C: star fort;
- D: tiered (Himeji).

**Chosen: B, motte and bailey.**
- From afar it has the clearest silhouette: one tall keep, a dark ring wall and a gate.
- A is too busy at map size.
- C's star only reads from above.
- D reads as a pagoda, not a castle.

**How the castle reads from afar** (the same kit is used on all four options):
- **Colour contrast.** The curtain walls are dark rust containers. The drum towers are bright orange and white, in a "lit toon" material: toon shading plus a warm self-light, so they read as floodlit, with small floodlights at their feet.
- **Lit battlements.** Amber lines run along every wall top and round every tower top.
- **Banners and gate.** Long orange banners with a white stripe, and a glowing gate with a portcullis.
- **Drawbridge.** A container on chains over a lit moat.

**Files:** `hq_meridian_close_night/day.jpg`, `combat_meridian.jpg`. The Site is the locked depot.

## Solace: the helix, lit
- **Down-lighting.** A bright strip runs along the underside of each strand, with soft light cones falling from it.
- **Spotlight.** A spotlight at the bottom centre points straight up through the helix.
- **LED chaser.** A band of bulbs climbs both strands (`solace_helix_lights.gif`, 12 frames, about 0.7 MB).

The strand colours stay calm; the lights carry the lime. The chaser is the frame-0 position in the stills.

**Regular Site: SOLACE GENERAL hospital.** A clinic block with two wings, a lime cross, an ambulance bay with ambulances, and a rooftop helipad.

## Halcyon: the Civic Core and its scanning eye
- **Changes.** The radar dishes are removed. The seven tiers and the stair ramps are kept.
- **The eye.** It is built as its own objects and turns about the pylon, sweeping ±55° with a translucent amber searchlight and a lit spot on the ground (`halcyon_eye_scan.gif`, about 1.8 MB, plus `halcyon_eye_scan_strip.jpg`). The stills and combat use the frame where it has turned 28° toward the left of the frame.
- **Regular Sites (both on the same plot):**
  - `site_halcyon_sphinx_night.jpg`: a civic sphinx on a plinth, with the amber eye on its headdress, amber headdress stripes, obelisks and police cars.
  - `site_halcyon_police_night.jpg`: the precinct as a POLICE station, with a lit sign and a red/blue roof bar, and no dish.

## Orbital: the silo is in the ground
- **The launch podium.** The plaza is a launch podium. The silo is a round hole with a yellow and black caution ring on the rim.
- **The doors.** They sit 1.6 units **below** the rim, so their edges never show above ground.
  - **Closed:** a cyan seam and red marker lights.
  - **Open:** the doors **slide sideways** into the podium and the rocket's nose rises out of the glowing shaft.
- **Kept:** the crescent of mast and dishes, and the rocket.

**Files:** `hq_orbital_close_night.jpg` (closed), `hq_orbital_close_night_open.jpg`, `hq_orbital_close_day.jpg`. `combat_orbital.jpg` uses the open silo.

**Regular Site: OC-TV.** A broadcast studio with three radar dishes on the roof, a lattice mast with red lights, a big video screen and an uplink truck.

## Files
| File | What it shows |
|---|---|
| `hq_<corp>_close_night.jpg`, `hq_<corp>_close_day.jpg` | Close-ups, with the area behind the wheels softened. |
| `combat_<corp>.jpg` | The boss fights. |
| `site_<corp>[_variant]_night.jpg` | The regular Sites. |
| `hq_<corp>_city.jpg` | City-map crops. |
| `city_night_hq_v4.jpg` | The full city night view. |
| `hq_compare_v2.jpg` | The round 26 comparison sheet. |
| `meridian_castle_options.png` | The four castle silhouettes and the choice. |
| `solace_helix_lights.gif`, `halcyon_eye_scan.gif` | The two animations (both under 3 MB). |

**Build** (from `scripts/`):
1. `python citydata.py`
2. `render_all26.ps1` (17 Blender jobs; anim mode renders 12 frames in one session)
3. `python backdrop26.py`
4. `python make_gifs26.py`
5. `python city_hq_v4.py`
6. Boss wheels and slots: `wheels_r18/render_bosses24.py`, `wheels_r18/dump_boss_slots24.py`, `combat_r23/render_player24.py`
7. `combat_r23/make_combat26.py`
8. `python make_sheets26.py`

The Meridian options are `hq_scene.py -- meridian_hq <dir> preview|mapprev <concentric|motte|star|japan>`.

## Weakest parts / open
- **Halcyon's searchlight is the brightest thing behind the player wheel** in combat; it was toned down once already. In game it moves, so it will draw the eye. If it competes, dim it further or fade it while the player is aiming.
- **The translucent cones are dithered.** The searchlight and Solace's spotlight show grain.
- **District colours on the city map are still the round 6 palette.**
- **The castle keep at map size reads as a single tall drum.** A crown of merlons or a flag on it would help.
