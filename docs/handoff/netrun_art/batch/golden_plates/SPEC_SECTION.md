DRAFT for the art-pass session; unverified (no render).
<!-- model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id gold__spec; status ok; tokens in 920 cache-write 0 cache-read 68276 out 38404; cost $0.200 -->

# Draft: golden plates and Python/GDScript parity (PIPELINE_SPEC)

**Placement.** Insert as new sections **12.8 Golden plates**, **12.9 Python/GDScript parity** and **12.10 Process** (all after 12.7), plus a new **12.11** open-numbers list that is mirrored into 14.1. The section 12 checks already live in 12, and 12.6 already has a one-line parity row, which becomes a pointer. A new top-level number would force renumbering 15 and every "section 15" reference.

**Nothing here is rendered or run.** Every tolerance not already in the spec is marked `PROPOSED (N6..N11)`. Class names for GDScript twins other than `NetrunArtDeriver`, `NetrunCameraRig` and `OcclusionHelper` are ASSUMPTION.

---

## 12.8 Golden plates (designer ruling D8, 2026-10-16)

A **golden plate** is a frozen Blender reference frame plus its measured values and every input needed to rebuild it. The art-pass session produces plates. The build session captures the same view in Godot, runs the section 12 checks on the capture, and reports drift against the plate (12.8.6). The D3 reference city is a city_A2-style procedural planner city (2.0b, 3.7).

### 12.8.1 Rules

1. A plate is immutable. A change is a new `drop_id` (12.10), never an edit in place.
2. A plate carries its own camera. Godot captures use `camera` from the values JSON, not a re-solve. The rig (`NetrunCameraRig`) is tested separately against the same pose (pair P6, 12.9). If both did the same job, a rig bug would hide.
3. All plates are 16:9. The reference resolution is 1920 x 1080 (6.1 rule 2). Stored resolution is in 12.8.3.
4. A plate never contains UI, except the `_ui` variant of the storyboard keyframes (12.8.2, set K). Metrics are measured on the no-UI image.
5. Moving things are functions of `t` (3.6 rule 4). Every plate records `anim_t` in seconds within the 4.0 s loop, and Godot captures at the same `anim_t`.
6. Plates use fixed seeds only (`golden/SEEDS.json`). The per-game seed rule (2.0) is unchanged. A change to the city generator, the layout rules (3.2) or the zoning (3.4) is a re-bake trigger (12.10 rule 5).

### 12.8.2 Plate list

Id pattern: `<set>_<subject>_<view>[_<seedtag>][_<state>]`, lowercase, underscores. Priority: **P0** = checked on every build, **P1** = nightly, **P2** = before a drop is accepted.

Seed tags (`golden/SEEDS.json`; values are chosen by art-pass at the first drop):
- `s1`: the concept city, `city_A2.json`, with the spec's "seed 1" counts. ASSUMPTION: the Returns Processing link is the selected Site.
- `s2`: a second generated planner city. ASSUMPTION: chosen so `start_left` is false (the one-city mirror rule, C18) and the HQ lots differ in size from `s1` (tests `k_fit`).
- `s3`: a third city, for variance and the blended `variance_pref` falloff (3.5b).

Fixture run graphs (inputs, not game output; 8.4 hard rule): `F7` is 7 layers of 2-4 nodes (GDD 4.2). `F11` is 11 layers, for HQ slot generation on demand (D10, 8.4 rule 5).

State shorthand: `L3` = current layer 3 (zero-based) of `F7`, layers 0-2 walked, 3 options with numbers 1-3.

