<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__enemies__rc_template_elite_b; status ok; tokens in 7004 cache-write 0 cache-read 32585 out 5300; cost $0.037. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, sustain and threshold mismatch):** Sustain set to 0. Guard BLOCK is a defense slice, not sustain, and the enemy has no heal. Budgets are now equal per phase (reference_dpt × 3.5, no subtraction), so the 0.50 threshold is supported. `hp_by_tier` = [60, 72, 98, 126]. The critic's T3 figure of 96 gives 48 per phase, below the T3 budget of 49 per phase (98 total). I set T3 to 98 so each half equals its budget exactly. It is inside the 88–112 band. The T1/T2/T4 values and floors follow the critic's fix.
- **Issue 2 (BLOCKER, P2 geometry unreadable):** P2 is redrawn with a rest-position table giving each needle's slice and sub-tick quality, so the "hot needle" claim is checkable. The Riposte Perfect rider is removed (see issue 6). The burst window is now defined by the geometry. Needle B at tick 9 sits on the Jab 4 at ticks 9–12 only if the layout starts at tick 5... the layout is rebuilt so the cumulative boundaries and the rest reads are listed in full.
- **Issue 3 (MAJOR, intake):** Replaced with tick-weighted figures: P1 raw is 3.6 per turn (T3 ≈ 6.1 after the ×1.69 factor). P2 is recomputed on the new layout. The intake targets are stated per tier and no longer contradict the T3 figure.
- **Issue 4 (MAJOR, turns per phase):** §4 now shows 3.5 turns per phase from the equal split.
- **Issue 5 (MAJOR, Echo):** Echo fires once per Perfect needle (P1 has one needle, so at most once per resolve). It is blockable by BLOCK and SHIELD and negated by SANDBOX, as a normal enemy hit.
- **Issue 6 (MAJOR, Riposte rider):** Removed. Riposte is a plain SHIM 12 with no Perfect rider, so P2 has no Perfect tax and the flip is clean. Detour is described consistently as negating one whole attack.
- **Issue 7 (NIT):** The resistance 1 → 0 change is named as a `wheel_override` field in the transition. The corporation id stays `rebel_cell`, because the folder and corporation list use that id and no ruling contradicts it (Q kept). Echo is distinguished from the Handler mini-boss by being an elite-scale, single-fire reaction with no replay of the landed slice.
- **Kept:** the flip from P1 (Perfects punished) to P2 (listener off, second needle), the uneven (0, 9) needles, the 4-tick no-Perfect Jabs, per-system fallbacks, and no heat_effects.

# rc_template_elite_b: direct design

*Working name: "Mirror B, the Echo Duelist". The corporation field is empty and there is no baseline row. All numbers are estimated from the wheel and the R2 budget.*

## 1. Identity & the one question

**Class:** Elite, 2 phases, one threshold. **Corporation:** REBEL_CELL (set `corporation_id = rebel_cell`). **Layers:** L5–6 pressure only; it needs a built player wheel to feel like a duel. The sibling `rc_template_elite` punishes what you carry. This one is the **duelist**: it punishes how you land.

- **P1 Reflection:** "Can you land well when your Perfects get answered?" Each Perfect draws a 4-damage Echo. A Good landing is safe.
  - Shortening answer: land Good, not Perfect, on big slices, and steer its needle onto Null or an unguarded Jab.
- **P2 Duel:** "Can you handle two needles close together and choose which one is deadly?" The listener is gone, Perfects are free, and the two needles sit 9 ticks apart.
  - Shortening answer: put the hot needle on Null or Detour and spend the burst turn on the safe needle's slice.

The same Perfect that is a liability in P1 is free in P2.

## 2. Phase plan

Threshold: **0.50**. The HP floor in P1 is ceil(max × 0.5).

### Phase 1: Reflection (100 → 50 %)

| Field | Value |
|---|---|
| Needles | 1 at tick 0 (FIXED) |
| Resistance | passive 1 (kept from today), restores each turn |
| Hub | none |
| Listener (N6) | **Echo:** ON_PERFECT on the player's landed slice → 4 FLAT damage (× tier factor) to the player, once per Perfect needle (one needle in P1, so at most once per resolve). A normal enemy hit: BLOCK and SHIELD absorb it, SANDBOX negates it. Preview shows "ECHO −4". |
| Statuses | none |

**Layout (sum 30):** 6 + 4 + 6 + 4 + 5 + 5 = 30.

