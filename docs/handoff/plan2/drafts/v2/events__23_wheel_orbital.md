<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__23_wheel_orbital; status ok; tokens in 5531 cache-write 0 cache-read 32585 out 3193; cost $0.025. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1

- **Issue 1 (BLOCKER, 8-tick Flare-Out):** Flare-Out is now 7 ticks with the R11 default map W W G P G W W. The 8-tick slice and its Perfect-less map are gone. Sizes are re-added below.
- **Issue 2 (BLOCKER, Dead Sky narrow dud):** Dead Sky is now 4 ticks (W G G W, no Perfect). A dud should not be a precision target. Narrowness is now reserved for good outcomes: Clean Burn (3, Perfect) is the only narrow-and-valuable slice. The "narrow aim" claim is rewritten to say that.
- **Issue 3 (MAJOR, dominance, reach):** Extra nudges are now 5 HP each, max 2, so total reach is 3 ticks. Choice 1 and the free nudge are restructured (see Issue 6). Telemetry Spike is made a real tradeoff (+25 Cycles, +5 Heat), and a Heat rider also lands on WEAK reads. I added an explicit break-even line.
- **Issue 4 (MAJOR, payouts):** Clean Burn is +30 Cycles (Perfect 60). Perfect doubling now applies only to Clean Burn and Flare-Out; it is removed from penalty slices. The Misfire Cycles reward is gone, replaced by a fixed −10 Cycle cost. The notes are rewritten against the 25–30 Cycle event norm, and the "peak" wording is fixed.
- **Issue 5 (MAJOR, CORRUPTED duration):** Added `next_combat_overrides` and the N16 tag. The fallback is hp_cost 6 on Misfire.
- **Issue 6 (MAJOR, choice 1 is just a worse choice 2):** Choice 1 is now "Let it run": the pointer is revealed only after you commit and no nudges are allowed. It is a true gamble with no nudge and no cost. Choice 2 reveals the pointer and gives 1 free nudge plus 2 paid ones.
- **Issue 7 (NIT, determinism wording):** Condensed to one statement.
- **Issue 8 (NIT, spelling):** "an oil drum".
- **Issue 9 / Q:** Kept the HP vs Cycles question. The critic's free-nudge question is answered: choice 2 has 1 free nudge, because a wheel with all-paid nudges would read as a pure tax.
- **Critic "Keep" items:** kept varied sizes summing to 30, the Heat-on-telemetry theme, and preview/undo until confirm with a checkpointed `events` stream.

# ev_orb_stuck_thruster: Stuck Thruster

**Mechanic:** WHEEL, corporation orbital, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** Gamble blind on a looping thruster's fire sequence, pay HP to steer it toward a payout, or pay Cycles to kill it safely.

## TerminalEventData fields
- id: `ev_orb_stuck_thruster`
- title: Stuck Thruster
- speaker: STREET_MERC
- text: "A rooftop attitude thruster the size of an oil drum is cycling its firing sequence on a bad relay. Every burn rattles the Terminal housing and lights the alley blue. The panel shows a six-step dial, and the arrow is moving. Whatever step it stops on is what the Orbital Commons thinks the satellite wants. Lean on it too hard and you eat the exhaust."
- corporation_id: `orbital`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Let it run (blind)**
- label: "Step back and let it fire"
- result_text: "You watch the arrow slow. Whatever it picks, the alley remembers."
- cycle_cost: 0, hp_cost: 0
- effects: the wheel result applies
- reward: per slice
- (new) event_wheel: Thruster Dial (N17), pointer hidden until confirm, nudge budget 0

**2. Steer the relay**
- label: "Pry the panel and steer it (1 free nudge; 2 more cost 5 HP each)"
- result_text: "You wedge a screwdriver into the relay and lean on the sequence. The exhaust scorches your sleeve each time."
- cycle_cost: 0, hp_cost: 0 (paid per extra nudge)
- effects: the wheel result applies
- (new) event_wheel: Thruster Dial, pointer visible, 1 free nudge, up to 2 extra at 5 HP each (max 10 HP)

