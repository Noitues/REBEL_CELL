extends Control
## M10 sweep-raid lab: the playable view. Reads M10Model / M10Play and draws; the rules live in M10Rules.
## Flow: contact, plan, forecast (on the grid), hands-off playout with the spoof decision, aftermath, leg record.
## Capture mode: `-- --shots=<abs dir> [--spoof=choice|press] [--repair=value|half] [--scramble]` auto-plays raid 1.

enum Phase { CONTACT, PLAN, FORECAST, PLAY, AFTER, RECORD }

const G = preload("res://tools/raid_lab_m10/m10_glyphs.gd")
const SPEEDS := [1.0, 2.0, 4.0]
const NODE_R := 28.0
const SHAPE_NAME := ["TRIANGLE", "SQUARE", "DIAMOND"]
const DASHES := [Vector2(18, 8), Vector2(6, 6), Vector2(14, 4)]
const PANEL_X := 780.0
const STRIP_Y := 676.0
const LEVER_TEXT := {
	"ghost": ["GHOST", "Hides an asset node from every beam.", "1"],
	"decoy": ["DECOY", "A beam stops on it and counts it as a find.", "2"],
	"dark": ["GO DARK", "Hides an asset; its next income is lost.", "3"],
}

var model := M10Model.new()
var play: M10Play = null
var row: Dictionary = {}
var phase: int = Phase.CONTACT
var sel_lever: String = ""
var speed_i: int = 0
var hits: Array = []
var mouse := Vector2(-100, -100)
var status_msg: String = ""
var capture_dir: String = ""
var _settled: bool = false


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shots="):
			capture_dir = a.substr(8)
		elif a.begins_with("--spoof="):
			M10Config.toggles["SPOOF_MODE"] = a.substr(8)
		elif a.begins_with("--repair="):
			M10Config.toggles["REPAIR"] = a.substr(9)
		elif a.begins_with("--key="):
			M10Config.toggles["KEY_LABEL"] = a.substr(6)
		elif a == "--scramble":
			G.scramble = true
	if capture_dir != "":
		_run_capture.call_deferred()


func _process(delta: float) -> void:
	if phase == Phase.PLAY and play != null and capture_dir == "":
		play.advance(delta * SPEEDS[speed_i], delta)
		_check_done()
	queue_redraw()


func _check_done() -> void:
	if play != null and play.is_done() and not _settled:
		_settled = true
		row = model.settle(play)
		phase = Phase.AFTER


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
	match code:
		KEY_F1:
			_act("tog:SPOOF_MODE")
		KEY_F2:
			_act("tog:REPAIR")
		KEY_F3:
			_act("tog:KEY_LABEL")
		KEY_1:
			_act("lever:ghost" if phase in [Phase.PLAN, Phase.FORECAST] else "speed:0")
		KEY_2:
			_act("lever:decoy" if phase in [Phase.PLAN, Phase.FORECAST] else "speed:1")
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
			if phase == Phase.PLAY:
				if code == KEY_SPACE:
					_act("press")
			else:
				_act("next")


# ---------- actions ----------
func _act(id: String) -> void:
	status_msg = ""
	if id.begins_with("tog:"):
		if phase == Phase.PLAY:
			status_msg = "Toggles change between raids, not during a sweep."
		else:
			M10Config.cycle(id.substr(4))
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
	elif id == "press":
		if phase == Phase.PLAY and play != null:
			play.press()


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
				model.next_raid()
				phase = Phase.CONTACT
		Phase.RECORD:
			model.new_leg()
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
		if play.state == M10Play.S.DECIDE:
			if not play.choose_spoof(c):
				status_msg = "Pick a node on the lit beam-2 line."


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


func _draw_path(path: PackedVector2Array, col: Color, w: float, head_arrow: bool = true) -> void:
	if path.size() < 2:
		return
	draw_polyline(path, col, w, true)
	if head_arrow:
		var last: Vector2 = path[path.size() - 1]
		var prev: Vector2 = path[path.size() - 2]
		if last.distance_to(prev) > 0.5:
			var d := (last - prev).normalized()
			var n := Vector2(-d.y, d.x)
			draw_colored_polygon(PackedVector2Array([last + d * 9.0, last - d * 6.0 + n * 8.0, last - d * 6.0 - n * 8.0]), col)


func _draw_dashed_path(path: PackedVector2Array, col: Color, dash: Vector2, w: float) -> void:
	for i in range(path.size() - 1):
		G.dashed_line(self, path[i], path[i + 1], col, dash.x, dash.y, w)
	if path.size() >= 2:
		var last: Vector2 = path[path.size() - 1]
		var d: Vector2 = (last - path[path.size() - 2]).normalized()
		var n := Vector2(-d.y, d.x)
		draw_colored_polygon(PackedVector2Array([last + d * 9.0, last - d * 6.0 + n * 8.0, last - d * 6.0 - n * 8.0]), col)


## Offsets (px) for lines that coincide with an earlier line, so they stay apart: [b1, cand0, cand1, cand2].
func _offsets() -> Array:
	var keys: Array = []
	var out: Array = []
	var lines: Array = [model.b1] + model.cands
	for ln in lines:
		var cs: Array = []
		for c in ln:
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


## The middle of the first segment of a beam (where the hunter's badge sits).
func _mid(g: Dictionary) -> Vector2:
	var pts: Array = g["pts"]
	return ((pts[0] as Vector2) + (pts[1] as Vector2)) * 0.5


## Hunter columns that coincide with a known or candidate line shift 14 px so both stay visible.
func _h_off(x: int) -> float:
	var col_key := str(M10Rules.column(x))
	var lines: Array = [model.b1] + model.cands
	for ln in lines:
		if str(ln) == col_key:
			return 14.0
		var rev: Array = (ln as Array).duplicate()
		rev.reverse()
		if str(rev) == col_key:
			return 14.0
	return 0.0


# ---------- drawing ----------
func _draw() -> void:
	hits = []
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), G.BG)
	_draw_hud()
	match phase:
		Phase.CONTACT:
			_draw_net(false)
			_draw_contact()
		Phase.PLAN, Phase.FORECAST:
			_draw_plan()
		Phase.PLAY:
			_draw_play()
		Phase.AFTER:
			_draw_after()
		Phase.RECORD:
			_draw_record()
	_draw_strip()


func _hud_values() -> Dictionary:
	var h := model.heat
	var k := model.key
	var dh := 0
	var dk := 0
	if phase in [Phase.PLAN, Phase.FORECAST, Phase.PLAY]:
		h = model.heat_now()
		k = model.key_now()
		dh = h - model.heat
		dk = k - model.key
	elif phase == Phase.AFTER and not row.is_empty():
		dh = int(row["ledger"]["heat_after"]) - int(row["ledger"]["heat_before"])
		dk = int(row["ledger"]["key_after"]) - int(row["ledger"]["key_before"])
	return {"heat": h, "key": k, "dh": dh, "dk": dk}


