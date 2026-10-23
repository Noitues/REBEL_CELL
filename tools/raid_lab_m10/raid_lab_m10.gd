extends Control
## L5 sweep-raid lab: the playable view. Reads L5Model / L5Play and draws; the rules live in L5Rules.
## Flow: contact (the raid's strength by Heat band), plan (the leg kit tray, levers), forecast (per sealed line: the hold
## result, the nodes a spoof could save and the range with a spoof; it never names a best spoof), hands-off playout with
## the spoof decision, aftermath (outcome tier), the between-raids screen (repairs, one shop buy, run intensity), leg
## record. A touch that takes HOME to 0 integrity ends the sweep and the campaign (BREACH, full screen).
## Capture mode: `-- --shots=<abs dir> [--leg=0] [--line=planned|naive|greedy] [--lite] [--scramble]` plays the whole leg.

enum Phase { CONTACT, PLAN, FORECAST, PLAY, AFTER, REPAIR, BREACH, RECORD }

const G = preload("res://tools/raid_lab_m10/l5_glyphs.gd")
const SPEEDS := [1.0, 2.0, 4.0]
const NODE_R := 28.0
const DASHES := [Vector2(18, 8), Vector2(6, 6), Vector2(14, 4)]
const PANEL_X := 780.0
const PANEL_W := 460.0
const STRIP_Y := 676.0
## Where a spoof mark sits on its node (up and right, clear of the sealed lines' caps).
const SPOOF_OFF := Vector2(36, -34)
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
		elif a == "--demo=breachfix":
			cap_demo = "breachfix"
		elif a == "--demo=ownline":
			cap_demo = "ownline"
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
	elif id == "jam":
		if phase == Phase.PLAY and play != null:
			play.choose_jam()
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
		if play.state == L5Play.S.DECIDE:
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
	var col_key := str(L5Rules.column(x))
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
			var rk := model.real()
			return _geom(rd["cands"][rk], offs[3 + rk])
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
	_draw_age_labels()
	_draw_strip()


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
		var p := nx(c)
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
	var fillw := hw * clampf(float(heat) / L5Config.HEAT_MAX, 0.0, 1.0)
	var base_w := hw * clampf(float(heat - maxi(0, dh)) / L5Config.HEAT_MAX, 0.0, 1.0)
	draw_rect(Rect2(hx, hy, base_w, 20), G.HEAT)
	if dh > 0:
		draw_rect(Rect2(hx + base_w, hy, fillw - base_w, 20), G.HOLD)
	elif dh < 0:
		draw_rect(Rect2(hx + fillw, hy, base_w - fillw, 20), Color8(255, 110, 40, 90))
	draw_rect(Rect2(hx, hy, hw, 20), G.PANEL_EDGE, false, 2.0)
	for band in [[L5Config.EXTRA_AT, "+1 BEAM"], [L5Config.STRONG_AT, "+2 BEAMS"]]:
		var bxp: float = hx + hw * float(band[0]) / L5Config.HEAT_MAX
		var lit: bool = heat >= int(band[0])
		G.line(self, Vector2(bxp, hy - 5), Vector2(bxp, hy + 25), G.THREAT_LIGHT if lit else G.THREAT_FADE, 3.0)
		G.text(self, Vector2(bxp + 5, hy + 27), "%d: %s" % [band[0], band[1]], 12, G.THREAT_LIGHT if lit else G.DIM)
	G.text(self, Vector2(hx + hw + 10, hy - 3), str(heat), 22, G.HEAT)
	if dh != 0:
		G.text(self, Vector2(hx + hw + 52, hy), "%+d" % dh, 17, G.HOLD if dh > 0 else G.CLEAN)
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
	# Home integrity pips (with the projected loss in the forecast).
	G.text(self, Vector2(640, 12), "HOME", 13, G.DIM)
	var hp: int = int(v["hp"])
	var proj: Array = v["proj"]
	for k in range(L5Config.HOME_HP):
		var mode := "full"
		if k >= hp:
			mode = "lost"
		elif phase == Phase.FORECAST and k >= hp - int(proj[0]):
			mode = "saved" if (L5Config.spoof_view() and k < hp - int(proj[1])) else "proj"
		G.pip(self, Vector2(650 + k * 28, 42), 18.0, mode)
	# Bank: the number, and on the between screen the net change this step makes ("net", never a bare +N).
	var bx := 830.0
	G.coin(self, Vector2(bx + 12, 31), 11)
	G.text(self, Vector2(bx + 34, 14), str(v["bank"]), 26, G.CELL)
	if int(v["dbank"]) != 0:
		G.text(self, Vector2(bx + 92, 20), "net %+d" % int(v["dbank"]), 14, G.DMG if int(v["dbank"]) < 0 else G.CLEAN)
	G.text(self, Vector2(bx + 150, 20), L5Config.key_label().to_upper(), 13, G.DIM)
	# Assets kept, live (the score term the player otherwise meets only on the record).
	var kx := 1112.0
	G.text(self, Vector2(kx, 10), "ASSETS KEPT", 13, G.DIM)
	G.text(self, Vector2(kx, 24), str(v["kept"]), 26, G.INK)
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
			hint = "Forecast: each shape marks what that sealed line would do; a teal chevron marks a node a spoof could save. B edits. Enter launches."
		Phase.PLAY:
			hint = "Hands-off sweep. 1 / 2 / 4 speed, S skips. The response after the reveal (hold, skip or jam) needs you."
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
## Draw HOME: the server glyph, its integrity pips, a ghost ring.
func _draw_home(p: Vector2, hp: int, pl: Dictionary, loss: int = 0) -> void:
	var ghost: bool = (pl["ghost"] as Array).has(model.home())
	G.home_server(self, p, 28.0, G.INK)
	if ghost:
		G.dashed_ring(self, p, 38.0, G.CELL, 4.0)
		G.flame(self, p + Vector2(34, -32), 7)
	for k in range(L5Config.HOME_HP):
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
	if dark and st == "OK":
		# Go dark: the node is black and its income chip is struck (it earns nothing this interval).
		var inc := L5Rules.idiv(v, L5Config.INCOME_DIV)
		var cr := Rect2(p.x - 26, p.y - 60, 52, 22)
		G.panel(self, cr, G.DIM, G.BG, 1.0)
		G.coin(self, Vector2(cr.position.x + 12, cr.position.y + 11), 5, G.DIM)
		G.text(self, Vector2(cr.position.x + 22, cr.position.y + 4), "+%d" % inc, 13, G.DIM)
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
	var y := 648.0
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


