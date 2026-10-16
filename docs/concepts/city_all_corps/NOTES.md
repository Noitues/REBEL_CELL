# City, all corps: the one city with all seven corp districts (key art, 2026-10-15)

One city render that shows every corporation's district, like the earlier whole-city key art
(`round30_meridian_castle/city_night_hq_v6.jpg`), but built on the one-city layout and rules and in the approved AAA-2 look.

Nothing is committed and the Godot build is untouched. Everything is rendered headless in Blender 5.2.2: Cycles on the GPU
(RX 6700 XT, HIP, plain BVH2, OIDN) for the AAA-2 images, Eevee for the mainline check. All randomness is seeded
(`city_preset.SEEDS`).

## Files

| File | What it is |
|---|---|
| `city_all_corps_night.png` | **The hero shot**, 3840 x 2160. A high 3/4 aerial (yaw 135, the map's own direction, pitch 47) of the whole city at night in the AAA-2 look: fog banks lit by each district, beams, light-streaks on the arterials, the seven landmarks, the sea and the seawall. |
| `city_all_corps_labeled.png` | The same image with the district labels: the corp name in its hue, the crest disc and the landmark's name, in the map's tag style (the round 30 v6 tag: dark slanted plate, hue bar), with a leader to the landmark. |
| `city_all_corps_mainline.png` | The same camera in the MAINLINE City Grid look (toon ramp, ink, the post40 finish and the sb_mhq capture match). |
| `tethys_flooded_closeup.png` | 2560 x 1440. The drowned quarter from above the levee: clear water over the submerged blocks inside the curved seawall, fading to deep blue with depth and distance, soft caustic ripples, the shafts, ATLANTIS STATION in its trench. |
| `zoning_map.png` | A top view of the zoning (districts, the drowned quarter, the coast, the arterials, the aqueduct, the landmark clearances). |
| `scripts/` | Everything to rebuild (see "Rebuild"). |

## Results (revision 2, 2026-10-16 00:13: hero re-rendered; the close-up is the approved revision-1 render)

The first pass is backed up in `D:\rc_scratch\city_all_corps\v1\` (images + scripts). Before / after crops (left v1,
right revision, same camera and pixels) are in `D:\rc_scratch\city_all_corps\crops\` (`scripts/crops.py`).

Scene: 14 232 buildings, 35 227 ring props, about 670 k faces; 7 landmarks; Tethys bay, seabed and trench; the
Meridian freight viaduct (551 BU, 7 corners).

| Render | Engine | Resolution | Samples | Build | Render | Wall |
|---|---|---|---|---|---|---|
| hero (AAA-2), rev 2 | Cycles GPU (HIP, BVH2, OIDN) | 3840 x 2160 | 40 | 10.1 s | 266.2 s | 281 s |
| close (AAA-2) | Cycles GPU (HIP, BVH2, OIDN) | 2560 x 1440 | 40 | 9.5 s | 127.7 s | 142 s |
| hero (MAINLINE), rev 2 | Eevee | 3840 x 2160 | 16 TAA | 10.1 s | 4.7 s | 21 s |

Values (sRGB luma of the final PNG; AAA-2 targets: median about 0.14, 25-40 % under 0.10, at most 2.5 % over 0.85):

| Image | Median | Under 0.10 | Over 0.85 | Exposure k | Toe | v1 (median / under 0.10) |
|---|---|---|---|---|---|---|
| `city_all_corps_night.png` | 0.140 | 28.7 % | 0.25 % | 0.882 | 1.0 | 0.128 / 28.1 % (rev 1: 0.140 / 28.4 %) |
| `tethys_flooded_closeup.png` | 0.140 | 27.6 % | 1.66 % | 4.557 | 1.85 | 0.136 / 17.9 % |
| `city_all_corps_mainline.png` | 0.213 | 1.0 % | 0.02 % | n/a | n/a | 0.221 / 0.2 % (mainline look, not held to the band) |

Also in `D:\rc_scratch\city_all_corps\final\value_checks.json`. The post now takes the fog veil off at a black point
(0.85 x the frame's 5th percentile per channel, `AAA["black_point"]`) and solves exposure with the vignette inside the
solve; the toe is raised only if the dark share is still under 27 %.

## Rebuild

1. `python zoning.py` writes `zoned.json` and `zoning_map.png` to `D:\rc_scratch\city_all_corps\` (bay, outline flags,
   the rail search and the rail-side height cap).
2. `python run_jobs.py aaa hero,close 1.0 40 final`: the Cycles passes, under the GPU lock (`D:\rc_scratch\GPU_QUEUE.md`).
   Each Cycles run also writes `D:\rc_scratch\city_all_corps\meridian_rail.json` (the rail polyline, world BU).
3. `python run_jobs.py main hero 1.0 16 final_main`: the Eevee mainline pass (no lock).
4. `python make_all.py`: the post, the labels and the value checks, written into this folder.
5. `python crops.py`: the before / after crops against `v1`; `python beam_check.py <png> <anchors.json>`: the beam rule.
CPU previews (no lock): `sh cpu_prev.sh <cam> <res_k> <spp>`. Debug switches: `CITY_NOFOG`, `CITY_NOWVOL`, `CITY_NOWATER`.

## Art director review of the first pass: what changed

1. **Outlines (no wireframe grid).** Crown trims at 25 % of their old rate except on buildings flagged `art` (within
   1.3 lots of an arterial) or `border` (another district within 2 lots); street lanes at 25 % except arterial tiles;
   ring trims at 2.5 %; ring street glow cut to 0.3 (main roads) / 0.08 (others). Where a trim is dropped the roof gets
   1-3 clutter boxes and, at 35 %, a warm roof lamp (`OUTLINE` in `city_preset.py`). Crop `1_outlines_sprawl`.
2. **Districts without labels.** Rebel Cell heights x 0.7, red-weighted blade / box signs, lantern strings on every
   street face, glow power x 1.8 (`rebel_glow_k`). Meridian: container stacks on 95 % of freight roofs. Aurelian:
   travertine facades, gilt trims and gilt fog glow (verdigris now only on domes), no longer twin to Solace. Orbital:
   six flood masts lighting the podium disc, a light ring at the rim, the rocket keyed white. District glow mix 0.25.
   Crops `2a`-`2d`.
3. **Tethys and the coast.** The seawall and the coast curve into a bay (`BAY`: Gaussian bow 16 lots deep round the
   drowned quarter, headlands past 120 lots); the drowned blocks sit inside the wall under clear water; pump towers
   every 66 BU of arc follow the curve. Drowned windows: lit share at least 0.45 and wet facades x 2.6 emission before
   the water fade. A sea-mist volume from 30 lots past the coast thickens with path length, so the horizon dissolves.
   The low fog is 96 % cleared over the bay (`bay_clear`), the haze band too. Crop `3_bay_horizon`.
4. **Fog strata.** The low district banks (hue-lit by the district glow) plus a torn upper sheet at z 58 BU, and a low
   shore bank along the dry side of the levee. Hero median 0.140, 28.4 % under 0.10. Crop `4_fog_strata_full`.
5. **Beams.** Only roofs whose base AND a point 150 BU up the beam fall inside the central frame (24 % / 12 % margins);
   each beam is a soft 3 degree cone plus a 0.9 degree hot core (two spots); power raised to 2.2e8 / 2.6e8 so they
   read after the black point. The lower-left pink and cyan beams are gone. Crop `5_beams_lower_left`.
6. **Tethys close-up.** The voronoi crack caustics are replaced by soft noise-ridge ripples (two layers, distorted,
   blue-green, low floor, patchy). The shore city is darker (plazas 0.13, wet concrete 0.17), sits in the shore fog
   bank, and keeps its lit windows, kerb lamps and arterial streaks. The seawall curves. 27.6 % under 0.10 (was 17.9 %).
   Crops `6a`-`6c`.
7. **Meridian freight rail (designer note + pipeline-spec ruling).** The line is the street-tile BFS from the fort gate
   to the coast (zoning L4): it runs only over street centre lines, so it threads between buildings and never crosses
   one, then a jetty over the bay to a container terminal on the seawall. Per the art director ruling it leaves through
   the NORTH rail-yard gate (the yard, wagons, lamps and gantry crane moved to the fort's north half; a spur from the
   middle track runs out through a 6 x 5.2 BU orange-lit portal in the north container wall). The deck stands at
   17.5 BU (ramp up over 60 BU from the gate, down over 45 BU to the terminal at 8.7 BU); all 130 dry buildings within
   1.2 lots of the line are capped at a 15.5 BU roof (7 needed cutting) and keep plain roofs. Orange rail glow on both
   deck edges, orange signal lamps every 36 BU, two train light-streaks. The polyline (world BU, with deck z per corner)
   is exported to `D:\rc_scratch\city_all_corps\meridian_rail.json` as the source of truth for the HQ kit. These rail
   changes are IN this render (the GPU pass ran after the ruling). Crop `2b_meridian_rail`.

### Still open (honest self-review)

- The outline grid is much quieter, but the remaining arterial trims / lanes and the dimmed ring street glow still
  read as a faint grid in the outer ring at hero scale. A next pass could drop the ring glow further.
- From the hero height the viaduct reads as a thin warm line; it reads clearly only in the close crops and the Eevee
  debug view (`prev\dbg_rail_q.png`).
- Beams still read fairly rod-like at 3840 px (the soft cone is subtle); one landmark hero beam leaves the top edge.
- The close-up meets the dark share with a toe of 1.85 on top of the black point (the bay water fills the frame).

## Art director review of revision 1 (revision 2: hero only, 2026-10-16)

Revision 1 is committed as is; the close-up is approved and was not re-rendered.

1. **Beams.** The 6 roof beams and the two-spot rods are gone. Now ONE beam per landmark, rising from its crown (6: REBEL_CELL
   has no crown). Each one follows the storyboard round-3 recipe (`m44/onecity_cycles.py`): an emissive cone seen by the camera
   only, with a hot gaussian core over a wide soft skirt. It is brightest at the source and gone by 60 % of its length, with a
   slow noise breakup. A wide, fully soft 30-degree spot, linked to the fog only, lights the air round it (`AAA["beam"]`: length 420 BU, half-angle 1.1
   deg, emit 1.1, haze 1.2e7). Each beam is shortened in 10 % steps until its fade end sits inside the frame; Tethys is cut to 340 BU.
   The rule check (`beam_check.py`, final PNG luma) passes for every landmark:

   | Landmark | Landmark peak | Local bg | Ratio (>= 1.5) | Beam peak (< landmark) | End in frame |
   |---|---|---|---|---|---|
   | Aurelian | 0.999 | 0.315 | 3.17 | 0.858 | yes |
   | Halcyon | 1.000 | 0.324 | 3.09 | 0.796 | yes |
   | Meridian | 0.942 | 0.230 | 4.10 | 0.737 | yes |
   | Orbital | 1.000 | 0.240 | 4.17 | 0.801 | yes |
   | Solace | 0.949 | 0.290 | 3.27 | 0.696 | yes |
   | Tethys | 0.733 | 0.221 | 3.32 | 0.502 | yes |

2. **Outer ring grid.** Outside the seven districts (the sprawl and the ring), trim and lane emission is at 30 % of revision 1
   (`OUTLINE["out_k"]`; the ring street glow is now 0.09 / 0.024). Warm roof lamps (30 % of ring buildings) and a higher
   ring window lit share (0.14) carry the outer city. Crop `1_outlines_sprawl` (now v1 vs revision 2).
3. **Rail legibility.** The orange deck-edge glow is wider (0.12 -> 0.45 BU) and brighter (0.55 -> 0.9). There are three
   train light streaks (two with container wagons), 0.6 BU wide. At hero scale the line now reads from the north gate to
   the seawall terminal. Crop `2b_meridian_rail`.

Hero values: median 0.140, 28.7 % under 0.10, 0.25 % over 0.85 (exposure 0.882, toe 1.0). The crops in
`D:\rc_scratch\city_all_corps\crops\` were refreshed (the hero crops now show revision 2; the close-up crops are unchanged).
Still open: the Halcyon and Solace beams sit close to their landmark peaks (0.80 / 0.70 against 1.0 / 0.95). The outer
ring is quiet now but slightly flat.

## Round 3 (designer review of round 1, 2026-10-16): day + night, transit, influence colours, organic edge

Status: **1920 x 1080 Cycles tests only; waiting for the designer's review before the 4K finals.** The revision-2
scripts, images and `zoned.json` are backed up in `D:\rc_scratch\city_all_corps\v2b\`. The deliverable PNGs in this
folder are still revision 2 until the finals; the round-3 tests are in `D:\rc_scratch\city_all_corps\r3test\`.

### What changed, by designer note

1. **Day version** (`mode day`, `city_preset.DAY`). Late-afternoon sun (strength 7.5, warm, elevation 24, azimuth 15,
   angle 1.2 deg) under a gradient sky (warm hazy horizon, blue zenith, warm ground bounce). A sun- and sky-lit
   height-falloff haze with low torn banks (aerial perspective; thinner over the bay) replaces the night fog; the
   sea-mist volume is off (it denoised into blotches) and the far haze is a post depth haze instead (from 1300 BU,
   e-fold 2600, max 85 %, toward a pale haze at the lit city's 80th-percentile level; the depth pass is median-filtered
   because it is noisy through the water and glass). Day facades: the district albedo with a soft weathering noise and
   a 28 % tint of the corp hue (sprawl and REBEL_CELL untinted), glass windows (dark, glossy, mirroring the sky), 10 %
   of the night window emission. Neon at 22 % of night (signs still glow faintly). No beams, no district glow, no
   landmark key spots, no underwater area lights; direct-light clamp 8 and glossy blur 1 against glints. Traffic draws
   become cars (the same draws, `city_build.traffic`). Post `post_city.day`: black point 0.6 x p5, exposure solved to
   median 0.36 (no band set yet), Reinhard shoulder (white 6), contrast 1.12, saturation 1.12, light vignette.
2. **Orbital pad** (`ORBITAL_PAD`): the six flood masts, their 70-degree spots, the bright ring light and the
   camera-side key are gone. Five short masts at the platform edge each carry a housing, a lens and an 11-degree spot
   aimed at the rocket body (aim points alternate between z 10 and 26): the rocket is keyed, the pad stays dark. Rim
   lamps at 45 %.
3. **Aurelian** (`AURELIAN_LM`): three colonnade tiers of 60 round columns (base and entablature bands per tier), the
   arched wall recessed 1.7 BU behind them (lit gilt arches in the loggia), a solid attic band on top. The cavea is four
   seating rings of four flat terraces each with vertical risers (stair-stepped, no ramps); a gilt line on each ring's
   lowest step.
4. **Highways and trains** (zoning H4 / H5, `city_transit.py`). Highways: the longest arterial street lines that stay
   1.5 lots clear of every landmark clearance (2 on the lot x axis at deck z 24, 1 on y at z 30, so they cross as
   stacked decks), each over its whole land span, from 120 lots out in the sprawl to a ramp 6 lots short of the seawall
   or the drowned quarter. Deck slabs, girders, parapets with a cool edge light, piers on the street centre line every
   12 BU, sodium lamp masts on the median every 14 BU, dense traffic in two lanes each way (heads warm white, tails
   red). 52 map buildings standing in the gaps of the arterial runs were removed (the corridor is clear); the ring
   keeps its blocks off the lines. Metro: one elevated loop (z 12) through a waypoint per landmark corp at 60 % of the
   way from the centre to its HQ, routed over street centre lines by a Dijkstra with a turn cost (13 corners), off the
   highway and rail lines where it can; round piers, cyan edge lights, a station at each waypoint (two platforms, a
   lit canopy), seven lit trains of five cars. The Meridian freight line is re-derived by the same L4 rule from the
   moved fortress (the BFS is now blocked by every landmark footprint). Its polyline goes to
   `D:\rc_scratch\city_all_corps\meridian_rail_r3.json`; the round-2 `meridian_rail.json` the HQ kit reads is untouched.
5. **Colour by HQ influence** (H2, `INFLUENCE`, `city_rules.district_weights` / `draw_district`). Every building (map and
   inner ring) draws its district: weight exp(-d / 10 lots) per HQ (lambda x 0.75 for REBEL_CELL, x 1.15 for Tethys)
   against a constant sprawl weight exp(-23 / 10); all corp weights are scaled by the urban factor u (note 6); the draw
   is seeded per building key. A district is near-solid at its HQ, thins outward and mixes with its neighbours and the
   sprawl across the borders. The draw sets the building language too. Drowned buildings stay Tethys. Lane hues follow
   the tile's district. The fog glow colour is the same weight mix (the sprawl counts half so the hues stay readable);
   its power follows u.
6. **Organic city edge** (H3, `URBAN`, `city_rules.urban_u`). The urban core is a superellipse (p 3.2, r0 68 lots,
   squashed toward the coast) broken by seeded harmonics k = 2..7 (20 %) and 2D value noise (cell 11 lots, +-11); u
   fades over 30 lots. Map buildings past it go lower (down to x 0.55) and dimmer (lit share down to x 0.22) with fewer
   trims and dimmer lanes; ring buildings inside it become city buildings by the map's own rules (heights, language,
   colour draw). The arterial trails run on along their own lines into the sprawl (H6, up to 110 lots past the map)
   and thin out (density and brightness x exp(-d / 40 lots)); highway traffic thins the same way (55 lots). The ring
   light falls off over 80 lots (was 50), its street glow over 90 (was 60) and is brighter inside the core; the fog
   glow keeps an 18 % floor outside it.
7. **HQs pushed apart** (H1, `HQ_LAYOUT`). REBEL_CELL is the centre lot; Meridian at bearing 32 deg / 52 lots, Solace
   150 / 50, Orbital 208 / 52, Aurelian 268 / 53, Halcyon 326 / 52 (screen plane, 90 = toward the coast); Tethys keeps
   its pole over the drowned quarter. The minimum HQ spacing goes from about 30 to about 50 lots. New sites are
   cleared (landmark_r) and refilled outside their footprints; the old HQ plazas of the layout are built over (725
   refill blocks in all). Tiles under a landmark carry no lanes, lamps or trails.
8. **REBEL_CELL** wears the sprawl palette (`REBEL_KEYART_PALETTE`): sprawl facades, windows, trims, lane hue and fog
   glow; no red weighting in the canyon signs, amber / warm white lanterns, no fist windows, no beam (no crown), no
   `rebel_glow_k`. The canyon language (heights x 0.7, blade and box signs, shop fronts) and the MAINFRAME blade sign
   (now on the building nearest the centre lot) stay; that blade is the only red.

Also: the outer sprawl ring varies now (22 % of its blocks are one merged building over all four lots, 1.3x taller;
six concrete / brick tones; height spread 0.72); the metro edge lights are at 1.2 and the train windows at 1.5.

### Round 3 tests (1920 x 1080, Cycles GPU HIP BVH2 OIDN, 32 spp)

| File (`D:\rc_scratch\city_all_corps\r3test\`) | Median | Under 0.10 | Over 0.85 | Exposure | Render |
|---|---|---|---|---|---|
| `city_all_corps_night_r3test.png` (+ `_labeled_r3test.png`) | 0.140 | 34.9 % | 0.06 % | 0.751, toe 1.0 | 58 s (build 12 s) |
| `city_all_corps_day_r3test.png` | 0.360 | 2.0 % | 0.35 % | 1.983 | 29 s (build 11 s) |

Night is inside the AAA-2 band (median 0.14, 25-40 % under 0.10). Day: no band set; reported only. Also
`zoning_map_r3.png` (the top view: HQs, influence colours, highways, metro, rail, the urban edge contour). CPU previews
of the pad and the circus: `D:\rc_scratch\city_all_corps\r3prev\dbg_orb_cpu.png`, `dbg_aur_cpu.png`.

### Landmark modules (the swap-in hook)

`city_preset.LANDMARK_MODULES` maps a corp to a Python file. When the path is set and exists, `landmarks.py` loads it
(`importlib`) and calls its `build(ctx)` instead of the built-in function; unset or missing, the built-in landmark is
used (a missing path is logged). Meridian (`route_map_graph/hq_meridian_v3/`) and Tethys
(`route_map_graph/hq_tethys/scripts/tethys_landmark.py`) plug in here; both are `None` today (the current landmarks).

Contract: `build(ctx) -> dict(label=(x, y, z), crown=(x, y, z) or None, hue=(r, g, b))`. `label` anchors the map tag,
`crown` is where the landmark's one beam starts (None: no beam), `hue` colours the beam. `ctx` (a SimpleNamespace):

| Field | What |
|---|---|
| `corp`, `hq` (world BU xy of the HQ lot centre), `hq_lot`, `footprint` (the `LANDMARK_FP` entry: stay inside it) | where to build |
| `mode` (`aaa` night, `day`, `main` Eevee mainline), `district` (the `DISTRICTS` entry), `seed`, `zw` (sea level), `wet_cells`, `camdir` | context |
| `SURF` (facade shader; `face(pts, col, uv, wc, wl, wm, bid, wet)`), `SMOOTH`, `NEON` (emitters, col = emission), `GLASS`, `STREAK` | geometry accumulators |
| `prism`, `box`, `cyl`, `dome`, `bar`, `strip`, `ring_line`, `annulus`, `circle`, `sc`, `mixc` | the primitives of `city_build.py` |
| `spot_at(target, from, col, power, cone)`, `light_spots` (append dicts with `blend` / `k` for full control) | landmark key lights (off by day) |
| `station` | Tethys must set `station["centre"] = (x, y)` (the anchors and the close-up use it) |
| `W`, `O` (the zoned data), `CP` | lots -> world, everything else |

World BU, x east, y north, z up, the dry street at z 0. A module only adds faces and lights.

### Rebuild (round 3)

1. `python zoning.py` (now also places the HQs, draws the districts and the urban factor, picks the highways, routes
   the metro).
2. `python run_jobs.py aaa hero <res_k> <spp> <out>` and `python run_jobs.py day hero <res_k> <spp> <out>` (GPU queue;
   `run_jobs` now lets every other waiting agent go first).
3. `python post_city.py aaa <out>/hero_aaa <png>` and `python post_city.py day <out>/hero_day <png>`.

CPU previews: `CITY_CPU=1 blender -b -t 4 --factory-startup --python city_build.py -- <aaa|day> <cam> <dir> 0.2 12`.
New debug cameras: `dbg_orb` (the pad), `dbg_aur` (the circus), `dbg_hw` (the highway cross). The hero camera moved
(target b 18 -> 9 lots, distance 1100 -> 1180 BU) so Aurelian (now near the camera) stays in frame.

## Round 3b (art director + designer notes on the r3 tests, 2026-10-16)

Status: **new 1080p tests of night and day; waiting for review. The 4K finals are held until the Meridian (Gatehouse
Gantry, `hq_meridian_v3/`) and Tethys (`hq_tethys/`) landmark modules are approved and can be swapped in** (hook above).
The revision-3 zoning is backed up as `D:\rc_scratch\city_all_corps\zoning_pre_r3b.py`.

Transport (designer 1-3; zoning block "T", `city_transit.py`; config `CURVES`, `PORT`, `HUB`, `SPOKES`):
- **No 90-degree turns.** Every highway, rail and metro path is a centripetal Catmull-Rom curve (`city_rules.catmull_rom`,
  sampled every 0.5 lot). Corridors (half width + 0.35 lot) are cleared of map buildings (941 removed) and the ring keeps
  its blocks off the exported corridor cells. A landmark-clearance check warns if a curve passes a landmark (none do).
- **The port.** The freight rail now leaves the fortress's north gate straight, bends once (a gentle S, 5 lots off the
  chord) and ends in a PORT on the coast stretch a = 62..104 lots (east of the drowned quarter, outside Tethys' water):
  a raised terminal platform (z 3.6) with a quay wall 4 lots out over the sea, container blocks (3 wide, 1-4 high) in 7
  rows, 4 yard tracks with waiting wagons, 6 ship-to-shore gantry cranes (orange / white, booms over the water, a
  container on each spreader, warning lights), 3 container ships moored outside (hull, stern bridge, deck stacks), 9 yard
  light masts (sodium spots at night). The seawall, its pumps and lamps stop at the port; no drowned ruins in its water.
  The rail polyline goes to `meridian_rail_r3.json` (the HQ kit's `meridian_rail.json` is untouched).
- **The Meridian hub.** A ground-level truck ring road (10 BU, 4 lanes of traffic, kerb lamps) runs round the Meridian
  lot as a rounded square 10 BU outside the landmark footprint (corner radius 16 BU), so the Gatehouse Gantry keeps its
  lot. Four highway spokes leave it tangentially, ramp up (over 80 BU) to their decks (east and west z 24, south z 30)
  and run out into the sprawl through config waypoints; the port spur (z 14) ramps down into the port yard. The old
  straight arterial-line highways are gone. The metro is a smooth closed loop through its six stations.

Night (AD + designer 5, 7):
- Exposure target median 0.155 (designer: lift to 0.15-0.16 inside the approved 0.14 +- 0.03 band).
- Orbital: the five edge spots at 3.5e6 (was 3.2e5), so the rocket reads as a lit needle (`rocket_check.py` below).
- Solace: its key and fill spots x 1.8 (`SOLACE_LIFT`).
- The organic edge has a block-scale ragged term (`amp_f` 8 lots, cell 4) and stronger noise (`amp` 0.24, `amp_n` 15);
  ring blocks inside the edge become city buildings by a dithered draw (probability u x 2.5), so the map's diamond
  outline no longer shows as a line.

Sprawl (designer 6): lower and wider at the same coverage: 45 % of ring blocks are one merged low building over four
lots (x 0.85), single ring buildings x 0.62 height, 5 % empty lots (was 12 %), 6 % of blocks are parks; the map's own
buildings past the core edge go down to x 0.45.

Day (AD day notes + designer 4; designer wins where they conflict):
- Values matched to the references. Measured (sRGB Rec.709 luma; `D:\rc_scratch\city_all_corps\ref_values.py`):

  | Reference | Median | p10 | p90 | Spread | Under 0.10 | Saturation (median) |
  |---|---|---|---|---|---|---|
  | `round10_combat_c/combat_day_boss.png` (the in-game day map) | 0.147 | 0.044 | 0.434 | 0.390 | 25.5 % | 0.25 |
  | `round11_combat_target/.../boss_day.png` (street backdrop) | 0.575 | 0.400 | 0.712 | 0.312 | 0 % | 0.19 |
  | `round11_combat_target/.../boss_daycool.png` | 0.568 | 0.390 | 0.714 | 0.324 | 0 % | 0.24 |
  | `route_map_graph/storyboard/mainline_match.jpg` (mainline) | 0.144 | 0.038 | 0.425 | 0.388 | 32.4 % | 0.36 |
  | r3 day test (rejected: too bright) | 0.360 | 0.173 | 0.661 | 0.488 | 2.0 % | 0.18 |

  The two aerial / map references (the game's day map and the mainline match) sit at median 0.14-0.15, spread 0.39.
  The boss backdrops are bright street-level illustration (median 0.57) and do not match "much lower". The day now
  solves exposure to median 0.20 (a step above the night's 0.155, so day still reads as day) and solves the contrast
  (about the median, capped at 2.0) to the references' spread 0.39, with a shadow floor (lift 0.05) so p10 stays near
  the references' 0.04.
- Mood: a hazy smog day. The haze is denser and warm-grey (0.0012 per BU, e-fold 70 BU, banks 0.008), the low warm sun
  stays (strength 10, elevation 14, azimuth 80, angle 0.5: long crisp shadows) under a cooler, dimmer sky fill
  (strength 0.6), saturation 1.0.
- Materials (AD 2): each building draws a family by key (`DAY_MATS`: concrete, a dark glass curtain, brick, rust, pale
  stone; the sprawl draws from brick / rust / weathered concrete), a roof finish (`DAY_ROOFS`: tar, gravel, green roof,
  solar, terracotta), the window grid on every facade (glass mask), then the corp tint: 0.28 + 0.32 x exp(-d / 14 lots)
  from its own HQ (stronger near the HQ, AD 6).
- Ground (AD 3): streets and the ring's streets are dark asphalt; map plazas are parks (60 %, lawn + tree clumps) or
  paved squares; 6 % of ring blocks are parks (lawn, a cross of paths, 2-5 clumps of round trees).
- Sea (AD 4): the sea-mist volume is off; clean water (broad soft swell, roughness 0.09, soft glints) under the post
  depth haze.
- Signage (AD 5): the large billboards (blade signs and rooftop holo panels) are their own emitter (`BILL`) at 35 % of
  the night neon by day; the rest of the neon stays at 22 %; lit windows 18 %.

## Round 3c (designer notes on the r3b: roads, ramps, Meridian bypass, realism diagnostic, 2026-10-16)

Daylight, the port and the rest of r3b are approved. Code: `city_rules.py` (`LotPath`, `intersections`, `hermite`, `slip`,
`cloverleaf`, `ring_profile`), `zoning.py` (block "T"), `city_transit.py`, `city_world.py` (rail height); config
`city_preset.py` (`THROUGH`, `RING`, `RAIL_WEST`, `RAMPS`; `SPOKES` is gone).

1. **Perimeter ring highway** (replaces the circular metro loop, which is no longer built; `metro` is `None` in the zoned
   data). The urban edge (u = 0.5) is scanned every 2 degrees, dilated 14 degrees, smoothed (Gaussian 8 then 4 degrees), pushed
   4 lots out, held off the coast, the drowned quarter and the port yard (`ring_ok`), then a closed Catmull-Rom through
   every 4 degrees (1070 samples). Deck z 12, 6.6 BU wide, piers, sodium lamps, two-way traffic. Its corridor is cleared.
2. **Ramps and interchanges** (`RAMPS`): every ramp is a curved one-way deck (Hermite between two roads, z eased between the
   heights of the roads at its ends; hub / arterial ends are at ground), with edge lights, lamps, a light-trail lane and a
   slip (speed-change) lane alongside the road at each elevated end. 36 ramps: hub exits (below), 4 slips at each crossing
   of a through highway with the ring (diamond), a four-loop **cloverleaf** where the ring crosses the east-west highway in
   the SW sprawl, a **stack** (two loops, the crossing is at 50 degrees) where the two through highways cross in the core,
   and on / off ramps down to the arterials at four core crossings (spaced 28 lots).
3. **Meridian bypassed.** `THROUGH`: the east-west highway (z 24) passes the hub's south-west side and runs on, the
   north-south one (z 30) passes its west side and runs on to the port (ramping down into the yard, as before); neither
   starts or ends at the hub. Three exit pairs leave the hub's outer kerb at the kit's S, W and E exits (kit 14.2: S (0, -158),
   W (-158, -30), E (158, -30) kit units, scaled to the hub kerb, 52 BU: (0, -52), (-52, -10), (52, -10)), each with an
   on-ramp and an off-ramp to the nearest through highway. The freight rail (`RAIL_WEST`) now comes in from the west
   along the fort's north side at the level of the train bay, passes the north gate (z 0.7), then bends north-east to the
   port; the deck climbs only after the gate. The hub's truck ring is untouched.
4. **Realism diagnostic**: see below (A/B on one night hero frame, `D:\rc_scratch\city_all_corps\realism_ab.jpg`).

### Realism A/B (one night hero frame, 3840 x 2160, `D:\rc_scratch\city_all_corps\realism_ab.jpg`; frames in `ab_a/ ab_b/ ab_c/`)

| | Settings | Median | Under 0.10 | Over 0.85 | Spread | Render |
|---|---|---|---|---|---|---|
| (a) | current: 32 spp, 28 mm | 0.155 | 30.3 % | 0.23 % | 0.339 | 225 s |
| (b) | 80 spp (not 128: 128 would be about 13 min, over the 10 min batch rule), OIDN with albedo + normal guiding (`CITY_AB=b`), bloom x0.5, no vignette, district glow tint -40 %, toe capped at 2.0 (night never needed more than 1.0; the contrast cap applies to the day) | 0.155 | 28.4 % | 0.28 % | 0.328 | 476 s |
| (c) | (b) + 50 mm lens from 1.79x further back (`CITY_AB=c`) | 0.155 | 28.0 % | 0.39 % | 0.347 | 491 s |

There is no grain in the night post (the day and the mainline have none either), so "grain off" changes nothing. Judge the look in the sheet.

## Layout A2 (round 4: the designer-approved city plan "Horseshoe Bay A2", 2026-10-16)

The 3D city is rebuilt from `docs/concepts/city_planner/city_A2.json`. The legacy diamond-map pipeline is kept
(`CITY_LAYOUT=legacy` selects it); `city_preset.LAYOUT_MODE` defaults to `a2`.

**Scale.** 1 lot (100 m) = U = 6 BU, so 1 BU = 16.67 m and the plan's 20 km square is 200 lots / 1200 BU, the lot count of
the old map plus ring (about one building per lot). The hero camera distance stays about 1100 BU. Lot x = X / 100 + CX,
lot y = CY - Y / 100 (lot y still points south); world BU = (X, Y) x 0.06. `city_rules.ab` becomes (a, b) = (east, north) in lots.
The sea is now BELOW the street (`WATER["z"] = -1.2`; the coast is a quay); the drowned quarter sits behind its dams.

**Files.** `zoning_a2.py` (JSON to `zoned_a2.json` + `a2_fields.npz` + `zoning_map_a2.png`: the raster of cell classes, districts,
urban factor `u`, the Old City / corp buildings, the lagoon cells), `city_world_a2.py` (ground, parks, suburbs, industry,
informal housing, street glow, arterial traffic, sea, bed, drowned quarter, dams / barrier / walls / glyphs),
`city_transit_a2.py` (roads, interchange ramps, rails, stations, port, airport). `city_build.py`, `city_render.py`,
`city_rules.py`, `city_preset.py` carry the A2 switches (water-mask image for the fog, sea glow by water cell, camera).

**Taken from the JSON.** Ocean, lakes, rivers and canals (water cells); the drowned quarter, its two dams, the Bay Barrier
leaves and the sea walls; the 7 district polygons (Old City = REBEL_CELL in the sprawl palette) and the 6 HQ positions
(the colour-influence centres; the own polygon is boosted x8); R1 / R2, the 6 motorways, 3 truck roads, the arterials
(ground traffic, corridors cleared), all 21 interchanges with their plan ramps (cloverleaf / stack / diamond), the
freight main (viaduct at the Meridian HQ's north flank, down to the port terminus), the 5 commuter lines, 3 metros and 45
stations (tunnel runs cut), the Port of Meridian (terminal, 5 piers with gantry cranes, ships between them, yard tracks),
parks, plazas, cemeteries, industry, informal housing, the airport (runways, terminal), the spaceport (Orbital pad), corp
walls and gates, markets and the arcology / megastructure / stadium / power / datacentre / hospital glyphs.
**Not mapped:** terrain hills (the city is flat), the undercity, drone corridors, ferries, checkpoints, neighbourhood
names, the offshore wind farm, universities / schools / churches / water / sewage / recycling glyphs, the Westmere
reservoir's shoreline detail, commuter / metro tunnels (cut, no portals drawn). Road widths are exaggerated (28-40 m would
be 2 BU).

**Rules kept.** Colour by HQ proximity, the Rebel Cell as the sprawl-coloured centre, the organic suburb edge (value noise
on the R2 outline), lower suburbs (ring blocks, `sub_u` 0.32), facade / material variety (`building()` unchanged).
**Landmarks.** `LANDMARK_MODULES`: meridian and tethys are on (`meridian_landmark.py`, `tethys_landmark.py`; both ran
unchanged with the real context); Halcyon, Solace (x1.8), Orbital (needle spots) and Aurelian use the built-ins.
**Render.** Version (b): 80 spp, albedo + normal OIDN, bloom x0.5, no vignette, district glow tint -40 % (default in A2).
Hero camera: from the south over the bay, yaw 90, pitch 38, lens 28, dist 1090. The day sun azimuth is rotated -45 degrees
with the view (same angle to the camera as before).

**Tests (1920 x 1080, 80 spp, `D:\rc_scratch\city_all_corps\a2test\`).** Night median 0.155, 27.1 % under 0.10, 1.9 % over
0.85 (exposure 5.1, toe 1.85); day median 0.149, 41 % under 0.10 (p10 0: the contrast solve to the 0.39 spread crushes the
shadows), 0.05 % over 0.85. Render 75 s night, 46 s day (build 14 s). Known: the day sea is very dark; the Meridian /
Tethys modules were not re-tuned beyond a look; the north horizon is flat ground in fog.

### Layout A2, designer pass 2 (terrain, bay character, density, roads, day), tests in `a2test2\`

- **Terrain** (`terrain_a2.py`, `CP.TERRAIN`): a height field H (BU, one value per lot cell, plan grid + 170 cells of margin) from the JSON
  hills (x1.5), seeded foothills (from the outer ring) and ridged mountains (to about 300 BU at the far edge, a horizon ridge),
  beaches (a slope into the water), cliffs on seeded stretches outside the city, flat rigid zones (HQ discs at the hill's own height, port,
  airport, spaceport). The street level sits 1.2 BU above the sea (sea = 0). Every vertex of the city is lifted by H(x, y)
  (`city_build.Acc.obj`, `TERRAIN_FN`): buildings, decks, piers and lamps follow the ground; landmark labels, crowns and key spots
  are lifted too (the night beams keep their shape). No building above slope 0.30 or H 42. Ground tiles follow H (1 / 2 / 4 cell LOD).
  Roads and rails therefore ride the terrain at constant clearance (viaduct-like piers, smooth grades); cuttings and tunnels were NOT built.
- **Bay character** (`city_bay_a2.py`): a sand strip + surf line on the plan's coastline (hides the cell staircase), a lit promenade lamps on the
  city coast, 7 marinas (pier + moored boats + end beacon), 10 cargo ships at anchor (anchor lights), 6 ferries on the 3 plan routes with
  wakes, 28 channel buoys, a lighthouse on the most exposed headland (key spots, not a landmark beam), gate towers + signal lights + swing
  gates at the Bay Barrier lock, lamp posts along the causeway, a fort island and a park island (a shoal rises under each).
- **Density**: suburbs now fill out to the foothills (`outer` field, fading to 34 cells past R2), half the suburb cells are 2x2 sub-lots,
  fewer merged blocks, brighter windows; the districts use a street period of 5 cells.
- **Roads**: deck edge light x0.38, lane lights x0.72 and thinner (decks, not ropes); rail glow x0.5.
- **Day**: median target 0.25, contrast cap 2.0, shadow lift 0.10 (p10 0.11); a BLUE sea (body colour + sky reflection; clear only over
  the drowned quarter).
- Values (1920 x 1080, 80 spp): night median 0.155, 27.3 % under 0.10, 0.57 % over 0.85; day median 0.250, 8.6 % under 0.10, 0.02 % over 0.85.
