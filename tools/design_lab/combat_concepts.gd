extends Control
## Design lab (not part of the game): three combat-screen concepts for review, one idea
## per feedback item, numbered to match the list:
##   1 spinner, needle, HP and RAM   2 slice icons (action + value, label on hover)
##   3 actions around the spinner    5 SEND IT in dripping marker
##   6 "what will resolve" as icons over each spinner   (7: no log in any concept)
## Run: godot --path . res://tools/design_lab/combat_concepts.tscn -- --concept=A|B|C

const PLAYER := [[RC.SliceType.ATTACK, 6], [RC.SliceType.DEFEND, 5], [RC.SliceType.CRIT, 12], [RC.SliceType.ATTACK, 6], [RC.SliceType.MISS, 0], [RC.SliceType.ATTACK, 6]]
const ENEMY := [[RC.SliceType.DEFEND, 5], [RC.SliceType.ATTACK, 7], [RC.SliceType.CRIT, 12], [RC.SliceType.ATTACK, 7], [RC.SliceType.MISS, 0], [RC.SliceType.SHIELD, 4]]

var concept: String = "A"
## Pointer design for the E concepts (0 = the zine arrow of D).
var pointer: int = 0
var art: Control


func _ready() -> void:
	UiTheme.apply(self)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--concept="):
			concept = a.trim_prefix("--concept=")
	var bg := WireframeBackground.new()
	bg.city.dim = 0.62
	add_child(bg)
	bg.set_district(&"solace")
	art = Control.new()
	art.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	art.mouse_filter = Control.MOUSE_FILTER_IGNORE
	art.draw.connect(_draw_art)
	add_child(art)
	# Hand: the sticker cards stay (item 4).
	var hand := HBoxContainer.new()
	hand.position = Vector2(170, 560)
	hand.add_theme_constant_override("separation", 12)
	add_child(hand)
	var cards := [["BRUTE SPIN", 2, "Spin a wheel 6 ticks."], ["JOLT", 1, "Spin a wheel 3 ticks."], ["JOLT", 1, "Spin a wheel 3 ticks."], ["MIRROR FLIP", 3, "Flip a wheel."], ["CACHE", 0, "Gain 3 RAM."]]
	for i in cards.size():
		var c := ZineCard.new(cards[i][0], cards[i][1], cards[i][2], i)
		hand.add_child(c)
	var send := DripButton.new("SEND IT", "[SPACE]", DripButton.DRIP_PINK, 54, DripButton.SEND_IT_DRIPS)
	send.position = Vector2(1000, 560)
	add_child(send)
	var tag := Label.new()
	tag.text = "COMBAT CONCEPT %s  //  %s" % [concept, {"A": "DECK & TONEARM", "B": "NEON GAUGE", "C": "ZINE DIAL", "D1": "BLEND - flat paper tag", "D2": "BLEND - rounded speech bubble",
		"E1": "POINTER 1 - neon gauge blade", "E2": "POINTER 2 - gauge needle", "E3": "POINTER 3 - rim clamp", "E4": "POINTER 4 - blade in a notch"}[concept]]
	tag.theme_type_variation = &"HudLabel"
	tag.position = Vector2(0, 0)
	tag.size = Vector2(1280, 30)
	add_child(tag)


