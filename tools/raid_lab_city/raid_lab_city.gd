extends Control
## Raid lab L8/L9/L10: the playable city raid (docs/handoff/raid_lab_l8/SPEC.md section 8, with L9_CHANGES.md and the
## L10_CHANGES.md presentation applied).
## This is the root script of raid_lab_city.tscn, and everything is built in code. A 3D L8Board renders in a SubViewport
## behind a 2D overlay. The overlay holds the HUD, the 420 px right panel, the legend strip and the hint line.
## Every state change goes through L8Rules. The view only reads its results and turns traces into board cues.
## Flow per raid: DECAY (raids 2 and 3), CAPTURE, PLAN, FORECAST, the known beams, the REVEAL, the RESPONSE, then the
## sealed beam and the hunter, AFTERMATH, BETWEEN. RECORD follows raid 3 or a breach.
## In PLAN and FORECAST one sealed route is selected (Q W E or a panel row). Its HOLD outcome is drawn on the board, and
## the other candidate routes are drawn faint.
## Tiers read without words: each has a mark and a hue (check, shield, cracked shield, X, skull on black).
## Highlights carry meaning: capture targets, repair targets, and picked choices (a white check ring).
## At HOME 1/3 the last HOME pip pulses red with a skull, and the between screen warns that the next hit ends the campaign.
## Flags (after --): --leg=N (golden seeds 0 3 5 8), --auto=greedy|naive, --shots=<abs dir> (with --auto), --scramble.

enum Phase { CAPTURE, PLAN, FORECAST, PLAY, REVEAL, RESPONSE, AFTER, BETWEEN, RECORD, DECAY }

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
const LETHAL_HZ := 1.5
const LINE_ID := {"beam1": 10, "extra1": 11, "extra2": 12, "sealed": 13, "hunter": 14}
const BEAM_NAME := {"beam1": "BEAM 1", "extra1": "EXTRA 1", "extra2": "EXTRA 2", "sealed": "SEALED", "hunter": "HUNTER"}
const CELL_ROW := ["NOR", "MID", "SOU"]
const INTEN_KEY := ["L", "N", "O"]
const ROUTE_KEY := ["Q", "W", "E"]

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
const YELLOW := Color8(255, 236, 60)
const WHITE := Color8(255, 255, 255)
const BLACK := Color8(0, 0, 0)
const HEAT_COL := Color8(255, 122, 40)
const GREY := Color8(110, 116, 134)
const HOLDS_COL := Color8(63, 224, 176)
const TYPE_COLOR := {"D": Color8(92, 225, 255), "N": Color8(255, 64, 214), "E": Color8(255, 140, 26)}
## Tier language (L10): EVADED check in acid green, HOLDS shield in green-cyan, BATTERED cracked shield in amber,
## DAMAGED X in red, BREACHED skull on black with a red border. The marks are drawn by _tier_glyph.
const TIER_COLOR := {"BREACHED": Color8(255, 255, 255), "DAMAGED": Color8(255, 61, 77), "BATTERED": Color8(255, 176, 32),
	"HOLDS": Color8(63, 224, 176), "EVADED": Color8(212, 255, 0)}
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
var fc_change: Array = []
var sel_route: int = 0
var sel_hold: Dictionary = {}
var rd: Dictionary = {}
var real: int = 0
var before: Dictionary = {}
var heat_launch: int = 0
var mid: Dictionary = {}
var known_tr: Array = []
var stage: String = ""
var resp_opts: Array = []
var resp_rows: Array = []
var resp_all_same: bool = false
var redeploy_from: Variant = null
var resp_scroll: int = 0
var resp_hover: int = -1
var result: Dictionary = {}
var b_repair: Variant = null
var b_build: Variant = null
var b_inten: String = "NORMAL"
var build_armed: bool = false
var decay_lines: PackedStringArray = PackedStringArray()

var busy: bool = false
var speed: float = 1.0
var instant: bool = false
var hud_hp: int = 3
var lethal_on: bool = false
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
	decay_lines = PackedStringArray()
	hud_hp = int(st["home_hp"])
	board.setup({"w": L8Rules.W, "h": L8Rules.H, "values": leg["values"], "exploits": leg["exploits"]})
	board.set_scramble(scramble)
	lethal_on = int(st["home_hp"]) == 1
	board.set_lethal(lethal_on)
	board.clear_outcome()
	board.show_state(st, _empty_place())
	_begin_raid()


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


## The one-line breakdown of the leg value: bank, districts, exploits, HOME, Heat.
func _parts_text(s: Dictionary) -> String:
	if s.is_empty():
		return ""
	var sp: Dictionary = L8Rules.score_parts(leg, s)
	if bool(sp["breach"]):
		return "a breach leaves no score"
	return "bank %d + districts %d + exploits %d - HOME %d - Heat %s" % [int(sp["bank"]), int(sp["cells"]),
		int(sp["exploits"]), int(sp["home_loss"]), _num(float(sp["heat_carry"]))]


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


## Which districts a touch list names: "hit MID 0, SOU 1; blocked at NOR 0".
func _cells_text(touches: Array) -> String:
	var hit := PackedStringArray()
	var blk := PackedStringArray()
	for e: Array in touches:
		match String(e[1]):
			"hit":
				hit.append(_cell_name(e[0]))
			"block":
				blk.append(_cell_name(e[0]))
	var parts := PackedStringArray()
	if not hit.is_empty():
		parts.append("hit " + ", ".join(hit))
	if not blk.is_empty():
		parts.append("blocked at " + ", ".join(blk))
	if parts.is_empty():
		return "no district touched"
	return "; ".join(parts)


## The key that decides "same outcome": the same touches and the same tier.
func _okey(touches: Array, tier: String) -> String:
	return "%s|%s" % [str(touches), tier]


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


func _now() -> float:
	return float(Time.get_ticks_msec()) / 1000.0


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


