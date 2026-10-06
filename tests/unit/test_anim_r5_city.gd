extends GutTest
## Animation pass ANIM-R5, city, raid, HQ and bake part (P1-P17; DECISIONS "Animation pass -
## ANIM-R5 city, raid, HQ and bake"). Views only. The bakes run headless under
## CityBakeCache.simulate (requests are recorded, a test lands them with `_land_all`); the
## real renderer's bake is checked by tools/design_lab/bake_smoke.gd (docs/TEST_SUITE.md).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const HqScript := preload("res://scripts/ui/hq_scene.gd")
const SCREEN := Rect2(0, 0, 1280, 720)
const CORPORATIONS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
## Rounds of "let the views ask, then land what they asked for" a page gets to settle.
const LAND_ROUNDS := 5

var _reduce: bool
var _scale: float


class Counter extends Node:
	## Counts the presses that reach it (it sits before the panel in the tree, so the panel
	## sees each event first).
	var got: int = 0

	func _input(event: InputEvent) -> void:
		if MotionSkip.is_press(event):
			got += 1


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r5_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	Motion.force_live = false
	Motion.set_speed(1.0)
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx._set_jacking(false)
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


func _tex() -> ImageTexture:
	return ImageTexture.create_from_image(Image.create(8, 8, false, Image.FORMAT_RGBA8))


## Lands every bake asked for (simulated) with a small picture; returns how many.
func _land_all() -> int:
	var n := 0
	for key: String in CityBakeCache._pending.keys():
		var p: Dictionary = CityBakeCache._pending[key]
		CityBakeCache.store(key, {"look": p["look"], "region": p["region"], "texture": _tex(), "scale": 1.0, "roofs": {},
			"beacons": [] as Array[Dictionary], "lights": [] as Array[Dictionary], "trails": [] as Array[Dictionary], "signs": [] as Array[Dictionary]})
		n += 1
	return n


## Lets the views ask for their bakes and lands them, LAND_ROUNDS times (a page's own view,
## then the prebakes it queues behind it).
func _settle_bakes() -> void:
	for r in LAND_ROUNDS:
		await _frames(NeonCity.BAKE_SETTLE_FRAMES + 2)
		_land_all()
	await _frames(2)


## A campaign against `corp_id` with the first Site off home claimed and, when `defended`,
## two turrets on it; a raid pending (ANIM-R4 city's helper).
func _raid_campaign(corp_id: StringName, defended: bool, home_integrity: int = -1, ice: int = 0,
		home_id: StringName = RunManager.DEFAULT_HOME) -> void:
	RunManager.new_campaign(1)
	var corp := RunManager.lookup().get_content(corp_id) as CorporationData
	var home := RunManager.lookup().get_content(home_id) as HomeServerVariantData
	RunManager.corporation = corp
	RunManager.campaign = CampaignRules.new_campaign(corp, RunManager.config(), RunManager.lookup(), 1,
		RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, ice, home)
	var c := RunManager.campaign
	c.schematics = 400
	var first: StringName = corp.city_grid.get_site(c.grid.home_site_id).links[0]
	var run := RunState.new()
	run.site_id = first
	CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	if defended:
		c.armory = [&"turret", &"turret"]
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	if home_integrity > 0:
		c.grid.home_integrity = home_integrity
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


func _home_variants() -> Array[StringName]:
	var out: Array[StringName] = []
	for id in RunManager.lookup().ids_of_class(&"HomeServerVariantData"):
		out.append(id)
	out.sort()
	return out


# --- P1: the bake's picture is checked, a failed one shows the silhouette --------------------------

func test_a_baked_picture_is_checked_before_it_is_drawn() -> void:
	assert_false(CityBakeCache.usable(null), "no texture")
	assert_true(CityBakeCache.usable(_tex()), "a texture with a size and a RID")
	assert_false(CityBakeCache.usable(ImageTexture.new()), "an empty texture")
	assert_null(BakedTexture.of_viewport(null), "no viewport, no picture")
	assert_null(BakedTexture.of_rd(RID()), "no RenderingDevice texture, no picture")
	var vp := SubViewport.new()
	vp.size = Vector2i(8, 8)
	add_child(vp)
	var kept := BakedTexture.of_viewport(vp)
	if kept != null:
		assert_true(CityBakeCache.usable(kept), "a kept viewport's picture is drawn through its ViewportTexture")
		assert_eq(kept.get_rid(), vp.get_texture().get_rid(), "the texture drawn is the viewport's own target")
		assert_eq(Vector2i(kept.get_size()), vp.size)
		vp.free()
		assert_false(CityBakeCache.usable(kept), "its viewport gone, the picture is not drawn")
	else:
		vp.free()
	assert_true(CityBakeCache.keep_viewports, "the kept viewports are the game's path (measured faster than the copy)")


