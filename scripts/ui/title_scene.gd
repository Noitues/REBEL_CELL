extends Control
## Title / main menu (gap analysis 2.5; ART_BIBLE §11 Title, Campaign slots, Codex, Options,
## Stats and achievements; art pass W8a): Continue, Campaigns (three case-file slots, new /
## load / delete with confirmation), Tutorial, Codex, Stats & achievements, Options, Quit.
## Focal order: the baked logo, then Continue (the one primary), then the city. The menu is
## GLASS over a SCRIM with one PAPER note and one scrawl taped to it; a prompt bar with a
## pad. Every action goes through RunManager; the scene only displays state.

const SLOTS: Array[String] = ["1", "2", "3"]
## Subtitle lines the header band holds.
const HEADER_LINES := 2
## The plan note on the main menu at text scale 1.0 (it grows with the text, H21 #15).
const PLAN_NOTE := Vector2(150, 96)
## The plan note's text box: its side and top margins (ZineNote) and the lines it holds.
const PLAN_PAD := Vector2(20, 16)
const PLAN_LINES := 3
const PLAN_TILT := -4.0
## Screen margins (§5.1: the 24 px safe margin; the top a half step under it).
const MARGIN_X := UiTheme.SAFE_MARGIN
const MARGIN_TOP := UiTheme.SP_M
const MARGIN_BOTTOM := UiTheme.SAFE_MARGIN
## The main menu's least width at text scale 1.0 (px), grown with the text up to this scale.
const MENU_W := 380.0
const MENU_W_SCALE_MAX := 1.3
## How far the plan note is taped over the menu's right edge (px): its frame only, never the
## Continue line's glyphs under it.
const NOTE_OVERLAP := UiTheme.SP_S
## Stats grid columns (§11: 3), and the rows of section tabs the codex allows for.
const STAT_COLUMNS := 3
## A stats cell's width at text scale 1.0 (px): its longest word fits whole.
const STAT_CELL_W := 150.0
## Seconds before a --demo-page-after page opens (review captures only).
const DEMO_PAGE_DELAY := 1.0
## Frames a new page checks that it fits under the logo (see _trim_page).
const TRIM_PASSES := 3
## The uplink panel's field columns.
const UPLINK_COLUMNS := 2
const CODEX_TAB_ROWS := 2

var background: CyberdeckBackground
## The subtitles' band in the header (H21 #11).
var subtitle_strip: SubtitleStrip
var margin: MarginContainer
var _panel_host: VBoxContainer
var _panel: Control = null
var panel_name: String = ""
var _confirm: ConfirmDialog = null
## The slot the Continue line offers ("" = the newest numbered slot, RunManager.latest_slot).
## H24 S13: the storyboard shows its own private slot, so its title matches its HQ.
var continue_slot: String = ""
## The baked logo (W8a) and the pad's prompt bar (§5.2).
var logo: LogoArt
var prompts: PadPrompts


func _ready() -> void:
	UiTheme.apply(self)
	# Capture variants (ANIM-6): --demo-set / --demo-speed tune a copy of the motion table.
	MotionDemo.apply_args()
	# Subtitles still on screen from a campaign sit in the top band over the header, clear
	# of every menu (H20).
	Dialogue.dock_default()
	background = CyberdeckBackground.new()
	add_child(background)
	margin = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["margin_left", "margin_right"]:
		margin.add_theme_constant_override(side, MARGIN_X)
	margin.add_theme_constant_override("margin_top", MARGIN_TOP)
	margin.add_theme_constant_override("margin_bottom", MARGIN_BOTTOM)
	add_child(margin)
	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", UiTheme.SP_S)
	margin.add_child(root)
	var header := HBoxContainer.new()
	header.name = "Header"
	header.add_theme_constant_override("separation", UiTheme.SP_L)
	# W8a (ART_BIBLE §11 Title, §4.3 rule 5): the logo is baked art, first in the focal order.
	logo = LogoArt.new()
	logo.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	header.add_child(logo)
	# The subtitles' band beside the logo (H21 #11): no menu, no tag under it.
	subtitle_strip = SubtitleStrip.new(HEADER_LINES)
	header.add_child(subtitle_strip)
	root.add_child(header)
	_panel_host = VBoxContainer.new()
	_panel_host.name = "PanelHost"
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(_panel_host)
	# §5.2: the prompt bar at the foot of every page while a pad is in use.
	prompts = PadPrompts.new()
	root.add_child(prompts)
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
			margin.visible = false
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
			margin.visible = false
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
	# Review captures (W8a): --demo-page-after=slots opens that page DEMO_PAGE_DELAY s after
	# the main menu, so a Movie Maker run records the page transition.
	for a in args:
		if a.begins_with("--demo-page-after="):
			var page := "show_" + a.trim_prefix("--demo-page-after=")
			if has_method(page):
				get_tree().create_timer(DEMO_PAGE_DELAY).timeout.connect(Callable(self, page))


