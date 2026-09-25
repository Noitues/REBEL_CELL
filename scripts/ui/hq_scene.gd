extends Control
## HQ scene: start screen (seed, ICE, home server, profile), HQ (roster, recruit, station,
## boosts, unlocks, Rank 3 segment swaps, Armory, story, pending raids), City Grid (Site
## status and actions, node install with unlock gating, upgrades), raid setup with exact
## projection, the raid playout with speed controls, the summary, campaign end. Every
## action goes through RunManager and CampaignRules; the scene only displays state.

const STATUS_NAMES := {GridState.SiteStatus.CORPORATE: "corporate", GridState.SiteStatus.CLEARED: "cleared",
	GridState.SiteStatus.CLAIMED: "claimed", GridState.SiteStatus.SEIZED: "SEIZED"}

var _status: Label
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var panel_name: String = ""
var background: CyberdeckBackground
var wireframe: WireframeBackground
var grid_view: GridMapView = null
var playout: RaidPlayoutPanel = null
var _settings_panel: PauseMenu = null
var _last_warned_raid: String = ""
## Site picked on the Grid map (its actions are listed first).
var selected_site: StringName = &""


func _ready() -> void:
	UiTheme.apply(self)
	_build_ui()
	var args := OS.get_cmdline_user_args()
	if args.has("--demo-start"):
		RunManager.save_slot = "demo"
		show_start()
		return
	if args.has("--demo-hq") or args.has("--demo-grid") or args.has("--demo-raid"):
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
		if args.has("--demo-grid") or args.has("--demo-raid"):
			var c := RunManager.campaign
			c.schematics = 100
			var grid_data := RunManager.corporation.city_grid
			var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
			CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), _demo_run(first))
			CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
			c.armory = [&"turret", &"ice_lock", &"decoy"]
			if args.has("--demo-raid"):
				CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
				show_raid()
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


func launch(site_id: StringName, operative_id: StringName) -> bool:
	var err := RunManager.launch_error(operative_id, site_id)
	if err != "":
		_log.append_text("[color=orange]%s[/color]\n" % err)
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
	_panel = p
	panel_name = name
	_panel_host.add_child(p)
	UiFocus.focus_first(p)
	# Worlds (STYLE_GUIDE 1): the room is a cyberdeck, the Grid and raids are wireframe.
	var net := name in ["grid", "raid", "raid_playout", "raid_summary"]
	background.visible = not net
	wireframe.visible = net
	AudioDirector.play_music("raid" if name.begins_with("raid") else ("grid" if name == "grid" else "hq"),
		RunManager.campaign.corporation_id if RunManager.campaign != null else &"")
	if RunManager.campaign != null:
		var band := RunManager.campaign.heat_majors_crossed(RunManager.config())
		background.heat_band = band
		wireframe.corp_creep = band / 3.0
		wireframe.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
	_refresh_status()


