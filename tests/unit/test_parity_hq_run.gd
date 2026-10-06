extends GutTest
## Parity S-HQRUN (designer group ruling 2026-10-05; DECISIONS "Parity fix — HQ runs and gate
## (designer group ruling)"; docs/art_review/PARITY/GAPS.md HQRUN-01, 03..08, GATE-01..03):
## the HQ run's page and the Central Server's gate match the round 43 / round 38 concepts
## without the mechanics the rules lack (G6, G11, G12). The page: the title sticker per
## corporation, the HQ MECHANIC terminal presenting today's rules, the state key, name tabs
## and choice numbers, cut-off nodes on a pale backing; the per-corporation framing (Meridian,
## Halcyon, Orbital further out; the DISPATCH canyon an elevated perspective down the street);
## the gate: the concept's bordered panel at its size, the kind words, BREACH under the
## panel, one CENTRAL SERVER label, the page behind blurred; everything on the page at text
## scale 1.0 / 1.6 / 2.0. Headless: maths and layout (frames are read windowed in
## tools/art_pipeline/hq_run/hq_run_lab.tscn; sheet fixes/HQRUN.jpg).

const CORPS: Array[StringName] = [&"meridian", &"solace", &"halcyon", &"orbital", &"rebel_cell"]
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const VIEWS: Array[Vector2] = [Vector2(1280, 720), Vector2(1920, 1080)]
const SEEDS: Array[int] = [1, 7, 42]
const HQ_TIER := 4

var _resolver: CombatResolver
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _solace: CorporationData
var _city: CityConfig = CityView3D.CONFIG
var _scale_before := 1.0


func before_all() -> void:
	_resolver = CombatFixture.resolver()
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()
	_solace = ContentRegistry.get_content(&"solace") as CorporationData


func before_each() -> void:
	_scale_before = Settings.text_scale


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale_before):
		Settings.set_text_scale(_scale_before)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _breach(run_seed: int = 3) -> NetrunSession:
	var c := CampaignRules.new_campaign(_solace, _cfg, _lookup, 3, ContentRegistry.get_content(&"breaker") as ClassData, GridFixture.home_node())
	for e in [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]:
		c.exploits.append(e)
	return NetrunSession.start_special(_resolver, c, c.roster[0].id, "boss", &"the_genome_core", HQ_TIER, run_seed,
		_solace.final_boss.id, CampaignRules.boss_overrides(c, _solace), _solace)


## A full run map half walked (the lab's `full_<corp>`): three nodes walked, the current one's
## next nodes selectable.
func _full(run_seed: int) -> Dictionary:
	var g := MapGenerator.generate(HQ_TIER, _cfg, RngStreams.make_stream(run_seed, &"map"))
	var visited: Array[StringName] = []
	var at: StringName = g.first_layer_ids()[0]
	var current: StringName = &""
	for i in 3:
		visited.append(at)
		var nx: Array = g.get_node(at).get("next", [])
		if nx.is_empty():
			break
		current = at
		at = nx[0]
	var avail: Array[StringName] = []
	for n in g.get_node(current).get("next", []):
		avail.append(n)
	return {"graph": g, "current": current, "visited": visited, "available": avail}


func _page(corp: StringName, view: Vector2, full_seed: int = 0) -> HqRunView:
	var v := HqRunView.new()
	v.size = view
	add_child_autofree(v)
	if full_seed > 0:
		var f := _full(full_seed)
		v.show_run(corp, f["graph"], f["current"], f["visited"], f["available"], "THE CORE")
	else:
		var s := _breach()
		v.show_run(corp, s.run.map, s.run.current_node_id, s.run.visited, s.available_nodes(), "THE CORE")
	return v


# --- HQRUN-01: the title sticker and the state key; the terminal shows today's rules ----------

