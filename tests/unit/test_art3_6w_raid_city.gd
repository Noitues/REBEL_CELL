extends GutTest
## ART-3 6w (bible v2 §4.1, §4.8, Appendix C #13; DECISIONS "Art direction — ART-3 6w"): the raid
## on the unified 3D city, headless. The raid's pages hold the RAID band on the 3D city; the
## raid zoom is fitted to the network and clamped to the config's raid range (the playout too);
## the building nodes are the concept's uplink pads placed by its rule; the picture covers a
## held frame; the SAVED stamp keeps off the Speed / Skip strip. The looks are checked windowed
## (tools/design_lab/raid_lab.tscn, states setup_<corp>, playout_*, uplink_close).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const CITY_CONFIG := preload("res://content/config/city_config.tres")
## A part of the city for the pad tests (lots).
const PART := Rect2i(10, 0, 30, 30)

var cfg: CityConfig = CITY_CONFIG
var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art3_6w"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func HqScript() -> GDScript:
	return load("res://scripts/ui/hq_scene.gd") as GDScript


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


## A campaign with three claimed nodes, a defence and a raid pending.
func _raid_campaign() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"vault_terminal", &"relay"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


# --- The raid zoom (bible §4.1 "fitted to the network", Appendix C #13) -----------------------

func test_the_raid_zoom_fits_the_network_inside_the_config_clamp() -> void:
	var w := 1280.0
	for o in [cfg.raid_fit_min, 300.0, cfg.raid_fit_max]:
		assert_almost_eq(RaidZoomFit.ortho_of(RaidZoomFit.zoom_of(o, w), w), o, 0.001, "zoom and ortho convert both ways")
	var near := PackedVector2Array([Vector2(30, 30), Vector2(31, 31)])
	assert_eq(RaidZoomFit.fit_ortho(cfg, near, Vector2(3000, 2000), w), cfg.raid_fit_min, "a small network in a big free part is clamped to the closest raid zoom")
	var far := PackedVector2Array([Vector2(-60, 0), Vector2(60, 0), Vector2(0, -60), Vector2(0, 60)])
	assert_eq(RaidZoomFit.fit_ortho(cfg, far, Vector2(800, 400), w), cfg.raid_fit_max, "a huge network is clamped to the widest")
	var mid := PackedVector2Array([Vector2(20, 20), Vector2(32, 26), Vector2(26, 34)])
	var o := RaidZoomFit.fit_ortho(cfg, mid, Vector2(800, 400), w)
	assert_between(o, cfg.raid_fit_min, cfg.raid_fit_max)
	var z := RaidZoomFit.zoom_of(o, w)
	var box := RaidZoomFit.box_of(cfg, mid)
	var m := cfg.raid_fit_margin * NeonCity.px_per_bu() * 2.0
	if o > cfg.raid_fit_min + 0.01 and o < cfg.raid_fit_max - 0.01:
		assert_true((box.size.x + m) * z <= 800.01 and (box.size.y + m) * z <= 400.01, "the network and its margin fit the free part")
		assert_true(is_equal_approx((box.size.x + m) * z, 800.0) or is_equal_approx((box.size.y + m) * z, 400.0), "as close as fits")
	assert_eq(RaidZoomFit.fit_ortho(cfg, PackedVector2Array(), Vector2(800, 400), w), cfg.raid_fit_max, "no network: the widest")