func _draw_hud() -> void:
	var v := _hud_values()
	# Heat meter with the cobalt notch.
	var hx := 60.0
	var hw := 420.0
	var hy := 22.0
	G.flame(self, Vector2(36, hy + 10), 10)
	draw_rect(Rect2(hx, hy, hw, 20), Color8(30, 34, 56))
	var fillw := hw * float(v["heat"]) / M10Config.HEAT_MAX
	var base_w := hw * float(int(v["heat"]) - maxi(0, int(v["dh"]))) / M10Config.HEAT_MAX
	draw_rect(Rect2(hx, hy, base_w, 20), G.HEAT)
	if int(v["dh"]) > 0:
		draw_rect(Rect2(hx + base_w, hy, fillw - base_w, 20), G.HOLD)
	elif int(v["dh"]) < 0:
		draw_rect(Rect2(hx + fillw, hy, base_w - fillw, 20), Color8(255, 110, 40, 90))
	draw_rect(Rect2(hx, hy, hw, 20), G.PANEL_EDGE, false, 2.0)
	var nxp := hx + hw * M10Config.HEAT_NOTCH / M10Config.HEAT_MAX
	G.line(self, Vector2(nxp, hy - 6), Vector2(nxp, hy + 26), G.THREAT_LIGHT, 3.0)
	G.shield(self, Vector2(nxp, hy + 36), 8.0)
	G.text(self, Vector2(nxp + 14, hy + 28), "NOTCH %d" % M10Config.HEAT_NOTCH, 12, G.THREAT_LIGHT)
	G.text(self, Vector2(hx + hw + 10, hy - 2), str(v["heat"]), 22, G.HEAT)
	if int(v["dh"]) != 0:
		G.text(self, Vector2(hx + hw + 48, hy + 1), "%+d" % int(v["dh"]), 18, G.HOLD if int(v["dh"]) > 0 else G.CLEAN)
	# Raid pips.
	G.text(self, Vector2(580, 14), "RAID %d/%d" % [model.raid + 1, M10Config.LEG_SEEDS.size()], 14, G.DIM)
	for j in range(M10Config.LEG_SEEDS.size()):
		var c := Vector2(590 + j * 24, 48)
		if j < model.history.size():
			G.disc(self, c, 7, G.CLEAN if model.history[j]["evaded"] else G.DMG)
		elif j == model.raid:
			G.circle(self, c, 7, G.CELL, 3.0)
		else:
			G.circle(self, c, 7, G.PANEL_EDGE)
	# Key bar.
	var kx := 740.0
	var kw := 360.0
	var ky := 22.0
	draw_rect(Rect2(kx, ky, kw, 20), Color8(30, 34, 56))
	var kfill := kw * float(v["key"]) / M10Config.KEY_MAX
	draw_rect(Rect2(kx, ky, kfill, 20), G.CELL)
	if int(v["dk"]) < 0:
		var lost_w := kw * float(-int(v["dk"])) / M10Config.KEY_MAX
		_hatch(Rect2(kx + kfill, ky + 2, lost_w, 16), G.DMG)
	elif int(v["dk"]) > 0:
		draw_rect(Rect2(kx + kfill - kw * float(v["dk"]) / M10Config.KEY_MAX, ky, kw * float(v["dk"]) / M10Config.KEY_MAX, 20), G.CLEAN)
	draw_rect(Rect2(kx, ky, kw, 20), G.PANEL_EDGE, false, 2.0)
	G.hexagon(self, Vector2(kx + kw + 22, ky + 10), 14, Color8(40, 30, 70), G.THREAT_LIGHT, 2.0)
	G.text(self, Vector2(kx + kw + 44, ky - 2), "%d/%d" % [v["key"], M10Config.KEY_MAX], 22, G.INK)
	if int(v["dk"]) != 0:
		G.text(self, Vector2(kx + kw + 112, ky + 1), "%+d" % int(v["dk"]), 18, G.DMG if int(v["dk"]) < 0 else G.CLEAN)
	G.text(self, Vector2(kx + kw + 44, ky + 26), "KEY  " + M10Config.key_label().to_upper(), 12, G.DIM)
	if phase == Phase.FORECAST:
		_draw_bracket(kx, kw, ky, int(v["key"]))


func _hatch(r: Rect2, col: Color) -> void:
	draw_rect(r, Color(col.r, col.g, col.b, 0.28))
	var x := r.position.x
	while x < r.end.x:
		var x2 := minf(x + r.size.y, r.end.x)
		draw_line(Vector2(x, r.end.y), Vector2(x2, r.end.y - (x2 - x)), col, 2.0)
		x += 6.0


## The loss range as a bracket on the key bar (min..max repair over the sealed candidates).
func _draw_bracket(kx: float, kw: float, ky: float, key_now: int) -> void:
	var rng := model.loss_range()
	var lo: int = mini(int(rng[0]), key_now)
	var hi: int = mini(int(rng[1]), key_now)
	var end_x := kx + kw * float(key_now) / M10Config.KEY_MAX
	var x_lo := end_x - kw * lo / M10Config.KEY_MAX
	var x_hi := end_x - kw * hi / M10Config.KEY_MAX
	if lo > 0:
		draw_rect(Rect2(x_lo, ky, end_x - x_lo, 20), G.DMG)
	if hi > lo:
		_hatch(Rect2(x_hi, ky + 2, x_lo - x_hi, 16), G.DMG)
	var by := ky + 30.0
	var xa := minf(x_hi, x_lo)
	var xb := end_x
	draw_polyline(PackedVector2Array([Vector2(xa, by - 6), Vector2(xa, by), Vector2(xb, by), Vector2(xb, by - 6)]), G.INK, 2.0, true)
	var label := _loss_str(int(rng[0])) if rng[0] == rng[1] else "%s .. %s" % [_loss_str(int(rng[0])), _loss_str(int(rng[1]))]
	G.text_c(self, Vector2((xa + xb) * 0.5, by + 14), label, 15, G.INK)
	if int(rng[0]) == 0:
		G.check(self, Vector2(xb + 22, by + 6), 7)
		G.text(self, Vector2(xb + 36, by - 2), "EVADE +%d" % M10Config.EVADE, 13, G.CLEAN)


