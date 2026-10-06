extends Control
## The material kit sheet (ART-1 1B, dev tool, not exported): every material of
## `scripts/ui/kit/materials/` at rest and through its motion, laid out like the round 3
## references so a windowed capture reads next to them:
##   --page=kit        `docs/art_reference/foundations/round3_overlay/combined_v2/04_kit_sheet.jpg`
##                     (sticker words, sticker objects, grease pencil on glass, light spill)
##   --page=lifecycle  `05_lifecycle.jpg` (SEND IT APPEAR / IDLE / EXIT with the pencil target)
##   --page=materials  the CRT terminal, decrypted holo, corp paper, binary bits and the 3D
##                     cel / toon + ink material
## The pieces loop their motion (`--still` holds the rest state). Run windowed only through
## tools/run_windowed.py, e.g.
##   python tools/run_windowed.py --log <log> -- res://tools/design_lab/kit_sheet.tscn
##     --resolution 1600x900 --write-movie <dir>/f.png --fixed-fps 30 --quit-after 150 -- --page=kit

const SHEET := Vector2(1600, 900)
const GROUND := Color(0.204, 0.204, 0.22)
const TXT := Color(0.91, 0.90, 0.88)
const SUB := Color(0.63, 0.63, 0.65)
const RULE := Color(0.43, 0.43, 0.455)
const COLS: Array[Vector2] = [Vector2(24, 392), Vector2(412, 792), Vector2(812, 1192), Vector2(1212, 1576)]
## Seconds between replays of a piece's motion on the sheet.
const LOOP := 3.0

var page: String = "kit"
var still: bool = false
var stage: Control = null
var _loops: Array[Callable] = []
var _clock: float = 0.0
var _next_loop: float = 0.6


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--page="):
			page = a.get_slice("=", 1)
		elif a == "--still":
			still = true
	set_anchors_preset(Control.PRESET_FULL_RECT)
	stage = Control.new()
	stage.size = SHEET
	add_child(stage)
	var bg := ColorRect.new()
	bg.color = GROUND
	bg.size = SHEET
	stage.add_child(bg)
	var grain := Control.new()
	grain.size = SHEET
	grain.draw.connect(_draw_grain.bind(grain))
	stage.add_child(grain)
	match page:
		"lifecycle":
			_build_lifecycle()
		"materials":
			_build_materials()
		_:
			_build_kit()
	get_viewport().size_changed.connect(_fit)
	_fit()


func _fit() -> void:
	var vs := get_viewport_rect().size
	var k := minf(vs.x / SHEET.x, vs.y / SHEET.y)
	stage.scale = Vector2(k, k)


func _process(delta: float) -> void:
	if still:
		return
	_clock += delta
	if _clock >= _next_loop:
		_next_loop = _clock + LOOP
		for f in _loops:
			f.call()


func _draw_grain(c: Control) -> void:
	for i in 2600:
		var p := Vector2(KitNoise.h01(9, i, 1) * SHEET.x, KitNoise.h01(9, i, 2) * SHEET.y)
		var v := KitNoise.h11(9, i, 3) * 0.035
		c.draw_rect(Rect2(p, Vector2(3, 3)), Color(1, 1, 1, maxf(v, 0.0)) if v > 0.0 else Color(0, 0, 0, -v))


# --- Helpers ------------------------------------------------------------------------------

func _label(text: String, at: Vector2, px: int, col: Color, font: Font = null, centre: bool = false, width: float = -1.0) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override(&"font", font if font != null else Palette.body_medium())
	l.add_theme_font_size_override(&"font_size", px)
	l.add_theme_color_override(&"font_color", col)
	l.position = at
	if centre:
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		l.size = Vector2(width if width > 0.0 else 300.0, px * 1.4)
		l.position = at - Vector2(l.size.x * 0.5, 0)
	stage.add_child(l)
	return l


func _rule(y: float, x0: float, x1: float) -> void:
	var r := ColorRect.new()
	r.color = RULE
	r.position = Vector2(x0, y)
	r.size = Vector2(x1 - x0, 1)
	stage.add_child(r)


func _head(col: int, h1: String, h2: String, body: String) -> void:
	var c := COLS[col]
	_rule(76, c.x, c.y)
	_label(h1, Vector2(c.x, 84), 22, TXT, Palette.body_medium())
	_label(h2, Vector2(c.x, 113), 14, Palette.CELL_PINK, Palette.body_medium())
	_label(body, Vector2(c.x, 592), 15, SUB, Palette.body())


