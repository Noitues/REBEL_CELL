<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__collections_agent; status ok; tokens in 19007 cache-write 0 cache-read 32007 out 3223; cost $0.038. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# collections_agent: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, Solace. Appears in L1-2 as the first "you are being pressured" fight (teaching) and in L5-6 at T2+ as pressure.
- **Concept:** a debt collector with a bodyguard. Its drone is a toll booth: it guards the one slice that matters, and the collector's wheel is built so only one slice is dangerous.
- **The one question:** *"Which of its slices do you let read, and can you get your hit past the guard?"* The Overflow is its only big threat. The drone sits on the Dose, not on the Overflow. The player must choose between killing the drone (which opens the Dose-guard slice) and ignoring it.
- **Answer that shortens the fight:** steer its needle to Null or Defrag, then hit the collector directly. Hits taken by the drone are wasted, so steer the *collector's pointer* onto a slice that isn't the guarded one. Killing the drone first is the slow answer.
- **Distinct from siblings:** Billing Daemon (RAM economy), Care Swarm (many bodies), Compliance Officer (resistance), Dosage Dispenser (Dose-only), Triage Unit (heal). This one is the bodyguard / "dock matters" fight.

## 2. Phase plan
Single phase, no threshold, no floor (R3 n/a). 1 needle, tick 0, FIXED.

| Slice | Ticks | Effect | Mode |
|---|---|---|---|
| Shim | 5 | Damage 6 | FLAT |
| Null | 5 | nothing | n/a |
| Dose | 5 | Damage 4 + CORRUPTED on 1 random non-NULL slice of yours (RAM tax, R9) | FLAT |
| Defrag | 5 | BLOCK 6 | FLAT |
| Overflow | 5 | Damage 14 | FLAT |
| Shim | 5 | Damage 6 | FLAT |

Total 30. Order around the wheel: Shim, Null, Dose, Defrag, Overflow, Shim. Overflow sits opposite Null so a single 15-tick spin swaps them.

- **Satellite (kept):** the Collector Drone, docked on the **Dose** slice at combat start (`dock_slot` 1 → 2), fixed (R12), 1 active. It is a bodyguard: any pointer hit aimed while the needle reads Dose hits the drone. It has 6 HP at T1 (placeholder, see below), a mini-wheel of Shim 3 / Defrag 3, and resolves after the host.
- **Hub rule:** none.
- **Statuses:** only CORRUPTED from Dose. It is a RAM debuff now (2× RAM on that slice). This is the only pressure the Dose gives beyond its 4 damage.
- **Listeners:** none.
- **Transition:** none (1 phase).

The question is about *when* the needle reads Dose: the player can leave the drone alone and never pay for it, or kill it and gain nothing. Killing the drone is only worth it when the Dose is about to land.

## 3. Sustain and intake
- **Sustain:** one source, Defrag BLOCK 6 on 1 of 6 slices, landing 1/6 of turns. Expected 1 BLOCK per turn × ~1.0 = 1 per turn, and it only absorbs damage, never heals HP. The drone's mini-wheel Defrag 3 adds at most 0.5 per turn on its own wheel. Total ≈ 1.5 per turn, against a 30% cap of 0.3 × 9 = 2.7 at T1. Passes. No heal turns.
- **Intake at the reference player** (needle uniform over the wheel, 6-tick chance each, no steering): average (6 + 0 + 4 + 0 + 14 + 6) / 6 = 5.0 per turn, ×tier factor. With steering by a competent player landing Null or Defrag two turns in three, intake is ≈ 2-3 per turn at T1. It is above 0 and visibly dangerous only through the Overflow. T1 5.0, T2 6.5, T3 8.5, T4 11.0 unsteered.
- The Dose's 4 damage matters less than the CORRUPTED RAM tax: it makes the player's later nudges cost 2×.

## 4. HP by tier
Band R2 normal (1 phase): T1 28-36 · T2 34-44 · T3 44-56 · T4 56-70. Budget = `reference_dpt` × 3.5 × (needles landing = 1), minus sustain × 3.5.

