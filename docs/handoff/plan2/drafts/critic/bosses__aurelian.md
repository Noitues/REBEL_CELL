<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01Jqt9aXUdGm76ioUwgCwf7Z, custom_id critic__bosses__aurelian; status ok; tokens in 21095 cache-write 32585 cache-read 0 out 17743; cost $0.151. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: bosses/aurelian

**Verdict:** FIX

## Issues

1. **BLOCKER, R2 budget / §3.4 buff 5 and §3.3.** The Lictor buff is not in the phase budget and is not optional. A player pointer that lands on a guarded slice must hit the satellite (GDD 2.7). "Only paid by players who attack a guarded slice" is therefore wrong. The text "Lictors on the Gladius slices (P2–P4)" also fails in P3, which has one Gladius (5 ticks) for two Lictors. In P2 and P4 the two Gladius slices cover 40 % of the ticks, so the satellite HP (2 × 15 at T4) pushes those phases to about 4.5 turns, over the 3–4 limit.

2. **BLOCKER, arithmetic, §4.2 Praetorian P1 sustain.** The percent shield is computed on the wrong HP. SHIELD PERCENT 5 % reads max HP, so 5 % × 58 = 2.9, and × 5/30 gives 0.48 per turn, not 0.25. The T2–T4 values (0.29, 0.37, 0.46) are halved the same way. The authored HP still lands in band, but the shown numbers are wrong.

3. **MAJOR, R1 "every phase a new question" / §3.4 Gate Codes.**
   - P1 has no Thumbs or Dole slice, so the hub CALL is its only verdict source.
   - With Gate Codes ("hub only MARKs"), P1 has no verdict question left and becomes attrition.
   - P4's inversion also disappears, because the CALL it modifies is off.
   - This contradicts "counters degrade, never delete a phase", and it is a signature buff.

4. **MAJOR, design duplication, §3.2 P3 and P5.** The Murmillo "×3 on Perfect" with "deny the Perfect" counterplay copies Genome Core's Medicine and the "deny the Perfect" answer to it. P5 copies Genome P4 almost exactly: two needles, no defense, pierce, and ×N Perfect. The brief asked for a distinct boss, and the shared skeleton is acknowledged in §3.8 but not resolved.

5. **MAJOR, R11, 8-tick slices.** The mini-boss P3 Thumbs, the Dole Cart Dole and the boss P1 Null are 8 ticks, and R11's default table stops at 7. The rule gives W W W G G W W W (no Perfect), so 75 % of that slice reads WEAK. The intake arithmetic assumes full output on it and is overstated.

6. **NIT, R2, Vestal.** The text says the percent shield is "never rescaled", but the sustain numbers 1.5 / 1.9 / 2.4 are scaled by the damage factor. Unscaled values are 1.36 / 1.76 / 2.24, so the budgets are 33.7 / 42.8 / 55.2. The authored HP is still in band.

7. **NIT, US spelling.** "defence" and "Defence" appear several times, and "flavour" in the headings. Use "defense" and "flavor".

8. **NIT, internal contradictions.**
   - §1.2 says VERDICT is "not a new system" but §1.7 and §5 require NEW-A.
   - The second enrage step at turn 16 is not "start of P5" (P5 starts near turn 14).
   - Gladius/Thumbs "clear marks by landing WEAK" is bad advice, because it trades the mark for CORRUPTED.
   - DECOY is an asset type, not a threat.

## Concrete fixes

- **(1) Lictors:**
  - Lictor buff: one Lictor, P2 only, docked on the first Gladius (6 ticks), 8 HP.
  - Set the thresholds to 0.88 / 0.775 / 0.46 / 0.33, so the floor is ceil(0.775 × 380) = 295.
  - Phase HP is then P1 45, P2 40 (+8 Lictor = 48), P3 295 − 175 = 120, P4 49, P5 126 (total 380).
  - Turns are 3.4 / 3.2 / 3.9 / 3.7 / 3.5 = 17.7.
  - Replace "optional detour" with "a forced guard when the needle sits on that Gladius; budgeted in P2".
- **(2) Praetorian P1 sustain:** 1.81 / 2.31 / 2.99 / 3.85.
  - P1 budget: 25.2 / 30.4 / 38.5 / 49.5.
  - Sum: 56.7 / 68.9 / 87.5 / 112.5.
  - Keep the authored 58 / 70 / 89 / 114 (in band) and the threshold 0.55.
- **(3) Gate Codes → TOLL GATE:** "CALL becomes deferred. Marks it would judge are judged at your next turn start; the verdict map, including P4's inversion, is unchanged." Every phase keeps its question, and you get one turn to Cleanse.
- **(4) Murmillo:** "OVERFLOW 7, ×3 while the slice under your pointer is marked" (rider `multiplier_vs_status`, NEW: slice rider, N20 extension). The answers become Cleanse, Encrypt or steering, not the Genome nudge. Redo the P3 and P5 pairing tables around marks instead of Perfect ticks.
- **(5):** Add "8-tick default map: W W W G G W W W; no Perfect" to §2.2. Redo the P3 intake as 10/30 × 9 × 0.5-weighted for WEAK-heavy reads, or author `tick_quality` G G G G G G G G if full output is intended.
- **(6):** Vestal sustain is 1.36 / 1.76 / 2.24, with budgets 33.7 / 42.8 / 55.2.

## Keep

- The house rule is genuinely new: it grades the landing tier. The read-tier table and the inversion as a data-only `verdict_map` change are elegant.
- Every layout sums to 30. I verified all boss, mini-boss, normal and elite layouts, the 5-phase budget (379), the floors, and the 17.6-turn total. The uneven-needle pairing tables are the best readability aid in the draft.
- The roster teaches mark → call before the Games Master uses them, and the draft honestly says that N6, N7 and N10 are not needed.

## Q:
- Should a PERFECT-to-OVERCLOCKED "loan" be valued by the sim before the Perfect-hook classes are judged under the boss P4 inversion?
- Is a forced bodyguard satellite acceptable on a boss at all, or should Lictors be mini-boss-only?
- Does the Dole's +3 RAM gift count as a "flat amount" under R2 (scaled by tier), or is it a buff exempt from scaling?
