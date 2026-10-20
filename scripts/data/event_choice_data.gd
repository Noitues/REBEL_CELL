class_name EventChoiceData
extends Resource

@export var label: String
@export_multiline var result_text: String
@export var cycle_cost: int = 0
@export var hp_cost: int = 0
@export var effects: Array[EffectData] = []
## Card, Firmware, Daemon, DefenseAsset or ClassData (rescued operative).
@export var reward: Resource
## Plan 2 EV-01: what a choice can start or leave behind. All default to none.
## A fight the choice opens on the spot (resolved by the run, rewards per EventFightData).
@export var starts_combat: EventFightData
## A pending modifier for the next `duration_combats` completed fights (stored in the run).
@export var next_combat_overrides: EventCombatModsData
## A pending modifier for the next raid (stored on the campaign, spent by that raid).
@export var next_raid_overrides: EventRaidModsData
## An event wheel the choice spins (outcome on commit).
@export var event_wheel: EventWheelData
## Edits to the run's map, applied in order.
@export var map_edits: Array[MapEditData] = []
## One common Firmware drawn from the `events` stream, offered as a pick (a "?" in the preview).
@export var common_firmware: bool = false


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if label == "":
		errors.append("event_choice_label_missing: a choice needs a label.")
	if starts_combat != null and event_wheel != null:
		errors.append("event_choice_fight_and_wheel: a choice starts a fight or spins a wheel, not both.")
	for e in effects:
		if e != null:
			errors.append_array(e.validate())
	for m in map_edits:
		if m != null:
			errors.append_array(m.validate())
	if starts_combat != null:
		errors.append_array(starts_combat.validate())
	if next_combat_overrides != null:
		errors.append_array(next_combat_overrides.validate())
	if next_raid_overrides != null:
		errors.append_array(next_raid_overrides.validate())
	if event_wheel != null:
		errors.append_array(event_wheel.validate())
	return errors
