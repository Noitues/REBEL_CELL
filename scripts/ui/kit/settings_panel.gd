class_name SettingsPanel
extends Control
## Options (GDD 9.5, 9.6, STYLE_GUIDE 6): five sections. Accessibility (reduce effects,
## flash limiter, text scale, subtitles), Display (window mode, resolution, vsync, fps
## counter), Audio (master, music, SFX), Controls (rebind the combat keys; card keys stay
## 1-9), Language. Writes to the Settings autoload only.
## ART-10 4C (ART_BIBLE v2 §4.13 "Settings"; round 31 `settings_menu.jpg`): a v2 terminal
## (`> PAUSED // OPTIONS`) with the yellow OPTIONS title sticker; terminal tabs (LB / RB
## switch them); Accessibility in two columns: EFFECTS & MOTION switches on the left (name in
## CAPS, what it does in Plex, ON / OFF pills; HEAT GLITCH with its LIMITED chip), and on
## the right the text-scale slider with its live sample, the colour-blind and resolve-speed
## tiles and the Heat glitch preview; the close button and pad prompts at the foot. C's
## behaviour is unchanged: the same widgets (CheckButton, OptionButton, HSlider) drive the
## same Settings setters, built once, moved between sections.

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
## Parity OPT-02 (designer group ruling 2026-10-05: the options match round 31's concept): the
## rows' words as the concept prints them, kept true to what each setting does.
const HIGH_CONTRAST_WORDS := "High contrast (opaque panels, 7:1 text and thick edges)" # TR
const REDUCE_EFFECTS_WORDS := "Reduce effects (no scanlines, flicker, chromatic or distortion)" # TR
const FLASH_WORDS := "Flash limiter (at most 3 flashes a second. On by default.)" # TR
const HEAT_GLITCH_WORDS := "Heat glitch (screen-wide Heat distortion, pulsing harder as Heat rises. Off by default.)" # TR
const SUBTITLES_WORDS := "Subtitles (every spoken line, with the speaker's name)" # TR
const ASSIST_WORDS := "Assist mode (new campaigns: %s free nudge a turn, %s%% HP. No ICE records or achievements.)" # TR
## Parity OPT-01 (round 31's foot): RESET TO DEFAULTS resets the open tab's settings; the pad's Y
## does the same (the prompt row says so).
const RESET_WORDS := "Reset to defaults" # TR
const RESET_TIP := "Puts every setting on this tab back to its default." # TR
const RESET_PROMPT := "reset" # TR
## The settings each tab's RESET TO DEFAULTS puts back ([Settings property, its setter]); the
## Controls tab also resets the key binds (Settings.reset_keybinds).
const RESETS := {
	"Accessibility": [[&"reduce_effects", &"set_reduce_effects"], [&"reduce_motion", &"set_reduce_motion"], [&"flash_limiter", &"set_flash_limiter"],
		[&"heat_glitch", &"set_heat_glitch"], [&"high_contrast", &"set_high_contrast"], [&"subtitles", &"set_subtitles"],
		[&"subtitle_typing", &"set_subtitle_typing"], [&"assist_mode", &"set_assist_mode"], [&"text_scale", &"set_text_scale"],
		[&"colorblind_mode", &"set_colorblind_mode"], [&"resolve_speed", &"set_resolve_speed"]],
	"Display": [[&"window_mode", &"set_window_mode"], [&"resolution", &"set_resolution"], [&"vsync", &"set_vsync"], [&"show_fps", &"set_show_fps"],
		[&"map_legend", &"set_map_legend"], [&"always_show_all_nodes", &"set_always_show_all_nodes"], [&"system_log", &"set_system_log"],
		[&"palette_skin", &"set_palette_skin"]],
	"Audio": [[&"master_volume", &"set_master_volume"], [&"music_volume", &"set_music_volume"], [&"sfx_volume", &"set_sfx_volume"]],
	"Controls": [[&"pad_glyph_set", &"set_pad_glyph_set"]],
	"Language": [[&"language", &"set_language"]]}
