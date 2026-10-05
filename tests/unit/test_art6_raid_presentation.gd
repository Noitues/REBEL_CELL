extends GutTest
## ART-6 3A (raid presentation, ART_BIBLE v2 §4.8; DECISIONS "Art direction — ART-6 3A raid
## presentation"): the raid's panels by fiction, the grease pencil (routes and state marks), the
## sockets (node health v2, DOWN = the bolt), vehicle icons v4, the drag's IF PLACED terminal and
## the after-action report. The looks are checked windowed (tools/design_lab/raid_lab); these
## check what the views say: true to the rules, reading holds never shortened, reduce effects =
## end state, headless never waits.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art6_raid"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	Motion.set_speed(1.0)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


## A campaign against `corp_id` with up to four nodes claimed, a turret on the first, a weak
## node, and a raid pending.
func _raid_campaign(corp_id: StringName, defended: bool = true, home_integrity: int = -1) -> void:
	RunManager.new_campaign(1)
	var corp := RunManager.lookup().get_content(corp_id) as CorporationData
	RunManager.corporation = corp
	var home := RunManager.lookup().get_content(RunManager.DEFAULT_HOME) as HomeServerVariantData
	RunManager.campaign = CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
		RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, 0, home)
	var c := RunManager.campaign
	c.schematics = 400
	var types: Array[StringName] = [&"firewall_relay", &"vault_terminal", &"relay"]
	for t in types:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	var ids := c.grid.claimed_ids()
	if defended and ids.size() > 1:
		c.armory = [&"turret", &"ice_lock"]
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, ids[1])
	for id in ids:
		if id != c.grid.home_site_id and c.grid.node_type_of(id) == &"vault_terminal":
			c.grid.sites[id]["integrity"] = 2
	if home_integrity > 0:
		c.grid.home_integrity = home_integrity
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


# --- Kit pieces ------------------------------------------------------------------------------

func test_a_threat_icons_type_comes_from_its_rules() -> void:
	for id in RunManager.lookup().ids_of_class(&"ThreatData"):
		var t := RunManager.lookup().get_content(id) as ThreatData
		var want := RaidVehicle.SPECIAL if (t.freezes_edges or t.alters_edges) else (RaidVehicle.FAST if t.edges_per_step >= 2 else RaidVehicle.HEAVY)
		assert_eq(RaidVehicle.type_of(t), want, "%s: shape = what it does" % id)
		for corp in CORPORATIONS:
			for hp in [1.0, 0.6, 0.1]:
				assert_not_null(RaidVehicle.texture(RaidVehicle.type_of(t), corp, hp), "%s %s: the concept's baked icon (icons22)" % [id, corp])
	assert_eq(RaidVehicle.hp_step(0.01), 25, "a threat still standing never shows the empty icon")
	assert_eq(RaidVehicle.hp_step(0.0), 0)
	var manifest := JSON.parse_string(FileAccess.get_file_as_string("res://assets/raid/icons/manifest.json")) as Dictionary
	assert_eq(String(manifest["source"]["script"]), "docs/concepts/round22_raid_world/scripts/icons22.py", "the icons come from the concept script")


func test_node_health_v2_drains_north_to_south() -> void:
	# The sockets are the concept's own (netdecal19/21, baked): every node type, every look.
	for t in [&"relay", &"firewall_relay", &"vault_terminal", &"proxy_relay", &"safehouse", &"compiler_rack", &"home_server"]:
		var g := RaidSocket.glyph_of(t)
		for spec: Dictionary in [{"health": 1.0}, {"health": 0.6}, {"health": 0.3}, {"state": RaidSocket.STATE_DOWN},
				{"state": RaidSocket.STATE_TAKEN}, {"forecast": RaidSocket.STATE_DOWN}, {"forecast": RaidSocket.STATE_TAKEN},
				{"dock": RaidSocket.DRAG_VALID}, {"dock": RaidSocket.DRAG_INVALID}]:
			spec["glyph"] = g
			assert_not_null(RaidSocket.texture(spec), "%s %s: the concept's baked socket" % [t, RaidSocket.image_of(spec)])
	assert_eq(RaidSocket.hp_step(0.95), 75, "damaged never shows the full fill")
	assert_eq(RaidSocket.hp_step(1.0), 100)
	assert_eq(RaidSocket.image_of({"glyph": "relay", "health": 0.5}), "relay_hp050", "the fill drains with health")
	var manifest := JSON.parse_string(FileAccess.get_file_as_string("res://assets/raid/sockets/manifest.json")) as Dictionary
	assert_true(str(manifest["source"]["scripts"]).contains("netdecal21.py"), "the sockets come from the concept's health v2 script")
	assert_eq(RaidSocket.frame_color(RaidSocket.GLYPH_CORE), Palette.CELL_PINK, "CORE pink")
	assert_eq(RaidSocket.frame_color(RaidSocket.GLYPH_RELAY), Palette.GAIN, "holds green")


