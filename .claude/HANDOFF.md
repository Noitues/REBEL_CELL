# Handoff — REBEL_CELL (change plan 1, gate PT-002 in progress)

| | |
|---|---|
| Written | 2026-10-13 21:03 local |
| Session id | be016cca-ea5b-43a2-b75d-e286cee33d9f |
| Branch / commit | main @ 84c8aa3e (pushed: origin/main @ d086ca5a; 52ba1e94 merge + PT-002 list + routes are local only) |
| Reason for pause | Designer: the session is long; hand off and resume in a new one |

## Goal
REBEL_CELL (Godot 4.7 roguelite deckbuilder). M14 is complete (gate PT-001). We are running **change plan 1**
(`docs/handoff/gates/CHANGE_PLAN_1.md`), built from Claude-playtester feedback and the designer's playtests:
- wave 1 / 1b: flow bugs;
- wave 2: combat legibility (precision tags, planned-outcome chips, labels / legend, card faces, round 45 inner ring);
- wave 3: city clarity (next).

The designer said "keep going to the gate": finish **gate PT-002**, hand the designer the playtest list, then STOP
and wait for their feedback. **Rule CP-002 #1:** gather feedback, act on none until the designer decides; triage →
rulings → plan.

## State of the tree
- **Main @ 84c8aa3e** has everything for PT-002 merged: waves 1b + 2, raid STEP divider, US English pass, deferred
  test tier, round 45 ring + polish (52ba1e94), INCOMING fixes, routes for build 52ba1e94.
- **Uncommitted in main:** nothing of mine. Untracked files that belong to others stay untouched:
  - `docs/HANDOFF_H20_MERGE.md`, `docs/art_asset.md`, `du.exe.stackdump`;
  - `.playtest_sessions/*`, `.playtest_saves/*` (gitignored);
  - some `*.gd.uid` import leftovers.
- **`project.godot`:** the designer's open editor keeps re-saving it (it drops the translations line and
  `aspect="keep"`, adds `[dotnet]`). The designer authorized restoring it: `git restore project.godot` whenever it
  shows as modified.
- **Not pushed:** 52ba1e94 (ring polish + PT-002 list draft) and 84c8aa3e (routes). Push only through the push gate
  (below).

## In flight (independent of this session)
1. **PT-002 combat screen batch**: `python tools/playtest/gate.py --gate PT-002 --profile combat --compare PB-010
   --build 52ba1e94` (started via PowerShell Start-Process, pid 23456).
   - Logs: `%TEMP%\gate_pt002\gate_combat.log` and `.err`.
   - Output: `docs/playtest/claude/gates/PT-002.md`, the batch under `.playtest_sessions/<batch>/`, `_FINDINGS.md`
     in `docs/playtest/claude/<batch>/`.
   - Testers: 2 novice + 1 intermediate + 1 keyboard_only, from `route:to_netrun`, combat escalation off, decision
     parity on the first intermediate.
   - About $4–10, ~60–90 min.
   - It pins build 52ba1e94 because the routes are recorded for that sha. Routes are keyed by the playtest-build
     HEAD[:8], so a new build sha means copying the routes (JSON **and** the step-PNG folders) or re-recording.
2. **Perfect-quiz probe** (PB-016 / glasswing, intermediate casual_evening, focus wheel_combat; cmd.exe pid 6112):
   - `harness.py --probe-perfect 30 --route to_netrun --minutes 25 --max-usd 1.0 --defer`, then
     `perfect_quiz.py --session .playtest_sessions/PB-016/glasswing`.
   - Logs: `%TEMP%\gate_pt002\probe_play.log`, `probe_quiz.log`. Output: `docs/playtest/claude/probes/perfect_PB-016_glasswing.md`.
   - Baseline is `docs/playtest/claude/probes/perfect_PB-013_nullpoint.md`: vision 87% vs "always no" 90%. The goal is
     that A1's PERFECT tag lets a reader beat "always no" clearly.
3. **Leak-fix agent** (fix-mechanical, worktree `.claude/worktrees/agent-aeead6f2686f9638a`, base 52ba1e94, temp tag
   `plan1-gate-leaks`). It **dies with this session**. Fast-tier-only reds that the full suite didn't show:
   - `test_art10_menus::test_simulate_starts_the_tutorial_and_overthrow_a_new_campaign`: order-dependent, probably
     a save-slot leak;
   - `test_art0_kit_states::test_a_confirm_sits_on_a_scrim_that_takes_the_page_clicks_and_traps_the_pad`.

   In the new session, check its branch (`git log worktree-agent-aeead6f2686f9638a`). If no useful commit, re-spawn
   the same brief (fix-mechanical, QUICK precommit) or fix by hand.

