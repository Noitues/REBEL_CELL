class_name CombatBot
extends RefCounted
## A fair greedy combat player for simulations (balance tooling, gap analysis V4). Each
## turn it adds actions one at a time, keeping the action whose End Turn preview scores
## best (damage dealt minus weighted damage taken), until doing nothing more is best.
## It only uses information a player has: the preview. Cards whose outcome is random
## (Respin, random slice picks, draws that could reshuffle) are never played, so the bot
## never peeks at future rolls. Pure: acts on the session it is given.

const MAX_ACTIONS_PER_TURN := 4
## Damage taken counts this much more than damage dealt.
const TAKEN_WEIGHT := 1.4
## Flat bonus per enemy killed by the resolve.
const KILL_BONUS := 25.0


## Plays one full turn through `act` (a Callable taking a CombatAction and returning a
## CombatResult, e.g. NetrunSession.combat_action) and ends it. Returns actions taken.
static func play_turn(session: CombatSession, act: Callable) -> int:
	var taken := 0
	_retarget(session, act)
	while taken < MAX_ACTIONS_PER_TURN and not session.state.is_over():
		var best: CombatAction = null
		var best_score := _score(session, session.state, CombatResolver.clone_rng(session.rng))
		for a in _candidates(session):
			var r := session.resolver.apply(session.state, a, CombatResolver.clone_rng(session.rng))
			if not r.ok():
				continue
			var sc := _score(session, r.state, CombatResolver.clone_rng(session.rng))
			if sc > best_score + 0.01:
				best_score = sc
				best = a
		if best == null:
			break
		var result: CombatResult = act.call(best)
		if result == null or not result.ok():
			break
		taken += 1
	if not session.state.is_over():
		act.call(CombatAction.end_turn())
	return taken


## Aims at the living non-satellite enemy with the least HP (ties: spawn order).
static func _retarget(session: CombatSession, act: Callable) -> void:
	var best: CombatantState = null
	for e in session.state.living_enemies(false):
		if best == null or e.hp < best.hp:
			best = e
	if best != null and best.id != session.state.target_id:
		act.call(CombatAction.target(best.id))


static func _score(session: CombatSession, state: CombatState, rng: RandomNumberGenerator) -> float:
	var before_enemy := 0
	var alive_before := 0
	for e in state.enemies:
		if e.is_alive() and not e.is_satellite:
			before_enemy += e.hp
			alive_before += 1
	var before_player := state.player.hp
	var s := state.duplicate_state()
	session.resolver.resolve_turn(s, rng, [] as Array[Dictionary])
	var after_enemy := 0
	var alive_after := 0
	for e in s.enemies:
		if e.is_alive() and not e.is_satellite:
			after_enemy += e.hp
			alive_after += 1
	var score := float(before_enemy - after_enemy) - TAKEN_WEIGHT * float(before_player - s.player.hp)
	score += KILL_BONUS * (alive_before - alive_after)
	if s.player.hp <= 0:
		score -= 1000.0
	return score


static func _candidates(session: CombatSession) -> Array[CombatAction]:
	var out: Array[CombatAction] = []
	var s := session.state
	var cfg := session.resolver.config
	var target := s.target_id
	for dir in [1, -1]:
		if s.free_nudges > 0 or s.ram >= cfg.extra_nudge_ram_cost:
			out.append(CombatAction.nudge(&"player", dir))
			if target != &"":
				out.append(CombatAction.nudge(target, dir))
			if s.player.wheel.has_inner_ring():
				out.append(CombatAction.nudge(&"player", dir, RC.RingScope.INNER))
	for i in s.hand.size():
		var card := session.resolver.lookup.get_content(s.hand[i]) as CardData
		if card == null or card.ram_cost > s.ram or _is_random(card):
			continue
		var wheels: Array[StringName] = []
		match card.wheel_target:
			RC.WheelTarget.OWN:
				wheels = [&"player"]
			RC.WheelTarget.ENEMY, RC.WheelTarget.SATELLITE:
				wheels = [target]
			_:
				wheels = [&"player", target]
		var picks := _needs_slot(card)
		for w in wheels:
			if w == &"":
				continue
			for dir in [1, -1]:
				if picks:
					var c := s.get_combatant(w)
					if c == null:
						continue
					for slot in c.wheel.slot_slice_ids.size():
						var a := CombatAction.play_card(i, w, slot)
						a.direction = dir
						out.append(a)
				else:
					var a := CombatAction.play_card(i, w)
					a.direction = dir
					out.append(a)
				if not _uses_direction(card):
					break
	return out


static func _is_random(card: CardData) -> bool:
	for e in card.effects:
		if e != null and (e.type == RC.EffectType.RESPIN or e.type == RC.EffectType.DRAW_CARDS or e.slice_pick == RC.SlicePick.RANDOM_NON_MISS):
			return true
	return false


static func _needs_slot(card: CardData) -> bool:
	for e in card.effects:
		if e != null and e.slice_pick == RC.SlicePick.CHOSEN:
			return true
	return false


static func _uses_direction(card: CardData) -> bool:
	for e in card.effects:
		if e != null and (e.type == RC.EffectType.NUDGE or e.type == RC.EffectType.CUSTOM):
			return true
	return false
