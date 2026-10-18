# NA-03 module map: concept sources, signatures, spec sections, NA-02 fields

Date 2026-10-18. Orchestrator pre-write for `docs/handoff/plan2/drafts/briefs/na03.md`. Input to the NA-03 batch drafts.

Sources of truth, in order: `docs/handoff/plan2/NA02_FIELDS.md` (incl. its Rulings section; it wins over the spec),
then `docs/handoff/netrun_art/PIPELINE_SPEC.md` (re-imported from art-pass b68f2871), then the concept scripts.
Spec deltas D1-D12 and Rulings O1-O13 in NA02_FIELDS are binding. "NA02 sN" = section N of NA02_FIELDS.

## 0. Pinning and reading rules

| Item | Value |
|---|---|
| Concept repo (READ ONLY) | `C:/Users/noitu/Documents/Godot/rebel_cell`, branch `art-pass`, tip `6a58733cb8a461e6485de1eb32a1514275c6a52b` at 2026-10-18 |
| Pin form | per file: the last commit touching it (`git -C <repo> log -1 --format=%H art-pass -- <path>`), 8-char abbreviation; read with `git -C <repo> show art-pass:docs/concepts/<path>` |
| Never | copy `docs/concepts/` into main; import a concept script from main; edit the art-pass repo |
| Path roots below | `SB/` = `route_map_graph/storyboard/scripts/`; `M44/` = `SB/m44/`; `V3D/` = `route_map_graph/side_view/v3_dynamic/scripts/`; `HK/` = `route_map_graph/hq_meridian/scripts/hq_kit/`; `HM/` = `route_map_graph/hq_meridian/scripts/`; `CAC/` = `city_all_corps/scripts/`; all under `docs/concepts/` |
| Signature column | Python signature as written in the concept source. The sources are **untyped**: arg types and units in brackets are read from the function body or the spec and marked `~`; NA-03 adds annotations. Nothing here is a new API |

## 1. Cross-cutting findings (apply to several modules)

| # | Finding | Effect on NA-03 |
|---|---|---|
| X1 | No concept module imports `bpy` in its logic, except the ones marked **BPY** below. `bpy` appears in `HK/section.py` (shader insertion), `M44/onecity_build.py`, `M44/onecity_cycles.py` | Only `section` (part) and `dress` (part) need a split |
| X2 | `derive`, `rig` (street) and `hq.slots` read a **mock route graph**: `sgraph3` (`WALK_START`, `NODES`, `LAYER`, `K`, `KIND`, `states`, `edge_states`, `room_corners`) and `hq_graph` / `hqk_graph` tables. NA-02 replaces it with `run_graph.json` (NA02 s4) | The ports take a `run_graph` dict and never import a mock; the mock stays a test fixture (spec 8.4) |
| X3 | Concept buildings are keyed by legacy `key` (int) and carry `q` (polygon in lots), `ts` (taper), `x0..y1` in world BU. NA-02 uses `bid` (string), `parts[] {poly, z0, h, taper}`, already BU (NA02 s2, C2) | Every `key` in a signature or output becomes `bid`; `ts` becomes `taper`; `z0*KH` conversions drop (heights are BU). `buildings[].key` stays only for the `frontage_min_floors` jitter `abs(key) % 3` |
| X4 | Concept code draws randomness from `random.Random(<literal>)` (e.g. `9970 + k`, `7719`) and Python `random` module-level calls. NA-02 s7 forbids this in the pure modules | Replace by `seeds.splitmix64(seeds.art_seed(layout_seed, stream, *keys))`. Python `random` only in Blender-only dressing (NA-05) |
| X5 | Concept scripts load fixed paths (`scratch/layout/unified*.json`, `net36.json`, env `NET36`) and write files from `main()` / module top level | Ports are functions on dicts; file I/O only in `io.py` and CLI shims |
| X6 | Concept `derive()` returns tuples and 3-tuples (`front`, `path`); NA-02 s1 requires JSON arrays and floats rounded to 1e-4 | `io.canonical_dumps` is the only writer; modules return plain lists/dicts |
| X7 | numpy and PIL are imported by `zoning_a2.py`, `zoning.py` (raster, k-means, maps) and by `states.py` (image drawing). Not `bpy`, but not stdlib | Open O-A: allowed deps for `tools/netrun_art/` are not stated |

## 2. Summary