func _draw_art() -> void:
	var p := Vector2(380, 300)
	var e := Vector2(900, 300)
	match concept:
		"A":
			_wheel_deck(p, PLAYER, 0.9, Palette.CELL_PINK, 42, 60, true)
			_wheel_deck(e, ENEMY, 2.1, Palette.CORP_SOLACE, 30, 42, false)
			_actions_radial(p)
			_resolve_chips(p, e)
			_callout(Vector2(20, 60), 1, "tonearm needle, HP arc, RAM chips")
			_callout(Vector2(20, 90), 2, "icon + value inside each slice")
			_callout(Vector2(20, 120), 3, "nudge / respin / flip on the rim")
			_callout(Vector2(20, 150), 6, "result chips over each spinner")
			_callout(Vector2(20, 180), 5, "SEND IT: drip tag, key hint")
		"B":
			_wheel_gauge(p, PLAYER, 0.9, Palette.CELL_PINK, 42, 60, true)
			_wheel_gauge(e, ENEMY, 2.1, Palette.CORP_SOLACE, 30, 42, false)
			_actions_arcs(p)
			_resolve_ghost(p, e)
			_callout(Vector2(20, 60), 1, "pointer blade, HP in the hub, RAM cells")
			_callout(Vector2(20, 90), 2, "badge tiles: icon, value subscript")
			_callout(Vector2(20, 120), 3, "arc arrows + icon buttons")
			_callout(Vector2(20, 150), 6, "ghost pointer + outcome badge")
			_callout(Vector2(20, 180), 5, "SEND IT: acid drip tag")
		"D1", "D2", "E1", "E2", "E3", "E4":
			pointer = 0 if concept.begins_with("D") else int(concept.substr(1))
			_wheel_blend(p, PLAYER, 0.0, Palette.CELL_PINK, 42, 60, true)
			_wheel_blend(e, ENEMY, 0.0, Palette.CORP_SOLACE, 30, 42, false)
			_actions_stickers(p)
			if concept != "D2":
				_tag_bubble(p + Vector2(-80, -262), RC.SliceType.DEFEND, "+5 ×2 block!")
				_tag_bubble(e + Vector2(-60, -262), RC.SliceType.DEFEND, "+6 block")
			else:
				_round_bubble(p + Vector2(-80, -272), RC.SliceType.DEFEND, "+5 ×2 block!")
				_round_bubble(e + Vector2(-60, -272), RC.SliceType.DEFEND, "+6 block")
		_:
			_wheel_zine(p, PLAYER, 0.9, Palette.CELL_PINK, 42, 60, true)
			_wheel_zine(e, ENEMY, 2.1, Palette.CORP_SOLACE, 30, 42, false)
			_actions_stickers(p)
			_resolve_bubbles(p, e)
			_callout(Vector2(20, 60), 1, "taped arrow, HP tag, RAM tally")
			_callout(Vector2(20, 90), 2, "big marker value, icon corner")
			_callout(Vector2(20, 120), 3, "taped sticker actions")
			_callout(Vector2(20, 150), 6, "speech bubbles with icons")
			_callout(Vector2(20, 180), 5, "SEND IT: paper-white drip tag")


# --- Helpers -------------------------------------------------------------------------------

func _wedge(c: Vector2, r0: float, r1: float, a0: float, a1: float) -> PackedVector2Array:
	var pts := PackedVector2Array()
	for k in 13:
		var a := lerpf(a0, a1, k / 12.0)
		pts.append(c + Vector2(cos(a), sin(a)) * r1)
	for k in 13:
		var a := lerpf(a1, a0, k / 12.0)
		pts.append(c + Vector2(cos(a), sin(a)) * r0)
	return pts


func _slice_col(type: int) -> Color:
	return Palette.slice_color(type)


func _angle(i: int, n: int, rot: float) -> float:
	return -PI * 0.5 + TAU * i / n + rot


func _callout(at: Vector2, number: int, text: String) -> void:
	art.draw_circle(at, 13, Palette.CELL_ACID)
	art.draw_string(Palette.display(), at + Vector2(-13, 8), str(number), HORIZONTAL_ALIGNMENT_CENTER, 26, 20, Palette.INK)
	var w := Palette.mono().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 12).x
	art.draw_rect(Rect2(at + Vector2(16, -10), Vector2(w + 10, 20)), Color(0, 0, 0, 0.8))
	art.draw_string(Palette.mono(), at + Vector2(21, 5), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.CELL_ACID)


# --- Concept A: deck & tonearm -------------------------------------------------------------

