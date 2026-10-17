<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__28_raidwin_rebel_cell; status ok; tokens in 5107 cache-write 0 cache-read 32585 out 3146; cost $0.024. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, random Daemon):** the Daemon is now fixed: `Clean Signal` (GDD 6.2). No RNG is involved, and the determinism note says so.
- **Issue 2 (BLOCKER, `next_combat_overrides` scope, Heat, label):**
  - Scope is now explicit: duration is the first netrun launched after this raid. It is consumed on the first Normal fight on layers 1–3, or discarded unused if that run ends without one.
  - If a raid interrupts a run, the override stays queued and is not consumed by raid interludes.
  - The win Heat is a stated effect (`MODIFY_HEAT` +1, win only).
  - The label is now "snitch later", and the draft says outright that this is an event-option ambush, which the rulings allow (no Ambush node).
  - Choice 2 is no longer billed as safe. It is the low-Heat now, fight later option.
  - A data-only fallback is given.
- **Issue 3 (MAJOR, map edit):**
  - The edit is tagged "NEW: grid_link_edit", not N16 `map_edits`.
  - The cost drops to 0 Cycles.
  - The reward is Patch+ plus a free nudge card, so it isn't dominated.
  - Fallback keeps the Firmware and card and drops the link.
  - The Grid link edit was left to a Q:, since it may belong to the raid design pass.
- **Issue 4 (MAJOR, choice 4 dominates):**
  - Death stake removed and `hp_cost` is 0.
  - No HP override: `loyalty_test` is a Normal (1 phase) at its tier band (T1 28–36, per R2), and ×0.8 would break the band.
  - A win gives rare Firmware. A loss costs Firmware and +3 Heat. A loss is not death (a ruling-safe soft stake).
  - Fallback: −6 HP for a common Firmware.
- **Issue 5 (MAJOR, choice 1):** now +30 Cycles and +5 Heat. Heat crossing a MINOR step fires a complication, and the text says so.
- **Issue 6 (NIT, clue):** choice 2's result_text now carries the second clue, the beacon.
- **Issue 7 (NIT):** the fight has a stake line, and the word count is raised.
- **Kept:** the voice, the "buyer who pays before the collapse" line, four choices in different currencies, and the raid-win framing.

# ev_rc_held_courier: The Man in the Van

**Mechanic:** RAIDWIN, corporation rebel_cell, min_tier 1, weight 0.8, dispatch_clue true
**One-line decision:** Interrogate, free, recruit, or crack open a captured courier's drives, trading Cycles now against Heat, a planted future fight, a route, or a gamble on a rare chip.

## TerminalEventData fields
- id: `ev_rc_held_courier`
- title: The Man in the Van
- speaker: STREET_MERC
- text: "The raid is over and the street is quiet. In the back of a dead recall van, one courier sits zip-tied. He's a subbie with a corp lanyard and a bag of sealed drives, and he's shaking. He swears he only drives. He also says the drives were ordered by 'a buyer who pays before the collapse.' Your crew is waiting on you to decide what he is: a source, a witness, a hire, or a trap."
- corporation_id: `rebel_cell`
- min_tier: 1
- dispatch_clue: true
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Squeeze him for the drives**
- label: "Interrogate him (+30 Cycles, +5 Heat)"
- result_text: "He gives up the drive keys in ten minutes. The drives hold payroll skims. By morning someone upstairs notices the courier never checked in, and the city feels a little warmer."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 30. MODIFY_HEAT, target CAMPAIGN, amount 5.
- reward: none
- (new) starts_combat: none
- (new) next_combat_overrides: none
- (new) map_edits: none

**2. Cut him loose and take the buyer's name**
- label: "Let him walk (-2 Heat, snitch later)"
- result_text: "He runs without looking back. At the corner he mouths a name you've seen on an escrow receipt, and presses a dispatch beacon into your hand. It's already warm, like something on the other end is listening. He'll talk, and so will whoever he tells."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount -2.
- reward: Daemon `Clean Signal` (fixed, the beacon)
- (new) next_combat_overrides: this is an event-option ambush, not a map node. Duration: the first netrun launched after this raid. The first Normal fight on layers 1–3 of that run swaps its enemy to `cell_informant`. On a win, MODIFY_HEAT +1. The override is consumed by that fight. Raid interludes during the run don't consume it. If the run has no such fight, it is discarded when the run ends. Stake: the courier tipped off the corp, who sent a snitch. Fixed by event id and layer, no RNG.
- (new) starts_combat: none
- (new) map_edits: none
- Fallback without N16: no override, just −2 Heat and the Daemon.

**3. Hand him to the crew's medic**
- label: "Patch him up, recruit him (free)"
- result_text: "He's got a bad shoulder and worse ethics. The medic wraps him up and he mutters that he'll drive for anyone who doesn't bill him. He opens a route on his dash map and hands over a chip and a tuned nudge routine from his van."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: Firmware `Patch+` (common) and one free nudge card (common)
- (new) grid_link_edit (NEW: grid_link_edit): opens one locked cross-link on the City Grid to the nearest locked Site. It is flagged as a raid route as well, per the cross-link rule.
- (new) starts_combat: none
- (new) next_combat_overrides: none
- Fallback without grid_link_edit: keep the Firmware and card, drop the link.

**4. Hold on, check the drive first**
- label: "Open the drives on-site (fight, rare chip or +3 Heat)"
- result_text: "The drive is trapped. A loyalty process wakes in the van, and your crew has to put it down before it phones home."
- cycle_cost: 0
- hp_cost: 0
- effects: none
- reward: rare Firmware on a win
- (new) starts_combat: enemy `loyalty_test`, no HP override. It is a Normal (1 phase) at its tier band (T1 28–36, R2). Stake: a win gives the rare Firmware. A loss gives nothing and costs +3 Heat. A loss is not a death; the operatives are not at risk, only the haul.
- (new) next_combat_overrides: none
- (new) map_edits: none
- Fallback without N16: "−6 HP for a common Firmware".

## Event wheel
Not used.

## Design notes
- **Spread:**
  - Choice 1 is the cash and Heat play. 30 Cycles is about one Mainframe purchase. +5 Heat can cross a MINOR step (every 10) and fire a netrun complication.
  - Choice 2 is the cheap, Heat-lowering option with a delayed bill: one snitch fight, +1 Heat on a win, and a common Daemon up front.
  - Choice 3 costs nothing and gives a common Firmware, a card and a map route. Its price is opening a raid route, which a defender may not want.
  - Choice 4 is the gamble: the best reward, but a real fight and +3 Heat if it goes wrong.
  - None dominates because each pays in a different currency: Cycles, Heat, map or risk.
- **Raid-win context:** Heat is likely high after a raid, so choice 2 is attractive and choice 1 is tense. The player has just defended, so the stakes feel earned.
- **Dispatch clue:** two clues. The buyer line echoes GDD 8.2. The warm beacon in choice 2 hints that DISPATCH is listening.
- **Determinism:** no randomness. The Daemon is fixed, the swapped enemy is fixed by event id and layer, and choice 4's fight uses the normal combat seed from the events stream at a checkpoint.
- **Systems:** next_combat_overrides and the impromptu fight need N16. Choice 3 needs NEW: grid_link_edit. A data-only fallback exists for each choice (above).
- **Text keys:** the title, the text and four labels with results. This event needs the approved raid-win reward-screen context.

## Q:
- Q: Should a cross-link opened by choice 3 count as a new raid entry point immediately, or only after the next Heat threshold?
- Q: Does grid_link_edit belong to N16 or to the raid design pass?
