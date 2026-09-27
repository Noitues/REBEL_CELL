extends Control
## Functional M2 netrun scene (placeholder look): start screen, map, combat (embedded
## CombatScene), rewards, Terminal events, Modem shop and the run summary. Every
## action goes through RunManager's NetrunSession; the scene only displays state.

const COMBAT_SCENE := preload("res://scenes/combat/combat_scene.tscn")
## What each route node holds (the route buttons' tooltips).
const NODE_TIPS := {RC.InfilNodeType.ROUTER: "Router: a fight. Win it for Cycles and loot.",
	RC.InfilNodeType.TERMINAL: "Terminal: an event with choices.",
	RC.InfilNodeType.MODEM: "Modem: the cyber shop (cards, Firmware, Daemons, slices, card removal).",
	RC.InfilNodeType.SERVER_RACK: "Server Rack: the Site's guardian. Breach it to complete the run."}

## What each route node is, in a word (H21 #14: two "Router" buttons looked the same) and
## as an icon; an elite Router is an "Elite fight" with the crown.
const NODE_WORDS := {RC.InfilNodeType.ROUTER: "Fight", RC.InfilNodeType.TERMINAL: "Event",
	RC.InfilNodeType.MODEM: "Shop", RC.InfilNodeType.SERVER_RACK: "Rack"}
const NODE_ICONS := {RC.InfilNodeType.ROUTER: StatIcon.FIGHT, RC.InfilNodeType.TERMINAL: StatIcon.TERMINAL,
	RC.InfilNodeType.MODEM: StatIcon.SHOP, RC.InfilNodeType.SERVER_RACK: StatIcon.RACK}
const ELITE_WORD := "Elite fight"
## The pause menu's least top (px); it opens under the subtitle band.
const PAUSE_TOP := 100.0
## A reachable route node's colour on the map (route_graph) and on its button's icon.
const ROUTE_NEXT_COLOR := Palette.CELL_ACID
## The home server's name (as the HQ shows it; never its id).
const HOME_LABEL := "CORE"
## The Modem's quadrant (px) and the room its window frame and title take (px): shop cards
## grow with the text size only as far as a quadrant holds them (H21 #15).
const MODEM_QUAD := Vector2(490, 250)
const QUAD_FRAME := Vector2(24, 56)
const QUAD_GAP := 12.0
## LEAVE THE MODEM (in the free corner of the REMOVE A CARD quadrant, so the Modem ends
## on screen at text scale 1.6) and its exit icon beside it (px).
const LEAVE_AT := Vector2(900, 440)
const LEAVE_ICON := 34.0
## Loot stickers at text scale 1.0 and the most a row of them may grow (px).
const LOOT_CARD := Vector2(150, 170)
const LOOT_ROW_MAX := 900.0

var _status: Label
## Top strip: screen title and the status line (`_status`).
var hud: HudBar
## The subtitles' band under the top bar (H21 #11); hidden while a fight docks its own.
var subtitle_strip: SubtitleStrip
## The route drawn on the city (map phase) and whether it is zoomed out to the Grid.
var city_overlay: CityMapOverlay = null
var _grid_zoomed: bool = false
var _panel_host: PanelContainer
var _log: RichTextLabel
var _panel: Control = null
var combat_scene: Control = null
var background: WireframeBackground
var map_view: NetrunMapView = null
var playout: RaidPlayoutPanel = null
var _spoken_events: Dictionary = {}
var _settings_panel: PauseMenu = null
## The route's node buttons (their key hints follow the device).
var _route_buttons: Array[Button] = []
## The route view's map key (placed clear of the nodes; null when zoomed out).
var route_legend: MapLegend = null

## Event types that pop a toast (H20: the log strip is optional).
const TOAST_WARN_EVENTS: Array[String] = ["refused", "deploy_failed", "undock_failed"]


func _ready() -> void:
	UiTheme.apply(self)
	# Subtitles sit in the top band, clear of every control (H20); combat docks its own.
	Dialogue.dock_default()
	Settings.hints_changed.connect(_relabel_route)
	_build_ui()
	var args := OS.get_cmdline_user_args()
	for a in args:
		# Design review: portrait and slice-icon styles.
		if a.begins_with("--demo-portrait="):
			PortraitArt.style = int(a.trim_prefix("--demo-portrait="))
		elif a.begins_with("--demo-iconstyle="):
			SliceIcon.style = int(a.trim_prefix("--demo-iconstyle="))
	if args.has("--demo-shop"):
		RunManager.save_slot = "demo"
		new_campaign(1)
		start_run(1)
		RunManager.netrun.run.cycles = 120
		RunManager.netrun._open_shop()
		_show_current()
		if args.has("--demo-deckview"):
			open_remove()
			(get_node("DeckView") as DeckView).select(2)
		elif args.has("--demo-carddetail"):
			open_remove()
			(get_node("DeckView") as DeckView).open_card.call_deferred(2)
		elif args.has("--demo-spinnerview"):
			open_overwrite(1)
			(get_node("SpinnerView") as SpinnerView).select(2)
		elif args.has("--demo-loadout"):
			open_loadout()
		elif args.has("--demo-daemons"):
			RunManager.netrun.run.operative.daemon_ids.append_array([&"twin_pointer", &"shield_cache", &"zero_day", &"feedback_loop"])
			_refresh_status()
			open_daemons()
			(get_node("DaemonTray") as DaemonTray).show_card(&"shield_cache", false)
		elif args.has("--demo-spinnergrid"):
			open_overwrite(1)
		elif args.has("--demo-deckgrid"):
			open_remove()
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
	if args.has("--demo-gridzoom"):
		_grid_zoomed = true
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
	# A fight docks its subtitles in its own column and needs the height (H21 #11).
	subtitle_strip.visible = not p.has_method("attach_netrun")
	hud.stats.max_height = HudBar.BAND_HEIGHT if p.has_method("attach_netrun") else 0.0
	_panel_host.theme_type_variation = &"GlassPanel" if glass else &""
	_clear_route()
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_STOP
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
		background.corp_creep = clampf(RunManager.campaign.heat / float(RunManager.config().heat_max), 0.0, 1.0)
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
		box.add_child(_icon_button("Resume saved game", resume, StatIcon.CONTINUE))
	if RunManager.campaign != null:
		var living := RunManager.campaign.living_operatives()
		var info := "Campaign: Heat %d, Schematics %d, roster %d living." % [RunManager.campaign.heat, RunManager.campaign.schematics, living.size()]
		box.add_child(_label(info))
		for op in living:
			box.add_child(_label("  %s (%s) Rank %d, HP %d/%d, deck %d, daemons %d" % [op.name, _content_name(op.class_id), op.rank, op.hp, op.max_hp, op.deck.size(), op.daemon_ids.size()]))
		if RunManager.has_active_run():
			box.add_child(_icon_button("Continue the current run", _show_current, StatIcon.CONTINUE))
		elif not living.is_empty():
			box.add_child(_icon_button("Start a netrun at the first open Site", func() -> void: start_run(1), StatIcon.PLAY))
		box.add_child(_icon_button("Go to HQ (City Grid, raids, roster)", RunManager.go_to_hq, StatIcon.BACK))
	_set_panel(box)