func test_every_corp_has_its_paper_holo_and_skin() -> void:
	for corp in CORPORATIONS:
		var s := RaidSkin.of(corp)
		assert_ne(s.division(), "", "%s: a letterhead line" % corp)
		assert_true(s.order_number(&"raid_story", 25).begins_with("WO 25-"), "%s: a work order number" % corp)
		var paper: RaidPaper = add_child_autofree(RaidPaper.new(corp, "X", RaidPaper.STAMP_CLASSIFIED))
		assert_true(paper.paper is CorpPaperPanel, "%s: 1B's corp paper is the sheet" % corp)
		var holo: RaidHolo = add_child_autofree(RaidHolo.new(corp, "THREAT INTEL"))
		assert_true(holo.holo is DecryptedHoloPanel, "%s: 1B's decrypted holo" % corp)
		assert_false(holo.holo.scrim, "%s: the holo beside the map is no modal (no full-screen scrim)" % corp)
	var term: RaidTerminal = add_child_autofree(RaidTerminal.new("YOUR NETWORK", Palette.NET_CYAN))
	assert_true(term.crt is CrtTerminalPanel, "YOUR NETWORK is 1B's CRT terminal")
	assert_eq(term.crt.accent_kind, CrtTerminalPanel.Accent.CELL)
	var sticker: RaidSticker = add_child_autofree(RaidSticker.new("CELL HOLDS", UiTheme.DISPLAY, RaidSticker.YELLOW))
	assert_true(sticker.vinyl is VinylSticker, "CELL HOLDS is 1B's vinyl sticker")


# --- The setup: panels by fiction, pencil routes true to the rules ----------------------------

func test_the_setup_shows_the_panels_by_fiction_and_the_projected_routes() -> void:
	for corp in [&"meridian", &"halcyon"]:
		_raid_campaign(corp)
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(4)
		assert_true(hq._panel.find_child("RaidCard", true, false) is RaidPaper, "%s: RAID INCOMING is the intercepted work order" % corp)
		assert_true(hq._panel.find_child("NodeOrders", true, false) is RaidTerminal, "%s: YOUR NETWORK is the Cell's terminal" % corp)
		assert_true(hq._panel.find_child("ThreatIntel", true, false) is RaidHolo, "%s: THREAT INTEL is the decrypted holo" % corp)
		assert_true(hq._panel.find_child("RunRaid", true, false) is RaidSticker, "%s: START DEFENSE is a vinyl sticker" % corp)
		assert_not_null(hq._panel.find_child("SpeedStrip", true, false), "%s: the Speed / Skip strip under it" % corp)
		var projection := RunManager.project_raid()
		var home := hq._panel.find_child("HomeForecast", true, false) as Label
		assert_string_contains(home.text, str(projection.home_after), "%s: the order's forecast is the projection's" % corp)
		var routes: Array[Array] = hq.raid_routes.routes
		assert_eq(routes, HqScript().raid_route_paths(projection.events), "%s: the pencil routes are the projection's" % corp)
		# Preview equals result: the routes the raid really runs are the ones drawn.
		var events := RunManager.fight_raid()
		assert_eq(HqScript().raid_route_paths(events), routes, "%s: the drawn routes are the raid's own" % corp)
		for i in routes.size():
			assert_eq(hq.raid_routes.letter_of(StringName(String(routes[i][0]))) != "", true, "%s: entry %d lettered" % [corp, i])
		hq.get_parent().queue_free()
		await _frames(1)


func HqScript() -> GDScript:
	return load("res://scripts/ui/hq_scene.gd")


# --- The playout: pencil marks, reading holds, reduce effects ---------------------------------

