# REBEL_CELL city generation: evaluation and missing rules

Date 2026-10-29. Read-only research. Sources: game repo `D:/Godot/rebel_cell` (main), art view `art/tide-r35` (a168aa7c) of `D:/rc_art/godot_look_tide` (copy of `city_view_3d.gd` read at `D:/rc_scratch/cv3d_r35.gd`), `docs/concepts/city_planner/`, MAILBOX A-104 to A-109, renders `G1_parity/r35/compare_r34_r35.jpg` and the designer's `r14_red_boxes.webp`.
No Godot was run. Anything that would need a run is marked **unverified**. Pixel regions are in the original image pixel space of the 1920x2160 contact sheet (displayed coordinates x 1.08).

Headline: the planner is a hand-drawn macro plan (coast, districts, 53 roads, 12 rails, 15 parks, 21 interchanges) rasterised onto a 121 m lot grid. Everything finer than that is **a uniform random street grid and independent random heights, with no cross-checks between layers**. The view then fixes collisions one at a time by hiding buildings. That is exactly the setup that produces "silly mistakes when zoomed in".

---

## 1. How the city is generated today

Scale: `city_a2_metres_per_lot = 121.212` (campaign_config.tres:503). One lot = 121 m. Local blocks are 4-7 lots (`city_a2_block_lots`, tres:518) = 485-850 m. Real blocks are 80-200 m. So the "street grid" is already a super-grid and each lot is a whole building.

