class_name CampaignConfigData
extends Resource
## Global tuning in one place (Section 11). One .tres for the whole game.

@export_group("Heat")
@export var heat_max: int = 100
@export var heat_thresholds: Array[HeatThresholdData] = []
@export var death_heat_base: int = 10
@export var lost_raid_heat: int = 5
## Heat per Server Rack capture, indexed by tier - 1.
@export var rack_heat_by_tier: PackedInt32Array = PackedInt32Array([2, 3, 5, 8])

@export_group("Economy")
@export var cycles_per_schematic: int = 10
## Schematics per Server Rack, indexed by tier - 1.
@export var rack_schematics_by_tier: PackedInt32Array = PackedInt32Array([10, 17, 29, 50])
@export var raid_schematics_by_tier: PackedInt32Array = PackedInt32Array([8, 12, 18, 25])
@export var node_repair_ratio: float = 0.5
@export var enemy_scale_per_tier: float = 1.6
@export var reward_scale_per_tier: float = 1.7

@export_group("Combat")
@export var hand_size: int = 5
@export var draw_per_turn: int = 5
@export var partial_multiplier: float = 0.5
@export var overclock_multiplier: float = 1.5
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
@export var elite_heat: int = 1
@export var card_reward_choices: int = 3
@export var elite_firmware_choices: int = 2
@export var rack_daemon_choices: int = 3
@export var asset_drop_chance: float = 0.4

@export_group("Defense")
@export var armory_capacity: int = 6
@export var raid_step_cap: int = 30
@export var cascade_ratio: float = 0.5

@export_group("Campaign")
@export var starting_schematics: int = 20
@export var starting_rookies: int = 2
@export var min_exploits_for_breach: int = 3
@export var ice_ladder: Array[IceLevelData] = []
## Unlock REBEL_CELL at this ICE on every other corporation.
@export var rebel_cell_unlock_ice: int = 10
## New corporations may start at (global best ICE - this).
@export var new_corp_ice_offset: int = 5


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	for arr in [rack_heat_by_tier, rack_schematics_by_tier, raid_schematics_by_tier]:
		if arr.size() != 4:
			errors.append("Per-tier arrays need 4 entries.")
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
