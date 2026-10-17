<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__launch_pad; status ok; tokens in 6852 cache-write 0 cache-read 32585 out 7807; cost $0.049. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Critic 1 (BLOCKER, Flare row contradicts R11):** The Flare row now states the size-4 default map, W G G W. The 6-tick rows are labeled "default W W G G W W, no Perfect"; the "narrow-tier" wording is gone.
- **Critic 2 (BLOCKER, R13 naming):** The Fuel Shield slice is retyped as SHIELD: lingering, capped, PERCENT. It is no longer called SANDBOX. SANDBOX is reserved for the whole-attack-negate evade rule.
- **Critic 3 (BLOCKER, sustain arithmetic):**
  - Recomputed from the rounded HP: shield is 2.4 / 3.0 / 3.8 / 4.8 at T1-T4. The per-turn upper bound is 0.40 / 0.48 / 0.63 / 0.80, which is 4.4 % of the reference at every tier.
  - Deductions at 3.5 turns are 1.4 / 1.7 / 2.2 / 2.8. HP is 30 / 37 / 47 / 60.
  - The garbled "46 → band" text is removed and a T3 sustain figure is added.
- **Critic 4 (MAJOR, drone damage):**
  - The drone resolves only when its host slice (Launch) is under the pad's needle. That is 6/30 of turns, and 3 damage on half its mini-wheel, ≈ 0.3 per turn at T1.
  - The v1 "≈ 1.5" figure was wrong.
  - The intake table is recomputed, now also weighted by WEAK output (0.5×).
- **Critic 5 (MAJOR, dock slot and fields):**
  - The drone now docks on the **Launch** slice itself, so the dangerous slice is the guarded one. v1 had it on the weak Shim 5.
  - The cadence and `max_active` fields are tagged: today's `spawns` every 2 turns and `max_active` exist, and `dock_slot` fixed plus REPLACE is N13.
  - The N13 fallback is now stated honestly. Without N13 the drone docks by today's rule and a second launch does nothing while one is alive.
- **Critic 6 (MAJOR, win % under target):** Pre-tuned: Launch is 10 (was 12) and Shim is 8 (kept). Predictions are now T3 94 % and T4 91 %.
- **Critic 7 (NIT):**
  - The counterplay line about pushing the needle to Null is kept but reworded as a free nudge of the pad's wheel. It does not conflict with the single-sustain claim, because Null is not sustain.
  - Cleanse is dropped from the normal-fight advice.
- **Found while re-adding ticks:** v1 summed to 32, not 30 (5+6+6+5+4+6). Null is now 4 ticks (W G G W), so the sum is 5+6+6+5+4+4 = 30.
- **Critic Qs:**
  - Drone damage lands only on Launch's trigger (answered in §3).
  - `max_active` 1 with REPLACE only fires on the turn-4 launch (answered in §2).
  - The shared shield cap stays as Q.
- **Designer rulings:** no conflict.

# launch_pad: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, no enrage. Orbital Commons.
- **Layers:** L1-3 on T1-T2 as the Orbital teaching fight for fixed satellite replacement (R12/N13). L5-6 on T3-T4 as pressure.
- **The one question:** *"A drone sits on the Launch slice. Do you kill it, or steer your needle elsewhere and hit the pad?"*
  - Bodyguard rule (GDD 2.7): a Pointer attack at a guarded slice hits the drone, not the pad.
  - Satellites are fixed (R12), so the guard never moves. The guarded slice is readable.
  - **The answer that shortens the fight:** land on an unguarded slice. Shim 5 and the Shield slice both have a Perfect window, and Shim 8 is unguarded. Killing the 5 HP drone costs a hit that does no damage to the pad, but it also removes Launch's 10-damage threat.
- It owns "one drone at a time, readable a turn ahead", distinct from Mission Director (rim gates), Weather Satellite and Orbital Debris.

## 2. Phase plan
**Single phase.** No threshold, no floor, no phase change (R1).

