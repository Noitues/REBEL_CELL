<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__01_future_solace; status ok; tokens in 3667 cache-write 0 cache-read 32585 out 1619; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/01_future_solace
**Verdict:** FIX

## Issues
1. **MAJOR, R2/R3 (HP bands, threshold parking):** Choice 2's `enemy_hp_pct = -15` "bypasses the R2 band validator" and uses a "floor of 1 per phase". R3 parking uses the HP floor ceil(max HP × next threshold). A raw max-HP cut is undefined against the thresholds. It also mislabels the interaction in Design notes ("stacks with R2 band checks"). It must state that the cut changes max HP before the floors are computed, and that the validator reads the authored `hp_by_tier`, not the run override.
2. **MAJOR, effect strength and economy:** Choice 2 is probably dominant. It applies to 3 fights, so it is roughly 3× the value of Choice 1. The notes say "half a phase on a normal, ~0.5 turns", but a normal has 1 phase of 3–4 turns, so −15 % HP is about 0.5 turns. That saves about 1.5 turns across 3 fights at a cost of 6 HP and 2 Heat. Resistance −1 is also free value. The cost is small against a 45–60 HP run, and the notes admit it.
3. **MAJOR, Choice 1 is nearly worthless:** the Freeze rule means "skip its next start-of-turn respin". At fight start the wheel has just been placed, and the Freeze skips only one respin. The draft doesn't say which respin. It also doesn't say that Freeze fails against Compliance Lock-style resistance. That claim is wrong: GDD 2.5 lists Freeze with no resistance clause, so the note is unverified.
4. **MAJOR, Choice 3 vs R4 and `reveal_phases`:** `player_extra_free_nudges = 1` is not a listed N16 field, only an example ("a free nudge"). Reveal on a normal (1 phase) has nothing to reveal. Choice 3 is dead if the next node is a normal.
5. **MAJOR, "Choice 4" heat:** `MODIFY_HEAT −1` makes the decline strictly better than Choice 1 whenever the next fight is easy. The "no dominant option" claim fails.
6. **NIT, Design notes, 450–900 words:** the "Odile" text is fine, but `dispatch_clue: false` with `foreshadows &""` is acceptable. The text has 5 sentences, within the template limit.
7. **NIT:** the text uses "leash reinstated" (lexicon, good). The enum `STREET_MERC` is correct.
8. **NIT, systems:** every override is tagged "(new)" but not N16 or a data-only fallback. `next_combat_overrides` is N16, which depends on N2. No fallback is stated; the Freeze and resistance deltas could use existing effects at combat start.

## Concrete fixes
- **Issue 1:** replace the override line with: `enemy_hp_pct = -15 (rounds up, min 1; applied to max HP before the R3 floors are computed; thresholds stay fractional; validator reads authored hp_by_tier only)`.
- **Issue 2:** reduce Choice 2 to `enemy_hp_pct = -10`, `duration 2 combats`, `hp_cost 8`, `+2 Heat`. Remove the free resistance delta, or make it elite-only.
- **Issue 3:** `enemy_wheel_frozen = true` becomes `FREEZE on the enemy wheel at combat start (skips the turn-1 respin; the player sees the layout with the pointer already placed)`. Add `+1 free nudge on turn 1` for value.
- **Issue 4:** `reveal_phases = true` becomes `(elite or mini-boss only; normals: 15 Cycles refunded)`. Alternatively: `player_extra_free_nudges = 1` for the next 2 fights, `cycle_cost 10`.
- **Issue 5:** change Choice 4 to `MODIFY_HEAT 0` and add `reward: +5 Cycles`, so the decline is neutral.
- **Issue 8:** add this line to Design notes: "Depends on N16 (N2). Data-only fallback: apply FREEZE and MODIFY_RESISTANCE through existing ON_COMBAT_START effects on a run Daemon."

## Keep
- A strong noir hook: Odile and the "favor owed" frame fit the Solace voice.
- The counting rule (completed fights, not nodes visited) and the determinism note are clear and correct.
- The four-choice structure includes a genuine hedge (Choice 3).

## Q:
- Q: Should HP cuts exclude mini-boss and Rack fights?
- Q: Do overrides end when the netrun ends (proposed yes)?