func _wheel_deck(c: Vector2, slices: Array, rot: float, col: Color, hp: int, max_hp: int, player: bool) -> void:
	var r := 118.0
	var n := slices.size()
	art.draw_circle(c, r + 30, Color(0, 0, 0, 0.6))
	# HP: a segmented arc under the wheel.
	var segs := 20
	for k in segs:
		var a0 := PI * 0.15 + PI * 0.7 * k / segs
		var a1 := a0 + PI * 0.7 / segs * 0.8
		var lit := float(k) / segs < float(hp) / max_hp
		art.draw_colored_polygon(_wedge(c, r + 16, r + 26, a0, a1), Color("#3DFF8B") if lit else Color(1, 1, 1, 0.1))
	art.draw_string(Palette.display(), c + Vector2(-60, r + 56), "%d/%d HP" % [hp, max_hp], HORIZONTAL_ALIGNMENT_CENTER, 120, 22, Palette.PAPER)
	# Vinyl body with grooves, slices as wedges, icon + value inside each.
	art.draw_circle(c, r, Color("#07080F"))
	for g in 6:
		art.draw_arc(c, r * (0.35 + g * 0.1), 0, TAU, 48, Color(1, 1, 1, 0.05), 1.0)
	for i in n:
		var a0 := _angle(i, n, rot) - PI / n
		var a1 := a0 + TAU / n
		var t: int = slices[i][0]
		var sc := _slice_col(t)
		art.draw_colored_polygon(_wedge(c, r * 0.42, r, a0 + 0.02, a1 - 0.02), Color(sc, 0.35 if t != RC.SliceType.MISS else 0.08))
		art.draw_polyline(_wedge(c, r * 0.42, r, a0 + 0.02, a1 - 0.02), Color(sc, 0.9), 1.5)
		var mid := c + Vector2(cos((a0 + a1) * 0.5), sin((a0 + a1) * 0.5)) * r * 0.72
		SliceIcon.draw_icon(art, mid + Vector2(0, -9), 12, t, Palette.PAPER)
		if int(slices[i][1]) > 0:
			art.draw_string(Palette.display(), mid + Vector2(-20, 20), str(slices[i][1]), HORIZONTAL_ALIGNMENT_CENTER, 40, 20, Palette.PAPER)
	art.draw_circle(c, r * 0.4, Color("#12131C"))
	art.draw_arc(c, r * 0.4, 0, TAU, 32, Color(col, 0.8), 2.0)
	art.draw_arc(c, r, 0, TAU, 64, col, 2.5)
	# Tonearm from the upper right; the stylus touches the rim at the top.
	var pivot := c + Vector2(r + 20, -r - 20)
	var tip := c + Vector2(0, -r + 4)
	art.draw_circle(pivot, 12, Color("#2A2E38"))
	art.draw_arc(pivot, 12, 0, TAU, 20, col, 2.0)
	art.draw_line(pivot, tip + Vector2(20, -24), Color("#C9CED8"), 5.0)
	art.draw_line(tip + Vector2(20, -24), tip, Color("#C9CED8"), 5.0)
	art.draw_circle(tip, 7, Palette.PAPER)
	art.draw_circle(tip, 14, Color(Palette.PAPER, 0.25))
	art.draw_string(Palette.marker(), c + Vector2(-90, -r - 40), "BREAKER" if player else "BILLING DAEMON", HORIZONTAL_ALIGNMENT_CENTER, 180, 16, col)
	if player:
		# RAM chips.
		for k in 12:
			var rc := Rect2(c + Vector2(-96 + k * 16, r + 70), Vector2(12, 12))
			art.draw_rect(rc, Palette.NET_CYAN if k < 6 else Color(1, 1, 1, 0.1))
			art.draw_rect(rc, Color(Palette.NET_CYAN, 0.6), false, 1.0)
		art.draw_string(Palette.mono(), c + Vector2(104, r + 81), "RAM 6/12", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.NET_CYAN)


func _round_btn(at: Vector2, glyph: String, label: String, col: Color) -> void:
	art.draw_circle(at, 17, Color(Palette.NIGHT_SKY, 0.95))
	art.draw_arc(at, 17, 0, TAU, 24, col, 2.0)
	art.draw_string(Palette.display(), at + Vector2(-17, 7), glyph, HORIZONTAL_ALIGNMENT_CENTER, 34, 18, col)
	if label != "":
		art.draw_string(Palette.mono(), at + Vector2(-30, 32), label, HORIZONTAL_ALIGNMENT_CENTER, 60, 11, Palette.PAPER)


func _actions_radial(c: Vector2) -> void:
	_round_btn(c + Vector2(-158, -40), "◀", "-1 [Q]", Palette.CELL_ACID)
	_round_btn(c + Vector2(158, -40), "▶", "+1 [E]", Palette.CELL_ACID)
	_round_btn(c, "⟳", "", Palette.NET_CYAN)
	art.draw_string(Palette.mono(), c + Vector2(-30, 30), "RESPIN", HORIZONTAL_ALIGNMENT_CENTER, 60, 11, Palette.NET_CYAN)
	_round_btn(c + Vector2(-150, 70), "◎", "RING [R]", Palette.CELL_PINK)
	_round_btn(c + Vector2(150, 70), "⇄", "FLIP", Palette.CELL_PINK)