| Property | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | none |
| Statuses | OVERCLOCKED via Solar Flare (existing) |
| Listeners | none |
| Satellite | Launch Drone (`orbital_drone.tres`, 5 HP, mini-wheel Shim 3 / Defrag 3), launched on turns 2 and 4 (today's `spawns` every 2 turns), `dock_slot` = the Launch slice (fixed, N13), `max_active` = 1, `on_occupied` = REPLACE (N13) |

The turn-4 launch replaces a surviving drone. That happens only in a fight that reaches turn 4 with the drone alive, so REPLACE is exercised rarely.

**Layout (ticks, clockwise from tick 0, sum 30):** Shield 5 · Shim 6 · Launch 6 · Shim 5 · Flare 4 · Null 4, since 5+6+6+5+4+4 = 30.

| Slice | Ticks | Effect | Mode | Sub-tick map (R11) |
|---|---|---|---|---|
| Shield (SHIELD, lingering, cap 15) | 5 | gain shield 8 % of max HP | PERCENT | W G P G W |
| Shim (heavy) | 6 | deal 8 to the player | FLAT × tier factor | W W G G W W (no Perfect) |
| Launch (OVERFLOW type; docks the drone) | 6 | deal 10 to the player | FLAT × tier factor | W W G G W W (no Perfect) |
| Shim (light) | 5 | deal 5 | FLAT × tier factor | W G P G W |
| Solar Flare (INFECT type) | 4 | APPLY_STATUS OVERCLOCKED on 1 random non-NULL slice of yours | n/a | W G G W |
| Null | 4 | nothing | n/a | W G G W |

A Perfect on a 6-tick slice is impossible, so Perfect-based hooks are not available on the pad's heavy slices. The player's best landing there is Good.

**Why OVERCLOCKED stays:** it is the Orbital identity. The status gives the player's slice 1.5× once, then it becomes CORRUPTED. Under R9 that is a 2× RAM tax, so the Flare asks "do I fire the boosted slice before it burns?"

## 3. Sustain and intake
- **Sustain:** one source, the Shield slice, 8 % of max HP. Its needle probability is 5/30, and the figures below are upper bounds that ignore the WEAK 0.5×.

| Tier | HP | Shield | Per turn (× 5/30) | % of reference dpt |
|---|---|---|---|---|
| T1 | 30 | 2.4 | 0.40 | 4.4 % of 9 |
| T2 | 37 | 3.0 | 0.48 | 4.4 % of 11 |
| T3 | 47 | 3.8 | 0.63 | 4.5 % of 14 |
| T4 | 60 | 4.8 | 0.80 | 4.4 % of 18 |

  All are far below the 30 % cap, and the shield stays well under the cap of 15.
- **Intake per turn (reference player, no block or evade):** the needle is uniform over 30 ticks. Expected WEAK weighting is 0.667 for 6-tick slices and 0.8 for 5-tick slices.
  - T1 (factor 1.0):
    - Shim 8: 6/30 × 8 × 0.667 = 1.07.
    - Launch: 6/30 × 10 × 0.667 = 1.33.
    - Shim 5: 5/30 × 5 × 0.8 = 0.67.
    - Pad total is 3.07.
    - The drone adds 0.3 (it fires only on Launch's trigger, 6/30, with Shim 3 on half its wheel).
    - Total **≈ 3.4**.
  - T2 (×1.3): 4.0 + 0.39 = **≈ 4.4**.
  - T3 (×1.69): 5.2 + 0.51 = **≈ 5.7**.
  - T4 (×2.2): 6.75 + 0.66 = **≈ 7.4**.
- Always above 0. It drops toward 1 if the player steers onto Shield, Flare or Null edges. Over 3.4 turns, T4 costs ≈ 25 HP.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Budget = reference dpt × 3.5 turns × 1 needle − sustain per turn × 3.5.

| Tier | dpt × 3.5 | − sustain × 3.5 | Result | HP |
|---|---|---|---|---|
| T1 | 9 × 3.5 = 31.5 | 0.40 × 3.5 = 1.4 | 30.1 | **30** |
| T2 | 11 × 3.5 = 38.5 | 0.48 × 3.5 = 1.7 | 36.8 | **37** |
| T3 | 14 × 3.5 = 49 | 0.63 × 3.5 = 2.2 | 46.8 | **47** |
| T4 | 18 × 3.5 = 63 | 0.80 × 3.5 = 2.8 | 60.2 | **60** |

T3 is 47, essentially today's 46, so the most-tested tier barely moves. All values are inside the bands.

## 5. Enrage
None (R4, normals). The fight is 3-4 turns, and the drone is capped at one active, so nothing can snowball.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:**
  - Read the pad's needle and the drone on Launch. Use the free nudge to put your own pointer on Shim light or the Shield slice's Perfect window, rather than the guarded Launch slice.
  - Nudge or spin the pad's wheel so its needle lands on Null or the Flare's edge, avoiding Shim heavy and Launch.
  - Take the one Perfect-capable unguarded window (Shim 5 or Shield) for the Perfect hook.
  - Fire an OVERCLOCKED slice the turn it appears, before it burns into CORRUPTED.
- **Weak player:** shoots the drone every turn (5 HP, no pad damage), lets OVERCLOCKED burn into the 2× RAM tax, and runs short of RAM by turn 4.

## 8. Systems needed
- **N12** (slice sizes 4 and 6). *Fallback (data-only):* six 5-tick slices with Launch 10, Shim 8, Shim 5, Shield, Flare and Null. The 6-tick no-Perfect read is lost, but the fight plays.
- **N13** (fixed dock slot, REPLACE). *Fallback:* today's dock rule with `max_active` 1. A second launch while one is alive is simply skipped, and the fixed-guard question is weaker.
- **N1** (PERCENT shield, FLAT × tier factor). *Fallback:* flat shield 3, unscaled.
- **N2** (`hp_by_tier`, `enemy_damage_by_tier`). *Fallback:* today's single `hp` and multiplier.
- The `spawns` cadence and `max_active` fields exist today. If the per-spawn dock slot is not authorable, it is NEW: spawn dock slot (data field), covered by N13.
- N3, N4, N6, N10: not used.

## 9. Delta vs today
- **Kept:** the id, display name, Solar Flare, the Launch Drone, `spawns` every 2 turns, `cycle_reward` 15, T3 HP ≈ 46.
- **Changed:**
  - Layout from equal 6×5 to sizes 5/6/6/5/4/4. A 10-damage Launch slice with a guard replaces the second shield slice.
  - The shield is retyped from SANDBOX to SHIELD (R13), moving from a flat 5 to PERCENT 8 %.
  - `max_active` 2 → 1 with REPLACE.
  - `hp_by_tier` is 30 / 37 / 47 / 60.
- **`heat_effects`:** none authored today, none added.

## 10. Predicted sim check
No baseline row exists, so this is an estimate from the wheel.
- **Turns:** ≈ 3.4 at the reference skill, p90 ≈ 5.
- **Win %:** T1 ≈ 98 %, T2 ≈ 97 %, T3 ≈ 94 %, T4 ≈ 91 %.
- **Why:** intake of 3.4-7.4 per turn over 3.4 turns costs ≈ 12-25 HP, survivable against 45-60 HP operatives. Launch at 10 (not 12) keeps T3-T4 above the ≥ 90 % target. The Care Swarm failure (43 HP lost at T3) is not repeated.

## 11. Open questions
Q: Does a replaced drone count as destroyed for Daemons (Botnet Seed, kill-reward hooks)?
Q: Is the enemy percent shield cap shared with the player's `shield_cap` of 15 (CONTENT_DESIGN_V2 Q9)?
Q: Should Solar Flare stay random non-NULL, or hit the slice under the pointer so it is steerable?
Q: Is a PERCENT shield on a normal too fiddly to read, compared with flat 3 × tier factor?
Q: Should launches fire on turns 1 and 3 instead, so the guard is up from the opening turn?