## The sealed candidates: dashed lines told apart by end shape and dash pattern (the shape of each candidate is
## shuffled per raid). `only` is the lit candidate; `fade` dims the others. A decoy stops them like any beam.
func _draw_candidates(only: int = -1, fade: float = 0.0) -> void:
	var offs := _offsets()
	var cands: Array = model.raid_data()["cands"]
	for i in range(cands.size()):
		var g := _geom(cands[i], offs[3 + i])
		var sh: int = model.shape(i)
		var col := G.THREAT_LIGHT
		if only >= 0 and i != only:
			col = G.THREAT_LIGHT.lerp(G.THREAT_FADE, fade)
		var full := float((g["pts"] as Array).size() + 1)
		var u := _stop_u(cands[i], g)
		_draw_dashed_path(_path(g, u), col, DASHES[sh], 4.0)
		if u < full:
			_stop_bar(g, u, col)
		var a: Vector2 = g["a"]
		G.cand_shape(self, a, sh, 11.0, col, G.BG)
		if only >= 0 and i == only:
			continue	## the lit beam draws its own badge
		G.badge(self, a - (g["dir"] as Vector2) * 28.0, "?", col.darkened(0.2) if only >= 0 else G.THREAT)


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
		_hunter_col(known_first.x, G.THREAT_LIGHT, 3.0, "3", Vector2(10, 6), 0.0)
		G.turn_arrow(self, nx(known_first), 22.0, G.THREAT_LIGHT, 4.0, 1.0, -_h_off(known_first.x))
		return
	var own_needed := false
	var arrows: Array = []
	for f: Dictionary in fc:
		var sh: int = f["shape"]
		var fst: Vector2i = f["first"]
		if fst != L5Rules.NONE:
			var col := G.THREAT_LIGHT.darkened(0.25)
			_hunter_col(fst.x, col, 2.0, "", DASHES[sh], (sh - 1) * 12.0, sh)
			if not arrows.has(fst):
				arrows.append(fst)
				G.turn_arrow(self, nx(fst), 22.0, col, 3.0, 1.0, -((sh - 1) * 12.0 + _h_off(fst.x)))
		else:
			own_needed = true
	if own_needed:
		var ox: int = (model.raid_data()["own3"][0] as Vector2i).x
		_hunter_col(ox, G.THREAT_LIGHT.darkened(0.45), 2.0, "3", Vector2(4, 8), 0.0)
		G.own_line(self, nx(Vector2i(ox, 0)) + Vector2(-_h_off(ox), -66.0), 6.0, G.THREAT_LIGHT.darkened(0.45))


