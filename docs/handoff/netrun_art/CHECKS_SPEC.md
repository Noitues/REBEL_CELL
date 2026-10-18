# NA-04 checks spec: inputs, metrics, thresholds, reference mapping

Date 2026-10-18. Orchestrator pre-write for `docs/handoff/plan2/drafts/briefs/na04.md`. Input to the NA-04 batch drafts.

Sources: `docs/handoff/netrun_art/PIPELINE_SPEC.md` section 12 (re-imported from art-pass b68f2871; "spec 12.x" below),
`docs/handoff/plan2/NA02_FIELDS.md` (data files), and the art-pass reference checks (read only, repo
`C:/Users/noitu/Documents/Godot/rebel_cell`, branch `art-pass`, tip `6a58733cb8a461e6485de1eb32a1514275c6a52b`).
Where the spec and a reference script differ, the spec wins and the row says so. Every number below is copied from one
of those files; a value that no file gives is in the final **Open** list.

## 0. Reference sources (pinned)

All paths under `docs/concepts/` on `art-pass`; read with `git -C <repo> show art-pass:docs/concepts/<path>`.

| Short | Path | Last commit (8-char) | Role |
|---|---|---|---|
| `PVC` | `route_map_graph/proc_vs_custom/scripts/pvc_metrics.py` | 018dcbb1 | metric code moved into `netrun_art.checks` (spec 12.7) |
| `RUN` | `route_map_graph/proc_vs_custom/scripts/run_proc_vs_custom.py` | ded90765 | `RULES` table (lines 41-55), view scopes (58-60, 146-163), PASS/FAIL logic (166-187) |
| `CFG` | `route_map_graph/proc_vs_custom/scripts/pvc_config.json` | ded90765 | per-image boxes, skyline range, facade band (example) |
| `RC` | `route_map_graph/proc_vs_custom/metrics/rules_check.md` | ded9076543a4be175405487a646d0f44346a6bf4 | the reference table: 44 image rows x 14 rule columns |
| `HV` | `route_map_graph/hq_meridian/scripts/hq_values.py` | c47c67a9 | 12.1 frame values and 12.2 landmark ratio |
| `DT` | `route_map_graph/hq_meridian/scripts/hq_kit/downtown.py` | 46d161ce | `in_corridor`, `corridor_dist`, `corridor_low`, `occlusion_state` (12.4, 12.6) |
| `CO` | `route_map_graph/side_view/v3_dynamic/scripts/check_occlusion.py` | 47850a23 | rooms-unblocked check (12.6), `LIMIT = 0.08` |
| `OC` | `route_map_graph/storyboard/scripts/m44/onecity_cycles.py` | c83e3b00 | beam selection rules (12.5.3), lines 236-250 |
| `BC` | `city_all_corps/scripts/beam_check.py` | a032bf6c | landmark-vs-beam image rule (not a spec 12 check; listed for completeness) |

The 12.3.1, 12.3.4, 12.5.1 and 12.6 parity checks have **no art-pass script** (spec 12.6 source column: "new").

## 1. Common contract

### 1.1 Capture contract (spec 12.0, audit row 5)

| File | Content | Used by |
|---|---|---|
| `beauty.png` | 8-bit sRGB, no UI | 12.1, 12.2, 12.7 |
| `id.png` | unlit, nearest-sampled, no UI; **R = class**. Classes: 0 sky, 1 landmark compound, 2 city, 5 rooms, 6 landmark movers; 3 and 4 are reserved (NA02 header). The Blender pass also carries 4 ground, 7 streaks (spec 8.1); Godot captures do not | 12.2, 12.7 R-FOCUS-1 |
| `capture.json` | camera pose, resolution, `layout_seed` (decimal string), run id | all image checks (camera parameters, no hard-coded size) |
| Golden plate | the same three files; its measured values are written by the same checks | NA-04 acceptance 2 |

The image checks accept any PNG size (brief acceptance 6). `capture.json` has no field for the **view type** (OVERVIEW /
DECISION, street / HQ / city) or the **look** (AAA-2 vs mainline); the exemptions and scopes below need them (Open O-1).

