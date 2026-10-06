class_name PauseMenu
extends Control
## Pause menu (gap analysis 2.5): Resume, Options (the SettingsPanel inline), Codex,
## Save & quit to title, Quit to desktop (confirmed). Scenes open it on Esc; it never
## changes game state itself beyond asking RunManager to save and switch scenes.
## ART-10 4C (ART_BIBLE v2 §4.13, §2.10; round 33 `abandon_dialog.jpg`, `ui_kit.jpg` MENU):
## a v2 terminal (`> PAUSED // WHERE`), its lines in terminal CAPS with the `>` caret and
## lime brackets on focus; the Codex as terminal text, the Options single-column inside it,
## the quit confirm in the abandon dialog's look.
## M14 parity PAUSE-01..03 (designer 2026-10-05): the page behind is blurred and darkened
## (GlassScrim, as every other modal); no PAUSED sticker (the raid plays on under the menu,
## so no running raid is paused). PAUSE-02, ported from art-m13-final
## scripts/ui/kit/pause_menu.gd: `Resume [Esc]` is the one pink verb sticker, the other rows
## carry icons (StatIcon), the campaign code sits in a CodeField with a copy button.
## ABANDON-QUIT (designer ruling 2026-10-05, GDD 4.5): the in-run pause has "Abandon run", the
## campaign's pause (no run in progress) "Abandon campaign", both rows in HARM (as the slots'
## DELETE: the destructive verb's edge) asking with the abandon dialog (ExitDialogs); "Quit to
## desktop" asks with the quit confirm and its key hints. The answers go to RunManager.

signal resumed
signal quit_to_title

var settings_panel: SettingsPanel = null
var codex_note: CrtText = null
var _menu: VBoxContainer
## The icon rows under Resume (they carry the menu motion; Resume is a sticker).
var _rows: VBoxContainer
## The campaign code field (null without a campaign).
var code_field: CodeField = null
var _host: VBoxContainer
var resume_button: Button
## ABANDON-QUIT: the destructive rows (null when the menu has none) and the open exit dialog.
var abandon_run_button: Button = null
var abandon_campaign_button: Button = null
var exit_dialog: ConfirmDialog = null
## Who had focus before the menu opened (the combat hand); it gets it back on close.
var _return_focus: Control = null


## Menu size: wide enough for the Controls grid and Accessibility switches at text scale
## 1.6 (the content scrolls vertically inside it).
const MENU_SIZE := Vector2(760, 520)
## Resume's sticker lettering (px at text scale 1.0) and its tilt.
const RESUME_PX := 28.0
const RESUME_TILT := -1.5


## Full-screen, click-eating backdrop behind the menu: no click reaches the game (H17).
var _backdrop: GlassScrim


func _init() -> void:
	custom_minimum_size = MENU_SIZE
	# ANIM-R3 A2: motion helpers leave presses to an open pause menu (MotionSkip.pause_open).
	add_to_group(MotionSkip.PAUSE_GROUP)
	_backdrop = GlassScrim.new()  # PAUSE-01: the page behind blurred and dimmed (SCRIM)
	_backdrop.name = "Backdrop"
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
	_menu.name = "Menu"
	_host.add_child(_menu)
	# PAUSE-02: the one primary, a pink verb sticker (its words are given whole by _relabel).
	var resume := VerbSticker.new(tr("Resume"), VerbSticker.Fill.PINK, RESUME_PX, RESUME_TILT)
	resume.pre_translated = true
	resume.name = "Resume"
	resume.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	resume.pressed.connect(func() -> void: resumed.emit())
	_menu.add_child(resume)
	resume_button = resume
	_rows = VBoxContainer.new()
	_rows.name = "Rows"
	_menu.add_child(_rows)
	_relabel()
	Settings.hints_changed.connect(_relabel)
	_add(tr("Options"), show_options, StatIcon.SETTINGS)
	_add(tr("Codex"), show_codex, StatIcon.CODEX)
	_add(tr("Save & quit to title"), func() -> void:
		if RunManager.campaign != null:
			RunManager.autosave()
		quit_to_title.emit(), StatIcon.SAVE)
	# ABANDON-QUIT: in a run, abandon it; at HQ (a live campaign, no run), abandon the campaign.
	if RunManager.has_active_run():
		abandon_run_button = _add(tr("Abandon run"), confirm_abandon_run, StatIcon.OPERATIVE)
		abandon_run_button.name = "AbandonRun"
		_harm(abandon_run_button)
	elif RunManager.has_campaign():
		abandon_campaign_button = _add(tr("Abandon campaign"), confirm_abandon_campaign, StatIcon.CAMPAIGNS)
		abandon_campaign_button.name = "AbandonCampaign"
		_harm(abandon_campaign_button)
	var quit := _add(tr("Quit to desktop"), confirm_quit, StatIcon.QUIT)
	quit.name = "Quit"
	# H24 S11 / PAUSE-02: the campaign's share code in a mono field with a copy button (it
	# read like debug output on the HQ's Pirate Radio note, then as a plain line here).
	var code := share_code()
	if code != "":
		var row := VBoxContainer.new()
		row.name = "CodeRow"
		var head := Label.new()
		head.name = "CodeHeading"
		head.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		head.text = code_heading()
		UiWrap.whole_words(head)  # ART-0 F (art pass W9F §4.3.3): whole words, never mid-word
		head.add_theme_color_override("font_color", Palette.TEXT_MID)
		head.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
		row.add_child(head)
		code_field = CodeField.new(code, true, tr("Copy the campaign code"))
		code_field.name = "SeedLine"
		code_field.tooltip_text = UiTip.fold(tr("Share this code: Start from code on the new campaign screen starts this campaign again."))
		code_field.field.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		code_field.copy_button.tooltip_auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		row.add_child(code_field)
		_menu.add_child(row)
	# Focus moves slide the highlight and type the line in (Animation pass ANIM-6).
	MenuMotion.attach(_rows)
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


