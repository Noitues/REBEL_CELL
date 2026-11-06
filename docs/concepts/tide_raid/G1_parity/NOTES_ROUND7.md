# G1 round 7, branch art/tide-proto (last commit "G1 round 7: smoothed beach corners ...")

Judge by final/01 and final/05 and generality/seeds_cameras_sheet_r7.jpg. The metrics below are against a plate-pipeline target built on the opaque Godot capture and are no longer a good guide (see "Metrics").

## Defects, in your order
1. Milky veil: FIXED at the histogram. Cause: the generated ambient floor plus the wet-reflection light taps and sheen lifted every dark. Ambient gain cut (up-facing blue only, walls 0.3), wet taps / sheen off, black point 0.07, contrast 1.3, exposure 2.1. Luma percentiles (city region), plate vs Godot: p1 0.060 / 0.066, p5 0.088 / 0.093, p25 0.180 / 0.175, p50 0.292 / 0.326, p75 0.467 / 0.432, p95 0.863 / 0.811. (Before: p5 0.161.)
2. Building hue: IMPROVED. The warm district body tint was pushing buildings salmon; warm tint is now (1.25, 0.86, 0.85). Building median (65,55,117) vs plate (69,56,107): violet / indigo. Ground is bluer and a little lighter than the plate (91,103,162 vs 89,95,144).
3. Warm street light: PARTLY. Lamps now glow everywhere (warm floor 0.8, core x2.5, pools x1.6, neighbour glow x3). They show on open ground (park, promenade, plazas) all over the top half too. In the dense low-rise bottom-left the plate shows amber street grids between the buildings because its buildings are see-through; ours are opaque (designer ruling), so those streets are hidden. Warm share is still low in the metric (-71 %).
4. Window lattices: IMPROVED (window gain x3, lit share x2.2 under the grade); the plate's white / cyan grid facades and edge lines are still brighter and more regular.
5. Park: resolved with 1; canopy is mid blue-green, not the plate's lush green with magenta blooms (no plum / bloom edge built).
6. Beam: thick glowing pink chain ribbon with a core and a halo, one continuous mitred strip (core 1.9 BU, glow 6 BU, period 5 BU). Closer to the plate; chain read is a link / dash pattern, no true link silhouettes.

Kept: hex chip with broken heart and -6, head icon over the blast, no cage, opaque buildings, smoothed shore colour edge.

## A. River bank (mesh): DONE
`CityMeshKit.shore_h`: on the VISUAL ground only (ground_mesh_on, land_mesh) the beach corners (height under `shore_beach_bu` 1.5 BU) take a 5x5 binomial average of their neighbours, so the contour where the ground meets the sea plane is a smooth curve. Corners above the beach, building bases, the lot ownership and the water mask (terrain.height_at) are untouched. Toggle `shore_smooth_on` (CityConfig). Close-up: closeups/bank_seed3_before_after.png (left before, right after; seed 3 coast). The plate camera's coast is a straight sea wall. Tests: test_city_a2 (corner check now via shore_h), test_city_grade (beach only moves, land never sunk).
## B. Water: DONE
Grade water body (`g1_water_body`): deep navy plate colour; a flow-aligned ripple (noise stretched along the flow diagonal, scrolling 1.2 BU/s, +-18 %) so the surface breaks up; city lights smeared down the column from a coarse mip (soft vertical streaks, wobbled by the ripple, never a mirror image); a faint cool glow at the bank where the smoothed water edge falls. Calm and darker than the city. Close-up: closeups/water_bank_01_plate_vs_godot.png. The streaks are subtle at the plate camera (few bright lights near the shore). Perf: water adds about 0.2 ms at level 3 (it only runs on water pixels).

## Bake tool: NOT built
After 1-3 the visible gap is the plate's Cycles lighting; I did not start a Cycles render and fit (that is a multi-hour job needing the GPU lock) because the metric I would fit against is not trustworthy now. If you want it, confirm the target: either an opaque Cycles reference render of the plan camera, or accept the opaque plate-pipeline target.

## Metrics (vs the opaque target, plan 01)
Squint 0.240 (worse than round 6's 0.19: the contrast / black-point change deepens darks, which the opaque target, built from the flatter legacy capture, does not have). Luma +4.7 %, sat +9.2 %, warm -71 %, light points +20 %, reflection 0.0 %, hue L1 0.31. These are out of tolerance; I believe the histogram match to the real plate (above) is the better reading, but I cannot prove it numerically.

## Perf (perf.md, city GPU p95)
legacy 10.64, level 1 11.01, level 2 11.15, level 3 12.38 ms. Level 3 minus each feature: wet reflection 1.2, bloom 0.4, rain 0.05, lamp pools 0.4. All under 1.5 ms. Height-field sky visibility, lamp occlusion and water are included.

## Tests
test_city_grade 13/13, test_tide_fx_proto 11/11, test_tide_fx_seam 4/4, test_tide_raid_screen 23/23, test_city3d_model 12/12, test_city_a2 14/14, test_art5_city_integration 10/10. Full suite not run.
