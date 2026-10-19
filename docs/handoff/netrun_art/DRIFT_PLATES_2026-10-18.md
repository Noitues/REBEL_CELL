# Drift compare against the 18 golden plates (NA-04b, refreshed W1 NA-04c, re-run W1 LAMPSHIFT on the re-baked street plates, 2026-10-18)

Drift compare of our image checks (`tools/netrun_art/checks`) against the golden plates of art-pass `ed8675a8` (street plates re-baked; the street baselines are now empty) (PIPELINE_SPEC 12.8), read-only: the plates were read with `git show` from the art-pass repo and extracted to a scratch folder; no image was copied into the repo. Command, from `tools`:

    python -m netrun_art.checks.drift <plates dir> --work <scratch dir> --out <file>

Method: each plate's `<stem>.png`, `<stem>_id.png`, `<stem>_capture.json` is run through `check_capture_folder` (12.1, 12.2, 12.7, 12.6 route) and each image value is compared with the plate's `values.json` inside `checks.tolerance.renderer` (median 0.02, under 0.10 0.05, over 0.85 0.01, landmark ratio 0.15, calm share 0.04, hue entropy 0.2, hue top share 0.05, everything else 10 % relative). The derive fields of every plate are null (concept renders), so only image values are compared. `our status` is the status our check gives the value; `[baseline]` marks a check the plate already fails (reported, not a capture failure); `[baseline (theirs)]` a plate baseline item our check does not score (out of scope or report only); `[pre-accepted]` a config pre-accepted warn.

## Result

- 18 plates, 1 DRIFT row (street_decision R-REP-1, see below); the other 17 plates are 0 DRIFT. Deltas are 0 to rounding, except R-FOCUS-1 (up to 0.0042, nearest resample of the id box). The plates' values were written by the same metric code, so this is a regression anchor for the renderer comparison; the first Godot capture of a plate is the first real delta.
- Day/night (AD answers 2026-10-18, spec 12.0 / 12.7): `capture.json` `time` is `"night"` (default) or `"day"`. A day frame makes the 12.1 value band (R-VAL-1/2/3), the 12.2 landmark ratio and R-FOCUS-1 report only: status n/a, value kept. The earlier kind/look heuristic is gone. The concept plates' `capture.json` lacks `time`, so for them (and only when `time` is absent) the stem is looked up in `landmark_ratio.day_stems` (`city_a2_day`). Result: `city_a2_day` R-VAL-1/2/3 (0.2501 / 0.0834 / 0.0006), ratio 1.1977 and R-FOCUS-1 are n/a with values kept; `city_a2_night` passes R-FOCUS-1 at 1.7756.
- Tethys decision 2.0242 and city night 2.7990 are warns, tagged pre-accepted from config (`landmark_ratio.pre_accepted`). HQ Tethys overview ratio 1.8067 passes with the id mask.
- 12.6 route never occluded: n/a on all 18 plates (HQ and street plates have G = 0 everywhere; city plates have no route rooms). The check now also excludes occlusion stubs (class 2 with G = 255 and B = 0, written for a cut or ghosted building) besides the route-column cut surface (class 2 with B > 0); it first runs on Godot captures.
- Honored baseline fails (`[baseline]` rows): Halcyon overview R-VAL-2, Halcyon decision R-REP-1, Meridian decision R-VAL-3 / ratio 1.06 / R-FOCUS-1 / R-REP-1, Orbital R-VAL-2 / R-VAL-3 / R-FOCUS-1, Rebel Cell ratio 1.40 / 1.18 and overview R-VAL-2, Tethys R-FOCUS-1, city R-HUE-1/2 (the street plates no longer carry a baseline). None is a capture failure.
- art-pass to fix in `values.json` (their side, later): (1) the `city_a2_day` baseline still lists `landmark_ratio`, which is report only by day (stale). (2) `city_a2_night` and `street_decision` have R-FOCUS-1 null in `values.json` while we score it (city_a2_night 1.7756 pass; street_decision 1.1087 fail on the re-baked plate); art-pass to fill it, not a drift.

