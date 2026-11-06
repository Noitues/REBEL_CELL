# Neon-push variant (branch art/tide-neon-push, head 1d9ea46b, from de4c3896)

art/tide-proto is untouched (de4c3896, checked out again after this work). Nothing outside variant_neon/ was written in G1_parity. Files here: compare_r13_vs_neon.jpg (plan camera r13 | neon-push, a zoom-3 hotspot close-up of each, both 320 px squints), squint_320_r13_vs_neon.png (the two squints enlarged).

## The switch
`CityConfig.neon_push` (content/config/city_config.tres, default false = the round-13 look, verified: the default plan capture matches r13 to 0.001 on every luma percentile). One bool, with the values in the `neon_push_*` exports next to it. Look-dev: `--neon-push` in tools/look_parity/parity_capture.gd.

## What the push does
- Saturation: the neon shader boosts saturation 1.45x and the white share (frames, light blocks) drops from 35 % to 10 %; content stays fully saturated tones.
- Coloured bloom: the grade's neon-class bloom gain 2.2x (`g1_neon_bloom`); spill and halo strength 1.6x.
- Avenues: blade signs on 80 % of avenue-facing walls from 14 BU (was 45 % from 20), a vertical neon edge strip up a corner on 35 % of avenue-facing buildings, LED crowns on every tower over 28 BU (was 80 % over 40).
- Northern strip: buildings along the strip get screens from 9 BU (instead of 18), so the strip is real signage rather than halos.
- Holo ads: see the bug below; in the push they are visible (width 2.4 lots, 14-30 BU high, 12 % of towers over 30 BU, never over Solace).
- Unchanged: no pink in parks, lamps stay dim amber, darks stay deep (p1 / p5 0.062 / 0.129 vs r13 0.062 / 0.127).

## A bug found in round 12 / 13 (baseline, not fixed there)
The holo ads never rendered in rounds 12 and 13: their height threshold was 60 BU but the tallest building in the plan is 52.9 BU, so zero holos were built (the round-12 report said they were present but hard to see: wrong). The test passed because the test city had 60 BU towers. Suggest lowering `neon_holo_min_h` to about 30 in the baseline if holos are wanted; I left the baseline alone as asked.

## Metrics and perf
Push plan luma p1/5/25/50/75/95: 0.062 0.129 0.245 0.308 0.431 0.809 (r13: 0.062 0.127 0.244 0.309 0.427 0.809); median rgb (69,76,124).
Perf, level 3 city GPU (a 500-frame run with --neon-push): mean 11.39 ms, p95 11.77 ms against round 9's 11.07 ms: +0.70 ms, inside the +1.5 ms budget (round 13 itself: 11.14 ms).
Tests: test_city_neon_kit 8 and test_city_grade 13 pass on the branch (no new tests for the preset). Full suite not run.

## Gaps
The push is a clear step toward saturated cyan / magenta / green / orange, but holo ads read as pale scanlined boards (the holo shader keeps a white edge and 42 % dropped lines); one magenta holo hovers near the garden edge (not over it). The Shibuya density is still not reached.

## Slips
None on `python -`. No foreign files touched; a temporary debug print in the view was added and removed before the commit.
