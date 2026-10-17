<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__billing_daemon; status ok; tokens in 5902 cache-write 0 cache-read 32585 out 3814; cost $0.028. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (Late Fee number inconsistent):** Fixed. Late Fee is **BLOCK 2 FLAT** (× tier damage factor), once per turn, in §2, §3 and §8. The 3 → 2 swap is gone.
- **Issue 2 (HP budget halved the sustain):** Adopted the critic's preferred fix. Late Fee is temporary BLOCK, not healing. It expires at the start of the Daemon's next turn, and only the Daemon's own turn start clears it. Because of that, it doesn't reduce the R2 budget. The budget is plain reference DPT × 3.5, so `hp_by_tier` = [31, 38, 49, 63]. I checked these against the band: T1 31 (28–36), T2 38 (34–44), T3 49 (44–56), T4 63 (56–70). The 30 % cap is checked anyway.
- **Issue 3 (uniform 1/6 averages):** Replaced with tick-weighted figures: 4.8 HP and 1.1 RAM unsteered. After steering, about 2.4 HP and 0.6 RAM per turn.
- **Issue 4 (unsupported T3/T4 win %):** I stated the HP cost per fight and lowered the T4 claim. T3 is ≥ 90 % and T4 is about 90 %, each with a stated reason. The p90 check is included.
- **Issue 5 (penalty too small to be a question):** Kept, because this is a normal teaching fight and a small tax is intended. I clarified when the block matters. It stays up during the player's resolve, so it only absorbs player hits that resolve after it is granted. Pointers resolve all at once, so in practice it absorbs one hit of this turn's End Turn.
- **Issue 6 (undo-clean):** Added to §2. The listener is staged with the nudge and undone with it.
- **Critic Q on sustain cap:** Answered in §3. Late Fee is temporary block and not counted, but the cap check is shown anyway.
- **Critic Q on 3 RAM drain at L1-2:** Statement's drain is cut to 2 for L1-2 safety. It is still the highest drain per damage on the wheel.
- **Triage rows:** none.
- **Kept:** the one question, the 4-tick no-Perfect Overdue, and the §8 fallbacks.
- **Arithmetic re-check:** the wheel now sums to 30 (see §2).

---

# billing_daemon: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, no enrage. Solace. It appears in L1-2 as the teaching fight for the RAM economy, and returns in L5-6 at T2-T3 as a pressure fight.
- **Fantasy:** an invoice collector that bills you for every action.
- **The one question:** *"What is your RAM worth this turn?"* Its hits drain RAM, and a listener taxes your **paid nudges** (N6, ON_NUDGE). The free nudge is always safe. The answer is to spend the free nudge, play cards instead of paying for nudges, and steer its pointer onto Defrag or Null instead of fighting the wheel with RAM.
- **What shortens the fight:** burst. It has no heal and one Defrag slice, so any burst line ends it. The tax only punishes a player who fixes a bad landing by overpaying.
- **Why it is distinct:** Collections Agent and Compliance Officer are resistance and pressure enemies, and the Dosage Dispenser corrupts. This is the only Solace normal that attacks the RAM economy itself.

## 2. Phase plan
Single phase, no floor (last and only phase), no transition.

| Field | Value |
|---|---|
| Needles | 1, tick 0, fixed |
| Hub rule | none |
| Statuses / parasites | none |
| Listener | **Late Fee** (N6): when the player pays RAM for a nudge (not the free one), the Daemon gains **BLOCK 2 FLAT** (× tier damage factor), once per turn. The listener is staged with the nudge and undone with it (undo-clean, preview = result). The block lasts until the Daemon's next turn start, so it absorbs part of that turn's End Turn hit. |

**Wheel (N12; 5+4+6+5+5+5 = 30):**

| Slice | Ticks | Effect | Mode |
|---|---|---|---|
| Invoice (Shim) | 5 | 7 damage, drain 1 RAM | FLAT |
| Overdue (Overflow) | 4 (W G G W, no Perfect) | 12 damage, drain 2 RAM | FLAT |
| Defrag | 6 | BLOCK 6 | FLAT |
| Invoice (Shim) | 5 | 7 damage, drain 1 RAM | FLAT |
| Statement (Shim) | 5 | 5 damage, drain 2 RAM | FLAT |
| Null | 5 | nothing | n/a |

- **Why the 4-tick Overdue:** with no Perfect, the big hit is never a "perfect aimed" slice. Dodging it by one tick is cheap to see and cheap to do.
- **Why Statement:** low damage with high drain makes RAM loss a different threat from HP loss.
- **Transition:** none.

