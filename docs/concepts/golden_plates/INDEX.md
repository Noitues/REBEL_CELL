# Golden plates (PIPELINE_SPEC 12.8), built from existing renders

Built 2026-10-18 on branch `art-pass` with `scripts/build_all.py` (manifest) and `scripts/make_plate.py` (writer). CPU only. The Tethys, street, city and Aurelian index passes are Blender / Cycles renders kept in D:/rc_scratch (see "ID re-render batch").
Four files per plate: `<stem>.png`, `<stem>_id.png`, `<stem>_capture.json`, `<stem>_values.json`.
18 of 18 plates written, all with an `_id.png`. Re-run: `python scripts/build_all.py` (needs `D:/rc_scratch/` for the index passes and street poses).

## Table

"Art-pass commit" is the last commit that touched the source final. "id" = `_id.png` written from a saved Object Index pass.
Value status lists the checks that are not `pass` (values are in `<stem>_values.json`; 12.1 bands, 12.2 ratio band, 12.7 provisional thresholds).

| Stem | Source final | Art-pass commit | id | Value status (median / under 0.10 / over 0.85 / ratio_median) | Needs later |
|---|---|---|---|---|---|
| `hq_halcyon_overview` | `route_map_graph/hq_halcyon/plates/H_overview_v2_plate.png` | 46d161ce | yes | 0.109 / 46.3 % / 0.2 % / 3.19. R-VAL-1 warn (pre-accepted, Q4 plate). R-VAL-2 fail (46 % over the 25-40 % band). Ratio warn (>2.0), not pre-accepted. R-CALM-1/2 fail | derive inputs, layout seed, run graph |
| `hq_halcyon_decision` | `.../hq_halcyon/plates/H_decision_E_v2_plate.png` (variant E) | 46d161ce | yes | 0.166 / 31.7 % / 0.3 % / 2.67. Ratio warn. R-CALM-1/2 and R-REP-1 fail | same |
| `hq_solace_overview` | `.../hq_solace/plates/H_overview_v4_plate.png` | 1827e4ac | yes | 0.127 / 37.4 % / 0.7 % / 2.56. Ratio warn (pre-accepted). R-CALM-1/2 fail | same |
| `hq_solace_decision` | `.../hq_solace/plates/H_decision_v4_plate.png` | 1827e4ac | yes | 0.121 / 34.9 % / 2.1 % / 2.57. Ratio warn (pre-accepted). R-CALM-1/2 fail | same |
| `hq_orbital_overview` | `.../hq_orbital/plates/H_overview_v2_plate.png` | 46d161ce | yes | 0.118 / 40.9 % / 1.1 % / 3.85. R-VAL-2 fail (40.9 %), ratio warn, R-CALM-1/2 fail | same; Halcyon and Orbital also predate the occlusion rule (handoff queue 5) |
| `hq_orbital_decision` | `.../hq_orbital/plates/H_decision_v2_plate.png` | 46d161ce | yes | 0.122 / 41.3 % / 2.7 % / 3.44. R-VAL-2 fail, R-VAL-3 fail (2.71 % over 0.85), ratio warn, R-FOCUS-1 fail | same |
| `hq_meridian_overview` | `.../hq_meridian_v3/plates/H_overview_v3_plate.png` | 5c97940f | yes | 0.139 / 35.9 % / 1.8 % / 2.51. Ratio warn. R-CALM-1/2 fail | same |
| `hq_meridian_decision` | `.../hq_meridian_v3/plates/H_decision_v3_plate.png` | 5c97940f | yes | 0.175 / 25.3 % / 2.8 % / **1.06**. R-VAL-1 warn (known, handoff 3), R-VAL-3 fail, **ratio fail (below 1.5)**, R-FOCUS-1 fail, R-REP-1 fail | same |
| `hq_rebel_cell_overview` | `.../hq_rebel_cell/plates/H_overview_v3_plate.png` | 6d3a5658 | yes | 0.121 / 42.3 % / 1.9 % / **1.18**. R-VAL-2 fail, ratio fail. R-FOCUS-1 n/a (box fills the frame, empty ring) | same |
| `hq_rebel_cell_decision` | `.../hq_rebel_cell/plates/H_decision_v3_plate.png` | 6d3a5658 | yes | 0.145 / 35.3 % / 2.4 % / **1.40**. Ratio fail. R-FOCUS-1 n/a | same |
| `hq_tethys_overview` | `.../hq_tethys/H_overview_v2_plate.png` | 3092f4a6 | yes | 0.140 / 31.0 % / 0.09 % / 1.81. Ratio pass (peak 5.91 and mean 1.99 from id classes; the earlier disc-mask 3.72 / 1.88 are superseded). R-FOCUS-1 fail (new, baseline). R-CALM-1/2 fail (report only) | derive inputs, layout seed, run graph; camera tgt is a fit (note 2) |
| `hq_tethys_decision` | `.../hq_tethys/H_decision_v2_plate.png` | fd462c07 | yes | 0.140 / 29.3 % / 0.23 % / 2.02. Ratio warn (2.02, just above 2.0, not pre-accepted; peak 6.56, mean 2.17). R-FOCUS-1 fail (new, baseline). R-CALM-1 fail (report only) | same; camera is exact |
| `street_overview` | `.../street_r2/plates/01_OVERVIEW_closed_s1_plate.png` | W1 re-render (art seed 1, 40 spp)| yes | yes| 0.130 / 29.9 % / 0.5 % / 1.67 (route rooms vs city). All pass (R-REP-1 0.409, R-DET-2 676). Alignment 1.01. Route never occluded: 0 blobs.|
| `street_decision` | `.../street_r2/plates/02_DECISION_closed_s1_plate.png` | W1 re-render (art seed 1, 40 spp)| yes | 0.141 / 31.9 % / 1.1 % / 1.76 (rooms vs city). R-DET-2 fail (blobs), R-REP-1 fail (known, handoff 3). Alignment 0.94 by the variance test, but the overlay shows the pass on the plate (noisy index, flat night street) | 0.141 / 32.7 % / 1.0 % / 1.70. All pass (W1: R-DET-2 459, R-REP-1 0.589 on the facade band, AD 2026-10-18). Route never occluded: 0 blobs. Alignment 0.76|
| `city_a2_night` | `city_all_corps/city_all_corps_night.png` | 199a450e | yes | 0.155 / 27.6 % / 0.9 % / 2.80 (landmark 65.6 k px of 8.3 M). Ratio warn (>2.0, not pre-accepted). R-FOCUS-1 1.77 pass (id.png box). R-HUE-1/2 fail (city night is one hue family) | camera is partial (note 4) |
| `city_a2_day` | `city_all_corps/city_all_corps_day.png` | 199a450e | yes | 0.250 / 8.3 % / 0.06 % / **1.20**. Capture `time: "day"` (12.8): R-VAL-1/2/3, landmark ratio 1.20 and R-FOCUS-1 0.93 are **report only** (never fail, never baseline; band verdicts in the notes; AD to set a day band). R-HUE-1/2 fail (baseline). Alignment 0.15 by the variance test (flat daylight); overlay checked by eye, the pass sits on the plate | same camera |
| `hq_aurelian_overview` | `.../hq_aurelian/plates/H_overview_v2_plate.png` | untracked (v2 finals, AD round 3, 2026-10-18) | yes | 0.152 / 38.1 % / 0.8 % / 2.46. Ratio warn, accepted as for v1 (AD 2026-10-18). Every other check pass. No baseline fails | derive inputs, layout seed, run graph |
| `hq_aurelian_decision` | `.../hq_aurelian/plates/H_decision_v2_plate.png` (an outer-arcade room, v2 + face band, 2026-10-18) | untracked (v2 finals) | yes | 0.153 / 36.0 % / 0.5 % / 2.79. Ratio warn, accepted as for v1. No baseline fails | same |

