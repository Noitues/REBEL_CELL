<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__07_future_tethys; status ok; tokens in 6466 cache-write 0 cache-read 32007 out 1952; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_tet_pressure_rumor: Pressure Rumor

**Mechanic:** FUTURE, corporation tethys, min_tier 2, weight 1.0, dispatch_clue false, foreshadows none
**One-line decision:** Pay to confirm a dockside rumor, act on it unverified, or sell it on. A true rumor weakens the next fight, a false one hardens it, and the only way to know is to pay for the answer.

## TerminalEventData fields
- id: `ev_tet_pressure_rumor`
- title: Pressure Rumor
- speaker: STREET_MERC (1)
- text: "A diver with a cracked faceplate is feeding the whole bulkhead the same story. The next hull section down is running a pressure fault, and the locks on it cycle slow. She heard it from a man who heard it from a pump tech, and the pump tech is nowhere. The water in this corridor is already ankle deep, and everyone is nodding like it's gospel. A rumor is only worth what it costs you to be wrong."
- corporation_id: `tethys`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 1.0

## Choices

### 1. "Pay the pump tech's cousin to verify (-20 Cycles)"
- label: Pay to verify (-20 Cycles)
- result_text: "The cousin pulls a maintenance log. The rumor is half true: the locks are slow, but the pressure is not what she said. You walk in knowing exactly where to lean."
- cycle_cost: 20
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new): for the **next 1 combat**: the enemy's wheel is nudge-locked on turn 1 only (`nudge_locked`, N7), and the phase layouts are revealed from the start (phase reveal). The result is the same every time, with no hidden roll.
- Stake: a small, certain edge, bought with Cycles.

### 2. "Trust it and go in heavy"
- label: Act on the rumor
- result_text: "You plan around a slow lock. If she was right, you walk through it. If not, the hull answers back."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: none
- next_combat_overrides (new): for the **next 2 combats**, decided by the `events` RNG stream at a checkpoint (the rumor is true or false, so the preview must show the odds, never a single outcome):
  - **True (50 %):** the enemy starts Frozen (skips its first respin) and takes −1 resistance. Both combats get a free extra nudge on turn 1.
  - **False (50 %):** the enemy deals +20 % damage and starts with +1 resistance. The player's turn-1 free nudge is lost for both combats.
- The checkpoint is saved, so quitting and reloading cannot reroll it.
- Stake: a swingy bet that runs two fights.

### 3. "Sell the rumor to the Cell's own gossip desk"
- label: Sell it on
- result_text: "You pass it up the line as fact. It pays now. If it turns out false, the divers will remember who lied to them."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 25; MODIFY_HEAT, target CAMPAIGN, amount +2
- reward: none
- next_combat_overrides (new): for the **next 1 combat**: the enemy starts with a stronger opening (+10 % enemy damage on turn 1). A false lead spreads and the water is watching you.
- Stake: instant money, a small Heat cost, and a mild penalty.

## Design notes
- **No dominant option.** Verifying costs 20 Cycles for a small certain edge. Trusting is free but is a coin flip, and the swing is bigger than verifying's gain (true is strictly better than verifying, false is worse). Selling is the greedy line: it nets +25 Cycles at the price of +2 Heat and a mild penalty, and it never helps the next fight.
- **Economy.** Placeholders against GDD 11: a typical Router pays about 15–25 Cycles. Verifying costs about one fight's income. Selling yields about one fight's income plus Heat, so it is a modest net gain only if the player is Cycle-starved.
- **EV check.** Trusting averages out at roughly even to slightly better than verifying, but with variance across two fights. Safe players verify and risk-takers trust.
- **Interactions.** The Frozen and resistance overrides stack with Ghost's resistance-ignore nudge and with Hub Breach. A phase reveal also counters a "Chart Hidden" boss buff (R7) for that one fight.
- **Determinism.** The true/false split is drawn once from the `events` stream when the choice is made, stored in `next_combat_overrides`, and shown as "Rumor: 50/50" on the choice tooltip. No further randomness is added during combat.
- **Dependencies.** The N16 `next_combat_overrides` run-level field is required. Phase reveal needs N3 and N7 for `nudge_locked`. Data-only fallback: replace the overrides with MODIFY_RESISTANCE and MODIFY_HEAT effects and drop the true/false split.
- **Text keys.** `ev_tet_pressure_rumor.title`, `.text`, `.c1`–`.c3` labels and results, and a tooltip key `rumor_odds`.

## Q:
Q: Should a false rumor in choice 2 be revealed to the player once the first combat starts (a "rumor false" badge), or stay hidden until the damage lands?
Q: Does the Heat on choice 3 belong on this event, or should the cost be only the future penalty?
