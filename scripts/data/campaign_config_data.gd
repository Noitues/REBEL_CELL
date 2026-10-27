class_name CampaignConfigData
extends Resource

## Config fields N9 retired; the content validator rejects them (retired_field_errors).
const RETIRED_FIELDS: Array[String] = ["corrupted_self_damage", "corrupted_damage_per_major", "corrupted_ram_drain"]
## Global tuning in one place (Section 11). One .tres for the whole game.

@export_group("Heat")
@export var heat_max: int = 100
@export var heat_thresholds: Array[HeatThresholdData] = []
@export var death_heat_base: int = 10
@export var clean_defense_heat: int = 5
## RAID-FIX A: a raid whose Home loses more than this percent of its integrity is AMBER (severity tier 1).
## Heat per Exploit extracted (11.5).
@export var exploit_heat: int = 10
## Heat per Server Rack capture, indexed by tier - 1.
@export var rack_heat_by_tier: PackedInt32Array = PackedInt32Array([2, 3, 5, 8])

@export_group("Economy")
@export var cycles_per_schematic: int = 10
## Schematics per Server Rack, indexed by tier - 1.
@export var rack_schematics_by_tier: PackedInt32Array = PackedInt32Array([10, 17, 29, 50])
@export var raid_schematics_by_tier: PackedInt32Array = PackedInt32Array([8, 12, 18, 25])
@export var node_repair_ratio: float = 0.5
## N2 (CONTENT_DESIGN_V2 R2, decision 2026-10-18): tier sets base values only. Enemy slice
## output (damage, block, heal, shield, hits) per tier, indexed by tier - 1. One table
## replaces GDD 11.6's 1.2^(t-1), the old config 1.3 and the old schema default 1.6. Applies
## to bosses and mini-bosses like everything else. Read it through enemy_damage_factor(tier).
@export var enemy_damage_by_tier: PackedFloat64Array = PackedFloat64Array([1.0, 1.3, 1.69, 2.2])
## N2 legacy HP fallback: an enemy with no hp_by_tier / hp_bands keeps base HP x this entry
## (the old 1.6^(t-1) made explicit), so no fight changes before the re-author pass. Read
## it through enemy_hp_scale(tier).
@export var enemy_hp_scale_by_tier: PackedFloat64Array = PackedFloat64Array([1.0, 1.6, 2.56, 4.096])
## R2 phase budget: the reference player's damage per turn, indexed by tier - 1.
@export var reference_dpt_by_tier: PackedInt32Array = PackedInt32Array([9, 11, 14, 18])
## R1 / R2: the turns one phase should last.
@export var target_turns_per_phase: float = 3.5
## R2 HP bands per class: [min, max] pairs for T1..T4 (8 entries; 0, 0 = no band at that
## tier). EnemyData.validate() checks hp_by_tier against them; HpBandLint lints content.
@export var hp_band_normal: PackedInt32Array = PackedInt32Array([28, 36, 34, 44, 44, 56, 56, 70])
@export var hp_band_elite: PackedInt32Array = PackedInt32Array([56, 72, 68, 88, 88, 112, 112, 144])
@export var hp_band_mini_boss_2: PackedInt32Array = PackedInt32Array([56, 72, 68, 88, 88, 112, 0, 0])
@export var hp_band_mini_boss_3: PackedInt32Array = PackedInt32Array([85, 105, 104, 128, 132, 162, 0, 0])
## A boss's last hp_bands ceiling must be at least this: the open-ended "above" zone.
@export var boss_hp_band_open_ceiling: float = 99.0
@export var reward_scale_per_tier: float = 1.7
## Cycles earned (11.1) as inclusive [min, max] ranges.
@export var cycles_combat_range: Vector2i = Vector2i(10, 20)
@export var cycles_elite_range: Vector2i = Vector2i(30, 40)
@export var cycles_router_range: Vector2i = Vector2i(15, 25)

@export_group("Shop")
## Mainframe shop prices in Cycles (11.2), inclusive [min, max] ranges.
@export var card_price_range: Vector2i = Vector2i(50, 75)
@export var firmware_price_range: Vector2i = Vector2i(75, 150)
@export var daemon_price_range: Vector2i = Vector2i(150, 250)
@export var card_removal_price: int = 50
## Added to card_removal_price after each removal.
@export var card_removal_increment: int = 25
@export var slice_overwrite_price: int = 100
@export var null_slice_overwrite_price: int = 150
## Slice catalogue a Mainframe draws its overwrite offers from (designer ruling 2026-09-24).
@export var shop_slices: Array[SliceData] = []
@export var shop_slice_choices: int = 3

@export_group("Schematic costs")
## Campaign purchases in Core Schematics (11.4).
@export var rookie_cost: int = 15
@export var node_base_cost: int = 20
## Successive node upgrade costs.
@export var node_upgrade_costs: PackedInt32Array = PackedInt32Array([30, 60])
## Each upgrade level adds this much of the node's base integrity and this many asset slots.
@export var node_upgrade_integrity_pct: float = 50.0
@export var node_upgrade_asset_slots: int = 1
@export var netrun_boost_cost_range: Vector2i = Vector2i(10, 20)
## The one-time boosts HQ sells (GDD 11.4).
@export var netrun_boosts: Array[NetrunBoostData] = []
## Buying Heat reduction: removes heat_purchase_amount for heat_purchase_cost,
## which rises by heat_purchase_increment after each purchase.
@export var heat_purchase_amount: int = 5
@export var heat_purchase_cost: int = 25
@export var heat_purchase_increment: int = 10
## Patching the home server at HQ: Schematics per integrity point restored (decision
## 2026-09-24, found by the balance simulation: home damage was otherwise permanent).
@export var home_repair_cost_per_point: float = 1.0
@export var class_unlock_cost: int = 80

@export_group("Combat")
@export var hand_size: int = 5
@export var draw_per_turn: int = 5
## RAM per turn, starting RAM and the RAM cap (6 / +4 / 12, GDD 2.2 and 5.2) live on
## ClassData (starting_ram, ram_regen, max_ram) because classes vary them.
## RAM cost of a Respin (11.3). Cards cost 0-3 RAM each (content); first nudge is free.
@export var respin_ram_cost: int = 4
@export var weak_multiplier: float = 0.5
@export var overclock_multiplier: float = 1.5
## N8 (R8): each OUTPUT_DOWN stack takes this share off the slice's output; the stacks add
## (one signed sum, ruling Q35 b) and the factor never goes below 0: 1 - share x stacks.
@export var output_down_per_stack: float = 0.25
## N8 (R8): a PARASITE (the retired Botnet status) is this many OUTPUT_DOWN stacks; with
## 0.25 a stack, 2 keeps the old half output. Applies and the v2 -> v3 save migration read it.
@export var parasite_output_down_stacks: int = 2
## N8: the most stacks one status may hold on one slot (placeholder, designer 2026-10-18).
## RC.UNCAPPED_STATUSES (ENCRYPTED, CORRUPTED) ignore it.
@export var status_stack_cap: int = 5
@export var shield_cap: int = 15
## N14 (ruling Q39): SANDBOX charges a DETOUR slice gives when it resolves at WEAK or GOOD,
## and at PERFECT. Each charge negates one incoming hit whole; charges add up.
@export var sandbox_charges: int = 1
@export var sandbox_charges_perfect: int = 2
## Plan 2 N6 (designer 2026-10-18, answer 1; ruling Q8 a): how often an enemy listener with no
## authored `max_per_turn` may fire each turn. At least 1.
@export var listener_max_per_turn_default: int = 1
## N9 (ruling Q36): while a needle of the operative's wheel touches a CORRUPTED slice, every RAM
## cost is multiplied by this (a cost of 0 stays 0; no cap). At least 1.
@export var corrupted_ram_cost_multiplier: int = 2
## N9 (ruling Q37): manipulating an enemy wheel whose needle touches a CORRUPTED slice costs
## this many times less (halved, rounded up). At least 1.
@export var corrupted_enemy_ram_divisor: int = 2
@export var extra_nudge_ram_cost: int = 1
## Phases per enemy class (plan 2 R1), counting the base phase, indexed by RC.EnemyClass
## (normal, elite, mini-boss, boss): EnemyData.validate holds `phases.size() + 1` inside
## [min, max]. The boss minimum is 3 until the boss design passes author 4-5 (R1 says 4; N3
## adds no content phases: DECISIONS 2026-10-18 N3).
@export var phase_count_min_by_class: PackedInt32Array = PackedInt32Array([1, 1, 2, 3])
@export var phase_count_max_by_class: PackedInt32Array = PackedInt32Array([1, 2, 3, 5])
## N11 (GDD 2.1, Q27): the most pointers a wheel or phase layout may author (validate:
## too_many_pointers). Pointers sit on any tick 0-29, at least 1 tick apart.
@export var max_pointers: int = 4
## N11: where an ICE BOSS_EXTRA_POINTER pointer goes, in ticks after pointer 0, tried in
## order; the first tick no pointer holds wins (the legacy evenly spaced 15 / 10 / ...).
@export var boss_extra_pointer_offsets: PackedInt32Array = PackedInt32Array([15, 10, 20, 5, 25])
## Plan 2 N12 (R11, ruling Q20; designer W1 N12): slice sizes run 0-30 and every wheel sums
## to 30, so the ticks are the only size cap. The slot-count caps stay (an empty 0-size slot
## does not count): an operative wheel holds at most operative_slice_cap slices, an enemy
## wheel enemy_slice_cap. A slice with ticks is at least slice_size_min ticks.
@export var operative_slice_cap: int = 6
@export var enemy_slice_cap: int = 30
@export var slice_size_min: int = 1
## Plan 2 N12 (R11): the default sub-tick quality map. A tick at distance d from its slice's
## middle reads PERFECT at d = 0, GOOD at d <= tick_quality_good_reach, else WEAK
## (WheelMath.default_quality; 1 gives 5 = W G P G W, 4 = W G G W).
@export var tick_quality_good_reach: int = 1
## N4 (plan 2 R4, ruling Q33): class enrage defaults, indexed by RC.EnemyClass (normal,
## elite, mini-boss, boss). A start turn of 0 means no enrage (normals). An EnemyData's
## authored `enrage` wins over these (enrage_for). Steps are additive; defaults add no
## resistance (resistance_step is for authored enrages).
@export var enrage_start_turn_by_class: PackedInt32Array = PackedInt32Array([0, 8, 10, 10])
@export var enrage_every_n_turns_by_class: PackedInt32Array = PackedInt32Array([0, 5, 5, 5])
@export var enrage_damage_pct_step_by_class: PackedInt32Array = PackedInt32Array([0, 25, 25, 25])
## N21 (rulings Q16, Q31): each enemy's per-turn spin resistance (wheel passive + hub at fight
## start, before ICE / Heat modifiers) lies inside its class range, indexed by RC.EnemyClass
## (normal 1-2, elite 3-4, mini-boss 3-4, boss 5-6). EnemyData.validate holds it; satellites
## (2- and 3-slice wheels) are not fights and stay outside the table.
@export var resistance_min_by_class: PackedInt32Array = PackedInt32Array([1, 3, 3, 5])
@export var resistance_max_by_class: PackedInt32Array = PackedInt32Array([2, 4, 4, 6])

