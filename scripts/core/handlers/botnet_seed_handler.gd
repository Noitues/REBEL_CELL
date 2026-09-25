extends RefCounted
## Botnet Seed (GDD 6.2): each Perfect deploys a 1-HP drone on the triggered slice
## (at most the Daemon's `amount` seed drones alive). The drone is the `seed_drone` content entry.

const DRONE_ID := &"seed_drone"


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
	var daemon: DaemonData = context.get("daemon")
	var cap := daemon.amount if daemon != null else 0
	var alive := 0
	for d in state.living_drones():
		if d.source_id == DRONE_ID:
			alive += 1
	if alive >= cap:
		return [{"type": "drone_cap", "text": "Botnet Seed: already %d seed drones docked." % cap}]
	var events: Array[Dictionary] = [{"type": "botnet_seed", "text": "Botnet Seed: the Perfect sprouts a drone."}]
	fx.deploy_drone(state, owner, template, int(context.get("slice_index", 0)), events)
	return events
