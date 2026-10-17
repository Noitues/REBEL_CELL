# Plan 2: batch design drafts, round 3

Lane: Message Batches API. Plan and surface only: markdown drafts under `docs/handoff/plan2/drafts/<batch>/`.
No game code, content `.tres`, GDD or DECISIONS changes. Spend cap: $15 total (estimate before each submit).

Reuse `tools/batch/build_design_drafts2.py`, `submit_drafts2.py`, `ingest_drafts.py` (--ledger); add
`build_design_drafts3.py` on the same pattern. Keep the system head and shared block byte-identical to rounds 1 and 2
(cache hits); round-3 notes go after the cache point.

Sources: `docs/GDD.md`, `docs/handoff/plan2/CONTENT_DESIGN_V2.md` (R1-R13, N1-N20),
`docs/handoff/gates/REPLAN_2026-10-16.md` (NA-0..NA-4, W0-W3, D1-D10), `docs/DECISIONS.md` (rulings 2026-10-14,
2026-10-16), `docs/balance/BASELINE_e2e13918.md`, `docs/handoff/plan2/BALANCE_SIM.md`, `drafts/README.md`.

## Stage A (submit together)

1. **triage/** (Haiku): every BLOCKER in `critic/*.md` (file, draft id, one line). `triage/BLOCKERS.md`: drafts ranked
   by blocker count, then blockers grouped by theme. Shard per batch folder if needed; merge locally by script.
3. **questions/** (Haiku): every open question / "designer to decide" item across all 227 drafts; dedupe and group
   locally; `questions/DESIGNER_QUESTIONS.md`, one numbered list with source links.
5. **test_plans/** (Sonnet): one file per N1-N20, GUT test-case lists per CLAUDE.md rule 6 (preview = result, seeded
   replay, determinism, tie-breaks), target test file names and manifest tier.
6. **raids/** (Sonnet): the single raid design pass (designer Q14), ultimatum as a schematics sink; consistent with
   the round-1 raids draft and its critic.
7. **names/** (Haiku): Central Server name options, 3 per corp for Meridian, Orbital, Solace, Tethys, Aurelian (conflicts
   in `docs/handoff/netrun_art/`); Halcyon is THE PANOPTICON (chosen). One-line rationale each.
8. **balance_sweeps/** (Sonnet): S5 sweep specs in exact `tools/balance/balance.py --set/--variant` syntax (read the
   tool), hypotheses from the baseline (boss 38 turns / 25 % win; campaign 605 min vs 395), incl. step-0 calibration.

## Stage B (after triage is ingested)

2. **v2/** (Sonnet): revise each of the 96 round-1 drafts with its own critic file plus its triage rows;
   `v2/<batch>__<id>.md`, starting with "Changes vs v1". Originals untouched.
4. **briefs/** (Sonnet): agent briefs for W0 slices NA-02, NA-03, NA-04, N1, N2, N3, N4, N19, N11, N13, N14 in the
   repo's brief style (see `docs/handoff/plan1/W3.md`): goal, files, acceptance, tests, agent type and lane, base/tag
   placeholders. Briefs must stay under the 4000-char agent brief limit (long lists in a named file).

## Finish

Extend `drafts/README.md` with a round-3 section and index; commit (batches and cost in the message); run
`QUICK=1 bash tools/precommit.sh --base main`; tag `plan2-batch-drafts-3`. Payloads and batch ids stay in the
scratchpad. Retry truncated requests alone at a higher max_tokens.
