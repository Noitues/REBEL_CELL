class_name SimMetrics
extends RefCounted
## N19: per-fight, per-phase metrics for the balance sim. OBSERVATIONAL ONLY: it reads the events a
## CombatResult already carries (and one number from the state), never touches a CombatState, never draws
## from an RNG stream. Schema: docs/handoff/N19_METRICS_SCHEMA.md.

const PATHS: Array[String] = ["hit", "self", "parasite", "pierce"]

var _player_id: StringName
var _listeners_supported: bool
var _phases: Array[Dictionary] = []
var _phase_idx: int = 0
var _own_this_turn: bool = false
var _enemy_this_turn: bool = false
var _heal_this_turn: bool = false
var _enrage_max: int = 0
var _fires: Dictionary = {}
var _turn_kinds: Dictionary = {"own": 0, "enemy": 0, "both": 0, "none": 0}


## `player_id`: the player's combatant id. `listeners_supported`: false while N6 is absent (fires report null).
func _init(player_id: StringName, listeners_supported: bool = false) -> void:
	_player_id = player_id
	_listeners_supported = listeners_supported


## An empty phase record.
static func new_phase() -> Dictionary:
	var by_path := {}
	for p in PATHS:
		by_path[p] = 0
	return {"turns": 0, "parked": 0, "parked_by_path": by_path, "intake": 0, "heal_turns": 0,
		"resistance_absorbed": 0, "incomplete": false}


func _bucket(idx: int) -> Dictionary:
	while _phases.size() <= idx:
		_phases.append(new_phase())
	return _phases[idx]


## One accepted combat action: `events` of its result, `enrage_step` the highest step among the enemies after it.
## The End Turn call counts the turn in the phase it began in; a `boss_phase` event moves later events on.
func observe(is_end_turn: bool, events: Array, enrage_step: int = 0) -> void:
	var start_idx := _phase_idx
	var b := _bucket(_phase_idx)
	var advance := false
	for ev in events:
		var e: Dictionary = ev
		var kind := String(e.get("type", ""))
		var target := StringName(String(e.get("target", "")))
		match kind:
			"damage":
				if target == _player_id:
					if not bool(e.get("sandboxed", false)):
						b["intake"] = int(b["intake"]) + int(e.get("hp_damage", 0))
				else:
					var path := "pierce" if bool(e.get("pierce", false)) else ("self" if StringName(String(e.get("attacker", ""))) == target else "hit")
					_park(b, path, int(e.get("parked", 0)))
			"corrupted":
				if target != _player_id:
					_park(b, "self", int(e.get("parked", 0)))
			"parasite":
				if target != _player_id:
					_park(b, "parasite", int(e.get("parked", 0)))
			"heal":
				if target != _player_id and int(e.get("amount", 0)) > 0:
					_heal_this_turn = true
			"nudge_absorbed":
				if target != _player_id:
					b["resistance_absorbed"] = int(b["resistance_absorbed"]) + 1
					_mark(is_end_turn, false)
			"spin":
				if target != _player_id:
					b["resistance_absorbed"] = int(b["resistance_absorbed"]) + int(e.get("absorbed", 0))
				_mark(is_end_turn, target == _player_id)
			"nudge", "flip":
				_mark(is_end_turn, target == _player_id)
			"boss_phase":
				advance = true
			"listener_fire":
				if _listeners_supported:
					var id := String(e.get("listener", e.get("source_id", "")))
					_fires[id] = int(_fires.get(id, 0)) + 1
	_enrage_max = maxi(_enrage_max, enrage_step)
	if is_end_turn:
		_end_turn(_bucket(start_idx))
	if advance:
		_phase_idx += 1


func _mark(is_end_turn: bool, own: bool) -> void:
	if is_end_turn:
		return  # the End Turn resolve is the enemy acting; only the player's own actions count
	if own:
		_own_this_turn = true
	else:
		_enemy_this_turn = true


func _park(b: Dictionary, path: String, amount: int) -> void:
	if amount <= 0:
		return
	b["parked"] = int(b["parked"]) + amount
	var bp: Dictionary = b["parked_by_path"]
	bp[path] = int(bp[path]) + amount


func _end_turn(b: Dictionary) -> void:
	b["turns"] = int(b["turns"]) + 1
	if _heal_this_turn:
		b["heal_turns"] = int(b["heal_turns"]) + 1
	var key := "both" if _own_this_turn and _enemy_this_turn else ("own" if _own_this_turn else ("enemy" if _enemy_this_turn else "none"))
	_turn_kinds[key] = int(_turn_kinds[key]) + 1
	_own_this_turn = false
	_enemy_this_turn = false
	_heal_this_turn = false


## A card ended the fight mid-turn: that turn counts (as the probe's turn count does).
func finish_mid_turn() -> void:
	_end_turn(_bucket(_phase_idx))


## The fight's metrics. `won` false (death, stuck) flags the last phase incomplete. Empty phases drop.
func to_dict(won: bool) -> Dictionary:
	var phases: Array = []
	for p in _phases:
		if int(p["turns"]) > 0:
			phases.append(p.duplicate(true))
	if not phases.is_empty() and not won:
		phases[phases.size() - 1]["incomplete"] = true
	return {"phases": phases, "enrage_step": _enrage_max, "listener_fires": _fires.duplicate() if _listeners_supported else null,
		"turn_manipulation": _turn_kinds.duplicate()}
