extends Control
## Functional M2 netrun scene (placeholder look): start screen, map, combat (embedded
## CombatScene), rewards, Terminal events, Modem shop and the run summary. Every
## action goes through RunManager's NetrunSession; the scene only displays state.

const COMBAT_SCENE := preload("res://scenes/combat/combat_scene.tscn")
const NODE_LABELS := {RC.InfilNodeType.ROUTER: "Router", RC.InfilNodeType.TERMINAL: "Terminal",
	RC.InfilNodeType.MODEM: "Modem", RC.InfilNodeType.SERVER_RACK: "Server Rack"}

var _status: Label
## Top strip: screen title and the status line (`_status`).
var hud: HudBar
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var combat_scene: Control = null
var background: WireframeBackground
var map_view: NetrunMapView = null
var playout: RaidPlayoutPanel = null
var _spoken_events: Dictionary = {}
var _settings_panel: PauseMenu = null


func _ready() -> void:
	UiTheme.apply(self)
	_build_ui()
	var args := OS.get_cmdline_user_args()
	if args.has("--demo-shop"):
		RunManager.save_slot = "demo"
		new_campaign(1)
		start_run(1)
		RunManager.netrun.run.cycles = 120
		RunManager.netrun._open_shop()
		_show_current()
		return
	if args.has("--demo-event") or args.has("--demo-dispatch") or args.has("--demo-loot"):
		# Screenshot shortcuts for the Terminal event (street / DISPATCH voice) and loot.
		RunManager.save_slot = "demo"
		new_campaign(1)
		start_run(1)
		var run := RunManager.netrun.run
		if args.has("--demo-loot"):
			run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
			run.phase = RunState.Phase.REWARD
		else:
			run.event_id = &"ev_dispatch_early_reply" if args.has("--demo-dispatch") else &"ev_leash_on_the_floor"
			run.phase = RunState.Phase.EVENT
		_show_current()
		return
	if args.has("--demo-run") or args.has("--demo-combat") or args.has("--demo-tutorial"):
		# Dev shortcut for screenshots: godot --path . -- --demo-run (uses its own save slot)
		RunManager.save_slot = "demo"
		new_campaign(1)
		for a in args:
			if a.begins_with("--demo-class="):
				# Screenshot operative of another class (campaign-only, bypasses Profile unlocks).
				var cls := RunManager.lookup().get_content(StringName(a.trim_prefix("--demo-class="))) as ClassData
				if cls != null:
					RunManager.campaign.roster.clear()
					RunManager.campaign.recruit(cls)
		start_run(1)
		if args.has("--demo-combat") or args.has("--demo-tutorial"):
			RunManager.pending_tutorial = args.has("--demo-tutorial")
			enter_node(RunManager.netrun.available_nodes()[0])
		return
	if RunManager.has_active_run():
		_show_current()
	else:
		_show_start()


# --- Public API (used by buttons and the integration test) --------------------------

func new_campaign(seed: int) -> void:
	RunManager.new_campaign(seed)
	_log.append_text("[b]New campaign[/b] (seed %d): %d Schematics, %d rookies.\n" % [seed, RunManager.campaign.schematics, RunManager.campaign.roster.size()])
	_show_start()


func start_run(_tier: int = 1) -> void:
	var s := RunManager.start_run()
	if s == null:
		_log.append_text("[color=orange]No living operative or open Site: go to HQ.[/color]\n")
		return
	_report(s.last_events)
	_show_current()


func resume() -> void:
	if RunManager.resume():
		_log.append_text("[b]Resumed.[/b]\n")
		_show_current()
	else:
		_log.append_text("[color=orange]Nothing to resume.[/color]\n")


func enter_node(node_id: StringName) -> void:
	var s := RunManager.netrun
	_report(s.enter_node(node_id))
	RunManager.after_step()
	_show_current()


func choose_reward(index: int, slot: int = -1) -> void:
	_report(RunManager.netrun.choose_reward(index, slot))
	RunManager.after_step()
	_show_current()


func skip_reward() -> void:
	_report(RunManager.netrun.skip_reward())
	RunManager.after_step()
	_show_current()


func choose_event(index: int) -> void:
	_report(RunManager.netrun.choose_event_option(index))
	RunManager.after_step()
	_show_current()


func buy(kind: String, index: int, slot: int = -1) -> void:
	_report(RunManager.netrun.buy(kind, index, slot))
	RunManager.after_step()
	_show_current()