### 1.2 Record and status

Brief acceptance 1: every check returns `{id, status: pass|warn|fail, value, threshold, note}`; the CLI exit code is 1 on
any fail and 0 otherwise; warn never fails. The reference `RC` knows only PASS / FAIL / `n/a` (`n/a` = the rule does not apply
to the view, or the metric is NaN). `n/a` maps to a record with `status: pass` and `note: "n/a"` unless the orchestrator rules
otherwise (Open O-2). `warn` exists only in 12.1 (median) and 12.2 (ratio above 2.0).

### 1.3 Luma and working image

| Item | Value | Source |
|---|---|---|
| Luma | Rec.709 weights on **sRGB-encoded** values scaled 0..1 (no linearization): `0.2126 R + 0.7152 G + 0.0722 B` | spec 12.1; `HV.lum`; `PVC.luma` |
| 12.1 / 12.2 resolution | native plate size, no resampling | `HV.check` |
| 12.7 working image | resampled to `WORK_W = 1280` px wide, `LANCZOS`, height `round(h * 1280 / w)`, RGB / 255 | `PVC.load_work` (l.59) |
| Valid mask | all True on captures (no UI). In the reference it is a list of normalized boxes `[x0, y0, x1, y1]` set to False | `PVC.valid_mask` (l.77) |
| Boxes | normalized `[x0, y0, x1, y1]`, converted with `round(x * w)` | `PVC.box_px` (l.71) |

## 2. Value band: 12.1 (maps to `RC` R-VAL-1, R-VAL-2, R-VAL-3)

| Item | Detail |
|---|---|
| Inputs | `beauty.png`; the exemption flags from `capture.json` (Open O-1) |
| Metrics | `median` of luma; `under_010` = share of pixels with luma < 0.10; `over_085` = share with luma > 0.85 (`HV.check`) |
| Exempt (reported, never failed) | hover power-cut frames; mainline-look frames (held instead to the capture: median 0.214 +- 0.03, `SB/NOTES.md:120`); Rebel Cell red-sequence frames; beam-pass flash frames of an entrance beat; look-blend frames (0 < look_blend < 1) |

| Check id | Pass | Warn | Fail | Source |
|---|---|---|---|---|
| 12.1 R-VAL-1 (median) | 0.11 to 0.17 (0.14 +- 0.03) | 0.09 to 0.11 and 0.17 to 0.19 (reported, never blocks) | below 0.09 or above 0.19 | spec 12.1 (Designer 2026-10-16, Q4) |
| 12.1 R-VAL-2 (under 0.10) | 0.25 to 0.40 (25-40 %) | none given | outside 0.25 to 0.40 | spec 12.1, 12.7 |
| 12.1 R-VAL-3 (over 0.85) | <= 0.025 (2.5 %) | none given | > 0.025 | spec 12.1, 12.7 |

**Conflict with the reference.** `RC` / `RUN` l.51 use R-VAL-1 = `between (0.12, 0.17)`, PASS / FAIL only. The spec band
(0.11-0.17 pass, warn bands) is wider. On the 44 `RC` rows the two disagree wherever the median is in [0.11, 0.12)
or in (0.17, 0.19] or in [0.09, 0.11): e.g. `p_sb_closed` 0.115, `p_f0340` 0.119, `p_orb_ov` 0.118 (RC FAIL, spec pass);
`c_orb_rocket` 0.176, `c_mer_ov` 0.189 (RC FAIL, spec warn); `g_solace_H_overview_test_t2_plate` 0.102 (RC FAIL, spec warn).
Brief acceptance 2 ("100 % of rows match `rules_check.md`") therefore needs a stated comparison mode (Open O-3).
R-VAL-2 and R-VAL-3 thresholds agree between spec and `RC` (25-40 %, <= 2.5 %).

`RC` scope for R-VAL: AAA-2 renders only (`RUN.NOT_AAA2` = `c_dyn_ov`, `c_v6`, `p_city_main`, `a_mainline_w3`, `a_sb_hq` are excluded).