func _chip(at: Vector2, type: int, text: String, col: Color) -> void:
	var w := Palette.display().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 18).x + 40
	art.draw_rect(Rect2(at, Vector2(w, 30)), Color(Palette.NIGHT_SKY, 0.92))
	art.draw_rect(Rect2(at, Vector2(w, 30)), col, false, 1.5)
	SliceIcon.draw_icon(art, at + Vector2(16, 15), 10, type, col)
	art.draw_string(Palette.display(), at + Vector2(30, 23), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Palette.PAPER)


func _resolve_chips(p: Vector2, e: Vector2) -> void:
	_chip(p + Vector2(-80, -215), RC.SliceType.DEFEND, "+5 BLOCK ×2", Palette.NET_CYAN)
	_chip(e + Vector2(-70, -215), RC.SliceType.DEFEND, "+6 BLOCK", Palette.CORP_SOLACE)
	# Nothing hits this turn: a crossed arrow says so.
	art.draw_string(Palette.mono(), (p + e) * 0.5 + Vector2(-70, 0), "no damage this turn", HORIZONTAL_ALIGNMENT_CENTER, 140, 12, Color(Palette.PAPER, 0.7))


# --- Concept B: neon gauge ---------------------------------------------------------------

func _wheel_gauge(c: Vector2, slices: Array, rot: float, col: Color, hp: int, max_hp: int, player: bool) -> void:
	var r := 122.0
	var n := slices.size()
	art.draw_circle(c, r + 20, Color(0, 0, 0, 0.55))
	for i in n:
		var a0 := _angle(i, n, rot) - PI / n
		var a1 := a0 + TAU / n
		var t: int = slices[i][0]
		var sc := _slice_col(t)
		art.draw_colored_polygon(_wedge(c, r - 26, r, a0 + 0.04, a1 - 0.04), Color(sc, 0.8 if t != RC.SliceType.MISS else 0.15))
		var mid := c + Vector2(cos((a0 + a1) * 0.5), sin((a0 + a1) * 0.5)) * (r + 30)
		art.draw_circle(mid, 20, Color(Palette.NIGHT_SKY, 0.95))
		art.draw_arc(mid, 20, 0, TAU, 24, sc, 2.0)
		SliceIcon.draw_icon(art, mid, 11, t, Palette.PAPER)
		if int(slices[i][1]) > 0:
			art.draw_circle(mid + Vector2(14, 14), 10, sc)
			art.draw_string(Palette.display(), mid + Vector2(4, 20), str(slices[i][1]), HORIZONTAL_ALIGNMENT_CENTER, 20, 14, Palette.INK)
	# Inner HP ring and hub number.
	art.draw_arc(c, r - 40, 0, TAU, 64, Color(1, 1, 1, 0.08), 8.0)
	art.draw_arc(c, r - 40, -PI * 0.5, -PI * 0.5 + TAU * hp / max_hp, 64, Color("#3DFF8B"), 8.0)
	art.draw_string(Palette.display(), c + Vector2(-50, 14), str(hp), HORIZONTAL_ALIGNMENT_CENTER, 100, 44, Palette.PAPER)
	art.draw_string(Palette.mono(), c + Vector2(-50, 34), "/%d HP" % max_hp, HORIZONTAL_ALIGNMENT_CENTER, 100, 12, Palette.PAPER)
	# Pointer blade from the rim at the top, pointing in.
	var tip := c + Vector2(0, -r + 30)
	var blade := PackedVector2Array([tip, tip + Vector2(-13, -44), tip + Vector2(13, -44)])
	art.draw_colored_polygon(blade, Palette.PAPER)
	art.draw_polyline(blade + PackedVector2Array([blade[0]]), col, 2.0)
	art.draw_string(Palette.marker(), c + Vector2(-80, -r - 58), "BREAKER" if player else "BILLING DAEMON", HORIZONTAL_ALIGNMENT_CENTER, 160, 16, col)
	if player:
		for k in 12:
			var rc := Rect2(c + Vector2(-72 + k * 12, r + 58), Vector2(9, 18))
			art.draw_rect(rc, Palette.NET_CYAN if k < 6 else Color(1, 1, 1, 0.08))
		art.draw_string(Palette.mono(), c + Vector2(-72, r + 94), "RAM 6/12", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Palette.NET_CYAN)


