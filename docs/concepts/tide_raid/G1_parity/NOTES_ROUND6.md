# G1 round 6 (designer rulings), branch art/tide-proto

State: items 1, 3, 4, 5, 6, 7 done; item 2 done as built but it did not move the squint (0.19 stays; bar 0.11 missed). The per-city bake tool was NOT built (reason below).

1. Beam, one continuous ribbon: DONE. `TideRibbon.strip_mesh` is now a single triangle strip with a shared vertex pair at every point, mitre-offset (length clamped at 2.5 x half width), so there is no per-segment overlap and no stacked alpha; the ghost pass draws the core only. Unit test updated (6 UV verts for 3 points, 12 indices). Look at 04: one clean line with a dash pattern, thin core, narrow halo. NOT matched: the plate's chain-link texture and bloom read; the link pattern is a small dash/ring pattern at this width, and halo bloom is light.
2. Bent-normal AO + sky visibility: BUILT, kept, low effect. Runtime sky visibility from the roof height field (a per-lot texture built from the layout at load, `g1_height_tex`; 8 horizon directions x 6 steps, walls count only the directions in front), applied to ambient (0.8) and body colour (0.5, dark 0.5). Plus lamp occlusion by the same height field (a lamp lights only what it sees), default on. A/B: skyvis_amb / skyvis_body / lamp_occ = 0. Squint against the opaque target: 0.190 to 0.189 for lamp occlusion; sky visibility alone slightly worse on luma (it darkens, the plate target here is not darker). Tower-foot and street-canyon darks are visibly deeper in the frames, but the metric did not reward it. Screen-space AO and scene bleed exist, off.
   Per-city irradiance bake: not built. Reasoning: the runtime path already is a seed- and camera-free irradiance model (sky visibility + occluded lamp pools); the remaining error is the plate's Blender Cycles light placement, which a layout bake approximates no better than this does. If you still want it, say so and give a reference (a Cycles bake of the city) to fit against.
3. HQ cage: agreed, none in Godot, not counted as a gap.
4. Roads through buildings: DONE. Cause: the raid band's see-through buildings (post `has_ground` / opacity 0.32 draw the ground pass through them). Under the grade the buildings are opaque (`opaque_buildings`; A/B `see_through_buildings`). This also drops the ground pass (perf). Checked on plates 01-07 city shots and the generality sheet.
   Because the old plate target contained the see-through roads, I rebuilt all targets from an opaque capture (`targetO_*`, `make_city_target.py` with BASE_IMG, capture flag `--opaque`). Metrics in metrics.md are against these; hue L1 is much worse than before (0.18, mid 0.4) because the opaque base differs in chroma from what the plate grade was built on; treat metrics as indicative and judge by the side-by-sides.
5. River banks: DONE for the visible coast. The shore (land / outer-land class edge, lot-stepped) is blended through a ring-averaged soft threshold (`shore_radius_px` 14, taps 12), so the colour edge is a smooth curve; geometry stairs remain under it (a geometry fix is build's: smooth `CityMeshKit.land_mesh`).
6. HOME hit chip: DONE. The plate's amber hexagon with a broken heart (ink heart, amber crack) and "-6" beside it, outlined (`TideFx.hit_chip`).
7. HOME hit icon: KEPT. Godot's attacking-head icon stays over the blast (scale 0.6).

## Numbers (plate 01, vs the opaque target)
Squint 0.190; luma -1.7 %, sat +0.9, warm -12.0, light points +9.7, reflection -2.1, hue L1 0.208. Out of tolerance: warm (all -12, top -69, mid -44, right -30), hue L1, bottom / left light points +27-30 %. Other beats squint 0.190 to 0.195.

## Perf (perf.md, city GPU p95)
legacy 10.77 (noisy run, p50 9.40), level 1 11.73, level 2 11.03, level 3 12.35 ms. Level 3 minus each feature: wet reflection 0.5, bloom 1.2, rain 0.3, lamp pools 0.8. All under 1.5 ms; sky visibility and lamp occlusion are inside the level 2 / 3 numbers.

## Open
Squint 0.19; warm and hue distribution vs the opaque target; chain-link and bloom on the beam; garden canopy colour; plum edge. Seed-bound items unchanged (facades, lamp lattice bake).
