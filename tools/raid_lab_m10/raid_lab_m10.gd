extends Control
## L2 sweep-raid lab: the playable view. Reads L2Model / L2Play and draws; the rules live in L2Rules.
## Flow: contact (the raid's strength by Heat band), plan, forecast (outcomes per node, held spoof included),
## hands-off playout with the spoof decision, aftermath, the between-raids repair step, leg record. A raid that touches HOME
## to 0 integrity ends the campaign (BREACH, full screen).
## Capture mode: `-- --shots=<abs dir> [--leg=0] [--line=planned|naive|greedy] [--lite] [--scramble]` plays the whole leg.

enum Phase { CONTACT, PLAN, FORECAST, PLAY, AFTER, REPAIR, BREACH, RECORD }

const G = preload("res://tools/raid_lab_m10/l2_glyphs.gd")
const SPEEDS := [1.0, 2.0, 4.0]
const NODE_R := 28.0
const DASHES := [Vector2(18, 8), Vector2(6, 6), Vector2(14, 4)]
const PANEL_X := 780.0
const PANEL_W := 460.0
const STRIP_Y := 676.0
const GREY := Color8(82, 86, 104)
const GREY_EDGE := Color8(130, 136, 160)
const LEVER_TEXT := {
	"ghost": ["GHOST", "Hides one asset or HOME from every beam.", "1"],
	"decoy": ["DECOY", "A beam stops on it: a touch, not a find.", "2"],
	"dark": ["GO DARK", "Hides one asset; it earns nothing this interval.", "3"],
}

var model := L2Model.new()
var play: L2Play = null
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
var _settled: bool = false
var _badges: Array = []


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shots="):
			capture_dir = a.substr(8)
		elif a.begins_with("--leg="):
			model.new_leg(int(a.substr(6)))
		elif a.begins_with("--line="):
			cap_line = a.substr(7)
		elif a.begins_with("--spoofview="):
			L2Config.toggles["SPOOF_VIEW"] = a.substr(12)
		elif a.begins_with("--key="):
			L2Config.toggles["KEY_LABEL"] = a.substr(6)
		elif a == "--lite":
			cap_lite = true
		elif a == "--scramble":
			G.scramble = true
	if capture_dir != "":
		_run_capture.call_deferred()


func _process(delta: float) -> void:
	if phase == Phase.PLAY and play != null and capture_dir == "":
		play.advance(delta * SPEEDS[speed_i])
		_check_done()
	queue_redraw()


## When the playout ends: settle the raid; a breach goes to the full-screen end, else to the aftermath.
func _check_done() -> void:
	if play != null and play.is_done() and not _settled:
		_settled = true
		row = model.settle(play)
		phase = Phase.BREACH if model.breached else Phase.AFTER


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
		KEY_S:
			_act("skip")
		KEY_H:
			_act("hold")
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
		L2Config.cycle(id.substr(4))
	elif id == "next":
		_next()
	elif id == "back":
		if phase == Phase.FORECAST:
			phase = Phase.PLAN
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
			phase = Phase.FORECAST
	elif id == "launch":
		_launch()
	elif id.begins_with("speed:"):
		speed_i = int(id.substr(6))
	elif id == "skip":
		if phase == Phase.PLAY and play != null:
			play.skip()
			_check_done()
	elif id == "hold":
		if phase == Phase.PLAY and play != null:
			play.pass_spoof()


func _next() -> void:
	match phase:
		Phase.CONTACT:
			phase = Phase.PLAN
			sel_lever = ""
		Phase.PLAN:
			phase = Phase.FORECAST
		Phase.FORECAST:
			_launch()
		Phase.AFTER:
			if model.leg_over():
				phase = Phase.RECORD
			else:
				phase = Phase.REPAIR
		Phase.REPAIR:
			model.finish_between()
			phase = Phase.CONTACT
		Phase.BREACH:
			phase = Phase.RECORD
		Phase.RECORD:
			model.new_leg(model.seed_id)
			phase = Phase.CONTACT


func _launch() -> void:
	if phase in [Phase.PLAN, Phase.FORECAST]:
		play = model.make_play()
		_settled = false
		phase = Phase.PLAY
		sel_lever = ""


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
		if play.state == L2Play.S.DECIDE:
			if not play.choose_spoof(c):
				status_msg = "Pick a node on the lit beam-2 line."
	elif phase == Phase.REPAIR:
		status_msg = model.toggle_repair(c)


# ---------- geometry ----------
static func nx(c: Vector2i) -> Vector2:
	return Vector2(190.0 + c.x * 150.0, 215.0 + c.y * 130.0)


func _add_hit(r: Rect2, id: String) -> void:
	hits.append({"rect": r, "id": id})


func _hot(r: Rect2) -> bool:
	return r.has_point(mouse)


func _btn(r: Rect2, label: String, id: String, enabled: bool = true, size: int = 18) -> void:
	G.button(self, r, label, _hot(r), enabled, size)
	if enabled:
		_add_hit(r, id)


func _cell_hit(c: Vector2i) -> void:
	_add_hit(Rect2(nx(c) - Vector2(46, 46), Vector2(92, 92)), "cell:%d,%d" % [c.x, c.y])


## Beam geometry: node centers, the start extension a, the end extension b, the direction and a perpendicular offset.
func _geom(line: Array, off: float = 0.0) -> Dictionary:
	var pts: Array = []
	for c in line:
		pts.append(nx(c))
	var dir: Vector2 = ((pts.back() as Vector2) - (pts[0] as Vector2)).normalized()
	var step: float = ((pts[1] as Vector2) - (pts[0] as Vector2)).length()
	var perp := Vector2(-dir.y, dir.x) * off
	for i in range(pts.size()):
		pts[i] = (pts[i] as Vector2) + perp
	return {"pts": pts, "a": (pts[0] as Vector2) - dir * step * 0.45, "b": (pts.back() as Vector2) + dir * step * 0.4, "dir": dir}


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


func _draw_path(path: PackedVector2Array, col: Color, w: float, head_arrow: bool = true) -> void:
	if path.size() < 2:
		return
	draw_polyline(path, col, w, true)
	if head_arrow:
		_arrow_head(path, col)


func _draw_dashed_path(path: PackedVector2Array, col: Color, dash: Vector2, w: float) -> void:
	for i in range(path.size() - 1):
		G.dashed_line(self, path[i], path[i + 1], col, dash.x, dash.y, w)
	if path.size() >= 2:
		_arrow_head(path, col)


## The six lines of a raid in a fixed order: beam 1, extra, extra2, the 3 sealed candidates.
func _all_lines() -> Array:
	var rd: Dictionary = model.raid_data()
	return [rd["b1"], rd["extra"], rd["extra2"], rd["cands"][0], rd["cands"][1], rd["cands"][2]]


## Offsets (px) for lines that coincide with an earlier line, so they stay apart (same order as _all_lines).
func _offsets() -> Array:
	var keys: Array = []
	var out: Array = []
	for ln in _all_lines():
		var cs: Array = []
		for c: Vector2i in ln:
			cs.append(c.x * 10 + c.y)
		cs.sort()
		var k := str(cs)
		var dup := 0
		for kk in keys:
			if kk == k:
				dup += 1
		keys.append(k)
		out.append(dup * 13.0)
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


## Hunter columns that coincide with another line shift 14 px so both stay visible.
func _h_off(x: int) -> float:
	var col_key := str(L2Rules.column(x))
	for ln in _all_lines():
		if str(ln) == col_key:
			return 14.0
		var rev: Array = (ln as Array).duplicate()
		rev.reverse()
		if str(rev) == col_key:
			return 14.0
	return 0.0


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
			return _geom(rd["cands"][L2Config.REVEAL], offs[3 + L2Config.REVEAL])
	return _geom(line, _h_off((line[0] as Vector2i).x))


# ---------- drawing ----------
func _draw() -> void:
	hits = []
	_badges = []
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), G.BG)
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
	_draw_strip()


## What the HUD shows now: {heat, bank, hp, dheat, dbank, base_hp, proj}.
func _hud_values() -> Dictionary:
	var s := model.state
	var v := {"heat": s.heat, "bank": s.bank, "hp": s.home_hp, "dheat": 0, "dbank": 0, "proj": [0, 0]}
	match phase:
		Phase.PLAN, Phase.FORECAST:
			v["heat"] = model.heat_now()
			v["bank"] = model.bank_now()
			v["dheat"] = int(v["heat"]) - s.heat
			v["dbank"] = int(v["bank"]) - s.bank
			if phase == Phase.FORECAST:
				v["proj"] = model.worst_home_loss()
		Phase.PLAY:
			v["heat"] = play.run_heat
			v["bank"] = model.bank_now()
			v["dheat"] = play.run_heat - play.before.heat
			v["dbank"] = int(v["bank"]) - play.before.bank
			v["hp"] = play.status_now()["home_hp"]
		Phase.AFTER, Phase.RECORD:
			if not row.is_empty() and phase == Phase.AFTER:
				var l: Dictionary = row["ledger"]
				v["dheat"] = int(l["heat_after"]) - int(l["heat_before"])
				v["dbank"] = int(l["bank_after"]) - int(l["bank_before"])
		Phase.REPAIR:
			var bp: Dictionary = model.between_preview()
			var ns: L2State = bp["state"]
			v["heat"] = ns.heat
			v["bank"] = ns.bank
			v["dheat"] = ns.heat - s.heat
			v["dbank"] = ns.bank - s.bank
	return v