func _draw_strip() -> void:
	draw_rect(Rect2(0, STRIP_Y, 1280, 720 - STRIP_Y), Color(0, 0, 0, 0.55))
	var hint := ""
	match phase:
		Phase.CONTACT:
			hint = "Contact. Enter plans the defense."
		Phase.PLAN:
			hint = "Pick a lever (1 2 3), click a node to place it, click a placed lever to take it off. Z undoes. Enter shows the forecast."
		Phase.FORECAST:
			hint = "Forecast on the grid: each shape marks what that sealed line would find. B edits the plan. Enter launches the sweep."
		Phase.PLAY:
			hint = "Hands-off sweep. 1 / 2 / 4 speed, S skips. The spoof decision needs you."
			if play != null and play.state == M10Play.S.PRESS:
				hint = "Press SPACE as the ring closes on the node."
		Phase.AFTER:
			hint = "Aftermath. Enter continues."
		Phase.RECORD:
			hint = "Leg record. Enter plays the leg again."
	if status_msg != "":
		hint = status_msg
	G.text(self, Vector2(10, STRIP_Y + 3), hint, 13, G.INK if status_msg != "" else G.DIM)
	var tx := 10.0
	var items := [["SPOOF_MODE", "SPOOF: " + M10Config.spoof_mode().to_upper(), "F1"], ["REPAIR", "REPAIR: " + M10Config.repair_mode().to_upper(), "F2"],
		["KEY_LABEL", "KEY: " + M10Config.key_label().to_upper(), "F3"]]
	for it in items:
		var label: String = "%s  [%s]" % [it[1], it[2]]
		var w := G.text_w(label, 13) + 20.0
		var r := Rect2(tx, STRIP_Y + 21, w, 22)
		G.panel(self, r, G.PANEL_EDGE, Color8(60, 52, 24) if _hot(r) else G.PANEL, 1.0)
		G.text_c(self, r.get_center(), label, 13, G.CELL)
		_add_hit(r, "tog:" + String(it[0]))
		tx += w + 8.0
	G.text(self, Vector2(tx + 14, STRIP_Y + 24), "M10 SWEEP lab  |  designer toggles (labels only except SPOOF)", 12, G.DIM)


# ---- the network ----
## One node. `state`: found/down overrides come from the callers.
func _draw_node(c: Vector2i, plan: Dictionary, found: Array = [], down: bool = false) -> void:
	var p := nx(c)
	var v: int = model.assets.get(c, -1)
	if plan["decoys"].has(c):
		draw_colored_polygon(PackedVector2Array([p + Vector2(0, -26), p + Vector2(26, 0), p + Vector2(0, 26), p + Vector2(-26, 0)]), G.PANEL)
		draw_polyline(PackedVector2Array([p + Vector2(0, -26), p + Vector2(26, 0), p + Vector2(0, 26), p + Vector2(-26, 0), p + Vector2(0, -26)]), G.CELL, 4.0, true)
		draw_colored_polygon(PackedVector2Array([p + Vector2(0, -10), p + Vector2(10, 0), p + Vector2(0, 10), p + Vector2(-10, 0)]), G.CELL)
		return
	if v < 0:
		G.disc(self, p, 8, G.EMPTY_NODE)
		return
	var is_found := found.has(c)
	var ghost: bool = plan["ghost"].has(c)
	var dark: bool = plan["dark"].has(c)
	var edge := G.CELL
	var fill := G.PANEL
	if dark:
		fill = Color8(10, 10, 16)
		edge = G.DIM
	if is_found:
		edge = G.DMG
		if down:
			fill = Color8(60, 30, 36)
	G.disc(self, p, NODE_R, fill)
	G.circle(self, p, NODE_R, edge, 4.0)
	if ghost:
		G.dashed_ring(self, p, NODE_R + 5, G.CELL, 4.0)
		G.flame(self, p + Vector2(32, -28), 7)
	var inkc := G.DIM if dark else G.INK
	G.coin(self, p + Vector2(-9, 0), 8, G.DIM if dark else G.CELL)
	G.text(self, p + Vector2(3, -11), str(v), 19, inkc)
	if is_found:
		G.cross(self, p, 30, G.DMG, 3.0)
	if is_found and down:
		G.wrench(self, p + Vector2(22, 22), 11)


func _draw_net(show_hit_areas: bool, found: Array = [], down: bool = false) -> void:
	for c in M10Rules.nodes():
		_draw_node(c, model.plan, found, down)
		if show_hit_areas:
			var p := nx(c)
			_add_hit(Rect2(p - Vector2(46, 46), Vector2(92, 92)), "cell:%d,%d" % [c.x, c.y])


## Beam 1 (known): solid with badge 1, stopping at a decoy.
func _draw_beam1_full(with_plan: bool) -> void:
	var offs := _offsets()
	var g := _geom(model.b1, offs[0])
	var u := float(g["pts"].size() + 1)
	if with_plan:
		for i in range(model.b1.size()):
			if model.plan["decoys"].has(model.b1[i]):
				u = i + 1.0
				break
	_draw_path(_path(g, u), G.THREAT, 6.0)
	G.badge(self, (g["a"] as Vector2) - (g["dir"] as Vector2) * 24.0, 1)


## The sealed candidates: dashed lines told apart by end shape and dash pattern. `fade` dims the others.
func _draw_candidates(only: int = -1, fade: float = 0.0) -> void:
	var offs := _offsets()
	for i in range(model.cands.size()):
		var g := _geom(model.cands[i], offs[i + 1])
		var col := G.THREAT_LIGHT
		if only >= 0 and i != only:
			col = G.THREAT_LIGHT.lerp(G.THREAT_FADE, fade)
		var path := _path(g, float(g["pts"].size() + 1))
		_draw_dashed_path(path, col, DASHES[i], 4.0)
		var a: Vector2 = g["a"]
		G.cand_shape(self, a, i, 11.0, col, G.BG)
		if only >= 0 and i == only:
			continue	## the lit beam draws its own badge
		G.badge(self, a - (g["dir"] as Vector2) * 28.0, 2, col.darkened(0.2) if only >= 0 else G.THREAT)


## Thin dashed hunter columns: beam 3 turns down the column of the first thing found.
func _draw_hunter_plan() -> void:
	var offs := _offsets()
	var b1_first := Vector2i(-1, -1)
	var res1 := M10Rules.sweep(model.assets, model.b1, model.cands[0], model.own3, model.plan)
	# first find of beam 1 alone
	for st in res1["beams"][0]["steps"]:
		if st["kind"] == "found" or st["kind"] == "decoy":
			b1_first = st["cell"]
			break
	if b1_first.x >= 0:
		_hunter_col(b1_first.x, G.THREAT_LIGHT, 3.0, 3, Vector2(10, 6), 0.0)
		return
	var own_needed := false
	for i in range(model.cands.size()):
		var r := M10Rules.sweep(model.assets, model.b1, model.cands[i], model.own3, model.plan)
		var f: Vector2i = r["first"]
		if f.x >= 0:
			_hunter_col(f.x, G.THREAT_LIGHT.darkened(0.25), 2.0, -1, DASHES[i], (i - 1) * 12.0, i)
		else:
			own_needed = true
	if own_needed:
		_hunter_col(model.own3[0].x, G.THREAT_LIGHT.darkened(0.45), 2.0, 3, Vector2(4, 8), 0.0)


