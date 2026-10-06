class_name VerbSticker
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
## scene decides what a press means. View only.
## PINK and YELLOW are drawn by Group 1B's VinylSticker (`vinyl`, the kit material: die-cut,
## keyline, extrude, rim, gloss, its own hover / press / disabled states and motions); this
## Button gives it focus, presses and the lime focus halo. BLUE (the pictogram letter) and
## GLITCH have no kit fill yet, so they are drawn here with the kit's raster Anton.

enum Fill { PINK, YELLOW, BLUE, GLITCH, GREY }

const SHADER := preload("res://shaders/chrome/vinyl_sticker.gdshader")
## Motion entries: hover growth + gloss sweep, the press squash, the glitch bursts.
const HOVER_MOTION := &"sticker_hover"
const SWEEP_MOTION := &"sticker_gloss_sweep"
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
## The scale the running hover / press motion ends on.
var _scale_to: Vector2 = Vector2.ONE
## The sweep's off position (the shader's default).
const SWEEP_OFF := -10000.0
## Group 1B's sticker drawing a PINK / YELLOW word (null for BLUE / GLITCH).
var vinyl: VinylSticker = null
## Room round the kit sticker's body for the focus halo (px), the halo's stroke and corner.
const HALO_ROOM := 9.0
## The kit sticker's die-cut border as a share of the lettering size.
const KIT_DIE_CUT := 0.2
const HALO_STROKE := 4.0
const HALO_RADIUS := 16


## The concept art baked by tools/art/bake_menus_r33.py (round 33 title.py / menu33.py /
## ui31.sticker, unchanged): `<key>.png` at rest and `<key>_burst_N.png` (the glitch). Focus is not baked: it is the
## rainbow sweep and the curl drawn over the rest art (designer 2026-10-05).
const ART_DIR := "res://assets/ui/menus/stickers/"
## The baked stickers are at 2x the 1920 board: a third of their pixels in the game.
const ART_TO_GAME := 1.0 / 3.0
## The concept's two glitch bursts by loop frame (title.py GLITCH_FRAMES).
const BURST_FRAMES := {9: 0, 10: 1, 27: 1, 28: 0}
## The baked art's key ("" = none: drawn).
var art_key: String = ""
## Parity SLOTS (designer 2026-10-05): a baked sticker shown smaller than the board it was
## baked for (the slots page's DELETE, at the size of the LOAD beside it). Set it with
## `set_art_scale` (it refits).
var art_scale: float = 1.0


## Shows the baked art at `k` x its game size (1.0 = as baked) and refits.
func set_art_scale(k: float) -> VerbSticker:
	art_scale = k
	_fit()
	return self
var _art_rest: Texture2D = null
## The baked art's opaque body (texture px).
var _art_body: Rect2 = Rect2()
var _art_bursts: Array[Texture2D] = []
## Hovered or focused (the rainbow sheen and the curl show).
var _focused: bool = false
## The corner curl's size as a share of the sticker's shorter side, the sheen's band width as a share of its
## height, and where the static sheen (no motion) stands across its width.
const CURL_BACK_LIGHTEN := 0.35


## The baked art key for a screen-title word ("OPTIONS" -> "title_options"), or "" when the
## concept has none (the kit's sticker draws it).
static func title_art(word: String) -> String:
	var key := "title_" + word.to_lower().replace(" ", "_")
	return key if ResourceLoader.exists(ART_DIR + key + ".png") else ""


## True when the kit's VinylSticker draws this fill (no baked art for it).
func uses_kit() -> bool:
	return art_key == "" and (fill == Fill.PINK or fill == Fill.YELLOW)


## True when the concept's baked art draws it.
func uses_art() -> bool:
	return _art_rest != null


func _load_art() -> void:
	if art_key == "" or not ResourceLoader.exists(ART_DIR + art_key + ".png"):
		return
	_art_rest = load(ART_DIR + art_key + ".png") as Texture2D
	_art_body = _opaque_rect(_art_rest.get_image())  # the opaque body in texture px (the art has a shadow margin)
	var k := 0
	while ResourceLoader.exists(ART_DIR + "%s_burst_%d.png" % [art_key, k]):
		_art_bursts.append(load(ART_DIR + "%s_burst_%d.png" % [art_key, k]) as Texture2D)
		k += 1


