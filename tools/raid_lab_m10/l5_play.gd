class_name L5Play
extends RefCounted
## The hands-off playout of one sweep as a small state machine. It only sequences the beats and logs which node each
## beam touched; every decision (touch, status change, hunter column) comes from L5Rules.resolve. Beats: beam 1, the
## known extra beams Heat brought, beam 2 unseals, the response after the reveal (HOLD, SKIP one node of the lit line, or
## JAM the hunter; when the kit holds no spoof a "no spoof left" beat shows instead), beam 2, the hunter turns on the
## column of the first touch (not when jammed), the hunter beam, the end.
## A touch that empties HOME ends the sweep at once (`cut`): the campaign is lost, so no decision follows it.
## Time: advance(dt). dt is already scaled by the speed control.

enum S { BEAM, UNSEAL, DECIDE, NOTE, TURN, END, DONE }

var leg: Dictionary
var raid_i: int
var before: L5State
var alloc: Dictionary
var b2: Array
## NONE (hold), a cell of the lit line (SKIP) or L5Rules.JAM once the player has chosen.
var spoof: Vector2i = L5Rules.NONE
var spoof_used: bool = false
## Fast mode (a settled breach): one short beat per beam, every step of a beam shown at once, no decision and no
## "no spoof left" beat; the response is always HOLD. The rules' result is the same as in the slow playout.
var fast: bool = false
const FAST_BEAT := L7Config.FAST_BEAT
const FAST_UNSEAL := L7Config.FAST_UNSEAL
const FAST_TURN := L7Config.FAST_TURN
const FAST_END := L7Config.FAST_END
## True when the kit holds a spoof, so the decision after the reveal is offered.
var can_spoof: bool = false
## True when the sweep was cut short by the breach.
var cut: bool = false
var state: int = S.BEAM
var t: float = 0.0
var clock: float = 0.0
## The Heat the sweep runs at (after the ghost's +5).
var run_heat: int = 0
## The resolution that is the real result (with the response once chosen).
var res: Dictionary = {}
## The resolution if the player holds: what the hunter would do, whatever is chosen.
var hold_res: Dictionary = {}
var order: Array = []
var bi: int = 0
## Revealed steps in order: {beam, cell, kind, outcome ("" for steps that are no touch), at}.
var events: Array = []
var _next_step: int = 0
var _touch_i: int = 0
var _outcomes: Array = []
var _home_hp: int = 0


func _init(p_leg: Dictionary, p_raid_i: int, p_before: L5State, p_alloc: Dictionary, p_b2: Array) -> void:
	leg = p_leg
	raid_i = p_raid_i
	before = p_before
	alloc = p_alloc
	b2 = p_b2
	can_spoof = int(before.kit["spoof"]) > 0
	_home_hp = before.home_hp
	run_heat = before.heat + L5Config.GHOST_HEAT * (alloc["ghost"] as Array).size()
	_resolve()
	hold_res = res
	_rebuild_order()


func _resolve() -> void:
	res = L5Rules.resolve(leg, raid_i, before, b2, alloc, spoof)
	_outcomes = L5Rules.outcomes(before, res["touches"])


func _rebuild_order() -> void:
	order = []
	for b: Dictionary in res["beams"]:
		order.append(b["id"])


func beam_steps(k: int) -> Array:
	return res["beams"][k]["steps"]


## The id of the beam being drawn ("b1", "extra", "extra2", "b2", "hunter"), or "" outside the beams.
func beam_id() -> String:
	if state == S.BEAM:
		return order[bi]
	if state in [S.UNSEAL, S.DECIDE, S.NOTE]:
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
	if fast:
		return float(beam_steps(bi).size())
	return minf(maxf(0.0, t - lead_of(order[bi])) / L7Config.STEP_T, float((beam_steps(bi)).size()))


## How long beam `id` glows at its start before its head moves: the lit real line holds before it fires, the hunter leads
## shorter. Fast mode has none.
func lead_of(id: String) -> float:
	if fast:
		return 0.0
	match id:
		"b2":
			return L7Config.FIRE_HOLD
		"hunter":
			return L7Config.HUNTER_LEAD
	return L7Config.BEAM_LEAD


func is_waiting() -> bool:
	return state == S.DECIDE


func is_done() -> bool:
	return state == S.DONE


## True if the node may be a SKIP target (it lies on the revealed sealed line).
func can_target(c: Vector2i) -> bool:
	return state == S.DECIDE and b2.has(c)