func _draw_hud() -> void:
	var v := _hud_values()
	# Heat meter with the two band notches and what each adds.
	var hx := 60.0
	var hw := 360.0
	var hy := 20.0
	G.flame(self, Vector2(36, hy + 10), 10)
	draw_rect(Rect2(hx, hy, hw, 20), Color8(30, 34, 56))
	var heat: int = int(v["heat"])
	var dh: int = int(v["dheat"])
	var fillw := hw * clampf(float(heat) / L2Config.HEAT_MAX, 0.0, 1.0)
	var base_w := hw * clampf(float(heat - maxi(0, dh)) / L2Config.HEAT_MAX, 0.0, 1.0)
	draw_rect(Rect2(hx, hy, base_w, 20), G.HEAT)
	if dh > 0:
		draw_rect(Rect2(hx + base_w, hy, fillw - base_w, 20), G.HOLD)
	elif dh < 0:
		draw_rect(Rect2(hx + fillw, hy, base_w - fillw, 20), Color8(255, 110, 40, 90))
	draw_rect(Rect2(hx, hy, hw, 20), G.PANEL_EDGE, false, 2.0)
	for band in [[L2Config.EXTRA_AT, "+1 BEAM"], [L2Config.STRONG_AT, "+2 BEAMS"]]:
		var bxp: float = hx + hw * float(band[0]) / L2Config.HEAT_MAX
		var lit: bool = heat >= int(band[0])
		G.line(self, Vector2(bxp, hy - 5), Vector2(bxp, hy + 25), G.THREAT_LIGHT if lit else G.THREAT_FADE, 3.0)
		G.text(self, Vector2(bxp + 5, hy + 27), "%d: %s" % [band[0], band[1]], 12, G.THREAT_LIGHT if lit else G.DIM)
	G.text(self, Vector2(hx + hw + 10, hy - 3), str(heat), 22, G.HEAT)
	if dh != 0:
		G.text(self, Vector2(hx + hw + 52, hy), "%+d" % dh, 17, G.HOLD if dh > 0 else G.CLEAN)
	# Raid pips.
	G.text(self, Vector2(530, 12), "RAID %d/%d" % [mini(model.raid + 1, L2Config.RAIDS), L2Config.RAIDS], 13, G.DIM)
	for j in range(L2Config.RAIDS):
		var c := Vector2(540 + j * 24, 44)
		if j < model.history.size():
			var h: Dictionary = model.history[j]
			G.disc(self, c, 7, G.CLEAN if h["evaded"] else G.DMG)
		elif j == model.raid:
			G.circle(self, c, 7, G.CELL, 3.0)
		else:
			G.circle(self, c, 7, G.PANEL_EDGE)
	# Home integrity pips (with the projected loss in the forecast).
	G.text(self, Vector2(640, 12), "HOME", 13, G.DIM)
	var hp: int = int(v["hp"])
	var proj: Array = v["proj"]
	for k in range(L2Config.HOME_HP):
		var mode := "full"
		if k >= hp:
			mode = "lost"
		elif phase == Phase.FORECAST and k >= hp - int(proj[0]):
			mode = "saved" if (L2Config.spoof_view() and k < hp - int(proj[1])) else "proj"
		G.pip(self, Vector2(650 + k * 28, 42), 18.0, mode)
	# Bank.
	var bx := 830.0
	G.coin(self, Vector2(bx + 12, 31), 11)
	G.text(self, Vector2(bx + 34, 14), str(v["bank"]), 26, G.CELL)
	if int(v["dbank"]) != 0:
		G.text(self, Vector2(bx + 94, 18), "%+d" % int(v["dbank"]), 18, G.DMG if int(v["dbank"]) < 0 else G.CLEAN)
	G.text(self, Vector2(bx + 140, 20), L2Config.key_label().to_upper(), 13, G.DIM)


func _draw_strip() -> void:
	draw_rect(Rect2(0, STRIP_Y, 1280, 720 - STRIP_Y), Color(0, 0, 0, 0.55))
	var hint := ""
	match phase:
		Phase.CONTACT:
			hint = "Contact. Heat sets the raid's strength. Enter plans the defense."
		Phase.PLAN:
			hint = "Pick a lever (1 2 3), click a node to place it, click a placed lever to take it off. Z undoes. Enter shows the forecast."
		Phase.FORECAST:
			hint = "Forecast: each shape marks what that sealed line would do to the node. B edits the plan. Enter launches the sweep."
		Phase.PLAY:
			hint = "Hands-off sweep. 1 / 2 / 4 speed, S skips. The spoof decision needs you."
		Phase.AFTER:
			hint = "Aftermath. Enter continues."
		Phase.REPAIR:
			hint = "Between raids: click a DOWN asset to repair it (cost shown, paid from the bank). Enter goes on."
		Phase.BREACH:
			hint = "The campaign is lost. Enter shows the leg record."
		Phase.RECORD:
			hint = "Leg record. Enter plays the leg again."
	if status_msg != "":
		hint = status_msg
	G.text(self, Vector2(10, STRIP_Y + 3), hint, 13, G.INK if status_msg != "" else G.DIM)
	var tx := 10.0
	var items := [["SPOOF_VIEW", "SPOOF IN FORECAST: " + L2Config.toggles["SPOOF_VIEW"].to_upper(), "F1"],
		["KEY_LABEL", "CURRENCY: " + L2Config.key_label().to_upper(), "F2"]]
	for it in items:
		var label: String = "%s  [%s]" % [it[1], it[2]]
		var w := G.text_w(label, 13) + 20.0
		var r := Rect2(tx, STRIP_Y + 21, w, 22)
		G.panel(self, r, G.PANEL_EDGE, Color8(60, 52, 24) if _hot(r) else G.PANEL, 1.0)
		G.text_c(self, r.get_center(), label, 13, G.CELL)
		_add_hit(r, "tog:" + String(it[0]))
		tx += w + 8.0
	G.text(self, Vector2(tx + 14, STRIP_Y + 24), "L2 SWEEP lab  |  leg %d  |  designer toggles" % model.seed_id, 12, G.DIM)


# ---- the network ----
## Draw HOME: the server glyph, its integrity pips, a ghost ring.
func _draw_home(p: Vector2, hp: int, pl: Dictionary, loss: int = 0) -> void:
	var ghost: bool = (pl["ghost"] as Array).has(model.home())
	G.home_server(self, p, 28.0, G.INK)
	if ghost:
		G.dashed_ring(self, p, 38.0, G.CELL, 4.0)
		G.flame(self, p + Vector2(34, -32), 7)
	for k in range(L2Config.HOME_HP):
		var mode := "full" if k < hp else "lost"
		G.pip(self, p + Vector2((k - 1) * 18.0, 44.0), 12.0, mode)


## One node. `status` is the cell -> status map to show.
func _draw_node(c: Vector2i, status: Dictionary, hp: int, pl: Dictionary) -> void:
	var p := nx(c)
	if c == model.home():
		_draw_home(p, hp, pl)
		return
	if (pl["decoys"] as Array).has(c):
		var pts := PackedVector2Array([p + Vector2(0, -26), p + Vector2(26, 0), p + Vector2(0, 26), p + Vector2(-26, 0)])
		draw_colored_polygon(pts, G.PANEL)
		pts.append(pts[0])
		draw_polyline(pts, G.CELL, 4.0, true)
		draw_colored_polygon(PackedVector2Array([p + Vector2(0, -10), p + Vector2(10, 0), p + Vector2(0, 10), p + Vector2(-10, 0)]), G.CELL)
		return
	if not model.values().has(c):
		G.disc(self, p, 8, G.EMPTY_NODE)
		return
	var v: int = model.values()[c]
	var st: String = status[c]
	var ghost: bool = (pl["ghost"] as Array).has(c)
	var dark: bool = (pl["dark"] as Array).has(c)
	var fill := G.PANEL
	var edge := G.CELL
	match st:
		"DOWN":
			fill = GREY
			edge = GREY_EDGE
		"TAKEN":
			fill = Color8(22, 30, 74)
			edge = G.THREAT
	if dark:
		fill = Color8(10, 10, 16)
		edge = G.DIM
	G.disc(self, p, NODE_R, fill)
	G.circle(self, p, NODE_R, edge, 4.0)
	if ghost:
		G.dashed_ring(self, p, NODE_R + 5, G.CELL, 4.0)
		G.flame(self, p + Vector2(32, -28), 7)
	match st:
		"OK":
			G.coin(self, p + Vector2(-9, 0), 8, G.DIM if dark else G.CELL)
			G.text(self, p + Vector2(3, -11), str(v), 19, G.DIM if dark else G.INK)
		"DOWN":
			G.bolt(self, p, 19.0, G.INK)
			G.text_c(self, p + Vector2(33, -26), str(v), 14, G.DIM)
		"TAKEN":
			G.corp(self, p, 21.0)
			G.text_c(self, p + Vector2(33, -26), str(v), 14, G.DIM)
			G.line(self, p + Vector2(23, 40), p + Vector2(39, 20), G.DMG, 2.0)