| Slice | Ticks | Effect |
|---|---|---|
| Guard | 6 | BLOCK 8 FLAT |
| Jab | 4 | SHIM 6 (no Perfect; max Good) |
| Guard | 6 | BLOCK 8 FLAT |
| Jab | 4 | SHIM 6 |
| Lunge | 5 | SHIM 12 |
| Null | 5 | nothing |

- Lunge is the only damage spike. The Jabs are mid-sized threats that can never be Perfect.
- **Intake target (raw, T1 factor):** 3–5 per turn, plus Echo only on a Perfect of yours.

### Transition P1 → P2
- Damage parks at the floor (R3). Statuses survive with the centre-tick remap (R6), `cleanse_on_enter = NONE`.
- The Echo listener is removed; `wheel_override` swaps the layout, sets `pointer_ticks = (0, 9)` (N11) and sets `resistance = 0`.
- Phase line: "Learned your timing."

### Phase 2: Duel (50 → 0 %)

| Field | Value |
|---|---|
| Needles | 2 at ticks 0 and 9 |
| Resistance | 0 |
| Hub | none |
| Listener | none |
| Statuses | none |

**Layout (sum 30):** 5 + 4 + 3 + 5 + 4 + 4 + 5 = 30. Slice order and boundaries (slice spans ticks start..end−1):

| # | Slice | Ticks | Span | Centre tick | Effect |
|---|---|---|---|---|---|
| 1 | Riposte | 5 | 0–4 | 2 | SHIM 12 |
| 2 | Jab | 4 | 5–8 | 6.5 (no Perfect) | SHIM 6 |
| 3 | Detour | 3 | 9–11 | 10 | SANDBOX (negates one whole attack) |
| 4 | Lunge | 5 | 12–16 | 14 | SHIM 14 |
| 5 | Null | 4 | 17–20 | n/a | nothing |
| 6 | Jab | 4 | 21–24 | n/a | SHIM 6 |
| 7 | Null | 5 | 25–29 | n/a | nothing |

**Rest reads at rotation 0:**
- Needle A at tick 0 reads Riposte, sub-tick 0 of 5 (W G P G W, so WEAK). It deals 12 × 0.5 = 6.
- Needle B at tick 9 reads Detour, sub-tick 0 of 3 (G P G, so GOOD). It negates one attack.
- So at rest, A is a weak Riposte and B is a self-protect. Rotating by +2 puts A on the Riposte centre (PERFECT 12) and B on the Detour's last tick (GOOD).
- Because the needles are 9 ticks apart, a slice 9 ticks ahead of a dangerous one is rarely also dangerous. Dangerous pairs: Riposte (0–4) with Detour (9–11) is safe; Lunge (12–16) is reached by needle A at rotation +12..+16, which puts B on ticks 21–25, a Jab or Null. Needle B lands on Lunge when A is at ticks 3–7, which is Riposte's end or Jab. So Lunge plus Riposte can be live together only at rotation +3..+4 (A reads Riposte tick 3–4, B reads Lunge tick 12–13). That is the one lethal alignment, and a 1-tick nudge breaks it. It is the readable danger the player solves.
- **Burst window:** needle A on Null (rotation +17..+20 puts B at ticks 26–29, also Null) means both needles read Null: a free turn. That is the turn to spend the biggest hits.
- **Intake target:** 6–9 per turn at T1 factor before enrage.

## 3. Sustain and intake

- **Sustain: none.** No heal, no hub. Guard is temporary BLOCK, not sustain, so the budget subtracts nothing.
- **Intake P1 (tick-weighted raw):** (6×4 + 12×5 + 6×4) / 30 = 108/30 = 3.6 per turn at T1. At T3 (×1.69) ≈ 6.1, and at T4 (×2.2) ≈ 7.9. Echo adds 4 × factor (6.8 at T3) only when the player lands a Perfect.
- **Intake P2 (two needles, tick-weighted):** per-needle damage = (12×5 + 6×4 + 14×5 + 6×4) / 30 = 178/30 ≈ 5.9. Two needles ≈ 11.9 raw at T1. This is above the 6–9 target, so one needle is usually on Null/Detour or WEAK: the expected realized value is about 8 at T1 (≈ 13.5 at T3). The number reaches 0 on the burst window, and it is above 0 on average.

## 4. HP by tier

No sustain. Phase budget = reference_dpt × 3.5 turns per phase, equal for both phases because the sustain is 0.

