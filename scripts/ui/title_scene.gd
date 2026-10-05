extends Control
## Title / main menu (gap analysis 2.5): Continue, Campaigns (three save slots with a
## summary, new / load / delete with confirmation), Tutorial, Codex, Stats &
## achievements, Options, Quit. Every action goes through RunManager; the scene only
## displays state.
## ART-10 4C (ART_BIBLE v2 §4.13 title option A "the plan", D10; round 33 `title_screen.jpg`,
## `title_screen_alt_simulate.jpg`): the REBEL_CELL neon sign over the living night city;
## three numbered vinyl verbs on terminal chips (1. BREACH = Continue with the slot summary,
## default focus; 2. SIMULATE = Tutorial; 3. OVERTHROW = New campaign); the rest in a terminal
## MORE panel with key hints; the profile in a terminal panel; pad prompts; the ON AIR
## ticker. The sub-pages carry a yellow title sticker over a v2 terminal.

const SLOTS: Array[String] = ["1", "2", "3"]
## Subtitle lines the header band holds.
const HEADER_LINES := 2
## The verb stickers' lettering size (px at 1280x720, text scale 1.0) and tilts.
const VERB_PX := 36.0
const VERB_TILTS: Array[float] = [-2.0, 1.5, -1.0]
## The page's title sticker size and tilt.
const TITLE_STICKER_PX := 30.0
const TITLE_STICKER_TILT := -3.0
## The motto's tilt (degrees).
const MOTTO_TILT := 3.0
## Margins of the page (px): sides, top, bottom (the ticker's room is added).
const PAGE_MARGIN := Vector3(40, 22, 8)
## Gaps (px): sign to the verbs, between verb rows, a sticker to its chip.
const GAP_SIGN := 14
const GAP_ROWS := 4
const GAP_CHIP := 22
## The verbs' chips' least width (px at text scale 1.0).
const CHIP_MIN_W := 300.0
## The MORE panel's and the profile panel's least widths (px at text scale 1.0).
const MORE_W := 300.0
const PROFILE_W := 290.0
## From this text scale the MORE panel moves to the right column (the left one is full).
const MORE_RIGHT_FROM := 1.6
## The city's dim behind the title (it reads as the backdrop, round 33's blurred city).
const CITY_DIM := 0.58
## The page widths for the codex / stats / slots terminals (px at 1.0) and the codex text's
## least height.
const PAGE_W := 900.0
const SLOTS_W := 620.0
const CODEX_H := 420.0
const STATS_H := 200.0
const HISTORY_H := 150.0
## The ON AIR ticker's words (keys; round 33's ticker).
const TICKER_WORDS := ["PIRATE RADIO 88.1", "HALCYON RAISES FARES AGAIN"] # TR
## The confirm's caption under CANCEL (a key).
const CONFIRM_WORDS := ["keep going [B]"] # TR

var background: CyberdeckBackground
## The subtitles' band (H21 #11), top right, clear of every menu.
var subtitle_strip: SubtitleStrip
var margin: MarginContainer
var ticker: OnAirTicker
var _panel_host: VBoxContainer
var _panel: Control = null
var panel_name: String = ""
var _confirm: ConfirmDialog = null
## The slot the Continue line offers ("" = the newest numbered slot, RunManager.latest_slot).
## H24 S13: the storyboard shows its own private slot, so its title matches its HQ.
var continue_slot: String = ""
## The three verb stickers on the main page (BREACH, SIMULATE, OVERTHROW), for tests.
var verbs: Array[VerbSticker] = []


