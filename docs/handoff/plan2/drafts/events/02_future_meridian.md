<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__02_future_meridian; status ok; tokens in 6467 cache-write 0 cache-read 32007 out 2176; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_mer_dock_broadcast: Dock Floor Broadcast

**Mechanic:** FUTURE, corporation meridian, min_tier 1, weight 1.0, no dispatch_clue, no foreshadows
**One-line decision:** Spend the Terminal's open channel to tip the next fights in your favor, and choose between a quiet edge, a loud edge that costs Heat, and a paid edge on one specific enemy.

## TerminalEventData fields
- **id:** `ev_mer_dock_broadcast`
- **title:** Dock Floor Broadcast
- **speaker:** STREET_MERC (1)
- **text:** "Every loading bay in the sector runs one shared PA, and the Terminal sits on its channel. A dispatcher's voice is reading out shift assignments: bay numbers, pallet counts, which conveyor wardens are rolling next. Somebody left the mic open and nobody is cleared to cut in. You could listen, jam it, or talk. A voice on this channel gets obeyed by a few hundred machines."
- **corporation_id:** `meridian`
- **min_tier:** 1
- **dispatch_clue:** false
- **foreshadows:** (empty)
- **weight:** 1.0

## Choices

### 1. Listen to the shift roster
- **label:** "Take notes on the roster (next fight: enemy phases revealed, +1 free nudge)"
- **result_text:** "You copy the rotations and the dead zones in the schedule. The next crew you meet is exactly where the roster says it'll be."
- **cycle_cost:** 0, **hp_cost:** 0
- **effects:** none
- **reward:** none
- **next_combat_overrides (new):**
  - `reveal_phases = true` (N3 phase reveal, so the player sees thresholds and next layouts)
  - `bonus_free_nudges = 1`
  - duration: the next 1 combat

### 2. Jam the channel
- **label:** "Jam the PA (next 2 fights: enemy resistance −1, enemy damage −10%; +2 Heat)"
- **result_text:** "Static floods the bays. Wardens stall at junctions waiting for orders that never come. Somewhere a supervisor starts logging a fault, and the log has your signature in it."
- **cycle_cost:** 0, **hp_cost:** 0
- **effects:** MODIFY_HEAT / CAMPAIGN / amount 2
- **reward:** none
- **next_combat_overrides (new):**
  - `enemy_resistance_delta = −1` (floor 0)
  - `enemy_damage_pct = −10`
  - duration: the next 2 combats

### 3. Issue a false order
- **label:** "Broadcast a fake dispatch (−8 HP; next Elite or Mini-Boss: starts Frozen, HP −15%)"
- **result_text:** "You mimic the dispatcher's cadence and send an elite unit to the wrong dock. Feedback from the PA loop rattles your skull, but the order sticks. When the real unit finally gets back on route, it's late and short on parts."
- **cycle_cost:** 0, **hp_cost:** 8
- **effects:** none
- **reward:** none
- **next_combat_overrides (new):**
  - `enemy_starts_frozen = true` (skips its first start-of-turn respin, per Freeze)
  - `enemy_hp_pct = −15`
  - applies to: the next combat whose enemy class is elite or mini_boss; it persists until that fight, with a cap of 3 fights, after which it expires unused

### 4. Walk on
- **label:** "Cut the line and walk on"
- **result_text:** "The voice goes back to reading pallet counts. Nobody noticed you were ever there."
- No cost, effects or reward.

## Design notes
- **The tradeoff:** Choice 1 is free and safe, but it covers one fight only. Choice 2 lasts two fights and softens every enemy, but pays for it in Heat (+2 is about 1/12 of a MINOR threshold of 10, which is cheap early and more painful once the player is near a MAJOR line). Choice 3 is the highest-impact option but conditional. It costs 8 HP (about 13% of a 60 HP Breaker) and only pays off if the player reaches an elite or mini-boss within 3 fights. Layers 3–6 typically offer about one elite per layer, so it usually lands, but a player who has taken a Terminal at layer 2 can still dodge elites. Each option wins in a different situation, so none dominates.
- **Numbers (placeholders):** An elite at 2 phases has about 88–112 HP at T3. −15% is roughly 13–17 HP, nearly a full phase of reference damage at T1–T2. Frozen removes one turn of enemy re-aim, so the first turn's intent is known and stable.
- **Interactions:** The phase reveal in choice 1 gives no benefit against normals (1 phase), so it is best saved for a visible elite or boss on the map; the player must guess the next fight. It stacks with Chart Hidden by countering it. Choice 2's resistance reduction combines with the HEAT-based "+1 resistance" modifier at Heat 50 and floors at 0. Overrides from several events stack additively per field and are consumed per combat.
- **Determinism:** All overrides are fixed data in `RunState.next_combat_overrides`. They are applied at `create_combat`, so previews match results. No new RNG is drawn. They must be saved with the run so reloading doesn't reset or reroll them.
- **Dependencies:** N16 (`next_combat_overrides`) with the `duration_combats` and `applies_to_class` filters; N3 for `reveal_phases`. **Data-only fallback:** none for the overrides themselves. Without N16, choice 1 could degrade to a plain `GAIN_RAM`-style effect, which loses the "future" identity.
- **Text keys:** `ev_mer_dock_broadcast.title`, `.text`, `.c1`–`.c4` labels and results; an override chip tooltip for each field (reveal, nudge, resistance, damage, frozen, HP).

## Q:
- Should the Frozen and HP override in choice 3 expire after 3 fights (as drafted) or persist until used, accepting a possible long wait?
- Should override chips show on the map so the player can plan which node benefits, or stay hidden until combat starts?