@export_group("Netrun")
## Plan 2 N22 (ruling Q12): the first N normal fights of a run draw from the EASY normal pool
## (EnemyData.normal_pool), later ones from HARD. An old save without the counter counts as
## N once its current node lies past layer N, else 0 (NetrunSession.from_dict).
@export var easy_normal_fights: int = 2
## Plan 2 EV-01: the highest tier an event fight's tier_delta can raise the enemy tables to.
@export var event_fight_tier_cap: int = 4
## Plan 2 EV-02 hosts: a won raid offers one RAID_WIN event (designer call, Q6: every win). false = none.
@export var raid_win_event_enabled: bool = true
## Plan 2 EV-02 hosts: after every Nth completed netrun the HQ offers one HQ_VIEW event. 0 = never.
@export var hq_event_every_runs: int = 3
@export var map_layers: int = 7
@export var map_nodes_min: int = 2
@export var map_nodes_max: int = 4
## Layers (1-based) holding a Server Rack. The last one is the run's final node.
@export var rack_layers: PackedInt32Array = PackedInt32Array([4, 7])
## At least one Mainframe somewhere in these layers (inclusive band).
@export var map_mainframe_layers: Vector2i = Vector2i(3, 5)
## About this many Elite Routers per layer in this band (4.2 guarantees).
@export var map_elite_layers: Vector2i = Vector2i(3, 6)
@export var map_elites_per_layer: int = 1
## Terminals as a fraction of the nodes left after the guarantees. ELITE_FREQUENCY_PCT
## modifiers (Heat 25+, ICE 3+) add that fraction of an elite per band layer at
## generation time; a normal Router flips to elite once a whole node accumulates
## (designer ruling 2026-09-24: node types are fixed before the player sees the map).
@export var map_terminal_ratio: float = 0.25
@export var elite_heat: int = 1
@export var card_reward_choices: int = 3
@export var elite_firmware_choices: int = 2
## Routers drop common Firmware this often (GDD 6.3); elites always offer Firmware.
@export var router_firmware_chance: float = 0.35
@export var router_firmware_choices: int = 2
@export var rack_daemon_choices: int = 3
@export var asset_drop_chance: float = 0.4

@export_group("Defense")
@export var armory_capacity: int = 6
## The temporary asset a stationed Botnet adds to its node for each raid (DEPLOY_DRONE
## station bonus).
@export var station_deploy_asset: DefenseAssetData
@export var raid_step_cap: int = 30
@export var cascade_ratio: float = 0.5

@export_group("Campaign")
@export var starting_schematics: int = 20
@export var starting_rookies: int = 2
@export var min_exploits_for_breach: int = 3
## Solace vertical (SOLACE_VERTICAL steps 3-4): when non-empty, every place a campaign picks its corporation
## (new campaign, the picker, CampaignSimulator) uses this corporation, so a playtest is one corp end to end.
## "" = all corporations (shipped). Other corporations' content stays in the game.
@export var campaign_focus_corp: StringName = &""
## Extracting an Exploit at or above this Heat provokes a RETALIATION raid (GDD 4.4;
## Heat objectives never do: they are sinks).
@export var retaliation_min_heat: int = 50
@export var ice_ladder: Array[IceLevelData] = []
## Unlock REBEL_CELL at this ICE on every other corporation.
@export var rebel_cell_unlock_ice: int = 10
## Assist mode (Settings.assist_mode): extra free nudges a turn and operative HP multiple.
@export var assist_free_nudges: int = 1
@export var assist_hp_multiplier: float = 1.25
## REBEL_CELL Mirrors (RebelCellBuilder): slice output multiple, threat integrity multiple
## and damage bonus. "Final final" needs every corporation at this ICE (GDD 8.5).
@export var mirror_output_factor: float = 1.5
@export var mirror_threat_integrity: float = 1.5
@export var mirror_threat_damage_bonus: int = 2
@export var final_final_ice: int = 20
## Mirror elites' passive resistance; the output a Trojan slice mirrors as (an Attack);
## Mirror threat floors (integrity, damage) and the mirrored decoy's speed.
@export var mirror_resistance: int = 1
@export var mirror_trojan_base: int = 6
@export var mirror_threat_min_integrity: int = 10
@export var mirror_threat_min_damage: int = 4
@export var mirror_decoy_speed: int = 2
## New corporations may start at (global best ICE - this).
@export var new_corp_ice_offset: int = 5
## ICE selectable on a fresh profile, and how far past its best win a corporation unlocks.
@export var ice_base_cap: int = 3
@export var ice_unlock_step: int = 3
## Mainframe stock (GDD 4.4): cards, Firmware and Daemons offered per visit.
@export var shop_card_stock: int = 3
@export var shop_firmware_stock: int = 2
@export var shop_daemon_stock: int = 1
## Achievement thresholds: Racks for Banked, raids won for Wall, Perfects for
## Perfectionist (Purge Survivor uses the top Heat threshold).
@export var achievement_racks: int = 10
@export var achievement_raids: int = 20
@export var achievement_perfects: int = 500
## ICE levels a win must reach for the ICE 5 and ICE 10 achievements.
@export var achievement_ice_low: int = 5
@export var achievement_ice_high: int = 10
## Raid pacing: steps between waves, and the Heat per step of threat integrity scaling.
@export var raid_wave_interval: int = 5
@export var raid_heat_scaling_step: int = 10
## DISPATCH voice drift (GDD 8.2): campaigns started before stage 1 and stage 2 lines.
@export var dispatch_drift_mid: int = 3
@export var dispatch_drift_late: int = 6
## Rookie price when no operative is alive (decision 2026-09-24): the cell can always rebuild.
@export var emergency_rookie_cost: int = 0
## ART-0 S0 (ruling 5): where saves and replays go. A run from source saves in the project's
## own git-ignored folder, an exported build in the user folder; finished combats write a
## replay into `replay_subdir` of the save folder when `write_replays` (source runs only).
@export var save_dir_source: String = "res://saves"
@export var save_dir_export: String = "user://saves"
@export var replay_subdir: String = "replays"
@export var write_replays: bool = true
## ART-0 audit B4: the most replay files the replay folder keeps; writing one more deletes
## the oldest (storyboard, demo and harness runs would pile them up). 0 = no cap.
@export var max_replays: int = 50
@export_group("Corp theme")
## Plan 2 WH-02 (REPLAN 2026-10-19 A 2.4): the W2 corporation themes' numbers, one section,
## keys and defaults from the WH-01 tables (docs/handoff/plan2/drafts/themes/tables/). WH-02
## adds them unread; each corp slice (WH-11, WH-21, WH-30, WH-41, WH-51) reads its own.
## Solace THE BLOOM: thousandths of a layer (milli); per-tier arrays are T1..T4.
@export var bloom_start_gap_milli_by_tier: PackedInt32Array = PackedInt32Array([4000, 3500, 3000, 2500])
@export var bloom_hq_start_gap_milli: int = 3000
@export var bloom_pace_node_milli_by_tier: PackedInt32Array = PackedInt32Array([500, 600, 650, 700])
@export var bloom_hq_pace_node_milli: int = 700
## Front advance per combat turn, applied at fight end.
@export var bloom_pace_turn_milli: int = 100
## Extra front advance for an HQ ACROSS move.
@export var bloom_pace_cross_milli: int = 500
@export var bloom_dose_push_milli: int = 1000
## Cycles per dose (Mainframe, Terminal option).
@export var bloom_dose_price: int = 15
## Gap clamp after a dose.
@export var bloom_max_gap_milli: int = 5000
## Band ceilings (gap <=): CLOSE, CATCHING.
@export var bloom_close_gap_milli: int = 2000
@export var bloom_catch_gap_milli: int = 1000
## Percent multiplier on node and turn pace with the Virus key (floor division, minimum 1).
@export var bloom_virus_pace_pct: int = 75
## Heat pace multiplier by band (COOL, NOTICED, FLAGGED, HUNTED, PURGE), percent; applies to
## node and turn pace on the street and in the HQ.
@export var bloom_pace_heat_pct_by_band: PackedInt32Array = PackedInt32Array([100, 110, 125, 140, 160])
## Breach key: one-time setback of the front on the first node entry of a netrun.
@export var bloom_breach_setback_milli: int = 1000
## Intel key: percent multiplier on the per-turn fight cost.
@export var bloom_intel_turn_pct: int = 50
## Solace HQ ladder (WH-10, drafts/hq/solace.md): rungs between the Clinic Gate and the Genome
## Core crown (D10: more than 7 layers), the rung whose rooms hold the Account Manager, the
## Ward-tower rungs that are guaranteed ward rests, and each tower's room-kind weights in the
## order fight, rest, event, elite, shop (stream `hq_graph`, drawn once at generation).
@export var solace_hq_rungs: int = 9
@export var solace_hq_mini_boss_rung: int = 9
@export var solace_hq_ward_rest_rungs: PackedInt32Array = PackedInt32Array([5, 8])
@export var solace_hq_ward_weights: PackedInt32Array = PackedInt32Array([45, 20, 15, 15, 5])
@export var solace_hq_billing_weights: PackedInt32Array = PackedInt32Array([30, 5, 20, 20, 25])
## Plan 2 EX-02 / EX-03 (REPLAN 2.3, 2.10; drafts/exploit_buildings/solace.md): the exploit buildings. Each corporation's
## three Exploit types (intel, breach, virus) are a special building each, placed on a city lot (KeyLots).
## `exploit_building_kinds`: "<corp>/<exploit>" -> the building's kind; an absent entry is "key_<exploit>" (an unbuilt key lot).
@export var exploit_building_kinds: Dictionary = {"solace/virus": "culture_garden"}
## How far (lots, Chebyshev) from its Exploit Site's lot a key's building may stand.
@export var exploit_building_reach_lots: int = 24
## The footprint (BU, width along lot i, depth along lot j) and height class of an exploit building, and the clearance
## round it (BU, the border-street width) that the run's start stands outside of. Art-pass may overrule.
@export var exploit_building_lot_w_bu: float = 48.0
@export var exploit_building_lot_d_bu: float = 42.0
@export var exploit_building_height_class: int = 2
@export var exploit_building_clearance_bu: float = 8.0
## How far (lots) beyond the clearance the border street's start lot is looked for.
@export var exploit_building_start_reach_lots: int = 4
## The run shape: outside layers (O0 start through the gate), inside layers, and the per-layer width cap.
@export var exploit_building_outside_layers: int = 4
@export var exploit_building_inside_layers: int = 5
@export var exploit_building_max_width: int = 3
## Solace campaign infection, basis points: per step base, per living threat per step, the CITY
## LOST threshold, and the decays (raid held, per threat destroyed, per cure: Heat objective Site
## or Proxy Relay completion).
@export var raid_infection_bp_base: int = 50
@export var raid_infection_bp_per_threat: int = 100
@export var raid_infection_lost_bp: int = 10000
@export var raid_infection_decay_hold_bp: int = 1000
@export var raid_infection_decay_per_kill_bp: int = 100
@export var raid_infection_decay_cure_bp: int = 1500

