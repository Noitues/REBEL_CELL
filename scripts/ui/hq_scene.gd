extends Control
## Functional M3 HQ scene (placeholder look): start screen, HQ (roster, recruit, station,
## spend, Armory, story, pending raids), City Grid (Site status and actions), raid setup
## with exact projection and playout, campaign end. Every action goes through RunManager
## and CampaignRules; the scene only displays state.

const STATUS_NAMES := {GridState.SiteStatus.CORPORATE: "corporate", GridState.SiteStatus.CLEARED: "cleared",
	GridState.SiteStatus.CLAIMED: "claimed", GridState.SiteStatus.SEIZED: "SEIZED"}
const NODE_CHOICES: Array[StringName] = [&"relay", &"firewall_relay", &"safehouse"]

var _status: Label
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var panel_name: String = ""


func _ready() -> void:
	_build_ui()
	var args := OS.get_cmdline_user_args()
	if args.has("--demo-hq") or args.has("--demo-grid") or args.has("--demo-raid"):
		# Dev shortcut for screenshots: godot --path . -- --demo-grid (own save slot)
		RunManager.save_slot = "demo"
		new_campaign(1)
		if args.has("--demo-grid") or args.has("--demo-raid"):
			var c := RunManager.campaign
			c.schematics = 100
			CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), _demo_run(&"t1_a"))
			CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), &"t1_a", &"firewall_relay")
			c.armory = [&"turret", &"ice_lock", &"decoy"]
			if args.has("--demo-raid"):
				CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, &"t1_a")
				show_raid()
			else:
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


# --- Public API (buttons and the integration test) ---------------------------------------

func new_campaign(seed: int) -> void:
	RunManager.new_campaign(seed)
	_log.append_text("[b]New campaign[/b] (seed %d) against %s. Story path: %s.\n" % [seed, RunManager.corporation.display_name, RunManager.campaign.story_path_id])
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
	RunManager.go_to_netrun()
	return true


func claim(site_id: StringName, node_type_id: StringName) -> void:
	_report(CampaignRules.claim(RunManager.campaign, RunManager.corporation, RunManager.config(), RunManager.lookup(), site_id, node_type_id))
	RunManager.autosave()
	show_grid()


func repair(site_id: StringName) -> void:
	_report(CampaignRules.repair(RunManager.campaign, RunManager.config(), RunManager.lookup(), site_id))
	RunManager.autosave()
	show_grid()


func recruit() -> void:
	_report(CampaignRules.recruit(RunManager.campaign, RunManager.config(), RunManager.class_data()))
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
	if RunManager.campaign.is_over():
		show_end()
	else:
		show_raid_summary()


# --- Panels ---------------------------------------------------------------------------------

func _set_panel(p: Control, name: String) -> void:
	if _panel != null:
		_panel.queue_free()
	_panel = p
	panel_name = name
	_panel_host.add_child(p)
	_refresh_status()


func show_start() -> void:
	var box := VBoxContainer.new()
	box.add_child(_label("REBEL_CELL - HQ (M3 placeholder)"))
	var row := HBoxContainer.new()
	box.add_child(row)
	row.add_child(_label("Campaign seed:"))
	var seed_spin := SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = 999999
	seed_spin.value = 1
	row.add_child(seed_spin)
	row.add_child(_button("New campaign vs Solace", func() -> void: new_campaign(int(seed_spin.value))))
	if RunManager.has_save():
		box.add_child(_button("Resume saved campaign", resume))
	var p := RunManager.profile
	box.add_child(_label("Profile: %d campaigns started, %d won, %d lost; %d runs completed, %d operatives lost, raids %d/%d; best ICE %d." % [
		p.campaigns_started, p.campaigns_won, p.campaigns_lost, p.runs_completed, p.operatives_lost, p.raids_won, p.raids_lost, p.best_ice]))
	_set_panel(box, "start")


func show_hq() -> void:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	var box := VBoxContainer.new()
	box.add_child(_label("HQ - %s" % RunManager.corporation.display_name))
	var actions := HBoxContainer.new()
	box.add_child(actions)
	actions.add_child(_button("City Grid", show_grid))
	actions.add_child(_button("Recruit rookie (%d)" % cfg.rookie_cost, recruit))
	actions.add_child(_button("Scrub Heat -%d (%d)" % [cfg.heat_purchase_amount, CampaignRules.heat_purchase_price(c, cfg)], buy_heat_reduction))
	if not c.pending_raids.is_empty():
		var raid := CampaignRules.raid_data(c.pending_raids[0], RunManager.lookup())
		actions.add_child(_button("RAID PENDING: %s (%d)" % [raid.display_name, c.pending_raids.size()], show_raid))
	actions.add_child(_button("Save", func() -> void: RunManager.autosave(); _log.append_text("Saved.\n")))
	var mods := HeatRules.active_modifiers(c, cfg)
	var mod_text := ""
	for m in mods:
		mod_text += " %s %+.0f" % [RC.RuleModifierType.keys()[m.type], m.value]
	box.add_child(_label("Active Heat modifiers:%s" % (mod_text if mod_text != "" else " none")))
	box.add_child(_label("Roster:"))
	for op in c.roster:
		var row := HBoxContainer.new()
		var where := CampaignRules.stationed_site(c, op.id)
		row.add_child(_label("  %s (%s) Rank %d HP %d/%d deck %d daemons %d %s%s" % [op.name, op.class_id, op.rank, op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size(),
			"" if op.alive else "[DEAD]", (" stationed on %s" % where) if where != &"" else ""]))
		if op.alive:
			if where != &"":
				var id := op.id
				row.add_child(_button("Recall", func() -> void: recall(id)))
			else:
				for site_id in c.grid.claimed_ids():
					var node := RunManager.lookup().get_content(c.grid.node_type_of(site_id)) as NetworkNodeData
					if node != null and node.station_slots > 0 and c.grid.stationed_on(site_id) == &"" and c.grid.is_active_node(site_id):
						var oid := op.id
						var sid := site_id
						row.add_child(_button("Station on %s" % site_id, func() -> void: station(oid, sid)))
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