func _ready() -> void:
	UiTheme.apply(self)
	# Capture variants (ANIM-6): --demo-set / --demo-speed tune a copy of the motion table.
	MotionDemo.apply_args()
	Dialogue.dock_default()
	background = CyberdeckBackground.new()
	add_child(background)
	var dim := ColorRect.new()
	dim.name = "CityDim"
	dim.color = Color(Palette.NET_BG_OUTER, CITY_DIM)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(dim)
	ticker = OnAirTicker.new(PackedStringArray([tr(TICKER_WORDS[0]), tr(TICKER_WORDS[1])]))
	ticker.anchor_left = 0.0
	ticker.anchor_right = 1.0
	ticker.anchor_top = 1.0
	ticker.anchor_bottom = 1.0
	ticker.grow_vertical = Control.GROW_DIRECTION_BEGIN
	margin = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", int(PAGE_MARGIN.x))
	margin.add_theme_constant_override("margin_right", int(PAGE_MARGIN.x))
	margin.add_theme_constant_override("margin_top", int(PAGE_MARGIN.y))
	margin.add_theme_constant_override("margin_bottom", int(PAGE_MARGIN.z + ticker.get_combined_minimum_size().y))
	add_child(margin)
	add_child(ticker)
	_panel_host = VBoxContainer.new()
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	margin.add_child(_panel_host)
	# The subtitles' band, top right (H21 #11): no menu under it.
	subtitle_strip = SubtitleStrip.new(HEADER_LINES)
	subtitle_strip.anchor_left = 0.55
	subtitle_strip.anchor_right = 1.0
	subtitle_strip.offset_right = -PAGE_MARGIN.x
	subtitle_strip.offset_top = PAGE_MARGIN.y
	add_child(subtitle_strip)
	AudioDirector.play_music("hq")
	var args := OS.get_cmdline_user_args()
	# The main menu drifts slowly over the whole city.
	background.city.pan = true
	for a in args:
		if a.begins_with("--demo-district="):
			background.city.pan = false
			background.set_district(StringName(a.trim_prefix("--demo-district=")))
		elif a.begins_with("--demo-ink="):
			background.city.ink_set = int(a.trim_prefix("--demo-ink="))
		elif a.begins_with("--demo-jitter="):
			var parts := a.trim_prefix("--demo-jitter=").split(",")
			(background.city.material as ShaderMaterial).set_shader_parameter("wobble", float(parts[0]))
			(background.city.material as ShaderMaterial).set_shader_parameter("jitter", float(parts[1]))
		elif a.begins_with("--demo-texture="):
			background.city.face_texture = int(a.trim_prefix("--demo-texture="))
		elif a == "--demo-cultures":
			background.city.cultures = {&"solace": "arabic", &"meridian": "chinese", &"halcyon": "egyptian", &"orbital": "english"}
			background.city.refresh()
		elif a.begins_with("--demo-bigoverview="):
			# Design review: the whole city at a given zoom in a big window.
			var city := background.city
			city.pan = false
			var z := float(a.trim_prefix("--demo-bigoverview="))
			city.territory_labels = true
			city.scale = Vector2(z, z)
			city.offset_right = get_viewport_rect().size.x * (1.0 / z - 1.0)
			city.offset_bottom = get_viewport_rect().size.y * (1.0 / z - 1.0)
			_hide_chrome()
		elif a == "--demo-nopan":
			background.city.pan = false
		elif a == "--demo-overview":
			# Design review: the whole city zoomed out, menus hidden.
			var city := background.city
			city.pan = false
			var z := 0.26
			city.territory_labels = true
			city.scale = Vector2(z, z)
			city.offset_right = 1280.0 * (1.0 / z - 1.0)
			city.offset_bottom = 720.0 * (1.0 / z - 1.0)
			_hide_chrome()
	if args.has("--demo-options"):
		show_options()
	elif args.has("--demo-slots"):
		show_slots()
	elif args.has("--demo-codex"):
		show_codex()
	elif args.has("--demo-stats"):
		show_stats()
	else:
		show_main()


func _hide_chrome() -> void:
	margin.visible = false
	ticker.visible = false
	(get_node("CityDim") as CanvasItem).visible = false


# --- Panels -----------------------------------------------------------------------------------

func _set_panel(p: Control, name: String) -> void:
	# ART-0 F (ported from art-pass W8a, ART_BIBLE v1 §10 rule 6): an open modal (a confirm)
	# closes before the page changes.
	if PageTransition.modal_open(self):
		PageTransition.after_modals(self, _set_panel.bind(p, name))
		return
	if _panel != null:
		_panel.queue_free()
	_panel = p
	# ANIM-6: each page enters (glass slides in, back to the main menu from the left; paper
	# drops); focus lands when it ends.
	var back := name == "main" and panel_name != ""
	panel_name = name
	# The sub-pages start under the subtitles' band (H21 #11); the main page keeps its top
	# left for the sign (the band sits top right, clear of it).
	margin.add_theme_constant_override("margin_top", int(PAGE_MARGIN.y if name == "main" else SubtitleStrip.top_below(PAGE_MARGIN.y)))
	# H24 S4: the page shows its words as given (translated once where built).
	TextDb.shown_as_given(p)
	_panel_host.add_child(p)
	Dialogue.enter_screen("title")
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	var first := _default_focus(p)
	PageTransition.enter(p, PageTransition.look_of(p), (func() -> void: first.grab_focus()) if first != null else UiFocus.focus_first.bind(p), -1 if back else 1)