@export_group("Solace tide")
## The Solace raid, the Infected Tide (H5; docs/handoff/raid_integration/SOLACE_RAID_SPEC.md section 7). SolaceTideRules
## reads every number from here. The oracle name of each key is in the spec.
## Longest Genome Core -> HOME route the corp may use, in links (locked links count).
@export var solace_tide_route_max_links: int = 5
## Sealed route candidates the corp draws each raid (the top of the P-target order).
@export var solace_tide_candidates: int = 3
## Raid hand size: the base, plus one for each Heat level in solace_tide_hand_heat reached.
@export var solace_tide_hand_base: int = 4
@export var solace_tide_hand_heat: PackedInt32Array = PackedInt32Array([25, 50, 75])
## A known beam fires for each level in this list the Heat (with the ghost's Heat) reaches, on top of the first.
@export var solace_tide_beam_heat: PackedInt32Array = PackedInt32Array([75, 100])
## Sentries the PLAN can place from the hand.
@export var solace_tide_max_placed: int = 2
@export var solace_tide_ghost_start: int = 2
@export var solace_tide_ghost_heat: int = 5
## Heat a card response (REDEPLOY, DEPLOY, JAM, JAM_B, DIVERT) costs.
@export var solace_tide_card_response_heat: int = 2
## The first `early_raids` raids draw each known beam as a route to HOME with `early_route_pct` percent; later raids
## with `known_route_pct` percent (else it is a street).
@export var solace_tide_early_raids: int = 4
@export var solace_tide_early_route_pct: int = 100
@export var solace_tide_known_route_pct: int = 0
## HOME integrity one hit removes, by Heat band (COOL, NOTICED, FLAGGED, HUNTED, PURGE). Index 4 only for the raid the
## first crossing of the PURGE level queued. Equals the threat damage of the Solace raids (see the schema smoke check).
@export var solace_tide_home_hit_damage_by_band: PackedInt32Array = PackedInt32Array([5, 10, 13, 29, 43])
## Sites lost since the last raid that make the infection spread at DECAY.
@export var solace_tide_spread_min: int = 2
@export var solace_tide_doses_per_decay: int = 2
## A DOSE card arrives every Nth netrun.
@export var solace_tide_dose_every: int = 4
## SACRIFICE needs this many raids since the last one.
@export var solace_tide_sacrifice_gap: int = 2
## Schematics to clean one INFECTED card at the HQ.
@export var solace_tide_clean_price: int = 10
## A raid fires after this many netruns since the last raid (a Heat-threshold raid also resets the count). H7: 3 -> 2
## (R-L lowered the skilled loss to 0.05; the cadence brings it back into 0.08-0.15).
@export var solace_tide_raid_every: int = 2
## H5: a HOME hit adds an INFECTED card tied to HOME.
@export var solace_tide_home_hit_infects: bool = true
## H5: failed Genome Core breaches allowed before the Exploits are spent (one retry = 1).
@export var solace_tide_breach_retries: int = 1
## H5: a SHIFT card may bend a known beam (DIVERT).
@export var solace_tide_divert: bool = true
## H6 (R-I, designer 2026-10-26): CITY LOST is checked only when a raid closes, after the RESPONSE; DECAY and netruns no
## longer end the campaign. False = the H5 checks (after DECAY and after every netrun too).
@export var solace_tide_city_lost_at_raid_end: bool = true
## H6 (R-J, designer 2026-10-26): a known beam draws its path among the paths of its pool through the most live owned
## Sites (the sealed candidates' P-target rule); every path when none crosses one. False = the H5 uniform draw.
@export var solace_tide_known_target: bool = true
## H7 (R-K, designer 2026-10-26): any TAKEN Site can be the target of a netrun (a reclaim run); winning it returns the
## Site to claimed OK at once (its INFECTED card stays). False = a reclaim run only clears it (claim it again).
@export var solace_tide_retake_taken: bool = true
## R-K: Heat a retake adds on top of the run's own.
@export var solace_tide_retake_heat: int = 0
## R-K: Schematics a retake pays to bring the Site back OK; with fewer the Site is only cleared (claim it again).
@export var solace_tide_retake_schematics: int = 0
## R-K: the node a retaken Site comes back with (its old node was lost when it was TAKEN).
@export var solace_tide_retake_node: StringName = &"firewall_relay"
## H7 (R-L, designer 2026-10-26): a sentry that blocks a beam of its type shields its Site for the rest of the raid.
@export var solace_tide_sentry_shields: bool = true
## R-D: percent of an entry step the Bloom start front moves per INFECTED card.
@export var solace_tide_infected_front_step_pct: int = 100
## R-F: percent of the Genome Core's HP added per INFECTED card at the breach. 0 = off until it is calibrated with the
## CampaignSimulator (Phase 2b).
@export var solace_tide_boss_hp_pct_per_infected: int = 25
## The opening defense deck, one "id:type:verb" per card (type D, N or E; verb GUARD, SHIFT or JAM) until R-C maps the
## Armory and the stationed operatives onto cards.
@export var solace_tide_start_deck: PackedStringArray = PackedStringArray(["s0:D:GUARD", "s1:D:GUARD", "s2:N:GUARD",
	"s3:N:GUARD", "s4:E:GUARD", "s5:D:SHIFT", "s6:E:SHIFT", "s7:N:JAM"])
## R-C (Phase 2b): an Armory asset becomes a defense card. Indexed by RC.AssetType (TURRET, ICE_LOCK, DECOY): the card's
## type (D, N or E) and verb. A damage asset guards, an ICE Lock jams, a Decoy shifts the beam.
@export var solace_tide_asset_card_types: PackedStringArray = PackedStringArray(["D", "N", "E"])
@export var solace_tide_asset_card_verbs: PackedStringArray = PackedStringArray(["GUARD", "JAM", "SHIFT"])
## R-C: the class card a stationed operative adds to the raid deck, one "class_id:type:verb" per class.
@export var solace_tide_class_cards: PackedStringArray = PackedStringArray(["breaker:D:GUARD", "wrecker:D:GUARD",
	"overclocker:D:SHIFT", "ghost:E:GUARD", "phantom:E:SHIFT", "rigger:N:GUARD", "botnet:N:JAM", "hivemind:N:SHIFT"])