| # | Stage | Where | Owner | What it does |
|---|---|---|---|---|
| 1 | Plan data | `content/city/city_A2.json`, loaded by `CityPlanA2` (`city_plan_a2.gd:79-203`) | layout (hand-authored, art-pass origin) | Fixed coordinates in metres. Seeds never change it. Validation (`validate`, :96-148) checks only schema: 7 districts, ocean polygon, road ids and classes. No geometric validation at all: nothing checks that rails miss lots, roads end on land, parks are not crossed. |
| 2 | Raster | `CityA2Raster.make` (`city_a2_raster.gd:43-113`) | layout | Ocean/lake/river polygons to `water` (1 = sea, 2 = river, :60-68); districts to lot ids (:77-84); parks (:85); roads stroked as discs of half-width `max(width/2/mpl, 0.5)` lots (:87-97, `_stroke` :213-239), so every road is >= 1 lot wide and 4-connected; neighbourhood kinds (:98-111). Shore depth by BFS (`_depths` :244-279). **Rails, walls, interchanges, stations, port, undercity are not rasterised** (grep: no `rails`/`walls`/`interchange` in raster, builder or `city_plan.gd`). |
| 3 | Terrain | `CityA2Terrain` (`city_a2_terrain.gd:51-427`) | layout | Gaussian hills, foothills/mountains rising past the outer ring `road_001`, value noise from a fixed `city_a2_terrain_seed`, beach falloff. Seed-independent. Used for the `_bare` test and for where decks stand. |
| 4 | HQ and Site placement | `CityA2Builder.make_plan` (:80-132), `_place_hq` (:162-185), `_hq_ok` (:190-200), `_aim` (:208-238) | layout | HQ rect jittered +-4 lots around the A2 HQ point, all lots land and in own district, 1 lot gap. Site heading by seeded shuffle + score; a Site on a road or park only costs -1 (:233), so Sites can sit on roads/parks and the building "stands next to it". |
| 5 | Lot kinds | `_subdivide` (:296-505) | layout | In order: HQ plazas (:309-317); A2 road class lots become K_STREET (:323-326); water; park; open-sprawl K_BARE (:331-335). |
| 6 | Local street grid | `_subdivide` :338-358 | layout | **One rectangular grid per A2 district**: spacing sx, sy and phase drawn from the seeded stream (:339-342); any ground/park/river lot on a grid line or on a district border becomes K_STREET. Comment at :343 says it outright: "They run through parks and bridge rivers". No hierarchy, no connectivity test, no check against coast, highways, rails. |
| 7 | Highways | A2 `ring/motorway/truck` lots are K_STREET; `city_a2_corridor` (tres:598, 1 lot each class) clears K_GROUND within 1 lot to K_BARE (builder :398-409) | layout | The elevated look itself is view-side (stage 13). The corridor is the only land-use rule tied to highways, and it only clears K_GROUND, not K_PARK or streets. |
| 8 | Coast setback | builder :410-436 | layout | K_GROUND within 2 lots of sea becomes K_BARE, **except lots beside a street** (:421-424, "A street's frontage stays"). Rivers excluded (:428). |
| 9 | Street pruning | builder :437-461 | layout | A rank-0 local street with no K_GROUND within 1 lot becomes K_BARE and is erased from `streets`. Only a 1-lot radius, run once, no iterate; leaves stubs and dead ends. |
| 10 | Buildings, heights | builder :462-505, `_extrusions` :600-667, `_height_kind` :579-596, config `city_a2_heights` (tres:521-533) | layout | Each remaining K_GROUND lot, row order, may merge east/south (35% in code default, 10% in tres:519). Height = `lerp(lo, hi, u^pow)` with `u = rng.randf()` per cell (:607): **independent per building, no spatial coherence**. Spike 6% x1.9 (:611), HQ rise up to x2.2 within 18 lots (:626), sunk blocks in the drowned quarter. Setback tier over 18 BU. |
| 11 | Solace re-lay | `CitySolaceDistrict.apply` (`city_solace_district.gd:23`) | layout | The whole Solace territory is thrown away and re-laid as a park plus 2-3 lot blocks in a lawn lattice. A **second, different generator** for one district. |
| 12 | Layout rules | `CityLayoutRuler.apply` (`city_layout_ruler.gd:11`) | layout/netrun | NA-11 frontage rules (>= 6 floors on border streets) re-edit prism heights for the Netrun. Third height pass on top of 10 and 11. |
| 13 | A2 features | `CityA2Features.build` (`city_a2_features.gd:45-67`; tide-r35 `_roads` :299, `_rails` :478, `_walls` :517) | art view (originally layout, now art-owned) | Decks drawn from **A2 polylines in metres**, not from the lot raster: highways/rails as lifted quads with pillars, tunnels skipped, stations as boxes, walls (now drawn as highways, A-109). Fully independent of where lots are. |
| 14 | Interchanges | `CityInterchangeKit.crossings/ramps` (tide-r35, `city_interchange_kit.gd:15,116`) | art view | Ignores the plan's own `interchanges` (21 in the JSON) and invents ramps at every highway/highway crossing by geometry. |
| 15 | Shapes, colour | `CityShapeKit.pick` (:33), `CityCorpColor.weights/prepare` (:23,:56) | art view | Seeded per-building shape; colour is a weighted random pick per building across all corps, capped at `corp_max_share`, so corp colour is salt-and-pepper, not a district identity. |
| 16 | Neon | `CityNeonKit.hotspots` (:28), `avenue_strips` (:574), `audit` (:723), `audit_avenues` (:651) | art view | Hotspots at busy intersections, glowing avenue strips on straight street lots with >= 2 built neighbours (excluding highway zone, rivers). |
| 17 | Lamps | `CityLampPlan.lamps` (:28), `highway_zone` (:105), `audit`, `audit_rails` | art view | Lamps only on street lots with a building beside them. Good rule, implemented as dressing. |
| 18 | View hiding | `CityView3D._build_wall_skip` (`D:/rc_scratch/cv3d_r35.gd:1711-1721`), `pocket_lots` (:1704, skip at :2232), `_in_cleared` (:2569), `in_view_cut` | art view | Hides buildings under the rail and wall routes, Solace pocket lots, HQ compound footprints. |
| 19 | Traffic | `CityTraffic` sky lanes (`city_traffic.gd:20-51`: over the busiest avenue lines), deck streaks (`city_a2_features.gd` tide-r35 `_traffic` :417) | art view | Sky lanes follow lot-avenue lines; deck traffic follows deck polylines. |
| 20 | Water, parks | `CityWater` (781 lines), `CityParkKit.mesh` (:41) | art view | Parks are K_PARK lots with lawn plus tree clumps; the park read depends on K_PARK lots being contiguous. |

Existing automated checks are all in the view branch, and all per-feature: `CityNeonKit.audit/audit_avenues`, `CityLampPlan.audit/audit_rails`, `CitySolacePockets.audit`, `CityA2Features.wall_clash`. I found **no layout-level audit** in the game repo (a `tests/` name search for city/a2/layout in the main repo returned no matches; unverified beyond that search).