## The control a page focuses first: BREACH (or the first live verb) on the main page.
func _default_focus(p: Control) -> Control:
	if panel_name != "main" or p != _panel:
		return null
	for v in verbs:
		if is_instance_valid(v) and not v.disabled:
			return v
	return null


func show_main() -> void:
	var page := Control.new()
	page.name = "MainPage"
	page.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var left := VBoxContainer.new()
	left.name = "LeftColumn"
	left.add_theme_constant_override("separation", GAP_SIGN)
	page.add_child(left)
	var sign := NeonSign.new()
	sign.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	left.add_child(sign)
	# The motto in grease pencil, written across the sign's lower right corner (round 33); it
	# takes no room of its own.
	var motto := PencilWords.new(tr("NEVER SLEEP"), MOTTO_TILT, true)
	motto.name = "Motto"
	var mm := motto.get_combined_minimum_size()
	motto.position = Vector2(NeonSign.BOARD.x - mm.x * 0.55, NeonSign.BOARD.y - mm.y * 0.15)
	motto.size = mm
	page.add_child(motto)
	motto.visible = not big_text()  # big text: the chips take its room
	# The plan: three numbered verbs, each on its terminal chip.
	var plan := HBoxContainer.new()
	plan.name = "Plan"
	plan.add_theme_constant_override("separation", 8)
	plan.custom_minimum_size.y = 0
	var rows := VBoxContainer.new()
	rows.name = "Verbs"
	rows.add_theme_constant_override("separation", GAP_ROWS)
	plan.add_child(PencilPlan.new(rows))
	plan.add_child(rows)
	left.add_child(plan)
	verbs.clear()
	var latest := continue_slot if continue_slot != "" else RunManager.latest_slot()
	var summary := RunManager.slot_summary(latest) if latest != "" else {}
	var cont_line := slot_text(latest, summary) if not summary.is_empty() else tr("no saved campaign yet")
	var breach := _verb(rows, "BREACH", VerbSticker.Fill.PINK, -1, "Continue", cont_line,
		(func() -> void: load_slot(latest)) if not summary.is_empty() else Callable(),
		"%s\n%s" % [tr("Pick up the campaign saved most recently."), slot_words(latest, summary)] if not summary.is_empty() else tr("No campaign is saved yet: OVERTHROW starts one."))
	breach.name = "Breach"
	_verb(rows, "SIMULATE", VerbSticker.Fill.GLITCH, -1, "Tutorial", tr("a practice run in a simulated net"), start_tutorial,
		tr("A guided first fight in a simulated net.")).name = "Simulate"
	_verb(rows, "OVERTHROW", VerbSticker.Fill.BLUE, "OVERTHROW".length() - 2, "New campaign", tr("pick a corporation to bring down"), new_campaign,
		tr("Start a new campaign: pick the corporation to bring down.")).name = "Overthrow"
	_align_verbs(rows)
	# MORE: the rest of the menu, with key hints.
	var more := CrtWindow.new(tr("MORE"))
	more.name = "More"
	more.tag_label.text = "v%s" % ProjectSettings.get_setting("application/config/version", "dev")
	more.tag_label.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	more.custom_minimum_size.x = MORE_W * maxf(1.0, Settings.text_scale * 0.7)
	var box := more.body
	box.name = "MoreList"
	_item(box, tr("Campaign slots"), show_slots, StatIcon.SLOTS, tr("The three campaign slots: start, load or delete."), "C")
	_item(box, tr("Codex"), show_codex, StatIcon.CODEX, tr("Everything the Cell knows: slices, cards, Firmware, Daemons, rules."), "X")
	_item(box, tr("Stats & achievements"), show_stats, StatIcon.STATS, tr("Your records, achievements and run history."), "S")
	_item(box, tr("Options"), show_options, StatIcon.SETTINGS, tr("Text size, sound, controls, subtitles."), "O")
	_item(box, tr("Quit"), confirm_quit, StatIcon.QUIT, tr("Leave REBEL_CELL (asks first)."), tr("ESC"))
	# ANIM-6: the highlight slides, the line types in, the caret blinks.
	MenuMotion.attach(box)
	var profile := _profile_panel()
	var foot := _foot()
	page.add_child(more)
	page.add_child(profile)
	# Big text: the right column is MORE; the profile is on the Stats page (it has the same tags).
	profile.visible = not big_text()
	page.add_child(foot)
	_place_bottom(profile, true)
	_place_bottom(foot, false, true)
	if big_text():
		# Big text: the left column is full; MORE heads the right column.
		more.anchor_left = 1.0
		more.anchor_right = 1.0
		more.grow_horizontal = Control.GROW_DIRECTION_BEGIN
		# Under the subtitles' band (H21 #11: no menu under it).
		more.offset_top = SubtitleStrip.top_below(PAGE_MARGIN.y) - PAGE_MARGIN.y
	else:
		_place_bottom(more, false)
		more.offset_bottom = -foot.get_combined_minimum_size().y - 6.0
	_set_panel(page, "main")