func remove_card(deck_index: int) -> void:
	_report(RunManager.netrun.remove_card(deck_index))
	RunManager.after_step()
	_show_current()


func overwrite_slice(slot: int, stock_index: int) -> void:
	_report(RunManager.netrun.overwrite_slice(slot, stock_index))
	RunManager.after_step()
	_show_current()


func leave_shop() -> void:
	_report(RunManager.netrun.leave_shop())
	RunManager.after_step()
	_show_current()


func raid_deploy_run_asset(index: int, site_id: StringName) -> void:
	_report(RunManager.netrun.raid_deploy_run_asset(index, site_id))
	RunManager.after_step()
	_show_current()


func raid_deploy_armory(index: int, site_id: StringName) -> void:
	_report(RunManager.netrun.raid_deploy_armory(index, site_id))
	RunManager.after_step()
	_show_current()


func raid_move(from_site: StringName, index: int, to_site: StringName) -> void:
	_report(RunManager.netrun.raid_move(from_site, index, to_site))
	RunManager.after_step()
	_show_current()


func raid_fight() -> void:
	var events := RunManager.netrun.raid_fight()
	_report(events)
	RunManager.after_step()
	_show_raid_playout(events)


func finish_run() -> void:
	RunManager.clear_run()
	RunManager.go_to_hq()
	_show_start()


func save_and_quit() -> void:
	RunManager.autosave()
	_log.append_text("Saved.\n")
	RunManager.go_to_hq()
	_show_start()


# --- Panels --------------------------------------------------------------------------

func _show_current() -> void:
	var s := RunManager.netrun
	if s == null:
		_show_start()
		return
	_refresh_status()
	match s.run.phase:
		RunState.Phase.MAP:
			_show_map()
		RunState.Phase.COMBAT:
			_show_combat()
		RunState.Phase.REWARD:
			_show_reward()
		RunState.Phase.EVENT:
			_show_event()
		RunState.Phase.SHOP:
			_show_shop()
		RunState.Phase.RAID:
			_show_raid()
		_:
			_show_end()


## `glass` = false for screens built from their own terminal windows (the city shows
## between them).
func _set_panel(p: Control, glass: bool = true) -> void:
	if _panel != null:
		_panel.queue_free()
	_panel = p
	combat_scene = null
	_panel_host.theme_type_variation = &"GlassPanel" if glass else &""
	_panel_host.add_child(p)
	if p.has_method("focus_hand"):
		p.focus_hand()  # the combat scene links and focuses its own hand
	else:
		UiWrap.fit(p)
		UiFocus.link_layout(p)
		UiFocus.focus_first(p)
	var s := RunManager.netrun
	_title_screen(s)
	if s != null and not s.run.is_over():
		AudioDirector.play_music("raid" if s.run.phase == RunState.Phase.RAID else "netrun", s.campaign.corporation_id)
		if s.run.phase != RunState.Phase.COMBAT:
			background.visible = true
	if RunManager.campaign != null:
		background.corp_creep = clampf(RunManager.campaign.heat / 100.0, 0.0, 1.0)
		background.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
		background.set_district(RunManager.campaign.corporation_id)
	# The combat panel brings its own log; give it the height instead.
	_log.custom_minimum_size = Vector2(0, 50 if p.get_script() == COMBAT_SCENE.get_script() or p.has_method("attach_netrun") else 110)


## Names the screen on the HUD strip from the run phase (STYLE_GUIDE 4, "Neon city").
func _title_screen(s: NetrunSession) -> void:
	if s == null:
		hud.set_screen("", "NETRUN")
		return
	match s.run.phase:
		RunState.Phase.MAP:
			hud.set_screen("", "NETRUN // ROUTE")
		RunState.Phase.COMBAT:
			hud.set_screen("", "")
		RunState.Phase.REWARD:
			hud.set_screen("", "BREACH PAYOUT")
		RunState.Phase.EVENT:
			hud.set_screen("04", "TERMINAL EVENT & DISPATCH")
		RunState.Phase.SHOP:
			hud.set_screen("05", "MODEM CYBER SHOP")
		RunState.Phase.RAID:
			hud.set_screen("", "NETRUN // RAID")
		_:
			hud.set_screen("", "NETRUN // JACK OUT")


