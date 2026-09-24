class_name CombatSession
extends RefCounted
## One combat from start to finish: the live state, its RNG, checkpoints and the
## action log (TECH_SPEC 5.4). Pure data + rules; CombatEngine (Node) wraps it.
##
## Checkpoint rule: any action that consumes combat RNG creates a new checkpoint
## after resolving, so actions_since_checkpoint never contain randomness and rewind
## (restore checkpoint, replay all but the last action) is exact.

var resolver: CombatResolver
var combat_seed: int = 0
var rng: RandomNumberGenerator = RandomNumberGenerator.new()
var state: CombatState = null
var checkpoint_state: CombatState = null
var checkpoint_rng_state: int = 0
var actions_since_checkpoint: Array[CombatAction] = []
## Every action applied since the combat started (replay / determinism tests).
var history: Array[CombatAction] = []
## What the combat was built from, by content id, so replay can rebuild it.
var setup: Dictionary = {}
## Events of the last successful apply()/rewind(), for the log.
var last_events: Array[Dictionary] = []


## Starts a combat: builds the state from content ids, seeds the RNG, runs turn 1.
static func start(p_resolver: CombatResolver, class_id: StringName, enemy_ids: Array[StringName], p_seed: int, ring_id: StringName = &"", heat_majors_crossed: int = 0) -> CombatSession:
	var session := CombatSession.new()
	session.resolver = p_resolver
	session.combat_seed = p_seed
	session.rng.seed = p_seed
	session.setup = {"class_id": String(class_id), "enemy_ids": [], "ring_id": String(ring_id), "heat_majors_crossed": heat_majors_crossed}
	for id in enemy_ids:
		session.setup["enemy_ids"].append(String(id))
	var lookup := p_resolver.lookup
	var class_data := lookup.get_content(class_id) as ClassData
	var enemies: Array[EnemyData] = []
	for id in enemy_ids:
		enemies.append(lookup.get_content(id) as EnemyData)
	var ring: InnerRingData = null
	if ring_id != &"":
		ring = _ring_from_class(class_data, ring_id)
	var initial := p_resolver.create_combat(class_data, enemies, session.rng, ring, heat_majors_crossed)
	var result := p_resolver.begin_combat(initial, session.rng)
	session.state = result.state
	session.last_events = result.events
	session._set_checkpoint()
	return session


## Rebuilds a combat from `p_setup`/`p_seed` and replays `actions`. The result's
## state hash must equal the original's (tested).
static func replay(p_resolver: CombatResolver, p_setup: Dictionary, p_seed: int, actions: Array[CombatAction]) -> CombatSession:
	var enemy_ids: Array[StringName] = []
	for id in p_setup.get("enemy_ids", []):
		enemy_ids.append(StringName(String(id)))
	var session := start(p_resolver, StringName(String(p_setup.get("class_id", ""))), enemy_ids, p_seed,
		StringName(String(p_setup.get("ring_id", ""))), int(p_setup.get("heat_majors_crossed", 0)))
	for a in actions:
		session.apply(a)
	return session


## Applies a player action. On success the state advances and the action is logged;
## a refused action leaves everything untouched and reports why.
func apply(action: CombatAction) -> CombatResult:
	var rng_before := rng.state
	var result := resolver.apply(state, action, rng)
	if not result.ok():
		return result
	state = result.state
	history.append(action)
	last_events = result.events
	if rng.state != rng_before:
		_set_checkpoint()
	else:
		actions_since_checkpoint.append(action)
	return result


func can_rewind() -> bool:
	return not actions_since_checkpoint.is_empty() and not state.is_over()


## Undoes the last action: restores the checkpoint and replays the others. Never
## crosses a checkpoint (a random event).
func rewind() -> CombatResult:
	var result := CombatResult.new()
	if not can_rewind():
		result.error = "Nothing to rewind: the last checkpoint is a random event."
		result.state = state
		return result
	var to_replay := actions_since_checkpoint.duplicate()
	to_replay.pop_back()
	history.pop_back()
	state = checkpoint_state.duplicate_state()
	rng.state = checkpoint_rng_state
	actions_since_checkpoint.clear()
	for a in to_replay:
		var r := resolver.apply(state, a, rng)
		state = r.state
		actions_since_checkpoint.append(a)
	result.state = state
	result.events.append({"type": "rewind", "text": "Rewound one action (%d left before the checkpoint)." % actions_since_checkpoint.size()})
	last_events = result.events
	return result


## Preview of `action` without touching the session (TECH_SPEC 5.4).
func preview(action: CombatAction) -> CombatResult:
	return resolver.preview(state, action, rng)


## Preview of End Turn: the resolved state before the next turn's random respins.
func preview_end_turn() -> CombatResult:
	return resolver.preview_end_turn(state, rng)


func state_hash() -> int:
	return state.state_hash()


# --- Save / load -----------------------------------------------------------------

func to_dict() -> Dictionary:
	var since := []
	for a in actions_since_checkpoint:
		since.append(a.to_dict())
	var hist := []
	for a in history:
		hist.append(a.to_dict())
	return {
		"setup": setup.duplicate(true),
		"seed": str(combat_seed),
		"rng_state": str(rng.state),
		"state": state.to_dict(),
		"checkpoint_state": checkpoint_state.to_dict(),
		"checkpoint_rng_state": str(checkpoint_rng_state),
		"actions_since_checkpoint": since,
		"history": hist,
	}


static func from_dict(p_resolver: CombatResolver, d: Dictionary) -> CombatSession:
	var session := CombatSession.new()
	session.resolver = p_resolver
	session.setup = d.get("setup", {}).duplicate(true)
	session.combat_seed = int(String(d.get("seed", "0")))
	session.rng.seed = session.combat_seed
	session.rng.state = int(String(d.get("rng_state", "0")))
	session.state = CombatState.from_dict(d.get("state", {}))
	session.checkpoint_state = CombatState.from_dict(d.get("checkpoint_state", {}))
	session.checkpoint_rng_state = int(String(d.get("checkpoint_rng_state", "0")))
	for ad in d.get("actions_since_checkpoint", []):
		session.actions_since_checkpoint.append(CombatAction.from_dict(ad))
	for ad in d.get("history", []):
		session.history.append(CombatAction.from_dict(ad))
	return session


# --- Internals -------------------------------------------------------------------

func _set_checkpoint() -> void:
	checkpoint_state = state.duplicate_state()
	checkpoint_rng_state = rng.state
	actions_since_checkpoint.clear()


## Finds the Inner Ring `ring_id` names among the class's rank rewards. Rings carry no
## id of their own, so the id is the rank reward's first segment id prefixed "ring:",
## or simply the rank number as "rank:N".
static func _ring_from_class(class_data: ClassData, ring_id: StringName) -> InnerRingData:
	var s := String(ring_id)
	for reward in class_data.rank_rewards:
		if reward == null or reward.inner_ring == null:
			continue
		if s == "rank:%d" % reward.rank:
			return reward.inner_ring
	push_error("CombatSession: class %s has no inner ring '%s'." % [class_data.id, ring_id])
	return null
