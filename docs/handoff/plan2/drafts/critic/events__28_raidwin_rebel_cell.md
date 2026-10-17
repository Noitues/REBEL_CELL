<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__28_raidwin_rebel_cell; status ok; tokens in 3582 cache-write 0 cache-read 32585 out 1700; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/28_raidwin_rebel_cell

**Verdict:** FIX

## Issues

1. **BLOCKER, template (choice 2, reward):** "a random common Daemon from the rebel_cell pool". The core allows no randomness outside named RNG streams, and the draft names no stream. The draft's own determinism note says only the enemy swap is fixed, so the Daemon pick is unaccounted for.
2. **BLOCKER, systems (choice 2, `next_combat_overrides`):** the field is "the first Normal fight on layer 1–3 swaps its enemy to `cell_informant`, with +1 Heat on a win". The N16 field `next_combat_overrides` is a run-level override, but the draft doesn't say what happens when no netrun is launched next, or where it applies if a raid interrupts a run. The Heat on a win is also unstated as an effect. The label reads "ambush later", but the Ambush node is ruled "no as a node; maybe as an event option". This is acceptable only if the draft names it an event-option ambush. It also makes choice 2 contradict its own label: it is billed as the safe option, yet it adds Heat and a fight.
3. **MAJOR, systems (choice 3, `map_edits`):** the draft opens a "Courier Route" cross-link and flags it as a raid route. D6 and the G11 rulings keep the City Grid layer, but `map_edits` in N16 is defined for the netrun map graph (`map_graph`), not for Grid cross-links. This needs its own tag: "NEW: grid_link_edit". The data-only fallback also drops the link, which leaves choice 3 as −10 Cycles for a common Patch+, a clearly dominated choice.
4. **MAJOR, template and rules (choice 4):** the draft puts the raid-win screen on a "real impromptu fight" with death consequences, at −4 HP, against `loyalty_test` at ×0.8 HP. The HP is a placeholder with no derivation against the R2 tier bands (Normal T1 is 28–36). `loyalty_test`'s phase count and HP are not shown. "Rare Firmware" is a reward far above the other three, so it dominates unless the loss risk is real. The draft's "skill-check" note says the fight is only against a normal enemy, so the risk is small, and the −4 HP is a negligible cost. The fallback ("−4 HP for the Firmware") removes the risk entirely and gives away a rare reward. Choice 4 dominates.
5. **MAJOR, balance (choice 1):** +35 Cycles for +4 Heat, with no reference to the economy. Heat crossing a MINOR step (every 10) also fires a netrun complication, which the notes call "modest".
6. **NIT, template:** `foreshadows` is empty (fine), but `dispatch_clue: true` is carried only by the line "a buyer who pays before the collapse", while the "dispatch beacon" in choice 2 is the second clue. Choice 2 carries no clue text in its result_text.
7. **NIT:** "Hold on, check the drive first" is the label of a choice whose fight carries no stake text. Text is about 370 words, under the 450 minimum.

## Concrete fixes

- **1:** Replace with "reward: Daemon `Clean Signal` (GDD 6.2, fixed)". Or draw from the `events` stream at a checkpoint and write that into the determinism note.
- **2:** Change the label to "Let him walk (-2 Heat, snitch later)". Add: "next_combat_overrides: duration 1 netrun launched after this raid; the first Normal fight on layer 1–3 uses `cell_informant`; MODIFY_HEAT +1 on win. Fallback: no override; the Daemon only." State that it is an event-option ambush (ruled allowed).
- **3:** Tag the edit "(NEW: grid_link_edit)". Raise the reward to rare-less but real: Patch+ plus one free nudge-card, or cut the cost to 0 Cycles. Fallback: keep the Firmware and drop the cost to 5.
- **4:** Remove the death stake. Make it: `loyalty_test` at its normal HP, hp_cost 0, win = a rare Firmware, loss = Firmware lost and +3 Heat (not death). Show HP: T1 normal band 28–36, so ×0.8 ≈ 26 would break the band, so use no HP override. Fallback: "−6 HP for a common Firmware".
- **5:** Set +30 Cycles and +5 Heat, so Heat crosses a 10-step with a visible penalty.

## Keep
- The voice and the clue line ("a buyer who pays before the collapse") match GDD 8.2.
- Four choices that pay in different currencies is the right shape; the raid-win framing is clean.

## Q:
- Q: Is `loyalty_test` a Normal (1 phase) here, so a ×0.8 HP override would be outside the R2 band?
- Q: Does the cross-link edit belong to N16 or to the raid design pass?
