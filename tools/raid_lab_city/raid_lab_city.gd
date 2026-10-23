extends Control
## Raid lab L8: the playable city raid (docs/handoff/raid_lab_l8/SPEC.md section 8). This is the root script of
## raid_lab_city.tscn, and everything is built in code. A 3D L8Board renders in a SubViewport behind a 2D overlay. The
## overlay holds the HUD, the 420 px right panel, the legend strip and the hint line.
## Every state change goes through L8Rules. The view only reads its results and turns traces into board cues.
## Flow per raid: CAPTURE, PLAN, FORECAST, the known beams, the REVEAL, the RESPONSE, then the sealed beam and the hunter,
## AFTERMATH, BETWEEN. RECORD follows raid 3 or a breach.
## Flags (after --): --leg=N (golden seeds 0 3 5 8), --auto=greedy|naive, --shots=<abs dir> (with --auto), --scramble.

enum Phase { CAPTURE, PLAN, FORECAST, PLAY, REVEAL, RESPONSE, AFTER, BETWEEN, RECORD }

const GOLDEN_PATH := "res://tools/raid_lab_city/data/l8_golden.json"
const VIEW := Vector2(1280.0, 720.0)
const PANEL_W := 420.0
const PANEL_X := 860.0
const PAD := 16.0
const HUD_H := 64.0
const LEGEND_Y := 672.0
const HINT_Y := 698.0
const PICK_R := 40.0
const HOME_CELL := Vector2i(-1, 1)
const HEAT_MAX := 100.0
const ROW_H := 38.0
const AUTO_WAIT := 0.6
const UNTIL_GUARD := 60000
const SCRAMBLE_SEED := 8808
const LINE_ID := {"beam1": 10, "extra1": 11, "extra2": 12, "sealed": 13, "hunter": 14}
const BEAM_NAME := {"beam1": "BEAM 1", "extra1": "EXTRA 1", "extra2": "EXTRA 2", "sealed": "SEALED", "hunter": "HUNTER"}
const CELL_ROW := ["NOR", "MID", "SOU"]
const INTEN_KEY := ["L", "N", "O"]

# Palette (matches l8_board.gd).
const BG := Color8(3, 5, 15)
const PANEL := Color8(9, 13, 30)
const PANEL_HI := Color8(42, 34, 16)
const EDGE := Color8(52, 62, 100)
const INK := Color8(228, 233, 248)
const DIM := Color8(130, 140, 168)
const AMBER := Color8(255, 176, 32)
const GOLD := Color8(255, 210, 77)
const COBALT := Color8(61, 107, 255)
const COBALT_HOT := Color8(159, 192, 255)
const ACID := Color8(212, 255, 0)
const RED := Color8(255, 61, 77)
const HEAT_COL := Color8(255, 122, 40)
const GREY := Color8(110, 116, 134)
const TYPE_COLOR := {"D": Color8(92, 225, 255), "N": Color8(255, 64, 214), "E": Color8(255, 140, 26)}
const TIER_COLOR := {"BREACHED": Color8(255, 61, 77), "DAMAGED": Color8(255, 110, 80), "BATTERED": Color8(255, 176, 32),
	"HOLDS": Color8(159, 192, 255), "EVADED": Color8(212, 255, 0)}
const TIER_TEXT := {"BREACHED": "HOME is at 0: the campaign is lost.", "DAMAGED": "HOME lost integrity this raid.",
	"EVADED": "Nothing was touched: Heat -10.", "BATTERED": "2+ districts went DOWN, or one was TAKEN.",
	"HOLDS": "The cell holds."}

# ---------------------------------------------------------------- state
var golden: Dictionary = {}
var leg_entry: Dictionary = {}
var leg: Dictionary = {}
var leg_seed: int = 0
var load_error: String = ""
var board: L8Board
var ui: Control
var font: Font

var phase: int = Phase.CAPTURE
var st: Dictionary = {}
var raid: int = 0
var breached: bool = false
var history: Array = []
var cap_opts: Array = []
var cap_cell: Variant = null
var place: Dictionary = {"sentries": {}, "ghost": null}
var undo: Array = []
var tool: String = ""
var fc: Array = []
var rd: Dictionary = {}
var real: int = 0
var before: Dictionary = {}
var heat_launch: int = 0
var mid: Dictionary = {}
var known_tr: Array = []
var stage: String = ""
var resp_opts: Array = []
var redeploy_from: Variant = null
var resp_scroll: int = 0
var resp_hover: int = -1
var result: Dictionary = {}
var b_repair: Variant = null
var b_build: Variant = null
var b_inten: String = "NORMAL"
var build_armed: bool = false

var busy: bool = false
var speed: float = 1.0
var instant: bool = false
var hud_hp: int = 3
var status_msg: String = ""
var mouse := Vector2(-100.0, -100.0)
var hits: Array = []

var auto_line: String = ""
var shots_dir: String = ""
var shot_n: int = 0
var scramble: bool = false


# ---------------------------------------------------------------- setup
func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	font = ThemeDB.fallback_font
	_parse_args()
	# A fixed 1280x720 board render: with stretch on, a HiDPI window doubles the SubViewport and the board is cropped.
	var svc := SubViewportContainer.new()
	svc.stretch = false
	svc.position = Vector2.ZERO
	svc.size = VIEW
	svc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(svc)
	var sv := SubViewport.new()
	sv.size = Vector2i(int(VIEW.x), int(VIEW.y))
	sv.own_world_3d = true
	sv.transparent_bg = false
	sv.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	svc.add_child(sv)
	board = L8Board.new()
	sv.add_child(board)
	ui = Control.new()
	ui.set_anchors_preset(Control.PRESET_FULL_RECT)
	ui.size = VIEW
	ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(ui)
	ui.draw.connect(_draw_ui)
	if not _load_golden():
		return
	_start_leg()
	if auto_line != "":
		_run_auto.call_deferred()


func _parse_args() -> void:
	for a: String in OS.get_cmdline_user_args():
		if a.begins_with("--leg="):
			leg_seed = int(a.substr(6))
		elif a.begins_with("--auto="):
			auto_line = a.substr(7)
		elif a.begins_with("--shots="):
			shots_dir = a.substr(8)
		elif a == "--scramble":
			scramble = true
	if shots_dir != "" and auto_line == "":
		auto_line = "greedy"
	if auto_line != "" and auto_line != "greedy" and auto_line != "naive":
		push_error("raid_lab_city: unknown --auto=%s, using greedy" % auto_line)
		auto_line = "greedy"


func _load_golden() -> bool:
	var txt := FileAccess.get_file_as_string(GOLDEN_PATH)
	var parsed: Variant = JSON.parse_string(txt)
	if typeof(parsed) != TYPE_DICTIONARY:
		load_error = "Cannot read %s" % GOLDEN_PATH
		push_error(load_error)
		return false
	golden = parsed
	var legs: Array = golden.get("legs", [])
	if legs.is_empty():
		load_error = "The golden has no legs."
		return false
	for e: Variant in legs:
		var d: Dictionary = e
		if int(d["seed"]) == leg_seed:
			leg_entry = d
	if leg_entry.is_empty():
		push_error("raid_lab_city: leg %d is not in the golden, using the first" % leg_seed)
		leg_entry = legs[0]
		leg_seed = int(leg_entry["seed"])
	leg = L8Rules.leg_from_json(leg_entry["leg"])
	return true


func _start_leg() -> void:
	st = L8Rules.initial(leg)
	raid = 0
	breached = false
	history = []
	result = {}
	hud_hp = int(st["home_hp"])
	board.setup({"w": L8Rules.W, "h": L8Rules.H, "values": leg["values"], "exploits": leg["exploits"]})
	board.show_state(st, _empty_place())
	_enter_capture()


func _process(_delta: float) -> void:
	ui.queue_redraw()


# ---------------------------------------------------------------- small helpers
func _none(v: Variant) -> bool:
	return typeof(v) == TYPE_NIL


func _is_home(v: Variant) -> bool:
	return typeof(v) == TYPE_STRING and String(v) == L8Rules.HOME


func _empty_place() -> Dictionary:
	return {"sentries": {}, "ghost": null}


func _cell_name(c: Variant) -> String:
	if typeof(c) != TYPE_VECTOR2I:
		return str(c)
	var v: Vector2i = c
	return "%s %d" % [CELL_ROW[v.y], v.x]


func _line_name(ln: Dictionary) -> String:
	if String(ln["kind"]) == "ROUTE":
		return "%s route to HOME" % L8Rules.ROUTE_NAMES[int(ln["index"])]
	var cs: Array = ln["cells"]
	var first: Vector2i = cs[0]
	return "street %d %s" % [int(ln["index"]), "down" if first.y == 0 else "up"]


func _tname(t: String) -> String:
	return String(L8Rules.TYPE_NAMES.get(t, t))


func _num(f: float) -> String:
	if absf(f - roundf(f)) < 0.001:
		return "%d" % int(roundf(f))
	return "%.1f" % f


func _score_text(s: Dictionary) -> String:
	if int(s["home_hp"]) <= 0:
		return "campaign lost"
	return _num(L8Rules.score(leg, s))


func _status_of(s: Dictionary, c: Variant) -> String:
	return String((s["owned"] as Dictionary).get(c, "NEUTRAL"))


## A short reading of touches: "2 hit, 1 block, HOME -1" or "untouched".
func _sum(touches: Array) -> String:
	var hit := 0
	var blk := 0
	var home := 0
	for e: Array in touches:
		var k := String(e[1])
		if k == "hit":
			hit += 1
		elif k == "block":
			blk += 1
		elif k == "home":
			home += 1
	if hit + blk + home == 0:
		return "untouched"
	var parts := PackedStringArray()
	if hit > 0:
		parts.append("%d hit" % hit)
	if blk > 0:
		parts.append("%d block%s" % [blk, "" if blk == 1 else "s"])
	if home > 0:
		parts.append("HOME -%d" % home)
	return ", ".join(parts)


