extends RefCounted
## Cold Exit (GDD 6.2): finish a netrun without the Miss slice resolving: -amount Heat.
## Run-level hook: `state` is the RunState and the context carries "trigger".


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if int(context.get("trigger", -1)) != RC.Trigger.ON_NETRUN_COMPLETE:
		return []
	if state.miss_resolved:
		return [{"type": "cold_exit_missed", "text": "Cold Exit: the Miss slice resolved this run, no bonus."}]
	var d: DaemonData = context.get("daemon")
	var amount := d.amount if d != null else 0
	return [{"type": "campaign_effect", "effect": RC.EffectType.MODIFY_HEAT, "amount": -amount, "source_id": &"cold_exit",
		"text": "Cold Exit: clean run, -%d Heat." % amount}]
