<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__15_ambush_meridian; status ok; tokens in 3562 cache-write 0 cache-read 32585 out 1625; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/15_ambush_meridian

**Verdict:** FIX

## Issues

1. **BLOCKER, template / N16 fields.** Choice 2 invents `enemy_phase_skip` and `starting_hp_pct`, and choice 3 uses `replace_enemy` with `tier_delta`. The brief allows only "a named existing enemy, a tier tweak, a stake and a reward." Phase skipping is also barred by R1 (elites are 2 phases, and parking cannot be skipped).
2. **BLOCKER, economy / dominated choice.** The voluntary fight at tier-1 pays +45 Cycles, a Firmware choice and −2 Heat. Signing costs 20 Cycles and +4 Heat. Any operative with moderate HP fights (it is also a rewind-safe deterministic fight), so Sign is dominated. Refusing and fighting is also a "free" Heat reduction. The notes say "the fight is dominated only if you can't afford the HP", which concedes that Sign is only the broke-run option.
3. **MAJOR, choice 3 is a trap.** It costs 8 HP and no reward, and it defers a +1 tier Enforcer with no bonus. That is strictly worse than choice 2 in every way except the HP timing. It also contradicts the notes' claim that it "defers a worse fight". Nothing offsets the tier+1 fight, and it is conditional on an Elite Router existing (silently dropped otherwise), so the real cost is unclear to the player.
4. **MAJOR, label arithmetic.** The Choice 1 header says "-15 Cycles/ +Heat" but cycle_cost is 20. The "65 Cycles of swing" figure holds only if Heat is ignored (45 + 20 = 65, but Heat swings 6 on top).
5. **MAJOR, no stake on voluntary fight.** "No HP restored, no flee" is just default combat. There is no stake that differs from signing, such as a loss consequence beyond death.
6. **NIT, template / mechanic.** An "ambush" that the player chooses to start contradicts the ruling "Ambush: no as a node; maybe as an event option," so this is acceptable only as an option. The text says "scanning against a bounty list", but the contract flavor and result text never mention that a refusal-fight is optional.
7. **NIT, pacing.** The draft gives no fight length. Last-Mile Enforcer is a 132 HP elite at T3, so at tier 1 (T2−1) the R2 elite band is 56–72 HP and must use `hp_by_tier` (N2). Say so.
8. **NIT, text.** `dispatch_clue: false` and an empty `foreshadows` are fine. "Last-Mile jacket" is consistent with the corp.

## Concrete fixes

**1, 3 (choice 2 and 3 overrides):**
- Choice 2 `starts_combat`: enemy `last_mile_enforcer`, `combat_overrides: {tier_delta: -1}` only. Delete `enemy_phase_skip`, `starting_hp_pct`. State: enemy HP from `hp_by_tier` (N2), 2 phases.
- Choice 3 `next_combat_overrides`: `{enemy_id: last_mile_enforcer, tier_delta: 0, consumes: next Elite Router, expires: netrun end, converts: if none exists, the next Router}`. Add reward +25 Cycles so it pays for the risk.

**2, 5 (rebalance):**
- Sign: cycle_cost 25, MODIFY_HEAT +6.
- Fight: reward 35 Cycles + Firmware choice (1 of 3), no Heat change. The stake is "on win, +2 Heat (the courier files a loss report)". This makes the fight a Heat-for-Firmware trade against Sign's Cycles-and-Heat price.
- Sneak: hp_cost 8, deferred fight at the run tier, reward 35 Cycles + the same Firmware choice. The player takes the same fight later for a smaller up-front price and a fixed cost in HP.

**4:** Change the choice 1 header to "Sign it (-25 Cycles, +6 Heat)" and recompute the notes' swing: 35 Cycles + Firmware against 25 Cycles + 6 Heat.

## Keep
- The contract-as-trap framing is original and fits Meridian.
- Determinism via a stored `next_combat_overrides` in run state is correct.
- Showing the "may be dropped" case in a tooltip is a good readability call.

## Q:
- Q: Should a deferred ambush that finds no Elite Router convert the next Router, or fizzle?
- Q: Is Firmware as a combat reward consistent with the data-driven rewards list (N18) rather than a fixed event reward?