func open_settings() -> void:
	if _settings_panel != null:
		_settings_panel.queue_free()
		_settings_panel = null
		return
	_settings_panel = PauseMenu.new()
	_settings_panel.position = Vector2(size.x / 2.0 - 280, 100)
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
	box.add_child(GraffitiTag.new("REBEL_CELL"))
	box.add_child(_label("[HQ] the deck is warm. Jack a campaign in."))
	var row := HBoxContainer.new()
	box.add_child(row)
	row.add_child(_label("Campaign seed:"))
	var seed_spin := SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = 999999
	seed_spin.value = 1
	row.add_child(seed_spin)
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
	row.add_child(_button("New campaign", func() -> void:
		new_campaign(int(seed_spin.value), int(ice_spin.value), variants[home_pick.selected].id if not variants.is_empty() else RunManager.DEFAULT_HOME,
			classes[class_pick.selected].id if not classes.is_empty() else RunManager.DEFAULT_CLASS,
			corps[corp_pick.selected].id if not corps.is_empty() else RunManager.DEFAULT_CORPORATION)))
	box.add_child(ice_text)
	var code_row := HBoxContainer.new()
	code_row.add_child(_button("Daily run", func() -> void:
		var d := Time.get_date_dict_from_system()
		new_campaign(CampaignCode.daily_seed(d["year"], d["month"], d["day"]))))
	var code_edit := LineEdit.new()
	code_edit.name = "CodeEdit"
	code_edit.placeholder_text = "RC1-corporation-ice-seed-home-class"
	code_edit.custom_minimum_size.x = 360
	code_row.add_child(code_edit)
	code_row.add_child(_button("Start from code", func() -> void: start_from_code(code_edit.text)))
	box.add_child(code_row)
	if RunManager.has_save():
		box.add_child(_button("Resume saved campaign", resume))
	var p := RunManager.profile
	box.add_child(_label("Profile: %d campaigns started, %d won, %d lost; %d runs completed, %d operatives lost, raids %d/%d; best ICE %s." % [
		p.campaigns_started, p.campaigns_won, p.campaigns_lost, p.runs_completed, p.operatives_lost, p.raids_won, p.raids_lost, ProfileState.ice_text(p.best_ice)]))
	box.add_child(_label(ice_records_text()))
	var unlock_names := PackedStringArray()
	for uid in p.unlocks:
		var ud := RunManager.lookup().get_content(uid) as ProfileUnlockData
		unlock_names.append(ud.display_name if ud != null else String(uid))
	box.add_child(_label("Unlocks: %s" % (", ".join(unlock_names) if not unlock_names.is_empty() else "none yet (buy them at HQ with campaign Schematics)")))
	box.add_child(_button("Options [Esc]", open_settings))
	box.add_child(_button("Codex", show_codex))
	box.add_child(_button("Back to title", RunManager.go_to_title))
	_set_panel(box, "start")


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
	var header := HBoxContainer.new()
	header.add_child(GraffitiTag.new("REBEL_CELL"))
	var poster := HeatPoster.new(true)
	poster.hot_color = Palette.corp_color(c.corporation_id)
	poster.set_heat(c.heat, cfg.heat_max, cfg.major_heat_levels())
	header.add_child(poster)
	var radio := ZineNote.new("PIRATE RADIO", Vector2(260, 70))
	var dj_line := Dialogue.line("dj", RC.Voice.NARRATOR, c.corporation_id, &"", c.runs_started + c.runs_completed * 7)
	radio.append(dj_line.text if dj_line != null else "lo-fi loop: HQ")
	radio.append("vs %s | ICE %d%s" % [RunManager.corporation.display_name, c.ice_level, " | ASSIST" if c.is_assisted() else ""])
	var code := CampaignCode.of(c, c.start_class_id)
	radio.append("Code: %s%s" % [code, " (local: REBEL_CELL is built from your profile)" if RunManager.corporation.generated_from_profile else ""])
	radio.tooltip_text = dj_line.text if dj_line != null else ""
	header.add_child(radio)
	var jack := ZineStamp.new("JACK IN", Palette.CELL_PINK)
	jack.pressed.connect(show_grid)
	header.add_child(jack)
	box.add_child(header)
	var actions := HBoxContainer.new()
	box.add_child(actions)
	actions.add_child(_button("City Grid", show_grid))
	actions.add_child(_button("Codex", show_codex))
	actions.add_child(_button("Settings [Esc]", open_settings))
	for cls in RunManager.available_classes():
		var cid := cls.id
		actions.add_child(_button("Recruit %s (%d)" % [cls.display_name, cfg.rookie_cost], func() -> void: recruit(cid)))
	actions.add_child(_button("Scrub Heat -%d (%d)" % [cfg.heat_purchase_amount, CampaignRules.heat_purchase_price(c, cfg)], buy_heat_reduction))
	if c.grid.home_integrity < c.grid.home_max_integrity:
		actions.add_child(_button("Patch home +%d (%d)" % [c.grid.home_max_integrity - c.grid.home_integrity, CampaignRules.home_repair_price(c, cfg)], repair_home))
	if not c.pending_raids.is_empty():
		var raid := CampaignRules.raid_data(c.pending_raids[0], lookup)
		actions.add_child(_button("RAID PENDING: %s (%d)" % [raid.display_name, c.pending_raids.size()], show_raid))
	actions.add_child(_button("Save", func() -> void: RunManager.autosave(); _log.append_text("Saved.\n")))
	var mods := HeatRules.active_modifiers(c, cfg)
	var mod_text := ""
	for m in mods:
		mod_text += " %s %+.0f" % [RC.RuleModifierType.keys()[m.type], m.value]
	box.add_child(_label("Active Heat modifiers:%s | ICE %d" % [mod_text if mod_text != "" else " none", c.ice_level]))
	# Boosts for the next run (GDD 11.4).
	var boosts := HBoxContainer.new()
	boosts.add_child(_label("Next-run boosts:"))
	for b in cfg.netrun_boosts:
		if b == null:
			continue
		var bid := b.id
		var btn := _button("%s (%d)" % [b.display_name, b.cost], func() -> void: buy_boost(bid))
		btn.tooltip_text = b.description
		btn.disabled = c.pending_boosts.has(b.id) or c.schematics < b.cost
		boosts.add_child(btn)
	if not c.pending_boosts.is_empty():
		boosts.add_child(_label("queued: %s" % ", ".join(c.pending_boosts)))
	box.add_child(boosts)
	# Profile unlocks (GDD 3.4).
	var unlocks := HBoxContainer.new()
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
		btn.tooltip_text = u.description
		btn.disabled = c.schematics < u.schematic_cost
		unlocks.add_child(btn)
	if not any_unlock:
		unlocks.add_child(_label("everything unlocked"))
	box.add_child(unlocks)
	box.add_child(_label("Roster:"))
	for op in c.roster:
		var row := HBoxContainer.new()
		var where := CampaignRules.stationed_site(c, op.id)
		var polaroid := Polaroid.new("%s R%d" % [op.name, op.rank], "[%s PORTRAIT]" % op.class_id.to_upper(), -2.0 if c.roster.find(op) % 2 == 0 else 2.0)
		polaroid.glitch = not op.alive or op.hp * 4 <= op.max_hp
		row.add_child(polaroid)
		row.add_child(_label("  %s (%s) Rank %d HP %d/%d deck %d daemons %d %s%s" % [op.name, op.class_id, op.rank, op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size(),
			"" if op.alive else "[DEAD]", (" stationed on %s" % where) if where != &"" else ""]))
		if op.alive:
			if where != &"":
				var id := op.id
				row.add_child(_button("Recall", func() -> void: recall(id)))
			else:
				for site_id in c.grid.claimed_ids():
					var node := lookup.get_content(c.grid.node_type_of(site_id)) as NetworkNodeData
					if node != null and node.station_slots > 0 and c.grid.stationed_on(site_id) == &"" and c.grid.is_active_node(site_id):
						var oid := op.id
						var sid := site_id
						row.add_child(_button("Station on %s" % site_id, func() -> void: station(oid, sid)))
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
					row.add_child(pick)
		box.add_child(row)
	box.add_child(_label("Armory (%d/%d): %s" % [c.armory.size(), cfg.armory_capacity, ", ".join(c.armory) if not c.armory.is_empty() else "empty"]))
	box.add_child(_label("Exploits: %s" % _exploit_names(c)))
	var beats := CampaignRules.revealed_beats(c, RunManager.corporation)
	if not beats.is_empty():
		box.add_child(_label("Story so far:"))
		for b in beats:
			var t := RichTextLabel.new()
			t.fit_content = true
			t.custom_minimum_size = Vector2(700, 0)
			t.text = "  [%s] %s" % [b.title, b.text]
			box.add_child(t)
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
	var lookup := RunManager.lookup()
	var box := VBoxContainer.new()
	var top := HBoxContainer.new()
	box.add_child(top)
	grid_view = GridMapView.new()
	var paths: Array[Array] = []
	for pending in c.pending_raids:
		for entry in CampaignRules.raid_entries(c, corp, pending):
			var path: Array = [entry]
			var cur := entry
			var guard := 0
			while cur != c.grid.home_site_id and guard < 12:
				guard += 1
				cur = c.grid.next_hop(cur, c.grid.home_site_id, corp.city_grid)
				path.append(cur)
			paths.append(path)
	grid_view.show_grid(c, corp, paths)
	top.add_child(grid_view)
	var plan := ZineNote.new("THE PLAN", Vector2(300, 380))
	plan.append("Cleared Sites can be claimed.")
	plan.append("Relays extend your reach.")
	plan.append("%d/%d Exploits for the breach." % [c.exploits.size(), cfg.min_exploits_for_breach])
	plan.append("ICE %d | Heat %d" % [c.ice_level, c.heat])
	if not c.disabled_objectives.is_empty():
		plan.append("ICE switched off: %s" % ", ".join(c.disabled_objectives))
	if not c.pending_raids.is_empty():
		plan.append("[b]Raid pending:[/b] threat paths drawn in %s." % corp.display_name)
	var launchable := RunManager.launchable_sites()
	for s in launchable:
		plan.append("-> %s (T%d, %s)" % [s.display_name, s.tier, CampaignRules.run_kind_for(c, s)])
	if not RunManager.patrol_sites().is_empty():
		plan.append("Patrols: re-run a cleared or claimed Site for Rank (no objective).")
	launchable.append_array(RunManager.patrol_sites())
	top.add_child(plan)
	grid_view.selected_id = selected_site
	grid_view.site_clicked.connect(select_site)
	box.add_child(_button("Back to HQ", show_hq))
	var living := c.living_operatives()
	var choices := _node_choices()
	# The Site picked on the map (GDD 9.3): its actions first, highlighted on the map.
	if selected_site != &"" and CampaignRules.site_data(corp, selected_site) != null:
		var picked := _site_row(CampaignRules.site_data(corp, selected_site), launchable, living, choices)
		picked.name = "SelectedSite"
		var head := _label("SELECTED >")
		head.add_theme_color_override("font_color", Palette.CELL_ACID)
		picked.add_child(head)
		picked.move_child(head, 0)
		box.add_child(picked)
	for site in corp.city_grid.sites:
		if site == null:
			continue
		box.add_child(_site_row(site, launchable, living, choices))
	_set_panel(box, "grid")