func _actions_arcs(c: Vector2) -> void:
	for side in [-1.0, 1.0]:
		var a0 := PI + 0.5 if side < 0 else -0.5
		art.draw_arc(c, 190, a0, a0 + 0.8 * (1.0 if side < 0 else 1.0), 24, Palette.CELL_ACID, 4.0)
		var end := c + Vector2(cos(a0 + 0.8), sin(a0 + 0.8)) * 190
		art.draw_circle(end, 8, Palette.CELL_ACID)
		art.draw_string(Palette.display(), c + Vector2(side * 205 - 30, -20), "-1" if side < 0 else "+1", HORIZONTAL_ALIGNMENT_CENTER, 60, 22, Palette.CELL_ACID)
	for k in 3:
		var at := c + Vector2(-60 + k * 60, 200)
		art.draw_rect(Rect2(at - Vector2(22, 16), Vector2(44, 32)), Color(Palette.NIGHT_SKY, 0.95))
		art.draw_rect(Rect2(at - Vector2(22, 16), Vector2(44, 32)), Palette.NET_CYAN, false, 1.5)
		art.draw_string(Palette.display(), at + Vector2(-22, 8), ["⟳", "⇄", "◎"][k], HORIZONTAL_ALIGNMENT_CENTER, 44, 20, Palette.NET_CYAN)


func _resolve_ghost(p: Vector2, e: Vector2) -> void:
	# Ghost pointer: where this spin lands (dashed acid) and the outcome badge.
	for k in 10:
		var a := -PI * 0.5 + 0.1 * k
		if k % 2 == 0:
			art.draw_arc(p, 150, a, a + 0.08, 4, Palette.CELL_ACID, 3.0)
	_chip(p + Vector2(20, -220), RC.SliceType.DEFEND, "5 ×2 = 10 BLOCK", Palette.CELL_ACID)
	_chip(e + Vector2(-60, -220), RC.SliceType.DEFEND, "6 BLOCK", Palette.CORP_SOLACE)


# --- Concept C: zine dial -----------------------------------------------------------------

func _wheel_zine(c: Vector2, slices: Array, rot: float, col: Color, hp: int, max_hp: int, player: bool) -> void:
	var r := 116.0
	var n := slices.size()
	var papers := [Palette.NOTE_PAPER, Palette.STICKER_PINK, Palette.NOTE_YELLOW]
	for i in n:
		var a0 := _angle(i, n, rot) - PI / n
		var a1 := a0 + TAU / n
		var t: int = slices[i][0]
		var wedge := _wedge(c, 18, r, a0 + 0.03, a1 - 0.03)
		art.draw_colored_polygon(wedge, papers[i % 3] if t != RC.SliceType.MISS else Color(0.3, 0.3, 0.3))
		art.draw_polyline(wedge, Palette.INK, 2.0)
		var mid := c + Vector2(cos((a0 + a1) * 0.5), sin((a0 + a1) * 0.5)) * r * 0.62
		if int(slices[i][1]) > 0:
			art.draw_string(Palette.marker(), mid + Vector2(-20, 10), str(slices[i][1]), HORIZONTAL_ALIGNMENT_CENTER, 40, 30, Palette.INK)
		SliceIcon.draw_icon(art, mid + Vector2(18, -16), 9, t, _slice_col(t))
	# Taped paper arrow pointing down at the top slice.
	var tip := c + Vector2(0, -r + 10)
	var arrow := PackedVector2Array([tip, tip + Vector2(-16, -30), tip + Vector2(-6, -30), tip + Vector2(-6, -60), tip + Vector2(6, -60), tip + Vector2(6, -30), tip + Vector2(16, -30)])
	art.draw_colored_polygon(arrow, Palette.CELL_ACID)
	art.draw_polyline(arrow + PackedVector2Array([arrow[0]]), Palette.INK, 2.0)
	art.draw_rect(Rect2(tip + Vector2(-14, -58), Vector2(28, 10)), Palette.NOTE_TAPE)
	# HP tag (torn paper) and hearts.
	var tag := Rect2(c + Vector2(-70, r + 16), Vector2(140, 44))
	art.draw_rect(tag, Palette.NOTE_PAPER)
	art.draw_rect(tag, Palette.INK, false, 1.5)
	art.draw_string(Palette.display(), tag.position + Vector2(8, 34), "%d" % hp, HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.INK)
	art.draw_string(Palette.marker(), tag.position + Vector2(62, 30), "/%d HP" % max_hp, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.INK)
	art.draw_string(Palette.marker(), c + Vector2(-80, -r - 70), "BREAKER" if player else "BILLING DAEMON", HORIZONTAL_ALIGNMENT_CENTER, 160, 16, col)
	if player:
		var x := c.x - 60
		for k in 6:
			var gx := x + k * 10 + (k / 5) * 10
			art.draw_line(Vector2(gx, c.y + r + 74), Vector2(gx + 2, c.y + r + 94), Palette.NET_CYAN, 3.0)
		art.draw_string(Palette.marker(), Vector2(x + 76, c.y + r + 94), "RAM 6/12", HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.NET_CYAN)