## Designer ruling 2026-10-25: Solace keeps its story and retaliation raids (claim and node-built stay off); in a tide campaign
## each queues a tide raid. A raid's HOME hit is at least the damage of this Heat band (index into
## `solace_tide_home_hit_damage_by_band`): story = 9 + 6 as if every threat reached HOME (15, nearest the 13 of band 2),
## retaliation = 3 + 4 (7, nearest the 5 of band 0).
@export var solace_tide_story_band: int = 2
@export var solace_tide_retaliation_band: int = 0
## The automatic defense (the simulator and an unattended raid) scores each placement by the raid's damage over the
## forecast's 12 outcomes: HOME points lost, Sites newly TAKEN and Sites newly DOWN, each times its weight; the lowest wins.
@export var solace_tide_auto_home_weight: int = 4
@export var solace_tide_auto_taken_weight: int = 3
@export var solace_tide_auto_down_weight: int = 1
## SACRIFICE picks the cheapest live Site off every line: a Site is worth this by tier (index tier - 1, clamped), plus
## the bonus for an Exploit Site. (Spec ambiguity: the oracle's TIER_VALUE and EXPLOIT_BONUS were not listed in section 7.)
@export var solace_tide_site_value_by_tier: PackedInt32Array = PackedInt32Array([6, 8, 10])
@export var solace_tide_exploit_site_value: int = 6
## Halcyon THE EYE: sector width and step (degrees), octants moved per campaign turn (one ended netrun), turns
## fixed after an Exploit.
@export var eye_sector_deg: int = 90
@export var eye_step_deg: int = 45
@export var eye_move_per_turn: int = 1
@export var eye_fix_turns: int = 2
## TIER_DOWN stacks on the scanned slice; Blade classes per level (EnemyClass names plus RACK).
@export var blade_tier_drop: int = 1
@export var blade_classes_l1: Array[StringName] = [&"ELITE", &"MINI_BOSS", &"RACK"]
@export var blade_classes_l2: Array[StringName] = [&"NORMAL", &"ELITE", &"MINI_BOSS", &"BOSS", &"RACK"]
## Heat added per Elite fight at Spotted level 2.
@export var spotted_elite_heat: int = 1
## HQ gaze steps per completed node and per climb; BLOCKED half width (degrees); dial centres.
@export var hq_gaze_step_per_node: int = 1
@export var hq_gaze_step_per_climb: int = 2
@export var hq_beam_half_width_deg: int = 4
@export var hq_dial_steps: int = 3
## Threat damage bonus inside the sector (percent).
@export var raid_eye_damage_pct: int = 25
## Unused since v2 (a shuttered node cannot be entered).
@export var eye_shuttered_cost_heat: int = 1
## Halcyon v2: the Blade's top level, the HQ gaze step per Stall, Alert gains (eye fight, Stall,
## Power cut), the Lockdown threshold, beam multiplier and Blade bonus, Cut the Power's asleep steps.
@export var blade_level_max: int = 2
@export var hq_gaze_step_per_stall: int = 1
@export var hq_alert_gain_eye_fight: int = 1
@export var hq_alert_gain_stall: int = 1
@export var hq_alert_gain_power_cut: int = 2
@export var hq_lockdown_alert: int = 4
@export var hq_lockdown_beam_mult: int = 2
@export var hq_lockdown_blade_bonus: int = 1
@export var hq_power_cut_steps: int = 2
## Halcyon HQ graph (WH-20, drafts/hq/halcyon.md): layer kinds (comma lists of R router, E elite,
## T terminal, M mainframe, B bay/rest, C cache, K rack, X mini-boss, V vault boss), each layer's
## face azimuth, the azimuth jitter per layer and the spread between a layer's nodes (degrees),
## the Annex layers and their kinds (rest, cache, power), the climbs (origin and target layers),
## the rest heal percent, cache choices and rebuild attempts.
@export var halcyon_hq_layer_kinds: PackedStringArray = PackedStringArray(["R,R,R", "R,T", "R,T,M", "R,E", "B,R,C", "K,R,E", "E,R", "R,T,M", "B,R", "R,E,R", "K,B", "X", "V"])
@export var halcyon_hq_layer_face_deg: PackedInt32Array = PackedInt32Array([180, 180, 180, 90, 90, 0, 0, 270, 270, 180, 180, 90, 0])
@export var halcyon_hq_face_jitter_deg: int = 20
@export var halcyon_hq_node_spread_deg: int = 24
@export var halcyon_hq_annex_layers: PackedInt32Array = PackedInt32Array([3, 7, 9])
@export var halcyon_hq_annex_kinds: PackedStringArray = PackedStringArray(["cache", "power", "rest"])
@export var halcyon_hq_climb_origins: PackedInt32Array = PackedInt32Array([3, 5])
@export var halcyon_hq_climb_targets: PackedInt32Array = PackedInt32Array([10, 12])
@export var halcyon_hq_rest_heal_pct: int = 35
@export var halcyon_hq_cache_choices: int = 3
@export var halcyon_hq_max_attempts: int = 300
## REBEL_CELL DISPATCH: operatives (one per lane), layers per lane graph, lead limit (layers).
@export var hq_lanes_required: int = 3
@export var hq_lane_layers: int = 7
@export var hq_lead_limit: int = 2
## Heal percent of max HP per Rest node and at THROW.
@export var hq_rest_heal_pct: int = 30
@export var hq_throw_heal_pct: int = 20
## Extra starting RAM in a scouted lane's first fight.
@export var lane_scout_ram: int = 2
## Step thresholds for seq 1 and seq 2 (seq 3 on THROW).
@export var hq_seq_steps: PackedInt32Array = PackedInt32Array([3, 5])
## Percent node weights per lane (the rest goes as the generator allocates).
@export var hq_lane_node_weights: Dictionary = {
	&"ROOF": {&"elite": 30, &"event": 15, &"shop": 10},
	&"STREET": {&"elite": 20, &"event": 25, &"shop": 15},
	&"SEWER": {&"elite": 15, &"event": 40, &"shop": 15},
}
## Percent of the HQ tilt away from neutral STREET weights in a street netrun.
@export var street_lane_tilt_pct: int = 50
## Start-of-fight modifiers on dispatch_core, one per ARMED lane.
@export var hq_lane_effects: Dictionary = {
	&"ROOF": {&"enemy_resistance_delta": -2, &"enemy_resistance_floor": 0},
	&"STREET": {&"first_phase_hub_heal": false},
	&"SEWER": {&"operative_ram_bonus": 2},
}
## First-wave threat count for REBEL_CELL raids (the table's raid_config key; no raid config
## resource exists, so it lives here).
@export var rebel_raid_first_wave: int = 3
## Fixed lane order, also the finale resolve order (Q34); a Site without a lane tag reads
## `lane_tag_default` (RebelCellCampaignTheme).
@export var hq_lane_ids: Array[StringName] = [&"ROOF", &"STREET", &"SEWER"]
@export var lane_tag_default: StringName = &"STREET"
## Orbital BLACKOUT: dark fight nodes per street netrun and their layer range, DARK turn
## cadence (street, HQ) and first DARK turn; the HQ dark residues of `layer mod modulus`.
@export var street_dark_nodes: int = 1
@export var dark_layer_min: int = 3
@export var dark_layer_max: int = 6
@export var street_dark_every: int = 3
@export var hq_dark_every: int = 2
@export var dark_turn_first: int = 1
@export var hq_dark_pattern: PackedInt32Array = PackedInt32Array([0, 1])
@export var dark_pattern_modulus: int = 4
## Layers lit after an Uplink Dish clear; Uplink Dish nodes per HQ run; Dead Zone hops.
@export var uplink_lit_layers: int = 2
@export var hq_uplink_count: int = 3
@export var raid_dark_radius: int = 1
## Meridian A PAYLOAD (the table's `meridian.` keys): Load weights, Capacity (base, per Rank,
## per target tier T1..T4), Over resistance cap, Jettison refund percent and Cycles values,
## Weigh Stations (capacity penalty, HQ layers), boss hub divisor, raid node capacity and delay.
@export var meridian_weight_firmware: int = 1
@export var meridian_weight_daemon: int = 2
@export var meridian_weight_asset: int = 2
@export var meridian_capacity_base: int = 5
@export var meridian_capacity_per_rank: int = 1
@export var meridian_capacity_tier_bonus: PackedInt32Array = PackedInt32Array([2, 1, 1, 0])
@export var meridian_over_resistance_cap: int = 3
@export var meridian_jettison_refund_pct: int = 50
@export var meridian_station_capacity_penalty: int = 2
@export var meridian_weigh_station_layers: PackedInt32Array = PackedInt32Array([4, 7, 10])
@export var meridian_hub_load_divisor: int = 3
@export var meridian_raid_node_capacity: int = 2
@export var meridian_raid_overcap_delay_steps: int = 1
@export var meridian_jettison_value_firmware: int = 30
@export var meridian_jettison_value_daemon: int = 60
@export var meridian_jettison_value_asset: int = 40
@export_group("City generator")
## Plan 2 NA-12 (D3), kept by the planner city A2 (CITY-A2 step 2 removed the grid generator and its other numbers):
## HQ rects and Site layouts stay `city_gen_edge_lots` inside the city and Sites `city_gen_coast_clear` lots from the
## water; Site layout headings are tried `city_gen_aim_step_deg` degrees apart round each HQ.
@export var city_gen_edge_lots: int = 6
@export var city_gen_coast_clear: int = 4
@export var city_gen_aim_step_deg: float = 15.0
@export_group("City plan A2")
## CITY-A2 (D3, 2026-10-19): every city seed is the art-pass planner city `city_a2_path` (CityPlanA2; step 2: the
## default seed too). A2 metres per lot (20 km over the 165-lot city), the lots rasterised past the city rect, the river
## kinds that are water, the least road half width (lots), and A2 district id -> game territory id (others: Sprawl).
@export var city_a2_path: String = "res://content/city/city_A2.json"
@export var city_a2_metres_per_lot: float = 121.212
@export var city_a2_raster_margin: int = 16
@export var city_a2_river_kinds: PackedStringArray = PackedStringArray(["river"])
@export var city_a2_road_half_min: float = 0.5
@export var city_a2_territories: Dictionary = {"centre": "rebel_cell", "halcyon": "halcyon", "solace": "solace",
	"orbital": "orbital", "meridian": "meridian"}
