<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__launch_pad; status ok; tokens in 15770 cache-write 0 cache-read 32007 out 3582; cost $0.037. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# launch_pad: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, no enrage. Orbital Commons. Appears in **L2-5** as the "launch window" fight. It is the Orbital teaching fight for **fixed satellite replacement** (R12/N13), so it sits at L1-3 on T1-T2 and returns as pressure at L5-6 on T3-T4.
- **The one question:** *"A drone launches every other turn onto a fixed slice. Do you kill the drone, or steer around it and hit the pad?"*
  - Bodyguard rule (GDD 2.7): a Pointer attack at a guarded slice hits the satellite, not the pad.
  - Satellites are fixed (R12), so a drone stays on its slice. The player can read the guarded slice and aim the needle elsewhere.
  - **Shortens the fight:** nudge or spin so the player's pointer lands on an unguarded pad slice, and spend a Perfect only on the Launch slice. Killing a 5 HP drone costs a hit that does no damage to the pad.
- Distinct from Mission Director (rim gates and replacement), Weather Satellite and Orbital Debris. Launch Pad owns "one drone at a time, readable two turns ahead".

## 2. Phase plan
**Single phase.** No threshold, no floor, no phase change (R1). The pad is stationary and uses one needle.

| Property | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | none |
| Statuses | OVERCLOCKED via Solar Flare (existing) |
| Listeners | none |
| Satellite | Launch Drone (existing `orbital_drone.tres`, 5 HP), every 2 turns on the pad's start-of-turn trigger, `dock_slot` = the Launch slice's neighbour (fixed), `max_active = 1`, `on_occupied = REPLACE` (N13) |

**Layout (ticks, sum 30):** Sandbox 5 · Shim 8 · Launch 6 · Shim 5 · Solar Flare 4 · Null 6

| Slice | Ticks | Effect | Mode | Perfect/Weak window |
|---|---|---|---|---|
| Fuel Shield (SANDBOX type, enemy shield) | 5 | gain SHIELD 8% max HP | PERCENT (of max HP; ~4 at T1) | W G P G W |
| Shim 8 | 6 | deal 8 to the player | FLAT × tier factor | W W G G W W: **no Perfect**, narrow-tier |
| Launch | 6 | OVERFLOW-type 12 damage, hits once | FLAT × tier factor | W W G G W W, so the dangerous slice is hard to hit "perfectly" but easy to land Good |
| Shim 5 | 5 | deal 5 | FLAT | W G P G W |
| Solar Flare | 4 | APPLY_STATUS OVERCLOCKED on 1 random non-NULL slice of yours | n/a | G G G G is the default W G G W; it applies on any landing |
| Null | 6 | nothing | n/a | n/a |

Tick order sums: 5+6+6+5+4+6 = 30. Slice sizes of 4 and 6 require N12 (R11).

**Why OVERCLOCKED stays:** it is the Orbital identity. On the player's slice it is 1.5× once, then CORRUPTED. Under R9 CORRUPTED is a RAM tax of 2×, so the Flare question is "do I use the free power-up before it burns?"

**Drone intent:** the 5 HP drone (existing mini-wheel Shim 3 / Defrag 3) docks on the Launch slice's neighbour, i.e. the Shim 5 slice at the Launch slice's clockwise side (fixed, N13).
- Launched on turns 2 and 4 (start-of-turn trigger every_n = 2).
- With `max_active = 1` and REPLACE, a second launch on turn 4 replaces a living drone instead of stacking.

## 3. Sustain and intake
- **Sustain:** one source, the Fuel Shield. 8% max HP ≈ 4 at T1 (46→ band 28-36, shield ≈ 3), landing on 1 of 6 slices (≈ 1/6 of turns by span, 5 of 30 ticks).
- Reference dpt T1 = 9. Expected shield per turn ≈ 3 × (5/30) = 0.5 → **5.6% of reference**, below the 30% cap. At T4 shield ≈ 5 against 18 dpt (≈ 0.8 per turn, 4.6%).
- **Intake per turn (reference player, no block/evade):** the pointer is uniform over 30 ticks, so expected damage = Σ(span/30 × output × tier factor).
  - T1: Shim 8 (6/30 × 8 = 1.6) + Launch (6/30 × 12 = 2.4) + Shim 5 (5/30 × 5 = 0.83) = **4.8 per turn**, plus the drone's 3 (turns 2-4, average ≈ 1.5 per turn) = **≈ 6.3**.
  - T4 factor 2.2: **≈ 10.6 + 3.3 ≈ 13.9**. Always above 0.
