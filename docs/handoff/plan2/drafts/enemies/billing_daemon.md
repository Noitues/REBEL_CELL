<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__billing_daemon; status ok; tokens in 18849 cache-write 0 cache-read 32007 out 3077; cost $0.037. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# billing_daemon: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, no enrage. Solace, appears L1-2 as the teaching fight for the RAM economy and returns in L5-6 as a pressure fight at T2-T3.
- **Fantasy:** an invoice collector. It bills you for every action you take.
- **The one question:** *"What is your RAM worth this turn?"* Its hits drain RAM, and its wheel carries a listener that taxes your **paid nudges** (N6 ON_NUDGE). The free nudge is always safe. The answer is to spend the free nudge, play cards instead of paying for nudges, and steer its pointer onto Defrag or Null rather than fighting the wheel with RAM.
- **What shortens the fight:** killing it fast. It has no sustain and a single Defrag, so any burst line ends it. The tax only punishes the player who tries to fix a bad landing by overpaying.
- **Why it is distinct:** Collections Agent and Compliance Officer are resistance and pressure enemies, and the Dosage Dispenser corrupts. This one is the only Solace normal that attacks the RAM economy itself.

## 2. Phase plan
Single phase. HP floor: none (last and only phase). One needle at tick 0, FIXED.

| Field | Value |
|---|---|
| Needles | 1, tick 0, fixed |
| Hub rule | none |
| Statuses / parasites | none |
| Listener | **Late Fee** (N6): when the player pays RAM for a nudge (not the free one), the Daemon gains BLOCK 3 FLAT (×tier damage factor). Cap: once per turn, so a heavy nudger gets 3, not a spiral. |

**Wheel (sizes sum to 30, N12):**

| Slice | Ticks | Effect | Mode |
|---|---|---|---|
| Invoice (Shim) | 5 | 7 damage, drain 1 RAM | FLAT |
| Overdue (Overflow) | 4 (no Perfect: W G G W) | 12 damage, drain 2 RAM | FLAT |
| Defrag | 6 | BLOCK 6 | FLAT |
| Invoice (Shim) | 5 | 7 damage, drain 1 RAM | FLAT |
| Statement (Shim) | 5 | 5 damage, drain 3 RAM | FLAT |
| Null | 5 | nothing | n/a |

Total 5+4+6+5+5+5 = 30.

- **Why the 4-tick Overdue:** with no Perfect, a landing on it is only ever Good or WEAK, so the big hit is never a "perfect aimed" slice. The player decides whether to dodge it by one tick, which is cheap to see and cheap to do.
- **Why Statement:** a low-damage, high-drain slice makes RAM loss a different threat from HP loss. Landing on it hurts the economy more than the body.
- **Transition:** none (single phase).

## 3. Sustain and intake
- **Sustain:** none. Its only defense is Defrag 6, which is temporary BLOCK, not healing, plus Late Fee BLOCK 3 at most once per turn. Worst case, the player nudges for pay once per turn: the sustain is 3 × 1.0 = 3 per turn at T1, against the 30 % cap of 9 × 0.3 = 2.7 at T1. That is a hair over the cap, so Late Fee is **BLOCK 2** at T1 base: 2 per turn, which is 22 % of the T1 reference of 9. At T4 it is 2 × 2.2 = 4.4, which is 24 % of 18. Under cap.
- **Intake per turn at the reference player (T1, one needle):** the expected slice is the average over a random landing, minus the player's steering. Unsteered mean damage ≈ (7+12+0+7+5+0)/6 ≈ 5.2 per turn, and RAM drain ≈ (1+2+0+1+3+0)/6 ≈ 1.2 per turn. The reference player steers away from half of it, so intake lands near **2.5-3 HP and ~0.8 RAM per turn**, above 0 as required. That is higher than today's 1.22 HP per turn, because the 12-damage slice now bites.

## 4. HP by tier
Class band (Normal, 1 phase): 28-36 / 34-44 / 44-56 / 56-70.
Budget: reference_dpt × 3.5 turns × (1 needle) − sustain × 3.5.

