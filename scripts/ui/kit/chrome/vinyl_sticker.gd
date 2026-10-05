class_name VinylSticker
extends Button
## ART-10 4C: a vinyl sticker word that presses like a button (ART_BIBLE v2 §1.2 "Vinyl
## sticker", §2.10, §4.13; round 33 `ui_kit.jpg`, `title_screen.jpg`, `abandon_dialog.jpg`):
## Anton lettering with an ink keyline and extrude, a white die-cut border, a vertical fill
## gradient with the rest gloss (0.22), one gloss sweep on hover. States: hover grows it
## (`sticker_hover`, 1.05) and sweeps the gloss, a press squashes it (`sticker_press`), focus
## is a lime die-cut halo (never brackets, §2.10), disabled is 80 % grey. Fills: PINK (the
## committing verb), YELLOW (the safe choice, screen titles), BLUE (OVERTHROW, with a red
## rebel fist for one letter), GLITCH (SIMULATE: the CORRUPTED glitch inside the letters,
## bursting twice a loop, `title_glitch_burst`). A sticker is a word that never changes; the
## scene decides what a press means. Runtime-drawn until Group 1B's sticker material lands
## (Chrome is the seam). View only.

enum Fill { PINK, YELLOW, BLUE, GLITCH, GREY }

const SHADER := preload("res://shaders/chrome/vinyl_sticker.gdshader")
## Motion entries: hover growth + gloss sweep, the press squash, the glitch bursts.
const HOVER_MOTION := &"sticker_hover"
const PRESS_MOTION := &"sticker_press"
const GLITCH_MOTION := &"title_glitch_burst"
## Geometry as shares of the lettering size (round 33 sticker_lib: keyline 5 px, extrude
## 7 px, die-cut 12 px at 144 px lettering, drawn thicker at menu sizes so they read).
const DIE_CUT := 0.17
const KEYLINE := 0.075
const EXTRUDE := 0.1
const HALO := 0.13
## Anton's cap height as a share of the font size (the lettering box).
const CAP_SHARE := 0.74
## The shadow under the die-cut (offset as a share of the size) and its alpha.
const SHADOW_SHARE := 0.07
const SHADOW_ALPHA := 0.55
## The die-cut's ink rim (px beyond the white) and the focus halo's ink rim.
const RIM_PX := 2.0
## Stickers scale as whole objects with the text (§5.6), up to this share.
const SCALE_MAX := 1.5
## Disabled: greyscale share (§4.13: disabled greyscale 80 %).
const DISABLED_GREY := 0.8
## The glitch: the light split at rest (px at size 44) and the burst's band offsets (shares
## of the size), and the frames of the 48-frame loop the bursts cover (round 33: 9-10, 27-28).
const SPLIT_SHARE := 0.045
const BURST_SHIFTS: Array[float] = [0.14, -0.1, 0.07, -0.16, 0.11]
const LOOP_FRAMES := 48.0
const BURSTS: Array[Vector2] = [Vector2(9, 11), Vector2(27, 29)]
## The fist pictogram in the letter slot (unit box: x 0..1, y 0..1 from the cap top).
const FIST_KNUCKLES := 4
const FIST_BODY := Rect2(0.06, 0.1, 0.88, 0.62)
const FIST_CUFF := Rect2(0.24, 0.72, 0.52, 0.28)
const FIST_THUMB := Rect2(0.1, 0.44, 0.56, 0.17)
const FIST_KNUCKLE_R := 0.115

var fill: int = Fill.PINK
## Lettering size at text scale 1.0 (px at 1280x720).
var base_size: float = 40.0
## Tilt in degrees (the sticker was slapped on, not placed).
var tilt: float = 0.0
## The letter index drawn as the red rebel fist (-1: none).
var fist_at: int = -1
## The label is already translated.
var pre_translated := false

var _mat: ShaderMaterial
var _hover_k: float = 0.0
var _sweep_tween: Tween = null
var _scale_tween: Tween = null
var _clock: float = 0.0


