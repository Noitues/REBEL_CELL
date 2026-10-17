<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__25_wheel_aurelian; status ok; tokens in 5710 cache-write 0 cache-read 32585 out 5893; cost $0.038. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, EV arithmetic):** Replaced the EV line with a per-slice table in Cycle-equivalents (1 Heat = 10, 1 HP = 3). Null Clause is included and each slice uses its real tick share. Unsteered EV ≈ +5.3; the bribe variant ≈ +6.5 before its cost. Sizes re-added: both layouts sum to 30.
- **Issue 2 (BLOCKER, tier riders):** Added a Tier riders column using the R11 default maps. Bread Dole is 4 ticks (W G G W), so WEAK pays ×0.5. Patron's Favor is 3 ticks (G P G) and its Perfect tick adds +10 Cycles. The false "Perfect-only" claim is removed, since Favor fires on any tick.
- **Issue 3 (BLOCKER, forced elite):** The Arena Bout is always waivable for 20 Cycles; if the player has less, they pay all they have. Win and lose stakes are explicit. "Flee" is deleted because the GDD has no flee mechanic. `starts_combat` is tagged N16.
- **Issue 4 (MAJOR, N# tags):** Tagged N17, N16, and N12 (sizes, optional for N17). Replaced the vague fallback with three fixed offers.
- **Issue 5 (MAJOR, nudge cost):** Extra nudges cost 3 HP or 1 Heat each, max 3, chosen per nudge by a prompt. Heat applies at event end, so no mid-event threshold fires (this answers the old Heat-timing Q). The forge is cut to +25 Cycles and +2 Heat (net +5, about the unsteered EV), so steering can beat it.
- **Issue 6 (MAJOR, bribe):** Budget stays 2 and the cost drops to 25 Cycles, per the fix. The EV table shows it is a poor deal; I keep it as a fear-of-the-fight option and say so honestly.
- **Issue 7 (NIT):** Replaced "DRAIN" with an HP-loss field. Noted "common Firmware" and "uncommon card" as unscaled placeholders.
- **Kept:** the uneven six-slice wheel, the 3-tick Favor steering target, the `events` RNG with checkpoint and undo, and the forge as a safe baseline.

# ev_aur_lanista_contract: The Lanista's Contract

**Mechanic:** WHEEL, corporation aurelian, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Spin a clause wheel and steer it with a few paid nudges, bribe the clerk to shrink the fight, forge a safe payout, or walk.

## TerminalEventData fields
- id: `ev_aur_lanista_contract`
- title: The Lanista's Contract
- speaker: CORPO
- text: "A Lanista in a gold-thread suit waits behind a velvet rope, holding a slate. 'The Patron's compliments. Sign, and the Concord will find you work, glory and bread.' Six clauses glow on the slate, each marked *Terms apply*. The signature field is already warm, as if someone just lifted a thumb from it. 'The Verdict picks the clause,' the Lanista smiles. 'You merely witness.'"
- corporation_id: `aurelian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Sign the slate (N17)**
- label: "Sign and spin the clause wheel"
- result_text: "The wheel turns under the Lanista's thumbnail. Whatever lands, the ink has already dried."
- cycle_cost 0, hp_cost 0, effects none, reward none
- (new) event_wheel: base wheel below, nudge budget 2 free.

**2. Bribe the clerk**
- label: "Pay the clerk to re-weight the wheel (25 Cycles)"
- result_text: "The clerk shrinks the Arena wedge and fattens the Bread. Nobody looks at the slate."
- cycle_cost 25, hp_cost 0, effects none, reward none
- (new) event_wheel: same wheel with `size_ticks` override (Arena 6 → 3, Bread 4 → 7; sum still 30). Nudge budget stays 2.

**3. Forge the seal**
- label: "Counter-sign with a forged seal"
- result_text: "The seal passes. Somewhere a ledger flags a duplicate patron."
- cycle_cost 0, hp_cost 0
- effects: GAIN_CYCLES CAMPAIGN 25; MODIFY_HEAT CAMPAIGN +2 (a MINOR threshold applies as usual)
- reward: none

**4. Decline**
- label: "Decline the contract"
- result_text: "'Terms apply regardless,' the Lanista says mildly. You walk on."
- No costs, no effects.

## Event wheel (N17; sizes need N12, optional for N17)
One pointer on the OUTER ring. The start tick comes from the `events` RNG stream.

| # | Slice | size_ticks | Outcome | Tier riders (R11 map) |
|---|---|---|---|---|
| 1 | Bread Dole | 4 | GAIN_CYCLES CAMPAIGN +40 | W G G W: WEAK pays ×0.5 (+20) |
| 2 | Circus Ticket | 5 | Reward: pick 1 of 3 uncommon cards | tier-independent |
| 3 | Arena Bout | 6 | (new, N16) `starts_combat`: `station_commander`, no overrides. Win: common Firmware + 35 Cycles. Lose: normal operative death (GDD 4.2). | tier-independent |
| 4 | Fine Print | 7 | hp_cost 8 (slice HP-loss field); MODIFY_HEAT CAMPAIGN +3 | tier-independent |
| 5 | Patron's Favor | 3 | HEAL SELF 12; MODIFY_HEAT CAMPAIGN −2 | G P G: the Perfect tick adds GAIN_CYCLES +10 |
| 6 | Null Clause | 5 | Nothing: "Void for lack of consideration." | n/a |

Sizes: 4+5+6+7+3+5 = 30. Bribed layout: 7+5+3+7+3+5 = 30.
- **Arena waiver:** when the Arena Bout resolves, the player may pay 20 Cycles (all they have, if fewer) to convert it to Null Clause. The fight is never forced. Because the enemy is a fixed id, it needs no RNG.
- **Nudge budget:** 2 free nudges of ±1 tick. Extra nudges cost 3 HP or 1 Heat each, chosen per nudge by a prompt, max 3 extra. Heat spent is applied at event end, so no threshold fires mid-event.
- **Determinism:** the start tick is drawn once from `events`, checkpointed when the wheel opens. Nudges are staged and undo-clean. The preview shows the slice and tier under the pointer, so preview equals result.

## Design notes
- **Unsteered EV per spin** (Cycle-equivalents; 1 Heat = 10, 1 HP = 3; tick-weighted):

| Slice | Value |
|---|---|
| Bread | 4/30 × 30 average (two WEAK ticks) = +4.0 |
| Circus | 5/30 × 30 = +5.0 |
| Arena | 6/30 × (60 − 45 risk) = +3.0 |
| Fine Print | 7/30 × (−24 − 30) = −12.6 |
| Favor | 3/30 × 56 = +5.6, plus the Perfect tick 1/30 × 10 = +0.3 |
| Null | 0 |

  Total ≈ **+5.3**. Waiving a landed Arena costs 20, so it only makes sense at low HP.
- **Bribe:** Bread 7 ticks (four WEAK) = 200/30 = +6.7, Arena 3/30 × 15 = +1.5, Circus +5.0, Fine Print −12.6, Favor +5.9. Total ≈ +6.5, a +1.2 gain for 25 Cycles, so a bad deal on EV. It buys only fewer fight outcomes.
- **Forge:** +25 Cycles − 20 (2 Heat) = +5 flat, about the unsteered EV with zero variance. A skilled steerer beats it: 5 nudges toward Favor (3 HP each) are worth about +56 against a −54 danger slice.
- **Dominance check:** each option wins for some player. A low-HP player forges or declines, a high-HP player with Heat sinks spins, and a rich player facing a bad start tick bribes.
- **Interactions:** Clean Signal and Scrubber offset the Heat costs.
- **Text keys:** `ev_aur_lanista_contract.title/text`, `wheel.bread_dole` … `wheel.null_clause`, `wheel.extra_nudge_hp`, `wheel.extra_nudge_heat`, `wheel.waive_arena`, "Terms apply" footer.
- **Fallback without N17/N16:** three fixed offers (Bread +25 Cycles; one uncommon card; a gamble that starts the fixed `station_commander` fight for common Firmware + 35 Cycles). It is data-only, but the steering decision is lost.

## Q:
- Q: If the player holds under 20 Cycles, is paying "all they have" to waive the Arena fair, or should low-Cycle players get an HP-based waiver instead?
- Q: Is a per-nudge HP-or-Heat prompt acceptable mouse/keyboard UI, or should the player pick one currency when the wheel opens?
