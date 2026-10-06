class_name PauseMenu
extends Control
## Pause menu (gap analysis 2.5; M14 parity PAUSE-01..03, designer 2026-10-05 and the layout
## of the same day). Scenes open it on Esc; it never changes game state itself beyond asking
## RunManager to save, abandon and switch scenes.
## - The page behind is blurred and darkened (GlassScrim, as every other modal); no PAUSED sticker.
## - Two columns of vinyl stickers (the kit's VinylSticker through HoloSticker, each always in its
##   role's colour; the focused one lifts and runs the gloss sweep, no brackets). LEFT: RESUME
##   (pink, the one primary, its key hint beside it), OPTIONS (the SettingsPanel inline), CODEX.
##   RIGHT: ABANDON CAMPAIGN (at HQ; ABANDON RUN in a run: the same slot, ABANDON-QUIT, GDD 4.5,
##   harm red, asking with ExitDialogs, hold to confirm), QUIT TO MAIN MENU (saves, returns to the
##   title, whose Continue resumes it), QUIT TO DESKTOP (the quit confirm, not destructive).
## - Grease-pencil notes (the kit's PencilWords): "Down with the Oligarchy!" under Resume,
##   "No Going Back" (red) under the abandon sticker, "Come Back Soon" under Quit to desktop; they
##   drop out when big text leaves no room.
## - The campaign code sits in a CodeField with a copy button on the bottom row.
## ART-10 4C kept: the v2 terminal glass (`> PAUSED // WHERE`), the Codex as terminal text, the
## Options single-column inside it.

signal resumed
signal quit_to_title

var settings_panel: SettingsPanel = null
var codex_note: CrtText = null
var _menu: VBoxContainer
## The two columns of stickers (left: Resume, Options, Codex; right: abandon, quit to the main
## menu, quit to the desktop) and their box.
var _columns: HBoxContainer
var _left: VBoxContainer
var _right: VBoxContainer
## The key hint beside Resume (`[Esc]`, or the pad's button).
var resume_hint: Label = null
## Every sticker with its grease-pencil note (null when it has none), in focus order.
var _stickers: Array[HoloSticker] = []
var _notes: Array[PencilWords] = []
## Resume's note: beside the sticker, or (when the width is short) below its key hint; and where it stands now.
var _resume_beside: PencilWords = null
var _resume_below: PencilWords = null
enum NoteMode { BESIDE, BELOW, NONE }
var note_mode: NoteMode = NoteMode.BESIDE
## The abandon and quit notes (below their stickers) show.
var _other_notes: bool = true
## The campaign code field (null without a campaign).
var code_field: CodeField = null
var _host: VBoxContainer
var resume_button: HoloSticker
## ABANDON-QUIT: the destructive rows (null when the menu has none) and the open exit dialog.
var abandon_run_button: Button = null
var abandon_campaign_button: Button = null
var exit_dialog: ConfirmDialog = null
## Who had focus before the menu opened (the combat hand); it gets it back on close.
var _return_focus: Control = null