## Esc / B on a title page goes back to the main menu (Options and the confirm answer it
## themselves first).
func _unhandled_input(event: InputEvent) -> void:
	if panel_name in ["slots", "codex", "stats"] and event.is_action_pressed("ui_cancel") and not PageTransition.modal_open(self):
		get_viewport().set_input_as_handled()
		show_main()


# --- Panels -----------------------------------------------------------------------------------

func _set_panel(p: Control, name: String) -> void:
	# ART_BIBLE §10 rule 6: an open modal (a confirm) closes before the page changes.
	if PageTransition.modal_open(self):
		PageTransition.after_modals(self, _set_panel.bind(p, name))
		return
	if _panel != null:
		# Out of the host at once: the new page is laid out alone, where it rests, and never
		# reflows under the old one mid-slide (critique gifs/21).
		if _panel.get_parent() != null:
			_panel.get_parent().remove_child(_panel)
		_panel.queue_free()
	_panel = p
	panel_name = name
	# H24 S4: the page shows its words as given (translated once where built).
	TextDb.shown_as_given(p)
	_panel_host.add_child(p)
	Dialogue.enter_screen("title")
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	prompts.set_prompts([["ui_accept", "Select"]] if name == "main" else [["ui_accept", "Select"], ["ui_cancel", "Back"]])
	# §10: glass slides in from the right, paper drops; focus lands when it ends.
	PageTransition.enter(p, PageTransition.look_of(p), UiFocus.focus_first.bind(p))
	# W7: the city calms behind the page (the main menu names its two panels instead).
	var calm: Array[Control] = [p]
	background.set_calm_controls(calm)
	_trim_left = TRIM_PASSES
	# From the next frame: the page's views fit themselves as it is laid out first.
	if is_inside_tree() and not get_tree().process_frame.is_connected(_trim_page):
		get_tree().process_frame.connect(_trim_page, CONNECT_ONE_SHOT)


## §5.3: a page whose rows outside its scrolling view took more room than reserved (the
## tabs wrapping to a third row at big text) gives the excess back from its scrolling view,
## over its first frames (before its entrance moves it; the view only ever shrinks).
func _trim_page() -> void:
	var p := _panel
	if p == null or not is_instance_valid(p) or not is_inside_tree():
		return
	var foot := get_viewport_rect().size.y - MARGIN_BOTTOM
	if prompts.visible:
		foot -= prompts.get_combined_minimum_size().y + UiTheme.SP_S
	var over := _panel_host.global_position.y + p.get_combined_minimum_size().y - foot
	if over > 0.5:
		var best: FitScroll = null
		for n in p.find_children("*", "FitScroll", true, false):
			var f := n as FitScroll
			if f.max_height > 0.0 and (best == null or f.max_height > best.max_height):
				best = f
		if best != null:
			best.max_height = maxf(FitScroll.MIN_VIEW * Settings.text_scale, best.max_height - ceilf(over))
	_trim_left -= 1
	if _trim_left > 0 and not get_tree().process_frame.is_connected(_trim_page):
		get_tree().process_frame.connect(_trim_page, CONNECT_ONE_SHOT)


