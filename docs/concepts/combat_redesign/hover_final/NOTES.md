# Hover plates, round 2 (one per card effect type, Shifting Waves)

Hover designer, VISUAL_PLAN H plus the R51 review. 1920x1080, bio room (`combat_backdrop/v3_1/room_bio_bare.png`), state unchanged (turn 2, seed 49, f1/f2 from the sim, read only).
Start with `hover_overview.png` (all 11 plates and the key). `h00_key.png` is the grammar key drawn with the plate code. `slips/` holds each plate with its review slip under the frame. `lift_styles.png` shows the per-finalist hook for the lifted card.

## What changed from round 1
- Dim is value x0.40, chroma x0.45 (round 1 rendered at 0.50 by mistake). The hand not in play drops to 70 percent.
- Every hover move and proposal is PLAN pencil: L5 arrowed outlines in PLAN yellow with ink edges. Orange and pink arrows are gone from hover (they appear only in resolve).
- FOCUS is corner brackets only, 12 px legs, 2 px legal, 3.5 px aimed. No full outlines.
- Changed numbers are ringed in pencil on the bill (hero LANDS / THROUGH, the RAM coin spent, the TRACE pip added). The nowords bill rings the tally runs.
- 11 plates, not 14: Spin2 and Nudge are insets on h01, the bump is an inset on h06, Trigger after Twist is an inset on h03. h10 (soak toggle) and h11 (unit hover) are new.
- The review note is off the plate: it sits in `slips/`. Plates carry only the game's own words (card names in the insets).
- Board is now the redesigned grammar board (wave queue top-left, time grammar, hatch HP, no dashes, slate enemy units) instead of the patched E10 board.

## The grammar (all plates)
| Mark | Meaning |
|---|---|
| lit vs dim | lit = what the card touches; dim = everything else |
| lifted card on a pink offset print | the hovered card (P family) |
| lime corners 2 px / 3.5 px | legal target / aimed target |
| PLAN arrow (L5) | this moves along here |
| pencil outline, 74 percent ghost, veiled origin | the thing at its new place |
| pencil ring / square | this number or pip changes under the plan |
| pink hatch / red hatch / indigo hatch | lost at this END TURN: ours / the enemy takes it from you / your soak |
| pink burst | a hit that lands (never on an icon) |

## Rule per card
| Plate | Card (type) | Lit | Dim | Marks |
|---|---|---|---|---|
| h01 | Spin 3, Spin 2, Nudge (turn the tower) | tower, ring NOW, guns, arcs, bill | rings +1/+2, queue | tower drawn at plan angle, pencil rim, one PLAN arc round the hub (3, 2 or 1 sectors), plan tracers; insets Spin 2 and Nudge |
| h02 | Brace (protect a slice) | six slices, landing arcs, bill | rings, queue | corners on every slice, thick on the aimed one, clamp ghost with L10 double edge, pencil bar on the arc that stops |
| h03 | Trigger (resolve a unit now) | legal units, victim, slices 3-4, bill, RAM/TRACE | rest | corners on legal units, PLAN arrows down the resolved sectors, pink hatch + burst on the victim, refund coin, pencil ring on TRACE; inset after Twist |
| h04 | Twist (turn one ring) | rings +1/+2, bezel, arcs, bill | ring NOW, tower | corners on the two ring tags (thick on aimed), PLAN arrow along the ring, twist pill, pencil-edged landings |
| h05 | Strike (damage a unit) | every unit in range, arcs | tower, schedule | corners on units, pink hatch + burst + speed lines on the aimed unit |
| h06 | Shove (move sideways) | rings NOW/+1, Adjuster, arcs | ring +2, schedule | veiled origin, ghost, PLAN arrow, new arc; inset bump: burst, 1 HP hatched each |
| h07 | Pull (move inward) | the one legal unit, its cells, arcs | rest | veiled origin, ghost one ring in, PLAN arrow inward |
| h08 | Hold (stop the rings) | bezel, all rings, arcs | tower interior | PLAN arrow outside the bezel, pencil outline on the live cell, arcs recomputed |
| h09 | Firewall (burn a sector) | the column, the two units, bill | tower, other columns | corners on legal columns, pink wash + pencil flame strokes, bursts and hatch on the units |
| h10 | Soak toggle (no card) | tower, arcs, bill | rings, hand idle | corners on all slices, SOAK band with inward chevrons on the hovered one, pencil ring on THROUGH and on the saved HP |
| h11 | Unit hover (p2b form) | unit, route, landing slices, arcs, bill, tag | rest | PLAN route arrow, thick corners on the cell, pencil rim on landing slices, E10 tag (content parked) |

Nowords: h01-h04 `_nowords.png`.

## Honest caveats
- The finalist p1 plates do not exist yet, so the plates are NOT on a finalist's art: the tower, cards and HUD are the E10 look on the grammar board. The one finalist-dependent hover element, the lifted card's print, has a hook (`STYLE['lift']`: base, F1 wheat-paste, F2 misregistered press), shown in `lift_styles.png`. Re-render the 11 plates per finalist once p1 is approved: `HV_LIFT=F1 python src/hv_run2.py ...`.
- FOCUS lime #D4FF00 and PLAN yellow #FFE200 are close in hue; they are told apart by form (corners vs pencil). Worth a designer check.
- Not run: assert_draw_log, the 320 px squint and the colour-blind sheet for these plates. I opened every plate and the key at full size.
- Edge clipping of the outermost landing arcs at the left screen edge belongs to the grammar board layout, not to hover.
- Shove bump: the 1 HP hatches on the unit HP ticks are small at 1x; the pink burst carries the read.
- Process slips: `python -` with an empty heredoc was run twice by mistake; one exited alone, the other (PID 12480) was stopped. Nothing else touched.

Generator copy: `D:/rc_scratch/combat_redesign/hover2/src` (snapshot of the new files in `src/`). Sim and combat_e10_design untouched.
