class_name SettingsPanel
extends Control
## Options (GDD 9.5, 9.6, STYLE_GUIDE 6): five sections on one zine panel. Accessibility
## (reduce effects, flash limiter, text scale, subtitles), Display (window mode,
## resolution, vsync, fps counter), Audio (master, music, SFX), Controls (rebind the
## combat keys; card keys stay 1-9), Language. Writes to the Settings autoload only.

signal closed

const SECTIONS := ["Accessibility", "Display", "Audio", "Controls", "Language"]
const ACTION_LABELS := {&"nudge_left": "Nudge -1", &"nudge_right": "Nudge +1", &"cycle_target": "Cycle target",
	&"end_turn": "End turn", &"rewind": "Rewind", &"toggle_card_target": "Card target", &"toggle_ring": "Ring",
	&"toggle_nudge_wheel": "Nudge wheel", &"toggle_direction": "Card direction", &"cycle_slot": "Chosen slice",
	&"respin": "Respin", &"open_settings": "Pause / options"}

var reduce_check: CheckButton
var flash_check: CheckButton
var subtitles_check: CheckButton
var assist_check: CheckButton
var scale_slider: HSlider
var master_slider: HSlider
var music_slider: HSlider
var sfx_slider: HSlider
var mode_option: OptionButton
var resolution_option: OptionButton
var vsync_check: CheckButton
var fps_check: CheckButton
var language_option: OptionButton
var section: String = "Accessibility"
## Action waiting for a key press (Controls section), or empty.
var rebinding: StringName = &""
var _body: VBoxContainer
var _tabs: HBoxContainer
var _key_buttons: Dictionary = {}
var _label_counter: int = 0


func _init() -> void:
	custom_minimum_size = Vector2(520, 360)
	var panel := ZinePanel.new("OPTIONS", 0.0)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	var box := VBoxContainer.new()
	panel.content.add_child(box)
	_tabs = HBoxContainer.new()
	box.add_child(_tabs)
	for name in SECTIONS:
		var b := Button.new()
		b.text = name
		var n: String = name
		b.pressed.connect(func() -> void: show_section(n))
		_tabs.add_child(b)
	_body = VBoxContainer.new()
	_body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.add_child(_body)
	# Widgets are built once so tests (and Settings.changed) can drive them by name.
	reduce_check = _check("Reduce effects (no scanlines, flicker, chromatic, distortion)", Settings.reduce_effects, Settings.set_reduce_effects)
	flash_check = _check("Flash limiter (max 3 flashes per second)", Settings.flash_limiter, Settings.set_flash_limiter)
	subtitles_check = _check("Subtitles with speaker names", Settings.subtitles, Settings.set_subtitles)
	var cfg := RunManager.config()
	assist_check = _check("Assist mode for new campaigns (+%d free nudge a turn, +%d%% HP; no ICE records or achievements)" % [cfg.assist_free_nudges, roundi((cfg.assist_hp_multiplier - 1.0) * 100.0)], Settings.assist_mode, Settings.set_assist_mode)
	assist_check.name = "AssistCheck"
	scale_slider = _slider("Text scale", Settings.TEXT_SCALE_MIN, Settings.TEXT_SCALE_MAX, 0.1, Settings.text_scale, Settings.set_text_scale)
	master_slider = _slider("Master volume", 0.0, 1.0, 0.05, Settings.master_volume, Settings.set_master_volume)
	music_slider = _slider("Music volume", 0.0, 1.0, 0.05, Settings.music_volume, Settings.set_music_volume)
	sfx_slider = _slider("SFX volume", 0.0, 1.0, 0.05, Settings.sfx_volume, Settings.set_sfx_volume)
	mode_option = OptionButton.new()
	for m in ["Windowed", "Fullscreen", "Borderless"]:
		mode_option.add_item(m)
	mode_option.select(Settings.window_mode)
	mode_option.item_selected.connect(func(i: int) -> void: Settings.set_window_mode(i))
	resolution_option = OptionButton.new()
	for i in Settings.RESOLUTIONS.size():
		var r: Vector2i = Settings.RESOLUTIONS[i]
		resolution_option.add_item("%d x %d" % [r.x, r.y])
		if r == Settings.resolution:
			resolution_option.select(i)
	resolution_option.item_selected.connect(func(i: int) -> void: Settings.set_resolution(Settings.RESOLUTIONS[i]))
	vsync_check = _check("V-sync", Settings.vsync, Settings.set_vsync)
	fps_check = _check("Show frame rate", Settings.show_fps, Settings.set_show_fps)
	language_option = OptionButton.new()
	var langs := Settings.available_languages()
	for i in langs.size():
		language_option.add_item(langs[i])
		if langs[i] == Settings.language:
			language_option.select(i)
	language_option.item_selected.connect(func(i: int) -> void: Settings.set_language(langs[i]))
	var close := Button.new()
	close.text = "Close [Esc]"
	close.pressed.connect(func() -> void: closed.emit())
	box.add_child(close)
	show_section("Accessibility")


