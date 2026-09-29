class_name ModemSign
extends Control
## The Modem's vertical neon sign (left edge of the shop): a rounded pink border, a dense
## printed-circuit board inside it with traces running in from the border, MODEM stacked
## in the drawn cybernetic face (pink) and CYBER SHOP under it (cyan), both sprouting
## traces, and BUY / SHRED sticky notes overlapping the bottom-right corner (the Modem
## sells and removes cards; nothing is sold back, H20). Decoration.

const PINK := Palette.CELL_PINK
## The sticky notes' lettering (px; a longer translation shrinks to fit).
const STICKY_FONT := 24
## The sticky notes: what the Modem does (keys, translated when drawn).
const NOTES: Array[String] = ["BUY", "SHRED"] # TR
## ANIM-R6 B11: a sticky note's width and its glyph's radius (px), the sign's bag (its radius,
## its top inside the border, its glow's size and alpha), and the bag's tube id (warm-up).
const STICKY_W := 104.0
const STICKY_GLYPH := 12.0
const BAG_R := 22.0
const BAG_TOP := 22.0
const GLOW_GROW := 1.25
const GLOW_ALPHA := 0.35
const TUBE_BAG := 99
## ANIM-R6 B11: the sign's glyph (a shop bag) and each sticky note's (a cart for BUY, a
## shredder for SHRED), readable whatever the language.
const SIGN_GLYPH := StatIcon.SHOP
const NOTE_GLYPHS: Array[StringName] = [StatIcon.CART, StatIcon.SHRED]
## The sign's words (keys; H24 S3: drawn in the player's language, in the cybernetic face
## when it has every letter, else in the display font).
const WORD_MODEM := "MODEM" # TR
const WORD_CYBER := "CYBER" # TR
const WORD_SHOP := "SHOP" # TR


## Animation pass ANIM-6 (ANIMATION_HANDOFF 4.19): on entering the Modem the neon tubes warm
## up (`modem_sign_warmup`: each tube flickers on at its own, hash-picked moments, then
## holds) and the circuit traces light up one after another with CYBER SHOP last
## (`modem_trace`). 1 = lit (the rest state; reduce effects and headless stay there).
var warm: float = 1.0
var trace: float = 1.0
var _tweens: Array[Tween] = []
## Flicker steps across the warm-up, and the alpha of an unlit tube.
const WARM_STEPS := 14
const TUBE_OFF_ALPHA := 0.12
## ANIM-R3 A7 / ANIM-R4 C5: every tube strikes within `modem_sign_strike` of the warm-up,
## flickers for `modem_sign_flicker` after it (lit at a flicker step with this chance: a
## drawing threshold, not motion), then holds.
const FLICKER_ON := 0.6
## Tube ids for the warm-up hash: the border, then each letter.
const TUBE_BORDER := 0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(210, 540)
	MotionSkip.register_passive(self)  # ANIM-R6 D7: the warm-up ends with any press that ends a motion


## MotionSkip (ANIM-R6 D7): the sign is warming up.
func motion_running() -> bool:
	return warming()


## MotionSkip (ANIM-R6 D7): the sign lit at once.
func complete_motion() -> void:
	settle()


## Warms the sign up from dark (entering the Modem).
func warm_up() -> void:
	settle()
	if Motion.live(&"modem_sign_warmup"):
		var e := Motion.entry(&"modem_sign_warmup")
		warm = 0.0
		var tw := create_tween()
		tw.tween_method(func(v: float) -> void:
			warm = v
			queue_redraw(), 0.0, 1.0, Motion.seconds(&"modem_sign_warmup")).set_delay(Motion.delay_of(&"modem_sign_warmup")).set_ease(e.ease).set_trans(e.trans)
		_tweens.append(tw)
	if Motion.live(&"modem_trace"):
		var te := Motion.entry(&"modem_trace")
		trace = 0.0
		var tt := create_tween()
		tt.tween_method(func(v: float) -> void:
			trace = v
			queue_redraw(), 0.0, 1.0, Motion.seconds(&"modem_trace")).set_delay(Motion.delay_of(&"modem_trace")).set_ease(te.ease).set_trans(te.trans)
		_tweens.append(tt)
	queue_redraw()


## Ends the warm-up at once (lit).
func settle() -> void:
	for tw in _tweens:
		if tw != null and tw.is_valid():
			tw.kill()
	_tweens.clear()
	warm = 1.0
	trace = 1.0
	queue_redraw()


## True while the sign is still warming up.
func warming() -> bool:
	return warm < 1.0 or trace < 1.0


## A tube's brightness now: lit once warm, else flickering on at hash-picked steps.
## ANIM-R3 A7: each tube strikes at its own hash-picked moment in the first
## strike_share() of the warm-up, flickers for flicker_share(), then holds lit, so the sign is
## whole well before the warm-up ends (a still mid-way showed one lit letter: it read as
## broken).
func tube(id: int) -> float:
	if warm >= 1.0:
		return 1.0
	var strike := float(absi(hash([id, 41])) % 1000) / 1000.0 * strike_share()
	if warm < strike:
		return TUBE_OFF_ALPHA
	if warm >= strike + flicker_share():
		return 1.0
	var step := floori(warm * WARM_STEPS)
	var h := float(absi(hash([id, step, 43])) % 1000) / 1000.0
	return 1.0 if h < FLICKER_ON else TUBE_OFF_ALPHA


