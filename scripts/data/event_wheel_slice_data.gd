class_name EventWheelSliceData
extends Resource
## Plan 2 EV-01: one slice of an event wheel and what lands when the pointer rests on it.

@export var label: String
@export_range(1, 30) var size_ticks: int = 1
## Run-level effects (GAIN_CYCLES, MODIFY_HEAT, HEAL, DEAL_DAMAGE, GAIN_SCHEMATICS).
@export var effects: Array[EffectData] = []
@export var map_edits: Array[MapEditData] = []
## One common Firmware drawn from the `events` stream, offered as a pick.
@export var common_firmware: bool = false
@export var next_combat_overrides: EventCombatModsData
@export var starts_combat: EventFightData


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if label == "":
		errors.append("wheel_slice_label_missing: a wheel slice needs a label.")
	if size_ticks < 1:
		errors.append("wheel_slice_size_lt_1: size_ticks is %d." % size_ticks)
	for e in effects:
		if e != null:
			errors.append_array(e.validate())
	for m in map_edits:
		if m != null:
			errors.append_array(m.validate())
	if next_combat_overrides != null:
		errors.append_array(next_combat_overrides.validate())
	if starts_combat != null:
		errors.append_array(starts_combat.validate())
	return errors
