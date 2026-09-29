extends GutTest
## H20 screens (GAP_ANALYSIS H20; DECISIONS "H20 screens"): no text logs on the HQ, Grid,
## raid setup and netrun end (badges, cards and the map instead; refusals as toasts); real
## tooltips; subtitles clear of every control at text scale 1.0 and 1.6; pad focus held by
## the Modem / HQ modals; raid targets by pad; the Modem's per-slot price; key hints that
## follow the device; names instead of ids; per-operative loadout and faces; the kit
## leftovers; demo slots keep a private profile.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const TITLE := "res://scenes/menu/title_scene.tscn"
const SLOT := "gut_screens_h20"
const LONG_LINE := "Runner, the compliance office has flagged your cell for audit. Keep the needle off the Miss slice, bank the Rack before the auditors land, and do not let the Heat climb past the next threshold or the whole district locks down for a week."

var _text_scale_before: float = 1.0
var _legend_before: bool = true
var _log_before: bool = false
var _pad_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_legend_before = Settings.map_legend
	_log_before = Settings.system_log
	_pad_before = Settings.pad_active


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
	if Settings.system_log != _log_before:
		Settings.set_system_log(_log_before)
	Settings.set_pad_active(_pad_before)
	Settings.reset_keybinds()
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	get_tree().paused = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


