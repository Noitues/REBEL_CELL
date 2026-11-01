# Combat backdrop v3: Cutaway kit, missing rooms + density fix (art-pass, overnight, 2026-10-31)

Art only, REBEL_CELL Solace slice. Same pipeline, camera, grade and lime as v2 (`../v2/NOTES.md`). v2 folder untouched. The E10 board (`D:/rc_tmp/combat_critic/plates/waves_e10/p1_decide.png`) is untouched; composites use post.py's board composite step (bd_common.compose). Scratch: `D:/rc_scratch/cutaway_kit_v3/`.

## Files
- `room_<type>.png`, `room_<type>_bare.png`, `squint_<type>.png` for bio, srv, gh, rec, lobby, event, shop.
- `sheet.jpg` (all composites + squints), `v2_vs_v3_density.jpg` (v2 vs v3 crops for bio/srv/gh + fill bars), `kit_sheet.jpg` (updated: clutter, event and shop props, 7 layout grids), `stats.json`.
- `scripts/`: updated copies. `run_all.sh` (render + post all rooms), `render_room.sh <type> <seed> <name>`, `post.py <name> [v_out] [zroom] [v_in]`, `sheet_v3.py`.

## Changes vs v2
1. **Rooms rendered**: records/office (`rec`) and lobby/reception (`lobby`) as top-floor rooms.
2. **Density fix** (`kit_gen.generate`): the v2 layout is kept unchanged (verified: v3 props start with the identical v2 prop list for bio/srv/gh), then a second fill phase continues until the seeded density target: (a) variety cap loosened to 3 big / 5 small, (b) floor clutter on any free cell: crate, crate_stack, barrel, cable_run (2x1 low), box_small. Rule 7 (only <= 1.2 m props on cut-edge cells y<2 or x>=7) is enforced for everything; all clutter is <= 1.2 m. Plus 2-4 puddle decals per room (floor-only, no occupancy, NOT counted in fill). Lobby density target raised to 0.50-0.64 (was 0.28-0.42) so all five Site rooms land in the same band. The lobby layer drawn under the room still uses the v2 generator (`v2=True`), unchanged look.
3. **Netrun street proposals** (art proposals, not Site rooms, no game objects mapped): `event_room` (back-room clinic/meeting: windowless, violet light, wall screens, hero holo table, exam bed, privacy screens, folding chairs, med cabinet, IV stand, scanner arch, trestle) and `shop` (street-level storefront: room floor on the pavement at z 0.62, no lobby below, front and right edges open onto the street, back-wall SUNDRIES sign, blade sign on the kerb, bollards and A-frame, hero display island, counter, shelf units, gondola, cooler, vending, crate display, basket rack). Same 9x7 grid, same shell modules, same cut-edge language.

## Seeds and fill (cells / 63; "hard" = without clutter)
| Room | type | seed | v2 fill | v3 fill | v3 hard | clutter props | props total |
|---|---|---|---|---|---|---|---|
| bio-lab | bio_lab | 11 | 0.41 | 0.54 | 0.43 | 4 | 20 |
| server room | server_room | 23 | 0.38 | 0.63 | 0.41 | 11 | 26 |
| greenhouse | greenhouse | 37 | 0.32 | 0.68 | 0.40 | 13 | 30 |
| records/office | records_office | 41 | 0.33* | 0.59 | 0.38 | 13 | 29 |
| lobby/reception | lobby | 53 | 0.32* | 0.63 | 0.35 | 14 | 28 |
| event room | event_room | 67 | n/a | 0.59 | 0.44 | 6 | 22 |
| shop | shop | 71 | n/a | 0.62 | 0.49 | 8 | 27 |
*v2 generator run with the same seed (the room was not rendered in v2). All seven are inside 0.50-0.70. Honest read: the loosened cap alone only reaches about 0.35-0.49 "hard"; most of the gain is clutter, and the hard-prop fill of srv/gh/rec/lobby is still below 0.50.

## Squint table (1/16 + blur, composite over the E10 board, visible backdrop only)
| Room | mean | p95 | loud >0.38 |
|---|---|---|---|
| bio | 0.243 | 0.490 | 12.3 % |
| srv | 0.249 | 0.488 | 13.4 % |
| gh | 0.245 | 0.479 | 12.3 % |
| rec | 0.253 | 0.518 | 13.8 % |
| lobby | 0.241 | 0.506 | 11.0 % |
| event | 0.242 | 0.441 | 11.4 % |
| shop | 0.250 | 0.527 | 13.6 % |
v2 for reference (bio/srv/gh): 0.24 / 0.48 / 10.9 %, 0.24 / 0.49 / 11.5 %, 0.24 / 0.44 / 9.8 %. Baseline old backdrop: 0.28 / 0.44 / 14.5 %. Dense props raise loud share by 1.5-2 points; all seven stay under the old baseline and the board still reads first. Rec (amber) and shop are the loudest; if the board needs air, lower `v_out` (or `v_in`) in post.py.

## Choices made (designer asleep)
- Counted clutter in fill (physical objects on cells) but not puddles; both numbers reported.
- Kept v2 layouts as the base so before/after is a pure addition; bio gains the least (4 clutter) because its v2 fill was already 0.41.
- Seeds for new rooms: 41 (records), 53 (lobby), 67 (event), 71 (shop); picked arbitrarily, first try, not cherry-picked.
- Event room light = violet (new; keeps it apart from lime/cyan/amber). Shop light = corp lime (a paler white-green first try rendered p95 0.60 / loud 15.7 %, too hot).
- Shop is rendered with post `v_in` 0.76 (others 0.84) and `zroom` 0.62; its grade focus hull follows the lower room. Its first right-hand neighbour is replaced by a low (1.8 m) kiosk strip, since the 3.6 m shop would hide the room at street level and dropping it left empty sky.
- Shop blade sign sits out on the kerb at 2.5 m tall so it hides no floor cell.

## Gaps / what did not work
- v2 bug found, left as is for comparability: the dark backing box of `right`-facing signs sits in front of the sign plane, so `solace_v` on the building is a black slab in all v2 renders and in v3 bio/srv/gh/rec/lobby/event. Fixed only for the ground shop (`sign()` offset under `GROUND`). One-line fix in bl_scene.py if wanted everywhere (it changes the right edge of every building render).
- Clutter is placed randomly; it reads as scattered rather than staged (no cable runs that connect racks, no crates by a door). The hard-prop fill is still under 0.50 for 4 of the 7 rooms; reaching it by props alone needs more variety per room type.
- Event room and shop have not been viewed in context of an actual netrun street graph; the shop's neighbours and the street come from the existing slice, so the shop reads small in frame (its floor is lower, more street visible). The rooms have no people, as in v2.
- Facade, ink wobble, rain and vehicles gaps from v2 are unchanged.
- Process: I accidentally launched a `python -` command once early on (it hung and was stopped by the harness); an idle python process from it may still exist (my own, not Blender). I could not kill it (permission denied), so it needs a manual kill if it is still there.
