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


## The amount_mode problems, each led by a stable code (`mode_unsupported_for_type`,
## `percent_out_of_range`), then those of the extra effects.
func validate() -> PackedStringArray:
	var errors := PackedStringArray()
	if amount_mode == RC.AmountMode.PERCENT:
		if not (slice_type in [RC.SliceType.HOTFIX, RC.SliceType.DEFRAG, RC.SliceType.SANDBOX]):
			errors.append("mode_unsupported_for_type: PERCENT is for HOTFIX, DEFRAG and SANDBOX, not %s." % RC.SliceType.keys()[slice_type])
		if base_output < 0 or base_output > RC.PERCENT_MAX:
			errors.append("percent_out_of_range: PERCENT base_output %d is outside 0..%d." % [base_output, RC.PERCENT_MAX])
	for te in extra_effects:
		if te == null:
			continue
		for e in te.effects:
			if e != null:
				errors.append_array(e.amount_mode_errors())
	return errors
