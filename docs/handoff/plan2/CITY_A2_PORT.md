# CITY-A2 port: the art-pass planner city replaces the old lot-grid city

Designer ruling D3 (DECISIONS `**D3:**`, follow-up 2026-10-19): the city is the full planner city A2 (coast,
districts, terrain), not a seeded copy of the old square grid. Step 1 (this branch) ports the format and builds the
game's city from it behind today's APIs; step 2 removes the old generator and makes the views read the rest of A2.
DECISIONS entry: "2026-10-19 - CITY-A2 step 1".

## Sources (art-pass, A-039)
- Data: `docs/concepts/city_planner/city_A2.json` @ 3a9cbc7f (nothing newer than 9866af3c), rules in
  `design_A2_horseshoe_bay.md`. Vendored to `content/city/city_A2.json` (sidecar `city_A2.source.md`).
- Look plates `city_a2_*`: `city_all_corps/` (NOTES.md + scripts). Landmark modules: `city_all_corps/` @ 77cdfde9
  (ENTRIES.json + 6 landmark .glb; ours under `assets/city/landmarks/` hold 5 corps: check they match). Aurelian arcade
  in the city model @ 6d214ce9.

## Game-scale mapping
- A2 is metres, origin = map centre, +X east, +Y north; the game is lots (6 BU each), +i east, +j south.
- `lot = city_rect.centre + (x_m, -y_m) / city_a2_metres_per_lot`, `city_a2_metres_per_lot` = 121.212 (A2's 20 km
  extent over the 165-lot `city_rect`). Hills: sigma / 121.212 lots, height_m x (lot_bu / 121.212) BU (247 m -> 12 BU),
  rotation negated (plan y = -j).
- Raster (`CityA2Raster`, seed-independent, built once): city rect grown by `city_a2_raster_margin`; water = ocean
  polygon + lakes + rivers of `city_a2_river_kinds` (canals are not water); district / territory per lot
  (`city_a2_territories`: centre -> rebel_cell, the four game corps by id; Aurelian, Tethys -> Sprawl until their
  content exists); road class per lot (4-connected strokes, at least `city_a2_road_half_min` half width); parks; signed
  shore depth (BFS); territory runner-up and border share (NeonCity's `_territory_pair` form, BORDER_BLEND lots).

## How a campaign seed varies the city (DEFAULT, logged as an open question)
Every campaign uses A2's districts, coast, terrain, roads (and later rails / landmarks); the Old City (Rebel Cell) sits
at the bay head, each corp in its A2 district. The city seed varies, on stream `city_layout` (CityA2Builder.make_plan):
each HQ rect (within `city_a2_hq_jitter` of A2's HQ, whole rect on land in its own district, `city_gen_edge_lots` in,
`city_a2_hq_gap` apart; then the A2 spot, then the nearest fit), the Cell's spot near the Old City centre, each Site
layout's heading and mirror (Sites `city_gen_coast_clear` off the water and off other HQs; score +1 own district, -1 on
an A2 road or park). On stream `city_blocks` (CityA2Builder.lots_for): each district's local street spacing
(`city_a2_block_lots` 4-7) and phase, lot merges, building heights (by neighbourhood kind / corp / old core / sprawl,
rising near corp HQs), tapers, setbacks, inks. Fixed: every district border is a street on both sides (district grids
meet there, one network); local streets run through parks and bridge rivers; a Site in a park gets the 3x3 park lots
round it built on.