func test_a_failed_bake_shows_the_silhouette_and_is_not_asked_again() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	await _frames(2)
	city._camera()
	var look := city.look_key()
	var region := city.bake_region()
	CityBakeCache.store(look + "@" + var_to_str(Rect2i(region)), {"look": look, "region": region, "failed": true})
	city.refresh()
	await _frames(NeonCity.BAKE_SETTLE_FRAMES + 3)
	assert_true(city.is_baked(), "the city still draws from bakes (no seconds-long procedural build on the main thread)")
	assert_true(city._sil.visible, "a failed bake shows the city's silhouette, never an empty map")
	assert_false(city.view_covered(), "not covered")
	assert_true(CityBakeCache._pending.is_empty(), "and it is not asked for again")
	# An entry with no usable texture reads as failed too.
	CityBakeCache.clear()
	CityBakeCache.store(look + "@" + var_to_str(Rect2i(region)), {"look": look, "region": region, "texture": ImageTexture.new()})
	city.refresh()
	await _frames(2)
	assert_true(city._sil.visible, "a texture with nothing in it: the silhouette")


# --- P2: pages open on a baked city ----------------------------------------------------------------

## ART-7 7w: the route is the 3D city (covered, no bake); the pages after it stay 2D and are
## baked ahead behind it.
func test_the_runs_pages_open_on_their_bake_behind_the_3d_route() -> void:
	CityBakeCache.simulate = true
	RunManager.new_campaign(1)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	await _settle_bakes()
	var city: NeonCity = scene.background.city
	assert_true(city.city3d, "the route is the 3D city")
	assert_true(city.view_covered(), "the route is covered")
	var run := RunManager.netrun.run
	for page in ["event", "loot", "shop"]:
		match page:
			"event":
				run.event_id = &"ev_leash_on_the_floor"
				run.phase = RunState.Phase.EVENT
			"loot":
				run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
				run.phase = RunState.Phase.REWARD
			"shop":
				RunManager.netrun._open_shop()
		scene._show_current()
		await _frames(2)
		assert_false(city.city3d, "%s: a 2D page" % page)
		assert_true(city.view_covered(), "%s: its city is covered on its first frames (baked ahead behind the route)" % page)
		run.pending_rewards.clear()
		run.phase = RunState.Phase.MAP
		scene._show_current()
		await _frames(2)
		assert_true(city.view_covered(), "back on the route after %s: covered at once" % page)
		# The player reads the route a moment: what it asks for behind itself lands.
		await _settle_bakes()


func test_a_raid_interlude_bakes_its_playout_ahead() -> void:
	CityBakeCache.simulate = true
	RunManager.new_campaign(2)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	HeatRules.add_heat(RunManager.campaign, RunManager.config().major_heat_levels()[0] + 1, RunManager.config(), "test")
	RunManager.netrun._maybe_raid_interlude()
	scene._show_current()
	await _settle_bakes()
	var city: NeonCity = scene.background.city
	assert_true(city.view_covered(), "the interlude is covered")
	var c := RunManager.campaign
	var look := city.look_key()
	var g := CityLayout.grid_graph(c, RunManager.corporation, CityLayout.threat_paths(c, RunManager.corporation))
	var size: Vector2 = scene.size
	var checked := 0
	for n: Dictionary in g["nodes"]:
		var view := city.region_for(Vector2(n["at"]) + Vector2(0.5, 0.5), NetrunScript.PLAYOUT_ANCHOR, NetrunScript.RAID_ZOOM, size).grow(-NeonCity.REGION_MARGIN)
		assert_ne(CityBakeCache.find(look, view), "", "a fight at %s is baked ahead" % n["id"])
		checked += 1
	assert_gt(checked, 1)
	# START DEFENSE (instant headless) then the route (ART-7 7w: the 3D city, no bake).
	scene.raid_fight()
	await _settle_bakes()
	assert_true(city.view_covered(), "the route after the raid is covered")


func test_a_runs_end_warms_the_hq_and_that_bake_outlives_the_run() -> void:
	CityBakeCache.simulate = true
	RunManager.new_campaign(1)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	await _settle_bakes()
	scene._show_end()
	await _frames(2)
	var holder_id := CityBakeCache._holder().get_instance_id()
	var outliving := 0
	for key: String in CityBakeCache._pending:
		if (CityBakeCache._pending[key]["waiters"] as Array).has(holder_id):
			outliving += 1
	assert_gt(outliving, 0, "the HQ's bake is asked for and outlives the run's scene")
	scene.get_parent().free()
	CityBakeCache.drop_stale()
	assert_gt(CityBakeCache._pending.size(), 0, "the jack out does not drop it")
	_land_all()
	var hq := _scene(HQ)
	hq.show_hq()
	await _frames(2)
	assert_true(hq.background.city.view_covered(), "the HQ opens on its baked city")


