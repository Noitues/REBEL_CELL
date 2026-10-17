<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__recall_unit; status ok; tokens in 7940 cache-write 0 cache-read 32585 out 12117; cost $0.072. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, budget split and T4 intake):**
  - §4 now splits HP at the 0.5 floor, per tier: 64 → 32/32, 78 → 39/39, 98 → 49/49, 126 → 63/63. Each half is checked against the 3.5-turn budget.
  - §3 has a per-tier intake table, with the tier factor applied once to every flat amount.
  - The "tempered" wording is gone. T4 intake is higher, and the table says so.
  - Base flat amounts are cut (SHIM 9 → 7 in P1 and 6 in P2; OVERFLOW 15 → 12 and 11) so T4 P2 stays survivable. The critic's 8/13 caps were not strict enough once the Tag is counted.
- **Issue 2 (BLOCKER, uniform-pointer intake):**
  - Removed the "≈5.0 average" and the unsupported "steers to ≈3".
  - The respin is uniform, so the unsteered expectation is the tick-weighted mean. That is stated as an upper bound.
  - Steered intake is a bracket [0.5, 1.0] × raw, with 0.6 as the placeholder midpoint. Step-0 calibration sets it; no derivation is claimed.
  - The orbit is a fixed telegraphed shift applied after the respin, so the preview is the true tick.
  - I did not adopt the critic's "turns 1-3 hit Notice 9, 9, 9" schedule. The start-of-turn respin randomizes the wheel (GDD 2.2), so a start-tick schedule would break the turn flow.
- **Issue 3 (MAJOR, Lock-On):** dropped. P2 is ORBIT +3/turn (data only), and the transition now reads "orbit speeds from +2 to +3". The "orbit stops" identity is removed. P2 layout has a single 6-tick Null, interleaved.
- **Issue 4 (MAJOR, Tag staging):** the Tag is specified as an ON_PERFECT listener (N6). It is staged in the preview once the wheels settle and is recomputed or undone with the action. It is one hit appended to the unit's offensive pass. BLOCK, SHIELD and SANDBOX apply to it, and Pierce is not involved. "Pre-announced" is replaced by "forecast chip". The Q about Perfect nudge-cards is dropped: the Tag fires on slice landings only.
- **Issue 5 (MAJOR, distinctness and dominated cost):**
  - The Tag is no longer flat. It is 25 % of the damage the Perfect-landed slice dealt to the unit, with a floor of 2 FLAT × factor.
  - Big Perfects cost more and small ones almost nothing, so it is a reflect, not Clawback's flat 4.
  - It does not scale with tier (a percent of your output, per R2), which also answers the critic's Q1.
  - P2 asks a second question (when to spend the Perfect-hook turn), not just "pay or not".
- **Issue 6 (MAJOR, sustain and absorb wording):**
  - §3 states that sustain = 0, so the budget subtracts nothing.
  - P1 BLOCK and SHIELD are defense and are not in the formula. Their tempo cost is noted.
  - The Tag's absorb rules are written out in §2.
- **Issue 7 (NIT):**
  - L3-6 placement kept, because it matches the elite feed.
  - The heat_effects claim is flagged as unverified against the `.tres`, with a decision that holds either way.
  - The baseline T1/T2 numbers were not in the supplied baseline and are removed. Only T3 20.2 and T4 36 are quoted.
- **Issue 8 (NIT):** "defence" → "defense".
- **New change (my own finding):** P1 resistance 1 is dropped. It would absorb the 1-tick free nudge entirely and make steering impossible. This answers v1's Q4.
- **Kept, because strong:** the notice → retrieval story, the HP table values 64/78/98/126, the wide Null slice, the 4-tick slices (no Perfect), and retiring heat_effects.

# recall_unit: direct design

## 1. Identity & the one question
- **Class:** Elite, Solace, 2 phases, one threshold at 50 %. It appears at L3-6 of T1-T3 netruns (the elite feed), never L1-2.
- **Theme:** a recall is a notice, then a pursuit.
  - P1 is the Notice: a slow, telegraphed orbit.
  - P2 is the Retrieval: the orbit speeds up, all defense is dropped, and it reflects a share of your Perfects back at you.
- **P1 Notice asks:** "Can you read a moving needle and cash in while it sits on a soft slice?"
  - The orbit is a fixed +2 ticks shown on a trail, so a nudge you aimed is shifted by 2 and you must pre-compensate.
  - A player who reads the final tick before committing hits when the needle is on Null, Plating or Quarantine.
  - A player who doesn't walks into the 12 OVERFLOW.
- **P2 Retrieval asks:** "Is this Perfect worth what it reflects?"
  - The unit has no defense, so everything you land counts.
  - A Perfect on a big hit reflects 25 % of that damage back at you; a small Perfect costs almost nothing.
  - So the question is which turn to spend the Perfect hook (Breaker double-resolve, Ghost strip) and which to land Good.
- **Shorter fight:**
  - P1: pick the turn where the final tick is on a soft slice.
  - P2: take Perfects only on a slice whose output is high enough to end the phase sooner than the reflect costs.