## True at big text (MORE_RIGHT_FROM and up): MORE heads the right column, the chips drop
## their second line (it stays in the tooltip), the motto and the profile panel make room.
func big_text() -> bool:
	return Settings.text_scale >= MORE_RIGHT_FROM


## Pins `c` to the page's bottom (right when `right`), growing up (and left).
func _place_bottom(c: Control, right: bool, full_width: bool = false) -> void:
	c.anchor_top = 1.0
	c.anchor_bottom = 1.0
	c.grow_vertical = Control.GROW_DIRECTION_BEGIN
	if full_width:
		c.anchor_left = 0.0
		c.anchor_right = 1.0
	elif right:
		c.anchor_left = 1.0
		c.anchor_right = 1.0
		c.grow_horizontal = Control.GROW_DIRECTION_BEGIN


## One numbered verb row: the sticker (it takes focus) and its terminal chip (the plain
## label and line; a click on it does the same). Returns the sticker.
func _verb(rows: Control, word: String, fill: int, fist: int, label: String, line: String, on_pressed: Callable, tip: String) -> VerbSticker:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", GAP_CHIP)
	row.alignment = BoxContainer.ALIGNMENT_BEGIN
	var s := VerbSticker.new(tr(word), fill, VERB_PX, VERB_TILTS[verbs.size()])
	s.pre_translated = true
	s.fist_at = fist
	s.tooltip_text = UiTip.fold(tip)
	# Big text (MORE_RIGHT_FROM): the chip keeps its label; its line moves into the tooltip.
	var chip := MenuChip.new(tr(label), line if not big_text() else "")
	chip.pre_translated = true
	chip.name = label.replace(" ", "")
	chip.focus_mode = Control.FOCUS_NONE
	chip.min_width = CHIP_MIN_W  # it grows with its label at big text
	chip.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	chip.tooltip_text = s.tooltip_text
	if on_pressed.is_valid():
		s.pressed.connect(on_pressed)
		chip.pressed.connect(on_pressed)
	else:
		s.disabled = true
		chip.disabled = true
	# The chip lights with its sticker (one control for the pad: the sticker).
	s.focus_entered.connect(func() -> void: KitState.force(chip, KitState.HOVER))
	s.focus_exited.connect(func() -> void: KitState.clear_force(chip))
	s.mouse_entered.connect(func() -> void: KitState.force(chip, KitState.HOVER))
	s.mouse_exited.connect(func() -> void: if not s.has_focus(): KitState.clear_force(chip))
	var slot := Control.new()
	slot.name = "StickerSlot"
	slot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	slot.add_child(s)
	row.add_child(slot)
	row.add_child(chip)
	rows.add_child(row)
	verbs.append(s)
	return s


## Gives every sticker slot the widest sticker's size, so the chips line up.
func _align_verbs(rows: Control) -> void:
	var w := 0.0
	var h := 0.0
	for v in verbs:
		var m := v.get_combined_minimum_size()
		w = maxf(w, m.x)
		h = maxf(h, m.y)
	for v in verbs:
		var slot := v.get_parent() as Control
		slot.custom_minimum_size = Vector2(w, h)
		v.position = Vector2(0, (h - v.size.y) * 0.5)
	rows = rows


