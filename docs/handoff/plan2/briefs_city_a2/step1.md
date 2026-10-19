# CITY-A2 step 1: the art-pass planner city format replaces the old lot-grid city layout

## Why
Designer ruling D3 (DECISIONS, grep "**D3:**"): the city moves to "the new procedural generation and new layout (option b, the
full planner city: coast, districts, terrain), not just a seeded version of today's layout". NA-12 r1-r3 (on w1-close) instead
seeded the OLD square lot grid and carved an A2-shaped bay into it. That is wrong. The designer asked (2026-10-19): "why are you
preserving the old city layout when the art-pass made a whole new city layout format for you?"

## Source (art-pass branch, read with `git -C D:/rc_art/art-pass show art-pass:<path>`, or from D:/rc_art/art-pass on disk)
`docs/concepts/city_planner/`: `city_A2.json`, README.md, design_A2_horseshoe_bay.md, scripts/design_a2.py, citymap2.py, run_a2.py,
geom.py, verify_a2.py, metrics.py. Never copy concept images into the repo; JSON and ported code are fine.

city_A2.json (schema v1, metres, origin = map center, +X east +Y north): meta, terrain (coastline, hills as Gaussians h*260 m),
defences, drowned_quarter, districts (7: Old City = Rebel Cell + 6 corps; polygons, colors), neighbourhoods (26), landmarks (40),
roads (53; class ring|motorway|truck|arterial|collector; polylines, tunnels, bridges), interchanges, rails (freight|commuter|metro),
stations, port, parks, plazas, cemeteries, markets, industry, informal_housing, airport, spaceport, undercity, checkpoints, ferries,
drone_corridors. The plan is hand-made (fixed coordinates; seeds only for the street textures).

## Base
Worktree starts at main: FIRST `git reset --hard w1-close` (NA-12 r1-r3, STREET-CAM, P1+P5). Commit on your branch only.

## Items
1. `docs/handoff/plan2/CITY_A2_PORT.md`: every consumer of today's layout (grep CityModel, CityGenerator, CityLayout,
   CityLayoutRecorder, NeonCity, city.json readers and writers, netrun_street_deriver / StreetRouteData, Site lots, key_locations,
   the bake cache key, IdCapture, city_view_3d, campaign save) -> what it reads now and what it will read from A2. The game-scale
   mapping (A2 metres -> BU / lots). How a campaign seed varies the city inside the A2 plan.
   DEFAULT (log under DECISIONS "Open questions for the designer", revisitable): every campaign uses A2's districts, coast, terrain,
   roads, rails and landmarks; the seed varies block subdivision and building fill inside districts / neighbourhoods, which lots hold
   Sites and key locations, and the street textures. Corps sit in their A2 districts; Rebel Cell = Old City at the bay head.
2. Port: `content/city/city_A2.json` (vendored, source sha in a sidecar .md); a pure RefCounted `CityPlanA2` loader and validator
   (scripts/city3d/); a seeded block / lot subdivider turning A2 districts + roads into the lots and buildings CityModel needs
   (RngService stream passed in, IdSort, no global RNG). CityModel builds from it behind its current API so consumers keep working;
   the old grid generator stays only as a config fallback until step 2 removes it.
3. Tests: same seed -> byte-identical model export; each corp HQ inside its A2 district; every A2 road present; Sites on lots with
   buildings; 200-seed sweep under the config time budget; schema check in tools/schema_smoke_checks.gd (CLAUDE.md rule 8) +
   DECISIONS entry.
4. One capture: whole city seed 1 night beside art-pass `golden_plates/city_a2_night.png` -> `docs/art_review/PLAN2/CITY_A2_step1.jpg`
   (windowed only via `python tools/run_windowed.py`). Shape and placement, not look polish.

## Out of scope / don't edit
shaders/city/*, scripts/netrun_art/street_r2_*, scripts/ui/route_rig.gd (P2 step 2 and P6 agents), scripts/core/netrun_session.gd
(WH-11 agent).

## Hand back
RESULT block: commit sha, port doc, consumers changed, defaults taken, what step 2 must do. Stop at 60 % context with
docs/handoff/STATE_city_a2.md and status HANDOFF.