- **Distinct from siblings:**
  - Claims Adjuster is burst.
  - Account Manager's Clawback is a flat hit on any Perfect, plus a RAM economy.
  - The Recall Unit's Tag is proportional to your own output, with no bodyguards or RAM.

## 2. Phase plan

### P1 "Notice" (100 → 50 % HP)
| Field | Value |
|---|---|
| Needles | 1, base tick 0, **ORBIT +2 ticks/turn**, applied after the start-of-turn respin; the trail shows next turn's tick if you don't move it |
| Resistance | **0** (v1's 1 would absorb the free 1-tick nudge and make steering impossible) |
| Hub rule | none |
| Statuses / parasites | none |
| Listeners | none |

Layout, clockwise (ticks sum 30):

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Notice (SHIM) | 5 | 7 dmg FLAT |
| 2 | Notice (SHIM) | 5 | 7 dmg FLAT |
| 3 | Plating (DEFRAG → BLOCK) | 5 | 7 BLOCK FLAT |
| 4 | Retrieval (OVERFLOW) | 4 | 12 dmg FLAT (W G G W: no Perfect) |
| 5 | Quarantine (SANDBOX → SHIELD) | 5 | 5 SHIELD FLAT |
| 6 | Null | 6 | none (W W G G W W) |

Sum: 5+5+5+4+5+6 = 30.

### Transition P1 → P2 (at ≤ 50 % HP)
- Damage parks at ceil(0.5 × max HP); the excess is lost (R3). The phase changes at the end of that resolve, and later hits in that resolve are also lost.
- `wheel_override` swaps the layout. The orbit speeds from **+2 to +3**. The Tag listener turns on.
- `cleanse_on_enter` = NONE, so statuses stay and are remapped by centre tick (R6).
- The phase line plays and the new layout is revealed.

### P2 "Retrieval" (50 → 0 %)
| Field | Value |
|---|---|
| Needles | 1, base tick 0, **ORBIT +3 ticks/turn** |
| Resistance | 0 |
| Hub rule | none |
| Statuses | none |
| Listener (N6) | **Recall Tag:** ON_PERFECT on a player slice landing. Deals max(25 % of the damage that slice dealt to the unit, 2 FLAT × tier factor) to you. The percent part is not rescaled (R2). It is staged in the preview as a "TAG −N" chip once the wheels settle, and is undone with the action. It is appended to the unit's offensive pass as one hit: BLOCK and SHIELD absorb it and SANDBOX negates it. It is not Pierce. |

Layout (ticks sum 30):

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Recall Order (SHIM) | 5 | 6 dmg FLAT |
| 2 | Recall Order (SHIM) | 5 | 6 dmg FLAT |
| 3 | Null | 6 | none |
| 4 | Recall Order (SHIM) | 4 | 6 dmg FLAT (no Perfect) |
| 5 | Final Notice (OVERFLOW) | 5 | 11 dmg FLAT |
| 6 | Recall Order (SHIM) | 5 | 6 dmg FLAT |

Sum: 5+5+6+4+5+5 = 30. The Null is interleaved, and with +3 per turn the needle crosses it about every 10 turns, so it is a hole you steer into, not a place the orbit parks.

## 3. Sustain and intake
- **Sustain: none.** The unit has no heal, so the R2 formula subtracts 0 (0 % of the 30 % cap).
- P1 BLOCK and SHIELD are defense, not sustain. They cover 10 of 30 ticks and a reference player avoids them. A landing on Plating costs about one turn's damage, which is why P1 may run ~4 turns.
- **Intake method:**
  - The respin is uniform each turn, so the unsteered expectation is the tick-weighted mean of enemy damage.
  - Steered intake falls between 0.5× and 1.0× of that. 0.6× is the placeholder midpoint, to be calibrated in step 0.
  - Every flat amount is multiplied by the tier factor [1.0, 1.3, 1.69, 2.2] exactly once.
- **Raw expectation:**
  - P1: (5·7 + 5·7 + 4·12)/30 = 118/30 = 3.93.
  - P2: Orders (5+5+4+5 = 19 ticks) × 6 = 114, plus Final 5 × 11 = 55, so 169/30 = 5.63.

| Tier | P1 unsteered | P1 steered (0.6×) | P2 unsteered | P2 steered | Tag per Perfect | P2 steered + 1 Perfect/turn |
|---|---|---|---|---|---|---|
| T1 (1.0) | 3.9 | 2.4 | 5.6 | 3.4 | ≈2.3 | 5.7 |
| T2 (1.3) | 5.1 | 3.1 | 7.3 | 4.4 | ≈2.8 | 7.2 |
| T3 (1.69) | 6.6 | 4.0 | 9.5 | 5.7 | ≈3.5 | 9.2 |
| T4 (2.2) | 8.7 | 5.2 | 12.4 | 7.4 | ≈4.5 | 11.9 |

- **Tag arithmetic:** 25 % of the reference damage of a Perfect turn (9, 11, 14, 18 per turn) gives 2.3, 2.8, 3.5 and 4.5. The 2 FLAT × factor floor (2.0, 2.6, 3.4, 4.4) is about equal at the reference.
- **Survivability:** over 3.5 turns, a greedy T4 P2 costs ≈ 42 HP, and a Good-only P2 ≈ 26 HP. Both are above 0 and below an operative's carried HP at T4 rank.

## 4. HP by tier
R2 band (elite, 2 phases): T1 56-72, T2 68-88, T3 88-112, T4 112-144. Per-phase budget = `reference_dpt` × 3.5 turns × 1 needle − sustain (0). The floor sits at ceil(0.5 × HP).

| Tier | dpt | Per-phase budget | Sum | `hp_by_tier` | P1 band (HP − floor) | P2 band (floor) |
|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 63 | **64** | 32 | 32 |
| T2 | 11 | 38.5 | 77 | **78** | 39 | 39 |
| T3 | 14 | 49 | 98 | **98** | 49 | 49 |
| T4 | 18 | 63 | 126 | **126** | 63 | 63 |

All values are inside the band. Each half is within 0.5 of its budget, which is the ceiling rounding.

## 5. Enrage
Elite default: start turn 8, every 5 turns, +25 % additive. It raises slice damage and the Tag's 2-FLAT floor, not the percent part. At a 6-8 turn target the first step is a safety net only.

## 6. Buffs and counter Exploits
Not a boss. Not applicable.

## 7. Counterplay
- **P1:**
  - Read the final tick, since the orbit shifts the landing by +2, and plan the nudge after the shift.
  - With resistance 0 the free nudge works. Push the needle off the 4-tick Retrieval onto Null or Plating, or hit hard on a turn it sits on Null.
  - Don't chip the Plating: its BLOCK is small and expires.
- **P2:**
  - There is no defense, so every Good landing counts in full.
  - Land Perfects only when the slice is big enough to end the phase sooner than the Tag costs (a double-resolve hook on a high-damage slice is worth about 25 % reflect).
  - Hold SHIELD or SANDBOX on a Perfect turn, because the Tag is absorbed by SHIELD and negated by SANDBOX.
  - Steer the needle into the 6-tick Null before it reaches the Final Notice.
- **Weak play:** chasing Perfects on small slices and bleeding the Tag for nothing; ignoring the +2/+3 shift in nudge planning; spending turns on the Plating.

## 8. Systems needed
| System | Use | Fallback |
|---|---|---|
| N1, N2 | tier factors, `hp_by_tier` | required (R2) |
| N3 | one threshold, parking, status keep | required |
| N4 | Enrage | required |
| N11 | not used (needle at tick 0) | n/a |
| N12 | 4- and 6-tick slices | 5-tick slices only: Retrieval and the 4-tick Order gain a Perfect; the idea weakens but still works |
| N6 | ON_PERFECT listener (the Tag) | drop it and give P2 a plain hub rule "damage +25 %"; this loses the Perfect question |
| N14 | BLOCK / SHIELD names | cosmetic |
| ORBIT behavior (GDD 2.11) | +2 and +3 per turn | exists today; the P2 speed-up is data only |

No new "Lock-On" system.

## 9. Delta vs today
- **Kept:** the orbit, the slice set (Shim, Defrag, Overflow, Sandbox, Null), `cycle_reward` 35, the elite flag.
- **Changed:**
  - HP 106 → 64/78/98/126.
  - Flat amounts rebased (SHIM 9 → 7 and 6, OVERFLOW 15 → 12 and 11).
  - Resistance 1 → 0.
  - A P2 layout with no defense, an orbit speed-up, and the Tag.
  - Slice sizes 4 and 6.
- **New:** one threshold at 0.5 with parking.
- **heat_effects:** I could not verify the current file's `heat_effects` here. Decision: **retire any that exist and add none.** The Tag and the threshold carry the identity, and an elite node already adds +1 Heat.

## 10. Predicted sim check
| Tier | Turns (mean) | Win % | Baseline |
|---|---|---|---|
| T1 | 6-7 | ≥95 | not in the supplied baseline |
| T2 | 6-8 | ≥95 | not in the supplied baseline |
| T3 | 7-8 | ≥90 | 20.2 turns |
| T4 | 7-9 | ~70-80 | 36 turns |

- **Why:** HP is tuned to reference damage instead of a tier multiplier, so the long T3/T4 fights collapse to the class target. T4 win rate drops from threat, not from length.
- Check P1 and P2 each take 3-4 turns, using N19.

## 11. Q:
- Q: Is 0.6× the right placeholder for how much a reference player steers intake down? Step-0 calibration should replace it.
- Q: Should the Tag's percent be 25 %, or tuned per tier so T4 greedy play (~42 HP over a phase) is less punishing?
- Q: Does a double-resolve Perfect hook (Breaker) count its second resolve in the Tag's "damage dealt", or only the first?
- Q: With resistance gone in P1, is the orbit alone enough to keep P1 from being a pure Null-parking exercise?
- Q: Should heat_effects be kept on any elite, or retired class-wide?
