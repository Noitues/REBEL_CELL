# Change plan 1 — wave 3b: PT-002 screen-batch bugs (B1–B3, B5–B8)

Orchestrator decision, overnight 2026-10-13 (DECISIONS "Overnight run"): PT-002's confirmed P1s are fixed now. Evidence:
`docs/playtest/claude/PB-PT-002/_FINDINGS.md` rows B1–B8, with the tester reports and step PNGs it cites
(`.playtest_sessions/PB-PT-002/<tester>/`). B4 rides W3-HQ. B10 (single-tester ignored inputs) is unconfirmed input:
not in scope.

Rules: the "Every slice" list of `docs/handoff/plan1/W3.md`. **Reproduce first**, in a headless test that drives the
real scene / state (seeded), and keep that test as the regression test. A bug that does not reproduce from the
described steps: write down what you tried in DECISIONS and leave it (no speculative fixes).

## W3B-AIM (combat + rules)
- **B1 (P1):** a card or nudge aim (Fine Tune, Jolt, Brute Spin, free nudge) sticks and cannot be cancelled; RAM debt
  stays; Quit → Continue restores the stuck aim. Every cancel path (Esc, right-click, Z, UNDO) must clear the aim and
  its RAM debt, and a saved game must not restore a half-made aim. Recurs PB-010 B3: read what wave 1 changed first.
- **B2 (P1):** UNDO blocked after Jolt / respin / a random pick with no or a vague reason; UNDO flickers, Z ignored.
  The undo rule itself (rewind must not cross a checkpoint, rule 6) stays; the fix is a stable state and a reason that
  names the event ("Jolt rolled a random spin"). Recurs PB-010 B6.
- **B6 (P2):** Q/E never moved the needle in the tutorial at turn 7 (state: no free nudge / nudge card?). If the state
  is the cause, Q/E say why when pressed.
- **B7 (P2):** respin spent RAM but no respin appeared.
- **B8 (P2):** after an escalation on an Elite's turn 2 the fight ignored keys, clicks and Space until pause / resume
  (an input lock not released).

## W3B-FLOW (combat + screens + rules)
- **B3 (P1):** the tutorial overlay persists into real netrun fights (box on turns 4–10; nudge box every turn); after a
  reload the title started a tutorial fight. Tutorial state must end with the tutorial and never be restored into a
  campaign save.
- **B5 (P2):** both sides at 0 on turn 11 (Dosage Dispenser "0/38 DELETED") counted as a defeat. Check the GDD's
  simultaneous-zero rule; if the GDD is silent, keep the current resolver outcome but make the screen agree with it,
  and add the question under "Open questions for the designer".
- **B9 (P2):** a raid ran with no Start Defense step (openloop 19.0m): check whether an auto-start rule exists (GDD 4);
  if not, it is a bug.

Gate: PT-003.
