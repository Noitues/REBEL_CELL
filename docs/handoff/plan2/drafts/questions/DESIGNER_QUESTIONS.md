# Designer questions (round 3 extraction)

729 raw questions from 220 drafts, grouped into 655 decisions (same decision across drafts = one entry, sources listed). Extracted by Haiku, grouped by `tools/batch/merge_round3.py`. Order: area, then most-raised first.

## balance

1. **citation targeting** (3 drafts): Should Citation target the slice under the pointer (readable) rather than a random one (a preview-equals-result risk)?
   - also: Should Citation target a random slice or the slice under the pointer (more readable, less variance)?
   - also: Should Citation's OUTPUT_DOWN ×2 hit the slice under the player's pointer instead of a random one?
   - sources: [enemies/cell_informant](../enemies/cell_informant.md), [enemies/permit_office](../enemies/permit_office.md), [enemies/surveillance_mast](../enemies/surveillance_mast.md)
2. **drain scaling by tier** (3 drafts): Should the Priority RAM drain scale by the tier factor (2, 3, 3, 4) or stay flat at 2, since RAM is a player resource?
   - also: Should the orbit step scale (2, 3 at T3+) as a base value, or stay fixed tier-independent?
   - also: Should RAM drain scale with tier at all? Proposed no (flat), since RAM income is fixed at +4.
   - sources: [enemies/conveyor_warden](../enemies/conveyor_warden.md), [enemies/surveillance_mast](../enemies/surveillance_mast.md), [enemies/tariff_collector](../enemies/tariff_collector.md)
3. **class specific upgrades** (2 drafts): Does Phantom class get the same upgrade or a class-specific one?
   - also: Do Overclocker and Rigger need different + upgrade choices, given Overclocker's inner-ring focus?
   - sources: [card_upgrades/blind_spot](../card_upgrades/blind_spot.md), [card_upgrades/ring_tap](../card_upgrades/ring_tap.md)
4. **drone hp scaling** (2 drafts): Should drone HP scale with tier (flat 4, or × damage factor) so SWEEP doesn't trivialise T1 and T4 alike?
   - also: Does the drone's HP use the tier damage factor, or is it a fixed 6 so a single Shim 9 always kills it?
   - sources: [enemies/care_swarm](../enemies/care_swarm.md), [enemies/dead_drop](../enemies/dead_drop.md)
5. **late fee scaling** (2 drafts): Should Late Fee scale as a PERCENT of max HP or stay FLAT × tier factor?
   - also: Should the Tag be flat 4 or a percent share of max HP (so it does not scale with tier)?
   - sources: [enemies/billing_daemon](../enemies/billing_daemon.md), [enemies/recall_unit](../enemies/recall_unit.md)
6. **lock failure penalty** (2 drafts): Should the Lockkeeper's turn limit be a hard fail (the Head is set to HIGH) or a softer penalty, given that the HQ boss's own enrage is also a turn clock?
   - also: Should a lost lock cost the operative anything permanent (HP only, or a possible death), or only deny the removal?
   - sources: [hq/tethys](../hq/tethys.md), [sync_strike/strike](../sync_strike/strike.md)
7. **overflow damage** (2 drafts): Is a 14-damage Overflow on a 4-tick slice (never Perfect, so a flat 14 or 7) too swingy for L1-2 teaching? Would 12 be safer?
   - also: Should the Overflow keep a 14 base at T4, where the pair hits for about 48, or should a normal's biggest hit be capped?
   - sources: [enemies/cargo_hauler](../enemies/cargo_hauler.md), [enemies/route_optimizer](../enemies/route_optimizer.md)
8. **percent heal cap** (2 drafts): Do Tethys PERCENT shields need their own cap? Sea Wall at HIGH is 20 (P1) / 24 (P3), more than player's cap of 15.
   - also: Does the PERCENT heal need a per-resolution cap (proposed 30 % max HP) on the player side, like `shield_cap`?
   - sources: [bosses/tethys](../bosses/tethys.md), [slice_upgrades/hotfix](../slice_upgrades/hotfix.md)
9. **rest firmware swap cost** (2 drafts): Does a Rest Firmware swap cost anything, or limit swaps per visit?
   - sources: [gdd/s04](../gdd/s04.md), [gdd/s06](../gdd/s06.md)
10. **run length target** (2 drafts): Is a 30 to 36 minute HQ run acceptable, or should the Circus be capped near 25 minutes by dropping a ring?
   - also: Run length: acceptable at 50-55 minutes, or cut to ~7 steps to match normal run length?
   - sources: [hq/aurelian](../hq/aurelian.md), [hq/rebel_cell](../hq/rebel_cell.md)
11. **seed cap interaction** (2 drafts): Should the + version also raise `shield_cap` for the turn, or is the cap of 15 sacred?
   - also: Does Botnet Seed (1-HP drones) stack with Level III-a's 2-drone deploy past the cap?
   - sources: [card_upgrades/shield_wall](../card_upgrades/shield_wall.md), [slice_upgrades/trojan](../slice_upgrades/trojan.md)
12. **upgrade depth** (2 drafts): Is a single "+" level enough, or does Inner Drift also get a second level that reaches 4 ticks?
   - also: Should the upgrade also lower the self-damage (4 → 3) at a later level, or is a one-level pass enough?
   - sources: [card_upgrades/inner_drift](../card_upgrades/inner_drift.md), [card_upgrades/overload](../card_upgrades/overload.md)
13. **alert floor severity** (1 draft): Is the Alert floor on retry (Alert 1 per death) too harsh or too soft?
   - sources: [hq/halcyon](../hq/halcyon.md)
14. **aurelian phase questions** (1 draft): For Aurelian Concord's phase questions (R1), should each phase impose a specific mechanical question or only narrative variety?
   - sources: [gdd/s08](../gdd/s08.md)
15. **backspin role post upgrade** (1 draft): Does Backspin remain a reward-pool card once Heavy Spin+ exists, or does it become the base upgrade path?
   - sources: [card_upgrades/heavy_spin](../card_upgrades/heavy_spin.md)
16. **base card swap behavior** (1 draft): Should SWAP be the base card's behavior too, once REPLACE can destroy a player's own drone?
   - sources: [card_upgrades/undock](../card_upgrades/undock.md)
17. **bench absorption death risk** (1 draft): Does a benched operative's HP pay for absorbed hits, risking a permanent death off-screen, or is the bench absorption capped at their HP floor of 1?
   - sources: [sync_strike/strike](../sync_strike/strike.md)
18. **block cap scope** (1 draft): Does the 25% BLOCK cap per landing apply to enemy BLOCK as well?
   - sources: [slice_upgrades/defrag](../slice_upgrades/defrag.md)
19. **block scaling balance** (1 draft): Should enemy-side tier-scaled BLOCK values compete with this design?
   - sources: [card_upgrades/bulwark](../card_upgrades/bulwark.md)
20. **boss high ice length** (1 draft): Is the high-ICE boss length acceptable (≈23 turns at 530 band), or should top band cut P1–P2 HP to keep P3–P5 and spend extra length on late phases?
   - sources: [bosses/tethys](../bosses/tethys.md)
21. **boss immunity to overrides** (1 draft): Does the Frozen start apply to a boss-class enemy, or should bosses and mini-bosses be exempt from choice 1?
   - sources: [events/03_future_halcyon](../events/03_future_halcyon.md)
22. **boss winrate target** (1 draft): Boss win-rate target at ICE 0 (baseline 25 % fresh, 8 % in campaigns).
   - sources: [gdd/s13](../gdd/s13.md)
23. **breaker double resolve perfect stacking** (1 draft): Does the Breaker's Perfect hook (resolves twice) apply the Perfect bonus on both resolves?
   - sources: [firmware/overvolt](../firmware/overvolt.md)
24. **breaker perfect loss** (1 draft): Should the Level II no-Perfect penalty be softened for classes whose hook depends on Perfect (Breaker), for example by giving Breaker's wheel a hook variant that triggers on a 4-tick Good?
   - sources: [slice_upgrades/overflow](../slice_upgrades/overflow.md)
25. **breaker version necessity** (1 draft): Is Breaker's +1 spin bonus (7) enough to want a separate Breaker version, or is the neutral+ fine?
   - sources: [card_upgrades/brute_spin](../card_upgrades/brute_spin.md)
26. **buffer endofraid conversion** (1 draft): Should Buffer end-of-raid conversion be capped at missing integrity, or may it overheal the node?
   - sources: [station/rigger](../station/rigger.md)
27. **bulkhead redundancy** (1 draft): Should Bulkhead be raised to +60% on DEFRAG/SANDBOX so it keeps a niche, or retired as redundant?
   - sources: [firmware/patch_plus](../firmware/patch_plus.md)
28. **buys per visit count** (1 draft): Is one buy per visit too tight when upgrades are the only permanent in-run growth? Would two buys at 1.5× cost be better?
   - sources: [nodes/workshop](../nodes/workshop.md)
29. **calibrate plus deep calibrate overlap** (1 draft): Is the + version too close to Deep Calibrate? Should it instead keep 2 free nudges and gain only the corruption relief?
   - sources: [card_upgrades/calibrate](../card_upgrades/calibrate.md)
30. **calibrated interaction** (1 draft): Is the Calibrated restriction (sizes 4–7 only) acceptable, or should IV-A's multiplier be capped when Calibrated is socketed?
   - sources: [slice_upgrades/overflow](../slice_upgrades/overflow.md)
31. **calibrated size cap scope** (1 draft): Should Calibrated cap at size ≤ 4 for all classes, or only for classes with Perfect hooks?
   - sources: [firmware/new_chips](../firmware/new_chips.md)
32. **calibrated stacking** (1 draft): Should Calibrated stack with itself, or is a Level III slice the way to reach ×2 tier raises?
   - sources: [gdd/s06](../gdd/s06.md)
33. **class alternative bonuses** (1 draft): Do class alternatives keep a unique station bonus too, even where the core differs only slightly?
   - sources: [gdd/s03](../gdd/s03.md)
34. **clean slate balance** (1 draft): Does Clean Slate (1.5× corrupted RAM) undercut the corruption design (R9), and should it be a Level I-IV result instead of a Daemon?
   - sources: [gdd/s06](../gdd/s06.md)
35. **cleared dishes boss buffs** (1 draft): Should cleared dish stations disable boss buffs one-for-one (D5-linked), or is that too much overlap with the Exploit draw (R7)?
   - sources: [hq/orbital](../hq/orbital.md)
36. **climb frequency cap** (1 draft): Should climbs be limited to one per run to keep long routes meaningful?
   - sources: [hq/halcyon](../hq/halcyon.md)
37. **corrupted skip perfect landing** (1 draft): Should the + also skip the burn-out into CORRUPTED when the slice lands Perfect?
   - sources: [card_upgrades/hot_patch](../card_upgrades/hot_patch.md)
38. **corruption cap** (1 draft): Should CORRUPTED cap at a share of the wheel (e.g. at most 3 of 5 non-NULL slices) so a 4-turn fight cannot fully lock a player?
   - sources: [enemies/dosage_dispenser](../enemies/dosage_dispenser.md)
39. **counter selection method** (1 draft): Counter source: is most-used Firmware the right basis, or should counter always be seed-chosen to prevent shop gaming?
   - sources: [hq/rebel_cell](../hq/rebel_cell.md)
40. **cycle cost premium** (1 draft): Is a 40% cycle premium right for a cost-only upgrade?
   - sources: [card_upgrades/cold_snap](../card_upgrades/cold_snap.md)
41. **damage buff stacking** (1 draft): Does the +15% enemy damage from "ON FILE" stack with a Heat-based modifier, or does the higher one win?
   - sources: [events/04_future_orbital](../events/04_future_orbital.md)
42. **damped redundancy** (1 draft): Is DAMPED needed alongside TIER_DOWN, or does TIER_DOWN cover the "deny Medicine's Perfect" need?
   - sources: [catalog/status](../catalog/status.md)
43. **debt enemy tier** (1 draft): Can the added debt_due enemy be an Elite at T3+, or always a normal?
   - sources: [events/30_paths_any](../events/30_paths_any.md)
44. **defensive slice type** (1 draft): Should the second Defrag be BLOCK at all, or a SHIELD so a Perfect burst has to chew through something?
   - sources: [enemies/mirror_script](../enemies/mirror_script.md)
45. **defrag difficulty** (1 draft): Should the Defrag slice (4 ticks, no Perfect) read as a "free landing" or be 5 ticks so it can be a Perfect block the player must deny?
   - sources: [enemies/compliance_officer](../enemies/compliance_officer.md)
46. **defrag slice width** (1 draft): Should the Defrag be a 7-tick slice (soft-block, wide) or a 4-tick slice (hard-to-hit)? I chose 7 so the block is easy to dodge-or-feed.
   - sources: [enemies/transit_controller](../enemies/transit_controller.md)
47. **detonate cleanse behavior** (1 draft): Should Detonate also cleanse OVERCLOCKED (so the burn is consumed), or leave it so the player keeps the 1.5× next turn?
   - sources: [enemies/station_commander](../enemies/station_commander.md)
48. **direct lift value** (1 draft): Is ±2 starting RAM and a free first card the right Direct Lift swing?
   - sources: [hq/meridian](../hq/meridian.md)
49. **dish links cap** (1 draft): Do Dish Links need a cap at the netrun level so they cannot trivialise resistance-heavy elites?
   - sources: [hq/orbital](../hq/orbital.md)
50. **dole gift scaling** (1 draft): Should the Dole gift scale with ICE tier, or remain flat +3 RAM at all tiers?
   - sources: [bosses/aurelian](../bosses/aurelian.md)
51. **dose scaling by tier** (1 draft): Should Dose damage 4 scale with tier damage factor or stay fixed to remain a RAM threat at T4?
   - sources: [enemies/collections_agent](../enemies/collections_agent.md)
52. **drone hp budget inclusion** (1 draft): Is the drone's HP counted toward the normal's R2 budget if the player must kill it?
   - sources: [enemies/collections_agent](../enemies/collections_agent.md)
53. **drone positioning scaling** (1 draft): Is a single-slice guard enough of a question for an L5-6 pressure fight, or should the drone dock on Overflow at T3+?
   - sources: [enemies/collections_agent](../enemies/collections_agent.md)
54. **drone spawn frequency balance** (1 draft): Is "launches every turn, max 2" too strong against the free nudge, given the drone's HP is also tier-banded?
   - sources: [enemies/drone_dispatcher](../enemies/drone_dispatcher.md)
55. **dual citation pick modes** (1 draft): Is a normal allowed two different Citation pick modes, or should slice 2 and 6 be merged to keep L1-2 simpler?
   - sources: [enemies/parking_warden](../enemies/parking_warden.md)
56. **dwell cost** (1 draft): Is "at most 2 Dwells, +2 Heat each, may cost the Rack" the right price?
   - sources: [hq/meridian](../hq/meridian.md)
57. **echo damage amount** (1 draft): Is 4 FLAT the right price, or should it scale with the Perfect slice's output (PERCENT of the landed damage)?
   - sources: [enemies/echo_process](../enemies/echo_process.md)
58. **echo damage frequency** (1 draft): Is Echo (5 on every Perfect) too punishing for Breaker and Ghost, whose Perfect hooks are their identity? Should it only fire once per turn?
   - sources: [enemies/rc_template_elite](../enemies/rc_template_elite.md)
59. **echo listener redundancy** (1 draft): Does Echo (25% replay on Perfect) overlap too much with The Handler's Echo listener (50%)?
   - sources: [enemies/dispatch_core](../enemies/dispatch_core.md)
60. **elite encounter quotas** (1 draft): Does the deferred Enforcer (choice 3) count toward the guaranteed Elite per layer, or replace one?
   - sources: [events/15_ambush_meridian](../events/15_ambush_meridian.md)
61. **encrypt plus ram cost** (1 draft): Should the + version cost 2 RAM and carry a third pick, or stay at 1 RAM with Cycle price as balancing cost?
   - sources: [card_upgrades/encrypt](../card_upgrades/encrypt.md)
62. **enemy corrupted penalty** (1 draft): Should a burnt-out enemy slice read at −25% (OUTPUT_DOWN ×1) for one turn, giving the player a reward for letting the overclock land?
   - sources: [bosses/tethys](../bosses/tethys.md)
63. **enemy defense scaling** (1 draft): Do FLAT enemy block and shield also scale by tier, or should shield stay fixed at 5?
   - sources: [enemies/handler_proxy](../enemies/handler_proxy.md)
64. **enemy difficulty tuning** (1 draft): Is a 50/50 pair-of-needles read (only Overflow+Block dangerous) enough for L1-2, or should L1 drop Overflow to 12?
   - sources: [enemies/mirror_script](../enemies/mirror_script.md)
65. **enemy tier cap** (1 draft): Does "tier +1" cap at the run's access tier, or can it reach T4 on a T3 node?
   - sources: [events/17_ambush_orbital](../events/17_ambush_orbital.md)
66. **enrage formula** (1 draft): Enrage steps: additive or compounding.
   - sources: [gdd/s13](../gdd/s13.md)
67. **enrage step stacking** (1 draft): Should the enrage steps compound instead of adding?
   - sources: [gdd/s02](../gdd/s02.md)
68. **event scope global vs local** (1 draft): Do Terminal events that alter future fights apply globally across all remaining corporations, or only within the current run?
   - sources: [gdd/s08](../gdd/s08.md)
69. **exhaust fallback balance** (1 draft): Is the repeatable fallback (no exhaust, Cycle ×2) too strong for a free Perfect? It would let a deck snap every turn.
   - sources: [card_upgrades/lock_on](../card_upgrades/lock_on.md)
70. **exhaust prevention** (1 draft): Does the draw rider push 0-RAM cycling loops, and should Flick+ exhaust to prevent that?
   - sources: [card_upgrades/flick](../card_upgrades/flick.md)
71. **exploit building specifics** (1 draft): Exploit building roster, costs, integrity and per-building effects?
   - sources: [gdd/s03](../gdd/s03.md)
72. **express cost** (1 draft): Is skipping both leg elites acceptable, or should Express require another cost?
   - sources: [hq/meridian](../hq/meridian.md)
73. **favor verdict conflict** (1 draft): Does Favor from VERDICT landings pull the player toward Perfect-hunting in every fight, conflicting with the Rostrum fight's own VERDICT?
   - sources: [hq/aurelian](../hq/aurelian.md)
74. **feather touch plus chain limit** (1 draft): Should the + version be restricted to one use per turn to prevent chaining several copies into unlimited free nudges?
   - sources: [card_upgrades/feather_touch](../card_upgrades/feather_touch.md)
75. **fight lethality target** (1 draft): Is net intake of ~55 HP over the fight (one full operative bar) the intended lethality, or should boss win-rate target force it lower?
   - sources: [enemies/renewal_engine](../enemies/renewal_engine.md)
