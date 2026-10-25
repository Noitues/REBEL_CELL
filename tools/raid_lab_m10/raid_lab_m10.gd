extends Control
## L5 sweep-raid lab: the playable view. Reads L5Model / L5Play and draws; the rules live in L5Rules.
## Flow: contact (the raid's strength by Heat band), plan (the leg kit tray, levers), forecast (per sealed line: the hold
## result, the nodes a spoof could save and the range with a spoof; it never names a best spoof), hands-off playout with
## the spoof decision, aftermath (outcome tier), the between-raids screen (repairs, one shop buy, run intensity), leg
## record. A touch that takes HOME to 0 integrity ends the sweep and the campaign (BREACH, full screen).
## Capture mode: `-- --shots=<abs dir> [--leg=0] [--line=planned|naive|greedy] [--lite] [--scramble]` plays the whole leg.

enum Phase { CONTACT, PLAN, FORECAST, PLAY, AFTER, REPAIR, BREACH, RECORD }

const G = preload("res://tools/raid_lab_m10/l5_glyphs.gd")
const SPEEDS := L7Config.SPEEDS
const NODE_R := 28.0
const DASHES := [Vector2(18, 8), Vector2(6, 6), Vector2(14, 4)]
const PANEL_X := 780.0
const PANEL_W := 460.0
const STRIP_Y := 676.0
## Where a spoof mark sits on its node (up and right, clear of the sealed lines' caps).
const SPOOF_OFF := Vector2(36, -34)
## Parallel beams on one row or column draw in fixed, ordered lanes this far apart (px), centered on the row or column.
const LANE := 18.0
const GREY := Color8(82, 86, 104)
const GREY_EDGE := Color8(130, 136, 160)
const LEVER_TEXT := {
	"ghost": ["GHOST", "Hides one asset or HOME from every beam.", "1"],
	"decoy": ["DECOY", "A beam stops on it: a touch, not a find.", "2"],
	"dark": ["GO DARK", "Hides one asset; it earns nothing this interval.", "3"],
}

var model := L5Model.new()
var play: L5Play = null
var row: Dictionary = {}
var phase: int = Phase.CONTACT
var sel_lever: String = ""
var speed_i: int = 0
var hits: Array = []
var mouse := Vector2(-100, -100)
var status_msg: String = ""
var capture_dir: String = ""
var cap_line: String = "planned"
var cap_lite: bool = false
var cap_demo: String = ""
var _settled: bool = false
var board: L7Board = null
var max_shots: int = 0
## The decoys a beam has stopped on in the picture drawn now (set with the board's state each frame).
var _spent: Array = []
## The cues of the raid in play (L7Fx), read off the resolver's events as they happen.
var fx := L7Fx.new()
## The ambient clock (pulses, shimmer): real frames, or fixed steps in a capture.
var anim_t: float = 0.0
## The speed-scaled clock of the UI-level effects (Heat meter, stamps, count-ups) and when the current screen began.
var fx_clock: float = 0.0
var phase_at: float = 0.0
## The Heat meter's easing: it shows `_heat_from` easing to `_heat_to` since `_heat_t0`; the thresholds crossed pulse.
var _heat_from: float = -1.0
var _heat_to: float = -1.0
var _heat_t0: float = 0.0
var _heat_pulses: Array = []
## The Heat the meter shows right now (set by the HUD each frame), and the next-raid beam strip's beam count and when it changed.
var _heat_disp: float = 0.0
var _nb_shown: int = -1
var _nb_at: float = 0.0
## HOME's drain on the HUD: the integrity it showed, and when each pip was last lost (the white lag bar).
var _home_shown: int = -1
var _home_lost_at: Dictionary = {}
## Clip mode (Movie Maker): a scripted run played in real time, `--clip=planned|breach`.
var clip_mode: String = ""
## True while the settled breach plays fast (no contact, plan, forecast or decision screens), under the "cell falls" banner.
var fast_play: bool = false
## The extra known beams (0..2) the screen's raid runs with: only those lines take a lane.
var lane_extra: int = 2
var _shot_n: int = 0
var _badges: Array = []
## The one lever that would avoid a certain breach, cached per plan: {lever, cell} or {}.
var _bf_key: String = ""
var _bf_val: Dictionary = {}
## The decision screen's option the grid previews: set by the pointer on a row, or pinned by the capture.
const NO_FOCUS := Vector2i(-9, -9)
var dec_pin: Vector2i = NO_FOCUS
var dec_focus: Vector2i = NO_FOCUS


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	# The 3D board sits behind this control's own drawing (a canvas layer below the default one).
	board = L7Board.new()
	var back := CanvasLayer.new()
	back.layer = -1
	back.add_child(board)
	add_child(back)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shots="):
			capture_dir = a.substr(8)
		elif a.begins_with("--leg="):
			model.new_leg(int(a.substr(6)))
		elif a.begins_with("--line="):
			cap_line = a.substr(7)
		elif a.begins_with("--spoofview="):
			L5Config.toggles["SPOOF_VIEW"] = a.substr(12)
		elif a.begins_with("--key="):
			L5Config.toggles["KEY_LABEL"] = a.substr(6)
		elif a == "--lite":
			cap_lite = true
		elif a.begins_with("--maxshots="):
			max_shots = int(a.substr(11))
		elif a == "--demo=breachfix":
			cap_demo = "breachfix"
		elif a == "--demo=ownline":
			cap_demo = "ownline"
		elif a == "--demo=amber":
			cap_demo = "amber"
		elif a == "--scramble":
			G.scramble = true
		elif a == "--instant":
			L7Config.instant = true
		elif a.begins_with("--speed="):
			speed_i = clampi(int(a.substr(8)), 0, SPEEDS.size() - 1)
		elif a.begins_with("--clip="):
			clip_mode = a.substr(7)
	if capture_dir != "":
		_run_capture.call_deferred()
	elif clip_mode != "":
		_run_clip.call_deferred()


func _process(delta: float) -> void:
	var dt: float = delta * SPEEDS[speed_i]
	# In a capture the ambient clock steps by a fixed frame so the stills repeat; the capture script paces everything else.
	anim_t += (1.0 / 60.0) if capture_dir != "" else delta
	if capture_dir == "":
		fx_clock += dt
	if phase == Phase.PLAY and play != null and capture_dir == "":
		_adv(dt)
	queue_redraw()


## Advance the playout by dt seconds (already speed-scaled) and read its new events into the cues. Instant mode runs to the
## next decision or to the end in one go: the same steps, the same events, no pacing.
func _adv(dt: float) -> void:
	if play == null:
		return
	if L7Config.instant:
		var guard := 0
		while not play.is_done() and play.state != L5Play.S.DECIDE and guard < 4000:
			play.advance(0.05)
			fx.consume(play)
			guard += 1
	else:
		play.advance(dt)
		fx.consume(play)
	_check_done()


## Change screen: remember when it began (the stamp, the count-up and the meter ease from here).
func _set_phase(p: int) -> void:
	if p != phase:
		phase_at = fx_clock
	phase = p


## Seconds the current screen has been up (speed-scaled; a capture adds its own settle time).
func screen_t() -> float:
	return fx_clock - phase_at


## When the playout ends: settle the raid; a breach goes to the full-screen end, else to the aftermath.
func _check_done() -> void:
	if play != null and play.is_done() and not _settled:
		_settled = true
		row = model.settle(play)
		_set_phase(Phase.BREACH if model.breached else Phase.AFTER)


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		mouse = (event as InputEventMouseMotion).position
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		for k in range(hits.size() - 1, -1, -1):
			if (hits[k]["rect"] as Rect2).has_point(event.position):
				_act(hits[k]["id"])
				return
	elif event is InputEventKey and event.pressed and not event.echo:
		_key(event.keycode)


func _key(code: int) -> void:
	var planning: bool = phase in [Phase.PLAN, Phase.FORECAST]
	if phase == Phase.REPAIR:
		match code:
			KEY_1:
				_act("buy:ghost")
				return
			KEY_2:
				_act("buy:decoy")
				return
			KEY_3:
				_act("buy:spoof")
				return
			KEY_4:
				_act("buy:dark")
				return
			KEY_0:
				_act("buy:none")
				return
			KEY_L:
				_act("inten:LOW")
				return
			KEY_N:
				_act("inten:NORMAL")
				return
			KEY_H:
				_act("inten:HOT")
				return
	match code:
		KEY_F1:
			_act("tog:SPOOF_VIEW")
		KEY_F2:
			_act("tog:KEY_LABEL")
		KEY_1:
			_act("lever:ghost" if planning else "speed:0")
		KEY_2:
			_act("lever:decoy" if planning else "speed:1")
		KEY_3:
			_act("lever:dark")
		KEY_4:
			_act("speed:2")
		KEY_I:
			_act("instant")
		KEY_S:
			_act("skip")
		KEY_H:
			_act("hold")
		KEY_J:
			_act("jam")
		KEY_Z, KEY_BACKSPACE:
			_act("undo")
		KEY_ESCAPE:
			sel_lever = ""
		KEY_B:
			_act("back")
		KEY_ENTER, KEY_SPACE:
			if phase != Phase.PLAY:
				_act("next")


# ---------- actions ----------
func _act(id: String) -> void:
	status_msg = ""
	if id.begins_with("tog:"):
		L5Config.cycle(id.substr(4))
	elif id == "next":
		_next()
	elif id == "back":
		if phase == Phase.FORECAST:
			_set_phase(Phase.PLAN)
	elif id.begins_with("lever:"):
		if phase in [Phase.PLAN, Phase.FORECAST]:
			var lv := id.substr(6)
			sel_lever = "" if sel_lever == lv else lv
	elif id.begins_with("cell:"):
		var p := id.substr(5).split(",")
		_click_cell(Vector2i(int(p[0]), int(p[1])))
	elif id == "undo":
		if phase in [Phase.PLAN, Phase.FORECAST]:
			model.undo()
	elif id == "forecast":
		if phase == Phase.PLAN:
			_set_phase(Phase.FORECAST)
	elif id == "launch":
		_launch()
	elif id.begins_with("speed:"):
		speed_i = clampi(int(id.substr(6)), 0, SPEEDS.size() - 1)
	elif id == "instant":
		L7Config.instant = not L7Config.instant
	elif id == "skip":
		if phase == Phase.PLAY and play != null:
			play.skip()
			_check_done()
	elif id == "hold":
		if phase == Phase.PLAY and play != null:
			play.pass_spoof()
			fx.consume(play)
	elif id == "jam":
		if phase == Phase.PLAY and play != null:
			play.choose_jam()
			fx.consume(play)
	elif id.begins_with("buy:"):
		if phase == Phase.REPAIR:
			var what := id.substr(4)
			status_msg = model.set_buy("" if what == "none" else what)
	elif id.begins_with("inten:"):
		if phase == Phase.REPAIR:
			model.set_intensity(id.substr(6))


func _next() -> void:
	match phase:
		Phase.CONTACT:
			_set_phase(Phase.PLAN)
			sel_lever = ""
		Phase.PLAN:
			_set_phase(Phase.FORECAST)
		Phase.FORECAST:
			_launch()
		Phase.AFTER:
			if model.leg_over():
				_set_phase(Phase.RECORD)
			else:
				_set_phase(Phase.REPAIR)
		Phase.REPAIR:
			var settled := model.breach_settled()
			model.finish_between()
			if settled:
				_launch_settled()
			else:
				_set_phase(Phase.CONTACT)
		Phase.BREACH:
			_set_phase(Phase.RECORD)
		Phase.RECORD:
			model.new_leg(model.seed_id)
			_set_phase(Phase.CONTACT)


func _launch() -> void:
	if phase in [Phase.PLAN, Phase.FORECAST]:
		play = model.make_play()
		fx.reset()
		_stamp_shown = false
		fx.consume(play)
		_settled = false
		fast_play = false
		_set_phase(Phase.PLAY)
		sel_lever = ""


## A settled breach: the next raid is played at once with no levers and no response (HOLD), one short beat per beam, to the
## BREACHED card. The rules' result is the same as in the slow playout (every plan and every response loses HOME).
func _launch_settled() -> void:
	play = model.make_play()
	play.fast = true
	fx.reset()
	_stamp_shown = false
	fx.consume(play)
	_settled = false
	fast_play = true
	_set_phase(Phase.PLAY)
	sel_lever = ""
	speed_i = 0


func _click_cell(c: Vector2i) -> void:
	if phase in [Phase.PLAN, Phase.FORECAST]:
		if model.lever_at(c) != "":
			model.remove_at(c)
		elif sel_lever != "":
			var why := model.why_not(sel_lever, c)
			if why != "":
				status_msg = "Cannot place: " + why
			else:
				model.place(sel_lever, c)
		else:
			status_msg = "Pick a lever first (1 ghost, 2 decoy, 3 go dark)."
	elif phase == Phase.PLAY and play != null:
		if play.state == L5Play.S.DECIDE:
			if not play.choose_spoof(c):
				status_msg = "Pick a node on the lit beam-2 line."
			else:
				fx.consume(play)
	elif phase == Phase.REPAIR:
		status_msg = model.toggle_repair(c)


# ---------- geometry ----------
## Where a cell sits on the screen at the beam plane: beams, hunter arrows and flash rings pass here (the target camera).
static func nx(c: Vector2i) -> Vector2:
	return L7Cam.beam_pos(c)


## Where the cell's chip (value, status glyph, pips) floats over its tower; HOME's rides higher on its taller tower.
func chip_at(c: Vector2i) -> Vector2:
	return L7Cam.chip_pos(c, c == model.home())


func _add_hit(r: Rect2, id: String) -> void:
	hits.append({"rect": r, "id": id})


func _hot(r: Rect2) -> bool:
	return r.has_point(mouse)


func _btn(r: Rect2, label: String, id: String, enabled: bool = true, size: int = 18) -> void:
	G.button(self, r, label, _hot(r), enabled, size)
	if enabled:
		_add_hit(r, id)


func _cell_hit(c: Vector2i) -> void:
	var top := chip_at(c)
	var low := nx(c)
	_add_hit(Rect2(Vector2(low.x - 46.0, top.y - 46.0), Vector2(92.0, maxf(92.0, low.y - top.y + 92.0))), "cell:%d,%d" % [c.x, c.y])


## Beam geometry: node centers, the start extension a, the end extension b, the direction and a perpendicular offset.
func _geom(line: Array, off: float = 0.0) -> Dictionary:
	var pts: Array = []
	for c in line:
		pts.append(nx(c))
	var dir: Vector2 = ((pts.back() as Vector2) - (pts[0] as Vector2)).normalized()
	var step: float = ((pts[1] as Vector2) - (pts[0] as Vector2)).length()
	# Lanes are measured from the line's canonical direction (right or down), so lane 0 is always on the same side of a
	# row or column whichever way the beam runs.
	var canon := dir if (dir.x + dir.y) >= 0.0 else -dir
	var perp := Vector2(-canon.y, canon.x) * off
	for i in range(pts.size()):
		pts[i] = (pts[i] as Vector2) + perp
	return {"pts": pts, "a": (pts[0] as Vector2) - dir * step * 0.62, "b": (pts.back() as Vector2) + dir * step * 0.4, "dir": dir}


## The path of a beam up to head u (0 = start, i + 1 = node i, n + 1 = end extension).
func _path(g: Dictionary, u: float) -> PackedVector2Array:
	var pts: Array = g["pts"]
	var n := pts.size()
	var out := PackedVector2Array([g["a"]])
	var uu := clampf(u, 0.0, n + 1.0)
	for i in range(n + 1):
		var target: Vector2 = pts[i] if i < n else g["b"]
		if uu >= i + 1.0:
			out.append(target)
		else:
			var prev: Vector2 = out[out.size() - 1]
			out.append(prev.lerp(target, uu - i))
			break
	return out


func _arrow_head(path: PackedVector2Array, col: Color) -> void:
	var last: Vector2 = path[path.size() - 1]
	var prev: Vector2 = path[path.size() - 2]
	if last.distance_to(prev) > 0.5:
		var d := (last - prev).normalized()
		var n := Vector2(-d.y, d.x)
		draw_colored_polygon(PackedVector2Array([last + d * 9.0, last - d * 6.0 + n * 8.0, last - d * 6.0 - n * 8.0]), col)


## A beam as a light ribbon (L7Draw.beam): settled beams glow, the active head glows hotter, pending lines stay thin and plain.
func _draw_path(path: PackedVector2Array, col: Color, w: float, head_arrow: bool = true) -> void:
	if path.size() < 2:
		return
	var gl := 0.85
	if col == G.THREAT_FADE:
		gl = 0.0
	elif col == G.THREAT_LIGHT:
		gl = 1.3
	L7Draw.beam(self, path, col, w, gl, head_arrow)


## A dashed line with an arrow head; `phase` scrolls the dashes (the shimmer of a sealed line).
func _draw_dashed_path(path: PackedVector2Array, col: Color, dash: Vector2, w: float, phase: float = 0.0, glow: bool = true) -> void:
	if path.size() < 2:
		return
	if glow:
		L7Draw.dashed(self, path, Color(col.r, col.g, col.b, col.a * 0.22), dash.x, dash.y, w * 2.6, phase)
	L7Draw.dashed(self, path, col, dash.x, dash.y, w, phase)
	_arrow_head(path, col)


## The first `f` (0..1) of a path by length.
func _trim(path: PackedVector2Array, f: float) -> PackedVector2Array:
	var total := 0.0
	for i in range(path.size() - 1):
		total += path[i].distance_to(path[i + 1])
	var want := total * clampf(f, 0.0, 1.0)
	var out := PackedVector2Array([path[0]])
	var run := 0.0
	for i in range(path.size() - 1):
		var seg := path[i].distance_to(path[i + 1])
		if run + seg >= want:
			var u := 0.0 if seg < 0.001 else (want - run) / seg
			out.append(path[i].lerp(path[i + 1], u))
			return out
		out.append(path[i + 1])
		run += seg
	return out


## The six lines of a raid in a fixed order: beam 1, extra, extra2, the 3 sealed candidates.
func _all_lines() -> Array:
	var rd: Dictionary = model.raid_data()
	return [rd["b1"], rd["extra"], rd["extra2"], rd["cands"][0], rd["cands"][1], rd["cands"][2]]


## The row or column a line runs along: "r<y>" for a row, "c<x>" for a column.
func _lane_key(line: Array) -> String:
	var a: Vector2i = line[0]
	var b: Vector2i = line[line.size() - 1]
	return "r%d" % a.y if a.y == b.y else "c%d" % a.x


## How many lanes a row or column holds: the raid's lines on it, plus one reserved lane on every column for the hunter.
func _lane_count(key: String) -> int:
	var n := 0
	var lines := _all_lines()
	for i in range(lines.size()):
		if _lane_live(i) and _lane_key(lines[i]) == key:
			n += 1
	return n + (1 if key.begins_with("c") else 0)


## A line takes a lane only when it runs this raid: beam 1 and the sealed candidates always, the extra known beams only
## once the Heat has brought them (`lane_extra`, set each frame from the screen's raid).
func _lane_live(i: int) -> bool:
	return i == 0 or i >= 3 or i <= lane_extra


## Lane k of n, centered on the row or column (px).
func _lane_px(k: int, n: int) -> float:
	return (float(k) - float(n - 1) * 0.5) * LANE


## Offsets (px) of the six lines (same order as _all_lines): parallel beams on one row or column take fixed, ordered lanes
## (beam 1, extra, extra 2, sealed candidates in that order), side by side, centered on the row or column.
func _offsets() -> Array:
	var seen := {}
	var out: Array = []
	var lines := _all_lines()
	for i in range(lines.size()):
		var key := _lane_key(lines[i])
		var k: int = int(seen.get(key, 0))
		if _lane_live(i):
			seen[key] = k + 1
		out.append(_lane_px(k, _lane_count(key)))
	return out


## Where a beam stops: its decoy node, or past the last node.
func _beam_u(b: Dictionary, g: Dictionary) -> float:
	return float((b["steps"] as Array).size()) if b["stopped"] else float((g["pts"] as Array).size() + 1)


## A beam's start badge, moved along the line's back direction when another badge already sits there.
func _start_badge(g: Dictionary, label: String) -> void:
	var p: Vector2 = (g["a"] as Vector2) - (g["dir"] as Vector2) * 24.0
	var guard := 0
	var moved := true
	while moved and guard < 6:
		moved = false
		for q: Vector2 in _badges:
			if p.distance_to(q) < 26.0:
				p -= (g["dir"] as Vector2) * 28.0
				moved = true
		guard += 1
	_badges.append(p)
	G.badge(self, p, label)


func _mid(g: Dictionary) -> Vector2:
	var pts: Array = g["pts"]
	return ((pts[0] as Vector2) + (pts[1] as Vector2)) * 0.5


## The hunter runs down a column in the lane reserved for it, after the raid's own lines on that column.
## `k` > 0 is for the plan's per-shape hunter columns that share one column: each takes the next lane beyond.
func _h_off(x: int, k: int = 0) -> float:
	var key := "c%d" % x
	return _lane_px(_lane_count(key) - 1 + k, _lane_count(key))


## Geometry of a beam by id for the current raid.
func _beam_geom(id: String, line: Array = []) -> Dictionary:
	var offs := _offsets()
	var rd: Dictionary = model.raid_data()
	match id:
		"b1":
			return _geom(rd["b1"], offs[0])
		"extra":
			return _geom(rd["extra"], offs[1])
		"extra2":
			return _geom(rd["extra2"], offs[2])
		"b2":
			var rk := model.real()
			return _geom(rd["cands"][rk], offs[3 + rk])
	return _geom(line, _h_off((line[0] as Vector2i).x))


## The pylons whose eyes are lit: where a line of this raid starts (rows from the left or right, columns from the top).
func _pylon_keys() -> Array:
	var keys: Array = []
	if phase in [Phase.RECORD, Phase.BREACH, Phase.REPAIR]:
		return keys
	var lines := _all_lines()
	for i in range(lines.size()):
		if not _lane_live(i):
			continue
		var line: Array = lines[i]
		var a: Vector2i = line[0]
		var b: Vector2i = line[line.size() - 1]
		if a.y == b.y:
			keys.append(("L:%d" if a.x < b.x else "R:%d") % a.y)
		elif a.y < b.y:
			keys.append("T:%d" % a.x)
	return keys


## What the 3D board shows now: the statuses of the cells the screen draws, the levers on them, and the beam effects.
func _board_state() -> Dictionary:
	var status: Dictionary = model.state.status
	var alloc: Dictionary = model.plan
	var spent: Array = []
	var home_hit := 0.0
	var flash := {}
	var shake := {}
	var flip := {}
	match phase:
		Phase.PLAY:
			status = play.status_now()["status"]
			alloc = play.alloc
			for e: Dictionary in play.events:
				var c: Vector2i = e["cell"]
				var a := _age(e)
				if e["outcome"] == "DECOY":
					spent.append(c)
				if a < 0.0:
					continue
				if a < L7Config.FLASH_T:
					flash[c] = maxf(float(flash.get(c, 0.0)), pow(1.0 - a / L7Config.FLASH_T, 2.0))
				if e["outcome"] == "DOWN" and a < L7Config.SHAKE_T:
					shake[c] = Vector2(sin(a * 75.0) * 0.16 * (1.0 - a / L7Config.SHAKE_T), 0.0)
				if e["outcome"] == "TAKEN" and a < L7Config.FLIP_T:
					flip[c] = a / L7Config.FLIP_T
					if a < L7Config.FLIP_T * 0.5:
						status[c] = "DOWN"
				if e["outcome"] == "HOME":
					home_hit = maxf(home_hit, clampf(1.0 - a / L7Config.HOME_NUM_T, 0.0, 1.0))
		Phase.AFTER, Phase.BREACH:
			if not row.is_empty():
				status = (row["after_raid"] as L5State).status
				alloc = row["alloc"]
				for o: Dictionary in row["outcomes"]:
					if o["outcome"] == "DECOY":
						spent.append(o["cell"])
		Phase.REPAIR:
			status = model.state.status.duplicate()
			for pc: Vector2i in model.pending_repairs:
				status[pc] = "OK"
			alloc = {"ghost": [], "dark": (model.history.back()["alloc"] as Dictionary)["dark"], "decoys": []}
		Phase.RECORD:
			alloc = L5Rules.empty_alloc()
	_spent = spent
	return {"values": model.values(), "home": model.home(), "status": status, "ghost": alloc["ghost"], "dark": alloc["dark"],
		"decoys": alloc["decoys"], "spent": spent, "home_hit": home_hit, "flash": flash, "shake": shake, "flip": flip}


