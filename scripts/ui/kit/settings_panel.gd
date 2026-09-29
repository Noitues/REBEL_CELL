class_name SettingsPanel
extends Control
## Options (GDD 9.5, 9.6, STYLE_GUIDE 6; ART_BIBLE §11 Options, §6.5; art pass W8a): one
## GLASS panel with five tabs, Accessibility (reduce effects, reduce motion, flash limiter,
## high contrast, subtitles, assist, text scale with a live preview, colour-blind
## correction, resolve speed), Display (window mode, resolution, vsync, frame rate, map
## legend, system log), Audio (master, music, SFX), Controls (rebind the combat keys, cards
## stay 1-9; pad glyphs) and Language. Every control is a kit component, never a native OS
## widget: pickers are TilePickers, switches are ZineToggles beside their labels (each
## section's switches aligned 16 px right of its longest label), sliders are ZineSliders
## with a value readout ("1.6×"). Every section is built once and the panel keeps **one
## size across its tabs** (the largest section's); taller content scrolls inside it (§5.3).
## A pad reads the prompt bar (the host's, or this panel's own with `own_prompts`), never
## "Close [B]". Writes to the Settings autoload only.

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
## Art pass W9 (ART_BIBLE §12, §10), as tiles (W8a: a short name and a meta line, so a
## tile never cuts its words): in Settings' list orders (COLORBLIND_MODES, RESOLVE_SPEEDS,
## PAD_GLYPH_SETS). Keys in assets/text/strings.csv.
const COLORBLIND_TILES := [["Off", "no correction"], ["Deutan", "green-weak"], ["Protan", "red-weak"], ["Tritan", "blue-weak"]] # TR
const RESOLVE_SPEED_TILES := [["1x", "full replay"], ["2x", "twice as fast"], ["Instant", "results at once"]] # TR
const GLYPH_TILES := [["Automatic", "match the pad"], ["Xbox", ""], ["PlayStation", ""], ["Switch", ""], ["Steam Deck", ""]] # TR
## The switches and sliders: [short label, what it does] (keys).
const TOGGLE_WORDS := {
	&"reduce": ["Reduce effects", "No scanlines, flicker, chromatic or distortion."], # TR
	&"motion": ["Reduce motion", "No camera moves or parallax; pages cross-fade."], # TR
	&"flash": ["Flash limiter", "At most 3 flashes a second."], # TR
	&"contrast": ["High contrast", "Opaque panels, 7:1 text and thick edges."], # TR
	&"subtitles": ["Subtitles", "Every spoken line, with the speaker's name."], # TR
	&"typing": ["Subtitles type in", "Off: each line shows at once."], # TR
	&"assist": ["Assist mode", "For new campaigns: %s free nudge a turn, %s%% HP. No ICE records or achievements."], # TR
	&"vsync": ["V-sync", "Frames wait for the screen (no tearing)."], # TR
	&"fps": ["Frame rate", "Shows frames per second in a corner."], # TR
	&"legend": ["Map legend", "The key on the city views."], # TR
	&"log": ["System log", "A strip of system lines at the foot of the screen."], # TR
} # TR
## The rows' headings (keys).
const HEADINGS := ["Text scale", "Colour-blind correction", "Resolve speed after SEND IT", "Window mode", "Resolution (windowed)", # TR
	"Master volume", "Music volume", "SFX volume", "Pad button glyphs", "Language", # TR
	"Choose an action, then press its new key. Cards stay on 1-9.", "Reset to defaults", "Close", # TR
	"Patterns and glyphs stay the main cue.", "Hold Fast-forward to speed a resolve up.", # TR
	"The Cell never sleeps. Every word on every page grows with this."] # TR
## Every W9 word (tests check each has a strings.csv key and no mouse wording).
const W9_WORDS := ["Off", "Deutan", "Protan", "Tritan", "no correction", "green-weak", "red-weak", "blue-weak", "1x", "2x", "Instant",
	"Automatic", "match the pad", "Xbox", "PlayStation", "Switch", "Steam Deck", "Reduce motion", "High contrast",
	"Colour-blind correction", "Resolve speed after SEND IT", "Pad button glyphs", "Fast-forward the resolve (hold)"]