func _skull(c: Vector2, r: float, col: Color, hole: Color) -> void:
	ui.draw_circle(c + Vector2(0.0, -r * 0.15), r * 0.8, col)
	ui.draw_rect(Rect2(c + Vector2(-r * 0.45, r * 0.3), Vector2(r * 0.9, r * 0.6)), col)
	ui.draw_circle(c + Vector2(-r * 0.32, -r * 0.15), r * 0.22, hole)
	ui.draw_circle(c + Vector2(r * 0.32, -r * 0.15), r * 0.22, hole)
	var tw := maxf(1.0, r * 0.12)
	ui.draw_line(c + Vector2(-r * 0.15, r * 0.5), c + Vector2(-r * 0.15, r * 0.9), hole, tw)
	ui.draw_line(c + Vector2(r * 0.15, r * 0.5), c + Vector2(r * 0.15, r * 0.9), hole, tw)


## A white check ring around a picked or committed choice, with a check badge at its upper right.
func _check_ring(p: Vector2) -> void:
	ui.draw_arc(p, 34.0, 0.0, TAU, 40, WHITE, 3.0)
	var c := p + Vector2(24.0, -24.0)
	ui.draw_circle(c, 9.0, BLACK)
	ui.draw_arc(c, 9.0, 0.0, TAU, 20, WHITE, 1.5)
	ui.draw_polyline(PackedVector2Array([c + Vector2(-5.0, 0.0), c + Vector2(-1.5, 4.0), c + Vector2(5.0, -4.0)]), WHITE, 2.5)


func _tier_col(tier: String) -> Color:
	return TIER_COLOR.get(tier, INK)


func _shield_pts(c: Vector2, r: float) -> PackedVector2Array:
	return PackedVector2Array([c + Vector2(-r * 0.8, -r * 0.85), c + Vector2(r * 0.8, -r * 0.85),
		c + Vector2(r * 0.8, -r * 0.05), c + Vector2(0.0, r * 0.95), c + Vector2(-r * 0.8, -r * 0.05)])


## The tier's own mark: EVADED check, HOLDS shield, BATTERED cracked shield, DAMAGED X, BREACHED skull.
func _tier_glyph(c: Vector2, tier: String, r: float, col: Color) -> void:
	var w := maxf(2.0, r * 0.3)
	match tier:
		"EVADED":
			ui.draw_polyline(PackedVector2Array([c + Vector2(-r * 0.85, -r * 0.05), c + Vector2(-r * 0.3, r * 0.6),
				c + Vector2(r * 0.85, -r * 0.65)]), col, w)
		"HOLDS":
			ui.draw_colored_polygon(_shield_pts(c, r), col)
		"BATTERED":
			ui.draw_colored_polygon(_shield_pts(c, r), col)
			ui.draw_polyline(PackedVector2Array([c + Vector2(-r * 0.1, -r * 0.9), c + Vector2(r * 0.25, -r * 0.35),
				c + Vector2(-r * 0.2, r * 0.1), c + Vector2(r * 0.15, r * 0.55), c + Vector2(0.0, r * 0.9)]), BG,
				maxf(1.5, r * 0.22))
		"DAMAGED":
			ui.draw_line(c + Vector2(-r * 0.75, -r * 0.75), c + Vector2(r * 0.75, r * 0.75), col, w)
			ui.draw_line(c + Vector2(r * 0.75, -r * 0.75), c + Vector2(-r * 0.75, r * 0.75), col, w)
		"BREACHED":
			_skull(c, r, col, BLACK)
		_:
			ui.draw_circle(c, r * 0.5, col)


## A square tier pip (record rows and the record strip): the mark in a box of its hue; BREACHED is black with a red border.
func _tier_pip(c: Vector2, tier: String, r: float) -> void:
	var col := _tier_col(tier)
	var rect := Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)
	if tier == "BREACHED":
		ui.draw_rect(rect, BLACK)
		ui.draw_rect(rect, RED, false, 2.0)
	else:
		ui.draw_rect(rect, PANEL)
		ui.draw_rect(rect, col, false, 2.0)
	_tier_glyph(c, tier, r * 0.68, col)


## A small right-aligned tier stamp: mark then name. BREACHED sits white on black inside a red border.
func _tier_tag(right: Vector2, tier: String, size: int = 13) -> void:
	var col := _tier_col(tier)
	var tw := _tw(tier, size)
	var h := font.get_height(size)
	var gr := float(size) * 0.45
	var gx := right.x - tw - gr - 6.0
	if tier == "BREACHED":
		var left := gx - gr - 4.0
		var r := Rect2(left, right.y - 2.0, right.x - left + 4.0, h + 4.0)
		ui.draw_rect(r, BLACK)
		ui.draw_rect(r, RED, false, 2.0)
	_tier_glyph(Vector2(gx, right.y + h * 0.5), tier, gr, col)
	_tr(right, tier, size, col)


## The big aftermath stamp at p (top-left). Returns its height.
func _tier_big(p: Vector2, tier: String) -> float:
	var size := 34
	var col := _tier_col(tier)
	var h := font.get_height(size)
	var gr := 15.0
	if tier == "BREACHED":
		var r := Rect2(p.x - 6.0, p.y - 4.0, gr * 2.0 + 26.0 + _tw(tier, size), h + 8.0)
		ui.draw_rect(r, BLACK)
		ui.draw_rect(r, RED, false, 3.0)
	_tier_glyph(p + Vector2(gr + 2.0, h * 0.5), tier, gr, col)
	_t(p + Vector2(gr * 2.0 + 12.0, 0.0), tier, size, col)
	return h + 12.0


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
	if busy or phase == Phase.PLAY or phase == Phase.REVEAL or phase == Phase.DECAY:
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
				KEY_Q:
					_select_route(0)
				KEY_W:
					_select_route(1)
				KEY_E:
					_select_route(2)
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
					elif resp_all_same:
						status_msg = "Nothing you can do changes this: HOLD [H]."
					else:
						status_msg = "No spoof left: JAM is not available."
				KEY_ESCAPE:
					redeploy_from = null
					_build_resp_rows()
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
	elif id.begins_with("route:"):
		_select_route(int(id.substr(6)))
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
		if i >= 0 and i < resp_rows.size():
			var o: Dictionary = resp_opts[int(resp_rows[i]["rep"])]
			_respond(o["response"])
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


