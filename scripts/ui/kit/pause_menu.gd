class_name PauseMenu
extends Control
## Pause menu (gap analysis 2.5; ART_BIBLE §11 HQ "pause menu sized to content", §5.3,
## §6.5; art pass W8a): Resume (the one primary), Options (the SettingsPanel inline),
## Codex (the codex spread, one column), Save & quit to title, Quit to desktop (confirmed
## on a SCRIM). GLASS over a dim backdrop. The campaign's share code sits in a read-only
## CodeField with a copy button, never as body text. The menu is as big as what it shows:
## narrow around its lines, MENU_SIZE wide while Options or the Codex are open, and never
## taller than MENU_SIZE nor past the screen's foot (it scrolls inside then); it stays
## centred where its host put its MENU_SIZE box. Scenes open it on Esc; it never changes
## game state itself beyond asking RunManager to save and switch scenes.

signal resumed
signal quit_to_title

var settings_panel: SettingsPanel = null
## The codex spread while the Codex is open (null otherwise).
var codex_note: CodexSpread = null
## The campaign code field (null without a campaign).
var code_field: CodeField = null
## The pad's prompt bar (shown only while a pad is in use).
var prompts: PadPrompts = null
var _menu: VBoxContainer
var _host: VBoxContainer
var resume_button: Button
## Who had focus before the menu opened (the combat hand); it gets it back on close.
var _return_focus: Control = null


## The most room the menu takes: wide enough for the Controls grid and Accessibility
## switches at every text scale (the content scrolls vertically inside it). Hosts centre
## this box; the menu keeps that centre at whatever size it has.
const MENU_SIZE := Vector2(760, 520)
## Dim over the game while paused.
const BACKDROP_COLOR := Color(Palette.SCRIM, 0.35)
## The least the menu is tall and the screen edge it keeps clear of (px).
const FIT_MIN_H := 120.0
const FIT_MARGIN := 12.0
## The Codex rows the menu shows before its spread scrolls (px at 1.0).
const CODEX_VIEW := 300.0


## Full-screen, click-eating backdrop behind the menu: no click reaches the game (H17).
var _backdrop: ColorRect
## The x of the MENU_SIZE box's centre the host placed (NAN until known).
var _centre_x: float = NAN


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
	var panel := ZinePanel.new(tr("PAUSED"), 0.0, true)
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(panel)
	_panel = panel
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.follow_focus = true
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	panel.content.add_child(scroll)
	_host = VBoxContainer.new()
	_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_host.add_theme_constant_override("separation", UiTheme.SP_S)
	scroll.add_child(_host)
	_menu = VBoxContainer.new()
	_menu.name = "Menu"
	_host.add_child(_menu)
	resume_button = _add(tr("Resume"), func() -> void: resumed.emit(), StatIcon.CONTINUE)
	resume_button.name = "Resume"
	# §5.3: one primary per state.
	resume_button.theme_type_variation = UiTheme.PRIMARY
	_relabel()
	Settings.hints_changed.connect(_relabel)
	_add(tr("Options"), show_options, StatIcon.SETTINGS)
	_add(tr("Codex"), show_codex, StatIcon.CODEX)
	_add(tr("Save & quit to title"), func() -> void:
		if RunManager.campaign != null:
			RunManager.autosave()
		quit_to_title.emit(), StatIcon.SAVE)
	_add(tr("Quit to desktop"), _confirm_quit, StatIcon.QUIT)
	# H24 S11 / §6.5: the campaign's share code in a mono field with a copy button.
	var code := share_code()
	if code != "":
		var row := VBoxContainer.new()
		row.name = "CodeRow"
		row.add_theme_constant_override("separation", 0)
		var head := Label.new()
		head.name = "CodeHeading"
		head.text = code_heading()
		UiWrap.whole_words(head)  # art pass W9F §4.3.3: whole words, never mid-word
		head.add_theme_color_override("font_color", Palette.TEXT_MID)
		head.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
		row.add_child(head)
		code_field = CodeField.new(code, true, tr("Copy the campaign code"))
		code_field.name = "SeedLine"
		code_field.tooltip_text = UiTip.fold(tr("Share this code: Start from code on the new campaign screen starts this campaign again."))
		code_field.field.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		row.add_child(code_field)
		_menu.add_child(row)
	# §5.2: the prompt bar at the menu's foot while a pad is in use.
	prompts = PadPrompts.new()
	prompts.name = "PadPrompts"
	_menu.add_child(prompts)
	_relabel()
	# Focus moves slide the highlight and type the line in (Animation pass ANIM-6).
	MenuMotion.attach(_menu)
	# ANIM-R5 P4: as tall as what it shows; Options and the Codex grow it up to MENU_SIZE.
	_host.minimum_size_changed.connect(_fit_height)
	_fit_height()


