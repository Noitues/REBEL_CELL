# Balance comparison: boss_enrage6

- A: `boss_camp_base.json` (overrides: none)
- B: `boss_camp_enrage6.json` (overrides: config.enrage_start_turn_by_class=[0,8,10,6])
- mode boss; A 20 records, B 20 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 0 of 29 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

None: every difference is within noise.

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 19.961 | 20.858 | +0.898 | [-5.134, +6.763] | +4.5 % | noise |
| boss@ice0 | died | 0.895 | 0.947 | +0.053 | [-0.105, +0.211] | +5.9 % | noise |
| boss@ice0 | enrage_step | 2.842 | 2.842 | +0.000 | [-1.474, +1.474] | +0.0 % | noise |
| boss@ice0 | hp_lost | 54.316 | 57.474 | +3.158 | [-4.421, +11.368] | +5.8 % | noise |
| boss@ice0 | intake | 55.684 | 54.526 | -1.158 | [-11.424, +9.374] | -2.1 % | noise |
| boss@ice0 | parked | 6.684 | 3.158 | -3.526 | [-11.476, +2.947] | -52.8 % | noise |
| boss@ice0 | resistance_absorbed | 24.842 | 21.000 | -3.842 | [-13.739, +5.950] | -15.5 % | noise |
| boss@ice0 | taken_per_turn | 6.105 | 6.958 | +0.854 | [-2.154, +3.900] | +14.0 % | noise |
| boss@ice0 | turns | 20.895 | 16.632 | -4.263 | [-12.526, +3.053] | -20.4 % | noise |
| boss@ice0 | turns_both_share | 0.244 | 0.260 | +0.017 | [-0.043, +0.074] | +6.8 % | noise |
| boss@ice0 | won | 0.053 | 0.053 | +0.000 | [-0.105, +0.105] | +0.0 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 19 | 0.00 | 18.67 | 46 | 6.7 | 55.7 | 24.8 | 11 | 0.23 |
| B boss@ice0 | 19 | 0.00 | 18.00 | 46 | 3.2 | 54.5 | 21.0 | 10 | 0.24 |