## Frames the current page still checks its fit (see _trim_page).
var _trim_left: int = 0


## The height a page may take under the logo (px): the screen less its margins, the header
## and the prompt bar, and `reserve` for the page's own rows outside its scrolling view.
func page_room(reserve: float = 0.0) -> float:
	var h := get_viewport_rect().size.y - MARGIN_TOP - MARGIN_BOTTOM - logo.get_combined_minimum_size().y - UiTheme.SP_S * 2
	if prompts.visible:
		h -= prompts.get_combined_minimum_size().y + UiTheme.SP_S
	return maxf(FitScroll.MIN_VIEW * Settings.text_scale, h - reserve)


## The Back line at the foot of a page (a menu line with its icon).
func _back_row(box: Control) -> Button:
	var b := _item(box, tr("Back"), show_main, StatIcon.BACK, tr("Back to the main menu."))
	b.name = "Back"
	b.theme_type_variation = UiTheme.SECONDARY
	b.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	b.custom_minimum_size.x = 0
	return b


func show_main() -> void:
	var page := HBoxContainer.new()
	page.name = "MainPage"
	page.add_theme_constant_override("separation", UiTheme.GUTTER)
	page.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var row := HBoxContainer.new()
	row.name = "Main"
	# The note is taped over the menu's right edge (critique 01: anchored, not floating).
	row.add_theme_constant_override("separation", -NOTE_OVERLAP)
	row.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	page.add_child(row)
	# The REBEL_CELL name stays as the brand mark (H24 S3).
	var menu := TerminalWindow.new(tr("REBEL_CELL // MAIN MENU"))
	menu.name = "Menu"
	menu.custom_minimum_size = Vector2(MENU_W * minf(Settings.text_scale, MENU_W_SCALE_MAX), 0)
	menu.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var box := menu.body
	var latest := continue_slot if continue_slot != "" else RunManager.latest_slot()
	var cont: Button = null
	# Each item carries an icon (H21 #13) and says what it does on hover.
	if latest != "":
		var summary := RunManager.slot_summary(latest)
		if not summary.is_empty():
			# H24 S13: "Continue" on its own line and the saved campaign under it as a line of
			# stat icons (it read like debug output); the tooltip says it in words.
			cont = _item(box, tr("Continue"), func() -> void: load_slot(latest), StatIcon.CONTINUE,
				"%s\n%s" % [tr("Pick up the campaign saved most recently."), slot_words(latest, summary)])
			cont.name = "Continue"
			var line := slot_line(latest, summary)
			# On the pink primary the line is ink (§3.7: 4.5:1 and more).
			line.color = Palette.INK
			line.icon_color = Palette.INK
			IconLine.attach(cont, line)
	_item(box, tr("Campaigns"), show_slots, StatIcon.SLOTS, tr("The three campaign slots: start, load or delete."))
	_item(box, tr("Tutorial"), start_tutorial, StatIcon.TUTORIAL, tr("A guided first fight."))
	_item(box, tr("Codex"), show_codex, StatIcon.CODEX, tr("Everything the Cell knows: slices, cards, Firmware, Daemons, rules."))
	_item(box, tr("Stats & achievements"), show_stats, StatIcon.STATS, tr("Your records, achievements and run history."))
	_item(box, tr("Options"), show_options, StatIcon.SETTINGS, tr("Text size, sound, controls, subtitles."))
	_item(box, tr("Quit"), confirm_quit, StatIcon.QUIT, tr("Leave REBEL_CELL (asks first)."))
	for b in box.get_children():
		b.theme_type_variation = &"MenuItem"
		(b as Button).alignment = HORIZONTAL_ALIGNMENT_LEFT
	# §11 Title focal order: logo, then Continue, the one primary (filled CELL_PINK).
	if cont != null:
		cont.theme_type_variation = UiTheme.PRIMARY
	# ANIM-6: the highlight slides, the line types in, the caret blinks.
	MenuMotion.attach(box)
	# The build's version, readable (critique 01: caption size, 4.5:1 on the glass).
	var v := Label.new()
	v.name = "Version"
	v.auto_translate_mode = Node.AUTO_TRANSLATE_MODE_DISABLED
	v.text = tr("v%s // cell uplink") % ProjectSettings.get_setting("application/config/version", "dev")
	v.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	v.add_theme_color_override("font_color", Palette.TEXT_MID)
	v.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	menu.body.add_child(v)
	row.add_child(menu)
	# The Cell's voice, taped to the menu: one PAPER note (the plan) and one scrawl.
	var deco := VBoxContainer.new()
	deco.name = "Deco"
	deco.add_theme_constant_override("separation", UiTheme.SP_S)
	deco.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	deco.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var drop := Control.new()
	drop.custom_minimum_size.y = UiTheme.SP_XL
	drop.mouse_filter = Control.MOUSE_FILTER_IGNORE
	deco.add_child(drop)
	# The plan note holds its three lines at any text size (H21 #15: at 1.6 it showed only
	# the last two and scrolled "1. BREACH" away).
	var ts := Settings.text_scale
	var plan_h := PLAN_PAD.y + Palette.marker().get_height(UiTheme.font_px(UiTheme.BODY)) * PLAN_LINES
	var plan := ZineNote.new("", Vector2(PLAN_NOTE.x * maxf(1.0, ts), maxf(PLAN_NOTE.y, plan_h)))
	plan.name = "PlanNote"
	plan.paper_color = Palette.NOTE_YELLOW
	plan.label.add_theme_font_override("normal_font", Palette.marker())
	plan.label.add_theme_font_size_override("normal_font_size", UiTheme.font_px(UiTheme.BODY))
	plan.label.scroll_following = false
	# Three lines and no trailing break (append adds one: a fourth, empty line was cut, W10 lint).
	plan.label.append_text(tr("1. BREACH\n2. DISABLE\n3. EXFIL"))
	plan.rotation_degrees = PLAN_TILT
	plan.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plan.label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plan.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	deco.add_child(plan)
	var scrawl := ScrawlArt.new(SvgArt.SCRAWL_NEVER_SLEEP, "Never sleep")
	scrawl.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	deco.add_child(scrawl)
	row.add_child(deco)
	# The profile at a glance on its own glass, right-aligned and quiet (after Continue and
	# the city in the focal order): icon + number fields, never paper tags (one PAPER note).
	var gap := Control.new()
	gap.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	gap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	page.add_child(gap)
	var up := uplink(RunManager.profile)
	page.add_child(up)
	_set_panel(page, "main")
	# W7 (ART_BIBLE 2 CITY: calm behind text): the city dims and settles behind both panels.
	var calm: Array[Control] = [menu, up]
	background.set_calm_controls(calm)


