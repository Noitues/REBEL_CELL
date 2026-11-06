# G1 round 29, branch art/tide-r29 (from 08bcd22c). Outputs in r29/: lookdev_vs_round6.jpg (round 6 | r28 | r29), compare_r28_r29.jpg (plan, hotspot, seed 3, highway), tools/. The look-dev was about 3 iterations; the user-facing question is whether it now passes the squint test against round 6: it is much closer in colour, still not identical.
Per item:
1. Ground: DONE. `ground_mul` (0.22, 0.28, 0.8) on the street / lot / land albedo (lawn exempt) gives near-black navy ground; lawn is saturated dark green; bay is navy again (level-0 post lost the grey cast with fog / haze cut: `r6_haze_k` 0.06, `r6_fog` 0.04).
2. Avenues: DONE. Strength 0.9 (r28 1.4 was already pale), strips now run THROUGH intersections (an intersection lot carries each axis whose two neighbours are street lots), one hue per street line, wider (half 0.24 lot). Audit updated (no intersection rule; highway zone, river and open ground still excluded; test passes). Not matched to round 6: no soft bloom halo around them (bloom 0.3, strips are solid quads), and some strips read as flat pastel slabs near building bases.
3. Grade: DONE. Post saturation 1.3, contrast 1.15, no lift (level 0); families mauve / teal / slate / rose / green, values 0.6-1.0, tinted 38 % toward the corp colour.
4. Toon bands: DONE (partly): ramp 0.16 / 0.42 / 0.80 violet; lit, mid and shadow walls separate on towers; flat-ish on some low-rise.
5. Ink: DONE. width 0.8 x zoom factor, alpha 0.8, depth-edge threshold 1.2 to 3.0, wobble 0.7. The rough edges on tall towers are gone in the hotspot crop; not exhaustively checked at every zoom.
6. Windows: PARTLY. small squares, 30 % lit, corp colour; some warm yellow from the base window palette; crispness at plan zoom is low.
7. Mast tips: DONE, gain 1.1 to 0.8 (they keep the corp hue; still bright).
8. Shape kit: DONE. New HEX and OCT kinds (6 / 8 sided prisms inside the lot, test `meshes_fit_the_unit_square` caught and fixed a radius over the lot), sprawl weights give them 14 % / 16 % of the picks (tall ones included; min height 8 BU). Tapered tops (SLANT) and stepped (SETBACK) unchanged.
9. Traffic occlusion (upper deck hides streaks below; glow only on top deck): NOT DONE.
10. Pink-lilac haze on open ground: NOT FOUND/REMOVED as a bug; at level 0 with ground_mul the open ground now reads navy-violet; a pink fringe remains on the western plan edge in seed 3.
Numbers: plan luma p1/5/25/50/75/95 0.009 0.043 0.132 0.235 0.437 0.869 (deep blacks, high highlights as round 6). GPU p95 10.80 ms. Tests: neon kit 15, a2 16 + 2, grade 13, lamp plan 9, shape kit 7, city3d model 12 pass.
BUILD HAND-OFF: `CityView3D.art_look` gate (also gates r6_look) as before. Stopped after r29 as asked.
Slips: none.
