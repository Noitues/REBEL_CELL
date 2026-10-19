class_name SliceData
extends Resource
## A wheel slice type: Attack, Defend, Crit, Null, etc.

@export var id: StringName
@export var display_name: String
@export var slice_type: RC.SliceType = RC.SliceType.SHIM
@export var target_rule: RC.TargetRule = RC.TargetRule.POINTER
## Damage for SHIM/OVERFLOW, block for DEFRAG/SANDBOX, drone count for TROJAN.
@export var base_output: int = 0
## FLAT or PERCENT (plan 2 R5). PERCENT only on HOTFIX, DEFRAG and SANDBOX: `base_output`
## is then 0..100, a share of the owner's max HP, never rescaled by the tier factor.
## (A corrupting slice's PERCENT lives on its APPLY_STATUS effect.)
@export var amount_mode: RC.AmountMode = RC.AmountMode.FLAT
@export var extra_effects: Array[TriggeredEffectData] = []
@export var icon: Texture2D
## Plan 2 N20 rider: separate hits one landing deals (SHIM / OVERFLOW only). Each hit meets
## the target's SANDBOX charge, bodyguard, BLOCK and SHIELD on its own. With
## `hits_per_target_status` set, this is the minimum hit count instead. No cap (ruling Q40).
@export var hits: int = 1
## Plan 2 N20 rider (Genome Core IV): when not NONE, the hit count is the target wheel's
## non-NULL slices carrying this status (one per slice, whatever its stacks) times
## `hits_per_status_slice`, never below `hits`.
@export var hits_per_target_status: RC.Status = RC.Status.NONE
## Hits per slice counted by `hits_per_target_status` (0 = unset; 1 or more when it is set).
@export var hits_per_status_slice: int = 0
## Plan 2 N20 rider (Medicine): output multiplier applied only when the landing is PERFECT.
@export var perfect_multiplier: float = 1.0
## Plan 2 N20 rider (Adrenaline, R13): the hits skip BLOCK and SHIELD, never a SANDBOX
## charge or a bodyguard (ruling Q39).
@export var pierce: bool = false


## The amount_mode problems, each led by a stable code (`mode_unsupported_for_type`,
## `percent_out_of_range`), then the rider problems (`rider_errors`), then those of the
## extra effects.
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if amount_mode == RC.AmountMode.PERCENT:
		if not (slice_type in [RC.SliceType.HOTFIX, RC.SliceType.DEFRAG, RC.SliceType.SANDBOX]):
			errors.append("mode_unsupported_for_type: PERCENT is for HOTFIX, DEFRAG and SANDBOX, not %s." % RC.SliceType.keys()[slice_type])
		if base_output < 0 or base_output > RC.PERCENT_MAX:
			errors.append("percent_out_of_range: PERCENT base_output %d is outside 0..%d." % [base_output, RC.PERCENT_MAX])
	errors.append_array(rider_errors())
	for te in extra_effects:
		if te == null:
			continue
		for e in te.effects:
			if e != null:
				errors.append_array(e.amount_mode_errors())
	return errors


## Whether any N20 rider differs from its default (a default slice resolves as before N20).
func has_riders() -> bool:
	return hits != 1 or hits_per_target_status != RC.Status.NONE or hits_per_status_slice != 0 \
		or perfect_multiplier != 1.0 or pierce


## The N20 rider problems, each led by a stable code: `hits_lt_1`, `hits_per_status_lt_1`
## (a status set with fewer than 1 hit per slice), `hits_per_status_without_status` (a count
## with status NONE), `perfect_multiplier_not_positive`, `riders_on_non_damage` (any rider on
## a slice that is not SHIM or OVERFLOW).
func rider_errors() -> PackedStringArray:
	var errors := PackedStringArray()
	if hits < 1:
		errors.append("hits_lt_1: hits %d must be 1 or more." % hits)
	if hits_per_target_status != RC.Status.NONE and hits_per_status_slice < 1:
		errors.append("hits_per_status_lt_1: hits_per_status_slice %d must be 1 or more with hits_per_target_status %s." % [hits_per_status_slice, RC.Status.keys()[hits_per_target_status]])
	if hits_per_target_status == RC.Status.NONE and hits_per_status_slice != 0:
		errors.append("hits_per_status_without_status: hits_per_status_slice %d needs a hits_per_target_status." % hits_per_status_slice)
	if perfect_multiplier <= 0.0:
		errors.append("perfect_multiplier_not_positive: perfect_multiplier %s must be above 0." % perfect_multiplier)
	if has_riders() and not (slice_type in [RC.SliceType.SHIM, RC.SliceType.OVERFLOW]):
		errors.append("riders_on_non_damage: hit riders are for SHIM and OVERFLOW, not %s." % RC.SliceType.keys()[slice_type])
	return errors
