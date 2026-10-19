extends Node
## Plan 2 NA-12 capture (windowed only, through tools/run_windowed.py): the per-seed city on the game's City Grid page.
## Per campaign seed it starts a campaign in the HQ scene (the real path: the page's city follows the campaign's city seed),
## opens the Grid page and writes `grid_<seed>.png` (the Grid as fitted) and `city_<seed>.png` (the whole city, zoomed
## out to WHOLE_ORTHO, night); for the first seed also `shore_<seed>.png` (the bay head close at SHORE_ORTHO: sea wall,
## piers, reflections), `look_<seed>.png` (that close under the netrun look, look_blend 1) and `day_<seed>.png` (the
## whole city by day, the motion layers' real crossfade). Prints NA12 lines (campaign seed, city seed, coast side, HQ
## lots, piers, wall edges). Frames 800x450. Run:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/city/na12_capture.tscn -- --out=<abs dir>
##       [--seeds=1,2]

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1280, 720)
const SHOT := Vector2i(800, 450)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 60
## The whole-city framing (ortho BU) and its centre (lots); the shoreline close (ortho BU).
const WHOLE_ORTHO := 1250.0
const WHOLE_CENTRE := Vector2(2.5, 2.5)
const SHORE_ORTHO := 240.0
## The shoreline close looks this many lots out to sea from the bay head (half sea, half shore).
const SHORE_SEA_LOTS := 8.0

var _out := ""


func _ready() -> void:
	var seeds: Array[int] = [1, 2]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--seeds="):
			seeds.clear()
			for s in a.trim_prefix("--seeds=").split(",", false):
				seeds.append(int(s))
	DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://na12_capture_settings.json"
	SaveService.save_dir = "user://saves/na12_capture"
	RunManager.save_slot = "gut_na12_capture"
	RunManager.scene_switching_enabled = false
	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	for k in seeds.size():
		await _seed(seeds[k], k == 0)
	print("NA12 DONE")
	RunManager.delete_save()
	get_tree().quit(0)


func _seed(campaign_seed: int, extras: bool) -> void:
	var hq: Control = HQ.instantiate()
	get_tree().root.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	hq.new_campaign(campaign_seed)
	hq.show_grid()
	var city: NeonCity = hq.wireframe.city
	city.follow_city_seed()
	var view: CityView3D = null
	for i in MODEL_WAIT_FRAMES:
		view = city.view3d
		if view != null and view.model != null and view._pending.is_empty() and view.chunks_built() > 0:
			break
		await get_tree().process_frame
	if view == null or view.model == null:
		print("NA12 FAIL seed=%d no view" % campaign_seed)
		hq.queue_free()
		return
	await _settle()
	var plan := CityPlan.current()
	var hqs := []
	for t in plan.territories:
		if t["id"] != &"":
			hqs.append("%s@%s" % [t["id"], t["at"]])
	print("NA12 campaign=%d city=%s view_seed=%s model_seed=%s sea=%s attempts=%d piers=%d wall=%d hqs=%s" % [campaign_seed,
		ArtSeed.u64_str(RunManager.campaign.city_seed), ArtSeed.u64_str(view.city_seed), ArtSeed.u64_str(view.model.city_seed),
		plan.sea_side(), plan.attempts, view.water.piers if view.water != null else -1, view.water.wall_edges if view.water != null else -1,
		" ".join(hqs)])
	await _shot("grid_%d" % campaign_seed)
	hq._frame_city(float(hq.size.x) / (WHOLE_ORTHO * NeonCity.px_per_bu()), WHOLE_CENTRE, Vector2(0.5, 0.5))
	await _settle()
	await _shot("city_%d" % campaign_seed)
	if extras:
		var head := float(plan.coast["bay_at"])
		var shore := plan.edge_point(head, plan.shore_at(head) - SHORE_SEA_LOTS)
		hq._frame_city(float(hq.size.x) / (SHORE_ORTHO * NeonCity.px_per_bu()), shore, Vector2(0.5, 0.5))
		await _settle()
		await _shot("shore_%d" % campaign_seed)
		view.set_look_blend(1.0)
		await _settle()
		await _shot("look_%d" % campaign_seed)
		view.set_look_blend(0.0)
		hq._frame_city(float(hq.size.x) / (WHOLE_ORTHO * NeonCity.px_per_bu()), WHOLE_CENTRE, Vector2(0.5, 0.5))
		var lay := city.city_motion.layers if city.city_motion != null else null
		if lay != null:
			lay.set_light(CityMotionLayers.Daylight.DAY, false)
			await _settle(roundi(Motion.seconds(CityMotionLayers.LIGHT_FADE) * 60.0) + SETTLE_FRAMES)
			print("NA12 day share=%.2f" % view.night_share)
			await _shot("day_%d" % campaign_seed)
	hq.queue_free()
	RunManager.reset()
	await get_tree().process_frame
	await get_tree().process_frame


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.resize(SHOT.x, SHOT.y, Image.INTERPOLATE_BILINEAR)
	img.save_png(_out.path_join(name_ + ".png"))