## The rect of the pixels of `img` that are mostly opaque (alpha over 0.5), in px; the whole image when none is.
static func _opaque_rect(img: Image) -> Rect2:
	var x0 := img.get_width()
	var y0 := img.get_height()
	var x1 := -1
	var y1 := -1
	for y in img.get_height():
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.5:
				x0 = mini(x0, x)
				x1 = maxi(x1, x)
				y0 = mini(y0, y)
				y1 = maxi(y1, y)
	if x1 < 0:
		return Rect2(Vector2.ZERO, Vector2(img.get_size()))
	return Rect2(Vector2(x0, y0), Vector2(x1 - x0 + 1, y1 - y0 + 1))


func _init(p_text: String = "", p_fill: int = Fill.PINK, p_size: float = 40.0, p_tilt: float = 0.0, p_art: String = "") -> void:
	text = p_text
	art_key = p_art
	_load_art()
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


## MotionSkip: the hover growth, press squash and gloss sweep drawn here (BLUE / GLITCH; the
## kit sticker registers its own) end with any press another helper takes. The glitch loop
## is an idle T0 loop, not a motion to skip.
func motion_running() -> bool:
	return (_scale_tween != null and _scale_tween.is_running()) or (_sweep_tween != null and _sweep_tween.is_running())


func complete_motion() -> void:
	if _scale_tween != null and _scale_tween.is_valid():
		_scale_tween.kill()
		scale = _scale_to
	if sweep_running():
		_sweep_tween.kill()
		_sweep_tween = null
		_finish_sweep()


func _ready() -> void:
	MotionSkip.register_passive(self)
	if uses_kit() and vinyl == null:
		vinyl = VinylSticker.new()
		vinyl.name = "Vinyl"
		vinyl.fill = VinylSticker.Fill.YELLOW if fill == Fill.YELLOW else VinylSticker.Fill.PINK
		vinyl.tilt_deg = tilt
		vinyl.ambient_sweep = true
		vinyl.sweep_primary = sweep_primary
		vinyl.seed = hash(text) % 997
		add_child(vinyl)
		_fit()
	Settings.changed.connect(_refit_later)
	resized.connect(_pivot)
	_pivot()
	set_process(true)


func _enter_tree() -> void:
	StickerSweepQueue.join(self)


func _exit_tree() -> void:
	StickerSweepQueue.leave(self)
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
	if uses_art():
		var k := ART_TO_GAME * art_scale * clampf(Settings.text_scale, 1.0, SCALE_MAX)
		custom_minimum_size = (_art_rest.get_size() * k).ceil()
		size = custom_minimum_size
		_pivot()
		queue_redraw()
		return
	if vinyl != null:
		vinyl.font_step = maxi(1, roundi(letter_px() / Settings.text_scale))
		# The die-cut edge is the kit's own, proportional to the lettering (VinylSticker.edge_for).
		vinyl.text = shown_text()
		var b := vinyl.body_rect
		custom_minimum_size = (b.size + Vector2(HALO_ROOM, HALO_ROOM) * 2.0).ceil()
		size = custom_minimum_size
		vinyl.position = Vector2(HALO_ROOM, HALO_ROOM) - b.position
		_pivot()
		queue_redraw()
		return
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
	rotation_degrees = 0.0 if vinyl != null else tilt  # the kit sticker tilts itself


## Re-measures (after a text or text-scale change).
func refit() -> void:
	_fit()


func set_label(t: String) -> void:
	if t != text:
		text = t
		_fit()


func _hot(on: bool) -> void:
	_grow(on or has_focus())
	queue_redraw()


func _notification(what: int) -> void:
	if what == NOTIFICATION_FOCUS_ENTER:
		_grow(true)
	elif what == NOTIFICATION_FOCUS_EXIT:
		_grow(bool(get_meta(KitState.META_HOVER, false)))