func test_a_claim_stamps_at_once_and_the_tint_follows_its_bake() -> void:
	CityBakeCache.simulate = true
	_raid_campaign(&"solace", false)
	RunManager.campaign.pending_raids.clear()
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_grid()
	await _settle_bakes()
	var city: NeonCity = hq.wireframe.city
	assert_true(city.view_covered())
	var marked := [0]
	city.territory_marked.connect(func(_m: Array) -> void: marked[0] += 1)
	var c := RunManager.campaign
	var site: StringName = &""
	for s in CampaignRules.launchable_sites(c, RunManager.corporation, RunManager.config()):
		if c.grid.is_corporate(s.id):
			site = s.id
			break
	var run := RunState.new()
	run.site_id = site
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), run)
	hq.claim(site, &"firewall_relay")
	await _frames(2)
	# ART-5 5a: the Grid is the unified 3D city: no bake to wait for, the new look is on at once.
	assert_true(city.city3d)
	assert_true(city.view_covered(), "the 3D city covers its view throughout")
	assert_eq(marked[0], 1, "CLAIMED stamps at once")
	assert_false(city.marks.is_empty())
	await _settle_bakes()
	assert_eq(marked[0], 1, "and the tint followed without stamping again")


# --- P3: the raid's Heat line agrees with its verdict --------------------------------------------

func test_the_raids_heat_line_agrees_with_its_verdict_across_the_sweep() -> void:
	var told := 0
	var ice_top := RunManager.config().ice_ladder.size()
	for corp in CORPORATIONS:
		for home_id in _home_variants():
			for ice in [0, ice_top]:
				for setup in [[true, -1], [false, -1], [false, 3]]:
					_raid_campaign(corp, setup[0], setup[1], ice, home_id)
					if RunManager.pending_raid().is_empty():
						continue
					var events := RunManager.fight_raid()
					var r: Dictionary = RunManager.campaign.last_raid
					var panel := RaidPlayoutPanel.new(null)
					add_child_autofree(panel)
					panel.results = r
					var tag := "%s %s ICE %d %s" % [corp, home_id, ice, setup]
					var verdict := RaidVerdict.of_result(r)
					for e in events:
						var line := panel.feed_line(e)
						if String(e.get("type", "")) != "heat" or String(e.get("reason", "")) != "lost raid":
							continue
						told += 1
						assert_false(line.to_lower().contains("lost"), "%s: the Heat line never says the raid was lost (%s / %s)" % [tag, line, verdict.replace("\n", " ")])
						var reached := int(r.get("home_after", 0)) < int(r.get("home_before", 0))
						if reached:
							assert_string_contains(line, tr("CORE"), "%s: home was hit: the line names what reached CORE" % tag)
						else:
							assert_false(line.contains(tr("CORE")), "%s: nothing reached CORE (%s)" % [tag, verdict.replace("\n", " ")])
						assert_string_contains(line, "%d → %d" % [int(e["before"]), int(e["after"])], "%s: from and to" % tag)
	assert_gt(told, 5, "raids that raised Heat were told")
	assert_false(FileAccess.get_file_as_string("res://assets/text/strings.csv").contains("for the lost raid"), "the old line is gone from the catalogue")


# --- P18: a built REBEL_CELL stays with its campaign; one outcome per fallen node -----------------

func test_a_built_rebel_cell_leaves_the_lookup_with_its_campaign() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10
	var template := RunManager.lookup().get_content(&"rebel_cell") as CorporationData
	assert_true(template.generated_from_profile, "the shipped REBEL_CELL is the template")
	var count := RunManager.lookup().ids().size()
	# The sweeps' path: a REBEL_CELL campaign builds the mirror into the lookup.
	RunManager.new_campaign(1, &"rebel_cell")
	if RunManager.corporation.id == &"rebel_cell":
		assert_ne(RunManager.lookup().get_content(&"rebel_cell"), template, "its campaign reads the built corporation")
	RunManager.reset()
	assert_eq(RunManager.lookup().get_content(&"rebel_cell"), template, "forgetting the campaign gives the lookup its template back")
	assert_eq(RunManager.lookup().ids().size(), count, "and drops what the build added")
	# A second campaign builds from the template, never from the first one's build.
	RunManager.new_campaign(2, &"rebel_cell")
	RunManager.new_campaign(3, &"solace")
	assert_eq(RunManager.lookup().get_content(&"rebel_cell"), template, "another campaign starts on the shipped content")


