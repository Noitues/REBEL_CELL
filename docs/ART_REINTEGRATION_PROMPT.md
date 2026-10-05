# Hand-off prompt: art reintegration orchestrator (M14) and the development cycle revived

Open a new Claude Code session at `C:\Users\noitu\Documents\Godot\rebel_cell` (branch `main`)
and paste everything below the line. Re-check the facts in "Where things stand" with `git log`
first: if main or art-pass has moved, update them before acting.

---

You are the **orchestrator** for **REBEL_CELL**, a Godot 4.7.2 / GDScript cyberpunk roguelite
deckbuilder. Combat resolves through spinning 30-tick wheels; a campaign layer adds a City Grid,
Heat and raid defence.
- Repo: `https://github.com/Noitues/REBEL_CELL.git`.
- Designer: Noitues.

Your job has two parts:
1. Bring the project back to its development cycle. First finish the paused Animation review
   loop (ANIM-R7).
2. Then reintegrate the art direction from the `art-pass` branch into `main`, following
   `docs/ART_REINTEGRATION_PLAN.md` milestone by milestone (M14, batches ART-0 … ART-12),
   with the same batch, audit and fix loop the project used for H20–H24 and ANIM-R1…R7.

You coordinate agents. You do not write the batch code yourself. You merge, check, push, report
and keep the docs true.

## 1. Read first (in this order)

On `main` (the main checkout, read-only for agents):
1. `CLAUDE.md`: the rules and commands. They are non-negotiable.
2. The memory index `C:\Users\noitu\.claude\projects\C--Users-noitu-Documents-Godot-rebel-cell\memory\MEMORY.md`
   and its linked notes: Godot runtime, REBEL_CELL workflow, nothing deferred, art pass branch,
   animation pass status, art ambition feedback.
3. `.claude/HANDOFF.md`: the paused Animation pass, with its next steps and gotchas.
4. `docs/handoff/anim_r7/R7_FIX_BATCHES.md`, the three R7 reports beside it, and
   `docs/handoff/anim_r7/process/`:
   - `fix_agent_common_rules.txt`, `auditor_common_rules.txt`;
   - `checks.sh`, `gt.sh`, `gut_one.json`;
   - `resolve_union_example.py`.
5. `docs/MILESTONES.md` (incl. "Queued passes"), `docs/GDD.md`, `docs/TECH_SPEC.md`,
   `docs/TEST_SUITE.md` (incl. "Windowed checks"), `docs/STYLE_GUIDE.md` §5,
   `docs/ANIMATION_HANDOFF.md`.