## The profile at a glance (round 33 PROFILE // CELL-03): campaigns, won, best ICE, runs,
## raids held, badges; Stats has the rest. Live numbers in the terminal mono.
func _profile_panel() -> CrtWindow:
	var win := CrtWindow.new(tr("PROFILE // THE CELL"))
	win.name = "ProfileTags"
	win.custom_minimum_size.x = PROFILE_W * maxf(1.0, Settings.text_scale * 0.8)
	win.body.add_child(profile_grid(2))
	return win


## The profile's numbers as a grid of caption + value cells (`columns` wide): campaigns,
## won, best ICE, runs, raids held, badges.
static func profile_grid(columns: int) -> GridContainer:
	var p := RunManager.profile
	var grid := GridContainer.new()
	grid.name = "Tags"
	grid.columns = columns
	grid.add_theme_constant_override("h_separation", 28)
	grid.add_theme_constant_override("v_separation", 4)
	var items := [[TranslationServer.translate("CAMPAIGNS"), str(p.campaigns_started), TranslationServer.translate("Campaigns started on this profile.")],
		[TranslationServer.translate("WON"), str(p.campaigns_won), TranslationServer.translate("Campaigns won.")],
		[TranslationServer.translate("BEST ICE"), HudStats.ice_value(p.best_ice), TranslationServer.translate("The highest ICE level cleared (— until you clear one). Each corporation keeps its own ladder.")],
		[TranslationServer.translate("RUNS"), str(p.runs_completed), TranslationServer.translate("Netruns completed.")],
		[TranslationServer.translate("RAIDS HELD"), str(p.raids_won), TranslationServer.translate("Raids repelled.")],
		[TranslationServer.translate("BADGES"), "%d/%d" % [p.achievements.size(), Achievements.DEFS.size()], TranslationServer.translate("Achievements earned (Stats & achievements lists them).")]]
	for it in items:
		var cell := VBoxContainer.new()
		cell.add_theme_constant_override("separation", 0)
		cell.mouse_filter = Control.MOUSE_FILTER_PASS
		cell.tooltip_text = UiTip.fold(String(it[2]))
		var cap := Chrome.caps_label(String(it[0]), UiTheme.CAPTION, Palette.TEXT_MID)
		cap.name = "Caption"
		cell.add_child(cap)
		var value := Chrome.caps_label(String(it[1]), UiTheme.TITLE, Palette.TEXT_HI)
		value.name = "Value"
		value.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
		cell.add_child(value)
		grid.add_child(cell)
	return grid


## The page's foot: the build line (left) and the pad prompts (right).
func _foot() -> HBoxContainer:
	var foot := HBoxContainer.new()
	foot.name = "Foot"
	foot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var build := Chrome.caps_label(tr("REBEL_CELL v%s // cell uplink") % ProjectSettings.get_setting("application/config/version", "dev"), UiTheme.CAPTION, Palette.TEXT_LO)
	build.name = "Build"
	build.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	foot.add_child(build)
	var prompts := HBoxContainer.new()
	prompts.name = "Prompts"
	prompts.add_theme_constant_override("separation", 22)
	for p in [[JOY_BUTTON_A, tr("select")], [JOY_BUTTON_B, tr("back")], [JOY_BUTTON_Y, tr("codex")]]:
		prompts.add_child(PadPrompts.make_pair(int(p[0]), String(p[1])))
	foot.add_child(prompts)
	return foot


## A sub-page: its yellow title sticker over its terminal (round 33: screen titles are
## yellow stickers, §2.10).
func _page(title_word: String, content: Control, page_name: String) -> VBoxContainer:
	var box := VBoxContainer.new()
	box.name = page_name
	box.add_theme_constant_override("separation", 6)
	var head := HBoxContainer.new()
	var sticker := VerbSticker.new(tr(title_word), VerbSticker.Fill.YELLOW, TITLE_STICKER_PX, TITLE_STICKER_TILT)
	sticker.pre_translated = true
	sticker.name = "TitleSticker"
	sticker.focus_mode = Control.FOCUS_NONE
	sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	head.add_child(sticker)
	box.add_child(head)
	box.add_child(content)
	return box


