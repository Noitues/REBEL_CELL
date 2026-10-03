# Round 30: Meridian castle with a rail yard, finer detail, faceted moat and motion

The castle is round 29's locked A: texture A, lower walls, the moat, and the crane keep with its boom lowered. Earlier rounds are untouched, nothing is committed, and `scratch/` is cleared.

## What's new (`scripts/heroes30.py`)
1. **Train tracks** run on the side the boom reaches (world +Y, past the moat):
   - a loading track under the boom and a through track, with rails, sleepers and ballast;
   - yard light masts and green signals;
   - a waiting freight train: an orange locomotive with hazard chevrons, and flatcars, one of them empty under the boom.

   The city buildings in that strip are removed on both the map and the close-ups (`citydata.blocks_view`), so the map = close-up rule still holds.
2. **More polygon detail:**
   - ladders up the front towers and the gate towers;
   - a catwalk with railing and lamps along the front wall;
   - bolt caps on the tower corners and red warning lamps at the gate;
   - on the crane: bolt bands and a ladder on the legs, and lights under the boom.

   The round 28 corrugation and door detail on every container is kept, as is the cel/ink style.
3. **Faceted moat water.** A triangulated low-poly grid with height jitter and tone variation. Facets near the lit towers and the gate catch the light as orange glints.
4. **Motion.** The moving parts are built once per animation frame (16 frames), and each frame renders its own ink, id and depth passes, so the line art follows the crane.
   - **The loop:** the trolley carries a container out over the wall and the moat, lowers it onto the empty flatcar, and returns while the boom lifts and settles. Then it picks up the next container. A through freight train passes in the second half.
   - **`combat_meridian_motion.gif`:** the loop under the combat HUD (960×540, 16 frames at 160 ms, about 2.4 MB), plus `combat_meridian_motion_strip.jpg`.
   - **The motion is mostly hidden behind the boss wheel**, so `meridian_backdrop_motion.gif` (about 3.5 MB) shows the same loop without the HUD. In it, the boom lift, the container travel and the passing train all read clearly.

## Files
- `combat_meridian.jpg`
- `hq_meridian_close_night.jpg`, `hq_meridian_close_day.jpg`
- `hq_meridian_city.jpg`
- `city_night_hq_v6.jpg`: the full map with the round 30 Meridian, including the tracks.
- `combat_meridian_motion.gif`, `combat_meridian_motion_strip.jpg`, `meridian_backdrop_motion.gif`

## Build (from `scripts/`)
1. `python citydata.py`
2. `render_all30.ps1`
3. `python backdrop30.py`
4. `python city_hq_v6.py`
5. `wheels_r18/render_bosses24.py meridian`, `wheels_r18/dump_boss_slots24.py`, `combat_r23/render_player24.py`
6. `python make_motion30.py`

## Open
- **In combat, the boom, the trolley and the trains sit behind the boss wheel** (right side). The crane's A-frame and legs in the centre gap show the lift. To show the train under the HUD, the yard would have to be on the left (mirror the crane), where the player wheel sits.
- **On the map, the tracks are thin at map scale.** The train reads as a dotted line next to the castle.

## v2 (combat framing tweak)
The combat camera pans 32 units sideways (`HQ_PAN=32`), so the castle and yard sit left of centre: the boom, trolley, container and tracks fill the gap between the wheels, and the castle sits partly behind the player wheel. Files: `combat_meridian_v2.jpg`, `combat_meridian_motion_v2.gif` (2.4 MB) and `combat_meridian_motion_strip_v2.jpg`; v1 files kept. Build: `HQ_PAN=32 render anim`, then `python make_motion30_v2.py`.