func _hunter_col(x: int, col: Color, w: float, badge_n: int, dash: Vector2, off: float, shape_i: int = -1) -> void:
	var g := _geom(M10Rules.column(x), off + _h_off(x))
	var path := _path(g, float(g["pts"].size() + 1))
	_draw_dashed_path(path, col, dash, w)
	var b: Vector2 = g["b"]
	if shape_i >= 0:
		G.cand_shape(self, b + Vector2(0, 18), shape_i, 7.0, col, G.BG, 2.0)
	if badge_n > 0:
		G.badge(self, _mid(g), badge_n)


func _draw_contact() -> void:
	# Haul panel.
	G.panel(self, Rect2(PANEL_X, 100, 460, 270))
	G.text(self, Vector2(PANEL_X + 20, 112), "HAUL", 15, G.DIM)
	G.text(self, Vector2(PANEL_X + 100, 112), "your run nodes are assets here", 13, G.DIM)
	var vals: Array = []
	for c in model.assets:
		vals.append(int(model.assets[c]))
	vals.sort()
	vals.reverse()
	for i in range(vals.size()):
		var px := PANEL_X + 50.0 + (i % 3) * 140.0
		var py := 180.0 + (i / 3) * 80.0
		G.coin(self, Vector2(px, py), 14)
		G.text(self, Vector2(px + 24, py - 14), str(vals[i]), 26, G.INK)
	var total := 0
	for v in vals:
		total += v
	G.text(self, Vector2(PANEL_X + 20, 330), "%d assets, %d in all" % [vals.size(), total], 14, G.DIM)
	# Why contact: the cause chain.
	_draw_cause_chain()
	if not model.run_note.is_empty():
		var rn := model.run_note
		G.text(self, Vector2(PANEL_X, 390), "The run since the last raid", 14, G.DIM)
		G.flame(self, Vector2(PANEL_X + 10, 428), 9)
		G.text(self, Vector2(PANEL_X + 26, 417), "+%d" % int(rn["heat"]), 20, G.HEAT)
		G.coin(self, Vector2(PANEL_X + 120, 428), 9)
		G.text(self, Vector2(PANEL_X + 138, 417), "+%d" % int(rn["gain"]), 20, G.CELL)
		if int(rn["dark_loss"]) > 0:
			G.text(self, Vector2(PANEL_X + 210, 420), "-%d dark income lost" % int(rn["dark_loss"]), 14, G.DIM)
	_btn(Rect2(PANEL_X, 560, 460, 56), "PLAN THE DEFENSE  [Enter]", "next", true, 20)


func _draw_cause_chain() -> void:
	var y := 600.0
	for i in range(M10Config.RUN_NODES):
		var c := Vector2(70 + i * 46, y)
		G.circle(self, c, 14, G.CELL, 3.0)
		G.check(self, c, 7, G.CELL)
	G.text(self, Vector2(56, y + 22), "RUN NODES", 12, G.DIM)
	G.arrow(self, Vector2(260, y), Vector2(330, y), G.HEAT, 4.0)
	G.flame(self, Vector2(358, y + 4), 14)
	G.text(self, Vector2(344, y + 22), "HEAT %d" % model.heat, 12, G.HEAT)
	G.arrow(self, Vector2(392, y), Vector2(460, y), G.HEAT, 4.0)
	G.shield(self, Vector2(492, y - 4), 16)
	G.text(self, Vector2(470, y + 22), "NOTCH %d" % M10Config.HEAT_NOTCH, 12, G.THREAT_LIGHT)
	G.arrow(self, Vector2(522, y), Vector2(590, y), G.THREAT, 4.0)
	G.contact(self, Vector2(620, y), 18)
	G.text(self, Vector2(592, y + 24), "CONTACT", 12, G.THREAT_LIGHT)


# ---- plan / forecast ----
func _draw_plan() -> void:
	var fc_mode: bool = phase == Phase.FORECAST
	_draw_net(true)
	_draw_beam1_full(true)
	_draw_candidates()
	_draw_hunter_plan()
	if fc_mode:
		_draw_forecast_marks()
	# hover feedback for the selected lever
	if sel_lever != "":
		for c in M10Rules.nodes():
			var p := nx(c)
			if Rect2(p - Vector2(46, 46), Vector2(92, 92)).has_point(mouse):
				var ok := model.why_not(sel_lever, c) == ""
				G.circle(self, p, 40, G.CLEAN if ok else G.DMG, 3.0)
	# lever tray
	G.text(self, Vector2(PANEL_X, 96), "LEVERS", 14, G.DIM)
	var y := 120.0
	for lv in M10Model.LEVERS:
		_draw_lever_card(lv, Rect2(PANEL_X, y, 460, 78))
		y += 88.0
	# spoof held
	var sr := Rect2(PANEL_X, y, 460, 70)
	G.panel(self, sr, G.CLEAN)
	G.spoof_key(self, Vector2(PANEL_X + 44, y + 35), G.CLEAN)
	G.text(self, Vector2(PANEL_X + 90, y + 10), "SPOOF  x1", 18, G.CLEAN)
	var sp_line := "Held for after the reveal." if M10Config.spoof_mode() == "choice" else "Held: aim it after the reveal, land it with SPACE."
	G.text(self, Vector2(PANEL_X + 90, y + 38), sp_line, 13, G.DIM)
	y += 82.0
	if fc_mode:
		_draw_forecast_legend(y)
	_btn(Rect2(PANEL_X, 612, 120, 48), "UNDO [Z]", "undo", model.can_undo(), 16)
	if fc_mode:
		_btn(Rect2(PANEL_X + 134, 612, 90, 48), "BACK [B]", "back", true, 16)
		_btn(Rect2(PANEL_X + 238, 612, 222, 48), "LAUNCH SWEEP [Enter]", "launch", true, 17)
	else:
		_btn(Rect2(PANEL_X + 134, 612, 326, 48), "FORECAST [Enter]", "forecast", true, 18)