## 3. Landmark ratio: 12.2 (no `RC` column; complements R-FOCUS-1)

| Item | Detail |
|---|---|
| Inputs | `beauty.png`, `id.png` (R = class), `capture.json` |
| Metric | `ratio = median luma of pixels with class in {1, 5, 6} / median luma of pixels with class in {0, 2}`, the latter taken **inside the landmark box**. Box = bounding box of the {1, 5, 6} mask, grown by 35 % of its own height (`gy = int((y1 - y0) * 0.35)`) and width (`gx = int((x1 - x0) * 0.35)`) on each side, clipped at 0 (`HV.check`) |
| Class read | `round(R)` compared with the class set (`np.isin(np.round(idx), ...)`) |
| Pass | 1.5 <= ratio <= 2.0 |
| Warn | ratio > 2.0, never a fail (Halcyon 2.9 and Solace 2.8 were accepted) |
| Fail | ratio < 1.5; no per-corp exception (the MAINFRAME 10x exception is withdrawn) |
| Shots | OVERVIEW and DECISION; hover frames exempt |
| Silhouette | a 320 px wide thumbnail written for review (manual, no threshold): `im.resize((320, int(320 * h / w)), LANCZOS)` |
| Other keys `HV` writes | `landmark`, `local_bg`, `landmark_share` (landmark pixels / frame pixels) |
| Reference table | none: `RC` has no 12.2 column. `HV` prints values only and has no pass/fail |
| Edge cases | `HV` raises on an empty {1, 5, 6} mask (`ys.min()`) and omits `ratio` when the background mask is empty. Behavior for a frame with no landmark is not specified (Open O-4) |

## 4. Determinism: 12.3.1 and 12.3.4 (data only; no `RC` row; no art-pass script)

| Check id | Inputs | Metric | Pass | Fail | Source |
|---|---|---|---|---|---|
| 12.3.1 data hash | `derive_<run>.json`, the placement lists and the occlusion params, as canonical JSON bytes (NA02 s1, Ruling O12) | SHA-256 of each file from three runs: twice in one process, once in a fresh process with a different `PYTHONHASHSEED` | all hashes equal | any hash differs | spec 12.3.1; brief acceptance 3 (3 seeds) |
| 12.3.4 seed sensitivity | the same files for a seed pair `(s, s')` | (a) changing `layout_seed` changes the dressing hash; (b) changing only an unrelated building's `bid` changes no other building's placement (per-key streams, spec 3.5 rule 3) | (a) hash differs for 3 of 3 seed pairs; (b) all other buildings' placements byte-equal | otherwise | spec 12.3.4; brief acceptance 4 |

No warn level. Brief acceptance 8: the data suite runs in under 20 s on 3 seeds and the time is reported (a measurement, not a threshold on the record).

## 5. No intersections with rails or viaducts: 12.4 (data part; no `RC` row)

Reference code: `DT` `in_corridor(cfg, x0, y0, x1, y1)`, `corridor_dist(cfg, x, y)`, `corridor_low(cfg, x, y, h)`.
`cfg["corridor"]` is a list of `(ax, ay, bx, by, half)` segments (BU). The spec cites `CAC/zoning.py:353-375` for the
zoning rail; in the pinned commit 306a6865 those lines are the drowned-quarter and arterial (T1) code, so the rail code is
elsewhere in that file (the corridor clearing is near lines 383 and 616). Treat the citation as stale.