# ---------- drawing ----------
func _draw() -> void:
	hits = []
	_badges = []
	lane_extra = _screen_extra()
	board.apply(_board_state())
	board.light_pylons(_pylon_keys())
	if phase == Phase.RECORD:
		draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), G.BG)
	elif phase != Phase.BREACH:
		# The side panel and the HUD read over the 3D scene through a dark veil.
		draw_rect(Rect2(PANEL_X - 12.0, 0, 1280.0 - PANEL_X + 12.0, 720), Color(G.BG.r, G.BG.g, G.BG.b, 0.84))
		draw_rect(Rect2(0, 0, PANEL_X - 12.0, 72), Color(G.BG.r, G.BG.g, G.BG.b, 0.8))
		draw_line(Vector2(0, 72), Vector2(PANEL_X - 12.0, 72), Color(G.HOLD.r, G.HOLD.g, G.HOLD.b, 0.6), 1.0)
	if phase != Phase.BREACH:
		_draw_hud()
	match phase:
		Phase.CONTACT:
			_draw_contact()
		Phase.PLAN, Phase.FORECAST:
			_draw_plan()
		Phase.PLAY:
			_draw_play()
		Phase.AFTER:
			_draw_after()
		Phase.REPAIR:
			_draw_repair()
		Phase.BREACH:
			_draw_breach()
		Phase.RECORD:
			_draw_record()
	_draw_age_labels()
	_draw_strip()


## The extra known beams the drawn raid runs with: the plan's Heat while planning, the sweep's Heat in play, the ledger's after.
func _screen_extra() -> int:
	match phase:
		Phase.CONTACT:
			return L5Rules.extra_count(model.state.heat)
		Phase.PLAN, Phase.FORECAST:
			return model.extra_now()
		Phase.PLAY:
			return L5Rules.extra_count(play.run_heat) if play != null else 0
		Phase.AFTER, Phase.BREACH:
			return int(row["ledger"]["extra"]) if not row.is_empty() else 0
	return 0


## "down N raids" on every DOWN asset that has stayed down (top left of the node, over the beams so it stays legible). Shown
## on the contact, plan, forecast and between screens, and in the aftermath for assets down two raids or more.
func _draw_age_labels() -> void:
	var status: Dictionary = {}
	match phase:
		Phase.CONTACT, Phase.PLAN, Phase.FORECAST:
			status = model.state.status
		Phase.REPAIR:
			status = model.state.status.duplicate()
			for pc: Vector2i in model.pending_repairs:
				status[pc] = "OK"
		Phase.AFTER:
			status = (row["after_raid"] as L5State).status
	for c: Vector2i in status:
		var age: int = int(model.down_raids.get(c, 0))
		if status[c] != "DOWN" or age <= 0 or (phase == Phase.AFTER and age < 2):
			continue
		var txt := "down %d raid%s" % [age, "" if age == 1 else "s"]
		var w := G.text_w(txt, 12) + 12.0
		var p := chip_at(c)
		var r := Rect2(p.x - 22.0 - w, p.y - 54.0, w, 20.0)
		G.panel(self, r, G.HOLD if age > 1 else G.PANEL_EDGE, G.BG, 1.0)
		G.text(self, Vector2(r.position.x + 6, r.position.y + 3), txt, 12, G.HOLD if age > 1 else G.DIM)


## What the HUD shows now: {heat, bank, hp, dheat, dbank, proj, kept, kept_was}. `kept` is the assets-kept number
## (live on every screen), `kept_was` what it was before this screen's change (-1 = no change to show).
func _hud_values() -> Dictionary:
	var s := model.state
	var v := {"heat": s.heat, "bank": s.bank, "hp": s.home_hp, "dheat": 0, "dbank": 0, "proj": [0, 0], "kept": model.kept_now(), "kept_was": -1}
	match phase:
		Phase.PLAN, Phase.FORECAST:
			v["heat"] = model.heat_now()
			v["bank"] = model.state.bank
			v["dheat"] = int(v["heat"]) - s.heat
			v["dbank"] = int(v["bank"]) - s.bank
			if phase == Phase.FORECAST:
				v["proj"] = model.worst_home_loss()
		Phase.PLAY:
			v["heat"] = play.run_heat
			v["bank"] = model.state.bank
			v["dheat"] = play.run_heat - play.before.heat
			v["dbank"] = int(v["bank"]) - play.before.bank
			v["hp"] = play.status_now()["home_hp"]
			var ks: L5State = play.before.copy()
			ks.status = play.status_now()["status"]
			v["kept"] = L5Rules.assets_kept(model.leg, ks)
			v["kept_was"] = L5Rules.assets_kept(model.leg, play.before)
		Phase.AFTER, Phase.RECORD:
			if not row.is_empty() and phase == Phase.AFTER:
				var l: Dictionary = row["ledger"]
				v["dheat"] = int(l["heat_after"]) - int(l["heat_before"])
				v["kept_was"] = L5Rules.assets_kept(model.leg, row["before"])
		Phase.REPAIR:
			var bp: Dictionary = model.between_preview()
			var ns: L5State = bp["state"]
			v["heat"] = ns.heat
			v["bank"] = ns.bank
			v["dheat"] = ns.heat - s.heat
			v["dbank"] = ns.bank - s.bank
			v["kept"] = model.kept_after_picks()
			v["kept_was"] = model.kept_now()
	if int(v["kept_was"]) == int(v["kept"]):
		v["kept_was"] = -1
	return v


## The Heat the meter shows: it eases from what it showed to `target` over HEAT_EASE_T, and every Heat line crossed on the
## way up registers a pulse (the notch's glyph is stamped). Instant mode shows the target at once.
func _hud_heat(target: float) -> float:
	if _heat_to < 0.0:
		_heat_from = target
		_heat_to = target
		_heat_t0 = fx_clock - 99.0
	if absf(target - _heat_to) > 0.001:
		var cur := target if L7Config.instant else _heat_value_now()
		_heat_from = cur
		_heat_to = target
		_heat_t0 = fx_clock
		if not L7Config.instant:
			for line: int in [L5Config.EXTRA_AT, L5Config.STRONG_AT]:
				if cur < float(line) and target >= float(line):
					var hit := 1.0
					for k in range(41):
						var u := float(k) / 40.0
						if lerpf(cur, target, L7Config.ease_out(u)) >= float(line):
							hit = u
							break
					_heat_pulses.append({"line": line, "at": fx_clock + hit * L7Config.HEAT_EASE_T})
	return target if L7Config.instant else _heat_value_now()


func _heat_value_now() -> float:
	var u := clampf((fx_clock - _heat_t0) / L7Config.HEAT_EASE_T, 0.0, 1.0)
	return lerpf(_heat_from, _heat_to, L7Config.ease_out(u))


## Track HOME's integrity: a pip lost now starts its white lag bar.
func _track_home(hp: int) -> void:
	if _home_shown < 0:
		_home_shown = hp
	if hp < _home_shown:
		for k in range(hp, _home_shown):
			_home_lost_at[k] = fx_clock
	elif hp > _home_shown:
		_home_lost_at.clear()
	_home_shown = hp


## One HOME integrity pip (the L6 pip) and, for a pip just lost, the white lag bar that drains behind the red one.
func _home_pip(c: Vector2, s: float, k: int, mode: String) -> void:
	G.pip(self, c, s, mode)
	if mode == "lost" and _home_lost_at.has(k) and not L7Config.instant:
		var u: float = (fx_clock - float(_home_lost_at[k]) - L7Config.HOME_LAG_DELAY) / L7Config.HOME_LAG_T
		var left := 1.0 - clampf(u, 0.0, 1.0)
		if left > 0.0 and (fx_clock - float(_home_lost_at[k])) < L7Config.HOME_LAG_DELAY + L7Config.HOME_LAG_T:
			draw_rect(Rect2(c.x - s * 0.5, c.y - s * 0.5, s * left, s), Color(1, 1, 1, 0.9))


func _draw_hud() -> void:
	var v := _hud_values()
	var hx := 60.0
	var hw := 360.0
	var hy := 18.0
	var hh := 22.0
	var hd := _hud_heat(float(v["heat"]))
	_heat_disp = hd
	var dh: int = int(v["dheat"])
	L7Draw.glow(self, Vector2(34, hy + 12), 20.0, G.HEAT, 0.55)
	G.flame(self, Vector2(34, hy + 12), 10)
	# The meter: a dark track, the Heat in orange (a gradient toward red), the part this screen added with a bright top.
	draw_rect(Rect2(hx - 2, hy - 2, hw + 4, hh + 4), Color(0.01, 0.02, 0.08, 0.95))
	var frac := clampf(hd / L5Config.HEAT_MAX, 0.0, 1.0)
	var base_frac := clampf((float(v["heat"]) - float(maxi(0, dh))) / L5Config.HEAT_MAX, 0.0, 1.0)
	var segs := 36
	for k in range(segs):
		var sx := hx + hw * float(k) / segs
		var sw := hw / segs + 0.5
		var lit := clampf(hw * frac - (sx - hx), 0.0, sw)
		if lit > 0.0:
			draw_rect(Rect2(sx, hy, lit, hh), G.heat_color((float(k) + 0.5) / segs))
	if dh > 0 and frac > base_frac:
		draw_rect(Rect2(hx + hw * base_frac, hy, hw * (frac - base_frac), 6), Color(1.0, 0.86, 0.5, 0.95))
	elif dh < 0:
		draw_rect(Rect2(hx + hw * frac, hy, hw * (base_frac - frac), hh), Color(1, 1, 1, 0.22))
	draw_rect(Rect2(hx, hy, hw, hh), Color(G.HOLD.r, G.HOLD.g, G.HOLD.b, 0.55), false, 1.5)
	# The two notches, each wearing the glyph of the beam it adds; a crossing pulses and stamps the glyph.
	for band in [[L5Config.EXTRA_AT, "+", ""], [L5Config.STRONG_AT, "++", ""]]:
		var bxp: float = hx + hw * float(band[0]) / L5Config.HEAT_MAX
		var lit: bool = hd >= float(int(band[0])) - 0.01
		var pop := 1.0
		for pu: Dictionary in _heat_pulses:
			var age: float = fx_clock - float(pu["at"])
			if int(pu["line"]) == int(band[0]) and age >= 0.0 and age < L7Config.HEAT_PULSE_T:
				var u: float = age / L7Config.HEAT_PULSE_T
				pop = 1.0 + 0.55 * (1.0 - u) * (1.0 - u)
				draw_arc(Vector2(bxp, hy + hh * 0.5), 10.0 + 30.0 * u, 0.0, TAU, 32, Color(G.HEAT.r, G.HEAT.g, G.HEAT.b, 0.9 * (1.0 - u)), 4.0, true)
				draw_arc(Vector2(bxp, hy + hh + 17.0), 14.0 + 22.0 * u, 0.0, TAU, 32, Color(G.THREAT_HOT.r, G.THREAT_HOT.g, G.THREAT_HOT.b, 0.8 * (1.0 - u)), 3.0, true)
		G.line(self, Vector2(bxp, hy - 6), Vector2(bxp, hy + hh + 6), G.INK if lit else G.PANEL_EDGE, 3.0)
		draw_set_transform(Vector2(bxp, hy + hh + 17.0), 0.0, Vector2(pop, pop))
		G.badge(self, Vector2.ZERO, band[1], G.THREAT if lit else G.THREAT_FADE)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		G.text(self, Vector2(bxp + 17, hy + hh + 10), str(band[0]), 12, G.THREAT_LIGHT if lit else G.DIM)
	_heat_pulses = _heat_pulses.filter(func(pu: Dictionary) -> bool: return fx_clock - float(pu["at"]) < L7Config.HEAT_PULSE_T)
	var hn := str(int(round(hd)))
	G.text(self, Vector2(hx + hw + 14, hy - 10), hn, 32, G.HEAT)
	if dh != 0:
		G.text(self, Vector2(hx + hw + 22 + G.text_w(hn, 32), hy - 2), "%+d" % dh, 17, G.HOLD if dh > 0 else G.CLEAN)
	# Raid pips.
	G.text(self, Vector2(530, 12), "RAID %d/%d" % [mini(model.raid + 1, L5Config.RAIDS), L5Config.RAIDS], 13, G.DIM)
	for j in range(L5Config.RAIDS):
		var c := Vector2(540 + j * 24, 44)
		if j < model.history.size():
			var h: Dictionary = model.history[j]
			G.disc(self, c, 7, G.tier_color(String(h["tier"])))
		elif j == model.raid:
			G.circle(self, c, 7, G.CELL, 3.0)
		else:
			G.circle(self, c, 7, G.PANEL_EDGE)
	# Home integrity pips (with the projected loss in the forecast); a pip just lost drains a white lag bar.
	G.text(self, Vector2(640, 12), "HOME", 13, G.DIM)
	var hp: int = int(v["hp"])
	_track_home(hp)
	var proj: Array = v["proj"]
	for k in range(L5Config.HOME_HP):
		var mode := "full"
		if k >= hp:
			mode = "lost"
		elif phase == Phase.FORECAST and k >= hp - int(proj[0]):
			mode = "saved" if (L5Config.spoof_view() and k < hp - int(proj[1])) else "proj"
		_home_pip(Vector2(650 + k * 28, 42), 18.0, k, mode)
	# Bank: the number, and on the between screen the net change this step makes ("net", never a bare +N).
	var bx := 830.0
	G.coin(self, Vector2(bx + 12, 31), 11)
	G.text(self, Vector2(bx + 34, 12), str(v["bank"]), 28, G.CELL)
	if int(v["dbank"]) != 0:
		G.text(self, Vector2(bx + 92, 20), "net %+d" % int(v["dbank"]), 14, G.DMG if int(v["dbank"]) < 0 else G.CLEAN)
	G.text(self, Vector2(bx + 150, 20), L5Config.key_label().to_upper(), 13, G.DIM)
	# Assets kept, live (the score term the player otherwise meets only on the record).
	var kx := 1112.0
	G.text(self, Vector2(kx, 10), "ASSETS KEPT", 13, G.DIM)
	G.text(self, Vector2(kx, 24), str(v["kept"]), 28, G.INK)
	if int(v["kept_was"]) >= 0:
		G.text(self, Vector2(kx + 54, 34), "was %d" % int(v["kept_was"]), 13, G.DIM)



func _draw_strip() -> void:
	draw_rect(Rect2(0, STRIP_Y, 1280, 720 - STRIP_Y), Color(0, 0, 0, 0.55))
	var hint := ""
	match phase:
		Phase.CONTACT:
			hint = "Contact. Heat sets the raid's strength. Enter plans the defense."
		Phase.PLAN:
			hint = "Pick a lever (1 2 3), click a node to place it, click a placed lever to take it off. Z undoes. Enter shows the forecast. The kit lasts the whole leg."
		Phase.FORECAST:
			hint = "Forecast: each shape marks what that sealed line would do; a lime chevron marks a node a spoof could save. B edits. Enter launches."
		Phase.PLAY:
			hint = "The loss was decided between the raids: the sweep plays out at once." if fast_play else "Hands-off sweep. 1 / 2 / 4 speed, S skips. The response after the reveal (hold, skip or jam) needs you."
		Phase.AFTER:
			hint = "Aftermath. Enter continues."
		Phase.REPAIR:
			hint = "Between raids: repairs (click a DOWN asset), one shop buy (1 2 3 4, 0 none), run intensity (L N H). Enter goes on."
		Phase.BREACH:
			hint = "The campaign is lost. Enter shows the leg record."
		Phase.RECORD:
			hint = "Leg record. Enter plays the leg again."
	if status_msg != "":
		hint = status_msg
	G.text(self, Vector2(10, STRIP_Y + 3), hint, 13, G.INK if status_msg != "" else G.DIM)
	var tx := 10.0
	var items := [["SPOOF_VIEW", "SPOOF HINTS: " + L5Config.toggles["SPOOF_VIEW"].to_upper(), "F1"],
		["KEY_LABEL", "CURRENCY: " + L5Config.key_label().to_upper(), "F2"]]
	for it in items:
		var label: String = "%s  [%s]" % [it[1], it[2]]
		var w := G.text_w(label, 13) + 20.0
		var r := Rect2(tx, STRIP_Y + 21, w, 22)
		G.panel(self, r, G.PANEL_EDGE, Color8(60, 52, 24) if _hot(r) else G.PANEL, 1.0)
		G.text_c(self, r.get_center(), label, 13, G.CELL)
		_add_hit(r, "tog:" + String(it[0]))
		tx += w + 8.0
	G.text(self, Vector2(tx + 14, STRIP_Y + 24), "L5 SWEEP lab  |  leg %d  |  designer toggles" % model.seed_id, 12, G.DIM)


# ---- the network ----
## The playout's events on cell `c` (all beams, oldest first); empty outside the playout.
func _events_on(c: Vector2i) -> Array:
	var out: Array = []
	if phase == Phase.PLAY and play != null:
		for e: Dictionary in play.events:
			if e["cell"] == c:
				out.append(e)
	return out


## How long ago (seconds of the playout clock) an event happened; instant mode shows everything settled.
func _age(e: Dictionary) -> float:
	return 1.0e9 if (L7Config.instant or play == null) else play.clock - float(e["at"])


## The chip's shake (px) just after its cell went DOWN or HOME was hit.
func _chip_shake(c: Vector2i) -> Vector2:
	for e: Dictionary in _events_on(c):
		if e["outcome"] == "DOWN" or e["outcome"] == "HOME":
			var a := _age(e)
			if a >= 0.0 and a < L7Config.SHAKE_T:
				var k := 1.0 - a / L7Config.SHAKE_T
				return Vector2(sin(a * 75.0) * 6.0 * k, cos(a * 61.0) * 3.0 * k)
	return Vector2.ZERO


## Draw HOME: the server glyph on its chip, its integrity pips (a lost one drains a white lag bar), a ghost ring. A hit flashes
## the edge red and floats "-1" up off it.
func _draw_home(p: Vector2, hp: int, pl: Dictionary) -> void:
	var ghost: bool = (pl["ghost"] as Array).has(model.home())
	var hit := 0.0
	for e: Dictionary in _events_on(model.home()):
		if e["outcome"] == "HOME":
			var a := _age(e)
			hit = maxf(hit, clampf(1.0 - a / L7Config.HOME_NUM_T, 0.0, 1.0))
			if a >= 0.0 and a < L7Config.HOME_NUM_T:
				var u: float = a / L7Config.HOME_NUM_T
				G.text_c(self, p + Vector2(46, -22 - 40.0 * u), "-1", 36, Color(G.DMG.r, G.DMG.g, G.DMG.b, 1.0 - u * u), "head")
	L7Draw.glow(self, p, 44.0, G.DMG if hit > 0.0 else G.CELL, 0.25 + 0.5 * hit)
	G.home_server(self, p, 28.0, G.INK.lerp(G.DMG, minf(1.0, hit * 2.0)), Color(0.02, 0.03, 0.09, 0.95))
	if ghost:
		G.dashed_ring(self, p, 38.0, G.CELL, 4.0)
		G.flame(self, p + Vector2(34, -32), 7)
	for k in range(L5Config.HOME_HP):
		_home_pip(p + Vector2((k - 1) * 18.0, 44.0), 12.0, k, "full" if k < hp else "lost")


## One node as a chip floating over its tower: the value (Anton) with pips and the status glyph, in the cell's gold ring (DOWN
## grey, TAKEN cobalt, go dark hollow). The tower, hex ring and floor are the 3D board's.
func _draw_node(c: Vector2i, status: Dictionary, hp: int, pl: Dictionary) -> void:
	var p := chip_at(c) + _chip_shake(c)
	if c == model.home():
		_draw_home(p, hp, pl)
		return
	if (pl["decoys"] as Array).has(c):
		var spent := _spent.has(c)
		var dc := G.CELL if not spent else G.DIM
		var pts := PackedVector2Array([p + Vector2(0, -26), p + Vector2(26, 0), p + Vector2(0, 26), p + Vector2(-26, 0)])
		L7Draw.glow(self, p, 38.0, dc, 0.3)
		draw_colored_polygon(pts, Color(0.02, 0.03, 0.09, 0.94))
		pts.append(pts[0])
		draw_polyline(pts, dc, 4.0, true)
		draw_colored_polygon(PackedVector2Array([p + Vector2(0, -10), p + Vector2(10, 0), p + Vector2(0, 10), p + Vector2(-10, 0)]), dc)
		return
	if not model.values().has(c):
		return
	var v: int = model.values()[c]
	var st: String = status[c]
	var ghost: bool = (pl["ghost"] as Array).has(c)
	# Go dark (an OK asset): a hollow, dimmed node with a closed eye and a struck income pip. It never wears the DOWN look.
	var dark_any: bool = (pl["dark"] as Array).has(c)
	var dark: bool = dark_any and st == "OK"
	var fill := Color(0.02, 0.03, 0.09, 0.94)
	var edge := G.CELL
	match st:
		"DOWN":
			fill = Color(0.1, 0.11, 0.15, 0.95)
			edge = GREY_EDGE
		"TAKEN":
			fill = Color(0.04, 0.07, 0.22, 0.95)
			edge = G.THREAT_HOT
	if dark:
		fill = Color(G.BG.r, G.BG.g, G.BG.b, 0.9)
	if not dark:
		L7Draw.glow(self, p, NODE_R + 14.0, edge, 0.22)
	G.disc(self, p, NODE_R, fill)
	if dark:
		G.circle(self, p, NODE_R, Color(G.DIM.r, G.DIM.g, G.DIM.b, 0.55), 2.0)
	else:
		G.circle(self, p, NODE_R, edge, 3.0)
	if ghost:
		G.dashed_ring(self, p, NODE_R + 5, G.CELL, 4.0)
		G.flame(self, p + Vector2(32, -28), 7)
	# The node's worth without a number: one pip per PIP_VALUE of value.
	var n_pips := G.pip_count(v)
	var pip_pos := p + Vector2(0, 17)
	match st:
		"OK":
			if dark:
				G.eye_closed(self, p + Vector2(0, -2), 11.0, G.DIM, 2.5)
				G.text_c(self, p + Vector2(33, -26), str(v), 14, G.DIM)
				G.pips(self, pip_pos, n_pips, Color(G.DIM.r, G.DIM.g, G.DIM.b, 0.6))
			else:
				G.coin(self, p + Vector2(-13, -7), 7, G.CELL)
				G.text_c(self, p + Vector2(5, -6), str(v), 24, G.INK, "head")
				G.pips(self, pip_pos, n_pips, G.CELL)
		"DOWN":
			G.bolt(self, p + Vector2(0, -4), 15.0, G.INK)
			G.text_c(self, p + Vector2(33, -26), str(v), 14, G.DIM)
			G.pips(self, pip_pos, n_pips, G.GREY_PIP)
		"TAKEN":
			var pop := 1.0
			for e: Dictionary in _events_on(c):
				if e["outcome"] == "TAKEN":
					pop = L7Config.ease_back((_age(e) - L7Config.FLIP_T * 0.5) / (L7Config.FLIP_T * 0.5))
			if pop > 0.02:
				G.corp(self, p + Vector2(0, -4), 17.0 * pop)
			G.text_c(self, p + Vector2(33, -26), str(v), 14, G.DIM)
			G.line(self, p + Vector2(23, 40), p + Vector2(39, 20), G.DMG, 2.0)
			G.pips(self, pip_pos, n_pips, G.THREAT_LIGHT)
	if dark:
		# Its income pip is struck: it earns nothing this interval.
		_income_chip(p + Vector2(0, -49), L5Rules.idiv(v, L5Config.INCOME_DIV), true)
	elif dark_any:
		# Dark on a DOWN or TAKEN asset: it keeps its status look and wears the closed-eye chip (hidden from the beams).
		var ec := p + Vector2(-36, -30)
		G.disc(self, ec, 13, G.BG)
		G.circle(self, ec, 13, G.DIM, 2.0)
		G.eye_closed(self, ec + Vector2(0, 1), 7.0, G.INK, 2.0)


