# Checkpoint queue

Pending: **CP-002** (below), shipped with PT-001 at the M14 gate (2026-10-12). Add items as they come up (template
`docs/process/templates/CHECKPOINT.md`); BLOCKING questions go to chat at once, not here.

# CP-002 — M14 completion gate (PT-001)            2026-10-12 · main @ 4780b5c0

Answer as a numbered list (`1A 2C 3: free text`). Unanswered items keep their default.
Report: `docs/handoff/gates/PT-001.md`. Playtest: `docs/playtest/PT-001_m14-close-out-group-2.md`.

## Questions (GATE class)
### 1. What starts after M14
Context: M14 is complete; work is paused per "pause after M14". MILESTONES "After ART-12" lists R7, G1–G16, the
horizontal list, then H25+ and the Queued passes.
- **A (recommended)**: start the After-ART-12 list with the R7 re-evaluation (Animation pass resumes): ~2 waves, 1 gate.
- B: G1–G16 re-evaluation with you first (a ruling session), R7 after.
- C: wait: nothing starts until you say.
Default if unanswered: C (nothing starts without you). Blocks: all post-M14 work.

### 2. M0–M4 acceptance boxes never ticked
Context: 37 boxes in M0 (4), M1 (11), M2 (6), M3 (6), M4 (6) were never ticked, though later milestones built on them.
- **A (recommended)**: one bookkeeping slice: an agent checks each box against tests / DECISIONS, ticks it with evidence or lists it as open.
- B: leave them; MILESTONES is read from M14 on.
Default if unanswered: B. Blocks: nothing.

## Defaults taken (FYI class; veto by number, otherwise they stand)
- D6. `tools/precommit.sh` re-imports when the staged diff adds or renames a `class_name` (a stale class cache failed one merge run) — gate report PT-001 §2.
- D7. Brief footer adds "stop your own background runs before the RESULT block; one precommit at a time" — gate report PT-001 §2.
- D8. `run_tests.py` uses a fresh shard directory per invocation (overlapping runs collided) — gate report PT-001 §2.

## Already ruled, not re-asked (for reference)
- This PC is the target PC; tier 1 here is the Deck tier → DECISIONS "M14 gate (PT-001)" (2026-10-12).
- Group 2 look → art-pass session APPROVED (R1–R3 + polish), DECISIONS "M14 G2R*" / "G2 polish" (2026-10-12).

## Answered
- **CP-001** (2026-10-10 → answered 2026-10-11): 1A rule 6 scoped to rule-bearing code; 2A full suite once per
  gate, **never ×3**; 3A Batch API lane in use (key still to be set by the designer); 4A playtest gates per
  group. Logged: DECISIONS "2026-10-11 — Designer rulings CP-001"; CLAUDE.md rule 6 and "Commands" updated.
  Defaults D1–D5 stood unvetoed.

## Items queued for CP-002
- none open. Settled by the art director (2026-10-11, close-out group review), reported to the designer as
  "settled unless you object": Mainframe pegboard at 0.86 at text 2.0 (art, not text: the text floor does not apply);
  corp letterheads use a short `letterhead_name` per corp instead of an ellipsis (M14 FOLLOW-UP slice).