## Decision: beam 2 skips this node (spends one spoof, +SPOOF_HEAT Heat after the sweep).
func choose_spoof(c: Vector2i) -> bool:
	if not can_target(c):
		return false
	spoof = c
	spoof_used = true
	_resolve()
	_rebuild_order()
	_enter_beam(order.find("b2"))
	return true


## Decision: JAM, the hunter does not run this raid (spends one spoof, +SPOOF_HEAT Heat after the sweep).
func choose_jam() -> bool:
	if state != S.DECIDE:
		return false
	spoof = L5Rules.JAM
	spoof_used = true
	_resolve()
	_rebuild_order()
	_enter_beam(order.find("b2"))
	return true


## Decision: hold the spoof.
func pass_spoof() -> bool:
	if state != S.DECIDE:
		return false
	_enter_beam(order.find("b2"))
	return true


## The options of the decision screen, hold first, then a SKIP per node of the lit line, then JAM. Each is
## {cell (NONE = hold, JAM), kind ("hold" / "skip" / "jam"), res, summary, heat_run, heat_after, spoof_heat, up (Heat lines
## crossed upwards), down (lines crossed downwards)}. Every figure is the rules' own resolution of that choice.
func options() -> Array:
	var out: Array = []
	for c: Vector2i in L5Rules.responses(before, b2):
		var pr := L5Rules.resolve(leg, raid_i, before, b2, alloc, c)
		var ns: L5State = pr["state"]
		var up: Array = []
		var down: Array = []
		for line: int in [L5Config.EXTRA_AT, L5Config.STRONG_AT]:
			if run_heat < line and ns.heat >= line:
				up.append(line)
			elif run_heat >= line and ns.heat < line:
				down.append(line)
		out.append({"cell": c, "kind": "hold" if c == L5Rules.NONE else ("jam" if c == L5Rules.JAM else "skip"), "res": pr,
			"summary": L5Rules.summary(before, pr["touches"]), "heat_run": run_heat, "heat_after": ns.heat,
			"spoof_heat": 0 if c == L5Rules.NONE else L5Config.SPOOF_HEAT, "up": up, "down": down})
	return out


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
	return lead_of(order[k]) + float(beam_steps(k).size()) * L7Config.STEP_T + L7Config.BEAM_TAIL


func advance(dt: float) -> void:
	if state == S.DONE:
		return
	clock += dt
	t += dt
	match state:
		S.BEAM:
			var steps: Array = beam_steps(bi)
			while _next_step < steps.size() and (fast or t - lead_of(order[bi]) >= (_next_step + 1) * L7Config.STEP_T):
				_log(steps[_next_step], order[bi])
				_next_step += 1
				if cut:
					return
			if t >= (FAST_BEAT if fast else _beam_len(bi)):
				_after_beam()
		S.UNSEAL:
			if fast:
				if t >= FAST_UNSEAL:
					_enter_beam(order.find("b2"))
			elif t >= L7Config.UNSEAL_T:
				if can_spoof:
					state = S.DECIDE
					t = 0.0
				else:
					state = S.NOTE
					t = 0.0
		S.NOTE:
			if t >= L7Config.NOTE_T:
				_enter_beam(order.find("b2"))
		S.TURN:
			if t >= (FAST_TURN if fast else L7Config.TURN_T):
				_enter_beam(bi)
		S.END:
			if t >= (FAST_END if fast else L7Config.END_T):
				state = S.DONE


## SKIP: run to the end. Stops at the decision (it needs the player).
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


## What the sweep would do after this response: the resolution with that spoof (NONE = hold, JAM = jam).
func preview(c: Vector2i) -> Dictionary:
	return L5Rules.resolve(leg, raid_i, before, b2, alloc, c)


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


## The cell of the first touch the hunter turns on, or NONE (JAM does not change it: the hunter just does not run).
func hunter_from() -> Vector2i:
	return res["first"]


## True when the hunter runs this raid (it does not after a JAM).
func hunter_runs() -> bool:
	return spoof != L5Rules.JAM


## The hunter beam of the hold resolution ({id, line, steps, stopped}): the turn the hunter would take.
func hunter_beam() -> Dictionary:
	for b: Dictionary in hold_res["beams"]:
		if b["id"] == "hunter":
			return b
	return {}


## Index of the last beam the sweep entered (a cut sweep stops there).
func last_beam() -> int:
	if state in [S.BEAM, S.UNSEAL, S.DECIDE, S.NOTE, S.TURN]:
		return beam_idx()
	return bi
