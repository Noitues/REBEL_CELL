<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__28_raidwin_rebel_cell; status ok; tokens in 6411 cache-write 0 cache-read 32007 out 2138; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_rc_held_courier: The Man in the Van

**Mechanic:** RAIDWIN, corporation rebel_cell, min_tier 1, weight 0.8, dispatch_clue true
**One-line decision:** Interrogate, free, or hand over a captured corporate courier, trading Cycles now against Heat, a future fight, or a clue about DISPATCH.

## TerminalEventData fields
- id: `ev_rc_held_courier`
- title: The Man in the Van
- speaker: STREET_MERC (1)
- text: "The raid is over and the street is quiet. In the back of a dead recall van, one courier sits zip-tied. He's a subbie with a corp lanyard and a bag of sealed drives, and he's shaking. He swears he only drives. He also says the drives were ordered by 'a buyer who pays before the collapse.' Your people are waiting for you to decide what he is."
- corporation_id: `rebel_cell`
- min_tier: 1
- dispatch_clue: true
- foreshadows: (empty)
- weight: 0.8

## Choices

**1. Squeeze him for the drives**
- label: "Interrogate him (+35 Cycles, +4 Heat)"
- result_text: "He gives up the drive keys in ten minutes. The sealed drives hold payroll skims. By morning someone upstairs notices the courier never checked in."
- cycle_cost: 0
- hp_cost: 0
- effects: GAIN_CYCLES, target CAMPAIGN, amount 35. MODIFY_HEAT, target CAMPAIGN, amount 4.
- reward: none
- (new) starts_combat: none
- (new) next_combat_overrides: none
- (new) map_edits: none

**2. Cut him loose and take the buyer's name**
- label: "Let him walk (-2 Heat, ambush later)"
- result_text: "He runs without looking back. At the corner he mouths a name to you, one you've seen on an escrow receipt. He will talk, and so will whoever he tells."
- cycle_cost: 0
- hp_cost: 0
- effects: MODIFY_HEAT, target CAMPAIGN, amount -2.
- reward: a random common Daemon from the rebel_cell pool, a stolen dispatch beacon the courier slipped you (the clue)
- (new) next_combat_overrides: for the next netrun only (duration 1 run), the first Normal fight on layer 1–3 swaps its enemy to `cell_informant`, with +1 Heat on a win. Stake: the courier tipped off the corp, who sent a snitch.
- (new) starts_combat: none
- (new) map_edits: none

**3. Hand him to the crew's medic**
- label: "Patch him up, recruit him (-10 Cycles)"
- result_text: "He's got a bad shoulder and worse ethics. The medic wraps him up and he mutters that he'll drive for anyone who doesn't bill him. You don't ask whether that's loyalty."
- cycle_cost: 10
- hp_cost: 0
- effects: none
- reward: a Firmware chip from his van (Patch+, common)
- (new) starts_combat: none
- (new) map_edits: adds a one-use "Courier Route" cross-link on the Grid to the nearest locked Site (a locked cross-link opens, flagged as a raid route as well, per the approved cross-link rule).
- (new) next_combat_overrides: none

**4. Hold on, check the drive first**
- label: "Open the drives on-site (-4 HP, fight)"
- result_text: "The drive is trapped. A loyalty process wakes in the van and your crew has to put it down before it phones home."
- cycle_cost: 0
- hp_cost: 4
- effects: none
- reward: rare Firmware on a win (the drive's contents)
- (new) starts_combat: enemy `loyalty_test`, overrides: enemy HP ×0.8, no Heat on win. Stake: on a win, the rare reward above; on a loss, the normal death consequences apply (the event is a real impromptu fight).
- (new) next_combat_overrides: none
- (new) map_edits: none

## Event wheel
Not used.

## Design notes
- **Spread:** Choice 1 is the cash and Heat play (35 Cycles is roughly one Mainframe purchase; 4 Heat is a modest MINOR-step cost). Choice 2 is the cheap, safe, Heat-lowering option, but it plants a later fight, so the debt comes due. Choice 3 is the tempo-and-map option: a Firmware plus a cross-link costs 10 Cycles, but a cross-link also opens a raid route, which a defender may not want. Choice 4 is the skill-check option: it gets the best reward but risks HP and a real fight against a normal enemy. None dominates, because each pays in a different currency (Cycles, Heat, map, risk).
- **Raid-win context:** after a raid the player's HP is not an issue, but Heat is likely rising, which makes choice 2 attractive and choice 1 tense. The player has just defended, so the stakes feel earned.
- **Dispatch clue:** the "buyer who pays before the collapse" line echoes the GDD 8.2 clue about a buyer who profits from every collapse. The tone is Tech-Noir with a Street Merc voice. No extra text keys beyond the title, text and four labels and results.
- **Determinism:** the swapped enemy in choice 2 is fixed by event id and layer, with no RNG. Choice 4's fight uses the normal combat seed from the events stream.
- **Systems:** next_combat_overrides and the impromptu fight need N16. Map edits need N16 `map_edits`. Without N16, a data-only fallback keeps only the Cycles, Heat and reward fields: choice 2 becomes −2 Heat plus the Daemon, choice 3 drops the cross-link, and choice 4 becomes "−4 HP for the Firmware".
- **Raid screen:** this event requires the approved raid-win reward-screen context.

## Q:
- Q: Should a cross-link opened by choice 3 count as a new raid entry point immediately, or only after the next Heat threshold?
- Q: Should choice 2's planted `cell_informant` fight be skippable by paying Cycles at the node?