- Intake falls to about 2 if the player steers onto Fuel Shield, Null or Flare edges.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Budget = reference dpt × 3.5 turns × needles landing (1) − sustain × 3.5.

| Tier | dpt | 3.5 turns | − sustain (≈0.5-0.8 × 3.5) | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | −1.8 | **30** |
| T2 | 11 | 38.5 | −2.0 | **36** |
| T3 | 14 | 49 | −2.4 | **46** |
| T4 | 18 | 63 | −2.8 | **60** |

T3 matches today's 46 HP exactly, so no change at the tier most tested. Add 1 drone-kill turn into the 3.5: each drone-kill costs a Shim hit but removes 3 expected damage, which is cheaper than racing.

## 5. Enrage
None (R4, normals). Fights end in 3-4 turns; the drone is capped at 1 active and cannot snowball.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:**
  - T1 start: read the pad's needle and the Fuel Shield.
  - Use the free nudge to move the player pointer off the guarded slice before the drone launches (turn 2 telegraph: drone lands next to Launch).
  - Land a Perfect on the Shim 5 slice (the only slice with a pad Perfect window), or Good on the 6-tick slices.
  - Spend one nudge to push the enemy needle to Null (6 ticks, easy to hit).
  - Cleanse the OVERCLOCKED slice or fire it first, because a burned slice taxes 2× RAM.
- **Weak player:** shoots the drone every time (5 HP, no pad damage), lets Launch land at WEAK-then-Good on their own wheel, and lets OVERCLOCKED burn into CORRUPTED without using it. Runs out of RAM in turn 4.

## 8. Systems needed
- **N12** (slice sizes 4, 6) for the layout above. *Fallback:* data-only, 5-tick slices ×6 with Launch at 12, Shim 7, Flare, Null; loses the narrow-Perfect read but plays fine.
- **N13** (fixed satellites, REPLACE). *Fallback:* none needed for a first test: the current satellite dock rule already works, but a replacement drone is untested.
- **N1** (PERCENT shield, tier-scaled FLAT). *Fallback:* flat 4 shield, unscaled.
- **N2** (`hp_by_tier`, `enemy_damage_by_tier`). *Fallback:* today's single `hp` and multiplier.
- N10, N6, N3, N4: **not used**.

## 9. Delta vs today
- **Kept:** the id, display name, Solar Flare, the Launch Drone, `spawns` every 2 turns, `cycle_reward = 15`, T3 HP 46.
- **Changed:**
  - Layout from equal 6×5 to sizes 5/6/6/5/4/6; the second Sandbox is replaced by a Launch slice (12 damage) so the pad has one strong hit worth steering around.
  - Shield changes from a flat 5 to a PERCENT 8%.
  - `max_active = 2` → 1 with REPLACE.
  - `hp_by_tier` = 30/36/46/60.
- **`heat_effects`:** none authored today, none added.

## 10. Predicted sim check
No baseline row exists, so this is an estimate from the wheel.
- **Turns:** ≈ 3.4 at the reference skill, p90 ≈ 5.
- **Win %:** T1 ≈ 98%, T2 ≈ 96%, T3 ≈ 92%, T4 ≈ 88%. The drop at T4 comes from the drone on a damaged operative.
- **Why:** intake of 6-14 per turn over 3.4 turns costs 20-47 HP, survivable within an operative's 45-60 HP at L2-5. The Care Swarm failure (43 HP at T3) is not repeated.
- T4 would sit just under the ≥ 90% target at T3-T4. Tune the Launch slice down to 10 if so.

## 11. Open questions
Q: Should the drone's `max_active` be 1 with REPLACE, or 2 so the replacement rule is never exercised in a normal fight?
Q: Does a replaced drone count as destroyed for Daemons (Botnet Seed, kill-reward hooks)?
Q: Should the Launch slice's 6-tick, no-Perfect profile be authored explicitly via `tick_quality` (W G G G G W) so Good-or-better is wider?
Q: Is a PERCENT shield on a normal too fiddly to read; would flat 4 × tier factor be clearer?
Q: Should Solar Flare stay random non-NULL, or pick the slice under the pointer so it is steerable?
