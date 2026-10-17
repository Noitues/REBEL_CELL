<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__05_future_rebel_cell; status ok; tokens in 5148 cache-write 0 cache-read 32585 out 3082; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, HP -15 % recomputes thresholds):** Removed the enemy HP percent override and the sentence about recomputed thresholds. Choice 1 now uses `opening_stun` (enemy's first turn-1 intent is skipped, an extension of the Freeze behavior), `resistance_delta -1`, and `first_hit_bonus` (the player's first landed hit in each fight deals +25 %). This does not touch `hp_by_tier`, `hp_bands` or phase floors, so R2 and R3 stay intact and "3-4 turns per phase" holds.
- **Issue 2 (BLOCKER, boss applicability):** Stated the rule in the Mechanic line and the design notes: overrides apply to Router, Elite Router and Server Rack fights only. Mini-boss and HQ boss fights are skipped, and the counter keeps its value (a skipped fight does not tick it). Racks are named as covered, so the fight-4 damage penalty rule is now consistent (it can land on an Elite or a Rack). This answers both of the critic's Q lines and removes the v1 Q on boss fights.
- **Issue 3 (MAJOR, dominance):** Haggle is now 2 fights, -3 HP, a single benefit (resistance -1), and no satellite key. It is weaker than short in both ceiling and length. Long now costs 20 Cycles, adds +4 Heat, and its fight 4 deals +25 % enemy damage, so the cost is clearer and a player who expects to die at fight 4 has a real reason to take short.
- **Issue 4 (MAJOR, satellite key):** Dropped the satellite override entirely rather than inventing a key. This adds no scope.
- **Issue 5 (MAJOR, free nudge and phase reveal):** Both are marked as N16 `next_combat_overrides` keys, `free_nudge_bonus` and `reveal_phases`. The extra nudge refreshes each turn with the start-of-turn free nudge refresh (GDD 2.2). `reveal_phases` is a per-fight display flag only: it shows phase thresholds and next layouts from turn 1, and it does not cancel a boss's Chart Hidden buff (moot here, since bosses are excluded).
- **Issue 6 (NIT, template fields):** Heat is now `MODIFY_HEAT / CAMPAIGN / amount / duration_turns 0`, and a chip key exists for each choice result.
- **Issue 7 (NIT, replacement key):** The replacement rule is tied to the override group key `contract`. A new contract replaces the existing `contract` group and its counter.
- **Critic Q (chip on the map):** Kept as a Q.

---

# ev_rc_standing_contract: Standing Contract
**Mechanic:** FUTURE, corporation rebel_cell, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none. Overrides apply to Router, Elite Router and Server Rack fights only; mini-boss and HQ boss fights are skipped and do not tick the counter.
**One-line decision:** Sign a contract that softens the next fights in exchange for a burden, choosing between a short strong deal, a long front-loaded deal with a debt, or a small safe hedge.

## TerminalEventData fields
- id: `ev_rc_standing_contract`
- title: Standing Contract
- speaker: STREET_MERC
- text: "A fixer in a rain-slick doorway holds out a slate with one paragraph on it. She says the Cell's old suppliers still have friends inside the corporate patrol schedules. Sign, and the next few fights get softer at the edges. Break it, and everyone in the doorway remembers. 'Nobody here works for free, leash-breaker. Not even the ones who say they do.'"
- corporation_id: `rebel_cell`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Sign the short contract
- label: "Sign for two fights (-8 HP, +6 Heat)"
- result_text: "The ink is warm. Two patrol routes shift on a schedule you never saw. Your pulse does not like the pen."
- cycle_cost: 0
- hp_cost: 8
- effects: MODIFY_HEAT / CAMPAIGN / amount 6 / duration_turns 0
- reward: none
- (new) next_combat_overrides, group `contract`, counted fights 2 (N16):
  - `opening_stun`: the enemy's first intent is skipped (data-only fallback: Freeze status on its wheel at combat start)
  - `resistance_delta -1` (floor 0)
  - `first_hit_bonus 25 %`: the player's first landed hit each fight

### 2. Sign the long contract
- label: "Sign for four fights (-20 Cycles, +4 Heat, fight 4 hits harder)"
- result_text: "'Four,' she says, and smiles like a ledger. The favors stack up. So does the interest."
- cycle_cost: 20
- hp_cost: 0
- effects: MODIFY_HEAT / CAMPAIGN / amount 4 / duration_turns 0
- reward: none
- (new) next_combat_overrides, group `contract`, counted fights 4 (N16):
  - fights 1-4: `free_nudge_bonus 1` (one extra free nudge, refreshing each turn)
  - fights 1-4: `reveal_phases` (thresholds and next layouts shown from turn 1)
  - fight 4 only: `enemy_damage_pct +25` (the debt called in)

### 3. Haggle over the fine print
- label: "Haggle (-3 HP, two fights)"
- result_text: "She raises an eyebrow, crosses out a clause, and initials it. 'Half the favor, half the knife.'"
- cycle_cost: 0
- hp_cost: 3
- effects: none
- reward: none
- (new) next_combat_overrides, group `contract`, counted fights 2 (N16):
  - `resistance_delta -1`
  - no penalty clause
- Fixed text, no roll.

### 4. Tear it up
- label: "Walk away"
- result_text: "The slate goes dark. She does not look insulted. She looks like she is writing your name somewhere else."
- cycle_cost: 0, hp_cost: 0, effects: none, reward: none
- (new) none

## Design notes
- **Decision shape:** each deal wins in a different spot, and none dominates.
  - Short is the strongest per fight: a skipped enemy opener, -1 resistance and a +25 % first hit. That is worth about one fewer enemy turn per fight, roughly 3-4 HP at T2-T3 intake, so about 6-8 HP back over two fights against 8 HP and 6 Heat paid up front. It is a break-even trade that rewards builds finishing quickly (Breaker).
  - Long gives four fights of precision aid (about 1 RAM per turn plus planning information) for 20 Cycles and 4 Heat, but the final fight hits 25 % harder. That fight is often an Elite or a Rack at the stretch's end, so a player who is low on HP by then may be better off with short.
  - Haggle is the cheap hedge: 3 HP for -1 resistance over two fights. It is useful to Ghost and similar builds, but it has the lowest ceiling.
- **Economy vs a typical run:** a run has about 5 combats and 100-150 Cycles. 20 Cycles is a real cost, and 4-6 Heat is roughly half a minor threshold. All numbers are placeholders for the sim.
- **Interactions:**
  - No override touches HP, `hp_by_tier` or phase thresholds, so R2 and R3 budgets stand.
  - The counter ticks only on a completed counted fight. A fled or abandoned fight does not tick it.
  - A new contract replaces the existing `contract` group and resets its counter. Contracts never stack.
  - `opening_stun` on an already frozen enemy applies once.
- **Determinism:** no randomness. Overrides are a fixed list in `next_combat_overrides` on RunState, saved with the run. The preview shows each as an enemy chip ("CONTRACT: -1 RES"), so preview equals result.
- **Tone:** the contract mirrors the corporate subscription: you are reading someone else's terms.
- **Text keys:** `ev_rc_standing_contract.title|text|choice1..4.label|choice1..4.result`; chip keys `contract_chip_stun`, `contract_chip_res`, `contract_chip_hit`, `contract_chip_nudge`, `contract_chip_reveal`, `contract_chip_debt` with parameters {fights_left}.

## Q:
- Q: Should the contract chip also show remaining fights on the node map, or only on the enemy in combat?
- Q: Should the long deal's fight-4 debt skip to the next eligible fight if fight 4 would be a mini-boss, or simply lapse?
