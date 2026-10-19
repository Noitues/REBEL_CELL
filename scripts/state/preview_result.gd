class_name PreviewResult
extends RefCounted
## Plan 2 Q19: a forecast of one staged action (a nudge, a respin or a card play): the result
## with every KNOWN part exact and each random part marked unknown instead of rolled. The
## forecast draws nothing from the real RNG and changes no state (CombatResolver.forecast).
## An unknown part is {kind, target, listener}: `target` is the wheel the roll would hit and
## `listener` says it happened inside an enemy listener's reaction (that part only is "?").

## Unknown kinds.
const RESPIN := &"respin"  # a respin's landing: the needle stays where it is
const RANDOM_SLICE := &"random_slice"  # a RANDOM_NON_NULL pick
const RESHUFFLE := &"reshuffle"  # the draw pile runs out and the discard is shuffled in
const UNMODELLED := &"unmodelled"  # a rule drew RNG without marking it (safety net)

## The action's result computed with every random part left undecided.
var result: CombatResult = null
## The unknown parts, in the order they would have rolled.
var unknowns: Array[Dictionary] = []


func ok() -> bool:
	return result != null and result.ok()


func state() -> CombatState:
	return result.state if result != null else null


func events() -> Array[Dictionary]:
	return result.events if result != null else ([] as Array[Dictionary])


## True when any part of the play is random.
func has_unknown() -> bool:
	return not unknowns.is_empty()


## True when a random part of `kind` (any kind when &"") hits wheel `wheel_id` (any wheel when &"").
func is_unknown(kind: StringName = &"", wheel_id: StringName = &"") -> bool:
	for u in unknowns:
		if (kind == &"" or u["kind"] == kind) and (wheel_id == &"" or u["target"] == wheel_id):
			return true
	return false
