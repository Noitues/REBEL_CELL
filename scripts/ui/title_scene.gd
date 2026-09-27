extends Control
## Title / main menu (gap analysis 2.5): Continue, Campaigns (three save slots with a
## summary, new / load / delete with confirmation), Tutorial, Codex, Stats &
## achievements, Options, Quit. Cyberdeck world with the graffiti tag. Every action goes
## through RunManager; the scene only displays state.

const SLOTS: Array[String] = ["1", "2", "3"]
## Subtitle lines the header band holds.
const HEADER_LINES := 2
## The plan note on the main menu at text scale 1.0 (it grows with the text, H21 #15).
const PLAN_NOTE := Vector2(150, 96)
## The plan note's text box: its side and top margins (ZineNote) and the lines it holds.
const PLAN_PAD := Vector2(20, 16)
const PLAN_LINES := 3

var background: CyberdeckBackground
## The subtitles' band in the header (H21 #11).
var subtitle_strip: SubtitleStrip
var margin: MarginContainer
var _panel_host: VBoxContainer
var _panel: Control = null
var panel_name: String = ""
var _confirm: ConfirmDialog = null


func _ready() -> void:
	UiTheme.apply(self)
	# Subtitles still on screen from a campaign sit in the top band over the header, clear
	# of every menu (H20).
	Dialogue.dock_default()
	background = CyberdeckBackground.new()
	add_child(background)
	margin = MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["margin_left", "margin_right"]:
		margin.add_theme_constant_override(side, 36)
	margin.add_theme_constant_override("margin_top", 18)
	margin.add_theme_constant_override("margin_bottom", 30)
	add_child(margin)
	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", 10)
	margin.add_child(root)
	var header := HBoxContainer.new()
	header.add_child(GraffitiTag.new("REBEL_CELL"))
	var v := Label.new()
	v.text = "v%s // cell uplink" % ProjectSettings.get_setting("application/config/version", "dev")
	v.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	v.add_theme_color_override("font_color", Color(Palette.NET_CYAN, 0.7))
	header.add_child(v)
	# The subtitles' band beside the tag (H21 #11): no menu, no tag under it.
	subtitle_strip = SubtitleStrip.new(HEADER_LINES)
	header.add_child(subtitle_strip)
	root.add_child(header)
	_panel_host = VBoxContainer.new()
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(_panel_host)
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


# --- Panels -----------------------------------------------------------------------------------

func _set_panel(p: Control, name: String) -> void:
	if _panel != null:
		_panel.queue_free()
	_panel = p
	panel_name = name
	_panel_host.add_child(p)
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	UiFocus.focus_first(p)


