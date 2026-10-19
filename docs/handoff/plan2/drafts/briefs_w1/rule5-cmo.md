<!-- W1 brief via Message Batches, claude-sonnet-5-5, batch msgbatch_01XJNbnNCPMUUX88XP2A5B47, custom_id brief__rule5cmo; status ok; tokens in 8868 cache-write 0 cache-read 33457 out 1487; cost $0.020. DRAFT brief: not yet dispatched. -->
<!-- shortened by a second pass (compress), cost $0.012 -->

# RULE5-CMO: city_map_overlay R5 literal-to-const remainder

- **Goal**
  - Replace ~12 inline literals in `scripts/ui/city_map_overlay.gd` with named consts carrying `##` docs. Values stay identical, with no behavior, layout, or visual change.
  - The overlay stays (not retired). This finishes the R5 items left after W0 RULE5b.
- **Base / tag:** `<BASE_SHA>` / `<TEMP_TAG>`
- **Agent type and lane:** Batch const_edits (Sonnet) drafts, then fix-mechanical (Sonnet) applies and verifies. No Opus: no RNG, save format, damage order, or determinism contract is touched.
- **Depends on:** none (not NA-26).

## Read first
- `docs/process/agent_rules/common.md` (no magic numbers, `##` docs, motion rule).
- `docs/handoff/RULE5_CMO_LINES.md`, written by the Batch step. Per R5 line: line number, literal, proposed const name, classification (layout / color / motion timing / count).
- No designer Q rulings apply. Q19 (preview "?" rule) is out of scope.
- Run `python tools/batch/context_slice.py --deps scripts/ui/city_map_overlay.gd`. Don't read the whole file.

## Files
- `scripts/ui/city_map_overlay.gd` (only owned file).
- `content/config/ui_motion.tres` + lab demo: only for motion timing literals (REQUIRED_IDS entry + lab demo).
- `tests/test_manifest.json`: only if a test is added.

## Acceptance
1. Every line in `RULE5_CMO_LINES.md` is replaced by a const. Remaining R5 literal count is 0 (grep check in report).
2. Each const has a `##` doc and a value equal to the replaced literal (per-line before/after table in report).
3. Layout/color consts stay in the file. Timing literals go to `ui_motion.tres`.
4. Diff shows only literal-to-const swaps and const declarations. No signature, node path, or signal changes.
5. The raid map overlay still opens, and its existing flow test passes unchanged.
6. `QUICK=1 bash tools/precommit.sh --base main` is green. Don't run the full suite.

## Tests
- Run the existing raid-map and city-overlay flow tests, unchanged.
- If any value moves to `ui_motion.tres`, run the existing ui_motion REQUIRED_IDS and lab tests.
- No new rule test: view glue only (CLAUDE.md rule 6). No test plan exists.

## Not in scope
- Retiring or redesigning the overlay, NA-26 views, Remove Site names.
- Motion timings in `combat_fx_layer` and `wheel_view`.
- Value changes and new strings (no `export_text` re-export).
- Captures: none intended. If taken, before|after to `docs/art_review/`.

## Conflicts
- `city_map_overlay.gd` is not in REPLAN C.2 shared areas, but NA-23's overlay work (Remove Site names) may touch it. Merge this slice first, or rebase on that one.
- `ui_motion.tres` is shared with the RULE5b motion consts. Rebase before editing.

## Report
RESULT envelope per `docs/process/agent_rules/common.md`:
```
RESULT <round tag> RULE5-CMO
status: DONE | HANDOFF | BLOCKED
commit: <sha> on <branch>
checks: precommit=<0/1> (sha <sha>)
items: <n> done / <n> listed
- <item id>: done — <test name or capture path>
- <item id>: differs — <one line why>
notes: <≤ 5 lines>
```

Q: Should literals that are clearly shared with `wheel_view` or `combat_fx_layer` (for example the same fade span) move to one shared `ui_motion.tres` id, or stay a local const here?