## `col` at brightness `k` (1 = lit; an unlit tube is the colour darkened, so every glow
## layer the painters build from it dims too).
static func _tube_color(col: Color, k: float) -> Color:
	return col if k >= 1.0 else col.darkened(1.0 - k)


func _draw() -> void:
	var r := Rect2(Vector2(6, 6), Vector2(size.x - 44, size.y - 40))
	_rounded_border(r, 26, _tube_color(PINK, tube(TUBE_BORDER)))
	_board_traces(r.grow(-12), PINK, 80)
	_border_traces(r, PINK)
	# ANIM-R6 B11: a shop bag in neon at the head of the sign (the sign said what it was in
	# words only: under a language the player can't read it was a column of letters).
	var bag_at := r.position + Vector2(r.size.x * 0.5, BAG_TOP + BAG_R)
	var bag_col := _tube_color(Palette.CELL_ACID, tube(TUBE_BAG))
	StatIcon.draw(self, bag_at, BAG_R * GLOW_GROW, SIGN_GLYPH, Color(bag_col, GLOW_ALPHA))
	StatIcon.draw(self, bag_at, BAG_R, SIGN_GLYPH, bag_col)
	# The name stacked letter by letter down the sign (as many rows as it has letters), under
	# the bag.
	var name_word := tr(WORD_MODEM).to_upper()
	var n := maxi(1, name_word.length())
	var head := BAG_TOP + BAG_R * 2.0
	var step := (r.size.y - 160.0 - head) / float(maxi(5, n))
	var u := minf(11.0, step / 8.2)
	var cyber := CyberType.can_draw(name_word)
	for i in name_word.length():
		var at := r.position + Vector2((r.size.x - 4.0 * u) * 0.5, head + 10 + i * step)
		var lit := _tube_color(PINK, tube(i + 1))
		if cyber:
			CyberType.draw_text(self, at, name_word[i], u, lit, 3.2, i == 0 or i == name_word.length() - 1, 0.7)
		else:
			_plain(Rect2(r.position.x, at.y, r.size.x, step), name_word[i], lit)
	var cu := 4.4
	for k in 2:
		var word: String = tr([WORD_CYBER, WORD_SHOP][k]).to_upper()
		var row := Rect2(r.position.x + 6.0, r.position.y + r.size.y - 118 + k * 42, r.size.x - 12.0, 6.0 * cu)
		# CYBER SHOP lights last, as the traces reach it.
		var cyan := _tube_color(Palette.NET_CYAN, lerpf(TUBE_OFF_ALPHA, 1.0, clampf((trace - 0.6 - k * 0.2) / 0.2, 0.0, 1.0)) if trace < 1.0 else 1.0)
		if CyberType.can_draw(word) and CyberType.width(word, cu) <= row.size.x:
			CyberType.draw_text(self, Vector2(r.position.x + (r.size.x - CyberType.width(word, cu)) * 0.5, row.position.y), word, cu, cyan, 2.0, false, 0.8)
		else:
			_plain(row, word, cyan)
	_sticky(r.end + Vector2(-8, -54), tr(NOTES[0]), Palette.NOTE_YELLOW, 0.1, NOTE_GLYPHS[0])
	_sticky(r.end + Vector2(14, 4), tr(NOTES[1]), Palette.STICKER_PINK, -0.07, NOTE_GLYPHS[1])


## `text` in the display font, centred in `box` and as large as fits it (a translated sign
## word the cybernetic face has no letters for).
func _plain(box: Rect2, text: String, col: Color) -> void:
	var f := Palette.display()
	var fs := maxi(8, roundi(box.size.y * 0.9))
	while fs > 8 and f.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > box.size.x:
		fs -= 1
	var y := box.position.y + (box.size.y + f.get_ascent(fs) - f.get_descent(fs)) * 0.5
	draw_string(f, Vector2(box.position.x, y), text, HORIZONTAL_ALIGNMENT_CENTER, box.size.x, fs, col)


func _rounded_border(r: Rect2, radius: float, col: Color) -> void:
	var pts := PackedVector2Array()
	var corners := [[Vector2(r.end.x - radius, r.position.y + radius), -PI * 0.5], [Vector2(r.end.x - radius, r.end.y - radius), 0.0],
		[Vector2(r.position.x + radius, r.end.y - radius), PI * 0.5], [Vector2(r.position.x + radius, r.position.y + radius), PI]]
	for cr in corners:
		for k in 9:
			var a: float = cr[1] + PI * 0.5 * k / 8.0
			pts.append(cr[0] + Vector2(cos(a), sin(a)) * radius)
	draw_colored_polygon(pts, Color(0.02, 0.02, 0.05, 0.94))
	pts.append(pts[0])
	draw_polyline(pts, Color(col, 0.12), 20.0, true)
	draw_polyline(pts, Color(col, 0.3), 9.0, true)
	draw_polyline(pts, col.lightened(0.35), 3.2, true)


