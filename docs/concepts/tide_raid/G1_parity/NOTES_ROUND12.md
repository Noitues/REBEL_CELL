# G1 round 12, branch art/tide-proto (D:/rc_art/godot_look_tide), commits 26f28c0e, dc40e96b (head dc40e96b)

Close-ups: closeups/r12/hotspots_vs_shibuya_r12.jpg (plan-camera crops and a zoom 3 hotspot next to the Shibuya, neon alley and Tokyo highway refs), closeups/r12/plan_squint320_r12.png (320 px squint, r12 | plate), final/01_plan_*, generality/seeds_cameras_sheet_r12.jpg. Only final/01 and the seeds sheet were refreshed (02-07 are round 11).

## Done
- Hotspots win at the plan camera: more screens (all tall walls over 18 BU in a hotspot, share 1.0, bigger: 26-50 % of height, up to 28 BU), roof screens on nearly all hotspot roofs (full roof width, also L / T / slanted), 3-4 hotspots per territory (4 asked, min traffic 0.4, 9 lots apart), colour haze (two additive fans per hotspot in its two neon colours, `city_neon_haze.gdshader`, one mesh), body tint (buildings in a hotspot lerp their base colour toward the hotspot colour, 40 % at the centre, via the instance buffer), street trees at the crossing corners with a green underglow (lit from below), wet reflection of neon: the existing wet-reflection taps now read neon-class pixels in their own colour (gain 3.0, `g1_neon_wet`).
- Background signage everywhere: blade signs on avenue-facing walls of buildings over 20 BU (45 % of walls, 9 colours weighted to the cyan / magenta pair with acid green, orange, electric blue), glowing roof logos (30 % of tall roofs), floating holo ads (scanlined, half the lines dropped and rolling, edge frame, gentle flicker) over towers over 60 BU (50 %), LED crowns on 80 % of towers over 40 BU.
- Value structure: side-street lamps 0.3, avenues 1, dense-core lamp scale 1.3 (outskirts 0.4); crowns brighter (gain 1.8). Rain streak opacity -30 % (rain_k 0.035 -> 0.0245).
- No pink in parks (unchanged), lamps stay dim amber lines, p1 / p5 kept.

## Metrics (plan)
luma p1/5/25/50/75/95 0.061 0.121 0.238 0.299 0.405 0.843 (plate 0.069 0.113 0.232 0.325 0.481 0.844); median rgb (67,74,124).
## Perf
Level 3 city GPU p95 11.16 ms (round 9: 11.07 ms; budget +1.5). Level 2 11.58.

## Gaps
- The hotspots read as bright clusters but the screens and haze skew white-cyan / white-pink (bloom and tone map wash the saturation); the grain from dithered spill is visible at close range. Not Shibuya's saturation.
- Hotspots cluster in the south-west core; the north half shows only roof logos and crown accents. Holo ads are present but hard to see at the plan camera. No full neon avenue strip.
- Avenues are still not clear continuous amber lines through the core (towers hide them).
- Tests: test_city_neon_kit, test_city_grade, test_city_lamp_plan still pass; no new tests for blade signs / holo (deterministic hashes, same pattern as the kit tests). Full suite not run.

## Slips
None on `python -`. An `rm -rf` of my own scratch perf folder (D:/rc_scratch/g1/r11/perf12) was used once; no foreign files touched; no background processes left.