| # | Module (file in `tools/netrun_art/`) | Pinned concept source (path under `docs/concepts/`, commit) | Spec section | BPY in logic |
|---|---|---|---|---|
| 1 | `seeds.py` | `HANDOFF_PACKAGE/na02/seeds_ref.py` 6a58733c (frozen copy on main: `tools/netrun_art/fixtures/seeds_ref.py`) | 3.5, NA02 s7 | no |
| 2 | `io.py` | none (new). Rules: NA02 s1, Ruling O12; spec 11.5 | 11.5, 2.0c | no |
| 3 | `layout.py` | `M44/layout36.py` 96c1af6f; `SB/sb_onecity.py` c83e3b00 (`apply_layout_rules`, `merged_buildings`, `bld_info`) | 2.2 `layout.*`, 3.1, 3.2, 3.7 | no |
| 4 | `zoning.py` | `CAC/zoning.py` 306a6865 (rules Z1-Z6, L1-L4, T1); `CAC/zoning_a2.py` 16c427cd (planner raster); `CAC/city_preset.py` 16c427cd (numbers) | 3.4, 3.7 | no (numpy, PIL) |
| 5 | `derive/street.py` | `SB/sb_onecity.py` c83e3b00 (`derive`, `choose_street`, `frontage`, `assign`, `room_boxes`, `link_paths`, `frame`) | 3.3, 2.3 | no |
| 6 | `hq/slots.py` | `HK/layout.py` c47c67a9 (`Compound`); `HM/hq_graph.py` 46d161ce (Meridian tables, mover logic) | 8.1, 8.4, 2.3 | no |
| 7 | `rig.py` | `V3D/cam_rig.py` 47850a23; `SB/sb_ocjobs.py` c83e3b00 (`pose_at`, `zoom_of`, `mix`, `hover_pose`); `HK/orbit.py` c47c67a9; `HM/hq_cam.py` c47c67a9 | 6.1-6.5 | no (`sb_ocjobs` launcher code is Blender-side, not ported) |
| 8 | `lod.py` | `HK/lod.py` c47c67a9; `SB/look_preset.py` c83e3b00 (`PRESET["lod_bands"]`) | 5.1, 5.2, 5.2b | no |
| 9 | `occlusion.py` | `HK/downtown.py` 46d161ce (`occlusion_params`, `occlusion_state`, `_knot`, `_sstep`, `in_corridor`, `corridor_dist`, `corridor_low`) | 7.1-7.4, 12.4 | no |
| 10 | `section.py` | `HK/downtown.py` 46d161ce (`section_params`); `SB/sb_ocjobs.py` c83e3b00 (`zcut`, `look_w`); `HK/section.py` 46d161ce (constants only) | 5.3, 7.4 | **yes**, `HK/section.py:insert` and `M44/onecity_build.py:section` are shader code |
| 11 | `states.py` | `route_map_graph/hq_orbital/scripts/hq_kit/states.py` c47c67a9 | 8.1 `states` | no (PIL in two functions) |
| 12 | `dress.py` | `M44/onecity_build.py` c83e3b00 lines 98-126; `M44/onecity_cycles.py` c83e3b00 lines 169-371, 612-648 | 9, 4.1, 13.1 | **yes**, placement is interleaved with `_light`, mesh and material calls |

The `hq_kit` copies in `hq_halcyon`, `hq_orbital`, `hq_solace`, `hq_rebel_cell` are byte-identical to `hq_meridian` per spec 0
(`states.py` and `city_ring.py` exist only under `hq_orbital`).

## 3. Modules

### 3.1 `seeds.py` (spec 3.5; NA02 s7)

| Item | Detail |
|---|---|
| Source | `HANDOFF_PACKAGE/na02/seeds_ref.py` 6a58733c, 72 lines, stdlib only |
| Public functions | `fnv1a64(data: bytes) -> int` (u64); `art_seed(layout_seed: int, stream: str, *keys: int\|str) -> int` (u64; `TypeError` for float, bool or other key types; hashes `utf8(compact_json([str(layout_seed), "art/"+stream, *keys]))`, separators `,` `:`, `ensure_ascii`); `splitmix64(state: int)` generator of u64 draws (the docstring says "(next_state, value)" but the code yields the value only; trust the code); `uniform(x: int) -> float` (`(x >> 11) * 2**-53`) |
| Reads (NA-02) | `layout_seed`, the u64 decimal string of the `city.json` header (NA02 s2). The port accepts the string and `int()`s it, so `str(layout_seed)` reproduces the digits |
| Writes (NA-02) | `derive_<run>.json` `art_seeds {stream: "<u64 decimal>"}`: the unkeyed streams plus the base seeds of `variance`, `terrain`, `fauna.tethys`, `key_landmark.<corp>` (NA02 s6, D8) |
| Gate | 11 golden vectors in `tools/netrun_art/fixtures/na02_vectors.json` (brief says at least 5; use all 11, incl. u64 max, 2^53+1, a negative key, a non-ASCII key) |
| BPY | none |

### 3.2 `io.py` (spec 11.5, 2.0c; NA02 s1)