## The panel's width at text scale 1.0 (px; it grows with the text up to the room it has).
const PANEL_W := 720.0
## The room the scroll bar takes at the content's right (px).
const SCROLL_ROOM := UiTheme.SP_M
## The key column of the Controls grid, as characters of the mono face.
const KEY_CHARS := 12

## Set by a modal host (the pause menu): D-pad focus never leaves the panel.
var trap_focus: bool = false
## Why the last key pressed while rebinding was refused (Controls section).
var _bind_note: Label = null
var _paper_panel: ZinePanel = null
var reduce_check: ZineToggle
var flash_check: ZineToggle
var subtitles_check: ZineToggle
## Subtitles type in, or show whole at once (Animation pass ANIM-6).
var typing_check: ZineToggle
var assist_check: ZineToggle
var scale_slider: ZineSlider
var master_slider: ZineSlider
var music_slider: ZineSlider
var sfx_slider: ZineSlider
var mode_option: TilePicker
var resolution_option: TilePicker
var vsync_check: ZineToggle
var fps_check: ZineToggle
var legend_check: ZineToggle
var log_check: ZineToggle
var language_option: TilePicker
## W9 rows: colour-blind correction, high contrast, reduce motion, resolve speed (all in
## Accessibility) and the pad glyph set (Controls).
var colorblind_option: TilePicker
var high_contrast_check: ZineToggle
var reduce_motion_check: ZineToggle
var resolve_speed_option: TilePicker
var glyph_option: TilePicker
## The text-scale sample under the slider (§11 Options: a live preview).
var text_preview: Label
var close_button: Button
## The pad's prompt bar inside the panel (shown only with `own_prompts`, a host without one).
var prompts: PadPrompts
## True when the panel shows its own prompt bar (the pause menu); the title has its own.
var own_prompts: bool = false:
	set(v):
		own_prompts = v
		_relabel_close()
var section: String = "Accessibility"
## Action waiting for a key press (Controls section), or empty.
var rebinding: StringName = &""
## The section boxes by name (all built once; one shows).
var sections: Dictionary = {}
var tab_buttons: Dictionary = {}
var _body: VBoxContainer
var _fit: FitScroll
var _tabs: HFlowContainer
var _tab_group: ButtonGroup
var _key_buttons: Dictionary = {}
var _key_grid: GridContainer
var _descriptions: Array[Label] = []
var _toggle_groups: Array = []
var _pickers: Array[TilePicker] = []
var _max_height: float = 0.0
var _max_width: float = 0.0
var _built_scale: float = -1.0


func _init() -> void:
	name = "SettingsPanel"
	TextDb.shown_as_given(self)
	var panel := ZinePanel.new(tr("OPTIONS"), 0.0, true)
	panel.name = "Glass"
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	_paper_panel = panel
	# The panel grows with its content (inside the pause menu's scroll), never clipping it.
	panel.content.minimum_size_changed.connect(update_minimum_size)
	var box := VBoxContainer.new()
	box.name = "Box"
	box.add_theme_constant_override("separation", UiTheme.SP_S)
	panel.content.add_child(box)
	# GLASS tabs: one pressed (a ButtonGroup), Secondary buttons.
	_tabs = HFlowContainer.new()
	_tabs.name = "Tabs"
	_tabs.add_theme_constant_override("h_separation", UiTheme.SP_XS)
	_tabs.add_theme_constant_override("v_separation", UiTheme.SP_XS)
	box.add_child(_tabs)
	_tab_group = ButtonGroup.new()
	for n in SECTIONS:
		var b := Button.new()
		b.name = "Tab_%s" % n
		b.text = tr(n)
		b.toggle_mode = true
		b.button_group = _tab_group
		b.theme_type_variation = UiTheme.SECONDARY
		CodexSpread.tab_marker(b)
		var sn: String = n
		b.pressed.connect(func() -> void: show_section(sn))
		_tabs.add_child(b)
		tab_buttons[n] = b
	_body = VBoxContainer.new()
	_body.name = "Sections"
	# Room at the sides for a focused control's pad scale (1.03) inside the scrolling view.
	var pad_room := MarginContainer.new()
	pad_room.name = "PadRoom"
	for side in ["margin_left", "margin_right"]:
		pad_room.add_theme_constant_override(side, UiTheme.SP_S)
	pad_room.add_child(_body)
	_fit = FitScroll.new(pad_room, 0.0)
	_fit.name = "SectionScroll"
	box.add_child(_fit)
	_build_widgets()
	for n in SECTIONS:
		var s := VBoxContainer.new()
		s.name = "Section_%s" % n
		s.add_theme_constant_override("separation", UiTheme.SP_S)
		s.visible = false
		_body.add_child(s)
		sections[n] = s
	_fill_sections()
	var foot := HBoxContainer.new()
	foot.name = "Foot"
	box.add_child(foot)
	close_button = Button.new()
	close_button.name = "Close"
	close_button.theme_type_variation = UiTheme.SECONDARY
	close_button.pressed.connect(func() -> void: closed.emit())
	IconMark.attach(close_button, StatIcon.CLOSE)
	foot.add_child(close_button)
	prompts = PadPrompts.new()
	prompts.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	foot.add_child(prompts)
	show_section("Accessibility")


