# G1 round 4 (general ambient), branch art/tide-proto @ c7bbacf0

Goal changed from "fit this view" to "any seed, any camera". Status: general, but the seed-7 plate match got WORSE. Not at the squint bar on any beat.

## Built
- Generated ambient / bounce (city_grade.gdshaderinc `g1_ambient`, config group Ambient): sky fill by surface normal (up vs wall, sea own colour), district-warm variant, wide lamp bounce from the same world lamp lattice, optional SSAO (`ao_*`) and scene bleed (`bleed_*`), both off (they did not help). Colours were fitted by class and district from the plate target (inverse tone map), not tuned per band. It reads the world only (a unit test checks it never reads the plate-frame maps).
- The fitted spill / warmth maps are now the A/B toggle `use_fitted_maps` (also `--post=g1_baked=1` in the capture tool). The plate-seed light features (hero glow, HOME beacon, rooftop cones) only run when the city has the plate facade set (seed-bound), via `g1_plate_lights`.
- capture tool: `--seed=N --zoom=Z --cen=x,y`.
- Beam: one chain family; N is a thorn-link diamond, no rungs. HOME burst: no shock ring, small head over a white flare, cream polygon at 0.35. Not iterated further this round (see gaps).

## Numbers, plan 01 (squint = 4 px blur mean abs / mean)
| | squint | luma | sat | warm | lights | refl |
|---|---|---|---|---|---|---|
| fitted (round 3) | 0.091 | +1.2 | -4.5 | -6.5 | +3.3 | +3.6 |
| generated ambient | 0.197 | -2.9 | +0.5 | -12.8 | +5.7 | -0.8 |
Out of tolerance in metrics.md: warm all -12.8, top -40, mid -17.5, right -19.9, mid light points +23.5, left sat -9.0, right luma -5.9. Other beats: squint 0.196 to 0.206.
The requirement was within +0.01 of 0.088 on seed 7; it is NOT met (0.197). The fitted result had 3x less error because it carried per-pixel plate light; a world-only model gets the class and district means (luma, hue L1 0.09) but not the plate's local light placement (soft amber pools at specific lamps, bounce under towers).

## Other seeds and cameras (sanity, generality/)
seeds_cameras_sheet.jpg: seed 3 zoom 1.0, seed 19 zoom 1.2, seed 7 zoom 2.4 at another centre, and seed 3 with the fitted maps for contrast. The model looks consistent: warm lamp pools and cool sea / park, no maroon trees, no plate-frame artifacts. With the fitted maps on another seed (4th tile) the result is visibly wrong (smeared plate light), confirming they cannot ship. The seed-3 and seed-19 frames also show the plate's tower beams only on seed 7 (hero facades are seed-bound).

## Gaps, honestly
- Squint 0.197 vs bar 0.088; warm share out in several bands. More ambient detail needed: per-lamp pool radius and brightness, bounce under towers, a proper SSAO/bent-normal term. SSAO as built did nothing useful at the plate target; the residual is dominated by street pools and bright-roof glow (target luma > 0.4 area is 16 % of pixels, 31 % of the error).
- 05: the N beam still reads as a double rail at this size (the 3D ribbon's two edges plus the ghost pass), not a thin pink chain; I did not get to thin it further. The burst is closer (white flare, no ring) but has no confetti or tower cracks.
- Garden canopy: no further work this round; plum edge not built.

## Perf (perf.md): city GPU p95 legacy 9.39, level 1 10.11, level 2 11.66, level 3 11.18 ms (+1.8 over legacy). Level 2 is the costliest by 0.5 ms because the generated ambient and shafts run before bloom/rain are on; each feature under 1.5 ms.