# ---------------------------------------------------------------- DECAY
## Start a raid: from raid 2 on, every district still DOWN is TAKEN by the corp (L8Rules.decay), shown as a short beat.
## CAPTURE then works on the decayed state.
func _begin_raid() -> void:
	decay_lines = PackedStringArray()
	if raid > 0:
		var dec: Dictionary = L8Rules.decay(leg, st)
		var gone: Array = []
		for c: Vector2i in L8Rules.CELLS:
			if _status_of(st, c) != L8Rules.TAKEN and _status_of(dec, c) == L8Rules.TAKEN:
				gone.append(c)
		if not gone.is_empty():
			var sent: Dictionary = st["sentries"]
			for cv: Variant in gone:
				var line := "Left DOWN: %s is TAKEN by the corp" % _cell_name(cv)
				if sent.has(cv):
					line += " (its %s sentry is lost)" % _tname(String(sent[cv]))
				decay_lines.append(line)
			board.reset_playout()
			board.clear_paths()
			board.clear_outcome()
			board.clear_highlight()
			board.show_state(st, {"sentries": st["sentries"], "ghost": null})
			phase = Phase.DECAY
			busy = true
			board.set_instant(instant)
			await board.decay(gone)
			st = dec
			board.show_state(st, {"sentries": st["sentries"], "ghost": null})
			busy = false
			if shots_dir != "":
				await _shot("r%d_decay" % (raid + 1))
		st = dec
	_enter_capture()


func _draw_decay() -> void:
	var x := PANEL_X + PAD
	var y := _head("DECAY  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Districts left DOWN fall to the corp.")
	for ln: String in decay_lines:
		_taken_icon(Vector2(x + 7.0, y + 8.0))
		_t(Vector2(x + 22.0, y), ln, 13, COBALT_HOT)
		y += 22.0
	y += 8.0
	_t(Vector2(x, y), "A DOWN district not repaired between raids is lost.", 12, DIM)


# ---------------------------------------------------------------- CAPTURE
func _enter_capture() -> void:
	board.reset_playout()
	board.clear_paths()
	board.clear_outcome()
	cap_opts = L8Rules.capture_options(leg, st)
	cap_cell = null
	board.show_state(st, {"sentries": st["sentries"], "ghost": null})
	if cap_opts.is_empty():
		status_msg = "No district can be captured: the raid goes on."
		_enter_plan()
		return
	phase = Phase.CAPTURE
	board.clear_highlight()
	board.highlight_kind(cap_opts, "capture")


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
	y = _draw_kit(y, false)
	if not decay_lines.is_empty():
		y += 6.0
		for ln: String in decay_lines:
			_taken_icon(Vector2(x + 7.0, y + 7.0))
			_t(Vector2(x + 22.0, y), ln, 12, COBALT_HOT)
			y += 18.0
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
	undo = []
	tool = ""
	fc = []
	fc_change = []
	sel_route = 0
	phase = Phase.PLAN
	board.clear_highlight()
	_plan_view()


## Redraw the plan on the board: the state and placement, the planned paths and the selected route's HOLD outcome.
func _plan_view() -> void:
	board.show_state(st, place)
	_show_plan_paths()
	_refresh_outcome()


func _select_route(k: int) -> void:
	if phase != Phase.PLAN and phase != Phase.FORECAST:
		return
	var n: int = (leg["raids"][raid]["cands"] as Array).size()
	if k < 0 or k >= n:
		return
	sel_route = k
	_show_plan_paths()
	_refresh_outcome()


func _beam_type(r_now: Dictionary, beam: String, cand: int) -> String:
	match beam:
		"beam1":
			return String(r_now["b1"]["type"])
		"extra1", "extra2":
			return String(r_now[beam]["type"])
		"sealed":
			return String(r_now["cands"][cand]["type"])
	return String(r_now["hunter_type"])


## The board outcome of sealed route k with HOLD, from L8Rules.trace and L8Rules.hunter_line.
func _outcome(k: int) -> Dictionary:
	var r_now: Dictionary = leg["raids"][raid]
	var tr: Array = L8Rules.trace(leg, raid, st, k, place, ["HOLD"])
	var hit_cells: Array = []
	var blocks: Array = []
	var btypes: Array = []
	var home := false
	for e: Array in tr:
		var kind := String(e[2])
		if kind == "home":
			home = true
			continue
		if typeof(e[1]) != TYPE_VECTOR2I:
			continue
		var c: Vector2i = e[1]
		if kind == "hit" and not hit_cells.has(c):
			hit_cells.append(c)
		elif kind == "block" and not blocks.has(c):
			blocks.append(c)
			btypes.append(_beam_type(r_now, String(e[0]), k))
	var hl: Variant = L8Rules.hunter_line(leg, raid, st, k, place, ["HOLD"])
	return {"hits": hit_cells, "blocks": blocks, "block_types": btypes, "home": home,
		"hunter": hl if typeof(hl) == TYPE_DICTIONARY else null}