func _sticker(text: String, fill: VinylSticker.Fill, at: Vector2, tilt: float, step: int = UiTheme.HERO, seed: int = 1) -> VinylSticker:
	var s := VinylSticker.new()
	s.text = text
	s.fill = fill
	s.font_step = step
	s.seed = seed
	stage.add_child(s)
	s.tilt_deg = tilt
	s.place_center(at)
	return s


func _object(shape: VinylSticker.Shape, size: Vector2, at: Vector2, tilt: float, stock: VinylSticker.Stock = VinylSticker.Stock.GLOSS) -> VinylSticker:
	var s := VinylSticker.new()
	s.shape = shape
	s.stock = stock
	s.body_size = size
	s.border_px = 10.0
	stage.add_child(s)
	s.tilt_deg = tilt
	s.place_center(at)
	return s


func _content_label(s: VinylSticker, text: String, at: Vector2, px: int, col: Color, font: Font) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override(&"font", font)
	l.add_theme_font_size_override(&"font_size", px)
	l.add_theme_color_override(&"font_color", col)
	l.position = at
	s.content_root.add_child(l)
	return l


# --- Page: kit (04_kit_sheet.jpg) ---------------------------------------------------------

func _build_kit() -> void:
	_label("REBEL_CELL MATERIAL KIT  v2 (Godot)", Vector2(24, 16), 28, TXT, Palette.body_medium())
	_label("stickers for every word and object  //  grease pencil for plans  //  light spill in the base  //  CRT for the Cell's systems",
		Vector2(520, 26), 16, SUB, Palette.body())
	_head(0, "C  STICKER WORDS", "VERBS + HEADLINES", "bold die-cut lettering: black keyline, chunky\nextrude, thick crisp white border, gloss 0.22 at rest,\none slow sweep on one sticker at a time. Holo foil on\nthe primary verb, slapped over the system word.")
	_head(1, "C  STICKER OBJECTS", "THINGS", "crew ID (holo), Heat poster, price dot, kraft note\ncard. White or kraft die-cut, gloss, soft shadow,\ncorner curl. Holo only on the key items.")
	_head(2, "A  GREASE PENCIL ON GLASS", "PLANS", "yellow = plan and route, red = threat and target.\nSolid = will happen, dashed = what-if. Waxy lit\nstrokes, dropouts, 4 px cast shadow; writes on and\nwipes off by trimming points (never alpha).")
	_head(3, "D  LIGHT SPILL", "BASE LAYER", "glowing base elements (neon, MAINFRAME sign, spinner\nrims) light the facets around them: the spill\nmultiplies what is under it plus a little haze.")
	_build_sticker_words()
	_build_sticker_objects()
	_build_pencil_column()
	_build_spill_column()
	_build_footer()


func _build_sticker_words() -> void:
	var sw := SystemWordSticker.new()
	sw.position = Vector2(58, 152)
	sw.size = Vector2(300, 92)
	stage.add_child(sw)
	sw.set_verb("SEND IT", VinylSticker.Fill.HOLO)
	sw.sticker.rest_curl = 0.09
	sw.sticker.ambient_sweep = true
	_label("primary verb (holo) over system word", Vector2(208, 318), 14, SUB, Palette.body_medium(), true, 340)
	var leave := _sticker("LEAVE", VinylSticker.Fill.PINK, Vector2(108, 390), -4, UiTheme.DISPLAY, 23)
	var hit := _sticker("HIT THIS", VinylSticker.Fill.RED, Vector2(300, 410), 5, UiTheme.DISPLAY, 33)
	var ours := _sticker("OURS", VinylSticker.Fill.YELLOW, Vector2(110, 492), 4, UiTheme.DISPLAY, 31)
	var them := _sticker("THEM", VinylSticker.Fill.RED, Vector2(290, 500), -5, UiTheme.DISPLAY, 41)
	for s in [leave, hit, ours, them]:
		(s as VinylSticker).ambient_sweep = true
	_label("verb  /  headline words", Vector2(208, 556), 14, SUB, Palette.body_medium(), true, 340)
	_loops.append(func() -> void:
		sw.sticker.slap())


