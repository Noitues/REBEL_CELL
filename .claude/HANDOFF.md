# Handoff — REBEL_CELL (build session; start W0 of REPLAN_2026-10-16)

| | |
|---|---|
| Written | 2026-10-18 |
| Branch / commit | main, pushed (see `git log origin/main -1`) |
| Reason | The designer cleared the old session after the plan-only freeze. The weekly token reset is in: **full parallel development resumes.** |

## Goal
REBEL_CELL (Godot 4.7 roguelite deckbuilder). M14, change plan 1 (gates PT-001..PT-003) and change plan 2's design
work are done. Now: **build W0 of `docs/handoff/gates/REPLAN_2026-10-16.md`** (→ gate PT-004, closes plan 2), then W1
to W3 (gates PT-005..PT-007).

## First steps for the new session
1. Read: `CLAUDE.md`, the replan (all of it, esp. §C.1-C.3 and §D), `docs/handoff/plan2/CONTENT_DESIGN_V2.md`
   (R1-R13, N1-N20), the newest entries of `docs/DECISIONS.md`.
2. **Designer answers to the decision sheet** (`docs/handoff/plan2/drafts/questions/DECISION_SHEET.md`, Q1-Q47 and
   A1-A7) arrive in the designer's first prompt. Log them in `docs/DECISIONS.md` (one entry, "Designer rulings
   2026-10-18: decision sheet"), each as `Qn: <choice>`; "default" means the sheet's RECOMMENDED option. A5/A6 go to
   the art-pass session; A7 is ours. Unanswered questions: take the default and list them in the entry as "default
   taken, designer may revisit".
3. Fold the rulings into the W0 briefs (`docs/handoff/plan2/drafts/briefs/`) where they touch them, then cut slices.
4. Start W0 in parallel (limits below).

## W0 (replan §C.1)
- **Art build:** NA-02 → NA-03 → NA-04 (briefs `na02/na03/na04.md`). NA-01 is merged (21a22a52).
- **Content foundation:** N1 → N2 → N3 → N4 → N19, with N11, N13, N14 in parallel (briefs `n*.md`; test plans
  `drafts/test_plans/n*.md`).
- **Queued:** the PANOPTICON rename (display name only; id `civic_core` stays); B-TEACH follow-ups 1-3
  (`docs/art_review/PLAN2/B_TEACH.md`); the B-MENU + C-SCREENS capture sheet; the F-RULE5 remainder (skip files being
  retired); S5 balance sweeps incl. step-0 calibration (specs in `drafts/balance_sweeps/`, feeds N2; tool
  `tools/balance/`, branch `balance`); remove Site names (before NA-23's overlay). The pending HQ camera test
  (`tests/unit/test_hq_b_city.gd`) folds into NA-34.
- **Ordering rules:** replan §C.2 (one slice per merge wave on `netrun_session.gd`: N2 → NA-02 → ...).
- **D6 corrected overrides the replan text:** the City Grid view STAYS (campaign monitoring + raids). JACK IN zooms
  into the netrun; the player can zoom out to the grid and back at will. Only the old 2D route page retires (§C.4).
- **D4 nodes:** REST (heal or swap firmware), Workshop, Cache (vet the minipuzzle); Relay only in unique runs; Ambush
  maybe as an event option; Safehouse and Heat Sink are grid-view nodes; Black Market maybe as an unknown event.

## Design material ready (Batch API drafts, all unreviewed by the designer unless the sheet rules on them)
Index: `docs/handoff/plan2/drafts/README.md`. Rounds 1-3 + the sheet cost about $20 total.
- Round 1: 96 drafts (enemies 50, bosses 2, HQ 7, nodes 6, raids 1, events 30). **Use the `v2/` versions** (revised
  against their critic files).
- Round 2: critic reviews (all FIX; triage by BLOCKER count), stations, slice / card upgrades, inner ring a/b/c, rim
  gates, status + parasite catalogs, Sync Strike, firmware, GDD amendment drafts.
- Round 3: `triage/BLOCKERS.md` (192 blockers; top: phase HP / tick math vs R2 and the 3-4 turn rule), test plans
  N1-N20, `raids/unified.md`, names, balance sweeps, v2 drafts, W0 briefs.
- Netrun art: `docs/handoff/netrun_art/batch/` (spec audit, vision review, landmark drafts, golden plates draft,
  Aurelian DESIGN, Tethys shots, asset matrix). **The spec audit's 3 BLOCKERs** (spec vs D3/D4/Gantry; data contract
  vs D8 with three layout inputs and two building-id forms; Central Server names) must be settled with the art-pass
  session before NA-02 freezes `city.json` / `net.json` / `run_graph.json`.

## Art-pass session (separate)
Lives in `C:/Users/noitu/Documents/Godot/rebel_cell` (branch `art-pass`). It never writes here; we never merge
`docs/concepts` (4 GB). Ownership (D8): art-pass = Blender, look-dev, golden plates, `.glb` exports; we = `tools/netrun_art`
pure modules, checks, GDScript twins, Godot. Its addendum from this session:
`docs/handoff/netrun_art/ART_ADDENDUM_2026-10-18.md`. Address it by session id from `list_sessions`.

## How to work (hard-won rules)
- **Lanes (memory `route-cheapest-first`):** Batch API for patch- and draft-shaped work (`tools/batch/`); code-cleanup
  (Haiku) for one diff; Sonnet agents for Godot runs and captures; Opus only with `OPUS-BECAUSE:`. API key: user env
  var (PowerShell `$env:ANTHROPIC_API_KEY=[Environment]::GetEnvironmentVariable('ANTHROPIC_API_KEY','User')`), never
  printed.
- **Parallelism (replan §C.3):** 3 local agent worktrees (2 Godot + 1 Python-only), cap 5; windowed / GPU jobs one at
  a time; balance sims at most 2; the full suite only at a gate, alone. Agent briefs ≤ 4000 chars (hook): rules file
  path + footer.
- **Checks:** agents `QUICK=1 bash tools/precommit.sh --base main`; one fast tier per merge wave; full suite once per
  gate (rerun-alone verdicts on red, never ×3).
- **Push gate:** write fast / smoke / validate exit codes and the sha to a summary file; push only if
  `fast=0`, `smoke=0`, `validate=0` and the sha matches HEAD.
- **Merges:** conflicts in `docs/DECISIONS.md` (keep both), `tests/test_manifest.json` (JSON union of stages :2/:3),
  `assets/text/strings.csv` (`--ours`, then `godot --headless --path . -s tools/export_text.gd`). Before merging,
  delete untracked `.uid` files in main that the branch tracks. After merges adding a `class_name`:
  `godot --headless --path . --import`. Fresh worktrees need the import before precommit.
- **Shell:** never `python -` or stdin heredocs into python; never pipe Godot output (redirect to a file); windowed
  Godot only via `tools/run_windowed.py`. Git Bash `grep` in pipes can core-dump on this machine: use the Grep tool or
  redirect to a file first.
- **`project.godot`:** the designer's editor re-saves it; `git restore project.godot` when it shows modified.
- **Playtests:** `tools/playtest/gate.py` (aborts on build mismatch); scripted steps runner judged on the Batch API
  (`tools/playtest/steps_judge.py`). CP-002: gather feedback, act on none until the designer rules.
- Untracked `docs/HANDOFF_H20_MERGE.md`, `docs/art_asset.md` belong to the designer: leave them.
- Local tags `archive/worktree-agent-*` hold 11 old unmerged M14 branches (restorable); `worktree-agent-a71a521e…`
  is the on-hold W2R1 ring-plate WIP.