const COLORBLIND_HEADING := "Colour-blind correction (patterns and glyphs stay the main cue)" # TR
const RESOLVE_SPEED_HEADING := "Resolve speed after SEND IT (hold Fast-forward to speed it up)" # TR
const GLYPH_HEADING := "Pad button glyphs" # TR
## ART-12 12s: the palette skin row (Display); its choices are PaletteSkins.WORDS.
const SKIN_HEADING := "Interface skin (terminal colours only; meanings and layout stay)" # TR
## Every word the W9 rows add (tests check each has a strings.csv key and no mouse wording).
const W9_WORDS := COLORBLIND_WORDS + RESOLVE_SPEED_WORDS + GLYPH_WORDS + [REDUCE_MOTION_WORDS, HIGH_CONTRAST_WORDS,
	COLORBLIND_HEADING, RESOLVE_SPEED_HEADING, GLYPH_HEADING, "Fast-forward the resolve (hold)", REDUCE_EFFECTS_WORDS, FLASH_WORDS,
	HEAT_GLITCH_WORDS, SUBTITLES_WORDS, RESET_WORDS, RESET_TIP]
## ART-10 4C: the v2 headings, sample and foot words (keys).
const V2_WORDS := ["EFFECTS & MOTION", "SUBTITLES & ASSIST", "TEXT SCALE", "COLOUR-BLIND CORRECTION", "RESOLVE SPEED AFTER SEND IT",
	"HEAT GLITCH PREVIEW (HUNTED, 82)", "The Cell never sleeps. Every word grows with this.", "Patterns and glyphs stay the main cue.",
	"saved to profile", "switch tab", "toggle", "close", "OPTIONS", "PAUSED", "LIMITED: flash limiter on, slow layer only",
	"LIMITED: reduce effects on, slow layer only"] # TR

## Width the refusal note wraps at.
const BIND_NOTE_WIDTH := 480.0
## ART-10 4C layout (px at 1280x720): the panel's widths with one and two columns, the gap
## between the columns, the title sticker's lettering size and tilt, the tick marks under
## the text-scale slider, and from which text scale Accessibility stacks its columns.
## Parity OPT-01: two columns are round 31's centred terminal (1320 of the 1920 board = 880 px),
## widened to 980 so the four colour-blind tiles keep one row at the game's type steps (they are
## a third larger than the concept's), the right column a little wider than the left (round 31:
## 580 to 640 board px of tiles and previews beside the switches).
const WIDTH_ONE := 620.0
const WIDTH_TWO := 980.0
const RIGHT_SHARE := 1.1
const COLUMN_GAP := 28
const TITLE_PX := 34.0
const TITLE_TILT := -3.0
const SCALE_TICKS: Array[float] = [1.0, 1.5, 2.0]
const STACK_FROM := 1.5
## A section heading stands this many caption lines tall (its room above it).
const HEADING_LINES := 2.4
## The title sticker overlaps the header strip by this share of its height.
const STICKER_RISE := 0.45
## The space the panel leaves under it when it fits its own height (px at 1.0; the title
## page's header and foot).
const SCREEN_ROOM := 150.0

## Why the last key pressed while rebinding was refused (Controls section).
var _bind_note: Label = null
## Set by a modal host (the pause menu): D-pad focus never leaves the panel.
var trap_focus: bool = false
## One column always (set by a narrow host: the pause menu's MENU_SIZE).
var compact: bool = false
## Where the Options were opened from (the header: "> PAUSED // OPTIONS"); translated.
var context: String = ""
var reduce_check: CheckButton
## ART-0 C (art pass W9): reduce motion and high contrast (Accessibility), the colour-blind
## correction and the resolve speed (Accessibility), the pad glyph set (Controls).
var reduce_motion_check: CheckButton
var high_contrast_check: CheckButton
var colorblind_option: OptionButton
var resolve_speed_option: OptionButton
var glyph_option: OptionButton
## ART-12 12s: the palette skin picker (Display).
var skin_option: OptionButton
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
## ART-7 3B (D13): "Always show all nodes" on the netrun map.
var all_nodes_check: CheckButton
var language_option: OptionButton
var close_button: Button
## Parity OPT-01: the foot's RESET TO DEFAULTS (the open tab's settings).
var reset_button: Button
var section: String = "Accessibility"
## Action waiting for a key press (Controls section), or empty.
var rebinding: StringName = &""
## ART-10 4C: the v2 pieces: the terminal, the title sticker, the tabs, the tile rows, the
## text-scale readout and sample, the glitch preview.
var window: CrtWindow
var title_sticker: VerbSticker
var colorblind_tiles: CrtTiles
var resolve_tiles: CrtTiles
var glitch_preview: HeatGlitchPreview
var _scale_value: Label
var _scale_sample: Label
var _scale_block: VBoxContainer
var _body: VBoxContainer
## ART-10 4C (ART-0 carry-over: panels adopt FitScroll): the section scrolls inside the
## terminal when the panel would be taller than `max_height` (0: it sizes to its section,
## inside a host that scrolls, the pause menu).
var fit: FitScroll
var max_height: float = 0.0:
	set(v):
		max_height = v
		_queue_fit()
