# Golden plates (PIPELINE_SPEC 12.8), built from existing renders

Built 2026-10-18 on branch `art-pass` with `scripts/build_all.py` (manifest) and `scripts/make_plate.py` (writer). CPU only, no Blender, no GPU.
Four files per plate: `<stem>.png`, `<stem>_id.png`, `<stem>_capture.json`, `<stem>_values.json`. Plates with no id pass have no `_id.png`.
16 of 18 plates written; the 2 Aurelian plates are pending. Re-run: `python scripts/build_all.py` (needs `D:/rc_scratch/` for the index passes and street poses).

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
| `hq_tethys_overview` | `.../hq_tethys/H_overview_v2_plate.png` | 3092f4a6 | **no** | 0.140 / 31.0 % / 0.09 % / ratio_median null. ratio_peak 3.72 and ratio_mean 1.88 copied from the Tethys post tool (disc mask, not id classes): warn pre-accepted. R-CALM-1/2 fail | **ID re-render** (Tethys writes rgb/emit/z only); camera tgt is a fit (note 2) |
| `hq_tethys_decision` | `.../hq_tethys/H_decision_v2_plate.png` | fd462c07 | **no** | 0.140 / 29.3 % / 0.2 % / null. ratio_peak 3.10, ratio_mean 1.57 (disc mask). R-CALM-1 fail | **ID re-render**; camera is exact |
| `street_overview` | `.../street_r2/plates/01_OVERVIEW_closed_s1_plate.png` | ded90765 | **no** | 0.136 / 26.9 % / 0.5 % / n/a. All pass (R-SIL, R-DET, R-CALM, R-HUE, R-REP) | **ID re-render** (street_r2 writes albedo/emit/z/combined); plate is 1920 x 1080; layout_seed (art seed 1 only), run graph |
| `street_decision` | `.../street_r2/plates/02_DECISION_closed_s1_plate.png` | ded90765 | **no** | 0.141 / 31.9 % / 1.1 % / n/a. R-DET-2 fail (blobs), R-REP-1 fail (known, handoff 3) | same |
| `city_a2_night` | `city_all_corps/city_all_corps_night.png` | 199a450e | **no** | 0.155 / 27.6 % / 0.9 % / null. R-HUE-1/2 fail (city night is one hue family) | **ID re-render**; camera is partial (note 4) |
| `city_a2_day` | `city_all_corps/city_all_corps_day.png` | 199a450e | **no** | 0.250 / 8.3 % / 0.06 % / null. R-VAL checks n/a (day band is reported only, 12.8). R-HUE-1/2 fail | **ID re-render**; same camera |
| `hq_aurelian_overview` | none | pending | no | pending | no `_v1` finals exist (only Eevee / Cycles test rounds, 1280 x 720); build after the Aurelian finals |
| `hq_aurelian_decision` | none | pending | no | pending | same |

## Missing, by reason

- **Aurelian (2 plates): pending.** `hq_aurelian/` has DESIGN.md, test sheets and scratch test renders only. Its 1280 x 720 test index passes exist in `D:/rc_scratch/aurelian/big/bl_stills_test/`, but a test render is not a plate.
- **No Object Index pass, so no `_id.png` (6 plates).** Tethys overview and decision (the Tethys pipeline writes rgb/emit/z only), street overview and decision (`street_r2` writes albedo/emit/z/combined), city night and day (rgb/emit/z). For these `ratio_median`, `ratio_mean`, `ratio_peak` are null with `n/a` (street: no landmark expected; city and Tethys: id missing) and R-FOCUS-1 is `n/a`. Tethys carries its own disc-mask ratio_mean / ratio_peak, labelled in `checks.notes`.
- **Cameras:** complete for the 10 HQ plates, Tethys and street. City is partial (note 4).
- **All plates:** `layout_seed`, `run`, `anim_t`, `art_seeds`, the fixture `run_graph.json` and the five `inputs` hashes are `null`. No derive run exists for any of these renders (they predate derive v2), so the 12.8 rule 3 and 4 fields cannot be filled without inventing them. They are listed in each capture's `pending`.

## Notes