| Sub-check | Inputs | Metric | Threshold | Source |
|---|---|---|---|---|
| 12.4.1 footprints | `city.json` building footprints (`parts[].poly`), `zoned.json` corridor segments | any building footprint (inset 0) within `half` of a corridor segment (`in_corridor` samples the segment every 2 BU) | none allowed | spec 12.4.1 |
| 12.4.2 heights | building tops, `deck_z`, `corridor_low` distance | within `corridor_low` distance, every top <= `deck_z - 2` BU, i.e. <= 15.5 BU for `deck_z` 17.5 BU | tops <= 15.5 BU | spec 12.4.2 (AD ruling 2026-10-15, C8); `RAIL.deck_z` 17.5, `RAIL.side_cap` 15.5 in `city_preset.py` 16c427cd |
| 12.4.3 piers | pier positions, street tiles of `city.json` `streets[]` | each viaduct pier stands on a street tile | all piers on street tiles | spec 12.4.3; `RAIL.pier_step` 7.0 |
| 12.4.4 one line | the HQ scene's rail polyline and `deck_z`; `zoned.json`'s | byte equality of the two | equal | spec 12.4.4 (C8) |
| 12.4.5a links | `derive` `edges[].path`, `city.json` volumes | no link path passes through a non-route building volume | none | spec 12.4.5 |
| 12.4.5b openings | `derive` `rooms[].front/back`, `city.json` volumes | no room opening inside another building | none | spec 12.4.5 |
| 12.4.5c foreground | dressing placement lists (stalls, lanterns, poles), room openings | no foreground dressing in front of a room opening | none | spec 12.4.5 (`HQ_rebel_cell/NOTES.md` v2 r2) |

No warn level. Unit of the `corridor_low` distance and of `RAIL.side_d` (1.2): Open O-5.

## 6. Beam style: 12.5.1 and 12.5.3 (data/config only; no `RC` row); 12.5.2 is out of scope

| Check id | Inputs | Metric | Pass | Fail | Source |
|---|---|---|---|---|---|
| 12.5.1 config | the beam/light placement list and preset (spots, shafts) | (a) no media-linked spot with cone < 10 deg; (b) every media-linked spot has blend >= 0.8; (c) no shadowed beam; (d) every beam shaft uses the shaft material | all four hold | any violated | spec 12.5.1 (the beam rules of spec 4.1) |
| 12.5.3 count and spacing | beam placement list, route column `bid`s | beam count <= `beams` (6); pairwise spacing >= 45 BU; no beam on a route column | all hold | any violated | spec 12.5.3; `OC` lines 236-250 (`beams` 6, `> 45` BU, `key in _rk` excluded, sort `(-top, key)`) |

For orientation, the dressing values the config check will see (spec 4.1 beam table): haze spot cone 30 deg, blend 1.0,
no shadow; wash spot cone 70, blend 0.8. `BC` (`beam_check.py`) is a different rule (landmark peak >= 1.5 x local
background, beam peak < landmark peak, beam end in frame) on anchors JSON; it is not a spec 12.5 row.

## 7. Parity: 12.6 (data; no `RC` row; no art-pass script)

| Check id | Inputs | Metric | Pass | Fail | Source |
|---|---|---|---|---|---|
| 12.6 parity | two JSON files (Python and GDScript outputs): `derive_<run>.json`, pose, occlusion | byte-for-byte comparison; report the first differing path (JSON path) | identical bytes (self-compare passes) | any difference (a 1-byte mutation fails) | spec 12.6; brief acceptance 5 |

Floats are compared as text: both sides write rounded 1e-4 canonical JSON (NA02 s1), so there is no numeric tolerance.

Other 12.6 rows exist in the spec but are **not in the NA-04 brief's list** (listed so nothing is silently dropped):

| Row | Rule (spec 12.6) | Reference | Note |
|---|---|---|---|
| Room readability | every room's front projects >= 46 px tall at OVERVIEW 1080p (`room_px_target` 46.0, `RULES` in `sb_onecity.py` c83e3b00) | `derive()` computes `floor_px` | needs a camera pose from `capture.json` |
| Available rooms unblocked | <= 8 % of an available room's opening blocked, opening shrunk 3 px, in DECISION / HOVER | `CO` `LIMIT = 0.08`, `MinFilter(7)` | `CO` reads a Blender semantic colour pass (`_sem.png`), not `id.png` classes; blocked-class mapping to `id.png` is Open O-6 |
| Occlusion never hides | every building opacity >= `ghost`; stub >= min(stub, top) | `DT.occlusion_state` returns `(cut_height, opacity)` | pure data check on the NA-03 occlusion output |
| Frame continuity, wax clear of stickers/UI, 1280 x 720 readability | sequence and UI-overlay checks | `SB/NOTES.md:265-295`, `SB/wax_r2.py:8-9, 28` | need sequences or UI masks; no NA-04 input exists |

