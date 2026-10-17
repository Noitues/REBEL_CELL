<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__handler_proxy; status ok; tokens in 5869 cache-write 0 cache-read 32585 out 6534; cost $0.042. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **1 (BLOCKER, Overflow lacks Perfect):** Overflow is now a 5-tick slice (W G P G W), so a Perfect exists. Final sizes are Leash 5, Shim 6, Block 4, Overflow 5, Shield 4, Null 6 = 30. The false "2 of 6 Perfect-quality" claim is removed. The 6-tick Shim (W W G G W W) and the 4-tick Block and Shield (W G G W) have no Perfect, per R11. The 6-tick Shim is now the weak-to-read slice, not Overflow.
- **2 (BLOCKER, HP over budget):** `hp_by_tier` is now 32 / 38 / 48 / 62, at or below the R2 budget of 31.5 / 38.5 / 49 / 63. The "+2 to +3 tolerance" is gone. Defense soak is quantified in §4 and shown to stay inside the 3-4 turn target.
- **3 (MAJOR, spiky intake):** Overflow drops from 14 to 10 FLAT. I also recomputed intake with the WEAK 0.5× factor, which v1 ignored, and dropped the "may need Overflow at 12" note. Intake is now 2.8 / 3.6 / 4.7 / 6.2 per turn; the arithmetic is in §3. The 6-tick Shim keeps 8 FLAT, so it is now the largest single hit at Good or better (T3 13.5, T4 17.6).
- **4 (MAJOR, garbled resistance line):** rewritten in §7 as "use the free nudge on your own wheel (no resistance)". The Ghost note is corrected to say only the first nudge ignores resistance.
- **5 (MAJOR, preview):** §2 and §7 now say Leash targets the slice under your pointer at resolve. The preview shows "LEASH on slice X", so preview equals result. I chose this over the opaque "best slice" design (the critic's Q).
- **6 (MAJOR, fallback):** the PARASITE fallback keeps Leash damage at 3. It is stronger (−50 % vs −25 %), and that is accepted for the fallback.
- **7 (NIT, names):** slice 3 is now BLOCK 6 and slice 5 is SHIELD 5. The old type names are no longer used.
- **8 (NIT, "T-less" wording):** reworded, and §10 asks the sim for the missing baseline row.
- **Kept:** the single-question concept, no sustain, no enrage, Resistance 2 and the single needle at tick 0.

# handler_proxy: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, REBEL_CELL. At L1-2 it teaches reading a status on your own wheel. At L5-6 it checks whether you kept a nudge in reserve.
- **Concept:** DISPATCH's local relay. It plants a LEASH (an OUTPUT_DOWN ×1 stack, −25 % output) on the slice your own pointer is reading when it resolves.
- **Question:** "Which of your slices is leashed, and do you pay to land elsewhere or accept the tax and burst?"
- **Fast answer:** Use the free nudge on your own wheel. Dodge the previewed Leash or Overflow, then hit it while its needle sits on Shield, Block or Null. Don't spend RAM nudging its Resistance 2 wheel.
- **Distinct from siblings:** Mirror Script, Echo Process and Cell Informant copy or replay you. The Proxy is the only normal built on a status on your wheel plus resistance.

## 2. Phase plan (single phase, no threshold, no floor)

| Item | Design |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | Resistance 2, restored each player turn (passive) |
| Statuses | OUTPUT_DOWN ×1 on your slice under your pointer (N8/N9) |
| Listeners | none |

**Layout (ticks sum 30; N12):**

| # | Slice | Ticks | Quality map | Effect |
|---|---|---|---|---|
| 1 | Leash | 5 | W G P G W | INFECT: OUTPUT_DOWN ×1 on your slice under your pointer (UNDER_POINTER), plus 3 FLAT damage |
| 2 | Shim | 6 | W W G G W W | SHIM 8 FLAT |
| 3 | Block | 4 | W G G W | BLOCK 6 FLAT |
| 4 | Overflow | 5 | W G P G W | OVERFLOW 10 FLAT, the threat slice |
| 5 | Shield | 4 | W G G W | SHIELD 5 FLAT (defense, not sustain) |
| 6 | Null | 6 | W W G G W W | nothing |

5+6+4+5+4+6 = 30.

- Leash is the signature slice. Its status resolves in the status pass, so the tax lands the next time that slice resolves.
- The preview shows the Leash target and the stack. The result equals the preview.
- Flat amounts are multiplied by the tier damage factor (R2).
- **Transition:** none.

## 3. Sustain and intake
- **Sustain:** none, so 0 % of reference damage. Block and Shield are defense, not heal.
- **Intake per turn.**
  - Assumptions: the needle lands uniformly over ticks, and WEAK ticks deal 0.5×.
  - Tick-weighted output factor: 5-tick slice 4/5, 6-tick slice 4/6 of full (W W G G W W has four WEAK ticks).
  - Full-output sum over the wheel, base values: Leash 3×4 = 12, Shim 8×4 = 32, Overflow 10×4 = 40. Total 84, divided by 30 ticks, gives 2.8 at T1.

| Tier | Factor | Intake/turn |
|---|---|---|
| T1 | 1.0 | 2.8 |
| T2 | 1.3 | 3.6 |
| T3 | 1.69 | 4.7 |
| T4 | 2.2 | 6.2 |

- All values are above 0.
- Spike hits at Good or better:
  - Overflow: T3 16.9, T4 22.
  - Shim: T3 13.5, T4 17.6.
- A good player dodges with the free nudge and takes about 1-2 per turn. A weak player takes the full intake plus the Leash tax.

## 4. HP by tier
R2 budget = reference dpt × 3.5 turns × 1 needle, with no sustain to subtract.

| Tier | dpt | Budget | hp_by_tier | Normal band |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 32 | 28-36 |
| T2 | 11 | 38.5 | 38 | 34-44 |
| T3 | 14 | 49 | 48 | 44-56 |
| T4 | 18 | 63 | 62 | 56-70 |

- **Defense soak** (R2 does not subtract it):
  - Block and Shield cover 8 of 30 ticks, and WEAK ticks halve them.
  - Block per tick, T1: 3, 6, 6, 3 (sum 18). Shield: 2.5, 5, 5, 2.5 (sum 15). Together 33 / 30 ≈ 1.1 per turn at T1.
  - That is about 12-13 % of dpt at every tier, so the fight runs about 0.4 turns over budget: 3.9 turns at the reference.
  - This stays inside 3-4. It is also why HP is not rounded up.

## 5. Enrage
None (R4). With no sustain, it cannot stall.

## 6. Buffs and counter Exploits
Not applicable (normal enemy).

## 7. Counterplay
- **Good player:**
  - Reads the Leash preview and uses the free nudge on their own wheel (no resistance) to move off the leashed slice. Cleanse or Encrypt also work.
  - Dodges Overflow's Perfect and Good ticks the same way.
  - Bursts on its Shield, Block or Null turns. Nudging its wheel only works for 3+ ticks, and only the Ghost's first nudge ignores resistance.
- **Weak player:**
  - Ignores the Leash, so their next Perfect Shim deals 0.75×.
  - Spends RAM on its resistant wheel.
  - Over-defends against Shim and then eats a full Overflow.

## 8. Systems needed
- **N12** for the 4, 5 and 6-tick slices. **Fallback:** six 5-tick slices with the same effects.
- **N8/N9** for ×N stacks and OUTPUT_DOWN. **Fallback:** the existing PARASITE status (−50 %) as the Leash, still 3 damage. It is stronger, and that is accepted for the fallback.
- **N1/N2** for FLAT scaling and `hp_by_tier`. **Fallback:** a single `hp`.
- Not needed: N3-N7, N10, N11.

## 9. Delta vs today
- **Kept:** id, corporation, passive_resistance 2, one needle at 0, cycle_reward 15, a Null slice.
- **Changed:**
  - Wheel goes from Defrag, Shim, Defrag, Shim, Sandbox, Null to Leash, Shim, Block, Overflow, Shield, Null with uneven sizes.
  - HP goes from 64 to 32 / 38 / 48 / 62.
  - Description: "Marks your slice, then hits it."
- **heat_effects:** none on the file, none added.

## 10. Predicted sim check
There is no baseline row for this enemy, so the sim should record one.
- **Turns:** about 3.9 mean at the reference, p90 5.
- **Win %:** T1 ≥ 97, T2 ≥ 96, T3 ≈ 93, T4 ≈ 91.
- Why: the intake is 3-6 per turn, so a 3.9-turn fight costs roughly 11-24 HP against a 45-60 HP operative, with the Leash tax as the only compounding.

## 11. Q:
- Q: Is a 10 FLAT Overflow, with Perfect and Good ticks on a 5-wide slice, too spiky for L1-2 teaching, or should the layer-1 variant swap it for Shim?
- Q: Does ×1 OUTPUT_DOWN still apply on a WEAK Leash landing (R8 default: yes)?
- Q: Should the 5 FLAT Shield also scale by tier (R2 says yes)? Or does the shield cap make it fixed?
- Q: Is Resistance 2 a strong enough signature once Cell Informant and Loyalty Test are redesigned?