func _build_widgets() -> void:
	var cfg := RunManager.config()
	reduce_check = _toggle(&"reduce", "ReduceCheck", Settings.reduce_effects, Settings.set_reduce_effects)
	reduce_motion_check = _toggle(&"motion", "ReduceMotionCheck", Settings.reduce_motion, Settings.set_reduce_motion)
	flash_check = _toggle(&"flash", "FlashCheck", Settings.flash_limiter, Settings.set_flash_limiter)
	high_contrast_check = _toggle(&"contrast", "HighContrastCheck", Settings.high_contrast, Settings.set_high_contrast)
	subtitles_check = _toggle(&"subtitles", "SubtitlesCheck", Settings.subtitles, Settings.set_subtitles)
	typing_check = _toggle(&"typing", "TypingCheck", Settings.subtitle_typing, Settings.set_subtitle_typing)
	assist_check = _toggle(&"assist", "AssistCheck", Settings.assist_mode, Settings.set_assist_mode,
		[TextDb.signed(cfg.assist_free_nudges), TextDb.signed(roundi((cfg.assist_hp_multiplier - 1.0) * 100.0))])
	vsync_check = _toggle(&"vsync", "VsyncCheck", Settings.vsync, Settings.set_vsync)
	fps_check = _toggle(&"fps", "FpsCheck", Settings.show_fps, Settings.set_show_fps)
	legend_check = _toggle(&"legend", "LegendCheck", Settings.map_legend, Settings.set_map_legend)
	log_check = _toggle(&"log", "LogCheck", Settings.system_log, Settings.set_system_log)
	scale_slider = _slider("TextScale", Settings.TEXT_SCALE_MIN, Settings.TEXT_SCALE_MAX, 0.1, Settings.text_scale, Settings.set_text_scale,
		func(v: float) -> String: return "%s×" % String.num(v, 1))
	scale_slider.value_changed.connect(_preview_scale)
	var percent := func(v: float) -> String: return "%d%%" % roundi(v * 100.0)
	master_slider = _slider("MasterVolume", 0.0, 1.0, 0.05, Settings.master_volume, Settings.set_master_volume, percent)
	music_slider = _slider("MusicVolume", 0.0, 1.0, 0.05, Settings.music_volume, Settings.set_music_volume, percent)
	sfx_slider = _slider("SFXVolume", 0.0, 1.0, 0.05, Settings.sfx_volume, Settings.set_sfx_volume, percent)
	text_preview = Label.new()
	text_preview.name = "TextPreview"
	text_preview.text = tr("The Cell never sleeps. Every word on every page grows with this.")
	text_preview.add_theme_color_override("font_color", Palette.TEXT_HI)
	text_preview.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_preview_scale(Settings.text_scale)
	var modes: Array[Dictionary] = []
	for m in MODE_WORDS:
		modes.append({"name": tr(m)})
	mode_option = _picker("ModeOption", modes, Settings.window_mode, func(i: int) -> void: Settings.set_window_mode(i))
	var res: Array[Dictionary] = []
	var res_at := 0
	for i in Settings.RESOLUTIONS.size():
		var r: Vector2i = Settings.RESOLUTIONS[i]
		res.append({"name": "%d × %d" % [r.x, r.y]})
		if r == Settings.resolution:
			res_at = i
	resolution_option = _picker("ResolutionOption", res, res_at, func(i: int) -> void: Settings.set_resolution(Settings.RESOLUTIONS[i]))
	var langs := Settings.available_languages()
	var lang_tiles: Array[Dictionary] = []
	for l in langs:
		lang_tiles.append({"name": TranslationServer.get_locale_name(l), "meta": l})
	language_option = _picker("LanguageOption", lang_tiles, maxi(0, langs.find(Settings.language)), func(i: int) -> void: Settings.set_language(langs[i]))
	colorblind_option = _choice("ColorblindOption", COLORBLIND_TILES, Settings.COLORBLIND_MODES, Settings.colorblind_mode, Settings.set_colorblind_mode)
	resolve_speed_option = _choice("ResolveSpeedOption", RESOLVE_SPEED_TILES, Settings.RESOLVE_SPEEDS, Settings.resolve_speed, Settings.set_resolve_speed)
	glyph_option = _choice("GlyphOption", GLYPH_TILES, Settings.PAD_GLYPH_SETS, Settings.pad_glyph_set, Settings.set_pad_glyph_set)


