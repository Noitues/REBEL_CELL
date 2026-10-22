class_name M10Play
extends RefCounted
## The hands-off playout of one sweep as a small state machine. It only sequences the beats and logs which node each
## beam touched; every found/skipped decision comes from M10Rules.sweep. Beats: beam 1, beam 2 unseals, the spoof
## decision (SPOOF_MODE "choice": click a node; "press": click the target, then SPACE inside a timing window as the
## beam crosses it), beam 2, the hunter turns, beam 3.
## Time: advance(dt, dt_real). dt is scaled by the speed control; the press window runs on dt_real so it is fair at any speed.

enum S { B1, UNSEAL, DECIDE, B2, PRESS, HUNTER, B3, END, DONE }

var assets: Dictionary
var b1: Array
var cands: Array
var reveal: int
var own3: Array
var plan: Dictionary
var mode: String
var state: int = S.B1
var t: float = 0.0
var clock: float = 0.0
## Touched nodes in order: {beam (0..2), cell, kind, at}.
var events: Array = []
var spoof_cell := Vector2i(-1, -1)
var spoof_armed: bool = false
var spoof_used: bool = false
var press_t: float = 0.0
var press_done: bool = false
var press_hit: bool = false
## The sweep that is the real result; set once the spoof is settled.
var final: Dictionary = {}
var _miss: Dictionary = {}
var _next_step: int = 0
var _press_idx: int = -1


func _init(p_assets: Dictionary, p_b1: Array, p_cands: Array, p_reveal: int, p_own3: Array, p_plan: Dictionary) -> void:
	assets = p_assets
	b1 = p_b1
	cands = p_cands
	reveal = p_reveal
	own3 = p_own3
	plan = p_plan
	mode = M10Config.spoof_mode()
	_miss = M10Rules.sweep(assets, b1, cands[reveal], own3, plan)
	final = _miss


func beam_steps(k: int) -> Array:
	return final["beams"][k]["steps"]


## Beam index (0..2) being drawn, or -1 outside the sweeps.
func beam_now() -> int:
	match state:
		S.B1:
			return 0
		S.UNSEAL, S.DECIDE, S.B2, S.PRESS:
			return 1
		S.HUNTER, S.B3:
			return 2
	return -1


## Head position along the current beam in cells: 0 = just before the first node, i + 1 = at node i.
func head() -> float:
	var k := beam_now()
	if k < 0:
		return 0.0
	var n: int = (final["beams"][k]["steps"] as Array).size()
	match state:
		S.B1, S.B2, S.B3:
			return minf(t / M10Config.STEP_T, float(n))
		S.PRESS:
			return float(_press_idx + 1)
	return 0.0


func is_waiting() -> bool:
	return state == S.DECIDE or state == S.PRESS


func is_done() -> bool:
	return state == S.DONE


## The line of the revealed beam 2 (cells in scan order).
func line2() -> Array:
	return cands[reveal]


## True if the node may be a spoof target (it lies on the revealed beam 2).
func can_target(c: Vector2i) -> bool:
	return state == S.DECIDE and line2().has(c)


## Decision: skip this node with beam 2. In "choice" mode the effect is certain; in "press" mode it is armed and
## lands only if SPACE hits the window.
func choose_spoof(c: Vector2i) -> bool:
	if not can_target(c):
		return false
	spoof_cell = c
	spoof_used = true
	if mode == "choice":
		final = M10Rules.sweep(assets, b1, cands[reveal], own3, plan, [1, c])
		press_hit = true
	else:
		_press_idx = line2().find(c)
		## A decoy earlier on the line stops the beam before the node: there is nothing to press.
		spoof_armed = _press_idx < (_miss["beams"][1]["steps"] as Array).size()
	_enter(S.B2)
	return true


## Decision: hold the spoof (not used).
func pass_spoof() -> bool:
	if state != S.DECIDE:
		return false
	_enter(S.B2)
	return true


## SPACE during the press window. Returns true if it landed.
func press() -> bool:
	if state != S.PRESS or press_done:
		return false
	press_done = true
	press_hit = absf(press_t - M10Config.PRESS_PERFECT) <= M10Config.PRESS_TOL
	_settle_press()
	return press_hit


func _settle_press() -> void:
	if press_hit:
		final = M10Rules.sweep(assets, b1, cands[reveal], own3, plan, [1, spoof_cell])
	state = S.B2
	t = (_press_idx + 1) * M10Config.STEP_T
	_next_step = _press_idx


func _enter(s: int) -> void:
	state = s
	t = 0.0
	_next_step = 0


func _log(k: int, step: Dictionary) -> void:
	events.append({"beam": k, "cell": step["cell"], "kind": step["kind"], "at": clock})


## Log the beam's steps whose time has come. `hold_at` >= 0 stops before that step (the press window).
func _reveal_steps(k: int, hold_at: int = -1) -> void:
	var steps: Array = beam_steps(k)
	while _next_step < steps.size() and t >= (_next_step + 1) * M10Config.STEP_T:
		if hold_at >= 0 and _next_step == hold_at:
			return
		_log(k, steps[_next_step])
		_next_step += 1


func _beam_len(k: int) -> float:
	return (beam_steps(k).size()) * M10Config.STEP_T + 0.35


func advance(dt: float, dt_real: float = -1.0) -> void:
	if dt_real < 0.0:
		dt_real = dt
	if state == S.DONE:
		return
	clock += dt
	match state:
		S.B1:
			t += dt
			_reveal_steps(0)
			if t >= _beam_len(0):
				_enter(S.UNSEAL)
		S.UNSEAL:
			t += dt
			if t >= M10Config.UNSEAL_T:
				_enter(S.DECIDE)
		S.DECIDE:
			pass
		S.B2:
			t += dt
			var hold := -1
			if spoof_armed and not press_done:
				hold = _press_idx
			_reveal_steps(1, hold)
			if hold >= 0 and _next_step == hold and t >= (hold + 1) * M10Config.STEP_T:
				state = S.PRESS
				press_t = 0.0
				return
			if t >= _beam_len(1):
				_enter(S.HUNTER)
		S.PRESS:
			press_t += dt_real
			if press_t >= M10Config.PRESS_WINDOW and not press_done:
				press_done = true
				press_hit = false
				_settle_press()
		S.HUNTER:
			t += dt
			if t >= M10Config.HUNTER_T:
				_enter(S.B3)
		S.B3:
			t += dt
			_reveal_steps(2)
			if t >= _beam_len(2):
				_enter(S.END)
		S.END:
			t += dt
			if t >= M10Config.END_T:
				state = S.DONE


## SKIP: run to the end. Stops at the spoof decision (it needs the player); an open press window counts as missed.
func skip() -> void:
	var guard := 0
	while state != S.DONE and state != S.DECIDE and guard < 4000:
		if state == S.PRESS and not press_done:
			press_done = true
			press_hit = false
			_settle_press()
		advance(0.05, 0.05)
		guard += 1


## The found cells logged by the sweeps (checked against `final` in flow_check).
func logged_found() -> Array:
	var out: Array = []
	for e in events:
		if e["kind"] == "found":
			out.append(e["cell"])
	return out


## The cell of the first find (or decoy) the hunter turns on, or (-1, -1).
func hunter_from() -> Vector2i:
	return final["first"]
