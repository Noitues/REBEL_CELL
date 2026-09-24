class_name EffectData
extends Resource
## One atomic effect. Slices, cards, Firmware, ring segments, Hubs, Daemons
## and network nodes all describe what they do as lists of these.

@export var type: RC.EffectType = RC.EffectType.DEAL_DAMAGE
@export var target: RC.EffectTarget = RC.EffectTarget.POINTER_TARGET
## Nudges hit one ring; spins, flips and respins always hit the whole wheel.
@export var ring_scope: RC.RingScope = RC.RingScope.OUTER
@export var amount: int = 0
@export var multiplier: float = 1.0
@export var status: RC.Status = RC.Status.NONE
## Slice-level effects only (APPLY_STATUS, CLEANSE): which slice of the target wheel.
@export var slice_pick: RC.SlicePick = RC.SlicePick.UNDER_POINTER
## 0 = instant or permanent.
@export var duration_turns: int = 0
## Only used when type is CUSTOM (rule-breaking behaviour lives in code).
@export var custom_handler: Script


func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	var whole_wheel_only := [RC.EffectType.SPIN, RC.EffectType.FLIP, RC.EffectType.RESPIN]
	if type in whole_wheel_only and ring_scope != RC.RingScope.WHOLE_WHEEL:
		errors.append("%s must use ring_scope WHOLE_WHEEL." % RC.EffectType.keys()[type])
	if type == RC.EffectType.NUDGE and ring_scope == RC.RingScope.WHOLE_WHEEL:
		errors.append("NUDGE must target OUTER or INNER ring.")
	if type == RC.EffectType.APPLY_STATUS and status == RC.Status.NONE:
		errors.append("APPLY_STATUS needs a status.")
	if type == RC.EffectType.CUSTOM and custom_handler == null:
		errors.append("CUSTOM effect needs a custom_handler script.")
	return errors