func _draw_net(show_hit_areas: bool, status: Dictionary = {}, hp: int = -1, pl: Dictionary = {}) -> void:
	var st: Dictionary = status if not status.is_empty() else model.state.status
	var h: int = hp if hp >= 0 else model.state.home_hp
	var plan: Dictionary = pl if not pl.is_empty() else model.plan
	for c in L2Rules.nodes():
		_draw_node(c, st, h, plan)
		if show_hit_areas:
			_cell_hit(c)


func _draw_legend() -> void:
	var y := 648.0
	var x := 24.0
	var items := ["decoy", "ghost", "down", "taken", "home"]
	var names := {"decoy": "DECOY", "ghost": "GHOST", "down": "DOWN", "taken": "TAKEN", "home": "HOME"}
	for it in items:
		var c := Vector2(x + 12, y)
		match it:
			"decoy":
				draw_polyline(PackedVector2Array([c + Vector2(0, -11), c + Vector2(11, 0), c + Vector2(0, 11), c + Vector2(-11, 0), c + Vector2(0, -11)]), G.CELL, 3.0, true)
			"ghost":
				G.dashed_ring(self, c, 10, G.CELL, 3.0)
			"down":
				G.disc(self, c, 11, GREY)
				G.bolt(self, c, 9.0)
			"taken":
				G.corp(self, c, 11.0)
			"home":
				G.home_server(self, c, 10.0, G.INK)
		G.text(self, Vector2(x + 30, y - 8), names[it], 13, G.DIM)
		x += 30 + G.text_w(names[it], 13) + 26


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


## Where a known beam stops in the plan: at the first decoy on it.
func _known_u(line: Array, g: Dictionary) -> float:
	for i in range(line.size()):
		if (model.plan["decoys"] as Array).has(line[i]):
			return i + 1.0
	return float((g["pts"] as Array).size() + 1)


func _draw_known_beams(extra: int, with_plan: bool) -> void:
	for kb: Dictionary in _known_beams(extra):
		var g := _beam_geom(kb["id"])
		var u: float = _known_u(kb["line"], g) if with_plan else float((g["pts"] as Array).size() + 1)
		_draw_path(_path(g, u), G.THREAT, 6.0)
		_start_badge(g, kb["badge"])


## The sealed candidates: dashed lines told apart by end shape and dash pattern. `fade` dims the others.
func _draw_candidates(only: int = -1, fade: float = 0.0) -> void:
	var offs := _offsets()
	var cands: Array = model.raid_data()["cands"]
	for i in range(cands.size()):
		var g := _geom(cands[i], offs[3 + i])
		var col := G.THREAT_LIGHT
		if only >= 0 and i != only:
			col = G.THREAT_LIGHT.lerp(G.THREAT_FADE, fade)
		_draw_dashed_path(_path(g, float(g["pts"].size() + 1)), col, DASHES[i], 4.0)
		var a: Vector2 = g["a"]
		G.cand_shape(self, a, i, 11.0, col, G.BG)
		if only >= 0 and i == only:
			continue	## the lit beam draws its own badge
		G.badge(self, a - (g["dir"] as Vector2) * 28.0, "?", col.darkened(0.2) if only >= 0 else G.THREAT)


## Thin dashed hunter columns: the hunter turns down the column of the first touch.
func _draw_hunter_plan(fc: Array) -> void:
	var known_first := L2Rules.NONE
	for b: Dictionary in (fc[0]["beams"] as Array):
		if b["id"] in ["b2", "hunter"]:
			continue
		for stp: Dictionary in b["steps"]:
			if stp["kind"] in ["asset", "home", "decoy"]:
				known_first = stp["cell"]
				break
		if known_first != L2Rules.NONE:
			break
	if known_first != L2Rules.NONE:
		_hunter_col(known_first.x, G.THREAT_LIGHT, 3.0, "3", Vector2(10, 6), 0.0)
		return
	var own_needed := false
	for i in range(fc.size()):
		var f: Vector2i = fc[i]["first"]
		if f != L2Rules.NONE:
			_hunter_col(f.x, G.THREAT_LIGHT.darkened(0.25), 2.0, "", DASHES[i], (i - 1) * 12.0, i)
		else:
			own_needed = true
	if own_needed:
		_hunter_col((model.raid_data()["own3"][0] as Vector2i).x, G.THREAT_LIGHT.darkened(0.45), 2.0, "3", Vector2(4, 8), 0.0)


func _hunter_col(x: int, col: Color, w: float, badge_s: String, dash: Vector2, off: float, shape_i: int = -1) -> void:
	var g := _geom(L2Rules.column(x), off + _h_off(x))
	_draw_dashed_path(_path(g, float(g["pts"].size() + 1)), col, dash, w)
	var b: Vector2 = g["b"]
	if shape_i >= 0:
		G.cand_shape(self, b + Vector2(0, 18), shape_i, 7.0, col, G.BG, 2.0)
	if badge_s != "":
		G.badge(self, _mid(g), badge_s)


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
			G.dashed_ring(self, Vector2(x, origin.y), 13.0, G.THREAT_LIGHT if not dim else G.THREAT_FADE, 3.0)
			G.text_c(self, Vector2(x, origin.y), "?", 15, G.INK)
		else:
			G.badge(self, Vector2(x, origin.y), s, col)
		x += 40.0


func _draw_contact() -> void:
	var s := model.state
	var extra: int = L2Rules.extra_count(s.heat)
	_draw_net(false)
	_draw_known_beams(extra, false)
	# Raid strength by Heat band.
	G.text(self, Vector2(PANEL_X, 80), "THE RAID'S STRENGTH, BY HEAT", 14, G.DIM)
	var bands := [[0, "HEAT UNDER %d" % L2Config.EXTRA_AT, "Beam 1, a sealed beam, the hunter."],
		[1, "HEAT %d AND UP" % L2Config.EXTRA_AT, "Adds a known beam after beam 1."],
		[2, "HEAT %d AND UP" % L2Config.STRONG_AT, "Adds a second known beam."]]
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
		G.text(self, Vector2(PANEL_X, 416), "Between raids", 14, G.DIM)
		G.flame(self, Vector2(PANEL_X + 10, 452), 9)
		G.text(self, Vector2(PANEL_X + 26, 441), "+%d" % L2Config.RUN_HEAT, 20, G.HEAT)
		G.coin(self, Vector2(PANEL_X + 110, 452), 9)
		G.text(self, Vector2(PANEL_X + 128, 441), "+%d" % int(rn["income"]), 20, G.CELL)
		if int(rn["repair_cost"]) > 0:
			G.text(self, Vector2(PANEL_X + 200, 444), "repair -%d" % int(rn["repair_cost"]), 14, G.DIM)
	_draw_status_summary(Vector2(PANEL_X, 478))
	_btn(Rect2(PANEL_X, 566, PANEL_W, 56), "PLAN THE DEFENSE  [Enter]", "next", true, 20)
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
		var at: int = L2Config.EXTRA_AT if k == 0 else L2Config.STRONG_AT
		var cx := 180.0 + k * 100.0
		var passed: bool = heat >= at
		G.shield(self, Vector2(cx, y - 2), 14, G.THREAT if passed else G.THREAT_FADE)
		G.text(self, Vector2(cx - 20, y + 20), "LINE %d" % at, 12, G.THREAT_LIGHT if passed else G.DIM)
	G.arrow(self, Vector2(400, y), Vector2(450, y), G.THREAT, 4.0)
	_band_chips(Vector2(484, y), extra, false)
	G.text(self, Vector2(466, y + 20), "%d KNOWN BEAM%s" % [1 + extra, "" if extra == 0 else "S"], 12, G.THREAT_LIGHT)