## The netrun map as a wireframe graph (GDD 9.1): click a reachable node to enter it.
## Keyboard: 1-9 pick the reachable nodes in order.
func _show_map() -> void:
	var s := RunManager.netrun
	# The route on the city in blueprint, zoomed into the target Site's neighbourhood;
	# GRID VIEW zooms out to the whole campaign Grid (greyed city). `map_view` stays as the
	# route model (hidden): pad keys and clicks go through it as before.
	var panel := VBoxContainer.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var top := HBoxContainer.new()
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	panel.add_child(top)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(spacer)
	map_view = NetrunMapView.new()
	map_view.visible = false
	map_view.corp_color = Palette.corp_color(RunManager.campaign.corporation_id)
	map_view.show_map(s.run.map, s.run.current_node_id, s.run.visited, s.available_nodes(), s.map_heat())
	map_view.node_clicked.connect(func(id: StringName) -> void:
		if RunManager.netrun != null and RunManager.netrun.available_nodes().has(id):
			enter_node(id))
	top.add_child(map_view)
	# The number keys pick nodes on the keyboard; the pad has none, so its hints are blank
	# (H20: each button carries its own key hint, refreshed when the device changes).
	var win := TerminalWindow.new("ROUTE // pick the next node", Palette.CELL_ACID)
	win.custom_minimum_size.x = 300
	win.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	# The route column: the choices, then the map key under them (H22 #14: the route view
	# had none; in the column it hides no part of the route).
	var route_col := VBoxContainer.new()
	route_col.name = "RouteColumn"
	route_col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	route_col.add_theme_constant_override("separation", 8)
	top.add_child(route_col)
	route_col.add_child(win)
	var available := s.available_nodes()
	var row := VBoxContainer.new()
	row.name = "RouteNodes"
	win.body.add_child(row)
	_route_buttons.clear()
	for i in available.size():
		var node := s.run.map.get_node(available[i])
		# H21 #14: what the node is (word + icon), its index on every device (the map's
		# label carries the same index), Heat when entering changes it.
		var text := node_word(node)
		var heat := s.node_heat(available[i])
		if heat != 0:
			text += " %+d Heat" % heat
		var id: StringName = available[i]
		var b := _button(text, func() -> void: enter_node(id))
		b.name = "Node%d" % (i + 1)
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.set_meta(&"route_base", text)
		b.set_meta(&"route_index", i)
		IconMark.attach(b, node_icon(node), StatIcon.color_of(node_icon(node)))
		# H22 #14: the node's own map icon (the map's painter, its colour for a next node),
		# so the same node looks the same on the button and on the map.
		IconMark.attach_map(b, CityMapOverlay.route_kind(int(node["type"]), bool(node["elite"])), ROUTE_NEXT_COLOR)
		b.tooltip_text = UiTip.fold(String(NODE_TIPS.get(node["type"], "")) + (" Elite: a harder fight." if _is_elite(node) else "") + ((" Entering it changes Heat by %+d." % heat) if heat != 0 else ""))
		_route_buttons.append(b)
		row.add_child(b)
	_label_route_buttons()
	var zoom_btn := _button("GRID VIEW" if not _grid_zoomed else "ROUTE VIEW", func() -> void:
		_grid_zoomed = not _grid_zoomed
		_show_map())
	zoom_btn.name = "GridZoom"
	zoom_btn.tooltip_text = UiTip.fold("Zoom out to the whole City Grid." if not _grid_zoomed else "Back to this run's route.")
	IconMark.attach(zoom_btn, StatIcon.MAP)
	win.body.add_child(zoom_btn)
	var quit_btn := _button("Save & quit to start screen", save_and_quit)
	quit_btn.name = "SaveQuit"
	quit_btn.tooltip_text = UiTip.fold("Save the run and leave it; Continue picks it up here.")
	IconMark.attach(quit_btn, StatIcon.SAVE)
	win.body.add_child(quit_btn)
	if _grid_zoomed:
		win.body.add_child(MapLegend.new(RunManager.campaign.corporation_id))
	else:
		# The route view's map key (H22 #14: it had none) in the room under the choices,
		# scaled down if that room is short (LegendSpot).
		top.size_flags_vertical = Control.SIZE_EXPAND_FILL
		route_col.size_flags_vertical = Control.SIZE_EXPAND_FILL
		var key_room := Control.new()
		key_room.name = "LegendRoom"
		key_room.mouse_filter = Control.MOUSE_FILTER_IGNORE
		key_room.size_flags_vertical = Control.SIZE_EXPAND_FILL
		route_col.add_child(key_room)
		route_legend = MapLegend.pin_to(key_room, RunManager.campaign.corporation_id)
	_set_panel(panel, false)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if _grid_zoomed:
		var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, CityLayout.threat_paths(RunManager.campaign, RunManager.corporation), s.run.site_id)
		_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, 0.85, Vector2(0.4, 0.56), Vector2.INF)
		city_overlay.avoid_controls([win])  # map labels stay clear of the ROUTE window
	else:
		var r := route_graph()
		_mount_route(r["nodes"], r["edges"], CityMapOverlay.Look.ISOLATE, 1.45, Vector2(0.46, 0.58), Vector2.INF)
		city_overlay.avoid_controls([win, route_legend])
		route_legend.minimum_size_changed.connect(func() -> void: place_route_legend.call_deferred())
		city_overlay.node_clicked.connect(func(id: StringName) -> void: map_view.node_clicked.emit(id))
		place_route_legend.call_deferred()
		route_legend.get_parent().resized.connect(place_route_legend)
		if not background.city.rebuilt.is_connected(place_route_legend):
			background.city.rebuilt.connect(place_route_legend)


