<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__care_swarm; status ok; tokens in 6894 cache-write 0 cache-read 32585 out 10097; cost $0.061. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, core HP below band, drone HP smuggled into the band):** changed. The core's `hp_by_tier` is now inside the R2 band on its own (28 / 34 / 44 / 56). The "band includes satellites" line is deleted. Drone HP is budgeted separately, as an explicit guard tax (§4).
- **Issue 2 (BLOCKER, drone HP unscaled, flat amounts inconsistent):** changed in two parts.
  - Drone HP is HP, so it comes from an authored tier table (4 / 5 / 6 / 8), not a damage multiplier. I did not take the critic's 4 / 5 / 7 / 9 (damage factor × 4), because R2 says HP is by band and not by multiplier. The values are about 0.45 turns of reference dpt each.
  - Every flat amount (Cover block, Sting, Pulse, drone Shim) now has an explicit × tier-factor column, so §2 and §3 use the same numbers.
- **Issue 3 (MAJOR, intake double-count):** changed. The intake is recomputed per slot: a drone's Shim resolves with its host slot and is added to it. Result: 2.5 / 3.5 / 4.0 / 5.5 with drones alive (§3).
- **Issue 4 (MAJOR, Tend mis-tagged as N6, "zero sustain" misleading):**
  - Tend is deleted.
  - Its replacement (Frayed) is tagged "NEW: satellite-destroyed trigger" (no N#), with a data-only fallback.
  - The Cover block is now counted in §3 as defense, not heal. Sustain is stated as 0 heal.
- **Issue 5 (MAJOR, dominated play, kills never right):** changed, following the critic's fix 5. Killing a drone now weakens the core's Cover slices by 2 × tier factor. A kill pays twice: it removes the drone's Shim and removes some of the core's defense. The drone is no longer a pure soak.
- **Issue 6 (MAJOR, unsourced baseline, missing tables):**
  - Baseline turn numbers are removed.
  - §2 now has a needle table with tick positions and a hub-rule table.
  - Cited baseline facts are limited to those in the brief (0 % win at T4, 43 HP lost at T3).
- **Issue 7 (NIT, N13 fallback wording):** reworded. `dock_slot` fixes only the placement, not immobility.
- **Kept, because the critic marked them strong:**
  - Both HOTFIX slices and the respawning third drone are gone.
  - One question: target selection through bodyguards.
  - Drones fixed to the attacking slices.
  - Enrage off.
  - Layout summing to 30.
- **Critic's Q on a 4-tick no-Perfect Pulse:** not adopted. It would add N12 (scope). It is listed as a Q.
- **No ruling conflicts.**

# care_swarm: direct design

## 1. Identity & the one question
- **Class and corporation:** Normal, 1 phase, 3–4 turns, no enrage (R1, R4). Solace.
- **Layers:** L1–2 teaches bodyguards. L5–6 adds pressure through the intake figures in §3.
- **The one question:** *"Your pointer hits whatever sits there. Is it the core or a drone, and can one nudge move your hit onto the core without moving the Pulse onto you?"*
- **Which answer shortens the fight:**
  - Steer onto an unguarded, unblocked slice (slot 3 or 5).
  - Kill a drone when the kill pays: it removes a Shim and weakens Cover.
  - Do not spend hits on a drone that is not about to matter.
- **Distinct from other Solace normals:** it is the only one whose question is target selection through bodyguards.
- **What today's fight gets wrong:**
  - Two Hotfix slices heal the core.
  - Three drones dock at random and respawn, so the fight is a pile of soak.
  - Baseline: 0 % win at T4, 43 HP lost at T3.

## 2. Phase plan (single phase, no threshold, no floor)

**Needle**

| Needle | Tick | Behavior |
|---|---|---|
| Enemy | 0 | FIXED. One pointer. |

**Wheel (size_ticks 5 × 6 = 30)**

| Slot | Ticks | Slice | Base | Scaled (T1 / T2 / T3 / T4, ×1.0 / 1.3 / 1.69 / 2.2, rounded) |
|---|---|---|---|---|
| 0 | 5 | Cover (BLOCK, FLAT) | 4 | 4 / 5 / 7 / 9 |
| 1 | 5 | Sting (SHIM, FLAT) | 3 | 3 / 4 / 5 / 7 |
| 2 | 5 | Cover (BLOCK, FLAT) | 4 | 4 / 5 / 7 / 9 |
| 3 | 5 | Sting (SHIM, FLAT) | 3 | 3 / 4 / 5 / 7 |
| 4 | 5 | Pulse (SHIM, FLAT; the one real attack) | 5 | 5 / 7 / 8 / 11 |
| 5 | 5 | Null | n/a | n/a |

The 5-tick slices are uniform on purpose. The question is the bodyguard, not the Perfect window.

**Satellites (Care Drones)**
- Two fixed drones, docked at combat start on **slot 1 and slot 4**, the attacking slices.
- Each drone has one mini-wheel slice: SHIM 2 (FLAT, × tier factor: 2 / 3 / 3 / 4). It resolves after its host.
- If your pointer rests on a guarded slice, the drone takes the hit (bodyguard).
- Drones do not respawn.
- Drone `hp_by_tier` is 4 / 5 / 6 / 8 (§4).

**Hub rule**

| Rule | Trigger | Effect |
|---|---|---|
| Frayed | NEW: satellite-destroyed trigger | When a drone dies, all Cover slices lose 2 BLOCK (FLAT × tier factor, floor 0) for the rest of combat. |

**Statuses, parasites, listeners:** none.

**Transition:** none (1 phase).

**The loop**
- Slots 3 and 5 are unguarded and unblocked. Slots 0 and 2 are blocked. Slots 1 and 4 are guarded.
- A nudge turns the wheel under both pointers. Moving your hit off a guard also moves what the enemy resolves, so the preview shows both.
- Three answers:
  - Nudge onto slot 3 or 5.
  - Kill a drone to cut Cover and a Shim.
  - Accept the soak and race.

## 3. Sustain and intake
- **Sustain:** 0 heal and no other sustain source. Cover is defense (BLOCK, expires), not sustain, so the 30 % cap (30 % × 11 = 3.3 per turn) is not in play. Frayed only weakens Cover.
- **Intake per turn at the reference player.** The enemy pointer is on a uniform slot after the respin, so each slot has probability 1/6. Drone Shim adds to its host slot's damage. Before defense:

| Tier | Slot 1 (Sting + drone) | Slot 3 | Slot 4 (Pulse + drone) | Sum / 6 (drones alive) | Drones dead (drone terms removed) |
|---|---|---|---|---|---|
| T1 | 3+2 = 5 | 3 | 5+2 = 7 | 15 / 6 = **2.5** | 11 / 6 = 1.8 |
| T2 | 4+3 = 7 | 4 | 7+3 = 10 | 21 / 6 = **3.5** | 15 / 6 = 2.5 |
| T3 | 5+3 = 8 | 5 | 8+3 = 11 | 24 / 6 = **4.0** | 18 / 6 = 3.0 |
| T4 | 7+4 = 11 | 7 | 11+4 = 15 | 33 / 6 = **5.5** | 25 / 6 = 4.2 |

Intake is above 0 at every tier. The Pulse slot is a constant threat. At T3 the v1 baseline was about 6.9 per turn.

## 4. HP by tier
**R2 normal band:** T1 28–36, T2 34–44, T3 44–56, T4 56–70.

**Core HP.** The core is the enemy's HP and sits in the band on its own. Budget = reference dpt × 3.5 turns (one enemy needle, sustain 0).

| Tier | dpt | Budget (dpt × 3.5) | Core `hp_by_tier` | Turns to kill core at ref dpt |
|---|---|---|---|---|
| T1 | 9 | 31.5 | **28** | 3.1 |
| T2 | 11 | 38.5 | **34** | 3.1 |
| T3 | 14 | 49 | **44** | 3.1 |
| T4 | 18 | 63 | **56** | 3.1 |

The core sits at the bottom of the band, 3.5–7 HP under budget, which is slack for the bodyguard tax.

**Guard tax.** Drones are guards, not part of the band. Their HP is authored as `hp_by_tier` on the satellite (N2): 4 / 5 / 6 / 8, about 0.45 turns of reference dpt each (4 / 9, 5 / 11, 6 / 14, 8 / 18).
- Killing both costs about 0.9 turns of reference damage.
- A player who steers kills neither.
- A player who tries to kill both ends the fight at about 3.1 + 0.9 = 4.0 turns, which is the top of the target.
- A player who never nudges loses about a third of their hits to drones (slots 1, 4) and a share to Cover on 0 and 2. Their fight runs over 4 turns. That is intended for a weak player.

## 5. Enrage
**Off** (Normal default, R4). The fight is 3–4 turns and has no heal.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Reads guarded slots 1 and 4 in the preview.
  - Uses the free nudge to put the hit on slot 3 or 5 and checks that the Pulse is not at the same time landing on them.
  - Kills a drone when it also guts Cover. A SWEEP or multi-hit card clears both in one resolve.
  - Defends the Pulse turn: SHIELD, or SANDBOX if the Pulse and a drone Shim are in one resolution.
- **Weak player:**
  - Feeds hits into the drones one by one and then meets a core with only Cover to chew through, or ignores Frayed and wastes the kill.
  - Never nudges, so about a third of hits are soaked.
  - Misses the Pulse warning in the preview.
  - Runs 5+ turns and loses HP.

## 8. Systems needed
- **N1** (amount modes, flat × tier factor). Data-only fallback: plain flat `base_output` as today.
- **N2** (`hp_by_tier` for the core and the drones). Fallback: single `hp`, with the tier values hand-set per scale.
- **N13** (fixed satellites). Fallback: `dock_slot` 1 and 4 in `SatelliteSpawnData`, which already supports `dock_slot ≥ 0`. That fixes placement only, so drones stay nudgeable until N13.
- **NEW: satellite-destroyed trigger** (for Frayed, no N#, not covered by N6). Fallback: drop Frayed. Then drones matter only through their Shim, and the "kill" answer is weak, so the fight reduces to steering.
- **N11 / N12:** not needed.

## 9. Delta vs today
- **Removed:** both HOTFIX slices, the third drone, random docking, per-turn respawn.
- **Changed:**
  - HP 25 → core 28 / 34 / 44 / 56 by tier, plus drone HP 4 / 5 / 6 / 8.
  - Layout: Defrag, Hotfix, Defrag, Hotfix, Shim, Null → Cover, Sting, Cover, Sting, Pulse, Null.
  - Drone wheel (Shim 3, Shim 3, Defrag 2) → one Shim 2.
  - New hub rule Frayed.
- **Kept:** the 6 × 5 layout, `cycle_reward` 15, the `care_drone` resource (retuned), the single pointer at tick 0.
- **`heat_effects`:** none today, none added.

## 10. Predicted sim check
Mean turns about 3.4 at T1–T2 and 3.8 at T3–T4. Turn counts and win rates are estimates until the sim runs.

| Tier | Win % | Why |
|---|---|---|
| T1 | ~100 | Intake about 2.5 per turn |
| T2 | ~100 | About 3.5 per turn |
| T3 | ≥ 92 | About 4.0 per turn undefended, against 6.9 today with no heals |
| T4 | ≥ 85 | About 5.5 per turn, about 19 HP over 3.5 turns undefended, against 0 % win today |

The big win is removing both heals and the respawning third drone.

## 11. Q:
- Q: Should the core's HP (band) and a guard tax be judged separately for all satellite-bearing enemies, or should R2 define a pool rule that counts satellites?
- Q: Does a satellite-destroyed trigger belong under N6 (extending its trigger list) or does it need its own N#?
- Q: Does a drone kill count as "enemy destroyed" for Daemons and rewards (V2 open question 7)?
- Q: Is the fixed drone placement too static for a bot that never nudges?
- Q: Should the Pulse become a 4-tick slice with no Perfect (N12) to give nudging a second payoff?
