# 05 — Claude playtesters (black-box, full campaigns, many at once)

A **Claude playtester** plays REBEL_CELL the way a person does: it looks at screenshots and uses
the mouse and keyboard, from NEW CAMPAIGN to the won / lost end screen. It never reads code,
scenes, content, the GDD or any design doc, and nothing in the game is instrumented for it. Each
tester is rolled with a **skill tier**, a **persona**, a **focus** and **quirks**, so a batch
plays differently and reports from different angles, in the studio feedback format
(`templates/CLAUDE_PLAYTEST_FEEDBACK.md`; motion testers: `templates/CLAUDE_MOTION_FEEDBACK.md`).
A batch rolls up into one page.

It complements the Human Playtest gate (doc 04); it does not replace it. Audio, drag-and-drop
feel and "does it look right" stay with the designer and the art-direction session.

There are two ways to run a tester. **Use the harness** (§3) for batches: ~8–11× cheaper than
the agent for the same play. The `playtester` agent (§4) stays for one-off, judgement-heavy
sessions and for comparing.

## 1. The black box

| Piece | Role |
|---|---|
| `tools/playtest/blackbox.py` | eyes and hands: `start`, `shot [--grid]`, `click`, `move`, `scroll`, `key` (chords like `ctrl+z`), `type`, `wait`, `status`, `stop`. Captures the game window's pixels (`PrintWindow`, works off-screen, ~22 ms a frame) and posts mouse/keyboard messages to it. Every action logs to `actions.log`. |
| `tools/run_windowed.py` | launched by `start`: no focus, Dummy audio, window off the screen. Testers never touch the designer's mouse, keyboard or speakers. |
| `start --private-copy` | each tester plays its own copy of the build in `<session>/game` (hard links, so no disk cost; `.godot/` copied; no `saves/`). A run from source saves to `res://saves`, so testers sharing one folder would share one save. The copy is kept for resuming. |
| per-session `APPDATA` | `start` points `%APPDATA%` at `<session>/appdata`: each tester has its own `user://` (settings, profile). |
| `.claude/worktrees/playtest-build` | the build a batch plays (a detached worktree at the batch's sha, imported); testers copy it. |
| `tools/hooks/guard_playtester.py` | for the `playtester` agent: Read only its session folder, report and template; Write only its journal and report; Bash only blackbox calls. |

**Input limit:** Godot's drag-and-drop does not start from posted messages, so testers play cards
by click → target (the game supports both). Keyboard, hover, right-click, scroll and chords work.

## 2. Tiers, personas, focuses, quirks (`tools/playtest/personas.json`)

**The skill tier is the main axis**: random, blind play does not get far, so how well a tester
plays, and how much it already knows, is what changes what it can reach and report.

| Tier | Acts with | Decision screens go to | Playbook | Combat coaching (designer, 2026-10-12) | Wheel close-ups | What it is for |
|---|---|---|---|---|---|---|
| novice | Haiku | — | nothing | none | none | onboarding, confusion, the first hour |
| intermediate | Haiku | Sonnet | rules observed by 2+ sessions | own wheel: needle on the centre of a high-value slice (a Perfect), read the shown result before SEND IT, UNDO to retry, clear statuses, damage Firmware | own | the mid-campaign loop, economy, raids |
| expert | Sonnet | Opus | everything, unconfirmed rules marked | both wheels: also push the enemy needle off centre onto a low or block slice | own + enemy | reaching the end, balance, dominant strategies |

Coaching lives in `personas.json` (`tiers.<tier>.coaching`); close-ups are full-resolution crops
of the wheel areas (`WHEEL_REGIONS` in harness.py) added to the stronger model's view on combat
decisions. Testers log every fight as `FIGHT won|lost turns=N hp_lost=N perfects=N`, and
`_BATCH.md` gets a combat-skill table from those lines. The designer, playing for Perfects, takes
almost no damage over 4–5 netruns, so deaths and "too hard" from testers that do not align well are
**tester skill-limited**, and the findings synthesis labels them so.

"Decision screens" = combat turn starts, rewards, shops, map and Site choices, events, raid setup,
HQ; the harness escalates them itself from the actor's `kind` label, plus any screen the actor
flags, plus any screen it has been stuck on.

**The playbook** (`docs/playtest/claude/playbook.json`) is what testers learned by playing, never
from code or docs: after each batch, the journals are distilled into lessons and merged (§6), each
rule with how many sessions confirmed or contradicted it and the builds it was seen on. It is how
an "experienced" tester exists without breaking the black box. Novices never get it, so fresh eyes
keep testing onboarding. A wrong belief can spread; the confirmation counts and novices are the check.

Personas (10, each with a tier) add the flavour that changes the feedback: reading habits, risk,
pace, tutorial or not, voice. Focuses (11 + the motion focus, which is dealt only on request) set
what the tester watches, with three focus questions and any settings to apply first. Quirks (1–2
of 18) push play off the beaten path (big deck vs lean, hoard vs spend, UNDO-heavy vs never...).

```bash
python tools/playtest/roll_testers.py --batch PB-010 --mix novice=6,intermediate=3,expert=1 --seed 7 --build main
python tools/playtest/roll_testers.py --batch PB-011 --count 2 --persona strategist --focus raids
```
Rolls are reproducible from `--batch` + `--seed`; within a batch, personas and focuses are dealt
without repeats before any repeat. Briefs land in `.playtest_sessions/<batch>/<handle>/brief.md`.

## 3. The harness (default)

```bash
python tools/playtest/harness.py --brief .playtest_sessions/PB-010/<handle>/brief.md --minutes 240 --max-usd 15 --defer
```
A Python loop with no conversation history. Each step sends the cached system prompt (rules,
the brief, the playbook for the tier), the tester's own notes (NOW block, the last 15 log lines,
the last 8 actions and whether the screen changed), and **one** 960×540 screenshot. The model
answers with one JSON decision: up to 6 actions, a journal note, an optional zoom (a crop sent
enlarged), `kind`, `watch`, `done`. Frames are taken only once the screen is still, so no steps
are spent waiting for animations. Every call's usage goes to `usage.jsonl` / `cost.json`.

