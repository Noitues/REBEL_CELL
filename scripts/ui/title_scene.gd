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
const PAGE_MARGIN := Vector3(40, 22, 0)
## Gaps (px): sign to the verbs, between verb rows, a sticker to its chip.
const GAP_SIGN := 4
const GAP_ROWS := 4
const GAP_CHIP := 22
## The verbs' chips' least width (px at text scale 1.0).
const CHIP_MIN_W := 300.0
## The MORE panel's and the profile panel's least widths (px at text scale 1.0).
const MORE_W := 300.0
const PROFILE_W := 290.0
## From this text scale the MORE panel moves to the right column (the left one is full).
const MORE_RIGHT_FROM := 1.6
## The MORE lines' type step (round 33: five lines in 156 px of the board).
const MORE_STEP := UiTheme.BODY
## The least gap between a MORE line's words and its key hint (px).
const HINT_GAP := 12.0
## The gap between the bottom panels (MORE, PROFILE) and the foot row (px).
const FOOT_GAP := 6.0
## Parity TITLE-02 (concept 33 `title_screen.png`): the least gap from OVERTHROW's focus halo
## down to the MORE panel (px at 1280x720; at rest the sticker's die-cut sits ~10 px further
## up, the concept's ~25 px). MORE's lines keep the concept's pitch (five lines in ~125 px):
## each line's empty top and bottom padding overlaps its neighbour's by MORE_ROW_SEP (the
## words, the hover wash's lit rule and the focus brackets keep their size), so MORE sits
## lower and clear of the verbs.
const MORE_GAP := 20.0
const MORE_ROW_SEP := -4
## The city's dim behind the title (it reads as the backdrop, round 33's blurred city).
const CITY_DIM := 0.58
## The page widths for the codex / stats / slots terminals (px at 1.0) and the codex text's
## least height.
const PAGE_W := 900.0
## Frames the slots page checks its panel's fit after it is laid out (SLOTS-04).
const SLOTS_TRIM_PASSES := 3
const CODEX_H := 420.0
const STATS_H := 200.0
const HISTORY_H := 150.0
## The least height of a page's reference text (px): it scrolls inside the room it gets.
const TEXT_FLOOR_H := 72.0
## The gap between a slot's lines and its buttons (px): the focus brackets reach above a button.
const SLOT_ROW_GAP := 8
## The ON AIR ticker's words (keys; round 33's ticker).
const TICKER_WORDS := ["PIRATE RADIO 88.1", "HALCYON RAISES FARES AGAIN"] # TR
## The confirm's caption under CANCEL (a key).
const CONFIRM_WORDS := ["keep going [B]"] # TR
## The verbs, their chips' labels and the page titles (keys, translated where they are shown).
const PAGE_WORDS := ["BREACH", "SIMULATE", "OVERTHROW", "Continue", "Tutorial", "New campaign", "CAMPAIGN SLOTS", "CODEX", "STATS"] # TR

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
	# left for the sign, which hangs from the top edge on its cables (the band sits top right).
	margin.add_theme_constant_override("margin_top", int(0.0 if name == "main" else SubtitleStrip.top_below(PAGE_MARGIN.y)))
	# H24 S4: the page shows its words as given (translated once where built).
	TextDb.shown_as_given(p)
	_panel_host.add_child(p)
	Dialogue.enter_screen("title")
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	if name == "slots":
		_link_slots(p)  # the case files' grid (SLOTS-01)
	var first := _default_focus(p)
	PageTransition.enter(p, PageTransition.look_of(p), _page_focus.bind(p, first), -1 if back else 1)