func test_a_node_down_then_taken_is_one_taken_node_everywhere() -> void:
	_raid_campaign(&"solace", true)
	var c := RunManager.campaign
	var site: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
	var r := {"raid_id": "test", "steps_run": 3, "won": false, "campaign_lost": false, "home_before": 50, "home_after": 50,
		"threats_destroyed": 0, "threats_reached_home": 0, "nodes": {String(site): {"before": 30, "after": 0, "outcome": "taken"}},
		"down": [String(site)], "taken": [String(site)]}
	assert_eq(RaidVerdict.of_result(r), CityMapOverlay.tr_word(RaidVerdict.TAKEN) % 1, "the verdict names the stronger loss once")
	var panel := RaidPlayoutPanel.new(null)
	add_child_autofree(panel)
	panel.results = r
	var tally := panel.feed_line({"type": "raid_end", "won": false, "steps": 3})
	assert_string_contains(tally, tr(RaidPlayoutPanel.FEED_TALLY) % [0, 0, 0, 1], "the feed's tally counts it once, as TAKEN")
	c.last_raid = r
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid_summary()
	await _frames(2)
	var site_label: String = hq.site_name(site)
	# ART-6 3A: the report is the corp's after-action report: a row per node (its value says
	# TAKEN) and the reclaimed Sites' line, each naming the node once.
	var rows: Array[Node] = hq._panel.find_children("ReportRow_%s" % site, "HBoxContainer", true, false)
	assert_eq(rows.size(), 1, "the report lists the node once")
	if rows.size() == 1:
		assert_string_contains((rows[0].get_child(1) as Label).text, tr("TAKEN"), "the report says TAKEN")
	var reclaimed := hq._panel.find_child("ReportReclaimed", true, false) as Label
	assert_not_null(reclaimed, "the reclaimed Sites' line")
	if reclaimed != null:
		assert_eq(reclaimed.text.count(site_label.to_upper()), 1, "named once there")
	assert_null(hq._panel.find_child("ReportDown", true, false), "a node DOWN then TAKEN is not also listed DOWN")


# --- P4: the campaign's end and the pause menu ---------------------------------------------------

func test_the_campaign_end_is_the_audit_dossier_with_its_stamp() -> void:
	for won in [true, false]:
		for scale in [1.0, Settings.TEXT_SCALE_MAX]:
			Settings.set_text_scale(scale)
			RunManager.new_campaign(1)
			var c := RunManager.campaign
			c.story_beats_revealed = 99
			c.outcome = CampaignState.Outcome.WON if won else CampaignState.Outcome.LOST
			var hq := _scene(HQ)
			await _frames(1)
			hq.show_end()
			await _frames(3)
			var tag := "%s %.1f" % ["won" if won else "lost", scale]
			assert_eq(hq.panel_name, "end")
			assert_eq(hq._panel_host.theme_type_variation, &"", "%s: no opaque glass over the desk" % tag)
			var dossier := hq._panel as AuditDossier
			assert_not_null(dossier, "%s: the corporation's audit dossier (ART-11 4D)" % tag)
			var stamp := dossier.find_child("CaseStamp", true, false) as RubberStamp
			assert_not_null(stamp, "%s: a verdict stamp on the report" % tag)
			assert_true(stamp.visible, "%s: it has landed (headless: at once)" % tag)
			assert_eq(stamp.text, tr("AT LARGE") if won else tr("CASE CLOSED"))
			assert_not_null(dossier.find_child("EndStory", true, false), "%s: the story uncovered (annex A)" % tag)
			assert_not_null(dossier.find_child("ProfileFacts", true, false), "%s: the profile's records (annex B)" % tag)
			var width := 0.0
			for sheet in dossier.find_children("*", "PaperSheet", true, false):
				width = maxf(width, (sheet as Control).get_global_rect().end.x)
			assert_true(width <= SCREEN.size.x + 1.0, "%s: the sheets on the screen" % tag)
			hq.get_parent().queue_free()
			await _frames(1)


func test_the_pause_menu_is_as_tall_as_what_it_shows() -> void:
	RunManager.new_campaign(1)
	var hq := _scene(HQ)
	await _frames(1)
	hq.open_settings()
	await _frames(3)
	var menu: PauseMenu = hq._settings_panel
	var want := menu._panel.get_combined_minimum_size().y + menu._host.get_combined_minimum_size().y
	assert_almost_eq(menu.size.y, maxf(want, PauseMenu.FIT_MIN_H), 1.5, "sized to its lines")
	assert_lt(menu.size.y, PauseMenu.MENU_SIZE.y - 100.0, "well under the old 520 px box: the city shows round it")
	var short := menu.size.y
	menu.show_options()
	await _frames(3)
	assert_gt(menu.size.y, short, "Options grows it")
	assert_true(menu.get_global_rect().end.y <= SCREEN.size.y, "never past the screen's foot")
	hq.open_settings()


# --- P5 / P6 / P7 / P8: the raid on the map --------------------------------------------------------

func test_the_interlude_frames_core_and_the_entries_beside_its_window() -> void:
	RunManager.new_campaign(2)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	HeatRules.add_heat(RunManager.campaign, RunManager.config().major_heat_levels()[0] + 1, RunManager.config(), "test")
	RunManager.netrun._maybe_raid_interlude()
	scene._show_current()
	await _frames(4)
	var c := RunManager.campaign
	var pts: PackedVector2Array = scene.raid_frame_points()
	var entries := CampaignRules.raid_entries(c, RunManager.corporation, RunManager.netrun.raid_pending())
	assert_eq(pts.size(), entries.size() + 1, "CORE and the raid's entries only (not the whole Grid)")
	var overlay: CityMapOverlay = scene.city_overlay
	var area: Rect2 = scene._raid_map_area.get_global_rect()
	var win := scene._panel.find_child("RaidWindow", true, false) as Control
	var core := overlay.get_global_transform() * overlay.icon_at(c.grid.home_site_id)
	assert_true(area.grow(1.0).has_point(core), "CORE sits in the map area (%s in %s)" % [core, area])
	assert_false(win.get_global_rect().has_point(core), "not under the RAID window")


