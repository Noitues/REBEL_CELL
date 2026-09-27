extends Control
## HQ scene: start screen (seed, ICE, home server, profile), HQ (roster, recruit, station,
## boosts, unlocks, Rank 3 segment swaps, Armory, story, pending raids), City Grid (Site
## status and actions, node install with unlock gating, upgrades), raid setup with exact
## projection, the raid playout with speed controls, the summary, campaign end. Every
## action goes through RunManager and CampaignRules; the scene only displays state.

const STATUS_NAMES := {GridState.SiteStatus.CORPORATE: "corporate", GridState.SiteStatus.CLEARED: "cleared",
	GridState.SiteStatus.CLAIMED: "claimed", GridState.SiteStatus.SEIZED: "SEIZED"}

## Screen titles on the HUD strip, by panel name (STYLE_GUIDE 4, "Neon city").
const SCREEN_TITLES := {"start": ["00", "JACK A CAMPAIGN IN"], "hq": ["01", "CYBERDECK HQ"], "grid": ["02", "CITY GRID"],
	"raid": ["03", "CELL DEFENSE RAID SETUP"], "raid_playout": ["03", "RAID IN PROGRESS"], "raid_summary": ["03", "RAID REPORT"],
	"codex": ["", "CODEX"], "end": ["", "CAMPAIGN END"]}

## The home server's name on the Grid, the raid map and the orders (never its id).
const HOME_LABEL := "CORE"
## Event types that pop a toast (H20: the log strip is optional): refusals in pink,
## news in acid.
const TOAST_WARN_EVENTS: Array[String] = ["refused", "deploy_failed", "undock_failed"]
const TOAST_NEWS_EVENTS: Array[String] = ["unlocked"]
## The Grid's side column and the raid setup column (px).
const GRID_SIDE_WIDTH := 440.0
const RAID_SIDE_WIDTH := 380.0
## Glyphs for Site objectives and facts on badges (the map uses the same).
const GLYPH_EXPLOIT := "◈"
const GLYPH_HEAT := "❄"
const GLYPH_BOSS := "✦"
const GLYPH_HOME := "⌂"
const GLYPH_NODE := "⬡"
const GLYPH_RULE := "!"
const GLYPH_UPGRADE := "▲"
const GLYPH_GUARD := "☻"
const GLYPH_THREAT := "◆"
const GLYPH_ENTRY := ">"
const GLYPH_LINK := "⛓"
## Raid setup: the projection stamp's side and a node's target button width (px).
const PROJECTION_STAMP := 124.0
const TARGET_BUTTON_WIDTH := 150.0
## Entry Sites shown one badge each up to this many; more collapse into a count.
const MAX_ENTRY_BADGES := 3
## Height of the raid's node orders list (px); more nodes scroll inside it.
const ORDERS_HEIGHT := 150.0
## What each Site status means (the selected Site card's status badge).
const STATUS_TIPS := {GridState.SiteStatus.CORPORATE: "Corporate: run it to clear it.",
	GridState.SiteStatus.CLEARED: "Cleared: claim it to build a node of your network.",
	GridState.SiteStatus.CLAIMED: "Claimed: part of your network; it defends in raids.",
	GridState.SiteStatus.SEIZED: "Seized by a raid: run it again to take it back."}

var _status: Label
## Top strip: screen title and the status line (`_status`).
var hud: HudBar
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var panel_name: String = ""
var background: CyberdeckBackground
var wireframe: WireframeBackground
var grid_view: GridMapView = null
var playout: RaidPlayoutPanel = null
## The map drawn on the city (Grid, raids); freed when another panel opens.
var city_overlay: CityMapOverlay = null
var _settings_panel: PauseMenu = null
var _last_warned_raid: String = ""
## Site picked on the Grid map (its card and actions show in the side column) or the
## raid target node.
var selected_site: StringName = &""
## Operative picked on a dossier: VIEW LOADOUT and the Daemon tray show them.
var selected_operative: StringName = &""
## Buttons carrying a key hint (relabelled on Settings.hints_changed).
var _hint_buttons: Array[Button] = []


func _ready() -> void:
	UiTheme.apply(self)
	# Subtitles sit in the top band, clear of every control on these screens (H20).
	Dialogue.dock_default()
	Settings.hints_changed.connect(_relabel_hints)
	_build_ui()
	var args := OS.get_cmdline_user_args()
	for a in args:
		# Design review: portrait and slice-icon styles.
		if a.begins_with("--demo-portrait="):
			PortraitArt.style = int(a.trim_prefix("--demo-portrait="))
		elif a.begins_with("--demo-iconstyle="):
			SliceIcon.style = int(a.trim_prefix("--demo-iconstyle="))
	if args.has("--demo-start"):
		RunManager.save_slot = "demo"
		show_start()
		return
	if args.has("--demo-hq") or args.has("--demo-grid") or args.has("--demo-raid") or args.has("--demo-playout"):
		# Dev shortcut for screenshots: godot --path . -- --demo-grid (own save slot)
		RunManager.save_slot = "demo"
		new_campaign(1)
		for a in args:
			if a.begins_with("--demo-corp="):
				# Screenshot campaign against another corporation (bypasses Profile unlocks,
				# campaign-only).
				var corp := RunManager.lookup().get_content(StringName(a.trim_prefix("--demo-corp="))) as CorporationData
				if corp != null:
					var home := RunManager.lookup().get_content(RunManager.DEFAULT_HOME) as HomeServerVariantData
					RunManager.corporation = corp
					RunManager.campaign = CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
						RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, 0, home)
					show_hq()
		if args.has("--demo-classes"):
			# Screenshot roster: one operative of every class (bypasses Profile unlocks,
			# campaign-only, never saved to the profile).
			RunManager.campaign.roster.clear()
			for id in [&"ghost", &"rigger", &"botnet", &"wrecker", &"phantom", &"overclocker", &"hivemind"]:
				RunManager.campaign.recruit(RunManager.lookup().get_content(id) as ClassData)
			show_hq()
		if args.has("--demo-grid") or args.has("--demo-raid") or args.has("--demo-playout"):
			var c := RunManager.campaign
			c.schematics = 100
			var grid_data := RunManager.corporation.city_grid
			var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
			CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), _demo_run(first))
			CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
			c.armory = [&"turret", &"ice_lock", &"decoy"]
			if args.has("--demo-raid") or args.has("--demo-playout"):
				CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
				show_raid()
				if args.has("--demo-playout"):
					fight_raid()
			else:
				for sd in grid_data.sites:
					if sd.objective == RC.SiteObjective.EXPLOIT:
						selected_site = sd.id
						break
				show_grid()
		return
	if RunManager.campaign == null and RunManager.has_save():
		RunManager.resume()
	if RunManager.campaign == null:
		show_start()
	elif RunManager.campaign.is_over():
		show_end()
	else:
		show_hq()


# --- Public API (buttons and the integration tests) ---------------------------------------

## Best ICE per corporation (GDD 3.4) and the road to REBEL_CELL.
func ice_records_text() -> String:
	var p := RunManager.profile
	var lookup := RunManager.lookup()
	var parts := PackedStringArray()
	var cleared := 0
	var total := 0
	var need := RunManager.config().rebel_cell_unlock_ice
	var corp_ids := lookup.ids_of_class(&"CorporationData")
	for id in corp_ids:
		var corp := lookup.get_content(id) as CorporationData
		if corp == null:
			continue
		if corp.generated_from_profile and not CampaignRules.corporation_available(p, lookup, corp):
			continue
		parts.append("%s %s" % [corp.display_name, ProfileState.ice_text(p.best_ice_for(corp.id))])
		if not corp.generated_from_profile:
			total += 1
			if p.best_ice_for(corp.id) >= need:
				cleared += 1
	var tail := ("Something opens at ICE %d everywhere (%d/%d)." % [need, cleared, total]) if cleared < total else ""
	return "Best ICE: %s. %s" % [", ".join(parts), tail]


## Starts the campaign a share code describes (GAP_ANALYSIS P2 12). Locked choices fall
## back like the start panel (RunManager.new_campaign). Returns false for a bad code.
func start_from_code(code: String) -> bool:
	var d := CampaignCode.decode(code)
	if d.is_empty():
		var refused: Array[Dictionary] = [{"type": "refused", "text": "That is not a campaign code."}]
		_report(refused)
		return false
	new_campaign(int(d["seed"]), int(d["ice"]), d["home"], d["class"], d["corporation"])
	return true


func new_campaign(seed: int, ice: int = 0, home_variant_id: StringName = RunManager.DEFAULT_HOME, class_id: StringName = RunManager.DEFAULT_CLASS, corporation_id: StringName = RunManager.DEFAULT_CORPORATION) -> void:
	RunManager.new_campaign(seed, corporation_id, ice, home_variant_id, class_id)
	_log.append_text("[b]New campaign[/b] (seed %d, ICE %d, %s) against %s. Story path: %s.\n" % [seed, RunManager.campaign.ice_level,
		RunManager.campaign.home_variant_id, RunManager.corporation.display_name, RunManager.campaign.story_path_id])
	show_hq()


func resume() -> void:
	if RunManager.resume():
		_log.append_text("[b]Resumed.[/b]\n")
		if RunManager.has_active_run():
			RunManager.go_to_netrun()
		else:
			show_hq()
	else:
		_log.append_text("[color=orange]Nothing to resume.[/color]\n")
		notify("Nothing to resume.", true)


func launch(site_id: StringName, operative_id: StringName) -> bool:
	var err := RunManager.launch_error(operative_id, site_id)
	if err != "":
		_log.append_text("[color=orange]%s[/color]\n" % err)
		notify(err, true)
		return false
	var s := RunManager.start_run(operative_id, site_id)
	if s == null:
		return false
	_report(s.last_events)
	Dialogue.briefing(RunManager.campaign.corporation_id, site_id, RunManager.campaign.campaign_seed)
	RunManager.go_to_netrun()
	return true


func claim(site_id: StringName, node_type_id: StringName) -> void:
	_report(CampaignRules.claim(RunManager.campaign, RunManager.corporation, RunManager.config(), RunManager.lookup(), site_id, node_type_id, RunManager.profile))
	RunManager.autosave()
	show_grid()


