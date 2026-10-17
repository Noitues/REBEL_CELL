<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__port_authority; status ok; tokens in 6476 cache-write 0 cache-read 32585 out 8166; cost $0.051. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (sustain skipped in §4)** → fixed. I recomputed Hold's sustain from its actual sub-tick map (W W G G W W, mean 0.667, not 0.8). P1 is now 3.5 × (ref dpt − sustain). `hp_by_tier` is now [61, 74, 93, 120], with the arithmetic shown per tier in §4. I do not use the critic's 0.47 threshold. The floor is the HP remaining when P2 starts, which is P2's share (~52 %), not 1 minus P1's share. The threshold is **0.52**.
- **Issue 2 (intake unshown / Hold sourcing)** → fixed. §3 shows the working from the sub-tick maps. Corrected values: P1 raw damage 2.6 at T1 (not 2.8 or the critic's 3.1), P2 2.9 (not 3.3). v1's claim that P2 adds RAM drain was wrong: P1 drains 1.0 RAM/turn and P2 only 0.4. Hold is sourced as block that only counts when the pointer reads it.
- **Issue 3 (turn check)** → added to §4, §5 and §10: expected P2 start about turn 4 and end about turn 7; enrage turn 8 is reached only on slow play.
- **Issue 4 (TIER_DOWN uncapped)** → added a cap: **TIER_DOWN ×2 per slice.** A Demurrage landing on a slice already at ×2 deals its 2 damage and adds nothing. §7 and §10 are updated.
- **Issue 5** → skipped, as the critic said. The RAM drain bypasses nothing, and the R3 floor applies on every loss path.
- **Issue 6 (fallback changes the question)** → §8 now says plainly that the PARASITE fallback turns "keep your Perfects" into "keep your output" and is stopgap only.
- **Issue 7 (Ruling 11)** → Q rewritten to cite CONTENT_DESIGN_V2 §7 open question 11.
- **Issue 8 (heat_effects)** → decision kept (author none). The unverified claim is flagged as "verify against the .tres", and the false R2 citation is replaced with GDD 4.3.
- **Kept, because the critic marked them strong:** the question flip (P1 taxes steering, P2 frees steering but taxes tier), the honest no-Perfect maps on the 6- and 4-tick slices, the single needle, and the N8/N9/N12 fallbacks.

# port_authority: direct design

## 1. Identity & the one question
- **Class and corporation:** Elite, Meridian. It appears at L3–L6, so it is L5–6 pressure with a teachable P1.
- **Fantasy:** a customs checkpoint. First it inspects: a Weight wall and a toll on your RAM. Then it impounds: the wall opens, but it taxes the quality of your landings.
- **P1 Inspection asks:** "Is steering worth the toll?" Resistance 2 makes nudges expensive, and Priority drains about 1 RAM per turn. The answer that shortens the fight is to skip nudging. Use spin cards (they lose only the first 2 ticks to resistance) and push damage.
- **P2 Impound asks:** "Can you keep your Perfects?" Steering is free again, but Demurrage stacks TIER_DOWN on your slices (cap ×2). The answer that shortens the fight is to burst early in P2 and keep the damage slice clean (steer Demurrage off it, or Cleanse or Encrypt it).
- **Distinct from the rest of Meridian:** Conveyor Warden and Drone Dispatcher own orbit and drones, and the Logistics Director owns the parasite ring and the respin lock. This elite is the only one that combines Weight with a tier tax.

## 2. Phase plan
Flat amounts are T1 base values and get × `enemy_damage_by_tier` [1.0, 1.3, 1.69, 2.2] (R2). RAM drain is not scaled.

**P1 Inspection (100 → 52 %)**

| Field | Value |
|---|---|
| Needles | 1, fixed at tick 0 |
| Hub | Customs Wall: resistance 2, restored each turn (existing) |
| Statuses, listeners | none |

| Slice | Ticks | Effect | Sub-tick map |
|---|---|---|---|
| Hold | 6 | BLOCK 6 FLAT | W W G G W W (no Perfect) |
| Shim | 5 | 6 damage | W G P G W |
| Priority | 5 | drain 3 RAM | W G P G W |
| Shim | 5 | 6 damage | W G P G W |
| Tariff (Overflow) | 4 | 10 damage | W G G W (no Perfect) |
| Priority | 5 | drain 3 RAM | W G P G W |

Sizes: 6+5+5+5+4+5 = 30 ✓.

**P2 Impound (52 → 0 %)**

| Field | Value |
|---|---|
| Needles | 1, fixed at tick 0 |
| Hub | Wall Down: resistance 0 (`hub_override`) |
| Statuses | Demurrage applies TIER_DOWN ×1 to the player slice under the pointer. **Cap ×2 per slice.** At the cap it deals its 2 damage only. |
| Listeners | none |

| Slice | Ticks | Effect | Sub-tick map |
|---|---|---|---|
| Shim | 6 | 6 damage | W W G G W W |
| Demurrage | 5 | 2 damage + TIER_DOWN ×1 | W G P G W |
| Tariff (Overflow) | 5 | 12 damage | W G P G W |
| Priority | 4 | drain 3 RAM | W G G W |
| Demurrage | 5 | 2 damage + TIER_DOWN ×1 | W G P G W |
| Null | 5 | nothing | W G P G W |

Sizes: 6+5+5+4+5+5 = 30 ✓. There is no Hold, so the burst window opens.

**Transition P1 → P2:**
- `wheel_override` plus `hub_override` (resistance 2 → 0).
- R3: damage parks at the floor, ceil(max × 0.52), on every loss path. The excess is lost.
- R6: statuses are kept. P1 applies none, so `cleanse_on_enter` = NONE.
- The phase line plays and the P2 layout is revealed.

## 3. Sustain and intake
**Sustain: one source, Hold.** It counts only when the pointer reads Hold, so the expected value is (6/30) × 6 × tier factor × the map mean 0.667.

| Tier | Sustain per turn | % of ref dpt (cap 30 %) |
|---|---|---|
| T1 | 0.8 | 8.9 |
| T2 | 1.04 | 9.5 |
| T3 | 1.35 | 9.6 |
| T4 | 1.76 | 9.8 |

P2 has no sustain.

**Intake** is raw expected damage per turn at the reference player, before the player's block. The pointer lands uniformly with no steering, and each slice is weighted by ticks × amount × its sub-tick map mean.
- **P1 working:**
  - Shim: 5 × 6 × 0.8 = 24 (×2 slices).
  - Tariff: 4 × 10 × 0.75 = 30.
  - Sum = 78, over 30 ticks = **2.6** at T1.
  - RAM: 10/30 × 3 = 1.0 per turn.
- **P2 working:**
  - Shim: 6 × 6 × 0.667 = 24.
  - Demurrage: 5 × 2 × 0.8 = 8 (×2 slices).
  - Tariff: 5 × 12 × 0.8 = 48.
  - Sum = 88, over 30 ticks = **2.9** at T1.
  - RAM: 4/30 × 3 = 0.4 per turn.

| Tier | P1 | P2 |
|---|---|---|
| T1 | 2.6 | 2.9 |
| T2 | 3.4 | 3.8 |
| T3 | 4.4 | 5.0 |
| T4 | 5.7 | 6.5 |

Intake is above 0. The real pressure is the RAM toll in P1 and stacking TIER_DOWN in P2.

## 4. HP by tier
Phase budget = `reference_dpt` × 3.5 − sustain × 3.5, with 1 needle per phase.

| Tier | P1 budget | P2 budget | Total | Elite band | In band |
|---|---|---|---|---|---|
| T1 (ref 9) | 31.5 − 2.8 = 28.7 → 29 | 31.5 → 32 | **61** | 56–72 | yes |
| T2 (ref 11) | 38.5 − 3.6 = 34.9 → 35 | 38.5 → 39 | **74** | 68–88 | yes |
| T3 (ref 14) | 49 − 4.7 = 44.3 → 44 | 49 | **93** | 88–112 | yes |
| T4 (ref 18) | 63 − 6.2 = 56.8 → 57 | 63 | **120** | 112–144 | yes |

- **`hp_by_tier`:** [61, 74, 93, 120].
- **Threshold 0.52.** Floors are ceil(max × 0.52): 32 / 39 / 49 / 63. These equal the P2 budgets, so P2 starts with its full budget at every tier.
- **Turn check:** P1 ≈ 3.5 turns, so P2 starts about turn 4. P2 ≈ 3.5 turns, so the fight ends about turn 7, inside the 6–8 target.
- Today's 144 HP exceeds the T3 band.

## 5. Enrage
**Default** (start turn 8, every 5 turns, +25 % damage). The fight ends around turn 7, so the first step arrives only if P2 starts after turn 4 or the player stalls. The pressure design is Demurrage stacking (capped), so enrage is only a backstop. Nothing authored.

## 6. Buffs and counter Exploits
n/a (elite).

## 7. Counterplay
**P1**
- **Good player:**
  - Plays spin cards, not nudges. A 5-tick spin loses only 2 ticks.
  - Uses the free nudge only to push Tariff or Priority off the pointer.
  - Keeps RAM above the 3-per-landing drain.
  - Banks burst into P1's short HP.
- **Weak player:**
  - Burns RAM nudging against resistance 2, then eats Priority drains and enters P2 with nothing left.
  - Tries Flip or Respin (blocked by the wall) and loses the card.

**P2**
- **Good player:**
  - Opens P2 with burst while tiers are clean.
  - Steers Demurrage off the damage slice (nudges are free of resistance now) or Cleanses or Encrypts it.
  - Remembers that ×2 turns a Perfect into WEAK. It is better to let a utility slice take the stacks.
- **Weak player:** lets Demurrage land on their best slice until it is capped at ×2, which leaves it WEAK-only. The fight then stalls toward the turn-8 enrage.

## 8. Systems needed
- **N2** (`hp_by_tier`, damage factor).
- **N3** (an elite phase with parking).
- **N4** (enrage).
- **N8 + N9** for TIER_DOWN and the ×2 cap. **Fallback:** the existing PARASITE status (halves output). This changes the question from "keep your Perfects" to "keep your output", so it is a stopgap only.
- **N12** for variable sizes and sub-tick maps. **Fallback:** six 5-tick slices (Hold, Shim, Priority, Shim, Tariff, Priority; P2 swaps Hold and Priority for Demurrage and Null). It loses the no-Perfect edges on Hold and Tariff. Not recommended.
- **N19** for sim metrics.
- No N5, N6, N7 or N10.

## 9. Delta vs today
- **Kept:** the id; the Meridian theme (Priority, Overflow as the big hit); resistance 2 as the wall; `cycle_reward = 35`.
- **Changed:**
  - 144 HP becomes [61, 74, 93, 120].
  - Two needles (0/15) become one needle.
  - A second phase (Impound) is added, with Demurrage and the wall at 0.
  - Amounts are tier-scaled from base values.
- **`heat_effects`:** author none. Heat modifiers come from the Grid thresholds (GDD 4.3). Verify against the current `.tres`; if it holds any, retire them.

## 10. Predicted sim check
Estimated from the wheel; no baseline row exists.
- **Turns:** about 6.5–7.5 (phases of 3.5 ± 0.5), p90 ≤ 9. Enrage step 1 (turn 8) appears only in slow runs.

| Tier | Win % | Why |
|---|---|---|
| T1–T2 | ≥ 95 | Intake is under 4 per turn. |
| T3 | ≈ 90 | The ×2 cap bounds the tier tax, so Demurrage costs about 1 turn if ignored. |
| T4 | ≈ 88–92 | Intake of 5.7–6.5 is mild, but a RAM-starved weak player can stall. |

- **Compared with today:** 144 HP with 2 needles ran roughly twice as long (≈ 12 turns, my estimate).

## 11. Open questions
Q: Should Hold's block count against the 30 % sustain cap, or does the cap apply only to heals?
Q: Is a TIER_DOWN cap of ×2 the right ceiling at T4, where a Perfect already drops to WEAK?
Q: Should Priority drain RAM only on Good-or-better, so a weak landing is a real escape?
Q: Does `reference_dpt` assume nudging against resistance 2? I assumed it does not.
Q: Do statuses still apply on a WEAK landing (CONTENT_DESIGN_V2 §7 question 11)? I assumed yes, so Demurrage always stacks.
