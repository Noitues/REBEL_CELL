extends Control
## Raid lab L8 to L17: the playable city raid (docs/handoff/raid_lab_l8/SPEC.md section 8, with the L9_CHANGES.md,
## L10_CHANGES.md, L11_CHANGES.md, L12_CHANGES.md, L13_UI.md, L14_UI.md, L15_UI.md, L16_UI.md and L17_UI.md presentation
## applied). This is the root script of raid_lab_city.tscn, and everything is built in code. A 3D L8Board renders in a
## SubViewport behind a 2D overlay. The overlay holds the HUD, the right panel, the legend strip and the hint line. Two
## more Controls sit in the bottom bar: the deck strip (left edge, one pip per card, wounds as red cracked pips, hover
## shows the counts) and the hand row (the cards dealt this raid; wordless faces: verb glyph, type corner badge).
## Every state change goes through L8Rules. The view only reads its results and turns traces into board cues.
## Flow per raid:
## - DECAY (raids 2 and 3; each district lost adds a wound that flies into the deck strip);
## - CAPTURE (twice after a HOT between step);
## - DRAW: the run deck deals L8Rules.hand (base 4, +1 card at Heat 50 and 75, dealt with a gold edge);
## - PLAN: pick a hand card, then a district (at most 2). The HOLD forecast runs live, with the guard line, and each
##   route's worst tier stands at its HOME lane end (board.show_home_glyphs);
## - FORECAST: per sealed A, a 2 x 2 table (B route x hunter street) of HOLD outcomes as glyphs;
## - the known beams (one by one, each dimmed when done), REVEAL A, the RESPONSE, sealed A, REVEAL B, sealed B, the
##   HUNTER REVEAL and the hunter run (unless JAM);
## - AFTERMATH, BETWEEN (repair, add a D / N / E guard card or CLEAN a wound, intensity, all as icons), RECORD.
## L16:
## - response rows lead with a large verb glyph; hovering or selecting a row previews it on the board
##   (board.preview_response);
## - five tier shapes everywhere (L8Board.tier_icon), and a tier ladder pinned in the bottom bar, best to worst;
## - the playout collapses the side panel to a slim strip and fits the board wider (board.set_view_rect), and at
##   Heat >= 75 the board fans stacked markers out (board.set_fan);
## - panel text is at least 14 px and never truncated.
## L17:
## - the guard line "HOLD -> <tier> . best: <row> -> <tier>" (or "no response changes this") in PLAN (rows held over
##   all 12 outcomes) and in RESPONSE (over the 4 sealed outcomes). The best row has the highest worst tier, then the
##   highest mean score;
## - fast resolve (2x, no reveal holds, "FAST" chip) only when every response row yields the same tier on every
##   outcome; the RESPONSE panel is still skipped only when every row also changes nothing;
## - the HOLD confirm fires whenever HOLD's worst outcome loses a HOME pip that some visible row saves;
## - hovering a forecast cell or a response row draws that outcome on the city as a ghost overlay
##   (board.show_outcome_ghost); under --auto the chosen row (and the selected forecast cell) are drawn for their beat;
## - the intensity cards show the net leg value as one large signed number, with captures, income and Heat icons.
## Launch friction (L15): a second Enter is needed when HOME drops on every one of the 12 HOLD outcomes, or whenever
## HOME is at 1.
## Flags (after --): --leg=N (golden seeds 0 3 5 8), --auto=greedy|naive, --shots=<abs dir> (with --auto), --scramble.

enum Phase { CAPTURE, DRAW, PLAN, FORECAST, PLAY, REVEAL, RESPONSE, AFTER, BETWEEN, RECORD, DECAY, FALL }

const GOLDEN_PATH := "res://tools/raid_lab_city/data/l8_golden.json"
const VIEW := Vector2(1280.0, 720.0)
const PANEL_W := 420.0
const PANEL_X := 860.0
## L16 item 6: the slim strip during the playout.
const SLIM_W := 250.0
const SLIM_X := 1030.0
const PAD := 16.0
const HUD_H := 64.0
const LEGEND_Y := 672.0
const HINT_Y := 698.0
const PICK_R := 40.0
const HOME_CELL := Vector2i(-1, 1)
const HEAT_MAX := 100.0
## Response list (L15): a group row (two lines), a variant row in the hover list, a ghost / fold row.
const GROUP_H := 44.0
const SUB_H := 22.0
const GHOST_H := 24.0
const MAX_GROUPS := 8
const POP_W := 260.0
const RESP_GLYPH_W := 34.0
const AUTO_WAIT := 0.6
const UNTIL_GUARD := 60000
const SCRAMBLE_SEED := 8808
const LETHAL_HZ := 1.5
const LINE_ID := {"beam1": 10, "extra1": 11, "extra2": 12, "sealed": 13, "hunter": 14, "sealed_b": 15}
const BEAM_NAME := {"beam1": "BEAM 1", "extra1": "EXTRA 1", "extra2": "EXTRA 2", "sealed": "SEALED A",
	"sealed_b": "SEALED B", "hunter": "HUNTER"}
const CELL_ROW := ["NOR", "MID", "SOU"]
const INTEN_KEY := ["L", "N", "O"]
const ROUTE_KEY := ["Q", "W", "E"]
const HUNT_KEY := ["A", "B"]
const CARD_H := 160.0
## Panel text never goes below this size (L16 item 7).
const TXT := 14
## The bottom bar, the HUD's small labels and the board tags (outside the panel).
const BAR_TXT := 13
const SAFE_BUDGET_MS := 12
const REP_ROW_H := 22.0
const MEAN_EPS := 1e-6
const FRICTION_BREACH := "Every outcome breaks HOME with this plan: change it?"
const FRICTION_LOSS := "Every outcome costs HOME with this plan: change it?"
const FRICTION_LAST := "HOME is at 1/3: one hit ends the campaign. Launch?"
const FRICTION_HOLD := "HOLD is worse than"
const TIER_RANK := {"EVADED": 0, "HOLDS": 1, "BATTERED": 2, "DAMAGED": 3, "BREACHED": 4}
## L16 item 3: the tier ladder, best to worst.
const TIER_LADDER := ["EVADED", "HOLDS", "BATTERED", "DAMAGED", "BREACHED"]
## L16 item 1: a fast launch plays at this multiple of the chosen speed; other reveals hold this long (at 1x).
const FAST_K := 2.0
const REVEAL_HOLD := 0.45
## The bottom bar (L14): the deck strip at the left edge, the hand row right of it.
const DECK_W := 66.0
const HAND_X := 74.0
const HCARD_W := 110.0
const HCARD_H := 42.0
const HCARD_GAP := 6.0
const DECK_POS := Vector2(33.0, 696.0)
const DEAL_T := 0.28
const DEAL_GAP := 0.12
const FLY_T := 0.35
const PIP_COLS := 7

# Palette (matches l8_board.gd).
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
const WOUND_FILL := Color8(40, 42, 50)
const HOLDS_COL := Color8(63, 224, 176)
const TYPE_COLOR := {"D": Color8(92, 225, 255), "N": Color8(255, 64, 214), "E": Color8(255, 140, 26)}
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
var hand_ui: Control
var deck_ui: Control
var cv: CanvasItem
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
var hand_ids: Array = []
var hand_cards: Array = []
var sel_card: String = ""
var deal_t0: float = 0.0
var deck_view: Array = []
var deck_live: bool = true
var fly_cards: Array = []
var hand_hits: Array = []
var place: Dictionary = {"sentries": {}, "ghost": null}
var undo: Array = []
var tool: String = ""
## The live HOLD forecast of the current placement (computed in PLAN, kept through the launch).
var fc: Array = []
## The worst and best HOLD tier over the 12 forecast outcomes; fc_locked is the tier when they all agree, else "".
var fc_range: Array = ["HOLDS", "HOLDS"]
var fc_locked: String = ""
## L17 item 1: the guard of the plan (every row held over the 12 outcomes) and of the RESPONSE (over the 4 outcomes):
## {hold: tier, best: {response, worst, mean} or {}, uniform: bool, sent: sentries}.
var plan_guard: Dictionary = {}
var resp_guard: Dictionary = {}
## L17 item 2: the hovered forecast cell [k, bi, h], the shown ghost overlay's key and the auto line's chosen option.
var fc_hover: Array = []
var ghost_key: String = ""
var auto_opt: int = -1
var fric: int = 0
var launch_armed: bool = false
var route_v: Array = []
var sel_route: int = 0
var sel_b: int = 0
var sel_hunt: int = 0
var sel_hold: Dictionary = {}
var rd: Dictionary = {}
var real: int = 0
var real_b: int = 1
var hunt: int = 0
var hunter_revealed: bool = false
var cur_resp: Array = ["HOLD"]
var used_card: String = ""
var before: Dictionary = {}
var heat_launch: int = 0
var mid: Dictionary = {}
var known_tr: Array = []
var known_last: String = "beam1"
var stage: String = ""
## Every legal response with its 4 outcomes: {response, outs, card, mean, core, key, paid, nothing, better}.
var resp_opts: Array = []
## The visible response groups (merged by identical outcomes): {members: [option index], better, mean, first}.
var resp_groups: Array = []
## Ghost rows: [head, text] per impossible kind.
var resp_ghosts: Array = []
var hold_mean: float = 0.0
var redeploy_from: Variant = null
var deploy_type: String = ""
var resp_page: int = 0
var resp_sel: int = -1
var resp_open: int = -1
var resp_hover_opt: int = -1
var resp_head_y: Dictionary = {}
var resp_pop_rect: Rect2 = Rect2()
var resp_follow: bool = false
var resp_prev: int = -2
var resp_skipped: bool = false
## HOLD needs a second commit; hold_better is the group that saves the HOME pip HOLD loses (L17 item 1).
var hold_armed: bool = false
var hold_better: int = -1
var result: Dictionary = {}
var b_repair: Variant = null
var b_build: Variant = null
var b_inten: String = "NORMAL"
var build_armed: bool = false
var safe_cache: Dictionary = {}
var next_cache: Dictionary = {}
var safe_pending: Dictionary = {}
var b_hash: int = 0
var b_all_unsafe: int = -1
var decay_lines: PackedStringArray = PackedStringArray()

var busy: bool = false
var speed: float = 1.0
var instant: bool = false
## L17 item 1: this launch plays fast (every row, one tier on every outcome).
var fast: bool = false
## L16 item 6: the side panel is a slim strip.
var slim: bool = false
var fan_on: bool = false
var tier_tex: Dictionary = {}
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
	cv = ui
	deck_ui = Control.new()
	deck_ui.position = Vector2(0.0, LEGEND_Y)
	deck_ui.size = Vector2(DECK_W, VIEW.y - LEGEND_Y)
	deck_ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(deck_ui)
	deck_ui.draw.connect(_draw_deck)
	hand_ui = Control.new()
	hand_ui.position = Vector2(DECK_W, LEGEND_Y)
	hand_ui.size = Vector2(PANEL_X - DECK_W, VIEW.y - LEGEND_Y)
	hand_ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(hand_ui)
	hand_ui.draw.connect(_draw_hand)
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
	route_v = []
	safe_pending = {}
	hand_ids = []
	hand_cards = []
	sel_card = ""
	deck_live = true
	deck_view = []
	fly_cards = []
	fc = []
	fc_locked = ""
	plan_guard = {}
	resp_guard = {}
	fast = false
	hold_armed = false
	hold_better = -1
	auto_opt = -1
	hud_hp = int(st["home_hp"])
	board.setup({"w": L8Rules.W, "h": L8Rules.H, "values": leg["values"], "exploits": leg["exploits"]})
	board.set_scramble(scramble)
	lethal_on = int(st["home_hp"]) == 1
	board.set_lethal(lethal_on)
	heat_ghosts_k = -1
	fan_on = false
	board.set_fan(false)
	slim = false
	_apply_view()
	board.set_speed(speed)
	board.clear_outcome()
	board.clear_response_preview()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	_clear_b()
	_clear_home_glyphs()
	_clear_ghost()
	resp_prev = -2
	_show_st(st, _empty_place())
	_begin_raid()


func _process(_delta: float) -> void:
	if phase == Phase.BETWEEN and not safe_pending.is_empty():
		_work_safe()
	ui.queue_redraw()
	hand_ui.queue_redraw()
	deck_ui.queue_redraw()


# ---------------------------------------------------------------- small helpers
func _none(v: Variant) -> bool:
	return typeof(v) == TYPE_NIL


func _is_home(v: Variant) -> bool:
	return typeof(v) == TYPE_STRING and String(v) == L8Rules.HOME


func _empty_place() -> Dictionary:
	return {"sentries": {}, "ghost": null}


## The left edge of the side panel (the slim strip during the playout).
func _px() -> float:
	return SLIM_X if slim else PANEL_X


## L16 item 6: the free board area the camera fills (left of the panel or of the slim strip).
func _apply_view() -> void:
	board.set_view_rect(Rect2(0.0, HUD_H, _px(), LEGEND_Y - 2.0 - HUD_H))


func _set_slim(on: bool) -> void:
	if slim == on:
		return
	slim = on
	_apply_view()


## The playout speed (doubled for a fast launch).
func _pspeed() -> float:
	return speed * (FAST_K if fast else 1.0)


## The card lookup the board reads: {id: [type, verb]} for every card of the state's deck.
func _cards_lookup(s: Dictionary) -> Dictionary:
	var out := {}
	for cd: Array in s.get("deck", []):
		out[String(cd[0])] = [String(cd[1]), String(cd[2])]
	return out


## Show a state and a placement on the board (card-id sentries with their card lookup).
func _show_st(s: Dictionary, p: Dictionary) -> void:
	board.show_state(s, p, _cards_lookup(s))


## Remove the B candidates when the board offers it.
func _clear_b() -> void:
	if board.has_method("clear_b_cands"):
		board.call("clear_b_cands")


## L15 item 10: each route's worst tier at its HOME lane end (one tier per route 0..2).
func _show_home_glyphs(per_route: Array) -> void:
	if board.has_method("show_home_glyphs"):
		board.call("show_home_glyphs", per_route)


func _clear_home_glyphs() -> void:
	if board.has_method("clear_home_glyphs"):
		board.call("clear_home_glyphs")


## L15 item 6: a beam has finished (the board dims it).
func _beam_done(beam: String) -> void:
	if board.has_method("set_beam_done"):
		board.call("set_beam_done", beam)


## L17 item 2: remove the ghost outcome overlay from the board.
func _clear_ghost() -> void:
	ghost_key = ""
	if board.has_method("clear_outcome_ghost"):
		board.call("clear_outcome_ghost")


func _hand_card(id: String) -> Array:
	for cd: Array in hand_cards:
		if String(cd[0]) == id:
			return cd
	return []


## The type of a card id (hand first, then the deck of the state or before).
func _ctype(id: String) -> String:
	var cd := _hand_card(id)
	if not cd.is_empty():
		return String(cd[1])
	var t := L8Rules.card_type(st, id)
	if t == "" and not before.is_empty():
		t = L8Rules.card_type(before, id)
	return t


func _cverb(id: String) -> String:
	var cd := _hand_card(id)
	if not cd.is_empty():
		return String(cd[2])
	var c2 := L8Rules.card_of(st, id)
	return "" if c2.is_empty() else String(c2[2])


func _hand_phase() -> bool:
	return phase in [Phase.DRAW, Phase.PLAN, Phase.FORECAST, Phase.PLAY, Phase.REVEAL, Phase.RESPONSE]


func _deck_shown() -> Array:
	if deck_live:
		return st.get("deck", [])
	return deck_view


func _wounds_in(deck: Array) -> int:
	var n := 0
	for cd: Array in deck:
		if String(cd[2]) == L8Rules.V_WOUND:
			n += 1
	return n


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


func _signed(f: float) -> String:
	return ("+" if f >= 0.0 else "-") + _num(absf(f))


func _score_text(s: Dictionary) -> String:
	if int(s["home_hp"]) <= 0:
		return "campaign lost"
	return _num(L8Rules.score(leg, s))


## The one-line breakdown of the leg value (compact, so it never truncates).
func _parts_text(s: Dictionary) -> String:
	if s.is_empty():
		return ""
	var sp: Dictionary = L8Rules.score_parts(leg, s)
	if bool(sp["breach"]):
		return "a breach leaves no score"
	return "bank %d + districts %d + exploits %d - HOME %d - Heat %s - wounds %d" % [int(sp["bank"]), int(sp["cells"]),
		int(sp["exploits"]), int(sp["home_loss"]), _num(float(sp["heat_carry"])), int(sp["wounds"])]


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


func _rank(t: String) -> int:
	return int(TIER_RANK.get(t, 0))


## [worst, best] tier over outcomes that carry "tier".
func _tier_range(outs: Array) -> Array:
	var worst := ""
	var best := ""
	for ov: Variant in outs:
		var t := String((ov as Dictionary)["tier"])
		if worst == "" or _rank(t) > _rank(worst):
			worst = t
		if best == "" or _rank(t) < _rank(best):
			best = t
	if worst == "":
		return ["HOLDS", "HOLDS"]
	return [worst, best]


## The lowest HOME over outcomes that carry "state".
func _min_hp(outs: Array) -> int:
	var lo := 99
	for ov: Variant in outs:
		lo = mini(lo, int(((ov as Dictionary)["state"] as Dictionary)["home_hp"]))
	return lo


## The worst outcome: the highest tier rank, then the lowest score.
func _worst_out(outs: Array) -> Dictionary:
	var best: Dictionary = {}
	var bs := 0.0
	for ov: Variant in outs:
		var o: Dictionary = ov
		var t := _rank(String(o["tier"]))
		var s := L8Rules.score(leg, o["state"])
		if best.is_empty() or t > _rank(String(best["tier"])) or (t == _rank(String(best["tier"])) and s < bs - MEAN_EPS):
			best = o
			bs = s
	return best


## Nested [[o per hunt] per B] flattened in order.
func _flat(rows: Array) -> Array:
	var out: Array = []
	for rv: Variant in rows:
		out.append_array(rv as Array)
	return out


func _hunt_street(h: int) -> int:
	return int((leg["raids"][raid]["hunter_cands"] as Array)[h])


func _cand_b() -> int:
	return int(L8Rules.other_cands(sel_route)[sel_b])


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
	var t := _ctype(String(sentries.get(r[1], "")))
	return "MOVE %s %s > %s" % [_tname(t), _cell_name(r[1]), _cell_name(r[2])]


## A placement in words: "DRONE GUARD on NOR 0, ghost on HOME".
func _place_text(p: Dictionary) -> String:
	var parts := PackedStringArray()
	var sd: Dictionary = p.get("sentries", {})
	for c: Vector2i in L8Rules.sorted_cells(sd):
		var id := String(sd[c])
		parts.append("%s %s on %s" % [_tname(_ctype(id)), _cverb(id), _cell_name(c)])
	var g: Variant = p.get("ghost")
	if _is_home(g):
		parts.append("ghost on HOME")
	elif typeof(g) == TYPE_VECTOR2I:
		parts.append("ghost on " + _cell_name(g))
	if parts.is_empty():
		return "no sentries, no ghost"
	return ", ".join(parts)


func _placed_total() -> int:
	return (place.get("sentries", {}) as Dictionary).size()


## The cell a card id is placed on in the plan, or null.
func _card_cell(id: String) -> Variant:
	var sd: Dictionary = place.get("sentries", {})
	for c: Vector2i in L8Rules.sorted_cells(sd):
		if String(sd[c]) == id:
			return c
	return null


func _screen(c: Variant) -> Vector2:
	if typeof(c) == TYPE_VECTOR2I:
		var v: Vector2i = c
		return board.cell_screen_pos(v)
	return board.cell_screen_pos(HOME_CELL)


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


func _state_hash(s: Dictionary) -> int:
	return str(L8Rules.state_to_json(s)).hash()


func _card_rect(i: int) -> Rect2:
	return Rect2(HAND_X + float(i) * (HCARD_W + HCARD_GAP), LEGEND_Y + 3.0, HCARD_W, HCARD_H)


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
	cv.draw_string(font, p + Vector2(0.0, font.get_ascent(size)), _scr(text), HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _tw(text: String, size: int) -> float:
	return font.get_string_size(_scr(text), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x


func _tc(center: Vector2, text: String, size: int = TXT, col: Color = INK) -> void:
	_t(center - Vector2(_tw(text, size) * 0.5, font.get_height(size) * 0.5), text, size, col)


func _tr(p: Vector2, text: String, size: int = TXT, col: Color = INK) -> void:
	_t(Vector2(p.x - _tw(text, size), p.y), text, size, col)


## The line height for a font size.
func _lh(size: int) -> float:
	return float(size) + 5.0


## The largest size from size down to TXT at which text fits maxw (TXT when none does).
func _fsize(text: String, size: int, maxw: float) -> int:
	var s := size
	while s > TXT and _tw(text, s) > maxw:
		s -= 1
	return s


## Word-wrapped lines no wider than maxw (a single word wider than maxw keeps its own line).
func _wrap(text: String, size: int, maxw: float) -> PackedStringArray:
	var out := PackedStringArray()
	var cur := ""
	for word: String in text.split(" "):
		var cand := word if cur == "" else cur + " " + word
		if cur != "" and _tw(cand, size) > maxw:
			out.append(cur)
			cur = word
		else:
			cur = cand
	if cur != "" or out.is_empty():
		out.append(cur)
	return out


## Wrapped text (panel lines wrap, never "..."). Returns the height used.
func _tf(p: Vector2, text: String, size: int = TXT, col: Color = INK, right_x: float = VIEW.x - PAD) -> float:
	var ls := _wrap(text, size, right_x - p.x)
	for i in range(ls.size()):
		_t(p + Vector2(0.0, float(i) * _lh(size)), ls[i], size, col)
	return float(ls.size()) * _lh(size)


## One line, shrunk from size down to TXT to fit; wrapped at TXT when even that is too wide. Returns the height used.
func _ts(p: Vector2, text: String, size: int = TXT, col: Color = INK, right_x: float = VIEW.x - PAD) -> float:
	var maxw := right_x - p.x
	var s := _fsize(text, size, maxw)
	if _tw(text, s) <= maxw:
		_t(p, text, s, col)
		return _lh(s)
	return _tf(p, text, TXT, col, right_x)


func _box(r: Rect2, edge: Color, fill: Color, w: float = 2.0) -> void:
	cv.draw_rect(r, fill)
	cv.draw_rect(r, edge, false, w)


func _btn(r: Rect2, label: String, id: String, on: bool = true, sel: bool = false, size: int = 14) -> void:
	var hot := on and r.has_point(mouse)
	_box(r, (AMBER if sel else (INK if hot else EDGE)) if on else EDGE.darkened(0.4), PANEL_HI if (sel or hot) else PANEL)
	_tc(r.get_center(), label, _fsize(label, size, r.size.x - 10.0), INK if on else DIM)
	if on:
		hits.append({"rect": r, "id": id})


func _head(title: String, todo: String, x: float = PANEL_X + PAD) -> float:
	_t(Vector2(x, HUD_H + 10.0), title, _fsize(title, 20, VIEW.x - PAD - x), AMBER)
	var h := _tf(Vector2(x, HUD_H + 38.0), todo, TXT, INK)
	return HUD_H + 38.0 + maxf(h, 18.0) + 8.0


# ---------------------------------------------------------------- glyphs
func _glyph(c: Vector2, t: String, r: float, col: Color) -> void:
	match t:
		"D":
			cv.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -r), c + Vector2(r * 0.9, r * 0.65),
				c + Vector2(-r * 0.9, r * 0.65)]), col)
		"N":
			cv.draw_rect(Rect2(c - Vector2(r, r) * 0.75, Vector2(r, r) * 1.5), col)
		_:
			cv.draw_circle(c, r * 0.8, col)


