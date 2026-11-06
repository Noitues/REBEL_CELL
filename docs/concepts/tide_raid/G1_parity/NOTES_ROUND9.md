# G1 round 9, branch art/tide-proto (D:/rc_art/godot_look_tide), commits 03aa736e, 424e967a, 7024c30c, 91b3f157, 34bf11bc, 86092c19 and the warm-share commit after it

Judge by final/01..07, generality/seeds_cameras_sheet_r9.jpg and the closeups/ named per item. Metrics and perf in metrics.md / perf.md.

## 1. Lamps from the road graph: DONE
- `CityLampPlan` (scripts/city3d/city_lamp_plan.gd, pure): kerb lamps on street lots of straight streets, alternating sides, per-street phase and seeded spacing jitter (+-0.35 lot), 13 % seeded outages, per-lamp intensity (0.62..1, texture alpha); two opposite corners of each intersection (a hashed diagonal); plaza-lot edges; both rails of bridges; the river quay. A street with no building or plaza beside it (open ground) gets none, so no lattice anywhere: interiors of parks, vacant lots stay dark. No lamps within 2 lots of elevated highways (ring, motorway, truck) or ramps.
- The post reads a per-city lamp texture (3 BU cells, one lamp per texel) built at load (`CityView3D._build_lamps`); the baked plate lattice is gone (lamp_lattice.png no longer referenced). Occlusion by the height field unchanged.
- Look (designer notes): no emissive head; only cast light: pool sigma 0.8 BU (was 1.09), core 0.25 BU, wide wall/ambient bounce 1.1 BU; dense small pools. Size steps: closeups/lamps_r9_size_steps.png (before, big, mid, chosen). Warm share restored with wall / ambient / pool gains (metrics.md).
- Close-ups: closeups/lamps_r9_before_after_streets.png, lamps_r9_before_after_b.png, lamps_r9_plan_before_after_side_by_side.png and _squint.png (320 px squint: strings along streets, not a dotted grid).
- Tests: test_city_lamp_plan (6): lamps on kerbs / corners, none on open ground, deterministic and sorted, jittered, bridge rails and quay, highway zone removal, texture intensity.

## 2. Beam: braided double helix: DONE
- `TideRibbon` (tools/raid_tide/proto/tide_ribbon.gd) rebuilt: polyline -> fillet (radius 7 BU, clamped to half the shorter adjacent segment, 0.25 BU arc samples) -> resample by arc length (0.5 BU) -> two strands offset +-1.35 BU * sin(2 PI s / 10 BU + {0, PI}) with continuous s (phase never resets at corners, fade-in/out over half a period) -> white bead at sin = 0 (every half twist) -> soft magenta halo strip, no dark fill. Mesh = three continuous triangle strips (halo, two strands), no caps, arrows, chevrons or mitres. Ends taper to a point. The head icon and timing follow the same filleted route. Vertical drops are the same arcs (heights interpolated along the arc).
- Close-ups (3x, plate vs Godot): closeups/beam_r9_corner1..3_plate_vs_godot.png.
- Tests: test_tide_fx_proto 14 (fillet radius and clamp, no kinks, three strips with continuous phase, bead / half-twist count, strand mirror).
- Gap: the plate's strands are a little more luminous and the plate adds a faint link texture; ours is a clean bright pair with soft halo.

