<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_016rDc21753X1Q3WpA7ajrQD, custom_id enemy__rc_template_elite_b; status ok; tokens in 3800 cache-write 0 cache-read 32007 out 3821; cost $0.026. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# rc_template_elite_b: direct design

*Working name: "Mirror B, the Echo Duelist". The corporation field is empty and there is no baseline row. Every number below is estimated from the wheel and from the R2 budget.*

## 1. Identity & the one question

**Class:** Elite, 2 phases, one threshold. **Corporation:** REBEL_CELL (the data has `corporation_id = &""`; set it to `rebel_cell`). **Layers:** L5–6 pressure only. It shows up when the player has a built wheel for it to copy. The other REBEL_CELL elite (`rc_template_elite`) is the only sibling, so this one needs a distinct hook. It is the **duelist**: it punishes how *you* land, where the sibling will punish what you carry.

**The question per phase:**
- **P1 Reflection:** "Can you land well when your Perfects get answered?" It is a counter-puncher. Its Echo listener fires on each of your Perfects, and a Good landing is safe.
  - Shortening answer: land Good, not Perfect, on your big slices. Burn its Guard slices with Strip or Spin so its needles sit on Null.
- **P2 Duel:** "Can you survive two needles that are close together, so you choose which one is deadly?" The listener is gone. Needles sit 9 ticks apart (uneven), and a 5-tick Riposte slice is hit-and-run.
  - Shortening answer: put the hot needle on Null or Detour and kill it during the burst window.

The same Perfect that is a liability in P1 becomes free in P2. That is the flip.

## 2. Phase plan

Threshold: **0.50**. Phase 2 is entered at HP floor ceil(max × 0.5).

### Phase 1: Reflection (100 → 50 %)