func _resp_label(r: Array, sentries: Dictionary) -> String:
	if r.is_empty():
		return "?"
	var head := String(r[0])
	if head == "HOLD":
		return "HOLD"
	if head == "JAM":
		return "JAM the hunter"
	var t := String(sentries.get(r[1], "?"))
	return "MOVE %s %s > %s" % [_tname(t), _cell_name(r[1]), _cell_name(r[2])]


func _placed(t: String) -> int:
	var n := 0
	var sd: Dictionary = place.get("sentries", {})
	for c: Variant in sd:
		if String(sd[c]) == t:
			n += 1
	return n


func _screen(c: Variant) -> Vector2:
	if typeof(c) == TYPE_VECTOR2I:
		var v: Vector2i = c
		return board.cell_screen_pos(v)
	return board.cell_screen_pos(HOME_CELL)


## The nearest cell (or HOME) within PICK_R px of pos, else null.
func _pick(pos: Vector2, with_home: bool) -> Variant:
	var best: Variant = null
	var bd := PICK_R
	for c: Vector2i in L8Rules.CELLS:
		var d := board.cell_screen_pos(c).distance_to(pos)
		if d < bd:
			bd = d
			best = c
	if with_home and board.cell_screen_pos(HOME_CELL).distance_to(pos) < bd:
		best = L8Rules.HOME
	return best


# ---------------------------------------------------------------- scramble and text
func _scr(text: String) -> String:
	if not scramble:
		return text
	var out := ""
	var word := ""
	for i in range(text.length()):
		var ch := text[i]
		if _is_letter(ch):
			word += ch
		else:
			out += _noise(word) + ch
			word = ""
	return out + _noise(word)


func _is_letter(ch: String) -> bool:
	var u := ch.unicode_at(0)
	return (u >= 65 and u <= 90) or (u >= 97 and u <= 122)


func _noise(word: String) -> String:
	if word == "":
		return ""
	var s: int = (word.hash() ^ SCRAMBLE_SEED) & 0x7fffffff
	var out := ""
	for i in range(word.length()):
		s = (s * 1103515245 + 12345) & 0x7fffffff
		var ch := String.chr(97 + (s >> 16) % 26)
		out += ch.to_upper() if word[i] == word[i].to_upper() else ch
	return out


func _t(p: Vector2, text: String, size: int = 14, col: Color = INK) -> void:
	ui.draw_string(font, p + Vector2(0.0, font.get_ascent(size)), _scr(text), HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _tw(text: String, size: int) -> float:
	return font.get_string_size(_scr(text), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


func _tc(center: Vector2, text: String, size: int = 14, col: Color = INK) -> void:
	_t(center - Vector2(_tw(text, size) * 0.5, font.get_height(size) * 0.5), text, size, col)


func _tr(p: Vector2, text: String, size: int = 14, col: Color = INK) -> void:
	_t(Vector2(p.x - _tw(text, size), p.y), text, size, col)


func _box(r: Rect2, edge: Color, fill: Color, w: float = 2.0) -> void:
	ui.draw_rect(r, fill)
	ui.draw_rect(r, edge, false, w)


func _btn(r: Rect2, label: String, id: String, on: bool = true, sel: bool = false, size: int = 14) -> void:
	var hot := on and r.has_point(mouse)
	_box(r, (AMBER if sel else (INK if hot else EDGE)) if on else EDGE.darkened(0.4), PANEL_HI if (sel or hot) else PANEL)
	_tc(r.get_center(), label, size, INK if on else DIM)
	if on:
		hits.append({"rect": r, "id": id})


func _head(title: String, todo: String) -> float:
	var x := PANEL_X + PAD
	_t(Vector2(x, HUD_H + 10.0), title, 20, AMBER)
	_t(Vector2(x, HUD_H + 38.0), todo, 13, INK)
	return HUD_H + 64.0


# ---------------------------------------------------------------- glyphs
## The type's shape: D triangle, N square, E circle.
func _glyph(c: Vector2, t: String, r: float, col: Color) -> void:
	match t:
		"D":
			ui.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -r), c + Vector2(r * 0.9, r * 0.65),
				c + Vector2(-r * 0.9, r * 0.65)]), col)
		"N":
			ui.draw_rect(Rect2(c - Vector2(r, r) * 0.75, Vector2(r, r) * 1.5), col)
		_:
			ui.draw_circle(c, r * 0.8, col)


func _ghost_icon(c: Vector2, r: float, col: Color) -> void:
	for k in range(8):
		var a := TAU * float(k) / 8.0
		ui.draw_arc(c, r, a, a + TAU / 16.0, 4, col, 2.0)


func _sentry_icon(c: Vector2, t: String) -> void:
	var col: Color = TYPE_COLOR.get(t, GREY)
	ui.draw_rect(Rect2(c + Vector2(-5.0, 6.0), Vector2(10.0, 3.0)), GREY)
	ui.draw_line(c + Vector2(0.0, 6.0), c + Vector2(0.0, -3.0), GREY, 2.0)
	_glyph(c + Vector2(0.0, -7.0), t, 5.0, col)


func _down_icon(c: Vector2) -> void:
	ui.draw_circle(c, 8.0, GREY.darkened(0.4))
	ui.draw_line(c + Vector2(-4.0, 4.0), c + Vector2(4.0, -4.0), INK, 2.5)
	ui.draw_arc(c + Vector2(4.0, -4.0), 2.5, 0.0, TAU, 8, INK, 1.5)


func _taken_icon(c: Vector2) -> void:
	ui.draw_rect(Rect2(c - Vector2(7.0, 7.0), Vector2(14.0, 14.0)), COBALT)
	ui.draw_rect(Rect2(c - Vector2(7.0, 7.0), Vector2(14.0, 14.0)), COBALT_HOT, false, 1.5)


func _key_icon(c: Vector2, col: Color) -> void:
	ui.draw_arc(c + Vector2(-5.0, 0.0), 3.5, 0.0, TAU, 12, col, 2.0)
	ui.draw_line(c + Vector2(-1.5, 0.0), c + Vector2(8.0, 0.0), col, 2.0)
	ui.draw_line(c + Vector2(6.0, 0.0), c + Vector2(6.0, 4.0), col, 2.0)
	ui.draw_line(c + Vector2(3.0, 0.0), c + Vector2(3.0, 3.0), col, 2.0)


func _hound_icon(c: Vector2) -> void:
	ui.draw_rect(Rect2(c + Vector2(-7.0, -3.0), Vector2(11.0, 5.0)), COBALT_HOT)
	ui.draw_rect(Rect2(c + Vector2(3.0, -7.0), Vector2(6.0, 5.0)), COBALT_HOT)
	for lx: float in [-6.0, -3.0, 0.0, 3.0]:
		ui.draw_line(c + Vector2(lx, 2.0), c + Vector2(lx, 7.0), COBALT_HOT, 1.5)


# ---------------------------------------------------------------- input
func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		mouse = (event as InputEventMouseMotion).position
	elif event is InputEventMouseButton and event.pressed:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP:
			resp_scroll = maxi(0, resp_scroll - 1)
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			resp_scroll += 1
		elif mb.button_index == MOUSE_BUTTON_LEFT:
			_click(mb.position)
	elif event is InputEventKey and event.pressed and not event.echo:
		_key((event as InputEventKey).keycode)


func _click(pos: Vector2) -> void:
	for k in range(hits.size() - 1, -1, -1):
		if (hits[k]["rect"] as Rect2).has_point(pos):
			var id := String(hits[k]["id"])
			if auto_line != "" and not (id.begins_with("speed:") or id == "instant"):
				return
			status_msg = ""
			_act(id)
			return
	if auto_line != "" or busy:
		return
	if pos.x >= PANEL_X or pos.y < HUD_H or pos.y > LEGEND_Y:
		return
	status_msg = ""
	match phase:
		Phase.CAPTURE:
			var c: Variant = _pick(pos, false)
			if not _none(c):
				_do_capture(c)
		Phase.PLAN, Phase.FORECAST:
			var c: Variant = _pick(pos, true)
			if not _none(c):
				_plan_click(c)
		Phase.RESPONSE:
			_response_click(_pick(pos, false))
		Phase.BETWEEN:
			var c: Variant = _pick(pos, false)
			if not _none(c):
				_between_click(c)


func _key(code: int) -> void:
	if code == KEY_I:
		_toggle_instant()
		return
	if busy or phase == Phase.PLAY or phase == Phase.REVEAL:
		match code:
			KEY_1:
				_set_speed(1.0)
			KEY_2:
				_set_speed(2.0)
			KEY_4:
				_set_speed(4.0)
		return
	if auto_line != "":
		return
	status_msg = ""
	var enter := code == KEY_ENTER or code == KEY_KP_ENTER
	match phase:
		Phase.PLAN, Phase.FORECAST:
			match code:
				KEY_1:
					_set_tool("D")
				KEY_2:
					_set_tool("N")
				KEY_3:
					_set_tool("E")
				KEY_G:
					_set_tool("G")
				KEY_Z, KEY_BACKSPACE:
					_undo()
				KEY_ESCAPE:
					tool = ""
					_highlight_tool()
				KEY_B:
					_back_to_plan()
			if enter:
				_next()
		Phase.RESPONSE:
			match code:
				KEY_H:
					_respond(["HOLD"])
				KEY_J:
					if _has_jam():
						_respond(["JAM"])
					else:
						status_msg = "No spoof left: JAM is not available."
				KEY_ESCAPE:
					redeploy_from = null
					_highlight_sources()
		Phase.BETWEEN:
			match code:
				KEY_B:
					build_armed = true
					status_msg = "Build: press 1 (drone), 2 (netrunner), 3 (enforcer) or 0 (none)."
				KEY_1:
					_set_build("D")
				KEY_2:
					_set_build("N")
				KEY_3:
					_set_build("E")
				KEY_0:
					_set_build(null)
				KEY_L:
					_set_inten("LOW")
				KEY_N:
					_set_inten("NORMAL")
				KEY_O:
					_set_inten("HOT")
			if enter:
				_next()
		_:
			if enter:
				_next()


