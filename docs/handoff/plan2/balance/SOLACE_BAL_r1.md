# SOLACE_BAL_r1: Solace balance pass (BAL-03 / 04 / 05)

2026-10-20, branch `sol-bal`, base main @ 3c3f88d6. Scope: Solace only, class breaker, ICE 0.
Every number names its policy. **reference** = `--policy reference` (heuristic strategist, lookahead 2). **builtin** = CombatBot.
Raw reports: `D:/rc_tmp/solbal/runs/*.md|json` (not committed; the numbers below are copied from them).

## What shipped
| item | result |
|---|---|
| BAL-03 | `balance.py run boss --source save --state FILE|DIR` (boss from a saved campaign state); `--source campaign --dump-state DIR` writes the breach states. Tool-only, no game code. Saved-state fight of seed 1001 equals its campaign-source fight (same 56 turns, same HP curve). `--trace FILE` added for campaign mode (one line per run, fight, action). |
| BAL-04 | `docs/balance/TARGETS.md` (new; there was no targets file): policy per number, builtin numbers as floors, 50 % boss win on reference, class bands, pace. |
| BAL-05 boss | Genome Core (`renewal_engine`) HP 360 -> 400. Phases (3), thresholds (66 / 33 %), enrage (additive 25 % steps) unchanged and pinned by new `tests/unit/test_solace_boss_pins.gd`. |
| BAL-05 elite / mini-boss | Claims Adjuster 112 -> 96 HP, Account Manager 150 -> 128 HP. |
| BAL-05 normals | Care Swarm: tune measured, **not shipped** (see Still open). |
| Theme numbers | Unchanged (see Campaign pace). |

## Boss, reference policy, ICE 0, saved breach states
Crews: 25 breach states from reference campaigns (seeds 1001-1031; 6 of 30 campaigns never reached the breach). Each state is
fought with several combat seeds. Win / died / cap = won, operative died, 60-turn cap reached (counted as a non-win).

| content | n fights | win % | died | cap | turns mean / median / p90 |
|---|---|---|---|---|---|
| BEFORE: HP 360 (campaign source, 24 fights) | 24 | 58.3 | n/a | n/a | 37.1 / 32 / 60 |
| BEFORE: HP 360 (saved states, other combat seeds) | 25 | 56.0 | 5 | 6 | 37.8 / 33 / 60 |
| HP 360 x 1.1 | 25 | 52.0 | 5 | 7 | 40.1 / 35 / 60 |
| HP 360 x 1.2 | 25 | 52.0 | 6 | 6 | 40.7 / 36 / 60 |
| **AFTER: HP 400 (shipped)** | **50** | **52.0** | 12 | 12 | 39.7 / 35.5 / 60 |

Pooled BEFORE (HP 360): 28 / 49 = 57 % (95 % interval about +-14). AFTER: 26 / 50 = 52 % (about +-14). Both are inside the
40-60 % band, so the 50 % goal is met within the sample's resolution; the nudge moves the point estimate by 5 points and is
not statistically distinguishable from no change. HP x1.2 did no better than x1.1, so the shipped step is the smaller one.
Phase turns AFTER (mean): 19.7 / 13.7 / 8.1; the boss heals on 38.6 of 39.7 turns (Auto-Renew), unchanged. Operative arrives with
rank 18.6, 60 max HP, and ends with 27 HP on average.
Enrage was not changed: HP alone put the win rate in band, and S5 showed enrage start / step / interval were inside noise.
Builtin policy for reference only: boss win 6 % (S5_RESULTS, 97 fights), a floor, not re-measured.

## Fights, reference policy (starter operative, 60 HP, one foe, seeds 1000-1004; pooled per category)
BEFORE = shipped content before this pass. AFTER = with the Claims Adjuster and Account Manager HP change; care_swarm
unchanged, so normals and T1-T3 elites are identical to BEFORE.

| class | tier | n | win % | turns | HP lost | band (TARGETS.md) |
|---|---|---|---|---|---|---|
| normal | 1 | 30 | 100 | 2.2 | 3.2 | in |
| normal | 2 | 30 | 100 | 3.2 | 6.3 | in |
| normal | 3 | 30 | 100 | 5.2 | 10.4 | in |
| normal | 4 | 30 | 86.7 | 8.1 | 19.6 | win under 90: out (Care Swarm 20 %, rest 100 %) |
| elite | 1 / 2 / 3 | 10 each | 100 | 3.9 / 6.5 / 10.6 | 5.4 / 9.5 / 27.9 | in |
| elite | 4 | 10 | 80 | 18.0 | 30.6 | in (pooled) |
| mini-boss | 1 / 2 / 3 | 5 each | 100 | 6.0 / 9.0 / 14.6 | 6.0 / 13.6 / 30.4 | in |
| mini-boss | 4 | 5 | 80 | 30.0 | 53.6 | in (thin sample) |

