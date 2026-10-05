class_name SettingsPanel
extends Control
## Options (GDD 9.5, 9.6, STYLE_GUIDE 6): five sections on one zine panel. Accessibility
## (reduce effects, flash limiter, text scale, subtitles), Display (window mode,
## resolution, vsync, fps counter), Audio (master, music, SFX), Controls (rebind the
## combat keys; card keys stay 1-9), Language. Writes to the Settings autoload only.

signal closed

## H24 S3/S4: the section names and action labels are keys ("# TR"); the panel shows its
## words as given, translated where they are set.
const SECTIONS := ["Accessibility", "Display", "Audio", "Controls", "Language"] # TR
const ACTION_LABELS := {&"nudge_left": "Nudge anticlockwise", &"nudge_right": "Nudge clockwise", &"cycle_target": "Cycle target", # TR
	&"end_turn": "End turn", &"rewind": "Rewind", &"toggle_ring": "Nudge ring (outer / inner)", # TR
	&"toggle_nudge_wheel": "Nudge wheel (mine / target)", # TR
	&"respin": "Respin", &"open_settings": "Pause / options", # TR
	&"resolve_fast_forward": "Fast-forward the resolve (hold)"} # TR
## The window modes in words (keys).
const MODE_WORDS := ["Windowed", "Fullscreen", "Borderless"] # TR
## ART-0 C (art pass W9, ART_BIBLE §12, §10): the choices' words, in Settings' list orders
## (COLORBLIND_MODES, RESOLVE_SPEEDS, PAD_GLYPH_SETS). Keys.
const COLORBLIND_WORDS := ["Off (no correction)", "Deutan (green-weak)", "Protan (red-weak)", "Tritan (blue-weak)"] # TR
const RESOLVE_SPEED_WORDS := ["1x (full replay)", "2x (twice as fast)", "Instant (results at once)"] # TR
const GLYPH_WORDS := ["Automatic (match the pad)", "Xbox", "PlayStation", "Switch", "Steam Deck"] # TR
## The rows' words (keys).
const REDUCE_MOTION_WORDS := "Reduce motion (no camera moves or parallax; pages cross-fade)" # TR
const HIGH_CONTRAST_WORDS := "High contrast (opaque panels, 7:1 text, thick edges)" # TR
const COLORBLIND_HEADING := "Colour-blind correction (patterns and glyphs stay the main cue)" # TR
const RESOLVE_SPEED_HEADING := "Resolve speed after SEND IT (hold Fast-forward to speed it up)" # TR
const GLYPH_HEADING := "Pad button glyphs" # TR
## Every word the W9 rows add (tests check each has a strings.csv key and no mouse wording).
const W9_WORDS := COLORBLIND_WORDS + RESOLVE_SPEED_WORDS + GLYPH_WORDS + [REDUCE_MOTION_WORDS, HIGH_CONTRAST_WORDS,
	COLORBLIND_HEADING, RESOLVE_SPEED_HEADING, GLYPH_HEADING, "Fast-forward the resolve (hold)"]

## Set by a modal host (the pause menu): D-pad focus never leaves the panel.
## Why the last key pressed while rebinding was refused (Controls section).
var _bind_note: Label = null
## Width the refusal note wraps at.
const BIND_NOTE_WIDTH := 480.0
var _paper_panel: ZinePanel = null
var trap_focus: bool = false
var reduce_check: CheckButton
## ART-0 C (art pass W9): reduce motion and high contrast (Accessibility), the colour-blind
## correction and the resolve speed (Accessibility), the pad glyph set (Controls).
var reduce_motion_check: CheckButton
var high_contrast_check: CheckButton
var colorblind_option: OptionButton
var resolve_speed_option: OptionButton
var glyph_option: OptionButton
var flash_check: CheckButton
## ART-0 D11: the Heat glitch extra (off by default).
var heat_glitch_check: CheckButton
var subtitles_check: CheckButton
## Subtitles type in, or show whole at once (Animation pass ANIM-6).
var typing_check: CheckButton
var assist_check: CheckButton
var scale_slider: HSlider
var master_slider: HSlider
var music_slider: HSlider
var sfx_slider: HSlider
var mode_option: OptionButton
var resolution_option: OptionButton
var vsync_check: CheckButton
var fps_check: CheckButton
var legend_check: CheckButton
var log_check: CheckButton
var language_option: OptionButton
var close_button: Button
var section: String = "Accessibility"
## Action waiting for a key press (Controls section), or empty.
var rebinding: StringName = &""
var _body: VBoxContainer
var _tabs: HBoxContainer
var _key_buttons: Dictionary = {}
var _label_counter: int = 0


