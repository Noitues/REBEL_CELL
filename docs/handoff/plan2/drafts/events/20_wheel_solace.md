<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__20_wheel_solace; status ok; tokens in 6435 cache-write 0 cache-read 32007 out 2154; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_sol_payment_plan: Payment Plan Roulette

**Mechanic:** WHEEL, corporation solace, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Spin a collections agent's "hardship wheel" to settle a dead man's debt, and decide how much HP or Heat to burn nudging the pointer toward the good slices.

## TerminalEventData fields
- id: `ev_sol_payment_plan`
- title: Payment Plan Roulette
- speaker: CORPO (3)
- text: "Your Continuum account is 41 days past due, and Solace Collections would like to help. Select a Hardship Option by spinning the Compassion Wheel. Outcomes are final, except where nudged. A balance of 180 credits was inherited from the previous holder of this terminal, a Mr. Okafor, who is no longer reachable. Terms apply. Smile, subbie."
- corporation_id: `solace`
- min_tier: 1
- dispatch_clue: false
- foreshadows: &""
- weight: 0.8

## Choices

**1. Spin the Compassion Wheel**
- label: "Spin the wheel (free first nudge)"
- result_text: "The pointer ticks round and settles. A pleasant voice reads out your terms."
- cycle_cost: 0, hp_cost: 0
- effects: none directly; outcome comes from the wheel.
- reward: none
- (new) event_wheel: `wheel_payment_plan` (below)

**2. Pay the debt in full**
- label: "Pay the 180 (-40 Cycles)"
- result_text: "The balance clears. Okafor's file closes with a stamped 'SETTLED'. You get a receipt and a stranger's key fob."
- cycle_cost: 40
- hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount -1
- reward: none
- (new) none

**3. Wipe the ledger**
- label: "Wipe the ledger (+2 Heat)"
- result_text: "The record burps and blanks. Somewhere a collector gets a very confusing morning, and a Collections Agent arrives early."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount 2
- reward: none
- (new) next_combat_overrides: next Router fight only; enemy `collections_agent` added as an extra enemy, stake: +1 start-of-fight Block on it; duration 1 combat.

**4. Walk away**
- label: "Walk on"
- result_text: "The wheel keeps spinning for nobody."
- No costs or effects.

## Event wheel: `wheel_payment_plan`
Six uneven slices; pointer starts on a seeded tick (see RNG note).

| # | Slice | size_ticks | Outcome |
|---|---|---|---|
| 1 | Debt Forgiven | 3 | +45 Cycles (GAIN_CYCLES 45), -1 Heat |
| 2 | Hardship Grant | 5 | +25 Cycles |
| 3 | Defer Payment | 6 | Nothing; "Come back next quarter." |
| 4 | Processing Fee | 7 | -20 Cycles (clamped at 0) |
| 5 | Late Penalty | 6 | +3 Heat (MODIFY_HEAT 3) |
| 6 | Referral to Recovery | 3 | Impromptu fight: (new) starts_combat `collections_agent`, normal rewards, +1 Heat on entry |

Sum: 3+5+6+7+6+3 = 30.

Sub-tick quality (R11): size 3 is G P G, so a pointer at the exact centre of Debt Forgiven or Referral reads PERFECT. Both extremes are narrow and risky to chase. Quality only matters for slice 1 and 2: GOOD or better pays in full; WEAK on Hardship Grant pays 12.

- **Nudge budget:** 2 free nudges, ±1 tick each, on the wheel only.
- **Extra nudge cost:** 3 HP each, or 1 Heat (player picks per nudge), up to 4 extra. Cycles never pay, because Solace already took them.
- **Deterministic RNG note:** start tick drawn from the `events` stream at a checkpoint when the page opens, so quitting and reloading cannot reroll. Each nudge previews the landing slice, tier and outcome exactly; Undo restores the budget.

## Design notes
- **Why it's interesting:** Pay is a safe -40 Cycles for -1 Heat. Wipe trades +2 Heat plus a tougher next fight for a free exit. The wheel has positive EV (about +9 Cycles by slice weight, ignoring the fight tail) but includes two hazard slices flanking the jackpot: Debt Forgiven is adjacent to Referral on the wrap (tick 0 / 29), so over-nudging for the jackpot can tip you into a fight. A cautious player can pay 3 HP to shift one tick off a hazard.
- **Economy:** Typical Terminal rewards are 25–30 Cycles (Billing Loop +30 with 3 Heat). Max win here is 45 and the worst case is a Collections fight plus a Heat, comparable to a mild ambush. Paying 40 buys safety, about one Mainframe item.
- **Interactions:** Referral fight uses standard combat; if HP is low the player may buy nudges with Heat instead. Scrubber and Cold Exit are unaffected. Boosts the Solace "debt" voice without repeating Billing Loop or Clause 44.
- **Text keys:** `ev_sol_payment_plan.title`, `.text`, `.wheel.slice_1..6`, `.nudge_hp`, `.nudge_heat`, `.paid`, `.walk`.
- **Fallback without N17:** replace choice 1 with a flat 3-outcome choice and drop the nudge economy. This loses the central decision.

## Q:
Q: Should the nudge be allowed to wrap past slice 6 into slice 1 (current design), or should the wheel be non-looping like a real shop wheel?
Q: Does the Referral fight's Heat apply even if the player wins, or only on a loss?