func _act(id: String) -> void:
	if id.begins_with("tool:"):
		_set_tool(id.substr(5))
	elif id == "undo":
		_undo()
	elif id == "next":
		_next()
	elif id == "back":
		_back_to_plan()
	elif id.begins_with("cap:"):
		var i := int(id.substr(4))
		if i >= 0 and i < cap_opts.size():
			_do_capture(cap_opts[i])
	elif id.begins_with("resp:"):
		var i := int(id.substr(5))
		if i >= 0 and i < resp_opts.size():
			_respond(resp_opts[i]["response"])
	elif id.begins_with("build:"):
		var t := id.substr(6)
		if t == "none":
			_set_build(null)
		else:
			_set_build(t)
	elif id.begins_with("inten:"):
		_set_inten(id.substr(6))
	elif id.begins_with("speed:"):
		_set_speed(float(id.substr(6)))
	elif id == "instant":
		_toggle_instant()


func _next() -> void:
	if busy:
		return
	match phase:
		Phase.PLAN:
			_enter_forecast()
		Phase.FORECAST:
			_launch()
		Phase.AFTER:
			if breached or raid >= L8Rules.RAIDS - 1:
				_enter_record()
			else:
				_enter_between()
		Phase.BETWEEN:
			_confirm_between()
		Phase.RECORD:
			if shots_dir == "":
				_start_leg()


func _set_speed(s: float) -> void:
	speed = s
	board.set_speed(s)


func _toggle_instant() -> void:
	instant = not instant
	board.set_instant(instant)


# ---------------------------------------------------------------- CAPTURE
func _enter_capture() -> void:
	board.reset_playout()
	board.clear_paths()
	cap_opts = L8Rules.capture_options(leg, st)
	cap_cell = null
	board.show_state(st, {"sentries": st["sentries"], "ghost": null})
	if cap_opts.is_empty():
		status_msg = "No district can be captured: the raid goes on."
		_enter_plan()
		return
	phase = Phase.CAPTURE
	board.highlight(cap_opts, GOLD)


func _do_capture(c: Variant) -> void:
	if phase != Phase.CAPTURE:
		return
	if typeof(c) != TYPE_VECTOR2I or not cap_opts.has(c):
		status_msg = "Pick a glowing district: next to one of yours, or in column 0."
		return
	st = L8Rules.capture(leg, st, c)
	cap_cell = c
	_enter_plan()


func _draw_capture() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("CAPTURE  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Claim one glowing district (it stands in for a netrun).")
	_t(Vector2(x, y), "Next to one of your districts, or in column 0 by HOME.", 12, DIM)
	y += 26.0
	var vals: Dictionary = leg["values"]
	var ex: Array = leg["exploits"]
	for i in range(cap_opts.size()):
		var c: Vector2i = cap_opts[i]
		var r := Rect2(x, y, w, 30.0)
		var hot := r.has_point(mouse)
		_box(r, AMBER if hot else EDGE, PANEL_HI if hot else PANEL)
		_t(r.position + Vector2(10.0, 7.0), _cell_name(c), 14, INK)
		_t(r.position + Vector2(130.0, 7.0), "value %d" % int(vals[c]), 14, AMBER)
		if ex.has(c):
			_key_icon(r.position + Vector2(260.0, 15.0), ACID)
			_t(r.position + Vector2(276.0, 7.0), "EXPLOIT", 13, ACID)
		hits.append({"rect": r, "id": "cap:%d" % i})
		y += 34.0
	y += 8.0
	_draw_kit(y, false)
	for cv: Variant in cap_opts:
		var c: Vector2i = cv
		var p := _screen(c)
		_tc(p + Vector2(0.0, -50.0), str(int(vals[c])), 16, AMBER)
		if ex.has(c):
			_tc(p + Vector2(0.0, -32.0), "KEY", 12, ACID)


## The sentry pool and the kit. In PLAN it shows placed/pool per type.
func _draw_kit(y: float, planning: bool) -> float:
	var x := PANEL_X + PAD
	var pool: Dictionary = st["pool"]
	var kit: Dictionary = st["kit"]
	_t(Vector2(x, y), "SENTRIES", 12, DIM)
	for i in range(3):
		var t: String = L8Rules.TYPES[i]
		var gx := x + 100.0 + i * 96.0
		_glyph(Vector2(gx, y + 8.0), t, 8.0, TYPE_COLOR[t])
		var s := ("%d/%d placed" % [_placed(t), int(pool[t])]) if planning else ("x%d" % int(pool[t]))
		_t(Vector2(gx + 12.0, y), s, 12, INK)
	y += 22.0
	_t(Vector2(x, y), "KIT", 12, DIM)
	_ghost_icon(Vector2(x + 108.0, y + 8.0), 7.0, GOLD)
	_t(Vector2(x + 120.0, y), "GHOST %d" % int(kit["ghost"]), 13, GOLD)
	_t(Vector2(x + 220.0, y), "SPOOF %d" % int(kit["spoof"]), 13, ACID)
	return y + 26.0


# ---------------------------------------------------------------- PLAN
func _enter_plan() -> void:
	var sd := {}
	var prev: Dictionary = st["sentries"]
	var pool: Dictionary = st["pool"]
	var counts := {"D": 0, "N": 0, "E": 0}
	for c: Vector2i in L8Rules.sorted_cells(prev):
		var t := String(prev[c])
		if L8Rules.is_live(st, c) and counts.has(t) and int(counts[t]) < int(pool[t]):
			sd[c] = t
			counts[t] = int(counts[t]) + 1
	place = {"sentries": sd, "ghost": null}
	_show_plan_paths()
	undo = []
	tool = ""
	fc = []
	phase = Phase.PLAN
	board.clear_highlight()
	board.show_state(st, place)


func _set_tool(t: String, toggle: bool = true) -> void:
	if phase == Phase.FORECAST:
		_back_to_plan()
	if phase != Phase.PLAN:
		return
	if t == "G" and int(st["kit"]["ghost"]) <= 0:
		status_msg = "No ghost left in the kit."
		return
	tool = "" if (toggle and tool == t) else t
	_highlight_tool()


func _highlight_tool() -> void:
	if tool == "":
		board.clear_highlight()
		return
	var cells := L8Rules.live_cells(st)
	if tool == "G":
		cells.append(L8Rules.HOME)
		board.highlight(cells, GOLD)
	else:
		board.highlight(cells, TYPE_COLOR[tool])


func _push() -> void:
	undo.append({"sentries": (place["sentries"] as Dictionary).duplicate(), "ghost": place["ghost"]})


func _undo() -> void:
	if phase == Phase.FORECAST:
		_back_to_plan()
	if phase != Phase.PLAN:
		return
	if undo.is_empty():
		status_msg = "Nothing to undo."
		return
	place = undo.pop_back()
	board.show_state(st, place)


func _back_to_plan() -> void:
	if phase == Phase.FORECAST:
		phase = Phase.PLAN
		fc = []


func _plan_click(c: Variant) -> void:
	if phase == Phase.FORECAST:
		_back_to_plan()
	if phase != Phase.PLAN or _none(c):
		return
	var sd: Dictionary = place["sentries"]
	var home := _is_home(c)
	if tool == "G":
		if not home and not L8Rules.is_live(st, c):
			status_msg = "The ghost goes on HOME or on one of your live districts."
			return
		if L8Rules._same(place["ghost"], c):
			_push()
			place["ghost"] = null
		elif int(st["kit"]["ghost"]) <= 0:
			status_msg = "No ghost left in the kit."
			return
		else:
			_push()
			place["ghost"] = c
	elif tool != "":
		if home or not L8Rules.is_live(st, c):
			status_msg = "Sentries go on your own districts (not TAKEN)."
			return
		var cur := String(sd.get(c, ""))
		var pool := int(st["pool"][tool])
		_push()
		if cur == tool:
			sd.erase(c)
		else:
			if _placed(tool) >= pool:
				for k: Vector2i in L8Rules.sorted_cells(sd):
					if String(sd[k]) == tool:
						sd.erase(k)
						break
			if _placed(tool) >= pool:
				undo.pop_back()
				status_msg = "No %s sentry in the pool." % _tname(tool)
				return
			sd[c] = tool
	else:
		if not home and sd.has(c):
			_push()
			sd.erase(c)
		elif L8Rules._same(place["ghost"], c):
			_push()
			place["ghost"] = null
		else:
			status_msg = "Pick a sentry (1 2 3) or the ghost (G) first."
			return
	board.show_state(st, place)


