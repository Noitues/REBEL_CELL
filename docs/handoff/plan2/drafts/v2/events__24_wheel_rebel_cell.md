<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__24_wheel_rebel_cell; status ok; tokens in 5376 cache-write 0 cache-read 32585 out 3330; cost $0.025. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, enemy ids):** kept `echo_process` and `loyalty_test`. Both appear in the CONTENT_DESIGN_V2 §4 inventory under REBEL_CELL normals (cell_informant, dead_drop, echo_process, handler_proxy, loyalty_test, mirror_script). `ev_rc_witness_stand` and `ew_rc_witness` are the event's own new content ids.
- **Issue 2 (MAJOR, determinism):** Slice 1 no longer rolls after commit. The Daemon is rolled from the `events` stream when the wheel opens (checkpoint) and shown on the slice. The start pointer tick is rolled at the same checkpoint. Preview equals result.
- **Issue 3 (MAJOR, dominance):**
  - Choice 2 is now −5 Heat for 15 Cycles.
  - Choice 3 is now −8 HP, +4 Schematics, and next-combat `echo_process` ×0.9 HP.
  - Blank is now +10 Cycles, so the default outcome is not a loss.
  - Choice 3 is also gated: it is hidden unless HP is above 20. This answers the critic's Q2 and the ruinous-when-low concern.
- **Issue 4 (MAJOR, arithmetic):** the EV sum is shown below, with placeholder Cycle values.
- **Issue 5 (MAJOR, R11):** stated that quality tiers on event slices are cosmetic and the sub-tick map is not read. "OUTER ring" is dropped.
- **Issue 6 (NIT, currency):** extra nudges cost 8 Cycles, or 2 HP. The Heat option is dropped. Currency is fixed to those two per nudge (the player picks at nudge time).
- **Issue 7 (NIT, clue):** added `dispatch_clue`: true. It fires only if Slice 1 (The Face) lands, and it is in the slice text. The event header carries no clue otherwise.
- **Issue 8 (NIT, combat stake):** Slice 5 now states its stake: a normal Router fight with +10 Cycles bonus and standard Heat (0). Choice 1 lists the combat as a wheel-slice outcome.
- The ruling on rewinding and RNG checkpoints is unchanged. The uneven sizes, the Cell-as-judge tone, the 4-nudge cap and the N17 fallback are kept, as the critic marked them strong.

# ev_rc_witness_stand: The Witness Stand

**Mechanic:** WHEEL, corporation rebel_cell, min_tier 2, weight 0.8, dispatch_clue only via Slice 1, no foreshadows
**One-line decision:** A burned-out ex-subbie will testify about the Cell's old handler, and a wheel decides what she remembers. Do you pay to steer her memory, buy a quiet record, or take the stand yourself?

## TerminalEventData fields
- id: `ev_rc_witness_stand`
- title: The Witness Stand
- speaker: STREET_MERC
- text: "A woman sits alone in a dead tribunal feed, a mic bolted to her chair. She was a bricked subbie once, and one night she watched a Cell runner walk out of a corp tower with a data spike and no face. Nobody ever asked her to talk. The feed offers a recall wheel: six fragments of that night, and you can lean on her memory, but every push costs you. She smiles like she already knows which fragment you're hoping for."
- corporation_id: `rebel_cell`
- min_tier: 2
- dispatch_clue: true (only on Slice 1)
- foreshadows: (empty)
- weight: 0.8

## Choices

### 1. Run the recall wheel
- label: Run the recall wheel (first nudge free)
- result_text: "She closes her eyes. The wheel turns, and what she saw is what you get."
- cycle_cost: 0
- hp_cost: 0
- effects: none directly; the outcome comes from the landing slice
- reward: from the slice
- (new) event_wheel: `ew_rc_witness` (below)
- (new) starts_combat: only through Slice 5 (see the wheel)
- (new) combat_overrides / map_edits: none

### 2. Cut the feed
- label: Cut the feed (15 Cycles, −5 Heat)
- result_text: "You wipe the stand. She doesn't object. 'Nobody listens anyway,' she says."
- cycle_cost: 15
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount −5
- reward: none