func repair(site_id: StringName) -> void:
	_report(CampaignRules.repair(RunManager.campaign, RunManager.config(), RunManager.lookup(), site_id))
	RunManager.autosave()
	show_grid()


func upgrade(site_id: StringName) -> void:
	_report(CampaignRules.upgrade_node(RunManager.campaign, RunManager.config(), RunManager.lookup(), site_id))
	RunManager.autosave()
	show_grid()


func repair_home() -> void:
	_report(CampaignRules.repair_home(RunManager.campaign, RunManager.config()))
	RunManager.autosave()
	show_hq()


func recruit(class_id: StringName = RunManager.DEFAULT_CLASS) -> void:
	_report(RunManager.recruit(class_id))
	RunManager.autosave()
	show_hq()


func station(operative_id: StringName, site_id: StringName) -> void:
	_report(CampaignRules.station(RunManager.campaign, RunManager.lookup(), operative_id, site_id))
	RunManager.autosave()
	show_hq()


func recall(operative_id: StringName) -> void:
	CampaignRules.recall(RunManager.campaign, operative_id)
	RunManager.autosave()
	show_hq()


func buy_heat_reduction() -> void:
	_report(CampaignRules.buy_heat_reduction(RunManager.campaign, RunManager.config()))
	RunManager.autosave()
	show_hq()


func buy_boost(boost_id: StringName) -> void:
	_report(CampaignRules.buy_boost(RunManager.campaign, RunManager.config(), boost_id))
	RunManager.autosave()
	show_hq()


func purchase_unlock(unlock_id: StringName) -> void:
	_report(CampaignRules.purchase_unlock(RunManager.campaign, RunManager.profile, RunManager.lookup(), unlock_id))
	RunManager.save_profile()
	RunManager.autosave()
	show_hq()


func swap_segment(operative_id: StringName, index: int, segment_id: StringName) -> void:
	_report(CampaignRules.swap_ring_segment(RunManager.campaign, RunManager.lookup(), operative_id, index, segment_id))
	RunManager.autosave()
	show_hq()


func deploy_asset(armory_index: int, site_id: StringName) -> void:
	_report(CampaignRules.deploy_asset(RunManager.campaign, RunManager.config(), RunManager.lookup(), armory_index, site_id))
	RunManager.autosave()
	show_raid()


func move_asset(from_site: StringName, index: int, to_site: StringName) -> void:
	_report(CampaignRules.move_asset(RunManager.campaign, RunManager.config(), RunManager.lookup(), from_site, index, to_site))
	RunManager.autosave()
	show_raid()


func fight_raid() -> void:
	var events := RunManager.fight_raid()
	_report(events)
	show_raid_playout(events)


# --- Panels ---------------------------------------------------------------------------------

func _set_panel(p: Control, name: String) -> void:
	if _panel != null:
		_panel.queue_free()
	_clear_city_map()
	# City map screens: clicks fall through the empty panel area to the map.
	var on_city := name in ["grid", "raid", "raid_playout", "raid_summary"] or name.begins_with("city")
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE if on_city else Control.MOUSE_FILTER_STOP
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel = p
	panel_name = name
	_panel_host.add_child(p)
	# Screens built from terminal windows let the city show between them.
	_panel_host.theme_type_variation = &"" if name in ["hq", "start", "grid", "raid", "raid_playout", "raid_summary"] or name.begins_with("city") else &"GlassPanel"
	var t: Array = SCREEN_TITLES.get(name, ["", ""])
	hud.set_screen(t[0], t[1])
	UiWrap.fit(p)
	UiFocus.link_layout(p)
	UiFocus.focus_first(p)
	_scroll_to_top.call_deferred()
	# Worlds (STYLE_GUIDE 1): the room is a cyberdeck, the Grid and raids are wireframe.
	var net := name in ["grid", "raid", "raid_playout", "raid_summary"] or name.begins_with("city")
	background.visible = not net
	wireframe.visible = net
	AudioDirector.play_music("raid" if name.begins_with("raid") else ("grid" if name == "grid" else "hq"),
		RunManager.campaign.corporation_id if RunManager.campaign != null else &"")
	if RunManager.campaign != null:
		var band := RunManager.campaign.heat_majors_crossed(RunManager.config())
		background.heat_band = band
		wireframe.corp_creep = band / 3.0
		wireframe.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
		background.set_district(RunManager.campaign.corporation_id)
		wireframe.set_district(RunManager.campaign.corporation_id)
	_refresh_status()


## A new panel opens at its top (the first focus lands before layout and can
## otherwise leave the scroll part-way down, hiding the header row).
func _scroll_to_top() -> void:
	var scroll := _panel_host.get_parent() as ScrollContainer
	if scroll != null:
		scroll.scroll_vertical = 0
		await get_tree().process_frame
		if is_instance_valid(scroll):
			scroll.scroll_vertical = 0


## VIEW LOADOUT: an operative's deck and spinner. A dossier's Loadout button opens its
## operative (and selects them); the top bar opens the selected one, and NEXT OPERATIVE
## in the view cycles through the living crew (H20).
func open_loadout(op: OperativeState = null) -> void:
	var c := RunManager.campaign
	if c == null or has_node("LoadoutView"):
		return
	if op == null:
		op = selected_op()
		if op == null:
			return
	select_operative(op.id)
	var view := LoadoutView.new(op, RunManager.lookup(), RunManager.config().shop_slices, c.living_operatives())
	view.operative_changed.connect(select_operative)
	add_child(view)


## The Daemon tray of the selected operative (top bar DAEMONS icon).
func open_daemons() -> void:
	var op := selected_op()
	if op == null or has_node("DaemonTray"):
		return
	add_child(DaemonTray.new(op.daemon_ids, RunManager.lookup(), hud.daemon_button.get_global_rect().end.x, op.name))


## Makes `operative_id` the operative the top bar's VIEW LOADOUT and DAEMONS show.
func select_operative(operative_id: StringName) -> void:
	selected_operative = operative_id
	_refresh_status()


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
	_settings_panel = PauseMenu.new()
	_settings_panel.position = Vector2((size.x - PauseMenu.MENU_SIZE.x) / 2.0, 100)
	_settings_panel.resumed.connect(open_settings)
	_settings_panel.quit_to_title.connect(func() -> void: open_settings(); RunManager.go_to_title())
	add_child(_settings_panel)
	get_tree().paused = false


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("open_settings"):
		open_settings()
		get_viewport().set_input_as_handled()


func show_start() -> void:
	var cfg := RunManager.config()
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	var head := HBoxContainer.new()
	head.add_theme_constant_override("separation", 24)
	head.add_child(GraffitiTag.new("REBEL_CELL"))
	head.add_child(GraffitiScrawl.new("TRUST\nNO ONE", -7.0, 26))
	box.add_child(head)
	var setup := TerminalWindow.new("NEW CAMPAIGN // [HQ] the deck is warm. Jack a campaign in.")
	box.add_child(setup)
	var row := HFlowContainer.new()
	setup.body.add_child(row)
	row.add_child(_label("Campaign seed:"))
	var seed_spin := SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = 999999
	seed_spin.value = 1
	seed_spin.name = "SeedSpin"
	row.add_child(seed_spin)
	var next_seed := _button("+1", func() -> void: seed_spin.value = int(seed_spin.value) + 1)
	next_seed.name = "SeedNext"
	row.add_child(next_seed)
	row.add_child(_label("Target:"))
	var corp_pick := OptionButton.new()
	corp_pick.name = "CorporationPicker"
	var corps := RunManager.available_corporations()
	for corp in corps:
		corp_pick.add_item(corp.display_name)
	row.add_child(corp_pick)
	var cap := RunManager.ice_cap(corps[0].id if not corps.is_empty() else RunManager.DEFAULT_CORPORATION)
	var ice_label := _label("ICE (0-%d):" % cap)
	row.add_child(ice_label)
	var ice_spin := SpinBox.new()
	ice_spin.name = "IceSpin"
	ice_spin.min_value = 0
	ice_spin.max_value = cap
	ice_spin.value = 0
	row.add_child(ice_spin)
	# SpinBoxes ignore the D-pad: explicit buttons make ICE and seed pad-reachable.
	var ice_down := _button("-", func() -> void: ice_spin.value = maxf(ice_spin.min_value, ice_spin.value - 1))
	ice_down.name = "IceDown"
	row.add_child(ice_down)
	var ice_up := _button("+", func() -> void: ice_spin.value = minf(ice_spin.max_value, ice_spin.value + 1))
	ice_up.name = "IceUp"
	row.add_child(ice_up)
	# Each corporation has its own ICE ladder (GDD 3.4).
	corp_pick.item_selected.connect(func(i: int) -> void:
		var corp_cap := RunManager.ice_cap(corps[i].id)
		ice_spin.max_value = corp_cap
		ice_label.text = "ICE (0-%d):" % corp_cap)
	var ice_text := _label(_ice_description(0))
	ice_spin.value_changed.connect(func(v: float) -> void: ice_text.text = _ice_description(int(v)))
	row.add_child(_label("Home server:"))
	var home_pick := OptionButton.new()
	var variants := RunManager.available_home_variants()
	for v in variants:
		home_pick.add_item(v.display_name)
	row.add_child(home_pick)
	row.add_child(_label("Crew:"))
	var class_pick := OptionButton.new()
	var classes := RunManager.available_classes()
	for cls in classes:
		class_pick.add_item(cls.display_name)
	row.add_child(class_pick)
	var start_btn := _button("New campaign", func() -> void:
		new_campaign(int(seed_spin.value), int(ice_spin.value), variants[home_pick.selected].id if not variants.is_empty() else RunManager.DEFAULT_HOME,
			classes[class_pick.selected].id if not classes.is_empty() else RunManager.DEFAULT_CLASS,
			corps[corp_pick.selected].id if not corps.is_empty() else RunManager.DEFAULT_CORPORATION))
	start_btn.theme_type_variation = &"HotButton"
	start_btn.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
	setup.body.add_child(ice_text)
	setup.body.add_child(start_btn)
	# Daily run and share codes side by side; the daily panel lists today's setup and
	# has room for the day's modifiers.
	var code_split := HBoxContainer.new()
	code_split.add_theme_constant_override("separation", 14)
	box.add_child(code_split)
	var daily := TerminalWindow.new("TODAY'S RUN", Palette.CELL_ACID)
	daily.name = "DailyRun"
	daily.custom_minimum_size.x = 420
	code_split.add_child(daily)
	var today := Time.get_date_dict_from_system()
	var daily_seed := CampaignCode.daily_seed(today["year"], today["month"], today["day"])
	daily.tag_label.text = "%04d-%02d-%02d" % [today["year"], today["month"], today["day"]]
	for line in daily_lines(daily_seed):
		daily.body.add_child(_label(line))
	daily.body.add_child(_button("Daily run", func() -> void: new_campaign(daily_seed)))
	var codes := TerminalWindow.new("SHARE CODES", Palette.CELL_ACID)
	codes.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	code_split.add_child(codes)
	var code_row := HFlowContainer.new()
	var code_edit := LineEdit.new()
	code_edit.name = "CodeEdit"
	code_edit.placeholder_text = "RC1-corporation-ice-seed-home-class"
	code_edit.custom_minimum_size.x = 360
	# Esc leaves the field (a focused LineEdit would otherwise swallow it).
	code_edit.gui_input.connect(func(ev: InputEvent) -> void:
		if ev.is_action_pressed("ui_cancel") or ev.is_action_pressed("open_settings"):
			code_edit.release_focus()
			code_edit.accept_event()
			UiFocus.focus_first(_panel))
	code_row.add_child(code_edit)
	code_row.add_child(_button("Start from code", func() -> void: start_from_code(code_edit.text)))
	codes.body.add_child(code_row)
	var lower := HBoxContainer.new()
	lower.add_theme_constant_override("separation", 14)
	box.add_child(lower)
	var menu := TerminalWindow.new("CYBERDECK")
	menu.custom_minimum_size.x = 300
	menu.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	lower.add_child(menu)
	var profile := TerminalWindow.new("PROFILE // RECORDS", Palette.CELL_PINK)
	profile.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lower.add_child(profile)
	if RunManager.has_save():
		menu.body.add_child(_button("Resume saved campaign", resume))
	var p := RunManager.profile
	profile.body.add_child(_para("Profile: %d campaigns started, %d won, %d lost; %d runs completed, %d operatives lost, raids %d/%d; best ICE %s." % [
		p.campaigns_started, p.campaigns_won, p.campaigns_lost, p.runs_completed, p.operatives_lost, p.raids_won, p.raids_lost, ProfileState.ice_text(p.best_ice)]))
	profile.body.add_child(_para(ice_records_text()))
	var unlock_names := PackedStringArray()
	for uid in p.unlocks:
		var ud := RunManager.lookup().get_content(uid) as ProfileUnlockData
		unlock_names.append(ud.display_name if ud != null else String(uid))
	profile.body.add_child(_para("Unlocks: %s" % (", ".join(unlock_names) if not unlock_names.is_empty() else "none yet (buy them at HQ with campaign Schematics)")))
	var options_btn := _hint_button("Options", &"open_settings", open_settings)
	options_btn.name = "OptionsButton"
	menu.body.add_child(options_btn)
	menu.body.add_child(_button("Codex", show_codex))
	menu.body.add_child(_button("Back to title", RunManager.go_to_title))
	_as_menu(menu.body)
	_set_panel(box, "start")


