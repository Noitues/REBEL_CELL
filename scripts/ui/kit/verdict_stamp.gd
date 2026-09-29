class_name VerdictStamp
extends Control
## Art pass W8c (ART_BIBLE §6.6, §4.2 `hero`, §11 Run failed): a run's verdict as a big
## rubber stamp: FLATLINED, JACKED OUT, HOME FELL. Solid ink in the verdict's colour, a
## double box frame, the word in the display face at the `hero` step (64 px x the text
## size, never over HERO_MAX), rotated a few degrees; the word shrinks only to fit 140% of
## its width inside the screen (§4.3 rule 5), never under `display`. Display only (no
## focus, no clicks). PAPER. View only.

## The frame's inner gap, its two rules' widths and the padding round the word (px at 1.0).
const FRAME_GAP := 6.0
const OUTER_RULE := 5.0
const INNER_RULE := 2.0
const PAD := Vector2(UiTheme.SP_L, UiTheme.SP_S)
## The stamp's tilt (degrees; §6.6: ±6).
const TILT := -5.0
## Localisation slack the word keeps inside `max_width` (§4.3 rule 5).
const SLACK := 1.4
## The ink's roughness: the flecks' alpha (the backdrop's dark through the ink) and their count.
const SPECKLE_ALPHA := 0.42
const SPECKLES := 60

var word: String = ""
var color: Color = Palette.HARM
## The word's size in use (px) and the most width the stamp may take (px; 0 = no limit).
var font_px: int = 0
var max_width: float = 0.0


func _init(p_word: String = "", p_color: Color = Palette.HARM, p_max_width: float = 0.0) -> void:
	name = "VerdictStamp"
	word = p_word
	color = p_color
	max_width = p_max_width
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	rotation_degrees = TILT
	_fit()


func _ready() -> void:
	pivot_offset = size * 0.5
	resized.connect(func() -> void: pivot_offset = size * 0.5)


## The hero size at the player's text size, capped at HERO_MAX (px).
static func hero_px() -> int:
	return mini(UiTheme.font_px(UiTheme.HERO), UiTheme.HERO_MAX)


func _fit() -> void:
	var f := Palette.display()
	var s := Settings.text_scale
	font_px = hero_px()
	var chrome := (PAD.x + FRAME_GAP + OUTER_RULE) * 2.0 * s
	while max_width > 0.0 and font_px > UiTheme.font_px(UiTheme.DISPLAY) \
			and f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px).x * SLACK + chrome > max_width:
		font_px -= 1
	var w := f.get_string_size(word, HORIZONTAL_ALIGNMENT_LEFT, -1, font_px).x + chrome
	var h := f.get_height(font_px) + (PAD.y + FRAME_GAP + OUTER_RULE) * 2.0 * s
	custom_minimum_size = Vector2(ceilf(w), ceilf(h))
	queue_redraw()


func _draw() -> void:
	var s := Settings.text_scale
	var r := Rect2(Vector2.ZERO, size)
	var ink := color
	if Settings.high_contrast:
		draw_rect(r, HighContrast.BG)
	draw_rect(r.grow(-OUTER_RULE * 0.5 * s), ink, false, OUTER_RULE * s)
	draw_rect(r.grow(-(OUTER_RULE + FRAME_GAP) * s), ink, false, INNER_RULE * s)
	var f := Palette.display()
	var y := (size.y + f.get_ascent(font_px) - f.get_descent(font_px)) * 0.5
	draw_string(f, Vector2(0, y), word, HORIZONTAL_ALIGNMENT_CENTER, size.x, font_px, ink)
	# Rubber-stamp speckle: hashed flecks of the backdrop's dark through the ink (a stamp,
	# not a sign), fixed per word (no motion).
	if not Settings.high_contrast:
		for k in SPECKLES:
			var h := absi(hash([word, k]))
			var p := Vector2(float(h % 1000) / 1000.0 * size.x, float((h / 1000) % 1000) / 1000.0 * size.y)
			draw_circle(p, (1.0 + float((h / 7) % 3)) * s, Color(Palette.NIGHT_SKY, SPECKLE_ALPHA))


## The word as stamped (tests).
func shown_word() -> String:
	return word