func _board_traces(r: Rect2, col: Color, count: int) -> void:
	var dirs := [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1), Vector2(1, 1).normalized(), Vector2(-1, 1).normalized(), Vector2(1, -1).normalized(), Vector2(-1, -1).normalized()]
	for n in count:
		# The traces light one after another as `trace` runs (all lit at 1).
		if trace < 1.0 and float(n) / count >= trace:
			continue
		var h := absi(hash([n, 17]))
		var p := r.position + Vector2(float(h % 1000) / 1000.0 * r.size.x, float((h / 1000) % 1000) / 1000.0 * r.size.y)
		var pts := PackedVector2Array([p])
		var d: Vector2 = dirs[(h / 7) % 4]
		for seg in 2 + (h / 13) % 2:
			var q := (p + d * (8.0 + float((h / (17 + seg)) % 22))).clamp(r.position, r.end)
			pts.append(q)
			p = q
			d = dirs[4 + (h / (29 + seg)) % 4] if seg % 2 == 0 else dirs[(h / (31 + seg)) % 4]
		draw_polyline(pts, Color(col, 0.28), 1.4, true)
		if (h / 3) % 3 == 0:
			draw_circle(pts[0], 2.2, Color(col, 0.35))
		var end := pts[pts.size() - 1]
		if (h / 5) % 2 == 0:
			draw_circle(end, 3.2, Color(col, 0.55))
			draw_circle(end, 1.3, Palette.NIGHT_SKY)
		else:
			draw_rect(Rect2(end - Vector2(2.5, 2.5), Vector2(5, 5)), Color(col, 0.45))


func _border_traces(r: Rect2, col: Color) -> void:
	for side in [-1.0, 1.0]:
		var n := int((r.size.y - 80.0) / 34.0)
		for q in n:
			if trace < 1.0 and float(q) / maxf(1.0, n) >= trace:
				continue
			var y := r.position.y + 44.0 + q * 34.0
			var a := Vector2(r.position.x if side < 0 else r.end.x, y)
			var b := a + Vector2(-side * (10.0 + (q % 3) * 7.0), 0)
			var c := b + Vector2(-side, (1.0 if q % 2 == 0 else -1.0)).normalized() * (8.0 + (q % 4) * 4.0)
			var pts := PackedVector2Array([a, b, c])
			draw_polyline(pts, Color(col, 0.2), 6.0, true)
			draw_polyline(pts, Color(col, 0.85), 1.8, true)
			draw_circle(c, 4.0, Color(col, 0.9))
			draw_circle(c, 1.6, Palette.NIGHT_SKY)


## ANIM-R6 B11: a sticky note with its verb's glyph (`glyph`: a StatIcon kind) before its
## word, so the note reads with the words scrambled.
func _sticky(at: Vector2, text: String, paper: Color, tilt: float, glyph: StringName = &"") -> void:
	draw_set_transform(at, tilt, Vector2.ONE)
	draw_rect(Rect2(Vector2(-STICKY_W * 0.5 + 4, -26 + 5), Vector2(STICKY_W, 52)), Palette.SHADOW)
	draw_rect(Rect2(Vector2(-STICKY_W * 0.5, -26), Vector2(STICKY_W, 52)), paper)
	draw_rect(Rect2(Vector2(-18, -31), Vector2(36, 11)), Palette.NOTE_TAPE)
	var left := -STICKY_W * 0.5
	if glyph != &"":
		StatIcon.draw(self, Vector2(left + 4.0 + STICKY_GLYPH, 0.0), STICKY_GLYPH, glyph, Palette.INK)
		left += STICKY_GLYPH * 2.0 + 6.0
	var room := STICKY_W * 0.5 - left - 4.0
	var fs := STICKY_FONT
	while fs > 8 and Palette.marker().get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	draw_string(Palette.marker(), Vector2(left, 10), text, HORIZONTAL_ALIGNMENT_CENTER, room, fs, Palette.INK)
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)


## The sign's words as drawn, in the player's language (tests).
func shown_words() -> PackedStringArray:
	return PackedStringArray([tr(WORD_MODEM), tr(WORD_CYBER), tr(WORD_SHOP), tr(NOTES[0]), tr(NOTES[1])])


## ANIM-R4 C5: each tube strikes within this share of the warm-up (`modem_sign_strike`).
static func strike_share() -> float:
	return clampf(Motion.amplitude(&"modem_sign_strike"), 0.0, 1.0)


## ANIM-R4 C5: a struck tube flickers for this share of the warm-up (`modem_sign_flicker`).
static func flicker_share() -> float:
	return clampf(Motion.amplitude(&"modem_sign_flicker"), 0.0, 1.0)