| Id | What it shows | Camera (pose model 6.1) | Seed | Corp | State | Pri |
|---|---|---|---|---|---|---|
| `hq_<c>_ov` | HQ OVERVIEW: landmark in its city, every route node, no UI | per-corp OVERVIEW (6.4 table: pitch, lens, yaw), framed fill 0.95 / 0.90 | `s1` | halcyon, meridian, orbital, solace, rebel_cell | `F7`, `L3` | P0 |
| `hq_<c>_dec` | HQ DECISION: front and centre on the current room + options, occlusion cone active | 6.4 DECISION azimuth rule; per-corp `cam` pitch_lo..hi at layer 3, lens 30, fill per the 6.4 table; Rebel Cell is the side view at yaw 0 | `s1` | same 5 | `F7`, `L3`, no hover | P0 |
| `hq_<c>_hov` | HQ HOVER option 1: hover pose (22 %, 3 deg, x 0.96) + the 2D power cut (9.4) | hover pose from DECISION | `s1` | same 5 | `F7`, `L3`, hover = option 1 | P0 |
| `hq_<c>_mech` | The corp's mechanic at its distinctive state: Halcyon eye + lockdown, Meridian train in / crane slewed, Orbital rocket risen + doors open, Solace UNREAD rooms frosted, Rebel Cell `SEQ` 3 + `PULSE` | DECISION | `s1` | same 5 | `F7`, `L3`, `mt` / `room_state` fixture `golden/mech/<c>.json` | P1 |
| `hq_meridian_ov_s2`, `hq_halcyon_ov_s2` | `k_fit` on a different lot size; landmark covers >= 90 % of the inset lot (8.6) | OVERVIEW | `s2` | meridian, halcyon | `F7`, `L3` | P1 |
| `hq_<c>_ov` / `_dec` / `_hov` for `tethys`, `aurelian` | same triple; **pending**: Tethys finals and the Aurelian design pass (D1, D8). `_mech` follows their mechanics | as above | `s1` | tethys, aurelian | `F7`, `L3` | pending |
| `hq_<c>_ov_f11` | Slot generation for 11 layers (D10) | OVERVIEW | `s1` | halcyon, solace (the two most vertical kits) | `F11`, layer 5 | P2 |
| `st_s1_ov` | Street OVERVIEW | one-city override (6.2): yaw `yaw0 - sgn*7.2`, pitch 2.0, lens 40, fill 0.95 / 0.90, base at 0.815 | `s1` | street (blended `variance_pref`) | `L3`, start-left | P0 |
| `st_s1_dec_a`, `st_s1_dec_b` | Street DECISION at two layers (tests the pan along the street and the yaw curve) | yaw `yaw0 - sgn*24`, pitch 9, lens 30, fill 0.66 / 0.70, bias `sgn*0.10` | `s1` | street | `L1` and `L5` | P0 (`_a`), P1 (`_b`) |
| `st_s1_hov` | Street HOVER option 1 + power cut | hover pose | `s1` | street | `L3`, hover 1 | P0 |
| `st_s1_dive_<zz>` | The dive at `zoom_dive` = 00, 25, 40, 55, 85, 100 (x 100): look blend, section cut, plinth | dive path 6.3 at the matching `u` | `s1` | street | walls closed, no route light | P1 |
| `st_s1_reveal_mid` | REVEAL mid-state: layer 2 walls dissolving, links L1 -> L2 written | OVERVIEW | `s1` | street | beat 4 at 15.2 s (ASSUMPTION) | P2 |
| `st_s2_ov`, `st_s2_dec` | Street with the start on the right (camera mirrors) | one-city overrides, `sgn = -1` | `s2` | street | `L3` | P1 |
| `st_s3_ov` | Third street; variance blend near a different HQ | OVERVIEW | `s3` | street | `L3` | P2 |
| `city_a2_night_map` | Mainline map camera, whole city, night | orthographic, yaw 135, pitch 40, lot 6 BU, emulated by 300 mm lens (6.3) | `s1` | all | mainline look | P0 |
| `city_a2_night_hero`, `city_a2_day_hero` | City hero frame, night (4.4 settings b) and day (median target 0.25, contrast cap 2.0) | fixed hero pose (art-pass records it) | `s1` | all | night / day | P1 |
| `city_a2_bay` | Bay dressing, terrain, drowned quarter | fixed pose | `s1` | tethys | night | P2 |
| `lm_<c>_city` | Canonical landmark from the full-city view, for the 8.6b silhouette IoU against `hq_<c>_ov`, normalized to a common box at 320 px | map camera framed on the landmark | `s1` | the 5 (+ tethys, aurelian pending) | night | P1 |
| `ml_hq_page` | Mainline HQ page, `look_blend` 0 (held to median 0.214 +- 0.03, 12.1) | mainline pose | `s1` | n/a | beat 1 | P1 |
| `kf_f0340`, `kf_f0400` | Storyboard frames 340 (14.17 s) and 400 (16.67 s), REVEAL; `f_0400` is also the Q4 street reference | OVERVIEW | `s1` | street | beat 4 | P1 |
| `kf_f0530`, `kf_f0600` | Storyboard hover holds (the Q6 frames): option 1, and the held hover moved to option 2 | DECISION + hover | `s1` | street | beat 7 | P1 |
| `kf_b1`..`kf_b6` | One keyframe per other entry beat (10): b1 HQ at 1.5 s, b2 plan pencil at 5.5 s, b3a terminal at 8.0 s, b3b rain at 9.4 s, b3c CRT at 10.2 s, b3d dive at 11.2 / 11.95 / 12.7 s, b5 MARK at 18.3 s, b6 zoom midpoint at 19.39 s. Frame = `round(t * 24)`; times are ASSUMPTION | per beat | `s1` | street | per beat | P2 |

Count: about 65 plates, 14 of them P0. The storyboard keyframes (set K) are also stored as `_ui` variants (12.8.3).

### 12.8.3 Plate files

**1. Location and handover.**
- Plate package (JSON, manifest, 320 px thumbs, 1280 x 720 PNGs): `docs/handoff/netrun_art/golden/<drop_id>/`.
- Full-resolution PNGs: not in git (NA-01 imported no binaries; Q1). Each is referenced by `png_sha256`.
- Inputs: `golden/<drop_id>/inputs/<seedtag>/{city.json, net.json, run_graph.json, zoned.json, derive_<plate>.json}`.
- Calibration: `golden/<drop_id>/calibration/godot_<set>.json` (12.8.5).
- Art-pass publishes with a git tag `golden/<drop_id>`.
- `MANIFEST.json` lists the SHA-256 of every file, the pinned `netrun_art` commit, Blender version, spec revision and `status` per plate. The build session verifies the manifest before using a drop.

**2. Names.** For plate id `X`:

| File | Content |
|---|---|
| `X_plate.png` | 8-bit sRGB, no UI, 1280 x 720 (repo copy). Final (2560 x 1440) or `sheet` per the 8.1 quality table for the stored original. |
| `X_plate_values.json` | values (below). The existing `*_plate_values.json` suffix is kept so the `hq_values` writers keep working. |
| `X_idx.png` | 8-bit object-index pass (0 sky, 1 compound, 2 city, 4 ground, 5 rooms, 6 movers, 7 streaks; 8.1). Godot needs this because it has no object-index pass. |
| `X_nofog_plate.png` | same camera with the volume contribution removed (12.8.5 item 2). |
| `X_thumb320.png` | 320 px wide (silhouette check, 8.3 rule 3). |
| `X_ui.png` | keyframes only: the same frame with UI. |