func test_hqrun_01_title_sticker_per_corporation_and_the_state_key() -> void:
	var words := {&"solace": "SOLACE", &"meridian": "MERIDIAN", &"halcyon": "HALCYON", &"orbital": "ORBITAL", &"rebel_cell": "REBEL_CELL"}
	for corp in CORPS:
		var v := _page(corp, VIEWS[0])
		assert_eq(HqRunView.corp_word(corp), words[corp], "%s: the corporation's short name" % corp)
		# B4 (review Q11): "<CORPORATION>: <CENTRAL SERVER NAME>" until the mechanic names ship.
		assert_eq(v.title_text(), "%s: THE CORE" % words[corp], "%s: the page's title sticker" % corp)
		assert_not_null(v.title_sticker, "%s: the title sticker is built" % corp)
		assert_eq(v.title_sticker.fill, VerbSticker.Fill.YELLOW, "the concept's yellow title sticker")
		assert_eq(v.title_sticker.focus_mode, Control.FOCUS_NONE, "a title takes no focus")
		var keys := v.key_strip.find_child("Keys", true, false)
		assert_eq(keys.get_child_count(), HqRunView.KEY_STATES.size(), "one key per ring state")
		for i in HqRunView.KEY_STATES.size():
			assert_eq(String(keys.get_child(i).name), "Key_%s" % HqRunView.KEY_STATES[i], "the concept's key order")
		assert_false(HqRunView.KEY_WORDS.has("danger"), "no danger ring: the eye is G12")


func test_hqrun_01_the_terminal_presents_the_rules_that_exist() -> void:
	var v := _page(&"solace", VIEWS[0])
	var need := RunManager.config().min_exploits_for_breach
	assert_eq(v.min_exploits, need, "the gate's Exploits come from the campaign config")
	assert_eq(v.mechanic_text.text, tr(HqRunView.BREACH_RULE) % need, "today's run: the breach and its gate")
	assert_eq(v.mechanic.tag_label.text, "STEP 0/1", "the chip: the step of the run")
	assert_string_contains(v.mechanic.title.to_upper(), "HQ MECHANIC")
	var full := _page(&"solace", VIEWS[0], 7)
	assert_eq(full.mechanic_text.text, tr(HqRunView.MAP_RULE) % [full.graph.layer_count(), need], "a full map: its layers")
	assert_eq(full.mechanic.tag_label.text, "STEP 3/%d" % full.graph.layer_count(), "three nodes walked")
	for word in ["HELIX", "CRANE", "TRAIN", "EYE", "MISSILE", "SYNC"]:
		assert_false(v.mechanic_text.text.to_upper().contains(word), "no G12 mechanic in the words (%s)" % word)


func test_hqrun_01_the_page_chrome_fits_at_every_text_size() -> void:
	for view in VIEWS:
		for k in SCALES:
			Settings.set_text_scale(k)
			var v := _page(&"meridian", view)
			await _frames()
			var page := Rect2(Vector2.ZERO, view)
			var rects := v.chrome_rects()
			assert_eq(rects.size(), 3)
			for r in rects:
				assert_true(page.grow(0.5).encloses(r), "%s at %.1f: %s on the page" % [view, k, r])
			assert_gte(rects[0].position.y, HudBar.BAND_HEIGHT, "the title sits under the run's HUD band")
			assert_false(rects[1].intersects(rects[2]), "%s at %.1f: the terminal and the key apart" % [view, k])
			assert_false(rects[0].intersects(rects[1]), "the title clear of the terminal")
			v.free()


# --- HQRUN-03 / 04: markers ---------------------------------------------------------------------

