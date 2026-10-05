class_name RaidSticker
extends Button
## ART-6 3A: a vinyl sticker word on the raid (ART_BIBLE v2 §1.2 "Vinyl sticker"): the things
## that never change (START DEFENSE, CELL HOLDS, BACK TO THE GRID). Anton lettering in a two-
## tone fill, an ink keyline, an extrude, a white die-cut border and a soft shadow; a focused
## sticker gets a lime die-cut halo (§2.10), a hovered one lifts, a disabled one is grey
## vinyl. As a button it presses like any other (the scene decides what a press means); as a
## stamp (`stamp_only`) it takes no input.
##
## Seam: 1B's vinyl sticker material (gloss sweep, peel / slap / dissolve) replaces this
## drawing; the raid's sticker motions (`raid_holds_slap`, `raid_start_peel`) are played by
## the scene on this node's scale / rotation / position, so they carry over.

## Fill pairs (top, bottom): pink = the committing verb, yellow = the safe choice and the
## result stamp (§2.10 two-sticker choice; STICKER_SAFE once 1A lands).
const PINK := &"pink"
const YELLOW := &"yellow"

## The die-cut, keyline and extrude (x the lettering size; §2.9: keyline 5 px, extrude 7 px,
## die-cut 12 px at 96 px lettering).
const DIE_CUT := 0.2
const KEYLINE := 0.075
const EXTRUDE := 0.07
## The top tone's lift (x size) over the bottom tone, the shadow's offset (x size) and alpha.
const TOP_LIFT := 0.035
const SHADOW_OFF := Vector2(0.05, 0.08)
const SHADOW_ALPHA := 0.55
## The hover lift (px) and the focus halo's width (x size).
const HOVER_LIFT := 2.0
const HALO := 0.07
## Most copies an outline ring draws.
const RING_STEPS := 24
## Room round the word for the die-cut (x size).
const ROOM := 0.32

var px: int = 32
var fill: StringName = PINK
var tilt_deg: float = -2.0
var _hot: bool = false


func _init(p_text: String = "", p_px: int = 32, p_fill: StringName = PINK, p_tilt: float = -2.0) -> void:
	text = p_text
	px = p_px
	fill = p_fill
	tilt_deg = p_tilt
	flat = true
	clip_text = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for key in ["normal", "hover", "pressed", "disabled", "hover_pressed"]:
		add_theme_stylebox_override(key, StyleBoxEmpty.new())
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		add_theme_color_override(key, Palette.AUTO)
	add_theme_font_override("font", Palette.display())
	add_theme_font_size_override("font_size", px)
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)
	_fit()


## A sticker that takes no input (CELL HOLDS on the report).
func stamp_only() -> RaidSticker:
	focus_mode = Control.FOCUS_NONE
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	return self


## MotionSkip (ANIM-R6 D7): a sticker motion (peel, slap) runs on its position, turn, scale
## or alpha.
func motion_running() -> bool:
	for p: NodePath in [^"position", ^"rotation", ^"scale", ^"modulate:a"]:
		if Motion.held(self, p):
			return true
	return false


## MotionSkip: the sticker at its motion's end (a peeled sticker is gone).
func complete_motion() -> void:
	for p: NodePath in [^"position", ^"rotation", ^"scale", ^"modulate:a"]:
		Motion.settle(self, p)
	if has_meta(&"peel"):
		queue_free()


## The word as drawn (translated, as a Button shows it).
func shown_text() -> String:
	return tr(text).to_upper()


func _fit() -> void:
	var f := Palette.display()
	var sz := f.get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	custom_minimum_size = Vector2(sz.x + px * ROOM * 2.0, f.get_height(px) + px * ROOM * 1.4)
	pivot_offset = custom_minimum_size * 0.5


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSLATION_CHANGED:
		_fit()
		queue_redraw()
	elif what == NOTIFICATION_RESIZED:
		pivot_offset = size * 0.5


## The two tones of `fill` (top, bottom).
static func tones(p_fill: StringName) -> Array[Color]:
	if p_fill == YELLOW:
		return [Palette.STICKER_SAFE,
			Palette.STICKER_SAFE_LOW]
	return [Palette.CELL_PINK.lerp(Palette.STICKER_PINK, 0.3), Palette.CELL_PINK.darkened(0.12)]


func _draw() -> void:
	var f := Palette.display()
	var word := shown_text()
	var sz := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, px)
	var lift := HOVER_LIFT if (_hot or has_focus()) and not disabled else 0.0
	var c := size * 0.5 - Vector2(0, lift)
	draw_set_transform(c, deg_to_rad(tilt_deg), Vector2.ONE)
	var at := Vector2(-sz.x * 0.5, -sz.y * 0.5 + f.get_ascent(px))
	var t := tones(fill)
	var top: Color = t[0]
	var bottom: Color = t[1]
	var white := Palette.TEXT_HI
	var ink := Palette.NIGHT_SKY
	if disabled:
		var g := top.get_luminance()
		top = Color(g, g, g).lerp(Palette.DISABLED, 0.3)
		bottom = top.darkened(0.15)
		white = white.darkened(0.25)
	var die := maxi(2, roundi(px * DIE_CUT))
	var key := maxi(1, roundi(px * KEYLINE))
	var ext := maxf(1.0, px * EXTRUDE)
	# Outlines as rings of offset copies (an MSDF face caps how wide an outline can draw).
	_ring(f, at + SHADOW_OFF * px, word, die + 2.0, Color(ink, SHADOW_ALPHA))
	if has_focus() and not disabled:
		_ring(f, at, word, die + px * HALO * 2.0, Palette.FOCUS)
	_ring(f, at, word, die, white)
	# The extrude: the keyline stepped down and right.
	var steps := maxi(1, ceili(ext))
	for s in range(steps, 0, -1):
		var o := Vector2(1, 1) * ext * s / steps
		_ring(f, at + o, word, key, ink)
	_ring(f, at, word, key, ink)
	draw_string(f, at, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, bottom)
	draw_string(f, at - Vector2(0, px * TOP_LIFT), word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Color(top, 0.85))
	draw_set_transform(Vector2.ZERO)


## `word` drawn round `at` at radius `r` (filled in at half radius too): a solid outline.
func _ring(f: Font, at: Vector2, word: String, r: float, col: Color) -> void:
	draw_string(f, at, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
	for ring: float in [r * 0.5, r]:
		var n := clampi(ceili(ring * 1.6), 8, RING_STEPS)
		for i in n:
			draw_string(f, at + Vector2.from_angle(TAU * i / n) * ring, word, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)
