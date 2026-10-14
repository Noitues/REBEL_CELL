class_name RealChips
extends RefCounted
## The chips the real play gives, built the way the combat scene builds them (W2-A2): the spin
## is what the play turned (`landing` = the state right after it, before SEND IT) and NULL says a
## needle lands on NULL there. Tests hold the previewed chips to this.

## `landing` null = no play before SEND IT (the state itself).
static func build(resolver: CombatResolver, before: CombatState, landing: CombatState, after: CombatState,
		events: Array[Dictionary], id: StringName, random_status: int, heat: int) -> Array[Dictionary]:
	var land := landing if landing != null else before
	var lc := land.get_combatant(id)
	var null_hit := false
	if lc != null:
		for rd in resolver.pointer_readouts(land, lc):
			if (rd["slice"] as SliceData).slice_type == RC.SliceType.NULL:
				null_hit = true
	return ResultChipModel.build(before, after, events, id, random_status, heat, land, null_hit)
