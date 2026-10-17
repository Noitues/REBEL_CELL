<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__last_mile_enforcer; status ok; tokens in 16128 cache-write 0 cache-read 32007 out 4386; cost $0.041. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# last_mile_enforcer: direct design

## 1. Identity & the one question

**Class:** Elite, Meridian, 2 phases, one threshold at 50 %. Appears at L3-6 (pressure) and as an L5-6 gate. It is not a teaching enemy; Port Authority covers the Meridian elite teaching slot.

**Distinct from the rest of Meridian:**
- Conveyor Warden and Weight enemies already own spin resistance.
- Port Authority and Customs Seal own shields and "Customs".
- Drone Dispatcher owns spawning drones.
- The Enforcer is the **delivery** enemy: it commits to a landing zone and punishes you for being there. It uses orbit (readable ahead), a *marked* delivery, and a single escort. It uses no resistance and no heal.

| Phase | Question |
|---|---|
| P1 Route (100 → 50 %) | **"Where will it be in two turns, and where will you be?"** Its needle orbits 2 ticks per turn, so the hit is readable ahead. The player must set up a landing that avoids the big slices when the needle arrives. |
| P2 Signature Required (50 → 0 %) | **"Can you take the delivery or refuse it?"** The needle stops orbiting and *latches* onto the first slice it lands on. Every escort kill or Perfect redirects it. This is a SANDBOX-timing puzzle. |

**Answer that shortens the fight:** killing the escort drone early denies the guard bodyguard in P1. In P2, dodging its big Overflow with SANDBOX or a nudge turns the fight into a burst window.

## 2. Phase plan

### P1 Route (100 → 50 %, floor at 50 %)

| Item | Value |
|---|---|
| Needles | 1, tick 0, ORBIT 2 ticks per turn (trail shows future ticks) |
| Escort | Courier Drone (existing `courier_drone.tres`), docked on slot 1, max_active 1, respawns every 3rd turn if dead |
| Hub | none |
| Statuses | none |
| Listeners | none |

**Layout (sum 30):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 0 | Shim | 5 | 8 damage FLAT |
| 1 | Shim | 4 | 8 damage FLAT (escort docked here) |
| 2 | Defrag | 5 | BLOCK 6 FLAT |
| 3 | Overflow | 4 | 14 damage FLAT. At 4 ticks it has no Perfect, only G/G. A WEAK edge is possible. |
| 4 | Sandbox | 6 | SHIELD 6 FLAT |
| 5 | Null | 6 | none |

With orbit +2 per turn and a 30-tick wheel, the needle walks through the slices over about 7 turns, so each turn's landing is preview-able two turns ahead. A narrow Overflow (4 ticks, no Perfect) makes it a short, dangerous window: most needle ticks fall on its WEAK (0.5×) edge only if the player has nudged the wheel there.

### Transition P1 → P2 (parks at 50 %)
- Wheel override with a new layout; the escort is cleared (`cleanse_on_enter` = OWN is not needed; its escort drone is removed by the override).
- The player's statuses are kept (R6), with the centre-tick remap.
- The needle's orbit is replaced by the **Latch**: `pointer_orbit_per_turn = 0`, and the needle begins on tick 0.
- Phase line: "SIGNATURE REQUIRED."

### P2 Signature Required (50 → 0 %, no floor)

| Item | Value |
|---|---|
| Needles | 2, ticks 0 / 12 (uneven, R10); both fixed |
| Escort | none |
| Hub rule | **Proof of Delivery (listener, N6):** each time you land a Perfect, it gains BLOCK 4 FLAT on its next resolve (cap 8). It punishes Perfect-fishing. |
| Statuses | Parcel Hold: Cite puts OUTPUT_DOWN ×1 on your slice under the needle (stacks to ×2) |
| Listeners | The Hub rule above |

**Layout (sum 30):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 0 | Overflow | 7 | 16 damage FLAT; Perfect ×1 |
| 1 | Cite (INFECT) | 3 | 5 damage FLAT + OUTPUT_DOWN ×1 on the slice under the pointer |
| 2 | Shim | 4 | 8 damage FLAT |
| 3 | Defrag | 4 | BLOCK 6 FLAT |
| 4 | Overflow | 5 | 16 damage FLAT |
| 5 | Null | 4 | none |
| 6 | Shim | 3 | 8 damage FLAT |

Needles at 0 and 12 sit on a 7-tick Overflow (centre) and a boundary between a Shim and a Defrag. The player will often face one big hit and one small one; choosing which needle takes the Overflow is the puzzle. One needle can be steered to Null with a 1-tick nudge.

## 3. Sustain and intake

**Sustain:** none in either phase. The Perfect-block listener is a small defense, not a heal, capped at 8 per resolve (≈ 2.3 per turn) against the reference's 14 DPT at T3 = 16 %, under the 30 % cap.

**Intake per turn** (reference player at T3, enemy damage factor 1.69; flat amounts scale by the tier damage factor):
- **P1:** the needle visits a damaging slice about 4 of 6 turns. Average base damage per resolve is (8+8+14)/6 × ~0.8 hit rate ≈ 4 raw, ×1.69 ≈ 6.8 at T3 before player block. Targeting 6-9 with decent play after block ≈ 3-5. Above 0.
- **P2:** two needles; average ≈ 11 base per resolve × 1.69 ≈ 19 before defense, ≈ 8-12 after reference play. Above 0.

## 4. HP by tier (R2, Elite 2 phases)