## Per seed: an HQ centre within `city_a2_hq_jitter` lots of its A2 HQ (draws, then the A2 spot, then the nearest fit),
## the whole rect on land in its own district, `city_gen_edge_lots` inside the city, `city_a2_hq_gap` lots off any other.
@export var city_a2_hq_jitter: float = 4.0
@export var city_a2_hq_tries: int = 24
@export var city_a2_hq_gap: int = 1
@export var city_a2_hq_search: int = 12
## Local streets: per A2 district a seeded spacing (lots, min / max, both axes) and phase; a building cell spans two
## lots with `city_a2_merge_share`; footprints inset `city_a2_inset` lots.
@export var city_a2_block_lots: Vector2i = Vector2i(4, 7)
@export var city_a2_merge_share: float = 0.35
@export var city_a2_inset: float = 0.12
## Building height (BU, min / max) by neighbourhood kind (A2 `neighbourhoods[].kind`, a lot inside its radius), else
## &"corp" (a corporation's district), &"old_core" (the Old City), &"sprawl"; within `city_a2_hq_rise_lots` of a
## corporation's HQ heights grow up to x(1 + `city_a2_hq_rise`). Towers over `city_a2_setback_from` BU get a setback
## tier (`city_a2_setback`: x inset lots, y share of the height below it); taper range on the top tier.
@export var city_a2_heights: Dictionary = {&"corp": Vector2(10.0, 34.0), &"old_core": Vector2(5.0, 16.0),
	&"sprawl": Vector2(4.0, 14.0), &"industrial": Vector2(4.0, 10.0), &"informal": Vector2(2.0, 6.0),
	&"rail_grid": Vector2(5.0, 14.0), &"suburb": Vector2(3.0, 8.0)}
@export var city_a2_hq_rise: float = 1.2
@export var city_a2_hq_rise_lots: float = 18.0
@export var city_a2_setback_from: float = 18.0
@export var city_a2_setback: Vector2 = Vector2(0.18, 0.6)
@export var city_a2_taper: Vector2 = Vector2(0.85, 1.0)
## Street look: share of a territory's street lots in its corporation's color; traffic by A2 road class (local: &"local").
@export var city_a2_corp_ink_share: float = 0.35
## LOOK L5 (whole-city plate parity, art-pass city_world_a2 "four sub-lots: denser, finer grain"): a single lot of a kind in
## `city_a2_sub_kinds` under the setback height splits with `city_a2_sub_share` into four quarter-lot buildings, inset
## `city_a2_sub_inset` lots, each its own height in the kind's range x `city_a2_sub_h_k`.
@export var city_a2_sub_kinds: Array[StringName] = []
@export var city_a2_sub_share: float = 0.0
@export var city_a2_sub_inset: float = 0.05
@export var city_a2_sub_h_k: float = 0.8
## LOOK L5 suite: a split lot's four stand on a whole-lot plinth this tall (bu; 0 = none), its base part for the NA-11 rules.
@export var city_a2_sub_plinth_bu: float = 0.0
@export var city_a2_traffic: Dictionary = {&"ring": 1.0, &"motorway": 1.0, &"truck": 0.8, &"arterial": 0.6,
	&"collector": 0.45, &"local": 0.2}
## The most one seed's A2 plan and subdivision may take (seconds, this machine; the 200-seed sweep asserts it).
@export var city_a2_budget_s: float = 2.0
## CITY-A2 step 2: the terrain (CityA2Terrain). A2's hills (height_m x lot_bu / metres per lot x `city_a2_hill_exag`);
## outside the outer ring road `city_a2_outer_ring` (a closed A2 road id) foothills and mountains rising with the distance
## d (lots) past it: over `city_a2_foot` (d from / to) up to `city_a2_foot_h` BU, over `city_a2_mountain` up to
## `city_a2_mountain_h` BU, shaped by value noise on lattices of `city_a2_noise_cells` lots (broad, fine, ridge) drawn
## from stream `city_terrain` of `city_a2_terrain_seed`; no mountain within `city_a2_mountain_shore` lots of the water; the
## land falls to the sea over `city_a2_beach` lots. The land runs `city_a2_land_margin` lots past the city rect, sampled
## every `city_a2_land_step` lots past the raster.
@export var city_a2_hill_exag: float = 1.5
@export var city_a2_outer_ring: StringName = &"road_001"
@export var city_a2_foot: Vector2 = Vector2(2.5, 25.0)
@export var city_a2_foot_h: float = 12.0
@export var city_a2_mountain: Vector2 = Vector2(28.0, 80.0)
@export var city_a2_mountain_h: float = 60.0
@export var city_a2_noise_cells: Vector3 = Vector3(33.0, 13.0, 40.0)
@export var city_a2_terrain_seed: int = 5101
@export var city_a2_mountain_shore: Vector2 = Vector2(1.2, 7.5)
@export var city_a2_beach: Vector2 = Vector2(0.5, 2.5)
## LOOK L5 (designer 2026-10-20): the shore's blur radius (lots) on the fine ground: the coast runs as a smooth line, not
## lot steps (0 = the lot-grid shore).
@export var city_a2_coast_smooth: float = 0.0
@export var city_a2_land_margin: int = 120
@export var city_a2_land_step: int = 3
## CITY-A2 r2 (art-pass terrain_a2.py): the far horizon ridge, the mountains x(1 + x) rising over y..z lots past the outer
## ring; the raster's fine heights blend into the coarse land over `city_a2_land_blend` lots inside the raster's edge (one
## surface, no step); per-lot jitter lattice (a 4th lattice of the terrain stream, 1 lot cells).
@export var city_a2_mountain_edge: Vector3 = Vector3(0.45, 78.0, 124.0)
## LOOK L5 (whole-city plate parity): the mountains' ridged relief, x BU on hashed value noise of y and z lots (weights 0.7,
## 0.3), rising over `city_a2_relief_from` lots past the outer ring (no stream draw; 0 BU = none).
@export var city_a2_relief: Vector3 = Vector3(0.0, 17.0, 7.0)
@export var city_a2_relief_from: Vector2 = Vector2(10.0, 40.0)
## LOOK L5 (designer 2026-10-20: "more character"): the relief's domain warp, x lots on value noise of y lots (0 = none),
## and a third, finer ridged octave of z x the relief on cells of half its fine cell.
@export var city_a2_relief_warp: Vector3 = Vector3(0.0, 30.0, 0.0)
## LOOK L5 (designer 2026-10-20, the plate's west cliffs; art-pass terrain_a2.py cliff): x BU of sea cliff on the coast
## past the outer ring (rising over 1..6 lots past it), west of A2 x metres `city_a2_cliff_x` (full at .x, none at .y);
## its face rises over shore lots `city_a2_cliff_shore` .x..y and its back falls over .z..w (0 BU = none).
@export var city_a2_cliff: float = 0.0
@export var city_a2_cliff_x: Vector2 = Vector2(-7000.0, -5500.0)
@export var city_a2_cliff_shore: Vector4 = Vector4(0.4, 1.6, 4.0, 14.0)
@export var city_a2_land_blend: float = 12.0
## CITY-A2 r2 (art-pass zoning_a2.py): no building on ground over `city_a2_max_build_h` BU or steeper than
## `city_a2_max_build_slope` (BU per BU); past the outer ring (lots, moved by the terrain's broad noise x
## `city_a2_edge_noise` lots) a lot keeps its building with the chance falling over `city_a2_sprawl_fade` (from, to).
@export var city_a2_max_build_h: float = 42.0
@export var city_a2_max_build_slope: float = 0.3
@export var city_a2_edge_noise: float = 5.0
@export var city_a2_sprawl_fade: Vector2 = Vector2(0.5, 6.0)
## LOOK L5 (designer 2026-10-20): the city's edge dwindles, not stops: past the outer ring a lot's building chance also
## falls as its ground nears `city_a2_max_build_h` (from x of it) and its slope `city_a2_max_build_slope` (from y of it),
## and within z lots of the plan rect's edge; the building's height shrinks with that chance to `city_a2_dwindle_h_min`.
@export var city_a2_dwindle: Vector3 = Vector3(1.0, 1.0, 0.0)
@export var city_a2_dwindle_h_min: float = 1.0
## LOOK L5 (designer 2026-10-20, height variety): per height kind, the height range's curve exponent (1 = even; over 1:
## mostly low with a few tall) and a share of buildings `city_a2_height_spike` x taller (by a hash of the lot, no draw).
@export var city_a2_height_pow: Dictionary = {}
@export var city_a2_height_spike: Vector2 = Vector2(0.0, 1.0)
## LOOK L5 suite: no spike on a lot within this many lots of an HQ rect (NA-11c HQ zone; 0 = spikes anywhere).
@export var city_a2_spike_hq_clear: int = 0
## LOOK L5 (designer 2026-10-20, the drowned quarter): there `city_a2_sink_share` of the buildings (no Site's) stand
## sunk, their base `city_a2_sink_bu` (from, to) BU under the ground and their top under the water.
@export var city_a2_sink_share: float = 0.0
@export var city_a2_sink_bu: Vector2 = Vector2(3.0, 7.0)
## Past the outer ring by more than this (lots), open Sprawl land has no local streets either.
@export var city_a2_sprawl_streets: float = 16.0
## LOOK L5 (designer 2026-10-20): no building within this many lots (Chebyshev) of a sea lot (0 = build to the shore;
## rivers keep their frontage, a Site its building).
@export var city_a2_coast_setback: int = 0
## LOOK L5 (designer 2026-10-20): a local street lot with no building lot within this many lots (Chebyshev) is open land
## (0 = keep every street; a Site's streets always stay).
@export var city_a2_prune_streets: int = 0
## Within this many lots of a Site the sprawl does not thin (the run's street keeps its frontage).
@export var city_a2_sprawl_site_keep: int = 8
## CITY-A2 r2 (art-pass zoning `clear`): lots each side of an A2 road of the class kept open under its elevated deck.
@export var city_a2_corridor: Dictionary = {&"ring": 1, &"motorway": 1, &"truck": 1}
## Solace district layout (A-069 / A-070, designer 2026-10-21). Off in the script default (every other config and test keeps
## the A2 grid); the shipped config turns it on. On: inside the Solace territory the local street grid becomes one park, the
## buildings stand in blocks of `city_sol_block_lots` lots a side with a lawn gap of `city_sol_gap_lots` lots, heights are
## `city_sol_height_k` of the A2 Solace heights (never under `city_sol_min_floors` storeys), and the HQ plinth circle is cleared.
@export var city_sol_layout: bool = false
## Block side (lots), min..max.
@export var city_sol_block_lots: Vector2i = Vector2i(2, 3)
## Lawn lots between two blocks (at least).
@export var city_sol_gap_lots: int = 1
## Share of the A2 Solace building height a block keeps.
@export var city_sol_height_k: float = 0.5
## Least storeys of a Solace block (x NetrunArtUnits.floor_bu).
@export var city_sol_min_floors: int = 3
## The HQ plinth's outer radius (BU): no block reaches into this circle round the HQ centre.
@export var city_sol_plinth_r_bu: float = 35.0
## Lots between two path gates along the park edge, and the service lanes (curved, gate to gate).
@export var city_sol_gate_spacing: int = 8
@export var city_sol_lanes: int = 3
## Path routing: a lot's cost is 1 + wobble x its noise (more = more winding).
@export var city_sol_path_wobble: float = 1.6
## Path / lane widths (BU).
@export var city_sol_path_width_bu: float = 2.4
@export var city_sol_lane_width_bu: float = 4.0
## Ponds: count and radius range (lots).
@export var city_sol_ponds: int = 3
@export var city_sol_pond_r: Vector2 = Vector2(0.9, 1.4)
## The park outline's corner cutting passes and its wobble (lots).
@export var city_sol_outline_passes: int = 2
@export var city_sol_outline_wobble: float = 0.18
@export_group("Combat FX")
## ART-2 2C (ART_BIBLE v2 §3.20, round 18 binary_damage NOTES): a hit's 0/1 shards scale
## with the damage it deals: count = base + per_dmg x damage (at most max), glyph px =
## base + per_dmg x damage (at most max; px at text scale 1.0). A crit uses the max.
@export var fx_shard_base: int = 8
@export var fx_shard_per_dmg: float = 1.4
@export var fx_shard_max: int = 40
@export var fx_glyph_px_base: float = 18.0
@export var fx_glyph_px_per_dmg: float = 0.9
@export var fx_glyph_px_max: float = 38.0
## ART-2 2C (§3.15 H1 "the city reacts"): what the combat backdrop shows per Heat band,
## indexed COOL, NOTICED, FLAGGED, HUNTED, PURGE (PURGE = HUNTED's look for now): alarm
## beacons on side buildings, searchlights at the screen sides (sweeping away from the
## target), alarm beacons on the target, police light clusters, searchlights on the target.
@export var heat_city_side_beacons: PackedInt32Array = PackedInt32Array([0, 3, 0, 0, 0])
@export var heat_city_side_searchlights: PackedInt32Array = PackedInt32Array([0, 0, 2, 0, 0])
@export var heat_city_target_beacons: PackedInt32Array = PackedInt32Array([0, 0, 2, 0, 0])
@export var heat_city_police_lights: PackedInt32Array = PackedInt32Array([0, 0, 0, 13, 13])
@export var heat_city_target_searchlights: PackedInt32Array = PackedInt32Array([0, 0, 0, 2, 2])
## ART-0 audit B1 (ART_BIBLE v2 §3.15, §5.5; round 18-22 heat_glitch band table): the Heat
## glitch Options extra per band (COOL, NOTICED, FLAGGED, HUNTED, PURGE = HUNTED's): seconds
## between bursts, a burst's seconds, the chromatic tear bands and the macroblocks a burst
## throws at its peak. Each band adds to the one before; every burst is short and periodic.
@export var heat_glitch_period: PackedFloat32Array = PackedFloat32Array([3.2, 2.6, 2.0, 1.6, 1.6])
@export var heat_glitch_burst: PackedFloat32Array = PackedFloat32Array([0.08, 0.16, 0.26, 0.32, 0.32])
@export var heat_glitch_tears: PackedInt32Array = PackedInt32Array([0, 10, 12, 18, 18])
@export var heat_glitch_blocks: PackedInt32Array = PackedInt32Array([0, 0, 48, 96, 96])