76. **fine print echo scaling** (1 draft): Should the Fine Print echo be 50 % of the Perfect hit, or a flat +4?
   - sources: [enemies/claims_adjuster](../enemies/claims_adjuster.md)
77. **first fight difficulty assignment** (1 draft): Is a Meridian L1-2 teacher with two needles too hard for a first fight; should Customs Scanner own that role instead?
   - sources: [enemies/route_optimizer](../enemies/route_optimizer.md)
78. **first hit reduction balance** (1 draft): Is a 50 % first-hit reduction too strong against the Genome Core's multi-hit IVs?
   - sources: [slice_upgrades/sandbox](../slice_upgrades/sandbox.md)
79. **fixed drone readability** (1 draft): Do fixed drones on the two attack slices make the fight too static when the player never nudges (bot skill)?
   - sources: [enemies/care_swarm](../enemies/care_swarm.md)
80. **flak anti air tag** (1 draft): Should Flak get a dedicated anti-air tag, or does its 3-shot profile suffice as FLYING counter?
   - sources: [raids/main](../raids/main.md)
81. **flare status type** (1 draft): Should the Flare status be OUTPUT_DOWN ×1, or TIER_DOWN, which fits "tracking loses precision" better thematically?
   - sources: [enemies/tracking_station](../enemies/tracking_station.md)
82. **flash offer guarantees** (1 draft): Should flash offers be guaranteed to include at least one upgrade for the slice type the class is built around?
   - sources: [slice_upgrades/shim](../slice_upgrades/shim.md)
83. **flip resistance bypass** (1 draft): Is "+" enough, or does the Flip need a second level that lifts the resistance block (Compliance Lock counter) at a higher cost?
   - sources: [card_upgrades/mirror_flip](../card_upgrades/mirror_flip.md)
84. **four tick slice redirect** (1 draft): Should Shunt be allowed on 4-tick slices if the neighbor multiplier is cut to 1.0×, as a pure redirect?
   - sources: [firmware/shunt](../firmware/shunt.md)
85. **free nudge tension** (1 draft): Should the ring get its own free detent step each turn, or share the one free nudge with the outer ring?
   - sources: [inner_ring/a](../inner_ring/a.md)
86. **freeze target scope** (1 draft): Is ANY target too permissive for a cheap exhaust card, or should it stay ENEMY with only the cost cut and the satellite rider?
   - sources: [card_upgrades/freeze](../card_upgrades/freeze.md)
87. **gate density cap** (1 draft): Is a three-gate cap per wheel right, given 30 ticks and uneven needles?
   - sources: [rim_gates/gates](../rim_gates/gates.md)
88. **ghost deck overlap** (1 draft): At 1 RAM, does Jam+ cannibalise Feather Touch and Ghost Step in the Ghost deck, and should Ghost Step move to 2 RAM?
   - sources: [card_upgrades/jam](../card_upgrades/jam.md)
89. **ghost heat bonus uniqueness** (1 draft): Is the optional non-raid Heat reduction too close to the Proxy Relay node (−1 Heat per netrun), and should it be dropped?
   - sources: [station/ghost](../station/ghost.md)
90. **heal scaling by max hp** (1 draft): Should heals ever be PERCENT (a share of max HP) on cards, so the same card is worth more to a high-HP operative?
   - sources: [card_upgrades/stim_patch](../card_upgrades/stim_patch.md)
91. **heat in fight cost** (1 draft): Should Heat have an in-fight consequence (e.g. enemy +1 damage after N Burner triggers) so the cost is felt inside a netrun?
   - sources: [firmware/burner](../firmware/burner.md)
92. **heat leech bite interaction** (1 draft): Does Heat (HUNTED band) add a free Leech Bite on the first enemy hit each fight, or does Heat stay out of the ring?
   - sources: [catalog/parasite](../catalog/parasite.md)
93. **heat nudge cost** (1 draft): Is Heat-paid nudge in option 2 too punishing next to +2 Heat entry fee, or should max extra nudges be capped at 2?
   - sources: [events/22_wheel_halcyon](../events/22_wheel_halcyon.md)
94. **heat scaling identity** (1 draft): Should Triage Unit keep any hint of its old "heals faster than you cut" identity at L5-6 via a Heat-scaled Hub heal?
   - sources: [enemies/triage_unit](../enemies/triage_unit.md)
95. **heat sink node effect** (1 draft): What is the Heat Sink node's effect amount per run?
   - sources: [gdd/s11](../gdd/s11.md)
96. **heat sustain role** (1 draft): Is retiring the Heat-75 heal acceptable, or should Heat 75+ add a third Late Fee trigger (+2 block) in P1?
   - sources: [enemies/account_manager](../enemies/account_manager.md)
97. **hit cap value** (1 draft): Is a hit cap of 4 right, or should it be 3 so a fully stamped wheel stays survivable at T1?
   - sources: [enemies/permit_office](../enemies/permit_office.md)
98. **hivemind upgrade design** (1 draft): Should Hivemind get a class-specific Pull+ (draw 2, next drone costs −1 RAM) instead of this neutral one?
   - sources: [card_upgrades/pull](../card_upgrades/pull.md)
99. **hold perfect availability** (1 draft): Is "no Perfect" on a 6-tick Hold too punishing for the enemy's own block?
   - sources: [enemies/port_authority](../enemies/port_authority.md)
100. **hot null heat balance** (1 draft): Is Hot Null's Heat cost too punishing at Level IV, given Heat drives raids?
   - sources: [slice_upgrades/null](../slice_upgrades/null.md)
101. **hot swap ram balance** (1 draft): Is +1 net RAM per play too strong when stacked with steady_hand and Rigger Hub, or should refund stay at 1 and cost drop to 1?
   - sources: [card_upgrades/hot_swap](../card_upgrades/hot_swap.md)
102. **hotfix healing percent** (1 draft): Is a flat 4% Hotfix too negligible to count as a "sustain" identity, or should it be 6% with a Perfect-less 3-tick slice?
   - sources: [enemies/weather_satellite](../enemies/weather_satellite.md)
103. **hotfix player availability** (1 draft): Should a HOTFIX-capable player class exist, or is HOTFIX permanently enemy-facing?
   - sources: [firmware/nanite_mesh](../firmware/nanite_mesh.md)
104. **hp band tuning** (1 draft): Is the 330 / 360 / 400 / 440 band right, given phase budgets sum to ≈ 445 at 18 DPT? Should P3-P5 be shorter instead?
   - sources: [enemies/commons_array](../enemies/commons_array.md)
105. **hp bands reference** (1 draft): Reference player for HP bands: bot, testers or midpoint.
   - sources: [gdd/s13](../gdd/s13.md)
106. **hp scaling multi needle** (1 draft): Should a 2-needle normal get HP above the 1-needle band (the pointer rule) or stay inside it as proposed?
   - sources: [enemies/route_optimizer](../enemies/route_optimizer.md)
107. **hp tier band placement** (1 draft): Is a 72/88/112/144 HP set at the very top of the band acceptable, or should the Board sit mid-band given Halcyon's status taxes?
   - sources: [enemies/zoning_board](../enemies/zoning_board.md)
108. **hq tier** (1 draft): Do all HQ fights use T4 enemies, or follow the campaign's current tier?
   - sources: [hq/meridian](../hq/meridian.md)
109. **hub dose fairness** (1 draft): Does the Standing Prescription hub dose (guaranteed 1 per turn) feel fair, or should it be skipped on a turn where a Dose slice already resolved?
   - sources: [enemies/dosage_dispenser](../enemies/dosage_dispenser.md)
110. **hub heal balance** (1 draft): Is a 4 % Hub heal too punishing at T4 (about 2.3 HP) for a player who deliberately defends?
   - sources: [enemies/triage_unit](../enemies/triage_unit.md)
111. **ice scaling alignment** (1 draft): Should ICE boss-strength steps match HP band ceilings, or should HP bands be separate from damage?
   - sources: [gdd/s11](../gdd/s11.md)
112. **jolt plus cycle multiplier** (1 draft): Should the + keep ×1.5 Cycle, or sit at ×1.25 given Jolt is a 50-Cycle card?
   - sources: [card_upgrades/jolt](../card_upgrades/jolt.md)
113. **late fee audit stacking** (1 draft): Does Late Fee (Heat 50+) double-dip with Audit unfairly for RAM-starved Ghosts, who rely on paid nudges?
   - sources: [enemies/compliance_officer](../enemies/compliance_officer.md)
114. **launch slice perfect window** (1 draft): Should the Launch slice's 6-tick, no-Perfect profile be authored explicitly via `tick_quality` so Good-or-better is wider?
   - sources: [enemies/launch_pad](../enemies/launch_pad.md)
115. **launder fee design** (1 draft): Is the launder fee (1 Schematic per Heat beyond 20) the right brake or hard cap?
   - sources: [nodes/heat_sink](../nodes/heat_sink.md)
116. **level ii branch availability** (1 draft): Do Level II branches both exist at every Rack, or is only one offered at a time to keep the choice small?
   - sources: [slice_upgrades/defrag](../slice_upgrades/defrag.md)
117. **level ii perfect tradeoff** (1 draft): Should Level II's 4-tick shape (no Perfect) be the default upgrade path, or is giving up Perfect too punishing for Perfect-hook classes?
   - sources: [slice_upgrades/hotfix](../slice_upgrades/hotfix.md)
118. **level iv availability** (1 draft): Is Level IV exclusive to Rack "flash" (my choice), or should the Workshop reach IV at layer 7?
   - sources: [nodes/workshop](../nodes/workshop.md)
119. **level iv cost balance** (1 draft): Is the Level IV cooldown too punishing against the enrage timer, or does Event Horizon need a different cost?
   - sources: [slice_upgrades/detour](../slice_upgrades/detour.md)
120. **level iv second socket** (1 draft): Should a Level IV slice get a second socket (which would allow Calibrated + Patch+)?
   - sources: [firmware/new_chips](../firmware/new_chips.md)
121. **level iv shield overlap** (1 draft): Is Level IV's SHIELD-on-Perfect too close to the SHIELD slice's role?
   - sources: [slice_upgrades/hotfix](../slice_upgrades/hotfix.md)
122. **mesh damage balance** (1 draft): Is a flat 1-2 damage per threat per step significant enough compared with the raid threat HP scale, pending the raid sim?
   - sources: [station/hivemind](../station/hivemind.md)
123. **metabolism buff strength** (1 draft): Should Metabolism ship as a "strong" buff (heal ≈4-5/turn, small)? If it needs more bite, second heal source breaks sustain cap.
   - sources: [enemies/renewal_engine](../enemies/renewal_engine.md)
124. **minimum slice size** (1 draft): Is a minimum SHIM size of 3 right, or do you want a 2-tick GG SHIM as a Level IV gamble?
   - sources: [slice_upgrades/shim](../slice_upgrades/shim.md)
125. **minimum slice size for siphon** (1 draft): Is 2-tick "always Good" intended as a cheap discount for tiny slices, or should Siphon be disallowed on slices under 4 ticks?
   - sources: [firmware/siphon](../firmware/siphon.md)
126. **muffler listener suppression frequency** (1 draft): Is `muffler` too strong for the Account Manager and Handler minis? Should it be once per combat?
   - sources: [firmware/new_chips](../firmware/new_chips.md)
127. **needle count distribution** (1 draft): Is a single FIXED needle in P1 and P2 acceptable, or should P3 have uneven needles?
   - sources: [enemies/logistics_director](../enemies/logistics_director.md)
128. **needle count phase balance** (1 draft): Keep one needle (budget-clean), or allow two readers in P1 and cut P1's HP share to 1 turn?
   - sources: [enemies/port_authority](../enemies/port_authority.md)
129. **needle gap tier scaling** (1 draft): Should the P2 uneven needle gap (12) be fixed, or authored per tier to narrow at higher tiers?
   - sources: [enemies/last_mile_enforcer](../enemies/last_mile_enforcer.md)
130. **netrun duration** (1 draft): Does "single roguelike runs, about 15 minutes each" still hold as pitch figure, given HQ runs that may be longer?
   - sources: [gdd/s01](../gdd/s01.md)
131. **netrun ram bonus overlap** (1 draft): Is the netrun-start +RAM acceptable next to Compiler Rack (a bonus card or Firmware), or does it overlap?
   - sources: [station/overclocker](../station/overclocker.md)