T4 per enemy, 15 fights each (seeds 1000-1014), BEFORE vs AFTER (HP x0.85, measured with `--set`, shipped as 96 / 128):

| enemy (T4) | win % BEFORE | win % AFTER | turns | HP lost AFTER | floor |
|---|---|---|---|---|---|
| claims_adjuster (elite) | 53 | 67 | 11.5 | 46.3 | 60 : now in |
| account_manager (mini-boss) | 67 | 80 | 23.3 | 42.0 | 60 : in before, mini-boss pooled 75 floor now met |
| recall_unit (elite, 15 fights) | 100 | unchanged | 24.4 | 17.5 | in |

The 15-seed AFTER rows use the override on a copy of the content; the shipped `.tres` values are the same within rounding
(95.2 -> 96, 127.5 -> 128). The 5-seed table above was not re-run after the HP change (hours of CPU at lookahead 2); the T1-T3
numbers of these two enemies get easier and stay in band.

## Campaign pace (GDD 11.8: about 24 runs, about 395 minutes)
**The campaign numbers use cheaper setups than the full reference run.** Reference campaigns cost 30 to 150 minutes each at
about 3-5 s per planning step (the seed 1007 run was slow, not hung: it was in run 41 and its HQ boss fight at 60 turns when
stopped; seed 1009 likewise). So: reference on 8 seeds (1000-1006, 1008; seeds 1007 and 1009 killed), builtin on 8 seeds.

| policy | seeds | win % | runs mean | minutes mean | raids | deaths |
|---|---|---|---|---|---|---|
| reference (HP 400 content) | 8 | 75 (6 / 8, rest hit the 60-run cap) | 45.4 | 700 (375 to 930) | 4.0 | 0.4 |
| builtin, shipped content | 8 | 25 | 58.9 | 916 | 6.6 | 16.8 |
| builtin, pre-pass numbers (via `--set`) | 8 | 25 | 53.5 | 834 | n/a | 16.2 |

Reading: the pass did not move the builtin campaign win (25 % both ways at n=8). The builtin floor in TARGETS.md (50 %,
BASELINE_e2e13918) is not met on today's main; the drop predates this pass (the pre-pass-numbers row is also 25 %), so it
comes from other main changes since the baseline (not investigated). The reference policy rarely dies (0.4 per campaign), so
the Bloom, its turn cost and infection are not what stretches the campaign. The length is the run count: 24-60 runs, mean 45
against 24, driven by the Exploit sites and rank gating (3 Exploits for the breach, Tier needs Rank), which are shared rules. **No
Solace theme number was changed** (no evidence they bind; moving shared pace levers is outside "Solace only"). Out of band.

## Findings that need someone else
1. **Latent view-timing failure:** `tests/unit/test_anim_r2_combat.gd::test_hits_fly_one_at_a_time_and_the_result_holds_before_the_respin`
   fails (care_swarm: "THIS TURN once every HP roll has finished") whenever Care Swarm dies sooner (HP 20, HP 22, or 20 HP with
   2 satellites; fails alone too). It passes on the shipped numbers. The animation owner should look at the schedule for a
   combat that ends within the turn; this blocks the Care Swarm tune.
2. **Disk/CPU cost:** reference campaigns do not fit a 30 minute box (see above).
3. Seed 1000's boss fight (reference, first dump) exited with 0xC0000409 (a Godot fail-fast) after its state was written; not
   reproduced, not investigated.

## CALLS (made, logged in DECISIONS "SOLACE_BAL_r1")
1. Boss tuned by HP only (360 -> 400); enrage and phases untouched (HP alone landed in band).
2. Class bands were written after the first measurements, around what the starter-operative fight sim shows; there is no
   designer band yet (TARGETS.md says so).
3. Care Swarm tune not shipped (blocked by finding 1). GDD A.3 still lists Care Swarm 25 HP / 3 satellites.
4. Claims Adjuster and Account Manager HP edits lag the GDD A.3 table (90 / 120 originally): designer to update the table.
5. Saved-state seeds beyond the dump reuse a dumped state with a new combat seed (doubles the sample, same 25 crews).
6. Theme numbers unchanged; the campaign pace gap is reported as an open question.

## Still open
- Care Swarm at T4 on the starter operative (20 % win, 59 HP lost): tuned in the sim, held back by finding 1.
- Campaign length (45 runs vs 24) and the builtin campaign win (25 % vs the 50 % floor).
- Boss: 24 % of reference boss fights end on the 60-turn cap; is a cap a loss? Tester data (BAL-02) was not available here, so
  "inside the tester band" is unchecked. Sample size is 25 crews x 2 seeds; a second sample from other seeds would tighten the
  interval.
- N1b tier damage factor and EASY / HARD pools (BAL-06 rows) not touched.
- Golden replays: no replay fixture referenced the changed enemies; none regenerated. Tests with old HP pins updated:
  test_boss, test_m3_answers, test_ice_combat, test_enemies_m2.
