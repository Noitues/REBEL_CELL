# Balance comparison: boss_step10

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_step10.json` (overrides: config.enrage_damage_pct_step_by_class=[0,25,25,10])
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 20.126 | +0.166 | [-6.014, +6.189] | +0.8 % | noise |
| boss@ice0 | died | 0.895 | 0.842 | -0.053 | [-0.211, +0.105] | -5.9 % | noise |
| boss@ice0 | enrage_step | 2.842 | 3.158 | +0.316 | [-1.263, +2.000] | +11.1 % | noise |
| boss@ice0 | hp_lost | 54.316 | 52.842 | -1.474 | [-10.326, +8.000] | -2.7 % | noise |
| boss@ice0 | intake | 55.684 | 54.316 | -1.368 | [-13.789, +11.476] | -2.5 % | noise |
| boss@ice0 | parked | 6.684 | 6.158 | -0.526 | [-9.211, +8.268] | -7.9 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 27.211 | +2.368 | [-7.424, +12.211] | +9.5 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 5.865 | -0.240 | [-3.243, +2.963] | -3.9 % | noise |
| boss@ice0 | turns | 20.895 | 22.263 | +1.368 | [-7.368, +9.529] | +6.5 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.248 | +0.004 | [-0.052, +0.060] | +1.8 % | noise |
| boss@ice0 | won | 0.053 | 0.105 | +0.053 | [-0.105, +0.211] | +100.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 17.80 | 46 | 6.2 | 54.3 | 27.2 | 11 | 0.23 |

