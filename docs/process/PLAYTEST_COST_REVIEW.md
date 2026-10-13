# Claude playtest cost review            2026-10-12 · main @ 19432d7d

Designer request: find extraneous or redundant playtests, cut the API cost, consider a classic heuristic AI instead of
the LLM, and pick the tester tiers per wave. Facts are from the pipeline map (doc 05, `tools/playtest`, `tools/agent`,
the PB-004…PB-015 and SA-000 / SA-001 reports and their `cost.json` files).

## 1. Where a gate's money goes today (≈ $41 measured, $50 budgeted)
| Part | Measured | What it produced | Value |
|---|---|---|---|
| Expert screen tester (rustbelt, Sonnet → Opus) | **$14.02** (34 %) | 2 findings; spent all 151 min on New Campaign setup | very low |
| 3 intermediate screen testers (Haiku → Sonnet) | $10.57 | 69 findings, most shared with the novices. ~92 % of the cost is Sonnet escalations, mostly on combat turn starts trying to align the wheels from pixels | medium |
| 3 novice screen testers (Haiku only) | **$1.00** | 42 findings; the flow and onboarding bugs | **highest** |
| Motion tester | $2.21 | M1–M10, queued: the animation pass is paused | none now |
| Judging: screen audit | $1.66 | mostly the audit-only polish rows on the ignore list | low |
| Judging: reports, lessons, Opus findings, playbook | $2.06 | the batch synthesis | keep |
| State sweep, LLM strategist (7,399 calls) | **$9.40** | D1 boss wall, D2 pacing, D3 Schematics: no other source | high, but see §3 |
| Routes, save library, watchdog, replay audit, aggregate | $0 | the replay audit is the ground truth behind A1 | keep |
| Perfect quiz + decision parity (one-offs) | $0.49 + $1.41 (one play $1.18 wasted: 0 paired turns) | ranked A1, A2, A4 | keep, targeted |

Redundant or wasted spend:
- **PB-012 re-ran PB-010's build.** It cost $3.77, and its own report says another run "would only re-confirm".
- **PB-004 and PB-005** were superseded by PB-010.
- **PB-014's parity play** paired 0 turns, so the $1.18 produced nothing.
- **Screen testers' combat escalations** spend Sonnet and Opus guessing what the replay audit computes exactly for $0.
  The Perfect quiz showed vision cannot tell centre from ±1 tick anyway.
- **Cost accounting bug:** `run_batch.py:53-54` globs `judge/cost.json` and line 215 adds it again. PB-012's "$4.59"
  is really $3.77, and the same glob feeds the budget check.

## 2. Recommendations (cheapest first; all tooling, no game code)
1. **No expert screen tester at ordinary gates** (saves ~$14). The state sweep and the replay audit measure expert
   play exactly. Use an expert only for a targeted probe: started from a save or route, 30 min cap, at the screen
   under test.
2. **Screen testers stop escalating on combat turn starts** (intermediate cost ~$3.5 → ~$1). Their job is reading and
   flow; combat skill comes from the replay audit at $0. Escalate only for non-combat decision screens, on a watchdog,
   or on `escalate`.
3. **Every tester starts from a route or a save at the area the wave changed.** PB-012 reached the netrun in 0.6 min
   against 10–25 min. Novices doing onboarding still start at Title.
4. **Motion tester off** until the animation pass resumes (saves $2.2).
5. **Screen audit only on screens that changed** (the route pixel diff names them), and drop audit-only rows
   (saves ~$1.3).
6. **Fix the accounting double count;** refresh doc 05's stale lines (the SA-000 "won in 11 runs", "HQ / shops
   built-in").
7. **Parity runs pair turns by replay** (fixes the PB-014 waste) and only in waves that change combat legibility.

## 3. A classic heuristic strategist instead of the LLM (recommended)
Of SA-001's 7,399 calls:
- **combat, 57 % (Haiku):** a choice among `TurnPlanner`'s six options. The planner is already a deterministic beam
  search with exact outcomes; the LLM mostly picked between equal plans.
