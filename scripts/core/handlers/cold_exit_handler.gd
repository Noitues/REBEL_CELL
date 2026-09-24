extends RefCounted
## Cold Exit (GDD 6.2): finish a netrun without the Miss slice resolving: -3 Heat.
## Run-level hook: `state` is the RunState and the context carries "trigger".


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if int(context.get("trigger", -1)) != RC.Trigger.ON_NETRUN_COMPLETE:
		return []
	if state.miss_resolved:
		return [{"type": "cold_exit_missed", "text": "Cold Exit: the Miss slice resolved this run, no bonus."}]
	return [{"type": "campaign_effect", "effect": RC.EffectType.MODIFY_HEAT, "amount": -3, "source_id": &"cold_exit",
		"text": "Cold Exit: clean run, -3 Heat."}]