## The profile's uplink panel: a GLASS window of icon + number fields (campaigns, won, best
## ICE, runs, raids, badges), each named in its tooltip; a number or a dash, never "none".
func uplink(p: ProfileState) -> TerminalWindow:
	var up := TerminalWindow.new(tr("UPLINK"), Palette.NET_CYAN)
	up.name = "Uplink"
	up.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var grid := GridContainer.new()
	grid.name = "ProfileFields"
	grid.columns = UPLINK_COLUMNS
	grid.add_theme_constant_override("h_separation", UiTheme.SP_M)
	grid.add_theme_constant_override("v_separation", UiTheme.SP_XS)
	for f in uplink_fields(p):
		var sf := StatField.new(f[0], String(f[1]), UiTheme.font_px(UiTheme.LABEL), Palette.TEXT_HI)
		sf.tooltip_text = UiTip.fold(tr(String(f[2])))
		sf.mouse_filter = Control.MOUSE_FILTER_PASS
		grid.add_child(sf)
	up.body.add_child(grid)
	return up


## The uplink's fields as [kind, value, words].
static func uplink_fields(p: ProfileState) -> Array:
	return [[StatIcon.CAMPAIGNS, str(p.campaigns_started), "Campaigns started on this profile."], # TR
		[StatIcon.WON, str(p.campaigns_won), "Campaigns won."], # TR
		[StatIcon.ICE, HudStats.ice_value(p.best_ice), "The highest ICE level cleared (— until you clear one). Each corporation keeps its own ladder."], # TR
		[StatIcon.RUNS, str(p.runs_completed), "Netruns completed."], # TR
		[StatIcon.RAIDS, raid_value(p), "Raids repelled / lost."], # TR
		[StatIcon.BADGES, str(p.achievements.size()), "Achievements earned (Stats & achievements lists them)."]] # TR