## The widest the panel may be (px; 0 = no cap): the host's room.
var max_width: float = 0.0
## The header's and foot's hints (`[LB] [RB] switch tab`, the pad prompts, "saved to profile"):
## shown below STACK_FROM; at big text they give their rows to the section (the keys still work).
var _hints: Array[Control] = []
var _tabs: HFlowContainer
var _tab_buttons: Dictionary = {}
var _key_buttons: Dictionary = {}
var _label_counter: int = 0


func _init() -> void:
	custom_minimum_size = Vector2(WIDTH_ONE, 360)
	TextDb.shown_as_given(self)
	window = CrtWindow.new("OPTIONS")
	window.name = "OptionsWindow"
	window.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(window)
	# The panel grows with its section (inside the pause menu's scroll), never clipping it.
	window.minimum_size_changed.connect(update_minimum_size)
	var box := window.body
	box.add_theme_constant_override("separation", 10)
	var tab_row := HFlowContainer.new()
	tab_row.name = "TabRow"
	box.add_child(tab_row)
	_tabs = HFlowContainer.new()
	_tabs.name = "Tabs"
	_tabs.add_theme_constant_override("h_separation", 6)
	_tabs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tab_row.add_child(_tabs)
	for name in SECTIONS:
		var b := MenuChip.new(tr(name))
		b.plate = &"tab"  # ui31.tabs plates (round 31)
		b.pre_translated = true
		b.label_step = UiTheme.BODY
		b.name = "Tab%s" % name
		b.set_meta(UiFocus.META_NO_SCALE, true)
		b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var n: String = name
		b.pressed.connect(func() -> void: show_section(n))
		_tabs.add_child(b)
		_tab_buttons[name] = b
	var switch_hint := Chrome.caps_label("[LB] [RB] %s" % tr("switch tab"), UiTheme.CAPTION, Palette.TEXT_LO)
	switch_hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	tab_row.add_child(switch_hint)
	_hints.append(switch_hint)
	_body = VBoxContainer.new()
	_body.name = "Body"
	_body.add_theme_constant_override("separation", 4)
	_body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	fit = FitScroll.new(_body)
	fit.size_flags_vertical = Control.SIZE_EXPAND_FILL
	# Parity OPT-01: the panel is sized to its words, so a view snapped above a cut row left an
	# empty band under it inside the terminal (a row is 50 px at 1.6): the view scrolls freely,
	# MORE BELOW saying there is more (as the codex and slots views).
	fit.hint.snap_rows = false
	box.add_child(fit)
	# Widgets are built once so tests (and Settings.changed) can drive them by name.
	reduce_check = _check(tr(REDUCE_EFFECTS_WORDS), Settings.reduce_effects, Settings.set_reduce_effects)
	flash_check = _check(tr(FLASH_WORDS), Settings.flash_limiter, Settings.set_flash_limiter)
	heat_glitch_check = _check(tr(HEAT_GLITCH_WORDS), Settings.heat_glitch, Settings.set_heat_glitch)
	heat_glitch_check.name = "HeatGlitchCheck"
	(heat_glitch_check as CrtSwitch).note = _glitch_note
	reduce_motion_check = _check(tr(REDUCE_MOTION_WORDS), Settings.reduce_motion, Settings.set_reduce_motion)
	reduce_motion_check.name = "ReduceMotionCheck"
	high_contrast_check = _check(tr(HIGH_CONTRAST_WORDS), Settings.high_contrast, Settings.set_high_contrast)
	high_contrast_check.name = "HighContrastCheck"
	colorblind_option = _choice("ColorblindOption", COLORBLIND_WORDS, Settings.COLORBLIND_MODES, Settings.colorblind_mode, Settings.set_colorblind_mode)
	resolve_speed_option = _choice("ResolveSpeedOption", RESOLVE_SPEED_WORDS, Settings.RESOLVE_SPEEDS, Settings.resolve_speed, Settings.set_resolve_speed)
	skin_option = _choice("SkinOption", PaletteSkins.WORDS, Settings.PALETTE_SKINS, Settings.palette_skin, Settings.set_palette_skin)
	glyph_option = _choice("GlyphOption", GLYPH_WORDS, Settings.PAD_GLYPH_SETS, Settings.pad_glyph_set, Settings.set_pad_glyph_set)
	colorblind_tiles = CrtTiles.new(colorblind_option)
	resolve_tiles = CrtTiles.new(resolve_speed_option)
	subtitles_check = _check(tr(SUBTITLES_WORDS), Settings.subtitles, Settings.set_subtitles)
	typing_check = _check(tr("Subtitles type in (off: each line shows at once)"), Settings.subtitle_typing, Settings.set_subtitle_typing)
	typing_check.name = "TypingCheck"
	var cfg := RunManager.config()
	assist_check = _check(tr(ASSIST_WORDS) % [TextDb.signed(cfg.assist_free_nudges), TextDb.signed(roundi((cfg.assist_hp_multiplier - 1.0) * 100.0))], Settings.assist_mode, Settings.set_assist_mode)
	assist_check.name = "AssistCheck"
	scale_slider = _slider("Text scale", Settings.TEXT_SCALE_MIN, Settings.TEXT_SCALE_MAX, 0.1, Settings.text_scale, Settings.set_text_scale)
	master_slider = _slider("Master volume", 0.0, 1.0, 0.05, Settings.master_volume, Settings.set_master_volume)
	music_slider = _slider("Music volume", 0.0, 1.0, 0.05, Settings.music_volume, Settings.set_music_volume)
	sfx_slider = _slider("SFX volume", 0.0, 1.0, 0.05, Settings.sfx_volume, Settings.set_sfx_volume)
	_scale_block = _text_scale_block()
	glitch_preview = HeatGlitchPreview.new()
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
	all_nodes_check = _check(tr("Always show all nodes on the netrun map"), Settings.always_show_all_nodes, Settings.set_always_show_all_nodes)
	all_nodes_check.name = "AllNodesCheck"
	language_option = OptionButton.new()
	var langs := Settings.available_languages()
	for i in langs.size():
		language_option.add_item(langs[i])
		if langs[i] == Settings.language:
			language_option.select(i)
	language_option.item_selected.connect(func(i: int) -> void: Settings.set_language(langs[i]))
	# The foot (round 31): RESET TO DEFAULTS, Close (the pointer's way out; B / Esc close too),
	# the pad prompts (A toggle, B close, Y reset), "saved to profile".
	var foot := HFlowContainer.new()
	foot.name = "Foot"
	foot.add_theme_constant_override("h_separation", 18)
	box.add_child(foot)
	reset_button = Button.new()
	reset_button.name = "ResetDefaults"
	reset_button.text = tr(RESET_WORDS).to_upper()
	reset_button.tooltip_text = UiTip.fold(tr(RESET_TIP))
	reset_button.pressed.connect(reset_section)
	foot.add_child(reset_button)
	var close := Button.new()
	close.name = "Close"
	close_button = close
	close.pressed.connect(func() -> void: closed.emit())
	foot.add_child(close)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	foot.add_child(spacer)
	for p in [[JOY_BUTTON_A, tr("toggle")], [JOY_BUTTON_B, tr("close")], [JOY_BUTTON_Y, tr(RESET_PROMPT)]]:
		var pair := PadPrompts.make_pair(int(p[0]), String(p[1]))
		foot.add_child(pair)
		_hints.append(pair)
	var saved := Chrome.caps_label(tr("saved to profile"), UiTheme.CAPTION, Palette.TEXT_LO)
	saved.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	foot.add_child(saved)
	_hints.append(saved)
	_show_hints()
	# The yellow OPTIONS title sticker over the header's right end (round 31).
	title_sticker = VerbSticker.new(tr("OPTIONS"), VerbSticker.Fill.YELLOW, TITLE_PX, TITLE_TILT, VerbSticker.title_art("OPTIONS"))
	title_sticker.pre_translated = true
	title_sticker.name = "TitleSticker"
	title_sticker.focus_mode = Control.FOCUS_NONE
	title_sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(title_sticker)
	resized.connect(_place_sticker)
	show_section("Accessibility")