## The campaign's share code alone ("" without a campaign).
static func share_code() -> String:
	var c := RunManager.campaign
	if c == null or RunManager.corporation == null:
		return ""
	return CampaignCode.of(c, c.start_class_id)


## The words over the code field, in the player's language.
static func code_heading() -> String:
	return TranslationServer.translate("Campaign code (share it: it starts this campaign)") + (
		TranslationServer.translate(" (local: REBEL_CELL is built from your profile)") if RunManager.corporation != null and RunManager.corporation.generated_from_profile else "")


## The campaign's share code as a line (H24 S11), in the player's language; "" without a
## campaign.
static func code_line() -> String:
	var c := RunManager.campaign
	if c == null or RunManager.corporation == null:
		return ""
	return TranslationServer.translate("Campaign code (share it: it starts this campaign): %s%s") % [CampaignCode.of(c, c.start_class_id),
		TranslationServer.translate(" (local: REBEL_CELL is built from your profile)") if RunManager.corporation.generated_from_profile else ""]


## The menu's size: its glass's own (title, margins) plus what it holds, never over
## MENU_SIZE nor past the screen's bottom less FIT_MARGIN (it scrolls inside then). Narrow
## round its lines; MENU_SIZE wide while Options or the Codex are open. Centred on the box
## its host placed.
func _fit_height() -> void:
	if _panel == null or _host == null:
		return
	var want := _panel.get_combined_minimum_size().y + _host.get_combined_minimum_size().y
	var most := MENU_SIZE.y
	if is_inside_tree():
		most = minf(most, get_viewport_rect().size.y - global_position.y - FIT_MARGIN)
	var h := clampf(ceilf(want), minf(FIT_MIN_H, most), most)
	var w := MENU_SIZE.x
	if not _sub_open():
		var inner := maxf(_menu.get_combined_minimum_size().x, _panel.title_rect().size.x)
		w = minf(MENU_SIZE.x, ceilf(inner + UiTheme.PANEL_PAD_H * 2 + UiTheme.SP_M))
	if is_nan(_centre_x) and is_inside_tree():
		_centre_x = position.x + MENU_SIZE.x * 0.5
	custom_minimum_size = Vector2(w, h)
	size = custom_minimum_size
	if not is_nan(_centre_x):
		position.x = roundf(_centre_x - w * 0.5)
	_cover_screen()


func _sub_open() -> bool:
	return (settings_panel != null and is_instance_valid(settings_panel)) or (codex_note != null and is_instance_valid(codex_note))


## The menu's glass (it drops in when the menu opens, Animation pass ANIM-6).
var _panel: ZinePanel = null


func _notification(what: int) -> void:
	if what == NOTIFICATION_READY and _panel != null:
		if code_field != null:
			# The whole code shows in its field (the field's own least width is a seed's).
			var px := UiTheme.font_px(UiTheme.BODY)
			code_field.field.custom_minimum_size.x = ceilf(Palette.mono().get_string_size(code_field.value + "  ", HORIZONTAL_ALIGNMENT_LEFT, -1, px).x) + UiTheme.SP_M
		_fit_height()
		# A wrapped line (the code heading at 1.6) knows its height only once laid out at its
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