func test_pencil_marks_hold_their_reading_time_at_every_speed() -> void:
	var hold := Motion.entry(RaidFxLayer.MARK_HOLD).duration
	for s in [1.0, 2.0, 4.0]:
		Motion.set_speed(s)
		assert_almost_eq(RaidFxLayer.mark_seconds(RaidFxLayer.MARK_HOLD), hold, 0.0001, "%.0fx: the hold is never shortened" % s)
	Motion.set_speed(0.5)
	assert_gt(RaidFxLayer.mark_seconds(RaidFxLayer.MARK_HOLD), hold, "a slower speed holds longer")
	Motion.set_speed(1.0)
	# Headless (no motion): writes and wipes take no time, the hold keeps its reading time.
	assert_eq(RaidFxLayer.mark_seconds(RaidFxLayer.MARK_WRITE), 0.0, "headless: written at once")
	assert_eq(RaidFxLayer.mark_seconds(RaidFxLayer.MARK_WIPE), 0.0, "headless: wiped at once")
	Motion.force_live = true
	assert_gt(RaidFxLayer.mark_seconds(RaidFxLayer.MARK_WRITE), 0.0, "live: it writes on")
	Settings.set_reduce_effects(true)
	assert_eq(RaidFxLayer.mark_seconds(RaidFxLayer.MARK_WRITE), 0.0, "reduce effects: the end state at once")
	assert_almost_eq(RaidFxLayer.mark_seconds(RaidFxLayer.MARK_HOLD), hold, 0.0001, "reduce effects: still read")


func test_the_marks_name_what_the_raid_did_and_end_at_a_skip() -> void:
	var seen_down := false
	for corp in CORPORATIONS:
		for setup in [[true, -1], [false, -1], [false, 2]]:
			_raid_campaign(corp, setup[0], setup[1])
			if RunManager.pending_raid().is_empty():
				continue
			var events := RunManager.fight_raid()
			var r: Dictionary = RunManager.campaign.last_raid
			var overlay := CityMapOverlay.new()
			add_child_autofree(overlay)
			var fx := RaidFxLayer.new(overlay)
			overlay.add_child(fx)
			fx.setup(r, RunManager.campaign.grid.home_site_id, RunManager.campaign.grid.home_max_integrity, Palette.corp_color(corp))
			var at := 0.0
			for group in RaidBeats.group(events):
				var tl := RaidBeats.timeline(group)
				for b: Dictionary in tl["beats"]:
					fx.play_beat(b, at + float(b["t0"]))
				at += float(tl["seconds"])
			fx.finish_all()
			var tag := "%s %s" % [corp, setup]
			for id in r["nodes"]:
				var outcome := String(r["nodes"][id]["outcome"])
				var kinds := fx.marks().filter(func(m: Dictionary) -> bool: return m["site"] == StringName(String(id))).map(func(m: Dictionary) -> String: return m["kind"])
				if outcome == "down":
					seen_down = true
					assert_true(kinds.has("down"), "%s: %s DOWN is written" % [tag, id])
				if outcome == "taken":
					assert_true(kinds.has("taken"), "%s: %s TAKEN is written" % [tag, id])
				if outcome == "holds":
					assert_false(kinds.has("down") or kinds.has("taken"), "%s: %s holds: no loss written" % [tag, id])
			if bool(r["campaign_lost"]):
				assert_true(fx.marks().any(func(m: Dictionary) -> bool: return m["kind"] == "breached"), "%s: BREACHED is written" % tag)
			for m in fx._marks:
				var pr := fx.mark_progress(m)
				if bool(m.get("stays", false)):
					assert_eq(pr.x, 1.0, "%s: BREACHED stays written after a skip" % tag)
				else:
					assert_eq(pr.y, 1.0, "%s: a skip shows the mark's end state (wiped)" % tag)
			# Sockets fall with the raid: DOWN shows the bolt state, TAKEN burns once wiped.
			for id in r["nodes"]:
				var sid := StringName(String(id))
				if sid == RunManager.campaign.grid.home_site_id:
					continue
				var o := String(r["nodes"][id]["outcome"])
				var live: Variant = fx.socket_state(sid)
				if live == null:
					continue
				if o == "down":
					assert_eq(String((live as Dictionary).get("state", "")), RaidSocket.STATE_DOWN, "%s: %s's socket is DOWN" % [tag, id])
				if o == "taken":
					assert_eq(String((live as Dictionary).get("state", "")), RaidSocket.STATE_TAKEN, "%s: %s's socket is burnt" % [tag, id])
	assert_true(seen_down, "a raid with a node DOWN")