func show_slots() -> void:
	var win := CrtWindow.new(tr("Campaign slots"))
	win.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	win.custom_minimum_size.x = SLOTS_W
	var box := win.body
	box.add_theme_constant_override("separation", 10)
	for slot in SLOTS:
		var row := VBoxContainer.new()
		row.name = "Slot%s" % slot
		row.add_theme_constant_override("separation", 2)
		var summary := RunManager.slot_summary(slot)
		row.add_child(Chrome.caps_label(tr("SLOT %s") % slot, UiTheme.LABEL, Palette.NET_CYAN))
		row.add_child(_label(_describe(summary)))
		var buttons := HFlowContainer.new()
		buttons.add_theme_constant_override("h_separation", 10)
		var s := slot
		if summary.is_empty():
			_item(buttons, tr("New campaign"), func() -> void: new_in_slot(s), StatIcon.PLAY, tr("Start a new campaign in slot %s.") % s)
		else:
			_item(buttons, tr("Load"), func() -> void: load_slot(s), StatIcon.CONTINUE, tr("Load the campaign in slot %s.") % s)
			_item(buttons, tr("Delete"), func() -> void: confirm_delete(s), StatIcon.QUIT, tr("Delete the campaign in slot %s (asks first).") % s)
		row.add_child(buttons)
		box.add_child(row)
	_item(box, tr("Back"), show_main, StatIcon.BACK, tr("Back to the main menu."))
	_set_panel(_page("CAMPAIGN SLOTS", win, "SlotsPage"), "slots")


func show_codex() -> void:
	var box := VBoxContainer.new()
	var note := CrtText.new(tr("CODEX // WHAT THE CELL KNOWS"), Vector2(PAGE_W, CODEX_H)).make_reference()
	note.name = "Codex"
	note.fill_codex()
	box.add_child(note)
	_item(box, tr("Back"), show_main, StatIcon.BACK, tr("Back to the main menu."))
	_set_panel(_page("CODEX", box, "CodexPage"), "codex")


func show_stats() -> void:
	var p := RunManager.profile
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 8)
	var records := CrtWindow.new(tr("PROFILE // THE CELL"))
	records.name = "Records"
	records.body.add_child(profile_grid(6))
	box.add_child(records)
	var note := CrtText.new(tr("STATS // RECORDS"), Vector2(PAGE_W, STATS_H)).make_reference()
	note.name = "Stats"
	note.append(tr("Campaigns: %d started, %d won, %d lost. Runs completed: %d. Operatives lost: %d. Raids: %d won / %d lost.") % [
		p.campaigns_started, p.campaigns_won, p.campaigns_lost, p.runs_completed, p.operatives_lost, p.raids_won, p.raids_lost])
	note.append(tr("Best ICE: %s. Perfects: %d. Racks captured: %d. Cycles earned: %d. Assisted wins: %d.") % [HudStats.ice_value(p.best_ice), int(p.stats.get("perfects", 0)), int(p.stats.get("racks", 0)), int(p.stats.get("cycles", 0)), int(p.stats.get("assisted_wins", 0))])
	var per_corp := PackedStringArray()
	for cid in RunManager.lookup().ids_of_class(&"CorporationData"):
		var corp := RunManager.lookup().get_content(cid) as CorporationData
		if corp != null and (not corp.generated_from_profile or CampaignRules.corporation_available(p, RunManager.lookup(), corp)):
			per_corp.append("%s %s" % [TextDb.t(corp, "display_name"), HudStats.ice_value(p.best_ice_for(corp.id))])
	note.append(tr("Best ICE by corporation: %s.") % ", ".join(per_corp))
	note.heading(tr("Achievements"))
	for d in Achievements.DEFS:
		var have := p.achievements.has(d["id"])
		note.append("[color=#%s]%s[/color] [b]%s[/b]  %s" % [(Palette.CELL_ACID if have else Palette.TEXT_LO).to_html(false), "[x]" if have else "[ ]", d["title"], d["text"]])
	box.add_child(note)
	var history := CrtText.new(tr("RUN HISTORY"), Vector2(PAGE_W, HISTORY_H)).make_reference()
	history.name = "History"
	if p.run_history.is_empty():
		history.append(tr("no runs yet"))
	for r in p.run_history:
		var corp := RunManager.lookup().get_content(StringName(String(r.get("corporation", "")))) as CorporationData
		history.append("%s T%d %s: %s, %d Cycles, %d banked" % [TextDb.t(corp, "display_name") if corp != null else r.get("corporation", "?"), int(r.get("tier", 1)), r.get("site", "?"), r.get("outcome", "?"), int(r.get("cycles", 0)), int(r.get("banked", 0))])
	box.add_child(history)
	_item(box, tr("Back"), show_main, StatIcon.BACK, tr("Back to the main menu."))
	_set_panel(_page("STATS", box, "StatsPage"), "stats")


