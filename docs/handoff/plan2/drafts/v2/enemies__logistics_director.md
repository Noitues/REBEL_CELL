<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__logistics_director; status ok; tokens in 8824 cache-write 0 cache-read 32585 out 13408; cost $0.079. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (P1 intake arithmetic):** The P1 intake is recomputed on the new P1 layout. Shim(5) 1.33 + Overflow 1.40 + Shim(4) 1.00 = **3.73**, not 3.3. T3 P1 becomes 6.3 (P2 7.0 and P3 12.7 re-added and correct). The tick sums, floors and HP budgets are re-checked in §4 and unchanged: 87 / 105 / 132.
- **Issue 2 (Package geometry):** A Package is now a **6-tick segment covering ticks [c, c+5] clockwise** in the player wheel's own frame. c is the tick your pointer reads when Tag resolves, so there is no centre-tick ambiguity and it works with any slice size (N12).
  - The entry Packages sit at ticks **8-13 and 23-28**, covering the Perfect ticks 10 and 25 and the Good ticks around them.
  - The false "weak edges" claim is removed. They can only be dodged by steering or Cleanse.
- **Issue 3 (Package threat too soft):** Two 6-tick Packages cover 12 of 30 ticks, so a careless read is **40 %** per turn. The cost stays at 2 RAM plus ×0.5 damage on that resolve.
  - Because the Package rotates with your wheel, it permanently poisons the same part of your own slice, which makes "which slice do I read" a real question.
  - Dodging a 6-tick Package from inside it takes up to 3 nudge ticks, which is not free.
  - The "weak player keeps reading it" claim is softened. The turn-start respin re-randomizes, so it is a 40 % risk per turn, not a lock-in.
- **Issue 4 (Priority too weak):**
  - Priority now drains **5 RAM**, and P1 has **two** Priority slices (4 ticks each), taking over 4 ticks from the Null slice (6 → 4) and 2 from Defrag/Shim.
  - Expected drain is 8/30 × 5 = **1.33 RAM per turn**, about a third of the +4 income, so steering at 3 RAM per tick is a real trade.
  - The "RAM-starved" claim is restated honestly as a cumulative ~4.7 RAM per phase.
- **Issue 5 (respin lock overlap):** §8 and §7 now state that **Weight above 0 already blocks enemy-wheel Respin and Flip in all three phases** (GDD 2.5), so Flip on the enemy wheel is unavailable throughout unless Breached. N7 covers only the new **own-wheel respin lock** in P3.
- **Issue 6 (fallbacks):** The `on_enter_effects` fallback is rewritten: no entry Packages, so P2 starts with an empty ring. The N12 fallback is now given for every phase as six 5-tick slices, including P1.
- **Issue 7 (naming):** Dock is renamed **Tag**.
- **Issue 8 (R10):** Kept, because the needle is at tick 0 in every phase. Q4 now says explicitly that the pointer-on-any-tick tool is unused.
- **Critic Q1 (start-of-turn respin):** Decided in the draft. The turn-start respin stays; it is the one random event, and the plan starts from that landing.
- **Critic Q3 (Packages persist into P3):** Kept as persistent. This makes P2's tagging consequential and gives Cleanse a reason to be played.
- **Critic Q2 (second Priority slice):** Adopted up front (two Priority slices in P1) instead of waiting for the sim.
- **Kept, because the critic marked it strong:** dropping Orbit and the P3 second needle, the 87 / 105 / 132 HP and floors, the Parasite-ring question in P2 with an honest N10 fallback, and Weight on the Hub in P1-P2.

# logistics_director: direct design

## 1. Identity & the one question

- **Class:** mini-boss, 3 phases, guards the final Rack (layer 7) of a Meridian netrun at T1-T3. It is never met in L1-6, so the Meridian normals and elites must have already taught WEIGHT (resistance) and PRIORITY (RAM drain).
- **Concept:** a middle manager whose job is friction. It makes everything slower and costlier, tags your best work, then removes your rerolls.
- **Changes from the CONTENT_DESIGN_V2 §3 concept:**
  - **Orbit is dropped.** Every wheel respins to a random tick at the start of each turn, so a single orbiting needle is a no-op.
  - **P3's second needle is dropped.** It would double the phase budget and push HP out of the 3-phase band.
  - **Package latching is tied to the Director's own Tag slices** instead of an "every other turn" timer, so the player can steer its needle off them.
  - **Weight sits on the Hub in P1 and P2,** so Hub Breach is a real answer.

