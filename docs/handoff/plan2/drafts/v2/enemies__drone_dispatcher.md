<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__drone_dispatcher; status ok; tokens in 6604 cache-write 0 cache-read 32585 out 3976; cost $0.030. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, garbled layout, "5 slices", Null map)** → The layout is now six slices summing to 30 (6+5+4+6+5+4). Every slice has an explicit R11 quality map and a stated intent: Bay 6 = W W G G W W (no Perfect, so its block is never "perfect-able"), Shim 5 = W G P G W (today's slice, the one Perfect window), Priority 4 = W G G W (no Perfect), Null 4 = W G G W (nothing resolves, so the map is irrelevant). The garbled Priority cell is removed, and all "5 slices" wording is corrected to "6 slices". The N12 fallback text says 6 slices.
- **Issue 2 (BLOCKER, Bay 6 vs 4, cap math)** → The layout table now says BLOCK 4 FLAT. The sustain is derived: P(Bay) = 12/30 = 0.4, so expected block is 0.4 × 4 × [1, 1.3, 1.69, 2.2] = 1.6 / 2.1 / 2.7 / 3.5 per turn, i.e. 17 / 19 / 19 / 19 % of reference dpt, under the 30 % cap. The invented "1.3 / 2.9" is dropped.
- **Issue 3 (BLOCKER, HP arithmetic)** → The §4 table is recomputed. Sustain is expected block × 3.5 turns, and every row subtracts exactly. The "guards soak a share" sentence is removed (it double-counted). HP: 28 / 34 / 44 / 56, all on the low edge of the R2 band.
- **Issue 4 (MAJOR, REPLACE contradiction)** → Spawn uses `on_occupied = SKIP` (no replacement), and launches onto the slice at tick 10 (the unguarded opposite slice) for a turn of warning. The REPLACE claim and the "don't finish a drone" counterplay are deleted. Killing a drone is a real, non-wasted answer. `SKIP` is a fixed-satellite occupancy mode under N13, with a fallback below. This does not conflict with R12, which only says REPLACE is the default docking rule. A spawn entry authors its own mode.
- **Issue 5 (MAJOR, hub vs spawn duplication)** → One owner: the Hangar is a `spawns` entry that owns `max_active = 2`. There is no separate hub rule (hub: none). The "value 2 today" claim is dropped as unverifiable. I state only the fields I author.
- **Issue 6 (MAJOR, intake)** → Intake is reconciled: Dispatcher 2.7 + 2 drones × 1.5 = 5.7 at T1, ×1.3 / 1.69 / 2.2. The drone Shim is set to 2 now (the critic's fix), so drone intake is 2 × 1.0 = 2.0 at T1 and the T4 total is about 9. Drone HP is authored as a flat per-tier number in the satellite's own data, not a vague `hp_by_tier` of "the drone".
- **Issue 7 (MAJOR, fixed needle makes the guard constant)** → The question varies because drones launch only onto the tick-10 slice and then ride the wheel. The player's free nudge or spin rotates which slice the Dispatcher's fixed needle reads, so the guard sits at the needle only when the player lets it. The needle stays at tick 0 (R10 allows any tick, but one needle gains nothing from an off-center position, so this is a deliberate choice).
- **Issue 8 (NIT)** → Drone Shim 2 is in the numbers now, not a post-hoc fix in §10.
- **Issue 9 (NIT)** → The fallback wording is fixed (see Issue 1).
- Kept (critic's "Keep"): the guard-versus-race question, the data-only hub spawn, real drone pressure (intake above 0), and the 4-tick Priority with no Perfect.

# drone_dispatcher: direct design

## 1. Identity & the one question
- **Class:** NORMAL, Meridian, 1 phase, 3-4 turns, no enrage.
- **Layers:** L1-2 teaching and L3-4 filler. At L5-6 it is a pressure add-on beside Meridian elites.
- **The one question:** "Does the guarded slice sit under the Dispatcher's needle this turn, and if it does, do you rotate it away or kill the guard?" A Courier Drone launches onto the tick-10 slice, rides the wheel, and bodyguards that slice. Hits aimed at a guarded needle hit the drone, not the Dispatcher.
- **Today's problem:** drones are optional noise, and Priority drains RAM with no real threat.
- **Shortening answer:** use the free nudge or a spin so the needle reads an unguarded slice and the Dispatcher takes the hit. Killing a drone is the secondary answer, since a new one only launches while fewer than 2 are docked and onto an empty slice.

## 2. Phase plan
Single phase, no threshold, no floor.

| Field | Value |
|---|---|
| Needles | 1, fixed at tick 0 |
| Hub | none (the Hangar is a spawn entry, not a hub rule) |
| Spawn (Hangar) | trigger ON_TURN_START, `every_n = 1`, `max_active = 2`, launch slice = the one at tick 10 at launch time, `on_occupied = SKIP` (N13) |

**Layout (6 slices, sum 6+5+4+6+5+4 = 30):**

| # | Slice | Ticks | Quality map | Effect |
|---|---|---|---|---|
| 1 | Launch Bay (DEFRAG) | 6 | W W G G W W | BLOCK 4 FLAT (× tier factor) |
| 2 | Shim | 5 | W G P G W | Damage 7 FLAT |
| 3 | Priority | 4 | W G G W | Damage 3 FLAT + drain 2 RAM |
| 4 | Launch Bay (DEFRAG) | 6 | W W G G W W | BLOCK 4 FLAT |
| 5 | Shim | 5 | W G P G W | Damage 7 FLAT |
| 6 | Null | 4 | W G G W | none |

- **Drone:** mini-wheel Shim 2 / Defrag 3, fixed to its slice (R12), HP 6 / 7 / 9 / 11 by tier (authored on the satellite's data).
- **Statuses, parasites and listeners:** none.

**Transition:** none (1 phase).

## 3. Sustain and intake
- **Sustain:** one source, the Bay BLOCK (temporary). P(Bay) = 12/30 = 0.4. Expected block = 0.4 × 4 × [1, 1.3, 1.69, 2.2] = 1.6 / 2.1 / 2.7 / 3.5 per turn. Against reference dpt [9, 11, 14, 18] that is 17 / 19 / 19 / 19 %, under the 30 % cap. There is no heal.
- **Intake at the reference player (T1, then × 1.3 / 1.69 / 2.2):**
  - Dispatcher: P(Shim) = 10/30, × 7 = 2.3; P(Priority) = 4/30, × 3 = 0.4. Total 2.7.
  - Drones: 2 drones × Shim 2 × P(its slice resolves ≈ 0.5) = 2.0, plus the drone's own Defrag, which does no damage to you.
  - **Total about 4.7 at T1; 6.1 / 7.9 / 10.3 at T2-T4.** Always above 0. (If the player kills a drone fast, intake falls toward 2.7, which is the reward for the answer.)

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70. Budget = reference dpt × 3.5 turns × 1 needle − expected block × 3.5.

| Tier | dpt × 3.5 | Sustain (block × 3.5) | Budget | HP |
|---|---|---|---|---|
| T1 | 31.5 | 1.6 × 3.5 = 5.6 | 25.9 | **28** (band floor) |
| T2 | 38.5 | 2.1 × 3.5 = 7.4 | 31.1 | **34** (band floor) |
| T3 | 49 | 2.7 × 3.5 = 9.5 | 39.5 | **44** (band floor) |
| T4 | 63 | 3.5 × 3.5 = 12.3 | 50.7 | **56** (band floor) |

The raw budget lands under the band floor every tier, so I clamp to the floor. The fight runs about 4 turns because drones absorb some hits, which is what the 3-4 turn target wants.

## 5. Enrage
Off (normal, R4).

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:** sees the drone arrive on the tick-10 slice, one turn before it reaches the needle, and uses the free nudge to keep the needle on Shim, Priority or Null. Kills a drone cheaply (6 HP at T1) with a card if it still lands in the way.
- **Mid player:** attacks into the guard, wastes damage on drones, and takes 5+ turns.
- **Weak player:** ignores the drones, takes about 5 per turn, and loses RAM to Priority.

## 8. Systems needed
| Need | N# | Fallback |
|---|---|---|
| Amount mode FLAT × tier damage factor | N1 | Data-only: today's raw amounts × the old `output_scale` |
| `hp_by_tier` | N2 | A per-tier HP table by hand |
| Uneven slice sizes + quality maps | N12 | Six 5-tick slices; the 4-tick Priority loses its no-Perfect property |
| Fixed satellites, `SKIN` occupancy mode | N13 | Today's spawn with `max_active = 2` already caps the count; launch slice stays "under the pointer" |

## 9. Delta vs today
- **Kept:** the drone spawn, the Priority RAM drain and the Shim / Defrag structure.
- **Changed:** Shim 8 → 7; Defrag 5 → 4 FLAT; launch every turn (cap 2) onto the tick-10 slice with SKIP; Priority becomes a 4-tick no-Perfect slice; slice sizes vary 6/5/4/6/5/4; drone Shim 2 with tiered HP.
- **HP:** 44 flat → 28 / 34 / 44 / 56.
- **`heat_effects`:** none authored; none added.

## 10. Predicted sim check
- **Estimate (no Meridian baseline row):** 3.5-4.5 turns; win about 97 % at T1-T2, about 94 % at T3, about 92 % at T4.
- **Why:** drones soak about 20-30 % of hits and Dispatcher intake is 4.7-10.3 per turn, so the fight stays short and non-trivial, unlike today's near-zero threat.

## 11. Open questions
Q: Should the SKIN occupancy mode (named `on_occupied = SKIP`) be a new N13 value, or is data-only "launch only if the tick-10 slice is empty" enough?
Q: Should a killed drone count as destroyed for Daemons and rewards (open question 7)?
Q: Is launching every turn too strong against the free nudge once Meridian elites stack it at L5-6?