func _sticker(at: Vector2, text: String, col: Color, tilt: float) -> void:
	art.draw_set_transform(at, tilt, Vector2.ONE)
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x + 20
	art.draw_rect(Rect2(Vector2(-w / 2 + 3, -14 + 4), Vector2(w, 30)), Palette.SHADOW)
	art.draw_rect(Rect2(Vector2(-w / 2, -14), Vector2(w, 30)), col)
	art.draw_rect(Rect2(Vector2(-w / 2, -14), Vector2(w, 30)), Palette.INK, false, 1.5)
	art.draw_rect(Rect2(Vector2(-12, -19), Vector2(24, 9)), Palette.NOTE_TAPE)
	art.draw_string(Palette.marker(), Vector2(-w / 2 + 10, 8), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.INK)
	art.draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


func _actions_stickers(c: Vector2) -> void:
	_sticker(c + Vector2(-205, -20), "◀ NUDGE", Palette.NOTE_YELLOW, -0.1)
	_sticker(c + Vector2(205, -20), "NUDGE ▶", Palette.NOTE_YELLOW, 0.08)
	_sticker(c + Vector2(-200, 70), "RESPIN", Palette.STICKER_PINK, 0.06)
	_sticker(c + Vector2(200, 70), "FLIP", Palette.NOTE_PAPER, -0.07)


func _bubble(at: Vector2, type: int, text: String) -> void:
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20).x + 50
	var rect := Rect2(at, Vector2(w, 40))
	art.draw_rect(rect, Palette.PAPER)
	art.draw_colored_polygon(PackedVector2Array([at + Vector2(24, 40), at + Vector2(44, 40), at + Vector2(30, 56)]), Palette.PAPER)
	art.draw_rect(rect, Palette.INK, false, 2.0)
	SliceIcon.draw_icon(art, at + Vector2(20, 20), 11, type, Palette.slice_color(type))
	art.draw_string(Palette.marker(), at + Vector2(38, 28), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.INK)


func _resolve_bubbles(p: Vector2, e: Vector2) -> void:
	_bubble(p + Vector2(-40, -262), RC.SliceType.DEFEND, "+5 ×2 block!")
	_bubble(e + Vector2(-40, -262), RC.SliceType.DEFEND, "+6 block")


# --- Concept D: the blend --------------------------------------------------------------------
# Neon gauge bars with icons in the wedge and values outside (no circles), a perfect-spot
# arrow on each slice's outer edge, zine dial arrow / stickers / bubble, tonearm HP + RAM.