func show_section(name: String) -> void:
	section = name
	rebinding = &""
	for c in _body.get_children():
		_body.remove_child(c)
		if c is Label and c.name.begins_with("_tmp"):
			c.queue_free()
	_key_buttons.clear()
	match name:
		"Accessibility":
			for w in [reduce_check, flash_check, subtitles_check, assist_check, _labelled("Text scale"), scale_slider]:
				_body.add_child(w)
		"Display":
			for w in [_labelled("Window mode"), mode_option, _labelled("Resolution (windowed)"), resolution_option, vsync_check, fps_check]:
				_body.add_child(w)
		"Audio":
			for w in [_labelled("Master volume"), master_slider, _labelled("Music volume"), music_slider, _labelled("SFX volume"), sfx_slider]:
				_body.add_child(w)
		"Controls":
			_body.add_child(_labelled("Click a key, then press the new one. Cards stay on 1-9."))
			var grid := GridContainer.new()
			grid.columns = 4
			_body.add_child(grid)
			for action in Settings.REBINDABLE:
				var l := _labelled(ACTION_LABELS.get(action, String(action)))
				grid.add_child(l)
				var b := Button.new()
				b.text = _key_name(Settings.key_for(action))
				var a: StringName = action
				b.pressed.connect(func() -> void: begin_rebind(a))
				grid.add_child(b)
				_key_buttons[action] = b
			var reset := Button.new()
			reset.text = "Reset to defaults"
			reset.pressed.connect(func() -> void: Settings.reset_keybinds(); show_section("Controls"))
			_body.add_child(reset)
		"Language":
			for w in [_labelled("Language (translations from assets/text/strings.csv)"), language_option]:
				_body.add_child(w)
	UiFocus.link_layout(self)  # the section swapped its controls
	UiFocus.focus_first(_body)


func begin_rebind(action: StringName) -> void:
	rebinding = action
	if _key_buttons.has(action):
		_key_buttons[action].text = "press a key..."


## Feeds a key event to the rebinding (called from _unhandled_input and by tests).
func handle_key(event: InputEventKey) -> bool:
	if rebinding == &"" or not event.pressed:
		return false
	if event.physical_keycode == KEY_ESCAPE:
		rebinding = &""
		show_section("Controls")
		return true
	Settings.rebind(rebinding, event.physical_keycode)
	rebinding = &""
	show_section("Controls")
	return true


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventKey and rebinding != &"":
		if handle_key(event):
			get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("ui_cancel"):
		closed.emit()
		get_viewport().set_input_as_handled()


static func _key_name(physical: int) -> String:
	if physical <= 0:
		return "-"
	if DisplayServer.get_name() == "headless":
		return OS.get_keycode_string(physical)
	return OS.get_keycode_string(DisplayServer.keyboard_get_keycode_from_physical(physical))


func _check(text: String, value: bool, setter: Callable) -> CheckButton:
	var c := CheckButton.new()
	c.text = text
	c.button_pressed = value
	c.add_theme_color_override("font_color", Palette.INK)
	c.toggled.connect(func(on: bool) -> void: setter.call(on))
	return c


func _slider(text: String, lo: float, hi: float, step: float, value: float, setter: Callable) -> HSlider:
	var s := HSlider.new()
	s.name = text.replace(" ", "")
	s.min_value = lo
	s.max_value = hi
	s.step = step
	s.value = value
	s.custom_minimum_size = Vector2(300, 20)
	s.value_changed.connect(func(v: float) -> void: setter.call(v))
	return s


func _labelled(text: String) -> Label:
	var l := Label.new()
	_label_counter += 1
	l.name = "_tmp_%d" % _label_counter
	l.text = text
	l.add_theme_color_override("font_color", Palette.INK)
	return l


func _ready() -> void:
	UiFocus.focus_first(self)
