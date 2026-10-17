<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__nodes__cache; status ok; tokens in 6981 cache-write 0 cache-read 32585 out 1998; cost $0.020. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: nodes/cache

**Verdict:** FIX

## Issues

1. **BLOCKER, determinism / §2 layout rule vs §3 RNG.** "The jackpot is never adjacent to the start position… the generator picks a start rotation" conflicts with "the full outcome is a pure function of start rotation, layout…" and with the forced tutorial start. The rule is also internally broken: "free nudge = reachable for one slice distance only, so a jackpot 2 slices away costs 1 paid nudge." A jackpot "never adjacent" is at distance 2 or 3 on a 6-ring, which costs 1 or 2 paid nudges. Example 2 (Firmware adjacent to the start, "free") also violates the rule that the best slice is never adjacent. The rule is a constraint on layout and start, but it is never stated as one, and the draw is not defined (which draw, over which candidate set).
2. **BLOCKER, §2 nudge budget.** "cache_max_nudges = 3 (1 free + 2 paid)", yet the nudge is ±1 slice with the ring wrapping. Distance 3 is reachable with all 3 nudges, so the cost the player pays is arbitrary. Example 1 says "pay +2 Heat to take two steps further": that is two nudges, which makes 1 free + 1 paid = 2 steps total. The text implies the paid nudge covers two steps. The arithmetic is inconsistent.
3. **MAJOR, config keys.** §2 lists `cache_extra_nudge_cost` as the cost, but the key list names `cache_extra_nudge_heat` and `cache_extra_nudge_hp_pct`. `cache_run_chance`, `cache_trip_cannot_kill` and the reward amounts are missing from the list.
4. **MAJOR, systems.** N17 is "event wheel", which uses `EventWheelData` and nudge budget. The draft redefines N17 ("this draft fixes N17's spec") and then adds `CacheData` and `CacheSliceData`, duplicating `EventWheelData`. "N14/N1: amount modes" mislabels N14 (the defense trio). `InfilNodeType.CACHE` is a new enum value, but the "NEW:" tag is given to the node type without the DECISIONS check (D4 allows Cache, with the puzzle "vetted first"). The N16 and N18 `slice_flash` dependencies are not noted. The `seen_cache` profile flag is a new profile field, untagged.
5. **MAJOR, §5 "Death".** The trip damage is capped to leave 1 HP and is also PERCENT of max HP. The draft does not say whether this applies to R3-style loss paths. It's fine, but the HP-attrition effect compounds across layers (20 % heal is offset by a 15 % trap).
6. **MAJOR, design quality.** Heat variant: paid nudges cost +2 Heat and HEAT_DOWN gives −2, so the best case is net zero. HEAT_DOWN is a dominated slice, and EMPTY is strictly worse than LEAVE. TRIPWIRE next to the start is always avoided by LEAVE, so the draft needs a reason to never LEAVE (it doesn't have one besides the free nudge).
7. **NIT, §3.** "Never replaces… Rack layer slot" and "shares the Terminal share" conflict with the 25 % Terminal guarantee; state it explicitly. "None on a boss-only path" has no definition.
8. **NIT, spelling/format.** US spelling is correct. Section 4 mentions "Free turns" where §2 says nudges.

## Concrete fixes

- **#1/#2:** Replace the layout rule with: "Authored layouts have exactly one JACKPOT. The start is drawn from `events` among the slices at ring distance 2 or 3 from the JACKPOT and never on the TRIPWIRE. The jackpot therefore costs 1 paid nudge (distance 2) or 2 (distance 3); budget `cache_max_nudges` = 3 covers both." Fix Example 1 to "free nudge, then 1 paid nudge (+2 Heat)". Fix Example 2: put FIRMWARE (the JACKPOT) 2 slices from the start.
- **#3:** Replace the key list with `cache_free_nudges`, `cache_max_nudges`, `cache_extra_nudge_heat` = 2, `cache_extra_nudge_hp_pct` = 0.05, `cache_trip_hp_pct` = 0.15, `cache_trip_heat` = 3, `cache_run_chance` = 0.6. Delete `cache_nudge_ticks` (fixed at 5 ticks per slice) and `cache_extra_nudge_cost`.
- **#4:** State: "Cache = a consumer of N17. `CacheData` is an `EventWheelData` row with `step_nudge`, `cost_variant`, `layout`." Change "N14/N1" to "N1". Add the fallback: the Terminal three-choice event, as already written.
- **#6:** HEAT_DOWN becomes −4 in PAY_HEAT caches (net +2 against a paid nudge) or is removed there. Replace EMPTY with a smaller CYCLES 10.

## Keep

- Slice-only, no-tier, no-RAM reads separate the Cache from combat, and the visible layout keeps preview = result.
- The checkpointed `events` draw with a forced tutorial start is deterministic and teaches nudging.
- Free LEAVE, the TRIPWIRE that cannot kill, and one cost currency per Cache.

## Q:
Q: Should the layout be hidden for the first Cache, or fully visible always?
Q: Does LEAVE need a cost to stop skipping Caches with a TRIPWIRE near the start?
Q: Is Heat a good cost, given Heat objective Sites reduce it?