## "LIMITED: ..." under HEAT GLITCH while the flash limiter or reduce effects holds it to its
## slow layer (§4.13, §5.5); "" otherwise.
func _glitch_note() -> String:
	if not Settings.heat_glitch:
		return ""
	if Settings.reduce_effects:
		return tr("LIMITED: reduce effects on, slow layer only")
	if Settings.flash_limiter:
		return tr("LIMITED: flash limiter on, slow layer only")
	return ""


func _place_sticker() -> void:
	if title_sticker == null:
		return
	# Inside the pause menu its PAUSED sticker is the title.
	title_sticker.visible = not compact
	var m := title_sticker.get_combined_minimum_size()
	title_sticker.size = m
	title_sticker.position = Vector2(size.x - m.x - Chrome.CHAMFER * 3.0, -m.y * STICKER_RISE)


## How far the OPTIONS sticker rises over the panel's top edge (px; 0 when it is hidden): a
## host keeps that room above the panel.
func sticker_rise() -> float:
	if title_sticker == null or compact:
		return 0.0
	return title_sticker.get_combined_minimum_size().y * STICKER_RISE


## Parity OPT-01: the panel's width with one column: WIDTH_ONE growing with the text (a centred
## terminal sized to its words; narrow at big text, its tabs and foot wrapped to rows that took
## the section's room), up to `max_width` (the host's room; 0 = no cap).
func one_column_width() -> float:
	var w := WIDTH_ONE * maxf(1.0, Settings.text_scale)
	return minf(w, max_width) if max_width > 0.0 else w