### 3. Testify yourself
- label: Testify yourself (−8 HP, +4 Schematics)
- result_text: "You tell the empty room what you've done. The feed logs it. Something in the Cell's records changes."
- cycle_cost: 0
- hp_cost: 8 (hidden unless current HP > 20)
- effects: GAIN_SCHEMATICS, target CAMPAIGN, amount 4
- reward: none
- (new) next_combat_overrides: next fight only, enemy `echo_process` `hp_by_tier` ×0.9 (it heard your confession). Expires after that fight, or at the end of the netrun if none occurs.

## Event wheel: `ew_rc_witness`
Six fragments, uneven sizes. Sizes sum: 3 + 6 + 6 + 7 + 5 + 3 = 30. The start pointer tick and Slice 1's Daemon are both drawn from the `events` RNG stream when the wheel opens, at a checkpoint, so rewinding cannot reroll them. The preview shows the landing slice and its exact outcome (including the named Daemon) before commit.

| # | Slice | size_ticks | Outcome |
|---|---|---|---|
| 1 | The Face | 3 | Reward: the pre-rolled Daemon shown on the slice; +3 Heat (someone heard). Header clue: she describes a voice that answered before the runner spoke (DISPATCH). |
| 2 | The Spike | 6 | Reward: common Firmware |
| 3 | The Route | 6 | GAIN_CYCLES +35 |
| 4 | Small Detail | 7 | GAIN_CYCLES +10 ("she remembers a small thing") |
| 5 | False Memory | 5 | Starts a normal Router combat vs `loyalty_test`, normal rewards, +10 Cycles bonus, Heat 0 |
| 6 | The Echo | 3 | MODIFY_HEAT −6, but HP −6 |

- **Quality tiers are cosmetic.** The outcome is fixed per slice, and the sub-tick map is not read. A 3-tick slice has no extra Perfect payout.
- **Nudge budget:** 1 free nudge, ±1 tick. Maximum 4 total nudges.
- **Extra nudge cost:** 8 Cycles, or 2 HP, chosen at nudge time. No Heat option.
- **Resistance:** none. The wheel can't be flipped, spun or respun.

## Design notes
- **Why it's interesting:** the pointer's start decides what you would pay to reach a better slice. Blank is the largest slice (7), so the default outcome is a small gain, and the strong outcomes (Daemon, −6 Heat) sit on 3-tick slices that cost nudges to reach.
- **Wheel EV (placeholder Cycles-equivalent):** 0.10×40 (Daemon, −3 Heat) + 0.20×25 (Firmware) + 0.20×35 + 0.233×10 + 0.167×10 (fight, net of risk) + 0.10×0 (−6 Heat vs −6 HP) = 4 + 5 + 7 + 2.3 + 1.7 + 0 ≈ 20, before nudge costs. All Cycle values are placeholders for the balance sim.
- **No dominant option:**
  - The wheel (EV ≈ 20, free, with a fight at 17 %) beats the guaranteed Cut the feed (−5 Heat, costs 15) on Cycles, while Cut the feed wins on certainty and Heat.
  - Testify yields 4 Schematics (= 40 Cycles at the 10:1 conversion) plus a softer fight for 8 HP. It is the best value but costs HP and is unavailable when low.
  - The wheel has the highest ceiling (a Daemon) and real downside (the fight, Heat).
- **Interactions:** Rigger's free nudge and Linked Bus do not apply (event wheel, not a combat wheel). Cold Exit and Clean Signal are unaffected. The Choice 3 HP loss is event damage and carries into the next fight's start HP.
- **Tone:** the Cell turned judge, with the witness as its unresolved debt. A memory you steer is a memory you've corrupted.
- **Text keys:** `ev_rc_witness_stand.title/text`, three choice labels and results, six slice names with flavor lines, the nudge-payment prompt ("Cycles / HP").
- **Dependencies:** N17 (event wheel), N16 (`next_combat_overrides`, `starts_combat`), N12 optional (variable sizes; fallback is six 5-tick slices, so Slices 1 and 6 lose their narrowness). If N17 is absent, Choice 1 falls back to one checkpointed `events` roll giving a single reward (common Firmware).

## Q:
- Q: Should Slice 1's DISPATCH clue stay on the wheel, or move into the event header text for all outcomes?
- Q: Should Slice 5's fight count as a normal Router fight for Heat, since it is a Router in rewards but arrives from an event?
