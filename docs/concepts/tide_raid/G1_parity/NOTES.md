# G1 parity: the live Godot raid city against the P3 golden plates

Branch art/tide-proto @ a3134ab8 (D:/rc_art/godot_look_tide). Not merged, nothing posted to the mailbox, nothing committed in art-pass.

## Verdict (honest)
Numbers are inside the bar. The picture is NOT yet indistinguishable at a glance. Metrics are on the plan frame, whole frame (tolerance in brackets): luma +0.2 % (5), saturation +0.7 % (8), warm share -2.5 % (10), light points +3.2 % (15), street-reflection energy -2.1 % (20). Baseline was luma -15 %, sat -44 %, warm -78 %, lights -64 %. Misses: top band warm -29 % (far city has less sodium than the plate); hue-histogram L1 0.175 (not small: Godot carries more magenta/violet and less teal-blue than the plate); mean-abs squint L1 0.136. See "Remaining gaps". Judge with side-by-sides in final/ and running_sheet.jpg, not the numbers.
Metrics compare against a city-only target: the plates own offline pipeline run on the same Godot capture, with the plates Blender light-spill layer, with no beams, UI or pressure layers (make_city_target.py). The raw plate also holds beams, HUD and cards that the live city lacks.

## What was built
- Parity harness (tools/look_parity/): parity_capture.gd (plate camera, --still, --perf with GPU timers, --g1-debug/--g1-off/--g1-level/--grade look-dev switches), run_capture.sh + gpu_lock_run.py (GPU lock per batch, run_windowed only), parity_compare.py (side by side, heatmap, per-band luma/sat/hue/warm/lights/reflection, squint rows), make_city_target.py, tune.py/variant.py, make_report/make_perf/running_sheet/side_by_side. tide_proto_lab.gd gained --plate-cam so the beam prototype runs at the plate camera.
- City grade in the post (shaders/city/city_grade.gdshaderinc, config scripts/city3d/city_grade_config.gd + content/config/city_grade.tres, applier city_grade_look.gd): tone (sat 1.5, pow 1.1, dim .95), warmth field (baked plate map, procedural fallback), warm/cool tint and lift, local-contrast light recolour by district, sodium lamp lattice (baked plate lattice) with pools on street and neighbours, wet-street reflection (screen taps plus analytic lamp streaks, puddles, ripple, sky sheen), teal water via class tag, baked plate light spill, hero glow, HOME beacon and four rooftop cones, depth haze, 3-sigma bloom, rain, ACES, vignette/fringe/scan/grain. The grade takes the map look + veil as its input (as the plates did).
- Hero facades (8) and 15 wordless signs: facade quads from a baked set (hero_facade/sign_facade shaders, city_facade_look.gd, content/look/city_facades.tres), depth-matched to the wall.
- 2D finish (tilt-shift, fringe, vignette, scan, grain) as a canvas shader on the city view (city_finish.gdshader, wired in neon_city.gd).
- Class tags in ROUGHNESS (street 0 / land+sea .15 / park trees .30 / building 1) via ground, water and park-kit changes; terrain height texture for the street mask.
- Test: tests/unit/test_city_grade.gd (8 tests, manifest tier fast). Also ran unchanged and green: test_art5_city_integration, art3_6w_raid_city, city_shaders, city_water_look, city3d_grid, hq_b_city, hq_m14_12q_raid, hq_aaa_state_gate, aaa_street_look, id_capture, city_map_sweeps, art6_acceptance, city_a2, city3d_model. The FULL suite was not run (build runs it at merge).

## Quality toggle and perf (perf.md)
Tier 0 = level 1, tier 1 = level 2 (+ wet reflection, shafts, neighbour pool glow), tier 2 = level 3 (+ bloom, rain, 2D finish); config enabled=false is the old post. City GPU p95 (RX 6700 XT, machine shared): legacy 9.57 ms, level 1 9.74 (+0.2), level 2 11.16 (+1.6), level 3 11.57 (+2.0). Per feature at level 3: reflection/pool/shafts group +0.4, bloom +0.8, rain +0.8; each is under 1.5 ms. Wall-clock is vsync capped at 16.7 ms mean (p95 about 17.4 vs 18.2 legacy).

## Files (branch)
scripts/city3d/{city_grade_config,city_grade_look,city_facade_look,city_facade_set}.gd, city_materials/city_view_3d/city_water/city_park_kit.gd (tags, hooks), scripts/ui/kit/neon_city.gd (finish material), shaders/city/{city_grade.gdshaderinc,city_finish,hero_facade,sign_facade,facade_common.gdshaderinc}, city_post/city_ground/city_water shaders, content/config/city_grade.tres, content/look/city_facades.tres, assets/look/{district_warmth,city_spill,lamp_lattice}.png, tools/look_parity/*, tools/raid_tide/tide_proto_lab.gd, tests/unit/test_city_grade.gd, tests/test_manifest.json, docs/DECISIONS.md.

## Remaining gaps
1. Not indistinguishable at a glance. The plate city is softer (Blender bloom and Cycles bounce); Godot keeps the toon ink and crisp roof outlines, so edges read harder and the lit roof diamonds read whiter.
2. Hue: more violet/magenta, less teal-blue in mid band; top-band warm -29 %.
3. Blue ambient is a baked plate layer (city_spill.png), correct only for this camera and seed; outside the frame it falls back to the mean. A real ambient/AO model is the proper fix.
4. Warmth, lamp lattice, facades and spill are baked to campaign seed 7 (city seed 5046707608688524560); other seeds get the procedural warmth fallback, no facades, mean spill.
5. Hero facades are a decent match (positions exact) but flatter than the Blender material; no shaft cones under facades (removed as asked).
6. Garden: crisper than before but trees read darker/noisier than the plate canopy; no green force-field cage or pressure plum (pressure layer is out of scope).
7. Beams, rings, tiles, heads are the earlier prototype, not tuned in this task; 04/05 side-by-sides show city only plus the prototype beams.
8. Street reflections are screen-space plus analytic lamps; no true planar mirror, so reflections of objects off-screen are missing.
9. Tide plates 06/07 not side-by-sided (06 4K only landed late; city identical).

## Spec items for build (out of my scope)
- Terrain-following 3D beam node, frame clock, shake hookup: the earlier P3_proto list still stands.
- Facade/lamp/warmth baking for arbitrary seeds: port plates pick_heroes (planar tall facades) and a deterministic cell hash; replace baked textures.
- Decide whether the grade replaces map mode for the raid view permanently (it currently hides the veil when graded).
- Settings: expose city_quality tiers mapping to grade levels.
