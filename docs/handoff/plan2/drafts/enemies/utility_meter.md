<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__utility_meter; status ok; tokens in 15362 cache-write 0 cache-read 32007 out 4068; cost $0.039. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# utility_meter: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. Halcyon.
- **Layers:** L1-2 teaching (T1-T2) and L5-6 at T3-T4. It is Halcyon's "reading the meter" lesson.
- **Concept:** a billing meter that only runs while the street is fed. It has three readings, bills by the meter, and its Resistance 1 makes cheap steering feel expensive.
- **The one question:** *"Which of my turns is the meter reading?"* It has a **Peak Rate** window. Its Shim (the Surcharge) scales with how much block it holds, so the question is whether you strip the block before the Surcharge lands, or steer the pointer off the Surcharge.
- **Shortens the fight:** landing the pointer on Defrag only buys the Meter more bill. Steer it onto the Hotfix or Null edges and hit hard while the block is low. The Meter has just one wheel-based sustain source, and it is a Hotfix with a cap.
- **Distinct from siblings:** the Parking Warden, Patrol Unit and Permit Office each ask about citations, stops and queues. This one asks about a single self-fed damage number (Surcharge = its own block).

## 2. Phase plan
Single phase, no threshold, no parking (last phase has no floor).

| | Phase 1: Metered Service (100 → 0 %) |
|---|---|
| Needles | 1, tick 0 (fixed) |
| Resistance | passive 1, restores each player turn (kept from today). Costs the first nudge tick. |
| Hub rule | none (keeps the passive resistance only) |
| Statuses / parasites / listeners | none |

**Layout (sizes sum to 30, R11, uneven sizes):**

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Reserve (BLOCK) | 6 | Gain block 8 | FLAT (× tier factor) |
| 2 | Surcharge (SHIM) | 4 | Deal 4 damage + 50 % of the Meter's current BLOCK (rounded down, max 8 bonus) | FLAT 4, bonus is a rider |
| 3 | Rebate (HOTFIX) | 5 | Heal 5 % max HP | PERCENT |
| 4 | Null | 5 | nothing | n/a |
| 5 | Reserve (BLOCK) | 4 | Gain block 8 | FLAT |
| 6 | Peak Rate (OVERFLOW) | 6 | Deal 9 damage | FLAT |

- The 4-tick Surcharge has no Perfect (W G G W), so the Meter's damage is never Perfect-boosted. It is hardest to land correctly *on the slice*, not harder to hit.
- The Surcharge bonus uses the existing block value on the Meter at resolve time. Block resolves in the defensive pass before offensive slices (GDD 2.2), so a Reserve landing *and* a Surcharge cannot occur with one needle. The bonus matters for block carried from the previous turn only if block persisted. Block expires at the start of the owner's next turn, so the bonus is only live when something *else* granted block that turn. **Decision:** make the Surcharge read the Meter's *current block at resolve*, and give Reserve 4 ticks of a sibling "Shield" slice instead: see below.

Fix to keep it consistent with the rules: the Meter's Reserve uses **SHIELD** (lingers, R13), not BLOCK, so it accumulates across turns, capped at `shield_cap` 15. The Surcharge then reads the Meter's current SHIELD.

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Reserve (SHIELD) | 6 | +6 shield, FLAT × tier factor |
| 2 | Surcharge (SHIM) | 4 | 4 damage + ½ of the Meter's current shield (rider), max +6 |
| 3 | Rebate (HOTFIX) | 5 | heal 5 % max HP, PERCENT |
| 4 | Null | 5 | nothing |
| 5 | Reserve (SHIELD) | 4 | +6 shield, FLAT |
| 6 | Peak Rate (OVERFLOW) | 6 | 9 damage |

The shield-reading rider is a slice rider (N20 family, `damage_per_owner_shield`). Data-only fallback below.

## 3. Sustain and intake
- **Sustain:** one source, the Rebate. 5 % of max HP per landing. At T3 (HP 50) that is 2.5, rounded to 3 HP when it lands. Chance per turn: Rebate covers 5 of 30 ticks, so expected ~0.83 HP per turn, worst case 3 HP per turn. The reference damage at T3 is 14 per turn, so the cap is 30 % × 14 = 4.2. Worst case 3 HP is 21 %. Inside the cap. Shield gain is a defense, not sustain.
- **Intake per turn at the reference player** (random pointer; each of the 30 ticks equally likely, the reference player nudges away from the worst slice about half the time, so I count a random landing):
  - Surcharge: 4 ticks of 30 × (4 + bonus ~3) × tier factor.
  - Peak Rate: 6 ticks of 30 × 9.
  - T1 expected: (4/30 × 7) + (6/30 × 9) = 0.93 + 1.8 = **~2.7 per turn**, ~9-10 HP over a 3.5-turn fight.
  - T3 (×1.69): ~**4.6 per turn**.
  - Always above 0, and below the 5-8 band of an elite's first phase, as befits a normal.
- Estimate only: there is no baseline row for Halcyon.