## Selects a Site clicked on the Grid map and redraws the Grid with its actions first.
func select_site(site_id: StringName) -> void:
	selected_site = site_id
	show_grid()


## One Site's status line and the actions it allows now (launch, claim, repair, upgrade).
func _site_row(site: SiteData, launchable: Array[SiteData], living: Array[OperativeState], choices: Array[NetworkNodeData]) -> HBoxContainer:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	var lookup := RunManager.lookup()
	var s := c.grid.site(site.id)
	var row := HBoxContainer.new()
	var text := "T%d %s [%s]" % [site.tier, site.display_name, STATUS_NAMES.get(int(s["status"]), "?")]
	if c.grid.is_claimed(site.id):
		text += " %s %d/%d%s%s assets:%s" % [c.grid.node_type_of(site.id), s["integrity"], s["max_integrity"],
			" DISABLED" if int(s["condition"]) == GridState.Condition.DISABLED else "",
			(" +%d" % c.grid.upgrade_level_of(site.id)) if c.grid.upgrade_level_of(site.id) > 0 else "", ", ".join(c.grid.assets_on(site.id))]
	var objective := CampaignRules.site_objective(c, site)
	if objective == RC.SiteObjective.EXPLOIT:
		text += " (Exploit: %s)" % RC.ExploitType.keys()[site.exploit_type]
	elif objective == RC.SiteObjective.HEAT_REDUCTION:
		text += " (Heat %d)" % site.heat_change
	elif objective == RC.SiteObjective.BOSS:
		text += " (BOSS)"
	elif site.objective == RC.SiteObjective.HEAT_REDUCTION:
		text += " (objective off: ICE)"
	text += " links: %s" % ", ".join(c.grid.neighbors(site.id, corp.city_grid))
	row.add_child(_label(text))
	var launchable_here := false
	for l in launchable:
		if l.id == site.id:
			launchable_here = true
	if launchable_here and not living.is_empty():
		var op_pick := OptionButton.new()
		for op in living:
			op_pick.add_item("%s R%d" % [op.name, op.rank])
		row.add_child(op_pick)
		var sid := site.id
		var kind := CampaignRules.run_kind_for(c, site)
		row.add_child(_button("Launch %s" % kind, func() -> void: launch(sid, living[op_pick.selected].id)))
	if c.grid.is_cleared(site.id) and site.claimable:
		var node_pick := OptionButton.new()
		for i in choices.size():
			var node := choices[i]
			var available := CampaignRules.node_available(RunManager.profile, lookup, node)
			node_pick.add_item("%s (%d)%s" % [node.display_name, node.install_cost, "" if available else " [locked]"])
			node_pick.set_item_disabled(i, not available)
		row.add_child(node_pick)
		var sid2 := site.id
		row.add_child(_button("Claim", func() -> void: claim(sid2, choices[node_pick.selected].id)))
	if c.grid.is_claimed(site.id) and int(s["condition"]) == GridState.Condition.DISABLED:
		var sid3 := site.id
		row.add_child(_button("Repair", func() -> void: repair(sid3)))
	if c.grid.is_active_node(site.id) and site.id != c.grid.home_site_id:
		var cost := CampaignRules.upgrade_cost(c, cfg, site.id)
		if cost >= 0:
			var sid4 := site.id
			row.add_child(_button("Upgrade (%d)" % cost, func() -> void: upgrade(sid4)))
	return row


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
	var box := VBoxContainer.new()
	box.add_child(_label("RAID SETUP - %s: %s" % [raid.display_name, raid.warning_text]))
	box.add_child(_label("Entry: %s | Threat strength %+.0f%% | Projection: %s, home %d -> %d, %d/%d threats destroyed, %d steps" % [
		", ".join(CampaignRules.raid_entries(c, RunManager.corporation, pending)), CampaignRules.raid_strength_pct(c, cfg, pending, RunManager.corporation),
		"HOLDS" if projection.won else ("CAMPAIGN LOST" if projection.campaign_lost else "breached"),
		projection.home_before, projection.home_after, projection.threats_destroyed, projection.threats_destroyed + projection.threats_reached_home + _still_active(projection), projection.steps_run]))
	for e in projection.events:
		if e.get("type", "") in ["link_frozen", "link_altered"]:
			box.add_child(_label("  " + String(e["text"])))
	for site_id in c.grid.claimed_ids():
		var row := HBoxContainer.new()
		var n: Dictionary = projection.nodes.get(String(site_id), {})
		row.add_child(_label("%s (%s) %s -> %s [%s] assets: %s" % [site_id, c.grid.node_type_of(site_id), n.get("before", "?"), n.get("after", "?"), String(n.get("outcome", "?")).to_upper(), ", ".join(c.grid.assets_on(site_id))]))
		var assets := c.grid.assets_on(site_id)
		for i in assets.size():
			var idx := i
			var sid := site_id
			row.add_child(_button("Withdraw %s" % assets[i], func() -> void: move_asset(sid, idx, &"")))
			for other in c.grid.claimed_ids():
				if other != site_id and c.grid.is_active_node(other):
					var oid := other
					row.add_child(_button("-> %s" % other, func() -> void: move_asset(sid, idx, oid)))
		if not c.armory.is_empty() and c.grid.is_active_node(site_id):
			var pick := OptionButton.new()
			for a in c.armory:
				pick.add_item(String(a))
			row.add_child(pick)
			var sid2 := site_id
			row.add_child(_button("Deploy", func() -> void: deploy_asset(pick.selected, sid2)))
		box.add_child(row)
	box.add_child(_button("RUN THE RAID", fight_raid))
	box.add_child(_button("Back to HQ (raid stays pending)", show_hq))
	_set_panel(box, "raid")
	if _last_warned_raid != String(pending.get("raid_id", "")):
		_last_warned_raid = String(pending.get("raid_id", ""))
		Dialogue.raid_warning(c.corporation_id, StringName(String(pending.get("raid_id", raid.id))), c.raids_won + c.raids_lost)


