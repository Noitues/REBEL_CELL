# Common rules for every REBEL_CELL agent (stable; referenced by path from briefs)

Read this file, then your area file (`docs/process/agent_rules/<area>.md`), then the brief footer.
Do not read DECISIONS.md whole: `grep -n "<topic>" docs/DECISIONS.md` and read the lines you need.
Do not read source files whole before you need to edit them:
`python tools/batch/context_slice.py --deps <file>` gives signatures and doc comments.

## Start
1. `git log -1` — your worktree must be at or above the base sha in the footer; else `git merge main`.
2. `godot --headless --path . --import > "$TEMP/<tag>/import.log" 2>&1` (always after a merge that adds class_names).
3. Work only on the items in the footer, in the files you own. A fix that needs another area's file:
   smallest change, say so in the report.

## Code rules (CLAUDE.md, enforced by tests)
Deterministic core (`scripts/core/`, `scripts/state/` pure RefCounted, no Nodes); randomness only via
`RngService` streams passed in; loaded Resources are read-only (runtime values in `scripts/state/`);
Signal Up / Call Down (views never change state); no magic numbers (tuning in `content/config/*.tres`;
motion timings in `content/config/ui_motion.tres` with a REQUIRED_IDS entry and a lab demo); ties by
content id then node id; static typing, snake_case, `##` on public functions, one class per file.
Every **rule** gets a test (preview == result, rewind never crosses a checkpoint, seeded replay
matches). View glue needs no unit test; a flow test per screen and the playtest gate cover it.
Text reaches the player only through TextDb keys (`strings.csv`; re-export with
`godot --headless --path . -s tools/export_text.gd`, then import). Layout holds at text scale
1.0 / 1.6 / 2.0; reduce effects = end state; headless never waits.

## Tests
- New test script → `tests/test_manifest.json` with a tier (`fast` for rules, `full` for sweeps).
- Bounded waits only (`tests/helpers/bounded_wait.gd`); no frame-signal lambdas; restore every
  Settings value you change; MotionSkip registration for anything that animates.
- Iterate with `bash tools/precommit.sh` (staged) — seconds to a minute. Hand back after
  `bash tools/precommit.sh --base main` is green. **Do not run the full suite**; the orchestrator
  runs it once at the gate.

## Machine rules (non-negotiable)
- Never `python -` (hangs on stdin). Write a `.py` file and run it.
- Never pipe Godot output: redirect to a file under `%TEMP%\<tag>\` and wrap in `timeout`.
- Windowed runs ONLY via `python tools/run_windowed.py --log <file> -- <godot args>` from your
  worktree (never the main checkout, never a bare windowed godot: it steals focus and plays sound).
  Make the Movie Maker folder first. Read frames as a contact sheet, not one by one; delete them after.
- One Godot window at a time; kill only PIDs you started; never `taskkill /IM godot.exe`.
- Disk: check `df -h /c`; under 5 GB free, stop capturing and say so. Delete your `%TEMP%\<tag>\`
  folder before hand-back, except the report files.
- Git: stage explicitly (never `git add -A`); never touch `project.godot`, `docs/reference/`,
  `.claude/`, `docs/ART_*.md`, `docs/VISUAL_*.md`. Small commits "<round tag> <area>: <criterion>",
  ending with the Co-Authored-By line from the footer. Do not push.
- Context: at 60 % of your window, stop, write `docs/handoff/STATE_<area>.md` from
  `docs/process/templates/STATE_HANDOFF.md`, commit, and report `status: HANDOFF`.

## Report (your final message; the orchestrator reads only this)
```
RESULT <round tag> <area>
status: DONE | HANDOFF | BLOCKED
commit: <sha> on <branch>
checks: precommit=<0/1> (sha <sha>)
items: <n> done / <n> listed
- <item id>: done — <test name or capture path>
- <item id>: differs — <one line why>
notes: <≤ 5 lines: files outside the area, NEEDS lines, Q: questions>
```