func _fill_sections() -> void:
	var a: VBoxContainer = sections["Accessibility"]
	var acc_toggles := [reduce_check, reduce_motion_check, flash_check, high_contrast_check, subtitles_check, typing_check, assist_check]
	for t in acc_toggles:
		_add_toggle_row(a, t)
	_toggle_groups.append(acc_toggles)
	a.add_child(_heading(tr("Text scale")))
	a.add_child(scale_slider)
	a.add_child(_preview_box())
	a.add_child(_heading(tr("Colour-blind correction"), tr("Patterns and glyphs stay the main cue.")))
	a.add_child(colorblind_option)
	a.add_child(_heading(tr("Resolve speed after SEND IT"), tr("Hold Fast-forward to speed a resolve up.")))
	a.add_child(resolve_speed_option)
	var d: VBoxContainer = sections["Display"]
	d.add_child(_heading(tr("Window mode")))
	d.add_child(mode_option)
	d.add_child(_heading(tr("Resolution (windowed)")))
	d.add_child(resolution_option)
	var disp_toggles := [vsync_check, fps_check, legend_check, log_check]
	for t in disp_toggles:
		_add_toggle_row(d, t)
	_toggle_groups.append(disp_toggles)
	var au: VBoxContainer = sections["Audio"]
	for pair in [["Master volume", master_slider], ["Music volume", music_slider], ["SFX volume", sfx_slider]]:
		au.add_child(_heading(tr(pair[0])))
		au.add_child(pair[1])
	var c: VBoxContainer = sections["Controls"]
	c.add_child(_description(tr("Choose an action, then press its new key. Cards stay on 1-9.")))
	_key_grid = GridContainer.new()
	_key_grid.name = "Keys"
	_key_grid.add_theme_constant_override("h_separation", UiTheme.SP_M)
	_key_grid.add_theme_constant_override("v_separation", UiTheme.SP_XS)
	c.add_child(_key_grid)
	for action in Settings.REBINDABLE:
		var l := Label.new()
		l.name = "Label_%s" % String(action)
		l.text = tr(String(ACTION_LABELS.get(action, String(action))))
		l.add_theme_color_override("font_color", Palette.TEXT_HI)
		_key_grid.add_child(l)
		var b := Button.new()
		b.name = "Key_%s" % String(action)
		b.theme_type_variation = UiTheme.SECONDARY
		var act: StringName = action
		b.pressed.connect(func() -> void: begin_rebind(act))
		_key_grid.add_child(b)
		_key_buttons[action] = b
	_bind_note = _description("")
	_bind_note.name = "BindNote"
	_bind_note.add_theme_color_override("font_color", Palette.WARN)
	c.add_child(_bind_note)
	c.add_child(_heading(tr("Pad button glyphs")))
	c.add_child(glyph_option)
	var reset := Button.new()
	reset.name = "Reset"
	reset.text = tr("Reset to defaults")
	reset.theme_type_variation = UiTheme.SECONDARY
	reset.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	reset.pressed.connect(func() -> void:
		Settings.reset_keybinds()
		_relabel_keys())
	c.add_child(reset)
	_relabel_keys()
	var lg: VBoxContainer = sections["Language"]
	lg.add_child(_heading(tr("Language")))
	lg.add_child(language_option)


