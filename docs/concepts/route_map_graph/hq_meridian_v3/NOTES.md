# Meridian HQ v3: THE GATEHOUSE GANTRY (finals)

A goliath gantry crane built as a castle gatehouse over a container-walled freight yard. Two crenellated tower-legs ride
the E and W walls, a battlemented span joins them (underside 104 BU = 2.5x the wall), and the keep (the trolley) crowns
it with THE MASTER MANIFEST in an open lantern. A high-speed train runs on the N side, a 6-lane truck ring road with
queues surrounds the lot, rust-orange paint with sodium-white lit edges, everything inside the 240 x 240 lot. Design,
massing, ring-road exits (section 14.2) and rulings are in `DESIGN.md`.

## Finals (2560 x 1440, Cycles 64 spp)
`H_overview_v3.png`, `H_decision_v3.png`, `H_hover_v3.png` (plates without UI in `plates/`). Overview camera: yaw +35
(SW), pitch 38. Post exposure 2.85.

| shot | median (0.14 +-0.03) | under 0.10 (25-40 %) | over 0.85 (<= 2.5 %) |
|---|---|---|---|
| H_overview | 0.139 | 35.9 % | 1.8 % |
| H_decision | 0.175 | 25.3 % | 2.8 % |
| H_hover | 0.006 | 85 % | 2.0 % |

H_hover is the kit's power-cut look (everything not on the hovered branch is dimmed), not an exposure fault.
The landmark / local-background ratio was 2.2 on the overview test (2e).

## Rebuild (from `scripts/`)
- previews: `HQ_LOCK_HELD=1 python hq_test.py H_overview,H_hover eevee` (no GPU lock)
- finals: `python locked.py finals -- python hq_jobs.py stills final all` (takes the GPU lock), then
  `python hq_compose.py stills all`; passes go to `D:\rc_scratch\meridian_v3`.
- re-post only (no GPU): `python hq_compose.py stills all`. Needs `scratch/emblems` (`python emblems20.py`).

## City hook
`scripts/meridian_landmark.py` has `build(ctx)` for `city_preset.LANDMARK_MODULES["meridian"]`: it returns
`dict(label, crown, hue)`, scales the kit by 0.2375 around `ctx.hq`, writes into SURF / NEON / GLASS and adds
`ctx.spot_at` lights (the HQ's area and point lights become downward spots; the rim lights are dropped). Rooms and the
rail are off (the city has its own). Checked with a fake ctx (`scratch/test_city_ctx.py`, plain python): about 11.6k
solid, 2.5k emissive faces, 41 spots, extent about +-28.5 BU around the lot centre, top 42.7 BU. Not yet run inside the
real city build. Emission strength mapping (`_CITY_EMIT_K`) and the spot powers will need tuning by eye there.
