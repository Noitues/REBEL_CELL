You port one Python module of the REBEL_CELL netrun-art pipeline to a GDScript twin (Godot 4.7). The Python code is the ORACLE:
the twin must give the same numbers, in the same operation order, so that its output is byte-identical to Python after rounding
to 1e-4 (half up). Output exactly ONE fenced ```gdscript block holding the whole file, then at most 5 lines of notes (what you
changed on purpose, any doubt). No other prose.

## File rules
- `class_name <Name>` + `extends RefCounted`; tab indentation; static typing on every variable, parameter and return type;
  snake_case; a `##` doc comment on every public function and constant (one line is enough; copy the Python docstring's point).
- All functions are `static`. No Nodes, no scenes, no signals, no autoloads. No randomness calls at all.
- Public function names = the Python names (a leading underscore stays private). Arguments keep the Python order. A Python
  default of `None` becomes the "none value" given in the contract below. Python `raise` becomes `return {"error": "<message>"}`
  for functions that return a Dictionary (callers test `has("error")`); say so in the doc comment.
- Tuning numbers are NOT written as literals. Read them from `NetrunArtConfigData.shipped().<field>[key]` (field names in the
  config table below). Only structural constants (count of depth knots, the 4 faces, loop counts, 0/1/2 indices, 0.5 midpoints,
  1e-6 style epsilons that the Python source also writes inline) may be literals, as `const` with a `##` doc where they are named
  in the Python source. A Python module constant that is a number from the config table is read from config each time you need it
  (cache it in a local variable inside the function).
- Data is JSON-shaped: `Dictionary`, `Array`, `String`, `float`, `int`, `bool`. NEVER Vector2/Vector3/Transform (they are 32-bit
  floats and break parity). A point is `Array` of floats, e.g. `[x, y, z]`. Poses are `NetrunPose` (see below).
- INT vs FLOAT matters: the output is serialized and a Python `int` prints `3`, a float prints `3.0`. Keep every value the same
  type as in Python (ids, layer numbers, floor numbers, counts, indices are `int`; coordinates and weights are `float`). Write
  `0.0`, not `0`, where Python has a float. GDScript `int / int` is INTEGER division (Python `/` is true division): cast to
  `float` first, `//` becomes `int(floorf(...))` (or `a / b` on two ints, on purpose). Python `**` is `pow()` (or `x * x`, same value).
  `round(x)` is not `roundf` for ties; use the Python semantic stated in a comment if you meet one (prefer `roundf(x * 10.0) / 10.0`
  for `round(x, 1)`).
- Python `math.hypot(a, b)` -> `NetrunArtUnits.hypot(a, b)`; `math.radians/degrees` -> `deg_to_rad/rad_to_deg`; `sum(list)` ->
  `NetrunArtUnits.sum_f(list)` for float lists; `math.floor` -> `floorf`; `max/min` of two floats -> `maxf/minf`; of an Array -> `Array.max()/min()`
  (non-empty) or a loop. `math.log/exp/sin/cos/atan2/sqrt` -> same GDScript builtins.
- SORTING: Godot's `sort_custom` is NOT stable, and `Array.sort()` on strings is wrong for ids. Sort string ids with
  `IdSort.sort_ids(arr)`. For tuple keys (`key=lambda q: (q["a"], q["b"])`) write a comparator that compares ALL key parts in
  order (ints/floats with `<`, strings with `String(a) < String(b)`), so the order is total and stability is irrelevant. Python
  `sorted(d)` of a dict = sorted keys. Python `min(list of tuples)` compares lexicographically: write the loop.
- Aliasing: GDScript Dictionaries and Arrays are references. Python `dict(x)`, `list(x)`, `x[:]`, `tuple(x)` copy: use
  `.duplicate()` / `.duplicate(true)` where Python copies or where you later mutate a value the caller still holds. Never mutate
  an argument unless Python does (then the doc comment says so).
- Python truthiness: `if x:` on a list/dict/str is "non-empty", on a number "non-zero". `x or default` likewise.
- Python dict iteration is insertion order; GDScript Dictionary too. A Python `set` becomes a `Dictionary` used as a set (key -> true).
- The result must parse with no warnings-as-errors: no unused variables, no shadowed names (do not name a variable `range`, `seed`,
  `sign`, `floor`, `ceil`, `round`, `min`, `max`, `abs`, `len`, `dir`, `pow`, `log`), no `var x := <Variant>` (annotate the type).
  Use `maxf/minf/clampf/absf/floorf` for floats, `maxi/mini/absi` for ints. Variables named `F`, `u`, `v` are fine.