func _show_start() -> void:
	_refresh_status()
	var box := VBoxContainer.new()
	box.add_child(GraffitiTag.new("NETRUN"))
	var row := HBoxContainer.new()
	box.add_child(row)
	row.add_child(_label("Campaign seed:"))
	var seed_spin := SpinBox.new()
	seed_spin.min_value = 0
	seed_spin.max_value = 999999
	seed_spin.value = 1
	row.add_child(seed_spin)
	row.add_child(_button("New campaign", func() -> void: new_campaign(int(seed_spin.value))))
	if RunManager.has_save():
		box.add_child(_button("Resume saved game", resume))
	if RunManager.campaign != null:
		var living := RunManager.campaign.living_operatives()
		var info := "Campaign: Heat %d, Schematics %d, roster %d living." % [RunManager.campaign.heat, RunManager.campaign.schematics, living.size()]
		box.add_child(_label(info))
		for op in living:
			box.add_child(_label("  %s (%s) Rank %d, HP %d/%d, deck %d, daemons %d" % [op.name, op.class_id, op.rank, op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size()]))
		if RunManager.has_active_run():
			box.add_child(_button("Continue the current run", _show_current))
		elif not living.is_empty():
			box.add_child(_button("Start a netrun at the first open Site", func() -> void: start_run(1)))
		box.add_child(_button("Go to HQ (City Grid, raids, roster)", RunManager.go_to_hq))
	_set_panel(box)


## The netrun map as a wireframe graph (GDD 9.1): click a reachable node to enter it.
## Keyboard: 1-9 pick the reachable nodes in order.
func _show_map() -> void:
	var s := RunManager.netrun
	var win := TerminalWindow.new("ROUTE // Pick the next node (Heat cost shown; follow the links). Click a glowing node or press 1-9.")
	var box := win.body
	map_view = NetrunMapView.new()
	map_view.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
	map_view.show_map(s.run.map, s.run.current_node_id, s.run.visited, s.available_nodes(), s.map_heat())
	map_view.node_clicked.connect(func(id: StringName) -> void:
		if RunManager.netrun != null and RunManager.netrun.available_nodes().has(id):
			enter_node(id))
	box.add_child(map_view)
	var row := HBoxContainer.new()
	box.add_child(row)
	var available := s.available_nodes()
	for i in available.size():
		var node := s.run.map.get_node(available[i])
		var text: String = "%d: %s%s" % [i + 1, NODE_LABELS.get(node["type"], "?"), " (elite)" if node["elite"] and node["type"] == RC.InfilNodeType.ROUTER else ""]
		var heat := s.node_heat(available[i])
		if heat != 0:
			text += " %+d Heat" % heat
		var id: StringName = available[i]
		row.add_child(_button(text, func() -> void: enter_node(id)))
	row.add_child(_button("Save & quit to start screen", save_and_quit))
	var panel := VBoxContainer.new()
	panel.add_child(win)
	_set_panel(panel, false)


## Raid playout (GDD 7.2): threat markers animate over the Grid; 1x/2x/4x and skip.
func _show_raid_playout(events: Array[Dictionary]) -> void:
	var c := RunManager.campaign
	var box := VBoxContainer.new()
	var view := GridMapView.new()
	view.custom_minimum_size = Vector2(760, 300)
	view.show_grid(c, RunManager.corporation)
	box.add_child(view)
	playout = RaidPlayoutPanel.new(view)
	box.add_child(playout)
	var cont := _button("Continue", _show_current)
	cont.disabled = true
	playout.finished.connect(func() -> void: cont.disabled = false)
	box.add_child(cont)
	_set_panel(box)
	playout.play(events, _instant_playout())
	if playout.is_done() and _instant_playout():
		_show_current()


func _instant_playout() -> bool:
	return DisplayServer.get_name() == "headless" or not Fx.effects_enabled()


func _show_combat() -> void:
	var s := RunManager.netrun
	var scene: Control = COMBAT_SCENE.instantiate()
	scene.auto_start = false
	scene.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_set_panel(scene)
	background.visible = false  # the arena draws its own wireframe world
	combat_scene = scene
	scene.attach_netrun(s)
	scene.engine.state_changed.connect(_on_combat_state_changed)


func _on_combat_state_changed(state: CombatState, _events: Array[Dictionary]) -> void:
	_refresh_status()
	if state.is_over():
		RunManager.after_step()
		_report(RunManager.netrun.last_events)
		# Leave the final combat state visible for a moment, then move on.
		var timer := get_tree().create_timer(0.8)
		timer.timeout.connect(_show_current)


