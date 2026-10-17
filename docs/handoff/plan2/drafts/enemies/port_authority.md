<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__port_authority; status ok; tokens in 16137 cache-write 0 cache-read 32007 out 10926; cost $0.074. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# port_authority: direct design

## 1. Identity & the one question
- **Class and corporation:** Elite, Meridian. Appears at L3–L6 (about one per layer there), so it is L5–6 pressure with a teachable P1.
- **No baseline row.** I estimated from the wheel.
- **Fantasy:** a customs checkpoint. First it inspects: a wall of Weight and a toll on your RAM. Then it impounds: the wall opens, but it taxes the quality of your landings.
- **P1 Inspection asks:** "Is steering worth the toll?" Resistance 2 makes nudges expensive, and Priority drains RAM. The answer that shortens the fight is to skip nudging. Use spin cards, which lose only the first 2 ticks to resistance, or accept the landing and push the damage.
- **P2 Impound asks:** "Can you keep your Perfects?" Steering is now free, but Demurrage stacks TIER_DOWN on your slices. The answer that shortens the fight is to burst early in P2, and to Cleanse or Encrypt the slice that carries your damage.
- **Distinct from the rest of Meridian:**
  - Conveyor Warden and Drone Dispatcher own orbit and drones.
  - The Logistics Director owns the parasite ring and the respin lock.
  - This elite is the only one that combines Weight with a tier tax.

## 2. Phase plan
Flat amounts below are T1 base values. They get × `enemy_damage_by_tier` [1.0, 1.3, 1.69, 2.2] per R2. RAM drain is not scaled.

**P1 Inspection (100 → 50 %)**

| Field | Value |
|---|---|
| Needles | 1, fixed at tick 0 |
| Hub | Customs Wall: resistance 2, restored each turn (existing) |
| Statuses, listeners | none |

