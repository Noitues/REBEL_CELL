<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__care_swarm; status ok; tokens in 17495 cache-write 0 cache-read 32007 out 3740; cost $0.039. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# care_swarm: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3–4 turns, no enrage (R1, R4).
- **Corporation:** Solace.
- **Layers:** L1–2 teaching and L5–6 pressure. At L1–2 it teaches that bodyguards soak your pointer hit, and that a nudge can steer your needle to the core.
- **The one question:** *"Your pointer hits whatever sits at it. Is that the core or a drone, and can you steer onto the core?"*
- **What shortens the fight:**
  - Steer the player needle onto the slice that carries no live drone, or onto a drone-free core slice.
  - Kill drones with SWEEP or multi-hit.
  - Stop spending hits on drones that heal or shield for the core.
- **Distinct from the other Solace normals:**
  - Triage Unit is a healer, Dosage Dispenser is a corruptor, Billing Daemon and Collections Agent are RAM and damage, Compliance Officer is resistance.
  - The Swarm is the only one whose question is *target selection through bodyguards*.
- **What today's fight gets wrong:**
  - Defrag, Hotfix, Defrag, Hotfix, Shim, Null means two heals and two blocks on a 25 HP body.
  - Three drones are docked at random each turn, so the fight is a pile of soak.
  - Baseline: 0 % win at T4 and 43 HP lost at T3.
  - Intake is 6.9 per turn at T3, mostly from the drones' two Shim 3 slices (the satellites keep attacking after you kill the host slice).

## 2. Phase plan (single phase, no threshold, no floor)

**Needles:** 1, at tick 0, fixed, no pointer behavior. Enemy wheel: **6 slices, 5 ticks each (size_ticks 5)**. Sizes sum to 30. A uniform layout is fine here; the question is the bodyguard, not the Perfect window.

| Slot | Ticks | Slice | Effect (FLAT unless noted) |
|---|---|---|---|
| 0 | 5 | Cover | BLOCK 4 (× tier damage factor, R2) |
| 1 | 5 | Sting | SHIM 3 |
| 2 | 5 | Cover | BLOCK 4 |
| 3 | 5 | Sting | SHIM 3 |
| 4 | 5 | Pulse | SHIM 5 to the player (the one real attack) |
| 5 | 5 | Null | nothing |

- **No HOTFIX slices.** The Swarm no longer heals from its wheel; its sustain is zero.
- **Satellites (Care Drones):**
  - 2 fixed drones, 4 HP each (R12), docked at combat start on **slot 1 (Sting) and slot 4 (Pulse)**, the attacking slices. Fixed placement replaces random `dock_slot = -1`, so the fight is readable and the preview is static.
  - Each drone has a 1-slice mini-wheel: SHIM 2 (resolves after its host).
  - If your pointer rests on a guarded slice, the drone eats the hit (bodyguard rule).
  - Drones **don't respawn**. `max_active = 2`, trigger once at combat start only (spawn trigger 1, `every_n` unused).
- **Swarm rule (hub, passive):** *Tend.* When a drone dies, the core gains **BLOCK 4 (FLAT × tier factor)**, not a heal. It is a block, so it expires, and it punishes killing drones in the wrong order without adding sustain.
- **Statuses, parasites and listeners:** none.
- **Transition:** none (1 phase).

**The loop the wheel creates:**
- Core slots 0, 2, 3 and 5 are unguarded.
- The core is hit when your pointer lands there.
- The two guarded attack slices are the ones you want to cut, because a hit that lands on the Sting or Pulse slice goes to a drone.
- You have three answers:
  1. Nudge so your pointer is on an unguarded slot.
  2. Pay for the drone kill so the attack slice loses its escort.
  3. Accept the drone's soak and race.

## 3. Sustain and intake
- **Sustain:** 0 per turn. The Tend rule is BLOCK, not heal, so it doesn't count against the 30 % cap (30 % of 11 = 3.3 per turn). Even if it did, 4 BLOCK on a drone death happens at most twice per fight = 8 total over about 3.5 turns, about 2.3 per turn, which is under the cap.
- **Intake per turn at the reference player** (T3: factor 1.69, wheel pointer on a uniformly random slot as the baseline for random respin):
  - Sting 3 × 1.69 ≈ 5 → 2 slots; Pulse 5 × 1.69 ≈ 8; drone Shim 2 ≈ 3 each.
  - Expected unblocked, no steering: (2 × 5 + 8) / 6 ≈ 3.0 core damage, plus drones' resolves roughly (2 × 3 × P(host resolves)) ≈ 2 × 3 × 2/6 ≈ 1.
  - ≈ **4.0 per turn** at T3 before defense, against 6.91 today. At T1: ≈ 2.4. At T4 (2.2): ≈ 5.2.
  - Always above 0, since the Pulse slot plus drones is a constant threat.

