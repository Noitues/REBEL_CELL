<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__drone_dispatcher; status ok; tokens in 16078 cache-write 0 cache-read 32007 out 3174; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# drone_dispatcher: direct design

## 1. Identity & the one question
- **Class:** NORMAL, Meridian, 1 phase, 3-4 turns, no enrage.
- **Layers:** L1-2 teaching and L3-4 filler. At L5-6 it is a pressure add-on, since its sat management stacks with Meridian elites.
- **The one question:** "Do you kill the dispatcher's hangar before it fills, or race the dispatcher through the guards?" Its needle sits behind a satellite. Hits at the guarded slice go to the drone, not the Dispatcher.
- **Today's problem:** the drone is optional noise. Drones launch every other turn, so the fight is slow, and Priority drains 3 RAM with no threat.
- **Shortening answer:** steer your pointer to an unguarded slice or Null so the Dispatcher takes the hit. Do not spend damage on drones.
  - A drone has HP and a small attack, so killing the first one early is the secondary answer.
  - Damage into a drone is damage not taken by the Dispatcher.

## 2. Phase plan
Single phase, no threshold and no floor (the last phase has no floor).

| Field | Value |
|---|---|
| Needles | 1, at tick 0 (R10 allows any tick; kept fixed for teaching) |
| Hub | Hangar: at turn start, if fewer than 2 drones are docked, launch one (fixed, N13). Hub rule is data-only via the existing `spawns` (every_n=1). |

**Layout (sum 30), 5 slices on uneven sizes (N12):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Launch Bay (DEFRAG) | 6 | BLOCK 6 FLAT (×tier damage factor) |
| 2 | Shim | 5 | Damage 7 FLAT |
| 3 | Priority | 4 (G P P G is not used; default W G G W, no Perfect) | Damage 3 + drain 2 RAM (ON_SLICE_TRIGGER) |
| 4 | Launch Bay (DEFRAG) | 6 | BLOCK 6 FLAT |
| 5 | Shim | 5 | Damage 7 FLAT |
| 6 | Null | 4 | none |

- **Satellite:** Courier Drone, docked on a slice. Fixed (R12). `dock_slot = -1` keeps today's placement, i.e. the slice under the pointer when launched.
- **Drone mini-wheel:** Shim 3 / Defrag 3. Drone HP is 6 at T1, scaled by `hp_by_tier` of the drone. Max 2 active.
- **Spawn:** trigger ON_TURN_START (value 2 today), `every_n = 1` from turn 1, `max_active = 2`, `on_occupied = REPLACE` (N13). Replacement keeps a damaged drone from being parked in place: a new drone overwrites the old one on the same slice. This is wanted. The hangar is always topped up, so the real cost of killing drones is tempo.
- **Statuses/parasites/listeners:** none. Normals stay readable.

**Transition:** none (1 phase).

## 3. Sustain and intake
- **Sustain:** one source, the BLOCK on Launch Bay. It is temporary and expires at the start of its next turn.
  - Bay 6 FLAT × tier factor is 6 at T1 and 13 at T4 (6 × 2.2).
  - It is only gained when the pointer lands there, 2 of 6 slices, so the expected value is about 4 per turn at T1 and about 9 at T4.
  - Cap check: 30 % of reference dpt is 2.7 at T1 and 5.4 at T4. Raw blocks at T4 exceed this, so **drop Bay to 4 FLAT** (4 → 4 / 5.2 / 6.8 / 8.8 by tier). Expected absorbed is about 1.3 at T1 and 2.9 at T4, since P(Bay) ≈ 0.4 and block only matters if you attack into it.
  - Within the cap at every tier. No heal.
