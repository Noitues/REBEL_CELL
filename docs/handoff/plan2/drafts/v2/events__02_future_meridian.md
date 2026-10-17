<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__02_future_meridian; status ok; tokens in 5271 cache-write 0 cache-read 32585 out 3242; cost $0.025. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, undefined filter/expiry, contradicts the Q):** Decided. Choice 3 uses `applies_to_class = [elite, mini_boss]`, `duration_combats = 1`, and it persists until a matching fight. There is no `expires_after_combats` cap and no second expiry system. The first Q (expire vs persist) is removed because it is now decided. The map chip tells the player what is pending.
- **Issue 2 (BLOCKER, arithmetic):** Fixed. +2 Heat is one fifth of a MINOR step (10). HP figures are now stated per tier against the R2 bands (see Design notes).
- **Issue 3 (MAJOR, HP percent vs R2/R3):** `enemy_hp_pct` now applies to **max HP at `create_combat`**, and R3 floors are computed from the reduced max: ceil(reduced max × threshold).
- **Issue 4 (MAJOR, choice 2 dominates, choice 1 weak):** Choice 2 is now 1 combat, with resistance −1 and damage −10% together, +2 Heat. Choice 1 gains `enemy_hp_pct = −10` and works on any class. Both are one-combat edges that differ in kind: information and tempo versus Heat-paid softening.
- **Issue 5 (MAJOR, mistagged systems):** `reveal_phases`, `bonus_free_nudges` and `enemy_starts_frozen` are retagged as N16 override fields. N5 (Chart Hidden) is involved only as the buff that reveal overrides.
- **Issue 6 (MAJOR, Freeze rule):** Frozen now reads "skips its next start-of-turn respin", which is turn 1 of that fight. The preview shows the frozen state and the unchanged tick from the first turn on, so the intent is known.
- **Issue 7 (NIT):** Defined: `reveal_phases` overrides Chart Hidden for that fight.
- **Issue 8 (NIT):** `dispatch_clue` is left empty.
- **Second critic Q (additive vs cap):** Decided: same-field overrides sum additively. Resistance delta is floored at 0 total, damage at −50%, HP at −40%.
- **Kept:** the three-way quiet/loud/paid split, the run-state storage with application at `create_combat`, and choice 3's HP-cost-for-conditional-payoff shape.

# ev_mer_dock_broadcast: Dock Floor Broadcast

**Mechanic:** FUTURE, corporation meridian, min_tier 1, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** Spend the Terminal's open channel on a safe info-and-tempo edge for the next fight, a Heat-paid softening edge, or an HP-paid ambush on the next elite or mini-boss.

## TerminalEventData fields
- **id:** `ev_mer_dock_broadcast`
- **title:** Dock Floor Broadcast
- **speaker:** STREET_MERC
- **text:** "Every loading bay in the sector runs one shared PA, and the Terminal sits on its channel. A dispatcher's voice is reading out shift assignments: bay numbers, pallet counts, which conveyor wardens are rolling next. Somebody left the mic open and nobody is cleared to cut in. You could listen, jam it, or talk. A voice on this channel gets obeyed by a few hundred machines."
- **corporation_id:** `meridian`
- **min_tier:** 1
- **dispatch_clue:** (empty)
- **foreshadows:** (empty)
- **weight:** 1.0

## Choices

### 1. Listen to the shift roster
- **label:** "Take notes on the roster (next fight: phases revealed, +1 free nudge, enemy max HP −10%)"
- **result_text:** "You copy the rotations and the dead zones in the schedule. The next crew you meet is exactly where the roster says it'll be, and a few units are already off-shift."
- **cycle_cost:** 0, **hp_cost:** 0
- **effects:** none
- **reward:** none
- **starts_combat (new):** none
- **next_combat_overrides (new, N16):**
  - `reveal_phases = true` (overrides Chart Hidden for that fight)
  - `bonus_free_nudges = 1`
  - `enemy_hp_pct = −10` (max HP at `create_combat`; R3 floors recomputed from the new max)
  - `applies_to_class = any`, `duration_combats = 1`
- **map_edits (new):** none

