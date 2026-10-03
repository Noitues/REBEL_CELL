# Round 29: a lower Meridian fortress with a moat and a crane keep

The fortress uses texture A from round 28 (raw corrugated steel, unified Meridian orange). Earlier rounds are untouched, nothing is committed, and `scratch/` is cleared.

## Changes (`scripts/heroes29.py`)
1. **Lower and wider.**
   - The curtain walls are 2 containers high (were 4).
   - The corner towers are 4 courses high (were 7) and wider (11 instead of 10 units across).
   - The gatehouse is 3 courses high, and the fortress is more compact (half-width 18 instead of 21).
2. **A moat** surrounds the whole fortress:
   - dark water with stone kerbs and lit amber edges, plus ripple lines;
   - broken vertical reflection streaks of the lit towers and gate on the front water;
   - the container drawbridge spans the moat at the gate.
3. **A ship-to-shore gantry crane is the keep.** It replaces the office tower:
   - four heavy lit legs on bogies, portal and sill beams with bracing;
   - a machinery house with the MERIDIAN sign, and an A-frame with red beacons;
   - twin hazard-striped boom girders, a backreach with a counterweight, and tie rods;
   - a trolley with a downlight, cables, a yellow spreader, and a container.

   It stands **side-on** to the gate camera (the boom runs across the view), so the camera sees the classic crane silhouette.

## Options (`castle_v29_options.png`)
- **A: boom lowered across the wall (recommended).** The boom runs over the east wall, with the spreader and container held above the moat. It reads wide and grounded, and the crane plainly is the keep.
- **B: boom raised to 72°.** A taller landmark, but the boom leaves the top of the frame and crowds the HUD.

## Recommended (A)
- `combat_meridian.jpg`
- `hq_meridian_close_night.jpg`, `hq_meridian_close_day.jpg`
- `hq_meridian_city.jpg`

The map crop is round 27's crop with A's map sprite composited at the HQ position. The full city map has not been re-rendered.

## Build (from `scripts/`)
1. `python citydata.py`
2. `render_all29.ps1`
3. `python make_round29.py`
4. `wheels_r18/render_bosses24.py meridian`, `wheels_r18/dump_boss_slots24.py`, `combat_r23/render_player24.py`, `combat_r23/make_combat27.py meridian`

## Fix
`hq_scene.build_at()` now really rotates the geometry. Before this, `rot` only turned the sign objects, which affected the rotated Sites in rounds 26–27.

## Open
- **In combat, the wheels cover the boom ends and the container.** The A-frame and portal stay visible in the centre gap.
- **On the map crop, a sliver of round 27's taller castle may show behind the new, lower sprite.** A full `city_hq_v5` re-render fixes it.