func test_hqrun_03_selectable_nodes_carry_name_tabs_and_numbers() -> void:
	var v := _page(&"solace", VIEWS[1], 7)
	assert_gt(v.available.size(), 0, "the half-walked map has a choice")
	for id: StringName in v.available:
		var words := String(RouteLegend.SHORT[v.kind_of(id)])
		assert_string_contains(v.tab_text(id), words, "%s: the tab names its kind" % id)
		var tab := v.tab_rect(id)
		assert_true(tab.has_area(), "%s: a tab is drawn" % id)
		assert_gt(tab.position.y, v.screen_of(id).y + v.node_radius(id) - 0.5, "%s: the tab sits under its sticker" % id)
		if v.available.size() > 1:
			assert_eq(v.number_of(id), v.available.find(id) + 1, "numbered as the ROUTE window's buttons")
			assert_true(v.tab_text(id).begins_with(str(v.number_of(id))), "the number leads the tab")
	var b := _page(&"solace", VIEWS[1])
	var server := b.graph.final_node_id()
	assert_eq(b.number_of(server), 0, "the breach's one choice is not numbered")
	assert_eq(b.kind_of(server), CityMapOverlay.KIND_RACK, "the Central Server is the rack sticker")


func test_hqrun_04_full_maps_read_on_every_compound() -> void:
	for corp in CORPS:
		for run_seed in SEEDS:
			var v := _page(corp, VIEWS[1], run_seed)
			var page := Rect2(Vector2.ZERO, VIEWS[1])
			var free := v.free_rect(VIEWS[1]).grow(1.0)
			var cut := 0
			for n in v.graph.all_nodes():
				var id: StringName = n["id"]
				assert_true(free.has_point(v.screen_of(id)), "%s seed %d: %s clear of the chrome" % [corp, run_seed, id])
				if v.state_of(id) == RouteOverlay.STATE_CUT:
					cut += 1
			assert_gt(cut, 0, "%s seed %d: a half-walked map has cut-off nodes (small grey discs)" % [corp, run_seed])
			for id: StringName in v.available:
				assert_true(page.encloses(v.tab_rect(id)), "%s seed %d: %s's tab on the page" % [corp, run_seed, id])
			assert_true(free.has_point(v.entry_screen()), "%s: the entry's diamond clear of the chrome" % corp)
			v.free()
	# B4 (review D18): a cut-off node is a small grey disc at 60 % of a sticker, no backing.
	assert_almost_eq(HqRunView.CUT_SHARE, 0.6, 0.001, "cut-off nodes are 60 % discs")


# --- HQRUN-05..08: the framing --------------------------------------------------------------------

## The compound's footprint box (its ground and roof corners) on screen at the page camera.
func _footprint_screen(corp: StringName, cam: CityIsoCamera) -> Rect2:
	var m := HqCompoundStage.manifest(corp)
	var at := HqCompoundStage.place(_city, corp, m)
	var fp: Dictionary = m["footprint"]
	var lo: Array = fp["min"]
	var hi: Array = fp["max"]
	var r := Rect2(cam.project(at * Vector3(float(lo[0]), float(lo[1]), float(lo[2]))), Vector2.ZERO)
	for x in [lo[0], hi[0]]:
		for y in [lo[1], hi[1]]:
			for z in [lo[2], hi[2]]:
				r = r.expand(cam.project(at * Vector3(float(x), float(y), float(z))))
	return r


