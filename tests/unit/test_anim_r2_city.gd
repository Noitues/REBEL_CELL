extends GutTest
## Animation pass ANIM-R2 (the second fix batch), city, maps and transitions: a map screen
## draws its nodes and labels on its first frame (the baked city's placement answers at once;
## the image fades in when its bake lands), a bake is asked for only once the camera holds
## still and waits on a running one that will cover it, a partial stand-in never shows,
## the jack blocks input before the scene sees it, the bake cache frees everything it holds,
## the Heat banner fits its poster, and the raid playout's step skip takes the one press
## rule. Headless has no renderer: `CityBakeCache.simulate` makes the cities take the baked
## path with nothing built (a test lands a bake with `store`).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _reduce: bool
var _scale: float


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r2_city"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	Motion.force_live = false
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


func _placed_nodes(overlay: CityMapOverlay) -> int:
	var n := 0
	for d: Dictionary in overlay.nodes:
		if overlay.icon_at(d["id"]).x != INF:
			n += 1
	return n


# --- R1: a map is never empty -----------------------------------------------------------------

func test_the_grid_draws_its_nodes_before_any_bake_lands() -> void:
	CityBakeCache.simulate = true
	var hq: Control = _scene(HQ)
	await _frames(1)
	hq.new_campaign(1)
	hq.show_grid()
	await _frames(1)
	var city: NeonCity = hq.wireframe.city
	assert_true(city.is_baked(), "the city takes the baked path")
	assert_false(city.view_covered(), "no bake has landed")
	var overlay: CityMapOverlay = hq.city_overlay
	assert_eq(_placed_nodes(overlay), overlay.nodes.size(), "every node is placed on the first frame")
	assert_false(overlay.label_rects().is_empty(), "and the labels")
	assert_true(city.camera_settled(), "the fit's passes ran under the placement")
	assert_true(hq.arrival_ready(), "a jack lands on it without waiting for the image")