## An income chip: the same pip as the node's value, one per point of income, and the number; struck when it is lost.
func _income_chip(center: Vector2, inc: int, struck: bool) -> void:
	var w := 18.0 + inc * 7.0 + G.text_w("+%d" % inc, 13)
	var cr := Rect2(center.x - w * 0.5, center.y - 11, w, 22)
	var col := G.DIM if struck else G.CLEAN
	G.panel(self, cr, col, G.BG, 1.0)
	G.pips(self, Vector2(cr.position.x + 9 + inc * 3.5, center.y), inc, col, 4.5, 2.5)
	G.text(self, Vector2(cr.position.x + 12 + inc * 7.0, cr.position.y + 4), "+%d" % inc, 13, col)
	if struck:
		G.line(self, Vector2(cr.position.x + 3, cr.end.y - 3), Vector2(cr.end.x - 3, cr.position.y + 3), G.DMG, 3.0)


func _draw_net(show_hit_areas: bool, status: Dictionary = {}, hp: int = -1, pl: Dictionary = {}) -> void:
	var st: Dictionary = status if not status.is_empty() else model.state.status
	var h: int = hp if hp >= 0 else model.state.home_hp
	var plan: Dictionary = pl if not pl.is_empty() else model.plan
	for c in L5Rules.nodes():
		_draw_node(c, st, h, plan)
		if show_hit_areas:
			_cell_hit(c)


func _draw_legend() -> void:
	var y := 658.0
	var x := 20.0
	var items := ["decoy", "ghost", "dark", "spoof", "sealed", "down", "taken", "home"]
	var names := {"decoy": "DECOY", "ghost": "GHOST", "dark": "DARK", "spoof": "SPOOF", "sealed": "SEALED", "down": "DOWN", "taken": "TAKEN", "home": "HOME"}
	for it in items:
		var c := Vector2(x + 12, y)
		match it:
			"decoy":
				G.diamond(self, c, 11, G.CELL)
			"ghost":
				G.dashed_ring(self, c, 10, G.CELL, 3.0)
			"dark":
				G.dark_disc(self, c, 10.0)
			"spoof":
				G.skip_chevron(self, c, 7.0, G.CLEAN, 2.5)
			"sealed":
				_sealed_chip(c + Vector2(-2, 0), G.THREAT_LIGHT)
			"down":
				G.disc(self, c, 11, GREY)
				G.bolt(self, c, 9.0)
			"taken":
				G.corp(self, c, 11.0)
			"home":
				G.home_server(self, c, 10.0, G.INK)
		G.text(self, Vector2(x + 30, y - 8), names[it], 13, G.DIM)
		x += 30 + G.text_w(names[it], 13) + 18


# ---- beams ----
## Known beams of the plan: [{id, line, off_i, badge}] for beam 1 and the extras Heat brings.
func _known_beams(extra: int) -> Array:
	var rd: Dictionary = model.raid_data()
	var out: Array = [{"id": "b1", "line": rd["b1"], "badge": "1"}]
	if extra >= 1:
		out.append({"id": "extra", "line": rd["extra"], "badge": "+"})
	if extra >= 2:
		out.append({"id": "extra2", "line": rd["extra2"], "badge": "++"})
	return out


## Where a line stops in the plan: at the first decoy on it (path position of that node), else past its last node.
func _stop_u(line: Array, g: Dictionary) -> float:
	for i in range(line.size()):
		if (model.plan["decoys"] as Array).has(line[i]):
			return i + 1.0
	return float((g["pts"] as Array).size() + 1)


## The bar that stops a beam at a decoy (drawn just before the decoy's node).
func _stop_bar(g: Dictionary, u: float, col: Color) -> void:
	var pts: Array = g["pts"]
	var k := int(u) - 1
	if k < 0 or k >= pts.size():
		return
	var d: Vector2 = g["dir"]
	G.stop_bar(self, (pts[k] as Vector2) - d * 34.0, d, col)


func _draw_known_beams(extra: int, with_plan: bool) -> void:
	for kb: Dictionary in _known_beams(extra):
		var g := _beam_geom(kb["id"])
		var full := float((g["pts"] as Array).size() + 1)
		var u: float = _stop_u(kb["line"], g) if with_plan else full
		_draw_path(_path(g, u), G.THREAT, 6.0)
		if u < full:
			_stop_bar(g, u, G.THREAT_LIGHT)
		_start_badge(g, kb["badge"])


## The ghost's effect on the grid: the ghosted node is drawn over the beams (they pass behind it) and every line that
## reaches it gets a yellow detour round the node.
func _draw_ghost_skips() -> void:
	var ghosts: Array = model.plan["ghost"]
	if ghosts.is_empty():
		return
	var offs := _offsets()
	var rd: Dictionary = model.raid_data()
	var lines: Array = []
	for kb: Dictionary in _known_beams(model.extra_now()):
		lines.append([kb["line"], _beam_geom(kb["id"])])
	for i in range((rd["cands"] as Array).size()):
		lines.append([rd["cands"][i], _geom(rd["cands"][i], offs[3 + i])])
	for gc: Vector2i in ghosts:
		_draw_node(gc, model.state.status, model.state.home_hp, model.plan)
		var side := 1.0
		for ln: Array in lines:
			var line: Array = ln[0]
			var idx := line.find(gc)
			if idx < 0:
				continue
			var g: Dictionary = ln[1]
			if _stop_u(line, g) <= idx + 1.0:
				continue
			G.detour(self, nx(gc), NODE_R + 18.0, g["dir"], side, G.CELL, 3.0)
			side = -side


## The sealed candidates: dashed lines told apart by end shape and dash pattern (the shape of each candidate is shuffled
## per raid). A decoy stops them like any beam. Modes: "plan" (all three, a gentle shimmer), "unseal" (`u` 0..1 of the
## unseal: all three shimmer, two collapse back to their pylons struck out, the real one ignites end to end), "revealed"
## (the two that collapsed stay struck out; the real line is drawn lit by the playout).
func _draw_candidates(mode: String = "plan", u: float = 0.0) -> void:
	var offs := _offsets()
	var cands: Array = model.raid_data()["cands"]
	var real := model.real()
	for i in range(cands.size()):
		var g := _geom(cands[i], offs[3 + i])
		var sh: int = model.shape(i)
		var full := float((g["pts"] as Array).size() + 1)
		var us := _stop_u(cands[i], g)
		var path := _path(g, us)
		var a: Vector2 = g["a"]
		var d: Vector2 = g["dir"]
		var is_real := i == real
		var col := Color8(104, 146, 255)
		var shimmer := 0.85 + 0.15 * sin(anim_t * 5.0 + i * 2.1)
		var cut := 1.0
		var alpha := 1.0
		var mark_x := false
		var lit := 0.0
		var badge := true
		match mode:
			"unseal":
				var s_end := L7Config.UNSEAL_SHIMMER_END
				var c_end := L7Config.UNSEAL_COLLAPSE_END
				shimmer = 0.5 + 0.5 * sin(anim_t * 16.0 + i * 2.1)
				if u >= s_end and not is_real:
					var k := clampf((u - s_end) / (c_end - s_end), 0.0, 1.0)
					cut = 1.0 - L7Config.ease_out(k)
					alpha = 1.0 - 0.5 * k
					mark_x = k > 0.55
					badge = false
				if u >= c_end and is_real:
					lit = clampf((u - c_end) / (1.0 - c_end), 0.0, 1.0)
			"revealed":
				if is_real:
					continue	## the playout draws the lit line and its badge
				cut = 0.0
				mark_x = true
				badge = false
		if cut > 0.001:
			var dc := Color(col.r, col.g, col.b, alpha * shimmer * (1.0 - 0.6 * lit))
			_draw_dashed_path(_trim(path, cut), dc, DASHES[sh], 4.0, anim_t * (70.0 if mode == "unseal" else 22.0))
			if us < full and cut > 0.99:
				_stop_bar(g, us, col)
		if lit > 0.0:
			var lp := _trim(path, lit)
			L7Draw.beam(self, lp, G.THREAT, 6.0, 1.2, false)
			L7Draw.glow(self, lp[lp.size() - 1], 34.0, G.THREAT_HOT, 0.8)
		G.cand_shape(self, a, sh, 11.0, col if not mark_x else G.THREAT_FADE, G.BG)
		if mark_x:
			G.cross(self, a, 12.0, G.DMG, 3.5)
		if badge and not (is_real and lit > 0.0):
			G.badge(self, a - d * 28.0, "?", G.THREAT)
		elif is_real and lit > 0.0:
			G.badge(self, a - d * 28.0, "2", G.THREAT)


## The hunter's rule on the grid: a thin dashed column with down chevrons and, at the first touch, an arrow that
## turns down that column. When the first touch depends on the sealed line, each line's column wears its shape.
func _draw_hunter_plan(fc: Array) -> void:
	var known_first := L5Rules.NONE
	for b: Dictionary in (fc[0]["beams"] as Array):
		if b["id"] in ["b2", "hunter"]:
			continue
		for stp: Dictionary in b["steps"]:
			if stp["kind"] in ["asset", "home", "decoy"]:
				known_first = stp["cell"]
				break
		if known_first != L5Rules.NONE:
			break
	if known_first != L5Rules.NONE:
		_hunter_col(known_first.x, G.THREAT_LIGHT, 3.0, "3", Vector2(10, 6), 0)
		G.turn_arrow(self, nx(known_first), 22.0, G.THREAT_LIGHT, 4.0, 1.0, -_h_off(known_first.x))
		return
	var own_needed := false
	var arrows: Array = []
	var shared := {}
	for f: Dictionary in _by_shape(fc):
		var sh: int = f["shape"]
		var fst: Vector2i = f["first"]
		if fst != L5Rules.NONE:
			var col := G.THREAT_LIGHT.darkened(0.25)
			var k: int = int(shared.get(fst.x, 0))
			shared[fst.x] = k + 1
			_hunter_col(fst.x, col, 2.0, "", DASHES[sh], k, sh)
			if not arrows.has(fst):
				arrows.append(fst)
				G.turn_arrow(self, nx(fst), 22.0, col, 3.0, 1.0, -_h_off(fst.x, k))
		else:
			own_needed = true
	if own_needed:
		var ox: int = (model.raid_data()["own3"][0] as Vector2i).x
		_hunter_col(ox, G.THREAT_LIGHT.darkened(0.45), 2.0, "3", Vector2(4, 8), 0)
		G.own_line(self, nx(Vector2i(ox, 0)) + Vector2(-_h_off(ox), -66.0), 6.0, G.THREAT_LIGHT.darkened(0.45))


func _hunter_col(x: int, col: Color, w: float, badge_s: String, dash: Vector2, k: int, shape_i: int = -1) -> void:
	var line := L5Rules.column(x)
	var g := _geom(line, _h_off(x, k))
	var full := float((g["pts"] as Array).size() + 1)
	var u := _stop_u(line, g)
	_draw_dashed_path(_path(g, u), col, dash, w)
	_column_chevrons(g, u, col)
	if u < full:
		_stop_bar(g, u, col)
	var b: Vector2 = g["b"]
	if shape_i >= 0:
		G.cand_shape(self, b + Vector2(0, 18), shape_i, 7.0, col, G.BG, 2.0)
	if badge_s != "":
		G.badge(self, _mid(g), badge_s)
		# The word the frames put at the column's end (the hunter's down chevron, then HUNTER).
		var tr := Rect2(b.x - 36.0, b.y + 10.0, 84.0, 19.0)
		G.panel(self, tr, G.THREAT, Color(0.02, 0.03, 0.09, 0.95), 1.0)
		G.chevron_down(self, Vector2(tr.position.x + 11.0, tr.position.y + 9.5), 4.0, G.THREAT_LIGHT, 2.0)
		G.text(self, Vector2(tr.position.x + 22.0, tr.position.y + 3.0), "HUNTER", 12, G.THREAT_LIGHT)


## Down chevrons between the rows of a hunter column, up to the path position u.
func _column_chevrons(g: Dictionary, u: float, col: Color) -> void:
	var pts: Array = g["pts"]
	for k in range(1, pts.size()):
		if u >= k + 1.0:
			G.chevron_down(self, ((pts[k - 1] as Vector2) + (pts[k] as Vector2)) * 0.5, 5.0, col, 2.0)


# ---- contact ----
func _band_chips(origin: Vector2, extra: int, dim: bool) -> void:
	var items: Array = ["1"]
	if extra >= 1:
		items.append("+")
	if extra >= 2:
		items.append("++")
	items.append("?")
	items.append("3")
	var x := origin.x
	for s: String in items:
		var col := G.THREAT_FADE if dim else G.THREAT
		if s == "?":
			_sealed_chip(Vector2(x, origin.y), G.THREAT_LIGHT if not dim else G.THREAT_FADE)
		else:
			G.badge(self, Vector2(x, origin.y), s, col)
		x += 40.0


func _draw_contact() -> void:
	var s := model.state
	var extra: int = L5Rules.extra_count(s.heat)
	_draw_known_beams(extra, false)
	_draw_net(false)
	# Raid strength by Heat band.
	G.text(self, Vector2(PANEL_X, 80), "THE RAID'S STRENGTH, BY HEAT", 14, G.DIM)
	var bands := [[0, "HEAT UNDER %d" % L5Config.EXTRA_AT, "Beam 1, a sealed beam, the hunter."],
		[1, "HEAT %d AND UP" % L5Config.EXTRA_AT, "Adds a known beam after beam 1."],
		[2, "HEAT %d AND UP" % L5Config.STRONG_AT, "Adds a second known beam."]]
	var y := 104.0
	for b in bands:
		var now: bool = int(b[0]) == extra
		var r := Rect2(PANEL_X, y, PANEL_W, 92)
		G.panel(self, r, G.CELL if now else G.PANEL_EDGE, G.PANEL, 3.0 if now else 2.0)
		G.text(self, Vector2(r.position.x + 16, y + 10), String(b[1]), 15, G.INK if now else G.DIM)
		if now:
			G.text_r(self, Vector2(r.end.x - 16, y + 10), "NOW  HEAT %d" % s.heat, 15, G.HEAT)
		_band_chips(Vector2(r.position.x + 36, y + 52), int(b[0]), not now)
		G.text(self, Vector2(r.position.x + 230, y + 44), String(b[2]), 12, G.INK if now else G.DIM)
		y += 102.0
	# Why: the cause chain at the bottom of the grid.
	_draw_cause_chain(s.heat, extra)
	if not model.run_note.is_empty():
		var rn := model.run_note
		G.text(self, Vector2(PANEL_X, 414), "Between raids: run %s" % String(rn["intensity"]), 14, G.DIM)
		G.flame(self, Vector2(PANEL_X + 10, 446), 9)
		G.text(self, Vector2(PANEL_X + 26, 435), "+%d" % int(rn["heat_add"]), 20, G.HEAT)
		G.coin(self, Vector2(PANEL_X + 110, 446), 9)
		G.text(self, Vector2(PANEL_X + 128, 435), "+%d" % int(rn["income"]), 20, G.CELL)
		var nx_s := 200.0
		if int(rn["repair_cost"]) > 0:
			G.text(self, Vector2(PANEL_X + nx_s, 438), "repair -%d" % int(rn["repair_cost"]), 14, G.DIM)
			nx_s += 96.0
		if String(rn["bought"]) != "":
			G.text(self, Vector2(PANEL_X + nx_s, 438), "bought %s -%d" % [rn["bought"], rn["buy_cost"]], 14, G.CLEAN)
	_draw_status_summary(Vector2(PANEL_X, 474))
	_draw_kit_tray(Rect2(PANEL_X, 530, PANEL_W, 38))
	_btn(Rect2(PANEL_X, 574, PANEL_W, 48), "PLAN THE DEFENSE  [Enter]", "next", true, 18)
	_draw_legend()


func _draw_status_summary(p: Vector2) -> void:
	var s := model.state
	G.text(self, Vector2(p.x, p.y), "THE NETWORK", 14, G.DIM)
	G.disc(self, p + Vector2(14, 40), 11, G.PANEL)
	G.circle(self, p + Vector2(14, 40), 11, G.CELL, 3.0)
	G.text(self, p + Vector2(32, 30), "%d OK" % s.count("OK"), 17, G.INK)
	G.disc(self, p + Vector2(120, 40), 11, GREY)
	G.bolt(self, p + Vector2(120, 40), 9.0)
	G.text(self, p + Vector2(138, 30), "%d DOWN" % s.count("DOWN"), 17, G.INK)
	G.corp(self, p + Vector2(240, 40), 11.0)
	G.text(self, p + Vector2(258, 30), "%d TAKEN" % s.count("TAKEN"), 17, G.INK)


func _draw_cause_chain(heat: int, extra: int) -> void:
	var y := 596.0
	G.flame(self, Vector2(60, y + 2), 14)
	G.text(self, Vector2(44, y + 20), "HEAT %d" % heat, 12, G.HEAT)
	G.arrow(self, Vector2(90, y), Vector2(150, y), G.HEAT, 4.0)
	for k in range(2):
		var at: int = L5Config.EXTRA_AT if k == 0 else L5Config.STRONG_AT
		var cx := 180.0 + k * 100.0
		var passed: bool = heat >= at
		G.shield(self, Vector2(cx, y - 2), 14, G.THREAT if passed else G.THREAT_FADE)
		G.text(self, Vector2(cx - 20, y + 20), "LINE %d" % at, 12, G.THREAT_LIGHT if passed else G.DIM)
	G.arrow(self, Vector2(400, y), Vector2(540, y), G.THREAT, 4.0)
	_band_chips(Vector2(574, y), extra, false)
	G.text(self, Vector2(556, y + 20), "%d KNOWN BEAM%s" % [1 + extra, "" if extra == 0 else "S"], 12, G.THREAT_LIGHT)


# ---- plan / forecast ----
func _draw_plan() -> void:
	var fc_mode: bool = phase == Phase.FORECAST
	var fc: Array = model.forecast()
	_draw_known_beams(model.extra_now(), true)
	_draw_candidates()
	_draw_hunter_plan(fc)
	_draw_net(true)	## the nodes sit over the beams, so a number or a pip is never struck through
	_draw_ghost_skips()
	# Words beside the placed levers, as in the frames (the glyphs and the 3D markers say it without them).
	for lv: Array in [["ghost", "GHOST"], ["decoys", "DECOY"], ["dark", "DARK"]]:
		for lc: Vector2i in model.plan[lv[0]]:
			_lever_tag(chip_at(lc), String(lv[1]))
	if fc_mode:
		_draw_forecast_marks(fc)
	if sel_lever != "":
		for c in L5Rules.nodes():
			var p := chip_at(c)
			if Rect2(p - Vector2(46, 46), Vector2(92, 92)).has_point(mouse):
				var ok := model.why_not(sel_lever, c) == ""
				G.circle(self, p, 40, G.CLEAN if ok else G.DMG, 3.0)
	_draw_kit_tray(Rect2(PANEL_X, 76, PANEL_W, 44), {"ghost": (model.plan["ghost"] as Array).size(), "decoy": (model.plan["decoys"] as Array).size(), "dark": (model.plan["dark"] as Array).size()})
	var y := 128.0
	for lv in L5Model.LEVERS:
		_draw_lever_card(lv, Rect2(PANEL_X, y, PANEL_W, 56))
		y += 60.0
	G.text(self, Vector2(PANEL_X + 4, y + 2), "Spoof (after the reveal): SKIP a node or JAM the hunter, +%d Heat." % L5Config.SPOOF_HEAT, 12, G.DIM)
	y += 24.0
	if fc_mode:
		_draw_forecast_panel(fc, y)
	else:
		_draw_strength_panel(y)
	_btn(Rect2(PANEL_X, 614, 120, 46), "UNDO [Z]", "undo", model.can_undo(), 16)
	if fc_mode:
		_btn(Rect2(PANEL_X + 134, 614, 90, 46), "BACK [B]", "back", true, 16)
		_btn(Rect2(PANEL_X + 238, 614, 222, 46), "LAUNCH SWEEP [Enter]", "launch", true, 17)
	else:
		_btn(Rect2(PANEL_X + 134, 614, 326, 46), "FORECAST [Enter]", "forecast", true, 18)
	_draw_breach_warning(fc)
	_draw_kit_strip()
	_draw_legend()


## A small word tag over a placed lever's chip (GHOST, DECOY, DARK), amber like the frames' lever labels.
func _lever_tag(p: Vector2, word: String) -> void:
	var w := G.text_w(word, 12) + 14.0
	var r := Rect2(p.x - w * 0.5, p.y - NODE_R - 27.0, w, 19.0)
	G.panel(self, r, G.HOLD, Color(0.02, 0.03, 0.09, 0.95), 1.0)
	G.text_c(self, r.get_center(), word, 12, G.CELL)


## PLAN / FORECAST: "kit after this raid" under the grid. The kit the plan leaves (ghosts, decoys, spoofs, go dark), the Heat
## the plan leaves against the Heat notches (50 and 75, each with the glyph of the beam it adds), and the next raid's beam
## count at that Heat plus the cheapest run (LOW). Amber when the plan spends the last kit item and the next raid will run
## more beams than this one. Only numbers the rules already produce (kit_left, extra_count).
func _draw_kit_strip() -> void:
	var pv := model.kit_after_preview()
	var last: bool = model.raid >= L5Config.RAIDS - 1
	var amber: bool = bool(pv["amber"]) and not last
	var r := Rect2(20, 576, 740, 66)
	G.panel(self, r, G.HOLD if amber else G.PANEL_EDGE, Color8(48, 34, 12) if amber else G.PANEL, 3.0 if amber else 2.0)
	G.text(self, Vector2(r.position.x + 12, r.position.y + 4), "KIT AFTER THIS RAID", 12, G.HOLD if amber else G.DIM)
	var kit: Dictionary = pv["kit"]
	for i in range(L5Config.KITS.size()):
		var kind: String = L5Config.KITS[i]
		var n: int = int(kit[kind])
		var x0 := r.position.x + 14 + i * 92.0
		var col: Color = KIT_COL[kind] if n > 0 else G.DIM
		_kit_icon(kind, Vector2(x0 + 10, r.position.y + 34), 9.0, col)
		G.text(self, Vector2(x0 + 26, r.position.y + 22), str(n), 20, G.INK if n > 0 else G.DMG)
		for k in range(n):
			draw_rect(Rect2(x0 + 46 + k * 7, r.position.y + 29, 5, 10), col)
	if last:
		G.text(self, Vector2(r.position.x + 12, r.position.y + 44), "The last raid of the leg.", 13, G.DIM)
		return
	var beams: int = int(pv["beams_next"])
	var levers: int = int(pv["levers_left"])
	var msg := "next raid: %d beam%s, %d lever%s left" % [beams, "" if beams == 1 else "s", levers, "" if levers == 1 else "s"]
	G.text(self, Vector2(r.position.x + 12, r.position.y + 44), msg, 14, G.HOLD if amber else G.INK)
	# The Heat the plan leaves against the notches.
	var mx := r.position.x + 392.0
	var mw := 330.0
	var my := r.position.y + 34.0
	var segs := 33
	for k in range(segs):
		var gc := G.heat_color((float(k) + 0.5) / segs)
		var sx := mx + mw * float(k) / segs
		var lit := (float(k) + 0.5) / segs * L5Config.HEAT_MAX <= float(pv["heat_leaves"])
		var nxt := (float(k) + 0.5) / segs * L5Config.HEAT_MAX <= float(pv["heat_next"])
		draw_rect(Rect2(sx, my, mw / segs + 0.5, 12), gc if lit else (gc.darkened(0.45) if nxt else Color(gc.r * 0.25, gc.g * 0.25, gc.b * 0.25)))
	draw_rect(Rect2(mx, my, mw, 12), G.PANEL_EDGE, false, 2.0)
	for band in [[L5Config.EXTRA_AT, "+"], [L5Config.STRONG_AT, "++"]]:
		var bxp: float = mx + mw * float(band[0]) / L5Config.HEAT_MAX
		var passed: bool = int(pv["heat_next"]) >= int(band[0])
		G.line(self, Vector2(bxp, my - 6), Vector2(bxp, my + 18), G.INK if passed else G.PANEL_EDGE, 4.0)
		G.badge(self, Vector2(bxp, my - 16), band[1], G.THREAT if passed else G.THREAT_FADE)
	var hxp: float = mx + mw * clampf(float(pv["heat_leaves"]) / L5Config.HEAT_MAX, 0.0, 1.0)
	G.flame(self, Vector2(hxp, my + 24), 7)
	G.text(self, Vector2(hxp + 11, my + 16), str(pv["heat_leaves"]), 13, G.HEAT)
	G.text_r(self, Vector2(mx - 8, my - 2), "Heat", 12, G.DIM)


