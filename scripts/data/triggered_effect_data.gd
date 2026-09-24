class_name TriggeredEffectData
extends Resource
## "When X happens (and conditions hold), do these effects."

@export var trigger: RC.Trigger = RC.Trigger.ON_SLICE_TRIGGER
## Minimum precision tier needed for slice-based triggers.
@export var min_tier: RC.PrecisionTier = RC.PrecisionTier.PARTIAL
## e.g. Clean Signal = 3 consecutive ON_PERFECT.
@export_range(1, 10) var consecutive_required: int = 1
## 0 = unlimited. e.g. Stolen Intent = 1.
@export var limit_per_combat: int = 0
@export var effects: Array[EffectData] = []


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if effects.is_empty():
		errors.append("Triggered effect has no effects.")
	for e in effects:
		if e == null:
			errors.append("Triggered effect contains an empty entry.")
		else:
			errors.append_array(e.validate())
	return errors
