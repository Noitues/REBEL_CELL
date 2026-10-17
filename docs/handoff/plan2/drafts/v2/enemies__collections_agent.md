<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__collections_agent; status ok; tokens in 6225 cache-write 0 cache-read 32585 out 3549; cost $0.027. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Critic 1 (BLOCKER, drone guards the harmless slice) -> fixed.** The Collector Drone now docks on **Overflow** (14 base damage), so the guard protects the collector from nothing and shields you from nothing. Wait, correction of the logic: a bodyguard absorbs *your* pointer hits aimed at that slice. While the needle reads Overflow, your hits go to the drone, so the collector is untouchable on its most dangerous turn. This gives a real choice: kill the drone (slow), or steer the needle off Overflow (fast). §1, §2, §7, §9 rewritten. The 15-tick spin remark was checked: Null (idx 1) and Overflow (idx 4) are 3 slices = 15 ticks apart, so the claim holds, but I reworded it to "opposite", not "adjacent".
- **Critic 2 (BLOCKER, block conflated with sustain) -> fixed.** §3 now says sustain = 0 HP of heal. Defrag BLOCK 6 is defense, listed separately, and the drone's wheel is not counted. The 30 % cap is stated as satisfied trivially.
- **Critic 3 (MAJOR, invented +4 drone allowance, block subtracted) -> fixed.** The budget is now dpt × 3.5 with no deductions. Values are the same: [32, 38, 48, 62].
- **Critic 4 (MAJOR, base-value labeling) -> fixed.** The table is headed "T1 base × `enemy_damage_by_tier`". The Q on Dose scaling is dropped (R2: flat enemy amounts always scale).
- **Critic 5 (MAJOR, satellite details) -> fixed.** Re-dock is "never" everywhere. Drone HP is tagged as a new field (`hp_by_tier` on the satellite spawn data, N2). The replacement and fixed rules are tagged N13.
- **Critic 6 (MAJOR, sim sources) -> fixed.** The baseline figures are marked as quoted from my v1 and unverified; the T4 win claim is lowered to a range with the reason.
- **Critic 7 (NIT, nudge advice) -> fixed.** §7 now says to nudge off the Overflow's Perfect tick onto WEAK (7 base damage), or off the slice entirely.
- **Critic Q on random CORRUPTED pick -> kept, because** it is a real determinism question; moved to Q (listed below).

# collections_agent: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, Solace. L1-2: the first fight where a slice is guarded (teaching). L5-6 at T2+: pressure.
- **Concept:** a debt collector with a bodyguard standing in front of its big hit.
- **The one question:** *"Do you spend your hits on the drone to open its Overflow, or steer the needle away from the Overflow?"* While the needle reads Overflow, your pointer attacks hit the drone, so the collector can't be damaged on its most dangerous turn.
- **Answer that shortens the fight:** steer the needle off Overflow (nudge, spin card) and hit the collector on the other five slices. Killing the drone first is the slow answer.
- **Distinct from siblings:** Billing Daemon (RAM economy), Care Swarm (many bodies), Compliance Officer (resistance), Dosage Dispenser (Dose-only), Triage Unit (heal). This is the bodyguard / "dock matters" fight.

## 2. Phase plan
Single phase, no threshold, no floor (R3 n/a). 1 needle at tick 0, FIXED.

**Layout (T1 base; FLAT amounts × `enemy_damage_by_tier` [1.0, 1.3, 1.69, 2.2])**

| Slice | Ticks | Effect | Mode |
|---|---|---|---|
| Shim | 5 | Damage 6 | FLAT |
| Null | 5 | nothing | n/a |
| Dose | 5 | Damage 4 + CORRUPTED on 1 non-NULL slice of yours | FLAT |
| Defrag | 5 | BLOCK 6 | FLAT |
| Overflow | 5 | Damage 14 (guarded) | FLAT |
| Shim | 5 | Damage 6 | FLAT |

Ticks: 6 × 5 = 30. Order around the wheel: Shim, Null, Dose, Defrag, Overflow, Shim. Null and Overflow are 15 ticks apart, so one 15-tick spin swaps which of them is under the needle.

- **Satellite:** Collector Drone, docked on the **Overflow** slice at combat start, fixed (R12, N13), one only, never re-docks. A pointer attack aimed while the needle reads Overflow hits the drone instead of the collector. Mini-wheel: Shim 3 / Defrag 3, resolves after the host. HP by tier 6 / 8 / 10 / 12 (a new field on the satellite spawn data, N2).
- **Hub rule:** none.
- **Statuses:** CORRUPTED from Dose (R9: 2× RAM on that slice). The target slice is the slice under *your* pointer at resolve time, not random, for determinism (see Q).
- **Listeners:** none.
- **Transition:** none (1 phase).

