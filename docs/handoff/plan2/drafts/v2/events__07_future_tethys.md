<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__07_future_tethys; status ok; tokens in 4820 cache-write 0 cache-read 32585 out 2938; cost $0.023. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, undefined RNG stream)** -> The roll is removed and the event is fully deterministic, which also answers critic Q1. The truth of the rumor is a pure function of a saved run field, `combat_index % 2`: even is true, odd is false. This needs no RNG stream and no N17. The tooltip shows the exact result for the current combat, so preview equals result. The player can read the parity from the map position, which turns the gamble into a reading puzzle. The triage row is resolved by removing the roll. A designer ruling already allows hidden outcomes only at saved checkpoints, so there is no conflict.
- **Issue 2 (MAJOR, dominance and asymmetry)** -> Choice 2 now covers 1 combat, and the true and false magnitudes mirror each other. Because the outcome is known from the parity, choice 2 is no longer dominated by "strictly better than verifying". The player picks it when the parity is favorable, and the cost is never hidden. The EV arithmetic is shown in the notes.
- **Issue 3 (MAJOR, phase reveal dead on normals, wrong N#)** -> Choice 1 is now Frozen plus a turn-1 `nudge_locked`. The layout reveal applies only if the target has 2+ phases (a no-op on normals, and the text says so). It is tagged "N5 Chart Hidden counter".
- **Issue 4 (MAJOR, choice 3 near-dominant, Heat)** -> Heat is dropped (Heat is not FUTURE family; critic Q2 answered). Choice 3 is now +25 Cycles with enemy +20% damage on turn 1 and +1 resistance for the next combat. The "divers remember" line is changed to match the actual effect.
- **Issue 5 (MAJOR, nudge fields without an N#)** -> The fields are named: `next_combat_overrides.player_free_nudge` (+1 / −1), `enemy_start_frozen`, `enemy_resistance_delta`, `enemy_damage_pct`, `enemy_damage_turns`, all N16. `nudge_locked` is N7. Frozen is defined as "skips its first start-of-turn respin" (GDD Freeze).
- **Issue 6 (NIT, label and speaker)** -> The label now includes "the pump tech's cousin". The text is rewritten in the Street Merc voice (first person).
- **Issue 7 (NIT, `tethys`)** -> `tethys` is confirmed as a D1 corporation id (Tethys Deep), and this is noted in the notes. It is not in the round-1 enemy list, so the event names no enemy ids.

# ev_tet_pressure_rumor: Pressure Rumor

**Mechanic:** FUTURE, corporation tethys, min_tier 2, weight 1.0, dispatch_clue false, foreshadows none
**One-line decision:** Pay to confirm a dockside rumor, bet on it based on where you are in the run, or sell it on. A rumor is true on even-numbered fights and false on odd ones, so you can read it, but only if you count.

## TerminalEventData fields
- id: `ev_tet_pressure_rumor`
- title: Pressure Rumor
- speaker: STREET_MERC (1)
- text: "A diver with a cracked faceplate is feeding the whole bulkhead the same story. The next hull section is running a pressure fault, and the locks on it cycle slow. She heard it from a man who heard it from a pump tech, and the pump tech is nowhere. Water's ankle deep in this corridor and everybody's nodding like it's gospel. I've seen rumors drown better crews than ours."
- corporation_id: `tethys`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 1.0

## Choices

### 1. Pay to verify
- label: Pay the pump tech's cousin (-20 Cycles)
- result_text: "The cousin pulls a maintenance log. The locks really are slow. You walk in knowing where to lean."
- cycle_cost: 20
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new, N16), duration 1 combat:
  - `enemy_start_frozen: true` (the enemy skips its first start-of-turn respin)
  - `nudge_locked` on the enemy wheel, turn 1 only (N7)
  - `reveal_phases: true`, applied only if the target has 2+ phases (a no-op on normals). This is the N5 Chart Hidden counter.
- Stake: a small, certain edge, bought with Cycles.

### 2. Act on the rumor
- label: Act on the rumor (this fight is {true/false}, shown in the tooltip)
- result_text: "You plan around a slow lock. If she's right, you walk through it. If not, the hull answers back."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new, N16), duration 1 combat. The branch is set by `combat_index % 2`: even is true, odd is false. It is a pure function of a saved run field, so no RNG is used and the tooltip shows the exact result.
  - **True:** `enemy_start_frozen: true`, `enemy_resistance_delta: -1`, `player_free_nudge: +1`.
  - **False:** `enemy_damage_pct: +15`, `enemy_damage_turns: all`, `enemy_resistance_delta: +1`, `player_free_nudge: -1`.
- Stake: free, but it is a bet on counting.

### 3. Sell it on
- label: Sell the rumor to the gossip desk (+25 Cycles)
- result_text: "You pass it up the line as fact. It pays now. The next hull section gets nervous, and so does the crew that has to fight in it."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 25
- reward: none
- next_combat_overrides (new, N16), duration 1 combat: `enemy_damage_pct: +20`, `enemy_damage_turns: 1` (turn 1 only), `enemy_resistance_delta: +1`.
- Stake: instant money, paid for with a harder next fight.

## Design notes
- **No dominant option.** Choice 2 is free and strictly strongest on a true parity (Frozen, −1 resistance, +1 nudge) but strictly worse than verifying on a false parity (+15% damage, +1 resistance, −1 nudge). Verifying costs 20 Cycles for a certain, modest edge. Selling is the greedy line: it nets +25 Cycles against a harder fight. Each option wins in a different state of the run.
- **EV, symmetrical.** Treat a nudge as worth about 1 RAM. True is about +3 value (freeze ≈ 1.5, −1 resistance ≈ 1, nudge ≈ 0.5). False is about −3 (damage ≈ 1.5, +1 resistance ≈ 1, −1 nudge ≈ 0.5). A player who cannot read the parity averages 0, which is below verifying's certain edge (≈ +2 for 20 Cycles). A player who reads the parity gets +3 free, or skips to option 1 or 3.
- **Economy (GDD 11 placeholders).** A Router pays about 15–25 Cycles, so verifying costs about one fight's income. Selling gains about the same, but with a −2 to −3 value penalty, so it only helps Cycle-starved players.
- **Interactions.** The Frozen and resistance changes stack with Ghost's resistance-ignore nudge and with Hub Breach. The phase reveal counters Chart Hidden for that one fight.
- **Determinism.** No randomness is added. `combat_index` is a saved run field, so the result survives save and load and matches the preview.
- **Dependencies.** N16 (`next_combat_overrides`, required), N7 (`nudge_locked`), N5 (Chart Hidden counter). Data-only fallback: use MODIFY_RESISTANCE and GAIN_CYCLES effects on the next combat, and drop the nudge fields.
- **Text keys.** `ev_tet_pressure_rumor.title`, `.text`, `.c1`–`.c3` labels and results, and a tooltip key `rumor_parity`.

## Q:
Q: Should the parity hint be shown outright in the tooltip, or discoverable from the node count on the map?
Q: Is a +1/−1 free-nudge override acceptable under N16, or should it be a RAM grant instead?