func _refresh_outcome() -> void:
	sel_hold = {}
	if (phase != Phase.PLAN and phase != Phase.FORECAST) or L8Rules.check_place(st, place) != "":
		board.clear_outcome()
		return
	board.show_outcome(_outcome(sel_route))
	var res := L8Rules.resolve(leg, raid, st, sel_route, place, ["HOLD"])
	if not res.has("error"):
		var ns: Dictionary = res["state"]
		sel_hold = {"touches": res["touches"], "tier": L8Rules.tier(st, ns, res["touches"]), "home_hp": int(ns["home_hp"])}


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
	_plan_view()


func _back_to_plan() -> void:
	if phase == Phase.FORECAST:
		phase = Phase.PLAN
		fc = []
		fc_change = []


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
	_plan_view()


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
	if not sel_hold.is_empty():
		y += 4.0
		_t(Vector2(x, y), "ON THE BOARD: %s ROUTE WITH HOLD  [Q W E]" % L8Rules.ROUTE_NAMES[sel_route], 12, DIM)
		y += 18.0
		_t(Vector2(x, y), "%s   HOME %d/%d" % [_sum(sel_hold["touches"]), int(sel_hold["home_hp"]), L8Rules.HOME_HP], 12, INK)
		_tier_tag(Vector2(PANEL_X + PANEL_W - PAD, y), String(sel_hold["tier"]), 13)
		y += 22.0
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
		var sr := Rect2(gx - 12.0, y - 3.0, 96.0, 20.0)
		if k == sel_route:
			_box(sr, AMBER, PANEL_HI, 1.5)
		elif sr.has_point(mouse):
			_box(sr, INK, PANEL, 1.0)
		_glyph(Vector2(gx, y + 8.0), t, 7.0, TYPE_COLOR[t])
		_t(Vector2(gx + 10.0, y), "%s [%s]" % [L8Rules.ROUTE_NAMES[k], ROUTE_KEY[k]], 12, INK)
		hits.append({"rect": sr, "id": "route:%d" % k})
	y += 20.0
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
## Draw this raid's known beams (the ones its launch Heat brings) and the three sealed candidates on the board. The
## board draws the selected candidate (its index in the lines) and the known beams at full strength, the others faint.
func _show_plan_paths() -> void:
	var r_now: Dictionary = leg["raids"][raid]
	var h := L8Rules.launch_heat(st, place)
	var lines: Array = [r_now["b1"]]
	if h >= L8Rules.EXTRA_AT:
		lines.append(r_now["extra1"])
	if h >= L8Rules.STRONG_AT:
		lines.append(r_now["extra2"])
	var cands: Array = r_now["cands"]
	var selected := -1
	for k in range(cands.size()):
		lines.append(cands[k])
		if k == sel_route:
			selected = lines.size() - 1
	board.show_paths(lines, selected)


## True when some response for sealed route k gives other touches or another tier than HOLD.
func _response_changes(k: int) -> bool:
	var hold := L8Rules.resolve(leg, raid, st, k, place, ["HOLD"])
	if hold.has("error"):
		return false
	var hkey := _okey(hold["touches"], L8Rules.tier(st, hold["state"], hold["touches"]))
	for rv: Variant in L8Rules.response_options(leg, raid, st, k, place):
		var r: Array = rv
		var res := L8Rules.resolve(leg, raid, st, k, place, r)
		if res.has("error"):
			continue
		if _okey(res["touches"], L8Rules.tier(st, res["state"], res["touches"])) != hkey:
			return true
	return false


func _enter_forecast() -> void:
	if phase != Phase.PLAN:
		return
	var err := L8Rules.check_place(st, place)
	if err != "":
		status_msg = "Placement: " + err
		return
	fc = L8Rules.forecast(leg, raid, st, place)
	fc_change = []
	for fv: Variant in fc:
		var f: Dictionary = fv
		fc_change.append(_response_changes(int(f["cand"])))
	tool = ""
	board.clear_highlight()
	phase = Phase.FORECAST
	_show_plan_paths()
	_refresh_outcome()


func _draw_forecast() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("FORECAST  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Each sealed route with HOLD. Q W E shows one on the board.")
	y = _draw_kit(y, true)
	var cands: Array = leg["raids"][raid]["cands"]
	for i in range(fc.size()):
		var f: Dictionary = fc[i]
		var k := int(f["cand"])
		var t := String(cands[k]["type"])
		var hold: Dictionary = f["hold"]
		var r := Rect2(x, y, w, 92.0)
		var sel := k == sel_route
		var hot := r.has_point(mouse)
		_box(r, AMBER if sel else (INK if hot else EDGE), PANEL_HI if sel else PANEL)
		hits.append({"rect": r, "id": "route:%d" % k})
		_glyph(r.position + Vector2(16.0, 15.0), t, 9.0, TYPE_COLOR[t])
		_t(r.position + Vector2(32.0, 5.0), "%s ROUTE  %s" % [L8Rules.ROUTE_NAMES[k], _tname(t)], 14, INK)
		_tr(Vector2(r.end.x - 10.0, r.position.y + 6.0), "[%s]%s" % [ROUTE_KEY[k], "  on the board" if sel else ""], 11,
			AMBER if sel else DIM)
		var yy := r.position.y + 28.0
		var ht := String(hold["tier"])
		var hs: Dictionary = hold["state"]
		_t(Vector2(x + 10.0, yy), "HOLD", 12, DIM)
		_t(Vector2(x + 64.0, yy), "%s   HOME %d/%d" % [_sum(hold["touches"]), int(hs["home_hp"]), L8Rules.HOME_HP], 12, INK)
		_tier_tag(Vector2(r.end.x - 10.0, yy), ht, 13)
		yy += 20.0
		_t(Vector2(x + 64.0, yy), _cells_text(hold["touches"]), 11, DIM)
		yy += 20.0
		var ch: bool = bool(fc_change[i]) if i < fc_change.size() else false
		_t(Vector2(x + 64.0, yy), "a response changes this" if ch else "no response changes this", 12, ACID if ch else DIM)
		y += 98.0
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
	board.clear_outcome()
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
	var keys := {}
	for o: Dictionary in resp_opts:
		keys[_okey(o["touches"], String(o["tier"]))] = true
	resp_all_same = keys.size() <= 1
	redeploy_from = null
	resp_scroll = 0
	phase = Phase.RESPONSE
	_build_resp_rows()
	_highlight_sources()


