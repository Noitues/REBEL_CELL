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

**Lost-click limit (PB-SOL-1 I1, 2026-10-21):** a posted `WM_MOUSEMOVE` while the real cursor is
elsewhere makes Windows send `WM_MOUSELEAVE` at once; Godot then drops the hovered control, and a
`Button` presses only on a release it still counts as inside. Testers saw JACK IN, LOOT, CONTINUE,
Quit and the like "ignore" 1-4 clicks, with Enter or a centre click working. Real-input flow tests
(`test_pt_p1_clicks`, `_hq_clicks`, `_loot_clicks`: move, press, release through the viewport, live
motion on, centre and every edge) pass first time on all of them, so the game takes the click.
`click` now re-posts the move right before the press and before the release. A control that still
drops a click after that is a harness artifact until a flow test reproduces it; confirm on a real
mouse before filing a game bug. Remaining known limit: dialogs over a `GlassScrim` can still lose
posted clicks (use Esc, or the keyboard answers the dialog offers).

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

"Decision screens" = rewards, shops, map and Site choices, events, raid setup, HQ; the harness
escalates them itself from the actor's `kind` label, plus any screen the actor flags, plus any
screen the watchdog or the stuck-step guard says it is stuck on. **Combat turn starts are not
escalated by default** (since 2026-10-12): the replay audit measures combat skill exactly for $0,
and vision cannot tell the centre of a slice from +-1 tick anyway. `harness.py --combat-escalation`
(or `gate.py --combat-escalation`, `run_batch.py --combat-escalation`) turns it back on for a
targeted probe; the tiers' wheel close-ups then apply again.

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
  saw (near-duplicates dropped, at most `--audit-max`; **only screens that changed**: a screen
  matching one the `--compare` batch's testers saw is skipped, `--audit-all` audits everything and
  also passes audit-only rows to the findings; by default audit rows reach `_FINDINGS.md` only
  through the testers' reports): clipped or overlapping text,
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
| **Escalation throttle** | A non-combat decision screen goes to the stronger model when it is new (or every 4 steps), not on every browsing step. Combat turn starts no longer do by default (`--combat-escalation` restores it, with the alignment plan required in the answer). |
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
free baseline (greedy `CombatBot`). Shops and HQ upkeep are decisions too (kinds `shop` and `hq`, the v2 sinks).

```bash
python tools/playtest/state_agent.py --name SA-001 --seeds 1000-1004 --tier intermediate --persona strategist --budget 10
python tools/playtest/state_agent.py --name SA-000 --seeds 1000-1004 --builtin all          # free baseline
```
Tiers: novice = Haiku everywhere; intermediate = Haiku in combat, nodes and events, Sonnet on rewards,
launches and raids; expert = Sonnet everywhere. First runs: 2 netruns, ~70 decisions, $0.09; a full
campaign is ~$2–3 at intermediate. Baseline SA-000 (greedy bot, ICE 0, 60-run cap, seeds 1000-1004): no
seed won; 17-19 deaths each, Heat peak 100 on every seed. Output: `.playtest_sessions/state/<name>/<seed>/` (report,
decisions with reasons) and `docs/playtest/claude/state/<name>.md`.

## 10b. Boss save (V4)

A save at the Genome Core breach, for a human (or a tester) who wants the boss without 25 runs of
set-up. `tools/agent/make_boss_save.gd` plays a campaign with the HeuristicStrategist (same as
`state_agent.py --strategist heuristic`) and stops at the first moment it would launch the breach
(3 Exploits, crew ready), then writes that campaign through `SaveService.save_dict` (the layout
`RunManager.autosave()` uses, so the title's CONTINUE / slot list loads it) as `campaign_<slot>.json`
plus a `profile.json` (which also lists the slot), and prints one summary line (seed, run, Heat, crew
with Rank and HP, deck, Firmware, Daemons, Schematics). Exit 1 if no breach within 60 runs.

```bash
godot --headless --path . -s tools/agent/make_boss_save.gd -- seed=1002 out=<abs dir> [slot=1]
python tools/agent/make_boss_saves.py --seeds 1002,1017,1018      # into .playtest_saves/boss/<seed>/ + meta.json (label boss)
python tools/playtest/streamline.py saves list --build boss       # the library
```
Play one: copy a seed's `campaign_1.json` and `profile.json` into the game's `saves/` folder (back up
the old ones), then CONTINUE. Test: `tests/unit/test_boss_save_writer.gd` (round trip on a one-run
fixture; the 60-run play is not in the suite).

## 11. Next: decision parity, visual vs headless (designer idea 2026-10-12)

Once both testers perform well: rebuild a screen tester's fights from its combat replays
(`saves/replays`, seed + actions) headless, ask the state tester what it would do at the same turn,
and turn every disagreement into a single-turn visual probe ("what on screen would have led you to
the other plan?"). The output is a list of visual changes that would let a player make the decision
the numbers support: developer-facing findings with the exact turn and screenshot.

## 12. At every User-Ready Gate (designer rulings 2026-10-12; cost review PLAYTEST_COST_REVIEW.md)

```bash
python tools/playtest/gate.py --gate PT-014 --profile combat --compare <previous screen batch>
python tools/playtest/gate.py --gate PT-014 --profile city --dry-run      # the plan and the $ caps; no API calls
```
`--profile` picks the tester mix, start points, caps and skips by **wave type**. No profile = `milestone`.
Defaults: no expert at an ordinary gate (the state sweep and the replay audit measure expert play exactly);
no motion tester in any profile (motion is held until the animation pass resumes); screen testers do not
escalate on combat; every tester starts from a route or save at the changed area (`--at route:to_netrun`
by default; `--at title`, `--at save:heat>=25`) except novices on onboarding / city clarity, who start at
the title; the screen audit judges only changed screens.

| Profile | Testers (box, cap) | Start | State sweep | Also | Typical $ | Worst case $ |
|---|---|---|---|---|---|---|
| `flow` | 2 novice (40 min, $1), 1 intermediate (60, $2) | `--at` | sweep, free with the heuristic | | 2.8 (`--llm-sweep`: +9.4) | 5.8 (llm: +12) |
| `combat` | 2 novice, 1 intermediate, 1 `keyboard_only` | `--at` | none | decision parity on the first intermediate session (skipped when 0 turns pair); the Perfect quiz is a separate on-demand probe | 4.4 | 10.2 |
| `access` | 1 novice + 1 `keyboard_only`, both focus readability (text 2.0, reduce effects, high contrast) | `--at` | none | | 2.3 | 4.4 |
| `city` | 3 novice (title), 1 intermediate `explorer` | novices title, explorer `--at` | none | | 3.3 | 7.2 |
| `balance` | 1 expert (30 min, $3) | save `heat>=25` | 20 seeds, 2-turn lookahead once the strategist supports it | | 3.2 heuristic (llm: +9.4) | 4.0 (llm: +12) |
| `milestone` | 2 novice (title), 2 intermediate, 1 expert (120 min, $8) | expert save `heat>=25` | the free heuristic sweep (20 seeds); LLM calibration sweep (5 seeds, $12 cap) only with `--llm-sweep` | | 10.5 (`--llm-sweep`: +9.4) | 16.6 (llm: +12) |

The state sweep is the free heuristic strategist (`state_agent.py --strategist heuristic`, $0, any number of
seeds) in every profile that has one. The LLM sweep is **opt-in in every profile, the milestone included**:
add `--llm-sweep` (designer ruling 4, 2026-10-13); it is always the 5-seed calibration (about $9.4, $12 cap) and
runs in addition to the heuristic sweep. `gate.py --dry-run --profile X [--llm-sweep]` prints the exact table
for a profile with its current options.
for a profile with its current options.

1. **Build and routes:** the build copy is pointed at main and every recorded route is replayed on a
   fresh copy. A broken route means that screen changed: re-record it (§9) and note it in the gate
   report; until then testers start from the title.
2. **State sweep** (profiles that have one): win rate, deaths, Heat, raids and the reasons behind picks.
3. **Screen batch:** the profile's mix with `caps + judge reserve` as its budget, judged in batch,
   `_FINDINGS.md` compared with the previous batch. Combat skill comes from the **replay audit** (every
   fight rebuilt from the game's combat replays: was a Perfect reachable, did the tester land it, damage vs
   the best plan), not from the testers' own counts.
4. **Decision parity** (`combat` profile): pairs the screen tester's turns with the replays' turns by
   order, replay end time and the on-screen TURN header, and exits without spending when 0 turns pair.
Output: `docs/playtest/claude/gates/<gate>.md`. The findings feed doc 04 section 3 (bugs and clarity ->
slice items, balance and design -> checkpoint questions); the next gate's batch shows what landed.

Cost accounting: `run_batch.py` counts the judge's cost once (the testers' spend excludes `judge/cost.json`,
the judge's is added once at the end); the budget check no longer includes it a second time.

First audit (PB-010, 574 turns): a Perfect was reachable on 93–100 % of turns; testers landed one on
~20 %, the same as taking no action; the best plan takes ~0.8 damage per turn vs the testers' ~3.5.

## 13. Scripted steps (batch-judged)

For a playtest plan's step table (PT-003 first) a script, not a tester, drives the game, and the Batch API judges the pictures:
1. `python tools/run_windowed.py --log <file> -- res://tools/playtest/steps/pt003_steps.tscn -- --out=<abs>/.playtest_sessions/PT003-steps`
   (one windowed run; `--only=2,3` re-runs steps and merges them into `steps.json`). Per step: screenshots or frame strips,
   the action, the adjusted PASS sentence and machine facts read from the game. Steps it cannot drive are marked SKIP, never faked.
2. `python tools/playtest/steps_judge.py run` (`estimate` prints the cost first; hard cap `--max-usd 2`). One batch request per step
   (haiku vision), JSON verdict PASS / FAIL / PARTIAL, then `docs/playtest/claude/steps/PT-003_steps.md` with the PT feedback block.
   `report` re-ingests the stored results without an API call.
The judge's verdict is evidence; motion steps need the designer's eyes. No unit tests (tools, rule 6).