Guards learned from the benchmarks: a tester stuck for 6 steps with no visible change is told
to note the bug and leave through the pause menu; `won` / `lost` must be claimed twice (an
operative's death is not the campaign's end); `done=time` before the time box is ignored.

The API key comes from the environment or the user environment (registry); the base URL is
pinned to the public API, never a proxy inherited from a Claude Code session.

Run several harnesses at once as background processes (≤ 4 on this PC to start). Without
`--defer` the harness writes its report itself at the end; with `--defer` it only plays and the
judging runs in a batch (§6).

## 4. The `playtester` agent (one-off, judgement-heavy)

Spawn one `playtester` agent per brief with the prompt `Brief: <path>` (all in one message, in
the background). It drives blackbox.py through Bash, keeps `journal.md`, and writes its report.
Pinned to Sonnet medium. It keeps every screenshot it has seen in its context, which is why it
costs ~10× the harness for the same play.

## 5. Motion tester (`harness.py --motion`, focus `animation_feel`)

When the actor marks an action `watch` (a card played, a spin, SEND IT, a reward reveal, a map
move, a transition, a raid playout), the harness grabs frames at ~15 fps until the screen has
been still for 0.6 s (max 5 s) and builds a time-labelled contact sheet (12 frames, 4 per row).
At most 3 sheets per (screen kind, action type) and 40 per session. A Sonnet critic judges each
sheet: cause and effect, timing, impact, glitches, flash risk (verdicts: clear and satisfying,
clear but flat, too slow, too fast, hard to follow, janky, flash risk, no animation). It cannot
see smoothness between frames or hear sound. Live, a judgement costs ~$0.007; with `--defer`
the sheets queue in `motion/pending.jsonl` and are judged in the batch at half that.

## 6. Judging in batch (`tools/playtest/judge_batch.py`, Message Batches API, 50 %)