## The route legend where it covers no route node (H22 #14).
func place_route_legend() -> void:
	if route_legend != null and is_instance_valid(route_legend) and city_overlay != null and is_instance_valid(city_overlay):
		LegendSpot.place(route_legend, city_overlay)


## A route node in a word: Fight, Elite fight, Event, Shop, Rack.
static func node_word(node: Dictionary) -> String:
	return ELITE_WORD if _is_elite(node) else String(NODE_WORDS.get(node["type"], "?"))


## A route node's icon: crosshair, crown (elite), terminal, bag (shop), server rack.
static func node_icon(node: Dictionary) -> StringName:
	return StatIcon.ELITE if _is_elite(node) else StringName(NODE_ICONS.get(node["type"], &""))


static func _is_elite(node: Dictionary) -> bool:
	return bool(node["elite"]) and int(node["type"]) == RC.InfilNodeType.ROUTER


## The index route choice `i` shows on its button and its map label: the key that picks it
## on the keyboard ("[1]"), its number on a pad (H21 #14: the pad's labels were identical).
static func route_index_text(i: int) -> String:
	var hint := Settings.hint(StringName("card_%d" % (i + 1))) if i < 9 else ""
	return hint if hint != "" else str(i + 1)


## "[1] Fight" on the keyboard, "1 Fight" on a pad: the route's index follows the device
## and the binds.
func _relabel_route() -> void:
	_label_route_buttons()
	# The map's node labels carry the same hints.
	if not _route_buttons.is_empty() and not _grid_zoomed and city_overlay != null and is_instance_valid(city_overlay) and RunManager.netrun != null:
		var r := route_graph()
		city_overlay.set_graph(r["nodes"], r["edges"])


func _label_route_buttons() -> void:
	var alive: Array[Button] = []
	for b in _route_buttons:
		if not is_instance_valid(b) or b.is_queued_for_deletion():
			continue
		b.text = "%s %s" % [route_index_text(int(b.get_meta(&"route_index"))), String(b.get_meta(&"route_base"))]
		alive.append(b)
	_route_buttons = alive


## The run's map as buildings in the target Site's neighbourhood (layers step in from
## the street towards the Site).
func route_graph() -> Dictionary:
	var s := RunManager.netrun
	var map := s.run.map
	var target: Vector2 = CityLayout.site_points(RunManager.corporation).get(s.run.site_id, NeonCity.hq_of(RunManager.corporation.id))
	var layers := map.layer_count()
	var available := s.available_nodes()
	var type_glyph := {RC.InfilNodeType.ROUTER: "○", RC.InfilNodeType.TERMINAL: "▭", RC.InfilNodeType.MODEM: "◇", RC.InfilNodeType.SERVER_RACK: "⬢"}
	var rows := {}
	for n in map.all_nodes():
		rows[int(n["layer"])] = maxi(int(rows.get(int(n["layer"]), 0)), int(n["index"]) + 1)
	var nodes: Array[Dictionary] = []
	for n in map.all_nodes():
		var li := int(n["layer"])
		var count := int(rows[li])
		var at := target - CityLayout.RIGHT * (layers - li) * 1.7 + CityLayout.DOWN * (int(n["index"]) - (count - 1) * 0.5) * 2.2
		var col := Palette.NET_CYAN
		if n["id"] == s.run.current_node_id:
			col = Palette.CELL_PINK
		elif available.has(n["id"]):
			col = ROUTE_NEXT_COLOR
		elif s.run.visited.has(n["id"]):
			col = Color(Palette.NET_CYAN, 0.5)
		elif n["elite"] or n["type"] == RC.InfilNodeType.SERVER_RACK:
			col = Palette.corp_color(RunManager.campaign.corporation_id)
		var idx := available.find(n["id"])
		# The reachable nodes carry their route button's index and word (H21 #14); "kind"
		# is the StatIcon the button shows.
		nodes.append({"id": n["id"], "at": at, "color": col, "glyph": type_glyph.get(int(n["type"]), "?"),
			"label": "%s %s" % [route_index_text(idx), node_word(n)] if idx >= 0 else "", "big": n["type"] == RC.InfilNodeType.SERVER_RACK,
			"tip": "%s: %s" % [node_word(n), String(NODE_TIPS.get(n["type"], ""))],
			# The map paints its own node icons (CityMapOverlay); the route buttons draw the same
			# kind with the same painter (H22 #14).
			"kind": CityMapOverlay.route_kind(int(n["type"]), n["elite"]), "icon": node_icon(n),
			"here": n["id"] == s.run.current_node_id, "next": idx >= 0})
	var edges: Array[Dictionary] = []
	for n in map.all_nodes():
		for nxt in n["next"]:
			var live: bool = n["id"] == s.run.current_node_id and available.has(nxt)
			edges.append({"a": n["id"], "b": nxt, "color": Palette.CELL_ACID if live else Color(Palette.NET_CYAN, 0.45), "width": 3.0 if live else 1.6, "dashed": not live, "flow": live})
	return {"nodes": nodes, "edges": edges}