func show_options() -> void:
	var box := VBoxContainer.new()
	var panel := SettingsPanel.new()
	panel.context = tr("TITLE")
	# The page's room (under the subtitles' band, over the ticker): past it the section scrolls.
	panel.max_height = get_viewport_rect().size.y - SubtitleStrip.top_below(PAGE_MARGIN.y) - PAGE_MARGIN.z - ticker.get_combined_minimum_size().y
	panel.closed.connect(show_main)
	box.add_child(panel)
	_set_panel(box, "options")


# --- Actions ---------------------------------------------------------------------------------

func new_in_slot(slot: String) -> void:
	if PageTransition.modal_open(self):
		PageTransition.after_modals(self, new_in_slot.bind(slot))
		return
	RunManager.save_slot = slot
	RunManager.reset()
	RunManager.change_scene(RunManager.HQ_SCENE)


## OVERTHROW: a new campaign in the first empty slot (the slots page when all three hold one).
func new_campaign() -> void:
	for slot in SLOTS:
		if RunManager.slot_summary(slot).is_empty():
			new_in_slot(slot)
			return
	show_slots()


func load_slot(slot: String) -> void:
	if PageTransition.modal_open(self):
		PageTransition.after_modals(self, load_slot.bind(slot))
		return
	RunManager.save_slot = slot
	RunManager.reset()
	if RunManager.resume():
		if RunManager.has_active_run():
			RunManager.go_to_netrun()
		else:
			RunManager.change_scene(RunManager.HQ_SCENE)
	else:
		show_slots()


func confirm_delete(slot: String) -> void:
	_ask(tr("Delete the campaign in slot %s?") % slot, func() -> void:
		RunManager.delete_slot(slot)
		show_slots(), "DELETE", tr("Everything in slot %s is gone for good: its Cell, its city, its Heat.") % slot, "DELETE SLOT", true) # TR


func confirm_quit() -> void:
	_ask(tr("Quit REBEL_CELL?"), RunManager.quit_game, "QUIT", tr("Your campaign is autosaved."), "QUIT") # TR


func start_tutorial() -> void:
	if PageTransition.modal_open(self):
		PageTransition.after_modals(self, start_tutorial)
		return
	RunManager.pending_tutorial = true
	RunManager.change_scene(RunManager.COMBAT_SCENE)


## Opens the confirm: `verb` and `what` are keys (the dialog translates them), `question` and
## `detail` come translated.
func _ask(question: String, on_yes: Callable, verb: String = "Yes", detail: String = "", what: String = "", destructive: bool = false) -> void:
	if _confirm != null and is_instance_valid(_confirm):
		_confirm.queue_free()
	# 2D's ConfirmDialog (the round 33 abandon dialog): `what` is its title, `detail` its body.
	_confirm = ConfirmDialog.new(question, verb, "CANCEL", what if what != "" else "ARE YOU SURE?", detail, destructive, "", "keep going [B]")
	_confirm.position = (size - _confirm.custom_minimum_size) * 0.5
	_confirm.confirmed.connect(on_yes)
	add_child(_confirm)


func confirm_visible() -> bool:
	return _confirm != null and is_instance_valid(_confirm) and _confirm.is_inside_tree()


## Keys and pad shortcuts on the main page (round 33 MORE hints: C slots, X codex, S stats,
## O options, Esc quit; pad Y codex); B / Esc on a sub-page goes back.
func _unhandled_input(event: InputEvent) -> void:
	if PageTransition.modal_open(self) or confirm_visible():
		return
	if panel_name in ["slots", "codex", "stats"] and event.is_action_pressed("ui_cancel"):
		show_main()
		get_viewport().set_input_as_handled()
		return
	if panel_name != "main":
		return
	if event is InputEventJoypadButton and event.pressed and (event as InputEventJoypadButton).button_index == JOY_BUTTON_Y:
		show_codex()
		get_viewport().set_input_as_handled()
		return
	if not (event is InputEventKey) or not event.pressed or (event as InputEventKey).echo:
		return
	match (event as InputEventKey).keycode:
		KEY_C:
			show_slots()
		KEY_X:
			show_codex()
		KEY_S:
			show_stats()
		KEY_O:
			show_options()
		KEY_ESCAPE:
			confirm_quit()
		_:
			return
	get_viewport().set_input_as_handled()