# ---- plan / forecast ----
func _draw_plan() -> void:
	var fc_mode: bool = phase == Phase.FORECAST
	var fc: Array = model.forecast()
	_draw_net(true)
	_draw_known_beams(model.extra_now(), true)
	_draw_candidates()
	_draw_hunter_plan(fc)
	if fc_mode:
		_draw_forecast_marks(fc)
	if sel_lever != "":
		for c in L2Rules.nodes():
			var p := nx(c)
			if Rect2(p - Vector2(46, 46), Vector2(92, 92)).has_point(mouse):
				var ok := model.why_not(sel_lever, c) == ""
				G.circle(self, p, 40, G.CLEAN if ok else G.DMG, 3.0)
	G.text(self, Vector2(PANEL_X, 78), "LEVERS", 14, G.DIM)
	var y := 98.0
	for lv in L2Model.LEVERS:
		_draw_lever_card(lv, Rect2(PANEL_X, y, PANEL_W, 60))
		y += 66.0
	# The held spoof.
	var sr := Rect2(PANEL_X, y, PANEL_W, 54)
	G.panel(self, sr, G.CLEAN)
	G.spoof_key(self, Vector2(PANEL_X + 44, y + 27), G.CLEAN)
	G.text(self, Vector2(PANEL_X + 90, y + 6), "SPOOF  x1", 17, G.CLEAN)
	G.text(self, Vector2(PANEL_X + 90, y + 30), "Held: after the reveal, beam 2 skips one node.", 13, G.DIM)
	y += 62.0
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
	_draw_legend()


func _draw_lever_card(lv: String, r: Rect2) -> void:
	var used: int = (model.plan[L2Model.ALLOC_KEY[lv]] as Array).size()
	var cap: int = {"ghost": L2Config.MAX_GHOST, "decoy": L2Config.MAX_DECOY, "dark": L2Config.MAX_DARK}[lv]
	var sel := sel_lever == lv
	G.panel(self, r, G.CELL if sel else G.PANEL_EDGE, Color8(60, 52, 24) if (sel or _hot(r)) else G.PANEL, 3.0 if sel else 2.0)
	_add_hit(r, "lever:" + lv)
	var c := Vector2(r.position.x + 38, r.position.y + 30)
	match lv:
		"ghost":
			G.dashed_ring(self, c, 18, G.CELL if used > 0 else G.DIM, 4.0)
		"decoy":
			var col := G.CELL if used > 0 else G.DIM
			draw_polyline(PackedVector2Array([c + Vector2(0, -19), c + Vector2(19, 0), c + Vector2(0, 19), c + Vector2(-19, 0), c + Vector2(0, -19)]), col, 3.0, true)
		"dark":
			G.disc(self, c, 18, Color8(10, 10, 16))
			G.circle(self, c, 18, G.DIM, 3.0)
	var nm: Array = LEVER_TEXT[lv]
	G.text(self, Vector2(r.position.x + 74, r.position.y + 5), "%s  [%s]" % [nm[0], nm[2]], 16, G.INK)
	G.text(self, Vector2(r.position.x + 74, r.position.y + 24), nm[1], 12, G.DIM)
	var cx := r.position.x + 74
	var cy := r.position.y + 42
	match lv:
		"ghost":
			G.flame(self, Vector2(cx + 6, cy + 7), 7)
			G.text(self, Vector2(cx + 20, cy), "+%d Heat now" % L2Config.GHOST_HEAT, 13, G.HEAT)
		"decoy":
			G.coin(self, Vector2(cx + 6, cy + 7), 6)
			G.text(self, Vector2(cx + 20, cy), "-%d %s now" % [L2Config.DECOY_COST, L2Config.key_label()], 13, G.CELL)
		"dark":
			var loss := 0
			for dc: Vector2i in model.plan["dark"]:
				if model.state.status[dc] == "OK":
					loss += L2Rules.idiv(int(model.values()[dc]), L2Config.INCOME_DIV)
			G.coin(self, Vector2(cx + 6, cy + 7), 6, G.DIM)
			G.line(self, Vector2(cx - 1, cy + 14), Vector2(cx + 13, cy), G.DMG, 3.0)
			G.text(self, Vector2(cx + 20, cy), "income lost this interval: %d" % loss, 13, G.DIM)
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
		line1 = "Heat %d passed %d: a known beam (+) is added." % [heat, L2Config.EXTRA_AT]
	elif extra == 2:
		line1 = "Heat %d passed %d: two known beams (+ ++)." % [heat, L2Config.STRONG_AT]
	G.text(self, Vector2(r.position.x + 16, y + 94), line1, 13, G.INK)
	var nxt := ""
	if extra == 0:
		nxt = "%d more Heat adds a known beam." % (L2Config.EXTRA_AT - heat)
	elif extra == 1:
		nxt = "%d more Heat adds a second known beam." % (L2Config.STRONG_AT - heat)
	else:
		nxt = "Already at the strongest raid."
	G.text(self, Vector2(r.position.x + 16, y + 116), nxt, 13, G.DIM)
	if (model.plan["ghost"] as Array).size() > 0:
		var base_extra: int = L2Rules.extra_count(model.state.heat)
		if extra > base_extra:
			G.text(self, Vector2(r.position.x + 16, y + 142), "The ghost's +%d Heat added a beam." % L2Config.GHOST_HEAT, 13, G.HOLD)
		else:
			G.text(self, Vector2(r.position.x + 16, y + 142), "The ghost's +%d Heat adds no beam." % L2Config.GHOST_HEAT, 13, G.DIM)
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
		G.text(self, Vector2(cx + 24, y - 8), "-%d" % int(sm["home"]), 15, G.DMG)
		cx += 50.0
		shown = true
	if not shown:
		draw_polyline(PackedVector2Array([Vector2(cx + 9, y - 10), Vector2(cx + 19, y), Vector2(cx + 9, y + 10), Vector2(cx - 1, y), Vector2(cx + 9, y - 10)]), G.CELL, 3.0, true)
		G.text(self, Vector2(cx + 26, y - 8), "DECOY ONLY", 12, G.DIM)
		cx += 100.0
	return cx


func _draw_forecast_panel(fc: Array, y: float) -> void:
	var r := Rect2(PANEL_X, y, PANEL_W, 188)
	G.panel(self, r)
	var sv := L2Config.spoof_view()
	G.text(self, Vector2(r.position.x + 14, y + 8), "IF THE SEALED LINE IS", 13, G.DIM)
	G.text(self, Vector2(r.position.x + 200, y + 8), "HOLD", 13, G.DIM)
	if sv:
		G.spoof_key(self, Vector2(r.position.x + 330, y + 17), G.CLEAN)
		G.text(self, Vector2(r.position.x + 362, y + 8), "BEST SPOOF", 13, G.CLEAN)
	for i in range(fc.size()):
		var ry := y + 34.0 + i * 44.0
		var f: Dictionary = fc[i]
		G.cand_shape(self, Vector2(r.position.x + 28, ry + 17), i, 11.0, G.THREAT_LIGHT, G.BG)
		_chips(r.position.x + 62, ry + 17, f["summary"])
		if sv:
			G.arrow(self, Vector2(r.position.x + 238, ry + 17), Vector2(r.position.x + 290, ry + 17), G.CLEAN, 2.0, 7.0)
			if f["saves"]:
				_chips(r.position.x + 306, ry + 17, f["best_summary"])
			else:
				G.text(self, Vector2(r.position.x + 306, ry + 9), "no spoof helps", 13, G.DIM)
	var wl: Array = model.worst_home_loss()
	var py := y + 168.0
	G.text(self, Vector2(r.position.x + 14, py - 8), "HOME", 13, G.DIM)
	var hp: int = model.state.home_hp
	for k in range(L2Config.HOME_HP):
		var mode := "full"
		if k >= hp - int(wl[0]):
			mode = "saved" if (sv and k < hp - int(wl[1])) else "proj"
		G.pip(self, Vector2(r.position.x + 78 + k * 24, py), 14.0, mode)
	var msg := "worst case: lose %d" % int(wl[0])
	if sv:
		msg += ", with the best spoof: lose %d" % int(wl[1])
	G.text(self, Vector2(r.position.x + 156, py - 8), msg, 13, G.INK if int(wl[0]) > 0 else G.DIM)