## The two columns side by side (wide enough, text below STACK_FROM).
func two_columns() -> bool:
	return not compact and Settings.text_scale < STACK_FROM


func show_section(name: String) -> void:
	section = name
	rebinding = &""
	for s in _tab_buttons:
		(_tab_buttons[s] as MenuChip).selected = s == name
	# ANIM-R4 C3: the built widgets wait off the tree for their section; everything else a
	# section made (its labels, the Controls grid, the note, Reset) goes (they leaked: 49
	# Controls per Options opened). Queued: Reset calls this from its own press.
	# ANIM-R6 D10: what goes stays in the tree, hidden, until its free (taken out and only
	# queued, it was an orphan node until the frame ended: 74 counted after one test).
	var keep := _persistent()
	_release(_body, keep)
	_key_buttons.clear()
	match name:
		"Accessibility":
			var left := _column("Left")
			left.add_child(_heading(tr("EFFECTS & MOTION")))
			for w in [reduce_check, reduce_motion_check, flash_check, heat_glitch_check, high_contrast_check, subtitles_check, typing_check, assist_check]:
				left.add_child(w)
			var right := _column("Right")
			right.size_flags_stretch_ratio = RIGHT_SHARE
			right.add_child(_heading(tr("TEXT SCALE")))
			right.add_child(_scale_block)
			right.add_child(_heading(tr("COLOUR-BLIND CORRECTION")))
			right.add_child(colorblind_tiles)
			right.add_child(_note(tr("Patterns and glyphs stay the main cue.")))
			right.add_child(_heading(tr("RESOLVE SPEED AFTER SEND IT")))
			right.add_child(resolve_tiles)
			right.add_child(_heading(tr("HEAT GLITCH PREVIEW (HUNTED, 82)")))
			right.add_child(glitch_preview)
			var cols: BoxContainer = HBoxContainer.new() if two_columns() else VBoxContainer.new()
			cols.name = "Columns"
			cols.add_theme_constant_override("separation", COLUMN_GAP if two_columns() else 14)
			cols.add_child(left)
			cols.add_child(right)
			_body.add_child(cols)
		"Display":
			for w in [_heading(tr("Window mode")), mode_option, _heading(tr("Resolution (windowed)")), resolution_option, vsync_check, fps_check, legend_check, all_nodes_check, log_check,
					_heading(tr(SKIN_HEADING)), skin_option]:
				_body.add_child(w)
		"Audio":
			for w in [_heading(tr("Master volume")), master_slider, _heading(tr("Music volume")), music_slider, _heading(tr("SFX volume")), sfx_slider]:
				_body.add_child(w)
		"Controls":
			_body.add_child(_heading(tr(GLYPH_HEADING)))
			_body.add_child(glyph_option)
			_body.add_child(_labelled(UiTip.for_input(tr("Click a key, then press the new one. Cards stay on 1-9."), tr("Press a key, then press the new one. Cards stay on 1-9."))))
			var grid := GridContainer.new()
			grid.columns = 4
			grid.add_theme_constant_override("h_separation", 12)
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
			UiWrap.whole_words(_bind_note)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
			_bind_note.custom_minimum_size.x = BIND_NOTE_WIDTH
			_body.add_child(_bind_note)
			var reset := Button.new()
			reset.name = "ResetKeys"
			reset.text = tr("Reset to defaults").to_upper()
			reset.pressed.connect(func() -> void: Settings.reset_keybinds(); show_section("Controls"))
			_body.add_child(reset)
		"Language":
			for w in [_heading(tr("Language (translations from assets/text/strings.csv)")), language_option]:
				_body.add_child(w)
	custom_minimum_size.x = WIDTH_TWO if (name == "Accessibility" and two_columns()) else one_column_width()
	UiWrap.fit(self)
	if trap_focus:
		UiFocus.trap(self)  # inside the pause menu: focus stays in the panel
	else:
		UiFocus.link_layout(self)  # the section swapped its controls
	UiFocus.focus_first(_body)
	_queue_fit()