## Shows section `name` (its tab pressed); the panel keeps its size.
func show_section(name_key: String) -> void:
	if not sections.has(name_key):
		return
	section = name_key
	if rebinding != &"":
		rebinding = &""
		_relabel_keys()
	for n in sections:
		(sections[n] as Control).visible = n == name_key
		(tab_buttons[n] as Button).set_pressed_no_signal(n == name_key)
		CodexSpread.show_tab(tab_buttons[n] as Button, n == name_key)
	if _bind_note != null:
		_bind_note.text = ""
	UiWrap.fit(self)
	if trap_focus:
		UiFocus.trap(self)  # inside the pause menu: focus stays in the panel
	else:
		UiFocus.link_layout(self)  # the section swapped its controls
	UiFocus.focus_first(sections[name_key])


## Caps the panel: its section scrolls past `max_height` px (0 = no cap), and it is at most
## `max_width` px wide (0 = the screen less its safe margins). Returns the panel.
func fit_room(max_height: float, max_width: float = 0.0) -> SettingsPanel:
	_max_height = max_height
	_max_width = max_width
	if is_inside_tree():
		_relayout()
	return self


## The panel's width now (px): PANEL_W grown with the text, within the room it has.
func panel_width() -> float:
	var room := _max_width
	if room <= 0.0:
		room = (get_viewport_rect().size.x if is_inside_tree() else float(ProjectSettings.get_setting("display/window/size/viewport_width", 1280))) - UiTheme.SAFE_MARGIN * 2
	return minf(PANEL_W * Settings.text_scale, room)


## The width inside the glass the sections lay out in (px).
func content_width() -> float:
	return panel_width() - UiTheme.PANEL_PAD_H * 2 - SCROLL_ROOM - UiTheme.SP_S * 2


## The size every tab shows at (the largest section's, px).
func section_size() -> Vector2:
	var out := Vector2.ZERO
	for n in sections:
		var s := sections[n] as Control
		var was := s.visible
		s.visible = true
		out = out.max(s.get_combined_minimum_size())
		s.visible = was
	return out


func _notification(what: int) -> void:
	if what == NOTIFICATION_READY:
		_relayout()
	elif what == NOTIFICATION_THEME_CHANGED:
		_relayout.call_deferred()


## Sizes everything for the text scale and the room: the descriptions wrap at the content
## width, the pickers reflow their columns, the toggles align per section, the Controls grid
## takes 4 or 2 columns, and the sections share the largest one's size.
func _relayout() -> void:
	if not is_inside_tree():
		return
	_built_scale = Settings.text_scale
	var w := content_width()
	# A wrapped line knows its height only at its width: every wrapped label takes the
	# content width now (a section not shown yet is measured at it, never at width 0).
	for l in _descriptions:
		l.custom_minimum_size.x = w
		l.size.x = w
	text_preview.custom_minimum_size.x = w - UiTheme.PANEL_PAD_H * 2
	text_preview.size.x = text_preview.custom_minimum_size.x
	for group in _toggle_groups:
		for t in group:
			(t as ZineToggle).update_minimum_size()
		ZineToggle.align_group(group)
	var tile := TilePicker.TILE_W * Settings.text_scale + TilePicker.TILE_GAP
	for p in _pickers:
		p.columns = clampi(int((w + TilePicker.TILE_GAP) / tile), 1, maxi(1, p.tiles.size()))
		p.update_minimum_size()
		p.queue_redraw()
	for s in [scale_slider, master_slider, music_slider, sfx_slider]:
		s.custom_minimum_size.x = minf(w, ZineSlider.TRACK_MIN_W * 2.0 * Settings.text_scale)
		s.update_minimum_size()
	_key_grid.columns = 4 if _controls_two_pairs_fit(w) else 2
	_body.custom_minimum_size = Vector2(w, 0)
	_body.custom_minimum_size = section_size()
	# The cap is the whole panel's: the section's view gets what the tabs, the foot and the
	# glass's own title and margins leave.
	if _max_height > 0.0:
		var chrome := _paper_panel.get_combined_minimum_size().y - _fit.get_combined_minimum_size().y
		# The MORE BELOW hint's own room under the view (ScrollHint keeps it while it scrolls).
		var hint_room := _fit.hint.get_combined_minimum_size().y + ScrollHint.MARGIN.y * 2.0 + UiTheme.SP_S
		_fit.max_height = maxf(FitScroll.MIN_VIEW * Settings.text_scale, _max_height - chrome - hint_room)
		_trim.call_deferred()
	else:
		_fit.max_height = 0.0
	custom_minimum_size.x = panel_width()
	update_minimum_size()