## Consumers: what they read now and from A2
| Consumer | Reads now (step 1) | Step 2 |
|---|---|---|
| `CityPlan` (`for_seed`, `current`, `hq_rects`, `hq_of`, `is_water`, `land_depth`, `shoreline`, `sea_cells`, `city_sections`, `to_dict`) | Generated seeds: `CityPlan.generate` -> `CityA2Builder.make_plan` (`plan.a2` = raster; `coast` = {side, a2}). Fixed seed 7: unchanged fixed city. `&"grid"` config: NA-12 `generate_grid`. | Drop `generate_grid`, the parametric coast (`shore_at`, `edge_point`, `coast` waves) and decide the fixed seed (goldens) |
| `CityGenerator` | Only behind `city_layout_source = &"grid"`; `site_points_at` is reused by A2 | Remove (keep `site_points_at` / `site_box` in a small helper) |
| `CityLayoutRecorder` (extends NeonCity) | A2 plan: `_record_a2` copies the seed's subdivision in the same draw order and record forms; no NeonCity placement runs | Becomes a pure recorder of A2 lots (no NeonCity base) |
| `CityModel` (`build`, `shared`, async build in `CityView3D._start_model`, `CombatBackdrop._extend_city`, `CityDistrict`) | Unchanged code: chunks of recorder output (A2 for generated seeds); HQ stand-ins from `hqs`; layout rules (NA-11) on top | Prisms straight from `CityA2Builder` (no Node recorder; workers no longer instance NeonCity) |
| `NeonCity` (2D painter: grid map, minimap, backdrops, bake cache) | Territories from A2 districts via `CityPlan.territory_pair` (one-line hook in `_territory_pair`), water from A2; its own grid streets and buildings still drawn (do not match the 3D A2 lots) | Paint A2 lots / roads (or retire the 2D painter where the 3D city covers it) |
| `CityBakeCache` key | `[city_seed, district, look...]`: in-process cache, layout source is a per-process config, so no stale entry | Add the layout source / A2 sha if bakes ever persist |
| `city.json` writers (`NetrunArtExport.city_json`, `export_runner`, `StreetRouteData`) | From the model (A2 lots, streets, plazas, HQs) + `city_sections` (A2 shoreline / sea cells / hills) | Optional v1 sections: districts, roads by class, rails |
| `netrun_street_deriver` / `StreetRouteData` / `NetrunArtLayout.route_on_streets` | city.json streets: A2 roads + local grids (one network, test_city_a2 full-city routes) | Use A2 road classes for lane widths |
| Site lots / `CityLayout.site_points_in` / `CityLayoutRuler` | Plan's A2 HQ + seeded heading; Sites have a building within `art_site_bid_reach_lots` | Snap Sites to A2 neighbourhoods? |
| `key_locations.json` (`NetrunArtExport.key_locations_json`) | Site points + building index from the A2 model | none |
| `IdCapture`, `city_view_3d` picking, `CityWater` | Model / plan as above; `CityWater` runs along `coast.side` (A2: the side with most sea lots, south) and uses `land_depth` | Water mesh from the A2 ocean polygon; rivers; drowned quarter |
| `CityLandmarks` / HQ compounds | `model.hqs` (A2-placed HQ rects) | Place from A2 `landmarks` + art-pass ENTRIES.json footprints |
| Campaign save | `city_seed` only (u64 string): format unchanged; a resumed campaign regenerates its city as A2 | none |

## Not read yet (step 2)
Rails, stations, port, interchanges, airport, spaceport, undercity, checkpoints, ferries, drone corridors,
defences, drowned quarter, district walls / gates, landmarks; tunnels are drawn at the surface.

## Step 2 must
1. Remove the grid generator (`CityGenerator` attempts, `city_gen_*` coast / ring numbers, `generate_grid`,
   `city_layout_source`) and its tests (`test_city_generator*` now exercise A2 through `CityPlan.generate`).
2. Build prisms without the NeonCity recorder; make the 2D painter (or its replacements) draw A2.
3. Rails, landmarks (ENTRIES.json), walls / gates, port, tunnels, the drowned quarter, Aurelian / Tethys when content
   exists.
4. Street frontage height (A-039 finding): on the old city the netrun street frontage came out low (median top 15 BU
   vs 24 on art-pass's street, r2_rules.layout_pass). The A2 lots must let the street frontage reach r2 layout_pass
   heights: check `city_a2_heights` / HQ rise against layout_pass on the A2 city (the layout rules still run on top).
5. Decide whether the fixed seed (7) also becomes A2 (re-pin goldens and fixtures).

## Tests
`tests/unit/test_city_a2.gd` (fast): file validates, A2 source, byte-identical plan and city.json after a rebuild,
two seeds differ in one plan, HQ rects inside their A2 districts and equal to the model's, every A2 road on the
streets, plan and full-city problems clean, no global RNG. `tests/unit/test_city_a2_sweep.gd` (full): 200 seeds, 95th percentile (best of two) under
`city_a2_budget_s`, no fallback, clean plans, HQs in districts, Sites with buildings; three full cities.
Probe: `godot --headless --path . res://tools/city/city_a2_probe.tscn -- <seed>` (ASCII map, counts, timing).
