extends Control
## Raid lab L8 to L13: the playable city raid (docs/handoff/raid_lab_l8/SPEC.md section 8, with the L9_CHANGES.md,
## L10_CHANGES.md, L11_CHANGES.md, L12_CHANGES.md and L13_UI.md presentation applied).
## This is the root script of raid_lab_city.tscn, and everything is built in code. A 3D L8Board renders in a SubViewport
## behind a 2D overlay. The overlay holds the HUD, the 420 px right panel, the legend strip and the hint line.
## Every state change goes through L8Rules. The view only reads its results and turns traces into board cues.
## Flow per raid: DECAY (raids 2 and 3), CAPTURE (twice after a HOT between step), PLAN, FORECAST, the known beams, the
## sealed REVEAL, the RESPONSE (chosen without knowing the hunter street), the sealed beam, the HUNTER REVEAL (one of the
## two sealed streets ignites), the hunter run (unless JAM), AFTERMATH, BETWEEN. RECORD follows raid 3, a breach, or a
## DECIDED cut.
## In PLAN and FORECAST one sealed route (Q W E) and one hunter street (H flips A / B) are selected; their HOLD outcome is
## drawn on the board, and both hunter streets show as sealed hound lanes. FORECAST shows, per sealed route, the HOLD
## result for hunter street A and B and the best response by mean over both streets. Each route's worse tier is stamped
## at its lane (L8Board.show_route_verdicts) and stays through the launch.
## Launch friction (L13, graduated): when HOME drops on every sealed route even with the best response, or whenever HOME
## is at 1, LAUNCH needs a second Enter or click. The panel names one fix when one exists: the first placement, in the
## rules' enumeration order, whose best responses keep HOME on every route and street (else one that avoids a breach).
## RESPONSE rows group options by outcome over both hunter streets and show "A / B" tiers; SACRIFICE rows trade a
## district for a shielded HOME. Hovering a row previews it on the board.
## Between raids every intensity card (with its perk: NORMAL free repair, HOT two captures next raid) and every repair
## and build option carries a verdict from L8Rules.safe_next ("HOLDABLE" shield or "LOST" skull), checked off a queue.
## When no between option holds, the screen says DECIDED, a fall beat plays and the record follows.
## Heat thresholds show as ghost beams on the corp tower (L8Board.set_heat_ghosts).
## Flags (after --): --leg=N (golden seeds 0 3 5 8), --auto=greedy|naive, --shots=<abs dir> (with --auto), --scramble.

enum Phase { CAPTURE, PLAN, FORECAST, PLAY, REVEAL, RESPONSE, AFTER, BETWEEN, RECORD, DECAY, FALL }

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
## A response row: three 13 px lines (label and tiers, A / B touches, HOME or the sacrifice note).
const ROW_H := 58.0
const AUTO_WAIT := 0.6
const UNTIL_GUARD := 60000
const SCRAMBLE_SEED := 8808
const LETHAL_HZ := 1.5
const LINE_ID := {"beam1": 10, "extra1": 11, "extra2": 12, "sealed": 13, "hunter": 14}
const BEAM_NAME := {"beam1": "BEAM 1", "extra1": "EXTRA 1", "extra2": "EXTRA 2", "sealed": "SEALED", "hunter": "HUNTER"}
const CELL_ROW := ["NOR", "MID", "SOU"]
const INTEN_KEY := ["L", "N", "O"]
const ROUTE_KEY := ["Q", "W", "E"]
const HUNT_KEY := ["A", "B"]
const CARD_H := 160.0
## Panel text never goes below this size (L13 item 8).
const TXT := 13
## Milliseconds of queued safe_next checks worked per frame on the between screen (at least one per frame).
const SAFE_BUDGET_MS := 12
const REP_ROW_H := 21.0
const FRICTION_BREACH := "Every route breaks HOME with this plan: change it?"
const FRICTION_LOSS := "Every route costs HOME with this plan: change it?"
const FRICTION_LAST := "HOME is at 1/3: one hit ends the campaign. Launch?"
const TIER_RANK := {"EVADED": 0, "HOLDS": 1, "BATTERED": 2, "DAMAGED": 3, "BREACHED": 4}

# Palette (matches l8_board.gd). DIM and LATER are lifted for contrast (L13 item 8).
const BG := Color8(3, 5, 15)
const PANEL := Color8(9, 13, 30)
const PANEL_HI := Color8(42, 34, 16)
const EDGE := Color8(60, 72, 112)
const INK := Color8(232, 236, 250)
const DIM := Color8(168, 178, 206)
const LATER := Color8(128, 138, 164)
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
const GREY := Color8(120, 126, 144)
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
var decided: bool = false
var decided_raid: int = -1
var history: Array = []
var cap_opts: Array = []
var cap_cells: Array = []
var cap_slots: int = 1
var place: Dictionary = {"sentries": {}, "ghost": null}
var undo: Array = []
var tool: String = ""
var fc: Array = []
## Per sealed candidate: {response, outcomes: [{state, touches, tier}] per hunter street}, or {} when none resolves.
var fc_best: Array = []
## Launch friction: 0 none, 1 HOME drops on every route, 2 every route breaches, 3 HOME is at 1.
var fric: int = 0
var launch_armed: bool = false
var launch_fix: Variant = null
var fix_kind: String = ""
var fix_cache: Dictionary = {}
var route_v: Array = []
var sel_route: int = 0
var sel_hunt: int = 0
var sel_hold: Dictionary = {}
var rd: Dictionary = {}
var real: int = 0
var hunt: int = 0
var hunter_revealed: bool = false
var cur_resp: Array = ["HOLD"]
var before: Dictionary = {}
var heat_launch: int = 0
var mid: Dictionary = {}
var known_tr: Array = []
var stage: String = ""
var resp_opts: Array = []
var resp_rows: Array = []
var resp_all_same: bool = false
var redeploy_from: Variant = null
var deploy_type: String = ""
var resp_scroll: int = 0
var resp_hover: int = -1
var resp_sel: int = -1
var resp_follow: bool = false
var resp_prev: int = -2
var resp_hunters: Array = []
var tray_pos: Dictionary = {}
var result: Dictionary = {}
var b_repair: Variant = null
var b_build: Variant = null
var b_inten: String = "NORMAL"
var build_armed: bool = false
## Between verdicts: option key (leg, raid, state hash, repair, build, intensity) -> bool; persistent across screens.
var safe_cache: Dictionary = {}
## safe_next results by (leg, raid, hash of the state it runs on) -> bool; options that give the same state share it.
var next_cache: Dictionary = {}
## Checks still to run: option key -> [repair, build, intensity], worked by _process.
var safe_pending: Dictionary = {}
var b_hash: int = 0
var b_all_unsafe: int = -1
var decay_lines: PackedStringArray = PackedStringArray()

var busy: bool = false
var speed: float = 1.0
var instant: bool = false
var hud_hp: int = 3
var lethal_on: bool = false
var heat_ghosts_k: int = -1
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
	decided = false
	decided_raid = -1
	history = []
	result = {}
	decay_lines = PackedStringArray()
	launch_armed = false
	launch_fix = null
	route_v = []
	safe_pending = {}
	hud_hp = int(st["home_hp"])
	board.setup({"w": L8Rules.W, "h": L8Rules.H, "values": leg["values"], "exploits": leg["exploits"]})
	board.set_scramble(scramble)
	lethal_on = int(st["home_hp"]) == 1
	board.set_lethal(lethal_on)
	heat_ghosts_k = -1
	board.clear_outcome()
	board.clear_response_preview()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	resp_prev = -2
	board.show_state(st, _empty_place())
	_begin_raid()


func _process(_delta: float) -> void:
	if phase == Phase.BETWEEN and not safe_pending.is_empty():
		_work_safe()
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


func _cells_list(cs: Array) -> String:
	var parts := PackedStringArray()
	for c: Variant in cs:
		parts.append(_cell_name(c))
	return ", ".join(parts)


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


## The one-line breakdown of the leg value: bank, districts, exploits, HOME (15 each), Heat (with its bands).
func _parts_text(s: Dictionary) -> String:
	if s.is_empty():
		return ""
	var sp: Dictionary = L8Rules.score_parts(leg, s)
	if bool(sp["breach"]):
		return "a breach leaves no score"
	return "bank %d + districts %d + exploits %d - HOME %d (%d each) - Heat %s (bands %d)" % [int(sp["bank"]),
		int(sp["cells"]), int(sp["exploits"]), int(sp["home_loss"]), L8Rules.HOME_LOSS_COST,
		_num(float(sp["heat_carry"])), int(sp["heat_bands"])]


func _status_of(s: Dictionary, c: Variant) -> String:
	return String((s["owned"] as Dictionary).get(c, "NEUTRAL"))


## A short reading of touches: "2 hit, 1 block, HOME -1" or "untouched".
func _sum(touches: Array) -> String:
	var hit := 0
	var blk := 0
	var home := 0
	var sh := 0
	for e: Array in touches:
		var k := String(e[1])
		if k == "hit":
			hit += 1
		elif k == "block":
			blk += 1
		elif k == "home":
			home += 1
		elif k == "shielded":
			sh += 1
	if hit + blk + home + sh == 0:
		return "untouched"
	var parts := PackedStringArray()
	if hit > 0:
		parts.append("%d hit" % hit)
	if blk > 0:
		parts.append("%d block%s" % [blk, "" if blk == 1 else "s"])
	if home > 0:
		parts.append("HOME -%d" % home)
	if sh > 0:
		parts.append("HOME shielded")
	return ", ".join(parts)


## The key that decides "same outcome": the same touches and the same tier.
func _okey(touches: Array, tier: String) -> String:
	return "%s|%s" % [str(touches), tier]


func _worse(a: String, b: String) -> String:
	return a if int(TIER_RANK.get(a, 0)) >= int(TIER_RANK.get(b, 0)) else b


func _hunt_street(h: int) -> int:
	return int((leg["raids"][raid]["hunter_cands"] as Array)[h])


## True when HOME drops below hp in some outcome.
func _any_loss(outs: Array, hp: int) -> bool:
	for ov: Variant in outs:
		var o: Dictionary = ov
		if int((o["state"] as Dictionary)["home_hp"]) < hp:
			return true
	return false


func _resp_label(r: Array, sentries: Dictionary) -> String:
	if r.is_empty():
		return "?"
	var head := String(r[0])
	if head == "HOLD":
		return "HOLD"
	if head == "JAM":
		return "JAM the hunter"
	if head == "DEPLOY":
		return "DEPLOY %s > %s" % [_tname(String(r[1])), _cell_name(r[2])]
	if head == "SACRIFICE":
		return "SACRIFICE %s" % _cell_name(r[1])
	var t := String(sentries.get(r[1], "?"))
	return "MOVE %s %s > %s" % [_tname(t), _cell_name(r[1]), _cell_name(r[2])]


## A placement in words: "DRONE on NOR 0, NETRUNNER on MID 1, ghost on HOME".
func _place_text(p: Dictionary) -> String:
	var parts := PackedStringArray()
	var sd: Dictionary = p.get("sentries", {})
	for c: Vector2i in L8Rules.sorted_cells(sd):
		parts.append("%s on %s" % [_tname(String(sd[c])), _cell_name(c)])
	var g: Variant = p.get("ghost")
	if _is_home(g):
		parts.append("ghost on HOME")
	elif typeof(g) == TYPE_VECTOR2I:
		parts.append("ghost on " + _cell_name(g))
	if parts.is_empty():
		return "no sentries, no ghost"
	return ", ".join(parts)


func _placed(t: String) -> int:
	var n := 0
	var sd: Dictionary = place.get("sentries", {})
	for c: Variant in sd:
		if String(sd[c]) == t:
			n += 1
	return n


func _placed_total() -> int:
	return (place.get("sentries", {}) as Dictionary).size()


func _count_type(sd: Dictionary, t: String) -> int:
	var n := 0
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


## A stable hash of a state (its JSON form), for the verdict caches.
func _state_hash(s: Dictionary) -> int:
	return str(L8Rules.state_to_json(s)).hash()


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


func _t(p: Vector2, text: String, size: int = TXT, col: Color = INK) -> void:
	ui.draw_string(font, p + Vector2(0.0, font.get_ascent(size)), _scr(text), HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _tw(text: String, size: int) -> float:
	return font.get_string_size(_scr(text), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


func _tc(center: Vector2, text: String, size: int = TXT, col: Color = INK) -> void:
	_t(center - Vector2(_tw(text, size) * 0.5, font.get_height(size) * 0.5), text, size, col)


func _tr(p: Vector2, text: String, size: int = TXT, col: Color = INK) -> void:
	_t(Vector2(p.x - _tw(text, size), p.y), text, size, col)


## text cut to fit maxw px (with "..."), so nothing in the panel clips.
func _fit(text: String, size: int, maxw: float) -> String:
	if _tw(text, size) <= maxw:
		return text
	var s := text
	while s.length() > 1 and _tw(s + "...", size) > maxw:
		s = s.substr(0, s.length() - 1)
	return s.strip_edges() + "..."


## Left-aligned text cut to fit up to the panel's right edge (or right_x).
func _tf(p: Vector2, text: String, size: int = TXT, col: Color = INK, right_x: float = PANEL_X + PANEL_W - PAD) -> void:
	_t(p, _fit(text, size, right_x - p.x), size, col)


func _box(r: Rect2, edge: Color, fill: Color, w: float = 2.0) -> void:
	ui.draw_rect(r, fill)
	ui.draw_rect(r, edge, false, w)


func _btn(r: Rect2, label: String, id: String, on: bool = true, sel: bool = false, size: int = 14) -> void:
	var hot := on and r.has_point(mouse)
	_box(r, (AMBER if sel else (INK if hot else EDGE)) if on else EDGE.darkened(0.4), PANEL_HI if (sel or hot) else PANEL)
	_tc(r.get_center(), _fit(label, size, r.size.x - 10.0), size, INK if on else DIM)
	if on:
		hits.append({"rect": r, "id": id})


func _head(title: String, todo: String) -> float:
	var x := PANEL_X + PAD
	_t(Vector2(x, HUD_H + 10.0), title, 20, AMBER)
	_tf(Vector2(x, HUD_H + 38.0), todo, TXT, INK)
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


## A wrench pictogram (the NORMAL perk: free repair).
func _wrench_icon(c: Vector2, col: Color) -> void:
	ui.draw_line(c + Vector2(-6.0, 6.0), c + Vector2(3.0, -3.0), col, 3.0)
	ui.draw_arc(c + Vector2(4.0, -4.0), 3.5, 0.0, TAU, 12, col, 2.0)


## A pennant flag pictogram; the HOT perk draws two (two captures next raid).
func _flag_icon(c: Vector2, col: Color) -> void:
	ui.draw_line(c + Vector2(0.0, 7.0), c + Vector2(0.0, -7.0), col, 1.5)
	ui.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -7.0), c + Vector2(8.0, -4.0), c + Vector2(0.0, -1.0)]), col)


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