## ART-2 2C: the 0/1 shard count for a hit of `damage` (a crit takes the most).
## Config problems (N9): a RAM-cost multiplier or divisor below 1.
func config_errors() -> PackedStringArray:
	var errors := PackedStringArray()
	if corrupted_ram_cost_multiplier < 1:
		errors.append("corrupted_ram_cost_multiplier: %d is below 1." % corrupted_ram_cost_multiplier)
	if corrupted_enemy_ram_divisor < 1:
		errors.append("corrupted_enemy_ram_divisor: %d is below 1." % corrupted_enemy_ram_divisor)
	return errors


## The N9 retired fields still written in a config .tres text (CORRUPTED no longer damages
## or drains; it is a RAM cost, ruling Q36). One error per field found.
static func retired_field_errors(tres_text: String) -> PackedStringArray:
	var errors := PackedStringArray()
	for field in RETIRED_FIELDS:
		for line in tres_text.split("\n"):
			if line.strip_edges().begins_with(field + " ="):
				errors.append("%s: retired by N9 (CORRUPTED is a RAM cost, ruling Q36); remove it from the config." % field)
				break
	return errors


func fx_shard_count(damage: int, crit: bool = false) -> int:
	if crit:
		return fx_shard_max
	return clampi(fx_shard_base + roundi(fx_shard_per_dmg * maxi(0, damage)), 1, fx_shard_max)


## ART-2 2C: the largest shard glyph (px at text scale 1.0) for a hit of `damage`.
func fx_glyph_px(damage: int, crit: bool = false) -> float:
	if crit:
		return fx_glyph_px_max
	return minf(fx_glyph_px_max, fx_glyph_px_base + fx_glyph_px_per_dmg * maxi(0, damage))


## Highest ICE level on the ladder (final_final_ice when the ladder is empty).
func max_ice_level() -> int:
	var top := -1
	for l in ice_ladder:
		if l != null:
			top = maxi(top, l.level)
	return top if top >= 0 else final_final_ice


## The MAJOR Heat threshold levels, ascending (UI bands and poster marks).
func major_heat_levels() -> Array[int]:
	var out: Array[int] = []
	for t in heat_thresholds:
		if t != null and t.kind == RC.ThresholdKind.MAJOR:
			out.append(t.heat)
	out.sort()
	return out


## The Solace tide's opening deck as cards: [[id, type, verb], ...] (see `solace_tide_start_deck`).
func solace_tide_start_cards() -> Array:
	var out: Array = []
	for entry in solace_tide_start_deck:
		var p := entry.split(":")
		if p.size() == 3:
			out.append([p[0], p[1], p[2]])
	return out


## The class card of `class_id` as [id, type, verb] ("c_<class>" is not used: the caller names the id), or [] for none.
func solace_tide_class_card(class_id: StringName) -> Array:
	for entry in solace_tide_class_cards:
		var p := entry.split(":")
		if p.size() == 3 and p[0] == String(class_id):
			return [p[0], p[1], p[2]]
	return []


## The [type, verb] card an Armory asset of `asset_type` (RC.AssetType) becomes.
func solace_tide_asset_card(asset_type: int) -> Array:
	var i := clampi(asset_type, 0, solace_tide_asset_card_types.size() - 1)
	return [solace_tide_asset_card_types[i], solace_tide_asset_card_verbs[clampi(i, 0, solace_tide_asset_card_verbs.size() - 1)]]


func _validate_solace_tide(errors: PackedStringArray) -> void:
	if solace_tide_story_band < 0 or solace_tide_story_band > 4 or solace_tide_retaliation_band < 0 or solace_tide_retaliation_band > 4:
		errors.append("solace_tide_story_band and _retaliation_band are Heat bands 0..4.")
	if solace_tide_asset_card_types.size() != solace_tide_asset_card_verbs.size() or solace_tide_asset_card_types.is_empty():
		errors.append("solace_tide_asset_card_types and _verbs need one entry per asset type.")
	for t in solace_tide_asset_card_types:
		if not ["D", "N", "E"].has(t):
			errors.append("solace_tide_asset_card_types: '%s' is not D, N or E." % t)
	for v in solace_tide_asset_card_verbs:
		if not ["GUARD", "SHIFT", "JAM"].has(v):
			errors.append("solace_tide_asset_card_verbs: '%s' is not GUARD, SHIFT or JAM." % v)
	for entry in solace_tide_class_cards:
		var p := entry.split(":")
		if p.size() != 3 or not ["D", "N", "E"].has(p[1]) or not ["GUARD", "SHIFT", "JAM"].has(p[2]):
			errors.append("solace_tide_class_cards entry '%s' must be class:type:verb." % entry)
	if solace_tide_home_hit_damage_by_band.size() != 5:
		errors.append("solace_tide_home_hit_damage_by_band needs 5 entries (COOL .. PURGE).")
	if solace_tide_route_max_links < 2 or solace_tide_candidates < 2 or solace_tide_max_placed < 0:
		errors.append("solace_tide route links, candidates and max placed are out of range.")
	if solace_tide_dose_every < 1 or solace_tide_raid_every < 1:
		errors.append("solace_tide_dose_every and solace_tide_raid_every must be >= 1.")
	if solace_tide_retake_heat < 0 or solace_tide_retake_schematics < 0 or solace_tide_retake_node == &"":
		errors.append("solace_tide_retake_heat / _schematics must be >= 0 and solace_tide_retake_node set.")
	if solace_tide_early_route_pct < 0 or solace_tide_early_route_pct > 100 or solace_tide_known_route_pct < 0 or solace_tide_known_route_pct > 100:
		errors.append("solace_tide route percents must be 0..100.")
	if solace_tide_site_value_by_tier.is_empty():
		errors.append("solace_tide_site_value_by_tier needs at least one entry.")
	if solace_tide_start_cards().size() != solace_tide_start_deck.size():
		errors.append("solace_tide_start_deck entries must be id:type:verb.")


