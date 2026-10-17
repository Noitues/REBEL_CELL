<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__rc_template_elite; status ok; tokens in 3706 cache-write 0 cache-read 32007 out 5671; cost $0.035. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# rc_template_elite: direct design

Working name: **Mirror A, "Your Echo"**. Its sibling `rc_template_elite_b` is a separate pass. Note that "Mirror" is also a Firmware name (GDD 6.1) and a card name, so display names need a later pass.

## 1. Identity & the one question

**Class:** Elite, 2 phases, one threshold at 0.5. **Corporation:** REBEL_CELL (the file has `corporation_id = &""`; set it to `rebel_cell`). It is the "your own wheel used against you" elite of the corporation. **Layers:** it appears at L3–L6 on REBEL_CELL Grids. It is a pressure elite rather than a teaching elite, because it has to be read against the player's own wheel.

**Design hook:** it fights with a copy of your outer wheel layout, at your own slice sizes. Today's data is a fixed generic wheel with a 24-damage Overflow, which says nothing about the player. Phase 1 asks which of your slices are dangerous to you. Phase 2 asks whether you can afford a Perfect.

Both phases are built on the same fact: the dangerous slices are the ones you also like to land.

| Phase | The question | The answer that shortens the fight |
|---|---|---|
| P1 Reflection | "Your best slice is my best slice. Which of us lands it first?" | Land your big slice on its wheel while steering its needle off the matching slice on yours. Burst the half before it ramps. |
| P2 Feedback | "Every Perfect you land is paid back." | Land Good instead of Perfect, or pay the echo deliberately for a burst. Tick offsets matter because the needles are uneven. |

**Data-only reading of "copy your wheel":** until a mirror-of-player-wheel system exists, the layouts below are authored fixed wheels that imitate a generic operative (Overflow, Shim, Defrag, Null). The "mirror" is flavour in the data and mechanical only in P2's listener.

## 2. Phase plan

Threshold: **0.50**. The HP floor in P1 is ceil(max HP × 0.5).

### P1: Reflection (100 → 50 %)

| Field | Value |
|---|---|
| Needles | 2, uneven: ticks 0 / 12 (R10, N11) |
| Resistance | 1 passive (as today); restores each turn |
| Hub | none |
| Statuses/parasites | none |
| Listeners | none |

Layout (sum 30):

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Overflow (large) | 6 | 16 dmg FLAT |
| 2 | Shim | 5 | 7 dmg FLAT |
| 3 | Defrag (BLOCK) | 4 | 8 FLAT |
| 4 | Shim | 5 | 7 FLAT |
| 5 | Overflow (small) | 5 | 10 FLAT |
| 6 | Null | 5 | none |

Sizes are 6+5+4+5+5+5 = 30.

Notes:
- **Needle spacing:** needles 12 ticks apart on slices of 4–6 ticks, so one needle is usually on a damage slice while the other is on Defrag or Null. Both needles are rarely dangerous together, and that is the read.
- **Big Overflow:** its 6-tick slice gives sub-ticks W W G G W W, so the Overflow has no Perfect. Reading it at G on a 6-tick slice is a normal landing and cannot be forced into a Perfect-only window. Its danger is size: it is easy to land on.
- **Damage numbers:** Overflow is 16 rather than today's 24, since two needles now hit and the R2 factor applies at T2+.

### P2: Feedback (50 → 0 %)

| Field | Value |
|---|---|
| Needles | 2, uneven: ticks 0 / 11 (shifted with `MIGRATE`, telegraphed) |
| Resistance | 1 (kept) |
| Hub | none |
| Statuses | OUTPUT_DOWN ×1 applied by Echo hits (see below) |
| Listener (N6) | **Echo:** on each player PERFECT landing, deal 5 FLAT to the player (one hit; SANDBOX negates). Not applied on a Good or Weak landing. |

Layout (sum 30):

| # | Slice | Ticks | Effect |
|---|---|---|---|
| 1 | Overflow | 5 | 14 FLAT, pierce (N20) |
| 2 | Shim | 4 | 6 ×2 hits (N20); Good-only window (W G G W) |
| 3 | Null | 4 | none |
| 4 | Shim | 5 | 6 FLAT; applies OUTPUT_DOWN ×1 to the slice under your pointer |
| 5 | Defrag (BLOCK) | 6 | 6 FLAT |
| 6 | Overflow | 6 | 12 FLAT |

Sizes are 5+4+4+5+6+6 = 30.

Notes:
- **Pierce:** it sits on the 5-tick Overflow only, so it is a reading problem and not a constant.
- **OUTPUT_DOWN source:** the Shim at slot 4 applies it, which is the status identity of the phase (anti-Firmware). It cuts your slice output by 25 % per stack, so a Perfect on that slice is worth less, and the Echo still pays.
- **Defense:** only one Defrag, now bigger and lower. P2 has fewer ways to hide and more ways to be punished, which is the flip from P1.

