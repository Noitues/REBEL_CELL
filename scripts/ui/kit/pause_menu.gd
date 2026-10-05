class_name PauseMenu
extends Control
## Pause menu (gap analysis 2.5): Resume, Options (the SettingsPanel inline), Codex,
## Save & quit to title, Quit to desktop (confirmed). Scenes open it on Esc; it never
## changes game state itself beyond asking RunManager to save and switch scenes.
## ART-10 4C (ART_BIBLE v2 §4.13, §2.10; round 33 `abandon_dialog.jpg`, `ui_kit.jpg` MENU):
## the yellow PAUSED title sticker over a v2 terminal (`> PAUSED // WHERE`), its lines in
## terminal CAPS with the `>` caret and lime brackets on focus; the Codex as terminal text,
## the Options single-column inside it, the quit confirm in the abandon dialog's look.

signal resumed
signal quit_to_title

var settings_panel: SettingsPanel = null
var codex_note: CrtText = null
var _menu: VBoxContainer
var _host: VBoxContainer
var resume_button: Button
## Who had focus before the menu opened (the combat hand); it gets it back on close.
var _return_focus: Control = null


## Menu size: wide enough for the Controls grid and Accessibility switches at text scale
## 1.6 (the content scrolls vertically inside it).
const MENU_SIZE := Vector2(760, 520)
## Dim over the game while paused.
const BACKDROP_COLOR := Color(0, 0, 0, 0.35)


## Full-screen, click-eating backdrop behind the menu: no click reaches the game (H17).
var _backdrop: ColorRect


func _init() -> void:
	custom_minimum_size = MENU_SIZE
	# ANIM-R3 A2: motion helpers leave presses to an open pause menu (MotionSkip.pause_open).
	add_to_group(MotionSkip.PAUSE_GROUP)
	_backdrop = ColorRect.new()
	_backdrop.name = "Backdrop"
	_backdrop.color = BACKDROP_COLOR
	_backdrop.mouse_filter = Control.MOUSE_FILTER_STOP
	_backdrop.focus_mode = Control.FOCUS_NONE
	add_child(_backdrop)
	# H24 S4: the menu shows its words as given, translated where set.
	TextDb.shown_as_given(self)
	var panel := CrtWindow.new(tr("PAUSED"))
	panel.name = "PauseWindow"
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	_panel = panel
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.body.add_child(scroll)
	_host = VBoxContainer.new()
	_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_host)
	_menu = VBoxContainer.new()
	_host.add_child(_menu)
	resume_button = _add(tr("Resume"), func() -> void: resumed.emit())
	resume_button.name = "Resume"
	_relabel()
	Settings.hints_changed.connect(_relabel)
	_add(tr("Options"), show_options)
	_add(tr("Codex"), show_codex)
	_add(tr("Save & quit to title"), func() -> void:
		if RunManager.campaign != null:
			RunManager.autosave()
		quit_to_title.emit())
	_add(tr("Quit to desktop"), func() -> void:
		var confirm := ConfirmDialog.new(tr("Quit REBEL_CELL? Progress is autosaved."), TextDb.mark("QUIT"), TextDb.mark("CANCEL"), TextDb.mark("QUIT"))  # ART-2 2D: sticker verbs
		confirm.position = Vector2(60, 120)
		add_child(confirm)
		confirm.confirmed.connect(func() -> void: RunManager.quit_game()))
	# H24 S11: the campaign's share code has its line here (it read like debug output on
	# the HQ's Pirate Radio note).
	var code := code_line()
	if code != "":
		var seed_line := Label.new()
		seed_line.name = "SeedLine"
		seed_line.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		seed_line.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		seed_line.text = code
		UiWrap.whole_words(seed_line)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
		seed_line.mouse_filter = Control.MOUSE_FILTER_PASS
		seed_line.tooltip_text = UiTip.fold(tr("Share this code: Start from code on the new campaign screen starts this campaign again."))
		_menu.add_child(seed_line)
	# Focus moves slide the highlight and type the line in (Animation pass ANIM-6).
	MenuMotion.attach(_menu)
	# The yellow PAUSED title sticker over the terminal's top left (round 33).
	title_sticker = VerbSticker.new(tr("PAUSED"), VerbSticker.Fill.YELLOW, TITLE_PX, TITLE_TILT)
	title_sticker.pre_translated = true
	title_sticker.name = "TitleSticker"
	title_sticker.focus_mode = Control.FOCUS_NONE
	title_sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(title_sticker)
	# ANIM-R5 P4: as tall as what it shows (the box stood 520 px tall round ~200 px of lines,
	# hiding the city behind it); Options and the Codex grow it up to MENU_SIZE.
	_host.minimum_size_changed.connect(_fit_height)
	_fit_height()


## ANIM-R5 P4: the menu's height: its glass's own (title, margins) plus what it holds, never
## over MENU_SIZE.y nor past the screen's bottom less FIT_MARGIN (it scrolls inside then).
func _fit_height() -> void:
	if _panel == null or _host == null:
		return
	var want := _panel.get_combined_minimum_size().y + _host.get_combined_minimum_size().y
	var most := MENU_SIZE.y
	if is_inside_tree():
		most = minf(most, get_viewport_rect().size.y - global_position.y - FIT_MARGIN)
	var h := clampf(ceilf(want), minf(FIT_MIN_H, most), most)
	custom_minimum_size = Vector2(MENU_SIZE.x, h)
	size = custom_minimum_size
	if title_sticker != null:
		var m := title_sticker.get_combined_minimum_size()
		title_sticker.size = m
		title_sticker.position = Vector2(Chrome.CHAMFER * 2.0, -m.y * STICKER_RISE)


