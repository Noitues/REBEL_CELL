<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__23_wheel_orbital; status ok; tokens in 4002 cache-write 0 cache-read 32585 out 1683; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/23_wheel_orbital

**Verdict:** FIX

## Issues

1. **BLOCKER, template / mechanic family: slice sizes vs tick maps.** The draft's Flare-Out map is "W W G G G G W W" (8 ticks). R11 defines sizes 2-7, and an 8-tick slice has no default map. The map as written also has no Perfect tick (the center sits between two ticks), so the Perfect rule and the "forgiving" claim are inconsistent. Either the slice must be capped at 7 or the map must be an authored `tick_quality` override.
2. **BLOCKER, R11 / sub-tick quality: Dead Sky, size 3.** Its map "G P G" is right, but the Perfect payload is "Nothing". Doubling nothing is fine, but Dead Sky takes 3 ticks of aim for a pure null outcome. The draft calls Clean Burn and Dead Sky "narrow aim targets", yet one is the jackpot and the other a dud, so the narrowness reads as noise.
3. **MAJOR, dominance: choice 2 vs choice 1.** Landing the pointer is previewed and undoable. With 3 extra nudges (±1 tick each, 3 ticks of reach), the player can steer from most starts to a good slice. Nothing limits "preview, then pick". Reach of 4 ticks total (1 free + 3 paid) covers about one slice width from any start. Clean Burn (3 ticks) is reachable only from near starts; the player pays 4-12 HP to guarantee +35 to +45 Cycles. Telemetry Spike (+35 Cycles, +4 Heat) is also a net positive for most players, so only Misfire (-10 Cycles) and Dead Sky are real losses. The wheel is positive-EV everywhere except the corruption rider, and the "Cycles" slices are not balanced against the 10 Cycle option 3.
4. **MAJOR, arithmetic and economy: payout claims.** Notes say "45 Cycle peak matches a typical 25-30 event". A Perfect Clean Burn doubles 45 to 90 Cycles, which exceeds the stated "peak" and the "a third of a typical shop buy" claim. Likewise a Perfect Misfire "doubles" its 10 Cycles, a reward on a bad slice, and a WEAK landing on Misfire still corrupts at full strength. Doubling the Cycles cost is not defined.
5. **MAJOR, R9 / statuses: Misfire corruption "for the next fight".** CORRUPTED lasts until cleansed or combat ends, and the player's wheel is not a campaign-level object between events. The duration needs an N16-style `next_combat_overrides` field, which the draft never declares. No N16 tag appears.
6. **MAJOR, template: choice 3 is not a wheel choice, and choice 1 is an uninformed gamble.** Choice 1 has "free nudge only" (budget 1), so the player reads the preview anyway. It is not a gamble, just a worse choice 2.
7. **NIT, determinism wording:** the "events RNG stream" is fine, but "Quitting restores the pointer" duplicates the checkpoint rule.
8. **NIT, spelling/text:** "the size of a oil drum" should be "an oil drum". Rooftop thruster flavor is fine.
9. **NIT, Q2:** HP vs Cycles cost is a reasonable question.

## Concrete fixes

- **Fix 1:** shrink Flare-Out to 7 ticks, map "W W G P G W W", HEAL +8. Rebalance by making Dead Sky 4 ticks (map "W G G W", no Perfect), so sizes are 3+4+7+7+5+4 = 30.
- **Fix 3/4:** drop the Perfect doubling on penalty slices (Misfire, Telemetry Spike). Set Clean Burn to +30 Cycles (Perfect 60), Telemetry Spike +25 Cycles and +5 Heat. Add "extra nudges: 5 HP each, max 2" so reach is 3 ticks. Make choice 1 start the pointer unrevealed until confirm, or drop it and let choice 2 carry a free nudge.
- **Fix 5:** add the line "(new) next_combat_overrides: apply CORRUPTED to 1 RANDOM_NON_NULL slice of the player's wheel at combat start, duration 1 fight (N16)". Fallback: replace it with `hp_cost` 6.

## Keep
- Varied slice sizes make aim matter, and the sizes sum to 30 (as drafted).
- The Heat-on-telemetry theme fits Orbital.
- Preview and undo until confirm, with the events stream checkpointed.

## Q:
- Does the free nudge exist at all on an event wheel, or should every nudge cost the extra currency?
- Should the pointer start be visible before the player commits to choice 1 or 2?