| Slice | Ticks | Effect | Sub-tick map |
|---|---|---|---|
| Hold | 6 | BLOCK 6 FLAT | W W G G W W (no Perfect: mostly a weak block) |
| Shim | 5 | 6 damage | W G P G W |
| Priority | 5 | drain 3 RAM (existing `priority.tres`) | W G P G W |
| Shim | 5 | 6 damage | W G P G W |
| Tariff (Overflow) | 4 | 10 damage | W G G W (a big hit that can't Perfect, and half its landings are weak) |
| Priority | 5 | drain 3 RAM | W G P G W |

The sizes sum to 30.

**P2 Impound (50 → 0 %)**

| Field | Value |
|---|---|
| Needles | 1, fixed at tick 0 |
| Hub | Wall Down: resistance 0 (`hub_override`) |
| Statuses | Demurrage applies TIER_DOWN ×1 to your slice under the pointer, stacking |
| Listeners | none |

| Slice | Ticks | Effect | Sub-tick map |
|---|---|---|---|
| Shim | 6 | 6 damage | W W G G W W |
| Demurrage | 5 | 2 damage + TIER_DOWN ×1 | W G P G W |
| Tariff (Overflow) | 5 | 12 damage | W G P G W |
| Priority | 4 | drain 3 RAM | W G G W |
| Demurrage | 5 | 2 damage + TIER_DOWN ×1 | W G P G W |
| Null | 5 | nothing | W G P G W |

The sizes sum to 30. No Hold: the enemy's defense goes away, which opens the burst window.

**Transition P1 → P2:**
- The wheel is overridden (`wheel_override` plus `hub_override`: resistance 2 → 0).
- Damage parks at the floor, ceil(max × 0.5), per R3. The excess is lost.
- Statuses are kept with the R6 remap. P1 applies none, so `cleanse_on_enter` = NONE.
- The phase line plays and the P2 layout is revealed.

## 3. Sustain and intake
- **Sustain:** none. The only mitigation is Hold. Its expected block is 20 % of ticks × 6 × tier factor × a 0.8 tier mean ≈ 1.0 per turn at T1. That is about 11 % of the reference 9 damage per turn, under the 30 % cap. I fold it into the budget as a ~3 HP margin.
- **Intake per turn** (raw at the reference player, before the player's block; a landing-tier mean of about 0.85 is already applied):

| Tier | P1 | P2 |
|---|---|---|
| T1 | ≈ 2.8 | ≈ 3.3 |
| T2 | ≈ 3.7 | ≈ 4.3 |
| T3 | ≈ 4.7 | ≈ 5.6 |
| T4 | ≈ 6.2 | ≈ 7.3 |

- **Intake is above 0.** P2 adds about 0.7 RAM per turn from Priority plus the tier tax. Stack growth is the real pressure.

## 4. HP by tier
Formula: `reference_dpt[t]` × 3.5 turns × 1 needle per phase, with no sustain.

| Tier | Ref dpt | Per phase | Total | Elite band | In band |
|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 63 | 56–72 | yes |
| T2 | 11 | 38.5 | 77 | 68–88 | yes |
| T3 | 14 | 49 | 98 | 88–112 | yes |
| T4 | 18 | 63 | 126 | 112–144 | yes |

- **`hp_by_tier`:** [63, 77, 98, 126]. The threshold is 0.5, so each phase gets half. Today's 144 is above the T3 band.
- **Why single needle:** it keeps the budget at one needle per phase. A second reader (as today) doubles the budget and would push the elite out of band. The elite band assumes 1 needle.

## 5. Enrage
**Default** (start turn 8, every 5 turns, +25 % damage). The expected fight is 6–8 turns, so the first step lands only on slow play. I authored nothing: the fight's pressure is Demurrage stacking, and enrage is only a backstop.

## 6. Buffs and counter Exploits
n/a (elite).

## 7. Counterplay
**P1**
- **Good player:**
  - Plays spin cards, not nudges (a 5-tick spin loses only 2). Uses the free nudge only to push Tariff or a Priority off the pointer.
  - Nudges a Hold landing to the weak edge. This is cheap, because a 6-tick Hold has no Perfect.
  - Keeps RAM above the Priority drain.
  - Banks burst into P1's 49 HP, because P1 is short.
- **Weak player:**
  - Burns RAM nudging against resistance 2, then eats Priority drains and has nothing left for P2.
  - Respins (blocked by the wall) or Flips (blocked) and loses the card.

**P2**
- **Good player:**
  - Spends the opening turn of P2 on burst while their tiers are clean.
  - Moves Demurrage off the pointer (nudges are free of resistance now) or Cleanses and Encrypts the slice that carries their damage.
  - Realises TIER_DOWN ×2 turns a Perfect into WEAK. It is better to stack it on a utility slice than on the Overflow slice.
- **Weak player:** lets Demurrage keep landing on their best slice, then sees halved output and no Perfect hooks. The fight stalls past the turn-8 enrage.

## 8. Systems needed
- **N2** tier base-value tables (`hp_by_tier`, damage factor).
- **N3** phases on an elite, with threshold parking.
- **N4** enrage.
- **N8 + N9** for TIER_DOWN. Data-only fallback: use the existing PARASITE status (halves output). Same question, blunter; keep it until N8/N9 land.
- **N12** for the variable sizes. Data-only fallback: six 5-tick slices (Hold, Shim, Priority, Shim, Tariff, Priority; Demurrage replaces Hold and Null in P2). The design survives but loses the weak-block and weak-Tariff edge nuance. Not recommended: the Hold edge is the interesting nudge.
- **N19** for the sim metrics.
- No N5, N6, N7 or N10 needed.

## 9. Delta vs today
- **Kept:** the id; the Meridian theme (Priority, Overflow as the airmail-style big hit); resistance 2 as the wall; `cycle_reward = 35`.
- **Changed:**
  - 144 HP becomes [63, 77, 98, 126].
  - Two needles (0/15) become one needle.
  - A second phase (Impound) is added with a Demurrage slice and the wall dropping to 0.
  - Shim/Overflow amounts are now tier-scaled from base values.
- **`heat_effects`:** the current file has none. Decision: do not add any. Heat modifiers already come from Grid thresholds (R2: tier and Heat stay out of enemy mechanics).

## 10. Predicted sim check
Estimated from the wheel; no baseline row exists.
- **Turns:** about 6.5–7.5 (2 phases × 3–4 turns), p90 ≤ 9.
- **Win %:**

| Tier | Win % | Why |
|---|---|---|
| T1–T2 | ≥ 95 | Intake is below 5 per turn. |
| T3 | ≈ 90 | Demurrage costs about 1 turn if left alone. |
| T4 | ≈ 85–90 | Intake of 6–7 is mild, but a full RAM drain plus TIER_DOWN could stall a weak player. |

- **Compared with today:** the 144 HP and 2-needle intake gave roughly 2× the fight length (≈ 12 turns, my estimate).

## 11. Open questions
Q: Keep one needle (budget-clean), or allow two readers in P1 and cut P1's HP share to 1 turn?
Q: Does TIER_DOWN on a WEAK landing floor out at WEAK, or can it drop below (Ruling 11 on statuses on weak landings)?
Q: Is "no Perfect" on a 6-tick Hold too punishing for the enemy's own block?
Q: Does `reference_dpt` assume nudge use against resistance 2? I assumed it does not, since the ref player skips nudges.
Q: Should Priority drain RAM only on Good-or-better, so a weak landing is a real escape?
