# Standing rules for every art-pass workstream agent

These rules apply to every workstream brief; each brief repeats the key ones.

## Project and branches
- REBEL_CELL, Godot 4.7.2 / GDScript. Read `CLAUDE.md`, then `docs/ART_BIBLE.md` in full, then the parts of `docs/ART_PLAN.md` for your workstream.
- You work **only** in your own worktree (the path is in your brief), on your branch `art/w<n>-<slug>`, which forks from `art-pass`.
  - Never touch the main checkout at `C:\Users\noitu\Documents\Godot\rebel_cell` (it is mid-merge and belongs to another session).
  - Never check out `main`, never merge, never push `art-pass` or `main`, never force-push.
  - Push your own branch (`git push -u origin <branch>`) after each green commit.
- Stage files explicitly; never `git add -A` or `git add .`.
- Commit messages: one per acceptance item, with the item in the message, ending with:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

## Scope
- **Presentation only.** Never change game rules, content values or balance, save formats, or public APIs and signals. Wrap and extend them instead.
- Don't edit files owned by another workstream (see ART_PLAN §3). If you need a change there, describe it in your report.
- CLAUDE.md rules apply in full:
  - static typing and `##` doc comments;
  - one class per file;
  - no magic numbers: colours from `Palette`, sizes from `UiTheme`, timings in `content/config/ui_motion.tres`;
  - never mutate loaded Resources;
  - signal up, call down;
  - every rule gets a test.
- Schema changes in `scripts/data/` are minimal, go into `tools/schema_smoke_test.gd`, and get logged.
- If ART_BIBLE doesn't answer a question, **decide it yourself** in the spirit of §1 (north star) and §2 (materials). Log the decision in your report (the orchestrator copies it into DECISIONS). Never ask the user.

## Machine practice (Windows; these rules matter)
- Godot 4.7.2 is on PATH. After creating the worktree and after adding any `class_name`, run `godot --headless --path . --import`.
- **Never pipe Godot output.** Redirect it to a log file and wrap the command in `timeout`. A `-s` script that fails to parse never quits.
- **Never run `python -`** (a stdin-reading Python hangs the shell), not even with a heredoc. Write a `.py` file and run `python file.py`.
- Anything windowed (Movie Maker captures, storyboard, motion lab) runs **only** through `python tools/run_windowed.py --log <file> -- <godot args>`, from your worktree. It never takes focus and makes no sound. Create the Movie Maker output folder first; Godot writes nothing into a missing one. Grep the log for `ERROR`.
- Never `taskkill /IM godot.exe`; kill only PIDs you started.
- The schema smoke test can segfault (139) at shutdown after printing PASS. Re-run it before treating that as a failure.
- Headless has no renderer, so GPU paths (city bakes) never run in tests. Verify any render change in a windowed capture.
- The Bash tool can halve backslashes in heredocs, so write scripts that contain backslashes with the Write tool.

## Checks before you report "done"
1. `python tools/run_tests.py -j 4` (the full suite; the fast tier alone never counts)
2. `godot --headless --path . -s tools/schema_smoke_test.gd`
3. `godot --headless --path . -s tools/validate_content.gd`

New test scripts go into `tests/test_manifest.json` with their tier.

## Review output (the designer reviews this folder while work continues)
Write to `docs/art_review/W<n>/` in your worktree and commit it:
- before/after PNGs (keep them web-sized: 1280×720 or cropped strips; no raw Movie Maker frame dumps);
- a `README.md` with:
  - what changed (files);
  - the ART_BIBLE §14 checklist with pass/fail per item for everything you touched;
  - decisions you made (one line each, citing the bible section);
  - what you couldn't do and why;
  - any bible rule you think is wrong (**don't** change the bible yourself).

## Your final report to the orchestrator
Include:
- branch name and last commit;
- a summary of changes;
- the results of the three checks (pass counts);
- review folder paths;
- a decisions list, ready to paste into DECISIONS;
- cross-workstream requests;
- known gaps.

Keep it under 600 words.
