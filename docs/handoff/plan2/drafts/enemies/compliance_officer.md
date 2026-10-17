<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__compliance_officer; status ok; tokens in 18810 cache-write 0 cache-read 32007 out 3348; cost $0.039. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# compliance_officer: direct design

## 1. Identity & the one question
- **Class:** Normal, 1 phase, 3-4 turns, no enrage. Solace, the compliance enforcer.
- **Layers:** L1-2 teaching (T1 Sites, the first "my nudges are not free" fight) and L5-6 pressure at T2-T3, where it is the Solace fight that punishes sloppy nudging.
- **The one question:** *"What does your landing cost you?"* Every Solace enemy asks about damage or sustain. This one asks about **manipulation economy**. It is a locked wheel, and the only thing it taxes is the player's wheel work.
- **Answer that shortens the fight:** don't fight the lock. Take the free nudge on your own wheel, and let the 12-damage Overflow tell you where to be. Pay RAM only when the pointer is exactly one tick from a Perfect. Hub Breach and Ghost's resistance-ignoring first nudge are the premium answers.
- **Today's problem:** resistance 3 does nothing to a Perfect-heavy bot (94 % Perfect, 3.0 turns at T1), but testers report "I couldn't find a way to make progress" (12+ turns). The lock blocks Flip and Respin entirely and is an invisible wall, and the fight has no moment where the player can win it by reading.

## 2. Phase plan
One phase, no threshold, no floor. Needle uneven on purpose (R10): one pointer on tick 0, and a **Compliance Notice** listener is its only extra rule.

| Item | Design |
|---|---|
| Needles | 1, tick 0, FIXED |
| Hub | Compliance Lock: resistance **2** (was 3), restores each turn. Blocks Flip and Respin while > 0 (unchanged rule). |
| Listener (N6) | **Audit:** on your ON_NUDGE that spends RAM (paid nudge on any wheel), it gains BLOCK 4 FLAT (×tier damage factor). The free nudge never triggers it. |
| Statuses | none |

**Layout (ticks sum 30):**

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Shim 7 (Notice) | 5 | 7 damage to pointer target |
| 2 | Defrag 6 | 4 (W G G W, no Perfect) | BLOCK 6 FLAT |
| 3 | Shim 7 | 5 | 7 damage |
| 4 | Overflow 12 (Penalty) | 3 (G P G) | 12 damage, narrow window |
| 5 | Shim 7 | 7 (W W G P G W W) | 7 damage, wide, the safe landing |
| 6 | Null | 6 | nothing |

Sum: 5+4+5+3+7+6 = 30.

**Why this layout:** Overflow shrinks to 3 ticks, so it is hard to land by luck but easy to steer away from (1 tick). The 7-tick Shim is the "safe" slice. Defrag has no Perfect, so landing the enemy on its own block is a weak-for-it result and the player pays nothing extra. The enemy's wheel is spun by the start-of-turn respin; you read it, then choose between a free nudge (no Audit block) or a paid nudge to push it onto Null.

**Transition:** none (1 phase).

## 3. Sustain & intake
- **Sustain:** none (no heal). Only conditional BLOCK 4 from Audit when you pay RAM. Cap check: reference dpt T1 9; 30 % = 2.7/turn. Audit fires at most once or twice a turn if the player spends RAM; expected 4 × ~0.5 paid nudges/turn ≈ 2/turn ≤ 2.7. OK. The Defrag slice adds BLOCK 6 only when it resolves (1 in 6 landings, ~1 per turn on average of the 6-wide wheel, weighted by size 4/30 ≈ 13 %), ≈ 0.8/turn. Total worst case ≈ 2.8 ≈ cap at T1. Flag in Q1.
- **Intake per turn** at the reference player (random start position, 1 free nudge): the weighted expected hit by tick share, assuming a lazy player who nudges to avoid Overflow but not onto Null:
  - Shim slices: (5+5+7)/30 = 57 % × 7 = 4.0; Overflow 10 % × 12 = 1.2; others 0. ≈ 5.2/turn raw, ≈ 2.5-3.5 after one free nudge. Target 2-4 at T1, so above 0 and in line with the baseline's 2.5 taken/turn.
  - Scaling by the tier factor: 1.0 / 1.3 / 1.69 / 2.2 → ≈ 3 / 4 / 5 / 6.6 per turn.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70.