## Group the visible options by outcome (same touches, same tier) into rows. When every option gives the same outcome,
## only HOLD is offered. Each row plays its representative: HOLD if it is in the row, else JAM, else the first move.
func _build_resp_rows() -> void:
	resp_rows = []
	var has_hold := false
	for o: Dictionary in resp_opts:
		if String((o["response"] as Array)[0]) == "HOLD":
			has_hold = true
	var idx: Array = []
	for i in range(resp_opts.size()):
		var r: Array = resp_opts[i]["response"]
		var head := String(r[0])
		if resp_all_same and has_hold and head != "HOLD":
			continue
		if not _none(redeploy_from) and head == "REDEPLOY" and r[1] != redeploy_from:
			continue
		idx.append(i)
	var keymap := {}
	for iv: Variant in idx:
		var i: int = iv
		var o: Dictionary = resp_opts[i]
		var key := _okey(o["touches"], String(o["tier"]))
		if not keymap.has(key):
			keymap[key] = resp_rows.size()
			resp_rows.append({"members": [], "rep": -1})
		var row: Dictionary = resp_rows[int(keymap[key])]
		(row["members"] as Array).append(i)
	for rowv: Variant in resp_rows:
		var row: Dictionary = rowv
		var members: Array = row["members"]
		var rep: int = int(members[0])
		var rank := 3
		for mv: Variant in members:
			var head := String((resp_opts[int(mv)]["response"] as Array)[0])
			var rk := 0 if head == "HOLD" else (1 if head == "JAM" else 2)
			if rk < rank:
				rank = rk
				rep = int(mv)
		row["rep"] = rep


func _row_label(members: Array, sd: Dictionary) -> String:
	var has_hold := false
	var has_jam := false
	var reds: Array = []
	for mv: Variant in members:
		var r: Array = resp_opts[int(mv)]["response"]
		match String(r[0]):
			"HOLD":
				has_hold = true
			"JAM":
				has_jam = true
			_:
				reds.append(r)
	var kinds := (1 if has_hold else 0) + (1 if has_jam else 0) + (1 if not reds.is_empty() else 0)
	var parts := PackedStringArray()
	if has_hold:
		parts.append("HOLD [H]")
	if has_jam:
		parts.append("JAM [J]" if kinds > 1 else "JAM the hunter [J]")
	if reds.size() == 1:
		parts.append("MOVE" if kinds > 1 else _resp_label(reds[0], sd))
	elif reds.size() > 1:
		parts.append("REDEPLOY (%d ways)" % reds.size())
	return " / ".join(parts)


func _has_jam() -> bool:
	if resp_all_same:
		return false
	for o: Dictionary in resp_opts:
		if String((o["response"] as Array)[0]) == "JAM":
			return true
	return false


func _highlight_sources() -> void:
	if resp_all_same:
		board.clear_highlight()
		return
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
	if resp_all_same:
		status_msg = "Nothing you can do changes this: HOLD [H]."
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
			_build_resp_rows()
			_highlight_sources()
		return
	var from: Vector2i = redeploy_from
	if cell == from:
		redeploy_from = null
		_build_resp_rows()
		_highlight_sources()
		return
	if sent.has(cell):
		redeploy_from = cell
		resp_scroll = 0
		_build_resp_rows()
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
	if resp_opts.size() <= 1:
		_t(Vector2(x, y), "No response is available: HOLD.", 13, AMBER)
		y += 20.0
	elif resp_all_same:
		_t(Vector2(x, y), "Nothing you can do changes this.", 13, AMBER)
		y += 20.0
	else:
		_t(Vector2(x, y), "Options with the same result share a row.", 12, DIM)
		y += 20.0
	if not _none(redeploy_from):
		var st_t := String((mid["sentries"] as Dictionary).get(redeploy_from, "?"))
		_t(Vector2(x, y), "Moves of the %s sentry on %s  (Esc: all rows)" % [_tname(st_t), _cell_name(redeploy_from)], 12, ACID)
		y += 20.0
	var max_rows := maxi(1, int((LEGEND_Y - 22.0 - y) / ROW_H))
	resp_scroll = clampi(resp_scroll, 0, maxi(0, resp_rows.size() - max_rows))
	var sd: Dictionary = mid["sentries"]
	for j in range(resp_scroll, mini(resp_rows.size(), resp_scroll + max_rows)):
		var row: Dictionary = resp_rows[j]
		var o: Dictionary = resp_opts[int(row["rep"])]
		var ns: Dictionary = o["state"]
		var tier := String(o["tier"])
		var rr := Rect2(x, y, w, ROW_H - 4.0)
		var hot := rr.has_point(mouse)
		if hot:
			resp_hover = j
		_box(rr, ACID if hot else EDGE, PANEL_HI if hot else PANEL)
		_t(rr.position + Vector2(8.0, 3.0), _row_label(row["members"], sd), 13, INK)
		_tier_tag(Vector2(rr.end.x - 8.0, rr.position.y + 3.0), tier, 13)
		_t(rr.position + Vector2(8.0, 19.0), "%s   HOME %d/%d   Heat %d" % [_sum(o["touches"]), int(ns["home_hp"]),
			L8Rules.HOME_HP, int(ns["heat"])], 11, DIM)
		hits.append({"rect": rr, "id": "resp:%d" % j})
		y += ROW_H
	if resp_rows.size() > max_rows:
		_tr(Vector2(PANEL_X + PANEL_W - PAD, LEGEND_Y - 18.0), "rows %d-%d of %d (wheel scrolls)" % [resp_scroll + 1,
			mini(resp_rows.size(), resp_scroll + max_rows), resp_rows.size()], 11, DIM)