func _show_reward() -> void:
	var s := RunManager.netrun
	var offer := s.current_reward()
	var win := TerminalWindow.new("RACK BREACHED // LOOT: pick a %s" % offer["kind"], Palette.CELL_ACID)
	win.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	var box := win.body
	box.add_child(GraffitiTag.new("LOOT: pick a %s" % offer["kind"]))
	var slot_option: OptionButton = null
	if offer["kind"] == "firmware":
		var row := HBoxContainer.new()
		row.add_child(_label("Socket into slot:"))
		slot_option = OptionButton.new()
		for i in s.run.operative.slot_slice_ids.size():
			var fw := s.run.operative.slot_firmware_ids[i]
			slot_option.add_item("%d: %s%s" % [i, s.run.operative.slot_slice_ids[i], (" {%s}" % fw) if fw != &"" else ""])
		row.add_child(slot_option)
		box.add_child(row)
	# Offers as zine stickers (STYLE_GUIDE 4): cards show their RAM cost, others none.
	var stickers := HBoxContainer.new()
	stickers.name = "Stickers"
	stickers.add_theme_constant_override("separation", 14)
	box.add_child(stickers)
	for i in offer["options"].size():
		var id := StringName(String(offer["options"][i]))
		var res := s.lookup.get_content(id)
		var cost := int(res.get("ram_cost")) if res is CardData else -1
		var sticker := ZineCard.new(TextDb.t(res, "display_name"), cost, TextDb.t(res, "description"), i)
		sticker.custom_minimum_size = Vector2(150, 170)
		sticker.hotkey = ""  # rewards are picked by click or focus, not number keys
		sticker.tooltip_text = Codex.describe(res)
		var index: int = i
		sticker.pressed.connect(func() -> void: choose_reward(index, slot_option.selected if slot_option != null else -1))
		stickers.add_child(sticker)
	box.add_child(_button("Skip", skip_reward))
	var wrap := CenterContainer.new()
	wrap.add_child(win)
	_set_panel(wrap, false)


## Terminal event (GDD 4.2): zine paper for street and corporate voices; DISPATCH stays
## clean system text on a dark strip (STYLE_GUIDE 3), never zined.
func _show_event() -> void:
	var s := RunManager.netrun
	var ev := s.current_event()
	var box := VBoxContainer.new()
	var body := VBoxContainer.new()
	var dispatch := ev.speaker == RC.Voice.DISPATCH
	var holder: Control
	if dispatch:
		var strip := PanelContainer.new()
		var style := UiTheme.box(Color(0.02, 0.03, 0.07, 0.96), Palette.CRT_AMBER, 1, 16, 14)
		style.border_width_left = 4
		style.shadow_color = Color(0, 0, 0, 0.5)
		style.shadow_size = 8
		strip.add_theme_stylebox_override("panel", style)
		strip.material = UiTheme.crt_material()
		strip.custom_minimum_size = Vector2(700, 220)
		strip.add_child(body)
		holder = strip
	else:
		var panel := ZinePanel.new(TextDb.t(ev, "title").to_upper(), -1.0)
		panel.custom_minimum_size = Vector2(760, 200)
		panel.content.add_child(body)
		holder = panel
	holder.name = "EventPanel"
	var split := HBoxContainer.new()
	split.add_theme_constant_override("separation", 22)
	box.add_child(split)
	split.add_child(holder)
	holder.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	var options := VBoxContainer.new()
	options.add_theme_constant_override("separation", 14)
	options.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	split.add_child(options)
	var who: String = Dialogue.speaker_name(ev.speaker, ev.corporation_id if ev.corporation_id != &"" else RunManager.campaign.corporation_id)
	var speaker := _label(who + ((" - " + TextDb.t(ev, "title")) if dispatch else ""))
	speaker.add_theme_color_override("font_color", Palette.CRT_AMBER if dispatch else Palette.CELL_PINK)
	body.add_child(speaker)
	var text := RichTextLabel.new()
	text.fit_content = true
	text.custom_minimum_size = Vector2(720, 60)
	text.text = TextDb.t(ev, "text")
	text.add_theme_color_override("default_color", Palette.CRT_AMBER if dispatch else Palette.INK)
	body.add_child(text)
	if not _spoken_events.has(ev.id):
		_spoken_events[ev.id] = true
		Dialogue.say(ev.speaker, TextDb.t(ev, "text"), 0.0, ev.corporation_id if ev.corporation_id != &"" else RunManager.campaign.corporation_id)
	for i in ev.choices.size():
		var c := ev.choices[i]
		var b := Button.new()
		b.text = _choice_text(TextDb.t(c, "label"), s.choice_costs(c))
		var err := s.choice_error(c)
		b.disabled = err != ""
		b.tooltip_text = err
		var index := i
		b.pressed.connect(func() -> void: choose_event(index))
		b.theme_type_variation = &"NoteButton"
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		options.add_child(b)
	options.add_child(GraffitiScrawl.new("PLAY IT\nSAFE??", -6.0, 24))
	_set_panel(box, false)


