<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__rc_template_elite; status ok; tokens in 9198 cache-write 0 cache-read 32585 out 11308; cost $0.069. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, HP unrederived):** §4 now derives every tier from the R2 budget with sustain = 0. P1 factor is 1.0 and P2 factor is 1.3, so the budget is T1 31.5 + 41 = 72.5, T2 88.5, T3 112.7, T4 144.9. Chosen HP is 70 / 86 / 110 / 144. v1's invented "needles ×2 on the player side" doubling is gone, replaced by a one-line justification of the 1.0 and 1.3 factors. T3 moves from the critic's 108 to 110 because the budget gives 112.7 and the band tops at 112.
- **Issue 2 (BLOCKER, threshold):** the critic's "about 0.42" is P1's share of the HP, not the floor. P1 is 43 % of the budget, so the floor is 57 % of max HP: threshold **0.57** (not 0.45 or 0.5). I rechecked the critic's own example: floor 32 would make P1 take 38 and P2 only 32, which inverts the budget. Floors are 40 / 50 / 63 / 83. P1 is about 3.4 turns and P2 about 3.5, which now follows from the numbers.
- **Issue 3 (BLOCKER, sustain):** replaced with "sustain none; BLOCK is defense, not sustain; R2 sustain term = 0". No cap breach is accepted, and the "3 vs 4–5" mismatch is gone. The "may I accept this" paragraph is deleted.
- **Issue 4 (MAJOR, pointers):** P1 needles are now 0 / 13 and tick boundaries are listed for both layouts. The worst pair and the safe pairs are computed from them. The false "never both dangerous" claim is removed.
- **Issue 4, also:** v1 said the 6-tick Overflow was "easy to land on". Enemy WEAK reads output 0.5×, and a 6-tick slice reads full on only 2 of 6 sub-ticks, so it is now described as a nudge-it-to-half slice. Intake is recomputed with tier weighting.
- **Issue 5 (MAJOR):** Echo is a staged ON_PERFECT listener (N6) with an "ECHO −5" preview that undoes with the action. The 4-tick Shim names its `tick_quality` as W G G W (the R11 default), so no override is needed.
- **Issue 6 (MAJOR):** OUTPUT_DOWN is ×1 per Shim hit, capped at ×2, and removed by the existing Cleanse.
- **Issue 7 (MAJOR):** the N20 fallback is now "Overflow 14 single hit, no pierce; Shim one 12 hit". The invented Pierce-segment claim is removed.
- **Issue 8 (NIT):** the 150 HP is marked "per the file as read in v1, unverified", and the Recall Unit precedent is dropped. There is no REBEL_CELL baseline row.
- **Issue 9 (NIT):** the naming paragraph is cut to one line.
- **Kept, because the critic marked it strong:** the uneven needles, the P1 → P2 question flip, the heat_effects decision and the tagged dependencies. Damage numbers are lowered slightly (Overflow 14 / 9 in P1) after the tier-weighted intake recompute.
- **Critic Q on Echo:** decided. Echo fires at most once per turn.
- **Ruling check:** nothing conflicts with the designer rulings. R3 floors and R6 status keep are used as written.

# rc_template_elite: direct design

Working name: **Mirror A, "Your Echo"**. Its sibling `rc_template_elite_b` is a separate pass. Display names are a later pass.

## 1. Identity & the one question

**Class:** Elite, 2 phases, one threshold at **0.57**. **Corporation:** REBEL_CELL (set `corporation_id = rebel_cell`; the file has it empty). **Layers:** L3–L6 on REBEL_CELL Grids. It is a pressure elite and not a teaching elite, because it needs the player's own wheel to read it against.

| Phase | The question | The answer that shortens the fight |
|---|---|---|
| P1 Reflection | "Two needles, one pair of slices each turn. Which pairing do you accept?" | Nudge so the pair is safe (Null plus Defrag or Shim). Land your big slice, then burst P1 down to the floor. |
| P2 Feedback | "Every Perfect you land is paid back." | Land Good where a Perfect isn't needed, or take the Echo on purpose for one finishing burst. |

**Mirror flavor:** the layouts are authored to imitate a generic operative (Overflow, Shim, Defrag, Null). Only P2's listener is mechanically "your echo". Copying the player's real wheel is a separate system (Q1).

## 2. Phase plan

### P1: Reflection (100 → 57 %)

| Field | Value |
|---|---|
| Needles | 2, uneven: ticks 0 / 13 (R10, N11) |
| Resistance | 1, passive (as today), restores each turn |
| Hub / statuses / listeners | none |

Layout (sum 30), starting at tick 0, with sub-tick quality by R11:

| # | Slice | Ticks | Boundaries | Sub-ticks | Effect |
|---|---|---|---|---|---|
| 1 | Overflow (big) | 6 | 0–5 | W W G G W W | 14 FLAT |
| 2 | Shim | 5 | 6–10 | W G P G W | 6 FLAT |
| 3 | Defrag (BLOCK) | 4 | 11–14 | W G G W | 8 FLAT |
| 4 | Shim | 5 | 15–19 | W G P G W | 6 FLAT |
| 5 | Overflow (small) | 5 | 20–24 | W G P G W | 9 FLAT |
| 6 | Null | 5 | 25–29 | — | none |