## Gate PT-002 status
- **Part 1 done**, on 52ba1e94 code. Summary file: `%TEMP%\gate_pt002\summary.txt`.
  - Full suite once: `python tools/run_tests.py -j 4` → 2286 tests, 0 failing, 104 pending (deferred), 716 s wall.
  - Smoke 0, validate 0.
  - Heuristic sweep `docs/playtest/claude/state/SA-004-PT002.md`: 15/20 won, identical to SA-003 (deterministic,
    no regression); boss 25 attempts / 15 wins; Schematics end mean 177.
  - Fast-tier timing: 193 s vs 196 s before the deferred tier. **No measurable saving** (the deferred tier moved
    mostly full-tier work); the full suite is slower than PT-002a's 498 s because it has more tests. Say so honestly
    in the report.
- **Part 2 running:** screen batch + parity, Perfect probe (above).
- **Left to do:** the gate report and tagging (Next steps).

## Decisions and rationale (this session; all logged in docs/DECISIONS.md, newest at the top of "Implementation decisions")
**Scope and process**
- Scope until gameplay is final: **text 1.0 + mouse/keyboard only**. 1.6 / 2.0, high contrast, gamepad and
  accessibility are deferred.
  - Tier `deferred` in `tests/test_manifest.json`, skipped by `run_tests.py` and `select_tests.py`.
  - Helper `tests/helpers/test_scope.gd`: `TestScope.deferred()` and `scales()`.
- **US English** for all player text (test `test_us_english.gd`).
- **Route cheapest first** (memory `route-cheapest-first`): Batch API (Haiku) for patch-shaped work, code-cleanup
  (Haiku) for one diff, Sonnet agents only when Godot runs or captures are needed, Opus only with `OPUS-BECAUSE:`.
  **The designer flagged that I drifted. Use the batch lane for test-expectation / lint / literal-move fixes.**
  - Batch API key: user env var. In PowerShell: `$env:ANTHROPIC_API_KEY=[Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY','User')`.
    Never print it.
- **Precommit:**
  - Agents use `QUICK=1 bash tools/precommit.sh` / `QUICK=1 git commit` (parse + their changed tests only).
  - Merges within a wave use `git commit --no-verify`.
  - The orchestrator runs ONE full diff-selected check per wave batch as a background shell (no model).
  - Default `-j 4`.
  - The full suite runs once per gate only.

**Rulings: features and content**
- **Gate state sweep** = free heuristic strategist (`state_agent.py --strategist heuristic`). The LLM sweep only when
  the designer asks (`gate.py --llm-sweep`).
- **PT-002a** had no screen testers (fixed, tested bugs); screen testers return at PT-002 for the A+B re-test.
- **Inner ring:** round 45 spec (art-pass commit 2216c126, `docs/concepts/round45_inner_ring/NOTES.md`) replaced the
  W2-A6 plates.
  - Twin Pointer: every needle lights its own segment and wedge.
  - ANCHOR / ACCEL / ECHO marks at 1.4× with a keyline; a keyline rule for future modifiers.
- **Resting hand cards** don't grow; a later pass makes them readable at rest (maybe icon only).
- **Boss:** the designer beat the Genome Core easily but found it **boring**. D1 becomes a **content design pass**
  (enemies, bosses, events, raids: what they do, unique fun mechanics), planned after change plan 1, concepts and
  rulings before any build.