**3. Values JSON.** UTF-8, sorted keys, floats rounded to 1e-4 (11.5). `E` = field exists today (`hq_tethys/H_overview_v2_plate_values.json`), `N` = new.

| Field | Type, unit | Note |
|---|---|---|
| `median`, `under_010`, `over_085`, `mean` (E) | float, 0..1 fractions | Rec.709 luma of the 1280 x 720 sRGB PNG, no UI (12.1). `under_010` and `over_085` are shares, not percent. |
| `exposure`, `toe` (E) | float | Blender solve values (4.1, `values.solve`). |
| `hq_peak`, `hq_mean`, `local_bg`, `ratio_peak`, `ratio_mean` (E) | float | Today's landmark numbers. Kept for compatibility. |
| `ratio_median` (N) | float | **The 12.2 measure**: median luma of {1, 5, 6} over median of {0, 2} inside the screen box grown 35 %. Not stored today (review note 2). |
| `schema` (N) | string `"plate_values/1"` | |
| `plate_id`, `set`, `subject`, `view`, `state`, `status` (N) | strings | `status` is `candidate`, `golden` or `retired`. |
| `drop_id`, `spec_rev`, `netrun_art_commit`, `blender_version`, `rules_version` (N) | strings | `rules_version` = `derive_<run>.json` `version`. |
| `seeds` (N) | `{layout_seed:int, art_seeds:{stream:int}, seed_key:int, seedtag:string}` | The values the derivation exported (2.3). |
| `hashes` (N) | `{derive, placements, occlusion_params, geometry, png}` as hex SHA-256; `preview` = 640 x 360 deterministic render hash (12.3 rule 3) | Data and geometry hashes are exact checks. |
| `camera` (N) | `{F:[x,y,z] BU, yaw:deg, pitch:deg, dist:BU, lens:mm, sx, sy (frame widths), sensor_mm:36, res:[w,h], zoom_dive, zoom_detail, look_blend, ortho:bool}` | The pose model (6.1) in Blender axes (x east, y north, z up). Godot converts at the boundary. |
| `anim_t` (N) | float, s, 0..4 | |
| `render` (N) | `{engine, quality, spp, denoiser, device, exposure_stops, black_point}` | |
| `exempt` (N) | list of strings from `hover_cut`, `mainline`, `red_sequence`, `beam_flash`, `look_blend` | The 12.1 exemptions. |
| `probes` (N) | `[{name, world:[x,y,z] BU, px:[x,y] at 1280 x 720}]` | At least 8: the current room's 4 front corners, the TARGET, the landmark box corners. Tests the projection (12.8.5 item 8). |
| `landmark` (N) | `{present, box_px:[x0,y0,x1,y1] (grown 35 %), area_px, thumb:path, idx_counts}` | The box comes from `X_idx.png`. |
| `luma_nofog` (N) | `{median, under_010, over_085}` | Same measures on `X_nofog_plate.png`. |
| `fog` (N) | `{share:float}` | Share of pixels where Volume Direct luma > 50 % of Combined. |
| `hover` (N) | `{branch_mean, outside_mean, outside_chroma, ratio}` | Hover plates only. Values as in `Q6_power_cut.json`; `ratio` = branch / outside (about 6 expected for the 9.4 presets). |
| `rooms` (N) | `[{id, box_px, mean_luma, state}]` | Route rooms in view. |
| `occlusion` (N) | `[{bld, cut_height, opacity}]` | Buildings with `opacity < 1` or `cut_height < top + CLUTTER`, after the 0.35 s ease has settled. |
| `tiers` (N) | `{asset_kind: tier}` | The reveal tier chosen by camera distance (5.2b). |
| `beams` (N) | `{n, spacing_min, profiles:[{id, step_max, rise_px}]}` | 12.5. |
| `composition` (N) | `{R-SIL-1:…, R-DET-1:…, …}` | Raw metric values (12.7), `null` where the plate type is exempt. |
| `overlay` (N, `_ui` plates) | `{stickers:[{id, c_px}], links:[{a, b, polyline_px}], target:{mode:"arrow"|"circle"|"both", visible_share}}` | |
| `checks` (N) | `{check_id: {status, value}}` | The art-pass self-check; a `fail` blocks the drop. |
| `inputs` (N) | `{city_json, net_json, run_graph_json, zoned_json: sha256}` | Used to find plates affected by a change. |

**4. glb export** (11.5; one file per corp landmark, one per room kit, one for the route-column kit):
- glTF 2.0 binary. Z-up to Y-up by the exporter (Blender (x, y, z) -> glTF (x, z, -y); ASSUMPTION).
- Per-vertex color attribute `col` (linear). Building id as the custom attribute `_BUILDING_ID` (int, `(ci, key)` packed per the `unique_building_id` rule; ASSUMPTION on packing).
- Modular parts as named nodes (walls, courses, tubes, truss, per 11.1).
- Slots as empties named `slot_<class>_<i>` with `extras` `{normal, size, tier, course, floor}` (8.4).
- Scene `extras`: `{unit:"BU", k_units:0.2375, k_fit:<float>, kit_footprint:[w,d], rev, netrun_art_commit, geometry_hash}`.
- Lights are not in the glb. They come from the preset `.tres`.
- `geometry_hash` is the 12.3 rule 2 hash of the buffers, repeated in `MANIFEST.json`.