| Phase | The question | The answer that shortens the fight |
|---|---|---|
| P1 Intake | "Moving its heavy wheel costs RAM, and Priority drains RAM. Pay to steer, or race?" | Hub Breach, Strip, or a spin card that carries past the Weight. Otherwise accept the hits and burst. |
| P2 Packages | "Every slice you read gets tagged, and the tag rides on your wheel. Which part of your wheel do you read?" | Steer its needle off Tag, Cleanse, or rotate your own wheel so Packages sit off your pointer. |
| P3 Overtime | "No rerolls, and leftover tags tax you. What is the best line from the landing you got?" | Plan nudge + card from the turn-start landing and finish before the enrage. |

## 2. Phase plan

Layouts list slices clockwise from tick 0 as `slice (ticks)`. The needle sits at tick 0 in every phase (R10 left unused; see Q4). Enemy damage and block are FLAT × the tier damage factor (R2). RAM drain is flat and not tier-scaled.

### P1 Intake (100 → 66 %)

| Field | Value |
|---|---|
| Needles | 1, FIXED at tick 0 |
| Layout (sum 30) | Shim 10 (5) · Priority (4) · Defrag 8 (5) · Overflow 14 (4) · Shim 10 (4) · Priority (4) · Null (4). 5+4+5+4+4+4+4 = 30 |
| Effects | Shim and Overflow: FLAT damage. Defrag: FLAT block. Priority: drain 5 RAM, flat, on any landing tier. |
| Hub rule | **Weight:** resistance 3, restored each player turn. Hub-sourced, so Hub Breach disables it for a turn. |
| Statuses / parasites / listeners | None |

- Moving its wheel 1 tick costs the free nudge plus 3 RAM. Spin cards absorb only the first 3 ticks, so a large spin carries through.
- Priority takes 8 of 30 ticks, so the expected drain is 1.33 RAM per turn.
- Enemy-wheel Respin and Flip are blocked while Weight is above 0, in every phase.

### P2 Packages (66 → 33 %)

| Field | Value |
|---|---|
| Needles | 1, FIXED at tick 0 |
| Layout (sum 30) | Shim 10 (5) · Tag (4) · Overflow 18 (4) · Defrag 8 (5) · Shim 10 (4) · Tag (3) · Null (5). 5+4+4+5+4+3+5 = 30 |
| Hub rule | **Weight 1** (breachable). Steering costs the free nudge plus 1 RAM per tick. |
| Tag | Deals no damage. When it resolves it latches a **Package** on your wheel. |
| Package | A **6-tick** segment of the Parasite ring, covering ticks [c, c+5] clockwise, where c is the tick your pointer reads at the Tag resolve. It sits in your wheel's frame and rotates with it. Max 2; a third replaces the oldest. When your pointer reads any of its ticks: drain 2 RAM, and your outgoing damage this resolve is ×0.5 (a flat, tier-independent debuff). |
| Entry | 2 Packages are pre-latched at your-wheel ticks 8-13 and 23-28. They cover the Perfect ticks 10 and 25 and the neighbouring Good ticks, so they are dodgeable only by steering or Cleanse. |
| Statuses / listeners | None |

- Two Packages cover 12 of 30 ticks, a 40 % read chance per turn if you ignore them.
- Cleanse removes one Package.

### P3 Overtime (33 → 0 %)

| Field | Value |
|---|---|
| Needles | 1, FIXED at tick 0 |
| Layout (sum 30) | Overflow 18 (5) · Shim 10 (4) · Overflow 18 (4) · Priority (4) · Defrag 8 (4) · Shim 10 (4) · Shim 10 (5). 5+4+4+4+4+4+5 = 30 |
| Passive traits | **Overtime:** your own-wheel player-initiated Respin (cards and the 4 RAM respin) is locked. The start-of-turn respin still happens. **Weight 1:** restores each turn, not breachable. Both are passive traits, so Hub Breach does not help in P3. |
| Tag | None. No new Packages are latched. |
| Carry-over | Packages from P2 persist (`cleanse_on_enter = NONE`). |
| Statuses | None |

### Transitions
- Each transition parks damage at ceil(max HP × the next threshold) (R3).
- Statuses and the Parasite ring are kept (R6).
- The preview shows "PARKED −N" on a capped hit.
- **P1 → P2** ("Delivery audit: every route gets a tag"):
  - `wheel_override` + `hub_override` (Weight 3 → 1);
  - `on_enter_effects` latch the 2 entry Packages.
- **P2 → P3** ("Overtime is mandatory"): `wheel_override` + the passive trait changes (Overtime on, hub Weight becomes a passive trait).

## 3. Sustain and intake

Sustain is Defrag block only; there is no heal. Expected value = size/30 × mean landing multiplier × amount, with the multiplier 0.8 for a 5-tick slice and 0.75 for a 4-tick one. Block is FLAT × tier factor, shown here at T1.

