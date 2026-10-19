# Handoff — REBEL_CELL (build session, W1 of REPLAN_2026-10-16)

| | |
|---|---|
| Written | 2026-10-18 (evening) |
| Branch | main (pushed at gate/PT-004 b98e1def; later W1 merges are local until the PT-005 gate) |

## State
- Plan 2 / W0 closed: PT-004 automated gate passed and pushed (playtest skipped by designer).
- **Overnight directive (designer):** don't wait for decisions: take defaults, log them in DECISIONS. If PT-005 is
  reached before 07:00 2026-10-19, run its automated gate (full suite once, smoke, validate, push gate), then go to W2
  unless a replan is needed (themes, WATER LEVEL, exploit buildings, Q24.1 death likely need one: Batch-draft it, then
  start the next wave). Memory: `overnight-run-2026-10-18`.
- Defaults already logged: DECISIONS "Overnight: defaults taken on open calls".

## W1 status (briefs: `docs/handoff/plan2/drafts/briefs_w1/` + README queue rows)
- Merged: NA-21, NA-22/22b/22c/22d, NA-23, NA-24, NA-25 (+fix), NA-11, NA-11b, NA-04b/c, OCCBAND, OCC-OUTLINE,
  LAMPSHIFT, N8, N9, N20, N6, N7, N12. Replan draft for W2+: `docs/handoff/gates/REPLAN_2026-10-19.md`.
- NA-26 (street on by default, old route page retired): merge BACKED OUT twice for reds; its agent is fixing 4 tests
  (pass24 translated twice, pass21_city route tooltips, anim_r5 route move, motion_lab orphaned route_* ids).
- NA-04d merged (a35b41b0): 12.6 by depth.png, R-REP-1 facade band, drift vs art-pass 7772e6ba = 0 DRIFT (sent to art-pass).
- Running: NA-11c (spike cap 1.6x, 6-10 floors, sky >= 15 %, HQ proximity 0.6x landmark), NA-23b (span so every
  room >= 46 px, Meridian seed-1 capacity; Python + twin).
- Next (art-pass fix lists, ART_REPLIES items 11-13): NA-23b (derive: every room >= 46 px, Meridian seed 1 capacity),
  NA-23c (NA-22c look in DECISION/HOVER, cutaway rooms, quieter lanes, closed facade for unrevealed rooms, depth.png),
  NA-24c (sign core+panel, blade hero signs, district palettes table, rooms -25 %), NA-25b (+ blotch fix: wet mask,
  wash vertical faces only), NA-24b, N12b, NA-ID, CAP-W1, Q19-PREVIEW, MOTION-TIMINGS, RULE5-CMO, NA-12. Then PT-005.

## Art-pass session
`local_9bc8d6cd-...` ("Resume Art-Pass"); reads spec from art-pass and re-import text into
`docs/handoff/netrun_art/`. Pending from it: W1_NA22 approval after NA-22c; W1_NA23 sheet review. Theme rules drafts
(`docs/handoff/plan2/drafts/themes/`) answer its corp_themes questions; send it rulings as they land.

## How to work
Lanes: Batch for drafts; fix-rules defaults to Sonnet (Opus only with OPUS-BECAUSE); 2 Godot + 1 Python slots.
Merge: union `tests/test_manifest.json` (stages :2/:3), keep both in DECISIONS, smoke-check chain line + both funcs
(check every func still ends with `return fails`), import after new class_names, never a bare `.sort()` on ids
(`IdSort.sort_ids`; allowlist int sorts in `tests/unit/test_no_bare_id_sort.gd`).
