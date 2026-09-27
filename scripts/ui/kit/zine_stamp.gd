class_name ZineStamp
extends Button
## Circular rubber stamp (STYLE_GUIDE 4): JACK IN at HQ, the result stamps (REPELLED,
## CLEAN EXIT...). `hint` is an optional key hint under the word (empty by default: H20,
## a stamp only names a key that really presses it). A result stamp is `display_only()`:
## no focus, no clicks.

var stamp_text: String = "SEND IT"
var stamp_color: Color = Palette.CELL_PINK
## Key hint under the word ("[Space]"); "" draws none.
var hint: String = "":
	set(value):
		hint = value
		queue_redraw()
var _hot: bool = false

## Hint font size at text scale 1.0.
const HINT_SIZE := 11
const WORD_SIZE := 20


func _init(p_text: String = "SEND IT", p_color: Color = Palette.CELL_PINK, p_hint: String = "") -> void:
	stamp_text = p_text
	stamp_color = p_color
	hint = p_hint
	custom_minimum_size = Vector2(112, 112)
	flat = true
	focus_mode = Control.FOCUS_ALL
	# Draws its own hover/focus glow; no theme box around the sticker.
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	mouse_entered.connect(func() -> void: _hot = true; queue_redraw())
	mouse_exited.connect(func() -> void: _hot = false; queue_redraw())
	focus_entered.connect(func() -> void: _hot = true; queue_redraw())
	focus_exited.connect(func() -> void: _hot = false; queue_redraw())


## A stamp that only shows a result: it takes no focus and no clicks.
func display_only() -> ZineStamp:
	focus_mode = Control.FOCUS_NONE
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	return self


func _draw() -> void:
	var c := size / 2.0
	var r := minf(size.x, size.y) / 2.0 - 4
	var col := stamp_color if not disabled else Color(stamp_color, 0.35)
	draw_circle(c, r, Color(Palette.NIGHT_SKY, 0.85))
	if _hot and not disabled:
		draw_circle(c, r + 4, Color(Palette.CELL_ACID, 0.45))
		draw_circle(c, r, Color(Palette.NIGHT_SKY, 0.85))
	draw_arc(c, r, 0, TAU, 48, col, 4.0)
	draw_arc(c, r - 9, 0, TAU, 48, col, 1.5)
	draw_string(Palette.display(), c + Vector2(-r + 12, 8), stamp_text, HORIZONTAL_ALIGNMENT_CENTER, r * 2 - 24, WORD_SIZE, col)
	if hint != "":
		draw_string(Palette.mono(), c + Vector2(-r + 12, 26), hint, HORIZONTAL_ALIGNMENT_CENTER, r * 2 - 24, roundi(HINT_SIZE * Settings.text_scale), col)
