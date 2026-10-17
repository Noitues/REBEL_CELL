<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__drone_dispatcher; status ok; tokens in 4628 cache-write 0 cache-read 32585 out 2035; cost $0.018. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/drone_dispatcher

**Verdict:** FIX

## Issues

1. **BLOCKER, arithmetic, §2 layout.** The table has 6 slices with sizes 6+5+4+6+5+4 = 30, so the sum is fine. But the text says "5 slices on uneven sizes", and the "Priority 4 (G P P G is not used…)" cell is garbled. Slice 6 (Null, 4) has no stated quality map. Slices of 4, 5 and 6 ticks mix three maps with no stated intent.
2. **BLOCKER, R2/§3, sustain and Bay amount.** The layout still says "BLOCK 6 FLAT" while §3 and §9 say "drop to 4". The layout table contradicts the decision. The cap check is also wrong: with 2 of 6 slices and sizes 6+6 of 30, P(Bay) is 12/30 = 0.4, so the expected block is 0.4 × 4 × factor = 1.6 / 2.1 / 2.7 / 3.5. That is 17 / 19 / 19 / 19 % of reference dpt, so it is within the cap. The draft's "1.3 / 2.9" is neither derived nor consistent.
3. **BLOCKER, R3/R1, §4 HP arithmetic.** The sustain column is used as a subtraction of "3.5 × 1.3-2.9", which gives 4.5 / 5 / 7 / 10. That is inconsistent with the stated 1.3 and 2.9 (3.5 × 1.3 = 4.6 works, but T4 should be 3.5 × 3.5 = 12). The T1 result 31.5 − 4.5 = 27 does not equal the stated 30. T2 38.5 − 5 = 33.5 ≠ 36, T3 49 − 7 = 42 ≠ 46, T4 63 − 10 = 53 ≠ 58. Every row is off by 3-5 HP. The draft then adds "guards soak a share", which double counts.
4. **MAJOR, N13/GDD 2.7, §2 spawn.** "Launch on the pointer's slice" under REPLACE means a drone can replace a damaged drone every turn. That makes drone-killing pointless and contradicts "kill the first drone early" in §1. §7 also says "don't finish a drone about to be replaced", which contradicts §1's "shortening answer".
5. **MAJOR, Hub.** "Hangar: fewer than 2 drones, launch one" is described as `spawns` data. The text says "ON_TURN_START (value 2 today)" and "every_n = 1", which is not verifiable against the .tres. The hub rule and the spawn are two descriptions of the same thing.
6. **MAJOR, intake.** The sources do not reconcile. "Drones ≈ 3 at steady state" is the main damage, yet the Dispatcher alone is 2.7. The total of "3-5" is below 2.7 + 3. The drone damage is tier-scaled but the drone HP source is vague ("scaled by hp_by_tier of the drone"). A drone is not an `EnemyData`.
7. **MAJOR, §1 question.** "Needle sits behind a satellite" with a fixed needle at tick 0 means the guard is constant, so the question does not vary. Using R10 uneven needles is not an option for a single needle, but the position matters. The draft says "kept fixed for teaching" yet this is a normal at L3-6.
8. **NIT.** §10 says "drop drone Shim 3 → 2 if > 35 HP lost". That is a fix applied after the fact and should be in the numbers now.
9. **NIT.** The §8 N12 fallback says the layout is "6/5/4/6/5/4", which is inconsistent with the "5 slices" wording.

## Concrete fixes

- **Layout (fixes 1, 2):** replace slice 1 and 4 effect with "BLOCK 4 FLAT"; set quality maps: Bay 6 = W W G G W W, Shim 5 = default, Priority 4 = W G G W, Null 4 = none. Replace "5 slices" with "6 slices".
- **Sustain row:** expected block = 0.4 × 4 × [1, 1.3, 1.69, 2.2] = 1.6 / 2.1 / 2.7 / 3.5 per turn, i.e. 17-19 % of reference dpt (cap 30 %).
- **§4 table (3.5 turns, 1 needle; sustain × 3.5):**
  | Tier | Budget | Sustain | HP |
  |---|---|---|---|
  | T1 | 31.5 | −5.6 | 28 (band 28-36) |
  | T2 | 38.5 | −7.4 | 34 |
  | T3 | 49 | −9.5 | 44 |
  | T4 | 63 | −12.3 | 56 |
  Remove the "guards soak a share" sentence.
- **Spawn (4):** `on_occupied = SKIP` if a drone is on the target slice, and launch onto the slice at tick 10 (the opposite, unguarded one) so the player has a turn of warning. Delete the REPLACE claim and the "do not finish a drone" counterplay.
- **Intake (6):** state Dispatcher 2.7 + 2 drones × 1.5 = 5.7 per turn at T1, ×1.3 / 1.69 / 2.2 = 7.4 / 9.6 / 12.5. Set drone Shim to 2 now, so T4 is about 9.

## Keep

- The guard-versus-race question and a hub spawn that is data-only.
- Making drone pressure real, so the intake is above 0, which fixes the 0.05 problem.
- The 4-tick Priority with no Perfect is a good use of R11.

## Q:

Q: Should drone HP be a fixed 6, or hp_by_tier-banded as a satellite?
Q: Is the Hangar a hub rule or a spawn entry; which owns the max of 2?
