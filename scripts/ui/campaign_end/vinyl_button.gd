class_name VinylButton
extends Button
## ART-11 4D: a verb as a vinyl sticker you press (ART_BIBLE v2 §1.2 "buttons and verbs",
## §2.10: pink = the committing verb, yellow = the safe or back-out choice; a focused sticker
## gets a lime die-cut halo, never brackets). The words are the Button's own text (a key), drawn
## in upper case by a VinylWord; the Button draws none itself. A seam for 1B's vinyl material.
## The screen decides what a press means (Signal Up).

var sticker: VinylWord = null
var _hot: bool = false

## The halo round a focused or hovered sticker (px at 1.0).
const HALO := 4.0


func _init(p_text: String = "", p_fill: Array[Color] = Palette.END_VINYL_PINK, p_font_size: int = UiTheme.TITLE) -> void:
	text = p_text
	flat = true
	clip_text = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		add_theme_color_override(key, Palette.AUTO)  # the sticker draws its own words
	sticker = VinylWord.new(tr(p_text).to_upper(), p_fill, p_font_size)
	sticker.pre_translated = true
	sticker.name = "Sticker"
	add_child(sticker)
	mouse_entered.connect(_set_hot.bind(true))
	mouse_exited.connect(_set_hot.bind(false))
	focus_entered.connect(_set_hot.bind(true))
	focus_exited.connect(_set_hot.bind(false))
	KitState.track(self)
	refit()


## Re-measures after a text-size change.
func refit() -> void:
	sticker.refit()
	custom_minimum_size = sticker.custom_minimum_size
	size = custom_minimum_size
	sticker.position = Vector2.ZERO


func _set_hot(on: bool) -> void:
	_hot = on
	queue_redraw()


func _process(_delta: float) -> void:
	# ART-0 F (§6): hover lifts the sticker, a press drops it.
	var lift := KitState.lift(KitState.of(self))
	if not is_equal_approx(sticker.position.y, lift):
		sticker.position.y = lift


func _draw() -> void:
	if _hot and not disabled:
		var poly := sticker.plate_polygon()
		var grown := Geometry2D.offset_polygon(poly, HALO * Settings.text_scale)
		for g: PackedVector2Array in grown:
			draw_colored_polygon(g, Palette.FOCUS)
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), KitState.of(self), false)