func _draw_lever_card(lv: String, r: Rect2) -> void:
	var used: int = (model.plan[{"ghost": "ghost", "decoy": "decoys", "dark": "dark"}[lv]] as Array).size()
	var cap: int = {"ghost": M10Config.MAX_GHOST, "decoy": M10Config.MAX_DECOY, "dark": M10Config.MAX_DARK}[lv]
	var sel := sel_lever == lv
	G.panel(self, r, G.CELL if sel else G.PANEL_EDGE, Color8(60, 52, 24) if (sel or _hot(r)) else G.PANEL, 3.0 if sel else 2.0)
	_add_hit(r, "lever:" + lv)
	var c := Vector2(r.position.x + 44, r.position.y + 39)
	match lv:
		"ghost":
			G.dashed_ring(self, c, 20, G.CELL if used > 0 else G.DIM, 4.0)
		"decoy":
			var col := G.CELL if used > 0 else G.DIM
			draw_polyline(PackedVector2Array([c + Vector2(0, -22), c + Vector2(22, 0), c + Vector2(0, 22), c + Vector2(-22, 0), c + Vector2(0, -22)]), col, 3.0, true)
		"dark":
			G.disc(self, c, 21, Color8(10, 10, 16))
			G.circle(self, c, 21, G.DIM, 3.0)
	var nm: Array = LEVER_TEXT[lv]
	G.text(self, Vector2(r.position.x + 90, r.position.y + 8), "%s  [%s]" % [nm[0], nm[2]], 18, G.INK)
	G.text(self, Vector2(r.position.x + 90, r.position.y + 34), nm[1], 13, G.DIM)
	# cost in its own currency
	var cx := r.position.x + 90
	var cy := r.position.y + 58
	match lv:
		"ghost":
			G.flame(self, Vector2(cx + 6, cy + 2), 8)
			G.text(self, Vector2(cx + 20, cy - 8), "+%d Heat now" % M10Config.GHOST_HEAT, 14, G.HEAT)
		"decoy":
			G.coin(self, Vector2(cx + 6, cy + 2), 7)
			G.text(self, Vector2(cx + 20, cy - 8), "-%d key now" % M10Config.DECOY_COST, 14, G.CELL)
		"dark":
			G.coin(self, Vector2(cx + 6, cy + 2), 7, G.DIM)
			G.line(self, Vector2(cx - 2, cy + 10), Vector2(cx + 14, cy - 6), G.DMG, 3.0)
			var loss := M10Rules.plan_dark_loss(model.assets, model.plan)
			G.text(self, Vector2(cx + 20, cy - 8), "next income lost: %d" % loss, 14, G.DIM)
	G.text_r(self, Vector2(r.end.x - 14, r.position.y + 10), "%d/%d" % [used, cap], 18, G.INK if used > 0 else G.DIM)


func _draw_forecast_marks() -> void:
	var fc := model.forecast_all()
	for i in range(fc.size()):
		for c in fc[i]["found"]:
			var p := nx(c) + Vector2((i - 1) * 24.0, 44.0)
			G.cand_shape(self, p, i, 8.0, G.DMG, Color(G.DMG.r, G.DMG.g, G.DMG.b, 0.35), 2.5)
		if (fc[i]["found"] as Array).is_empty():
			var g := _geom(model.cands[i], _offsets()[i + 1])
			var a: Vector2 = g["a"]
			G.check(self, a + (g["dir"] as Vector2) * 0.0 + Vector2(0, 0) - (g["dir"] as Vector2) * 52.0, 7)


func _draw_forecast_legend(y: float) -> void:
	G.text(self, Vector2(PANEL_X, y), "A shape on a node = found if that sealed line is the real beam 2:", 13, G.DIM)
	for i in range(3):
		G.cand_shape(self, Vector2(PANEL_X + 24 + i * 40, y + 32), i, 9.0, G.DMG, Color(G.DMG.r, G.DMG.g, G.DMG.b, 0.35), 2.5)
	G.check(self, Vector2(PANEL_X + 160, y + 33), 7)
	G.text(self, Vector2(PANEL_X + 176, y + 24), "= that line finds nothing (evaded)", 13, G.DIM)


# ---- playout ----
func _draw_play() -> void:
	var p := play
	var offs := _offsets()
	var k := p.beam_now()
	_draw_net_play()
	# Candidates and the revealed line.
	var st := p.state
	if st == M10Play.S.B1:
		_draw_candidates()
	elif st == M10Play.S.UNSEAL:
		_draw_candidates(p.reveal, clampf(p.t / M10Config.UNSEAL_T, 0.0, 1.0))
	else:
		_draw_candidates(p.reveal, 0.8)
	# Beam 1.
	var g1 := _geom(model.b1, offs[0])
	var path1: PackedVector2Array
	var u1_full := _beam_u(p.final["beams"][0], g1)
	if st == M10Play.S.B1:
		_draw_path(_path(g1, u1_full), G.THREAT_FADE, 4.0, false)
		_draw_path(_path(g1, minf(p.head(), u1_full)), G.THREAT_LIGHT, 8.0)
	else:
		_draw_path(_path(g1, u1_full), G.THREAT, 6.0)
	G.badge(self, (g1["a"] as Vector2) - (g1["dir"] as Vector2) * 24.0, 1)
	# Beam 2 (revealed).
	if st >= M10Play.S.UNSEAL:
		var g2 := _geom(p.line2(), offs[p.reveal + 1])
		var u2_full := _beam_u(p.final["beams"][1], g2)
		var lit := G.THREAT_LIGHT.lerp(G.THREAT, 0.5)
		if st == M10Play.S.UNSEAL or st == M10Play.S.DECIDE:
			var a := clampf(p.t / M10Config.UNSEAL_T, 0.0, 1.0) if st == M10Play.S.UNSEAL else 1.0
			_draw_path(_path(g2, float(g2["pts"].size() + 1)), Color(lit.r, lit.g, lit.b, 0.35 + 0.65 * a), 5.0)
		elif st == M10Play.S.B2 or st == M10Play.S.PRESS:
			_draw_path(_path(g2, float(g2["pts"].size() + 1)), G.THREAT_FADE, 4.0, false)
			_draw_path(_path(g2, minf(p.head(), u2_full)), G.THREAT_LIGHT, 8.0)
		else:
			_draw_path(_path(g2, u2_full), G.THREAT, 6.0)
		G.badge(self, (g2["a"] as Vector2) - (g2["dir"] as Vector2) * 24.0, 2)
	# Hunter and beam 3.
	if st >= M10Play.S.HUNTER:
		var line3: Array = p.final["beams"][2]["line"]
		var g3 := _geom(line3, _h_off((line3[0] as Vector2i).x))
		var u3_full := _beam_u(p.final["beams"][2], g3)
		var first: Vector2i = p.hunter_from()
		if st == M10Play.S.HUNTER:
			var a3 := clampf(p.t / M10Config.HUNTER_T, 0.0, 1.0)
			if first.x >= 0:
				var pf := nx(first)
				G.circle(self, pf, NODE_R + 8 + 6.0 * sin(p.t * 8.0), G.DMG, 4.0)
				_draw_dashed_path(_path(g3, float(g3["pts"].size() + 1)), Color(G.THREAT_LIGHT.r, G.THREAT_LIGHT.g, G.THREAT_LIGHT.b, a3), Vector2(10, 6), 4.0)
				G.text(self, pf + Vector2(36, -50), "TURNS", 13, G.INK)
			else:
				_draw_dashed_path(_path(g3, float(g3["pts"].size() + 1)), Color(G.THREAT_LIGHT.r, G.THREAT_LIGHT.g, G.THREAT_LIGHT.b, a3), Vector2(4, 8), 4.0)
				G.text_c(self, (g3["b"] as Vector2) + Vector2(0, 40), "OWN LINE", 13, G.INK)
		elif st == M10Play.S.B3:
			_draw_path(_path(g3, float(g3["pts"].size() + 1)), G.THREAT_FADE, 4.0, false)
			_draw_path(_path(g3, minf(p.head(), u3_full)), G.THREAT_LIGHT, 8.0)
		else:
			_draw_path(_path(g3, u3_full), G.THREAT, 5.0)
		G.badge(self, _mid(g3), 3)
	# The spoof decision.
	if st == M10Play.S.DECIDE:
		for c in p.line2():
			var pc := nx(c)
			var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 220.0)
			G.dashed_ring(self, pc, NODE_R + 12 + 3.0 * pulse, G.CLEAN, 4.0)
			_add_hit(Rect2(pc - Vector2(46, 46), Vector2(92, 92)), "cell:%d,%d" % [c.x, c.y])
	if st == M10Play.S.PRESS:
		_draw_press_ring()
	# Pulses.
	for e in p.events:
		var age: float = p.clock - float(e["at"])
		if age < 0.7:
			var pc := nx(e["cell"])
			var col: Color = {"found": G.DMG, "near": G.INK, "decoy": G.CELL, "dup": G.DIM, "spoofed": G.CLEAN, "empty": G.THREAT_FADE}[e["kind"]]
			var a := 1.0 - age / 0.7
			G.circle(self, pc, NODE_R + 4 + age * 40.0, Color(col.r, col.g, col.b, a), 4.0)
	_draw_play_panel()


