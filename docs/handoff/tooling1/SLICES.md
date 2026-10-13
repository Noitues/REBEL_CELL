# Tooling 1 — playtest cost slices (designer go 2026-10-12)

Source: `docs/process/PLAYTEST_COST_REVIEW.md` (§2, §3, §4, §5). Doc 05: `docs/process/05_CLAUDE_PLAYTESTER.md`.
Playtest tooling only: no game code under `scripts/`, `scenes/` or `content/`, except a new config `.tres` for the
strategist's thresholds if needed (`content/config/`, with its schema check per CLAUDE.md rule 8).

## T1 — gate profiles and harness savings (fix-mechanical)
Owns: `tools/playtest/gate.py`, `run_batch.py`, `harness.py`, `judge_batch.py`, `parity.py`, `roll_testers.py`
(mix only), `personas.json` (only if needed), and doc 05.
1. `gate.py --profile flow|combat|access|city|balance|milestone`, with the mixes, start points (route or save at
   the changed area; novices on onboarding start at Title) and skips from the review §4 table. No profile = milestone.
   The `MIX` hard-code goes. Add a `--state-mode heuristic|llm` option, default `llm`; T2 flips the default once its
   strategist lands.
2. Harness: screen testers do **not** escalate on combat turn starts by default. They still escalate on non-combat
   decision screens, on the watchdog (level ≥2) or on `escalate`. `--combat-escalation` turns it back on for a
   targeted probe.
3. **Motion: HELD** (designer 2026-10-12: animation slices come first). Do not touch the motion tester, motion critic or burst capture, and add no `motion` profile. Gate profiles just leave motion out (no motion tester in any profile mix).
4. The screen audit only judges screens that changed: use the route pixel diff, or compare screen signatures against
   the previous gate's batch; `--audit-all` keeps today's behaviour. Audit-only rows are not passed to the Stage C
   findings prompt.
5. Fix the `run_batch.py` cost double count (`spent()` globs `judge/cost.json`, then line ~215 adds it again), which
   also affects the budget check.
6. `parity.py` pairs turns by replay end time and TURN header so the pairing never comes out empty (PB-014: 0 paired
   turns), and refuses to spend on probes when 0 turns pair.
7. Doc 05: the gate profiles, the new defaults and costs; fix the stale lines (SA-000 "won in 11 runs"; "HQ / shops
   built-in").
Tests: these are tools, so give them a dry-run mode (`gate.py --dry-run --profile X` prints the plan and the $ caps
with no API calls) and test that the dry run lists the right testers per profile. `bash tools/precommit.sh --base main`.

## T2 — HeuristicStrategist (fix-rules)
Owns: `tools/agent/*` (new `heuristic_strategist.gd`, wiring in `agent_simulator.gd` / `agent_bridge.gd`),
`tools/playtest/state_agent.py` (a `--strategist heuristic|llm` mode), its config `.tres`, its tests.
1. A deterministic GDScript strategist answers every state decision kind with no LLM:
   - **combat:** `TurnPlanner` option 0; tie-break on HP taken, then kills.
   - **node:** HP-aware path score: avoid an Elite under an HP threshold, prefer heal / shop when low, otherwise
     maximise rewards.
   - **reward:** card-value score from tags plus synergy with the deck; skip below a threshold.
   - **launch / Heat / crew:** rules distilled from SA-001's launch decisions and reasons
     (`.playtest_sessions/*/state/*/decisions.jsonl`, kind `launch`, 262 rows; `docs/playtest/claude/state/SA-001.md`).
   - **raid:** the existing exact projection.
   - **hq / shop:** v2 sinks by a priority list.
   All thresholds come from a config resource (rule 5). Seeded and deterministic: the same seed gives the same campaign
   (test it).
2. `state_agent.py --strategist heuristic` runs it with $0 of API, any number of seeds in parallel, and writes the same
   report format as SA-001 (wins, run of the win, deaths, Heat peak, Schematics end, boss attempts).
3. **Calibration:** run the heuristic over seeds 1000–1019, and one LLM intermediate sweep on seeds 1000–1004 (budget cap
   $12; API key from the user environment; the harness pins the public API URL). Report both side by side in
   `docs/playtest/claude/state/SA-002_heuristic_calibration.md`. Accept when the heuristic's bands overlap the LLM's
   (wins within ±1 of 5, win run within the LLM's range ±30 %, deaths ≤ 2× LLM, Heat peak ≤ 60). If it misses, tune the
   config once and report.
4. Then flip `gate.py --state-mode` to default `heuristic` (a one-line change; T1 owns the rest of `gate.py`).
5. Also report the 2-turn-lookahead variant (CP-003 3A, change plan V3): the heuristic with `turn_planner` lookahead 2,
   seeds 1000–1019, boss attempts and wins. It is free with the heuristic.
Tests: determinism, every decision kind answered, config thresholds read (no literals). `bash tools/precommit.sh --base main`.