## Once the hint's room has settled (its row snap), the view gives back whatever still
## pushes the panel past its cap. It only ever shrinks, so it settles.
func _trim() -> void:
	if _max_height <= 0.0 or not is_inside_tree():
		return
	var over := _paper_panel.get_combined_minimum_size().y - _max_height
	if over > 0.5 and _fit.max_height - over >= FitScroll.MIN_VIEW * Settings.text_scale:
		_fit.max_height -= ceilf(over)


func _controls_two_pairs_fit(w: float) -> bool:
	var px := UiTheme.font_px(UiTheme.BODY)
	var widest := 0.0
	for a in ACTION_LABELS:
		widest = maxf(widest, Palette.mono().get_string_size(tr(String(ACTION_LABELS[a])), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x)
	var key := Palette.mono().get_string_size("M".repeat(KEY_CHARS), HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	return (widest + key + UiTheme.SP_M * 2) * 2.0 <= w


func begin_rebind(action: StringName) -> void:
	rebinding = action
	if _key_buttons.has(action):
		_key_buttons[action].text = tr("press a key...")


## Feeds a key event to the rebinding (called from _input and by tests).
func handle_key(event: InputEventKey) -> bool:
	if rebinding == &"" or not event.pressed:
		return false
	if event.physical_keycode == KEY_ESCAPE:
		rebinding = &""
		_relabel_keys()
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
	_relabel_keys()
	if _bind_note != null:
		_bind_note.text = ""
	return true


func _relabel_keys() -> void:
	for action in _key_buttons:
		(_key_buttons[action] as Button).text = _key_name(Settings.key_for(action))


## While rebinding, the next key is the new bind, even an arrow key or Tab that GUI focus
## navigation would otherwise take first (H16).
func _input(event: InputEvent) -> void:
	if visible and event is InputEventKey and rebinding != &"":
		if handle_key(event):
			get_viewport().set_input_as_handled()


func _unhandled_input(event: InputEvent) -> void:
	if not is_visible_in_tree():
		return
	if event is InputEventKey and rebinding != &"":
		return
	if event.is_action_pressed("ui_cancel"):
		closed.emit()
		get_viewport().set_input_as_handled()


static func _key_name(physical: int) -> String:
	return Settings.key_name(physical)


## A switch from TOGGLE_WORDS[`key`]: its short label beside it, `args` filled into its
## description (shown under it and as its tooltip).
func _toggle(key: StringName, node_name: String, value: bool, setter: Callable, args: Array = []) -> ZineToggle:
	var words: Array = TOGGLE_WORDS[key]
	var t := ZineToggle.new(tr(String(words[0])), value)
	t.name = node_name
	var desc := tr(String(words[1]))
	if not args.is_empty():
		desc = desc % args
	t.set_meta(&"description", desc)
	t.tooltip_text = UiTip.fold(desc)
	t.toggled.connect(func(on: bool) -> void: setter.call(on))
	return t


func _add_toggle_row(box: VBoxContainer, t: ZineToggle) -> void:
	var row := VBoxContainer.new()
	row.name = "Row_%s" % t.name
	row.add_theme_constant_override("separation", 0)
	row.add_child(t)
	row.add_child(_description(String(t.get_meta(&"description", ""))))
	box.add_child(row)


## A picker row from [[name, meta], ...] word pairs (keys) shown for `values`, `current`
## chosen; choosing one calls `setter` with its value.
func _choice(node_name: String, pairs: Array, values: Array[StringName], current: StringName, setter: Callable) -> TilePicker:
	var tiles: Array[Dictionary] = []
	for p in pairs:
		tiles.append({"name": tr(String(p[0])), "meta": tr(String(p[1])) if String(p[1]) != "" else ""})
	return _picker(node_name, tiles, maxi(0, values.find(current)), func(i: int) -> void: setter.call(values[i]))


func _picker(node_name: String, tiles: Array[Dictionary], current: int, on_choose: Callable) -> TilePicker:
	var p := TilePicker.new(tiles)
	p.name = node_name
	p.value = current
	p.cursor = current
	p.tile_chosen.connect(on_choose)
	_pickers.append(p)
	return p


func _slider(node_name: String, lo: float, hi: float, step: float, value: float, setter: Callable, fmt: Callable) -> ZineSlider:
	var s := ZineSlider.new(lo, hi, step, value)
	s.name = node_name
	s.format = fmt
	s.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	s.value_changed.connect(func(v: float) -> void: setter.call(v))
	return s


## A row heading (label step, TEXT_HI), with an optional description under it.
func _heading(text: String, note: String = "") -> Control:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 0)
	var l := Label.new()
	l.name = "Heading"
	l.text = text
	l.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.LABEL))
	l.add_theme_color_override("font_color", Palette.TEXT_HI)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_descriptions.append(l)
	box.add_child(l)
	if note != "":
		box.add_child(_description(note))
	return box


