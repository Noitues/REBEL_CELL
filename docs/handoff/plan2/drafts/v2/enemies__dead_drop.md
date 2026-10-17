<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__dead_drop; status ok; tokens in 6959 cache-write 0 cache-read 32585 out 4886; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, the Perfect claim is false):** Kept the six sizes (6/4/5/5/6/4 = 30) and corrected the text. Cache (5) and Dose (5) both keep the W G P G W map. Neither Perfect rewards the player directly. I made the Dose Perfect meaningful: a Perfect on Dose resolves at a lower level, so the player has a reason to steer the enemy's needle there. This follows R10/R11 and adds no new system. See the layout notes in §2.
- **Issue 2 (BLOCKER, HP above budget):** Rebuilt HP at the band minima (28 / 34 / 44 / 56). The arithmetic is shown in §4 and gives HP at or below budget minus sustain at every tier. The drone soak is quantified.
- **Issue 3 (BLOCKER, sustain 1.4 vs 1.5, two defense sources):** Deleted the Cache BLOCK, so Stash SHIELD is the only defense and sustain source. Slice 2 becomes SHIM 6 FLAT. Sustain is derived per tier (0.2 × 12 % × HP). Stacking is resolved: it stacks to cap 15, and the Q is removed.
- **Issue 4 (MAJOR, drone HP contradiction):** Drone HP is FLAT 6 × the tier damage factor (6 / 8 / 10 / 13). The Q is removed.
- **Issue 5 (MAJOR, assumed echo_drone.tres and the Undock Q):** The drone is now authored in full in this draft (HP, wheel) instead of assumed from the file. The intake contribution is derived, not asserted. The Undock Q is dropped as speculative scope. The satellite wheel is flagged as an authoring field.
- **Issue 6 (MAJOR, the kill-the-drone path):** Made the plan explicit. With max_active 1 and a spawn every 2 turns, a kill buys one drone-free window. The fast path is shown: kill it on the turn it docks off the body's slice, or steer around it. The weak-player text no longer says steering is the only fix.
- **Issue 7 (NIT, Dose 10 %):** Corrected to 5/30 = 16.7 %.
- **Issue 8 (NIT, dead Perfect on Cache):** Cache is now a SHIM 6 and its Perfect has a purpose. See §2.
- **Critic Qs:** Stash stacking is decided (stacks to cap 15). The REPLACE-versus-destroyed question stays open as a Q. "Is one drone per 2 turns too slow" is answered in §1 and §3: the drone is a soak, not the damage.

---

# dead_drop: direct design

## 1. Identity & the one question

- **Class:** Normal, 1 phase, no enrage. Corporation: REBEL_CELL.
- **Layers:** L1-2 teaching and L3-4 filler. The same wheel can appear at L5-6 at T3-T4.
- **Concept:** a dead drop is a hidden stash. The enemy buries its damage behind a courier drone, and attacks aimed at the docked slice hit the drone first (GDD 2.7 bodyguard).
- **Distinct from siblings:** Mirror Script, Echo Process and Handler Proxy are mirror, copy and listener enemies. Dead Drop has no listeners. Its question is spatial.
- **The one question:** "Which slice is the courier on: do I pay a hit to clear it, or steer my pointer onto a slice it doesn't guard?"
- **The answer that shortens the fight:** the drone has 6 / 8 / 10 / 13 HP, so one decent hit kills it. A kill buys a drone-free window until the next spawn (every 2 turns). Do the work in that window, or steer around the drone. A player who clears the drone on the turn it docks off the body's slice, then bursts, finishes in 3 turns. A player who keeps hitting the drone slice never reaches the body and takes 5 or more.

## 2. Phase plan

One phase, no threshold. R3 does not apply to a last phase.

| Field | Value |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | none |
| Statuses | CORRUPTED from Dose (R9: a RAM tax, no damage) |
| Listeners | none |

**Layout (ticks 6+4+5+5+6+4 = 30, N12):**

