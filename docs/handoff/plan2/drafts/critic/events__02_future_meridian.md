<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__02_future_meridian; status ok; tokens in 3674 cache-write 0 cache-read 32585 out 1754; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/02_future_meridian
**Verdict:** FIX

## Issues
1. **BLOCKER, template / "Use only enemy ids"**: the draft has no `starts_combat`, `map_edits` or `event_wheel` lines, but it also lacks the required per-choice field lines (`cycle_cost` and `hp_cost` are shown, `starts_combat` is not). Only "(new)" lines that are used are strictly needed, so this is minor. The real blocker is the missing mechanic scope: the choice 3 filter "elite or mini_boss" with "cap of 3 fights" is not in the N16 field list and is not defined. It is a second, undefined expiry system, and it contradicts the Q (expire vs. persist), so the draft is internally undecided.
2. **BLOCKER, arithmetic / design notes**: "+2 Heat is about 1/12 of a MINOR threshold of 10" is wrong. 2/10 = 1/5. Also "−15% ≈ 13–17 HP" is computed from T3 bands (88–112) but then called "nearly a full phase at T1–T2". A phase at T1–T2 is about 28–44 HP; 13–17 HP is under half a phase.
3. **MAJOR, R2 / N16**: `enemy_hp_pct = −15` applies to a boss-class (mini-boss) fight. HP must come from tier bands, and a percent change shifts the phase-threshold HP (R3 floors are ceil(max × threshold)). The draft does not say whether max HP or current HP changes, or that the floors recompute. Specify max HP, with floors recomputed from the new max.
4. **MAJOR, ruling "Tier sets base values only; buffs tier-independent"**: `enemy_damage_pct = −10` is fine as a tier-independent debuff. But the Jam choice stacks resistance −1 and damage −10% for 2 fights for only 2 Heat and no HP or Cycles. It dominates choice 1 for any player not at a Heat threshold. Choice 1's "reveal_phases" is useless against 1-phase normals, as the draft admits, so choice 1 is mostly the weak option.
5. **MAJOR, system tagging**: `bonus_free_nudges`, `enemy_starts_frozen` and `reveal_phases` are listed as "(N3 phase reveal)". N3 does not cover reveal; it belongs to N16 overrides plus the Chart Hidden buff (N5). Mistagged. A phase reveal on a normal enemy is also a null effect.
6. **MAJOR, Freeze rule**: the draft says Frozen "skips its first start-of-turn respin, per Freeze". Freeze means the target skips its next respin. That is the first turn only, but the notes claim it "removes one turn of enemy re-aim" and make intent "known and stable". That is true only if the preview shows it, which is unstated.
7. **NIT**: "Chart Hidden … stacks … by countering it" is unclear. Define it: reveal overrides Chart Hidden.
8. **NIT**: the text's "A voice on this channel gets obeyed by a few hundred machines" is fine. "dispatch_clue: false" should be left empty.

## Concrete fixes
- Fix 1: choice 3, replace the filter with N16's field: `applies_to_class = [elite, mini_boss]`, `duration_combats = 1`, `expires_after_combats = 3`. Declare `expires_after_combats` as "NEW: override expiry", or drop it and make the override persist until used (decision: persist; the preview chip on the map tells the player).
- Fix 2: "+2 Heat is one fifth of a MINOR step (10)." "−15% max HP is ~5–6 HP on a 36 HP T1 normal, ~13–17 on a T3 elite: under half a phase at T1–T2 (28–44 HP per phase), about a third at T3."
- Fix 3: `enemy_hp_pct = −15` applies to **max HP at create_combat**; R3 floors are computed from the reduced max.
- Fix 4: change choice 2 to `enemy_resistance_delta = −1` (1 combat) **or** `enemy_damage_pct = −10` (2 combats), not both. Or add `cycle_cost: 15`. Choose: split into 1 combat of both, +2 Heat. Choice 1: `reveal_phases` plus `bonus_free_nudges = 1` plus `enemy_hp_pct = −10`, the next 1 combat of any class.
- Fix 5: retag `reveal_phases`, `bonus_free_nudges` and `enemy_starts_frozen` to N16 (new override fields); reveal needs N5's Chart Hidden only to counter it.

## Keep
- The three-way split of quiet, loud and paid edges has a clear, readable tradeoff.
- Overrides saved in run state and applied at `create_combat` keep previews equal to results.
- Choice 3's HP cost against conditional payoff is a good risk shape.

## Q:
- Should overrides show as map chips (recommended, since the tradeoff depends on knowing the target)?
- Do stacked overrides from several events sum additively, or cap per field?