func _init() -> void:
	custom_minimum_size = Vector2(520, 360)
	TextDb.shown_as_given(self)
	var panel := ZinePanel.new(tr("OPTIONS"), 0.0, true)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	_paper_panel = panel
	# The panel grows with its section (inside the pause menu's scroll), never clipping it.
	panel.content.minimum_size_changed.connect(update_minimum_size)
	var box := VBoxContainer.new()
	panel.content.add_child(box)
	_tabs = HBoxContainer.new()
	box.add_child(_tabs)
	for name in SECTIONS:
		var b := Button.new()
		b.text = tr(name)
		var n: String = name
		b.pressed.connect(func() -> void: show_section(n))
		_tabs.add_child(b)
	_body = VBoxContainer.new()
	_body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	box.add_child(_body)
	# Widgets are built once so tests (and Settings.changed) can drive them by name.
	reduce_check = _check(tr("Reduce effects (no scanlines, flicker, chromatic, distortion)"), Settings.reduce_effects, Settings.set_reduce_effects)
	flash_check = _check(tr("Flash limiter (max 3 flashes per second)"), Settings.flash_limiter, Settings.set_flash_limiter)
	heat_glitch_check = _check(tr("Heat glitch (the screen distorts as Heat rises; off by default)"), Settings.heat_glitch, Settings.set_heat_glitch)
	heat_glitch_check.name = "HeatGlitchCheck"
	reduce_motion_check = _check(tr(REDUCE_MOTION_WORDS), Settings.reduce_motion, Settings.set_reduce_motion)
	reduce_motion_check.name = "ReduceMotionCheck"
	high_contrast_check = _check(tr(HIGH_CONTRAST_WORDS), Settings.high_contrast, Settings.set_high_contrast)
	high_contrast_check.name = "HighContrastCheck"
	colorblind_option = _choice("ColorblindOption", COLORBLIND_WORDS, Settings.COLORBLIND_MODES, Settings.colorblind_mode, Settings.set_colorblind_mode)
	resolve_speed_option = _choice("ResolveSpeedOption", RESOLVE_SPEED_WORDS, Settings.RESOLVE_SPEEDS, Settings.resolve_speed, Settings.set_resolve_speed)
	glyph_option = _choice("GlyphOption", GLYPH_WORDS, Settings.PAD_GLYPH_SETS, Settings.pad_glyph_set, Settings.set_pad_glyph_set)
	subtitles_check = _check(tr("Subtitles with speaker names"), Settings.subtitles, Settings.set_subtitles)
	typing_check = _check(tr("Subtitles type in (off: each line shows at once)"), Settings.subtitle_typing, Settings.set_subtitle_typing)
	typing_check.name = "TypingCheck"
	var cfg := RunManager.config()
	assist_check = _check(tr("Assist mode for new campaigns (%s free nudge a turn, %s%% HP; no ICE records or achievements)") % [TextDb.signed(cfg.assist_free_nudges), TextDb.signed(roundi((cfg.assist_hp_multiplier - 1.0) * 100.0))], Settings.assist_mode, Settings.set_assist_mode)
	assist_check.name = "AssistCheck"
	scale_slider = _slider("Text scale", Settings.TEXT_SCALE_MIN, Settings.TEXT_SCALE_MAX, 0.1, Settings.text_scale, Settings.set_text_scale)
	master_slider = _slider("Master volume", 0.0, 1.0, 0.05, Settings.master_volume, Settings.set_master_volume)
	music_slider = _slider("Music volume", 0.0, 1.0, 0.05, Settings.music_volume, Settings.set_music_volume)
	sfx_slider = _slider("SFX volume", 0.0, 1.0, 0.05, Settings.sfx_volume, Settings.set_sfx_volume)
	mode_option = OptionButton.new()
	for m in MODE_WORDS:
		mode_option.add_item(tr(m))
	mode_option.select(Settings.window_mode)
	mode_option.item_selected.connect(func(i: int) -> void: Settings.set_window_mode(i))
	resolution_option = OptionButton.new()
	for i in Settings.RESOLUTIONS.size():
		var r: Vector2i = Settings.RESOLUTIONS[i]
		resolution_option.add_item("%d x %d" % [r.x, r.y])
		if r == Settings.resolution:
			resolution_option.select(i)
	resolution_option.item_selected.connect(func(i: int) -> void: Settings.set_resolution(Settings.RESOLUTIONS[i]))
	vsync_check = _check(tr("V-sync"), Settings.vsync, Settings.set_vsync)
	fps_check = _check(tr("Show frame rate"), Settings.show_fps, Settings.set_show_fps)
	legend_check = _check(tr("Map legend on the city views"), Settings.map_legend, Settings.set_map_legend)
	legend_check.name = "LegendCheck"
	log_check = _check(tr("System log strip at the foot of the screen"), Settings.system_log, Settings.set_system_log)
	log_check.name = "LogCheck"
	language_option = OptionButton.new()
	var langs := Settings.available_languages()
	for i in langs.size():
		language_option.add_item(langs[i])
		if langs[i] == Settings.language:
			language_option.select(i)
	language_option.item_selected.connect(func(i: int) -> void: Settings.set_language(langs[i]))
	var close := Button.new()
	close.name = "Close"
	close_button = close
	close.pressed.connect(func() -> void: closed.emit())
	box.add_child(close)
	show_section("Accessibility")


