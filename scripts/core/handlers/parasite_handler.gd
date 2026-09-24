extends RefCounted
## Swarm Core Perfect hook (GDD 5.2 Botnet): a Perfect on a DEPLOY slice docks a Parasite
## on the target's slice under the matching pointer (Status.PARASITE: half output until
## cleansed). Other Perfects do nothing extra.


func handle(context: Dictionary, state, _rng: RandomNumberGenerator) -> Array[Dictionary]:
	if not (state is CombatState):
		return []
	var fx: EffectInterpreter = context["fx"]
	var owner: CombatantState = context.get("owner")
	var target: CombatantState = context.get("target")
	if owner == null or target == null or not target.is_alive():
		return []
	var slot := int(context.get("slice_index", -1))
	if slot < 0 or fx.slice_of(owner.wheel, slot).slice_type != RC.SliceType.DEPLOY:
		return []
	var pointer := clampi(int(context.get("pointer_index", 0)), 0, target.wheel.pointer_ticks.size() - 1)
	var victim_slot := target.wheel.slice_at(pointer)
	var events: Array[Dictionary] = [{"type": "parasite", "target": target.id, "slot": victim_slot,
		"text": "Perfect Deploy: a parasite drone latches onto %s slot %d." % [target.display_name, victim_slot]}]
	fx.apply_status(target, victim_slot, RC.Status.PARASITE, events)
	return events