## A Terminal choice's label with its costs from the data, replacing the hand-written
## "(...)" summary so a hidden or unscaled cost can't slip through.
static func _choice_text(label: String, costs: String) -> String:
	var base := label
	var open := base.rfind(" (")
	if open > 0 and base.ends_with(")"):
		base = base.substr(0, open)
	return base if costs == "" else "%s (%s)" % [base, costs]


## Modem (GDD 11.2), laid out like the reference cyber shop: the neon MODEM sign with
## BUY / SELL / TRADE, MICROCHIPS (Firmware and Daemons as glowing chips), the CARD
## BUILDER (cards, removal, slice overwrite), shop notes and the operative's inventory.
func _show_shop() -> void:
	var s := RunManager.netrun
	var shop := s.run.shop
	var op := s.run.operative
	var outer := HBoxContainer.new()
	outer.add_theme_constant_override("separation", 16)
	var signs := VBoxContainer.new()
	signs.add_theme_constant_override("separation", 10)
	signs.add_child(NeonSign.new("MODEM", "CYBER SHOP"))
	signs.add_child(NeonTag.new("BUY", Palette.NET_CYAN))
	signs.add_child(NeonTag.new("SELL", Palette.CELL_PINK))
	signs.add_child(NeonTag.new("TRADE", Palette.CRT_AMBER))
	outer.add_child(signs)
	var mid := VBoxContainer.new()
	mid.add_theme_constant_override("separation", 12)
	mid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	outer.add_child(mid)
	var fw_slot := OptionButton.new()
	for k in op.slot_slice_ids.size():
		fw_slot.add_item("Firmware into slot %d: %s" % [k, op.slot_slice_ids[k]])
	var chips_win := TerminalWindow.new("MICROCHIPS")
	chips_win.tag_label.text = "CYCLE"
	var chips := HBoxContainer.new()
	chips.name = "Chips"
	chips.add_theme_constant_override("separation", 10)
	chips_win.body.add_child(chips)
	var cards_win := TerminalWindow.new("CARD BUILDER", Palette.CELL_PINK)
	cards_win.tag_label.text = "CYCLE"
	# Cards first: the "Stickers" row holds the shop's cards in stock order.
	var stickers := HBoxContainer.new()
	stickers.name = "Stickers"
	stickers.add_theme_constant_override("separation", 10)
	cards_win.body.add_child(stickers)
	var n := 0
	for kind in ["cards", "firmware", "daemons"]:
		var prices: Array = shop.get(kind.trim_suffix("s") + "_prices", [])
		for i in shop.get(kind, []).size():
			var id := StringName(String(shop[kind][i]))
			var res := s.lookup.get_content(id)
			var sticker := ZineCard.new(TextDb.t(res, "display_name"), int(prices[i]), "%s: %s" % [kind.trim_suffix("s"), TextDb.t(res, "description")], n)
			sticker.hotkey = ""
			if kind == "cards":
				sticker.as_tile(ZineCard.Look.CARD_TILE, Palette.CELL_PINK)
			else:
				sticker.as_tile(ZineCard.Look.CHIP, Palette.NET_CYAN if kind == "firmware" else Palette.NEON_VIOLET)
			sticker.tooltip_text = "%d Cycles\n%s" % [int(prices[i]), Codex.describe(res)]
			sticker.disabled = int(prices[i]) > s.run.cycles
			var index: int = i
			var k: String = kind
			sticker.pressed.connect(func() -> void: buy(k, index, fw_slot.selected if k == "firmware" else -1))
			(stickers if kind == "cards" else chips).add_child(sticker)
			n += 1
	if chips.get_child_count() > 0:
		mid.add_child(chips_win)
		if not shop.get("firmware", []).is_empty():
			chips_win.body.add_child(fw_slot)
	mid.add_child(cards_win)
	var removal := HBoxContainer.new()
	removal.add_child(_label("Remove a card (%d Cycles):" % s.card_removal_price()))
	var deck_option := OptionButton.new()
	for i in op.deck.size():
		deck_option.add_item("%d: %s" % [i, op.deck[i]])
	removal.add_child(deck_option)
	removal.add_child(_button("Remove", func() -> void: remove_card(deck_option.selected)))
	cards_win.body.add_child(removal)
	var overwrite := HBoxContainer.new()
	overwrite.add_child(_label("Overwrite a slice:"))
	var slot_pick := OptionButton.new()
	for i in op.slot_slice_ids.size():
		slot_pick.add_item("slot %d: %s (%d Cycles)" % [i, op.slot_slice_ids[i], s.slice_overwrite_price(i)])
	overwrite.add_child(slot_pick)
	var slice_pick := OptionButton.new()
	for sid in shop.get("slices", []):
		slice_pick.add_item(String(sid))
	overwrite.add_child(slice_pick)
	overwrite.add_child(_button("Overwrite", func() -> void: overwrite_slice(slot_pick.selected, slice_pick.selected)))
	cards_win.body.add_child(overwrite)
	mid.add_child(_button("Leave the Modem", leave_shop))
	var side := VBoxContainer.new()
	side.add_theme_constant_override("separation", 14)
	side.custom_minimum_size.x = 200
	outer.add_child(side)
	var notes := TerminalWindow.new("SHOP NOTES")
	for line in ["> Limited stock", "> No refunds", "> Better chips", "> Better runs"]:
		notes.body.add_child(_label(line))
	side.add_child(notes)
	side.add_child(GraffitiScrawl.new("UPGRADE\nOR DIE!", -8.0, 30))
	var inv := TerminalWindow.new("INVENTORY", Palette.CELL_ACID)
	var installed := 0
	for fw in op.slot_firmware_ids:
		if fw != &"":
			installed += 1
	inv.body.add_child(_label("CHIPS    %d" % (installed + op.daemon_ids.size())))
	inv.body.add_child(_label("CARDS    %d" % op.deck.size()))
	inv.body.add_child(_label("CYCLES   %d" % s.run.cycles))
	side.add_child(inv)
	_set_panel(outer, false)


