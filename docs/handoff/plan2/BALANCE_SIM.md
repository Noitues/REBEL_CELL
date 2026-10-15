# Balance sim: logic-only combat + campaign simulation (designer 2026-10-15)

Goal: balance changes made **independently of the graphical work**. They touch data only (`content/**/*.tres`,
`content/config/*.tres`) and are measured with a logic-only sim. No scene, view or Node rules.

**Exists already, reuse it:**
- `scripts/core/campaign_simulator.gd`: pure core, plays whole campaigns with fair policies.
- `CombatBot`.
- `tools/agent/heuristic_strategist.gd` (+ `turn_planner.gd`, lookahead).
- `tools/agent/agent_bridge.gd` and `tools/playtest/state_agent.py --strategist heuristic`: headless, $0,
  deterministic.
- `tools/simulate_campaign.gd`: pacing against GDD 11.8.
- `tools/agent/boss_stop_simulator.gd`.

**Missing:**
- data overrides without editing files;
- fight-only and boss-only modes;
- the balance metrics in one report;
- A/B comparison;
- isolation of balance commits.

## S1: `BalanceSim` (tools/balance/)
- **One entry point:** `godot --headless --path . -s tools/balance/balance_sim.gd -- <mode> …`. Python driver
  `tools/balance/balance.py`: shards seeds in parallel (`-j`), merges JSON, writes markdown.
- **Modes:**
  - `campaign`: whole campaigns, through `CampaignSimulator` or the heuristic strategist.
  - `fight`: one enemy or encounter id × N seeds × an operative / deck preset.
  - `boss`: the boss fight from boss saves or a built state.
  - `netrun`: one run from a campaign state, to measure HP attrition across layers.
- **Policies:** `builtin` (CombatBot) / `heuristic` / `heuristic --lookahead N`, plus a **skill knob**: a share of
  turns played well, to model the testers' 15–25 % Perfect rate against an expert.
- **Overrides:** `--set path=value` and `--variant file.json`. They apply to **duplicated** copies of the content and
  config Resources, held in a sim-local registry. Never modify a loaded Resource (rule 3); files on disk are never
  touched.
- **Determinism:** same seed + same overrides = the same report (a test).

## S2: metrics (one JSON schema and one markdown report)
- **Fight:** turns, damage dealt and taken per turn, HP lost, deaths, Perfect rate, RAM debt, heal turns (the enemy's
  self-heal), win rate.
- **Netrun:** HP on arrival per layer (attrition curve), heals available and used, layers survived, deaths, Cycles.
- **Campaign:**
  - runs and raids;
  - the Heat curve and its peak; raids from flatline Heat vs from actions;
  - Schematics and Cycles income / spend / unspent;
  - recruits and deaths;
  - win / loss;
  - estimated minutes, against GDD 11.8.
- **Boss:** turns per phase, total turns, HP curve, the player's HP at the end.
- **Distributions:** mean, median, p10 / p90 for every metric, not just the mean.

## S3: compare
`balance.py compare A.json B.json` gives a delta per metric with a bootstrap 90 % interval over the seeds. It flags
changes that are within noise. Output `docs/balance/CMP_<name>.md`.

## S4: isolation and baseline
- **Branch:** balance work lives on branch `balance` (its own worktree). Commits there may touch only `content/`,
  `docs/balance/` and `tools/balance/`. A precommit check fails a balance-branch commit that touches anything else.
  `validate_content.gd` and the schema smoke test must pass.
- **Merging:** `balance` merges to main like any branch. It only touches data, so it never conflicts with view work,
  and the fast tier runs on the merge.
- **Baseline:** `docs/balance/BASELINE_<sha>.md` from the current content (campaign 20 seeds × ICE 0 / 5; fight sweep
  over every enemy; boss; netrun attrition), committed as the reference.

## S5: balance work (restarted on the sim)
The issues, each with variant sweeps leading to `docs/handoff/plan2/BALANCE_OPTIONS.md` (2–3 options with numbers,
for the designer's rulings; no content change until then):
- D2 HP attrition with no heal;
- D3 fight length (9–16 turns), enemy HP and self-heal;
- the boss length (V4: "tediously long");
- D5 flatline Heat driving raids;
- D6 the Schematics economy (unspent, recruit price).

After the rulings, the chosen options become content edits on `balance`, each with a compare report.

## Lanes
- **S1–S4:** one fix-mechanical agent (Sonnet; tooling, Godot runs).
- **S5 sweeps:** the same tooling, $0 (no LLM).
- **S5 options write-up:** the Batch API (Sonnet) summarises the sweep JSON into option text; the orchestrator
  reviews it.

**Tests (rule 6):**
- overrides never mutate a loaded Resource;
- same seed + same overrides = the same report;
- a fight-mode result equals `CombatResolver` replayed from the same seed;
- the balance-branch path guard.

Tools themselves get no other unit tests.