## FORECAST: on each node, one slot per sealed line that touches it (shape = the line, glyph = the outcome); a teal
## mark where that line's best spoof would skip.
func _draw_forecast_marks(fc: Array) -> void:
	var sv := L2Config.spoof_view()
	for i in range(fc.size()):
		var f: Dictionary = fc[i]
		var done: Array = []
		for o: Dictionary in f["outcomes"]:
			var c: Vector2i = o["cell"]
			if done.has(c):
				continue
			done.append(c)
			var p := nx(c) + Vector2((i - 1) * 46.0, 58.0)
			G.cand_shape(self, p + Vector2(-9, 0), i, 7.0, G.THREAT_LIGHT, G.BG, 2.0)
			match o["outcome"]:
				"DOWN":
					G.disc(self, p + Vector2(9, 0), 8, GREY)
					G.bolt(self, p + Vector2(9, 0), 6.0)
				"TAKEN":
					G.corp(self, p + Vector2(9, 0), 8.0)
				"HOME":
					G.text_c(self, p + Vector2(10, 0), "-1", 13, G.DMG)
				_:
					draw_polyline(PackedVector2Array([p + Vector2(9, -6), p + Vector2(15, 0), p + Vector2(9, 6), p + Vector2(3, 0), p + Vector2(9, -6)]), G.CELL, 2.0, true)
		if sv and f["saves"]:
			var sp: Vector2i = f["best_spoof"]
			var q := nx(sp) + Vector2((i - 1) * 30.0, -50.0)
			G.disc(self, q, 11, G.BG)
			G.circle(self, q, 11, G.CLEAN, 2.5)
			G.cand_shape(self, q, i, 5.0, G.CLEAN, Color(0, 0, 0, 0), 2.0)


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
	_draw_net_play(sn)
	var st: int = p.state
	var cur: int = p.order.size()
	if st in [L2Play.S.BEAM, L2Play.S.UNSEAL, L2Play.S.DECIDE, L2Play.S.TURN]:
		cur = p.beam_idx()
	var b2_i: int = p.order.find("b2")
	# Sealed candidates until beam 2 unseals.
	if cur < b2_i:
		_draw_candidates()
	elif st == L2Play.S.UNSEAL:
		_draw_candidates(L2Config.REVEAL, clampf(p.t / L2Config.UNSEAL_T, 0.0, 1.0))
	else:
		_draw_candidates(L2Config.REVEAL, 0.8)
	for k in range(p.res["beams"].size()):
		var b: Dictionary = p.res["beams"][k]
		var id: String = b["id"]
		if id == "hunter" and cur < k:
			continue
		var bs := _beam_state(k, cur)
		var g := _beam_geom(id, b["line"])
		var u_full := _beam_u(b, g)
		var badge_s := {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[id] as String
		if id == "b2":
			if cur < b2_i:
				continue
			var lit := G.THREAT_LIGHT.lerp(G.THREAT, 0.5)
			if st == L2Play.S.UNSEAL or st == L2Play.S.DECIDE:
				var a := clampf(p.t / L2Config.UNSEAL_T, 0.0, 1.0) if st == L2Play.S.UNSEAL else 1.0
				_draw_path(_path(g, float(g["pts"].size() + 1)), Color(lit.r, lit.g, lit.b, 0.35 + 0.65 * a), 5.0)
			elif bs == "now":
				_draw_path(_path(g, float(g["pts"].size() + 1)), G.THREAT_FADE, 4.0, false)
				_draw_path(_path(g, minf(p.head(), u_full)), G.THREAT_LIGHT, 8.0)
			else:
				_draw_path(_path(g, u_full), G.THREAT, 6.0)
		elif id == "hunter":
			if st == L2Play.S.TURN:
				_draw_hunter_turn(g, b)
			elif bs == "now":
				_draw_path(_path(g, float(g["pts"].size() + 1)), G.THREAT_FADE, 4.0, false)
				_draw_path(_path(g, minf(p.head(), u_full)), G.THREAT_LIGHT, 8.0)
			else:
				_draw_path(_path(g, u_full), G.THREAT, 5.0)
		else:
			match bs:
				"now":
					_draw_path(_path(g, u_full), G.THREAT_FADE, 4.0, false)
					_draw_path(_path(g, minf(p.head(), u_full)), G.THREAT_LIGHT, 8.0)
				"done":
					_draw_path(_path(g, u_full), G.THREAT, 6.0)
				_:
					_draw_path(_path(g, u_full), G.THREAT_FADE, 3.0, false)
		if id == "hunter":
			G.badge(self, _mid(g), badge_s)
		else:
			_start_badge(g, badge_s)
	# The spoof decision.
	if st == L2Play.S.DECIDE:
		for c: Vector2i in p.b2:
			var pc := nx(c)
			var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 220.0)
			G.dashed_ring(self, pc, NODE_R + 12 + 3.0 * pulse, G.CLEAN, 4.0)
			_cell_hit(c)
	# Pulses for the steps just taken.
	for e: Dictionary in p.events:
		var age: float = p.clock - float(e["at"])
		if age < 0.7:
			var pc := nx(e["cell"])
			var col := _pulse_col(e)
			var a := 1.0 - age / 0.7
			G.circle(self, pc, NODE_R + 4 + age * 40.0, Color(col.r, col.g, col.b, a), 4.0)
	_draw_play_panel()


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
	return G.THREAT_FADE


func _draw_hunter_turn(g: Dictionary, b: Dictionary) -> void:
	var a3 := clampf(play.t / L2Config.TURN_T, 0.0, 1.0)
	var first: Vector2i = play.hunter_from()
	var col := Color(G.THREAT_LIGHT.r, G.THREAT_LIGHT.g, G.THREAT_LIGHT.b, a3)
	if first != L2Rules.NONE:
		var pf := nx(first)
		G.circle(self, pf, NODE_R + 8 + 6.0 * sin(play.t * 8.0), G.DMG, 4.0)
		_draw_dashed_path(_path(g, float(g["pts"].size() + 1)), col, Vector2(10, 6), 4.0)
		G.text(self, pf + Vector2(36, -50), "TURNS", 13, G.INK)
	else:
		_draw_dashed_path(_path(g, float(g["pts"].size() + 1)), col, Vector2(4, 8), 4.0)
		G.text_c(self, (g["b"] as Vector2) + Vector2(0, 40), "OWN LINE", 13, G.INK)


## Nodes during the sweep: the statuses as the sweep has left them; hidden near misses keep a ring.
func _draw_net_play(sn: Dictionary) -> void:
	for c in L2Rules.nodes():
		_draw_node(c, sn["status"], int(sn["home_hp"]), play.alloc)
	for e: Dictionary in play.events:
		if e["kind"] == "hidden":
			G.circle(self, nx(e["cell"]), NODE_R + 10, G.INK, 2.0)
	if play.spoof_used and play.state != L2Play.S.DECIDE:
		G.dashed_ring(self, nx(play.spoof), NODE_R + 14, G.CLEAN, 3.0)