## The least the menu is tall and the screen edge it keeps clear of (px).
const FIT_MIN_H := 120.0
const FIT_MARGIN := 12.0


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


## The menu's glass (it drops in when the menu opens, Animation pass ANIM-6).
var _panel: CrtWindow = null


func _notification(what: int) -> void:
	if what == NOTIFICATION_READY and _panel != null:
		if code_field != null:
			# The whole code shows in its field (the field's own least width is a seed's).
			var px := UiTheme.font_px(UiTheme.BODY)
			code_field.field.custom_minimum_size.x = ceilf(Palette.mono().get_string_size(code_field.value + "  ", HORIZONTAL_ALIGNMENT_LEFT, -1, px).x) + UiTheme.SP_M
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


func _add(text: String, on_pressed: Callable, kind: StringName) -> Button:
	var b := Button.new()
	b.text = text
	# ART-10 4C: a terminal menu line (`> ITEM` on focus, lime brackets), CAPS.
	b.theme_type_variation = &"MenuItem"
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.add_theme_font_override(&"font", Chrome.caps_font(UiTheme.BODY))
	b.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.BODY))
	b.set_meta(UiFocus.META_NO_SCALE, true)
	b.pressed.connect(on_pressed)
	IconMark.attach(b, kind)  # PAUSE-02: the row's icon (StatIcon), in the chevron's place
	_rows.add_child(b)
	return b


## ABANDON-QUIT: a destructive row reads in HARM (its words and its icon), as the slots' DELETE.
func _harm(b: Button) -> void:
	for key in [&"font_color", &"font_hover_color", &"font_focus_color", &"font_pressed_color", &"font_hover_pressed_color"]:
		b.add_theme_color_override(key, Palette.HARM)
	IconMark.attach(b, IconMark.kind_of(b), Palette.HARM)


## Abandon run: the abandon dialog with the run's costs (RunManager.abandon_run_preview); BURN IT
## kills the operative (RunManager.abandon_run; the netrun scene shows the run's end).
func confirm_abandon_run() -> void:
	var p := RunManager.abandon_run_preview()
	if p.is_empty():
		return
	_open_exit(ExitDialogs.abandon_run(p), func() -> void:
		resumed.emit()
		RunManager.abandon_run())


## Abandon campaign: the abandon dialog with the campaign's costs; BURN IT ends it
## (RunManager.abandon_campaign) and HQ opens again on the campaign's end page.
func confirm_abandon_campaign() -> void:
	var p := RunManager.abandon_campaign_preview()
	if p.is_empty():
		return
	var corp := TextDb.t(RunManager.corporation, "display_name") if RunManager.corporation != null else String(p.get("corporation", ""))
	_open_exit(ExitDialogs.abandon_campaign(p, corp), func() -> void:
		resumed.emit()
		RunManager.abandon_campaign()
		RunManager.change_scene(RunManager.HQ_SCENE))


## Quit to desktop: the quit confirm (not destructive); QUIT saves and quits.
func confirm_quit() -> void:
	_open_exit(ExitDialogs.quit(RunManager.has_active_run()), func() -> void: RunManager.quit_game())


## Opens `d` over the menu, centred on the screen as its panel takes its size, `on_yes` on its
## confirm.
func _open_exit(d: ConfirmDialog, on_yes: Callable) -> void:
	if exit_dialog != null and is_instance_valid(exit_dialog):
		exit_dialog.queue_free()
	exit_dialog = d
	add_child(d)
	var centre := func() -> void:
		if is_instance_valid(d) and d.is_inside_tree():
			d.global_position = ((get_viewport_rect().size - d.size) * 0.5).floor()
	d.resized.connect(centre)
	centre.call()
	d.confirmed.connect(on_yes)


## "Resume [Esc]" / "Resume [Start]": the hint follows the device and the binds (H20).
func _relabel() -> void:
	(resume_button as VerbSticker).set_label(("%s %s" % [tr("Resume"), Settings.hint(&"open_settings")]).strip_edges())


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
