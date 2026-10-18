# Derive v2 schema proposal (nested shapes, poses, lod / section params, dress lists)

Date 2026-10-18. Round W0 NA-03a. **A review document for the art-pass session. Nothing here is coded against yet.**
Per `NA03_NA04_ANSWERS.md` "Two build-session calls (b)": art-pass reviews this BEFORE any module codes against it, then
it freezes as derive v2. NA-03 ports `dress` last because its lists are not designed.

Sources, in order of authority: `NA03_NA04_ANSWERS.md` (wins), `docs/handoff/plan2/NA02_FIELDS.md` (sections 1, 6, 7 and
Rulings O4, O10), `NA03_MODULES.md` section 3.5, 3.7 to 3.12, `PIPELINE_SPEC.md` 5.1, 6.1 to 6.4, 7.2.
Conventions are NA02 section 1: canonical JSON (indent 1, sorted keys, floats 1e-4, u64 as decimal strings), BU plan
coordinates (x east, y north), heights BU above local ground, ids are strings, sort ties by id (`bid`, then node id).

Status words in the **Open** column: `ok` = read straight from sources, no question; `Q` = a question for art-pass.
Rows marked **not designed yet** are placeholders only: do not review their field names, only the open questions.

## 0. What changes from v1

| Item | v1 (NA02 section 6) | v2 (this doc) |
|---|---|---|
| `version` | `1` | `2` (int). A v1 file stays valid for the game keys; the reader must reject unknown versions |
| Nested shapes | top-level keys only (Ruling O10) | frozen below (section 1) |
| Poses | not in the file | separate `poses_<run>.json` (section 2) |
| LOD / section | not in the file | `lod` and `section` blocks in `poses_<run>.json` (section 3) |
| Dress | not in the file | separate `dress_<run>.json`, **not designed yet** (section 4) |
| Zoom names | n/a | `zoom_dive` and `zoom_detail` only; never an unqualified `zoom` (O-G) |

Q0.1: one bump for all three files, or does `poses_` / `dress_` carry its own `version` starting at 1? Proposal: each
file has its own `version` int; `derive_<run>.json` goes to 2, the two new files start at 1. (Needs art-pass: the Blender
scene, the checks and the Godot runtime all read these.)

## 1. `derive_<run>.json` v2: nested shapes

Top-level keys are unchanged from NA02 section 6. Only the nested element shapes below are new. `bid` replaces the
concept `key` everywhere (C2); `ts` becomes `taper`.

### 1.1 Primitive shapes

| Name | JSON | Unit | Source | Open |
|---|---|---|---|---|
| `xy` | `[x, y]` floats | BU plan | `sb_onecity` leg ends, `nrm` | ok |
| `xyz` | `[x, y, z]` floats | BU world; z = height above ground | `room_boxes` 3-tuples | ok |
| `quad` | 4 x `xyz`, in the concept corner order | BU world | `room_boxes.front` / `back` | Q1.1 state the corner order (the concept does not document it) |
| `path` | list of `xyz` (4 points for a facade link) | BU world | `link_paths` | ok |

### 1.2 `rooms{}` (value of each node id key)

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `front` | `quad` | BU world | `sb_onecity.room_boxes` | Q1.1 |
| `back` | `quad` | BU world | `room_boxes` | ok |
| `floor` | int | floor index | `room_boxes` | Q1.2 0-based from `base_floor` 0? |
| `span` | int | floors, 1 or 2 | `room_boxes`; equals top-level `span` | ok |
| `bld` | string | `bid` | `room_boxes` (was `key`) | ok |
| `parts` | array of string | `bid` list | `room_boxes` | Q1.3 the concept lists building parts; in NA02 a building has `parts[]` polygons, so is this a list of `bid` (one building) or of part indices? Proposal: part indices (int) into `buildings[bld].parts` |
| `layer` | int | 1-based, as `run_graph.nodes[].layer` | `room_boxes` | ok |
| `kind` | string | none | node `type` of `run_graph.json`: `router`, `terminal`, `mainframe`, `server_rack` (NA02 D9, O13) | ok |

Keys of `rooms` are node ids (`L<layer>N<index>`); emitted in sorted order by the canonical writer.

### 1.3 `edges[]`

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `a`, `b` | string | node id | `link_paths` | ok |
| `type` | string | none | `"facade"` (the only value in the concept) | Q1.4 any other link type planned? |
| `path` | `path` | BU world | `link_paths`: Manhattan polyline 0.5 BU in front of the faces | ok |

Sorted by `(a, b)`.

