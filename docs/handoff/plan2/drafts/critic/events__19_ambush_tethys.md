<!-- draft via Message Batches API, claude-sonnet-5-5, batch msgbatch_012ieKaHm8j2yMaAfRN1Wf8G, custom_id critic__events__19_ambush_tethys; status ok; tokens in 3404 cache-write 0 cache-read 32585 out 1651; cost $0.015. A DESIGN DRAFT for the designer's review: nothing here is built. -->

# critic: events/19_ambush_tethys

**Verdict:** FIX

## Issues

1. **BLOCKER, template/ids:** `corporation_id: tethys` and the enemies `last_mile_enforcer` and `customs_scanner` are Meridian enemies. The ids were supposed to come from the list given. Tethys has no enemy ids in the inventory, and the draft doesn't say whether the fight is meant to be a cross-corp ambush. This reads as an invented or mismatched pairing, and the text ("retrieval unit", "collector") doesn't match either enemy.
2. **BLOCKER, R1/R2, Choice 1 elite:** "tier tweak −1 (min 1) so it fights as a fresh elite" is incoherent. A tier tweak changes the starting HP and damage, not the phase count. The Last-Mile Enforcer is a 2-phase elite, with its 132 HP at T3 as today's value. R2 sets elite HP at T1 56–72 / T2 68–88. The draft never says which tier applies at min_tier 2, and it doesn't show the phase budget arithmetic. "T2-adjacent band" is vague.
3. **MAJOR, R2, start block:** "+8 flat, tier-independent" contradicts "scaled by the enemy damage factor at that tier" in the same draft. R2 says flat enemy amounts are multiplied by the tier damage factor. It also isn't in Rule R5 format (amount_mode FLAT).
4. **MAJOR, template, Heat and Cycles:** `MODIFY_HEAT` and `GAIN_CYCLES` are quoted as "type 21 / type 22, target 6". Counting the enum from 0, MODIFY_HEAT is 21 and GAIN_CYCLES is 22, so those are right. The use as on-entry and victory-branch effects has no field though (see Q1). Heat +2 on entering a fight is also a stake the preview should show.
5. **MAJOR, design quality:** Choice 2 is nearly dominated by Choice 1. It costs 4 HP and −2 RAM for a common card and 15 Cycles. Choice 1 is a Firmware plus 30 Cycles for +2 Heat and the elite risk. The note calls Firmware "the strongest reward", but nothing offsets the elite risk. Choice 3 is a flat tax with no upside, so it's a pure loss unless the player fears death.
6. **MAJOR, text consistency:** Choice 2's label says "Daemon-fragment card", but the reward is a common block card, "Pressure Valve". The result text says "A cheap card drops out". The "ambush follows" fight is a collector, and `customs_scanner` is a Meridian normal. "RAM −2" for the fight start is an invented override with no system tag (a combat_overrides field under N16, but not listed).
7. **NIT:** The text keys list shows no key for the fight stake or preview lines. The speaker is given as "NARRATOR (0)". Spelling is US ("equalizes").

## Concrete fixes

- **Ids:** Either set `corporation_id: any` and keep the Meridian enemies, or use a real Tethys enemy id. Add "cross-corporation ambush: couriers are contracted out" to the text. A text line like "A Meridian-marked retrieval unit surfaces behind the sled." would justify it.
- **Choice 1 overrides:** `combat_overrides: {tier_offset: 0 at T2 (enemy fights at the Grid's tier), enemy_start_block: 8 FLAT (× tier damage factor 1.3 = ≈10)}`. State the HP honestly: "Last-Mile Enforcer, 2 phases, T2 band 68–88 HP, ≈ 3.5 turns per phase, ≈ 7 turns."
- **Rebalance:** Choice 1 reward Firmware only, Cycles +15, Heat +2. Choice 2 reward card + 15 Cycles, hp_cost 4, no RAM override (drop it), and `customs_scanner` as a 1-phase normal (T2 34–44 HP, ≈ 3.5 turns). Choice 3: cost 15 Cycles, and add reward −1 Heat ("voided claim, traceable record wiped").
- **Choice 2 label:** "Pry it open and run (+1 card, collector follows)".

## Keep

- The setup is clean: the sled and the "SIGNATURE VOIDS DEPTH LIABILITY" line carry the noir tone.
- It is deterministic, with fixed enemy, overrides and rewards, and a stated data-only fallback.
- Three choices with a safe floor, and the preview of enemy and reward up front.

## Q:
- Should Heat on entering a fight apply even if the player dies in it?
- Is a cross-corporation enemy in an event allowed, or must it match `corporation_id`?