| Item | Detail |
|---|---|
| Source | none: new module. Rules come from NA02 s1 and Ruling O12 |
| Public functions | **no concept signature exists** (see Open O-B). Required capabilities: canonical dump, load, schema validation of the five NA-02 files and the derive file |
| Rules | UTF-8, LF, one trailing LF, no BOM; keys sorted by code point at every depth; floats rounded to 1e-4 and written fixed with trailing zeros trimmed to at least one decimal, no exponent, no `-0.0`, no NaN/Inf; ints within +-2^53; every u64 a decimal string; `version` int `1`; **pretty-printed, indent 1 space** (Ruling O12, which closes the whitespace gap in NA02 s1) |
| Reads / writes | all of `city.json`, `net.json`, `run_graph.json`, `key_locations.json`, `derive_<run>.json` |
| BPY | none |

### 3.3 `layout.py` (spec 2.2 `layout.import_city` / `import_net` / `rules`, 3.1, 3.2, 3.7)

| Source function | Signature (source) | Notes |
|---|---|---|
| `M44/layout36.py` 96c1af6f `W` | `W(p)` [`p`=(lot_x, lot_y) lots ~] -> (x, y) BU: `((p0-CX)*U, -(p1-CY)*U)`, `U`=6.0, `CX=CY=6.0` | Becomes `lot_to_plan(lot, origin_lot, lot_bu)`; `origin_lot` and `lot_bu` come from the `city.json` header, not constants |
| `layout36.lots` | `lots(wx, wy)` -> (lot_x, lot_y), inverse of `W` | same |
| `layout36.street_graph / nbrs / bfs / simplify / nearest_cell / junction` | cell-path helpers on lot cells | Link routing for the concept `net36.json`; NA02 Ruling O3: `links[].pts` = straight `[a, b]`, so the BFS routing is **not** ported in v1 |
| `layout36.build_network`, `transit_view`, `load_net` | `build_network(d, L, cell_base=None)`; `transit_view(net)`; `load_net()` | Build the concept `net36.json` from `citydata`; replaced by reading NA-02 `net.json`. Not ported |
| `SB/sb_onecity.py` c83e3b00 `apply_layout_rules` | `apply_layout_rules()` (reads/writes fixed JSON paths; no args) | The rules: `LAYOUT_RULES = dict(frontage_min_floors=6, border_street_width=8.0, base_street_width=6.0, hero_sign_rule=dict(blade=True, band=True, palette=("district_a","district_b")))`. Port as `apply_layout_rules(city: dict, net: dict, rules: dict) -> dict` (returns the new `city.json` dict). Frontage test: building z0 <= 0.05, near edge within `front_band` (0.8, 6.5) BU of a border link leg extended by `max(RULES["extend"])` = 60 BU; raise to `(frontage_min_floors + abs(key) % 3) * floor_bu + 0.1` where `floor_bu`=1.9; step the street face back by `(border_street_width - base_street_width) / 2` = 1.0 BU |
| `sb_onecity.merged_buildings`, `bld_info` | `merged_buildings()`; `bld_info(b)` | A street-level base plus stacked parts (z0 > 0.05, footprint inside the base) is ONE building, height = top of the highest part. In `city.json` this is already the `bid` with `parts`; the port reads it, it does not re-merge |

| NA-02 field | Direction |
|---|---|
| `city.json` header (`layout_seed`, `units`, `lot_bu`, `origin_lot`), `buildings[]` (`bid`, `cell`, `terr`, `hq`, `key`, `parts[] {poly, z0, h, taper}`), `streets[]`, `plazas[]`, `hqs{}` | reads (import_city); `layout.rules` writes the same shape back, with `parts[].h` raised and `parts[].poly` faces stepped back |
| `net.json` (`nodes[] {id, lot, state}`, `links[] {a, b, state, pts}`) | reads. Coordinates are **BU plan** (Ruling O3, overrides NA02 s3 "lots"); `pts` is the straight segment `[a, b]` |
| `city_base.json` (spec 2.2 intermediate) | no NA-02 schema; keep in memory, do not write (see Open O-C) |

Note: the concept rule picks "border" links by `l["state"] == "border"`. `net.json` link states are `open`, `locked`, `opened`
(NA02 s3); there is no `border`. See Open O-D. BPY: none.

### 3.4 `zoning.py` (spec 3.4 Z1-Z6, L1-L4, T1; 3.7)