### 1.4 `col_info[]`, `columns[]`, `frontage[]`

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `col_info[].layer` | int | 1-based | `derive` | ok |
| `col_info[].bid` | string | `bid` | `derive` (was `key`) | ok |
| `col_info[].top` | float | BU | `derive` | ok |
| `col_info[].u0`, `u1` | float | BU along the street from `street.a` | `derive` | Q1.5 the origin of `u` is `street.a`? Not stated in the concept |
| `col_info[].face` | `quad` or `[xy, xy]` | BU | `derive` | Q1.6 the concept shape is not recorded in NA03_MODULES; art-pass to state which |
| `columns[]` | `[layer int, bid string]` | | `derive` | ok (NA02 s6) |
| `frontage[]` | `[bid, h, floors, taper]` = `[string, float BU, int, float 0..1]` | | `derive` | ok (NA02 s6) |

### 1.5 Pose object (`overview`, `decision`; also used by section 2)

Concept shape `{target, yaw, pitch, dist, persp: {lens, sx, sy, loc, tgt?}}` (`sb_onecity.cam`, `derive()` 365-378),
reconciled with `V3D/cam_rig.py Pose.to_json()` `{loc, tgt, lens, shift_x, shift_y, yaw, pitch, dist}`. Proposal: one flat
shape, the `Pose.to_json()` one, because the Blender and Godot cameras read `loc`, `tgt`, `lens`, `shift_*` directly.

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `loc` | `xyz` | BU world | `Pose.loc()` | ok |
| `tgt` | `xyz` | BU world | the framed target `F` | ok |
| `yaw` | float | degrees | `Pose` | Q1.7 sign and zero (the spec 6.2 rule 1: `yaw0 = atan2(nrm)`); state the compass convention once |
| `pitch` | float | degrees | `Pose` | ok |
| `dist` | float | BU, camera to target | `Pose` | ok |
| `lens` | float | mm; sensor `SENSOR` 36 mm | `Pose` | ok |
| `shift_x`, `shift_y` | float | frame widths | `Pose.sx`, `sy` | Q1.8 "frame widths" for both axes, as in Blender `shift_x/y`? Confirm |

The concept `persp` sub-object is dropped (its contents are the flat fields above). Open Q1.9: does any consumer need
`persp`? Proposal: no.

## 2. `poses_<run>.json` v1 (new; NA03_MODULES Open O-F)

Written by `rig`. Reads `derive_<run>.json` `rooms`, `col_info`, `overview`, `decision`, `nrm`, `start_left`.

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `version` | int | none | constant `1` | Q0.1 |
| `run` | string | none | copy of derive `run` | ok |
| `layout_seed` | string | decimal u64 | copy | ok |
| `kind` | string | none | `"street"` or `"hq"` | ok |
| `overview` | pose (1.5) | | `rig.overview` | ok |
| `decision` | object: node id -> pose | | `rig.decision(walked)` for every node as current | Q2.1 one pose per node (the concept takes `walked`, a node-id list); poses for every node as "current" with walked = path to it assumes one canonical walk. Which walked set? |
| `hover` | object: node id -> pose | | `rig.hover(walked, node, k=1.0)` | Q2.1 same walked question; `k` stored? Proposal: store at `k` 1.0 and let the runtime scale |
| `dive` | `{d0, d1, samples[]}` | BU | `sb_ocjobs.pose_at(u)` (spec 6.3) | Q2.2 sample the dive path at fixed `u` (proposal: 0, 0.05, .. 1.0, 21 samples) or store the end poses and let the runtime interpolate by spec 6.3? Proposal: end poses plus `dive.hq_pose` and `dive.overview_pose` and the constants; the interpolation rule is in the spec |
| `dive.hq_pose`, `dive.overview_pose` | pose (1.5) | | `sb_ocjobs.hq_cam()`, `overview` | the HQ start is orthographic emulated by `HQ_LENS` 300 mm: record `lens` 300 |
| `dive.duration_s` | float | seconds | `DIVE_S` 3.0 (spec 6.3, Designer Q7) | ok |
| `rig` | object of constants | see below | `cam_rig` | Q2.3 see below |
| `zoom` | `{d0, d1, d_ov, d_dec}` | BU | O-G | see Q2.4 |

`rig` constants (copied from the spec table so a reader needs no other file): `hover_pull` 0.22, `hover_yaw` 3 (deg),
`hover_dolly` 0.96, `ov_yaw_k` 0.3, `pitch_o` 6 (deg), `lens_o` 40 (mm), `fill_ow` 0.95, `fill_oh` 0.90, `t_step` 0.9,
`t_hover_in` 0.30, `t_hover_out` 0.35, `t_zoom` 1.0 (all seconds where `t_`). Q2.3: stored in the file, or only in a
module (`# placeholder`)? Proposal: stored, so the Godot rig reads one source.