func _draw_play_panel() -> void:
	var p := play
	G.text(self, Vector2(PANEL_X, 78), "SWEEP", 14, G.DIM)
	# Beam track.
	var cur := -1
	if p.state in [L2Play.S.BEAM, L2Play.S.UNSEAL, L2Play.S.DECIDE, L2Play.S.TURN]:
		cur = p.beam_idx()
	var ids: Array = p.order
	for i in range(ids.size()):
		var c := Vector2(PANEL_X + 24 + i * 56, 114)
		var done: bool = i < cur or cur < 0
		var active: bool = i == cur
		var s: String = {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[ids[i]]
		G.disc(self, c, 17, G.THREAT if (done or active) else G.PANEL)
		G.circle(self, c, 17, G.CELL if active else G.PANEL_EDGE, 3.0 if active else 2.0)
		G.text_c(self, c, s, 17, G.INK)
		if i < ids.size() - 1:
			G.line(self, c + Vector2(22, 0), c + Vector2(34, 0), G.THREAT if done else G.PANEL_EDGE, 3.0)
	G.text(self, Vector2(PANEL_X + 24 + ids.size() * 56 + 6, 104), _beat_name(), 14, G.INK)
	# Speed controls.
	var labels := ["1x", "2x", "4x"]
	for i in range(3):
		var r := Rect2(PANEL_X + i * 84, 144, 76, 36)
		G.panel(self, r, G.CELL if speed_i == i else G.PANEL_EDGE, Color8(60, 52, 24) if (speed_i == i or _hot(r)) else G.PANEL, 3.0 if speed_i == i else 2.0)
		G.text_c(self, r.get_center(), labels[i], 17, G.CELL if speed_i == i else G.INK)
		_add_hit(r, "speed:%d" % i)
	var rs := Rect2(PANEL_X + 252, 144, 100, 36)
	G.panel(self, rs, G.PANEL_EDGE, Color8(60, 52, 24) if _hot(rs) else G.PANEL, 2.0)
	G.text_c(self, rs.get_center(), "SKIP [S]", 15, G.INK)
	_add_hit(rs, "skip")
	_draw_spoof_box(Rect2(PANEL_X, 194, PANEL_W, 226))
	_draw_hit_log(432.0)


func _draw_spoof_box(box: Rect2) -> void:
	var p := play
	var waiting := p.state == L2Play.S.DECIDE
	G.panel(self, box, G.CLEAN if waiting else G.PANEL_EDGE, G.PANEL, 3.0 if waiting else 2.0)
	G.spoof_key(self, Vector2(box.position.x + 40, box.position.y + 24), G.CLEAN)
	G.text(self, Vector2(box.position.x + 82, box.position.y + 6), "SPOOF", 17, G.CLEAN)
	var x0 := box.position.x + 16
	var y := box.position.y
	if waiting:
		G.text(self, Vector2(x0, y + 46), "Beam 2 is unsealed. Click a node on the lit line:", 13, G.INK)
		var rows: Array = [L2Rules.NONE] + p.b2
		var ry := y + 70.0
		for c: Vector2i in rows:
			var pr: Dictionary = p.preview(c)
			var sm := L2Rules.summary(p.before, pr["touches"])
			if c == L2Rules.NONE:
				G.text(self, Vector2(x0, ry + 4), "HOLD [H]", 13, G.INK)
			else:
				G.circle(self, Vector2(x0 + 12, ry + 12), 11, G.CLEAN, 2.0)
				if c == model.home():
					G.home_server(self, Vector2(x0 + 12, ry + 12), 6.0, G.INK)
				elif model.values().has(c):
					G.text_c(self, Vector2(x0 + 12, ry + 12), str(model.values()[c]), 12, G.INK)
				else:
					G.disc(self, Vector2(x0 + 12, ry + 12), 3, G.DIM)
				G.text(self, Vector2(x0 + 30, ry + 4), "skip", 13, G.DIM)
			G.arrow(self, Vector2(x0 + 92, ry + 12), Vector2(x0 + 130, ry + 12), G.DIM, 2.0, 6.0)
			_chips(x0 + 142, ry + 12, sm)
			ry += 28.0
	elif p.spoof_used:
		G.text(self, Vector2(x0, y + 46), "Spoof used: beam 2 skipped the ringed node.", 13, G.CLEAN)
		var sm2 := L2Rules.summary(p.before, p.res["touches"])
		G.text(self, Vector2(x0, y + 72), "Result with it:", 13, G.DIM)
		_chips(x0 + 120, y + 80, sm2)
	elif p.state in [L2Play.S.BEAM, L2Play.S.UNSEAL] and p.order.find("b2") > maxi(p.beam_idx(), -1):
		G.text(self, Vector2(x0, y + 46), "Held for after the reveal.", 13, G.DIM)
	else:
		G.text(self, Vector2(x0, y + 46), "Held, not used.", 13, G.DIM)
	if waiting:
		_btn(Rect2(box.end.x - 150, box.position.y + 8, 136, 30), "HOLD  [H]", "hold", true, 14)


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
	match play.state:
		L2Play.S.BEAM:
			return {"b1": "BEAM 1", "extra": "KNOWN BEAM +", "extra2": "KNOWN BEAM ++", "b2": "BEAM 2", "hunter": "THE HUNTER"}[play.order[play.bi]]
		L2Play.S.UNSEAL:
			return "BEAM 2 UNSEALS"
		L2Play.S.DECIDE:
			return "SPOOF DECISION"
		L2Play.S.TURN:
			return "THE HUNTER TURNS"
	return "DONE"


# ---- aftermath ----
## A tag stamped on a node: glyph + short word.
func _node_tag(c: Vector2i, kind: String) -> void:
	var p := nx(c) + Vector2(-37, 34)
	var r := Rect2(p.x, p.y, 74, 22)
	var col := G.INK
	match kind:
		"DOWN":
			col = G.INK
		"TAKEN":
			col = G.THREAT_LIGHT
		"HOME":
			col = G.DMG
	G.panel(self, r, col, Color8(14, 16, 32, 230), 2.0)
	var gc := Vector2(r.position.x + 12, r.position.y + 11)
	match kind:
		"DOWN":
			G.bolt(self, gc, 8.0)
			G.text(self, Vector2(r.position.x + 24, r.position.y + 3), "DOWN", 13, col)
		"TAKEN":
			G.corp(self, gc, 8.0)
			G.text(self, Vector2(r.position.x + 24, r.position.y + 3), "TAKEN", 13, col)
		"HOME":
			G.home_server(self, gc, 7.0, G.DMG)
			G.text(self, Vector2(r.position.x + 24, r.position.y + 3), "HOME -1", 13, col)
		_:
			draw_polyline(PackedVector2Array([gc + Vector2(0, -8), gc + Vector2(8, 0), gc + Vector2(0, 8), gc + Vector2(-8, 0), gc + Vector2(0, -8)]), G.CELL, 2.0, true)
			G.text(self, Vector2(r.position.x + 24, r.position.y + 3), "DECOY", 13, G.CELL)


func _draw_after() -> void:
	var after: L2State = row["after_raid"]
	_draw_net(false, after.status, after.home_hp, row["alloc"])
	for b: Dictionary in row["beams"]:
		var g := _beam_geom(b["id"], b["line"])
		_draw_path(_path(g, _beam_u(b, g)), G.THREAT_FADE.lerp(G.THREAT, 0.5), 4.0)
		var badge_s := {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[b["id"]] as String
		if b["id"] == "hunter":
			G.badge(self, _mid(g), badge_s)
		else:
			_start_badge(g, badge_s)
	var done: Array = []
	for o: Dictionary in row["outcomes"]:
		if not done.has(o["cell"]):
			done.append(o["cell"])
			_node_tag(o["cell"], o["outcome"])
	var sm: Dictionary = row["summary"]
	if row["evaded"]:
		G.stamp(self, Vector2(1010, 120), "EVADED", G.CLEAN, 44, "nothing touched")
	else:
		var parts: Array = []
		if int(sm["down"]) > 0:
			parts.append("%d DOWN" % int(sm["down"]))
		if int(sm["taken"]) > 0:
			parts.append("%d TAKEN" % int(sm["taken"]))
		if int(sm["home"]) > 0:
			parts.append("HOME -1")
		G.stamp(self, Vector2(1010, 120), "CELL HOLDS", G.HOLD, 40, "  ".join(parts) if not parts.is_empty() else "a decoy took the beam")
	_draw_ledger(row["ledger"])
	var last := model.leg_over()
	_btn(Rect2(PANEL_X, 628, PANEL_W, 40), ("LEG RECORD  [Enter]" if last else "BETWEEN RAIDS  [Enter]"), "next", true, 18)
	_draw_legend()


func _ledger_row(y: float, label: String, amount: String, col: Color, glyph: String = "") -> void:
	G.text(self, Vector2(PANEL_X + 20, y), label, 15, G.INK)
	G.text_r(self, Vector2(PANEL_X + PANEL_W - 20, y), amount, 17, col)
	match glyph:
		"coin":
			G.coin(self, Vector2(PANEL_X + 320, y + 9), 7, col)
		"flame":
			G.flame(self, Vector2(PANEL_X + 320, y + 10), 7, col)


func _draw_ledger(l: Dictionary) -> void:
	G.panel(self, Rect2(PANEL_X, 190, PANEL_W, 428))
	var y := 200.0
	G.coin(self, Vector2(PANEL_X + 28, y + 10), 10)
	G.text(self, Vector2(PANEL_X + 50, y), L2Config.key_label().to_upper(), 15, G.DIM)
	y += 26.0
	_ledger_row(y, "BEFORE", str(l["bank_before"]), G.INK, "coin")
	y += 24.0
	if int(l["decoy"]) > 0:
		_ledger_row(y, "DECOY", "-%d" % int(l["decoy"]), G.DMG, "coin")
		y += 24.0
	draw_line(Vector2(PANEL_X + 20, y + 2), Vector2(PANEL_X + PANEL_W - 20, y + 2), G.PANEL_EDGE, 2.0)
	y += 6.0
	_ledger_row(y, "AFTER THE RAID", str(l["bank_after"]), G.CELL, "coin")
	y += 38.0
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
	draw_line(Vector2(PANEL_X + 20, y + 2), Vector2(PANEL_X + PANEL_W - 20, y + 2), G.PANEL_EDGE, 2.0)
	y += 6.0
	_ledger_row(y, "AFTER THE RAID", str(l["heat_after"]), G.HEAT, "flame")
	y += 30.0
	G.text(self, Vector2(PANEL_X + 20, y), "The sweep ran at Heat %d: %d known beam%s." % [l["run_heat"], 1 + int(l["extra"]), "" if int(l["extra"]) == 0 else "s"], 12, G.DIM)
	y += 30.0
	G.home_server(self, Vector2(PANEL_X + 28, y + 12), 9.0, G.INK)
	G.text(self, Vector2(PANEL_X + 50, y), "HOME", 15, G.DIM)
	for k in range(L2Config.HOME_HP):
		var mode := "full" if k < int(l["home_after"]) else "lost"
		G.pip(self, Vector2(PANEL_X + 150 + k * 28, y + 10), 18.0, mode)
	G.text_r(self, Vector2(PANEL_X + PANEL_W - 20, y), "%d -> %d" % [l["home_before"], l["home_after"]], 17, G.DMG if int(l["home_lost"]) > 0 else G.INK)
	y += 36.0
	var after: L2State = row["after_raid"]
	G.text(self, Vector2(PANEL_X + 20, y), "Network: %d OK, %d DOWN, %d TAKEN" % [after.count("OK"), after.count("DOWN"), after.count("TAKEN")], 14, G.INK)
	y += 24.0
	G.text(self, Vector2(PANEL_X + 20, y), "Leg value now: %d" % model.final_score(), 14, G.DIM)


# ---- between raids ----
func _draw_repair() -> void:
	var s := model.state
	var bp: Dictionary = model.between_preview()
	var dark: Array = row["alloc"]["dark"]
	var shown_status: Dictionary = s.status.duplicate()
	for pc: Vector2i in model.pending_repairs:
		shown_status[pc] = "OK"
	_draw_net(false, shown_status, s.home_hp, {"ghost": [], "dark": dark, "decoys": []})
	var vals: Dictionary = model.values()
	for c: Vector2i in s.status:
		var pp := nx(c)
		if s.status[c] == "DOWN":
			var cost := L2Rules.idiv(int(vals[c]), L2Config.REPAIR_DIV)
			var picked: bool = model.pending_repairs.has(c)
			var affordable: bool = picked or cost <= model.repair_budget()
			var col := G.CLEAN if picked else (G.CELL if affordable else G.DIM)
			G.circle(self, pp, NODE_R + 8, col, 4.0 if picked else 3.0)
			var tag := Rect2(pp.x - 36, pp.y + 34, 72, 22)
			G.panel(self, tag, col, G.PANEL, 2.0)
			G.coin(self, Vector2(tag.position.x + 12, tag.position.y + 11), 6, col)
			G.text(self, Vector2(tag.position.x + 24, tag.position.y + 3), "-%d" % cost if not picked else "FIX -%d" % cost, 13, col)
			_cell_hit(c)
		elif s.status[c] == "OK" and not dark.has(c) and L2Rules.idiv(int(vals[c]), L2Config.INCOME_DIV) > 0:
			var inc := L2Rules.idiv(int(vals[c]), L2Config.INCOME_DIV)
			G.text_c(self, pp + Vector2(0, 46), "+%d" % inc, 14, G.CLEAN)
		elif s.status[c] == "OK" and dark.has(c):
			G.text_c(self, pp + Vector2(0, 46), "dark: +0", 12, G.DIM)
	# Picked repairs show the asset back to OK.
	for c: Vector2i in model.pending_repairs:
		G.text_c(self, nx(c) + Vector2(0, -42), "REPAIRED", 12, G.CLEAN)
	# Ledger.
	G.panel(self, Rect2(PANEL_X, 80, PANEL_W, 520))
	var ns: L2State = bp["state"]
	var y := 92.0
	G.text(self, Vector2(PANEL_X + 20, y), "BETWEEN RAIDS", 17, G.INK)
	y += 34.0
	G.coin(self, Vector2(PANEL_X + 28, y + 10), 10)
	G.text(self, Vector2(PANEL_X + 50, y), L2Config.key_label().to_upper(), 15, G.DIM)
	y += 26.0
	_ledger_row(y, "AFTER THE RAID", str(s.bank), G.INK, "coin")
	y += 24.0
	var rc: int = int(bp["repair_cost"])
	_ledger_row(y, "REPAIR  (%d)" % (bp["repaired"] as Array).size(), "-%d" % rc if rc > 0 else "0", G.DMG if rc > 0 else G.DIM, "coin")
	y += 24.0
	_ledger_row(y, "INCOME  (OK, not dark)", "+%d" % int(bp["income"]), G.CLEAN, "coin")
	y += 24.0
	draw_line(Vector2(PANEL_X + 20, y + 2), Vector2(PANEL_X + PANEL_W - 20, y + 2), G.PANEL_EDGE, 2.0)
	y += 6.0
	_ledger_row(y, "NEXT RAID", str(ns.bank), G.CELL, "coin")
	y += 40.0
	G.flame(self, Vector2(PANEL_X + 28, y + 10), 10)
	G.text(self, Vector2(PANEL_X + 50, y), "HEAT", 15, G.DIM)
	y += 26.0
	_ledger_row(y, "AFTER THE RAID", str(s.heat), G.INK, "flame")
	y += 24.0
	_ledger_row(y, "THE RUN", "+%d" % L2Config.RUN_HEAT, G.HOLD, "flame")
	y += 24.0
	draw_line(Vector2(PANEL_X + 20, y + 2), Vector2(PANEL_X + PANEL_W - 20, y + 2), G.PANEL_EDGE, 2.0)
	y += 6.0
	_ledger_row(y, "NEXT RAID", str(ns.heat), G.HEAT, "flame")
	y += 26.0
	var nxt_extra: int = L2Rules.extra_count(ns.heat)
	G.text(self, Vector2(PANEL_X + 20, y), "Next raid: %d known beam%s." % [1 + nxt_extra, "" if nxt_extra == 0 else "s"], 14, G.THREAT_LIGHT if nxt_extra > 0 else G.DIM)
	y += 34.0
	G.text(self, Vector2(PANEL_X + 20, y), "Repair costs half the asset's value; income is a third", 12, G.DIM)
	y += 18.0
	G.text(self, Vector2(PANEL_X + 20, y), "of the value of each OK asset. DOWN assets earn nothing.", 12, G.DIM)
	y += 26.0
	G.text(self, Vector2(PANEL_X + 20, y), "Network: %d OK, %d DOWN, %d TAKEN" % [s.count("OK"), s.count("DOWN"), s.count("TAKEN")], 14, G.INK)
	y += 24.0
	G.text(self, Vector2(PANEL_X + 20, y), "Leg value now: %d" % model.final_score(), 14, G.DIM)
	_btn(Rect2(PANEL_X, 614, PANEL_W, 46), "NEXT RAID  [Enter]", "next", true, 18)
	_draw_legend()


# ---- breach ----
func _draw_breach() -> void:
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), Color8(34, 6, 12))
	# The dead network, dim, behind the end card.
	var after: L2State = row["after_raid"]
	var saved := Color8(34, 6, 12)
	for c in L2Rules.nodes():
		_draw_node(c, after.status, 0, row["alloc"])
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), Color(saved.r, saved.g, saved.b, 0.94))
	var cx := 640.0
	# A broken HOME server.
	var hc := Vector2(cx, 170)
	G.home_server(self, hc, 56.0, G.DMG, Color8(60, 10, 20))
	G.line(self, hc + Vector2(-40, -62), hc + Vector2(-8, -4), Color8(34, 6, 12), 8.0)
	G.line(self, hc + Vector2(-8, -4), hc + Vector2(-34, 60), Color8(34, 6, 12), 8.0)
	G.line(self, hc + Vector2(40, -62), hc + Vector2(14, 8), Color8(34, 6, 12), 8.0)
	for k in range(L2Config.HOME_HP):
		G.pip(self, Vector2(cx + (k - 1) * 34.0, 252), 22.0, "lost")
	G.text_c(self, Vector2(cx, 330), "BREACHED", 84, G.DMG)
	G.text_c(self, Vector2(cx, 398), "THE CAMPAIGN IS LOST", 30, G.INK)
	G.text_c(self, Vector2(cx, 446), "Raid %d: the beams reached HOME and its last integrity went." % (int(row["raid"]) + 1), 18, G.DIM)
	var l: Dictionary = row["ledger"]
	G.text_c(self, Vector2(cx, 476), "HOME %d -> 0   |   Heat %d   |   %d %s left" % [l["home_before"], l["heat_after"], l["bank_after"], L2Config.key_label()], 16, G.DIM)
	G.text_c(self, Vector2(cx, 520), "Leg score: -%d" % L2Config.BREACH, 26, G.DMG)
	_btn(Rect2(cx - 200, 568, 400, 52), "LEG RECORD  [Enter]", "next", true, 20)


