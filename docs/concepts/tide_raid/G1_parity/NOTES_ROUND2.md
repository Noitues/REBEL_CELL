# G1 round 2 (after the art-pass review of the first final), branch art/tide-proto @ 10e87dfe

All comparisons are against the P3 plates (docs/concepts/tide_raid/P3_plates/plates/). City-only targets are rebuilt per beat from the P3 scripts (make_city_target.py, plus each beat's Blender spill layer). Side-by-sides for 01 to 07 are in final/ (01-03, 06, 07 city only; 04 and 05 with the beam and burst prototype at the plate camera). NOTES.md (round 1) still describes the build; this file only records what changed.

## Fixed from the review
1. Cast and crispness: bilateral surface smoothing before the grade (removes the toon spill dither on faces; keeps edges, lit outlines, windows), toon ink alpha x0.49 and wobble x0.3 under the grade, blue-violet hue rotation (-4 deg on 232..330 deg, warm districts exempt). Hue-histogram L1 whole frame 0.175 to 0.065 (bar < 0.08): top 0.075, mid 0.080, right 0.079 pass or touch; bottom 0.104 and left 0.117 do not.
2. Warm lattice: warm-share error all / top / mid / bottom / left / right = -3.0 / -3.7 / -5.1 / -5.7 / -7.8 / +3.1 % (bar +-10 %, met in every band). Lamp streak march lengthened (100 px, 48 taps), warm tint and exposure retuned.
3. Beams and HOME: the 3D ribbon is a neon (white-hot core, ink under-stroke, additive halo, ghost pass too, brighter D tile band, plates D/N/E colours in tide_look.tres). HOME hit is a cream star polygon with thick gold rays and thin black spokes. Garden canopy gain added.

## Metrics, final iter56 against the plan city target
Whole frame: luma +0.8, sat -1.6, warm -3.0, light points +5.5, reflection -1.2 %. Worst band per metric: luma +4.5 (left), sat -4.8 (top), warm -7.8 (left), lights +11.4 (top), reflection -5.1 (bottom). All inside the bar. Full table in metrics.md (no row marked NO).
Squint L1 (4 px blur, mean abs over mean) 0.132; bar was < 0.08: NOT met.

## Honest gaps
- Not indistinguishable at a glance. Aggregates match; positions do not: the plate has large soft amber pools under lamps (Cycles bounce) and softer bloom; Godot's pools are smaller, and light points sit in different places. This is the squint L1 miss.
- Street reflections are screen space plus analytic lamps, no true mirror.
- The plates carry beams, HUD, tiers, wireframe towers, plum creep and the green cage; those are other layers, so plate vs city-only Godot differs there by design. 04: beam is a neon now but has no link texture or true bloom. 05: burst has no confetti bits, scorch or tear.
- Garden canopy is brighter but still darker and less varied than the plate; no cage.
- Everything baked is seed 7 and the plate camera.

## Perf (perf.md, refreshed)
City GPU p95: legacy 9.51, level 1 10.29, level 2 10.87, level 3 11.35 ms. Level 3 costs +1.8 ms p95 over legacy (bloom about +0.5, rain +0.2, wet reflection +0.1); no single feature over 1.5 ms.