## Today's daily run as display lines: the fixed setup, then the day's modifiers (the
## list is empty until daily modifiers are designed; DECISIONS.md open question).
func daily_lines(seed: int) -> PackedStringArray:
	var lines := PackedStringArray()
	lines.append("> SEED     %d" % seed)
	lines.append("> TARGET   %s" % RunManager.lookup().get_content(RunManager.DEFAULT_CORPORATION).display_name)
	lines.append("> ICE      0")
	lines.append("> HOME     standard")
	lines.append("> CREW     Breaker")
	var mods := daily_modifiers(seed)
	lines.append("> MODIFIERS")
	if mods.is_empty():
		lines.append("    none today")
	for m in mods:
		lines.append("    + %s" % m)
	return lines


## The day's modifier descriptions (none yet: the daily run fixes only the seed).
func daily_modifiers(_seed: int) -> PackedStringArray:
	return PackedStringArray()


## The cumulative ICE ladder up to `level`, one line.
func _ice_description(level: int) -> String:
	if level <= 0:
		return "ICE 0: the baseline rules."
	var parts := PackedStringArray()
	for l in RunManager.config().ice_ladder:
		if l != null and l.level <= level and l.description != "":
			parts.append("%d %s" % [l.level, l.description])
	return "ICE %d: %s" % [level, " | ".join(parts)]


