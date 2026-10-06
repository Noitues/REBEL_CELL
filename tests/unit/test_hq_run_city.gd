extends GutTest
## ART-8 8w: HQ runs on the city. The compound's place, camera and node points
## (HqCompoundStage), the DISPATCH canyon's layout on screen, the breach preview equal to the
## fight start (NetrunSession.breach_preview), the HQ-run page's marks (HqRunView), the
## Central Server gate's states (CentralServerGate), the city staging (CityView3D) and the
## combat backdrop's city close-up choice (BackdropCatalog, D17). Headless: pure maths and the
## views' end states (no renderer).

const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
const SEEDS: Array[int] = [1, 7, 42]
const HQ_TIER := 4
const VIEW := Vector2(1920, 1080)

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _solace: CorporationData
var _city: CityConfig = CityView3D.CONFIG


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_solace = ContentRegistry.get_content(&"solace") as CorporationData


func _breach(run_seed: int, exploits: Array = []) -> NetrunSession:
	var c := CampaignRules.new_campaign(_solace, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	for e in exploits:
		c.exploits.append(e)
	return NetrunSession.start_special(_resolver, c, c.roster[0].id, "boss", &"the_genome_core", HQ_TIER, run_seed,
		_solace.final_boss.id, CampaignRules.boss_overrides(c, _solace), _solace)


# --- Stage maths ------------------------------------------------------------------------------

func test_the_canyon_stands_on_its_own_lots_and_the_corps_on_their_hq_lots() -> void:
	for corp in CORPS:
		var m := HqCompoundStage.manifest(corp)
		assert_false(m.is_empty(), "%s has a compound manifest" % corp)
		var at := HqCompoundStage.place(_city, corp, m)
		var lot := HqCompoundStage.place_lot(corp, m)
		if corp == &"rebel_cell":
			assert_eq(lot, Vector2(36.5, 36.5), "the canyon on round 34's own canyon lots (place_lot)")
		else:
			assert_eq(lot, NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5, "%s on its HQ lot's centre" % corp)
		assert_eq(at.origin, CityIsoCamera.lot_to_world(_city, lot), "%s: the origin is the lot point" % corp)
		assert_eq(at.basis, Basis(), "%s: the compound's frame is the city's" % corp)
		assert_true(HqCompoundStage.footprint_rect(m, at).has_point(Vector2(at.origin.x, at.origin.z)), "%s: the footprint holds its origin" % corp)
		assert_true(ResourceLoader.exists(HqCompoundStage.model_path(corp, m)), "%s: its glTF is there" % corp)


func test_the_hq_run_camera_follows_the_manifest() -> void:
	for corp in CORPS:
		var m := HqCompoundStage.manifest(corp)
		var cam := HqCompoundStage.camera(_city, m, HqCompoundStage.place(_city, corp, m), VIEW)
		var s: Dictionary = m["settings"]
		assert_eq(cam.yaw_deg, float(s["yaw_deg"]), "%s yaw" % corp)
		assert_eq(cam.pitch_deg, float(s["pitch_deg"]), "%s pitch" % corp)
		assert_eq(cam.ortho, float(s["reference_camera"]["ortho"]), "%s ortho" % corp)
	var canyon := HqCompoundStage.manifest(&"rebel_cell")
	assert_eq(float(canyon["settings"]["yaw_deg"]), 180.0, "the canyon looks down the street")
	assert_eq(float(canyon["settings"]["pitch_deg"]), 40.0, "at the city's own pitch")
	assert_eq(HqCompoundStage.server_name(canyon), "DISPATCH CORE", "the Cell's Central Server is DISPATCH CORE")


## Every slot of the canyon (and its Central Server) stands apart on screen at the HQ-run
## camera, the rows climbing up the street away from the camera (the validator's 50 px rule,
## here through the game's own camera).
func test_the_canyon_layout_reads_on_screen() -> void:
	var corp := &"rebel_cell"
	var m := HqCompoundStage.manifest(corp)
	var l := HqCompoundStage.layout(corp)
	var at := HqCompoundStage.place(_city, corp, m)
	var cam := HqCompoundStage.camera(_city, m, at, VIEW)
	var pts: Array[Vector2] = []
	for i in l.layer_slots.size():
		pts.append(cam.project(at * l.layer_slots[i]))
	pts.append(cam.project(HqCompoundStage.server_point(l, at)))
	for i in pts.size():
		assert_true(Rect2(Vector2.ZERO, VIEW).has_point(pts[i]), "slot %d on screen (%s)" % [i, pts[i]])
		for j in range(i + 1, pts.size()):
			assert_gt(pts[i].distance_to(pts[j]), 45.0, "slots %d and %d apart on screen" % [i, j])
	# The rows run up the street: each row's alley slot higher on screen than the last.
	for row in range(1, l.layer_rows()):
		var a := cam.project(at * l.slot_position(row, 1))
		var b := cam.project(at * l.slot_position(row + 1, 1))
		assert_lt(b.y, a.y, "row %d stands further up the canyon than row %d" % [row + 1, row])


func test_a_full_run_map_lands_inside_the_compound() -> void:
	for corp in CORPS:
		var m := HqCompoundStage.manifest(corp)
		var at := HqCompoundStage.place(_city, corp, m)
		var fp := HqCompoundStage.footprint_rect(m, at).grow(1.0)
		for run_seed in SEEDS:
			var g := MapGenerator.generate(HQ_TIER, _cfg, RngStreams.make_stream(run_seed, &"map"))
			var pts := HqCompoundStage.node_points(HqCompoundStage.layout(corp), g, at)
			assert_eq(pts.size(), g.node_count(), "%s seed %d: every node has a point" % [corp, run_seed])
			for id: StringName in pts:
				var p: Vector3 = pts[id]
				assert_true(fp.has_point(Vector2(p.x, p.z)), "%s seed %d: %s inside the compound" % [corp, run_seed, id])


# --- The breach preview equals the fight start ------------------------------------------------

func test_the_breach_preview_equals_the_fight_start_and_changes_nothing() -> void:
	for run_seed in SEEDS:
		var s := _breach(run_seed, [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS])
		var before := s.state_hash()
		var campaign_before := s.campaign.to_dict()
		var preview := s.breach_preview()
		assert_not_null(preview, "seed %d: the breach has a preview" % run_seed)
		assert_eq(s.state_hash(), before, "seed %d: the preview leaves the run and its streams" % run_seed)
		assert_eq(s.campaign.to_dict(), campaign_before, "seed %d: the preview leaves the campaign" % run_seed)
		assert_eq(s.breach_preview().to_dict(), preview.to_dict(), "seed %d: the preview is deterministic" % run_seed)
		s.enter_node(s.available_nodes()[0])
		assert_true(s.in_combat(), "the breach starts its fight")
		assert_eq(preview.to_dict(), s.combat.to_dict(), "seed %d: the gate preview equals the fight start" % run_seed)
		assert_null(s.breach_preview(), "no preview once the fight is on")


func test_a_netrun_has_no_breach_preview() -> void:
	var c := CampaignRules.new_campaign(_solace, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	var s := NetrunSession.start(_resolver, c, c.roster[0].id, 1, &"t1_a", 5, _solace)
	assert_null(s.breach_preview(), "only the HQ breach has a gate")


# --- The HQ-run page --------------------------------------------------------------------------

func test_the_hq_run_page_marks_the_central_server_and_the_live_link() -> void:
	for corp in CORPS:
		var s := _breach(3)
		var v := HqRunView.new()
		v.size = VIEW
		add_child_autofree(v)
		v.show_run(corp, s.run.map, s.run.current_node_id, s.run.visited, s.available_nodes(), "THE CORE")
		var server := s.run.map.final_node_id()
		var p := v.screen_of(server)
		assert_true(Rect2(Vector2.ZERO, VIEW).has_point(p), "%s: the Central Server is on the page" % corp)
		assert_true(Rect2(Vector2.ZERO, VIEW).has_point(v.entry_screen()), "%s: the entry is on the page" % corp)
		assert_eq(v.node_at(p), server, "%s: a click on the server picks it" % corp)
		assert_eq(v.node_at(p + Vector2(400, 400)), &"", "%s: empty map picks nothing" % corp)
		assert_eq(v.state_of(server), RouteOverlay.STATE_NEXT, "%s: the server is selectable" % corp)
		var links := v.links()
		assert_eq(links.size(), 1, "%s: one link, entry to server" % corp)
		assert_eq(links[0]["state"], "live", "%s: the live link is the orange dash" % corp)
		var chip := v.chip_rect()
		assert_true(chip.has_area(), "%s: the chip is drawn" % corp)
		var circle_top := p.y - v.node_radius(server) * RouteOverlay.TARGET_SHARE * RouteOverlay.TARGET_SQUASH
		var circle_bottom := p.y + v.node_radius(server) * RouteOverlay.TARGET_SHARE * RouteOverlay.TARGET_SQUASH
		assert_true(chip.end.y <= circle_top + 0.5 or chip.position.y >= circle_bottom - 0.5, "%s: the chip sits clear of the pencil circle" % corp)
		assert_true(Rect2(Vector2.ZERO, VIEW).encloses(chip), "%s: the chip is on the page" % corp)
		watch_signals(v)
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.pressed = true
		click.position = p
		v._gui_input(click)
		assert_signal_emitted_with_parameters(v, "node_pressed", [server])


func test_a_walked_server_shows_walked() -> void:
	var s := _breach(3)
	var server := s.run.map.final_node_id()
	var v := HqRunView.new()
	v.size = VIEW
	add_child_autofree(v)
	var walked: Array[StringName] = [server]
	var none: Array[StringName] = []
	v.show_run(&"solace", s.run.map, server, walked, none, "THE GENOME CORE")
	assert_eq(v.state_of(server), RouteOverlay.STATE_WALKED)
	assert_eq(v.links()[0]["state"], "walked", "the walked link is the solid lime line")
	assert_eq(v.node_at(v.screen_of(server)), &"", "nothing to pick once walked")


# --- The gate ---------------------------------------------------------------------------------

func _gate(held: Array[int], with_preview: bool) -> CentralServerGate:
	var g := CentralServerGate.new()
	var s := _breach(5, [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS])
	g.setup(&"solace", "Solace", "THE GENOME CORE", HQ_TIER, held, _cfg.min_exploits_for_breach,
		s.breach_preview() if with_preview else null, _lookup)
	add_child_autofree(g)
	return g


func test_the_gate_with_every_exploit_lands_ready_headless() -> void:
	var all: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	var g := _gate(all, true)
	assert_false(g.motion_running(), "headless never waits: the end state at once")
	for st in g.socket_states():
		assert_true(st["filled"], "every socket holds its card")
		assert_eq(st["card"], 1.0, "the card slapped in")
		assert_eq(st["ring"], 1.0, "the socket rang")
	assert_eq(g.breach_t, 1.0, "BREACH is pink")
	assert_false(g.breach_button.disabled, "BREACH works")
	assert_not_null(g.wheel, "the boss wheel shows the preview")
	assert_eq(g.wheel.combatant.source_id, _solace.final_boss.id, "the preview's boss")
	for k in CentralServerGate.KINDS:
		assert_true(ResourceLoader.exists(g.keycard_path(k)), "the generator's keycard for %s" % k)
	watch_signals(g)
	g.breach_button.pressed.emit()
	assert_signal_emitted(g, "breach_pressed")


func test_the_gate_short_of_exploits_stays_locked() -> void:
	var one: Array[int] = [RC.ExploitType.BREACH]
	var g := _gate(one, false)
	var st := g.socket_states()
	assert_false(st[0]["filled"], "INTEL's socket is empty")
	assert_true(st[1]["filled"], "BREACH's card is in")
	assert_eq(st[1]["ring"], 1.0)
	assert_eq(st[0]["ring"], 0.0, "an empty socket stays dashed")
	assert_eq(g.breach_t, 0.0, "BREACH stays grey")
	assert_true(g.breach_button.disabled, "BREACH is locked under the minimum")
	assert_null(g.wheel, "no preview, no wheel")


func test_the_gate_completes_on_one_press_and_reduce_effects_is_the_end_state() -> void:
	var all: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	Motion.force_live = true
	var g := _gate(all, false)
	assert_true(g.motion_running(), "the cards slap in when motion plays")
	assert_lt(g.breach_t, 1.0, "BREACH turns pink at the end")
	g.complete_motion()
	assert_false(g.motion_running())
	assert_eq(g.breach_t, 1.0, "one press lands the end state")
	Motion.force_live = false
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	var r := _gate(all, false)
	assert_false(r.motion_running(), "reduce effects: no motion")
	assert_eq(r.breach_t, 1.0, "reduce effects: the end state")
	Settings.reduce_effects = was


# --- City staging and the combat backdrop -----------------------------------------------------

func test_staging_a_compound_clears_its_footprint_and_skips_the_landmark() -> void:
	var v := CityView3D.new()
	assert_null(v.stage_compound(&"rebel_cell"), "headless: no model drawn")
	assert_true(v.compounds.has(&"rebel_cell"), "the canyon is staged")
	var m := HqCompoundStage.manifest(&"rebel_cell")
	var at := HqCompoundStage.place(v.cfg, &"rebel_cell", m)
	assert_true(v.is_cleared(Vector2(at.origin.x, at.origin.z)), "the city's own buildings give way in the canyon")
	assert_false(v._place_landmark(&"rebel_cell", "res://assets/city/landmarks/rebel_cell/rebel_cell_district.glb", Transform3D(), null),
		"the Cell's district stays off while the canyon stands")
	var near := Rect2(Vector2(at.origin.x, at.origin.z) - Vector2(3, 3), Vector2(6, 6))
	assert_true(v._under_compound(near), "a Site landmark on the canyon's lot gives way (the compound wins)")
	assert_false(v._under_compound(Rect2(near.position + Vector2(2000, 2000), near.size)), "one elsewhere stands")
	v.unstage_compound(&"rebel_cell")
	assert_false(v._under_compound(near), "unstaged: nothing covers the lot")
	assert_false(v.compounds.has(&"rebel_cell"))
	assert_false(v.is_cleared(Vector2(at.origin.x, at.origin.z)), "unstaged: the lot is the city's again")
	v.free()


func test_the_backdrop_takes_the_city_close_up_by_tier_and_frames_the_place() -> void:
	assert_false(BackdropCatalog.city_mode(_city, 2, false), "no renderer: the stills")
	for t in _city.backdrop_city_tiers.size():
		assert_eq(BackdropCatalog.city_mode(_city, t, true), _city.backdrop_city_tiers[t], "tier %d" % t)
	var lots := CityLayout.site_points(_solace)
	var site := BackdropCatalog.city_shot(_city, BackdropCatalog.place(&"solace", false, false, &"t1_a"), lots, VIEW)
	# Parity fix S-ARENA round 2: a Site fight frames its own Site's lot (never moved; t1_a does
	# not carry Solace's Site landmark), the Site's building the subject (test_parity_arena_backdrop).
	assert_eq(site["focus"], "site", "a regular fight frames its Site")
	assert_false(site.has("landmark"), "no Site landmark repeated on another Site")
	assert_eq(site["lot"], lots[&"t1_a"])
	assert_eq(site["won_site"], &"t1_a", "the Site's lights turn once won")
	var cam: CityIsoCamera = site["camera"]
	assert_gte(cam.ortho, _city.backdrop_site_ortho, "never closer than the plain Site framing")
	var boss := BackdropCatalog.city_shot(_city, BackdropCatalog.place(&"solace", true, false), lots, VIEW)
	assert_eq(boss["focus"], "hq", "a boss fight frames the HQ")
	assert_eq(boss["stage"], &"")
	var canyon := BackdropCatalog.city_shot(_city, BackdropCatalog.place(&"rebel_cell", true, false), {}, VIEW)
	assert_eq(canyon["focus"], "compound", "DISPATCH's fight is in the canyon")
	assert_eq(canyon["stage"], &"rebel_cell", "the canyon is staged")
	assert_eq((canyon["camera"] as CityIsoCamera).yaw_deg, 180.0, "looking down the street")
	var lost := BackdropCatalog.city_shot(_city, BackdropCatalog.place(&"solace", false, false, &"no_such_site"), lots, VIEW)
	assert_eq(lost["focus"], "hq", "a Site without a lot falls back to the HQ")


func test_compound_materials_map_onto_the_landmark_roles() -> void:
	assert_eq(HqCompoundMaterials.role_of("hq_toon"), 0)
	assert_eq(HqCompoundMaterials.role_of("hq_lit"), 2)
	assert_eq(HqCompoundMaterials.role_of("hq_neon"), 3)
	assert_eq(HqCompoundMaterials.role_of("hq_win"), 4)
	assert_eq(HqCompoundMaterials.role_of("hq_sign"), 8)
	assert_eq(HqCompoundMaterials.role_of("hq_beam"), -1, "the light cone")
	assert_eq(HqCompoundMaterials.role_of("lm_toon"), -2, "only compound names map")


# --- The netrun page's press path -------------------------------------------------------------

## A boss run's page is the compound; pressing the Central Server (its ROUTE button, as the map
## click) opens the gate first, focus on BREACH; Back closes it; BREACH starts the fight.
func test_the_breach_goes_through_the_gate_on_the_netrun_page() -> void:
	RunManager.save_slot = "gut_hq_run_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	var scene: Control = add_child_autofree(load("res://scenes/netrun_map/netrun_scene.tscn").instantiate())
	RunManager.new_campaign(9)
	var c := RunManager.campaign
	for e in [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]:
		c.exploits.append(e)
	var corp := RunManager.corporation
	var boss_site: StringName = &""
	for sd in corp.city_grid.sites:
		if sd != null and sd.objective == RC.SiteObjective.CENTRAL_SERVER:
			boss_site = sd.id
	RunManager.netrun = NetrunSession.start_special(RunManager.resolver, c, c.living_operatives()[0].id, "boss", boss_site, HQ_TIER, 77,
		corp.final_boss.id, CampaignRules.boss_overrides(c, corp), corp)
	scene._show_current()
	assert_not_null(scene.hq_run_view, "the HQ run's page is the compound")
	assert_null(scene.city_overlay, "no transit route on an HQ run")
	var server := RunManager.netrun.run.map.final_node_id()
	scene._request_node(server)
	assert_not_null(scene.gate, "the Central Server's press opens its gate")
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.MAP, "the gate starts nothing")
	await wait_physics_frames(2)
	assert_true(scene.gate.breach_button.has_focus(), "pad focus on BREACH")
	scene.gate.back_pressed.emit()
	assert_null(scene.gate, "Back closes the gate")
	scene._request_node(server)
	scene.gate.breach_pressed.emit()
	assert_null(scene.gate, "BREACH closes the gate")
	assert_true(RunManager.netrun.in_combat(), "BREACH starts the fight")
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true