Sizes: 6+5+4+5+5+5 = 30 ✓.

- **Enemy tiers:** WEAK reads 0.5×, and Good and Perfect read 1.0×. The big Overflow therefore hits full on only 2 of its 6 sub-ticks, so a 1–2 tick nudge halves it.
- **Needle pairing:** needle A reads tick r and needle B reads r+13.
  - **Worst pair:** A on the small Overflow (20–22) puts B on the big Overflow (3–5): 14 + 9 = 23 raw at full tier.
  - **Safe pairs:** A on Null (25–29) puts B on 8–12, which is Shim or Defrag. A on the big Overflow (0–5) puts B on 13–18, which is Defrag or Shim, never an Overflow.
  - The read is therefore which pair, not "avoid both".

### P2: Feedback (57 → 0 %)

| Field | Value |
|---|---|
| Needles | 2, uneven: ticks 0 / 11 |
| Resistance | 1 (kept) |
| Hub | none |
| Status | OUTPUT_DOWN ×1 per Shim-4 hit, cap ×2 (R8; Cleanse removes it) |
| Listener (N6) | **Echo:** on a player PERFECT landing, deal 5 × tier damage factor to the player. **At most once per turn.** One hit; SANDBOX negates. It is a staged ON_PERFECT listener: the preview shows "ECHO −5" on the Perfect landing and undoes with the action. |

| # | Slice | Ticks | Boundaries | Sub-ticks | Effect |
|---|---|---|---|---|---|
| 1 | Overflow | 5 | 0–4 | W G P G W | 14 FLAT, **pierce** (N20) |
| 2 | Shim | 4 | 5–8 | W G G W (`tick_quality` default) | 6 FLAT ×2 hits (N20) |
| 3 | Null | 4 | 9–12 | — | none |
| 4 | Shim | 5 | 13–17 | W G P G W | 6 FLAT, plus OUTPUT_DOWN on your slice under the pointer |
| 5 | Defrag (BLOCK) | 6 | 18–23 | W W G G W W | 6 FLAT |
| 6 | Overflow | 6 | 24–29 | W W G G W W | 12 FLAT |

Sizes: 5+4+4+5+6+6 = 30 ✓.

- **Flip from P1:** one small Defrag, less Null, and a pierce Overflow, so P2 has fewer places to hide.

### Transition (P1 → P2)

- **Parks:** the floor is ceil(max HP × 0.57). Excess damage is lost (R3), so P2 cannot be skipped in one turn. The phase changes at the end of that resolve.
- **Statuses:** kept with the centre-tick remap (R6). `cleanse_on_enter = NONE`.
- **Wheel:** `wheel_override` to the P2 layout with needles at 0 / 11. It takes effect at the next turn's respin, with intents visible. A phase line is played.

## 3. Sustain and intake

**Sustain: none.** There is no heal, no hub heal and no shield. BLOCK is defense, not sustain: 8 FLAT on one 4-tick slice (P1), 6 on one 6-tick slice (P2). The R2 sustain term is 0, and the 30 % cap is not approached. BLOCK's effect on the player's damage is already inside the phase factors in §4.

**Intake at the reference player, T1** (tier-weighted: 5-tick = 0.8, 6-tick = 0.667, 4-tick = 0.75):

| Phase | Per needle | Two needles raw | Steered by the reference player |
|---|---|---|---|
| P1 | (6×14×.667 + 2×5×6×.8 + 5×9×.8)/30 = 140/30 = 4.7 | 9.3 | 4–6 |
| P2 | (5×14×.8 + 4×12×.75 + 5×6×.8 + 6×12×.667)/30 = 164/30 = 5.5 | 10.9 | 6–8, plus Echo 5 per turn with a Perfect |

Intake is above 0 in both phases. Multiply by 1.0 / 1.3 / 1.69 / 2.2 for T1–T4.

## 4. HP by tier

R2 phase budget = `reference_dpt` × 3.5 × the phase's hit factor − sustain (0).

- **Factor 1.0 in P1:** two needles double the player's pointer hits, but Defrag and Null reads on the enemy wheel absorb about half of them.
- **Factor 1.3 in P2:** only one Defrag (6 ticks), so more of the double hit lands.

| Tier | dpt | P1 = dpt×3.5×1.0 | P2 = dpt×3.5×1.3 | Sum | Band (elite) | **HP** | Floor (×0.57) | P1 takes / P2 takes |
|---|---|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 41.0 | 72.5 | 56–72 | **70** | 40 | 30 / 40 |
| T2 | 11 | 38.5 | 50.1 | 88.6 | 68–88 | **86** | 50 | 36 / 50 |
| T3 | 14 | 49.0 | 63.7 | 112.7 | 88–112 | **110** | 63 | 47 / 63 |
| T4 | 18 | 63.0 | 81.9 | 144.9 | 112–144 | **144** | 83 | 61 / 83 |

