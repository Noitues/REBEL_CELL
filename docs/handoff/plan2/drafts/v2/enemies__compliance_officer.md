<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__compliance_officer; status ok; tokens in 6431 cache-write 0 cache-read 32585 out 7166; cost $0.046. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, needle claim and undefined ticks):** The "uneven on purpose (R10)" claim is dropped. A single needle needs no unevenness. The needle is fixed at tick 0, and every slice now has explicit start-end ticks at rotation 0 (rotation is re-randomized each turn). Sizes re-added: 5+3+7+6+4+5 = 30 (see §2). I kept tick 0 rather than tick 15 because the respin randomizes rotation, so the pointer position carries no information. What matters is the slice map.
- **Issue 2 (BLOCKER, Audit contradicts advice):** Audit now fires only on a paid nudge on the enemy wheel (`ON_NUDGE`, target wheel = enemy). Own-wheel nudges, free or paid, never feed it, so "pay RAM only near a Perfect" is consistent. The question is resolved as "which wheel do you move?". Audit is a tripwire on the one move the lock makes futile. This resolves critic Q1: keep it, and show an ABSORBED preview.
- **Issue 3 (MAJOR, wrong mechanics):** Counterplay rewritten. Resistance 2 absorbs a ±1 nudge fully, so enemy-wheel nudges do nothing. The enemy wheel is effectively fixed after the respin. Real movers are Spin ≥3, Freeze (skips the respin), Hub Breach and Ghost's first nudge.
- **Issue 4 (MAJOR, two sustain sources):** Defrag is removed from the layout (replaced by a Shim, so Shims ×4). Audit is the only sustain. It is BLOCK 2 FLAT, at most once per turn. Cap check is in §3.
- **Issue 5 (MAJOR, intake not derived):** Intake is now derived tick by tick, with the tier-quality weighting (§3). The mistaken "rarer Perfect" claim is removed.
- **Issue 6 (MAJOR, HP derivation):** Adopted `hp_by_tier` = [30, 36, 47, 61] with one consistent −2 sustain deduction per tier (§4).
- **Issue 7 (MAJOR, prediction):** Redone. T4 is predicted below 90% and the "lowers friction" contradiction is removed (§10).
- **Issue 8 (NIT, Late Fee):** The rename is dropped. The existing Heat 50+ effect is kept unchanged, with no new name.

# compliance_officer: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns, no enrage. Solace compliance enforcer.
- **Layers:** L1-2 teaching at T1 (the first "the enemy's wheel is locked" fight). At T2-T3 in L5-6 it is the fight that punishes players who try to steer the enemy instead of themselves.
- **The one question:** *"Which wheel do you move?"* Resistance 2 makes the enemy wheel effectively fixed after the respin. The honest answer is your own wheel: make your best landing and deal with its landing by block, SANDBOX or damage race.
- **Answer that shortens the fight:** ignore its wheel, nudge your own wheel to your best slice, and burst. Premium answers: Hub Breach, Freeze, Spin ≥3 and Ghost's resistance-ignoring first nudge, if you want to move its needle.
- **Today's problem:** resistance 3 is an invisible wall (testers: 12+ turns, no way to make progress). This version states the wall in the preview (ABSORBED) and gives a payoff for working around it.

## 2. Phase plan
One phase, no threshold, no floor.

| Item | Design |
|---|---|
| Needle | 1, fixed at tick 0 |
| Hub | Compliance Lock: resistance **2** (was 3), restores each turn. Blocks Flip and Respin while > 0. |
| Listener (N6) | **Audit:** on your paid nudge on the enemy wheel (it will be absorbed), it gains BLOCK 2 FLAT (× tier damage factor), at most once per turn. Preview shows "ABSORBED 1/2, AUDIT +2". Free nudges and own-wheel nudges never trigger it. |
| Statuses | none |

**Layout at rotation 0** (rotation re-randomizes each turn; sizes sum 5+3+7+6+4+5 = 30):

| # | Slice | Ticks | Size | Effect |
|---|---|---|---|---|
| 1 | Shim | 0-4 | 5 (W G P G W) | 6 damage FLAT |
| 2 | Overflow (Penalty) | 5-7 | 3 (G P G) | 12 damage FLAT |
| 3 | Shim | 8-14 | 7 (W W G P G W W) | 6 damage FLAT |
| 4 | Null | 15-20 | 6 | nothing |
| 5 | Shim | 21-24 | 4 (W G G W) | 6 damage FLAT |
| 6 | Null | 25-29 | 5 | nothing |

**Why this layout:** the 3-tick Overflow is narrow but cannot be moved off by nudging, so the answer is defense or speed. The two Null slices (11 ticks) are the "lucky" outcomes. Shims never reach full Perfect on the 4-tick slice, so that landing is a modest hit.

**Transition:** none.