| Item | Detail |
|---|---|
| Source | `CAC/zoning.py` 306a6865 (798 lines): public functions `ab(x, y)` (lots -> screen-aligned a/b, lots), `from_ab(a, b)`, `centroid(q)`, `kmeans(X, k, iters=60)`, `smooth(x, a, b)`, `main()` (lines 84-723, the whole rule set), `draw_map(O, path)` (PIL map, not ported). `CAC/zoning_a2.py` 16c427cd (474 lines): `lot(p)`, `lots(poly)`, `to_px(p)`, `raster(polys=(), lines=(), width_cells=0.0)` -> bool `[N, N]`, `dist_to(mask)`, `box_blur(a, r, passes=3)`, `smooth(x, e0, e1)`, `vnoise(shape_xy, cell, seed)`, `seg_d`, `in_poly`, `main()`, `draw_map` |
| Numbers | `CAC/city_preset.py` 16c427cd: `ZONING` (l.58), `WATER` (l.72), `BAY` (l.150), `RAIL` (l.162: `deck_z` 17.5, `side_cap` 15.5, `side_d` 1.2, `pier_step` 7.0, `ramp` 60.0, `end_ramp` 45.0), `LANDMARK_FP` (l.138), `SEEDS` (l.24, 7701-7708) |
| Required split | Both `main()` functions are monolithic: they read fixed paths (`CP.A2_JSON`, `CP.ZONED`), draw randomness from `random` with `SEEDS` literals, and write `zoned.json`. Port as `zone(city: dict, key_locations: dict, preset: dict, layout_seed: str) -> dict`. Drop `draw_map`. The A2 planner raster path (`zoning_a2.py`) is a concept-city adapter (spec 2.0b): NA-03 reads `city.json` only |
| Reads (NA-02) | `city.json` (`buildings[].terr/cell/hq`, `streets[].traffic`, `hqs{}`), `key_locations.json` (`locations[].bid`, for clearances; spec 2.0c) |
| Writes | `zoned.json`: **no NA-02 schema** (Open O-C). Spec 2.2 lists its content: district per building, HQ lots, landmark clearances, coast, drowned quarter, arterials, aqueduct, the freight-rail polyline + `deck_z` |
| Seeds | `zoning` .. `post` streams: names between them are not given (Ruling O6: absent until art-pass names them). Use only named streams; do not invent |
| BPY | none (numpy, PIL) |

### 3.5 `derive/street.py` (spec 3.3, 2.3)

| Source function (`SB/sb_onecity.py` c83e3b00) | Signature (source) | Output / notes |
|---|---|---|
| `floors` | `floors(b)` [`b` building dict with `h`, `ts`, `x0..y1`, `axis` ~] -> int | Usable floors: `int(h / floor_bu)`; on a tapered building (`ts` < 0.99) only floors whose setback at the room top stays within `max_setback` |
| `frontage` | `frontage(B, a, c, side)` [`a`,`c`: leg ends, BU plan; `side`: +1/-1] -> list of dicts (`along`, `face`, `nrm`, `axis`, `dirn` added), sorted by `(along, key)` | Sort tie-break must become `(along, bid)` (CLAUDE.md rule 7) |
| `assign` | `assign(front, span=1)` -> `(list[(layer, building)], ok: bool)` | Layer to frontage building in link order, skipping a building without the floors |
| `choose_street` | `choose_street(B=None)` -> tuple `(score, leg_index, side, a, c, frontage, assignment, start_left)` | Score `(len(asg), nfl, 1 if start_left else 0)`; best by max, first wins on ties (deterministic) |
| `room_boxes` | `room_boxes(asg, span)` -> `{node id: {front: [4 x (x, y, z)], back: [4 x (x, y, z)], floor: int, span: int, bld, parts, layer, kind}}` | World BU 3-tuples; `bld` becomes `bid`, `parts` become `bid` list |
| `link_paths` | `link_paths(rooms)` -> `[{a, b, type: "facade", path: [4 x (x, y, z)]}]` | Manhattan polyline on the facade plane, 0.5 BU in front of the faces |
| `cam`, `proj`, `frame`, `street_yaw` | `cam(target, yaw, pitch, dist, lens, sx=0.0, sy=0.0)`; `proj(c, p)`; `frame(pts, yaw, pitch, lens, fw, fh, bias=0.0)`; `street_yaw(nrm)` | Pose solving: shared with `rig.py` (3.7). The concept uses layout36 `W_, H_ = 1920, 1080` as the frame |
| `derive` | `derive(span=None)` -> dict(`col_info`, `edges`, `floor_px`, `leg`, `side`, `a`, `c`, `nrm`, `start_left`, `span`, `columns`, `route_keys`, `street_len`, `rooms`, `overview`, `decision`, `frontage`) | Port as `derive_street(city: dict, net: dict, run_graph: dict, site: str, rules: dict) -> dict` returning the NA02 s6 keys. `RULES`: `front_band` (0.8, 6.5), `floor_bu` 1.9, `base_floor` 0, `room_inset` 0.45, `room_depth` 2.6, `room_px_target` 46.0, `min_width` 2.5, `max_setback` 0.6, `extend` (12.0, 60.0), `ov_pitch` 2.0, `ov_base_frac` 0.815 |