## Hover / focus: the sticker grows to the `sticker_hover` amplitude (1.05) about its centre.
func _grow(on: bool) -> void:
	if vinyl != null:
		vinyl.set_state(VinylSticker.State.DISABLED if disabled else (VinylSticker.State.HOVER if on else VinylSticker.State.REST))
		return
	# Focus / hover (designer 2026-10-06, B1d): the peel-back only (the corner curl, _draw_curl, and the
	# grow); the rainbow gloss is the one scheduled sweep (run_sweep), never focus.
	_focused = on and not disabled
	queue_redraw()
	var to := Vector2.ONE * (Motion.amplitude(HOVER_MOTION) if on and not disabled else 1.0)
	if _scale_tween != null:
		_scale_tween.kill()
	_scale_to = to
	_scale_tween = Motion.run(HOVER_MOTION, self, ^"scale", to)


## A press squashes it (`sticker_press`: x to VinylSticker.PRESS_X, y to the amplitude); a
## release springs it back to its hover size.
func _press(down: bool) -> void:
	if disabled:
		return
	if vinyl != null:
		var hot := has_focus() or bool(get_meta(KitState.META_HOVER, false))
		vinyl.set_state(VinylSticker.State.PRESSED if down else (VinylSticker.State.HOVER if hot else VinylSticker.State.REST))
		return
	var a := Motion.amplitude(PRESS_MOTION)
	var hover := Motion.amplitude(HOVER_MOTION) if (has_focus() or bool(get_meta(KitState.META_HOVER, false))) else 1.0
	var to := Vector2(VinylSticker.PRESS_X, a) if down else Vector2.ONE * hover
	if _scale_tween != null:
		_scale_tween.kill()
	_scale_to = to
	_scale_tween = Motion.run(PRESS_MOTION, self, ^"scale", to)


## StickerSweepQueue interface (drawn and baked art; the kit sticker joins through its own vinyl).
@export var ambient_sweep: bool = true
## The screen names this sticker its primary verb: the queue sweeps it before any other (rank 0).
@export var sweep_primary: bool = false:
	set(v):
		sweep_primary = v
		if vinyl != null:
			vinyl.sweep_primary = v


## Order of the primary pick: 0 named, 1 pink, 2 the rest.
func sweep_rank() -> int:
	if sweep_primary:
		return 0
	return 1 if fill == Fill.PINK else 2


## It may take the turn: shown, enabled, drawn here (the kit sticker's vinyl sweeps for itself).
func sweep_ready() -> bool:
	return vinyl == null and is_visible_in_tree() and not disabled


func sweep_running() -> bool:
	return _sweep_tween != null and _sweep_tween.is_valid() and _sweep_tween.is_running()


## One rainbow gloss sweep across the lettering (`sticker_gloss_sweep`, run by StickerSweepQueue on the
## primary verb); none when the motion does not play. Returns its seconds.
func run_sweep() -> float:
	if vinyl != null or not Motion.live(SWEEP_MOTION):
		_finish_sweep()
		return 0.0
	if _sweep_tween != null:
		_sweep_tween.kill()
	var d := Motion.seconds(SWEEP_MOTION)
	# ONE narrow 45 degree band (x + y = sweep): its width a share of the sticker's width (the entry's `delay`), the
	# alpha the entry's amplitude; it crosses from off one corner to off the other.
	var half := Motion.entry(SWEEP_MOTION).delay * size.x * 0.5
	var from := -half * 2.0
	var to := size.x + size.y + half * 2.0
	_mat.set_shader_parameter(&"sweep_width", half)
	_mat.set_shader_parameter(&"rainbow", Motion.amplitude(SWEEP_MOTION))
	_mat.set_shader_parameter(&"sweep", from)
	_sweep_tween = create_tween()
	_sweep_tween.tween_method(func(x: float) -> void: _mat.set_shader_parameter(&"sweep", x), from, to, d)
	_sweep_tween.tween_callback(_finish_sweep)
	return d