## 3. Sustain & intake
- **Sustain:** Audit only, BLOCK 2 FLAT once per turn. At T1 the cap is 30 % × 9 = 2.7/turn and Audit gives 2 (×1.0). The other tiers: T2 2.6 vs 3.3, T3 3.4 vs 4.2, T4 4.4 vs 5.4. All are under the cap. It fires only if the player attempts an enemy-wheel paid nudge, so a good player takes none.
- **Intake** (enemy wheel can't be moved, so the landing is the raw expectation). Average output per landing by slice size:
  - 5-tick Shim: (1 + 2 + 2×0.5)/5 = 0.8 → 5 ticks × 0.8 = 4.0
  - 7-tick Shim: (1 + 2 + 4×0.5)/7 = 0.714 → 7 × 0.714 = 5.0
  - 4-tick Shim: (2 + 2×0.5)/4 = 0.75 → 3.0
  - Shim total 12.0 weighted ticks × 6 / 30 = 2.4
  - Overflow: 3 ticks × 1.0 × 12 / 30 = 1.2
  - Raw intake **3.6/turn at T1**.
- By tier damage factor (1.0 / 1.3 / 1.69 / 2.2): **3.6 / 4.7 / 6.1 / 7.9**. This is above 0 and inside the 2-4 target at T1. Block, SANDBOX or a Freeze can reduce it.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70.
Budget = `reference_dpt` × 3.5 turns × 1 needle − sustain (2 per tier, one Audit block):
- T1: 9 × 3.5 = 31.5 − 2 = 29.5 → **30**
- T2: 11 × 3.5 = 38.5 − 2 = 36.5 → **36**
- T3: 14 × 3.5 = 49 − 2 = 47 → **47**
- T4: 18 × 3.5 = 63 − 2 = 61 → **61**

`hp_by_tier` = [30, 36, 47, 61], all inside the bands. Today: 50 flat × a multiplier.

## 5. Enrage
Off (Normal, R4). The fight is 3-4 turns and Audit is capped at one block per turn.

## 6. Buffs and counter Exploits
Not applicable (normal).

## 7. Counterplay
- **Good player:** reads the wheel after the respin and accepts that it is fixed. Puts the free nudge and RAM into their own wheel for the best landing, and spends a SANDBOX or block when the pointer sits on the 3-tick Overflow. If they want to move its needle: Spin ≥3 (resistance 2 absorbs the first 2 ticks), Freeze to keep a safe wheel, Hub Breach, or Ghost's first nudge. They never pay for an enemy-wheel nudge, since the preview shows it absorbed.
- **Weak player:** pays RAM to nudge the enemy wheel (absorbed, plus Audit block), burns Flip and Respin cards into the lock, and doesn't use their own wheel's free nudge.

## 8. Systems needed
| System | Use | Fallback |
|---|---|---|
| N1 | FLAT amounts × tier damage factor | Data-only (amounts are flat today) |
| N2 | `hp_by_tier` | Single `hp` with a multiplier |
| N6 | Audit listener (paid enemy-wheel nudge) | Drop Audit; slices and resistance only (the fight is still valid) |
| N12 | Slice sizes 3, 4, 6, 7 | 5-tick slices: loses the narrow Overflow window |

## 9. Delta vs today
- **Kept:** id, corporation, Compliance Lock hub, Shim / Overflow / Null composition, `cycle_reward`.
- **Changed:** Defrag becomes a fourth Shim (single sustain source); slices resized (N12) with Null split in two; resistance 3 → 2; Audit listener added; HP 50 flat → [30, 36, 47, 61].
- **heat_effects:** keep the Heat 50+ RAM drain on attacks as it is. It taxes RAM on hits, not nudges, so it doesn't overlap with Audit.

## 10. Predicted sim check
Baseline: T1 3.0 turns (100 %), T2 5.1, T3 7.9 (95 %), T4 12.6 (70 %).
- **Predicted:** T1 3.2 turns, 100 %; T2 3.5, 100 %; T3 3.8, ≥ 92 %; T4 4.0, ~85 %.
- **Why:** HP follows the 3.5-turn budget instead of a multiplier on 50, which removes the T3-T4 tail. Resistance 2 loosens the wall, but intake is now unavoidable by nudging (3.6 → 7.9/turn), so T4 loses some wins to the hits. That is intended pressure at L5-6.

## 11. Open questions
Q: Audit only punishes a futile move that the preview already marks ABSORBED. Is that tripwire worth a listener, or should the fight run data-only?
Q: With resistance 2, does a Spin ≥3 card still feel worth playing, or should resistance be 1?
Q: Two separate Null slices (6 and 5) read as one 11-tick safe zone. Do we want that much free time per wheel?
Q: Is 3.6 intake/turn at T1 right for a teaching fight, with no way to move the enemy needle?
Q: If N6 slips, is the data-only fight acceptable as shipped?
