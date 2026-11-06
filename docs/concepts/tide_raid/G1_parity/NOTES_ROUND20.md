# G1 round 20, branch art/tide-r20 (D:/rc_art/godot_look_tide, head after b80a3027). Outputs in r20/ (compare_r19_r20.jpg, generality_sheet_r20.jpg, tools/); earlier folders untouched.

1. Highway glow plane removed: DONE. The `hwy_haze` part, its config and its test are gone. Streams brighter (tail 4.6, head 4.2 HDR), edge gain 1.5, so the line read comes from stream brightness and bloom. At the real 320 px downsample the highway curves still read as thin pale lines, but weaker than r19 (the glow band was what made them wide); compare_r19_r20.jpg bottom row.
2. Dark-gap buildings: DONE. Band half width 1.3 to 0.5 lots: 23 % to 10.0 % of the plan frame (192 of 1919).
3. District tuning: DONE. Teal window gain 0.95 to 0.72; magenta tint and body desaturated 20 % toward grey.
4. White towers: 9 in the plan frame (asked 8; spacing 19 lots; one sits at the frame edge).
5. Values: exposure 2.6 (2.4 gave p50 0.283). p1/5/25/50/75/95 0.043 0.081 0.202 0.309 0.428 0.811. p1 / p5 are higher than r19 (fewer black slabs).
6. Structure metric: coarse std full frame 0.128 (r19 0.137, r18 0.123, plate 0.165): giving up the black gaps and the glow costs part of r19's gain; still above r18.
Perf: p95 12.38 ms (limit 12.57). Tests: neon kit 14, a2 16 + sweep 2, grade 13, lamp plan 9 all pass.
Slips: typed `python -` once more (an empty heredoc, harmless, no hang). No background processes left; no foreign files touched.