func _finish_sweep() -> void:
	_mat.set_shader_parameter(&"sweep", SWEEP_OFF)
	_mat.set_shader_parameter(&"rainbow", 0.0)
	StickerSweepQueue.done(self, Time.get_ticks_msec(), Motion.seconds(SWEEP_MOTION))


func _process_sweep() -> void:
	if ambient_sweep and vinyl == null and StickerSweepQueue.take_turn(self, Time.get_ticks_msec()):
		run_sweep()


func _process(delta: float) -> void:
	_process_sweep()
	if fill != Fill.GLITCH:
		return
	if fill != Fill.GLITCH or not Motion.live(GLITCH_MOTION):
		if _clock != 0.0:
			_clock = 0.0
			queue_redraw()
		return
	var was := burst_phase()
	_clock = fmod(_clock + delta, maxf(0.05, Motion.seconds(GLITCH_MOTION)))
	if burst_phase() != was:
		queue_redraw()


## True while the glitch bursts (frames 9-10 and 27-28 of its 48-frame loop).
func bursting() -> bool:
	return burst_phase() >= 0


## The burst frame shown now (title.py GLITCH_FRAMES), -1 at rest.
func burst_phase() -> int:
	if fill != Fill.GLITCH or not Motion.live(GLITCH_MOTION):
		return -1
	var f := int(_clock / maxf(0.05, Motion.seconds(GLITCH_MOTION)) * LOOP_FRAMES)
	return int(BURST_FRAMES.get(f, -1))


func _fill_colors() -> Array[Color]:
	match fill:
		Fill.YELLOW:
			return Palette.STICKER_FILL_YELLOW
		Fill.BLUE:
			return [Palette.STICKER_BLUE, Palette.STICKER_BLUE_LOW]
		Fill.GREY:
			return [Palette.TEXT_MID, Palette.DISABLED]
	return Palette.STICKER_FILL_PINK


func _draw() -> void:
	_mat.set_shader_parameter(&"grey", DISABLED_GREY if disabled else 0.0)
	if uses_art():
		_draw_art()
		return
	if vinyl != null:
		_draw_kit_frame()
		return
	var word := shown_text()
	var f: Font = VinylSticker.art_font()  # the kit's raster Anton (one face for every sticker)
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
	# The shadow, the ink rim and the white die-cut (focus is the rainbow sheen and the curl, never a halo).
	draw_string_outline(f, origin + Vector2(s * SHADOW_SHARE * 0.5, s * SHADOW_SHARE), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer + roundi(RIM_PX * 2.0), Color(Palette.VINYL_INK, SHADOW_ALPHA))
	draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer + roundi(RIM_PX * 2.0), Palette.VINYL_INK)
	draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, outer, Palette.STICKER_DIE_CUT)
	# The extrude (down and right), then the keyline.
	var steps := maxi(2, roundi(ext))
	for i in range(steps, 0, -1):
		var o := origin + Vector2(ext, ext) * (float(i) / steps)
		draw_string_outline(f, o, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(key * 2.0), Palette.VINYL_INK)
		draw_string(f, o, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.VINYL_INK)
	draw_string_outline(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, roundi(key * 2.0), Palette.VINYL_INK)
	# The fill (the shader paints the marker colours).
	if fill == Fill.GLITCH:
		_draw_glitch(f, origin, word, px)
	elif fist_at >= 0 and fist_at < word.length():
		var head := word.substr(0, fist_at)
		var tail := word.substr(fist_at + 1)
		var head_w := f.get_string_size(head, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		var slot_w := f.get_string_size(word.substr(0, fist_at + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
		draw_string(f, origin, head, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.STICKER_FILL_MARKER)
		draw_string(f, origin + Vector2(slot_w, 0), tail, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.STICKER_FILL_MARKER)
		_draw_fist(Rect2(Vector2(origin.x + head_w, top), Vector2(slot_w - head_w, cap)).grow(key * 0.8), key)
	else:
		draw_string(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.STICKER_FILL_MARKER)
	var edge := die + key
	_draw_curl(Rect2(Vector2(origin.x - edge, top - edge), Vector2(w + ext + edge * 2.0, cap + ext + edge * 2.0)))
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), state(), false)


## The concept art: its disabled state follows the Button's, the lime halo round
## its body on focus (designer 2026-10-05: no halo, no brackets: the kit sticker's own rainbow sheen and curl).
func _draw_kit_frame() -> void:
	var want := VinylSticker.State.DISABLED if disabled else vinyl.state
	if vinyl.state != want or (vinyl.state == VinylSticker.State.DISABLED and not disabled):
		vinyl.set_state.call_deferred(want if disabled else VinylSticker.State.REST)
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), state(), false)


