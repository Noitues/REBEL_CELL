extends Node
## Plan 2 NA-12 capture (windowed only, through tools/run_windowed.py): the per-seed city on the game's City Grid page.
## Per campaign seed it starts a campaign in the HQ scene (the real path: the page's city follows the campaign's city seed),
## opens the Grid page and writes `grid_<seed>.png` (the Grid as fitted) and `city_<seed>.png` (the whole city, zoomed
## out to WHOLE_ORTHO). Prints NA12 lines (campaign seed, city seed, coast side, HQ lots). Frames 800x450. Run:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/city/na12_capture.tscn -- --out=<abs dir>
##       [--seeds=1,2,3]

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1280, 720)
const SHOT := Vector2i(800, 450)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 60
## The whole-city framing (ortho BU) and its centre (lots).
const WHOLE_ORTHO := 1250.0
const WHOLE_CENTRE := Vector2(2.5, 2.5)

var _out := ""


func _ready() -> void:
	var seeds: Array[int] = [1, 2, 3]
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
	for s in seeds:
		await _seed(s)
	print("NA12 DONE")
	RunManager.delete_save()
	get_tree().quit(0)


func _seed(campaign_seed: int) -> void:
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
	print("NA12 campaign=%d city=%s view_seed=%s model_seed=%s coast=%s attempts=%d hqs=%s" % [campaign_seed,
		ArtSeed.u64_str(RunManager.campaign.city_seed), ArtSeed.u64_str(view.city_seed), ArtSeed.u64_str(view.model.city_seed),
		str(plan.coast.get("side", -1)), plan.attempts, " ".join(hqs)])
	await _shot("grid_%d" % campaign_seed)
	hq._frame_city(float(hq.size.x) / (WHOLE_ORTHO * NeonCity.px_per_bu()), WHOLE_CENTRE, Vector2(0.5, 0.5))
	await _settle()
	await _shot("city_%d" % campaign_seed)
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