func _hunter_col(x: int, col: Color, w: float, badge_s: String, dash: Vector2, off: float, shape_i: int = -1) -> void:
	var line := L5Rules.column(x)
	var g := _geom(line, off + _h_off(x))
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
	_draw_net(false)
	_draw_known_beams(extra, false)
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
	_draw_net(true)
	_draw_known_beams(model.extra_now(), true)
	_draw_candidates()
	_draw_hunter_plan(fc)
	_draw_ghost_skips()
	if fc_mode:
		_draw_forecast_marks(fc)
	if sel_lever != "":
		for c in L5Rules.nodes():
			var p := nx(c)
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
	_draw_legend()


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
	G.text(self, Vector2(r.position.x + 74, r.position.y + 4), "%s  [%s]" % [nm[0], nm[2]], 16, G.INK)
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
	var r := Rect2(20, 66, 740, 56)
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
		G.circle(self, nx(c), NODE_R + 14.0 + 3.0 * pulse, G.CLEAN, 4.0)
		_kit_icon(lv, Vector2(x + 8, r.position.y + 40), 6.0, G.CLEAN)
		x += 22.0
	G.text(self, Vector2(x + 2, r.position.y + 32), "Avoid it: %s (ringed)." % " and ".join(parts), 13, G.CLEAN)