func _build_sticker_objects() -> void:
	# crew ID: a holo die-cut card with a portrait stand-in, name plate and class line
	var crew := _object(VinylSticker.Shape.RECT, Vector2(138, 168), Vector2(510, 262), 4, VinylSticker.Stock.HOLO)
	crew.lifted_corner = VinylSticker.Lift.BOTTOM_RIGHT
	crew.rest_curl = 0.09
	var face := Control.new()
	face.draw.connect(func() -> void:
		face.draw_rect(Rect2(6, 20, 106, 92), Palette.RESIST_GOLD)
		face.draw_circle(Vector2(59, 72), 34.0, Palette.HARM)
		face.draw_rect(Rect2(36, 60, 46, 40), Palette.VINYL_INK)
		face.draw_rect(Rect2(36, 66, 46, 7), Palette.CELL_PINK)
		face.draw_rect(Rect2(6, 100, 106, 12), Palette.HARM.darkened(0.3)))
	crew.content_root.add_child(face)
	_content_label(crew, "CELL-9 // CREW", Vector2(8, 2), 10, Palette.VINYL_INK, Palette.mono())
	_content_label(crew, "VOSS", Vector2(8, 114), 24, Palette.VINYL_INK, Palette.display())
	crew.refresh()
	# Heat poster
	var heat := _object(VinylSticker.Shape.RECT, Vector2(132, 170), Vector2(700, 256), -4)
	heat.lifted_corner = VinylSticker.Lift.BOTTOM_LEFT
	heat.rest_curl = 0.10
	var dark := ColorRect.new()
	dark.color = Palette.VINYL_INK
	dark.size = Vector2(112, 150)
	heat.content_root.add_child(dark)
	var stripes := Control.new()
	stripes.draw.connect(func() -> void:
		stripes.draw_rect(Rect2(0, 0, 112, 16), Palette.RESIST_GOLD)
		for i in 8:
			var x := i * 14.0
			stripes.draw_colored_polygon(PackedVector2Array([Vector2(x, 16), Vector2(x + 7, 16), Vector2(x + 15, 0), Vector2(x + 8, 0)]), Palette.VINYL_INK))
	heat.content_root.add_child(stripes)
	_content_label(heat, "HEAT", Vector2(8, 16), 22, Palette.RESIST_GOLD, Palette.display())
	_content_label(heat, "62", Vector2(14, 40), 54, Palette.STICKER_DIE_CUT, Palette.display())
	var band := ColorRect.new()
	band.color = Palette.HARM
	band.position = Vector2(4, 120)
	band.size = Vector2(104, 24)
	heat.content_root.add_child(band)
	_content_label(heat, "FLAGGED", Vector2(20, 120), 18, Palette.STICKER_DIE_CUT, Palette.display())
	heat.refresh()
	_label("crew ID / holo", Vector2(510, 372), 14, SUB, Palette.body_medium(), true, 160)
	_label("Heat poster", Vector2(700, 372), 14, SUB, Palette.body_medium(), true, 160)
	# kraft note card
	var note := _object(VinylSticker.Shape.RECT, Vector2(206, 92), Vector2(530, 470), -3, VinylSticker.Stock.KRAFT)
	note.rest_curl = 0.12
	_content_label(note, "BACKDOOR FIRST\nTHEN BRUTE IT", Vector2(12, 14), 19, Palette.VINYL_INK, Palette.pencil())
	_content_label(note, "CELL//NOTE", Vector2(130, 4), 10, Palette.KRAFT_FIBRE, Palette.mono())
	note.refresh()
	# price dot
	var dot := _object(VinylSticker.Shape.CIRCLE, Vector2(64, 64), Vector2(722, 474), 9)
	var disc := Control.new()
	disc.draw.connect(func() -> void:
		disc.draw_circle(Vector2(22, 22), 22.0, Palette.RESIST_GOLD))
	dot.content_root.add_child(disc)
	_content_label(dot, "60", Vector2(8, 4), 26, Palette.VINYL_INK, Palette.display())
	dot.refresh()
	_label("note card / kraft", Vector2(530, 556), 14, SUB, Palette.body_medium(), true, 200)
	_label("price dot", Vector2(722, 520), 14, SUB, Palette.body_medium(), true, 120)