## A crack polyline (wound cards and pips).
func _crack(c: Vector2, r: float, col: Color, w: float = 2.0) -> void:
	cv.draw_polyline(PackedVector2Array([c + Vector2(-r * 0.2, -r), c + Vector2(r * 0.25, -r * 0.35),
		c + Vector2(-r * 0.2, r * 0.1), c + Vector2(r * 0.2, r * 0.55), c + Vector2(0.0, r)]), col, w)


func _xmark(c: Vector2, r: float, col: Color, w: float = 2.0) -> void:
	cv.draw_line(c + Vector2(-r, -r), c + Vector2(r, r), col, w)
	cv.draw_line(c + Vector2(r, -r), c + Vector2(-r, r), col, w)


## The card's verb glyph: GUARD shield, SHIFT curved arrow, JAM zigzag, WOUND crack.
func _verb_glyph(c: Vector2, verb: String, r: float, col: Color) -> void:
	var lw := maxf(1.5, r * 0.2)
	match verb:
		"GUARD":
			cv.draw_colored_polygon(_shield_pts(c, r), col)
		"SHIFT":
			var rr := r * 0.75
			cv.draw_arc(c + Vector2(0.0, r * 0.2), rr, PI, TAU, 14, col, lw)
			var e := c + Vector2(rr, r * 0.2)
			cv.draw_colored_polygon(PackedVector2Array([e + Vector2(-r * 0.4, -r * 0.05), e + Vector2(r * 0.4, -r * 0.05),
				e + Vector2(0.0, r * 0.55)]), col)
		"JAM":
			cv.draw_polyline(PackedVector2Array([c + Vector2(-r, r * 0.2), c + Vector2(-r * 0.5, -r * 0.6),
				c + Vector2(0.0, r * 0.6), c + Vector2(r * 0.5, -r * 0.6), c + Vector2(r, r * 0.2)]), col, lw)
		"WOUND":
			_crack(c, r, col, lw)


## L15 item 7: a wordless card face in r. The verb glyph dominates; the type shape is a corner badge in its color. A
## wound is a cracked gray card with a red X.
func _card_face(r: Rect2, cd: Array, dim: bool = false) -> void:
	if cd.is_empty():
		return
	var s := minf(r.size.x, r.size.y)
	if L8Rules.is_wound(cd):
		_box(r, GREY, WOUND_FILL, 1.5)
		var c := r.get_center()
		_crack(c, s * 0.4, GREY.lightened(0.2), maxf(1.5, s * 0.06))
		_xmark(c, s * 0.28, RED.darkened(0.35) if dim else RED, maxf(1.5, s * 0.09))
		return
	var t := String(cd[1])
	var tc: Color = TYPE_COLOR.get(t, GREY)
	_box(r, EDGE.darkened(0.4) if dim else EDGE, PANEL, 1.5)
	_verb_glyph(r.get_center() + Vector2(0.0, s * 0.05), String(cd[2]), s * 0.32, DIM if dim else INK)
	var br := maxf(3.0, s * 0.13)
	_glyph(r.position + Vector2(br + 3.0, br + 3.0), t, br, tc.darkened(0.45) if dim else tc)


## A small card chip (34 x 20). Returns its width + gap.
func _mini_card(p: Vector2, cd: Array) -> float:
	if cd.is_empty():
		return 0.0
	_card_face(Rect2(p, Vector2(34.0, 20.0)), cd)
	return 38.0


func _ghost_icon(c: Vector2, r: float, col: Color) -> void:
	for k in range(8):
		var a := TAU * float(k) / 8.0
		cv.draw_arc(c, r, a, a + TAU / 16.0, 4, col, 2.0)


func _sentry_icon(c: Vector2, t: String) -> void:
	var col: Color = TYPE_COLOR.get(t, GREY)
	cv.draw_rect(Rect2(c + Vector2(-5.0, 6.0), Vector2(10.0, 3.0)), GREY)
	cv.draw_line(c + Vector2(0.0, 6.0), c + Vector2(0.0, -3.0), GREY, 2.0)
	_glyph(c + Vector2(0.0, -7.0), t, 5.0, col)


func _down_icon(c: Vector2) -> void:
	cv.draw_circle(c, 8.0, GREY.darkened(0.4))
	cv.draw_line(c + Vector2(-4.0, 4.0), c + Vector2(4.0, -4.0), INK, 2.5)
	cv.draw_arc(c + Vector2(4.0, -4.0), 2.5, 0.0, TAU, 8, INK, 1.5)


func _wrench_icon(c: Vector2, col: Color) -> void:
	cv.draw_line(c + Vector2(-6.0, 6.0), c + Vector2(3.0, -3.0), col, 3.0)
	cv.draw_arc(c + Vector2(4.0, -4.0), 3.5, 0.0, TAU, 12, col, 2.0)


func _flag_icon(c: Vector2, col: Color) -> void:
	cv.draw_line(c + Vector2(0.0, 7.0), c + Vector2(0.0, -7.0), col, 1.5)
	cv.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -7.0), c + Vector2(8.0, -4.0), c + Vector2(0.0, -1.0)]), col)


func _coin(c: Vector2, r: float, col: Color = GOLD) -> void:
	cv.draw_circle(c, r, col)
	cv.draw_arc(c, r * 0.6, 0.0, TAU, 12, col.darkened(0.45), maxf(1.0, r * 0.25))


func _taken_icon(c: Vector2) -> void:
	cv.draw_rect(Rect2(c - Vector2(7.0, 7.0), Vector2(14.0, 14.0)), COBALT)
	cv.draw_rect(Rect2(c - Vector2(7.0, 7.0), Vector2(14.0, 14.0)), COBALT_HOT, false, 1.5)


func _key_icon(c: Vector2, col: Color) -> void:
	cv.draw_arc(c + Vector2(-5.0, 0.0), 3.5, 0.0, TAU, 12, col, 2.0)
	cv.draw_line(c + Vector2(-1.5, 0.0), c + Vector2(8.0, 0.0), col, 2.0)
	cv.draw_line(c + Vector2(6.0, 0.0), c + Vector2(6.0, 4.0), col, 2.0)
	cv.draw_line(c + Vector2(3.0, 0.0), c + Vector2(3.0, 3.0), col, 2.0)


func _hound_icon(c: Vector2, col: Color = COBALT_HOT) -> void:
	cv.draw_rect(Rect2(c + Vector2(-7.0, -3.0), Vector2(11.0, 5.0)), col)
	cv.draw_rect(Rect2(c + Vector2(3.0, -7.0), Vector2(6.0, 5.0)), col)
	for lx: float in [-6.0, -3.0, 0.0, 3.0]:
		cv.draw_line(c + Vector2(lx, 2.0), c + Vector2(lx, 7.0), col, 1.5)


func _skull(c: Vector2, r: float, col: Color, hole: Color) -> void:
	cv.draw_circle(c + Vector2(0.0, -r * 0.15), r * 0.8, col)
	cv.draw_rect(Rect2(c + Vector2(-r * 0.45, r * 0.3), Vector2(r * 0.9, r * 0.6)), col)
	cv.draw_circle(c + Vector2(-r * 0.32, -r * 0.15), r * 0.22, hole)
	cv.draw_circle(c + Vector2(r * 0.32, -r * 0.15), r * 0.22, hole)
	var tw := maxf(1.0, r * 0.12)
	cv.draw_line(c + Vector2(-r * 0.15, r * 0.5), c + Vector2(-r * 0.15, r * 0.9), hole, tw)
	cv.draw_line(c + Vector2(r * 0.15, r * 0.5), c + Vector2(r * 0.15, r * 0.9), hole, tw)


## A heart (two lobes and a point); broken adds a dark zigzag.
func _heart(c: Vector2, r: float, col: Color, broken: bool) -> void:
	cv.draw_circle(c + Vector2(-r * 0.45, -r * 0.2), r * 0.5, col)
	cv.draw_circle(c + Vector2(r * 0.45, -r * 0.2), r * 0.5, col)
	cv.draw_colored_polygon(PackedVector2Array([c + Vector2(-r * 0.93, -r * 0.05), c + Vector2(r * 0.93, -r * 0.05),
		c + Vector2(0.0, r * 0.95)]), col)
	if broken:
		cv.draw_polyline(PackedVector2Array([c + Vector2(0.0, -r * 0.55), c + Vector2(r * 0.18, -r * 0.15),
			c + Vector2(-r * 0.15, r * 0.2), c + Vector2(r * 0.1, r * 0.55), c + Vector2(0.0, r * 0.9)]), BG,
			maxf(1.5, r * 0.22))


## HOME after an outcome, as a tier icon (L16 item 3): kept HOLDS, lost integrity DAMAGED, at 0 BREACHED.
func _home_glyph(c: Vector2, hp: int, hp0: int, r: float) -> void:
	var t := "HOLDS"
	if hp <= 0:
		t = "BREACHED"
	elif hp < hp0:
		t = "DAMAGED"
	_tier_glyph(c, t, r, _tier_col(t))


func _flame(c: Vector2, r: float) -> void:
	cv.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -r * 1.35), c + Vector2(r * 0.5, -r * 0.45),
		c + Vector2(r * 0.75, r * 0.3), c + Vector2(r * 0.4, r * 0.85), c + Vector2(-r * 0.4, r * 0.85),
		c + Vector2(-r * 0.75, r * 0.3), c + Vector2(-r * 0.35, -r * 0.5)]), HEAT_COL)
	cv.draw_circle(c + Vector2(0.0, r * 0.35), r * 0.38, YELLOW)


func _beam_icons(p: Vector2, types: Array, k: int) -> float:
	var x := p.x
	for j in range(mini(k, types.size())):
		var t := String(types[j])
		var col: Color = TYPE_COLOR.get(t, GREY)
		var c := Vector2(x, p.y)
		cv.draw_line(c + Vector2(-6.0, 0.0), c + Vector2(1.0, 0.0), col, 2.0)
		_glyph(c + Vector2(4.5, 0.0), t, 4.5, col)
		x += 17.0
	return x


## L15 item 9: the "+1 beam" tick icon (a short beam with a head).
func _beam_tick(c: Vector2, col: Color) -> void:
	cv.draw_line(c + Vector2(-6.0, 0.0), c + Vector2(2.0, 0.0), col, 2.0)
	cv.draw_colored_polygon(PackedVector2Array([c + Vector2(1.0, -4.0), c + Vector2(6.0, 0.0), c + Vector2(1.0, 4.0)]), col)


## L15 item 9: the "+1 card" tick icon (a small card with a plus).
func _card_tick(c: Vector2, col: Color) -> void:
	var r := Rect2(c - Vector2(4.5, 6.0), Vector2(9.0, 12.0))
	cv.draw_rect(r, PANEL)
	cv.draw_rect(r, col, false, 1.5)
	cv.draw_line(c + Vector2(-2.0, 0.0), c + Vector2(2.0, 0.0), col, 1.5)
	cv.draw_line(c + Vector2(0.0, -2.0), c + Vector2(0.0, 2.0), col, 1.5)


func _check_ring(p: Vector2) -> void:
	cv.draw_arc(p, 34.0, 0.0, TAU, 40, WHITE, 3.0)
	var c := p + Vector2(24.0, -24.0)
	cv.draw_circle(c, 9.0, BLACK)
	cv.draw_arc(c, 9.0, 0.0, TAU, 20, WHITE, 1.5)
	cv.draw_polyline(PackedVector2Array([c + Vector2(-5.0, 0.0), c + Vector2(-1.5, 4.0), c + Vector2(5.0, -4.0)]), WHITE, 2.5)


func _tier_col(tier: String) -> Color:
	return TIER_COLOR.get(tier, INK)


func _shield_pts(c: Vector2, r: float) -> PackedVector2Array:
	return PackedVector2Array([c + Vector2(-r * 0.8, -r * 0.85), c + Vector2(r * 0.8, -r * 0.85),
		c + Vector2(r * 0.8, -r * 0.05), c + Vector2(0.0, r * 0.95), c + Vector2(-r * 0.8, -r * 0.05)])


## L16 item 3: the board's tier icon (cached; null falls back to the drawn shapes).
func _tier_tex(t: String) -> Texture2D:
	if tier_tex.has(t):
		return tier_tex[t]
	var tex: Texture2D = L8Board.tier_icon(t)
	tier_tex[t] = tex
	return tex


## A tier glyph of radius r: the board's tier icon, or the same five shapes drawn (HOLDS full shield, BATTERED
## cracked shield, DAMAGED broken heart, BREACHED skull, EVADED open eye).
func _tier_glyph(c: Vector2, tier: String, r: float, col: Color) -> void:
	var tex := _tier_tex(tier)
	if tex != null:
		cv.draw_texture_rect(tex, Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0), false, Color(1.0, 1.0, 1.0, col.a))
		return
	var w := maxf(2.0, r * 0.3)
	match tier:
		"EVADED":
			cv.draw_arc(c + Vector2(0.0, r * 0.55), r, PI * 1.2, PI * 1.8, 12, col, w * 0.6)
			cv.draw_arc(c - Vector2(0.0, r * 0.55), r, PI * 0.2, PI * 0.8, 12, col, w * 0.6)
			cv.draw_circle(c, r * 0.32, col)
		"HOLDS":
			cv.draw_colored_polygon(_shield_pts(c, r), col)
		"BATTERED":
			cv.draw_colored_polygon(_shield_pts(c, r), col)
			cv.draw_polyline(PackedVector2Array([c + Vector2(-r * 0.1, -r * 0.9), c + Vector2(r * 0.25, -r * 0.35),
				c + Vector2(-r * 0.2, r * 0.1), c + Vector2(r * 0.15, r * 0.55), c + Vector2(0.0, r * 0.9)]), BG,
				maxf(1.5, r * 0.22))
		"DAMAGED":
			_heart(c, r, col, true)
		"BREACHED":
			_skull(c, r, col, BLACK)
		_:
			cv.draw_circle(c, r * 0.5, col)


func _tier_pip(c: Vector2, tier: String, r: float) -> void:
	var col := _tier_col(tier)
	var rect := Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)
	if tier == "BREACHED":
		cv.draw_rect(rect, BLACK)
		cv.draw_rect(rect, RED, false, 2.0)
	else:
		cv.draw_rect(rect, PANEL)
		cv.draw_rect(rect, col, false, 2.0)
	_tier_glyph(c, tier, r * 0.75, col)


func _tier_tag(right: Vector2, tier: String, size: int = TXT) -> float:
	var col := _tier_col(tier)
	var tw := _tw(tier, size)
	var h := font.get_height(size)
	var gr := float(size) * 0.5
	var gx := right.x - tw - gr - 6.0
	var left := gx - gr - 4.0
	if tier == "BREACHED":
		var r := Rect2(left, right.y - 2.0, right.x - left + 4.0, h + 4.0)
		cv.draw_rect(r, BLACK)
		cv.draw_rect(r, RED, false, 2.0)
	_tier_glyph(Vector2(gx, right.y + h * 0.5), tier, gr, col)
	_tr(right, tier, size, col)
	return left


## Two tier stamps "a / b" right-aligned at right. Returns the left x of the pair.
func _tier_pair(right: Vector2, ta: String, tb: String, size: int = TXT) -> float:
	if ta == tb:
		return _tier_tag(right, ta, size)
	var lb := _tier_tag(right, tb, size)
	_tc(Vector2(lb - 5.0, right.y + font.get_height(size) * 0.5), "/", size, DIM)
	return _tier_tag(Vector2(lb - 12.0, right.y), ta, size)


## L15 item 1: the worst and best tier as glyphs only (one tag with its word when they agree). Returns the left x.
func _tier_glyphs(right: Vector2, ta: String, tb: String) -> float:
	if ta == tb:
		return _tier_tag(right, ta)
	var cy := right.y + 9.0
	_tier_glyph(Vector2(right.x - 8.0, cy), tb, 7.5, _tier_col(tb))
	_tc(Vector2(right.x - 23.0, cy), "/", TXT, DIM)
	_tier_glyph(Vector2(right.x - 38.0, cy), ta, 7.5, _tier_col(ta))
	return right.x - 48.0


func _tier_big(p: Vector2, tier: String, size: int = 34) -> float:
	var col := _tier_col(tier)
	var h := font.get_height(size)
	var gr := float(size) * 0.44
	if tier == "BREACHED":
		var r := Rect2(p.x - 6.0, p.y - 4.0, gr * 2.0 + 26.0 + _tw(tier, size), h + 8.0)
		cv.draw_rect(r, BLACK)
		cv.draw_rect(r, RED, false, 3.0)
	_tier_glyph(p + Vector2(gr + 2.0, h * 0.5), tier, gr, col)
	_t(p + Vector2(gr * 2.0 + 12.0, 0.0), tier, size, col)
	return h + 12.0


## A small drawn arrow (the font may not carry an arrow character) starting at x, centered on cy.
func _arrow(x: float, cy: float, col: Color) -> void:
	cv.draw_line(Vector2(x, cy), Vector2(x + 9.0, cy), col, 2.0)
	cv.draw_colored_polygon(PackedVector2Array([Vector2(x + 8.0, cy - 4.0), Vector2(x + 13.0, cy), Vector2(x + 8.0, cy + 4.0)]), col)


## L17 item 1: the guard line "HOLD -> <glyph> TIER . best: <row glyph> <ROW> -> <glyph> TIER", or "HOLD -> <tier> .
## no response changes this", wrapped at word boundaries inside right. Returns the height used.
func _guard_line(p: Vector2, g: Dictionary, right: float) -> float:
	var hold := String(g.get("hold", "HOLDS"))
	var toks: Array = [["t", "HOLD", INK], ["a", INK], ["g", hold], ["t", hold, _tier_col(hold)], ["t", "\u00b7", DIM]]
	var best: Dictionary = g.get("best", {})
	if best.is_empty():
		for wd: String in "no response changes this".split(" "):
			toks.append(["t", wd, DIM])
	else:
		var r: Array = best["response"]
		toks.append(["t", "best:", DIM])
		toks.append(["r", r])
		var sent: Dictionary = g.get("sent", {})
		for wd: String in _resp_label(r, sent).split(" "):
			if wd != "":
				toks.append(["t", wd, GOLD])
		var bt := String(best["worst"])
		toks.append(["a", GOLD])
		toks.append(["g", bt])
		toks.append(["t", bt, _tier_col(bt)])
	var lh := _lh(TXT) + 2.0
	var x := p.x
	var y := p.y
	for tv: Variant in toks:
		var tk: Array = tv
		var kind := String(tk[0])
		var w := 22.0
		if kind == "t":
			w = _tw(String(tk[1]), TXT)
		elif kind == "a":
			w = 14.0
		elif kind == "g":
			w = 16.0
		if x > p.x and x + w > right:
			x = p.x
			y += lh
		var cy := y + 9.0
		if kind == "t":
			_t(Vector2(x, y), String(tk[1]), TXT, tk[2] as Color)
		elif kind == "a":
			_arrow(x, cy, tk[1] as Color)
		elif kind == "g":
			_tier_glyph(Vector2(x + 8.0, cy), String(tk[1]), 7.5, _tier_col(String(tk[1])))
		else:
			_resp_glyph(Vector2(x + 11.0, cy), tk[1] as Array, 8.5, false)
		x += w + 5.0
	return y - p.y + lh


## The fast-resolve chip (every response row yields one tier on every outcome). Returns the y below it.
func _fast_chip(p: Vector2, w: float) -> float:
	var lab := "FAST: every row, one tier"
	var cw := minf(w, _tw(lab, TXT) + 44.0)
	var r := Rect2(p, Vector2(cw, 24.0))
	_box(r, GOLD, PANEL_HI, 2.0)
	var t := String(plan_guard.get("hold", fc_locked if fc_locked != "" else "HOLDS"))
	_tier_glyph(r.position + Vector2(14.0, 12.0), t, 7.5, _tier_col(t))
	_ts(r.position + Vector2(28.0, 3.0), lab, TXT, GOLD, r.end.x - 4.0)
	return p.y + 30.0


## A value delta right-aligned at right: a small up / down triangle and the signed number.
func _delta_r(right: Vector2, d: float) -> void:
	var txt := _signed(d)
	var col := ACID if d > 0.001 else (RED if d < -0.001 else DIM)
	_tr(right, txt, TXT, col)
	var c := Vector2(right.x - _tw(txt, TXT) - 8.0, right.y + 9.0)
	if d >= 0.0:
		cv.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, -5.0), c + Vector2(5.0, 4.0), c + Vector2(-5.0, 4.0)]), col)
	else:
		cv.draw_colored_polygon(PackedVector2Array([c + Vector2(0.0, 5.0), c + Vector2(5.0, -4.0), c + Vector2(-5.0, -4.0)]), col)


func _verdict_mark(right: Vector2, v: int, size: int = TXT) -> void:
	var text := "HOLDABLE" if v == 1 else ("LOST" if v == 0 else "checking")
	var col := HOLDS_COL if v == 1 else (RED if v == 0 else DIM)
	var tw := _tw(text, size)
	var h := font.get_height(size)
	var gc := Vector2(right.x - tw - 9.0, right.y + h * 0.5)
	if v == 1:
		_tier_glyph(gc, "HOLDS", 6.0, col)
	elif v == 0:
		_tier_glyph(gc, "BREACHED", 6.0, col)
	else:
		cv.draw_arc(gc, 4.0, 0.0, TAU, 12, col, 1.5)
	_tr(right, text, size, col)


func _verdict_dot(c: Vector2, v: int) -> void:
	if v == 1:
		_tier_glyph(c, "HOLDS", 6.5, HOLDS_COL)
	elif v == 0:
		_tier_glyph(c, "BREACHED", 6.5, RED)
	else:
		cv.draw_arc(c, 4.0, 0.0, TAU, 12, DIM, 1.5)


