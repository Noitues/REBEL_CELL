<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__rc_template_elite; status ok; tokens in 7125 cache-write 0 cache-read 32585 out 2172; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/rc_template_elite
**Verdict:** FIX

## Issues
1. **BLOCKER, R2 phase budget / HP arithmetic (§4).** The draft's own sum is 32 + 45 = 77, which is above the T1 band of 56-72, so it trims "to the upper edge" and picks 70 without redoing the budget. It also invents a "needles hit ×2 on the player side" doubling. In R2, "needles the player's hits land on" counts the enemy needles that the player's pointer attack hits, so that part is arguable. But the trim is unjustified, and the T3/T4 values (108, 140) are never derived.
2. **BLOCKER, R3 / R1 phase split (§4).** The threshold is 0.5, but the arithmetic says P2 is worth about 45 and P1 about 32. A 50/50 split makes P1 about 4+ turns and P2 about 3 at the reference player, so the "3.5 per phase" claim doesn't follow from the numbers. Set the threshold to match the budget (about 0.42), or justify 0.5.
3. **BLOCKER, §3 sustain.** The text contradicts itself: "below the 30 % cap ... Worst case ... over the cap ... I accept this." Accepting a breach of the cap is a hard-rule violation. The "3" used in the budget is also unrelated to the "4-5" it computed. Defense is not sustain in R2, but the draft counted it as sustain and then exceeded its own cap.
4. **MAJOR, R11 / R10 (§2 P1 notes).** "Big Overflow has no Perfect (6-tick, W W G G W W)" is correct. But the layout puts the pointers at 0 and 12, and the draft gives no slice boundaries, so the claim that "one needle is usually on a damage slice while the other is on Defrag or Null" is unverified. With sizes 6/5/4/5/5/5 (starting at tick 0), the boundaries are 0-6, 6-11, 11-15, 15-20, 20-25, 25-30. Tick 12 falls inside Defrag (slice 3) while tick 0 is on the Overflow edge. Both needles' positions are fixed at turn start by the respin, so no steady read is possible.
5. **MAJOR, N6 / ON_PERFECT.** Echo fires "on each player PERFECT landing", but Perfect-landing damage is dealt on resolve, so the preview shows the damage only if N6's listener is staged. This is correct as an N6 dependency but the draft doesn't state the preview behavior. R11 also says a 4-tick slice has no Perfect, so "Good-only window" on the Shim needs the `tick_quality` map named.
6. **MAJOR, §2 P2 / R8.** The Shim "applies OUTPUT_DOWN to the slice under your pointer" and is also a damage slice. That is acceptable under R8. But "Cleanses OUTPUT_DOWN" is offered as counterplay for a status that has no stated source of cleanse in the draft, and the status is ×1 with no cap stated.
7. **MAJOR, §8 fallback.** The N7/N20 `pierce` fallback says "pierce via an existing Pierce segment is not available to enemies". That is inventing a claim. The N20 fallback should state "drop pierce, raise Overflow".
8. **NIT, §9 / §1.** "Today's 150 HP" is a different elite's number from the file (the draft says it also carries a tier factor); verify. The Recall Unit precedent is cited as if it were a REBEL_CELL sim row.
9. **NIT,** the "Mirror" naming is placeholder-only and not worth the paragraph.

## Concrete fixes
- **Sustain (#3):** replace the paragraph with: "Sustain: none (no heal, no shield). BLOCK is defense, not sustain: 8 FLAT on one 4-tick slice (P1), 6 on one 6-tick slice (P2). Sustain term in R2 = 0."
- **HP (#1, #2):** budget with sustain 0 and the threshold at 0.45. T1: P1 = 9 × 3.5 × ~1.0 = 31.5. P2 = 9 × 3.5 × ~1.3 (the second-needle hit share) = 41. Total ≈ 72, so HP = 70. Floor = ceil(70 × 0.45) = 32 (P1 takes 38, P2 takes 32). T2: 11 × 3.5 × 2.3 ≈ 88, so use 86. T3: 14 × 3.5 × 2.3 ≈ 113, so use 108. T4: 18 × 3.5 × 2.3 ≈ 145, so use 140 (the band tops out at 144). Table rows: 70 / 86 / 108 / 140, floors 32 / 39 / 49 / 63.
- **Pointers (#4):** show tick boundaries and state that the Overflow's edge sits at tick 0. Put the needles at 0 / 13 so one lands in Defrag's 11-15 centre (tick 13) rather than on an edge.
- **Echo (#5):** add: "Echo is a staged ON_PERFECT listener; the preview shows 'ECHO −5' on the Perfect landing and undoes with the action."
- **Shim 4-tick (#5):** state `tick_quality` = W G G W (the R11 default for size 4), so no override is needed.
- **Cleanse (#6):** "OUTPUT_DOWN ×1 per Shim hit, cap ×2; removed by Cleanse (existing)."
- **N20 fallback (#7):** "Without N20: Overflow 14 FLAT single hit, no pierce; Shim one 12-damage hit."

## Keep
- The uneven needles and the no-Perfect big Overflow make the "which of us lands it" read a real one.
- The P2 question (is a Perfect worth 5?) flips cleanly from P1, and the P1 → P2 layout change is a new question, not attrition.
- The heat_effects decision is right (none exist, none added), and the dependencies are tagged with fallbacks.

## Q:
Q: Should Echo fire once per turn, so that multi-pointer Perfect classes aren't doubled?
Q: Should the P2 pierce Overflow be T2+ only?
Q: Does the "mirror" flavor need a copied wheel (a new system), or is authored data acceptable?