- **Raid feed:** "Step N:" became one "— STEP N —" divider per step.
- **CP-002 #7:** hostile tick marks stay off by default (colour-blind setting only), long-term removal.
- **Freeze** targets enemy wheels only (GDD A.2 #15); unchanged.

## Constraints and gotchas discovered
- **Merge conflicts every time** in `docs/DECISIONS.md`, `tests/test_manifest.json` and `assets/text/strings.csv`. The
  tools are in the scratchpad; recreate them if it's gone:
  - `keep_both.py`: keep both sides of conflict blocks;
  - `merge_manifest.py`: JSON union of git stages :2 and :3;
  - `group_sheet.py`: numbered review sheet, stacked at 1600 px wide.

  For `strings.csv`: `git checkout --ours` it, then `godot --headless --path . -s tools/export_text.gd` (regenerates
  from code), then `git add`.
- **Before `git merge` of an agent branch:** remove untracked `*.gd.uid` in main that exist in the branch
  (`git cat-file -e <sha>:<f>` then `rm`), or the merge refuses.
- **After any merge that adds a `class_name`:** `godot --headless --path . --import`, or every dependent script
  fails to compile (stale class cache).
- Agents put DECISIONS entries at the file top (above "Locked design decisions"). Move them under "Implementation
  decisions" as `### date — title`.
- **Precommit's per-file parse check is slow** (~6 s per file; 35 min for ~300 files). For big batches, parse-check
  the changed files yourself and run `run_tests.py --tier fast` instead. One Godot process parsing all files would
  be a good tooling fix.
- **`roll_testers.py --count 0 --build X`** fails on a missing batch.json after checking out. The checkout still
  worked; run `godot --headless --path .claude/worktrees/playtest-build --import` yourself. Untracked `.uid` files in
  the playtest-build worktree block its checkout; delete those that are tracked on main.
- **Labs and captures used to write the player's `settings.json`**, which set reduce_effects ON and skipped every
  playout. Fixed in 1B-PLAYOUT (windowed runs use `settings_windowed.json`). If the designer reports skipped
  animations, check `%APPDATA%\Godot\app_userdata\REBEL_CELL\settings.json`.
- **Never `python -` with a heredoc**: it hangs on stdin (done twice this session). Never pipe Godot output.
- **TaskStop on agents:** the designer refused it once. Prefer messaging the agent to stop and commit WIP.
- **Agents hand back while their own background runs are still alive**, then re-notify repeatedly. Merge from the
  branch and ignore the repeats.

## Verification status
- Gate PT-002 part 1 as above (full suite PASS on 52ba1e94).
- Batch checks: fast tier on d086ca5a = 1531 tests, 0 failing, 67 pending (fast, smoke and validate all 0); pushed.
- **Not yet run:** the full suite on 84c8aa3e. It only adds route data, so it's covered by the 52ba1e94 run.
- Art-pass session (REBEL_CELL art direction and integration) APPROVED:
  - W1b + W2 (with the ring item replaced by round 45);
  - W2 R2 (round 45 ring + INCOMING) after three polish items, all merged in 52ba1e94 / d086ca5a.

  No further review loop is owed for wave 2.

## Next steps
1. Wait for part 2: check `%TEMP%\gate_pt002\gate_combat.log` and `probe_quiz.log`, and that
   `docs/playtest/claude/gates/PT-002.md` exists.
2. Leak-fix agent: merge its branch if done (QUICK checks), else redo. Re-run `python tools/run_tests.py --tier
   fast` once to confirm 0 failing.
3. Write the gate report `docs/handoff/gates/PT-002.md` (template `docs/process/templates/GATE_REPORT.md`):
   - verdict;
   - screen batch vs PB-010 (replay audit: tester Perfect rate vs the ~20% baseline; deaths; damage vs best plan);
   - parity vs PB-015;
   - Perfect quiz vs PB-013;
   - sweep SA-004;
   - the timing finding;
   - retrospective (agents × model, batch tokens = 0 so far: say so; hook denials);
   - light replan: wave 3 next, then the input-prompt pass + rewards screen, then the content design pass.
4. Set the build sha in `docs/playtest/PT-002_plan-1-waves-1b-and-2-combat-legibility.md` (draft already written,
   20 steps, ~34 min; header says "main @ (set at the gate)").
5. Commit, `git tag gate/PT-002`, then push through the push gate: parse a summary file for suite / fast / smoke /
   validate = 0 and a matching sha, never chain push after grep (memory `push-gate`).
6. Hand the designer the PT-002 list, then STOP and wait for feedback (CP-002 rule 1). Triage their feedback before
   acting.
7. Update `docs/handoff/STATE.md` (its "Current goal" block is long; trim and refresh it).

## Open questions for the user
- None blocking. After PT-002 the plan says wave 3 (city clarity, with F1/F2 HQ fixes, R5–R8, smear notches); the
  designer will rule after their playtest.
