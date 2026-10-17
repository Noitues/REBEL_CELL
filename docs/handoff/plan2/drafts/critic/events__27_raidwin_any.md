<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__27_raidwin_any; status ok; tokens in 3369 cache-write 0 cache-read 32585 out 1511; cost $0.014. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/27_raidwin_any
**Verdict:** FIX

## Issues
1. **BLOCKER, new-system tagging:** `next_raid_overrides` (`raid_scout_bonus`, `RAID_STRENGTH_PCT`, `RAID_EXTRA_WAVE`, `rumor_true_flag`) has no N# or NEW: tag. N16 only covers `next_combat_overrides`, so it needs "NEW: next_raid_overrides" or an N16 extension. The template also requires an N# or NEW: on the raid-win screen context itself. Choice 1's fallback is not equivalent, since −2 Heat is not a scouting bonus.
2. **BLOCKER, determinism / preview = result:** Choice 3 is a hidden 30% roll, and the Q concedes "previews equal results, but this is a roll". The core forbids a hidden outcome behind an unlabeled roll. The `events` stream at a checkpoint is allowed, but the roll must be shown as odds (GDD 2.10 "show odds") and drawn exactly once at the checkpoint. A reload must not reroll it. The draft says "seed", which would make the result fixed per campaign, contradicting a checkpointed stream draw.
3. **MAJOR, dominated choice:** Choice 3 (+25 Cycles, 30% chance of one extra wave) beats choice 2 (+10 Cycles, +2 Heat, +10% raid strength, a certain penalty). Choice 2 is nearly dominated, so the "no dominant option" note fails. Choice 1 buys information and gives no spoils, so it is not comparable. The note also contradicts itself: it says choice 2 "pays slightly more than choice 1 costs", but +10 is less than 20.
4. **MAJOR, economy:** The "+25 Cycles matches Abandoned Cache" claim is unverifiable. A raid-win reward is already paid by the raid, so these Cycles stack on top of it. The draft also doesn't say whether the Cycles are banked.
5. **MAJOR, rule consistency:** "Raid strength scales with current Heat" (GDD 4.4), and choice 2 adds Heat and also +10% strength, which double-penalizes. "Heat bands" appear, but a +2 Heat tip over a 25 threshold would fire a raid event, which the note flags but doesn't resolve.
6. **NIT, template:** The word count is fine. The `effects` line for choice 1 says "none", though `MODIFY_HEAT` is invented as the fallback. Choice 3's reward line mentions a pool that isn't specified. The R4 ultimatum interaction is asserted without a mechanism.

## Concrete fixes
- Tag: "(new) next_raid_overrides: **NEW: raid_overrides** (or an N16 extension to raids); fallback: `MODIFY_HEAT` −2 or a flat Cycles reward."
- Choice 3: replace the hidden flag with a labeled roll: "30% (events stream, one draw at the checkpoint on choice commit): `RAID_EXTRA_WAVE +1` next raid". Preview text: "30% chance of an extra wave". Drop "from the campaign seed".
- Rebalance:
  - Choice 2: `GAIN_CYCLES` +15, `MODIFY_HEAT` +2, no strength override (remove the double penalty).
  - Choice 3: +25 Cycles, with the 30% extra wave as a labeled gamble.
  - Choice 1: −20 Cycles, `raid_scout_bonus`, plus a 10% spoils bonus (a tradeoff to compare with 2).
- Fix the note: "Choice 2 is the safe middle (+15, +2 Heat, certain); choice 3 is +10 more Cycles for a 30% extra-wave risk; choice 1 buys planning."

## Keep
- The setting: a street source at the loot table fits the raid-win screen and is corporation-neutral.
- Three clearly different stances (buy information, a certain middle, a gamble) are the right shape.
- Using the `events` stream at a checkpoint is the correct determinism approach once the roll is labeled.

## Q:
Q: Does a raid-win reward screen exist as a named context (and where does the event's Cycle gain sit relative to the raid's own rewards)?
Q: Can the scouted-route bonus be expressed through existing raid setup data, or does it need NEW: raid_overrides?