### 12.8.4 Tolerances

"Abs" columns are binding spec rules. "Drift" is the Godot capture against the plate, **PROPOSED (N6)**; the build session calibrates it in the first calibration pass.

| Check | Blender plate (abs, binding) | Godot capture (abs) | Godot vs plate (drift) PROPOSED |
|---|---|---|---|
| 12.1 `median` (R-VAL-1) | pass 0.11-0.17; warn 0.09-0.11 and 0.17-0.19 (reported, never blocks); fail < 0.09 or > 0.19 (Q4) | same band | pass `abs(d) <= 0.02`; warn `<= 0.04`; fail above |
| 12.1 `under_010` (R-VAL-2) | 25-40 % | same | pass `<= 5` pp; warn `<= 10` pp |
| 12.1 `over_085` (R-VAL-3) | <= 2.5 % | same | pass `<= 1` pp; warn `<= 2` pp |
| 12.1 exempt frames | reported, not failed; `mainline` frames held to 0.214 +- 0.03 | same | reported |
| 12.1 `luma_nofog` (all three) | reported | reported | tighter: `median` pass `<= 0.015`, warn `<= 0.03` |
| 12.2 `ratio_median` | pass 1.5-2.0; warn > 2.0; fail < 1.5; no per-corp exception | same | relative: pass `<= 15 %`; warn `<= 30 %`; fail above |
| 8.6b silhouette IoU `hq_<c>_ov` vs `lm_<c>_city` | >= 0.85 (provisional), 320 px | same, on the Godot HQ and city captures | none (absolute only) |
| 12.3 data hash | exact (`derive`, `placements`, `occlusion_params`) | exact | **exact** (also the parity job, 12.9) |
| 12.3 geometry hash | exact | exact (glb buffers, Godot-built route columns) | **exact** |
| 12.3 image | preview (Eevee / CPU Cycles, fixed seed, denoiser off, 640 x 360): hash-exact twice. GPU finals: MAD <= 1/255 on 320 x 180, max <= 8/255 | **Godot repeatability**: two captures of one build, same camera, `anim_t`, TAA / jitter off: MAD <= 1/255, max <= 8/255 | not applicable (different renderers) |
| 12.5 beams (config) | exact | exact (media-linked spot cone >= 10 deg, blend >= 0.8, no shadow, shaft material) | exact |
| 12.5 beams (image) | step <= 25 % of peak, rise >= 3 px at 1080p (N4) | same on a beam-only capture (cull-mask layer) | reported until N4 is calibrated |
| 12.7 composition | thresholds of 12.7 | same | per metric relative: pass `<= 20 %`; warn `<= 40 %` (N7); reported for rules without a test |
| 9.4 `hover.ratio` | about 6 with the Q6 presets | same | pass `+-20 %`; warn `+-35 %` |
| 7 `occlusion` block | exact buildings set | exact set | per building `cut_height` `<= 0.05` BU, `opacity` `<= 0.02` |
| 5.2b `tiers` | exact | exact | **exact** |
| 6.1 `probes` | n/a | n/a | every probe within 1.0 px at 1280 x 720, else the image compare is skipped and reported as `camera` |
| Structural (luma, 320 x 180 blurred) | n/a | n/a | SSIM warn < 0.75, reported (N6) |

### 12.8.5 Expected Godot-vs-Blender differences and how the compare handles them

1. **Tone mapping and exposure.** Blender's view transform and Godot's `Environment` tonemap differ. A **calibration file** per set (`calibration/godot_<set>.json`: `exposure_offset_stops`, `tonemap`, `white`, `glow`) is fitted once on the P0 plates by matching `median`, then frozen. Drift is measured **after** the calibration. A calibration change is a drop change and needs AD approval (12.10). `abs(exposure_offset_stops) <= 0.5` is the bound (N10). Beyond it the environment is wrong, not calibrated.
2. **Fog (N5).** The r3 look relied on Blender light linking, which Godot lacks. The plate carries `luma_nofog` (the Volume Direct pass subtracted), and the Godot capture mode `--no-fog` disables the FogVolume and the volumetric fog. Drift on `luma_nofog` and on `landmark.ratio_median` is tight, and the full-frame drift is wider. Fog differences alone can never fail the landmark check.
3. **Shadows and room lights.** Cycles area lights and the few named shadows (11.3) have no exact Godot equivalent. Rooms are compared by `rooms[].mean_luma` over `box_px`, warn-only at `+-35 %` (N6).
4. **Reflections and puddles.** SSR against path tracing. The bottom street band (`foreground.street` proxy) is reported, not failed.
5. **Noise, denoise, TAA, rain.** Compare after the 1280-wide resample, on medians and shares; the SSIM row is report-only. Rain and plume particles are not compared.
6. **Bloom and glow.** `over_085` has the widest drift tolerance (2 pp warn). The glow strength lives in the calibration file.
7. **LOD tiers.** The tier of each asset kind follows the camera distance (5.2b) in both renderers. The `tiers` dictionary is compared exactly, a cheap data check that runs before any image compare.
8. **Camera and overlay projection.** The `probes` check runs first. A frustum or `frustum_offset` mistake (6.1) otherwise looks like image drift.
9. **UI.** The capture mode hides the UI layers. The `_ui` variant compares `overlay.stickers` and `overlay.links` within 2 px.