## 3. Sustain and intake
- **Sustain: none.** No HEAL, so 0 HP/turn, under the 30 % cap (0.3 × 9 = 2.7 at T1). Defrag BLOCK 6 on 1 of 6 slices (about 1.0 block per turn) is defense, not sustain, and is not counted against the cap. The drone's Defrag 3 is on its own wheel.
- **Intake at the reference player** (needle uniform, no steering): (6 + 0 + 4 + 0 + 14 + 6) / 6 = 5.0 per turn at T1. Scaled: T2 6.5, T3 8.45, T4 11.0. A player who steers off Overflow and Dose takes about 2-3 at T1. Above 0 at every tier.
- The Dose's CORRUPTED RAM tax matters more than its 4 damage.

## 4. HP by tier
R2 normal (1 phase) band: T1 28-36 · T2 34-44 · T3 44-56 · T4 56-70. Budget = `reference_dpt` × 3.5 × 1 needle, no sustain deduction.

| Tier | Arithmetic | HP |
|---|---|---|
| T1 | 9 × 3.5 = 31.5 | 32 |
| T2 | 11 × 3.5 = 38.5 | 38 |
| T3 | 14 × 3.5 = 49 | 48 |
| T4 | 18 × 3.5 = 63 | 62 |

`hp_by_tier` = [32, 38, 48, 62]. Drone HP (6 / 8 / 10 / 12) is separate and optional, so it is not in the budget. Since the guard costs the player roughly 1 in 6 turns of landed hits when ignored, this stays inside the 3-4 turn target.

## 5. Enrage
None (normal class, R4).

## 6. Buffs and counter Exploits
Not applicable.

## 7. Counterplay
- **Good player:** reads the needle. If it sits on Overflow, spends the free nudge to take it off the Overflow's Perfect tick (WEAK landing, 7 base damage) or off the slice entirely, or uses a 15-tick spin card to swap Overflow with Null. Hits the collector on every unguarded slice. Shoots the drone only when a spare turn lets the needle sit on Overflow anyway.
- **Weak player:** shoots the drone every turn (it never re-docks, so this is only a waste), lets the Overflow land, and ends with two CORRUPTED slices that double RAM costs.

## 8. Systems needed
- **N1** (flat × tier damage factor) and **N2** (`hp_by_tier`, `enemy_damage_by_tier`, drone HP by tier). Fallback: hand-set per-tier amounts in the `.tres`.
- **N9** (CORRUPTED as 2× RAM). Fallback: today's CORRUPTED (3 self-damage + 1 RAM); the design still works.
- **N13** (fixed satellites, replacement rule). Fallback: the drone can be nudged, which weakens the guard.
- N3/N4 not needed. No N12: all slices are 5 ticks.

## 9. Delta vs today
- **Kept:** six-slice theme, bodyguard drone, Dose with CORRUPTED, Overflow as the single big hit, Null.
- **Changed:** the drone docks on Overflow (the big threat) instead of an early slice; Dose gains 4 damage so it is never a free turn; Shim 8 → 6; HP 40 → [32, 38, 48, 62]; drone HP now by tier.
- **heat_effects:** none in the data; none added.

## 10. Predicted sim check
Baseline turns below are quoted from my own v1 notes and are unverified against `BASELINE_e2e13918`.

| Tier | Baseline turns | Predicted | Win % |
|---|---|---|---|
| T1 | 2.5 | 3.2 | 100 |
| T2 | 3.9 | 3.5 | ≥ 97 |
| T3 | 5.8 | 3.8 | ≥ 93 |
| T4 | 9.9 | 4.2 | 85-92 |

HP drops into the R2 band, so fights land near 3-4 turns. The guard adds about 0.3 turns when the needle sits on Overflow. At T4 a 2.2× Overflow (about 31) plus corruption makes the 90 % target uncertain; tune the sim after the first pass.

## 11. Q:
- Q: Should Dose's CORRUPTED pick be the slice under your pointer (deterministic, proposed) or a checkpointed random non-NULL slice?
- Q: Should drone HP scale by tier through its own `hp_by_tier` (proposed) or stay fixed?
- Q: Does a CORRUPTED slice raise the free nudge's cost from 0 to 1 RAM? It decides how hard Dose bites a competent player.
- Q: Is a single guarded slice enough of a question at L5-6, or should T3+ add a second drone?
