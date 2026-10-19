class_name RamCost
extends RefCounted
## What an action costs in RAM (plan 2 N9, rulings Q36 / Q37). One pure function shared by the
## resolver (validate and apply) and the preview / forecast chip, so forecast == result.
##
## Q36: while a needle of the operative's wheel touches a CORRUPTED slice, every RAM cost is
## multiplied by CampaignConfigData.corrupted_ram_cost_multiplier, once per action however
## many needles touch one; a cost of 0 stays 0 (the free nudge stays free); no cap.
## Q37: manipulating an enemy wheel whose needle touches a CORRUPTED slice costs the divisor
## less (halved, rounded up, so a paid action never drops to 0). Both: x2, then ceil(/2).


## Whether any needle of `c`'s wheel reads a slice that carries CORRUPTED.
static func touches_corrupted(c: CombatantState) -> bool:
	if c == null or c.wheel == null:
		return false
	for i in c.wheel.pointer_ticks.size():
		var slot := WheelMath.slice_at(c.wheel.tick_at(i), c.wheel.slice_count)
		if slot >= 0 and slot < c.wheel.slice_stacks.size() and c.wheel.stacks_of(slot, RC.Status.CORRUPTED) > 0:
			return true
	return false


## `base` RAM after the Q36 multiplier and the Q37 halving. `manipulated` is the wheel an
## enemy-wheel manipulation acts on (null for none or the operative's own wheel).
static func adjusted(base: int, state: CombatState, manipulated: CombatantState, cfg: CampaignConfigData) -> int:
	if base <= 0:
		return 0
	var cost := base
	if touches_corrupted(state.player):
		cost *= maxi(1, cfg.corrupted_ram_cost_multiplier)
	if manipulated != null and not manipulated.is_player and touches_corrupted(manipulated):
		var d := maxi(1, cfg.corrupted_enemy_ram_divisor)
		cost = int(ceil(float(cost) / float(d)))
	return cost


## The RAM `action` costs in `state` (0 for actions that cost none, or a free nudge).
static func of_action(state: CombatState, action: CombatAction, resolver: CombatResolver) -> int:
	var cfg := resolver.config
	match action.type:
		CombatAction.Type.RESPIN:
			return adjusted(cfg.respin_ram_cost, state, null, cfg)
		CombatAction.Type.NUDGE:
			if state.free_nudges > 0:
				return 0
			return adjusted(cfg.extra_nudge_ram_cost, state, state.get_combatant(action.wheel_id), cfg)
		CombatAction.Type.PLAY_CARD:
			if action.hand_index < 0 or action.hand_index >= state.hand.size():
				return 0
			var card := resolver.lookup.get_content(state.hand[action.hand_index]) as CardData
			if card == null:
				return 0
			var target := resolver.card_target(state, card, action)
			var manipulated: CombatantState = target if _manipulates(state, card, target) else null
			return adjusted(card.ram_cost, state, manipulated, cfg)
	return 0


static func _manipulates(state: CombatState, card: CardData, target: CombatantState) -> bool:
	if target == null or target.is_player:
		return false
	for e in card.effects:
		if e != null and e.type in CombatResolver.SATELLITE_MOVING_EFFECTS and e.target not in [RC.EffectTarget.SELF, RC.EffectTarget.OWN_WHEEL, RC.EffectTarget.CAMPAIGN]:
			return true
	return false
