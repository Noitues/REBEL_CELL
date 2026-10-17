<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_01TQsqGnerTdLwJEata9mp6i, custom_id v2__events__27_raidwin_any; status ok; tokens in 4711 cache-write 0 cache-read 32585 out 2801; cost $0.022. A DESIGN DRAFT for the designer's review: nothing here is built. -->

## Changes vs v1
- **Issue 1 (BLOCKER, no NEW: tag) -> fixed.** `next_raid_overrides` is now tagged **NEW: raid_overrides** and listed as an extension of N16's `next_combat_overrides` pattern to raids. The raid-win screen context is tagged too (approved in the DECISIONS rulings; the screen itself is **NEW: raid_win_reward_screen**). The choice 1 fallback is now a flat Cycles reward, not −2 Heat, because −2 Heat is not a scouting bonus.
- **Issue 2 (BLOCKER, hidden roll) -> fixed.** The roll in choice 3 is labeled (30% chance of an extra wave). It is drawn exactly once from the `events` stream at a checkpoint when the choice is committed, and a reload can't reroll it. "From the campaign seed" is removed. The odds are in the label and the preview, per GDD 2.10 ("show odds").
- **Issue 3 (MAJOR, dominated choice) -> fixed.** Choice 2 is rebalanced to +15 Cycles, +2 Heat and no strength override, so it is a certain, safe middle. Choice 3 is +25 Cycles with a labeled gamble. Choice 1 adds a 10% spoils bonus to its scouting. The contradictory "pays slightly more than choice 1 costs" line is removed.
- **Issue 4 (MAJOR, economy) -> fixed.** The unverifiable "matches Abandoned Cache" claim is removed. The note now says that event Cycles are on top of the raid's own rewards and are banked to the campaign immediately.
- **Issue 5 (MAJOR, double penalty and Heat bands) -> fixed.** Choice 2 no longer adds strength. The +2 Heat is gated: the event is not offered when current Heat would cross a 25/50/75 MAJOR threshold (it would fire a raid event), and the offer check is stated.
- **Issue 6 (NIT) -> fixed.** Choice 1's effects line lists its real effects. The reward pool line is removed. The R4 ultimatum interaction now has a mechanism.
- **Keep list:** kept the street source setting, the three stances and the `events` stream at a checkpoint.
- **Q from critic:** answered in the Q lines below.

# ev_rw_second_hand_rumor: Second-Hand Rumor
**Mechanic:** RAIDWIN, corporation any, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows. Context: the raid-win reward screen (**NEW: raid_win_reward_screen**, approved by designer ruling).
**One-line decision:** A street kid sells a rumor about the next raid at the loot table. Pay for scouting, take a safe small bonus, or take the most Cycles and gamble on the rumor being true.

## TerminalEventData fields
- id: `ev_rw_second_hand_rumor`
- title: Second-Hand Rumor
- speaker: STREET_MERC
- text: "Smoke's still coming off the relay when a noodle-stall runner finds you at the loot table. He heard from a cousin, who heard from a night-shift tech, that the corps already priced your next hit. 'Three days, maybe four,' he says, 'and they're bringing something nasty.' Could be real, could be a kid selling air. The spoils are laid out between you, and he's looking at them, not at you."
- corporation_id: `&""`
- min_tier: 1
- dispatch_clue: false
- foreshadows: `&""`
- weight: 0.8
- Offer condition: not offered if current Heat + 2 would cross a MAJOR threshold (25/50/75/100).

## Choices

**1. Pay for the details**
- label: Pay for the details (−20 Cycles; scout the next raid; +10% spoils)
- result_text: "He talks for ten minutes. Entry link, timing, the lot. You scribble it on your sleeve and he vanishes with your cash."
- cycle_cost: 20
- hp_cost: 0
- effects: `GAIN_SCHEMATICS` target CAMPAIGN amount = 10% of this raid's Schematics reward (min 1; `amount_mode` PERCENT, N1)
- reward: none
- (new) next_raid_overrides: `raid_scout_bonus = true`. In the next raid's setup, one threat vector's route is revealed one step earlier. Clears when that raid starts. **NEW: raid_overrides**
- (new) starts_combat / next_combat_overrides / map_edits: none
- Data-only fallback: replace the scouting with `GAIN_CYCLES` +20 (refund; the choice becomes a plain 10% spoils bonus).

**2. Take his free version**
- label: Hear him out (+15 Cycles, +2 Heat)
- result_text: "You nod along while pocketing the haul. He's vague about the date and certain about the 'something nasty.' You'll watch the sky."
- cycle_cost: 0
- hp_cost: 0
- effects: `GAIN_CYCLES` target CAMPAIGN amount +15; `MODIFY_HEAT` target CAMPAIGN amount +2
- reward: none
- (new) none. Fully data-only.

**3. Wave him off and take the best salvage**
- label: Wave him off (+25 Cycles; 30% chance of an extra wave next raid)
- result_text: "'Air,' you say. He shrugs and melts into the crowd. The salvage is real, anyway."
- cycle_cost: 0
- hp_cost: 0
- effects: `GAIN_CYCLES` target CAMPAIGN amount +25
- reward: none
- (new) next_raid_overrides: 30% (one draw from the `events` stream at a checkpoint on commit): `RAID_EXTRA_WAVE +1` for the next raid only. The draw is stored in the checkpoint, so a reload shows the same result. The preview shows "30% chance of an extra wave" and the result screen shows the outcome. **NEW: raid_overrides**
- Data-only fallback: a flat `RAID_STRENGTH_PCT` +5% for the next raid (certain, no roll).

## Event wheel
Not used. The one roll is the labeled 30% draw in choice 3.

## Design notes
- **No dominant option.** Choice 2 is the safe middle: +15 Cycles and +2 Heat, certain. Choice 3 is +10 more Cycles and no Heat, for a 30% chance of an extra wave. Choice 1 pays 20 Cycles for planning value and a small spoils bonus. A cautious player takes 2, a greedy one takes 3, a defender who plans takes 1.
- **Numbers (placeholders).** Event Cycles are banked to the campaign at once and sit on top of the raid's own rewards, so they are small against a full raid payout. −20 Cycles is under one typical shop purchase. +2 Heat is well under one MINOR step (10). The scouted route is worth about one asset repositioning. The 30% extra wave risks roughly one DOWN node at T1–T2.
- **Heat rules.** Heat raises raid strength through the Heat bands (GDD 4.3–4.4), so choice 2's +2 Heat is its only cost, with no extra strength override. The offer gate keeps +2 Heat from firing a MAJOR event.
- **Interactions.** With the R4 ultimatum raid (the Schematics sink), a scouted route lets the player place assets before deciding to pay the ultimatum. This holds only if the ultimatum is the next raid.
- **Text keys:** `rw_second_hand_rumor.title`, `.text`, `.c1`–`.c3` labels and results; tooltip on choice 3: "Unverified. 30% it is true."
- **Corporation-neutral.** The speaker is a street source and the text avoids corporation names.

## Q:
Q: Should the raid-win screen show this event before or after the raid's own reward list, and does the Cycle gain share the reward screen's total?
Q: Can the scouting bonus be expressed through existing raid setup data (a revealed-vector count), or does it need NEW: raid_overrides as an N16 extension?