# ---------------------------------------------------------------- AFTERMATH
func _draw_after() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var tier := String(result.get("tier", "HOLDS"))
	var y := _head("AFTERMATH  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Enter goes on.")
	y += _tier_big(Vector2(x, y), tier)
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
	_t(Vector2(x, y), "Districts held: %d    Leg value now: %s" % [live, _score_text(st)], 13, INK)
	y += 22.0
	var last := breached or raid >= L8Rules.RAIDS - 1
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "RECORD [Enter]" if last else "BETWEEN RAIDS [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- BETWEEN
func _enter_between() -> void:
	board.clear_paths()
	board.clear_outcome()
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


## Repair targets (DOWN districts) get the repair highlight; the picked repair gets the picked check ring.
func _highlight_down() -> void:
	board.clear_highlight()
	var todo: Array = []
	for cv: Variant in _down_cells():
		if not L8Rules._same(b_repair, cv):
			todo.append(cv)
	if not todo.is_empty():
		board.highlight_kind(todo, "repair")
	if not _none(b_repair):
		board.highlight_kind([b_repair], "picked")


func _bp(inten: String) -> Dictionary:
	return L8Rules.between_parts(leg, st, b_repair, b_build, inten)


## The next raid's routes to HOME left uncovered by a between choice, worst case and before any forecast: beam 1 when
## it is a route, and each sealed route. A route counts as covered when, after this step and the next raid's decay,
## the pool holds a sentry of its type and a live district sits on that route. Entries are [label, type].
func _home_gaps(repair: Variant, build: Variant) -> Array:
	var out: Array = []
	if raid + 1 >= L8Rules.RAIDS:
		return out
	var p := L8Rules.between_parts(leg, st, repair, build, b_inten)
	var ds: Dictionary = L8Rules.decay(leg, p["state"])
	var pool: Dictionary = ds["pool"]
	var rows := {}
	for cv: Variant in L8Rules.live_cells(ds):
		if typeof(cv) == TYPE_VECTOR2I:
			var v: Vector2i = cv
			rows[v.y] = true
	var rn: Dictionary = leg["raids"][raid + 1]
	var threats: Array = []
	var b1: Dictionary = rn["b1"]
	if bool(b1["home"]):
		threats.append(["BEAM 1 " + String(L8Rules.ROUTE_NAMES[int(b1["index"])]), b1])
	for cv: Variant in rn["cands"]:
		var ln: Dictionary = cv
		threats.append([String(L8Rules.ROUTE_NAMES[int(ln["index"])]), ln])
	for thv: Variant in threats:
		var th: Array = thv
		var ln: Dictionary = th[1]
		var t := String(ln["type"])
		if int(pool.get(t, 0)) <= 0 or not rows.has(int(ln["index"])):
			out.append([String(th[0]), t])
	return out


func _between_click(c: Variant) -> void:
	if phase != Phase.BETWEEN or typeof(c) != TYPE_VECTOR2I:
		return
	if _status_of(st, c) != L8Rules.DOWN:
		status_msg = "Only a DOWN district can be repaired."
		return
	if L8Rules._same(b_repair, c):
		b_repair = null
		_highlight_down()
		return
	var p := L8Rules.between_parts(leg, st, c, b_build, b_inten)
	if _none(p["repaired"]):
		status_msg = "Not enough bank to repair it (cost %d)." % L8Rules.repair_cost(leg, c)
		return
	b_repair = c
	if not _none(b_build) and _none(p["built"]):
		b_build = null
		status_msg = "The repair leaves too little for the build: the build is dropped."
	_highlight_down()


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
	_begin_raid()