## A wrapped line of explanation in TEXT_MID (4.5:1 and more on the glass).
func _description(text: String) -> Label:
	var l := Label.new()
	l.name = "Description"
	l.text = text
	l.add_theme_color_override("font_color", Palette.TEXT_MID)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size.x = PANEL_W - UiTheme.PANEL_PAD_H * 2 - SCROLL_ROOM
	_descriptions.append(l)
	return l


## The preview's frame: a darker glass box holding the sample at the slider's scale.
func _preview_box() -> Control:
	var box := PanelContainer.new()
	box.name = "PreviewBox"
	box.add_theme_stylebox_override(&"panel", UiTheme.box(Palette.TERMINAL_BG, Palette.TERMINAL_EDGE, 1, UiTheme.PANEL_PAD_H, UiTheme.PANEL_PAD_V))
	box.add_child(text_preview)
	return box


## The sample shows body text at scale `v` (the slider's value, before the page follows).
func _preview_scale(v: float) -> void:
	text_preview.add_theme_font_size_override("font_size", UiTheme.font_px_at(UiTheme.BODY, v))


func _ready() -> void:
	Settings.hints_changed.connect(_relabel_close)
	Settings.changed.connect(_on_settings)
	_relabel_close()
	UiFocus.focus_first(sections[section])


func _on_settings() -> void:
	if not is_equal_approx(_built_scale, Settings.text_scale):
		_relayout.call_deferred()


## "Close [Esc]" with keys; with a pad the prompt bar says it (§12: glyphs, never letters in
## brackets), and the button reads "Close".
func _relabel_close() -> void:
	if close_button == null:
		return
	var hint := "" if Settings.pad_active else Settings.hint(&"ui_cancel")
	close_button.text = ("%s %s" % [tr("Close"), hint]).strip_edges()
	if prompts != null:
		prompts.set_prompts([["ui_accept", "Select"], ["ui_cancel", "Close"]] if own_prompts else [])


## At least the content's size, so a host that scrolls can reach every control.
func _get_minimum_size() -> Vector2:
	if _paper_panel == null or _paper_panel.content == null:
		return Vector2.ZERO
	return _paper_panel.content.get_combined_minimum_size().max(Vector2(custom_minimum_size.x, 0))
