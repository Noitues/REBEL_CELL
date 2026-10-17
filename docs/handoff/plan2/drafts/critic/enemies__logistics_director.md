<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__logistics_director; status ok; tokens in 7063 cache-write 0 cache-read 32585 out 9460; cost $0.058. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/logistics_director

**Verdict:** FIX (the P1 intake arithmetic is wrong, the Package geometry is undefined, and the respin-lock rule double-counts an existing rule)

## Issues

1. **MAJOR, §3 arithmetic (intake P1).** "Shim 1.07 + Overflow 1.4 + Shim 0.8 ≈ 3.3" is wrong.
   - Shim 10 (5 ticks): 5/30 × 0.8 × 10 = 1.33, not 1.07.
   - Shim 10 (4 ticks): 4/30 × 0.75 × 10 = 1.0, not 0.8.
   - The P1 total is 3.73, not 3.3. The T3 figure (5.6) shifts to about 6.3.
   - P2 (4.13) and P3 (7.53) re-add correctly. The tick sums (30 / 30 / 30) and the HP floors and budgets (87 / 105 / 132) also check out.
2. **MAJOR, §2 P2 Package geometry.** "A 4-tick segment centred on the tick your pointer reads" is undefined, because an even width has no centre tick.
   - The claim that the pre-latched Packages at ticks 7 and 22 "sit on weak edges" is false. A 4-tick segment around 7 covers ticks 6–9, which includes Good ticks (6 and 9).
   - The player wheel may also have variable slice sizes (N12).
3. **MAJOR, §2 P2 / design quality (Package threat).** Two 4-tick Packages cover 8 of 30 ticks, so a read happens about 27 % of turns and costs 2 RAM and half damage once. The expected cost is roughly 0.5 RAM per turn.
   - Steering around a Package is nearly free, so P2's question ("which slice do you read") is weak.
   - The §7 "weak player keeps reading it" claim is overstated, because the start-of-turn respin re-randomizes the landing.
4. **MAJOR, §2 P1 / §7 (Priority is too weak).** Priority covers 5 of 30 ticks and drains 3 RAM, about 0.4 RAM per turn against +4 RAM income.
   - The "RAM-starved going into P2" outcome never happens.
   - Racing is then dominant over paying to steer, so P1's question has a dominated answer.
5. **MAJOR, §2 P3 / §8 (the respin lock overlaps an existing rule).** GDD 2.5 already says Respin and Flip are "Blocked while resistance > 0". Weight 1 therefore already blocks both on the enemy wheel in P1–P3.
   - Only the own-wheel lock is new in N7.
   - The "None" fallback for N7 should say so.
   - The draft never notes that Flip is also blocked in every phase, which changes the counterplay lists.
6. **NIT, §8 on_enter_effects.** The fallback ("a hub ON_TURN_START that latches only when the ring is empty") is muddled. The N12 fallback P1 list is missing; it should give six 5-tick slices.
7. **NIT, naming.** "Dock" collides with the satellite-docking verb. Use "Tag" or similar.
8. **NIT, R10.** Needles are on tick 0 in every phase, so the pointer-on-any-tick tool is unused. This is acceptable, but Q4 should state it.

## Concrete fixes

- **Issue 1:** replace the P1 row with `≈ 3.7 (Shim 1.33 + Overflow 1.4 + Shim 1.0)`. At T3 this is ≈ 6.3.
- **Issues 2 and 3:** use a **6-tick Package**, defined as ticks [c, c+5] where c is the pointer's tick at the Dock resolve, clockwise. Max 2.
  - The entry Packages are pre-latched at ticks 8–13 and 23–28. This covers the Perfect ticks 10 and 25 and ticks 8, 9, 11, 12, 13, so they are dodgeable only by steering.
  - A read is then about 40 % per turn if the player is careless.
  - Fix the wording to "covers Perfect and Good ticks, so steer or Cleanse".
- **Issue 4:** set Priority to **drain 5 RAM**. The expected drain is 5/30 × 0.8 × 5 = 0.67 RAM per turn, and two Priority slices would be needed for real pressure. Add Priority to P1's Null slice only if the sim shows racing still dominates; otherwise drop the "RAM-starved" claim.
- **Issue 5:** in §8 write `N7: own-wheel respin lock only (enemy-wheel respin and Flip are already blocked by Weight >0, GDD 2.5). Fallback: none.` Add to §7 that Flip is unavailable in all phases.
- **Issue 6:** the N12 fallback P1 is Shim 10 · Defrag 8 · Priority · Overflow 14 · Shim 10 · Null, all 5 ticks.

## Keep

- Dropping Orbit (a no-op under the per-turn respin) and the P3 second needle, with the reasoning given.
- HP and phase floors with parking (87 / 105 / 132) that re-add correctly, and the clean three-phase band fit.
- P2 makes the Parasite ring the question, and its N10 fallback to the existing PARASITE status is honest.
- Resistance on the Hub in P1 and P2, so Hub Breach is a real answer.

## Q:
- Q: Should the own-wheel respin lock (P3) also apply while the start-of-turn respin is pending, or is the turn-start landing the one allowed random event?
- Q: Does the sim need a second Priority slice, or is Weight alone enough pressure for P1?
- Q: Do Packages persist into P3 (as drafted), or is `cleanse_on_enter = PLAYER` safer against enrage stacking?