## Menu size: wide enough for the Controls grid and Accessibility switches at text scale
## 1.6 (the content scrolls vertically inside it).
const MENU_SIZE := Vector2(760, 520)
## Sticker lettering (px at text scale 1.0): Resume, and every other row. Stickers follow the
## player's text size up to STICKER_SCALE_MAX (as VerbSticker.SCALE_MAX: the pair of columns must fit).
const RESUME_PX := 34
const ROW_PX := 22
const STICKER_SCALE_MAX := 1.5
## The grease-pencil notes: type step and tilt (deg) under Resume, the abandon sticker and quit.
const NOTE_STEP := UiTheme.LABEL
const RESUME_NOTE_TILT := -2.0
const ABANDON_NOTE_TILT := 1.5
const QUIT_NOTE_TILT := -1.5


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
	# PAUSE-02 (designer layout 2026-10-05): two columns of vinyl stickers, each always in its
	# role's colour. LEFT: Resume (the one pink verb), Options, Codex. RIGHT: Abandon campaign /
	# Abandon run (harm red; only with a campaign), Quit to Main Menu, Quit to desktop.
	_columns = HBoxContainer.new()
	_columns.name = "Columns"
	_columns.add_theme_constant_override(&"separation", UiTheme.SP_XL)
	_menu.add_child(_columns)
	_left = _column("Left")
	_right = _column("Right")
	var resume_cell := _cell(_left, "Resume", tr("Resume"), VinylSticker.Fill.PINK, RESUME_PX, resumed.emit,
		tr("Down with the Oligarchy!"), Palette.PENCIL_PLAN, RESUME_NOTE_TILT, true)
	resume_button = resume_cell
	resume_hint = Label.new()
	resume_hint.name = "ResumeHint"
	resume_hint.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	resume_hint.add_theme_font_override(&"font", Palette.mono())
	resume_hint.add_theme_font_size_override(&"font_size", UiTheme.font_px(UiTheme.LABEL))
	resume_hint.add_theme_color_override(&"font_color", Palette.CELL_PINK)
	resume_hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var resume_box := resume_cell.get_parent().get_parent()  # the cell: [sticker + note beside], hint, note below
	resume_box.add_child(resume_hint)
	_resume_beside = _notes[0]
	_resume_below = PencilWords.new(_resume_beside.words, RESUME_NOTE_TILT)
	_resume_below.color = _resume_beside.color
	_resume_below.step = NOTE_STEP
	_resume_below.name = "ResumeNoteBelow"
	_resume_below.visible = false
	resume_box.add_child(_resume_below)
	_notes.append(_resume_below)
	_relabel()
	Settings.hints_changed.connect(_relabel)
	_cell(_left, "Options", tr("Options"), VinylSticker.Fill.YELLOW, ROW_PX, show_options)
	_cell(_left, "Codex", tr("Codex"), VinylSticker.Fill.WHITE, ROW_PX, show_codex)
	# ABANDON-QUIT: in a run, abandon it; at HQ (a live campaign, no run), abandon the campaign.
	# Same slot (top right), same rules and dialogs (ExitDialogs, hold to confirm).
	if RunManager.has_active_run():
		abandon_run_button = _cell(_right, "AbandonRun", tr("Abandon run"), VinylSticker.Fill.RED, ROW_PX, confirm_abandon_run,
			tr("No Going Back"), Palette.PENCIL_THREAT, ABANDON_NOTE_TILT)
	elif RunManager.has_campaign():
		abandon_campaign_button = _cell(_right, "AbandonCampaign", tr("Abandon campaign"), VinylSticker.Fill.RED, ROW_PX, confirm_abandon_campaign,
			tr("No Going Back"), Palette.PENCIL_THREAT, ABANDON_NOTE_TILT)
	_cell(_right, "QuitMain", tr("Quit to Main Menu"), VinylSticker.Fill.WHITE, ROW_PX, func() -> void:
		if RunManager.campaign != null:
			RunManager.autosave()
		quit_to_title.emit())
	_cell(_right, "Quit", tr("Quit to desktop"), VinylSticker.Fill.HOLO, ROW_PX, confirm_quit,
		tr("Come Back Soon"), Palette.PENCIL_PLAN, QUIT_NOTE_TILT)
	_link_columns()
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
	want = _fit_notes(want, most)
	var h := clampf(ceilf(want), minf(FIT_MIN_H, most), most)
	custom_minimum_size = Vector2(MENU_SIZE.x, h)
	size = custom_minimum_size


## The grease-pencil notes (designer 2026-10-05): Resume's sits BESIDE its sticker when the two columns
## still fit the menu's width; else BELOW its key hint; else (big text) every note drops. The abandon and quit
## notes sit below their stickers and drop with it. Returns the menu's wanted height with the notes as set.
func _fit_notes(want: float, most: float) -> float:
	var bare := want - _notes_extra_h(note_mode, _other_notes)
	var budget := MENU_SIZE.x - UiTheme.SP_XL
	var modes: Array = [[NoteMode.BESIDE, true], [NoteMode.BELOW, true], [NoteMode.NONE, false]]
	var pick: Array = modes[2]
	for m in modes:
		if _columns_width(m[0], m[1]) <= budget and bare + _notes_extra_h(m[0], m[1]) <= most:
			pick = m
			break
	note_mode = pick[0]
	_other_notes = pick[1]
	if _resume_beside != null:
		_resume_beside.visible = note_mode == NoteMode.BESIDE
		_resume_below.visible = note_mode == NoteMode.BELOW
	for n in _notes:
		if n != _resume_beside and n != _resume_below:
			n.visible = _other_notes
	return bare + _notes_extra_h(note_mode, _other_notes)


