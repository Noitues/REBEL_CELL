class_name EventFightData
extends Resource
## Plan 2 EV-01: a fight a Terminal event choice (or an event wheel slice) opens on the spot.
## It runs as a combat of the run (the run's tier and overrides) against `enemy_id`.

@export var enemy_id: StringName = &""
## Modifiers for this fight only.
@export var combat_overrides: EventCombatModsData
## true: the fight pays the usual Router rewards (Cycles roll, card offer, Firmware chance) as
## well as the win payload below. false: the win payload replaces them.
@export var normal_rewards: bool = true
## Heat added when the fight starts.
@export var entry_heat: int = 0
## Stake: the win payload is paid only if the operative ends the fight at or above this percent
## of max HP (0 = no stake). A lost stake is still a won fight.
@export_range(0, 100) var stake_min_hp_pct: int = 0
## The win payload (stake permitting).
@export var win_cycles: int = 0
@export var win_heat: int = 0
## One common Firmware drawn from the `events` stream, offered as a pick.
@export var win_common_firmware: bool = false


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if enemy_id == &"":
		errors.append("event_fight_enemy_missing: starts_combat needs an enemy_id.")
	if combat_overrides != null:
		errors.append_array(combat_overrides.validate())
	if stake_min_hp_pct < 0 or stake_min_hp_pct > 100:
		errors.append("event_fight_stake_range: stake_min_hp_pct %d is outside 0..100." % stake_min_hp_pct)
	if stake_min_hp_pct > 0 and win_cycles == 0 and win_heat == 0 and not win_common_firmware:
		errors.append("event_fight_stake_empty: a stake guards nothing (no win payload).")
	return errors