### 12.8.6 Drift report format

The build session writes, per capture batch: `docs/handoff/netrun_art/drift/<drop_id>__<godot_commit>/drift_<plate_id>.json` and `SUMMARY.md`, and posts the summary to the art-pass session.

```json
{
 "schema": "drift_report/1",
 "plate_id": "hq_meridian_dec",
 "drop_id": "<drop>",
 "godot_commit": "<sha>",
 "capture_sha256": "<hex>",
 "calibration": "godot_hq@<drop>",
 "overall": "pass|warn|fail",
 "rows": [
  {"check":"12.1.median","plate":0.1399,"godot":0.151,"delta":0.0111,
   "band":{"pass":0.02,"warn":0.04},"abs_status":"pass","drift_status":"pass","exempt":null}
 ],
 "suspected_cause": ["tonemap","fog","light_linking","shadow","ssr","lod_tier","occlusion","camera","geometry","seed","calibration"],
 "images": ["side_by_side.png","diff_luma.png"]
}
```

Rules:
1. `overall` is the worst of `abs_status` and `drift_status`, ignoring exempt rows.
2. `SUMMARY.md` has one table (plate x check, with the status) and the list of fails.
3. A `fail` on a P0 plate blocks the Godot build's art gate. It never blocks a Blender render.

---

## 12.9 Python/GDScript parity

12.6 requires identical output from the pure Python modules and their GDScript twins. This section defines the pairs, the numeric conventions, the shared vector files and the CI job. The Python module is the reference. Where a Blender node implementation exists, it also reads the vectors (Q3).

### 12.9.1 Twin pairs

| Id | Rule (spec) | Python (reference) | GDScript twin | Output compared |
|---|---|---|---|---|
| P1 | Art seeds, named streams, per-object draws, tables for flicker / strobes / windows (3.5) | `netrun_art.seeds` | `NetrunArtSeeds` (ASSUMPTION) | hashes, `u64` draws, floats, the flicker tables |
| P1b | Variance blend by HQ proximity (3.5b `district_weights`) | `netrun_art.variance` | same class | the six settings per lot |
| P2 | Mainline layout rules (3.2) | `layout.rules` | city layout builder in `MAIN/` | `city.json` bytes |
| P3 | Zoning (Z1-Z6, L3, L4, T1; 3.4) | `zoning` | **only if** the game re-runs zoning at runtime (Q2) | `zoned.json` bytes |
| P4 | Street derivation (3.3) | `derive.street` | `NetrunArtDeriver` | `derive_<run>.json` bytes |
| P5 | HQ slots on demand (8.4 rule 5) | `hq.slots` | same twin | slot list + `derive_<run>.json` (`kind: "hq"`) |
| P6 | Camera rig: framing solver, street overrides, dive path, hover, HQ orbit, `zoom_dive`, `zoom_detail` (6) | `rig` | `NetrunCameraRig` | poses (6.1 tuples) |
| P7 | LOD: bands, `reveal` tiers by distance, look blend, fog / glow multipliers (5) | `lod` | `NetrunLod` (ASSUMPTION) | weights, tier per asset kind |
| P8 | Section cut `z_cut`, plinth weight (5.3) | `section` | same | `z_cut`, plinth |
| P9 | Occlusion `occlusion_params`, `occlusion_state`, ease (7.3) | `occlusion` | `OcclusionHelper` | per-building `(cut_height, opacity)`, tween samples |
| P10 | Dressing placement lists: hero signs (9.1), city signs, lamps, washes, beams (pick, spacing, lean hash), lanes (4.1) | `dress` | `NetrunDress` (ASSUMPTION) | placement lists |
| P11 | Hover power cut: the 2D grade and the mask (9.4) | `netrun_art.grade.hover_cut` (numpy) | grade shader + mask builder | 8-bit image, per-pixel |
| P12 | Off-screen TARGET marker: visible share, arrow geometry, the 50 % switch with 5 % hysteresis, 0.15 s cross-fade (9.5b) | `netrun_art.overlay.target_marker` | same logic in the overlay view | state machine over time |
| P13 | Entry schedule: beat times, REVEAL per-layer times, MARK stagger, skip (10) | `netrun_art.entry` | the entry sequence view | state at sampled `t` |
| P14 | Link polylines clear of stickers and UI (9.2 `CLEAR_PAD`) | `overlay.link_clear` | same | polyline in px |
| P15 | Canonical JSON writer and hashes (12.3, 3.5 rule 4) | `netrun_art.canon` | `NetrunCanon` | bytes, SHA-256 |
| P16 | Preset constants (`ROOM_TL`, state colors, `LOOK`, `LOD_BANDS`) | presets (Python dicts) | exported `.tres` (11.5) | field equality; no twin logic |

### 12.9.2 Numeric conventions (both sides must follow)