- LAMPSHIFT (kerb lamps shifted, not dropped; dress fixtures regenerated) does not touch the image checks: the plates are read-only art-pass renders, so the street rows below depend only on the re-baked plates.
- DRIFT, street_decision R-REP-1: ours 0.7850, theirs 0.5885 (delta 0.1965, tol 0.0785, our status fail, their status pass). The values.json R-REP-1 was written by art-pass metric code, so this is a real difference between our R-REP-1 and theirs on the re-baked plate, not a rounding. Not fixed here (a metric/design call): open question for the owner of `checks/image_checks.py` R-REP-1 vs art-pass. R-FOCUS-1 is null in their values.json for street_decision and we score it 1.1087 (fail); art-pass to fill it.

## Summary

| plate | ok | DRIFT | n/a |
|---|---|---|---|
| city_a2_day | 8 | 0 | 0 |
| city_a2_night | 8 | 0 | 1 |
| hq_aurelian_decision | 8 | 0 | 0 |
| hq_aurelian_overview | 8 | 0 | 0 |
| hq_halcyon_decision | 8 | 0 | 0 |
| hq_halcyon_overview | 8 | 0 | 0 |
| hq_meridian_decision | 8 | 0 | 0 |
| hq_meridian_overview | 8 | 0 | 0 |
| hq_orbital_decision | 8 | 0 | 0 |
| hq_orbital_overview | 8 | 0 | 0 |
| hq_rebel_cell_decision | 7 | 0 | 0 |
| hq_rebel_cell_overview | 7 | 0 | 0 |
| hq_solace_decision | 8 | 0 | 0 |
| hq_solace_overview | 8 | 0 | 0 |
| hq_tethys_decision | 8 | 0 | 0 |
| hq_tethys_overview | 8 | 0 | 0 |
| street_decision | 10 | 1 | 1 |
| street_overview | 13 | 0 | 0 |

## Rows

