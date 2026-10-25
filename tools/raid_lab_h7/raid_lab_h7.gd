extends Control
## H7 Bastion raid lab: the playable view. Reads H7LabModel and draws; the rules live in the H7* classes.
## Flow: leg view, visit (shop, crew, forecast), hands-off raid playout, aftermath, leg record.
## Capture mode: `-- --shots=<abs dir>` auto-plays leg 0's planned line and saves PNGs.

enum Phase { LEG, VISIT, PLAY, AFTER, RECORD }

const G = preload("res://tools/raid_lab_h7/h7_glyphs.gd")
const MAP_O := Vector2(290, 120)
const MAP_S := 0.72
const BASE_POS := {"HOME": Vector2(110, 260), "FW": Vector2(300, 140), "VAULT": Vector2(330, 290), "SAFE": Vector2(290, 440),
	"RELAY": Vector2(510, 150), "PROXY": Vector2(520, 400), "C1": Vector2(710, 80), "C2": Vector2(720, 470)}
const NODE_NAME := {"HOME": "HOME SERVER", "FW": "FIREWALL", "VAULT": "VAULT", "SAFE": "SAFEHOUSE", "RELAY": "RELAY",
	"PROXY": "PROXY", "C1": "SOLACE CLINIC", "C2": "SOLACE DEPOT"}
const NODE_R := 22.0
const PIECE_NAME := {"TURRET": "TURRET", "SENTRY": "SENTRY", "RAILGUN": "RAILGUN", "ICE": "ICE", "DECOY": "DECOY"}
const SPEEDS := [1.0, 2.0, 4.0]

var model := H7LabModel.new()
var phase: int = Phase.LEG
var sel_piece: String = ""
var sel_crew: bool = false
var play_t: float = 0.0
var speed_i: int = 0
var row: Dictionary = {}
var hits: Array = []
var mouse: Vector2 = Vector2(-100, -100)
var capture_dir: String = ""
var status_msg: String = ""
var cap_leg: int = 0
var cap_bare: bool = false


func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shots="):
			capture_dir = a.substr(8)
		elif a.begins_with("--leg="):
			cap_leg = int(a.substr(6))
		elif a == "--nobuy":
			cap_bare = true
	if capture_dir != "":
		_run_capture.call_deferred()


func _process(delta: float) -> void:
	if phase == Phase.PLAY and capture_dir == "":
		play_t += delta * SPEEDS[speed_i]
		if play_t >= _beats():
			_finish_playout()
	queue_redraw()


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		mouse = (event as InputEventMouseMotion).position
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		for k in range(hits.size() - 1, -1, -1):
			if (hits[k]["rect"] as Rect2).has_point(event.position):
				_act(hits[k]["id"])
				return
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
				if phase == Phase.VISIT:
					sel_piece = H7Data.PIECES[event.keycode - KEY_1]
					sel_crew = false
			KEY_ENTER, KEY_SPACE:
				match phase:
					Phase.LEG:
						_act("enter")
					Phase.VISIT:
						_act("start")
					Phase.AFTER:
						_act("next")
					Phase.RECORD:
						_act("restart")
			KEY_Z:
				_act("undo")
			KEY_ESCAPE:
				sel_piece = ""
				sel_crew = false


# ---------- actions ----------
func _act(id: String) -> void:
	status_msg = ""
	if id.begins_with("leg:"):
		if phase == Phase.LEG:
			model.new_leg(int(id.substr(4)))
	elif id == "enter":
		phase = Phase.VISIT
		sel_piece = ""
		sel_crew = false
	elif id.begins_with("piece:"):
		var p := id.substr(6)
		if model.can_buy(p):
			sel_piece = "" if sel_piece == p else p
			sel_crew = false
		else:
			status_msg = "Cannot buy %s: %s" % [p, "2 pieces per visit" if model.buys.size() >= H7LabModel.MAX_BUYS else "not enough bank"]
	elif id == "crewtok":
		if model.crew_free():
			sel_crew = not sel_crew
			sel_piece = ""
		else:
			status_msg = "The SAFEHOUSE is lost: the crew cannot station"
	elif id.begins_with("node:"):
		_click_node(id.substr(5))
	elif id == "undo":
		model.undo()
	elif id == "start":
		_start_raid()
	elif id.begins_with("speed:"):
		speed_i = int(id.substr(6))
	elif id == "skip":
		_finish_playout()
	elif id == "next":
		if model.leg_over():
			phase = Phase.RECORD
		else:
			model.next_visit()
			phase = Phase.VISIT
	elif id == "restart":
		model.new_leg(model.leg_index)
		phase = Phase.LEG


func _click_node(n: String) -> void:
	if phase != Phase.VISIT:
		return
	if model.state.lost.has(n):
		status_msg = "%s is lost for the leg" % NODE_NAME[n]
		return
	if sel_piece != "":
		if model.buy_place(sel_piece, n):
			if not model.can_buy(sel_piece):
				sel_piece = ""
		return
	if sel_crew:
		model.station_crew(n)
		sel_crew = false


func _start_raid() -> void:
	row = model.start_raid()
	phase = Phase.PLAY
	play_t = 0.0
	sel_piece = ""
	sel_crew = false


func _finish_playout() -> void:
	phase = Phase.AFTER


func _beats() -> int:
	return (row["r"] as H7Result).steps.size() * 2


# ---------- drawing ----------
func _np(id: String) -> Vector2:
	return MAP_O + BASE_POS[id] * MAP_S


func _add_hit(r: Rect2, id: String) -> void:
	hits.append({"rect": r, "id": id})


func _hot(r: Rect2) -> bool:
	return r.has_point(mouse)


func _btn(r: Rect2, label: String, id: String, enabled: bool = true, size: int = 20) -> void:
	G.button(self, r, label, _hot(r), enabled, size)
	if enabled:
		_add_hit(r, id)