Budget: `reference_dpt × 3.5 turns × 1 needle` minus sustain (≈ 2 × 3.5 = 7 at worst; use 1.5 expected ≈ 5).
- T1: 9 × 3.5 = 31.5 − 3 ≈ 29 → **32**
- T2: 11 × 3.5 = 38.5 − 3 ≈ 35 → **38**
- T3: 14 × 3.5 = 49 − 3 ≈ 46 → **50**
- T4: 18 × 3.5 = 63 − 3 ≈ 60 → **62**

`hp_by_tier` = [32, 38, 50, 62]. Today is 50 at all tiers scaled by a multiplier, giving 64-128 at T3 per the brief.

## 5. Enrage
Off (Normal). A 3-4 turn fight has no room for a stall, and the Audit block is capped by the player's own RAM spend.

## 6. Buffs and counter Exploits
Not applicable (normal).

## 7. Counterplay
- **Good player:** reads the start-of-turn wheel. If the pointer sits on a 5/7-tick Shim, takes the free nudge to put it on a Good or Perfect of your own wheel and eats 7 as the price. If it sits on Overflow's 3-tick window, one free nudge of your own does not move its wheel, so the answer is a card (Spin, with resistance 2 absorbing the first 2 ticks) or a SANDBOX. Never pays RAM to nudge a block into it. Hub Breach turns off resistance and Audit stays, so you still choose.
- **Weak player:** spends RAM nudges every turn "to be precise" and feeds Audit; fights at 6+ turns. Burns Flip and Respin cards into the lock. Lands on its Defrag with no Perfect and wonders why.

## 8. Systems needed
| System | Use | Fallback |
|---|---|---|
| N1 | FLAT block × tier factor | Data-only (amount is flat today) |
| N2 | `hp_by_tier` | Keep the single `hp` field with a multiplier |
| N6 | Audit listener on paid nudge | Drop Audit; the fight is then slices and resistance only |
| N12 | Variable slice sizes (3, 4, 6, 7) | Use 5-tick slices; the Overflow window then stays 5 and the design loses its main read |
| N11 | not required (pointer at tick 0) | n/a |

## 9. Delta vs today
- **Kept:** id, corporation, the six-slice composition (Shim 7 ×3, Defrag 6, Overflow 12, Null), Compliance Lock hub, `cycle_reward`.
- **Changed:** slices resized (N12); resistance 3 → 2; Audit listener added; HP 50 flat → [32, 38, 50, 62].
- **heat_effects:** keep the Heat 50+ "Audit" drain 1 RAM on attacks, but rename it **Late Fee** to avoid the clash with the new Audit listener (rename is a placeholder). It stacks cleanly: a paid nudge and a hit both tax RAM, which is the fight's theme.

## 10. Predicted sim check
Baseline: T1 3.0 turns, 100 % win; T2 5.1; T3 7.9, 95 %; T4 12.6, 70 %.
- **Predicted:** T1 3.3 turns, 100 %; T2 3.6, 100 %; T3 3.9, ≥ 95 %; T4 4.0, ≥ 90 %.
- **Why:** HP now follows the 3.5-turn budget instead of a 1.3× multiplier on 50, which removes the T3-T4 tail. Resistance 2 lowers the lock's friction, while Audit adds a RAM cost for careless play. Intake rises to ~3-6.6 per turn, up from 2.5-4.4 baseline, because the 3-tick Overflow window makes Perfect landings against you rarer but each tier factor still applies.

## 11. Open questions
Q: Is Audit's trigger "any paid nudge" right, or only paid nudges on the enemy wheel, so the player may still spend RAM on their own wheel freely?
Q: Resistance 2 vs 3: does a 2-tick absorb still make Spin cards meaningfully worse, or does it vanish into the noise?
Q: Should the Defrag slice (4 ticks, no Perfect) read as a "free landing" or be 5 ticks so it can be a Perfect block the player must deny?
Q: Does Late Fee (Heat 50+) double-dip with Audit unfairly for RAM-starved Ghosts, who rely on paid nudges?
Q: If N6 slips, is the fight acceptable as data-only (slices and resistance), or should it wait for the listener?