## FORECAST: on each node, one slot per sealed line that touches it (shape = the line, glyph = the outcome); a teal
## spoof mark (the line's shape, then a skip-chevron) on every node a spoof could save for that line.
func _draw_forecast_marks(fc: Array) -> void:
	var sv := L5Config.spoof_view()
	for f: Dictionary in fc:
		var sh: int = f["shape"]
		var done: Array = []
		for o: Dictionary in f["outcomes"]:
			var c: Vector2i = o["cell"]
			if done.has(c):
				continue
			done.append(c)
			var p := nx(c) + Vector2((sh - 1) * 46.0, 58.0)
			G.cand_shape(self, p + Vector2(-9, 0), sh, 7.0, G.THREAT_LIGHT, G.BG, 2.0)
			match o["outcome"]:
				"DOWN":
					G.disc(self, p + Vector2(9, 0), 8, GREY)
					G.bolt(self, p + Vector2(9, 0), 6.0)
				"TAKEN":
					G.corp(self, p + Vector2(9, 0), 8.0)
				"HOME":
					G.text_c(self, p + Vector2(10, 0), "-1", 13, G.DMG)
				_:
					G.diamond(self, p + Vector2(9, 0), 6.0, G.CELL, 2.0)
		if sv and f["can_spoof"]:
			for sc: Vector2i in f["save_cells"]:
				var q := nx(sc) + Vector2((sh - 1) * 40.0, -50.0)
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
	_draw_net_play(sn)
	var st: int = p.state
	var cur: int = p.order.size()
	if st in [L5Play.S.BEAM, L5Play.S.UNSEAL, L5Play.S.DECIDE, L5Play.S.NOTE, L5Play.S.TURN]:
		cur = p.beam_idx()
	var b2_i: int = p.order.find("b2")
	# Sealed candidates until beam 2 unseals.
	if cur < b2_i:
		_draw_candidates()
	elif st == L5Play.S.UNSEAL:
		_draw_candidates(model.real(), clampf(p.t / L5Config.UNSEAL_T, 0.0, 1.0))
	else:
		_draw_candidates(model.real(), 0.8)
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
			var lit := G.THREAT_LIGHT.lerp(G.THREAT, 0.5)
			if st in [L5Play.S.UNSEAL, L5Play.S.DECIDE, L5Play.S.NOTE]:
				var a := clampf(p.t / L5Config.UNSEAL_T, 0.0, 1.0) if st == L5Play.S.UNSEAL else 1.0
				_draw_path(_path(g, float(g["pts"].size() + 1)), Color(lit.r, lit.g, lit.b, 0.35 + 0.65 * a), 5.0)
			elif bs == "now":
				_draw_path(_path(g, float(g["pts"].size() + 1)), G.THREAT_FADE, 4.0, false)
				_draw_path(_path(g, minf(p.head(), u_full)), G.THREAT_LIGHT, 8.0)
			else:
				_draw_path(_path(g, u_full), G.THREAT, 6.0)
		elif id == "hunter":
			if st == L5Play.S.TURN:
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
	# The hunter's rule stays on the grid from the turn on: an arrow from the first touch, turning down its column.
	var h_i: int = p.order.find("hunter")
	var hf: Vector2i = p.hunter_from()
	if h_i >= 0 and hf != L5Rules.NONE and cur >= h_i and not (p.cut and p.last_beam() < h_i):
		var prog := 1.0
		if st == L5Play.S.TURN:
			prog = clampf(p.t / L5Config.TURN_T * 1.5, 0.0, 1.0)
		G.turn_arrow(self, nx(hf), 22.0, G.THREAT_LIGHT, 5.0, prog, -_h_off(hf.x))
	if not p.hunter_runs() and not p.cut:
		_draw_jam_chip(Vector2(20, 70))
	# The response after the reveal: the focused option's consequence on the grid, and a SKIP target on every lit node.
	if st == L5Play.S.DECIDE:
		for c: Vector2i in p.b2:
			var pc := nx(c)
			var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 220.0)
			_spoof_mark(pc + SPOOF_OFF, 9.0 + 2.0 * pulse)
			_cell_hit(c)
		_draw_decision_preview()
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
	var a3 := clampf(play.t / L5Config.TURN_T, 0.0, 1.0)
	var first: Vector2i = play.hunter_from()
	var col := Color(G.THREAT_LIGHT.r, G.THREAT_LIGHT.g, G.THREAT_LIGHT.b, a3)
	if first != L5Rules.NONE:
		var pf := nx(first)
		G.circle(self, pf, NODE_R + 8 + 6.0 * sin(play.t * 8.0), G.DMG, 4.0)
		_draw_dashed_path(_path(g, float(g["pts"].size() + 1)), col, Vector2(10, 6), 4.0)
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
		G.circle(self, nx(foc), NODE_R + 12.0, G.CLEAN, 4.0)
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
			G.circle(self, nx(e["cell"]), NODE_R + 10, G.INK, 2.0)
	if play.spoof_used and play.spoof != L5Rules.JAM and play.state != L5Play.S.DECIDE:
		_spoof_mark(nx(play.spoof) + SPOOF_OFF, 9.0)


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
	for i in range(3):
		var r := Rect2(PANEL_X + i * 84, 144, 76, 36)
		G.panel(self, r, G.CELL if speed_i == i else G.PANEL_EDGE, Color8(60, 52, 24) if (speed_i == i or _hot(r)) else G.PANEL, 3.0 if speed_i == i else 2.0)
		G.text_c(self, r.get_center(), labels[i], 17, G.CELL if speed_i == i else G.INK)
		_add_hit(r, "speed:%d" % i)
	var rs := Rect2(PANEL_X + 252, 144, 100, 36)
	G.panel(self, rs, G.PANEL_EDGE, Color8(60, 52, 24) if _hot(rs) else G.PANEL, 2.0)
	G.text_c(self, rs.get_center(), "SKIP [S]", 15, G.INK)
	_add_hit(rs, "skip")
	if p.state == L5Play.S.DECIDE:
		_draw_response_box(Rect2(PANEL_X, 188, PANEL_W, 410))
	else:
		dec_focus = NO_FOCUS
		_draw_spoof_box(Rect2(PANEL_X, 194, PANEL_W, 226))
		_draw_hit_log(432.0)


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
	G.text_r(self, Vector2(box.end.x - 14, box.position.y + 8), "%d spoof in the kit" % int(p.before.kit["spoof"]), 13, G.DIM)
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
	var p := nx(c) + Vector2(-46, 34)
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
	_draw_net(false, after.status, after.home_hp, row["alloc"])
	for b: Dictionary in row["beams"]:
		var g := _beam_geom(b["id"], b["line"])
		_draw_path(_path(g, _beam_u(b, g)), G.THREAT_FADE.lerp(G.THREAT, 0.5), 4.0)
		var badge_s := {"b1": "1", "extra": "+", "extra2": "++", "b2": "2", "hunter": "3"}[b["id"]] as String
		if b["id"] == "hunter":
			G.badge(self, _mid(g), badge_s)
		else:
			_start_badge(g, badge_s)
	var hunter_ran := false
	for b: Dictionary in row["beams"]:
		hunter_ran = hunter_ran or b["id"] == "hunter"
	if hunter_ran and row["first"] != L5Rules.NONE:
		G.turn_arrow(self, nx(row["first"]), 22.0, G.THREAT_LIGHT, 5.0, 1.0, -_h_off((row["first"] as Vector2i).x))
	elif row["spoof"] == L5Rules.JAM:
		_draw_jam_chip(Vector2(20, 70))
	var done: Array = []
	for o: Dictionary in row["outcomes"]:
		if not done.has(o["cell"]):
			done.append(o["cell"])
			_node_tag(o["cell"], o["outcome"])
	if row["spoof"] != L5Rules.NONE and row["spoof"] != L5Rules.JAM:
		_spoof_mark(nx(row["spoof"]) + SPOOF_OFF, 9.0)
	var sm: Dictionary = row["summary"]
	var tier: String = row["tier"]
	var col := G.tier_color(tier)
	var parts: Array = []
	if int(sm["down"]) > 0:
		parts.append("%d DOWN" % int(sm["down"]))
	if int(sm["taken"]) > 0:
		parts.append("%d TAKEN" % int(sm["taken"]))
	if int(sm["home"]) > 0:
		parts.append("HOME -%d" % int(sm["home"]))
	match tier:
		"EVADED":
			G.stamp(self, Vector2(1010, 122), "EVADED", col, 44, "nothing touched")
		"HOLDS":
			G.stamp(self, Vector2(1010, 122), "CELL HOLDS", col, 40, "  ".join(parts) if not parts.is_empty() else "a decoy took the beam")
		"BATTERED":
			G.stamp(self, Vector2(1010, 122), "CELL BATTERED", col, 36, "  ".join(parts))
		_:
			G.stamp(self, Vector2(1010, 122), "CELL DAMAGED", col, 38, "  ".join(parts))
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
	var vals: Dictionary = model.values()
	for c: Vector2i in s.status:
		var pp := nx(c)
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
			G.text_c(self, pp + Vector2(0, 46), "+%d" % inc, 14, G.CLEAN)
	for c: Vector2i in model.pending_repairs:
		G.text_c(self, nx(c) + Vector2(0, -42), "REPAIRED", 12, G.CLEAN)
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
	_btn(Rect2(PANEL_X, 624, PANEL_W, 44), "NEXT RAID  [Enter]", "next", true, 18)
	_draw_legend()


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