func test_the_route_and_the_raid_setup_draw_their_nodes_before_any_bake() -> void:
	CityBakeCache.simulate = true
	var nr: Control = _scene(NETRUN)
	await _frames(1)
	nr.new_campaign(1)
	nr.start_run(1)
	await _frames(1)
	assert_eq(_placed_nodes(nr.city_overlay), nr.city_overlay.nodes.size(), "route: every node on its first frame")
	assert_false(nr.background.city.view_covered(), "no bake has landed")
	assert_true(nr.arrival_ready(), "the jack in lands on it")
	var hq: Control = _scene(HQ)
	await _frames(1)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var first: StringName = RunManager.corporation.city_grid.get_site(c.grid.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	assert_false(RunManager.pending_raid().is_empty(), "the claim brings a raid")
	hq.show_raid()
	await _frames(1)
	assert_eq(_placed_nodes(hq.city_overlay), hq.city_overlay.nodes.size(), "raid setup: every node on its first frame")


func test_the_placement_answers_before_the_image_and_keeps_when_it_lands() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var bg := WireframeBackground.new()
	holder.add_child(bg)
	RunManager.new_campaign(1)
	bg.set_district(RunManager.campaign.corporation_id)
	var overlay := CityMapOverlay.new(bg.city)
	bg.city.add_child(overlay)
	var g := CityLayout.grid_graph(RunManager.campaign, RunManager.corporation, [])
	overlay.set_graph(g["nodes"], g["edges"])
	await _frames(2)
	var city := bg.city
	var id: StringName = g["nodes"][0]["id"]
	var before := overlay.icon_at(id)
	assert_ne(before.x, INF, "placed without an image")
	assert_eq(city.bake_fade, 0.0, "the sky shows (nothing fades yet)")
	# Streets come from the placement too (the baked city had none: routes cut blocks).
	var streets := 0
	for i in range(-6, 6):
		if city.is_street(i, 0):
			streets += 1
	assert_gt(streets, 0, "the baked city knows its streets")
	# The image lands.
	var look := city.look_key()
	var region := city.bake_region()
	var img := Image.create(8, 8, false, Image.FORMAT_RGBA8)
	CityBakeCache.store(look + "@" + var_to_str(Rect2i(region)), {"look": look, "region": region, "texture": ImageTexture.create_from_image(img), "scale": 1.0,
		"roofs": {}, "beacons": [] as Array[Dictionary], "lights": [] as Array[Dictionary], "trails": [] as Array[Dictionary], "signs": [] as Array[Dictionary]})
	await _frames(2)
	assert_true(city.view_covered(), "the image covers the view")
	assert_eq(city.bake_fade, 1.0, "headless: faded in at once (the end state)")
	assert_eq(overlay.icon_at(id), before, "the nodes stay where they were")


func test_a_bake_is_asked_for_once_the_camera_holds_still() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	# A fit moves the camera every frame for a few frames: no bake is asked for meanwhile.
	for k in 5:
		city.focus_grid = Vector2(k * 7, 3)
		city.refresh()
		await _frames(1)
		assert_true(CityBakeCache._pending.is_empty(), "frame %d: the camera still moves, no bake" % k)
	await _frames(NeonCity.BAKE_SETTLE_FRAMES + 2)
	assert_eq(CityBakeCache._pending.size(), 1, "once it holds still, one bake is asked for")
	# A move inside the region the running bake covers waits on it (no second bake).
	city.focus_grid = Vector2(4 * 7, 3) + Vector2(0.5, 0)
	city.refresh()
	await _frames(NeonCity.BAKE_SETTLE_FRAMES + 2)
	assert_eq(CityBakeCache._pending.size(), 1, "a view the running bake will cover waits on it")


func test_a_partial_stand_in_never_shows() -> void:
	CityBakeCache.simulate = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	await _frames(1)
	city._camera()
	var look := city.look_key()
	var view := city.view_rect()
	var tex := ImageTexture.create_from_image(Image.create(4, 4, false, Image.FORMAT_RGBA8))
	# A strip over a quarter of the view: the sky reads better.
	CityBakeCache.store("strip", {"look": look, "region": Rect2(view.position, Vector2(view.size.x, view.size.y * 0.25)), "texture": tex})
	assert_eq(city._stand_in(look, view), "", "a strip is no stand-in")
	CityBakeCache.store("most", {"look": look, "region": Rect2(view.position, Vector2(view.size.x, view.size.y * 0.95)), "texture": tex})
	assert_eq(city._stand_in(look, view), "most", "nearly all of the view is")


# --- R3: the jack blocks input before the scene sees it -------------------------------------------

var _presses: int = 0


func _count(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed:
		_presses += 1


func test_the_jack_blocks_input_before_the_scene_sees_it() -> void:
	await _frames(1)
	var gate: JackInputGate = Fx.input_gate
	assert_not_null(gate, "the gate is up")
	assert_true(gate.is_inside_tree(), "under the root")
	var scene := InputProbe.new()
	scene.seen.connect(_count)
	get_tree().root.add_child(scene)
	await _frames(1)
	_presses = 0
	var key := InputEventKey.new()
	key.keycode = KEY_SPACE
	key.physical_keycode = KEY_SPACE
	key.pressed = true
	get_viewport().push_input(key)
	assert_eq(_presses, 1, "no jack: the scene's own _input sees the press")
	Fx._set_jacking(true)
	# The arriving scene is added under the root after the gate: the gate moves behind it.
	var arriving := InputProbe.new()
	arriving.seen.connect(_count)
	get_tree().root.add_child(arriving)
	await _frames(1)
	_presses = 0
	var stopped := gate.stopped
	get_viewport().push_input(key)
	var enter := InputEventKey.new()
	enter.keycode = KEY_ENTER
	enter.physical_keycode = KEY_ENTER
	enter.pressed = true
	get_viewport().push_input(enter)
	assert_eq(_presses, 0, "during the jack no scene handler sees Space or Enter")
	assert_eq(gate.stopped - stopped, 2, "the gate stopped both")
	Fx._set_jacking(false)
	get_viewport().push_input(key)
	assert_eq(_presses, 2, "after the jack presses reach the scenes again")
	scene.queue_free()
	arriving.queue_free()


# --- R10 / R11: the bake cache lets go of everything --------------------------------------------

func test_clear_frees_every_baked_texture() -> void:
	var tex := ImageTexture.create_from_image(Image.create(4, 4, false, Image.FORMAT_RGBA8))
	var ref: WeakRef = weakref(tex)
	CityBakeCache.store("a", {"look": "x", "region": Rect2(0, 0, 10, 10), "texture": tex})
	tex = null
	assert_not_null(ref.get_ref(), "the cache holds it")
	CityBakeCache.clear()
	assert_null(ref.get_ref(), "clear() lets it go")
	assert_eq(CityBakeCache.memory_bytes(), 0)


func test_shutdown_stops_a_running_bake_and_frees_its_painter() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	var painter := city.make_painter(Rect2(-1200, -800, 2400, 1600), 1.0)
	var ref: WeakRef = weakref(painter)
	CityBakeCache.request("running", city.look_key(), painter, city)
	CityBakeCache.request("queued", city.look_key(), city.make_painter(Rect2(0, 0, 256, 256), 1.0), city)
	assert_eq(CityBakeCache.busy(), 2, "one builds, one waits for the slot")
	assert_eq(CityBakeCache._building, 1, "one build at a time (R11)")
	CityBakeCache.shutdown()
	assert_null(ref.get_ref(), "the running bake's painter is freed")
	assert_eq(CityBakeCache.busy(), 0, "nothing runs or waits")
	assert_true(CityBakeCache._pending.is_empty())
	await _frames(3)
	assert_false(CityBakeCache.has("running"), "a stopped bake never lands")


func test_a_painter_copies_the_influence() -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	var city := NeonCity.new()
	holder.add_child(city)
	city.bind_campaign(RunManager.campaign, RunManager.corporation)
	assert_false(city.influence.is_empty())
	var painter := city.make_painter(Rect2(0, 0, 64, 64), 1.0)
	assert_true(painter.influence == city.influence, "the same values")
	assert_false(is_same(painter.influence, city.influence), "not the same dictionary (its workers read it)")
	painter.free()


func test_a_threaded_bake_builds_in_slices_and_lets_the_slot_go() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var city := NeonCity.new()
	city.net_mode = true
	holder.add_child(city)
	CityBakeCache.request("small", city.look_key(), city.make_painter(Rect2(0, 0, 256, 192), 1.0), city)
	var rec: Dictionary = CityBakeCache._live.get("small", {})
	assert_false(rec.is_empty(), "the bake runs")
	for k in 600:
		if rec.has("vp") and CityBakeCache._building == 0:
			break
		await _frames(1)
	# (The dummy renderer never draws a frame, so a headless bake stops at its readback.)
	assert_true(rec.has("vp"), "the sliced build ran through and its chunks went in")
	assert_eq(CityBakeCache._building, 0, "the build slot is free for the next bake")
	var painter: NeonCity = rec["painter"]
	assert_true(painter._slices.is_empty(), "the slices are freed")
	assert_true(painter._parts.is_empty(), "the geometry was handed over")
