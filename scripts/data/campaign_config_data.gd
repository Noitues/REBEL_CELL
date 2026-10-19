class_name CampaignConfigData
extends Resource

## Config fields N9 retired; the content validator rejects them (retired_field_errors).
const RETIRED_FIELDS: Array[String] = ["corrupted_self_damage", "corrupted_damage_per_major", "corrupted_ram_drain"]
## Global tuning in one place (Section 11). One .tres for the whole game.

@export_group("Heat")
@export var heat_max: int = 100
@export var heat_thresholds: Array[HeatThresholdData] = []
@export var death_heat_base: int = 10
@export var lost_raid_heat: int = 5
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
## Doses granted at T1 netrun start.
@export var bloom_free_doses_t1: int = 1
## Band ceilings (gap <=): CLOSE, CATCHING.
@export var bloom_close_gap_milli: int = 2000
@export var bloom_catch_gap_milli: int = 1000
## Percent multiplier on node and turn pace with the Virus key (floor division, minimum 1).
@export var bloom_virus_pace_pct: int = 75
## Mini-boss and boss fights add no turn pace (node entry still applies).
@export var bloom_exempt_boss_turn_cost: bool = true
## Heat never changes street pace.
@export var bloom_heat_affects_street: bool = false
## Solace raid infection, basis points: start per Heat band (COOL, NOTICED, FLAGGED, HUNTED,
## PURGE), per step base, per living threat per step, the CITY LOST threshold.
@export var raid_infection_start_bp_by_band: PackedInt32Array = PackedInt32Array([0, 500, 1000, 1500, 2000])
@export var raid_infection_bp_base: int = 50
@export var raid_infection_bp_per_threat: int = 100
@export var raid_infection_lost_bp: int = 10000
## Halcyon THE EYE: sector width and step (degrees), octants moved per counted netrun, netruns
## fixed after an Exploit.
@export var eye_sector_deg: int = 90
@export var eye_step_deg: int = 45
@export var eye_move_per_netrun: int = 1
@export var eye_fix_netruns: int = 2
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
## Heat charged to use a non-fight HQ node in the eye.
@export var eye_shuttered_cost_heat: int = 1
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
## Plan 2 NA-12 (D3): the per-seed city (CityGenerator), in lots. The Cell's territory stands
## within `city_gen_cell_jitter` of the land's centre; every corporation's HQ centre on a ring
## round it (`city_gen_ring_lots` min / max radius), evenly turned with `city_gen_angle_jitter`
## (share of the even step) of play, two HQ centres at least `city_gen_hq_gap` apart. HQ rects
## and Site layouts stay `city_gen_edge_lots` inside the city and `city_gen_coast_clear` from
## the water. Territory pull per corporation and per neutral Sprawl centre (count, range);
## `city_gen_candidates` best-candidate draws per Sprawl centre; `city_gen_attempts` whole
## layouts before the fixed city is the fallback.
@export var city_gen_cell_jitter: float = 10.0
@export var city_gen_ring_lots: Vector2 = Vector2(34.0, 42.0)
@export var city_gen_angle_jitter: float = 0.2
@export var city_gen_hq_gap: float = 26.0
@export var city_gen_edge_lots: int = 6
@export var city_gen_coast_clear: int = 4
@export var city_gen_pull_range: Vector2 = Vector2(0.9, 1.2)
@export var city_gen_neutral_count: int = 3
@export var city_gen_neutral_pull_range: Vector2 = Vector2(0.8, 1.0)
@export var city_gen_candidates: int = 24
@export var city_gen_attempts: int = 16
## The coast (one side of the city is sea): depth from the city's edge, wave amplitude and
## wavelength (lots, min / max).
@export var city_gen_coast_depth: Vector2 = Vector2(8.0, 18.0)
@export var city_gen_coast_wave: Vector2 = Vector2(2.0, 5.0)
@export var city_gen_coast_wavelength: Vector2 = Vector2(40.0, 80.0)
## NA-12 r2 (art-pass item 17, the A2 bay): a second, shorter shore wave (amplitude, wavelength); the bay (a
## Gaussian bump of the shore into the land: depth, width (sigma), and how far its middle may sit off the sea edge's
## middle, as a share of that edge); the Cell's HQ centre this many lots inland of the bay head; the arc (degrees,
## centred on the inland direction) the ring's corporations share; corporations whose HQ stands on the shore (its
## rect within `city_gen_shore_touch` lots of the water, on a bay flank `city_gen_shore_flank` bay widths off its middle).
@export var city_gen_coast_wave2: Vector2 = Vector2(1.0, 3.0)
@export var city_gen_coast_wavelength2: Vector2 = Vector2(15.0, 30.0)
@export var city_gen_bay_depth: Vector2 = Vector2(18.0, 30.0)
@export var city_gen_bay_width: Vector2 = Vector2(16.0, 26.0)
@export var city_gen_bay_shift: float = 0.15
@export var city_gen_cell_inland: float = 10.0
@export var city_gen_ring_arc_deg: float = 220.0
@export var city_gen_shore_corps: Array[StringName] = [&"tethys"]
@export var city_gen_shore_touch: float = 2.0
@export var city_gen_shore_flank: Vector2 = Vector2(1.2, 2.0)
## Terrain hills (data only until NA-12c): count, sigma (lots) and height (BU) ranges, on land.
@export var city_gen_hill_count: Vector2i = Vector2i(2, 4)
@export var city_gen_hill_sigma: Vector2 = Vector2(8.0, 20.0)
@export var city_gen_hill_height: Vector2 = Vector2(6.0, 24.0)
## Site layout headings tried round each HQ (degrees apart).
@export var city_gen_aim_step_deg: float = 15.0
## The most one seed's generation may take (seconds, this machine; the 1,000-seed sweep asserts it).
@export var city_gen_budget_s: float = 2.0
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
	if easy_normal_fights < 0:
		errors.append("easy_normal_fights must be >= 0.")
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


