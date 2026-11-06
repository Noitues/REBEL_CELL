# G1 round 25, branch art/tide-r25 (from 3f3a871a). Outputs in r25/: compare_r24_r25.jpg (plan, hotspot, amber close-up, seed 3, plate | r24 | r25 real 320 px, plate lower-left crop pair), amber_options.jpg, tools/.
Plate crop sample (lower left): body colour about (46,30,68) to (82,60,102) display, i.e. medium violet.

1. Bodies: DONE. Amber district body (0.24,0.17,0.42), a medium blue-violet (A / B used 0.15,0.10,0.28).
2. Windows: DONE. 0.45 of the old size (tiny points), gain 90 to 1.2, 50 % of floors lit; no bloom halo. They read pale-yellow / white, not amber: at higher gain they turned pink then bloomed (see amber_options B).
3. Warmth at street level: DONE. New `CityNeonKit.warm_street_pools`: one soft amber ground fan per STREET lot of the amber district (feather lots 0.4x), radius 0.55 lot, strength 2.0, no audit category (ground level only, never on highways, river or open land); warm base glow on lowest floors raised 0.9 to 3.0 (fades over 9 BU); lit violet roof outlines on the district's roofs. In the plan-scale crop it now reads like the plate's lit streets between medium violet blocks.
4. Structure: NOT met. Coarse 0.135 (target 0.144; r24 0.135); edge 0.152. At the squint the amber zone is now nearly gone: the street pools are too small to register at 320 px, and body-vs-street contrast did not raise the coarse metric. Plainly: the zone does not read at the real 320 px squint any more.
5. Highway streams x1.4 (tail 7.0, head 6.7 / 5.2 / 3.4, edge gain 2.5). Brightest lines at 320 px: not verified separately; they are visible as the pink-orange curve.
Third round on this zone and it still does not match at the squint: amber_options.jpg shows A (white points, mild street pools), B (brighter amber points) and C (lifted bodies, strong street + base warmth, the one committed) against the plate crop, for the designer to pick. A squint cell for A is missing in the sheet (layout slip); A is the same as C but with darker bodies and weaker pools.
Values p50 0.308, p75 0.429. Perf p95 11.77 ms. Tests: neon kit 14, a2 16 + 2, grade 13, lamp plan 9 pass.
Slips: none (no `python -`).
