<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__logistics_director; status ok; tokens in 16826 cache-write 0 cache-read 32007 out 19728; cost $0.119. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# logistics_director: direct design

## 1. Identity & the one question

- **Class:** mini-boss, 3 phases, guards the final Rack (layer 7) of a Meridian netrun at T1-T3. It is never met in L1-6, so its three questions have to be taught by the Meridian normals and elites before it. This assumes WEIGHT and PRIORITY already appear on those normals.
- **Concept:** a middle manager whose whole job is friction. It makes everything slower and costlier, then tags your best work.
- **Changes from the section 3 concept:**
  - **Orbit is dropped.** Every wheel respins to a random tick at the start of each turn. A single orbiting needle is therefore a no-op unless the wheel is Frozen. The needle count and spacing are what matter.
  - **P3's second needle is dropped.** It would add a doubled phase budget. That puts HP outside the 85-105 band and muddies the question.
  - **Package latching is made player-readable.** It is tied to the Director's own Dock slices instead of a "every other turn" timer. The player can steer the needle off them.
  - **Resistance lives on the Hub in P1 and P2,** so Hub Breach is a real answer.

| Phase | The question | The answer that shortens the fight |
|---|---|---|
| P1 Intake | "Moving a heavy wheel costs RAM, and Priority drains RAM. Do you pay to steer, or race?" | Hub Breach, Strip, or a spin card that carries past the Weight; otherwise accept the hits and burst. |
| P2 Packages | "Every slice you play gets tagged. Which slice do you read, and where does the tag sit?" | Steer its needle off Dock, or Cleanse. Land your hits on untagged slices. |
| P3 Overtime | "No rerolls, no resistance relief, and leftover tags tax your RAM. What is the single best line from the landing you got?" | Plan nudge + card from the turn-start landing. Finish before the enrage. |

## 2. Phase plan

The wheel layout lists slices clockwise from tick 0 as `slice (ticks)`. The needle sits at tick 0 unless noted.

### P1 Intake (100 → 66 %)
Fixed needle, one question: Weight.

| Field | Value |
|---|---|
| Needles | 1, FIXED at tick 0 |
| Layout (sum 30) | Shim 10 (5) · Defrag 8 (6) · Priority (5) · Overflow 14 (4) · Shim 10 (4) · Null (6) |
| Effects | Shim and Overflow: FLAT damage × tier factor. Defrag: FLAT block × tier factor. Priority: drain 3 RAM when it resolves (unscaled, it is RAM). |
| Hub rule | **Weight:** resistance 3, restored each player turn. Hub-sourced, so Hub Breach disables it for a turn. |
| Statuses / parasites / listeners | None |

- A 1-tick move on its wheel costs 4 nudge ticks: the free nudge plus 3 RAM. Priority drains 3 RAM. The two loops feed each other.
- Spin cards absorb only the first 3 ticks, so a large spin carries through.

### P2 Packages (66 → 33 %)

| Field | Value |
|---|---|
| Needles | 1, FIXED at tick 0 |
| Layout (sum 30) | Shim 10 (5) · Dock (4) · Overflow 18 (4) · Defrag 8 (5) · Shim 10 (4) · Dock (3) · Null (5) |
| Hub rule | **Weight 1** (breachable). Steering now costs the free nudge plus 1 RAM. |
| Dock | Deals no damage. When it resolves it latches a **Package** parasite, a 4-tick segment centred on the tick your pointer reads, so it sits on the slice you just used. Max 2 Packages; a third replaces the oldest. |
| Package | A segment of the Parasite ring on your wheel; it rotates with your wheel. When your pointer reads it: drain 2 RAM, and your outgoing damage this resolve is ×0.5 (a flat tier-independent debuff). |
| Entry | 2 Packages are pre-latched at your-wheel ticks 7 and 22. |
| Statuses / listeners | No statuses; no listeners |

### P3 Overtime (33 → 0 %)

| Field | Value |
|---|---|
| Needles | 1 at tick 0 |
| Layout (sum 30) | Overflow 18 (5) · Shim 10 (4) · Overflow 18 (4) · Priority (4) · Defrag 8 (4) · Shim 10 (4) · Shim 10 (5) |
| Hub rule | **Overtime:** player-initiated respin is locked on both wheels (cards and the 4 RAM respin; the start-of-turn respin still happens). Weight 1 as a passive trait: restores each turn, not breachable. |
| Dock | None; no new Packages. |
| Carry-over | Packages latched in P2 persist. `cleanse_on_enter = NONE`. |
| Statuses | None |