func _add(text: String, on_pressed: Callable, kind: StringName) -> Button:
	var b := Button.new()
	b.text = text
	b.theme_type_variation = &"MenuItem"
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.pressed.connect(on_pressed)
	IconMark.attach(b, kind)
	_menu.add_child(b)
	return b


func _confirm_quit() -> void:
	var confirm := ConfirmDialog.new(tr("Quit REBEL_CELL? Progress is autosaved."))
	confirm.name = "QuitConfirm"
	confirm.position = Vector2(UiTheme.SP_XXL, UiTheme.SP_XXL * 2)
	# §3.3 / §5.3: a modal over a SCRIM, opened as a modal (<= 0.22 s).
	var scrim := GlassScrim.new()
	scrim.name = "ModalScrim"
	scrim.top_level = true
	scrim.show_behind_parent = true
	scrim.mouse_filter = Control.MOUSE_FILTER_STOP
	confirm.add_child(scrim)
	add_child(confirm)
	scrim.size = get_viewport_rect().size
	confirm.confirmed.connect(func() -> void: RunManager.quit_game())
	PageTransition.open_modal(confirm)


## "Resume [Esc]" / "Resume [Start]": the hint follows the device and the binds (H20).
func _relabel() -> void:
	# §12: with a pad the prompt bar names the buttons; the words carry no "[Menu]".
	var hint := "" if Settings.pad_active else Settings.hint(&"open_settings")
	resume_button.text = ("%s %s" % [tr("Resume"), hint]).strip_edges()
	if prompts != null:
		prompts.set_prompts([["ui_accept", "Select"], ["ui_cancel", "Resume"]])


func show_options() -> void:
	_close_sub()
	settings_panel = SettingsPanel.new()
	settings_panel.closed.connect(_close_sub)
	settings_panel.trap_focus = true
	settings_panel.own_prompts = true
	# As wide as the menu's glass allows; the menu itself scrolls past its height.
	settings_panel.fit_room(0.0, MENU_SIZE.x - UiTheme.PANEL_PAD_H * 2 - UiTheme.SP_M)
	_host.add_child(settings_panel)
	_fit_height()
	PageTransition.enter(settings_panel, PageTransition.Look.GLASS)
	UiWrap.fit(settings_panel)
	UiFocus.trap.call_deferred(settings_panel)
	UiFocus.focus_first(settings_panel)


func show_codex() -> void:
	_close_sub()
	var room := MENU_SIZE.x - UiTheme.PANEL_PAD_H * 2 - UiTheme.SP_M
	codex_note = CodexSpread.new(Codex.entries(RunManager.lookup(), RunManager.profile), CODEX_VIEW * Settings.text_scale, room)
	codex_note.name = "Codex"
	_host.add_child(codex_note)
	_fit_height()
	PageTransition.enter(codex_note, PageTransition.Look.PAPER)
	var back := Button.new()
	back.text = tr("Back")
	back.name = "CodexBack"
	back.theme_type_variation = UiTheme.SECONDARY
	back.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	IconMark.attach(back, StatIcon.BACK)
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
	_fit_height.call_deferred()
	UiFocus.trap.call_deferred(self)
	UiFocus.focus_first(_menu)


func _unhandled_input(event: InputEvent) -> void:
	if not visible:
		return
	if codex_note != null and event.is_action_pressed("ui_cancel"):
		_close_sub()  # Esc in the Codex returns to the menu, like Esc in Options
		get_viewport().set_input_as_handled()
		return
	if settings_panel == null and not PageTransition.modal_open(self) and (event.is_action_pressed("ui_cancel") or event.is_action_pressed("open_settings")):
		resumed.emit()
		get_viewport().set_input_as_handled()
		return
	# While the menu is open no hotkey reaches the game behind it (Space ending a turn,
	# 1-9 entering a map node): it is the last child, so it sees unhandled input first.
	if event is InputEventKey or event is InputEventJoypadButton or event is InputEventJoypadMotion:
		get_viewport().set_input_as_handled()