func show_hq() -> void:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	var cols := HBoxContainer.new()
	cols.add_theme_constant_override("separation", 14)
	box.add_child(cols)
	# Right column (built now, added last): wanted poster, pirate radio, JACK IN.
	var right := VBoxContainer.new()
	right.add_theme_constant_override("separation", 10)
	var poster := HeatPoster.new(true)
	poster.hot_color = Palette.corp_color(c.corporation_id)
	poster.set_heat(c.heat, cfg.heat_max, cfg.major_heat_levels())
	poster.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	poster.tooltip_text = heat_tip()
	var lead := selected_op()
	if lead != null:
		poster.wanted = PortraitArt.operative_subject(lead.class_id, lead.id, lead.name)
	var radio := ZineNote.new("PIRATE RADIO", Vector2(230, 96))
	var dj_line := Dialogue.line("dj", RC.Voice.NARRATOR, c.corporation_id, &"", c.runs_started + c.runs_completed * 7)
	radio.append(dj_line.text if dj_line != null else "lo-fi loop: HQ")
	radio.append("vs %s | ICE %d%s" % [RunManager.corporation.display_name, c.ice_level, " | ASSIST" if c.is_assisted() else ""])
	var code := CampaignCode.of(c, c.start_class_id)
	radio.append("Code: %s%s" % [code, " (local: REBEL_CELL is built from your profile)" if RunManager.corporation.generated_from_profile else ""])
	radio.tooltip_text = dj_line.text if dj_line != null else ""
	radio.label.scroll_following = false
	# No key hint: JACK IN is pressed by click or focus (Space does nothing here).
	var jack := ZineStamp.new("JACK IN", Palette.CELL_PINK)
	jack.name = "JackIn"
	jack.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	jack.tooltip_text = "Open the City Grid: pick a Site and launch a netrun."
	jack.pressed.connect(show_grid)
	var top_right := HBoxContainer.new()
	top_right.add_theme_constant_override("separation", 10)
	top_right.add_child(poster)
	top_right.add_child(jack)
	right.add_child(top_right)
	right.add_child(radio)
	var left := VBoxContainer.new()
	left.add_theme_constant_override("separation", 12)
	left.custom_minimum_size.x = 300
	cols.add_child(left)
	# The deck menu (reference: "> OPERATIVES / NETWORK / LOADOUT").
	var deck := TerminalWindow.new("CYBERDECK")
	left.add_child(deck)
	var actions := deck.body
	_add_tip(actions, _button("City Grid", show_grid), "The campaign map: pick a Site, launch runs, claim and upgrade nodes.")
	if not c.pending_raids.is_empty():
		var raid := CampaignRules.raid_data(c.pending_raids[0], lookup)
		var raid_btn := _button("RAID PENDING: %s (%d)" % [raid.display_name, c.pending_raids.size()], show_raid)
		raid_btn.add_theme_color_override("font_color", Palette.CELL_PINK)
		_add_tip(actions, raid_btn, raid.warning_text)
	var scrub := HeatRules.scaled_delta(c, -cfg.heat_purchase_amount, cfg)
	_add_tip(actions, _button("Scrub Heat %d (%d)" % [scrub, CampaignRules.heat_purchase_price(c, cfg)], buy_heat_reduction),
		"Pay %d Schematics to change Heat by %d." % [CampaignRules.heat_purchase_price(c, cfg), scrub])
	if c.grid.home_integrity < c.grid.home_max_integrity:
		_add_tip(actions, _button("Patch home +%d (%d)" % [c.grid.home_max_integrity - c.grid.home_integrity, CampaignRules.home_repair_price(c, cfg)], repair_home),
			"Repair the home server to full integrity.")
	_add_tip(actions, _button("Codex", show_codex), "Everything the Cell knows: slices, cards, Firmware, Daemons, rules.")
	var settings_btn := _hint_button("Settings", &"open_settings", open_settings)
	settings_btn.name = "SettingsButton"
	actions.add_child(settings_btn)
	_add_tip(actions, _button("Save", func() -> void: RunManager.autosave(); _log.append_text("Saved.\n"); notify("Saved.")), "Save the campaign now (it also saves after every action).")
	_as_menu(actions)
	# The Cell at a glance (H20: badges, not a text readout): home, Exploits, Armory and the
	# rules the Heat thresholds added; each badge's tooltip says what it means.
	var status := TerminalWindow.new("CELL STATUS")
	status.name = "CellStatus"
	left.add_child(status)
	status.body.add_child(cell_badges())
	# The crew: Polaroids with their stats and orders.
	# The deck monitor: the City Grid at a glance (click or JACK IN to open it).
	var monitor := TerminalWindow.new("CITY GRID // %s" % RunManager.corporation.display_name)
	monitor.tag_label.text = "STATUS: %s" % ("RAID INBOUND" if not c.pending_raids.is_empty() else "STABLE")
	monitor.tag_label.add_theme_color_override("font_color", Palette.CELL_PINK if not c.pending_raids.is_empty() else Palette.CELL_ACID)
	monitor.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var center := VBoxContainer.new()
	center.add_theme_constant_override("separation", 12)
	center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	cols.add_child(center)
	center.add_child(monitor)
	var mini := GridMapView.new()
	mini.custom_minimum_size = Vector2(420, 170)
	mini.show_grid(c, RunManager.corporation, _threat_paths())
	mini.site_clicked.connect(func(id: StringName) -> void: selected_site = id; show_grid())
	mini.tooltip_text = "Click a Site to open it on the City Grid."
	monitor.body.add_child(mini)
	cols.add_child(right)
	var crew := TerminalWindow.new("CREW // ROSTER", Palette.CELL_PINK)
	crew.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var roster_box := HFlowContainer.new()
	roster_box.add_theme_constant_override("h_separation", 18)
	roster_box.add_theme_constant_override("v_separation", 14)
	crew.body.add_child(roster_box)
	for op in c.roster:
		# A crew dossier: Polaroid, name, tags, HP, kit, then orders.
		var where := CampaignRules.stationed_site(c, op.id)
		var cls_data := lookup.get_content(op.class_id) as ClassData
		var row := CrewCard.new(op.name, cls_data.display_name if cls_data != null else String(op.class_id), op.rank, op.hp, op.max_hp,
			"HP %d/%d · DECK %d · DAEMONS %d%s" % [op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size(),
			"" if op.alive else " · [DEAD]"], -1.5 if c.roster.find(op) % 2 == 0 else 1.5)
		row.name = "Crew_%s" % op.id
		row.set_operative(op.class_id, op.id)
		row.tooltip_text = UiTip.fold("%s%s" % [cls_data.description if cls_data != null else "", ("\nStationed on %s." % site_name(where)) if where != &"" else ""])
		row.polaroid.glitch = not op.alive or op.hp * 4 <= op.max_hp
		row.dead = not op.alive
		if where != &"" and op.alive:
			row.stamp_text = "ON %s" % site_name(where).to_upper()
		var orders := row.orders
		if op.alive:
			var view_row := HBoxContainer.new()
			var op_ref := op
			var loadout_btn := _button("Loadout", func() -> void: open_loadout(op_ref))
			loadout_btn.name = "Loadout"
			loadout_btn.tooltip_text = "%s's deck, spinner, hub core and inner ring. VIEW LOADOUT and DAEMONS in the top bar follow them." % op.name
			view_row.add_child(loadout_btn)
			orders.add_child(view_row)
			if where != &"":
				var id := op.id
				_add_tip(orders, _button("Recall", func() -> void: recall(id)), "Bring %s back from %s." % [op.name, site_name(where)])
			else:
				for site_id in c.grid.claimed_ids():
					var node := lookup.get_content(c.grid.node_type_of(site_id)) as NetworkNodeData
					if node != null and node.station_slots > 0 and c.grid.stationed_on(site_id) == &"" and c.grid.is_active_node(site_id):
						var oid := op.id
						var sid := site_id
						_add_tip(orders, _button("Station on %s" % site_name(site_id), func() -> void: station(oid, sid)),
							"%s guards %s (%s): the class's station bonus helps it hold in raids." % [op.name, site_name(site_id), node.display_name])
			# Rank 3 Inner Ring segment swaps (GDD 6.4).
			var cls := lookup.get_content(op.class_id) as ClassData
			var options := CampaignRules.ring_segment_options(op, cls)
			if not options.is_empty():
				for k in RC.RING_SEGMENTS:
					var pick := OptionButton.new()
					pick.add_item("seg %d: default" % k)
					pick.set_item_metadata(0, &"")
					var current: StringName = op.ring_segment_ids[k] if k < op.ring_segment_ids.size() else &""
					for i in options.size():
						var seg := lookup.get_content(options[i]) as RingSegmentData
						pick.add_item("seg %d: %s" % [k, seg.display_name if seg != null else String(options[i])])
						pick.set_item_metadata(i + 1, options[i])
						if options[i] == current:
							pick.select(i + 1)
					var oid2 := op.id
					var index := k
					pick.item_selected.connect(func(i: int) -> void: swap_segment(oid2, index, pick.get_item_metadata(i)))
					pick.tooltip_text = "Inner ring segment %d: Rank 3 lets you swap it for another." % k
					orders.add_child(pick)
		roster_box.add_child(row)
	center.add_child(crew)
	# The market: recruits, next-run boosts (GDD 11.4) and Profile unlocks (GDD 3.4).
	var market := TerminalWindow.new("BLACK MARKET // SCHEMATICS %d" % c.schematics, Palette.CELL_ACID)
	box.add_child(market)
	var recruits := HFlowContainer.new()
	recruits.add_child(_label("Recruit:"))
	for cls in RunManager.available_classes():
		var cid := cls.id
		_add_tip(recruits, _button("Recruit %s (%d)" % [cls.display_name, CampaignRules.rookie_price(c, cfg)], func() -> void: recruit(cid)), cls.description)
	market.body.add_child(recruits)
	var boosts := HFlowContainer.new()
	boosts.add_child(_label("Next-run boosts:"))
	for b in cfg.netrun_boosts:
		if b == null:
			continue
		var bid := b.id
		var btn := _button("%s (%d)" % [b.display_name, b.cost], func() -> void: buy_boost(bid))
		btn.tooltip_text = UiTip.fold(b.description)
		btn.disabled = c.pending_boosts.has(b.id) or c.schematics < b.cost
		boosts.add_child(btn)
	if not c.pending_boosts.is_empty():
		var queued := PackedStringArray()
		for bid in c.pending_boosts:
			for b in cfg.netrun_boosts:
				if b != null and b.id == bid:
					queued.append(b.display_name)
		boosts.add_child(_label("queued: %s" % ", ".join(queued)))
	market.body.add_child(boosts)
	var unlocks := HFlowContainer.new()
	unlocks.add_child(_label("Profile unlocks:"))
	var any_unlock := false
	for id in lookup.ids_of_class(&"ProfileUnlockData"):
		var u := lookup.get_content(id) as ProfileUnlockData
		if u == null or RunManager.profile.has_unlock(u.id):
			continue
		# Free unlocks (REBEL_CELL) open by themselves once their requirements are met.
		if u.schematic_cost == 0:
			continue
		any_unlock = true
		var uid := u.id
		var btn := _button("%s (%d)" % [u.display_name, u.schematic_cost], func() -> void: purchase_unlock(uid))
		btn.tooltip_text = UiTip.fold(u.description)
		btn.disabled = c.schematics < u.schematic_cost
		unlocks.add_child(btn)
	if not any_unlock:
		unlocks.add_child(_label("everything unlocked"))
	market.body.add_child(unlocks)
	var beats := CampaignRules.revealed_beats(c, RunManager.corporation)
	if not beats.is_empty():
		var story := TerminalWindow.new("Story so far:", Palette.CRT_AMBER)
		box.add_child(story)
		for b in beats:
			var t := RichTextLabel.new()
			t.fit_content = true
			t.custom_minimum_size = Vector2(700, 0)
			t.text = "  [%s] %s" % [b.title, b.text]
			story.body.add_child(t)
	_set_panel(box, "hq")


## Node types the player can install, in id order (home cores excluded); locked ones
## are listed but disabled.
func _node_choices() -> Array[NetworkNodeData]:
	var out: Array[NetworkNodeData] = []
	for id in RunManager.lookup().ids_of_class(&"NetworkNodeData"):
		var node := RunManager.lookup().get_content(id) as NetworkNodeData
		if node != null and node.node_type != RC.NetworkNodeType.HOME_SERVER and node.install_cost > 0:
			out.append(node)
	return out


func show_grid() -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	# The Grid lives on the city (M3: the rest of the city greyed out); the side column
	# holds the plan, the legend and the Site list. `grid_view` stays as the (hidden)
	# summary map model: its clicks and selection mirror the city map's.
	var outer := HBoxContainer.new()
	outer.add_theme_constant_override("separation", 0)
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	outer.add_child(spacer)
	grid_view = GridMapView.new()
	grid_view.visible = false
	grid_view.show_grid(c, corp, _threat_paths())
	grid_view.selected_id = selected_site
	grid_view.site_clicked.connect(select_site)
	outer.add_child(grid_view)
	var side := VBoxContainer.new()
	side.name = "GridSide"
	side.custom_minimum_size.x = GRID_SIDE_WIDTH
	side.add_theme_constant_override("separation", 10)
	outer.add_child(side)
	# H20: no plan note or Site list; the map carries status and objectives, the side
	# column holds the picked Site's card with its actions, the runs open now, the legend.
	var launchable := RunManager.launchable_sites()
	launchable.append_array(RunManager.patrol_sites())
	if (selected_site == &"" or CampaignRules.site_data(corp, selected_site) == null) and not launchable.is_empty():
		selected_site = launchable[0].id
	if selected_site == &"" or CampaignRules.site_data(corp, selected_site) == null:
		selected_site = c.grid.home_site_id
	# A 2-column grid, not an HBox: the pad links the card's own action row (UiFocus).
	var top := GridContainer.new()
	top.columns = 2
	top.add_theme_constant_override("h_separation", 10)
	side.add_child(top)
	var site := CampaignRules.site_data(corp, selected_site)
	if site != null:
		var card := _site_card(site, launchable, c.living_operatives(), _node_choices())
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		card.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		top.add_child(card)
	var legend := MapLegend.new(c.corporation_id)
	top.add_child(legend)
	# Every Site stays reachable without the mouse: step through them, or jump to a run.
	# First in the column: the city screens don't scroll by mouse wheel, so Back to HQ
	# must stay on screen at text scale 1.6.
	var nav := HBoxContainer.new()
	nav.name = "SiteNav"
	nav.add_theme_constant_override("separation", 8)
	side.add_child(nav)
	side.move_child(nav, 0)
	var prev := _button("< PREV SITE", func() -> void: step_site(-1))
	prev.name = "PrevSite"
	_add_tip(nav, prev, "Select the previous Site on the Grid (the map follows).")
	var next := _button("NEXT SITE >", func() -> void: step_site(1))
	next.name = "NextSite"
	_add_tip(nav, next, "Select the next Site on the Grid (the map follows).")
	var back := _button("Back to HQ", show_hq)
	back.name = "BackToHq"
	nav.add_child(back)
	if not c.pending_raids.is_empty():
		var raid_btn := _button("RAID SETUP", show_raid)
		raid_btn.theme_type_variation = &"HotButton"
		_add_tip(nav, raid_btn, "A raid is coming along the dashed routes: set up the defence.")
	if not launchable.is_empty():
		var runs := TerminalWindow.new("RUNS OPEN NOW", Palette.CELL_ACID)
		runs.name = "RunsOpen"
		side.add_child(runs)
		var flow := HFlowContainer.new()
		flow.add_theme_constant_override("h_separation", 8)
		flow.add_theme_constant_override("v_separation", 6)
		runs.body.add_child(flow)
		for s in launchable:
			var sid := s.id
			var b := _button("%s %s" % [_site_glyph(s), site_name(s.id)], func() -> void: select_site(sid))
			b.name = "Run_%s" % s.id
			if s.id == selected_site:
				b.add_theme_color_override("font_color", Palette.CELL_ACID)
			_add_tip(flow, b, "T%d %s: %s. Select it to launch." % [s.tier, site_name(s.id), CampaignRules.run_kind_for(c, s)])
	_set_panel(outer, "grid")
	UiFocus.link_layout(side)  # the side column row by row (nav, card actions, runs)
	var g := grid_graph()
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.4, 0.56), 0.85)
	city_overlay.selected_id = selected_site
	city_overlay.node_clicked.connect(func(id: StringName) -> void: grid_view.site_clicked.emit(id))