func test_the_home_banner_keeps_off_cores_label_and_the_tokens_and_the_packets_stop() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		_raid_campaign(&"solace", false)
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(3)
		hq.fight_raid()
		await _frames(3)
		var overlay: CityMapOverlay = hq.city_overlay
		if hq.panel_name != "raid_playout" and hq.panel_name != "raid_summary":
			continue
		assert_false(overlay.packets, "%.1f: the network's packets stopped with the verdict" % scale)
		hq.show_raid_summary()
		await _frames(2)
		assert_false(hq.city_overlay.packets, "%.1f: none on the report" % scale)
		hq.get_parent().queue_free()
		await _frames(1)
	# The banner's spot search: home's label and the token standing on CORE are kept clear.
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		_raid_campaign(&"solace", false)
		var c := RunManager.campaign
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(4)
		var overlay: CityMapOverlay = hq.city_overlay
		var r := RunManager.project_raid().to_dict()
		r["home_after"] = int(r["home_before"]) - 5
		var fx := RaidFxLayer.new(overlay)
		overlay.add_child(fx)
		fx.setup(r, c.grid.home_site_id, c.grid.home_max_integrity, Palette.CORP_SOLACE)
		assert_gt(overlay.token_radius, CityMapOverlay.MARKER_SIZE, "%.1f: the labels know the tokens' size" % scale)
		var events: Array[Dictionary] = [{"type": "threat_enters", "step": 1, "threat": "t0", "site": c.grid.home_site_id},
			{"type": "raid_end", "won": false, "steps": 1}]
		var at := 0.0
		for group in RaidBeats.group(events):
			var tl := RaidBeats.timeline(group)
			for b: Dictionary in tl["beats"]:
				fx.play_beat(b, at + float(b["t0"]))
			at += float(tl["seconds"])
		fx.clock = at + 100.0
		await _frames(2)
		var banner := fx.banner_rect()
		assert_true(banner.has_area(), "%.1f: the banner shows" % scale)
		var tilted := NeonCity._tilted_bounds(banner, RaidFxLayer.STAMP_TILT)
		var labels := overlay.label_rects()
		if labels.has(String(c.grid.home_site_id)):
			assert_false(tilted.intersects(labels[String(c.grid.home_site_id)]), "%.1f: the banner keeps off CORE's label" % scale)
		for t in fx.token_rects():
			assert_false(tilted.intersects(t), "%.1f: and off the token standing on CORE" % scale)
		hq.get_parent().queue_free()
		await _frames(1)


func test_labels_keep_off_the_threat_tokens() -> void:
	_raid_campaign(&"solace", false)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(4)
	var overlay: CityMapOverlay = hq.city_overlay
	var c := RunManager.campaign
	var home := c.grid.home_site_id
	overlay.token_radius = CityMapOverlay.MARKER_SIZE * RaidFxLayer.TOKEN_SCALE * RaidFxLayer.TOKEN_HALO
	overlay.threat_markers = {home: ["Collector"]}
	await _frames(2)
	var k := overlay.screen_k()
	var tok := overlay.token_radius * k
	var slot := overlay.marker_slot(home, 0, 1)
	var token := Rect2(slot - Vector2(tok, tok), Vector2(tok, tok) * 2.0)
	var rects := overlay.label_rects()
	assert_true(rects.has(String(home)), "CORE keeps its label")
	for key in rects:
		assert_false((rects[key] as Rect2).intersects(token.grow(-1.0)), "%s's label is not under the token on CORE" % key)


func test_the_raid_report_keeps_each_nodes_hp_on_its_row_and_the_forecast_float_says_forecast() -> void:
	_raid_campaign(&"solace", true)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(3)
	hq.fight_raid()
	await _frames(2)
	if hq.panel_name != "raid_summary":
		hq.show_raid_summary()
	await _frames(3)
	var rows: Array = hq._panel.find_children("ReportRow_*", "HBoxContainer", true, false)
	assert_false(rows.is_empty(), "each node's report row")
	for row in rows:
		var name_l := row.get_child(0) as Control
		var badge := row.get_child(1) as Control
		assert_true(badge is Label, "ART-6 3A: the after-action report's value")
		var a := name_l.get_global_rect()
		var b := badge.get_global_rect()
		assert_true(b.position.y < a.end.y and b.end.y > a.position.y, "%s: the HP beside its name, not on a line below" % row.name)
	assert_eq(CityMapOverlay.tr_word(CityMapOverlay.CHANGE_CAPTION), hq.city_overlay.change_caption(), "the forecast float carries its caption")
	assert_ne(hq.city_overlay.change_caption(), "")


