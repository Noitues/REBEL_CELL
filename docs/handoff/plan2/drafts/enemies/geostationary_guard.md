<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__geostationary_guard; status ok; tokens in 16053 cache-write 0 cache-read 32007 out 14190; cost $0.090. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# geostationary_guard: direct design

## 1. Identity & the one question
- **Class:** Elite (2 phases, one threshold at 50 %). It appears from L3 upward in Orbital's pool and is rare at L1-2. It is a pressure fight at L5-6 and not a teaching fight.
- **Fantasy:** a satellite that sits still until it is forced down. In P1 it holds station and cannot be shoved. In P2 it breaks station, spirals, and overclocks you.
- **P1 "On Station":** *You can't steer it, so what do you pay to steer around it?*
  - Its wheel is locked by resistance 3, so nudges on it are expensive.
  - A bodyguard drone sits on its big Overflow slice.
  - The shortening answer: shape your own landing, and hold your spin and Flip cards for P2 instead of burning them on resistance.
- **P2 "Re-entry":** *Cash in the overclock before it burns you.*
  - Resistance is gone and the needle orbits 3 ticks per turn, so its wheel can be steered.
  - Two Solar Flare slices overclock your slices (1.5×, then CORRUPTED).
  - The shortening answer: land your overclocked slices on a Perfect or Good before they burn, and Flip or Spin its Overflow off your needle.
- **Distinct from siblings:** it has no rim gates and no satellite replacement (Mission Director), and the Station Commander is not designed here. Its signature is the resistance lock in P1 that switches off in P2. Both phases use one needle.

## 2. Phase plan
Tick geometry: slice spans start at tick −2 and run by cumulative size, as the 5-tick slice does today. All numbers are T1 base values. Flat enemy amounts are multiplied by `enemy_damage_by_tier` (R2).

**P1 On Station (100 → 50 %)**

| Item | Design |
|---|---|
| Needle | 1 at tick 0, orbit 0 |
| Layout (sum 30) | Shield 5 (−2..2) · Shim 5 (3..7) · Flare 5 (8..12) · Overflow 4 (13..16, drone docked) · Shim 5 (17..21) · Null 6 (22..27) |
| Shield (SANDBOX type → SHIELD) | 6 FLAT, ×tier factor, capped at 15 (`shield_cap`) |
| Shim | 10 FLAT |
| Overflow | 16 FLAT. A 4-tick slice (W G G W) has no Perfect; it is full output on 2 of 4 ticks. |
| Solar Flare | OVERCLOCK on 1 random non-NULL slice of yours (existing `slice_pick` = RANDOM_NON_NULL) |
| Hub | Station Hold: resistance 3, restored each player turn. Hub Breach cards disable it for one turn. |
| Satellite | Orbital Drone (existing `orbital_drone.tres`), fixed on the Overflow slice (R12), `max_active` 1, respawns every 2 turns |
| Statuses | OVERCLOCKED on you from Flare |
| Listeners | none |

**Transition at 50 %**
- Damage parks at ceil(max × 0.5) (R3) and the excess is lost. The preview shows "PARKED −N".
- **Wheel:** `wheel_override` to the P2 layout; hub resistance 3 → 0; orbit 0 → 3.
- **Drone:** removed (see §8).
- **Statuses:** all kept on both sides (R6). Your overclocked slices follow the centre-tick remap, so a P1 overclock is a P2 resource. `cleanse_on_enter` = NONE: the carry-over is deliberate.
- **Phase line:** one line of text. The new layout is revealed on entry.

**P2 Re-entry (50 → 0 %)**