132. **nudge economy scope** (1 draft): Should the + version also hit the free-nudge economy (e.g. freeze lasts through enemy's next two turns on Normals), or is pure resistance and cost upgrade enough?
   - sources: [card_upgrades/blind_spot](../card_upgrades/blind_spot.md)
133. **nudge payment currency** (1 draft): Should extra-nudge payment be the player's choice of currency each time, or fixed per event?
   - sources: [events/24_wheel_rebel_cell](../events/24_wheel_rebel_cell.md)
134. **nudge play difficulty** (1 draft): Does a 4-tick W G G W Shim feel too safe for the player's nudge play, since a one-tick nudge can only move between WEAK and GOOD?
   - sources: [enemies/cell_informant](../enemies/cell_informant.md)
135. **null slice size cap** (1 draft): Should NULL slices be allowed to grow (6–7 ticks) at all, or should the loadout cap NULL at 5 to protect this chip's economy?
   - sources: [firmware/recycler](../firmware/recycler.md)
136. **once per action cap** (1 draft): Is "once per gate per action" too forgiving, since a Spin 30 would then cross everything once? Or should the gate fire per full revolution?
   - sources: [rim_gates/gates](../rim_gates/gates.md)
137. **opening difficulty spike** (1 draft): Should the first player turn (a 15 HP operative case from playtests) get a guaranteed gentle reading, for example a P1 opening respin that avoids Overflow + Shim?
   - sources: [enemies/claims_adjuster](../enemies/claims_adjuster.md)
138. **orbit speed with variable sizes** (1 draft): Should the orbit be 1 tick per turn or 2, given variable slice sizes make 1 tick meaningful on 4-tick slices?
   - sources: [enemies/uplink_relay](../enemies/uplink_relay.md)
139. **orbital nudge currency** (1 draft): Is HP the right extra-nudge currency here, or should Orbital events use Cycles to differ from Halcyon's HP-flavored costs?
   - sources: [events/23_wheel_orbital](../events/23_wheel_orbital.md)
140. **output down floor** (1 draft): Should OUTPUT_DOWN's floor be −75 % (proposed) or −50 % so a slice is never nearly dead?
   - sources: [catalog/status](../catalog/status.md)
141. **output down immunity interaction** (1 draft): Should the rider's stack count be capped on bosses with OUTPUT_DOWN immunity buffs, or is Compliance Lock enough?
   - sources: [card_upgrades/arc_flash](../card_upgrades/arc_flash.md)
142. **output down vs tier down** (1 draft): Does OUTPUT_DOWN ×2 on player's best slice feel too similar to Halcyon Citation stacking? Should Meridian use TIER_DOWN instead?
   - sources: [enemies/last_mile_enforcer](../enemies/last_mile_enforcer.md)
143. **overflow damage scaling** (1 draft): Is 3-tick Overflow (G P G) too punishing at T4 (14 × 2.2 = 31 on a Perfect), or should the amount drop to 12?
   - sources: [enemies/transit_controller](../enemies/transit_controller.md)
144. **overflow difficulty** (1 draft): Is a 4-tick Overflow with no Perfect too harsh, or should the Mast's Overflow be 5-tick?
   - sources: [enemies/surveillance_mast](../enemies/surveillance_mast.md)
145. **overflow difficulty teaching** (1 draft): Is a 3-tick Overflow with no WEAK landing too punishing for T1 teaching? If so, widen it to 4 and drop the Null to 7.
   - sources: [enemies/ground_control](../enemies/ground_control.md)
146. **overflow perfect readability** (1 draft): Should Overflow 4-tick slice stay without Perfect, or add Perfect to make best hit less safe to read?
   - sources: [enemies/loyalty_test](../enemies/loyalty_test.md)
147. **overflow tick width** (1 draft): Is the narrow no-Perfect Overflow too punishing without Firmware R11? Should it be 5 ticks at T1-T2?
   - sources: [enemies/last_mile_enforcer](../enemies/last_mile_enforcer.md)
148. **override boss application** (1 draft): Does Choice 2's HP cut apply to a mini-boss's last Rack fight, or only to normals and elites?
   - sources: [events/01_future_solace](../events/01_future_solace.md)
149. **override cost design** (1 draft): Should the override cost Fallout (corruption at fight start) or a stronger, simpler cost such as a flat HP loss, given that CORRUPTED is a 2× RAM tax and could snowball the boss fight?
   - sources: [hq/orbital](../hq/orbital.md)
150. **p rider multiplier** (1 draft): Should P Riders always include an x2-style multiplier, or can classes be flexible?
   - sources: [inner_ring/c](../inner_ring/c.md)
151. **p1 needle weight factor** (1 draft): Is the 1.5× two-needle HP factor right, or should P1 count a full ×2?
   - sources: [enemies/station_commander](../enemies/station_commander.md)
152. **p2 flare slice size** (1 draft): Should P2's second Flare slice stay at 4 ticks, or be reduced if sim shows overclock cascades?
   - sources: [enemies/geostationary_guard](../enemies/geostationary_guard.md)
153. **p3 resistance level** (1 draft): Should P3 remain on 1 resistance, or should Flip and Respin be unblocked (0)?
   - sources: [enemies/city_manager](../enemies/city_manager.md)
154. **p3 status cleanse strategy** (1 draft): Is `cleanse_on_enter` = OWN on P3 right, or should P3 keep the Director's statuses so a Virus Exploit stays live?
   - sources: [enemies/mission_director](../enemies/mission_director.md)
155. **p4 ram resolve balance** (1 draft): Is P4's "RAM ≥ 8 resolves again" too punishing for banking RAM?
   - sources: [enemies/the_manifest](../enemies/the_manifest.md)
156. **parasite anti tracer** (1 draft): Should a Parasite-ring "anti-tracer" exist that restores resistance, or is that overkill?
   - sources: [firmware/tracer](../firmware/tracer.md)
157. **parasite block interaction** (1 draft): Should parasite damage be blockable by default (proposed), with only Cutter piercing, or should some always bypass BLOCK?
   - sources: [catalog/parasite](../catalog/parasite.md)
158. **perfect hook p4** (1 draft): Is perfect-hook punishment in boss P4 acceptable, or should Calibrated Firmware be guaranteed in the Aurelian pool?
   - sources: [bosses/aurelian](../bosses/aurelian.md)
159. **perfect ram stacking balance** (1 draft): Is two total RAM on a Perfect too strong for the Rigger, whose Perfect hook already refunds 1 RAM?
   - sources: [firmware/power_cell](../firmware/power_cell.md)
160. **phase 2 resistance value** (1 draft): Should P2 resistance go to 0, or stay at 1 to protect the Detour window?
   - sources: [enemies/rc_template_elite_b](../enemies/rc_template_elite_b.md)
161. **phase count and structure** (1 draft): Are the five phases right, or should P4 (drones) be dropped for 4 phases at ~4 turns each?
   - sources: [enemies/dispatch_core](../enemies/dispatch_core.md)
162. **phase duration scaling** (1 draft): Raise the 3-phase band to fit a 2-needle P3, or accept 3.05 turns per phase instead of 3.5?
   - sources: [enemies/the_handler](../enemies/the_handler.md)
163. **phase threshold scaling** (1 draft): Should the phase thresholds scale with the HP band, or stay percent as authored?
   - sources: [enemies/civic_core](../enemies/civic_core.md)
164. **pierce tier gate** (1 draft): Should the pierce window in P2 exist on an elite at T1, or only from T2 up?
   - sources: [enemies/rc_template_elite](../enemies/rc_template_elite.md)
165. **pressure and corruption interaction** (1 draft): Is the Pressure RAM cap acceptable alongside the corruption RAM tax (R9), or do the two stack into too much RAM pressure for the final boss?
   - sources: [hq/tethys](../hq/tethys.md)
166. **pressure at boss** (1 draft): Should Tower pressure also affect the Genome Core fight, or reset at the crown?
   - sources: [hq/solace](../hq/solace.md)
167. **priority drain landing quality gating** (1 draft): Should Priority drain RAM only on Good-or-better, so a weak landing is a real escape?
   - sources: [enemies/port_authority](../enemies/port_authority.md)
168. **priority drain scaling** (1 draft): Should Priority's RAM drain scale with tier like damage, or stay flat at 3 RAM?
   - sources: [enemies/logistics_director](../enemies/logistics_director.md)
169. **priority pressure** (1 draft): Is Priority (RAM drain 2) enough pressure on its own, or should it become a corrupt-adjacent RAM tax once N9 lands?
   - sources: [enemies/cell_informant](../enemies/cell_informant.md)
170. **pulse damage type** (1 draft): Should Pulse become a PERCENT-of-player-HP hit, or stay FLAT?
   - sources: [enemies/care_swarm](../enemies/care_swarm.md)
171. **ram cost balance** (1 draft): Is the RAM 1 cost too cheap given that both wheels move in one play?
   - sources: [card_upgrades/gear_mesh](../card_upgrades/gear_mesh.md)
172. **ram drain tuning** (1 draft): Is 2 RAM drain per Priority hit too weak to matter now that RAM is banked to 12?
   - sources: [enemies/customs_scanner](../enemies/customs_scanner.md)
173. **rank 3 gate customization** (1 draft): Should Rank 3 let players choose the gates (WEAK/GOOD/PERFECT order), or are the three gates fixed?
   - sources: [inner_ring/b](../inner_ring/b.md)
174. **rank 3 netrun benefit** (1 draft): Should Rank 3 add a netrun-side benefit (a starting drone), or does stationing stay raid-only?
   - sources: [station/hivemind](../station/hivemind.md)
175. **rank 3 swap limit** (1 draft): Should Rank 3 Retune let the player swap two segments, or is one swap enough?
   - sources: [inner_ring/a](../inner_ring/a.md)
176. **ratchet ram cost** (1 draft): Is a RAM cost of 1 too cheap next to Gear Shift (5 ticks, 1 RAM)?
   - sources: [card_upgrades/ratchet](../card_upgrades/ratchet.md)
177. **reference dpt nudge assumption** (1 draft): Does `reference_dpt` assume nudge use against resistance 2? I assumed it does not.
   - sources: [enemies/port_authority](../enemies/port_authority.md)
178. **relative card pricing** (1 draft): Should Spin Cycle+ be priced above Heavy Spin (9 ticks, 2 RAM), which becomes nearly the same card?
   - sources: [card_upgrades/spin_cycle](../card_upgrades/spin_cycle.md)
179. **resistance bypass overlap** (1 draft): Does the first nudge's resistance bypass overlap too much with Ghost Step, so that the Ghost-class benefit is diluted?
   - sources: [card_upgrades/fine_tune](../card_upgrades/fine_tune.md)
180. **resistance friction balance** (1 draft): Resistance 2 vs 3: does a 2-tick absorb still make Spin cards meaningfully worse, or does it vanish into the noise?
   - sources: [enemies/compliance_officer](../enemies/compliance_officer.md)
181. **resistance necessity** (1 draft): Does the P1 resistance of 1 still earn its place now that the orbit is the main tracking question?
   - sources: [enemies/recall_unit](../enemies/recall_unit.md)
182. **resistance on normal** (1 draft): Should Resistance 1 on a normal with a single needle be kept as a flavor tax, or dropped to keep L1 free of the nudge-absorption lesson?
   - sources: [enemies/utility_meter](../enemies/utility_meter.md)
183. **resistance strip scaling** (1 draft): Should the amount be a PERCENT of max resistance for Heat-scaled +1 resistance modifiers, or stay FLAT?
   - sources: [card_upgrades/deep_strip](../card_upgrades/deep_strip.md)
184. **rest workshop cache placement rate** (1 draft): Rate and placement of Rest/Workshop/Cache nodes are unruled (A8 numbers are placeholders).
   - sources: [gdd/s04](../gdd/s04.md)
185. **reward scaling by difficulty** (1 draft): Should tier_delta -1 on a voluntary fight also lower the reward pool, or is a flat reward right?
   - sources: [events/15_ambush_meridian](../events/15_ambush_meridian.md)
186. **rewire cost** (1 draft): Should REWIRE cost something (a small Cycles fee or 1 Heat) to keep it from being the default at high HP?
   - sources: [nodes/rest](../nodes/rest.md)
187. **rider scaling** (1 draft): Should the rider be a flat +3, or a percent-style "the same again at half" to scale better against resistance?
   - sources: [card_upgrades/whirl](../card_upgrades/whirl.md)
188. **rider target scope** (1 draft): Should the rider fire when spin targets enemy wheel, not just own wheel?
   - sources: [card_upgrades/backspin](../card_upgrades/backspin.md)
189. **rigger adjacency stacking** (1 draft): Is "one operative per Safehouse slot" firm? Should I add an adjacency cap to prevent double-stacking?
   - sources: [station/rigger](../station/rigger.md)
190. **run length and layer count** (1 draft): Is an 11-layer, about 30-minute HQ run the right length for the designer, given the 15-minute standard netrun and the open-ended D10 range?
   - sources: [hq/tethys](../hq/tethys.md)
191. **rung count and pacing** (1 draft): Is 9 rungs (about 30 minutes) acceptable for the capstone, or should it be 7 for a typical session?
   - sources: [hq/solace](../hq/solace.md)
192. **same class stacking** (1 draft): Should a second stationed operative stack at 50 %, or should the second slot hold a different class bonus only (no same-class stacking)?
   - sources: [nodes/safehouse](../nodes/safehouse.md)
193. **segment consolidation** (1 draft): Should Dampener and Tithe be one segment ("tax") to keep the roster smaller, with the percent as the dial?
   - sources: [catalog/parasite](../catalog/parasite.md)
194. **segment role uniqueness** (1 draft): Is "no two segments of the same role" acceptable, or should x2 + Echo be allowed on one ring?
   - sources: [inner_ring/a](../inner_ring/a.md)
195. **sell rumor heat cost** (1 draft): Does the Heat on choice 3 belong on this event, or should the cost be only the future penalty?
   - sources: [events/07_future_tethys](../events/07_future_tethys.md)
196. **shield cap boss specific** (1 draft): Is 15 % shield cap acceptable without a boss-specific cap?
   - sources: [enemies/the_manifest](../enemies/the_manifest.md)
197. **shield cap exception** (1 draft): Should the SHIELD cap exception exist at all, or should the chip stay a plain ×1.5 and let the cap punish it?
   - sources: [firmware/bulkhead](../firmware/bulkhead.md)
198. **shield cap scaling** (1 draft): Does a shield cap raise at Level IV (e.g. 20) make Level IV more exciting than the stripped-immunity design?
   - sources: [slice_upgrades/sandbox](../slice_upgrades/sandbox.md)
199. **shield status interaction** (1 draft): Should chip-granted PERCENT shield be scaled by OUTPUT_DOWN, or is it exempt so the chip counters Citation?
   - sources: [firmware/static_coat](../firmware/static_coat.md)
200. **shim damage threat level** (1 draft): Is 7 damage on Shim too low at T1 to register as a threat for the new player in the 3-turn fight?
   - sources: [enemies/uplink_relay](../enemies/uplink_relay.md)
201. **sibling elite threshold distinctness** (1 draft): Should the second REBEL_CELL elite also have a distinct threshold (e.g. 0.6) so the two are not the same shape?
   - sources: [enemies/rc_template_elite_b](../enemies/rc_template_elite_b.md)
202. **signature buff guarantee** (1 draft): Should the Orbit Schedule buff be the one the designer wants guaranteed in every Grid draw?
   - sources: [enemies/commons_array](../enemies/commons_array.md)
203. **signature distinction** (1 draft): Is Resistance 2 enough of a signature once Cell Informant and Loyalty Test are redesigned?
   - sources: [enemies/handler_proxy](../enemies/handler_proxy.md)
204. **skip reward forfeit** (1 draft): Should a Skip that bypasses a Rack-layer node also forfeit the Rack's Schematics, or should Racks be exempt?
   - sources: [events/26_wheel_any](../events/26_wheel_any.md)
205. **skippable planted combat** (1 draft): Should choice 2's planted cell_informant fight be skippable by paying Cycles at the node?
   - sources: [events/28_raidwin_rebel_cell](../events/28_raidwin_rebel_cell.md)
206. **slab damage value** (1 draft): Do I want Slab at 9 or keep the old 10 for continuity?
   - sources: [enemies/orbital_debris](../enemies/orbital_debris.md)
207. **slice layout** (1 draft): Should the Null slice be 8 ticks (27% dead turns) or split into two 4-tick Nulls so a Shim always sits next to it?
   - sources: [enemies/patrol_unit](../enemies/patrol_unit.md)
208. **slice level steps costs** (1 draft): What are the exact Slice Level steps, costs, and output changes (pending design pass)?
   - sources: [gdd/s05](../gdd/s05.md)
209. **slice size progression** (1 draft): Is a 4-tick no-Perfect Surcharge the right teaching of R11 at T1, or should T1 show a 5-tick slice and unlock uneven maps at T2?
   - sources: [enemies/utility_meter](../enemies/utility_meter.md)
210. **small slice steerability** (1 draft): Is a 3-tick Dose B (no WEAK edge, 1 Perfect tick) too hard to steer past with a 1-tick nudge granularity?
   - sources: [enemies/dosage_dispenser](../enemies/dosage_dispenser.md)
211. **snap lock on balance** (1 draft): Does Snap+ at 1 RAM make Lock On (0 RAM, exhaust) redundant in neutral decks, so that Lock On needs its own revisit?
   - sources: [card_upgrades/snap](../card_upgrades/snap.md)
212. **softlock prevention** (1 draft): Is the guarantee "every room reaches the next ring within 4 steps" enough, or should a minimum of 2 simultaneously open descents per ring be enforced?
   - sources: [hq/aurelian](../hq/aurelian.md)
213. **solar flare retention** (1 draft): Do we want to keep Solar Flare for L5-6 pressure only, as an optional variant slot?
   - sources: [enemies/mirror_script](../enemies/mirror_script.md)
214. **solar flare target method** (1 draft): Should Solar Flare stay random non-NULL, or pick the slice under the pointer so it is steerable?
   - sources: [enemies/launch_pad](../enemies/launch_pad.md)
215. **spawn drone cost balance** (1 draft): Is the 1 RAM cost too cheap next to TROJAN's free drone? Does it need to stay at 2 with the refresh as the entire upgrade?
   - sources: [card_upgrades/spawn_drone](../card_upgrades/spawn_drone.md)
216. **spotted fight difficulty** (1 draft): Are SPOTTED fights too punishing at T4 with scan blow every turn plus early enrage?
   - sources: [hq/halcyon](../hq/halcyon.md)
217. **statement drain severity** (1 draft): Is draining 3 RAM on one slice too punishing at L1-2, given the RAM cap of 12 and the start of 6?
   - sources: [enemies/billing_daemon](../enemies/billing_daemon.md)
218. **station bonus values** (1 draft): What is the station bonus for each class and each alternate version (unique per G8)?
   - sources: [gdd/s05](../gdd/s05.md)
219. **stationed operative recovery** (1 draft): Should stationed operatives recover something (for example, a Rank progress tick every N raids survived), or is the defensive bonus the only reward?
   - sources: [nodes/safehouse](../nodes/safehouse.md)
220. **status carryover between phases** (1 draft): P3's partial cleanse_on_enter (PLAYER) hides a status-stack puzzle from P2; is a total NONE (stacks carry) better?
   - sources: [enemies/dispatch_core](../enemies/dispatch_core.md)
221. **strip plus class relevance** (1 draft): Do ghost and phantom "first nudge ignores resistance" hooks make Strip+ redundant, so should the rider be class-neutral at all?
   - sources: [card_upgrades/strip](../card_upgrades/strip.md)
222. **sustain definition** (1 draft): Does the P1 Barrier on one needle count as "sustain" for the 30 % cap, or only heals?
   - sources: [enemies/riot_control](../enemies/riot_control.md)
223. **t2 hp 72 vs 68** (1 draft): Should the mini-boss band lower edge hold for T2 at 72 HP, or is 68 (the exact budget) closer to the intended feel?
   - sources: [enemies/account_manager](../enemies/account_manager.md)
224. **t4 lock on damage** (1 draft): Should T4 Lock-On drop to 10 damage if sim shows under 90% win rate?
   - sources: [enemies/tracking_station](../enemies/tracking_station.md)
225. **telegraph visibility** (1 draft): Should the 4-step lookahead be Intel's reward (proposed) or default knowledge?
   - sources: [hq/aurelian](../hq/aurelian.md)
226. **tethys pressure mechanic** (1 draft): Is Tethys's slow-pressure theme meant to be mechanically an enrage variant, or only flavor?
   - sources: [gdd/s08](../gdd/s08.md)
227. **threat readability** (1 draft): Is a 3-tick Overflow (no steering margin except one nudge) too punishing for L1-2, or should the teaching version use a 4-tick Overflow with no Perfect?
   - sources: [enemies/patrol_unit](../enemies/patrol_unit.md)
228. **tier down punishment** (1 draft): Is TIER_DOWN on a Denial slice too punishing in a phase that already doubles RAM on corrupted slices? An alternative is OUTPUT_DOWN x1 (−25 %).
   - sources: [enemies/claims_adjuster](../enemies/claims_adjuster.md)
229. **tier down slice exemption** (1 draft): Is TIER_DOWN too punishing on a 4-tick slice (no Perfect already)? Consider exempting it.
   - sources: [enemies/zoning_board](../enemies/zoning_board.md)
230. **tier override ceiling** (1 draft): Should the +1 tier cap at the run's current tier ceiling, or may an ambush exceed it?
   - sources: [events/14_ambush_solace](../events/14_ambush_solace.md)
231. **tier tweak hp scaling** (1 draft): Does a tier tweak on an impromptu fight also move the enemy's HP band (hp_by_tier), or only its starting damage?
   - sources: [events/19_ambush_tethys](../events/19_ambush_tethys.md)
232. **toll corruption scaling** (1 draft): Should Toll gates cost RAM at the corrupted 2× rate (R9), or a flat 1 RAM?
   - sources: [rim_gates/gates](../rim_gates/gates.md)
233. **toll drain amount** (1 draft): Is a 1-RAM drain on every Toll too small to notice at the reference player, versus 2?
   - sources: [enemies/tariff_collector](../enemies/tariff_collector.md)
234. **transition cleanse design** (1 draft): Should the P1 → P2 transition ever cleanse the player (`cleanse_on_enter` = PLAYER) for a gentler pass, or does keeping overclocks defeat that?
   - sources: [enemies/station_commander](../enemies/station_commander.md)
235. **tripwire cost currency** (1 draft): Is a PERCENT-HP trap acceptable given "a TRIPWIRE can't kill", or should the trap cost only Heat to avoid HP attrition?
   - sources: [nodes/cache](../nodes/cache.md)
236. **two needle bands** (1 draft): Should the R2 band tables grow a "+1 needle" column, or are two needles boss-only?
   - sources: [bosses/aurelian](../bosses/aurelian.md)
237. **ultimatum heat direction** (1 draft): Should "pay Heat to cancel" raise Heat (bribe queuing raids), or be a Heat reduction variant?
   - sources: [raids/main](../raids/main.md)
238. **ultimatum reward scaling** (1 draft): Does an accepted ultimatum's larger reward scale with Heat, or is it a flat multiple?
   - sources: [gdd/s07](../gdd/s07.md)
239. **undock card availability** (1 draft): If R12 makes the drone un-nudgeable, should Undock exist as a player card in the REBEL_CELL pool so this enemy has a hard counter?
   - sources: [enemies/dead_drop](../enemies/dead_drop.md)
240. **upgrade class restriction** (1 draft): Should the + version be cross-class, or Rigger-only like the base?
   - sources: [card_upgrades/torque_wrench](../card_upgrades/torque_wrench.md)
241. **upgrade consistency across classes** (1 draft): Should hivemind get the same + version, or a variant with a different rider?
   - sources: [card_upgrades/parasite_pulse](../card_upgrades/parasite_pulse.md)
242. **upgrade cost positioning** (1 draft): Is a 1 RAM spin at 7 ticks too close to Jolt and Counter-Spin? Should the + version stay at 2 RAM with a stronger rider instead?
   - sources: [card_upgrades/whirl](../card_upgrades/whirl.md)
243. **upgrade cycle cost multiplier** (1 draft): Should the upgraded Cycle cost multiplier be one value for all cards (×1.5) or priced per card?
   - sources: [card_upgrades/double_jam](../card_upgrades/double_jam.md)
244. **upgrade cycle pricing** (1 draft): Is a flat Cycle multiplier ×1.5 right for every upgrade, or does each card get its own price?
   - sources: [card_upgrades/data_surge](../card_upgrades/data_surge.md)
245. **upgrade design alternative** (1 draft): Is the 0-RAM cost reduction a better + once CORRUPTED on enemies has a defined effect?
   - sources: [card_upgrades/corrupt_packet](../card_upgrades/corrupt_packet.md)
246. **upgrade identity and value** (1 draft): Is a pure discount (3 → 2 RAM) enough, or should direction choice be a required part of the + version, given the extra UI?
   - sources: [card_upgrades/spin_cycle](../card_upgrades/spin_cycle.md)
247. **upgrade identity niche** (1 draft): Is a heal-6 + cleanse card too close to Sanitize for deck slots, or should the + keep heal-only identity with flat cost cut?
   - sources: [card_upgrades/patch_up](../card_upgrades/patch_up.md)
248. **upgrade rarity inheritance** (1 draft): Should Duck+ be Uncommon rarity, or keep the rarity of Duck, so that upgrading doesn't change drop tables?
   - sources: [card_upgrades/duck](../card_upgrades/duck.md)
249. **upgrade scope** (1 draft): Should the upgrade also allow a 5-tick nudge in either direction on the outer ring, or stay inner-ring only?
   - sources: [card_upgrades/gear_shift](../card_upgrades/gear_shift.md)
250. **variant per cache** (1 draft): Should the PAY_HEAT / PAY_HP variant be tied to the corporation or rolled per Cache from the map stream?
   - sources: [nodes/cache](../nodes/cache.md)
251. **weak rider buff** (1 draft): Should W Riders buff WEAK landings, making low-precision play viable?
   - sources: [inner_ring/c](../inner_ring/c.md)
252. **wrecker early rank balance** (1 draft): Is "first wave only" at Ranks 0–1 too weak compared with the Breaker's continuous +50%?
   - sources: [station/wrecker](../station/wrecker.md)

## economy

253. **cleanse availability** (2 drafts): Does a Cleanse card appear reliably early enough in a T1 run for this to be a fair teaching fight?
   - also: Does Cleanse need a guaranteed supply at L1-2 for this fight to teach rather than punish?
   - sources: [enemies/parking_warden](../enemies/parking_warden.md), [enemies/permit_office](../enemies/permit_office.md)
254. **upgrade distribution** (2 drafts): Should the + version keep the base card's reward-pool presence, or appear only as an upgrade at Workshop/Rest nodes?
   - also: Is "reward pool only" intended to keep + versions out of Mainframes, or is that the same pool in the data?
   - sources: [card_upgrades/flip_switch](../card_upgrades/flip_switch.md), [card_upgrades/sanitize](../card_upgrades/sanitize.md)
255. **botnet campaign identity** (1 draft): Is the non-raid Schematic trickle worth keeping for distinct campaign-layer identity?
   - sources: [station/botnet](../station/botnet.md)
256. **branch refit mechanic** (1 draft): Should a "refit" re-roll between Level II and III branches exist, and at what price?
   - sources: [slice_upgrades/trojan](../slice_upgrades/trojan.md)
257. **cache in hq** (1 draft): Do Caches ever appear in HQ netruns, or are they street-only?
   - sources: [nodes/cache](../nodes/cache.md)
258. **cycles scaling** (1 draft): Should Cycles scale with node tier (PERCENT of shop prices), or stay flat for a predictable economy?
   - sources: [firmware/skimmer](../firmware/skimmer.md)
259. **exploit payoff relationship** (1 draft): Do the Exploit payoffs (Tide Tables, Master Valve, Contamination) replace the existing Intel/Breach/Virus Grid functions in this HQ, or sit on top of them as bonuses?
   - sources: [hq/tethys](../hq/tethys.md)
260. **first safehouse placement** (1 draft): Should the first Safehouse come pre-built in the home server variants, or stay a 20-Schematic first purchase?
   - sources: [nodes/safehouse](../nodes/safehouse.md)
261. **healing budget source** (1 draft): Should the HQ's total heal budget come from Rest nodes, or should the operative start healed with Favor as the scarce resource?
   - sources: [hq/aurelian](../hq/aurelian.md)
262. **heat chip distribution** (1 draft): Should Heat-reduction chips be exclusive to Rack or elite rewards, to keep the Heat-sink economy in tune with the Daemons?
   - sources: [firmware/coolant_loop](../firmware/coolant_loop.md)
263. **level iv acquisition** (1 draft): Should Level IV be reachable only through Racks, or also a Workshop at a high price?
   - sources: [slice_upgrades/shim](../slice_upgrades/shim.md)
264. **license unlock type** (1 draft): License as a Schematics sink (my choice) or a built network node (a "Machine Shop" near your territory that sets the netrun's Workshop count), tying it to the campaign layer and to raids?
   - sources: [nodes/workshop](../nodes/workshop.md)
265. **mesh non stationed upgrade** (1 draft): Should the Mesh's persistence also apply when the operative is not stationed, as a node upgrade the player buys later?
   - sources: [station/hivemind](../station/hivemind.md)
266. **new corporation unlock order** (1 draft): What is the unlock order and gating for Aurelian Concord and Tethys Deep?
   - sources: [gdd/s03](../gdd/s03.md)
267. **null upgrade cost** (1 draft): Is "free upgrade" for NULL acceptable, or must it cost Cycles to keep the shop economy consistent?
   - sources: [slice_upgrades/null](../slice_upgrades/null.md)
268. **operative deck configuration** (1 draft): Shared or separate decks: one deck per operative or single shared deck for all three?
   - sources: [hq/rebel_cell](../hq/rebel_cell.md)
269. **retired slice economy** (1 draft): Should the retired defrag_2/3/5/8 stay in the shop pool as Level I swap targets with cheaper prices?
   - sources: [slice_upgrades/defrag](../slice_upgrades/defrag.md)
270. **retune card necessity** (1 draft): Is the Retune card needed, or is the HQ swap alone enough?
   - sources: [inner_ring/c](../inner_ring/c.md)
271. **schematic payout economy** (1 draft): Should the Rank 3 Schematic payout be allowed, or does it break the Schematics sink economy?
   - sources: [station/breaker](../station/breaker.md)
272. **shop level availability** (1 draft): Should the shop sell Level II only, leaving III and IV for Racks?
   - sources: [slice_upgrades/sandbox](../slice_upgrades/sandbox.md)
273. **strike tally scope** (1 draft): Is the campaign-level strike tally (each retarget turns an Orbital Site into a raid-free source) in scope for the raid pass, or too large an effect for an HQ reward?
   - sources: [hq/orbital](../hq/orbital.md)
274. **tag cap inclusion** (1 draft): Does the Tag count against the 30% sustain cap analogue, or only at the designer's discretion?
   - sources: [enemies/recall_unit](../enemies/recall_unit.md)
275. **ultimatum payment options** (1 draft): Is the Heat-payable ultimatum (+8 Heat) wanted, or Schematics only?
   - sources: [gdd/s11](../gdd/s11.md)
276. **upgrade acquisition method** (1 draft): Should the + version be shop-only upgrades (Rest node: Workshop) or per-class reward upgrades, given that 8 classes share it?
   - sources: [card_upgrades/fine_tune](../card_upgrades/fine_tune.md)
277. **upgrade availability** (1 draft): Should upgraded cards be offered=false in reward pools and only reachable through upgrade station or Rack reward?
   - sources: [card_upgrades/power_tap](../card_upgrades/power_tap.md)
278. **upgrade cycle cost rule** (1 draft): Does an upgrade multiply Cycle cost by a fixed ×1.3 for every card, or is it authored per card?
   - sources: [card_upgrades/shield_wall](../card_upgrades/shield_wall.md)
279. **upgrade cycle cost waiver** (1 draft): Should the + version waive its Cycle surcharge at a Workshop (D4 node) where upgrades are sold?
   - sources: [card_upgrades/cleanse](../card_upgrades/cleanse.md)
280. **upgrade persistence across runs** (1 draft): Should upgrades persist on an operative who survives and returns to HQ, as deck and Firmware do (GDD 4.2 "keeping deck, Firmware and Daemons"), or reset per netrun?
   - sources: [nodes/workshop](../nodes/workshop.md)
281. **upgrade pricing model** (1 draft): Does an upgrade pass use the same `cycle_cost`, or should upgrades be priced separately at the shop or Workshop?
   - sources: [card_upgrades/stim_patch](../card_upgrades/stim_patch.md)
282. **upgrade reward source** (1 draft): Should the upgraded version be offered only as a Rack or "flash" reward, or also as a Mainframe purchase?
   - sources: [card_upgrades/micro_adjust](../card_upgrades/micro_adjust.md)

## narrative

283. **corporation story paths** (2 drafts): How many story paths should Aurelian Concord and Tethys Deep each have, and what are their titles?
   - also: Do Aurelian Concord and Tethys Deep each get their own ICE ladder, as REBEL_CELL does?
   - sources: [gdd/s08](../gdd/s08.md), [gdd/s13](../gdd/s13.md)
284. **consequence callbacks** (1 draft): Should the sold tip in choice 3 later surface as a raid-win or HQ event (the prisoner returning)?
   - sources: [events/18_ambush_rebel_cell](../events/18_ambush_rebel_cell.md)
285. **corporation boss content** (1 draft): What are the Aurelian Concord boss, its Exploit pool, and Tethys Deep's pool?
   - sources: [gdd/s11](../gdd/s11.md)
286. **corporation flavor details** (1 draft): What are the Aurelian (LEVIES) and Tethys theme facts, rosters, vehicle mixes and twists?
   - sources: [raids/main](../raids/main.md)
287. **corporation naming** (1 draft): Does the pitch keep Solace as the "first" corporation, or does the seven-corporation roster make that framing misleading?
   - sources: [gdd/s01](../gdd/s01.md)
288. **dispatch voice shift tracking** (1 draft): Should DISPATCH's voice shift track the number of corporations cleared in the profile (as proposed in A2), or the current campaign's progress?
   - sources: [gdd/s08](../gdd/s08.md)
289. **foreshadowing path targeting** (1 draft): Do you want the foreshadowing path (A4) to point only to uncleared corporations, or to a fixed successor chain?
   - sources: [gdd/s08](../gdd/s08.md)
290. **narrative persistence** (1 draft): Should the "favor" thread persist with a flag so a later Orbital event can call it in, or stay a one-off?
   - sources: [events/11_paths_orbital](../events/11_paths_orbital.md)
291. **tower deck scope** (1 draft): Should the HQ's tower decks use only Solace normals, or can Waiting Room debts bring cross-corporation foreshadow?
   - sources: [hq/solace](../hq/solace.md)

## new-system

292. **direction choice generalization** (2 drafts): Should direction choice become a general flag on all spin cards, or stay a Flick+ feature?
   - also: Should direction choice become a general field for all spin cards (Twist, Whirl and so on), so it is no longer a feature unique to this +?
   - sources: [card_upgrades/flick](../card_upgrades/flick.md), [card_upgrades/inner_drift](../card_upgrades/inner_drift.md)
293. **bug decay trigger mechanism** (1 draft): If we do build Bug+, what escalates Bug to Bug+: a Heat threshold, an enemy listener (N6), or a parasite effect (N10)?
   - sources: [card_upgrades/bug](../card_upgrades/bug.md)
294. **cache node mechanics** (1 draft): What is the Cache node's Cycle payout and event mini-puzzle design?
   - sources: [gdd/s11](../gdd/s11.md)
295. **cache puzzle design** (1 draft): Cache puzzle design needs vetting before it is final.
   - sources: [gdd/s04](../gdd/s04.md)
296. **conditional effect system** (1 draft): Do upgraded cards need a general conditional-effect field, or should each use a CUSTOM handler?
   - sources: [card_upgrades/inner_snap](../card_upgrades/inner_snap.md)
297. **conditional rider system** (1 draft): Should the + version use a conditional rider (needs new `condition` field), or take the data-only +4 block fallback?
   - sources: [card_upgrades/armor_plate](../card_upgrades/armor_plate.md)
298. **daemon rest hook** (1 draft): Should a Daemon family hook REST (for example a "Field Medic" Daemon: PATCH +10%), and if so does it need an ON_REST_ENTER trigger?
   - sources: [nodes/rest](../nodes/rest.md)
299. **debris parasite launch readiness** (1 draft): Is a Debris parasite on the player's ring (N10) acceptable at launch, or should P5 wait for the ring?
   - sources: [enemies/commons_array](../enemies/commons_array.md)
300. **drone presence** (1 draft): Is dropping the civic drone acceptable, or should it return as one fixed Clerk satellite on the Stamp Pad?
   - sources: [enemies/permit_office](../enemies/permit_office.md)
301. **effect level pierce timing** (1 draft): Should the + version be one tool per card (pierce here), or should the upgrade pass avoid effect-level pierce until N20 exists?
   - sources: [card_upgrades/static_shock](../card_upgrades/static_shock.md)
302. **exploit flavor and buildings** (1 draft): What are the specific Exploit flavors and access-key buildings for Aurelian Concord and Tethys Deep?
   - sources: [gdd/s08](../gdd/s08.md)
303. **exploit pool gates** (1 draft): With 5 Exploits drawn per Grid, do any 3 open the breach, and may art add an eighth Site type?
   - sources: [bosses/aurelian](../bosses/aurelian.md)
304. **general effect mode** (1 draft): Should a percent-of-output damage effect become a general effect mode or stay a one-off for this chip?
   - sources: [firmware/barbed_wire](../firmware/barbed_wire.md)
305. **inert pointers system** (1 draft): Add `inert_pointers` field to phase data for Second Opinion counter, or accept Breach removes needle and re-tune HP?
   - sources: [enemies/renewal_engine](../enemies/renewal_engine.md)
306. **landing tier condition system** (1 draft): Need new EffectData.require_tier field and effect_interpreter check, or use data-only fallback?
   - sources: [card_upgrades/bulwark](../card_upgrades/bulwark.md)
307. **lock on implementation** (1 draft): Is Lock-On a new hub rule worth a field, or should P2 simply keep a slower orbit as the data-only fallback?
   - sources: [enemies/recall_unit](../enemies/recall_unit.md)
308. **lock phase mapping** (1 draft): Should the locks be tied to class (each class gets its own phase rule) or to the operative's equipped Firmware (the profile-built Mirror idea from GDD 8.5)?
   - sources: [sync_strike/strike](../sync_strike/strike.md)
309. **mirror actual wheel** (1 draft): Should the layouts mirror the player's actual wheel (slice types and sizes copied from the operative running the netrun) instead of being authored?
   - sources: [enemies/rc_template_elite](../enemies/rc_template_elite.md)
310. **needle gap standardization** (1 draft): Should the 0 / 11 needle gap be a Meridian-wide pattern, or reserved for this scanner?
   - sources: [enemies/customs_scanner](../enemies/customs_scanner.md)
311. **netrun side identity** (1 draft): Should the raid-only identity stay, or does the designer want a netrun-side perk from stationing?
   - sources: [station/breaker](../station/breaker.md)
312. **next raid overrides field** (1 draft): Is "next_raid_overrides" a new field distinct from next_combat_overrides, or should next_combat_overrides be extended to cover raids?
   - sources: [events/27_raidwin_any](../events/27_raidwin_any.md)
313. **p5 package uniqueness** (1 draft): Should the P5 Packages use the Logistics Director's exact Package, or a distinct anti-slice?
   - sources: [enemies/the_manifest](../enemies/the_manifest.md)
314. **per step raid hook scope** (1 draft): Is the per-step raid hook a worthwhile new system for one class, or should we take the data-only fallback (a one-shot node SHIELD)?
   - sources: [station/overclocker](../station/overclocker.md)
315. **player placed parasites** (1 draft): Should the player ever place parasites on an enemy wheel (Botnet's mirror), or stay with statuses only?
   - sources: [catalog/parasite](../catalog/parasite.md)
316. **player tide tools** (1 draft): Should the player ever read the tide as a tool (Firmware/Daemon like "Dead Reckoning" that nudges the tide one step or shows next two steps)?
   - sources: [bosses/tethys](../bosses/tethys.md)
317. **rim gate effects** (1 draft): What are the authored effects for rim gates?
   - sources: [gdd/s02](../gdd/s02.md)
318. **sandbox separate chip** (1 draft): Should SANDBOX (the evade) get its own chip, for example "negates one extra hit", rather than a multiplier?
   - sources: [firmware/bulkhead](../firmware/bulkhead.md)
319. **shield bonus future class** (1 draft): Is a node SHIELD-type bonus wanted for another alternate to complete trio mapping?
   - sources: [station/phantom](../station/phantom.md)
320. **shield rider scope** (1 draft): Should the Surcharge's shield rider be a new slice rider (N20), or a general effect modifier reusable by other enemies?
   - sources: [enemies/utility_meter](../enemies/utility_meter.md)
321. **sink objective site tie** (1 draft): Should the objective Site offer a "claim as Heat Sink" conversion, or build-only?
   - sources: [nodes/heat_sink](../nodes/heat_sink.md)
322. **slice upgrade mechanics** (1 draft): What are the slice Level cap, per-Level effects, and Workshop stock rules?
   - sources: [gdd/s11](../gdd/s11.md)
323. **spin direction generalization** (1 draft): Should direction choice become a general SPIN rider for the whole spin family (Twist+, Whirl+) rather than a one-off here?
   - sources: [card_upgrades/jolt](../card_upgrades/jolt.md)
324. **spin direction upgrade scope** (1 draft): Should direction choice become the + standard for the whole spin family, or is it a special upgrade only for Heavy Spin?
   - sources: [card_upgrades/heavy_spin](../card_upgrades/heavy_spin.md)
325. **toll table ownership** (1 draft): Who owns the toll rule table: this HQ only, or should future HQs reuse tolls on their own links?
   - sources: [hq/solace](../hq/solace.md)
326. **workshop function** (1 draft): Workshop's exact function beyond "yes" needs to be determined.
   - sources: [gdd/s04](../gdd/s04.md)

## process

327. **corporation unlock progression** (1 draft): Should the profile start with all six non-REBEL corporations available, or unlock the two new ones after the first clear?
   - also: Which corporations unlock after the first clear, if not all six non-REBEL corporations start available?
   - sources: [gdd/s08](../gdd/s08.md)
328. **gamepad scope** (2 drafts): Is gamepad support dropped from the platform line for 1.0, or only deprioritized?
   - also: Is gamepad support dropped for 1.0 only, or removed from the pitch entirely?
   - sources: [gdd/s01](../gdd/s01.md), [gdd/s13](../gdd/s13.md)
329. **audit system fallback** (1 draft): If N6 slips, is the fight acceptable as data-only (slices and resistance), or should it wait for the listener?
   - sources: [enemies/compliance_officer](../enemies/compliance_officer.md)
330. **cache node status** (1 draft): Should the Cache vetting result be recorded here as an open item until decided?
   - sources: [gdd/s13](../gdd/s13.md)
331. **card slot default state** (1 draft): Should the card slot be on by default, or should the first release be slice-only (card slot empty) until the card pass lands?
   - sources: [nodes/workshop](../nodes/workshop.md)
332. **card upgrade link** (1 draft): Does the card-upgrade link field need a new data convention like `cold_snap_plus`?
   - sources: [card_upgrades/cold_snap](../card_upgrades/cold_snap.md)
333. **card upgrade replacement model** (1 draft): Should a card's + version replace the base in the deck in place, or be a separate reward-pool entry?
   - sources: [card_upgrades/tap_tap](../card_upgrades/tap_tap.md)
334. **card upgrade storage** (1 draft): Does the upgraded variant keep the same `id` plus a `plus` flag, or a separate resource with `upgrades_to`?
   - sources: [card_upgrades/scrap_code](../card_upgrades/scrap_code.md)
335. **elite flag removal** (1 draft): Is dropping `is_elite` from a mini-boss acceptable for the reward and route code that currently reads it?
   - sources: [enemies/city_manager](../enemies/city_manager.md)
336. **elite variant** (1 draft): Should Cargo Hauler lose its elite-size history entirely, or do we want a "Heavy Hauler" elite variant later?
   - sources: [enemies/cargo_hauler](../enemies/cargo_hauler.md)
337. **enemy placeholder swap** (1 draft): Should an Aurelian elite replace `geostationary_guard` in choice 2 before content pass, or is a borrowed enemy acceptable?
   - sources: [events/12_paths_aurelian](../events/12_paths_aurelian.md)
338. **hub exploit eligibility** (1 draft): Should P2's resistance-1 hub be a counter Exploit target in a later elite-buff pass, or is that boss-only?
   - sources: [enemies/zoning_board](../enemies/zoning_board.md)
339. **non raid bonus timing** (1 draft): Should Phantom's non-raid half ship with raid half or wait for N16?
   - sources: [station/phantom](../station/phantom.md)
340. **pillar scope** (1 draft): Should pillar 5 ("every enemy is designed") be a pillar, or live in Section 11 only?
   - sources: [gdd/s01](../gdd/s01.md)
341. **progression teaching** (1 draft): Should T1 use the fallback 5-tick layout so it teaches nudging before uneven slices appear?
   - sources: [enemies/patrol_unit](../enemies/patrol_unit.md)
342. **scope and length** (1 draft): Is the extra circuit (the 15-layer route) worth keeping alongside the override, or does it make the HQ too long for a campaign that already runs 605 min against a 395 target?
   - sources: [hq/orbital](../hq/orbital.md)
343. **section organization** (1 draft): Should "Decided, not yet built" stay in section 13, or move into sections 2–11 as rules with build state tracked elsewhere?
   - sources: [gdd/s13](../gdd/s13.md)
344. **tutorial opening constraint** (1 draft): Should the first-ever Halcyon fight force a fixed opening (needle on the under-pointer Citation) as a tutorial beat, or stay on the normal random respin?
   - sources: [enemies/parking_warden](../enemies/parking_warden.md)
345. **upgrade card id scope** (1 draft): Should the upgrade be a separate card id so the base can appear in pools, or a swap of the same card in place?
   - sources: [card_upgrades/ghost_step](../card_upgrades/ghost_step.md)
346. **upgrade data structure** (1 draft): Should upgrades be separate card ids or an `upgrade_of` link plus a `level` field on CardData?
   - sources: [card_upgrades/firewall](../card_upgrades/firewall.md)
347. **upgrade replacement method** (1 draft): Does the upgrade pass keep both versions as separate card ids in the deck, or swap in place with an `upgrade_of` link?
   - sources: [card_upgrades/cache](../card_upgrades/cache.md)

## rules

348. **corrupted free nudge cost** (8 drafts): Does a free nudge on a CORRUPTED slice still cost 1 RAM?
   - also: Does a free nudge from Calibrate on a CORRUPTED slice cost 0 or 1 under R9?
   - also: Does CORRUPTED's ×2 RAM apply to the free nudge (i.e. does the free nudge cost 1 on a corrupted slice)?
   - sources: [card_upgrades/backspin](../card_upgrades/backspin.md), [card_upgrades/calibrate](../card_upgrades/calibrate.md), [catalog/status](../catalog/status.md), [enemies/account_manager](../enemies/account_manager.md), [enemies/collections_agent](../enemies/collections_agent.md), [enemies/dosage_dispenser](../enemies/dosage_dispenser.md), [gdd/s02](../gdd/s02.md), [gdd/s11](../gdd/s11.md)
349. **drone destruction semantics** (5 drafts): Does a drone kill count as an "enemy destroyed" for Daemons and rewards (R12 open question 7)?
   - also: Should a replaced drone count as destroyed for Daemons and rewards?
   - also: Do replaced Relays count as destroyed for Daemons like Botnet Seed?
   - sources: [enemies/care_swarm](../enemies/care_swarm.md), [enemies/drone_dispatcher](../enemies/drone_dispatcher.md), [enemies/launch_pad](../enemies/launch_pad.md), [enemies/mission_director](../enemies/mission_director.md), [firmware/new_chips](../firmware/new_chips.md)
350. **enemy shield cap** (4 drafts): Do enemy shields share the player's shield_cap or have their own cap?
   - also: Is the Shield cap of 15 right for an enemy, or should the enemy's flat shield be uncapped?
   - also: Does the Meter's shield cap equal the player's shield_cap 15, or does an enemy percent shield need its own cap?
   - sources: [bosses/aurelian](../bosses/aurelian.md), [enemies/geostationary_guard](../enemies/geostationary_guard.md), [enemies/utility_meter](../enemies/utility_meter.md), [gdd/s13](../gdd/s13.md)
351. **free nudge scope** (4 drafts): Should the free inner nudge be ring-restricted, or use the generic free-nudge counter like Calibrate?
   - also: Should free nudges granted by several cards stack additively, or be capped per turn at 3?
   - also: Should the free nudge be restricted to your own wheel, or does "next nudge" cover any wheel?
   - sources: [card_upgrades/ring_tap](../card_upgrades/ring_tap.md), [card_upgrades/torque_wrench](../card_upgrades/torque_wrench.md), [card_upgrades/twist](../card_upgrades/twist.md), [nodes/cache](../nodes/cache.md)
352. **corrupted enemy effect** (3 drafts): Should CORRUPTED on an enemy wheel have a real effect at all under R9, or does this card family lack purpose without one?
   - also: Should the rider's free inner nudge be exempt from CORRUPTED 2× RAM rule, or count as card action paying doubled cost?
   - also: What does CORRUPTED on enemy wheels do now that it is a RAM debuff?
   - sources: [card_upgrades/malware_drop](../card_upgrades/malware_drop.md), [card_upgrades/ring_lock](../card_upgrades/ring_lock.md), [gdd/s02](../gdd/s02.md)
353. **echo listener trigger** (3 drafts): Does Echo trigger on a class hook's second resolve (Breaker double), or only once per Perfect slice?
   - also: Should the Echo listener hit once per resolve or once per Perfect needle?
   - also: Should Riot Response (the P2 listener) fire on ON_NUDGE instead, so a good player has two ways to play around it?
   - sources: [enemies/echo_process](../enemies/echo_process.md), [enemies/rc_template_elite_b](../enemies/rc_template_elite_b.md), [enemies/riot_control](../enemies/riot_control.md)
354. **output down on weak** (3 drafts): Does ×1 OUTPUT_DOWN on a WEAK landing still apply?
   - also: Does a WEAK landing on Citation still apply OUTPUT_DOWN, or is the pair's quiet turn truly free?
   - also: Does OUTPUT_DOWN ×1 on a WEAK landing still apply (R8 default yes)? If not, the Citation 4-tick edge is a free dodge.
   - sources: [enemies/handler_proxy](../enemies/handler_proxy.md), [enemies/mirror_script](../enemies/mirror_script.md), [enemies/parking_warden](../enemies/parking_warden.md)
355. **sandbox negation scope** (3 drafts): Does SANDBOX negating Report's hit count as negating a whole attack, or does listener hit sit outside resolution?
   - also: Should Containment (SANDBOX) read its negation on the enemy side too, or is a player-facing "negates one attack" only?
   - also: Should a SANDBOX charge negate one threat's whole step or one damage event per threat per step?
   - sources: [enemies/loyalty_test](../enemies/loyalty_test.md), [enemies/orbital_debris](../enemies/orbital_debris.md), [station/phantom](../station/phantom.md)
356. **satellite movement class** (3 drafts): Which class moves satellites, and does Undock survive?
   - also: Which operative class may move and nudge satellites, and is it a Hub passive or a Perfect hook?
   - also: Which operative class moves satellites, whether Undock stays, and whether a replaced satellite counts as destroyed.
   - sources: [gdd/s02](../gdd/s02.md), [gdd/s05](../gdd/s05.md), [gdd/s13](../gdd/s13.md)
357. **swap level retention** (3 drafts): Should a type swap keep its Level (minus one) or always reset to Level I?
   - also: Does a swap in a flash keep the Level (a Level III Overflow swapped for a Shim arrives as Level III), or reset to I?
   - also: Does a swap to another type keep any Level progress?
   - sources: [slice_upgrades/hotfix](../slice_upgrades/hotfix.md), [slice_upgrades/overflow](../slice_upgrades/overflow.md), [slice_upgrades/shim](../slice_upgrades/shim.md)
358. **combat override scope** (2 drafts): Should "next 3 combats" count only fights, or also elite and Rack fights?
   - also: Should "next 2 combats" count only fights, or Terminal-skipped nodes too?
   - sources: [events/03_future_halcyon](../events/03_future_halcyon.md), [events/04_future_orbital](../events/04_future_orbital.md)
359. **combo enemy spin** (2 drafts): Should the spin combo apply on the first card of the turn when Counter-Spin+ follows an enemy-triggered spin, or only on player-played spins?
   - also: Should the refund apply to the first spin of the turn too, or only the combo?
   - sources: [card_upgrades/counter_spin](../card_upgrades/counter_spin.md), [card_upgrades/momentum](../card_upgrades/momentum.md)
360. **corrupted enemy interaction** (2 drafts): Should a re-armed guard be allowed on a slice carrying CORRUPTED, i.e. does it stop the debuff from spreading but not remove it?
   - also: The effect of CORRUPTED on enemy wheels now that it is a RAM debuff.
   - sources: [firmware/hardened](../firmware/hardened.md), [gdd/s13](../gdd/s13.md)
361. **corruption cleanse interaction** (2 drafts): Should the second trigger of a doubled nudge card repeat for free in RAM, or should corrupted slices charge the repeat too?
   - also: Should the chosen-slice picker allow skipping when no slice is CORRUPTED, so the card isn't blocked from playing?
   - sources: [card_upgrades/overclock_nudges](../card_upgrades/overclock_nudges.md), [card_upgrades/patch_up](../card_upgrades/patch_up.md)
362. **echo damage scaling** (2 drafts): Is flat 4 tax too weak to change play against Perfect-hook classes, or use PERCENT of max HP instead?
   - also: Should Echo scale with the landed slice's output (60%, needs N6 rider) or be flat amount 5?
   - sources: [enemies/loyalty_test](../enemies/loyalty_test.md), [enemies/the_handler](../enemies/the_handler.md)
363. **encrypt interaction** (2 drafts): Do ENCRYPTED slices on the player's wheel stop the hub dose entirely, or does the hub bypass them?
   - also: Should Flare Feed in P2 skip the player's slices that are ENCRYPTED, giving Encrypt a clear role as the counter?
   - sources: [enemies/dosage_dispenser](../enemies/dosage_dispenser.md), [enemies/station_commander](../enemies/station_commander.md)
364. **escort respawn sustain** (2 drafts): Should the escort's respawn every 3rd turn count as "sustain" for the 30% cap, since it re-creates a bodyguard?
   - also: Should Defrag count as "sustain" under the 30% cap, since it expires every turn?
   - sources: [enemies/last_mile_enforcer](../enemies/last_mile_enforcer.md), [enemies/patrol_unit](../enemies/patrol_unit.md)
365. **exploit breach requirements** (2 drafts): If an Exploit's building is unbuilt, does the key still count toward min_exploits_for_breach?
   - also: Do any 3 of the drawn 5 Exploits open the breach, or do some Exploits stay fixed gate types?
   - sources: [gdd/s04](../gdd/s04.md), [gdd/s11](../gdd/s11.md)
366. **exploit gates system** (2 drafts): Whether any 3 of the drawn Exploits open the breach, or the Intel / Breach / Virus gate types stay fixed; the number drawn per Grid (5).
   - also: Are Intel / Breach / Virus still fixed gate types, or which Meridian Exploits own each building?
   - sources: [gdd/s13](../gdd/s13.md), [hq/meridian](../hq/meridian.md)
367. **flare landing threshold** (2 drafts): Does a Flare landing on a WEAK tier still apply its status?
   - also: May Flare apply on a WEAK landing, as Q11 proposes, or only on Perfect/center?
   - sources: [enemies/geostationary_guard](../enemies/geostationary_guard.md), [enemies/tracking_station](../enemies/tracking_station.md)
368. **free nudge stacking** (2 drafts): Is "gain a free nudge" additive with the once-per-turn free nudge, or does it restore it after use?
   - also: Does the free nudge stack with the turn's free nudge or only fill the turn's first free slot when already used?
   - sources: [card_upgrades/pull](../card_upgrades/pull.md), [card_upgrades/twist](../card_upgrades/twist.md)
369. **free nudge trigger condition** (2 drafts): Should the free-nudge rider trigger when resistance was already 0 before the play?
   - also: Should the free-nudge rider trigger only on exact clear to 0, or also when resistance was already 0?
   - sources: [card_upgrades/deep_strip](../card_upgrades/deep_strip.md), [card_upgrades/strip](../card_upgrades/strip.md)
370. **gaze advancement trigger** (2 drafts): Should the gaze advance per completed node or per layer travelled?
   - also: Should the Head advance on completed nodes (current draft, player can stall) or on a hard per-layer step (no stall, but no planning from rests)?
   - sources: [hq/halcyon](../hq/halcyon.md), [hq/tethys](../hq/tethys.md)
371. **ghost resistance interaction** (2 drafts): Should the extra draw fire if the earlier spin was fully absorbed by resistance?
   - also: Does Ghost's "first nudge each turn ignores resistance" apply to every nudge in this card, or only the first?
   - sources: [card_upgrades/tailspin](../card_upgrades/tailspin.md), [card_upgrades/tap_tap](../card_upgrades/tap_tap.md)
372. **heat reduction scaling** (2 drafts): Should the total be capped at 2 Heat per combat, or should a Perfect give 1 and a Good 1, ignoring tier?
   - also: Does HEAT_SINK_PCT from ICE already scale node Heat reduction or only Daemons?
   - sources: [firmware/coolant_loop](../firmware/coolant_loop.md), [nodes/heat_sink](../nodes/heat_sink.md)
373. **map edit validation** (2 drafts): May a PATHS edit remove the guaranteed Mainframe in layers 3-5, or should edits be validated against generation guarantees?
   - also: Should `cut_layer_option` ever remove the only remaining path to a Server Rack, or must the validator refuse it?
   - sources: [events/11_paths_orbital](../events/11_paths_orbital.md), [events/12_paths_aurelian](../events/12_paths_aurelian.md)
374. **overclocked multiplier scope** (2 drafts): Should the 2× multiplier be authored per card (the `multiplier` field) or become a global OVERCLOCKED tuning value?
   - also: Does the OVERCLOCKED multiplier live on the status instance or is it global?
   - sources: [card_upgrades/hot_patch](../card_upgrades/hot_patch.md), [card_upgrades/overdrive](../card_upgrades/overdrive.md)
375. **parasite duration** (2 drafts): Whether the Parasite ring rotates with the player wheel (proposed: yes).
   - also: Can an enemy parasite replace a Rider, or only jam it for one turn?
   - sources: [gdd/s13](../gdd/s13.md), [inner_ring/c](../inner_ring/c.md)
376. **replaced satellite destroyed** (2 drafts): Does a replaced satellite count as destroyed for Daemon and reward purposes?
   - sources: [gdd/s02](../gdd/s02.md), [gdd/s05](../gdd/s05.md)
377. **respin lock scope** (2 drafts): Should the + version guard against enemy spins on your inner ring, or only your own spins?
   - also: Does the P3 respin lock block only player-initiated respins, leaving the start-of-turn respin?
   - sources: [card_upgrades/ring_lock](../card_upgrades/ring_lock.md), [enemies/logistics_director](../enemies/logistics_director.md)
378. **sandbox drain interaction** (2 drafts): Does a Surcharge drain still happen if SANDBOX negates the hit? Proposed no, it negates the whole resolution.
   - also: Should the chip's damage ignore SANDBOX like a rider, so hybrid slices have reason against sandboxed bosses?
   - sources: [enemies/tariff_collector](../enemies/tariff_collector.md), [firmware/barbed_wire](../firmware/barbed_wire.md)
379. **account manager placement** (1 draft): Does the Account Manager appear once (either rung 5 or 9), or always at rung 9 with rung 5 being elite only?
   - sources: [hq/solace](../hq/solace.md)
380. **alternate bonus range** (1 draft): Should class alternates be allowed a different bonus range (hops), or only different numbers?
   - sources: [nodes/safehouse](../nodes/safehouse.md)
381. **arena bout forfeit** (1 draft): Should Arena Bout allow a "decline the bout" refund (forfeit the wheel result) at −10 Cycles, to prevent forced elites at low HP?
   - sources: [events/25_wheel_aurelian](../events/25_wheel_aurelian.md)
382. **asset cap drones** (1 draft): Should drones count toward the raid asset cap, or live in their own pool?
   - sources: [station/botnet](../station/botnet.md)
383. **audit trigger scope** (1 draft): Is Audit's trigger "any paid nudge" right, or only paid nudges on the enemy wheel, so the player may still spend RAM on their own wheel freely?
   - sources: [enemies/compliance_officer](../enemies/compliance_officer.md)
384. **ban threshold edge cases** (1 draft): Does a 0-cost or free card count toward the P2 Ban threshold, and does a replayed card count twice?
   - sources: [enemies/civic_core](../enemies/civic_core.md)
385. **bay locked duration** (1 draft): Should BAY_LOCKED be a status that lasts N turns, or a parasite effect that lasts as long as its segment stays latched?
   - sources: [inner_ring/b](../inner_ring/b.md)
386. **block carry mechanics** (1 draft): Should a Level-IV carry-over be allowed to break the "BLOCK expires" rule, or be converted to SHIELD to keep the trio distinct?
   - sources: [slice_upgrades/defrag](../slice_upgrades/defrag.md)
387. **block sustain cap** (1 draft): Does BLOCK on the enemy count against the 30 % sustain cap, or only heal and shield?
   - sources: [enemies/rc_template_elite](../enemies/rc_template_elite.md)
388. **boss retry progression** (1 draft): Boss retry state: after failed showdown, re-arm with lanes cleared or force replay?
   - sources: [hq/rebel_cell](../hq/rebel_cell.md)
389. **botnet asset pool** (1 draft): Does the Botnet's free asset use the Armory type pool, or is it a fixed Safehouse-specific TURRET variant?
   - sources: [nodes/safehouse](../nodes/safehouse.md)
390. **breach mechanic** (1 draft): Should Breach ("Emergency Override") now turn off the boss heal instead of removing a pointer?
   - sources: [enemies/civic_core](../enemies/civic_core.md)
391. **breach phase interaction** (1 draft): Does breached Hub still run phase-change hub_overrides mid-turn or does breach end at phase change?
   - sources: [card_upgrades/hub_breach](../card_upgrades/hub_breach.md)
392. **cache exploit rewards** (1 draft): Should a Cache reward slice ever be Exploit-adjacent (access key hint), or does that blur the Rack's role?
   - sources: [nodes/cache](../nodes/cache.md)
393. **calibrated centre definition** (1 draft): Should a Calibrated chip's raised P ticks on even slices count as "centre" for Shunt, or is Shunt keyed to the geometric centre only?
   - sources: [firmware/shunt](../firmware/shunt.md)
394. **charge persistence** (1 draft): Should Charge persist between raids (a long-term bank) or reset at raid end?
   - sources: [station/overclocker](../station/overclocker.md)
395. **chip stacking rules** (1 draft): Is Burner meant to be exclusive with other output chips on the same slice, or may it stack with Patch+ (1.5 × 1.5 = 2.25)?
   - sources: [firmware/burner](../firmware/burner.md)
396. **class hook wheel interaction** (1 draft): Should the operative's own class hooks (Rigger's free nudge, Ghost's resistance bypass) feed the event wheel's nudge budget, or is it a fixed pool of its own?
   - sources: [events/23_wheel_orbital](../events/23_wheel_orbital.md)
397. **cleanse stacks** (1 draft): Does Cleanse remove all TIER_DOWN stacks on a slice or one? The design assumes all, which makes it a strong P3 card.
   - sources: [enemies/civic_core](../enemies/civic_core.md)
398. **cleanse timing enemy statuses** (1 draft): Should the cleanse also work on enemy-applied statuses from listeners (N6) mid-resolve, or only those present at turn start?
   - sources: [firmware/nanite_mesh](../firmware/nanite_mesh.md)
399. **code blue blocked damage** (1 draft): Does Code Blue rider fire when BLOCK absorbs all damage? Proposed: yes, making SANDBOX the only counter.
   - sources: [enemies/renewal_engine](../enemies/renewal_engine.md)
400. **cold chain virus fit** (1 draft): Does Cold Chain's Virus counter fit, since Virus today only corrupts slices?
   - sources: [enemies/the_manifest](../enemies/the_manifest.md)
401. **combat counting definition** (1 draft): Should "the combat after" skip non-fight nodes only, and count Elite fights, or only the next Normal Router?
   - sources: [events/06_future_aurelian](../events/06_future_aurelian.md)
402. **combat heat application** (1 draft): Does the Referral fight's Heat apply even if the player wins, or only on a loss?
   - sources: [events/20_wheel_solace](../events/20_wheel_solace.md)
403. **combat outcome classification** (1 draft): Does Slice 5's fight count as a normal Router fight for Heat and rewards?
   - sources: [events/24_wheel_rebel_cell](../events/24_wheel_rebel_cell.md)
404. **combat reward stacking** (1 draft): Does the Audit Flag fight win count as clearing the event wheel reward as well, or does the Cycle stake replace it?
   - sources: [events/21_wheel_meridian](../events/21_wheel_meridian.md)
405. **combat reward structure** (1 draft): Should a combat reward be a single choice in EventChoiceData (victory branch) or a separate victory_effects list?
   - sources: [events/19_ambush_tethys](../events/19_ambush_tethys.md)
406. **combat stat attribution** (1 draft): Does a won impromptu fight count toward Rank and Daemon counters?
   - sources: [events/16_ambush_halcyon](../events/16_ambush_halcyon.md)
407. **conditional effects on commons** (1 draft): Does a card with conditions on state count as "different from the role"? If so, use 9-flat fallback instead.
   - sources: [card_upgrades/firewall](../card_upgrades/firewall.md)
408. **conditional rider simplification** (1 draft): Should the ENCRYPT rider apply when the chosen slice is not CORRUPTED, with the condition dropped for simplicity and the RAM cost raised to 2?
   - sources: [card_upgrades/sanitize](../card_upgrades/sanitize.md)
409. **conditional spin tracking** (1 draft): Should the conditional reuse Momentum's check, or should "already spun" count the first free nudge and spins from Firmware?
   - sources: [card_upgrades/gear_mesh](../card_upgrades/gear_mesh.md)
410. **consolation condition scope** (1 draft): Should the rider count a NULL landing on an enemy wheel (the player respinning the enemy's wheel) as a consolation, or only on the player's own wheel?
   - sources: [card_upgrades/reroll](../card_upgrades/reroll.md)
411. **corrupted cost pointer scope** (1 draft): For cards aimed at an enemy wheel, which pointer's slice decides the 2× corrupted cost?
   - sources: [gdd/s02](../gdd/s02.md)
412. **corrupted duration** (1 draft): Should CORRUPTED from Curfew last the whole netrun instead of just the next combat?
   - sources: [events/22_wheel_halcyon](../events/22_wheel_halcyon.md)
413. **corrupted enemy mechanic** (1 draft): Virus on enemy wheels: under R9, what does CORRUPTED do on an enemy wheel (assume double RAM cost)?
   - sources: [hq/rebel_cell](../hq/rebel_cell.md)
414. **corrupted enemy ram** (1 draft): Do corrupted enemy slices pay RAM costs?
   - sources: [gdd/s11](../gdd/s11.md)
415. **corrupted enemy wheels** (1 draft): Should CORRUPTED on enemy wheels exist at all, or does Corrupt become OUTPUT_DOWN permanently?
   - sources: [inner_ring/b](../inner_ring/b.md)
416. **corrupted slice tax** (1 draft): Should a 0-RAM card cost 0 on a CORRUPTED slice, or a minimum of 1 RAM, so the free fix doesn't dodge the R9 tax?
   - sources: [card_upgrades/micro_adjust](../card_upgrades/micro_adjust.md)
417. **countdown overflow stacking** (1 draft): Does the Countdown's extra Overflow at 3 stack with the Director's normal pointer resolve, or replace it?
   - sources: [enemies/mission_director](../enemies/mission_director.md)
418. **counterstrike pierce interaction** (1 draft): Should the counter damage be blocked by an enemy's BLOCK or SHIELD, or should it pierce?
   - sources: [firmware/counterstrike](../firmware/counterstrike.md)
419. **cross link timing** (1 draft): Should a cross-link opened by choice 3 count as a new raid entry point immediately, or only after the next Heat threshold?
   - sources: [events/28_raidwin_rebel_cell](../events/28_raidwin_rebel_cell.md)
420. **curfew card interaction** (1 draft): Should Curfew's lock extend to cards in a later tier, or is "cards always work" a hard rule for the corporation?
   - sources: [enemies/city_manager](../enemies/city_manager.md)
421. **curfew lock scope** (1 draft): Does the Curfew lock also refuse the free nudge, or only paid ones?
   - sources: [enemies/city_manager](../enemies/city_manager.md)
422. **curse duration** (1 draft): Are curses permanent for the run, or do they expire after N combats as drafted (3)?
   - sources: [nodes/black_market](../nodes/black_market.md)
423. **damage definition** (1 draft): Does a heal that the player's hit cancels count as damage if a Block absorbed all of it?
   - sources: [enemies/triage_unit](../enemies/triage_unit.md)
424. **debt scope** (1 draft): Should an unpaid borrow carry into the next netrun (Grid-level debt), or stay within the run?
   - sources: [events/30_paths_any](../events/30_paths_any.md)
425. **detonate fallback design** (1 draft): Is losing the "count your overclocks" question acceptable if N20 `hits_per_target_status` slips (the flat-10 fallback)?
   - sources: [enemies/station_commander](../enemies/station_commander.md)
426. **detour weak interaction** (1 draft): Does a Detour read at WEAK tier still negate the attack, or should WEAK landing only negate half?
   - sources: [enemies/surveillance_mast](../enemies/surveillance_mast.md)
427. **divert persistence** (1 draft): Does the player keep a permanent Divert (a node stays drained for the run), or should Divert fade after one tide cycle to keep the puzzle repeatable?
   - sources: [hq/tethys](../hq/tethys.md)
428. **drain overflow penalty** (1 draft): Should the drain be capped at the player's current RAM (no going negative), with excess becoming a HP penalty?
   - sources: [enemies/tariff_collector](../enemies/tariff_collector.md)
429. **draw refund conditions** (1 draft): Should the refund be conditional (only if you drew 3 cards) or flat as drafted?
   - sources: [card_upgrades/data_surge](../card_upgrades/data_surge.md)
430. **drone phase transition** (1 draft): Should the drone be killed or removed at the transition?
   - sources: [enemies/geostationary_guard](../enemies/geostationary_guard.md)
431. **drone redock behavior** (1 draft): Should the drone re-dock after death once per fight, or never?
   - sources: [enemies/collections_agent](../enemies/collections_agent.md)
432. **drone refresh scope** (1 draft): Should the refresh also work on a drone docked by the TROJAN slice, or only on drones from this card?
   - sources: [card_upgrades/spawn_drone](../card_upgrades/spawn_drone.md)
433. **drone spawn cap** (1 draft): Should the drone's `max_active` be 1 with REPLACE, or 2 so the replacement rule is never exercised?
   - sources: [enemies/launch_pad](../enemies/launch_pad.md)
434. **drone spawn placement** (1 draft): Should the Hangar launch land on the pointer's slice (hit guard immediately) or on the slice opposite to give one turn of warning?
   - sources: [enemies/drone_dispatcher](../enemies/drone_dispatcher.md)
435. **drone wheel contents** (1 draft): Is `echo_drone.tres` really Shim 3 / Null? I did not have its file and assumed it from the brief's description.
   - sources: [enemies/dead_drop](../enemies/dead_drop.md)
436. **echo listener firmware interaction** (1 draft): Does a Good landing that the Calibrated Firmware raises to Perfect still trigger Echo?
   - sources: [enemies/echo_process](../enemies/echo_process.md)
437. **echo listener multi wheel** (1 draft): Should Echo apply once per Perfect or once per turn on a 2-wheel (drone/satellite) Perfect?
   - sources: [enemies/echo_process](../enemies/echo_process.md)
438. **encrypted flare interaction** (1 draft): Does a flared slice that is Encrypted absorb the Flare, and is that the intended cheap answer at L1-2?
   - sources: [enemies/uplink_relay](../enemies/uplink_relay.md)
439. **encrypted self absorption** (1 draft): Should ENCRYPTED applied through Cleanse+ be exempt from absorbing its own re-corruption in the same resolve?
   - sources: [card_upgrades/cleanse](../card_upgrades/cleanse.md)
440. **encrypted status interaction** (1 draft): Does ENCRYPTED absorb Parasite ring latches, or only statuses?
   - sources: [card_upgrades/armor_plate](../card_upgrades/armor_plate.md)
441. **enrage visibility** (1 draft): Should the enrage countdown be hidden by the Chart Hidden buff, or always visible?
   - sources: [gdd/s09](../gdd/s09.md)
442. **exploit breach availability** (1 draft): Should DOWN or TAKEN Exploit buildings deduct from min_exploits_for_breach, or only block breach attempts?
   - sources: [gdd/s03](../gdd/s03.md)
443. **exploit corrupted miniboss** (1 draft): Does Virus Exploit's CORRUPTED on boss slices affect the Handler mini-boss, given CORRUPTED is now a RAM debuff only?
   - sources: [enemies/the_handler](../enemies/the_handler.md)
444. **exploit interaction** (1 draft): Should Hub Breach bypass boss hub-based Exploit-counterable buffs or stay immune to keep Exploit meaningful?
   - sources: [card_upgrades/hub_breach](../card_upgrades/hub_breach.md)
445. **exposed entity status** (1 draft): Is EXPOSED (a player-offensive entity status) acceptable under the anti-Firmware ruling, or should player damage amplification live only in cards?
   - sources: [catalog/status](../catalog/status.md)
446. **exposed mark placement** (1 draft): Can the EXPOSED mark be moved onto a node that is currently DOWN?
   - sources: [gdd/s07](../gdd/s07.md)
447. **fence accept scope** (1 draft): Can the Fence accept Server Rack Schematics assets or the Armory pieces, or only deck, Firmware and Daemons?
   - sources: [nodes/black_market](../nodes/black_market.md)
448. **fight defeat consequences** (1 draft): Should a lost impromptu fight cost the operative nothing beyond the HP lost and the Heat stake, or end the node (forcing a retreat)?
   - sources: [events/17_ambush_orbital](../events/17_ambush_orbital.md)
449. **firmware rider propagation** (1 draft): Should a copied neighbour fire its own Firmware riders, or only its base slice?
   - sources: [firmware/mirror](../firmware/mirror.md)
450. **flare corrupted interaction** (1 draft): Does a Flare landing on an already-CORRUPTED slice do nothing, or upgrade it to a stronger debuff (R9 leaves it unspecified)?
   - sources: [enemies/weather_satellite](../enemies/weather_satellite.md)
451. **flare pick prediction** (1 draft): Should the Flare pick be random or deterministic (opposite side), so players can predict and use the flared slice?
   - sources: [enemies/uplink_relay](../enemies/uplink_relay.md)
452. **flying threat turret interaction** (1 draft): Do FLYING threats ignore the built-in Firewall Relay turret's targeting as well, or only player assets?
   - sources: [gdd/s07](../gdd/s07.md)
453. **forecast history vs preview** (1 draft): Is the Forecast landing record (this turn vs previous turn) acceptable as new state, or should DISPATCH read the current staged landing at preview time?
   - sources: [enemies/dispatch_core](../enemies/dispatch_core.md)
454. **free nudge definition** (1 draft): Does the free nudge after a card-granted nudge count as "paid" for Late Fee, or only RAM-costed nudges?
   - sources: [enemies/billing_daemon](../enemies/billing_daemon.md)
455. **free nudge effect type** (1 draft): Is "free nudge" an EffectData type today, or only a Calibrate custom handler?
   - sources: [card_upgrades/feather_touch](../card_upgrades/feather_touch.md)
456. **free nudge expiration** (1 draft): Does the free nudge need a "this turn only, unused expires" rule to stay deterministic across rewinds?
   - sources: [card_upgrades/flip_switch](../card_upgrades/flip_switch.md)
457. **free nudge restriction** (1 draft): Should the free nudge be restricted to your own wheel when the spin targets the enemy wheel?
   - sources: [card_upgrades/brute_spin](../card_upgrades/brute_spin.md)
458. **freeze interaction orbit** (1 draft): Does Freeze on the enemy wheel stop the orbit too, or only the respin?
   - sources: [enemies/ground_control](../enemies/ground_control.md)
459. **freeze nudge interaction** (1 draft): Should the + version also skip the target's next nudge, or keep one-turn Freeze only?
   - sources: [card_upgrades/cold_snap](../card_upgrades/cold_snap.md)
460. **freeze phase interaction** (1 draft): Should Freeze+ on an enemy phase-change wheel survive the `_apply_wheel_override`, or should phase entry clear the freeze?
   - sources: [card_upgrades/freeze](../card_upgrades/freeze.md)
461. **ghost decrypt scope** (1 draft): Does a Ghost's free decrypt apply to every encrypted threat, or one per raid?
   - sources: [gdd/s07](../gdd/s07.md)
462. **hand cap mechanics** (1 draft): Should the draw bonus respect the 5-card hand cap, or can the hand exceed 5 mid-turn?
   - sources: [card_upgrades/scrap_code](../card_upgrades/scrap_code.md)
463. **heal rounding** (1 draft): Percent heal rounding (1.5 % of 300 = 4.5): round up, to nearest, or keep integer 1 % / 2 %?
   - sources: [enemies/renewal_engine](../enemies/renewal_engine.md)
464. **healing during phase parking** (1 draft): Should a heal-on-hit chip be allowed to heal while an R3 floor holds the enemy, or should healing pause while the boss is parked?
   - sources: [firmware/siphon](../firmware/siphon.md)
465. **heat retaliation trigger** (1 draft): Does paying Heat here count as "Heat gained from an objective" for retaliation (4.4), or is it exempt?
   - sources: [nodes/black_market](../nodes/black_market.md)
466. **heat sink raid targeting** (1 draft): Does a Heat Sink count toward raid targeting, and what are its numbers?
   - sources: [gdd/s03](../gdd/s03.md)
467. **heat threshold timing** (1 draft): Does Heat-for-nudge count as a MINOR Heat threshold trigger mid-event, or is it deferred to event end?
   - sources: [events/25_wheel_aurelian](../events/25_wheel_aurelian.md)
468. **home adjacent sacrifice spill** (1 draft): May a Home-adjacent node be sacrificed deliberately (spotlight there), and does that need a spill cap?
   - sources: [raids/main](../raids/main.md)
469. **hq boss and rack placement** (1 draft): Does the final-layer mini-boss replace the Rack on HQ netruns, or does the HQ boss take its place?
   - sources: [gdd/s04](../gdd/s04.md)
470. **hq combat slot cost** (1 draft): Does an HQ-view impromptu fight (choice 4) cost the operative a netrun slot, or is it free between runs?
   - sources: [events/29_hqview_any](../events/29_hqview_any.md)
471. **hq netrun length and minimum** (1 draft): Does an HQ netrun count toward the 8-run minimum path, and how long may it be (layers)?
   - sources: [gdd/s04](../gdd/s04.md)
472. **hq rest inclusion** (1 draft): Do HQ netruns (unique per corporation) include REST nodes, or is the sustain there authored per HQ?
   - sources: [nodes/rest](../nodes/rest.md)
473. **hub breach buff interaction** (1 draft): Does the Hub breach on a boss whose heal is a buff (Metabolism) get ignored, and is that the intended Exploit tension?
   - sources: [card_upgrades/shatter](../card_upgrades/shatter.md)
474. **hub breach persistence** (1 draft): Should a Hub breach survive a boss `hub_override` at a phase change (R6 covers statuses, not Hub state)?
   - sources: [card_upgrades/short_circuit](../card_upgrades/short_circuit.md)
475. **inner ring nudge fallback** (1 draft): Does the fx1 inner-ring nudge need a fallback when the target has no inner ring (refund 1 RAM, or fall back to the outer ring)?
   - sources: [card_upgrades/double_jam](../card_upgrades/double_jam.md)
476. **inner ring rewire** (1 draft): Is the Inner Ring included in REWIRE once the G1 redesign settles how segments are manipulated?
   - sources: [nodes/rest](../nodes/rest.md)
477. **isolated node launch source** (1 draft): Does a cut-off but powered node region allow launches from its own nodes, or only if linked to home server?
   - sources: [gdd/s03](../gdd/s03.md)
478. **landing quality reading** (1 draft): Should Leech read the sub-tick quality of the actual landing, or the slice's best tick, on 2-tick slices where every landing is Good?
   - sources: [firmware/leech](../firmware/leech.md)
479. **late fee linked bus** (1 draft): Does Late Fee trigger on Linked Bus nudges (a Daemon nudge on the enemy wheel that also moves yours, free)?
   - sources: [enemies/account_manager](../enemies/account_manager.md)
480. **leash targeting** (1 draft): Should Leash target the slice your pointer will read this resolve, or your best slice?
   - sources: [enemies/handler_proxy](../enemies/handler_proxy.md)
481. **level four branching** (1 draft): Should Level IV carry its branch (Hive vs Seeder) or merge into one slice?
   - sources: [slice_upgrades/trojan](../slice_upgrades/trojan.md)
482. **level iv branch respec** (1 draft): Should Level IV branches be exclusive (one pick, permanent), or can a Rack respec a branch?
   - sources: [slice_upgrades/sandbox](../slice_upgrades/sandbox.md)
483. **link closure targeting** (1 draft): Should closing the link target the highest-tier option deterministically, or should the player choose which one to foreclose?
   - sources: [events/10_paths_halcyon](../events/10_paths_halcyon.md)
484. **link directionality** (1 draft): Should Sign's added link be one-way, so the shortcut can't be used to retreat?
   - sources: [events/09_paths_meridian](../events/09_paths_meridian.md)
485. **link skip rack layers** (1 draft): Should ADD_LINK be allowed to skip over a Rack layer (4 or 7), or must it be capped to avoid bypassing the Rack?
   - sources: [events/13_paths_tethys](../events/13_paths_tethys.md)
486. **linked bus gate trigger** (1 draft): Does a player Linked Bus echo on the enemy wheel count as a player action for gate triggers?
   - sources: [rim_gates/gates](../rim_gates/gates.md)
487. **lock bypass inclusion** (1 draft): Should the lock-bypass rider ship at all, since cards already work under nudge locks?
   - sources: [card_upgrades/jam](../card_upgrades/jam.md)
488. **map tile unified city** (1 draft): Does unified-city ruling (flooded district of one model) hold, so TIDE chip is legible on map? If separate map, HQ and raid use of same clock needs new ruling.
   - sources: [bosses/tethys](../bosses/tethys.md)
489. **market hq access** (1 draft): Should the Market appear in HQ runs (G12), or only street netruns?
   - sources: [nodes/black_market](../nodes/black_market.md)
490. **miniboss placement** (1 draft): Does the mini-boss at L12 stay a separate gate, or does the boss draft want it folded into the vault as a phase?
   - sources: [hq/halcyon](../hq/halcyon.md)
491. **mirror two tick behavior** (1 draft): On a 2-tick slice, should Mirror always fire a single neighbour, or is it excluded (min_size 3)?
   - sources: [firmware/mirror](../firmware/mirror.md)
492. **multi needle rider targeting** (1 draft): On multi-needle enemies, should the rider hit every needle's slice or only the primary needle's?
   - sources: [card_upgrades/arc_flash](../card_upgrades/arc_flash.md)
493. **multiple pointers payout** (1 draft): Should extra pointers on a Twin Pointer wheel pay once (best tier) or per pointer?
   - sources: [card_upgrades/steady_hand](../card_upgrades/steady_hand.md)
494. **multiplier stacking** (1 draft): Should module multipliers multiply or add when several are lit?
   - sources: [inner_ring/b](../inner_ring/b.md)
495. **negate count ordering** (1 draft): Should negate_count be ordered (the first N attacks) or "the N largest"? The latter needs a preview ordering rule.
   - sources: [slice_upgrades/detour](../slice_upgrades/detour.md)
496. **negate frequency** (1 draft): Should NULL's Level IV negate be once per combat (proposed) or once per turn, given the tiny landing chance?
   - sources: [slice_upgrades/null](../slice_upgrades/null.md)
497. **node skip visibility** (1 draft): Should the skipped node be marked cleared or removed from the graph?
   - sources: [events/16_ambush_halcyon](../events/16_ambush_halcyon.md)
498. **node unlock gating** (1 draft): Is the Sink a profile-unlocked node or core from campaign start?
   - sources: [nodes/heat_sink](../nodes/heat_sink.md)
499. **nudge action interaction** (1 draft): Does the +1 nudge interact with Calibrate / Deep Calibrate (free nudges), or are card nudges distinct from nudge actions?
   - sources: [card_upgrades/ghost_step](../card_upgrades/ghost_step.md)
500. **nudge cost symmetry** (1 draft): Does the player's free nudge apply to the enemy wheel at the same cost, so the BLOCK dodge costs 0 RAM on turn 1?
   - sources: [enemies/transit_controller](../enemies/transit_controller.md)
501. **nudge lock interaction** (1 draft): Does the 4th free nudge still read correctly under N7 nudge-lock effects (the lock takes precedence, and the card is not refunded)?
   - sources: [card_upgrades/deep_calibrate](../card_upgrades/deep_calibrate.md)
502. **nudge scope after flip** (1 draft): Should the bundled nudge be able to move the wheel the card just flipped when that wheel is the enemy's, or stay own-wheel only as drafted?
   - sources: [card_upgrades/mirror_flip](../card_upgrades/mirror_flip.md)
503. **nudge scope choice** (1 draft): Should the free ±1 be limited to the inner ring, or let the player pick either ring?
   - sources: [card_upgrades/ratchet](../card_upgrades/ratchet.md)
504. **operative count requirement** (1 draft): Operative count: is the HQ run gated on three alive operatives, or do fewer lanes run with a smaller crew?
   - sources: [hq/rebel_cell](../hq/rebel_cell.md)
505. **operative death stakes** (1 draft): Should a loss on the ambush ever risk operative death, or stay capped at HP damage as drafted?
   - sources: [events/18_ambush_rebel_cell](../events/18_ambush_rebel_cell.md)
506. **operative slice count cap** (1 draft): Can an operative wheel have other than six slices, or is the six-slice cap kept for operatives while only enemies vary?
   - sources: [gdd/s05](../gdd/s05.md)
507. **opposite slice targeting** (1 draft): Is OPPOSITE worth a new enum value, or is two CHOSEN picks the better + version?
   - sources: [card_upgrades/encrypt](../card_upgrades/encrypt.md)
508. **orbit gate crossing** (1 draft): Should a gate crossed by the Director's own orbit in P3 count, or only player crossings?
   - sources: [enemies/mission_director](../enemies/mission_director.md)
509. **orbit gate traversal** (1 draft): Should the enemy's own orbit (P3 Orbital) ever fire gates, or stay excluded for readability?
   - sources: [rim_gates/gates](../rim_gates/gates.md)
510. **orbit timing** (1 draft): Does orbit move the needle before or after the preview and resolve?
   - sources: [enemies/geostationary_guard](../enemies/geostationary_guard.md)
511. **orbit timing lookahead** (1 draft): In P3 and P5 does the orbit apply after the start-of-turn respin, so the trail is only a one-turn lookahead?
   - sources: [enemies/civic_core](../enemies/civic_core.md)
512. **output down stacking** (1 draft): Does OUTPUT_DOWN ×3 (−75 %) stack additively or multiplicatively?
   - sources: [enemies/city_manager](../enemies/city_manager.md)
513. **override counter flee** (1 draft): Should the override counter tick down on a fight fled or abandoned, or only on a completed one?
   - sources: [events/05_future_rebel_cell](../events/05_future_rebel_cell.md)
514. **override expiration mechanic** (1 draft): Should the Frozen and HP override in choice 3 expire after 3 fights or persist until used?
   - sources: [events/02_future_meridian](../events/02_future_meridian.md)
515. **override persistence scope** (1 draft): Should an override persist through a death-adjacent abandon, or end with the netrun?
   - sources: [events/01_future_solace](../events/01_future_solace.md)
516. **override scope bosses** (1 draft): Do next_combat_overrides apply to mini-boss and boss fights, or skip them?
   - sources: [events/05_future_rebel_cell](../events/05_future_rebel_cell.md)
517. **own effect blocking** (1 draft): Should Hardened also block statuses the player applies to own slices (such as Overclock from a card), or only enemy-sourced ones?
   - sources: [firmware/hardened](../firmware/hardened.md)
518. **p3 status inheritance** (1 draft): Is the PLAYER cleanse on entering P3 correct, or should P3 inherit accumulated statuses from P2?
   - sources: [enemies/the_handler](../enemies/the_handler.md)
519. **package damage tax frequency** (1 draft): Does a Package's −50% damage apply to every resolve, or once per Package per turn?
   - sources: [enemies/logistics_director](../enemies/logistics_director.md)
520. **package persistence** (1 draft): Do Packages persist into P3, or does P2 → P3 cleanse the player's ring?
   - sources: [enemies/logistics_director](../enemies/logistics_director.md)
521. **parasite trigger scope** (1 draft): Do parasite segments trigger on any of your pointers, or only the first?
   - sources: [gdd/s02](../gdd/s02.md)
522. **penalty card upgrade strategy** (1 draft): Do we want a Bug+ at all, or is "Bug has no upgrade" the right ruling for the whole penalty-card family?
   - sources: [card_upgrades/bug](../card_upgrades/bug.md)
523. **perfect hook double resolve burnout** (1 draft): Should the burnout exemption cover a Perfect-hook double resolve, so the first resolve overclocks and the second does not re-corrupt?
   - sources: [card_upgrades/overdrive](../card_upgrades/overdrive.md)
524. **perfect multiplier data location** (1 draft): Should `perfect_multiplier` live on FirmwareData, or only on SliceData per N20, with a Firmware-level override?
   - sources: [firmware/overvolt](../firmware/overvolt.md)
525. **perfect snap even slices** (1 draft): Should snap on an even-size slice count as "Perfect" for Rigger's Perfect hook once Calibrated exists, or only true centre ticks?
   - sources: [card_upgrades/hot_swap](../card_upgrades/hot_swap.md)
526. **perwave trigger acceptable** (1 draft): Is a per-wave trigger acceptable in raid resolution, or should the bonus resolve only at raid start and end?
   - sources: [station/rigger](../station/rigger.md)
527. **phantom negation frequency** (1 draft): Should the Phantom's negation apply per raid or per wave, given that R4 ultimatum waves add a second wave?
   - sources: [station/ghost](../station/ghost.md)
528. **phase design overlap** (1 draft): Do Hold locks count against "Every phase asks a new question" if a Weight buff makes them overlap with resistance?
   - sources: [enemies/the_manifest](../enemies/the_manifest.md)
529. **phase two slice count** (1 draft): P2's 7 slots need N12 and the 6-slice cap lifted. Should P2 stay at 6 slots to keep a fallback?
   - sources: [enemies/claims_adjuster](../enemies/claims_adjuster.md)
530. **pierce interaction scope** (1 draft): Pierce on asset damage: does it also bypass a threat's own ICE-Lock hold, or only armor and shield?
   - sources: [station/breaker](../station/breaker.md)
531. **pierce shield interaction** (1 draft): Does pierce on a card bypass an enemy percent shield (R5), or should the enemy shield cap (open question 9) apply to it?
   - sources: [card_upgrades/static_shock](../card_upgrades/static_shock.md)
532. **pointer rule application** (1 draft): Does the player's hit really land on both enemy needles, or does the ×1 conservative factor need confirmation?
   - sources: [enemies/tracking_station](../enemies/tracking_station.md)
533. **pressure mechanic overlap** (1 draft): Does the Pressure ramp (+10 % per turn at shut doors) duplicate the R4 enrage too closely, or should the antenna elites author their own trigger instead?
   - sources: [hq/orbital](../hq/orbital.md)
534. **preview interval accuracy** (1 draft): Is a preview interval acceptable when encrypted, given it is sound and collapses to exact on decrypt?
   - sources: [raids/main](../raids/main.md)
535. **processing scope** (1 draft): Should Processing count only stamped slices, or also CORRUPTED ones (so Solace and Halcyon interact)?
   - sources: [enemies/permit_office](../enemies/permit_office.md)
536. **purge interruptibility** (1 draft): Should PURGE (Heat 100) be flushable below 100 to avert it, or uninterruptible?
   - sources: [nodes/heat_sink](../nodes/heat_sink.md)
537. **quorum pointer interaction** (1 draft): Does Quorum (50% damage on first needle) conflict with the pointer rule (GDD 2.7), where a hit lands on each pointer?
   - sources: [enemies/dispatch_core](../enemies/dispatch_core.md)
538. **rack gating bypass** (1 draft): Should `add_link` skipping a layer be allowed to bypass the layer-7 Rack gating, or only up to layer 6?
   - sources: [events/08_paths_solace](../events/08_paths_solace.md)
539. **ram overflow handling** (1 draft): Should RAM gains that overflow the 12 cap be refunded or wasted?
   - sources: [card_upgrades/cache](../card_upgrades/cache.md)
540. **rank 3 retune scope** (1 draft): Does the Rank 3 retune apply to the slot or to the Rider?
   - sources: [inner_ring/c](../inner_ring/c.md)
541. **recycler cold exit interaction** (1 draft): Should Recycler count as a Cold Exit NULL resolve (a conflict between the two chips), or should it be separated?
   - sources: [firmware/recycler](../firmware/recycler.md)
542. **reflect perfect interaction** (1 draft): Should reflect damage count as Perfect-based for Kernel Sync-type Daemons?
   - sources: [slice_upgrades/detour](../slice_upgrades/detour.md)
543. **relay destruction on replace** (1 draft): Do Relays count as destroyed when a later satellite replaces them (R12 Q7)?
   - sources: [enemies/commons_array](../enemies/commons_array.md)
544. **repeat trigger implementation** (1 draft): Does the "repeat before all fire" trigger in P5 need N20, or can the sim treat it as an authored Enrage variant?
   - sources: [enemies/commons_array](../enemies/commons_array.md)
545. **replace as destruction** (1 draft): Is replacing a drone through REPLACE a "destroyed" drone for Daemons?
   - sources: [slice_upgrades/trojan](../slice_upgrades/trojan.md)
546. **report trigger scope** (1 draft): Should Report fire on Perfect landed on enemy's wheel by card/nudge, or only on own wheel resolution?
   - sources: [enemies/loyalty_test](../enemies/loyalty_test.md)
547. **resistance application scope** (1 draft): Should the rider ignore resistance on the free nudges only, or on all nudges this turn, paid ones included?
   - sources: [card_upgrades/deep_calibrate](../card_upgrades/deep_calibrate.md)
548. **resistance cap** (1 draft): Should the Shim +1 resistance growth be capped (for example at 4) in data, or left to the 3-4 turn length to cap itself?
   - sources: [enemies/cargo_hauler](../enemies/cargo_hauler.md)
549. **resistance strip duration** (1 draft): Does resistance stripped mid-resolve apply to player's own later nudges and cards this turn, or only to the resolve?
   - sources: [firmware/tracer](../firmware/tracer.md)
550. **resistance strip passive interaction** (1 draft): Should resistance strip on an enemy with a passive trait (restores each turn) count as the same "absorbed" tick that nudges use, so Shatter+ reads as "clear one nudge of tax" in the preview?
   - sources: [card_upgrades/shatter](../card_upgrades/shatter.md)
551. **resistance strip scope** (1 draft): Does MODIFY_RESISTANCE with a negative amount remove Hub-sourced and trait-sourced resistance equally, or only the active source?
   - sources: [card_upgrades/short_circuit](../card_upgrades/short_circuit.md)
552. **retainer removal destroyed status** (1 draft): Are the Retainers' removal at the transition "destroyed" for Daemons and rewards?
   - sources: [enemies/account_manager](../enemies/account_manager.md)
553. **retrigger chip trigger** (1 draft): Does a Retrigger of the slice fire this chip's shield again, or only the slice's own BLOCK?
   - sources: [firmware/static_coat](../firmware/static_coat.md)
554. **rewire empty socket** (1 draft): Should REWIRE also move a Firmware to an empty socket, or swap two slices' Firmware only?
   - sources: [nodes/rest](../nodes/rest.md)
555. **rim gates player wheel scope** (1 draft): Are rim gates one set per wheel, or may the Director's gates also appear on the player's wheel in later tiers?
   - sources: [enemies/mission_director](../enemies/mission_director.md)
556. **ring attackability** (1 draft): Should the ring be attackable by enemies with a lock effect in later passes, or stay purely player-owned?
   - sources: [inner_ring/a](../inner_ring/a.md)
557. **ring frame binding** (1 draft): Is the ring bound to the wheel (proposed) or to the pointer's frame (Q10)?
   - sources: [catalog/parasite](../catalog/parasite.md)
558. **rng determinism preview** (1 draft): With the Citation's random slice pick, is the OUTPUT_DOWN placement deterministic under a named RNG stream, and does the preview show the target slice?
   - sources: [enemies/riot_control](../enemies/riot_control.md)
559. **rotating focus scope** (1 draft): Is phase-boundary rotation (Option C) enough of a "rotating focus" for the designer, or is per-turn swapping across three live wheels (Option B) a requirement?
   - sources: [sync_strike/strike](../sync_strike/strike.md)
560. **sandbox riders** (1 draft): Does SANDBOX negate status and verdict riders of the resolution, or only damage?
   - sources: [bosses/aurelian](../bosses/aurelian.md)
561. **sandbox scope definition** (1 draft): Should the base Duck's "next incoming attack" be used up by an enemy's sweep attack or by an attack on a drone? Does the evade take effect only on attacks that reach the player?
   - sources: [card_upgrades/duck](../card_upgrades/duck.md)
562. **sandbox trigger condition** (1 draft): Does the counter still fire if the SANDBOX absorbs nothing (the enemy has no attack this turn)?
   - sources: [firmware/counterstrike](../firmware/counterstrike.md)
563. **satellite move triggers** (1 draft): Does a swapped satellite count as moved for Daemon and Firmware triggers?
   - sources: [card_upgrades/undock](../card_upgrades/undock.md)
564. **satellite phase override semantics** (1 draft): Does the Civic Drone count as destroyed when the phase override clears it?
   - sources: [enemies/zoning_board](../enemies/zoning_board.md)
565. **satellite respin behavior** (1 draft): Do satellites get the start-of-turn respin?
   - sources: [gdd/s02](../gdd/s02.md)
566. **second roll exclusion** (1 draft): Should the second roll exclude the slice already corrupted, guaranteeing two distinct slices, or is repeat risk the intended sidegrade?
   - sources: [card_upgrades/malware_drop](../card_upgrades/malware_drop.md)
567. **self damage listeners** (1 draft): Does self-damage from Power Tap+ trigger any future "damage taken" listeners (N6), such as Echo reactions?
   - sources: [card_upgrades/power_tap](../card_upgrades/power_tap.md)
568. **self damage mechanics** (1 draft): Should enemy-side damage reduction count the self-damage of this card, since it comes from the player?
   - sources: [card_upgrades/overload](../card_upgrades/overload.md)
569. **shadow spin interaction** (1 draft): Does Shadow listener also fire on SPIN effects, or only nudge actions?
   - sources: [enemies/the_handler](../enemies/the_handler.md)
570. **shield refund condition** (1 draft): Should the RAM refund still pay when the shield is wasted at the 15 cap, or only when the slice actually adds shield?
   - sources: [firmware/power_cell](../firmware/power_cell.md)
571. **shield stacking behavior** (1 draft): Should Stash's SHIELD stack on top of an existing shield up to the cap of 15, or refresh?
   - sources: [enemies/dead_drop](../enemies/dead_drop.md)
572. **shield stacking mechanics** (1 draft): Should Shield be allowed to stack across turns here (cap 15), or is a 5-shield on a normal worth a PERCENT variant later?
   - sources: [enemies/ground_control](../enemies/ground_control.md)
573. **single operative strike** (1 draft): With one operative, does the strike run at all, or is DISPATCH a plain boss fight on that route?
   - sources: [sync_strike/strike](../sync_strike/strike.md)
574. **size bonus calculation** (1 draft): Does the size bonus read the slot's size_ticks, or the live slice size after any shrink effects?
   - sources: [firmware/patch_plus](../firmware/patch_plus.md)
575. **skip link rack interaction** (1 draft): Does the skip link in choice 2 bypass a Server Rack at layer 4, or must it never skip a layer holding a Rack?
   - sources: [events/10_paths_halcyon](../events/10_paths_halcyon.md)
576. **slice size change direction** (1 draft): Does a slice's size change (Narrow Band / Wide Band) take ticks from the clockwise neighbour, the counterclockwise one, or the player's choice at the socket?
   - sources: [gdd/s06](../gdd/s06.md)
577. **slice size limits** (1 draft): Sizes 1 and 8 are outside R11's table. Allow them, or cap slices at 2-7?
   - sources: [firmware/new_chips](../firmware/new_chips.md)
578. **snap behavior on even slices** (1 draft): Should Snap on a size-4 slice (no Perfect) pick a GOOD tick, or stay refused and show a "no Perfect available" preview?
   - sources: [card_upgrades/snap](../card_upgrades/snap.md)
579. **snap target even slices** (1 draft): Should the snap rule on even-sized slices pick the nearest best tick, or the slice's geometric centre?
   - sources: [card_upgrades/lock_on](../card_upgrades/lock_on.md)
580. **spin effect definition** (1 draft): Does a Respin or a Flip count as "already spun" for the condition, or only SPIN effects?
   - sources: [card_upgrades/tailspin](../card_upgrades/tailspin.md)
581. **spin flag scope** (1 draft): Does the existing Momentum "already spun" flag count spins from other cards and from the free nudge, or only SPIN effects?
   - sources: [card_upgrades/counter_spin](../card_upgrades/counter_spin.md)
582. **spin source qualification** (1 draft): Does a Spin granted by Firmware/Daemon (e.g. `+1 spin on all cards`) count as "already spun" for the combo?
   - sources: [card_upgrades/momentum](../card_upgrades/momentum.md)
583. **stacking multiplier behavior** (1 draft): Does the window stack if the + card is played twice, or does it refresh to a flat ×2?
   - sources: [card_upgrades/overclock_nudges](../card_upgrades/overclock_nudges.md)
584. **stacking resistance rules** (1 draft): Should the live-tracker slice's next_combat_overrides stack with Heat-driven enemy resistance, or take the higher value?
   - sources: [events/29_hqview_any](../events/29_hqview_any.md)
585. **stake partial reward** (1 draft): Should a lost stake (below 40% HP at a win) still pay the Cycles, or does it pay nothing?
   - sources: [events/14_ambush_solace](../events/14_ambush_solace.md)
586. **status on weak** (1 draft): Whether statuses apply on a WEAK landing (proposed: yes).
   - sources: [gdd/s13](../gdd/s13.md)
587. **status slot limit** (1 draft): Should the 3-distinct-status slot limit stay, or is a single status-slot limit simpler to read?
   - sources: [catalog/status](../catalog/status.md)
588. **swap firmware reset** (1 draft): Does a swap in a flash reset the Firmware socket, or only warn?
   - sources: [slice_upgrades/detour](../slice_upgrades/detour.md)
589. **sync strike focus rotation** (1 draft): Should the Sync Strike's rotating focus cycle through all three wheels equally, or favor certain positions?
   - sources: [gdd/s08](../gdd/s08.md)
590. **tag trigger scope** (1 draft): Should the Recall Tag also trigger on the player's Perfect nudge-cards, not only slice landings?
   - sources: [enemies/recall_unit](../enemies/recall_unit.md)
591. **tend block system cost** (1 draft): Is a Tend BLOCK on drone death worth N6, or do we drop it for simplicity?
   - sources: [enemies/care_swarm](../enemies/care_swarm.md)
592. **threat targeting scope** (1 draft): Should the damage reduction apply to threats passing through the node, or only to threats whose destination is the node?
   - sources: [station/ghost](../station/ghost.md)
593. **tick quality firmware order** (1 draft): Does a Calibrated tick raise apply to the ENCRYPTED / TIER_DOWN interplay before or after the status, i.e. is the order fixed?
   - sources: [gdd/s05](../gdd/s05.md)
594. **tide lock map scope** (1 draft): Should Tide Lock skip LOW in the HQ's BALLAST TIDE too, so one Exploit is felt on map and fight, or stay fight-only?
   - sources: [bosses/tethys](../bosses/tethys.md)
595. **tier condition timing** (1 draft): Does the tier condition read the landing at play time, or at resolve?
   - sources: [card_upgrades/bulwark](../card_upgrades/bulwark.md)
596. **tier down weak landing interaction** (1 draft): Does TIER_DOWN on a WEAK landing floor out at WEAK, or can it drop below?
   - sources: [enemies/port_authority](../enemies/port_authority.md)
597. **toll visibility** (1 draft): Are tolls shown on the route before commit at every rung, or only inside the read horizon?
   - sources: [hq/solace](../hq/solace.md)
598. **trigger cap generalization** (1 draft): Should a per-resolve cap be a general field on TriggeredEffectData, since other chips (Siphon, Skimmer) have the same stacking risk?
   - sources: [firmware/leech](../firmware/leech.md)
599. **upgrade implementation approach** (1 draft): Should the + rider be a CUSTOM handler, or a new `slice_pick` value (cheaper to preview and test)?
   - sources: [card_upgrades/corrupt_packet](../card_upgrades/corrupt_packet.md)
600. **upgrade ram floor rule** (1 draft): Should upgrades share a rule that "+ never lowers RAM below the base card's RAM cost when it also adds a rider"?
   - sources: [card_upgrades/leech_worm](../card_upgrades/leech_worm.md)
601. **waiting mechanics** (1 draft): May the player wait in place (a step passes with no fight) to catch a gate, or only walk?
   - sources: [hq/aurelian](../hq/aurelian.md)
602. **wave two setup gate** (1 draft): Do waves resolve sequentially with shared defenses today, and should wave 2 open a re-setup window?
   - sources: [raids/main](../raids/main.md)
603. **weaken vs corrupt** (1 draft): Should Weaken replace Corrupt as a status on the enemy slice, or should CORRUPTED stay as a RAM debuff?
   - sources: [inner_ring/a](../inner_ring/a.md)
604. **wheel wrap behavior** (1 draft): Should the nudge be allowed to wrap past slice 6 into slice 1, or should the wheel be non-looping?
   - sources: [events/20_wheel_solace](../events/20_wheel_solace.md)
605. **wrecker strike scope** (1 draft): Should the strike deal damage to threats only, or can it also remove a TAKEN-state pressure on the node?
   - sources: [station/wrecker](../station/wrecker.md)
606. **wrecker strike trigger** (1 draft): Should the strike also hit when a threat is already ICE-Locked on the node, or only on first entry?
   - sources: [station/wrecker](../station/wrecker.md)

## ui-and-art

607. **orbit preview length** (3 drafts): Should the orbit trail show only next turn's landing or two turns ahead (more teaching at L1-2)?
   - also: Should the sticky orbit be shown as a trail of the next 2 turns, or only the next turn, for L1-2 teaching?
   - also: Should the orbit trail show the full next 2 turns or only the next 1?
   - sources: [enemies/cell_informant](../enemies/cell_informant.md), [enemies/conveyor_warden](../enemies/conveyor_warden.md), [enemies/ground_control](../enemies/ground_control.md)
608. **needle readability** (2 drafts): Is the P2 needle seat 0 / 11 too close to read on the HUD?
   - also: Is 11 apart (0 / 11) too hard to read on the HUD? Should the gap be at least 12?
   - sources: [enemies/riot_control](../enemies/riot_control.md), [enemies/tracking_station](../enemies/tracking_station.md)
609. **nudge cost currency** (2 drafts): Should extra-nudge costs mix (HP or Heat per nudge) or be one fixed currency per event?
   - also: Should the extra-nudge cost be fixed to one currency per wheel to keep the UI simple, or is the player's choice worth the extra button?
   - sources: [events/21_wheel_meridian](../events/21_wheel_meridian.md), [events/26_wheel_any](../events/26_wheel_any.md)
610. **closed node preview handling** (1 draft): Does a closed node refund or remove an already-visible reward preview (e.g. a revealed Elite), or is it silently gone?
   - sources: [events/08_paths_solace](../events/08_paths_solace.md)
611. **crane naming** (1 draft): Does the art confirm the Reach as gantry N-S plus trolley E-W for hook sectors?
   - sources: [hq/meridian](../hq/meridian.md)
612. **defrag tick quality pattern** (1 draft): Would an authored `tick_quality` on the 7-tick Defrag (W W W P W W W) make the block's Perfect more readable?
   - sources: [enemies/transit_controller](../enemies/transit_controller.md)
613. **direction choice input** (1 draft): Is a chosen-direction input acceptable on cards, or should direction stay fixed on all cards, with upgrades adding RAM-efficiency instead?
   - sources: [card_upgrades/gear_shift](../card_upgrades/gear_shift.md)
614. **elite conversion preview** (1 draft): Should the converted Elite be shown as a changed node before the player commits, or should the cost of the gamble include the surprise?
   - sources: [events/13_paths_tethys](../events/13_paths_tethys.md)
615. **encrypt interaction feedback** (1 draft): Should a Citation applied to an ENCRYPTED slice consume the Encrypt for a visible message, or silently?
   - sources: [enemies/zoning_board](../enemies/zoning_board.md)
616. **enemy plate visibility** (1 draft): Should enemy plates be shown at all, or hidden unless an Exploit reveals them?
   - sources: [inner_ring/b](../inner_ring/b.md)
617. **even slice restriction** (1 draft): Should the chip be barred from even-sized slices at loadout, or just carry a warning? A dead socket is a trap for new players.
   - sources: [firmware/skimmer](../firmware/skimmer.md)
618. **grid zoom during combat** (1 draft): Can the Grid zoom open during an active fight, or only at map nodes?
   - sources: [gdd/s03](../gdd/s03.md)
619. **heat display zoom levels** (1 draft): Whether Heat chip and raid tick show on every Grid zoom level.
   - sources: [gdd/s04](../gdd/s04.md)
620. **hivemind persistence clarity** (1 draft): Does hivemind's dormant-revive mechanic read clearly in grid preview, or use more drones with no regrow?
   - sources: [station/botnet](../station/botnet.md)
621. **hub heal ui** (1 draft): Should the conditional Hub heal show a "ARMED / SPENT" chip, or is a plain tooltip enough?
   - sources: [enemies/triage_unit](../enemies/triage_unit.md)
622. **hud trail needles** (1 draft): Should the orbit step (+1 per turn) be preserved as a trail on the HUD, or does N11 need the trail redrawn when two needles sit 12 ticks apart?
   - sources: [enemies/transit_controller](../enemies/transit_controller.md)
623. **late fee visibility** (1 draft): Should Late Fee be hidden until first triggered, or shown on the intent chip from turn 1?
   - sources: [enemies/billing_daemon](../enemies/billing_daemon.md)
624. **listener preview display** (1 draft): Does the Proof of Delivery listener need preview showing "BLOCK +4 if you land a Perfect" before action commit?
   - sources: [enemies/last_mile_enforcer](../enemies/last_mile_enforcer.md)
625. **map preview clarity** (1 draft): When Open cuts a node, should the preview name the node (clear) or only say "a node in layer N" (more tension)?
   - sources: [events/09_paths_meridian](../events/09_paths_meridian.md)
626. **market recognisability** (1 draft): Should the Market be recognisable after the first visit (a profile unlock "Fixer contact" that reveals it on the map), or stay unknown forever?
   - sources: [nodes/black_market](../nodes/black_market.md)
627. **needle gap hud marker** (1 draft): Does the 9-tick needle gap need a HUD marker for the pair?
   - sources: [enemies/rc_template_elite_b](../enemies/rc_template_elite_b.md)
628. **no perfect readability** (1 draft): P1 big Overflow has no Perfect (6-tick). Is a no-Perfect damage slice readable enough, or should the player-facing map flag it more clearly on the intent chip?
   - sources: [enemies/rc_template_elite](../enemies/rc_template_elite.md)
629. **orbit visibility** (1 draft): Should the orbit be a reference-player-visible trail (the future slices lit for 2 turns) so the "plan ahead" question is a read and not a calculation?
   - sources: [enemies/weather_satellite](../enemies/weather_satellite.md)
630. **overclocked countdown display** (1 draft): Should an OVERCLOCKED slice show its burn-out countdown in preview, making the trade readable?
   - sources: [enemies/uplink_relay](../enemies/uplink_relay.md)
631. **override visibility on map** (1 draft): Should override chips show on the map so the player can plan which node benefits, or stay hidden until combat starts?
   - sources: [events/02_future_meridian](../events/02_future_meridian.md)
632. **override visibility ui** (1 draft): Should a pending override show on the map as a chip before the next combat starts, and should the +25 % punishment in choice 1 be hidden until it fires?
   - sources: [events/06_future_aurelian](../events/06_future_aurelian.md)
633. **parasite animation sync** (1 draft): Do the Parasite ring segments share the wheel's rotation animation exactly, or lag it for readability?
   - sources: [gdd/s09](../gdd/s09.md)
634. **perfect hit feedback** (1 draft): Do the 4-tick Hotfix slices make the first-time player feel cheated that Perfect never works on them?
   - sources: [enemies/triage_unit](../enemies/triage_unit.md)
635. **perfect tick legibility** (1 draft): Is a 4-tick Overflow with no Perfect legible enough, or should it show a "no Perfect" marker on the intent plate?
   - sources: [enemies/conveyor_warden](../enemies/conveyor_warden.md)
636. **phase transition telegraph** (1 draft): Does the threshold line "Claim reviewed. Denied." need a one-turn warning telegraph, as the Migrate pointer has in GDD 2.11?
   - sources: [enemies/claims_adjuster](../enemies/claims_adjuster.md)
637. **preview chip display** (1 draft): Should the + version show expected payout in preview chip ("+2 RAM next turn")?
   - sources: [card_upgrades/steady_hand](../card_upgrades/steady_hand.md)
638. **preview legibility** (1 draft): Should the snap preview show "0 ticks, draw" on hover so the rider is legible before playing?
   - sources: [card_upgrades/inner_snap](../card_upgrades/inner_snap.md)
639. **resistance preview feedback** (1 draft): Should resistance show a preview line "your nudge moves 0" so the wheel's heaviness is legible to a first-time player?
   - sources: [enemies/orbital_debris](../enemies/orbital_debris.md)
640. **rider complexity tradeoff** (1 draft): Is a conditional free nudge too fiddly for the tooltip, or should the upgrade be the plain RAM 1 cost cut?
   - sources: [card_upgrades/reroll](../card_upgrades/reroll.md)
641. **riposte perfect clarity** (1 draft): Is "Perfect-quality Riposte gains +6" too hard to read? A plain damage bump may be clearer.
   - sources: [enemies/rc_template_elite_b](../enemies/rc_template_elite_b.md)
642. **rumor false feedback timing** (1 draft): Should a false rumor in choice 2 be revealed to the player once the first combat starts, or stay hidden until the damage lands?
   - sources: [events/07_future_tethys](../events/07_future_tethys.md)
643. **rumor outcome disclosure** (1 draft): Should the unscouted outcome of choice 3 be disclosed as odds in the label, or kept hidden so the rumor stays a rumor?
   - sources: [events/27_raidwin_any](../events/27_raidwin_any.md)
644. **sandbox readability** (1 draft): Does Sandbox on a 3-tick slice read clearly enough, or should Sandbox sit on a 5-tick slice and lose the narrow window?
   - sources: [enemies/cargo_hauler](../enemies/cargo_hauler.md)
645. **second target selection** (1 draft): Should the second target be CHOSEN (more control, an extra UI step) or the slice opposite the pointer (deterministic and no UI, but less choice)?
   - sources: [card_upgrades/leech_worm](../card_upgrades/leech_worm.md)
646. **shield flat vs percent** (1 draft): Is a PERCENT shield on a normal too fiddly to read; would flat 4 × tier factor be clearer?
   - sources: [enemies/launch_pad](../enemies/launch_pad.md)
647. **shop wheel pricing position** (1 draft): Which of the three shop-wheel slices gets the 80 price?
   - sources: [gdd/s11](../gdd/s11.md)
648. **status preview display** (1 draft): Should the second status stack be preview-visible as a combined "×0.375" chip on the enemy slice?
   - sources: [card_upgrades/parasite_pulse](../card_upgrades/parasite_pulse.md)
649. **swap rebalance method** (1 draft): Should a swap that breaks the 30-tick sum auto-resize the neighbours, or force a manual fix-up?
   - sources: [slice_upgrades/null](../slice_upgrades/null.md)
650. **tick strip visibility** (1 draft): Should the tick-strip under the pointer be always on, or only on hover and in the loadout?
   - sources: [gdd/s09](../gdd/s09.md)
651. **tier scaling approach** (1 draft): Should the pyramid scale its tiers to the generated graph, or should the generator cap layers per tier to fit fixed art dimensions?
   - sources: [hq/halcyon](../hq/halcyon.md)
652. **ui feedback on imperfect slices** (1 draft): Should Seizure (no Perfect) be marked in the intent UI as "cannot be Perfected" so players learn the sub-tick map?
   - sources: [enemies/customs_scanner](../enemies/customs_scanner.md)
653. **wheel tick reassignment** (1 draft): Should a size shrink require free wheel ticks to be reassigned manually, or are freed ticks distributed automatically to neighbours?
   - sources: [slice_upgrades/overflow](../slice_upgrades/overflow.md)
654. **zoom mid fight** (1 draft): Is the zoom to the Grid view allowed mid-fight, or only on the netrun map between nodes?
   - sources: [gdd/s09](../gdd/s09.md)
655. **zoom structure placement** (1 draft): Should 1.3 show the zoom as part of the structure, or leave it to Section 9 as UX?
   - sources: [gdd/s01](../gdd/s01.md)