func _build_pencil_column() -> void:
	var glass := Rect2(825, 152, 354, 392)
	var bg := Control.new()
	bg.draw.connect(func() -> void:
		bg.draw_rect(glass, Color(0.085, 0.085, 0.10))
		# printed reticle and range ring (print, not pencil)
		var c := Vector2(1093, 246)
		var red := Palette.PENCIL_THREAT
		red.a = 0.8
		# printed corner brackets round the target
		for k in 4:
			var sx := -1.0 if k % 2 == 0 else 1.0
			var sy := -1.0 if k < 2 else 1.0
			var corner := c + Vector2(sx, sy) * 50.0
			bg.draw_line(corner, corner - Vector2(sx * 14.0, 0), red, 1.6, true)
			bg.draw_line(corner, corner - Vector2(0, sy * 14.0), red, 1.6, true)
		var ring := red
		ring.a = 0.55
		for k in 36:
			if k % 2 == 0:
				bg.draw_arc(c, 72, k * TAU / 36.0, (k + 1) * TAU / 36.0, 4, ring, 1.4, true)
		# the acrylic sheen band across the glass
		var sheen := Color(0.85, 0.92, 1.0, 0.04)
		bg.draw_colored_polygon(PackedVector2Array([glass.position + Vector2(150, 0), glass.position + Vector2(230, 0),
			glass.position + Vector2(90, glass.size.y), glass.position + Vector2(10, glass.size.y)]), sheen))
	stage.add_child(bg)
	var pencil := Node2D.new()
	stage.add_child(pencil)
	var target := GreasePencilMark.new()
	target.ink = GreasePencilMark.Ink.THREAT
	target.seed = 7
	pencil.add_child(target)
	target.add_stroke(PencilShapes.hand_circle(Vector2(1093, 246), Vector2(42, 40), 7, 1.15))
	var word := GreasePencilWord.new()
	word.text = "HIT IT"
	word.text_step = UiTheme.DISPLAY
	word.position = Vector2(860, 268)
	pencil.add_child(word)
	var arrow := GreasePencilMark.new()
	arrow.ink = GreasePencilMark.Ink.THREAT
	arrow.seed = 9
	pencil.add_child(arrow)
	for s in PencilShapes.arrow(PencilShapes.bezier(Vector2(1000, 262), Vector2(1024, 274), Vector2(1046, 258)), 14.0, 9):
		arrow.add_stroke(s)
	var plan := GreasePencilMark.new()
	plan.ink = GreasePencilMark.Ink.PLAN
	plan.seed = 11
	pencil.add_child(plan)
	plan.add_stroke(PencilShapes.hand_circle(Vector2(907, 372), Vector2(34, 40), 11, 1.1))
	var route := GreasePencilMark.new()
	route.ink = GreasePencilMark.Ink.PLAN
	route.dashed = true
	route.seed = 13
	pencil.add_child(route)
	var path := PencilShapes.chaikin(PackedVector2Array([Vector2(858, 505), Vector2(925, 472), Vector2(1000, 483), Vector2(1075, 440), Vector2(1125, 392)]), 3)
	for s in PencilShapes.arrow(path, 20.0, 13):
		route.add_stroke(s)
	var wp := Control.new()
	wp.draw.connect(func() -> void:
		wp.draw_circle(Vector2(1000, 483), 13.0, Palette.PENCIL_PLAN)
		wp.draw_arc(Vector2(1000, 483), 13.0, 0, TAU, 24, Palette.VINYL_INK, 2.0, true)
		wp.draw_string(Palette.display(), Vector2(995, 491), "1", HORIZONTAL_ALIGNMENT_LEFT, -1, 20, Palette.VINYL_INK))
	stage.add_child(wp)
	var marks: Array = [word, arrow, target, plan, route]
	_loops.append(func() -> void:
		var t := 0.0
		for m in marks:
			var mk: Node2D = m
			get_tree().create_timer(t).timeout.connect(func() -> void: mk.call(&"write_on"))
			t += 0.35
		get_tree().create_timer(2.2).timeout.connect(func() -> void: route.wipe()))


## A faceted low-poly backdrop (Cv2 stand-in: triangles with tone jitter) in `r`.
func _facets(c: Control, r: Rect2, seed: int, hue: Color, cell: float = 34.0) -> void:
	var cols := int(r.size.x / cell) + 4
	var rows := int(r.size.y / cell) + 4
	var pts := []
	for y in rows:
		var row := []
		for x in cols:
			var j := Vector2(KitNoise.h11(seed, x, y), KitNoise.h11(seed, y, x + 99)) * cell * 0.38
			row.append(r.position + Vector2((x - 1) * cell, (y - 1) * cell) + j)
		pts.append(row)
	for y in rows - 1:
		for x in cols - 1:
			var a: Vector2 = pts[y][x]
			var b: Vector2 = pts[y][x + 1]
			var cc: Vector2 = pts[y + 1][x]
			var d: Vector2 = pts[y + 1][x + 1]
			for k in 2:
				var tri := PackedVector2Array([a, b, d]) if k == 0 else PackedVector2Array([a, d, cc])
				var tone := 0.10 + 0.14 * KitNoise.h01(seed, x * 7 + k, y * 13)
				var col := Palette.NIGHT_SKY.lerp(hue, tone)
				col = col.lightened(0.04 * KitNoise.h01(seed + 1, x, y * 2 + k))
				c.draw_colored_polygon(tri, col)