func test_hqrun_05_06_07_the_corporations_are_framed_as_their_concepts() -> void:
	# B4 (review D18, round 43 `hq_*_compound.png`; art director's fix): an orthographic page
	# stands the union of the compound's footprint and the run's network 55 to 65 % of the
	# frame's height (a wide, low box is held to its width share), for the breach and full maps.
	for corp in [&"solace", &"meridian", &"halcyon", &"orbital"]:
		for run_seed in [0] + SEEDS:
			var v := _page(corp, VIEWS[1], run_seed)
			assert_false(v.iso.perspective(), "%s: the city's iso camera" % corp)
			var share: float = v.landmark_share()
			var box := HqCompoundStage.landmark_box(v.iso, v._manifest, v._at, v.run_points())
			var wide := box.size.x / v.iso.ortho >= _city.hq_run_landmark_width_max - 0.001
			if wide:
				assert_lte(share, _city.hq_run_landmark_share + 0.001, "%s seed %d: a wide box held to the width (%.2f)" % [corp, run_seed, share])
			else:
				assert_between(share, 0.55, 0.65, "%s seed %d: the compound and its run stand %.2f of the height" % [corp, run_seed, share])
			var server: Vector2 = v.screen_of(v.graph.final_node_id())
			assert_true(Rect2(Vector2.ZERO, VIEWS[1]).grow(-HqRunView.FIT_MARGIN_PX).has_point(server), "%s: the Central Server well inside the page" % corp)
			v.free()
	# The combat backdrop keeps the manifest's own camera.
	for corp in CORPS:
		var m := HqCompoundStage.manifest(corp)
		var cam := HqCompoundStage.camera(_city, m, HqCompoundStage.place(_city, corp, m), VIEWS[1])
		assert_false(cam.perspective(), "%s: the backdrop's camera is unchanged" % corp)
		assert_eq(cam.ortho, float(m["settings"]["reference_camera"]["ortho"]))


func test_hqrun_08_the_dispatch_canyon_is_an_angled_view_down_the_street() -> void:
	var corp := &"rebel_cell"
	var m := HqCompoundStage.manifest(corp)
	var l := HqCompoundStage.layout(corp)
	var at := HqCompoundStage.place(_city, corp, m)
	var cam := HqCompoundStage.page_camera(_city, m, at, VIEWS[1])
	assert_true(cam.perspective(), "the canyon's page is a perspective view (round 34's telephoto)")
	assert_eq(cam.fov_deg, float(_city.hq_run_fov_by_corp[corp]))
	assert_between(cam.pitch_deg, 15.0, 30.0, "an elevated view down the street, not near top-down")
	assert_eq(cam.yaw_deg, 180.0, "still down the street toward DISPATCH CORE")
	# Perspective: the canyon's lanes converge toward its head (the near row's outer slots
	# further apart on screen than the far row's), the rows climb up the screen.
	var near_w := cam.project(at * l.slot_position(1, 0)).distance_to(cam.project(at * l.slot_position(1, l.slots_per_layer - 1)))
	var far_w := cam.project(at * l.slot_position(l.layer_rows(), 0)).distance_to(cam.project(at * l.slot_position(l.layer_rows(), l.slots_per_layer - 1)))
	assert_gt(near_w, far_w * 1.15, "the lanes converge down the canyon (near %.0f px, far %.0f px)" % [near_w, far_w])
	for row in range(1, l.layer_rows()):
		assert_lt(cam.project(at * l.slot_position(row + 1, 1)).y, cam.project(at * l.slot_position(row, 1)).y, "row %d further up" % (row + 1))
	# The page keeps the run on screen: the breach and every full map.
	for view in VIEWS:
		var v := _page(corp, view)
		assert_true(v.free_rect(view).grow(1.0).has_point(v.entry_screen()), "%s: the entry clear of the chrome" % view)
		assert_true(v.free_rect(view).grow(1.0).has_point(v.screen_of(v.graph.final_node_id())), "%s: DISPATCH CORE clear of the chrome" % view)
		v.free()
		for run_seed in SEEDS:
			var f := _page(corp, view, run_seed)
			for n in f.graph.all_nodes():
				assert_true(f.free_rect(view).grow(1.0).has_point(f.screen_of(n["id"])), "%s seed %d: %s clear of the chrome (%s in %s)" % [view, run_seed, n["id"], f.screen_of(n["id"]), f.free_rect(view)])
			f.free()