## The page's first focus once it has entered, unless a confirm opened meanwhile (it holds
## the focus: the page behind never takes it).
func _page_focus(p: Control, first: Control) -> void:
	if confirm_visible() or PageTransition.modal_open(self) or not is_instance_valid(p):
		return
	if first != null and is_instance_valid(first):
		first.grab_focus()
	else:
		UiFocus.focus_first(p)


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
	var motto := PencilWords.new(tr("NEVER SLEEP"), MOTTO_TILT, true, PencilWords.MOTTO_ART)
	motto.name = "Motto"
	motto.position = PencilWords.motto_at()
	motto.size = motto.get_combined_minimum_size()
	page.add_child(motto)
	motto.visible = not big_text()  # big text: the chips take its room
	# The plan: three numbered verbs, each on its terminal chip.
	var plan := HBoxContainer.new()
	plan.name = "Plan"
	plan.add_theme_constant_override("separation", 8)
	plan.custom_minimum_size.y = 0
	var rows := VBoxContainer.new()
	rows.name = "Verbs"
	rows.add_theme_constant_override("separation", 0)  # the concept's row pitch (PencilPlan.row_pitch)
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
	more.custom_minimum_size.x = MORE_W * maxf(1.0, Settings.text_scale * 0.65)
	var box := more.body
	box.name = "MoreList"
	box.add_theme_constant_override("separation", MORE_ROW_SEP)  # TITLE-02: the concept's pitch
	_item(box, tr("Campaign slots"), show_slots, StatIcon.SLOTS, tr("The three campaign slots: start, load or delete."), "C")
	_item(box, tr("Codex"), show_codex, StatIcon.CODEX, tr("Everything the Cell knows: slices, cards, Firmware, Daemons, rules."), "X")
	# Big text: the line reads STATS (its page's title; the tooltip names the achievements) so
	# MORE fits beside the verbs at 2.0.
	_item(box, tr("Stats & achievements") if not big_text() else tr("STATS"), show_stats, StatIcon.STATS, tr("Your records, achievements and run history."), "S")
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
	profile.offset_bottom = -foot.get_combined_minimum_size().y - FOOT_GAP  # above the pad prompts (round 33)
	_place_bottom(foot, false, true)
	if big_text():
		# Big text: the left column is full; MORE heads the right column.
		more.anchor_left = 1.0
		more.anchor_right = 1.0
		more.grow_horizontal = Control.GROW_DIRECTION_BEGIN
		# Under the subtitles' band (H21 #11: no menu under it).
		more.offset_top = SubtitleStrip.top_below(PAGE_MARGIN.y)  # the main page starts at the top edge
	else:
		_place_bottom(more, false)
		more.offset_bottom = -foot.get_combined_minimum_size().y - FOOT_GAP
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
	# The concept's own sticker art (round 33 title.py / menu33.py, baked): BREACH, SIMULATE, OVERTHROW.
	var s := VerbSticker.new(tr(word), fill, VERB_PX, VERB_TILTS[verbs.size()], word.to_lower())
	s.pre_translated = true
	s.fist_at = fist
	s.tooltip_text = UiTip.fold(tip)
	# Big text (MORE_RIGHT_FROM): the chip keeps its label; its line moves into the tooltip.
	var chip := MenuChip.new(tr(label), line if not big_text() else "")
	chip.pre_translated = true
	chip.name = label.replace(" ", "")
	chip.focus_mode = Control.FOCUS_NONE
	chip.min_width = CHIP_MIN_W  # it grows with its label at big text
	if big_text():
		chip.label_step = UiTheme.BODY  # the right column is MORE: the chips stay narrower
		chip.min_width = 0.0  # as wide as its label: MORE needs the room
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
	# The rows keep the concept's pitch (title.py: 112 px on the 1920 board) so the pencil's
	# numbers sit on them; a sticker (its focus halo, its shadow) may reach past its row.
	var w := 0.0
	var h := PencilPlan.row_pitch()
	for v in verbs:
		w = maxf(w, v.get_combined_minimum_size().x)
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
	var sticker := VerbSticker.new(tr(title_word), VerbSticker.Fill.YELLOW, TITLE_STICKER_PX, TITLE_STICKER_TILT, VerbSticker.title_art(title_word))
	sticker.pre_translated = true
	sticker.name = "TitleSticker"
	sticker.focus_mode = Control.FOCUS_NONE
	sticker.mouse_filter = Control.MOUSE_FILTER_IGNORE
	head.add_child(sticker)
	box.add_child(head)
	box.add_child(content)
	# The page takes the room between the top and the ticker; its reference texts share it.
	box.size_flags_vertical = Control.SIZE_EXPAND_FILL
	content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	return box