## Missing, by reason

- **Nothing missing from the set: 18 plates, 18 id passes.** Aurelian was built from the `_v1` finals (c8f41aa6) and their 2560 x 1440 index passes in `D:/rc_scratch/aurelian/big/bl_stills/` (same final run and timestamps as the beauty npy).
- **Cameras:** complete for the 12 HQ plates, Tethys and street. City is partial (note 4).
- **All plates:** `layout_seed`, `run`, `anim_t`, `art_seeds`, the fixture `run_graph.json` and the five `inputs` hashes are `null`. No derive run exists for any of these renders (they predate derive v2), so the 12.8 rule 3 and 4 fields cannot be filled without inventing them. They are listed in each capture's `pending`.

## ID re-render batch (done 2026-10-18)

The three Blender pipelines now write an Object Index pass by class, same mapping and export as `hq_scene.py` (0 sky, 1 landmark compound, 2 city, 4 ground, 5 rooms, 6 movers, 7 light streaks; `<name>_index.npy`, float32, first channel):
- `city_all_corps/scripts/city_idpass.py` (new) carves the landmark faces (and the Tethys wildlife) out of the merged accumulators into their own objects. That only moves faces between objects (geometry and materials are unchanged, so the beauty is too) and sets `pass_index`. `city_render.py` calls it, `landmarks.py` records the face-count mark before the landmark loop, `use_pass_object_index` is on and `Object Index` is exported.
- `hq_tethys/scripts/tethys_build.py`: same, patched into the render source at run time (`city_base` stays untouched); marks before the landmark loop (class 1) and before the wildlife (whales and shoals, class 6).
- `street_r2/scripts/r2_scene.py` (`_idpass`) and `r2_cycles.py`: by object (HQs, Cell base and megastructure 1; city, signs and lamps 2; route rooms and walls 5; HQ movers 6; ground 4; traffic lanes, beams and plumes 7). `r2_jobs.py` honours `R2_OUT` so the finals are not overwritten.