| # | Slice | Ticks | Effect | Tick map |
|---|---|---|---|---|
| 0 | Stash | 6 | SHIELD, PERCENT 12 % of max HP, stacks to cap 15 | W W G G W W (no Perfect) |
| 1 | Pickup | 4 | SHIM 9, FLAT | W G G W (no Perfect) |
| 2 | Cache | 5 | SHIM 6, FLAT | W G P G W |
| 3 | Dose | 5 | Applies CORRUPTED to 1 random non-NULL player slice (FLAT 1); 0 damage | W G P G W |
| 4 | Handoff | 6 | SHIM 9, FLAT | W W G G W W (no Perfect) |
| 5 | Null | 4 | Nothing | W G G W |

**Where Perfects exist:** only Cache and Dose, both 5-tick slices. Pickup, Handoff and Stash have no Perfect, so the enemy's heaviest hits cannot be sharpened by a player nudge: they read G or W only. That is intended, since the question is the drone and not precision. The Perfect windows sit on the two lighter slices, so a player who nudges the enemy onto Cache or Dose Perfect gains nothing. Nothing on this enemy depends on it, and the preview shows it.

**Satellite (Echo Drone), authored here:**

| Field | Value |
|---|---|
| Spawn | every 2 turns (`every_n = 2`), `max_active = 1` (was 2) |
| First dock | slice 1 (Pickup); later spawns use next free clockwise (`dock_slot = -1`) |
| Replace | N13 `on_occupied = REPLACE`: a new drone replaces the old one, so it is always fresh |
| Drone HP | FLAT 6 × tier damage factor: 6 / 8 / 10 / 13 |
| Drone wheel | Shim 3 FLAT (×tier factor) / Null, authoring field to confirm in `echo_drone.tres` |
| Fixed | per R12, no one can nudge it |

**Transition:** none. The only event is a drone arriving every second turn.

## 3. Sustain and intake

**Sustain (one source only):** the Stash SHIELD, a lingering shield and not a heal. There is no BLOCK and no heal on this enemy.
- Landing odds: 6/30 = 0.2 per turn.
- Sustain per turn = 0.2 × 12 % × max HP:

| Tier | HP | Shield per landing | Sustain per turn | 30 % of reference dpt |
|---|---|---|---|---|
| T1 | 28 | 3.4 | 0.67 | 2.7 |
| T2 | 34 | 4.1 | 0.82 | 3.3 |
| T3 | 44 | 5.3 | 1.06 | 4.2 |
| T4 | 56 | 6.7 | 1.34 | 5.4 |

Every tier is well under the cap. Stacking is capped at 15 (shield_cap), and one Stash landing is at most 6.7, so the cap never binds on its own.

**Intake per turn** (the needle lands by slice size; slice damage is FLAT × tier factor):

| Slice | Chance | T1 damage |
|---|---|---|
| Pickup | 4/30 | 9 |
| Cache | 5/30 | 6 |
| Handoff | 6/30 | 9 |
| Stash, Dose, Null | 15/30 | 0 |

- T1 expected intake = (4 × 9 + 5 × 6 + 6 × 9) / 30 = 120 / 30 = **4.0 per turn**. T2 (×1.3) is 5.2, T3 (×1.69) is 6.8 and T4 (×2.2) is 8.8.
- The drone's Shim 3 adds little: it fires only when its host slice is read, about 4/30 × 3 = 0.4 at T1, and only while it lives.
- Intake is above 0 at every tier, which fixes the Dosage Dispenser failure.
- Dose lands 5/30 = 16.7 % per turn and corrupts one slice. Its cost is RAM (2×), so over a 3-4 turn fight it bites through nudges and cards, not HP.

## 4. HP by tier (R2 normal band)

Budget = reference dpt × 3.5 turns × 1 needle − sustain × 3.5, then reduced for the drone soak. Soak: the drone docks on the read slice in roughly 1 turn in 4, and one such hit lands on the drone and not the body. I deduct one expected soaked hit of about 0.4 of that turn's dpt.