## The crew of the campaign in `slot` ([{id, name, class_id, alive}]; [] when unreadable).
## Read-only: the save file is read, never written.
static func slot_crew(slot: String) -> Array:
	var data := SaveService.load_dict(SaveService.campaign_path(slot))
	var out := []
	for od in (data.get("campaign", {}) as Dictionary).get("roster", []):
		if od is Dictionary:
			out.append({"id": String(od.get("id", "")), "name": String(od.get("name", "")), "class_id": String(od.get("class_id", "")),
				"alive": bool(od.get("alive", true))})
	return out


func show_slots() -> void:
	var win := TerminalWindow.new(tr("Campaign slots"))
	win.name = "Slots"
	# A compact window, not the full width.
	win.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	win.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var latest := RunManager.latest_slot()
	var any := false
	for slot in SLOTS:
		any = any or not RunManager.slot_summary(slot).is_empty()
	# §5.3: the case files fill their columns, 3 at 1.0, fewer as the text grows.
	var grid := GridContainer.new()
	grid.name = "Cards"
	grid.columns = slot_columns()
	grid.add_theme_constant_override("h_separation", UiTheme.GUTTER)
	grid.add_theme_constant_override("v_separation", UiTheme.GUTTER)
	for slot in SLOTS:
		var summary := RunManager.slot_summary(slot)
		# §5.3 one primary: Load on the newest campaign, or New in the first slot when none.
		var primary := (slot == latest) if any else (slot == SLOTS[0])
		var card := CaseFileCard.new(slot, summary, slot_crew(slot) if not summary.is_empty() else [], primary)
		card.load_pressed.connect(load_slot)
		card.delete_pressed.connect(confirm_delete)
		card.new_pressed.connect(new_in_slot)
		grid.add_child(card)
	win.body.add_child(grid)
	var back_room := UiTheme.font_px(UiTheme.BODY) * 3.0
	win.scroll_body(page_room(back_room + UiTheme.font_px(UiTheme.BODY) * 3.0))
	var page := VBoxContainer.new()
	page.name = "SlotsPage"
	page.add_theme_constant_override("separation", UiTheme.SP_S)
	page.add_child(win)
	_back_row(page)
	_set_panel(page, "slots")


## Case files per row: 3 while three fit the screen, then 2, then 1 (§5.3).
func slot_columns() -> int:
	var room := get_viewport_rect().size.x - MARGIN_X * 2 - UiTheme.PANEL_PAD_H * 4
	var w := CaseFileCard.FOLDER.x * Settings.text_scale + UiTheme.GUTTER
	return clampi(int(room / w), 1, SLOTS.size())


func show_codex() -> void:
	var page := VBoxContainer.new()
	page.name = "CodexPage"
	page.add_theme_constant_override("separation", UiTheme.SP_S)
	var width := get_viewport_rect().size.x - MARGIN_X * 2
	# The tabs take one or more rows above the spread; the Back line sits under it.
	var tabs_room := UiTheme.font_px(UiTheme.BODY) * CODEX_TAB_ROWS * 2.2
	var spread := CodexSpread.new(Codex.entries(RunManager.lookup(), RunManager.profile), page_room(tabs_room + UiTheme.font_px(UiTheme.BODY) * 5.0), width)
	page.add_child(spread)
	_back_row(page)
	_set_panel(page, "codex")