Q2.4: `zoom_dive` and `zoom_detail` are **functions of camera distance**, not stored values per pose (O-G stores them
"as two floats"). Proposal: store `zoom.d0`, `d1`, `d_ov`, `d_dec` (BU) and, per pose, the two floats `zoom_dive` and
`zoom_detail` computed from `dist` (so a reader can check). `d_dec` has no concept value and must come from the HQ
DECISION pose (O-G): for `kind: "street"` the file has `d_dec: null` until art-pass gives the rule. Q2.5: what is
`d_dec` for the street kind?

## 3. LOD and section parameters (inside `poses_<run>.json`)

### 3.1 `lod` block

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `lod.bands` | object: band name -> `[d_near, d_far]` | BU camera distance | `lod.DEFAULT_BANDS` = spec 5.2 distance table (`d(z) = d0 * (d1/d0)^z`, d0 3833, d1 114.6) | Q3.1 the distance table is "normative" but only three of its values are quoted in the answers (e.g. `fog_octaves` 0.25 -> 1593); NA-03 needs the whole 6-band table as numbers. Which direction is `[near, far]` (weight 0 at far, 1 at near)? |
| `lod.floors` | object: band name -> float | weight | `lod.FLOORS` `signage_on_at` 0.0, `small_lights_on_at` 0.25 | ok |
| `lod.weights` | object: pose name -> object band name -> float 0..1 | none | `lod.weights(d_bu)` at each stored pose's `dist` | Q3.2 which poses get weights stored (OVERVIEW, DECISION, dive samples)? Weights are derivable from `dist`, so is storing them parity data only? Proposal: yes, parity data for NA-21 |

Band names (6): `fog_octaves_by_zoom`, `wisps_on_at`, `plumes_on_at`, `signage_on_at`, `small_lights_on_at`,
`puddles_sharp_at`. Q3.3: the `_by_zoom` / `_on_at` suffixes mention zoom, but the bands are by distance now. Rename to
`fog_octaves`, `wisps`, `plumes`, `signage`, `small_lights`, `puddles_sharp`? Proposal: yes rename in v2.

### 3.2 `section` block

Pure part of `HK/downtown.py section_params` and `sb_ocjobs.zcut / look_w`. Constants converted to one-city BU per
`NA03_NA04_ANSWERS.md` O-K.

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `section.params` | object `sec_*` | see below | `section_params(pose_loc, cfg, rooms_pts, zref, margin)` | Q3.4 |
| `section.params.sec_on` | bool (0/1 in the shader) | none | | Q3.5 bool or 0/1 int in JSON? Proposal: bool |
| `sec_ox`, `sec_oy` | float | BU plan | cone origin | ok |
| `sec_ux`, `sec_uy` | float | unit vector | axis | ok |
| `sec_s0`, `sec_w0`, `sec_slope` | float | BU, BU, none | band start, width, widening slope | Q3.6 the concept keys have no unit notes; confirm BU, BU, unitless |
| `sec_zref` | float | BU height | `zref - zref_margin` | ok |
| `sec_widen` | float | none | 0.45 | ok |
| `sec_plinth` | float | BU | 0.6 | Q3.7 0.6 is the concept value; is it already one-city BU? Not in the O-K table |
| `section.consts` | object | BU | O-K | |
| `consts.band_overview` | float | BU | 30.0 kit x 0.2375 = **7.125** | `k_fit` caveat of O-K: apply `k_fit` if the HQ scene is scaled uniformly (Q3.8) |
| `consts.band_rooms` | float | BU | 24.0 kit = **5.70** | same |
| `consts.zref_margin` | float | BU | 1.5 kit = **0.356** | name per O-K; same caveat |
| `consts.clutter` | float | BU | **6** (spec 7.2; 25 kit = 5.94) | ok, one constant |
| `consts.stub` | float | BU | **3.8** (ruling C1, `2 * floor_bu`) | ok |
| `consts.front_fade` | float | BU | **1.425** (6.0 kit; O-K AD call, provisional) | confirm |
| `consts.edge_band` | float | BU | **0.095** (0.4 kit) | confirm |
| `consts.ground_tol` | float | BU | **0.038** (0.16 kit) | confirm |
| `consts.cone_margin` | float | none | 0.10 (was `OCC.margin`) | ok |
| `consts.ghost`, `edge`, `tsoft`, `vsoft` | float | none | 0.18, 0.6, 0.035, 0.025 | ok |
| `consts.nk` | int | count | 5 | ok |
| `section.zcut` | `{zf, zn, a, b}` | see `look.preset` | `PRESET["lod_bands"]["section_by_zoom"]` | Q3.9 lives in the future `look.preset`; the values and their zoom axis (`zoom_dive`) must be given. 1.0e4 is the "no cut" value at u = 0: keep it? |
| `section.look_blend` | `[z0, z1]` | `zoom_dive` | `look_w` smoothstep range | Q3.9 same |

