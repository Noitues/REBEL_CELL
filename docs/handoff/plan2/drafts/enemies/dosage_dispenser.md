<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__dosage_dispenser; status ok; tokens in 18428 cache-write 0 cache-read 32007 out 4475; cost $0.044. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# dosage_dispenser: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, 3-4 turns, no enrage. Solace, appears in L1-2 as the teaching fight for **corruption as a RAM tax** (R9) and in L5-6 as pressure on an already-stressed economy.
- **Today's failure:** 0.05-0.84 damage taken per turn. Its wheel is 4 of 6 slices that do nothing to a sane player. Its Shim 6 lands on only about 1 pointer read in 3, and the Dose is invisible in its effects, because CORRUPTED is an inert self-damage trap that the player never steps on.
- **The one question: "Which of your slices is it dosing, and can you afford to read it?"** It is a metronome that stamps CORRUPTED onto your wheel every turn. Under R9 a corrupted slice doubles the RAM cost of every card or nudge made while the pointer sits on it. The player has to decide each turn whether to pay the tax, cleanse, steer around the corrupted slices, or burst it down before the tax compounds.
- **Which answer shortens the fight:** killing it fast. Each turn it stays alive adds up to one more corrupted slice, so the RAM tax grows. Burst plus steering finishes in 3 turns. A player who dawdles gets taxed into passivity.
- **Distinct from siblings:**
  - Collections Agent and Billing Daemon: damage/RAM pressure.
  - Triage Unit: sustain.
  - Compliance Officer: resistance.
  - Care Swarm: multi-body.
  - Dispenser is the only normal whose entire threat is the corruption ledger.

## 2. Phase plan
Single phase, no threshold, no parking (R3: the last/only phase has no floor).

| Field | Value |
|---|---|
| Phase | 1 "Dispensing" (100 % → 0 %) |
| Needles | 1, tick 0 (fixed). No orbit. |
| Hub | none (no passive, no resistance) |
| Statuses used | CORRUPTED (R9 RAM ×2) on the player's wheel |
| Listeners | none |

**Wheel layout (variable sizes, sum 30, R11):**

| # | Slice | Ticks | Effect | Mode |
|---|---|---|---|---|
| 1 | Dose A | 4 | 3 damage + CORRUPTED on 1 random non-NULL player slice | FLAT (damage, ×tier factor); corruption count FLAT 1 |
| 2 | Shim | 5 | 5 damage | FLAT |
| 3 | Dose B | 3 | CORRUPTED on 1 random non-NULL player slice, no damage | FLAT 1 |
| 4 | Defrag | 6 | BLOCK 6 | FLAT |
| 5 | Shim | 5 | 5 damage | FLAT |
| 6 | Null | 7 | nothing | n/a |

Sum = 4+5+3+6+5+7 = **30**.

**Design notes on size (R11):**
- Dose B is a 3-tick slice (G P G). It is the smallest and only 1 tick wide for Perfect, so it is not readily steerable by the player, but it has no sub-tick WEAK edge.
- Dose A is a 4-tick slice (W G G W, no Perfect). Its damage is the only rider that is tier-sensitive.
- Null is 7 ticks wide (W W G P G W W) and Defrag 6 ticks. These two big, safe slices are the "good" parking places for its needle.
- Needle position is random each turn from the start-of-turn respin. A uniform tick lands on a slice proportionally to its size, so the odds per turn are:

| Slice | P(resolves) |
|---|---|
| Dose A | 13 % |
| Dose B | 10 % |
| Shim ×2 | 33 % |
| Defrag | 20 % |
| Null | 23 % |

- P(a Dose resolves) ≈ 23 % per turn raw. That is too low to carry the fight, so the data below adds a **second-order rule**: the Dispenser **doses at end of turn on its hub**.

**Hub rule: Standing Prescription (new hub passive, via ON_TURN_END listener, N6-style but only against its own state, so data-only):** at the end of each enemy resolve, if no Dose slice resolved this turn, apply CORRUPTED (FLAT 1) to one random non-NULL player slice, drawn from the `combat` RNG stream and logged for preview (the preview shows "+1 CORRUPTED (random: shows odds)" per GDD 2.10).
- **Why:** it guarantees the one question is asked every turn, even if the needle parks on Null.
- **Caveat:** a random target means a preview with odds, not a single result; this is an existing rule (2.10, "random targets show odds"). The combat RNG stream is a named stream, so it stays deterministic.
- **Fallback:** if hub-timing is not available, replace Null with Dose C (5 ticks) and drop the hub rule (see §8).

**Transition:** none, single phase.

## 3. Sustain and intake
- **Sustain:** one source, the 6-tick Defrag, BLOCK FLAT 6 (×tier factor), temporary, expires next turn. It is not healing. 20 % chance per turn × 6 ≈ 1.2 expected damage absorbed per turn at T1. That is **≈ 13 % of the T1 reference 9 dpt**, under the 30 % cap. No heal, no shield.
- **Intake per turn at the reference player (R2 reference 9/11/14/18):** expected raw hit damage per turn at T1:
  - Shim: 33 % × 5 = 1.65
  - Dose A: 13 % × 3 = 0.4
  - Total ≈ **2.0 per turn** at T1, plus the RAM tax, which is the real intake.
- **By tier** (×1.0 / 1.3 / 1.69 / 2.2): 2.0 / 2.6 / 3.4 / 4.4 per turn, above 0 at every tier (baseline 0.05-0.84).
- **RAM intake (the real pressure):** corruption count after n turns ≈ min(n, 5) with roughly 1.2 stamps per turn (hub guarantee + Dose slices). RAM economy is +4 per turn, so by turn 3 about 3 of the player's 5 non-NULL slices are CORRUPTED. Any card or nudge made on a corrupted slice then costs 2×.

