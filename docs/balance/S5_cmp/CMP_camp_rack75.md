# Balance comparison: camp_rack75

- A: `camp_base.json` (overrides: none)
- B: `camp_rack75.json` (overrides: config.rack_schematics_by_tier*=0.75)
- mode campaign; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 80 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | deaths | 21.950 | 21.800 | -0.150 | [-6.650, +6.250] | -0.7 % | noise |
| campaign@ice0 | heat_peak | 91.700 | 92.300 | +0.600 | [-7.950, +9.200] | +0.7 % | noise |
| campaign@ice0 | minutes | 745.530 | 745.500 | -0.030 | [-164.747, +170.166] | -0.0 % | noise |
| campaign@ice0 | raids | 6.000 | 6.000 | +0.000 | [-0.800, +0.800] | +0.0 % | noise |
| campaign@ice0 | recruits | 21.400 | 21.300 | -0.100 | [-6.550, +6.402] | -0.5 % | noise |
| campaign@ice0 | runs | 47.700 | 47.700 | +0.000 | [-11.103, +10.455] | +0.0 % | noise |
| campaign@ice0 | schematics_income | 1276.300 | 1128.200 | -148.100 | [-392.580, +123.555] | -11.6 % | noise |
| campaign@ice0 | schematics_unspent | 134.400 | 116.250 | -18.150 | [-61.900, +28.453] | -13.5 % | noise |
| campaign@ice0 | turns | 1236.100 | 1244.150 | +8.050 | [-279.455, +292.262] | +0.7 % | noise |
| campaign@ice0 | won | 0.200 | 0.200 | +0.000 | [-0.200, +0.200] | +0.0 % | noise |