| Tier | Budget arithmetic | HP |
|---|---|---|
| T1 | 9 × 3.5 = 31.5 − (1.5 × 3.5 = 5.3) + ~4 drone-dodge allowance | 32 |
| T2 | 11 × 3.5 = 38.5 − 5.3 + 4 | 38 |
| T3 | 14 × 3.5 = 49 − 5.3 + 4 | 48 |
| T4 | 18 × 3.5 = 63 − 5.3 + 4 | 62 |

`hp_by_tier` = [32, 38, 48, 62]. The drone's HP is separate and is spent only when the player chooses to shoot it (6 / 8 / 10 / 12). It is not counted in the budget.

## 5. Enrage
None (normal class, R4). Fights run 3-4 turns and the wheel has no stall mechanism.

## 6. Buffs and counter Exploits
Not applicable (bosses only).

## 7. Counterplay
- **Good player:** reads the pointer. If it sits on Overflow, spends the free nudge to move it one tick toward Null's WEAK edge or onto Shim; leaves the drone alone until the Dose is coming up; hits the collector on the other slices; never lets Dose read on a slice they have already corrupted.
- **Spending view:** a 15-tick spin that moves the Overflow to Null costs one card and removes the biggest threat of the fight.
- **Weak player:** shoots the drone every turn (it re-docks only once, so this is not a loop, but it wastes damage), lets the Overflow land, and ends up with two CORRUPTED slices that double RAM costs.

## 8. Systems needed
- **N1** (flat amounts × tier damage factor) and **N2** (`hp_by_tier`, `enemy_damage_by_tier`): needed to scale properly. Fallback: hand-set slice amounts per tier in the `.tres` and use one hp.
- **N9** (CORRUPTED as RAM ×2). Fallback: keep today's CORRUPTED (3 self-damage + 1 RAM) until N9 lands; the design still works.
- **N13** (fixed satellites): already effectively true in current data. No fallback needed; with it unavailable the drone can be nudged, which weakens the bodyguard.
- N3/N4 are not needed (single phase, no enrage). No N12 requirement: all slices are 5 ticks.

## 9. Delta vs today
- **Kept:** the six-slice theme, the bodyguard drone, Dose with CORRUPTED, Overflow as the single big hit, Null.
- **Changed:** the layout now puts Overflow opposite Null and the drone on Dose rather than slice 1, so the guarded slice is the *less dangerous* one and the guard has a real cost/benefit. Shim drops from 8 to 6 (the second Shim replaces the old Shim/Shim/Defrag clustering) and Dose gains 4 damage so it is never a free turn. HP 40 → [32, 38, 48, 62].
- **heat_effects:** no entry in the data; none added.
- **Drone HP:** 6 / 8 / 10 / 12 by tier, authored on the satellite.

## 10. Predicted sim check
| Tier | Turns (baseline) | Predicted | Win % |
|---|---|---|---|
| T1 | 2.5 | 3.0 | 100 |
| T2 | 3.9 | 3.4 | 100 |
| T3 | 5.8 | 3.8 | ≥ 95 |
| T4 | 9.9 | 4.2 | ≥ 90 |

The baseline's T4 fight is 9.9 turns at 17 dealt/turn because HP is flat 40 × a tier multiplier. Dropping HP to the R2 band brings every tier inside 3-4 turns. T4 might run slightly over target; p90 should stay at or under 6. Taken/turn rises slightly at T1 (Dose now hits) and falls at T4 (shorter fight, same wheel).

## 11. Q:
- Q: Should the drone re-dock after death once per fight, or never? (I chose never; re-docking makes shooting it feel like a tax.)
- Q: Does a CORRUPTED slice double the *free* nudge's cost (1 RAM instead of 0)? This decides how hard Dose bites a competent player.
- Q: Is the drone's HP counted toward the normal's R2 budget if the player must kill it? I excluded it as optional.
- Q: Should Dose damage 4 scale with the tier damage factor (FLAT × factor) or stay fixed so Dose stays a RAM threat at T4?
- Q: Is a single-slice guard enough of a question for an L5-6 pressure fight, or should the drone dock on Overflow at T3+ via `hp_by_tier`-style data?