func _draw_lever_card(lv: String, r: Rect2) -> void:
	var used: int = (model.plan[L5Model.ALLOC_KEY[lv]] as Array).size()
	var cap: int = {"ghost": mini(L5Config.MAX_GHOST, int(model.state.kit["ghost"])), "decoy": mini(L5Config.MAX_DECOY, int(model.state.kit["decoy"])), "dark": mini(L5Config.MAX_DARK, int(model.state.kit["dark"]))}[lv]
	var sel := sel_lever == lv
	G.panel(self, r, G.CELL if sel else G.PANEL_EDGE, Color8(60, 52, 24) if (sel or _hot(r)) else G.PANEL, 3.0 if sel else 2.0)
	_add_hit(r, "lever:" + lv)
	var c := Vector2(r.position.x + 38, r.position.y + 28)
	match lv:
		"ghost":
			G.dashed_ring(self, c, 18, G.CELL if used > 0 else G.DIM, 4.0)
		"decoy":
			G.diamond(self, c, 19, G.CELL if used > 0 else G.DIM)
		"dark":
			G.disc(self, c, 18, Color8(10, 10, 16))
			G.circle(self, c, 18, G.DIM, 3.0)
	var nm: Array = LEVER_TEXT[lv]
	G.head(self, Vector2(r.position.x + 74, r.position.y + 3), "%s  [%s]" % [nm[0], nm[2]], 17, G.INK)
	if used > 0:
		var pr := Rect2(r.end.x - 106.0, r.position.y + 7.0, 58.0, 16.0)
		draw_rect(pr, G.CLEAN)
		G.text_c(self, pr.get_center(), "PLACED", 11, G.BG)
	G.text(self, Vector2(r.position.x + 74, r.position.y + 22), nm[1], 12, G.DIM)
	var cx := r.position.x + 74
	var cy := r.position.y + 38
	match lv:
		"ghost":
			G.flame(self, Vector2(cx + 6, cy + 7), 7)
			G.text(self, Vector2(cx + 20, cy), "+%d Heat now (%d in the kit)" % [L5Config.GHOST_HEAT, int(model.state.kit["ghost"])], 13, G.HEAT)
		"decoy":
			G.text(self, Vector2(cx, cy), "free, from the kit (%d in it), up to %d a raid" % [int(model.state.kit["decoy"]), L5Config.MAX_DECOY], 13, G.CELL)
		"dark":
			var loss := 0
			for dc: Vector2i in model.plan["dark"]:
				if model.state.status[dc] == "OK":
					loss += L5Rules.idiv(int(model.values()[dc]), L5Config.INCOME_DIV)
			G.coin(self, Vector2(cx + 6, cy + 7), 6, G.DIM)
			G.line(self, Vector2(cx - 1, cy + 14), Vector2(cx + 13, cy), G.DMG, 3.0)
			G.text(self, Vector2(cx + 20, cy), "income lost: %d  (%d in the kit)" % [loss, int(model.state.kit["dark"])], 13, G.DIM)
	G.text_r(self, Vector2(r.end.x - 14, r.position.y + 6), "%d/%d" % [used, cap], 16, G.INK if used > 0 else G.DIM)


## PLAN: this raid's beams at the current Heat, and what the next band would add.
func _draw_strength_panel(y: float) -> void:
	var r := Rect2(PANEL_X, y, PANEL_W, 190)
	G.panel(self, r)
	var heat: int = model.heat_now()
	var extra: int = model.extra_now()
	G.text(self, Vector2(r.position.x + 16, y + 10), "THIS RAID'S BEAMS", 14, G.DIM)
	G.flame(self, Vector2(r.end.x - 70, y + 20), 9)
	G.text_r(self, Vector2(r.end.x - 16, y + 10), str(heat), 18, G.HEAT)
	_band_chips(Vector2(r.position.x + 36, y + 62), extra, false)
	var line1 := "Beam 1, a sealed beam, the hunter."
	if extra == 1:
		line1 = "Heat %d passed %d: a known beam (+) is added." % [heat, L5Config.EXTRA_AT]
	elif extra == 2:
		line1 = "Heat %d passed %d: two known beams (+ ++)." % [heat, L5Config.STRONG_AT]
	G.text(self, Vector2(r.position.x + 16, y + 94), line1, 13, G.INK)
	var nxt := ""
	if extra == 0:
		nxt = "%d more Heat adds a known beam." % (L5Config.EXTRA_AT - heat)
	elif extra == 1:
		nxt = "%d more Heat adds a second known beam." % (L5Config.STRONG_AT - heat)
	else:
		nxt = "Already at the strongest raid."
	G.text(self, Vector2(r.position.x + 16, y + 116), nxt, 13, G.DIM)
	if (model.plan["ghost"] as Array).size() > 0:
		var base_extra: int = L5Rules.extra_count(model.state.heat)
		if extra > base_extra:
			G.text(self, Vector2(r.position.x + 16, y + 142), "The ghost's +%d Heat added a beam." % L5Config.GHOST_HEAT, 13, G.HOLD)
		else:
			G.text(self, Vector2(r.position.x + 16, y + 142), "The ghost's +%d Heat adds no beam." % L5Config.GHOST_HEAT, 13, G.DIM)
	G.text(self, Vector2(r.position.x + 16, y + 164), "Beams: 1 known, + extra, ? sealed, 3 hunter.", 12, G.DIM)


## Small outcome chips for a summary. y is the center line; returns the x after the last chip.
func _chips(x: float, y: float, sm: Dictionary) -> float:
	var cx := x
	if not bool(sm["touched"]):
		G.check(self, Vector2(cx + 8, y), 7)
		G.text(self, Vector2(cx + 22, y - 8), "EVADED", 13, G.CLEAN)
		return cx + 86.0
	var shown := false
	if int(sm["down"]) > 0:
		G.disc(self, Vector2(cx + 9, y), 11, GREY)
		G.bolt(self, Vector2(cx + 9, y), 8.0)
		G.text(self, Vector2(cx + 24, y - 8), "x%d" % int(sm["down"]), 15)
		cx += 50.0
		shown = true
	if int(sm["taken"]) > 0:
		G.corp(self, Vector2(cx + 9, y), 10.0)
		G.text(self, Vector2(cx + 24, y - 8), "x%d" % int(sm["taken"]), 15)
		cx += 50.0
		shown = true
	if int(sm["home"]) > 0:
		G.home_server(self, Vector2(cx + 9, y), 8.0, G.DMG)
		if bool(sm["breach"]):
			G.text(self, Vector2(cx + 24, y - 8), "BREACH", 14, G.DMG)
			cx += 84.0
		else:
			G.text(self, Vector2(cx + 24, y - 8), "-%d" % int(sm["home"]), 15, G.DMG)
			cx += 50.0
		shown = true
	if not shown:
		G.diamond(self, Vector2(cx + 9, y), 10.0, G.CELL, 3.0)
		G.text(self, Vector2(cx + 26, y - 8), "DECOY ONLY", 12, G.DIM)
		cx += 100.0
	return cx


## The forecast lines in the fixed order triangle, square, circle (the candidate behind each shape changes per raid).
func _by_shape(fc: Array) -> Array:
	var out: Array = fc.duplicate()
	out.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return int(a["shape"]) < int(b["shape"]))
	return out


## Everything one forecast line costs: "2 DOWN, 1 TAKEN, HOME -1".
func _worst_s(sm: Dictionary) -> String:
	if bool(sm["breach"]):
		return "BREACH, the campaign is lost"
	var parts: Array = []
	if int(sm["down"]) > 0:
		parts.append("%d DOWN" % int(sm["down"]))
	if int(sm["taken"]) > 0:
		parts.append("%d TAKEN" % int(sm["taken"]))
	if int(sm["home"]) > 0:
		parts.append("HOME -%d" % int(sm["home"]))
	if parts.is_empty():
		return "a decoy only" if bool(sm["decoy"]) else "nothing touched"
	return ", ".join(parts)


func _draw_forecast_panel(fc: Array, y: float) -> void:
	var r := Rect2(PANEL_X, y, PANEL_W, 268)
	G.panel(self, r)
	var sv := L5Config.spoof_view()
	var can: bool = int(model.state.kit["spoof"]) > 0
	var x := r.position.x
	var rows := _by_shape(fc)
	G.text(self, Vector2(x + 14, y + 8), "IF YOU HOLD THE SPOOF", 12, G.DIM)
	if sv:
		G.skip_chevron(self, Vector2(x + 312, y + 15), 5.0, G.CLEAN, 2.0)
		G.text(self, Vector2(x + 330, y + 8), "SPOOF, BEST CASE", 12, G.CLEAN)
	for i in range(rows.size()):
		var ry := y + 30.0 + i * 62.0
		var f: Dictionary = rows[i]
		if i > 0:
			draw_line(Vector2(x + 12, ry - 4), Vector2(x + PANEL_W - 12, ry - 4), G.PANEL_EDGE, 1.0)
		G.cand_shape(self, Vector2(x + 28, ry + 16), int(f["shape"]), 11.0, G.THREAT_LIGHT, G.BG)
		_chips(x + 62, ry + 16, f["summary"])
		if not sv:
			continue
		G.arrow(self, Vector2(x + 262, ry + 16), Vector2(x + 300, ry + 16), G.DIM, 2.0, 7.0)
		if not f["can_spoof"]:
			G.text(self, Vector2(x + 312, ry + 8), "no spoof left", 13, G.DIM)
		elif f["saves"]:
			_chips(x + 312, ry + 16, f["floor_summary"])
		else:
			G.text(self, Vector2(x + 312, ry + 8), "no change", 12, G.DIM)
		# Which nodes a spoof could save (no pick is made for the player).
		G.skip_chevron(self, Vector2(x + 28, ry + 42), 5.0, G.CLEAN if (can and f["saves"]) else G.DIM, 2.0)
		var cells_s: Array = f["save_cells"]
		var jam_s: bool = f["jam_saves"]
		if cells_s.is_empty() and not jam_s:
			G.text(self, Vector2(x + 62, ry + 35), "no node to save" if can else "no spoof in the kit", 12, G.DIM)
		else:
			G.text(self, Vector2(x + 62, ry + 35), "could save:", 12, G.CLEAN)
			for k in range(cells_s.size()):
				_node_chip(Vector2(x + 168 + k * 30, ry + 42), cells_s[k], G.CLEAN)
			if jam_s:
				G.jam_mark(self, Vector2(x + 168 + cells_s.size() * 30, ry + 42), 10.0, G.CLEAN)
	var wl: Array = model.worst_home_loss()
	var wc: Dictionary = model.worst_case(fc)
	var hold_w: Dictionary = wc["hold"]
	var any_breach: bool = bool(hold_w["breach"])
	var py := y + 242.0
	G.text(self, Vector2(x + 14, py - 8), "HOME", 13, G.DIM)
	var hp: int = model.state.home_hp
	for k in range(L5Config.HOME_HP):
		var mode := "full"
		if k >= hp - int(wl[0]):
			mode = "saved" if (sv and can and k < hp - int(wl[1])) else "proj"
		G.pip(self, Vector2(x + 78 + k * 24, py), 14.0, mode)
	var lost_any: bool = int(hold_w["down"]) + int(hold_w["taken"]) + int(hold_w["home"]) > 0
	G.text(self, Vector2(x + 156, py - 16), "worst: " + _worst_s(hold_w), 13, G.DMG if any_breach else (G.INK if lost_any else G.DIM))
	if sv and can:
		G.text(self, Vector2(x + 156, py + 2), "with a spoof: " + _worst_s(wc["with_spoof"]), 13, G.CLEAN)


## The red warning when the forecast shows BREACH on every sealed line, even with the best spoof: it names the one
## lever that would avoid it (and rings its node), or says that none does. The playout still runs to the HOME touch.
func _draw_breach_warning(fc: Array) -> void:
	if not model.breach_certain(fc):
		return
	var key := "%d|%s" % [model.raid, str(model.plan)]
	if key != _bf_key:
		_bf_key = key
		_bf_val = model.breach_fix()
	var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 260.0)
	var r := Rect2(20, 78, 740, 56)
	G.panel(self, r, G.DMG, Color8(52, 10, 20), 4.0)
	var hc := Vector2(r.position.x + 32, r.position.y + 28)
	G.home_server(self, hc, 18.0, G.DMG, Color8(80, 12, 24))
	G.cross(self, hc, 9.0, G.DMG, 3.0)
	G.text(self, Vector2(r.position.x + 62, r.position.y + 11), "BREACH", 30, G.DMG)
	var tx := r.position.x + 214
	G.text(self, Vector2(tx, r.position.y + 7), "Every sealed line empties HOME, even with a spoof: the campaign is lost.", 13, G.INK)
	if _bf_val.is_empty():
		G.text(self, Vector2(tx, r.position.y + 32), "No lever left in the kit avoids it.", 13, G.DIM)
		return
	var parts: Array = []
	var x := tx
	for stp: Dictionary in (_bf_val["steps"] as Array):
		var lv: String = stp["lever"]
		var c: Vector2i = stp["cell"]
		var where := "HOME" if c == model.home() else ("the %d asset" % int(model.values()[c]) if model.values().has(c) else "an empty node")
		parts.append("%s on %s" % [{"ghost": "a GHOST", "dark": "GO DARK", "decoy": "a DECOY"}[lv], where])
		G.circle(self, chip_at(c), NODE_R + 14.0 + 3.0 * pulse, G.CLEAN, 4.0)
		_kit_icon(lv, Vector2(x + 8, r.position.y + 40), 6.0, G.CLEAN)
		x += 22.0
	G.text(self, Vector2(x + 2, r.position.y + 32), "Avoid it: %s (ringed)." % " and ".join(parts), 13, G.CLEAN)


## A sealed line's result at one cell as a small pill: the line's shape, then a glyph for what it does there (DOWN bolt,
## TAKEN corp flag, HOME with -1, a diamond for a decoy). Centered at p.
func _outcome_pill(p: Vector2, sh: int, outcome: String, edge: Color) -> void:
	var w := 54.0 if outcome == "HOME" else 42.0
	G.panel(self, Rect2(p.x - w * 0.5, p.y - 9.0, w, 18.0), edge, G.BG, 2.0)
	G.cand_shape(self, p + Vector2(-w * 0.5 + 10.0, 0), sh, 5.5, G.THREAT_LIGHT, G.BG, 2.0)
	var q := p + Vector2(-w * 0.5 + 27.0, 0)
	match outcome:
		"DOWN":
			G.disc(self, q, 7, GREY)
			G.bolt(self, q, 5.5)
		"TAKEN":
			G.corp(self, q, 7.0)
		"HOME":
			G.home_server(self, q, 5.5, G.DMG)
			G.text(self, q + Vector2(9, -7), "-1", 12, G.DMG)
		_:
			G.diamond(self, q, 5.5, G.CELL, 2.0)


## FORECAST: on each node, one slot per sealed line that touches it (shape = the line, glyph = the outcome); a lime
## spoof mark (the line's shape, then a skip-chevron) on every node a spoof could save for that line.
func _draw_forecast_marks(fc: Array) -> void:
	var sv := L5Config.spoof_view()
	var offs := _offsets()
	var rd: Dictionary = model.raid_data()
	var stack := {}
	for f: Dictionary in fc:
		var sh: int = f["shape"]
		var cand: Array = rd["cands"][int(f["cand"])]
		var g := _geom(cand, offs[3 + int(f["cand"])])
		var done: Array = []
		var touches: Array = f["touches"]
		var outs: Array = f["outcomes"]
		for i in range(outs.size()):
			var c: Vector2i = outs[i]["cell"]
			var beam: String = touches[i]["beam"]
			if done.has(c) or beam not in ["b2", "hunter"]:
				continue
			done.append(c)
			var p := nx(c)
			if beam == "b2":
				# On the sealed line itself: in its lane, just before the node it hits (after it for the line's first node).
				var d: Vector2 = g["dir"]
				var q: Vector2 = (g["pts"] as Array)[cand.find(c)]
				var vertical: bool = absf(d.y) > 0.5
				var rank: int = int(stack.get(c, 0))
				if vertical:
					stack[c] = rank + 1
				var back: float = NODE_R + 22.0 + (rank * 19.0 if vertical else 0.0)
				p = q - d * back if cand.find(c) > 0 else q + d * (NODE_R + 22.0 + (rank * 19.0 if vertical else 0.0))
				_outcome_pill(p, sh, String(outs[i]["outcome"]), G.THREAT_LIGHT)
			else:
				# The hunter's touch under this sealed line: below the node, in the hunter's column lane.
				p = Vector2(p.x - _h_off(c.x), p.y + NODE_R + 20.0 + sh * 19.0)
				_outcome_pill(p, sh, String(outs[i]["outcome"]), G.THREAT_FADE.lerp(G.THREAT_LIGHT, 0.5))
		if sv and f["can_spoof"]:
			for sc: Vector2i in f["save_cells"]:
				var q := chip_at(sc) + Vector2((sh - 1) * 40.0, -48.0)
				var chip := Rect2(q - Vector2(17, 11), Vector2(34, 22))
				G.panel(self, chip, G.CLEAN, G.BG, 2.0)
				G.cand_shape(self, q + Vector2(-8, 0), sh, 4.5, G.THREAT_LIGHT, Color(0, 0, 0, 0), 2.0)
				G.skip_chevron(self, q + Vector2(7, 0), 4.5, G.CLEAN, 2.0)


# ---- playout ----
func _beam_state(k: int, cur: int) -> String:
	if k < cur:
		return "done"
	if k == cur:
		return "now"
	return "later"