## Mounts the map overlay on the net city and frames the camera on it. `zoom` > 1 moves
## the camera in; `focus` (grid) overrides the graph's centre.
func _mount_city_map(nodes: Array[Dictionary], edges: Array[Dictionary], look: int, anchor: Vector2, zoom: float = 1.0, focus: Vector2 = Vector2.INF) -> void:
	_clear_city_map()
	var city := wireframe.city
	city_overlay = CityMapOverlay.new(city)
	city.add_child(city_overlay)
	city_overlay.set_look(look)
	city_overlay.set_graph(nodes, edges)
	_frame_city(zoom, city_overlay.centre() if focus == Vector2.INF else focus, anchor)


## Camera on the net city: zoom and put grid point `focus` at screen fraction `anchor`.
func _frame_city(zoom: float, focus: Vector2, anchor: Vector2) -> void:
	var city := wireframe.city
	city.scale = Vector2(zoom, zoom)
	city.offset_left = 0
	city.offset_top = 0
	city.offset_right = size.x / zoom - size.x
	city.offset_bottom = size.y / zoom - size.y
	city.focus_grid = focus
	city.focus_anchor = anchor
	city.refresh()


func _clear_city_map() -> void:
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.queue_free()
	city_overlay = null
	var city := wireframe.city
	if city.focus_grid != Vector2.INF or city.scale != Vector2.ONE:
		city.focus_grid = Vector2.INF
		city.scale = Vector2.ONE
		city.offset_right = 0
		city.offset_bottom = 0
		city.refresh()


## The campaign's Grid as a graph for the city overlay (CityLayout.grid_graph).
func grid_graph() -> Dictionary:
	return CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, _threat_paths(), selected_site)


## Pending raids' routes, entry -> home, for the map's corporate arrows.
func _threat_paths() -> Array[Array]:
	return CityLayout.threat_paths(RunManager.campaign, RunManager.corporation)


## Selects a Site clicked on the Grid map and redraws the Grid with its actions first.
func select_site(site_id: StringName) -> void:
	selected_site = site_id
	show_grid()


## Selects the Site `step` places after the selected one in the Grid's order (wraps), so a
## pad reaches every Site without the map (H20).
func step_site(step: int) -> void:
	var sites := RunManager.corporation.city_grid.sites.filter(func(s: SiteData) -> bool: return s != null)
	if sites.is_empty():
		return
	var i := 0
	for k in sites.size():
		if sites[k].id == selected_site:
			i = k
	select_site(sites[posmod(i + step, sites.size())].id)


## The glyph the map puts on a Site (objective, tier, CORE).
func _site_glyph(site: SiteData) -> String:
	var c := RunManager.campaign
	if site.id == c.grid.home_site_id:
		return GLYPH_HOME
	match CampaignRules.site_objective(c, site):
		RC.SiteObjective.EXPLOIT:
			return GLYPH_EXPLOIT
		RC.SiteObjective.HEAT_REDUCTION:
			return GLYPH_HEAT
		RC.SiteObjective.BOSS:
			return GLYPH_BOSS
	return "T%d" % site.tier


## The picked Site as a card (H20, replacing the Site list): its facts as badges (status,
## objective, node and integrity, upgrades, assets, station) and the actions it allows now
## (launch, claim, repair, upgrade). Named "SelectedSite".
func _site_card(site: SiteData, launchable: Array[SiteData], living: Array[OperativeState], choices: Array[NetworkNodeData]) -> TerminalWindow:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var s := c.grid.site(site.id)
	var status := int(s["status"])
	var accent := Palette.CELL_PINK if status == GridState.SiteStatus.CLAIMED else (Palette.NET_CYAN if status == GridState.SiteStatus.CLEARED else Palette.corp_color(c.corporation_id))
	var card := TerminalWindow.new(site_name(site.id), accent)
	card.name = "SelectedSite"
	card.tag_label.text = "T%d // %s" % [site.tier, String(STATUS_NAMES.get(status, "?")).to_upper()]
	var facts := HFlowContainer.new()
	facts.name = "SiteFacts"
	facts.add_theme_constant_override("h_separation", 10)
	facts.add_theme_constant_override("v_separation", 4)
	card.body.add_child(facts)
	facts.add_child(Badge.new(String(STATUS_NAMES.get(status, "?")), accent, _site_glyph(site), STATUS_TIPS.get(status, "")))
	var objective := CampaignRules.site_objective(c, site)
	if objective == RC.SiteObjective.EXPLOIT:
		var ename: String = RC.ExploitType.keys()[site.exploit_type]
		facts.add_child(Badge.new(ename.capitalize(), Palette.CELL_ACID, GLYPH_EXPLOIT, "Clear this Site for the %s Exploit (%d/%d for the breach)." % [ename.capitalize(), c.exploits.size(), cfg.min_exploits_for_breach]))
	elif objective == RC.SiteObjective.HEAT_REDUCTION:
		var dh := HeatRules.scaled_delta(c, site.heat_change, cfg)
		facts.add_child(Badge.new("Heat %+d" % dh, Palette.NET_CYAN, GLYPH_HEAT, "Clearing this Site changes Heat by %d." % dh))
	elif objective == RC.SiteObjective.BOSS:
		facts.add_child(Badge.new("BOSS", Palette.corp_color(c.corporation_id), GLYPH_BOSS, "The corporation's core. The breach needs %d Exploits." % cfg.min_exploits_for_breach))
	elif site.objective == RC.SiteObjective.HEAT_REDUCTION:
		facts.add_child(Badge.new("off", Color(Palette.NET_CYAN, 0.6), GLYPH_HEAT, "This Site's Heat objective is switched off at this ICE level."))
	if c.grid.is_claimed(site.id):
		var node_col := Palette.CELL_PINK if int(s["condition"]) != GridState.Condition.DISABLED else Palette.RESIST_GOLD
		var node_text := "%s %d/%d" % [_display(c.grid.node_type_of(site.id)), int(s["integrity"]), int(s["max_integrity"])]
		if int(s["condition"]) == GridState.Condition.DISABLED:
			node_text += " DISABLED"
		var node_data := lookup.get_content(c.grid.node_type_of(site.id)) as NetworkNodeData
		facts.add_child(Badge.new(node_text, node_col, GLYPH_NODE, node_data.description if node_data != null else "").with_meter(int(s["integrity"]), int(s["max_integrity"])))
		if c.grid.upgrade_level_of(site.id) > 0:
			facts.add_child(Badge.new("+%d" % c.grid.upgrade_level_of(site.id), Palette.CELL_ACID, GLYPH_UPGRADE, "Node upgrade level %d." % c.grid.upgrade_level_of(site.id)))
		for aid in c.grid.assets_on(site.id):
			var data := lookup.get_content(aid) as DefenseAssetData
			facts.add_child(Badge.new(_display(aid), Palette.CELL_PINK, "", data.description if data != null else "", aid))
		var guard := c.grid.stationed_on(site.id)
		if guard != &"":
			var guard_op := c.get_operative(guard)
			facts.add_child(Badge.new(guard_op.name if guard_op != null else "guarded", Palette.PAPER, GLYPH_GUARD, "An operative is stationed here: their class's station bonus helps the node in raids."))
	var row := HFlowContainer.new()
	row.name = "SiteActions"
	row.add_theme_constant_override("h_separation", 8)
	card.body.add_child(row)
	var launchable_here := false
	for l in launchable:
		if l.id == site.id:
			launchable_here = true
	if launchable_here and not living.is_empty():
		var op_pick := OptionButton.new()
		op_pick.name = "OperativePick"
		for op in living:
			var post := CampaignRules.stationed_site(c, op.id)
			op_pick.add_item("%s R%d%s" % [op.name, op.rank, (" (leaves %s)" % site_name(post)) if post != &"" else ""])
		op_pick.tooltip_text = "Who runs it."
		row.add_child(op_pick)
		var sid := site.id
		var kind := CampaignRules.run_kind_for(c, site)
		var go := _button("Launch %s" % kind, func() -> void: launch(sid, living[op_pick.selected].id))
		go.name = "Launch"
		go.theme_type_variation = &"HotButton"
		_add_tip(row, go, "Jack into %s: a %s netrun." % [site_name(site.id), kind])
	if c.grid.is_cleared(site.id) and site.claimable:
		var node_pick := OptionButton.new()
		node_pick.name = "NodePick"
		for i in choices.size():
			var node := choices[i]
			var available := CampaignRules.node_available(RunManager.profile, lookup, node)
			node_pick.add_item("%s (%d)%s" % [node.display_name, node.install_cost, "" if available else " [locked]"])
			node_pick.set_item_disabled(i, not available)
			node_pick.set_item_tooltip(i, UiTip.fold(node.description))
		row.add_child(node_pick)
		var sid2 := site.id
		_add_tip(row, _button("Claim", func() -> void: claim(sid2, choices[node_pick.selected].id)), "Build the picked node here: it joins your network and defends in raids.")
	if c.grid.is_claimed(site.id) and int(s["condition"]) == GridState.Condition.DISABLED:
		var sid3 := site.id
		_add_tip(row, _button("Repair (%d)" % CampaignRules.repair_cost(c, cfg, lookup, sid3), func() -> void: repair(sid3)), "Bring the disabled node back online.")
	if c.grid.is_active_node(site.id) and site.id != c.grid.home_site_id:
		var cost := CampaignRules.upgrade_cost(c, cfg, site.id)
		if cost >= 0:
			var sid4 := site.id
			_add_tip(row, _button("Upgrade (%d)" % cost, func() -> void: upgrade(sid4)), "Upgrade the node one level (level %d now)." % c.grid.upgrade_level_of(site.id))
	return card


