# Round 31: Meridian combat view facing the boom

The castle model is the same as round 30. Earlier rounds are untouched, nothing is committed, and `scratch/` is cleared.

## What changed
- **Camera.** It now looks from behind the loading track (world +Y), facing the crane boom: camera at (0, 150, 60), aimed at (0, 22, 15). The crane's portal and A-frame sit in the centre, in the gap between the wheels, and the boom points toward the viewer. The track runs left to right in front of the fortress.
- **View corridor.** The buildings between this camera and the castle are cleared (`citydata.CAM_DIR["meridian"]` set to the new direction).
- **The loop** (20 frames, 150 ms each; `scripts/heroes31.py`):
  1. **f15–f3:** a train pulls in from the left and slows down.
  2. **f4–f9:** the train stands, and the crane lowers its container onto the empty flatcar.
  3. **f10–f14:** the train accelerates off to the right, with light and colour streaks trailing it and smeared ghosts of the locomotive. Meanwhile the trolley returns to the yard.
  4. **f15–f19:** the trolley carries the next container out, and the next train arrives.

## Files
- `combat_meridian.jpg`: the still, at frame 6 (train stopped, container coming down).
- `combat_meridian_motion.gif`: with the HUD, 960×540, 3.7 MB.
- `meridian_backdrop_motion.gif`: no HUD, 880×495, 1.1 MB.
- `combat_meridian_motion_strip.jpg`: key frames, with and without the HUD.
- `hq_meridian_close_night.jpg`, `hq_meridian_close_day.jpg`

## Build (from `scripts/`)
1. `python citydata.py`
2. Render the close-up and the animation frames:
   - `blender -b --factory-startup --python hq_scene.py -- meridian_hq ../scratch/bl close`
   - the same command with `anim` in place of `close`
3. Wheels: `wheels_r18/render_bosses24.py meridian`, `wheels_r18/dump_boss_slots24.py`, `combat_r23/render_player24.py`
4. `python make_motion31.py`

The backdrop gif was re-quantised to 880 px with one shared palette to stay under 4 MB.

## Open
- **The departing train leaves the frame in about 2 frames.** The streaks carry the speed, so the track is empty for frames 12–14.
- **The city map still shows the round 30 view corridor.** Re-run `city_hq_v6.py` with these scripts if the map should match this camera exactly.
