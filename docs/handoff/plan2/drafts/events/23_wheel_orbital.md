<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__23_wheel_orbital; status ok; tokens in 6438 cache-write 0 cache-read 32007 out 2532; cost $0.022. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_orb_stuck_thruster: Stuck Thruster

**Mechanic:** WHEEL, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** A malfunctioning station-keeping thruster is firing on a loop; you can nudge its fire sequence toward a payout. Each extra nudge costs HP from the exhaust, and the worst slices spend Heat.

## TerminalEventData fields
- id: `ev_orb_stuck_thruster`
- title: Stuck Thruster
- speaker: STREET_MERC (1)
- text: "A rooftop attitude thruster the size of a oil drum is cycling its firing sequence on a bad relay. Every burn rattles the Terminal housing and lights the alley blue. The maintenance panel shows a six-step sequence on a spinning dial, and the arrow is moving. Whichever step it lands on is what the Orbital Commons thinks the satellite wants. Tap it too hard and you eat the exhaust."
- corporation_id: `orbital`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Ride the dial (spin once, no extra nudges)**
- label: "Let it fire as is (free nudge only)"
- result_text: "You step back and let the thruster decide. Whatever it picks, the alley remembers."
- cycle_cost: 0, hp_cost: 0
- effects: none directly; the wheel result applies
- reward: none
- (new) event_wheel: the Thruster Dial (below), nudge budget 1 (free), no extra nudges allowed

**2. Fight the relay (nudge for results)**
- label: "Pry the panel and steer it (extra nudges cost 4 HP)"
- result_text: "You wedge a screwdriver into the relay and lean on the sequence. The exhaust scorches your sleeve each time."
- cycle_cost: 0, hp_cost: 0 (paid per extra nudge)
- effects: none directly
- reward: none
- (new) event_wheel: the same Thruster Dial, nudge budget 1 free + up to 3 extra, each extra costs 4 HP

**3. Kill the burn (safe, small)**
- label: "Cut the fuel line (-1 Heat, 10 Cycles)"
- result_text: "The thruster coughs and dies. Some warranty clerk will blame the wrong subcontractor."
- cycle_cost: 10, hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount -1
- reward: none

## Event wheel
**Name:** Thruster Dial. Six slices of varied size (sum 30). The pointer starts at a position chosen from the `events` RNG stream at a checkpoint; nudges move it ±1 tick on the dial and are previewed and undoable until the player confirms.

| # | Slice | size_ticks | Tick map | Outcome |
|---|---|---|---|---|
| 1 | Clean Burn | 3 | G P G | GAIN_CYCLES +45 (CAMPAIGN) |
| 2 | Salvaged Nozzle | 4 | W G G W (no Perfect) | Reward: Firmware (common); on a WEAK read, only 15 Cycles |
| 3 | Flare-Out | 8 | W W G G G G W W | HEAL +8 HP (SELF); ambient warmth from the burn |
| 4 | Misfire | 7 | W W G P G W W | APPLY_STATUS: CORRUPTED on 1 slice of your wheel (RANDOM_NON_NULL) for the next fight; 10 Cycles |
| 5 | Telemetry Spike | 5 | W G P G W | MODIFY_HEAT +4 (CAMPAIGN); GAIN_CYCLES +35 |
| 6 | Dead Sky | 3 | G P G | Nothing; the thruster powers down |

- Sizes total 3+4+8+7+5+3 = 30.
- Outcome quality: a PERFECT landing doubles the slice's numeric payout (Cycles or HP). GOOD reads at 1.0×. WEAK reads at 0.5× (rounded down), and the status and Heat riders stay at full strength. This makes the narrow positive slices hard to hit precisely.
- Nudge budget: 1 free nudge, then up to 3 extra (choice 2 only). Extra nudge cost: 4 HP each.
- Determinism: the starting tick comes from the `events` RNG stream, checkpointed when the wheel opens, so a reload or undo cannot reroll it. Once the pointer is set, every nudge is deterministic and the final slice is shown in the preview before confirming. Quitting mid-event restores the same pointer and nudges used.

## Design notes
- **Dominance check:** Choice 3 is a guaranteed minor gain (−1 Heat, but −10 Cycles). Choice 1 has an expected value above it, but with real variance (a Misfire corrupts your slice going into the next fight). Choice 2 can reach the best slice but spends HP at 4 per nudge, which matters when HP carries between fights. Max cost is 12 HP for a ~45 Cycle payout, about a third of a typical shop buy. That is deliberately tight.
- **Slice weighting:** Dead Sky and Clean Burn are small (3 ticks each), so landing on them takes aim. The big Flare-Out (8 ticks) is the forgiving, low-value outcome. The two risky slices (Misfire 7, Telemetry Spike 5) are wide enough to be common results, so doing nothing is not safe.
- **Economy:** Typical event values are 25–30 Cycles (Abandoned Cache, Billing Loop). The wheel's 45 Cycle peak matches the risk. Telemetry Spike is a Billing Loop-style trade (+35 Cycles, +4 Heat), slightly harsher on Heat.
- **Orbital tone:** the malfunction is a privatized-orbit hardware fault. Heat comes from the Commons noticing unscheduled telemetry.
- **Interactions:** Free-nudge Daemons and Rigger's "free nudge" hook could be reused for the wheel's free nudge (Q below). The CORRUPTED rider reads as a RAM debuff under R9, which makes Misfire hurt next fight.
- **Dependencies:** N17 (EventWheelData page, `events` RNG at a checkpoint), N12 (variable slice sizes) for the 3/4/5/7/8 sizes. Fallback without N12: six 5-tick slices, losing the shaped difficulty. The CORRUPTED status uses existing APPLY_STATUS. Per-slice PERFECT scaling is data-only inside EventWheelData.
- **Text keys needed:** `ev_orb_stuck_thruster.title`, `.text`, a label per choice and result per slice (six wheel results), and the extra-nudge prompt "Steer it (−4 HP)".

## Q:
- Should the operative's own class hooks (Rigger's free nudge, Ghost's resistance bypass) feed the event wheel's nudge budget, or is it a fixed pool of its own?
- Is HP the right extra-nudge currency here, or should Orbital events use Cycles to differ from Halcyon's HP-flavored costs?