func show_raid() -> void:
	var c := RunManager.campaign
	var pending := RunManager.pending_raid()
	if pending.is_empty():
		show_hq()
		return
	var lookup := RunManager.lookup()
	var cfg := RunManager.config()
	var raid := CampaignRules.raid_data(pending, lookup)
	var projection := RunManager.project_raid()
	var claimed := c.grid.claimed_ids()
	if not claimed.has(selected_site):
		selected_site = claimed[claimed.size() - 1] if not claimed.is_empty() else &""
	# Raid setup on the city (rest of the city greyed out): the network and the threat
	# routes on real streets, each node's projected outcome on the map; the raid card, the
	# node orders and the Armory in the side column and below (H20: no text wall).
	var outer := VBoxContainer.new()
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var top := HBoxContainer.new()
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.size_flags_vertical = Control.SIZE_EXPAND_FILL
	outer.add_child(top)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(spacer)
	MapLegend.pin_to(spacer, c.corporation_id)  # the raid map has its key too (H20 #22)
	var side := VBoxContainer.new()
	side.name = "RaidSide"
	side.custom_minimum_size.x = RAID_SIDE_WIDTH
	side.add_theme_constant_override("separation", 8)
	top.add_child(side)
	side.add_child(_raid_card(raid, pending, projection))
	var orders_win := TerminalWindow.new("YOUR NODES // pick the target", Palette.CELL_PINK)
	orders_win.name = "NodeOrders"
	side.add_child(orders_win)
	# A fixed-height list (many claimed nodes scroll inside it; follow_focus for the pad).
	var orders_scroll := ScrollContainer.new()
	orders_scroll.custom_minimum_size = Vector2(0, ORDERS_HEIGHT)
	orders_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	orders_scroll.follow_focus = true
	orders_win.body.add_child(orders_scroll)
	var orders := VBoxContainer.new()
	orders.name = "Orders"
	orders.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	orders.add_theme_constant_override("separation", 4)
	orders_scroll.add_child(orders)
	for site_id in claimed:
		orders.add_child(_node_order_row(site_id, projection, claimed))
	var go := HBoxContainer.new()
	go.add_theme_constant_override("separation", 10)
	side.add_child(go)
	var run_btn := _button("RUN THE RAID", fight_raid)
	run_btn.name = "RunRaid"
	run_btn.theme_type_variation = &"HotButton"
	_add_tip(go, run_btn, "Play the raid out on the map; the result matches the projection.")
	go.add_child(_button("Back to HQ", show_hq))
	var loadout := TerminalWindow.new("DEFENSE LOADOUT // ARMORY %d/%d // pick a node, then a card" % [c.armory.size(), cfg.armory_capacity], Palette.CELL_PINK)
	loadout.tag_label.text = "TARGET: %s" % site_name(selected_site)
	outer.add_child(loadout)
	var cards := HFlowContainer.new()
	cards.name = "AssetCards"
	cards.add_theme_constant_override("h_separation", 14)
	loadout.body.add_child(cards)
	var seen := {}
	for i in c.armory.size():
		var aid: StringName = c.armory[i]
		if seen.has(aid):
			continue
		seen[aid] = true
		var data := lookup.get_content(aid) as DefenseAssetData
		var card := AssetCard.new(aid, data.display_name if data != null else String(aid), data.integrity if data != null else 0, c.armory.count(aid))
		card.custom_minimum_size = Vector2(110, 120)
		card.tooltip_text = UiTip.fold("%s\nDeploys to %s." % [data.description if data != null else "", site_name(selected_site)])
		card.disabled = selected_site == &"" or not c.grid.is_active_node(selected_site)
		var index := i
		card.pressed.connect(func() -> void: deploy_asset(index, selected_site))
		cards.add_child(card)
	if c.armory.is_empty():
		cards.add_child(_label("Armory empty: runs bank assets from their drops."))
	_set_panel(outer, "raid")
	var g := raid_graph(projection, {})
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.36, 0.42))
	city_overlay.selected_id = selected_site
	city_overlay.node_clicked.connect(func(id: StringName) -> void:
		if RunManager.campaign.grid.is_claimed(id):
			select_target(id))
	if _last_warned_raid != String(pending.get("raid_id", "")):
		_last_warned_raid = String(pending.get("raid_id", ""))
		Dialogue.raid_warning(c.corporation_id, StringName(String(pending.get("raid_id", raid.id))), c.raids_won + c.raids_lost)


## Makes claimed node `site_id` the raid setup's target (map click, or its target button
## in the node orders for the pad and keyboard; H20).
func select_target(site_id: StringName) -> void:
	selected_site = site_id
	show_raid()
	var b := _panel.find_child("Target_%s" % site_id, true, false) as Control if _panel != null else null
	if b != null:
		b.grab_focus.call_deferred()


## The raid at a glance: the projected result as a stamp, then badges for home before and
## after, threats destroyed, strength, steps, the entry Sites and the link changes; the
## raid's warning in the tooltip.
func _raid_card(raid: RaidData, pending: Dictionary, projection: RaidResolver.RaidResult) -> TerminalWindow:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var corp_col := Palette.corp_color(c.corporation_id)
	var card := TerminalWindow.new("RAID // %s" % raid.display_name, corp_col)
	card.name = "RaidCard"
	card.tooltip_text = UiTip.fold(raid.warning_text)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	card.body.add_child(row)
	var verdict := "HOLDS" if projection.won else ("LOST" if projection.campaign_lost else "BREACHED")
	var stamp := ZineStamp.new(verdict, Palette.CELL_ACID if projection.won else Palette.CELL_PINK).display_only()
	stamp.name = "Projection"
	stamp.custom_minimum_size = Vector2(PROJECTION_STAMP, PROJECTION_STAMP)
	row.add_child(stamp)
	var facts := HFlowContainer.new()
	facts.name = "RaidFacts"
	facts.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	facts.add_theme_constant_override("h_separation", 10)
	facts.add_theme_constant_override("v_separation", 4)
	row.add_child(facts)
	var home_col := Palette.CELL_ACID if projection.home_after >= projection.home_before else Palette.CELL_PINK
	facts.add_child(Badge.new("%d > %d" % [projection.home_before, projection.home_after], home_col, GLYPH_HOME,
		"Projected home integrity after the raid (exact: the playout matches it).").with_meter(projection.home_after, c.grid.home_max_integrity))
	var total := projection.threats_destroyed + projection.threats_reached_home + _still_active(projection)
	facts.add_child(Badge.new("%d/%d" % [projection.threats_destroyed, total], Palette.CELL_ACID, GLYPH_THREAT, "Threats your nodes destroy, of all that come."))
	facts.add_child(Badge.new("%+.0f%%" % CampaignRules.raid_strength_pct(c, cfg, pending, RunManager.corporation), corp_col, GLYPH_RULE, "Threat strength from Heat, ICE and seized Sites."))
	# Entry Sites: a badge each for a few, else one count (names in its tooltip); the
	# dashed routes on the map show them all.
	var entries := PackedStringArray()
	for e in CampaignRules.raid_entries(c, RunManager.corporation, pending):
		entries.append(site_name(e))
	if entries.size() <= MAX_ENTRY_BADGES:
		for entry in entries:
			facts.add_child(Badge.new(entry, corp_col, GLYPH_ENTRY, "Threats come in at %s (the dashed routes on the map)." % entry))
	else:
		facts.add_child(Badge.new("%d entries" % entries.size(), corp_col, GLYPH_ENTRY, "Threats come in at: %s (the dashed routes on the map)." % ", ".join(entries)))
	for e in projection.events:
		if e.get("type", "") in ["link_frozen", "link_altered"]:
			facts.add_child(Badge.new("link", Palette.RESIST_GOLD, GLYPH_LINK, String(e["text"])))
	return card


## One claimed node in the raid orders: its target button (name, node type) and its
## projected outcome and assets as badges; the target's row also carries the withdraw and
## move buttons for its assets.
func _node_order_row(site_id: StringName, projection: RaidResolver.RaidResult, claimed: Array[StringName]) -> Control:
	var c := RunManager.campaign
	var n: Dictionary = projection.nodes.get(String(site_id), {})
	var holds := String(n.get("outcome", "")) == "holds"
	var box := VBoxContainer.new()
	box.name = "Order_%s" % site_id
	var row := HFlowContainer.new()
	row.add_theme_constant_override("h_separation", 8)
	box.add_child(row)
	var picked := site_id == selected_site
	var target := _button(("> %s" if picked else "%s") % site_name(site_id), func() -> void: select_target(site_id))
	target.name = "Target_%s" % site_id
	target.custom_minimum_size.x = TARGET_BUTTON_WIDTH
	target.alignment = HORIZONTAL_ALIGNMENT_LEFT
	if picked:
		target.add_theme_color_override("font_color", Palette.CELL_ACID)
	target.disabled = not c.grid.is_active_node(site_id)
	_add_tip(row, target, "%s (%s): make it the target for the Armory's assets." % [site_name(site_id), _display(c.grid.node_type_of(site_id))])
	if not n.is_empty():
		row.add_child(Badge.new("%s > %s %s" % [n.get("before", "?"), n.get("after", "?"), String(n.get("outcome", "?")).to_upper()],
			Palette.CELL_ACID if holds else Palette.CELL_PINK, GLYPH_NODE, "Projected integrity before and after the raid, and whether the node holds."))
	var assets := c.grid.assets_on(site_id)
	for aid in assets:
		row.add_child(Badge.new("", Palette.CELL_PINK, "", _display(aid), aid))
	if picked:
		var moves := HFlowContainer.new()
		moves.name = "Moves"
		moves.add_theme_constant_override("h_separation", 6)
		box.add_child(moves)
		for i in assets.size():
			var idx := i
			_add_tip(moves, _button("Withdraw %s" % _display(assets[i]), func() -> void: move_asset(site_id, idx, &"")), "Back to the Armory.")
			for other in claimed:
				if other != site_id and c.grid.is_active_node(other):
					var oid := other
					_add_tip(moves, _button("%s > %s" % [_display(assets[i]), site_name(other)], func() -> void: move_asset(site_id, idx, oid)), "Move it to %s." % site_name(other))
	return box