## The concept art: rest, focus (lime halo), the sweep's frame, the glitch's burst frame; centred.
func _draw_art() -> void:
	var tex := _art_rest  # focus is not baked: the rainbow sheen and the curl are drawn over it
	var ph := burst_phase()
	if ph >= 0 and ph < _art_bursts.size():
		tex = _art_bursts[ph]
	var k := ART_TO_GAME * art_scale * clampf(Settings.text_scale, 1.0, SCALE_MAX)
	var sz := tex.get_size() * k
	draw_texture_rect(tex, Rect2((size - sz) * 0.5, sz), false)
	_draw_curl(Rect2((size - sz) * 0.5 + _art_body.position * k, _art_body.size * k))
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), state(), false)


## The focus curl for the drawn and baked stickers: the top right corner peels back (a paper-backed
## flap over the corner and its cast shadow; the kit sticker's own curl is the shader's fold).
func _draw_curl(body: Rect2) -> void:
	if not _focused:
		return
	var c := VinylSticker.peel_leg(body.size.x, get_viewport_rect().size.y)  # round 44: a fixed 45 degree fold
	var flap := curl_flap(body, c)
	var tr := body.position + Vector2(body.size.x, 0.0)
	var shade := PackedVector2Array([tr + Vector2(-c, c), tr + Vector2(0.0, c), tr + Vector2(-c, c * 1.35)])
	draw_colored_polygon(shade, Color(Palette.VINYL_INK, SHADOW_ALPHA * 0.5))
	draw_colored_polygon(flap, Palette.VINYL_BACKING.lightened(CURL_BACK_LIGHTEN))
	draw_polyline(PackedVector2Array([flap[0], flap[2]]), Color(Palette.STICKER_DIE_CUT, 0.9), 1.0)


## The curl's flap on a baked / drawn sticker whose body is `body`, for a fold leg `c`: OPAQUE and covering the
## original corner pixels (the triangle the fold takes away) as well as the folded-over triangle, so no doubled
## corner shows (the proper corner cut for baked art is B5's). Points: top edge, corner, side edge, fold inner.
static func curl_flap(body: Rect2, c: float) -> PackedVector2Array:
	var tr := body.position + Vector2(body.size.x, 0.0)
	return PackedVector2Array([tr + Vector2(-c, 0.0), tr, tr + Vector2(0.0, c), tr + Vector2(-c, c)])


## SIMULATE: white letters with a pink split on the left and a green split on the right and
## thin scan lines; in a burst, horizontal bands of the letters shift sideways (the die-cut
## never moves: it was drawn from the clean word).
func _draw_glitch(f: Font, origin: Vector2, word: String, px: int) -> void:
	var split := float(px) * SPLIT_SHARE
	draw_string(f, origin - Vector2(split, 0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.CELL_PINK)
	draw_string(f, origin + Vector2(split, 0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.CORP_SOLACE)
	if not bursting():
		draw_string(f, origin, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.STICKER_GLITCH_MARKER)
		return
	for i in BURST_SHIFTS.size():
		var marker := Palette.STICKER_GLITCH_MARKER
		marker.b = float(i + 1) / 8.0
		draw_string(f, origin + Vector2(BURST_SHIFTS[i] * px, 0), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, marker)


## The red rebel fist in a letter's slot (round 33 §2): four knuckles, a thumb across the
## front, a forearm with a cuff; ink keyline like the letters.
func _draw_fist(box: Rect2, key: float) -> void:
	var red := Palette.CORP_REBEL_CELL
	var ink := Palette.VINYL_INK
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
