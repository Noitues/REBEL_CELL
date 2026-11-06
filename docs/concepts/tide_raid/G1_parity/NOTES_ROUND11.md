# G1 round 11, branch art/tide-proto (D:/rc_art/godot_look_tide), commits 95898598, 80cafd97 (head 80cafd97)

Before = round-10 head 06fa2a1d, after = round 11. Close-ups in closeups/r11/ (*_r11_before_after.png), refs sheet closeups/r11/refs_vs_r11_sheet.jpg, generality/seeds_cameras_sheet_r11.jpg, final/01..07, metrics.md (round-11 table below), perf.md.

## Items
1. Neon hotspots: PARTLY (clearly better, still short of Shibuya).
   - Screens are emissive with content in the shader (`city_neon.gdshader` mode 1): a bright near-white edge frame, scanlines, a coarse animated block pattern that re-rolls about every 1.3 s per block, a slow gradient and flicker; emission gain 2.2 so the bloom picks them up.
   - Sign spill: two dithered halo rings on the wall round each screen tint the facade; a wide colour pool (14 BU) and a long narrow streak (26 BU) lie on the street in front. Dithered glow (mode 2) keeps the colour saturated while the coverage fades.
   - Hotspot crossings: intersection lots within 4.5 lots of a hotspot glow white or amber.
   - Close-ups: hotspot_r11_before_after.png, hotspot2_r11_before_after.png, refs sheet.
   - NOT done: lit-from-below trees in hotspots; the streaks are flat ground quads, not through the wet-reflection path (the existing wet taps do not see them); the hotspot is not yet the brightest region of its district at squint (screens are small against the 3 BU-high tall towers around them).
2. Street grid brightness: PARTLY. Facade wash gain 2.0 -> 1.3 and its height scale 3.0 -> 2.4 BU (a lower, tighter base glow); the avenue lines keep scale 1 (side streets 0.45). At squint (low_squint_r11_before_after.png) the street grid reads as lines in the low district; through the tall core the lines are still mostly hidden by the towers.
3. Contrast: DONE moderately. contrast 1.3 -> 1.4, saturation 1.66 -> 1.9, haze strength 0.18 -> 0.12, black level 0.07 -> 0.05, exposure 2.1 -> 2.2. Luma p1/p5 kept (0.058 / 0.112), p50 0.336 -> 0.295 (mids deeper, plate 0.325), bodies more saturated and less milky. The haze (depth haze in the post, nothing else) was the main whitening in the mid distance; reduced.
4. Shapes legible from above: DONE. Setback steps are bigger (tiers 0.55 / 0.82, widths 1.0 / 0.74 / 0.5, allowed from 20 BU); L and T have deeper notches; spires 0.2 of the height and thicker, with a bright tip; stepped roofs get a lit edge (cyan / cream / amber) on the seen edges; green rooftop gardens on 12 % of low flat roofs (green only). Non-box share about 45-48 % per district in config (was 40-50 % weights, but the chosen plain share was higher). Close-ups: shapes_r11_before_after.png, shapes2_r11_before_after.png.
5. Low-building amber squares: DONE. Global lamp gain 0.75 and a smooth local-mean-height scale (mean roof within 5 lots, 14..42 BU blends 0.4 -> 1, config `lamp_global_gain`, `lamp_low_scale`, `lamp_area_h`, `lamp_area_radius_lots`), plus the lower facade wash. Dimmer warm strings, same lamp count; avenues stay brighter. Close-ups: low_r11_before_after.png (full size), low_squint_r11_before_after.png (squint).
6. Housekeeping: final/02..07 recaptured (02 / 03 from the daemon moment, 04 / 05 from the home moment, 06 / 07 are the city alone: no aftermath / lost-city overlay exists in the lab). New tests: test_city_neon_kit (6: hotspots deterministic, capped and spaced, plan deterministic with screen and glow modes, gardens green not pink, pocket pick deterministic and spaced, pocket lamps and path), registered in tests/test_manifest.json (fast). test_city_shape_kit (7) now clamps roof boxes into the lot. Targeted tests pass: test_city_neon_kit 6, test_city_lamp_plan 9, test_city_shape_kit 7, test_city_grade 13. The full suite was not run.

## Metrics (plan, round 11)
luma p1/5/25/50/75/95 0.058 0.112 0.236 0.295 0.390 0.813 (plate 0.069 0.113 0.232 0.325 0.481 0.844); median rgb (65,73,122); warm share top / mid / bottom 0.006 / 0.040 / 0.155, all 0.067 (plate 0.153; the lamps are deliberately dimmer). Seed 3 p5 0.121, seed 19 0.108.

## Perf
Level 3 city GPU p95 11.06 ms (round 9: 11.07 ms; level 2 11.58). Within budget.

## Gaps
- Hotspot is not the brightest place at squint; no lit-from-below trees; streaks not in the wet-reflection path.
- p75 0.390 is now well under the plate (0.481): the mids and lamps are darker; warm share all 6.7 % vs 15 %.
- The plan camera still shows the shapes mostly as tops; only the close-ups show the steps clearly.

## Slips
None this round: every command was checked for `python -`; all Python ran from files. One cleanup command was refused by the auto-mode classifier (it combined a wildcard-free but odd `rm` loop); I did not retry it. The temporary worktree in D:/rc_scratch/g1/r11 was removed. No background processes left.
