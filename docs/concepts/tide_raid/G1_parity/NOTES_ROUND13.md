# G1 round 13, branch art/tide-proto (D:/rc_art/godot_look_tide), head de4c3896

Close-ups: closeups/r13/hotspots_vs_shibuya_r13.jpg (plan crops and a zoom-3 hotspot next to the Shibuya, neon alley and Tokyo refs), closeups/r13/plan_squint320_r13.png, final/01..07 (all refreshed; 02/03 daemon-lab frames, 04/05 home-lab frames, 06/07 the city alone), generality/seeds_cameras_sheet_r13.jpg, metrics.md, perf.md.

## Done
1. Saturation kept: DONE. The post's tone map is hue-preserving for the neon class (the filmic curve acts on luminance, RGB scaled, clamped by the max channel: no per-channel white clip). Bloom reads the neon's own colour (a class test per tap) instead of the district light colour. Screen gain 1.7 -> 1.2, neon_screen_gain 1.25 -> 1.0. At squint the hotspots read cyan / magenta / green / yellow clusters, not white. Remaining pale spots: the lighter content block and the frame (35 % toward white, by design).
2. Dither grain killed: DONE. Spill, haze, crossings, storefront strips, wall halos, tree underglow and avenue lines are all smooth additive radial / linear gradients (`city_neon_haze.gdshader`, vertex colour premultiplied by strength); the dithered mode is no longer used by any quad.
3. Screens: DONE. Clean rectangles with a crisp lighter frame, large flat colour fields (3 x 2 big blocks, three tones of one hue, one lighter block, changing slowly), 7 % scanlines, no noise, no flicker.
4. Distribution: DONE. Hotspots are chosen per territory and 44-lot region with traffic relative to the region's own busiest crossing (quiet districts get them), Solace excluded (parks). One full neon avenue strip: the northernmost long avenue gets a hotspot every 6 lots (`avenue_strip`). The plan shows clusters in the south-west and centre, the north tower cluster, and the north-east.
5. Avenues: DONE (faint). A continuous amber glow line (smooth cross-fade, alpha 0.5) down every avenue (traffic at least 0.8 of the busiest), visible between towers.
Also: hotspot crossings are a smooth fan toned toward the hotspot colour (alpha 0.32).

## Tests
test_city_neon_kit 8 (new: blade signs, roof logos and holos outside hotspots are deterministic and vanish at share 0; the avenue strip is one northern line), test_city_grade 13. Others untouched this round. Full suite not run.

## Metrics (plan)
luma p1/5/25/50/75/95 0.062 0.127 0.244 0.309 0.427 0.809 (plate 0.069 0.113 0.232 0.325 0.481 0.844); median rgb (69,77,124).
## Perf
Level 3 city GPU p95 11.14 ms (round 9: 11.07 ms; budget +1.5), level 2 11.22.

## Gaps
- Some screens and halos stay pale pastel (cyan-white, pink-white) next to Shibuya's deep saturation; the post's saturation grade and the pale content block are the cause.
- The strip in the north is visible mostly as halo and roof tints; the avenue glow line is faint through the dense core.
- Holo ads are still small at the plan camera.

## Slips
None on `python -`. One `rm -rf` of my own scratch folders (perf13 / lab13) was used. No foreign files touched; no background processes left.