# --- The drag: IF PLACED is true to the rules ------------------------------------------------

func test_if_placed_says_what_placing_really_does() -> void:
	_raid_campaign(&"solace", false)
	var hq := _scene(HQ)
	await _frames(1)
	var c := RunManager.campaign
	c.armory = [&"turret"]
	hq.show_raid()
	await _frames(3)
	var site: StringName = c.grid.home_site_id
	var lines: Array = hq.if_placed_lines({"kind": "asset", "index": 0, "asset": &"turret"}, site)
	assert_false(lines.is_empty(), "IF PLACED has lines")
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, site)
	var after := RunManager.project_raid()
	assert_string_contains(String(lines[lines.size() - 1]), "> %d" % after.home_after, "the forecast it shows is the one placing gives")


# --- The report: the corp's after-action report, CELL HOLDS when the Cell survived -----------

func test_the_report_is_the_corps_paper_with_cell_holds_when_the_cell_survived() -> void:
	for lost in [false, true]:
		_raid_campaign(&"halcyon", not lost, 1 if lost else -1)
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(2)
		RunManager.fight_raid()
		hq.show_raid_summary()
		await _frames(3)
		var r: Dictionary = RunManager.campaign.last_raid
		assert_true(hq._panel.find_child("RaidReport", true, false) is RaidPaper, "the after-action report is corp paper")
		var holds: Node = hq._panel.find_child("CellHolds", true, false)
		assert_eq(holds != null, not bool(r["campaign_lost"]), "CELL HOLDS only when the Cell survived (lost %s)" % lost)
		var verdict := hq._panel.find_child("RaidVerdict", true, false) as ForecastStamp
		assert_not_null(verdict, "the raid's one verdict stays its stamp")
		hq.get_parent().queue_free()
		await _frames(1)


func test_a_stationed_operative_shows_its_class_beacon_from_the_concept() -> void:
	for cls in [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]:
		var strip := RaidBeaconLayer.strip(cls)
		assert_not_null(strip, "%s: the concept's beacon (screens21.beacon), baked" % cls)
		if strip != null:
			assert_eq(strip.get_width(), int(RaidBeaconLayer.FRAME_PX.x) * RaidBeaconLayer.FRAMES, "%s: one strip of the idle loop" % cls)
	var manifest := JSON.parse_string(FileAccess.get_file_as_string(RaidBeaconLayer.DIR + "manifest.json")) as Dictionary
	assert_eq(int(manifest["frames"]), RaidBeaconLayer.FRAMES)
	assert_true(String(manifest["source"]["script"]).begins_with("docs/concepts/round22_raid_world/scripts/screens21.py"), "the beacons come from the concept script")
	Settings.set_reduce_effects(true)
	assert_eq(RaidBeaconLayer.frame_at(0.9), 0, "reduce effects: the beacon stands still")
	Settings.set_reduce_effects(false)
	_raid_campaign(&"halcyon")
	var c := RunManager.campaign
	var site := c.grid.claimed_ids()[1]
	var op := c.living_operatives()[0]
	c.grid.sites[site]["stationed"] = String(op.id)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(2)
	var layer := hq.find_child("RaidBeacons", true, false) as RaidBeaconLayer
	assert_not_null(layer, "the raid map carries the beacons")
	if layer != null:
		var shown := layer.shown()
		assert_eq(shown.size(), 1, "one beacon")
		if shown.size() == 1:
			assert_eq(String(shown[0]["site"]), String(site), "over the node it is stationed on")
			assert_eq(String(shown[0]["class"]), String(op.class_id), "in its class")


func test_ice_is_the_concepts_baked_crystals_growing_in_steps() -> void:
	for step in range(1, RaidFxLayer.ICE_STEPS + 1):
		var p := RaidFxLayer.ICE_DIR + "ice_%02d.png" % step
		assert_true(ResourceLoader.exists(p), "%s: the concept's ice (ui22.ice), baked" % p)
	var manifest := JSON.parse_string(FileAccess.get_file_as_string(RaidFxLayer.ICE_DIR + "manifest.json")) as Dictionary
	assert_true(String(manifest["source"]["script"]).begins_with("docs/concepts/round22_raid_ui/scripts/ui22.py"), "the ice comes from the concept script")
	assert_eq(int(manifest["steps"]), RaidFxLayer.ICE_STEPS, "every baked step is used")
