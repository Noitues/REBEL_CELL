<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__dispatch_core; status ok; tokens in 8822 cache-write 0 cache-read 32585 out 2272; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/dispatch_core

**Verdict:** FIX

## Issues

1. **BLOCKER, §2 layouts, tick sums.** I re-added every layout.
   - P1: 5+5+4+6+4+6 = 30 ✔.
   - P2: 5+4+5+4+6+3+3 = 30 ✔.
   - P3: 3+5+4+5+3+5+5 = 30 ✔.
   - P4: 5+5+5+4+5+6 = 30 ✔.
   - P5: 4+4+4+4+5+4+5 = 30 ✔.

   Sums pass. The failure is inside the slices. P4 lists "Echo Drone dock slot 5" as a slice, but a satellite is not a slice type. P3 says "Overwrite 3 · … Perfect is the only dangerous Perfect for me too", which is unreadable. P1's 4-tick Strike (W G G W) has no Perfect, yet the text says "same output" without stating the consequence.
2. **BLOCKER, R3/R1 thresholds.** §2 states 0.80/0.60/0.40/0.20, §4 replaces them with 0.82/0.64/0.44/0.22. The shares in the §4 table are 18/18/20/22/22 = 100 ✔, but the §2 header and the P1–P5 captions still use the old values. Also, P1's budget row (54 HP vs 52.5) is fine, but "bonus ≈ 70" for P3/P4 is unjustified. R2 says HP is proportional to the player's hits landing on the enemy's needles, and that is not shown.
3. **BLOCKER, R4/R2, enrage vs turn count.** The path puts P4→P5 at turn 13–14, but cumulative turns are 3.6+3.6+3+3.3 = 13.5. The enrage step at turn 10 therefore lands in P4, not "P3–P4". That is minor. The real problem is that 17.2 turns includes P5 at 3.7, with the turn-15 step inside P5, so the fight is pressured exactly as intended; this part is fine.
4. **BLOCKER, R8/R9, P2 Audit Strike.** `hits_per_target_status` is described as "+1 hit per stack, max 3". The text says "Total up to 66 at ×2", which is 3 hits × 22. With a max of 3 hits, ×2 stacks gives 3 hits. OK, but P3's cleanse text says "cleans one stack tier: OUTPUT_DOWN ×1 each", and `cleanse_on_enter` has no such partial mode (NONE/OWN/PLAYER/BOTH). R6 gives no partial cleanse.
5. **MAJOR, R7, buffs.**
   - The Forecast row contains "Off: only … no: off =" (an unedited draft remnant).
   - Three of the eight buffs have no Exploit mapping given the "legacy Virus (replaced)" claim.
   - Quorum conflicts with the pointer rule (GDD 2.7), and the draft itself raises this in a Q.
   - "Pool is 8" is fine, but the draft counts 5 "new" and 3 "legacy" without listing which is which.
6. **MAJOR, N# tagging.**
   - Late Fee uses ON_RAM_SPENT (N6) ✔.
   - The Forecast record is tagged NEW but should be N6 with a per-turn record (ON_RESOLVE already exists).
   - `repeat_multiplier` is a new rider that belongs under N20.
   - Echo uses ON_PERFECT ✔.
   - The P5 "ON_HIT_DEALT" is correct as N6.
7. **MAJOR, Mirror Eye line.** Written as "is retired (too much, see Q)": a dead rule left in the table, with no matching Q.
8. **MAJOR, R6/R9 and the phase text.** Dose is a RAM tax. P1's intake, "2–4 per turn", conflicts with the Strike doubling to 36 on repeat. The 2–4 figure is reached only with perfect rotation, so it is not an intake at the reference player.
9. **MAJOR, §10.** The estimate says "12–20", then asserts a skilled bot finishes in 11–13, below the band. No baseline row is compared.
10. **NIT.** The draft lists Late Fee as a "listener" without stating cap-per-turn units. "Forecast" appears as both a slice and a buff.

## Concrete fixes

- **Fix 1.** Replace the P4 layout row with: `Order 5 · Forecast Strike 5 · Directive 4 · Audit Strike 5 · Null 6 · Order 5` = 30. Echo Drones dock on slices as satellites (N13); they are not a slice entry.
- **Fix 2.** Thresholds everywhere: 0.82 / 0.64 / 0.44 / 0.22. Replace the §2 line "0.80 / 0.60 / 0.40 / 0.20" with that. Replace "bonus ≈ 70" with: P3 and P4 get 2 needles, so the player's hits land twice. Budget = (18 − 3) × 3.5 × 1.3 ≈ 68 for 60–66 HP, reading 3.0–3.3 turns.
- **Fix 4.** Use `cleanse_on_enter` = PLAYER (R6), or NONE; delete "cleans one stack tier".
- **Fix 5.** Replace the Forecast row's Notes with "Off: no repeat tax." Also add: Cell Patch's Exploit is a Virus-type.
- **Fix 6.** Retag: `repeat_multiplier` is N20 plus N6; remove "NEW: last-landing record" and use N6 with a saved per-turn field.
- **Fix 7.** Delete the Mirror Eye sentence.
- **Fix 8.** State P1 intake as "6–10 with rotation, 36 on repeat".
- **Fix 9.** Add: the bot's best play (16–35 dpt) gives 9–12 turns, so the fight sits under target. Raise HP via hp_bands for ICE >1.30.

## Keep

- The Forecast concept (punish habits, a reading test) is distinct from the Handler's mirror.
- The P5 race with Code Red, no defense and three needles.
- A single sustain source at 3.6 against a cap of 5.4, shown with arithmetic.

## Q:

Q: Should Forecast record the previous landing, or read the staged landing (pure function)?
Q: Is Quorum worth keeping given it conflicts with the pointer rule?
Q: Should the P2 stack puzzle carry into P3 (NONE)?