## `path` inside a 1280x720 holder (the design canvas).
func _open(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	return scene


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


## Visible text of every Label and Button under `root`.
func _texts(root: Node) -> PackedStringArray:
	var out := PackedStringArray()
	for n in _all(root):
		if (n is Label or n is Button) and (n as Control).is_visible_in_tree():
			out.append(String(n.get("text")))
	return out


## Every visible, usable control under `root` (buttons, fields, sliders).
func _controls(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		if (n is BaseButton and not (n as BaseButton).disabled and (n as Control).mouse_filter != Control.MOUSE_FILTER_IGNORE) or n is LineEdit or (n is Range and not (n is ScrollBar)):
			out.append(n)
	return out


## The controls a pad reaches from the focus owner (Godot's own neighbour search).
func _reachable() -> Array:
	var start := get_viewport().gui_get_focus_owner()
	if start == null:
		return []
	var seen := {start: true}
	var queue: Array = [start]
	while not queue.is_empty():
		var c: Control = queue.pop_front()
		for side in [SIDE_LEFT, SIDE_RIGHT, SIDE_TOP, SIDE_BOTTOM]:
			var n := c.find_valid_focus_neighbor(side)
			if n != null and not seen.has(n):
				seen[n] = true
				queue.append(n)
		for nx in [c.find_next_valid_focus(), c.find_prev_valid_focus()]:
			if nx != null and not seen.has(nx):
				seen[nx] = true
				queue.append(nx)
	return seen.keys()


## Two claimed nodes beside the home server, an Armory, and a pending raid.
func _raid_campaign() -> CampaignState:
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var claimed := 0
	for sd in grid_data.sites:
		if sd.tier == 1 and sd.id != grid_data.home_site_id and sd.objective == RC.SiteObjective.NONE and claimed < 2:
			var s := c.grid.site(sd.id)
			s["status"] = GridState.SiteStatus.CLAIMED
			s["node_type"] = "firewall_relay"
			s["integrity"] = 30
			s["max_integrity"] = 30
			s["assets"] = ["turret"] if claimed == 0 else []
			claimed += 1
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	return c


func _shop_scene() -> Control:
	var scene := _open(NETRUN)
	scene.start_run(1)
	var s := RunManager.netrun
	s.run.cycles = 400
	s._open_shop()
	scene._show_current()
	return scene


# --- No text logs (designer: "ditch any text logs") ---------------------------------------

func test_hq_status_is_badges_not_a_readout() -> void:
	var c := RunManager.campaign
	c.armory = [&"turret", &"turret", &"decoy"]
	var hq := _open(HQ)
	await _frames()
	for n in _all(hq._panel):
		assert_false(n is TerminalWindow and (n as TerminalWindow).title == "SYSTEM ONLINE", "no SYSTEM ONLINE readout")
	var badges: Node = hq._panel.find_child("CellBadges", true, false)
	assert_not_null(badges, "CELL STATUS badges")
	var assets := 0
	var home := false
	for b in badges.get_children():
		assert_true(b is Badge, "only badges")
		assert_ne((b as Badge).tooltip_text, "", "every badge says what it means")
		if (b as Badge).asset_id != &"":
			assets += 1
		home = home or (b as Badge).glyph == hq.GLYPH_HOME
	assert_eq(assets, 2, "one badge per Armory asset kind")
	assert_true(home, "home integrity badge")
	assert_false(hq._log.visible, "the log strip stays off by default")


func test_the_grid_is_a_site_card_not_a_list_and_every_site_is_reachable() -> void:
	var hq := _open(HQ)
	hq.show_grid()
	await _frames()
	for n in _all(hq._panel):
		assert_false(n is ZineNote and (n as ZineNote).title == "THE PLAN", "no plan note")
		assert_false(n is TerminalWindow and String((n as TerminalWindow).title).begins_with("SITES"), "no Site list")
	var card := hq._panel.find_child("SelectedSite", true, false) as TerminalWindow
	assert_not_null(card, "the picked Site's card")
	assert_ne(hq.selected_site, &"", "a Site is picked from the start")
	assert_not_null(card.find_child("Launch", true, false), "the first open run is picked, its Launch right there")
	assert_not_null(hq._panel.find_child("RunsOpen", true, false), "the open runs as buttons")
	for t in _texts(hq._panel):
		assert_false(t.contains("links:"), "no raw links line: %s" % t)
		for sd in RunManager.corporation.city_grid.sites:
			assert_false(t.contains(String(sd.id) + " ") or t == String(sd.id), "no raw Site id in '%s'" % t)
	# The pad steps through every Site.
	var seen := {}
	for i in RunManager.corporation.city_grid.sites.size():
		seen[hq.selected_site] = true
		hq.step_site(1)
	assert_eq(seen.size(), RunManager.corporation.city_grid.sites.size(), "NEXT SITE visits every Site")
	await _frames()
	var reach := _reachable()
	for id in ["PrevSite", "NextSite", "BackToHq"]:
		assert_true(reach.has(hq._panel.find_child(id, true, false)), "%s reachable by pad" % id)


func test_raid_setup_shows_each_nodes_projected_outcome_without_a_text_wall() -> void:
	var c := _raid_campaign()
	var hq := _open(HQ)
	hq.show_raid()
	await _frames()
	assert_eq(hq.panel_name, "raid")
	for n in _all(hq._panel):
		assert_false(n is ZineNote, "no THREAT ROUTE note")
		assert_false(n is TerminalWindow and (n as TerminalWindow).title == "NODE ORDERS", "no text orders")
	var projection := RunManager.project_raid()
	var orders: Node = hq._panel.find_child("Orders", true, false)
	for id in c.grid.claimed_ids():
		var row: Node = orders.find_child("Order_%s" % id, true, false)
		assert_not_null(row, "an order row for %s" % hq.site_name(id))
		var n: Dictionary = projection.nodes.get(String(id), {})
		var badge_text := ""
		for b in _all(row):
			if b is Badge and (b as Badge).text.contains("→"):
				badge_text = (b as Badge).text
		# H23 S5 (updated on purpose): the numbers say they are the node's HP.
		assert_eq(badge_text, "HP %s → %s %s" % [n.get("before", "?"), n.get("after", "?"), String(n.get("outcome", "?")).to_upper()], "exact projected outcome for %s (GDD 9.3)" % id)
	# H22 #9 (updated on purpose): a dashed forecast, "IF THE RAID RUNS NOW:" + verdict.
	var stamp := hq._panel.find_child("Projection", true, false) as ForecastStamp
	# ANIM-R4 H3 (updated on purpose): ALL HOLD only when nothing is lost; else the losses.
	assert_eq(stamp.verdict, RaidVerdict.of_projection(projection))
	assert_eq(stamp.focus_mode, Control.FOCUS_NONE, "the projection stamp is display only")
	# The map labels the network by name (CORE for the home server), never by id.
	var g: Dictionary = hq.raid_graph(projection, {})
	for node in g["nodes"]:
		if node.has("result"):
			assert_ne(String(node["label"]), String(node["id"]), "map label is a name")
			if node["id"] == c.grid.home_site_id:
				assert_eq(node["label"], hq.HOME_LABEL)


func test_raid_targets_are_pad_reachable_and_deploy_there() -> void:
	var c := _raid_campaign()
	var hq := _open(HQ)
	hq.show_raid()
	await _frames()
	var claimed := c.grid.claimed_ids()
	var other: StringName = claimed[0] if claimed[0] != hq.selected_site else claimed[1]
	var target := hq._panel.find_child("Target_%s" % other, true, false) as Button
	assert_not_null(target, "each node has a target button")
	var reach := _reachable()
	assert_true(reach.has(target), "the pad reaches the target button")
	target.pressed.emit()
	await _frames()
	assert_eq(hq.selected_site, other, "the pressed node is the target")
	var cards: Node = hq._panel.find_child("AssetCards", true, false)
	var card := cards.get_child(0) as AssetCard
	assert_string_contains(card.tooltip_text, hq.site_name(other), "the card says where it deploys")
	var before := c.grid.assets_on(other).size()
	card.pressed.emit()
	await _frames()
	assert_eq(c.grid.assets_on(other).size(), before + 1, "deployed to the pad-picked node")


func test_the_netrun_end_is_tags_and_a_stamp_that_takes_no_focus() -> void:
	var scene := _open(NETRUN)
	scene.start_run(1)
	RunManager.netrun.run.outcome = RunState.Outcome.COMPLETED
	RunManager.netrun.run.phase = RunState.Phase.ENDED
	scene._show_end()
	await _frames()
	var stamp := scene._panel.find_child("ResultStamp", true, false) as ZineStamp
	assert_eq(stamp.focus_mode, Control.FOCUS_NONE)
	assert_eq(stamp.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq(stamp.hint, "", "no key hint on a result")
	assert_true(scene._panel.find_child("RunTags", true, false) is HudStats, "the run in numbers as tags")
	for n in _all(scene._panel):
		assert_false(n is ZineNote, "no summary note")
	var owner := get_viewport().gui_get_focus_owner()
	assert_true(owner is Button and (owner as Button).text == "Back to HQ", "Back to HQ has the first focus")


func test_a_refusal_shows_a_toast_not_only_the_log() -> void:
	var hq := _open(HQ)
	await _frames()
	var c := RunManager.campaign
	c.schematics = 0
	hq.buy_heat_reduction()
	await _frames()
	var toast := hq.get_node_or_null(ToastNote.NODE_NAME) as ToastNote
	assert_not_null(toast, "a refusal pops a toast")
	assert_ne(toast.label.text, "")
	assert_eq(toast.mouse_filter, Control.MOUSE_FILTER_IGNORE, "the toast never eats a click")
	assert_eq(toast.focus_mode, Control.FOCUS_NONE)


# --- #7 subtitles never cover a control -----------------------------------------------------

func _bar_rect() -> Rect2:
	return Rect2(Dialogue.bar.global_position, Dialogue.bar.size)


func _assert_clear(root: Node, label: String) -> void:
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, LONG_LINE)
	await _frames(3)
	assert_true(Dialogue.is_showing(), "%s: a subtitle is up" % label)
	var bar := _bar_rect()
	for c in _controls(root):
		var r := c.get_global_rect()
		assert_false(bar.intersects(r), "%s: the subtitle (%s) covers %s '%s' at %s (text %.1f)" % [label, bar, c.get_class(), c.get("text"), r, Settings.text_scale])
	Dialogue.clear()


func test_subtitles_never_cover_controls_on_any_screen() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		_raid_campaign()
		var hq := _open(HQ)
		await _frames()
		await _assert_clear(hq, "HQ")
		var crew: Node = hq._panel.find_child("Crew_%s" % RunManager.campaign.roster[0].id, true, false)
		(crew.find_child("Loadout", true, false) as Button).pressed.emit()
		await _frames()
		await _assert_clear(hq, "loadout view")
		(hq.get_node("LoadoutView") as LoadoutView)._view.close()
		await _frames()
		hq.show_grid()
		await _frames()
		await _assert_clear(hq, "Grid")
		hq.show_raid()
		await _frames()
		await _assert_clear(hq, "raid setup")
		hq.show_start()
		await _frames()
		await _assert_clear(hq, "HQ start")
		hq.open_settings()
		await _frames()
		hq._settings_panel.show_options()
		await _frames()
		await _assert_clear(hq, "pause Options")
		hq.open_settings()
		var shop := _shop_scene()
		await _frames()
		await _assert_clear(shop, "Modem")
		var title := _open(TITLE)
		title.show_codex()
		await _frames()
		await _assert_clear(title, "title Codex")
		title.show_options()
		await _frames()
		for n in _all(title._panel):
			if n is SettingsPanel:
				(n as SettingsPanel).show_section("Controls")
		await _frames()
		await _assert_clear(title, "title Controls")


func test_the_default_dock_pages_and_names_the_speaker_inline() -> void:
	Dialogue.dock_default()
	assert_true(Dialogue.inline_speaker)
	Dialogue.say(RC.Voice.DISPATCH, "Short line.")
	assert_eq(Dialogue.current_text(), "Short line.", "the words without the name")
	assert_false(Dialogue.speaker_label.visible, "the name leads the line instead of its own row")
	assert_string_contains(Dialogue.text_label.get_parsed_text(), "DISPATCH:")
	Dialogue.clear()
	Settings.set_text_scale(LayoutScales.VERIFIED_MAX)
	assert_eq(Dialogue.dock_lines, Dialogue.lines_fitting(Dialogue.default_rect), "the page size follows the text scale")


# --- #9 modals hold pad focus ---------------------------------------------------------------

func _assert_modal(view: Control, label: String) -> void:
	await _frames()
	var owner := get_viewport().gui_get_focus_owner()
	assert_not_null(owner, "%s: something has focus" % label)
	assert_true(owner != null and view.is_ancestor_of(owner), "%s: focus starts inside the modal" % label)
	for c in _reachable():
		assert_true(view.is_ancestor_of(c), "%s: the pad can't reach %s '%s' behind the modal" % [label, c.get_class(), c.get("text")])


func test_modem_modals_hold_focus_and_give_it_back() -> void:
	var scene := _shop_scene()
	await _frames()
	var shred := scene._panel.find_child("RemoveCard", true, false) as Control
	shred.grab_focus()
	scene.open_remove()
	var deck := scene.get_node("DeckView") as DeckView
	await _assert_modal(deck, "DeckView")
	deck.close()
	await _frames()
	assert_eq(get_viewport().gui_get_focus_owner(), shred, "focus back on the tile that opened it")
	scene.open_overwrite(0)
	await _assert_modal(scene.get_node("SpinnerView"), "SpinnerView")
	(scene.get_node("SpinnerView") as SpinnerView).close()
	await _frames()
	scene.open_loadout()
	await _assert_modal(scene.get_node("LoadoutView"), "LoadoutView")
	(scene.get_node("LoadoutView") as LoadoutView)._view.close()
	await _frames()
	RunManager.netrun.run.operative.daemon_ids.append(&"shield_cache")
	scene.open_daemons()
	await _assert_modal(scene.get_node("DaemonTray"), "DaemonTray")
	(scene.get_node("DaemonTray") as DaemonTray).close()
	await _frames()
	for n in _all(scene._panel):
		if n is Control:
			assert_ne((n as Control).focus_behavior_recursive, Control.FOCUS_BEHAVIOR_DISABLED, "the Modem takes focus again after the modals")


func test_a_modal_keeps_hotkeys_from_the_route_behind_it() -> void:
	var scene := _open(NETRUN)
	scene.start_run(1)
	await _frames()
	var at := RunManager.netrun.run.current_node_id
	scene.open_loadout()
	await _frames()
	var key := InputEventKey.new()
	key.physical_keycode = KEY_1
	key.keycode = KEY_1
	key.pressed = true
	get_viewport().push_input(key)
	await _frames()
	assert_eq(RunManager.netrun.run.current_node_id, at, "1 does not enter a route node behind the loadout view")


func test_hq_viewers_hold_focus_too() -> void:
	var hq := _open(HQ)
	await _frames()
	hq.open_loadout()
	await _assert_modal(hq.get_node("LoadoutView"), "HQ LoadoutView")
	(hq.get_node("LoadoutView") as LoadoutView)._view.close()
	await _frames()
	hq.selected_op().daemon_ids.append(&"shield_cache")
	hq.open_daemons()
	await _assert_modal(hq.get_node("DaemonTray"), "HQ DaemonTray")


# --- #13 the Modem's per-slot price ----------------------------------------------------------

func test_upgrade_a_slice_shows_the_picked_slots_own_price() -> void:
	var scene := _shop_scene()
	var s := RunManager.netrun
	var op := s.run.operative
	var miss := -1
	for i in op.slot_slice_ids.size():
		var sd := s.lookup.get_content(op.slot_slice_ids[i]) as SliceData
		if sd != null and sd.slice_type == RC.SliceType.MISS:
			miss = i
	assert_true(miss >= 0, "the starting spinner has a Miss slot")
	var plain := 0 if miss != 0 else 1
	scene.open_overwrite(0)
	await _frames()
	var view := scene.get_node("SpinnerView") as SpinnerView
	assert_false(view.window.title.contains("CYCLES"), "no single price in the title")
	view.select(miss)
	assert_eq(view.price_label.text, "%d CYCLES" % s.slice_overwrite_price(miss), "the Miss slot's own price")
	view.select(plain)
	assert_eq(view.price_label.text, "%d CYCLES" % s.slice_overwrite_price(plain))
	assert_ne(s.slice_overwrite_price(miss), s.slice_overwrite_price(plain), "the Miss slot costs more (config)")
	view.close()
	await _frames()
	s.run.cycles = s.slice_overwrite_price(miss) - 1
	scene.open_overwrite(0)
	await _frames()
	view = scene.get_node("SpinnerView") as SpinnerView
	watch_signals(view)
	view.select(miss)
	assert_eq(view.price_label.get_theme_color("font_color"), Palette.CELL_PINK, "unaffordable in pink")
	assert_true(view._action_button.disabled, "UPGRADE is off")
	view.confirm()
	assert_signal_not_emitted(view, "slot_picked")


# --- #16 key hints ---------------------------------------------------------------------------

func test_key_hints_follow_the_device_outside_combat() -> void:
	var hq := _open(HQ)
	await _frames()
	var settings_btn := hq._panel.find_child("SettingsButton", true, false) as Button
	assert_eq(settings_btn.text, ("Settings %s" % Settings.hint(&"open_settings")).strip_edges())
	Settings.set_pad_active(true)
	await _frames()
	assert_eq(settings_btn.text, ("Settings %s" % Settings.hint(&"open_settings")).strip_edges(), "relabelled for the pad")
	var jack := hq._panel.find_child("JackIn", true, false) as ZineStamp
	assert_eq(jack.hint, "", "JACK IN names no key (Space does nothing at HQ)")
	var menu := PauseMenu.new()
	add_child_autofree(menu)
	await _frames()
	assert_eq(menu.resume_button.text, ("Resume %s" % Settings.hint(&"open_settings")).strip_edges())
	menu.show_options()
	await _frames()
	assert_eq(menu.settings_panel.close_button.text, ("Close %s" % Settings.hint(&"ui_cancel")).strip_edges())
	Settings.set_pad_active(false)
	await _frames()
	assert_eq(menu.resume_button.text, ("Resume %s" % Settings.hint(&"open_settings")).strip_edges(), "back to the keyboard")
	assert_eq(menu.settings_panel.close_button.text, ("Close %s" % Settings.hint(&"ui_cancel")).strip_edges())
	hq.show_start()
	await _frames()
	var options := hq._panel.find_child("OptionsButton", true, false) as Button
	assert_eq(options.text, ("Options %s" % Settings.hint(&"open_settings")).strip_edges())


func test_viewer_close_and_route_hints_follow_the_device() -> void:
	var scene := _open(NETRUN)
	scene.start_run(1)
	await _frames()
	var first := scene._panel.find_child("Node1", true, false) as Button
	assert_true(first.text.begins_with(Settings.hint(&"card_1")), "keyboard: [1] before the node")
	Settings.set_pad_active(true)
	await _frames()
	# H21 #14: a pad still sees the index (the map label carries it too), not the key.
	assert_eq(first.text, "1 %s" % String(first.get_meta(&"route_base")), "pad: the index, no key hint")
	scene.open_loadout()
	await _frames()
	var deck := (scene.get_node("LoadoutView") as LoadoutView)._view as DeckView
	assert_eq(deck.close_button.text, ("Close %s" % Settings.hint(&"ui_cancel")).strip_edges())
	Settings.set_pad_active(false)
	await _frames()
	assert_eq(deck.close_button.text, ("Close %s" % Settings.hint(&"ui_cancel")).strip_edges())
	assert_string_contains(deck.close_button.text, "Esc")


# --- #21 names, not ids -----------------------------------------------------------------------

func test_crew_stamps_and_station_orders_use_site_names() -> void:
	var c := _raid_campaign()
	var node_id: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
	var op := c.living_operatives()[0]
	c.grid.site(node_id)["stationed"] = String(op.id)
	var hq := _open(HQ)
	await _frames()
	var card := hq._panel.find_child("Crew_%s" % op.id, true, false) as CrewCard
	assert_eq(card.stamp_text, "ON %s" % hq.site_name(node_id).to_upper())
	assert_false(card.stamp_text.contains(String(node_id).to_upper()), "no raw id on the stamp")
	for t in _texts(hq._panel):
		assert_false(t.contains("stationed on %s" % node_id) or t.contains("Station on %s" % node_id), "no raw id in '%s'" % t)
	assert_eq(hq.site_name(c.grid.home_site_id), hq.HOME_LABEL, "the home server is CORE")


# --- #23 which operative; faces --------------------------------------------------------------

func test_loadout_and_daemons_follow_the_picked_operative() -> void:
	var c := RunManager.campaign
	var second := c.recruit(RunManager.lookup().get_content(&"ghost") as ClassData)
	second.daemon_ids.append(&"shield_cache")
	var hq := _open(HQ)
	await _frames()
	var card := hq._panel.find_child("Crew_%s" % second.id, true, false) as CrewCard
	var loadout_btn := card.orders.find_child("Loadout", true, false) as Button
	assert_not_null(loadout_btn, "the dossier has its Loadout button")
	loadout_btn.pressed.emit()
	await _frames()
	var view := hq.get_node("LoadoutView") as LoadoutView
	assert_eq(view.op.id, second.id, "the dossier opens its own operative")
	assert_eq(hq.selected_operative, second.id)
	assert_eq(hq.hud.daemon_ids, second.daemon_ids, "the top bar's Daemons follow")
	var next := view._view.tab_row.find_child("TabNEXT OPERATIVE >", true, false) as Button
	assert_not_null(next, "NEXT OPERATIVE with two living operatives")
	next.pressed.emit()
	await _frames()
	assert_ne(view.op.id, second.id, "cycled to the other operative")
	assert_eq(hq.selected_operative, view.op.id)
	view._view.close()
	await _frames()
	hq.select_operative(second.id)
	hq.open_daemons()
	await _frames()
	var tray := hq.get_node("DaemonTray") as DaemonTray
	assert_eq(tray.ids, second.daemon_ids, "the tray shows the picked operative's Daemons")
	assert_eq((tray.find_child("Owner", true, false) as Label).text, second.name.to_upper())


func test_the_loadout_spinner_shows_hub_and_inner_ring() -> void:
	var c := RunManager.campaign
	var op := c.living_operatives()[0]
	var cls := RunManager.lookup().get_content(op.class_id) as ClassData
	var ring_rank := 0
	for r in cls.rank_rewards:
		if r != null and r.inner_ring != null and (ring_rank == 0 or r.rank < ring_rank):
			ring_rank = r.rank
	if ring_rank > 0:
		op.rank = ring_rank
	var core := LoadoutView.core_of(op, RunManager.lookup())
	assert_not_null(core["hub"], "a hub core")
	var view := LoadoutView.new(op, RunManager.lookup(), RunManager.config().shop_slices)
	add_child_autofree(view)
	await _frames()
	view.show_spinner()
	await _frames()
	var spinner := view._view as SpinnerView
	assert_eq(spinner.hub, core["hub"])
	assert_not_null(spinner.find_child("HubPad", true, false), "the hub is a pad with its detail")
	assert_ne((spinner.find_child("HubPad", true, false) as Button).tooltip_text, "")
	if ring_rank > 0:
		assert_true((core["ring"] as Array).size() > 0, "a ring class shows its inner ring")
		assert_eq(spinner.ring.size(), (core["ring"] as Array).size())
		assert_not_null(spinner.find_child("RingPad0", true, false))


func test_every_operative_has_its_own_face() -> void:
	var a := PortraitArt.operative_subject(&"breaker", &"op_a")
	assert_eq(a, PortraitArt.operative_subject(&"breaker", &"op_a"), "deterministic")
	var keys := {}
	var looks := {}
	for i in 8:
		var s := PortraitArt.operative_subject(&"breaker", StringName("op_%d" % i))
		keys[s["key"]] = true
		var shapes := PortraitArt.shapes(Rect2(0, 0, 100, 100), s)
		looks[str(shapes["hair"]) + str(s["tint"])] = true
	assert_eq(keys.size(), 8, "one key per operative")
	assert_true(looks.size() > 1, "operatives of one class don't all share a face")
	var c := RunManager.campaign
	var op := c.living_operatives()[0]
	var hq := _open(HQ)
	await _frames()
	var card := hq._panel.find_child("Crew_%s" % op.id, true, false) as CrewCard
	assert_eq(card.polaroid.subject["key"], PortraitArt.operative_subject(op.class_id, op.id)["key"], "the dossier shows the operative's face")
	for n in _all(hq._panel):
		if n is HeatPoster:
			assert_eq((n as HeatPoster).wanted["key"], card.polaroid.subject["key"], "the wanted poster shows the same face")


# --- #24 kit leftovers, #25 demo profile ------------------------------------------------------

func test_modem_sign_and_unused_kit_classes() -> void:
	assert_false(ModemSign.NOTES.has("SELL"), "the Modem sells nothing back")
	assert_eq(ModemSign.PINK, Palette.CELL_PINK)
	for f in ["raid_board_view", "drip_label", "neon_sign", "neon_tag", "screen_header"]:
		assert_false(FileAccess.file_exists("res://scripts/ui/kit/%s.gd" % f), "%s removed" % f)


func test_demo_slots_keep_a_private_profile() -> void:
	assert_true(RunManager.is_private_slot("demo"))
	assert_true(RunManager.is_private_slot("gut_x"))
	assert_false(RunManager.is_private_slot("1"))
	assert_false(RunManager.is_private_slot(RunManager.DEFAULT_SLOT))
	RunManager.save_slot = "demo_gut_screens_h20"
	assert_ne(RunManager.profile_path(), SaveService.profile_path(), "a demo run never writes the player's profile")
	RunManager.new_campaign(1)
	RunManager.save_profile()
	assert_true(FileAccess.file_exists(RunManager.profile_path()), "the demo profile is its own file")
	RunManager.delete_save()
	assert_false(FileAccess.file_exists(RunManager.profile_path()), "its profile goes with it")


# --- #15 kit flows and tooltips ---------------------------------------------------------------

func test_deck_and_spinner_pick_flows_reach_the_shop() -> void:
	var scene := _shop_scene()
	var s := RunManager.netrun
	var deck_size := s.run.operative.deck.size()
	scene.open_remove()
	await _frames()
	var deck := scene.get_node("DeckView") as DeckView
	deck.select(0)
	deck.confirm()
	await _frames()
	assert_eq(s.run.operative.deck.size(), deck_size - 1, "REMOVE removed the picked card")
	var stock_id := StringName(String(s.run.shop["slices"][0]))
	var slot := 0
	scene.open_overwrite(0)
	await _frames()
	var spinner := scene.get_node("SpinnerView") as SpinnerView
	spinner.select(slot)
	spinner.confirm()
	await _frames()
	assert_eq(s.run.operative.slot_slice_ids[slot], stock_id, "UPGRADE installed the slice in the picked slot")


func test_daemon_tray_shows_cards_and_closes() -> void:
	var tray := DaemonTray.new([&"shield_cache", &"zero_day"] as Array[StringName], RunManager.lookup(), 600.0, "Nova")
	add_child_autofree(tray)
	await _frames()
	var sigil := tray.find_child("Daemon_shield_cache", true, false) as Button
	assert_ne(sigil.tooltip_text, "", "each sigil has a tooltip")
	sigil.pressed.emit()
	assert_not_null(tray.find_child("DaemonCard", true, false), "a click pins the Daemon's card")
	watch_signals(tray)
	tray.close()
	assert_signal_emitted(tray, "closed")


func test_tooltips_are_themed_and_on_the_screens_controls() -> void:
	var c := _raid_campaign()
	var hq := _open(HQ)
	await _frames()
	var style := hq.get_theme_stylebox(&"panel", &"TooltipPanel") as StyleBoxFlat
	assert_not_null(style, "the tooltip panel has the terminal look")
	assert_eq(style.border_color, Palette.CELL_PINK)
	assert_true(UiTip.make("A long line that wraps", "Title") is Control, "custom tooltip body")
	for line in UiTip.fold(LONG_LINE).split("\n"):
		assert_true(line.length() <= UiTip.COLUMNS, "tooltip lines wrap")
	# HUD stat tags answer per tag.
	# At each tag's own rect (H23: tags are sized to their translated names).
	var rects: Array[Rect2] = hq.hud.stats.tag_rects()
	assert_ne(hq.hud.stats._get_tooltip(rects[0].get_center()), "", "HEAT tag tooltip")
	assert_ne(hq.hud.stats._get_tooltip(rects[1].get_center()), "", "SCHEMATICS tag tooltip")
	assert_ne(hq.hud.stats.mouse_filter, Control.MOUSE_FILTER_IGNORE, "the tags take hover")
	var tipped := {"poster": false, "crew": false, "jack": false}
	for n in _all(hq._panel):
		if n is HeatPoster:
			tipped["poster"] = n.tooltip_text != "" and n.mouse_filter != Control.MOUSE_FILTER_IGNORE
		elif n is CrewCard:
			tipped["crew"] = n.tooltip_text != ""
		elif n is ZineStamp:
			tipped["jack"] = n.tooltip_text != ""
	for k in tipped:
		assert_true(tipped[k], "HQ %s has a tooltip" % k)
	hq.show_grid()
	await _frames()
	for b in _all(hq._panel.find_child("SelectedSite", true, false)):
		if b is Button and (b as Button).name == "Launch":  # JACK IN (H21 #21)
			assert_ne((b as Button).tooltip_text, "", "Launch tooltip")
	hq.show_raid()
	await _frames()
	for n in _all(hq._panel):
		if n is AssetCard or (n is Button and String(n.name).begins_with("Target_")):
			assert_ne((n as Control).tooltip_text, "", "%s tooltip" % n.name)
	# A fresh campaign: no raid interlude before the route.
	RunManager.new_campaign(1)
	var scene := _open(NETRUN)
	scene.start_run(1)
	await _frames()
	var node_btn := scene._panel.find_child("Node1", true, false) as Button
	assert_not_null(node_btn, "the route is up")
	if node_btn != null:
		assert_ne(node_btn.tooltip_text, "", "route node tooltip")