```bash
python tools/playtest/judge_batch.py run --batch PB-010 [--audit-model opus] [--audit-max 40]
```
- **Stage A:** the queued motion sheets; a **screen audit** of the distinct screens each tester
  saw (near-duplicates dropped, at most `--audit-max`): clipped or overlapping text,
  placeholder strings, contrast, colour-only information, glitches, and what a newcomer would
  try next (`audit.jsonl`, `audit.md`); and **lessons** distilled from each journal.
- **Stage B:** every report (journal + motion judgements + audit findings) and the **playbook
  merge**.
Both stages are batches (usually minutes, at most 24 h); the command waits and is resumable
(state in `.playtest_sessions/<batch>/judge/`).

## 7. After a batch

```bash
python tools/playtest/aggregate.py --batch PB-010
```
writes `docs/playtest/claude/PB-010/_BATCH.md`: one row per tester, averages, outcomes, the cards
most often called overpowered or weak, and every tester's top frustration and change. Reports,
the batch page and the playbook are committed; session folders stay local.

Read `_BATCH.md`, then the reports it points to. A bug that two testers hit, or one tester hit
with steps that reproduce (the report quotes `actions.log` times, the screenshots are in the
session folder), becomes a finding with a slice item (nothing deferred). Treat input-related
bugs (a click that "does nothing") as **unconfirmed until a human or a second method repeats
them**: posted input is not a real mouse. Balance and feel opinions are evidence for the designer,
not findings: they go to the next checkpoint as a summary, never straight into tuning.

**Resuming:** run the harness again with the same brief; it reads `journal.md` and `cost.json`, and
the tester's private copy still holds its save (Continue on the title).

## 8. Benchmarks (2026-10-12, build 19ad76a3, same persona and focus)

| Run | Model use | Minutes | Inputs | Cost | $/input | $/minute | Got to |
|---|---|---|---|---|---|---|---|
| `playtester` agent (PB-000) | Sonnet, full history | 23 | 158 (+97 waits) | $5.66 | $0.036 | $0.25 | tutorial, campaign set-up, HQ, first netrun started |
| harness v1 (PB-001) | Haiku only | 7.5 | 107 | $0.085 | $0.0008 | $0.011 | tutorial won, then declared itself stuck (no escalation, no escape) |
| harness v2 (PB-002) | Haiku + Sonnet on decision screens | 23.7 | 223 | $0.75 | $0.0034 | $0.032 | first netrun, fight won, Firmware pick |
| motion (PB-003) | v2 + 23 live motion judgements | 17.5 | 192 | $0.66 | — | $0.038 | 4 fights, operative died at a Server Rack |

v2 against the agent: **~10.6× cheaper per input, ~7.8× per minute**, with similar progress and
similar findings (5 bugs and 5 confusion entries vs 3 and 3). Agent cost is the API-equivalent
of its transcript (`tools/playtest/bench_transcript.py`).

Batch judging (`judge_batch.py`, 50 %):

| Batch | Play | Judge | Judged |
|---|---|---|---|
| PB-002 (v2 session) | $0.75 live | $0.25 | 23 screens audited, lessons, report, playbook merge |
| PB-003 (motion, judged live) | $0.66 live | $0.24 | 21 screens, lessons, report, merge |
| PB-004 (motion, `--defer`, 15 min) | $0.33 | $0.33 | 29 motion sheets ($0.0033 each vs $0.0066 live), 18 screens, lessons, report, merge |

The screen audit is thorough but loud (~8 issues per screen, ~20 % blocker/major; the same menu
issue repeats on near-identical screens): read `audit.md` top-down and stop at the polish rows.

## 9. Streamlining: spend the budget on decisions (designer ruling 2026-10-12)

PB-010 lost roughly 40–50 % of play to menus, setup, the Site hunt and stuck screens (one expert
spent $14 on the New Campaign page). Testers now skip what they are not there to test:

| Piece | What it does |
|---|---|
| **Checked routes** (`tools/playtest/routes.py`, `routes/<build8>/*.json`) | Recorded inputs with a checkpoint frame per step, compared by pixels (no model call), optionally on a static region (`--region`) where the background animates. A mismatch stops the route and hands the tester the screen with "the route broke here" (a sign the UI changed). Recorded per build: `new_campaign` (title → HQ, city seed 1), `to_netrun` (→ the first netrun map), `continue` (title → CONTINUE). Record: `rec-start`, `rec <action>`, `rec-fix --region`, `rec-end`; check: `test`. |
| **Save library** (`tools/playtest/streamline.py`, `.playtest_saves/<build8>/`) | Saves collected from testers' private copies on every HQ arrival and the first raid setup (and `saves harvest --batch` from finished sessions). `--start-save heat>=25` installs one and the `continue` route loads it. The picker skips dying campaigns (home under half, crew wiped) and prefers the Heat closest to the floor. |
| **Watchdog** | Levels: a hint after 5 min on navigation screens or 15 min without a fight / reward / map move; a forced stronger look 3–5 min later; then a restart + Continue (or the start route), twice at most, then the session ends "blocked: …". A setup cap (10 min to the first fight) applies to testers that start on a route. |
| **Shared blockers** (`<batch>/blockers.jsonl`) | Every watchdog obstacle, and how a tester got past it, is shown to the other testers of the batch: they note "seen" and move on. |
| **Coverage plan** (`run_batch.py`) | Novices and the opening focuses (onboarding, UI flow, readability, story) play from the title; raids / economy / campaign focuses start from a Heat ≥ 25 save; everyone else starts at the first netrun. Someone always plays the opening. |
| **Escalation throttle** | A decision screen goes to the stronger model when it is new (or every 4 steps), not on every browsing step; combat turn starts always do, with an alignment plan required in the answer. |
| **Batch-wide audit dedupe** | A screen already audited for one tester of the batch is not audited again; at most 25 per tester. |

PB-012 (3 testers, 30 min): the route tester reached the netrun map in 0.6 min (PB-010: 10–25 min,
one never), the save tester loaded a Heat 70 campaign in 0.3 min. Screen testers still report
**0 Perfects** in every fight, coached or not, while the state tester (§10) picks PERFECT landings
from its menu: the screen may not make a Perfect legible (see §11).

## 10. State tester: decisions from exact menus (designer ruling 2026-10-12)

For balance and difficulty, not for clarity: `tools/agent/agent_bridge.gd` runs a campaign headless
(`AgentSimulator` = `CampaignSimulator` with its decisions handed out through request/response files),
and `tools/playtest/state_agent.py` answers with an LLM in a persona's style, with a one-line reason
per pick. Menus: whole-turn combat plans from a beam search over the preview (cards and nudges within
RAM, each with damage dealt / taken, kills, RAM and where every pointer lands: PERFECT / GOOD / WEAK),
map nodes with Heat, rewards (Firmware per empty slot), events with costs, launches, raid placements
with their exact projected outcome. Option 0 is always the built-in policy, so `--builtin all` is the
free baseline (greedy `CombatBot`). Shops and HQ upkeep stay built-in (v1).

```bash
python tools/playtest/state_agent.py --name SA-001 --seeds 1000-1004 --tier intermediate --persona strategist --budget 10
python tools/playtest/state_agent.py --name SA-000 --seeds 1000-1004 --builtin all          # free baseline
```
Tiers: novice = Haiku everywhere; intermediate = Haiku in combat, nodes and events, Sonnet on rewards,
launches and raids; expert = Sonnet everywhere. First runs: 2 netruns, ~70 decisions, $0.09; a full
campaign is ~$2–3 at intermediate. Baseline (greedy bot, ICE 0, 60-run cap): seeds 1000 and 1001 never
won (19 deaths each), 1002 won in 11 runs. Output: `.playtest_sessions/state/<name>/<seed>/` (report,
decisions with reasons) and `docs/playtest/claude/state/<name>.md`.

## 11. Next: decision parity, visual vs headless (designer idea 2026-10-12)

Once both testers perform well: rebuild a screen tester's fights from its combat replays
(`saves/replays`, seed + actions) headless, ask the state tester what it would do at the same turn,
and turn every disagreement into a single-turn visual probe ("what on screen would have led you to
the other plan?"). The output is a list of visual changes that would let a player make the decision
the numbers support: developer-facing findings with the exact turn and screenshot.
