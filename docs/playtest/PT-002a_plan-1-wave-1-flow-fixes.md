# PT-002a — Plan 1 wave 1 flow fixes

since gate/PT-001 · main @ 627f32a6 (code; checked) · 2026-10-13 · build: run from the editor (F5) or `godot --path .`

## 1. Scope and changes (what is new for you)
- **Tutorial:** the tutorial's practice fight now shows CONTINUE when you win (B1). Step 5 explains undo honestly:
  it rewinds your nudges and card plays this turn, until a Respin or a random-slice card (B6; the rule is unchanged).
- **Loot:** the Firmware slot spinner starts on a slot the chip fits (B2). If you try to take a chip into a slot it
  doesn't fit, one note says why and which slot fits, using the chip's name; CONTINUE is never silently blocked.
- **Map Key:** hover opens it; a click pins it open; a second click or Esc closes it (B7).
- **Raid:** after the raid plays out, the title shows the verdict (e.g. HOME -10), not RAID IN PROGRESS; the feed shows
  "Step N:" once per step (B8).
- **New Campaign at text 2.0:** START stays on screen (pinned at the bottom right) (B9).
- **Stickers:** every CONTINUE / BACK TO HQ shows its whole word, with the focus fold beside it, not over it.
- **Combat:** the enemy's precision-tag tooltip says it shows where the needle lands *after this play*.

Known limits (not FAILs): nothing else in combat changed yet (readability is wave 2). B3 (aim stuck) and B5 (Quit) are
closed after your check and are re-checked in the animation pass.
Settings touched: text size (steps say when; set back after).
Seed for the campaign steps: any NEW RUN.

## 2. Playtest steps
| # | Where (reach it) | Do | Look for | PASS when | Time |
|---|---|---|---|---|---|
| 1 | Title → SIMULATE (tutorial) | Play to step 5 (undo) | the step's text | It says undo rewinds nudges and plays this turn until a Respin or random-slice card; nudge then undo completes the step | 2 |
| 2 | Same tutorial | Win the practice fight | the win screen | A whole CONTINUE appears and takes you out of the tutorial | 2 |
| 3 | NEW RUN → JACK IN → win a fight with a Firmware drop | Look at the slot spinner | its start slot | It starts on a slot the chip fits | 2 |
| 4 | Same loot | Turn the spinner to a slot that doesn't fit, press CONTINUE / take | the message | One readable note names the chip and the slot that fits; no tiny red pencil text; nothing overlaps SKIP or CONTINUE | 1 |
| 5 | Same loot | Pick the fitting slot, take it | flow | The take works and the page moves on | 1 |
| 6 | Any loot or fight win | Look at CONTINUE (mouse hover and pad focus) | the sticker | The word reads CONTINUE whole; the fold sits beside it | 1 |
| 7 | HQ → hover the MAP KEY | Hover, then click, move the mouse away, click again; then click and press Esc | the key | Hover opens it, click pins it, it stays open off-hover, second click / Esc closes it; never an empty box | 2 |
| 8 | HQ → let a raid come → START DEFENSE → watch to the end | Read the title and the feed | title, feed | After "Raid over" the title shows the verdict, not RAID IN PROGRESS; each "Step N:" appears once | 4 |
| 9 | Raid result | Look at CONTINUE at text 1.0 | the sticker | CONTINUE reads whole | 1 |
| 10 | Options → text 2.0 → Title → NEW RUN | Find START, scroll the setup page | START | START stays on screen (bottom right) the whole time; exactly one START | 2 |
| 11 | Text 2.0: steps 2, 4 and 9 again | — | stickers and note | Same results at 2.0 | 4 |
| 12 | In a fight, hover the enemy's precision tag | Read the tooltip | the tooltip | It says the tag shows where the needle lands after this play | 1 |
| 13 | Options | Text size back to 1.0 | — | — | 0 |

Total: ~23 min

## 3. Expected vs actual (how to judge)
PASS = the "PASS when" sentence holds at first sight.
FAIL = it does not, or anything crashes, hangs, shows a `KEY_` / rules-English string, loses input,
or looks wrong for more than a second.
PARTIAL = passes with a nit you would still ship (say what).
SKIP = could not run the step (say why).

## 4. Feedback (paste back as is)
```
PLAYTEST: PT-002a
STATUS: PASS | FAIL | PARTIAL
STEPS: <only the steps that are not PASS, e.g. "3 FAIL, 7 PARTIAL, 12 SKIP">
LOGS: <optional: path to the Godot log, or the ERROR lines>
NOTES: <optional: "<step>: <what you saw>" per line>
```
