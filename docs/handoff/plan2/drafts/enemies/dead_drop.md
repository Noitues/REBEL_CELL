<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__dead_drop; status ok; tokens in 15873 cache-write 0 cache-read 32007 out 4092; cost $0.040. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# dead_drop: direct design

## 1. Identity & the one question

- **Class:** Normal, 1 phase, no enrage. Corporation: REBEL_CELL.
- **Layers:** L1-2 teaching and L3-4 filler. The satellite is a plain bodyguard and has no listeners. It can reach L5-6 at T3-T4 with the same wheel.
- **Concept:** a dead drop is a hidden stash, so the enemy buries its output behind a courier. The Echo Drone rides a slice, and attacks aimed at that slice hit the drone instead.
- **Distinction from siblings:** Mirror Script, Echo Process and Handler Proxy are mirror, copy and listener enemies. Dead Drop uses none of those. Its question is spatial, about satellites and bodyguards.
- **The one question:** "Which slice is the courier on, and do I hit the drone or steer around it?" It asks a different thing from the other normals.
- **The answer that shortens the fight:** the drone has few HP. Kill it with one cheap hit, or nudge so your pointer reads a slice the drone isn't docked on. A player who kills the drone, then bursts the body in the open window, finishes in 3 turns. A player who ignores the drone spends their hits on it every turn and takes 5+.

## 2. Phase plan

One phase, no threshold, no HP floor (R3 does not apply to a last phase).

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | none |
| Statuses | CORRUPTED from Dose (R9: a RAM tax, no damage) |
| Listeners | none |

**Layout (ticks sum 30, needs N12):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 0 | Stash | 6 | SHIELD, PERCENT 12 % of max HP (see §3). Tick map W W G G W W, no Perfect. Cap 15 stays. |
| 1 | Pickup | 4 | SHIM 9, FLAT. Map W G G W, no Perfect. |
| 2 | Cache | 5 | SANDBOX-as-shield becomes BLOCK 5, FLAT. Map W G P G W. |
| 3 | Dose | 5 | Applies CORRUPTED to 1 random non-NULL player slice. FLAT 1 slice. 0 damage. |
| 4 | Handoff | 6 | SHIM 9, FLAT, ×1.0. Map W W G G W W. |
| 5 | Null | 4 | Nothing. |

Today's two slices called sandbox_5 are shields. Under R13 the SANDBOX name means "negate a whole attack", so I reassign them. Slice 0 is the lingering SHIELD (small, percent mode), and slice 2 becomes a short BLOCK.

**Why these sizes:** the Perfect window is narrow on the dangerous slices. Pickup is 4 ticks with no Perfect, and Handoff has none either, so the player's steering matters less than what is docked. The only Perfect on the enemy wheel is on Cache, a defensive slice. Hitting it Perfect does nothing for the player, so there is no reward for precision there.

**Satellite (Echo Drone, existing):**

| Field | Value |
|---|---|
| Spawn | every 2 turns (trigger = 2, every_n = 2), max_active 1 (was 2) |
| Dock | slice 1 (Pickup) is the first dock. Later spawns use `dock_slot = -1` (next free clockwise). |
| Replace | with N13 `on_occupied = REPLACE`. With max_active 1 a new drone replaces the old one, so the drone is always fresh. |
| Drone HP | 6 (PERCENT of nothing: a flat amount, ×tier damage factor at T2+, per R2) |
| Drone wheel | Shim 3 / Null (exists in echo_drone.tres; I have not seen its file, so I assume it) |
| Fixed | per R12 the drone cannot be nudged by anyone |

**Transition:** none. The wheel never changes. The drone arriving every second turn is the only event.

## 3. Sustain and intake

**Sustain (one source):** Stash SHIELD 12 % of max HP.
- At the T3 mid-band HP of 50, 12 % is 6 shield, and that lands on 1 of 6 slices.
- Expected landing frequency is about 1 in 6 turns by slice weight (6/30 ticks = 0.2 per turn).
- Expected sustain: 0.2 × 6 = 1.2 per turn.
- Cap: 30 % of reference damage at T3 (14 × 0.3 = 4.2). 1.2 is well inside it. At T1: 12 % of 32 = 4, × 0.2 = 0.8 per turn against 2.7 allowed.
- Block on Cache (5, flat) is a second defensive source. I count it as a defense, not sustain, because it expires. It does not heal and is not in the 30 % cap. Heal total is 0.

**Intake per turn at the reference player (must be > 0):**
Needle at tick 0 after a random respin lands on a slice weighted by size.

| Slice | Chance | Damage at T1 |
|---|---|---|
| Pickup 9 | 4/30 | 9 |
| Handoff 9 | 6/30 | 9 |
| Others | 20/30 | 0 (Dose adds a RAM tax) |

- Expected intake = 10/30 × 9 = **3.0 per turn at T1**. At T3 (×1.69) it is 5.1. At T4 (×2.2) it is 6.6.
- The drone adds Shim 3 on its own wheel, about 0.5 per turn once docked.
- That is above 0 and fixes the Dosage Dispenser failure. It is lower than the Genome Core P1 intake of 2-4 only at T1, which is deliberate for a teaching enemy.
- Dose lands 3/30 = 10 % per turn and corrupts one slice. This is a RAM cost, so the player feels it more over 4 turns than as damage.