Renders (same seeds, cameras, spp and resolution as the finals; Cycles HIP, GPU lock taken and released per batch): Tethys `t_over@2.0` and `t_dec` at 40 spp (6 min), street `ov_closed` and `dec_closed`, seed 1, 40 spp (5.5 and 7 min), city night and day hero at 80 spp (6.2 and 4 min). Beauty check against the finals (median of the rgb / combined pass, new vs old): Tethys overview 0.0974 / 0.0966, decision 0.1120 / 0.1124; street 0.0515 / 0.0515 and 0.0836 / 0.0836; city night 0.0286 / 0.0287, day 0.1156 / 0.1156. Not bit-identical on the GPU (denoise, adaptive sampling) but the same picture, so this is an ID add and not a re-bake. Passes are in `D:/rc_scratch/tethys/idpass/`, `D:/rc_scratch/idpass/street/` and `D:/rc_scratch/city_all_corps/idpass/` (not committed). Class-map overlays on the plates were checked by eye at 1280 px for both Tethys views, street decision and city day.

Read-outs: in Tethys the drowned quarter shows as class 2 through the water (the water surface is transparent to the pass). The street ratio compares route rooms (class 5) with the city, because the street frame holds no HQ; the old "no landmark expected" n/a is gone.

## Notes

1. **Index pass to class map.** Passes come from `hq_scene.py` (`Acc(..., pass_index, ...)`): 0 sky, 1 compound, 2 city, 4 ground, 5 rooms, 6 movers, 7 light streaks. Mapped: 3 and 7 to class 4, rest identity. Pass 3 is not link structure in these renders: Solace uses it for the plaza apron ring, Rebel Cell for the MAINFRAME sign quad. Mapping both to 4 keeps the 12.2 masks ({1,5,6} / {0,2}) identical to `hq_values.py`; checked on Solace v4 (2.555 / 2.573, same as the 2026-10-16 `values_final_v4.json`). Class 3 therefore never appears in these plates. Rebel Cell is the exception: AD ruling maps its pass 3 to class 1 (note 3). G and B are 0 everywhere (the HQ passes carry no room ids). The raw pass is speckled with class 0 and 2 holes inside buildings (Cycles unfiltered index); it is kept as saved, nearest-sampled. Alignment of each pass to its plate is recorded in `checks.notes.id_alignment` (variance share explained by the classes, divided by the same with the classes shifted 25-40 px; 1.17-3.58 on the 10 HQ plates, Halcyon the weakest because its plate was post-processed 26 min after the pass; 1.13-2.34 on Aurelian, Tethys, street overview and city night; below 1 on street decision, 0.94, and city day, 0.15, where flat lighting gives the test little variance to explain: both checked by overlay).
2. **Tethys cameras.** Decision: exact from `tethys_preset.CAMS["t_dec"]` (matches the render log). Overview: the preset gives `target_ab`, which needs the zoning frame, so `tgt` (-328.75, 275.25) is fitted to the 28 room anchors of `D:/rc_scratch/tethys/final4/t_over_aaa_rooms.json` (mean error 0.8 px, +-0.25 BU; render log says (-329, 275)). Yaw is converted layout to rig (`rig = 90 - layout`).
3. **Rebel Cell sources** are committed in 6d3a5658 (v3 plates and `ov_stills.json`); that is the cited source commit. Pass 3 (the MAINFRAME sign) is mapped to class 1 for Rebel Cell (AD ruling, a5e11c38); the Rebel overview ratio moved 1.17 to 1.18 and still fails.
4. **City camera (AD ruling: keep the perspective hero camera).** The plate is the perspective A2 hero frame: lens 28, pitch 33, dist 1130, rig yaw 0 (looking north), loc (12, -960, 615) and tgt (12, -12, 0) from the render log (rounded to 1 BU). 12.8 asks for the orthographic mainline camera (yaw 135, pitch 40, lot 6 BU) for these two plates. The art does not use it. Ruled: the hero camera stays.
5. **Street cameras** come from the render job (`loc`, `tgt`, `lens`, `sx`, `sy`); yaw / pitch / dist are derived. The plates are 1920 x 1080, not 2560 x 1440. Poses use the rig yaw convention (0 north, clockwise), checked against each job's own yaw to 0.3 deg for every HQ plate.
6. **`look`** is `aaa2` for HQ, street and city night, null for city day (no enum value for it). `kind / view / corp` as in 12.8; city plates use `view: "city"`.
7. **Baseline (AD ruling, a5e11c38).** The plates are the finals as they are. Each `values.json` lists the checks the plate already fails in `checks.baseline`; R-CALM-1/2 on HQ views are `checks.report_only` and not in the baseline. **Pre-accepted warns** are recorded under `checks.pre_accepted`: Halcyon overview median 0.109, Solace ratio 2.56, Tethys overview ratio peak (moot now: the id ratio is 1.81), Aurelian ratios 2.52 and 2.26 (accepted like Solace, AD 2026-10-18). Everything else in the "not pass" column is new against 12.8 and for the AD, notably Meridian decision (ratio 1.06, over 0.85 at 2.8 %), Orbital (under 0.10 at 41 %, decision over 0.85 at 2.7 %), Rebel Cell (ratio 1.17 and 1.40), Halcyon overview (46 % under 0.10), and R-CALM-1/2 on nearly every HQ plate.
8. **Landmark ratios.** `ratio_median` is the gated 12.2 measure. `ratio_mean` = mean(landmark) / median(background), `ratio_peak` = p99(landmark) / median(background), the same convention `post_tethys.py` uses. `hq_values.py` itself writes only the median ratio.