func show_section(name: String) -> void:
	section = name
	rebinding = &""
	# ANIM-R4 C3: the built widgets wait off the tree for their section; everything else a
	# section made (its labels, the Controls grid, the note, Reset) goes (they leaked: 49
	# Controls per Options opened). Queued: Reset calls this from its own press.
	# ANIM-R6 D10: what goes stays in the tree, hidden, until its free (taken out and only
	# queued, it was an orphan node until the frame ended: 74 counted after one test).
	var keep := _persistent()
	for c in _body.get_children():
		if keep.has(c):
			_body.remove_child(c)
		elif not c.is_queued_for_deletion():
			(c as CanvasItem).hide()
			c.queue_free()
	_key_buttons.clear()
	match name:
		"Accessibility":
			for w in [reduce_check, reduce_motion_check, flash_check, heat_glitch_check, high_contrast_check, subtitles_check, typing_check, assist_check,
					_labelled(tr(COLORBLIND_HEADING)), colorblind_option, _labelled(tr(RESOLVE_SPEED_HEADING)), resolve_speed_option,
					_labelled(tr("Text scale")), scale_slider]:
				_body.add_child(w)
		"Display":
			for w in [_labelled(tr("Window mode")), mode_option, _labelled(tr("Resolution (windowed)")), resolution_option, vsync_check, fps_check, legend_check, log_check]:
				_body.add_child(w)
		"Audio":
			for w in [_labelled(tr("Master volume")), master_slider, _labelled(tr("Music volume")), music_slider, _labelled(tr("SFX volume")), sfx_slider]:
				_body.add_child(w)
		"Controls":
			_body.add_child(_labelled(tr(GLYPH_HEADING)))
			_body.add_child(glyph_option)
			_body.add_child(_labelled(tr("Click a key, then press the new one. Cards stay on 1-9.")))
			var grid := GridContainer.new()
			grid.columns = 4
			_body.add_child(grid)
			for action in Settings.REBINDABLE:
				var l := _labelled(tr(String(ACTION_LABELS.get(action, String(action)))))
				grid.add_child(l)
				var b := Button.new()
				b.text = _key_name(Settings.key_for(action))
				var a: StringName = action
				b.pressed.connect(func() -> void: begin_rebind(a))
				grid.add_child(b)
				_key_buttons[action] = b
			_bind_note = _labelled("")
			_bind_note.name = "BindNote"
			_bind_note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			_bind_note.custom_minimum_size.x = BIND_NOTE_WIDTH
			_body.add_child(_bind_note)
			var reset := Button.new()
			reset.text = tr("Reset to defaults")
			reset.pressed.connect(func() -> void: Settings.reset_keybinds(); show_section("Controls"))
			_body.add_child(reset)
		"Language":
			for w in [_labelled(tr("Language (translations from assets/text/strings.csv)")), language_option]:
				_body.add_child(w)
	UiWrap.fit(self)
	if trap_focus:
		UiFocus.trap(self)  # inside the pause menu: focus stays in the panel
	else:
		UiFocus.link_layout(self)  # the section swapped its controls
	UiFocus.focus_first(_body)