1. **Floats.** GDScript `float` is 64-bit. `Vector2` / `Vector3` components are 32-bit in default builds. Hash-critical and derivation code uses plain `float` and `PackedFloat64Array`, never `Vector3` (ASSUMPTION about Godot 4.7 default builds; the vectors would reveal it).
2. **Rounding.** Positions are rounded to 1e-4 with `floor(x * 1e4 + 0.5) / 1e4` on both sides. Python's `round()` (banker's rounding) and GDScript `round()` (half away from zero) differ and are **not** used.
3. **Integers.** 64-bit wrap-around multiplication for FNV-1a 64 and splitmix64. GDScript `int` is signed: use `& 0xFFFFFFFFFFFFFFFF` equivalents and compare with `>> 11` masked to 53 bits (`(x >> 11) & 0x1FFFFFFFFFFFFF`), because `>>` is arithmetic on negatives. Vectors compare `u64` as 16-digit hex strings.
4. **Canonical serialization.** The seed key `[layout_seed, "art/<stream>", *keys]` and every hashed JSON go through a hand-written serializer: no spaces, ints as ints, floats rounded 1e-4 and printed without exponent, `-0` printed as `0`, keys sorted, strings ASCII-escaped. Neither side relies on its JSON library (`json.dumps`, `JSON.stringify` differ on spacing and number types).
5. **Sorting.** Tuple keys ending in an id (3.6 rule 3). Never dict or set order.
6. **Transcendentals.** `sin cos atan2 exp log pow` may differ in the last digits across libm. Comparisons use the float tolerances below, and the byte-exact outputs are produced after rounding to 1e-4.
7. **Time.** All time-dependent twins take `t` as an argument and never read a clock.

### 12.9.3 Vector file format

Files: `tests/parity/vectors/<pair>.vec.json` (P1 ... P16), UTF-8, canonical JSON. Binary inputs (P11) sit next to it as PNG.

```json
{
 "format": "parity_vectors/1",
 "pair": "P9",
 "spec_ref": "7.3",
 "rules_version": "<derive version>",
 "source_hash": "<sha256 of the Python module files, sorted by path>",
 "generated_by": {"cmd": "python -m netrun_art.parity.gen --pair P9", "commit": "<sha>"},
 "tolerance": {"float_abs": 1e-9, "float_rel": 1e-9, "transcendental_abs": 1e-6,
               "int": "exact", "string": "exact", "image_levels": 1},
 "cases": [
  {"id": "occ_single_target_behind_building",
   "tags": ["edge", "golden:hq_meridian_dec"],
   "inputs": {"cam": [0,0,10], "pts": [[0,50,3]], "cfg": {}, "bld": [[0,30,18,2,2]]},
   "expected": {"cut_height": 3.8, "opacity": 0.18},
   "tol": {"cut_height": {"float_abs": 1e-6}}}
 ]
}
```

(The numbers above are a shape example, not generated values.)

