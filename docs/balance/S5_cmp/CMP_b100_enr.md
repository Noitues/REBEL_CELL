# Balance comparison: b100_enr

- A: `boss100_base.json` (overrides: none)
- B: `boss100_enrage14_every8.json` (overrides: config.enrage_start_turn_by_class=[0,8,10,14], config.enrage_every_n_turns_by_class=[0,5,5,8])
- mode boss; A 100 records, B 100 records; interval = 2000-resample bootstrap of the difference of means over the seeds, 90 %
- 1 of 30 metrics moved outside the noise (the interval excludes 0)

## Changed outside noise

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | enrage_step | 3.351 | 1.969 | -1.381 | [-2.052, -0.763] | -41.2 % | **CHANGED** |

## Headline metrics

| group | metric | A mean | B mean | delta B-A | 90 % interval | rel. | verdict |
|---|---|---|---|---|---|---|---|
| boss@ice0 | dealt_per_turn | 23.296 | 23.603 | +0.307 | [-3.199, +3.813] | +1.3 % | noise |
| boss@ice0 | died | 0.856 | 0.804 | -0.052 | [-0.144, +0.031] | -6.0 % | noise |
| boss@ice0 | enrage_step | 3.351 | 1.969 | -1.381 | [-2.052, -0.763] | -41.2 % | **CHANGED** |
| boss@ice0 | hp_lost | 54.402 | 52.268 | -2.134 | [-6.124, +1.663] | -3.9 % | noise |
| boss@ice0 | intake | 55.928 | 55.031 | -0.897 | [-7.723, +5.702] | -1.6 % | noise |
| boss@ice0 | parked | 6.948 | 7.144 | +0.196 | [-3.475, +3.774] | +2.8 % | noise |
| boss@ice0 | resistance_absorbed | 28.691 | 30.186 | +1.495 | [-4.156, +6.805] | +5.2 % | noise |
| boss@ice0 | taken_per_turn | 4.994 | 4.861 | -0.133 | [-1.244, +1.024] | -2.7 % | noise |
| boss@ice0 | turns | 23.505 | 25.031 | +1.526 | [-2.289, +5.402] | +6.5 % | noise |
| boss@ice0 | turns_both_share | 0.218 | 0.220 | +0.002 | [-0.029, +0.034] | +0.9 % | noise |
| boss@ice0 | won | 0.062 | 0.082 | +0.021 | [-0.041, +0.082] | +33.3 % | noise |

## Phase metrics (N19), A then B per group

| group | fights | in target (3-4) | turns/phase | heal turns/phase max | parked | intake | resist absorbed | enrage step | both-wheel turns |
|---|---|---|---|---|---|---|---|---|---|
| A boss@ice0 | 97 | 0.02 | 20.63 | 60 | 6.9 | 55.9 | 28.7 | 11 | 0.21 |
| B boss@ice0 | 97 | 0.02 | 19.49 | 60 | 7.1 | 55.0 | 30.2 | 6 | 0.21 |

