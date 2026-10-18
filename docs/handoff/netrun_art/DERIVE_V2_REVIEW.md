# Derive v2 schema: art-pass review

Date 2026-10-18. Reviews `D:/Godot/rebel_cell/docs/handoff/netrun_art/DERIVE_V2_SCHEMA.md` (read only). One heading per question ID,
short answer first. Facts cite `file:line` at commit `6a58733c`; path abbreviations are `PIPELINE_SPEC.md` section 0
(`SB/` = `route_map_graph/storyboard/scripts/`, `M44/` = `SB/m44/`, `V3D/`, `HK/`; `HK/` copies are byte-identical, line numbers below are
`hq_rebel_cell`). `sb_onecity.py` = `SB/sb_onecity.py`, `onecity_cycles.py` = `M44/onecity_cycles.py`.
"AD 2026-10-18" marks an art-director ruling given with the review request. "Recommendation" marks my call where no ruling was given; the
build session may push back on those.

## Findings that change the proposal (read first)

1. **Two yaw conventions exist** (Q1.7). Derive poses use the layout36 yaw; the camera rig and spec 6.1 use another. They differ by `yaw_rig = 90 - yaw_layout36`.
2. **`col_info.u0/u1` are absolute world x or y, not "from `street.a`"** (Q1.5), and **`face` is a single float** (Q1.6).
3. **`zoom_dive` uses the distance to the OVERVIEW target, not the pose's own `dist`** (Q2.4), and `d0`, `d1` are per run while the band table anchors are constants (Q3.1).
4. **The rig constants list is incomplete and has one wrong value for the street**: `pitch_o` is 2.0 in the one-city derive, not 6 (Q2.3).
5. **The DECISION look-bias sign differs between the derive and the rig** (Q2.1).
6. **`section.params` and `occlusion.params` are per pose, not per run** (Q3.4).
7. **Dress lists: the concept has facts the Part B shapes lose** (beam lean is 2-axis, a streak lane is many streaks, a hero sign has a band, lamps alternate colour). Details in Q4.

## Facts at a glance (Part A)

| ID | Answer |
|---|---|
| Q1.1 | Both quads: bottom at the lower axis coordinate, bottom at the higher, top at the higher, top at the lower. "Left to right" from the street depends on `nrm`; see Q1.1. |
| Q1.2 | `floor` is 0-based from the ground floor (`base_floor` 0); the room's lowest floor index. |
| Q1.3 | `parts` is the list of building keys of the base and the stacked parts above it, base first. Map to sorted int indices into `buildings[bld].parts`. |
| Q1.5 | `u` is the absolute world x (street along x) or y (street along y), not an offset. |
| Q1.6 | `face` is one float: the world coordinate of the street-facing wall on the cross axis. |
| Q1.7 | Derive: 0 = +x, counter-clockwise positive. Rig and spec 6.1: 0 = +y, clockwise positive. Pick the rig one for v2 files. |
| Q1.8 | Both shifts are fractions of frame WIDTH (the 36 mm sensor, horizontal fit). `shift_y` too (Blender convention). |
| Q3.1 | Table in Q3.1. Weight 1 at the near end (`d1` 114.6), 0 at the far end (`d0` 3833). |
| Q3.6 | `sec_s0`, `sec_w0` are BU of the scene they are computed in; `sec_slope` is unitless (rise over run). |
| Q3.7 | `sec_plinth` 0.6 is a kit-unit literal, not converted; one-city value 0.1425. Nothing in the concept reads it. |
| Q3.9 | `section_by_zoom` = (zf 60, zn 0.4, a 0.25, b 0.85), `look_blend_by_zoom` = (0.20, 0.55), both on the `zoom_dive` axis. |
| Q3.10 | The shader twin reads 28 flat keys (`KEYS`, `section.py:31-32`); the three arrays unpack to `occ_t0..4`, `occ_T0..4`, `occ_v0..4`. |

---

## Q0.1 Version scheme

**AD 2026-10-18: each file has its own `version` int. `derive_<run>.json` goes to 2; `poses_<run>.json` and `dress_<run>.json` start at 1.**
A reader rejects any version it does not know (no best-effort read). Nothing in the code contradicts this.

## Q1.1 Corner order of `front` / `back`

**Both quads list: bottom at the lower axis coordinate, bottom at the higher, top at the higher, top at the lower.**
`sb_onecity.py:271-272` (street along x): `[(u0,face,z0), (u1,face,z0), (u1,face,z1), (u0,face,z1)]` for `front`, the same with `back` for `back`.
`:274-275` (street along y): the same with `(face,u,z)` and `(back,u,z)`. `u0 < u1` is world x (axis 0) or world y (axis 1) (`:260-263`); `back` is `face + room_depth * nrm`, so it lies inside the
building; `z0 = floor*1.9 + 0.12`, `z1 = (floor + span)*1.9 - 0.12` (`:266-267`).

Seen from the street the order is NOT a fixed "bottom-left first". The camera looks along `nrm` (`choose_street`, `sb_onecity.py:243-246`, `right = (nrm.y, -nrm.x)`).
`u` increases to the screen right only when `nrm` is `(0, +1)` or `(-1, 0)`. For `(0, -1)` and `(+1, 0)` the same order reads bottom-right, bottom-left, top-left, top-right. All four cases occur (`side` and the leg both vary).

**Recommendation:** the v2 writer normalises to "bottom-left, bottom-right, top-right, top-left seen from the street (the viewer looks along `nrm`)", by reversing the `u` order when `u` runs right-to-left. Then no consumer needs a case analysis for winding or texture u.
Nothing in the concept indexes `front[0..3]` by horizontal position (`derive()` uses only the z of `[0]` and `[3]`, `link_paths` uses min/max), so the change is safe. The Python reference and the GDScript twin must both do the normalisation.

## Q1.2 `floor`