## 3. River: DONE (visual); width spec below
- Water body (`g1_water_body`) now edge to edge, dark blue-teal (no sky fade to black), gentle flow ripple, broad slow current bands, sparse crest glints, quay and bridge lamps smeared along the water (analytic march, wobbled by the ripple, never a mirror) plus a faint lit-city smear; no ambient / spill on top. The river lots carry vertex alpha 0.5 on the sea mesh (the same class tag the seabed used), so the whole channel is river class.
- Rainbow chips: they were the shore-light reflection smears (`ShoreReflections`, palette amber / pink / cyan / violet quads hanging down the screen from every shore edge) drawn on the river banks, and the pier decks; river edges now get none, and no piers.
- Quay: `CityWater._wall_meshes` splits the shore into bay and river chains. River wall is `river_wall_h` = 0.55 BU (bay 2.4), narrow coping, a stone top strip (1.2 BU) on the land side, chain relaxed 12 passes and pushed 1.6 BU toward the water so the stone hides the lot staircase. Water surface is only just under the street. A lamp row stands on the quay (item 1).
- Bridges: street lots over river water are decks (`CityMeshKit._deck_on`): top at `river_wall_h + river_deck_h`, sides into the water, dark stone parapet along the open sides with a lit warm rail top; lanes ride the deck. They read as bridges with rails and lamps.
- Close-ups at the plan camera plus 2 seeds: closeups/river_r9_plan_camera_crop.png (plan), river_r9_seed7_z6_after.png / river_r8_seed7_z6_before.png, river_r9_seed7_z3_before/after.png, river_r9_seed3.png, river_r9_seed19.png.
- Bay: flat deep colour back near round 6: closeups/bay_r6_vs_r8_vs_r9.png (round 6 | round 8 | now). Round 8 had gone near-black at the bottom (sky fade); `water_sky_fall` 1800 and `water_color` give top/mid/low (14,67,133)/(5,58,129)/(1,39,99) against round 6 (13,74,135)/(6,55,130)/(2,31,104). The 2D fade to dark toward the foot of the frame is smaller than round 6's own.
- BUILD SPEC (river width): the river is 1-2 lots wide in this plan (166 river lots over 79 rows; runs of 1 lot along most of its length, 2 where it bends). At 6 BU per lot the water is a 6-12 BU channel; at the plan camera that is 12-25 px across and it reads as a canal. For a river that reads at the plan camera the channel should be 3 lots wide (18 BU) with the banks following the same course (and bridge decks every 12-15 lots); 4 lots on the main reach. Reason: the quay (1.2 BU stone + coping) and lamp row eat about 1.5 BU per bank, so under 3 lots the water is a strip a few px wide between the lamps. Lives in A2 plan data (roads / rivers polyline widths in `CityPlanA2`); I did not touch it.
- Tests: test_city_water_look 7 (river quay lower than the sea wall, river lots are water, quay chain offset), test_city_a2 14 / 2, test_art5_city_integration 10.

## 4. Cars on the roads: DONE (a regression in the sense of the raster; fixed)
- Cause: the street car lanes (`CitySkyLanes.build` street_rows) were laid along the WHOLE avenue line from its first to its last street lot at a fixed `street_height` of 0.5 BU over world y = 0: they ran over parks, plazas, water and the elevated highways, and on any ground above 0 (the terrain hills, the shore, bridges) they were under the road mesh or in the air. The A2 city has terrain, so the lane height must follow it. shore_h, the ground mesh and the road mesh are not at fault (they agree with `terrain.height_at`); the lanes simply never read the terrain.
- Fix: `CityMotionSite` carries the ground function, the street lot set (minus elevated-highway lots) and the bridge deck height; lanes are cut into runs of at least 3 contiguous street lots and every lane point stands `street_height` over the ground (a bridge: its deck). `street_min_traffic` 0.3 -> 0.2 so the local streets carry cars too.
- Close-ups: closeups/cars_r9_before_after_a.png and _b.png.
- Tests: test_city_motion 17 (new: street car points stand on street lots at road height, no highway lots, runs >= 3 lots).

## 5. Windows: DONE
- Under the grade (`CityGradeConfig` window_*): lattice pitch x0.55 and pane size x0.5 of the city config (about 3x the windows per facade, regular rows and columns), lit share x2.0, window gain x1.0 (was 3.0 with the coarse lattice), dimmest window 0.3 of the brightest, and tapered buildings carry the lattice too (`window_all`). Building colour reads through. Close-up: closeups/windows_r9_before_after.png.

## 6. Park: DONE; shore promenade: DONE
- Canopy: mid green (tree colours and a canopy gain applied only to what is greener than red), tree share 0.8. Bloom clusters: 7-12 small magenta / pink domes per tree lot (`park_bloom_*`), drawn as their own light (ground shader `bloom` branch) and as a park sub-class the post leaves un-tinted (cool district tint would turn pink violet). Plum edge glow: one gradient quad per park lot edge that meets non-park ground (full plum on the boundary, fading to black over 2.4 BU).
- Shore promenade: street-class pixels on land lower than 6 BU are multiplied by (0.36, 0.38, 0.6) (full under 1.5 BU): darker, bluer, like the plate's land. Still a little lighter than the plate near the water; stronger values start to crush the highway deck.
- Close-ups: closeups/park_r9_before_after_a.png, _b.png; closeups/shore_r9_plate_before_after.png.

## Not done / gaps
- The beam strands are crisper than the plate's. Lamp pools are intentionally dark in open ground, so the top band's warm share stays low (metrics.md).
- Full suite not run (targeted tests only; see the report).