func _wheel_blend(c: Vector2, slices: Array, rot: float, col: Color, hp: int, max_hp: int, player: bool) -> void:
	var r := 118.0
	var band := 40.0
	var n := slices.size()
	art.draw_circle(c, r + 36, Color(0, 0, 0, 0.55))
	art.draw_circle(c, r - band - 4, Color("#07080F"))
	for i in n:
		var a0 := _angle(i, n, rot) - PI / n
		var a1 := a0 + TAU / n
		var am := (a0 + a1) * 0.5
		var t: int = slices[i][0]
		var sc := _slice_col(t)
		var wedge := _wedge(c, r - band, r, a0 + 0.035, a1 - 0.035)
		art.draw_colored_polygon(wedge, Color(sc, 0.85 if t != RC.SliceType.MISS else 0.18))
		var closed := wedge.duplicate()
		closed.append(wedge[0])
		art.draw_polyline(closed, Color(sc.lightened(0.3), 0.9), 1.2)
		# Icon inside the bar.
		SliceIcon.draw_icon(art, c + Vector2(cos(am), sin(am)) * (r - band * 0.5), 12, t, Palette.PAPER)
		# Value outside the slice, no circle.
		if int(slices[i][1]) > 0:
			var vp := c + Vector2(cos(am), sin(am)) * (r + 30)
			art.draw_string(Palette.display(), vp + Vector2(-20, 9), str(slices[i][1]), HORIZONTAL_ALIGNMENT_CENTER, 40, 24, sc.lightened(0.35))
		# Perfect spot: a small white arrow inside the slice at its outer edge, pointing out.
		var tip := c + Vector2(cos(am), sin(am)) * (r - 3)
		var base := c + Vector2(cos(am), sin(am)) * (r - 11)
		var side := Vector2(-sin(am), cos(am)) * 5.0
		art.draw_colored_polygon(PackedVector2Array([tip, base + side, base - side]), Palette.PAPER)
	_pointer(c, r, band, col)
	art.draw_string(Palette.marker(), c + Vector2(-90, -r - 76), "BREAKER" if player else "BILLING DAEMON", HORIZONTAL_ALIGNMENT_CENTER, 180, 16, col)
	# Tonearm HP: segmented arc under the wheel with the number.
	var segs := 20
	var hp_col := Color("#3DFF8B")
	for k in segs:
		# Split around the bottom: the numbers sit in the gap.
		var a0 := PI * 0.1 + PI * 0.8 * k / segs
		var a1 := a0 + PI * 0.8 / segs * 0.8
		if absf((a0 + a1) * 0.5 - PI * 0.5) < 0.34:
			continue
		var lit := float(k) / segs < float(hp) / max_hp
		art.draw_colored_polygon(_wedge(c, r + 50, r + 60, a0, a1), hp_col if lit else Color(1, 1, 1, 0.1))
	art.draw_string(Palette.display(), c + Vector2(-50, r + 64), "%d/%d" % [hp, max_hp], HORIZONTAL_ALIGNMENT_CENTER, 100, 22, hp_col)
	if player:
		for k in 12:
			var rc := Rect2(c + Vector2(-96 + k * 16, r + 84), Vector2(12, 12))
			art.draw_rect(rc, Palette.NET_CYAN if k < 6 else Color(1, 1, 1, 0.1))
			art.draw_rect(rc, Color(Palette.NET_CYAN, 0.6), false, 1.0)


## The pointer at the top of the wheel (E concepts iterate from the neon gauge blade).
func _pointer(c: Vector2, r: float, band: float, col: Color) -> void:
	var top := c + Vector2(0, -r)
	match pointer:
		0:
			var ptip := c + Vector2(0, -r + 6)
			var arrow := PackedVector2Array([ptip, ptip + Vector2(-16, -30), ptip + Vector2(-6, -30), ptip + Vector2(-6, -62), ptip + Vector2(6, -62), ptip + Vector2(6, -30), ptip + Vector2(16, -30)])
			art.draw_colored_polygon(arrow, Palette.CELL_ACID)
			art.draw_polyline(arrow + PackedVector2Array([arrow[0]]), Palette.INK, 2.0)
			art.draw_rect(Rect2(ptip + Vector2(-14, -60), Vector2(28, 10)), Palette.NOTE_TAPE)
		1:
			# Neon gauge blade: a white blade from above the rim, its tip in the band, glowing.
			var tip := top + Vector2(0, band * 0.55)
			var blade := PackedVector2Array([tip, top + Vector2(-13, -30), top + Vector2(13, -30)])
			art.draw_colored_polygon(PackedVector2Array([tip + Vector2(0, 6), top + Vector2(-19, -36), top + Vector2(19, -36)]), Color(col, 0.25))
			art.draw_colored_polygon(blade, Palette.PAPER)
			art.draw_polyline(blade + PackedVector2Array([blade[0]]), col, 2.0)
		2:
			# Gauge needle: a thin needle from a hub above the wheel down through the band.
			var hub := top + Vector2(0, -34)
			var tip := top + Vector2(0, band + 2)
			art.draw_line(hub, tip, Color(Palette.CELL_ACID, 0.3), 9.0)
			art.draw_colored_polygon(PackedVector2Array([tip, hub + Vector2(-4, 0), hub + Vector2(4, 0)]), Palette.CELL_ACID)
			art.draw_circle(hub, 10, Palette.NIGHT_SKY)
			art.draw_arc(hub, 10, 0, TAU, 24, Palette.CELL_ACID, 2.5)
			art.draw_circle(hub, 3.5, Palette.CELL_ACID)
		3:
			# Rim clamp: two prongs straddle the band at the top with a centre hairline.
			var w := 22.0
			var clamp := PackedVector2Array([top + Vector2(-w, -26), top + Vector2(w, -26), top + Vector2(w, -8), top + Vector2(8, 4), top + Vector2(-8, 4), top + Vector2(-w, -8)])
			art.draw_colored_polygon(clamp, Palette.PAPER)
			art.draw_polyline(clamp + PackedVector2Array([clamp[0]]), col, 2.0)
			art.draw_line(top + Vector2(0, -20), top + Vector2(0, band + 4), Palette.CELL_ACID, 2.0)
			for sx in [-1.0, 1.0]:
				art.draw_line(top + Vector2(sx * 12, 4), top + Vector2(sx * 6, band * 0.6), Color(Palette.PAPER, 0.9), 3.0)
		_:
			# Blade in a notch: the rim ring is cut at the top and the blade sits in the cut,
			# a short acid tick marking the exact tick under it.
			art.draw_arc(c, r + 12, -PI * 0.5 + 0.18, -PI * 0.5 + TAU - 0.18, 64, Color(col, 0.7), 3.0)
			var tip := top + Vector2(0, band * 0.4)
			var blade := PackedVector2Array([tip, top + Vector2(-11, -20), top + Vector2(-11, -34), top + Vector2(11, -34), top + Vector2(11, -20)])
			art.draw_colored_polygon(blade, Palette.PAPER)
			art.draw_polyline(blade + PackedVector2Array([blade[0]]), Palette.INK, 2.0)
			art.draw_line(tip, tip + Vector2(0, band * 0.55), Palette.CELL_ACID, 2.0)