Budget = `reference_dpt_by_tier` × 3.5 turns × phases (1 needle in P1, 2 needles in P2 give the player's hits more landings, so P2 needles weigh heavier), minus sustain.

| Tier | DPT | P1 (3.5 t) | P2 (3.5 t) | Block-listener cut (2.3/t × 3.5 ≈ 8) | HP |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 31.5 | 8 | **64** (band 56–72) |
| T2 | 11 | 38.5 | 38.5 | 8 | **78** (68–88) |
| T3 | 14 | 49 | 49 | 8 | **100** (88–112) |
| T4 | 18 | 63 | 63 | 8 | **128** (112–144) |

Threshold at 0.5 gives each phase half. The needle count in P2 matters for the *player's* hits, not the enemy's, so no extra adjustment is made. Today is 132 at every tier (T3 band ceiling 112, so this is a cut of 24 %).

## 5. Enrage

**Default** (start turn 8, every 5, +25 %, additive). The fight targets 6-8 turns, so enrage only bites a stalled fight. Authored enrage is not needed. The orbit gives deterministic readability, so a slow player has no new surprise to learn; only the damage clock.

## 6. Buffs and counter Exploits
Elite: none.

## 7. Counterplay

- **P1 (good):** read the orbit trail. Spend the free nudge on turns when the needle approaches the 4-tick Overflow, nudging it by 1-2 ticks onto a Null or a Defrag. Kill the escort first (it guards slot 1's Shim); damage on slot 1 hits the drone instead. Burst the boss as the needle crosses Defrag/Sandbox turns. Get to 50 % quickly; damage beyond it is lost to the park.
- **P1 (weak):** ignores the trail, eats the Overflow at T3 (≈ 24 damage), and wastes burst hitting the escort repeatedly because it respawns every 3rd turn.
- **P2 (good):** save a SANDBOX or Flip for the turn both needles read big slices. Land Good, not Perfect, when the Block listener is at cap. Cleanse stacked OUTPUT_DOWN on your best slice. The two needles on 0 / 12 allow a nudge to move one onto Null while the other stays on a small slice.
- **P2 (weak):** chases Perfects (feeding the block), stacks OUTPUT_DOWN ×2 on their Overflow slice and loses their burst, then dies to enrage.

## 8. Systems needed

| N# | Use | Fallback |
|---|---|---|
| N2 | `hp_by_tier`, `enemy_damage_by_tier` | none; required (data field) |
| N3 | Phase threshold parking | without it, the phase still triggers, but the first threshold has no floor. Acceptable for a first test |
| N1 | FLAT amounts × damage factor | the current scaling already does this approximately |
| N11 | Needles at 0 / 12 | use 0 / 15 (evenly spaced, today's rule) |
| N12 | Slice sizes 3-7 | use 5-tick slices: 6 slices; lose the narrow-Overflow window (P1 becomes a flat orbit puzzle) |
| N6 | Proof of Delivery listener | drop the listener; P2 loses its anti-Perfect pressure and relies on two needles |
| N8, N9 | OUTPUT_DOWN ×N stacks | use today's PARASITE as one OUTPUT_DOWN ×2 stack, no stacking |
| N4, N19 | Enrage, metrics | n/a |

A data-only version exists: P1 with 5-tick slices, one extra needle at 15 in P2, and no listener, status or size changes.

## 9. Delta vs today

- **Kept:** the corporation, the ORBIT 2 needle and the escort drone as the P1 identity; slice values 14/16/8 shrink only by the new tiering.
- **Changed:** HP 132 → 64/78/100/128; adds a second phase; the one flat wheel becomes two designed wheels; 4-tick Overflow; second needle in P2; Cite replaces nothing and a Perfect-block listener is new.
- **Removed:** the Sandbox 8 slice in P2 (replaced by a Defrag), to make SANDBOX scarce for the player to out-trade.
- **heat_effects:** no `heat_effects` appear in the supplied .tres, so there is nothing to keep. If the live file carries any, **retire them**: Heat should change the enemy via the global ICE and Heat modifiers (R2 buffs are tier-independent), and a bespoke effect would blur the phase budget.

## 10. Predicted sim check

No baseline row exists (Solace only); this is an estimate from the wheels.
- **Expected turns:** P1 ≈ 3.5 and P2 ≈ 3.5, total ≈ 7 at the reference skill; p90 ≈ 9.
- **Win %:** T1 ≈ 97, T2 ≈ 95, T3 ≈ 90, T4 ≈ 82 (T4 is low, because 19 raw damage per turn from two needles overwhelms an under-defended player; the pass line is 90 % at T3 and T4 is allowed to be harder).
- **Why:** 132 HP at the 14 DPT reference is ~9.4 turns, so today it overruns the 6-8 target. 100 HP at T3 gives ~7. The orbit's readability is the main source of wins.

## 11. Open questions

Q: Should the escort's respawn every 3rd turn count as "sustain" for the 30 % cap, since it re-creates a bodyguard?
Q: Is the narrow no-Perfect Overflow too punishing without the Firmware that raises sub-tick tiers (R11)? Should it be 5 ticks at T1-T2?
Q: Does OUTPUT_DOWN ×2 on the player's best slice feel like the Halcyon mini-boss's Citation stacking too closely? Should Meridian use TIER_DOWN instead?
Q: Does the Proof of Delivery listener need the preview to show "BLOCK +4 if you land a Perfect" before the action is committed?
Q: Should the P2 uneven needle gap (12) be fixed, or authored per tier so higher tiers narrow it to 9?
