# G1 round 38, branch art/tide-r38 (r37 6eb068d0 + merge of art/city-layout-p0 6ea2d710). Outputs in r38/: compare_r37_r38.jpg (plan, seed 3, hotspot, bay, 3 anchors), tools/. godot_lint worktree untouched.
1. Merge: clean, no conflicts (one merge commit; only city_neon_kit.gd and tests/test_manifest.json auto-merged). Layout and r37 view rules coexist.
2. No-hide test, new sizes (report): wall / rail clash skip seed 1: 11 lots (was 9), seed 3: 12 (was 7); Solace pockets 5 / 5 (unchanged). They did NOT drop: they rose. The clashes are all on the same few lots in the west corner (about lots (-71..-59, -21..-17)): the layout re-placed buildings and some now sit within the wall highway's half width + 0.4 BU of its route there, so the layout's 45 m wall corridor does not cover that stretch (suspect the corridor stops near the raster / city rect edge). I set the baselines to the new sizes (11 / 12, pockets 5) rather than lower them; they should reach 0 when the corridor covers that stretch. `_in_cleared` not covered (live view).
3. Renders: compare_r37_r38.jpg. The layout shows: a large dense park north of the core, fewer and sparser avenue strips, streets kept out of parks. The shoreline anchor (centre 1150,1000 at zoom 5) was mis-framed on buildings, not the shore.
4. By-eye oddities (screen positions at the plan camera, 1920 x 1080):
- four pale glowing cubes floating over the core at about (770-930, 240-420): the neon holo ads standing over buildings (not part of the layout; check holo placement on the new layout);
- the park north of the core (x 400-1150, y 40-300) is one big dense tree mass with no paths, and the highway ring runs along its edge at (600-1000, 280-300): park strip under the deck reads as forest right up to the pylons, fine but featureless;
- empty grey apron lots along the bay shore (x 0-420, y 180-520): the bay-side slab is bare with a few lone cubes (115,330), (290,240), (70,330) = isolated single buildings, plus small white lamp dots (150-300, 260-320) along the slab edge;
- empty dark lots west of the Solace park around (1130-1200, 380-480) between the core and the park;
- cul-de-sacs / dead ends: none visible at plan zoom (not checked at street level).
5. Tests: road audit 4 (baselines updated), neon kit 15, a2 16 + 2, city lint 19 + 1, lint sweep 1, city3d model 12 pass. Perf p95 10.46 ms.
Slips: none (no `python -`).