### 3.3 `occlusion` block (per frame, for parity and the checks)

| Field | Type | Unit | Source | Open |
|---|---|---|---|---|
| `occlusion.params` | object `occ_*` | | `occlusion_params(cam, pts, cfg)` | |
| `occ_on` | bool | | | Q3.5 |
| `occ_cx`, `occ_cy`, `occ_cz` | float | BU world | camera | ok |
| `occ_ux`, `occ_uy` | float | unit vector | | ok |
| `occ_tsoft`, `occ_vsoft`, `occ_a0`, `occ_amax`, `occ_stub`, `occ_ghost`, `occ_edge` | float | none, except `occ_stub` BU | | ok |
| `occ_t0..4`, `occ_T0..4`, `occ_v0..4` | float | none (cone knots, NK = 5) | | Q3.10 as three arrays of 5, or the 15 flat keys? Proposal: three arrays `occ_t`, `occ_T`, `occ_v` (the shader twin reads `KEYS`; art-pass says which) |
| `occlusion.buildings[]` | `{bid, cut_height, opacity}` | BU, 0..1 | `occlusion_state(p, b)` | parity data, NA-03 acceptance 7 |

The rail clearing uses `zoned.json` `rail.side_d` 7.2 BU and `rail.side_cap` (O-H), not the HQ-kit `corridor_low`
tuple (retired from the pipeline). Q3.11: confirm `occlusion.py` takes the rail from `zoned.json` only.

## 4. Dress lists (`dress_<run>.json`): **not designed yet**

Nothing below is a proposal. It lists only what the sources say the lists contain, so art-pass can design the shapes.
Spec 2.2 says only: "signage, beams, lamps, washes, fog fields, streak lanes, glows as placement lists".

| List | Concept source (`M44/onecity_build.py`, `onecity_cycles.py` c83e3b00) | Contents per item | Seed stream (NA02 section 7) | Shape |
|---|---|---|---|---|
| `signs` | hero blade signs, one per route column | position BU, orientation, size, palette index (`_PAL2` 2 colours), panel count | `hero_sign` key column index `k` | **not designed yet** |
| `lamps` | kerb lamps every `lamp_step` 6.0 BU at +-2.6 BU, y 1.6 | position BU, side | none (regular) | **not designed yet** |
| `washes` | wash spots 3.5 BU across the street | position BU, direction, power | none | **not designed yet** |
| `glows` | ground glows on a 9.0 BU grid, depth 60.0, p 0.55 | position BU, colour, power | `ground_glow` | **not designed yet** |
| `beams` | K = 6 tallest roofs clearing `beam_rise` 1.35 x `H_FRONT`, 25 < d < 170, spacing > 45, sort `(-top, bid)`, colours a/b/warm/b/a/cool | `bid`, position BU, lean, sweep, colour | `beams` key `bid` | **not designed yet** |
| `streak_lanes` | streak lanes `LANES` | lane geometry, speed, colour | `street_lanes` | **not designed yet** |
| `fog_fields` | fog fields | volume box BU, density | none | **not designed yet** |

Open for the whole section (Q4.1 to Q4.4):
- Q4.1: units for power (watts as Blender, or relative)? NA-03 places, NA-05 creates the lights.
- Q4.2: colour as RGB floats or palette ids? The palette lives in `look.preset` (not yet a module).
- Q4.3: does the Godot runtime read the dress lists at all, or only Blender? It decides whether they need a Godot twin.
- Q4.4: Python `random` was used in the concept (seeds 9970 + k, 7719, 9402); all become `splitmix64(art_seed(...))`
  (X4), so the draw order inside a stream must be fixed in the design (per-object streams keyed by id, spec 3.5 rule 3).

## 5. Summary of questions for art-pass

Blocking before coding: Q0.1 (version scheme), Q1.1, Q1.3, Q1.6 (corner order, `parts`, `face`), Q2.1 (walked set for
per-node poses), Q2.4 and Q2.5 (`d_dec` for street), Q3.1 (band table numbers), Q3.9 (`look.preset` values), all of
section 4. The rest have a stated proposal and can proceed on it unless art-pass objects.
