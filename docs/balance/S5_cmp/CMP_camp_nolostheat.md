# Balance comparison: camp_nolostheat

- A: `camp_base.json` (overrides: none)
- B: `camp_nolostheat.json` (overrides: config.lost_raid_heat=0)
- mode campaign; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 80 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | deaths | 21.950 | 21.100 | -0.850 | [-7.400, +5.450] | -3.9 % | noise |
| campaign@ice0 | heat_peak | 91.700 | 88.500 | -3.200 | [-13.353, +6.655] | -3.5 % | noise |
| campaign@ice0 | minutes | 745.530 | 746.520 | +0.990 | [-175.232, +176.742] | +0.1 % | noise |
| campaign@ice0 | raids | 6.000 | 5.600 | -0.400 | [-1.200, +0.400] | -6.7 % | noise |
| campaign@ice0 | recruits | 21.400 | 20.600 | -0.800 | [-6.750, +5.450] | -3.7 % | noise |
| campaign@ice0 | runs | 47.700 | 47.900 | +0.200 | [-10.300, +10.852] | +0.4 % | noise |
| campaign@ice0 | schematics_income | 1276.300 | 1304.300 | +28.000 | [-223.015, +283.787] | +2.2 % | noise |
| campaign@ice0 | schematics_unspent | 134.400 | 159.650 | +25.250 | [-27.453, +83.860] | +18.8 % | noise |
| campaign@ice0 | turns | 1236.100 | 1265.050 | +28.950 | [-257.483, +326.603] | +2.3 % | noise |
| campaign@ice0 | won | 0.200 | 0.250 | +0.050 | [-0.150, +0.250] | +25.0 % | noise |