## Art items from baseline fails

Recorded in each plate as `checks.baseline`; each is an art item, not a plate defect.
- **Meridian decision:** landmark ratio 1.06 (needs 1.5-2.0), R-FOCUS-1 fail, over 0.85 at 2.8 %, R-REP-1 fail.
- **Orbital overview:** under 0.10 at 40.9 % (band 25-40 %). **Orbital decision:** under 0.10 at 41.3 %, over 0.85 at 2.7 %, R-FOCUS-1 fail.
- **Halcyon overview:** under 0.10 at 46.3 % (median 0.109 is the pre-accepted warn). **Halcyon decision:** R-REP-1 fail.
- **Rebel Cell:** ratio still fails after the pass 3 mapping: overview 1.18 (also under 0.10 at 42.3 %), decision 1.40.
- **Street decision:** none (W1: R-DET-2 and R-REP-1 pass).
- **City night and day:** R-HUE-1/2 (one hue family), baseline. Night landmark ratio 2.80 warn; night R-FOCUS-1 1.77 pass. By day (`time: "day"`) the value band, landmark ratio (1.20) and R-FOCUS-1 (0.93) are report only (12.8, AD 2026-10-18).
- **Tethys:** R-FOCUS-1 fail on both views (new with the id pass); decision ratio 2.02 warn.
- **Aurelian (v2, 2026-10-18):** no baseline fails; ratios 2.46 and 2.79 are warns (accepted as for v1).
- **Look bias:** see `look_bias_check.jpg`: the derive sign (+sgn x 0.10) is the right one; the 6.2 table row and the `cam_rig.py:34` comment need the edit.
