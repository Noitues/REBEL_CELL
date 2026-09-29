class_name ZineStamp
extends Button
## Circular rubber stamp (STYLE_GUIDE 4, ART_BIBLE §6.6): JACK IN at HQ, the result stamps
## (REPELLED, CLEAN EXIT...). A stamp says one thing in at most MAX_WORDS words (a debug
## warning otherwise) and is held long enough to read: `hold_seconds` (0.6 s + 0.05 s per
## character, from the `stamp_hold` entry). `stamp_in` reveals the ring with W6's
## `marker_stroke` shader (the end state at once under reduce effects). `hint` is an
## optional key hint under the word (empty by default: H20, a stamp only names a key that
## really presses it). A result stamp is `display_only()`: no focus, no clicks.
## All six §6 states: hover glows, focus adds the FOCUS brackets, pressed drops, disabled
## draws the DISABLED ring with a lock, refused flashes HARM (KitState).

## §6.6: a stamp says one thing in at most this many words.
const MAX_WORDS := 3
## The reading-time entry (duration = the base, amplitude = seconds per character).
const HOLD_MOTION := &"stamp_hold"
## The reveal's entry (T2: the ring draws on, the stamp lands from amplitude x scale).
const IN_MOTION := &"zine_stamp_in"
const STROKE_SHADER := "res://shaders/marker_stroke.gdshader"
## The stamp's diameter at text scale 1.0 (px).
const SIDE := 112.0
## The inner ring's inset and the word's side inset (px), and the rings' strokes.
const RING_GAP := 9.0
const WORD_INSET := 12.0
const RING_W := 4.0
const INNER_RING_W := 1.5
const RING_SEGMENTS := 48
## The hover / focus glow: this far outside the ring (px) at this alpha (x the §6 glow).
const GLOW_GROW := 4.0
const GLOW_ALPHA := 0.45
## The dark disc behind the words.
const DISC_ALPHA := 0.85
## Word baseline and hint baseline below the centre (px).
const WORD_BASE := 8.0
const HINT_BASE := 26.0
## The icon over the word: radius and lift as shares of the stamp's radius; the word moves
## down by WORD_DROP of the radius to make room.
const ICON_SHARE := 0.2
const ICON_LIFT := 0.36
const WORD_DROP := 0.12

var stamp_text: String = "SEND IT":
	set(value):
		stamp_text = value
		warn_if_wordy(value)
		queue_redraw()
var stamp_color: Color = Palette.CELL_PINK
## Key hint under the word ("[Space]"); "" draws none.
var hint: String = "":
	set(value):
		hint = value
		queue_redraw()
## A StatIcon over the word (H22 #14: JACK IN carried its meaning in words only); &"" none.
var icon_kind: StringName = &"":
	set(value):
		icon_kind = value
		queue_redraw()


func _init(p_text: String = "SEND IT", p_color: Color = Palette.CELL_PINK, p_hint: String = "") -> void:
	stamp_text = p_text
	stamp_color = p_color
	hint = p_hint
	custom_minimum_size = Vector2(SIDE, SIDE)
	flat = true
	focus_mode = Control.FOCUS_ALL
	# Draws its own states (KitState); no theme box around the sticker.
	for key in [&"focus", &"normal", &"hover", &"pressed", &"disabled", &"hover_pressed"]:
		add_theme_stylebox_override(key, StyleBoxEmpty.new())
	KitState.track(self)
	button_down.connect(queue_redraw)
	button_up.connect(queue_redraw)


## §6.6: how long a stamp or banner reading `text` holds (s): the `stamp_hold` entry's base
## plus its amplitude per character (0.6 s + 0.05 s/char). Read raw (never sped up).
static func hold_seconds(text: String) -> float:
	var e := Motion.entry(HOLD_MOTION)
	if e == null:
		return 0.0
	return e.duration + e.amplitude * text.strip_edges().length()


## §6.6: the number of words in a stamp's `text`.
static func word_count(text: String) -> int:
	return text.strip_edges().split(" ", false).size()


## Warns (debug builds) when a stamp says more than MAX_WORDS words; true when it does.
static func warn_if_wordy(text: String) -> bool:
	if word_count(text) <= MAX_WORDS:
		return false
	if OS.is_debug_build():
		push_warning("ZineStamp: '%s' is over %d words (ART_BIBLE 6.6: a stamp says one thing)." % [text, MAX_WORDS])
	return true


## Animation pass ANIM-6 (4.13): the rings' scale; JACK IN breathes (`jack_ring_breathe`,
## a slow loop between 1 and the entry's amplitude). 1 at rest.
var ring_scale: float = 1.0
var _breath: Tween = null
## §6.6 reveal: the share of the ring drawn on (1 = whole) while `stamp_in` plays.
var reveal: float = 1.0
var _stroke: ColorRect = null


