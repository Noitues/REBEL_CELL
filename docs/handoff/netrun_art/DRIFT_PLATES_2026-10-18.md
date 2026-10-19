# Drift compare against the 18 golden plates (NA-04b, refreshed W1 NA-04c, W1 LAMPSHIFT, re-run W1 NA-04d on art-pass 7772e6ba, 2026-10-19)

Drift compare of our image checks (`tools/netrun_art/checks`) against the golden plates of art-pass `7772e6ba` (PIPELINE_SPEC 12.8), read-only. `7772e6ba` is the newest art-pass commit and has all the wanted plate commits as ancestors: city `57c901fc` / `8e6f6b7d`, Halcyon `d22d8559`, Orbital `8cc68f14`, Meridian `ced68d20`, Rebel Cell `7772e6ba` (checked with `git merge-base --is-ancestor`; street stamps `ed8675a8` also included). The plates were read with `git show 7772e6ba:docs/concepts/golden_plates/<file>` from the art-pass repo and extracted to a scratch folder; no image was copied into the repo. Command, from `tools`:

    python -m netrun_art.checks.drift <plates dir> --work <scratch dir> --out <file>

Method: each plate's `<stem>.png`, `<stem>_id.png`, `<stem>_capture.json` is run through `check_capture_folder` (12.1, 12.2, 12.7, 12.6 route) and each image value is compared with the plate's `values.json` inside `checks.tolerance.renderer`. The derive fields are null (concept renders), so only image values are compared. `[baseline]` marks a check the plate already fails (reported, not a capture failure); `[pre-accepted]` a config pre-accepted warn.

## Result

- 18 plates, 0 DRIFT rows. The one open drift of the previous run (street_decision R-REP-1, ours 0.7850 vs theirs 0.5885) is closed: it was a scope bug in our check. We measured the whole frame on the street decision view; 12.7 says R-REP-1 on street views is the facade band only. Both street views now use `composition.facade.street_overview` = `[0.0, 0.10, 1.0, 0.80]` (frame fractions, y from the top), the band art-pass passes as `spec["facade"]` to `pvc_metrics.repetition` (art-pass `golden_plates/scripts/make_plate.py:179-181`; `route_map_graph/proc_vs_custom/scripts/pvc_metrics.py:15, 372`; `pvc_metrics.repetition` is the 128 px tile / stride 64 autocorrelation p90 that `checks/metrics.py repetition` already ports). street_decision R-REP-1 is now 0.5885 vs 0.5885, street_overview 0.4086 vs 0.4086.
- Deltas are 0 to rounding, except R-FOCUS-1 (up to 0.0042, nearest resample of the id box).
- Updated plates: all four HQ fixes carry the new values with no drift (Halcyon, Orbital, Meridian, Rebel Cell). Their `[baseline]` rows are gone: the plates now pass what they used to fail (Halcyon decision R-REP-1, Halcyon / Orbital / Rebel Cell overview R-VAL-2, Meridian decision R-VAL-3 / ratio / R-FOCUS-1 / R-REP-1, Orbital R-VAL-3 / R-FOCUS-1, Rebel Cell ratio). Remaining baseline fails: city R-HUE-1/2 (day and night) and Tethys R-FOCUS-1 (decision and overview).
- City plates (`57c901fc`, `8e6f6b7d`): `time` key present; city_a2_day value band, ratio and R-FOCUS-1 are n/a (report only, values kept); city_a2_night R-FOCUS-1 is 1.7756 vs theirs 1.7731 (delta 0.0025, ok), ratio 2.7990 warn is pre-accepted from config.
- Warns / fails that are not baseline and not drift (same as before, plate and ours agree): 12.2 ratio warns on most HQ plates (over 2.0 landmark ratio), R-CALM-1/2 fails on the HQ plates.
- 12.6 route never occluded is now counted by depth (NA-04d, spec 12.0): n/a on all 18 plates, since none has `depth.png` (and HQ / street plates have G = 0, city plates no route rooms). It first runs on Godot captures.
- art-pass to fix in `values.json` (their side): `street_decision` has R-FOCUS-1 null in `values.json` while we score it (1.1087, fail); art-pass to fill it, not a drift.