## Codex (GDD 8.1): everything the Cell knows, zine-styled, plus the lexicon.
func show_codex() -> void:
	var box := VBoxContainer.new()
	box.add_child(GraffitiTag.new("CODEX"))
	var entries := Codex.entries(RunManager.lookup(), RunManager.profile)
	var tabs := HBoxContainer.new()
	box.add_child(tabs)
	var body := ZineNote.new("", Vector2(900, 380))
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	for section in entries:
		var name: String = section
		tabs.add_child(_button(name, func() -> void: _fill_codex(body, name, entries[name])))
	box.add_child(body)
	_fill_codex(body, "Slices", entries["Slices"])
	if not Dialogue.history.is_empty():
		var lines := ZineNote.new("LINES HEARD", Vector2(900, 100))
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
	var box := VBoxContainer.new()
	var view := GridMapView.new()
	view.custom_minimum_size = Vector2(760, 330)
	view.show_grid(c, RunManager.corporation)
	box.add_child(view)
	playout = RaidPlayoutPanel.new(view)
	box.add_child(playout)
	var cont := _button("Continue", _after_playout)
	cont.disabled = true
	playout.finished.connect(func() -> void: cont.disabled = false)
	box.add_child(cont)
	_set_panel(box, "raid_playout")
	var instant := DisplayServer.get_name() == "headless" or not Fx.effects_enabled()
	playout.play(events, instant)
	if instant:
		_after_playout()