- Do not add behaviour that is not in the Python module. Do not port Blender, file I/O or test-only helpers. Skip anything the
  contract below marks as skipped.

## Optional / none values (contract)
- Python `Optional[str]` (a node id or None) -> `String`, `""` means None.
- Python `Optional[Sequence]` / `Optional[Pt3]` -> `Array`, `[]` means None.
- Python `Optional[dict]` override (`rig`, `rules`, `params`, `cfg`, `partial`, `bands`, `floors`, `z`) -> `Dictionary`, `{}` means None (merge over the config default).
- Python `Optional[float]` -> `float` with default `NAN`; test with `is_nan(x)`.
- Python function returning a point/tuple -> `Array`; returning `None` for "no result" -> empty `Array` / empty `Dictionary` (stated per function below).
- `NetrunPose.proj` returns `[]` when the point is behind the camera (Python None).

## Config table: `NetrunArtConfigData.shipped()` fields (all Dictionary unless noted; keys = the Python keys)
`units` {floor_bu, kit_storey, k_fit}; `rig` (= Python `rig.RIG`: yaw_max, pitch_d, lens_d, fill_w, fill_h, look_bias, hover_pull,
hover_yaw, hover_dolly, ov_yaw_k, pitch_o, lens_o, fill_ow, fill_oh, ov_base_frac, t_step, t_hover_in, t_hover_out, t_zoom, sensor_mm,
ref_w, ref_h, use [x0,y0,x1,y1], solver_iters, solver_bracket [lo,hi]); `look_bias_sign` (float field); `dive` (= `rig.DIVE`: duration_s,
hq_lens, hq_yaw_l36, hq_pitch, lag_k, lag_pow); `hq_page` (= `rig.HQ_PAGE`: fit_margin, fit_share, anchor, ortho_clamp, grid_ortho, free);
`hq_rig` (= `orbit.HQ_RIG` but with `dmin_kit` = 135.0 instead of `dmin`; the rig's dmin is `NetrunArtUnits.kit(dmin_kit)`);
`occlusion` (= `occlusion.OCC` keys cone_margin, stub, ghost, edge, tsoft, vsoft, plus front_fade_kit 6.0, clutter_kit 25.0, ease_s, min_span;
`FRONT_FADE = kit(front_fade_kit)`, `CLUTTER = kit(clutter_kit)`); `lod` {d0, d1, bands {name: [a, b]}, floors, ramps, ramp_levels};
`section` {zcut {zf, zn, a, b}, look_blend [a, b], no_cut, poche, edge_col, band_overview_kit 30.0, band_rooms_kit 24.0, zref_margin_kit 1.5,
plinth_kit 0.6, widen}; `street_rules` (= `derive.street.RULES` without floor_bu, front_band, extend); `layout` {front_band, extend, base_tol, axis_tol};
`slot_params` (= `hq.slots.SLOT_PARAMS`); `landmark_entries` ({corp: {entry, entry_nrm}}); `reveal` ({asset: [[tier, d_far, d_near], ...]});
`frustum_tolerance` (float field). Section `CONSTS` of the Python module = {k_units, k_fit, band_overview = kit(30.0) * K_FIT,
band_rooms = kit(24.0) * K_FIT, zref_margin = kit(1.5) * K_FIT, plinth = kit(0.6), widen}, built from those keys with the same arithmetic.
Config arrays that Python holds as tuples (`front_band`, `extend`, `use`, ...) are `Array`.

## Support classes that already exist (use them, do not redefine)
`NetrunArtUnits` (static): `NEAR_Z`, `floor_bu()`, `k_units()`, `k_fit()`, `kit(v)`, `r4(v)`, `smoothstep01(t)`, `clamp01(x)`,
`lerp_f(a, b, t)`, `sub3(a, b)`, `dot3(a, b)`, `cross3(a, b)`, `norm3(a)`, `dist3(a, b)`, `hypot(x, y)`, `sum_f(arr)`,
`merge(base: Dictionary, over: Dictionary) -> Dictionary` (= Python `dict(base, **over)`, deep copy of base).
`NetrunPose` (RefCounted; fields `F: Array`, `yaw`, `pitch`, `dist`, `lens`, `sx`, `sy`): `NetrunPose.make(focus: Array, yaw, pitch, dist, lens, sx = 0.0, sy = 0.0)`,
`dir() -> Array`, `loc() -> Array`, `proj(P: Array, shift: bool = true) -> Array` (`[]` behind camera), `to_json() -> Dictionary`,
`NetrunPose.from_json(js: Dictionary)`, `mix(o: NetrunPose, t: float) -> NetrunPose`.
`IdSort.sort_ids(arr: Array)` for string ids.

## The twin modules and their public API (every module you write must call the OTHERS exactly as written here)
`NetrunCameraRig` (rig.py): `ease(t)`, `ease_out(t)`, `smootherstep(t)`, `yaw_to_rig(yaw_l36: float) -> float`, `yaw_of_nrm(nrm: Array) -> float`,
`unwrap_yaw(y, ref) -> float`, `bbox_px(pose: NetrunPose, pts: Array) -> Array` (`[x0, y0, x1, y1]`, EMPTY when no point is in front of the camera),
`frame_points(pts: Array, yaw: float, pitch: float, lens: float, fw: float, fh: float, bias: float = 0.0, centre: Array = [], dmin: float = 0.0) -> NetrunPose`,
`room_corners(room: Dictionary) -> Array`, `room_center(room: Dictionary) -> Array`, `street_yaw0(nrm: Array) -> float`,
`street_overview(rooms: Dictionary, nrm: Array, start_left: bool, rig_over: Dictionary = {}) -> NetrunPose`, `street_u(layers: int, current_layer: int) -> float`,
`street_decision(rooms: Dictionary, current: String, options: Array, u: float, nrm: Array, start_left: bool, rig_over: Dictionary = {}, entry: Array = []) -> NetrunPose`,
`street_hover(decision: NetrunPose, target_room: Dictionary, nrm: Array, k: float = 1.0, rig_over: Dictionary = {}) -> NetrunPose`,
`hq_page_camera(net: Dictionary) -> Array` (`[target: Array, width: float]`), `hq_page_pose(target: Array, width: float) -> NetrunPose`,
`dive_pose(u: float, hq: NetrunPose, ov: NetrunPose) -> NetrunPose`, `dive_distance(p: NetrunPose, ov: NetrunPose) -> float`,
`street_rig_json() -> Dictionary` (`dict(RIG, look_bias_sign=LOOK_BIAS_SIGN)`), `dive_constants() -> Dictionary` (a copy of the `dive` config).
`NetrunHqOrbit` (hq/orbit.py): `hq_rig() -> Dictionary` (config `hq_rig` without `dmin_kit`, plus `dmin = kit(dmin_kit)`), `room_normal(room) -> Array`, `face_index(room) -> int`,
`decision_yaw(rooms: Dictionary, ids: Array, look_ahead: float = 0.0) -> float`,
`hq_decision(rooms: Dictionary, current: String, options: Array, layer_idx: int, n_layers: int, rig_over: Dictionary = {}, entry: Array = []) -> NetrunPose`,
`hq_hover(decision: NetrunPose, room: Dictionary, k: float = 1.0, rig_over: Dictionary = {}) -> NetrunPose`, `overview_yaw(rooms: Dictionary, live: Array, current: String) -> float`,
`overview_points(comp: Dictionary) -> Array`, `hq_overview(rooms: Dictionary, comp: Dictionary, live: Array, current: String, rig_over: Dictionary = {}) -> NetrunPose`,
`visible_room(room: Dictionary, pose: NetrunPose, margin: float = NAN) -> bool`.
`NetrunHqSlots` (hq/slots.py): `const FACES: Array = [[0, 1], [1, 0], [0, -1], [-1, 0]]` (ints), `slot_params() -> Dictionary`,
`hq_lot_rect(city: Dictionary, corp: String) -> Array` (`[x0, x1, y0, y1]`), `plan_compound(rect: Array, n_tiers: int, params_over: Dictionary = {}) -> Dictionary` (or `{"error"}`),
`set_entrance(comp: Dictionary, overview: NetrunPose, corp: String = "") -> Dictionary` (mutates and returns comp), `place_slots(run_graph: Dictionary, rect: Array, hq_bid: String, n_parts: int = 1, params_over: Dictionary = {}) -> Dictionary` (rooms by node id, or `{"error"}`),
`room_slot_box(room) -> Array`, `overlaps(rooms) -> Array`, `inside_rect(room, rect) -> bool`, `link_paths(rooms: Dictionary, edges: Array, params_over: Dictionary = {}) -> Array`,
`derive_hq(city: Dictionary, run_graph: Dictionary, corp: String, partial: Dictionary = {}, params_over: Dictionary = {}, rig_over: Dictionary = {}) -> Dictionary` (or `{"error"}`).
`NetrunStreetDeriver` (derive/street.py): `const ROOM_KINDS: Array`, `const LINK_TYPES: Array`, `rules() -> Dictionary` (Python `RULES`: config `street_rules` + `floor_bu` from units + `front_band`, `extend` from config `layout`),
`floors(b: Dictionary, rules_over: Dictionary = {}) -> int`, `frontage(B: Array, a: Array, c: Array, side: int, rules_over: Dictionary = {}) -> Array`, `layer_nodes(run_graph: Dictionary) -> Array` (`[[layer: int, nodes: Array], ...]`),
`assign(front: Array, layers: Array, span: int = 1, rules_over: Dictionary = {}) -> Array` (`[out: Array of [layer, b], ok: bool]`),
`choose_street(B: Array, legs: Array, layers: Array, rules_over: Dictionary = {}) -> Dictionary` (EMPTY when Python returns None; else keys `score` (Array), `li`, `side`, `a`, `c`, `front`, `asg`, `ok`, `start_left`),
`select_link(net: Dictionary, site: String) -> Dictionary` (`{link, pts}` or `{"error"}`), `room_boxes(asg: Array, layers: Array, span: int, rules_over: Dictionary = {}, ground_z: float = 0.0) -> Dictionary`,
`link_paths(rooms: Dictionary, edges: Array, rules_over: Dictionary = {}) -> Array`, `normalise_quad(q: Array, nrm: Array) -> Array`,
`derive_street(city: Dictionary, net: Dictionary, run_graph: Dictionary, site: String, partial: Dictionary = {}, rules_over: Dictionary = {}, rig_over: Dictionary = {}) -> Dictionary` (or `{"error"}`).
`NetrunArtLayout` (layout.py, WITHOUT `apply_layout_rules`): `lot_to_plan(lot: Array, origin_lot: Array, lot_bu: float) -> Array`, `plan_to_lot(...)`, `poly_bbox(poly: Array) -> Array` (`[x0, x1, y0, y1]`),
`base_part_index(b: Dictionary) -> int` (-1 for None), `building_info(b: Dictionary) -> Dictionary` (EMPTY for None), `merged_buildings(city: Dictionary, include_hq: bool = false) -> Array`, `border_links(net: Dictionary) -> Array`,
`street_cells(city: Dictionary) -> Dictionary` (set of `Vector2i`), `route_on_streets(city: Dictionary, a: Array, b: Array) -> Array`, `link_legs(city: Dictionary, pts: Array) -> Array`, `leg_axis(a: Array, c: Array) -> int`.
`OcclusionHelper` (occlusion.py): `const NK := 5`, `keys() -> Array` (the 28 `occ_*` names), `occlusion_params(cam: Array, pts: Array, cfg: Dictionary = {}) -> Dictionary`, `occlusion_state(p: Dictionary, b: Array) -> Array` (`[cut_height, opacity]`),
`building_boxes(city: Dictionary, skip: Dictionary = {}) -> Array` (rows `{bid, box: [x, y, top, hx, hy]}`; skip = set of bids), `occlusion_block(params: Dictionary, boxes: Array, eps: float = 1e-4) -> Dictionary`,
`rail_segments(rail)`, `corridor_dist(segs, x, y)`, `in_corridor(segs, x0, y0, x1, y1)`, `rail_cap(rail, x, y, h) -> Array` (`[h, capped]`).
`RevealTiers` (lod.py + reveal tiers): see its request. `NetrunSection` (section.py): `zcut(zoom: float, z: Dictionary = {}) -> float`, `look_w(zoom: float, blend: Array = []) -> float`,
`consts() -> Dictionary`, `section_params(pose_loc: Array, keep: Array, rooms_pts: Array = [], zref: float = NAN, zref_k: float = 1.0) -> Dictionary` (keep `["rect", hx, hy]` / `["circ", r]` / `[]`), `section_block() -> Dictionary`.
`NetrunPoseBuilder` (poses.py): see its request.