1. **Index pass to class map.** Passes come from `hq_scene.py` (`Acc(..., pass_index, ...)`): 0 sky, 1 compound, 2 city, 4 ground, 5 rooms, 6 movers, 7 light streaks. Mapped: 3 and 7 to class 4, rest identity. Pass 3 is not link structure in these renders: Solace uses it for the plaza apron ring, Rebel Cell for the MAINFRAME sign quad. Mapping both to 4 keeps the 12.2 masks ({1,5,6} / {0,2}) identical to `hq_values.py`; checked on Solace v4 (2.555 / 2.573, same as the 2026-10-16 `values_final_v4.json`). Class 3 therefore never appears in these plates. Rebel Cell is the exception: AD ruling maps its pass 3 to class 1 (note 3). G and B are 0 everywhere (the HQ passes carry no room ids). The raw pass is speckled with class 0 and 2 holes inside buildings (Cycles unfiltered index); it is kept as saved, nearest-sampled. Alignment of each pass to its plate is recorded in `checks.notes.id_alignment` (variance share explained by the classes, divided by the same with the classes shifted 25-40 px; 1.17-3.58 on all 10, Halcyon the weakest because its plate was post-processed 26 min after the pass).
2. **Tethys cameras.** Decision: exact from `tethys_preset.CAMS["t_dec"]` (matches the render log). Overview: the preset gives `target_ab`, which needs the zoning frame, so `tgt` (-328.75, 275.25) is fitted to the 28 room anchors of `D:/rc_scratch/tethys/final4/t_over_aaa_rooms.json` (mean error 0.8 px, +-0.25 BU; render log says (-329, 275)). Yaw is converted layout to rig (`rig = 90 - layout`).
3. **Rebel Cell sources** are committed in 6d3a5658 (v3 plates and `ov_stills.json`); that is the cited source commit. Pass 3 (the MAINFRAME sign) is mapped to class 1 for Rebel Cell (AD ruling, a5e11c38); the Rebel overview ratio moved 1.17 to 1.18 and still fails.
4. **City camera (AD ruling: keep the perspective hero camera).** The plate is the perspective A2 hero frame: lens 28, pitch 33, dist 1130, rig yaw 0 (looking north), loc (12, -960, 615) and tgt (12, -12, 0) from the render log (rounded to 1 BU). 12.8 asks for the orthographic mainline camera (yaw 135, pitch 40, lot 6 BU) for these two plates. The art does not use it. Ruled: the hero camera stays.
5. **Street cameras** come from the render job (`loc`, `tgt`, `lens`, `sx`, `sy`); yaw / pitch / dist are derived. The plates are 1920 x 1080, not 2560 x 1440. Poses use the rig yaw convention (0 north, clockwise), checked against each job's own yaw to 0.3 deg for every HQ plate.
6. **`look`** is `aaa2` for HQ, street and city night, null for city day (no enum value for it). `kind / view / corp` as in 12.8; city plates use `view: "city"`.
7. **Baseline (AD ruling, a5e11c38).** The plates are the finals as they are. Each `values.json` lists the checks the plate already fails in `checks.baseline`; R-CALM-1/2 on HQ views are `checks.report_only` and not in the baseline. **Pre-accepted warns** are recorded under `checks.pre_accepted`: Halcyon overview median 0.109, Solace ratio 2.56, Tethys overview ratio peak. Everything else in the "not pass" column is new against 12.8 and for the AD, notably Meridian decision (ratio 1.06, over 0.85 at 2.8 %), Orbital (under 0.10 at 41 %, decision over 0.85 at 2.7 %), Rebel Cell (ratio 1.17 and 1.40), Halcyon overview (46 % under 0.10), and R-CALM-1/2 on nearly every HQ plate.
8. **Landmark ratios.** `ratio_median` is the gated 12.2 measure. `ratio_mean` = mean(landmark) / median(background), `ratio_peak` = p99(landmark) / median(background), the same convention `post_tethys.py` uses. `hq_values.py` itself writes only the median ratio.

## Art items from baseline fails

Recorded in each plate as `checks.baseline`; each is an art item, not a plate defect.
- **Meridian decision:** landmark ratio 1.06 (needs 1.5-2.0), R-FOCUS-1 fail, over 0.85 at 2.8 %, R-REP-1 fail.
- **Orbital overview:** under 0.10 at 40.9 % (band 25-40 %). **Orbital decision:** under 0.10 at 41.3 %, over 0.85 at 2.7 %, R-FOCUS-1 fail.
- **Halcyon overview:** under 0.10 at 46.3 % (median 0.109 is the pre-accepted warn). **Halcyon decision:** R-REP-1 fail.
- **Rebel Cell:** ratio still fails after the pass 3 mapping: overview 1.18 (also under 0.10 at 42.3 %), decision 1.40.
- **Street decision:** R-DET-2 (bright blobs per MP) and R-REP-1.
- **City night and day:** R-HUE-1/2 (one hue family), baseline.

## Queued Blender batch: 6 ID re-renders (Tethys x2, street x2, city x2)

None of the three job scripts writes an Object Index pass today (no `use_pass_object_index` or `pass_index` in `city_render.py`, `r2_scene.py`, `tethys_build.py`). Patch each first so every object gets `pass_index` by class (0 sky, 1 landmark compound, 2 city, 4 ground, 5 rooms, 6 movers), enable `view_layer.use_pass_object_index` and export the pass as `<name>_index.npy` the way `hq_scene.py` does (`exr_to_npy` "Object Index"). Then run, one GPU-queue batch, same seeds and cameras so the beauty matches the plate:

```
# Tethys overview + decision (index only; beauty already final)
python docs/concepts/route_map_graph/hq_tethys/scripts/run_tethys.py aaa t_over,t_dec 1.0 40 idpass
# street overview + decision, art seed 1, walls closed
python docs/concepts/route_map_graph/street_r2/scripts/r2_jobs.py finals 1 ov_closed dec_closed
# city night + day (A2 hero, 80 spp)
python docs/concepts/city_all_corps/scripts/run_jobs.py aaa hero 1.0 80 idpass
python docs/concepts/city_all_corps/scripts/run_jobs.py day hero 1.0 80 idpass
```

Then run `python scripts/make_plate.py` through `build_all.py` with the new `index` paths (set `index` in the Tethys, street and city entries). Check the beauty is unchanged first (same median); if the geometry changed, it is a re-bake, not an ID add.