func _draw_play() -> void:
	var p := play
	var sn: Dictionary = p.status_now()
	var st: int = p.state
	var cur: int = p.order.size()
	if st in [L5Play.S.BEAM, L5Play.S.UNSEAL, L5Play.S.DECIDE, L5Play.S.NOTE, L5Play.S.TURN]:
		cur = p.beam_idx()
	var b2_i: int = p.order.find("b2")
	# Sealed candidates until beam 2 unseals; then the three shimmer, two collapse struck out, the real one ignites.
	if cur < b2_i:
		_draw_candidates("plan")
	elif st == L5Play.S.UNSEAL:
		var dur: float = L5Play.FAST_UNSEAL if p.fast else L7Config.UNSEAL_T
		_draw_candidates("unseal", clampf(p.t / dur, 0.0, 1.0))
	else:
		_draw_candidates("revealed")
	for k in range(p.res["beams"].size()):
		var b: Dictionary = p.res["beams"][k]
		var id: String = b["id"]
		if id == "hunter" and cur < k:
			continue
		if p.cut and k > p.last_beam():
			continue
		var bs := _beam_state(k, cur)
		var g := _beam_geom(id, b["line"])
		var u_full := _beam_u(b, g)
		if p.cut and k == p.last_beam():
			u_full = float(_beam_events(id))
		var badge_s := {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[id] as String
		if id == "b2":
			if cur < b2_i:
				continue
			var full_path := _path(g, float(g["pts"].size() + 1))
			if st == L5Play.S.UNSEAL:
				pass	## the candidates' ignite draws the line coming alight
			elif st in [L5Play.S.DECIDE, L5Play.S.NOTE]:
				# The real line stands lit end to end, breathing, while the response is open.
				L7Draw.beam(self, full_path, G.THREAT, 6.0, 1.1 + 0.25 * sin(anim_t * 7.0), true)
			elif bs == "now":
				var charging: bool = p.head() <= 0.0
				L7Draw.beam(self, full_path, G.THREAT, 6.0, (1.1 + 0.35 * sin(anim_t * 22.0)) if charging else 0.55, not charging)
				if not charging:
					var hp := _path(g, minf(p.head(), u_full))
					_draw_path(hp, G.THREAT_LIGHT, 8.0)
					L7Draw.glow(self, hp[hp.size() - 1], 34.0, G.THREAT_HOT, 0.9)
			else:
				_draw_path(_path(g, u_full), G.THREAT, 6.0)
		elif id == "hunter":
			if st == L5Play.S.TURN:
				_draw_hunter_turn(g, b)
			elif bs == "now":
				_draw_path(_path(g, float(g["pts"].size() + 1)), G.THREAT_FADE, 4.0, false)
				var hp := _path(g, minf(p.head(), u_full))
				_draw_path(hp, G.THREAT_LIGHT, 8.0)
				L7Draw.glow(self, hp[hp.size() - 1], 34.0, G.THREAT_HOT, 0.9)
			else:
				_draw_path(_path(g, u_full), G.THREAT, 5.0)
		else:
			match bs:
				"now":
					_draw_path(_path(g, u_full), G.THREAT_FADE, 4.0, false)
					# A beam glows at its pylon before the head moves; the head sweeps cell by cell.
					if p.head() <= 0.0:
						L7Draw.glow(self, g["a"], 26.0 + 6.0 * sin(anim_t * 20.0), G.THREAT_HOT, 0.8)
					else:
						var hp := _path(g, minf(p.head(), u_full))
						_draw_path(hp, G.THREAT_LIGHT, 8.0)
						L7Draw.glow(self, hp[hp.size() - 1], 34.0, G.THREAT_HOT, 0.9)
				"done":
					_draw_path(_path(g, u_full), G.THREAT, 6.0)
				_:
					_draw_path(_path(g, u_full), G.THREAT_FADE, 3.0, false)
		if id == "hunter":
			G.badge(self, _mid(g), badge_s)
		else:
			_start_badge(g, badge_s)
	_draw_touch_floor_fx()
	_draw_net_play(sn)	## the nodes sit over the beams
	_draw_touch_fx()
	# The hunter's rule stays on the grid from the turn on: an arrow from the first touch, turning down its column.
	var h_i: int = p.order.find("hunter")
	var hf: Vector2i = p.hunter_from()
	if h_i >= 0 and hf != L5Rules.NONE and cur >= h_i and not (p.cut and p.last_beam() < h_i):
		var prog := 1.0
		if st == L5Play.S.TURN:
			prog = clampf(p.t / L7Config.TURN_T * 1.5, 0.0, 1.0)
		G.turn_arrow(self, nx(hf), 22.0, G.THREAT_LIGHT, 5.0, prog, -_h_off(hf.x))
	if fast_play:
		_draw_fall_banner()
	elif not p.hunter_runs() and not p.cut:
		_draw_jam_chip(Vector2(20, 82))
	_draw_pick_fx()
	# The unseal's headline (frame 2): it lights as the real line ignites and stays while the response is open.
	if (st == L5Play.S.UNSEAL and p.t / (L5Play.FAST_UNSEAL if p.fast else L7Config.UNSEAL_T) >= L7Config.UNSEAL_COLLAPSE_END) or st in [L5Play.S.DECIDE, L5Play.S.NOTE]:
		_draw_headline("BEAM 2 UNSEALED")
	# The response after the reveal: the focused option's consequence on the grid, a SKIP target on every lit node, JAM pulsing.
	if st == L5Play.S.DECIDE:
		_draw_spoof_window()
		_draw_decision_preview()
	_draw_end_stamp()
	_draw_play_panel()


## A big glowing cobalt headline over the top-left of the board (Anton, the frames' "BEAM 2 UNSEALED").
func _draw_headline(word: String) -> void:
	var p := Vector2(24, 80)
	for off: Vector2 in [Vector2(-2, 0), Vector2(2, 0), Vector2(0, -2), Vector2(0, 2), Vector2(0, 0)]:
		G.text(self, p + off * 1.5, word, 38, Color(G.THREAT.r, G.THREAT.g, G.THREAT.b, 0.18), HORIZONTAL_ALIGNMENT_LEFT, -1.0, "head")
	G.text(self, p, word, 38, G.THREAT_HOT, HORIZONTAL_ALIGNMENT_LEFT, -1.0, "head")


func _pulse_col(e: Dictionary) -> Color:
	match e["outcome"]:
		"DOWN":
			return G.INK
		"TAKEN":
			return G.THREAT_LIGHT
		"HOME":
			return G.DMG
		"DECOY":
			return G.CELL
	match e["kind"]:
		"hidden":
			return G.INK
		"spoofed":
			return G.CLEAN
	return G.THREAT_HOT


## The geometry of the beam an event belongs to (the hunter's column comes from the resolved line).
func _geom_of_event(e: Dictionary) -> Dictionary:
	for b: Dictionary in play.res["beams"]:
		if b["id"] == e["beam"]:
			return _beam_geom(String(b["id"]), b["line"])
	return {}


## The point of a beam's lane over cell `c` (the lane's offset keeps it off the cell's center).
func _lane_point(g: Dictionary, c: Vector2i) -> Vector2:
	var best: Vector2 = nx(c)
	var bd := 1.0e9
	for gp: Vector2 in (g["pts"] as Array):
		var dd: float = gp.distance_to(nx(c))
		if dd < bd:
			bd = dd
			best = gp
	return best


## Under the nodes: a touched cell's hex ring on the floor lights and spreads (every cell a beam touches flashes), and a
## decoy pulls the beam aside.
func _draw_touch_floor_fx() -> void:
	for e: Dictionary in play.events:
		var age := _age(e)
		if age < 0.0 or age > L7Config.FLASH_T + L7Config.DECOY_PULL_T:
			continue
		var c: Vector2i = e["cell"]
		var col := _pulse_col(e)
		if age < L7Config.FLASH_T:
			var u: float = age / L7Config.FLASH_T
			L7Draw.floor_ring(self, c, 1.2 + 1.1 * u, Color(col.r, col.g, col.b, 1.0 - u), 4.0, 6)
			L7Draw.floor_ring(self, c, 1.05 + 0.5 * u, Color(col.r, col.g, col.b, 0.5 * (1.0 - u)), 9.0, 6)
		if e["outcome"] == "DECOY" and age < L7Config.DECOY_PULL_T + 0.3:
			var g := _geom_of_event(e)
			if not g.is_empty():
				var d: Vector2 = g["dir"]
				var tgt: Vector2 = _lane_point(g, c)
				var q := tgt - d * 82.0
				var u := clampf(age / L7Config.DECOY_PULL_T, 0.0, 1.0)
				var fade := 1.0 - clampf((age - L7Config.DECOY_PULL_T) / 0.3, 0.0, 1.0)
				for k in range(3):
					var bulge := (k - 1) * 22.0
					L7Draw.arc(self, q, tgt, bulge, Color(G.CELL.r, G.CELL.g, G.CELL.b, 0.85 * fade), 3.0, u)
				L7Draw.glow(self, tgt, 40.0 * u, G.CELL, 0.9 * fade)


## Over the nodes: the chip ring of a touch, the wrench dropping onto a node going DOWN.
func _draw_touch_fx() -> void:
	for e: Dictionary in play.events:
		var age := _age(e)
		if age < 0.0:
			continue
		var c: Vector2i = e["cell"]
		var col := _pulse_col(e)
		if age < L7Config.FLASH_T:
			var u: float = age / L7Config.FLASH_T
			G.circle(self, chip_at(c), NODE_R + 4.0 + u * 30.0, Color(col.r, col.g, col.b, 1.0 - u), 3.0)
		if e["outcome"] == "DOWN" and age < L7Config.WRENCH_T + 0.9:
			var a := 1.0 - clampf((age - L7Config.WRENCH_T - 0.4) / 0.5, 0.0, 1.0)
			L7Draw.wrench_token(self, chip_at(c) + Vector2(32, -20), age / L7Config.WRENCH_T, a)


## The spoof window: every node of the lit line is a SKIP target (lime brackets, pulsing, the skip badge) and JAM pulses on the
## hunter's column. A countdown ring runs in the response box but never forces a choice.
func _draw_spoof_window() -> void:
	var p := play
	var pulse := 0.5 + 0.5 * sin(anim_t * TAU / L7Config.PULSE_T)
	for c: Vector2i in p.b2:
		var pc := chip_at(c)
		L7Draw.brackets(self, pc, Vector2.ONE * (NODE_R + 9.0 + 3.0 * pulse), G.CLEAN, 3.0, 11.0)
		_spoof_mark(pc + SPOOF_OFF, 9.0 + 2.0 * pulse)
		_cell_hit(c)
		if dec_focus == c:
			var lr := Rect2(pc.x - 42.0, pc.y + NODE_R + 12.0, 84.0, 18.0)
			draw_rect(lr, G.CLEAN)
			G.text_c(self, lr.get_center(), "SKIP TARGET", 11, G.BG)
	var hb: Dictionary = p.hunter_beam()
	if not hb.is_empty():
		var g := _beam_geom("hunter", hb["line"])
		var m := _mid(g) + Vector2(0, 26)
		L7Draw.glow(self, m, 34.0 + 6.0 * pulse, G.CLEAN, 0.5)
		G.disc(self, m, 17.0, Color(G.BG.r, G.BG.g, G.BG.b, 0.95))
		G.circle(self, m, 17.0 + 2.0 * pulse, G.CLEAN, 3.0)
		G.jam_mark(self, m, 10.0, G.CLEAN)
		if dec_focus == L5Rules.JAM:
			var lr2 := Rect2(m.x - 42.0, m.y + 22.0, 84.0, 18.0)
			draw_rect(lr2, G.CLEAN)
			G.text_c(self, lr2.get_center(), "JAM TARGET", 11, G.BG)


## What the pick did: SKIP draws the bypass arc round the skipped node on beam 2; JAM strikes the hunter's turn out.
func _draw_pick_fx() -> void:
	var p := play
	if not p.spoof_used or fx.pick_at < 0.0:
		return
	var u := 1.0 if L7Config.instant else clampf((p.clock - fx.pick_at) / L7Config.PICK_FX_T, 0.0, 1.0)
	if p.spoof == L5Rules.JAM:
		var hb: Dictionary = p.hunter_beam()
		if hb.is_empty():
			return
		var g := _beam_geom("hunter", hb["line"])
		var dim := Color(G.THREAT_FADE.r + 0.1, G.THREAT_FADE.g + 0.1, G.THREAT_FADE.b + 0.2, 0.9)
		var first: Vector2i = p.hold_res["first"]
		_draw_dashed_path(_path(g, _beam_u(hb, g)), dim, Vector2(10, 6), 3.0, 0.0, false)
		if first != L5Rules.NONE:
			G.turn_arrow(self, nx(first), 22.0, dim, 3.0, 1.0, -_h_off(first.x))
		var m := _mid(g)
		var s1 := minf(1.0, u * 2.0)
		var s2 := clampf(u * 2.0 - 1.0, 0.0, 1.0)
		G.line(self, m + Vector2(-30, -30), m + Vector2(-30, -30).lerp(Vector2(30, 30), s1), G.DMG, 7.0)
		if s2 > 0.0:
			G.line(self, m + Vector2(-30, 30), m + Vector2(-30, 30).lerp(Vector2(30, -30), s2), G.DMG, 7.0)
	elif p.spoof != L5Rules.NONE:
		var g2 := _beam_geom("b2")
		var idx: int = p.b2.find(p.spoof)
		if idx < 0:
			return
		var q: Vector2 = (g2["pts"] as Array)[idx]
		var d: Vector2 = g2["dir"]
		var r := NODE_R + 6.0
		var a := q - d * r
		var b := q + d * r
		var n := Vector2(-d.y, d.x)
		var bulge := r * 1.1 if n.y < 0.0 else -r * 1.1
		L7Draw.arc(self, a, b, bulge, Color(G.CLEAN.r, G.CLEAN.g, G.CLEAN.b, 0.35), 9.0, u)
		L7Draw.arc(self, a, b, bulge, G.CLEAN, 4.0, u)


## The tier the sweep ends in, from the resolver's own result (the stamp slams before the aftermath settles the row).
func _tier_now() -> String:
	if play.cut:
		return "BREACHED"
	return L5Rules.tier(play.before, play.res["state"], (play.res["touches"] as Array).size())


## The stamp's words for a tier: [word, sub-line] (the rules' tier names, never the frames' "HOLDS" for a home hit).
func _stamp_words(tier: String, sm: Dictionary) -> Array:
	var parts: Array = []
	if int(sm["down"]) > 0:
		parts.append("%d DOWN" % int(sm["down"]))
	if int(sm["taken"]) > 0:
		parts.append("%d TAKEN" % int(sm["taken"]))
	if int(sm["home"]) > 0:
		parts.append("HOME -%d" % int(sm["home"]))
	var sub := "  ".join(parts)
	match tier:
		"EVADED":
			return ["EVADED", "nothing touched"]
		"HOLDS":
			return ["CELL HOLDS", sub if sub != "" else "a decoy took the beam"]
		"BATTERED":
			return ["CELL BATTERED", sub]
		"DAMAGED":
			return ["CELL DAMAGED", sub]
	return ["BREACHED", sub]


const STAMP_POS := Vector2(262, 588)
## True once this raid's stamp has landed on the board (the aftermath then shows it settled).
var _stamp_shown: bool = false


## The outcome stamp: it slams in at the end of the sweep (after a beat), and stays on the board into the aftermath.
func _draw_end_stamp() -> void:
	var p := play
	if not (p.state in [L5Play.S.END, L5Play.S.DONE]) or fx.end_at < 0.0:
		return
	var u := 1.0 if L7Config.instant else clampf((p.clock - fx.end_at - L7Config.STAMP_DELAY) / L7Config.STAMP_T, 0.0, 1.0)
	if u <= 0.0:
		return
	var tier := _tier_now()
	var words := _stamp_words(tier, L5Rules.summary(p.before, p.shown_touches() if p.cut else p.res["touches"]))
	G.stamp(self, STAMP_POS, String(words[0]), G.tier_color(tier), 34, String(words[1]), u)
	if u >= 0.99:
		_stamp_shown = true


func _draw_hunter_turn(g: Dictionary, b: Dictionary) -> void:
	var a3 := clampf(play.t / L7Config.TURN_T, 0.0, 1.0)
	var first: Vector2i = play.hunter_from()
	var col := Color(G.THREAT_LIGHT.r, G.THREAT_LIGHT.g, G.THREAT_LIGHT.b, a3)
	if first != L5Rules.NONE:
		var pf := nx(first)
		G.circle(self, pf, NODE_R + 8 + 6.0 * sin(play.t * 8.0), G.DMG, 4.0)
		_draw_dashed_path(_path(g, float(g["pts"].size() + 1)), col, Vector2(10, 6), 4.0, anim_t * 40.0)
		_column_chevrons(g, float(g["pts"].size() + 1), col)
	else:
		_draw_dashed_path(_path(g, float(g["pts"].size() + 1)), col, Vector2(4, 8), 4.0)
		G.own_line(self, (g["a"] as Vector2) + Vector2(0, -12.0), 7.0, Color(G.INK.r, G.INK.g, G.INK.b, a3))


## The decision screen's focused option on the grid: the hunter's column and turn, and for JAM the same turn struck out.
func _draw_decision_preview() -> void:
	if dec_focus == NO_FOCUS:
		return
	var foc := dec_focus
	var jam := foc == L5Rules.JAM
	var pr: Dictionary = play.hold_res if jam else play.preview(foc)
	if foc != L5Rules.NONE and not jam:
		G.circle(self, chip_at(foc), NODE_R + 12.0, G.CLEAN, 4.0)
	var hb: Dictionary = {}
	for b: Dictionary in pr["beams"]:
		if b["id"] == "hunter":
			hb = b
	if hb.is_empty():
		return
	var g := _beam_geom("hunter", hb["line"])
	var col: Color = G.THREAT_FADE if jam else G.THREAT_LIGHT
	_draw_dashed_path(_path(g, _beam_u(hb, g)), col, Vector2(10, 6), 4.0)
	_column_chevrons(g, _beam_u(hb, g), col)
	var first: Vector2i = pr["first"]
	if first != L5Rules.NONE:
		G.turn_arrow(self, nx(first), 22.0, col, 4.0, 1.0, -_h_off(first.x))
	else:
		G.own_line(self, (g["a"] as Vector2) + Vector2(0, -12.0), 7.0, col)
	G.badge(self, _mid(g), "3", col.darkened(0.3) if jam else G.THREAT)
	if jam:
		var m := _mid(g)
		G.line(self, m + Vector2(-30, -30), m + Vector2(30, 30), G.DMG, 6.0)
		G.line(self, m + Vector2(-30, 30), m + Vector2(30, -30), G.DMG, 6.0)


## The banner over the grid while a settled breach plays out.
func _draw_fall_banner() -> void:
	var r := Rect2(20, 80, 740, 46)
	G.panel(self, r, G.DMG, Color8(52, 10, 20), 3.0)
	var hc := Vector2(r.position.x + 30, r.position.y + 23)
	G.home_server(self, hc, 16.0, G.DMG, Color8(80, 12, 24))
	G.cross(self, hc, 8.0, G.DMG, 3.0)
	G.text(self, Vector2(r.position.x + 62, r.position.y + 6), "THE CELL FALLS", 28, G.DMG)


## The "JAM" chip shown on the grid while the hunter is stopped.
func _draw_jam_chip(p: Vector2) -> void:
	G.panel(self, Rect2(p, Vector2(262, 30)), G.CLEAN, G.BG, 2.0)
	G.jam_mark(self, p + Vector2(18, 15), 10.0, G.CLEAN)
	G.text(self, p + Vector2(38, 6), "JAM: the hunter does not run", 14, G.CLEAN)


## Nodes during the sweep: the statuses as the sweep has left them; hidden near misses keep a ring.
func _draw_net_play(sn: Dictionary) -> void:
	for c in L5Rules.nodes():
		_draw_node(c, sn["status"], int(sn["home_hp"]), play.alloc)
	for e: Dictionary in play.events:
		if e["kind"] == "hidden":
			G.circle(self, chip_at(e["cell"]), NODE_R + 10, G.INK, 2.0)
	if play.spoof_used and play.spoof != L5Rules.JAM and play.state != L5Play.S.DECIDE:
		_spoof_mark(chip_at(play.spoof) + SPOOF_OFF, 9.0)


func _draw_play_panel() -> void:
	var p := play
	G.text(self, Vector2(PANEL_X, 78), "SWEEP", 14, G.DIM)
	# Beam track.
	var cur := -1
	if p.state in [L5Play.S.BEAM, L5Play.S.UNSEAL, L5Play.S.DECIDE, L5Play.S.NOTE, L5Play.S.TURN]:
		cur = p.beam_idx()
	elif p.cut:
		cur = p.last_beam() + 1
	var ids: Array = p.order
	for i in range(ids.size()):
		var c := Vector2(PANEL_X + 24 + i * 56, 114)
		var done: bool = i < cur or cur < 0
		var active: bool = i == cur and not p.cut
		var s: String = {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[ids[i]]
		G.disc(self, c, 17, G.THREAT if (done or active) else G.PANEL)
		G.circle(self, c, 17, G.CELL if active else G.PANEL_EDGE, 3.0 if active else 2.0)
		if s == "+" or s == "++":
			G.beam_plus(self, c, s.length(), G.THREAT if (done or active) else G.PANEL)
		else:
			G.text_c(self, c, s, 17, G.INK)
		if i < ids.size() - 1:
			G.line(self, c + Vector2(22, 0), c + Vector2(34, 0), G.THREAT if done else G.PANEL_EDGE, 3.0)
	var name_x := PANEL_X + 24 + ids.size() * 56 + 6
	if not p.hunter_runs():
		# JAM: the hunter's beam 3 is struck out of the track.
		var c3 := Vector2(PANEL_X + 24 + ids.size() * 56, 114)
		G.disc(self, c3, 17, G.PANEL)
		G.circle(self, c3, 17, G.PANEL_EDGE, 2.0)
		G.text_c(self, c3, "3", 17, G.DIM)
		G.line(self, c3 + Vector2(-14, 14), c3 + Vector2(14, -14), G.DMG, 4.0)
		name_x += 50.0
	G.text(self, Vector2(name_x, 104), _beat_name(), 14, G.INK)
	# Speed controls.
	var labels := ["1x", "2x", "4x"]
	for i in range(0 if fast_play else 3):
		var r := Rect2(PANEL_X + i * 84, 144, 76, 36)
		G.panel(self, r, G.CELL if speed_i == i else G.PANEL_EDGE, Color8(60, 52, 24) if (speed_i == i or _hot(r)) else G.PANEL, 3.0 if speed_i == i else 2.0)
		G.text_c(self, r.get_center(), labels[i], 17, G.CELL if speed_i == i else G.INK)
		_add_hit(r, "speed:%d" % i)
	if not fast_play:
		var rs := Rect2(PANEL_X + 252, 144, 100, 36)
		G.panel(self, rs, G.PANEL_EDGE, Color8(60, 52, 24) if _hot(rs) else G.PANEL, 2.0)
		G.text_c(self, rs.get_center(), "SKIP [S]", 15, G.INK)
		_add_hit(rs, "skip")
		var ri := Rect2(PANEL_X + 360, 144, 100, 36)
		var inst := L7Config.instant
		G.panel(self, ri, G.CELL if inst else G.PANEL_EDGE, Color8(60, 52, 24) if (inst or _hot(ri)) else G.PANEL, 3.0 if inst else 2.0)
		G.text_c(self, ri.get_center(), "INSTANT [I]", 14, G.CELL if inst else G.INK)
		_add_hit(ri, "instant")
	if p.state == L5Play.S.DECIDE:
		_draw_response_box(Rect2(PANEL_X, 188, PANEL_W, 410))
	else:
		dec_focus = NO_FOCUS
		if fast_play:
			_draw_fast_box(Rect2(PANEL_X, 194, PANEL_W, 226))
		else:
			_draw_spoof_box(Rect2(PANEL_X, 194, PANEL_W, 226))
		_draw_hit_log(432.0)


## The note box of a settled breach's fast playout: the raid runs with no levers and no response, and nothing could stop it.
func _draw_fast_box(box: Rect2) -> void:
	G.panel(self, box, G.DMG, Color8(52, 10, 20), 3.0)
	var hc := Vector2(box.position.x + 40, box.position.y + 40)
	G.home_server(self, hc, 20.0, G.DMG, Color8(80, 12, 24))
	G.cross(self, hc, 10.0, G.DMG, 3.0)
	G.text(self, Vector2(box.position.x + 82, box.position.y + 18), "THE CELL FALLS", 22, G.DMG)
	G.text(self, Vector2(box.position.x + 20, box.position.y + 84), "Decided between the raids: every plan and every", 14, G.INK)
	G.text(self, Vector2(box.position.x + 20, box.position.y + 106), "response loses HOME on all three sealed lines.", 14, G.INK)
	G.text(self, Vector2(box.position.x + 20, box.position.y + 140), "The sweep plays at once, one beat per beam.", 13, G.DIM)


## The "Heat a -> b" line of one response, with what moved it and any Heat line it crosses. Returns the x after the text.
func _heat_line(x: float, y: float, heat_run: int, heat_after: int, spoof_heat: int, evaded: bool, up: Array, down: Array) -> float:
	G.flame(self, Vector2(x + 7, y + 8), 7)
	var s := "Heat %d -> %d" % [heat_run, heat_after]
	G.text(self, Vector2(x + 20, y), s, 13, G.HEAT)
	var cx := x + 20.0 + G.text_w(s, 13) + 8.0
	var why: Array = []
	if evaded:
		why.append("evaded -%d" % L5Config.EVADE_HEAT)
	if spoof_heat > 0:
		why.append("spoof +%d" % spoof_heat)
	if not why.is_empty():
		var w := "(%s)" % ", ".join(why)
		G.text(self, Vector2(cx, y), w, 12, G.HOLD if spoof_heat > 0 else G.CLEAN)
		cx += G.text_w(w, 12) + 8.0
	for ln: int in up:
		var u := "crosses %d: +1 beam" % ln
		G.text(self, Vector2(cx, y), u, 12, G.DMG)
		cx += G.text_w(u, 12) + 8.0
	for ln: int in down:
		var d := "under %d again" % ln
		G.text(self, Vector2(cx, y), d, 12, G.CLEAN)
		cx += G.text_w(d, 12) + 8.0
	return cx


## The decision screen after the reveal: HOLD, a SKIP per node of the lit line and JAM side by side, each with its result
## (what goes DOWN or TAKEN, HOME) and the Heat after it, +SPOOF_HEAT included. Nothing is highlighted as best.
func _draw_response_box(box: Rect2) -> void:
	var p := play
	G.panel(self, box, G.CLEAN, G.PANEL, 3.0)
	G.spoof_key(self, Vector2(box.position.x + 40, box.position.y + 22), G.CLEAN)
	G.text(self, Vector2(box.position.x + 82, box.position.y + 4), "AFTER THE REVEAL: PICK ONE", 16, G.CLEAN)
	var remain := 1.0 if (fx.decide_at < 0.0 or L7Config.instant) else clampf(1.0 - (p.clock - fx.decide_at) / L7Config.DECIDE_RING_T, 0.0, 1.0)
	L7Draw.countdown_ring(self, Vector2(box.end.x - 36, box.position.y + 28), 19.0, remain, G.CLEAN, str(int(p.before.kit["spoof"])))
	L7Draw.drain_bar(self, Rect2(box.position.x + 8, box.position.y + 52, box.size.x - 16, 3), remain, G.CLEAN)
	G.text(self, Vector2(box.position.x + 82, box.position.y + 28), "SKIP or JAM costs +%d Heat after the sweep." % L5Config.SPOOF_HEAT, 12, G.DIM)
	var hovered := NO_FOCUS
	var ry := box.position.y + 56.0
	for o: Dictionary in p.options():
		var c: Vector2i = o["cell"]
		var r := Rect2(box.position.x + 8, ry, box.size.x - 16, 48)
		var hot := _hot(r)
		if hot:
			hovered = c
		var lit: bool = hot or (hovered == NO_FOCUS and dec_pin == c)
		G.panel(self, r, G.CLEAN if lit else G.PANEL_EDGE, Color8(40, 56, 70) if lit else G.BG, 3.0 if lit else 2.0)
		var hit_id := "hold"
		if o["kind"] == "jam":
			hit_id = "jam"
		elif o["kind"] == "skip":
			hit_id = "cell:%d,%d" % [c.x, c.y]
		_add_hit(r, hit_id)
		var cy := r.position.y + 15.0
		var x0 := r.position.x + 10.0
		match o["kind"]:
			"hold":
				G.text(self, Vector2(x0, cy - 9), "HOLD [H]", 14, G.INK)
			"skip":
				_node_chip(Vector2(x0 + 12, cy), c, G.CLEAN)
				G.skip_chevron(self, Vector2(x0 + 46, cy), 6.0, G.CLEAN, 2.0)
				G.text(self, Vector2(x0 + 66, cy - 8), "SKIP", 12, G.DIM)
			_:
				G.jam_mark(self, Vector2(x0 + 12, cy), 11.0, G.CLEAN)
				G.text(self, Vector2(x0 + 32, cy - 9), "JAM [J]", 14, G.INK)
		_chips(r.position.x + 124, cy, o["summary"])
		_heat_line(r.position.x + 10, r.position.y + 29, int(o["heat_run"]), int(o["heat_after"]), int(o["spoof_heat"]),
			not bool((o["summary"] as Dictionary)["touched"]), o["up"], o["down"])
		ry += 52.0
	dec_focus = hovered if hovered != NO_FOCUS else dec_pin
	G.text(self, Vector2(box.position.x + 16, box.end.y - 22), "Click a row or a lit node. H holds, J jams.", 12, G.DIM)


## The spoof box outside the decision: what happened to the spoof (used as SKIP or JAM, held, none left, cut by the breach).
func _draw_spoof_box(box: Rect2) -> void:
	var p := play
	var noting := p.state == L5Play.S.NOTE
	G.panel(self, box, G.CLEAN if noting else G.PANEL_EDGE, G.PANEL, 3.0 if noting else 2.0)
	var kc := Vector2(box.position.x + 40, box.position.y + 24)
	G.spoof_key(self, kc, G.CLEAN if p.can_spoof else G.DIM)
	if not p.can_spoof:
		G.line(self, kc + Vector2(-26, 14), kc + Vector2(26, -14), G.DMG, 3.0)
	G.text(self, Vector2(box.position.x + 82, box.position.y + 6), "SPOOF", 17, G.CLEAN if p.can_spoof else G.DIM)
	G.text_r(self, Vector2(box.end.x - 16, box.position.y + 8), "%d in the kit" % int(p.before.kit["spoof"]), 14, G.DIM)
	var x0 := box.position.x + 16
	var y := box.position.y
	if p.spoof_used:
		var sm2 := L5Rules.summary(p.before, p.res["touches"])
		if p.spoof == L5Rules.JAM:
			G.jam_mark(self, Vector2(x0 + 12, y + 56), 11.0, G.CLEAN)
			G.text(self, Vector2(x0 + 34, y + 46), "Used: JAM. The hunter does not run.", 13, G.CLEAN)
		else:
			G.skip_chevron(self, Vector2(x0 + 12, y + 56), 7.0, G.CLEAN, 2.5)
			G.text(self, Vector2(x0 + 34, y + 46), "Used: SKIP. Beam 2 skips the marked node.", 13, G.CLEAN)
		G.text(self, Vector2(x0, y + 72), "Result with it:", 13, G.DIM)
		_chips(x0 + 120, y + 80, sm2)
		_heat_line(x0, y + 104, p.run_heat, (p.res["state"] as L5State).heat, L5Config.SPOOF_HEAT, not bool(sm2["touched"]), [], [])
	elif p.cut:
		G.text(self, Vector2(x0, y + 46), "HOME fell before any decision. The sweep ends.", 13, G.DMG)
		if p.can_spoof:
			G.text(self, Vector2(x0, y + 72), "The spoof stays in the kit.", 13, G.DIM)
	elif not p.can_spoof:
		G.text(self, Vector2(x0, y + 46), "No spoof left in the kit.", 15, G.INK if noting else G.DIM)
		G.text(self, Vector2(x0, y + 72), "Nothing to decide: the sweep goes on.", 13, G.DIM)
	elif p.state == L5Play.S.UNSEAL or (p.state == L5Play.S.BEAM and p.order.find("b2") > p.beam_idx()):
		G.text(self, Vector2(x0, y + 46), "Held: decide after the reveal.", 13, G.DIM)
	else:
		G.text(self, Vector2(x0, y + 46), "Held: not used, it stays in the kit.", 13, G.DIM)


func _draw_hit_log(y: float) -> void:
	G.text(self, Vector2(PANEL_X, y), "WHAT THE BEAMS TOUCHED", 14, G.DIM)
	var shown := 0
	var ys := y + 26.0
	var touches: Array = []
	for e: Dictionary in play.events:
		if e["outcome"] != "":
			touches.append(e)
	if touches.is_empty():
		G.check(self, Vector2(PANEL_X + 14, ys + 10), 8, G.DIM)
		G.text(self, Vector2(PANEL_X + 34, ys), "nothing yet", 15, G.DIM)
		return
	for e: Dictionary in touches.slice(maxi(0, touches.size() - 7)):
		var c := Vector2(PANEL_X + 16, ys + 11)
		match e["outcome"]:
			"DOWN":
				G.disc(self, c, 10, GREY)
				G.bolt(self, c, 8.0)
				G.text(self, Vector2(PANEL_X + 38, ys), "an asset goes DOWN", 15, G.INK)
			"TAKEN":
				G.corp(self, c, 10.0)
				G.text(self, Vector2(PANEL_X + 38, ys), "an asset is TAKEN", 15, G.THREAT_LIGHT)
			"HOME":
				G.home_server(self, c, 8.0, G.DMG)
				G.text(self, Vector2(PANEL_X + 38, ys), "HOME integrity -1", 15, G.DMG)
			_:
				draw_polyline(PackedVector2Array([c + Vector2(0, -9), c + Vector2(9, 0), c + Vector2(0, 9), c + Vector2(-9, 0), c + Vector2(0, -9)]), G.CELL, 2.5, true)
				G.text(self, Vector2(PANEL_X + 38, ys), "a decoy stops the beam", 15, G.CELL)
		G.text_r(self, Vector2(PANEL_X + PANEL_W - 10, ys + 2), {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[e["beam"]], 14, G.DIM)
		ys += 25.0
		shown += 1


func _beat_name() -> String:
	if play.cut and play.state in [L5Play.S.END, L5Play.S.DONE]:
		return "HOME BREACHED"
	match play.state:
		L5Play.S.BEAM:
			return {"b1": "BEAM 1", "extra": "KNOWN BEAM +", "extra2": "KNOWN BEAM ++", "b2": "BEAM 2", "hunter": "THE HUNTER"}[play.order[play.bi]]
		L5Play.S.UNSEAL:
			return "BEAM 2 UNSEALS"
		L5Play.S.DECIDE:
			return "HOLD, SKIP OR JAM"
		L5Play.S.NOTE:
			return "NO SPOOF LEFT"
		L5Play.S.TURN:
			return "THE HUNTER TURNS"
	return "DONE"


# ---- aftermath ----
## A tag stamped on a node: glyph + short word.
func _node_tag(c: Vector2i, kind: String) -> void:
	var p := chip_at(c) + Vector2(-46, 34)
	var r := Rect2(p.x, p.y, 92, 22)
	var col := G.INK
	match kind:
		"DOWN":
			col = G.INK
		"TAKEN":
			col = G.THREAT_LIGHT
		"HOME":
			col = G.DMG
	G.panel(self, r, col, Color8(14, 16, 32, 230), 2.0)
	var gc := Vector2(r.position.x + 13, r.position.y + 11)
	match kind:
		"DOWN":
			G.bolt(self, gc, 8.0)
			G.text(self, Vector2(r.position.x + 26, r.position.y + 3), "DOWN", 13, col)
		"TAKEN":
			G.corp(self, gc, 8.0)
			G.text(self, Vector2(r.position.x + 26, r.position.y + 3), "TAKEN", 13, col)
		"HOME":
			G.home_server(self, gc, 7.0, G.DMG)
			G.text(self, Vector2(r.position.x + 26, r.position.y + 3), "HOME -1", 13, col)
		_:
			G.diamond(self, gc, 8.0, G.CELL, 2.0)
			G.text(self, Vector2(r.position.x + 26, r.position.y + 3), "DECOY", 13, G.CELL)


func _draw_after() -> void:
	var after: L5State = row["after_raid"]
	for b: Dictionary in row["beams"]:
		var g := _beam_geom(b["id"], b["line"])
		_draw_path(_path(g, _beam_u(b, g)), G.THREAT_FADE.lerp(G.THREAT, 0.5), 4.0)
		var badge_s := {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[b["id"]] as String
		if b["id"] == "hunter":
			G.badge(self, _mid(g), badge_s)
		else:
			_start_badge(g, badge_s)
	_draw_net(false, after.status, after.home_hp, row["alloc"])
	var hunter_ran := false
	for b: Dictionary in row["beams"]:
		hunter_ran = hunter_ran or b["id"] == "hunter"
	if hunter_ran and row["first"] != L5Rules.NONE:
		G.turn_arrow(self, nx(row["first"]), 22.0, G.THREAT_LIGHT, 5.0, 1.0, -_h_off((row["first"] as Vector2i).x))
	elif row["spoof"] == L5Rules.JAM:
		_draw_jam_chip(Vector2(20, 82))
	var done: Array = []
	for o: Dictionary in row["outcomes"]:
		if not done.has(o["cell"]):
			done.append(o["cell"])
			_node_tag(o["cell"], o["outcome"])
	if row["spoof"] != L5Rules.NONE and row["spoof"] != L5Rules.JAM:
		_spoof_mark(chip_at(row["spoof"]) + SPOOF_OFF, 9.0)
	var sm: Dictionary = row["summary"]
	var tier: String = row["tier"]
	var col := G.tier_color(tier)
	var words := _stamp_words(tier, sm)
	# The stamp stays where the sweep slammed it on the board (it slams here only when the sweep was skipped past its end).
	var su := 1.0 if (_stamp_shown or L7Config.instant) else clampf((screen_t() - L7Config.STAMP_DELAY) / L7Config.STAMP_T, 0.0, 1.0)
	G.stamp(self, STAMP_POS, String(words[0]), col, 34, String(words[1]), su)
	var hb := Rect2(PANEL_X, 84, PANEL_W, 92)
	G.panel(self, hb, col, G.PANEL, 3.0)
	G.text(self, hb.position + Vector2(18, 8), String(words[0]), 40, col)
	G.text(self, hb.position + Vector2(20, 58), String(words[1]), 20, G.INK, HORIZONTAL_ALIGNMENT_LEFT, -1.0, "head")
	_draw_ledger(row["ledger"])
	var last := model.leg_over()
	_btn(Rect2(PANEL_X, 628, PANEL_W, 40), ("LEG RECORD  [Enter]" if last else "BETWEEN RAIDS  [Enter]"), "next", true, 18)
	_draw_legend()


func _ledger_row(y: float, label: String, amount: String, col: Color, glyph: String = "") -> void:
	_lrow(PANEL_X + 20, PANEL_X + PANEL_W - 20, y, label, amount, col)
	match glyph:
		"coin":
			G.coin(self, Vector2(PANEL_X + 320, y + 9), 7, col)
		"flame":
			G.flame(self, Vector2(PANEL_X + 320, y + 10), 7, col)


func _draw_ledger(l: Dictionary) -> void:
	G.panel(self, Rect2(PANEL_X, 190, PANEL_W, 430))
	var y := 200.0
	# The kit: before -> after, per item.
	G.text(self, Vector2(PANEL_X + 20, y), "KIT  (the raid took from it; Schematics stay %d)" % int(l["bank"]), 13, G.DIM)
	y += 24.0
	for i in range(L5Config.KITS.size()):
		var kind: String = L5Config.KITS[i]
		var x0 := PANEL_X + 20 + i * 108.0
		var cy := y + 12
		_kit_icon(kind, Vector2(x0 + 11, cy), 10.0, KIT_COL[kind])
		var used: int = int(l["kit_used"][kind])
		G.text(self, Vector2(x0 + 30, cy - 9), "%d -> %d" % [int(l["kit_before"][kind]), int(l["kit_after"][kind])], 16, G.INK if used == 0 else G.HOLD)
	y += 40.0
	G.flame(self, Vector2(PANEL_X + 28, y + 10), 10)
	G.text(self, Vector2(PANEL_X + 50, y), "HEAT", 15, G.DIM)
	y += 26.0
	_ledger_row(y, "BEFORE", str(l["heat_before"]), G.INK, "flame")
	y += 24.0
	if int(l["ghost"]) > 0:
		_ledger_row(y, "GHOST", "+%d" % int(l["ghost"]), G.HOLD, "flame")
		y += 24.0
	if int(l["evade"]) > 0:
		_ledger_row(y, "EVADED", "-%d" % int(l["evade"]), G.CLEAN, "flame")
		y += 24.0
	if int(l["spoof_heat"]) > 0:
		_ledger_row(y, "SPOOF  (%s)" % String(l["spoof_kind"]), "+%d" % int(l["spoof_heat"]), G.HOLD, "flame")
		y += 24.0
	draw_line(Vector2(PANEL_X + 20, y + 2), Vector2(PANEL_X + PANEL_W - 20, y + 2), G.PANEL_EDGE, 2.0)
	y += 6.0
	_ledger_row(y, "AFTER THE RAID", str(l["heat_after"]), G.HEAT, "flame")
	y += 28.0
	G.text(self, Vector2(PANEL_X + 20, y), "The sweep ran at Heat %d: %d known beam%s." % [l["run_heat"], 1 + int(l["extra"]), "" if int(l["extra"]) == 0 else "s"], 12, G.DIM)
	y += 26.0
	G.home_server(self, Vector2(PANEL_X + 28, y + 12), 9.0, G.INK)
	G.text(self, Vector2(PANEL_X + 50, y), "HOME", 15, G.DIM)
	for k in range(L5Config.HOME_HP):
		var mode := "full" if k < int(l["home_after"]) else "lost"
		G.pip(self, Vector2(PANEL_X + 150 + k * 28, y + 10), 18.0, mode)
	G.text_r(self, Vector2(PANEL_X + PANEL_W - 20, y), "%d -> %d" % [l["home_before"], l["home_after"]], 17, G.DMG if int(l["home_lost"]) > 0 else G.INK)
	y += 34.0
	var after: L5State = row["after_raid"]
	G.text(self, Vector2(PANEL_X + 20, y), "Network: %d OK, %d DOWN, %d TAKEN" % [after.count("OK"), after.count("DOWN"), after.count("TAKEN")], 14, G.INK)
	y += 24.0
	if model.breached:
		G.text(self, Vector2(PANEL_X + 20, y), "The campaign is lost.", 14, G.DMG)
		return
	G.text(self, Vector2(PANEL_X + 20, y), "Assets kept now: %d" % L5Rules.assets_kept(model.leg, after), 14, G.INK)
	y += 24.0
	y = _formula(after, PANEL_X + 20, y, "Leg value now")
	G.text(self, Vector2(PANEL_X + 20, y), _carried_s(int(l["carried"])) + "  (Heat above %d counts against the leg)" % L5Config.START_HEAT, 12, G.HEAT if int(l["carried"]) > 0 else G.DIM)


## The leg value with every term on screen beside it: "= bank 12 + assets kept 24 - HOME lost 0 x 8 - Heat carried 17".
## Returns the y after the two lines.
func _formula(st: L5State, x: float, y: float, head: String) -> float:
	var kept := L5Rules.assets_kept(model.leg, st)
	var lost := L5Config.HOME_HP - st.home_hp
	G.text(self, Vector2(x, y), "%s: %d" % [head, L5Rules.score(model.leg, st)], 15, G.CELL)
	G.text(self, Vector2(x, y + 20), "= bank %d + assets kept %d - HOME lost %d x %d - Heat carried %d" % [st.bank, kept, lost, L5Config.HOME_LOSS_COST, L5Rules.heat_carried(st)], 12, G.DIM)
	return y + 44.0


# ---- between raids ----
func _draw_repair() -> void:
	var s := model.state
	var bp: Dictionary = model.between_preview()
	var ns: L5State = bp["state"]
	var last: Dictionary = model.history.back()
	var dark: Array = last["alloc"]["dark"]
	var shown_status: Dictionary = s.status.duplicate()
	for pc: Vector2i in model.pending_repairs:
		shown_status[pc] = "OK"
	_draw_net(false, shown_status, s.home_hp, {"ghost": [], "dark": dark, "decoys": []})
	if not model.breach_settled():
		_draw_next_raid_strip(L5Rules.extra_count(int(round(_heat_disp))))
	var vals: Dictionary = model.values()
	for c: Vector2i in s.status:
		var pp := chip_at(c)
		if s.status[c] == "DOWN":
			var cost := L5Rules.idiv(int(vals[c]), L5Config.REPAIR_DIV)
			var picked: bool = model.pending_repairs.has(c)
			var affordable: bool = picked or cost <= model.budget()
			var col := G.CLEAN if picked else (G.CELL if affordable else G.DIM)
			G.circle(self, pp, NODE_R + 8, col, 4.0 if picked else 3.0)
			var tag := Rect2(pp.x - 36, pp.y + 34, 72, 22)
			G.panel(self, tag, col, G.PANEL, 2.0)
			G.coin(self, Vector2(tag.position.x + 12, tag.position.y + 11), 6, col)
			G.text(self, Vector2(tag.position.x + 24, tag.position.y + 3), "-%d" % cost if not picked else "FIX -%d" % cost, 13, col)
			if picked:
				# Committed: a check on the node and a frame round the tag.
				G.disc(self, pp + Vector2(26, -26), 11, G.CLEAN)
				G.check(self, pp + Vector2(26, -26), 5, G.BG)
				G.panel(self, tag.grow(3.0), G.CLEAN, Color(0, 0, 0, 0), 2.0)
			_cell_hit(c)
		elif s.status[c] == "OK" and not dark.has(c) and L5Rules.idiv(int(vals[c]), L5Config.INCOME_DIV) > 0:
			var inc := L5Rules.idiv(int(vals[c]), L5Config.INCOME_DIV)
			_income_chip(pp + Vector2(0, 50), inc, false)
	for c: Vector2i in model.pending_repairs:
		G.text_c(self, chip_at(c) + Vector2(0, -42), "REPAIRED", 12, G.CLEAN)
	# One screen, three choices.
	var x0 := PANEL_X + 16
	var wi := PANEL_W - 32.0
	G.panel(self, Rect2(PANEL_X, 74, PANEL_W, 544))
	G.text(self, Vector2(x0, 80), "BETWEEN RAIDS", 17, G.INK)
	G.text_r(self, Vector2(x0 + wi, 84), "after raid %d" % (model.raid + 1), 13, G.DIM)
	G.text(self, Vector2(x0, 108), "1  REPAIRS  (1 crew: pick one)", 13, G.DIM)
	var rc: int = int(bp["repair_cost"])
	var n_down: int = s.count("DOWN")
	if model.pending_repairs.is_empty():
		G.text_r(self, Vector2(x0 + wi, 108), "click a DOWN asset" if n_down > 0 else "nothing is DOWN", 12, G.DIM)
	else:
		var stay: int = n_down - model.pending_repairs.size()
		G.text_r(self, Vector2(x0 + wi, 108), "%d fixed  -%d%s" % [model.pending_repairs.size(), rc, ("   %d stay DOWN" % stay) if stay > 0 else ""], 13, G.DMG)
	G.text(self, Vector2(x0, 130), "2  SHOP: ONE BUY  (after repairs)", 13, G.DIM)
	var bw := (wi - 32.0) / 5.0
	_shop_btn(Rect2(x0, 150, bw, 44), "")
	var bi := 1
	for kind in L5Config.KITS:
		_shop_btn(Rect2(x0 + bi * (bw + 8.0), 150, bw, 44), kind)
		bi += 1
	G.text(self, Vector2(x0, 204), "3  RUN INTENSITY  (Heat, income, the next raid's breach risk)", 13, G.DIM)
	var cw := (wi - 20.0) / 3.0
	for i in range(3):
		var name: String = L5Config.INTENSITIES[i]
		var cr := Rect2(x0 + i * (cw + 10.0), 224, cw, 142)
		var sel: bool = model.pending_intensity == name
		var com: bool = sel and model.intensity_committed
		G.panel(self, cr, G.CLEAN if com else (G.CELL if sel else G.PANEL_EDGE), Color8(60, 52, 24) if (sel or _hot(cr)) else G.PANEL, 4.0 if com else (3.0 if sel else 2.0))
		_add_hit(cr, "inten:" + name)
		if com:
			G.disc(self, Vector2(cr.end.x - 18, cr.position.y + 18), 11, G.CLEAN)
			G.check(self, Vector2(cr.end.x - 18, cr.position.y + 18), 5, G.BG)
		elif sel:
			G.text_r(self, Vector2(cr.end.x - 8, cr.position.y + 6), "default", 12, G.DIM)
		var alt := L5Rules.between_parts(model.leg, s, dark, model.pending_repairs, name, model.pending_buy)
		var ast: L5State = alt["state"]
		var nb: int = L5Rules.extra_count(ast.heat)
		G.text(self, Vector2(cr.position.x + 10, cr.position.y + 4), name, 16, G.CLEAN if com else (G.CELL if sel else G.INK))
		G.flame(self, Vector2(cr.position.x + 18, cr.position.y + 36), 8)
		G.text(self, Vector2(cr.position.x + 34, cr.position.y + 26), "+%d Heat" % int(alt["heat_add"]), 15, G.HEAT)
		G.coin(self, Vector2(cr.position.x + 18, cr.position.y + 57), 7)
		G.text(self, Vector2(cr.position.x + 34, cr.position.y + 47), "x%s: +%d" % [["0.5", "1", "1.5"][i], int(alt["income"])], 14, G.CELL)
		G.text(self, Vector2(cr.position.x + 10, cr.position.y + 68), "next Heat %d" % ast.heat, 13, G.INK)
		G.text(self, Vector2(cr.position.x + 10, cr.position.y + 83), "%d known beam%s" % [1 + nb, "" if nb == 0 else "s"], 13, G.THREAT_LIGHT if nb > 0 else G.DIM)
		G.text_r(self, Vector2(cr.end.x - 8, cr.position.y + 84), "[%s]" % name.substr(0, 1), 12, G.DIM)
		_draw_risk(cr, name)
	# Ledger: Schematics (left) and Heat (right).
	var ly := 376.0
	var xl := x0
	var xr := x0 + 206.0
	var xm := x0 + 222.0
	var xe := x0 + wi
	G.coin(self, Vector2(xl + 8, ly + 9), 8)
	G.text(self, Vector2(xl + 24, ly), L5Config.key_label().to_upper(), 14, G.DIM)
	var yy := ly + 24.0
	_lrow(xl, xr, yy, "AFTER THE RAID", str(s.bank), G.INK)
	yy += 19.0
	_lrow(xl, xr, yy, "REPAIRS", "-%d" % rc if rc > 0 else "0", G.DMG if rc > 0 else G.DIM)
	yy += 19.0
	var bcost: int = int(bp["buy_cost"])
	_lrow(xl, xr, yy, "SHOP", "-%d" % bcost if bcost > 0 else "0", G.DMG if bcost > 0 else G.DIM)
	yy += 19.0
	draw_line(Vector2(xl, yy + 2), Vector2(xr, yy + 2), G.PANEL_EDGE, 2.0)
	yy += 6.0
	_lrow(xl, xr, yy, "BANK NOW", str(s.bank - rc - bcost), G.INK)
	yy += 19.0
	_lrow(xl, xr, yy, "INCOME (next run)", "+%d" % int(bp["income"]), G.CLEAN)
	yy += 19.0
	draw_line(Vector2(xl, yy + 2), Vector2(xr, yy + 2), G.PANEL_EDGE, 2.0)
	yy += 6.0
	_lrow(xl, xr, yy, "NEXT RAID", str(ns.bank), G.CELL)
	G.flame(self, Vector2(xm + 8, ly + 9), 9)
	G.text(self, Vector2(xm + 24, ly), "HEAT", 14, G.DIM)
	yy = ly + 24.0
	_lrow(xm, xe, yy, "AFTER THE RAID", str(s.heat), G.INK)
	yy += 19.0
	_lrow(xm, xe, yy, "THE RUN", "+%d" % int(bp["heat_add"]), G.HOLD)
	yy += 19.0
	draw_line(Vector2(xm, yy + 2), Vector2(xe, yy + 2), G.PANEL_EDGE, 2.0)
	yy += 6.0
	_lrow(xm, xe, yy, "NEXT RAID", str(ns.heat), G.HEAT)
	yy += 26.0
	var nxt_extra: int = L5Rules.extra_count(ns.heat)
	G.text(self, Vector2(xm, yy), "Next raid: %d known beam%s." % [1 + nxt_extra, "" if nxt_extra == 0 else "s"], 13, G.THREAT_LIGHT if nxt_extra > 0 else G.DIM)
	yy += 20.0
	G.text(self, Vector2(xm, yy), _carried_s(L5Rules.heat_carried(ns)), 13, G.HEAT if L5Rules.heat_carried(ns) > 0 else G.DIM)
	var ty := 540.0
	G.text(self, Vector2(x0, ty), "Network: %d OK, %d DOWN, %d TAKEN     Assets kept: %d" % [s.count("OK"), s.count("DOWN"), s.count("TAKEN"), model.kept_after_picks()], 13, G.INK)
	_formula(ns, x0, ty + 22.0, "Leg value after this step (income counted)")
	var settled := model.breach_settled()
	if settled:
		_draw_settled_banner()
		var lr := Rect2(PANEL_X, 624, PANEL_W, 44)
		G.panel(self, lr, G.DMG, Color8(80, 14, 28) if _hot(lr) else Color8(52, 10, 20), 4.0)
		G.home_server(self, Vector2(lr.position.x + 30, lr.get_center().y), 13.0, G.DMG, Color8(80, 12, 24))
		G.cross(self, Vector2(lr.position.x + 30, lr.get_center().y), 7.0, G.DMG, 3.0)
		G.text_c(self, lr.get_center() + Vector2(14, 0), "LAUNCH: THE CELL FALLS  [Enter]", 17, G.DMG)
		_add_hit(lr, "next")
	else:
		_btn(Rect2(PANEL_X, 624, PANEL_W, 44), "NEXT RAID  [Enter]", "next", true, 18)
	_draw_legend()


## The next raid's beams, read off the Heat the meter shows as it fills: one chip per beam (1, +, ++, the sealed ?, the hunter 3);
## the chip of a beam the meter has just earned pops in.
func _draw_next_raid_strip(nb: int) -> void:
	if nb != _nb_shown:
		_nb_at = fx_clock if _nb_shown >= 0 else fx_clock - 99.0
		_nb_shown = nb
	var r := Rect2(20, 82, 350, 42)
	G.panel(self, r, G.THREAT, G.PANEL, 2.0)
	G.text(self, Vector2(r.position.x + 10, r.position.y + 5), "NEXT RAID", 12, G.DIM)
	G.text(self, Vector2(r.position.x + 10, r.position.y + 21), "%d BEAM%s" % [1 + nb, "" if nb == 0 else "S"], 13, G.THREAT_LIGHT)
	var items: Array = ["1"]
	if nb >= 1:
		items.append("+")
	if nb >= 2:
		items.append("++")
	items.append("?")
	items.append("3")
	var x := r.position.x + 126.0
	for i in range(items.size()):
		var s: String = items[i]
		var pop := 1.0
		if (s == "+" or s == "++") and i == nb and not L7Config.instant:
			var age: float = fx_clock - _nb_at
			if age >= 0.0 and age < 0.55:
				pop = 1.0 + 0.8 * (1.0 - age / 0.55) * (1.0 - age / 0.55)
		var c := Vector2(x, r.position.y + 21.0)
		draw_set_transform(c, 0.0, Vector2(pop, pop))
		if s == "?":
			_sealed_chip(Vector2.ZERO, G.THREAT_LIGHT)
		else:
			G.badge(self, Vector2.ZERO, s, G.THREAT)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
		x += 42.0


## The between screen when breach_risk is 3/3 on every intensity: the loss is decided, so say so.
func _draw_settled_banner() -> void:
	var r := Rect2(20, 78, 740, 56)
	G.panel(self, r, G.DMG, Color8(52, 10, 20), 4.0)
	var hc := Vector2(r.position.x + 32, r.position.y + 28)
	G.home_server(self, hc, 18.0, G.DMG, Color8(80, 12, 24))
	G.cross(self, hc, 9.0, G.DMG, 3.0)
	G.text(self, Vector2(r.position.x + 62, r.position.y + 11), "DECIDED", 30, G.DMG)
	G.text(self, Vector2(r.position.x + 232, r.position.y + 7), "The next raid empties HOME on every sealed line, whatever you plan.", 13, G.INK)
	G.text(self, Vector2(r.position.x + 232, r.position.y + 32), "Launch plays it out at once: no forecast, no choices.", 13, G.DIM)


## What an intensity card says about the next raid's breach (sweep_l5.breach_risk, live with the repair and the buy):
## {risk, kind ("breach" / "levers" / "safe"), line1, line2}. "BREACH on k/3 lines" when no plan avoids it, "safe with
## levers" when only a plan does, "safe" otherwise.
func risk_card(intensity: String) -> Dictionary:
	var risks := {}
	for nm: String in L5Config.INTENSITIES:
		risks[nm] = model.risk_for(nm)
	var rk: Dictionary = risks[intensity]
	var risk: int = rk["risk"]
	if risk > 0:
		var same := true
		for nm: String in L5Config.INTENSITIES:
			same = same and int((risks[nm] as Dictionary)["risk"]) == risk
		var why := "even with the best plan"
		if risk == L5Config.CANDIDATES:
			why = "whatever you pick" if same else "whatever you plan"
		return {"risk": risk, "kind": "breach", "line1": "BREACH on %d/%d lines" % [risk, L5Config.CANDIDATES], "line2": why}
	if int(rk["empty"]) > 0:
		return {"risk": 0, "kind": "levers", "line1": "safe with levers", "line2": "no lever: %d/%d breach" % [int(rk["empty"]), L5Config.CANDIDATES]}
	return {"risk": 0, "kind": "safe", "line1": "safe", "line2": "no line breaches"}


## The risk text on an intensity card: red frame for a breach, amber for "safe with levers", lime for "safe".
func _draw_risk(cr: Rect2, intensity: String) -> void:
	var rc := risk_card(intensity)
	var x := cr.position.x + 10
	var y := cr.position.y + 104
	match String(rc["kind"]):
		"breach":
			G.panel(self, Rect2(cr.position.x + 4, y - 4, cr.size.x - 8, 38), G.DMG, Color8(52, 10, 20), 2.0)
			G.text(self, Vector2(x, y), String(rc["line1"]), 12, G.DMG)
			G.text(self, Vector2(x, y + 16), String(rc["line2"]), 12, G.INK)
		"levers":
			G.text(self, Vector2(x, y), String(rc["line1"]), 13, G.HOLD)
			G.text(self, Vector2(x, y + 16), String(rc["line2"]), 12, G.DIM)
		_:
			G.text(self, Vector2(x, y), String(rc["line1"]), 13, G.CLEAN)
			G.text(self, Vector2(x, y + 16), String(rc["line2"]), 12, G.DIM)


# ---- breach ----
func _draw_breach() -> void:
	var after: L5State = row["after_raid"]
	var tint := Color8(34, 6, 12)
	# The dead network (HOME drained to 0) stays dimly behind the card, under a red veil.
	for c in L5Rules.nodes():
		_draw_node(c, after.status, 0, row["alloc"])
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), Color(tint.r, tint.g, tint.b, 0.93))
	var u := 1.0 if L7Config.instant else clampf(screen_t() / L7Config.BREACH_CARD_T, 0.0, 1.0)
	var s := L7Config.ease_back(u)
	var mid := 640.0
	# A broken HOME server, shaking as the card lands.
	var hc := Vector2(mid, 170) + Vector2(sin(screen_t() * 70.0), cos(screen_t() * 55.0)) * 5.0 * (1.0 - u)
	G.home_server(self, hc, 56.0, Color(G.DMG.r, G.DMG.g, G.DMG.b, u), Color8(60, 10, 20))
	G.line(self, hc + Vector2(-40, -62), hc + Vector2(-8, -4), tint, 8.0)
	G.line(self, hc + Vector2(-8, -4), hc + Vector2(-34, 60), tint, 8.0)
	G.line(self, hc + Vector2(40, -62), hc + Vector2(14, 8), tint, 8.0)
	for k in range(L5Config.HOME_HP):
		G.pip(self, Vector2(mid + (k - 1) * 34.0, 252), 22.0, "lost")
	draw_set_transform(Vector2(mid, 330), 0.0, Vector2(s, s))
	G.text_c(self, Vector2.ZERO, "BREACHED", 84, Color(G.DMG.r, G.DMG.g, G.DMG.b, minf(1.0, u * 3.0)))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	var fade := clampf((u - 0.4) / 0.6, 0.0, 1.0)
	G.text_c(self, Vector2(mid, 398), "THE CAMPAIGN IS LOST", 30, Color(G.INK.r, G.INK.g, G.INK.b, fade))
	G.text_c(self, Vector2(mid, 446), "Raid %d: the beams reached HOME and its last integrity went." % (int(row["raid"]) + 1), 18, Color(G.DIM.r, G.DIM.g, G.DIM.b, fade))
	var l: Dictionary = row["ledger"]
	G.text_c(self, Vector2(mid, 480), "HOME %d -> 0   |   Heat %d" % [l["home_before"], l["heat_after"]], 16, Color(G.DIM.r, G.DIM.g, G.DIM.b, fade))
	_btn(Rect2(mid - 200, 540, 400, 52), "LEG RECORD  [Enter]", "next", true, 20)


# ---- leg record ----
func _draw_record() -> void:
	G.text(self, Vector2(40, 80), "LEG RECORD", 22, G.INK)
	if model.breached:
		G.text(self, Vector2(220, 84), "BREACHED: the campaign was lost in raid %d" % model.history.size(), 17, G.DMG)
	else:
		G.text(self, Vector2(220, 84), "THE CELL SURVIVED THE LEG", 17, G.CLEAN)
	for j in range(L5Config.RAIDS):
		var r := Rect2(30 + j * 410, 116, 390, 440)
		if j >= model.history.size():
			G.panel(self, r, G.PANEL_EDGE, G.PANEL, 2.0)
			G.text(self, Vector2(r.position.x + 20, r.position.y + 14), "RAID %d" % (j + 1), 20, G.DIM)
			G.text(self, Vector2(r.position.x + 20, r.position.y + 60), "NOT PLAYED", 24, G.DIM)
			continue
		var h: Dictionary = model.history[j]
		var l: Dictionary = h["ledger"]
		var sm: Dictionary = h["summary"]
		var tier: String = h["tier"]
		var col := G.tier_color(tier)
		G.panel(self, r, col, G.PANEL, 3.0)
		G.text(self, Vector2(r.position.x + 20, r.position.y + 12), "RAID %d" % (j + 1), 20, G.DIM)
		G.text_r(self, Vector2(r.end.x - 20, r.position.y + 10), G.tier_word(tier), 22, col)
		G.flame(self, Vector2(r.position.x + 30, r.position.y + 62), 10)
		G.text(self, Vector2(r.position.x + 48, r.position.y + 50), "%d -> %d" % [l["heat_before"], l["heat_after"]], 20, G.HEAT)
		_band_chips(Vector2(r.position.x + 190, r.position.y + 62), int(l["extra"]), false)
		_mini_map(Vector2(r.position.x + 20, r.position.y + 92), h)
		G.text(self, Vector2(r.position.x + 20, r.position.y + 228), "ring: changed in this raid   dim: carried over", 11, G.DIM)
		var tx := r.position.x + 214
		var ty := r.position.y + 100.0
		G.text(self, Vector2(tx, ty - 4), "CHANGED IN THIS RAID", 11, G.DIM)
		ty += 20.0
		_chips(tx, ty + 10, sm)
		ty += 34.0
		G.home_server(self, Vector2(tx + 8, ty + 10), 7.0, G.INK)
		for k in range(L5Config.HOME_HP):
			G.pip(self, Vector2(tx + 40 + k * 22, ty + 10), 14.0, "full" if k < int(l["home_after"]) else "lost")
		ty += 30.0
		var used: Dictionary = l["kit_used"]
		G.text(self, Vector2(tx, ty), "USED", 11, G.DIM)
		for ki in range(L5Config.KITS.size()):
			var kx := tx + 40.0 + ki * 31.0
			var kk: String = L5Config.KITS[ki]
			_kit_icon(kk, Vector2(kx, ty + 8), 6.0, KIT_COL[kk])
			G.text(self, Vector2(kx + 11, ty), str(used[kk]), 14, G.INK if int(used[kk]) > 0 else G.DIM)
		if String(l["spoof_kind"]) != "":
			if l["spoof_kind"] == "JAM":
				G.jam_mark(self, Vector2(tx + 8, ty + 32), 8.0, G.CLEAN)
			else:
				G.skip_chevron(self, Vector2(tx + 8, ty + 32), 5.0, G.CLEAN, 2.0)
			G.text(self, Vector2(tx + 24, ty + 24), "%s  Heat +%d" % [l["spoof_kind"], int(l["spoof_heat"])], 12, G.CLEAN)
		G.text(self, Vector2(r.position.x + 20, r.position.y + 250), "SEALED LINE", 11, G.DIM)
		G.cand_shape(self, Vector2(r.position.x + 108, r.position.y + 258), int(h["real_shape"]), 8.0, G.THREAT_LIGHT, G.BG, 2.5)
		G.text(self, Vector2(tx, r.position.y + 250), "ASSETS KEPT  %d" % L5Rules.assets_kept(model.leg, h["after_raid"]), 13, G.INK)
		var ar: L5State = h["after_raid"]
		G.text(self, Vector2(r.position.x + 20, r.position.y + 404), "AFTER THE RAID", 11, G.DIM)
		_status_counts(Vector2(r.position.x + 20, r.position.y + 420), ar)
		var bt: Dictionary = h["between"]
		var ly := r.position.y + 282.0
		if not bt.is_empty():
			G.text(self, Vector2(r.position.x + 20, ly), "Run %s: Heat +%d, income +%d" % [bt["intensity"], bt["heat_add"], bt["income"]], 13, G.INK)
			var rep := "repaired %d (-%d)" % [(bt["repaired"] as Array).size(), bt["repair_cost"]]
			var buy_s := "bought %s (-%d)" % [bt["bought"], bt["buy_cost"]] if String(bt["bought"]) != "" else "no shop buy"
			G.text(self, Vector2(r.position.x + 20, ly + 22), "%s   %s" % [rep, buy_s], 13, G.INK)
			var nb: L5State = bt["after"]
			G.text(self, Vector2(r.position.x + 20, ly + 46), "Next raid: Heat %d, %d known beam%s" % [nb.heat, 1 + L5Rules.extra_count(nb.heat), "" if L5Rules.extra_count(nb.heat) == 0 else "s"], 13, G.DIM)
			G.text(self, Vector2(r.position.x + 20, ly + 68), _carried_s(L5Rules.heat_carried(nb), "Heat carried so far"), 13, G.HEAT if L5Rules.heat_carried(nb) > 0 else G.DIM)
		elif tier == "BREACHED":
			G.text(self, Vector2(r.position.x + 20, ly), "No between step: the campaign ended.", 13, G.DMG)
		elif j == model.history.size() - 1:
			G.text(self, Vector2(r.position.x + 20, ly), "The last raid: no between step.", 13, G.DIM)
			G.text(self, Vector2(r.position.x + 20, ly + 22), _carried_s(int(l["carried"])), 13, G.HEAT if int(l["carried"]) > 0 else G.DIM)
	var s := model.state
	var kept := L5Rules.assets_kept(model.leg, s)
	var lost: int = L5Config.HOME_HP - s.home_hp
	var sc: String
	if model.breached:
		sc = "CAMPAIGN LOST: the leg has no score"
	else:
		sc = "SCORE  %d   =  bank %d  +  assets kept %d  -  HOME lost %d x %d  -  Heat carried %d  (Heat %d, start %d)" % [model.final_score(), s.bank, kept, lost, L5Config.HOME_LOSS_COST, L5Rules.heat_carried(s), s.heat, L5Config.START_HEAT]
	G.text(self, Vector2(40, 566), sc, 18, G.DMG if model.breached else G.CELL)
	G.text(self, Vector2(40, 592), "LEG END", 13, G.DIM)
	_status_counts(Vector2(120, 590), s)
	_btn(Rect2(40, 612, 400, 46), "PLAY THE LEG AGAIN  [Enter]", "next", true, 18)
	_draw_verdict(Rect2(460, 598, 790, 70))


## The leg verdict on the record: what the leg kept ("CELL KEPT 4/6, HOME 3/3"), with the assets as glyphs, and the score
## ranked against the golden careless line of the same leg, so three BATTERED stamps on a good line do not read as losing.
func _draw_verdict(r: Rect2) -> void:
	var s := model.state
	var cells: Array = s.status.keys()
	cells.sort_custom(func(a: Vector2i, b: Vector2i) -> bool: return a.x < b.x or (a.x == b.x and a.y < b.y))
	var kept_n := 0
	for c: Vector2i in cells:
		if s.status[c] != "TAKEN":
			kept_n += 1
	var delta: int = model.final_score() - model.careless_score()
	var good: bool = not model.breached and s.home_hp >= L5Config.HOME_HP - 1 and delta > 0
	var col := G.DMG if model.breached else (G.CLEAN if good else G.HOLD)
	G.panel(self, r, col, G.PANEL, 3.0)
	var x := r.position.x + 18
	var cy := r.position.y + 22
	for c: Vector2i in cells:
		match String(s.status[c]):
			"OK":
				G.disc(self, Vector2(x + 11, cy), 11, G.PANEL)
				G.circle(self, Vector2(x + 11, cy), 11, G.CELL, 3.0)
			"DOWN":
				G.disc(self, Vector2(x + 11, cy), 11, GREY)
				G.bolt(self, Vector2(x + 11, cy), 9.0)
			_:
				G.corp(self, Vector2(x + 11, cy), 11.0)
		x += 30.0
	G.text(self, Vector2(x + 12, r.position.y + 7), "CELL KEPT %d/%d" % [_cnt(kept_n), cells.size()], 22, col)
	var hx := x + 12 + G.text_w("CELL KEPT %d/%d" % [kept_n, cells.size()], 22) + 22.0
	G.text(self, Vector2(hx, r.position.y + 7), "HOME %d/%d" % [_cnt(maxi(0, s.home_hp)), L5Config.HOME_HP], 22, col)
	for k in range(L5Config.HOME_HP):
		G.pip(self, Vector2(hx + 130 + k * 24, r.position.y + 21), 16.0, "full" if k < s.home_hp else "lost")
	var cmp_y := r.position.y + 42.0
	if model.breached:
		G.text(self, Vector2(r.position.x + 18, cmp_y), "The campaign is lost: the leg has no score.", 14, G.DMG)
		return
	if model.careless_score() <= -L5Config.BREACH:
		# The careless line loses the campaign: a broken HOME, not a score to beat by 100.
		G.text(self, Vector2(r.position.x + 18, cmp_y), "CARELESS", 13, G.DIM)
		G.home_server(self, Vector2(r.position.x + 120, cmp_y + 8), 9.0, G.DMG)
		G.cross(self, Vector2(r.position.x + 120, cmp_y + 8), 5.0, G.DMG, 2.0)
		G.text(self, Vector2(r.position.x + 140, cmp_y), "BREACH", 14, G.DMG)
		G.check(self, Vector2(r.position.x + 270, cmp_y + 9), 8, G.CLEAN)
		G.text(self, Vector2(r.position.x + 288, cmp_y - 2), "YOUR LEG SCORES %d" % _cnt(model.final_score()), 16, G.CLEAN)
		return
	# Against the careless line: two bars on one scale.
	var top: float = float(maxi(1, maxi(model.final_score(), model.careless_score())))
	var bw := 150.0
	G.text(self, Vector2(r.position.x + 18, cmp_y), "YOU", 13, G.INK)
	draw_rect(Rect2(r.position.x + 62, cmp_y + 3, bw * _cu() * clampf(float(model.final_score()) / top, 0.0, 1.0), 10), col)
	G.text(self, Vector2(r.position.x + 62 + bw + 8, cmp_y), str(_cnt(model.final_score())), 14, G.INK)
	G.text(self, Vector2(r.position.x + 300, cmp_y), "CARELESS", 13, G.DIM)
	draw_rect(Rect2(r.position.x + 392, cmp_y + 3, bw * _cu() * clampf(float(maxi(0, model.careless_score())) / top, 0.0, 1.0), 10), G.GREY_PIP)
	G.text(self, Vector2(r.position.x + 392 + bw + 8, cmp_y), str(_cnt(model.careless_score())), 14, G.DIM)
	G.text(self, Vector2(r.position.x + 640, cmp_y - 2), "%+d" % _cnt(delta), 20, G.CLEAN if delta > 0 else G.HOLD)


## The count-up of the record's verdict: 0..1 since the screen opened (instant mode shows the final numbers).
func _cu() -> float:
	return 1.0 if L7Config.instant else L7Config.ease_out(clampf(screen_t() / L7Config.COUNT_UP_T, 0.0, 1.0))


## A verdict number counting up to `v`.
func _cnt(v: int) -> int:
	return int(round(float(v) * _cu()))


## "n OK  n DOWN  n TAKEN" with the status glyphs, one line starting at p (p.y is the text top).
func _status_counts(p: Vector2, st: L5State) -> void:
	G.disc(self, p + Vector2(10, 10), 9, G.PANEL)
	G.circle(self, p + Vector2(10, 10), 9, G.CELL, 3.0)
	G.text(self, p + Vector2(26, 0), "%d OK" % st.count("OK"), 16, G.INK)
	G.disc(self, p + Vector2(100, 10), 9, GREY)
	G.bolt(self, p + Vector2(100, 10), 7.0)
	G.text(self, p + Vector2(116, 0), "%d DOWN" % st.count("DOWN"), 16, G.HOLD if st.count("DOWN") > 0 else G.INK)
	G.corp(self, p + Vector2(210, 10), 9.0)
	G.text(self, p + Vector2(226, 0), "%d TAKEN" % st.count("TAKEN"), 16, G.THREAT_LIGHT if st.count("TAKEN") > 0 else G.INK)


func _mini_map(origin: Vector2, h: Dictionary) -> void:
	var after: L5State = h["after_raid"]
	var before: L5State = h["before"]
	var touched: Array = []
	for o: Dictionary in h["outcomes"]:
		touched.append(o["cell"])
	for c in L5Rules.nodes():
		var p := origin + Vector2(c.x * 44.0 + 20.0, c.y * 44.0 + 20.0)
		var cell_r := Rect2(p.x - 20, p.y - 20, 40, 40)
		draw_rect(cell_r, Color8(20, 24, 46))
		draw_rect(cell_r, G.PANEL_EDGE, false, 1.0)
		var changed := false
		if c == model.home():
			G.home_server(self, p, 12.0, G.INK)
			changed = touched.has(c)
		elif after.status.has(c):
			changed = after.status[c] != before.status[c]
			match after.status[c]:
				"OK":
					G.circle(self, p, 11, G.CELL, 3.0)
				"DOWN":
					G.disc(self, p, 12, GREY)
					G.bolt(self, p, 9.0)
				"TAKEN":
					G.corp(self, p, 12.0)
			if after.status[c] != "OK" and not changed:
				draw_rect(cell_r.grow(-1.0), Color(20 / 255.0, 24 / 255.0, 46 / 255.0, 0.62))
		elif (h["alloc"]["decoys"] as Array).has(c):
			G.diamond(self, p, 11, G.CELL, 2.5)
		else:
			G.disc(self, p, 3, G.EMPTY_NODE)
		if changed or (touched.has(c) and not after.status.has(c)):
			draw_rect(cell_r.grow(-1.0), G.DMG, false, 2.0)


## The sealed beam's own mark: a short dashed line capped by a square.
func _sealed_chip(p: Vector2, col: Color) -> void:
	G.dashed_line(self, p + Vector2(-17, 0), p + Vector2(-3, 0), col, 4.0, 3.0, 3.0)
	G.cand_shape(self, p + Vector2(7, 0), 1, 8.0, col, G.BG, 2.5)
	G.text_c(self, p + Vector2(7, 0), "?", 12, G.INK)


## A lime skip-chevron in a round badge: "a spoof skips this node".
func _spoof_mark(p: Vector2, r: float) -> void:
	G.disc(self, p, r + 4.0, G.BG)
	G.circle(self, p, r + 4.0, G.CLEAN, 2.5)
	G.skip_chevron(self, p, r * 0.6, G.CLEAN, 2.5)


## The leg kit tray: ghosts, decoys, spoofs and go-dark charges left as pips; planned uses show hollow.
func _draw_kit_tray(r: Rect2, planned: Dictionary = {}) -> void:
	G.panel(self, r)
	var cy := r.position.y + r.size.y * 0.5
	G.text(self, Vector2(r.position.x + 10, cy - 8), "KIT", 14, G.DIM)
	var n := L5Config.KITS.size()
	var tw := (r.size.x - 50.0) / n
	for i in range(n):
		var kind: String = L5Config.KITS[i]
		var have: int = int(model.state.kit[kind])
		var used: int = int(planned.get(kind, 0))
		var x0 := r.position.x + 46.0 + i * tw
		var col: Color = KIT_COL[kind]
		if have <= 0:
			col = G.DIM
		_kit_icon(kind, Vector2(x0 + 10, cy), 9.0, col)
		G.text(self, Vector2(x0 + 26, cy - 10), "%d" % (have - used), 19, G.INK if have - used > 0 else G.DIM)
		for k in range(have):
			var pr := Rect2(x0 + 46 + k * 11, cy - 6, 8, 12)
			if k < have - used:
				draw_rect(pr, col)
			else:
				draw_rect(pr, G.PANEL_EDGE, false, 2.0)


## A node as a small round chip (its value, or the HOME server), edged lime for the spoof list.
func _node_chip(p: Vector2, c: Vector2i, edge: Color) -> void:
	G.circle(self, p, 11, edge, 2.0)
	if c == model.home():
		G.home_server(self, p, 6.0, G.INK)
	elif (model.plan["decoys"] as Array).has(c):
		G.diamond(self, p, 6.0, G.CELL, 2.0)
	elif model.values().has(c):
		G.text_c(self, p, str(model.values()[c]), 12, G.INK)
	else:
		G.disc(self, p, 3, G.DIM)


## Revealed steps of one beam so far.
func _beam_events(id: String) -> int:
	var n := 0
	for e: Dictionary in play.events:
		if e["beam"] == id:
			n += 1
	return n


## "Heat carried: N" (the points the leg score subtracts; the same number and sign on every screen).
func _carried_s(n: int, label: String = "Heat carried") -> String:
	return "%s: %d" % [label, n]


const KIT_COL := {"ghost": Color8(255, 210, 77), "decoy": Color8(255, 210, 77), "spoof": Color8(212, 255, 0), "dark": Color8(206, 214, 236)}


## A kit item's glyph (ghost ring, decoy diamond, spoof chevron, go-dark disc) at p, size s.
func _kit_icon(kind: String, p: Vector2, s: float, col: Color) -> void:
	match kind:
		"ghost":
			G.dashed_ring(self, p, s, col, 3.0)
		"decoy":
			G.diamond(self, p, s + 1.0, col)
		"dark":
			G.dark_disc(self, p, s, col)
		_:
			G.skip_chevron(self, p, s * 0.7, col, 2.5)


## A ledger row between x_l and x_r.
func _lrow(x_l: float, x_r: float, y: float, label: String, amount: String, col: Color) -> void:
	G.text(self, Vector2(x_l, y), label, 14, G.INK)
	G.text_r(self, Vector2(x_r, y), amount, 16, col)


func _shop_btn(r: Rect2, kind: String) -> void:
	var picked: bool = model.pending_buy == kind
	var price: int = int(L5Config.PRICES[kind]) if kind != "" else 0
	var spent: int = model.budget() + (int(L5Config.PRICES[model.pending_buy]) if model.pending_buy != "" else 0)
	var ok: bool = kind == "" or price <= spent
	var col := G.CLEAN if picked else (G.CELL if ok else G.DIM)
	var default_pick: bool = kind == "" and model.pending_buy == ""
	if default_pick:
		col = G.CLEAN if model.buy_committed else G.CELL
	G.panel(self, r, col, Color8(60, 52, 24) if (_hot(r) and ok) else G.PANEL, 4.0 if (picked or (default_pick and model.buy_committed)) else (3.0 if default_pick else 2.0))
	_add_hit(r, "buy:" + ("none" if kind == "" else kind))
	var cy := r.position.y + r.size.y * 0.5
	if kind == "":
		G.text_c(self, Vector2(r.get_center().x, cy - 8), "NO BUY", 13, col)
		G.text_c(self, Vector2(r.get_center().x, cy + 11), "[0]" if model.buy_committed else "default", 12, G.DIM)
		if model.pending_buy == "" and model.buy_committed:
			G.disc(self, Vector2(r.end.x - 11, r.position.y + 11), 9, G.CLEAN)
			G.check(self, Vector2(r.end.x - 11, r.position.y + 11), 4, G.BG)
		return
	_kit_icon(kind, Vector2(r.position.x + 18, cy), 8.0, col if col != G.CELL else KIT_COL[kind])
	if picked:
		G.disc(self, Vector2(r.end.x - 11, r.position.y + 11), 9, G.CLEAN)
		G.check(self, Vector2(r.end.x - 11, r.position.y + 11), 4, G.BG)
	G.coin(self, Vector2(r.position.x + 44, cy - 8), 6, col)
	G.text(self, Vector2(r.position.x + 56, cy - 17), str(price), 16, col)
	G.text(self, Vector2(r.position.x + 36, cy + 3), "have %d" % int(model.state.kit[kind]), 12, G.DIM)


## A numbered shot: the number is the frame's place in the leg, so the folder sorts in play order. `settle` lets the screen's
## own effects (the meter's ease, a stamp, a count-up) finish first; the playout's beats are paced by the capture itself.
func _shot(label: String, settle: bool = true) -> void:
	if settle:
		fx_clock += 3.0
	var shot_name := "%02d_%s" % [_shot_n, label]
	_shot_n += 1
	await _snap(shot_name)
	if max_shots > 0 and _shot_n >= max_shots:
		get_tree().quit(0)


# ---------- capture ----------
func _snap(shot_name: String) -> void:
	queue_redraw()
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [capture_dir, shot_name])
	print("shot ", shot_name)


## Advance the playout by a fixed step in a capture, reading the new events into the cues (what _process does in a run).
func _cap_adv(dt: float = 0.05) -> void:
	play.advance(dt)
	fx.consume(play)
	fx_clock += dt
	# A capture draws no frame between its steps: the stamp counts as landed once its slam time has passed.
	if play.state in [L5Play.S.END, L5Play.S.DONE] and fx.end_at >= 0.0 and play.clock - fx.end_at >= L7Config.STAMP_DELAY + L7Config.STAMP_T:
		_stamp_shown = true


## Play the sweep of the current raid beat by beat, taking a picture at each, choosing the spoof from the line's step.
func _capture_sweep(rn: int, spoof_cell: Variant) -> void:
	var seen := {}
	var guard := 0
	while not play.is_done() and guard < 4000:
		guard += 1
		var bid: String = play.beam_id()
		if play.state == L5Play.S.DECIDE:
			if not seen.has("decide"):
				seen["decide"] = true
				# The grid previews the option the run is about to choose (a pointer on its row would do the same).
				dec_pin = L5Rules.NONE
				if spoof_cell is String:
					dec_pin = L5Rules.JAM
				elif spoof_cell != null:
					dec_pin = spoof_cell
				await _shot("r%d_decision" % rn, false)
				dec_pin = NO_FOCUS
			if spoof_cell == null:
				_act("hold")
			elif spoof_cell is String:
				_act("jam")
			else:
				var sc: Vector2i = spoof_cell
				_act("cell:%d,%d" % [sc.x, sc.y])
			if not cap_lite:
				_cap_adv(0.3)
				await _shot("r%d_after_decision" % rn, false)
			continue
		if play.state == L5Play.S.NOTE and play.t >= 0.3 and not seen.has("note"):
			seen["note"] = true
			await _shot("r%d_no_spoof_left" % rn, false)
		_cap_adv(0.05)
		if play.state == L5Play.S.BEAM:
			var n: int = play.beam_steps(play.bi).size()
			var lead: float = play.lead_of(bid)
			if not cap_lite and bid == "b1" and play.t >= lead * 0.7 and not seen.has("launch"):
				seen["launch"] = true
				await _shot("r%d_launch_b1" % rn, false)
			if play.t >= lead + (n * 0.5 + 0.6) * L7Config.STEP_T and not seen.has("beam_" + bid):
				seen["beam_" + bid] = true
				if not cap_lite or bid in ["b1", "hunter"]:
					await _shot("r%d_beam_%s" % [rn, bid], false)
		elif play.state == L5Play.S.UNSEAL:
			var u: float = play.t / L7Config.UNSEAL_T
			if not cap_lite:
				for step: Array in [[0.2, "unseal_shimmer"], [0.55, "unseal_collapse"], [0.85, "unseal_ignite"]]:
					if u >= float(step[0]) and not seen.has(step[1]):
						seen[step[1]] = true
						await _shot("r%d_%s" % [rn, step[1]], false)
		elif play.state == L5Play.S.TURN and play.t >= 0.45 and not seen.has("turn"):
			seen["turn"] = true
			if not cap_lite:
				await _shot("r%d_hunter_turn" % rn, false)
		elif play.state == L5Play.S.END and play.cut and not seen.has("cut"):
			seen["cut"] = true
			await _shot("r%d_breach_touch" % rn, false)
		# The impacts: a picture a moment after the first DOWN, TAKEN, HOME and DECOY touch of the raid.
		for e: Dictionary in play.events:
			var oc: String = e["outcome"]
			var key := "imp_" + oc
			if oc in ["DOWN", "TAKEN", "HOME", "DECOY"] and not seen.has(key) and play.clock - float(e["at"]) >= 0.28:
				seen[key] = true
				if not cap_lite or oc in ["DOWN", "HOME"]:
					await _shot("r%d_impact_%s" % [rn, oc.to_lower()], false)
		if play.state in [L5Play.S.END, L5Play.S.DONE] and fx.end_at >= 0.0 and not seen.has("stamp") and play.clock - fx.end_at >= L7Config.STAMP_DELAY + 0.22 * L7Config.STAMP_T:
			seen["stamp"] = true
			await _shot("r%d_stamp_slam" % rn, false)
	_check_done()


## The settled breach's fast playout: a picture at each beam's beat and at the touch that empties HOME.
func _capture_fast(rn: int) -> void:
	var seen := {}
	var guard := 0
	await _shot("r%d_fall_start" % rn, false)
	while not play.is_done() and guard < 4000:
		guard += 1
		_cap_adv(0.05)
		var bid: String = play.beam_id()
		if play.state == L5Play.S.BEAM and play.t >= 0.2 and not seen.has("beam_" + bid):
			seen["beam_" + bid] = true
			await _shot("r%d_fall_beam_%s" % [rn, bid], false)
		elif play.state == L5Play.S.END and play.cut and not seen.has("cut"):
			seen["cut"] = true
			await _shot("r%d_fall_home_breached" % rn, false)
		if play.state == L5Play.S.END and fx.end_at >= 0.0 and not seen.has("drain") and play.clock - fx.end_at >= 0.45:
			seen["drain"] = true
			await _shot("r%d_fall_home_drain" % rn, false)
	_check_done()


## Demo frames of the breach warning that names a lever: golden naive leg 0 at raid 3 (every line breaches), with one
## ghost put back in the kit so a lever exists. Plan with the warning, the lever placed, the forecast without a breach.
func _run_demo_breachfix() -> void:
	var steps: Array = model.leg["naive"]
	model.raid = 2
	model.state = L5State.from_golden(steps[2]["before"])
	model.state.kit["ghost"] = 1
	_set_phase(Phase.PLAN)
	_shot_n = 0
	await _shot("demo_breach_warning_names_a_lever")
	var fix: Dictionary = model.breach_fix()
	for stp: Dictionary in fix["steps"]:
		_act("lever:" + String(stp["lever"]))
		_click_cell(stp["cell"])
	sel_lever = ""
	await _shot("demo_lever_placed_warning_gone")
	_act("next")
	await _shot("demo_forecast_after_the_fix")
	get_tree().quit(0)


## Demo frames of the hunter's own line: every asset TAKEN and HOME ghosted, so nothing is touched and the hunter has no
## first touch to turn on (it runs its own line, drawn as a pinned ring over its column, no word).
func _run_demo_ownline() -> void:
	for c: Vector2i in model.state.status:
		model.state.status[c] = "TAKEN"
	_set_phase(Phase.PLAN)
	_act("lever:ghost")
	_click_cell(model.home())
	sel_lever = ""
	_shot_n = 0
	await _shot("demo_plan_own_line")
	_act("next")
	_act("next")
	await _capture_sweep(1, null)
	await _shot("demo_aftermath_evaded")
	get_tree().quit(0)


## Demo frames of the amber kit strip: one ghost left in the kit and Heat 44, so placing it spends the last lever and the
## next raid (49 + the cheapest run) will run an extra beam.
func _run_demo_amber() -> void:
	for k in L5Config.KITS:
		model.state.kit[k] = 0
	model.state.kit["ghost"] = 1
	_set_phase(Phase.PLAN)
	_shot_n = 0
	await _shot("demo_kit_strip_before_the_last_lever")
	_act("lever:ghost")
	_click_cell(model.values().keys()[1])
	sel_lever = ""
	await _shot("demo_kit_strip_amber")
	get_tree().quit(0)


func _run_capture() -> void:
	DirAccess.make_dir_recursive_absolute(capture_dir)
	if cap_demo == "amber":
		await _run_demo_amber()
		return
	if cap_demo == "breachfix":
		await _run_demo_breachfix()
		return
	if cap_demo == "ownline":
		await _run_demo_ownline()
		return
	var steps: Array = model.leg[cap_line]
	_shot_n = 0
	for i in range(steps.size()):
		var s: Dictionary = steps[i]
		var rn := i + 1
		await _shot("r%d_contact" % rn)
		_act("next")
		if not cap_lite:
			await _shot("r%d_plan_empty" % rn)
		var al := L5Data.alloc_of(s["alloc"])
		for c: Vector2i in al["ghost"]:
			if sel_lever != "ghost":
				_act("lever:ghost")
			_click_cell(c)
		for c: Vector2i in al["decoys"]:
			if sel_lever != "decoy":
				_act("lever:decoy")
			_click_cell(c)
		for c: Vector2i in al["dark"]:
			if sel_lever != "dark":
				_act("lever:dark")
			_click_cell(c)
		sel_lever = ""
		if not cap_lite:
			await _shot("r%d_plan_levers" % rn)
		_act("next")
		await _shot("r%d_forecast" % rn)
		_act("next")
		var spoof_cell: Variant = null
		if s["spoof"] is String:
			spoof_cell = String(s["spoof"])
		elif s["spoof"] != null:
			spoof_cell = L5Data.cell(s["spoof"])
		await _capture_sweep(rn, spoof_cell)
		if phase == Phase.AFTER:
			if not cap_lite:
				# The Heat meter eases to the raid's end Heat (a pulse for each line crossed) as the aftermath opens.
				await _shot("r%d_after_open" % rn, false)
				fx_clock += 0.3
				await _shot("r%d_after_heat" % rn, false)
			await _shot("r%d_aftermath" % rn)
		elif phase == Phase.BREACH:
			await _shot("r%d_breach" % rn)
			_act("next")
			break
		_act("next")
		if phase == Phase.REPAIR:
			if not cap_lite:
				# The meter fills to the next raid's Heat as the screen opens: the beam count it brings is shown with it.
				await _shot("r%d_between_fill_a" % rn, false)
				fx_clock += 0.3
				await _shot("r%d_between_fill_b" % rn, false)
			await _shot("r%d_between_open" % rn)
			var b: Dictionary = s["between"]
			for c: Vector2i in L5Data.cells(b["repairs"]).slice(0, L5Config.REPAIR_SLOTS):
				_click_cell(c)
			if not cap_lite:
				await _shot("r%d_between_repairs" % rn)
			_act("buy:" + ("none" if b["buy"] == null else String(b["buy"])))
			_act("inten:" + String(b["intensity"]))
			await _shot("r%d_between_picked" % rn)
			_act("next")
			if fast_play:
				# A settled breach: the next raid plays at once, to the card.
				await _capture_fast(rn + 1)
				if phase == Phase.BREACH:
					await _shot("r%d_breach" % (rn + 1))
					_act("next")
					break
	await _shot("record")
	get_tree().quit(0)


# ---------- scripted runs (the instant replay of a golden raid, and the Movie Maker clips) ----------
## Play one golden step (levers, forecast, launch, the spoof it chose, the aftermath) through the lab's own input path with the
## instant toggle on, and leave the view on the between screen (or on the record after the last raid). Nothing waits.
func _play_step_instant(s: Dictionary) -> void:
	var was := L7Config.instant
	L7Config.instant = true
	_act("next")	## contact -> plan
	var al := L5Data.alloc_of(s["alloc"])
	for c: Vector2i in al["ghost"]:
		if sel_lever != "ghost":
			_act("lever:ghost")
		_click_cell(c)
	for c: Vector2i in al["decoys"]:
		if sel_lever != "decoy":
			_act("lever:decoy")
		_click_cell(c)
	for c: Vector2i in al["dark"]:
		if sel_lever != "dark":
			_act("lever:dark")
		_click_cell(c)
	sel_lever = ""
	_act("next")	## forecast
	_act("next")	## launch
	var guard := 0
	while phase == Phase.PLAY and guard < 400:
		guard += 1
		if play.state == L5Play.S.DECIDE:
			if s["spoof"] == null:
				_act("hold")
			elif s["spoof"] is String:
				_act("jam")
			else:
				var sc := L5Data.cell(s["spoof"])
				_act("cell:%d,%d" % [sc.x, sc.y])
		_adv(0.05)
	L7Config.instant = was
	if phase == Phase.AFTER:
		_act("next")	## aftermath -> between (or the record)


## The between picks of a golden step (repair, buy, intensity), as the capture makes them.
func _pick_between(s: Dictionary) -> void:
	var b: Dictionary = s["between"]
	for c: Vector2i in L5Data.cells(b["repairs"]).slice(0, L5Config.REPAIR_SLOTS):
		_click_cell(c)
	_act("buy:" + ("none" if b["buy"] == null else String(b["buy"])))
	_act("inten:" + String(b["intensity"]))


var _clip_dir: String = ""
var _clip_n: int = 0


## Wait `sec` seconds of the run's own clock (fixed steps under Movie Maker).
func _wait(sec: float) -> void:
	var t := 0.0
	while t < sec:
		await get_tree().process_frame
		t += get_process_delta_time()


## A key frame of the clip: the frame the clip is recording right now, saved as a PNG.
func _clip_frame(label: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("%s/%02d_%s.png" % [_clip_dir, _clip_n, label])
	_clip_n += 1
	print("clip frame ", label)


## `--clip=planned|breach` (with `--clipdir=<abs dir>` for the key frames): a scripted run played in real time, for Movie Maker.
func _run_clip() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--clipdir="):
			_clip_dir = a.substr(10)
	if _clip_dir != "":
		DirAccess.make_dir_recursive_absolute(_clip_dir)
	if clip_mode == "breach":
		await _clip_breach()
	else:
		await _clip_planned()
	await _wait(0.3)
	get_tree().quit(0)


## One planned raid (golden leg 0, raid 1): the levers, the forecast, the launch, the unseal, the spoof window and the pick, the
## impacts, the stamp, the aftermath and the between screen with the meter filling.
func _clip_planned() -> void:
	var s: Dictionary = (model.leg["planned"] as Array)[0]
	await _wait(1.0)
	_act("next")
	await _wait(0.5)
	var al := L5Data.alloc_of(s["alloc"])
	for pair in [["ghost", "ghost"], ["decoy", "decoys"], ["dark", "dark"]]:
		for c: Vector2i in al[pair[1]]:
			_act("lever:" + String(pair[0]))
			_click_cell(c)
			await _wait(0.55)
	sel_lever = ""
	await _wait(0.4)
	await _clip_frame("plan_levers")
	_act("next")
	await _wait(1.3)
	_act("next")
	var seen := {}
	var decide_t := 0.0
	var guard := 0
	while phase == Phase.PLAY and guard < 6000:
		guard += 1
		await get_tree().process_frame
		var p := play
		if p == null:
			break
		if p.state == L5Play.S.BEAM and p.beam_id() == "b1" and p.head() >= 1.6 and not seen.has("launch"):
			seen["launch"] = true
			await _clip_frame("launch_flash")
		if p.state == L5Play.S.UNSEAL:
			var u := p.t / L7Config.UNSEAL_T
			if u >= 0.52 and not seen.has("collapse"):
				seen["collapse"] = true
				await _clip_frame("unseal_collapse")
			if u >= 0.9 and not seen.has("ignite"):
				seen["ignite"] = true
				await _clip_frame("unseal_ignite")
		if p.state == L5Play.S.DECIDE:
			decide_t += get_process_delta_time()
			if decide_t >= 1.5 and not seen.has("window"):
				seen["window"] = true
				await _clip_frame("spoof_window")
			if decide_t >= 2.6 and not seen.has("pick"):
				seen["pick"] = true
				if s["spoof"] == null:
					_act("hold")
				elif s["spoof"] is String:
					_act("jam")
				else:
					var sc := L5Data.cell(s["spoof"])
					_act("cell:%d,%d" % [sc.x, sc.y])
		for e: Dictionary in p.events:
			if e["outcome"] == "DOWN" and not seen.has("impact") and p.clock - float(e["at"]) >= 0.3:
				seen["impact"] = true
				await _clip_frame("impact_down")
		if p.state in [L5Play.S.END, L5Play.S.DONE] and fx.end_at >= 0.0 and not seen.has("stamp") and p.clock - fx.end_at >= L7Config.STAMP_DELAY + 0.3:
			seen["stamp"] = true
			await _clip_frame("stamp")
	await _wait(1.8)
	_act("next")
	await _wait(0.4)
	await _clip_frame("between_fill")
	await _wait(2.0)


## The settled breach (golden naive leg 0): raids 1 and 2 replayed at once off screen, then the between screen with the DECIDED
## banner, Launch, the fast playout under "the cell falls", HOME draining to 0, the BREACHED card.
func _clip_breach() -> void:
	var steps: Array = model.leg["naive"]
	for i in range(2):
		_play_step_instant(steps[i])
		if phase == Phase.REPAIR:
			_pick_between(steps[i])
			if i == 0:
				_act("next")
	await _wait(1.2)
	await _clip_frame("decided")
	await _wait(0.6)
	_act("next")	## LAUNCH: the cell falls
	await _wait(0.06)
	await _clip_frame("fall_start")
	var seen := {}
	var guard := 0
	while phase == Phase.PLAY and guard < 3000:
		guard += 1
		await get_tree().process_frame
		var p := play
		if p == null:
			break
		if p.state in [L5Play.S.END, L5Play.S.DONE] and fx.end_at >= 0.0 and not seen.has("stamp") and p.clock - fx.end_at >= L7Config.STAMP_DELAY + 0.3:
			seen["stamp"] = true
			await _clip_frame("stamp")
		for e: Dictionary in p.events:
			if e["outcome"] == "HOME" and not seen.has("hit") and p.clock - float(e["at"]) >= 0.18:
				seen["hit"] = true
				await _clip_frame("home_hit")
		if p.state == L5Play.S.END and fx.end_at >= 0.0 and not seen.has("drain") and p.clock - fx.end_at >= 0.55:
			seen["drain"] = true
			await _clip_frame("home_drain")
	await _wait(0.45)
	await _clip_frame("breached_slam")
	await _wait(1.4)
	await _clip_frame("breached_card")
	await _wait(0.5)
	_act("next")	## the leg record: the verdict counts up
	await _wait(0.55)
	await _clip_frame("record_count")
	await _wait(1.6)