func show_main() -> void:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 28)
	var menu := TerminalWindow.new("REBEL_CELL // MAIN MENU")
	menu.custom_minimum_size = Vector2(420, 0)
	menu.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var box := menu.body
	var latest := RunManager.latest_slot()
	# Each item carries an icon (H21 #13) and says what it does on hover.
	if latest != "":
		var summary := RunManager.slot_summary(latest)
		var cont := _item(box, "Continue (slot %s: %s)" % [latest, _describe(summary)], func() -> void: load_slot(latest), StatIcon.CONTINUE,
			"Pick up the campaign saved most recently.")
		cont.name = "Continue"
	_item(box, "Campaigns", show_slots, StatIcon.SLOTS, "The three campaign slots: start, load or delete.")
	_item(box, "Tutorial", start_tutorial, StatIcon.TUTORIAL, "A guided first fight.")
	_item(box, "Codex", show_codex, StatIcon.CODEX, "Everything the Cell knows: slices, cards, Firmware, Daemons, rules.")
	_item(box, "Stats & achievements", show_stats, StatIcon.STATS, "Your records, achievements and run history.")
	_item(box, "Options", show_options, StatIcon.SETTINGS, "Text size, sound, controls, subtitles.")
	_item(box, "Quit", confirm_quit, StatIcon.QUIT, "Leave REBEL_CELL (asks first).")
	for b in box.get_children():
		b.theme_type_variation = &"MenuItem"
		(b as Button).alignment = HORIZONTAL_ALIGNMENT_LEFT
	row.add_child(menu)
	# Right column: system readout, the plan on a taped note and a scrawl.
	var side := VBoxContainer.new()
	side.add_theme_constant_override("separation", 22)
	side.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var p := RunManager.profile
	# The profile at a glance as paper tags (H20: no text readout); Stats has the rest.
	var sys := TerminalWindow.new("SYSTEM ONLINE", Palette.NET_CYAN)
	sys.name = "ProfileTags"
	sys.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var tags := HudStats.new()
	tags.name = "Tags"
	# A number or "—", never "none" (H21 #21).
	tags.items = [["CAMPAIGNS", str(p.campaigns_started), "", "Campaigns started on this profile."],
		["WON", str(p.campaigns_won), "", "Campaigns won."],
		["BEST ICE", HudStats.ice_value(p.best_ice), "", "The highest ICE level cleared (— until you clear one). Each corporation keeps its own ladder."],
		["RUNS", str(p.runs_completed), "", "Netruns completed."],
		["RAIDS", "%d/%d" % [p.raids_won, p.raids_lost], "", "Raids repelled / lost."],
		["BADGES", str(p.achievements.size()), "", "Achievements earned (Stats & achievements lists them)."]]
	# The least room the tags need; they grow with the text where the column allows.
	tags.custom_minimum_size.x = tags.compact_width(1.0)
	sys.body.add_child(tags)
	side.add_child(sys)
	var notes := HBoxContainer.new()
	notes.add_theme_constant_override("separation", 30)
	# The plan note holds its three lines at any text size (H21 #15: at 1.6 it showed only
	# the last two and scrolled "1. BREACH" away).
	var ts := Settings.text_scale
	var plan_h := PLAN_PAD.y + Palette.marker().get_height(roundi(UiTheme.BASE_SIZE * ts)) * PLAN_LINES
	var plan := ZineNote.new("", Vector2(PLAN_NOTE.x * maxf(1.0, ts), maxf(PLAN_NOTE.y, plan_h)))
	plan.name = "PlanNote"
	plan.paper_color = Palette.NOTE_YELLOW
	plan.label.add_theme_font_override("normal_font", Palette.marker())
	plan.label.scroll_following = false
	plan.append("1. BREACH\n2. DISABLE\n3. EXFIL")
	plan.rotation_degrees = -4.0
	plan.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plan.label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	notes.add_child(plan)
	notes.add_child(GraffitiScrawl.new("NEVER\nSLEEP", -10.0, 34))
	side.add_child(notes)
	row.add_child(side)
	_set_panel(row, "main")


func show_slots() -> void:
	var win := TerminalWindow.new("Campaign slots")
	# A compact window, not the full width.
	win.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	win.custom_minimum_size.x = 560
	var box := win.body
	for slot in SLOTS:
		var row := HFlowContainer.new()
		var summary := RunManager.slot_summary(slot)
		row.add_child(_label("Slot %s: %s" % [slot, _describe(summary)]))
		var s := slot
		if summary.is_empty():
			_item(row, "New campaign", func() -> void: new_in_slot(s), StatIcon.PLAY, "Start a new campaign in slot %s." % s)
		else:
			_item(row, "Load", func() -> void: load_slot(s), StatIcon.CONTINUE, "Load the campaign in slot %s." % s)
			_item(row, "Delete", func() -> void: confirm_delete(s), StatIcon.QUIT, "Delete the campaign in slot %s (asks first)." % s)
		box.add_child(row)
	_item(box, "Back", show_main, StatIcon.BACK, "Back to the main menu.")
	_set_panel(win, "slots")


func show_codex() -> void:
	var box := VBoxContainer.new()
	var note := ZineNote.new("CODEX", Vector2(900, 420)).make_reference()
	var entries := Codex.entries(RunManager.lookup(), RunManager.profile)
	for section in entries:
		note.append("[b]%s[/b]" % section)
		for item in entries[section]:
			note.append("  %s - %s" % [item["title"], String(item["text"]).split("\n")[0]])
	box.add_child(note)
	_item(box, "Back", show_main, StatIcon.BACK, "Back to the main menu.")
	_set_panel(box, "codex")