---

## 2. Failure catalogue

Legend: [L] layout/build owner, [V] art view, [A-n] already asked, [R] already ruled in DIRECTION_REVIEW.

### 2a. Layout logic

| # | Defect | Evidence | Root cause |
|---|---|---|---|
| L1 | **Streets run straight into the bay / along the shore.** Street lots end at water edges as dead stubs, and a street can hug the coast. | r35 bay close-up (compare sheet, left of second row): the dark road at about (240-330, 880-960) in the left panel, ends in blue; many grid lines end at the bay at (650-800, 870-1000). Also the shoreline "slab" at the top left. **[A-108.3] asked.** | Grid lines painted on any K_GROUND (builder :345-358) with no look at water. The coast setback explicitly keeps street frontage (:421-424), so the setback never removes the street. No rule "street must end at a road, plaza or quay". |
| L2 | **Streets slice parks.** Parks read as fragments cut by grid lines. | Designer's red boxes (r14): lower right box, park with lines. In r35 the HQ park (Solace) is protected, but top-left parks (compare sheet, panel 1 around (150-420, 80-250)) show street grid cutting tree fields. **[A-108.2] / ruled.** | Builder :345-348 turns K_PARK into K_STREET on any grid line, by design. |
| L3 | **River infill voids.** Land within a few lots of the river is neither built, street nor park, leaving flat "slab" fields. | r34 panel 1 (centre-left, (480-700, 380-470)) dark empty land beside the river. **[A-108.1], [A-104].** | River lots excluded from coast setback (:428), but K_BARE rules (:331-335, :390-395, :398-409) still strip buildings around them; there is no fill rule. |
| L4 | **Wide bare slab between highway and bay with lone cubes on it.** Isolated 1-lot buildings stand in a grey field with no street or plot context. | r35 bay close-up (right panel), (60-560, 520-700) grey slab with 4-6 cubes and a rectangle cluster at (1000-1250, 760-860 in sheet coordinates of that panel). | Sprawl thinning (`_bare/_keep`, builder :513-541) uses a pure random per-lot chance, so survivors are isolated singletons. K_BARE then draws as bare asphalt-grey ground. No "cluster survivors", no vegetation or yard fill. |
| L5 | **Even field of towers in the dense core, no height rhythm.** | r35 plan: full-width tower field with no low-rise breaks; r35 seed 3 same. **[A-107].** | Height is one independent `randf` per lot (builder :607). Only HQ rise (:626) is spatial. No block-level height field, no low breaks. |
| L6 | **Height cliffs at district borders.** Corp-range heights (e.g. `corp_orbital` 16-42, `corp_meridian` 5-14) abut `old_core` 3.5-11 and `sprawl` 2.2-9 with a hard step along the territory border. | Seed-independent. Visible in r35 seed 3 where the dark tower mass meets the low blocks at about (520-600, 1100-1400). | `_height_kind` (:579-596) picks a kind per lot by territory; the only smoothing is the HQ rise. No blend across the `border` field that the raster already computes. |
| L7 | **Tower next to park with no transition.** 35-40 BU towers directly on the edge of the HQ park; low-rise stub next to a field of foliage. | r35 "HQ park edge" panel: towers abut lawn at (640-880, 1560-1900); designer red box 2 (r14) same. | No park frontage rule (setback, step-down, or street at the park edge). |
| L8 | **Random merged cells and orphaned lots.** A lot merged east/south can leave 1-lot dead-end K_BARE pockets, and street-less interior lots. | **Unverified** (needs a sweep): reasoned from :477-484 and prune :437-461. | Merge ignores whether it cuts street frontage; prune is one-pass. |
| L9 | **Street dead ends and grid mismatch at district borders.** Two district grids with different pitch meet on the border street (:350-356), so streets on one side end at the border and do not continue. | Plan view of r35, left-centre where district grids change. | Per-district independent `sx, sy, phase` (:339-342). Real cities continue arterials across districts and shift grids at wedges or arterials. |
| L10 | **Rails/walls/highways routed over lots, then patched.** | **[A-106]**, `_build_wall_skip` hides prisms. | Rails are never rasterised, so the builder cannot avoid them (see E1). |
| L11 | **Sites on roads/parks.** `_aim` only penalises -1 for a Site on a road or park lot (:233). A building stands next to a road or a park lot gets cleared to ground (:359-365). | Code only. **unverified visually.** | Soft score instead of constraint. |

