<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__05_future_rebel_cell; status ok; tokens in 6468 cache-write 0 cache-read 32007 out 2155; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_rc_standing_contract: Standing Contract
**Mechanic:** FUTURE, corporation rebel_cell, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Sign a contract that weakens the next fights in exchange for a standing obligation: a burden the Cell must carry through the following fights, not only the one after the signature.

## TerminalEventData fields
- id: `ev_rc_standing_contract`
- title: Standing Contract
- speaker: STREET_MERC (1)
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
- effects: MODIFY_HEAT / CAMPAIGN / amount 6
- reward: none
- (new) next_combat_overrides, duration the next 2 combats:
  - enemy starts FROZEN (skips its first start-of-turn respin)
  - enemy resistance -1 (floor 0)
  - enemy HP -15 % (percent of that enemy's max HP, applied after the tier base per R2)

### 2. Sign the long contract
- label: "Sign for four fights (-25 Cycles, enemy damage +15 % in the final one)"
- result_text: "'Four,' she says, and smiles like a ledger. The favors stack up. So does the interest."
- cycle_cost: 25
- hp_cost: 0
- effects: none
- reward: none
- (new) next_combat_overrides, duration the next 4 combats:
  - fights 1-4: one free nudge extra on the player's wheel (an additional free nudge per turn)
  - fights 1-4: phase reveal (all enemy phases and next layouts shown from turn 1)
  - fight 4 only: enemy damage +15 % (a debt called in)
- Note: the burden lands exactly when the run is likely deepest in; the benefit is front-loaded.

### 3. Counter-offer: read the fine print
- label: "Haggle (-3 HP, 50 % of the benefit)"
- result_text: "She raises an eyebrow, crosses out a clause, and initials it. 'Half the favor, half the knife.'"
- cycle_cost: 0
- hp_cost: 3
- effects: none
- reward: none
- (new) next_combat_overrides, duration the next 3 combats:
  - enemy resistance -1
  - satellite removal: the first satellite spawned by the enemy in each of these combats never docks (the data-only form is `satellite_spawn_count -1`)
  - no penalty clause
- Note: deterministic, no roll. The haggling is a fixed text, not a check.

### 4. Tear it up
- label: "Walk away"
- result_text: "The slate goes dark. She does not look insulted. She looks like she is writing your name somewhere else."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- (new) none

## Design notes
- **Decision shape:** three levels of commitment (short, long, haggled), none strictly dominant.
  - Short is the strongest per fight: the freeze, -1 resistance and -15 % HP give roughly one fewer turn per fight. That is worth about 3-4 HP per fight at T2-T3 intake. It costs 8 HP and 6 Heat now.
  - Long covers a whole mid-run stretch with the free nudge and the reveal (a precision aid, worth about 1 RAM per turn), but fight 4 hits 15 % harder, and that fight is typically the elite or Rack at the end of the stretch. A player who dies in fight 4 would have been better off with the short deal.
  - Haggle is the safe, lower-ceiling choice that pairs well with builds relying on nudges (Ghost) and satellites (Botnet, which gains from no enemy satellite docking).
- **Economy vs a typical run:** a run has about 5 combats and 100-150 Cycles. 25 Cycles is a real but not crippling cost, and 6 Heat is about 1 minor threshold of 10. These are placeholders for the balance sim.
- **Interactions:**
  - The -15 % HP override must still respect the R3 floors: percent HP changes scale max HP for the fight and thresholds are recomputed from it, so phases stay 3-4 turns.
  - The freeze override clashes with an enemy already frozen: no stacking, it just applies once.
  - A boss at the end of the window is excluded: overrides ignore the HQ boss (a Q below), so the long contract does not trivialize it.
  - Contracts do not stack: a second Standing Contract replaces the first (the same override key).
- **Determinism:** no randomness anywhere. Overrides are a fixed list stored in `next_combat_overrides` on RunState with a counter, saved with the run. The preview shows each override as a chip on the enemy ("CONTRACT: -1 RES").
- **Tone:** REBEL_CELL is the Cell's own world, so the speaker is a fixer who deals in favors. The contract is a mirror of the corporate subscription: you are reading someone else's terms.
- **Text keys:** `ev_rc_standing_contract.*` for the title, text, three labels and four results; an override chip label `contract_chip` with the parameters {resistance, hp_pct, dmg_pct, fights_left}.

## Q:
- Q: Do next_combat_overrides apply to mini-boss and boss fights, or skip them? (The draft assumes the window skips boss fights and keeps the count for the next normal or elite one.)
- Q: Should the override counter tick down on a fight fled or abandoned, or only on a completed one?