**3. Kill the burn**
- label: "Cut the fuel line (10 Cycles, −2 Heat)"
- result_text: "The thruster coughs and dies. Some warranty clerk will blame the wrong subcontractor."
- cycle_cost: 10, hp_cost: 0
- effects: MODIFY_HEAT, CAMPAIGN, amount −2
- reward: none

## Event wheel
**Thruster Dial** (N17, with N12 for variable sizes). The start tick comes from the `events` RNG stream, checkpointed when the wheel opens. Nudges are ±1 tick, previewed and undoable until confirm.

| # | Slice | size_ticks | Tick map | Outcome |
|---|---|---|---|---|
| 1 | Clean Burn | 3 | G P G | GAIN_CYCLES +30 (CAMPAIGN) |
| 2 | Salvaged Nozzle | 4 | W G G W | Reward: common Firmware; on WEAK, 15 Cycles instead |
| 3 | Flare-Out | 7 | W W G P G W W | HEAL +8 HP (SELF) |
| 4 | Misfire | 7 | W W G P G W W | −10 Cycles; (new) next_combat_overrides: CORRUPTED on 1 RANDOM_NON_NULL slice of your wheel |
| 5 | Telemetry Spike | 5 | W G P G W | GAIN_CYCLES +25; MODIFY_HEAT +5 (CAMPAIGN) |
| 6 | Dead Sky | 4 | W G G W | Nothing; the thruster powers down |

- Sizes: 3+4+7+7+5+4 = 30.
- **Quality:** PERFECT doubles Clean Burn (+60 Cycles) and Flare-Out (+16 HP). GOOD is 1.0×. WEAK is 0.5×, rounded down, on Cycles and HP only. The Heat, corruption and Cycle-loss riders always stay at full strength.
- **Nudges:** choice 1 has none. Choice 2 has 1 free plus 2 extra at 5 HP, so reach is 3 ticks.
- **Determinism:** one checkpointed `events` draw sets the start tick. Everything after is deterministic, and the preview equals the result.

## Design notes
- **Blind vs steered:** Choice 1 is a pure gamble. By tick coverage, the odds are about 23% to land a bad slice (Misfire 7/30, Telemetry Spike is mixed). Positive-and-clean slices (Clean Burn, Nozzle, Flare-Out) cover 14/30. Choice 2 reaches most targets at ≤10 HP, but Clean Burn is only 3 ticks wide, so many starts cannot reach it even with 3 ticks of reach.
- **Choice 3 break-even:** −10 Cycles for −2 Heat is a safe, fixed trade. Steering to Clean Burn earns +30 for at most 10 HP, a clear win when reachable. Misfire (−10 Cycles plus a RAM tax) and Telemetry Spike (+25 Cycles, +5 Heat) keep the dial from being positive everywhere, and Dead Sky is a pure miss.
- **Aim targets:** only Clean Burn is narrow and valuable. Dead Sky is a forgiving dud, so spending nudges to avoid it is a real HP-for-Cycles decision.
- **Economy:** typical events pay 25–30 Cycles. Clean Burn matches that at GOOD and exceeds it only on a rare Perfect (3-tick window, 1 tick of exact center).
- **Dependencies:** N17 (EventWheelData page, `events` RNG at a checkpoint); N12 (sizes 3, 4, 5, 7). Fallback without N12: six 5-tick slices, losing the shaped difficulty. N16 (`next_combat_overrides`) for the CORRUPTED rider; fallback is `hp_cost` 6 on Misfire. R9 makes CORRUPTED a 2× RAM tax.
- **Text keys:** `ev_orb_stuck_thruster.title`, `.text`, three choice labels, six slice results, and the prompt "Steer it (−5 HP)".

## Q:
- Should the operative's class hooks (Rigger's free nudge, Ghost's resistance bypass) add to the wheel's nudge budget, or stay out of events?
- Is HP the right extra-nudge currency for Orbital, or should it be Heat or Cycles to differ from Halcyon's HP-flavored costs?
