# Critic review: sweep-raid lab L3

**Verdict: 32/50. That puts it between Teamfight Tactics (31) and Kingdom Rush (33). It is not ready for the real build. There is one P1 tell, and the decision layer is dominated: the shop is dead and go dark is used every raid.**

Material: `shots_scrambled/` (leg 5, 23 frames), `shots/` (leg 0, planned line, 45 frames), `shots_breach/` (leg 0, naive line, 38 frames), `LAB_README.md`. Godot was not run. I made contact sheets in `sheets/`. The evidence sheet is `refs/side_by_side_lab.png`, built from the lab's own captures. I downloaded no external references, so this review cites no URLs.

## Scores

| Axis | Score | One-line reason |
| --- | --- | --- |
| W: what / why / when | 7 | The contact screen states the strength by Heat band, the beam order (1, +, 2, 3) and the Heat-to-beam chain. *Why* the hunter turns where it does is never stated: it is one word ("TURNS") on a red ring. |
| P: predictability before committing | 8 | The forecast covers every sealed candidate, with the result if you hold and the best result with a spoof, and it is deterministic. Two things undercut it. "Worst case: lose N" counts HOME integrity only (R3 said "lose 0" and then 3 assets went DOWN). And the forecast gives counts, not node names. |
| N: no words | 5 | Numbers, flames, coins, bolts and the intensity cards survive the scramble. The three levers (diamond, dashed ring, black disc) do not, and neither do the hunter rule, the score formula or the stamp tiers beyond "teal = good". About 55% understood. |
| D: decision depth across the leg | 5 | On paper: 3 levers, the spoof, repairs, a shop and intensity. In practice the shop is never used (all 6 golden legs `buy: None`), go dark is used every raid, LOW/NORMAL is almost always right, and the playout is hands-off apart from one spoof click. |
| C: consequences | 7 | The network, HOME integrity and Heat all persist across the leg. The ledger reconciles and the record is honest. Two weaknesses: "CELL HOLDS" covers everything from one decoy touch to 3 DOWN + 1 TAKEN, and the score's "assets kept" term is never shown until the record. |
| **Total** | **32/50** | |
| S: suspense in the playout | 5 | The reveal and the spoof click are the only beats. The reveal is always the triangle (see P1), and a breach at beam 1 is already settled at the forecast. |
| V: visuals | 4 | Clean placeholder vectors with a consistent icon grammar. The grid fills with tiny shape+bolt chips (breach R1 forecast). The right panel is dense ~11 px text. No animation and no sound. |
| Fit | 7 | Corporate beams sweeping a hacker network, decoys, going dark, and the home server as the loss condition all fit the premise well. |

**Placement:** Into the Breach 45 > Slay the Spire 42 > Invisible Inc. 39 > FTL 35 > Kingdom Rush 33 > **lab L3 32** > TFT 31.

- It beats TFT on prediction: its forecast is closer to Into the Breach than to anything else on the list.
- It loses to every title above it on no-words reading, suspense and visuals.
- It loses to Into the Breach and Invisible Inc. on depth: their choices are spatial, made every turn and not dominated. Here the real choice is roughly "where do my two decoys go".

## What the scrambled captures said, and what they failed to say

**Understood without words:**
- The Heat bar with ticks at 50 and 75.
- The raid count (1/3 pips), the HOME pips (three squares) and the bank.
- The beams as numbered lines in an order.
- The sealed beam as a family of three dashed alternatives, each marked with a `?`.
- The forecast rows as "shape, then lose xN, then with the teal chevron you lose fewer".
- The between screen: three cards (flame +6/+12/+18, coin x0.5/x1/x1.5), and bolted nodes with a coin cost meaning "pay to fix".
- A teal stamp reads as good and a white one as less good. Heat 49 -> 39 after the teal raid reads as "clean raid cools you".

**Failed:**
- **What each lever does.** The lite set has no plan frames, and the kit cards say it only in text. Nothing visual separates the diamond's "stops a beam" from the dashed ring's "hides" or the black disc's "hides, no income".
- **The hunter.** Where it starts, why it turns, which column it takes.
- **Why the beam "+" appears in raid 2.** The 50-line tick on the Heat bar is the only clue.
- **How bad a white stamp is.** "1 x bolt" and "2 x bolt" look the same weight. There is no visual scale from EVADED through HOLDS to DAMAGED apart from color.
- **The record's score line.** It is pure text.
- **Whether a choice happened.** `06_r1_between_open` and `07_r1_between_picked` are pixel-identical in content: NORMAL is preselected and nothing marks that the player committed.
- **What the chevron chips scattered under nodes on the forecast grid mean.** They read as noise.

## Ledger and consistency errors

