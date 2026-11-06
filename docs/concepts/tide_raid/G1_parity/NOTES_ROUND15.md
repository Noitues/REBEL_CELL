# G1 round 15, branch art/tide-r15 (D:/rc_art/godot_look_tide), from art/tide-r14 977f907f. final/ untouched. Outputs in r15/.

## 1. Brown arc: FOUND and removed
Node tree dump: r15/cityview3d_node_tree.txt (capture tool `--dump-tree`; `--hide=Name`, `--hide=Parent/Child`, `--hide=all:Pattern`, `--set=prop=value`). Bisecting by hiding nodes: the arc is `A2Features/Walls`, the plan's corporate district wall (a curved wall through the core, lit amber by lamp light). It is not a sky lane, a beam, a ramp or the HQ overlay. Now `a2_walls_draw = false` (the walls are plan flavour, not part of the raid view); test_city_a2 asserts "district walls are not drawn". r15/box1_r15_before_after.png (and box 1 is clean in the plan).

## 2. Placement audit: DONE (built, tested, all violations fixed)
`CityNeonKit.audit(cfg, prisms, streets, quads)` and `CityLampPlan.audit(lamps, street_lots)`; every neon quad carries cat / owner / face. Checks: wall quads (screen, blade sign, crown) inside the owner's footprint box, between its base and roof, facing a street lot (not a building, not open ground), not inside another building; roof pieces at or over the roof and inside the footprint; holos over a tower of at least `neon_holo_min_h`, not over Solace, above the roof; avenue traffic on a street lot; lamps on street lots. Tests in test_city_neon_kit (real cities seed 1 and 3: zero violations; a synthetic misplaced quad is caught).
First run found: roof logos / screens outside rotated or non-square footprints (43 + 178 on seed 1), screens poking above short roofs (1-2), holos over Solace (1). Fixed: roof pieces size from the footprint's own sides, screens clamped inside the wall height, no holos over Solace. Now 0 violations on seeds 1 and 3 (22857 / 26189 quads audited).
Also removed: the hotspot street trees (corner trees stood on street corners, not on park or pocket lots).

## 3. Signs on street-facing walls only: DONE
Hotspot screens, blade signs and crowns require the wall's outward lot to be a street (the audit checks it). The halo around a screen is clamped to the wall's own width and height.
## 4. Bridge light strings: DONE
Every street lot over river water (a bridge that carries a street) gets two lamps per lot on each of both rails (regular spacing), no building condition, full warm amber (not dimmed by the low-rise scale). Test: 12 lamps on a 6-lot bridge, both rails, far from buildings. Close-up: generality_sheet_r15.jpg bottom right. The river is thin, so the strings are small at the plan camera.
## 5. Hotspot spread: DONE
Hotspots are chosen per territory in 30-lot regions (up to 3, 8 lots apart, radius 9, screens from 12 BU), so every populated region has one, including the north-east and the far south-west. The trade-off: signs only on street-facing walls means fewer, smaller screens than r14, so the plan looks calmer. compare_r14_r15.jpg.
## 6. Re-shoot, metrics, perf
compare_r14_r15.jpg (plan, hotspot close-up, 320 squint), generality_sheet_r15.jpg (plan, seed 3, seed 19, river). Plan luma p1/5/25/50/75/95 0.043 0.065 0.163 0.267 0.366 0.769 (bay masked; r14 0.046 0.070 0.173 0.271 0.374 0.770). Perf level 3 city GPU p95 11.53 ms (mean 11.12) against the 12.57 limit.
Tests: test_city_neon_kit 11, test_city_lamp_plan 9, test_city_interchange_kit 5 pass; see the report for test_city_a2.
## Gaps
Neon is less loud than r14 (street-facing rule); holos are fewer; the audit does not yet check pocket-park lawn and trees or the highway dashes' height (they are placed by the deck height in code).