Case kinds:
1. **Pure** (`inputs` to `expected`). Floats at full precision (17 significant digits).
2. **Sequence** (P12, P13, P9 tween): `steps: [{"t": …, "inputs": …, "expected": …}]`, state carried between steps. Hysteresis cases include the 4.9 % / 5.1 % boundary around the 50 % switch.
3. **RNG** (P1): `{"layout_seed": …, "stream": "building", "keys": [12, 7], "canon": "<exact serialized string>", "fnv1a64_hex": "<generated>", "draws": {"u64_hex": [<8 values>], "f53": [<8 values>]}}`. Includes stream-isolation cases (adding a building does not change another building's draws, 12.3 rule 4).
4. **Image** (P11): `inputs.image = "hover_in_03.png"`, `inputs.mask = "hover_mask_03.png"`; the comparison is per-pixel with `image_levels` 8-bit levels.
5. **File** (P2, P3, P4, P5): `inputs` are paths to the golden inputs (12.8.3); `expected` is the SHA-256 of the output bytes, plus the output file stored for diff.

Required case content per pair (minimum 20 cases each unless stated):
- P9: camera behind the targets; target span 0 (the `max(span, 0.02)` guard); `hx = hy = 0` (the `max(hypot, 0.5)` guard); building exactly on the cone border; `top < stub`; 1 and 21 targets; compound buildings excluded.
- P6: bisection on both binding axes; `sgn = -1` mirror; dive path at `u` = 0, 0.25, 0.5, 0.75, 1 (pitch lags); HQ `dmin` binding.
- P7: every band at the interval edges and one step inside; a tier change position and footprint equal across tiers.
- P4: the golden scenes plus: tapered building, span 1 and 2 fallback, tie-breaks by key, a frontage that runs out (error case), duplicate keys across `ci`.
- P12: three visible-share regimes, chip position on the usable-area border (6.1 rule 3: x 300-1900, y 138-1012), camera moving across the 50 % switch.

### 12.9.4 Generation and consumption

1. The vectors are generated once by the reference Python: `python -m netrun_art.parity.gen --pair all --out tests/parity/vectors/`. The generator is deterministic. Running it twice (and with another `PYTHONHASHSEED`) gives byte-identical files.
2. The generator scans for values within 1e-9 of a 1e-4 rounding boundary and fails with `boundary_warning`, so a byte-exact case never sits on a tie.
3. `source_hash` stores the hash of the pure module files. Vectors are re-generated only on a `rules_version` bump or a deliberate vector change (12.10 rule 4). An unchanged `expected` plus a changed `source_hash` is a formatting-only regeneration.
4. Python consumes the vectors with a plain test (`tests/parity/test_vectors.py`).
5. Godot consumes them headless: `godot --headless --script tests/parity/run_parity.gd` (path ASSUMPTION). It writes `parity_report.json` with one row per case id.
6. The golden scene (`file`) cases additionally run the whole derivation in GDScript on `golden/<drop_id>/inputs/<seedtag>/` and compare bytes with the stored `derive_<plate>.json`.
7. Whole-seed coverage: the 3.3 rule 1 sweep (1,000 seeds) runs in Python only. The Godot twin runs a **seeded sample of `N8` seeds** (default PROPOSED 20) for P4 and P5.

### 12.9.5 CI check

Job `parity`, on every change to `tools/netrun_art/**`, the GDScript twins, `tests/parity/**` or a `golden/` drop:
1. `gen --check`: regenerate into a temp directory and diff against the committed vectors. A diff is a fail ("regenerate, review, and bump `rules_version` if outputs changed").
2. `source_hash` of the committed vectors must equal the current module hash, else fail ("vectors stale").
3. Python run of all vectors.
4. Godot headless run of all vectors.
5. Compare `parity_report.json` with the vector files: every case id must be reported (a missing id is a fail), every row `pass`.
6. On any fail the job prints the case id, the failing field path, expected, Python and Godot values.
7. The job also runs 12.3 rule 1 (fresh process, different `PYTHONHASHSEED`) and the P16 constants equality.

---

## 12.10 Process

1. **Generation.** The art-pass session builds the plate scenes in Blender from pure-module output at a pinned `netrun_art` commit (the build session owns the package). It renders them, runs the section 12 checks on the Blender plates, and publishes a drop (12.8.3 item 1). A drop with any `fail` on its own `checks` is not published.
2. **Verification.** The build session captures the P0 plates on every build and the rest nightly, runs the 12.8.4 checks, and writes drift reports (12.8.6). The art-pass session triages each fail into one of three classes: (a) a Godot defect (the build session fixes), (b) a stale plate (re-bake), (c) a tolerance or spec problem (AD, then the designer).
3. **Status.** A new plate starts as `candidate`. It becomes `golden` only after the designer approves it (rule 6). A `candidate` plate is reported, never gated.
4. **Vectors.** The build session owns the parity job. The art-pass session reviews the case content for edge cases drawn from the plates. A vector change needs a `rules_version` bump if any `expected` value changes.
5. **Re-bake triggers.** Re-bake only the affected plates, found through `inputs` and `hashes` in the values JSON:
   - a `rules_version` bump,
   - a `LOOK` change (the pending refresh after the storyboard v3 revision invalidates every plate, so **drop 0 waits for that refresh**),
   - a kit, landmark, preset or `k_units` change,
   - a city generator, layout rule or zoning change,
   - a Blender version change,
   - a calibration change,
   - a tolerance change.
6. **Approval.** The art-pass session sends the designer a contact sheet per drop: old and new side by side, the values table, the check statuses. The designer approves or rejects, and the ruling is logged in `docs/DECISIONS.md` as `GP-<drop_id>`. Mechanical re-bakes (metadata, hash stamps, no visible change: `abs(delta median) <= 0.005`, silhouette IoU >= 0.99, no check status change) are approved by the AD alone (ASSUMPTION). Any visible change goes to the designer.
7. **Expectation.** After the reset (2026-10-17) the art-pass session delivers the golden-plate set on a city_A2-style planner city, the Tethys decision / hover finals and the Aurelian design pass (D8). The Tethys and Aurelian rows stay `pending` until then.

## 12.11 New open numbers (add to 14.1; proposals, not final values)

| N | Item | Proposed default |
|---|---|---|
| N6 | Godot-vs-plate drift tolerances (12.8.4: median, shares, ratio, hover ratio, occlusion, SSIM, room luma) | as in the table, calibrated in the first calibration pass |
| N7 | Composition drift (12.7 on Godot captures) | pass `<= 20 %`, warn `<= 40 %` |
| N8 | Godot-side derivation sample size for P4 / P5 | 20 seeds |
| N9 | Parity float tolerances | `float_abs` 1e-9 and `float_rel` 1e-9 for arithmetic; `transcendental_abs` 1e-6 |
| N10 | Calibration bound | `abs(exposure_offset_stops) <= 0.5` |
| N11 | Stored plate resolution and repo copy | 1280 x 720 repo copy; originals by hash |

## Edits to make elsewhere in the spec

| Section | Edit |
|---|---|
| 2.2 modules table | Add `checks.drift` (reads golden plates), `parity` (vector generator + tests), `canon`, `grade`, `overlay`, `entry` rows. |
| 8.1 `values` module | Add `ratio_median` to its output and the `_plate_values.json` write (12.8.3). |
| 8.5 per-corp table | Add: the corp's `landmark.build` must export the glb with the 12.8.3 item 4 contents. |
| 8.6b rule 3 | Reference the `lm_<c>_city` plates for the IoU check. |
| 9.4 | Add the grade formula and the mask blur (review note 5); reference P11. |
| 9.5b | Add the arrow geometry and reference P12. |
| 11.1 Landmarks row | Add "validated by the glb manifest (12.8.3)". |
| 11.5 file formats | Add rows: plate PNG, `plate_values/1`, `parity_vectors/1`, `drift_report/1`, `calibration`. |
| 12 intro | Add: "A fail on a Godot capture blocks the Godot art gate, not a Blender render (12.8.6)." |
| 12.1 / 12.2 / 12.3 / 12.5 / 12.7 | Add "Godot captures: 12.8.4". |
| 12.6 `Python / GDScript parity` row | Replace the text by "see 12.9". |
| 14.1 open numbers | Add N6-N11 (12.11). |
| 15 conflicts | Add the entries in the review notes. |

---

## Review notes

1. **12.1 vs 13 (measurement resolution).** 12.1 measures the "final 8-bit sRGB PNG"; 13 resamples to 1280 px wide. This draft measures on the 1280 x 720 repo copy so both sessions get the same number (12.8.3). Needs a one-line change in 12.1. Proposed conflict entry C25.
2. **12.2 vs the existing values JSON.** 12.2 defines the ratio as median of {1, 5, 6} over median of {0, 2}. The example `hq_tethys/H_overview_v2_plate_values.json` stores `ratio_peak` 3.72 and `ratio_mean` 1.88 (`hq_peak` 0.623 / `local_bg` 0.168; `hq_mean` 0.315 / 0.168). Neither is the 12.2 measure. With peak the plate would **warn** (> 2.0); with mean it passes. This draft adds `ratio_median` (12.8.3). The writer in `HM/hq_values.py` may need a change; the old fields are kept.
3. **12.6 and object-index passes.** 12.2 reads Blender object-index passes (8.1). Godot has none. This draft stores `X_idx.png` and requires the build session to render an equivalent id mask (unlit id materials or cull layers). That is a build-session task not currently in 11.
4. **12.1 / 12 intro: "A fail blocks a final render batch".** For Godot captures the equivalent is blocking the art gate of the build, not a render. Stated in 12.8.6; the 12 intro needs the sentence.
5. **9.4, 9.5b, 7.2 are not formula-complete.** 9.4 gives presets but no formula (how desaturation, level and boost combine, the blur kernel of the mask); 9.5b gives no arrow geometry; 7.2 says "ease-in-out" with no curve. P11, P12 and P9 vectors cannot be generated until the AD fixes them. ASSUMPTION for generation: ease = smoothstep; grade outside = `lerp(rgb, luma, cut_desat * k) * lerp(1, cut_level, k)`, branch = `rgb * lerp(1, branch_boost, k)` plus the type glow.
6. **3.5 "JSON array" is ambiguous** (separators, number formats). 12.9.2 item 4 fixes it with a hand-written serializer. Needs a one-line change in 3.5 rule 1, which currently says "FNV-1a 64 over the UTF-8 of the JSON array".
7. **11.5 and 3.5 rounding.** The 1e-4 rounding is not defined as half-up. 12.9.2 item 2 defines it; Python `round()` would silently differ from GDScript.
8. **8.4 and fixtures.** 8.4 says the `Compound` chains are mock data "for concept renders only". Plates need fixture graphs (`F7`, `F11`) with game shape (GDD 4.2, D10). These are test fixtures in the spec's own words, but they should be listed in 8.4 as the only approved fixtures.
9. **Ownership boundary.** D8 gives `tools/netrun_art` to the build session; 2.2 puts `blender.scene` and `blender.*` inside that package, while the art-pass session "keeps Blender". This draft assumes art-pass authors the `blender/` subpackage and the build session merges it. Needs an AD ruling (Q3).
10. **NA-01 and binaries.** NA-01 imported text only, no binaries. Plate PNGs conflict with that (Q1); the draft stores 1280 x 720 copies and references originals by hash.
11. **Golden city vs 2.0.** 2.0 says the city is per game seed. Plates use fixed seeds and the `city_A2.json` planner format (2.0b) until the game generator emits that schema. Any game generator change is a re-bake trigger (12.10 rule 5).
12. **Q9 sheet seeds.** 40417 / 77231 / 91002 belong to the small-block variance sheet, not to full-city plates. They are not reused here, but 40417 is a good candidate for `s3`.
13. **Zoning twin.** Zoning is "re-run per seed on the game's layout" (3.4 L4). If that runs in-game, a GDScript zoning twin (P3) with a BFS and k-means is needed, which is not in the spec's twin list.
14. **Missing stream names.** 3.5's stream table lacks streams for the pencil wobble (0.7 px per vertex, 9.2) and the sticker gloss scheduler (9.3). Both need named streams so P14 and the overlay are reproducible.
15. **Name.** The example file is called `H_overview_v2_plate_values.json` inside `hq_tethys`. The proposed id pattern would rename it `hq_tethys_ov_plate_values.json`.

Q: (AD) May plate PNGs go into git (LFS or plain), or only the 1280 x 720 copies plus values JSON, with originals on shared storage and referenced by hash (NA-01 imported no binaries)?
Q: (build session / designer) Does Godot re-run zoning (Z1-Z6, L3, L4, T1) per seed at runtime, so P3 needs a GDScript twin, or does the game export `zoned.json`?
Q: (AD) Who owns the vector generator and the `netrun_art.blender.*` subpackage under D8, and should the Blender-node implementation of the occlusion clip (`HK/section.py`) also read the P9 vectors via an image test?
Q: (designer) Does the designer approve each new plate, or one contact sheet per drop, with the AD alone approving mechanical re-bakes (12.10 rule 6)?
Q: (AD) Can the AD fix the exact formulas for the hover grade (9.4), the ease curve (7.2) and the edge-arrow geometry (9.5b)? P9, P11 and P12 vectors depend on them.
Q: (AD) Should drop 0 wait for the `LOOK` refresh after the storyboard v3 revision (4.1 `TODO`), or ship first with the current `sb_ocjobs.LOOK` and re-bake everything after the refresh?