## D1: a flat taped paper tag, no tail.
func _tag_bubble(at: Vector2, type: int, text: String) -> void:
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20).x + 52
	art.draw_rect(Rect2(at + Vector2(4, 5), Vector2(w, 40)), Palette.SHADOW)
	art.draw_rect(Rect2(at, Vector2(w, 40)), Palette.NOTE_PAPER)
	art.draw_rect(Rect2(at, Vector2(w, 40)), Color(Palette.INK, 0.5), false, 1.0)
	art.draw_rect(Rect2(at + Vector2(w * 0.5 - 16, -6), Vector2(32, 11)), Palette.NOTE_TAPE)
	SliceIcon.draw_icon(art, at + Vector2(20, 20), 11, type, Palette.slice_color(type))
	art.draw_string(Palette.marker(), at + Vector2(38, 28), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.INK)


## D2: a rounded paper speech bubble with a curved tail.
func _round_bubble(at: Vector2, type: int, text: String) -> void:
	var w := Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20).x + 56
	var h := 44.0
	var pts := PackedVector2Array()
	var rad := 20.0
	var corners := [[Vector2(w - rad, rad), -PI * 0.5], [Vector2(w - rad, h - rad), 0.0], [Vector2(rad, h - rad), PI * 0.5], [Vector2(rad, rad), PI]]
	for cr in corners:
		for k in 7:
			var a: float = cr[1] + PI * 0.5 * k / 6.0
			pts.append(at + cr[0] + Vector2(cos(a), sin(a)) * rad)
	# Tail from the bottom edge, curving down-left.
	var tail := PackedVector2Array([at + Vector2(w * 0.45, h - 2), at + Vector2(w * 0.36, h + 22), at + Vector2(w * 0.32, h + 26), at + Vector2(w * 0.34, h + 18), at + Vector2(w * 0.3, h - 2)])
	var shadow := PackedVector2Array()
	for q in pts:
		shadow.append(q + Vector2(4, 5))
	art.draw_colored_polygon(shadow, Palette.SHADOW)
	art.draw_colored_polygon(pts, Palette.NOTE_PAPER)
	art.draw_colored_polygon(tail, Palette.NOTE_PAPER)
	var closed := pts.duplicate()
	closed.append(pts[0])
	art.draw_polyline(closed, Palette.INK, 2.0)
	art.draw_polyline(PackedVector2Array([tail[4], tail[3], tail[2], tail[1], tail[0]]), Palette.INK, 2.0)
	art.draw_line(tail[4] + Vector2(1, -1), tail[0] + Vector2(-1, -1), Palette.NOTE_PAPER, 3.0)
	SliceIcon.draw_icon(art, at + Vector2(24, h * 0.5), 11, type, Palette.slice_color(type))
	art.draw_string(Palette.marker(), at + Vector2(42, 30), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.INK)