func _init(p_text: String = "", p_fill: int = Fill.PINK, p_size: float = 40.0, p_tilt: float = 0.0) -> void:
	text = p_text
	fill = p_fill
	base_size = p_size
	tilt = p_tilt
	flat = true
	clip_text = true
	focus_mode = Control.FOCUS_ALL
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	set_meta(UiFocus.META_NO_SCALE, true)  # it grows itself on hover / focus
	for box in [&"normal", &"hover", &"pressed", &"hover_pressed", &"disabled", &"focus"]:
		add_theme_stylebox_override(box, StyleBoxEmpty.new())
	for key in [&"font_color", &"font_hover_color", &"font_pressed_color", &"font_focus_color", &"font_hover_pressed_color", &"font_disabled_color"]:
		add_theme_color_override(key, Palette.AUTO)  # the sticker draws its own lettering
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	material = _mat
	KitState.track(self)
	mouse_entered.connect(_hot.bind(true))
	mouse_exited.connect(_hot.bind(false))
	focus_exited.connect(queue_redraw)
	button_down.connect(_press.bind(true))
	button_up.connect(_press.bind(false))
	_fit()


func _ready() -> void:
	Settings.changed.connect(_refit_later)
	resized.connect(_pivot)
	_pivot()
	set_process(fill == Fill.GLITCH)


func _exit_tree() -> void:
	if Settings.changed.is_connected(_refit_later):
		Settings.changed.disconnect(_refit_later)


## The state drawn now (KitState: idle, hover, focus, pressed, disabled, refused).
func state() -> StringName:
	return KitState.of(self)


## Flashes the refused state.
func refuse() -> void:
	KitState.refuse(self)


## The lettering as drawn (translated unless given).
func shown_text() -> String:
	return text if pre_translated else tr(text)


## Lettering size now (px): the base size grown with the text scale up to SCALE_MAX.
func letter_px() -> int:
	return roundi(base_size * clampf(Settings.text_scale, 1.0, SCALE_MAX))


func _pad() -> float:
	var s := float(letter_px())
	return s * (DIE_CUT + KEYLINE + HALO) + RIM_PX * 2.0


func _fit() -> void:
	var s := float(letter_px())
	var w := Chrome.sticker_font().get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, letter_px()).x
	custom_minimum_size = Vector2(ceilf(w + _pad() * 2.0 + s * EXTRUDE), ceilf(s * CAP_SHARE + _pad() * 2.0 + s * EXTRUDE))
	size = get_combined_minimum_size()
	_pivot()
	queue_redraw()


func _refit_later() -> void:
	_fit.call_deferred()


func _pivot() -> void:
	pivot_offset = size * 0.5
	rotation_degrees = tilt


## Re-measures (after a text or text-scale change).
func refit() -> void:
	_fit()


func set_label(t: String) -> void:
	if t != text:
		text = t
		_fit()


func _hot(on: bool) -> void:
	_grow(on or has_focus())
	if on and not disabled:
		_sweep()
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_FOCUS_ENTER:
		_grow(true)
	elif what == NOTIFICATION_FOCUS_EXIT:
		_grow(bool(get_meta(KitState.META_HOVER, false)))


## Hover / focus: the sticker grows to the `sticker_hover` amplitude (1.05) about its centre.
func _grow(on: bool) -> void:
	var to := Vector2.ONE * (Motion.amplitude(HOVER_MOTION) if on and not disabled else 1.0)
	if _scale_tween != null:
		_scale_tween.kill()
	_scale_tween = Motion.run(HOVER_MOTION, self, ^"scale", to)


## A press squashes it (`sticker_press`: x by 1 + amplitude / 2, y by 1 - amplitude); a
## release springs it back to its hover size.
func _press(down: bool) -> void:
	if disabled:
		return
	var a := Motion.amplitude(PRESS_MOTION)
	var hover := Motion.amplitude(HOVER_MOTION) if (has_focus() or bool(get_meta(KitState.META_HOVER, false))) else 1.0
	var to := Vector2(1.0 + a * 0.5, 1.0 - a) if down else Vector2.ONE * hover
	if _scale_tween != null:
		_scale_tween.kill()
	_scale_tween = Motion.run(PRESS_MOTION, self, ^"scale", to)