## 8. Composition checks: 12.7

Applies to OVERVIEW and DECISION plates (no UI, UI masked). Metrics are `PVC` functions on the 1280-wide working image
(section 1.3). Thresholds are provisional ("derived from hand-built passes", spec 12.7) and live in config `checks.composition`.
`RC` column names equal the check ids. Fail action is **fail** for all (rule names in the last column).

| Check id | `RC` column | Inputs | Metric (`PVC` key, function, line) | Pass | Views (spec) | Rule |
|---|---|---|---|---|---|---|
| R-SIL-1 | R-SIL-1 | `beauty.png` | `lit_std` = std of the lit-mass top profile, frame heights; `skyline(L, rng)` l.213 | >= 0.15 | street | `frontage.silhouette` |
| R-SIL-2 | R-SIL-2 | same | `lit_min_q_std` = minimum std over any 1/4-frame window (step 1/16) | >= 0.08 | street | `frontage.silhouette` |
| R-DET-1 | R-DET-1 | `beauty.png` | `sobel_mean` = mean Sobel magnitude of luma over valid pixels; `sobel_mag` l.99 (`sqrt(gx^2 + gy^2) / 8`) | >= 0.028 | street | `dressing.signs` |
| R-DET-2 | R-DET-2 | same | `blobs_per_mp` = 4-connected components of (luma > `BRIGHT_BLOB` 0.6) on a 2x2-averaged 640-wide image, per valid megapixel at working size; `lights` l.276 | >= 450 | street | `dressing.signs` |
| R-CALM-1 | R-CALM-1 | same | `detail_cv` = std / mean of per-tile mean Sobel, 64 px tiles; tiles with valid share < 0.9 skipped; < 4 tiles gives NaN; `detail_variation` l.333 | 0.45 to 0.85 | street, HQ | `density.falloff` |
| R-CALM-2 | R-CALM-2 | same | `calm_share` = share of tiles below 0.5 x the median tile | 0.12 to 0.32 | street, HQ | `atmosphere.layers` |
| R-HUE-1 | R-HUE-1 | same | `hue_entropy_bits` = entropy of a 36-bin hue histogram weighted by S*V, chromatic pixels only (S > `CHROMA_S` 0.25 and V > `CHROMA_V` 0.15); fewer than 50 such pixels gives NaN; `palette` l.138 | >= 3.8 bits | street, city | `palette.districts`; corp HQ views exempt |
| R-HUE-2 | R-HUE-2 | same | `hue_top_share` = mass of the largest of 6 hue clusters (72-bin smoothed histogram, cluster = peak +- 3 bins) | <= 0.45 | street, city | `palette.districts`; corp HQ views exempt |
| R-FOCUS-1 | R-FOCUS-1 | `beauty.png`, `id.png` | `lm_ratio` = mean luma in the landmark box / mean luma in the ring (box grown by its own width and height on every side, clipped to the frame, box removed, valid pixels only); `landmark` l.252 | >= 1.5 | any frame with a landmark | `landmark.lead` |
| R-HOR-1 | R-HOR-1 | `beauty.png` | `sky_min_q_std` = minimum 1/4-window std of the built-mass-top profile (first rows with 7x7 luma std > 0.022); `skyline` l.213 | >= 0.015 | city | `horizon.break` |
| R-REP-1 | R-REP-1 | same | `rep_p90` = 90th percentile of per-tile autocorrelation peaks: 128 px tiles, stride 64, high-passed luma (`L - box_blur(L, 7)`), lags 4 to 48 px, tiles skipped if valid < 0.95 or std < 0.012; `repetition` l.178 | <= 0.60 | all | `repetition.guard` |
| R-VAL-1/2/3 | R-VAL-1/2/3 | same | see section 2 (12.1) | see section 2 | AAA-2 | `values.solve` |