## The raid's part of the Grid as an overlay graph: claimed nodes (coloured by `results`
## outcome, with their assets), the Sites on the threat routes, links among them.
func raid_graph(results: Variant, markers: Dictionary) -> Dictionary:
	var c := RunManager.campaign
	var g := grid_graph()
	var nodes_res: Dictionary = results.nodes if results is RaidResolver.RaidResult else results
	var network := {}
	for id in c.grid.claimed_ids():
		network[id] = true
	for path in _threat_paths():
		for id in path:
			network[id] = true
	for id in markers:
		network[id] = true
	var nodes: Array[Dictionary] = []
	for n in g["nodes"]:
		if not network.has(n["id"]):
			continue
		var res: Dictionary = nodes_res.get(String(n["id"]), {})
		if not res.is_empty():
			n["color"] = Palette.CELL_ACID if String(res["outcome"]) == "holds" else Palette.CELL_PINK
			n["result"] = "%s > %s %s" % [res["before"], res["after"], String(res["outcome"]).to_upper()]
			n["label"] = site_name(n["id"])  # never the raw id (H20)
		n["assets"] = c.grid.assets_on(n["id"])
		n["threat_corp"] = String(c.corporation_id)
		nodes.append(n)
	var edges: Array[Dictionary] = []
	for e in g["edges"]:
		if network.has(e["a"]) and network.has(e["b"]):
			edges.append(e)
	return {"nodes": nodes, "edges": edges}


## Codex (GDD 8.1): everything the Cell knows, zine-styled, plus the lexicon.
func show_codex() -> void:
	var box := VBoxContainer.new()
	box.add_child(GraffitiTag.new("CODEX"))
	var entries := Codex.entries(RunManager.lookup(), RunManager.profile)
	var tabs := HFlowContainer.new()
	box.add_child(tabs)
	var body := ZineNote.new("", Vector2(900, 380)).make_reference()
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for section in entries:
		var name: String = section
		tabs.add_child(_button(name, func() -> void: _fill_codex(body, name, entries[name])))
	box.add_child(body)
	_fill_codex(body, "Slices", entries["Slices"])
	if not Dialogue.history.is_empty():
		var lines := ZineNote.new("LINES HEARD", Vector2(900, 100)).make_reference()
		for h in Dialogue.history.slice(maxi(0, Dialogue.history.size() - 6)):
			lines.append("[%s] %s" % [Dialogue.speaker_name(int(h["speaker"]), StringName(String(h.get("corporation", "")))), h["text"]])
		box.add_child(lines)
	box.add_child(_button("Back to HQ", show_hq if RunManager.campaign != null else show_start))
	_set_panel(box, "codex")


func _fill_codex(body: ZineNote, section: String, items: Array) -> void:
	body.clear()
	body.append("[b]%s[/b]" % section.to_upper())
	for item in items:
		body.append("[b]%s[/b] - %s" % [item["title"], String(item["text"]).replace("\n", " / ")])


## Raid playout (GDD 7.2, 9.3): threat markers animate over the Grid; 1x/2x/4x and skip.
## Instant (straight to the summary) when headless or under reduce-effects.
func show_raid_playout(events: Array[Dictionary]) -> void:
	var c := RunManager.campaign
	# The raid live on the city, the camera zoomed in on the fight and following it; the
	# RAID FEED at the side.
	var box := HBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(spacer)
	MapLegend.pin_to(spacer, c.corporation_id)
	var side := VBoxContainer.new()
	side.add_theme_constant_override("separation", 12)
	box.add_child(side)
	var feed := TerminalWindow.new("RAID FEED // LIVE", Palette.corp_color(c.corporation_id))
	side.add_child(feed)
	var cont := _button("Continue", _after_playout)
	cont.theme_type_variation = &"HotButton"
	cont.disabled = true
	_set_panel(box, "raid_playout")
	var g := raid_graph({}, {})
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.36, 0.55), 1.9)
	var overlay := city_overlay
	overlay.markers_changed.connect(func() -> void: _follow_fight(overlay))
	playout = RaidPlayoutPanel.new(overlay, Vector2(330, 330))
	feed.body.add_child(playout)
	playout.finished.connect(func() -> void:
		cont.disabled = false
		if is_instance_valid(overlay):
			var done := raid_graph(RunManager.campaign.last_raid.get("nodes", {}), overlay.markers)
			overlay.set_graph(done["nodes"], done["edges"]))
	side.add_child(cont)
	var instant := DisplayServer.get_name() == "headless" or not Fx.effects_enabled()
	playout.play(events, instant)
	if instant:
		_after_playout()


## Keeps the zoomed camera on the threats (their first Site, else the network).
func _follow_fight(overlay: CityMapOverlay) -> void:
	if not is_instance_valid(overlay) or overlay != city_overlay:
		return
	var target := overlay.centre()
	for id in overlay.markers:
		target = Vector2(overlay.lot_of(id)) + Vector2(0.5, 0.5)
		break
	_frame_city(1.9, target, Vector2(0.36, 0.55))


func _after_playout() -> void:
	if RunManager.campaign.is_over():
		show_end()
	else:
		show_raid_summary()


func show_raid_summary() -> void:
	var c := RunManager.campaign
	var r := c.last_raid
	var won: bool = r.get("won", false)
	var outer := HBoxContainer.new()
	outer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var table := Control.new()
	table.name = "WarTable"
	table.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	table.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var stamp := ZineStamp.new("REPELLED" if won else "BREACHED", Palette.CELL_ACID if won else Palette.CELL_PINK).display_only()
	stamp.custom_minimum_size = Vector2(150, 150)
	stamp.position = Vector2(20, 16)
	stamp.rotation_degrees = -8.0
	table.add_child(stamp)
	outer.add_child(table)
	MapLegend.pin_to(table, c.corporation_id)
	var report := TerminalWindow.new("RAID REPORT", Palette.CELL_ACID if won else Palette.CELL_PINK)
	report.custom_minimum_size.x = 340
	outer.add_child(report)
	var box := report.body
	# The result as badges (H20): home, threats, then each node's outcome by name.
	var facts := HFlowContainer.new()
	facts.name = "RaidResult"
	facts.add_theme_constant_override("h_separation", 10)
	facts.add_theme_constant_override("v_separation", 4)
	box.add_child(facts)
	facts.add_child(Badge.new("%d > %d" % [int(r.get("home_before", 0)), int(r.get("home_after", 0))], Palette.CELL_ACID if won else Palette.CELL_PINK, GLYPH_HOME,
		"Home integrity before and after the raid.").with_meter(int(r.get("home_after", 0)), c.grid.home_max_integrity))
	facts.add_child(Badge.new("%d destroyed" % int(r.get("threats_destroyed", 0)), Palette.CELL_ACID, GLYPH_THREAT, "Threats your network destroyed."))
	if int(r.get("threats_reached_home", 0)) > 0:
		facts.add_child(Badge.new("%d reached home" % int(r.get("threats_reached_home", 0)), Palette.CELL_PINK, GLYPH_THREAT, "Threats that hit the home server."))
	var ids: Array = r.get("nodes", {}).keys()
	ids.sort()
	for id in ids:
		var n: Dictionary = r["nodes"][id]
		var holds := String(n["outcome"]) == "holds"
		var node_row := HFlowContainer.new()
		node_row.add_child(_label(site_name(StringName(String(id)))))
		node_row.add_child(Badge.new("%d > %d %s" % [int(n["before"]), int(n["after"]), String(n["outcome"]).to_upper()], Palette.CELL_ACID if holds else Palette.CELL_PINK, GLYPH_NODE,
			"Integrity before and after, and whether the node held."))
		box.add_child(node_row)
	for key in ["seized", "disabled"]:
		for id in r.get(key, []):
			box.add_child(Badge.new("%s %s" % [site_name(StringName(String(id))), key.to_upper()], Palette.RESIST_GOLD, GLYPH_RULE,
				"Seized: the corporation took the Site back." if key == "seized" else "Disabled: repair the node on the Grid."))
	box.add_child(_button("Back to HQ", show_hq))
	_set_panel(outer, "raid_summary")
	var g := raid_graph(r.get("nodes", {}), {})
	_mount_city_map(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, Vector2(0.36, 0.55))


func show_end() -> void:
	var c := RunManager.campaign
	Dialogue.speak("win" if c.outcome == CampaignState.Outcome.WON else "loss", RC.Voice.DISPATCH, c.corporation_id, &"", c.campaign_seed)
	var box := VBoxContainer.new()
	box.add_child(_label("CAMPAIGN %s" % (("WON - %s is down" % RunManager.corporation.final_boss.display_name) if c.outcome == CampaignState.Outcome.WON else "LOST - home server destroyed")))
	for b in CampaignRules.revealed_beats(c, RunManager.corporation):
		box.add_child(_label("  [%s] %s" % [b.title, b.text]))
	var p := RunManager.profile
	box.add_child(_para("Profile: %d won / %d lost, best ICE %s; next %s campaign may start up to ICE %d." % [p.campaigns_won, p.campaigns_lost, ProfileState.ice_text(p.best_ice), RunManager.corporation.display_name, RunManager.ice_cap(c.corporation_id)]))
	box.add_child(_para(ice_records_text()))
	box.add_child(_button("New campaign", func() -> void: RunManager.campaign = null; show_start()))
	box.add_child(_button("Back to title", RunManager.go_to_title))
	_set_panel(box, "end")


# --- Helpers ----------------------------------------------------------------------------------