| Phase | Defrag expected per turn (T1) | % of reference 9 DPT |
|---|---|---|
| P1 | 5/30 × 0.8 × 8 = 1.07 | 12 % |
| P2 | 5/30 × 0.8 × 8 = 1.07 | 12 % |
| P3 | 4/30 × 0.75 × 8 = 0.80 | 9 % |

All are well under the 30 % cap, and a steering player can dodge Defrag, so these are upper bounds.

**Unmitigated expected intake at T1:**

| Phase | Damage per turn | Other cost |
|---|---|---|
| P1 | **3.73** = Shim(5) 1.33 + Overflow 14 (4) 1.40 + Shim(4) 1.00 | Priority 8/30 × 5 = 1.33 RAM per turn |
| P2 | 4.13 = 1.33 + Overflow 18 (4) 1.80 + 1.00 | 23 % chance per turn of a new Tag; Package reads about 40 % per turn, each costing 2 RAM and ×0.5 damage |
| P3 | 7.53 = 2.40 + 1.00 + 1.80 + 1.00 + 1.33 | Priority 4/30 × 5 = 0.67 RAM per turn |

- At T3 (×1.69) the damage intake is 6.3 / 7.0 / 12.7 per turn.
- Intake is above 0 in every phase. Steering and Block roughly halve it for a good player.

## 4. HP by tier

Phase budget = (`reference_dpt[t]` − Defrag sustain × tier factor) × 3.5 turns × 1 needle. Every phase has one needle.

| Tier | Ref DPT | Sustain P1 / P2 / P3 | Net per turn | Budget P1 / P2 / P3 | Sum | R2 band (3 phases) | hp_by_tier |
|---|---|---|---|---|---|---|---|
| T1 (×1.0) | 9 | 1.07 / 1.07 / 0.80 | 7.93 / 7.93 / 8.20 | 27.8 / 27.8 / 28.7 | 84.3 | 85-105 | **87** |
| T2 (×1.3) | 11 | 1.39 / 1.39 / 1.04 | 9.61 / 9.61 / 9.96 | 33.6 / 33.6 / 34.9 | 102.1 | 104-128 | **105** |
| T3 (×1.69) | 14 | 1.81 / 1.81 / 1.35 | 12.19 / 12.19 / 12.65 | 42.7 / 42.7 / 44.3 | 129.7 | 132-162 | **132** |
| T4 | n/a | n/a | n/a | n/a | n/a | n/a | not used (mini-bosses stop at T3; entry 0) |

- **Floors** (thresholds 0.66 / 0.33):
  - T1: ceil(57.4) = 58 and ceil(28.7) = 29, so phases of 29 / 29 / 29.
  - T2: ceil(69.3) = 70 and ceil(34.65) = 35, so 35 / 35 / 35.
  - T3: ceil(87.1) = 88 and ceil(43.6) = 44, so 44 / 44 / 44.
- **Turns per phase** at the reference player: T1 3.66 / 3.66 / 3.54; T2 3.64 / 3.64 / 3.51; T3 3.61 / 3.61 / 3.48. All fall inside 3-4.
- **Parking** means no phase can be skipped, so the floor is 3 turns however hard the player bursts.
- Package penalties are not in the budget. They slow only a careless player.

## 5. Enrage

**Default** (turn 10, every 5 turns, +25 % additive, damage only).
- The reference path is about 3.6 × 3 ≈ 10.8 turns, so the first step lands at the tail of P3. A careless run pays at the end and the fight never stalls.
- No authored enrage. P3's respin lock is already its escalation, and a second authored clock would stack on the same pressure.

## 6. Buffs and counter Exploits

N/A. R7 applies to HQ bosses only.

## 7. Counterplay

**P1**
- **Good player:**
  - Hub Breach, Strip or a big spin where it counts.
  - The free nudge goes on their own wheel (unresisted).
  - Bursts on Defrag and Null turns and lets Priority land only when a steer would cost more than the 5 RAM.
- **Weak player:**
  - Spends the free nudge plus 3 RAM to move one tick, then eats Priority anyway.
  - Averages about 4.7 RAM drained over the phase and enters P2 short of RAM.
- Enemy-wheel Respin and Flip are unavailable in all three phases unless Breached.

**P2**
- **Good player:**
  - Reads where Packages sit on their own wheel and rotates or nudges so their best slice's Perfect tick is off a Package.
  - Spends a Cleanse on the Package covering their best slice.
  - Steers its needle off Tag when cheap (free nudge plus 1 RAM).
- **Weak player:**
  - Reads through a Package about 40 % of turns and loses 2 RAM and half their damage each time.
  - Ignores that new Tags latch onto the slice they just played.