Skyline detail (`PVC.skyline`, l.213-250), needed to port R-SIL and R-HOR exactly: search range `rng = [y0, y1]` as fractions of the
height (example `CFG` `c_aaa2r3`: `[0.0, 0.85]`); built mask = `box_blur(L*L, 3) - box_blur(L, 3)^2` > 0.022 sqrt-std, smoothed by
`box_blur(., 5)` and thresholded at 0.35; lit mask = `box_blur(L, 6) > percentile(L, 80)` (no run smoothing; the `lit_*` keys feed R-SIL, the built-mass `sky_*` keys feed R-HOR); the profile is the first row from the
top per column, `(span - first) / h`, median-filtered over 13 columns; statistics `std` over the width and the minimum std over windows of `w // 4`
columns stepped by `w // 16`.

R-FOCUS-1 box: the spec says the landmark and crop boxes come from the scene's object-index pass, not hand-placed boxes; on Godot
captures from `id.png` (classes {1, 5, 6}). The reference `RC` values were measured with hand-placed boxes (`CFG` `landmark`), so
`RC` R-FOCUS-1 numbers (e.g. `c_aaa2r3` 1.576, `p_f0340` 1.493) can differ from an `id.png` box on the same image (Open O-7).

Exempt as in 12.1 (hover power cut, mainline frames, red sequence, flash frames). The rules without a test yet (`streets.light`,
`foreground.street`, the depth planes of `atmosphere.layers`, `materials.mix`) report their proxy numbers until their passes exist (not NA-04 checks).

### 8.1 View scopes in the reference (`RUN` lines 58-60, 146-163)

| Rule scope | `RC` rule | Reference selection |
|---|---|---|
| `side` | R-SIL-1/2, R-DET-1/2 | image id in `SIDE_IDS` or config `view == "side"` |
| `netrun` | R-CALM-1/2 | not in `CITY_IDS`, not `a_*`, not `p_tethys` |
| `street_city` | R-HUE-1/2 | `SIDE_IDS` or `CITY_IDS` or config view in (`side`, `street_close`) |
| `aaa2` | R-VAL-1/2/3 | not in `NOT_AAA2` |
| `landmark` | R-FOCUS-1 | the image has an `lm_ratio` (a landmark box configured) |
| `city` | R-HOR-1 | in `CITY_IDS` and a `sky_std` was measured |
| `all` | R-REP-1 | always |

The reference scopes by image id and config. A capture has neither, so the same decision needs `capture.json` fields (Open O-1).

## 9. Reference comparison (brief acceptance 2)

| Item | Fact |
|---|---|
| Reference | `RC` ded9076543a4be175405487a646d0f44346a6bf4: 44 image rows (custom, procedural, anchor), 14 rule columns, each cell PASS / FAIL / n/a with the value |
| Brief wording | "8-row comparison table in the notes", and "100 % of rows". The file has 44 rows; which 8 (or all 44) form the golden set is not stated (Open O-8) |
| Inputs | the `RC` images are paths in `CFG` (e.g. `{C}/route_map_graph/side_view/v3_aaa/r3/plates/AAA2r3_plate.png`); they stay in the art-pass repo and are read from the CLI path, never copied into main |
| Mapping | the 14 `RC` columns map 1:1 to the ids in section 8 (R-SIL-1 .. R-REP-1, R-VAL-1/2/3). Checks 12.1 warn/pass boundary, 12.2, 12.3.x, 12.4, 12.5.x, 12.6 have no `RC` column |
| Blender-only | 12.3.2 (geometry hash), 12.3.3 (image hash), 12.5.2 (beam profile): **out of NA-04 scope** (spec 12.0 table: Blender only in v1). The only image tolerance the spec states is the 12.3.3 GPU-render tolerance (mean abs diff <= 1/255 on a 320 x 180 downsample, max <= 8/255), which belongs to that out-of-scope check |

## 10. Open (what the sources do not give)