## The risk text on an intensity card: red frame for a breach, amber for "safe with levers", teal for "safe".
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
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), Color8(34, 6, 12))
	# The dead network, dim, behind the end card.
	var after: L5State = row["after_raid"]
	var saved := Color8(34, 6, 12)
	for c in L5Rules.nodes():
		_draw_node(c, after.status, 0, row["alloc"])
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), Color(saved.r, saved.g, saved.b, 0.94))
	var cx := 640.0
	# A broken HOME server.
	var hc := Vector2(cx, 170)
	G.home_server(self, hc, 56.0, G.DMG, Color8(60, 10, 20))
	G.line(self, hc + Vector2(-40, -62), hc + Vector2(-8, -4), Color8(34, 6, 12), 8.0)
	G.line(self, hc + Vector2(-8, -4), hc + Vector2(-34, 60), Color8(34, 6, 12), 8.0)
	G.line(self, hc + Vector2(40, -62), hc + Vector2(14, 8), Color8(34, 6, 12), 8.0)
	for k in range(L5Config.HOME_HP):
		G.pip(self, Vector2(cx + (k - 1) * 34.0, 252), 22.0, "lost")
	G.text_c(self, Vector2(cx, 330), "BREACHED", 84, G.DMG)
	G.text_c(self, Vector2(cx, 398), "THE CAMPAIGN IS LOST", 30, G.INK)
	G.text_c(self, Vector2(cx, 446), "Raid %d: the beams reached HOME and its last integrity went." % (int(row["raid"]) + 1), 18, G.DIM)
	var l: Dictionary = row["ledger"]
	G.text_c(self, Vector2(cx, 480), "HOME %d -> 0   |   Heat %d" % [l["home_before"], l["heat_after"]], 16, G.DIM)
	_btn(Rect2(cx - 200, 540, 400, 52), "LEG RECORD  [Enter]", "next", true, 20)


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


