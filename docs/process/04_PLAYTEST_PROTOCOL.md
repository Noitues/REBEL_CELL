# 04 — User-Ready Gates and the Human Playtest Checklist

A **User-Ready Gate** is reached when a feature, a screen port, a milestone group or a major fix is
merged on `main` with the gate checks green (full suite once in isolation, smoke, validate, the
windowed checks where rendering changed, push gate). At that point the orchestrator produces one
**Human Playtest Task List** and, with it, the pending checkpoint batch (doc 02 §5). Nothing after
a gate starts until the playtest feedback is ingested or the designer says to go on.

Gates so far map to: each M14 group end, ART-12, each queued pass, each R7/G re-evaluation batch.
Smaller slices do not get a gate; their checks are the agent hand-back and the merge wave.

## 1. Generating the list

```bash
python tools/playtest/make_playtest.py --since <last gate tag or sha> --id PT-013 --title "Group 3 city"
```
writes `docs/playtest/PT-013_group-3-city.md` from the template with the scope prefilled: changed
screens (from the changed paths under `scripts/ui/`, `scenes/`, `content/`), new or changed
settings, new content ids, and the DECISIONS entries since the tag. The orchestrator then fills in
the steps by hand (10–25 steps; one gate, one list). Tag the gate: `git tag gate/PT-013`.

Steps are written for the designer running the game from the editor or `godot --path .`:
- Every step names **where** (screen, how to reach it in ≤ 3 actions), **what to do** (one
  action), **what to look for** (one observable), and the **PASS criterion** (one sentence a
  non-author can judge). Expected values come from the GDD / config, with the config key.
- Deterministic flows give the **seed** (campaign code or `--seed`) so a FAIL is reproducible;
  the list says how to enter it.
- Settings axes are explicit steps, not a matrix: text scale 1.0 / 1.6 / 2.0, pad and mouse,
  reduce effects, high contrast, the skin — only the ones the gate changed.
- Known limits are listed up front so they are not reported as FAILs.
- Captures are not required from the designer; a path for a screenshot is offered per step.

## 2. The template (`docs/process/templates/PLAYTEST.md`)

```markdown
# PT-<nnn> — <title>            gate/<tag> · main @ <sha> · <date> · build: run from the editor (F5) or `godot --path .`

## 1. Scope and changes (what is new for you)
- <screen or system>: <one line: what changed, user-visible>        (ART-n / H-n / DECISIONS anchor)
- ...
Known limits (not FAILs): <list, or "none">
Settings touched: <text scale / pad / reduce effects / skin / none>
Seed for the campaign steps: <code>  (Title → NEW RUN → CODE → paste)

## 2. Playtest steps
| # | Where (reach it) | Do | Look for | PASS when | Time |
|---|---|---|---|---|---|
| 1 | Title → OPTIONS → DISPLAY | set Text scale 1.6 | the whole options page | nothing clipped or overlapping, every label readable | 1 min |
| 2 | HQ (new run, seed above) → GRID | hover each Site marker | the marker tooltip | name, corp seal and owner match the key; no "KEY_" text | 2 min |
| ... |
Total: ~<n> min

## 3. Expected vs actual (how to judge)
PASS = the "PASS when" sentence holds at first sight. FAIL = it does not, or anything crashes, hangs,
shows a KEY_/rules-English string, loses input, or looks wrong for more than a second.
PARTIAL = passes with a nit you would still ship (say what). SKIP = could not run the step (say why).

## 4. Feedback (paste back as is)
PLAYTEST: PT-<nnn>
STATUS: PASS | FAIL | PARTIAL
STEPS: <step: PASS/FAIL/PARTIAL/SKIP, only the ones that are not PASS, e.g. "3 FAIL, 7 PARTIAL">
LOGS: <optional: path to the Godot log, or paste the ERROR lines>
NOTES: <optional: free text; one line per step, "<step>: <what you saw>">
RULINGS: <optional: answers to the checkpoint items shipped with this list, "1A 2C">
```

## 3. Ingesting the feedback (orchestrator, quick loop)

1. Parse the five lines. `STATUS: PASS` → the gate closes: log "PT-nnn PASS" in DECISIONS, untag
   nothing, move on (STATE.md next action).
2. Every `FAIL` / `PARTIAL` step → one **finding** with the step's "Look for" and the designer's
   note, reproduction = the step + seed, severity: FAIL = P1 (fix before the next gate), PARTIAL =
   P2 (fix in the next slice). Each finding gets a slice item (nothing deferred); P1s may spawn a
   fix agent at once.
3. `SKIP` → the step was not runnable: fix the list (a missing entry path, a wrong seed) and
   re-ask that step only.
4. `LOGS` ERROR lines → grep the names against the changed files; attach to the finding.
5. `RULINGS` → DECISIONS entries by checkpoint id, GDD lines updated.
6. After P1 fixes merge: a **re-gate** list with only the failed steps (`PT-nnn-b`), same seed.
   P2s ride the next gate's list.
7. STATE.md: the gate row gets PASS/FAIL, the finding ids, and the re-gate id.

## 4. What the orchestrator must not do at a gate
- Ship a list longer than ~30 minutes of play; split by screen instead.
- Mix two gates' changes in one list, or ask rulings that are not in the checkpoint file.
- Ask the designer to read diffs, logs or test names: the list is the only thing they need.
- Treat a PASS as approval of the look: visual approval stays with the art-direction session.