func show_stats() -> void:
	var p := RunManager.profile
	var page := VBoxContainer.new()
	page.name = "StatsPage"
	page.add_theme_constant_override("separation", UiTheme.SP_S)
	var sheet := VBoxContainer.new()
	sheet.name = "Sheet"
	sheet.add_theme_constant_override("separation", UiTheme.GUTTER)
	# Stats: a 3-column grid of icon + number fields, each named under it (GLASS data).
	var stats := TerminalWindow.new(tr("STATS"), Palette.NET_CYAN)
	stats.name = "Stats"
	# As wide as its grid (§5.3: no empty glass).
	stats.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	var grid := GridContainer.new()
	grid.name = "StatGrid"
	grid.columns = STAT_COLUMNS
	grid.add_theme_constant_override("h_separation", UiTheme.SP_XL)
	grid.add_theme_constant_override("v_separation", UiTheme.SP_S)
	for cell in stat_cells(p):
		grid.add_child(_stat_cell(cell))
	stats.body.add_child(grid)
	sheet.add_child(stats)
	# Achievements: sticker badges, earned in full colour, the rest outlined with a lock.
	var ach := TerminalWindow.new(tr("Achievements"), Palette.CELL_PINK)
	ach.name = "Achievements"
	var got := 0
	for d in Achievements.DEFS:
		got += 1 if p.achievements.has(d["id"]) else 0
	ach.tag_label.text = "%d/%d" % [got, Achievements.DEFS.size()]
	var badges := HFlowContainer.new()
	badges.name = "Badges"
	badges.add_theme_constant_override("h_separation", UiTheme.SP_S)
	badges.add_theme_constant_override("v_separation", UiTheme.SP_S)
	for d in Achievements.DEFS:
		badges.add_child(AchievementBadge.new(d["id"], tr(String(d["title"])), tr(String(d["text"])), p.achievements.has(d["id"])))
	ach.body.add_child(badges)
	sheet.add_child(ach)
	# Run history: taped receipts, or the designed empty slip.
	var hist := TerminalWindow.new(tr("RUN HISTORY"), Palette.CELL_ACID)
	hist.name = "History"
	var receipts := HFlowContainer.new()
	receipts.name = "Receipts"
	receipts.add_theme_constant_override("h_separation", UiTheme.SP_M)
	receipts.add_theme_constant_override("v_separation", UiTheme.SP_M)
	if p.run_history.is_empty():
		receipts.add_child(RunReceipt.empty())
	var i := 0
	for r in p.run_history:
		var corp := RunManager.lookup().get_content(StringName(String(r.get("corporation", "")))) as CorporationData
		receipts.add_child(RunReceipt.of_run(r, TextDb.t(corp, "display_name") if corp != null else String(r.get("corporation", "?")), i))
		i += 1
	hist.body.add_child(receipts)
	sheet.add_child(hist)
	var fit := FitScroll.new(sheet, page_room(UiTheme.font_px(UiTheme.BODY) * 3.0))
	fit.name = "StatsScroll"
	page.add_child(fit)
	_back_row(page)
	_set_panel(page, "stats")