**0-based from the ground floor.** `floor = RULES["base_floor"] + k * span_l` (`sb_onecity.py:265`), `base_floor = 0` (`:36`), `k` = the node's index within its layer, ordered by `G.K` (`layers()`, `:207-208`, sorted by `G.K`).
For a two-floor room the field is the lowest floor; the room covers floors `floor .. floor+span-1`. The `0.12` BU inset above and below is a literal (`:266-267`): it should become a named rule in the writer (CLAUDE.md rule 5).

## Q1.3 `parts`

**A list of the building keys of the street-level base plus every stacked part above it (z0 > 0.05) whose footprint centre lies in the base footprint, base key first.**
`merged_buildings()` sets `b["parts"] = [b["key"]]` (`sb_onecity.py:151`) and appends `u["key"]` for each stacked part (`:157`); `room_boxes` copies `b.get("parts", [b["key"]])` (`:276`).
It is not a list of "part polygons".

**Recommendation (as requested): store int indices into `buildings[bld].parts`, sorted ascending.** Index 0 is the base part. The writer maps each concept key through `bid` to the index in `buildings[bld].parts`; the top-level `route_keys` (`bid` list) is the union and stays. Rooms of one column that share a base get the same list.

## Q1.4 Link types

**AD 2026-10-18: only `"facade"` in v2. Reserve `"hq"` (links drawn on an HQ landmark surface, placed from `hq.slots`). A reader must reject unknown types.**
Code agrees: `link_paths` emits only `type="facade"` (`sb_onecity.py:304`); the path has 4 points (`:304`), 0.5 BU in front of the faces (`:291`).

## Q1.5 Origin of `u`

**Absolute world coordinate along the street axis: x when the street runs along x, y when along y. It is not measured from `street.a`.**
`col_info`: `u0 = b["x0"] if axis == 0 else b["y0"]`, `u1 = b["x1"] if axis == 0 else b["y1"]` (`sb_onecity.py:390-391`), the building's bounding extent.
The proposal's "BU along the street from `street.a`" is wrong for the concept.

**Recommendation:** use ONE definition of `u` in all v2 files, because `lamps[]` and `washes[]` also carry `u`. Define `u` = signed distance in BU along the unit vector `a -> c` from `street.a` (0 at `a`, increasing toward `c`), and write `col_info.u0 < u1` in that frame (swap if the street runs toward -x or -y).
The conversion is `u = (p - a) . dir`. This departs from the concept's raw coordinate; the Python reference must apply it once, in the writer. If the build session prefers the raw concept value, then the dress `u` must be renamed (e.g. `s`) so the two are never confused.

## Q1.6 Shape of `col_info[].face`

**One float: the world coordinate of the street-facing wall plane on the cross axis (y when the street runs along x, x when along y).**
`face=b["face"]` (`sb_onecity.py:391`), set from `near = b["y0"] if nrm[1] > 0 else b["y1"]` (axis 0) or `b["x0"]/b["x1"]` (axis 1) (`:194-198`, `:202`).
It is not a quad and not a pair. The axis is implied by `nrm` (`|nrm.y| == 1` means the street runs along x). v2: `face` is a float, unit BU world; no `axis` field is needed, but the spec should state the rule.

## Q1.7 Yaw convention

**There are two conventions. Choose the rig one (spec 6.1) for every stored `yaw`.**

- Derive poses (`sb_onecity.cam`, `:313-317`, via `layout36.basis`, `M44/layout36.py:52-57`): `fwd = (cos yaw cos pitch, sin yaw cos pitch, -sin pitch)`. Zero = +x (east); positive = counter-clockwise seen from above (toward +y). `street_yaw = atan2(nrm.y, nrm.x)` (`:349-352`). The HQ dive start is `yaw=135` in this convention (`SB/sb_ocjobs.py:67`).
- Rig (`V3D/cam_rig.py:3-4, 84-86`) and spec 6.1.1: `dir = (sin yaw cos pitch, cos yaw cos pitch, -sin pitch)`. Zero = +y (north); positive = clockwise seen from above (toward +x). "yaw > 0 looks right".
- Conversion: `yaw_rig = 90 - yaw_layout36`, so `yaw0_rig = atan2(nrm.x, nrm.y)`. Pitch is the same in both (positive looks down). No roll.

**The statement for the spec (once):** "yaw is in degrees, 0 looks along +y (north), positive turns clockwise seen from above toward +x (east); pitch is positive looking down; `dir = (sin yaw cos pitch, cos yaw cos pitch, -sin pitch)`; the camera is at `tgt - dist * dir`."
Spec 6.2 "One-city overrides" mixes the two: rule 1 `yaw0 = atan2(nrm)` and rule 3/4 `yaw0 - sgn * 7.2` / `- sgn * 24` are layout36. In the rig convention they become `yaw0_rig + sgn * 7.2` and `yaw0_rig + sgn * 24` (`sgn` +1 when the start is on the screen left; derive code `sb_onecity.py:363, 367, 377`). The writer converts once; `loc` and `tgt` are convention-free, so a consumer that only places cameras from `loc`/`tgt`/`lens`/`shift` is unaffected. The rig, which interpolates yaw, is not.
The dive start pose (yaw 135 layout36) is yaw -45 in the rig convention, and `pose_at` unwraps the shortest arc (`SB/sb_ocjobs.py:79-83`): the runtime must keep that unwrap after the conversion.

## Q1.8 Units of `shift_x` / `shift_y`

**Both are fractions of the frame WIDTH (the 36 mm sensor, horizontal fit), including `shift_y`.** This is also what Blender's `shift_x/y` means for a landscape frame with sensor fit AUTO or HORIZONTAL (the shift is a fraction of the larger sensor dimension, which is the width here).
`V3D/cam_rig.py:101-102`: `x_px = W/2 + (nx - sx)*W`, `y_px = H/2 - (ny - sy)*W`; the solver sets `sx = (cx_px - ucx)/W`, `sy = (ucy - cy_px)/W` (`:141-142`); the derive does the same (`sb_onecity.py:344-345`, `sy = -(cy - ucy)/W_`).
Sign: positive `shift_x` moves the projected content to screen left, positive `shift_y` moves it down, which is the Blender lens-shift sign. `SENSOR` = 36 mm (`cam_rig.py:25`); reference frame 1920 x 1080.
Caveat for Godot: the `frustum_offset` and `size` of `Camera3D.PROJECTION_FRUSTUM` must be derived from these width-fractions with the near-plane width. I did not verify the engine's unit here; the parity test is "project the 8 room corners with the stored pose in Python and in Godot and compare pixels".