### 2b. Element interaction

| # | Defect | Evidence | Root cause |
|---|---|---|---|
| E1 | **Rail decks and pillars pierce towers.** | **[A-106]**. Art skips lots (tide-r35 `_build_wall_skip` :1719-1720), so towers vanish under rails: gaps in tower rows. | Rails are not in the raster or builder. Highways at least get a corridor (:398-409); rails get nothing. View hides instead. |
| E2 | **Highway deck vs lot raster mismatch.** The deck is a smooth metre polyline; the "street" lot under it is a 4-connected staircase at least 1 lot (121 m) wide. Corridor of 1 lot is cleared on each side, but a deck 34 m wide diagonal to the grid shows building walls touching the pillar line where stair steps wander. | r35 plan: diagonal highway at (280-700, 250-900) with towers pushing right up to the pillars on the south-east side. | Two representations of the same road (`CityA2Raster._stroke` vs `CityA2Features._deck`) never reconciled; the corridor is measured in lots, not metres from the real polyline. |
| E3 | **Ramps and interchanges are invented by the view from crossings; the plan's own 21 `interchanges` are ignored.** Ramps can land on a building lot or park, and over the bay. | r35 bay close-up: the crossing at (1400-1560, 580-640) shows two decks and ramps landing on the slab with no connection into the ground street net. | `CityInterchangeKit.all_ramps` (art) vs `CityPlanA2.interchanges` (layout). The lot builder has no idea ramps exist (grep: no `interchange` in builder); ramps only get a lamp-zone treatment (`ramp_polylines`). |
| E4 | **Ground street grid is not connected to the elevated network.** No on/off ramps to ground streets; decks float over the grid, and local streets pass under them with no lot-level change. | r35 hotspot panel: deck at left (890-1040, 1000-1450) with avenue strips running right into the pillars at (900, 1330). | Only the ring/motorway/truck lots exist as ground "streets" with traffic rank (:323-326); nothing ties the lot street to the deck. |
| E5 | **Avenue strips cut across open ground and lawns.** The bright yellow/green strips in the hotspot panel run along bare lots with no buildings on one side, and end in the park. | r35 hotspot panel, (1300-1700, 1250-1420) yellow strip across bare slab; strip ends at the green HQ park (1780, 1300). | `avenue_strips` needs only >= 2 of 8 neighbours built plus `_open_run` bridging (neon :574-650). A strip's end is not tied to an intersection. |
| E6 | **Neon strips and street lots inside parks.** Strips and streets inside park polygons. | r34 panel 1 top-left cyan strips over the dark top-left parks, (700-850, 50-110). | Follows from L2. |
| E7 | **Traffic follows lot avenue lines, not roads.** Sky lanes (`city_traffic.gd:51` `avenue_lines`) run over the busiest avenue lines wherever those are, including across bays and river bridges, and across bare lots. **Unverified** on a render; derived from code. | Code. | Traffic keyed to the street raster, which is wrong at coast and parks (L1, L2). |
| E8 | **Lamps on frontage of streets that dead-end into water.** Lamp rule needs a building beside the lot, so partially safe. A lamp line stops where the building stops (a "lit bridge to nowhere" for river lots is already handled with `audit_rails`). | Code. | Fine as dressing; it inherits L1. |
| E9 | **Rail stations are boxes on arbitrary ground**, stations not tied to a plaza or street lot. | Code (`_rails` stations, tide-r35 :478+). | No station lot reservation. |
| E10 | **Floating single buildings on the coastal slab and on the quay.** | r35 bay close-up, (1300, 560-600): a cube on the slab corner. | Same as L4 plus Site exemptions (`SITE_KEEP`). |
| E11 | **Wall routes now drawn as highways but are not roads in the plan.** The Solace ring draws nothing, others draw as truck-class decks that pass over building lots and park. | **[A-109]**; r35 plan top: the wall highway looping at (760-880, 100-390). | Wall polygons were never road geometry: corp wall shapes turned into a highway by styling. They get no lot clearing (`wall_skip` now keyed off `a2_walls_draw`, :1712). |
| E12 | **Building lots clipped by view (skips) leave "missing teeth".** | `wall_skip`, `pocket_lots`, `_in_cleared` removal. | View hides layout errors rather than the layout being fixed. |