func _draw() -> void:
	hits = []
	draw_rect(Rect2(Vector2.ZERO, Vector2(1280, 720)), G.BG)
	var fc: Array = []
	if phase == Phase.VISIT or phase == Phase.LEG:
		fc = model.forecast()
	_draw_raid_panels(fc)
	_draw_left()
	match phase:
		Phase.LEG:
			_draw_map(fc[0]["r"], fc[0]["fort"], model.state, true)
			_draw_leg_right()
		Phase.VISIT:
			_draw_map(fc[0]["r"], fc[0]["fort"], model.state, true)
			_draw_visit(fc)
		Phase.PLAY:
			_draw_play()
		Phase.AFTER:
			_draw_map(row["r"], row["fort"], row["settle"].state, true)
			_draw_after()
		Phase.RECORD:
			_draw_record()
	_draw_status()


func _draw_status() -> void:
	draw_rect(Rect2(0, 700, 1280, 20), Color(0, 0, 0, 0.5))
	var hint := ""
	match phase:
		Phase.LEG:
			hint = "Pick a leg, then enter the first visit. Raids ahead are telegraphed (2 while the PROXY holds)."
		Phase.VISIT:
			hint = "Click a piece, then a held node to buy and place it (max 2 per visit). Click the crew, then a node. Z undoes. Enter starts the raid."
		Phase.PLAY:
			hint = "The raid plays out by itself. Only the speed controls and skip work."
		Phase.AFTER:
			hint = "Aftermath. Enter continues."
		Phase.RECORD:
			hint = "Leg record. Enter replays this leg."
	if status_msg != "":
		hint = status_msg
	G.text(self, Vector2(10, 702), "H7 BASTION lab  |  " + hint, 13, G.DIM)


## The fighting roster: a repeated id keeps its first slot with the last entry, as the resolver does.
func _uniq(roster: Array) -> Array:
	var out: Array = []
	for t in roster:
		var at := -1
		for k in range(out.size()):
			if out[k][0] == t[0]:
				at = k
		if at >= 0:
			out[at] = t
		else:
			out.append(t)
	return out


func _panel_infos(fc: Array) -> Array:
	## Per telegraphed raid: {known, done, roster, clean}.
	var out: Array = []
	var ahead_first := model.raid_index
	var fut: Array = fc
	if phase == Phase.AFTER or phase == Phase.RECORD or phase == Phase.PLAY:
		ahead_first = model.raid_index + 1
		var n_ahead: int = model.state.intel_ahead()
		if phase == Phase.PLAY:
			n_ahead = (row["before"] as H7State).intel_ahead() - 1
		fut = H7Campaign.forecast(model.leg(), ahead_first, model.state, [], [], model.active_crew(), n_ahead) if (ahead_first < model.leg().size() and not model.breached and n_ahead > 0) else []
	for j in range(H7Data.RAIDS_PER_LEG):
		if j < model.history.size():
			var cur_play := phase == Phase.PLAY and j == model.history.size() - 1
			out.append({"known": true, "done": not cur_play, "roster": _uniq(model.history[j]["roster"]), "clean": model.history[j]["r"].clean})
		elif j >= ahead_first and j - ahead_first < fut.size():
			out.append({"known": true, "done": false, "roster": _uniq(fut[j - ahead_first]["roster"]), "clean": false})
		else:
			out.append({"known": false, "done": false, "roster": [], "clean": false})
	return out


func _draw_raid_panels(fc: Array) -> void:
	var infos := _panel_infos(fc)
	for j in range(3):
		var x := 300.0 + j * 220.0
		var info: Dictionary = infos[j]
		var current := j == model.raid_index and phase in [Phase.LEG, Phase.VISIT, Phase.PLAY]
		var edge := G.CELL if current else (G.THREAT if info["known"] else G.PANEL_EDGE)
		if info["done"]:
			edge = Color8(60, 70, 110)
		G.panel(self, Rect2(x, 12, 200, 92), edge, G.PANEL, 3.0 if current else 2.0)
		G.text(self, Vector2(x + 8, 14), "RAID %d" % (j + 1), 11, G.DIM)
		G.flame(self, Vector2(x + 14, 42), 7)
		G.text(self, Vector2(x + 26, 31), str(H7Data.HEATS[j]), 15, G.HEAT)
		G.netrun_hex(self, Vector2(x + 76, 42), 8)
		G.text(self, Vector2(x + 88, 31), str(H7Data.NETRUNS[j]), 15)
		if info["done"]:
			if info["clean"]:
				G.check(self, Vector2(x + 180, 24), 7)
			else:
				G.text(self, Vector2(x + 140, 14), "HELD", 11, G.HOLD)
		if not info["known"]:
			G.eye(self, Vector2(x + 100, 74), 12, G.DIM)
			G.line(self, Vector2(x + 84, 88), Vector2(x + 116, 60), G.DIM, 3.0)
			continue
		var roster: Array = info["roster"]
		for k in range(mini(roster.size(), 6)):
			var t: Array = roster[k]
			var cx := x + 22.0 + k * 30.0
			G.threat(self, String(t[0]).split("#")[0], Vector2(cx, 66), 10, -1, String(t[0]).contains("#"))
			if not (t[2] as Array).is_empty():
				G.trait_glyph(self, Vector2(cx - 6, 92), t[2][0], 4.0)
		if infos[j]["known"] and not info["done"]:
			_add_hit(Rect2(x, 12, 200, 92), "noop")


func _draw_left() -> void:
	G.strongbox(self, Vector2(48, 150), 16)
	var bank: int = model.state.bank if phase != Phase.PLAY else model.history.back()["before"].bank
	if phase == Phase.VISIT:
		bank = model.free_bank()
	G.text(self, Vector2(74, 130), str(bank), 34)
	G.text(self, Vector2(20, 100), "BANK", 12, G.DIM)
	if phase == Phase.VISIT and model.pending_cost() > 0:
		G.text(self, Vector2(20, 180), "%d - %d spent" % [model.state.bank, model.pending_cost()], 13, G.DIM)
	if phase == Phase.LEG:
		G.text(self, Vector2(20, 212), "LEG", 12, G.DIM)
		for k in range(model.legs.size()):
			var r := Rect2(20 + (k % 3) * 82, 232 + (k / 3) * 56, 74, 46)
			var on := k == model.leg_index
			G.panel(self, r, G.CELL if on else G.PANEL_EDGE, Color8(60, 52, 24) if on or _hot(r) else G.PANEL, 3.0 if on else 2.0)
			G.text_c(self, r.get_center(), str(k + 1), 22, G.CELL if on else G.INK)
			_add_hit(r, "leg:%d" % k)
	else:
		G.text(self, Vector2(20, 212), "LEG %d" % (model.leg_index + 1), 14, G.DIM)
		for j in range(3):
			if j < model.history.size():
				G.check(self, Vector2(34 + j * 40, 252), 8, G.CLEAN) if model.history[j]["r"].clean else G.cross(self, Vector2(34 + j * 40, 252), 7, G.DMG)
			else:
				G.circle(self, Vector2(34 + j * 40, 252), 8, G.PANEL_EDGE)