## Q1.9 `persp`

**AD 2026-10-18: drop `persp`.** The code agrees: its contents (`loc`, `lens`, `sx`, `sy`, `tgt`) are the flat fields (`sb_onecity.py:316-317`, `SB/sb_ocjobs.py:90`). The concept `cam()` also carries `ortho = dist*36/lens`; derive it, do not store it. The concept names `target` and `sx/sy`; v2 uses `tgt`, `shift_x`, `shift_y`.
Consumers to update: `SB/sb_ocjobs.py:76, 88-90` and `sb_onecity.proj` read `persp`.

## Q2.1 Per-node DECISION / HOVER poses

**AD 2026-10-18: do NOT precompute per-node decision/hover poses. The walked set is dynamic in play, so `NetrunCameraRig` computes DECISION and HOVER at runtime from the real walked list. `poses_<run>.json` stores `overview`, the dive end poses, the rig constants, the zoom block and a `fixtures[]` list of `{walked[], current, hover?, decision pose, hover pose}` for parity: at least 3 walks per run (the first decision, a mid-route one, the last layer).**

Review notes (the runtime rule differs from the V3D rig in these places; the build session must port the one-city version):
1. **Fixtures need the option set.** `decision()` frames `current + options` (`V3D/cam_rig.py:150-158`); the options come from the game graph. Store `options[]` in each fixture so the parity test feeds the same set.
2. **Yaw is mirrored by `sgn` and runs off `yaw0`.** The rig has `yaw(u) = 24*(1-2u)` (`cam_rig.py:146-147`) with `u = layer/(LAST-1)` clamped 0..1 (last-layer `u` is above 1 and clamps). One-city: `yaw = yaw0_rig + sgn * 24 * (1 - 2u)`.
3. **The hover side test is world-x in the rig** (`cam_rig.py:165`, `c[0] > p.F[0]`). In the one-city street the street runs along any of x/y, either way. The test must be "the hovered room centre is to the screen right of `F`", i.e. `(c - F) . right > 0` with `right = (nrm.y, -nrm.x)`; `HOVER_YAW` is added when it is, subtracted when not.
4. **Look-bias sign differs.** The rig: `bias = -LOOK_BIAS * yaw/24`, documented "away from where the camera looks" (`cam_rig.py:34, 158`). The derive: `bias = sgn * 0.10` with the camera turned the same way (`sb_onecity.py:377`; `sgn = +1` start left, camera turned right, bias positive moves the framed set right, toward the look direction). They are opposite. The approved one-city renders came from the derive, so the derive sign should win, but this is **unverified against a still**; the build session must check one DECISION still and then the spec 6.2 table row `LOOK_BIAS` and the `cam_rig.py:34` comment need an edit. Either way the runtime and the fixtures must use the same sign.
5. The OVERVIEW is solved once and does not depend on `walked` (`sb_onecity.py:367`), unlike `cam_rig.overview(walked)` (`:170-177`). Store it.
6. Hover `k` is not stored: `hover(walked, node, k)` eases with `k` from 0 to 1 (`cam_rig.py:161-167`); the fixtures store the `k = 1` pose.

## Q2.2 Dive path

**AD 2026-10-18: store the end poses plus the constants; the runtime interpolates per spec 6.3. The fixtures include 5 dive samples (u = 0, .25, .5, .75, 1) for parity.**
Stored: `dive.hq_pose` (`loc`, `tgt`, `lens` 300, `yaw` 135 layout36 = -45 rig, `pitch` 40; `dist = frame width * 300/36` = 3833.33 for the 460 BU frame, `SB/sb_ocjobs.py:35, 65-67`), `dive.overview_pose`, `duration_s` 3.0 (`:33`), and the smootherstep and lag constants (`s = smootherstep(u)`, `sp = smootherstep(min(1, 1.08u)^1.6)`, `:60-62, 77-78`). The 1.08 and 1.6 are tuning numbers and belong in the file too (rule 5).

## Q2.3 Rig constants

**AD 2026-10-18: store the rig constants in the file.** The list in the proposal is incomplete and one value is wrong for the street. The runtime DECISION needs, from `V3D/cam_rig.py:24-37` and `sb_onecity.py:36-41`:

| Key | Value | Source |
|---|---|---|
| `yaw_max`, `pitch_d`, `lens_d`, `fill_w`, `fill_h`, `look_bias` | 24, 9, 30, 0.66, 0.70, 0.10 | `cam_rig.py:30-34` |
| `hover_pull`, `hover_yaw`, `hover_dolly` | 0.22, 3, 0.96 | `:35` |
| `ov_yaw_k`, `lens_o`, `fill_ow`, `fill_oh` | 0.3, 40, 0.95, 0.90 | `:36` |
| **`pitch_o` (street)** | **2.0**, not 6 (6 is the V3D side-view value) | `sb_onecity.py:40-41`, spec 6.2 rule 3 |
| `ov_base_frac` | 0.815 | `sb_onecity.py:41` |
| `t_step`, `t_hover_in`, `t_hover_out`, `t_zoom` | 0.9, 0.30, 0.35, 1.0 (spec 6.2 replaces the rig's 0.70) | `cam_rig.py:37`, spec 6.2 |
| `sensor_mm`, `ref_w`, `ref_h`, `use` | 36, 1920, 1080, (300, 138, 1900, 1012) | `cam_rig.py:24-26` |
| solver | 60 iterations, bracket [5, 3000] | `cam_rig.py:122-143` |

`ov_yaw_k * yaw_max = 7.2` is the derive's OVERVIEW offset (`sb_onecity.py:367`), so one constant set serves both.

## Q2.4 `zoom_dive` / `zoom_detail` per pose

**AD 2026-10-18: accept; store `zoom_dive` and `zoom_detail` per pose as check values.**
Correction to the proposal's wording "computed from `dist`": `zoom_dive` uses the distance from the camera **to the OVERVIEW target**, not the pose's own `dist` (`SB/sb_ocjobs.py:94-102`: `dist(p) = |p - ov.target|`; spec 5.1). During the dive the target moves, so the two differ. `d0` is `|hq_pose.loc - ov.tgt|` (not exactly 3833.33) and `d1` is `overview.dist`; both are per run. `zoom_detail` uses the camera distance to the pose's own target.
Store `zoom: {d0, d1, d_ov, d_dec}` in BU with these definitions.

## Q2.5 `d_dec`

**AD 2026-10-18: `d_dec = derive.decision.dist` (the solved top-level DECISION pose) for both kinds. It is never null.**
Note: for the street that is the first-decision pose (layer 0, `sb_onecity.py:363-377`, `cur = [G.WALK_START[-1]]`); its framed set differs at other layers, so `d_dec` is a reference constant, not the live DECISION distance. `zoom_detail` is consumed only by the HQ (spec 5.1), so this costs the street nothing.

## Q3.1 Band table

**`lod.bands` = the numbers below. Weight 1 at the near end (`d1` = 114.6 BU), 0 at the far end (`d0` = 3833 BU), a smoothstep in `zoom_dive`, which is linear in `ln d`, so use `t = clamp(ln(d_far/d)/ln(d_far/d_near))`, `w = t*t*(3-2t)` (not a smoothstep in linear distance).**
`lod.DEFAULT_BANDS` does not exist at `6a58733c`; the band source is `HK/lod.py:16-23` (`LOD_BANDS`, zoom pairs) and `SB/look_preset.py:74-91`. `d(z) = 3833 * (114.6/3833)^z`; `ln(d0/d1) = 3.50996`.

| Band (v2 name) | `(a, b)` | `d_far` (z = a) | `d_near` (z = b) | Spec 5.2 prints |
|---|---|---|---|---|
| `fog_octaves` | 0.25, 0.60 | 1593.9 | 466.6 | 1594 -> 466 |
| `wisps` | 0.45, 0.70 | 789.9 | 328.5 | 790 -> 328 |
| `plumes` | 0.50, 0.72 | 662.8 | 306.2 | 663 -> **307** |
| `signage` | 0.60, 0.82 | 466.6 | 215.6 | 466 -> 216 |
| `small_lights` | 0.75, 0.92 | 275.6 | 151.8 | 276 -> 152 |
| `puddles_sharp` | 0.85, 1.00 | 194.0 | 114.6 | 194 -> 115 |
| `fog_density` (ramp, level 0.35 at zoom 0) | 0.30, 0.90 | 1337.3 | 162.8 | 1336 -> 163 |
| `cityglow` (ramp, level 0.45 at zoom 0) | 0.30, 0.90 | 1337.3 | 162.8 | 1336 -> 163 |
| `look_blend` | 0.20, 0.55 | 1899.6 | 556.1 | 1898 -> 556 |
| `section` (cut height, 5.3) | 0.25, 0.85 | 1593.9 | 194.0 | 1594 -> 194 |

Rules for the file:
- The first six rows are the `lod` bands (`FLOORS`: `signage` 0.0, `small_lights` 0.25, `HK/lod.py:25`; weight `f + (1-f)*s`). The last four are ramps owned by `look.preset`, not `lod` (see Spec edits); `fog_density` and `cityglow` are read in `SB/fog_r3.py:186` and `SB/sb_r.py:178`.
- Spec 5.2 rounds, and three cells are off by more than rounding (`plumes` near 307 vs 306.2, `look_blend` far 1898 vs 1899.6, the fog ramp far 1336 vs 1337.3). Store the zoom pairs `(a, b)` as the source and the distances computed from them at 1e-4; the spec table is then descriptive.
- The anchors 3833 / 114.6 are constants of the table. `zoom_dive` for a pose uses the run's own `d0`, `d1` (Q2.4); they coincide only for the concept run.

## Q3.2 Weights

**AD 2026-10-18: weights are parity data only, stored for `overview`, `decision` and the fixture poses.** They are derivable from `dist`; the shader and the Godot code compute them live from the camera-to-asset distance.

## Q3.3 Band names

**AD 2026-10-18: rename to `fog_octaves`, `wisps`, `plumes`, `signage`, `small_lights`, `puddles_sharp`.** `lod.floors` keys follow (`signage`, `small_lights`). Spec 5.2 / 5.2b name the old keys; they get an alias note (Spec edits).

## Q3.4 `section.params`

**Per pose, not per run; and HQ only.** `section_params(pose_loc, cfg, rooms_pts, zref, margin)` (`HK/downtown.py:277-316`) depends on the camera position and the framed rooms: overview uses `rooms_pts=None` (the keep, `:306-310`), decision/hover use the framed rooms (`:301-304`), so the values change every frame. Store them under `poses.<name>.section` (overview, decision, fixtures) in the same way as `lod.weights`. The street netrun does not use `sec_*`: its cut is `section.zcut` (5.3). For `kind: "street"` omit `section.params`.

## Q3.5 `sec_on` / `occ_on`

**AD 2026-10-18: bool in JSON, 0/1 in the shader.** Code: the concept holds `1.0` and `set_frame` writes `float(p.get(k, 0.0))` for every key (`HK/section.py:19-22`), so a missing key is off.

## Q3.6 Units of `sec_s0`, `sec_w0`, `sec_slope`

**`sec_s0` and `sec_w0` are BU in the scene the function ran in; `sec_slope` is unitless (rise per BU of horizontal run).**
`s0` is a support distance along the horizontal camera direction (`HK/downtown.py:301`), `w0` is the lateral support plus a literal pad (`:302` rooms +24.0, `:307`/`:310` overview +30.0), `slope = (cam z - zref)/max(1, L - s0)` (`:312`). The pads are kit units; the values from the kit are in kit BU (8 BU storey). After the HQ is in one-city units, `s0`/`w0` computed from the rescaled points are one-city BU, and the pads come from `consts.band_*` (7.125 / 5.70). So the numeric parity data must be produced on one-city points, never converted afterwards.

## Q3.7 `sec_plinth` 0.6

**Not one-city BU.** It is a literal inside `section_params` (`HK/downtown.py:316`), in kit units, and `NA03_NA04_ANSWERS.md` O-K does not list it. By the O-K rule it becomes `0.6 * 0.2375 = 0.1425` BU.
Nothing in the concept reads it: `sec_plinth` and `sec_widen` (0.45, `:316`) appear only in the returned dict and in job JSON dumps; no script under `route_map_graph/*/scripts` consumes them. **Recommendation:** keep both in `section.params` with the converted value for parity, mark them "no concept reader", and drop them if NA-03 also finds no consumer.

## Q3.8 `k_fit`

**AD 2026-10-18: `k_fit` applies when the HQ scene is uniformly scaled. For the street, `k_fit = 1`.** Add `k_units` (0.2375) and `k_fit` to `section.consts` so the file shows which factor produced `band_overview`, `band_rooms` and `zref_margin`. Arithmetic checked: 30 x 0.2375 = 7.125, 24 x 0.2375 = 5.70, 1.5 x 0.2375 = 0.35625 (rounded 0.356 in the file is fine at 1e-4: 0.3563).

## Q3.9 `section.zcut` and `look_blend`

**AD 2026-10-18: keep `1.0e4` as the "no cut" sentinel.**
- `section_by_zoom` = `(zf, zn, a, b)` = `(60.0, 0.4, 0.25, 0.85)` (`SB/look_preset.py:90`), axis `zoom_dive`. `zcut(z)`: `u = smoothstep((z - a)/(b - a))`, result `exp(ln zf + (ln zn - ln zf) * u)` if `u > 0` else `1.0e4` (`SB/sb_ocjobs.py:111-115`). Spec 5.3 matches (60 -> 0.4, smoothstep over 0.25..0.85). The header comment in `look_preset.py:88-89` still says "1.2 BU plinth"; the value is 0.4.
- `look_blend_by_zoom` = `(0.20, 0.55)` (`SB/look_preset.py:87`), axis `zoom_dive`; `look_w(z) = smoothstep((z - 0.20)/0.35)` (`SB/sb_ocjobs.py:105-108`).
Store as `section.zcut {zf, zn, a, b}` and `section.look_blend [a, b]`, both documented "on `zoom_dive`".

## Q3.10 Key format of the shader twin

**Flat scalar keys.** `HK/section.py:31-32`: `KEYS = ("occ_on", "occ_cx", "occ_cy", "occ_cz", "occ_ux", "occ_uy", "occ_tsoft", "occ_a0", "occ_amax", "occ_vsoft", "occ_stub", "occ_ghost", "occ_edge") + tuple("occ_%s%d" % (c, k) for c in "tTv" for k in range(NK))`, `NK = 5`: 13 scalars + 15 knots (28 floats), order `occ_t0..4, occ_T0..4, occ_v0..4`. `set_frame` writes each as a float (`:19-22`). The same names are read in `occlusion_state` (`HK/downtown.py`, via `_knot`: `"occ_%s%d"`).
**AD 2026-10-18: three arrays of 5 in JSON (`occ_t`, `occ_T`, `occ_v`). The GDScript/shader twin unpacks them to the flat uniform names.** Keep the flat names for the 13 scalars, and keep `occ_a0` / `occ_amax` (the proposal's list omits neither).

## Q3.11 Rail source for occlusion

**AD 2026-10-18: confirmed, the rail comes from `zoned.json` only.** Code: `occlusion_params` / `occlusion_state` take only the camera, the target points and the buildings (`HK/downtown.py:323-`, `hq_tethys/scripts/occlusion.py:15-76`); the only rail-related code is `corridor_low` in the city build (`HK/downtown.py:121, 425`), not in the occlusion rule.

## Q4.0 Dress lists: design

**AD 2026-10-18: `dress_<run>.json` v1 is read by BOTH Godot and Blender. Godot builds the per-seed city at runtime, so `dress` needs a GDScript twin: add it to NA-21 scope, ported last.** (This answers Q4.3.)
Common rules: every list is sorted by its first key (then the next key); every id is a string, every key in a stream is an int or a string (spec 3.5 rule 1); positions rounded to 1e-4 BU (3.5 rule 4); `u` as in Q1.5; `nrm` is the same vector as `derive.nrm` (it points from the street into the building, so "toward the street" is `-nrm`); every list is generated regardless of the camera.

## Q4.1 Power units

**AD 2026-10-18: `power` is relative, 0..1, times a per-list base in `look.preset`.** `look.preset` also owns the maps from that to Blender watts and to Godot energy. Concept bases (`M44/onecity_cycles.py`, calibrated values in `SB/sb_ocjobs.py:36-44`): lamp 80 (`:178-182` uses `LKA["lamp"]`), wash 1500, ground lamp 20. For glows the concept power is `ground_lamp * uniform(0.6, 1.2)` (`:200`), so with `power = uniform(0.5, 1.0)` the base is `1.2 * ground_lamp` and the ratios are preserved.

## Q4.2 Colour

**AD 2026-10-18: colour is a palette id string into `look.preset` palettes, never RGB.** The concept uses colours that are not palette entries yet; `look.preset` must add them or the dress list cannot name them:
- palette today: `district_a` magenta (1, .16, .6), `district_b` cyan (.16, .8, 1), `accent_warm` amber (1, .58, .18), `accent_cool` violet (.62, .38, 1) (`SB/look_preset.py:10-18`).
- signs / bands (`_PAL2`, `M44/onecity_build.py:101`) = `district_a` / `district_b` exactly.
- beams (`_BCOL`, `onecity_cycles.py:253`) already use ids.
- glows (`_gcols`, `:191`) = (1, .62, .3), (1, .2, .62), (.2, .78, 1), (1, .62, .3), (.62, .38, 1): map to `accent_warm`, `district_a`, `district_b`, `accent_warm`, `accent_cool`; the drift is at most 0.12 per channel, so the look-dev golden images need a re-check.
- lamps (`:181`): (1, .72, .42) warm and (.55, .85, 1) cool: new ids `lamp_warm`, `lamp_cool`.
- lanes (`:620-622`): head (1, .92, .8), (1, .85, .6); tail (1, .12, .08), (.95, .15, .1): new ids `lane_head_a`, `lane_head_b`, `lane_tail_a`, `lane_tail_b`.

## Q4.3 Does Godot read the dress lists?

**Yes (AD 2026-10-18, see Q4.0). `dress` gets a GDScript twin, in NA-21 scope, ported last.** Not designed from concept code beyond what Q4.4 lists.

## Q4.4 Shapes and seed streams

**AD 2026-10-18 gave the shapes and stream keys below. The code check follows each list: what the concept does, and where the shape loses something.**
Per-object streams keyed by id; draws in the fixed field order given; `uniform` is the splitmix64 draw of spec 3.5 rule 2; `randrange(n) = floor(uniform * n)`. Moving items loop on T = 4.0 s (spec 3.6 rule 4); `phase` is the start offset.

### signs: stream `(hero_sign, bid)`
Shape (AD): `signs[] {bid, layer, pos xyz, nrm xy, w, h, panels int, pal}`, sorted by `bid`.
Concept (`M44/onecity_build.py:98-126`): one blade per route column, a lit band under the roof.
- **Draws: none today.** `hs = random.Random(9970 + k)` is created (`:110`) and never read; position, size and panel count are rules. Reserve the stream; a port must not invent draws.
- `pos` = the start-side corner: `u = ci.u1 - 0.25` if `street.a[axis] > street.c[axis]` else `ci.u0 + 0.25` (`:112`), offset 0.25 BU toward the street, `z = 2.2` (`:113`); `h = max(4.5, top - 1.6) - 2.2`; `panels = max(3, int(h / 1.4))` (`:115`); the blade stands out from the face by 0.35..1.15 BU, so `w = 0.8`.
- `pal`: `k % 2` over the layer-sorted columns (`:103`), `k = layer - 1`. Panel brightening `(p + k) % 3` (`:119`) is a rule from `panels` and `layer`, not stored.
- **Add `band_pal`** (the lit band is the OTHER palette of the pair, `_PAL2[(k+1) % 2]`, `:125`); the band spans `ci.u0 + 0.4 .. ci.u1 - 0.4` at `top - 0.75`, height 0.32 (`:123-125`). Without `band_pal` the hero element is half described. The band geometry can be derived from `col_info`.

### lamps: no stream
Shape (AD): `lamps[] {u, side -1|1, pos xyz}`. Kerb offset per audit row 37: half street width minus 0.3 BU, i.e. +-3.7 for the 8 BU border street, not +-2.6.
Concept: every `lamp_step` 6.0 BU from the street's `u` start (`:178`), `side` +-2.6 about the street centre line (`:179`; this is the value the audit row corrects, the street is 8 BU wide `:621`), `z = 1.6`. Deterministic.
- **Add `pal`:** the colour alternates over a running index `k` that counts lamps, not sides: `warm if k % 3 else cool` (`:181`), loop order `u` outer, `side` -1 then +1 inner. Either store `pal` (`lamp_warm` / `lamp_cool`) or state the rule "sorted by `(u, side)`, `k` = index, cool when `k % 3 == 0`". Recommendation: store `pal`.

### washes: no stream
Shape (AD): `washes[] {u, pos xyz, dir xyz, power, pal}`.
Concept (`:206-218`): one spot per route column, sorted by `bld` key (not by layer), at the column's `u` midpoint, 3.5 BU toward the street from the face (`d = -3.5 * nrm`), `z = 0.4`, aimed along `(nrm, 0.55)` normalised, spot 70 deg, blend 0.8, colour `k % 2` over that `bld` order (magenta when `k` is odd, the opposite of the sign pairing).
- Because the order differs from the signs' (layer vs `bld`), **store `pal` explicitly** (the shape already does); never derive it from an index. Spot angle and blend are look constants, not per-row.

### glows: stream `(ground_glow, i, j)`
Shape (AD): `glows[] {cell [i, j], pos xyz, power, pal}`, kept cells only, sorted by `(i, j)`.
Concept (`:187-203`): grid `i`: `u = u_start - 30 + 9.0 i` while `u < u_end + 30` (`:189`); `j`: depth `d = plinth_off + 2 + 7.2 j` (`ground_glow_step * 0.8`) while `d < 60`, `plinth_off` 4.2 (= border street width / 2 + 0.2, spec 5.3); `z = 0.9`; position `(u + jitter_u, cross_line - sign * (d + jitter_d))`.
- **Draw order per cell stream:** (1) keep test, keep when `uniform <= ground_glow_p` 0.55 (concept skips when `> p`); (2) `jitter_u = (uniform - 0.5) * 0.8 * 9.0`; (3) `jitter_d = (uniform - 0.5) * 0.6 * 9.0`; (4) `power = 0.5 + 0.5 * uniform` (Q4.1); (5) `pal = palette index floor(uniform * 5)` (Q4.2 list). Python evaluates the power draw before the colour draw (`:200-201`), and a skipped cell still consumes its keep draw. With per-cell streams that last point disappears.
- The grid origin (`u_start - 30`) must be stated in the spec; `cell` is meaningless without it.

### beams: stream `(beams, bid)`
Shape (AD): `beams[] {bid, pos xyz, lean_deg, sweep_deg, phase 0..1, pal}`.
Concept (`:236-262, 354-369`): 6 tallest non-route roofs with `top >= 1.35 * H_FRONT`, `25 < d < 170` from the street midpoint, `_far > 12`, spacing > 45, sort `(-top, bid)` (`:244-251`); colour by pick index `_BCOL[k % 6]` (`:253`, store as `pal`); `pos = (roof centre, top + 0.5)`.
- **Contradiction with the shape:** the concept beam is static (no sweep, no phase; the shaft is a fixed cone of half angle `beam_half` 6 deg, `:366`). `sweep_deg` / `phase` are new, taken from the r3 street set (`SB/look_preset.py:56`, `sweep_deg (4.5, 6.0)`).
- **Contradiction with `lean_deg` as one number:** the lean is a 2-axis direction `(lx, ly, 1)`: `lx = 0.12 + 0.30*h1` signed away from the street midpoint in world x, `ly = 0.18 + 0.12*h2` (only when the street runs along x) (`:358-361`). A single angle loses that. **Recommendation:** `lean_deg [x_deg, y_deg]` = `atan(lx)`, `atan(ly)` in world x and y.
- Draws (replacing the legacy key hash `key * 2654435761 % 1000`, `:358`, `key * 40503 % 1000`, `:360`): (1) `lx = 0.12 + 0.30 * uniform`; (2) `ly = 0.18 + 0.12 * uniform`; (3) `sweep_deg = 4.5 + 1.5 * uniform`; (4) `phase = uniform`. Legacy parity is lost by design.

### streak_lanes: stream `(street_lanes, lane_id)`
Shape (AD): `streak_lanes[] {lane_id, a xy, b xy, z, speed BU/s, phase 0..1, pal}`.
Concept (`:614-650`): 4 lanes at fractions `0.28, 0.62, -0.3, -0.64` of the half street width, direction +1, +1, -1, -1; each lane is a chain of quads, per streak `length = uniform(3, 16)`, `brightness = uniform(0.5, 1.3)`, then `gap = uniform(4, 22)` (`:627-637`); `z = 0.12`, half width 0.12. The whole chain slides by `dir * P * (t mod 4)/4` with `P = lane_period` 80 BU (`:615, 642-646`), i.e. 20 BU/s.
- **The shape has no place for the streaks.** A lane is a chain of many streaks; `{a, b, z, speed, phase, pal}` describes one moving item. **Recommendation:** one row per lane with `streaks [[s, length, brightness], ...]` (`s` = start offset along the lane in BU), so the file is self-contained and Godot need not replay the stream. Draw order along the lane: length, brightness, gap, repeated.
- **Loop seam:** the chain is not periodic in `P`, so sliding it by `P` and resetting produces a visible jump at the 4 s loop in the concept. For a seamless loop the pattern must repeat every `speed * T = 80` BU (generate one 80 BU cell and tile it) or each streak must wrap on its own. The AD to pick; until then write `speed = P / T` and state the seam.
- `lane_id`: ints 0..3 as keys (spec 3.5 allows ints or strings).

### fog_fields: no stream
Shape (AD): `fog_fields[] {id, min xyz, max xyz, density 0..1}`.
Concept: ONE box for the whole city, `x, y` -700..900, `z` 0..`max(240/S, 2.5 * H_SKY)` (`:529`), with peak density `fog_peak` 0.0507 and a procedural noise material. Note `-700..900` is a literal; the writer must derive the box from the city extent, not copy it. `density` 0..1 is a multiplier on `look.preset` `fog_peak`. Extra fields (`mid_bank`, `ground_bank`, `wisp_k`, `haze`) stay in `look.preset`.

---

## Spec edits (to `route_map_graph/PIPELINE_SPEC.md`; not applied)

1. **6.1 / 6.2:** state the yaw convention once (Q1.7) and rewrite the 6.2 one-city overrides in the rig convention: `yaw0 = atan2(nrm.x, nrm.y)`; OVERVIEW yaw `yaw0 + sgn * 7.2`; DECISION `yaw0 + sgn * 24 * (1 - 2u)`. Add the hover side test `(c - F) . right` (Q2.1.3).
2. **6.2 table:** `LOOK_BIAS` row: reconcile the sign with the derive (Q2.1.4) after one still is checked; add `ov_pitch` 2.0 and `ov_base_frac` 0.815 as street constants (Q2.3). The `OV` row says pitch 6 for the V3D rig only.
3. **2.3 `rooms` row:** `front` / `back` corner order (Q1.1); `floor` 0-based (Q1.2); `parts` as sorted indices into `buildings[bld].parts` (Q1.3); `col_info` `u0/u1` definition (Q1.5, if the recommendation is taken) and `face` as a float (Q1.6); `persp` removed (Q1.9); `kind` is an open string enum: spec 2.3 lists `rest`, `workshop`, `cache` besides the four the proposal names, so the reader must not reject them.
4. **2.3 `version`:** per-file versions (Q0.1); readers reject unknown versions; link `type` readers reject unknown types (Q1.4).
5. **2.2 / new section:** `poses_<run>.json` v1 and `dress_<run>.json` v1 file schemas (this review plus the proposal), including `fixtures[]` and the complete rig constants table of Q2.3.
6. **5.1:** `zoom_dive` distance is to the OVERVIEW target, `d0 = |hq.loc - ov.tgt|`, `d1 = overview.dist`, per run; `d_dec = derive.decision.dist` (Q2.4, Q2.5).
7. **5.2:** rename the six `lod` band keys (Q3.3), add the smoothstep-in-`ln d` formula and the "weight 1 at the near end" sentence (Q3.1), correct the rounded distances (`plumes` 306, `look_blend` 1900, ramps 1337 -> 163) or mark them approximate, and move `fog_density`, `cityglow`, `look_blend`, `section` out of the "bands" table into a "look ramps" table owned by `look.preset`.
8. **5.3:** note `look_preset.py:88-89` still says 1.2 BU plinth; the value is 0.4.
9. **7.2:** add the `sec_plinth` 0.1425 / `sec_widen` 0.45 rows with "no concept reader" (Q3.7); add `k_units`, `k_fit` to `section.consts`; `section.params` and `occlusion.params` are per pose (Q3.4); `occ_*` JSON as three arrays, GDScript unpacks to the flat `KEYS` names (Q3.10).
10. **3.5 stream table:** `hero_sign` row "no draws in the concept"; `beams` row draw order (Q4.4); `ground_glow` draw order and grid origin; `street_lanes` draw order and the `(street_lanes, lane_id)` key; add the `fog_fields` and `lamps` rows as "no stream".
11. **9.1 / 9.6 (dress):** `signs` carry `band_pal`; `lamps` carry `pal` and the +-3.7 offset (audit row 37); beams have a 2-axis lean and a sweep (new relative to `onecity_cycles.py`); streak lanes list their streaks and state the loop-seam rule; palette ids `lamp_warm`, `lamp_cool`, `lane_head_a/b`, `lane_tail_a/b` added to `look.preset` (Q4.2).
12. **NA-21 scope:** add the GDScript twin of `dress`, ported last (Q4.0).

## AD resolutions of the findings (AD 2026-10-18)

These override the rows above where they differ.

1. **Q1.1:** the writer normalises both quads to BL, BR, TR, TL as seen from the street (camera side), for every `nrm`.
2. **Q1.5:** `u0` and `u1` (and every dress `u`) are the signed distance in BU from `street.a`, measured along `street.c - street.a`. The concept's absolute axis coordinate is not kept.
3. **Q1.6:** `face` stays one float, the world coordinate on the cross axis.
4. **Q1.7:** v2 stores the rig convention: 0 = +y (north), clockwise positive. `yaw_rig = 90 - yaw_layout36`. The writer converts derive poses.
5. **Q1.8:** `shift_x` and `shift_y` are both fractions of the frame width. NA-21 adds a pixel-parity test for Godot's `frustum_offset`.
6. **Q2.3:** add the missing constants: `yaw_max`, `pitch_d`, `lens_d`, `fill_w`, `fill_h`, `look_bias`, `ov_base_frac`, the usable area, `sensor`. Use the street `pitch_o` 2.0 from the code, not 6.
7. **Q2.4:** `zoom_dive` uses the distance from the camera to the OVERVIEW target. `d0` and `d1` are per run in `zoom`; the band-table anchors (3833, 114.6) are constants in `lod`.
8. **Q2.1:** the hover side test becomes screen-right. Keep the derive's look-bias sign (+sgn x 0.10). Art-pass checks it against a still before NA-21 freezes.
9. **Q3.4:** `section.params` and `occlusion.params` are per pose. They are stored in the overview/decision poses and in each fixture, not per run. `sec_*` is HQ only.
10. **Q3.7:** `sec_plinth` is 0.1425 BU (0.6 kit x 0.2375).
11. **Q3.10, ruling reversed:** JSON uses the shader's 28 flat `KEYS` (HK/section.py:31-32) unchanged, so the twin copies them 1:1. No arrays.
12. **Spec 5.2:** use the computed edges in the Q3.1 table (plumes near 306.2, look_blend far 1899.6, fog ramps far 1337.3). Art-pass corrects the spec.
13. **Beams:** `lean` is `[x, y]`. Add `sweep_deg` (default 0, static as in the concept) and `phase`, so the always-alive sweep (9.6) can be enabled per preset. Lean comes from the (beams, bid) stream.
14. **Streak lanes:** `streak_lanes[] {lane_id, a, b, z, speed, pal, streaks[] {u0, len, gap, bright}}`. Each streak wraps per streak, modulo the lane length L. `speed` is quantised so that `L = k * speed * T` for an integer k, which loops seamlessly on T = 4 s.
15. **Signs:** add `band_pal`. The (hero_sign, bid) stream stays reserved for jitter; it has zero draws today.
16. **Lamps, washes:** store `pal` explicitly (the lamp pattern is cool when k % 3 == 0, the wash order is by bld).
17. **Glows:** the draw order is keep, jitter_u, jitter_d, power, colour. Colour is a palette id plus `drift` [r, g, b] (max 0.12 per channel) drawn from the stream. The palette-id list in Q4.2 is adopted, with new ids for lamps and lanes.
18. **Fog:** `fog_fields[]` keeps its list shape. The concept has one global box (-700..900), so v1 has one entry; per-district fields come later.
19. **Room kinds:** readers accept rest, workshop and cache as well as the four types; run_graph v2 adds them (D4). Unknown kinds are rejected.

## Check input shapes for NA-04 (AD 2026-10-18)

1. **Beam check input: accepted, with three changes.**
   - `beams[]` comes from `dress_<run>.json` `beams` (`bid`, `pos`, `lean` [x, y], `sweep_deg`, `phase`, `pal`), plus `top` from city.json.
   - `spot {cone_deg, blend, shadow, media_linked}` and `shaft {material, shadow}` are the look.preset beam rig, merged by the checks loader. They are not stored per beam in dress.
   - `route_bids` is derive `route_keys`, which now holds bids.
2. **Dress: `items[{kind, pos}]` rejected.** The checks read the typed lists of `dress_<run>.json` (signs, lamps, washes, glows, beams, streak_lanes, fog_fields). For 12.4.5 (foreground dressing in front of a room opening), the loader flattens every list item that has a `pos` into `(list name, pos)`.
3. **Piers: accepted** as `zoned.json` `rail.piers` [xy] in BU plan coordinates (piers every 7 BU on street tiles). This adds a field to the O-C rail object.
4. **12.4.5c: accepted** as the front-opening box grown by 0.5 BU, the same offset as the facade link paths. Provisional. **Superseded by AD 2026-10-18 (NA-03 Q1):** lateral margin 0.15 BU, vertical overlap, depth from the face outward; corner hero signs at 0.25 BU pass; `dress` skips kerb lamps in a route opening's `[u0-0.15, u1+0.15]`.

On `rules_check.md`: pin `p_city_night` to its ded90765 PNG. Don't regenerate it. The 4K city finals become golden plates (queue item 3) with their own values JSON, and the other 8 band-only differences are expected under spec 12.1.
