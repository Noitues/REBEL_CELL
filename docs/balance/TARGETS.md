# Balance targets (BAL-04, SOLACE_BAL_r1)

Scope: Solace only. Written 2026-10-20. Replaces every earlier bot-based goal. Rule for every number below and in every
balance report: it names its policy (`builtin`, `heuristic, lookahead N`, `reference`). A number without a policy is not a target.

## Policies
- **reference** = `--policy reference` (BAL-01): the heuristic strategist at lookahead 2, deterministic. It is the yardstick
  for goals. It plays about 17-21 damage per turn on normals and is far above a tester (3-5 per turn).
- **builtin** = CombatBot, the Monte Carlo policy. It is a *floor* policy now: its numbers are regress guards, never goals
  (designer ruling 2026-10-19: tuning to the bots makes the game easy for people who play well and wrong for people who do not).
- **tester band** = the Claude / designer play data (BAL-02). Not measured by this tool; a goal only when stated "tester".

## Goals (reference policy)
| number | goal | band | source |
|---|---|---|---|
| Boss win, Genome Core, ICE 0, from saved breach states | about 50 % | 40-60 % at n >= 50 fights | Q29 |
| Boss phases | 3, never fewer | pinned by `test_solace_boss_pins.gd` | Q29 |
| Boss phase thresholds / HP | 66 % / 33 %, HP 400 at T1 | pinned (same test) | Q29 |
| Boss enrage | additive steps (start turn, every N, +pct), never a countdown | pinned (same test) | N4, Q33 |

## Reference bands for the other Solace classes
Measured with `balance.py run fight` (a starter operative, 60 HP, against one foe at tier T, reference policy), pooled over
the category's enemies and seeds. A class is in band when its pooled row is inside every column. There is no sibling
threshold rule (Q46.3): each class has its own numbers. The starter operative is a floor crew; the campaign crew (rank
about 19 at the breach) does better, so a per-enemy win rate under 100 % at T4 here is expected and acceptable.

| class | tier | win % (pooled, min) | turns mean | HP lost mean (of 60) |
|---|---|---|---|---|
| normal | 1 | 95 | 1.5-3.5 | <= 8 |
| normal | 2 | 95 | 2.5-4.5 | <= 12 |
| normal | 3 | 90 | 4-7 | <= 20 |
| normal | 4 | 90 | 6-10 | <= 35 |
| elite | 1 | 95 | 3-6 | <= 10 |
| elite | 2 | 95 | 5-9 | <= 15 |
| elite | 3 | 90 | 8-13 | <= 32 |
| elite | 4 | 75 | 12-22 | <= 45 |
| mini-boss | 1 | 95 | 5-8 | <= 10 |
| mini-boss | 2 | 95 | 7-11 | <= 18 |
| mini-boss | 3 | 90 | 10-16 | <= 35 |
| mini-boss | 4 | 75 | 16-30 | <= 55 |

Per enemy inside a class: win % at least 60 at T4, at least 80 at T1-T3. An enemy under that floor is out of band even
when its class is in band.

## Floors (builtin policy; no regress against the 2026-10-18 measurements)
These are not goals. A change that lowers one of them needs a reason in DECISIONS.
- Boss win at ICE 0, builtin, campaign source: not below 6 % (S5_RESULTS, 97 fights).
- Campaign win at ICE 0, builtin, 20 seeds: not below 25 % (re-baselined 2026-10-20 from 50 %: after W0 N1, 324c7751, the tier-scaled Auto-Renew stalls the builtin bot at about 30 %; see `docs/handoff/plan2/balance/Q9_builtin.md`. The boss is tuned on the reference policy.)
- Fights in a builtin campaign: normals T1-T3 win >= 98 %, elites T1-T3 >= 94 %, mini-bosses T1-T3 >= 80 %.

## Pace (GDD 11.8)
Average campaign about 24 runs, about 395 minutes at 15 min per run and 5 per raid. Measured on `--policy heuristic --lookahead 1`
(12 seeds: 29 runs, 454 min after SOLACE_BAL_r2; 49 runs, 751 min before). The reference policy (lookahead 2) is an expert and plays
the GDD fast campaign (9 to 11 runs, 135 to 180 min); see SOLACE_BAL_r2. Raids: about 3 (fast) to 7 (average) per campaign.
