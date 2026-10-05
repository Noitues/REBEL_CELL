class_name VinylButton
extends Button
## ART-11 4D: a verb as a vinyl sticker you press (ART_BIBLE v2 §1.2 "buttons and verbs",
## §2.10: pink = the committing verb, yellow = the safe or back-out choice; a focused sticker
## gets a lime die-cut halo, never brackets). The words are the Button's own text (a key); 1B's
## VinylSticker letters them in upper case and follows the button's states (REST / HOVER /
## PRESSED / DISABLED); the Button draws no text itself. The button's rect is the sticker's
## body (its shadow pad takes no room). The screen decides what a press means (Signal Up).

var sticker: VinylSticker = null
var _hot: bool = false

## The halo round a focused or hovered sticker's body (px at 1.0) and its corner radius share.
const HALO := 4.0
const HALO_RADIUS_SHARE := 0.42


func _init(p_text: String = "", p_fill: VinylSticker.Fill = VinylSticker.Fill.PINK, p_step: int = UiTheme.TITLE) -> void:
	text = p_text
	flat = true
	clip_text = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		add_theme_color_override(key, Palette.AUTO)  # the sticker draws its own words
	sticker = VinylSticker.new()
	sticker.name = "Sticker"
	sticker.text = tr(p_text).to_upper()
	sticker.fill = p_fill
	sticker.font_step = p_step
	add_child(sticker)
	sticker.resized.connect(refit)
	mouse_entered.connect(_set_hot.bind(true))
	mouse_exited.connect(_set_hot.bind(false))
	focus_entered.connect(_set_hot.bind(true))
	focus_exited.connect(_set_hot.bind(false))
	button_down.connect(_sync_state)
	button_up.connect(_sync_state)
	KitState.track(self)


## Sizes the button to the sticker's body (once the sticker has built its art).
func refit() -> void:
	if sticker.body_rect.size == Vector2.ZERO:
		return
	custom_minimum_size = sticker.body_rect.size
	size = custom_minimum_size
	sticker.position = -sticker.body_rect.position
	queue_redraw()


func _set_hot(on: bool) -> void:
	_hot = on
	_sync_state()
	queue_redraw()


func _sync_state() -> void:
	if not sticker.is_inside_tree():
		return
	var s := VinylSticker.State.REST
	if disabled:
		s = VinylSticker.State.DISABLED
	elif button_pressed or is_pressed():
		s = VinylSticker.State.PRESSED
	elif _hot:
		s = VinylSticker.State.HOVER
	if sticker.state != s:
		sticker.set_state(s)


func _draw() -> void:
	if _hot and not disabled:
		var box := StyleBoxFlat.new()
		box.bg_color = Palette.FOCUS
		box.set_corner_radius_all(roundi(size.y * HALO_RADIUS_SHARE))
		draw_style_box(box, Rect2(Vector2.ZERO, size).grow(HALO * Settings.text_scale))
	KitState.draw_frame(self, Rect2(Vector2.ZERO, size), KitState.of(self), false)
