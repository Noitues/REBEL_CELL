# Combat backdrop v3.1: placed clutter, sign fix, real props (art-pass, overnight)

Follow-up to v3. v2/ and v3/ untouched. Scratch `D:/rc_scratch/cutaway_kit_v3_1/`. Scripts in `scripts/` (copy of v3 with edits); `run_all.sh` renders + posts all 7 rooms (about 9 min). Files: `room_<n>.png`, `room_<n>_bare.png`, `squint_<n>.png` (bio, srv, gh, rec, lobby, event, shop), `sheet.jpg`, `v3_vs_v3_1.jpg`, `stats.json`.

## Changes
1. Sign bug fixed everywhere (`bl_scene.sign`): the dark backing of right-facing signs now sits behind the plane for all rooms (was shop only). `solace_v` now reads on the building. The last letter is hidden by the right-hand neighbour roof ("SOLAC"), that is geometry, not the bug.
2. Clutter is staged (`kit_gen._phase_b`, same seeds, same v2 base layout, deterministic):
   - B1 two real extra props per room; B2 hard-prop fill toward 0.50 (cap 3 big / 5 small);
   - B3 floor cables: 2-3 routed runs (Dijkstra with turn penalty, max 12 cells) hero -> powered prop -> next prop, drawn as conduit with a lit strip and plugs at both prop edges (`kit_lib.draw_cable`). Runs may cross the door aisle (flat, no occupancy, not counted); cells they take elsewhere count as clutter;
   - B4 crates / crate stacks / boxes beside the door, just outside the 3-cell aisle, against the back wall;
   - B5 barrels in corners (back corners first; lobby and event use box piles instead of barrels);
   - B6 box/crate piles against walls and against existing props up to the density goal;
   - B7 2-4 puddles on street-side cells (front/right cut edges, y<=2 or x>=6).
   Rule 7 enforced for everything; the old random `cable_run` prop is no longer used.
3. Real props added (non-clutter, 2 per type, counted as hard): bio fume_hood, sample_fridge; srv patch_panel, kvm_cart; gh potting_bench, water_tank; rec filing_row, water_cooler; lobby info_wall, turnstile; event speaker_stack, lectern; shop mannequin, checkout. They also join the B2 fill pool. Placed in this seed: see table.

## Fill (cells / 63; hard = without clutter and cables)
| Room | seed | v3 fill | v3 hard | v3.1 fill | v3.1 hard | clutter props | cables (new cells) | puddles | extras placed |
|---|---|---|---|---|---|---|---|---|---|
| bio | 11 | 0.54 | 0.43 | 0.62 | 0.49 | 6 | 3 (2) | 2 | sample_fridge |
| srv | 23 | 0.63 | 0.41 | 0.67 | 0.48 | 6 | 2 (6) | 3 | kvm_cart |
| gh | 37 | 0.68 | 0.40 | 0.68 | 0.46 | 9 | 2 (5) | 4 | potting_bench, water_tank |
| rec | 41 | 0.59 | 0.38 | 0.59 | 0.43 | 9 | 2 (1) | 3 | water_cooler |
| lobby | 53 | 0.63 | 0.35 | 0.68 | 0.49 | 6 | 3 (6) | 2 | info_wall, turnstile |
| event | 67 | 0.59 | 0.44 | 0.70 | 0.49 | 6 | 2 (7) | 3 | speaker_stack, lectern |
| shop | 71 | 0.62 | 0.49 | 0.67 | 0.51 | 6 | 3 (4) | 4 | mannequin, checkout |
All inside 0.50-0.70. Event sits at the ceiling (0.70) because the dressing minimum (6 cells beyond hard) overrides a low seeded target; the total goal is max(seeded target, hard + 6) capped at 0.70.

## Squint (composite over E10 board)
| Room | mean | p95 | loud >0.38 | v3 loud | post v_in |
|---|---|---|---|---|---|
| bio | 0.245 | 0.497 | 13.2 % | 12.3 | 0.84 |
| srv | 0.249 | 0.503 | 13.6 % | 13.4 | 0.84 |
| gh | 0.244 | 0.483 | 12.9 % | 12.3 | 0.80 |
| rec | 0.247 | 0.499 | 13.6 % | 13.8 | 0.76 |
| lobby | 0.244 | 0.500 | 12.3 % | 11.0 | 0.84 |
| event | 0.239 | 0.433 | 11.0 % | 11.4 | 0.84 |
| shop | 0.255 | 0.524 | 15.3 % | 13.6 | 0.76 |
Baseline backdrop 0.28 / 0.44 / 14.5 %. Rec first rendered 16.3 % loud (amber cable and extras), gh 14.7 %; both re-posted with a lower `v_in` (render unchanged). Shop is 0.8 points over the old baseline even at v_in 0.76; it is the loudest and would take `v_in` ~0.70 or a dimmer lime to match.

## Choices
- Cables count in fill (they occupy cells) but are reported separately; hard fill excludes clutter and cables.
- Hard-fill goal 0.50 is attempted for every room; reaching it is limited by the dense v2 base layout (kept unchanged for comparability), so 5 of 7 rooms stop at 0.43-0.49. Only shop reaches 0.51 (event/lobby/bio 0.49).
- Cables are allowed over the door aisle (flat decor); crates, boxes and barrels never enter it.
- Shop post uses v_in 0.76 and zroom 0.62 as in v3.

## Gaps
- Hard fill below 0.50 in 6 of 7 rooms (0.43-0.49); only a wider prop set or a different base layout would close it.
- Only 1 of 2 extras fit in bio (fume_hood missing), srv (patch_panel missing) and rec (filing_row missing): the wall band of the packed v2 layout had no free 2-3 cell slot. The others placed 2 of 2.
- Cables are short in some rooms (rec: 1 new cell, mostly across the aisle) because the v2 layout leaves few connected free cells; they read as stubs there.
- Cables, crates and puddles were checked on the sheet only at 1/2 scale; no close-up review of every junction plug.
- Shop and event not tested in a real netrun street graph; facade, ink wobble, rain, vehicles gaps from v2 unchanged. `kit_sheet.jpg` was not regenerated (new props/cables not on the kit sheet).