func _mount_route(nodes: Array[Dictionary], edges: Array[Dictionary], look: int, zoom: float, anchor: Vector2, focus: Vector2) -> void:
	_clear_route()
	var city := background.city
	city_overlay = CityMapOverlay.new(city)
	city.add_child(city_overlay)
	city_overlay.set_look(look)
	city_overlay.set_graph(nodes, edges)
	city.scale = Vector2(zoom, zoom)
	city.offset_left = 0
	city.offset_top = 0
	city.offset_right = size.x / zoom - size.x
	city.offset_bottom = size.y / zoom - size.y
	city.focus_grid = city_overlay.centre() if focus == Vector2.INF else focus
	city.focus_anchor = anchor
	city.refresh()


func _clear_route() -> void:
	if city_overlay != null and is_instance_valid(city_overlay):
		city_overlay.queue_free()
	city_overlay = null
	var city := background.city
	if city.focus_grid != Vector2.INF or city.scale != Vector2.ONE:
		city.focus_grid = Vector2.INF
		city.scale = Vector2.ONE
		city.offset_right = 0
		city.offset_bottom = 0
		city.refresh()


## Raid playout (GDD 7.2): threat markers animate over the Grid; 1x/2x/4x and skip. The
## raid plays on the city (the Grid overlay, like the HQ playout), the feed at the side.
func _show_raid_playout(events: Array[Dictionary]) -> void:
	var c := RunManager.campaign
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
	playout = RaidPlayoutPanel.new(null, Vector2(330, 330))
	feed.body.add_child(playout)
	var cont := _icon_button("Continue", _show_current, StatIcon.CONTINUE)
	cont.disabled = true
	playout.finished.connect(func() -> void: cont.disabled = false)
	side.add_child(cont)
	_set_panel(box, false)
	(_panel_host.get_parent() as Control).mouse_filter = Control.MOUSE_FILTER_IGNORE
	_panel_host.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var g := CityLayout.grid_graph(c, RunManager.corporation, CityLayout.threat_paths(c, RunManager.corporation))
	_mount_route(g["nodes"], g["edges"], CityMapOverlay.Look.ISOLATE, 0.85, Vector2(0.4, 0.56), Vector2.INF)
	city_overlay.avoid_controls([side])
	playout.grid_view = city_overlay
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
		slot_option.name = "SlotPick"
		for i in s.run.operative.slot_slice_ids.size():
			slot_option.add_item(slot_name(s.run.operative, i))
		slot_option.tooltip_text = "The spinner slot the Firmware chip goes into."
		row.add_child(slot_option)
		box.add_child(row)
	# Offers as zine stickers (STYLE_GUIDE 4): cards show their RAM cost and what they do as
	# pictograms, others none. They grow with the text size as far as the row allows (H21).
	var stickers := HBoxContainer.new()
	stickers.name = "Stickers"
	stickers.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	stickers.add_theme_constant_override("separation", 14)
	box.add_child(stickers)
	var n: int = offer["options"].size()
	var ls := clampf(minf(Settings.text_scale, (LOOT_ROW_MAX - 14.0 * (n - 1)) / maxf(1.0, n * LOOT_CARD.x)), 1.0, Settings.TEXT_SCALE_MAX)
	for i in n:
		var id := StringName(String(offer["options"][i]))
		var res := s.lookup.get_content(id)
		var cost := int(res.get("ram_cost")) if res is CardData else -1
		var sticker := ZineCard.new(TextDb.t(res, "display_name"), cost, TextDb.t(res, "description"), i).scaled(ls)
		if res is CardData:
			sticker.with_card(res as CardData)
		sticker.custom_minimum_size = LOOT_CARD * ls
		sticker.hotkey = ""  # rewards are picked by click or focus, not number keys
		sticker.tooltip_text = UiTip.fold(Codex.describe(res))
		var index: int = i
		sticker.pressed.connect(func() -> void: choose_reward(index, slot_option.selected if slot_option != null else -1))
		stickers.add_child(sticker)
	var skip := _button("Skip", skip_reward)
	skip.name = "Skip"
	skip.tooltip_text = "Take nothing from this payout."
	IconMark.attach(skip, StatIcon.SKIP)
	box.add_child(skip)
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
		# H21 #13: the outcome as icons with numbers under the words (Heat as it applies);
		# H22 #12: the amounts it will really apply (a heal at full HP, Heat at 0).
		var outcome := OutcomeRow.of_choice(s, c)
		var costs := OutcomeRow.words(outcome)
		b.text = _choice_text(TextDb.t(c, "label"), costs)
		var err := s.choice_error(c)
		b.disabled = err != ""
		var tip := err if err != "" else (("Costs: %s." % costs) if costs != "" else "")
		if not outcome.is_empty():
			tip += ("\n" if tip != "" else "") + OutcomeRow.describe(outcome)
		b.tooltip_text = UiTip.fold(tip)
		var index := i
		b.name = "Choice%d" % (i + 1)
		b.pressed.connect(func() -> void: choose_event(index))
		b.theme_type_variation = &"NoteButton"
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		options.add_child(b)
		if not outcome.is_empty():
			OutcomeRow.attach(b, OutcomeRow.new(outcome))
	options.add_child(GraffitiScrawl.new("PLAY IT\nSAFE??", -6.0, 24))
	_set_panel(box, false)


