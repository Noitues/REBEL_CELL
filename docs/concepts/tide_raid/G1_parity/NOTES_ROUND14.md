# G1 round 14, branch art/tide-r14 (D:/rc_art/godot_look_tide), head c36377b2 (from r13 de4c3896; art/tide-proto and art/tide-neon-push untouched)

Everything is in r14/: compare_r12_r13_r14.jpg (plan, hotspot close-up zoom 3 and 320 px squint for each round), *_r14_before_after.png (before = r13, after = r14). final/ was NOT touched.

## Designer red-box bug (priority): FIXED
Cause: the hotspot light fans (two haze fans per hotspot, the crossing fans, the street spill pools) were additive and depth-write off, but far too strong: haze gain 0.16 on a 5-lot disc 10-24 BU above the street, crossings alpha 0.8 white / amber, spill 0.7 x 0.6. They summed to opaque-looking pale wedges. Now: haze gain 0.05, crossings 0.22 and tinted 80 % toward the hotspot colour (not white), spill alpha 0.3. All of them are in the additive material (blend_add, unshaded, depth-test on, depth-write never), so buildings behind read through. Close-up of the three boxes at the plan camera: designer_red_boxes_r14_before_after.png (box 3's remaining lilac is the district's own ground spill, not a fan).

## Brief
- Neon look of round 12 restored: DONE. `neon_r12` (default true) brings back r12's screens (white-hot frame, re-rolling blocks, scanlines, flicker, gain 1.7), the per-channel tone map and bloom in the district colour; `neon_r12 = false` is the r13 look; `neon_dither` (default false) selects dithered glows. Kept r13's grain removal (smooth glows), which does not change the screens' character. Compare: compare_r12_r13_r14.jpg, screens_r12_vs_r14.
- Holo bug: FIXED. `neon_holo_min_h` 60 -> 30 (share 0.25). Holos ON vs OFF: holos_off_vs_on_r14_before_after.png (`--no-holo` in the capture tool). New test: test_default_holo_threshold_is_below_the_tallest_real_building (threshold under 50 BU, a 45 BU tower carries a holo); the test city's towers are now 45 BU. test_city_neon_kit 9 pass.
- Fix 2 traffic: DONE. Highway / ramp dashes 2.2 BU long with 0.7 gaps, wider (0.28), brightness x2.2 over 0.75..1, tail red and head white; new avenue traffic (two dashes per lot per lane, red one lane, white the other, 1.6 gain). highway_traffic_r14_before_after.png.
- Fix 3 core value separation: DONE (moderate). District body tints (halcyon teal, meridian amber-brown, orbital blue, the Cell magenta, sprawl violet; 30 %), darker streets / land (ground_tint 0.15,0.17,0.27; land 0.2,0.25,0.42). Veil lift: `veil_k` exists but left at 1.0 (lowering the veil lifted the darks; p1 / p5 went up). core_districts_value_r14_before_after.png.
- Fix 4 contrast around screens: DONE. Hotspot buildings darken by 40 % at the centre and tint only 15 % toward the neon; wall halos 0.3. Screens keep r12 brightness.
- Fix 5 hotspot spread: PARTLY. 3 hotspots per territory per region (was 2); still concentrated in the core and the north tower cluster; NE and far SW are thin. Wet reflections of the neon: the existing wet path reads neon pixels (r13, kept).
- Fix 6 roof tiles: DONE. Share 0.42 -> 0.2 of roofs, width 0.22 -> 0.12 and varied 0.5-1.5x per building. low_district_roof_tiles_tints_r14_before_after.png. Not tinted to the roof colour (still the building ink).
- Fix 7 parks: DONE. Lawn and park edge near-black green; Solace blocks darkened x0.5, so the pale boxes in the seed-3 HQ park are dark now (seed3_r14.png, park_hq_r14_before_after.png). Canopy greens unchanged.
- Fix 8 water: PARTLY. Bay water colour near-black navy (0.002, 0.012, 0.045); bay and river close-ups bay_and_river / river_bottom_right. No new bridge light strings, the river is still thin (plan-data width spec from round 9 stands).

## Metrics (plan, bay corner masked by rectangle, so values differ from earlier tables)
r14 luma p1/5/25/50/75/95 0.046 0.069 0.173 0.271 0.374 0.770 (r13 on the same mask 0.043 0.066 0.174 0.278 0.385 0.781; r12 0.043 0.066 0.165 0.265 0.357 0.818). Median rgb (59,67,115); warm share all 0.043.
## Perf
Level 3 city GPU p95 12.38 ms (mean 11.72, p99 17.9 from one hitch), against 11.07: +1.31 ms, inside +1.5 but close; the avenue-traffic quads and fans are the additions.
## Tests
test_city_neon_kit 9, test_city_grade 13, test_city_lamp_plan 9, test_city_shape_kit 7 pass. Full suite not run.
## Slips
None. No `python -`; temporary worktrees in D:/rc_scratch/g1/r11 removed.
