<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__21_wheel_meridian; status ok; tokens in 6436 cache-write 0 cache-read 32007 out 2202; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_mer_favor_slot: Favor Slot

**Mechanic:** WHEEL, corporation meridian, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Spend a favor from a dead dispatcher on a rigged sort wheel, then decide how much Heat or HP to pay to steer it toward the outcome you need.

## TerminalEventData fields
- id: `ev_mer_favor_slot`
- title: Favor Slot
- speaker: STREET_MERC (1)
- text: "Hub sorter, third shift, nobody home. A dispatcher named Okafor left a note taped to the scanner: 'You moved my sister's crate once. This slot is yours, one pull, no questions.' The sorter wheel is a manual override, the kind Meridian swears it removed. Every bin on it is a different kind of trouble. Okafor can't collect on the favor anymore, so you owe nobody and everybody."
- corporation_id: `meridian`
- min_tier: 2
- dispatch_clue: false
- foreshadows: ``
- weight: 0.8

## Choices

**1. Pull the lever (use the favor)**
- label: "Pull the lever (3 free nudges)"
- result_text: "The sorter spins, clicks, and drops your parcel where it drops it."
- cycle_cost: 0, hp_cost: 0
- effects: none directly; resolves the event wheel.
- reward: none directly (see wheel).
- (new) event_wheel: `ew_favor_slot`, nudge budget 3 free, extra nudges cost 4 HP or +2 Heat (player picks per nudge).
- (new) starts_combat / combat_overrides / map_edits: none on the choice. Slices 5 and 6 carry their own.

**2. Sell the favor to a broker (+35 Cycles)**
- label: "Sell the slot (+35 Cycles)"
- result_text: "A fixer pays cash for a dead man's name on a ticket. The cash is clean. The conscience is not."
- cycle_cost: 0, hp_cost: 0
- effects: GAIN_CYCLES, CAMPAIGN, amount 35
- reward: none
- (new) none

**3. Burn the note (−1 Heat)**
- label: "Burn the note"
- result_text: "No favor on the books means no thread back to you."
- effects: MODIFY_HEAT, CAMPAIGN, amount −1
- reward: none
- (new) none

## Event wheel: `ew_favor_slot`
Six bins, sizes sum to 30. A wheel pointer starts on tick 0. The start position comes from the `events` RNG stream (checkpointed before the first nudge; undo can't reroll it). Nudge ±1 tick; the pointer reads the slice it ends on, and slice boundaries follow N12 variable sizes (the fallback is six 5-tick slices).

| # | Bin | size_ticks | Outcome |
|---|---|---|---|
| 1 | Express Crate | 4 | GAIN_CYCLES CAMPAIGN +50 |
| 2 | Spare Parts | 6 | reward: random Firmware (common pool, `events` stream at the checkpoint) |
| 3 | Dead Letter | 7 | Nothing. "Returned to sender." |
| 4 | Customs Hold | 5 | MODIFY_HEAT +4, GAIN_CYCLES +20 |
| 5 | Audit Flag | 4 | (new) starts_combat: `customs_scanner`, stake: win = +30 Cycles. Combat override: enemy starts with RESISTANCE +1 (weight). Flee is not possible. |
| 6 | Hot Freight | 4 | reward: random uncommon Daemon, plus next fight (new) `next_combat_overrides`: enemy damage +25 % (duration: the next 1 combat). |

Sizes: 4+6+7+5+4+4 = 30. Slice 3, the largest, is the dud, so a blind pull most often lands there. Slice 1, the best Cycles, is a narrow target. The pointer starts on tick 0 (the center of slice 1), so the roll displaces it and the nudges steer it. The preview shows the destination slice for any pending nudge, and every action is undoable until the final commit.

Extra nudges beyond 3: 4 HP or +2 Heat each, capped at 5 extra. The HP cost uses `hp_cost` semantics; the Heat cost uses MODIFY_HEAT.

## Design notes
- **No dominant option.** The wheel's expected value is about 28 Cycles equivalent plus a Firmware chance, which beats the 35-Cycle sale only with steering. Steering costs HP or Heat, and the Heat risk (slice 4) is partly self-inflicted. Burning the note is the safe, Heat-lowering route for a run that is already hot.
- **Economy placeholders:** 50 Cycles is about one Mainframe purchase; 35 is a guaranteed shop-tier price. Hot Freight's Daemon is the jackpot but sets up a damage-boosted fight, a real cost on a low-HP operative.
- **Weighted bins:** the two bad bins (Audit Flag, Hot Freight) are adjacent to Customs Hold, so over-nudging from a rough start can walk the player into trouble. Slice 3 sits between 2 and 4 as a safe buffer.
- **Interactions:** Scrubber and Cold Exit-style Heat Daemons make slice 4 cheaper. Low-HP runs lean on Heat payment, hot runs on HP.
- **Dependencies:** N17 (the wheel page, `events` RNG checkpoint), N16 (`starts_combat`, `next_combat_overrides`), N12 optional. **Data-only fallback:** choice 1 becomes a fixed three-choice list (Cycles / Firmware with +Heat / combat), and choices 2 and 3 work as written.
- **Text keys:** `ev_mer_favor_slot.title/.text`, six bin labels, `.nudge_extra_hp`, `.nudge_extra_heat`, `.pull_result.<1-6>`.

## Q:
- Q: Should extra-nudge costs mix (HP or Heat per nudge) or be one fixed currency per event?
- Q: Does the Audit Flag fight win count as clearing the event wheel reward as well, or does the Cycle stake replace it?
