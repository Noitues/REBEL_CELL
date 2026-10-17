<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__18_ambush_rebel_cell; status ok; tokens in 3593 cache-write 0 cache-read 32585 out 1589; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/18_ambush_rebel_cell
**Verdict:** FIX

## Issues
1. **BLOCKER, Template / N16 (stake + overrides).** Choice 1 invents `player_start_ram` and `heat_on_start`, which exist nowhere in N16 (`combat_overrides` is only listed as a field). The "-2 RAM" and "+2 Heat on start" are unbacked, and the Heat on start stacks with the +4 on loss.
2. **BLOCKER, Arithmetic / tier.** The notes say "At T2 a normal at T3 strength (44-56 HP)", yet min_tier is 2, so +1 delta gives T3 at T2 but T4 at a T3 run. The T4 normal band is 56-70, not 44-56. The "85-90 % win" claim has no basis and ignores the −2 RAM. The HP-loss average of "10-15" is unsourced.
3. **MAJOR, Choice 3 / systems.** The `cell_informant` add-in is left in as a "No:" self-correction, which is unfinished text. A "+10 % enemy damage factor" breaks R2 (tier sets base values; buffs are tier-independent, but there is no ruled per-combat damage rider). It is also not a listed override.
4. **MAJOR, Choice 2 / determinism.** The Firmware is "one random drawn from the events RNG stream" while the effects line shows no reward-pool field. Heat +1 plus 15 Cycles for a common Firmware makes it a safe default, so choice 1 is only for operative seekers.
5. **MAJOR, Choice 1 / stake.** A rookie is valued at "15 Schematics" at HQ, but the event also grants 20 Cycles and a Daemon fallback. The fallback is a bigger reward than a rookie, creating a perverse incentive when the roster is full. The loss stake (12 HP, floor 1, +4 Heat) is the only downside, and it means a loss costs the same as a skipped event plus 12 HP.
6. **MAJOR, Fallback.** The stated data-only fallback ("costs 12 HP, 50 % operative via events stream") drops the combat entirely and does not match the AMBUSH family. Say instead: if N16 is absent, hide the event.
7. **NIT, Template.** `result_text` is under 3-5 sentences in places, there is no `heat_effects` mention, and text keys are listed as "five result strings" but only four are named. Choice 1 also says "reward" twice.
8. **NIT, `handler_proxy` is a normal at tier 2+.** It is in the allowed list, but "mirror-grade handler" in the one-liner overstates it.

## Concrete fixes
- **Overrides (1, 2):** replace with N16-only fields: `starts_combat: {enemy: handler_proxy, combat_overrides: {tier_delta: +1 (cap T4)}, stake: {on_loss: hp_damage 12 (floor 1), heat +4}, reward: {on_win: rescued_operative or Daemon if roster full, gain_cycles 20}}`. Cut RAM and the start Heat. Fallback: if `tier_delta` is unsupported, use plain `handler_proxy` at the run's tier.
- **Notes arithmetic:** "Tier delta +1: a T2 run fights a T3 normal (44-56 HP, 3-4 turns); a T3 run fights T4 (56-70). Estimated loss 8-14 HP per fight, win rate to be set by the sim."
- **Choice 3:** `next_combat_overrides: {enemy_damage_pct: +10, duration: 1 combat}`. Mark it "NEW: combat rider (N16 extension)" or replace it with `MODIFY_HEAT +3` and a −1 shop-stock modifier (existing `SHOP_STOCK`, 1 node). Delete the "No: simpler" sentence.
- **Choice 2:** `reward: Firmware, common pool (events stream, checkpointed)`, with cost raised to 20 Cycles so it doesn't dominate.
- **Fallback line:** "If N16 is not built, hide the event (weight 0)."

## Keep
- The three-way choice (fight, pay, sell) with a morally gray sell.
- The roster-full fallback concept and the capped loss (no operative death).
- The `handler_proxy` pick as a normal that keeps R1's 3-4 turns.

## Q:
- Q: Is the rescued rookie worth more than the sell-out's 35 Cycles plus Heat, given Schematics pricing?
- Q: Should `tier_delta` apply to the enemy's `hp_by_tier` band and damage factor both?