# --- Helpers ----------------------------------------------------------------------------------

func _describe(summary: Dictionary) -> String:
	if summary.is_empty():
		return tr("empty")
	return tr("%s, Heat %d, ICE %d, %d runs, %s%s") % [corporation_name(String(summary.get("corporation", ""))), int(summary.get("heat", 0)), int(summary.get("ice", 0)),
		int(summary.get("runs", 0)), tr(String(summary.get("state", "active"))), (tr(" (run in progress)") if summary.get("in_run", false) else "")]


## Campaign states as a slot summary words them (keys).
const STATE_WORDS := ["active", "won", "lost"] # TR


## The Continue chip's line (round 33: "slot 1 // Halcyon Civic // run 9 // Heat 58"): the
## slot, the corporation, the runs and the Heat, and "in a run" while a run is in progress.
func slot_text(slot: String, summary: Dictionary) -> String:
	var parts := PackedStringArray()
	if slot in SLOTS:
		parts.append(tr("slot %s") % slot)
	parts.append(corporation_name(String(summary.get("corporation", ""))))
	parts.append(tr("run %d") % (int(summary.get("runs", 0)) + 1))
	parts.append(tr("Heat %d") % int(summary.get("heat", 0)))
	if bool(summary.get("in_run", false)):
		parts.append(tr("in a run"))
	elif String(summary.get("state", "active")) != "active":
		parts.append(tr(String(summary.get("state", "active"))))
	return " // ".join(parts)


## The saved campaign in words (the Continue tooltip).
func slot_words(slot: String, summary: Dictionary) -> String:
	return tr("Slot %s: %s. Heat %d, ICE %d, %d runs completed. Campaign %s%s.") % [slot, corporation_name(String(summary.get("corporation", ""))),
		int(summary.get("heat", 0)), int(summary.get("ice", 0)), int(summary.get("runs", 0)), tr(String(summary.get("state", "active"))),
		tr(", a run in progress") if summary.get("in_run", false) else ""]


## A corporation's display name from its id (H21 #21: the Continue line showed "solace").
static func corporation_name(corporation_id: String) -> String:
	var corp := RunManager.lookup().get_content(StringName(corporation_id)) as CorporationData if corporation_id != "" else null
	return TextDb.t(corp, "display_name") if corp != null else (corporation_id if corporation_id != "" else "?")


## A terminal menu line (`> ITEM`, CAPS) with a tooltip and an optional key hint at its
## right, added to `box`. The v2 MORE list shows the words and the key hint only (round
## 33); the other pages' buttons keep their icon.
func _item(box: Control, text: String, on_pressed: Callable, kind: StringName, tip: String, hint: String = "") -> Button:
	var b := _button(text, on_pressed)
	b.tooltip_text = UiTip.fold(tip)
	box.add_child(b)
	if box.name == "MoreList":
		b.text = text.to_upper()
		b.theme_type_variation = &"MenuItem"
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_override(&"font", Chrome.caps_font(UiTheme.LABEL))
		b.add_theme_font_size_override(&"font_size", Chrome.px(UiTheme.LABEL))
		b.add_theme_color_override(&"font_color", Palette.TEXT_HI)
		b.add_theme_color_override(&"font_hover_color", Palette.TEXT_HI)
		b.add_theme_color_override(&"font_focus_color", Palette.TEXT_HI)
		b.add_theme_icon_override(&"icon", ImageTexture.new())
		b.set_meta(UiFocus.META_NO_SCALE, true)
		if hint != "":
			var h := Chrome.caps_label("[%s]" % hint, UiTheme.CAPTION, Palette.TEXT_LO)
			h.name = "KeyHint"
			h.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
			h.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT, Control.PRESET_MODE_MINSIZE)
			h.grow_horizontal = Control.GROW_DIRECTION_BEGIN
			h.offset_right = -8
			h.mouse_filter = Control.MOUSE_FILTER_IGNORE
			b.add_child(h)
			b.custom_minimum_size.x = maxf(b.custom_minimum_size.x, 0.0)
	else:
		IconMark.attach(b, kind)
		b.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN  # a terminal chip, not a full-width bar
	return b


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(240, 0)
	b.pressed.connect(on_pressed)
	return b