## 4. HP by tier
R2 normal band: T1 28–36, T2 34–44, T3 44–56, T4 56–70.

**Phase budget:** reference_dpt × 3.5 turns × needles-landed. One enemy needle means the player's single hit lands once per damaging action. Two drones (4 HP each) soak real hits, so the drones count as part of the HP pool. Minus sustain = 0.

| Tier | dpt | Budget (dpt × 3.5) | Drone HP | hp_by_tier (core) |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 8 total | **26** (+8 = 34 effective, in 28–36) |
| T2 | 11 | 38.5 | 8 | **32** (+8 = 40, in 34–44) |
| T3 | 14 | 49 | 8 | **42** (+8 = 50, in 44–56) |
| T4 | 18 | 63 | 8 | **54** (+8 = 62, in 56–70) |

Drone HP is a flat 4 each (R2: flat amounts scale, but I choose to keep drone HP unscaled so its 1-hit-kill threshold stays readable; this is a Q below). Cores sit slightly under the band, but the band includes the satellites' HP.

## 5. Enrage
**Off** (Normal class default, R4). The fight is 3–4 turns and the Swarm has no sustain, so nothing can stall.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Reads the guarded slots 1 and 4. Uses the free nudge (or a 1-RAM nudge) to move the player pointer off a guarded slice.
  - Takes the core hit on an unguarded slot.
  - Kills drones only when the drone's slice is about to resolve (cutting the incoming Shim 2 and Tend's BLOCK 4 together).
  - Brings a SWEEP or multi-hit card for both drones in one resolve.
  - Defends the Pulse: SHIELD or SANDBOX on the turn Slot 4 is at the pointer.
- **Weak player:**
  - Spends every hit on drones one at a time, so the core survives with a fresh BLOCK 4 from each Tend.
  - Ignores the preview line showing the Pulse about to land.
  - The fight runs to 5–6 turns and costs HP.

## 8. Systems needed
- **N1** (amount modes, flat × tier damage factor for the BLOCK): data-only fallback is a plain `base_output` (today's behavior is a flat × scale).
- **N2** (`hp_by_tier`): fallback is a single `hp` with a scale; I recommend authoring `hp_by_tier` once N2 lands.
- **N13** (fixed satellites): fallback is `dock_slot` set to 1 and 4 in `SatelliteSpawnData`, which the existing spawn data already supports (dock_slot ≥ 0). Drones may still be nudged until N13.
- **N6** (listener, for Tend): fallback is none. A drone-death BLOCK needs an on-satellite-destroyed hook, so without it, drop Tend and make the cores' Cover slices BLOCK 6 instead.
- **N11/N12:** not needed.

## 9. Delta vs today
- **Removed:**
  - Both HOTFIX slices.
  - The third drone.
  - Random docking.
  - Respawning each turn.
- **Changed:**
  - HP 25 → 26 / 32 / 42 / 54 by tier.
  - Layout: Defrag, Hotfix, Defrag, Hotfix, Shim, Null → Cover, Sting, Cover, Sting, Pulse, Null.
  - Drone wheel: Shim 3, Shim 3, Defrag 2 → one Shim 2.
- **Kept:** the 6 × 5 layout, `cycle_reward` 15, the care_drone resource (retuned), the single pointer at tick 0.
- **`heat_effects`:** none today, none added.

## 10. Predicted sim check
Mean turns about 3.4 (T1–T2) and 3.8 (T3–T4); the baseline is 3.0, 4.2, 6.5 and 6.5.

| Tier | Win % | Why |
|---|---|---|
| T1 | ~100 | Intake about 2.4 per turn over 3 turns |
| T2 | ~100 | About 3 per turn |
| T3 | ≥ 92 | Intake falls from 6.9 to about 4.0 with no heals |
| T4 | ≥ 85 | About 5.2 per turn × 4 turns ≈ 21 HP, versus 60 today (0 % win) |

The big win is removing both heals and the respawning third drone.

## 11. Q:
- Q: Should drone HP scale with tier (flat 4, or × damage factor) so SWEEP doesn't trivialise T1 and T4 alike?
- Q: Is a Tend BLOCK on drone death worth N6, or do we drop it for simplicity?
- Q: Do fixed drones on the two attack slices make the fight too static when the player never nudges (bot skill)?
- Q: Does a drone kill count as an "enemy destroyed" for Daemons and rewards (R12 open question 7)?
- Q: Should Pulse become a PERCENT-of-player-HP hit, or stay FLAT?