## 4. HP by tier
Budget = reference dpt × 3.5 turns × needles (1) − sustain per turn × 3.5.
Sustain per turn ≈ 0.83 expected (×tier).

| Tier | dpt | Raw budget | Sustain | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | −2.9 | **30** |
| T2 | 11 | 38.5 | −2.9 | **38** |
| T3 | 14 | 49 | −2.9 | **48** |
| T4 | 18 | 63 | −2.9 | **60** |

All are inside the R2 normal bands (28-36 / 34-44 / 44-56 / 56-70). Today's 56 HP is T3 at the top of the band, so I move it to 48 and let the shield absorb the rest. The shield cap of 15 adds up to ~15 effective HP if the player lets it stack, which is the point of the question. `hp_by_tier` = [30, 38, 48, 60].

## 5. Enrage
None: normals have no enrage (R4). A 3-4 turn fight does not need one. The shield cap of 15 is the stall guard, and Surcharge reads at most +6.

## 6. Buffs and counter Exploits
Not applicable: normals have no buffs.

## 7. Counterplay
- **Good player:**
  - Reads the Surcharge slice in the preview. If shield is 6+ and the needle sits on the Surcharge (4 ticks, no Perfect), nudge one tick off it or play a SANDBOX to negate the whole hit.
  - Hits Reserve with a burst *before* the pointer returns: shield is the thing to break, and shield absorbs your damage first (R13).
  - Steers the pointer toward Null, accepting Rebate (a 3 HP heal) since it is a small, bounded cost.
  - Uses the first nudge for resistance 1: the first tick is absorbed, so a nudge of 2 ticks moves it 1. A spin card ignores that cost for free, because only the first R ticks are absorbed.
- **Weak player:**
  - Spends damage into the shield every turn and never lets the Meter reach Null.
  - Lands Reserve for the Meter by nudging "towards Null" by 1 tick when resistance absorbs it.
  - Ignores the Surcharge preview and takes 10 with a full shield.

## 8. Systems needed
| Need | N# | Fallback |
|---|---|---|
| FLAT/PERCENT amounts, flat × tier damage factor (shield, damage), percent heal | N1 | None; required by R2. It is cheap. |
| `hp_by_tier`, `enemy_damage_by_tier` | N2 | None; required. |
| Variable slice sizes (4, 5, 6) | N12 | Fallback: all slices 5 ticks. The Surcharge then has a Perfect and the design shifts: the Surcharge's Perfect window means a 1-tick nudge matters less. Playable, weaker. |
| Shield-scaling Surcharge rider (`damage_per_owner_shield`) | N20 (new rider) | Fallback: Surcharge is plain SHIM 8; the question reduces to "avoid the Surcharge and break the shield". |
| SHIELD / defense trio naming | N14 | Use existing SANDBOX slice type (data only; it already is a shield). |

## 9. Delta vs today
- **Changed:** HP 56 → [30, 38, 48, 60]; wheel from Defrag 8 / Hotfix 6 / Shim 10 / Hotfix 6 / Defrag 8 / Null (all 5 ticks) to uneven sizes; Defrag (block) → shield; the double Hotfix (two 6-flat heals, ~2 HP/turn heal at 4 of 6 slices... expected 2 per turn) → a single 5 % Rebate; Shim 10 → Surcharge 4 + shield rider and a Peak Rate Overflow 9.
- **Kept:** id, corporation, passive resistance 1, `cycle_reward` 15, a Null slice, the single fixed needle at 0.
- **Why:** the old Meter had 2 heals out of 6 slices, a sustain flaw (the Triage Unit pattern), and no question beyond "hit it".
- **heat_effects:** none on the current file; add none.

## 10. Predicted sim check
Estimate by hand; no baseline row for Halcyon.
- **Turns:** ~3.5 at the reference player; p90 ~5. The shield stacks to 15 if ignored, which adds ~1 turn. Inside the 3-4 target, with a tail.
- **Win %:** T1 ~98 % (intake ~10 of 60+ HP), T2 ~97 %, T3 ~94 %, T4 ~90 %. At T4 it takes ~4.6 × 1.3 per turn, ~16-20 total, a real cost but not lethal.
- **Why:** low intake and a 3-turn clock mean the fight rarely threatens a healthy operative. Its toll is HP carried into later fights.
- **Compared to the baseline:** none for Halcyon. The only Solace comparison is the Dosage Dispenser failure at 0.05 damage per turn, which this design avoids at ~2.7.

## 11. Open questions
Q: Should the Surcharge's shield rider be a new slice rider (N20), or should "scales with own shield" be a general effect modifier reusable by the Zoning Board and Riot Control?
Q: Does the Meter's shield cap equal the player's `shield_cap` 15, or does an enemy percent shield need its own cap (R-question 9)?
Q: Is a 4-tick no-Perfect Surcharge the right teaching of R11 at T1, or should the first tier show a 5-tick slice and only unlock the uneven map at T2?
Q: Resistance 1 on a normal with a single needle: keep it as a flavor tax, or drop it to keep L1 free of the nudge-absorption lesson?