## A flame pictogram (intensity cards): an outer flame in Heat orange with a yellow core.
func _flame(c: Vector2, r: float) -> void:
	ui.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -r * 1.35), c + Vector2(r * 0.5, -r * 0.45),
		c + Vector2(r * 0.75, r * 0.3), c + Vector2(r * 0.4, r * 0.85), c + Vector2(-r * 0.4, r * 0.85),
		c + Vector2(-r * 0.75, r * 0.3), c + Vector2(-r * 0.35, -r * 0.5)]), HEAT_COL)
	ui.draw_circle(c + Vector2(0.0, r * 0.35), r * 0.38, YELLOW)


## Small beam icons in a row: a short streak and the type's shape, one per known beam (up to k).
func _beam_icons(p: Vector2, types: Array, k: int) -> float:
	var x := p.x
	for j in range(mini(k, types.size())):
		var t := String(types[j])
		var col: Color = TYPE_COLOR.get(t, GREY)
		var c := Vector2(x, p.y)
		ui.draw_line(c + Vector2(-6.0, 0.0), c + Vector2(1.0, 0.0), col, 2.0)
		_glyph(c + Vector2(4.5, 0.0), t, 4.5, col)
		x += 17.0
	return x


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


## A small right-aligned tier stamp: mark then name. BREACHED sits white on black inside a red border. Returns its left x.
func _tier_tag(right: Vector2, tier: String, size: int = TXT) -> float:
	var col := _tier_col(tier)
	var tw := _tw(tier, size)
	var h := font.get_height(size)
	var gr := float(size) * 0.45
	var gx := right.x - tw - gr - 6.0
	var left := gx - gr - 4.0
	if tier == "BREACHED":
		var r := Rect2(left, right.y - 2.0, right.x - left + 4.0, h + 4.0)
		ui.draw_rect(r, BLACK)
		ui.draw_rect(r, RED, false, 2.0)
	_tier_glyph(Vector2(gx, right.y + h * 0.5), tier, gr, col)
	_tr(right, tier, size, col)
	return left


## Two tier stamps "A / B" right-aligned at right (hunter street A, then B). Returns the left x of the pair.
func _tier_pair(right: Vector2, ta: String, tb: String, size: int = TXT) -> float:
	var lb := _tier_tag(right, tb, size)
	_tc(Vector2(lb - 5.0, right.y + font.get_height(size) * 0.5), "/", size, DIM)
	return _tier_tag(Vector2(lb - 12.0, right.y), ta, size)


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


## A right-aligned between verdict: a shield and HOLDABLE, a skull and LOST, or a dim ring while still checking.
func _verdict_mark(right: Vector2, v: int, size: int = TXT) -> void:
	var text := "HOLDABLE" if v == 1 else ("LOST" if v == 0 else "checking")
	var col := HOLDS_COL if v == 1 else (RED if v == 0 else DIM)
	var tw := _tw(text, size)
	var h := font.get_height(size)
	var gc := Vector2(right.x - tw - 9.0, right.y + h * 0.5)
	if v == 1:
		_tier_glyph(gc, "HOLDS", 5.5, col)
	elif v == 0:
		_skull(gc, 5.5, col, BLACK)
	else:
		ui.draw_arc(gc, 4.0, 0.0, TAU, 12, col, 1.5)
	_tr(right, text, size, col)


## The verdict as a mark only (build buttons): shield, skull, or a dim ring while still checking.
func _verdict_dot(c: Vector2, v: int) -> void:
	if v == 1:
		_tier_glyph(c, "HOLDS", 6.0, HOLDS_COL)
	elif v == 0:
		_skull(c, 6.0, RED, BLACK)
	else:
		ui.draw_arc(c, 4.0, 0.0, TAU, 12, DIM, 1.5)


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
	if busy or phase == Phase.PLAY or phase == Phase.REVEAL or phase == Phase.DECAY or phase == Phase.FALL:
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
				KEY_H:
					_select_hunt(1 - sel_hunt)
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
				KEY_1:
					_arm_deploy("D")
				KEY_2:
					_arm_deploy("N")
				KEY_3:
					_arm_deploy("E")
				KEY_UP:
					_move_resp_sel(-1)
				KEY_DOWN:
					_move_resp_sel(1)
				KEY_ESCAPE:
					redeploy_from = null
					deploy_type = ""
					_build_resp_rows()
					_highlight_sources()
			if enter:
				if resp_sel >= 0 and resp_sel < resp_rows.size():
					_act("resp:%d" % resp_sel)
				else:
					status_msg = "Pick a row (Up/Down, then Enter), or press H to hold."
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
	elif id.begins_with("hunt:"):
		_select_hunt(int(id.substr(5)))
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
	elif id.begins_with("dep:"):
		_arm_deploy(id.substr(4))
	elif id.begins_with("rep:"):
		var i := int(id.substr(4))
		if i == 0:
			_clear_repair()
		else:
			var downs := _down_cells()
			if i - 1 < downs.size():
				_between_click(downs[i - 1])
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
## Its sentry goes back to the reserve. CAPTURE then works on the decayed state.
func _begin_raid() -> void:
	decay_lines = PackedStringArray()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	route_v = []
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
					line += " (its %s returns to the reserve)" % _tname(String(sent[cv]))
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
		_taken_icon(Vector2(x + 7.0, y + 9.0))
		_tf(Vector2(x + 22.0, y), ln, TXT, COBALT_HOT)
		y += 22.0
	y += 8.0
	_tf(Vector2(x, y), "A DOWN district not repaired between raids is lost.", TXT, DIM)


# ---------------------------------------------------------------- CAPTURE
## CAPTURE claims capture_slots cells (2 after a HOT between step, L13 R5), each from the updated state's options, then
## clears extra_capture (L8Rules.end_capture).
func _enter_capture() -> void:
	board.reset_playout()
	board.clear_paths()
	board.clear_outcome()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	cap_cells = []
	cap_slots = L8Rules.capture_slots(st)
	board.show_state(st, {"sentries": st["sentries"], "ghost": null})
	_capture_step()


func _capture_step() -> void:
	cap_opts = L8Rules.capture_options(leg, st)
	if cap_opts.is_empty() or cap_cells.size() >= cap_slots:
		if cap_opts.is_empty() and cap_cells.is_empty():
			status_msg = "No district can be captured: the raid goes on."
		elif cap_opts.is_empty() and cap_cells.size() < cap_slots:
			status_msg = "No second district can be captured: the raid goes on."
		st = L8Rules.end_capture(st)
		_enter_plan()
		return
	phase = Phase.CAPTURE
	board.show_state(st, {"sentries": st["sentries"], "ghost": null})
	board.clear_highlight()
	board.highlight_kind(cap_opts, "capture")


func _do_capture(c: Variant) -> void:
	if phase != Phase.CAPTURE:
		return
	if typeof(c) != TYPE_VECTOR2I or not cap_opts.has(c):
		status_msg = "Pick a glowing district: next to one of yours, or in column 0."
		return
	st = L8Rules.capture(leg, st, c)
	cap_cells.append(c)
	_capture_step()


