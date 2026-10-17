<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__cell_informant; status ok; tokens in 16363 cache-write 0 cache-read 32007 out 3057; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# cell_informant: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns, no enrage. **Corporation:** REBEL_CELL. **Layers:** L1-2 teaching; the first enemy a player meets that reads the player's wheel instead of its own.
- **Concept:** a snitch that tails your last move. Its reader orbits 3 ticks per turn (today's trait, kept). The orbit is a **deterministic, visible schedule**. The one question: **"Its needle moves 3 per turn, so which of its slices will it be on next turn, and can you steer the dangerous one onto the turn you've guarded?"**
- **Shortens the fight:** a player who reads the orbit trail, lets the big Overflow land into a SANDBOX or BLOCK turn, and bursts on the turns it sits on Null or Detour. A player who ignores the trail eats the Overflow and a Citation.
- Distinct from siblings: Dead Drop, Echo Process, Mirror Script, Handler Proxy and Loyalty Test are not changed here. The Informant owns **orbit-as-schedule** and a small status tax. It has no listener and no lock.

## 2. Phase plan

**Phase 1 "Tail" (100 → 0 %, no floor, as the only phase)**

| Item | Value |
|---|---|
| Needle | 1 pointer at tick 0, `pointer_orbit_per_turn = 3`. The orbit trail is shown. |
| Hub rule | none |
| Listeners | none |
| Statuses | OUTPUT_DOWN ×1 via Citation (N8/N9). Fallback: today's PARASITE. |

Layout: 7 slices, sizes sum to 30. Centres run clockwise from tick 0.

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Shim | 4 | 8 damage (FLAT, × tier factor) |
| 2 | Priority | 4 | drain 2 RAM (FLAT) |
| 3 | Detour | 4 | SANDBOX: negates one of your hits |
| 4 | Overflow | 4 | 16 damage (FLAT) |
| 5 | Citation | 5 | OUTPUT_DOWN ×1 on a random non-NULL slice of yours |
| 6 | Null | 4 | nothing |
| 7 | Shim | 5 | 8 damage |

4+4+4+4+5+4+5 = 30.

- 4-tick slices have no Perfect (W G G W). The 5-tick Citation and the last Shim keep a Perfect. Because Perfect is rare on its own wheel, the player's precision matters less and the orbit schedule matters more.
- The orbit is 3 ticks per turn, so it crosses a ~4-tick slice in about 1.3 turns. With the start-of-turn respin the position is random, and the trail shows where it lands after the orbit.
- **Orbit order matters:** from any start, the needle reaches Overflow right after Detour or Priority. The player can predict "Overflow next turn" and prepare.
- **Transition:** none (a single phase).

## 3. Sustain and intake
- **Sustain:** none. Sustain 0 is well inside the 30 % cap (≤ 2.7 damage per turn at T1).
- **Intake per turn at the reference player.** Assume an unprepared player and equal slice weight (4,4,4,4,5,4,5 of 30):
  - Shim 8 (weights 9/30): 2.4
  - Overflow 16 (4/30): 2.1
  - Shim, Priority, Citation, Detour and Null cost HP 0 directly, but Citation and Priority impose a status or RAM cost.
  - Expected HP loss per turn ≈ 4.5 damage at T1 before block. That is above 0 and in the L1-2 teaching band of 2-4 (slightly above, because the Overflow spike is the lesson).
  - Prepared play (SANDBOX the Overflow turn) drops it to about 2.5.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Budget = `reference_dpt` × 3.5 turns, single needle at 1.0.

| Tier | dpt | Budget | Sustain | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 0 | **32** |
| T2 | 11 | 38.5 | 0 | **39** |
| T3 | 14 | 49 | 0 | **50** |
| T4 | 18 | 63 | 0 | **63** |

`hp_by_tier` = [32, 39, 50, 63]. The current flat 46 is mid-band at T3, so today's number is replaced. Flat damage × `enemy_damage_by_tier` [1.0, 1.3, 1.69, 2.2] gives Overflow 16 / 21 / 27 / 35 and Shim 8 / 10 / 14 / 18. Check: the T4 Overflow at 35 is above a typical T4 block, which is why SANDBOX timing matters there.

## 5. Enrage
None. Class default is off for normals (R4). The fight is 3-4 turns and the schedule is finite.

## 6. Buffs and counter Exploits
Not applicable: not a boss.

## 7. Counterplay
- **Good player:** reads the trail on turn 1 and sees which slice the needle reaches next. Lands burst on the turns it is on Null or Detour. Plays BLOCK or SANDBOX on the Overflow turn. Cleanses or Encrypts against Citation if the fight runs long. The fight ends in 3 turns.
- **Weak player:** ignores the trail, wastes a card into the Detour turn (the hit is negated), and takes the Overflow at full value. A stacked Citation then makes their finishing burst slower and the fight reaches 5-6 turns.
- **Nudge tool:** the player can nudge the Informant's wheel by 1-2 ticks to turn the Overflow into a WEAK landing (0.5×) or to move to Null. The orbit makes this a planning decision across turns, not a one-turn fix.

## 8. Systems needed
- **N1** (FLAT amounts × tier factor): needed for the scaled damage. Fallback: current `output_scale` scaling works data-only.
- **N2** (`hp_by_tier`): needed. Fallback: set `hp` to 50 and accept the flat multiplier.
- **N12** (variable slice sizes): needed for 4/5-tick mix. Fallback: all 5-tick slices, 6 slices (drop one Shim). Cost: loses the "rare Perfect" feel.
- **N8/N9** (×N OUTPUT_DOWN): Citation fallback is today's PARASITE status (halve output), data-only.
- **N11** (pointers on any tick): not required (the pointer starts at 0).
- No N6, N7 or N10 dependencies.

## 9. Delta vs today
- **Kept:** the orbit of 3 per turn, Shim, Priority, Detour, Overflow, Citation and Null, and the REBEL_CELL identity.
- **Changed:**
  - 6 slices become 7, with 4-tick slices.
  - The Shim 10 slice is replaced by Shim 8 ×2 (damage spread).
  - Overflow 16 stays as the spike.
  - `hp` 46 becomes `hp_by_tier` [32, 39, 50, 63].
  - Detour is renamed SANDBOX (R13).
  - Citation's status becomes OUTPUT_DOWN ×1.
- **heat_effects:** none exist on a normal; none added.

## 10. Predicted sim check
No baseline row exists, so this is estimated from the wheel.
- **Turns:** 3.3 at T1-T2, 3.5 at T3-T4 (about 3.5 turns per fight at the reference player). p90 ≤ 5.
- **Win %:** T1 ≥ 97 %, T2 ≥ 96 %, T3 ≈ 93 %, T4 ≈ 90 %. The T4 Overflow of 35 is the only real killer, and it is readable.
- **Why:** low HP, one needle, no sustain and a known schedule keep fights short. Threat per turn is above 0 at every tier.

## 11. Q:
- Q: Should the orbit trail show only next turn's landing or two turns ahead (more teaching at L1-2)?
- Q: Does a 4-tick W G G W Shim feel too safe for the player's nudge play, since a one-tick nudge can only move between WEAK and GOOD?
- Q: Should Citation target the slice under the pointer (readable) rather than a random one (a preview-equals-result risk)?
- Q: Is Priority (RAM drain 2) enough pressure on its own, or should it become a corrupt-adjacent RAM tax once N9 lands?