func _still_active(projection: RaidResolver.RaidResult) -> int:
	return projection.seized.size()


func _demo_run(site_id: StringName) -> RunState:
	var r := RunState.new()
	r.site_id = site_id
	return r


func _exploit_names(c: CampaignState) -> String:
	var names := PackedStringArray()
	for e in c.exploits:
		names.append(RC.ExploitType.keys()[e])
	return ", ".join(names) if not names.is_empty() else "none (%d needed for the breach)" % RunManager.config().min_exploits_for_breach


func _refresh_status() -> void:
	var c := RunManager.campaign
	if c == null:
		_status.text = "No campaign."
		return
	var cfg := RunManager.config()
	_status.text = "Heat %d/%d | Schematics %d | Home %d/%d | Exploits %d | Raids pending %d | ICE %d | %s" % [
		c.heat, cfg.heat_max, c.schematics, c.grid.home_integrity, c.grid.home_max_integrity,
		c.exploits.size(), c.pending_raids.size(), c.ice_level, "campaign over" if c.is_over() else "active"]
	hud.set_stats([["HEAT", str(c.heat), "/%d" % cfg.heat_max, heat_tip()],
		["SCHEMATICS", str(c.schematics), "", "Schematics: the campaign's currency. Recruit, claim and upgrade nodes, repair, scrub Heat, buy boosts and Profile unlocks."],
		["HOME", str(c.grid.home_integrity), "/%d" % c.grid.home_max_integrity, "Home server integrity. At 0 the campaign is lost; raids that reach it take it down. Patch it at HQ."],
		["EXPLOITS", str(c.exploits.size()), "/%d" % cfg.min_exploits_for_breach, "Exploits found: %s. The breach on the corporation's core needs %d." % [_exploit_names(c), cfg.min_exploits_for_breach]],
		["RAIDS", str(c.pending_raids.size()), "", "Raids pending against your network. Set up the defence before the next run."],
		["ICE", str(c.ice_level), "", _ice_description(c.ice_level)],
		["CREW", str(c.living_operatives().size()), "", "Living operatives in the Cell."]])
	var op := selected_op()
	hud.loadout_button.visible = op != null
	if op != null:
		hud.set_daemons(op.daemon_ids)


## What the Heat number means now: the next threshold and the rules the crossed ones added.
func heat_tip() -> String:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var next := -1
	for t in cfg.heat_thresholds:
		if t != null and t.heat > c.heat and (next < 0 or t.heat < next):
			next = t.heat
	var lines := PackedStringArray()
	lines.append("Heat %d of %d: how hard the corporation hunts the Cell." % [c.heat, cfg.heat_max])
	if next >= 0:
		lines.append("Next threshold at %d." % next)
	var mods := PackedStringArray()
	for m in HeatRules.active_modifiers(c, cfg):
		mods.append(_modifier_text(m))
	lines.append("In force: %s." % (", ".join(mods) if not mods.is_empty() else "nothing yet"))
	return "\n".join(lines)


## A rule modifier as words ("Raid strength +10%").
static func _modifier_text(m: RuleModifierData) -> String:
	var key: String = RC.RuleModifierType.keys()[m.type]
	var pct := key.ends_with("_PCT")
	return "%s %+.0f%s" % [key.trim_suffix("_PCT").capitalize(), m.value, "%" if pct else ""]


## The operative VIEW LOADOUT and the Daemon tray show: the one picked on a dossier, else
## the first living operative (null when nobody is alive).
func selected_op() -> OperativeState:
	var c := RunManager.campaign
	if c == null:
		return null
	var living := c.living_operatives()
	for op in living:
		if op.id == selected_operative:
			return op
	return living[0] if not living.is_empty() else null


## A Site's name as the Grid shows it (the home server is CORE); never a raw id.
func site_name(site_id: StringName) -> String:
	if site_id == &"":
		return "-"
	var c := RunManager.campaign
	if c != null and c.grid != null and site_id == c.grid.home_site_id:
		return HOME_LABEL
	var sd := CampaignRules.site_data(RunManager.corporation, site_id) if RunManager.corporation != null else null
	return sd.display_name if sd != null else String(site_id)


## A content id's display name (node types, assets, boosts), else the id.
func _display(id: StringName) -> String:
	var res := RunManager.lookup().get_content(id)
	return String(res.get("display_name")) if res != null and res.get("display_name") != null else String(id)


## Adds `control` to `parent` with a wrapped tooltip; returns it.
func _add_tip(parent: Node, control: Control, tip: String) -> Control:
	control.tooltip_text = UiTip.fold(tip)
	parent.add_child(control)
	return control


## The Cell at a glance as badges (the HQ's CELL STATUS; H20 replaces the SYSTEM ONLINE
## text): home integrity with a meter, each Exploit found (or how many the breach needs),
## the Armory's assets by icon and count, and every rule the crossed Heat thresholds add.
func cell_badges() -> HFlowContainer:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var flow := HFlowContainer.new()
	flow.name = "CellBadges"
	flow.add_theme_constant_override("h_separation", 12)
	flow.add_theme_constant_override("v_separation", 6)
	var home_col := Palette.CELL_ACID if c.grid.home_integrity * 2 > c.grid.home_max_integrity else Palette.CELL_PINK
	flow.add_child(Badge.new("%d/%d" % [c.grid.home_integrity, c.grid.home_max_integrity], home_col, GLYPH_HOME,
		"Home server integrity. At 0 the campaign is lost.").with_meter(c.grid.home_integrity, c.grid.home_max_integrity))
	if c.exploits.is_empty():
		flow.add_child(Badge.new("0/%d" % cfg.min_exploits_for_breach, Palette.NET_CYAN, GLYPH_EXPLOIT,
			"No Exploits yet. Exploit Sites (◈ on the Grid) give one each; the breach needs %d." % cfg.min_exploits_for_breach))
	for e in c.exploits:
		var ename: String = RC.ExploitType.keys()[e]
		flow.add_child(Badge.new(ename.capitalize(), Palette.CELL_ACID, GLYPH_EXPLOIT,
			"Exploit %s found (%d/%d for the breach)." % [ename.capitalize(), c.exploits.size(), cfg.min_exploits_for_breach]))
	var seen := {}
	for aid in c.armory:
		if seen.has(aid):
			continue
		seen[aid] = true
		var data := lookup.get_content(aid) as DefenseAssetData
		flow.add_child(Badge.new("x%d" % c.armory.count(aid), Palette.CELL_PINK, "", "%s (Armory %d/%d)\n%s" % [
			_display(aid), c.armory.size(), cfg.armory_capacity, data.description if data != null else ""], aid))
	if c.armory.is_empty():
		flow.add_child(Badge.new("0/%d" % cfg.armory_capacity, Palette.CELL_PINK, GLYPH_NODE, "The Armory is empty: runs bank defence assets from their drops."))
	for m in HeatRules.active_modifiers(c, cfg):
		flow.add_child(Badge.new(_modifier_text(m), Palette.corp_color(c.corporation_id), GLYPH_RULE, "In force since a Heat threshold. Scrub Heat to fall back under it."))
	return flow


## Refusals, saves and unlocks the player must see (the log strip is optional): a toast.
func notify(text: String, warn: bool = false) -> void:
	ToastNote.show_on(self, text, warn)


func _report(events: Array[Dictionary]) -> void:
	if RunManager.campaign != null:
		CampaignRules.name_pending_raids(RunManager.campaign, RunManager.lookup(), events)
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")
			if String(e.get("type", "")) in TOAST_WARN_EVENTS:
				notify(String(e["text"]), true)
			elif String(e.get("type", "")) in TOAST_NEWS_EVENTS:
				notify(String(e["text"]))


## A button whose label ends in the key hint for `action`; relabelled when the device or
## the binds change (H20).
func _hint_button(text: String, action: StringName, on_pressed: Callable) -> Button:
	var b := _button(text, on_pressed)
	b.set_meta(&"hint_base", text)
	b.set_meta(&"hint_action", action)
	_hint_label(b)
	_hint_buttons.append(b)
	return b


func _hint_label(b: Button) -> void:
	b.text = ("%s %s" % [String(b.get_meta(&"hint_base")), Settings.hint(StringName(b.get_meta(&"hint_action")))]).strip_edges()


func _relabel_hints() -> void:
	var alive: Array[Button] = []
	for b in _hint_buttons:
		if is_instance_valid(b) and not b.is_queued_for_deletion():
			_hint_label(b)
			alive.append(b)
	_hint_buttons = alive


func _build_ui() -> void:
	background = CyberdeckBackground.new()
	add_child(background)
	wireframe = WireframeBackground.new()
	wireframe.visible = false
	add_child(wireframe)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE  # city map screens take clicks behind
	add_child(root)
	hud = HudBar.new()
	hud.loadout_pressed.connect(open_loadout)
	hud.daemons_pressed.connect(open_daemons)
	root.add_child(hud)
	_status = hud.label
	var scroll := ScrollContainer.new()
	scroll.follow_focus = true  # pad focus scrolls long lists (Grid Sites)
	# Never sideways: rows wrap (HFlowContainer) to the 1280-wide screen instead.
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(scroll)
	_panel_host = PanelContainer.new()
	_panel_host.theme_type_variation = &"GlassPanel"
	_panel_host.material = UiTheme.crt_material()
	_panel_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.add_child(_panel_host)
	_log = RichTextLabel.new()
	_log.theme_type_variation = &"LogText"
	_log.material = UiTheme.crt_material()
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.custom_minimum_size = Vector2(0, 96)
	root.add_child(_log)
	# Shown only when the player turns it on in Options.
	_log.visible = Settings.system_log
	Settings.changed.connect(func() -> void: _log.visible = Settings.system_log)


## Turns the buttons in `box` into "> ITEM" terminal menu lines.
func _as_menu(box: Control) -> void:
	for b in box.get_children():
		if b is Button:
			b.theme_type_variation = &"MenuItem"
			(b as Button).alignment = HORIZONTAL_ALIGNMENT_LEFT


## A long line of prose that wraps to the panel width (profile, unlocks, records).
func _para(text: String) -> Label:
	var l := _label(text)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return l


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b
