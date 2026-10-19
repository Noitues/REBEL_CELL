# CITY-A2 step 2: the rest of the A2 city (terrain, land beyond the edge, rails, landmarks, ring), old grid removed

## Context
Step 1 (merged into w1-close @ a8e6578a) made `content/city/city_A2.json` the city format: CityPlanA2 (loader / validator),
CityA2Raster (A2 laid on the lot grid: water, districts, roads, parks, shore depth, neighbourhood kinds), CityA2Builder (seeded lots,
`city_layout` + `city_blocks` streams), CityPlan.generate -> A2 by default. Read `docs/handoff/plan2/CITY_A2_PORT.md` first: its
"step 2 must" list is part of this brief.

Designer, 2026-10-19: "are you missing the terrain now?" Yes. A2's hills are in the plan data and the city.json sections, but nothing
draws height: the ground is flat, and the land is cut to a square slab at the city edge. The golden plate `city_a2_night` / `city_a2_day`
(art-pass golden_plates) shows hills, coastline and land beyond the city ring.

## Lanes (designer ruling A-041)
- Build owns geometry, data and generators: heightfield mesh, land / coast geometry, rails, landmark placement.
- Art-pass owns materials, shaders, light, fog, post and camera look settings.
- Put the terrain geometry in new code paths. If you must touch a look file (shaders/city/*, city_materials.gd look params,
  route_rig.gd look parts, StreetLightRig, env / post), stop and list it in your RESULT, so we can claim it with art-pass first.
- Use plain existing materials for new meshes (the ground material, the water material).

## Items
1. **Terrain:**
   - A2 hills (Gaussians, `height_m = h * 260`, scale per CITY_A2_PORT.md) become a heightfield the city sits on.
   - Lots, streets and buildings follow the ground (sampled at the lot center, so streets stay drivable), and the street deriver
     and route rooms keep working.
   - Add the heights to city.json (additive) so Blender renders the same ground.
2. **Land beyond the city edge:** A2's full extent (±10 km): land, coastline and sea out to the extent, so the city no longer
   ends in a square slab. Low-detail outside the playable lots is fine.
3. **Perimeter ring and roads by class:** A2's ring road and its motorway / truck / arterial classes visible as roads, plus
   interchanges.
4. **Rails and stations:** freight, commuter and metro lines from A2 as geometry, with underground sections hidden.
5. **Landmarks:** place them from art-pass `city_all_corps/ENTRIES.json` @ 77cdfde9 on their A2 districts. Reuse our
   assets/city/landmarks glbs; check that they match ENTRIES.
6. **Port, walls and gates, drowned quarter, tunnels:**
   - the port, and corp walls with checkpoints at road crossings;
   - the drowned quarter as land with flooded lots;
   - tunnels below grade.
   Any of these may be a simple first form; list what's simple.
7. **Remove the old grid:** CityGenerator, `generate_grid` and the parametric coast. Decide the fixed seed 7: the default is that it
   becomes an A2 city, with fixtures and goldens regenerated (log it).
8. **Frontage heights:** street frontage tops along the netrun street must reach r2 `layout_pass` heights (median about 24 BU, art-pass
   A-039; ours were about 15). Compare with art-pass `street_r2/scripts/r2_rules.py` `layout_pass` and fix in the lot or height rules.
9. **Perf:** test_netrun_art_export_sweep took 2884 s on a loaded machine (A2 builds run the NA-11 rules, about 2-3 s per seed). Cut
   it (fewer full-city builds, or a cached plan raster) to under the manifest number. Keep the seed sweep at the 95th-percentile
   budget.

## Acceptance
- Determinism tests from step 1 still pass, extended to heights, rails and landmarks.
- A whole-city capture, seed 1, night and day beside the plates, commits `docs/art_review/PLAN2/CITY_A2_step2.jpg`. The shape reads as
  the plate: bay, ring, hills, land beyond, landmarks.
- A2 street plate inputs: `tools/city/na23_lab.gd --export` for seed 1 writes `docs/handoff/netrun_art/plate_inputs/seed1/` from
  the A2 city. These replace the old-grid files; art-pass waits on them for L4.
- Schema smoke checks and DECISIONS entries for city.json additions.
