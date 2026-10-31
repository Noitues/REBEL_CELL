# Zoom rules, round 3: the staged street (ART CALL 48)

Godot: `D:/rc_art/godot_look_tide`, branch `art/netrun-zoom` (round-3 commit b8a1d115). View only, off by default, `zr_*` in `CityConfig`.

## The big find: the street camera was rendered 1.8x too zoomed in rounds 1-2
`CityView3D.set_iso` gave the frustum `size` as the frame HEIGHT, but the camera keeps its WIDTH, so the render was 22.6 degrees vertical (ppb about 68) instead of 40 (ppb 38): the frontage sat below the frame, the "road" never showed, the bottom 20 % of the round-1/2 frames was a 1.8x copy of the frontage's own shop band, and `get_camera_projection()` and my numbers agreed with each other and not with the pixels. Found with two red marker poles at known ground points (their bottoms were below y 1080 instead of at 872 and 949). Fixed (size = width, lens shift = share of the height). Everything below sits on that fix; the horizon is 0.74, the frontage base lands at y 872 (81 %) as the plate.

## 1. Staged street (view only, deterministic, gated)
`CityZoomStage` (pure): `cells` = the widened road, `zr_stage_rows` = 3 rows of lots (36 m, 3x a one-lot street) in front of the frontage line, across the frame + 2 lots; `hidden_prisms` = the buildings standing on those lots dissolve like any occluder; the facing row is never touched (heights and positions are the real ones; test compares the prism data before/after). The road mesh uses the road shader's lot data (axis across the view, `off` per row, `w` 3) so it gets markings; the dress treats the cells as street so the frontage walls get bands, signs and lamps; the highway pillars are hidden in the staged view (that was the pylon on the right third). Gate `CityZoomStage.active`: view rules on + perspective camera + street band fully in (melt 1) + `zr_stage_on`; the City view and rules-off are untouched (City-band diff below).
Node rule: `frame_top_bu` / `node_floor`: a node or marker gets the highest floor whose top is at least 1 BU under the frame top at its depth and not above the building (about 21 BU = 42 m of facade above the eye at the frontage). Not yet wired to a route (no node placement exists in this branch); it is the function item 10 must call.

## 2. Lit and wet hero street (partly)
Done: paved asphalt with edge lines, double yellow, zebra, across the whole widened width; storefront window gain x3.0; body above the shop zone dimmed to 0.4 albedo / 0.4 lit emission; road gloss and reflection gain up (0.6 base, 1.8); a staged lamp row (`CityZoomStage.lamps`: 7 m poles every 9 BU along the frontage kerb with lit heads and light pools of 6.4 BU at gain 1.8); corp-colour car streaks on the widened road (rule of CityTrafficCorp, which I reimplemented as `CityZoomRoad.car_*` in round 2: head = lerp(corp, white, 0.6), tail = corp at V 0.55, gain 3.0).
Measured (`scripts/lum_profile.py`, `roadshare.py`): brightest 24 px row at **80 % down** (y 864; the shop band and its kerb line; target 70-75 %), value 0.53, **ratio to the facade mean 2.24** (plate 2.72, round 2 1.58, target 2.5), frame mean 0.27 (plate 0.20); **road share 19.3 % of the frame** (y 872 down; round 2 about 0). Not reached: 2.5x and 70-75 %; the streaks and light pools are visible but faint, the road is a dim matte violet with little visible reflection of the signs, and the lamp poles are thin.

## 3. Real city behind, ZOOM_RULES detail on top
Unchanged real prisms with the facade grammar, fascia text, T2-T4 signs, tower fade and fog from rounds 1-2. The frame is lot (34.5,-9.0) N.

## Perf (GPU city viewport, 500 frames, frozen capture)
Street p95 **3.18 / 3.20 / 5.49 ms** (limit 12.57); District p95 2.36 / 2.33 / 2.33 ms. The GPU was uncontended this time (the camera now sees the real frustum, far fewer pixels of near geometry); `logs/perf_run*.log`.

## City band: bit-exact
Stage 1, fresh processes OFF / ON / OFF: **0 differing pixels** in ON vs OFF1, ON vs OFF2, OFF1 vs OFF2.

## Tests
New `tests/unit/test_city_zoom_stage.gd` (6): widening is 3 rows, deterministic, in front of the line for every look, never inside the frontage row; view-only (prism data unchanged, only the building on the road is hidden); the gate (rules off, orthographic, above the street band, null camera, default off); the node floor rule (inside the frame, caps by building height, grows with depth, ground floor at the lens). Targeted run, the round-2 list plus the stage script: **295 tests, 0 failing, 11 pending** (`logs/targeted_tests.log`). Not run: full suite, schema smoke, validate_content.

## Self-review against the plate
Matched: frontal long-lens frame with the frontage base at 81 %, a wide road filling the bottom fifth with markings, mid-rise row with shops and signs under a layer of fogged towers, a lamp row, no dominant slab, no pylon.
Not matched: ratio 2.24 vs 2.72 and the brightest row 10 points too low; faint streaks, no bokeh, weak sign reflections in the road; flat facades (no AC boxes, pipes); the frontage row here is dense mid-towers rather than the plate's lower row with towers behind; one cross street opens in the centre of the row. **Squint: closest yet and a PASS on structure (towers over a lit band over a wide road), still weaker than the plate on the one bright horizontal and on the wet foreground.**