## A reference text that shares the page's room (in proportion to `nominal`, its height at
## text scale 1.0) and scrolls past it, so the page fits from 1.0 to 2.0.
func _flex(t: CrtText, nominal: float) -> void:
	t.label.custom_minimum_size.y = minf(nominal, TEXT_FLOOR_H)
	t.size_flags_vertical = Control.SIZE_EXPAND_FILL
	t.size_flags_stretch_ratio = nominal
	t.body.size_flags_vertical = Control.SIZE_EXPAND_FILL


## Parity SLOTS-01..04 (designer 2026-10-05; ported from art-m13-final
## `scripts/ui/title_scene.gd` show_slots / slot_crew / slot_columns, reworked in v2): the
## CAMPAIGN SLOTS title sticker (SLOTS-03) over one terminal panel holding the three slots as
## case files in a row (CaseFileCard; fewer columns as the text grows), LOAD the page's one
## sticker verb on the newest campaign, DELETE a HARM terminal chip that asks first. The panel
## sizes to its cards up to the room above the Back line and the ticker, then scrolls inside
## (CrtWindow `max_body`: FitScroll + ScrollHint, SLOTS-04).
func show_slots() -> void:
	var latest := ""
	var best := -1.0
	for slot in SLOTS:
		var at := float(RunManager.slot_summary(slot).get("saved_at", -1.0))
		if at > best:
			best = at
			latest = slot
	var win := CrtWindow.new(tr("Campaign slots"), Palette.NET_CYAN, page_room())
	win.name = "Slots"
	win.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	var grid := GridContainer.new()
	grid.name = "Cards"
	grid.columns = slot_columns()
	grid.add_theme_constant_override("h_separation", UiTheme.GUTTER)
	grid.add_theme_constant_override("v_separation", UiTheme.GUTTER)
	for slot in SLOTS:
		var summary := RunManager.slot_summary(slot)
		var card := CaseFileCard.new(slot, summary, slot_crew(slot) if not summary.is_empty() else [], slot == latest)
		card.load_pressed.connect(load_slot)
		card.delete_pressed.connect(confirm_delete)
		card.new_pressed.connect(new_in_slot)
		# The slot in words on hover (a screen reader's line too).
		card.folder.tooltip_text = UiTip.fold("%s: %s" % [tr("SLOT %s") % slot, _describe(summary)])
		card.folder.mouse_filter = Control.MOUSE_FILTER_PASS
		grid.add_child(card)
	win.body.add_child(grid)
	var box := VBoxContainer.new()
	box.name = "SlotsBox"
	box.add_theme_constant_override("separation", SLOT_ROW_GAP)  # room for the focus brackets over Back
	box.add_child(win)
	var back := _item(box, tr("Back"), show_main, StatIcon.BACK, tr("Back to the main menu."))
	back.name = "Back"
	var page := _page("CAMPAIGN SLOTS", box, "SlotsPage")
	# SLOTS-04: the panel wraps its cards (the city shows below), never the page's full height.
	box.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	win.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	# The cards' first cap: the page's room less the rows outside the scrolling view that are
	# known before layout (the sticker, Back, the panel's pads); _trim_slots then gives the
	# view exactly the room left once the page is laid out.
	var head := page.get_child(0) as Control
	win.fit.max_height = maxf(FitScroll.MIN_VIEW * Settings.text_scale, page_room() - head.get_combined_minimum_size().y
		- back.get_combined_minimum_size().y - SLOT_ROW_GAP - CrtWindow.PAD_TOP - CrtWindow.PAD_BOTTOM)
	_set_panel(page, "slots")
	_slots_trims = SLOTS_TRIM_PASSES
	if is_inside_tree() and not get_tree().process_frame.is_connected(_trim_slots):
		get_tree().process_frame.connect(_trim_slots, CONNECT_ONE_SHOT)


## The page's room under the subtitles' band and over the ticker (px).
func page_room() -> float:
	return get_viewport_rect().size.y - SubtitleStrip.top_below(PAGE_MARGIN.y) - PAGE_MARGIN.z - ticker.get_combined_minimum_size().y


## Frames the slots page still checks its fit (see _trim_slots).
var _slots_trims: int = 0