### Transitions
- Each transition parks damage at ceil(max HP × the next threshold) (R3).
- Statuses are kept (R6).
- Each plays a phase line:
  - **P1 → P2** ("Delivery audit: every route gets a tag"): `wheel_override` and `hub_override` (resistance 3 → 1), plus `on_enter_effects` latching the 2 pre-placed Packages.
  - **P2 → P3** ("Overtime is mandatory"): `wheel_override` and `hub_override` (respin lock).
- The preview shows "PARKED −N" on a capped hit.

## 3. Sustain and intake

Sustain is Defrag block only. There is no heal. Expected value is size/30 × landing multiplier × amount, with block flat × tier factor.

| Phase | Defrag expected per turn (T1) | % of reference 9 DPT |
|---|---|---|
| P1 | 6/30 × 0.67 × 8 = 1.07 | 12 % |
| P2 | 5/30 × 0.8 × 8 = 1.07 | 12 % |
| P3 | 4/30 × 0.75 × 8 = 0.80 | 9 % |

All are well under the 30 % cap. The player can also dodge Defrag by steering, so these are upper bounds.

**Unmitigated expected intake at T1** (landing multiplier 0.75-0.8 by slice size):

| Phase | Damage per turn | Other cost |
|---|---|---|
| P1 | ≈ 3.3 (Shim 1.07 + Overflow 1.4 + Shim 0.8) | 0.4 RAM per turn from Priority |
| P2 | ≈ 4.1 (1.33 + 1.8 + 1.0) | Package RAM and damage tax |
| P3 | ≈ 7.5 (2.4 + 1.0 + 1.8 + 1.0 + 1.33) | 0.4 RAM per turn |

All are above 0, matching the target of rising pressure. At T3 (×1.69) this is 5.6 / 6.9 / 12.7 per turn. Steering and Block roughly halve it for a good player.

## 4. HP by tier

Phase budget = (`reference_dpt[t]` − sustain × tier factor) × 3.5 turns × 1 needle. Every phase has one needle, so the per-phase budgets are equal.

| Tier | Reference DPT | Sustain by phase (P1 / P2 / P3) | Net per turn | Budget per phase | Sum | Band (R2, 3 phases) | hp_by_tier |
|---|---|---|---|---|---|---|---|
| T1 (×1.0) | 9 | 1.07 / 1.07 / 0.80 | 7.93 / 7.93 / 8.20 | 27.8 / 27.8 / 28.7 | 84.3 | 85-105 | **87** |
| T2 (×1.3) | 11 | 1.39 / 1.39 / 1.04 | 9.61 / 9.61 / 9.96 | 33.6 / 33.6 / 34.9 | 102.1 | 104-128 | **105** |
| T3 (×1.69) | 14 | 1.81 / 1.81 / 1.35 | 12.19 / 12.19 / 12.65 | 42.7 / 42.7 / 44.3 | 129.6 | 132-162 | **132** |
| T4 | n/a | n/a | n/a | n/a | n/a | n/a | n/a (mini-bosses stop at T3; entry left 0) |

- **Floors** (thresholds 0.66 / 0.33):
  - T1 58 and 29 → phases of 29 / 29 / 29.
  - T2 70 and 35 → 35 / 35 / 35.
  - T3 88 and 44 → 44 / 44 / 44.
- **Margin:** each phase is 2-4 % above budget, which is about 3.5-3.7 turns per phase at the reference player.
- **Parking** means no phase can be skipped. The minimum is 3 turns, one per phase, however much the player bursts.

## 5. Enrage

**Default** (turn 10, every 5 turns, +25 % additive, damage only). The reference path is about 10.9 turns, so the first step lands near the end of P3. That is right for a mini-boss: slow or careless play pays at the end, and the fight never stalls.

An authored version isn't warranted. The respin lock already acts as P3's escalation, and a second clock would stack on the same pressure.

## 6. Buffs and counter Exploits

N/A. This is a mini-boss; R7 applies to HQ bosses only.

## 7. Counterplay

**P1**
- **Good player:** gauges whether to spend RAM. Often they ignore steering and put a Breach, Strip or large spin where it counts. They land the free nudge on their own wheel, which is unresisted. They also take the Defrag turn as a gift and hit hard while the needle sits on Null or Defrag.
- **Weak player:** burns 4 ticks of nudges to move a single tick, then gets drained by Priority. They end the phase RAM-starved going into P2.

**P2**
- **Good player:** lets the Dock slices pass by steering its wheel (cheap now: free nudge plus 1 RAM) or by spinning. They Cleanse a Package before it falls under the pointer, rotate their own wheel so Packages sit off the pointer, and land hits on slices that aren't tagged. The two Entry Packages sit on weak edges (ticks 7 and 22), so they can be dodged.
- **Weak player:** lets Dock latch onto their Perfect slice, then keeps reading it. Each read halves their damage and costs 2 RAM.