## Mid-run raid interlude (GDD 4.4, 7.3): setup with exact projection, run assets and
## the Armory both deployable, then the playout.
func _show_raid() -> void:
	var s := RunManager.netrun
	var c := s.campaign
	var pending := s.raid_pending()
	var raid := CampaignRules.raid_data(pending, s.lookup)
	var projection := s.raid_projection()
	var box := VBoxContainer.new()
	box.add_child(_label("RAID INTERLUDE - %s: %s" % [raid.display_name, raid.warning_text]))
	box.add_child(_label("Projection: %s, home %d -> %d, %d threats destroyed, %d steps" % [
		"HOLDS" if projection.won else ("CAMPAIGN LOST" if projection.campaign_lost else "breached"),
		projection.home_before, projection.home_after, projection.threats_destroyed, projection.steps_run]))
	var run_assets := s.run_assets()
	for site_id in c.grid.claimed_ids():
		var row := HFlowContainer.new()  # wraps inside the 1280 screen (horizontal pass 10)
		var n: Dictionary = projection.nodes.get(String(site_id), {})
		row.add_child(_label("%s (%s) %s -> %s [%s] assets: %s" % [site_id, c.grid.node_type_of(site_id), n.get("before", "?"), n.get("after", "?"),
			String(n.get("outcome", "?")).to_upper(), ", ".join(c.grid.assets_on(site_id))]))
		var deployed := c.grid.assets_on(site_id)
		for i in deployed.size():
			var idx := i
			var sid := site_id
			row.add_child(_button("Withdraw %s" % deployed[i], func() -> void: raid_move(sid, idx, &"")))
		if c.grid.is_active_node(site_id):
			if not run_assets.is_empty():
				var pick := OptionButton.new()
				for a in run_assets:
					pick.add_item("run: %s" % a)
				row.add_child(pick)
				var sid2 := site_id
				row.add_child(_button("Deploy run asset", func() -> void: raid_deploy_run_asset(pick.selected, sid2)))
			if not c.armory.is_empty():
				var pick2 := OptionButton.new()
				for a in c.armory:
					pick2.add_item("armory: %s" % a)
				row.add_child(pick2)
				var sid3 := site_id
				row.add_child(_button("Deploy armory asset", func() -> void: raid_deploy_armory(pick2.selected, sid3)))
		box.add_child(row)
	box.add_child(_button("RUN THE RAID", raid_fight))
	_set_panel(box)