## The least the menu is tall and the screen edge it keeps clear of (px).
const FIT_MIN_H := 120.0
const FIT_MARGIN := 12.0


## The campaign's share code as a line (H24 S11), in the player's language; "" without a
## campaign.
static func code_line() -> String:
	var c := RunManager.campaign
	if c == null or RunManager.corporation == null:
		return ""
	return TranslationServer.translate("Campaign code (share it: it starts this campaign): %s%s") % [CampaignCode.of(c, c.start_class_id),
		TranslationServer.translate(" (local: REBEL_CELL is built from your profile)") if RunManager.corporation.generated_from_profile else ""]


## The menu's glass (it drops in when the menu opens, Animation pass ANIM-6).
var _panel: CrtWindow = null
## ART-10 4C: the PAUSED title sticker, its size and tilt, and how far it rises over the
## terminal's top edge (share of its height).
var title_sticker: VerbSticker = null
const TITLE_PX := 30.0
const TITLE_TILT := -3.0
const STICKER_RISE := 0.6


func _notification(what: int) -> void:
	if what == NOTIFICATION_READY and _panel != null:
		_fit_height()
		# A wrapped line (the campaign code at 1.6) knows its height only once laid out at its
		# width: fitted again after the first layout.
		if not get_tree().process_frame.is_connected(_fit_height):
			get_tree().process_frame.connect(_fit_height, CONNECT_ONE_SHOT)
		PageTransition.enter(_panel, PageTransition.Look.GLASS)
	if what == NOTIFICATION_VISIBILITY_CHANGED or what == NOTIFICATION_READY:
		if is_visible_in_tree():
			_cover_screen.call_deferred()
			var owner := UiFocus.owner_of(self)
			if owner != null and not is_ancestor_of(owner):
				_return_focus = owner
			UiFocus.trap.call_deferred(self)
			UiFocus.focus_first(_menu)
		elif _return_focus != null and is_instance_valid(_return_focus) and _return_focus.is_visible_in_tree():
			_return_focus.grab_focus.call_deferred()
	elif what == NOTIFICATION_PREDELETE or what == NOTIFICATION_EXIT_TREE:
		if _return_focus != null and is_instance_valid(_return_focus) and _return_focus.is_inside_tree():
			_return_focus.grab_focus.call_deferred()


## Stretches the backdrop over the whole viewport, wherever the menu sits.
func _cover_screen() -> void:
	if _backdrop == null or not is_inside_tree():
		return
	_backdrop.size = get_viewport_rect().size
	_backdrop.global_position = Vector2.ZERO


func _add(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	# ART-10 4C: a terminal menu line (`> ITEM` on focus, lime brackets), CAPS.
	b.theme_type_variation = &"MenuItem"
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.add_theme_font_override(&"font", Chrome.caps_font(UiTheme.LABEL))
	b.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.LABEL))
	b.set_meta(UiFocus.META_NO_SCALE, true)
	b.pressed.connect(on_pressed)
	_menu.add_child(b)
	return b


## "Resume [Esc]" / "Resume [Start]": the hint follows the device and the binds (H20).
func _relabel() -> void:
	resume_button.text = ("%s %s" % [tr("Resume"), Settings.hint(&"open_settings")]).strip_edges()


func show_options() -> void:
	_close_sub()
	settings_panel = SettingsPanel.new()
	settings_panel.closed.connect(_close_sub)
	settings_panel.compact = true  # one column inside the menu (MENU_SIZE)
	settings_panel.show_section(settings_panel.section)
	settings_panel.trap_focus = true
	settings_panel.context = tr("PAUSED")
	_host.add_child(settings_panel)
	PageTransition.enter(settings_panel, PageTransition.Look.GLASS)
	UiWrap.fit(settings_panel)
	UiFocus.trap.call_deferred(settings_panel)
	UiFocus.focus_first(settings_panel)


func show_codex() -> void:
	_close_sub()
	codex_note = CrtText.new(tr("CODEX"), Vector2(520, 220)).make_reference()
	codex_note.fill_codex()
	_host.add_child(codex_note)
	PageTransition.enter(codex_note, PageTransition.Look.GLASS)
	var back := Button.new()
	back.text = tr("Back")
	back.name = "CodexBack"
	back.pressed.connect(_close_sub)
	_host.add_child(back)
	UiFocus.trap.call_deferred(_host)
	back.grab_focus.call_deferred()


func _close_sub() -> void:
	if settings_panel != null and is_instance_valid(settings_panel):
		settings_panel.queue_free()
	settings_panel = null
	if codex_note != null and is_instance_valid(codex_note):
		codex_note.queue_free()
		var back := _host.get_node_or_null("CodexBack")
		if back != null:
			back.queue_free()
	codex_note = null
	UiFocus.trap.call_deferred(self)
	UiFocus.focus_first(_menu)


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if codex_note != null and event.is_action_pressed("ui_cancel"):
		_close_sub()  # Esc in the Codex returns to the menu, like Esc in Options
		get_viewport().set_input_as_handled()
		return
	if settings_panel == null and (event.is_action_pressed("ui_cancel") or event.is_action_pressed("open_settings")):
		resumed.emit()
		get_viewport().set_input_as_handled()
		return
	# While the menu is open no hotkey reaches the game behind it (Space ending a turn,
	# 1-9 entering a map node): it is the last child, so it sees unhandled input first.
	if event is InputEventKey or event is InputEventJoypadButton or event is InputEventJoypadMotion:
		get_viewport().set_input_as_handled()