## NA-12: the city generator's numbers (ranges min <= max, counts and gaps positive).
func _validate_city_gen(errors: PackedStringArray) -> void:
	for r: Vector2 in [city_gen_ring_lots, city_gen_pull_range, city_gen_neutral_pull_range, city_gen_coast_depth,
			city_gen_coast_wave, city_gen_coast_wavelength, city_gen_coast_wave2, city_gen_coast_wavelength2, city_gen_bay_depth,
			city_gen_bay_width, city_gen_shore_flank, city_gen_hill_sigma, city_gen_hill_height]:
		if r.x > r.y or r.x < 0.0:
			errors.append("city_gen range %s must be 0 <= min <= max." % r)
	if city_gen_pull_range.x <= 0.0 or city_gen_neutral_pull_range.x <= 0.0 or city_gen_coast_wavelength.x <= 0.0:
		errors.append("city_gen pulls and the coast wavelength must be > 0.")
	if city_gen_hq_gap <= 0.0 or city_gen_candidates < 1 or city_gen_attempts < 1 or city_gen_neutral_count < 0:
		errors.append("city_gen_hq_gap, city_gen_candidates and city_gen_attempts must be > 0, city_gen_neutral_count >= 0.")
	if city_gen_edge_lots < 0 or city_gen_coast_clear < 0 or city_gen_cell_jitter < 0.0 or city_gen_angle_jitter < 0.0:
		errors.append("city_gen_edge_lots, city_gen_coast_clear, city_gen_cell_jitter and city_gen_angle_jitter must be >= 0.")
	if city_gen_coast_wavelength2.x <= 0.0 or city_gen_bay_width.x <= 0.0 or city_gen_hill_sigma.x <= 0.0:
		errors.append("city_gen_coast_wavelength2, city_gen_bay_width and city_gen_hill_sigma must be > 0.")
	if city_gen_ring_arc_deg <= 0.0 or city_gen_ring_arc_deg > 360.0 or city_gen_bay_shift < 0.0 or city_gen_bay_shift >= 0.5:
		errors.append("city_gen_ring_arc_deg must be in (0, 360] and city_gen_bay_shift in [0, 0.5).")
	if city_gen_hill_count.x < 0 or city_gen_hill_count.x > city_gen_hill_count.y or city_gen_shore_touch < 0.0 or city_gen_cell_inland < 0.0:
		errors.append("city_gen_hill_count must be 0 <= min <= max; city_gen_shore_touch and city_gen_cell_inland >= 0.")
	if city_gen_aim_step_deg <= 0.0 or city_gen_aim_step_deg > 360.0 or city_gen_budget_s <= 0.0:
		errors.append("city_gen_aim_step_deg must be in (0, 360] and city_gen_budget_s > 0.")


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
