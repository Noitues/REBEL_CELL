class_name Toast
extends PanelContainer
## A short-lived strip of taped paper that says why an action was refused ("Not enough
## RAM") right where the player is looking (H20: refusals used to go to a hidden log).
## View only. Instant and static under headless or reduce effects.

## Seconds on screen, and the fade at the end.
const SHOW_SECONDS := 2.4
const FADE_SECONDS := 0.35
const FONT_SIZE := 15
## A drawn no-entry mark leads the message (readable without the words): radius and the
## room it takes on the left (px at text scale 1.0).
const MARK_RADIUS := 8.0
const MARK_ROOM := 28.0

var label: Label
var _tween: Tween = null


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	visible = false
	var sb := StyleBoxFlat.new()
	sb.bg_color = Palette.NOTE_YELLOW
	sb.border_color = Palette.INK
	sb.set_border_width_all(2)
	sb.set_content_margin_all(8)
	sb.content_margin_left = MARK_ROOM
	add_theme_stylebox_override("panel", sb)
	label = Label.new()
	label.add_theme_color_override("font_color", Palette.INK)
	label.add_theme_font_override("font", Palette.marker())
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(label)


## Shows `text` centred on `anchor` (global, the toast's bottom centre).
func show_text(text: String, anchor: Vector2) -> void:
	label.text = text
	label.add_theme_font_size_override("font_size", roundi(FONT_SIZE * Settings.text_scale))
	reset_size()
	var sz := get_combined_minimum_size()
	global_position = (anchor - Vector2(sz.x * 0.5, sz.y)).floor()
	modulate.a = 1.0
	visible = true
	if _tween != null and _tween.is_valid():
		_tween.kill()
	if DisplayServer.get_name() == "headless":
		return  # stays up for tests to read; the next action replaces it
	_tween = create_tween()
	_tween.tween_interval(SHOW_SECONDS)
	if Fx.effects_enabled():
		_tween.tween_property(self, "modulate:a", 0.0, FADE_SECONDS)
	_tween.tween_callback(hide)


func _draw() -> void:
	var r := MARK_RADIUS * Settings.text_scale
	var c := Vector2(MARK_ROOM * 0.5, size.y * 0.5)
	draw_arc(c, r, 0, TAU, 20, Palette.CELL_PINK.darkened(0.2), 3.0, true)
	var d := Vector2(r, -r) * 0.7
	draw_line(c - d, c + d, Palette.CELL_PINK.darkened(0.2), 3.0, true)


func text() -> String:
	return label.text if visible else ""