func _show_end() -> void:
	var s := RunManager.netrun
	var box := VBoxContainer.new()
	var won := s.run.outcome == RunState.Outcome.COMPLETED
	var aborted := s.run.outcome == RunState.Outcome.ABORTED
	var head := HBoxContainer.new()
	head.add_child(ZineStamp.new("CLEAN EXIT" if won else ("ABORTED" if aborted else "FLATLINED"), Palette.CELL_ACID if won else Palette.CELL_PINK))
	var title := "NETRUN COMPLETE" if won else ("NETRUN ABORTED - the home server fell" if aborted else "NETRUN FAILED - operative lost")
	var note := ZineNote.new(title, Vector2(620, 130))
	note.append("Combats won %d, elites %d, Cycles %d, banked Schematics %d, Heat gained %d." % [s.run.combats_won, s.run.elites_defeated, s.run.cycles, s.run.banked_schematics, s.run.heat_gained])
	note.append("Campaign: Heat %d, Schematics %d, Armory %d." % [s.campaign.heat, s.campaign.schematics, s.campaign.armory.size()])
	head.add_child(note)
	box.add_child(head)
	box.add_child(_button("Back to HQ", finish_run))
	_set_panel(box)


# --- Helpers --------------------------------------------------------------------------

func _refresh_status() -> void:
	var c := RunManager.campaign
	if c == null:
		_status.text = "No campaign."
		return
	var s := RunManager.netrun
	var text := "Heat %d/%d | Schematics %d | Armory %d" % [c.heat, RunManager.resolver.config.heat_max, c.schematics, c.armory.size()]
	if s != null and not s.run.is_over():
		var op := s.run.operative
		text += " || Run T%d seed %d | %s HP %d/%d Rank %d | Cycles %d | banked %d | node %s" % [s.run.tier, s.run.run_seed, op.name, op.hp, op.max_hp, op.rank, s.run.cycles, s.run.banked_schematics, s.run.current_node_id]
	_status.text = text


func _report(events: Array[Dictionary]) -> void:
	var c := RunManager.campaign
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")
		if c == null:
			continue
		match String(e.get("type", "")):
			"run_start":
				Dialogue.speak("run_start", RC.Voice.DISPATCH, c.corporation_id, &"", c.runs_started)
				if RunManager.netrun != null:
					Dialogue.bark(RunManager.netrun.run.operative.class_id, "jack_in", c.runs_started)
			"run_complete":
				Dialogue.speak("run_complete", RC.Voice.DISPATCH, c.corporation_id, &"", c.runs_completed)
			"run_died":
				Dialogue.speak("run_died", RC.Voice.DISPATCH, c.corporation_id, &"", c.deaths)
			"rack_captured":
				Dialogue.speak("rack", RC.Voice.DISPATCH, c.corporation_id, &"", c.runs_started)
			"heat_threshold":
				Dialogue.threshold_line(c.corporation_id, int(e.get("heat", 0)), c.campaign_seed)
			"raid_interlude":
				Dialogue.raid_warning(c.corporation_id, StringName(String(e.get("queued_raid_id", e.get("raid_id", "")))), c.raids_won + c.raids_lost)


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
	if event.is_action_pressed("open_settings") and combat_scene == null:
		open_settings()
		get_viewport().set_input_as_handled()
		return
	if map_view != null and is_instance_valid(map_view) and RunManager.netrun != null and RunManager.netrun.run.phase == RunState.Phase.MAP:
		var available := RunManager.netrun.available_nodes()
		for i in mini(9, available.size()):
			if event.is_action_pressed("card_%d" % (i + 1)):
				enter_node(available[i])
				get_viewport().set_input_as_handled()
				return


func _build_ui() -> void:
	background = WireframeBackground.new()
	add_child(background)
	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(root)
	hud = HudBar.new()
	root.add_child(hud)
	_status = hud.label
	# Tall panels (a raid with many claimed Sites) scroll vertically; never sideways.
	var scroll := ScrollContainer.new()
	scroll.follow_focus = true
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
	_log.custom_minimum_size = Vector2(0, 110)
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
