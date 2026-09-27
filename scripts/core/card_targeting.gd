class_name CardTargeting
extends RefCounted
## Every legal way to play a card (H20 drag-to-target): which wheel it aims at, and for
## nudge cards which ring and which way, and for chosen-slice cards which slice. Pure: the
## combat view turns each option into a drop zone (a wheel, a nudge arrow, a slice), and
## a card with a single option plays on a click. Order is deterministic (wheel order as
## in the state, then ring, direction, slot).

## Chosen-slice effects (GDD 5.x Cleanse, Encrypt, Spawn Drone).
const CHOSEN_SLOT_TYPES := [RC.EffectType.APPLY_STATUS, RC.EffectType.CLEANSE, RC.EffectType.DEPLOY_DRONE]


static func options(resolver: CombatResolver, state: CombatState, hand_index: int) -> Array[CombatAction]:
	var out: Array[CombatAction] = []
	if state == null or hand_index < 0 or hand_index >= state.hand.size():
		return out
	var card := resolver.lookup.get_content(state.hand[hand_index]) as CardData
	if card == null:
		return out
	var directions: Array[int] = [1]
	if uses_direction(card):
		directions.append(-1)
	var ring_choice := chooses_ring(card)
	for w in candidate_wheels(state, card):
		var rings: Array[int] = [-1]
		if ring_choice and w.wheel.has_inner_ring():
			rings = [RC.RingScope.OUTER, RC.RingScope.INNER]
		var slots: Array[int] = [-1]
		var slot_wheel := slot_wheel_of(state, card, w)
		if slot_wheel != null:
			slots.clear()
			for i in slot_wheel.wheel.slice_count:
				slots.append(i)
		for r in rings:
			for d in directions:
				for s in slots:
					var a := CombatAction.play_card(hand_index, w.id, s)
					a.ring = r
					a.direction = d
					if resolver.validate_action(state, a) == "":
						out.append(a)
	return out


## Wheels the card may aim at, before validation.
static func candidate_wheels(state: CombatState, card: CardData) -> Array[CombatantState]:
	var out: Array[CombatantState] = []
	match card.wheel_target:
		RC.WheelTarget.OWN:
			out.append(state.player)
		RC.WheelTarget.ENEMY:
			out.append_array(state.living_enemies(true))
		RC.WheelTarget.SATELLITE:
			for e in state.living_enemies(true):
				if e.is_satellite:
					out.append(e)
		_:
			out.append(state.player)
			out.append_array(state.living_enemies(true))
	return out


static func uses_direction(card: CardData) -> bool:
	for e in card.effects:
		if e != null and e.type == RC.EffectType.NUDGE:
			return true
		if e != null and e.type == RC.EffectType.CUSTOM and _handler_const(e, "USES_DIRECTION", false):
			return true
	return false


## The way a play turns on screen: +1 clockwise. Nudges follow the action's direction; a
## custom handler (Undock) may say its direction reads the other way round on screen.
static func screen_direction(card: CardData, action: CombatAction) -> int:
	for e in card.effects:
		if e != null and e.type == RC.EffectType.CUSTOM and _handler_const(e, "USES_DIRECTION", false):
			return action.direction * int(_handler_const(e, "SCREEN_SIGN", 1))
	return action.direction


static func _handler_const(e: EffectData, name: String, fallback: Variant) -> Variant:
	if e.custom_handler == null:
		return fallback
	var consts := e.custom_handler.get_script_constant_map()
	return consts.get(name, fallback)


## A nudge card whose ring follows the player's choice (not fixed to the inner ring).
static func chooses_ring(card: CardData) -> bool:
	for e in card.effects:
		if e != null and e.type == RC.EffectType.NUDGE and e.ring_scope == RC.RingScope.OUTER:
			return true
	return false


## The wheel whose slices a chosen-slice card picks from when aimed at `aimed` (null when
## the card picks no slice): the operative's own wheel for self effects, else the aimed wheel.
static func slot_wheel_of(state: CombatState, card: CardData, aimed: CombatantState) -> CombatantState:
	for e in card.effects:
		if e != null and e.slice_pick == RC.SlicePick.CHOSEN and e.type in CHOSEN_SLOT_TYPES:
			if e.target in [RC.EffectTarget.SELF, RC.EffectTarget.OWN_WHEEL]:
				return state.player
			return aimed
	return null


## Whether the card has a random effect (Respin, random slice picks): previews show odds.
static func is_random(card: CardData) -> bool:
	for e in card.effects:
		if e != null and (e.type == RC.EffectType.RESPIN or e.slice_pick == RC.SlicePick.RANDOM_NON_MISS):
			return true
	return false


## Whether playing the card may reshuffle the discard pile (a random draw): its draws
## exceed the draw pile.
static func may_reshuffle(state: CombatState, card: CardData) -> bool:
	var draws := 0
	for e in card.effects:
		if e != null and e.type == RC.EffectType.DRAW_CARDS:
			draws += maxi(0, e.amount)
	return draws > state.draw_pile.size() and not state.discard_pile.is_empty()