**P3**
- **Good player:**
  - Treats the turn-start landing as a puzzle and picks the nudge + card line.
  - Cleanses leftover Packages early and keeps RAM for the end.
  - Avoids the Priority slice at 5 RAM.
- **Weak player:**
  - Plays for a Respin they can no longer use and runs into the turn-10 enrage on a poor landing.

## 8. Systems needed

| System | Why | Data-only fallback |
|---|---|---|
| N1 amount modes | FLAT damage and block × tier factor | None needed; this is the rule. |
| N2 tier tables | `hp_by_tier`, `enemy_damage_by_tier` | None; this is the rule. |
| N3 phases and parking | 3 phases, floors, R6 status keep | None. |
| N4 enrage | Class default | Authored `EnrageData` inline until class defaults exist. |
| N7 | **Own-wheel respin lock only** (P3). Enemy-wheel Respin and Flip are already blocked by Weight > 0 (GDD 2.5). | None; without it P3 loses its identity. |
| N10 Parasite ring (depends on N1, N9) | Packages | **Yes:** Tag becomes an INFECT slice applying today's PARASITE status (halves output) to the slice under your pointer. The status exists now. This loses the RAM drain, the 6-tick geometry and "the tag rides on your wheel", but keeps the question. |
| N12 variable slice sizes | 3-, 4- and 7-slice layouts | **Yes:** six 5-tick slices each: P1 Shim 10 · Priority · Defrag 8 · Overflow 14 · Priority · Null; P2 Shim 10 · Tag · Overflow 18 · Defrag 8 · Shim 10 · Null; P3 Overflow 18 · Shim 10 · Overflow 18 · Priority · Defrag 8 · Shim 10. |
| NEW: `BossPhaseData.on_enter_effects` (S) | The 2 pre-latched entry Packages | Drop them. P2 opens with an empty ring and the first Tag starts it. This is weaker but works. |

N6 listeners and N8 stacks are not needed.

## 9. Delta vs today

- **HP:** 150 → `hp_by_tier` [87, 105, 132, 0].
- **Thresholds:** 0.5 / 0.25 → 0.66 / 0.33, with a third phase added (P1 is the base wheel, two override entries).
- **Dropped:**
  - MULTIPLY (0, 15) and ORBIT (a no-op under the per-turn respin);
  - `passive_resistance` 2 (moved to the Hub as Weight);
  - Sandbox 5.
- **Kept:**
  - Shim 10, Defrag 8, Priority and Null (resized);
  - `cycle_reward = 60`.
- **New slices:** Overflow 14, Overflow 18, Tag. Also `hub_override` and `wheel_override` on P2 and P3.
- **Priority:** drain 3 → 5 RAM, and two copies in P1.
- **Flags:** `is_elite` stays true alongside `is_mini_boss` unless the code prefers one flag.
- **heat_effects:** none authored today; keep none. Heat should not change a fight with this much authored pressure.

## 10. Predicted sim check

There is no baseline row; this is an estimate from the wheel.

| Tier | Mean turns (reference skill) | Win |
|---|---|---|
| T1 | 10-11 | ~97 % |
| T2 | 10-11 | ~95 % |
| T3 | 10-11 | ~90 % |

- **Win rate:** intake is modest and Defrag is the only sustain. Losses come from P3 at T3, where 12.7 raw damage per turn and a RAM-drained player compound.
- **Turns:** the reference is about 10.8. A best-play bot should land around 4-6 (floor 3 from parking); skill 0.5 around 12, p90 ≤ 14.
- **Against the baseline:** today's 150 HP at T3 is one long attrition shape, and the Account Manager baseline (20.7 turns at T3) shows the old template running 2× over class target. Per-phase floors cap each phase at about 3.5 turns here.

## 11. Open questions

Q: Does a Package's ×0.5 apply once per resolve or once per read? I assumed once per resolve, which is identical with one needle, but Twin Pointer would double-read it.
Q: Should Priority's RAM drain scale with tier? I left 5 RAM flat (RAM is not a damage unit), which is gentler at T3. The sim should show whether two Priority slices in P1 are enough.
Q: Are 7-slice layouts acceptable, or must P1-P3 stay at 6 slices (the N12 fallback)? The tick maps (4-tick W G G W with no Perfect) matter for the read.
Q: Is a single FIXED needle at tick 0 in all three phases acceptable? If the designer wants uneven needles (R10), add a 2nd needle in P3 at 0 / 11 and raise T1 HP toward the band ceiling (~105), since P3's budget would double.
Q: Should Packages persist into P3 (as drafted) or be cleansed on entry? Persisting makes P2 consequential but can stack with the turn-10 enrage; `cleanse_on_enter = PLAYER` is the safe alternative.