| Item | Design |
|---|---|
| Needle | 1 at tick 0, orbit 3 per turn (trail shown) |
| Layout (sum 30) | Overflow 5 (−2..2) · Flare 5 (3..7) · Shim 4 (8..11) · Null 4 (12..15) · Flare 4 (16..19) · Overflow 4 (20..23) · Shim 4 (24..27) |
| Shim | 12 FLAT. 4-tick slices have no Perfect. |
| Overflow | 16 FLAT. The 5-tick one has a Perfect; the 4-tick one does not. |
| Flare | OVERCLOCK on 1 random non-NULL slice of yours (existing `slice_pick` = RANDOM_NON_NULL). Two Flare slices, 9 of 30 ticks. |
| Hub | none. Resistance 0, so Flip, Spin and Respin all work. |
| Enemy shield | none |

**Why these two phases are different questions**
- **P1** is defensive. The enemy's needle is stuck, you can't afford to move it, and the drone guards the Overflow.
- **P2** is a race. It is more dangerous, but now movable and exploitable.

## 3. Sustain and intake
**Sustain:** one source, the P1 Shield. P2 has none.
- It resolves on 5 of 30 ticks per turn at 6 FLAT × tier factor, so average sustain per turn = 5/30 × 6 × factor:

| Tier | Factor | Sustain per turn | Share of reference dpt |
|---|---|---|---|
| T1 | 1.0 | 1.0 | 11 % of 9 |
| T2 | 1.3 | 1.3 | 12 % of 11 |
| T3 | 1.69 | 1.7 | 12 % of 14 |
| T4 | 2.2 | 2.2 | 12 % of 18 |

This is well under the 30 % cap. The Shield is also the only thing the Hub Breach and Resistance questions protect.

**Intake per turn**, with the needle landing uniformly, a typical tier mix and no steering (T1 base):

| Phase | Calculation | Intake | Target |
|---|---|---|---|
| P1 | Shim 10/30 × 10 × 0.8 = 2.7, plus Overflow 4/30 × 16 × 0.75 = 1.6 | **≈ 4.3** | 3-5 |
| P2 | Shim 8/30 × 12 × 0.75 = 2.4, plus Overflow 9/30 × 16 × 0.8 = 3.8 | **≈ 6.2** | 5-8 |

Both are above 0. Flare adds a status tax on top of this.

## 4. HP by tier
Phase budget (R2) = `reference_dpt` × 3.5 turns × needles (1 here) − sustain × 3.5. Threshold 0.5.

| Tier | dpt | P1 budget | P2 budget | Total | Authored `hp_by_tier` | R2 elite band |
|---|---|---|---|---|---|---|
| T1 | 9 | (9 − 1.0) × 3.5 = 28 | 9 × 3.5 = 32 | 60 | **60** (30 / 30) | 56-72 |
| T2 | 11 | (11 − 1.3) × 3.5 = 34 | 38.5 | 72.5 | **72** (36 / 36) | 68-88 |
| T3 | 14 | (14 − 1.7) × 3.5 = 43 | 49 | 92 | **96** (48 / 48) | 88-112 |
| T4 | 18 | (18 − 2.2) × 3.5 = 55 | 63 | 118 | **120** (60 / 60) | 112-144 |

- The 0.5 threshold and equal halves are chosen over the exact 28/32 split. P1 loses a few HP per turn to drone interception, which offsets its smaller budget.
- This replaces today's 145 (about 1.5× the T3 band).

## 5. Enrage
**Default for elites:** start turn 8, every 5 turns, +25 % damage.
- The expected fight is about 7 turns, so enrage only catches stalling players, which is the purpose.
- It raises damage only; heal and defense are unchanged. It stays additive (×1.25 at turn 8, ×1.5 at turn 13).

## 6. Buffs and counter Exploits
Not applicable (elite).

## 7. Counterplay
**P1 (good player)**
- Reads its needle and does not spend nudges on it. Resistance 3 turns each nudge into a 3-RAM-or-nothing proposition.
- If the needle sits on the Overflow, takes the hit through the drone or SANDBOXes it. Otherwise ignores the drone and hits the guarded host elsewhere.
- Hands Flares to the later phase by keeping overclocked slices unburnt.
- Dumps burst before the 50 % park line. Overkill is lost, so the damage plan must come in just under the threshold and finish with leftover cards for P2.

