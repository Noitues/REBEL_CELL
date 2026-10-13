extends RefCounted
## Turn planner for the agent bridge (docs/process/05_CLAUDE_PLAYTESTER.md §11): enumerates
## whole-turn plans (up to MAX_ACTIONS card plays and nudges, cards and nudges in any order) by
## a beam search over the preview, and describes each plan the way a player would read it:
## what is played, the RAM it costs, where each pointer lands (Perfect / Good / Weak, slice),
## and what End Turn would do (damage dealt and taken, kills). Uses only what a player sees: the
## preview; random-outcome cards are left out, as CombatBot does. Pure: works on clones.

const MAX_ACTIONS := 4
const BEAM := 10
const OPTIONS := 6


## Plans for `session`'s current turn, best first: [{actions: Array[CombatAction], text, outcome, score}].
## The first plan is always the beam's best; "end turn now" is always included.
static func plans(session: CombatSession, k: int = OPTIONS) -> Array[Dictionary]:
	var start := {"state": session.state, "actions": [] as Array[CombatAction]}
	var beam: Array[Dictionary] = [start]
	var finals: Array[Dictionary] = [_finish(session, start)]
	for depth in MAX_ACTIONS:
		var next: Array[Dictionary] = []
		for node in beam:
			var probe := CombatSession.new()
			probe.resolver = session.resolver
			probe.state = node["state"]
			probe.rng = session.rng
			for a in CombatBot._candidates(probe):
				var r := session.resolver.apply(node["state"], a, CombatResolver.clone_rng(session.rng))
				if not r.ok():
					continue
				var acts: Array[CombatAction] = (node["actions"] as Array[CombatAction]).duplicate()
				acts.append(a)
				var child := {"state": r.state, "actions": acts}
				child["score"] = CombatBot._score(session, r.state, CombatResolver.clone_rng(session.rng))
				next.append(child)
		if next.is_empty():
			break
		next.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return float(a["score"]) > float(b["score"]))
		beam = next.slice(0, BEAM)
		for node in beam:
			finals.append(_finish(session, node))
	# Distinct outcomes only (two orders of the same cards are one choice), best first.
	finals.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return float(a["score"]) > float(b["score"]) or (float(a["score"]) == float(b["score"]) and (a["actions"] as Array).size() < (b["actions"] as Array).size()))
	var seen := {}
	var out: Array[Dictionary] = []
	var end_now: Dictionary = {}
	for f in finals:
		if (f["actions"] as Array).is_empty():
			end_now = f
		var key := String(f["outcome"]["key"])
		if seen.has(key):
			continue
		seen[key] = true
		if out.size() < k - 1 or (f["actions"] as Array).is_empty():
			out.append(f)
	if not end_now.is_empty() and not out.has(end_now):
		out.append(end_now)
	return out


## Scores and describes the plan that ends with `node`'s state.
static func _finish(session: CombatSession, node: Dictionary) -> Dictionary:
	var state: CombatState = node["state"]
	var before_enemies := {}
	for e in state.enemies:
		before_enemies[e.id] = e.hp
	var before_hp := state.player.hp
	var s := state.duplicate_state()
	var events: Array[Dictionary] = []
	session.resolver.resolve_turn(s, CombatResolver.clone_rng(session.rng), events)
	var dealt := 0
	var kills := 0
	var parts := PackedStringArray()
	for e in s.enemies:
		if e.is_satellite:
			continue
		var was := int(before_enemies.get(e.id, e.hp))
		dealt += was - e.hp
		if was > 0 and e.hp <= 0:
			kills += 1
		parts.append("%s %d->%d" % [e.display_name, was, maxi(e.hp, 0)])
	var taken := before_hp - s.player.hp
	var pointers := PackedStringArray()
	var own_tiers: Array[int] = []
	var enemy_tiers: Array[int] = []
	for ev in events:
		if String(ev.get("type", "")) == "pointer":
			pointers.append(String(ev["text"]).trim_suffix("."))
			if StringName(String(ev.get("owner", ""))) == state.player.id:
				own_tiers.append(int(ev["tier"]))
			else:
				enemy_tiers.append(int(ev["tier"]))
	var acts: Array[CombatAction] = node["actions"]
	var ram := session.state.ram - state.ram
	var outcome := {"dealt": dealt, "taken": taken, "kills": kills, "ram_spent": ram, "player_hp_after": s.player.hp,
		"own_perfect": own_tiers.has(RC.PrecisionTier.PERFECT), "own_tiers": own_tiers, "enemy_tiers": enemy_tiers,
		"enemies": ", ".join(parts), "pointers": pointers, "key": "%d|%d|%d|%d|%s" % [dealt, taken, kills, ram, ";".join(pointers)]}
	var score := float(node.get("score", CombatBot._score(session, state, CombatResolver.clone_rng(session.rng))))
	return {"actions": acts, "score": score, "outcome": outcome,
		"text": "%s. RAM %d. End Turn: you deal %d, take %d%s (%s). Pointers: %s" % [
			describe_actions(session, acts), ram, dealt, taken, (", %d kill(s)" % kills) if kills > 0 else "",
			outcome["enemies"], "; ".join(pointers)]}


## "Jolt on your wheel (+); nudge enemy wheel -1" in player words.
static func describe_actions(session: CombatSession, acts: Array[CombatAction]) -> String:
	if acts.is_empty():
		return "Play nothing, end the turn"
	var s := session.state
	var out := PackedStringArray()
	var hand := s.hand.duplicate()
	for a in acts:
		match a.type:
			CombatAction.Type.PLAY_CARD:
				var card := session.resolver.lookup.get_content(hand[a.hand_index]) as CardData
				var name := card.display_name if card != null else String(hand[a.hand_index])
				var where := "your wheel" if a.wheel_id == &"player" else "enemy wheel"
				var slot := (" slot %d" % (a.slot_index + 1)) if a.slot_index >= 0 else ""
				out.append("%s on %s%s (%s)" % [name, where, slot, "+" if a.direction > 0 else "-"])
				hand.remove_at(a.hand_index)
			CombatAction.Type.NUDGE:
				out.append("nudge %s %s1%s" % ["your wheel" if a.wheel_id == &"player" else "enemy wheel",
					"+" if a.direction > 0 else "-", " (inner ring)" if a.ring == RC.RingScope.INNER else ""])
			_:
				out.append(str(a.type))
	return "; ".join(out)