func _draw_plan() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("PLAN  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "1 2 3 a sentry, G the ghost, then click a district.")
	y = _draw_kit(y, true)
	var bw := (w - 24.0) / 4.0
	var tools: Array = ["D", "N", "E", "G"]
	for i in range(4):
		var t: String = tools[i]
		var r := Rect2(x + i * (bw + 8.0), y, bw, 44.0)
		var sel := tool == t
		var on := t != "G" or int(st["kit"]["ghost"]) > 0
		var hot := on and r.has_point(mouse)
		_box(r, AMBER if sel else (INK if hot else EDGE), PANEL_HI if (sel or hot) else PANEL)
		if t == "G":
			_ghost_icon(r.position + Vector2(16.0, 22.0), 8.0, GOLD if on else DIM)
			_t(r.position + Vector2(30.0, 6.0), "GHOST", 12, INK if on else DIM)
			_t(r.position + Vector2(30.0, 23.0), "[G] +%d H" % L8Rules.GHOST_HEAT, 11, DIM)
		else:
			_glyph(r.position + Vector2(16.0, 22.0), t, 9.0, TYPE_COLOR[t])
			_t(r.position + Vector2(30.0, 6.0), _tname(t).substr(0, 6), 12, INK)
			_t(r.position + Vector2(30.0, 23.0), "[%d] %d/%d" % [i + 1, _placed(t), int(st["pool"][t])], 11, DIM)
		if on:
			hits.append({"rect": r, "id": "tool:" + t})
	y += 54.0
	_t(Vector2(x, y), "A sentry blocks beams of its own type: the line stops there.", 12, DIM)
	y += 18.0
	_t(Vector2(x, y), "The ghost lets every beam pass its district (or HOME).", 12, DIM)
	y += 28.0
	y = _draw_beam_info(y)
	var err := L8Rules.check_place(st, place)
	if err != "":
		_t(Vector2(x, y + 6.0), "Placement: " + err, 12, RED)
	var by := LEGEND_Y - 58.0
	_btn(Rect2(x, by, 110.0, 42.0), "UNDO [Z]", "undo", not undo.is_empty())
	_btn(Rect2(x + 122.0, by, w - 122.0, 42.0), "FORECAST [Enter]", "next", err == "", false, 16)


## This raid's beams for the plan: beam 1, the extras the launch Heat brings, the sealed routes, the hunter.
func _draw_beam_info(y: float) -> float:
	var x := PANEL_X + PAD
	var r_now: Dictionary = leg["raids"][raid]
	var lh := L8Rules.launch_heat(st, place)
	var n := L8Rules.extra_count(lh)
	_t(Vector2(x, y), "THIS RAID  (launch Heat %d)" % lh, 12, DIM)
	y += 20.0
	y = _beam_row(y, "BEAM 1", r_now["b1"], true, "")
	y = _beam_row(y, "EXTRA 1", r_now["extra1"], n >= 1, "at Heat %d" % L8Rules.EXTRA_AT)
	y = _beam_row(y, "EXTRA 2", r_now["extra2"], n >= 2, "at Heat %d" % L8Rules.STRONG_AT)
	_t(Vector2(x, y), "SEALED", 13, INK)
	var cands: Array = r_now["cands"]
	for k in range(cands.size()):
		var t := String(cands[k]["type"])
		var gx := x + 84.0 + k * 102.0
		_glyph(Vector2(gx, y + 8.0), t, 7.0, TYPE_COLOR[t])
		_t(Vector2(gx + 10.0, y), L8Rules.ROUTE_NAMES[k], 12, INK)
	y += 18.0
	_t(Vector2(x + 84.0, y), "one of these three convoys comes", 11, DIM)
	y += 20.0
	var ht := String(r_now["hunter_type"])
	_hound_icon(Vector2(x + 6.0, y + 8.0))
	_t(Vector2(x + 18.0, y), "HUNTER", 13, COBALT_HOT)
	_glyph(Vector2(x + 92.0, y + 8.0), ht, 7.0, TYPE_COLOR[ht])
	_t(Vector2(x + 104.0, y), "%s: the street of the first touch" % _tname(ht), 12, INK)
	return y + 22.0


func _beam_row(y: float, label: String, ln: Dictionary, live: bool, note: String) -> float:
	var x := PANEL_X + PAD
	var t := String(ln["type"])
	var col := INK if live else DIM
	_t(Vector2(x, y), label, 13, col)
	_glyph(Vector2(x + 92.0, y + 8.0), t, 7.0, TYPE_COLOR[t] if live else DIM)
	_t(Vector2(x + 104.0, y), "%s, %s" % [_tname(t), _line_name(ln)], 12, col)
	if not live:
		_tr(Vector2(PANEL_X + PANEL_W - PAD, y), "off (%s)" % note, 11, DIM)
	return y + 20.0


# ---------------------------------------------------------------- FORECAST
## Draw this raid's known beams (the ones its launch Heat brings) and the three sealed candidates on the board.
func _show_plan_paths() -> void:
	var rd: Dictionary = leg["raids"][raid]
	var h := L8Rules.launch_heat(st, place)
	var lines: Array = [rd["b1"]]
	if h >= L8Rules.EXTRA_AT:
		lines.append(rd["extra1"])
	if h >= L8Rules.STRONG_AT:
		lines.append(rd["extra2"])
	lines.append_array(rd["cands"])
	board.show_paths(lines)


func _enter_forecast() -> void:
	if phase != Phase.PLAN:
		return
	var err := L8Rules.check_place(st, place)
	if err != "":
		status_msg = "Placement: " + err
		return
	fc = L8Rules.forecast(leg, raid, st, place)
	_show_plan_paths()
	tool = ""
	board.clear_highlight()
	phase = Phase.FORECAST


func _draw_forecast() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("FORECAST  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Each sealed route against this placement.")
	y = _draw_kit(y, true)
	var sd: Dictionary = place["sentries"]
	for fv: Variant in fc:
		var f: Dictionary = fv
		var k := int(f["cand"])
		var t := String(f["type"])
		var hold: Dictionary = f["hold"]
		var best: Dictionary = f["best"]
		var r := Rect2(x, y, w, 98.0)
		_box(r, EDGE, PANEL)
		_glyph(r.position + Vector2(16.0, 15.0), t, 9.0, TYPE_COLOR[t])
		_t(r.position + Vector2(32.0, 5.0), "%s ROUTE  %s" % [L8Rules.ROUTE_NAMES[k], _tname(t)], 14, INK)
		var yy := r.position.y + 28.0
		var ht := String(hold["tier"])
		var hs: Dictionary = hold["state"]
		_t(Vector2(x + 10.0, yy), "HOLD", 12, DIM)
		_t(Vector2(x + 64.0, yy), "%s   HOME %d/%d" % [_sum(hold["touches"]), int(hs["home_hp"]), L8Rules.HOME_HP], 12, INK)
		_tr(Vector2(r.end.x - 10.0, yy), ht, 13, TIER_COLOR.get(ht, INK))
		yy += 22.0
		var bt := String(best["tier"])
		var bs: Dictionary = best["state"]
		_t(Vector2(x + 10.0, yy), "BEST", 12, DIM)
		_t(Vector2(x + 64.0, yy), _resp_label(best["response"], sd), 12, ACID)
		yy += 20.0
		_t(Vector2(x + 64.0, yy), "%s   HOME %d/%d" % [_sum(best["touches"]), int(bs["home_hp"]), L8Rules.HOME_HP], 12, INK)
		_tr(Vector2(r.end.x - 10.0, yy), bt, 13, TIER_COLOR.get(bt, INK))
		y += 104.0
	var by := LEGEND_Y - 58.0
	_btn(Rect2(x, by, 110.0, 42.0), "BACK [B]", "back")
	_btn(Rect2(x + 122.0, by, w - 122.0, 42.0), "LAUNCH [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- LAUNCH and playout
func _cue(kind: String, c: Vector2i, t: String, line: int) -> Dictionary:
	return {"kind": kind, "cell": c, "type": t, "line": line}


func _trace_kind(tr: Array, beam: String, c: Variant) -> String:
	for e: Array in tr:
		if String(e[0]) == beam and typeof(e[1]) == typeof(c) and e[1] == c:
			return String(e[2])
	return ""


## One line's cues: a step per cell until a block, hit cues where the trace hits, a home cue when the trace says home.
func _line_cues(beam: String, ln: Dictionary, tr: Array) -> Array:
	var out: Array = []
	var t := String(ln["type"])
	var id: int = int(LINE_ID[beam])
	var stopped := false
	for cv: Variant in ln["cells"]:
		var c: Vector2i = cv
		var k := _trace_kind(tr, beam, c)
		if k == "block":
			out.append(_cue("block", c, t, id))
			stopped = true
			break
		out.append(_cue("hit" if k == "hit" else "beam_step", c, t, id))
	if not stopped and bool(ln["home"]) and _trace_kind(tr, beam, L8Rules.HOME) == "home":
		out.append(_cue("home", Vector2i(-1, int(ln["index"])), t, id))
	return out


func _known_cues(tr: Array) -> Array:
	var cues: Array = _line_cues("beam1", rd["b1"], tr)
	var n := L8Rules.extra_count(heat_launch)
	if n >= 1:
		cues.append_array(_line_cues("extra1", rd["extra1"], tr))
	if n >= 2:
		cues.append_array(_line_cues("extra2", rd["extra2"], tr))
	return cues


## Where the hunter turns: the first touch of the raid (any beam but the hunter, never HOME), else its own street's top.
func _turn_cell(tr: Array) -> Vector2i:
	for e: Array in tr:
		if String(e[0]) != "hunter" and typeof(e[1]) == TYPE_VECTOR2I:
			return e[1]
	return Vector2i(int(rd["hunter_street"]), 0)


func _late_cues(tr: Array, resp: Array) -> Array:
	var cues: Array = _line_cues("sealed", rd["cands"][real], tr)
	var ht := String(rd["hunter_type"])
	var turn := _turn_cell(tr)
	var hid: int = int(LINE_ID["hunter"])
	if String(resp[0]) == "JAM":
		cues.append(_cue("jam", turn, ht, hid))
	else:
		var hl: Variant = L8Rules.hunter_line(leg, raid, before, real, place, resp)
		if typeof(hl) == TYPE_DICTIONARY:
			cues.append(_cue("hunter_turn", turn, ht, hid))
			cues.append_array(_line_cues("hunter", hl, tr))
	if tr.is_empty():
		cues.append(_cue("evaded", Vector2i(1, 1), "D", -1))
	return cues


func _play_batch(cues: Array, label: String) -> void:
	busy = true
	board.set_instant(instant)
	await board.play(cues, speed)
	busy = false
	if shots_dir != "":
		await _shot(label)


func _cand_view() -> Array:
	var out: Array = []
	var cands: Array = rd["cands"]
	for k in range(cands.size()):
		out.append({"route": k, "type": String(cands[k]["type"])})
	return out


func _launch() -> void:
	if busy or phase != Phase.FORECAST:
		return
	var err := L8Rules.check_place(st, place)
	if err != "":
		status_msg = "Placement: " + err
		return
	before = L8Rules.copy_state(st)
	rd = leg["raids"][raid]
	real = int(rd["real"])
	heat_launch = L8Rules.launch_heat(st, place)
	hud_hp = int(st["home_hp"])
	var hold_tr := L8Rules.trace(leg, raid, st, real, place, ["HOLD"])
	known_tr = []
	for e: Array in hold_tr:
		if String(e[0]) in ["beam1", "extra1", "extra2"]:
			known_tr.append(e)
	board.clear_highlight()
	board.clear_paths()
	board.show_candidates(_cand_view(), -1)
	board.show_state(st, place)
	phase = Phase.PLAY
	stage = "known"
	await _play_batch(_known_cues(hold_tr), "r%d_known_beams" % (raid + 1))
	# The state after beam 1 and the extras, read from the rules' own sweep (the response is legal against it).
	var la: Dictionary = L8Rules._launch(leg, raid, st, place)
	var sw: Dictionary = la["sw"]
	mid = {"heat": heat_launch, "bank": int(st["bank"]), "home_hp": int(sw["hp"]),
		"owned": (sw["owned"] as Dictionary).duplicate(), "sentries": (sw["sent"] as Dictionary).duplicate()}
	hud_hp = int(mid["home_hp"])
	phase = Phase.REVEAL
	stage = "reveal"
	var sealed: Dictionary = rd["cands"][real]
	await _play_batch([_cue("reveal", Vector2i(L8Rules.W - 1, real), String(sealed["type"]), real)], "r%d_reveal" % (raid + 1))
	_enter_response()


func _beams_now() -> Array:
	var out: Array = ["beam1"]
	var n := L8Rules.extra_count(heat_launch)
	if n >= 1:
		out.append("extra1")
	if n >= 2:
		out.append("extra2")
	out.append("sealed")
	out.append("hunter")
	return out


func _beam_state(b: String) -> String:
	var known := b in ["beam1", "extra1", "extra2"]
	match stage:
		"known":
			return "now" if known else "later"
		"reveal":
			if known:
				return "done"
			return "now" if b == "sealed" else "later"
	return "done" if known else "now"


func _draw_play() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("LAUNCH  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "The raid runs. 1 2 4 set the speed, I toggles instant.")
	_t(Vector2(x, y), "Launch Heat %d: %d known beam%s" % [heat_launch, 1 + L8Rules.extra_count(heat_launch),
		"" if L8Rules.extra_count(heat_launch) == 0 else "s"], 12, HEAT_COL)
	y += 24.0
	for bv: Variant in _beams_now():
		var b: String = bv
		var s := _beam_state(b)
		var col := INK if s == "now" else (DIM if s == "done" else DIM.darkened(0.3))
		var r := Rect2(x, y, w, 30.0)
		_box(r, AMBER if s == "now" else EDGE, PANEL_HI if s == "now" else PANEL)
		_t(r.position + Vector2(10.0, 7.0), String(BEAM_NAME[b]), 13, col)
		var desc := ""
		var t := ""
		match b:
			"beam1", "extra1", "extra2":
				var ln: Dictionary = rd["b1" if b == "beam1" else b]
				t = String(ln["type"])
				desc = _line_name(ln)
			"sealed":
				if stage == "known":
					desc = "one of the three routes"
				else:
					var ln2: Dictionary = rd["cands"][real]
					t = String(ln2["type"])
					desc = _line_name(ln2)
			"hunter":
				t = String(rd["hunter_type"])
				desc = "the street of the first touch"
		if t != "":
			_glyph(r.position + Vector2(100.0, 15.0), t, 7.0, TYPE_COLOR[t])
		else:
			_t(r.position + Vector2(96.0, 7.0), "?", 13, COBALT_HOT)
		_t(r.position + Vector2(114.0, 7.0), desc, 12, col)
		_tr(Vector2(r.end.x - 8.0, r.position.y + 8.0), s.to_upper(), 11, AMBER if s == "now" else DIM)
		y += 34.0
	y += 6.0
	var labels: Array = [1.0, 2.0, 4.0]
	for i in range(3):
		var sp: float = labels[i]
		_btn(Rect2(x + i * 78.0, y, 70.0, 34.0), "%dx" % int(sp), "speed:%d" % int(sp), true, is_equal_approx(speed, sp))
	_btn(Rect2(x + 240.0, y, w - 240.0, 34.0), "INSTANT [I]", "instant", true, instant)
	y += 48.0
	if stage != "known":
		_t(Vector2(x, y), "THE KNOWN BEAMS TOUCHED", 12, DIM)
		y += 20.0
		y = _draw_touch_lines(known_tr, y)


## One line per beam of a trace: "BEAM 1: MID 0 hit, NOR 0 block". Returns the y after.
func _draw_touch_lines(tr: Array, y: float) -> float:
	var x := PANEL_X + PAD
	var any := false
	for bv: Variant in L8Rules.BEAMS:
		var b: String = bv
		var parts := PackedStringArray()
		for e: Array in tr:
			if String(e[0]) == b:
				parts.append("%s %s" % [_cell_name(e[1]), String(e[2])])
		if parts.is_empty():
			continue
		any = true
		_t(Vector2(x, y), "%s: %s" % [String(BEAM_NAME[b]), ", ".join(parts)], 12, INK)
		y += 18.0
	if not any:
		_t(Vector2(x, y), "Nothing touched.", 12, DIM)
		y += 18.0
	return y


# ---------------------------------------------------------------- RESPONSE
func _enter_response() -> void:
	resp_opts = []
	for rv: Variant in L8Rules.response_options(leg, raid, before, real, place):
		var r: Array = rv
		var res := L8Rules.resolve(leg, raid, before, real, place, r)
		if res.has("error"):
			continue
		var ns: Dictionary = res["state"]
		resp_opts.append({"response": r, "state": ns, "touches": res["touches"], "tier": L8Rules.tier(before, ns, res["touches"])})
	redeploy_from = null
	resp_scroll = 0
	phase = Phase.RESPONSE
	_highlight_sources()


func _has_jam() -> bool:
	for o: Dictionary in resp_opts:
		if String((o["response"] as Array)[0]) == "JAM":
			return true
	return false


func _highlight_sources() -> void:
	var cells: Array = []
	for o: Dictionary in resp_opts:
		var r: Array = o["response"]
		if String(r[0]) != "REDEPLOY":
			continue
		if _none(redeploy_from):
			if not cells.has(r[1]):
				cells.append(r[1])
		elif r[1] == redeploy_from and not cells.has(r[2]):
			cells.append(r[2])
	if cells.is_empty():
		board.clear_highlight()
	else:
		board.highlight(cells, ACID)


func _response_click(c: Variant) -> void:
	if phase != Phase.RESPONSE or busy or typeof(c) != TYPE_VECTOR2I:
		return
	var cell: Vector2i = c
	var sent: Dictionary = mid["sentries"]
	if _none(redeploy_from):
		if not sent.has(cell):
			status_msg = "Click one of your sentries to move it (or pick a row)."
		elif int(before["kit"]["spoof"]) <= 0:
			status_msg = "No spoof left: REDEPLOY is not available."
		else:
			redeploy_from = cell
			resp_scroll = 0
			_highlight_sources()
		return
	var from: Vector2i = redeploy_from
	if cell == from:
		redeploy_from = null
		_highlight_sources()
		return
	if sent.has(cell):
		redeploy_from = cell
		resp_scroll = 0
		_highlight_sources()
		return
	for o: Dictionary in resp_opts:
		var r: Array = o["response"]
		if String(r[0]) == "REDEPLOY" and r[1] == from and r[2] == cell:
			_respond(r)
			return
	status_msg = "Not a legal target: an owned, live district with no sentry."


func _respond(r: Array) -> void:
	if busy or phase != Phase.RESPONSE:
		return
	var resp := L8Rules.norm_response(r)
	if resp.is_empty():
		return
	var res := L8Rules.resolve(leg, raid, before, real, place, resp)
	if res.has("error"):
		status_msg = "Response: " + String(res["error"])
		return
	if String(resp[0]) == "REDEPLOY":
		var sent: Dictionary = (mid["sentries"] as Dictionary).duplicate()
		var t: Variant = sent[resp[1]]
		sent.erase(resp[1])
		sent[resp[2]] = t
		board.show_state(mid, {"sentries": sent, "ghost": place["ghost"]})
	board.clear_highlight()
	redeploy_from = null
	phase = Phase.PLAY
	stage = "late"
	var tr: Array = res["trace"]
	await _play_batch(_late_cues(tr, resp), "r%d_sealed_hunter" % (raid + 1))
	var ns: Dictionary = res["state"]
	result = {"state": ns, "touches": res["touches"], "trace": tr, "tier": L8Rules.tier(before, ns, res["touches"]),
		"response": resp}
	st = ns
	hud_hp = int(st["home_hp"])
	breached = int(st["home_hp"]) <= 0
	history.append({"raid": raid, "capture": cap_cell, "response": resp, "tier": result["tier"], "touches": res["touches"],
		"heat_launch": heat_launch, "heat_after": int(st["heat"]), "score": L8Rules.score(leg, st), "between": null,
		"sentries": (place["sentries"] as Dictionary).duplicate(), "ghost": place["ghost"]})
	board.show_state(st, {"sentries": st["sentries"], "ghost": null})
	phase = Phase.AFTER


func _draw_response() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("RESPONSE  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "H hold, J jam, a row, or a sentry then a cell.")
	var sealed: Dictionary = rd["cands"][real]
	var t := String(sealed["type"])
	_glyph(Vector2(x + 8.0, y + 9.0), t, 8.0, TYPE_COLOR[t])
	_t(Vector2(x + 22.0, y), "SEALED: %s ROUTE, %s" % [L8Rules.ROUTE_NAMES[real], _tname(t)], 14, INK)
	y += 22.0
	_t(Vector2(x, y), "Spoofs left %d. REDEPLOY or JAM costs 1 and +%d Heat." % [int(before["kit"]["spoof"]), L8Rules.SPOOF_HEAT], 12, DIM)
	y += 18.0
	_t(Vector2(x, y), "A REDEPLOY moves a sentry for the sealed beam and the hunter.", 12, DIM)
	y += 20.0
	if not _none(redeploy_from):
		var st_t := String((mid["sentries"] as Dictionary).get(redeploy_from, "?"))
		_t(Vector2(x, y), "Moves of the %s sentry on %s  (Esc: all rows)" % [_tname(st_t), _cell_name(redeploy_from)], 12, ACID)
		y += 20.0
	var view: Array = []
	for i in range(resp_opts.size()):
		var r: Array = resp_opts[i]["response"]
		if _none(redeploy_from) or String(r[0]) != "REDEPLOY" or r[1] == redeploy_from:
			view.append(i)
	var max_rows := maxi(1, int((LEGEND_Y - 22.0 - y) / ROW_H))
	resp_scroll = clampi(resp_scroll, 0, maxi(0, view.size() - max_rows))
	var sd: Dictionary = mid["sentries"]
	for j in range(resp_scroll, mini(view.size(), resp_scroll + max_rows)):
		var i: int = view[j]
		var o: Dictionary = resp_opts[i]
		var r: Array = o["response"]
		var ns: Dictionary = o["state"]
		var tier := String(o["tier"])
		var rr := Rect2(x, y, w, ROW_H - 4.0)
		var hot := rr.has_point(mouse)
		if hot:
			resp_hover = i
		_box(rr, ACID if hot else EDGE, PANEL_HI if hot else PANEL)
		var head := String(r[0])
		var key := " [H]" if head == "HOLD" else (" [J]" if head == "JAM" else "")
		_t(rr.position + Vector2(8.0, 3.0), _resp_label(r, sd) + key, 13, INK)
		_tr(Vector2(rr.end.x - 8.0, rr.position.y + 3.0), tier, 13, TIER_COLOR.get(tier, INK))
		_t(rr.position + Vector2(8.0, 19.0), "%s   HOME %d/%d   Heat %d" % [_sum(o["touches"]), int(ns["home_hp"]),
			L8Rules.HOME_HP, int(ns["heat"])], 11, DIM)
		hits.append({"rect": rr, "id": "resp:%d" % i})
		y += ROW_H
	if view.size() > max_rows:
		_tr(Vector2(PANEL_X + PANEL_W - PAD, LEGEND_Y - 18.0), "rows %d-%d of %d (wheel scrolls)" % [resp_scroll + 1,
			mini(view.size(), resp_scroll + max_rows), view.size()], 11, DIM)


# ---------------------------------------------------------------- AFTERMATH
func _draw_after() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var tier := String(result.get("tier", "HOLDS"))
	var y := _head("AFTERMATH  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Enter goes on.")
	_t(Vector2(x, y), tier, 34, TIER_COLOR.get(tier, INK))
	y += 46.0
	_t(Vector2(x, y), String(TIER_TEXT.get(tier, "")), 13, INK)
	y += 24.0
	_t(Vector2(x, y), "Response: %s" % _resp_label(result["response"], place["sentries"]), 13, ACID)
	y += 26.0
	_t(Vector2(x, y), "WHAT THE BEAMS TOUCHED", 12, DIM)
	y += 20.0
	y = _draw_touch_lines(result["trace"], y)
	y += 10.0
	var notes := PackedStringArray()
	if (result["trace"] as Array).is_empty():
		notes.append("evaded -%d" % L8Rules.EVADE_HEAT)
	if String((result["response"] as Array)[0]) != "HOLD":
		notes.append("spoof +%d" % L8Rules.SPOOF_HEAT)
	var note := "" if notes.is_empty() else "  (%s)" % ", ".join(notes)
	_t(Vector2(x, y), "Heat: launch %d -> %d%s" % [heat_launch, int(st["heat"]), note], 13, HEAT_COL)
	y += 22.0
	_t(Vector2(x, y), "HOME: %d -> %d" % [int(before["home_hp"]), int(st["home_hp"])], 13,
		RED if int(st["home_hp"]) < int(before["home_hp"]) else INK)
	y += 22.0
	var live := L8Rules.live_cells(st).size()
	_t(Vector2(x, y), "Districts held: %d    Score now: %s" % [live, _score_text(st)], 13, INK)
	y += 22.0
	var last := breached or raid >= L8Rules.RAIDS - 1
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "RECORD [Enter]" if last else "BETWEEN RAIDS [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- BETWEEN
func _enter_between() -> void:
	board.clear_paths()
	b_repair = null
	b_build = null
	b_inten = "NORMAL"
	build_armed = false
	phase = Phase.BETWEEN
	_highlight_down()


func _down_cells() -> Array:
	var out: Array = []
	for c: Vector2i in L8Rules.CELLS:
		if _status_of(st, c) == L8Rules.DOWN:
			out.append(c)
	return out


func _highlight_down() -> void:
	var cells := _down_cells()
	if cells.is_empty():
		board.clear_highlight()
	else:
		board.highlight(cells, AMBER)


func _bp(inten: String) -> Dictionary:
	return L8Rules.between_parts(leg, st, b_repair, b_build, inten)


func _between_click(c: Variant) -> void:
	if phase != Phase.BETWEEN or typeof(c) != TYPE_VECTOR2I:
		return
	if _status_of(st, c) != L8Rules.DOWN:
		status_msg = "Only a DOWN district can be repaired."
		return
	if L8Rules._same(b_repair, c):
		b_repair = null
		return
	var p := L8Rules.between_parts(leg, st, c, b_build, b_inten)
	if _none(p["repaired"]):
		status_msg = "Not enough bank to repair it (cost %d)." % L8Rules.repair_cost(leg, c)
		return
	b_repair = c
	if not _none(b_build) and _none(p["built"]):
		b_build = null
		status_msg = "The repair leaves too little for the build: the build is dropped."


func _set_build(t: Variant) -> void:
	if phase != Phase.BETWEEN:
		return
	build_armed = false
	if _none(t) or (not _none(b_build) and String(b_build) == String(t)):
		b_build = null
		return
	var p := L8Rules.between_parts(leg, st, b_repair, t, b_inten)
	if _none(p["built"]):
		status_msg = "Not enough bank to build (cost %d, after the repair)." % L8Rules.SENTRY_PRICE
		return
	b_build = String(t)


func _set_inten(name: String) -> void:
	if phase == Phase.BETWEEN and L8Rules.INTENSITY.has(name):
		b_inten = name


func _confirm_between() -> void:
	if phase != Phase.BETWEEN:
		return
	var parts := _bp(b_inten)
	if not history.is_empty():
		var row: Dictionary = history.back()
		row["between"] = {"repair": parts["repaired"], "build": parts["built"], "intensity": b_inten,
			"income": int(parts["income"]), "heat_add": int(parts["heat_add"])}
	st = L8Rules.between(leg, st, b_repair, b_build, b_inten)
	raid += 1
	hud_hp = int(st["home_hp"])
	board.clear_highlight()
	_enter_capture()


func _draw_between() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("BETWEEN RAIDS", "Repair, build, pick an intensity. Enter: next raid.")
	var parts := _bp(b_inten)
	_t(Vector2(x, y), "1  REPAIR ONE DISTRICT (click a DOWN one; cost value / 2)", 12, DIM)
	y += 20.0
	if _none(b_repair):
		_t(Vector2(x + 18.0, y), "none" if not _down_cells().is_empty() else "nothing is DOWN", 13, DIM)
	else:
		_t(Vector2(x + 18.0, y), "%s   -%d" % [_cell_name(b_repair), int(parts["repair_cost"])], 13, ACID)
	y += 28.0
	_t(Vector2(x, y), "2  BUILD ONE SENTRY (-%d)   [B then 1 2 3, 0 none]" % L8Rules.SENTRY_PRICE, 12, DIM)
	y += 20.0
	var bw := (w - 24.0) / 4.0
	var opts: Array = ["", "D", "N", "E"]
	for i in range(4):
		var t: String = opts[i]
		var r := Rect2(x + i * (bw + 8.0), y, bw, 40.0)
		var picked := (t == "" and _none(b_build)) or (t != "" and not _none(b_build) and String(b_build) == t)
		var ok := t == "" or not _none(L8Rules.between_parts(leg, st, b_repair, t, b_inten)["built"])
		var hot := ok and r.has_point(mouse)
		_box(r, AMBER if picked else (INK if hot else EDGE), PANEL_HI if (picked or hot) else PANEL)
		if t == "":
			_tc(r.get_center(), "NONE [0]", 12, INK)
		else:
			_glyph(r.position + Vector2(14.0, 20.0), t, 8.0, TYPE_COLOR[t] if ok else DIM)
			_t(r.position + Vector2(26.0, 4.0), _tname(t).substr(0, 6), 11, INK if ok else DIM)
			_t(r.position + Vector2(26.0, 21.0), "[%d] -%d" % [i, L8Rules.SENTRY_PRICE], 11, DIM)
		if ok:
			hits.append({"rect": r, "id": "build:" + ("none" if t == "" else t)})
	y += 50.0
	_t(Vector2(x, y), "3  RUN INTENSITY   [L N O]", 12, DIM)
	y += 20.0
	var cw := (w - 16.0) / 3.0
	for i in range(3):
		var nm: String = L8Rules.INTENSITY_ORDER[i]
		var cr := Rect2(x + i * (cw + 8.0), y, cw, 112.0)
		var sel := nm == b_inten
		var hot := cr.has_point(mouse)
		_box(cr, AMBER if sel else (INK if hot else EDGE), PANEL_HI if (sel or hot) else PANEL, 3.0 if sel else 2.0)
		hits.append({"rect": cr, "id": "inten:" + nm})
		var p := _bp(nm)
		var ns: Dictionary = p["state"]
		var k := L8Rules.extra_count(int(ns["heat"]))
		_t(cr.position + Vector2(8.0, 6.0), "%s [%s]" % [nm, INTEN_KEY[i]], 14, AMBER if sel else INK)
		_t(cr.position + Vector2(8.0, 30.0), "Heat +%d -> %d" % [int(p["heat_add"]), int(ns["heat"])], 12, HEAT_COL)
		_t(cr.position + Vector2(8.0, 49.0), "income +%d" % int(p["income"]), 12, GOLD)
		_t(cr.position + Vector2(8.0, 68.0), "bank -> %d" % int(ns["bank"]), 12, INK)
		_t(cr.position + Vector2(8.0, 87.0), "next: %d known beam%s" % [1 + k, "" if k == 0 else "s"], 11, RED if k > 0 else DIM)
	y += 124.0
	var ns2: Dictionary = parts["state"]
	_t(Vector2(x, y), "BANK %d - repair %d - build %d + income %d = %d" % [int(st["bank"]), int(parts["repair_cost"]),
		int(parts["build_cost"]), int(parts["income"]), int(ns2["bank"])], 13, INK)
	y += 20.0
	_t(Vector2(x, y), "HEAT %d + %d = %d" % [int(st["heat"]), int(parts["heat_add"]), int(ns2["heat"])], 13, HEAT_COL)
	y += 20.0
	_t(Vector2(x, y), "Score after this step: %s" % _score_text(ns2), 13, INK)
	y += 26.0
	_draw_kit(y, false)
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "NEXT RAID [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- RECORD
func _enter_record() -> void:
	phase = Phase.RECORD
	board.clear_highlight()


func _draw_record() -> void:
	ui.draw_rect(Rect2(0.0, HUD_H, PANEL_X, LEGEND_Y - HUD_H), Color(BG, 0.86))
	var x := 40.0
	var y := HUD_H + 20.0
	_t(Vector2(x, y), "LEG RECORD  (leg %d)" % leg_seed, 24, AMBER)
	y += 38.0
	if breached:
		_t(Vector2(x, y), "BREACHED in raid %d: the campaign is lost." % history.size(), 18, RED)
	else:
		_t(Vector2(x, y), "THE CELL SURVIVED THE LEG", 18, ACID)
	y += 40.0
	for hv: Variant in history:
		var h: Dictionary = hv
		var tier := String(h["tier"])
		var r := Rect2(x, y, 780.0, 74.0)
		_box(r, TIER_COLOR.get(tier, EDGE), PANEL)
		_t(r.position + Vector2(14.0, 8.0), "RAID %d" % (int(h["raid"]) + 1), 18, DIM)
		_t(r.position + Vector2(110.0, 8.0), tier, 18, TIER_COLOR.get(tier, INK))
		var cap := "no capture" if _none(h["capture"]) else "captured " + _cell_name(h["capture"])
		_t(r.position + Vector2(260.0, 10.0), cap, 13, INK)
		_t(r.position + Vector2(430.0, 10.0), "response " + _resp_label(h["response"], h["sentries"]), 13, ACID)
		_t(r.position + Vector2(14.0, 36.0), "%s   Heat %d -> %d" % [_sum(h["touches"]), int(h["heat_launch"]), int(h["heat_after"])], 13, INK)
		var bt: Variant = h["between"]
		if typeof(bt) == TYPE_DICTIONARY:
			var b: Dictionary = bt
			var rep := "no repair" if _none(b["repair"]) else "repaired " + _cell_name(b["repair"])
			var bld := "no build" if _none(b["build"]) else "built " + _tname(String(b["build"]))
			_t(r.position + Vector2(14.0, 54.0), "then %s, %s, ran %s (income +%d, Heat +%d)" % [rep, bld, String(b["intensity"]),
				int(b["income"]), int(b["heat_add"])], 12, DIM)
		y += 82.0
	var live := L8Rules.live_cells(st)
	var ex_kept := 0
	for c: Variant in leg["exploits"]:
		if live.has(c):
			ex_kept += 1
	var taken := 0
	for c: Vector2i in L8Rules.CELLS:
		if _status_of(st, c) == L8Rules.TAKEN:
			taken += 1
	y += 8.0
	_t(Vector2(x, y), "Districts kept: %d   TAKEN by the corp: %d   Exploits kept: %d/%d" % [live.size(), taken, ex_kept,
		L8Rules.EXPLOITS], 15, INK)
	var px := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var py := _head("SCORE", "Enter plays the leg again." if shots_dir == "" else "Shots done.")
	var sp := L8Rules.score_parts(leg, st)
	if bool(sp["breach"]):
		_t(Vector2(px, py), "CAMPAIGN LOST", 28, RED)
		_t(Vector2(px, py + 40.0), "A breach leaves no score.", 14, INK)
	else:
		var rows: Array = [["bank", "+%d" % int(sp["bank"])], ["districts held", "+%d" % int(sp["cells"])],
			["exploits held", "+%d" % int(sp["exploits"])], ["HOME lost", "-%d" % int(sp["home_loss"])],
			["Heat above %d" % L8Rules.START_HEAT, "-%s" % _num(float(sp["heat_carry"]))]]
		for rw: Variant in rows:
			var a: Array = rw
			_t(Vector2(px, py), String(a[0]), 14, INK)
			_tr(Vector2(px + w, py), String(a[1]), 14, AMBER)
			py += 24.0
		ui.draw_line(Vector2(px, py + 2.0), Vector2(px + w, py + 2.0), EDGE, 2.0)
		py += 10.0
		_t(Vector2(px, py), "TOTAL", 18, INK)
		_tr(Vector2(px + w, py - 4.0), _num(float(sp["total"])), 28, AMBER)
	if shots_dir == "":
		_btn(Rect2(px, LEGEND_Y - 58.0, w, 42.0), "PLAY THE LEG AGAIN [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- the frame
func _draw_ui() -> void:
	hits = []
	resp_hover = -1
	if load_error != "":
		ui.draw_rect(Rect2(Vector2.ZERO, VIEW), BG)
		_t(Vector2(40.0, 40.0), load_error, 18, RED)
		return
	_draw_hud()
	ui.draw_rect(Rect2(PANEL_X, HUD_H, PANEL_W, LEGEND_Y - HUD_H), Color(PANEL, 0.93))
	ui.draw_line(Vector2(PANEL_X, HUD_H), Vector2(PANEL_X, LEGEND_Y), EDGE, 1.0)
	match phase:
		Phase.CAPTURE:
			_draw_capture()
		Phase.PLAN:
			_draw_plan()
		Phase.FORECAST:
			_draw_forecast()
		Phase.PLAY, Phase.REVEAL:
			_draw_play()
		Phase.RESPONSE:
			_draw_response()
		Phase.AFTER:
			_draw_after()
		Phase.BETWEEN:
			_draw_between()
		Phase.RECORD:
			_draw_record()
	_draw_board_marks()
	_draw_legend()
	_draw_hint()


func _hud_values() -> Dictionary:
	var v := {"heat": int(st["heat"]), "note": "", "bank": int(st["bank"]), "hp": int(st["home_hp"]), "score": _score_text(st)}
	match phase:
		Phase.PLAN, Phase.FORECAST:
			var lh := L8Rules.launch_heat(st, place)
			if lh != int(st["heat"]):
				v["note"] = "ghost +%d" % L8Rules.GHOST_HEAT
			v["heat"] = lh
		Phase.PLAY, Phase.REVEAL, Phase.RESPONSE:
			v["heat"] = heat_launch
			v["note"] = "at launch"
			v["hp"] = hud_hp
			v["score"] = _score_text(before)
		Phase.BETWEEN:
			var ns: Dictionary = _bp(b_inten)["state"]
			v["heat"] = int(ns["heat"])
			v["note"] = "after the run"
			v["bank"] = int(ns["bank"])
			v["score"] = _score_text(ns)
	return v


func _draw_hud() -> void:
	ui.draw_rect(Rect2(0.0, 0.0, VIEW.x, HUD_H), Color(BG, 0.88))
	ui.draw_line(Vector2(0.0, HUD_H), Vector2(VIEW.x, HUD_H), EDGE, 1.0)
	var v := _hud_values()
	var heat := int(v["heat"])
	var hx := 20.0
	var hy := 30.0
	var hw := 300.0
	var hh := 16.0
	_t(Vector2(hx, 7.0), "HEAT", 12, DIM)
	ui.draw_rect(Rect2(hx, hy, hw, hh), Color8(20, 22, 36))
	var f := clampf(float(heat) / HEAT_MAX, 0.0, 1.0)
	ui.draw_rect(Rect2(hx, hy, hw * f, hh), AMBER.lerp(RED, f))
	ui.draw_rect(Rect2(hx, hy, hw, hh), EDGE, false, 1.5)
	var notches: Array = [[L8Rules.EXTRA_AT, "+1"], [L8Rules.STRONG_AT, "+2"]]
	for nv: Variant in notches:
		var n: Array = nv
		var nx := hx + hw * float(int(n[0])) / HEAT_MAX
		var lit := heat >= int(n[0])
		ui.draw_line(Vector2(nx, hy - 5.0), Vector2(nx, hy + hh + 5.0), INK if lit else DIM, 3.0)
		_t(Vector2(nx + 4.0, 7.0), "%d %s" % [int(n[0]), String(n[1])], 11, RED if lit else DIM)
	_t(Vector2(hx + hw + 12.0, 14.0), str(heat), 28, HEAT_COL)
	if String(v["note"]) != "":
		_t(Vector2(hx + hw + 62.0, 24.0), String(v["note"]), 11, DIM)
	_t(Vector2(480.0, 7.0), "RAID", 12, DIM)
	_t(Vector2(480.0, 22.0), "%d/%d" % [mini(raid + 1, L8Rules.RAIDS), L8Rules.RAIDS], 24, INK)
	_t(Vector2(560.0, 7.0), "HOME", 12, DIM)
	var hp := int(v["hp"])
	for k in range(L8Rules.HOME_HP):
		var pr := Rect2(560.0 + k * 26.0, 30.0, 20.0, 16.0)
		if k < hp:
			ui.draw_rect(pr, GOLD)
		else:
			ui.draw_rect(pr, RED.darkened(0.5))
			ui.draw_rect(pr, RED, false, 2.0)
	_t(Vector2(670.0, 7.0), "BANK", 12, DIM)
	_t(Vector2(670.0, 22.0), str(int(v["bank"])), 24, GOLD)
	_t(Vector2(750.0, 7.0), "SCORE", 12, DIM)
	_t(Vector2(750.0, 22.0), String(v["score"]), 24, INK)
	var tag := "L8 CITY RAID  |  leg %d" % leg_seed
	if auto_line != "":
		tag += "  |  auto %s" % auto_line
	_tr(Vector2(VIEW.x - PAD, 10.0), tag, 12, DIM)
	_tr(Vector2(VIEW.x - PAD, 30.0), "speed %dx%s" % [int(speed), "  instant" if instant else ""], 12, DIM)


## Overlay marks on the board: cell tags, the hovered cell, repair costs, the redeploy pick and the hovered row's move.
func _draw_board_marks() -> void:
	if phase in [Phase.PLAN, Phase.FORECAST, Phase.RESPONSE, Phase.AFTER, Phase.BETWEEN]:
		for c: Vector2i in L8Rules.CELLS:
			_tc(_screen(c) + Vector2(0.0, 36.0), _cell_name(c), 11, Color(DIM, 0.85))
	if phase == Phase.BETWEEN:
		for cv: Variant in _down_cells():
			var c: Vector2i = cv
			var p := _screen(c)
			_tc(p + Vector2(0.0, -50.0), "-%d" % L8Rules.repair_cost(leg, c), 15, AMBER)
		if not _none(b_repair):
			ui.draw_arc(_screen(b_repair), 34.0, 0.0, TAU, 40, ACID, 3.0)
	if phase == Phase.RESPONSE:
		if not _none(redeploy_from):
			ui.draw_arc(_screen(redeploy_from), 34.0, 0.0, TAU, 40, ACID, 3.0)
		if resp_hover >= 0:
			var r: Array = resp_opts[resp_hover]["response"]
			if String(r[0]) == "REDEPLOY":
				var a := _screen(r[1])
				var b := _screen(r[2])
				ui.draw_arc(a, 30.0, 0.0, TAU, 32, INK, 2.0)
				ui.draw_arc(b, 30.0, 0.0, TAU, 32, ACID, 3.0)
				ui.draw_line(a, b, ACID, 2.0)
	if busy or auto_line != "":
		return
	if not (phase in [Phase.CAPTURE, Phase.PLAN, Phase.FORECAST, Phase.RESPONSE, Phase.BETWEEN]):
		return
	if mouse.x >= PANEL_X or mouse.y < HUD_H or mouse.y > LEGEND_Y:
		return
	var hc: Variant = _pick(mouse, phase == Phase.PLAN or phase == Phase.FORECAST)
	if not _none(hc):
		ui.draw_arc(_screen(hc), 30.0, 0.0, TAU, 32, INK, 2.0)


func _draw_legend() -> void:
	ui.draw_rect(Rect2(0.0, LEGEND_Y, VIEW.x, VIEW.y - LEGEND_Y), Color(BG, 0.92))
	ui.draw_line(Vector2(0.0, LEGEND_Y), Vector2(VIEW.x, LEGEND_Y), EDGE, 1.0)
	var y := LEGEND_Y + 12.0
	var x := 16.0
	for tv: Variant in L8Rules.TYPES:
		var t: String = tv
		_glyph(Vector2(x + 8.0, y), t, 8.0, TYPE_COLOR[t])
		_t(Vector2(x + 20.0, y - 8.0), _tname(t), 12, INK)
		x += 32.0 + _tw(_tname(t), 12)
	var items: Array = ["SENTRY", "GHOST", "DOWN", "TAKEN", "EXPLOIT", "HUNTER", "HOME"]
	for iv: Variant in items:
		var it: String = iv
		var c := Vector2(x + 8.0, y)
		match it:
			"SENTRY":
				_sentry_icon(c, "D")
			"GHOST":
				_ghost_icon(c, 7.0, GOLD)
			"DOWN":
				_down_icon(c)
			"TAKEN":
				_taken_icon(c)
			"EXPLOIT":
				_key_icon(c, ACID)
			"HUNTER":
				_hound_icon(c)
			"HOME":
				ui.draw_rect(Rect2(c - Vector2(6.0, 8.0), Vector2(12.0, 16.0)), AMBER)
		_t(Vector2(x + 20.0, y - 8.0), it, 12, DIM)
		x += 32.0 + _tw(it, 12)


func _hint() -> String:
	match phase:
		Phase.CAPTURE:
			return "CAPTURE: click a glowing district, or its row in the panel."
		Phase.PLAN:
			return "PLAN: 1 2 3 pick a sentry (D N E), G the ghost, click a district; click a placed one to lift it. Z undoes, Enter forecasts."
		Phase.FORECAST:
			return "FORECAST: Enter launches, B goes back; any edit returns to the plan."
		Phase.PLAY, Phase.REVEAL:
			return "PLAYOUT: 1 2 4 set the speed, I toggles instant."
		Phase.RESPONSE:
			return "RESPONSE: H holds, J jams, click a row, or click a sentry then a free district (REDEPLOY). The wheel scrolls."
		Phase.AFTER:
			return "AFTERMATH: Enter goes on."
		Phase.BETWEEN:
			return "BETWEEN: click a DOWN district to repair it, B then 1 2 3 builds (0 for none), L N O sets the intensity, Enter starts the next raid."
		Phase.RECORD:
			return "RECORD: Enter plays the leg again."
	return ""


func _draw_hint() -> void:
	var msg := status_msg if status_msg != "" else _hint()
	if auto_line != "" and status_msg == "":
		msg = "[AUTO %s] %s" % [auto_line.to_upper(), msg]
	_t(Vector2(16.0, HINT_Y + 3.0), msg, 13, AMBER if status_msg != "" else DIM)


# ---------------------------------------------------------------- auto replay and shots
func _until(ps: Array) -> void:
	var guard := 0
	while not ps.has(phase) and guard < UNTIL_GUARD:
		guard += 1
		await get_tree().process_frame


func _beat(label: String) -> void:
	if shots_dir != "":
		await _shot(label)
	else:
		await get_tree().create_timer(AUTO_WAIT).timeout


func _shot(label: String) -> void:
	ui.queue_redraw()
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var path := "%s/%03d_%s.png" % [shots_dir, shot_n, label]
	img.save_png(path)
	shot_n += 1
	print("shot ", path)


func _auto_place(p: Dictionary) -> void:
	_push()
	place = {"sentries": {}, "ghost": null}
	var sd: Dictionary = p["sentries"]
	for c: Vector2i in L8Rules.sorted_cells(sd):
		_set_tool(String(sd[c]), false)
		_plan_click(c)
	if not _none(p["ghost"]):
		_set_tool("G", false)
		_plan_click(p["ghost"])
	tool = ""
	_highlight_tool()
	board.show_state(st, place)


func _auto_respond(r: Array) -> void:
	if r.is_empty():
		_respond(["HOLD"])
	elif String(r[0]) == "REDEPLOY":
		_response_click(r[1])
		_response_click(r[2])
	else:
		_respond(r)


func _verify(s: Dictionary) -> void:
	if history.is_empty():
		return
	var row: Dictionary = history.back()
	var ok_tier := String(row["tier"]) == String(s["tier"])
	var ok_score := absf(float(row["score"]) - float(s["score_raid"])) < 0.001
	if ok_tier and ok_score:
		print("auto %s raid %d: %s, score %s (matches the golden)" % [auto_line, int(s["raid"]) + 1, String(row["tier"]), _num(float(row["score"]))])
	else:
		push_warning("auto %s raid %d MISMATCH: lab %s %s, golden %s %s" % [auto_line, int(s["raid"]) + 1, String(row["tier"]),
			_num(float(row["score"])), String(s["tier"]), _num(float(s["score_raid"]))])


## Replay the golden line's choices for this leg through the same UI handlers (capture, place, response, between).
func _run_auto() -> void:
	var steps: Array = leg_entry.get(auto_line, [])
	if shots_dir != "":
		DirAccess.make_dir_recursive_absolute(shots_dir)
		instant = true
		board.set_instant(true)
	await get_tree().process_frame
	await get_tree().process_frame
	for sv: Variant in steps:
		var s: Dictionary = sv
		var rn := int(s["raid"]) + 1
		await _until([Phase.CAPTURE, Phase.PLAN, Phase.RECORD])
		if phase == Phase.RECORD:
			break
		if phase == Phase.CAPTURE:
			await _beat("r%d_capture" % rn)
			if not _none(s["capture"]):
				_do_capture(L8Rules.to_cell(s["capture"]))
		await _until([Phase.PLAN])
		_auto_place(L8Rules.place_from_json(s["place"]))
		await _beat("r%d_plan" % rn)
		_enter_forecast()
		await _beat("r%d_forecast" % rn)
		_launch()
		await _until([Phase.RESPONSE])
		await _beat("r%d_response" % rn)
		_auto_respond(L8Rules.norm_response(s["response"]))
		await _until([Phase.AFTER])
		_verify(s)
		await _beat("r%d_aftermath" % rn)
		_next()
		if phase == Phase.BETWEEN and typeof(s.get("between")) == TYPE_DICTIONARY:
			var b: Dictionary = s["between"]
			await _beat("r%d_between_open" % rn)
			if not _none(b["repair"]):
				_between_click(L8Rules.to_cell(b["repair"]))
			if not _none(b["build"]):
				_set_build(String(b["build"]))
			_set_inten(String(b["intensity"]))
			await _beat("r%d_between_picked" % rn)
			_next()
	await _until([Phase.RECORD])
	await _beat("record")
	if shots_dir != "":
		get_tree().quit(0)