## The profile's numbers as [kind, value, words] for the stats grid (a number or "—", never
## "none").
static func stat_cells(p: ProfileState) -> Array:
	var per_corp := PackedStringArray()
	for cid in RunManager.lookup().ids_of_class(&"CorporationData"):
		var corp := RunManager.lookup().get_content(cid) as CorporationData
		if corp != null and (not corp.generated_from_profile or CampaignRules.corporation_available(p, RunManager.lookup(), corp)):
			per_corp.append("%s %s" % [TextDb.t(corp, "display_name"), HudStats.ice_value(p.best_ice_for(corp.id))])
	var raids := raid_value(p)
	var perfects := str(int(p.stats.get(STAT_PERFECTS, 0)))
	var racks := str(int(p.stats.get(STAT_RACKS, 0)))
	var cycles := str(int(p.stats.get(STAT_CYCLES, 0)))
	var assisted := str(int(p.stats.get(STAT_ASSISTED, 0)))
	var badges := str(p.achievements.size())
	return [[StatIcon.CAMPAIGNS, str(p.campaigns_started), "Campaigns started"], [StatIcon.WON, str(p.campaigns_won), "Campaigns won"], # TR
		[StatIcon.CLOSE, str(p.campaigns_lost), "Campaigns lost"], [StatIcon.RUNS, str(p.runs_completed), "Runs completed"], # TR
		[StatIcon.CREW, str(p.operatives_lost), "Operatives lost"], [StatIcon.RAIDS, raids, "Raids won / lost"], # TR
		[StatIcon.ICE, HudStats.ice_value(p.best_ice), "Best ICE", ", ".join(per_corp)], [StatIcon.CHECK, perfects, "Perfects"], # TR
		[StatIcon.RACK, racks, "Racks captured"], [StatIcon.CYCLES, cycles, "Cycles earned"], # TR
		[StatIcon.PLUS, assisted, "Assisted wins"], [StatIcon.BADGES, badges, "Achievements"]] # TR


## Raids won / lost as "2/1".
static func raid_value(p: ProfileState) -> String:
	return "%d/%d" % [p.raids_won, p.raids_lost]


## The profile stats' keys the grid reads.
const STAT_PERFECTS := "perfects"
const STAT_RACKS := "racks"
const STAT_CYCLES := "cycles"
const STAT_ASSISTED := "assisted_wins"


func _stat_cell(cell: Array) -> Control:
	var v := VBoxContainer.new()
	v.name = "Stat_%s" % String(cell[0])
	v.add_theme_constant_override("separation", 0)
	v.tooltip_text = UiTip.fold(tr(String(cell[2])) + ("\n" + String(cell[3]) if cell.size() > 3 else ""))
	v.mouse_filter = Control.MOUSE_FILTER_PASS
	var f := StatField.new(cell[0], String(cell[1]), UiTheme.font_px(UiTheme.TITLE), Palette.TEXT_HI)
	f.mouse_filter = Control.MOUSE_FILTER_IGNORE
	v.add_child(f)
	var l := Label.new()
	l.text = tr(String(cell[2]))
	l.add_theme_font_size_override("font_size", UiTheme.font_px(UiTheme.CAPTION))
	l.add_theme_color_override("font_color", Palette.TEXT_MID)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	# Wraps at word boundaries at the cell's width, never inside a word (§4.3 rule 3).
	UiWrap.whole_words(l)  # art pass W9F §4.3.3: whole words, never mid-word
	l.custom_minimum_size.x = STAT_CELL_W * Settings.text_scale
	v.add_child(l)
	return v


func show_options() -> void:
	var box := VBoxContainer.new()
	box.name = "OptionsPage"
	var panel := SettingsPanel.new()
	# Its own width (PANEL_W at the text scale), not the page's: no empty glass (§5.3).
	panel.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	panel.fit_room(page_room())
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
	_ask(tr("Delete the campaign in slot %s? This cannot be undone.") % slot, func() -> void:
		RunManager.delete_slot(slot)
		show_slots())


func confirm_quit() -> void:
	_ask(tr("Quit REBEL_CELL?"), RunManager.quit_game)


func start_tutorial() -> void:
	if PageTransition.modal_open(self):
		PageTransition.after_modals(self, start_tutorial)
		return
	RunManager.pending_tutorial = true
	RunManager.change_scene(RunManager.COMBAT_SCENE)