func show_stats() -> void:
	var p := RunManager.profile
	var box := VBoxContainer.new()
	var note := ZineNote.new("STATS", Vector2(900, 200)).make_reference()
	note.append("Campaigns: %d started, %d won, %d lost. Runs completed: %d. Operatives lost: %d. Raids: %d won / %d lost." % [
		p.campaigns_started, p.campaigns_won, p.campaigns_lost, p.runs_completed, p.operatives_lost, p.raids_won, p.raids_lost])
	note.append("Best ICE: %s. Perfects: %d. Racks captured: %d. Cycles earned: %d. Assisted wins: %d." % [HudStats.ice_value(p.best_ice), int(p.stats.get("perfects", 0)), int(p.stats.get("racks", 0)), int(p.stats.get("cycles", 0)), int(p.stats.get("assisted_wins", 0))])
	var per_corp := PackedStringArray()
	for cid in RunManager.lookup().ids_of_class(&"CorporationData"):
		var corp := RunManager.lookup().get_content(cid) as CorporationData
		if corp != null and (not corp.generated_from_profile or CampaignRules.corporation_available(p, RunManager.lookup(), corp)):
			per_corp.append("%s %s" % [TextDb.t(corp, "display_name"), HudStats.ice_value(p.best_ice_for(corp.id))])
	note.append("Best ICE by corporation: %s." % ", ".join(per_corp))
	note.append("[b]Achievements[/b]")
	for d in Achievements.DEFS:
		var have := p.achievements.has(d["id"])
		note.append("%s %s - %s" % ["[x]" if have else "[ ]", d["title"], d["text"]])
	box.add_child(note)
	var history := ZineNote.new("RUN HISTORY", Vector2(900, 160)).make_reference()
	if p.run_history.is_empty():
		history.append("no runs yet")
	for r in p.run_history:
		var corp := RunManager.lookup().get_content(StringName(String(r.get("corporation", "")))) as CorporationData
		history.append("%s T%d %s: %s, %d Cycles, %d banked" % [TextDb.t(corp, "display_name") if corp != null else r.get("corporation", "?"), int(r.get("tier", 1)), r.get("site", "?"), r.get("outcome", "?"), int(r.get("cycles", 0)), int(r.get("banked", 0))])
	box.add_child(history)
	_item(box, "Back", show_main, StatIcon.BACK, "Back to the main menu.")
	_set_panel(box, "stats")


func show_options() -> void:
	var box := VBoxContainer.new()
	var panel := SettingsPanel.new()
	panel.closed.connect(show_main)
	box.add_child(panel)
	_set_panel(box, "options")


# --- Actions ---------------------------------------------------------------------------------

func new_in_slot(slot: String) -> void:
	RunManager.save_slot = slot
	RunManager.reset()
	RunManager.change_scene(RunManager.HQ_SCENE)


func load_slot(slot: String) -> void:
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
	_ask("Delete the campaign in slot %s? This cannot be undone." % slot, func() -> void:
		RunManager.delete_slot(slot)
		show_slots())


func confirm_quit() -> void:
	_ask("Quit REBEL_CELL?", RunManager.quit_game)


func start_tutorial() -> void:
	RunManager.pending_tutorial = true
	RunManager.change_scene(RunManager.COMBAT_SCENE)


func _ask(question: String, on_yes: Callable) -> void:
	if _confirm != null and is_instance_valid(_confirm):
		_confirm.queue_free()
	_confirm = ConfirmDialog.new(question)
	_confirm.position = Vector2(size.x / 2.0 - 210, 200)
	_confirm.confirmed.connect(on_yes)
	add_child(_confirm)


func confirm_visible() -> bool:
	return _confirm != null and is_instance_valid(_confirm) and _confirm.is_inside_tree()


# --- Helpers ----------------------------------------------------------------------------------

func _describe(summary: Dictionary) -> String:
	if summary.is_empty():
		return "empty"
	return "%s, Heat %d, ICE %d, %d runs, %s%s" % [corporation_name(String(summary.get("corporation", ""))), int(summary.get("heat", 0)), int(summary.get("ice", 0)),
		int(summary.get("runs", 0)), String(summary.get("state", "active")), (" (run in progress)" if summary.get("in_run", false) else "")]


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
