# Balance comparison: boss_e6_every3_hp050

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_e6_every3_hp050.json` (overrides: config.enrage_start_turn_by_class=[0,8,10,6], config.enrage_every_n_turns_by_class=[0,5,5,3], renewal_engine.hp*=0.5)
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 1 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | turns_phase_1 | 16.211 | 10.947 | -5.263 | [-9.526, -0.997] | -32.5 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 19.554 | -0.407 | [-6.195, +5.196] | -2.0 % | noise |
| boss@ice0 | died | 0.895 | 0.895 | +0.000 | [-0.158, +0.158] | +0.0 % | noise |
| boss@ice0 | enrage_step | 2.842 | 3.632 | +0.789 | [-0.947, +2.737] | +27.8 % | noise |
| boss@ice0 | hp_lost | 54.316 | 55.000 | +0.684 | [-7.500, +8.897] | +1.3 % | noise |
| boss@ice0 | intake | 55.684 | 52.474 | -3.211 | [-14.211, +7.739] | -5.8 % | noise |
| boss@ice0 | parked | 6.684 | 8.105 | +1.421 | [-7.897, +10.950] | +21.3 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 18.895 | -5.947 | [-15.266, +3.263] | -23.9 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 6.994 | +0.889 | [-2.145, +3.951] | +14.6 % | noise |
| boss@ice0 | turns | 20.895 | 14.842 | -6.053 | [-13.895, +1.055] | -29.0 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.272 | +0.028 | [-0.027, +0.084] | +11.4 % | noise |
| boss@ice0 | won | 0.053 | 0.105 | +0.053 | [-0.105, +0.211] | +100.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 12.92 | 24 | 8.1 | 52.5 | 18.9 | 17 | 0.26 |