| NA-02 field | Direction |
|---|---|
| `city.json` `buildings[]` (`bid`, `parts`), `streets[]` | reads |
| `net.json` links `pts` | reads: the selected Site's border link polyline (concept `link_pts()`: link between `RELAY` and `SITE`) |
| `run_graph.json` (`nodes[] {id, layer, index, type}`, `edges`) | reads, replaces the `sgraph3` mock (X2). Concept `kind` per room (`G.KIND`) must come from node `type`: values `router`, `terminal`, `mainframe`, `server_rack` (NA02 D9, O13) |
| `derive_<run>.json` | writes `street` {a, c}, `nrm`, `start_left`, `span`, `columns [[layer, bid]]`, `route_keys [bid]`, `col_info [{layer, bid, top, u0, u1, face}]`, `rooms`, `edges`, `overview`, `decision`, `frontage [[bid, h, floors, taper]]` into the partial file the game wrote (Ruling O4). `key` -> `bid` everywhere (C2). Concept returns `columns` as `(layer, key)` tuples |
| Nested shapes | NA02 Ruling O10: NA-03 freezes them in its schema bump. Pose dict shape from the concept: `{target, yaw, pitch, dist, persp: {lens, sx, sy, loc, tgt?}}` (`sb_onecity.cam`, `derive()` lines 365-378) |
| Rule-1 sweep (NA-03 acceptance 5) | Source: `LAYOUT_RULES["frontage_min_floors"]` = 6 and `hero_sign_rule` (blade, band), `apply_layout_rules` + `dress`; "frontage under 6 floors" is measured on `floors()` of the frontage list |

BPY: none. `sb_onecity` does import `layout36` and `sgraph3` (X2, X5) and writes no Blender data.

### 3.6 `hq/slots.py` (spec 8.1, 8.4, 2.3 `kind: "hq"`)

| Item | Detail |
|---|---|
| Source | `HK/layout.py` c47c67a9 (347 lines, imports `json`, `math`): `class Compound(cfg, watch=None)` with `tier_floor(r)`, `half_size(r)`, `tiers()`, `fp(f, d, u, z)`, `tier_of(i)`, `room_z(i)`, `room_front(i, f=None)`, `room_corners(i)`, `room_center(i)`, `start_pos()`, `crown_top()`, `eye_pos()`, `shortcuts_used(walked)`, `edges(walked)`, `succ(n, walked)`, `reach(froms, walked)`, `states(walked)`, `edge_states(walked, st)`, `branch(o, walked)`, `edge_type(a, b)`, `door(i, side)`, `edge_path(a, b)`, `watch_az(step)`, `room_az(i)`, `in_watch(i, step)`, `scanned(walked)`, `dump(path, walked, extra=None)`; module constants `FACES`, `N`, `T`, `DEFAULTS` (l.36), `SLAB`, `DOOR_Z`, `YF`. `HM/hq_graph.py` 46d161ce (486 lines): Meridian-specific tables (`NODES`, `SEQ`, `KIND`, `LAYER`, `WALLS`) and mover logic (`wall_pt`, `shuttle_at`, `moving`, `mover_order`, `shuttle_pos`, `crane_target`, `edge_path`, `door`, `seg_normal`, `mech`) |
| Gap | The sources are a **fixed mock chain per corp** (`rows`, `path`, `shortcuts`, `kinds`; spec 8.4). No concept function generates slots for an arbitrary graph. Spec 8.4 rule 5 (Designer Q2) requires "slots on demand for whatever graph the game sends". See Open O-E |
| Reads (NA-02) | `run_graph.json` (`nodes`, `layers`, `edges`); `zoned.json` HQ lot (Open O-C); `city.json` `hqs{}` |
| Writes | `derive_<run>.json` with `kind: "hq"`; `street`, `nrm`, `start_left` omitted (NA02 D10); `rooms` (`front`/`back`, `bld`=HQ `bid`, `parts`, `layer`, `kind`), `edges`, `overview`, `decision`, `col_info`/`columns` where applicable |
| Acceptance link | NA-03 acceptance 6: every node of 3 differing graphs placed, 0 overlapping slots, each slot inside its lot |
| BPY | none |

### 3.7 `rig.py` (spec 6.1-6.5, 5.1)