## 4. HP by tier
R2 normal band: 28-36 / 34-44 / 44-56 / 56-70.
Phase budget = reference_dpt × 3.5 turns − sustain × 3.5 (sustain is BLOCK, which only reduces a hit, so I count it as ~1.2 × 3.5 ≈ 4 HP-equivalent at T1, scaled by tier factor).

| Tier | dpt | Budget | Sustain adj. | HP |
|---|---|---|---|---|
| T1 | 9 | 31.5 | −0 (BLOCK is on me, not its HP) | **32** |
| T2 | 11 | 38.5 | | **40** |
| T3 | 14 | 49 | | **50** |
| T4 | 18 | 63 | | **62** |

All inside the bands. BLOCK 6 shields the enemy's own HP from the player's hits, as defense. The player's reference dpt is therefore reduced by roughly 1.2 × factor per turn; I leave it out of HP and note it appears in the simulator as a +0.3 turn drift.

Current hp 38 is T1-sized too large against the new T1 band, so the data moves to `hp_by_tier = [32, 40, 50, 62]`.

## 5. Enrage
**None** (normal, R4 default off). A 3-4 turn fight is its own clock, because the corruption ledger rises each turn.

## 6. Buffs and counter Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:**
  - Reads the preview. At turn 1 spends the free nudge to steer its needle onto Null or Defrag, or aims at its Dose B 3-tick slice with a precise nudge to turn it WEAK.
  - Burns it in 3 turns with Overflow plus a Perfect.
  - If two slices are already corrupted, avoids the corrupted ones and plays cards while the pointer reads clean slices.
  - A Cleanse card or an Encrypt on a key slice (ENCRYPTED absorbs the next status) is a strong answer.
  - Pays 2× RAM only where the payoff is a Perfect on Overflow.
- **Weak player:**
  - Ignores corruption and keeps nudging with the pointer on a corrupted slice, then bleeds RAM and cannot afford the card that would have ended the fight.
  - Spends cards defensively against a 2.0 dpt enemy.
  - Never steers its needle off Dose.
  - Ends turn 4+ with the whole wheel corrupted and RAM-locked.
- **Why this works as a teacher:** the only way to lose a fight against it is economic. The damage on its own is a rounding error.

## 8. Systems needed
| Need | N# | Data-only fallback |
|---|---|---|
| CORRUPTED as RAM ×2 | N9 | None: this is the entire point. Until N9, CORRUPTED is the old self-damage and the design degrades to a weak enemy again. |
| Amount modes (FLAT; flat enemy amounts × tier factor) | N1 | Authored values per tier by hand |
| Tier tables (`hp_by_tier`, `enemy_damage_by_tier`) | N2 | Keep HP multiplier |
| Variable slice sizes (4/5/3/6/5/7) | N12 | Use six 5-tick slices; the P(Dose) odds become 33 % and only the 2-needle odds shift |
| Hub end-of-turn dose (Standing Prescription) | N6 (self-listener on its own wheel resolve) | Replace Null with a third Dose slice (5 ticks), delete the hub rule |

Recommended fallback if N6/N12 slip: 6 × 5-tick slices = Dose, Shim 5, Dose, Defrag 6, Shim 5, Dose-lite (CORRUPTED, no damage). It still works under N9.

## 9. Delta vs today
- **Kept:** id, corporation, Dose/Shim/Defrag/Null slice vocabulary, single needle at tick 0, cycle_reward 15.
- **Changed:**
  - HP 38 → `hp_by_tier` [32, 40, 50, 62].
  - Wheel sizes 5/5/5/5/5/5 → 4/5/3/6/5/7.
  - Second Dose becomes a pure-corruption slice with no damage, and the first Dose gains 3 damage.
  - New Standing Prescription hub rule.
  - Shim 6 → 5 and Defrag 5 → 6 (flat amounts scale by tier factor under R2/N1).
- **Heat effects:** none present on the file, none added.
- **Description text:** "Stamps CORRUPTED on your wheel; every corrupted slice doubles what you pay."

## 10. Predicted sim check
| Tier | Turns (pred.) | Win % | Baseline |
|---|---|---|---|
| T1 | 3.2 | 100 | 2.5 turns, 100 % |
| T2 | 3.7 | 100 | 3.6, 100 % |
| T3 | 4.0 | 97 | 5.2, 100 % |
| T4 | 4.3 | 93 | 8.0, 100 % |

**Why:**
- Lower HP at T3-T4 (50/62 vs today's scaled values) cuts turns, which today run to 8 at T4.
- Taken/turn rises from 0.05-0.84 to roughly 2.0-4.4, plus the RAM tax.
- The win rate drops slightly at high tiers because of the tax. Pass criteria are ≥95 % at T1-T2 and ≥90 % at T3.
- If N9 is absent, the numbers revert to the baseline and the fight again fails the intake test.

## 11. Open questions
Q: Does the Standing Prescription hub dose (guaranteed 1 per turn) feel fair, or should it be skipped on a turn where a Dose slice already resolved (as drafted)?
Q: Should CORRUPTED cap at a share of the wheel (e.g. at most 3 of 5 non-NULL slices) so a 4-turn fight cannot fully lock a player?
Q: Does a free nudge on a corrupted slice cost 1 RAM (R9 doubles RAM only for paid actions)?
Q: Is a 3-tick Dose B (no WEAK edge, 1 Perfect tick) too hard to steer past with a 1-tick nudge granularity?
Q: Do ENCRYPTED slices on the player's wheel stop the hub dose entirely, or does the hub bypass them?