func _after_playout() -> void:
	if RunManager.campaign.is_over():
		show_end()
	else:
		show_raid_summary()


func show_raid_summary() -> void:
	var c := RunManager.campaign
	var r := c.last_raid
	var box := VBoxContainer.new()
	box.add_child(_label("RAID %s - %d steps, %d destroyed, %d reached home, home %d -> %d" % [
		"REPELLED" if r.get("won", false) else "LOST", int(r.get("steps_run", 0)), int(r.get("threats_destroyed", 0)),
		int(r.get("threats_reached_home", 0)), int(r.get("home_before", 0)), int(r.get("home_after", 0))]))
	for id in r.get("nodes", {}):
		var n: Dictionary = r["nodes"][id]
		box.add_child(_label("  %s: %d -> %d %s" % [id, int(n["before"]), int(n["after"]), String(n["outcome"]).to_upper()]))
	box.add_child(_label("Seized: %s | Disabled: %s" % [", ".join(r.get("seized", [])), ", ".join(r.get("disabled", []))]))
	box.add_child(_button("Back to HQ", show_hq))
	_set_panel(box, "raid_summary")


func show_end() -> void:
	var c := RunManager.campaign
	Dialogue.speak("win" if c.outcome == CampaignState.Outcome.WON else "loss", RC.Voice.DISPATCH, c.corporation_id, &"", c.campaign_seed)
	var box := VBoxContainer.new()
	box.add_child(_label("CAMPAIGN %s" % (("WON - %s is down" % RunManager.corporation.final_boss.display_name) if c.outcome == CampaignState.Outcome.WON else "LOST - home server destroyed")))
	for b in CampaignRules.revealed_beats(c, RunManager.corporation):
		box.add_child(_label("  [%s] %s" % [b.title, b.text]))
	var p := RunManager.profile
	box.add_child(_label("Profile: %d won / %d lost, best ICE %s; next %s campaign may start up to ICE %d." % [p.campaigns_won, p.campaigns_lost, ProfileState.ice_text(p.best_ice), RunManager.corporation.display_name, RunManager.ice_cap(c.corporation_id)]))
	box.add_child(_label(ice_records_text()))
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
	_status.text = "Heat %d/%d | Schematics %d | Home %d/%d | Exploits %d | Raids pending %d | ICE %d | %s" % [
		c.heat, RunManager.config().heat_max, c.schematics, c.grid.home_integrity, c.grid.home_max_integrity,
		c.exploits.size(), c.pending_raids.size(), c.ice_level, "campaign over" if c.is_over() else "active"]


func _report(events: Array[Dictionary]) -> void:
	if RunManager.campaign != null:
		CampaignRules.name_pending_raids(RunManager.campaign, RunManager.lookup(), events)
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")


func _build_ui() -> void:
	background = CyberdeckBackground.new()
	add_child(background)
	wireframe = WireframeBackground.new()
	wireframe.visible = false
	add_child(wireframe)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	_status = Label.new()
	root.add_child(_status)
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(scroll)
	_panel_host = PanelContainer.new()
	_panel_host.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_panel_host.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.add_child(_panel_host)
	_log = RichTextLabel.new()
	_log.bbcode_enabled = true
	_log.scroll_following = true
	_log.custom_minimum_size = Vector2(0, 140)
	root.add_child(_log)


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b