### Transition (P1 → P2)

- **Parks:** damage parks at 50 % (R3). A big burst that would cross is lost, which prevents skipping P2 in a single turn.
- **Statuses:** kept (R6). Your statuses remap by centre tick. `cleanse_on_enter = NONE`.
- **Wheel:** `wheel_override` to the P2 layout, pointers re-set to 0 / 11, `MIGRATE` telegraphed one turn ahead.
- **Phase line:** a short line in the REBEL_CELL voice. The new layout shows on entry.

## 3. Sustain and intake

**Sustain:** none. There is no heal, no hub heal and no shield. The only defense is BLOCK: 8 per Defrag in P1, 6 in P2, i.e. ≤ 8 per turn when read, and zero when its needle misses it. That is below the 30 % cap (30 % × 9 = 2.7 at T1... but BLOCK is defense on a hit, not sustain; it is counted as 0.6 × 8 ≈ 4–5 per turn of absorbed damage, and I count it as effective sustain). Worst case at T1, 5 of 9 reference dpt, over the cap. Choice: the P1 Defrag stays at 8 and I pay for it in the budget below (the sustain term of the formula). R13 BLOCK expires at your next turn so it is not a pool. I accept this.

**Budget sustain per turn used below:** 3 (≈ one Defrag read in 2 of 3 needle-turns, 8 × 0.4).

**Intake at the reference player (before BLOCK/SANDBOX):**

| Phase | Reads per turn | Expected damage/turn at T1 | Notes |
|---|---|---|---|
| P1 | 2 needles; each lands damage on ~4 of 6 slices | ≈ 5–8 | Slices avg ≈ 8; 2 needles × 4/6 × 8 ≈ 10.7 raw, minus Null and Defrag reads, ≈ 7 |
| P2 | 2 needles, one with pierce window | ≈ 8–11 + Echo 5 per Perfect landed | Echo is optional |

Intake is well above 0 in both phases. The tier damage factor (1.0 / 1.3 / 1.69 / 2.2) scales these at T2+.

## 4. HP by tier

R2: HP = reference_dpt × 3.5 turns × needles hit − sustain × 3.5. The budget counts the player's needle hits. This enemy has two needles, so the player's hits land twice per card on its wheel, and the budget doubles the "needles hit" factor for the player-side damage only when the player uses a pointer attack. Per R2's elite table (2 phases), I use the table band directly and check it against the arithmetic.

Arithmetic (T1, dpt 9, sustain 3 per turn counted as effective BLOCK):
- P1 = (9 − 3) × 3.5 = 21 per needle-hit. With 2 needles on its wheel the player's pointer attack (a SHIM) lands twice against it, so ≈ 2 × 21 = 42 × 0.75 (one needle often on defense) ≈ 32.
- P2 = (9 − 1.5) × 3.5 × ~1.7 ≈ 45 (less BLOCK, still two needles).
- Total ≈ 77, which is above the elite T1 band of 56–72. So I trim to the band's upper edge.

Chosen `hp_by_tier`:

| Tier | HP | Band (R2 elite) | Threshold floor (×0.5) |
|---|---|---|---|
| T1 | 70 | 56–72 | 35 |
| T2 | 86 | 68–88 | 43 |
| T3 | 108 | 88–112 | 54 |
| T4 | 140 | 112–144 | 70 |

Current 150 HP is above the T4 band, so 140 is a drop of ~7 % at T4 and much more against today's T3 271–287 (which includes tier factor).

Phase share: P1 and P2 are each ≈ 50 %, so each phase is ≈ 3.5 turns at the reference player (35 HP of P1 at T1 ÷ (9 − 3 + BLOCK variance) ≈ 3.5–4). This is at the top of the band for the reasons above. If the sim says fights run long, drop the P1 Defrag to 6.

## 5. Enrage

Default elite: start turn 8, every 5 turns, +25 % damage, additive. No authored override.

Why: the expected fight is 7 turns, so enrage lands just past the expected end. It punishes stalling on its Defrag and Null reads and not clean play.

## 6. Buffs and counter Exploits

Not applicable. This is an elite, and buffs and Exploits are for bosses only.

## 7. Counterplay

**P1:**
- **Good player:** treats the wheel as a map. Nudges to put the second needle (tick 12) onto Defrag or Null and leaves the tick-0 needle on a Shim. They spend the free nudge first, because resistance 1 absorbs one tick (a single nudge is lost, so a 2-tick nudge is the minimum). Burst the half with cards and Overflow to park at 50 %.
- **Weak player:** nudges one needle clear and puts the other on the 16 Overflow. They also feed Defrag turns by hitting while BLOCK is up.

