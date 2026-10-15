# Plan 2 B-TEACH / B-CODEX capture: findings

Sheet: `B_TEACH.jpg` (1600 px wide, before = main 04bf2973 | after = B-TEACH + B-CODEX merged on main). Tool:
`tools/design_lab/plan2_b_teach_capture.gd` (one windowed run per tree) and `plan2_b_teach_sheet.py` (joins them). Text 1.0,
a Triage Unit fight, seed 7. Each panel jumps the overlay to the beat's step by title; the screen state is real (nudge, a
played Jolt, `_preview_card(0)` for the hover).

Before has no steps for THE TAGS, AIM, FREE NUDGE, STAGED or RAM FORECAST (its steps: THE WHEEL, NUDGE, RESISTANCE, CARDS,
UNDO, SEND IT, HEAT & BANKING), so those rows show "no such step". Row 7 (UNDO) and row 8 (Codex) compare directly. The
Codex panel is the Lexicon tab: before has no Nudge / Free nudge / Tick entries.

## Checks that held
- AIM: one nudge off the start aim, the tag reads off PERFECT; the nudge back reads PERFECT and the tutorial moves to FREE NUDGE
  by itself (panel 3, logged: `perfect=true, step=FREE NUDGE`).
- RAM FORECAST with a card hovered: RAM shows "(-1 THIS PLAY)" as the step says.
- Codex shows NUDGE and FREE NUDGE (and TICK) in the Lexicon.

## Findings (nothing fixed; capture only)
1. **RAM FORECAST (and later beats): the THIS TURN list is covered by the tutorial box.** The list sits at the top of the notes
   column and the box starts below it, but the list grows with the plays (rows: nudges, Jolt, YOU, TRIAGE UNIT, RAM). With 3-4
   plays the bottom rows (TRIAGE UNIT / "RAM 6->4  NEXT 8") run under the box (panel 6; panel 7 too).
2. **RAM FORECAST: a yellow "...S HERE" callout peeks out from behind the tutorial box** (right edge, level with the enemy wheel's
   hovered slice): the preview ghost label is clipped by the box.
3. **THE TAGS: NEXT reads greyed** in the capture while later steps' NEXT is lit. It is most likely the NEXT pulse (`tutorial_next_pulse`,
   steps with no wait) at its low alpha when the frame was taken, but a still image of that step reads as disabled (PT-002 C9 was this).
   Worth a check in a live run that the pulse never drops below readable.
4. **STAGED: the step says the card "waits in THIS TURN", but the THIS TURN list is not on screen in that panel** (it appears one
   beat later, panel 6). Likely the list's fade-in after the play (30 frames in the capture); the step may read before the list does.
5. **FREE NUDGE vs the title bar:** the step says the title bar counts free nudges; at panel 4 the bar reads "FREE NUDGE 0" and the
   text says "Nudge once more to see it" (the capture had spent the free nudge). Consistent, but the demo state never shows the
   "(-N) next to RAM" until the player nudges; the step does not say it will not show until then.
6. The "(-N) next to RAM" when not hovering reads "NEXT TURN n" only; "AT SEND IT" was not captured (needs a CORRUPTED slice).
7. Capture artefact, not a bug: the dev fight picker ("Fight: collections_agent / Seed") shows at the top left because the
   tutorial was started by `start_tutorial()` rather than through `pending_tutorial`, which hides it.
8. The hovered raised card hides the player's HP number partly (the A-HAND issue, seen in panel 6; "HP" is cut at the card edge).