## Takes the built widgets out of `node` (they wait off the tree); frees the rest.
func _release(node: Node, keep: Array[Control]) -> void:
	for c in node.get_children():
		if keep.has(c):
			node.remove_child(c)
		elif not c.is_queued_for_deletion():
			_release(c, keep)
			(c as CanvasItem).hide()
			c.queue_free()


func _column(n: String) -> VBoxContainer:
	var col := VBoxContainer.new()
	col.name = n
	col.add_theme_constant_override("separation", 2)
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return col


## The text-scale block: the slider with its value and ticks, then the live sample (round
## 31: "The Cell never sleeps. Every word grows with this.").
func _text_scale_block() -> VBoxContainer:
	var block := VBoxContainer.new()
	block.name = "TextScaleBlock"
	block.add_theme_constant_override("separation", 4)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	scale_slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scale_slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(scale_slider)
	_scale_value = Chrome.caps_label("", UiTheme.LABEL, Palette.TEXT_HI)
	_scale_value.name = "ScaleValue"
	_scale_value.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	row.add_child(_scale_value)
	block.add_child(row)
	var ticks := HBoxContainer.new()
	ticks.name = "Ticks"
	for i in SCALE_TICKS.size():
		var t := Chrome.caps_label("%.1f" % SCALE_TICKS[i], UiTheme.CAPTION, Palette.TEXT_LO)
		t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		t.horizontal_alignment = [HORIZONTAL_ALIGNMENT_LEFT, HORIZONTAL_ALIGNMENT_CENTER, HORIZONTAL_ALIGNMENT_RIGHT][mini(i, 2)]
		ticks.add_child(t)
	block.add_child(ticks)
	var sample_box := PanelContainer.new()
	sample_box.name = "Sample"
	var sb := PaletteSkins.track_box(UiTheme.box(Palette.TERMINAL_BG, Palette.NET_CYAN, 1, 12, 8))
	sample_box.add_theme_stylebox_override(&"panel", sb)
	_scale_sample = Chrome.body_label(tr("The Cell never sleeps. Every word grows with this."), UiTheme.LABEL, Palette.TEXT_HI)
	_scale_sample.custom_minimum_size.x = 0
	sample_box.add_child(_scale_sample)
	block.add_child(sample_box)
	scale_slider.value_changed.connect(func(_v: float) -> void: _sync_scale())
	_sync_scale()
	return block


func _sync_scale() -> void:
	if _scale_value != null:
		_scale_value.text = "%.1fx" % scale_slider.value


## The widgets built once in _init (they move between the body and off the tree).
func _persistent() -> Array[Control]:
	return [reduce_check, flash_check, heat_glitch_check, subtitles_check, typing_check, assist_check, master_slider, music_slider,
		sfx_slider, mode_option, resolution_option, vsync_check, fps_check, legend_check, log_check, all_nodes_check, language_option,
		reduce_motion_check, high_contrast_check, colorblind_tiles, resolve_tiles, glyph_option, _scale_block, glitch_preview, skin_option]


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
		return
	# LB / RB switch the tab (round 31); Y resets the tab (round 31's foot: "Y reset").
	if event is InputEventJoypadButton and event.pressed:
		var b := (event as InputEventJoypadButton).button_index
		if b == JOY_BUTTON_Y:
			reset_section()
			get_viewport().set_input_as_handled()
			return
		if b == JOY_BUTTON_LEFT_SHOULDER or b == JOY_BUTTON_RIGHT_SHOULDER:
			var i := SECTIONS.find(section) + (1 if b == JOY_BUTTON_RIGHT_SHOULDER else -1)
			show_section(SECTIONS[wrapi(i, 0, SECTIONS.size())])
			get_viewport().set_input_as_handled()


## Parity OPT-01 (round 31 RESET TO DEFAULTS): puts every setting of the open tab back to its
## default (the Settings script's own initial values: no number is written here), through the
## same setters the rows call, then shows the tab again with the new values. The Controls tab
## also resets the key binds. Settings only; nothing else changes.
func reset_section() -> void:
	var defaults: Object = (Settings.get_script() as GDScript).new()
	for pair in RESETS.get(section, []):
		Settings.call(StringName(pair[1]), defaults.get(StringName(pair[0])))
	(defaults as Node).free()
	if section == "Controls":
		Settings.reset_keybinds()
	sync_widgets()
	show_section(section)


