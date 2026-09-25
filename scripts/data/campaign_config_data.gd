class_name CampaignConfigData
extends Resource
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
## Enemy HP per tier: base x this^(tier - 1) (GDD 11.6).
@export var enemy_scale_per_tier: float = 1.6
## Enemy slice output (damage, block, heal) per tier (decision 2026-09-24: split from HP
## scaling after the balance simulation; operatives do not gain HP, so 1.6^3 damage at T4
## one-shot them). Applies to bosses and mini-bosses like everything else.
@export var enemy_damage_scale_per_tier: float = 1.6
@export var reward_scale_per_tier: float = 1.7
## Cycles earned (11.1) as inclusive [min, max] ranges.
@export var cycles_combat_range: Vector2i = Vector2i(10, 20)
@export var cycles_elite_range: Vector2i = Vector2i(30, 40)
@export var cycles_router_range: Vector2i = Vector2i(15, 25)

@export_group("Shop")
## Modem shop prices in Cycles (11.2), inclusive [min, max] ranges.
@export var card_price_range: Vector2i = Vector2i(50, 75)
@export var firmware_price_range: Vector2i = Vector2i(75, 150)
@export var daemon_price_range: Vector2i = Vector2i(150, 250)
@export var card_removal_price: int = 50
## Added to card_removal_price after each removal.
@export var card_removal_increment: int = 25
@export var slice_overwrite_price: int = 100
@export var miss_slice_overwrite_price: int = 150
## Slice catalogue a Modem draws its overwrite offers from (designer ruling 2026-09-24).
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
@export var partial_multiplier: float = 0.5
@export var overclock_multiplier: float = 1.5
## Output of a slice with a PARASITE docked on it (Botnet).
@export var parasite_multiplier: float = 0.5
@export var shield_cap: int = 15
@export var corrupted_self_damage: int = 3
## Added to corrupted_self_damage per MAJOR Heat threshold crossed.
@export var corrupted_damage_per_major: int = 1
@export var corrupted_ram_drain: int = 1
@export var extra_nudge_ram_cost: int = 1

@export_group("Netrun")
@export var map_layers: int = 7
@export var map_nodes_min: int = 2
@export var map_nodes_max: int = 4
## Layers (1-based) holding a Server Rack. The last one is the run's final node.
@export var rack_layers: PackedInt32Array = PackedInt32Array([4, 7])
## At least one Modem somewhere in these layers (inclusive band).
@export var map_modem_layers: Vector2i = Vector2i(3, 5)
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
## Mirror elites' passive resistance; the output a Deploy slice mirrors as (an Attack);
## Mirror threat floors (integrity, damage) and the mirrored decoy's speed.
@export var mirror_resistance: int = 1
@export var mirror_deploy_base: int = 6
@export var mirror_threat_min_integrity: int = 10
@export var mirror_threat_min_damage: int = 4
@export var mirror_decoy_speed: int = 2
## New corporations may start at (global best ICE - this).
@export var new_corp_ice_offset: int = 5
## ICE selectable on a fresh profile, and how far past its best win a corporation unlocks.
@export var ice_base_cap: int = 3
@export var ice_unlock_step: int = 3
## Modem stock (GDD 4.4): cards, Firmware and Daemons offered per visit.
@export var shop_card_stock: int = 3
@export var shop_firmware_stock: int = 2
@export var shop_daemon_stock: int = 1
## Rookie price when no operative is alive (decision 2026-09-24): the cell can always rebuild.
@export var emergency_rookie_cost: int = 0


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


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	for arr in [rack_heat_by_tier, rack_schematics_by_tier, raid_schematics_by_tier]:
		if arr.size() != 4:
			errors.append("Per-tier arrays need 4 entries.")
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
	for t in heat_thresholds:
		if t == null:
			continue
		if t.heat <= last:
			errors.append("Heat thresholds must be in ascending order.")
		last = t.heat
	var levels := {}
	for l in ice_ladder:
		if l == null:
			continue
		if levels.has(l.level):
			errors.append("Duplicate ICE level %d." % l.level)
		levels[l.level] = true
	return errors
