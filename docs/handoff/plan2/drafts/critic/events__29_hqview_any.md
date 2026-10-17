<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__29_hqview_any; status ok; tokens in 3766 cache-write 0 cache-read 32585 out 1788; cost $0.016. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/29_hqview_any

**Verdict:** FIX

## Issues

1. **BLOCKER, template/R1-R13 (choice 4 stake): a corp-neutral event spawns a Meridian enemy.** The draft calls `tariff_collector` "corp-neutral enough". It carries a corporation identity and Meridian scaling, and the event is `any`. The fight also says "tier = the operative's next netrun tier" and "no tier scaling beyond the base", which contradicts itself. R2 says tier sets base values only.
2. **BLOCKER, arithmetic (wheel): the sub-tick text is wrong.** The sizes 10 + 12 + 8 = 30 do add up. But "a Salvage 10-tick slice reads W W G G G P..." is not the R11 default map. R11 only defines sizes 2-7. Sizes 8, 10 and 12 need an authored `tick_quality` map, and none is given. The claim that the 8-tick slice has the "narrowest Perfect" is unsupported, since a centre-distance map gives every size one Perfect tick.
3. **MAJOR, determinism and design (wheel): the wheel sits on top of fixed effects and the player can pay to buy the best slice.** Choice 1 pays +10 Schematics and +4 Heat before the wheel. The Salvage nudge is a pure Cycle sink with a known result. Choice 1 uses an `events` RNG pointer, but the "Expectation" arithmetic ignores that the nudge makes the outcome deterministic. The sunk 5-Cycle cost is not shown against Salvage's +30. Salvage is not a gamble once the pointer is nudged: at most 3 nudges for 15 Cycles buy +30.
4. **MAJOR, dominance (choice 2 vs the rest):** The draft says choice 2 is "almost strictly better in value". The numbers back that up: +20 Cycles plus a Firmware for 6 HP, which heals at HQ per GDD 4.2 ("survivors heal fully at HQ"). HP cost at HQ is effectively free, so choice 2 dominates 1 and 3. The "fragile class" argument fails because the HP is restored.
5. **MAJOR, rewards:** Choice 2 grants "one random common Firmware" with `events` RNG. The draft doesn't say whether this is a checkpointed stream draw. It also doesn't tell the designer when the roll happens. Choice 4's loss rule ("fight ends at 1 HP", "no death") is a new stake rule with no N# beyond N16, and it never says whether HQ-view HP matters.
6. **MAJOR, systems tagging:** `event_wheel` should be tagged N17 and `starts_combat` / `next_combat_overrides` N16. N12 is needed for the 8, 10 and 12-tick sizes. None of these tags appear. No data-only fallback is stated.
7. **NIT:** The text says "The Cell hasn't ordered anything in weeks", and the Q about a netrun slot is unresolved. Choice 2's label says "stationed operative" while the hp_cost says "the operative who would next launch". Choice 3's "itch in the back of your neck" is flavor with no mechanic.

## Concrete fixes

- **Fix 1:** Replace `tariff_collector` with an enemy id the designer picks from the provided list, or use the Solace id the designer approves. Set "Overrides: none; tier = the Site-tier of the operative's next netrun, base values from R2 tables."
- **Fix 2:** Author the maps:
  - Salvage 10: `tick_quality` = W W G G G P G G W W (centre tick P)
  - Dud 12: W W W G G G P G G G W W
  - Tracker 8: W G G P G G W W (the centre P is at tick 3)
  - Drop the "narrowest Perfect" claim. Tag N12 and N17, fallback: three 10-tick slices on the existing 5-tick-slice kit.
- **Fix 3:** Make nudges cost 5 Cycles each, with the first free capped at ±1. Add: "the Salvage slice is worth +30 at ≤15 Cycles in nudges". Alternatively remove the paid nudge and keep only the free one.
- **Fix 4:** Make choice 2 cost real: "−6 HP and that operative is unavailable for this netrun (rest this cycle)". Or drop the Firmware to a 50 % chance.
- **Fix 5:** State "Firmware draws from the `events` stream at a checkpoint".
- **Fix 6:** Add N# tags: `event_wheel` N17, `starts_combat` / `combat_overrides` / `next_combat_overrides` N16, wheel sizes N12. Fallback for choice 4: a fixed Heat toll instead of a fight.

## Keep

- The one-line decision frames four different resources.
- The Heat-driven "leave it" option and the Daemon-for-Cycles fight give a real spread of risk.
- Text keys and the sign-off on preview equality are in place.

## Q:

- Q: Should HQ-view events be allowed HP costs, given operatives heal fully at HQ?
- Q: Is the impromptu HQ fight allowed to give a Daemon, or is that reserved for Racks?
