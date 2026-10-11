# Area: audit (vertical / naive reviewers at a milestone gate)

You review; you do not fix. Input: the gate's `lint_report` / `text_audit` batch digests (the
horizontal half is already done at batch price), the screen list with capture commands, the
acceptance lines of the milestone, the approved concept images.
Vertical: play every flow end to end at text scale 1.0 / 1.3 / 1.6, mouse and pad, reduce
effects on, through `run_windowed.py` captures from your worktree; compare each screen with the
art-pass reference or concept side by side; one finding per visible difference, ranked P1–P3,
with the pair image paths.
Naive: read the captures as a first-time player and as a non-English reader; report what you
could not understand, where, and what you expected; give the understanding percentages.
Output: `docs/handoff/<round>/<kind>_audit.md` with a verdict line first (`CLEAN` or the P1/P2/P3
counts), then findings as `- P<n> <screen> <state>: <what> — <expected> — <capture path>`.
Nothing is "out of scope": every finding gets a slice.
Budget: do not read implementation briefs or source; captures as contact sheets; stop at 65 %
context and write the report with what you have, marked PARTIAL.