func _draw_press_ring() -> void:
	var p := play
	var pc := nx(p.spoof_cell)
	var f := (M10Config.PRESS_PERFECT - p.press_t) / M10Config.PRESS_PERFECT
	var r := NODE_R + 8 + 56.0 * maxf(f, -0.3)
	G.circle(self, pc, maxf(r, 12.0), G.CLEAN, 5.0)
	G.circle(self, pc, NODE_R + 8, G.INK, 2.0)
	G.text_c(self, pc + Vector2(0, 50), "SPACE", 16, G.CLEAN)


## Nodes during the sweep: found so far are marked as they are touched; near misses keep a ring.
func _draw_net_play() -> void:
	var found_now: Array = []
	var near_now: Array = []
	for e in play.events:
		if e["kind"] == "found":
			found_now.append(e["cell"])
		elif e["kind"] == "near":
			near_now.append(e["cell"])
	for c in M10Rules.nodes():
		_draw_node(c, model.plan, found_now, false)
	for c in near_now:
		G.circle(self, nx(c), NODE_R + 10, G.INK, 2.0)
	if play.spoof_used and play.state in [M10Play.S.B2, M10Play.S.HUNTER, M10Play.S.B3, M10Play.S.END, M10Play.S.DONE]:
		var col := G.CLEAN if play.press_hit else G.DMG
		G.dashed_ring(self, nx(play.spoof_cell), NODE_R + 14, col, 3.0)


func _draw_play_panel() -> void:
	var p := play
	G.text(self, Vector2(PANEL_X, 96), "SWEEP", 14, G.DIM)
	# Step track: beam 1, 2, 3.
	var k := p.beam_now()
	for i in range(3):
		var c := Vector2(PANEL_X + 40 + i * 110, 130)
		var done: bool = (i < k) or p.state in [M10Play.S.END, M10Play.S.DONE]
		var active: bool = i == k and not done
		G.disc(self, c, 16, G.THREAT if (done or active) else G.PANEL)
		G.circle(self, c, 16, G.CELL if active else G.PANEL_EDGE, 3.0 if active else 2.0)
		G.text_c(self, c, str(i + 1), 18, G.INK)
		if i < 2:
			G.line(self, c + Vector2(22, 0), c + Vector2(88, 0), G.THREAT if done else G.PANEL_EDGE, 3.0)
	G.text(self, Vector2(PANEL_X + 300, 120), _beat_name(), 16, G.INK)
	# Speed controls.
	var labels := ["1x", "2x", "4x"]
	for i in range(3):
		var r := Rect2(PANEL_X + i * 84, 168, 76, 40)
		G.panel(self, r, G.CELL if speed_i == i else G.PANEL_EDGE, Color8(60, 52, 24) if (speed_i == i or _hot(r)) else G.PANEL, 3.0 if speed_i == i else 2.0)
		G.text_c(self, r.get_center(), labels[i], 18, G.CELL if speed_i == i else G.INK)
		_add_hit(r, "speed:%d" % i)
	var rs := Rect2(PANEL_X + 252, 168, 100, 40)
	G.panel(self, rs, G.PANEL_EDGE, Color8(60, 52, 24) if _hot(rs) else G.PANEL, 2.0)
	G.text_c(self, rs.get_center(), "SKIP [S]", 16, G.INK)
	_add_hit(rs, "skip")
	# Spoof box.
	var y := 236.0
	var box := Rect2(PANEL_X, y, 460, 170)
	var waiting := p.state == M10Play.S.DECIDE
	G.panel(self, box, G.CLEAN if (waiting or p.state == M10Play.S.PRESS) else G.PANEL_EDGE, G.PANEL, 3.0 if waiting else 2.0)
	G.spoof_key(self, Vector2(PANEL_X + 44, y + 36), G.CLEAN if not (p.spoof_used and not p.is_waiting() and not p.press_hit) else G.DIM)
	G.text(self, Vector2(PANEL_X + 90, y + 10), "SPOOF", 18, G.CLEAN)
	if waiting:
		var l1 := "Beam 2 is unsealed. Click a node on the lit line:" if p.mode == "choice" else "Beam 2 is unsealed. Click the node to aim at:"
		var l2 := "the beam will skip it." if p.mode == "choice" else "then press SPACE as the ring closes."
		G.text(self, Vector2(PANEL_X + 20, y + 62), l1, 14, G.INK)
		G.text(self, Vector2(PANEL_X + 20, y + 84), l2, 14, G.INK)
		_btn(Rect2(PANEL_X + 20, y + 112, 420, 40), "HOLD THE SPOOF  [H]", "hold", true, 16)
	elif p.state == M10Play.S.PRESS:
		G.text(self, Vector2(PANEL_X + 20, y + 62), "Press SPACE when the ring meets the node.", 14, G.INK)
		_draw_timing_bar(Rect2(PANEL_X + 20, y + 100, 420, 22))
	elif p.spoof_used:
		var msg := ""
		var col := G.CLEAN
		if p.mode == "choice" or p.press_hit:
			msg = "Spoof used: beam 2 skipped the node."
		else:
			msg = "Spoof missed: the beam kept the node."
			col = G.DMG
		G.text(self, Vector2(PANEL_X + 20, y + 62), msg, 14, col)
	elif p.state in [M10Play.S.B1, M10Play.S.UNSEAL]:
		G.text(self, Vector2(PANEL_X + 20, y + 62), "Held for after the reveal.", 14, G.DIM)
	else:
		G.text(self, Vector2(PANEL_X + 20, y + 62), "Held, not used.", 14, G.DIM)
	# Found so far.
	var found_n := 0
	for e in p.events:
		if e["kind"] == "found":
			found_n += 1
	G.text(self, Vector2(PANEL_X, 430), "FOUND SO FAR", 14, G.DIM)
	for i in range(found_n):
		G.wrench(self, Vector2(PANEL_X + 30 + i * 46, 480), 14)
	if found_n == 0:
		G.check(self, Vector2(PANEL_X + 24, 478), 10, G.DIM)
		G.text(self, Vector2(PANEL_X + 44, 468), "nothing yet", 15, G.DIM)


