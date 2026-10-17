<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__20_wheel_solace; status ok; tokens in 5332 cache-write 0 cache-read 32585 out 3029; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, choice 2):** Removed the "stranger's key fob" line, so the text now matches the data. Payment is now 25 Cycles for −2 Heat, so it competes with the wheel's best case. The text reads "SETTLED" only.
- **Issue 2 (BLOCKER, R11):** Rewrote the sub-tick rules per R11 (size 3 = G P G, no WEAK ticks; size 5 = W G P G W). Removed the claim that the extremes are "narrow", which confused quality with width. Quality now matters on slices 1 and 2, with a PERFECT bonus on the jackpot (60 Cycles). Per the triage row, I kept the note that size-3 slices have no WEAK tick.
- **Issue 3 (MAJOR, hazard framing):** Only one flank is hazardous (slice 6 next to slice 1), so the notes now say that. Slice 2 is a gain.
- **Issue 4 (MAJOR, EV):** Stated the EV honestly, computed below. The wheel is slightly Cycle-positive and Heat-negative. The draw is the free nudge and the preview, which let the player aim at the 60/35 slices.
- **Issue 5 (MAJOR, budget):** Now 1 free nudge, then extra nudges cost 3 HP or 1 Heat (player's pick per nudge), max 3 extra. This matches the GDD free-first-nudge rule. The label no longer says "free first nudge" as a separate item.
- **Issue 6 (MAJOR, choice 3):** Added a precise `next_combat_overrides` list and a real upside: ×1.5 Cycle rewards on that fight, so Wipe becomes a gamble on Heat for payoff.
- **Issue 7 (MAJOR, systems):** Tagged `starts_combat` (N16) with a full field list. Wrote out the fallback outcomes.
- **Issue 8 (NIT):** Replaced Q1 (it wraps). The Heat-on-fight rule is now decided: the +1 Heat applies on entry, win or lose.
- **Issue 9 (NIT):** Trimmed the text to 4 sentences.

---

# ev_sol_payment_plan: Payment Plan Roulette

**Mechanic:** WHEEL, corporation solace, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Spin a collections agent's "hardship wheel" to settle a dead man's debt, and decide how much HP or Heat to burn nudging the pointer toward the 60-Cycle jackpot (next to the fight slice) instead of paying or leaving.

## TerminalEventData fields
- id: `ev_sol_payment_plan`
- title: Payment Plan Roulette
- speaker: CORPO
- text: "Your Continuum account is 41 days past due, and Solace Collections would like to help. Select a Hardship Option by spinning the Compassion Wheel. A balance of 180 credits was inherited from this terminal's previous holder, a Mr. Okafor, who is no longer reachable. Smile, subbie."
- corporation_id: `solace`
- min_tier: 1
- dispatch_clue: false
- foreshadows: &""
- weight: 0.8

## Choices

**1. Spin the Compassion Wheel**
- label: "Spin the wheel"
- result_text: "The pointer ticks round and settles. A pleasant voice reads out your terms."
- cycle_cost: 0, hp_cost: 0
- effects: none directly; the outcome comes from the wheel.
- reward: none
- (new) event_wheel: `wheel_payment_plan` (below), N17

**2. Pay the debt**
- label: "Pay 25 Cycles (-2 Heat)"
- result_text: "The balance clears. Okafor's file closes with a stamped SETTLED."
- cycle_cost: 25
- hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount -2
- reward: none

**3. Wipe the ledger**
- label: "Wipe the ledger (+2 Heat)"
- result_text: "The record blanks. Somewhere a collector gets a very confusing morning, and an agent comes looking."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount 2
- reward: none
- (new) next_combat_overrides (N16): {combat_type: next Router fight; extra_enemy: `collections_agent`; reward_multiplier: ×1.5 Cycles; duration: 1 combat}

**4. Walk away**
- label: "Walk on"
- result_text: "The wheel keeps spinning for nobody."
- No costs or effects.

## Event wheel: `wheel_payment_plan`

| # | Slice | size_ticks | Ticks | Outcome |
|---|---|---|---|---|
| 1 | Debt Forgiven | 3 | 0-2 (G P G) | GOOD: +45 Cycles, −1 Heat. PERFECT (tick 1): +60 Cycles, −1 Heat. No WEAK tick exists. |
| 2 | Hardship Grant | 5 | 3-7 (W G P G W) | WEAK +12 · GOOD +25 · PERFECT +35 Cycles |
| 3 | Defer Payment | 6 | 8-13 | Nothing: "Come back next quarter." |
| 4 | Processing Fee | 7 | 14-20 | −20 Cycles (floored at 0) |
| 5 | Late Penalty | 6 | 21-26 | +3 Heat |
| 6 | Referral to Recovery | 3 | 27-29 | Impromptu fight (N16) |

Sum: 3+5+6+7+6+3 = 30.

- **Slice 6 `starts_combat`:** {enemy: `collections_agent`; overrides: none; stake: normal rewards; +1 Heat on entry, win or lose}.
- **Wrap:** the wheel loops, so slice 1 (tick 0) sits next to slice 6 (tick 29). Chasing the jackpot from the left runs past the fight slice. The right flank, slice 2, is a gain.
- **Nudge budget:** 1 free nudge (±1 tick, event wheel only). Extra nudges cost 3 HP or 1 Heat each (player's pick per nudge), max 3 extra, so reach is ±4 ticks at most.
- **RNG note:** the start tick is drawn from the `events` stream at a checkpoint when the page opens, so reloading cannot reroll. Every nudge previews the landing slice, tier and outcome exactly. Undo restores the budget.

## Design notes
- **Honest EV (by tick weight, no nudging):** Cycles ≈ (2×45 + 1×60 + 2×25 + 1×35 + 1×12 + 2×12... computed simply: slice 1 = 3 ticks avg 50, slice 2 = 5 ticks avg 25, slice 4 = 7×(−20)) = (150 + 125 − 140)/30 ≈ +4.5 Cycles. Heat ≈ (−3 + 18 + 3)/30 ≈ +0.6, plus the fight tail. An unaimed spin is roughly neutral, so Walk away is a fair rival. The wheel pays only when you use the free nudge and the preview to reach slices 1 or 2.
- **No dominant option:** Pay is a sure −25 Cycles and −2 Heat. Wipe risks +2 Heat for a ×1.5 Cycle fight. The wheel gives up to +60, but a bad start can cost HP, Heat or a fight.
- **Economy:** typical Terminal rewards are 25-30 Cycles. The wheel's best case is double that, and its worst (fight plus Heat) is a mild ambush.
- **Interactions:** the Referral fight uses standard combat. Scrubber and Cold Exit are unaffected. Distinct from Billing Loop and Clause 44.
- **Text keys:** `ev_sol_payment_plan.title`, `.text`, `.wheel.slice_1..6`, `.nudge_hp`, `.nudge_heat`, `.paid`, `.walk`.
- **Fallback without N17 (data-only):** replace choice 1 with a previewed odds choice: 40 % +25 Cycles, 40 % nothing, 20 % +3 Heat. No fight, no nudge economy.

## Q:
Q: Should the free nudge be usable only before the wheel is revealed (a blind aim) or after, as the previewed design assumes?
Q: Is Heat the right second-nudge currency given the +3 Heat Late Penalty slice, or should Cycles also be allowed once the player has Cycles to spare?
