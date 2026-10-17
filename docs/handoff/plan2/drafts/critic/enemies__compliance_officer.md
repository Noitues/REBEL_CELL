<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__enemies__compliance_officer; status ok; tokens in 4795 cache-write 0 cache-read 32585 out 1785; cost $0.017. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: enemies/compliance_officer

**Verdict:** FIX

## Issues

1. **BLOCKER, §2/§7 vs R10 and the draft's own claim.** The draft calls the needle "uneven on purpose (R10)" but has one pointer at tick 0. The R10 claim is empty. The layout also never says which slice sits on tick 0, so no tick positions can be checked.
2. **BLOCKER, §1/§7, internal contradiction on the Audit trigger.** §2 says "paid nudge on any wheel" triggers Audit. §1 says "pay RAM only when exactly one tick from a Perfect", and §7 says a paid nudge pushes it onto Null. Q1 then asks whether the trigger should be enemy-wheel only. As written, the Audit block taxes the player's own precision nudges, so the draft's own advice (spend RAM only near a Perfect) always feeds Audit. The question the enemy asks is unresolved.
3. **MAJOR, §7, wrong mechanics.** "Hub Breach turns off resistance and Audit stays" is fine. But "one free nudge of your own does not move its wheel" is wrong: the free nudge can target the enemy wheel, and resistance 2 absorbs 2 ticks. A free nudge of 1 is fully absorbed, so a free nudge on the enemy wheel is useless. The draft never says this. Because a nudge on the enemy wheel can't succeed, the enemy wheel is effectively fixed after the respin, and only a Spin ≥3, Freeze or Hub Breach moves it. This changes what the fight asks.
4. **MAJOR, §3, sustain arithmetic.** Audit's 4 FLAT block × tier factor is sustain, and Defrag 6 is a second source. R1/§4 allow at most one source. The draft's own worst case, 2.8/turn against a 2.7 cap, already exceeds the limit. It also ignores that block only matters if the player's damage lands.
5. **MAJOR, §3, intake arithmetic.** (5+5+7)/30 = 17/30 = 57 %, which is right for the Shims. But 57 % × 7 = 4.0 and 10 % × 12 = 1.2 give 5.2/turn raw. "≈ 2.5-3.5 after one free nudge" is asserted, not derived. A 3-tick Overflow window at 10 % is also not "rarer Perfect landings" against you: the P is 1 tick.
6. **MAJOR, §4, HP budget.** The sustain deduction is inconsistent ("≈ 3", "5", "7"), and the same 3 is subtracted at every tier. Taking 31.5 − 3 ≈ 29 and rounding up to 32 breaks the stated arithmetic. T2 38, T3 50 and T4 62 are in band. The numbers need a consistent derivation.
7. **MAJOR, §10, prediction.** T4 at 4.0 turns while enemy intake rises to 6.6/turn is predicted without the new-Audit effect. The line "Resistance 2 lowers friction" contradicts the draft's claim that the fight gets harder.
8. **NIT, §9.** Heat effect "Late Fee" is a name-spend, and its rule isn't specified.

## Concrete fixes

- **Fix 1:** Put the pointer at tick 15, the centre of the 7-tick Shim. Say "needle fixed at tick 15, centre of the 7-tick Shim (slice 5)". State the slice start ticks: Shim 0-4, Defrag 5-8, Shim 9-13, Overflow 14-16, Shim 17-23, Null 24-29. That is the sum 30, and tick 15 is then the Overflow's centre, not the Shim's. Choose one and give the offsets. Drop "uneven on purpose (R10)".
- **Fix 2:** Audit: "on your paid nudge on the enemy wheel only (ON_NUDGE, target wheel = enemy)". Own-wheel paid nudges are free of Audit.
- **Fix 3:** Rewrite counterplay: "the free nudge on the enemy wheel is absorbed (resistance 2); real answers are Spin ≥3, Freeze, Hub Breach or Ghost's first nudge."
- **Fix 4:** Make Audit the sole sustain, and change Defrag 6 to Shim 7 or Null. Cap check: 4 × 0.5 = 2 ≤ 2.7.
- **Fix 5:** HP: T1 9×3.5 = 31.5 − 2 → 30; T2 38.5 − 2 → 36; T3 49 − 2 → 47; T4 63 − 2 → 61. `hp_by_tier` = [30, 36, 47, 61].

## Keep

- The question ("what does your landing cost you?") is a distinct manipulation-economy hook.
- The 3-tick Overflow window and 7-tick safe Shim are a readable risk/reward.
- A clear N12/N6 fallback table and a kept Compliance Lock identity.

## Q:

Q: Should the Audit trigger exist at all if enemy-wheel nudges are absorbed by resistance 2 anyway?
Q: Which slice starts at tick 0 or 15?