## L16 item 2: a response's large verb glyph: HOLD (two bars), REDEPLOY (curved arrow), DEPLOY (an arrow dropping on
## a pad), SACRIFICE (a dome over a cracked base), JAM (a struck-out hound).
func _resp_glyph(c: Vector2, r: Array, rad: float, dim: bool) -> void:
	var head := "HOLD" if r.is_empty() else String(r[0])
	var col := INK
	match head:
		"REDEPLOY":
			col = ACID
			if r.size() > 1:
				var sd: Dictionary = mid.get("sentries", place.get("sentries", {}))
				col = TYPE_COLOR.get(_ctype(String(sd.get(r[1], ""))), ACID)
		"DEPLOY":
			col = TYPE_COLOR.get(String(r[1]), ACID) if r.size() > 1 else ACID
		"SACRIFICE":
			col = COBALT_HOT
		"JAM":
			col = RED
	if dim:
		col = LATER
	var lw := maxf(2.0, rad * 0.22)
	match head:
		"HOLD":
			cv.draw_rect(Rect2(c + Vector2(-rad * 0.6, -rad * 0.75), Vector2(rad * 0.4, rad * 1.5)), col)
			cv.draw_rect(Rect2(c + Vector2(rad * 0.2, -rad * 0.75), Vector2(rad * 0.4, rad * 1.5)), col)
		"REDEPLOY":
			_verb_glyph(c, "SHIFT", rad, col)
		"DEPLOY":
			cv.draw_line(c + Vector2(0.0, -rad), c + Vector2(0.0, rad * 0.15), col, lw)
			cv.draw_colored_polygon(PackedVector2Array([c + Vector2(-rad * 0.45, rad * 0.05), c + Vector2(rad * 0.45, rad * 0.05),
				c + Vector2(0.0, rad * 0.6)]), col)
			cv.draw_line(c + Vector2(-rad * 0.8, rad * 0.85), c + Vector2(rad * 0.8, rad * 0.85), col, lw)
		"SACRIFICE":
			cv.draw_arc(c + Vector2(0.0, rad * 0.45), rad * 0.9, PI, TAU, 16, col, lw)
			cv.draw_line(c + Vector2(-rad, rad * 0.5), c + Vector2(rad, rad * 0.5), col, lw)
			_crack(c + Vector2(0.0, rad * 0.1), rad * 0.4, col, maxf(1.5, lw * 0.6))
		"JAM":
			_hound_icon(c, COBALT_HOT.darkened(0.3) if not dim else LATER)
			cv.draw_line(c + Vector2(-rad, rad * 0.8), c + Vector2(rad, -rad * 0.8), col, lw)


# ---------------------------------------------------------------- input
func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		mouse = (event as InputEventMouseMotion).position
	elif event is InputEventMouseButton and event.pressed:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_LEFT:
			_click(mb.position)
	elif event is InputEventKey and event.pressed and not event.echo:
		_key((event as InputEventKey).keycode)


func _click(pos: Vector2) -> void:
	for lst: Array in [hand_hits, hits]:
		for k in range(lst.size() - 1, -1, -1):
			if (lst[k]["rect"] as Rect2).has_point(pos):
				var id := String(lst[k]["id"])
				if auto_line != "" and not (id.begins_with("speed:") or id == "instant"):
					return
				status_msg = ""
				_act(id)
				return
	if auto_line != "" or busy:
		return
	if pos.x >= _px() or pos.y < HUD_H or pos.y > LEGEND_Y:
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
			hold_armed = false
			_response_click(_pick(pos, false))
		Phase.BETWEEN:
			var c: Variant = _pick(pos, false)
			if not _none(c):
				_between_click(c)


func _key(code: int) -> void:
	if code == KEY_I:
		_toggle_instant()
		return
	if busy or phase in [Phase.PLAY, Phase.REVEAL, Phase.DECAY, Phase.FALL, Phase.DRAW]:
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
				KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6:
					_select_card(code - KEY_1)
				KEY_G:
					_set_tool("G")
				KEY_Q:
					_select_route(0)
				KEY_W:
					_select_route(1)
				KEY_E:
					_select_route(2)
				KEY_R:
					_select_b(1 - sel_b)
				KEY_H:
					_select_hunt(1 - sel_hunt)
				KEY_Z, KEY_BACKSPACE:
					_undo()
				KEY_ESCAPE:
					tool = ""
					sel_card = ""
					_highlight_tool()
				KEY_B:
					_back_to_plan()
			if enter:
				_next()
		Phase.RESPONSE:
			if code != KEY_H and not enter:
				hold_armed = false
			match code:
				KEY_H:
					_respond(["HOLD"])
				KEY_J:
					if _has_jam():
						_respond(["JAM"])
					else:
						status_msg = "No JAM card in the response hand: JAM is not available."
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
					_build_resp_groups()
					_highlight_sources()
			if enter:
				if resp_sel >= 0 and resp_sel < resp_groups.size():
					_act("rgrp:%d" % resp_sel)
				else:
					status_msg = "Pick a row (Up/Down, then Enter), or press H to hold."
		Phase.BETWEEN:
			match code:
				KEY_B:
					build_armed = true
					status_msg = "Add a guard card: 1 (drone), 2 (netrunner), 3 (enforcer), C cleans, 0 none."
				KEY_1:
					_set_build("D")
				KEY_2:
					_set_build("N")
				KEY_3:
					_set_build("E")
				KEY_C:
					_set_build(L8Rules.CLEAN)
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
	if id.begins_with("card:"):
		_card_act(int(id.substr(5)))
	elif id.begins_with("tool:"):
		_set_tool(id.substr(5))
	elif id.begins_with("route:"):
		_select_route(int(id.substr(6)))
	elif id.begins_with("bsel:"):
		_select_b(int(id.substr(5)))
	elif id.begins_with("hunt:"):
		_select_hunt(int(id.substr(5)))
	elif id.begins_with("fc:"):
		var p := id.split(":")
		if p.size() == 4:
			_select_route(int(p[1]))
			_select_b(int(p[2]))
			_select_hunt(int(p[3]))
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
	elif id.begins_with("rgrp:"):
		var gi := int(id.substr(5))
		if gi >= 0 and gi < resp_groups.size():
			var mem: Array = resp_groups[gi]["members"]
			var r: Array = (resp_opts[int(mem[0])] as Dictionary)["response"]
			if String(r[0]) != "HOLD":
				hold_armed = false
			_respond(r)
	elif id.begins_with("ropt:"):
		var oi := int(id.substr(5))
		if oi >= 0 and oi < resp_opts.size():
			hold_armed = false
			_respond((resp_opts[oi] as Dictionary)["response"])
	elif id == "rmore":
		resp_page += 1
		resp_open = -1
		hold_armed = false
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
	board.set_speed(_pspeed())


func _toggle_instant() -> void:
	instant = not instant
	board.set_instant(instant)


# ---------------------------------------------------------------- wounds
## The cells each beam turns TAKEN, walking the trace from owned0 (after the sacrifice, when there is one).
func _taken_by(tr: Array, owned0: Dictionary, sac: Variant) -> Dictionary:
	var ow: Dictionary = owned0.duplicate()
	if typeof(sac) == TYPE_VECTOR2I:
		ow[sac] = L8Rules.TAKEN
	var out := {}
	for e: Array in tr:
		if String(e[2]) != "hit" or typeof(e[1]) != TYPE_VECTOR2I:
			continue
		var c: Vector2i = e[1]
		var s := String(ow.get(c, ""))
		if s == L8Rules.OK:
			ow[c] = L8Rules.DOWN
		elif s == L8Rules.DOWN:
			ow[c] = L8Rules.TAKEN
			var b := String(e[0])
			if not out.has(b):
				out[b] = []
			(out[b] as Array).append(c)
	return out


## A wound card flies from the district into the deck strip, then lands as a red cracked pip.
func _fly_wound(c: Vector2i) -> void:
	board.set_instant(instant)
	await board.wound_fly(c, DECK_POS)
	deck_view.append(["w%d" % _wounds_in(deck_view), L8Rules.WOUND_TYPE, L8Rules.V_WOUND])


func _fly_beams(taken: Dictionary, beams: Array) -> void:
	var cells: Array = []
	for bv: Variant in beams:
		cells.append_array(taken.get(String(bv), []))
	if cells.is_empty():
		return
	busy = true
	for wc: Variant in cells:
		await _fly_wound(wc)
	busy = false


# ---------------------------------------------------------------- DECAY
func _begin_raid() -> void:
	_set_slim(false)
	fast = false
	board.set_speed(speed)
	decay_lines = PackedStringArray()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	_clear_b()
	_clear_home_glyphs()
	route_v = []
	hand_ids = []
	hand_cards = []
	fc = []
	fc_locked = ""
	plan_guard = {}
	if raid > 0:
		var dec: Dictionary = L8Rules.decay(leg, st)
		var gone: Array = []
		for c: Vector2i in L8Rules.CELLS:
			if _status_of(st, c) != L8Rules.TAKEN and _status_of(dec, c) == L8Rules.TAKEN:
				gone.append(c)
		if not gone.is_empty():
			var sent: Dictionary = st["sentries"]
			for gv: Variant in gone:
				var line := "Left DOWN: %s is TAKEN, a wound joins the deck" % _cell_name(gv)
				if sent.has(gv):
					line += " (its card leaves the board)"
				decay_lines.append(line)
			board.reset_playout()
			board.clear_paths()
			board.clear_outcome()
			board.clear_highlight()
			_show_st(st, {"sentries": st["sentries"], "ghost": null})
			phase = Phase.DECAY
			busy = true
			deck_view = (st["deck"] as Array).duplicate(true)
			deck_live = false
			board.set_instant(instant)
			await board.decay(gone)
			_show_st(dec, {"sentries": dec["sentries"], "ghost": null})
			for gv: Variant in gone:
				await _fly_wound(gv)
			st = dec
			deck_live = true
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
		y += maxf(22.0, _tf(Vector2(x + 22.0, y), ln, TXT, COBALT_HOT) + 4.0)
	y += 8.0
	y += maxf(18.0, _tf(Vector2(x, y), "A DOWN district not repaired between raids is lost.", TXT, DIM))
	_tf(Vector2(x, y), "Each lost district wounds the run deck (-%d each at leg end)." % L8Rules.WOUND_COST, TXT, RED)


# ---------------------------------------------------------------- CAPTURE
func _enter_capture() -> void:
	board.reset_playout()
	board.clear_paths()
	board.clear_outcome()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	_clear_home_glyphs()
	cap_cells = []
	cap_slots = L8Rules.capture_slots(st)
	_show_st(st, {"sentries": st["sentries"], "ghost": null})
	_capture_step()


func _capture_step() -> void:
	cap_opts = L8Rules.capture_options(leg, st)
	if cap_opts.is_empty() or cap_cells.size() >= cap_slots:
		if cap_opts.is_empty() and cap_cells.is_empty():
			status_msg = "No district can be captured: the raid goes on."
		elif cap_opts.is_empty() and cap_cells.size() < cap_slots:
			status_msg = "No second district can be captured: the raid goes on."
		st = L8Rules.end_capture(st)
		_enter_draw()
		return
	phase = Phase.CAPTURE
	_show_st(st, {"sentries": st["sentries"], "ghost": null})
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
	y += maxf(22.0, _tf(Vector2(x, y), "Next to one of your districts, or in column 0 by HOME.", TXT, DIM) + 4.0)
	if not cap_cells.is_empty():
		y += maxf(20.0, _tf(Vector2(x, y), "Claimed: " + _cells_list(cap_cells), TXT, ACID) + 2.0)
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
			_t(r.position + Vector2(276.0, 6.0), "EXPLOIT", TXT, ACID)
		hits.append({"rect": r, "id": "cap:%d" % i})
		y += 34.0
	y += 8.0
	y = _draw_kit(y, false)
	if not decay_lines.is_empty():
		y += 6.0
		for ln: String in decay_lines:
			_taken_icon(Vector2(x + 7.0, y + 8.0))
			y += maxf(20.0, _tf(Vector2(x + 22.0, y), ln, TXT, COBALT_HOT) + 2.0)
	for cv2: Variant in cap_opts:
		var c: Vector2i = cv2
		var p := _screen(c)
		_tc(p + Vector2(0.0, -50.0), str(int(vals[c])), 16, AMBER)
		if ex.has(c):
			_tc(p + Vector2(0.0, -32.0), "KEY", BAR_TXT, ACID)


## The deck and the kit. In PLAN and FORECAST: the placed slots (n/MAX_PLACED) and the hand; otherwise the deck mix.
func _draw_kit(y: float, planning: bool) -> float:
	var x := PANEL_X + PAD
	var kit: Dictionary = st["kit"]
	var deck: Array = _deck_shown()
	if planning:
		var n := _placed_total()
		var cap: int = L8Rules.MAX_PLACED
		_t(Vector2(x, y), "PLACED", TXT, DIM)
		var sd: Dictionary = place["sentries"]
		var ids: Array = []
		for c: Vector2i in L8Rules.sorted_cells(sd):
			ids.append(String(sd[c]))
		for s in range(cap):
			var sr := Rect2(x + 66.0 + s * 40.0, y - 2.0, 36.0, 20.0)
			if s < ids.size():
				_mini_card(sr.position, _hand_card(String(ids[s])))
			else:
				_box(sr, EDGE, PANEL, 1.5)
		_t(Vector2(x + 70.0 + cap * 40.0, y), "%d/%d" % [n, cap], TXT, AMBER if n >= cap else INK)
		var dead := 0
		for cd: Array in hand_cards:
			if L8Rules.is_wound(cd):
				dead += 1
		var ht := "HAND %d cards" % hand_ids.size()
		if dead > 0:
			ht += ", %d dead" % dead
		_ts(Vector2(x + 200.0, y), ht, TXT, RED if dead > 0 else INK)
	else:
		var nt := {"D": 0, "N": 0, "E": 0}
		for cd: Array in deck:
			var t := String(cd[1])
			if nt.has(t):
				nt[t] = int(nt[t]) + 1
		_t(Vector2(x, y), "DECK %d" % deck.size(), TXT, DIM)
		for i in range(3):
			var t: String = L8Rules.TYPES[i]
			var gx := x + 84.0 + i * 64.0
			_glyph(Vector2(gx, y + 9.0), t, 7.0, TYPE_COLOR[t])
			_t(Vector2(gx + 11.0, y), "x%d" % int(nt[t]), TXT, INK)
		var wn := _wounds_in(deck)
		_ts(Vector2(x + 284.0, y), "wounds %d" % wn, TXT, RED if wn > 0 else DIM)
	y += 22.0
	_t(Vector2(x, y), "KIT", TXT, DIM)
	_ghost_icon(Vector2(x + 108.0, y + 9.0), 7.0, GOLD)
	_t(Vector2(x + 120.0, y), "GHOST %d" % int(kit["ghost"]), TXT, GOLD)
	return y + 26.0


# ---------------------------------------------------------------- DRAW
## The DRAW beat: the run deck deals this raid's hand into the hand row (L14 R9, R13).
func _enter_draw() -> void:
	hand_ids = L8Rules.hand(leg, raid, st)
	hand_cards = L8Rules.hand_cards(leg, raid, st)
	sel_card = ""
	phase = Phase.DRAW
	board.clear_highlight()
	_show_st(st, {"sentries": st["sentries"], "ghost": null})
	deal_t0 = _now()
	var dur := 0.0
	if not instant and not hand_cards.is_empty():
		dur = (float(hand_cards.size() - 1) * DEAL_GAP + DEAL_T) / maxf(speed, 0.1)
	busy = true
	if dur > 0.0:
		await get_tree().create_timer(dur).timeout
	busy = false
	if shots_dir != "":
		await _shot("r%d_draw" % (raid + 1))
	_enter_plan()