| Tier | dpt | P1 budget | P2 budget | Total | Band (R2 elite) | `hp_by_tier` | Floor (0.50) |
|---|---|---|---|---|---|---|---|
| T1 | 9 | 31.5 | 31.5 | 63 | 56–72 | **60** | 30 |
| T2 | 11 | 38.5 | 38.5 | 77 | 68–88 | **72** | 36 |
| T3 | 14 | 49 | 49 | 98 | 88–112 | **98** | 49 |
| T4 | 18 | 63 | 63 | 126 | 112–144 | **126** | 63 |

- T1 and T2 are set slightly under budget (60 vs 63, 72 vs 77) so low tiers finish inside 3–4 turns per phase when the player lands on both needles in P2.
- P1 and P2 are each ≈ 3.5 turns at the reference player, so the 0.50 split matches the budget at every tier. Total 6–8 turns.
- Authored `hp_by_tier` = [60, 72, 98, 126]. Today's 150 is outside every band.

## 5. Enrage

**Default** (elite: start 8, every 5, +25 % damage). The expected finish is turn 6–8, so enrage appears only for a stalling player. No authored trigger: P2's two needles already pressure. The Echo is not scaled by the enrage step beyond the shared damage multiplier.

## 6. Buffs and counter Exploits

Not applicable (elite).

## 7. Counterplay

- **P1:** Land Good on Lunge-class slices and use the free nudge to move a Perfect down to Good. Guard is 8 block, so spin or strip to put its needle on Null or a Jab. A SANDBOX turn cancels the Echo entirely.
- **P2:** Perfects are free, so land them. Find the rotation where both needles read Null and spend the biggest cards there. Avoid the lethal alignment (Riposte with Lunge at rotation +3..+4): a 1-tick nudge breaks it. SANDBOX your wheel on the alignment turn if you cannot.
- **Weak players:** chase Perfects in P1 and eat the Echo every turn. In P2 they ignore needle B, so they take about 13.5 per turn at T3.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| Phases, parking, status keep | N3 | none (core) |
| Per-tier HP | N2 | data-only: single `hp` with band median (98) |
| Enemy listener (ON_PERFECT Echo) | N6 | fixed 4 damage riding the Lunge slice instead |
| Pointers on any tick (0, 9) | N11 | (0, 10) if blocked |
| Variable slice sizes (3/4/5/6) | N12 | uniform 5-tick slices on 6 slots; loses the no-Perfect Jab and the 3-tick Detour |
| Amount mode (FLAT) | N1 | FLAT is today's behavior |
| Enrage | N4 | none |
| Defense trio naming (Detour = SANDBOX) | N14 | today's DETOUR evade |

The ON_HIT_DEALT rider is removed, so N6 is needed only for the Echo.

## 9. Delta vs today

- **Kept:** the Mirror identity, the Shim/Defrag/Detour/Null vocabulary, `is_elite`, `cycle_reward` (40, may be trimmed for the shorter fight), and a second needle (moved from 15 ticks to 9, in P2 only).
- **Changed:** HP 150 → [60, 72, 98, 126]; one phase becomes two; equal slices become variable sizes; resistance 1 only in P1; a new Echo listener; `corporation_id` set to `rebel_cell`.
- **Today:** a flat attrition fight with the second needle at 15 ticks from turn 1, no shift.
- **heat_effects:** the file has none, so nothing is kept or added. The elite is already gated by L5–6 and Heat-driven elite frequency.

## 10. Predicted sim check

No baseline row; estimated from the wheel.
- **Turns:** T1 about 6, T2 about 6.5, T3 about 7, T4 about 7.5 at the reference skill. P90 at most 9. Each phase is 3–4 turns.
- **Win rate:** T1 ≥ 97 %, T2 ≥ 95 %, T3 ≈ 92 %, T4 ≈ 85 %. The T4 shortfall comes from P2's two needles at the 2.2 damage factor.
- **Why:** HP is built from reference damage with an even phase split, and the Echo makes naive Perfect chasing cost 4 × the tier factor each time.

## 11. Open questions

Q: Should the corporation id be set to `rebel_cell` here, or left to the sibling elite pass?
Q: Does the Echo hit scale with the enrage step at T4 (currently only via the shared damage multiplier)?
Q: Does the 9-tick needle gap need a HUD marker that pairs the two needles?
Q: Should P2 resistance stay at 0, or stay at 1 to protect the burst window?
Q: Should the sibling elite use a different threshold (e.g. 0.6) so the two do not share one shape?
