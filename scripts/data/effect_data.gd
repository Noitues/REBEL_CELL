class_name EffectData
extends Resource
## One atomic effect. Slices, cards, Firmware, ring segments, Hubs, Daemons
## and network nodes all describe what they do as lists of these.

@export var type: RC.EffectType = RC.EffectType.DEAL_DAMAGE
@export var target: RC.EffectTarget = RC.EffectTarget.POINTER_TARGET
## Nudges hit one ring; spins, flips and respins always hit the whole wheel.
@export var ring_scope: RC.RingScope = RC.RingScope.OUTER
@export var amount: int = 0
## FLAT or PERCENT (plan 2 R5). PERCENT only on GAIN_BLOCK, GAIN_SHIELD, HEAL (share of
## the owner's max HP) and APPLY_STATUS CORRUPTED (share of the target's non-NULL slices);
## `amount` is then 0..100.
@export var amount_mode: RC.AmountMode = RC.AmountMode.FLAT
@export var multiplier: float = 1.0
@export var status: RC.Status = RC.Status.NONE
## APPLY_STATUS only (plan 2 N8): the stacks one apply adds to the slot (1 or more, at most
## CampaignConfigData.status_stack_cap; the cap clamps the slot at run time).
@export var stacks: int = 1
## CLEANSE only (N8): ALL stacks of every status on the slot, or ONE_STACK of each.
@export var cleanse_mode: RC.CleanseMode = RC.CleanseMode.ALL
## Slice-level effects only (APPLY_STATUS, CLEANSE): which slice of the target wheel.
@export var slice_pick: RC.SlicePick = RC.SlicePick.UNDER_POINTER
## 0 = instant or permanent.
@export var duration_turns: int = 0
## Only used when type is CUSTOM (rule-breaking behaviour lives in code).
@export var custom_handler: Script
## The Undock keyword (designer 2026-10-18, Q7): satellites and drones are fixed to their slice,
## and only an effect carrying this keyword may move one (its slice or its mini-wheel).
## Any card, class or Firmware effect may carry it.
@export var undock: bool = false


func validate(stack_cap: int = 0) -> PackedStringArray:
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
	errors.append_array(amount_mode_errors())
	errors.append_array(stack_errors(stack_cap))
	return errors


## The N8 stack problems, each led by a stable code: an APPLY_STATUS adding fewer than one
## stack (`stack_amount_lt_1`) or more than `cap` (`stack_amount_gt_cap`, checked when a cap
## is given: the content validator passes CampaignConfigData.status_stack_cap), the retired
## PARASITE (`status_retired`: author OUTPUT_DOWN stacks), or a cleanse_mode outside
## RC.CleanseMode (`cleanse_mode_invalid`).
func stack_errors(cap: int = 0) -> PackedStringArray:
	var errors := PackedStringArray()
	if type == RC.EffectType.APPLY_STATUS:
		if stacks < 1:
			errors.append("stack_amount_lt_1: APPLY_STATUS adds %d stacks; at least 1." % stacks)
		elif cap > 0 and stacks > cap and not (status in RC.UNCAPPED_STATUSES):
			errors.append("stack_amount_gt_cap: APPLY_STATUS adds %d stacks; the cap is %d." % [stacks, cap])
		if status == RC.Status.PARASITE:
			errors.append("status_retired: PARASITE is OUTPUT_DOWN x2 since N8; author OUTPUT_DOWN stacks.")
	if type == RC.EffectType.CLEANSE and not (cleanse_mode in RC.CleanseMode.values()):
		errors.append("cleanse_mode_invalid: cleanse_mode %d is not an RC.CleanseMode." % cleanse_mode)
	return errors


## The amount_mode problems alone, each led by a stable code: PERCENT on a type that has
## no percent reading (`mode_unsupported_for_type`), or outside 0..100 (`percent_out_of_range`).
func amount_mode_errors() -> PackedStringArray:
	var errors := PackedStringArray()
	if amount_mode != RC.AmountMode.PERCENT:
		return errors
	var percent_types := [RC.EffectType.GAIN_BLOCK, RC.EffectType.GAIN_SHIELD, RC.EffectType.HEAL]
	if not (type in percent_types or (type == RC.EffectType.APPLY_STATUS and status == RC.Status.CORRUPTED)):
		errors.append("mode_unsupported_for_type: PERCENT is for heal, block, shield and CORRUPTED, not %s." % RC.EffectType.keys()[type])
	if amount < 0 or amount > RC.PERCENT_MAX:
		errors.append("percent_out_of_range: PERCENT amount %d is outside 0..%d." % [amount, RC.PERCENT_MAX])
	return errors
