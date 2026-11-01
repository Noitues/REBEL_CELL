# Combat redesign (ART CALL 51): art director report

Saved by the orchestrator from the art director's returned text (the harness refused the subagent's own file write). Comparison sheet: `report_finalists.jpg`. Plan: `VISUAL_PLAN.md`. Review and ranking of the 5 styles: `REVIEW.md`, `review/board.jpg`.

## Recommendation: F1 Black-Book Burner, with five fixes
F2 Zaun Press is the fallback: it is more legible and closer to shippable.

**Why F1**
1. It answers note 1 literally. The designer asked for street or sketchbook graffiti. F1 is Miles' black book on the tower (marker on dot grid, ballpoint construction lines, block drop, bubble hub) plus wall pieces in the hand (wheat-paste cards, tag titles, kraft tape, a spray-slab SEND IT with drips). F2 is strong Spider-Verse print with Arcane doodles, but it is not graffiti.
2. It has the strongest player-owned read. Nothing else on screen is hand-made, and the read holds in grey (`finalist_1/grey_proof.jpg`).
3. It has the most visible craft, and the designer said art style is the goal.
4. Its set is fuller: it covers f2t and f2b; F2 does not.

**F1 fixes before approval**
1. Lower the tower's value by about 10 % (squint loud share now 0.125; target 0.08 or less; E10 was 0.041).
2. Card rules text at 20 px or more, and fit "SPIN 3" inside the card.
3. Give the hub more room: HP ring to r54-66, or a smaller bubble.
4. Clear the sector digits: the needle covers digit 0, ticks half-cover 5, and the HOLD THEN tag covers 3.
5. Render p3 on f2t and f2b, or mark them not applicable.

Also take F2's dark ink-seat icon discs.

## What was done per designer note
1. Five styles explored (`explore/*`, `review/board.jpg`); two finalists rendered on a fully new board.
2. Zero dashed lines on every finalist plate; one meaning per line type. Time grammar:
   - HOT (solid, glow, END notch) = this END TURN;
   - COLD (#D9877C, one pip) = next turn;
   - FAR (dotted marks, two pips) = later; future rings recede to 80 % and 62 % value.
3. The white slash is retired. Cross-hatch means lost at this END TURN; the hatch colour is the cause (red = enemy, blue = soak, pink = us). The HP ring moved to the hub.
4. The arrowed outline is kept and means movement only (hover route, the THIS TURN cell, the queue feed, Twist/Pull/Shove).
5. Lane and slice-type outline colours are gone: one enamel outline for all enemy cells, gold only for the boss, and a 12-colour legend.
6. The W4-W6 arcs are replaced by three tickets top-left; the freed rim went to the tower (r162 to r196).
7. 28 effects in 8 families, each with its own material (`effects_final/fx_00_overview.png`). Block vs break reads in one frame (`fx_block_vs_break.png`; each finalist re-skinned it). Each screen-element family has its own material.
8. Parked items untouched.
9. Dimming kept (value x0.40, chroma x0.45). 11 hover plates plus a key (`hover_final/`), and Brace, Twist and Trigger in each finalist's skin.
10. A real redesign: compare the before/after sheets and `report_finalists.jpg`.

## Game-information check
Eye check against state_e10.json f1/f2, plus each stream's asserts (F1 173 PASS, F2 72 PASS). These match on both finalists:
- p1: 12 -> 6, YOU 9 kept and 6 hatched, RAM 4, Trace 3/6;
- p2: 3 -> 0, options 6 -> 1, 9 -> 1, 3 -> 0;
- p3: chain of 6 steps;
- slice pips per hp_after;
- all 7 units plus the Adjuster, ward marks, Worm 2 dying;
- card costs, the Trace tab and rules text;
- wave tickets match the lineup.

No number, word or rule is lost. Draw collisions found:
- Both: the needle covers sector digit 0.
- F1: digit 5 is half-covered by ticks; digit 3 is under the HOLD THEN tag.
- F2: tape covers "// BREAKER" on the nameplate; the p2 REFUND tag reads "EFUND".
- F1 p2: 8 characters short of E10, attributed to E10 drawing the Trigger text twice (checked by word list only).
- F2 hover Twist: built on shifted f1 ghosts; its landings are not recomputed.

## Remaining weaknesses
- Both finalists are much louder than E10.
- Effects are stills only, drawn on the round-1 stand-in board, and not skinned per finalist beyond block, break, brace and soak.
- The 11 hover plates use the E10 tower and cards and must be re-rendered on the winner.
- CVD and dE checks were not run (SOAK vs NET_CYAN and TRACE_VIOLET; FOCUS lime vs PLAN yellow).
- No draw asserts or squint on the hover plates; F1's asserts are E10-layout based, so the collisions above slipped through.
- F2: press cyan vs NET_CYAN dE is only 17; its landing arcs are off spec (r442-500); no f2t/f2b plates.

## Open items
- Designer: pick F1 (recommended) or F2.
- Designer: confirm the arrowed-outline reading (movement only).
- Designer: how loud should player-owned be? (F1 loud 0.125, F2 0.082, E10 0.041; proposed target 0.08 or less.)
- Designer (F1): do the black-book tower and the wall-paste cards / SEND IT read as one hand or two?
- Designer: accept the HOT/COLD/FAR time grammar and the hatch-colour rule.
- After the pick: re-render the hover plates and rebuild the core effects in the winner's skin (with animation timings and a measured flash-rate check), run the colour checks, and add a layout-aware draw assert for digit and tag collisions.
