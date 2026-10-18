# Balance comparison: camp_sink10

- A: `camp_base.json` (overrides: none)
- B: `camp_sink10.json` (overrides: config.heat_purchase_amount=10)
- mode campaign; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 80 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| campaign@ice0 | deaths | 21.950 | 21.800 | -0.150 | [-6.450, +6.100] | -0.7 % | noise |
| campaign@ice0 | heat_peak | 91.700 | 90.650 | -1.050 | [-10.302, +8.653] | -1.1 % | noise |
| campaign@ice0 | minutes | 745.530 | 758.580 | +13.050 | [-151.682, +185.100] | +1.8 % | noise |
| campaign@ice0 | raids | 6.000 | 5.750 | -0.250 | [-1.153, +0.650] | -4.2 % | noise |
| campaign@ice0 | recruits | 21.400 | 21.300 | -0.100 | [-6.150, +6.002] | -0.5 % | noise |
| campaign@ice0 | runs | 47.700 | 48.650 | +0.950 | [-9.550, +11.507] | +2.0 % | noise |
| campaign@ice0 | schematics_income | 1276.300 | 1343.650 | +67.350 | [-174.140, +324.453] | +5.3 % | noise |
| campaign@ice0 | schematics_unspent | 134.400 | 168.850 | +34.450 | [-21.200, +91.450] | +25.6 % | noise |
| campaign@ice0 | turns | 1236.100 | 1266.800 | +30.700 | [-248.835, +309.035] | +2.5 % | noise |
| campaign@ice0 | won | 0.200 | 0.250 | +0.050 | [-0.150, +0.250] | +25.0 % | noise |

