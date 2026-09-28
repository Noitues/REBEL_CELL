class_name DripButton
extends Button
## Words in dripping marker (the Cell's voice) that still press like a button: no box,
## no circle, just the tag. Drips hang from chosen letters (`drips`), attached to the
## letter's bottom edge: thick where they leave the letter, thin through the middle, a
## round raindrop at the end. An optional key hint sits underneath in system mono.
## Hover/focus brighten the paint and add a halo so pad and mouse players see it.

## Hot pink of the combat concepts (DECK & TONEARM).
const DRIP_PINK := Color("#FF3DA8")
## Drip presets: long -> short, left to right.
const SEND_IT_DRIPS := [[0, 44, 0.3], [2, 28, 0.88], [6, 14, 0.5]]
const LEAVE_MODEM_DRIPS := [[0, 42, 0.25], [7, 26, 0.85], [10, 14, 0.2]]
## Key hint lettering under the tag (px at text scale 1.0).
const HINT_SIZE := 18
## The white outline round drip lettering (px each side) and its opacity.
const OUTLINE_PX := 2.0
const OUTLINE_ALPHA := 0.95
## Hover halo: HALO_COPIES faint copies jittered by the `drip_halo` motion amplitude (px).
const HALO_MOTION := &"drip_halo"
const HALO_COPIES := 6
const HALO_ALPHA := 0.12

var tag_text: String = ""
var key_hint: String = ""
var paint: Color = DRIP_PINK
var font_size: int = 44
## Each drip: [letter index, length (px at size 44, scales with size), anchor 0-1 across
## the letter's width].
var drips: Array = []
var _hot: bool = false
## Press motion (Animation pass ANIM-2): the lettering squashes (vertical scale; the width
## grows to keep the paint's volume) and the drips run `drip_run` px further.
var squash: float = 1.0
var drip_run: float = 0.0
var _press_tween: Tween = null
## Animation pass ANIM-6 (ANIMATION_HANDOFF 4.22): the drips grow from the letters the first
## time a tag appears this session (`drip_grow`; 0 = just a bead at the letter, 1 = full),
## then hold. Hover / focus: one halo pulse (`drip_halo`: the jitter reaches out and back),
## then the steady halo. Nothing loops.
var grow: float = 1.0
var halo_pulse: float = 1.0
var _grow_tween: Tween = null
var _halo_tween: Tween = null
## Tags that have grown this session (a tag grows once; a rebuilt page doesn't regrow it).
static var _grown: Dictionary = {}
## ANIM-R1 C7: SEND IT carries a drawn "▶▶" mark (by its key hint) that pulses gently
## (`send_it_ready`) while all RAM is spent. Its height (share of the hint's), width of one
## arrow (share of the hint's height) and gap to the hint (px).
var glyph: bool = false
var ready_pulse: float = 1.0
var _ready_on: bool = false
var _ready_tween: Tween = null
const GLYPH_H := 0.9
const GLYPH_W := 0.5
const GLYPH_GAP := 6.0


## Forgets which tags have grown (the motion lab replays the growth).
static func reset_growth() -> void:
	_grown.clear()


## Grows the drips now if this tag has not grown this session.
func grow_in() -> void:
	if _grown.has(tag_text) or not is_visible_in_tree():
		return
	_grown[tag_text] = true
	if not Motion.live(&"drip_grow"):
		return
	var e := Motion.entry(&"drip_grow")
	grow = 0.0
	_grow_tween = create_tween()
	_grow_tween.tween_method(func(v: float) -> void:
		grow = v
		queue_redraw(), 0.0, 1.0, Motion.seconds(&"drip_grow")).set_delay(Motion.delay_of(&"drip_grow")).set_ease(e.ease).set_trans(e.trans)


## Ends the growth and the halo pulse at once.
func settle_motion() -> void:
	for tw in [_grow_tween, _halo_tween]:
		if tw != null and (tw as Tween).is_valid():
			(tw as Tween).kill()
	grow = 1.0
	halo_pulse = 1.0
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_READY or (what == NOTIFICATION_VISIBILITY_CHANGED and is_inside_tree()):
		grow_in.call_deferred()


func _set_hot(on: bool) -> void:
	if on and not _hot and Motion.live(HALO_MOTION):
		if _halo_tween != null and _halo_tween.is_valid():
			_halo_tween.kill()
		var e := Motion.entry(HALO_MOTION)
		halo_pulse = 0.0
		_halo_tween = create_tween()
		_halo_tween.tween_method(func(v: float) -> void:
			halo_pulse = v
			queue_redraw(), 0.0, 1.0, Motion.seconds(HALO_MOTION)).set_ease(e.ease).set_trans(e.trans)
	_hot = on
	queue_redraw()


