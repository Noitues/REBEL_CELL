class_name SettingsPanel
extends Control
## Accessibility settings (GDD 9.6, STYLE_GUIDE 6): reduce effects, flash limiter, text
## scale, subtitles, volumes. Writes to the Settings autoload only.

signal closed

var reduce_check: CheckButton
var flash_check: CheckButton
var subtitles_check: CheckButton
var scale_slider: HSlider
var music_slider: HSlider
var sfx_slider: HSlider


func _init() -> void:
	custom_minimum_size = Vector2(360, 300)
	var panel := ZinePanel.new("ACCESSIBILITY", 0.0)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	var box := VBoxContainer.new()
	panel.content.add_child(box)
	reduce_check = _check(box, "Reduce effects (no scanlines, flicker, chromatic, distortion)", Settings.reduce_effects, Settings.set_reduce_effects)
	flash_check = _check(box, "Flash limiter (max 3 flashes per second)", Settings.flash_limiter, Settings.set_flash_limiter)
	subtitles_check = _check(box, "Subtitles with speaker names", Settings.subtitles, Settings.set_subtitles)
	scale_slider = _slider(box, "Text scale", Settings.TEXT_SCALE_MIN, Settings.TEXT_SCALE_MAX, 0.1, Settings.text_scale, Settings.set_text_scale)
	music_slider = _slider(box, "Music volume", 0.0, 1.0, 0.05, Settings.music_volume, Settings.set_music_volume)
	sfx_slider = _slider(box, "SFX volume", 0.0, 1.0, 0.05, Settings.sfx_volume, Settings.set_sfx_volume)
	var close := Button.new()
	close.text = "Close [Esc]"
	close.pressed.connect(func() -> void: closed.emit())
	box.add_child(close)


func _check(box: VBoxContainer, text: String, value: bool, setter: Callable) -> CheckButton:
	var c := CheckButton.new()
	c.text = text
	c.button_pressed = value
	c.add_theme_color_override("font_color", Palette.INK)
	c.toggled.connect(func(on: bool) -> void: setter.call(on))
	box.add_child(c)
	return c


func _slider(box: VBoxContainer, text: String, lo: float, hi: float, step: float, value: float, setter: Callable) -> HSlider:
	var l := Label.new()
	l.text = text
	l.add_theme_color_override("font_color", Palette.INK)
	box.add_child(l)
	var s := HSlider.new()
	s.min_value = lo
	s.max_value = hi
	s.step = step
	s.value = value
	s.custom_minimum_size = Vector2(300, 20)
	s.value_changed.connect(func(v: float) -> void: setter.call(v))
	box.add_child(s)
	return s


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		closed.emit()
		get_viewport().set_input_as_handled()