func test_your_nodes_never_ends_in_a_cut_row() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		_raid_campaign(&"solace", true)
		var c := RunManager.campaign
		# More nodes than the list shows.
		for s in CampaignRules.launchable_sites(c, RunManager.corporation, RunManager.config()):
			if c.grid.claimed_ids().size() >= 7:
				break
			var run := RunState.new()
			run.site_id = s.id
			CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), run)
			CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), s.id, &"firewall_relay")
		var hq := _scene(HQ)
		await _frames(1)
		hq.show_raid()
		await _frames(6)
		var hint: ScrollHint = hq.side_hint
		assert_not_null(hint, "%.1f: YOUR NODES has its hint" % scale)
		assert_true(hint.snap_rows)
		if hint.overflows():
			assert_almost_eq(hint.cut_row_reserve(), hint.snap_reserve, 1.0, "%.1f: the view ends above the row it would cut" % scale)
		hq.get_parent().queue_free()
		await _frames(1)


func test_the_grids_run_rows_say_what_a_clear_gives() -> void:
	RunManager.new_campaign(1)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_grid()
	await _frames(3)
	var caps: Array = hq._panel.find_children("GainsCaption", "Label", true, false)
	assert_false(caps.is_empty(), "every gains row opens with its caption")
	for cap in caps:
		assert_eq((cap as Label).text, tr(HqScript.GAIN_CAPTION))
	var words := PackedStringArray()
	for b in hq._panel.find_children("Gain_*", "Badge", true, false):
		words.append((b as Badge).text)
	var joined := " ".join(words)
	assert_false(joined.contains(CityMapOverlay.tr_word("CLAIM") + " ") or words.has(CityMapOverlay.tr_word("CLAIM")), "no bare CLAIM (read as a button)")
	for w in words:
		if w.begins_with("OPENS"):
			assert_true(w.ends_with("SITE") or w.ends_with("SITES"), "'%s' says what opens" % w)


# --- P9: the Heat banner's consequence reads ------------------------------------------------------

func test_the_heat_consequence_is_a_legible_note_held_to_be_read() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		for kind in [true, false]:
			var p := HeatPoster.new(kind)
			holder.add_child(p)
			p.size = p.custom_minimum_size if kind else Vector2(170, 134)
			p.position = Vector2(40, 200)
			p.heat = 30
			p._banner_at = 25
			var tag := "%.1f poster=%s" % [scale, kind]
			assert_gte(p.note_font_size(), roundi(HeatPoster.NOTE_FONT * scale), "%s: the note's lettering follows the text size" % tag)
			assert_gte(p.note_font_size(), HeatPoster.NOTE_FONT, "%s: never under the floor" % tag)
			assert_false(p.note_lines().is_empty(), "%s: it says what the band brings" % tag)
			var r := p.note_rect()
			assert_true(SCREEN.grow(0.5).encloses(r), "%s: on the screen" % tag)
			assert_false(r.intersects(p.get_global_rect().grow(-1.0)), "%s: beside the poster, not on it" % tag)
			for line in p.note_lines():
				assert_true(Palette.mono().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, p.note_font_size()).x <= r.size.x - HeatPoster.NOTE_PAD * 2.0 + 0.5, "%s: '%s' fits" % [tag, line])
			assert_true(p.sub_lines().is_empty(), "%s: no 9 px lines on the tilted sticker" % tag)
			if kind:
				var title := p.title_rect()
				for c in p.banner_corners():
					assert_false(title.grow(-1.0).has_point(c), "%s: the banner keeps off WANTED" % tag)
			p.free()
	# Held long enough to read the longest consequence (brisk: 5 words a second).
	var longest := 0
	for t in RunManager.config().heat_thresholds:
		longest = maxi(longest, TextDb.t(t, "event_text").split(" ", false).size())
	assert_gte(Motion.delay_of(&"heat_banner"), longest / 5.0, "the hold reads %d words" % longest)


# --- P10 / P11 / P12 ------------------------------------------------------------------------------

func test_a_polaroid_caption_is_never_cut() -> void:
	for w in [110.0, 80.0, 64.0]:
		var p := Polaroid.new("Breaker 1 R0", "[BREAKER PORTRAIT]")
		add_child_autofree(p)
		p.size = Vector2(w, w * 134.0 / 110.0)
		assert_true(_caption_fits(p), "%.0f px: the whole caption fits (%s)" % [w, p.caption_layout()])
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var hq := _scene(HQ)
		await _frames(3)
		var seen := 0
		for p in hq.find_children("*", "Polaroid", true, false):
			var pol := p as Polaroid
			if not pol.is_visible_in_tree() or pol.caption == "":
				continue
			seen += 1
			assert_true(_caption_fits(pol), "%.1f: '%s' whole on its Polaroid (%s)" % [scale, pol.caption, pol.caption_layout()])
		assert_gt(seen, 0, "%.1f: the crew's Polaroids were checked" % scale)
		hq.get_parent().queue_free()
		await _frames(1)