## A spinner slot by what is in it, never by ids (H21 #12: "crit_12" in the socket list):
## "Slot 2: ATK 10 + Barbed Wire".
static func slot_name(op: OperativeState, k: int) -> String:
	var lookup := RunManager.lookup()
	var sd := lookup.get_content(op.slot_slice_ids[k]) as SliceData
	var slice := "?"
	if sd != null:
		slice = String(Palette.SLICE_NAMES.get(sd.slice_type, "?")) + ((" %d" % sd.base_output) if sd.base_output > 0 else "")
	var fw_id: StringName = op.slot_firmware_ids[k] if k < op.slot_firmware_ids.size() else &""
	var fw: Resource = lookup.get_content(fw_id) if fw_id != &"" else null
	return "Slot %d: %s%s" % [k + 1, slice, (" + %s" % TextDb.t(fw, "display_name")) if fw != null else ""]


## A Terminal choice's label with its costs from the data, replacing the hand-written
## "(...)" summary so a hidden or unscaled cost can't slip through.
static func _choice_text(label: String, costs: String) -> String:
	var base := label
	var open := base.rfind(" (")
	if open > 0 and base.ends_with(")"):
		base = base.substr(0, open)
	return base if costs == "" else "%s (%s)" % [base, costs]


## Modem (GDD 11.2) in four quadrants over the storefront: MICROCHIPS (Firmware, top
## left), CARDS (as their own stickers, top right), SLICES + DAEMONS (bottom left, split)
## and REMOVE A CARD (bottom right, opens the deck viewer). Overwriting a slice opens the
## spinner viewer to pick the slot. "Leave the Modem" is a dripping tag in the corner.
func _show_shop() -> void:
	var s := RunManager.netrun
	var shop := s.run.shop
	var op := s.run.operative
	var root := Control.new()
	root.name = "ModemRoot"
	root.custom_minimum_size = Vector2(1240, 540)
	var sign := ModemSign.new()
	sign.name = "ModemSign"
	sign.position = Vector2(0, -6)
	sign.size = Vector2(230, 560)
	root.add_child(sign)
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	grid.position = Vector2(236, 0)
	root.add_child(grid)
	var q_size := MODEM_QUAD
	var ts := Settings.text_scale
	# Top left: microchips (Firmware). The socket list names each slot by its slice.
	var fw_slot := OptionButton.new()
	fw_slot.name = "SocketPick"
	for k in op.slot_slice_ids.size():
		fw_slot.add_item("Socket into %s" % slot_name(op, k))
	var chips_win := TerminalWindow.new("MICROCHIPS")
	chips_win.custom_minimum_size = q_size
	grid.add_child(chips_win)
	var chips := HBoxContainer.new()
	chips.name = "Chips"
	chips.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	chips.add_theme_constant_override("separation", 10)
	chips_win.body.add_child(chips)
	# Top right: cards as their stickers ("Stickers" holds them in stock order).
	var cards_win := TerminalWindow.new("CARDS", Palette.CELL_PINK)
	cards_win.custom_minimum_size = q_size
	grid.add_child(cards_win)
	var stickers := HBoxContainer.new()
	stickers.name = "Stickers"
	stickers.add_theme_constant_override("separation", 12)
	cards_win.body.add_child(stickers)
	# Bottom left: slices (overwrite) and daemons side by side.
	# A 2-column grid (not an HBox) so pad focus walks every tile in both windows.
	var lower_left := GridContainer.new()
	lower_left.columns = 2
	lower_left.add_theme_constant_override("h_separation", 12)
	lower_left.custom_minimum_size = q_size
	grid.add_child(lower_left)
	var slices_win := TerminalWindow.new("SLICES", Palette.CRT_AMBER)
	slices_win.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lower_left.add_child(slices_win)
	var daemons_win := TerminalWindow.new("DAEMONS", Palette.NEON_VIOLET)
	lower_left.add_child(daemons_win)
	var daemon_row := HBoxContainer.new()
	daemon_row.name = "Daemons"
	daemons_win.body.add_child(daemon_row)
	var n := 0
	# Cards grow with the text size as far as their quadrant holds them (H21 #15).
	var card_count: int = shop.get("cards", []).size()
	var card_fit := minf((q_size.x - QUAD_FRAME.x - QUAD_GAP * maxi(0, card_count - 1)) / maxf(1.0, card_count * ZineCard.STICKER_SIZE.x),
		(q_size.y - QUAD_FRAME.y) / ZineCard.STICKER_SIZE.y)
	var cs := clampf(minf(ts, card_fit), 1.0, Settings.TEXT_SCALE_MAX)
	for kind in ["cards", "firmware", "daemons"]:
		var prices: Array = shop.get(kind.trim_suffix("s") + "_prices", [])
		for i in shop.get(kind, []).size():
			var id := StringName(String(shop[kind][i]))
			var res := s.lookup.get_content(id)
			# H21 #12: the circle shows a card's real RAM cost; the price hangs on a tag with
			# the coin.
			var ram := (res as CardData).ram_cost if res is CardData else -1
			var sticker := ZineCard.new(TextDb.t(res, "display_name"), ram, TextDb.t(res, "description") if kind == "cards" else "%s: %s" % [kind.trim_suffix("s"), TextDb.t(res, "description")], n)
			sticker.hotkey = ""
			sticker.with_price(int(prices[i]))
			if kind == "cards":
				sticker.scaled(cs).with_card(res as CardData)
			elif kind == "firmware":
				sticker.as_tile(ZineCard.Look.CHIP, Palette.NET_CYAN).tile_text(ts)
			elif kind == "daemons":
				sticker.as_tile(ZineCard.Look.CHIP, Palette.NEON_VIOLET).tile_text(ts)
			sticker.tooltip_text = UiTip.fold("%d Cycles (you have %d)\n%s" % [int(prices[i]), s.run.cycles, Codex.describe(res)])
			sticker.disabled = int(prices[i]) > s.run.cycles
			var index: int = i
			var k: String = kind
			sticker.pressed.connect(func() -> void: buy(k, index, fw_slot.selected if k == "firmware" else -1))
			match kind:
				"cards":
					stickers.add_child(sticker)
				"firmware":
					chips.add_child(sticker)
				_:
					daemon_row.add_child(sticker)
			n += 1
	if not shop.get("firmware", []).is_empty():
		fw_slot.tooltip_text = "The spinner slot a bought Firmware chip goes into."
		chips_win.body.add_child(fw_slot)
	if daemon_row.get_child_count() == 0:
		daemons_win.body.add_child(_label("sold out"))
	var slice_row := HBoxContainer.new()
	slice_row.name = "Slices"
	slice_row.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	slice_row.add_theme_constant_override("separation", 8)
	slices_win.body.add_child(slice_row)
	var stock: Array = shop.get("slices", [])
	# A slice's price depends on the slot it overwrites: the tile shows the lowest ("N+"
	# when some slot costs more).
	var low := -1
	var high := -1
	for k in op.slot_slice_ids.size():
		var p := s.slice_overwrite_price(k)
		low = p if low < 0 else mini(low, p)
		high = maxi(high, p)
	for i in stock.size():
		var sd := s.lookup.get_content(StringName(String(stock[i]))) as SliceData
		if sd == null:
			continue
		var tile := ZineCard.new("%s %d" % [Palette.SLICE_NAMES.get(sd.slice_type, "?"), sd.base_output] if sd.base_output > 0 else String(Palette.SLICE_NAMES.get(sd.slice_type, "?")), -1, Codex.describe(sd), i)
		tile.as_tile(ZineCard.Look.SLICE_TILE, Palette.slice_color(sd.slice_type)).tile_text(ts)
		tile.slice_type = sd.slice_type
		tile.slice_output = sd.base_output
		tile.custom_minimum_size = Vector2(96, 130)
		tile.hotkey = ""
		if low >= 0:
			tile.with_price(low, high > low)
		tile.tooltip_text = UiTip.fold("Overwrite a slot of your spinner with this slice: %d Cycles%s (you have %d).\n" % [low, (" (%d for a pricier slot)" % high) if high > low else "", s.run.cycles] + Codex.describe(sd))
		var si := i
		tile.pressed.connect(func() -> void: open_overwrite(si))
		slice_row.add_child(tile)
	# Bottom right: remove a card, an icon action that opens the deck viewer.
	var remove_win := TerminalWindow.new("REMOVE A CARD", Palette.CELL_ACID)
	remove_win.custom_minimum_size = q_size
	grid.add_child(remove_win)
	var remove_row := HBoxContainer.new()
	remove_row.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	remove_row.add_theme_constant_override("separation", 16)
	remove_win.body.add_child(remove_row)
	var shred := ZineCard.new("SHRED A CARD", -1, "Pick a card from your deck to remove.", 0)
	shred.as_tile(ZineCard.Look.CARD_TILE, Palette.CELL_ACID).tile_text(ts)
	shred.with_price(s.card_removal_price())
	shred.name = "RemoveCard"
	shred.hotkey = ""
	shred.disabled = s.run.cycles < s.card_removal_price() or op.deck.is_empty()
	shred.icon_kind = "shred"
	shred.tooltip_text = UiTip.fold("Remove a card from your deck: %d Cycles (you have %d)." % [s.card_removal_price(), s.run.cycles])
	shred.pressed.connect(open_remove)
	remove_row.add_child(shred)
	# The wallet (H21 #11): the Cycles to spend, beside the shredder, in sight whatever
	# covers the top bar.
	var wallet := HudStats.new()
	wallet.name = "Wallet"
	wallet.items = [["CYCLES", str(s.run.cycles), "", "Cycles you have to spend in the Modem. Runs and events pay them; they don't leave the run."]]
	wallet.custom_minimum_size.x = wallet.full_width(ts)
	wallet.size_flags_vertical = Control.SIZE_SHRINK_BEGIN
	remove_row.add_child(wallet)
	var leave := DripButton.new("LEAVE THE MODEM", "", DripButton.DRIP_PINK, 32, DripButton.LEAVE_MODEM_DRIPS)
	leave.name = "LeaveModem"
	leave.position = LEAVE_AT
	leave.pressed.connect(leave_shop)
	leave.tooltip_text = "Leave the Modem and go back to the route."
	root.add_child(leave)
	var leave_icon := IconMark.standalone(StatIcon.EXIT, LEAVE_ICON, DripButton.DRIP_PINK)
	leave_icon.name = "LeaveIcon"
	leave_icon.position = LEAVE_AT + Vector2(-LEAVE_ICON - 4.0, 4.0)
	leave_icon.tooltip_text = leave.tooltip_text
	leave_icon.mouse_filter = Control.MOUSE_FILTER_PASS
	root.add_child(leave_icon)
	_set_panel(root, false)