## One gloss sweep across the lettering (§4.13: hover = gloss sweep); none when the motion
## does not play.
func _sweep() -> void:
	if not Motion.live(HOVER_MOTION):
		return
	if _sweep_tween != null:
		_sweep_tween.kill()
	var w := size.x
	_mat.set_shader_parameter(&"sweep", -w * 0.3)
	_sweep_tween = create_tween()
	_sweep_tween.tween_method(func(x: float) -> void: _mat.set_shader_parameter(&"sweep", x), -w * 0.3, w * 1.3,
		Motion.seconds(HOVER_MOTION) * 3.0)
	_sweep_tween.tween_callback(func() -> void: _mat.set_shader_parameter(&"sweep", -10000.0))


func _process(delta: float) -> void:
	if fill != Fill.GLITCH or not Motion.live(GLITCH_MOTION):
		if _clock != 0.0:
			_clock = 0.0
			queue_redraw()
		return
	var was := bursting()
	_clock = fmod(_clock + delta, maxf(0.05, Motion.seconds(GLITCH_MOTION)))
	if bursting() != was:
		queue_redraw()


## True while the glitch bursts (frames 9-10 and 27-28 of its 48-frame loop).
func bursting() -> bool:
	if fill != Fill.GLITCH or not Motion.live(GLITCH_MOTION):
		return false
	var f := _clock / maxf(0.05, Motion.seconds(GLITCH_MOTION)) * LOOP_FRAMES
	for b in BURSTS:
		if f >= b.x and f < b.y:
			return true
	return false


func _fill_colors() -> Array[Color]:
	match fill:
		Fill.YELLOW:
			return [Palette.STICKER_SAFE, Palette.STICKER_SAFE_LOW]
		Fill.BLUE:
			return [Palette.STICKER_BLUE, Palette.STICKER_BLUE_LOW]
		Fill.GREY:
			return [Palette.TEXT_MID, Palette.DISABLED]
	return [Palette.STICKER_COMMIT_HIGH, Palette.STICKER_COMMIT_LOW]


