<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__utility_meter; status ok; tokens in 7509 cache-write 0 cache-read 32585 out 7331; cost $0.047. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, two layouts) -> fixed.** The BLOCK layout and the "Decision / Fix" prose are deleted. One layout stands, using the SANDBOX slice type (the enemy shield, R13), and its ticks are re-added: 6+4+5+5+4+6 = 30.
- **Issue 2 (BLOCKER, sustain arithmetic) -> fixed.** Sustain is now 5/30 × 5 % × tier HP per turn, shown per tier in §3 and §4. The budget is recomputed from that formula: **30 / 37 / 48 / 61**, not 30 / 38 / 48 / 60. The 2.5-HP error is gone, and the heal is PERCENT of max HP rounded down, never up.
- **Issue 3 (MAJOR, intake) -> fixed.**
  - Intake now includes slice-quality multipliers and a stated average bonus of +2, because the bonus needs shield from an earlier turn.
  - The bonus is derived, so it is not tier-scaled again. T1 to T4 are all shown.
  - The numbers are lower than v1's.
- **Issue 4 (MAJOR, enemy shield and cap) -> fixed.** The Reserve is FLAT × tier factor, rounded down (6 / 7 / 10 / 13), under the existing `shield_cap` 15. The rider max +6 is a fixed derived cap and is not tier-aware. Whether enemy shields need their own cap stays open as a Q (CONTENT_DESIGN_V2 §7 question 9).
- **Issue 5 (MAJOR, N# tags) -> fixed.** The rider is tagged "NEW: owner-shield damage rider (N20 family)". N14 is marked naming only. The N12 fallback is rewritten as all slices 5 ticks, with the Surcharge gaining a Perfect.
- **Issue 6 (MAJOR, thin question) -> partly kept.**
  - Kept, because the critic's table keeps the layout: the Surcharge covers 13 % of the wheel.
  - Changed: shield persists across turns, so the bonus is live from turn 2. The question is now a per-turn decision: spend damage to burn shield, or steer. Reserve (6) and Surcharge (4) are adjacent, so a shield landing sits one slice from the threat it feeds.
  - Raised the bonus rider max from +6 to +7? **No**, kept +6 to limit scope.
- **Issue 7 (NIT, counterplay wording) -> fixed.** SANDBOX is the player's wheel slice, not a card. Reserve is a slice the Meter lands, not a target. The weak-player lines are rewritten.
- **Issue 8 (NIT, sim guess and citation) -> fixed.** Win rates are flagged as hand estimates. The citation is now "CONTENT_DESIGN_V2 §7 question 9".
- **Critic Q on resolve order -> answered.** The rider reads shield at resolve. With one needle only one slice resolves per turn, so a Reserve landing never feeds a same-turn Surcharge.

# utility_meter: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. Halcyon.
- **Layers:** L1-2 teaching (T1-T2) and L5-6 pressure (T3-T4). It teaches "read a number the enemy feeds itself".
- **Concept:** a billing meter that banks credit (shield) and bills it back. Resistance 1 makes cheap steering feel expensive.
- **The one question:** *"Is the Meter's banked shield about to be billed to me, or do I burn it first?"*
  - The Surcharge adds 50 % of the Meter's own shield (max +6). Shield lingers across turns, so the threat grows turn over turn and is live from turn 2.
  - Each turn is a choice: spend damage on shield, steer the needle off the Surcharge, or negate it with a SANDBOX slice.
- **Shortens the fight:** steer the needle onto Rebate, Null or a Reserve edge, and hit hard while shield is low. Your damage hits shield first, so burning it also removes the Surcharge bonus.
- **Distinct from siblings:** Parking Warden, Patrol Unit and Permit Office ask about citations, stops and queues. This one asks about a single self-fed damage number.

## 2. Phase plan
Single phase: no threshold, no parking, no floor (last phase).

| | Phase 1: Metered Service (100 → 0 %) |
|---|---|
| Needles | 1, tick 0, fixed |
| Resistance | passive 1, restores each player turn (kept from today). The first nudge tick on its wheel is absorbed. |
| Hub rule | none (passive resistance only) |
| Statuses / parasites / listeners | none |

**Layout (R11, sizes sum to 30):**

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Reserve (SANDBOX type = shield) | 6 | +6 shield | FLAT × tier factor, floor |
| 2 | Surcharge (SHIM) | 4 | 4 damage + 50 % of the Meter's current shield (rounded down, max +6) | FLAT × tier factor; the bonus is derived and not rescaled |
| 3 | Rebate (HOTFIX) | 5 | heal 5 % max HP | PERCENT, rounded down, min 1 |
| 4 | Null | 5 | nothing | n/a |
| 5 | Reserve (SANDBOX type) | 4 | +6 shield | FLAT × tier factor |
| 6 | Peak Rate (OVERFLOW) | 6 | 9 damage | FLAT × tier factor |

Check: 6+4+5+5+4+6 = 30.

- **Quality maps (R11 defaults):**
  - 4-tick Surcharge: W G G W, no Perfect, so the Surcharge is never boosted.
  - 6-tick slices: W W G G W W.
  - 5-tick slices: W G P G W.
- **Resolve order:** defensive pass first, then offensive (GDD 2.2). With one needle only one slice resolves, so the bonus reads shield carried from earlier turns.
- **Tier shield gain:** 6 / 7 / 10 / 13, under `shield_cap` 15.

## 3. Sustain and intake
- **Sustain:** one source, the Rebate. Heals 5 % of max HP, and the expected per turn is 5/30 × 5 % × HP.

| Tier | HP | Heal on landing (floor) | Expected per turn | 30 % of reference dpt (cap) |
|---|---|---|---|---|
| T1 | 30 | 1 | 0.25 | 2.7 |
| T2 | 37 | 1 | 0.31 | 3.3 |
| T3 | 48 | 2 | 0.40 | 4.2 |
| T4 | 61 | 3 | 0.51 | 5.4 |

  Worst case (one landing per turn) is 1-3 HP, still under the cap at every tier. Shield is defense, not sustain. The budget uses the unrounded expected value (0.25 / 0.31 / 0.40 / 0.51), a slight overstatement.
- **Intake per turn at the reference player (before defenses, random landing):**
  - Surcharge: 4/30 landing chance × 0.75 average quality × (4f + bonus). The average bonus is +2, because shield only exists after an earlier Reserve landing.
  - Peak Rate: 6/30 × 0.667 average quality × 9f.
  - Per-turn total = 0.1(4f+2) + 1.2f = 1.6f + 0.2.

| Tier | f | Intake per turn |
|---|---|---|
| T1 | 1.0 | 1.8 |
| T2 | 1.3 | 2.3 |
| T3 | 1.69 | 2.9 |
| T4 | 2.2 | 3.7 |

  Always above 0. It sits below an elite's first phase (about 2-4 and up), as a normal should. A single Peak Rate at T4 is 19.8 at full quality.

## 4. HP by tier
Budget = reference dpt × 3.5 turns × 1 needle − expected sustain per turn × 3.5.

| Tier | dpt | Raw (dpt × 3.5) | Sustain × 3.5 | Result | HP | R2 normal band |
|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 0.25 × 3.5 = 0.9 | 30.6 | **30** | 28-36 ✓ |
| T2 | 11 | 38.5 | 0.31 × 3.5 = 1.1 | 37.4 | **37** | 34-44 ✓ |
| T3 | 14 | 49.0 | 0.40 × 3.5 = 1.4 | 47.6 | **48** | 44-56 ✓ |
| T4 | 18 | 63.0 | 0.51 × 3.5 = 1.8 | 61.2 | **61** | 56-70 ✓ |

`hp_by_tier` = [30, 37, 48, 61]. Banked shield (up to 15) adds effective HP if ignored, which is the cost of not answering the question. Today's 56 HP at T3 drops to 48.

## 5. Enrage
None (R4: normals). The shield cap of 15 and the Surcharge bonus cap of +6 bound the stall.

## 6. Buffs and counter Exploits
Not applicable: normals have no buffs.

## 7. Counterplay
- **Good player:**
  - Watches the Meter's shield on the preview. When shield is 6 or more and the needle sits on the Surcharge, they nudge it off or land a SANDBOX slice to negate the whole hit.
  - Spends damage on shield when it is high, because it is both the Meter's defense and its Surcharge bonus.
  - Steers the needle toward Null and accepts a Rebate, a 1-3 HP heal.
  - Uses a spin card or a second nudge to move the Meter's wheel. The first absorbed tick makes a lone nudge useless.
- **Weak player:**
  - Spends the first nudge on the Meter's wheel and moves nothing.
  - Pours damage into a full shield every turn and never checks the Surcharge preview.
  - Takes a Surcharge with full shield bonus at T3-T4 when one SANDBOX slice would have negated it.

## 8. Systems needed
| Need | N# | Fallback |
|---|---|---|
| FLAT / PERCENT amounts, flat × tier damage factor | N1 | None; required by R2. |
| `hp_by_tier`, `enemy_damage_by_tier` | N2 | None; required. |
| Variable slice sizes (4, 5, 6) | N12 | All slices 5 ticks. The Surcharge gains a Perfect and the window is wider. Playable. |
| Surcharge shield-scaling rider | NEW: owner-shield damage rider (N20 family) | Surcharge is plain SHIM 8. The question reduces to "burn shield, avoid the hit". |
| Shield display names | N14 | Naming only. The SANDBOX slice type already behaves as shield. |

## 9. Delta vs today
- **Changed:**
  - HP 56 (T3) → [30, 37, 48, 61].
  - Wheel: five 5-tick slices plus one Null → uneven sizes 6 / 4 / 5 / 5 / 4 / 6.
  - Defrag block → shield.
  - Double Hotfix (two 6-flat heals) → a single 5 % Rebate.
  - Shim 10 → Surcharge (4 + shield rider) and a Peak Rate Overflow 9.
- **Kept:** id, corporation, passive resistance 1, `cycle_reward` 15, a Null slice, one fixed needle at tick 0.
- **Why:** the old Meter had two heals on six slices (the Triage Unit flaw) and asked nothing beyond "hit it".
- **heat_effects:** none on the current file; none added.

## 10. Predicted sim check
Hand estimate; there is no Halcyon baseline row.
- **Turns:** about 3.5 for the reference player, p90 about 5. An ignored shield adds about 1 turn.
- **Win %:** T1 ~98, T2 ~97, T3 ~94, T4 ~90. The intake is 1.8-3.7 per turn, about 6-13 HP over the fight at 3.5 turns.
- **Why:** low intake and a short clock rarely threaten a healthy operative. The toll is HP carried into later fights.
- **Baseline comparison:** the Dosage Dispenser failed at 0.05 damage per turn. This design's 1.8 at T1 passes the intake test.

## 11. Open questions
Q: Should the shield-reading rider be a general reusable modifier (for the Zoning Board, Riot Control) rather than one slice's rider?
Q: Does an enemy shield use the player's `shield_cap` 15, or its own cap (CONTENT_DESIGN_V2 §7 question 9)?
Q: Is a 13 % Surcharge window enough to carry the question, or should it be 5 ticks with a Perfect at T1-T2 only?
Q: Keep resistance 1 on a normal, or drop it so L1 does not teach nudge absorption?