func _beat_name() -> String:
	match play.state:
		M10Play.S.B1:
			return "BEAM 1"
		M10Play.S.UNSEAL:
			return "BEAM 2 UNSEALS"
		M10Play.S.DECIDE:
			return "SPOOF DECISION"
		M10Play.S.B2, M10Play.S.PRESS:
			return "BEAM 2"
		M10Play.S.HUNTER:
			return "THE HUNTER TURNS"
		M10Play.S.B3:
			return "BEAM 3"
	return "DONE"


func _draw_timing_bar(r: Rect2) -> void:
	var p := play
	draw_rect(r, Color8(30, 34, 56))
	var sweet_a := (M10Config.PRESS_PERFECT - M10Config.PRESS_TOL) / M10Config.PRESS_WINDOW
	var sweet_b := (M10Config.PRESS_PERFECT + M10Config.PRESS_TOL) / M10Config.PRESS_WINDOW
	draw_rect(Rect2(r.position.x + r.size.x * sweet_a, r.position.y, r.size.x * (sweet_b - sweet_a), r.size.y), Color(G.CLEAN.r, G.CLEAN.g, G.CLEAN.b, 0.5))
	draw_rect(r, G.PANEL_EDGE, false, 2.0)
	var mx := r.position.x + r.size.x * clampf(p.press_t / M10Config.PRESS_WINDOW, 0.0, 1.0)
	G.line(self, Vector2(mx, r.position.y - 6), Vector2(mx, r.end.y + 6), G.INK, 4.0)


# ---- aftermath ----
func _draw_after() -> void:
	var found: Array = row["found"]
	_draw_net(false, found, true)
	var offs := _offsets()
	var bsteps: Array = play.final["beams"]
	var g1 := _geom(model.b1, offs[0])
	_draw_path(_path(g1, _beam_u(bsteps[0], g1)), G.THREAT_FADE.lerp(G.THREAT, 0.5), 4.0)
	var g2 := _geom(model.cands[model.reveal], offs[model.reveal + 1])
	var u := _beam_u(bsteps[1], g2)
	_draw_path(_path(g2, u), G.THREAT_FADE.lerp(G.THREAT, 0.5), 4.0)
	var g3 := _geom(bsteps[2]["line"], _h_off(bsteps[2]["line"][0].x))
	_draw_path(_path(g3, _beam_u(bsteps[2], g3)), G.THREAT_FADE.lerp(G.THREAT, 0.5), 4.0)
	G.badge(self, _mid(g3), 3)
	var l: Dictionary = row["ledger"]
	if found.is_empty():
		G.stamp(self, Vector2(1010, 130), "EVADED", G.CLEAN, 50, "nothing found")
	else:
		G.stamp(self, Vector2(1010, 130), "CELL HOLDS", G.HOLD, 46, "%d DOWN" % found.size())
	_draw_ledger(l)
	var last := model.leg_over()
	_btn(Rect2(PANEL_X, 628, 460, 40), ("LEG RECORD  [Enter]" if last else "NEXT RAID  [Enter]"), "next", true, 18)


func _ledger_row(y: float, label: String, amount: String, col: Color, glyph: String = "") -> void:
	G.text(self, Vector2(PANEL_X + 20, y), label, 16, G.INK)
	G.text_r(self, Vector2(PANEL_X + 440, y), amount, 18, col)
	match glyph:
		"coin":
			G.coin(self, Vector2(PANEL_X + 320, y + 9), 7, col)
		"flame":
			G.flame(self, Vector2(PANEL_X + 320, y + 10), 7, col)


func _draw_ledger(l: Dictionary) -> void:
	G.panel(self, Rect2(PANEL_X, 214, 460, 404))
	var y := 226.0
	G.hexagon(self, Vector2(PANEL_X + 28, y + 10), 11, Color8(40, 30, 70), G.THREAT_LIGHT, 2.0)
	G.text(self, Vector2(PANEL_X + 50, y), "KEY  " + M10Config.key_label().to_upper(), 16, G.DIM)
	y += 30.0
	_ledger_row(y, "BEFORE", str(l["key_before"]), G.INK, "coin")
	y += 26.0
	var labels := {"decoy": "DECOY", "repair": "REPAIR  (%d DOWN)" % int(l["down"]), "evade": "EVADED", "short": "UNPAID (key at 0)", "cap": "OVER THE CAP"}
	for r in M10Rules.ledger_rows(l):
		var amt: int = int(r[1])
		var skip: bool = (r[0] == "decoy" and amt == 0) or (r[0] == "repair" and amt == 0 and int(l["down"]) == 0)
		if skip:
			continue
		_ledger_row(y, labels[r[0]], "%+d" % amt, G.CLEAN if amt > 0 else G.DMG, "coin")
		y += 26.0
	if M10Config.repair_mode() == "half":
		G.text(self, Vector2(PANEL_X + 20, y - 4), "repair = half of each asset's value", 12, G.DIM)
		y += 18.0
	draw_line(Vector2(PANEL_X + 20, y + 2), Vector2(PANEL_X + 440, y + 2), G.PANEL_EDGE, 2.0)
	y += 8.0
	_ledger_row(y, "AFTER", str(l["key_after"]), G.CELL, "coin")
	y += 40.0
	G.flame(self, Vector2(PANEL_X + 28, y + 10), 10)
	G.text(self, Vector2(PANEL_X + 50, y), "HEAT", 16, G.DIM)
	y += 30.0
	_ledger_row(y, "BEFORE", str(l["heat_before"]), G.INK, "flame")
	y += 26.0
	if int(l["heat_ghost"]) > 0:
		_ledger_row(y, "GHOST", "%+d" % int(l["heat_ghost"]), G.HOLD, "flame")
		y += 26.0
	if int(l["heat_evade"]) != 0:
		_ledger_row(y, "EVADED", "%+d" % int(l["heat_evade"]), G.CLEAN, "flame")
		y += 26.0
	_ledger_row(y, "AFTER", str(l["heat_after"]), G.HEAT, "flame")
	y += 34.0
	if int(l["dark_loss"]) > 0:
		G.coin(self, Vector2(PANEL_X + 28, y + 10), 8, G.DIM)
		G.line(self, Vector2(PANEL_X + 20, y + 20), Vector2(PANEL_X + 36, y + 2), G.DMG, 3.0)
		G.text(self, Vector2(PANEL_X + 50, y), "Dark: next income lost %d (not from the key)" % int(l["dark_loss"]), 13, G.DIM)