func _fort_of(n: String, fort: Dictionary) -> Array:
	return fort.get(n, [])


func _draw_map(r: H7Result, fort: Dictionary, st: H7State, tags: bool, hp_view: Dictionary = {}, cond_view: Dictionary = {}, show_routes: bool = true, route_alpha: float = 1.0) -> void:
	var lost: Array = st.lost
	# links
	for l in H7Data.LINKS:
		var corp: bool = String(l[0]).begins_with("C") or String(l[1]).begins_with("C")
		var col := Color8(40, 50, 90) if corp else G.CELL_DIM
		G.line(self, _np(l[0]), _np(l[1]), col, 4.0)
	for f in r.frozen:
		var a := _np(f[0])
		var b := _np(f[1])
		G.line(self, a, b, G.THREAT, 6.0)
		var m := a.lerp(b, 0.5)
		draw_rect(Rect2(m.x - 11, m.y - 7, 22, 18), G.BG)
		draw_rect(Rect2(m.x - 11, m.y - 7, 22, 18), G.THREAT, false, 2.0)
		draw_arc(m + Vector2(0, -7), 6, PI, TAU, 10, G.THREAT, 3.0, true)
	# corp sites
	for cid in ["C1", "C2"]:
		var cp := _np(cid)
		G.hexagon(self, cp, 25, Color8(24, 36, 100), G.THREAT, 3.0)
		G.shield(self, cp + Vector2(0, -2), 10)
		G.text(self, cp + Vector2(-44, 30), NODE_NAME[cid], 11, G.THREAT_LIGHT, HORIZONTAL_ALIGNMENT_CENTER, 88)
	# routes
	if show_routes:
		var k := 0
		for tid in r.routes:
			var route: Array = r.routes[tid]
			if route.size() < 2:
				continue
			var off := Vector2(0, (k % 3 - 1) * 5.0)
			var pts := PackedVector2Array()
			for n in route:
				pts.append(_np(n) + off)
			var col2 := Color(G.THREAT_LIGHT, 0.85 * route_alpha)
			draw_polyline(pts, col2, 3.0, true)
			var dir := (pts[pts.size() - 1] - pts[pts.size() - 2]).normalized()
			var tip := pts[pts.size() - 1] - dir * (NODE_R + 3.0)
			G.arrow(self, tip - dir * 18.0, tip, col2, 3.0, 11.0)
			k += 1
	# nodes
	var pend := {}
	if phase == Phase.VISIT:
		for p in model.places:
			pend[p] = pend.get(p, 0) + 1
	for n in H7Data.NODES:
		var c := _np(n)
		var is_lost := lost.has(n)
		var cond: String = cond_view.get(n, "ok")
		var col3 := G.CELL
		if is_lost or cond == "taken":
			col3 = G.DOWN_GREY
		elif cond == "down":
			col3 = G.DOWN_GREY
		draw_circle(c, NODE_R, G.BG2)
		G.circle(self, c, NODE_R, G.DMG if (is_lost or cond == "taken") else col3, 3.0)
		G.node_icon(self, n, c, 12, col3)
		if is_lost or cond == "taken":
			G.cross(self, c, 14, G.DMG, 3.0)
		if phase == Phase.VISIT:
			_add_hit(Rect2(c - Vector2(NODE_R + 6, NODE_R + 6), Vector2((NODE_R + 6) * 2, (NODE_R + 6) * 2)), "node:" + n)
			if (sel_piece != "" or sel_crew) and not is_lost:
				G.circle(self, c, NODE_R + 6, Color(G.CELL, 0.45 + 0.3 * sin(Time.get_ticks_msec() / 200.0)), 2.0)
		# hp bar
		var mx: int = H7Data.NODE_HP[n]
		var hpv: int = hp_view.get(n, mx)
		var bw := 44.0 if n != "HOME" else 56.0
		draw_rect(Rect2(c.x - bw / 2, c.y + NODE_R + 4, bw, 5), Color8(40, 70, 70))
		if not is_lost:
			draw_rect(Rect2(c.x - bw / 2, c.y + NODE_R + 4, bw * float(hpv) / mx, 5), G.CLEAN)
		G.text(self, c + Vector2(-50, NODE_R + 11), NODE_NAME[n], 11, G.INK, HORIZONTAL_ALIGNMENT_CENTER, 100)
		# jobs
		_job_chip(n, c, st)
		# pieces
		var pcs: Array = _fort_of(n, fort)
		var np: int = pend.get(n, 0)
		for k in range(pcs.size()):
			var a := PI + 0.1 + k * 0.62
			var pp := c + Vector2(cos(a), sin(a)) * (NODE_R + 17)
			var fresh: bool = k >= pcs.size() - np
			draw_circle(pp, 11, G.BG)
			G.circle(self, pp, 11, G.CELL if fresh else G.DIM, 2.0)
			G.piece(self, pcs[k], pp, 5.5, G.CELL if fresh else G.INK)
		# crew
		var crew_here: bool = (model.active_crew() == n and phase in [Phase.LEG, Phase.VISIT]) or (phase in [Phase.PLAY, Phase.AFTER, Phase.RECORD] and not row.is_empty() and row["crew"] == n)
		if crew_here:
			draw_circle(c + Vector2(NODE_R + 6, 14), 11, G.BG)
			G.circle(self, c + Vector2(NODE_R + 6, 14), 11, G.CELL, 2.0)
			G.person(self, c + Vector2(NODE_R + 6, 14), 7, G.CELL)
		# outcome tag
		if tags and not r.nodes.is_empty() and phase != Phase.LEG:
			_node_tag(n, c, r, is_lost)
		elif is_lost:
			_tag(c, "TAKEN", G.DMG)


