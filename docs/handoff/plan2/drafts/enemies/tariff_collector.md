<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__tariff_collector; status ok; tokens in 16629 cache-write 0 cache-read 32007 out 3362; cost $0.037. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# tariff_collector: direct design

## 1. Identity & the one question
- **Class:** Normal, Meridian, 1 phase, 3-4 turns, no enrage.
- **Layers:** L3-6 pressure. Not a teaching enemy. It is the first fight that taxes RAM, so it comes after L1-2, where RAM is still a free resource. L1-2 is for Cargo Hauler and the other basics.
- **The one question: "What is your RAM worth this turn?"** Every landed hit drains RAM, so the player chooses between paying RAM to dodge or steer, or taking the drain and keeping the plan.
- **Distinct from the rest of Meridian:**
  - Conveyor Warden and Route Optimizer own orbit and WEIGHT.
  - Customs Scanner and Drone Dispatcher own intel and drones.
  - The Collector is the only normal whose damage is mostly a RAM toll.
- **What shortens the fight:** keep one Perfect nudge (1 RAM) in reserve, and spend the free nudge to push the single needle off the Toll slices onto Null or Ledger. Burst its HP before the Overflow lines up.

## 2. Phase plan (single phase, no threshold, no floor)

Needles: 1, fixed at tick 0 (no uneven needles needed). Wheel is 6 slices summing to 30, using R11 sizes.

| # | Slice | Ticks | Tick map | Effect (placeholder numbers, at T1 base) |
|---|---|---|---|---|
| 0 | Toll | 5 | W G P G W | SHIM 6 damage FLAT, drain 1 RAM FLAT |
| 1 | Ledger | 6 | W W G G W W | DEFRAG 6 BLOCK FLAT (no Perfect; hard to optimize) |
| 2 | Surcharge | 4 | W G G W | OVERFLOW 10 FLAT, drain 3 RAM FLAT (no Perfect, so there is no tight window to deny) |
| 3 | Toll | 5 | W G P G W | as slice 0 |
| 4 | Late Fee | 4 | W G G W | INFECT: drain 2 RAM, OUTPUT_DOWN x1 on the slice under your pointer (R8 status, applied on any landing) |
| 5 | Null | 6 | W W G G W W | nothing |

Sum: 5+6+4+5+4+6 = 30.

- **Hub rule:** none (no heal, no resistance). The question stays pure.
- **Statuses used:** OUTPUT_DOWN x1 (N8, N9). Today's slices only drain.
- **Listeners:** none.
- **Transition:** none, single phase.
- **Why this layout:** its wheel today is Shim, Shim, Defrag, Priority, Overflow, Null, all 5-tick. Here the dangerous slices (Surcharge, Late Fee) are 4-tick with no Perfect. Nudging a pointer off them by a tick or two matters because the slice is narrow, not because of a Perfect. Both Tolls are 5-tick with a Perfect.

## 3. Sustain and intake

- **Sustain:** one source, Ledger BLOCK 6 FLAT, a defensive slice that appears once per revolution. Reference damage at T1 is 9 per turn, so the cap is 30 % x 9 = 2.7 per turn. Ledger lands on at most 1/6 of rolls, about 1 per 6 turns of resolve, which is 6 block / 6 = 1 block per turn expected. 1.0 ≤ 2.7, so it passes. It is block, not heal, and expires. No HEAL slice.
- **Intake** (HP damage, player assumed to take no steering; expected value over the 6 slices, 1 landing per turn, WEAK 0.5x on ~40 % of landings ≈ 0.8 average):

| Slice | Damage | RAM drain |
|---|---|---|
| Toll x2 | 6 | 1 |
| Surcharge | 10 | 3 |
| Late Fee | 0 | 2 + OUTPUT_DOWN |
| Ledger/Null | 0 | 0 |

  - Unsteered expected HP damage = (6+6+10)/6 x 0.8 ≈ 2.9 per turn at T1. With steering it drops to about 1.5. T1 intake 1.5-3, above 0. Each tier multiplies this by the damage table (1.0 / 1.3 / 1.69 / 2.2): T4 ≈ 6.4 unsteered.
  - Unsteered expected RAM drain = (1+1+3+2)/6 ≈ 1.2 per turn against a +4 RAM income. The player can absorb it, but not while also paying for nudges and strong cards. That is the design: a tax of about a third of the income.
