<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__parking_warden; status ok; tokens in 15817 cache-write 0 cache-read 32007 out 3750; cost $0.038. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# parking_warden: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, no enrage. Halcyon. Appears in **L1-2 as the Citation teacher** (first Halcyon fight, T1 Sites such as Parking Enforcement Office). At L5-6 it is a T2-T3 filler with the same shape.
- **The one question:** "Which of your slices can you afford to have cut by a Citation, and can you make the Citation land on a slice you don't need?"
- Its Citation is a *slow* status (OUTPUT_DOWN ×1, −25 %), not the old half-output PARASITE. A single stack is survivable, and the Warden's wheel is built so you learn to *steer the stamp*, not just cleanse it.
- **Answer that shortens the fight:** nudging so its pointer lands on the Citation's WEAK edge (or on Null), and bursting while its only defensive slice is off the pointer. **Answer that lengthens it:** letting Citations stack onto your Overflow/Shim and then trading at half output.
- Distinct from the other Halcyon normals: this is the pure single-stack Citation teacher with a "ticket" counter (see the hub below). Patrol Unit, Permit Office and the others should not own Citation-first design.

## 2. Phase plan (one phase, no threshold, no floor)

| Item | Value |
|---|---|
| Needles | 1, fixed at tick 0 (no uneven needles; this is the teaching enemy) |
| Hub rule | **Ticket Book (listener, N6):** on ON_CARD_PLAYED where the card is a nudge/spin card, nothing. Keep it simple: **no hub**. A pure-wheel enemy is the L1-2 teaching baseline |
| Statuses used | OUTPUT_DOWN ×1 (R8) via Citation |
| Parasites | none |
| Listeners | none |

**Layout (sizes sum to 30):**

| # | Slice | Ticks | Effect (damage amounts are FLAT, × the tier damage factor, R2) | Quality map |
|---|---|---|---|---|
| 1 | Shim 6 | 5 | 6 damage to pointer target | W G P G W |
| 2 | Citation | 4 | 3 damage + OUTPUT_DOWN ×1 on 1 random non-NULL slice of yours (SlicePick RANDOM_NON_NULL) | W G G W (no Perfect, so a stamp is never "precisely delivered") |
| 3 | Defrag 6 | 5 | BLOCK 6 FLAT | W G P G W |
| 4 | Overflow 10 | 4 | 10 damage | W G G W (the big hit has no Perfect and half-power edges) |
| 5 | Shim 6 | 5 | 6 damage | W G P G W |
| 6 | Citation | 3 | 3 damage + OUTPUT_DOWN ×1 on the slice **under your pointer** (SlicePick UNDER_POINTER) | G P G |
| 7 | Null | 4 | nothing | W G G W |

Sum: 5+4+5+4+5+3+4 = 30.

