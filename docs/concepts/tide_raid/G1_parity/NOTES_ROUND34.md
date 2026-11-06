# G1 round 34, branch art/tide-r34 (from c2c6bc64). Outputs in r34/: compare_r33_r34.jpg (plan, seed 3, bay close-up, river strip), tools/.
Designer decision: the OuterLand expanse is the bay. Done: in the r6 look OuterLand gets its own material (`CityMaterials.ground` with the new `bay` uniform in city_ground.gdshader): opaque emissive deep blue (`r6_bay` 0.07, 0.19, 0.47; probe RGB (30,65,141) / (34,74,162) in the plan vs the river (49,91,123) / (63,118,157): a little deeper and bluer, same family) with a slow value variation (`r6_bay_var`) and a faint ripple term. It is opaque and unlit by the land colour, so nothing under it recolours it. Keeps the water-class tag. `r6_land_mul` reverted to 1. City ground (grey-green), river and the south sea untouched.
NOT DONE: the shoreline highlight where the bay meets city land. The visible join in the plan is the city rect's own edge (a grey-green apron band with the highway ring on it), which is not a shore edge the OuterLand mesh knows; a highlight line there needs the coast contour (CityPlan.coast) or a mesh outline: not built this round. The bay edge is currently a hard line.
Structures left as they are in the bay region (screen positions at the bay close-up, zoom 3 centred 150,500, 1920 x 1080):
- building cluster on the left (x 0-500, y 500-840) and the shore islands next to it;
- three small cubes at the top (x 840-1080, y 80-240) standing in the water;
- stray dark road / slab stubs at about (780-880, 260-360) and a bridge-like road at (480-660, 700-840) (A-108 item 3 covers roads into the bay).
Perf p95 9.23 ms. Tests: neon kit 15, a2 16 + 2, city3d model 12 pass.
Slips: none (no `python -`).