**P1 (weak player)**
- Pours Spin and Flip cards into the resistance and stalls.
- Kills the drone first, which respawns every 2 turns.
- Takes Flares on the wheel's best slice and loses it to corruption.

**P2 (good player)**
- Flips or spins the Overflow off the needle. This is now cheap because resistance is 0.
- Reads the 3-tick orbit trail one turn ahead.
- Lands on an overclocked Overflow or Shim for the 1.5× burst before the slice burns.
- Uses ENCRYPTED or Cleanse on the Flare target.

**P2 (weak player)**
- Lets overclocked slices burn into CORRUPTED, which doubles RAM on that slice (R9).
- Never repositions, and eats a 16-damage Overflow Perfect.

## 8. Systems needed
| # | Use | Fallback without it |
|---|---|---|
| N1 | Flat amounts × tier factor | Author the numbers per tier by hand |
| N2 | `hp_by_tier` | A flat HP value |
| N3 | One threshold, parked damage, `_apply_wheel_override` keeps statuses | No park or status keep: wipes statuses and drops the Flare carry-over, so not recommended |
| N4 | Default enrage | Default HP only |
| N9 | OVERCLOCKED → CORRUPTED as a RAM tax | Today's CORRUPTED self-damage |
| N12 | Layout sizes 4 / 5 / 6 | **Data-only fallback:** six 5-tick slices. P1 is today's six (Shield, Shim, Flare, Overflow, Shim, Null). P2 is Overflow, Flare, Shim, Null, Flare, Overflow, with the Shim dropped into Shim 5. |
| N13 | Fixed drone (R12) | Dock on the same slice; mobile today |
| N14 | SHIELD rename | Name only, no rule change |
| NEW: phase clears satellites | Remove the drone at the transition | The drone survives, re-docked to slot 0, and just stops respawning |

## 9. Delta vs today
- **HP:** 145 → 60 / 72 / 96 / 120 by tier. It now has 2 phases and a 50 % park.
- **Wheel:** a single static 6×5 wheel → two distinct layouts with different sizes.
- **Orbit:** orbit 3 for the whole fight → P1 orbit 0, P2 orbit 3.
- **Resistance:** none → resistance 3 hub in P1 only.
- **Amounts:** Shim 14 → 10 (P1) / 12 (P2). Overflow stays 16. Sandbox 8 → Shield 6 FLAT × tier.
- **Flare:** 1 slice → 1 in P1, 2 in P2 (the P2 Flare is the burst window).
- **Drone:** kept as the P1 bodyguard, made fixed.
- **`heat_effects`:** the current `.tres` has none. None are added, because the two phases carry the difficulty on their own.

## 10. Predicted sim check
Estimated from the wheel; there is no baseline row for Orbital.
- **Turns:** about 6.5-7.5 at the step-0 skill, p90 at 9. Each phase is 3-4 turns.
- **Win rate:**

| Tier | Win % | Why |
|---|---|---|
| T1 | ≈ 98 % | Intake ≈ 4-6 |
| T2 | ≈ 96 % | |
| T3 | ≈ 92 % | |
| T4 | ≈ 85 % | Flares, burnt slices and RAM tax compound |

- **Today:** the 145 HP at T3 implies roughly 2 turns of extra attrition. The new fight is shorter and sharper.

## 11. Open questions
Q: Does orbit move the needle before or after the preview and resolve? I assume the preview shows the post-orbit landing (the trail), so preview equals result.
Q: Should the drone be killed or removed at the transition? Removing it needs the small new "phase clears satellites" field.
Q: Is the Shield cap of 15 right for an enemy (R2 open question 9), or should the enemy's flat shield be uncapped?
Q: Does a Flare landing on a WEAK tier still apply its status (R2 open question 11)? I assume yes.
Q: Should P2's second Flare slice stay at 4 ticks, or be reduced if sim shows overclock cascades?