- **reward, 24 % (Sonnet):** kept option 0 89 % of the time.
- **node, 12 %:** many reasons read "identical, take the first".
- **launch, 3.5 % (Sonnet):** the only kind where the LLM really differs from the built-in policy (86 %), and the
  reason the built-in policy fails (Heat 100, ~18 deaths).

**Proposal: a `HeuristicStrategist` in GDScript** (in `tools/agent`, beside `agent_simulator.gd`), replacing the
LLM at gates:

| Decision | Rule |
|---|---|
| combat | planner option 0; tie-break on HP taken, then kills |
| node | HP-aware path score: avoid an Elite under an HP threshold, prefer heal / shop when low, otherwise maximise rewards |
| reward | card-value table from tags, plus synergy with the deck; skip below a threshold |
| launch / Heat / crew | rules distilled from SA-001's 262 launch decisions and their reasons (Heat ceiling, crew rotation, breach when 3 Exploits and a ready crew) |
| raid | the existing exact projection |
| hq / shop | the v2 sinks with a priority list (answers 5A: is the Schematics surplus real?) |

All thresholds live in a config `.tres` (rule 5).

| | |
|---|---|
| Build cost | 1 `fix-rules` slice (Sonnet, or Opus with a stated reason) plus a calibration run: one SA-001-sized LLM sweep (~$9) to check the heuristic reaches the same outcome bands (wins, deaths, Heat) |
| Gate cost | $0. Deterministic and seeded: same seed gives the same campaign. Runs 20+ seeds in minutes where the LLM ran 5 in ~2 h, so the boss and pacing numbers get real error bars |
| Break-even | the first gate (~$9.40 each); over the ~3 gates of change plan 1 it saves ~$28 and gives exact regression comparison between builds |
| Keep the LLM strategist | at milestone gates only, as a "human-like" calibration: Haiku for routine kinds, Sonnet only for launch / raid |

Combat and nodes on the screen side stay LLM, since reading the screen is the thing under test; the heuristic
replaces only the state-side strategist.

## 4. Which testers after which wave
| Wave type | Use | Skip | Est. $ |
|---|---|---|---|
| **Flow bugs** (plan wave 1, B) | routes (break = changed screen); 2 novices + 1 intermediate started at the fixed screens; heuristic sweep (soft-lock regression) | expert, motion, parity, LLM sweep | **~$2–3** |
| **Combat legibility** (wave 2, A) | 2 novices + 2 intermediates (one keyboard_only) from a netrun save, no combat escalation; Perfect quiz and parity re-run vs the PB-013 / PB-015 baselines (the A1 / A2 metric); replay audit (tester Perfect rate vs the 20 % baseline) | expert, motion | **~$5–7** |
| **Accessibility / text size / contrast** | novice + intermediate (keyboard_only) at text 2.0 and high contrast, from routes; screen audit on changed screens | expert (they compensate), state sweep | ~$2–3 |
| **City clarity** (wave 3, C) | 3 novices from New Campaign (the Site hunt cost novices most); 1 intermediate explorer | expert, motion, parity | ~$3 |
| **Boss / balance** (D) | heuristic sweep, 20+ seeds incl. 2-turn lookahead; 1 expert from a strong save at the boss, 30 min | novices (never reach the boss), screen batch | ~$2–5 |
| **Motion** (when resumed) | motion tester + motion critic | others | ~$3 |
| **Milestone gate** | the trimmed full mix (2 novice, 2 intermediate, 1 expert from saves) + one LLM sweep | — | ~$15–20 |

**Net: an ordinary gate drops from ≈ $41–50 to ≈ $3–7; a milestone gate to ≈ $15–20.**

## 5. To implement (one tooling slice, `fix-mechanical`, on the designer's go)
- `gate.py --profile flow|combat|access|city|balance|motion|milestone`, with the §4 mixes, start points and skips.
- Harness: a `--no-combat-escalation` default for screen testers; the audit only on changed screens; motion opt-in.
- Fix the `run_batch` accounting; pair parity turns by replay; refresh doc 05.
- Then, separately, the `HeuristicStrategist` (one `fix-rules` slice plus the ~$9 calibration run).