## A teal skip-chevron in a round badge: "a spoof skips this node".
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


## A node as a small round chip (its value, or the HOME server), edged teal for the spoof list.
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


const KIT_COL := {"ghost": Color8(255, 210, 63), "decoy": Color8(255, 210, 63), "spoof": Color8(90, 220, 200), "dark": Color8(206, 214, 236)}


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


## A numbered shot: the number is the frame's place in the leg, so the folder sorts in play order.
func _shot(label: String) -> void:
	var shot_name := "%02d_%s" % [_shot_n, label]
	_shot_n += 1
	await _snap(shot_name)


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
				await _shot("r%d_decision" % rn)
				dec_pin = NO_FOCUS
			if spoof_cell == null:
				_act("hold")
			elif spoof_cell is String:
				_act("jam")
			else:
				var sc: Vector2i = spoof_cell
				_act("cell:%d,%d" % [sc.x, sc.y])
			if not cap_lite:
				await _shot("r%d_after_decision" % rn)
			continue
		if play.state == L5Play.S.NOTE and play.t >= 0.3 and not seen.has("note"):
			seen["note"] = true
			await _shot("r%d_no_spoof_left" % rn)
		play.advance(0.05)
		if play.state == L5Play.S.BEAM:
			var n: int = play.beam_steps(play.bi).size()
			if play.t >= (n * 0.5 + 0.6) * L5Config.STEP_T and not seen.has("beam_" + bid):
				seen["beam_" + bid] = true
				if not cap_lite or bid in ["b1", "hunter"]:
					await _shot("r%d_beam_%s" % [rn, bid])
		elif play.state == L5Play.S.UNSEAL and play.t >= 0.5 and not seen.has("unseal"):
			seen["unseal"] = true
			if not cap_lite:
				await _shot("r%d_unseal" % rn)
		elif play.state == L5Play.S.TURN and play.t >= 0.45 and not seen.has("turn"):
			seen["turn"] = true
			if not cap_lite:
				await _shot("r%d_hunter_turn" % rn)
		elif play.state == L5Play.S.END and play.cut and not seen.has("cut"):
			seen["cut"] = true
			await _shot("r%d_breach_touch" % rn)
	_check_done()


## Demo frames of the breach warning that names a lever: golden naive leg 0 at raid 3 (every line breaches), with one
## ghost put back in the kit so a lever exists. Plan with the warning, the lever placed, the forecast without a breach.
func _run_demo_breachfix() -> void:
	var steps: Array = model.leg["naive"]
	model.raid = 2
	model.state = L5State.from_golden(steps[2]["before"])
	model.state.kit["ghost"] = 1
	phase = Phase.PLAN
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
	phase = Phase.PLAN
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


func _run_capture() -> void:
	DirAccess.make_dir_recursive_absolute(capture_dir)
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
			await _shot("r%d_aftermath" % rn)
		elif phase == Phase.BREACH:
			await _shot("r%d_breach" % rn)
			_act("next")
			break
		_act("next")
		if phase == Phase.REPAIR:
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
	await _shot("record")
	get_tree().quit(0)