func test_the_raid_pages_are_on_the_3d_city_at_the_raid_band_and_fitted() -> void:
	_raid_campaign()
	var hq := _scene(HQ)
	await _frames(1)
	hq.show_raid()
	await _frames(30)
	var city: NeonCity = hq.wireframe.city
	assert_true(hq.wireframe.city3d, "the raid setup is on the unified 3D city")
	assert_eq(city.band_lock, CityLod.Band.RAID, "holding the RAID band (see-through buildings)")
	var ortho := RaidZoomFit.ortho_of(city.scale.x, hq.size.x)
	assert_between(ortho, cfg.raid_fit_min - 0.5, cfg.raid_fit_max + 0.5, "the raid zoom stays in the raid range")
	assert_almost_eq(hq.raid_min_zoom(), RaidZoomFit.zoom_of(cfg.raid_fit_max, hq.size.x), 0.0001, "the framing passes never go wider")
	# HQ-B (c): the setup is the HQ page in place: its free part and the fitted Sites (the network and the routes).
	var free: Rect2 = hq.hq_free_rect()
	var box: Rect2 = hq.wireframe.unrigged(hq.hq_fit_box)
	# Q5: up to the clamp (a network wider than the raid range at raid_fit_max overflows; the
	# wheel zooms out to the GRID band, Q4).
	if ortho < cfg.raid_fit_max - 0.5:
		assert_true(free.grow(1.0).encloses(box), "the nodes sit in the map's free part: %s in %s" % [box, free])
	# The pads go on the Cell's nodes only.
	var ids: Array = []
	for n in hq.raid_uplink_nodes():
		ids.append(n["id"])
		assert_true(RunManager.campaign.grid.is_claimed(n["id"]), "%s: a pad stands on the Cell's own node" % n["id"])
	for id in RunManager.campaign.grid.claimed_ids():
		assert_has(ids, id, "%s: every node of the Cell has its pad" % id)
	# The playout stays in the raid range too.
	assert_almost_eq(RaidZoomFit.ortho_of(hq.playout_zoom(), hq.size.x), cfg.raid_fit_min, 0.01)
	assert_almost_eq(RaidZoomFit.ortho_of(hq.playout_min_zoom(), hq.size.x), cfg.raid_fit_max, 0.01)
	hq.fight_raid()
	await _frames(4)
	assert_has(HqScript().RAID_CITY_PAGES, hq.panel_name, "the playout (headless: straight to the report) is a raid page")
	assert_true(hq.wireframe.city3d and city.band_lock == CityLod.Band.RAID, "the playout too")
	hq.show_raid_summary()
	await _frames(2)
	assert_true(hq.wireframe.city3d and city.band_lock == CityLod.Band.RAID, "and the report")
	hq.show_grid()
	await _frames(2)
	assert_true(hq.wireframe.city3d and city.band_lock == CityLod.Band.RAID, "HQ-B: the Grid is the HQ, at the RAID band (Q4: zoomed out it takes GRID)")
	hq.get_parent().queue_free()
	await _frames(1)


# --- Building nodes as uplink pads (bible §4.8 raid language B) ------------------------------