## Shows the Settings' values on the built widgets (no signal: nothing is set twice).
func sync_widgets() -> void:
	for pair in [[reduce_check, Settings.reduce_effects], [reduce_motion_check, Settings.reduce_motion], [flash_check, Settings.flash_limiter],
			[heat_glitch_check, Settings.heat_glitch], [high_contrast_check, Settings.high_contrast], [subtitles_check, Settings.subtitles],
			[typing_check, Settings.subtitle_typing], [assist_check, Settings.assist_mode], [vsync_check, Settings.vsync], [fps_check, Settings.show_fps],
			[legend_check, Settings.map_legend], [log_check, Settings.system_log], [all_nodes_check, Settings.always_show_all_nodes]]:
		(pair[0] as CheckButton).set_pressed_no_signal(bool(pair[1]))
		(pair[0] as Control).queue_redraw()
	for pair in [[scale_slider, Settings.text_scale], [master_slider, Settings.master_volume], [music_slider, Settings.music_volume], [sfx_slider, Settings.sfx_volume]]:
		(pair[0] as HSlider).set_value_no_signal(float(pair[1]))
	_sync_scale()
	for pair in [[colorblind_option, Settings.COLORBLIND_MODES, Settings.colorblind_mode], [resolve_speed_option, Settings.RESOLVE_SPEEDS, Settings.resolve_speed],
			[skin_option, Settings.PALETTE_SKINS, Settings.palette_skin], [glyph_option, Settings.PAD_GLYPH_SETS, Settings.pad_glyph_set]]:
		(pair[0] as OptionButton).select(maxi(0, (pair[1] as Array).find(pair[2])))
	for t in [colorblind_tiles, resolve_tiles]:
		(t as CrtTiles).refresh()
	mode_option.select(Settings.window_mode)
	var at := Settings.RESOLUTIONS.find(Settings.resolution)
	if at >= 0:
		resolution_option.select(at)
	var lang := Settings.available_languages().find(Settings.language)
	if lang >= 0:
		language_option.select(lang)


static func _key_name(physical: int) -> String:
	return Settings.key_name(physical)


func _check(text: String, value: bool, setter: Callable) -> CheckButton:
	var c := CrtSwitch.new(text)
	c.button_pressed = value
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


## A slider in the v2 look: a cyan track and fill, a white grabber (round 31 TEXT SCALE).
func _slider(text: String, lo: float, hi: float, step: float, value: float, setter: Callable) -> HSlider:
	var s := HSlider.new()
	s.name = text.replace(" ", "")
	s.min_value = lo
	s.max_value = hi
	s.step = step
	s.value = value
	s.custom_minimum_size = Vector2(300, 20)
	s.add_theme_stylebox_override(&"slider", PaletteSkins.track_box(UiTheme.box(Color(Palette.NET_CYAN, 0.18), Palette.AUTO, 0, 0, 2)))
	var fill := PaletteSkins.track_box(UiTheme.box(Palette.NET_CYAN, Palette.AUTO, 0, 0, 2))
	s.add_theme_stylebox_override(&"grabber_area", fill)
	s.add_theme_stylebox_override(&"grabber_area_highlight", fill)
	s.add_theme_icon_override(&"grabber", _grabber())
	s.add_theme_icon_override(&"grabber_highlight", _grabber())
	s.set_meta(UiFocus.META_NO_SCALE, true)
	s.value_changed.connect(func(v: float) -> void: setter.call(v))
	return s


static var _grab_tex: ImageTexture = null
const GRABBER_ART := "res://assets/ui/menus/kit/slider_handle.png"
const GRABBER_SCALE := 2.0 / 3.0


## The slider's grabber: the concept's white notched handle.
static func _grabber() -> Texture2D:
	if _grab_tex != null:
		return _grab_tex
	# The concept's notched handle (round 31 ui31.slider, baked by tools/art/bake_menus_r33.py),
	# at two thirds (board -> game); a texture's pixels, resized once (the loaded one is kept).
	var src := load(GRABBER_ART) as Texture2D
	var img := src.get_image()
	img.resize(maxi(1, roundi(img.get_width() * GRABBER_SCALE)), maxi(1, roundi(img.get_height() * GRABBER_SCALE)), Image.INTERPOLATE_LANCZOS)
	_grab_tex = ImageTexture.create_from_image(img)
	return _grab_tex