func _draw_draw() -> void:
	var x := PANEL_X + PAD
	var y := _head("DRAW  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "The run deck deals this raid's hand.")
	var heat := int(st["heat"])
	y += maxf(24.0, _tf(Vector2(x, y), "Hand %d: %d base, +1 card at Heat %d, +1 at %d (Heat %d)." % [hand_ids.size(),
		L8Rules.HAND_BASE, L8Rules.EXTRA_AT, L8Rules.STRONG_AT, heat], TXT, HEAT_COL) + 6.0)
	for i in range(hand_cards.size()):
		var cd: Array = hand_cards[i]
		_mini_card(Vector2(x, y - 2.0), cd)
		if L8Rules.is_wound(cd):
			_ts(Vector2(x + 44.0, y), "%s  WOUND: a dead draw" % String(cd[0]), TXT, RED)
		else:
			var tag := "   +1 from Heat" if i >= L8Rules.HAND_BASE else ""
			_ts(Vector2(x + 44.0, y), "%s  %s %s%s" % [String(cd[0]), _tname(String(cd[1])), String(cd[2]), tag], TXT,
				GOLD if tag != "" else INK)
		y += 24.0
	y += 6.0
	y += maxf(18.0, _tf(Vector2(x, y), "Wounds in the deck: %d (they dilute every hand)." % L8Rules.wound_count(st), TXT, DIM))
	_tf(Vector2(x, y), "Every card returns to the deck after the raid.", TXT, DIM)


# ---------------------------------------------------------------- PLAN
func _enter_plan() -> void:
	_set_slim(false)
	mid = {}
	var sd := {}
	var prev: Dictionary = st["sentries"]
	for c: Vector2i in L8Rules.sorted_cells(prev):
		if sd.size() >= L8Rules.MAX_PLACED:
			break
		var id := String(prev[c])
		var cd := _hand_card(id)
		if L8Rules.is_live(st, c) and not cd.is_empty() and not L8Rules.is_wound(cd):
			sd[c] = id
	place = {"sentries": sd, "ghost": null}
	undo = []
	tool = ""
	sel_card = ""
	fc = []
	fc_locked = ""
	plan_guard = {}
	fric = 0
	launch_armed = false
	route_v = []
	sel_route = 0
	sel_b = 0
	sel_hunt = 0
	phase = Phase.PLAN
	board.clear_highlight()
	board.hide_route_verdicts()
	_plan_view()


func _plan_view() -> void:
	_show_st(st, place)
	_show_plan_paths()
	_show_hunter()
	_compute_fc()
	_refresh_outcome()


## The live HOLD forecast of the placement (L15 items 2 and 10): fc, its tier range, the all-agree tier, each route's
## worst tier at its HOME lane end on the board, and (L17 item 1) the plan guard.
func _compute_fc() -> void:
	fc = []
	fc_range = ["HOLDS", "HOLDS"]
	fc_locked = ""
	plan_guard = {}
	if (phase != Phase.PLAN and phase != Phase.FORECAST) or L8Rules.check_place(leg, raid, st, place) != "":
		_clear_home_glyphs()
		return
	fc = L8Rules.forecast(leg, raid, st, place)
	if fc.is_empty():
		_clear_home_glyphs()
		return
	var all: Array = []
	var per_route: Array = ["", "", ""]
	var cands: Array = leg["raids"][raid]["cands"]
	for fv: Variant in fc:
		var f: Dictionary = fv
		var flat := _flat(f["outcomes"])
		all.append_array(flat)
		var ri := int(cands[int(f["cand"])]["index"])
		if ri >= 0 and ri < per_route.size():
			per_route[ri] = String(_tier_range(flat)[0])
	fc_range = _tier_range(all)
	if String(fc_range[0]) == String(fc_range[1]):
		fc_locked = String(fc_range[0])
	_show_home_glyphs(per_route)
	plan_guard = _plan_guard()


## L17 item 1: every response row held over all 12 outcomes (3 A x 2 B x 2 hunter streets), then the guard.
func _plan_guard() -> Dictionary:
	var rows: Array = []
	var cands: Array = leg["raids"][raid]["cands"]
	for rv: Variant in L8Rules.response_options(leg, raid, st, 0, place):
		var r: Array = rv
		var outs: Array = []
		var total := 0.0
		var ok := true
		for k in range(cands.size()):
			for bv: Variant in L8Rules.other_cands(k):
				for h in range(L8Rules.HUNTER_CANDS):
					var res := L8Rules.resolve(leg, raid, st, k, int(bv), h, place, r)
					if res.has("error"):
						ok = false
						break
					var ns: Dictionary = res["state"]
					outs.append({"tier": L8Rules.tier(st, ns, res["touches"])})
					total += L8Rules.score(leg, ns)
				if not ok:
					break
			if not ok:
				break
		if ok and not outs.is_empty():
			rows.append({"response": r, "outs": outs, "mean": total / float(outs.size())})
	return _guard_of(rows, place["sentries"])


## L17 item 1: the guard of rows [{response, outs (with tier), mean}]: HOLD's worst tier, the best other row (highest
## worst tier, then highest mean; kept only when it beats HOLD on one of them) and uniform (one tier everywhere).
func _guard_of(rows: Array, sent: Dictionary) -> Dictionary:
	var hold_w := ""
	var hold_m := 0.0
	var best: Dictionary = {}
	var tiers := {}
	for ov: Variant in rows:
		var o: Dictionary = ov
		var outs: Array = o["outs"]
		for tv: Variant in outs:
			tiers[String((tv as Dictionary)["tier"])] = true
		var w := String(_tier_range(outs)[0])
		var m := float(o["mean"])
		var r: Array = o["response"]
		if String(r[0]) == "HOLD":
			hold_w = w
			hold_m = m
			continue
		if best.is_empty() or _rank(w) < _rank(String(best["worst"])) or (_rank(w) == _rank(String(best["worst"]))
				and m > float(best["mean"]) + MEAN_EPS):
			best = {"response": r, "worst": w, "mean": m}
	if hold_w == "":
		hold_w = "HOLDS"
	var beats := false
	if not best.is_empty():
		var br := _rank(String(best["worst"]))
		var hr := _rank(hold_w)
		beats = br < hr or (br == hr and float(best["mean"]) > hold_m + MEAN_EPS)
	return {"hold": hold_w, "best": best if beats else {}, "uniform": tiers.size() <= 1, "sent": sent.duplicate()}


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


func _select_b(i: int) -> void:
	if phase != Phase.PLAN and phase != Phase.FORECAST:
		return
	if i < 0 or i > 1:
		return
	sel_b = i
	_refresh_outcome()


func _select_hunt(h: int) -> void:
	if phase != Phase.PLAN and phase != Phase.FORECAST:
		return
	if h < 0 or h >= L8Rules.HUNTER_CANDS:
		return
	sel_hunt = h
	_refresh_outcome()


func _beam_type(r_now: Dictionary, beam: String, cand: int, cand_b: int) -> String:
	match beam:
		"beam1":
			return String(r_now["b1"]["type"])
		"extra1", "extra2":
			return String(r_now[beam]["type"])
		"sealed":
			return String(r_now["cands"][cand]["type"])
		"sealed_b":
			return String(r_now["cands"][cand_b]["type"])
	return String(r_now["hunter_type"])


## The board outcome of sealed A = k, B = the selected other route and hunter street sel_hunt, with HOLD.
func _outcome(k: int) -> Dictionary:
	var r_now: Dictionary = leg["raids"][raid]
	var kb := _cand_b()
	var tr: Array = L8Rules.trace(leg, raid, st, k, kb, sel_hunt, place, ["HOLD"])
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
			btypes.append(_beam_type(r_now, String(e[0]), k, kb))
	return {"hits": hit_cells, "blocks": blocks, "block_types": btypes, "home": home, "hunter": null}


func _refresh_outcome() -> void:
	sel_hold = {}
	if (phase != Phase.PLAN and phase != Phase.FORECAST) or L8Rules.check_place(leg, raid, st, place) != "":
		board.clear_outcome()
		return
	board.show_outcome(_outcome(sel_route))
	var res := L8Rules.resolve(leg, raid, st, sel_route, _cand_b(), sel_hunt, place, ["HOLD"])
	if not res.has("error"):
		var ns: Dictionary = res["state"]
		sel_hold = {"touches": res["touches"], "tier": L8Rules.tier(st, ns, res["touches"]), "home_hp": int(ns["home_hp"])}


## Pick (or drop) hand card i as the card to place; wounds are dead.
func _select_card(i: int) -> void:
	if phase == Phase.FORECAST:
		_back_to_plan()
	if phase != Phase.PLAN or i < 0 or i >= hand_cards.size():
		return
	var cd: Array = hand_cards[i]
	if L8Rules.is_wound(cd):
		status_msg = "A wound is a dead draw: it cannot be placed or spent."
		return
	var id := String(cd[0])
	tool = ""
	sel_card = "" if sel_card == id else id
	_highlight_tool()


## A hand-row click: PLAN / FORECAST picks the card; RESPONSE arms a DEPLOY of its type.
func _card_act(i: int) -> void:
	if i < 0 or i >= hand_cards.size():
		return
	if phase == Phase.PLAN or phase == Phase.FORECAST:
		_select_card(i)
	elif phase == Phase.RESPONSE:
		hold_armed = false
		var cd: Array = hand_cards[i]
		if L8Rules.is_wound(cd):
			status_msg = "A wound is a dead draw: it cannot be spent."
			return
		if not _none(_card_cell(String(cd[0]))):
			status_msg = "This card is on the board: click its district to move it (needs a SHIFT card)."
			return
		_arm_deploy(String(cd[1]))


func _set_tool(t: String, toggle: bool = true) -> void:
	if phase == Phase.FORECAST:
		_back_to_plan()
	if phase != Phase.PLAN:
		return
	if t == "G" and int(st["kit"]["ghost"]) <= 0:
		status_msg = "No ghost left in the kit."
		return
	sel_card = ""
	tool = "" if (toggle and tool == t) else t
	_highlight_tool()


func _highlight_tool() -> void:
	var cells := L8Rules.live_cells(st)
	if tool == "G":
		cells.append(L8Rules.HOME)
		board.highlight(cells, GOLD)
	elif sel_card != "":
		board.highlight(cells, TYPE_COLOR.get(_ctype(sel_card), ACID))
	else:
		board.clear_highlight()


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
		fric = 0
		launch_armed = false
		route_v = []
		board.hide_route_verdicts()


## A picked card goes on a live district (moving it if already placed, replacing the card there); a third new card is
## refused. With nothing picked, a click lifts the card (back to the hand) or the ghost.
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
	elif sel_card != "":
		if home or not L8Rules.is_live(st, c):
			status_msg = "Cards go on your own districts (not TAKEN)."
			return
		var cur := String(sd.get(c, ""))
		if cur == sel_card:
			_push()
			sd.erase(c)
		else:
			var at: Variant = _card_cell(sel_card)
			if _none(at) and cur == "" and sd.size() >= L8Rules.MAX_PLACED:
				status_msg = "At most %d cards go on the board: lift one first." % L8Rules.MAX_PLACED
				return
			_push()
			if not _none(at):
				sd.erase(at)
			sd[c] = sel_card
			var i := hand_ids.find(sel_card)
			if i >= 0 and not instant:
				fly_cards.append({"card": _hand_card(sel_card), "from": _card_rect(i).get_center(), "to": _screen(c),
					"t0": _now()})
		sel_card = ""
		_highlight_tool()
	else:
		if not home and sd.has(c):
			_push()
			sd.erase(c)
		elif L8Rules._same(place["ghost"], c):
			_push()
			place["ghost"] = null
		else:
			status_msg = "Pick a hand card (1-6 or click it) or the ghost (G) first."
			return
	_plan_view()


func _draw_plan() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var right := PANEL_X + PANEL_W - PAD
	var y := _head("PLAN  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Pick a hand card (1-6 or click it), then a district.")
	y = _draw_kit(y, true)
	var gr := Rect2(x, y, 128.0, 38.0)
	var gon := int(st["kit"]["ghost"]) > 0
	var ghot := gon and gr.has_point(mouse)
	_box(gr, AMBER if tool == "G" else (INK if ghot else EDGE), PANEL_HI if (tool == "G" or ghot) else PANEL)
	_ghost_icon(gr.position + Vector2(16.0, 19.0), 8.0, GOLD if gon else DIM)
	_t(gr.position + Vector2(30.0, 1.0), "GHOST [G]", TXT, INK if gon else DIM)
	_t(gr.position + Vector2(30.0, 19.0), "+%d Heat" % L8Rules.GHOST_HEAT, TXT, DIM)
	if gon:
		hits.append({"rect": gr, "id": "tool:G"})
	var sr := Rect2(x + 136.0, y, w - 136.0, 38.0)
	_box(sr, AMBER if sel_card != "" else EDGE, PANEL, 1.5)
	if sel_card != "":
		_mini_card(sr.position + Vector2(8.0, 9.0), _hand_card(sel_card))
		_ts(sr.position + Vector2(50.0, 10.0), "%s %s: click a district" % [_tname(_ctype(sel_card)), _cverb(sel_card)],
			TXT, INK, sr.end.x - 6.0)
	else:
		_ts(sr.position + Vector2(10.0, 10.0), "no card picked", TXT, DIM, sr.end.x - 6.0)
	y += 46.0
	y += maxf(18.0, _tf(Vector2(x, y), "A card's sentry blocks its own type. At most %d placed." % L8Rules.MAX_PLACED, TXT, DIM))
	y += maxf(18.0, _tf(Vector2(x, y), "Unplaced SHIFT and JAM cards are held to pay a response.", TXT, ACID))
	y += maxf(24.0, _tf(Vector2(x, y), "The ghost lets every beam pass its district or HOME.", TXT, DIM) + 6.0)
	y = _draw_beam_info(y)
	if not sel_hold.is_empty():
		y += 2.0
		y += maxf(19.0, _tf(Vector2(x, y), "ON THE BOARD: A %s, B %s, hunter %s, HOLD" % [L8Rules.ROUTE_NAMES[sel_route],
			L8Rules.ROUTE_NAMES[_cand_b()], HUNT_KEY[sel_hunt]], TXT, DIM) + 1.0)
		var left := _tier_tag(Vector2(right, y), String(sel_hold["tier"]))
		_ts(Vector2(x, y), "%s   HOME %d/%d" % [_sum(sel_hold["touches"]), int(sel_hold["home_hp"]), L8Rules.HOME_HP],
			TXT, INK, left - 8.0)
		y += 22.0
	var by := LEGEND_Y - 58.0
	if not fc.is_empty():
		if not plan_guard.is_empty():
			y += _guard_line(Vector2(x, y), plan_guard, right) + 2.0
		if fc_locked == "" and y + 22.0 < by - 24.0:
			var lft := _tier_pair(Vector2(right, y), String(fc_range[0]), String(fc_range[1]))
			_ts(Vector2(x, y), "12 outcomes with HOLD, worst / best:", TXT, DIM, lft - 8.0)
			y += 22.0
	var err := L8Rules.check_place(leg, raid, st, place)
	if err != "":
		_tf(Vector2(x, y + 2.0), "Placement: " + err, TXT, RED)
	_btn(Rect2(x, by, 110.0, 42.0), "UNDO [Z]", "undo", not undo.is_empty())
	_btn(Rect2(x + 122.0, by, w - 122.0, 42.0), "FORECAST [Enter]", "next", err == "", false, 16)


## This raid's beams: beam 1, the extras the launch Heat brings, sealed A (Q W E), sealed B (R), the hunter streets (H).
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
	_t(Vector2(x, y), "SEALED A", TXT, INK)
	var cands: Array = r_now["cands"]
	for k in range(cands.size()):
		var t := String(cands[k]["type"])
		var gx := x + 84.0 + k * 104.0
		var sr := Rect2(gx - 12.0, y - 3.0, 100.0, 22.0)
		if k == sel_route:
			_box(sr, AMBER, PANEL_HI, 1.5)
		elif sr.has_point(mouse):
			_box(sr, INK, PANEL, 1.0)
		_glyph(Vector2(gx, y + 8.0), t, 7.0, TYPE_COLOR[t])
		_ts(Vector2(gx + 10.0, y), "%s [%s]" % [L8Rules.ROUTE_NAMES[k], ROUTE_KEY[k]], TXT, INK, gx + 86.0)
		hits.append({"rect": sr, "id": "route:%d" % k})
	y += 23.0
	_t(Vector2(x, y), "SEALED B", TXT, INK)
	var bs := L8Rules.other_cands(sel_route)
	for i in range(bs.size()):
		var b := int(bs[i])
		var t := String(cands[b]["type"])
		var gx := x + 84.0 + i * 104.0
		var sr := Rect2(gx - 12.0, y - 3.0, 100.0, 22.0)
		if i == sel_b:
			_box(sr, AMBER, PANEL_HI, 1.5)
		elif sr.has_point(mouse):
			_box(sr, INK, PANEL, 1.0)
		_glyph(Vector2(gx, y + 8.0), t, 7.0, TYPE_COLOR[t])
		_ts(Vector2(gx + 10.0, y), String(L8Rules.ROUTE_NAMES[b]), TXT, INK, gx + 86.0)
		hits.append({"rect": sr, "id": "bsel:%d" % i})
	_tr(Vector2(PANEL_X + PANEL_W - PAD, y), "[R]", TXT, DIM)
	y += 21.0
	y += maxf(22.0, _tf(Vector2(x + 84.0, y), "two convoys come: A, then B from the other two", TXT, DIM) + 4.0)
	var ht := String(r_now["hunter_type"])
	var hc: Array = r_now["hunter_cands"]
	_hound_icon(Vector2(x + 6.0, y + 8.0))
	_t(Vector2(x + 18.0, y), "HUNT", TXT, COBALT_HOT)
	for h in range(hc.size()):
		var gx := x + 84.0 + h * 104.0
		var sr := Rect2(gx - 12.0, y - 3.0, 100.0, 22.0)
		if h == sel_hunt:
			_box(sr, AMBER, PANEL_HI, 1.5)
		elif sr.has_point(mouse):
			_box(sr, INK, PANEL, 1.0)
		_ts(Vector2(gx - 4.0, y), "%s: street %d" % [HUNT_KEY[h], int(hc[h])], TXT, INK, gx + 86.0)
		hits.append({"rect": sr, "id": "hunt:%d" % h})
	y += 21.0
	_glyph(Vector2(x + 90.0, y + 9.0), ht, 6.0, TYPE_COLOR[ht])
	y += maxf(22.0, _tf(Vector2(x + 100.0, y), "%s hound runs one of them  [H]" % _tname(ht), TXT, DIM) + 4.0)
	return y


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
	var used := _ts(Vector2(x + 104.0, y), "%s, %s" % [_tname(t), _line_name(ln)], TXT, col, lim)
	return y + maxf(20.0, used + 1.0)


# ---------------------------------------------------------------- FORECAST
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


## The board's route verdicts: each sealed A's worst HOLD tier over its 4 (B, hunt) outcomes.
func _route_verdicts() -> Array:
	var out: Array = []
	var cands: Array = leg["raids"][raid]["cands"]
	for fv: Variant in fc:
		var f: Dictionary = fv
		var k := int(f["cand"])
		var flat := _flat(f["outcomes"])
		var tiers: Array = []
		for ov: Variant in flat:
			tiers.append(String((ov as Dictionary)["tier"]))
		out.append({"route": int(cands[k]["index"]), "tier": String(_tier_range(flat)[0]), "tiers": tiers})
	return out


## L15 item 4: 2 HOME breaks on every one of the 12 HOLD outcomes, 1 HOME drops on every one of them, 3 HOME is at 1,
## 0 none. Read from forecast().
func _friction() -> int:
	var hp := int(st["home_hp"])
	var all_loss := not fc.is_empty()
	var all_breach := all_loss
	for fv: Variant in fc:
		for ov: Variant in _flat((fv as Dictionary)["outcomes"]):
			var h := int(((ov as Dictionary)["state"] as Dictionary)["home_hp"])
			if h >= hp:
				all_loss = false
			if h > 0:
				all_breach = false
	if all_breach:
		return 2
	if all_loss:
		return 1
	if hp == 1:
		return 3
	return 0


func _enter_forecast() -> void:
	if phase != Phase.PLAN:
		return
	var err := L8Rules.check_place(leg, raid, st, place)
	if err != "":
		status_msg = "Placement: " + err
		return
	if fc.is_empty():
		_compute_fc()
	if fc.is_empty():
		status_msg = "The forecast failed for this placement."
		return
	fric = _friction()
	launch_armed = false
	tool = ""
	sel_card = ""
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


## One forecast cell as glyphs: tier icon, HOME as a tier icon, hit and block counts.
func _fc_cell(cr: Rect2, o: Dictionary, on: bool) -> void:
	var cy := cr.position.y + 9.0
	var tier := String(o["tier"])
	_tier_glyph(Vector2(cr.position.x + 11.0, cy), tier, 7.0, _tier_col(tier))
	_home_glyph(Vector2(cr.position.x + 30.0, cy), int((o["state"] as Dictionary)["home_hp"]), int(st["home_hp"]), 6.5)
	var hitn := 0
	var blkn := 0
	for e: Array in o["touches"]:
		var k := String(e[1])
		if k == "hit":
			hitn += 1
		elif k == "block":
			blkn += 1
	var x := cr.position.x + 46.0
	var tc := INK if on else DIM
	if hitn > 0:
		_crack(Vector2(x + 3.0, cy), 6.0, RED, 1.5)
		_t(Vector2(x + 9.0, cy - 9.0), str(hitn), TXT, tc)
		x += 28.0
	if blkn > 0:
		_verb_glyph(Vector2(x + 4.0, cy), "GUARD", 5.5, COBALT_HOT)
		_t(Vector2(x + 11.0, cy - 9.0), str(blkn), TXT, tc)
		x += 28.0
	if hitn == 0 and blkn == 0:
		_t(Vector2(x, cy - 9.0), "-", TXT, DIM)


func _draw_forecast() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var right := PANEL_X + PANEL_W - PAD
	var y := _head("FORECAST  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "HOLD per sealed A: hover a cell to draw it on the city.")
	y = _draw_kit(y, true)
	var r_now: Dictionary = leg["raids"][raid]
	var cands: Array = r_now["cands"]
	var cx0 := x + 96.0
	var cw := (w - 96.0) / 2.0
	for h in range(L8Rules.HUNTER_CANDS):
		_ts(Vector2(cx0 + h * cw + 4.0, y), "hunter %s: st %d" % [HUNT_KEY[h], _hunt_street(h)], TXT, COBALT_HOT,
			cx0 + (h + 1) * cw - 4.0)
	y += 19.0
	for i in range(fc.size()):
		var f: Dictionary = fc[i]
		var k := int(f["cand"])
		var t := String(cands[k]["type"])
		var outs: Array = f["outcomes"]
		var r := Rect2(x, y, w, 62.0)
		var sel := k == sel_route
		_box(r, AMBER if sel else (INK if r.has_point(mouse) else EDGE), PANEL_HI if sel else PANEL)
		hits.append({"rect": r, "id": "route:%d" % k})
		_glyph(r.position + Vector2(14.0, 11.0), t, 8.0, TYPE_COLOR[t])
		var tag := "[%s]%s" % [ROUTE_KEY[k], "  on the board" if sel else ""]
		_tr(Vector2(r.end.x - 10.0, r.position.y + 2.0), tag, TXT, AMBER if sel else DIM)
		_ts(r.position + Vector2(28.0, 2.0), "A: %s ROUTE  %s" % [L8Rules.ROUTE_NAMES[k], _tname(t)], TXT, INK,
			r.end.x - 18.0 - _tw(tag, TXT))
		var yy := r.position.y + 22.0
		var bs := L8Rules.other_cands(k)
		for bi in range(bs.size()):
			var b := int(bs[bi])
			var bt := String(cands[b]["type"])
			_glyph(Vector2(x + 14.0, yy + 9.0), bt, 5.5, TYPE_COLOR[bt])
			_ts(Vector2(x + 24.0, yy), "B %s" % L8Rules.ROUTE_NAMES[b], TXT, DIM, cx0 - 2.0)
			var row: Array = outs[bi]
			for h in range(row.size()):
				var o: Dictionary = row[h]
				var cr := Rect2(cx0 + h * cw, yy - 1.0, cw - 4.0, 19.0)
				var on := sel and bi == sel_b and h == sel_hunt
				var chot := cr.has_point(mouse) and auto_line == "" and not busy
				if on:
					_box(cr, ACID, PANEL_HI, 1.0)
				elif chot:
					_box(cr, INK, PANEL, 1.0)
				if chot:
					fc_hover = [k, bi, h]
				_fc_cell(cr, o, on)
				hits.append({"rect": cr, "id": "fc:%d:%d:%d" % [k, bi, h]})
			yy += 19.0
		y += 66.0
	var lx := x
	var ly := y + 9.0
	_tier_glyph(Vector2(lx + 6.0, ly), "HOLDS", 6.5, _tier_col("HOLDS"))
	_t(Vector2(lx + 16.0, y), "kept", TXT, DIM)
	lx += 54.0
	_tier_glyph(Vector2(lx + 6.0, ly), "DAMAGED", 6.5, _tier_col("DAMAGED"))
	_t(Vector2(lx + 16.0, y), "-1", TXT, DIM)
	lx += 42.0
	_tier_glyph(Vector2(lx + 6.0, ly), "BREACHED", 6.5, _tier_col("BREACHED"))
	_t(Vector2(lx + 16.0, y), "lost", TXT, DIM)
	lx += 52.0
	_crack(Vector2(lx + 4.0, ly), 6.0, RED, 1.5)
	_t(Vector2(lx + 12.0, y), "cells hit", TXT, DIM)
	lx += 80.0
	_verb_glyph(Vector2(lx + 5.0, ly), "GUARD", 5.5, COBALT_HOT)
	_t(Vector2(lx + 14.0, y), "blocks", TXT, DIM)
	y += 22.0
	var ht := String(r_now["hunter_type"])
	var hr := Rect2(x, y, w, 26.0)
	_box(hr, INK if hr.has_point(mouse) else EDGE, PANEL, 1.5)
	hits.append({"rect": hr, "id": "hunt:%d" % (1 - sel_hunt)})
	_hound_icon(hr.position + Vector2(12.0, 13.0))
	_glyph(hr.position + Vector2(30.0, 13.0), ht, 6.0, TYPE_COLOR[ht])
	_ts(hr.position + Vector2(42.0, 4.0), "HUNTER %s: A street %d or B street %d   [H] %s shown" % [_tname(ht),
		_hunt_street(0), _hunt_street(1), HUNT_KEY[sel_hunt]], TXT, COBALT_HOT, hr.end.x - 8.0)
	y += 32.0
	if not plan_guard.is_empty():
		y += _guard_line(Vector2(x, y), plan_guard, right) + 2.0
	if fc_locked == "":
		var lft := _tier_pair(Vector2(right, y), String(fc_range[0]), String(fc_range[1]))
		_ts(Vector2(x, y), "12 outcomes with HOLD, worst / best:", TXT, DIM, lft - 8.0)
		y += 24.0
	if fric > 0:
		var lines := _wrap(_friction_text(), TXT, w - 36.0)
		var wr := Rect2(x, y, w, 8.0 + float(lines.size()) * _lh(TXT))
		cv.draw_rect(wr, BLACK)
		cv.draw_rect(wr, RED, false, 2.0)
		_skull(wr.position + Vector2(13.0, 13.0), 8.0, RED, BLACK)
		_tf(wr.position + Vector2(28.0, 4.0), _friction_text(), TXT, WHITE, wr.end.x - 6.0)
		y += wr.size.y + 6.0
		if launch_armed:
			_tf(Vector2(x, y), "Enter again launches anyway; B or an edit goes back.", TXT, DIM)
		else:
			_tf(Vector2(x, y), "Launching needs a second Enter.", TXT, DIM)
	var by := LEGEND_Y - 58.0
	_btn(Rect2(x, by, 110.0, 42.0), "BACK [B]", "back")
	_btn(Rect2(x + 122.0, by, w - 122.0, 42.0), "LAUNCH ANYWAY [Enter]" if launch_armed else "LAUNCH [Enter]", "next",
		true, launch_armed, 16)


# ---------------------------------------------------------------- ghost outcome overlay (L17 item 2)
## The ghost overlay of one outcome: sealed A = a, B = b, hunter street h, response resp, from state s0 (the
## post-capture state). Returns {beams, fallen, home_lost, tier}, or {} on an illegal input.
## - beams: every beam that fires, as a line {beam, kind, index, cells (up to the block), type, home (reaches HOME),
##   home_hit, shielded, hits: [cells], block: cell or null};
## - fallen: {cell: "DOWN" | "TAKEN"} for the districts newly DOWN or TAKEN;
## - home_lost: the HOME pips lost; tier: the outcome's tier.
func _ghost_data(s0: Dictionary, a: int, b: int, h: int, resp: Array) -> Dictionary:
	var res := L8Rules.resolve(leg, raid, s0, a, b, h, place, resp)
	if res.has("error"):
		return {}
	var tr: Array = res["trace"]
	var ns: Dictionary = res["state"]
	var r_now: Dictionary = leg["raids"][raid]
	var cands: Array = r_now["cands"]
	var n := L8Rules.extra_count(L8Rules.launch_heat(s0, place))
	var plan: Array = [["beam1", r_now["b1"]]]
	if n >= 1:
		plan.append(["extra1", r_now["extra1"]])
	if n >= 2:
		plan.append(["extra2", r_now["extra2"]])
	plan.append(["sealed", cands[a]])
	plan.append(["sealed_b", cands[b]])
	var hl: Variant = L8Rules.hunter_line(leg, raid, s0, a, b, h, place, resp)
	if typeof(hl) == TYPE_DICTIONARY:
		plan.append(["hunter", hl])
	var beams: Array = []
	for pv: Variant in plan:
		var bn := String(pv[0])
		var ln: Dictionary = pv[1]
		var cs: Array = []
		var hit_cells: Array = []
		var stop: Variant = null
		for cv2: Variant in ln["cells"]:
			var c: Vector2i = cv2
			cs.append(c)
			var kind := _trace_kind(tr, bn, c)
			if kind == "hit":
				hit_cells.append(c)
			elif kind == "block":
				stop = c
				break
		var hk := "" if not _none(stop) else _trace_kind(tr, bn, L8Rules.HOME)
		beams.append({"beam": bn, "kind": String(ln["kind"]), "index": int(ln["index"]), "cells": cs,
			"type": String(ln["type"]), "home": bool(ln["home"]) and _none(stop), "home_hit": hk == "home",
			"shielded": hk == "shielded", "hits": hit_cells, "block": stop})
	var fallen := {}
	for c: Vector2i in L8Rules.CELLS:
		var sb := _status_of(s0, c)
		var sa := _status_of(ns, c)
		if sa == L8Rules.DOWN and sb == L8Rules.OK:
			fallen[c] = L8Rules.DOWN
		elif sa == L8Rules.TAKEN and sb != L8Rules.TAKEN:
			fallen[c] = L8Rules.TAKEN
	return {"beams": beams, "fallen": fallen, "home_lost": maxi(0, int(s0["home_hp"]) - int(ns["home_hp"])),
		"tier": L8Rules.tier(s0, ns, res["touches"])}


## Keep the board's ghost overlay on the hovered forecast cell or response row (its worst outcome); under --auto, on
## the selected forecast cell and on the chosen row. Cleared when nothing is hovered.
func _sync_ghost() -> void:
	var key := ""
	var args: Array = []
	if phase == Phase.FORECAST and not busy:
		var sel: Array = fc_hover
		if sel.is_empty() and auto_line != "":
			sel = [sel_route, sel_b, sel_hunt]
		if not sel.is_empty():
			var k := int(sel[0])
			var b := int(L8Rules.other_cands(k)[int(sel[1])])
			var h := int(sel[2])
			key = "f|%d|%d|%d|%d|%d" % [raid, k, b, h, str(L8Rules.place_to_json(place)).hash()]
			args = [st, k, b, h, ["HOLD"]]
	elif phase == Phase.RESPONSE and not busy:
		var j := resp_hover_opt
		if j < 0 and auto_line != "":
			j = auto_opt
		if j >= 0 and j < resp_opts.size():
			var o: Dictionary = resp_opts[j]
			var wo := _worst_out(o["outs"])
			if not wo.is_empty():
				key = "r|%d|%d|%d|%d|%s" % [raid, j, int(wo["b"]), int(wo["h"]), str(o["response"])]
				args = [before, real, int(wo["b"]), int(wo["h"]), o["response"]]
	if key == ghost_key:
		return
	if key == "":
		_clear_ghost()
		return
	ghost_key = key
	var g := _ghost_data(args[0], int(args[1]), int(args[2]), int(args[3]), args[4])
	if g.is_empty():
		if board.has_method("clear_outcome_ghost"):
			board.call("clear_outcome_ghost")
		return
	if board.has_method("show_outcome_ghost"):
		board.call("show_outcome_ghost", g["beams"], g["fallen"], int(g["home_lost"]), String(g["tier"]))


# ---------------------------------------------------------------- LAUNCH and playout
func _cue(kind: String, c: Vector2i, t: String, line: int, beam: String = "") -> Dictionary:
	var d := {"kind": kind, "cell": c, "type": t, "line": line}
	if beam != "":
		d["beam"] = beam
	return d


func _trace_kind(tr: Array, beam: String, c: Variant) -> String:
	for e: Array in tr:
		if String(e[0]) == beam and typeof(e[1]) == typeof(c) and e[1] == c:
			return String(e[2])
	return ""


func _line_cues(beam: String, ln: Dictionary, tr: Array) -> Array:
	var out: Array = []
	var t := String(ln["type"])
	var id: int = int(LINE_ID[beam])
	var stopped := false
	for cv2: Variant in ln["cells"]:
		var c: Vector2i = cv2
		var k := _trace_kind(tr, beam, c)
		if k == "block":
			out.append(_cue("block", c, t, id, beam))
			stopped = true
			break
		out.append(_cue("hit" if k == "hit" else "beam_step", c, t, id, beam))
	if not stopped and bool(ln["home"]):
		var hk := _trace_kind(tr, beam, L8Rules.HOME)
		if hk == "home":
			out.append(_cue("home", Vector2i(-1, int(ln["index"])), t, id, beam))
		elif hk == "shielded":
			out.append(_cue("block", Vector2i(-1, int(ln["index"])), t, id, beam))
	return out


func _hunter_cues(tr: Array, resp: Array) -> Array:
	var cues: Array = []
	var ht := String(rd["hunter_type"])
	var hid: int = int(LINE_ID["hunter"])
	var head := Vector2i(_hunt_street(hunt), 0)
	if String(resp[0]) == "JAM":
		cues.append(_cue("jam", head, ht, hid, "hunter"))
	else:
		var hl: Variant = L8Rules.hunter_line(leg, raid, before, real, real_b, hunt, place, resp)
		if typeof(hl) == TYPE_DICTIONARY:
			cues.append(_cue("hunter_turn", head, ht, hid, "hunter"))
			cues.append_array(_line_cues("hunter", hl, tr))
	if tr.is_empty() and String(resp[0]) != "SACRIFICE":
		cues.append(_cue("evaded", Vector2i(1, 1), "D", -1))
	return cues


func _play_batch(cues: Array, label: String) -> void:
	busy = true
	board.set_instant(instant)
	await board.play(cues, _pspeed())
	busy = false
	_restore_launch_marks()
	if shots_dir != "" and label != "":
		await _shot(label)


## An unfast raid holds a reveal beat briefly so it lands; a fast one does not.
func _reveal_hold() -> void:
	if fast or instant:
		return
	busy = true
	await get_tree().create_timer(REVEAL_HOLD / maxf(speed, 0.1)).timeout
	busy = false


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


func _launch() -> void:
	if busy or phase != Phase.FORECAST:
		return
	var err := L8Rules.check_place(leg, raid, st, place)
	if err != "":
		status_msg = "Placement: " + err
		return
	if fric > 0 and not launch_armed:
		launch_armed = true
		status_msg = "%s Worst %s, best %s of 12." % [_friction_text(), String(fc_range[0]), String(fc_range[1])]
		return
	launch_armed = false
	_clear_ghost()
	if plan_guard.is_empty():
		plan_guard = _plan_guard()
	before = L8Rules.copy_state(st)
	rd = leg["raids"][raid]
	real = int(rd["real"])
	real_b = int(rd["real_b"])
	hunt = int(rd["hunter_real"])
	hunter_revealed = false
	used_card = ""
	cur_resp = ["HOLD"]
	resp_skipped = false
	hold_armed = false
	fast = bool(plan_guard.get("uniform", false))
	board.set_speed(_pspeed())
	_set_slim(true)
	heat_launch = L8Rules.launch_heat(st, place)
	hud_hp = int(st["home_hp"])
	var hold_tr := L8Rules.trace(leg, raid, st, real, real_b, hunt, place, ["HOLD"])
	known_tr = []
	for e: Array in hold_tr:
		if String(e[0]) in ["beam1", "extra1", "extra2"]:
			known_tr.append(e)
	deck_view = (before["deck"] as Array).duplicate(true)
	deck_live = false
	board.clear_highlight()
	board.clear_outcome()
	board.clear_paths()
	_clear_home_glyphs()
	board.show_candidates(_cand_view(), -1)
	_show_st(st, place)
	_restore_launch_marks()
	phase = Phase.PLAY
	stage = "known"
	var rn := raid + 1
	var kb: Array = ["beam1"]
	var n := L8Rules.extra_count(heat_launch)
	if n >= 1:
		kb.append("extra1")
	if n >= 2:
		kb.append("extra2")
	var taken := _taken_by(known_tr, before["owned"], null)
	for i in range(kb.size()):
		var b: String = kb[i]
		if i > 0:
			_beam_done(String(kb[i - 1]))
		var ln: Dictionary = rd["b1"] if b == "beam1" else rd[b]
		await _play_batch(_line_cues(b, ln, hold_tr), "r%d_known_beams" % rn if i == kb.size() - 1 else "")
		await _fly_beams(taken, [b])
	known_last = String(kb.back())
	var la: Dictionary = L8Rules._launch(leg, raid, st, place)
	var sw: Dictionary = la["sw"]
	mid = {"heat": heat_launch, "bank": int(st["bank"]), "home_hp": int(sw["hp"]),
		"owned": (sw["owned"] as Dictionary).duplicate(), "sentries": (sw["sent"] as Dictionary).duplicate(),
		"deck": (sw["deck"] as Array).duplicate(true), "kit": before["kit"]}
	hud_hp = int(mid["home_hp"])
	phase = Phase.REVEAL
	stage = "reveal"
	var sealed: Dictionary = rd["cands"][real]
	await _play_batch([_cue("reveal", Vector2i(L8Rules.W - 1, real), String(sealed["type"]), real)], "r%d_reveal" % rn)
	await _reveal_hold()
	await _enter_response()


func _beams_now() -> Array:
	var out: Array = ["beam1"]
	var n := L8Rules.extra_count(heat_launch)
	if n >= 1:
		out.append("extra1")
	if n >= 2:
		out.append("extra2")
	out.append("sealed")
	out.append("sealed_b")
	out.append("hunter")
	return out


func _stage_rank() -> int:
	return int({"known": 0, "reveal": 1, "sealed": 2, "reveal_b": 3, "sealed_b": 4, "hreveal": 5, "hunt": 6}.get(stage, 6))


func _beam_state(b: String) -> String:
	var lo := 0
	var hi := 0
	match b:
		"sealed":
			lo = 1
			hi = 2
		"sealed_b":
			lo = 3
			hi = 4
		"hunter":
			lo = 5
			hi = 6
	var s := _stage_rank()
	if phase == Phase.RESPONSE and b == "sealed":
		return "now"
	if s < lo:
		return "later"
	if s > hi:
		return "done"
	return "now"


## A beam's playout description and type ("" when still sealed).
func _beam_desc(b: String) -> Array:
	var srank := _stage_rank()
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
		"sealed_b":
			if stage == "known":
				desc = "one of the other two routes"
			elif srank < 3 or phase == Phase.RESPONSE:
				var ob := L8Rules.other_cands(real)
				desc = "%s or %s, sealed" % [L8Rules.ROUTE_NAMES[int(ob[0])], L8Rules.ROUTE_NAMES[int(ob[1])]]
			else:
				var ln3: Dictionary = rd["cands"][real_b]
				t = String(ln3["type"])
				desc = _line_name(ln3)
		"hunter":
			t = String(rd["hunter_type"])
			if stage == "hreveal" or stage == "hunt":
				desc = "street %d (%s)%s" % [_hunt_street(hunt), HUNT_KEY[hunt],
					", jammed" if String(cur_resp[0]) == "JAM" else ""]
			else:
				desc = "street %d (A) or %d (B), sealed" % [_hunt_street(0), _hunt_street(1)]
	return [desc, t]


## The playout panel; in the slim strip (L16 item 6) each beam row wraps its description under its name.
func _draw_play() -> void:
	var x := _px() + PAD
	var w := VIEW.x - _px() - 2.0 * PAD
	var right := VIEW.x - PAD
	var y := _head("LAUNCH  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "1 2 4 set the speed, I toggles instant.", x)
	y += maxf(20.0, _tf(Vector2(x, y), "Launch Heat %d: %d known beam%s" % [heat_launch, 1 + L8Rules.extra_count(heat_launch),
		"" if L8Rules.extra_count(heat_launch) == 0 else "s"], TXT, HEAT_COL) + 2.0)
	if fast:
		y = _fast_chip(Vector2(x, y), w)
	elif slim:
		y += _tf(Vector2(x, y), "With HOLD, worst / best of 12:", TXT, DIM)
		_tier_pair(Vector2(right, y), String(fc_range[0]), String(fc_range[1]))
		y += 24.0
	else:
		var lft := _tier_pair(Vector2(right, y), String(fc_range[0]), String(fc_range[1]))
		_ts(Vector2(x, y), "With HOLD, worst / best of 12:", TXT, DIM, lft - 8.0)
		y += 22.0
	if resp_skipped:
		y += maxf(20.0, _tf(Vector2(x, y), "No response changes an outcome: HOLD.", TXT, ACID) + 2.0)
	for bv: Variant in _beams_now():
		var b: String = bv
		var s := _beam_state(b)
		var col := INK if s == "now" else (DIM if s == "done" else LATER)
		var dt := _beam_desc(b)
		var desc := String(dt[0])
		var t := String(dt[1])
		var stx := s.to_upper()
		var name := String(BEAM_NAME[b])
		if slim:
			var dl := _wrap(desc, TXT, w - 16.0)
			var rh := 24.0 + float(dl.size()) * _lh(TXT)
			var r := Rect2(x, y, w, rh)
			_box(r, AMBER if s == "now" else EDGE, PANEL_HI if s == "now" else PANEL)
			_t(r.position + Vector2(8.0, 3.0), name, TXT, col)
			var gx := r.position.x + 18.0 + _tw(name, TXT)
			if t != "":
				_glyph(Vector2(gx, r.position.y + 12.0), t, 7.0, TYPE_COLOR[t])
			else:
				_t(Vector2(gx - 4.0, r.position.y + 3.0), "?", TXT, COBALT_HOT)
			_tr(Vector2(r.end.x - 8.0, r.position.y + 3.0), stx, TXT, AMBER if s == "now" else DIM)
			for i in range(dl.size()):
				_t(r.position + Vector2(8.0, 22.0 + float(i) * _lh(TXT)), dl[i], TXT, col)
			y += rh + 4.0
		else:
			var r := Rect2(x, y, w, 28.0)
			_box(r, AMBER if s == "now" else EDGE, PANEL_HI if s == "now" else PANEL)
			_t(r.position + Vector2(10.0, 5.0), name, TXT, col)
			if t != "":
				_glyph(r.position + Vector2(100.0, 14.0), t, 7.0, TYPE_COLOR[t])
			else:
				_t(r.position + Vector2(96.0, 5.0), "?", TXT, COBALT_HOT)
			_tr(Vector2(r.end.x - 8.0, r.position.y + 5.0), stx, TXT, AMBER if s == "now" else DIM)
			_ts(r.position + Vector2(114.0, 5.0), desc, TXT, col, r.end.x - 16.0 - _tw(stx, TXT))
			y += 32.0
	y += 4.0
	var labels: Array = [1.0, 2.0, 4.0]
	if slim:
		var bw := (w - 18.0) / 4.0
		for i in range(3):
			var sp: float = labels[i]
			_btn(Rect2(x + i * (bw + 6.0), y, bw, 32.0), "%dx" % int(sp), "speed:%d" % int(sp), true, is_equal_approx(speed, sp))
		_btn(Rect2(x + 3.0 * (bw + 6.0), y, bw, 32.0), "I", "instant", true, instant)
	else:
		for i in range(3):
			var sp: float = labels[i]
			_btn(Rect2(x + i * 78.0, y, 70.0, 32.0), "%dx" % int(sp), "speed:%d" % int(sp), true, is_equal_approx(speed, sp))
		_btn(Rect2(x + 240.0, y, w - 240.0, 32.0), "INSTANT [I]", "instant", true, instant)
	y += 44.0
	if stage != "known":
		_t(Vector2(x, y), "THE KNOWN BEAMS TOUCHED", TXT, DIM)
		y += 20.0
		y = _draw_touch_lines(known_tr, y)


func _draw_touch_lines(tr: Array, y: float) -> float:
	var x := _px() + PAD
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
		y += _tf(Vector2(x, y), "%s: %s" % [String(BEAM_NAME.get(b, b)), ", ".join(parts)], TXT, INK)
	if not any:
		_t(Vector2(x, y), "Nothing touched.", TXT, DIM)
		y += 19.0
	return y


# ---------------------------------------------------------------- RESPONSE
## An outcome's core (what changes on the board and HOME, without Heat) and its full signature (with Heat).
func _out_core(o: Dictionary) -> String:
	var s: Dictionary = o["state"]
	var ow := PackedStringArray()
	for c: Vector2i in L8Rules.CELLS:
		ow.append(_status_of(s, c).substr(0, 1))
	return "%s|%d|%s|%d" % [String(o["tier"]), int(s["home_hp"]), "".join(ow), L8Rules.wound_count(s)]


## L16 item 1: every response row other than HOLD changes nothing.
func _all_nothing() -> bool:
	for ov: Variant in resp_opts:
		var o: Dictionary = ov
		if String((o["response"] as Array)[0]) != "HOLD" and not bool(o["nothing"]):
			return false
	return true


## Every legal response, resolved on both B routes and both hunter streets (still sealed), with its mean score, its
## outcome signatures and the flags: better (mean beats HOLD) and nothing (paid, every outcome as HOLD), then the
## response guard (L17 item 1). A fast launch where every row changes nothing skips the panel and holds.
func _enter_response() -> void:
	resp_opts = []
	var bs := L8Rules.other_cands(real)
	for rv: Variant in L8Rules.response_options(leg, raid, before, real, place):
		var r: Array = rv
		var outs: Array = []
		var ok := true
		for bv: Variant in bs:
			for h in range(L8Rules.HUNTER_CANDS):
				var res := L8Rules.resolve(leg, raid, before, real, int(bv), h, place, r)
				if res.has("error"):
					ok = false
					break
				var ns: Dictionary = res["state"]
				outs.append({"state": ns, "touches": res["touches"], "tier": L8Rules.tier(before, ns, res["touches"]),
					"b": int(bv), "h": h})
			if not ok:
				break
		if not ok:
			continue
		var total := 0.0
		var core := PackedStringArray()
		var full := PackedStringArray()
		for ov: Variant in outs:
			var od: Dictionary = ov
			total += L8Rules.score(leg, od["state"])
			var cs := _out_core(od)
			core.append(cs)
			full.append(cs + "|%d" % int((od["state"] as Dictionary)["heat"]))
		resp_opts.append({"response": r, "outs": outs, "card": L8Rules.response_card(leg, raid, before, place, r),
			"mean": total / maxf(1.0, float(outs.size())), "core": "#".join(core),
			"key": String(r[0]) + "#" + "#".join(full), "paid": L8Rules.response_spoofs(r), "nothing": false,
			"better": false})
	hold_mean = 0.0
	var hold_core := ""
	for ov: Variant in resp_opts:
		var o: Dictionary = ov
		if String((o["response"] as Array)[0]) == "HOLD":
			hold_mean = float(o["mean"])
			hold_core = String(o["core"])
	for ov: Variant in resp_opts:
		var o: Dictionary = ov
		var head := String((o["response"] as Array)[0])
		o["better"] = head != "HOLD" and float(o["mean"]) > hold_mean + MEAN_EPS
		o["nothing"] = bool(o["paid"]) and String(o["core"]) == hold_core
	resp_guard = _guard_of(resp_opts, mid["sentries"])
	redeploy_from = null
	deploy_type = ""
	resp_page = 0
	resp_sel = -1
	resp_open = -1
	resp_pop_rect = Rect2()
	resp_follow = false
	resp_head_y = {}
	hold_armed = false
	hold_better = -1
	auto_opt = -1
	if fast and _all_nothing():
		resp_skipped = true
		if shots_dir != "":
			await _shot("r%d_response" % (raid + 1))
		phase = Phase.RESPONSE
		_respond(["HOLD"], true)
		return
	_set_slim(false)
	_build_ghosts()
	phase = Phase.RESPONSE
	board.clear_response_preview()
	_show_hunter()
	_build_resp_groups()
	_highlight_sources()


## L15 item 3: one ghost row per impossible kind, with its reason ([head, text]).
func _build_ghosts() -> void:
	resp_ghosts = []
	var heads := {}
	for ov: Variant in resp_opts:
		heads[String(((ov as Dictionary)["response"] as Array)[0])] = true
	var rc: Array = L8Rules._response_cards(leg, raid, before, place)
	var sent: Dictionary = mid["sentries"]
	var has_shift := false
	for cd: Array in rc:
		if String(cd[2]) == L8Rules.V_SHIFT:
			has_shift = true
	if not heads.has("REDEPLOY"):
		if not has_shift:
			resp_ghosts.append(["REDEPLOY", "REDEPLOY: no SHIFT card in hand"])
		elif sent.is_empty():
			resp_ghosts.append(["REDEPLOY", "REDEPLOY: no sentry on the board"])
		else:
			resp_ghosts.append(["REDEPLOY", "REDEPLOY: no free district"])
	if not heads.has("DEPLOY"):
		if rc.is_empty():
			resp_ghosts.append(["DEPLOY", "DEPLOY: no card left in hand"])
		else:
			resp_ghosts.append(["DEPLOY", "DEPLOY: no free district"])
	if not heads.has("JAM"):
		resp_ghosts.append(["JAM", "JAM: no JAM card in hand"])


## The visible groups: options filtered by a picked sentry (REDEPLOY source) or a deploy type, merged when their
## outcomes are identical (same kind), the ones whose mean beats HOLD first (best mean first), then the rest in order.
func _build_resp_groups() -> void:
	resp_groups = []
	resp_prev = -2
	var by_key := {}
	for i in range(resp_opts.size()):
		var o: Dictionary = resp_opts[i]
		var r: Array = o["response"]
		var head := String(r[0])
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
		var k := String(o["key"])
		if head == "HOLD" or head == "JAM":
			k = "%s@%d" % [k, i]
		if by_key.has(k):
			((resp_groups[int(by_key[k])] as Dictionary)["members"] as Array).append(i)
		else:
			by_key[k] = resp_groups.size()
			resp_groups.append({"members": [i], "better": bool(o["better"]), "mean": float(o["mean"]), "first": i})
	var better: Array = []
	var rest: Array = []
	for gv: Variant in resp_groups:
		var g: Dictionary = gv
		if bool(g["better"]):
			better.append(g)
		else:
			rest.append(g)
	better.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		var ma := float(a["mean"])
		var mb := float(b["mean"])
		if absf(ma - mb) > MEAN_EPS:
			return ma > mb
		return int(a["first"]) < int(b["first"]))
	resp_groups = better + rest
	if resp_sel >= resp_groups.size():
		resp_sel = -1
	resp_open = -1
	resp_page = 0
	resp_head_y = {}


func _has_jam() -> bool:
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


func _pick_source(cell: Vector2i) -> void:
	var any := false
	for o: Dictionary in resp_opts:
		var r: Array = o["response"]
		if String(r[0]) == "REDEPLOY" and r[1] == cell:
			any = true
	if not any:
		status_msg = "No SHIFT card in the response hand: REDEPLOY is not available."
		return
	redeploy_from = cell
	deploy_type = ""
	_build_resp_groups()
	_highlight_sources()


func _arm_deploy(t: String) -> void:
	if phase != Phase.RESPONSE or busy:
		return
	hold_armed = false
	if deploy_type == t:
		deploy_type = ""
		_build_resp_groups()
		_highlight_sources()
		return
	if _deploy_targets(t).is_empty():
		status_msg = "No %s card in the response hand (or no free district)." % _tname(t)
		return
	deploy_type = t
	redeploy_from = null
	_build_resp_groups()
	_highlight_sources()


func _move_resp_sel(d: int) -> void:
	if resp_groups.is_empty():
		return
	if resp_sel < 0:
		resp_sel = 0 if d > 0 else resp_groups.size() - 1
	else:
		resp_sel = clampi(resp_sel + d, 0, resp_groups.size() - 1)
	resp_follow = true


func _response_click(c: Variant) -> void:
	if phase != Phase.RESPONSE or busy or typeof(c) != TYPE_VECTOR2I:
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
			status_msg = "Click one of your sentries to move it, a response card (or 1 2 3) to deploy, or pick a row."
		else:
			_pick_source(cell)
		return
	var from: Vector2i = redeploy_from
	if cell == from:
		redeploy_from = null
		_build_resp_groups()
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


## L17 item 1: when HOLD's worst outcome loses a HOME pip (at any HOME value), the visible group that saves the most
## HOME on its worst outcome (then the best worst tier, then the best mean); -1 when no visible row saves one.
func _hold_better() -> int:
	if mid.is_empty() or before.is_empty():
		return -1
	var hold_min := 99
	var found := false
	for ov: Variant in resp_opts:
		var o: Dictionary = ov
		if String((o["response"] as Array)[0]) == "HOLD":
			hold_min = _min_hp(o["outs"])
			found = true
	if not found or hold_min >= int(before["home_hp"]):
		return -1
	var idxs: Array = []
	if resp_head_y.is_empty():
		for i in range(resp_groups.size()):
			idxs.append(i)
	else:
		idxs = resp_head_y.keys()
	var best := -1
	var best_hp := hold_min
	var best_rank := 99
	var best_mean := 0.0
	for iv: Variant in idxs:
		var gi := int(iv)
		if gi < 0 or gi >= resp_groups.size():
			continue
		var g: Dictionary = resp_groups[gi]
		var o: Dictionary = resp_opts[int((g["members"] as Array)[0])]
		if String((o["response"] as Array)[0]) == "HOLD":
			continue
		var hp := _min_hp(o["outs"])
		if hp <= hold_min:
			continue
		var wr := _rank(String(_tier_range(o["outs"])[0]))
		var m := float(o["mean"])
		if best < 0 or hp > best_hp or (hp == best_hp and (wr < best_rank or (wr == best_rank and m > best_mean + MEAN_EPS))):
			best = gi
			best_hp = hp
			best_rank = wr
			best_mean = m
	return best


## Commit a response: sealed A, REVEAL B, sealed B, the HUNTER REVEAL, then the hunter run (or the jam). Every district
## turned TAKEN sends a wound into the deck strip; each beam is marked done as the next one starts. HOLD that loses a
## HOME pip some visible row saves needs a second commit unless force.
func _respond(r: Array, force: bool = false) -> void:
	if busy or phase != Phase.RESPONSE:
		return
	var resp := L8Rules.norm_response(r)
	if resp.is_empty():
		return
	if not force and String(resp[0]) == "HOLD" and not hold_armed:
		var bg := _hold_better()
		if bg >= 0:
			hold_armed = true
			hold_better = bg
			status_msg = "%s %s: launch anyway? H again holds." % [FRICTION_HOLD, _group_label(resp_groups[bg])]
			return
	hold_armed = false
	var res := L8Rules.resolve(leg, raid, before, real, real_b, hunt, place, resp)
	if res.has("error"):
		status_msg = "Response: " + String(res["error"])
		return
	board.clear_response_preview()
	_clear_ghost()
	resp_prev = -2
	resp_open = -1
	resp_pop_rect = Rect2()
	cur_resp = resp
	used_card = L8Rules.response_card(leg, raid, before, place, resp)
	var head := String(resp[0])
	var sac: Variant = null
	var sent: Dictionary = (mid["sentries"] as Dictionary).duplicate()
	var ms: Dictionary = mid.duplicate()
	if head == "REDEPLOY":
		var id: Variant = sent[resp[1]]
		sent.erase(resp[1])
		sent[resp[2]] = id
	elif head == "DEPLOY":
		sent[resp[2]] = used_card
	elif head == "SACRIFICE":
		var ow: Dictionary = (mid["owned"] as Dictionary).duplicate()
		ow[resp[1]] = L8Rules.TAKEN
		sent.erase(resp[1])
		ms["owned"] = ow
		sac = resp[1]
	board.show_state(ms, {"sentries": sent, "ghost": place["ghost"]}, _cards_lookup(before))
	board.clear_highlight()
	redeploy_from = null
	deploy_type = ""
	phase = Phase.PLAY
	stage = "sealed"
	_set_slim(true)
	board.set_speed(_pspeed())
	var rn := raid + 1
	if typeof(sac) == TYPE_VECTOR2I:
		busy = true
		await _fly_wound(sac)
		busy = false
	var tr: Array = res["trace"]
	var taken := _taken_by(tr, before["owned"], sac)
	_beam_done(known_last)
	await _play_batch(_line_cues("sealed", rd["cands"][real], tr), "")
	await _fly_beams(taken, ["sealed"])
	_beam_done("sealed")
	stage = "reveal_b"
	board.show_b_cands(L8Rules.other_cands(real))
	busy = true
	board.set_instant(instant)
	await board.reveal_b(real_b)
	busy = false
	_restore_launch_marks()
	await _reveal_hold()
	if shots_dir != "":
		await _shot("r%d_reveal_b" % rn)
	stage = "sealed_b"
	await _play_batch(_line_cues("sealed_b", rd["cands"][real_b], tr), "")
	await _fly_beams(taken, ["sealed_b"])
	_beam_done("sealed_b")
	stage = "hreveal"
	_show_hunter()
	busy = true
	board.set_instant(instant)
	await board.hunter_reveal(hunt)
	busy = false
	hunter_revealed = true
	await _reveal_hold()
	if shots_dir != "":
		await _shot("r%d_hunter_reveal" % rn)
	stage = "hunt"
	await _play_batch(_hunter_cues(tr, resp), "r%d_sealed_hunter" % rn)
	await _fly_beams(taken, ["hunter"])
	_beam_done("hunter")
	fast = false
	board.set_speed(speed)
	var ns: Dictionary = res["state"]
	result = {"state": ns, "touches": res["touches"], "trace": tr, "tier": L8Rules.tier(before, ns, res["touches"]),
		"response": resp}
	st = ns
	deck_live = true
	hud_hp = int(st["home_hp"])
	breached = int(st["home_hp"]) <= 0
	history.append({"raid": raid, "capture": cap_cells.duplicate(), "response": resp, "tier": result["tier"],
		"touches": res["touches"], "heat_launch": heat_launch, "heat_after": int(st["heat"]),
		"score": L8Rules.score(leg, st), "between": null, "sentries": (mid["sentries"] as Dictionary).duplicate(),
		"ghost": place["ghost"], "hunt": hunt, "cand": real, "cand_b": real_b, "wounds": L8Rules.wound_count(st)})
	route_v = []
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	_clear_b()
	_show_st(st, {"sentries": st["sentries"], "ghost": null})
	phase = Phase.AFTER


## The option shown on the board: the hovered row or variant, the auto line's chosen option, else the keyboard-selected
## group's first member.
func _preview_opt() -> int:
	if resp_hover_opt >= 0 and resp_hover_opt < resp_opts.size():
		return resp_hover_opt
	if auto_line != "" and auto_opt >= 0 and auto_opt < resp_opts.size():
		return auto_opt
	if resp_sel >= 0 and resp_sel < resp_groups.size():
		return int(((resp_groups[resp_sel] as Dictionary)["members"] as Array)[0])
	return -1


## L16 item 2: preview the hovered or selected row on the board (SACRIFICE dome and crumble, REDEPLOY ghost arrow,
## DEPLOY ghost sentry, JAM struck-out hound on the hunter lanes); HOLD clears it.
func _sync_resp_preview() -> void:
	var j := _preview_opt()
	if j == resp_prev:
		return
	resp_prev = j
	if j < 0:
		board.clear_response_preview()
		return
	var r: Array = (resp_opts[j] as Dictionary)["response"]
	match String(r[0]):
		"REDEPLOY":
			board.preview_response("REDEPLOY", r[1], r[2])
		"DEPLOY":
			board.preview_response("DEPLOY", r[2], String(r[1]))
		"SACRIFICE":
			board.preview_response("SACRIFICE", r[1], null)
		"JAM":
			board.preview_response("JAM", (rd["hunter_cands"] as Array).duplicate(), String(rd["hunter_type"]))
		_:
			board.clear_response_preview()


## A group's label: the exact response, or for merged groups their shared part with "xN variants".
func _group_label(g: Dictionary) -> String:
	var mem: Array = g["members"]
	var sd: Dictionary = mid["sentries"]
	var r0: Array = (resp_opts[int(mem[0])] as Dictionary)["response"]
	if mem.size() == 1:
		return _resp_label(r0, sd)
	var head := String(r0[0])
	var base := head
	var same := true
	match head:
		"REDEPLOY":
			for m: Variant in mem:
				if ((resp_opts[int(m)] as Dictionary)["response"] as Array)[1] != r0[1]:
					same = false
			base = "MOVE %s %s" % [_tname(_ctype(String(sd.get(r0[1], "")))), _cell_name(r0[1])] if same else "MOVE"
		"DEPLOY":
			for m: Variant in mem:
				if String(((resp_opts[int(m)] as Dictionary)["response"] as Array)[1]) != String(r0[1]):
					same = false
			base = "DEPLOY %s" % _tname(String(r0[1])) if same else "DEPLOY"
	return "%s  \u00d7%d variants" % [base, mem.size()]


## One group row: a large verb glyph, then label and card, then its HOME / Heat ranges, its cost note and its worst /
## best tier glyphs.
func _draw_group(gi: int, y: float) -> bool:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var g: Dictionary = resp_groups[gi]
	var mem: Array = g["members"]
	var o: Dictionary = resp_opts[int(mem[0])]
	var r: Array = o["response"]
	var head := String(r[0])
	var outs: Array = o["outs"]
	var nothing := bool(o["nothing"])
	var rr := Rect2(x, y, w, GROUP_H - 4.0)
	var hot := rr.has_point(mouse) and auto_line == "" and not busy
	var sel := gi == resp_sel
	var fill := PANEL_HI if (hot or sel) else (BG if nothing else PANEL)
	_box(rr, ACID if hot else (AMBER if sel else (EDGE.darkened(0.35) if nothing else EDGE)), fill)
	if bool(g["better"]):
		cv.draw_rect(rr.grow(2.0), GOLD, false, 2.5)
	_resp_glyph(rr.position + Vector2(RESP_GLYPH_W * 0.5 + 2.0, rr.size.y * 0.5), r, 12.0, nothing)
	var tx := x + RESP_GLYPH_W + 6.0
	var card := String(o["card"])
	var lim := rr.end.x - 8.0
	if card != "":
		_mini_card(Vector2(rr.end.x - 42.0, rr.position.y + 3.0), _hand_card(card))
		lim = rr.end.x - 48.0
	else:
		_tr(Vector2(rr.end.x - 8.0, rr.position.y + 2.0), "free", TXT, DIM)
		lim = rr.end.x - 16.0 - _tw("free", TXT)
	var key := ""
	if head == "HOLD":
		key = "  [H]"
	elif head == "JAM":
		key = "  [J]"
	var tcol := DIM if nothing else INK
	_ts(Vector2(tx, rr.position.y + 2.0), _group_label(g) + key, TXT, tcol, lim)
	var rg := _tier_range(outs)
	var left := _tier_glyphs(Vector2(rr.end.x - 8.0, rr.position.y + 20.0), String(rg[0]), String(rg[1]))
	var hp_lo := 99
	var hp_hi := -1
	var he_lo := 999
	var he_hi := -999
	for ov: Variant in outs:
		var s: Dictionary = (ov as Dictionary)["state"]
		hp_lo = mini(hp_lo, int(s["home_hp"]))
		hp_hi = maxi(hp_hi, int(s["home_hp"]))
		he_lo = mini(he_lo, int(s["heat"]))
		he_hi = maxi(he_hi, int(s["heat"]))
	var home_t := ("HOME %d/%d" % [hp_lo, L8Rules.HOME_HP]) if hp_lo == hp_hi else ("HOME %d-%d/%d" % [hp_lo, hp_hi,
		L8Rules.HOME_HP])
	var heat_t := ("Heat %d" % he_lo) if he_lo == he_hi else ("Heat %d-%d" % [he_lo, he_hi])
	var info := "%s  %s" % [home_t, heat_t]
	var note := ""
	var ncol := DIM
	if nothing:
		note = "changes nothing"
		ncol = LATER
	elif head == "SACRIFICE":
		note = "HOME shielded"
		ncol = COBALT_HOT
	elif bool(o["paid"]):
		note = "+%d Heat" % L8Rules.SPOOF_HEAT
	if bool(g["better"]):
		note = (note + "  " if note != "" else "") + "beats HOLD"
		ncol = GOLD if not nothing else ncol
	var ly := rr.position.y + 20.0
	var iw := _tw(info, TXT)
	if note == "" or iw + 10.0 + _tw(note, TXT) <= left - 8.0 - tx:
		_ts(Vector2(tx, ly), info, TXT, tcol, left - 8.0)
		if note != "":
			_t(Vector2(tx + 10.0 + iw, ly), note, TXT, ncol)
	elif iw <= left - 8.0 - tx:
		_t(Vector2(tx, ly), info, TXT, tcol)
		var nl := _tw(note, TXT)
		if tx + iw + 10.0 + nl > left - 8.0:
			note = "beats HOLD" if bool(g["better"]) else note
		_ts(Vector2(tx + iw + 10.0, ly), note, TXT, ncol, left - 8.0)
	else:
		_ts(Vector2(tx, ly), info, TXT, tcol, left - 8.0)
	hits.append({"rect": rr, "id": "rgrp:%d" % gi})
	if hot:
		resp_hover_opt = int(mem[0])
	return hot


func _draw_response() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var right := PANEL_X + PANEL_W - PAD
	var y := _head("RESPONSE  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Hover a row to see it on the city. H holds, J jams.")
	if fast:
		y = _fast_chip(Vector2(x, y - 2.0), w)
	var sealed: Dictionary = rd["cands"][real]
	var t := String(sealed["type"])
	_glyph(Vector2(x + 8.0, y + 10.0), t, 8.0, TYPE_COLOR[t])
	y += maxf(22.0, _ts(Vector2(x + 22.0, y), "SEALED A: %s ROUTE, %s" % [L8Rules.ROUTE_NAMES[real], _tname(t)], 14, INK) + 2.0)
	if not resp_guard.is_empty():
		y += _guard_line(Vector2(x, y), resp_guard, right) + 2.0
	var ob := L8Rules.other_cands(real)
	y += maxf(18.0, _tf(Vector2(x, y), "B is %s or %s, the hunter street is sealed: worst / best of 4." % [
		L8Rules.ROUTE_NAMES[int(ob[0])], L8Rules.ROUTE_NAMES[int(ob[1])]], TXT, COBALT_HOT))
	y += maxf(20.0, _tf(Vector2(x, y), "A card response costs +%d Heat; HOLD and SACRIFICE are free. Gold: beats HOLD." %
		L8Rules.SPOOF_HEAT, TXT, DIM) + 2.0)
	_t(Vector2(x, y), "RESPONSE HAND", TXT, DIM)
	var mx := x + 124.0
	for id: String in L8Rules.response_hand(leg, raid, before, place):
		if mx + 34.0 > right:
			break
		mx += _mini_card(Vector2(mx, y - 1.0), _hand_card(id))
	y += 26.0
	if hold_armed and hold_better >= 0 and hold_better < resp_groups.size():
		var hg: Dictionary = resp_groups[hold_better]
		var hb: Dictionary = resp_opts[int((hg["members"] as Array)[0])]
		var br := Rect2(x, y, w, 48.0)
		cv.draw_rect(br, BLACK)
		cv.draw_rect(br, RED, false, 2.0)
		_t(br.position + Vector2(8.0, 4.0), FRICTION_HOLD, TXT, WHITE)
		var gx := br.position.x + 8.0 + _tw(FRICTION_HOLD, TXT) + 16.0
		_resp_glyph(Vector2(gx, br.position.y + 13.0), hb["response"], 10.0, false)
		var wt := String(_tier_range(hb["outs"])[0])
		_tier_glyph(Vector2(gx + 24.0, br.position.y + 13.0), wt, 8.0, _tier_col(wt))
		_ts(Vector2(gx + 36.0, br.position.y + 4.0), ": launch anyway?", TXT, WHITE, br.end.x - 6.0)
		_ts(br.position + Vector2(8.0, 25.0), "H again holds; any other choice cancels.", TXT, DIM, br.end.x - 6.0)
		y += 54.0
	var filtered := false
	if not _none(redeploy_from):
		var sid := String((mid["sentries"] as Dictionary).get(redeploy_from, ""))
		y += maxf(20.0, _tf(Vector2(x, y), "Moves of the %s on %s  (Esc: all rows)" % [_tname(_ctype(sid)),
			_cell_name(redeploy_from)], TXT, ACID) + 2.0)
		filtered = true
	elif deploy_type != "":
		y += maxf(20.0, _tf(Vector2(x, y), "Deploys of a %s card  (Esc: all rows)" % _tname(deploy_type), TXT, ACID) + 2.0)
		filtered = true
	elif resp_opts.size() <= 1:
		y += maxf(20.0, _tf(Vector2(x, y), "No card response is available: HOLD.", TXT, AMBER) + 2.0)
	var ghosts: Array = [] if filtered else resp_ghosts
	var bottom := LEGEND_Y - 6.0
	var avail := bottom - y - float(ghosts.size()) * GHOST_H
	var ng := resp_groups.size()
	var per := clampi(int(avail / GROUP_H), 1, MAX_GROUPS)
	var fold := ng > per
	if fold:
		per = clampi(int((avail - GHOST_H) / GROUP_H), 1, MAX_GROUPS)
	var pages := maxi(1, L8Rules.idiv(ng + per - 1, per))
	if resp_follow and resp_sel >= 0:
		resp_page = L8Rules.idiv(resp_sel, per)
		resp_follow = false
	resp_page = posmod(resp_page, pages)
	var keep_open := resp_open >= 0 and resp_pop_rect.has_point(mouse)
	var hovered_g := -1
	resp_head_y = {}
	var g0 := resp_page * per
	for gi in range(g0, mini(ng, g0 + per)):
		resp_head_y[gi] = y
		if _draw_group(gi, y):
			hovered_g = gi
		y += GROUP_H
	if hovered_g >= 0:
		resp_open = hovered_g if ((resp_groups[hovered_g] as Dictionary)["members"] as Array).size() > 1 else -1
	elif keep_open:
		pass
	elif resp_sel >= 0 and resp_sel < ng and ((resp_groups[resp_sel] as Dictionary)["members"] as Array).size() > 1:
		resp_open = resp_sel
	else:
		resp_open = -1
	if fold:
		var fr := Rect2(x, y, w, GHOST_H - 3.0)
		var fhot := fr.has_point(mouse)
		_box(fr, INK if fhot else EDGE, PANEL_HI if fhot else PANEL, 1.5)
		var shown_to := mini(ng, g0 + per)
		_ts(fr.position + Vector2(8.0, 1.0), "MORE  rows %d-%d of %d  (click: next %s)" % [g0 + 1, shown_to, ng,
			"rows" if shown_to < ng else "fold"], TXT, AMBER, fr.end.x - 6.0)
		hits.append({"rect": fr, "id": "rmore"})
		y += GHOST_H
	for gv: Variant in ghosts:
		var ga: Array = gv
		var gr := Rect2(x, y, w, GHOST_H - 3.0)
		cv.draw_rect(gr, BG)
		cv.draw_rect(gr, EDGE.darkened(0.45), false, 1.0)
		_resp_glyph(gr.position + Vector2(RESP_GLYPH_W * 0.5 + 2.0, gr.size.y * 0.5), [String(ga[0])], 7.5, true)
		_ts(gr.position + Vector2(RESP_GLYPH_W + 6.0, 1.0), String(ga[1]), TXT, LATER, gr.end.x - 6.0)
		y += GHOST_H


## The hover list of a merged group (L15 item 1): every variant, clickable, beside the panel.
func _draw_resp_pop() -> void:
	resp_pop_rect = Rect2()
	if resp_open < 0 or resp_open >= resp_groups.size() or not resp_head_y.has(resp_open):
		return
	var mem: Array = (resp_groups[resp_open] as Dictionary)["members"]
	if mem.size() < 2:
		return
	var n := mini(mem.size(), int((LEGEND_Y - HUD_H - 34.0) / SUB_H))
	var h := 28.0 + float(n) * SUB_H
	var py := clampf(float(resp_head_y[resp_open]), HUD_H + 4.0, LEGEND_Y - 4.0 - h)
	var r := Rect2(PANEL_X - POP_W, py, POP_W + PAD + 2.0, h)
	_box(r, INK, Color(PANEL, 0.97), 1.5)
	_ts(r.position + Vector2(8.0, 4.0), "%d variants, same outcomes:" % mem.size(), TXT, DIM, PANEL_X - 6.0)
	var sd: Dictionary = mid["sentries"]
	for k in range(n):
		var oi := int(mem[k])
		var sr := Rect2(r.position.x + 4.0, py + 26.0 + k * SUB_H, POP_W - 8.0, SUB_H - 2.0)
		var hot := sr.has_point(mouse) and auto_line == "" and not busy
		if hot:
			_box(sr, ACID, PANEL_HI, 1.0)
			resp_hover_opt = oi
		_ts(sr.position + Vector2(6.0, 1.0), _resp_label((resp_opts[oi] as Dictionary)["response"], sd), TXT, INK,
			sr.end.x - 4.0)
		hits.append({"rect": sr, "id": "ropt:%d" % oi})
	resp_pop_rect = r


# ---------------------------------------------------------------- AFTERMATH
## The aftermath (in the slim strip during the playout, L16 item 6).
func _draw_after() -> void:
	var x := _px() + PAD
	var w := VIEW.x - _px() - 2.0 * PAD
	var tier := String(result.get("tier", "HOLDS"))
	var y := _head("AFTERMATH  RAID %d/%d" % [raid + 1, L8Rules.RAIDS], "Enter goes on.", x)
	y += _tier_big(Vector2(x, y), tier, 24 if slim else 34)
	y += maxf(24.0, _tf(Vector2(x, y), String(TIER_TEXT.get(tier, "")), TXT, INK) + 6.0)
	var resp: Array = result["response"]
	y += maxf(20.0, _tf(Vector2(x, y), "Response: %s" % _resp_label(resp, mid.get("sentries", place["sentries"])), TXT, ACID) + 2.0)
	y += maxf(20.0, _tf(Vector2(x, y), "Sealed A: %s   sealed B: %s" % [L8Rules.ROUTE_NAMES[real], L8Rules.ROUTE_NAMES[real_b]], TXT, INK) + 2.0)
	y += maxf(26.0, _tf(Vector2(x, y), "Hunter: street %d (%s)%s" % [_hunt_street(hunt), HUNT_KEY[hunt],
		", jammed" if String(resp[0]) == "JAM" else ""], TXT, COBALT_HOT) + 8.0)
	_t(Vector2(x, y), "WHAT THE BEAMS TOUCHED", TXT, DIM)
	y += 20.0
	y = _draw_touch_lines(result["trace"], y)
	y += 10.0
	var notes := PackedStringArray()
	if (result["trace"] as Array).is_empty() and String(resp[0]) != "SACRIFICE":
		notes.append("evaded -%d" % L8Rules.EVADE_HEAT)
	if L8Rules.response_spoofs(resp):
		notes.append("card +%d" % L8Rules.SPOOF_HEAT)
	var note := "" if notes.is_empty() else "  (%s)" % ", ".join(notes)
	y += maxf(22.0, _tf(Vector2(x, y), "Heat: launch %d -> %d%s" % [heat_launch, int(st["heat"]), note], TXT, HEAT_COL) + 4.0)
	y += maxf(22.0, _tf(Vector2(x, y), "HOME: %d -> %d" % [int(before["home_hp"]), int(st["home_hp"])], TXT,
		RED if int(st["home_hp"]) < int(before["home_hp"]) else INK) + 3.0)
	var wb := L8Rules.wound_count(before)
	var wa := L8Rules.wound_count(st)
	y += maxf(22.0, _tf(Vector2(x, y), "Wounds in the deck: %d -> %d" % [wb, wa], TXT, RED if wa > wb else DIM) + 3.0)
	var live := L8Rules.live_cells(st).size()
	_tf(Vector2(x, y), "Districts held: %d    Leg value now: %s" % [live, _score_text(st)], TXT, INK)
	var last := breached or raid >= L8Rules.RAIDS - 1
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "RECORD [Enter]" if last else "BETWEEN RAIDS [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- BETWEEN
func _enter_between() -> void:
	_set_slim(false)
	board.clear_paths()
	board.clear_outcome()
	board.clear_response_preview()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	_clear_home_glyphs()
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


func _highlight_down() -> void:
	board.clear_highlight()
	var todo: Array = []
	for dv: Variant in _down_cells():
		if not L8Rules._same(b_repair, dv):
			todo.append(dv)
	if not todo.is_empty():
		board.highlight_kind(todo, "repair")
	if not _none(b_repair):
		board.highlight_kind([b_repair], "picked", true)


func _bp(inten: String) -> Dictionary:
	return L8Rules.between_parts(leg, st, b_repair, b_build, inten)


func _opt_key(repair: Variant, build: Variant, inten: String) -> String:
	return "%d|%d|%d|%s|%s|%s" % [leg_seed, raid, b_hash, str(repair), str(build), inten]


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


func _safe(repair: Variant, build: Variant, inten: String, force: bool = false) -> int:
	var key := _opt_key(repair, build, inten)
	if safe_cache.has(key):
		return 1 if bool(safe_cache[key]) else 0
	if force or auto_line != "":
		return 1 if _compute_safe(key, repair, build, inten) else 0
	if not safe_pending.has(key):
		safe_pending[key] = [repair, build, inten]
	return -1


func _work_safe() -> void:
	var t0 := Time.get_ticks_msec()
	while not safe_pending.is_empty():
		var key: String = safe_pending.keys()[0]
		var a: Array = safe_pending[key]
		_compute_safe(key, a[0], a[1], String(a[2]))
		if Time.get_ticks_msec() - t0 >= SAFE_BUDGET_MS:
			break


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


func _repair_opts() -> Array:
	var out: Array = [null]
	for dv: Variant in _down_cells():
		if not _none(L8Rules.between_parts(leg, st, dv, b_build, b_inten)["repaired"]):
			out.append(dv)
	return out


## The build options at the current repair: none, every type the bank pays for, and CLEAN when a wound exists.
func _build_opts() -> Array:
	var out: Array = [null]
	var builds: Array = L8Rules.TYPES.duplicate()
	builds.append(L8Rules.CLEAN)
	for tv: Variant in builds:
		if not _none(L8Rules.between_parts(leg, st, b_repair, tv, b_inten)["built"]):
			out.append(tv)
	return out


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


func _req_line(y: float, text: String) -> float:
	var x := PANEL_X + PAD
	var lines := _wrap(text, TXT, PANEL_W - 2.0 * PAD - 14.0)
	var h := 4.0 + float(lines.size()) * _lh(TXT)
	var r := Rect2(x, y, PANEL_W - 2.0 * PAD, h)
	cv.draw_rect(r, RED.darkened(0.7))
	cv.draw_rect(r, RED, false, 2.0)
	_tf(r.position + Vector2(8.0, 2.0), text, TXT, WHITE, r.end.x - 6.0)
	return y + h + 4.0


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
		if String(t) == L8Rules.CLEAN:
			status_msg = "No wound to clean, or not enough bank (cost %d, after the repair)." % L8Rules.CLEAN_PRICE
		else:
			status_msg = "Not enough bank to add a card (cost %d, after the repair)." % L8Rules.SENTRY_PRICE
		return
	b_build = String(t)


func _set_inten(nm: String) -> void:
	if phase != Phase.BETWEEN or not L8Rules.INTENSITY.has(nm):
		return
	b_inten = nm
	if not _none(b_repair) and _none(L8Rules.between_parts(leg, st, b_repair, null, b_inten)["repaired"]):
		b_repair = null
		status_msg = "Not enough bank for the repair at %s: the repair is dropped." % nm
		_highlight_down()
	if not _none(b_build) and _none(L8Rules.between_parts(leg, st, b_repair, b_build, b_inten)["built"]):
		b_build = null
		status_msg = "Not enough bank for the build at %s: the build is dropped." % nm


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
			"repair_cost": int(parts["repair_cost"]), "extra_capture": int(parts["extra_capture"]),
			"new_card": parts["new_card"], "cleaned": parts["cleaned"]}
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
		_show_st(st, {"sentries": st["sentries"], "ghost": null})
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


## L15 item 8: the intensity perk as an icon: wrench (free repair), flag + (an extra capture), a dash (none).
func _draw_perk(p: Vector2, nm: String, sel: bool) -> void:
	var col := ACID if sel else INK
	match nm:
		"NORMAL":
			_wrench_icon(p + Vector2(8.0, 8.0), col)
		"HOT":
			_flag_icon(p + Vector2(4.0, 8.0), col)
			_t(p + Vector2(15.0, -1.0), "+1", TXT, col)
		_:
			cv.draw_line(p + Vector2(2.0, 8.0), p + Vector2(14.0, 8.0), DIM, 2.0)


func _dash_rect(r: Rect2, col: Color) -> void:
	var pts: Array = [r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y), r.position]
	for i in range(4):
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		var n := 4
		for k in range(n):
			cv.draw_line(a.lerp(b, float(k) / n), a.lerp(b, (float(k) + 0.55) / n), col, 1.5)