func test_uplink_pads_are_the_concepts_placed_by_its_rule() -> void:
	var manifest := JSON.parse_string(FileAccess.get_file_as_string("res://assets/raid/uplink/manifest.json")) as Dictionary
	assert_true(str(manifest["source"]["vendor"]).contains("unified40.py"), "the pads come from the concept's own lines")
	assert_eq(float(manifest["settings"]["riser_h"]), RaidUplinkPads.RISER_DRAWN, "the riser's drawn height")
	assert_not_null(RaidUplinkPads.mesh_of(RaidUplinkPads.PAD), "the pad mesh is exported")
	assert_not_null(RaidUplinkPads.mesh_of(RaidUplinkPads.RISER), "the riser mesh is exported")
	var model := CityModel.build(cfg, 7, PART)
	var nodes: Array[Dictionary] = []
	for i in range(PART.position.x + 2, PART.end.x - 2):
		for j in range(PART.position.y + 2, PART.end.y - 2, 3):
			if not RaidUplinkPads.top_prism(model, Vector2i(i, j)).is_empty():
				nodes.append({"id": StringName("n_%d_%d" % [i, j]), "lot": Vector2i(i, j), "door": Vector2(i + 2.5, j + 0.5)})
	assert_gt(nodes.size(), 3, "buildings to test on")
	var pads := RaidUplinkPads.of(model, cfg, nodes)
	assert_gt(pads.size(), 0, "pads are placed")
	for p in pads:
		var pr := RaidUplinkPads.top_prism(model, p["lot"])
		var top := float(pr["y0"]) + float(pr["h"])
		assert_almost_eq(float(p["top"]), top, 0.001, "%s: on the roof" % p["id"])
		assert_true(top >= cfg.uplink_min_top, "%s: a low roof carries none" % p["id"])
		var poly: PackedVector2Array = pr["poly"]
		var lo := poly[0]
		var hi := poly[0]
		for q in poly:
			lo = lo.min(q)
			hi = hi.max(q)
		var want := minf(hi.x - lo.x, hi.y - lo.y) * cfg.uplink_pad_share * clampf(float(pr["taper"]), 0.0, 1.0)
		assert_almost_eq(float(p["half"]), want, 0.001, "%s: the concept's half-size rule" % p["id"])
		var c: Vector3 = p["centre"]
		assert_almost_eq(c.y, top, 0.001)
		# The riser runs up the footprint corner nearest the node's street.
		var door := CityIsoCamera.lot_to_world(cfg, Vector2(p["lot"]) + Vector2(2.5, 0.5))
		var corner: Vector3 = p["corner"]
		for q in poly:
			assert_true(Vector2(corner.x, corner.z).distance_to(Vector2(door.x, door.z)) <= q.distance_to(Vector2(door.x, door.z)) + 0.001,
				"%s: the riser's corner faces the street" % p["id"])
		var xf := RaidUplinkPads.transforms(p)
		assert_almost_eq((xf[RaidUplinkPads.PAD] as Transform3D).basis.get_scale().x, float(p["half"]), 0.001, "the pad scaled to its roof")
		assert_almost_eq((xf[RaidUplinkPads.RISER] as Transform3D).basis.get_scale().y, top / RaidUplinkPads.RISER_DRAWN, 0.001, "the riser reaches the roof")
	var again := RaidUplinkPads.of(model, cfg, nodes)
	assert_eq(str(again), str(pads), "deterministic")
	var empty: Array[Dictionary] = [{"id": &"street", "lot": Vector2i(-500, -500), "door": Vector2(-500, -500)}]
	assert_eq(RaidUplinkPads.of(model, cfg, empty).size(), 0, "no building: no pad")


# --- The picture covers a held frame ---------------------------------------------------------

func test_the_3d_picture_covers_the_held_frame_within_its_cap() -> void:
	var city := NeonCity.new()
	city.set_anchors_preset(Control.PRESET_TOP_LEFT)
	city.size = Vector2(400, 300)
	assert_eq(city.cover_rect(), Rect2(0, 0, 400, 300), "no cover: just the control")
	city.view_cover = Rect2(-100, -50, 600, 400)
	assert_eq(city.cover_rect(), Rect2(-100, -50, 600, 400), "grown to the cover")
	city.view_cover = Rect2(-4000, -4000, 8000, 8000)
	var cap := Rect2(Vector2(200, 150) - Vector2(400, 300) * NeonCity.COVER_MAX * 0.5, Vector2(400, 300) * NeonCity.COVER_MAX)
	assert_eq(city.cover_rect(), cap, "at most COVER_MAX the control's size")
	var cam := city.iso_camera(Rect2(-100, -50, 600, 400))
	assert_almost_eq(cam.ortho, 600.0 / NeonCity.px_per_bu(), 0.001, "the cover's camera shows the cover's width")
	city.free()


# --- The SAVED stamp keeps off the Speed / Skip strip (3A's note) ----------------------------

func test_saved_keeps_off_the_greyed_speed_strip() -> void:
	var root: Control = add_child_autofree(Control.new())
	root.size = SCREEN.size
	var strip := RaidSpeedStrip.new(30)
	root.add_child(strip)
	strip.position = Vector2(1040, 680)
	strip.size = strip.custom_minimum_size
	await _frames(1)
	var avoid := Fx.avoid_rects(root)
	assert_has(avoid, strip.get_global_rect(), "the strip is a rect the stamp keeps off (its keys are drawn, not buttons)")
	var spot := Fx.saved_spot(Vector2(80, 30), SCREEN, avoid)
	assert_false(Rect2(spot, Vector2(80, 30)).intersects(strip.get_global_rect()), "SAVED never lands on SKIP")