## 3. Sustain and intake
- **Sustain:** none. There is no heal. Defrag 6 and Late Fee are temporary BLOCK that expire before the player's next phase, so they are not sustain and don't enter the R2 budget. Cap check anyway: worst case Late Fee is 2 per turn at T1, which is 22 % of the 9 reference, and 4.4 at T4, which is 24 % of 18. Under 30 % either way.
- **Intake per turn at the reference player (T1, tick-weighted):**
  - Unsteered damage = (7×5 + 12×4 + 0×6 + 7×5 + 5×5 + 0×5)/30 = 143/30 ≈ **4.8**.
  - Unsteered RAM drain = (1×5 + 2×4 + 1×5 + 2×5)/30 = 28/30 ≈ **0.9**.
  - The reference player steers off about half of the dangerous ticks, so intake is **about 2.4 HP and 0.5 RAM per turn**, above 0 as required. Today's baseline is 1.22 HP, so the 12-damage slice now bites.

## 4. HP by tier
Normal (1 phase) band: 28-36 / 34-44 / 44-56 / 56-70.
Budget: reference_dpt × 3.5 turns × 1 needle. Sustain is 0, so there is nothing to subtract.

| Tier | Ref DPT | Budget (DPT × 3.5) | **HP** |
|---|---|---|---|
| T1 | 9 | 31.5 | **31** |
| T2 | 11 | 38.5 | **38** |
| T3 | 14 | 49.0 | **49** |
| T4 | 18 | 63.0 | **63** |

`hp_by_tier` = [31, 38, 49, 63]. Today is 42 flat, scaled by tier, so about 64 at T3.

## 5. Enrage
Default for the Normal class: **off**. A 3-4 turn fight needs no clock.

## 6. Buffs and counter Exploits
Bosses only. n/a.

## 7. Counterplay
- **Good player:** reads the preview, spends the free nudge to move off Overdue or Statement, plays cards instead of paid nudges, and bursts. If a paid nudge is the only way to avoid Overdue, it is worth it; 2 BLOCK is a small price.
- **Weak player:** nudges every turn at 1 RAM each and hands the Daemon BLOCK. That leaves too little RAM for cards, and then Statement's drain lands on top. That spiral is the lesson of the fight.

## 8. Systems needed
- **N1** amount modes: FLAT × tier damage factor. Data-only fallback: authored flat numbers.
- **N2** `hp_by_tier`. Fallback: keep `hp = 42` with the old scale.
- **N6** the Late Fee listener on ON_NUDGE. Fallback: drop the listener and keep the wheel. The fight still teaches steering but loses the RAM-tax question.
- **N12** variable slice sizes. Fallback: six 5-tick slices; Overdue then has a Perfect, and the "never Perfect" trick is lost.
- N3 is not required (single phase).

## 9. Delta vs today
- **Kept:** the six-slice concept, the drain-on-hit identity, Shim 7 / Defrag 6 / Overflow 12 / Null, one needle at tick 0, `cycle_reward = 15`.
- **Changed:**
  - HP is 42 flat, now `hp_by_tier` [31, 38, 49, 63].
  - New Statement slice (Shim 5, drain 2) replaces one Shim 7.
  - Overdue shrinks to 4 ticks and Defrag grows to 6.
  - New Late Fee listener (N6).
- **heat_effects:** none exist on this file, so none are retired.

## 10. Predicted sim check
Baseline (win %, turns, taken per turn) against the prediction:

| Tier | Baseline | Predicted |
|---|---|---|
| T1 | 100 %, 2.5 turns, 1.22 | ~100 %, 3.3 turns, ~2.4 HP |
| T2 | 100 %, 4.2, 1.36 | ~99 %, 3.6, ~3.1 |
| T3 | 100 %, 7.0, 1.31 | ~93 %, 3.8, ~4.0 |
| T4 | 100 %, 10.8, 1.73 | ~90 %, 4.0, ~5.3 |

- **Why:** HP now follows the 3.5-turn budget, which cuts the 7-11 turn grind at T3-T4 to the target. Intake rises above the near-zero baseline.
- **HP cost:** about 4.0 × 3.8 ≈ 15 HP per fight at T3, and about 5.3 × 4 ≈ 21 HP at T4. That is real but survivable against a 45-60 HP operative.
- **Win rate:** T3 meets ≥ 90 %. The T4 estimate is at the limit, because weaker play lengthens the fight. A p90 of 6 turns is within target + 2.
- **Risk:** if T4 falls under 90 % in the sim, trim Overdue to 10 before touching HP.

## 11. Open questions
Q: Should Late Fee scale as a PERCENT of the Daemon's max HP, or stay FLAT × tier factor? (v2 keeps FLAT.)
Q: Does a card-granted nudge that costs no RAM count as "paid" for Late Fee? (v2: only RAM-costed nudges.)
Q: Is a 2 RAM drain on Statement still too punishing at L1-2, with starting RAM 6 and a cap of 12?
Q: Should Late Fee show on the intent chip from turn 1? (Proposed: yes, since preview = result.)