### 2c. Whole-city read

| # | Defect | Evidence | Root cause |
|---|---|---|---|
| W1 | **No land-use / zoning logic at lot level.** Corp districts are all "towers", differing only by height range and colour. No civic, industrial, residential, market adjacency. The `neighbourhoods` list (26) feeds only height kind (`_height_kind` :591-593). | Contact sheet: all districts read as the same tower texture in different heights. | Land use never enters lot placement. |
| W2 | **Density gradient is a cliff, not a falloff.** Dense core, then bare slab. The 22-lot sprawl fade (`city_a2_sprawl_fade`, tres:592) is random thinning. Outer parts get random singletons (L4). | r35 plan right half, (1500-1778, 400-500): towers on a flat dark slab. | Sprawl by random chance, not by lot size and use gradient. |
| W3 | **Waterfront treatment is absent.** No promenade, quay, pier district or waterfront height rule; a grey slab and floating cubes at the bay. Port exists as a feature. | r35 bay close-up (whole). **Rulings: bay, river already in DIRECTION_REVIEW (r27-r34).** | Setback produces K_BARE grey, nothing draws or places there. |
| W4 | **District transitions.** Colour is per-building random (`CityCorpColor`), so district identity is carried only by height range and by the HQ. Border streets are forced (:350-356) but there is no buffer land use. | r35 seed 3: purple field has no readable district edge except tower height. | Designer ruling 9/10 asked for per-building mixing, so this is intended; the cost is that zoning does not read. |
| W5 | **Scale ambiguity.** 485-850 m blocks plus one building per 121 m lot: buildings are city-block sized. Zoomed in, a "building" is 121 m wide (taller than wide for towers, but a 4x4 low-rise block is a megablock). | Hotspot panel low-rise cubes. | Lot = 121 m by config. Sub-lot buildings only for 85% of "sub kinds" and only when lots are not on a street (:639). |
| W6 | **Seed variation is shallow.** A2 is fixed; a seed changes HQ jitter, grid phase, merges, heights, inks. Seeds therefore look like the same city re-rolled; the layout defects (L1-L3, E1) are **structural, not seed-specific**. Per-seed counts of defects: unverified. | Code (`make_plan` :80-132). | By design (D3). |

---

## 3. Missing rules