| Tier | Ref DPT | Gross | Sustain (Late Fee) | **HP** |
|---|---|---|---|---|
| T1 | 9 | 31.5 | 2 × 3.5 = 7, but only if the player pays; budgeted at half = 3.5 | **30** |
| T2 | 11 | 38.5 | 2.6 × 3.5 × ½ ≈ 4.5 | **38** |
| T3 | 14 | 49 | 3.4 × 3.5 × ½ ≈ 6 | **48** |
| T4 | 18 | 63 | 4.4 × 3.5 × ½ ≈ 7.7 | **60** |

`hp_by_tier` = [30, 38, 48, 60]. Today is 42 flat, scaled by the tier, so T3 was about 64.

## 5. Enrage
Default for the Normal class: **off**. A 3-4 turn fight needs no clock.

## 6. Buffs and counter Exploits
Bosses only. n/a.

## 7. Counterplay
- **Good player:** reads the preview, spends the free nudge to move off Overdue or Statement, plays cards in preference to paid nudges, and bursts. If a paid nudge is truly the only way to avoid Overdue, it is worth it; the 2 BLOCK is a small price.
- **Weak player:** nudges every turn at 1 RAM each, hands the Daemon BLOCK, runs short of RAM for cards, and then takes the Statement drain on top. That spiral is the lesson of the fight.

## 8. Systems needed
- **N1** amount modes: FLAT × tier damage factor. Data-only fallback: authored flat numbers.
- **N2** `hp_by_tier`. Fallback: keep `hp = 42` with the old scale.
- **N6** the Late Fee listener on ON_NUDGE. **Fallback:** drop the listener and keep the wheel. The fight still teaches steering, but loses the RAM-tax question.
- **N12** variable slice sizes (4/6-tick slices). **Fallback:** keep six 5-tick slices; Overdue then has a Perfect and the "never Perfect" trick is lost.
- No parasites, statuses or phase systems needed (N3 is not required for a single phase).

## 9. Delta vs today
- **Kept:** the six-slice concept, the drain-on-hit identity, Shim 7 / Defrag 6 / Overflow 12 / Null, one needle at tick 0, `cycle_reward = 15`.
- **Changed:**
  - HP is 42 flat, now `hp_by_tier` [30, 38, 48, 60].
  - New Statement slice (Shim 5, drain 3) replaces one Shim 7.
  - Overdue shrinks to 4 ticks and Defrag grows to 6.
  - New Late Fee listener (N6).
- **heat_effects:** none exist on this file, so none are retired.

## 10. Predicted sim check
Baseline (win %, turns, taken/turn):

| Tier | Baseline | Predicted |
|---|---|---|
| T1 | 100 %, 2.5 turns, 1.22 | ~100 %, 3.3 turns, ~2.5 |
| T2 | 100 %, 4.2, 1.36 | ~100 %, 3.6, ~3.4 |
| T3 | 100 %, 7.0, 1.31 | ~98 %, 3.8, ~4.3 |
| T4 | 100 %, 10.8, 1.73 | ~95 %, 4.0, ~6 |

Why: the lower HP cuts the long T3-T4 grind (7-11 turns today) down to the 3-4 turn target, while the 12-damage slice and Statement drain lift the intake above the near-zero baseline. The Defrag at 6 ticks is the only thing that extends the fight, and it is passive.

## 11. Open questions
Q: Should Late Fee scale as a PERCENT of the Daemon's max HP, so it stays proportionate across tiers, or stay FLAT × tier factor?
Q: Does the free nudge after a card-granted nudge count as "paid" for Late Fee, or only RAM-costed nudges?
Q: Is draining 3 RAM on one slice too punishing at L1-2, given the RAM cap of 12 and the start of 6?
Q: Should Late Fee be hidden until first triggered, or shown on the intent chip from turn 1 (proposed: shown, since the preview must equal the result)?