| Tier | dpt | Raw budget | Sustain deduction | Soak deduction | Budget | HP chosen (band) |
|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 0.67 × 3.5 = 2.3 | ≈ 3.5 | 25.7 | **28** (28-36) |
| T2 | 11 | 38.5 | 0.82 × 3.5 = 2.9 | ≈ 4.3 | 31.3 | **34** (34-44) |
| T3 | 14 | 49 | 1.06 × 3.5 = 3.7 | ≈ 5.5 | 39.8 | **44** (44-56) |
| T4 | 18 | 63 | 1.34 × 3.5 = 4.7 | ≈ 7.0 | 51.3 | **56** (56-70) |

The budget falls below the band minimum at every tier, so I take the band minimum. The band is the floor R2 allows, and HP cannot go lower and stay valid. The remaining 2-5 HP overshoot means a reference player takes about 3.8-4.4 turns. That is the top of the 3-4 target, and I accept it because the drone window is the designed shortcut. Today is 48 at every tier.

## 5. Enrage

None (R4, normal). Intake of 4.0 to 8.8 per turn keeps the fight from stalling.

## 6. Buffs and counter Exploits

Not applicable (normal enemy).

## 7. Counterplay

- **Good player:**
  - Reads which slice the drone guards in the preview.
  - Spends the free nudge so the pointer reads an unguarded slice. A 1-tick nudge turns a guarded read into an open one.
  - Clears the drone with one hit on the turn it docks off the body's slice, then bursts the body in the open window before the next spawn.
  - Keeps CORRUPTED low. Dose is 16.7 % per turn, so one Cleanse covers a fight.
- **Weak player:**
  - Aims every hit at the drone slice. The body stays untouched and the fight runs past 5 turns.
  - Kills the drone, then expects a long window. REPLACE respawns it every 2 turns.
  - Ignores Dose, then pays 2× RAM and runs short for nudges.
  - Spends hits on Stash while a shield stacks to 15.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| Variable slice sizes (6/4/5/5/6/4) | N12 | Yes: six 5-tick slices. Loses the no-Perfect windows. |
| PERCENT shield | N1 | Yes: FLAT 4 on slice 0. It does not scale with HP. |
| Flat amounts × tier factor, hp_by_tier | N2 | Yes: one `hp` and the old multiplier. |
| Fixed satellite and REPLACE | N13 | Yes: `max_active 1` without REPLACE means no spawn while one lives. The drone lasts longer. |
| Corruption as a RAM cost | N9 | Until N9 ships, Dose self-damages. |
| Defense trio names | N14 | Names only. |

## 9. Delta vs today

- **Kept:** id, corporation, the six-slice concept, Dose, the Echo Drone every second turn, cycle_reward 15.
- **Changed:**
  - HP 48 becomes 28 / 34 / 44 / 56.
  - Two sandbox_5 shield slices become one 6-tick percent Stash. The other becomes SHIM 6 (Cache). This removes the second defense source.
  - The Shim 9 slices become 4 and 6 ticks.
  - Null shrinks to 4 ticks.
  - `max_active` goes from 2 to 1.
  - Dose stops dealing damage (R9) and becomes a RAM tax.
- **heat_effects:** none exist, so nothing to keep or retire.
- **Description:** "Buries its output behind a courier drone."

## 10. Predicted sim check

No baseline row exists, so this is an estimate from the wheel.

- **Turns:** about 3.8 for a reference player, 3 for a skilled one, 5 or more for a weak one.
- **Win %:** T1 about 98 %, T2 about 96 %, T3 about 92 %, T4 about 85 %. Intake runs 4.0 to 8.8 per turn, so a 4-turn fight costs 16 to 35 HP. That is fine at T1-T2 and tight at T4.
- **Why:** sustain is about 1 per turn and intake is real, so it cannot stall. The drone is the only length risk, and `max_active = 1` bounds it.
- **Compared with the baseline:** far shorter than Account Manager (20.7 turns) and well short of Care Swarm's lethality (43 HP lost at T3).

Q: Does a drone replaced by REPLACE count as destroyed for Daemons and rewards?
Q: Is the drone wheel in `echo_drone.tres` really Shim 3 / Null, or does it need re-authoring?
Q: With intake at 4.0 at T1, is that too lethal for a teaching enemy, or should Pickup drop to SHIM 7?
