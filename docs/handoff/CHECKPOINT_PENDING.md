# Checkpoint queue

Pending: **CP-003** (2026-10-12): `docs/handoff/gates/CP-003.md`, from the playtest analysis `docs/playtest/claude/ANALYSIS_2026-10-12.md`.
The full CP-002 as asked:
`docs/handoff/gates/CP-002_as_asked.md`. Add items as they come up (template `docs/process/templates/CHECKPOINT.md`);
BLOCKING questions go to chat at once, not here.

## Answered
- **CP-002** (2026-10-12 → answered 2026-10-12):
  1. Wait for playtest feedback: gather it all, act on none until the designer says; analyze → decide what changes and what is
     ignored → plan only the approved changes.
  2. R7 is retired as a fix list; it only informs a new set of updates (applying it as written would cause regressions).
  3. M0–M4 ticks are decided from the playtest evaluation.
  4. No timed netrun step (the M2 "12–18 min" box is not checked by a PT step).
  5. Overkill shows only the result clamped to the minimum: "→ 0" (or "→ 0 LEFT"), never the over-damage.
  6. Pacing comes later in the plan, after gameplay polish.
  7. B: hostile tick marks / reticles stay off by default, behind the colour-blind setting only; long term removed entirely.
  Defaults D6–D14 stand (none vetoed); D11 and D14 now apply to whatever plan follows the feedback, not to R7.
  Logged: DECISIONS "Designer rulings CP-002".
- **CP-001** (2026-10-10 → answered 2026-10-11): 1A rule 6 scoped to rule-bearing code; 2A full suite once per
  gate, **never ×3**; 3A Batch API lane in use (key still to be set by the designer); 4A playtest gates per
  group. Logged: DECISIONS "2026-10-11 — Designer rulings CP-001"; CLAUDE.md rule 6 and "Commands" updated.
  Defaults D1–D5 stood unvetoed.

## Items queued for CP-002
- none open. Settled by the art director (2026-10-11, close-out group review), reported to the designer as
  "settled unless you object": Mainframe pegboard at 0.86 at text 2.0 (art, not text: the text floor does not apply);
  corp letterheads use a short `letterhead_name` per corp instead of an ellipsis (M14 FOLLOW-UP slice).
