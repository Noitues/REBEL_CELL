<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__triage_unit; status ok; tokens in 6546 cache-write 0 cache-read 32585 out 7497; cost $0.047. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, two sustain sources):** the Triage Protocol Hub heal is deleted. The Hub now has no passive. The two Hotfix slices are the single sustain source, and the cap check in section 3 uses only them. The `hub_condition` item is removed from section 8.
- **Issue 2 (BLOCKER, HP above budget, T4 over target):** HP is re-derived from the R2 formula and the arithmetic is shown.
  - `hp_by_tier` is now [28, 34, 44, 56], the band floors from R2. These sit within 1 HP of the recomputed budget (28.0 / 33.95 / 43.1 / 55.3).
  - v1's [30, 36, 46, 58] exceeded the budget and the "Block absorbs 15 %" rationale pushed the wrong way. That rationale is dropped.
  - Enemy BLOCK is lowered from 6 to 4, so the Block slices stop adding hidden effective HP.
  - Predicted turns are recomputed, and T4 is no longer above 4.
- **Issue 3 (MAJOR, WEAK halving ignored):** the average heal now applies the sub-tick map. A 4-tick Hotfix reads W G G W, so its mean multiplier is 0.75. Heal per turn = 0.267 × 0.75 × Hotfix, which is 0.2 × Hotfix. Shim intake gets the same treatment (6-tick W W G G W W, mean 0.667).
- **Issue 4 (MAJOR, "only Null has Perfect"):** corrected. The 5-tick Block (slice 1) and the 5-tick Null have a Perfect centre. The Block Perfect is harmless because Perfect output equals Good output (1.0×).
- **Issue 5 (MAJOR, systems tag and fallback):** with the Hub heal gone, no listener or `hub_condition` is needed, so the data-only fallback problem disappears. The N12 fallback is rewritten to match the final table.
- **Issue 6 (NIT):** "better player" wording kept (Block's W edges are real). Q's are reduced to design questions, and the tuning Q's are dropped.
- **Kept, because the critic marked them strong:** the two 4-tick Hotfix slices that never read Perfect, the one-needle layout with sizes summing to 30, and an intake above 0.
- **Not changed:** Block slice 1 stays 5 ticks, since its Perfect is harmless and tick sums stay clean (it is a Q).

# triage_unit: direct design

## 1. Identity & the one question
- **Class:** NORMAL, 1 phase, no enrage. Solace, appears at L1-2 (teaching) and L5-6 (pressure, at T3-T4).
- **Concept:** a triage nurse whose only repair is its two Hotfix slices. It does not out-heal you. It punishes a needle you leave on a Hotfix.
- **The one question:** "Which slice is under its needle, and can I make it Null or Shim instead of Hotfix?" This replaces today's attrition question of out-racing a 6 heal and two 8 blocks.
- **Answer that shortens the fight:** one 1-tick nudge turns a landing on a Hotfix edge into the neighbouring slice. Burst on turns when the needle sits on Null or Shim.
- **Teaching value:** the first Solace enemy where steering the enemy wheel clearly pays.

## 2. Phase plan (single phase, no threshold)

| Field | Value |
|---|---|
| Phase | 1 of 1, no floor, no transition |
| Needles | 1, tick 0, FIXED |
| Hub | none |
| Statuses / parasites | none |
| Listeners | none |

**Wheel (sizes sum to 30):**

| # | Slice | Size | Effect | Mode |
|---|---|---|---|---|
| 1 | Triage Block | 5 | DEFRAG (BLOCK) 4 | FLAT × tier damage factor |
| 2 | Hotfix | 4 | HOTFIX 5 HP | FLAT × tier damage factor |
| 3 | Shim | 6 | SHIM 6 damage | FLAT × tier damage factor |
| 4 | Null | 5 | nothing | n/a |
| 5 | Hotfix | 4 | HOTFIX 5 HP | FLAT × tier damage factor |
| 6 | Triage Block | 6 | DEFRAG (BLOCK) 4 | FLAT × tier damage factor |

- Tick sum: 5 + 4 + 6 + 5 + 4 + 6 = 30.
- **Sub-tick maps (R11):**
  - Hotfix (4 ticks): W G G W, never Perfect, mean output 0.75×.
  - Shim and Block 6 (6 ticks): W W G G W W, never Perfect.
  - Block 5 (slice 1) and Null (5 ticks): W G P G W. The Block Perfect is harmless because Perfect output is 1.0×, the same as Good.
- Eight of 30 ticks are Hotfix, and half of those ticks read WEAK.
- **Lowered from today:** Hotfix 6 to 5, and Defrag 8 to 4. The unit stops being a wall.

## 3. Sustain and intake

**Sustain (one source: the Hotfix slices).** The Hub has no heal.
- Expected heal per turn = P(Hotfix tick) × mean tier multiplier × Hotfix amount = (8/30) × 0.75 × 5 × factor = 0.2 × Hotfix.
- The reference damage per turn comes from R2: [9, 11, 14, 18].

| Tier | Factor | Hotfix (5 × factor) | Expected heal/turn | 30 % cap of ref dpt |
|---|---|---|---|---|
| T1 | 1.0 | 5.0 | 1.0 | 2.7 |
| T2 | 1.3 | 6.5 | 1.3 | 3.3 |
| T3 | 1.69 | 8.45 | 1.7 | 4.2 |
| T4 | 2.2 | 11 | 2.2 | 5.4 |

- Expected sustain is about 11 to 12 % of reference damage, well under the cap.
- The worst single landing (Hotfix at Good) heals the full Hotfix amount, about 5 to 11. That is one turn in which the player left the needle on it.
- The BLOCK slices are defense, not sustain.

**Intake per turn** at the reference player, assuming the player does not block:
- Intake = (6/30) × 0.667 × 6 × factor = 0.8 × factor.

| Tier | Shim (6 × factor) | Intake/turn |
|---|---|---|
| T1 | 6.0 | 0.8 |
| T2 | 7.8 | 1.0 |
| T3 | 10.1 | 1.35 |
| T4 | 13.2 | 1.8 |

All values are above 0, against 0.39 to 0.77 today. This is threat, not lethality: a 4-turn fight costs about 3 to 7 HP.

## 4. HP by tier
R2 normal band: T1 28-36, T2 34-44, T3 44-56, T4 56-70.

Budget = ref dpt × 3.5 turns × 1 needle − expected heal × 3.5.

| Tier | dpt × 3.5 | − heal × 3.5 | Budget | `hp_by_tier` |
|---|---|---|---|---|
| T1 | 31.5 | 3.5 | 28.0 | **28** |
| T2 | 38.5 | 4.55 | 33.95 | **34** |
| T3 | 49.0 | 5.9 | 43.1 | **44** |
| T4 | 63.0 | 7.7 | 55.3 | **56** |

- Values are the band floors, within 1 HP of the budget.
- Block is not in the R2 formula. At 4 flat it absorbs about 1.07 × factor per turn if the player never steers off it. The free nudge is what offsets it (section 10).

## 5. Enrage
None (normal, R4). The fight is 3-4 turns, so there is nothing to stall.

## 6. Buffs and Exploits
Not applicable (not a boss).

## 7. Counterplay
- **Good player:** reads the preview and spends the free nudge to move the needle off a Hotfix or Block edge onto Null or Shim. Bursts on a Null or Shim turn, and keeps RAM for one spin if both Hotfixes sit near the pointer.
- **Better player:** parks the needle on a W edge of a Hotfix or Block, which gives half output, and saves RAM for a Perfect turn.
- **Weak player:** ignores the unit's wheel and plays into whatever it lands on. A Hotfix Good heals 5 to 11, and the fight runs to 5+ turns with Shim chip.

## 8. Systems needed
- **N1** (flat × tier damage factor on heal, block and damage). Fallback: bake the factor into per-tier authored values.
- **N2** (`hp_by_tier`). Fallback: keep `hp` at 28 and use the existing multiplier. The T4 value then diverges from the band.
- **N12** (4- and 6-tick slices). Fallback: six 5-tick slices.
  - Hotfix reads W G P G W (mean 0.8×), so use Hotfix 4 to keep expected heal near 0.2 × Hotfix.
  - The steering question stays, but "Hotfix never Perfect" is lost.
- No N4, N6 or new field is needed.

## 9. Delta vs today
- **Kept:** id, corporation, the six-slice family with Null, one needle at tick 0, `cycle_reward` 15.
- **Changed:** Defrag 8 to 4, Hotfix 6 to 5, slice sizes 5/4/6/5/4/6, and `hp_by_tier` = [28, 34, 44, 56] replaces `hp` 45 with its tier multiplier.
- **Retired:** the heal-exceeds-damage stalemate (3.9 heal turns at T4).
- **`heat_effects`:** none are authored on this normal, so none are kept.

## 10. Predicted sim check
Baseline (T1 to T4): 2.9 / 4.2 / 7.4 / 12.8 turns, 100 % win, taken/turn 0.39 to 0.77.

Net damage per turn, if the player never steers: dpt − heal − block (1.07 × factor). Turns = HP / net.

| Tier | Net/turn (no steering) | Turns (no steering) | Turns (nudge steers off half the Hotfix/Block) | Win % |
|---|---|---|---|---|
| T1 | 9 − 1.0 − 1.07 = 6.9 | 4.0 | 3.5 | 100 |
| T2 | 11 − 1.3 − 1.4 = 8.3 | 4.1 | 3.6 | 100 |
| T3 | 14 − 1.7 − 1.8 = 10.5 | 4.2 | 3.7 | 98 |
| T4 | 18 − 2.2 − 2.35 = 13.5 | 4.2 | 3.8 | 96 |

- Expected means are about 3.5 to 3.8 turns, with p90 about 5.
- The large change is T3/T4 turns falling from 7.4/12.8 to about 4, because the heal is a small, steerable slice instead of a 6-per-turn constant.
- If the sim shows T3/T4 means above 4.0, the first lever is Block 4 to 3.

## 11. Open questions
- Q: Should Block slice 1 stay 5 ticks, or become 4 to remove its stray Perfect?
- Q: With no Hub heal, do two Hotfix slices (about 11 % of reference damage) still carry the "treats the worst-hurt" identity?
- Q: Should the Hotfix slice preview show its tier-scaled heal in the intent chip, since a WEAK landing halves it?
- Q: Which tier row should the sim lock first: T3, where the baseline fight is longest?