func _draw_between() -> void:
	var x := PANEL_X + PAD
	var w := PANEL_W - 2.0 * PAD
	var right := PANEL_X + PANEL_W - PAD
	var y := _head("BETWEEN RAIDS", "Repair, add a card or clean, pick an intensity. Enter: next raid.")
	var parts := _bp(b_inten)
	_safe(b_repair, b_build, b_inten)
	if int(st["home_hp"]) == 1:
		var br := Rect2(x, y - 4.0, w, 24.0)
		cv.draw_rect(br, RED.darkened(0.45))
		cv.draw_rect(br, RED, false, 2.0)
		_skull(br.position + Vector2(13.0, 12.0), 8.0, WHITE, BLACK)
		_ts(br.position + Vector2(28.0, 3.0), "Next HOME hit ends the campaign", TXT, WHITE, br.end.x - 6.0)
		y += 26.0
	y += maxf(20.0, _tf(Vector2(x, y), "1  REPAIR ONE DOWN DISTRICT  (v / 2, free on NORMAL)", TXT, DIM) + 2.0)
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
			var lim := rr.end.x - 104.0
			if _none(o):
				_ts(rr.position + Vector2(22.0, 1.0), "no repair" if picked else "no repair [click]", TXT,
					INK if picked else DIM, lim)
			else:
				var c: Vector2i = o
				var cost := L8Rules.repair_cost(leg, c, b_inten)
				var ct := "free" if cost == 0 else "-%d" % cost
				_down_icon(rr.position + Vector2(10.0, 10.0))
				if picked:
					_ts(rr.position + Vector2(22.0, 1.0), "repair %s   %s" % [_cell_name(c), ct], TXT, ACID, lim)
				else:
					_ts(rr.position + Vector2(22.0, 1.0), "%s DOWN: repair (%s)" % [_cell_name(c), ct], TXT,
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
	y += maxf(20.0, _tf(Vector2(x, y), "2  ADD A GUARD CARD OR CLEAN A WOUND   [B 1 2 3, C]", TXT, DIM) + 2.0)
	var bw := (w - 32.0) / 5.0
	var opts: Array = ["", "D", "N", "E", L8Rules.CLEAN]
	var wn := L8Rules.wound_count(st)
	for i in range(opts.size()):
		var t: String = opts[i]
		var r := Rect2(x + i * (bw + 8.0), y, bw, 40.0)
		var picked := (t == "" and _none(b_build)) or (t != "" and not _none(b_build) and String(b_build) == t)
		var ok := t == "" or not _none(L8Rules.between_parts(leg, st, b_repair, t, b_inten)["built"])
		var hot := ok and r.has_point(mouse)
		_box(r, AMBER if picked else (INK if hot else EDGE), PANEL_HI if (picked or hot) else PANEL)
		var cr := Rect2(r.position + Vector2(5.0, 5.0), Vector2(22.0, 30.0))
		if t == "":
			_dash_rect(cr, DIM)
			_t(r.position + Vector2(32.0, 11.0), "[0]", TXT, DIM)
		else:
			var price := L8Rules.CLEAN_PRICE if t == L8Rules.CLEAN else L8Rules.SENTRY_PRICE
			if t == L8Rules.CLEAN:
				_card_face(cr, ["w", L8Rules.WOUND_TYPE, L8Rules.V_WOUND], not ok)
			else:
				_card_face(cr, ["b", t, L8Rules.V_GUARD], not ok)
			_coin(r.position + Vector2(37.0, 12.0), 5.0, GOLD if ok else DIM)
			_t(r.position + Vector2(45.0, 2.0), "%d" % price, TXT, GOLD if ok else DIM)
			var key := "[C]" if t == L8Rules.CLEAN else "[%d]" % i
			if t == L8Rules.CLEAN and wn == 0:
				key = "-"
			_t(r.position + Vector2(32.0, 20.0), key, TXT, DIM)
		if ok:
			_verdict_dot(Vector2(r.end.x - 8.0, r.end.y - 9.0), _safe(b_repair, null if t == "" else t, b_inten))
			hits.append({"rect": r, "id": "build:" + ("none" if t == "" else t)})
	y += 46.0
	var bq := _req_text(_build_opts(), false)
	if bq != "":
		y = _req_line(y, bq)
	_t(Vector2(x, y), "3  RUN INTENSITY   [L N O]   net leg value", TXT, DIM)
	y += 20.0
	var kt: Array = []
	if raid + 1 < L8Rules.RAIDS:
		var rn: Dictionary = leg["raids"][raid + 1]
		kt = [String(rn["b1"]["type"]), String(rn["extra1"]["type"]), String(rn["extra2"]["type"])]
	var cw := (w - 16.0) / 3.0
	var s_now := L8Rules.score(leg, st)
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
		_ts(cr.position + Vector2(7.0, 3.0), "%s [%s]" % [nm, INTEN_KEY[i]], TXT, AMBER if sel else INK,
			cr.end.x - 14.0 - 12.0 * (i + 1))
		# L17 item 3: the net leg value as one large signed number, with captures, income and Heat icons below.
		var alive := int(ns["home_hp"]) > 0
		var dv := (L8Rules.score(leg, ns) - s_now) if alive else 0.0
		var big := _signed(dv) if alive else "--"
		var bcol := DIM
		if alive and dv > 0.001:
			bcol = ACID
		elif alive and dv < -0.001:
			bcol = RED
		_tc(Vector2(cr.get_center().x, cr.position.y + 40.0), big, _fsize(big, 30, cw - 12.0), bcol)
		var iy := cr.position.y + 66.0
		var caps := 2 if int(p["extra_capture"]) > 0 else 1
		_flag_icon(Vector2(cr.position.x + 9.0, iy), INK)
		_t(Vector2(cr.position.x + 18.0, iy - 9.0), "x%d" % caps, TXT, ACID if caps > 1 else INK)
		_coin(Vector2(cr.position.x + 49.0, iy), 5.5)
		_t(Vector2(cr.position.x + 57.0, iy - 9.0), "+%d" % int(p["income"]), TXT, GOLD)
		_flame(Vector2(cr.position.x + 89.0, iy + 1.0), 5.0)
		_t(Vector2(cr.position.x + 96.0, iy - 9.0), "+%d" % int(p["heat_add"]), TXT, HEAT_COL)
		var ry := cr.position.y + 92.0
		_beam_icons(Vector2(cr.position.x + 16.0, ry), kt, k0)
		_tr(Vector2(cr.end.x - 7.0, ry - 9.0), "H%d" % h0, TXT, RED if k0 > 1 else DIM)
		ry += 18.0
		if ghost_ok:
			_ghost_icon(Vector2(cr.position.x + 11.0, ry), 4.5, GOLD)
			_beam_icons(Vector2(cr.position.x + 28.0, ry), kt, k1)
			_tr(Vector2(cr.end.x - 7.0, ry - 9.0), "H%d" % h1, TXT, RED if k1 > 1 else DIM)
		else:
			_ghost_icon(Vector2(cr.position.x + 11.0, ry), 4.5, DIM)
			_xmark(Vector2(cr.position.x + 11.0, ry), 4.0, DIM, 1.5)
		_draw_perk(Vector2(cr.position.x + 6.0, cr.position.y + 128.0), nm, sel)
	y += CARD_H + 8.0
	var ns2: Dictionary = parts["state"]
	var dec := _decided() == 1
	if dec:
		y = minf(y, LEGEND_Y - 112.0)
		var dr := Rect2(x, y, w, 26.0)
		cv.draw_rect(dr, BLACK)
		cv.draw_rect(dr, RED, false, 2.0)
		_skull(dr.position + Vector2(14.0, 13.0), 9.0, RED, BLACK)
		_ts(dr.position + Vector2(30.0, 4.0), "DECIDED: the cell falls next raid", TXT, WHITE, dr.end.x - 6.0)
		y += 30.0
		_tf(Vector2(x, y), "No repair, build or intensity leaves a plan that holds HOME.", TXT, DIM)
	else:
		y += maxf(19.0, _tf(Vector2(x, y), "BANK %d - repair %d - card %d + income %d = %d" % [int(st["bank"]),
			int(parts["repair_cost"]), int(parts["build_cost"]), int(parts["income"]), int(ns2["bank"])], TXT, INK) + 1.0)
		var heat_t := "HEAT %d + %d = %d" % [int(st["heat"]), int(parts["heat_add"]), int(ns2["heat"])]
		_t(Vector2(x, y), heat_t, TXT, HEAT_COL)
		var vx := x + _tw(heat_t, TXT) + 16.0
		_tf(Vector2(vx, y), "Leg value after: %s" % _score_text(ns2), TXT, INK, right)
	_btn(Rect2(x, LEGEND_Y - 58.0, w, 42.0), "THE CELL FALLS [Enter]" if dec else "NEXT RAID [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- FALL
func _draw_fall() -> void:
	var x := PANEL_X + PAD
	var y := _head("DECIDED", "The cell falls next raid.")
	_tier_glyph(Vector2(x + 10.0, y + 10.0), "BREACHED", 10.0, RED)
	y += maxf(24.0, _tf(Vector2(x + 28.0, y), "No line keeps HOME above 0 in raid %d." % (decided_raid + 1), TXT, RED) + 6.0)
	_tf(Vector2(x, y), "Every repair, build and intensity leaves a sealed route that ends the campaign.", TXT, DIM)


# ---------------------------------------------------------------- RECORD
func _enter_record() -> void:
	_set_slim(false)
	phase = Phase.RECORD
	board.clear_highlight()
	board.clear_outcome()
	board.clear_response_preview()
	board.hide_route_verdicts()
	board.clear_hunter_cands()
	_clear_b()
	_clear_home_glyphs()
	_clear_ghost()
	route_v = []
	resp_prev = -2


func _draw_record() -> void:
	cv.draw_rect(Rect2(0.0, HUD_H, PANEL_X, LEGEND_Y - HUD_H), Color(BG, 0.86))
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
		_tier_glyph(Vector2(x + 9.0, y + 11.0), "BREACHED", 9.0, RED)
		_ts(Vector2(x + 26.0, y), "BREACHED in raid %d: the campaign is lost." % history.size(), 18, RED, PANEL_X - 20.0)
	elif decided:
		_tier_glyph(Vector2(x + 9.0, y + 11.0), "BREACHED", 9.0, RED)
		_ts(Vector2(x + 26.0, y), "DECIDED before raid %d: no plan could hold HOME. The cell falls." % (decided_raid + 1), 18,
			RED, PANEL_X - 20.0)
	else:
		_t(Vector2(x, y), "THE CELL SURVIVED THE LEG", 18, ACID)
	y += 40.0
	for hv: Variant in history:
		var h: Dictionary = hv
		var tier := String(h["tier"])
		var tcol := _tier_col(tier)
		var r := Rect2(x, y, 780.0, 76.0)
		if tier == "BREACHED":
			_box(r, RED, BLACK, 3.0)
		else:
			_box(r, tcol, PANEL)
		_t(r.position + Vector2(14.0, 8.0), "RAID %d" % (int(h["raid"]) + 1), 18, DIM)
		_tier_pip(r.position + Vector2(116.0, 19.0), tier, 10.0)
		_t(r.position + Vector2(136.0, 8.0), tier, 18, tcol)
		var caps: Array = h["capture"]
		var cap := "no capture" if caps.is_empty() else "captured " + _cells_list(caps)
		_ts(r.position + Vector2(280.0, 10.0), cap, TXT, INK, r.position.x + 470.0)
		_ts(r.position + Vector2(480.0, 10.0), "response " + _resp_label(h["response"], h["sentries"]), TXT, ACID, r.end.x - 10.0)
		var hn := int(h.get("hunt", 0))
		_ts(r.position + Vector2(14.0, 34.0), "%s   Heat %d -> %d   A %s, B %s, hunter %s   wounds %d" % [_sum(h["touches"]),
			int(h["heat_launch"]), int(h["heat_after"]), L8Rules.ROUTE_NAMES[int(h.get("cand", 0))],
			L8Rules.ROUTE_NAMES[int(h.get("cand_b", 1))], HUNT_KEY[clampi(hn, 0, 1)], int(h.get("wounds", 0))], TXT,
			INK, r.end.x - 10.0)
		var bt: Variant = h["between"]
		if typeof(bt) == TYPE_DICTIONARY:
			var b: Dictionary = bt
			var rep := "no repair" if _none(b["repair"]) else "repaired " + _cell_name(b["repair"])
			if not _none(b["repair"]) and int(b.get("repair_cost", 1)) == 0:
				rep += " (free)"
			var bld := "no card"
			if not _none(b["build"]):
				bld = "cleaned a wound" if String(b["build"]) == L8Rules.CLEAN else "added a %s guard" % _tname(String(b["build"]))
			var perk := ", 2 captures next raid" if int(b.get("extra_capture", 0)) > 0 else ""
			_ts(r.position + Vector2(14.0, 54.0), "then %s, %s, ran %s (income +%d, Heat +%d%s)" % [rep, bld,
				String(b["intensity"]), int(b["income"]), int(b["heat_add"]), perk], TXT, DIM, r.end.x - 10.0)
		y += 84.0
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
	_ts(Vector2(x, y), "Districts kept: %d   TAKEN: %d   Exploits kept: %d/%d   Wounds in the run deck: %d" % [live.size(),
		taken, ex_kept, L8Rules.EXPLOITS, L8Rules.wound_count(st)], 15, INK, PANEL_X - 20.0)
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
			["Heat bands (%d / %d: %d each)" % [L8Rules.EXTRA_AT, L8Rules.STRONG_AT, L8Rules.HEAT_BAND], "-%d" % bands],
			["wounds x %d (%d in the deck)" % [L8Rules.WOUND_COST, L8Rules.wound_count(st)], "-%d" % int(sp["wounds"])]]
		for rw: Variant in rows:
			var a: Array = rw
			var val := String(a[1])
			_tr(Vector2(px + w, py), val, 14, AMBER)
			py += maxf(24.0, _ts(Vector2(px, py), String(a[0]), 14, INK, px + w - _tw(val, 14) - 10.0) + 5.0)
		cv.draw_line(Vector2(px, py + 2.0), Vector2(px + w, py + 2.0), EDGE, 2.0)
		py += 10.0
		_t(Vector2(px, py), "TOTAL", 18, INK)
		_tr(Vector2(px + w, py - 4.0), _num(float(sp["total"])), 28, AMBER)
	if shots_dir == "":
		_btn(Rect2(px, LEGEND_Y - 58.0, w, 42.0), "PLAY THE LEG AGAIN [Enter]", "next", true, false, 16)


# ---------------------------------------------------------------- the frame
func _draw_ui() -> void:
	cv = ui
	hits = []
	resp_hover_opt = -1
	fc_hover = []
	if load_error != "":
		cv.draw_rect(Rect2(Vector2.ZERO, VIEW), BG)
		_t(Vector2(40.0, 40.0), load_error, 18, RED)
		return
	_draw_hud()
	var px := _px()
	cv.draw_rect(Rect2(px, HUD_H, VIEW.x - px, LEGEND_Y - HUD_H), Color(PANEL, 0.93))
	cv.draw_line(Vector2(px, HUD_H), Vector2(px, LEGEND_Y), EDGE, 1.0)
	match phase:
		Phase.DECAY:
			_draw_decay()
		Phase.CAPTURE:
			_draw_capture()
		Phase.DRAW:
			_draw_draw()
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
	if phase == Phase.RESPONSE:
		_draw_resp_pop()
		_sync_resp_preview()
	else:
		resp_pop_rect = Rect2()
	_sync_ghost()
	_draw_bottom()


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
	cv.draw_rect(Rect2(0.0, 0.0, VIEW.x, HUD_H), Color(BG, 0.88))
	cv.draw_line(Vector2(0.0, HUD_H), Vector2(VIEW.x, HUD_H), EDGE, 1.0)
	var v := _hud_values()
	var heat := int(v["heat"])
	var ghosts := L8Rules.extra_count(heat)
	if ghosts != heat_ghosts_k:
		heat_ghosts_k = ghosts
		board.set_heat_ghosts(ghosts, ghosts < 2)
	var fan := heat >= L8Rules.STRONG_AT
	if fan != fan_on:
		fan_on = fan
		board.set_fan(fan)
	var hx := 20.0
	var hy := 30.0
	var hw := 300.0
	var hh := 16.0
	_t(Vector2(hx, 7.0), "HEAT", BAR_TXT, DIM)
	cv.draw_rect(Rect2(hx, hy, hw, hh), Color8(20, 22, 36))
	var f := clampf(float(heat) / HEAT_MAX, 0.0, 1.0)
	cv.draw_rect(Rect2(hx, hy, hw * f, hh), AMBER.lerp(RED, f))
	cv.draw_rect(Rect2(hx, hy, hw, hh), EDGE, false, 1.5)
	for at: int in [L8Rules.EXTRA_AT, L8Rules.STRONG_AT]:
		var nx := hx + hw * float(at) / HEAT_MAX
		var lit := heat >= at
		var col := RED if lit else DIM
		cv.draw_line(Vector2(nx, hy - 5.0), Vector2(nx, hy + hh + 5.0), INK if lit else DIM, 3.0)
		var lab := "%d" % at
		_t(Vector2(nx + 4.0, 7.0), lab, BAR_TXT, col)
		var ix := nx + 4.0 + _tw(lab, BAR_TXT) + 10.0
		_beam_tick(Vector2(ix, 15.0), col)
		_card_tick(Vector2(ix + 15.0, 15.0), GOLD if lit else DIM)
	_t(Vector2(hx + hw + 12.0, 14.0), str(heat), 28, HEAT_COL)
	if String(v["note"]) != "":
		_t(Vector2(hx + hw + 62.0, 12.0), String(v["note"]), BAR_TXT, DIM)
	var hn := hand_ids.size() if (_hand_phase() and not hand_ids.is_empty()) else L8Rules.hand_size(heat)
	_t(Vector2(hx + hw + 62.0, 32.0), "hand %d" % hn, BAR_TXT, GOLD if hn > L8Rules.HAND_BASE else DIM)
	_t(Vector2(480.0, 7.0), "RAID", BAR_TXT, DIM)
	_t(Vector2(480.0, 22.0), "%d/%d" % [mini(raid + 1, L8Rules.RAIDS), L8Rules.RAIDS], 24, INK)
	_t(Vector2(560.0, 7.0), "HOME", BAR_TXT, DIM)
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
				cv.draw_rect(pr, RED.darkened(0.6).lerp(RED, pulse))
				cv.draw_rect(pr, WHITE.lerp(RED, 1.0 - pulse), false, 2.0)
				_skull(pr.get_center(), 6.0, WHITE, BLACK)
			else:
				cv.draw_rect(pr, GOLD)
		else:
			cv.draw_rect(pr, RED.darkened(0.5))
			cv.draw_rect(pr, RED, false, 2.0)
	_t(Vector2(670.0, 7.0), "BANK", BAR_TXT, DIM)
	_t(Vector2(670.0, 22.0), str(int(v["bank"])), 24, GOLD)
	_t(Vector2(750.0, 7.0), "LEG VALUE NOW", BAR_TXT, DIM)
	_t(Vector2(750.0, 20.0), String(v["score"]), 22, INK)
	var pt := _parts_text(v["sstate"])
	var ps := BAR_TXT
	while ps > 10 and _tw(pt, ps) > VIEW.x - PAD - 750.0:
		ps -= 1
	_t(Vector2(750.0, 46.0), pt, ps, DIM)
	var tag := "L8 CITY RAID  |  leg %d" % leg_seed
	if auto_line != "":
		tag += "  |  auto %s" % auto_line
	_tr(Vector2(VIEW.x - PAD, 6.0), tag, BAR_TXT, DIM)
	_tr(Vector2(VIEW.x - PAD, 24.0), "speed %dx%s%s" % [int(speed), "  instant" if instant else "",
		"  (2x fast)" if fast else ""], BAR_TXT, GOLD if fast else DIM)


## Overlay marks on the board: cell tags, repair costs, check rings, the DEPLOY line from the response card to its
## target, and placed cards shrinking from the hand row onto their district.
func _draw_board_marks() -> void:
	if phase in [Phase.PLAN, Phase.FORECAST, Phase.RESPONSE, Phase.AFTER, Phase.BETWEEN, Phase.DECAY, Phase.FALL]:
		for c: Vector2i in L8Rules.CELLS:
			var p := _screen(c)
			if p.x < _px():
				_tc(p + Vector2(0.0, 36.0), _cell_name(c), BAR_TXT, Color(DIM, 0.9))
	if phase == Phase.BETWEEN:
		for dv: Variant in _down_cells():
			var c: Vector2i = dv
			var p := _screen(c)
			var cost := L8Rules.repair_cost(leg, c, b_inten)
			_tc(p + Vector2(0.0, -50.0), "free" if cost == 0 else "-%d" % cost, 15, AMBER)
		if not _none(b_repair):
			_check_ring(_screen(b_repair))
	if phase == Phase.RESPONSE:
		if not _none(redeploy_from):
			_check_ring(_screen(redeploy_from))
		var j := _preview_opt()
		if j >= 0:
			var o: Dictionary = resp_opts[j]
			var r: Array = o["response"]
			if String(r[0]) == "DEPLOY":
				var t := String(r[1])
				var col: Color = TYPE_COLOR.get(t, ACID)
				var ci := hand_ids.find(String(o["card"]))
				var a := _card_rect(ci).get_center() if ci >= 0 else DECK_POS
				var b := _screen(r[2])
				cv.draw_line(a, b, Color(col, 0.7), 2.0)
	if not fly_cards.is_empty():
		var keep: Array = []
		var now := _now()
		for fv: Variant in fly_cards:
			var fd: Dictionary = fv
			var u := (now - float(fd["t0"])) * speed / FLY_T
			if u >= 1.0:
				continue
			keep.append(fd)
			var p: Vector2 = (fd["from"] as Vector2).lerp(fd["to"] as Vector2, u)
			var s := lerpf(1.0, 0.4, u)
			var rr := Rect2(p - Vector2(HCARD_H * 0.8, HCARD_H) * 0.5 * s, Vector2(HCARD_H * 0.8, HCARD_H) * s)
			_card_face(rr, fd["card"])
			cv.draw_rect(rr, AMBER, false, 1.5)
		fly_cards = keep
	if busy or auto_line != "":
		return
	if not (phase in [Phase.CAPTURE, Phase.PLAN, Phase.FORECAST, Phase.RESPONSE, Phase.BETWEEN]):
		return
	if mouse.x >= _px() or mouse.y < HUD_H or mouse.y > LEGEND_Y or resp_pop_rect.has_point(mouse):
		return
	var hc: Variant = _pick(mouse, phase == Phase.PLAN or phase == Phase.FORECAST)
	if not _none(hc):
		cv.draw_arc(_screen(hc), 30.0, 0.0, TAU, 32, INK, 2.0)


## L16 item 3: the tier ladder width at a font size.
func _ladder_w(size: int) -> float:
	var w := 0.0
	for tv: Variant in TIER_LADDER:
		w += 17.0 + _tw(String(tv), size) + 10.0
	return w - 10.0


## The tier ladder (glyph + one word, best to worst) with its center line at p.y.
func _draw_ladder(p: Vector2, size: int) -> void:
	var x := p.x
	var h := font.get_height(size)
	for tv: Variant in TIER_LADDER:
		var t: String = tv
		_tier_glyph(Vector2(x + 7.0, p.y), t, 7.0, _tier_col(t))
		_t(Vector2(x + 17.0, p.y - h * 0.5), t, size, _tier_col(t))
		x += 17.0 + _tw(t, size) + 10.0


## The bottom bar: legend with the pinned tier ladder, and the hint (right of the deck strip); in the hand phases the
## hand row takes the left part, and the right part holds the tier ladder over the wrapped hint.
func _draw_bottom() -> void:
	cv.draw_rect(Rect2(0.0, LEGEND_Y, VIEW.x, VIEW.y - LEGEND_Y), Color(BG, 0.92))
	cv.draw_line(Vector2(0.0, LEGEND_Y), Vector2(VIEW.x, LEGEND_Y), EDGE, 1.0)
	var msg := status_msg if status_msg != "" else _hint()
	var col := AMBER if status_msg != "" else DIM
	if _hand_phase():
		cv.draw_line(Vector2(PANEL_X, LEGEND_Y), Vector2(PANEL_X, VIEW.y), EDGE, 1.0)
		var maxw := PANEL_W - 16.0
		var ls := BAR_TXT
		while ls > 10 and _ladder_w(ls) > maxw:
			ls -= 1
		_draw_ladder(Vector2(PANEL_X + 8.0, LEGEND_Y + 10.0), ls)
		var lines := _wrap(msg, BAR_TXT, maxw)
		for i in range(mini(lines.size(), 2)):
			_t(Vector2(PANEL_X + 8.0, LEGEND_Y + 19.0 + float(i) * 14.0), lines[i], BAR_TXT, col)
		return
	if auto_line != "" and status_msg == "":
		msg = "[AUTO %s] %s" % [auto_line.to_upper(), msg]
	_draw_legend()
	var hs := BAR_TXT
	while hs > 10 and _tw(msg, hs) > VIEW.x - PAD - HAND_X:
		hs -= 1
	_t(Vector2(HAND_X, HINT_Y + 3.0), msg, hs, col)


func _draw_legend() -> void:
	var y := LEGEND_Y + 12.0
	var lw := _ladder_w(BAR_TXT)
	var lx := VIEW.x - PAD - lw
	_draw_ladder(Vector2(lx, y), BAR_TXT)
	cv.draw_line(Vector2(lx - 10.0, LEGEND_Y + 3.0), Vector2(lx - 10.0, LEGEND_Y + 21.0), EDGE, 1.0)
	var stop := lx - 16.0
	var x := HAND_X
	for tv: Variant in L8Rules.TYPES:
		var t: String = tv
		var tw := _tw(_tname(t), BAR_TXT)
		if x + 20.0 + tw > stop:
			return
		_glyph(Vector2(x + 8.0, y), t, 8.0, TYPE_COLOR[t])
		_t(Vector2(x + 20.0, y - 9.0), _tname(t), BAR_TXT, INK)
		x += 26.0 + tw
	var items: Array = ["SENTRY", "GHOST", "DOWN", "TAKEN", "EXPLOIT", "HUNTER", "HOME", "WOUND"]
	for iv: Variant in items:
		var it: String = iv
		var tw := _tw(it, BAR_TXT)
		if x + 20.0 + tw > stop:
			return
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
				cv.draw_rect(Rect2(c - Vector2(6.0, 8.0), Vector2(12.0, 16.0)), AMBER)
			"WOUND":
				cv.draw_rect(Rect2(c - Vector2(5.0, 7.0), Vector2(10.0, 14.0)), WOUND_FILL)
				_xmark(c, 4.0, RED, 1.5)
		_t(Vector2(x + 20.0, y - 9.0), it, BAR_TXT, DIM)
		x += 26.0 + tw


## The hand row (a Control of its own): wordless cards (verb glyph dominant, type corner badge, wounds cracked with a
## red X), the selected one, the gold-edged Heat extras, the placed ones (with their district), the SHIFT / JAM cards
## held for the response, and the spent response card.
func _draw_hand() -> void:
	hand_hits = []
	if load_error != "" or not _hand_phase() or hand_cards.is_empty():
		return
	cv = hand_ui
	hand_ui.draw_set_transform(-hand_ui.position)
	var playing := phase in [Phase.PLAY, Phase.REVEAL, Phase.RESPONSE]
	for i in range(hand_cards.size()):
		var cd: Array = hand_cards[i]
		var r := _card_rect(i)
		if phase == Phase.DRAW and not instant:
			var u := clampf(((_now() - deal_t0) * speed - float(i) * DEAL_GAP) / DEAL_T, 0.0, 1.0)
			if u <= 0.0:
				continue
			var e := 1.0 - pow(1.0 - u, 3.0)
			r.position = (DECK_POS - r.size * 0.5).lerp(r.position, e)
		var id := String(cd[0])
		var wound := L8Rules.is_wound(cd)
		var at: Variant = _card_cell(id)
		var verb := String(cd[2])
		var held := not wound and _none(at) and (verb == L8Rules.V_SHIFT or verb == L8Rules.V_JAM)
		var used := playing and used_card == id
		var hot := r.has_point(mouse) and auto_line == "" and not busy
		var edge := EDGE
		var tag := ""
		var tag_col := DIM
		if used:
			tag = "USED"
			tag_col = ACID
		elif not wound and not _none(at):
			tag = _cell_name(at)
			tag_col = AMBER
		elif held:
			tag = "HELD"
			tag_col = ACID
			edge = ACID.darkened(0.2)
		if hot:
			edge = INK
		if sel_card == id:
			edge = AMBER
		var dim := wound or (not _none(at) and not used)
		var fill := WOUND_FILL if wound else (PANEL.lerp(BG, 0.5) if dim else (PANEL_HI if sel_card == id else PANEL))
		_box(r, edge, fill, 2.5 if sel_card == id else 2.0)
		if i >= L8Rules.HAND_BASE:
			cv.draw_rect(r.grow(2.0), GOLD, false, 1.5)
		var gc := r.position + Vector2(34.0, 22.0)
		if wound:
			_crack(gc, 14.0, GREY.lightened(0.2), 2.0)
			_xmark(gc, 10.0, RED, 3.0)
		else:
			var t := String(cd[1])
			var col: Color = TYPE_COLOR.get(t, GREY)
			_verb_glyph(gc, verb, 13.0, DIM if dim else INK)
			_glyph(r.position + Vector2(10.0, 10.0), t, 6.0, col.darkened(0.45) if dim else col)
		if phase == Phase.PLAN or phase == Phase.FORECAST:
			_tr(Vector2(r.end.x - 6.0, r.position.y + 2.0), "[%d]" % (i + 1), BAR_TXT, DIM)
		else:
			_tr(Vector2(r.end.x - 6.0, r.position.y + 2.0), id, BAR_TXT, LATER)
		if tag != "":
			_tr(Vector2(r.end.x - 6.0, r.position.y + 22.0), tag, BAR_TXT, tag_col)
		if phase in [Phase.PLAN, Phase.FORECAST, Phase.RESPONSE]:
			hand_hits.append({"rect": r, "id": "card:%d" % i})


## The deck strip (a Control of its own) at the left edge of the bottom bar: one pip per card in the type color,
## wounds as red cracked pips; hovering shows the counts.
func _draw_deck() -> void:
	if load_error != "" or st.is_empty():
		return
	cv = deck_ui
	deck_ui.draw_set_transform(-deck_ui.position)
	var deck: Array = _deck_shown()
	var r := Rect2(0.0, LEGEND_Y, DECK_W, VIEW.y - LEGEND_Y)
	cv.draw_rect(r, Color(BG, 0.96))
	cv.draw_line(Vector2(r.end.x, LEGEND_Y), Vector2(r.end.x, VIEW.y), EDGE, 1.0)
	_t(Vector2(6.0, LEGEND_Y + 2.0), "DECK %d" % deck.size(), BAR_TXT, DIM)
	for i in range(deck.size()):
		var cd: Array = deck[i]
		var col_i := i % PIP_COLS
		var row_i := L8Rules.idiv(i, PIP_COLS)
		var pr := Rect2(6.0 + col_i * 8.0, LEGEND_Y + 22.0 + row_i * 8.0, 6.0, 6.0)
		if String(cd[2]) == L8Rules.V_WOUND:
			cv.draw_rect(pr, RED.darkened(0.35))
			cv.draw_line(pr.position + Vector2(1.0, 0.0), pr.end - Vector2(1.0, 0.0), BLACK, 1.0)
		else:
			cv.draw_rect(pr, TYPE_COLOR.get(String(cd[1]), GREY))
	if not r.has_point(mouse):
		return
	var nt := {"D": 0, "N": 0, "E": 0}
	var nv := {"GUARD": 0, "SHIFT": 0, "JAM": 0}
	var built := 0
	for cd: Array in deck:
		if nt.has(String(cd[1])):
			nt[String(cd[1])] = int(nt[String(cd[1])]) + 1
		if nv.has(String(cd[2])):
			nv[String(cd[2])] = int(nv[String(cd[2])]) + 1
		if String(cd[0]).begins_with("b"):
			built += 1
	var wn := _wounds_in(deck)
	var lines: Array = ["DECK %d cards (%d built)" % [deck.size(), built],
		"DRONE %d   NETRUNNER %d   ENFORCER %d" % [int(nt["D"]), int(nt["N"]), int(nt["E"])],
		"GUARD %d   SHIFT %d   JAM %d" % [int(nv["GUARD"]), int(nv["SHIFT"]), int(nv["JAM"])],
		"WOUNDS %d: -%d each at leg end" % [wn, L8Rules.WOUND_COST],
		"hand: %d cards (+1 at Heat %d, +1 at %d)" % [L8Rules.HAND_BASE, L8Rules.EXTRA_AT, L8Rules.STRONG_AT]]
	var bw := 0.0
	for lv: Variant in lines:
		bw = maxf(bw, _tw(String(lv), TXT))
	var box := Rect2(4.0, LEGEND_Y - 10.0 - lines.size() * 19.0 - 8.0, bw + 20.0, lines.size() * 19.0 + 10.0)
	_box(box, EDGE, Color(PANEL, 0.97), 1.5)
	for k in range(lines.size()):
		_t(box.position + Vector2(10.0, 5.0 + k * 19.0), String(lines[k]), TXT, RED if k == 3 and wn > 0 else INK)


func _hint() -> String:
	match phase:
		Phase.DECAY:
			return "DECAY: districts left DOWN are TAKEN by the corp; each wounds the deck. 1 2 4 set the speed, I toggles instant."
		Phase.CAPTURE:
			if cap_slots > 1:
				return "CAPTURE: claim %d of %d (HOT perk). Click a glowing district, or its row in the panel." % [cap_cells.size() + 1, cap_slots]
			return "CAPTURE: click a glowing district, or its row in the panel."
		Phase.DRAW:
			return "DRAW: the run deck deals this raid's hand. 1 2 4 speed, I instant."
		Phase.PLAN:
			return "PLAN: 1-6 a card, then a district (2 max). G ghost. Q W E, R, H outcomes. Z undo, Enter forecast."
		Phase.FORECAST:
			if launch_armed:
				return "FORECAST: Enter again launches anyway; B or an edit goes back."
			if fric > 0:
				return "FORECAST: launching needs a second Enter. Hover a cell to draw it; B goes back."
			return "FORECAST: hover a cell to draw it on the city; Q W E, R, H select. Enter launches, B goes back."
		Phase.PLAY, Phase.REVEAL:
			if fast:
				return "PLAYOUT: fast resolve at 2x (every row, one tier). 1 2 4 set the speed, I toggles instant."
			return "PLAYOUT: 1 2 4 set the speed, I toggles instant."
		Phase.RESPONSE:
			if hold_armed:
				return "RESPONSE: H again holds anyway; any other row or key cancels."
			return "RESPONSE: hover a row to see it on the city. H hold, J jam. Sentry > district moves; card or 1 2 3 > district deploys."
		Phase.AFTER:
			return "AFTERMATH: Enter goes on."
		Phase.BETWEEN:
			return "BETWEEN: click a DOWN district to repair it, B then 1 2 3 adds a guard card, C cleans a wound, 0 none, L N O the intensity, Enter starts the next raid."
		Phase.FALL:
			return "DECIDED: no plan can hold HOME. The record follows."
		Phase.RECORD:
			return "RECORD: Enter plays the leg again."
	return ""


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
	hand_ui.queue_redraw()
	deck_ui.queue_redraw()
	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var path := "%s/%03d_%s.png" % [shots_dir, shot_n, label]
	img.save_png(path)
	shot_n += 1
	print("shot ", path)


## Place the golden step's cards (card ids from this raid's hand) and ghost through the same handlers as a player.
func _auto_place(p: Dictionary) -> void:
	_push()
	place = {"sentries": {}, "ghost": null}
	tool = ""
	sel_card = ""
	var sd: Dictionary = p["sentries"]
	for c: Vector2i in L8Rules.sorted_cells(sd):
		var id := String(sd[c])
		var i := hand_ids.find(id)
		if i < 0:
			push_warning("auto %s raid %d: card %s is not in the hand" % [auto_line, raid + 1, id])
			continue
		sel_card = ""
		_select_card(i)
		_plan_click(c)
	if not _none(p["ghost"]):
		_set_tool("G", false)
		_plan_click(p["ghost"])
	tool = ""
	sel_card = ""
	_highlight_tool()
	_plan_view()


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


## Select the group holding the golden response (its hover list opens when the group is merged), and remember the exact
## option so its ghost overlay and preview show for the response beat (L17 item 2).
func _auto_select(r: Array) -> void:
	resp_sel = -1
	auto_opt = -1
	var key := str(r)
	for i in range(resp_opts.size()):
		if str((resp_opts[i] as Dictionary)["response"]) == key:
			auto_opt = i
			break
	for gi in range(resp_groups.size()):
		for m: Variant in (resp_groups[gi] as Dictionary)["members"]:
			if str((resp_opts[int(m)] as Dictionary)["response"]) == key:
				resp_sel = gi
				resp_follow = true
				return


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
	if s.has("cand_b") and int(s["cand_b"]) != int(row.get("cand_b", -1)):
		push_warning("auto %s raid %d: sealed B %d, golden %d" % [auto_line, int(s["raid"]) + 1,
			int(row.get("cand_b", -1)), int(s["cand_b"])])
	if ok_tier and ok_score:
		print("auto %s raid %d: %s, score %s (matches the golden)" % [auto_line, int(s["raid"]) + 1, String(row["tier"]), _num(float(row["score"]))])
	else:
		push_warning("auto %s raid %d MISMATCH: lab %s %s, golden %s %s" % [auto_line, int(s["raid"]) + 1, String(row["tier"]),
			_num(float(row["score"])), String(s["tier"]), _num(float(s["score_raid"]))])


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


## Replay the golden line's choices (every capture, the card placement, the response, the between step) through the
## same UI handlers. DECAY and DRAW run on their own; the golden hand is checked against the dealt one. The launch
## friction and the HOLD confirm, when they show, are shot and confirmed at once. A skipped RESPONSE (fast, nothing
## changes) holds on its own. The forecast beat carries the selected cell's ghost overlay, the response beat the
## chosen row's.
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
				_enter_draw()
		await _until([Phase.PLAN])
		var gh: Array = s.get("hand", [])
		if not gh.is_empty() and str(gh) != str(hand_ids):
			push_warning("auto %s raid %d: hand %s, golden %s" % [auto_line, rn, str(hand_ids), str(gh)])
		_auto_place(L8Rules.place_from_json(s["place"]))
		await _beat("r%d_plan" % rn)
		_enter_forecast()
		await _beat("r%d_forecast" % rn)
		_launch()
		if phase == Phase.FORECAST and launch_armed:
			await _beat("r%d_launch_friction" % rn)
			_launch()
		await _until([Phase.RESPONSE, Phase.AFTER])
		var resp := L8Rules.norm_response(s["response"])
		if phase == Phase.RESPONSE:
			_auto_select(resp)
			await _beat("r%d_response" % rn)
			_auto_respond(resp)
			if phase == Phase.RESPONSE and hold_armed:
				await _beat("r%d_hold_confirm" % rn)
				_auto_respond(resp)
		elif not resp.is_empty() and String(resp[0]) != "HOLD":
			push_warning("auto %s raid %d: response skipped (fast), golden %s" % [auto_line, rn, str(resp)])
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