| Field | Value |
|---|---|
| Needles | 1, tick 0 (FIXED) |
| Resistance | passive 1 (kept from today), restores each turn |
| Hub | none |
| Listener (N6) | **Echo:** ON_PERFECT (player's landed slice) → deal 4 FLAT (×tier dmg factor) to the player, once per resolve. Skipped if the player's own result is SANDBOXed. Preview shows "ECHO −4". |
| Statuses | none |

**Layout (sum 30):**

| Slice | Ticks | Effect |
|---|---|---|
| Guard | 6 | BLOCK 8 FLAT |
| Jab | 4 | SHIM 6 |
| Guard | 6 | BLOCK 8 FLAT |
| Jab | 4 | SHIM 6 |
| Lunge | 5 | SHIM 12 (centre tick Perfect) |
| Null | 5 | nothing |

- 4-tick Jabs have no Perfect: a mid-sized threat that is always at most Good.
- Lunge is the only damage spike.
- **Intake target:** about 3–5 per turn at the reference player, plus the Echo.

### Transition P1 → P2
- Damage parks at the floor (R3). Statuses survive with the centre-tick remap (R6, `cleanse_on_enter = NONE`).
- The Echo listener is removed.
- `wheel_override` swaps the layout.
- `pointer_ticks` becomes (0, 9) (N11).
- Resistance is lowered 1 → 0.
- Phase line: "Learned your timing."

### Phase 2: Duel (50 → 0 %)

| Field | Value |
|---|---|
| Needles | 2: ticks 0 and 9 |
| Resistance | 0 |
| Hub | none |
| Listener | none |
| Statuses | none |

**Layout (sum 30):**

| Slice | Ticks | Effect |
|---|---|---|
| Riposte | 5 | SHIM 10, plus **ON_HIT_DEALT**: if a Riposte lands on a Perfect-quality tick, it gains +6 (so a landed Perfect is a tax on the player's nudging choices) |
| Jab | 4 | SHIM 6 |
| Detour | 3 | SANDBOX (negates one whole attack) |
| Lunge | 5 | SHIM 14 |
| Null | 4 | nothing |
| Jab | 4 | SHIM 6 |
| Null | 5 | nothing |

- Slice cumulative boundaries: 5, 9, 12, 17, 21, 25, 30.
- With needles at 0 and 9, the second needle falls near the Riposte/Jab edge when the wheel is at rest. Rotation moves them together, so there is a rotation offset for any given pair.
- Detour here is the enemy's SANDBOX. It is a block on one attack, which is why the burst window is at the Detour/Null edge.
- **Intake target:** 6–9 per turn before enrage.

## 3. Sustain and intake

- **Sustain: none.** The current data has no heal. DEFRAG Guard is temporary block, not a heal. At most 30 % of reference damage is allowed (T3: 0.3 × 14 = 4.2/turn). P1 Guard averages BLOCK 8 × ⅓ of landings ≈ 2.7 block per turn, under that cap. For the phase budget I count it as sustain of 2.7/turn.
- **Intake at the reference player (T3):** P1 about (6 + 6 + 12) / 6 slices × 1 needle ≈ 4 per turn of raw damage × T3 factor 1.69 ≈ 6.8 before block and misses. P2 two needles ≈ 8 average, so about 12–14 at T3 before defenses. Both are above 0. The Echo adds 4 × 1.69 ≈ 6.8 only on a player's Perfect.

## 4. HP by tier

Phase budget = reference_dpt[t] × 3.5 turns − sustain × 3.5, summed over 2 phases. Sustain: P1 2.7/turn, P2 0.

| Tier | dpt | P1 budget | P2 budget | Total | Band (R2 elite) | HP set |
|---|---|---|---|---|---|---|
| T1 | 9 | 9×3.5 − 9.5 = 22 | 31.5 | 54 | 56–72 | **60** |
| T2 | 11 | 38.5 − 9.5 = 29 | 38.5 | 68 | 68–88 | **72** |
| T3 | 14 | 49 − 9.5 = 39.5 | 49 | 88.5 | 88–112 | **96** |
| T4 | 18 | 63 − 9.5 = 53.5 | 63 | 116.5 | 112–144 | **120** |

- The second P2 needle (the player's hits land on extra enemy needles) adds a margin, so I sit slightly above budget in P2. Authored `hp_by_tier` = [60, 72, 96, 120].
- Current 150 HP is far above the band.
- Threshold 0.50 gives P1 slightly more HP than the budget at T1. This is accepted.

## 5. Enrage

**Default** (elite: start 8, every 5, +25 % damage), unchanged. Expected finish is turn 6–8, so enrage appears only for a stalling player. Authored enrage is not needed because P2 already threatens.

## 6. Buffs and counter Exploits

Not applicable (elite).

## 7. Counterplay

- **P1:** Land Good on Lunge-sized slices to avoid the Echo. Use the free nudge to move a Perfect to Good rather than spending RAM. Guard is 8 block, so brute damage against Guard is wasted, and Spin or Strip to move its needle onto Null or Jab. Skip a Perfect-hook turn if the hook is cheap.
- **P2:** Pick which needle reads Riposte or Lunge, and use Spin or Jam to put the hot needle on Null/Detour. Hit at its Detour/Null edge. Perfects are now free, so the burst window is a hit-heavy turn. SANDBOX your own wheel against a Lunge/Riposte double.
- **Weak players:** Chase Perfects in P1 and eat the Echo every turn. They also ignore the second needle, which turns P2 into 12+ damage per turn.

## 8. Systems needed

| Need | N# | Fallback |
|---|---|---|
| Phases, parking, status keep | N3 | none (core) |
| Per-tier HP | N2 | data-only: single `hp` with band median (96) |
| Enemy listener (ON_PERFECT Echo) | N6 | fallback: fixed 4 damage on Lunge instead of a listener |
| Pointers on any tick (0, 9) | N11 | (0, 10) if blocked |
| Variable slice sizes (4/6/3) | N12 | fallback: uniform 5-tick slices and 6 slots; loses the "no Perfect" Jab |
| Amount mode (FLAT) | N1 | FLAT is today's behaviour |
| Enrage | N4 | none |
| ON_HIT_DEALT rider (Riposte) | N6 | drop it; Riposte becomes a plain SHIM 14 |

Defense trio naming (N14) is used for Detour = SANDBOX.

## 9. Delta vs today

- **Kept:** the Mirror identity, the Shim/Defrag/Detour/Null vocabulary, `is_elite`, `cycle_reward = 40` (may be reduced, since the fight is shorter), and the second needle at 15 ticks reduced to 9 in P2 only.
- **Changed:** HP 150 → [60, 72, 96, 120]; a 2-phase structure; 6 equal slices become variable sizes; resistance 1 is only in P1; a new Echo listener.
- **Today's wheel** has the second needle at 15 ticks from the start. It is a flat attrition fight and has no shift.
- **heat_effects:** the file has none, so there is nothing to keep. I propose **none**: the elite is already gated by L5–6 and Heat-driven elite frequency.

## 10. Predicted sim check

No baseline row (estimated from the wheel).
- Turns: T1 about 6, T2 about 6.5, T3 about 7, T4 about 7.5 at reference skill. P90 is at most 9.
- Win rate: T1 ≥ 97 %, T2 ≥ 95 %, T3 ≈ 92 %, T4 ≈ 85 %. The T4 shortfall comes from P2's two needles plus the T4 damage factor of 2.2.
- Why: the budget is built from reference damage, and the Echo makes naive Perfect-chasing cost 6–9 per Perfect.

## 11. Open questions

Q: Should the Echo listener hit once per resolve or once per Perfect needle?
Q: Is "Perfect-quality Riposte gains +6" too hard to read? A plain damage bump may be clearer.
Q: Does the 9-tick needle gap need a HUD marker for the pair?
Q: Should P2 resistance go to 0, or stay at 1 to protect the Detour window?
Q: Should the second REBEL_CELL elite also have a distinct threshold (e.g. 0.6) so the two are not the same shape?