| Source function | Signature (source) | Notes |
|---|---|---|
| `V3D/cam_rig.py` 47850a23 `Pose` | `Pose(F, yaw, pitch, dist, lens, sx=0.0, sy=0.0)` [`F` 3-tuple BU target; yaw, pitch degrees; `dist` BU; `lens` mm; `sx`, `sy` shift in frame widths ~]; methods `dir()`, `loc()`, `proj(P, shift=True)`, `to_json()` -> `{loc, tgt, lens, shift_x, shift_y, yaw, pitch, dist}`, `mix(o, t)` (distance in log space) | `SENSOR` 36 mm in `HK/orbit.py` / `hq_cam.py` |
| `cam_rig.bbox_px / frame_points` | `bbox_px(pose, pts)`; `frame_points(pts, yaw, pitch, lens, fw, fh, bias=0.0)` -> `Pose` | Bisection of `dist` over [5.0, 3000.0], 60 iterations; the HQ variants add `centre=None, dmin=0.0` |
| `cam_rig.decision / hover / overview` | `decision(walked)`; `hover(walked, node, k=1.0)`; `overview(walked)` | Take `walked` (node ids) and use the `sgraph3` mock (X2); port takes `run_graph` and the `derive` rooms |
| `HK/orbit.py` c47c67a9 `Orbit` | `Orbit(compound, cfg=None)`; `decision(walked)`, `hover(walked, node, k=1.0)`, `overview(walked)`, `zoom_of(pose, walked)`, `visible_face(f, pose, margin=None)`, `decision_yaw`, `overview_yaw`, `overview_points`, `look_of_face`, `yaw_of`, `beat(row)` | HQ orbit rig; `ORBIT_DEFAULTS` constant |
| `HM/hq_cam.py` c47c67a9 | `pose_of(js)`, `look_yaw`, `centre_on(p, c)` (front-and-centre shift), `visible_n`, `visible_room`, `stills()` | `stills()` is concept output, not ported |
| `SB/sb_ocjobs.py` c83e3b00 | `smoother(t)`, `hq_cam()`, `pose_at(u, D=None)` (the dive path HQ -> street OVERVIEW), `zoom_of(c, D=None)` (log distance 0..1), `mix(a, b, k)`, `hover_pose(D, room)`, `full_at(f, D=None)` | Not ported from this file: `run`, `oc_block`, `_fr`, `full_jobs`, `frames` (Blender job launcher, `subprocess`, `BLENDER`) |

| NA-02 field | Direction |
|---|---|
| `derive_<run>.json` `rooms`, `col_info`, `overview`, `decision`, `nrm`, `start_left` | reads |
| `poses_<run>.json` (spec 2.1 output: OVERVIEW, DECISION, HOVER, dive path, `zoom`) | writes. **No NA-02 schema** (Open O-F) |

BPY: none. `look_preset` is imported by `sb_ocjobs` (`LP.PRESET["lod_bands"]`); the preset lives in the future `look.preset` module, not NA-03 (Open O-G).

### 3.8 `lod.py` (spec 5.1, 5.2, 5.2b)

| Item | Detail |
|---|---|
| Source | `HK/lod.py` c47c67a9, 48 lines, imports `math` only |
| Public | `sstep(x, a, b) -> float` (smoothstep, `b - a` floored at 1e-6); `zoom(d, d_overview, d_decision) -> float` (clamped `log(d_overview / d) / log(d_overview / d_decision)`; **0 = OVERVIEW, 1 = DECISION** in this file); `band(z, name, bands=None) -> float`; `weights(z, bands=None, floors=None) -> dict[str, float]`; constants `LOD_BANDS` (6 bands: `fog_octaves_by_zoom` (0.25, 0.60), `wisps_on_at` (0.45, 0.70), `plumes_on_at` (0.50, 0.72), `signage_on_at` (0.60, 0.82), `small_lights_on_at` (0.75, 0.92), `puddles_sharp_at` (0.85, 1.00)), `FLOORS` (`signage_on_at` 0.0, `small_lights_on_at` 0.25) |
| Convention clash | `SB/sb_ocjobs.py:zoom_of` defines `zoom_dive` as 0 = the HQ page camera, 1 = the street OVERVIEW (spec 5.1 table). `HK/lod.py` uses 0 = OVERVIEW .. 1 = DECISION. Two different zoom axes: the port keeps both named separately (`zoom_hq`, `zoom_dive`). See Open O-G |
| Reads / writes | `zoom` (float) in, band weights out; part of `poses_<run>.json` (Open O-F). No NA-02 file |
| BPY | none |

### 3.9 `occlusion.py` (spec 7.1-7.4)