## The widgets built once in _init (they move between the body and off the tree).
func _persistent() -> Array[Control]:
	return [reduce_check, flash_check, heat_glitch_check, subtitles_check, typing_check, assist_check, scale_slider, master_slider, music_slider,
		sfx_slider, mode_option, resolution_option, vsync_check, fps_check, legend_check, log_check, language_option,
		reduce_motion_check, high_contrast_check, colorblind_option, resolve_speed_option, glyph_option]


## ANIM-R4 C3: the built widgets of the sections not showing are off the tree, so the
## panel's own free never reaches them: they go with it.
func _notification(what: int) -> void:
	if what == NOTIFICATION_PREDELETE:
		for w in _persistent():
			if w != null and is_instance_valid(w) and w.get_parent() == null:
				w.free()


func begin_rebind(action: StringName) -> void:
	rebinding = action
	if _key_buttons.has(action):
		_key_buttons[action].text = tr("press a key...")


## Feeds a key event to the rebinding (called from _unhandled_input and by tests).
func handle_key(event: InputEventKey) -> bool:
	if rebinding == &"" or not event.pressed:
		return false
	if event.physical_keycode == KEY_ESCAPE:
		rebinding = &""
		show_section("Controls")
		return true
	var err := Settings.bind_error(rebinding, event.physical_keycode)
	if err != "":
		# Keep waiting for another key, and say why this one was refused.
		for action in ACTION_LABELS:
			err = err.replace("used by %s" % String(action), "used by %s" % tr(String(ACTION_LABELS[action])))
		if _bind_note != null and is_instance_valid(_bind_note):
			_bind_note.text = tr("%s - press another key.") % err  # wraps: the grid never widens
		return true
	Settings.rebind(rebinding, event.physical_keycode)
	rebinding = &""
	show_section("Controls")
	return true


## While rebinding, the next key is the new bind, even an arrow key or Tab that GUI focus
## navigation would otherwise take first (H16).
func _input(event: InputEvent) -> void:
	if visible and event is InputEventKey and rebinding != &"":
		if handle_key(event):
			get_viewport().set_input_as_handled()


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if event is InputEventKey and rebinding != &"":
		return
	if event.is_action_pressed("ui_cancel"):
		closed.emit()
		get_viewport().set_input_as_handled()


static func _key_name(physical: int) -> String:
	return Settings.key_name(physical)


func _check(text: String, value: bool, setter: Callable) -> CheckButton:
	var c := CheckButton.new()
	c.text = text
	c.button_pressed = value
	c.add_theme_color_override("font_color", Palette.TERMINAL_TEXT)
	c.toggled.connect(func(on: bool) -> void: setter.call(on))
	return c


## ART-0 C: a choice row: `words[i]` (keys) for `values[i]`; picking one calls `setter`.
func _choice(node_name: String, words: Array, values: Array[StringName], current: StringName, setter: Callable) -> OptionButton:
	var o := OptionButton.new()
	o.name = node_name
	for w in words:
		o.add_item(tr(String(w)))
	o.select(maxi(0, values.find(current)))
	o.item_selected.connect(func(i: int) -> void: setter.call(values[i]))
	return o


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
	l.add_theme_color_override("font_color", Palette.TERMINAL_TEXT)
	return l


func _ready() -> void:
	Settings.hints_changed.connect(_relabel_close)
	_relabel_close()
	UiFocus.focus_first(self)


## "Close [Esc]" / "Close [B]": the hint follows the device and the binds (H20).
func _relabel_close() -> void:
	close_button.text = ("%s %s" % [tr("Close"), Settings.hint(&"ui_cancel")]).strip_edges()


## At least the content's size, so a host that scrolls can reach every control.
func _get_minimum_size() -> Vector2:
	if _paper_panel == null or _paper_panel.content == null:
		return Vector2.ZERO
	return _paper_panel.content.get_combined_minimum_size()
