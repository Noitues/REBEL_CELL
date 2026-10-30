# final_proposed: the tide raid city on art/tide-r42

Branch **art/tide-r42**, head **bbdc20ae** (r41 6cb8bd29 + r42 work + the merge of art/city-test-fixes a76b09b6) (D:/rc_art/godot_look_tide). Seven beats in the same format and names as `../final/` (side_by_side.png: golden plate on the left as is, Godot on the right; squint.png: 320 px and 4 px blur pairs), plus `old_vs_new.jpg` (final/'s Godot half next to this one, per beat). The side-by-side labels read "plate r42 ..." on the left by the tool's fixed text; the left image is the unchanged golden plate.

## How they were made
- 01: `tools/look_parity/parity_capture.gd` plan camera (run_capture.sh, seed 7, plate camera zoom 1.5 about plate px (722,500)); 06 and 07: the same city-alone capture (as in the old final).
- 02 and 03: the P3 lab `tools/raid_tide/tide_proto_lab.tscn --moment=daemon --capture --plate-cam`, frames 60 and 150 (as labelled in the old final). 04 and 05: `--moment=home`, frames 70 and 86.
- Side-by-side and squint: `tools/side_by_side.py` (same tool as before). The lab wrapper is `labrun.sh` here (GPU lock + run_windowed.py), the sheet maker `oldnew.py`.
- All 7 beats rendered; none failed. The raid FX (ribbon, HOME ring, burst) draw correctly over the new layout.

## Config switches that differ from the defaults of the old final
- `CityView3D.art_look = true` (the default; the street netrun's route_rig sets it false). It gates the corporation colour (CityCorpColor), the corp neon, the r6 look and the park / apron dressing.
- `CityConfig.r6_look = true`, `r6_grade_level = 0` (the cel + ink post, no realism grade; the old final ran grade level 3), `r6_bloom` 0.3, `r6_saturation` 1.3, `r6_contrast` 1.15, ground multiplier dark grey-green, bay `r6_bay` deep blue on the OuterLand plane.
- `corp_color_on = true` (cap 0.65), `neon_holo_share = 0` and `neon_holo_min_count = 0` (holos off, ART CALL 39), `a2_walls_draw` true (wall routes draw as highways, the Solace ring draws nothing), `plan_ramps_on`, `park_dress_on`, `apron_dress_on`.
- Layout: P0 + P1 rules from art/city-layout-p0 and art/city-layout-p1 (in the branch via merges), plus the r41 edge-as-shore rule and the r42 90 m corridors.
- Motion: `CityMotionLayers.plan_hide_bu_per_px = 0.15` (set by the city view): the far sky-car dots and lane guides hide at plan zoom.

## Perf
Level 3 city GPU p95 10.15 ms (mean 7.67), limit 12.57 (perf.md, round 42).

## Test status (one branch, green end to end)
- Full suite `python tools/run_tests.py` on bbdc20ae: **4070 tests, 0 failing, 117 pending, PASSED** (4 shards, 2111 s; log D:/rc_scratch/g1/r42_full3.log).
- Schema smoke test: PASS. validate_content: PASS (3172 resources).
- The first full run found two regressions of mine (shape-kit low-rise slant, spike count with the wider corridors) and a schema-smoke pin on the 45 m corridor; all fixed in tests / config before the green run.

## Merge order
art/city-lint, then art/city-layout-p0, then art/city-layout-p1, then art/city-test-fixes (merged, green), then art/tide-r42. (r42 contains P0 and P1 by merge; the test fixes touch test_city_motion's weakened road-count assertion.)

## Open items
- The tall teal tower on the bay apron, the pale slab at the park / core edge and the glass cluster are Site buildings (a Site keeps its lot); they need a build decision, not a view fix.
- The grey diamonds in the north park (isolated lot quads of the chunk ground mesh; not found: hidden Parks, ParkDress, ApronDress, the grade, none removes them) and the grey slab beyond the dressing band.
- The layout P2 list, and the north park's featureless interior at plan zoom.
- The netrun-look decision: whether the street netrun adopts the r6 / corp-colour look; today `art_look = false` keeps it on its own look (the build hand-off must carry the gate).
- Honest note: against the golden plate the city is a different style (cel + ink, corp colours) by designer ruling, so the side-by-sides are not a parity claim.