## The press: the lettering squashes to `send_it_press`'s amplitude and springs back,
## the drips run `send_it_drips` px and draw back. Nothing under reduce effects.
func press_motion() -> void:
	if _press_tween != null and _press_tween.is_valid():
		_press_tween.kill()
	squash = 1.0
	drip_run = 0.0
	if not Motion.live(&"send_it_press") or not is_inside_tree():
		queue_redraw()
		return
	var pe := Motion.entry(&"send_it_press")
	var de := Motion.entry(&"send_it_drips")
	var d := Motion.seconds(&"send_it_press")
	var tw := create_tween()
	tw.tween_method(_set_squash, 1.0, Motion.amplitude(&"send_it_press"), d * Motion.POP_GROW_SHARE).set_ease(Tween.EASE_OUT)
	tw.tween_method(_set_squash, Motion.amplitude(&"send_it_press"), 1.0, d * (1.0 - Motion.POP_GROW_SHARE)).set_ease(pe.ease).set_trans(pe.trans)
	if Motion.live(&"send_it_drips"):
		var dd := Motion.seconds(&"send_it_drips")
		var out_share := clampf(Motion.amplitude(&"send_it_drips_share"), 0.0, 1.0)
		tw.parallel().tween_method(_set_run, 0.0, Motion.amplitude(&"send_it_drips"), dd * out_share).set_ease(de.ease).set_trans(de.trans)
		tw.tween_method(_set_run, Motion.amplitude(&"send_it_drips"), 0.0, dd * (1.0 - out_share)).set_ease(Tween.EASE_IN_OUT)
	_press_tween = tw


func _set_squash(v: float) -> void:
	squash = v
	queue_redraw()


func _set_run(v: float) -> void:
	drip_run = v
	queue_redraw()


func _init(p_text: String = "SEND IT", p_hint: String = "", p_color: Color = DRIP_PINK, p_size: int = 44, p_drips: Array = []) -> void:
	tag_text = p_text
	key_hint = p_hint
	paint = p_color
	font_size = p_size
	drips = p_drips
	flat = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	_fit_size()
	mouse_entered.connect(_set_hot.bind(true))
	mouse_exited.connect(_set_hot.bind(false))
	focus_entered.connect(_set_hot.bind(true))
	focus_exited.connect(_set_hot.bind(false))


func _fit_size() -> void:
	var longest := 0.0
	for d in drips:
		longest = maxf(longest, float(d[1]))
	var w := Palette.marker().get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	custom_minimum_size = Vector2(w + 24, font_size * 1.05 + longest * font_size / 44.0 + 14 + (HINT_SIZE * Settings.text_scale + 6.0 if key_hint != "" else 0.0))


## Replaces the lettering (ANIM-R3 A6h: the fight's next-step action is named by the
## netrun); the button refits.
func set_tag_text(text: String) -> void:
	if text == tag_text:
		return
	tag_text = text
	_fit_size()
	queue_redraw()


## Replaces the key hint under the tag (rebinds, pad glyphs).
func set_key_hint(hint: String) -> void:
	if hint != key_hint:
		key_hint = hint
		queue_redraw()