## Opens a modal viewer over the netrun screen. The viewers hold focus themselves
## (UiFocus.hold: the D-pad and A can't reach the Modem behind them; focus returns to the
## tile that opened them on close).
func _open_modal(view: Control) -> void:
	add_child(view)


## Deck viewer in pick mode: the chosen card is removed for the shop's price.
func open_remove() -> void:
	var s := RunManager.netrun
	var view := DeckView.new(s.run.operative.deck, s.lookup, "REMOVE A CARD // %d CYCLES" % s.card_removal_price(), "REMOVE")
	view.card_picked.connect(remove_card)
	_open_modal(view)


## Spinner viewer in pick mode: the chosen slot is overwritten with stock slice `stock_index`.
func open_overwrite(stock_index: int) -> void:
	var s := RunManager.netrun
	var sd := s.lookup.get_content(StringName(String(s.run.shop["slices"][stock_index]))) as SliceData
	var name_text := "%s %d" % [Palette.SLICE_NAMES.get(sd.slice_type, "?"), sd.base_output] if sd != null else "?"
	# The price depends on the slot (the Miss slot costs more): the view shows the picked
	# slot's own price and turns UPGRADE off when it is out of reach (H20).
	var view := SpinnerView.new(s.run.operative.slot_slice_ids, s.run.operative.slot_firmware_ids, s.lookup, "UPGRADE A SLICE // INSTALL %s" % name_text,
		"UPGRADE", RunManager.config().shop_slices)
	view.slot_picked.connect(func(slot: int) -> void: overwrite_slice(slot, stock_index))
	_open_modal(view)
	view.set_prices(s.slice_overwrite_price, s.run.cycles)