func _draw_between() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("BETWEEN RAIDS", "Repair, build, pick an intensity. Enter: next raid.")
	var parts := _bp(b_inten)
	if int(st["home_hp"]) == 1:
		var br := Rect2(x, y - 4.0, w, 24.0)
		ui.draw_rect(br, RED.darkened(0.45))
		ui.draw_rect(br, RED, false, 2.0)
		_skull(br.position + Vector2(13.0, 12.0), 8.0, WHITE, BLACK)
		_t(br.position + Vector2(28.0, 4.0), "Next HOME hit ends the campaign", 13, WHITE)
		y += 26.0
	# Which repair or build protects HOME next raid (only when the worst case could reach it).
	var base := _home_gaps(null, null)
	var guard_builds: Array = []
	var guard_repairs: Array = []
	if not base.is_empty():
		var nb := _home_gaps(b_repair, null).size()
		for tv: Variant in L8Rules.TYPES:
			var t: String = tv
			if _none(L8Rules.between_parts(leg, st, b_repair, t, b_inten)["built"]):
				continue
			if _home_gaps(b_repair, t).size() < nb:
				guard_builds.append(t)
		var nr := _home_gaps(null, b_build).size()
		for cv: Variant in _down_cells():
			if _none(L8Rules.between_parts(leg, st, cv, b_build, b_inten)["repaired"]):
				continue
			if _home_gaps(cv, b_build).size() < nr:
				guard_repairs.append(cv)
	_t(Vector2(x, y), "1  REPAIR ONE DISTRICT (click a DOWN one; cost value / 2)", 12, DIM)
	y += 20.0
	if _none(b_repair):
		_t(Vector2(x + 18.0, y), "none" if not _down_cells().is_empty() else "nothing is DOWN", 13, DIM)
	else:
		_t(Vector2(x + 18.0, y), "%s   -%d" % [_cell_name(b_repair), int(parts["repair_cost"])], 13, ACID)
	y += 22.0
	for cv: Variant in _down_cells():
		var c: Vector2i = cv
		if L8Rules._same(b_repair, c):
			continue
		_down_icon(Vector2(x + 26.0, y + 8.0))
		_t(Vector2(x + 40.0, y), "%s is DOWN: repair it or lose it (-%d)" % [_cell_name(c), L8Rules.repair_cost(leg, c)], 12, RED)
		y += 18.0
	y += 6.0
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
			if guard_builds.has(t):
				ui.draw_rect(Rect2(r.position.x + 4.0, r.end.y - 5.0, r.size.x - 8.0, 3.0), ACID)
		if ok:
			hits.append({"rect": r, "id": "build:" + ("none" if t == "" else t)})
	y += 46.0
	if not base.is_empty():
		var gaps := _home_gaps(b_repair, b_build)
		if gaps.is_empty():
			_t(Vector2(x, y), "HOME NEXT RAID: this choice can block every route to HOME", 11, ACID)
		else:
			var head := "HOME NEXT RAID OPEN:"
			_t(Vector2(x, y), head, 11, RED)
			var gx := x + _tw(head, 11) + 8.0
			for gv: Variant in gaps:
				var g: Array = gv
				var gt := String(g[1])
				_glyph(Vector2(gx + 5.0, y + 7.0), gt, 5.5, TYPE_COLOR.get(gt, GREY))
				_t(Vector2(gx + 13.0, y), String(g[0]), 11, INK)
				gx += 22.0 + _tw(String(g[0]), 11)
		y += 16.0
		var prot := PackedStringArray()
		for tv: Variant in guard_builds:
			prot.append("build " + _tname(String(tv)))
		for cv: Variant in guard_repairs:
			prot.append("repair " + _cell_name(cv))
		if not prot.is_empty():
			_t(Vector2(x, y), "PROTECTS HOME: " + ", ".join(prot), 11, ACID)
		elif not gaps.is_empty():
			var ghost_ok := int((parts["state"]["kit"] as Dictionary).get("ghost", 0)) > 0
			_t(Vector2(x, y), "No repair or build here covers it%s" % (": a ghost on HOME does" if ghost_ok else "."), 11, DIM)
		y += 18.0
	else:
		y += 4.0
	_t(Vector2(x, y), "3  RUN INTENSITY   [L N O]   next Heat: no ghost - with a ghost", 12, DIM)
	y += 20.0
	var cw := (w - 16.0) / 3.0
	for i in range(3):
		var nm: String = L8Rules.INTENSITY_ORDER[i]
		var cr := Rect2(x + i * (cw + 8.0), y, cw, 124.0)
		var sel := nm == b_inten
		var hot := cr.has_point(mouse)
		_box(cr, AMBER if sel else (INK if hot else EDGE), PANEL_HI if (sel or hot) else PANEL, 3.0 if sel else 2.0)
		hits.append({"rect": cr, "id": "inten:" + nm})
		var p := _bp(nm)
		var ns: Dictionary = p["state"]
		var h0 := int(ns["heat"])
		var ghost_ok := int((ns["kit"] as Dictionary).get("ghost", 0)) > 0
		var h1 := h0 + (L8Rules.GHOST_HEAT if ghost_ok else 0)
		var k0 := 1 + L8Rules.extra_count(h0)
		var k1 := 1 + L8Rules.extra_count(h1)
		var hr := str(h0) if h1 == h0 else "%d-%d" % [h0, h1]
		var kn := str(k0) if k1 == k0 else "%d-%d" % [k0, k1]
		_t(cr.position + Vector2(8.0, 6.0), "%s [%s]" % [nm, INTEN_KEY[i]], 14, AMBER if sel else INK)
		_t(cr.position + Vector2(8.0, 30.0), "Heat +%d -> %d" % [int(p["heat_add"]), h0], 12, HEAT_COL)
		_t(cr.position + Vector2(8.0, 49.0), "income +%d" % int(p["income"]), 12, GOLD)
		_t(cr.position + Vector2(8.0, 68.0), "bank -> %d" % int(ns["bank"]), 12, INK)
		_t(cr.position + Vector2(8.0, 87.0), "next Heat %s" % hr, 11, RED if k1 > 1 else DIM)
		_t(cr.position + Vector2(8.0, 104.0), "%s known beam%s" % [kn, "" if k1 == 1 else "s"], 11, RED if k1 > 1 else DIM)
	y += 132.0
	var ns2: Dictionary = parts["state"]
	_t(Vector2(x, y), "BANK %d - repair %d - build %d + income %d = %d" % [int(st["bank"]), int(parts["repair_cost"]),
		int(parts["build_cost"]), int(parts["income"]), int(ns2["bank"])], 13, INK)
	y += 20.0
	_t(Vector2(x, y), "HEAT %d + %d = %d" % [int(st["heat"]), int(parts["heat_add"]), int(ns2["heat"])], 13, HEAT_COL)
	y += 20.0
	_t(Vector2(x, y), "Leg value after this step: %s" % _score_text(ns2), 13, INK)
	y += 24.0
	if y + 48.0 <= LEGEND_Y - 62.0:
		_draw_kit(y, false)
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "NEXT RAID [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- RECORD
func _enter_record() -> void:
	phase = Phase.RECORD
	board.clear_highlight()
	board.clear_outcome()