### 2. Jam the channel
- **label:** "Jam the PA (next fight: enemy resistance −1, enemy damage −10%; +2 Heat)"
- **result_text:** "Static floods the bays. Wardens stall at junctions waiting for orders that never come. Somewhere a supervisor starts logging a fault, and the log has your signature in it."
- **cycle_cost:** 0, **hp_cost:** 0
- **effects:** MODIFY_HEAT / CAMPAIGN / amount 2
- **reward:** none
- **starts_combat (new):** none
- **next_combat_overrides (new, N16):**
  - `enemy_resistance_delta = −1` (total floored at 0)
  - `enemy_damage_pct = −10` (tier-independent debuff)
  - `applies_to_class = any`, `duration_combats = 1`
- **map_edits (new):** none

### 3. Issue a false order
- **label:** "Broadcast a fake dispatch (−8 HP; next Elite or Mini-Boss: starts Frozen, max HP −15%)"
- **result_text:** "You mimic the dispatcher's cadence and send an elite unit to the wrong dock. Feedback from the PA loop rattles your skull, but the order sticks. When the real unit finally gets back on route, it's late and short on parts."
- **cycle_cost:** 0, **hp_cost:** 8
- **effects:** none
- **reward:** none
- **starts_combat (new):** none
- **next_combat_overrides (new, N16):**
  - `enemy_starts_frozen = true` (skips its next start-of-turn respin, i.e. turn 1; the preview shows the frozen state)
  - `enemy_hp_pct = −15` (max HP at `create_combat`; floors recomputed)
  - `applies_to_class = [elite, mini_boss]`, `duration_combats = 1`
  - persists until a matching fight occurs; no expiry cap
- **map_edits (new):** none

### 4. Walk on
- **label:** "Cut the line and walk on"
- **result_text:** "The voice goes back to reading pallet counts. Nobody noticed you were ever there."
- No cost, effects or reward.

## Design notes
- **The tradeoff:** Choice 1 is free and safe but only useful if the player can guess which fight benefits (reveal does nothing on a 1-phase normal; the −10% HP and the nudge still help). Choice 2 pays Heat, which is one fifth of a MINOR step (10), for a damage and resistance edge on the next fight of any class. Choice 3 costs 8 HP (about 13% of a 60 HP Breaker) and waits for an elite or mini-boss. Layers 3–6 carry about one elite per layer, so the wait is usually short; the risk is that the HP is spent early and the payoff is far off. Each option wins in a different situation.
- **Numbers (placeholders, R2 bands):**
  - Choice 1: −10% max HP is about 3–4 HP on a 36 HP T1 normal, and about 6–7 on a 68 HP T3 elite phase pair.
  - Choice 3, T1 elite (56–72 HP): −15% is about 8–11 HP, under a third of a 28–36 HP phase. T3 elite (88–112): about 13–17 HP, a third of a phase. T3 mini-boss (3 phases, 132–162): about 20–24 HP.
  - The main value of choice 3 is the Frozen first turn, not the HP.
- **Interactions:** Overrides from several events sum per field; resistance delta is floored at total 0, damage at −50%, HP at −40%. Reveal overrides Chart Hidden (N5) for that fight. Choice 2's resistance reduction offsets the Heat-50 "+1 resistance" modifier.
- **Determinism:** Overrides are fixed data in `RunState.next_combat_overrides`, saved with the run and applied at `create_combat`. No RNG is drawn, and previews equal results.
- **Dependencies:** N16 (override fields `reveal_phases`, `bonus_free_nudges`, `enemy_starts_frozen`, `enemy_hp_pct`, `enemy_resistance_delta`, `enemy_damage_pct`, `applies_to_class`, `duration_combats`). N5 only for Chart Hidden. **Data-only fallback:** none for the overrides themselves; without N16 these choices collapse to plain Heat or HP trades.
- **Text keys:** `ev_mer_dock_broadcast.title`, `.text`, `.c1`–`.c4` labels and results; a map chip tooltip per pending override.

## Q:
- Should the map chip name the exact pending override (recommended) or only show an icon until the fight starts?
- Should choice 3's wait have a safety valve, such as converting to a plain −5% HP on the next normal if the run ends its last layer without an elite?
