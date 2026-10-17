<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__21_wheel_meridian; status ok; tokens in 3672 cache-write 0 cache-read 32585 out 1597; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/21_wheel_meridian

**Verdict:** FIX

## Issues

1. **BLOCKER, template / N17: contradictory pointer start.** "A wheel pointer starts on tick 0" and "The start position comes from the `events` RNG stream" can't both hold. "Tick 0 (the center of slice 1)" is also wrong. With sizes 4/6/7/5/4/4, slice 1 spans ticks 0-3 and its center is tick 1.5, so there is no single center tick. Under R11 a 4-tick slice has no Perfect.
2. **BLOCKER, determinism: random reward inside a slice.** Slice 2's "random Firmware (common pool, `events` stream at the checkpoint)" and slice 6's "random uncommon Daemon" make the reward unpredictable on commit. The steering preview can't show the actual outcome, so preview ≠ result.
3. **MAJOR, template: nudge economics are unsound.** Free nudges (3) plus up to 5 paid ones means up to 8 ticks of steering. On a 30-tick wheel with a 7-tick dud that is nearly free aiming. Extra nudges costing 4 HP or 2 Heat each is not tuned against slice 1 (+50 Cycles). The decision collapses to "always steer to slice 1 or 2". Design notes claim an EV of about 28 Cycles, but no arithmetic is shown, and the random start makes it unverifiable.
4. **MAJOR, quality: dominated or dead choices.** Choice 3 (−1 Heat, nothing else) is dominated by choice 2 (+35 Cycles) for any run not at a Heat threshold. Choice 1's hot-start risk is capped by the nudges.
5. **MAJOR, design notes: adjacency is wrong.** "The two bad bins (Audit Flag, Hot Freight) are adjacent to Customs Hold" is false only in part. Slices 4, 5 and 6 are adjacent, but Customs Hold is itself a mild-bad bin, so a cluster of three bad slices spans 13 ticks. Slice 1 neighbors slice 6, so wraparound from slice 1 lands on the worst slice. The notes also say slice 3 is "a safe buffer between 2 and 4", yet the wheel's 7-tick dud is the largest target.
6. **MAJOR, outcome spelling: slice 5 stake is underspecified.** "RESISTANCE +1 (weight)" is a combat override with no duration. "Flee is not possible" has no field. An elite or normal fight for +30 Cycles has no stated penalty on loss.
7. **NIT, ids and spelling:** `.nudge_extra_hp` and similar text keys are fine. "center" is US spelling. Choice 1 label "3 free nudges" leaks the mechanic, which is fine.

## Concrete fixes

1. Replace the start rule: "Pointer start tick = `events` stream draw in 0-29, checkpointed before the first nudge. Slices: 1 = ticks 0-3, 2 = 4-9, 3 = 10-16, 4 = 17-21, 5 = 22-25, 6 = 26-29. Quality map per R11." Delete "starts on tick 0".
2. Make the rewards fixed per slice at the data level: slice 2 = a named Firmware pool entry chosen at event spawn from `events`, shown on the wheel face. Slice 6 = a named Daemon, likewise. The preview then equals the result.
3. Retune nudges: 2 free; extra nudges cost 5 HP or +3 Heat each, max 3 extra. This gives a maximum of 5 ticks, which is under a quarter of the wheel.
4. Make choice 3 useful: "Burn the note: −3 Heat and +10 Cycles". Alternatively raise choice 2 to 30 and add −1 Heat as a rider.
5. Reorder to 1 (4), 3 (7), 2 (6), 4 (5), 6 (4), 5 (4), so that the best slice sits next to the jackpot and the dud buffers the fight.
6. Slice 5: `combat_overrides`: enemy RESISTANCE +1 for the whole fight; `flee_allowed = false` (new field on `starts_combat`); loss follows normal combat rules, and the +30 Cycles is paid only on a win.

## Keep
- The no-owed-debts hook and noir text are strong.
- The data-only fallback is clear and honest.
- The wheel pairs a safe pair of options with a gamble.

## Q:
- Q: Should the wheel face reveal each slice's exact reward before the pull?
- Q: Should the Heat cost scale with the current Heat band?