## What a Solace Site is worth to the SACRIFICE choice (tier clamped to the table).
func solace_tide_site_value(tier: int, exploit: bool) -> int:
	var t := solace_tide_site_value_by_tier
	var v := 0 if t.is_empty() else int(t[clampi(tier - 1, 0, t.size() - 1)])
	return v + (solace_tide_exploit_site_value if exploit else 0)


## Where the Heat bands start, ascending (GDD 4.3): the MAJOR levels and the PURGE level.
## Below the first is COOL; then NOTICED, FLAGGED, HUNTED, PURGE.
func heat_band_levels() -> Array[int]:
	var out: Array[int] = []
	for t in heat_thresholds:
		if t != null and (t.kind == RC.ThresholdKind.MAJOR or t.kind == RC.ThresholdKind.PURGE):
			out.append(t.heat)
	out.sort()
	return out


## N2: a tier (1..4) as an index into the per-tier tables; tiers below 1 clamp to 0, above
## 4 to 3.
static func tier_index(tier: int) -> int:
	return clampi(tier - 1, 0, 3)


## N2 (R2): enemy slice output factor at `tier` (clamped to 1..4).
func enemy_damage_factor(tier: int) -> float:
	return _table_at(enemy_damage_by_tier, tier)


## N2: legacy HP multiplier at `tier` (clamped) for enemies without hp_by_tier / hp_bands.
func enemy_hp_scale(tier: int) -> float:
	return _table_at(enemy_hp_scale_by_tier, tier)


## N2 (R2): the reference player's damage per turn at `tier` (clamped).
func reference_dpt(tier: int) -> int:
	if reference_dpt_by_tier.is_empty():
		return 0
	return reference_dpt_by_tier[mini(tier_index(tier), reference_dpt_by_tier.size() - 1)]


## N2 (R2): the HP band [min, max] of `band_class` (&"normal", &"elite", &"mini_boss_2",
## &"mini_boss_3") at `tier` (clamped). Vector2i.ZERO = no band at that tier.
func hp_band(band_class: StringName, tier: int) -> Vector2i:
	var arr: PackedInt32Array = hp_band_table(band_class)
	var i := tier_index(tier) * 2
	if arr.size() < i + 2:
		return Vector2i.ZERO
	return Vector2i(arr[i], arr[i + 1])


## N2: the raw 8-entry band array of `band_class`; empty for an unknown class.
func hp_band_table(band_class: StringName) -> PackedInt32Array:
	match band_class:
		&"normal": return hp_band_normal
		&"elite": return hp_band_elite
		&"mini_boss_2": return hp_band_mini_boss_2
		&"mini_boss_3": return hp_band_mini_boss_3
	return PackedInt32Array()


func _table_at(arr: PackedFloat64Array, tier: int) -> float:
	if arr.is_empty():
		return 1.0
	return arr[mini(tier_index(tier), arr.size() - 1)]


func _validate_tier_tables(errors: PackedStringArray) -> void:
	for pair in [["enemy_damage_by_tier", enemy_damage_by_tier], ["enemy_hp_scale_by_tier", enemy_hp_scale_by_tier],
			["reference_dpt_by_tier", reference_dpt_by_tier]]:
		var arr: Variant = pair[1]
		if arr.size() != 4:
			errors.append("%s must have 4 entries." % pair[0])
			continue
		for i in 4:
			if arr[i] <= 0:
				errors.append("%s must be > 0." % pair[0])
				break
		for i in range(1, 4):
			if arr[i] < arr[i - 1]:
				errors.append("%s must be non-decreasing." % pair[0])
				break
	if target_turns_per_phase <= 0.0:
		errors.append("target_turns_per_phase must be > 0.")
	for band_class: StringName in [&"normal", &"elite", &"mini_boss_2", &"mini_boss_3"]:
		var arr := hp_band_table(band_class)
		if arr.size() != 8:
			errors.append("hp_band_%s must have 8 entries (min, max per tier)." % band_class)
			continue
		for t in 4:
			if arr[t * 2] > arr[t * 2 + 1] or arr[t * 2] < 0:
				errors.append("hp_band_%s T%d has min above max." % [band_class, t + 1])
	if boss_hp_band_open_ceiling <= 1.0:
		errors.append("boss_hp_band_open_ceiling must be above 1.0.")


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	_validate_tier_tables(errors)
	errors.append_array(config_errors())  # N9
	if max_replays < 0:
		errors.append("max_replays must be >= 0 (0 = no cap).")
	_validate_city_gen(errors)
	for arr in [rack_heat_by_tier, rack_schematics_by_tier, raid_schematics_by_tier]:
		if arr.size() != 4:
			errors.append("Per-tier arrays need 4 entries.")
	_validate_enrage(errors)
	_validate_solace_tide(errors)
	if easy_normal_fights < 0:
		errors.append("easy_normal_fights must be >= 0.")
	if event_fight_tier_cap < 1 or event_fight_tier_cap > enemy_hp_scale_by_tier.size():
		errors.append("event_fight_tier_cap must be 1..%d (the tiers the enemy tables cover)." % enemy_hp_scale_by_tier.size())
	if hq_event_every_runs < 0:
		errors.append("hq_event_every_runs must be >= 0 (0 = no HQ events).")
	if resistance_min_by_class.size() != RC.EnemyClass.size() or resistance_max_by_class.size() != RC.EnemyClass.size():
		errors.append("Resistance ranges need one entry per enemy class (%d)." % RC.EnemyClass.size())
	else:
		for k in RC.EnemyClass.size():
			if resistance_min_by_class[k] < 0 or resistance_min_by_class[k] > resistance_max_by_class[k]:
				errors.append("Resistance range for class %d must be 0 <= min <= max." % k)
	if sandbox_charges < 1 or sandbox_charges_perfect < sandbox_charges:
		errors.append("sandbox_charges must be >= 1 and sandbox_charges_perfect >= sandbox_charges.")
	if listener_max_per_turn_default < 1:
		errors.append("listener_max_per_turn_default must be >= 1.")
	if phase_count_min_by_class.size() != RC.EnemyClass.size() or phase_count_max_by_class.size() != RC.EnemyClass.size():
		errors.append("Phase counts need one entry per enemy class (%d)." % RC.EnemyClass.size())
	else:
		for k in RC.EnemyClass.size():
			if phase_count_min_by_class[k] < 1 or phase_count_min_by_class[k] > phase_count_max_by_class[k]:
				errors.append("Phase count range for class %d must be 1 <= min <= max." % k)
	for r in [cycles_combat_range, cycles_elite_range, cycles_router_range, card_price_range,
			firmware_price_range, daemon_price_range, netrun_boost_cost_range]:
		if r.x > r.y:
			errors.append("Range %s has min above max." % r)
	if node_upgrade_costs.is_empty():
		errors.append("node_upgrade_costs needs at least one entry.")
	for b in netrun_boosts:
		if b != null and (b.cost < netrun_boost_cost_range.x or b.cost > netrun_boost_cost_range.y):
			errors.append("Boost %s costs %d, outside %s." % [b.id, b.cost, netrun_boost_cost_range])
	var last := 0
	var threshold_ids := {}
	for t in heat_thresholds:
		if t == null:
			continue
		if t.heat <= last:
			errors.append("Heat thresholds must be in ascending order.")
		last = t.heat
		# ANIM-R4 H5: the id keys the threshold's text for translation.
		if t.id == &"":
			errors.append("Heat threshold %d needs an id." % t.heat)
		elif threshold_ids.has(t.id):
			errors.append("Duplicate Heat threshold id %s." % t.id)
		threshold_ids[t.id] = true
	var levels := {}
	for l in ice_ladder:
		if l == null:
			continue
		if levels.has(l.level):
			errors.append("Duplicate ICE level %d." % l.level)
		levels[l.level] = true
	# ART-2 2C: the Heat city's counts are one per band (five bands).
	for arr in [heat_city_side_beacons, heat_city_side_searchlights, heat_city_target_beacons, heat_city_police_lights, heat_city_target_searchlights]:
		if arr.size() != 5:
			errors.append("Heat city counts need 5 entries (one per Heat band).")
	# ART-0 audit B1: the Heat glitch's table is one entry per band; a burst is shorter than its period.
	for arr in [heat_glitch_period, heat_glitch_burst, heat_glitch_tears, heat_glitch_blocks]:
		if arr.size() != 5:
			errors.append("Heat glitch values need 5 entries (one per Heat band).")
	if heat_glitch_period.size() == 5 and heat_glitch_burst.size() == 5:
		for b in 5:
			if heat_glitch_burst[b] <= 0.0 or heat_glitch_burst[b] >= heat_glitch_period[b]:
				errors.append("Heat glitch band %d: a burst must be > 0 and shorter than its period." % b)
	if fx_shard_base < 1 or fx_shard_max < fx_shard_base or fx_glyph_px_max < fx_glyph_px_base:
		errors.append("FX shard counts / glyph sizes out of order.")
	return errors


## N4: the class default enrage for RC.EnemyClass `cls` (a fresh EnrageData, never a loaded
## Resource), or null when that class has none (start turn 0 or no entry).
func enrage_default(cls: int) -> EnrageData:
	if cls < 0 or cls >= enrage_start_turn_by_class.size() or enrage_start_turn_by_class[cls] <= 0:
		return null
	var e := EnrageData.new()
	e.start_turn = enrage_start_turn_by_class[cls]
	e.every_n_turns = enrage_every_n_turns_by_class[cls] if cls < enrage_every_n_turns_by_class.size() else 0
	e.damage_pct_step = enrage_damage_pct_step_by_class[cls] if cls < enrage_damage_pct_step_by_class.size() else 0
	return e


## N4: the enrage `data` fights with: its authored one, else its class default, else null
## (normals). Satellites never enrage: CombatResolver skips them.
func enrage_for(data: EnemyData) -> EnrageData:
	if data == null:
		return null
	if data.enrage != null:
		return data.enrage
	return enrage_default(data.enemy_class())