func _caption_fits(p: Polaroid) -> bool:
	var lay := p.caption_layout()
	for line: String in lay["lines"]:
		if Palette.marker().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, int(lay["fs"])).x > p.size.x - Polaroid.CAPTION_INSET * 2.0 + 0.5:
			return false
	return true


func test_after_the_interlude_raid_the_route_starts_at_its_own_frame() -> void:
	RunManager.new_campaign(2)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	await _frames(2)
	scene.background.hold_camera()
	scene._leave_raid_playout()
	assert_false(scene.background.camera_easing(), "the fight camera's frame is let go: no ease from the raid's zoom")


func test_the_playout_follows_the_one_press_rule_and_speed_presses_skip_nothing() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var counter := Counter.new()
	holder.add_child(counter)
	var other := Button.new()
	other.text = "Back to HQ"
	other.position = Vector2(40, 600)
	other.size = Vector2(200, 50)
	holder.add_child(other)
	var panel := RaidPlayoutPanel.new()
	holder.add_child(panel)
	var events: Array[Dictionary] = []
	for step in range(1, 6):
		events.append({"type": "move", "step": step, "threat": &"t0", "from": &"a", "to": &"b", "text": "A threat moves."})
	events.append({"type": "raid_end", "text": "Raid over."})
	panel.play(events, false)
	await _frames(2)
	var two := panel.find_child("Speed2x", true, false) as Button
	# A focus move: passes, the step plays on.
	panel._clock = 0.0
	var got := counter.got
	get_viewport().push_input(_key(KEY_RIGHT))
	assert_eq(panel._clock, 0.0, "a focus move skips no step")
	assert_eq(counter.got, got + 1, "and passes on")
	# A press on 2x: speeds up, skips nothing.
	two.grab_focus()
	await _frames(1)
	panel._clock = 0.0
	assert_true(panel.drives_playout(_action(&"ui_accept")), "accept on 2x drives the playout")
	# A click on a button of the screen: the step ends and the click goes through (PASS).
	var next := panel._next_at
	panel._clock = 0.0
	var at := other.get_global_rect().get_center()
	var click := _click(at)
	assert_eq(MotionSkip.verdict(click, panel), MotionSkip.Verdict.PASS, "a click on the screen's button works the screen")
	assert_false(panel.drives_playout(click), "it does not drive the playout")
	panel._input(click)
	assert_almost_eq(panel._clock, next, 0.0001, "so it ends the step (it returned without ending it before) and passes on")
	# Any other press: the step ends and the press is consumed.
	panel._clock = 0.0
	got = counter.got
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_almost_eq(panel._clock, panel._next_at, 0.0001, "another press ends the step")
	assert_eq(counter.got, got, "and is consumed")
	Motion.set_speed(1.0)


func _key(k: Key, pressed: bool = true) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = pressed
	return e


func _click(at: Vector2, pressed: bool = true) -> InputEventMouseButton:
	var e := InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.button_mask = MOUSE_BUTTON_MASK_LEFT if pressed else 0
	e.pressed = pressed
	e.position = at
	e.global_position = at
	return e


func _motion(at: Vector2) -> InputEventMouseMotion:
	var e := InputEventMouseMotion.new()
	e.position = at
	e.global_position = at
	return e


func _action(action: StringName) -> InputEventAction:
	var e := InputEventAction.new()
	e.action = action
	e.pressed = true
	return e


func test_you_are_here_is_translated_once() -> void:
	var tr_x := Translation.new()
	tr_x.locale = "xx"
	tr_x.add_message(CityMapOverlay.HERE_LABEL, "XX-ICI")
	TranslationServer.add_translation(tr_x)
	var locale := TranslationServer.get_locale()
	TranslationServer.set_locale("xx")
	var overlay := CityMapOverlay.new()
	add_child_autofree(overlay)
	overlay.set_graph([{"id": &"n0", "at": Vector2(3, 3), "here": true}], [])
	assert_eq(Array(overlay.label_lines(&"n0")), ["XX-ICI"], "the node's words in the player's language")
	TranslationServer.set_locale(locale)
	TranslationServer.remove_translation(tr_x)
	assert_string_contains(FileAccess.get_file_as_string("res://assets/text/strings.csv"), "YOU ARE HERE,", "exported once")


# --- P13 / P14: tests R4 left out ------------------------------------------------------------------

func test_the_clear_previews_are_cached_per_campaign_state_and_hashed_once_per_pass() -> void:
	RunManager.new_campaign(1)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_hq()
	await _frames(1)
	var c := RunManager.campaign
	hq._sync_previews()
	var sites := RunManager.launchable_sites()
	assert_false(sites.is_empty())
	var s: SiteData = sites[0]
	var cached: Dictionary = hq.clear_preview_of(s)
	assert_eq(var_to_str(cached), var_to_str(CampaignRules.clear_preview(c, RunManager.corporation, RunManager.config(), s, RunManager.lookup())), "the cached preview is the rules' own")
	assert_true(hq._previews.has(s.id))
	# The campaign changes: the cache drops.
	c.schematics += 7
	hq._sync_previews()
	assert_false(hq._previews.has(s.id), "a changed campaign drops the cached previews")
	assert_eq(hq._previews_key, HqScript.campaign_key(c))
	# A warm pass hashes the campaign once, not every frame.
	hq._previews.clear()
	var before := HqScript.campaign_hashes
	hq._warm_previews()
	for i in sites.size() + 3:
		await get_tree().process_frame
	assert_lte(HqScript.campaign_hashes - before, 1, "one hash for the pass (it was one a frame)")
	assert_true(hq._previews.size() >= mini(sites.size(), 2), "and the pass worked previews out")