func _neon(c: Control, at: Vector2, word: String) -> void:
	var font := Palette.display()
	var px := 40
	c.draw_rect(Rect2(at - Vector2(52, 40), Vector2(104, 392)), Palette.CELL_PINK.darkened(0.2), false, 6.0)
	c.draw_rect(Rect2(at - Vector2(52, 40), Vector2(104, 392)), Palette.CELL_PINK.lightened(0.6), false, 2.0)
	for i in word.length():
		var w := font.get_string_size(word[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		var p := at + Vector2(-w * 0.5, 34 + i * 40)
		# a hollow tube: the glow, the pink tube and its hot core
		c.draw_string_outline(font, p, word[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px, 7, Palette.CELL_PINK.darkened(0.4))
		c.draw_string_outline(font, p, word[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px, 4, Palette.CELL_PINK)
		c.draw_string_outline(font, p, word[i], HORIZONTAL_ALIGNMENT_LEFT, -1, px, 2, Palette.CELL_PINK.lightened(0.8))


func _build_spill_column() -> void:
	for k in 2:
		var box := Control.new()
		box.position = Vector2(1232 + k * 178, 152)
		box.size = Vector2(163, 392)
		box.clip_contents = true
		var r := Rect2(Vector2.ZERO, box.size)
		box.draw.connect(func() -> void:
			_facets(box, r, 21, Palette.NEON_VIOLET)
			_neon(box, Vector2(81, 36), "MAINFRAME"))
		stage.add_child(box)
		if k == 1:
			var spill := LightSpill.new()
			spill.position = Vector2(81, 196)
			spill.source_size = Vector2(110, 400)
			spill.reach = 90.0
			spill.gain = LightSpill.GAIN_SHOP
			box.add_child(spill)
	_label("before", Vector2(1313, 552), 14, SUB, Palette.body_medium(), true, 120)
	_label("after spill", Vector2(1491, 552), 14, SUB, Palette.body_medium(), true, 120)


func _build_footer() -> void:
	_rule(700, 24, 1576)
	_label("PALETTE", Vector2(24, 712), 18, TXT, Palette.body_medium())
	var chips := [[Palette.CELL_PINK, "PINK", "verb stickers"], [Palette.STICKER_DIE_CUT, "WHITE", "die-cut border"],
		[Palette.VINYL_INK, "BLACK", "keyline, ink"], [Palette.PENCIL_PLAN, "YELLOW", "plan, route"],
		[Palette.PENCIL_THREAT, "RED", "threat, target"], [Palette.KRAFT, "KRAFT", "note cards"], [Palette.NET_CYAN, "CYAN", "CRT terminal"]]
	for i in chips.size():
		var x := 24.0 + i * 160.0
		var sw := ColorRect.new()
		sw.color = chips[i][0]
		sw.position = Vector2(x, 744)
		sw.size = Vector2(52, 52)
		stage.add_child(sw)
		_label(chips[i][1], Vector2(x + 62, 746), 16, TXT, Palette.body_medium())
		_label(chips[i][2], Vector2(x + 62, 770), 13, SUB, Palette.body())
	_label("RULES", Vector2(1180, 712), 18, TXT, Palette.body_medium())
	_label("Order: base > spill > pencil > object stickers > word stickers.\nEvery word is a sticker; pencil plans; CRT is the Cell.\nNever over spinner values, node icons, prices or HP.\nNo UI ever covers grease pencil.",
		Vector2(1180, 744), 13, SUB, Palette.body())


# --- Page: lifecycle (05_lifecycle.jpg) ---------------------------------------------------

func _build_lifecycle() -> void:
	var bg := ColorRect.new()
	bg.color = Palette.NET_BG_OUTER.lerp(Palette.DESK_DARK, 0.6)
	bg.size = SHEET
	stage.add_child(bg)
	_label("SEND IT  /  KIT LIFECYCLE  v2 (Godot)", Vector2(36, 26), 28, TXT, Palette.body_medium())
	_label("holo verb sticker + grease-pencil target, moving together on the combat screen", Vector2(36, 66), 16, SUB, Palette.body())
	var heads := [["01  APPEAR", "0.00 - 0.45 s", "SEND IT drops in from 1.24x, over-rotated 13 deg, and slaps:\nsquash 1.13 / 0.84 (90 ms), one overshoot, shine sweep.\nThe red pencil circle draws in writing order."],
		["02  IDLE", "loop", "The top-right corner flutters 0.08 <-> 0.20 (2.4 s).\nThe holo foil hue drifts; the gloss band breathes.\nA thin glint runs across the wax every ~3 s."],
		["03  EXIT", "0.30 s with the page", "The sticker peels from its lifted corner (fold 0 -> 0.6),\nlifts (shadow blurs) and curls away down-left.\nA palm drags the pencil off (cloth wipe). EXECUTE stays."]]
	for k in 3:
		var panel := Control.new()
		panel.position = Vector2(36 + k * 524, 108)
		panel.size = Vector2(500, 584)
		panel.clip_contents = true
		var r := Rect2(Vector2.ZERO, panel.size)
		panel.draw.connect(func() -> void:
			_facets(panel, r, 40, Palette.CORP_HALCYON, 46.0)
			panel.draw_rect(r, RULE, false, 1.0)
			# a slice "6" the pencil targets and a card stand-in
			panel.draw_colored_polygon(PackedVector2Array([Vector2(60, 90), Vector2(200, 60), Vector2(170, 190)]), Palette.NET_CYAN.darkened(0.55))
			panel.draw_string(Palette.display(), Vector2(98, 132), "6", HORIZONTAL_ALIGNMENT_LEFT, -1, 40, Palette.TEXT_HI)
			var card := Rect2(10, 360, 170, 240)
			panel.draw_rect(card, Palette.HARM.darkened(0.45))
			panel.draw_rect(card, Palette.PAPER_ALT.darkened(0.3), false, 3.0)
			panel.draw_string(Palette.display(), Vector2(24, 520), "BRUTE FORCE", HORIZONTAL_ALIGNMENT_LEFT, -1, 24, Palette.PAPER))
		stage.add_child(panel)
		# kraft note
		var note := VinylSticker.new()
		note.shape = VinylSticker.Shape.RECT
		note.stock = VinylSticker.Stock.KRAFT
		note.body_size = Vector2(206, 100)
		note.rest_curl = 0.12
		panel.add_child(note)
		note.tilt_deg = 3
		note.place_center(Vector2(380, 180))
		_content_label(note, "SLICE 6 CRACKED\nBACKDOOR FIRST\nTHEN BRUTE IT", Vector2(12, 8), 18, Palette.VINYL_INK, Palette.pencil())
		note.refresh()
		# EXECUTE + SEND IT
		var sw := SystemWordSticker.new()
		sw.position = Vector2(250, 400)
		sw.size = Vector2(220, 96)
		sw.hint = "> turn_resolve.exe [SPACE]"
		sw.word_step = UiTheme.HEADING
		panel.add_child(sw)
		sw.set_verb("SEND IT", VinylSticker.Fill.HOLO)
		sw.sticker.rest_curl = 0.08
		# pencil: circle round the 6, HIT IT, an arrow
		var circle := GreasePencilMark.new()
		circle.ink = GreasePencilMark.Ink.THREAT
		circle.seed = 5 + k
		panel.add_child(circle)
		circle.add_stroke(PencilShapes.hand_circle(Vector2(112, 118), Vector2(44, 40), 5, 1.15))
		var word := GreasePencilWord.new()
		word.text = "HIT IT"
		word.position = Vector2(240, 70)
		panel.add_child(word)
		var arrow := GreasePencilMark.new()
		arrow.ink = GreasePencilMark.Ink.THREAT
		panel.add_child(arrow)
		for s in PencilShapes.arrow(PencilShapes.bezier(Vector2(250, 84), Vector2(200, 120), Vector2(160, 116)), 14.0, 3):
			arrow.add_stroke(s)
		_label(heads[k][0], Vector2(52 + k * 524, 704), 22, TXT, Palette.body_medium())
		_label(heads[k][1], Vector2(380 + k * 524, 708), 15, SUB, Palette.body())
		_label(heads[k][2], Vector2(52 + k * 524, 740), 15, SUB, Palette.body())
		var tick := ColorRect.new()
		tick.color = Palette.CELL_PINK
		tick.position = Vector2(36 + k * 524, 704)
		tick.size = Vector2(5, 26)
		stage.add_child(tick)
		var st := sw.sticker
		var pen: Array = [circle, arrow, word]
		match k:
			0:
				_loops.append(func() -> void:
					st.slap()
					for m in pen:
						(m as Node2D).call(&"write_on"))
			1:
				st.flutter = true
				st.ambient_sweep = true
			2:
				_loops.append(func() -> void:
					st.slap()
					for m in pen:
						(m as Node2D).call(&"write_on")
					get_tree().create_timer(1.2).timeout.connect(func() -> void:
						st.peel()
						for m in pen:
							(m as Node2D).call(&"wipe")))


# --- Page: materials -----------------------------------------------------------------------

func _build_materials() -> void:
	_label("REBEL_CELL MATERIAL KIT  v2 (Godot): screens, intel, data, world", Vector2(24, 16), 28, TXT, Palette.body_medium())
	# CRT terminal
	_rule(76, 24, 520)
	_label("CRT TERMINAL", Vector2(24, 84), 22, TXT)
	_label("THE CELL'S SYSTEMS", Vector2(24, 113), 14, Palette.CELL_PINK)
	var kinds := [CrtTerminalPanel.Accent.CELL, CrtTerminalPanel.Accent.FIRMWARE, CrtTerminalPanel.Accent.SCHEMATICS, CrtTerminalPanel.Accent.DISPATCH]
	var lines := ["RAM 5/12  // next turn +2", "FIRMWARE: OVERCLOCK socketed", "SCHEMATICS 400  [B] buy", "DISPATCH: units en route to SITE 4"]
	var panels: Array[CrtTerminalPanel] = []
	for i in kinds.size():
		var p := CrtTerminalPanel.new()
		p.accent_kind = kinds[i]
		p.position = Vector2(40, 150 + i * 92)
		p.size = Vector2(460, 64)
		stage.add_child(p)
		p.text = lines[i]
		panels.append(p)
	_loops.append(func() -> void:
		for i in panels.size():
			panels[i].type_on(lines[i]))
	# binary bits: round a wheel rim into the HP
	_rule(76, 560, 1060)
	_label("BINARY BITS", Vector2(560, 84), 22, TXT)
	_label("DATA MOVING", Vector2(560, 113), 14, Palette.CELL_PINK)
	var wheel := Control.new()
	wheel.position = Vector2(560, 150)
	wheel.size = Vector2(480, 400)
	var centre := Vector2(200, 200)
	wheel.draw.connect(func() -> void:
		wheel.draw_circle(centre, 150.0, Palette.NET_BG_INNER)
		wheel.draw_arc(centre, 150.0, 0.0, TAU, 96, Palette.CELL_PINK, 4.0, true)
		wheel.draw_rect(Rect2(400, 40, 70, 30), Palette.GAIN))
	stage.add_child(wheel)
	var bits := BinaryBits.new()
	stage.add_child(bits)
	var gpu := true
	_loops.append(func() -> void:
		var o := wheel.global_position
		var src := PackedVector2Array()
		for i in 40:
			src.append(o + centre + Vector2(-120 + (i % 8) * 10, -30 + (i / 8) * 12))
		bits.use_cpu_fallback = not gpu
		gpu = not gpu
		bits.burst(src, o + Vector2(435, 55), Palette.CELL_PINK, o + centre, 150.0, 3))
	_label("GPU particles (odd loops) / CPU fallback (even): bits fly round the rim into HP", Vector2(560, 560), 13, SUB, Palette.body())
	# decrypted holo over its scrim
	_rule(76, 1100, 1576)
	_label("DECRYPTED HOLO  /  CORP PAPER", Vector2(1100, 84), 22, TXT)
	_label("WHAT THE CELL STOLE", Vector2(1100, 113), 14, Palette.CELL_PINK)
	var scrim_box := Control.new()
	scrim_box.position = Vector2(1100, 140)
	scrim_box.size = Vector2(476, 260)
	scrim_box.clip_contents = true
	scrim_box.draw.connect(func() -> void:
		_facets(scrim_box, Rect2(Vector2.ZERO, scrim_box.size), 33, Palette.CORP_SOLACE)
		scrim_box.draw_rect(Rect2(Vector2.ZERO, scrim_box.size), Palette.HOLO_SCRIM))
	stage.add_child(scrim_box)
	var holo := DecryptedHoloPanel.new()
	holo.scrim = false
	holo.position = Vector2(20, 20)
	holo.size = Vector2(436, 220)
	scrim_box.add_child(holo)
	for i in 3:
		var l := Label.new()
		l.text = ["SITE FILE // THE RACK", "THREAT INTEL: 2 turrets, 1 ICE lock", "Garrison rotates at 02:00"][i]
		l.add_theme_font_override(&"font", Palette.mono())
		l.add_theme_font_size_override(&"font_size", 16 if i > 0 else 20)
		l.add_theme_color_override(&"font_color", Palette.CORP_SOLACE.lightened(0.5))
		l.position = Vector2(18, 64 + i * 32)
		holo.content.add_child(l)
	var paper := CorpPaperPanel.new()
	paper.position = Vector2(1120, 420)
	paper.size = Vector2(430, 250)
	paper.rotation_degrees = -1.5
	stage.add_child(paper)
	paper.add_field("WORK ORDER", "RAID-0412")
	paper.add_field("TARGET", "CELL safehouse, sector 7")
	paper.add_field("ASSETS", "2 drones, 1 enforcer team")
	# 3D toon + ink
	_rule(600, 24, 1060)
	_label("CEL / TOON + INK (3D)", Vector2(24, 608), 22, TXT)
	_label("WORLD: 3 bands, tone jitter, ink hull, light spill, haze", Vector2(24, 637), 14, Palette.CELL_PINK)
	var svc := SubViewportContainer.new()
	svc.position = Vector2(24, 660)
	svc.size = Vector2(1036, 230)
	svc.stretch = true
	stage.add_child(svc)
	var vp := SubViewport.new()
	vp.size = Vector2i(1036, 230)
	vp.own_world_3d = true
	vp.transparent_bg = false
	svc.add_child(vp)
	_build_toon_scene(vp)


func _build_toon_scene(vp: SubViewport) -> void:
	var env := WorldEnvironment.new()
	var e := Environment.new()
	e.background_mode = Environment.BG_COLOR
	e.background_color = Palette.NIGHT_SKY
	e.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	e.ambient_light_color = Palette.NIGHT_BLOCK_LIT
	e.ambient_light_energy = 0.6
	e.glow_enabled = true
	env.environment = e
	vp.add_child(env)
	var cam := Camera3D.new()
	cam.projection = Camera3D.PROJECTION_ORTHOGONAL
	cam.size = 7.5
	cam.position = Vector3(14, 12, 14)
	vp.add_child(cam)
	cam.look_at(Vector3(-1.5, 1.5, 0.5))
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-50, -30, 0)
	sun.light_color = Palette.NET_CYAN.lerp(Palette.TEXT_HI, 0.6)
	sun.light_energy = 0.9
	vp.add_child(sun)
	var spills := [{"position": Vector3(-1.5, 2.0, 2.2), "radius": 6.0, "color": Palette.CELL_PINK, "intensity": 1.6},
		{"position": Vector3(4.0, 1.0, -1.0), "radius": 5.0, "color": Palette.NET_CYAN, "intensity": 1.2}]
	var tones := [Palette.NIGHT_BLOCK_LIT, Palette.DESK_METAL, Palette.NEON_VIOLET.darkened(0.6), Palette.CORP_HALCYON.darkened(0.5)]
	var ground := MeshInstance3D.new()
	var pm := PlaneMesh.new()
	pm.size = Vector2(40, 40)
	ground.mesh = pm
	var gm := ToonInkMaterial.make(Palette.NIGHT_STREET.lightened(0.15), 0.0)
	ToonInkMaterial.set_spill(gm, spills)
	ground.material_override = gm
	vp.add_child(ground)
	for i in 14:
		var b := MeshInstance3D.new()
		var h := 1.0 + KitNoise.h01(4, i) * 5.0
		if i % 3 == 0:
			var pr := PrismMesh.new()
			pr.size = Vector3(1.6, h, 1.6)
			b.mesh = pr
		else:
			var bx := BoxMesh.new()
			bx.size = Vector3(1.4 + KitNoise.h01(5, i), h, 1.4 + KitNoise.h01(6, i))
			b.mesh = bx
		b.position = Vector3((i % 7) * 2.6 - 8.0, h * 0.5, (i / 7) * 3.2 - 1.6 + KitNoise.h11(7, i))
		var m := ToonInkMaterial.make(tones[i % tones.size()])
		ToonInkMaterial.set_spill(m, spills)
		b.material_override = m
		vp.add_child(b)
	var sign := MeshInstance3D.new()
	var sb := BoxMesh.new()
	sb.size = Vector3(0.3, 1.6, 1.2)
	sign.mesh = sb
	sign.position = Vector3(-1.5, 2.0, 2.2)
	var sm := StandardMaterial3D.new()
	sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	sm.albedo_color = Palette.CELL_PINK.lightened(0.3)
	sign.material_override = sm
	vp.add_child(sign)