**P3**
- **Good player:** treats the turn-start landing as a puzzle. They pick the nudge and card line, keep RAM for the late turns, and avoid the Priority drain. Packages left from P2 are a RAM tax, so they Cleanse early or never read them.
- **Weak player:** relies on the respin they used to fish for a good landing. Locked out, they run into the turn-10 enrage still on a bad landing.

## 8. Systems needed

| System | Why | Data-only fallback |
|---|---|---|
| N1 amount modes | Flat enemy block and damage × tier factor | None needed; the effect interpreter's flat scaling is the rule. |
| N2 tier tables | `hp_by_tier`, `enemy_damage_by_tier` | None; this is the rule. |
| N3 phases and parking | 3 phases, floors, R6 status keep | None. |
| N4 enrage | Class default | Authored `EnrageData` inline until class defaults exist. |
| N7 respin lock | P3 | None; P3 would collapse to a plain wheel. |
| N10 Parasite ring | Packages | **Yes:** Dock becomes an INFECT slice applying today's PARASITE status (halves output) to the slice under your pointer. The status exists now. This loses the RAM drain and the "tag follows your wheel" identity but keeps the question. |
| N12 variable slice sizes | 3-, 4-, 6-tick slices | **Yes:** six 5-tick slices per phase, with P1 as today's wheel with Sandbox 5 swapped for Shim 10. P2: Shim 10 · Dock · Overflow 18 · Defrag 8 · Dock · Null. P3: Overflow 18 · Shim 10 · Overflow 18 · Priority · Defrag 8 · Shim 10. |
| NEW: `BossPhaseData.on_enter_effects` (S) | The 2 pre-placed Packages | A hub ON_TURN_START that latches only when the ring is empty; but then Cleanse undoes itself, so I recommend the field. |

N6 listeners and N8 stacks are not needed here, so it stays out of the Account Manager's lane.

## 9. Delta vs today

- **HP:** 150 → `hp_by_tier` [87, 105, 132, 0].
- **Thresholds:** 0.5 / 0.25 → 0.66 / 0.33, with a third phase added (2 entries in the array, P1 is the base wheel).
- **Dropped:**
  - MULTIPLY (0, 15) and ORBIT (a no-op under per-turn respin);
  - `passive_resistance` 2 (moved to the Hub);
  - Sandbox 5.
- **Kept:** Shim 10, Defrag 8, Priority and Null (resized to the layouts above), and `cycle_reward = 60`.
- **New slices:** Overflow 14, Overflow 18 and Dock. Also `hub_override` and `wheel_override` on P2 and P3.
- **Flags:** `is_elite` stays true alongside `is_mini_boss` unless the code prefers one flag.
- **heat_effects:** none authored today; keep none. Heat should not alter a fight with this much authored pressure.

## 10. Predicted sim check

There is no baseline row; this is an estimate from the wheel.

| Tier | Mean turns (reference skill) | Win |
|---|---|---|
| T1 | 10-11 | ~97 % |
| T2 | 10-11 | ~95 % |
| T3 | 10-11 | ~90 % |

- **Win rate:** intake is modest and Defrag is the only sustain. Losses come from P3 at T3, where 12.7 raw damage per turn and a RAM-starved player compound.
- **Turns:** reference is about 10.9. A best-play bot should land around 4-6 (floor 3 from parking); skill 0.5 around 12, p90 ≤ 14. Today's 150 HP at T3 (scaled) is the wrong shape: one long attrition phase.
- **Check against baseline:** the Account Manager baseline (20.7 turns at T3) shows the old template can run 2× past class target; this design's phase cap of about 3.5 turns each and the parked-damage floors prevent that.

## 11. Open questions

Q: Does the P3 respin lock block only player-initiated respins (cards and the 4 RAM respin), leaving the start-of-turn respin as designed? I assumed yes; "pure deterministic plan" in the concept only holds if the start-of-turn respin is also locked, which would break the core turn flow.
Q: Do Packages persist into P3, or does P2 → P3 cleanse the player's ring (`cleanse_on_enter = PLAYER`)? Persisting makes P2 consequential but could stack with enrage.
Q: Does a Package's −50 % damage apply to every resolve of the pointer's slice, or once per Package per turn? I assumed once per resolve (one needle makes them equal).
Q: Is a single FIXED needle in P1 and P2 acceptable, given no orbit or migrate? If the designer wants uneven needles (R10), add one to P3 and raise T1 HP to ~105 at the band ceiling, since P3's budget would double.
Q: Should Priority's RAM drain scale with tier like damage, or stay flat? Flat 3 RAM at T3 is gentler than damage scaling; I left it flat (RAM is not a damage unit).