func _draw_capture() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var todo := "Claim one glowing district (it stands in for a netrun)."
	if cap_slots > 1:
		todo = "Claim %d of %d: the HOT run brings two captures." % [cap_cells.size() + 1, cap_slots]
	var y := _head("CAPTURE  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], todo)
	_tf(Vector2(x, y), "Next to one of your districts, or in column 0 by HOME.", TXT, DIM)
	y += 22.0
	if not cap_cells.is_empty():
		_tf(Vector2(x, y), "Claimed: " + _cells_list(cap_cells), TXT, ACID)
		y += 20.0
	y += 4.0
	var vals: Dictionary = leg["values"]
	var ex: Array = leg["exploits"]
	for i in range(cap_opts.size()):
		var c: Vector2i = cap_opts[i]
		var r := Rect2(x, y, w, 30.0)
		var hot := r.has_point(mouse)
		_box(r, AMBER if hot else EDGE, PANEL_HI if hot else PANEL)
		_t(r.position + Vector2(10.0, 6.0), _cell_name(c), 14, INK)
		_t(r.position + Vector2(130.0, 6.0), "value %d" % int(vals[c]), 14, AMBER)
		if ex.has(c):
			_key_icon(r.position + Vector2(260.0, 15.0), ACID)
			_t(r.position + Vector2(276.0, 7.0), "EXPLOIT", TXT, ACID)
		hits.append({"rect": r, "id": "cap:%d" % i})
		y += 34.0
	y += 8.0
	y = _draw_kit(y, false)
	if not decay_lines.is_empty():
		y += 6.0
		for ln: String in decay_lines:
			_taken_icon(Vector2(x + 7.0, y + 8.0))
			_tf(Vector2(x + 22.0, y), ln, TXT, COBALT_HOT)
			y += 20.0
	for cv: Variant in cap_opts:
		var c: Vector2i = cv
		var p := _screen(c)
		_tc(p + Vector2(0.0, -50.0), str(int(vals[c])), 16, AMBER)
		if ex.has(c):
			_tc(p + Vector2(0.0, -32.0), "KEY", TXT, ACID)


## The sentry pool and the kit. In PLAN and FORECAST it is the tray: placed n/MAX_PLACED slots, and the reserve by type.
func _draw_kit(y: float, planning: bool) -> float:
	var x := PANEL_X + PAD
	var pool: Dictionary = st["pool"]
	var kit: Dictionary = st["kit"]
	if planning:
		var n := _placed_total()
		var cap: int = L8Rules.MAX_PLACED
		_t(Vector2(x, y), "PLACED", TXT, DIM)
		var sd: Dictionary = place["sentries"]
		var types: Array = []
		for c: Vector2i in L8Rules.sorted_cells(sd):
			types.append(String(sd[c]))
		for s in range(cap):
			var sr := Rect2(x + 62.0 + s * 26.0, y - 1.0, 22.0, 18.0)
			_box(sr, AMBER if s < types.size() else EDGE, PANEL, 1.5)
			if s < types.size():
				var tt: String = types[s]
				_glyph(sr.get_center(), tt, 6.0, TYPE_COLOR.get(tt, GREY))
		_t(Vector2(x + 66.0 + cap * 26.0, y), "%d/%d" % [n, cap], TXT, AMBER if n >= cap else INK)
		var rx := x + 176.0
		_t(Vector2(rx, y), "RESERVE", TXT, DIM)
		for i in range(3):
			var t: String = L8Rules.TYPES[i]
			var gx := rx + 72.0 + i * 46.0
			var r := maxi(0, int(pool[t]) - _placed(t))
			_glyph(Vector2(gx, y + 9.0), t, 6.5, TYPE_COLOR[t] if r > 0 else DIM)
			_t(Vector2(gx + 9.0, y), "x%d" % r, TXT, INK if r > 0 else DIM)
	else:
		_t(Vector2(x, y), "SENTRIES", TXT, DIM)
		for i in range(3):
			var t: String = L8Rules.TYPES[i]
			var gx := x + 100.0 + i * 96.0
			_glyph(Vector2(gx, y + 9.0), t, 8.0, TYPE_COLOR[t])
			_t(Vector2(gx + 12.0, y), "x%d" % int(pool[t]), TXT, INK)
	y += 22.0
	_t(Vector2(x, y), "KIT", TXT, DIM)
	_ghost_icon(Vector2(x + 108.0, y + 9.0), 7.0, GOLD)
	_t(Vector2(x + 120.0, y), "GHOST %d" % int(kit["ghost"]), TXT, GOLD)
	_t(Vector2(x + 220.0, y), "SPOOF %d" % int(kit["spoof"]), TXT, ACID)
	return y + 26.0


# ---------------------------------------------------------------- PLAN
func _enter_plan() -> void:
	var sd := {}
	var prev: Dictionary = st["sentries"]
	var pool: Dictionary = st["pool"]
	var counts := {"D": 0, "N": 0, "E": 0}
	for c: Vector2i in L8Rules.sorted_cells(prev):
		if sd.size() >= L8Rules.MAX_PLACED:
			break
		var t := String(prev[c])
		if L8Rules.is_live(st, c) and counts.has(t) and int(counts[t]) < int(pool[t]):
			sd[c] = t
			counts[t] = int(counts[t]) + 1
	place = {"sentries": sd, "ghost": null}
	undo = []
	tool = ""
	fc = []
	fc_best = []
	fric = 0
	launch_armed = false
	launch_fix = null
	fix_kind = ""
	route_v = []
	sel_route = 0
	sel_hunt = 0
	phase = Phase.PLAN
	board.clear_highlight()
	board.hide_route_verdicts()
	_plan_view()


## Redraw the plan on the board: the state and placement, the planned paths, the two sealed hunter streets and the
## selected route's HOLD outcome (on the selected hunter street).
func _plan_view() -> void:
	board.show_state(st, place)
	_show_plan_paths()
	_show_hunter()
	_refresh_outcome()


## Both sealed hunter streets as hound lanes on the board.
func _show_hunter() -> void:
	var r_now: Dictionary = leg["raids"][raid]
	board.show_hunter_cands((r_now["hunter_cands"] as Array).duplicate(), String(r_now["hunter_type"]))


func _select_route(k: int) -> void:
	if phase != Phase.PLAN and phase != Phase.FORECAST:
		return
	var n: int = (leg["raids"][raid]["cands"] as Array).size()
	if k < 0 or k >= n:
		return
	sel_route = k
	_show_plan_paths()
	_refresh_outcome()


func _select_hunt(h: int) -> void:
	if phase != Phase.PLAN and phase != Phase.FORECAST:
		return
	if h < 0 or h >= L8Rules.HUNTER_CANDS:
		return
	sel_hunt = h
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


## The board outcome of sealed route k and hunter street sel_hunt with HOLD, from L8Rules.trace. The hunter's lanes are
## drawn by show_hunter_cands, so the outcome carries no hunter line.
func _outcome(k: int) -> Dictionary:
	var r_now: Dictionary = leg["raids"][raid]
	var tr: Array = L8Rules.trace(leg, raid, st, k, sel_hunt, place, ["HOLD"])
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
	return {"hits": hit_cells, "blocks": blocks, "block_types": btypes, "home": home, "hunter": null}


func _refresh_outcome() -> void:
	sel_hold = {}
	if (phase != Phase.PLAN and phase != Phase.FORECAST) or L8Rules.check_place(st, place) != "":
		board.clear_outcome()
		return
	board.show_outcome(_outcome(sel_route))
	var res := L8Rules.resolve(leg, raid, st, sel_route, sel_hunt, place, ["HOLD"])
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


## Leave FORECAST for PLAN: the route verdict stamps go and the launch friction is disarmed.
func _back_to_plan() -> void:
	if phase == Phase.FORECAST:
		phase = Phase.PLAN
		fc = []
		fc_best = []
		fric = 0
		launch_armed = false
		launch_fix = null
		fix_kind = ""
		route_v = []
		board.hide_route_verdicts()


## A sentry tool places, moves (when the type's pool is all placed) or lifts a sentry. At most MAX_PLACED go on the
## board: a third new sentry is refused with a status line.
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
		if cur == tool:
			_push()
			sd.erase(c)
		else:
			if pool <= 0:
				status_msg = "No %s sentry in the pool." % _tname(tool)
				return
			var moving := _placed(tool) >= pool
			if cur == "" and not moving and sd.size() >= L8Rules.MAX_PLACED:
				status_msg = "At most %d sentries go on the board: lift one first (the rest stays in reserve)." % L8Rules.MAX_PLACED
				return
			_push()
			if moving:
				for k: Vector2i in L8Rules.sorted_cells(sd):
					if String(sd[k]) == tool:
						sd.erase(k)
						break
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
	var right := PANEL_X + PANEL_W - PAD
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
			_ghost_icon(r.position + Vector2(15.0, 22.0), 8.0, GOLD if on else DIM)
			_t(r.position + Vector2(28.0, 4.0), _fit("GHOST", TXT, bw - 31.0), TXT, INK if on else DIM)
			_t(r.position + Vector2(28.0, 22.0), _fit("[G] +%d" % L8Rules.GHOST_HEAT, TXT, bw - 31.0), TXT, DIM)
		else:
			_glyph(r.position + Vector2(15.0, 22.0), t, 9.0, TYPE_COLOR[t])
			_t(r.position + Vector2(28.0, 4.0), _fit(_tname(t).substr(0, 6), TXT, bw - 31.0), TXT, INK)
			_t(r.position + Vector2(28.0, 22.0), _fit("[%d] %d/%d" % [i + 1, _placed(t), int(st["pool"][t])], TXT, bw - 31.0), TXT, DIM)
		if on:
			hits.append({"rect": r, "id": "tool:" + t})
	y += 52.0
	_tf(Vector2(x, y), "A sentry blocks its own type. At most %d placed." % L8Rules.MAX_PLACED, TXT, DIM)
	y += 18.0
	_tf(Vector2(x, y), "The ghost lets every beam pass its district or HOME.", TXT, DIM)
	y += 26.0
	y = _draw_beam_info(y)
	if not sel_hold.is_empty():
		y += 4.0
		_tf(Vector2(x, y), "ON THE BOARD: %s, hunter %s, HOLD  [Q W E, H]" % [L8Rules.ROUTE_NAMES[sel_route],
			HUNT_KEY[sel_hunt]], TXT, DIM)
		y += 19.0
		var left := _tier_tag(Vector2(right, y), String(sel_hold["tier"]))
		_tf(Vector2(x, y), "%s   HOME %d/%d" % [_sum(sel_hold["touches"]), int(sel_hold["home_hp"]), L8Rules.HOME_HP],
			TXT, INK, left - 8.0)
		y += 22.0
	var err := L8Rules.check_place(st, place)
	if err != "":
		_tf(Vector2(x, y + 4.0), "Placement: " + err, TXT, RED)
	var by := LEGEND_Y - 58.0
	_btn(Rect2(x, by, 110.0, 42.0), "UNDO [Z]", "undo", not undo.is_empty())
	_btn(Rect2(x + 122.0, by, w - 122.0, 42.0), "FORECAST [Enter]", "next", err == "", false, 16)


## This raid's beams for the plan: beam 1, the extras the launch Heat brings, the sealed routes, the two sealed hunter
## streets.
func _draw_beam_info(y: float) -> float:
	var x := PANEL_X + PAD
	var r_now: Dictionary = leg["raids"][raid]
	var lh := L8Rules.launch_heat(st, place)
	var n := L8Rules.extra_count(lh)
	_t(Vector2(x, y), "THIS RAID  (launch Heat %d)" % lh, TXT, DIM)
	y += 20.0
	y = _beam_row(y, "BEAM 1", r_now["b1"], true, "")
	y = _beam_row(y, "EXTRA 1", r_now["extra1"], n >= 1, "Heat %d" % L8Rules.EXTRA_AT)
	y = _beam_row(y, "EXTRA 2", r_now["extra2"], n >= 2, "Heat %d" % L8Rules.STRONG_AT)
	_t(Vector2(x, y), "SEALED", TXT, INK)
	var cands: Array = r_now["cands"]
	for k in range(cands.size()):
		var t := String(cands[k]["type"])
		var gx := x + 84.0 + k * 102.0
		var sr := Rect2(gx - 12.0, y - 3.0, 96.0, 21.0)
		if k == sel_route:
			_box(sr, AMBER, PANEL_HI, 1.5)
		elif sr.has_point(mouse):
			_box(sr, INK, PANEL, 1.0)
		_glyph(Vector2(gx, y + 8.0), t, 7.0, TYPE_COLOR[t])
		_t(Vector2(gx + 10.0, y), _fit("%s [%s]" % [L8Rules.ROUTE_NAMES[k], ROUTE_KEY[k]], TXT, 72.0), TXT, INK)
		hits.append({"rect": sr, "id": "route:%d" % k})
	y += 20.0
	_tf(Vector2(x + 84.0, y), "one of these three convoys comes", TXT, DIM)
	y += 22.0
	var ht := String(r_now["hunter_type"])
	var hc: Array = r_now["hunter_cands"]
	_hound_icon(Vector2(x + 6.0, y + 8.0))
	_t(Vector2(x + 18.0, y), "HUNT", TXT, COBALT_HOT)
	for h in range(hc.size()):
		var gx := x + 84.0 + h * 102.0
		var sr := Rect2(gx - 12.0, y - 3.0, 96.0, 21.0)
		if h == sel_hunt:
			_box(sr, AMBER, PANEL_HI, 1.5)
		elif sr.has_point(mouse):
			_box(sr, INK, PANEL, 1.0)
		_t(Vector2(gx - 4.0, y), _fit("%s: street %d" % [HUNT_KEY[h], int(hc[h])], TXT, 84.0), TXT, INK)
		hits.append({"rect": sr, "id": "hunt:%d" % h})
	y += 20.0
	_glyph(Vector2(x + 90.0, y + 9.0), ht, 6.0, TYPE_COLOR[ht])
	_tf(Vector2(x + 100.0, y), "%s hound runs one of them  [H]" % _tname(ht), TXT, DIM)
	return y + 22.0


func _beam_row(y: float, label: String, ln: Dictionary, live: bool, note: String) -> float:
	var x := PANEL_X + PAD
	var right := PANEL_X + PANEL_W - PAD
	var t := String(ln["type"])
	var col := INK if live else DIM
	_t(Vector2(x, y), label, TXT, col)
	_glyph(Vector2(x + 92.0, y + 9.0), t, 7.0, TYPE_COLOR[t] if live else DIM)
	var lim := right
	if not live:
		var off := "off (%s)" % note
		_tr(Vector2(right, y), off, TXT, DIM)
		lim = right - _tw(off, TXT) - 8.0
	_tf(Vector2(x + 104.0, y), "%s, %s" % [_tname(t), _line_name(ln)], TXT, col, lim)
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
		var ln: Dictionary = (cands[k] as Dictionary).duplicate()
		ln["cand"] = k
		lines.append(ln)
		if k == sel_route:
			selected = lines.size() - 1
	board.show_paths(lines, selected)


## The board's route verdicts: each sealed route's worse HOLD tier over the two hunter streets (both kept in "tiers").
func _route_verdicts() -> Array:
	var out: Array = []
	var cands: Array = leg["raids"][raid]["cands"]
	for fv: Variant in fc:
		var f: Dictionary = fv
		var k := int(f["cand"])
		var outs: Array = f["outcomes"]
		var ta := String(outs[0]["tier"])
		var tb := String(outs[outs.size() - 1]["tier"])
		out.append({"route": int(cands[k]["index"]), "tier": _worse(ta, tb), "tiers": [ta, tb]})
	return out


## The greedy response for sealed candidate k (mean over the hunter streets), with a tier per street; {} when none.
func _best_view(k: int, opts: Array) -> Dictionary:
	var midleg := raid < L8Rules.RAIDS - 1
	var b := L8Rules._best_for(leg, raid, st, k, place, opts, midleg)
	if b.is_empty():
		return {}
	var outs: Array = []
	for ov: Variant in b["outcomes"]:
		var o: Dictionary = ov
		outs.append({"state": o["state"], "touches": o["touches"], "tier": L8Rules.tier(st, o["state"], o["touches"])})
	return {"response": b["response"], "outcomes": outs}


## Graduated friction: 2 every route breaches, 1 HOME drops on every route (on some hunter street, even with the best
## response), 3 HOME is at 1, 0 none.
func _friction() -> int:
	var hp := int(st["home_hp"])
	var all_loss := not fc_best.is_empty()
	var all_breach := all_loss
	for bv: Variant in fc_best:
		var b: Dictionary = bv
		if b.is_empty():
			continue
		var loss := false
		var breach := false
		for ov: Variant in b["outcomes"]:
			var h := int((ov as Dictionary)["state"]["home_hp"])
			if h < hp:
				loss = true
			if h <= 0:
				breach = true
		if not loss:
			all_loss = false
		if not breach:
			all_breach = false
	if all_breach:
		return 2
	if all_loss:
		return 1
	if hp == 1:
		return 3
	return 0


## A placement's grade with the best response per sealed candidate over both hunter streets: 2 keeps HOME everywhere,
## 1 avoids a breach everywhere, 0 breaches somewhere.
func _plan_grade(p: Dictionary) -> int:
	var hp := int(st["home_hp"])
	var midleg := raid < L8Rules.RAIDS - 1
	var opts := L8Rules.response_options(leg, raid, st, 0, p)
	var grade := 2
	for k in range(L8Rules.CANDIDATES):
		var b := L8Rules._best_for(leg, raid, st, k, p, opts, midleg)
		if b.is_empty():
			return 0
		for ov: Variant in b["outcomes"]:
			var h := int((ov as Dictionary)["state"]["home_hp"])
			if h <= 0:
				return 0
			if h < hp:
				grade = 1
	return grade


## The current plan's grade, read from fc_best.
func _cur_grade() -> int:
	var hp := int(st["home_hp"])
	var grade := 2
	for bv: Variant in fc_best:
		var b: Dictionary = bv
		if b.is_empty():
			return 0
		for ov: Variant in b["outcomes"]:
			var h := int((ov as Dictionary)["state"]["home_hp"])
			if h <= 0:
				return 0
			if h < hp:
				grade = 1
	return grade


## The friction's fix: the first placement (L8Rules.placements order) from the post-capture state that keeps HOME on
## every route and street ("keep"), else the first that avoids a breach ("safe"). Cached per (leg, raid, state hash).
func _find_fix() -> void:
	var key := "%d|%d|%d" % [leg_seed, raid, _state_hash(st)]
	if not fix_cache.has(key):
		var keep: Variant = null
		var safe: Variant = null
		for pv: Variant in L8Rules.placements(leg, st):
			var p: Dictionary = pv
			var g := _plan_grade(p)
			if g == 2:
				keep = p
				break
			if g == 1 and _none(safe):
				safe = p
		fix_cache[key] = {"keep": keep, "safe": safe}
	var e: Dictionary = fix_cache[key]
	launch_fix = null
	fix_kind = ""
	var cur := _cur_grade()
	if typeof(e["keep"]) == TYPE_DICTIONARY and cur < 2:
		launch_fix = e["keep"]
		fix_kind = "keep"
	elif typeof(e["safe"]) == TYPE_DICTIONARY and cur < 1:
		launch_fix = e["safe"]
		fix_kind = "safe"


func _enter_forecast() -> void:
	if phase != Phase.PLAN:
		return
	var err := L8Rules.check_place(st, place)
	if err != "":
		status_msg = "Placement: " + err
		return
	fc = L8Rules.forecast(leg, raid, st, place)
	if fc.is_empty():
		status_msg = "The forecast failed for this placement."
		return
	var opts := L8Rules.response_options(leg, raid, st, 0, place)
	fc_best = []
	for fv: Variant in fc:
		fc_best.append(_best_view(int((fv as Dictionary)["cand"]), opts))
	fric = _friction()
	launch_armed = false
	launch_fix = null
	fix_kind = ""
	if fric > 0:
		_find_fix()
	tool = ""
	board.clear_highlight()
	phase = Phase.FORECAST
	_show_plan_paths()
	_show_hunter()
	_refresh_outcome()
	route_v = _route_verdicts()
	board.show_route_verdicts(route_v)


func _friction_text() -> String:
	match fric:
		2:
			return FRICTION_BREACH
		1:
			return FRICTION_LOSS
		3:
			return FRICTION_LAST
	return ""


func _draw_forecast() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("FORECAST  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Each sealed route with HOLD, per hunter street. Q W E, H.")
	y = _draw_kit(y, true)
	var r_now: Dictionary = leg["raids"][raid]
	var cands: Array = r_now["cands"]
	var hp := int(st["home_hp"])
	for i in range(fc.size()):
		var f: Dictionary = fc[i]
		var k := int(f["cand"])
		var t := String(cands[k]["type"])
		var outs: Array = f["outcomes"]
		var r := Rect2(x, y, w, 84.0)
		var sel := k == sel_route
		var hot := r.has_point(mouse)
		_box(r, AMBER if sel else (INK if hot else EDGE), PANEL_HI if sel else PANEL)
		hits.append({"rect": r, "id": "route:%d" % k})
		_glyph(r.position + Vector2(16.0, 13.0), t, 9.0, TYPE_COLOR[t])
		var tag := "[%s]%s" % [ROUTE_KEY[k], "  on the board" if sel else ""]
		_tr(Vector2(r.end.x - 10.0, r.position.y + 4.0), tag, TXT, AMBER if sel else DIM)
		_tf(r.position + Vector2(32.0, 4.0), "%s ROUTE  %s" % [L8Rules.ROUTE_NAMES[k], _tname(t)], TXT, INK,
			r.end.x - 18.0 - _tw(tag, TXT))
		var yy := r.position.y + 23.0
		for h in range(outs.size()):
			var o: Dictionary = outs[h]
			var on_board := sel and h == sel_hunt
			var left := _tier_tag(Vector2(r.end.x - 10.0, yy), String(o["tier"]))
			_t(Vector2(x + 10.0, yy), "if %s, st %d" % [HUNT_KEY[h], _hunt_street(h)], TXT, ACID if on_board else DIM)
			_tf(Vector2(x + 96.0, yy), _sum(o["touches"]), TXT, INK, left - 8.0)
			yy += 18.0
		var b: Dictionary = fc_best[i] if i < fc_best.size() else {}
		if b.is_empty():
			_tf(Vector2(x + 10.0, yy), "no response resolves", TXT, DIM)
		else:
			var br: Array = b["response"]
			var bo: Array = b["outcomes"]
			if String(br[0]) == "HOLD":
				if _any_loss(bo, hp):
					_tf(Vector2(x + 10.0, yy), "no response saves this route", TXT, RED, r.end.x - 10.0)
				else:
					_tf(Vector2(x + 10.0, yy), "best response: HOLD (keep the kit)", TXT, DIM, r.end.x - 10.0)
			else:
				var left := _tier_pair(Vector2(r.end.x - 10.0, yy), String(bo[0]["tier"]), String(bo[bo.size() - 1]["tier"]))
				_tf(Vector2(x + 10.0, yy), "best response: %s ->" % _resp_label(br, place["sentries"]), TXT, ACID, left - 8.0)
		y += 90.0
	var ht := String(r_now["hunter_type"])
	var hr := Rect2(x, y, w, 24.0)
	_box(hr, INK if hr.has_point(mouse) else EDGE, PANEL, 1.5)
	hits.append({"rect": hr, "id": "hunt:%d" % (1 - sel_hunt)})
	_hound_icon(hr.position + Vector2(12.0, 12.0))
	_glyph(hr.position + Vector2(30.0, 12.0), ht, 6.0, TYPE_COLOR[ht])
	_tf(hr.position + Vector2(42.0, 3.0), "HUNTER %s: A street %d or B street %d   [H] %s shown" % [_tname(ht),
		_hunt_street(0), _hunt_street(1), HUNT_KEY[sel_hunt]], TXT, COBALT_HOT, hr.end.x - 8.0)
	y += 30.0
	if fric > 0:
		var wr := Rect2(x, y, w, 24.0)
		ui.draw_rect(wr, BLACK)
		ui.draw_rect(wr, RED, false, 2.0)
		_skull(wr.position + Vector2(13.0, 12.0), 8.0, RED, BLACK)
		_tf(wr.position + Vector2(28.0, 4.0), _friction_text(), TXT, WHITE, wr.end.x - 6.0)
		y += 30.0
		var cur := _cur_grade()
		if typeof(launch_fix) == TYPE_DICTIONARY:
			var lead := "One fix (keeps HOME at %d/%d on every route):" % [hp, L8Rules.HOME_HP] if fix_kind == "keep" \
				else "One fix (no breach on any route):"
			_tf(Vector2(x, y), lead, TXT, ACID)
			y += 18.0
			_tf(Vector2(x + 10.0, y), _place_text(launch_fix), TXT, INK)
			y += 20.0
		elif cur == 2:
			_tf(Vector2(x, y), "This plan keeps HOME on every route.", TXT, ACID)
			y += 20.0
		else:
			_tf(Vector2(x, y), "No plan keeps HOME on every route this raid.", TXT, RED)
			y += 20.0
		if launch_armed:
			_tf(Vector2(x, y), "Enter again launches anyway; B or an edit goes back.", TXT, DIM)
		else:
			_tf(Vector2(x, y), "Launching needs a second Enter.", TXT, DIM)
	var by := LEGEND_Y - 58.0
	_btn(Rect2(x, by, 110.0, 42.0), "BACK [B]", "back")
	_btn(Rect2(x + 122.0, by, w - 122.0, 42.0), "LAUNCH ANYWAY [Enter]" if launch_armed else "LAUNCH [Enter]", "next",
		true, launch_armed, 16)


# ---------------------------------------------------------------- LAUNCH and playout
func _cue(kind: String, c: Vector2i, t: String, line: int) -> Dictionary:
	return {"kind": kind, "cell": c, "type": t, "line": line}


func _trace_kind(tr: Array, beam: String, c: Variant) -> String:
	for e: Array in tr:
		if String(e[0]) == beam and typeof(e[1]) == typeof(c) and e[1] == c:
			return String(e[2])
	return ""


## One line's cues: a step per cell until a block, hit cues where the trace hits, a home cue when the trace says home.
## A shielded HOME (SACRIFICE) is a block at our HQ: a shield flash, no integrity lost.
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
	if not stopped and bool(ln["home"]):
		var hk := _trace_kind(tr, beam, L8Rules.HOME)
		if hk == "home":
			out.append(_cue("home", Vector2i(-1, int(ln["index"])), t, id))
		elif hk == "shielded":
			out.append(_cue("block", Vector2i(-1, int(ln["index"])), t, id))
	return out


func _known_cues(tr: Array) -> Array:
	var cues: Array = _line_cues("beam1", rd["b1"], tr)
	var n := L8Rules.extra_count(heat_launch)
	if n >= 1:
		cues.append_array(_line_cues("extra1", rd["extra1"], tr))
	if n >= 2:
		cues.append_array(_line_cues("extra2", rd["extra2"], tr))
	return cues


## The hunter's cues on the revealed street: it starts at the street head and runs it, or is jammed there.
func _hunter_cues(tr: Array, resp: Array) -> Array:
	var cues: Array = []
	var ht := String(rd["hunter_type"])
	var hid: int = int(LINE_ID["hunter"])
	var head := Vector2i(_hunt_street(hunt), 0)
	if String(resp[0]) == "JAM":
		cues.append(_cue("jam", head, ht, hid))
	else:
		var hl: Variant = L8Rules.hunter_line(leg, raid, before, real, hunt, place, resp)
		if typeof(hl) == TYPE_DICTIONARY:
			cues.append(_cue("hunter_turn", head, ht, hid))
			cues.append_array(_line_cues("hunter", hl, tr))
	if tr.is_empty() and String(resp[0]) != "SACRIFICE":
		cues.append(_cue("evaded", Vector2i(1, 1), "D", -1))
	return cues


## Play a batch of cues; label "" takes no shot. The route verdicts (and the sealed hunter lanes before their reveal)
## are put back afterwards, so they stay through the launch.
func _play_batch(cues: Array, label: String) -> void:
	busy = true
	board.set_instant(instant)
	await board.play(cues, speed)
	busy = false
	_restore_launch_marks()
	if shots_dir != "" and label != "":
		await _shot(label)


func _restore_launch_marks() -> void:
	if not route_v.is_empty():
		board.show_route_verdicts(route_v)
	if not hunter_revealed:
		_show_hunter()


func _cand_view() -> Array:
	var out: Array = []
	var cands: Array = rd["cands"]
	for k in range(cands.size()):
		out.append({"route": k, "type": String(cands[k]["type"])})
	return out


## LAUNCH. With friction (see _friction), the first call only arms it; the second call launches.
func _launch() -> void:
	if busy or phase != Phase.FORECAST:
		return
	var err := L8Rules.check_place(st, place)
	if err != "":
		status_msg = "Placement: " + err
		return
	if fric > 0 and not launch_armed:
		launch_armed = true
		status_msg = _friction_text()
		return
	launch_armed = false
	before = L8Rules.copy_state(st)
	rd = leg["raids"][raid]
	real = int(rd["real"])
	hunt = int(rd["hunter_real"])
	hunter_revealed = false
	cur_resp = ["HOLD"]
	heat_launch = L8Rules.launch_heat(st, place)
	hud_hp = int(st["home_hp"])
	var hold_tr := L8Rules.trace(leg, raid, st, real, hunt, place, ["HOLD"])
	known_tr = []
	for e: Array in hold_tr:
		if String(e[0]) in ["beam1", "extra1", "extra2"]:
			known_tr.append(e)
	board.clear_highlight()
	board.clear_outcome()
	board.clear_paths()
	board.show_candidates(_cand_view(), -1)
	board.show_state(st, place)
	_restore_launch_marks()
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
		"reveal", "sealed":
			if known:
				return "done"
			return "now" if b == "sealed" else "later"
	return "now" if b == "hunter" else "done"


func _draw_play() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("LAUNCH  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "The raid runs. 1 2 4 set the speed, I toggles instant.")
	_tf(Vector2(x, y), "Launch Heat %d: %d known beam%s" % [heat_launch, 1 + L8Rules.extra_count(heat_launch),
		"" if L8Rules.extra_count(heat_launch) == 0 else "s"], TXT, HEAT_COL)
	y += 24.0
	for bv: Variant in _beams_now():
		var b: String = bv
		var s := _beam_state(b)
		var col := INK if s == "now" else (DIM if s == "done" else LATER)
		var r := Rect2(x, y, w, 30.0)
		_box(r, AMBER if s == "now" else EDGE, PANEL_HI if s == "now" else PANEL)
		_t(r.position + Vector2(10.0, 6.0), String(BEAM_NAME[b]), TXT, col)
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
				if stage == "hreveal" or stage == "hunt":
					desc = "street %d (%s)%s" % [_hunt_street(hunt), HUNT_KEY[hunt],
						", jammed" if String(cur_resp[0]) == "JAM" else ""]
				else:
					desc = "street %d (A) or %d (B), sealed" % [_hunt_street(0), _hunt_street(1)]
		if t != "":
			_glyph(r.position + Vector2(100.0, 15.0), t, 7.0, TYPE_COLOR[t])
		else:
			_t(r.position + Vector2(96.0, 6.0), "?", TXT, COBALT_HOT)
		var stx := s.to_upper()
		_tr(Vector2(r.end.x - 8.0, r.position.y + 6.0), stx, TXT, AMBER if s == "now" else DIM)
		_tf(r.position + Vector2(114.0, 6.0), desc, TXT, col, r.end.x - 16.0 - _tw(stx, TXT))
		y += 34.0
	y += 6.0
	var labels: Array = [1.0, 2.0, 4.0]
	for i in range(3):
		var sp: float = labels[i]
		_btn(Rect2(x + i * 78.0, y, 70.0, 34.0), "%dx" % int(sp), "speed:%d" % int(sp), true, is_equal_approx(speed, sp))
	_btn(Rect2(x + 240.0, y, w - 240.0, 34.0), "INSTANT [I]", "instant", true, instant)
	y += 48.0
	if stage != "known":
		_t(Vector2(x, y), "THE KNOWN BEAMS TOUCHED", TXT, DIM)
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
		_tf(Vector2(x, y), "%s: %s" % [String(BEAM_NAME[b]), ", ".join(parts)], TXT, INK)
		y += 18.0
	if not any:
		_t(Vector2(x, y), "Nothing touched.", TXT, DIM)
		y += 18.0
	return y


# ---------------------------------------------------------------- RESPONSE
## Every legal response, resolved on both hunter streets (the street is still sealed): {response, outs: [{state,
## touches, tier}] per street}.
func _enter_response() -> void:
	resp_opts = []
	for rv: Variant in L8Rules.response_options(leg, raid, before, real, place):
		var r: Array = rv
		var outs: Array = []
		var ok := true
		for h in range(L8Rules.HUNTER_CANDS):
			var res := L8Rules.resolve(leg, raid, before, real, h, place, r)
			if res.has("error"):
				ok = false
				break
			var ns: Dictionary = res["state"]
			outs.append({"state": ns, "touches": res["touches"], "tier": L8Rules.tier(before, ns, res["touches"])})
		if ok:
			resp_opts.append({"response": r, "outs": outs})
	var keys := {}
	for o: Dictionary in resp_opts:
		keys[_opt_okey(o)] = true
	resp_all_same = keys.size() <= 1
	resp_hunters = []
	for h in range(L8Rules.HUNTER_CANDS):
		var hl: Variant = L8Rules.hunter_line(leg, raid, before, real, h, place, ["HOLD"])
		if typeof(hl) == TYPE_DICTIONARY:
			resp_hunters.append(hl)
	redeploy_from = null
	deploy_type = ""
	resp_scroll = 0
	resp_sel = -1
	resp_follow = false
	phase = Phase.RESPONSE
	board.clear_response_preview()
	_show_hunter()
	_build_resp_rows()
	_highlight_sources()


## An option's outcome key over both hunter streets; a SACRIFICE keys on its cell too (it loses a district).
func _opt_okey(o: Dictionary) -> String:
	var r: Array = o["response"]
	var key := ("S:%s|" % str(r[1])) if String(r[0]) == "SACRIFICE" else ""
	for ov: Variant in o["outs"]:
		var oo: Dictionary = ov
		key += _okey(oo["touches"], String(oo["tier"])) + "#"
	return key


## Group the visible options by outcome (same touches and tiers on both hunter streets) into rows. When every option
## gives the same outcome, only HOLD is offered. Each row plays its representative: HOLD, else JAM, else the first move,
## else the sacrifice. A picked sentry (REDEPLOY source) or reserve type (DEPLOY) narrows the moves to that source.
func _build_resp_rows() -> void:
	resp_rows = []
	resp_prev = -2
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
		if not _none(redeploy_from):
			if head == "DEPLOY" or head == "SACRIFICE":
				continue
			if head == "REDEPLOY" and r[1] != redeploy_from:
				continue
		elif deploy_type != "":
			if head == "REDEPLOY" or head == "SACRIFICE":
				continue
			if head == "DEPLOY" and String(r[1]) != deploy_type:
				continue
		idx.append(i)
	var keymap := {}
	for iv: Variant in idx:
		var i: int = iv
		var o: Dictionary = resp_opts[i]
		var key := _opt_okey(o)
		if not keymap.has(key):
			keymap[key] = resp_rows.size()
			resp_rows.append({"members": [], "rep": -1})
		var row: Dictionary = resp_rows[int(keymap[key])]
		(row["members"] as Array).append(i)
	for rowv: Variant in resp_rows:
		var row: Dictionary = rowv
		var members: Array = row["members"]
		var rep: int = int(members[0])
		var rank := 9
		for mv: Variant in members:
			var head := String((resp_opts[int(mv)]["response"] as Array)[0])
			var rk := 0 if head == "HOLD" else (1 if head == "JAM" else (3 if head == "SACRIFICE" else 2))
			if rk < rank:
				rank = rk
				rep = int(mv)
		row["rep"] = rep
	if resp_sel >= resp_rows.size():
		resp_sel = -1


func _row_label(members: Array, sd: Dictionary) -> String:
	var has_hold := false
	var has_jam := false
	var reds: Array = []
	var deps: Array = []
	var sacs: Array = []
	for mv: Variant in members:
		var r: Array = resp_opts[int(mv)]["response"]
		match String(r[0]):
			"HOLD":
				has_hold = true
			"JAM":
				has_jam = true
			"DEPLOY":
				deps.append(r)
			"SACRIFICE":
				sacs.append(r)
			_:
				reds.append(r)
	var kinds := (1 if has_hold else 0) + (1 if has_jam else 0) + (1 if not reds.is_empty() else 0) + \
		(1 if not deps.is_empty() else 0) + (1 if not sacs.is_empty() else 0)
	var parts := PackedStringArray()
	if has_hold:
		parts.append("HOLD [H]")
	if has_jam:
		parts.append("JAM [J]" if kinds > 1 else "JAM the hunter [J]")
	if reds.size() == 1:
		parts.append("MOVE" if kinds > 1 else _resp_label(reds[0], sd))
	elif reds.size() > 1:
		parts.append("REDEPLOY (%d ways)" % reds.size())
	if deps.size() == 1:
		parts.append("DEPLOY" if kinds > 1 else _resp_label(deps[0], sd))
	elif deps.size() > 1:
		parts.append("DEPLOY (%d ways)" % deps.size())
	if sacs.size() == 1:
		parts.append(_resp_label(sacs[0], sd))
	elif sacs.size() > 1:
		parts.append("SACRIFICE (%d ways)" % sacs.size())
	return " / ".join(parts)


## The sacrificed cell of a row (its representative), or null.
func _row_sacrifice(row: Dictionary) -> Variant:
	var r: Array = resp_opts[int(row["rep"])]["response"]
	if String(r[0]) == "SACRIFICE":
		return r[1]
	return null


func _has_jam() -> bool:
	if resp_all_same:
		return false
	for o: Dictionary in resp_opts:
		if String((o["response"] as Array)[0]) == "JAM":
			return true
	return false


func _deploy_targets(t: String) -> Array:
	var out: Array = []
	for o: Dictionary in resp_opts:
		var r: Array = o["response"]
		if String(r[0]) == "DEPLOY" and String(r[1]) == t and not out.has(r[2]):
			out.append(r[2])
	return out


func _highlight_sources() -> void:
	if resp_all_same:
		board.clear_highlight()
		return
	var cells: Array = []
	if deploy_type != "":
		cells = _deploy_targets(deploy_type)
	else:
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
		board.highlight(cells, TYPE_COLOR.get(deploy_type, ACID) if deploy_type != "" else ACID)


## Pick a placed sentry as the REDEPLOY source.
func _pick_source(cell: Vector2i) -> void:
	if int(before["kit"]["spoof"]) <= 0:
		status_msg = "No spoof left: REDEPLOY is not available."
		return
	redeploy_from = cell
	deploy_type = ""
	resp_scroll = 0
	_build_resp_rows()
	_highlight_sources()


## Arm (or disarm) a DEPLOY of a reserve sentry of type t: its legal target districts light up.
func _arm_deploy(t: String) -> void:
	if phase != Phase.RESPONSE or busy:
		return
	if resp_all_same:
		status_msg = "Nothing you can do changes this: HOLD [H]."
		return
	if deploy_type == t:
		deploy_type = ""
		_build_resp_rows()
		_highlight_sources()
		return
	if int(before["kit"]["spoof"]) <= 0:
		status_msg = "No spoof left: DEPLOY is not available."
		return
	if _deploy_targets(t).is_empty():
		status_msg = "No %s sentry in reserve to deploy (or no free district)." % _tname(t)
		return
	deploy_type = t
	redeploy_from = null
	resp_scroll = 0
	_build_resp_rows()
	_highlight_sources()


func _move_resp_sel(d: int) -> void:
	if resp_rows.is_empty():
		return
	if resp_sel < 0:
		resp_sel = 0 if d > 0 else resp_rows.size() - 1
	else:
		resp_sel = clampi(resp_sel + d, 0, resp_rows.size() - 1)
	resp_follow = true


func _response_click(c: Variant) -> void:
	if phase != Phase.RESPONSE or busy or typeof(c) != TYPE_VECTOR2I:
		return
	if resp_all_same:
		status_msg = "Nothing you can do changes this: HOLD [H]."
		return
	var cell: Vector2i = c
	var sent: Dictionary = mid["sentries"]
	if deploy_type != "":
		if sent.has(cell):
			_pick_source(cell)
			return
		for o: Dictionary in resp_opts:
			var r: Array = o["response"]
			if String(r[0]) == "DEPLOY" and String(r[1]) == deploy_type and r[2] == cell:
				_respond(r)
				return
		status_msg = "Not a legal DEPLOY target: an owned, live district with no sentry."
		return
	if _none(redeploy_from):
		if not sent.has(cell):
			status_msg = "Click one of your sentries to move it, press 1 2 3 for a reserve one, or pick a row."
		else:
			_pick_source(cell)
		return
	var from: Vector2i = redeploy_from
	if cell == from:
		redeploy_from = null
		_build_resp_rows()
		_highlight_sources()
		return
	if sent.has(cell):
		_pick_source(cell)
		return
	for o: Dictionary in resp_opts:
		var r: Array = o["response"]
		if String(r[0]) == "REDEPLOY" and r[1] == from and r[2] == cell:
			_respond(r)
			return
	status_msg = "Not a legal target: an owned, live district with no sentry."


## Commit a response: the sealed beam, the HUNTER REVEAL (one sealed street ignites), then the hunter run (or the jam).
func _respond(r: Array) -> void:
	if busy or phase != Phase.RESPONSE:
		return
	var resp := L8Rules.norm_response(r)
	if resp.is_empty():
		return
	var res := L8Rules.resolve(leg, raid, before, real, hunt, place, resp)
	if res.has("error"):
		status_msg = "Response: " + String(res["error"])
		return
	board.clear_response_preview()
	resp_prev = -2
	cur_resp = resp
	var head := String(resp[0])
	var sent: Dictionary = (mid["sentries"] as Dictionary).duplicate()
	if head == "REDEPLOY" or head == "DEPLOY" or head == "SACRIFICE":
		var ms: Dictionary = mid.duplicate()
		if head == "REDEPLOY":
			var t: Variant = sent[resp[1]]
			sent.erase(resp[1])
			sent[resp[2]] = t
		elif head == "DEPLOY":
			sent[resp[2]] = String(resp[1])
		else:
			var ow: Dictionary = (mid["owned"] as Dictionary).duplicate()
			ow[resp[1]] = L8Rules.TAKEN
			sent.erase(resp[1])
			ms["owned"] = ow
		board.show_state(ms, {"sentries": sent, "ghost": place["ghost"]})
	board.clear_highlight()
	redeploy_from = null
	deploy_type = ""
	phase = Phase.PLAY
	stage = "sealed"
	var rn := raid + 1
	var tr: Array = res["trace"]
	await _play_batch(_line_cues("sealed", rd["cands"][real], tr), "")
	stage = "hreveal"
	_show_hunter()
	busy = true
	board.set_instant(instant)
	await board.hunter_reveal(hunt)
	busy = false
	hunter_revealed = true
	if shots_dir != "":
		await _shot("r%d_hunter_reveal" % rn)
	stage = "hunt"
	await _play_batch(_hunter_cues(tr, resp), "r%d_sealed_hunter" % rn)
	var ns: Dictionary = res["state"]
	result = {"state": ns, "touches": res["touches"], "trace": tr, "tier": L8Rules.tier(before, ns, res["touches"]),
		"response": resp}
	st = ns
	hud_hp = int(st["home_hp"])
	breached = int(st["home_hp"]) <= 0
	history.append({"raid": raid, "capture": cap_cells.duplicate(), "response": resp, "tier": result["tier"],
		"touches": res["touches"], "heat_launch": heat_launch, "heat_after": int(st["heat"]),
		"score": L8Rules.score(leg, st), "between": null, "sentries": (mid["sentries"] as Dictionary).duplicate(),
		"ghost": place["ghost"], "hunt": hunt})
	route_v = []
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	board.show_state(st, {"sentries": st["sentries"], "ghost": null})
	phase = Phase.AFTER


## The row whose effect the board previews: the hovered one, else the selected one, else none.
func _preview_row() -> int:
	if resp_hover >= 0 and resp_hover < resp_rows.size():
		return resp_hover
	if resp_sel >= 0 and resp_sel < resp_rows.size():
		return resp_sel
	return -1


## A row's board preview: {moves: [{kind, from, to, type}], jam, sacrifice (cell or null), hunter, hunters}. A row
## holding HOLD previews nothing; a JAM row crosses out the hunter; a SACRIFICE row crumbles its cell and shields HOME;
## a move row draws every move it groups.
func _preview_of(j: int) -> Dictionary:
	var row: Dictionary = resp_rows[j]
	var members: Array = row["members"]
	var moves: Array = []
	var has_hold := false
	var rep_head := String((resp_opts[int(row["rep"])]["response"] as Array)[0])
	var sd: Dictionary = mid["sentries"]
	var h0: Variant = resp_hunters[0] if not resp_hunters.is_empty() else null
	for mv: Variant in members:
		var r: Array = resp_opts[int(mv)]["response"]
		match String(r[0]):
			"HOLD":
				has_hold = true
			"REDEPLOY":
				moves.append({"kind": "REDEPLOY", "from": r[1], "to": r[2], "type": String(sd.get(r[1], "D"))})
			"DEPLOY":
				moves.append({"kind": "DEPLOY", "from": null, "to": r[2], "type": String(r[1])})
	var base := {"moves": [], "jam": false, "sacrifice": null, "hunter": h0, "hunters": resp_hunters.duplicate()}
	if has_hold:
		return base
	if rep_head == "JAM":
		base["jam"] = true
		return base
	if rep_head == "SACRIFICE":
		base["sacrifice"] = _row_sacrifice(row)
		return base
	base["moves"] = moves
	return base


func _sync_resp_preview() -> void:
	var j := _preview_row()
	if j == resp_prev:
		return
	resp_prev = j
	if j < 0:
		board.clear_response_preview()
		return
	var p := _preview_of(j)
	if (p["moves"] as Array).is_empty() and not bool(p["jam"]) and _none(p["sacrifice"]):
		board.clear_response_preview()
	else:
		board.show_response_preview(p)


## The reserve tray in the RESPONSE panel: each type's reserve count, clickable (or 1 2 3) to arm a DEPLOY.
func _draw_resp_tray(y: float) -> float:
	var x := PANEL_X + PAD
	var pool: Dictionary = before["pool"]
	var sent: Dictionary = mid["sentries"]
	tray_pos = {}
	_t(Vector2(x, y), "RESERVE", TXT, DIM)
	for i in range(3):
		var t: String = L8Rules.TYPES[i]
		var n := maxi(0, int(pool[t]) - _count_type(sent, t))
		var ok := not resp_all_same and not _deploy_targets(t).is_empty()
		var r := Rect2(x + 76.0 + i * 102.0, y - 4.0, 94.0, 24.0)
		var sel := deploy_type == t
		var hot := ok and r.has_point(mouse)
		_box(r, AMBER if sel else (INK if hot else EDGE), PANEL_HI if (sel or hot) else PANEL, 1.5)
		var gc := r.position + Vector2(13.0, 12.0)
		_glyph(gc, t, 7.0, TYPE_COLOR[t] if n > 0 else DIM)
		_t(r.position + Vector2(26.0, 3.0), "x%d  [%d]" % [n, i + 1], TXT, INK if ok else DIM)
		tray_pos[t] = gc
		if ok:
			hits.append({"rect": r, "id": "dep:" + t})
	return y + 28.0


func _draw_response() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var y := _head("RESPONSE  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "H hold, J jam, a row, or a sentry / reserve then a cell.")
	var sealed: Dictionary = rd["cands"][real]
	var t := String(sealed["type"])
	_glyph(Vector2(x + 8.0, y + 9.0), t, 8.0, TYPE_COLOR[t])
	_tf(Vector2(x + 22.0, y), "SEALED: %s ROUTE, %s" % [L8Rules.ROUTE_NAMES[real], _tname(t)], 14, INK)
	y += 22.0
	_tf(Vector2(x, y), "Spoofs left %d: a move or JAM costs 1 and +%d Heat; SACRIFICE is free." % [int(before["kit"]["spoof"]),
		L8Rules.SPOOF_HEAT], TXT, DIM)
	y += 18.0
	_tf(Vector2(x, y), "The hunter street is still sealed: rows show A / B.", TXT, COBALT_HOT)
	y += 18.0
	_tf(Vector2(x, y), "REDEPLOY moves a sentry, DEPLOY adds a reserve one.", TXT, DIM)
	y += 22.0
	y = _draw_resp_tray(y)
	if resp_opts.size() <= 1:
		_tf(Vector2(x, y), "No response is available: HOLD.", TXT, AMBER)
		y += 20.0
	elif resp_all_same:
		_tf(Vector2(x, y), "Nothing you can do changes this.", TXT, AMBER)
		y += 20.0
	else:
		_tf(Vector2(x, y), "Options with the same result share a row.", TXT, DIM)
		y += 20.0
	if not _none(redeploy_from):
		var st_t := String((mid["sentries"] as Dictionary).get(redeploy_from, "?"))
		_tf(Vector2(x, y), "Moves of the %s on %s  (Esc: all rows)" % [_tname(st_t), _cell_name(redeploy_from)], TXT, ACID)
		y += 20.0
	elif deploy_type != "":
		_tf(Vector2(x, y), "Deploys of a reserve %s  (Esc: all rows)" % _tname(deploy_type), TXT, ACID)
		y += 20.0
	var max_rows := maxi(1, int((LEGEND_Y - 22.0 - y) / ROW_H))
	if resp_follow and resp_sel >= 0:
		if resp_sel < resp_scroll:
			resp_scroll = resp_sel
		elif resp_sel >= resp_scroll + max_rows:
			resp_scroll = resp_sel - max_rows + 1
		resp_follow = false
	resp_scroll = clampi(resp_scroll, 0, maxi(0, resp_rows.size() - max_rows))
	var sd: Dictionary = mid["sentries"]
	for j in range(resp_scroll, mini(resp_rows.size(), resp_scroll + max_rows)):
		var row: Dictionary = resp_rows[j]
		var o: Dictionary = resp_opts[int(row["rep"])]
		var outs: Array = o["outs"]
		var oa: Dictionary = outs[0]
		var ob: Dictionary = outs[outs.size() - 1]
		var rr := Rect2(x, y, w, ROW_H - 4.0)
		var hot := rr.has_point(mouse) and auto_line == "" and not busy
		if hot:
			resp_hover = j
		var sel := j == resp_sel
		_box(rr, ACID if hot else (AMBER if sel else EDGE), PANEL_HI if (hot or sel) else PANEL)
		var left := _tier_pair(Vector2(rr.end.x - 8.0, rr.position.y + 3.0), String(oa["tier"]), String(ob["tier"]))
		_tf(rr.position + Vector2(8.0, 3.0), _row_label(row["members"], sd), TXT, INK, left - 8.0)
		var sa := _sum(oa["touches"])
		var sb := _sum(ob["touches"])
		var line2 := ("A and B: %s" % sa) if sa == sb else ("A: %s   B: %s" % [sa, sb])
		_tf(rr.position + Vector2(8.0, 20.0), line2, TXT, DIM, rr.end.x - 8.0)
		var sac: Variant = _row_sacrifice(row)
		if not _none(sac):
			_tf(rr.position + Vector2(8.0, 37.0), "HOME is shielded this raid, %s is lost" % _cell_name(sac), TXT,
				COBALT_HOT, rr.end.x - 8.0)
		else:
			var sta: Dictionary = oa["state"]
			var stb: Dictionary = ob["state"]
			var hpa := int(sta["home_hp"])
			var hpb := int(stb["home_hp"])
			var home_t := ("HOME %d/%d" % [hpa, L8Rules.HOME_HP]) if hpa == hpb else ("HOME %d/%d | %d/%d" % [hpa,
				L8Rules.HOME_HP, hpb, L8Rules.HOME_HP])
			var ha := int(sta["heat"])
			var hb := int(stb["heat"])
			var heat_t := ("Heat %d" % ha) if ha == hb else ("Heat %d | %d" % [ha, hb])
			_tf(rr.position + Vector2(8.0, 37.0), "%s   %s" % [home_t, heat_t], TXT, DIM, rr.end.x - 8.0)
		hits.append({"rect": rr, "id": "resp:%d" % j})
		y += ROW_H
	if resp_rows.size() > max_rows:
		_tr(Vector2(PANEL_X + PANEL_W - PAD, LEGEND_Y - 20.0), "rows %d-%d of %d (wheel scrolls)" % [resp_scroll + 1,
			mini(resp_rows.size(), resp_scroll + max_rows), resp_rows.size()], TXT, DIM)
	_sync_resp_preview()


# ---------------------------------------------------------------- AFTERMATH
func _draw_after() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var tier := String(result.get("tier", "HOLDS"))
	var y := _head("AFTERMATH  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Enter goes on.")
	y += _tier_big(Vector2(x, y), tier)
	_tf(Vector2(x, y), String(TIER_TEXT.get(tier, "")), TXT, INK)
	y += 24.0
	var resp: Array = result["response"]
	_tf(Vector2(x, y), "Response: %s" % _resp_label(resp, mid.get("sentries", place["sentries"])), TXT, ACID)
	y += 20.0
	_tf(Vector2(x, y), "Hunter: street %d (%s)%s" % [_hunt_street(hunt), HUNT_KEY[hunt],
		", jammed" if String(resp[0]) == "JAM" else ""], TXT, COBALT_HOT)
	y += 26.0
	_t(Vector2(x, y), "WHAT THE BEAMS TOUCHED", TXT, DIM)
	y += 20.0
	y = _draw_touch_lines(result["trace"], y)
	y += 10.0
	var notes := PackedStringArray()
	if (result["trace"] as Array).is_empty() and String(resp[0]) != "SACRIFICE":
		notes.append("evaded -%d" % L8Rules.EVADE_HEAT)
	if L8Rules.response_spoofs(resp):
		notes.append("spoof +%d" % L8Rules.SPOOF_HEAT)
	var note := "" if notes.is_empty() else "  (%s)" % ", ".join(notes)
	_tf(Vector2(x, y), "Heat: launch %d -> %d%s" % [heat_launch, int(st["heat"]), note], TXT, HEAT_COL)
	y += 22.0
	_tf(Vector2(x, y), "HOME: %d -> %d" % [int(before["home_hp"]), int(st["home_hp"])], TXT,
		RED if int(st["home_hp"]) < int(before["home_hp"]) else INK)
	y += 22.0
	var live := L8Rules.live_cells(st).size()
	_tf(Vector2(x, y), "Districts held: %d    Leg value now: %s" % [live, _score_text(st)], TXT, INK)
	y += 22.0
	var last := breached or raid >= L8Rules.RAIDS - 1
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "RECORD [Enter]" if last else "BETWEEN RAIDS [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- BETWEEN
func _enter_between() -> void:
	board.clear_paths()
	board.clear_outcome()
	board.clear_response_preview()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	resp_prev = -2
	b_repair = null
	b_build = null
	b_inten = "NORMAL"
	build_armed = false
	safe_pending = {}
	b_hash = _state_hash(st)
	b_all_unsafe = -1
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
		board.highlight_kind([b_repair], "picked", true)


func _bp(inten: String) -> Dictionary:
	return L8Rules.between_parts(leg, st, b_repair, b_build, inten)


func _opt_key(repair: Variant, build: Variant, inten: String) -> String:
	return "%d|%d|%d|%s|%s|%s" % [leg_seed, raid, b_hash, str(repair), str(build), inten]


## safe_next on the next raid from a post-between state, cached by (leg, raid, state hash).
func _safe_next_cached(raid_i: int, s: Dictionary) -> bool:
	var key := "%d|%d|%d" % [leg_seed, raid_i, _state_hash(s)]
	if not next_cache.has(key):
		next_cache[key] = L8Rules.safe_next(leg, raid_i, s)
	return bool(next_cache[key])


func _compute_safe(key: String, repair: Variant, build: Variant, inten: String) -> bool:
	var ns: Dictionary = L8Rules.between(leg, st, repair, build, inten)
	var ok := _safe_next_cached(raid + 1, L8Rules.decay(leg, ns))
	safe_cache[key] = ok
	safe_pending.erase(key)
	return ok


## The verdict of a between option: L8Rules.safe_next on the next raid's state after the step and its decay.
## 1 = HOLDABLE (a plan exists), 0 = LOST (no plan holds HOME), -1 = still being checked (queued for _process).
## force (and --auto) computes it at once.
func _safe(repair: Variant, build: Variant, inten: String, force: bool = false) -> int:
	var key := _opt_key(repair, build, inten)
	if safe_cache.has(key):
		return 1 if bool(safe_cache[key]) else 0
	if force or auto_line != "":
		return 1 if _compute_safe(key, repair, build, inten) else 0
	if not safe_pending.has(key):
		safe_pending[key] = [repair, build, inten]
	return -1


## Work queued verdict checks for up to SAFE_BUDGET_MS this frame (at least one).
func _work_safe() -> void:
	var t0 := Time.get_ticks_msec()
	while not safe_pending.is_empty():
		var key: String = safe_pending.keys()[0]
		var a: Array = safe_pending[key]
		_compute_safe(key, a[0], a[1], String(a[2]))
		if Time.get_ticks_msec() - t0 >= SAFE_BUDGET_MS:
			break


## DECIDED: every intensity card for the current repair and build is LOST, and no between option at all holds.
## 1 = decided, 0 = not, -1 = still being checked (force computes everything at once).
func _decided(force: bool = false) -> int:
	if raid + 1 >= L8Rules.RAIDS:
		return 0
	var unknown := false
	for nv: Variant in L8Rules.INTENSITY_ORDER:
		var v := _safe(b_repair, b_build, String(nv), force)
		if v == 1:
			return 0
		if v < 0:
			unknown = true
	if unknown:
		return -1
	if b_all_unsafe < 0:
		var unk := false
		for ov: Variant in L8Rules.between_options(leg, st):
			var o: Array = ov
			var v := _safe(o[0], o[1], String(o[2]), force)
			if v == 1:
				b_all_unsafe = 0
				return 0
			if v < 0:
				unk = true
		if unk:
			return -1
		b_all_unsafe = 1
	return b_all_unsafe


## The repair options at the current build: none, then every DOWN district the bank can pay for.
func _repair_opts() -> Array:
	var out: Array = [null]
	for cv: Variant in _down_cells():
		if not _none(L8Rules.between_parts(leg, st, cv, b_build, b_inten)["repaired"]):
			out.append(cv)
	return out


## The build options at the current repair: none, then every type the bank can pay for after the repair.
func _build_opts() -> Array:
	var out: Array = [null]
	for tv: Variant in L8Rules.TYPES:
		if not _none(L8Rules.between_parts(leg, st, b_repair, tv, b_inten)["built"]):
			out.append(tv)
	return out


## The requirement line for repair (is_repair) or build options at the selected intensity: when some options hold the
## next raid and others lose it, name the holding ones ("Repair MID 0, or raid 3 cannot be held"). "" otherwise, or
## while a verdict is still being checked.
func _req_text(opts: Array, is_repair: bool) -> String:
	if raid + 1 >= L8Rules.RAIDS or opts.size() <= 1:
		return ""
	var good := PackedStringArray()
	var bad := false
	for o: Variant in opts:
		var v := _safe(o if is_repair else b_repair, b_build if is_repair else o, b_inten)
		if v < 0:
			return ""
		if v == 1:
			if _none(o):
				good.append("nothing")
			else:
				good.append(_cell_name(o) if is_repair else String(o))
		else:
			bad = true
	if good.is_empty() or not bad:
		return ""
	return "%s %s, or raid %d cannot be held" % ["Repair" if is_repair else "Build", " or ".join(good), raid + 2]


## A red-bordered requirement line. Returns the y after.
func _req_line(y: float, text: String) -> float:
	var x := PANEL_X + PAD
	var r := Rect2(x, y, PANEL_W - 2.0 * PAD, 21.0)
	ui.draw_rect(r, RED.darkened(0.7))
	ui.draw_rect(r, RED, false, 2.0)
	_tf(r.position + Vector2(8.0, 2.0), text, TXT, WHITE, r.end.x - 6.0)
	return y + 25.0


func _clear_repair() -> void:
	if phase != Phase.BETWEEN:
		return
	b_repair = null
	_highlight_down()


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
		status_msg = "Not enough bank to repair it (cost %d)." % L8Rules.repair_cost(leg, c, b_inten)
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


## Pick an intensity. The repair is free under NORMAL, so leaving NORMAL can make the picked repair or build
## unaffordable: it is dropped with a status line.
func _set_inten(name: String) -> void:
	if phase != Phase.BETWEEN or not L8Rules.INTENSITY.has(name):
		return
	b_inten = name
	if not _none(b_repair) and _none(L8Rules.between_parts(leg, st, b_repair, null, b_inten)["repaired"]):
		b_repair = null
		status_msg = "Not enough bank for the repair at %s: the repair is dropped." % name
		_highlight_down()
	if not _none(b_build) and _none(L8Rules.between_parts(leg, st, b_repair, b_build, b_inten)["built"]):
		b_build = null
		status_msg = "Not enough bank for the build at %s: the build is dropped." % name


## Apply the between step. When the screen is DECIDED, a short fall beat plays and the record follows (no dead raid).
func _confirm_between() -> void:
	if phase != Phase.BETWEEN or busy:
		return
	var parts := _bp(b_inten)
	var cut := _decided(true) == 1
	safe_pending = {}
	if not history.is_empty():
		var row: Dictionary = history.back()
		row["between"] = {"repair": parts["repaired"], "build": parts["built"], "intensity": b_inten,
			"income": int(parts["income"]), "heat_add": int(parts["heat_add"]),
			"repair_cost": int(parts["repair_cost"]), "extra_capture": int(parts["extra_capture"])}
	var rn := raid + 1
	st = L8Rules.between(leg, st, b_repair, b_build, b_inten)
	hud_hp = int(st["home_hp"])
	board.clear_highlight()
	if cut:
		decided = true
		decided_raid = raid + 1
		phase = Phase.FALL
		board.clear_paths()
		board.clear_outcome()
		board.clear_response_preview()
		board.show_state(st, {"sentries": st["sentries"], "ghost": null})
		busy = true
		board.set_instant(instant)
		await board.show_fall()
		busy = false
		if shots_dir != "":
			await _shot("r%d_decided" % rn)
		_enter_record()
		return
	raid += 1
	_begin_raid()


## An intensity card's perk: NORMAL free repair (wrench), HOT two captures next raid (double flag), LOW none.
func _draw_perk(p: Vector2, nm: String, sel: bool) -> void:
	var col := ACID if sel else INK
	match nm:
		"NORMAL":
			_wrench_icon(p + Vector2(8.0, 9.0), col)
			_t(p + Vector2(22.0, 0.0), "free repair", TXT, col)
		"HOT":
			_flag_icon(p + Vector2(4.0, 9.0), col)
			_flag_icon(p + Vector2(12.0, 9.0), col)
			_t(p + Vector2(26.0, 0.0), "2 captures", TXT, col)
			_t(p + Vector2(26.0, 16.0), "next raid", TXT, col)
		_:
			_t(p + Vector2(4.0, 0.0), "no perk", TXT, DIM)


func _draw_between() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var right := PANEL_X + PANEL_W - PAD
	var y := _head("BETWEEN RAIDS", "Repair, build, pick an intensity. Enter: next raid.")
	var parts := _bp(b_inten)
	_safe(b_repair, b_build, b_inten)	# the current choice is checked first
	if int(st["home_hp"]) == 1:
		var br := Rect2(x, y - 4.0, w, 24.0)
		ui.draw_rect(br, RED.darkened(0.45))
		ui.draw_rect(br, RED, false, 2.0)
		_skull(br.position + Vector2(13.0, 12.0), 8.0, WHITE, BLACK)
		_t(br.position + Vector2(28.0, 3.0), "Next HOME hit ends the campaign", TXT, WHITE)
		y += 26.0
	# 1: repair rows, each with its own verdict at the selected intensity and the current build.
	_tf(Vector2(x, y), "1  REPAIR ONE DOWN DISTRICT  (v / 2, free on NORMAL)", TXT, DIM)
	y += 20.0
	var downs := _down_cells()
	if downs.is_empty():
		_t(Vector2(x + 18.0, y), "nothing is DOWN", TXT, DIM)
		y += 22.0
	else:
		var ropts: Array = [null]
		ropts.append_array(downs)
		for i in range(ropts.size()):
			var o: Variant = ropts[i]
			var rr := Rect2(x, y, w, REP_ROW_H - 2.0)
			var picked := L8Rules._same(b_repair, o)
			var afford := _none(o) or not _none(L8Rules.between_parts(leg, st, o, b_build, b_inten)["repaired"])
			var hot := afford and rr.has_point(mouse)
			if picked or hot:
				_box(rr, AMBER if picked else INK, PANEL_HI, 1.0)
			var lim := rr.end.x - 100.0
			if _none(o):
				_tf(rr.position + Vector2(22.0, 1.0), "no repair" if picked else "no repair [click]", TXT,
					INK if picked else DIM, lim)
			else:
				var c: Vector2i = o
				var cost := L8Rules.repair_cost(leg, c, b_inten)
				var ct := "free" if cost == 0 else "-%d" % cost
				_down_icon(rr.position + Vector2(10.0, 9.5))
				if picked:
					_tf(rr.position + Vector2(22.0, 1.0), "repair %s   %s" % [_cell_name(c), ct], TXT, ACID, lim)
				else:
					_tf(rr.position + Vector2(22.0, 1.0), "%s DOWN: repair or lose it (%s)" % [_cell_name(c), ct], TXT,
						RED if afford else DIM, lim)
			if afford:
				_verdict_mark(Vector2(rr.end.x - 4.0, rr.position.y + 1.0), _safe(o, b_build, b_inten))
				hits.append({"rect": rr, "id": "rep:%d" % i})
			else:
				_tr(Vector2(rr.end.x - 4.0, rr.position.y + 1.0), "bank too low", TXT, DIM)
			y += REP_ROW_H
	var rq := _req_text(_repair_opts(), true)
	if rq != "":
		y = _req_line(y + 2.0, rq)
	y += 6.0
	# 2: build buttons, each with its own verdict mark.
	_tf(Vector2(x, y), "2  BUILD ONE SENTRY (-%d)   [B, then 1 2 3; 0 none]" % L8Rules.SENTRY_PRICE, TXT, DIM)
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
			_tc(r.get_center() - Vector2(8.0, 0.0), "NONE [0]", TXT, INK)
		else:
			_glyph(r.position + Vector2(13.0, 20.0), t, 8.0, TYPE_COLOR[t] if ok else DIM)
			_t(r.position + Vector2(25.0, 3.0), _fit(_tname(t).substr(0, 6), TXT, bw - 28.0), TXT, INK if ok else DIM)
			_t(r.position + Vector2(25.0, 20.0), "[%d] -%d" % [i, L8Rules.SENTRY_PRICE], TXT, DIM)
		if ok:
			_verdict_dot(Vector2(r.end.x - 9.0, r.end.y - 10.0), _safe(b_repair, null if t == "" else t, b_inten))
			hits.append({"rect": r, "id": "build:" + ("none" if t == "" else t)})
	y += 46.0
	var bq := _req_text(_build_opts(), false)
	if bq != "":
		y = _req_line(y, bq)
	# 3: intensity cards, each with its perk and its verdict badge.
	_tf(Vector2(x, y), "3  RUN INTENSITY   [L N O]", TXT, DIM)
	y += 20.0
	var kt: Array = []
	if raid + 1 < L8Rules.RAIDS:
		var rn: Dictionary = leg["raids"][raid + 1]
		kt = [String(rn["b1"]["type"]), String(rn["extra1"]["type"]), String(rn["extra2"]["type"])]
	var cw := (w - 16.0) / 3.0
	for i in range(3):
		var nm: String = L8Rules.INTENSITY_ORDER[i]
		var cr := Rect2(x + i * (cw + 8.0), y, cw, CARD_H)
		var sel := nm == b_inten
		var hot := cr.has_point(mouse)
		_box(cr, AMBER if sel else (INK if hot else EDGE), PANEL_HI if (sel or hot) else PANEL, 3.0 if sel else 2.0)
		hits.append({"rect": cr, "id": "inten:" + nm})
		var p := _bp(nm)
		var ns: Dictionary = p["state"]
		var h0 := int(ns["heat"])
		var ghost_ok := int((ns["kit"] as Dictionary).get("ghost", 0)) > 0
		var h1 := h0 + L8Rules.GHOST_HEAT
		var k0 := 1 + L8Rules.extra_count(h0)
		var k1 := 1 + L8Rules.extra_count(h1)
		for f in range(i + 1):
			_flame(Vector2(cr.end.x - 10.0 - f * 12.0, cr.position.y + 12.0), 5.0)
		_t(cr.position + Vector2(7.0, 3.0), _fit("%s [%s]" % [nm, INTEN_KEY[i]], TXT, cw - 20.0 - 12.0 * (i + 1)), TXT,
			AMBER if sel else INK)
		_t(cr.position + Vector2(7.0, 21.0), _fit("Heat +%d -> %d" % [int(p["heat_add"]), h0], TXT, cw - 12.0), TXT, HEAT_COL)
		_t(cr.position + Vector2(7.0, 38.0), _fit("bank +%d = %d" % [int(p["income"]), int(ns["bank"])], TXT, cw - 12.0), TXT, GOLD)
		var ry := cr.position.y + 63.0
		_beam_icons(Vector2(cr.position.x + 16.0, ry), kt, k0)
		_tr(Vector2(cr.end.x - 7.0, ry - 9.0), "H%d" % h0, TXT, RED if k0 > 1 else DIM)
		ry += 17.0
		if ghost_ok:
			_ghost_icon(Vector2(cr.position.x + 11.0, ry), 4.5, GOLD)
			_beam_icons(Vector2(cr.position.x + 28.0, ry), kt, k1)
			_tr(Vector2(cr.end.x - 7.0, ry - 9.0), "H%d" % h1, TXT, RED if k1 > 1 else DIM)
		else:
			_t(Vector2(cr.position.x + 7.0, ry - 9.0), _fit("no ghost left", TXT, cw - 12.0), TXT, DIM)
		_draw_perk(cr.position + Vector2(5.0, 89.0), nm, sel)
		var sv := _safe(b_repair, b_build, nm)
		var badge := Rect2(cr.position.x + 5.0, cr.position.y + 124.0, cr.size.x - 10.0, 32.0)
		if sv == 1:
			_box(badge, HOLDS_COL, PANEL, 2.0)
			_tier_glyph(badge.position + Vector2(11.0, 9.0), "HOLDS", 6.5, HOLDS_COL)
			_t(badge.position + Vector2(21.0, 0.0), _fit("HOLDABLE:", TXT, badge.size.x - 24.0), TXT, HOLDS_COL)
			_t(badge.position + Vector2(5.0, 15.0), _fit("a plan exists", TXT, badge.size.x - 8.0), TXT, HOLDS_COL)
		elif sv == 0:
			_box(badge, RED, BLACK, 2.0)
			_skull(badge.position + Vector2(11.0, 9.0), 6.5, RED, BLACK)
			_t(badge.position + Vector2(21.0, 0.0), _fit("LOST: no plan", TXT, badge.size.x - 24.0), TXT, RED)
			_t(badge.position + Vector2(5.0, 15.0), _fit("holds HOME", TXT, badge.size.x - 8.0), TXT, RED)
		else:
			_box(badge, EDGE, PANEL, 1.5)
			ui.draw_arc(badge.position + Vector2(11.0, 16.0), 4.5, 0.0, TAU, 12, DIM, 1.5)
			_t(badge.position + Vector2(21.0, 7.0), _fit("checking...", TXT, badge.size.x - 24.0), TXT, DIM)
	y += CARD_H + 8.0
	var ns2: Dictionary = parts["state"]
	var dec := _decided() == 1
	if dec:
		y = minf(y, LEGEND_Y - 110.0)
		var dr := Rect2(x, y, w, 26.0)
		ui.draw_rect(dr, BLACK)
		ui.draw_rect(dr, RED, false, 2.0)
		_skull(dr.position + Vector2(14.0, 13.0), 9.0, RED, BLACK)
		_tf(dr.position + Vector2(30.0, 4.0), "DECIDED: the cell falls next raid", TXT, WHITE, dr.end.x - 6.0)
		y += 30.0
		_tf(Vector2(x, y), "No repair, build or intensity leaves a plan that holds HOME.", TXT, DIM)
	else:
		_tf(Vector2(x, y), "BANK %d - repair %d - build %d + income %d = %d" % [int(st["bank"]), int(parts["repair_cost"]),
			int(parts["build_cost"]), int(parts["income"]), int(ns2["bank"])], TXT, INK)
		y += 19.0
		var heat_t := "HEAT %d + %d = %d" % [int(st["heat"]), int(parts["heat_add"]), int(ns2["heat"])]
		_t(Vector2(x, y), heat_t, TXT, HEAT_COL)
		var vx := x + _tw(heat_t, TXT) + 16.0
		_tf(Vector2(vx, y), "Leg value after: %s" % _score_text(ns2), TXT, INK, right)
		y += 22.0
		if y + 48.0 <= LEGEND_Y - 62.0:
			_draw_kit(y, false)
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "THE CELL FALLS [Enter]" if dec else "NEXT RAID [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- FALL (the DECIDED beat)
func _draw_fall() -> void:
	var x := PANEL_X + PAD
	var y := _head("DECIDED", "The cell falls next raid.")
	_skull(Vector2(x + 10.0, y + 10.0), 10.0, RED, BG)
	_tf(Vector2(x + 28.0, y), "No line keeps HOME above 0 in raid %d." % (decided_raid + 1), TXT, RED)
	y += 24.0
	_tf(Vector2(x, y), "Every repair, build and intensity leaves", TXT, DIM)
	y += 18.0
	_tf(Vector2(x, y), "a sealed route that ends the campaign.", TXT, DIM)


# ---------------------------------------------------------------- RECORD
func _enter_record() -> void:
	phase = Phase.RECORD
	board.clear_highlight()
	board.clear_outcome()
	board.clear_response_preview()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	route_v = []
	resp_prev = -2


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
	if decided:
		_tier_pip(Vector2(px0 + history.size() * 30.0, y + 15.0), "BREACHED", 11.0)
	y += 38.0
	if breached:
		_skull(Vector2(x + 9.0, y + 11.0), 9.0, RED, BG)
		_t(Vector2(x + 26.0, y), "BREACHED in raid %d: the campaign is lost." % history.size(), 18, RED)
	elif decided:
		_skull(Vector2(x + 9.0, y + 11.0), 9.0, RED, BG)
		_t(Vector2(x + 26.0, y), "DECIDED before raid %d: no plan could hold HOME. The cell falls." % (decided_raid + 1), 18, RED)
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
		var caps: Array = h["capture"]
		var cap := "no capture" if caps.is_empty() else "captured " + _cells_list(caps)
		_tf(r.position + Vector2(280.0, 10.0), cap, TXT, INK, r.position.x + 470.0)
		_tf(r.position + Vector2(480.0, 10.0), "response " + _resp_label(h["response"], h["sentries"]), TXT, ACID, r.end.x - 10.0)
		var hn := int(h.get("hunt", 0))
		_tf(r.position + Vector2(14.0, 34.0), "%s   Heat %d -> %d   hunter street %s" % [_sum(h["touches"]),
			int(h["heat_launch"]), int(h["heat_after"]), HUNT_KEY[clampi(hn, 0, 1)]], TXT, INK, r.end.x - 10.0)
		var bt: Variant = h["between"]
		if typeof(bt) == TYPE_DICTIONARY:
			var b: Dictionary = bt
			var rep := "no repair" if _none(b["repair"]) else "repaired " + _cell_name(b["repair"])
			if not _none(b["repair"]) and int(b.get("repair_cost", 1)) == 0:
				rep += " (free)"
			var bld := "no build" if _none(b["build"]) else "built " + _tname(String(b["build"]))
			var perk := ", 2 captures next raid" if int(b.get("extra_capture", 0)) > 0 else ""
			_tf(r.position + Vector2(14.0, 53.0), "then %s, %s, ran %s (income +%d, Heat +%d%s)" % [rep, bld,
				String(b["intensity"]), int(b["income"]), int(b["heat_add"]), perk], TXT, DIM, r.end.x - 10.0)
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
	if bool(sp["breach"]) or decided:
		_t(Vector2(px, py), "CAMPAIGN LOST", 28, RED)
		_tf(Vector2(px, py + 40.0), "A breach leaves no score." if not decided else "Decided: the cell falls next raid.", 14, INK)
	else:
		var bands := int(sp["heat_bands"])
		var linear := float(sp["heat_carry"]) - float(bands)
		var rows: Array = [["bank", "+%d" % int(sp["bank"])], ["districts held", "+%d" % int(sp["cells"])],
			["exploits held", "+%d" % int(sp["exploits"])],
			["HOME lost (%d each)" % L8Rules.HOME_LOSS_COST, "-%d" % int(sp["home_loss"])],
			["Heat above %d (x%s)" % [L8Rules.START_HEAT, _num(L8Rules.HEAT_CARRY)], "-%s" % _num(linear)],
			["Heat bands (%d / %d: %d each)" % [L8Rules.EXTRA_AT, L8Rules.STRONG_AT, L8Rules.HEAT_BAND], "-%d" % bands]]
		for rw: Variant in rows:
			var a: Array = rw
			var val := String(a[1])
			_tr(Vector2(px + w, py), val, 14, AMBER)
			_tf(Vector2(px, py), String(a[0]), 14, INK, px + w - _tw(val, 14) - 10.0)
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
		Phase.FALL:
			_draw_fall()
		Phase.RECORD:
			_draw_record()
	_draw_board_marks()
	_draw_legend()
	_draw_hint()


## The HUD numbers for the phase. The leg value counts the ghost's Heat as soon as the ghost is placed.
func _hud_values() -> Dictionary:
	var v := {"heat": int(st["heat"]), "note": "", "bank": int(st["bank"]), "hp": int(st["home_hp"]), "score": _score_text(st),
		"sstate": st}
	match phase:
		Phase.PLAN, Phase.FORECAST:
			var lh := L8Rules.launch_heat(st, place)
			if lh != int(st["heat"]):
				v["note"] = "ghost +%d" % L8Rules.GHOST_HEAT
				var gs := st.duplicate()
				gs["heat"] = lh
				v["score"] = _score_text(gs)
				v["sstate"] = gs
			v["heat"] = lh
		Phase.PLAY, Phase.REVEAL, Phase.RESPONSE:
			var bs := before.duplicate()
			bs["heat"] = heat_launch
			v["heat"] = heat_launch
			v["note"] = "at launch"
			v["hp"] = hud_hp
			v["score"] = _score_text(bs)
			v["sstate"] = bs
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
	# Heat thresholds as ghost beams on the corp tower: one per extra the Heat brings, a faint one for the next.
	var ghosts := L8Rules.extra_count(heat)
	if ghosts != heat_ghosts_k:
		heat_ghosts_k = ghosts
		board.set_heat_ghosts(ghosts, ghosts < 2)
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
		_t(Vector2(nx + 4.0, 7.0), "%d %s" % [int(n[0]), String(n[1])], 12, RED if lit else DIM)
	_t(Vector2(hx + hw + 12.0, 14.0), str(heat), 28, HEAT_COL)
	if String(v["note"]) != "":
		_t(Vector2(hx + hw + 62.0, 24.0), _fit(String(v["note"]), 12, 92.0), 12, DIM)
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
	_t(Vector2(750.0, 47.0), _fit(_parts_text(v["sstate"]), 12, VIEW.x - PAD - 750.0), 12, DIM)
	var tag := "L8 CITY RAID  |  leg %d" % leg_seed
	if auto_line != "":
		tag += "  |  auto %s" % auto_line
	_tr(Vector2(VIEW.x - PAD, 8.0), tag, 12, DIM)
	_tr(Vector2(VIEW.x - PAD, 26.0), "speed %dx%s" % [int(speed), "  instant" if instant else ""], 12, DIM)


## Overlay marks on the board: cell tags, the hovered cell, repair costs, the picked repair and redeploy source (white
## check rings), and the previewed DEPLOY row's lines from the reserve tray to its target districts.
func _draw_board_marks() -> void:
	if phase in [Phase.PLAN, Phase.FORECAST, Phase.RESPONSE, Phase.AFTER, Phase.BETWEEN, Phase.DECAY, Phase.FALL]:
		for c: Vector2i in L8Rules.CELLS:
			_tc(_screen(c) + Vector2(0.0, 36.0), _cell_name(c), 12, Color(DIM, 0.9))
	if phase == Phase.BETWEEN:
		for cv: Variant in _down_cells():
			var c: Vector2i = cv
			var p := _screen(c)
			var cost := L8Rules.repair_cost(leg, c, b_inten)
			_tc(p + Vector2(0.0, -50.0), "free" if cost == 0 else "-%d" % cost, 15, AMBER)
		if not _none(b_repair):
			_check_ring(_screen(b_repair))
	if phase == Phase.RESPONSE:
		if not _none(redeploy_from):
			_check_ring(_screen(redeploy_from))
		var j := _preview_row()
		if j >= 0:
			var pv := _preview_of(j)
			for mv: Variant in pv["moves"]:
				var m: Dictionary = mv
				if String(m["kind"]) != "DEPLOY":
					continue
				var t := String(m["type"])
				var col: Color = TYPE_COLOR.get(t, ACID)
				var a: Vector2 = tray_pos.get(t, Vector2(PANEL_X, HUD_H + 120.0))
				var b := _screen(m["to"])
				ui.draw_line(a, b, Color(col, 0.7), 2.0)
				ui.draw_arc(b, 30.0, 0.0, TAU, 32, col, 2.5)
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
			if cap_slots > 1:
				return "CAPTURE: claim %d of %d (HOT perk). Click a glowing district, or its row in the panel." % [cap_cells.size() + 1, cap_slots]
			return "CAPTURE: click a glowing district, or its row in the panel."
		Phase.PLAN:
			return "PLAN: 1 2 3 a sentry (2 at most), G the ghost, click a district (again to lift). Q W E a route, H the hunter street. Z undoes, Enter forecasts."
		Phase.FORECAST:
			if launch_armed:
				return "FORECAST: Enter again launches anyway; B or any edit returns to the plan."
			if fric > 0:
				return "FORECAST: this launch needs a second Enter. Q W E a route, H the hunter street, B goes back."
			return "FORECAST: Q W E or a row shows a route, H the hunter street. Enter launches, B goes back; any edit returns to the plan."
		Phase.PLAY, Phase.REVEAL:
			return "PLAYOUT: 1 2 4 set the speed, I toggles instant."
		Phase.RESPONSE:
			return "RESPONSE: H holds, J jams, Up/Down + Enter or click a row (SACRIFICE too); a sentry then a district (REDEPLOY); 1 2 3 then a district (DEPLOY)."
		Phase.AFTER:
			return "AFTERMATH: Enter goes on."
		Phase.BETWEEN:
			return "BETWEEN: click a DOWN district (or its row) to repair it, B then 1 2 3 builds (0 for none), L N O sets the intensity, Enter starts the next raid."
		Phase.FALL:
			return "DECIDED: no plan can hold HOME. The record follows."
		Phase.RECORD:
			return "RECORD: Enter plays the leg again."
	return ""


func _draw_hint() -> void:
	var msg := status_msg if status_msg != "" else _hint()
	if auto_line != "" and status_msg == "":
		msg = "[AUTO %s] %s" % [auto_line.to_upper(), msg]
	_t(Vector2(16.0, HINT_Y + 3.0), _fit(msg, TXT, VIEW.x - 32.0), TXT, AMBER if status_msg != "" else DIM)


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


## The golden step's capture as a list of cells (L13: a list of 0 to 2 cells; a single cell or null is accepted too).
func _golden_caps(v: Variant) -> Array:
	var out: Array = []
	if typeof(v) != TYPE_ARRAY:
		if not _none(v):
			out.append(L8Rules.to_cell(v))
		return out
	var a: Array = v
	if a.size() == 2 and (typeof(a[0]) == TYPE_INT or typeof(a[0]) == TYPE_FLOAT):
		out.append(L8Rules.to_cell(a))
		return out
	for c: Variant in a:
		out.append(L8Rules.to_cell(c))
	return out


## Select the response row holding the golden response, so its preview shows on the board before the shot.
func _auto_select(r: Array) -> void:
	resp_sel = -1
	var key := str(r)
	for j in range(resp_rows.size()):
		for mv: Variant in resp_rows[j]["members"]:
			if str(resp_opts[int(mv)]["response"]) == key:
				resp_sel = j
				resp_follow = true
				return


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
	if s.has("hunt") and int(s["hunt"]) != int(row.get("hunt", -1)):
		push_warning("auto %s raid %d: hunter street %d, golden %d" % [auto_line, int(s["raid"]) + 1,
			int(row.get("hunt", -1)), int(s["hunt"])])
	if ok_tier and ok_score:
		print("auto %s raid %d: %s, score %s (matches the golden)" % [auto_line, int(s["raid"]) + 1, String(row["tier"]), _num(float(row["score"]))])
	else:
		push_warning("auto %s raid %d MISMATCH: lab %s %s, golden %s %s" % [auto_line, int(s["raid"]) + 1, String(row["tier"]),
			_num(float(row["score"])), String(s["tier"]), _num(float(s["score_raid"]))])


## Compare the cards' HOLDABLE / LOST verdicts with the golden's safe_next for the chosen repair and build.
func _verify_safe(s: Dictionary) -> void:
	var g: Variant = s.get("safe_next")
	if typeof(g) != TYPE_DICTIONARY:
		return
	var gd: Dictionary = g
	var bad := PackedStringArray()
	for k: Variant in gd:
		if (_safe(b_repair, b_build, String(k), true) == 1) != bool(gd[k]):
			bad.append(String(k))
	if bad.is_empty():
		print("auto %s raid %d: safe_next verdicts match the golden" % [auto_line, int(s["raid"]) + 1])
	else:
		push_warning("auto %s raid %d safe_next MISMATCH on %s" % [auto_line, int(s["raid"]) + 1, ", ".join(bad)])


## Replay the golden line's choices for this leg through the same UI handlers (every capture, place, response,
## between). DECAY runs on its own at the start of raids 2 and 3, so the golden's captures are made from the decayed
## state. The launch friction, when it shows, is shot and confirmed at once. When a between screen is DECIDED, the fall
## beat plays and the replay stops at the record.
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
			var caps := _golden_caps(s.get("capture"))
			for i in range(caps.size()):
				if phase != Phase.CAPTURE:
					break
				await _beat("r%d_capture" % rn if i == 0 else "r%d_capture%d" % [rn, i + 1])
				_do_capture(caps[i])
			if phase == Phase.CAPTURE:
				if caps.is_empty():
					await _beat("r%d_capture" % rn)
				push_warning("auto %s raid %d: capture left open, ending it" % [auto_line, rn])
				st = L8Rules.end_capture(st)
				_enter_plan()
		await _until([Phase.PLAN])
		_auto_place(L8Rules.place_from_json(s["place"]))
		await _beat("r%d_plan" % rn)
		_enter_forecast()
		await _beat("r%d_forecast" % rn)
		_launch()
		if phase == Phase.FORECAST and launch_armed:
			await _beat("r%d_launch_friction" % rn)
			_launch()
		await _until([Phase.RESPONSE])
		var resp := L8Rules.norm_response(s["response"])
		_auto_select(resp)
		await _beat("r%d_response" % rn)
		_auto_respond(resp)
		await _until([Phase.AFTER])
		_verify(s)
		await _beat("r%d_aftermath" % rn)
		_next()
		if phase == Phase.BETWEEN and typeof(s.get("between")) == TYPE_DICTIONARY:
			var b: Dictionary = s["between"]
			await _beat("r%d_between_open" % rn)
			_set_inten(String(b["intensity"]))
			if not _none(b["repair"]):
				_between_click(L8Rules.to_cell(b["repair"]))
			if not _none(b["build"]):
				_set_build(String(b["build"]))
			_verify_safe(s)
			await _beat("r%d_between_picked" % rn)
			_next()
	await _until([Phase.RECORD])
	await _beat("record")
	if shots_dir != "":
		get_tree().quit(0)