func _ask(question: String, on_yes: Callable) -> void:
	if _confirm != null and is_instance_valid(_confirm):
		_confirm.queue_free()
	_confirm = ConfirmDialog.new(question)
	_confirm.position = Vector2(size.x / 2.0 - 210, 200)
	_confirm.confirmed.connect(on_yes)
	# §3.3 / §5.3: a modal sits over a SCRIM (the page behind blurred and dimmed; it takes
	# the clicks meant for the page), and opens as a modal (§10: <= 0.22 s, never a cut).
	var scrim := GlassScrim.new()
	scrim.name = "ModalScrim"
	scrim.top_level = true
	scrim.show_behind_parent = true
	scrim.mouse_filter = Control.MOUSE_FILTER_STOP
	scrim.size = get_viewport_rect().size
	_confirm.add_child(scrim)
	add_child(_confirm)
	PageTransition.open_modal(_confirm)


func confirm_visible() -> bool:
	return _confirm != null and is_instance_valid(_confirm) and _confirm.is_inside_tree()


# --- Helpers ----------------------------------------------------------------------------------

func _describe(summary: Dictionary) -> String:
	if summary.is_empty():
		return tr("empty")
	return tr("%s, Heat %d, ICE %d, %d runs, %s%s") % [corporation_name(String(summary.get("corporation", ""))), int(summary.get("heat", 0)), int(summary.get("ice", 0)),
		int(summary.get("runs", 0)), tr(String(summary.get("state", "active"))), (tr(" (run in progress)") if summary.get("in_run", false) else "")]


## Campaign states as a slot summary words them (keys).
const STATE_WORDS := ["active", "won", "lost"] # TR


## The Continue line's second line (H24 S13): the corporation, then Heat, ICE and runs each
## after its icon, and the state ("in a run" when a run is in progress).
func slot_line(slot: String, summary: Dictionary) -> IconLine:
	var lead := corporation_name(String(summary.get("corporation", "")))
	if slot in SLOTS:
		lead = tr("SLOT %s · %s") % [slot, lead]
	var items: Array[Dictionary] = [{"kind": StatIcon.HEAT, "text": str(int(summary.get("heat", 0)))},
		{"kind": StatIcon.ICE, "text": str(int(summary.get("ice", 0)))},
		{"kind": StatIcon.RUNS, "text": str(int(summary.get("runs", 0)))}]
	var state := String(summary.get("state", "active"))
	if bool(summary.get("in_run", false)):
		items.append({"kind": StatIcon.JACK_IN, "text": tr("in a run")})
	elif state != "active":
		items.append({"kind": StatIcon.WON if state == "won" else StatIcon.QUIT, "text": tr(state)})
	var line := IconLine.new(lead, items)
	line.name = "SlotLine"
	return line


## The saved campaign in words (the Continue item's tooltip).
func slot_words(slot: String, summary: Dictionary) -> String:
	return tr("Slot %s: %s. Heat %d, ICE %d, %d runs completed. Campaign %s%s.") % [slot, corporation_name(String(summary.get("corporation", ""))),
		int(summary.get("heat", 0)), int(summary.get("ice", 0)), int(summary.get("runs", 0)), tr(String(summary.get("state", "active"))),
		tr(", a run in progress") if summary.get("in_run", false) else ""]


## A corporation's display name from its id (H21 #21: the Continue line showed "solace").
static func corporation_name(corporation_id: String) -> String:
	var corp := RunManager.lookup().get_content(StringName(corporation_id)) as CorporationData if corporation_id != "" else null
	return TextDb.t(corp, "display_name") if corp != null else (corporation_id if corporation_id != "" else "?")


## A terminal-menu item with an icon and a tooltip, added to `box`.
func _item(box: Control, text: String, on_pressed: Callable, kind: StringName, tip: String) -> Button:
	var b := _button(text, on_pressed)
	IconMark.attach(b, kind)
	b.tooltip_text = UiTip.fold(tip)
	box.add_child(b)
	return b


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(320, 0)
	b.pressed.connect(on_pressed)
	return b