## SLOTS-04: once the slots page is laid out, the cards' view takes exactly the room left over
## the ticker: shorter when Back would run under the ticker, taller (up to its cards) when it
## scrolls with room to spare. Read from the page's own layout (its entrance may be moving it).
func _trim_slots() -> void:
	var page := _panel
	if panel_name != "slots" or page == null or not is_instance_valid(page) or not is_inside_tree():
		return
	var win := page.find_child("Slots", true, false) as CrtWindow
	var back := page.find_child("Back", true, false) as Control
	if win != null and win.fit != null and back != null:
		var bottom := _panel_host.global_position.y + (back.global_position.y - page.global_position.y) + back.size.y
		var spare := page_room() + SubtitleStrip.top_below(PAGE_MARGIN.y) - bottom
		if spare < -0.5 or (spare > 0.5 and win.fit.overflowing()):
			win.fit.max_height = maxf(FitScroll.MIN_VIEW * Settings.text_scale, win.fit.max_height + floorf(spare))
	_slots_trims -= 1
	if _slots_trims > 0 and not get_tree().process_frame.is_connected(_trim_slots):
		get_tree().process_frame.connect(_trim_slots, CONNECT_ONE_SHOT)


## Case files per row: 3 while three fit the screen, then 2, then 1 (ported from
## art-m13-final title_scene.gd slot_columns).
func slot_columns() -> int:
	var room := get_viewport_rect().size.x - PAGE_MARGIN.x * 2 - CrtWindow.PAD_H * 2
	var w := CaseFileCard.width() + UiTheme.GUTTER
	return clampi(int((room + UiTheme.GUTTER) / w), 1, SLOTS.size())


## The crew of the campaign in `slot` ([{id, name, class_id, alive}]; [] when unreadable).
## Read-only: the save file is read, never written (ported from art-m13-final).
static func slot_crew(slot: String) -> Array:
	var data := SaveService.load_dict(SaveService.campaign_path(slot))
	var out := []
	for od in (data.get("campaign", {}) as Dictionary).get("roster", []):
		if od is Dictionary:
			out.append({"id": String(od.get("id", "")), "name": String(od.get("name", "")), "class_id": String(od.get("class_id", "")),
				"alive": bool(od.get("alive", true))})
	return out


## The slots page's focus (the cards sit in a grid UiFocus cannot read): left / right walk
## the actions of a row of cards, up / down go to the card above / below (the same place in
## its actions, clamped), the last row down to Back and Back up to the last row.
func _link_slots(page: Control) -> void:
	var grid := page.find_child("Cards", true, false) as GridContainer
	var back := page.find_child("Back", true, false) as Control
	if grid == null:
		return
	var cards: Array[CaseFileCard] = []
	for c in grid.get_children():
		if c is CaseFileCard:
			cards.append(c)
	var cols := maxi(1, grid.columns)
	var rows := ceili(float(cards.size()) / cols)
	for k in cards.size():
		var r := k / cols
		var line: Array[Control] = []
		for j in range(r * cols, mini((r + 1) * cols, cards.size())):
			line.append_array(cards[j].actions())
		var own := cards[k].actions()
		for i in own.size():
			var c := own[i]
			var at := line.find(c)
			c.focus_neighbor_left = c.get_path_to(line[at - 1]) if at > 0 else NodePath()
			c.focus_neighbor_right = c.get_path_to(line[at + 1]) if at + 1 < line.size() else NodePath()
			c.focus_neighbor_top = NodePath()
			if r > 0:
				var up := cards[k - cols].actions()
				c.focus_neighbor_top = c.get_path_to(up[mini(i, up.size() - 1)])
			var below := k + cols
			if below >= cards.size() and r + 1 < rows:
				below = cards.size() - 1  # the last row is short: its last card
			if below < cards.size():
				var down := cards[below].actions()
				c.focus_neighbor_bottom = c.get_path_to(down[mini(i, down.size() - 1)])
			elif back != null:
				c.focus_neighbor_bottom = c.get_path_to(back)
	if back != null and not cards.is_empty():
		var last := cards[(rows - 1) * cols].actions()
		back.focus_neighbor_top = back.get_path_to(last[0])
		back.focus_neighbor_bottom = NodePath()
		back.focus_neighbor_left = NodePath()
		back.focus_neighbor_right = NodePath()