## NA-12: the numbers the planner city keeps from the grid generator.
func _validate_city_gen(errors: PackedStringArray) -> void:
	if city_gen_edge_lots < 0 or city_gen_coast_clear < 0:
		errors.append("city_gen_edge_lots and city_gen_coast_clear must be >= 0.")
	if city_gen_aim_step_deg <= 0.0 or city_gen_aim_step_deg > 360.0:
		errors.append("city_gen_aim_step_deg must be in (0, 360].")
	_validate_city_a2(errors)
	_validate_exploit_building(errors)


## CITY-A2: the planner city's numbers.
func _validate_city_a2(errors: PackedStringArray) -> void:
	if city_a2_metres_per_lot <= 0.0 or city_a2_raster_margin < 0 or city_a2_road_half_min <= 0.0 or city_a2_budget_s <= 0.0:
		errors.append("city_a2_metres_per_lot, city_a2_road_half_min and city_a2_budget_s must be > 0, city_a2_raster_margin >= 0.")
	if city_a2_hq_jitter < 0.0 or city_a2_hq_tries < 0 or city_a2_hq_gap < 0 or city_a2_hq_search < 0:
		errors.append("city_a2_hq_jitter, city_a2_hq_tries, city_a2_hq_gap and city_a2_hq_search must be >= 0.")
	if city_a2_block_lots.x < 2 or city_a2_block_lots.x > city_a2_block_lots.y:
		errors.append("city_a2_block_lots must be 2 <= min <= max.")
	if city_sol_block_lots.x < 1 or city_sol_block_lots.x > city_sol_block_lots.y or city_sol_gap_lots < 1 or city_sol_height_k <= 0.0 \
			or city_sol_min_floors < 1 or city_sol_plinth_r_bu < 0.0 or city_sol_gate_spacing < 2 or city_sol_lanes < 0 \
			or city_sol_ponds < 0 or city_sol_pond_r.x <= 0.0 or city_sol_pond_r.x > city_sol_pond_r.y or city_sol_outline_passes < 0:
		errors.append("city_sol_*: block 1 <= min <= max, gap >= 1, height_k > 0, min_floors >= 1, plinth_r >= 0, gate_spacing >= 2, lanes / ponds >= 0, pond_r 0 < min <= max.")
	if city_a2_merge_share < 0.0 or city_a2_merge_share > 1.0 or city_a2_corp_ink_share < 0.0 or city_a2_corp_ink_share > 1.0:
		errors.append("city_a2_merge_share and city_a2_corp_ink_share must be in [0, 1].")
	if city_a2_sub_share < 0.0 or city_a2_sub_share > 1.0 or city_a2_sub_inset < 0.0 or city_a2_sub_inset >= 0.25 or city_a2_sub_h_k <= 0.0:
		errors.append("city_a2_sub_share must be in [0, 1], city_a2_sub_inset in [0, 0.25), city_a2_sub_h_k > 0.")
	if city_a2_inset < 0.0 or city_a2_inset >= 0.5 or city_a2_setback.x < 0.0 or city_a2_setback.y <= 0.0 or city_a2_setback.y >= 1.0:
		errors.append("city_a2_inset must be in [0, 0.5), city_a2_setback x >= 0 and y in (0, 1).")
	if city_a2_taper.x <= 0.0 or city_a2_taper.x > city_a2_taper.y or city_a2_hq_rise < 0.0 or city_a2_hq_rise_lots <= 0.0:
		errors.append("city_a2_taper must be 0 < min <= max, city_a2_hq_rise >= 0, city_a2_hq_rise_lots > 0.")
	for k: StringName in [&"corp", &"old_core", &"sprawl"]:
		var h: Variant = city_a2_heights.get(k)
		if not (h is Vector2 and (h as Vector2).x > 0.0 and (h as Vector2).x <= (h as Vector2).y):
			errors.append("city_a2_heights %s must be a Vector2 0 < min <= max." % k)
	if not city_a2_traffic.has(&"local"):
		errors.append("city_a2_traffic needs a local entry.")
	if city_a2_land_blend < 0.0 or city_a2_land_blend > float(city_a2_raster_margin) or city_a2_max_build_h <= 0.0 \
			or city_a2_max_build_slope <= 0.0 or city_a2_sprawl_fade.x >= city_a2_sprawl_fade.y or city_a2_mountain_edge.y >= city_a2_mountain_edge.z:
		errors.append("city_a2_land_blend must be 0..city_a2_raster_margin, city_a2_max_build_h / _slope > 0, city_a2_sprawl_fade and city_a2_mountain_edge from < to.")
	if city_a2_hill_exag < 0.0 or city_a2_foot_h < 0.0 or city_a2_mountain_h < 0.0 or city_a2_land_margin < 0 or city_a2_land_step < 1:
		errors.append("city_a2_hill_exag, city_a2_foot_h, city_a2_mountain_h, city_a2_land_margin must be >= 0, city_a2_land_step >= 1.")
	for v: Vector2 in [city_a2_foot, city_a2_mountain, city_a2_mountain_shore, city_a2_beach]:
		if v.x < 0.0 or v.x >= v.y:
			errors.append("city_a2_foot, city_a2_mountain, city_a2_mountain_shore and city_a2_beach must be 0 <= from < to.")
			break
	if city_a2_noise_cells.x <= 0.0 or city_a2_noise_cells.y <= 0.0 or city_a2_noise_cells.z <= 0.0:
		errors.append("city_a2_noise_cells must be > 0.")


func _validate_enrage(errors: PackedStringArray) -> void:
	var n := RC.EnemyClass.size()
	if enrage_start_turn_by_class.size() != n or enrage_every_n_turns_by_class.size() != n or enrage_damage_pct_step_by_class.size() != n:
		errors.append("Enrage defaults need one entry per enemy class (%d)." % n)
		return
	if enrage_start_turn_by_class[RC.EnemyClass.NORMAL] != 0:
		errors.append("enrage_start_turn_by_class: normals have no enrage (0).")
	for k in n:
		var d := enrage_default(k)
		if d != null:
			for problem in d.validate():
				errors.append("%s (class %d default)" % [problem, k])

## RG-01 (run_graph v2): new netruns generate v2 graphs (REST, WORKSHOP, CACHE nodes may appear).
## False keeps v1 maps (no new node kinds).
@export var map_v2_enabled: bool = true
## RG-06 lint: unique node ids (MapGraph node key `unique_id`) allowed to be an Intel, Relay or
## Ambush node in a netrun map. Normal runs have none of these kinds.
@export var map_unique_allow: PackedStringArray = PackedStringArray(["orbital_uplink_dish"])

## RG-02 REST node (drafts/nodes/rest.md). PATCH heals this percent of the operative's max HP
## (round half up, clamped to max HP); REWIRE swaps Firmware between two wheel slots, this many
## swaps per visit (one mode per visit).
@export var rest_heal_pct: int = 35
@export var rest_rewire_swaps: int = 1
## Placement: the guaranteed REST sits in these layers (inclusive); `node_weight_rest` is the
## percent chance a run gets it (100 = always). An extra REST is rolled with the tier's percent
## (index tier - 1) in `rest_extra_layers`, at most `rest_max_per_run` in all, never two in a layer.
@export var node_weight_rest: int = 100
@export var rest_guaranteed_layers: Vector2i = Vector2i(4, 5)
@export var rest_extra_layers: Vector2i = Vector2i(3, 6)
@export var rest_extra_chance_pct_by_tier: PackedInt32Array = PackedInt32Array([0, 15, 35, 35])
@export var rest_max_per_run: int = 2

## RG-03 WORKSHOP (drafts/nodes/workshop.md; the slice-refit form while N18 slice upgrades are not built).
## Offers drawn per visit, purchases per visit, the refit price (the NULL slot costs more), the
## percent chance of one per run from `workshop_min_tier` up, and its layers (never in a layer that holds a Mainframe).
@export var workshop_offers_per_visit: int = 3
@export var workshop_buys_per_visit: int = 1
@export var workshop_slice_price: int = 60
@export var workshop_null_slice_price: int = 90
@export var node_weight_workshop: int = 90
@export var workshop_min_tier: int = 2
@export var workshop_layers: Vector2i = Vector2i(3, 6)

## RG-04 CACHE (drafts/nodes/cache.md). A plain reward: Cycles in `cache_cycles_range` (scaled by the tier's reward
## scale) and a card offer of `cache_card_choices`. The mini-puzzle stays off (`cache_puzzle_enabled`) until a puzzle
## passes the vetting rubric (CacheRules.VETTED_PUZZLES is empty). Placement: percent chance of one per run,
## on a Terminal in `cache_layers`.
@export var node_weight_cache: int = 60
@export var cache_layers: Vector2i = Vector2i(2, 6)
@export var cache_cycles_range: Vector2i = Vector2i(30, 60)
@export var cache_card_choices: int = 3
@export var cache_puzzle_enabled: bool = false


## EX-02 / EX-03: the exploit building numbers.
func _validate_exploit_building(errors: PackedStringArray) -> void:
	if exploit_building_reach_lots < 0 or exploit_building_start_reach_lots < 0:
		errors.append("exploit_building_reach_lots and exploit_building_start_reach_lots must be >= 0.")
	if exploit_building_lot_w_bu <= 0.0 or exploit_building_lot_d_bu <= 0.0 or exploit_building_clearance_bu < 0.0:
		errors.append("exploit_building_lot_w_bu and exploit_building_lot_d_bu must be > 0, exploit_building_clearance_bu >= 0.")
	if exploit_building_outside_layers < 1 or exploit_building_inside_layers < 3 or exploit_building_max_width < 3:
		errors.append("exploit_building_outside_layers must be >= 1, exploit_building_inside_layers >= 3, exploit_building_max_width >= 3.")