| # | Missing | Affects |
|---|---|---|
| O-1 | `capture.json` has no fields for view type (street OVERVIEW / DECISION, HQ, city), look (AAA-2 vs mainline), or the exemption flags (hover power cut, red sequence, flash frame, `look_blend`); the reference scopes by image id (section 8.1). Spec 12.0 lists only pose, resolution, `layout_seed`, run id | 12.1, all 12.7 scopes |
| O-2 | How `n/a` is recorded (status value) and how a NaN metric maps to a record | all |
| O-3 | Comparison mode for acceptance 2: `RC` uses R-VAL-1 band 0.12-0.17 with no warn; spec 12.1 uses 0.11-0.17 with warn bands. The orchestrator must rule whether the reference run uses the `RC` band (and how warn is compared) | 12.1, acceptance 2 |
| O-4 | Behavior of 12.2 / R-FOCUS-1 when the frame has no landmark pixels or an empty background mask | 12.2, R-FOCUS-1 |
| O-5 | Unit of the `corridor_low` distance and `RAIL.side_d` (1.2 in `city_preset.py`, lots; the check needs BU); the `corridor_low` tuple fields beyond `(dist, hmax)` | 12.4.2 |
| O-6 | How `check_occlusion.py`'s blocked classes (semantic colours 0.1, 0.6, 0.85, 0.95, 0.2 and 0.3/0.5 with a layer colour) map to `id.png` classes {0, 1, 2, 5, 6} | 12.6 rooms unblocked |
| O-7 | The skyline search range `rng` and the facade band for R-REP-1 are per-image config in `CFG` (example `[0.0, 0.85]`, `[0.0, 0.10, 1.0, 0.80]`); no default for captures. And R-FOCUS-1 boxes: `id.png` bbox vs the hand-placed `CFG` boxes behind the `RC` values | R-SIL, R-HOR, R-REP-1, R-FOCUS-1 |
| O-8 | Which `RC` rows form the golden comparison set (the brief says 8 rows and 100 %; the file has 44) | acceptance 2 |
| O-9 | Tolerances between a Blender PNG and a Godot capture of the same scene (brief acceptance 6 says "stated tolerances, none hard-coded"); the spec states none for the 12.1 / 12.7 metrics | image checks |
| O-10 | The config key `checks.composition` file and its schema (spec 12.7 says the thresholds live there) | 12.7 |
| O-11 | The 12.5.1 input file: no NA-02 schema for the beam/light placement list or preset (NA-03 Open O-I) | 12.5.1, 12.5.3, 12.4.5c |
| O-12 | The ground-truth pier positions and the HQ scene's rail polyline for 12.4.3 and 12.4.4: no NA-02 schema (`zoned.json`, NA-03 Open O-C) | 12.4 |

## Build-session rulings (2026-10-18)
- **O-3 (art-pass 2026-10-18):** one mode. Spec 12.1 is normative (Designer 2026-10-16 Q4): pass 0.11-0.17, warn
  0.09-0.11 and 0.17-0.19, fail outside; `rules_check.md`'s 0.12-0.17 is superseded. Acceptance 2 compares all rows;
  the rows whose R-VAL-1 verdict changes only because of the band are listed as expected differences.
- **O-8:** acceptance 2 compares all 44 `rules_check.md` rows on every column NA-04 implements; the "8-row" table in
  the brief means one summary row per check id (rows compared / matched).
- **O-A:** numpy and Pillow allowed (see NA03_MODULES rulings).
- **Art-pass to answer (sent 2026-10-18):** O-1 (`capture.json` view / look / exemption fields), O-4, O-5, O-6, O-7,
  O-9, O-10, and the stale `CAC/zoning.py:353-375` rail citation. NA-04 implements everything else first.
- **Art-pass answers (2026-10-18):** `NA03_NA04_ANSWERS.md` (art-pass 88a76010) answers O-1, O-4 (new status `n/a`,
  exit 0), O-5, O-6 (id.png v1 additions: class 3 = link structure; on class 5, G = room index, B = layer: the W1
  Godot ID-capture slice emits them), O-7, O-9 (provisional tolerances), O-10, and the rail citation. They win here.