func _draw() -> void:
	var word := shown_text()
	var f := Chrome.sticker_font()
	var px := letter_px()
	var s := float(px)
	var key := s * KEYLINE
	var die := s * DIE_CUT
	var ext := s * EXTRUDE
	var w := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var cap := s * CAP_SHARE
	var origin := Vector2((size.x - w - ext) * 0.5, (size.y - ext + cap) * 0.5)
	var top := origin.y - cap
	var cols := _fill_colors()
	_mat.set_shader_parameter(&"top_color", cols[0])
	_mat.set_shader_parameter(&"bottom_color", cols[1])
	_mat.set_shader_parameter(&"white_color", Palette.STICKER_DIE_CUT)
	_mat.set_shader_parameter(&"glitch_a", Palette.CELL_PINK)
	_mat.set_shader_parameter(&"glitch_b", Palette.CORP_SOLACE)
	_mat.set_shader_parameter(&"fill_top", top)
	_mat.set_shader_parameter(&"fill_bottom", origin.y)
	_mat.set_shader_parameter(&"sweep_width", s * 0.35)
	_mat.set_shader_parameter(&"scan_period", maxf(3.0, s * 0.12))
	_mat.set_shader_parameter(&"band_h", cap / BURST_SHIFTS.size())
	_mat.set_shader_parameter(&"grey", DISABLED_GREY if disabled else 0.0)
	var outer := roundi((die + key) * 2.0)
	# The lime die-cut halo (focus, §2.10), then the shadow, the ink rim and the white die-cut.
	if has_focus() or KitState.of(self) == KitState.FOCUS:
		draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer + roundi(s * HALO * 2.0) + roundi(RIM_PX * 2.0), Palette.GLYPH_INK)
		draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer + roundi(s * HALO * 2.0), Palette.FOCUS)
	draw_string_outline(f, origin + Vector2(s * SHADOW_SHARE * 0.5, s * SHADOW_SHARE), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer + roundi(RIM_PX * 2.0), Color(Palette.GLYPH_INK, SHADOW_ALPHA))
	draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer + roundi(RIM_PX * 2.0), Palette.GLYPH_INK)
	draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer, Palette.STICKER_DIE_CUT)
	# The extrude (down and right), then the keyline.
	var steps := maxi(2, roundi(ext))
	for i in range(steps, 0, -1):
		var o := origin + Vector2(ext, ext) * (float(i) / steps)
		draw_string_outline(f, o, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(key * 2.0), Palette.GLYPH_INK)
		draw_string(f, o, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.GLYPH_INK)
	draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(key * 2.0), Palette.GLYPH_INK)
	# The fill (the shader paints the marker colours).
	if fill == Fill.GLITCH:
		_draw_glitch(f, origin, word, px)
	elif fist_at >= 0 and fist_at < word.length():
		var head := word.substr(0, fist_at)
		var tail := word.substr(fist_at + 1)
		var head_w := f.get_string_size(head, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		var slot_w := f.get_string_size(word.substr(0, fist_at + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		draw_string(f, origin, head, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color.MAGENTA)
		draw_string(f, origin + Vector2(slot_w, 0), tail, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color.MAGENTA)
		_draw_fist(Rect2(Vector2(origin.x + head_w, top), Vector2(slot_w - head_w, cap)).grow(key * 0.8), key)
	else:
		draw_string(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color.MAGENTA)
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), state(), false)


## SIMULATE: white letters with a pink split on the left and a green split on the right and
## thin scan lines; in a burst, horizontal bands of the letters shift sideways (the die-cut
## never moves: it was drawn from the clean word).
func _draw_glitch(f: Font, origin: Vector2, word: String, px: int) -> void:
	var split := float(px) * SPLIT_SHARE
	draw_string(f, origin - Vector2(split, 0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.CELL_PINK)
	draw_string(f, origin + Vector2(split, 0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.CORP_SOLACE)
	if not bursting():
		draw_string(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color.GREEN)
		return
	for i in BURST_SHIFTS.size():
		var marker := Color.GREEN
		marker.b = float(i + 1) / 8.0
		draw_string(f, origin + Vector2(BURST_SHIFTS[i] * px, 0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, marker)


## The red rebel fist in a letter's slot (round 33 §2): four knuckles, a thumb across the
## front, a forearm with a cuff; ink keyline like the letters.
func _draw_fist(box: Rect2, key: float) -> void:
	var red := Palette.CORP_REBEL_CELL
	var ink := Palette.GLYPH_INK
	var lw := maxf(1.5, key * 1.2)
	var cuff := _unit(box, FIST_CUFF)
	draw_rect(cuff.grow(lw), ink)
	draw_rect(cuff, red.darkened(0.25))
	draw_rect(Rect2(cuff.position, Vector2(cuff.size.x, cuff.size.y * 0.35)), red.darkened(0.45))
	var body := _unit(box, FIST_BODY)
	var kr := box.size.x * FIST_KNUCKLE_R
	for i in FIST_KNUCKLES:
		var c := Vector2(body.position.x + body.size.x * (i + 0.5) / FIST_KNUCKLES, body.position.y + kr * 0.6)
		draw_circle(c, kr + lw, ink)
	draw_rect(body.grow(lw), ink)
	draw_rect(body, red)
	for i in FIST_KNUCKLES:
		var c := Vector2(body.position.x + body.size.x * (i + 0.5) / FIST_KNUCKLES, body.position.y + kr * 0.6)
		draw_circle(c, kr, red.lightened(0.18))
	for i in range(1, FIST_KNUCKLES):
		var x := body.position.x + body.size.x * float(i) / FIST_KNUCKLES
		draw_line(Vector2(x, body.position.y), Vector2(x, body.position.y + body.size.y * 0.55), ink, lw * 0.8)
	var thumb := _unit(box, FIST_THUMB)
	draw_rect(thumb.grow(lw * 0.8), ink)
	draw_rect(thumb, red.lightened(0.1))


static func _unit(box: Rect2, u: Rect2) -> Rect2:
	return Rect2(box.position + u.position * box.size, u.size * box.size)
