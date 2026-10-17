<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__24_wheel_rebel_cell; status ok; tokens in 6439 cache-write 0 cache-read 32007 out 2318; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_rc_witness_stand: The Witness Stand

**Mechanic:** WHEEL, corporation rebel_cell, min_tier 2, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** A burned-out ex-subbie will testify against the Cell's old handler, but the wheel decides what she remembers. Do you pay to nudge her memory toward the truth, or take whatever comes?

## TerminalEventData fields
- id: `ev_rc_witness_stand`
- title: The Witness Stand
- speaker: STREET_MERC
- text: "A woman sits alone in a dead tribunal feed, a mic bolted to her chair. She was a bricked subbie once, and one night she watched a Cell runner walk out of a corp tower with a data spike and no face. Nobody ever asked her to talk. The feed offers a recall wheel: six fragments of that night, and you can lean on her memory, but every push leaves a mark on the record. She smiles like she already knows which fragment you're hoping for."
- corporation_id: `rebel_cell`
- min_tier: 2
- dispatch_clue: false
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. "Run the recall wheel"
- label: Run the recall wheel (free first nudge)
- result_text: "She closes her eyes. The wheel turns, and what she saw is what you get."
- cycle_cost: 0
- hp_cost: 0
- effects: none directly; the outcome comes from the wheel slice
- reward: none directly
- (new) event_wheel: `ew_rc_witness` (below)
- (new) starts_combat / combat_overrides / map_edits: none

### 2. "Suppress the testimony (-2 Heat)"
- label: Cut the feed (-2 Heat, 10 Cycles)
- result_text: "You wipe the stand. She doesn't object. 'Nobody listens anyway,' she says."
- cycle_cost: 10
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount -2
- reward: none

### 3. "Take her place on the stand"
- label: Testify yourself (-8 HP)
- result_text: "You tell the empty room what you've done. The feed logs it. Something in the Cell's records changes."
- cycle_cost: 0
- hp_cost: 8
- effects: GAIN_SCHEMATICS, target CAMPAIGN, amount 6
- reward: none
- (new) next_combat_overrides: next fight only, enemy `echo_process` gets `hp_by_tier` x0.8 (it has "heard your confession")

## Event wheel: `ew_rc_witness`
Six fragments, uneven sizes (sum 30). The starting pointer tick is drawn from the `events` RNG stream at a checkpoint, so rewinding cannot reroll it. Preview shows the landing slice before commit.

| # | Slice | size_ticks | Outcome |
|---|---|---|---|
| 1 | The Face | 3 | She names a Daemon-carrier: reward = random Daemon (`events` stream), +3 Heat (someone heard) |
| 2 | The Spike | 6 | Reward: Firmware (common), no cost |
| 3 | The Route | 6 | GAIN_CYCLES +35 |
| 4 | Blank | 7 | Nothing; "she can't recall." |
| 5 | False Memory | 5 | Starts combat with `loyalty_test`, normal rewards, +10 Cycles bonus (she lied or was fed it) |
| 6 | The Echo | 3 | Heat -6, but HP -6 (the testimony hurts the one who hears it) |

Ticks sum: 3+6+6+7+5+3 = 30.
- Quality note: a 3-tick slice has a Perfect at its center tick only; Slice 1 and Slice 6 are the narrow, high-impact ones.
- **Nudge budget:** 1 free nudge, ±1 tick, OUTER ring.
- **Extra nudge cost:** 1 per extra nudge, paid in Cycles (8 each), or 2 HP, or +1 Heat (player chooses at nudge time). Maximum 4 total nudges.
- **Resistance:** none. The wheel can't be flipped or respun.

## Design notes
- **Why it's interesting:** The wheel shows everything up front, and the pointer's position decides what you'd have to pay to reach a better slice. Blank is the largest slice at 7 ticks, so the default outcome is a shrug, and good outcomes need nudges. Slice 1 (+Daemon) and Slice 6 (-6 Heat) are narrow targets, so you pay to hit them precisely.
- **No dominant option:** Choice 2 is a safe, small Heat sink for 10 Cycles. Choice 3 trades 8 HP for 6 Schematics (about a quarter of a typical Rack's worth) and a softer next fight, which is cheap in a short run but ruinous if you're already low. Choice 1 has the highest ceiling (a Daemon) and a real downside (Slice 5's fight, Slice 1 and 6 costs).
- **Economy:** Expected value of the wheel by tick share: Daemon 10 %, Firmware 20 %, 35 Cycles 20 %, nothing 23 %, fight 17 %, Heat/HP trade 10 %. Mean is roughly 15 Cycles-equivalent before nudge costs, below a Rack but with a spike. The 4-nudge cap prevents buying certainty.
- **Interactions:** Rigger's free nudge and the Linked Bus Daemon don't apply (event wheel, not a combat wheel). Clean Signal / Cold Exit are unaffected. Choice 3's HP loss counts as event damage, not combat.
- **Tone:** the Cell turned judge, the witness as the Cell's own unresolved debt. A memory you steer is a memory you've corrupted.
- **Text keys needed:** `ev_rc_witness_stand.title/text`, three choice labels and results, six slice names and flavor lines, nudge-payment prompt ("Cycles / HP / Heat").
- **Dependencies:** N17 (event wheel), N16 (`next_combat_overrides`, `starts_combat`), N12 optional (variable slice sizes; fallback: six 5-tick slices, with Slice 1 and 6 no longer narrow). If N17 is absent, Choice 1 falls back to a single deterministic reward (Firmware) from a checkpointed RNG roll.

## Q:
- Q: Should extra-nudge payment be the player's choice of currency each time, or fixed per event?
- Q: Does Slice 5's fight count as a normal Router fight for Heat and rewards?
