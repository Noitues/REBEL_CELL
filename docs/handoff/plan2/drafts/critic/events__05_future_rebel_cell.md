<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__05_future_rebel_cell; status ok; tokens in 3656 cache-write 0 cache-read 32585 out 1611; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/05_future_rebel_cell

**Verdict:** FIX

## Issues

1. **BLOCKER. R1/R2/R3 and the threshold floors.** Choice 1 gives "enemy HP -15 % (applied after the tier base per R2)", and the notes say "percent HP changes scale max HP for the fight and thresholds are recomputed". R2 sets HP from `hp_by_tier` and `hp_bands`, which are validated per class band, so this is a second HP path. Recomputing floors would push elites below their authored budget (2 phases at 3-4 turns each). Because the draft promises phases "stay 3-4 turns", this is also a falsified claim. Choice 1 is the only affected option, but it's the one the whole design leans on.
2. **BLOCKER. Self-contradiction on boss fights.** The Q asks whether overrides apply to boss fights. The notes already decide "overrides ignore the HQ boss" and that the window "keeps the count" for the next normal or elite fight. Nothing says whether that rule covers mini-bosses, which the HQ-boss wording leaves unclear. The fight-4 "+15 % damage" is also said to hit "the elite or Rack at the end", and Racks are elite-strength fights, so the exclusion rules are inconsistent.
3. **MAJOR. Dominance.** The short deal costs 8 HP and 6 Heat. For two fights it gives Freeze (a free skipped respin), -1 resistance and -15 % HP. The long deal costs only 25 Cycles, which is under a quarter of the draft's own 100-150 Cycle run economy, and is front-loaded with precision aids. The haggle costs 3 HP, has no penalty clause, covers 3 fights and gives -1 resistance and satellite removal. On paper the haggle is "half the benefit" but lasts longer and has no downside. It beats the short deal for any Ghost or Botnet build, and only the fight-4 +15 % damage penalty offsets the long deal.
4. **MAJOR. Satellite override is not an existing field.** `satellite_spawn_count -1` is not a field in the GDD or N16. It is a new override key with no N# or fallback.
5. **MAJOR. "Free nudge extra" and "phase reveal" are listed as overrides** without saying whether they are N16 keys. N16 lists them in the family description, but the draft doesn't say whether the extra free nudge refreshes with the start-of-turn refresh (GDD 2.2). Phase reveal duplicates the Chart Hidden counter Exploit on bosses.
6. **NIT. Template fields.** `effects` is written as "MODIFY_HEAT / CAMPAIGN / amount 6" with no `duration_turns`, and text keys omit a result key for choice 4's override chip.
7. **NIT. Contract replacement.** "A second Standing Contract replaces the first" isn't tied to a real key name.

## Concrete fixes

- **Issue 1:** Replace `enemy HP -15 %` with a flat-turn effect that doesn't touch HP, e.g. "enemy opens the fight with BLOCK 0, and its first start-of-turn intent is skipped" (the Freeze already does this). If HP stays, state it as "enemy `hp_by_tier` entry read one tier lower, floored at T1" and cap it at normals and elites. Drop the "thresholds recomputed" sentence.
- **Issues 2 and 3:** State "Overrides apply to normal, elite and Rack fights only; mini-boss and HQ boss are skipped; the counter keeps its value" in the Mechanic line. Change the haggle label to "(-3 HP, 2 fights)" and the duration to 2 so it is lower on both ceiling and length than the short deal. Add a +4 Heat penalty to the long deal, or drop it to a 20 Cycle cost and give the fight-4 penalty +25 % damage, so the long deal's value is clearer.
- **Issue 4:** Tag it `NEW: satellite override key (data-only fallback: enemy loses one satellite_spawn entry in `EnemyData`; none in this draft)`.
- **Issue 5:** Mark both as "N16 `next_combat_overrides` keys: `free_nudge_bonus`, `reveal_phases`" and note that the extra nudge refreshes each turn like the free nudge.

## Keep

The three levels of commitment with a clear price for each is the right shape. The deterministic, fixed-text haggle with no roll is correct. The "mirror of the corporate subscription" tone fits the Street Merc voice.

## Q:

- Should an override chip show remaining fights on the map as well as on the enemy?
- Does a skipped boss fight still tick the counter? (The draft says no.)