| Item | Detail |
|---|---|
| Source | `HK/downtown.py` 46d161ce lines 319-439 (pure; the file also contains `build` and `_street_face` which use `random` and belong to `hq.downtown`, not NA-03) |
| Public | `occlusion_params(cam, pts, cfg=None) -> dict` [`cam` = (x, y, z) BU; `pts` = list of (x, y, z) target front points BU; returns the `occ_*` dict: `occ_on`, `occ_cx/cy/cz`, `occ_ux/uy`, `occ_tsoft`, `occ_a0`, `occ_amax`, `occ_vsoft`, `occ_stub`, `occ_ghost`, `occ_edge`, and `occ_t0..4`, `occ_T0..4`, `occ_v0..4`]; `occlusion_state(p, b) -> (cut_height, opacity)` [`b` = (x, y, top, hx, hy) BU]; `_knot(p, key, a)`, `_sstep(x, w)`; `in_corridor(cfg, x0, y0, x1, y1) -> bool`; `corridor_dist(cfg, x, y) -> float`; `corridor_low(cfg, x, y, h) -> (h, capped: bool)` |
| Constants | Concept: `OCC = dict(margin=0.10, stub=6.4, ghost=0.18, edge=0.6, tsoft=0.035, vsoft=0.025)`, `NK = 5`. **Spec 7.2 wins on units:** `stub` = 3.8 BU (`2 * floor_bu`; the concept's 6.4 is in kit units, C1 rescale), front fade 6.0 BU (the literal `6.0` in `occlusion_state`), `CLUTTER` 6 BU (concept 25), ease 0.35 s. `margin`, `ghost`, `edge`, `tsoft`, `vsoft`, `NK` agree |
| Reads (NA-02) | `derive_<run>.json` (target points from `rooms[].front`), `city.json` footprints (building `(x, y, top, hx, hy)` from `parts`), `zoned.json` corridor segments `cfg["corridor"] = [(ax, ay, bx, by, half)]` and `cfg["corridor_low"]` (Open O-C) |
| Writes | per-frame `occ_*` params and per-building `(cut_height, opacity)` for the parity files (NA-03 acceptance 7) |
| Mixed units | `corridor_low` takes `cfg["corridor_low"] = (dist, hmax, ...)`; `RAIL.side_d` is in lots in `city_preset.py` while the check is in BU (Open O-H) |
| BPY | none (the shader twin is `HK/section.py`, see 3.10) |

### 3.10 `section.py` (spec 5.3, 7.4)

| Item | Detail |
|---|---|
| Source (pure) | `HK/downtown.py` 46d161ce line 277 `section_params(pose_loc, cfg, rooms_pts=None, zref=None, margin=1.5) -> dict` (`sec_on`, `sec_ox/oy`, `sec_ux/uy`, `sec_s0`, `sec_w0`, `sec_slope`, `sec_zref`, `sec_widen` 0.45, `sec_plinth` 0.6); `SB/sb_ocjobs.py` c83e3b00 `zcut(z)` (log-interpolated cut height from `PRESET["lod_bands"]["section_by_zoom"]` = (zf, zn, a, b); returns 1.0e4 when u = 0) and `look_w(z)` (smoothstep over `look_blend_by_zoom`); `HK/section.py` 46d161ce constants `NK` (5), `KEYS` (the `occ_*` scene keys), `POCHE` (0.010, 0.010, 0.013), `EDGE_COL` (0.55, 0.68, 0.85), `CLUTTER` (25.0 kit units; spec 7.2: 6 BU), and `set_frame(scene, params)` (a pure dict fill over `KEYS`) |
| **BPY, split out** | `HK/section.py:insert(mat)` (`import bpy`, edits material node trees) and `M44/onecity_build.py:section(mat)` / `section_all(skip=())` (node-tree insertion, module-level bmesh code) are **NA-05**, not NA-03. NA-03 ports only `section_params`, `zcut`, `look_w` and the constants |
| Reads / writes | `zoom` float and a pose location in; `sec_*` dict out; `poses_<run>.json` (Open O-F). No NA-02 file |

### 3.11 `states.py` (spec 8.1 `states`)

| Item | Detail |
|---|---|
| Source | `route_map_graph/hq_orbital/scripts/hq_kit/states.py` c47c67a9, 83 lines (imports `PIL`, `numpy`) |
| Pure part | constants `LIME`, `ORANGE`, `WHITE`, `GREY`, `RED`, `GOLD`, `STATE_COL`, `STATE_K`, `LOCKDOWN_K`, `LOCKDOWN_RGB`; `ring_colour(state, in_eye)`; `rule_word(consequence)` |
| Image part (PIL, split out) | `scan_lines(img, poly, k=1.0, phase=0.0, size=None)` and `eye_badge(px, crest_mask=None)` draw into a PIL image: look-dev overlays (spec 2.1 `overlay`), not a data contract. Keep out of the "no PIL" core or place behind a guarded import (Open O-A) |
| NA-02 | `run_graph` node state is not in NA-02 (walked state lives in `RunState`; NA02 D4). The state language (`state` argument) is the concept's `walked/available/...` set; the values are in `STATE_COL` |
| BPY | none |

### 3.12 `dress.py` (spec 9, 4.1, 13.1)

| Item | Detail |
|---|---|
| Source | `M44/onecity_build.py` c83e3b00 lines 98-126 (hero blade signs: one per route column, `_PAL2 = [(1.0,0.16,0.6),(0.16,0.8,1.0)]`, `random.Random(9970 + k)`); `M44/onecity_cycles.py` c83e3b00 lines 169-371 (kerb lamps every `lamp_step` 6.0 BU at +-2.6 BU, y 1.6; ground glows on a `ground_glow_step` 9.0 BU grid, `ground_glow_depth` 60.0, `ground_glow_p` 0.55, `random.Random(7719)`; wash spots 3.5 BU across the street; `H_FRONT`/`H_SKY`; beams: K=6 tallest roofs that clear `beam_rise` 1.35 x `H_FRONT`, 25 < d < 170, > 12 BU behind, not a route column, spacing > 45 BU, sort `(-top, key)`, colours a/b/warm/b/a/cool) and lines 612-648 (streak lanes, `LANES`, `set_lanes`, `random` seed 9402) |
| **BPY, split out** | Placement and creation are interleaved: `_light(name, kind, loc, rot, energy, col, size=None, spot=None, blend=0.3)`, `_beam_mat`, `_beam_shaft`, `_surf_mat`, `_emit_mat`, `_wet_mat`, `RBN.face(...)`, `beam(...)` are `bpy`/`bmesh`/`mathutils` calls. Port the **placement computations** into functions returning lists of dicts (position BU, direction, colour, power, stream key) and leave `_light`, mesh, material, node-tree and `dyn_mode` code to NA-05. Replace every `random.Random(<literal>)` with `splitmix64(art_seed(...))` using streams `hero_sign` (key `k`), `ground_glow`, `street_lanes`, `beams` (key `bid`) |
| Public signatures | **none in the source** (module-level script code, not functions). New: `dress_street(derive: dict, zoned: dict, preset: dict, art_seeds: dict) -> dict` returning placement lists (spec 2.2: "signage, beams, lamps, washes, fog fields, streak lanes, glows as placement lists"). Exact list schemas are not in NA-02 (Open O-I) |
| Reads (NA-02) | `derive_<run>.json` (`rooms`, `col_info`, `route_keys` as `bid`, `nrm`, `street`, `art_seeds`), `city.json` (building tops for `H_FRONT`/`H_SKY`), `zoned.json` |
| Writes | placement lists (no NA-02 schema); `art_seeds` consumed, never written |

## 4. Open (what the sources do not give)

| # | Missing | Needed by |
|---|---|---|
| O-A | Allowed dependencies for `tools/netrun_art/` (numpy, PIL?). `zoning`, `states` and the NA-04 image checks import them; the brief says only "no `bpy`" | zoning, states, NA-04 |
| O-B | `io.py` has no concept source and no signature anywhere. Names for dump, load and validate are free for NA-03 to choose, but must be listed in the schema bump | io |
| O-C | `zoned.json` and `city_base.json` have no NA-02 schema; corridor and rail polyline shapes (`cfg["corridor"]`, `cfg["corridor_low"]`) come from `city_preset.RAIL` and `zoning.py` only | zoning, occlusion, hq.slots |
| O-D | The concept rule selects border links by `state == "border"`; `net.json` states are `open/locked/opened`. Which links are "border links" for `apply_layout_rules` is undefined | layout |
| O-E | No concept generator of HQ slots for an arbitrary GDD 4.2 graph (spec 8.4 rule 5 requires one). Brief acceptance 6 (3 graphs, no overlap, inside lot) has no reference implementation | hq.slots |
| O-F | `poses_<run>.json` (rig output) and the lod/section parameter files have no NA-02 schema | rig, lod, section |
| O-G | Zoom convention: `HK/lod.py` (0 = OVERVIEW, 1 = DECISION) vs `sb_ocjobs.zoom_of` (`zoom_dive`, 0 = HQ page, 1 = street OVERVIEW). `lod_bands` live in `look_preset.PRESET`, i.e. the `look.preset` module, which is not in NA-03's list | lod, section, rig |
| O-H | Unit of `RAIL.side_d` (1.2) and `corridor_low` distance: lots in the preset, BU in the checks | occlusion, NA-04 12.4 |
| O-I | Schemas of the `dress` placement lists (lamps, washes, glows, beams, streak lanes, signs) | dress |
| O-J | Nested derive shapes beyond the concept's (NA02 Ruling O10 leaves them to NA-03). This document lists the concept shapes only (3.5); freezing them is NA-03's schema bump | derive.street |
| O-K | Kit-unit constants in the HQ sources (`OCC.stub` 6.4, `CLUTTER` 25, `section_params` bands `+ 30.0` / `+ 24.0`, `margin=1.5`) are not all rescaled in the spec: 7.2 gives `stub` and `CLUTTER` only. The `section_params` literals have no spec value | occlusion, section |