- RAM drain amounts are flat integers and are not scaled by tier (only damage scales, R2).

## 4. HP by tier

Phase budget (R2): `reference_dpt_by_tier` x 3.5 turns x needles (1), minus sustain per turn x 3.5.

| Tier | Ref dpt | Gross | Sustain (1.0/turn x 3.5) | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 3.5 | **32** (band 28-36) |
| T2 | 11 | 38.5 | 3.5 | **38** (34-44) |
| T3 | 14 | 49 | 3.5 | **48** (44-56) |
| T4 | 18 | 63 | 3.5 | **62** (56-70) |

Today's 53 HP sits mid-band at T3, so the pass lowers it at T1-T2 (the 3-4 turn target) and keeps T3 close. `hp_by_tier` = [32, 38, 48, 62].

## 5. Enrage
None (R4: normals off). The fight is capped by its own length, 3-4 turns.

## 6. Buffs and counter Exploits
Not a boss; not applicable.

## 7. Counterplay
- **Good player:**
  - Spend the free nudge to move the needle off Surcharge or Late Fee. Both are 4-tick slices, so a 1-2 tick nudge is enough.
  - Keep 1-2 RAM spare for the card that lands the burst.
  - Treat Toll as the cheap slice and let it land (1 RAM) rather than spend 1 RAM to avoid it.
  - Cleanse the Late Fee OUTPUT_DOWN only if it sits on the main damage slice.
  - SANDBOX (R13) cancels one Surcharge, saving 10 damage and 3 RAM.
- **Weak player:**
  - Pays nudge after nudge to dodge 1 RAM Tolls.
  - Goes RAM-dry by turn 3, so the finishing card is unaffordable.
  - Ignores Late Fee, so their best slice runs at -25 %.

## 8. Systems needed
- **N1:** amount modes, FLAT drain and damage. Existing fields can carry it as data.
- **N2:** `hp_by_tier` and the tier damage table.
- **N8 / N9:** OUTPUT_DOWN x1 on Late Fee. The existing PARASITE status halves output, so the fallback is a PARASITE (a 2-stack OUTPUT_DOWN per R8 migration) on Late Fee. It is harsher (-50 %).
- **N12:** variable slice sizes (4 and 6 ticks).
- **Fallback with no N12:** keep six 5-tick slices, which is the current wheel. Replace slot 4 with Late Fee and merge the Toll count to 2. This is data-only except the status choice. It loses the "narrow slice" nudge texture.

## 9. Delta vs today
- **Kept:** Shim 7 drain becomes Toll 6/drain 1, Defrag becomes Ledger, Overflow 12 becomes Surcharge 10/drain 3, Null stays. The RAM-toll identity, the single needle and the hub-less wheel stay.
- **Changed:**
  - The Priority slice (INFECT-type, drains 3, no damage) becomes Late Fee (drain 2 plus OUTPUT_DOWN). This gives a status counter that makes a RAM fight into a damage fight.
  - Sizes vary (5/6/4/5/4/6).
  - Overflow damage and drain are lowered, since the fight is shorter.
  - HP 53 to [32, 38, 48, 62].
- **heat_effects:** it has none; add none.
- **cycle_reward** stays 15.

## 10. Predicted sim check
No baseline row, so this is an estimate from the wheel.
- **Turns:** about 3.5 at the reference player at every tier (HP tracks reference damage by construction). p90 about 5.
- **Win %:** T1-T2 about 97 %, T3 about 94 %, T4 about 90 %.
- **Why:** it can only hurt through a 10-damage Overflow at one in six landings, so HP loss is low, and the real cost is RAM. Win rate falls only if RAM starvation stops the burst, which hits weaker builds at T4 where damage scales 2.2x.
- **Threat per turn:** 1.5-6.4 (above 0).
- **Heal turns:** 0.

## 11. Q:
- Q: Should RAM drain scale with tier at all? Proposed no (flat), since RAM income is fixed at +4.
- Q: Is a 1-RAM drain on every Toll too small to notice at the reference player, versus 2?
- Q: Does a Surcharge drain still happen if SANDBOX negates the hit? Proposed no, it negates the whole resolution.
- Q: Should the drain be capped at the player's current RAM (no going negative), with excess becoming a HP penalty?