| # | Rule | What real cities do | Prevents | Owner | Cost | Pri |
|---|---|---|---|---|---|---|
| 1 | **Rasterise rails, stations, wall/highway routes, ramps** into the lot grid (kind or overlay) and clear K_GROUND/park within a metre-based corridor of the true polyline. | Rail and elevated corridors have reserved right-of-way; buildings sit outside the structure's footprint plus safety offset. | E1, E2, E11, L10, view-side skip lists | layout | M | P0 |
| 2 | **Streets never end in water**: a street lot may only touch water if it is a bridge/quay road end; otherwise trim or turn it into a shore road at least 1 lot inland. | Streets terminate at waterfront boulevards, piers or quays (Embarcadero, Hudson Parkway); they do not stop at the edge. | L1, bay roads (A-108.3) | layout | S | P0 |
| 3 | **Parks bounded by streets, not cut by them**: park lots and their 4-neighbours are not grid lines; street grid stops at the park edge. | Park boundary follows street edges (Central Park: crossing roads are sunken transverses, not grid lines). | L2, E6 | layout | S | P0 |
| 4 | **No dead-end street**: after pruning, every street lot has >= 2 street neighbours or is a plaza/quay/cul-de-sac end by a flag; iterate prune to a fixed point and run a connectivity check (single component). | Street networks are connected; dead ends are rare, short and intentional (Marshall/Southworth street-network metrics). | L1, L8, L9, E8 | layout | S | P0 |
| 5 | **Street hierarchy**: arterial every 8-12 lots across districts, local grid between; arterials continue through district borders; collectors link local to arterial. | Hierarchical network: arterials every ~0.8-1.6 km, local every 100-200 m (Institute of Transportation Engineers street guidelines; CNU). | L9, W1, mismatched border pitches | layout | M | P1 |
| 6 | **Highway interchange spacing and ground connection**: grade-separated interchanges >= 1.6 km (13 lots) apart, each tied to a ground street; ramps land on road lots, never building/park; merge A2 `interchanges` with the view-invented ramps (one source). | US Interstate guideline of 1 mile minimum in urban areas (AASHTO Green Book; FHWA 2 km rural). | E3, E4 | layout + view | M | P1 |
| 7 | **Height field, not dice**: heights from a smooth 2-3 octave noise at block scale mixed with a density-from-core curve; plus low-rise breaks by rule (A-107). | Skyline follows land value: core peak, falling heights with distance, with clusters (Lynch; Burgess/Hoyt models; Hong Kong/Manhattan peaks at nodes). | L5, L6, W2 | layout | M | P1 |
| 8 | **Height step-down at borders and park/water edges**: across a territory border or next to a park/waterfront, heights taper over 3-5 lots (use the raster's `border` field). | Height limits by view corridors and shoreline step-downs (Vancouver view cones, Chicago lakefront). | L6, L7 | layout | S | P1 |
| 9 | **Waterfront band**: the first 2 lots from the sea are one of: quay/promenade street plus low blocks, port/industry, or park. Never bare ground and singleton cubes. | Waterfronts are reclaimed edges with a continuous quay road and low-rise or park (Hamburg HafenCity, Rotterdam Kop van Zuid, Barcelona Barceloneta). | W3, L4, E10 | layout (view for dressing) | M | P1 |
| 10 | **Clustered sprawl**: edge thinning drops whole blocks (cluster noise), not random lots; surviving lots have street frontage and a yard (lawn, trees) rather than grey. | Suburbs fade by lot size and block, with open land in whole parcels (Hoyt wedges; Alonso bid-rent). | L4, W2 | layout | S | P1 |
| 11 | **River frontage and infill** (A-108.1): lots within 3 of a river become low-rise, park or quay; river road bridges every 12-15 lots (A-104). | Rivers get embankment roads and bridges at regular spacing (Seine quais, bridges ~500 m). | L3 | layout | S | P1 |
| 12 | **Block-scale subdivision**: split a 121 m lot into 2x2 buildings in core, 3x3 plots in low-rise, whole megablock only for HQ/corp campus; sub-lot buildings also on street fronts. | Real city blocks are 80-200 m with 5-20 parcels (Manhattan 80x274 m; Barcelona Eixample 113 m). | W5, hotspot scale | layout | L | P2 |
| 13 | **Land-use zoning and adjacency**: assign a use per neighbourhood (CBD, residential, industrial, port, institutional, informal); forbid industry next to Solace/parks; transitions via buffer uses. | Euclidean zoning adjacency: industry downwind and by rail/port, residential not on industry, park buffers (Chicago Plan, Hoyt). The city_planner docs already state this logic ("industry downwind"). | W1, W4 | layout | L | P2 |
| 14 | **Park frontage rule**: park edge lots are streets or low-rise with entries; the tallest allowed adjacent height is 40% of core max. | Parks fronted by streets and mid-rise, "eyes on the park" (Jacobs). | L7 | layout | S | P2 |
| 15 | **Stations and plazas reserved as lots**: each rail station and checkpoint has a plaza lot with a street. | Stations sit at street intersections with plazas (Tokyo/Shibuya). | E9 | layout | S | P2 |
| 16 | **One source of truth for road geometry**: decks derive from the same road records as the raster; raster stroke width in metres, decks snapped to lot centre or lots snapped to deck. | n/a (engineering): single network graph (OSM-style). | E2, view/layout drift | layout + view | M | P1 |
| 17 | **Sites need a street**: Site lot must touch a street and not be on road/park (hard, not -1). | Access rule. | L11 | layout | S | P2 |
| 18 | **Avenue strips end at intersections**, never run past a built run into open land or parks; start at a lot with buildings on both sides. | Neon/commercial strips are bounded by cross streets. | E5 | view | S | P2 |
| 19 | **Traffic only on a validated road graph** (ground cars on K_STREET with >= 2 neighbours, sky lanes avoid bays and bare lots). | Traffic follows the network. | E7 | view | S | P2 |
| 20 | **District-identity colour**: keep per-building random but raise the local corp share near the district centre and fade at borders so zoning reads. | Neighbourhood identity (signage, material) clusters. | W4 | view | S | P3 (designer ruling 9/10 stands) |
| 21 | **No-hide policy**: the view may not skip lots/buildings; a skip list becomes a lint failure. | n/a | E12 | view + layout | S | P1 |
| 22 | **HQ and Solace transitions**: ring road or promenade around HQ parks; towers start 2 lots out. | Campus edges with perimeter roads. | L7 | layout | S | P2 |

---

## 4. Architecture assessment

The split is sound in principle: a deterministic layout feeds view-only dressing. What is wrong is **where the rules live**.

1. **Layout has one layer of rules (per-lot kind flags) and almost no inter-layer rules.** Raster has roads, water, parks, districts, but not rails, walls, ramps, stations. So the layout cannot see them, and the view has to keep removing buildings (`_build_wall_skip`, `pocket_lots`) or fix them with its own audits.
2. **The same rule is implemented several times.** Road geometry: lot stroke (raster :213) vs deck polyline (features `_deck`) vs interchange crossings (view) vs plan `interchanges`. "No lamps/avenues in highway zone": `CityLampPlan.highway_zone` plus `avenue_strips(zone)`. "Building must have street frontage": coast setback (:421), prune (:437), lamp rule, neon rule. Solace has its own generator.
3. **Audits live in the view and test only that feature against its own inputs.** `audit_avenues` checks that strips are on street lots, but not that the street lot is sane.
4. **The planner is hand-authored but the plan is never validated geometrically.** All the L-class failures follow from the plan and grid being unchecked against each other.

Recommendation: **(b) a "city lint" validation pass, with (a) targeted layout rules to fix what the lint finds.** Not (c).

Why (b) first:
- It gives an objective list. Today we find defects by designer screenshot (r14 red boxes, r26 notes) one at a time and patch in the view.
- The rules are cheap to express over data the builder already has (kind grid, streets, rank, rect, raster, terrain, polylines).
- It is pure and seedable, so it runs headless with no GPU (CLAUDE.md rule: deterministic core).
- It turns A-104 to A-109 into permanent regression tests instead of one-off asks.

Why not (c): the macro plan (A2) is good and the designer has accepted its read. A rewrite to a graph-first generator (street graph, then blocks, then parcels) would solve L1-L9 at root, but is multi-week. Do it only if the lint shows a failure rate that cannot be fixed by constraints.

Effort estimate: lint module (`scripts/core/city_lint.gd`, pure) 2-3 days for P0 checks, 1 week for the full list; layout rules P0 (rules 1-4) 3-4 days; P1 (5-11, 16) 2 weeks. Hide-policy (rule 21) can be enforced the day rules 1 and 11 land.

Where rules should live:
- **Layout (constraints)**: everything that changes what is a street, building, park, bare. Rules 1-17, 22.
- **View (dressing + audit)**: only how things look, and an audit that asserts the view drew only what the layout said (rules 18-21).
- **Lint**: reads the layout and the plan, never the view, and a view-level lint reads prisms and quads (existing audits) to assert no skip lists.

---

## 5. Seed sweep plan (plan only; nothing run)

**Seeds**: 1-3, 7, plus 20 seeds from a fixed list (e.g. 11, 23, 37, 41, 59, 61, 73, 89, 97, 101, ...). Layout defects that are structural will repeat across seeds; the sweep is to catch seed-dependent ones (HQ jitter, grid phase, merge).

**Layer 1: headless lint over every seed (no GPU)**, `CityLint.run(plan, lots) -> {rule: [lots]}`. Checks (each a count and a list of lots):
1. Street lot 4-adjacent to a sea lot (excluding declared quays and bridges): must be 0 (L1).
2. Street lot inside a park polygon (not boundary): 0 (L2).
3. Street dead ends (street lot with one street neighbour, not flagged quay, plaza, cul-de-sac): 0, or <= 2% of streets (L9, L8).
4. Street network connected components: 1 (plus islands that have a bridge).
5. Building lot within a metre buffer of any rail/ramp/wall-highway/highway polyline: 0 (E1, E2, E11).
6. Ramp end points and interchange centres on road lots or land: 100% (E3).
7. Park lots that are 4-adjacent to a street on both lateral sides: 0 (A-108.2).
8. Bare lots inside the dense zone (district not sprawl, depth > 2): <= N.
9. Singleton building (no building within 2 lots) inside the city ring: <= N (L4).
10. Height step between 4-adjacent buildings > 2.5x ratio count and > 25 BU: list (L6), plus fraction of dense-core lots with height < 50% of local median: 3-4% (A-107).
11. Building lots with no 4-neighbour street (no frontage): 0.
12. Site lots on road/park: 0.
13. View skip lists (`wall_skip`, `pocket_lots`, `_in_cleared`) size: 0 outside declared HQ compounds.
Pass = all counts 0 or within their budget on **every** seed. Fail output = lots with coordinates, ready to paste into a mailbox ask.

**Layer 2: existing view audits per seed** (headless): `CityNeonKit.audit`, `audit_avenues`, `CityLampPlan.audit`, `audit_rails`, `CitySolacePockets.audit`, `wall_clash` count (must be 0 once rule 1 lands). Run on the tide branch.

**Layer 3: render captures** (windowed, GPU free later; `python tools/run_windowed.py` per CLAUDE.md). Per seed, four zooms:
- plan zoom (existing G1 plate camera);
- zoom 2: 1 district (hotspot panel scale);
- street level at 3 fixed anchors: bay shoreline, a highway/ramp crossing, a park edge;
- one high oblique shot over the river reach.
Anchors are chosen from lint output (worst offender lot per rule) so the capture sees the defect. Pass = a human or critic checklist: no street into water, no rail through tower, no ramp to nowhere, no floating cube on slab, park reads as one. Keep a contact sheet per round (like `compare_*.jpg`) and diff against the previous round.

**Cadence**: lint in every build CI run (fast, pure); render sweep per art round on seeds 1, 3, 7 plus 2 random.

---

## 6. Top 10 actions

1. **Build (mailbox): rasterise rails, stations, ramps and wall-highways and clear buildings in a metre corridor** (rule 1). Subsumes A-106 and the view's skip lists. One-line spec: "treat every rail and highway polyline as a lot overlay and clear K_GROUND/park within `corridor_m` of it; no building may overlap."
2. **Build: street/coast/park rules** (rules 2, 3): "street lots may not 4-touch sea except flagged quays/bridges; grid lines stop at a park edge." Extends A-108.2 and A-108.3.
3. **Build: prune to fixed point and dead-end ban plus connectivity check** (rule 4): "iterate prune until stable; every street lot has >= 2 street neighbours or is a flagged end."
4. **Build: write `CityLint` (pure, headless)** with checks 1-13 above, run on 25 seeds, fail CI on violations. Gate everything else on it.
5. **Build: height field and rhythm** (rules 7, 8, A-107): "smooth block-scale noise times core falloff, step-down over 3-5 lots at territory borders, 3-4% low breaks."
6. **Build: waterfront band and river infill** (rules 9, 10, 11, A-104, A-108.1): "first 2 lots from the sea are quay road plus low-rise, port or park; river margin 3 lots filled."
7. **Art view: single road-geometry source** (rule 16): "decks and lot raster read from one road record set; align deck centre to the raster centre line; ramps from plan `interchanges` plus view crossings, deduplicated; ramps land on road lots."
8. **Art view: retire skip lists and add the 'no-hide' assertion** (rule 21): "after action 1, `_build_wall_skip` must return 0; fail in headless test otherwise. Keep the Solace pocket skip until A-105 lands."
9. **Build: street hierarchy** (rule 5): "arterial every 8-12 lots continuing across districts; local grid pitch blends instead of jumping at borders."
10. **Art view: avenue-strip and traffic end rules** (rules 18, 19): "strips start and end at intersections, never over bare run or park; sky lanes and ground cars only on validated road graph."

---

## Unverified / limits
- Per-seed defect counts (no Godot run). The statement "dead ends into the bay at seed N" is derived from the builder logic (:345-358 versus :421-424) and the r35 bay close-up; exact lot counts per seed need the lint.
- Whether `CityLayoutRuler` changes heights enough to break the A-107 targets: not traced.
- Existing tests in the main repo for city layout: only a filename search was done.
- Image regions are approximate, read from a downscaled contact sheet.