# ---- leg record ----
func _draw_record() -> void:
	G.text(self, Vector2(40, 80), "LEG RECORD", 22, G.INK)
	if model.breached:
		G.text(self, Vector2(220, 84), "BREACHED: the campaign was lost in raid %d" % model.history.size(), 17, G.DMG)
	else:
		G.text(self, Vector2(220, 84), "CELL HOLDS", 17, G.HOLD)
	for j in range(L2Config.RAIDS):
		var r := Rect2(30 + j * 410, 116, 390, 440)
		if j >= model.history.size():
			G.panel(self, r, G.PANEL_EDGE, G.PANEL, 2.0)
			G.text(self, Vector2(r.position.x + 20, r.position.y + 14), "RAID %d" % (j + 1), 20, G.DIM)
			G.text(self, Vector2(r.position.x + 20, r.position.y + 60), "NOT PLAYED", 24, G.DIM)
			continue
		var h: Dictionary = model.history[j]
		var l: Dictionary = h["ledger"]
		var sm: Dictionary = h["summary"]
		var edge: Color = G.CLEAN if h["evaded"] else (G.DMG if int(l["home_after"]) <= 0 else G.HOLD)
		G.panel(self, r, edge, G.PANEL, 3.0)
		G.text(self, Vector2(r.position.x + 20, r.position.y + 12), "RAID %d" % (j + 1), 20, G.DIM)
		if int(l["home_after"]) <= 0:
			G.text_r(self, Vector2(r.end.x - 20, r.position.y + 10), "BREACHED", 24, G.DMG)
		elif h["evaded"]:
			G.text_r(self, Vector2(r.end.x - 20, r.position.y + 10), "EVADED", 24, G.CLEAN)
		else:
			G.text_r(self, Vector2(r.end.x - 20, r.position.y + 10), "CELL HOLDS", 22, G.HOLD)
		# Heat band of the sweep: the beams it ran with.
		G.flame(self, Vector2(r.position.x + 30, r.position.y + 62), 10)
		G.text(self, Vector2(r.position.x + 48, r.position.y + 50), "%d -> %d" % [l["heat_before"], l["heat_after"]], 20, G.HEAT)
		_band_chips(Vector2(r.position.x + 190, r.position.y + 62), int(l["extra"]), false)
		# Mini map of the network after the raid.
		_mini_map(Vector2(r.position.x + 20, r.position.y + 92), h)
		# What changed.
		var tx := r.position.x + 214
		var ty := r.position.y + 100.0
		G.text(self, Vector2(tx, ty - 4), "STATUS CHANGES", 12, G.DIM)
		ty += 20.0
		_chips(tx, ty + 10, sm)
		ty += 34.0
		G.coin(self, Vector2(tx + 8, ty + 10), 8)
		G.text(self, Vector2(tx + 24, ty), "%d -> %d" % [l["bank_before"], l["bank_after"]], 17, G.INK)
		ty += 30.0
		G.home_server(self, Vector2(tx + 8, ty + 10), 7.0, G.INK)
		for k in range(L2Config.HOME_HP):
			G.pip(self, Vector2(tx + 40 + k * 22, ty + 10), 14.0, "full" if k < int(l["home_after"]) else "lost")
		ty += 30.0
		var plan_s := "ghost %d  decoy %d  dark %d" % [h["alloc"]["ghost"].size(), h["alloc"]["decoys"].size(), h["alloc"]["dark"].size()]
		G.text(self, Vector2(r.position.x + 20, r.position.y + 256), plan_s, 14, G.DIM)
		var sp: Vector2i = h["spoof"]
		G.text(self, Vector2(r.position.x + 20, r.position.y + 280), "spoof: " + ("used" if sp != L2Rules.NONE else "held"), 14, G.DIM)
		var bt: Dictionary = h["between"]
		if not bt.is_empty():
			G.text(self, Vector2(r.position.x + 20, r.position.y + 310), "Between: repaired %d (-%d), income +%d" % [(bt["repaired"] as Array).size(), bt["repair_cost"], bt["income"]], 13, G.INK)
			var nb: L2State = bt["after"]
			G.text(self, Vector2(r.position.x + 20, r.position.y + 334), "Next raid: Heat %d, %d known beam%s" % [nb.heat, 1 + L2Rules.extra_count(nb.heat), "" if L2Rules.extra_count(nb.heat) == 0 else "s"], 13, G.DIM)
		elif j == model.history.size() - 1:
			G.text(self, Vector2(r.position.x + 20, r.position.y + 310), "The last raid: no between step.", 13, G.DIM)
	var s := model.state
	var vals: Dictionary = model.values()
	var kept := 0
	for c: Vector2i in s.status:
		if s.status[c] != "TAKEN":
			kept += int(vals[c]) - (L2Rules.idiv(int(vals[c]), L2Config.REPAIR_DIV) if s.status[c] == "DOWN" else 0)
	var lost: int = L2Config.HOME_HP - s.home_hp
	var sc: String
	if model.breached:
		sc = "SCORE  -%d   (BREACHED)" % L2Config.BREACH
	else:
		sc = "SCORE  %d   =  bank %d  +  assets kept %d  -  HOME lost %d x %d" % [model.final_score(), s.bank, kept, lost, L2Config.HOME_LOSS_COST]
	G.text(self, Vector2(40, 572), sc, 20, G.DMG if model.breached else G.CELL)
	_btn(Rect2(40, 612, 400, 46), "PLAY THE LEG AGAIN  [Enter]", "next", true, 18)