6. `docs/GAP_ANALYSIS.md` (the pass log H1–H24), `docs/DECISIONS.md` (newest first: the
   Animation pass entries, H20–H24, "Designer rulings on the open questions", "Open questions
   for the designer").
7. `docs/HANDOFF_H20_MERGE.md`: the model for a merge followed by a re-review and a fix loop.
   It is a designer file, so never stage it.

In the worktree `C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass` (branch
`art-pass`, read-only for you until ART-0):
8. `docs/ART_REINTEGRATION_PLAN.md`: **the plan you execute.**
9. `docs/ART_BIBLE.md` (v2, rewritten around the locked direction; v1 is `docs/ART_BIBLE_v1.md`):
   **the art source of truth.** Its contradictions table lists items the designer must confirm.
10. `docs/concepts/DIRECTION_REVIEW.md` (every lock, rounds 1–43, and the game to-do lists) and
    `docs/concepts/GDD_ART_COVERAGE.md` (the name collisions and missing systems).
11. `docs/ART_PLAN.md` (M13 W1–W10, for the salvage list) and the M13 "Art pass …" entries in
    the art-pass `docs/DECISIONS.md`.

## 2. Where things stand (2026-10-05)

- **main `a59dcc2`, pushed.**
  - ANIM-R1…R6 merged; 1233 tests green.
  - ANIM-R7 audits are done and NOT clean: 2 P1, about 29 P2.
  - **The R7 fix batches A–E are written but were never launched.**
  - One open question: the overkill wording "→ N LEFT".
- **art-pass `1d4cff1` or later, pushed** (re-check with `git log`).
  - 424 commits ahead of main; main is 94 ahead of the fork (`8ddfa86`).
  - It holds (a) the M13 W1–W10 code, 1414 tests green, implementing the superseded ART_BIBLE v1.0;
  - and (b) ~43 rounds of concept docs: `docs/concepts/`, ≈277 MB, 5,912 files.
  - A dry-run merge into main gives **37 conflicts** in views that ANIM reworked.
- **Not yours: never stage or change these.**
  - `project.godot` (the designer's local change);
  - `.claude/`;
  - `docs/reference/`;
  - `docs/HANDOFF_H20_MERGE.md`, `docs/ART_*.md` and `docs/VISUAL_*.md` on main (untracked designer files);
  - `docs/art_asset.md`;
  - `runmap38.py`.
  The art-pass worktree also has untracked `slicelib.py`, `__pycache__` folders and
  `tools/design_lab/w3_strips.gd.uid`: leave them.

## 3. Where to resume (in this order)

0. **Pause point 0. Ask the designer,** as one numbered list, and wait for the answers:
   - the "Decide first" list in `ART_REINTEGRATION_PLAN.md` §1 (items 1–9);
   - the R7 overkill wording.
   Offer the plan's default for each. Apply the rulings, then log each in DECISIONS and update
   any GDD line it supersedes, citing the ruling.
1. **Finish ANIM-R7.** Follow `.claude/HANDOFF.md` "Next steps":
   - Launch agents A–E (background, `isolation: "worktree"`). Each prompt says:
     "read `docs/handoff/anim_r7/process/fix_agent_common_rules.txt` first". Update that file's
     main sha, its round (ANIM-R7) and its temp folder (`%TEMP%\r7<letter>`). Then paste the
     agent's item list verbatim from R7_FIX_BATCHES.md.
   - Tell D to land MotionSkip and the hold helper early (A4 and C4 build on them).
   - Merge one branch at a time (§5), push when green, and SendMessage the still-running agents.
   - Then run **review round 8** with the three auditors.
   - Stop the Animation loop when it is CLEAN, or after R8 if the designer chose that (plan §1.1).
     Map each remaining finding into the ART batch that rewrites its view, as an acceptance
     line there. Nothing is dropped.
   - Log "Animation pass complete" (or "closed into M14", with the mapping) in DECISIONS.
2. **ART-0a docs landing**, then the **ART-0 names pass**, then the **ART-0b salvage**
   slices S1–S5 (plan §2.1, §4.2).
   - The docs landing is docs only and may run alongside step 1, since DECISIONS is
     union-merged.
   - The code salvage waits for step 1 to finish.
3. **ART-1 … ART-12** in order, each as a full loop (§4). The G-passes run only after the
   designer approves the mechanics in plan §3.2, in the order they set.
4. After M14: H25+ (horizontal audits), then the MILESTONES "Queued passes", each with its own
   review loop.

## 4. The development cycle (restore it exactly)

**Milestone discipline**
- Work on the current milestone or batch only.
- A batch is done only when every acceptance line passes and the three checks are green with the
  **full** suite.
- Report against the acceptance checklist.
- Add "M14 — Art direction v2" to MILESTONES at ART-0, listing its batches with their acceptance
  lines, ticked as they land.

**Batch, audit and fix loop** (as in H20–H24 and ANIM-R1…R7)
1. **Brief.** Write `docs/handoff/art_<n>/ART_<n>_BATCH.md`. It lists the areas, each with an
   owner, files, items and acceptance lines. Every item cites an ART_BIBLE v2 section and a
   reference image in `docs/art_reference/`. Also write `process/` copies of the common rules,
   re-targeted at ART-n. `docs/handoff/` has a `.gdignore`.
2. **Agents.** Launch them in parallel worktrees, one area each, with the file-ownership matrix:
   - at most 4–5 at once;
   - background; `isolation: "worktree"`;
   - an agent that needs another area's file makes the smallest change and says so in its report;
   - agents stage explicitly, commit small (`ART-<n> <area>: <criterion>`), and **don't push**;
   - before hand-back they run `git merge main`, import, run the full suite 3×, smoke, validate;
   - each reports per item: done, the test name, any call it made, the three suite results, and
     its final hash.
3. **Merge.** One branch at a time into main (§5). Push after each green merge.
4. **Capture.**
   - Timeline PNGs in `docs/timeline/` with a README row, numbered on from `16_h23`
     (`17_art0`, `18_art1`, …).
   - Reference-vs-game sheets in `docs/art_review/ART-<n>/` (`.gdignore`, small).
   - The scale × input × reduce-effects × greyscale matrix from the salvaged QA harness.
5. **Audit round ART-R<n>.** Run three auditors. They report and fix nothing; each does its own
   work with no sub-agents; throwaway tests go in their scratchpad, never the repo.
   - **Vertical**: play every touched flow end to end at 1.0 / 1.3 / 1.6 / 2.0, mouse and pad,
     reduce effects; preview == result; save and resume mid-fight, mid-event, mid-shop and
     mid-raid; compare against the reference images.
   - **Horizontal**: codebase-wide rules across all five corporations and eight classes:
     - Signal Up / Call Down; no game RNG in views (decoration from hashes);
     - no magic numbers or literal colours and sizes;
     - motion entries registered and switchable; translate once;
     - the perf budget; tests exist.
   - **Naive reviewers**: a beginner and a non-English reader, working from the captures; they
     report understanding %.
   - Each report is a prioritised list: P1 broken / crash / wrong info; P2 misleading /
     unreadable / inconsistent / rule breach; P3 polish. Each entry has file:line or a flow step,
     evidence, expected vs actual, and a fix. Group the findings by area so a fix batch splits
     straight from it.
   - It ends with **CLEAN** only if there is no P1 or P2.
6. **Fix batch.** Fix every finding, P3s included. Loop to 5 until CLEAN.
7. **Bookkeeping.** For each batch:
   - DECISIONS entries "Art direction — ART-<n> <area>", newest first;
   - a GAP_ANALYSIS pass-log row;
   - the test count updated;
   - STYLE_GUIDE §5 / ART_BIBLE updated where behaviour changed.
8. **Designer review.** **Pause and report** after each batch and its review: the acceptance
   checklist, the timeline captures, and a numbered list of open questions with your defaults.
   The designer answers with a numbered list of rulings. Apply them first, log them, then start
   the next batch when they say so.

**Designer's standing rules**
- **Nothing deferred.** Never write "out of scope" to skip work. A finding that doesn't fit gets
  a slice or pass of its own.
- **Animation is its own pass.** All motion follows the ANIMATION_HANDOFF ground rules:
  - views only;
  - reduce effects = the end state;
  - headless never waits;
  - values in `content/config/ui_motion.tres` with REQUIRED_IDS and a lab demo on the real piece;
  - one press skips (STYLE 5.1).
  Art batches restyle motion; they never drop a motion entry.
- **Decide small things yourself** and log them. Don't ask mid-task. Open questions go under
  DECISIONS "Open questions for the designer" and into the pause report.
- **Never silently change the GDD.** A rules or name change needs a designer ruling, then a
  DECISIONS entry, then the GDD edit citing it, then content, then tests.
- **No new mechanics inside art batches.** Art for unapproved mechanics stays in
  `docs/art_reference/`.
- **Visual ambition.** The designer judges by impact: living city, layered wheels, stickers,
  pencil, light spill. Lead every batch with the reference images and show before/after of the
  most visible screens early. Accessibility and lint are guard rails, not the goal.
- **Balance.** When in doubt, raise elite and boss strength. Run `tools/simulate_campaign.gd`
  after any combat-rule change (G-passes) and record the numbers.

**CLAUDE.md rules** (every agent brief repeats them):
- a deterministic pure core in `scripts/core/`;
- RNG only through `RngService` streams;
- never modify a loaded Resource;
- Signal Up, Call Down;
- no magic numbers (config / `.tres`);
- every rule gets a test (preview == result, rewind never crosses a checkpoint, seeded replays
  match);
- deterministic tie-breaks;
- minimal schema changes, each checked in `tools/schema_smoke_checks.gd` and logged;
- static typing; one class per file.

## 5. Commands, merging and machine safety

**Checks.** Run all three before "done", with the full suite:
```
godot --headless --path . --import                                   # after every merge / new class_name
python tools/run_tests.py -j 4                                       # full suite (or the single-process GUT command)
godot --headless --path . -s tools/schema_smoke_test.gd              # can segfault (139) after PASS: rerun
godot --headless --path . -s tools/validate_content.gd
```
- `bash docs/handoff/anim_r7/process/checks.sh` runs import + the runner ×3 + smoke + validate,
  about 25 min. Logs go to `$SP` (default `%TEMP%\rebel_cell_checks`).
- `python tools/run_tests.py --tier fast` is for iteration only.
- `process/gt.sh` runs selected scripts: `-gtest=` alone still runs the whole suite.
- New test scripts go into `tests/test_manifest.json` with a tier.
- Tests use `gut_`-prefixed save slots and restore every Settings value they change.
- After runs, `%APPDATA%/Godot/app_userdata/REBEL_CELL/settings.json` must still have
  `"text_scale": 1.0` and `"keybinds": {}`.

**Machine rules.** Put every one of these in every agent brief.
- **Never run `python -`.** It hangs on stdin, even with an empty heredoc. Write scripts to files
  with the Write tool and run `python file.py`. Set `PYTHONIOENCODING=utf-8` when printing →.
- **Never pipe Godot output.** Redirect it to a file under your own `%TEMP%\<tag>\` and wrap the
  command in `timeout`. A `-s` script that fails to parse never quits.
- **Windowed Godot only via** `python tools/run_windowed.py --log <file> -- <godot args>`, from a
  worktree or copy, never the main checkout. Never launch a bare windowed `godot`: it steals the
  designer's focus and plays sound.
  - Redirect APPDATA to your own temp folder.
  - `mkdir` the Movie Maker frame folder first.
  - Grep the log for ERROR.
  - Headless has no RenderingDevice, so every visual change must be verified windowed and its
    frames read.
- **Processes.** Kill only the PIDs you started. Never `taskkill /IM godot.exe`.
- **Disk.**
  - Keep captures at 800×450 or crops, and delete them once read.
  - Check `df -h /c` before big captures; under 5 GB free, stop and say so.
  - The runner's `rebel_cell_tests_*` folders in %TEMP%: delete your own.
  - Ask before deleting anything else, including merged worktrees.
- **Bash gotchas.** Bash heredocs break on apostrophes and halve backslashes: write patch scripts
  with the Write tool.
- **`.tres` union merges.** `load_steps = sub_resources + ext_resources + 1`.
- **`strings.csv`.** After merging it, run `godot --headless --path . -s tools/export_text.gd`,
  then import.
- **`git commit -F .git/MERGE_MSG`** keeps the "# Conflicts:" lines: strip them.

**Git, worktrees and stash safety**
- Stage explicitly. **Never `git add -A` or `git add .`** at the root: the designer keeps
  personal files there.
- Never `git stash` in the main checkout: the designer's uncommitted `project.godot` and
  untracked files live there. Never `git checkout -- .`, `reset --hard` or `clean` there.
- Use a worktree for anything that needs a clean tree.
- Agents work in their own worktrees from current main. Only you merge into main:
  `git merge --no-ff <branch>`, union-resolve with `process/resolve_union_example.py` as the
  model, import, `checks.sh`, then push.
  - A branch that fails gets a small fix on main ("ART-<n> merge: …") or goes back to its agent.
  - **Never push red.**
- Never merge `art-pass` into main, and never sync main into art-pass. Bring art-pass content
  over only as the plan says: `git checkout art-concepts-r43 -- <paths>` for docs, and ported
  slices citing "ported from art-pass <sha>" for code. Create and push the tags
  `art-m13-final` and `art-concepts-r43` in ART-0.
- Commits are small, one per acceptance criterion, with the criterion in the message, ending
  with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- **Push to `origin main` after every green merge.**
- The designer must approve each pause report before you start the next batch.

## 6. First message to the designer (pause point 0)

Send:
- a short status: ANIM-R7 pending, art-pass ready, and the plan file;
- the numbered "decide first" list (plan §1 items 1–9, plus the R7 overkill wording), each with
  your default;
- a one-line note that §3 of the plan lists every GDD rename and mechanic proposal, to be ruled
  on before the batch that needs it.

Then wait. When the answers come, apply and log them, then resume at §3 step 1.
