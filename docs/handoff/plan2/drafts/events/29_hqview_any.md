<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__29_hqview_any; status ok; tokens in 6320 cache-write 0 cache-read 32007 out 2336; cost $0.021. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_hq_dead_letter_crate: Unmarked Crate at the Loading Door

**Mechanic:** HQVIEW, corporation any, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** An unlabeled delivery crate arrives at HQ with no sender. Open it now for a gamble, hand it to an operative who knows couriers, or leave it sealed and buy a quiet kind of safety.

## TerminalEventData fields
- id: `ev_hq_dead_letter_crate`
- title: Unmarked Crate at the Loading Door
- speaker: NARRATOR (0)
- text: "A courier bike idles at the loading door and leaves before anyone signs. It leaves behind a steel crate with no label, no manifest and a faint hum from the seams. The Cell hasn't ordered anything in weeks. Everyone at the door agrees it could be a gift, a trap, or someone else's problem that just became yours."
- corporation_id: `&""`
- min_tier: 1
- dispatch_clue: false
- foreshadows: `&""`
- weight: 0.8

## Choices

### 1. Pry it open now
- label: "Pry it open (HQ-side gamble)"
- result_text: "The lid comes up on foam, wiring and one sealed pouch. Half the contents are junk. The other half is not."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_SCHEMATICS, target CAMPAIGN, amount 10; MODIFY_HEAT, target CAMPAIGN, amount +4
- reward: none
- (new) event_wheel: see below. Spun after the effects above, as the contents are sorted.
- (new) starts_combat: none

### 2. Let the old courier inspect it
- label: "Have a stationed operative inspect it (−6 HP, safe)"
- result_text: "She reads the seams like a ledger, defuses the tamper wire and hands you the clean half of the haul. The wire bit her anyway."
- cycle_cost: 0
- hp_cost: 6 (taken from the operative who would next launch)
- effects: GAIN_CYCLES, target CAMPAIGN, amount 20
- reward: one random common Firmware (`events` RNG stream, checkpointed)
- (new) map_edits: none
- (new) next_combat_overrides: none

### 3. Leave it sealed outside
- label: "Leave it on the loading dock"
- result_text: "You log it as unclaimed and walk away. By morning the crate is gone. So is the hum, and so is the itch in the back of your neck."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount −1
- reward: none

### 4. Trace the sender
- label: "Trace the sender (−15 Cycles, fight likely)"
- result_text: "The trace bounces twice and lands on a corporate collections desk. An enforcer is already on the way to retrieve their property."
- cycle_cost: 15
- hp_cost: 0
- effects: none
- reward: one Daemon (common pool), granted on a win
- (new) starts_combat: enemy `tariff_collector` (meridian, normal), tier = the operative's next netrun tier, one impromptu fight in the HQ view. Overrides: enemy HP ×1.0, no tier scaling beyond the base. Stake: a win grants the Daemon and −2 Heat; a loss costs the operative 10 HP (no death, the fight ends at 1 HP) and no reward.
- (new) combat_overrides: none beyond the above; duration is this fight only.

## Event wheel (choice 1 only)
Deterministic reveal of the crate's contents, three outcomes.

| Slice | size_ticks | Outcome |
|---|---|---|
| Salvage | 10 | GAIN_CYCLES +30 |
| Dud | 12 | nothing, the foam was all junk |
| Live tracker | 8 | MODIFY_HEAT +4 more and, in (new) `next_combat_overrides`, the next netrun's first fight gets +1 enemy resistance (duration 1 combat) |

- Sum = 30; the pointer starts at tick 0 from the `events` RNG at a checkpoint (so rewind can't reroll).
- Nudge budget: 1 free nudge of ±1 tick. Extra nudges cost 5 Cycles each, max 3.
- Quality tiers use R11 sub-tick rules (a Salvage 10-tick slice reads W W G G G P... via the default map: centre-distance based). The 8-tick Tracker slice has the narrowest Perfect, so the player is steered toward the bigger slices.
- Preview shows the slice under the pointer before commit; preview equals the result.

## Design notes
- **Why it's interesting:** each option targets a different resource. Choice 1 trades Heat for upside and variance. Choice 2 trades HP on a particular operative for guaranteed Cycles and a likely Firmware. Choice 3 is a cheap, clean option that rewards a high-Heat run. Choice 4 spends Cycles for a fight that pays a Daemon, and is the only option with a lasting reward.
- **Economy:** typical run Cycles are around 100–150 across a netrun (placeholder). Choice 1's expectation: Salvage 10/30 × 30 + 0 + Tracker 8/30 × (−4 Heat equivalent), roughly breakeven on Cycles but positive Schematics. With a nudge the player can pull toward Salvage for 5 Cycles, a small premium. Choice 2 is almost strictly better in value but costs 6 HP at the start of a run, which matters most for fragile classes (Botnet 45 HP).
- **No dominant option:** at high Heat, choice 3 wins. At low Heat with a spare operative, choice 2 wins. A rich player who wants a Daemon takes choice 4. Choice 1 is for players who love wheels.
- **Interactions:** Scrubber and Clean Signal Daemons soften choice 1's Heat; a Proxy Relay in the network softens the Tracker. Choice 4 reuses the `tariff_collector` enemy (corp-neutral enough in HQ view; it's a "collections" lookalike).
- **Text keys:** `ev_hq_dead_letter_crate.title`, `.text`, `.c1`–`.c4` labels and results, wheel slice labels (`salvage`, `dud`, `tracker`).

## Q:
- Q: Does an HQ-view impromptu fight (choice 4) cost the operative a netrun slot, or is it free between runs?
- Q: Should the live-tracker slice's `next_combat_overrides` stack with Heat-driven enemy resistance (GDD 4.3, Heat 50), or take the higher value?
