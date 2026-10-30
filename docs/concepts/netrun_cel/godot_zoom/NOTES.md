# Netrun zoom prototype in the engine (Godot, real CityView3D)

Designer approved the Godot zoom prototype on 2026-10-30 (DIRECTION_REVIEW cohesion answers: the netrun is the city's look zoomed in, built from the real procedural city, with procedural detail added per zoom). v2 (Blender) proved the layout but did not look like the city, so this round runs in the engine: one camera path over the live r43 city (seed 7, HQ raid page, `art_look`, r6 cel + ink), at the same block as netrun_cel v2: the boulevard at lot rows j -26..-24 by the Solace park.

Godot work: `D:/rc_art/godot_look_tide`, branch `art/netrun-zoom` (from art/tide-r43 e2c9976c). Head: see the report. Capture tool: `tools/look_parity/nr_zoom.gd` (`nr_zoom.sh` runs it under the GPU lock and `run_windowed.py`).

## Files
| File | What |
|---|---|
| `stage_1..5_base.png` | the 5 stages, layers OFF (the unchanged r43 look), 1920x1080 |
| `stage_1..5_layers.png` | the same cameras with the per-zoom layers ON |
| `zoom_strip.jpg` | the five stages, layers on (top) and off (bottom) |
| `ref_vs_street.jpg` | golden street_overview next to stage 5, golden hq_rebel_cell_overview next to stage 4 |
| `squint_stage_N.png`, `squint_plate_street.png`, `squint_sheet.jpg` | 1/16 area reduction plus blur, back up to 960x540 (the netrun_cel recipe) |
| `zoom_motion.gif` | the camera move, 75 frames at 12 fps, 480 px wide, 6.5 MB (frames written by a screenshot loop under run_windowed, not Movie Maker: Movie Maker would also record the model build) |

## The camera path
Real `CityIsoCamera` poses, same city, same objects at every stage.
1. City: the r43 plan camera (ortho 394.6 BU, 4.9 px per BU).
2. x2: ortho 197 about the block (9.7 px/BU).
3. District x3: ortho 131.5 centred on the block, iso yaw 135, pitch 40 (14.6 px/BU).
4. Near street: perspective, fov 62, eye 20 BU (40 m) over the east end of the boulevard, looking west along it, pitch 20.
5. Street: perspective, fov 62, eye 5 BU (10 m) over the boulevard, 1.4 BU off the south kerb, pitch 5.
Units: 1 BU = 2 m, a lot = 6 BU. The motion gif dollies the focus point from stage 3 into 4 and 5 (log-space distance and field of view); an eye lerp first swung the camera up to the sky, which is a path error, not a look break.

## Where the real look breaks (layers OFF), per stage
- Stage 1 city: no break; it is the r43 plan. Note `building_lod` is hysteretic: the same camera gives lod 1 or 0 depending on where the camera came from (the layers run starts at lod 0 after stage 5). Cosmetic at this zoom.
- Stage 2 x2: the window lattice (pitch 3.0 x 3.6 BU, windows 0.8 x 0.7 BU, about 15% lit) reads as scattered yellow dots; the building LOD flips from 1 to 0 here (window grid and ledges appear). No ground-floor detail. Ink is fine.
- Stage 3 district: windows still sparse random squares; the per-triangle tone jitter shows as a triangle mosaic on every tower; avenue strips read as flat neon slabs on dark ground; no shopfronts, nothing on the street between the buildings and the park.
- Stage 4 near street: the facet jitter stretches into large triangles on the tall prisms; walls are huge and blank; ink is thick and wobbly (the ortho ink formula 0.6 + 160 / ortho gives 3.9x at the perspective camera's ortho of 48); the street lamps are a 1.5 BU cube base with a pole and a panel, sized for plan readability, so they read as toys; trees are low-poly blobs with fat ink; the ground is flat dark asphalt with one faint lane line; no sky (towers fill the frame); no haze (the shader's depth haze only runs at look_blend > 0).
- Stage 5 street: all of the above, plus: the near plane is 1 BU (2 m), so a wall closer than that is cut (my first eye 1.5 BU from a wall showed a flat wall filling the frame; moved off it); a black stipple band runs along the far kerb (the dithered ground / shadow edge, visible only at a low angle); no puddles or reflection; no storefronts, signs at street scale, or kerbs; lit windows are a handful of small squares on 80 m towers.
- Not seen as breaks: no LOD pop in the path frames beyond the 1 to 0 flip at stage 2, no clipping of the helix or park at these cameras, no texture swimming.

## What each layer does (all view only, behind `CityConfig.zoom_layers_on`, default false)
Code: `CityZoomPlan` (pure, scripts/city3d), `CityZoomLayers` (view node), `city_zoom_layer.gdshader`, `city_zoom_haze.gdshader`, and a few uniforms in `city_building.gdshader` (all multiplied by `zl_on`, 0 unless switched on). Switch: `CityView3D.set_zoom_layers(bool)`; it starts from the config flag. Tuning is `zl_*` in CityConfig (fade scales, shares, sizes, gains).
- Fade by screen scale, not by distance: every class fades in by pixels per BU at the fragment (`ppb`), `smoothstep(in.x, in.y, ppb) * (1 - smoothstep(out.x, out.y, ppb))`, the same maths for the ortho and the perspective camera. So a building shows the same things at every zoom, only more of them; below 7 px/BU at the focus no geometry is built at all (stage 1 costs nothing and is identical).
- Seeded by building: every choice is a hash of the prism key (`CityMeshKit.hash01`), never an RNG stream and never the camera. The camera only selects which buildings are dressed (a rect). Tested.
- Window panes (shader): from 16 to 36 px/BU the same window cells grow to 2x, split by a frame, a centre mullion and a transom, each pane gets its own light, unlit glass gets a sheen; the lit share rises (+0.18, and +0.3 more at street level fading out by 14 BU); the facet tone jitter calms to 20% and fine panel grime plus floor lines replace it. Same cells, same lit hash: a window stays where it was.
- District strip (class strip, 8 to 14 px/BU in, gone by 42): a lit ground-floor strip in a shop colour on the first shop wall of a building that fronts a street. Hands over to the bays.
- Roof signs (8 to 14 px/BU): a board on posts on tall roofs (share 0.5, 36 m and up) with glyph bars; the frame is lit on neon buildings only, the board is a dim tint, never black.
- Storefront bays (24 to 38 px/BU): on every street-facing wall, bays of 1.8 to 2.6 BU: dark frame, a lit window in a shop hue (amber, cool white, pink, cream, cyan, green), two shelves with goods blocks, a slanted two-tone awning on half the bays, a sign board with a frame and glyph bars; 16% of the shop walls get a ribbed shutter instead. Sign colour is the building's corp colour (`CityCorpColor.sign_color`) or a neon palette colour from the existing `CityNeonKit.PALETTE`.
- Blade signs (14 to 26): on 40% of the street walls, a 1.1 x 4.4 BU board standing out from the wall, frame and glyphs.
- Props (16 to 30): pavement and kerb strip along each street wall, air-conditioner boxes (with a vent line) and a drain pipe up the first floors, a lamp post with a warm head and a ground pool on one wall in three.
- Wet street (18 to 34): each lit shop window casts a streak on the ground in front of it (additive, fading out over 5 BU), the lamp pools do the same; and a low violet ground haze (additive, 1 BU high) in front of the shops.
- Neon is selective: `zl_neon_share` 0.34. Only those buildings get lit sign frames and a lit blade sign, roof sign and awning glow; the rest get unlit (dim) signs and weaker shop windows. (Tested: share within 0.04 of 0.34.)
- Ink: in perspective with the layers on, the ink width is `r6_ink_width * 1.6` instead of the ortho formula.

## Squint (1/16 area, blurred; `squint_sheet.jpg`, layers on)
- Stage 1 city: pass. The park and helix read as a lighter mass against the tower field.
- Stage 2 x2: weak pass. The helix and park read; the tower field is a noisy mass.
- Stage 3 district: pass for the park against the towers; the street between them is a dark wedge, no route (the route is not part of this prototype).
- Stage 4 near street: fail. One big orange ad wall (an existing neon screen) is the whole read; the street is a dark wedge.
- Stage 5 street: weak. The dark street wedge, a cyan ad and the park read; there is no bright storefront band as the lowest horizontal, which the plate has (compare `squint_plate_street.png`). The layers give small shapes that vanish at this scale.

## Perf (GPU time of the city viewport, 500 frames, run_windowed, 1920x1080; limit 12.57 ms)
| Stage | layers | gpu city mean | p95 | p99 |
|---|---|---|---|---|
| 3 district | off | 4.15 | 8.57 | 9.49 |
| 3 district | on | 4.22 | 9.13 | 9.55 |
| 5 street | off | 4.16 | 6.79 | 6.97 |
| 5 street | on | 4.19 | 6.80 | 7.23 |
Both stages are under the limit with the layers on (p95 9.13 ms at stage 3, 6.80 ms at stage 5). Logs in `D:/rc_scratch/nrzoom/perf/`. The quad count per rebuild was not logged (CityZoomLayers.quad_count exists for it).

## Tests
- New: `tests/unit/test_city_zoom_layers.gd`, 9 tests, in `tests/test_manifest.json` (fast tier): off by default (config script, shipped config, a new view, the shader uniform), the switch drives only the shader uniform, the same dressing whatever the rect (deterministic per building id), no quads without a street or a rect, far and near classes follow their own rects, neon share about 1 in 3, dim signs on non-neon buildings, the fade table, no geometry below the build scale.
- Targeted run (coordinator's rule for art-pass: no full suite, no schema smoke, no validate_content): `python tools/run_tests.py -j 2 --select` the new script plus test_city_shaders, test_city3d_model, test_aaa_street_look, test_art7_netrun_city, test_city_grade, test_city_lawn_ground, test_tide_raid_grade, test_city_motion, test_m14_perf_far_lod, test_hq_b_city, test_art5_city_integration, test_hq_run_city, test_suite_integrity (manifest) and test_city_neon_kit: 16 scripts, 179 tests, 0 failing, 9 pending, PASSED (log `D:/rc_scratch/nrzoom/targeted.log`). The full gate is build's merge.

## Gap to the golden plates (honest)
Layers on, the street is better than the base but nowhere near `street_overview.png` or `hq_rebel_cell_overview.png`.
- The towers are 40 to 80 m featureless prisms; the plate's facades carry hundreds of small panels, balconies, pipes and signs up their whole height. Ours add detail to the first 3 to 7 floors and a window pane pass above; the upper tower is still big flat blue.
- The plate's brightest horizontal is a continuous storefront band with neon signs and reflections on wet street; ours is a few lit bays at the foot of some towers, small against 80 m walls, and the street is mostly flat dark asphalt. The wet effect is additive streaks, not a reflection: no mirror of the towers, no puddles, no light streaks from traffic.
- Signs are small flat quads with glyph bars; no kana, no hierarchy of big blade signs over the street, no hanging lanterns or wires. Roof clutter (water towers, HVAC, catwalks) is missing.
- Palette: the plates are warm magenta, pink and cyan neon on near-black; the city's r6 cel look is blue-violet towers with lime and teal. Pink is only in a few signs.
- Existing city props are sized for plan readability: the lamp (cube base and pole) and the blob trees read as toys at street level; the layers add small lamps beside them but do not replace them. Replacing or scaling them is a change to existing views and was out of scope.
- No sky or skyline silhouette at street level, and no ground haze beyond a violet fog; the plate has a lit haze that separates the depth layers.
- The camera is a hand-placed pose on one block; stage 4 is dominated by one existing neon billboard.
- The HQ netrun set piece (authored helix and plaza) is not in this prototype.
Proposed next steps for a street that reads: facade detail over the full tower height (a second, finer panel shader and balcony and pipe geometry per floor band), scale or replace the street props at street zoom, a real wet-ground reflection (screen-space or planar mirror of the emissive layer), and a bigger, brighter storefront band with sign hierarchy.
