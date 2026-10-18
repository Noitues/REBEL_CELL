# Balance comparison: boss_every8

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_every8.json` (overrides: config.enrage_every_n_turns_by_class=[0,5,5,8])
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 19.945 | -0.015 | [-6.122, +5.942] | -0.1 % | noise |
| boss@ice0 | died | 0.895 | 0.842 | -0.053 | [-0.211, +0.105] | -5.9 % | noise |
| boss@ice0 | enrage_step | 2.842 | 2.053 | -0.789 | [-2.158, +0.632] | -27.8 % | noise |
| boss@ice0 | hp_lost | 54.316 | 52.842 | -1.474 | [-10.326, +8.000] | -2.7 % | noise |
| boss@ice0 | intake | 55.684 | 53.211 | -2.474 | [-14.371, +9.947] | -4.4 % | noise |
| boss@ice0 | parked | 6.684 | 6.158 | -0.526 | [-9.211, +8.268] | -7.9 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 25.421 | +0.579 | [-9.266, +10.789] | +2.3 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 6.019 | -0.086 | [-3.058, +3.092] | -1.4 % | noise |
| boss@ice0 | turns | 20.895 | 21.316 | +0.421 | [-8.318, +8.737] | +2.0 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.241 | -0.002 | [-0.059, +0.053] | -1.0 % | noise |
| boss@ice0 | won | 0.053 | 0.105 | +0.053 | [-0.105, +0.211] | +100.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 17.80 | 46 | 6.2 | 53.2 | 25.4 | 7 | 0.23 |

