# Balance baseline @ e2e13918

Reference for `balance.py compare`. Content = main @ 820e94b6 (no content edits); tooling = this commit.
Policy: built-in bot (CombatBot), skill 1.0, class breaker vs Solace, `-j 2`, seeds 1000..1019 (boss 1000..1007).
Raw merged records: `BASELINE_e2e13918/<name>.json`. Regenerate: `python tools/balance/balance.py run <mode> --name <name> ...`
(the exact arguments are in each section's header: `args`). Overrides: none.

## Campaign, ICE 0 (20 seeds, built-in bot)

- policy: builtin, skill 1.0, ICE 0, corp solace, class breaker
- seeds: 20 (1000..1019), records: 20
- overrides: none (content as committed)
- wall time: 744.8 s with -j 2

### campaign@ice0

Win rate **50.0 %** over 20 campaigns (loss 0.0 %).

| metric | mean | median | p10 | p90 |
|---|---|---|---|---|
| runs | 38.6 | 51.0 | 9.0 | 60.0 |
| completed runs | 26.6 | 30.0 | 9.0 | 42.1 |
| deaths | 10.5 | 13.5 | 0.0 | 19.1 |
| raids | 5.2 | 5.5 | 2.0 | 7.1 |
| raids won | 1.6 | 1.0 | 0.0 | 3.2 |
| raids lost | 3.6 | 4.0 | 1.9 | 6.1 |
| Heat peak | 84.4 | 100.0 | 45.8 | 100.0 |
| Heat at end | 52.4 | 57.0 | 0.0 | 100.0 |
| Heat at breach | 54.5 | 51.0 | 4.5 | 95.5 |
| minutes (GDD 11.8: ~395) | 605 | 793 | 145 | 935 |
| fights | 203.2 | 247.0 | 50.9 | 331.1 |
| raids from flatline Heat | 0.75 | 1.00 | 0.00 | 2.00 |
| raids from Heat of actions | 2.35 | 2.50 | 1.00 | 3.10 |
| raids from other sources | 0.90 | 1.00 | 0.00 | 2.00 |
| Schematics income | 1410 | 1554 | 496 | 2255 |
| Schematics spent | 1238 | 1440 | 149 | 2120 |
| Schematics unspent at end | 191 | 136 | 65 | 398 |
| operatives recruited | 10.2 | 13.5 | 0.0 | 19.0 |
| layers per run | 6.01 | 6.04 | 5.75 | 6.34 |
| heal HP per run | 1.67 | 2.00 | 0.32 | 2.54 |
| heals available per run | 1.94 | 1.98 | 1.77 | 2.09 |
| heals used per run | 0.37 | 0.38 | 0.26 | 0.50 |
| stuck fights | 1.45 | 0.00 | 0.00 | 3.10 |

### Heat after run N

| run | mean | median | p10 | p90 | n campaigns |
|---|---|---|---|---|---|
| 1 | 3.8 | 4.0 | 2.0 | 6.0 | 20 |
| 3 | 36.9 | 37.0 | 24.8 | 46.0 | 20 |
| 5 | 41.2 | 45.5 | 26.2 | 53.2 | 20 |
| 8 | 44.0 | 49.0 | 13.0 | 59.2 | 20 |
| 12 | 68.9 | 72.5 | 28.2 | 99.0 | 14 |
| 16 | 68.6 | 84.0 | 14.0 | 100.0 | 14 |
| 20 | 77.1 | 96.0 | 33.9 | 100.0 | 14 |
| 25 | 86.1 | 97.0 | 52.5 | 100.0 | 12 |
| 30 | 82.8 | 95.0 | 53.0 | 100.0 | 12 |
| 40 | 97.7 | 100.0 | 92.0 | 100.0 | 11 |
| 50 | 89.7 | 100.0 | 87.3 | 100.0 | 10 |
| 60 | 69.7 | 82.5 | 16.2 | 100.0 | 10 |

### HP on arrival per layer (fraction of max HP, mean [p10-p90])

| tier | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|---|---|---|---|---|---|---|---|
| T1 | 1.00 [1.00-1.00] n=275 | 0.93 [0.80-1.00] n=275 | 0.88 [0.70-1.00] n=275 | 0.80 [0.58-1.00] n=275 | 0.70 [0.43-1.00] n=275 | 0.66 [0.37-0.98] n=275 | 0.59 [0.27-0.95] n=273 |
| T2 | 1.00 [1.00-1.00] n=205 | 0.92 [0.74-1.00] n=205 | 0.86 [0.67-1.00] n=205 | 0.76 [0.47-1.00] n=205 | 0.69 [0.33-1.00] n=201 | 0.67 [0.30-1.00] n=199 | 0.63 [0.27-0.97] n=192 |
| T3 | 1.00 [1.00-1.00] n=169 | 0.88 [0.65-1.00] n=169 | 0.81 [0.48-1.00] n=168 | 0.72 [0.34-1.00] n=166 | 0.64 [0.22-0.98] n=160 | 0.62 [0.17-0.97] n=150 | 0.59 [0.15-0.97] n=141 |

### Fights in the campaigns (category.tier)

| category.tier | fights | turns mean | turns p90 | HP lost mean | win % |
|---|---|---|---|---|---|
| boss.t4 | 123 | 41.2 | 60.0 | 49.9 | 8 |
| elite.t1 | 474 | 4.7 | 8.0 | 6.9 | 100 |
| elite.t2 | 339 | 4.8 | 8.0 | 6.2 | 98 |
| elite.t3 | 253 | 7.5 | 12.0 | 7.6 | 94 |
| enemy.t1 | 972 | 2.5 | 4.0 | 3.8 | 100 |
| enemy.t2 | 712 | 2.7 | 4.0 | 4.4 | 99 |
| enemy.t3 | 586 | 3.8 | 5.0 | 6.2 | 98 |
| mini_boss.t1 | 273 | 7.2 | 11.0 | 9.1 | 87 |
| mini_boss.t2 | 192 | 7.1 | 10.0 | 7.2 | 90 |
| mini_boss.t3 | 141 | 10.1 | 13.0 | 10.0 | 80 |


## Campaign, ICE 5 (20 seeds, built-in bot)

- policy: builtin, skill 1.0, ICE 5, corp solace, class breaker
- seeds: 20 (1000..1019), records: 20
- overrides: none (content as committed)
- wall time: 821.0 s with -j 2

### campaign@ice5

Win rate **35.0 %** over 20 campaigns (loss 10.0 %).

| metric | mean | median | p10 | p90 |
|---|---|---|---|---|
| runs | 39.8 | 60.0 | 9.9 | 60.0 |
| completed runs | 24.9 | 24.0 | 9.0 | 40.0 |
| deaths | 10.1 | 8.5 | 0.0 | 21.0 |
| raids | 6.1 | 6.5 | 2.9 | 8.1 |
| raids won | 1.2 | 1.0 | 0.0 | 3.0 |
| raids lost | 4.9 | 5.0 | 2.0 | 7.2 |
| Heat peak | 87.6 | 100.0 | 45.9 | 100.0 |
| Heat at end | 66.8 | 78.5 | 0.0 | 100.0 |
| Heat at breach | 59.3 | 60.0 | 27.2 | 96.0 |
| minutes (GDD 11.8: ~395) | 627 | 925 | 165 | 940 |
| fights | 196.2 | 198.5 | 53.8 | 327.5 |
| raids from flatline Heat | 0.90 | 1.00 | 0.00 | 2.00 |
| raids from Heat of actions | 2.35 | 2.00 | 1.00 | 3.10 |
| raids from other sources | 1.30 | 1.00 | 0.00 | 2.10 |
| Schematics income | 1336 | 1234 | 487 | 2173 |
| Schematics spent | 1196 | 1150 | 306 | 2036 |
| Schematics unspent at end | 160 | 136 | 65 | 264 |
| operatives recruited | 9.8 | 8.5 | 0.0 | 20.1 |
| layers per run | 5.68 | 5.87 | 5.30 | 6.34 |
| heal HP per run | 1.65 | 1.30 | 0.08 | 2.56 |
| heals available per run | 1.71 | 1.79 | 1.53 | 2.00 |
| heals used per run | 0.31 | 0.28 | 0.11 | 0.51 |
| stuck fights | 4.85 | 2.00 | 0.00 | 9.70 |

### Heat after run N

| run | mean | median | p10 | p90 | n campaigns |
|---|---|---|---|---|---|
| 1 | 4.2 | 4.0 | 2.0 | 5.1 | 20 |
| 3 | 44.4 | 47.0 | 32.8 | 52.1 | 20 |
| 5 | 48.2 | 50.5 | 24.4 | 65.0 | 20 |
| 8 | 51.0 | 55.0 | 13.7 | 84.4 | 20 |
| 12 | 66.1 | 74.5 | 23.0 | 100.0 | 16 |
| 16 | 71.4 | 87.5 | 38.5 | 100.0 | 16 |
| 20 | 79.3 | 100.0 | 44.4 | 100.0 | 13 |
| 25 | 79.9 | 95.0 | 42.0 | 100.0 | 11 |
| 30 | 76.1 | 91.0 | 41.0 | 100.0 | 11 |
| 40 | 81.8 | 95.0 | 43.0 | 100.0 | 11 |
| 50 | 84.4 | 100.0 | 43.0 | 100.0 | 11 |
| 60 | 77.4 | 99.0 | 43.0 | 100.0 | 11 |

### HP on arrival per layer (fraction of max HP, mean [p10-p90])

| tier | L1 | L2 | L3 | L4 | L5 | L6 | L7 |
|---|---|---|---|---|---|---|---|
| T1 | 1.00 [1.00-1.00] n=266 | 0.93 [0.78-1.00] n=266 | 0.87 [0.69-1.00] n=266 | 0.79 [0.54-1.00] n=266 | 0.68 [0.36-0.99] n=265 | 0.64 [0.28-0.97] n=263 | 0.58 [0.23-0.95] n=262 |
| T2 | 1.00 [1.00-1.00] n=191 | 0.92 [0.77-1.00] n=191 | 0.87 [0.70-1.00] n=191 | 0.80 [0.57-1.00] n=191 | 0.72 [0.37-1.00] n=189 | 0.68 [0.33-1.00] n=186 | 0.65 [0.27-1.00] n=181 |
| T3 | 1.00 [1.00-1.00] n=154 | 0.89 [0.67-1.00] n=154 | 0.83 [0.55-1.00] n=152 | 0.74 [0.42-1.00] n=150 | 0.65 [0.28-1.00] n=144 | 0.63 [0.23-1.00] n=137 | 0.60 [0.21-0.93] n=127 |

### Fights in the campaigns (category.tier)

| category.tier | fights | turns mean | turns p90 | HP lost mean | win % |
|---|---|---|---|---|---|
| boss.t4 | 185 | 50.1 | 60.0 | 38.3 | 4 |
| elite.t1 | 499 | 4.6 | 7.0 | 6.8 | 99 |
| elite.t2 | 337 | 4.8 | 8.0 | 6.0 | 98 |
| elite.t3 | 238 | 7.1 | 11.0 | 8.2 | 93 |
| enemy.t1 | 913 | 2.5 | 4.0 | 3.9 | 100 |
| enemy.t2 | 657 | 2.7 | 4.0 | 4.0 | 100 |
| enemy.t3 | 524 | 3.8 | 5.0 | 5.8 | 98 |
| mini_boss.t1 | 262 | 7.3 | 11.0 | 9.7 | 84 |
| mini_boss.t2 | 181 | 7.0 | 10.0 | 5.4 | 91 |
| mini_boss.t3 | 127 | 9.9 | 13.0 | 8.7 | 83 |


## Fight sweep (every Solace enemy x tier 1-4 x 20 seeds, starter operative)

- policy: builtin, skill 1.0, ICE 0, corp solace, class breaker
- seeds: 20 (1000..1019), records: 720
- overrides: none (content as committed)
- wall time: 125.5 s with -j 2

### Tier 1

| enemy | category | n | win % | turns mean | median | p90 | HP lost mean | p90 | dealt/turn | taken/turn | Perfect % | heal turns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| account_manager | mini_boss | 20 | 100 | 6.7 | 6 | 8 | 11.8 | 21 | 23.4 | 1.75 | 89 | 0.0 |
| billing_daemon | enemy | 20 | 100 | 2.5 | 2 | 3 | 2.9 | 7 | 17.7 | 1.22 | 83 | 0.0 |
| care_swarm | enemy | 20 | 100 | 3.0 | 3 | 5 | 12.5 | 18 | 11.2 | 4.86 | 92 | 0.4 |
| claims_adjuster | elite | 20 | 100 | 3.1 | 3 | 4 | 5.6 | 11 | 39.1 | 1.86 | 94 | 0.0 |
| collections_agent | enemy | 20 | 100 | 2.5 | 2 | 4 | 4.3 | 9 | 17.1 | 1.79 | 88 | 0.0 |
| compliance_officer | enemy | 20 | 100 | 3.0 | 3 | 4 | 7.2 | 11 | 17.8 | 2.54 | 94 | 0.0 |
| dosage_dispenser | enemy | 20 | 100 | 2.5 | 2 | 3 | 0.1 | 0 | 16.3 | 0.05 | 87 | 0.0 |
| recall_unit | elite | 20 | 100 | 6.5 | 6 | 8 | 6.1 | 13 | 16.6 | 0.97 | 87 | 0.0 |
| triage_unit | enemy | 20 | 100 | 2.9 | 3 | 3 | 1.1 | 3 | 16.6 | 0.39 | 84 | 0.7 |

### Tier 2

| enemy | category | n | win % | turns mean | median | p90 | HP lost mean | p90 | dealt/turn | taken/turn | Perfect % | heal turns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| account_manager | mini_boss | 20 | 100 | 11.4 | 11 | 13 | 22.8 | 32 | 22.3 | 2.03 | 89 | 0.0 |
| billing_daemon | enemy | 20 | 100 | 4.2 | 4 | 5 | 5.3 | 13 | 17.3 | 1.36 | 91 | 0.0 |
| care_swarm | enemy | 20 | 100 | 4.2 | 4 | 7 | 23.6 | 33 | 11.3 | 6.08 | 84 | 0.5 |
| claims_adjuster | elite | 20 | 100 | 5.2 | 5 | 7 | 9.3 | 19 | 36.9 | 1.98 | 92 | 0.0 |
| collections_agent | enemy | 20 | 100 | 3.9 | 4 | 5 | 9.8 | 14 | 17.2 | 2.60 | 86 | 0.0 |
| compliance_officer | enemy | 20 | 100 | 5.1 | 5 | 6 | 13.4 | 24 | 16.5 | 2.62 | 85 | 0.0 |
| dosage_dispenser | enemy | 20 | 100 | 3.6 | 3 | 5 | 1.5 | 3 | 17.7 | 0.39 | 88 | 0.0 |
| recall_unit | elite | 20 | 100 | 11.2 | 10 | 14 | 12.3 | 21 | 15.9 | 1.16 | 87 | 0.0 |
| triage_unit | enemy | 20 | 100 | 4.2 | 4 | 6 | 2.2 | 4 | 18.5 | 0.55 | 88 | 1.0 |

### Tier 3

| enemy | category | n | win % | turns mean | median | p90 | HP lost mean | p90 | dealt/turn | taken/turn | Perfect % | heal turns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| account_manager | mini_boss | 20 | 90 | 20.7 | 20 | 26 | 40.2 | 57 | 19.4 | 1.95 | 82 | 0.0 |
| billing_daemon | enemy | 20 | 100 | 7.0 | 7 | 9 | 9.2 | 16 | 16.0 | 1.31 | 90 | 0.0 |
| care_swarm | enemy | 20 | 85 | 6.5 | 6 | 9 | 43.0 | 60 | 10.6 | 6.91 | 89 | 0.8 |
| claims_adjuster | elite | 20 | 100 | 8.8 | 9 | 11 | 19.5 | 35 | 33.8 | 2.18 | 90 | 0.0 |
| collections_agent | enemy | 20 | 100 | 5.8 | 6 | 7 | 15.4 | 21 | 18.4 | 2.78 | 92 | 0.0 |
| compliance_officer | enemy | 20 | 95 | 7.9 | 8 | 10 | 26.2 | 49 | 16.6 | 3.50 | 94 | 0.0 |
| dosage_dispenser | enemy | 20 | 100 | 5.2 | 5 | 7 | 2.9 | 6 | 19.1 | 0.56 | 90 | 0.0 |
| recall_unit | elite | 20 | 100 | 20.2 | 19 | 25 | 27.6 | 39 | 14.2 | 1.45 | 80 | 0.0 |
| triage_unit | enemy | 20 | 100 | 7.4 | 7 | 9 | 4.8 | 9 | 16.3 | 0.69 | 84 | 2.2 |

### Tier 4

| enemy | category | n | win % | turns mean | median | p90 | HP lost mean | p90 | dealt/turn | taken/turn | Perfect % | heal turns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| account_manager | mini_boss | 20 | 20 | 30.9 | 31 | 35 | 57.9 | 60 | 18.0 | 1.91 | 79 | 0.0 |
| billing_daemon | enemy | 20 | 100 | 10.8 | 11 | 13 | 18.4 | 26 | 16.5 | 1.73 | 88 | 0.0 |
| care_swarm | enemy | 20 | 0 | 6.5 | 6 | 8 | 60.0 | 60 | 11.1 | 9.78 | 89 | 0.7 |
| claims_adjuster | elite | 20 | 85 | 14.9 | 14 | 19 | 37.2 | 60 | 31.2 | 2.56 | 90 | 0.0 |
| collections_agent | enemy | 20 | 100 | 9.9 | 10 | 12 | 36.9 | 46 | 17.0 | 3.79 | 92 | 0.0 |
| compliance_officer | enemy | 20 | 70 | 12.6 | 12 | 15 | 51.5 | 60 | 16.1 | 4.40 | 90 | 0.0 |
| dosage_dispenser | enemy | 20 | 100 | 8.0 | 8 | 10 | 6.6 | 9 | 20.1 | 0.84 | 92 | 0.0 |
| recall_unit | elite | 20 | 65 | 36.0 | 35 | 43 | 46.0 | 60 | 11.7 | 1.35 | 70 | 0.0 |
| triage_unit | enemy | 20 | 100 | 12.8 | 14 | 15 | 9.7 | 16 | 14.8 | 0.77 | 82 | 3.9 |

### By enemy category and tier (pooled over enemies and seeds)

| category | tier | fights | turns mean | median | p90 | HP lost mean | win % |
|---|---|---|---|---|---|---|---|
| elite | 1 | 40 | 4.8 | 5 | 7 | 5.8 | 100 |
| elite | 2 | 40 | 8.2 | 8 | 12 | 10.8 | 100 |
| elite | 3 | 40 | 14.5 | 13 | 24 | 23.6 | 100 |
| elite | 4 | 40 | 25.5 | 22 | 42 | 41.6 | 75 |
| enemy | 1 | 120 | 2.7 | 3 | 4 | 4.7 | 100 |
| enemy | 2 | 120 | 4.2 | 4 | 6 | 9.3 | 100 |
| enemy | 3 | 120 | 6.6 | 7 | 9 | 16.9 | 97 |
| enemy | 4 | 120 | 10.1 | 10 | 14 | 30.5 | 78 |
| mini_boss | 1 | 20 | 6.7 | 6 | 8 | 11.8 | 100 |
| mini_boss | 2 | 20 | 11.4 | 11 | 13 | 22.8 | 100 |
| mini_boss | 3 | 20 | 20.7 | 20 | 26 | 40.2 | 90 |
| mini_boss | 4 | 20 | 30.9 | 31 | 35 | 57.9 | 20 |


## Boss (8 campaigns played to the breach)

- policy: builtin, skill 1.0, ICE 0, corp solace, class breaker
- seeds: 8 (1000..1007), records: 8
- overrides: none (content as committed)
- wall time: 155.3 s with -j 2

### boss@ice0

Win rate **25.0 %** over 8 fights (no breach reached: 0).

| metric | mean | median | p10 | p90 |
|---|---|---|---|---|
| turns, total | 38.1 | 35.0 | 22.3 | 58.6 |
| phases | 2.9 | 3.0 | 2.7 | 3.0 |
| turns in phase 1 | 17.4 | 17.5 | 11.1 | 23.3 |
| turns in phase 2 | 12.9 | 13.5 | 5.1 | 20.3 |
| turns in phase 3 | 9.0 | 5.0 | 2.2 | 20.8 |
| operative HP at the end | 8.9 | 0.0 | 0.0 | 26.6 |
| HP lost (fraction) | 0.85 | 1.00 | 0.56 | 1.00 |
| damage dealt per turn | 35.2 | 26.4 | 21.5 | 56.8 |
| damage taken per turn | 2.08 | 1.55 | 1.35 | 3.18 |
| Perfect rate | 0.97 | 0.98 | 0.93 | 1.00 |
| boss heal turns | 37.2 | 34.0 | 21.3 | 57.9 |
| operative rank | 6.8 | 8.0 | 3.7 | 8.0 |
| operative max HP | 60.0 | 60.0 | 60.0 | 60.0 |
| deck size | 16.0 | 16.0 | 16.0 | 16.0 |
| Heat at breach | 46.6 | 44.5 | 13.0 | 73.0 |

### Curves by turn (fights still running)

| turn | boss HP frac mean | median | p10 | p90 | operative HP mean | n |
|---|---|---|---|---|---|---|
| 1 | 0.99 | 0.99 | 0.98 | 0.99 | 60 | 8 |
| 2 | 0.97 | 0.97 | 0.95 | 0.99 | 56 | 8 |
| 3 | 0.95 | 0.95 | 0.91 | 0.97 | 51 | 8 |
| 5 | 0.90 | 0.91 | 0.85 | 0.95 | 50 | 8 |
| 8 | 0.84 | 0.85 | 0.77 | 0.89 | 48 | 8 |
| 10 | 0.78 | 0.79 | 0.70 | 0.86 | 47 | 8 |
| 15 | 0.63 | 0.71 | 0.43 | 0.77 | 43 | 8 |
| 20 | 0.59 | 0.65 | 0.39 | 0.71 | 43 | 7 |
| 25 | 0.47 | 0.55 | 0.23 | 0.62 | 36 | 7 |
| 30 | 0.48 | 0.49 | 0.45 | 0.52 | 46 | 4 |
| 40 | 0.32 | 0.33 | 0.27 | 0.36 | 32 | 4 |
| 50 | 0.18 | 0.18 | 0.11 | 0.26 | 15 | 2 |
| 60 | 0.25 | 0.25 | 0.25 | 0.25 | 13 | 1 |


## Netrun, tier 1 from a fresh start (20 seeds)

- policy: builtin, skill 1.0, ICE 0, corp solace, class breaker
- seeds: 20 (1000..1019), records: 20
- overrides: none (content as committed)
- wall time: 35.3 s with -j 2

### netrun@t1

Death rate **10.0 %** over 20 runs.

| metric | mean | median | p10 | p90 |
|---|---|---|---|---|
| layers reached | 7.00 | 7.00 | 7.00 | 7.00 |
| HP at end (fraction) | 0.44 | 0.43 | 0.24 | 0.73 |
| Cycles | 171 | 164 | 151 | 193 |
| heal HP gained | 0.6 | 0.0 | 0.0 | 0.4 |
| heals available (Terminals) | 2.30 | 2.00 | 1.90 | 3.00 |
| heals used | 0.40 | 0.00 | 0.00 | 1.00 |

### HP on arrival per layer (fraction of max HP)

| layer | mean | median | p10 | p90 | n |
|---|---|---|---|---|---|
| L1 | 1.00 | 1.00 | 1.00 | 1.00 | 20 |
| L2 | 0.91 | 0.93 | 0.81 | 1.00 | 20 |
| L3 | 0.86 | 0.83 | 0.73 | 1.00 | 20 |
| L4 | 0.79 | 0.80 | 0.60 | 1.00 | 20 |
| L5 | 0.70 | 0.69 | 0.51 | 0.89 | 20 |
| L6 | 0.63 | 0.62 | 0.40 | 0.87 | 20 |
| L7 | 0.56 | 0.57 | 0.25 | 0.77 | 20 |

### Fights in the campaigns (category.tier)

| category.tier | fights | turns mean | turns p90 | HP lost mean | win % |
|---|---|---|---|---|---|
| elite.t1 | 38 | 4.7 | 7.3 | 5.8 | 100 |
| enemy.t1 | 72 | 2.7 | 4.0 | 4.3 | 100 |
| mini_boss.t1 | 20 | 6.4 | 8.1 | 8.3 | 90 |


## Netrun, tier 2 from a fresh start (20 seeds)

- policy: builtin, skill 1.0, ICE 0, corp solace, class breaker
- seeds: 20 (1000..1019), records: 20
- overrides: none (content as committed)
- wall time: 50.4 s with -j 2

### netrun@t2

Death rate **60.0 %** over 20 runs.

| metric | mean | median | p10 | p90 |
|---|---|---|---|---|
| layers reached | 6.50 | 7.00 | 5.00 | 7.00 |
| HP at end (fraction) | 0.29 | 0.30 | 0.10 | 0.51 |
| Cycles | 231 | 246 | 160 | 290 |
| heal HP gained | 0.8 | 0.0 | 0.0 | 1.3 |
| heals available (Terminals) | 2.30 | 2.00 | 1.90 | 3.00 |
| heals used | 0.55 | 1.00 | 0.00 | 1.00 |

### HP on arrival per layer (fraction of max HP)

| layer | mean | median | p10 | p90 | n |
|---|---|---|---|---|---|
| L1 | 1.00 | 1.00 | 1.00 | 1.00 | 20 |
| L2 | 0.84 | 0.87 | 0.62 | 1.00 | 20 |
| L3 | 0.77 | 0.78 | 0.53 | 0.96 | 20 |
| L4 | 0.62 | 0.54 | 0.38 | 0.88 | 20 |
| L5 | 0.50 | 0.50 | 0.29 | 0.73 | 19 |
| L6 | 0.45 | 0.43 | 0.18 | 0.74 | 17 |
| L7 | 0.42 | 0.38 | 0.17 | 0.73 | 14 |

### Fights in the campaigns (category.tier)

| category.tier | fights | turns mean | turns p90 | HP lost mean | win % |
|---|---|---|---|---|---|
| elite.t2 | 32 | 7.9 | 12.8 | 10.3 | 97 |
| enemy.t2 | 71 | 4.1 | 6.0 | 7.3 | 93 |
| mini_boss.t2 | 14 | 10.4 | 12.0 | 10.3 | 57 |

