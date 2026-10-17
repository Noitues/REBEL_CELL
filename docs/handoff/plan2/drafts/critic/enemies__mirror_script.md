<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__mirror_script; status ok; tokens in 4219 cache-write 0 cache-read 32585 out 1728; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/mirror_script

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 geometry/arithmetic.** The layout is six 5-tick slices at ticks 0, 5, 10, 15, 20, 25, so the twin of slot i is slot i+3, which the table respects. But the claim "a 15-tick nudge or spin sends both needles to the twins" and "a 10-tick shift moves both" (§7) conflict: a 10-tick shift moves the pair to a different slot pair, not the twin. It also contradicts the "any rest position reads one of three pairs" claim (a needle reads one of 30 ticks, and the pair is always 15 apart, so the pairs are {0,3},{1,4},{2,5}; fine). The real error is that the pairs aren't equally likely: Citation+Null is 1/3 but Overflow+Block can't be avoided by "one needle is ever dangerous" since Shim+Block and Overflow+Block both put a damage slice on one needle. The "mirror geometry" is just a fixed pair table, so the stated "forcing both needles onto Null/Block and bursting while blanked" is wrong: Citation+Null has no Block, and there is no pair that is Null+Block.
2. **BLOCKER, §3 intake math.** Pair means (9+0+16)/3 = 8.3 is correct only at T1. It ignores that Block is on the enemy's own wheel, not yours. "Block 6 is defense only" and the Block-needle absorbs your damage, not its own intake. The 17 HP over 3.5 turns uses 5/turn with an unjustified "steers away half the time."
3. **MAJOR, §4 HP budget.** The draft admits it didn't use R2 (needles hit × dpt). With 2 needles the budget is 63/77/98/126 before sustain, and the draft picks ~half of that with a hand-wave ("65 % goes through"). The chosen values (34/40/50/64) sit inside the band, but the stated arithmetic doesn't derive them. Also, the draft says 50 "today is inside the T3 band" (44–56): true, so there's no change at T3.
4. **MAJOR, §2 vs ground truth.** The draft says hp in "today" is 50 and Solar Flare exists; I can't verify that, but "Echo Process / Handler Proxy / Loyalty Test not covered here" is filler, and the brief says rebel_cell mirror enemies use the player's wheel (GDD 8.5), which this ignores.
5. **MAJOR, §8 dependencies.** Citation as "OUTPUT_DOWN ×1" is called N8/N9, but ×1 on one status needs only N9. The fallback "PARASITE halves output" is a different value (−50 % vs −25 %). Name the delta.
6. **MAJOR, §10.** The fight length of 3.4 turns at "every tier" is asserted, not derived. T4 intake: 5 × 3.5 × 2.2 = 38.5 uses 5/turn (already unscaled at T1); the damage factor is 2.2 but the slice numbers (9, 16) are not scaled in the table.
7. **NIT, Q3.** "Q11" refers to the V2 list, not this file; the answer is already "yes unless a slice authors a minimum tier."
8. **NIT, §1.** Layer teaching claim "L1-2" with an Overflow 16 at T1 looks heavy for a teaching enemy.

## Concrete fixes

- **Issue 1/§7 replacement:** "Pairs are {Shim+Block, Citation+Null, Overflow+Block}. A 5-tick nudge moves both needles to the next pair. A 10-tick spin moves two pairs. Good player: if Overflow+Block, spend the free nudge (5 ticks) to land Citation+Null or Shim+Block, then burst." Delete "forcing both needles onto Null/Block."
- **Issue 2:** state "Block gives this enemy its own defense: it reduces your hits by 6 on the needle reading Block." Intake line: "T1 steered: 3 per turn (avoid Overflow); unsteered 8.3."
- **Issue 3 table:** Budget = dpt × 3.5 × 1.5 effective needles (one needle often reads Block/Null): T1 47 → too high for band; so state the choice: "HP 34/40/50/64 = band midpoints; effective needles ≈ 1.0 because one needle usually reads Block/Null."
- **Issue 5:** "Fallback: PARASITE at −50 % (harsher than OUTPUT_DOWN ×1 at −25 %); lower Citation to apply once only."

## Keep
A single clear geometry question, no sustain, nonzero intake, and cutting Solar Flare to avoid RAM-doubling chains on a normal.

## Q:
- Should the pair table include one Null+Block pair so "burst while blanked" is real?
- Should L1 use Overflow 12 as the draft suggests?
- Should the mirror theme (copying your wheel, GDD 8.5) appear at all in this normal?