func _draw_record() -> void:
	ui.draw_rect(Rect2(0.0, HUD_H, PANEL_X, LEGEND_Y - HUD_H), Color(BG, 0.86))
	var x := 40.0
	var y := HUD_H + 20.0
	var title := "LEG RECORD  (leg %d)" % leg_seed
	_t(Vector2(x, y), title, 24, AMBER)
	var px0 := x + _tw(title, 24) + 26.0
	for i in range(history.size()):
		var hd: Dictionary = history[i]
		_tier_pip(Vector2(px0 + i * 30.0, y + 15.0), String(hd["tier"]), 11.0)
	y += 38.0
	if breached:
		_skull(Vector2(x + 9.0, y + 11.0), 9.0, RED, BG)
		_t(Vector2(x + 26.0, y), "BREACHED in raid %d: the campaign is lost." % history.size(), 18, RED)
	else:
		_t(Vector2(x, y), "THE CELL SURVIVED THE LEG", 18, ACID)
	y += 40.0
	for hv: Variant in history:
		var h: Dictionary = hv
		var tier := String(h["tier"])
		var tcol := _tier_col(tier)
		var r := Rect2(x, y, 780.0, 74.0)
		if tier == "BREACHED":
			_box(r, RED, BLACK, 3.0)
		else:
			_box(r, tcol, PANEL)
		_t(r.position + Vector2(14.0, 8.0), "RAID %d" % (int(h["raid"]) + 1), 18, DIM)
		_tier_pip(r.position + Vector2(116.0, 19.0), tier, 10.0)
		_t(r.position + Vector2(136.0, 8.0), tier, 18, tcol)
		var cap := "no capture" if _none(h["capture"]) else "captured " + _cell_name(h["capture"])
		_t(r.position + Vector2(280.0, 10.0), cap, 13, INK)
		_t(r.position + Vector2(440.0, 10.0), "response " + _resp_label(h["response"], h["sentries"]), 13, ACID)
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
	var py := _head("FINAL SCORE", "Enter plays the leg again." if shots_dir == "" else "Shots done.")
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
		Phase.DECAY:
			_draw_decay()
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
	var v := {"heat": int(st["heat"]), "note": "", "bank": int(st["bank"]), "hp": int(st["home_hp"]), "score": _score_text(st),
		"sstate": st}
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
			v["sstate"] = before
		Phase.BETWEEN:
			var ns: Dictionary = _bp(b_inten)["state"]
			v["heat"] = int(ns["heat"])
			v["note"] = "after the run"
			v["bank"] = int(ns["bank"])
			v["score"] = _score_text(ns)
			v["sstate"] = ns
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
	var lethal := hp == 1
	if lethal != lethal_on:
		lethal_on = lethal
		board.set_lethal(lethal)
	var pulse := 1.0 if shots_dir != "" else 0.5 + 0.5 * sin(_now() * TAU * LETHAL_HZ)
	for k in range(L8Rules.HOME_HP):
		var pr := Rect2(560.0 + k * 26.0, 30.0, 20.0, 16.0)
		if k < hp:
			if lethal:
				ui.draw_rect(pr, RED.darkened(0.6).lerp(RED, pulse))
				ui.draw_rect(pr, WHITE.lerp(RED, 1.0 - pulse), false, 2.0)
				_skull(pr.get_center(), 6.0, WHITE, BLACK)
			else:
				ui.draw_rect(pr, GOLD)
		else:
			ui.draw_rect(pr, RED.darkened(0.5))
			ui.draw_rect(pr, RED, false, 2.0)
	_t(Vector2(670.0, 7.0), "BANK", 12, DIM)
	_t(Vector2(670.0, 22.0), str(int(v["bank"])), 24, GOLD)
	_t(Vector2(750.0, 7.0), "LEG VALUE NOW", 12, DIM)
	_t(Vector2(750.0, 20.0), String(v["score"]), 22, INK)
	_t(Vector2(750.0, 48.0), _parts_text(v["sstate"]), 10, DIM)
	var tag := "L8 CITY RAID  |  leg %d" % leg_seed
	if auto_line != "":
		tag += "  |  auto %s" % auto_line
	_tr(Vector2(VIEW.x - PAD, 10.0), tag, 12, DIM)
	_tr(Vector2(VIEW.x - PAD, 30.0), "speed %dx%s" % [int(speed), "  instant" if instant else ""], 12, DIM)


## Overlay marks on the board: cell tags, the hovered cell, repair costs, the picked repair and redeploy source (white
## check rings), and the hovered response row's moves.
func _draw_board_marks() -> void:
	if phase in [Phase.PLAN, Phase.FORECAST, Phase.RESPONSE, Phase.AFTER, Phase.BETWEEN, Phase.DECAY]:
		for c: Vector2i in L8Rules.CELLS:
			_tc(_screen(c) + Vector2(0.0, 36.0), _cell_name(c), 11, Color(DIM, 0.85))
	if phase == Phase.BETWEEN:
		for cv: Variant in _down_cells():
			var c: Vector2i = cv
			var p := _screen(c)
			_tc(p + Vector2(0.0, -50.0), "-%d" % L8Rules.repair_cost(leg, c), 15, AMBER)
		if not _none(b_repair):
			_check_ring(_screen(b_repair))
	if phase == Phase.RESPONSE:
		if not _none(redeploy_from):
			_check_ring(_screen(redeploy_from))
		if resp_hover >= 0 and resp_hover < resp_rows.size():
			var row: Dictionary = resp_rows[resp_hover]
			for mv: Variant in row["members"]:
				var r: Array = resp_opts[int(mv)]["response"]
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
		Phase.DECAY:
			return "DECAY: districts left DOWN are TAKEN by the corp. 1 2 4 set the speed, I toggles instant."
		Phase.CAPTURE:
			return "CAPTURE: click a glowing district, or its row in the panel."
		Phase.PLAN:
			return "PLAN: 1 2 3 a sentry, G the ghost, click a district (again to lift). Q W E preview a sealed route. Z undoes, Enter forecasts."
		Phase.FORECAST:
			return "FORECAST: Q W E or a row shows a route on the board. Enter launches, B goes back; any edit returns to the plan."
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
	_plan_view()


## The golden's response goes straight to _respond (it is legal even when the UI merges rows or offers HOLD only).
func _auto_respond(r: Array) -> void:
	if r.is_empty():
		_respond(["HOLD"])
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
## DECAY runs on its own at the start of raids 2 and 3, so the golden's capture is made from the decayed state.
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