## Starts the slow breathing of the rings (the HQ's JACK IN). Nothing under reduce effects
## or headless: the rings rest at 1.
func breathe() -> void:
	if _breath != null and _breath.is_valid():
		_breath.kill()
	_breath = Motion.loop_pulse(self, ^"ring_scale", &"jack_ring_breathe")


## True while the rings breathe.
func breathing() -> bool:
	return _breath != null and _breath.is_valid()


## §6.6 the stamp lands: its outer ring draws on in marker (`marker_stroke`, W6) and the
## stamp settles from the entry's scale. Under reduce effects or headless: whole at once.
func stamp_in() -> void:
	if not Motion.live(IN_MOTION):
		reveal = 1.0
		_drop_stroke()
		queue_redraw()
		return
	reveal = 0.0
	_stroke = ColorRect.new()
	_stroke.name = "StampStroke"
	_stroke.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var mat := ShaderMaterial.new()
	mat.shader = load(STROKE_SHADER)
	mat.set_shader_parameter(&"shape", 0)
	mat.set_shader_parameter(&"size_px", size)
	mat.set_shader_parameter(&"width_px", RING_W + 2.0)
	mat.set_shader_parameter(&"ink", stamp_color)
	mat.set_shader_parameter(&"progress", 0.0)
	_stroke.material = mat
	add_child(_stroke)
	_stroke.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var e := Motion.entry(IN_MOTION)
	pivot_offset = size * 0.5
	scale = Vector2.ONE * e.amplitude
	var tw := create_tween().set_parallel(true)
	tw.tween_method(func(k: float) -> void: mat.set_shader_parameter(&"progress", k), 0.0, 1.0, Motion.seconds(IN_MOTION))
	tw.tween_property(self, "scale", Vector2.ONE, Motion.seconds(IN_MOTION)).set_ease(e.ease).set_trans(e.trans)
	tw.chain().tween_callback(func() -> void:
		reveal = 1.0
		_drop_stroke()
		queue_redraw())


func _drop_stroke() -> void:
	if _stroke != null and is_instance_valid(_stroke):
		_stroke.queue_free()
	_stroke = null


## A stamp that only shows a result: it takes no focus and no clicks.
func display_only() -> ZineStamp:
	focus_mode = Control.FOCUS_NONE
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	return self


## The state drawn now (KitState: idle, hover, focus, pressed, disabled, refused).
func state() -> StringName:
	return KitState.of(self)


## The word's lettering: `title` at the text scale, down to `caption` to fit the ring.
func word_px(r: float) -> int:
	var px := UiTheme.font_px(UiTheme.TITLE)
	var floor_px := UiTheme.font_px(UiTheme.CAPTION)
	var room := r * 2.0 - WORD_INSET * 2.0
	while px > floor_px and Palette.display().get_string_size(stamp_text, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x > room:
		px -= 1
	return px


func _draw() -> void:
	var st := state()
	var c := size / 2.0 + Vector2(0, KitState.lift(st))
	var r := minf(size.x, size.y) / 2.0 - GLOW_GROW
	var col := stamp_color
	if st == KitState.DISABLED:
		col = Palette.DISABLED
	elif st == KitState.REFUSED:
		col = Palette.HARM
	draw_circle(c, r, Color(Palette.NIGHT_SKY, DISC_ALPHA))
	if st == KitState.HOVER or st == KitState.FOCUS or st == KitState.PRESSED:
		draw_circle(c, r + GLOW_GROW, Color(Palette.CELL_ACID, GLOW_ALPHA * KitState.glow(st)))
		draw_circle(c, r, Color(Palette.NIGHT_SKY, DISC_ALPHA))
	if reveal >= 1.0:
		draw_arc(c, r * ring_scale, 0, TAU, RING_SEGMENTS, col, RING_W)
	draw_arc(c, (r - RING_GAP) * ring_scale, 0, TAU, RING_SEGMENTS, col, INNER_RING_W)
	var drop := 0.0
	if icon_kind != &"":
		StatIcon.draw(self, c + Vector2(0, -r * ICON_LIFT), r * ICON_SHARE, icon_kind, col)
		drop = r * WORD_DROP
	# §3.7: the word on the disc keeps its contrast when disabled (TEXT_MID, not a faded ink).
	var ink := Palette.TEXT_MID if st == KitState.DISABLED else col
	draw_string(Palette.display(), c + Vector2(-r + WORD_INSET, WORD_BASE + drop), stamp_text, HORIZONTAL_ALIGNMENT_CENTER, r * 2 - WORD_INSET * 2,
		word_px(r), ink)
	if hint != "":
		draw_string(Palette.mono(), c + Vector2(-r + WORD_INSET, HINT_BASE), hint, HORIZONTAL_ALIGNMENT_CENTER, r * 2 - WORD_INSET * 2,
			UiTheme.font_px(UiTheme.CAPTION), ink)
	var face := Rect2(c - Vector2(r, r), Vector2(r, r) * 2.0)
	KitState.draw_frame(self, face, st)