## Draws `text` with drips on any CanvasItem at baseline `base` (shared with views that
## paint the lettering themselves). A thin white outline runs round the letters and the
## drips so the pink reads over the bright city.
static func draw_drip_text(ci: CanvasItem, base: Vector2, raw_text: String, size: int, col: Color, p_drips: Array, shadow: bool = true, outline: bool = true) -> void:
	# Drawn words translate (H24: SEND IT stayed English in the scrambled storyboard).
	var text := String(TranslationServer.translate(raw_text))
	var f := Palette.marker()
	if shadow:
		ci.draw_string(f, base + Vector2(3, 3), text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, Color(0, 0, 0, 0.7))
	var scale := size / 44.0
	var edge := OUTLINE_PX * (1.0 if size >= 30 else 0.75)
	var drops := []
	for d in p_drips:
		var idx: int = d[0]
		if idx < 0 or idx >= text.length():
			continue
		var x0 := f.get_string_size(text.substr(0, idx), HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		var cw := f.get_string_size(text[idx], HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		var x := base.x + x0 + cw * float(d[2])
		# Start inside the letter's bottom stroke so the drip is attached to it.
		drops.append([Vector2(x, base.y - size * 0.12), float(d[1]) * scale + size * 0.12, maxf(3.5, 9.5 * scale)])
	if outline:
		var white := Color(1, 1, 1, OUTLINE_ALPHA)
		# Stamped round the letters (12 directions), so it works with any font import.
		for k in 12:
			var o := Vector2(cos(TAU * k / 12.0), sin(TAU * k / 12.0)) * edge
			ci.draw_string(f, base + o, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, white)
		for dr in drops:
			_drip(ci, dr[0] + Vector2(0, -edge * 0.5), dr[1] + edge * 1.5, dr[2] + edge * 2.0, white)
	ci.draw_string(f, base, text, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)
	for dr in drops:
		_drip(ci, dr[0], dr[1], dr[2], col)


## One drip: thick where it leaves the letter, a thin neck, a teardrop at the end (point
## up into the neck, round at the bottom). A drip shorter than the teardrop alone is just
## the teardrop, hanging a little below the letter with its point touching it.
static func _drip(ci: CanvasItem, top: Vector2, length: float, w: float, col: Color) -> void:
	var drop_w := w * 0.85
	var drop_h := w * 2.1
	if length < drop_h * 1.15:
		# Short: flare, then the teardrop just below the letter.
		ci.draw_colored_polygon(PackedVector2Array([top + Vector2(-w * 0.7, -w * 0.2), top + Vector2(w * 0.7, -w * 0.2), top + Vector2(w * 0.25, w * 0.5), top + Vector2(-w * 0.25, w * 0.5)]), col)
		_teardrop(ci, top + Vector2(0, w * 0.3), drop_w, drop_h, col)
		return
	var neck := w * 0.36
	var neck_len := length - drop_h * 0.8
	var pts := PackedVector2Array()
	var steps := 10
	for k in steps + 1:
		var t := float(k) / steps
		# Wide at the top, pinching to the neck by 40%, holding thin to the drop.
		var hw := lerpf(w * 0.5, neck * 0.5, smoothstep(0.0, 0.4, t))
		pts.append(top + Vector2(hw, t * neck_len))
	for k in range(steps, -1, -1):
		var t := float(k) / steps
		var hw := lerpf(w * 0.5, neck * 0.5, smoothstep(0.0, 0.4, t))
		pts.append(top + Vector2(-hw, t * neck_len))
	# Flare into the letter at the top so the join reads as paint, not a stick.
	ci.draw_colored_polygon(PackedVector2Array([top + Vector2(-w * 0.9, -w * 0.2), top + Vector2(w * 0.9, -w * 0.2), top + Vector2(w * 0.5, w * 0.6), top + Vector2(-w * 0.5, w * 0.6)]), col)
	ci.draw_colored_polygon(pts, col)
	_teardrop(ci, top + Vector2(0, neck_len - drop_h * 0.2), drop_w, drop_h, col)


## A teardrop with its point at `tip`, `w` wide and `h` tall, with a small highlight.
static func _teardrop(ci: CanvasItem, tip: Vector2, w: float, h: float, col: Color) -> void:
	var pts := PackedVector2Array()
	for k in 25:
		var t := TAU * k / 24.0
		# Point at t = 0 (top), round belly at the bottom.
		var x := sin(t) * pow(sin(t * 0.5), 1.4) * w * 0.62
		var y := (1.0 - cos(t)) * 0.5 * h
		pts.append(tip + Vector2(x, y))
	ci.draw_colored_polygon(pts, col)
	ci.draw_circle(tip + Vector2(-w * 0.18, h * 0.62), w * 0.12, Color(1, 1, 1, 0.35))


## Automatic drips for any text: up to `count` letters with a stroke at the baseline,
## spread across the word, long -> short left to right (deterministic from the text).
static func auto_drips(text: String, count: int = 3) -> Array:
	var candidates: Array[int] = []
	for i in text.length():
		if text[i] in "ABDEHIKLMNRSTUXZ_":
			candidates.append(i)
	if candidates.is_empty():
		return []
	var picks: Array[int] = []
	var n := mini(count, candidates.size())
	for k in n:
		var at := candidates[int(round(float(k) * (candidates.size() - 1) / maxf(1.0, n - 1)))] if n > 1 else candidates[0]
		if not picks.has(at):
			picks.append(at)
	var lengths := [44, 28, 12, 20, 34]
	var out := []
	for k in picks.size():
		var ch := text[picks[k]]
		var anchor := 0.3
		if ch in "NMH":
			anchor = 0.88
		elif ch in "TI":
			anchor = 0.5
		out.append([picks[k], lengths[k % lengths.size()], anchor])
	return out


## The lettering as shown (translated) and the font size it is drawn at: the button is
## laid out for the source word, so a longer translation shrinks to that width instead of
## running off the screen's edge (ANIM-R1: SEND IT was cut under pseudolocalisation).
func shown_lettering() -> Array:
	var shown := String(TranslationServer.translate(tag_text))
	var f := Palette.marker()
	var room := f.get_string_size(tag_text, HORIZONTAL_ALIGNMENT_LEFT, -1, font_size).x
	var fs := font_size
	var floor_size := maxi(1, roundi(font_size * FIT_MIN_SHARE))
	while fs > floor_size and f.get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x > room:
		fs -= 1
	return [shown, fs]


## The smallest a translated lettering shrinks to, as a share of its font size.
const FIT_MIN_SHARE := 0.5


func _draw() -> void:
	var lettering := shown_lettering()
	var shown: String = lettering[0]
	var fs: int = lettering[1]
	var col := paint if not disabled else Color(paint, 0.35)
	if _hot and not disabled:
		col = paint.lightened(0.2)
	var base := Vector2(12, font_size * 1.0)
	if _hot and not disabled:
		# A fixed jitter pattern (x -3..2, y -2..2 steps), scaled so its x reach is the
		# halo amplitude in px.
		# The hover pulse: the jitter reaches out to twice its reach and back once.
		var swell := 1.0 + sin(PI * clampf(halo_pulse, 0.0, 1.0))
		var j := Motion.amplitude(HALO_MOTION) / (HALO_COPIES * 0.5) * swell
		for k in HALO_COPIES:
			var o := Vector2(k - HALO_COPIES * 0.5, (k * 7) % 5 - 2) * j
			draw_string(Palette.marker(), base + o, shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, Color(Palette.CELL_ACID, HALO_ALPHA * swell))
	if squash != 1.0:
		# Squash about the baseline: shorter and a little wider.
		var sx := 1.0 / maxf(0.01, squash)
		draw_set_transform(Vector2(base.x * (1.0 - sx), base.y * (1.0 - squash)), 0.0, Vector2(sx, squash))
	var run := drips
	if drip_run != 0.0 or grow < 1.0:
		run = []
		for dr in drips:
			run.append([dr[0], (float(dr[1]) + drip_run * 44.0 / font_size) * grow, dr[2]])
	DripButton.draw_drip_text(self, base, tag_text, fs, col, run)
	draw_set_transform(Vector2.ZERO)
	if key_hint != "":
		# The key sits centred under the lettering, big enough to find (H22: "[X]" at 13 px in
		# the corner was barely visible on the most important button).
		var hs := roundi(HINT_SIZE * Settings.text_scale)
		var tw := Palette.marker().get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		var hw := Palette.mono().get_string_size(key_hint, HORIZONTAL_ALIGNMENT_LEFT, -1, hs).x
		var hp := Vector2(12 + (tw - hw) * 0.5, size.y - 6)
		draw_rect(Rect2(hp + Vector2(-6, -hs), Vector2(hw + 12, hs + 6)), Color(Palette.NIGHT_SKY, 0.8))
		draw_string(Palette.mono(), hp, key_hint, HORIZONTAL_ALIGNMENT_LEFT, -1, hs, Palette.PAPER)
		if glyph:
			_draw_glyph(Vector2(hp.x - 6.0 - GLYPH_GAP, hp.y - hs * 0.5 + 3.0), hs, col)
	elif glyph:
		var hs := roundi(HINT_SIZE * Settings.text_scale)
		var tw := Palette.marker().get_string_size(shown, HORIZONTAL_ALIGNMENT_LEFT, -1, fs).x
		_draw_glyph(Vector2(12 + tw * 0.5 + hs * GLYPH_W, size.y - 6 - hs * 0.5), hs, col)


## ANIM-R1 C7: a drawn "▶▶" (the end-turn mark, readable in any language), right edge at
## `right` (vertical middle there), `h` px tall, scaled by the ready pulse.
func _draw_glyph(right: Vector2, h: float, col: Color) -> void:
	var s := h * GLYPH_H * ready_pulse
	var w := s * GLYPH_W / GLYPH_H
	for k in 2:
		var x1 := right.x - k * w
		var tri := PackedVector2Array([Vector2(x1, right.y), Vector2(x1 - w, right.y - s * 0.5), Vector2(x1 - w, right.y + s * 0.5)])
		draw_colored_polygon(tri, Color(1, 1, 1, OUTLINE_ALPHA))
		draw_colored_polygon(PackedVector2Array([tri[0] + Vector2(-OUTLINE_PX, 0), tri[1] + Vector2(OUTLINE_PX * 0.5, OUTLINE_PX), tri[2] + Vector2(OUTLINE_PX * 0.5, -OUTLINE_PX)]), col)


## ANIM-R1 C7: the end-turn mark pulses gently while there's nothing left to spend (`on`);
## off under reduce effects (the mark holds still).
func set_ready(on: bool) -> void:
	if on == _ready_on:
		return
	_ready_on = on
	Motion._settle(self, ^"ready_pulse")
	_ready_tween = null
	ready_pulse = 1.0
	if on and is_inside_tree():
		_ready_tween = Motion.loop_pulse(self, ^"ready_pulse", &"send_it_ready")
	queue_redraw()


## True while the ready pulse runs.
func ready_pulsing() -> bool:
	return _ready_tween != null and _ready_tween.is_valid()
