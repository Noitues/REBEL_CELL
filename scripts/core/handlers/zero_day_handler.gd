extends RefCounted
## Zero Day (GDD 6.2): a Perfect on the Miss slice resolves as an `amount`x Crit against
## the pointer target (that multiple of the wheel's best CRIT output, else its best ATTACK).


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if not (state is CombatState) or int(context.get("trigger", -1)) != RC.Trigger.ON_MISS_SLICE or int(context.get("tier", -1)) != RC.PrecisionTier.PERFECT:
		return []
	var fx: EffectInterpreter = context["fx"]
	var owner: CombatantState = context["owner"]
	var target: CombatantState = context.get("target")
	if target == null or not target.is_alive():
		return []
	var best_crit := 0
	var best_atk := 0
	for i in owner.wheel.slot_slice_ids.size():
		var s := fx.slice_of(owner.wheel, i)
		if s.slice_type == RC.SliceType.CRIT:
			best_crit = maxi(best_crit, s.base_output)
		elif s.slice_type == RC.SliceType.ATTACK:
			best_atk = maxi(best_atk, s.base_output)
	var d: DaemonData = context.get("daemon")
	var mult := d.amount if d != null else 0
	var amount := mult * (best_crit if best_crit > 0 else best_atk)
	var events: Array[Dictionary] = [{"type": "zero_day", "amount": amount, "text": "Zero Day: the Perfect Miss becomes a %dx Crit for %d." % [mult, amount]}]
	for q in target.wheel.pointer_ticks.size():
		var victim: CombatantState = target
		var guard: CombatantState = state.satellite_at(target.id, target.wheel.slice_at(q))
		if guard != null:
			victim = guard
		fx.deal_hit(state, owner, victim, amount, false, true, events, &"zero_day")
	return events
