<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_017iwACxXDMq9SHDq1C11Juv, custom_id event__27_raidwin_any; status ok; tokens in 6328 cache-write 0 cache-read 32007 out 1930; cost $0.019. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# ev_rw_second_hand_rumor: Second-Hand Rumor
**Mechanic:** RAIDWIN, corporation any, min_tier 1, weight 0.8, no dispatch_clue, no foreshadows
**One-line decision:** The raid is over and the spoils are on the table. A street kid sells a rumor about the next raid, and the player weighs paying for it, trusting the free version, or ignoring it.

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

## Choices

**1. Pay him for the full story**
- label: Pay for the details (-20 Cycles, +1 Armory prep)
- result_text: "He talks for ten minutes. Entry link, timing, the lot. You scribble it on your sleeve and he vanishes with your cash."
- cycle_cost: 20
- hp_cost: 0
- effects: none in the existing effect list (see the new-system line)
- reward: none
- (new) next_combat_overrides: none
- (new) map_edits: none
- (new) next_raid_overrides: `raid_scout_bonus = true`. On the next raid's setup phase, one threat vector's route is revealed one step earlier. Lasts until the next raid starts, then clears.
- Data-only fallback: replace it with `MODIFY_HEAT` amount -2, target CAMPAIGN ("he also sold your name down").

**2. Take his free version and keep the loot**
- label: Take the spoils, hear him out (free)
- result_text: "You nod along while pocketing the haul. He's vague about the date and certain about the 'something nasty.' You'll watch the sky."
- cycle_cost: 0
- hp_cost: 0
- effects: `GAIN_CYCLES` target CAMPAIGN amount +10; `MODIFY_HEAT` target CAMPAIGN amount +2
- reward: none
- (new) next_raid_overrides: `RAID_STRENGTH_PCT +10` for the next raid only (rumor was true-ish).
- Data-only fallback: omit the override and keep the cycles and Heat.

**3. Tell him to scram, take the best salvage**
- label: Wave him off (take salvage)
- result_text: "'Air,' you say. He shrugs and melts into the crowd. The salvage is real, anyway."
- cycle_cost: 0
- hp_cost: 0
- effects: `GAIN_CYCLES` target CAMPAIGN amount +25
- reward: none (the pool for a defense asset or minor Firmware would come from the raid-win reward list)
- (new) next_raid_overrides: `rumor_true_flag` is set deterministically from the campaign seed (the `events` RNG stream at its checkpoint). If true, the next raid has `RAID_EXTRA_WAVE +1`. Preview shows odds, not outcome (30% true).
- Data-only fallback: set the extra wave to a flat +5% `RAID_STRENGTH_PCT`.

## Event wheel
Not used. The only random roll is the hidden "rumor true" flag in choice 3, drawn from the `events` stream at a checkpoint so a reload can't reroll it.

## Design notes
- **No dominant option.** Choice 1 buys information at a real price, and the preview names the benefit as a scouted route. Choice 2 pays slightly more than choice 1 costs but adds Heat and a soft raid penalty. Choice 3 pays the most and carries a 30% hidden risk of an extra wave, which is the only choice the player can't fully read. A player who values defense planning picks 1, one who wants Cycles reads 2 vs 3 as a certain small penalty against a gamble.
- **Numbers.** +25 Cycles matches the Abandoned Cache baseline. -20 Cycles is under one typical shop purchase. +2 Heat sits well under a MINOR threshold step (10). The scouting bonus is worth about one asset repositioning in setup; the 30% extra wave is a stake of roughly one DOWN node at T1-T2.
- **Interactions.** It stacks with the R4 ultimatum raid (the Schematics sink): a scouted route helps place assets before the ultimatum. It also interacts with the Heat bands, since the +2 Heat in choice 2 can tip a player over a 25 threshold, so check that against the actual Heat before offering.
- **Text keys:** `rw_second_hand_rumor.title`, `.text`, `.c1`-`.c3` labels and results, and a tooltip on choice 3: "Unverified. 30% it was true."
- **Corporation-neutral.** The speaker is a street source, so it fits any corporation; the text avoids corporation names.

## Q:
Q: Should the unscouted outcome of choice 3 be disclosed as odds in the label, or kept hidden so the rumor stays a rumor (previews equal results, but this is a roll, not a preview)?
Q: Is "next_raid_overrides" a new field distinct from `next_combat_overrides` (N16), or should N16 be extended to cover raids so this event needs no new system?