## Summary

| plate | ok | DRIFT | n/a |
|---|---|---|---|
| city_a2_day | 9 | 0 | 0 |
| city_a2_night | 9 | 0 | 0 |
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
| street_decision | 11 | 0 | 1 |
| street_overview | 13 | 0 | 0 |

## Rows

| plate | check | ours | theirs | delta | tol | our status | verdict |
|---|---|---|---|---|---|---|---|
| city_a2_day | R-VAL-1 | 0.2501 | 0.2501 | 0.0000 | 0.0200 | n/a | ok [report-only] |
| city_a2_day | R-VAL-2 | 0.0834 | 0.0834 | 0.0000 | 0.0500 | n/a | ok [report-only] |
| city_a2_day | R-VAL-3 | 0.0006 | 0.0006 | 0.0000 | 0.0100 | n/a | ok [report-only] |
| city_a2_day | 12.2 ratio | 1.1977 | 1.1977 | 0.0000 | 0.1500 | n/a | ok [report-only] |
| city_a2_day | R-FOCUS-1 | 0.9274 | 0.9274 | 0.0000 | 0.0927 | n/a | ok [report-only] |
| city_a2_day | R-HOR-1 | 0.0397 | 0.0397 | 0.0000 | 0.0040 | pass | ok |
| city_a2_day | R-HUE-1 | 2.8440 | 2.8440 | 0.0000 | 0.2000 | fail | ok [baseline] |
| city_a2_day | R-HUE-2 | 0.6410 | 0.6410 | 0.0000 | 0.0500 | fail | ok [baseline] |
| city_a2_day | R-REP-1 | 0.1801 | 0.1801 | 0.0000 | 0.0180 | pass | ok |
| city_a2_day | 12.6 route never occluded | - | - | - | - | n/a | n/a: no visible route room |
| city_a2_night | R-VAL-1 | 0.1550 | 0.1550 | 0.0000 | 0.0200 | pass | ok |
| city_a2_night | R-VAL-2 | 0.2757 | 0.2757 | 0.0000 | 0.0500 | pass | ok |
| city_a2_night | R-VAL-3 | 0.0091 | 0.0091 | 0.0000 | 0.0100 | pass | ok |
| city_a2_night | 12.2 ratio | 2.7990 | 2.7990 | 0.0000 | 0.1500 | warn | ok [pre-accepted] |
| city_a2_night | R-FOCUS-1 | 1.7756 | 1.7731 | 0.0025 | 0.1776 | pass | ok |
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
| hq_halcyon_decision | R-VAL-1 | 0.1550 | 0.1550 | 0.0000 | 0.0200 | pass | ok |
| hq_halcyon_decision | R-VAL-2 | 0.3309 | 0.3309 | 0.0000 | 0.0500 | pass | ok |
| hq_halcyon_decision | R-VAL-3 | 0.0029 | 0.0029 | 0.0000 | 0.0100 | pass | ok |
| hq_halcyon_decision | 12.2 ratio | 2.3523 | 2.3523 | 0.0000 | 0.1500 | warn | ok |
| hq_halcyon_decision | R-CALM-1 | 0.3218 | 0.3218 | 0.0000 | 0.0322 | fail | ok |
| hq_halcyon_decision | R-CALM-2 | 0.0591 | 0.0591 | 0.0000 | 0.0400 | fail | ok |
| hq_halcyon_decision | R-FOCUS-1 | 1.7046 | 1.7046 | 0.0000 | 0.1705 | pass | ok |
| hq_halcyon_decision | R-REP-1 | 0.5730 | 0.5730 | 0.0000 | 0.0573 | pass | ok |
| hq_halcyon_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_halcyon_overview | R-VAL-1 | 0.1271 | 0.1271 | 0.0000 | 0.0200 | pass | ok |
| hq_halcyon_overview | R-VAL-2 | 0.3883 | 0.3883 | 0.0000 | 0.0500 | pass | ok |
| hq_halcyon_overview | R-VAL-3 | 0.0022 | 0.0022 | 0.0000 | 0.0100 | pass | ok |
| hq_halcyon_overview | 12.2 ratio | 2.6221 | 2.6221 | 0.0000 | 0.1500 | warn | ok |
| hq_halcyon_overview | R-CALM-1 | 0.3089 | 0.3089 | 0.0000 | 0.0309 | fail | ok |
| hq_halcyon_overview | R-CALM-2 | 0.0636 | 0.0636 | 0.0000 | 0.0400 | fail | ok |
| hq_halcyon_overview | R-FOCUS-1 | 2.6318 | 2.6317 | 0.0001 | 0.2632 | pass | ok |
| hq_halcyon_overview | R-REP-1 | 0.2763 | 0.2763 | 0.0000 | 0.0276 | pass | ok |
| hq_halcyon_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_meridian_decision | R-VAL-1 | 0.1660 | 0.1660 | 0.0000 | 0.0200 | pass | ok |
| hq_meridian_decision | R-VAL-2 | 0.3139 | 0.3139 | 0.0000 | 0.0500 | pass | ok |
| hq_meridian_decision | R-VAL-3 | 0.0174 | 0.0174 | 0.0000 | 0.0100 | pass | ok |
| hq_meridian_decision | 12.2 ratio | 1.8021 | 1.8021 | 0.0000 | 0.1500 | pass | ok |
| hq_meridian_decision | R-CALM-1 | 0.5652 | 0.5652 | 0.0000 | 0.0565 | pass | ok |
| hq_meridian_decision | R-CALM-2 | 0.1136 | 0.1136 | 0.0000 | 0.0400 | fail | ok |
| hq_meridian_decision | R-FOCUS-1 | 2.7120 | 2.7033 | 0.0087 | 0.2712 | pass | ok |
| hq_meridian_decision | R-REP-1 | 0.5065 | 0.5065 | 0.0000 | 0.0507 | pass | ok |
| hq_meridian_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_meridian_overview | R-VAL-1 | 0.1377 | 0.1377 | 0.0000 | 0.0200 | pass | ok |
| hq_meridian_overview | R-VAL-2 | 0.3613 | 0.3613 | 0.0000 | 0.0500 | pass | ok |
| hq_meridian_overview | R-VAL-3 | 0.0178 | 0.0178 | 0.0000 | 0.0100 | pass | ok |
| hq_meridian_overview | 12.2 ratio | 2.4178 | 2.4178 | 0.0000 | 0.1500 | warn | ok |
| hq_meridian_overview | R-CALM-1 | 0.3123 | 0.3123 | 0.0000 | 0.0312 | fail | ok |
| hq_meridian_overview | R-CALM-2 | 0.1091 | 0.1091 | 0.0000 | 0.0400 | fail | ok |
| hq_meridian_overview | R-FOCUS-1 | 1.6302 | 1.6302 | 0.0000 | 0.1630 | pass | ok |
| hq_meridian_overview | R-REP-1 | 0.2992 | 0.2992 | 0.0000 | 0.0299 | pass | ok |
| hq_meridian_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_orbital_decision | R-VAL-1 | 0.1275 | 0.1275 | 0.0000 | 0.0200 | pass | ok |
| hq_orbital_decision | R-VAL-2 | 0.3922 | 0.3922 | 0.0000 | 0.0500 | pass | ok |
| hq_orbital_decision | R-VAL-3 | 0.0159 | 0.0159 | 0.0000 | 0.0100 | pass | ok |
| hq_orbital_decision | 12.2 ratio | 3.4999 | 3.4999 | 0.0000 | 0.1500 | warn | ok |
| hq_orbital_decision | R-CALM-1 | 0.4372 | 0.4372 | 0.0000 | 0.0437 | fail | ok |
| hq_orbital_decision | R-CALM-2 | 0.1545 | 0.1545 | 0.0000 | 0.0400 | pass | ok |
| hq_orbital_decision | R-FOCUS-1 | 1.5357 | 1.5357 | 0.0000 | 0.1536 | pass | ok |
| hq_orbital_decision | R-REP-1 | 0.3388 | 0.3388 | 0.0000 | 0.0339 | pass | ok |
| hq_orbital_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_orbital_overview | R-VAL-1 | 0.1302 | 0.1302 | 0.0000 | 0.0200 | pass | ok |
| hq_orbital_overview | R-VAL-2 | 0.3662 | 0.3662 | 0.0000 | 0.0500 | pass | ok |
| hq_orbital_overview | R-VAL-3 | 0.0078 | 0.0078 | 0.0000 | 0.0100 | pass | ok |
| hq_orbital_overview | 12.2 ratio | 3.8421 | 3.8421 | 0.0000 | 0.1500 | warn | ok |
| hq_orbital_overview | R-CALM-1 | 0.3484 | 0.3484 | 0.0000 | 0.0348 | fail | ok |
| hq_orbital_overview | R-CALM-2 | 0.0545 | 0.0545 | 0.0000 | 0.0400 | fail | ok |
| hq_orbital_overview | R-FOCUS-1 | 2.1925 | 2.1908 | 0.0017 | 0.2192 | pass | ok |
| hq_orbital_overview | R-REP-1 | 0.3140 | 0.3140 | 0.0000 | 0.0314 | pass | ok |
| hq_orbital_overview | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_rebel_cell_decision | R-VAL-1 | 0.1618 | 0.1618 | 0.0000 | 0.0200 | pass | ok |
| hq_rebel_cell_decision | R-VAL-2 | 0.3412 | 0.3412 | 0.0000 | 0.0500 | pass | ok |
| hq_rebel_cell_decision | R-VAL-3 | 0.0194 | 0.0194 | 0.0000 | 0.0100 | pass | ok |
| hq_rebel_cell_decision | 12.2 ratio | 1.9575 | 1.9575 | 0.0000 | 0.1500 | pass | ok |
| hq_rebel_cell_decision | R-CALM-1 | 0.4827 | 0.4827 | 0.0000 | 0.0483 | pass | ok |
| hq_rebel_cell_decision | R-CALM-2 | 0.1500 | 0.1500 | 0.0000 | 0.0400 | pass | ok |
| hq_rebel_cell_decision | R-REP-1 | 0.5461 | 0.5461 | 0.0000 | 0.0546 | pass | ok |
| hq_rebel_cell_decision | 12.6 route never occluded | - | - | - | - | n/a | n/a: id.png carries no room indices (G = 0) |
| hq_rebel_cell_overview | R-VAL-1 | 0.1397 | 0.1397 | 0.0000 | 0.0200 | pass | ok |
| hq_rebel_cell_overview | R-VAL-2 | 0.3748 | 0.3748 | 0.0000 | 0.0500 | pass | ok |
| hq_rebel_cell_overview | R-VAL-3 | 0.0183 | 0.0183 | 0.0000 | 0.0100 | pass | ok |
| hq_rebel_cell_overview | 12.2 ratio | 1.8157 | 1.8157 | 0.0000 | 0.1500 | pass | ok |
| hq_rebel_cell_overview | R-CALM-1 | 0.5804 | 0.5804 | 0.0000 | 0.0580 | pass | ok |
| hq_rebel_cell_overview | R-CALM-2 | 0.2136 | 0.2136 | 0.0000 | 0.0400 | pass | ok |
| hq_rebel_cell_overview | R-REP-1 | 0.5016 | 0.5016 | 0.0000 | 0.0502 | pass | ok |
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
| street_decision | R-REP-1 | 0.5885 | 0.5885 | 0.0000 | 0.0589 | pass | ok |
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