## 4. HP by tier (R2 normal band)

Phase budget = reference_dpt × 3.5 turns × needles hit, minus sustain × 3.5.

| Tier | dpt | Budget | Sustain deduction | HP chosen | Band |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 0.8 × 3.5 = 2.8 | **30** | 28-36 |
| T2 | 11 | 38.5 | 1.0 × 3.5 = 3.5 | **36** | 34-44 |
| T3 | 14 | 49 | 1.2 × 3.5 = 4.2 | **46** | 44-56 |
| T4 | 18 | 63 | 1.5 × 3.5 = 5.3 | **58** | 56-70 |

(HP is trimmed below the budget to account for the drone's pointer-rule soak, since hits that land on the drone do not reach the body.) Today is 48 at all tiers, which fits T3 and is too high for T1.

**Drone HP** is separate and small, so killing it costs one decent hit. Its HP does not count against the budget.

## 5. Enrage

None (R4, normal). The drone cycle limits stalling because the enemy does 3.0 damage per turn at T1.

## 6. Buffs and counter Exploits

Not applicable (normal enemy).

## 7. Counterplay

- **Good player:**
  - Reads the drone's slice in the preview.
  - Spends the free nudge to move the pointer onto Handoff or Pickup. A 1-tick nudge turns a drone-guarded read into an open one.
  - Uses one cheap SHIM on the drone when it docks on the slice they must hit anyway, then bursts the body on the next turn.
  - Keeps CORRUPTED low. Dose is rare (10 % per turn), so a single Cleanse is enough.
- **Weak player:**
  - Fires every Shim at the drone slice and loses the damage to the bodyguard, then wonders why the body is still at 40 HP.
  - Ignores Dose, then pays 2× RAM on a corrupted slice and runs short of RAM for nudges.
  - Lets Stash SHIELD sit and wastes a turn of damage on it.
  - Assumes the drone can be moved. It can't (R12), so steering the player's own pointer is the only fix.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| Variable slice sizes (6/4/5/5/6/4) | N12 | Yes: the six slices at 5 ticks. Loses the no-Perfect windows. |
| Amount mode PERCENT on shield | N1 | Yes: FLAT 5 on slice 0. Works but does not scale with HP. |
| Flat amounts × tier damage factor | N2 | Needed for drone HP and damage at T2+. The fallback is today's 1.3^(t-1) multiplier. |
| Satellite replacement, fixed satellite | N13 | Yes: max_active 1 without REPLACE just means no spawn while one is alive. This is slightly weaker, and the drone lives longer. |
| Corruption as a RAM cost | N9 | Dose is harmless until N9 ships (today it self-damages). |
| Defense trio naming | N14 | Names only. |
| hp_by_tier | N2 | Yes: author one `hp` and use the old multiplier. |

## 9. Delta vs today

- **Kept:** id, corporation, the six-slice wheel concept, Dose, the Echo Drone spawn every second turn, cycle_reward 15.
- **Changed:**
  - HP 48 becomes 30 / 36 / 46 / 58.
  - The two Sandbox 5 slices become one SHIELD at 12 % (6 ticks) and one BLOCK 5.
  - Shim 9 stays on two slices but they are 4 and 6 ticks, not two 5-tick slices.
  - Null shrinks to 4 ticks.
  - max_active goes from 2 to 1 (two drones soak too many hits and cut the fight's intake to near 0).
  - Dose stops dealing damage (R9) and becomes a RAM tax.
- **heat_effects:** none exist on this file, so nothing to keep or retire.
- **Description** should read: "Buries its output behind a courier drone."

## 10. Predicted sim check

No baseline row exists, so this is an estimate from the wheel alone.

- **Turns:** about 3.5 at the reference player. A skilled player kills the drone in 1 turn and the body in 2-3, giving 3 turns. A weak player takes 5.
- **Win %:** T1 about 98 %, T2 about 96 %, T3 about 92 %, T4 about 85 %. Intake rises 3.0 to 6.6 per turn, so a 4-turn fight costs the player 12 to 26 HP, which is survivable at T1-T3 and tighter at T4.
- **Why:** low sustain (about 1 per turn) and a real intake (3 to 6.6) keep it from being a stall. The drone is the only long-fight risk, and `max_active = 1` bounds it.
- **Compared with Solace baselines:** it is far shorter than Account Manager (20.7 turns) and nowhere near Care Swarm's lethality (43 HP lost at T3).

Q: Does the drone's HP use the tier damage factor, or is it a fixed 6 so a single Shim 9 always kills it?
Q: Should Stash's SHIELD stack on top of an existing shield up to the cap of 15, or refresh? I assumed it stacks.
Q: Is `echo_drone.tres` really Shim 3 / Null? I did not have its file and assumed it from the brief's description.
Q: If R12 makes the drone un-nudgeable, should Undock exist as a player card in the REBEL_CELL pool so this enemy has a hard counter?