**P2:**
- **Good player:** lands Good, not Perfect, on most turns. Uses SANDBOX on the pierce Overflow turn (SHIELD and BLOCK are ignored by pierce). Cleanses OUTPUT_DOWN before a big slice. Decides once, on purpose, to take the 5-damage Echo for a burst turn that finishes it before the turn-8 enrage.
- **Weak player:** chases Perfects out of habit and pays 5 per Perfect. They block against the pierce Overflow with BLOCK and lose it. They let OUTPUT_DOWN stack to ×2 and lose half their damage.

## 8. Systems needed

| # | Need | Fallback |
|---|---|---|
| N3 | Phases and threshold parking on an elite; `validate` allows one phase entry | none; this is the core of R1 |
| N2 | `hp_by_tier` | keep a single `hp` and a manual tier table in `campaign_config`; weaker |
| N11 | Pointers on any tick (0 / 12, 0 / 11) | use 0 / 10 and 0 / 15, which are legal today, and lose the "uneven" feel |
| N12 | Variable slice sizes and sub-tick maps (4, 6) | all 5-tick slices; the 6-tick no-Perfect read is lost, and P2 Shim's narrow window is lost. Still playable |
| N6 | Echo listener (ON_PERFECT) | drop the listener; put the 5-damage on a slice instead. P2 then loses its question |
| N9 / N8 | OUTPUT_DOWN status | use today's PARASITE status (a 2-stack OUTPUT_DOWN equivalent) |
| N20 | `hits` (Shim ×2) and `pierce` on a slice | one hit of 12; pierce via an existing Pierce segment is not available to enemies, so drop it |
| N4 | Enrage default | none; use the default |
| N1 | PERCENT mode | not used; all FLAT |

**Data-only fallback overall:** P1 is fully buildable today with N3 and `wheel_override` (N11/N12 optional). P2 without N6 loses its distinct question and becomes "a harder P1", so I do not recommend shipping P2 without N6.

## 9. Delta vs today

| | Today | New |
|---|---|---|
| HP | 150 flat × tier factor | 70 / 86 / 108 / 140 by `hp_by_tier` |
| Phases | none | 2, threshold 0.5, parking |
| Wheel | Overflow 24, Shim ×3, Defrag, Null; 5-tick; pointers 0 / 15 | two authored layouts with variable sizes; pointers 0 / 12 and 0 / 11 |
| Damage | Overflow 24 | Overflow 16 (P1), 14 pierce and 12 (P2) |
| Resistance | 1 | kept, 1 |
| Listener | none | Echo on Perfect (P2) |
| Status | none | OUTPUT_DOWN ×1 from a Shim in P2 |
| Enrage | none | default elite |
| `corporation_id` | empty | `rebel_cell` |
| `cycle_reward` | 40 | kept |

**Kept:** the two-needle shape, passive resistance 1, `is_elite`, `cycle_reward`, id and the Overflow / Shim / Defrag / Null vocabulary.

**`heat_effects` decision:** this .tres has none, so there is nothing to retire. I do not add any. Heat is already carried by the Elite Router (+1).

## 10. Predicted sim check

There is no baseline row for REBEL_CELL, so this is estimated from the wheels only.

- **Expected turns:** about 6.5–7.5 at the reference player (3.5 per phase, plus about 0.5 turn lost to parking when a burst overshoots). Today's 150 HP at T1 with two needles and Overflow 24 is likely a 10–14 turn fight on the Solace elite precedent (Recall Unit 20 turns at T3, Claims Adjuster in the same family).
- **Win %:** T1 about 95 %, T2 about 93 %, T3 about 90 %, T4 about 85 %. Fall-off comes from the tier damage factor against a 70 HP pool that hits on two needles, with Echo and pierce adding to it.
- **Why:** damage per turn is low early (5–8) and rises with the phase, and the fight ends before the turn-8 enrage on a clean line. The risk is T4, where pierce plus Echo plus a 2.2× damage factor can burst a mistake-prone player. Check it against the pass criteria (≥ 90 % at T3) and, if short, drop the P2 pierce Overflow to 11.

## 11. Open questions

Q: Should the layouts mirror the player's actual wheel (slice types and sizes copied from the operative running the netrun) instead of being authored? That would be a real "Mirror" but breaks per-tier HP and previews unless the HP budget is computed from the copy. Needs its own system.

Q: Is Echo (5 on every Perfect) too punishing for Breaker and Ghost, whose Perfect hooks are their identity? Should it only fire once per turn?

Q: P1 big Overflow has no Perfect (6-tick). Is a no-Perfect damage slice readable enough, or should the player-facing map flag it more clearly on the intent chip?

Q: Should the pierce window in P2 exist on an elite at T1, or only from T2 up?

Q: Does BLOCK on the enemy count against the 30 % sustain cap, or only heal and shield?
