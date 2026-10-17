<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__the_handler; status ok; tokens in 7852 cache-write 0 cache-read 32585 out 1930; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/the_handler

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 tier bands / §4.** Authored HP is the band ceiling at every tier (105 / 128 / 162). The draft then sums its own phase budgets to 120 / 147 / 187, which is outside the band. "Scale every phase by ~0.87" is the justification, but 87% of 120.4 is 104.7, so the arithmetic only works if the budget already includes the 2-needle P3. The draft's claim of "~3.05 turns per phase" also fails R1's 3–4 turns. At skill 1.0 the fight is below the 6-turn floor.
2. **BLOCKER, R1 / §4 phase budget.** The 0.87 factor is applied uniformly. Phase HP is 27 / 28 / 50, so P3 is 48% of HP and P1/P2 are about 26% each. P1 and P2 at 27–28 HP against 9 dpt is 3.0–3.1 turns, under the 3-turn floor once parking and a missed turn are counted.
3. **MAJOR, R2 sustain / §3.** The sustain subtraction in §4 is 5.6 (7.3, 9.5). §3 gives 1.6/turn × 3.5 = 5.6, which is consistent. But Redact BLOCK 8 is a *defensive* slice on the player's damage only if it is read, and it is used as "sustain" even though BLOCK is not sustain in R2's sense (heal/shield per turn). It is acceptable, but the label should say so.
3b. **MAJOR, R9 / §2 P1 and P3.** The Dose rider says "CORRUPTED on 1 random non-NULL slice" with no named RNG stream. "Random" needs a checkpointed stream, and the preview must equal the result. Mark has the same problem.
4. **MAJOR, N6 / §8.** The Echo amount "derived from the triggering slice's output" is an NEW rider that is not tagged with an N# or a NEW: name. Shadow's "ignores resistance, staged with the action" is also a new rule, not covered by N6's listeners. Both need a NEW tag.
5. **MAJOR, R6 / §2 P2→P3.** `cleanse_on_enter = PLAYER` is described as "burns your marks", but R6 says cleanse is meant to pair with a counter Exploit. A free PLAYER cleanse on a mini-boss with no buffs removes the RAM puzzle that P2's CORRUPTED set up. P2 therefore asks no question that P3 inherits. This is a dominated outcome for Dose.
6. **MAJOR, R4 / §5.** Class default is start 10. "Slower players meet the first step in P3" fits, but the draft's own estimate of ~9.2 turns means enrage never matters for a reference player. State the intended effect, or author the turn-8 enrage and justify it.
7. **MAJOR, §10 / checks.** T3 win ≈ 84% falls below the proposed 90% criterion, and the draft says so without a fix. The ≈19-turn estimate for today's 170 HP at T1 is also unsupported (170 / 9 ≈ 19, ignoring the 2-resistance and 2-pointer phases).
8. **NIT, wheel math / §2 P3.** The sizes 5+3+6+4+4+4+4 = 30 are correct. The table lists ticks as 5 (0–4), 3 (5–7), 6 (8–13), 4 (14–17), 4 (18–21), 4 (22–25), 4 (26–29), which is also correct. The needle at 11 sits on Directive. The needle-pair counts (8+9+5+5+1+2 = 30) sum correctly, but the needle at tick 0 is on the edge of Order and Mark, so the "damage" counts should be rechecked against slice edges.
9. **NIT, text.** The notes in the draft header say the Handler "stays distinct from Mirror Script", yet P1's mirror-your-nudge idea is the same family. Say how it differs.

## Concrete fixes

- **#1/#2:** Pick one of two options. Option A: keep the bands and cut P3 to a single-pointer budget equivalent. Authored HP 90 / 110 / 138 split 30 / 30 / 30 at T1 (P1 33%, P2 33%, P3 33%) gives ~3.3 turns for P1 and P2. Option B: ask the designer to raise the band (Q1). Recommend A.
- **#3b:** Add "RNG stream `fight`, set at the checkpoint on resolve" to every random-slice rider.
- **#4:** Tag "NEW: listener output-read rider (N6 extension)" and "NEW: coupled-wheel nudge (N6 extension)". Fallbacks: flat Echo 5 × factor; P1 resistance 2.
- **#5:** Change to `cleanse_on_enter = NONE` and give P3 a Redact that cleanses nothing, or keep PLAYER and add the Cleanse card to the counterplay text.
- **#7:** Reword to "T3 below criterion; first knob is Directive 16 → 12".

## Keep

- Three phases that each ask a new question (shared motion, Perfect cost, uneven needles).
- The uneven needle at tick 11 and the needle-pair table.
- Echo that punishes Perfects and the Spin/Flip decoupling counterplay.

## Q:
1. Is raising the 3-phase band acceptable, or must P3 be budgeted as one needle?
2. Should P3 inherit the player's statuses, with the cleanse moved to another source?
3. Does Shadow need an N# of its own?
