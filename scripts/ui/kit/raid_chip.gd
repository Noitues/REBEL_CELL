class_name RaidChip
extends Label
## ART-6 3A: a status chip in the Cell's terminal (ART_BIBLE v2 §4.8 "YOUR NETWORK = CRT
## terminal with status chips", round 21 `ui19._draw_rows` "node" rows): the node's projected
## or resolved word in an outlined box, in its colour, always with the word (never colour
## alone, §5.1): HOLDS green, DOWN amber, TAKEN red, HOME -n pink, PLACED cyan.

const PAD := Vector2(6, 1)

var col: Color = Palette.GAIN


func _init(p_text: String = "", p_col: Color = Palette.GAIN) -> void:
	text = p_text
	col = p_col
	name = "Chip"
	add_theme_font_override("font", Palette.mono())
	add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	add_theme_color_override("font_color", col)
	var box := StyleBoxFlat.new()
	box.bg_color = Color(col, 0.08)
	box.border_color = col
	box.set_border_width_all(1)
	box.content_margin_left = PAD.x * Settings.text_scale
	box.content_margin_right = PAD.x * Settings.text_scale
	box.content_margin_top = PAD.y * Settings.text_scale
	box.content_margin_bottom = PAD.y * Settings.text_scale
	add_theme_stylebox_override("normal", box)
	size_flags_vertical = Control.SIZE_SHRINK_CENTER
	mouse_filter = Control.MOUSE_FILTER_PASS


## The chip colour of node outcome `outcome` (RaidResolver words; "" = no forecast).
static func outcome_color(outcome: String) -> Color:
	match outcome:
		"down":
			return Palette.WARN
		"taken", "breached":
			return Palette.HARM
	return Palette.GAIN