func _tag(c: Vector2, label: String, col: Color) -> void:
	var w := G.font.get_string_size(label, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x + 12
	var p := c + Vector2(-w / 2, NODE_R + 25)
	draw_rect(Rect2(p, Vector2(w, 17)), G.BG2)
	draw_rect(Rect2(p, Vector2(w, 17)), col, false, 1.5)
	G.text(self, p + Vector2(6, 2), label, 12, col)


func _node_tag(n: String, c: Vector2, r: H7Result, is_lost: bool) -> void:
	if is_lost:
		_tag(c, "TAKEN", G.DMG)
		return
	var v: Dictionary = r.nodes[n]
	match v["outcome"]:
		"holds":
			_tag(c, "HOLDS", G.DIM)
		"scuffed":
			_tag(c, "SCUFFED -%d" % (v["before"] - v["after"]), G.DIM if r.clean else G.HOLD)
		"down":
			_tag(c, "DOWN", G.DMG)
		"taken":
			_tag(c, "TAKEN", G.DMG)
		"breached":
			_tag(c, "BREACHED", G.BREACH)


func _job_chip(n: String, c: Vector2, st: H7State) -> void:
	var lost_job := st.lost.has(n)
	var col := G.DOWN_GREY if lost_job else G.CELL
	var p := c + Vector2(NODE_R - 2, -NODE_R - 14)
	match n:
		"VAULT":
			G.panel(self, Rect2(p, Vector2(44, 18)), col, G.BG2, 1.5)
			G.coin(self, p + Vector2(11, 9), 5, col)
			G.text(self, p + Vector2(21, 2), "+%d" % H7Data.VAULT_INC, 12, col)
		"RELAY":
			G.panel(self, Rect2(p, Vector2(44, 18)), col, G.BG2, 1.5)
			G.netrun_hex(self, p + Vector2(11, 9), 5, col)
			G.text(self, p + Vector2(21, 2), "+%d" % H7Data.RELAY_INC, 12, col)
		"PROXY":
			G.panel(self, Rect2(p, Vector2(30, 18)), col, G.BG2, 1.5)
			G.eye(self, p + Vector2(15, 9), 5, col)
		"SAFE":
			G.panel(self, Rect2(p, Vector2(30, 18)), col, G.BG2, 1.5)
			G.person(self, p + Vector2(15, 9), 5, col)
		"FW":
			G.panel(self, Rect2(p, Vector2(30, 18)), col, G.BG2, 1.5)
			G.piece(self, "TURRET", p + Vector2(15, 9), 5, col)


# ---------- phases ----------
func _draw_leg_right() -> void:
	G.panel(self, Rect2(956, 112, 312, 330))
	G.text(self, Vector2(970, 120), "ONE LEG, 3 RAIDS", 16, G.CELL)
	var lines := ["Each visit: buy up to 2 pieces,", "place them on held nodes, station", "the crew (while the SAFEHOUSE holds).",
		"", "Raids are telegraphed: Heat, netruns,", "threats and traits. The PROXY shows", "two raids ahead, else one.", "",
		"Jobs: VAULT +3, RELAY +2 income.", "A TAKEN node stays lost for the leg", "and becomes a corp foothold.", "",
		"Clean raid: scuffs heal free."]
	for k in range(lines.size()):
		G.text(self, Vector2(970, 148 + k * 20), lines[k], 14, G.INK)
	_btn(Rect2(1010, 640, 258, 50), "ENTER VISIT 1", "enter")
	_draw_shop(false)


func _draw_shop(active: bool) -> void:
	G.panel(self, Rect2(20, 516, 930, 180), G.CELL if active else G.PANEL_EDGE, G.PANEL, 3.0 if active else 2.0)
	G.text(self, Vector2(34, 524), "SHOP", 13, G.DIM)
	# crew token
	var cr := Rect2(34, 600, 92, 82)
	G.panel(self, cr, G.CELL if sel_crew else G.PANEL_EDGE, Color8(60, 52, 24) if sel_crew else G.BG2, 3.0 if sel_crew else 2.0)
	G.person(self, cr.position + Vector2(46, 30), 14, G.CELL if model.crew_free() else G.DOWN_GREY)
	var cn := "-" if model.active_crew() == "" else String(NODE_NAME[model.active_crew()]).split(" ")[0]
	G.text_c(self, cr.position + Vector2(46, 56), "CREW +2", 12, G.INK)
	G.text_c(self, cr.position + Vector2(46, 71), cn, 11, G.DIM)
	if active:
		_add_hit(cr, "crewtok")
	for k in range(5):
		var pid: String = H7Data.PIECES[k]
		var r := Rect2(150 + k * 156, 540, 146, 144)
		var sel := sel_piece == pid
		var can := model.can_buy(pid)
		G.panel(self, r, G.CELL if sel else G.PANEL_EDGE, Color8(60, 52, 24) if sel else G.BG2, 3.0 if sel else 2.0)
		var col := G.CELL if sel else (G.INK if can or not active else G.DOWN_GREY)
		G.piece(self, pid, r.position + Vector2(73, 40), 17, col)
		G.text_c(self, r.position + Vector2(73, 76), PIECE_NAME[pid], 15, col)
		G.coin(self, r.position + Vector2(48, 108), 9, col)
		G.text(self, r.position + Vector2(62, 96), str(H7Data.COST[pid]), 24, col)
		var cnt := 0
		for b in model.buys:
			if b == pid:
				cnt += 1
		if cnt > 0:
			G.text(self, r.position + Vector2(10, 6), "x%d" % cnt, 14, G.CELL)
		if active:
			_add_hit(r, "piece:" + pid)
	if active:
		G.text(self, Vector2(34, 546), "Click a piece,", 12, G.DIM)
		G.text(self, Vector2(34, 562), "then a held node.", 12, G.DIM)


func _draw_visit(fc: Array) -> void:
	_draw_shop(true)
	# forecast cards
	G.text(self, Vector2(956, 108), "FORECAST: this fortress, no more buys", 13, G.CELL)
	for j in range(3):
		var y := 128.0 + j * 104.0
		var card := Rect2(956, y, 312, 96)
		if model.raid_index + j >= H7Data.RAIDS_PER_LEG:
			continue
		if j >= fc.size():
			G.panel(self, card, G.PANEL_EDGE, G.BG2, 1.5)
			G.text(self, card.position + Vector2(10, 6), "RAID %d" % (model.raid_index + j + 1), 14, G.DIM)
			G.eye(self, card.position + Vector2(156, 54), 13, G.DIM)
			G.line(self, card.position + Vector2(138, 70), card.position + Vector2(174, 36), G.DIM, 3.0)
			continue
		var f: Dictionary = fc[j]
		var r: H7Result = f["r"]
		var first := j == 0
		G.panel(self, card, G.CELL if first else G.PANEL_EDGE, Color8(50, 46, 30) if first else G.BG2, 3.0 if first else 1.5)
		var ri := model.raid_index + j
		G.text(self, card.position + Vector2(10, 6), "RAID %d" % (ri + 1), 14, G.CELL if first else G.DIM)
		G.flame(self, card.position + Vector2(86, 17), 6)
		G.text(self, card.position + Vector2(96, 7), str(H7Data.HEATS[ri]), 14, G.HEAT)
		# clean / stamp
		if r.breached:
			G.text(self, card.position + Vector2(160, 6), "BREACH", 14, G.BREACH)
		elif r.clean:
			G.check(self, card.position + Vector2(180, 17), 7)
			G.text(self, card.position + Vector2(192, 7), "CLEAN", 14, G.CLEAN)
		else:
			G.text(self, card.position + Vector2(160, 7), "HELD, patch", 14, G.HOLD)
		# lost nodes
		var lostn: Array = []
		for k in r.nodes:
			if r.nodes[k]["outcome"] in ["down", "taken"] and k != "HOME" and not fc[j]["before"].lost.has(k):
				lostn.append(k)
		G.text(self, card.position + Vector2(10, 32), "LOST", 11, G.DIM)
		if lostn.is_empty():
			G.text(self, card.position + Vector2(48, 30), "none", 14, G.DIM)
		for k in range(lostn.size()):
			var cc := card.position + Vector2(58 + k * 28, 40)
			G.circle(self, cc, 11, G.DMG, 2.0)
			G.node_icon(self, lostn[k], cc, 6, G.DMG)
		G.signed_coin(self, card.position + Vector2(10, 58), f["settle"].net, 22)
		G.text(self, card.position + Vector2(110, 58), "NET", 11, G.DIM)
		G.strongbox(self, card.position + Vector2(200, 72), 10)
		G.text(self, card.position + Vector2(220, 58), str(f["settle"].state.bank if not r.breached else 0), 24)
		G.text(self, card.position + Vector2(220, 40), "BANK AFTER", 10, G.DIM)
	# adaptation chips
	var cy := 442.0
	for j in range(mini(fc.size(), 2)):
		var f2: Dictionary = fc[j]
		var top := H7Campaign.invested((f2["before"] as H7State).fort)
		if top == "":
			continue
		_adapt_chip(956, cy, top, f2["roster"], model.raid_index + j + 1)
		cy += 56.0
	var has_buys := not model.buys.is_empty()
	_btn(Rect2(956, 640, 92, 50), "UNDO", "undo", has_buys, 16)
	_btn(Rect2(1060, 640, 208, 50), "START RAID", "start")


func _adapt_chip(x: float, y: float, top: String, roster: Array, raid_no: int) -> void:
	G.panel(self, Rect2(x, y, 312, 50), G.THREAT, G.PANEL, 2.0)
	var tough: Array = []
	for t in roster:
		if not (t[2] as Array).is_empty():
			tough = t
	if tough.is_empty():
		return
	G.text(self, Vector2(x + 8, y + 3), "CORP ADAPTS, RAID %d" % raid_no, 10, G.THREAT_LIGHT)
	G.piece(self, top, Vector2(x + 26, y + 33), 9, G.INK)
	G.arrow(self, Vector2(x + 46, y + 33), Vector2(x + 82, y + 33), G.THREAT, 3.0, 9.0)
	G.threat(self, String(tough[0]).split("#")[0], Vector2(x + 106, y + 33), 11)
	G.trait_glyph(self, Vector2(x + 146, y + 33), tough[2][0], 8.0)
	G.text(self, Vector2(x + 190, y + 24), String(tough[2][0]), 13, G.THREAT_LIGHT)


# ---------- playout ----------
func _play_state() -> Dictionary:
	## The drawn state at beat play_t: positions, threat info, node hp/cond, shots shown.
	var r: H7Result = row["r"]
	var b := int(play_t)
	var s := clampi(b / 2, 0, r.steps.size() - 1)
	var sub := b % 2
	var frac: float = play_t - floor(play_t)
	var ev: Dictionary = r.steps[s]
	var prev_threats := {}
	var prev_hp: Dictionary = H7Data.NODE_HP.duplicate()
	var prev_cond := {}
	for k in H7Data.NODE_HP:
		prev_cond[k] = "taken" if (row["before"] as H7State).lost.has(k) else "ok"
	if s > 0:
		prev_threats = r.steps[s - 1]["threats"]
		prev_hp = r.steps[s - 1]["hp"]
		prev_cond = r.steps[s - 1]["cond"]
	var out := {"s": s, "sub": sub, "frac": frac, "ev": ev, "prev": prev_threats, "hp": prev_hp, "cond": prev_cond}
	if sub == 1:
		out["hp"] = ev["hp"]
		out["cond"] = ev["cond"]
	return out


func _draw_play() -> void:
	var r: H7Result = row["r"]
	var ps := _play_state()
	var ev: Dictionary = ps["ev"]
	_draw_map(r, row["fort"], row["before"], false, ps["hp"], ps["cond"], true, 0.35)
	var fighters: Array = _uniq(row["roster"])
	var ids: Array = fighters.map(func(t: Array) -> String: return t[0])
	var n := ids.size()
	var pos := {}
	var entry := {}
	for t in fighters:
		entry[t[0]] = t[1]
	for k in range(n):
		var tid: String = ids[k]
		var from_site: String = ps["prev"][tid][0] if ps["prev"].has(tid) else entry[tid]
		var info: Array = ev["threats"][tid]
		var to_site: String = info[0]
		var was_alive: bool = (ps["prev"][tid][2] if ps["prev"].has(tid) else true)
		if not was_alive:
			continue
		var rows_n := (n + 1) / 2
		var off := Vector2(52 + (k % 2) * 28, 8 + ((k / 2) - (rows_n - 1) / 2.0) * 26.0)
		var p0 := _np(from_site) + off
		var p1 := _np(to_site) + off
		var p := p0
		if ps["sub"] == 0:
			p = p0.lerp(p1, ease(clampf(ps["frac"] * 1.4, 0.0, 1.0), -2.0))
		else:
			p = p1
		pos[tid] = p
		var dead := false
		for kk in ev["kills"]:
			if kk[0] == tid:
				dead = true
		var spent: bool = not info[2] and not dead
		if ps["sub"] == 0 or not spent:
			G.threat(self, String(tid).split("#")[0], p, 11, info[1] if ps["sub"] == 1 else (ps["prev"][tid][1] if ps["prev"].has(tid) else H7Data.THREAT_DEF[String(tid).split("#")[0]][0]), String(tid).contains("#"))
			var tr: Array = []
			for t in fighters:
				if t[0] == tid:
					tr = t[2]
			if not tr.is_empty():
				G.trait_glyph(self, p + Vector2(-8, -24), tr[0], 4.0)
			if info[3] > 0 and ps["sub"] == 1:
				G.piece(self, "ICE", p + Vector2(18, -14), 5, G.THREAT_LIGHT)
		elif spent and ps["sub"] == 1 and ps["frac"] < 0.6:
			G.threat(self, String(tid).split("#")[0], p, 11, 0)
			G.text(self, p + Vector2(-20, 16), "SPENT", 10, G.DIM)
		if dead and ps["sub"] == 1:
			G.pencil_x(self, p, 13)
	if ps["sub"] == 1:
		var shots: Array = ev["shots"]
		var show := mini(shots.size(), int(ps["frac"] * (shots.size() + 1)) + 1)
		for k in range(show):
			var sh: Array = shots[k]
			if not pos.has(sh[2]):
				continue
			var a := _np(sh[0])
			var b: Vector2 = pos[sh[2]]
			G.line(self, a, b, G.CELL, 4.0)
			var perp := (b - a).orthogonal().normalized() * ((k % 3) - 1) * 16.0
			var m := a.lerp(b, 0.5) + perp
			draw_circle(m, 10, G.CELL)
			G.text_c(self, m, str(k + 1), 13, G.BG)
			G.text(self, b + Vector2(16, -34 + (k % 3) * 17), "-%d" % sh[3] if sh[3] > 0 else "BLOCKED", 16 if sh[3] > 0 else 12, G.CELL)
		for h in ev["hits"]:
			var hp_: Vector2 = _np(h[1])
			G.text(self, hp_ + Vector2(-34, -NODE_R - 30), "-%d" % h[2], 18, G.DMG)
	# right column: beat controls + log
	G.panel(self, Rect2(956, 112, 312, 380))
	G.text(self, Vector2(970, 120), "RAID %d  step %d/%d" % [model.raid_index + 1, ps["s"] + 1, r.steps.size()], 16, G.CELL)
	var lines := _step_lines(r, ps["s"], ps["sub"])
	for k in range(mini(lines.size(), 16)):
		G.text(self, Vector2(970, 150 + k * 20), lines[k], 13, G.INK)
	for k in range(3):
		var rr := Rect2(956 + k * 60, 640, 54, 50)
		G.panel(self, rr, G.CELL if k == speed_i else G.PANEL_EDGE, Color8(60, 52, 24) if k == speed_i else G.PANEL, 3.0 if k == speed_i else 2.0)
		G.text_c(self, rr.get_center(), "%dx" % int(SPEEDS[k]), 18, G.CELL if k == speed_i else G.INK)
		_add_hit(rr, "speed:%d" % k)
	_btn(Rect2(1140, 640, 128, 50), "SKIP", "skip")


func _step_lines(r: H7Result, s: int, sub: int) -> Array:
	var out: Array = []
	var ev: Dictionary = r.steps[s]
	if sub == 0:
		for m in ev["moves"]:
			out.append("%s moves %s > %s" % [String(m[0]).split("#")[0], m[1], m[2]])
		for h in ev["holds"]:
			out.append("%s held (ICE)" % String(h[0]).split("#")[0])
		if out.is_empty():
			out.append("no movement")
	else:
		var k := 1
		for sh in ev["shots"]:
			out.append("%d. %s at %s: %s" % [k, sh[1], String(sh[2]).split("#")[0], ("-%d" % sh[3]) if sh[3] > 0 else "BLOCKED"])
			k += 1
		for h in ev["hits"]:
			out.append("%s strikes %s -%d" % [String(h[0]).split("#")[0], h[1], h[2]])
		for kk in ev["kills"]:
			out.append("%s destroyed" % String(kk[0]).split("#")[0])
		for d in ev["down"]:
			out.append("%s DOWN" % d)
		for t in ev["taken"]:
			out.append("%s TAKEN" % t)
	return out


# ---------- aftermath ----------
func _draw_after() -> void:
	var r: H7Result = row["r"]
	var s: H7Settle = row["settle"]
	var stamp := "BREACHED" if r.breached else ("CLEAN" if r.clean else "HOLDS")
	var scol := G.BREACH if r.breached else (G.CLEAN if r.clean else G.HOLD)
	G.panel(self, Rect2(956, 112, 312, 520))
	var sr := Rect2(976, 126, 272, 64)
	draw_rect(sr, Color(scol, 0.12))
	draw_rect(sr, scol, false, 4.0)
	G.text_c(self, sr.get_center(), stamp, 38, scol)
	# net box
	var y := 204.0
	G.text(self, Vector2(970, y), "NET", 12, G.DIM)
	y += 18
	G.text(self, Vector2(970, y), "salvage  +%d x %d kills" % [H7Data.SALVAGE, s.kills], 14)
	G.text(self, Vector2(1190, y), "+%d" % (H7Data.SALVAGE * s.kills), 14, G.INK, HORIZONTAL_ALIGNMENT_RIGHT, 66)
	y += 22
	G.text(self, Vector2(970, y), "clean bonus", 14)
	G.text(self, Vector2(1190, y), "+%d" % (H7Data.BONUS if r.clean else 0), 14, G.INK, HORIZONTAL_ALIGNMENT_RIGHT, 66)
	y += 22
	G.text(self, Vector2(970, y), "patch (repairs)", 14)
	G.text(self, Vector2(1190, y), "-%d" % s.bill, 14, G.DMG if s.bill > 0 else G.DIM, HORIZONTAL_ALIGNMENT_RIGHT, 66)
	y += 24
	draw_line(Vector2(970, y), Vector2(1254, y), G.DIM, 2.0)
	y += 6
	G.text(self, Vector2(970, y + 4), "= NET", 14, G.DIM)
	G.signed_coin(self, Vector2(1150, y), s.net, 26)
	# income by job
	y += 46
	G.text(self, Vector2(970, y), "INCOME BY JOB", 12, G.DIM)
	y += 20
	var st: H7State = s.state
	var show_inc := not r.breached and s.income > 0
	G.netrun_hex(self, Vector2(982, y + 10), 9)
	G.text(self, Vector2(996, y), "+%d" % H7Data.BASE_INCOME if show_inc else "+0", 18)
	for j in range(2):
		var jn: String = ["VAULT", "RELAY"][j]
		var val: int = [H7Data.VAULT_INC, H7Data.RELAY_INC][j]
		var is_lost := st.lost.has(jn)
		var cx := 1050.0 + j * 66
		G.node_icon(self, jn, Vector2(cx, y + 10), 9, G.DOWN_GREY if is_lost else G.CELL)
		G.text(self, Vector2(cx + 14, y), "+%d" % (0 if (is_lost or not show_inc) else val), 18, G.DIM if is_lost else G.INK)
	G.text(self, Vector2(1186, y), "= +%d" % (s.income if show_inc else 0), 18, G.CELL)
	if r.breached:
		G.text(self, Vector2(970, y + 26), "Home server breached: the leg ends.", 13, G.BREACH)
	elif model.raid_index >= model.leg().size() - 1:
		G.text(self, Vector2(970, y + 26), "Last raid of the leg: no further income.", 13, G.DIM)
	# bank arithmetic
	y += 58
	G.text(self, Vector2(970, y), "BANK", 12, G.DIM)
	y += 18
	var before: H7State = row["before"]
	G.text(self, Vector2(970, y), "%d - %d spent %s %d net + %d income" % [before.bank, s.spend, "+" if s.net >= 0 else "-", absi(s.net), s.income if show_inc else 0], 13)
	G.strongbox(self, Vector2(990, y + 36), 12)
	G.text(self, Vector2(1014, y + 20), "= %d" % (0 if r.breached else st.bank), 30)
	# survivors / lost
	y += 70
	if not st.surv.is_empty() and not model.leg_over():
		G.text(self, Vector2(970, y), "SURVIVORS REJOIN THE NEXT RAID", 11, G.THREAT_LIGHT)
		for k in range(st.surv.size()):
			G.threat(self, String(st.surv[k][0]).split("#")[0], Vector2(990 + k * 32, y + 28), 11, -1, true)
		y += 50
	var lost_now: Array = []
	for k in st.lost:
		if not (before.lost.has(k)):
			lost_now.append(k)
	if not lost_now.is_empty():
		G.text(self, Vector2(970, y), "TAKEN: %s (now a corp foothold)" % ", ".join(lost_now), 12, G.DMG)
	if model.leg_over():
		_btn(Rect2(1010, 640, 258, 50), "LEG RECORD", "next")
	else:
		_btn(Rect2(1010, 640, 258, 50), "NEXT VISIT", "next")
	# bottom-left summary
	G.panel(self, Rect2(20, 516, 930, 180))
	G.text(self, Vector2(34, 524), "RAID %d RESULT" % (model.raid_index + 1), 13, G.DIM)
	var kills: Array = r.kill_ids()
	var klist := []
	for k in kills:
		klist.append(String(k).split("#")[0])
	G.text(self, Vector2(34, 552), "Destroyed: %s" % (", ".join(klist) if not klist.is_empty() else "none"), 18)
	var outs := []
	for k in r.nodes:
		var v: Dictionary = r.nodes[k]
		outs.append("%s %s" % [k, String(v["outcome"]).to_upper() if v["outcome"] != "scuffed" else "SCUFFED -%d" % (v["before"] - v["after"])])
	G.text(self, Vector2(34, 582), "Nodes: " + "   ".join(outs), 15, G.INK, HORIZONTAL_ALIGNMENT_LEFT, 890)
	G.text(self, Vector2(34, 612), "Steps: %d     Crew: %s" % [r.steps.size(), row["crew"] if row["crew"] != "" else "none"], 15, G.DIM)
	if r.clean:
		G.text(self, Vector2(34, 642), "CLEAN: scuffs heal for free, so a clean raid never nets negative.", 15, G.CLEAN)


# ---------- record ----------
func _draw_record() -> void:
	var line: Array = model.bank_line
	G.panel(self, Rect2(300, 130, 640, 360))
	G.text(self, Vector2(316, 138), "BANK LINE", 14, G.DIM)
	var lo := 0
	var hi := 10
	for v in line:
		hi = maxi(hi, v)
	var area := Rect2(350, 180, 560, 270)
	for k in range(5):
		var yy := area.position.y + area.size.y * k / 4.0
		draw_line(Vector2(area.position.x, yy), Vector2(area.end.x, yy), Color8(40, 46, 80), 1.0)
		G.text(self, Vector2(310, yy - 8), str(int(hi - (hi - lo) * k / 4.0)), 12, G.DIM)
	var pts := PackedVector2Array()
	for k in range(line.size()):
		var px := area.position.x + area.size.x * (k / float(maxi(1, H7Data.RAIDS_PER_LEG)))
		var vv: int = maxi(line[k], lo)
		pts.append(Vector2(px, area.end.y - area.size.y * float(vv - lo) / float(hi - lo)))
	if pts.size() >= 2:
		draw_polyline(pts, G.CELL, 4.0, true)
	for k in range(pts.size()):
		draw_circle(pts[k], 7, G.CELL)
		G.text_c(self, pts[k] + Vector2(0, -20), "BREACH" if line[k] <= H7Data.BREACH_SCORE else str(line[k]), 18)
		G.text_c(self, Vector2(pts[k].x, area.end.y + 18), "START" if k == 0 else "RAID %d" % k, 12, G.DIM)
	# per-raid table
	G.panel(self, Rect2(300, 500, 640, 190))
	G.text(self, Vector2(316, 508), "RAID", 12, G.DIM)
	G.text(self, Vector2(400, 508), "RESULT", 12, G.DIM)
	G.text(self, Vector2(560, 508), "NET", 12, G.DIM)
	G.text(self, Vector2(660, 508), "BANK", 12, G.DIM)
	G.text(self, Vector2(760, 508), "LOST / BOUGHT", 12, G.DIM)
	for j in range(model.history.size()):
		var h: Dictionary = model.history[j]
		var hr: H7Result = h["r"]
		var yy2 := 534.0 + j * 46.0
		G.text(self, Vector2(316, yy2), str(j + 1), 22)
		var res_txt := "BREACHED" if hr.breached else ("CLEAN" if hr.clean else "HOLDS")
		G.text(self, Vector2(400, yy2), res_txt, 20, G.BREACH if hr.breached else (G.CLEAN if hr.clean else G.HOLD))
		G.signed_coin(self, Vector2(556, yy2), h["settle"].net, 22)
		G.strongbox(self, Vector2(670, yy2 + 12), 9)
		G.text(self, Vector2(690, yy2), "BREACH" if h["settle"].state.bank <= H7Data.BREACH_SCORE else str(h["settle"].state.bank), 22)
		var bought: Array = h["buy"]
		var lost_t := ""
		for k in h["settle"].state.lost:
			if not (h["before"] as H7State).lost.has(k):
				lost_t += " lost %s" % k
		G.text(self, Vector2(760, yy2 + 3), (", ".join(bought) if not bought.is_empty() else "no buys") + lost_t, 13, G.INK, HORIZONTAL_ALIGNMENT_LEFT, 170)
	# right: shields and final bank
	G.panel(self, Rect2(956, 112, 312, 380))
	G.text(self, Vector2(970, 120), "LEG %d RECORD" % (model.leg_index + 1), 18, G.CELL)
	G.text(self, Vector2(970, 160), "CLEAN SHIELDS", 12, G.DIM)
	for j in range(3):
		var c := Vector2(1000 + j * 70, 214)
		var done: bool = j < model.history.size()
		var clean: bool = done and model.history[j]["r"].clean
		G.shield(self, c, 24, G.CLEAN if clean else Color8(50, 56, 90))
		if clean:
			G.check(self, c + Vector2(0, -2), 11, G.BG)
		elif done:
			G.cross(self, c + Vector2(0, -2), 9, G.DMG)
	G.text(self, Vector2(970, 270), "%d of 3 clean" % model.clean_count(), 18)
	G.strongbox(self, Vector2(996, 342), 20)
	var fb: int = model.state.bank
	G.text(self, Vector2(1030, 318), "BREACHED" if model.breached else str(fb), 38 if not model.breached else 30, G.BREACH if model.breached else G.INK)
	G.text(self, Vector2(970, 400), "FINAL BANK" if not model.breached else "THE LEG ENDED AT %d" % H7Data.BREACH_SCORE, 12, G.DIM)
	for k in range(model.legs.size()):
		var r := Rect2(970 + k * 58, 430, 50, 40)
		G.panel(self, r, G.CELL if k == model.leg_index else G.PANEL_EDGE, G.BG2, 2.0)
		G.text_c(self, r.get_center(), str(k + 1), 18, G.CELL if k == model.leg_index else G.DIM)
	_btn(Rect2(1010, 640, 258, 50), "PLAY AGAIN", "restart")


# ---------- capture ----------
func _snap(name: String) -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png("%s/%s.png" % [capture_dir, name])
	print("shot ", name)


func _run_capture() -> void:
	DirAccess.make_dir_recursive_absolute(capture_dir)
	var gold := H7Data.load_json(H7Data.GOLDEN_PATH)
	var line: Array = gold["leg0"]["planned"]
	model.new_leg(cap_leg)
	var n := 0
	await _snap("%02d_leg" % n)
	n += 1
	_act("enter")
	for i in range(3):
		var x: Dictionary = line[i]
		var buy: Array = [] if cap_bare else x["buy"]
		var place: Array = [] if cap_bare else x["place"]
		model.station_crew("SAFE" if cap_bare else x["crew"])
		for k in range(buy.size()):
			model.buy_place(buy[k], place[k])
		await _snap("%02d_visit%d" % [n, i + 1])
		n += 1
		_act("start")
		var beats: Array = [0.5, 1.6, 3.6] if i == 0 else ([2.6] if i == 2 else [])
		for b in beats:
			play_t = b
			await _snap("%02d_raid%d_beat%d" % [n, i + 1, int(b)])
			n += 1
		_act("skip")
		await _snap("%02d_aftermath%d" % [n, i + 1])
		n += 1
		_act("next")
	await _snap("%02d_record" % n)
	get_tree().quit(0)
