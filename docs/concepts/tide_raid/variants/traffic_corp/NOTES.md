# Variant: traffic carries the corporation colour (branch art/tide-traffic-corp in D:/rc_art/godot_look_traffic, from art/tide-r43 e2c9976c)

Pictures (r43 left, variant right): plan_, seed3_, closeup_, deck_, beat02_ `*_r43_vs_variant.jpg`; compare.jpg (all five at 960x540); squint_r43_vs_variant.png (blur 10 px, shrunk to 1/16, shown enlarged); traffic_motion.gif (r43 | variant, street-level close-up at zoom 5 on lot -57,3, 5.3 s at 15 fps, 12.2 MB). Sheets by tools/compose_traffic.py, gif by tools/make_gif.py. Raw PNGs are in D:/rc_scratch/traffic/ (cap/, lab/, movie/, movie_b/).
Cameras: plan = r43 plate camera, seed 7; seed 3; deck = lot -60,-22 zoom 2.2 (the "deck / viaduct" view (the r42 deck command was not kept: this is a re-fit, about 60 px off the r42 frame); closeup = zoom 5 at lot -57,3 (street level, where the street cars read); beat02 = tide lab daemon frame 60 with the raid grade.

## The switch
`CityConfig.traffic_corp_colour_on` (content default false = r43; verified: the plan capture with it off is the r43 look, test_city_traffic_corp). Capture: `--set=traffic_corp_colour_on=true` (parity_capture and the tide lab now both take `--set=`; parity_capture also `--every=K`).
ON does this, and nothing else changes:
- No avenue strips (CityNeonKit.avenue_strips is not appended; masts and bay bank stay).
- Every car light takes a seeded corporation (CityTrafficCorp): weights = CityCorpColor.weights (random, HQ-boosted, cap 0.65), draw = hash of car key and city seed, so it is deterministic per seed. Applies to all four traffic sources: the deck streaks (CityA2Features._traffic, the "one entity each" quads), the avenue dashes (CityNeonKit), the street cars and the sky cars (sky_car.gdshader, COLOR = corp colour, head / tail derived in the shader).
- Config (CityConfig, no magic numbers): `traffic_head_white` 0.6 (head = lerp(corp, white, 0.6)); `traffic_tail_value` 0.55 and `traffic_tail_saturation` 1.0 (tail = corp hue, S 1.0, V 0.55); `traffic_corp_salt` 7331; deck HDR gains `traffic_hwy_head_gain` 5.0 / `traffic_hwy_tail_gain` 6.0 (the r43 peaks, so the dark tail still glows); glow `traffic_glow_gain` 1.3, `traffic_halo_width` 2.0, `traffic_halo_gain` 0.18 (a soft halo quad under each deck streak and avenue dash; a gain on the street / sky car lights).
- Colour values: corp colours (CityConfig.corp_colors) solace (0.588,1,0.275), halcyon (0.69,0.43,1), meridian (1,0.55,0.10), orbital (0.80,0.94,1), aurelian (0.16,0.86,0.65). Heads (lerp 0.6 to white): solace (0.835,1,0.71), halcyon (0.876,0.772,1), meridian (1,0.82,0.64), orbital (0.92,0.976,1), aurelian (0.664,0.944,0.86). Tails (hue, S 1.0, V 0.55): solace (0.237,0.55,0), halcyon (0.251,0,0.55), meridian (0.55,0.275,0), orbital (0,0.385,0.55), aurelian (0,0.55,0.385). On the deck both are multiplied by the HDR gains and the glow gain.

## Colour removed from the roads (designer follow-up; found by hiding layers one at a time)
1. Chunk `Lanes` (CityMeshKit.lane_mesh_of): the lane glow strips of the street lots, the bundles of thin parallel pink / green hatch lines. Neutral now: `traffic_lane_neutral` (0.80,0.82,0.90) x `traffic_lane_neutral_gain` 0.45, same strokes and beds.
2. A2 `RoadGlow` (arterial / collector glow, interchange edges): luminance grey x `traffic_road_neutral_gain` 0.8 (CityA2Features._road_tint).
3. The highway deck edge rails (hwy_rail_colors, pink / green / cyan / amber): same grey tint.
4. The avenue strips (the original request) and the avenue neon-glow bands.
Checked and left: NeonHaze (general bloom, not a road mark), building / sign light, the sky-lane cars' lane lines (traffic, coloured by corp now), the Network layer (netrun only). Not checked: wet-street specular streaks of sign light on asphalt (they take the light's own colour, so they are not road colour; none visible in the close-up).

## Self-review
- Does the street network still read without the colour strips? Mostly no, outside the viaducts. In the plan the viaducts and the ring still carry the structure (white / corp dashes on dark deck), but the low-rise district at left lost its coloured grid and the streets are now dark grey slots between blocks; the grid is read only from building rows and the few street-car dashes (street cars are tiny at plan scale). At the close-up the street cars give a faint line along each road. This is the main cost of the variant. Option for the designer: a faint neutral street line (raise `traffic_lane_neutral_gain` to about 0.9) keeps the grid without colour.
- Do the corp colours still cluster near each HQ? In the plan the colour now sits only in the deck streaks (violet near the Halcyon side, green / teal near Solace, amber toward Meridian) and the building lights; the building clustering is unchanged (r43 corp colour), and it carries the HQ reading, not the traffic. The traffic colour is too small to show a clustering at plan scale and weights only the deck cars along the deck's length; the deck is mixed (5 corps, cap 0.65). At the deck and close-up zoom the cars show the mix clearly (cars near an HQ lean to its colour; test_city_traffic_corp pins the lean and the cap).
- Squint: r43 gives bright linear colour marks (yellow / cyan / green avenue lines) that survive the blur and make the grid; the variant squint is a calm purple-green mass with only the viaduct lines and a few warm dots. Calmer and less garish, but the squint no longer shows the street network. The deck streaks fuse to dashed white-ish lines (white heads dominate).
- Glow: after the follow-up the heads read as bright points at deck zoom; at the halo setting above the deck streaks start to fuse into a dashed band (halo 3.0 / 0.30 merged them into a checkerboard, so it was cut to 2.0 / 0.18).
- Open: the deck streaks are static quads (not moving) in this build; only the street and sky cars move (gif). The street and sky cars are small at plan zoom.

## Perf (level-3 city GPU p95, limit 12.57 ms), D:/rc_scratch/traffic/cap/log_perf_l3_*
Variant p95 7.22 ms (mean 4.32); r43 measured in the same session 9.76 ms (mean 5.72; the GPU clock state differs run to run, as in round 43). Both under the limit; the variant adds only a few quads.

## Tests
Targeted: test_city_traffic_corp (new, 5 tests: switch off by default, car corp deterministic per seed, lean to HQ and cap, head / tail tints, roads carry no colour with the switch on), test_city_motion, test_city_neon_kit, test_city_a2, test_city_sky, test_city_road_audit, test_city_interchange_kit, test_tide_raid_grade: all pass (60 + 33 + 5 tests, 0 failing). Full suite not run (as asked). Manifest entry added (fast).

## Slips
`python -` was started by mistake twice (stdin hang, stopped with TaskStop, nothing written). A foreign D:/rc_tmp/inspect.py shadows the stdlib when a script lives in D:/rc_tmp; scripts now run from other folders. Stray Stop-Process on my own chain was denied; I let the chain finish.
