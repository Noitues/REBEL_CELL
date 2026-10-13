class_name TurnQueue
extends RefCounted
## W2-A2 (V1 gaps 2 and 5): what has been played this turn and the running net, so a chain of
## plays reads as one plan ("JOLT, NUDGE, ... YOU 60→49, RAM 9→5"). View-side and pure: it keeps
## the state each action left (a copy per action, from the turn's start) and reads the numbers
## off those states and off the forecast the scene hands it (the End Turn resolve), never from
## a rule of its own. `rows()` is what the panel draws; tests hold it to the resolver.

## One recorded action: {label, ram (change: negative = spent), free (a free nudge used)}.
const KEY_LABEL := "label"
const KEY_RAM := "ram"
const KEY_FREE := "free"

## History size at the turn's start, and the state per history size ({"state", "label"}).
var _base_n: int = -1
var _turn_start: int = -1
var _snaps: Dictionary = {}
var _session_id: int = 0


## Forgets everything (a new fight).
func reset() -> void:
	_base_n = -1
	_turn_start = -1
	_snaps = {}
	_session_id = 0


## Brings the queue up to `history` (the session's actions, in order) with `state` the state they
## left. `label_of(prev_state, action)` names an action for the list. Safe to call after every
## state change: a new turn starts it over, a rewind drops the undone steps.
func sync(session_id: int, history: Array, state: CombatState, label_of: Callable) -> void:
	var n := history.size()
	var turn_start := 0
	for i in range(n - 1, -1, -1):
		if (history[i] as CombatAction).type == CombatAction.Type.END_TURN:
			turn_start = i + 1
			break
	if session_id != _session_id or _turn_start != turn_start or not _snaps.has(_base_n):
		_session_id = session_id
		_turn_start = turn_start
		_base_n = n  # a new turn starts here; joined mid-turn (a load), the queue starts from here
		_snaps = {_base_n: {"state": state.duplicate_state(), "label": ""}}
		return
	for k in _snaps.keys():
		if int(k) > n:
			_snaps.erase(k)
	if n > _base_n and not _snaps.has(n):
		var prev: Dictionary = _snaps.get(n - 1, {})
		var label := String(label_of.call(prev["state"], history[n - 1])) if not prev.is_empty() and label_of.is_valid() else ""
		_snaps[n] = {"state": state.duplicate_state(), "label": label, "action": history[n - 1]}


## The steps played so far this turn, oldest first (a TARGET change is no step).
func steps() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for k in range(_base_n + 1, _base_n + _snaps.size()):
		if not _snaps.has(k) or not _snaps.has(k - 1):
			continue
		var snap: Dictionary = _snaps[k]
		var action: CombatAction = snap.get("action")
		if action != null and action.type == CombatAction.Type.TARGET:
			continue
		out.append(step_between(_snaps[k - 1]["state"], _snaps[k]["state"], String(snap.get("label", ""))))
	return out


## The state the turn started in (null before the first sync).
func base_state() -> CombatState:
	return _snaps[_base_n]["state"] if _snaps.has(_base_n) else null


## One action as the list says it: its label, the RAM it changed and whether it used a free nudge.
static func step_between(prev: CombatState, next: CombatState, label: String) -> Dictionary:
	return {KEY_LABEL: label, KEY_RAM: next.ram - prev.ram, KEY_FREE: maxi(0, prev.free_nudges - next.free_nudges) > 0}


## The RAM the played steps (and `pending`, a step as `step_between` makes it, {} = none) spent in
## all: a positive number.
static func ram_spent(played: Array[Dictionary], pending: Dictionary = {}) -> int:
	var spent := 0
	for st in played:
		spent -= mini(0, int(st[KEY_RAM]))
	if not pending.is_empty():
		spent -= mini(0, int(pending[KEY_RAM]))
	return spent


## The net of the plan: per wheel (the operative first, then each enemy in order, satellites
## after their host) its HP at the turn's start and after `projected` (the End Turn resolve of
## the plan). [{id, before, after, is_player}]; a wheel gone before the turn started is left out.
static func net(base: CombatState, projected: CombatState) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if base == null or projected == null:
		return out
	for b in base.combatants_in_order():
		if not b.is_alive():
			continue
		var a := projected.get_combatant(b.id)
		out.append({"id": b.id, "before": b.hp, "after": maxi(0, a.hp) if a != null else 0, "is_player": b.is_player,
			"is_satellite": b.is_satellite})
	return out
