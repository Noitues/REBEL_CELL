# SA-002 — HeuristicStrategist calibration (Tooling 1 T2, 2026-10-12)

Build: main @ 174369ab (+ the strategist, tooling only). Breaker vs Solace, ICE 0, 60-run cap.
Sweeps: `SA-002-llm` (LLM, intermediate tier, persona strategist, seeds 1000–1004, **$10.22**, 4,981 calls, cap $12),
`SA-002-heuristic` (heuristic, seeds 1000–1019, $0), `SA-002-lookahead2` (heuristic with the 2-turn combat
lookahead, seeds 1000–1019, $0). Per-seed tables: `SA-002-llm.md`, `SA-002-heuristic.md`, `SA-002-lookahead2.md`.
Decision logs: `.playtest_sessions/state/<name>/<seed>/decisions.jsonl`.

## Bands, side by side

| Sweep | Seeds | Wins | Win run(s) | Deaths per seed | Heat peak mean / median / max | Schematics end (mean) | Boss attempts | Boss wins |
|---|---|---|---|---|---|---|---|---|
| LLM intermediate | 5 | 0 (0.0 per 5) | none | 3.2 (max 6) | 74 / 64 / 100 | n/a (base report) | 13 (from the run logs) | 0 |
| Heuristic, before the tune | 20 | 16 (4.0 per 5) | 10–56 | 0.3 (max 2) | 53 / 46 / 100 | 143 | 25 | 16 |
| **Heuristic (shipped config)** | 20 | 15 (3.8 per 5) | 10, 17, 26, 26, 27, 30, 36, 37, 43, 44, 51, 53, 54, 55, 56 | 0.5 (max 3) | 53 / 44 / 100 | 177 | 25 | 15 |
| Heuristic, 2-turn lookahead | 20 | 16 (4.0 per 5) | 13, 17, 25, 29, 32, 32, 34, 37, 38, 45, 53, 54, 55, 55, 56, 57 | 0.3 (max 2) | 56 / 46 / 100 | 170 | 22 | 16 |

For reference, SA-001 (same LLM tier on an older build, 19ad76a3 era): 2 wins of 5 (runs 30, 52), 1.8 deaths per seed,
Heat peak 40–48.

## Acceptance (brief: wins ±1 of 5, win run within the LLM's range ±30 %, deaths ≤ 2× LLM, Heat peak ≤ 60)

- Wins within ±1 of the LLM's per 5 seeds: **MISS** (3.8 vs 0).
- Win run within the LLM's range ±30 %: **MISS** (the LLM never won on this build; no range to compare).
- Deaths ≤ 2× the LLM's: **ACCEPT** (0.45 vs 3.2 per seed).
- Heat peak ≤ 60: **ACCEPT** on the mean (53); 2 of 20 seeds reach 100 (1000 and, with lookahead, 1001/1004).

**Verdict: MISS on the win bands; the heuristic plays the campaign much better than the intermediate LLM.**
The one config tune allowed (`hq_priority` drops next-run boosts, which the LLM bought 5 times in 5 campaigns and
the heuristic every rich HQ visit) changed almost nothing (16 → 15 wins), so boosts are not the gap.

## Why the bands differ (from the decision logs)

1. **Breach Heat.** The heuristic breaches only at Heat ≤ 10 (`breach_max_heat`; Heat at breach 0–10, mostly 0).
   The LLM breached at Heat 11–35 and kept re-breaching with fresh rookies (R3–R6) at Heat 24–51. Heat ≥ 25 makes
   elites more frequent and Heat ≥ 50 gives every enemy +1 resistance, the boss included.
2. **Deck.** The LLM's shop removes Jolt (17 removals; boss decks hold 1–4 Jolts, median 4 but often 2); the heuristic
   never thins Jolt (value 3) and enters the boss with 4–6.
3. **Combat.** Haiku left the planner's best plan in 358 of 4,867 combat turns; the heuristic only on exact ties
   (18 of 13,646).
4. **Boss attempts** are the deaths: the LLM's 16 deaths are 13 boss attempts plus 3 others; the heuristic's 9 deaths
   are 10 failed boss attempts' worth (one attempt ended stuck at the turn cap).

So the miss is the heuristic being a disciplined player, not a broken one. As a gate regression signal it is
deterministic (same seed → same campaign, tested) and its numbers move with the build; it is not a stand-in for an
intermediate human's win rate. Keep the LLM sweep at milestone gates for that (PLAYTEST_COST_REVIEW §3).

## Genome Core with the 2-turn lookahead (CP-003 3A, change plan V3)

| | Boss attempts | Boss wins | Win rate per attempt | Campaign wins (of 20) | Deaths |
|---|---|---|---|---|---|
| Heuristic, lookahead 1 | 25 | 15 | 60 % | 15 | 9 |
| Heuristic, lookahead 2 | 22 | 16 | 73 % | 16 | 6 |
| LLM intermediate (5 seeds) | 13 | 0 | 0 % | 0 | 16 |

The lookahead scores each plan with the best plan of the next turn after it (it reads the cloned combat RNG, so it
plays slightly better than a player could). With good campaign discipline (breach at Heat 0–10, full Jolt set) the
boss is beaten on the first attempt in most seeds even without lookahead; the deeper search adds ~13 points per
attempt. Of the seeds that never win, 1000 and 1006 never breach: Heat climbs to 67–100 while the strategist runs
the -5 patrol (each run's Heat gain outpaces it) and no third Exploit opens at Heat ≤ 40; 1001 and 1011 lose their
2–4 boss attempts.

## Not done / notes

- The LLM sweep ran on the base bridge, so its reports lack `schematics_end` and `boss_attempts` (counted from the
  run logs instead).
- Schematics surplus (5A): the heuristic ends campaigns with ~170 Schematics after scrubbing Heat whenever Heat ≥ 10
  and claiming relays; the LLM held 47–750 at its breaches on this build (SA-001 hoarded ~1,000–1,800).