1. **P1: the revealed sealed line is always the triangle.** Candidate 0 is always the real pick and always drawn as a triangle. That holds in all 7 raids captured: `shots/05`, `shots/22`, `shots/38`, `shots_breach` R1, and `shots_scrambled/03`, `/11`, `/19`. A player learns this in two raids, after which the three-candidate forecast and the reveal stop carrying information. P is inflated by this and S collapses. The shape-to-candidate mapping must be shuffled (seeded) per raid.
2. **"Worst case: lose N" is HOME-only.** `shots/34_r3_forecast` says "worst case: lose 0, at best with a spoof: lose 0". `shots/43_r3_aftermath` then shows 3 DOWN. The label must name HOME, or report the whole network.
3. **"INCOME (last)" is not last.** It is the pending income for the selected intensity: +5 at NORMAL, +3 at LOW (`12` vs `14_r1_between_*`).
4. **Two different "+N" values sit beside the currency.** The header shows the net bank change ("11 +1"); the panel shows income ("+3"). Same glyph, different meaning (`shots/14`).
5. **The sign convention for Heat carried flips.**
   - The aftermath and between screens show "Heat carried: -12".
   - The record's raid cards show "-6".
   - The score line shows "- Heat carried 17".
   - The aftermath at Heat 44 shows "0". At 50, the same field shows "-6".

   Choose one sign.
6. **"Leg value" cannot be reconstructed on screen.** "= bank + assets kept - HOME lost x 8 - Heat carried", but "assets kept" (DOWN counted as v minus its repair) appears only on the record. I verified R1: 10 + 34 = 44. The player cannot.
7. **The README and the screen disagree on a breach.** The README says BREACHED = -100. The screen says "the leg has no score".
8. **The "careful" golden line is not careful.**
   - In R3 it holds its last spoof when the decision offers node 4 -> x2 instead of x3 (`shots/38`). A leftover spoof has zero terminal value, so this leaves +2 on the table.
   - With 9 in the bank and 0 decoys before R3, it buys nothing, then loses 3 assets.

   Either the planner is not optimal, which makes the reference line misleading, or the score fails to reward these plays. Both are problems.
9. **The stamp mixes this raid's changes with escalations.** "CELL HOLDS 1 DOWN 1 TAKEN" (`shots/27`): the TAKEN asset was already DOWN from R1. That is an escalation, not a fresh loss, and the stamp does not say so.
10. **The raid-3 breach was settled at the forecast** (`shots_breach/34`: BREACH on all three lines, no spoof in the kit). That is fair, because 2 decoys sat unused. But the playout then cuts at beam 1, so the climax of the leg is a one-beam non-event.
11. **Known and unfixed:** the hunter's `3` badge overlaps node glyphs at three known beams. Heat is uncapped while the meter is drawn to 100.

## The 5 changes that would most raise the score

1. **Shuffle the candidate shapes per raid (seeded) and make the hunter's rule visible.** For the hunter, draw its trigger and its turn column on the plan grid with a glyph, not the word "TURNS". This fixes P1 and lifts S, N and W. *Not a rule change.*
2. **Give the playout a mid-sweep decision beyond the spoof.** Example: one decoy held in reserve that can be dropped after the reveal, or a go-dark that can be called after beam 1. Right now 90% of the raid is watched, not played. **(Designer decision.)**
3. **Fix the dominated economy.**
   - Make a shop buy competitive with repairs: price the decoy at 2-3, or let unused kit count toward the score.
   - Give go dark a real cost: a kit charge, or +Heat.
   - Make HOT tempting: let EVADED at HOT cool by more, or carry Heat at 0.5 per point.

   Re-run the planner so that it does buy, does choose HOT sometimes, and does not use go dark every raid. **(Designer decision.)**
4. **Split the tiers and the forecast summary by severity.** The forecast should say "worst: HOME -1, 3 DOWN", not "lose 1". HOLDS should become graded, for example HOLDS / BLED, with the stamp's weight scaling with losses. Show "assets kept" as a live number next to the bank. *Presentation, plus a designer decision on tier names.*
5. **Make the levers readable without words.** Draw each lever's effect on the grid at placement, using the visual grammar of Into the Breach's push arrows:
   - a decoy draws a beam stopping at it;
   - a ghost draws beams passing through a ghosted node;
   - a dark node draws a "no income" coin strike.

   Also add a committed-state mark on the between screen. *Not a rule change.*

## Ready for the real build?

**No.** The rules engine is solid: parity PASS, and the ledger reconciles wherever I checked it (income = sum of v // 3 x multiplier, repair = v // 2, score 19 = 12 + 24 - 17). But it should not be ported as is:
- The reveal is a tell (P1).
- Two of the five decision surfaces are dominated, per the lab's own README.
- The playout asks for one click per raid.

Ship these to L4 first:
- the shape shuffle;
- the hunter glyph;
- the forecast severity wording;
- the economy retune (designer decision).

Then re-run this exact capture set. Porting the engine as is would lock in a forecast UI that is better than the game it forecasts.
