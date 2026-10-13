# PT-002a — feedback triage            2026-10-13 · build gate/PT-002a (627f32a6)

The designer's feedback is filed verbatim in `PT-002a_FEEDBACK.md`. CP-002 ruling 1 applies: **nothing below is acted
on until the designer decides.** Each item gets an id, a class, and a proposed disposition (the recommended one first).

## 1. Wave 1 verification
| Step | Result | Finding | Proposed |
|---|---|---|---|
| 6 (CONTINUE whole) | FAIL | **F1** CONTINUE shows no sticker fold at all; **F2** SKIP has ">>" over its S | P1 re-fix in wave 1b: the fold-room fix gave room but the fold itself doesn't draw (or draws off-sticker), and SKIP was not covered |
| 9 (raid title / Step N:) | PARTIAL | "Step N:" unclear; also **F3** START DEFENSE skipped the whole playout straight to the report | Explain: "Step N:" is the feed's step label (keep it or drop it, your call). F3 is P1, see §2 |
| 11 (2.0 repeat) | PARTIAL | **F4** card rewards: a hovered card clips at 2.0; **F5** the loot screen's bottom is cut off (SKIP / CONTINUE / Deck half shown) | P1 for wave 1b (both are layout at 2.0) |
| 12 (tag tooltip) | FAIL | "What is the enemy precision tag?" Nothing on screen names it | Fold into wave 2 A1 (the precision tag becomes a named, visible element) |
| 13 (text back to 1.0) | PARTIAL | **F6 crash** on Esc in Options: `settings_panel.gd:572` calls `get_viewport()` after `closed.emit()` freed the panel | P1, one-line fix (handle the input before emitting) + a test; ship in wave 1b |

## 2. New bugs (P1: broken behaviour)
| Id | Where | Bug | Proposed |
|---|---|---|---|
| F3 | Raid, Tutorial, Combat | Playouts skipped: START DEFENSE goes straight to the report; SEND IT animations don't play; a tutorial win jumps straight to CONTINUE | **Investigate first.** It looks like one cause (motion forced off, or reduce effects / reduce motion stuck on, or a leaked test flag). Wave 1b, top priority |
| F7 | Main menu QUIT | None of the quit dialog's buttons respond; A doesn't quit; CONTINUE has no key | Re-open B5 (you saw it work before; now it doesn't). Wave 1b, with a real-mouse check |
| F8 | Combat win | Hovering the loot button opens the loot sheet before a click | Wave 1b |
| F9 | Combat | Freeze doesn't work on the player's spinner | Rules check first (GDD: should Freeze apply to the player's wheel?), then fix. Wave 1b |
| F10 | Combat (Compliance Officer) | The background switches from the medical building to the city when hovering the enemy wheel | Wave 1b |
| F11 | Combat | Hovering the enemy's nudge buttons shows no preview | Wave 2 (A2 preview completeness) |
| F12 | Rewards | SKIP may skip *all* reward types, not just the card pick | Verify; if true P1 (wave 1b). The "one rewards screen listing each reward" redesign is §4 D-UX1 |
| F13 | Netrun map | Zoom and pan reset (snap back to the current node) after hovering, then leaving, the map key | Wave 1b |
| F14 | Netrun map | Hovering the map key does nothing (expected: it highlights all node types) | Wave 1b (with F13) |
| F15 | HQ crew | CREW → BREAKER 1 → VIEW LOADOUT → NEXT OPERATIVE → CLOSE: polaroid says BREAKER 1, top bar shows BREAKER 2's loadout (0 daemons) | Wave 1b |
| F16 | Event | The selected option's yellow band doesn't follow arrow keys or mouse | Wave 1b |
| F17 | Raid setup | Dropping a defence card on a node shows no change on the node (only in YOUR NETWORK) | Wave 3 (C, city clarity), or 1b if you want it sooner |

## 3. Readability and teaching (they fit the approved sets)
| Id | Feedback | Set |
|---|---|---|
| R1 | Inner ring nearly impossible to read | A (wave 2), new item A6 |
| R2 | Loot: HARDENED's tooltip doesn't say what ENCRYPTED means | A3 (status labels and legend) |
| R3 | Loot: hovering a slice should explain the slice and its installed Firmware | A3 / A4 |
| R4 | Event: nothing says what the Daemon reward is; use the Daemon's icon and tooltip; tooltips on the right-hand icons | A4 (card / chip faces), extended to events |
| R5 | Netrun route: nodes drawn off the route are hard to read; proposal: draw them on-route, and on hover animate the node out to its building | C7 (route map). The animated part is motion: queue for the animation pass |
| R6 | GRID VIEW: shows no active netrun path or target; remove next-node choices there (route view only) | C (city clarity), new item C10 |
| R7 | HQ: MARKET's Schematics number and CREW 2/2 are redundant with the top bar; remove both | C, small |
| R8 | Raid report: pencil crowds the fields (more line space); CELL HOLDS reads as a clickable sticker (make it pencil); remove all other pencil words, circles and checks | Art (art-pass session confirms), wave 3 or 1b |

## 4. New UX direction (needs a ruling; not in the approved sets)
| Id | Proposal | Proposed disposition |
|---|---|---|
| D-UX1 | Rewards: one screen listing every reward gained (like Slay the Spire); click a reward to pick from it | **New design item.** It changes the loot flow and fixes F12 by design; plan it as its own slice after wave 2 |
| D-UX2 | Input glyphs only for the active device (pad or mouse / keyboard), never both; the same button look for both, only the glyph differs ("[ESC]" vs "[B]") | New item: one input-prompt system pass; size it (touches every screen with prompts) |
| D-UX3 | A Menu button at the top left, left of the Heat widget | Small; with D-UX2 |
| D-UX4 | Clicking outside a menu closes it (not dialogs, events or gameplay) | Small; with D-UX2 |
| D-UX5 | New Campaign hangs about 1 s before the screen appears: show a loading overlay | Small; wave 1b |
| D-UX6 | Grease-pencil glitch notches are flat grey squares: use a smear texture with alpha | Art (art-pass session); its own art slice |

## 5. Copy and small items
| Id | Item | Proposed |
|---|---|---|
| C-1 | "Centre" → "Center" | Ruling: switch the game's English to US spelling everywhere (one mechanical pass), or only this word? |
| C-2 | Tutorial page 7/7 text says "next" but the button says FINISH | Wave 1b |
| C-3 | BREACH and "> CONTINUE" on the title don't animate like SIMULATE / NEW CAMPAIGN | Motion: queue for the animation pass (D2), or a quick parity fix in 1b |

## 6. Proposed next steps (for the designer)
1. **Wave 1b, bugs only (before wave 2):**
   - F1, F2, F4, F5 and F6: the wave 1 fails and the crash;
   - F3: playouts skipped (investigate first);
   - F7: Quit;
   - F8, F9 (after the rules check), F10, F12 (verify), F13 + F14, F15, F16;
   - C-2, D-UX5.

   That is about 5 slices, one comparison sheet, then gate PT-002b with a short human list.
2. **Wave 2 (A)** as planned, extended with R1 (A6 inner ring), R2, R3, R4, F11 and step 12 (naming the tag).
3. **Wave 3 (C)** gains R5 (static part), R6, R7, F17, and R8 (with the art-pass session).
4. **Rulings needed:**
   - D-UX1, rewards screen: plan it, and when?
   - D-UX2 to D-UX4, input prompts and menus: one pass, and when?
   - D-UX6, smear notches: art slice when?
   - C-1, spelling: US everywhere?
   - "Step N:" in the raid feed: keep or drop?