func _mini_map(origin: Vector2, h: Dictionary) -> void:
	var after: L2State = h["after_raid"]
	var touched: Array = []
	for o: Dictionary in h["outcomes"]:
		touched.append(o["cell"])
	for c in L2Rules.nodes():
		var p := origin + Vector2(c.x * 44.0 + 20.0, c.y * 44.0 + 20.0)
		var cell_r := Rect2(p.x - 20, p.y - 20, 40, 40)
		draw_rect(cell_r, Color8(20, 24, 46))
		draw_rect(cell_r, G.PANEL_EDGE, false, 1.0)
		if c == model.home():
			G.home_server(self, p, 12.0, G.INK)
		elif after.status.has(c):
			match after.status[c]:
				"OK":
					G.circle(self, p, 11, G.CELL, 3.0)
				"DOWN":
					G.disc(self, p, 12, GREY)
					G.bolt(self, p, 9.0)
				"TAKEN":
					G.corp(self, p, 12.0)
		elif (h["alloc"]["decoys"] as Array).has(c):
			draw_polyline(PackedVector2Array([p + Vector2(0, -11), p + Vector2(11, 0), p + Vector2(0, 11), p + Vector2(-11, 0), p + Vector2(0, -11)]), G.CELL, 2.5, true)
		else:
			G.disc(self, p, 3, G.EMPTY_NODE)
		if touched.has(c):
			draw_rect(cell_r.grow(-1.0), G.DMG, false, 2.0)


# ---------- capture ----------
func _snap(shot_name: String) -> void:
	queue_redraw()
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [capture_dir, shot_name])
	print("shot ", shot_name)


## Play the sweep of the current raid beat by beat, taking a picture at each, choosing the spoof from the line's step.
func _capture_sweep(prefix: String, spoof_cell: Variant) -> void:
	var seen := {}
	var guard := 0
	while not play.is_done() and guard < 4000:
		guard += 1
		var bid: String = play.beam_id()
		if play.state == L2Play.S.DECIDE:
			if not seen.has("decide"):
				seen["decide"] = true
				await _snap("%s_decision" % prefix)
			if spoof_cell == null:
				_act("hold")
			else:
				var sc: Vector2i = spoof_cell
				_act("cell:%d,%d" % [sc.x, sc.y])
			if not cap_lite:
				await _snap("%s_after_decision" % prefix)
			continue
		play.advance(0.05)
		if play.state == L2Play.S.BEAM:
			var n: int = play.beam_steps(play.bi).size()
			if play.t >= (n * 0.5 + 0.6) * L2Config.STEP_T and not seen.has("beam_" + bid):
				seen["beam_" + bid] = true
				if not cap_lite or bid in ["b1", "hunter"]:
					await _snap("%s_beam_%s" % [prefix, bid])
		elif play.state == L2Play.S.UNSEAL and play.t >= 0.5 and not seen.has("unseal"):
			seen["unseal"] = true
			if not cap_lite:
				await _snap("%s_unseal" % prefix)
		elif play.state == L2Play.S.TURN and play.t >= 0.45 and not seen.has("turn"):
			seen["turn"] = true
			if not cap_lite:
				await _snap("%s_hunter_turn" % prefix)
	_check_done()


func _run_capture() -> void:
	DirAccess.make_dir_recursive_absolute(capture_dir)
	var steps: Array = model.leg[cap_line]
	var n := 0
	for i in range(steps.size()):
		var s: Dictionary = steps[i]
		var pre := "%02d_r%d" % [n, i + 1]
		await _snap(pre + "_contact")
		n += 1
		_act("next")
		if not cap_lite:
			await _snap("%02d_r%d_plan_empty" % [n, i + 1])
			n += 1
		var al := L2Data.alloc_of(s["alloc"])
		for c: Vector2i in al["ghost"]:
			_act("lever:ghost")
			_click_cell(c)
		for c: Vector2i in al["decoys"]:
			_act("lever:decoy")
			_click_cell(c)
		for c: Vector2i in al["dark"]:
			_act("lever:dark")
			_click_cell(c)
		sel_lever = ""
		if not cap_lite:
			await _snap("%02d_r%d_plan_levers" % [n, i + 1])
			n += 1
		_act("next")
		await _snap("%02d_r%d_forecast" % [n, i + 1])
		n += 1
		_act("next")
		var spoof_cell: Variant = null
		if s["spoof"] != null:
			spoof_cell = L2Data.cell(s["spoof"])
		await _capture_sweep("%02d_r%d" % [n, i + 1], spoof_cell)
		n += 1
		if phase == Phase.AFTER:
			await _snap("%02d_r%d_aftermath" % [n, i + 1])
			n += 1
		elif phase == Phase.BREACH:
			await _snap("%02d_r%d_breach" % [n, i + 1])
			n += 1
			_act("next")
			break
		_act("next")
		if phase == Phase.REPAIR:
			await _snap("%02d_r%d_repair_open" % [n, i + 1])
			n += 1
			for c: Vector2i in L2Data.cells(s["repairs"]):
				_click_cell(c)
			await _snap("%02d_r%d_repair_picked" % [n, i + 1])
			n += 1
			_act("next")
	await _snap("%02d_record" % n)
	get_tree().quit(0)