| plate | check | ours | theirs | delta | tol | our status | verdict |
|---|---|---|---|---|---|---|---|
| city_a2_day | R-VAL-1 | 0.2501 | 0.2501 | 0.0000 | 0.0200 | n/a | ok [report-only] |
| city_a2_day | R-VAL-2 | 0.0834 | 0.0834 | 0.0000 | 0.0500 | n/a | ok [report-only] |
| city_a2_day | R-VAL-3 | 0.0006 | 0.0006 | 0.0000 | 0.0100 | n/a | ok [report-only] |
| city_a2_day | 12.2 ratio | 1.1977 | 1.1977 | 0.0000 | 0.1500 | n/a | ok [baseline (theirs), report-only] |
| city_a2_day | R-HOR-1 | 0.0397 | 0.0397 | 0.0000 | 0.0040 | pass | ok |
| city_a2_day | R-HUE-1 | 2.8440 | 2.8440 | 0.0000 | 0.2000 | fail | ok [baseline] |
| city_a2_day | R-HUE-2 | 0.6410 | 0.6410 | 0.0000 | 0.0500 | fail | ok [baseline] |
| city_a2_day | R-REP-1 | 0.1801 | 0.1801 | 0.0000 | 0.0180 | pass | ok |
| city_a2_day | 12.6 route never occluded | - | - | - | - | n/a | n/a: no visible route room |
| city_a2_night | R-VAL-1 | 0.1550 | 0.1550 | 0.0000 | 0.0200 | pass | ok |
| city_a2_night | R-VAL-2 | 0.2757 | 0.2757 | 0.0000 | 0.0500 | pass | ok |
| city_a2_night | R-VAL-3 | 0.0091 | 0.0091 | 0.0000 | 0.0100 | pass | ok |
| city_a2_night | 12.2 ratio | 2.7990 | 2.7990 | 0.0000 | 0.1500 | warn | ok [pre-accepted] |
| city_a2_night | R-FOCUS-1 | 1.7756 | - | - | 0.1776 | pass | n/a (theirs null) |
| city_a2_night | R-HOR-1 | 0.0536 | 0.0536 | 0.0000 | 0.0054 | pass | ok |
| city_a2_night | R-HUE-1 | 3.3025 | 3.3025 | 0.0000 | 0.2000 | fail | ok [baseline] |
| city_a2_night | R-HUE-2 | 0.6060 | 0.6060 | 0.0000 | 0.0500 | fail | ok [baseline] |
| city_a2_night | R-REP-1 | 0.2474 | 0.2474 | 0.0000 | 0.0247 | pass | ok |
| city_a2_night | 12.6 route never occluded | - | - | - | - | n/a | n/a: no visible route room |
| hq_aurelian_decision | R-VAL-1 | 0.1535 | 0.1535 | 0.0000 | 0.0200 | pass | ok |
| hq_aurelian_decision | R-VAL-2 | 0.3599 | 0.3599 | 0.0000 | 0.0500 | pass | ok |
| hq_aurelian_decision | R-VAL-3 | 0.0047 | 0.0047 | 0.0000 | 0.0100 | pass | ok |
| hq_aurelian_decision | 12.2 ratio | 2.7923 | 2.7923 | 0.0000 | 0.1500 | warn | ok |
| hq_aurelian_decision | R-CALM-1 | 0.5430 | 0.5430 | 0.0000 | 0.0543 | pass | ok |
| hq_aurelian_decision | R-CALM-2 | 0.1773 | 0.1773 | 0.0000 | 0.0400 | pass | ok |
| hq_aurelian_decision | R-FOCUS-1 | 2.2608 | 2.2608 | 0.0000 | 0.2261 | pass | ok |
| hq_aurelian_decision | R-REP-1 | 0.4887 | 0.4887 | 0.0000 | 0.0489 | pass | ok |
| hq_aurelian_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_aurelian_overview | R-VAL-1 | 0.1520 | 0.1520 | 0.0000 | 0.0200 | pass | ok |
| hq_aurelian_overview | R-VAL-2 | 0.3814 | 0.3814 | 0.0000 | 0.0500 | pass | ok |
| hq_aurelian_overview | R-VAL-3 | 0.0076 | 0.0076 | 0.0000 | 0.0100 | pass | ok |
| hq_aurelian_overview | 12.2 ratio | 2.4602 | 2.4602 | 0.0000 | 0.1500 | warn | ok |
| hq_aurelian_overview | R-CALM-1 | 0.4901 | 0.4901 | 0.0000 | 0.0490 | pass | ok |
| hq_aurelian_overview | R-CALM-2 | 0.1682 | 0.1682 | 0.0000 | 0.0400 | pass | ok |
| hq_aurelian_overview | R-FOCUS-1 | 1.9013 | 1.9013 | 0.0000 | 0.1901 | pass | ok |
| hq_aurelian_overview | R-REP-1 | 0.4463 | 0.4463 | 0.0000 | 0.0446 | pass | ok |
| hq_aurelian_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_halcyon_decision | R-VAL-1 | 0.1656 | 0.1656 | 0.0000 | 0.0200 | pass | ok |
| hq_halcyon_decision | R-VAL-2 | 0.3168 | 0.3168 | 0.0000 | 0.0500 | pass | ok |
| hq_halcyon_decision | R-VAL-3 | 0.0033 | 0.0033 | 0.0000 | 0.0100 | pass | ok |
| hq_halcyon_decision | 12.2 ratio | 2.6669 | 2.6669 | 0.0000 | 0.1500 | warn | ok |
| hq_halcyon_decision | R-CALM-1 | 0.3475 | 0.3475 | 0.0000 | 0.0348 | fail | ok |
| hq_halcyon_decision | R-CALM-2 | 0.0909 | 0.0909 | 0.0000 | 0.0400 | fail | ok |
| hq_halcyon_decision | R-FOCUS-1 | 1.7477 | 1.7477 | 0.0000 | 0.1748 | pass | ok |
| hq_halcyon_decision | R-REP-1 | 0.7430 | 0.7430 | 0.0000 | 0.0743 | fail | ok [baseline] |
| hq_halcyon_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_halcyon_overview | R-VAL-1 | 0.1087 | 0.1087 | 0.0000 | 0.0200 | warn | ok |
| hq_halcyon_overview | R-VAL-2 | 0.4635 | 0.4635 | 0.0000 | 0.0500 | fail | ok [baseline] |
| hq_halcyon_overview | R-VAL-3 | 0.0023 | 0.0023 | 0.0000 | 0.0100 | pass | ok |
| hq_halcyon_overview | 12.2 ratio | 3.1907 | 3.1907 | 0.0000 | 0.1500 | warn | ok |
| hq_halcyon_overview | R-CALM-1 | 0.2884 | 0.2884 | 0.0000 | 0.0288 | fail | ok |
| hq_halcyon_overview | R-CALM-2 | 0.0364 | 0.0364 | 0.0000 | 0.0400 | fail | ok |
| hq_halcyon_overview | R-FOCUS-1 | 2.4445 | 2.4473 | 0.0028 | 0.2447 | pass | ok |
| hq_halcyon_overview | R-REP-1 | 0.3708 | 0.3708 | 0.0000 | 0.0371 | pass | ok |
| hq_halcyon_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_meridian_decision | R-VAL-1 | 0.1749 | 0.1749 | 0.0000 | 0.0200 | warn | ok |
| hq_meridian_decision | R-VAL-2 | 0.2531 | 0.2531 | 0.0000 | 0.0500 | pass | ok |
| hq_meridian_decision | R-VAL-3 | 0.0278 | 0.0278 | 0.0000 | 0.0100 | fail | ok [baseline] |
| hq_meridian_decision | 12.2 ratio | 1.0648 | 1.0648 | 0.0000 | 0.1500 | fail | ok [baseline] |
| hq_meridian_decision | R-CALM-1 | 0.5980 | 0.5980 | 0.0000 | 0.0598 | pass | ok |
| hq_meridian_decision | R-CALM-2 | 0.2000 | 0.2000 | 0.0000 | 0.0400 | pass | ok |
| hq_meridian_decision | R-FOCUS-1 | 1.1645 | 1.1603 | 0.0042 | 0.1165 | fail | ok [baseline] |
| hq_meridian_decision | R-REP-1 | 0.6918 | 0.6918 | 0.0000 | 0.0692 | fail | ok [baseline] |
| hq_meridian_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_meridian_overview | R-VAL-1 | 0.1386 | 0.1386 | 0.0000 | 0.0200 | pass | ok |
| hq_meridian_overview | R-VAL-2 | 0.3586 | 0.3586 | 0.0000 | 0.0500 | pass | ok |
| hq_meridian_overview | R-VAL-3 | 0.0182 | 0.0182 | 0.0000 | 0.0100 | pass | ok |
| hq_meridian_overview | 12.2 ratio | 2.5085 | 2.5085 | 0.0000 | 0.1500 | warn | ok |
| hq_meridian_overview | R-CALM-1 | 0.3083 | 0.3083 | 0.0000 | 0.0308 | fail | ok |
| hq_meridian_overview | R-CALM-2 | 0.1045 | 0.1045 | 0.0000 | 0.0400 | fail | ok |
| hq_meridian_overview | R-FOCUS-1 | 1.6474 | 1.6474 | 0.0000 | 0.1647 | pass | ok |
| hq_meridian_overview | R-REP-1 | 0.3174 | 0.3174 | 0.0000 | 0.0317 | pass | ok |
| hq_meridian_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_orbital_decision | R-VAL-1 | 0.1219 | 0.1219 | 0.0000 | 0.0200 | pass | ok |
| hq_orbital_decision | R-VAL-2 | 0.4125 | 0.4125 | 0.0000 | 0.0500 | fail | ok [baseline] |
| hq_orbital_decision | R-VAL-3 | 0.0271 | 0.0271 | 0.0000 | 0.0100 | fail | ok [baseline] |
| hq_orbital_decision | 12.2 ratio | 3.4424 | 3.4424 | 0.0000 | 0.1500 | warn | ok |
| hq_orbital_decision | R-CALM-1 | 0.4626 | 0.4626 | 0.0000 | 0.0463 | pass | ok |
| hq_orbital_decision | R-CALM-2 | 0.1682 | 0.1682 | 0.0000 | 0.0400 | pass | ok |
| hq_orbital_decision | R-FOCUS-1 | 1.3569 | 1.3569 | 0.0000 | 0.1357 | fail | ok [baseline] |
| hq_orbital_decision | R-REP-1 | 0.3531 | 0.3531 | 0.0000 | 0.0353 | pass | ok |
| hq_orbital_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_orbital_overview | R-VAL-1 | 0.1177 | 0.1177 | 0.0000 | 0.0200 | pass | ok |
| hq_orbital_overview | R-VAL-2 | 0.4093 | 0.4093 | 0.0000 | 0.0500 | fail | ok [baseline] |
| hq_orbital_overview | R-VAL-3 | 0.0110 | 0.0110 | 0.0000 | 0.0100 | pass | ok |
| hq_orbital_overview | 12.2 ratio | 3.8462 | 3.8462 | 0.0000 | 0.1500 | warn | ok |
| hq_orbital_overview | R-CALM-1 | 0.3637 | 0.3637 | 0.0000 | 0.0364 | fail | ok |
| hq_orbital_overview | R-CALM-2 | 0.0909 | 0.0909 | 0.0000 | 0.0400 | fail | ok |
| hq_orbital_overview | R-FOCUS-1 | 2.1995 | 2.1976 | 0.0019 | 0.2200 | pass | ok |
| hq_orbital_overview | R-REP-1 | 0.3139 | 0.3139 | 0.0000 | 0.0314 | pass | ok |
| hq_orbital_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_rebel_cell_decision | R-VAL-1 | 0.1448 | 0.1448 | 0.0000 | 0.0200 | pass | ok |
| hq_rebel_cell_decision | R-VAL-2 | 0.3530 | 0.3530 | 0.0000 | 0.0500 | pass | ok |
| hq_rebel_cell_decision | R-VAL-3 | 0.0240 | 0.0240 | 0.0000 | 0.0100 | pass | ok |
| hq_rebel_cell_decision | 12.2 ratio | 1.4036 | 1.4036 | 0.0000 | 0.1500 | fail | ok [baseline] |
| hq_rebel_cell_decision | R-CALM-1 | 0.4919 | 0.4919 | 0.0000 | 0.0492 | pass | ok |
| hq_rebel_cell_decision | R-CALM-2 | 0.1455 | 0.1455 | 0.0000 | 0.0400 | pass | ok |
| hq_rebel_cell_decision | R-REP-1 | 0.5524 | 0.5524 | 0.0000 | 0.0552 | pass | ok |
| hq_rebel_cell_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_rebel_cell_overview | R-VAL-1 | 0.1210 | 0.1210 | 0.0000 | 0.0200 | pass | ok |
| hq_rebel_cell_overview | R-VAL-2 | 0.4227 | 0.4227 | 0.0000 | 0.0500 | fail | ok [baseline] |
| hq_rebel_cell_overview | R-VAL-3 | 0.0193 | 0.0193 | 0.0000 | 0.0100 | pass | ok |
| hq_rebel_cell_overview | 12.2 ratio | 1.1820 | 1.1820 | 0.0000 | 0.1500 | fail | ok [baseline] |
| hq_rebel_cell_overview | R-CALM-1 | 0.6048 | 0.6048 | 0.0000 | 0.0605 | pass | ok |
| hq_rebel_cell_overview | R-CALM-2 | 0.2045 | 0.2045 | 0.0000 | 0.0400 | pass | ok |
| hq_rebel_cell_overview | R-REP-1 | 0.5054 | 0.5054 | 0.0000 | 0.0505 | pass | ok |
| hq_rebel_cell_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_solace_decision | R-VAL-1 | 0.1205 | 0.1205 | 0.0000 | 0.0200 | pass | ok |
| hq_solace_decision | R-VAL-2 | 0.3488 | 0.3488 | 0.0000 | 0.0500 | pass | ok |
| hq_solace_decision | R-VAL-3 | 0.0205 | 0.0205 | 0.0000 | 0.0100 | pass | ok |
| hq_solace_decision | 12.2 ratio | 2.5731 | 2.5731 | 0.0000 | 0.1500 | warn | ok |
| hq_solace_decision | R-CALM-1 | 0.2695 | 0.2695 | 0.0000 | 0.0270 | fail | ok |
| hq_solace_decision | R-CALM-2 | 0.0273 | 0.0273 | 0.0000 | 0.0400 | fail | ok |
| hq_solace_decision | R-FOCUS-1 | 1.7589 | 1.7604 | 0.0015 | 0.1760 | pass | ok |
| hq_solace_decision | R-REP-1 | 0.3596 | 0.3596 | 0.0000 | 0.0360 | pass | ok |
| hq_solace_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_solace_overview | R-VAL-1 | 0.1272 | 0.1272 | 0.0000 | 0.0200 | pass | ok |
| hq_solace_overview | R-VAL-2 | 0.3736 | 0.3736 | 0.0000 | 0.0500 | pass | ok |
| hq_solace_overview | R-VAL-3 | 0.0073 | 0.0073 | 0.0000 | 0.0100 | pass | ok |
| hq_solace_overview | 12.2 ratio | 2.5551 | 2.5551 | 0.0000 | 0.1500 | warn | ok |
| hq_solace_overview | R-CALM-1 | 0.3450 | 0.3450 | 0.0000 | 0.0345 | fail | ok |
| hq_solace_overview | R-CALM-2 | 0.1045 | 0.1045 | 0.0000 | 0.0400 | fail | ok |
| hq_solace_overview | R-FOCUS-1 | 1.5495 | 1.5509 | 0.0014 | 0.1551 | pass | ok |
| hq_solace_overview | R-REP-1 | 0.2122 | 0.2122 | 0.0000 | 0.0212 | pass | ok |
| hq_solace_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_tethys_decision | R-VAL-1 | 0.1400 | 0.1400 | 0.0000 | 0.0200 | pass | ok |
| hq_tethys_decision | R-VAL-2 | 0.2929 | 0.2929 | 0.0000 | 0.0500 | pass | ok |
| hq_tethys_decision | R-VAL-3 | 0.0023 | 0.0023 | 0.0000 | 0.0100 | pass | ok |
| hq_tethys_decision | 12.2 ratio | 2.0242 | 2.0242 | 0.0000 | 0.1500 | warn | ok [pre-accepted] |
| hq_tethys_decision | R-CALM-1 | 0.4128 | 0.4128 | 0.0000 | 0.0413 | fail | ok |
| hq_tethys_decision | R-CALM-2 | 0.1227 | 0.1227 | 0.0000 | 0.0400 | pass | ok |
| hq_tethys_decision | R-FOCUS-1 | 0.9966 | 0.9965 | 0.0001 | 0.0997 | fail | ok [baseline] |
| hq_tethys_decision | R-REP-1 | 0.2936 | 0.2936 | 0.0000 | 0.0294 | pass | ok |
| hq_tethys_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: no visible route room |
| hq_tethys_overview | R-VAL-1 | 0.1400 | 0.1400 | 0.0000 | 0.0200 | pass | ok |
| hq_tethys_overview | R-VAL-2 | 0.3100 | 0.3100 | 0.0000 | 0.0500 | pass | ok |
| hq_tethys_overview | R-VAL-3 | 0.0009 | 0.0009 | 0.0000 | 0.0100 | pass | ok |
| hq_tethys_overview | 12.2 ratio | 1.8067 | 1.8067 | 0.0000 | 0.1500 | pass | ok |
| hq_tethys_overview | R-CALM-1 | 0.3639 | 0.3639 | 0.0000 | 0.0364 | fail | ok |
| hq_tethys_overview | R-CALM-2 | 0.1136 | 0.1136 | 0.0000 | 0.0400 | fail | ok |
| hq_tethys_overview | R-FOCUS-1 | 1.3668 | 1.3659 | 0.0009 | 0.1367 | fail | ok [baseline] |
| hq_tethys_overview | R-REP-1 | 0.2470 | 0.2470 | 0.0000 | 0.0247 | pass | ok |
| hq_tethys_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: no visible route room |
| street_decision | R-VAL-1 | 0.1407 | 0.1407 | 0.0000 | 0.0200 | pass | ok |
| street_decision | R-VAL-2 | 0.3267 | 0.3267 | 0.0000 | 0.0500 | pass | ok |
| street_decision | R-VAL-3 | 0.0099 | 0.0099 | 0.0000 | 0.0100 | pass | ok |
| street_decision | 12.2 ratio | 1.6957 | 1.6957 | 0.0000 | 0.1500 | pass | ok |
| street_decision | R-CALM-1 | 0.6650 | 0.6650 | 0.0000 | 0.0665 | pass | ok |
| street_decision | R-CALM-2 | 0.1318 | 0.1318 | 0.0000 | 0.0400 | pass | ok |
| street_decision | R-DET-1 | 0.0314 | 0.0314 | 0.0000 | 0.0031 | n/a | ok |
| street_decision | R-DET-2 | 458.9844 | 458.9844 | 0.0000 | 45.8984 | n/a | ok |
| street_decision | R-FOCUS-1 | 1.1087 | - | - | 0.1109 | fail | n/a (theirs null) |
| street_decision | R-HUE-1 | 3.8970 | 3.8970 | 0.0000 | 0.2000 | pass | ok |
| street_decision | R-HUE-2 | 0.4360 | 0.4360 | 0.0000 | 0.0500 | pass | ok |
| street_decision | R-REP-1 | 0.7850 | 0.5885 | 0.1965 | 0.0785 | fail | DRIFT |
| street_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| street_overview | R-VAL-1 | 0.1302 | 0.1302 | 0.0000 | 0.0200 | pass | ok |
| street_overview | R-VAL-2 | 0.2987 | 0.2987 | 0.0000 | 0.0500 | pass | ok |
| street_overview | R-VAL-3 | 0.0049 | 0.0049 | 0.0000 | 0.0100 | pass | ok |
| street_overview | 12.2 ratio | 1.6698 | 1.6698 | 0.0000 | 0.1500 | pass | ok |
| street_overview | R-CALM-1 | 0.5985 | 0.5985 | 0.0000 | 0.0599 | pass | ok |
| street_overview | R-CALM-2 | 0.2545 | 0.2545 | 0.0000 | 0.0400 | pass | ok |
| street_overview | R-DET-1 | 0.0309 | 0.0309 | 0.0000 | 0.0031 | pass | ok |
| street_overview | R-DET-2 | 675.9983 | 675.9983 | 0.0000 | 67.5998 | pass | ok |
| street_overview | R-HUE-1 | 4.0958 | 4.0958 | 0.0000 | 0.2000 | pass | ok |
| street_overview | R-HUE-2 | 0.4380 | 0.4380 | 0.0000 | 0.0500 | pass | ok |
| street_overview | R-REP-1 | 0.4086 | 0.4086 | 0.0000 | 0.0409 | pass | ok |
| street_overview | R-SIL-1 | 0.1828 | 0.1828 | 0.0000 | 0.0183 | pass | ok |
| street_overview | R-SIL-2 | 0.1394 | 0.1394 | 0.0000 | 0.0139 | pass | ok |
| street_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
