<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__25_wheel_aurelian; status ok; tokens in 6437 cache-write 0 cache-read 32007 out 2420; cost $0.022. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_aur_lanista_contract: The Lanista's Contract

**Mechanic:** WHEEL, corporation aurelian, min_tier 2, weight 0.8, dispatch_clue false, foreshadows none
**One-line decision:** Sign a fight-contract whose terms are decided by a spinning clause wheel: take the free nudge, pay to bend the odds, or refuse.

## TerminalEventData fields
- id: `ev_aur_lanista_contract`
- title: The Lanista's Contract
- speaker: CORPO
- text: "A Lanista in a gold-thread suit waits behind a velvet rope, holding a slate. 'Patron's compliments. Sign, and the Concord will find you work, glory, and bread.' The slate lists six clauses, each marked *Terms apply*. The signature field is already warm, as if someone else just lifted a thumb from it. 'The VERDICT decides the clause,' the Lanista smiles. 'You merely witness.'"
- corporation_id: `aurelian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Sign and spin the Verdict (event wheel)**
- label: "Sign the slate (spin the clause wheel)"
- result_text: "The wheel turns under the Lanista's thumbnail. Whatever lands, the ink has already dried."
- cycle_cost: 0, hp_cost: 0
- effects: none (outcome comes from the wheel)
- reward: none
- (new) event_wheel: see below
- (new) starts_combat: none by the choice itself; the Arena Bout slice does (below)

**2. Bribe the clerk first**
- label: "Pay the clerk to re-weight the wheel (-35 Cycles)"
- result_text: "The clerk shrinks the Arena Bout wedge and widens the Bread. Nobody looks at the slate."
- cycle_cost: 35, hp_cost: 0
- effects: none
- (new) event_wheel: same wheel, `size_ticks` override: Arena Bout 6 → 3, Bread Dole 4 → 7. Nudge budget 1 (not 2).

**3. Counter-sign with a forged seal**
- label: "Forge the seal (+2 Heat), take the Patron's Gift outright"
- result_text: "The forged Concord seal passes. Somewhere a ledger flags a duplicate patron."
- cycle_cost: 0, hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount 2; GAIN_CYCLES, CAMPAIGN, amount 30
- reward: none

**4. Decline**
- label: "Decline the contract"
- result_text: "'Terms apply regardless,' the Lanista says mildly. You walk on."
- No costs, no effects.

## Event wheel
Wheel is 30 ticks, 6 slices, uneven. One pointer, default tick set by the `events` RNG stream.

| # | Slice | size_ticks | Outcome (effects) |
|---|---|---|---|
| 1 | Bread Dole | 4 | GAIN_CYCLES CAMPAIGN +40 |
| 2 | Circus Ticket | 5 | Reward: one uncommon card (offered, pick 1 of 3) |
| 3 | Arena Bout | 6 | (new) starts_combat: `station_commander` (elite), `combat_overrides`: none. Stake: win = Firmware reward (common) + 35 Cycles; flee/lose = standard death rules. |
| 4 | Fine Print | 7 | DRAIN: hp_cost 8 (via the event's HP loss) and MODIFY_HEAT CAMPAIGN +3 |
| 5 | Patron's Favor | 3 | HEAL SELF amount 12; MODIFY_HEAT CAMPAIGN -2 |
| 6 | Null Clause | 5 | Nothing. "Void for lack of consideration." |

- **Nudge budget:** 2 free nudges of ±1 tick (ring OUTER). Extra nudges cost 6 HP each (hp_cost) or, if the player prefers, 1 Heat (player picks; default is HP). Max 5 extra.
- **Sub-tick quality (R11):** the outcome resolves on the slice under the pointer. Perfect centre of Patron's Favor (3 ticks) grants +10 Cycles; WEAK edges on Bread Dole pay only 50 % (+20).
- **Determinism:** the starting pointer tick comes from the named `events` RNG stream, checkpointed when the wheel opens. Nudges are staged, the preview shows the slice and tier under the pointer, and undo returns to the checkpoint, so preview = result. Arena Bout's enemy is fixed, not drawn.

## Design notes
- **Why it's interesting:** Arena Bout is the largest slice (6 of 30, 20 %) and the best reward, but it is an elite fight mid-run. Fine Print (7 ticks, 23 %) is the largest and the worst. The player can read the wheel before committing, but each nudge is only ±1 tick, so reaching a distant slice is expensive. Slice sizes create clear steering targets: Patron's Favor is a tiny 3-tick slice with a Perfect-only bonus.
- **Expected values (placeholders; a run earns ~150 Cycles per layer set):** unsteered EV ≈ 20 % × (fight reward 35 + Firmware) + 13 % × 40 + 17 % × card + 10 % × (heal 12) − 23 % × (8 HP + 3 Heat). Roughly +15 Cycles-equivalent with variance. Bribe costs 35 for a ~+8 EV swing, which is not obviously worth it, so it is a real choice. The forged seal is a flat +30 for 2 Heat: safe but dull and slightly inflationary.
- **Anti-dominance:** Declining is free but forfeits the only event in this tier that offers a Firmware via fight. No option dominates: variance-averse players forge, builds with spare HP and Heat sinks gamble, rich players bribe.
- **Interactions:** Clean Signal and Scrubber Daemons offset Heat. Linked Bus is irrelevant. A Rigger's extra RAM does not apply.
- **Text keys:** `ev_aur_lanista_contract.title/text`, per-slice labels (`wheel.bread_dole` … `wheel.null_clause`), `wheel.extra_nudge_hp`, `wheel.extra_nudge_heat`, "Terms apply" footer.
- **Data fallback without N17:** a 4-choice event with fixed outcomes is possible, but the steering decision is lost.

## Q:
- Q: Should Arena Bout allow a "decline the bout" refund (forfeit the wheel result) at −10 Cycles, to prevent forced elites at low HP?
- Q: Does Heat-for-nudge count as a MINOR Heat threshold trigger mid-event, or is it deferred to event end?
