class_name CardData
extends Resource
## A Subroutine card. Cards only manipulate wheels (spin, nudge, flip,
## temporary bonuses); wheels do the attacking and defending.

@export var id: StringName
@export var display_name: String
@export_multiline var description: String
@export var rarity: RC.Rarity = RC.Rarity.COMMON
@export var ram_cost: int = 1
@export var cycle_cost: int = 60
## Empty = shared pool. Otherwise the id of the owning class.
@export var class_id: StringName = &""
@export var wheel_target: RC.WheelTarget = RC.WheelTarget.OWN
@export var effects: Array[EffectData] = []
@export var exhaust: bool = false
## False = never offered as a reward or in a Modem (the ICE "Bug" card).
@export var offered: bool = true
@export var art: Texture2D


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if effects.is_empty():
		errors.append("Card %s has no effects." % id)
	for e in effects:
		if e:
			errors.append_array(e.validate())
	return errors