## A section heading: terminal CAPS, cyan, caption step (round 31 "EFFECTS & MOTION").
func _heading(text: String) -> Label:
	var l := Chrome.caps_label(text.to_upper(), UiTheme.CAPTION, PaletteSkins.chrome(Palette.NET_CYAN))
	l.custom_minimum_size.x = 0.0  # a long heading wraps at its words (big text, the pause menu)
	l.custom_minimum_size.y = Chrome.px(UiTheme.CAPTION) * HEADING_LINES
	l.vertical_alignment = VERTICAL_ALIGNMENT_BOTTOM
	_label_counter += 1
	l.name = "_tmp_%d" % _label_counter
	return l


func _note(text: String) -> Label:
	var l := Chrome.body_label(text, UiTheme.BODY, Palette.TEXT_MID)
	_label_counter += 1
	l.name = "_tmp_%d" % _label_counter
	return l


func _labelled(text: String) -> Label:
	var l := Label.new()
	_label_counter += 1
	l.name = "_tmp_%d" % _label_counter
	l.text = text
	l.add_theme_color_override("font_color", Palette.TEXT_HI)
	return l


## The section's view: the room `max_height` leaves after the terminal's header, tabs and foot.
func _on_settings_changed() -> void:
	_show_hints()
	_queue_fit()


## The hints show below STACK_FROM only.
func _show_hints() -> void:
	for h in _hints:
		h.visible = Settings.text_scale < STACK_FROM


func _fit_body() -> void:
	if fit == null or not is_instance_valid(fit):
		return
	if max_height <= 0.0:
		fit.max_height = 0.0
		return
	var chrome := window.get_combined_minimum_size().y - fit.get_combined_minimum_size().y
	if window.is_inside_tree() and window.size.y > 0.0 and fit.size.y > 0.0:
		chrome = maxf(chrome, window.size.y - fit.size.y)  # as laid out (the tabs and the foot wrapped)
	# The view's own cap leaves out its MORE BELOW room under it.
	var hint_room := fit.get_combined_minimum_size().y - fit.scroll.get_combined_minimum_size().y
	fit.max_height = maxf(FitScroll.MIN_VIEW * Settings.text_scale, max_height - chrome - hint_room)


## Parity OPT-01: the panel sized to its words (centred, not stretched over its room) measures
## its header, tabs and foot only once they are laid out at their width (the tabs and the foot
## wrap): the view is fitted now and again over FIT_PASSES frames.
const FIT_PASSES := 3
var _fit_left: int = 0


func _queue_fit() -> void:
	_fit_left = FIT_PASSES
	_fit_body.call_deferred()
	if is_inside_tree() and not get_tree().process_frame.is_connected(_fit_pass):
		get_tree().process_frame.connect(_fit_pass, CONNECT_ONE_SHOT)


func _fit_pass() -> void:
	_fit_body()
	# A focus that landed while the rows were still being measured (a row's first frames are a
	# pre-layout height) left the view scrolled past it: bring it back (the section's first
	# control shows its heading too: the view's top).
	var focused := get_viewport().gui_get_focus_owner() if is_inside_tree() else null
	if focused != null and fit.scroll.is_ancestor_of(focused) and focused != UiFocus.first_focusable(_body):
		fit.scroll.ensure_control_visible(focused)
	else:
		fit.scroll.scroll_vertical = 0  # the focus on a tab or the section's first row: its top
	_fit_left -= 1
	if _fit_left > 0 and is_inside_tree() and not get_tree().process_frame.is_connected(_fit_pass):
		get_tree().process_frame.connect(_fit_pass, CONNECT_ONE_SHOT)


func _exit_tree() -> void:
	if get_tree().process_frame.is_connected(_fit_pass):
		get_tree().process_frame.disconnect(_fit_pass)


func _ready() -> void:
	_queue_fit()
	Settings.changed.connect(_on_settings_changed)
	Settings.hints_changed.connect(_relabel_close)
	_relabel_close()
	var where := context if context != "" else tr("PAUSED")
	window.title = "%s // %s" % [where, tr("OPTIONS")]
	var head := window.find_child("TerminalTitle", true, false) as Label
	if head != null:
		head.text = "> " + window.title.to_upper()
	_place_sticker()
	UiFocus.focus_first(self)


## "Close [Esc]" / "Close [B]": the hint follows the device and the binds (H20).
func _relabel_close() -> void:
	close_button.text = ("%s %s" % [tr("Close"), Settings.hint(&"ui_cancel")]).strip_edges()


## At least the content's size, so a host that scrolls can reach every control.
func _get_minimum_size() -> Vector2:
	if window == null:
		return Vector2.ZERO
	return window.get_combined_minimum_size()