- **Check:** P1 is 43 % of the budget, so the floor is 57 %. Sums are trimmed to the band top.
- **Turns at the reference player, T1:** P1 30 ÷ 9 ≈ 3.3, and P2 40 ÷ 11.7 ≈ 3.4. The total is about 6.7.
- **Today's HP:** the v1 reading of the file was 150 (unverified), so T4 drops.

## 5. Enrage

**Elite default:** start turn 8, every 5 turns, +25 % damage, additive. No override.

- **Why:** the expected fight is about 7 turns, so enrage lands just past the clean finish.
- **What it punishes:** stalling on Defrag and Null reads and refusing to burst.

## 6. Buffs and counter Exploits

Not applicable: this is an elite.

## 7. Counterplay

**P1**
- **Good player:** reads the pair before spending the free nudge. They nudge to Null + Shim or big Overflow + Defrag, and nudge the big Overflow off its 2 full sub-ticks (one tick halves it). They burst the half with cards and park at the floor.
- **Weak player:** leaves small Overflow + big Overflow (23 raw) up. They also burst into BLOCK turns.

**P2**
- **Good player:** lands Good on most turns and SANDBOXes the pierce Overflow (BLOCK and SHIELD do nothing against it). They Cleanse OUTPUT_DOWN before a big slice. Once, on purpose, they take the Echo for a finishing burst before the turn-8 enrage.
- **Weak player:** chases Perfects out of habit and pays Echo every turn. They BLOCK the pierce Overflow and lose it. They let OUTPUT_DOWN reach ×2.

## 8. Systems needed

| # | Need | Fallback |
|---|---|---|
| N3 | Elite phase, parking, `validate` allows one phase | none (core of R1) |
| N2 | `hp_by_tier` | a single `hp` plus a manual tier table (weaker) |
| N11 | Needles 0 / 13 and 0 / 11 | 0 / 10 or 0 / 15, legal today; the uneven feel is lost |
| N12 | Sizes 4 and 6, sub-tick maps | all 5-tick slices; the 6-tick half-damage read is lost |
| N6 | Echo listener | none worth shipping: P2 becomes "a harder P1" |
| N8 / N9 | OUTPUT_DOWN ×N | today's PARASITE status (equivalent to a 2-stack OUTPUT_DOWN) |
| N20 | `hits`, `pierce` | Overflow 14 FLAT single hit, no pierce; Shim one 12 hit |
| N4 | Default enrage | none |
| N1 | PERCENT mode | not used |

**Data-only reading:** P1 is buildable with N3 and `wheel_override`. P2 needs N6 to ask its own question.

## 9. Delta vs today

| | Today | New |
|---|---|---|
| HP | 150 (per v1, unverified) × tier factor | 70 / 86 / 110 / 144 (`hp_by_tier`) |
| Phases | none | 2, threshold 0.57, parking |
| Wheel | Overflow 24, Shim ×3, Defrag, Null; 5-tick; pointers 0 / 15 | two authored layouts, sizes 4–6; pointers 0 / 13 and 0 / 11 |
| Damage | Overflow 24 | Overflow 14 / 9 (P1); 14 pierce / 12 (P2) |
| Listener, status | none | Echo (P2), OUTPUT_DOWN from a Shim |
| Enrage | none | elite default |
| `corporation_id` | empty | `rebel_cell` |

- **Kept:** two needles, resistance 1, `is_elite`, `cycle_reward` 40, the id and the Overflow / Shim / Defrag / Null vocabulary.
- **`heat_effects`:** none exist in the file and none are added. The Elite Router already adds +1 Heat.

## 10. Predicted sim check

There is no REBEL_CELL baseline row, so this is estimated from the wheels only.

- **Turns:** about 6.7 at the reference player, plus about 0.5 lost to parking overshoot, so 7–7.5. Win rate falls with the tier factor on 2 needles, Echo and pierce.
- **Win %:** T1 about 95 %, T2 about 93 %, T3 about 90 %, T4 about 85 %.
- **Risk:** T4 (2.2× damage with pierce and Echo). If T3 comes in under 90 %, drop the P2 pierce Overflow to 11.

## 11. Open questions

Q: Should the layouts copy the player's actual wheel (slice types and sizes)? That is a true "Mirror", but it needs its own system and an HP budget computed from the copy.
Q: Echo is capped at once per turn; is 5 × factor right for Breaker and Ghost, whose Perfect hooks resolve twice?
Q: Should the pierce Overflow in P2 be T2+ only? As drafted it exists at every tier, since this is a pressure elite at L3+.
Q: Do the 6-tick slices (WEAK on 4 of 6 sub-ticks) read clearly enough on the intent chip, or do they need a "half on edge" hint?
Q: Should enemy BLOCK count against the 30 % sustain cap, or only heal and shield? This draft treats it as defense.