func test_the_perspective_camera_projects_and_picks_consistently() -> void:
	var cam := CityIsoCamera.make(_city, Vector3(10, 4, -3), 120.0, VIEWS[1])
	var ortho := cam.copy()
	cam.fov_deg = 36.9
	cam.pitch_deg = 19.0
	cam.yaw_deg = 180.0
	assert_true(cam.copy().perspective(), "a copy keeps the field of view")
	assert_almost_eq(cam.project(cam.target), VIEWS[1] * 0.5, Vector2(0.01, 0.01), "the target at the centre")
	for p in [Vector2(100, 900), Vector2(960, 540), Vector2(1800, 200)]:
		var w := cam.unproject(p, 0.0)
		assert_almost_eq(w.y, 0.0, 0.001)
		assert_almost_eq(cam.project(w), p, Vector2(0.05, 0.05), "pick and project agree at %s" % p)
	var e := cam.eye_distance()
	assert_almost_eq(e, 120.0 * 0.5 / tan(deg_to_rad(36.9) * 0.5), 0.001, "the eye frames `ortho` at the target")
	assert_almost_eq(cam.transform().origin.distance_to(cam.target), e, 0.001)
	assert_eq(cam.project(cam.eye() - cam.forward() * 5.0), Vector2.INF, "behind the eye: nothing")
	# Orthographic cameras are unchanged.
	assert_false(ortho.perspective())
	assert_eq(ortho.eye_distance(), ortho.distance)
	var w0 := ortho.target + ortho.right() * 30.0 + ortho.up() * 10.0
	assert_almost_eq(ortho.project(w0), Vector2((30.0 / ortho.ortho + 0.5) * VIEWS[1].x, (0.5 - 10.0 / (ortho.ortho * 9.0 / 16.0)) * VIEWS[1].y),
		Vector2(0.01, 0.01), "the iso projection as before")


# --- GATE-01..03 ----------------------------------------------------------------------------------

func _gate(held: Array[int]) -> CentralServerGate:
	var g := CentralServerGate.new()
	var s := _breach(5)
	g.setup(&"meridian", "Meridian Freight Systems", "THE MASTER MANIFEST", HQ_TIER, held, _cfg.min_exploits_for_breach, s.breach_preview(), _lookup)
	add_child_autofree(g)
	return g


func test_gate_01_the_panel_is_the_concepts_bordered_card() -> void:
	var all: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	var g := _gate(all)
	var box := g.panel.get_theme_stylebox(&"panel") as StyleBoxFlat
	assert_not_null(box, "a drawn card, not the terminal window")
	assert_eq(box.border_width_left, CentralServerGate.PANEL_EDGE, "the edge all round")
	assert_eq(box.border_color, Palette.corp_color(&"meridian"), "ready: the edge in the corp colour")
	assert_eq(box.corner_radius_top_left, CentralServerGate.PANEL_RADIUS, "rounded as the concept")
	assert_eq(box.bg_color, CentralServerGate.PANEL_FILL, "the concept's dark glass")
	for i in CentralServerGate.KINDS.size():
		var holder := g.panel.find_child("Holder%d" % (i + 1), true, false)
		var word := holder.find_child("Kind", true, false) as Label
		assert_eq(word.text, tr(CentralServerGate.KIND_WORDS[CentralServerGate.KINDS[i]]), "the kind word under socket %d" % i)
	var one: Array[int] = [RC.ExploitType.BREACH]
	var locked := _gate(one)
	var lbox := locked.panel.get_theme_stylebox(&"panel") as StyleBoxFlat
	assert_eq(lbox.border_color, CentralServerGate.EDGE_IDLE, "short of Exploits: the grey edge")


