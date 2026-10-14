# PT-002 — Plan 1 waves 1b and 2: combat legibility

since gate/PT-002a · main @ (set at the gate) · 2026-10-13 · build: run from the editor (F5) or `godot --path .`
**Scope: text size 1.0, mouse and keyboard only** (designer ruling 2026-10-13). Leave Options at 1.0, reduce effects OFF.

## 1. Scope and changes (what is new for you)
- **Reading a turn (wave 2):**
  - **Precision tag:** every needle (yours and the enemy's) wears PERFECT / GOOD / WEAK / NULL. It updates as you
    hover and queue cards and nudges; "PERFECT → NULL" means your play moves it.
  - **HP chips:** before → after ("60→49"). A kill reads "→ 0", and a red LETHAL chip warns before a lethal turn.
  - **THIS TURN panel:** queued plays, net HP per wheel, total RAM, RAM next turn. SPIN chips show ring moves.
  - **Chips labelled in place:** HP, BLOCKED, GUARD, RAM, HEAT. A combat legend opens with **L** or the "?" chip.
  - **Card faces:** full card text with direction ("clockwise"), and conditions on the face ("Needs an inner ring.",
    "Fits DEFRAG slices only.").
- **Inner ring (round 45):** a tinted ghost wedge with the modifier's mark lies over the outer slice the active
  segment applies to. The active segment is lit; words appear only when you hover a wedge or aim at that wheel. With
  Twin Pointer, each needle gets its own.
- **Teaching:** the tutorial's nudge step teaches Free Nudge and Q / E; the Q / E keys show OUTER / INNER.
- **Flow fixes (wave 1b):**
  - CONTINUE folds on a tab beside the word; SKIP is a sticker (no ">>").
  - A won fight waits for your LOOT / CONTINUE press.
  - The Quit dialog's buttons work; Esc in Options no longer crashes; New Campaign shows LOADING.
  - Event choices light on hover and arrow keys.
  - One combat backdrop per fight.
  - The netrun map keeps your zoom and pan after the map key; hovering a key row rings those nodes.
  - CREW → loadout → NEXT → CLOSE stays on the right operative.
  - The raid feed shows one "— STEP N —" divider per step.
- **US English everywhere** (center, color, defense).

Known limits (not FAILs): 1.6 / 2.0, high contrast and gamepad are deferred and not tested here. Motion polish
(cross-fades, beam overlap) is the animation pass. The Genome Core is still the old design (a content design pass is
planned).
Settings touched: none (keep text 1.0, reduce effects off).
Seed for the campaign steps: any NEW RUN.

## 2. Playtest steps
| # | Where (reach it) | Do | Look for | PASS when | Time |
|---|---|---|---|---|---|
| 1 | Options | Check reduce effects is OFF and text is 1.0 | — | (setup) | 1 |
| 2 | Title → SIMULATE (tutorial) | Play the nudge step | text and keys | It explains Free Nudge and Q / E; the Q / E keys show OUTER / INNER | 2 |
| 3 | Tutorial fight | Hover cards, queue one, hover another | tags and chips | Each needle shows PERFECT / GOOD / WEAK / NULL; chips read "60→49"; the tag changes as you hover | 3 |
| 4 | Same fight | Queue two plays and a nudge | THIS TURN panel | It lists the plays, net HP per wheel, total RAM and RAM next turn; UNDO removes the last play | 2 |
| 5 | Same fight | Press **L** (and click "?") | legend | Every chip, slice code (OVFL / SHIM / DFRG, the 1/0 Null) and status is explained | 1 |
| 6 | Same fight | SEND IT several times | the playout | The SEND IT animation plays (not instant); the result matches the forecast chips | 2 |
| 7 | Win the tutorial fight | — | the win | CONTINUE (whole word, fold on a tab) takes you on; nothing auto-advances | 1 |
| 8 | NEW RUN → JACK IN → a fight | Hover the enemy's nudge arrows | preview | The enemy's SPIN chip and tag show what the nudge does | 1 |
| 9 | Any fight | Bring an enemy to low HP; hover a killing card | kill readout | It reads "→ 0", not "→ N LEFT" | 1 |
| 10 | A fight where your HP is low | Hover a play that would kill you | LETHAL | A LETHAL chip warns before SEND IT | 2 |
| 11 | A fight with an inner ring (a Rigger, or a ring card) | Look at the ring at rest, then hover the tinted wedge | the ring | The wedge sits on the right outer slice, its mark is clear, the active segment is lit; the word plate shows only on hover or aim and covers no tag or HP | 3 |
| 12 | Any fight | Read the cards in hand (hover them) | card text | Hovered cards show their full text with direction; conditions show on the face | 2 |
| 13 | Win a fight → loot | Look at SKIP / CONTINUE; hover a slot on a Firmware drop | stickers, tooltip | SKIP has no ">>"; the slot tooltip explains the slice and its Firmware | 2 |
| 14 | Loot with a Firmware that doesn't fit | Try the wrong slot | note | One note names the chip and the slot that fits; it stays until you pick | 1 |
| 15 | An event | Move the mouse and arrows across choices; hover a Daemon reward icon | highlight, tooltip | The lit choice follows mouse and arrows; the Daemon reward shows its art and tooltip | 2 |
| 16 | Netrun map | Zoom out and pan, hover the map key, then leave | framing | The zoom and pan stay; hovering a key row rings those nodes | 2 |
| 17 | HQ → CREW → a runner → VIEW LOADOUT → NEXT OPERATIVE → CLOSE | — | top bar | The polaroid and the top bar show the same operative | 1 |
| 18 | HQ → a raid → START DEFENSE | Watch | feed, INCOMING | It plays (not instant); one "— STEP N —" per step; INCOMING reads whole, clear of the letter | 3 |
| 19 | Title → QUIT; Options → Esc | Click the Quit buttons; press Esc in Options | — | The buttons respond; Esc closes Options without an error | 1 |
| 20 | Title → NEW RUN | — | loading | LOADING shows at once | 1 |

Total: ~34 min

## 3. Expected vs actual (how to judge)
PASS = the "PASS when" sentence holds at first sight.
FAIL = it does not, or anything crashes, hangs, shows a `KEY_` / rules-English string, loses input,
or looks wrong for more than a second.
PARTIAL = passes with a nit you would still ship (say what).
SKIP = could not run the step (say why).

## 4. Feedback (paste back as is)
```
PLAYTEST: PT-002
STATUS: PASS | FAIL | PARTIAL
STEPS: <only the steps that are not PASS, e.g. "3 FAIL, 7 PARTIAL, 12 SKIP">
LOGS: <optional: path to the Godot log, or the ERROR lines>
NOTES: <optional: "<step>: <what you saw>" per line>
```