func test_music_is_built_ahead_and_collected_whole() -> void:
	AudioDirector.muted = false
	var ctx := AudioDirector.context_for("raid", &"solace")
	AudioDirector._music.erase(ctx)
	AudioDirector.prewarm_music(["raid"], &"solace")
	assert_true(AudioDirector._warming.has(ctx), "the loop is built on the worker pool")
	AudioDirector._collect_warm(ctx)
	assert_false(AudioDirector._warming.has(ctx), "collected")
	var built: AudioStreamWAV = AudioDirector._music.get(ctx)
	assert_not_null(built, "the loop is there for play_music")
	assert_eq(built.data, AudioDirector._make_music(ctx).data, "the same loop the main thread would build")
	AudioDirector.muted = true


func test_under_reduce_effects_the_end_states_show_at_once_and_raid_incoming_holds() -> void:
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	# The road pulse and the forecast change: at their ends.
	_raid_campaign(&"solace", false)
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(3)
	var c := RunManager.campaign
	var site: StringName = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
	c.armory = [&"turret"]
	hq.deploy_asset(0, site)
	await _frames(1)
	var overlay: CityMapOverlay = hq.city_overlay
	assert_eq(overlay.road_t, 1.0, "the road pulse at its end")
	assert_eq(overlay.change_t, 1.0, "the forecast change at its end")
	assert_eq(overlay.drop_t, 1.0, "the drop landed")
	# RAID INCOMING is a reading time: it holds under reduce effects too.
	assert_gte(Fx.note_hold(), 1.0, "RAID INCOMING holds (a reading time, not an effect)")
	# The route's choices during a move: at once.
	hq.get_parent().queue_free()
	RunManager.new_campaign(1)
	var scene := _scene(NETRUN)
	scene.start_run(1)
	await _frames(3)
	var s := RunManager.netrun
	scene.enter_node(s.available_nodes()[0])
	assert_false(scene._travelling, "no move plays")
	# The Heat banner: no banner, the band word at once.
	var p := HeatPoster.new(true)
	add_child_autofree(p)
	var marks: Array[int] = [25, 50, 75]
	p.set_heat(10, 100, marks)
	p.set_heat(30, 100, marks)
	await _frames(1)
	# ANIM-R6 C5: the banner and its consequence show at once, static, for their reading hold.
	assert_eq(p.banner_alpha, 1.0, "the banner shows static under reduce effects (ANIM-R6 C5)")
	assert_eq(p.banner_scale, 1.0, "with no stamp-on")
	assert_true(p.note_showing(), "and its note, to be read")
	assert_eq(roundi(p.shown_heat), 30, "the number at once")
	assert_eq(p.shown_band(), 1, "the band word at once")


# --- P15 / P16 ---------------------------------------------------------------------------------------

func test_raid_incoming_fits_a_long_translation_at_every_text_size() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		Fx._note = "RAID INCOMING\n%s" % "KONZERNSICHERHEITSVERWALTUNGSBEHÖRDE UND ÜBERWACHUNGSGESELLSCHAFT MIT BESCHRÄNKTER HAFTUNG"
		Fx._show_note(SCREEN.size)
		var span := Fx.note_span(Fx.note_label.size)
		assert_true(span <= SCREEN.size.x - Fx.NOTE_MARGIN * 2.0 + 1.0, "%.1f: the tilted stamp spans %.0f px of %.0f" % [scale, span, SCREEN.size.x])
		assert_gte(Fx.note_label.get_theme_font_size(&"font_size"), mini(roundi(Fx.NOTE_FONT * scale), roundi(Fx.NOTE_FONT_MIN * scale)), "%.1f: large still" % scale)
		Fx._hide_connect()
	Fx._note = "RAID INCOMING\nSOLACE BIOSYSTEMS"
	Settings.set_text_scale(Settings.TEXT_SCALE_MAX)
	Fx._show_note(SCREEN.size)
	assert_eq(Fx.note_label.get_theme_font_size(&"font_size"), roundi(Fx.NOTE_FONT * Settings.TEXT_SCALE_MAX), "a short one keeps its full size")
	Fx._hide_connect()


func test_the_heat_posters_notes_name_the_banner_as_it_reads() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/heat_poster.gd")
	assert_false(src.contains("HEAT 25 - NOTICED"), "no stale banner words in the comments")
	assert_false(src.contains("HEAT 30 - NOTICED"))
