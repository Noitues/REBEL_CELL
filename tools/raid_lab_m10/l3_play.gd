class_name L3Play
extends RefCounted
## The hands-off playout of one sweep as a small state machine. It only sequences the beats and logs which node each
## beam touched; every decision (touch, status change, hunter column) comes from L3Rules.resolve. Beats: beam 1, the
## known extra beams Heat brought, beam 2 unseals, the spoof decision (a click on the lit line, or hold; skipped when
## the kit has no spoof), beam 2, the hunter turns on the column of the first touch, the hunter beam, the end.
## A touch that empties HOME ends the sweep at once (`cut`): the campaign is lost, so no spoof decision follows it.
## Time: advance(dt). dt is already scaled by the speed control.

enum S { BEAM, UNSEAL, DECIDE, TURN, END, DONE }

var leg: Dictionary
var raid_i: int
var before: L3State
var alloc: Dictionary
var b2: Array
var spoof: Vector2i = L3Rules.NONE
var spoof_used: bool = false
## True when the kit holds a spoof, so the decision after the reveal is offered.
var can_spoof: bool = false
## True when the sweep was cut short by the breach.
var cut: bool = false
var state: int = S.BEAM
var t: float = 0.0
var clock: float = 0.0
## The Heat the sweep runs at (after the ghost's +5).
var run_heat: int = 0
## The resolution that is the real result (with the spoof once chosen).
var res: Dictionary = {}
var order: Array = []
var bi: int = 0
## Revealed steps in order: {beam, cell, kind, outcome ("" for steps that are no touch), at}.
var events: Array = []
var _next_step: int = 0
var _touch_i: int = 0
var _outcomes: Array = []
var _home_hp: int = 0


func _init(p_leg: Dictionary, p_raid_i: int, p_before: L3State, p_alloc: Dictionary, p_b2: Array) -> void:
	leg = p_leg
	raid_i = p_raid_i
	before = p_before
	alloc = p_alloc
	b2 = p_b2
	can_spoof = int(before.kit["spoof"]) > 0
	_home_hp = before.home_hp
	run_heat = before.heat + L3Config.GHOST_HEAT * (alloc["ghost"] as Array).size()
	_resolve()
	for b: Dictionary in res["beams"]:
		order.append(b["id"])


func _resolve() -> void:
	res = L3Rules.resolve(leg, raid_i, before, b2, alloc, spoof)
	_outcomes = L3Rules.outcomes(before, res["touches"])


func beam_steps(k: int) -> Array:
	return res["beams"][k]["steps"]


## The id of the beam being drawn ("b1", "extra", "extra2", "b2", "hunter"), or "" outside the beams.
func beam_id() -> String:
	if state == S.BEAM:
		return order[bi]
	if state in [S.UNSEAL, S.DECIDE]:
		return "b2"
	if state == S.TURN:
		return "hunter"
	return ""


## The index into res["beams"] of the beam in play, or -1.
func beam_idx() -> int:
	var id := beam_id()
	return order.find(id) if id != "" else -1


## Head position along the current beam in cells: 0 = just before the first node, i + 1 = at node i.
func head() -> float:
	if state != S.BEAM:
		return 0.0
	return minf(t / L3Config.STEP_T, float((beam_steps(bi)).size()))


func is_waiting() -> bool:
	return state == S.DECIDE


func is_done() -> bool:
	return state == S.DONE


## True if the node may be a spoof target (it lies on the revealed sealed line).
func can_target(c: Vector2i) -> bool:
	return state == S.DECIDE and b2.has(c)


## Decision: beam 2 skips this node (spends one spoof).
func choose_spoof(c: Vector2i) -> bool:
	if not can_target(c):
		return false
	spoof = c
	spoof_used = true
	_resolve()
	_enter_beam(order.find("b2"))
	return true


## Decision: hold the spoof.
func pass_spoof() -> bool:
	if state != S.DECIDE:
		return false
	_enter_beam(order.find("b2"))
	return true


func _enter_beam(i: int) -> void:
	state = S.BEAM
	bi = i
	t = 0.0
	_next_step = 0


func _after_beam() -> void:
	var nxt: int = bi + 1
	if nxt >= order.size():
		state = S.END
		t = 0.0
	elif order[nxt] == "b2":
		state = S.UNSEAL
		t = 0.0
		bi = nxt
	elif order[nxt] == "hunter":
		state = S.TURN
		t = 0.0
		bi = nxt
	else:
		_enter_beam(nxt)


func _log(step: Dictionary, id: String) -> void:
	var outcome := ""
	if step["kind"] in ["asset", "home", "decoy"]:
		outcome = String(_outcomes[_touch_i]["outcome"])
		_touch_i += 1
	events.append({"beam": id, "cell": step["cell"], "kind": step["kind"], "outcome": outcome, "at": clock})
	if outcome == "HOME":
		_home_hp -= 1
		if _home_hp <= 0:
			cut = true
			state = S.END
			t = 0.0


func _beam_len(k: int) -> float:
	return float(beam_steps(k).size()) * L3Config.STEP_T + 0.35


func advance(dt: float) -> void:
	if state == S.DONE:
		return
	clock += dt
	t += dt
	match state:
		S.BEAM:
			var steps: Array = beam_steps(bi)
			while _next_step < steps.size() and t >= (_next_step + 1) * L3Config.STEP_T:
				_log(steps[_next_step], order[bi])
				_next_step += 1
				if cut:
					return
			if t >= _beam_len(bi):
				_after_beam()
		S.UNSEAL:
			if t >= L3Config.UNSEAL_T:
				if can_spoof:
					state = S.DECIDE
					t = 0.0
				else:
					_enter_beam(order.find("b2"))
		S.TURN:
			if t >= L3Config.TURN_T:
				_enter_beam(bi)
		S.END:
			if t >= L3Config.END_T:
				state = S.DONE


## SKIP: run to the end. Stops at the spoof decision (it needs the player).
func skip() -> void:
	var guard := 0
	while state != S.DONE and state != S.DECIDE and guard < 4000:
		advance(0.05)
		guard += 1


## The network as the sweep has left it so far: {status (cell -> String), home_hp}.
func status_now() -> Dictionary:
	var s: Dictionary = before.status.duplicate()
	var hp: int = before.home_hp
	for e: Dictionary in events:
		if e["outcome"] == "DOWN" or e["outcome"] == "TAKEN":
			s[e["cell"]] = e["outcome"]
		elif e["outcome"] == "HOME":
			hp -= 1
	return {"status": s, "home_hp": hp}


## What beam 2 would do if it skipped this node: the resolution with that spoof (NONE = hold).
func preview(c: Vector2i) -> Dictionary:
	return L3Rules.resolve(leg, raid_i, before, b2, alloc, c)


## The touches the sweep revealed, as the rules' touch list prefix (all of them unless the sweep was cut).
func shown_touches() -> Array:
	var all: Array = res["touches"]
	var n := 0
	for e: Dictionary in events:
		if e["outcome"] != "":
			n += 1
	return all.slice(0, n)


## The touched cells logged beat by beat (checked against the result in flow_check).
func logged_touches() -> Array:
	var out: Array = []
	for e: Dictionary in events:
		if e["outcome"] != "":
			out.append([e["cell"].x, e["cell"].y, e["kind"]])
	return out


## The cell of the first touch the hunter turns on, or NONE.
func hunter_from() -> Vector2i:
	return res["first"]


## Index of the last beam the sweep entered (a cut sweep stops there).
func last_beam() -> int:
	if state in [S.BEAM, S.UNSEAL, S.DECIDE, S.TURN]:
		return beam_idx()
	return bi
