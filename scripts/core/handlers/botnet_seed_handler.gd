extends RefCounted
## Botnet Seed (GDD 6.2): each Perfect deploys a 1-HP drone on the triggered slice
## (max 2 seed drones alive). The drone is the `seed_drone` content entry.

const DRONE_ID := &"seed_drone"
const MAX_SEED_DRONES := 2


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if not (state is CombatState) or int(context.get("trigger", -1)) != RC.Trigger.ON_PERFECT:
		return []
	var owner: CombatantState = context.get("owner")
	if owner != state.player:
		return []
	var fx: EffectInterpreter = context["fx"]
	var template := fx.lookup.get_content(DRONE_ID) as EnemyData
	if template == null:
		return []
	var alive := 0
	for d in state.living_drones():
		if d.source_id == DRONE_ID:
			alive += 1
	if alive >= MAX_SEED_DRONES:
		return [{"type": "drone_cap", "text": "Botnet Seed: already %d seed drones docked." % MAX_SEED_DRONES}]
	var events: Array[Dictionary] = [{"type": "botnet_seed", "text": "Botnet Seed: the Perfect sprouts a drone."}]
	fx.deploy_drone(state, owner, template, int(context.get("slice_index", 0)), events)
	return events