## Mid-run raid interlude (GDD 4.4, 7.3): setup with exact projection, run assets and
## the Armory both deployable, then the playout.
func _show_raid() -> void:
	var s := RunManager.netrun
	var c := s.campaign
	var pending := s.raid_pending()
	var raid := CampaignRules.raid_data(pending, s.lookup)
	var projection := s.raid_projection()
	var box := VBoxContainer.new()
	box.add_child(_label("RAID INTERLUDE - %s: %s" % [TextDb.t(raid, "display_name"), TextDb.t(raid, "warning_text")]))
	box.add_child(_label("Projection: %s, home %d -> %d, %d threats destroyed, %d steps" % [
		"HOLDS" if projection.won else ("CAMPAIGN LOST" if projection.campaign_lost else "breached"),
		projection.home_before, projection.home_after, projection.threats_destroyed, projection.steps_run]))
	var run_assets := s.run_assets()
	for site_id in c.grid.claimed_ids():
		var row := HFlowContainer.new()  # wraps inside the 1280 screen (horizontal pass 10)
		var n: Dictionary = projection.nodes.get(String(site_id), {})
		var asset_names := PackedStringArray()
		for a in c.grid.assets_on(site_id):
			asset_names.append(_content_name(a))
		row.add_child(_label("%s (%s) %s -> %s [%s] assets: %s" % [_site_name(site_id), _content_name(c.grid.node_type_of(site_id)), n.get("before", "?"), n.get("after", "?"),
			String(n.get("outcome", "?")).to_upper(), ", ".join(asset_names)]))
		var deployed := c.grid.assets_on(site_id)
		for i in deployed.size():
			var idx := i
			var sid := site_id
			row.add_child(_button("Withdraw %s" % _content_name(deployed[i]), func() -> void: raid_move(sid, idx, &"")))
		if c.grid.is_active_node(site_id):
			if not run_assets.is_empty():
				var pick := OptionButton.new()
				for a in run_assets:
					pick.add_item("run: %s" % _content_name(a))
				row.add_child(pick)
				var sid2 := site_id
				row.add_child(_button("Deploy run asset", func() -> void: raid_deploy_run_asset(pick.selected, sid2)))
			if not c.armory.is_empty():
				var pick2 := OptionButton.new()
				for a in c.armory:
					pick2.add_item("armory: %s" % _content_name(a))
				row.add_child(pick2)
				var sid3 := site_id
				row.add_child(_button("Deploy armory asset", func() -> void: raid_deploy_armory(pick2.selected, sid3)))
		box.add_child(row)
	var run_btn := _button("RUN THE RAID", raid_fight)
	IconMark.attach(run_btn, StatIcon.RAIDS)
	box.add_child(run_btn)
	_set_panel(box)


## A content id's translated display name (the id only when there is no such content).
func _content_name(id: Variant) -> String:
	var res := RunManager.lookup().get_content(StringName(String(id)))
	return TextDb.t(res, "display_name") if res != null and "display_name" in res else String(id)


## A Site's translated name (CORE for the home server).
func _site_name(site_id: StringName) -> String:
	var c := RunManager.campaign
	if c != null and c.grid != null and site_id == c.grid.home_site_id:
		return HOME_LABEL
	var sd := CampaignRules.site_data(RunManager.corporation, site_id) if RunManager.corporation != null else null
	return TextDb.t(sd, "display_name") if sd != null else String(site_id)


