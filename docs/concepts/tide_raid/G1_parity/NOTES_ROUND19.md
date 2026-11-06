# G1 round 19, branch art/tide-r19 (D:/rc_art/godot_look_tide, head b80a3027, from art/tide-r18 97d887b9). Outputs in r19/; final/ and earlier rN/ untouched.

Deliverables in r19/: compare_r18_r19.jpg (plan, hotspot close-up, plate | r18 | r19 320 px squints), highway_before_after.png (core highway and interchange at zoom 4), district_map.png (district overlay, r19 and r18 squints, legend), generality_sheet_r19.jpg (plan, seed 3, seed 19, park edge), tools/ (metrics, structure metric, compose scripts).

## Task 1: rails and stations hidden again: DONE
`a2_rails_draw = false`, the buildings under the route are back (the rail skip in the view is gated by the same flag, so no lane of lots disappears). The rail audit code (`rail_segments`, the pierce test) and its test stay; `test_rails_hidden_and_highway_lights_ride_the_deck` asserts the flag.

## Task 2: highways are the brightest lines: DONE
`CityA2Features._traffic` rebuilt (config `hwy_*`), into two new parts `hwy_light` (neon shader: keeps its colour through the grade, bloom-visible) and `hwy_haze` (additive):
- two tail-light stripes (HDR red 3.2, 0.1, 0.05) down one half of the deck and two headlight stripes (3.0, 2.8, 2.4) down the other, a dark median between, 2.2 BU chunks with a small brightness hash, continuous;
- a thin lit deck edge on both sides (ring and truck amber, motorway warm red-orange);
- an additive glow 4 BU wide beside the deck (warm amber, gain 0.38) and a faint glow across the deck, butted exactly (an overlap summed to a comb of bright bands at every joint: found and fixed at zoom 4);
- the same on the interchange ramps; decks darkened (0.12-0.16 grey) so the lights carry.
At the 320 px squint the ring, the core motorway and the interchange tangle read as continuous warm lines (compare_r18_r19.jpg, bottom row; highway_before_after.png).

## Task 3: district structure at squint: DONE
New pure class `CityArtDistricts` (scripts/city3d/city_art_districts.gd): a jittered Voronoi (26 lot cells, seeded by the city seed) over the city rect; each cell takes one of 6 profiles and never the profile of an adjacent cell: cool dark, warm amber, neon-dense magenta, teal glass, violet mid, pale cold glass. Every profile has a window hue pull, a window brightness multiplier (0.30 to 1.8), a body colour, and a faint facade glow in its hue. Buildings within 1.3 lots of a border form the dark gap band (window gain 0.12, near-black body). The kind is packed with the territory into the instance COLOR.a (1 - (terr + 8 kind) / 128); the building shader decodes it (art_on, art_tint[9], art_gain[9], art_wall_emit). Only buildings with no corporation territory take a kind (the corp tints are unchanged); the sprawl's flat violet tint is replaced by the district bodies. Ground, streets and open land are untouched (the grid stays dim). district_map.png shows the partition on the plan and the squints before / after.
Note for the other sessions: the raid view is not `whole_look` (`terr_win_k` etc. are 0 there), so the art uniforms are switched on by `cfg.art_district_on` alone.

## Task 4: white-hot vertical accents: DONE (11 in frame, asked 6-10)
`CityArtDistricts.prepare`: buildings with no territory of at least 32 BU, the tallest of each 16-lot block, the blocks nearest the densest tall cluster win (spread, not piled up in the tallest cluster). Shader kind 8: every window lit pale white (gain 2.6), the vertical corner edges and the roof rim emissive white (3.2 / 3.8), pale roof. 36 in the city, 11 inside the plan frame (district_map.png, white dots with a black rim); lower `art_tower_spacing_lots` / raise `art_tower_min_h` to thin them.

## Task 5: keep: DONE
Plan luma (bay masked) p1/5/25/50/75/95: 0.034 0.071 0.199 0.312 0.445 0.812 (r18 0.041 0.065 0.187 0.318 0.435 0.825): p50 on target, p75 +3 %, p1 a little deeper (the dark gaps), p5 a touch up. To hold p50 the grade exposure went 2.75 to 2.5 and darks_k 0.65 to 0.55 (the glow and the district gains added light). r12 neon (screens, hotspots, holos), the dim amber lamp lines and the street grid are untouched. Placement audits: `test_placement_audit_real_cities` 0 violations on seeds 1 and 3; the new light parts are checked against the deck heights.

## Task 6: squint structure metric
See metrics.md (round 19 section): coarse value structure (std of the 80 px downsample) plate 0.165, r18 0.123, r19 0.137 (full frame); core crop 0.175 / 0.137 / 0.155. Edge energy and local contrast do not separate the renders (the facade texture dominates them: plate 0.136, r18 0.141, r19 0.137). The plate's coarse number includes its route lines and cards, so full parity on it is not the goal; the gain is +12 / +14 %.

## Perf
Level 3 city GPU p95 11.92 ms (mean 11.25), limit 12.57 (r18 11.59).

## Tests (fresh, headless, on the committed code)
test_city_neon_kit 14 (new: art districts deterministic, distinct neighbours, border = gap kind, pack round trip, towers few / tall / spread), test_city_a2 16 + sweep 2 (new: rails hidden, highway lights ride the deck), test_city_grade 13, test_city_lamp_plan 9; also test_city3d_model 12, test_city_shape_kit 7, test_solace_kits 7 (they build instance buffers). Full suite not run.

## Gaps / for the next round
- The district hues are strong at squint, but at the plan camera the cool-teal district reads blue-white rather than teal; the dark gap blocks read as black slabs in places (23 % of the buildings in the plan frame are gap kind).
- The highway glow is a flat additive plane at deck height: at zoom 4 it reads as a soft slab over low roofs beside the deck.
- The plate's own squint still has more mid-scale structure (its route lines, the amber lower-left lattice).

## Slips
`python -` typed by reflex three times (twice at the start, once appended to a command with `</dev/null`); each hung until I stopped my own background task with TaskStop, no code was ever passed. No foreign files touched, no taskkill by image. A temporary git worktree of r18 (D:/rc_scratch/g1/r19/wt_r18) was added for the r18 renders and removed again (`git worktree remove`); scratch is in D:/rc_scratch/g1/r19/. No background processes left running.