- **Intake per turn** at the reference player (the Dispatcher lands on Shim 7, Priority 3, or a Bay):
  - Dispatcher: per-resolve P(Shim) ≈ 10/30 = 0.33, damage 7. P(Priority) ≈ 4/30, damage 3. Expected about 2.7 at T1.
  - Drones: each drone's Shim 3 hits you with probability about 0.5, which is about 1.5 per drone. Two drones give about 3 at steady state, so drones are the main damage.
  - **Total about 3-5 per turn at T1, scaled by the damage table (×1.3 / 1.69 / 2.2), about 8-11 at T4.** This is above 0 at every tier.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70.

Budget: `reference_dpt[t] × 3.5 × needles (1)` minus sustain × 3.5. The sat guard soaks a share, so I give the full-damage budget and let the guards stretch the fight to 4 turns.

| Tier | dpt | ×3.5 | Sustain (3.5 × cap-checked ~1.3-2.9) | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | −4.5 | **30** |
| T2 | 11 | 38.5 | −5 | **36** |
| T3 | 14 | 49 | −7 | **46** |
| T4 | 18 | 63 | −10 | **58** |

Today's 44 HP at T3 is replaced by 46, and the 44 now sits inside the band's low edge.

## 5. Enrage
Off (normal, R4). Two drones keep the fight under 4 turns.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:** reads the launch pattern. The drone appears on the pointer's slice, so use the free nudge to make the Dispatcher's needle land on Shim or Null while your own pointer takes the unguarded slice. Kill the first drone with a cheap hit when the drone's HP is 6, or aim past it.
- **Mid player:** shoots at the guarded slice and wastes damage on drones that get replaced. Slow, taking 5+ turns and 12+ damage.
- **Weak player:** ignores drones, takes about 3-4 per turn, and loses the RAM race to Priority.
- **Answer:** replacing satellites (`REPLACE`) punishes overkill. Do not finish a drone that is about to be replaced.

## 8. Systems needed
| Need | N# | Fallback |
|---|---|---|
| Amount mode FLAT × tier damage factor | N1 | Data-only: today's raw amounts scaled by the old `output_scale` |
| `hp_by_tier` | N2 | Keep one `hp` per tier with a manual table |
| Uneven slice sizes (6/5/4/6/5/4) | N12 | Use 5-tick slices and a 6-slice layout (the current one); the 4-tick Priority without Perfect is lost |
| Fixed satellites + REPLACE | N13 | Data-only: drones are spawned today; without REPLACE the slot just waits (`max_active = 2` already caps) |

## 9. Delta vs today
- **Kept:** the drone spawn, Priority RAM drain, and the Shim 8 / Defrag 5 structure.
- **Changed:**
  - Shim 8 → 7 and Defrag 5 → 4 (the sustain cap).
  - Spawn every 2 turns → every turn from turn 1 up to 2 (the hangar fills faster and gives intake).
  - The first-turn drone makes the guard question real.
  - Priority becomes a 4-tick slice without Perfect, so a player cannot perfect-wipe the RAM drain.
  - Slice sizes vary (6/5/4/6/5/4).
- **HP:** 44 flat → 30/36/46/58.
- **`heat_effects`:** none authored on this file; none added.

## 10. Predicted sim check
- **Estimate (no baseline row for Meridian):** 3.5-4.5 turns at the reference player; win ≥ 97 % at T1-T2, ~93 % at T3, ~90 % at T4.
- **Why:** the drones soak about 20-30 % of the player's hits, the Dispatcher deals 3-5 per turn at T1, and the 4-tick Priority is the only RAM pressure.
- **Risk:** T4 intake of about 11 per turn over 4 turns is about 44, which is high for an add-on fight. I would watch HP lost at T4 and drop the drone Shim 3 → 2 if it exceeds 35.

## 11. Open questions
Q: Should a replaced drone count as destroyed for Daemons and rewards (open question 7 in the content design)?
Q: Is "launches every turn, max 2" too strong against the free nudge, given the drone's HP is also tier-banded?
Q: Should the Hangar launch land on the pointer's slice (hit guard immediately) or on the slice opposite to give one turn of warning?
