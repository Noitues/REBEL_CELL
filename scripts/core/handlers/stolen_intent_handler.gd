extends RefCounted
## Stolen Intent (GDD 6.2): once per combat, swap your resolved slice with the enemy's.
## Activation rule (implementation decision 2026-09-24): it fires automatically the first
## time the operative's first pointer would resolve the Miss slice while the target's
## first pointer resolves something else. Both wheels then resolve the other's slice
## with their own precision tier. The preview shows it because it runs inside RESOLVE.


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if not (state is CombatState) or int(context.get("trigger", -1)) != RC.Trigger.ON_RESOLVE:
		return []
	if int(state.per_combat_uses.get("stolen_intent", 0)) > 0:
		return []
	var target: CombatantState = context.get("target")
	if target == null or not target.is_alive():
		return []
	var resolutions: Array = context.get("resolutions", [])
	var mine: Dictionary = {}
	var theirs: Dictionary = {}
	for r in resolutions:
		if not CombatResolver.is_landing(r) or int(r["pointer_index"]) != 0:
			continue
		if r["owner"] == state.player:
			mine = r
		elif r["owner"] == target:
			theirs = r
	if mine.is_empty() or theirs.is_empty():
		return []
	var my_slice: SliceData = mine["slice"]
	var their_slice: SliceData = theirs["slice"]
	if my_slice.slice_type != RC.SliceType.MISS or their_slice.slice_type == RC.SliceType.MISS:
		return []
	mine["slice"] = their_slice
	theirs["slice"] = my_slice
	mine["firmware"] = null
	theirs["firmware"] = null
	mine["stolen"] = true
	theirs["stolen"] = true
	state.per_combat_uses["stolen_intent"] = 1
	return [{"type": "stolen_intent", "text": "Stolen Intent: you take %s's %s; it gets your Miss." % [target.display_name,
		their_slice.display_name if their_slice.display_name != "" else String(their_slice.id)]}]
