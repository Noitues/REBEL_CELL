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
- NA-04d merged (a35b41b0): 12.6 by depth.png, R-REP-1 facade band, drift vs art-pass 7772e6ba = 0 DRIFT (sent to art-pass).
- Merged 2026-10-19 (all art-pass APPROVED where visual): NA-26, NA-11c, RULE5-CMO, MOTION-TIMINGS, NA-23b (61029e84),
  CAP-W1/N12b, NA-24c (c983ca7b), NA-23c (fd0c9aa7). DECISION R-REP-1 ~0.62 accepted as warn (art-pass owns the 8 px lag).
- Merged later 2026-10-19: Q19-PREVIEW (3f4e1d46), NA-24b, NA-ID (093308f9), W2 drafts WH-01/EX-01 (b946de66).
- Integration branch `w1-close` (worktree .claude/worktrees/w1-close) = main + NA-25b + NA-12; merge to main when
  art-pass approves both. Agents based on it: street-on-generated-city fix, WH-02 (Opus), NA-31.
- Art-pass held replies 15-18 (art-pass b4a8cb42, docs/concepts/HANDOFF_PACKAGE/PENDING_TO_BUILD.md) = OPEN fix lists:
  - 15 NA-ID-b (QUEUED): ground drawn as class 4 (not hidden), ground-lying compound parts (plaza, aprons, rails) class 4
    via `id_ground` group / glb role, capture.json 1-space indent + sorted + LF + `time` night|day; re-run 3 frames.
  - 16 NA-25b r2 (RUNNING, agent a81de4284bc1f9b35): night-switch crossfade, binary-bit dissolve (ART_BIBLE 1.2),
    jack-in chain confirm (4.6), Grid/Route toggle = 1.1 s camera ease (no dive). Sheet W1_NA25b_r2.jpg.
  - 17 NA-12 r2 (RUNNING, agent adf53274290f3bfd9): water material, sea wall, piers, darker void, day blue; concave bay +
    noise; city.json `coast` + `terrain.hills` (additive); CENTRAL SERVER chip clear of pins. Sheet W1_NA12_r2.jpg.
    Terrain rendering = new slice NA-12c in W2 (before NA-32 HQ scenes).
  - 18.1+18.2 COMBAT-LOCK (QUEUED, on main): nudge lock = wax circle-slash per designer ruling (DECISIONS 34069fe7), word
    chips + toast removed, slash on locked RESPIN; Q19 respin ghost = 9 x 46 px chevrons chasing outside the rim (3.17),
    no dashed ring. Re-send CAP_W1 panel 3 and Q19 panel 2.
  - 18.3 NA-24d (QUEUED, on main): hero blade light spill on facade (1-2 BU, panel hue) + street pool, within over-0.85.
- PT-005 waits for: w1-close merged, 15, 18.1-18.3 merged.
- Gotcha: TaskStop on a backgrounded `git commit` leaves its run_tests/godot children alive; they race the next
  precommit in %TEMP%/precommit_rebel_cell. Kill them (Get-CimInstance Win32_Process match precommit_rebel_cell).

## Art-pass session
`local_9bc8d6cd-...` ("Resume Art-Pass"); reads spec from art-pass and re-import text into
`docs/handoff/netrun_art/`. Pending from it: W1_NA22 approval after NA-22c; W1_NA23 sheet review. Theme rules drafts
(`docs/handoff/plan2/drafts/themes/`) answer its corp_themes questions; send it rulings as they land.

## How to work
Lanes: Batch for drafts; fix-rules defaults to Sonnet (Opus only with OPUS-BECAUSE); 2 Godot + 1 Python slots.
Merge: union `tests/test_manifest.json` (stages :2/:3), keep both in DECISIONS, smoke-check chain line + both funcs
(check every func still ends with `return fails`), import after new class_names, never a bare `.sort()` on ids
(`IdSort.sort_ids`; allowlist int sorts in `tests/unit/test_no_bare_id_sort.gd`).
