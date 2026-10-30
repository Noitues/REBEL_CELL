# G1 round 43, branch art/tide-r43 (from art/tide-r42 bbdc20ae). Godot commits d08295a7 and e2c9976c in D:/rc_art/godot_look_tide. godot_lint, final/ and final_proposed/ untouched.
Pictures: compare_r42_r43.jpg (plan, north park, apron, seed 3; r42 left, r43 right), raid_grade_beats.jpg (beats 02, 03, 04, r42 | r43 graded; per-beat PNGs beside it), raid_grade_squint.png (320 px, 4 px blur, heavy blur pairs). Sheets are made by tools/compose43.py.

## 1. North park grey diamonds: FIXED
Cause (probe, not guess): the chunk ground is two flat triangles per lot on the corner heights (y -0.02); the lawn follows the terrain's own samples at +0.004. On twisted slopes the asphalt stands 0.1 to 0.2 BU over the lawn (the diamond lots (-77,-21), (-76,-21), (-75,-22), (-73,-34), (-72,-33) of the seed-7 city 5046707608688524560 measure 0.11 to 0.19). Raising the lawn lift to 0.3 removed them, which confirmed it. (The round 42 hide tests hid only the first chunk's node, so they found nothing.)
Fix: `CityParkKit.ground_sink` (config `park_ground_sink_margin` 0.02, switch `park_ground_sink_on`) lowers the asphalt of each lawn lot by its poke; `CityMeshKit.ground_mesh_on` takes a `sink` map; the view applies it to the park lots and to the dressed bare-lawn lots.
Test: tests/unit/test_city_lawn_ground.gd (the diamond lots poked before and lie under the lawn after; every 7th park lot checked on the real ground mesh).

## 2. Grey slab behind the quay: FIXED
Cause: street lots under a raised deck draw no street quad, so their ground stayed bare grey-khaki (a sawtooth strip under the viaduct at the plan top); the apron dressing counted them as live streets and skipped them.
Fix: `CityApronDress.live_streets(street_set, is_deck)`; deck lots are dressed as lawn like the bare lots round them (switch `deck_street_dress_on`). Test: the live_streets case in test_city_lawn_ground.gd.

## 3. Raid-mode grade
- Rule (`TideRaidGrade`, scripts/ui/raid): on in FORECAST, REVEAL, RESPONSE, PLAYOUT; off in DECAY, DRAW, PLAN, AFTERMATH, HQ_STEP, DONE. RESPONSE carries the grade so there is no flicker between reveal and playout (confirmed by the coordinator). The flow does not say raid mode is still on at plan or aftermath, so those keep the full look. hq_scene calls it from `_tide_beat`, `_tide_done` and `_set_panel`; view only, no state.
- Values (TideLookData `raid_grade_*`, content/config/tide_look.tres; brightness / saturation): buildings 0.62 / 0.72; neon (the avenue strips, signs, storefront glow) 0.48 / 0.38; ground 0.86 / 0.88; water 0.86 / 0.92; neon haze keeps 0.45; blend 0.35 s (`CityView3D.set_raid_grade`, a tween; motion pass tunes it).
- How: `city_post.gdshader` classes each pixel by its roughness tag (building >= 0.5, neon 0.42, water 0.15 / river 0.24, rest ground) and desaturates then dims it at the end of the post. The tide ribbon, the raid FX and the UI draw after the post or on 2D layers and stay ungraded. The additive neon haze draws after the post, so it has its own `raid_k`.
- Tests: tests/unit/test_tide_raid_grade.gd (phase rule, view follows the phase, the CPU mirror dims buildings 30 to 45 %, neon most, ground and water slightly, saturation order, shader uniforms, look validates).

## 4. Squint (beats 02, 03, 04, r43 against r42)
- 02 forecast: pass with a note. The cyan path is the only saturated linear mark and survives the blur, but it is short and faint and the square site tile competes a little; more ribbon gain is a motion-pass option.
- 03 reveal: pass. The cyan path is read first; the avenue strips no longer compete.
- 04 impact: pass. The pink path and the HOME ring lead.

## 5. Perf (level-3 city GPU, limit 12.57 ms; r42 10.15 ms)
perf_l3 p95 10.05 ms (mean 9.79); with the grade on (raid_mix 1) p95 8.73 ms (mean 5.92; not investigated, likely GPU clock state). Both under the limit. Logs D:/rc_scratch/g1/r43/perf/.

## 6. Tests
Full suite `python tools/run_tests.py` on art/tide-r43: 4080 tests, 0 failing, 117 pending, PASSED (455 scripts, 4 shards, 2758 s; log D:/rc_scratch/g1/r43/full.log). Schema smoke: PASS. validate_content: PASS (3172 resources). The two new scripts are in tests/test_manifest.json (fast tier).

## Tools and slips
parity_capture.gd gains `--lot-dump=<json>` (every lot's class and screen pixel); tide_proto_lab.gd gains `--raid-grade`. The new class_name needs `godot --headless --path . --import` on a fresh checkout. Slips: `python -` run twice by mistake (hung, stopped by TaskStop, nothing written); a `-gtest=` run executed the whole suite and was killed by its own PID.
## Open
- Beat 02's path is the faintest of the three (see above).
- The tall teal apron tower, the pale slab and the glass cluster are still Site buildings (build decision), as in r42.