func test_gate_01_breach_under_the_panel_and_everything_fits_at_every_text_size() -> void:
	var all: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	for view in VIEWS:
		for k in SCALES:
			Settings.set_text_scale(k)
			var host := Control.new()
			host.size = view
			add_child_autofree(host)
			var g := CentralServerGate.new()
			var s := _breach(5)
			g.setup(&"solace", "Solace Biosystems", "THE GENOME CORE", HQ_TIER, all, _cfg.min_exploits_for_breach, s.breach_preview(), _lookup)
			host.add_child(g)
			await _frames()
			var r := g.layout_rects()
			var page := Rect2(Vector2.ZERO, view)
			for key: String in r:
				assert_true(page.grow(0.5).encloses(r[key]), "%s at %.1f: %s on the page (%s)" % [view, k, key, r[key]])
			assert_gt(r["breach"].position.y, r["panel"].end.y - 0.5, "%s at %.1f: BREACH under the panel" % [view, k])
			assert_true(r["panel"].has_point(Vector2(r["breach"].get_center().x, r["panel"].get_center().y)), "BREACH within the panel's width")
			for a: String in ["panel", "breach", "back"]:
				assert_false(r[a].intersects(r["wheel"]), "%s at %.1f: %s clear of the wheel" % [view, k, a])
			assert_gt(r["wheel"].get_center().x, view.x * 0.5, "the wheel right of centre")
			host.free()


func test_gate_02_one_server_label_while_the_gate_is_open() -> void:
	var v := _page(&"solace", VIEWS[0])
	assert_false(v.gate_open)
	assert_true(v.chip_rect().has_area(), "the page names its Central Server")
	var all: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	var g := _gate(all)
	assert_true(v.gate_open, "the gate tells the page it is open")
	for c: Control in [v.title_sticker, v.mechanic, v.key_strip]:
		assert_false(c.visible, "%s steps aside under the gate" % c.name)
	assert_string_contains((g.panel.find_child("ServerTitle", true, false) as Label).text, "THE MASTER MANIFEST", "the gate's header names it once")
	var again := _gate(all)
	g.free()
	assert_true(v.gate_open, "an old gate leaving keeps the newer gate's page as it is")
	again.free()
	assert_false(v.gate_open, "closing the gate gives the page its chip back")
	for c: Control in [v.title_sticker, v.mechanic, v.key_strip]:
		assert_true(c.visible)


func test_gate_03_the_page_behind_is_blurred_and_dimmed() -> void:
	var all: Array[int] = [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]
	var g := _gate(all)
	assert_true(g.scrim is GlassScrim, "the shared blur-and-dim scrim")
	assert_eq(g.scrim.opaque(), Settings.high_contrast, "blurred unless high contrast asks for opaque")
	assert_eq(g.scrim.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	assert_eq(g.mouse_filter, Control.MOUSE_FILTER_STOP, "the gate stops clicks meant for the page")
	assert_between(CentralServerGate.SHADE_ALPHA, 0.0, 1.0)


## The page frames the run between the HUD band (and the chip's room) and the foot's chrome
## as laid out. At 1.6 and 2.0 on a 1280 x 720 page the foot is tall: the run stays on the page and
## the chip under the band, the frame at most FIT_MAX_SHARE wider than the concept's.
func test_the_run_stays_clear_of_the_chrome_at_every_text_size() -> void:
	for k in SCALES:
		Settings.set_text_scale(k)
		for corp in CORPS:
			var v := _page(corp, VIEWS[0])
			await _frames()
			var free := v.free_rect(VIEWS[0])
			var page := Rect2(Vector2(0, HudBar.BAND_HEIGHT), VIEWS[0] - Vector2(0, HudBar.BAND_HEIGHT))
			var area := free.grow(1.0) if k < 1.5 else page
			assert_true(area.has_point(v.entry_screen()), "%s at %.1f: the entry clear of the chrome" % [corp, k])
			assert_true(area.has_point(v.screen_of(v.graph.final_node_id())), "%s at %.1f: the server clear of the chrome" % [corp, k])
			assert_gte(v.chip_rect().position.y, HudBar.BAND_HEIGHT - 0.5, "%s at %.1f: the chip under the HUD band" % [corp, k])
			var m := HqCompoundStage.manifest(corp)
			var ref := HqCompoundStage.page_camera(_city, m, HqCompoundStage.place(_city, corp, m), VIEWS[0])
			assert_lte(v.iso.ortho, ref.ortho * HqRunView.FIT_MAX_SHARE + 0.01, "%s at %.1f: never zoomed far out" % [corp, k])
			v.free()
