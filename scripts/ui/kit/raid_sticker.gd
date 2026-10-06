class_name RaidSticker
extends Button
## ART-6 3A: a vinyl sticker word on the raid (ART_BIBLE v2 §1.2 "Vinyl sticker"): the things
## that never change (START DEFENSE, CELL HOLDS, BACK TO THE GRID), on 1B's VinylSticker
## (Anton lettering, ink keyline, extrude, white die-cut, gloss and its one sweep; slap, peel).
## As a button it presses like any other (the scene decides what a press means; focus shows
## the lime brackets, §2.10); as a stamp (`stamp_only`) it takes no input. The button is the
## sticker's body; the vinyl's shadow room spills outside it.

const PINK := &"pink"
const YELLOW := &"yellow"
## Room round the body (px) so the die-cut never touches the button's edge.
const ROOM := 2.0

var step: int = UiTheme.HEADING
var fill: StringName = PINK
var tilt_deg: float = -2.0
var vinyl: VinylSticker


func _init(p_text: String = "", p_step: int = UiTheme.HEADING, p_fill: StringName = PINK, p_tilt: float = -2.0) -> void:
	text = p_text
	step = p_step
	fill = p_fill
	tilt_deg = p_tilt
	flat = true
	clip_text = true
	focus_mode = Control.FOCUS_ALL
	add_theme_stylebox_override("focus", StyleBoxEmpty.new())  # focus = the vinyl's rainbow sheen and curl, no brackets
	for key in ["normal", "hover", "pressed", "disabled", "hover_pressed"]:
		add_theme_stylebox_override(key, StyleBoxEmpty.new())
	for key in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color", "font_disabled_color"]:
		add_theme_color_override(key, Palette.AUTO)
	vinyl = VinylSticker.new()
	vinyl.name = "Vinyl"
	vinyl.shape = VinylSticker.Shape.WORD
	vinyl.fill = VinylSticker.Fill.YELLOW if p_fill == YELLOW else VinylSticker.Fill.PINK
	vinyl.font_step = p_step
	vinyl.tilt_deg = p_tilt
	vinyl.rotation_degrees = p_tilt
	vinyl.text = shown_text()
	vinyl.seed = absi(p_text.hash()) % 997
	add_child(vinyl, false, Node.INTERNAL_MODE_FRONT)
	mouse_entered.connect(_state)
	mouse_exited.connect(_state)
	focus_entered.connect(_state)
	focus_exited.connect(_state)
	_fit()


func _ready() -> void:
	# In the tree its page's translate mode is known: the vinyl shows the word as the button would.
	if vinyl.text != shown_text():
		vinyl.text = shown_text()
	_fit.call_deferred()


## A sticker that takes no input (CELL HOLDS on the report).
func stamp_only() -> RaidSticker:
	focus_mode = Control.FOCUS_NONE
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	return self


## The word as drawn (translated, as a Button shows it).
func shown_text() -> String:
	return (atr(text) if can_auto_translate() else text).to_upper()


## The sticker's body size (the vinyl's, once built; an estimate before).
func body_size() -> Vector2:
	if vinyl != null and vinyl.body_rect.has_area():
		return vinyl.body_rect.size
	var f := Palette.display()
	var px := UiTheme.font_px(step)
	return f.get_string_size(shown_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, px) + Vector2(px, px) * 0.9


func _fit() -> void:
	custom_minimum_size = body_size() + Vector2(ROOM, ROOM) * 2.0
	_place()


func _place() -> void:
	if vinyl == null:
		return
	vinyl.position = size * 0.5 - vinyl.pivot_offset
	pivot_offset = size * 0.5


func _notification(what: int) -> void:
	if what == NOTIFICATION_TRANSLATION_CHANGED and vinyl != null:
		vinyl.text = shown_text()
		_fit.call_deferred()
	elif what == NOTIFICATION_RESIZED:
		_place()


func _state() -> void:
	if vinyl == null:
		return
	if disabled:
		vinyl.set_state(VinylSticker.State.DISABLED)
	elif is_hovered() or has_focus():
		vinyl.set_state(VinylSticker.State.HOVER)
	else:
		vinyl.set_state(VinylSticker.State.REST)


## The vinyl slaps on (`sticker_slap`; at rest at once when motion doesn't play).
func slap() -> float:
	return vinyl.slap() if vinyl != null else 0.0


## B3 (review Q7): the raid's result motion, moved off the map's banner onto CELL HOLDS.
const RESULT_MOTION := &"raid_result_banner"


## B3 (review Q7): CELL HOLDS lands as the raid's result on the after-action paper: after
## `raid_result_banner`'s delay it stamps down from the entry's amplitude (x its size) over its
## duration while the vinyl slaps on (`sticker_slap`). At rest at once when motion doesn't play
## (reduce effects, headless). Returns the seconds it takes.
func slap_result() -> float:
	if not Motion.live(RESULT_MOTION):
		Motion.run(RESULT_MOTION, self, ^"scale", Vector2.ONE)
		return slap()
	pivot_offset = size * 0.5
	scale = Vector2.ONE * maxf(1.0, Motion.amplitude(RESULT_MOTION))
	Motion.run(RESULT_MOTION, self, ^"scale", Vector2.ONE)
	return maxf(Motion.delay_of(RESULT_MOTION) + Motion.seconds(RESULT_MOTION), slap())


## The vinyl peels away (`sticker_peel`); the button hides once it is gone.
func peel() -> float:
	if vinyl == null:
		return 0.0
	var d := vinyl.peel()
	vinyl.motion_finished.connect(func(_kind: StringName) -> void: visible = false, CONNECT_ONE_SHOT)
	if d <= 0.0:
		visible = false
	return d