func show_codex() -> void:
	var box := VBoxContainer.new()
	var note := CrtText.new(tr("CODEX // WHAT THE CELL KNOWS"), Vector2(PAGE_W, CODEX_H)).make_reference()
	note.name = "Codex"
	note.fill_codex()
	_flex(note, CODEX_H)
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
	_flex(note, STATS_H)
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
	# Big text: the run history is a section of the records' text (a second window's frame is
	# room the page lacks at 1.6 and up).
	var history := note
	if big_text():
		note.heading(tr("RUN HISTORY"))
	else:
		history = CrtText.new(tr("RUN HISTORY"), Vector2(PAGE_W, HISTORY_H)).make_reference()
		history.name = "History"
		_flex(history, HISTORY_H)
	if p.run_history.is_empty():
		history.append(tr("no runs yet"))
	for r in p.run_history:
		var corp := RunManager.lookup().get_content(StringName(String(r.get("corporation", "")))) as CorporationData
		history.append("%s T%d %s: %s, %d Cycles, %d banked" % [TextDb.t(corp, "display_name") if corp != null else r.get("corporation", "?"), int(r.get("tier", 1)), r.get("site", "?"), r.get("outcome", "?"), int(r.get("cycles", 0)), int(r.get("banked", 0))])
	if history != note:
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


## The delete-slot confirm: the round 33 abandon dialog (AbandonDialog) with the slot's costs.
func confirm_delete(slot: String) -> void:
	var summary := RunManager.slot_summary(slot)
	var costs: Array = []
	if not summary.is_empty():
		costs = [[TextDb.mark("Target"), corporation_name(String(summary.get("corporation", "")))], [TextDb.mark("Runs"), int(summary.get("runs", 0))],
			[TextDb.mark("Heat"), int(summary.get("heat", 0))], [TextDb.mark("ICE"), int(summary.get("ice", 0))]]
	var d := AbandonDialog.new(tr("Delete the campaign in slot %s?") % slot, TextDb.mark("DELETE"), TextDb.mark("DELETE SLOT"),
		tr("The campaign in slot %s is lost for good, with everything in it:") % slot, costs, "",
		tr("Your stats and achievements stay."), tr("erase slot %s [A]") % slot, TextDb.mark("keep going [B]"))
	_open_confirm(d, func() -> void:
		RunManager.delete_slot(slot)
		show_slots())


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
	# 2D's ConfirmDialog (the round 33 abandon dialog): `what` is its title, `detail` its body.
	_open_confirm(ConfirmDialog.new(question, verb, "CANCEL", what if what != "" else "ARE YOU SURE?", detail, destructive, "", "keep going [B]"), on_yes)


## Shows `d` centred on the page (it re-centres as its panel takes its size) with `on_yes` on
## its confirm.
func _open_confirm(d: ConfirmDialog, on_yes: Callable) -> void:
	if _confirm != null and is_instance_valid(_confirm):
		_confirm.queue_free()
	_confirm = d
	d.resized.connect(func() -> void: d.position = ((size - d.size) * 0.5).floor())
	d.position = ((size - d.custom_minimum_size) * 0.5).floor()
	d.confirmed.connect(on_yes)
	add_child(d)


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
		b.add_theme_font_override(&"font", Chrome.caps_font(MORE_STEP))
		b.add_theme_font_size_override(&"font_size", Chrome.px(MORE_STEP))
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
			# The line keeps room for its key hint: the words never run under it.
			var f := b.get_theme_font(&"font")
			var sb := b.get_theme_stylebox(&"normal")
			var words := f.get_string_size(b.text, HORIZONTAL_ALIGNMENT_LEFT, -1, Chrome.px(MORE_STEP)).x
			b.custom_minimum_size.x = maxf(b.custom_minimum_size.x, ceilf(words + sb.get_margin(SIDE_LEFT) + h.get_combined_minimum_size().x + HINT_GAP - h.offset_right))
	else:
		IconMark.attach(b, kind)
		b.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN  # a terminal chip, not a full-width bar
	return b


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(240, 0)
	b.pressed.connect(on_pressed)
	return b