# ---- leg record ----
func _draw_record() -> void:
	G.text(self, Vector2(60, 96), "LEG RECORD", 22, G.INK)
	for j in range(model.history.size()):
		var h: Dictionary = model.history[j]
		var l: Dictionary = h["ledger"]
		var r := Rect2(60 + j * 390, 140, 370, 400)
		G.panel(self, r, G.CLEAN if h["evaded"] else G.HOLD, G.PANEL, 3.0)
		G.text(self, Vector2(r.position.x + 20, r.position.y + 14), "RAID %d" % (j + 1), 20, G.DIM)
		if h["evaded"]:
			G.check(self, Vector2(r.position.x + 330, r.position.y + 28), 12, G.CLEAN)
			G.text(self, Vector2(r.position.x + 20, r.position.y + 54), "EVADED", 30, G.CLEAN)
		else:
			G.wrench(self, Vector2(r.position.x + 330, r.position.y + 30), 14)
			G.text(self, Vector2(r.position.x + 20, r.position.y + 54), "%d DOWN" % int(l["down"]), 30, G.HOLD)
		G.coin(self, Vector2(r.position.x + 34, r.position.y + 140), 10)
		G.text(self, Vector2(r.position.x + 56, r.position.y + 128), "%d  ->  %d" % [l["key_before"], l["key_after"]], 24, G.INK)
		G.flame(self, Vector2(r.position.x + 34, r.position.y + 200), 11)
		G.text(self, Vector2(r.position.x + 56, r.position.y + 188), "%d  ->  %d" % [l["heat_before"], l["heat_after"]], 24, G.HEAT)
		var parts: Array = []
		if int(l["decoy"]) > 0:
			parts.append("decoy -%d" % int(l["decoy"]))
		if int(l["repair"]) > 0:
			parts.append("repair -%d" % int(l["repair"]))
		if int(l["evade_gain"]) > 0:
			parts.append("evade +%d" % int(l["evade_gain"]))
		G.text(self, Vector2(r.position.x + 20, r.position.y + 250), ", ".join(parts), 15, G.DIM)
		G.text(self, Vector2(r.position.x + 20, r.position.y + 276), "ghost %d, decoy %d, dark %d" % [h["plan"]["ghost"].size(), h["plan"]["decoys"].size(), h["plan"]["dark"].size()], 14, G.DIM)
		G.text(self, Vector2(r.position.x + 20, r.position.y + 300), "spoof: " + ("landed" if not (h["spoof"] as Array).is_empty() else "not landed"), 14, G.DIM)
	_btn(Rect2(60, 570, 400, 52), "PLAY THE LEG AGAIN  [Enter]", "next", true, 18)


# ---------- capture ----------
func _snap(shot_name: String) -> void:
	queue_redraw()
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [capture_dir, shot_name])
	print("shot ", shot_name)


## The spoof the capture driver aims: the node of the revealed line whose skip saves the most (a driver choice only).
func _capture_spoof() -> Vector2i:
	var best := Vector2i(-1, -1)
	var best_v := -1.0e9
	for c in model.cands[model.reveal]:
		var f := M10Rules.found_of(model.assets, model.b1, model.cands[model.reveal], model.own3, model.plan, [1, c])
		var v := M10Rules.value(model.assets, f, model.plan)
		if v > best_v:
			best_v = v
			best = c
	return best


func _advance_to(target_state: int, extra: float = 0.0) -> void:
	var guard := 0
	while play.state != target_state and not play.is_waiting() and not play.is_done() and guard < 2000:
		play.advance(0.05, 0.05)
		guard += 1
	if extra > 0.0:
		play.advance(extra, extra)


func _run_capture() -> void:
	DirAccess.make_dir_recursive_absolute(capture_dir)
	var n := 0
	await _snap("%02d_contact" % n)
	n += 1
	_act("next")
	await _snap("%02d_plan_empty" % n)
	n += 1
	_act("lever:ghost")
	_click_cell(Vector2i(3, 0))
	_act("lever:decoy")
	_click_cell(Vector2i(3, 1))
	_act("lever:dark")
	_click_cell(Vector2i(0, 0))
	sel_lever = ""
	await _snap("%02d_plan_levers" % n)
	n += 1
	_act("next")
	await _snap("%02d_forecast" % n)
	n += 1
	_act("next")
	play.advance(0.9, 0.9)
	await _snap("%02d_playout_beam1" % n)
	n += 1
	_advance_to(M10Play.S.UNSEAL, 0.5)
	await _snap("%02d_playout_unseal" % n)
	n += 1
	_advance_to(M10Play.S.DECIDE)
	await _snap("%02d_playout_decision" % n)
	n += 1
	var target := _capture_spoof()
	play.choose_spoof(target)
	if play.mode == "press":
		_advance_to(M10Play.S.PRESS)
		play.advance(0.0, 0.3)
		await _snap("%02d_playout_press_window" % n)
		n += 1
		play.advance(0.0, 0.4)
		play.press()
	play.advance(0.9, 0.9)
	await _snap("%02d_playout_beam2" % n)
	n += 1
	_advance_to(M10Play.S.HUNTER, 0.6)
	await _snap("%02d_playout_hunter" % n)
	n += 1
	_advance_to(M10Play.S.B3, 0.5)
	await _snap("%02d_playout_beam3" % n)
	n += 1
	play.skip()
	_check_done()
	await _snap("%02d_aftermath" % n)
	n += 1
	# The rest of the leg, to show the record screen (golden best_both plan, no spoof).
	for i in range(2):
		_act("next")
		await _snap("%02d_contact_raid%d" % [n, i + 2])
		n += 1
		var raw: Dictionary = model.case_["plans"]["best_both"]
		model.plan = M10Data.plan_of(raw)
		phase = Phase.PLAN
		_launch()
		play.skip()
		if play.state == M10Play.S.DECIDE:
			play.pass_spoof()
			play.skip()
		_check_done()
	_act("next")
	await _snap("%02d_record" % n)
	get_tree().quit(0)


func _loss_str(n: int) -> String:
	return "0" if n == 0 else "-%d" % n
