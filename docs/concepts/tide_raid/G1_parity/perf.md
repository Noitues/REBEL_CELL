# Perf: the raid city at the plate camera

RX 6700 XT, 1920 x 1080 window through `tools/run_windowed.py` (the window stays at its 60 Hz cap, so wall clock only shows p95 headroom). The numbers that count are the GPU times from `RenderingServer.viewport_get_measured_render_time_gpu` (city view = the 3D viewport; window = the 2D finish and UI). Other agents were rendering on the machine; GPU lock held during every capture batch.

| configuration | city GPU mean | p50 | p95 | p99 | window GPU p50 | wall p95 |
|---|---|---|---|---|---|---|
| legacy post (grade off, level 0) | 8.28 ms | 9.60 | 10.25 | 10.38 | 1.30 | 22.38 |
| level 1 (lite) | 10.37 ms | 10.37 | 10.62 | 10.82 | 0.83 | 17.20 |
| level 2 (+ wet reflections, shafts, pool glow) | 10.75 ms | 10.71 | 11.22 | 11.54 | 0.52 | 17.17 |
| level 3 (full, 2D finish) | 10.93 ms | 10.93 | 11.14 | 11.29 | 0.41 | 17.10 |
| level 3 without wet reflection (lamp streaks, light taps, sheen) | 10.72 ms | 10.73 | 10.92 | 11.02 | 0.52 | 17.05 |
| level 3 without bloom | 11.38 ms | 11.42 | 11.77 | 12.00 | 0.55 | 17.34 |
| level 3 without rain | 11.55 ms | 11.58 | 11.87 | 12.00 | 0.43 | 17.22 |
| level 3 without lamp pools | 11.37 ms | 11.35 | 11.85 | 12.04 | 0.43 | 17.36 |
| level 3 without bloom and rain | 10.42 ms | 10.42 | 10.73 | 11.34 | 0.77 | 17.52 |

r13

## Round 19
Level 3 city GPU (plan camera, 500 frames, GPU lock held): mean 11.25 ms, p50 11.18, p95 11.92 ms, p99 17.19 (limit 12.57). Window GPU p95 0.43 ms. r18: 11.59 ms p95. The added load is the highway light / glow quads and four array lookups per window pixel in the building shader.

## Round 20
Level 3 city GPU p95 12.38 ms (mean 11.83), limit 12.57. Higher than r19's 11.92 although a geometry layer was removed: the machine was shared, so treat it as noise but note the margin is 0.19 ms.

## Round 21
Level 3 city GPU p95 12.31 ms and 12.07 ms in two runs (means 11.63 / 11.46); limit 12.57. Nothing had to be cut.

## Round 22
Level 3 city GPU p95 12.35 ms (mean 11.63); limit 12.57.

## Round 23
Level 3 city GPU p95 11.57 ms (mean 11.14); limit 12.57.

## Round 24
Level 3 city GPU p95 11.70 ms (mean 11.16); limit 12.57.

## Round 25
Level 3 city GPU p95 11.77 ms (mean 11.26); limit 12.57.

## Round 26
Level 3 city GPU p95 12.31 ms (mean 11.78); limit 12.57 (0.26 ms margin; the strips add quads).

## Round 27
Level 3 city GPU p95 11.50 ms (mean 10.98); limit 12.57 (the strips are gone, the facades are off).

## Round 28
Level 3 city GPU p95 9.55 ms (mean 6.31; p50 8.85): the grade level 0 post (cel + ink, no realism grade) is cheaper than r27's 11.50 ms. Nothing cut.

## Round 29
Level 3 city GPU p95 10.80 ms (mean 10.05); limit 12.57.

## Round 30
Level 3 city GPU p95 9.43 ms (mean 6.08, p50 7.80); limit 12.57.

## Round 31
Level 3 city GPU p95 8.94 ms (mean 6.11); limit 12.57.

## Round 32
Level 3 city GPU p95 8.88 ms (mean 5.98); limit 12.57.

## Round 33
Level 3 city GPU p95 9.55 ms (mean 6.24); limit 12.57.

## Round 34
Level 3 city GPU p95 9.23 ms (mean 6.18); limit 12.57.

## Round 35
Level 3 city GPU p95 10.52 ms (mean 10.30); limit 12.57.

## Round 36
Level 3 city GPU p95 10.64 ms (mean 9.61); limit 12.57.

## Round 37
Level 3 city GPU p95 10.38 ms (mean 8.98); limit 12.57.

## Round 38
Level 3 city GPU p95 10.46 ms (mean 7.27); limit 12.57.

## Round 39
Level 3 city GPU p95 10.04 ms (mean 6.49); limit 12.57.

## Round 40
Level 3 city GPU p95 9.36 ms (mean 6.06); limit 12.57.

## Round 41
Level 3 city GPU p95 9.40 ms (mean 6.10); limit 12.57.
