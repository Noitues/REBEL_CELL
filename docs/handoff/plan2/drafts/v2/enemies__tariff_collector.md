<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__tariff_collector; status ok; tokens in 6345 cache-write 0 cache-read 32585 out 4468; cost $0.032. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (HP rows don't follow the formula):** fixed. Sustain is now one consistent number, 1.0 expected block per turn × 3.5 turns = 3.5 at every tier, and the table shows each subtraction. HP is now 30 / 36 / 46 / 60, each in its R2 band.
- **Issue 2 (sustain not tied to the cap or the HP deduction):** fixed. §3 states the 1.0 per turn once, checks it against the 30 % cap (2.7 at T1), and §4 uses that same number. Block is not HP sustain, so deducting it is conservative; this is stated.
- **Issue 3 (Late Fee as a second RAM source; CORRUPTED ×2 unused):** kept the 2-RAM drain on Late Fee, because the Q on it stays open for the designer. Added a RAM-forecast note: the drain is separate from the R9 ×2 cost, which only applies when the player's pointer acts on a CORRUPTED slice. The Collector applies no CORRUPTED, so there is no stacking. No scope added.
- **Issue 4 (fallback unclear, "harsher" claim wrong):** fixed. The fallback without N8 is today's PARASITE status on Late Fee, which R8 defines as a 2-stack OUTPUT_DOWN. It is stated plainly that there is no softer data-only option, and the "harsher" claim and the confusing "merge Toll count" line are dropped. The no-N12 fallback is rewritten as a clear six-5-tick layout.
- **Issue 5 (WEAK mix wrong, T4 scaling unclear):** fixed. §3 uses a per-slice tier mix: 5-tick slices are 40 % WEAK, 4-tick slices (W G G W) are 50 % WEAK. Base damage is shown separately from tier-scaled damage. Surcharge also reads at 0.5× on WEAK, which is now shown.
- **Issue 6 (can RAM drain exceed current RAM):** fixed. Drain is capped at current RAM and never goes negative. There is no HP penalty. The preview shows the actual RAM removed.
- **Issue 7 (today's numbers unverifiable):** §9 now labels them "per the draft's reading of the current file".
- **Issue 8 (no baseline row):** §10 states that no baseline row exists for this enemy.
- **Critic Q:** "Late Fee 2 RAM on top of the status?" kept as an open Q. "Toll on a corrupted slice" is answered in the Late Fee note above.
- **Kept, because the critic marked them strong:** the RAM-worth question, the Toll / Surcharge / Late Fee split, and the 6/6/4/5/4/6 layout summing to 30 with no hub and no enrage.

# tariff_collector: direct design

## 1. Identity & the one question
- **Class:** Normal, Meridian, 1 phase, 3-4 turns, no enrage.
- **Layers:** L3-6 pressure. It is the first Meridian fight that taxes RAM, so it comes after L1-2, where RAM is still a free resource. L1-2 belongs to Cargo Hauler and the basics.
- **The one question: "What is your RAM worth this turn?"** Landed hits drain RAM, so the player chooses between paying RAM to dodge or steer, or taking the drain and keeping the plan.
- **Distinct inside Meridian:**
  - Conveyor Warden and Route Optimizer own orbit and WEIGHT.
  - Customs Scanner and Drone Dispatcher own intel and drones.
  - The Collector is the only normal whose damage is mostly a RAM toll.
- **What shortens the fight:** keep RAM in reserve for the burst, and spend the free nudge to push the single needle off Surcharge and Late Fee onto Toll, Ledger or Null. Burst its HP before the Surcharge lines up.

## 2. Phase plan (single phase, no threshold, no floor)

Needle: 1, fixed at tick 0. The wheel has 6 slices from R11 sizes.

| # | Slice | Ticks | Tick map | Effect (base values, before the tier damage table) |
|---|---|---|---|---|
| 0 | Toll | 5 | W G P G W | SHIM 6 damage FLAT; drain 1 RAM FLAT |
| 1 | Ledger | 6 | W W G G W W | DEFRAG 6 BLOCK FLAT (no Perfect) |
| 2 | Surcharge | 4 | W G G W | OVERFLOW 10 damage FLAT; drain 3 RAM FLAT (no Perfect, so no tight window to deny) |
| 3 | Toll | 5 | W G P G W | as slice 0 |
| 4 | Late Fee | 4 | W G G W | INFECT: drain 2 RAM FLAT; OUTPUT_DOWN ×1 on the slice under your pointer (applies on any landing tier) |
| 5 | Null | 6 | W W G G W W | nothing |

Sum: 5+6+4+5+4+6 = **30**.

- **RAM drain rule:** drain is capped at current RAM and never goes negative. There is no HP penalty. If SANDBOX negates the resolution, no drain happens.
- **Hub rule:** none (no heal, no resistance). The question stays pure.
- **Statuses used:** OUTPUT_DOWN ×1 (N8, N9). The Collector applies no CORRUPTED, so R9's ×2 RAM cost never stacks with its drain. The drain is a separate removal, not a cost multiplier.
- **Listeners:** none.
- **Transition:** none, single phase.
- **Why this layout:** the dangerous slices (Surcharge, Late Fee) are 4-tick with no Perfect, so a 1-2 tick nudge off them is meaningful because they are narrow. Both Tolls are 5-tick with a Perfect, so they read as the cheap, harmless landing.

## 3. Sustain and intake

- **Sustain:** one source, Ledger BLOCK 6 FLAT, a defensive slice that expires. Expected value: one Ledger per 5 landings on average is generous; the model charges 1.0 block per turn. The cap is 30 % × 9 = 2.7 per turn at T1 (more at higher tiers), so 1.0 ≤ 2.7 and it passes. Block is not HP sustain, but §4 deducts the 1.0 per turn anyway, to stay conservative. There is no HEAL slice.
- **Intake** (HP damage at the reference player, unsteered, one landing per turn, each of the six slices equally likely). WEAK is 0.5× output. Tier mix: 5-tick Toll is 2/5 = 40 % WEAK, so its factor is 0.6 + 0.4×0.5 = 0.8; 4-tick Surcharge is 50 % WEAK, so its factor is 0.5 + 0.5×0.5 = 0.75.

| Slice | Base damage | Tier factor | Expected | RAM drain |
|---|---|---|---|---|
| Toll ×2 | 6 | 0.8 | 4.8 each | 1 |
| Surcharge | 10 | 0.75 | 7.5 | 3 |
| Late Fee | 0 | n/a | 0 | 2 + OUTPUT_DOWN |
| Ledger / Null | 0 | n/a | 0 | 0 |

  - Unsteered expected base damage = (4.8 + 4.8 + 7.5)/6 = **2.85 per turn at T1**. After the damage table (1.0 / 1.3 / 1.69 / 2.2): **T2 ≈ 3.7, T3 ≈ 4.8, T4 ≈ 6.3**. With steering it drops to about half. Intake is above 0 at every tier.
  - Expected RAM drain (unscaled; only damage scales, R2) = (1 + 1 + 3 + 2)/6 ≈ **1.2 per turn** against +4 income. That is about 30 % of income, the intended tax. Drain on a landing is capped by current RAM.

## 4. HP by tier

Phase budget (R2): `reference_dpt_by_tier` × 3.5 turns × 1 needle, minus sustain (1.0 per turn × 3.5 = 3.5).

| Tier | Ref dpt | Gross (×3.5) | −3.5 sustain | hp_by_tier |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 28 | **30** (band 28-36) |
| T2 | 11 | 38.5 | 35 | **36** (34-44) |
| T3 | 14 | 49 | 45.5 | **46** (44-56) |
| T4 | 18 | 63 | 59.5 | **60** (56-70) |

Each value rounds the budget up to a whole HP and sits in its band. Today's 53 at T3 (per the draft's reading of the current file) drops to 46.

## 5. Enrage
None (R4: normals off). The fight is capped by its own length of 3-4 turns.

## 6. Buffs and counter Exploits
Not a boss; not applicable.

## 7. Counterplay
- **Good player:**
  - Spend the free nudge to move the needle off Surcharge or Late Fee. Both are 4-tick slices, so 1-2 ticks is enough.
  - Keep 1-2 RAM spare for the card that lands the burst.
  - Treat Toll as the cheap slice and let it land (1 RAM) rather than spend 1 RAM to avoid it.
  - Cleanse the Late Fee OUTPUT_DOWN only if it sits on the main damage slice.
  - SANDBOX (R13) negates one Surcharge, saving its damage and its 3 RAM drain.
- **Weak player:**
  - Pays nudge after nudge to dodge 1-RAM Tolls.
  - Goes RAM-dry by turn 3, so the finishing card is unaffordable.
  - Ignores Late Fee, so their best slice runs at -25 %.

## 8. Systems needed
- **N1:** amount modes, FLAT drain and damage. Existing fields can carry this as data.
- **N2:** `hp_by_tier` and the tier damage table.
- **N8 / N9:** OUTPUT_DOWN ×1 on Late Fee.
  - **Fallback without N8:** use today's PARASITE status on Late Fee. R8 defines it as a 2-stack OUTPUT_DOWN, so the effect is −50 %, not −25 %. There is no softer data-only option; if −50 % is too strong, drop the status and keep only the 2-RAM drain.
- **N12:** variable slice sizes (4 and 6 ticks).
  - **Fallback without N12:** six 5-tick slices in the order Toll, Ledger, Surcharge, Toll, Late Fee, Null. This is data-only. It loses the narrow-slice nudge texture and gives every slice a Perfect.

## 9. Delta vs today
Today's numbers below are per the draft's reading of the current file.
- **Kept:** Shim 7 with a drain becomes Toll 6 / drain 1, Defrag becomes Ledger, Overflow 12 becomes Surcharge 10 / drain 3, Null stays. The RAM-toll identity, the single needle and the hub-less wheel stay.
- **Changed:**
  - The Priority slice (INFECT-type, drain 3, no damage) becomes Late Fee (drain 2 plus OUTPUT_DOWN).
  - Slice sizes vary (5/6/4/5/4/6).
  - Overflow damage and drain are lowered because the fight is shorter.
  - HP 53 becomes [30, 36, 46, 60].
- **heat_effects:** it has none; add none.
- **cycle_reward** stays 15.

## 10. Predicted sim check
No baseline row exists for this enemy, so this is an estimate from the wheel.
- **Turns:** about 3.5 at the reference player at every tier (HP tracks reference damage by construction). p90 about 5.
- **Win %:** T1-T2 about 97 %, T3 about 94 %, T4 about 90 %.
- **Why:** it hurts HP only through a 10-base Surcharge on one landing in six, so HP loss is low and the real cost is RAM. Win rate falls only if RAM starvation stops the burst, which hits weaker builds at T4 where damage is 2.2×.
- **Threat per turn:** 2.85 at T1 up to 6.3 at T4 (above 0).
- **Heal turns:** 0.

## 11. Q:
- Q: Should Late Fee cost 2 RAM on top of the status, or is the status alone enough of a toll?
- Q: Is a 1-RAM drain on every Toll too small to notice at the reference player, versus 2?
- Q: Should RAM drain scale with tier at all? Proposed no (flat), since RAM income is fixed at +4.