func show_grid() -> void:
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var box := VBoxContainer.new()
	box.add_child(_label("City Grid - pick a Site to netrun, claim or repair"))
	box.add_child(_button("Back to HQ", show_hq))
	var launchable := RunManager.launchable_sites()
	var living := c.living_operatives()
	for site in corp.city_grid.sites:
		if site == null:
			continue
		var s := c.grid.site(site.id)
		var row := HBoxContainer.new()
		var text := "T%d %s [%s]" % [site.tier, site.display_name, STATUS_NAMES.get(int(s["status"]), "?")]
		if c.grid.is_claimed(site.id):
			text += " %s %d/%d%s assets:%s" % [c.grid.node_type_of(site.id), s["integrity"], s["max_integrity"],
				" DISABLED" if int(s["condition"]) == GridState.Condition.DISABLED else "", ", ".join(c.grid.assets_on(site.id))]
		if site.objective == RC.SiteObjective.EXPLOIT:
			text += " (Exploit: %s)" % RC.ExploitType.keys()[site.exploit_type]
		elif site.objective == RC.SiteObjective.HEAT_REDUCTION:
			text += " (Heat %d)" % site.heat_change
		elif site.objective == RC.SiteObjective.BOSS:
			text += " (BOSS)"
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
			for n in NODE_CHOICES:
				var node := RunManager.lookup().get_content(n) as NetworkNodeData
				node_pick.add_item("%s (%d)" % [node.display_name, node.install_cost])
			row.add_child(node_pick)
			var sid2 := site.id
			row.add_child(_button("Claim", func() -> void: claim(sid2, NODE_CHOICES[node_pick.selected])))
		if c.grid.is_claimed(site.id) and int(s["condition"]) == GridState.Condition.DISABLED:
			var sid3 := site.id
			row.add_child(_button("Repair", func() -> void: repair(sid3)))
		box.add_child(row)
	_set_panel(box, "grid")


func show_raid() -> void:
	var c := RunManager.campaign
	var pending := RunManager.pending_raid()
	if pending.is_empty():
		show_hq()
		return
	var raid := CampaignRules.raid_data(pending, RunManager.lookup())
	var projection := RunManager.project_raid()
	var box := VBoxContainer.new()
	box.add_child(_label("RAID SETUP - %s: %s" % [raid.display_name, raid.warning_text]))
	box.add_child(_label("Entry: %s | Threat strength %+.0f%% | Projection: %s, home %d -> %d, %d/%d threats destroyed, %d steps" % [
		", ".join(CampaignRules.raid_entries(c, RunManager.corporation, pending)), CampaignRules.raid_strength_pct(c, RunManager.config()),
		"HOLDS" if projection.won else ("CAMPAIGN LOST" if projection.campaign_lost else "breached"),
		projection.home_before, projection.home_after, projection.threats_destroyed, projection.threats_destroyed + projection.threats_reached_home + _still_active(projection), projection.steps_run]))
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
	var box := VBoxContainer.new()
	box.add_child(_label("CAMPAIGN %s" % ("WON - the Renewal Engine is down" if c.outcome == CampaignState.Outcome.WON else "LOST - home server destroyed")))
	for b in CampaignRules.revealed_beats(c, RunManager.corporation):
		box.add_child(_label("  [%s] %s" % [b.title, b.text]))
	var p := RunManager.profile
	box.add_child(_label("Profile: %d won / %d lost, best ICE %d." % [p.campaigns_won, p.campaigns_lost, p.best_ice]))
	box.add_child(_button("New campaign", func() -> void: RunManager.campaign = null; show_start()))
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
	_status.text = "Heat %d/%d | Schematics %d | Home %d/%d | Exploits %d | Raids pending %d | %s" % [
		c.heat, RunManager.config().heat_max, c.schematics, c.grid.home_integrity, c.grid.home_max_integrity,
		c.exploits.size(), c.pending_raids.size(), "campaign over" if c.is_over() else "active"]


func _report(events: Array[Dictionary]) -> void:
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")


func _build_ui() -> void:
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