## The two columns' width (px) with Resume's note in `mode` and the other notes shown or not: the widest
## line of each column (Resume's sticker and note side by side count together), and the gap between.
func _columns_width(mode: NoteMode, others: bool) -> float:
	var total := float(_columns.get_theme_constant(&"separation"))
	for col in [_left, _right]:
		var w := 0.0
		for cell in (col as Control).get_children():
			for c in cell.get_children():
				var line := 0.0
				if c is HBoxContainer:  # Resume: the sticker and the note beside it
					for part in c.get_children():
						if part is PencilWords:
							line += (float(c.get_theme_constant(&"separation")) + (part as PencilWords).get_minimum_size().x) if mode == NoteMode.BESIDE else 0.0
						else:
							line += (part as Control).get_combined_minimum_size().x
				elif c is PencilWords:
					var is_resume := c == _resume_below
					if (is_resume and mode == NoteMode.BELOW) or (not is_resume and others):
						line = (c as PencilWords).get_minimum_size().x
				elif c is Label:
					line = 0.0
				else:
					line = (c as Control).get_combined_minimum_size().x
				w = maxf(w, line)
		total += w
	return total


## The height the notes add to the taller column (px) for Resume's note in `mode`.
func _notes_extra_h(mode: NoteMode, others: bool) -> float:
	var left := _resume_below.get_minimum_size().y if _resume_below != null and mode == NoteMode.BELOW else 0.0
	var right := 0.0
	if others:
		for n in _notes:
			if n != _resume_beside and n != _resume_below and not _left.is_ancestor_of(n):
				right += n.get_minimum_size().y
	return maxf(left, right)


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


## One column of the sticker grid.
func _column(p_name: String) -> VBoxContainer:
	var c := VBoxContainer.new()
	c.name = p_name
	c.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	c.add_theme_constant_override(&"separation", UiTheme.SP_M)
	_columns.add_child(c)
	return c


## A sticker `p_name` in `col`: the word (caps), its colour `fill`, its press, and under it a
## grease-pencil note when given. Stickers always show their colour; the focused one lifts and
## runs the kit's gloss sweep (ambient while it has focus). Returns the sticker button.
func _cell(col: VBoxContainer, p_name: String, word: String, fill: int, px: int, on_pressed: Callable,
		note: String = "", ink: Color = Palette.PENCIL_PLAN, tilt: float = 0.0, beside: bool = false) -> HoloSticker:
	var cell := VBoxContainer.new()
	cell.name = p_name + "Cell"
	cell.add_theme_constant_override(&"separation", 0)
	col.add_child(cell)
	var b := HoloSticker.word(word.to_upper(), fill, minf(Settings.text_scale, STICKER_SCALE_MAX), px)  # (it divides by the text scale itself)
	b.name = p_name
	b.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	b.pressed.connect(on_pressed)
	b.focus_entered.connect(func() -> void: b.sticker.ambient_sweep = true)
	b.focus_exited.connect(func() -> void: b.sticker.ambient_sweep = false)
	var row: Container = cell
	if beside:
		row = HBoxContainer.new()
		row.name = p_name + "Row"
		row.add_theme_constant_override(&"separation", UiTheme.SP_M)
		cell.add_child(row)
	row.add_child(b)
	_stickers.append(b)
	if note != "":
		var n := PencilWords.new(note, tilt)
		n.color = ink
		n.step = NOTE_STEP
		n.name = p_name + "Note"
		row.add_child(n)
		_notes.append(n)
	return b


## Left / Right cross the columns on the same row; Up / Down walk a column (focus order: the left
## column top-down, the right column top-down, then the code field).
func _link_columns() -> void:
	var l := _left.get_children().map(func(c: Node) -> Control: return c.get_child(0) as Control)
	var r := _right.get_children().map(func(c: Node) -> Control: return c.get_child(0) as Control)
	for i in l.size():
		if r.is_empty():
			break
		var other: Control = r[mini(i, r.size() - 1)]
		(l[i] as Control).focus_neighbor_right = (l[i] as Control).get_path_to(other)
	for i in r.size():
		var other: Control = l[mini(i, l.size() - 1)]
		(r[i] as Control).focus_neighbor_left = (r[i] as Control).get_path_to(other)


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
	if resume_hint != null:
		resume_hint.text = Settings.hint(&"open_settings")


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