- **The two Citations ask different questions:** slice 2 stamps a random slice (you can't aim, so you carry a Cleanse or accept the risk); slice 6 stamps the exact slice you are landing on (you can *see* it coming and nudge your own wheel off the slice you want to keep clean).
- Slice 4 cut from 14 to 10 and shrunk to 4 ticks without a Perfect: this is the normal-class burst, scaled for the 3-4 turn target. WEAK on it halves to 5.
- Block 6 is the only defense and the only sustain-like thing: no heal.

## 3. Sustain and intake
- **Sustain:** none beyond the 6 BLOCK slice. Heal is 0, so the 30 % cap is trivially met. BLOCK absorbs roughly 6 of your ~9-14 damage on a turn that lands on it, i.e. about 0.7 effective block per turn averaged over 7 slices (weighting by ticks: 5/30 chance × 6 = 1.0 absorbed per turn, ≈ 11 % of the T1 reference 9).
- **Intake per turn at the reference player** (T1 factor 1.0; chance of landing by tick share, uniform start; moderate steering ignored):
  - Shim 6 ×2 slices (10 ticks): 10/30 × 6 = 2.0
  - Citation 3 ×2 (7 ticks): 7/30 × 3 = 0.7
  - Overflow 10 (4 ticks): 4/30 × 10 = 1.3
  - Defrag, Null: 0
  - **≈ 4.0 damage per turn at T1** (before Perfect/Good/WEAK weighting: ~3.5 after the Overflow edge halving). Well above 0. Over 3.5 turns ≈ 12-14 HP lost, a fair teaching cost against a 60 HP Breaker.
  - Scaling: T2 ×1.3 ≈ 5.2, T3 ×1.69 ≈ 6.8, T4 ×2.2 ≈ 8.8.
- **Citation cost:** an unanswered OUTPUT_DOWN ×1 costs about 25 % of one slice's output for the rest of the fight, roughly 1-2 damage per turn of lost player damage. This is the "hidden" intake.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Phase budget = `reference_dpt[t]` × 3.5 turns × needles hit (1 player needle on its single-needle wheel), minus sustain × 3.5 (sustain ≈ 0 here; I credit the BLOCK as ~1/turn):

| Tier | dpt | Budget arithmetic | **hp_by_tier** |
|---|---|---|---|
| T1 | 9 | 9×3.5 = 31.5 (−3.5 block) ≈ 28 → round up to the band | **32** |
| T2 | 11 | 11×3.5 = 38.5 − 3.5 ≈ 35 → band | **38** |
| T3 | 14 | 14×3.5 = 49 − 3.5 ≈ 45.5 → band | **48** |
| T4 | 18 | 18×3.5 = 63 − 3.5 ≈ 59.5 → band | **60** |

This replaces today's 48 at all tiers (48 × a scale at T3 was ~64+ in the current table). Small teaching enemy at the low end of each band because its question is cheap to answer.

## 5. Enrage
**None** (normal class, R4). A fight of 3-4 turns doesn't need a clock.

## 6. Buffs and counter Exploits
Not a boss; n/a.

## 7. Counterplay
- **Good player:** reads the pointer at turn start. If it sits on Citation (slice 6), nudge your own wheel one tick so your *weakest* slice (Defrag, Null) is under your pointer when the stamp lands. Burst on turns when its needle sits on Defrag/Null, since those are the turns it can't hurt you. Use the free nudge to push its needle off the 4-tick Overflow, whose edges are WEAK, so a 1-tick nudge nearly always halves it. Carries or picks up one Cleanse if available; otherwise lets one ×1 stack ride.
- **Weak player:** leaves the Citation under their Overflow/Perfect slice so their best action runs at −25 %, ignores slice 2's random stamp, and spends RAM nudging its needle onto Shim 6 instead of Null. Takes about 14-18 damage and a longer fight (5-6 turns) without it being lethal.
- **Fight-length lever:** every Defrag/Null turn you deny is a free turn for your damage; killing in 3 turns requires roughly 11 average at T1.

## 8. Systems needed
- **N1** amount modes (flat × tier factor; the block is FLAT) and **N2** `hp_by_tier` + `enemy_damage_by_tier`.
- **N8** ×N stacks and **N9** OUTPUT_DOWN as a status (the Citation rule).
- **N12** variable slice sizes + sub-tick maps (the 3-, 4- and 5-tick slices; R11).
- **Data-only fallback:** keep all slices at 5 ticks (6 slices, drop the second Shim into Null) and keep today's PARASITE status (halves the slice) as a Citation. Loses the Perfect-less Overflow edge but keeps the shape. Hp_by_tier needs N2 or a flat tier multiplier.

## 9. Delta vs today
- **Kept:** id, corporation, Citation concept, wheel of Shim/Citation/Defrag/Overflow/Null, one needle at tick 0, `cycle_reward` 15.
- **Changed:** 6 slices → 7 with variable sizes; the Citation goes from "half output until cleansed" to OUTPUT_DOWN ×1 (−25 %) with two delivery modes (random vs under-pointer); Shim 9 → 6 and Overflow 14 → 10 with no-Perfect edge; Citation now carries 3 damage so it has nonzero threat; HP 48 flat → 32/38/48/60.
- **Description text:** "Writes Citations: your slice runs at −25 % per ticket until you cleanse it."
- **heat_effects:** none exist on the file; none added.

## 10. Predicted sim check
No baseline row for Halcyon (the sweep covered Solace only), so this is an estimate from the wheel.
- **Turns:** about 3.5 mean at the step-0 skill, p90 ≤ 5; 3.0 at skill 1.0.
- **Win %:** T1 ≈ 98 %, T2 ≈ 97 %, T3 ≈ 93 %, T4 ≈ 91 %. Intake of 4-9 per turn over about 3.5 turns is 14-31 HP, well inside a 45-60 HP operative at the corresponding rank.
- **Why:** the only sustain is one 6-BLOCK slice, so HP-band-sized kills fall inside the 3-4 turn window, and Citations add a tax rather than a wall.

## 11. Q:
- Q: Should the first-ever Halcyon fight force a fixed opening (needle on the under-pointer Citation) as a tutorial beat, or stay on the normal random respin?
- Q: Does OUTPUT_DOWN ×1 on a WEAK landing still apply (R8 default yes)? If not, the Citation 4-tick edge is a free dodge.
- Q: Is a normal allowed two different Citation pick modes, or should slice 2 and 6 be merged to keep L1-2 simpler?
- Q: Does a Cleanse card appear reliably early enough in a T1 run for this to be a fair teaching fight?