func _show_end() -> void:
	var s := RunManager.netrun
	var box := VBoxContainer.new()
	var won := s.run.outcome == RunState.Outcome.COMPLETED
	var aborted := s.run.outcome == RunState.Outcome.ABORTED
	var head := HBoxContainer.new()
	head.add_theme_constant_override("separation", 18)
	# The result stamp only shows the outcome: no focus, no clicks (H20).
	var stamp := ZineStamp.new("CLEAN EXIT" if won else ("ABORTED" if aborted else "FLATLINED"), Palette.CELL_ACID if won else Palette.CELL_PINK).display_only()
	stamp.name = "ResultStamp"
	head.add_child(stamp)
	var title := "NETRUN COMPLETE" if won else ("NETRUN ABORTED - the home server fell" if aborted else "NETRUN FAILED - operative lost")
	var report := TerminalWindow.new(title, Palette.CELL_ACID if won else Palette.CELL_PINK)
	report.name = "RunReport"
	head.add_child(report)
	# The run in numbers as the top bar's paper tags (H20: no text summary).
	var tags := HudStats.new()
	tags.name = "RunTags"
	tags.items = [["COMBATS", str(s.run.combats_won), "", "Fights won this run."],
		["ELITES", str(s.run.elites_defeated), "", "Elite fights won."],
		["CYCLES", str(s.run.cycles), "", "Cycles in hand when the run ended."],
		["BANKED", str(s.run.banked_schematics), "", "Schematics the run banked for the campaign."],
		["HEAT", "%+d" % s.run.heat_gained, "", "Heat the run added (campaign Heat is now %d)." % s.campaign.heat]]
	# The least room the tags need; they grow with the text size where the window allows.
	tags.custom_minimum_size.x = tags.compact_width(1.0)
	report.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	report.body.add_child(tags)
	box.add_child(head)
	var back := _button("Back to HQ", finish_run)
	back.tooltip_text = UiTip.fold("Back to HQ: the campaign, the City Grid and the crew.")
	IconMark.attach(back, StatIcon.BACK)
	box.add_child(back)
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
	# Every tag says what it means on hover (H21 #9); its icon is the resource's own.
	var stats := [["HEAT", str(c.heat), "/%d" % RunManager.resolver.config.heat_max, "Heat: how hard the corporation hunts the Cell. Thresholds add raids and harder rules."],
		["SCHEMATICS", str(c.schematics), "", "Schematics: the campaign's currency, spent at HQ."]]
	if s != null and not s.run.is_over():
		var op := s.run.operative
		stats.append_array([["HP", str(op.hp), "/%d" % op.max_hp, "%s's HP. At 0 the operative flatlines." % op.name],
			["CYCLES", str(s.run.cycles), "", "Cycles: this run's money, spent in the Modem."],
			["CARDS", str(op.deck.size()), "", "Cards in %s's deck (VIEW LOADOUT shows them)." % op.name],
			["RANK", str(op.rank), "", "Rank: runs survived. It brings wheel upgrades and higher netrun tiers."],
			["BANKED", str(s.run.banked_schematics), "", "Schematics this run has banked for the campaign."]])
	hud.set_stats(stats)
	hud.loadout_button.visible = s != null and not s.run.is_over()
	if s != null and not s.run.is_over():
		hud.set_daemons(s.run.operative.daemon_ids)


## The top bar's DAEMONS icon: the running operative's Daemons as a tray of sigils.
func open_daemons() -> void:
	var s := RunManager.netrun
	if s == null or has_node("DaemonTray"):
		return
	var at := hud.daemon_button.get_global_rect().end.x
	add_child(DaemonTray.new(s.run.operative.daemon_ids, s.lookup, at, s.run.operative.name))


## VIEW LOADOUT: the running operative's deck and spinner.
func open_loadout() -> void:
	var s := RunManager.netrun
	if s == null:
		return
	_open_modal(LoadoutView.new(s.run.operative, s.lookup, RunManager.config().shop_slices))


func _report(events: Array[Dictionary]) -> void:
	var c := RunManager.campaign
	for e in events:
		if e.has("text"):
			_log.append_text(String(e["text"]) + "\n")
			if String(e.get("type", "")) in TOAST_WARN_EVENTS:
				ToastNote.show_on(self, String(e["text"]), true)
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
	_settings_panel.position = Vector2((size.x - PauseMenu.MENU_SIZE.x) / 2.0, SubtitleStrip.top_below(PAUSE_TOP))  # under the subtitle band (H22: the top bar grows with its words)
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
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	hud = HudBar.new()
	hud.loadout_pressed.connect(open_loadout)
	hud.daemons_pressed.connect(open_daemons)
	root.add_child(hud)
	_status = hud.label
	subtitle_strip = SubtitleStrip.new()
	root.add_child(subtitle_strip)
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
	# Shown only when the player turns it on in Options.
	_log.visible = Settings.system_log
	Settings.changed.connect(func() -> void: _log.visible = Settings.system_log)


func _label(text: String) -> Label:
	var l := Label.new()
	l.text = text
	return l


func _button(text: String, on_pressed: Callable) -> Button:
	var b := Button.new()
	b.text = text
	b.pressed.connect(on_pressed)
	return b


## A button with a StatIcon before its words (H21 #13).
func _icon_button(text: String, on_pressed: Callable, kind: StringName) -> Button:
	var b := _button(text, on_pressed)
	IconMark.attach(b, kind)
	return b
