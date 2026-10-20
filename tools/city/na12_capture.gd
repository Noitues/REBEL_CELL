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
const WHOLE_ORTHO := 1900.0
const WHOLE_CENTRE := Vector2(2.5, 2.5)
const SHORE_ORTHO := 240.0
## The shoreline close looks this many lots out to sea from the bay head (half sea, half shore).
const SHORE_SEA_LOTS := 8.0
## The bay crop: ortho BU and how many lots out to sea from the bay head it centres.
const BAY_ORTHO := 600.0
const BAY_LOTS := 18.0
## Value strip: lots sampled on a grid this many lots apart over the view.
const SAMPLE_STEP := 3

## CITY-A2 r2: the art-pass golden plate camera (docs/concepts/golden_plates/city_a2_night_capture.json, Blender BU of
## art-pass's A2 scale, PLATE_M_PER_BU metres each): eye and target, lens (mm on a 36 mm wide sensor).
const PLATE_EYE := Vector3(12.0, -960.0, 615.0)
const PLATE_TGT := Vector3(12.0, -12.0, 0.0)
const PLATE_LENS_MM := 28.0
const PLATE_SENSOR_MM := 36.0
const PLATE_M_PER_BU := 100.0 / 6.0

var _out := ""
## --plate=1: the whole-city shots (v_city / v_day) through the plate camera (perspective) instead of the map framing.
var _plate := false
## --lit=1 (diagnosis only): the ground layer under a plain lit vertex-colour material, so the relief reads.
var _lit := false
## --top=1 (diagnosis only): art-pass's dbg_top camera instead (pitch 70, 900 BU over A2's origin).
var _top := false


func _ready() -> void:
	var seeds: Array[int] = [1, 2]
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--plate="):
			_plate = a.trim_prefix("--plate=") == "1"
		elif a.begins_with("--top="):
			_top = a.trim_prefix("--top=") == "1"
		elif a.begins_with("--lit="):
			_lit = a.trim_prefix("--lit=") == "1"
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
	print("NA12 campaign=%d city=%s view_seed=%s model_seed=%s sea=%s piers=%d wall=%d smears=%d hqs=%s" % [campaign_seed,
		ArtSeed.u64_str(RunManager.campaign.city_seed), ArtSeed.u64_str(view.city_seed), ArtSeed.u64_str(view.model.city_seed),
		plan.sea_side(), view.water.piers if view.water != null else -1, view.water.wall_edges if view.water != null else -1, view.water.smears if view.water != null else -1,
		" ".join(hqs)])
	if view.water != null:
		print("NA12 smear_lots %s" % str(view.water.smear_lots))
	await _shot("grid_%d" % campaign_seed)
	hq._frame_city(float(hq.size.x) / (WHOLE_ORTHO * NeonCity.px_per_bu()), Vector2(plan.rect.get_center()), Vector2(0.5, 0.5))
	await _settle()
	await _shot("city_%d" % campaign_seed)
	if _plate and plan.a2 != null:
		_plate_cam(view, plan)
		await _settle()
	await _view_shot(view, "v_city_%d" % campaign_seed)
	_values(view, plan, "night")
	if extras and plan.a2 != null:  # CITY-A2 step 2: the bay head is A2's Old City shore, the bay due south of it
		var head := plan.a2.lot_of(plan.a2.a2.old_city_centre)
		var shore := head + Vector2(0.0, SHORE_SEA_LOTS)
		hq._frame_city(float(hq.size.x) / (SHORE_ORTHO * NeonCity.px_per_bu()), shore, Vector2(0.5, 0.5))
		await _settle()
		await _shot("shore_%d" % campaign_seed)
		var bay := head + Vector2(0.0, BAY_LOTS)
		hq._frame_city(float(hq.size.x) / (BAY_ORTHO * NeonCity.px_per_bu()), bay, Vector2(0.5, 0.5))
		await _settle()
		await _view_shot(view, "v_bay_%d" % campaign_seed)
		view.set_look_blend(1.0)
		await _settle()
		await _shot("look_%d" % campaign_seed)
		view.set_look_blend(0.0)
		hq._frame_city(float(hq.size.x) / (WHOLE_ORTHO * NeonCity.px_per_bu()), Vector2(plan.rect.get_center()), Vector2(0.5, 0.5))
		var lay := city.city_motion.layers if city.city_motion != null else null
		if lay != null:
			lay.set_light(CityMotionLayers.Daylight.DAY, false)
			await _settle(roundi(Motion.seconds(CityMotionLayers.LIGHT_FADE) * 60.0) + SETTLE_FRAMES)
			print("NA12 day share=%.2f" % view.night_share)
			await _shot("day_%d" % campaign_seed)
			if _plate:
				_plate_cam(view, plan)
				await _settle()
			await _view_shot(view, "v_day_%d" % campaign_seed)
			_values(view, plan, "day")
			hq._frame_city(float(hq.size.x) / (BAY_ORTHO * NeonCity.px_per_bu()), bay, Vector2(0.5, 0.5))
			await _settle()
			await _view_shot(view, "v_bayday_%d" % campaign_seed)
	hq.queue_free()
	RunManager.reset()
	await get_tree().process_frame
	await get_tree().process_frame


## Points `view` through the art-pass plate camera: Blender BU -> A2 metres -> lots -> world, heights by the game's BU.
func _plate_cam(view: CityView3D, plan: CityPlan) -> void:
	var cfg := view.cfg
	var to_world := func(b: Vector3) -> Vector3:
		var lot: Vector2 = plan.a2.lot_of(Vector2(b.x, b.y) * PLATE_M_PER_BU)
		return CityIsoCamera.lot_to_world(cfg, lot, b.z * PLATE_M_PER_BU / plan.a2.metres_per_lot * cfg.lot_bu)
	var eye: Vector3 = to_world.call(PLATE_EYE)
	var tgt: Vector3 = to_world.call(PLATE_TGT)
	if _top:
		eye = to_world.call(Vector3(0.0, -900.0 * cos(deg_to_rad(70.0)), 900.0 * sin(deg_to_rad(70.0))))
		tgt = to_world.call(Vector3.ZERO)
	var d := eye - tgt
	var cam := view.iso.copy()
	cam.target = tgt
	cam.yaw_deg = rad_to_deg(atan2(d.z, -d.x))  # forward = -d: (cos yaw, -, -sin yaw)
	cam.pitch_deg = rad_to_deg(atan2(d.y, Vector2(d.x, d.z).length()))
	cam.fov_deg = rad_to_deg(2.0 * atan(PLATE_SENSOR_MM * 0.5 / PLATE_LENS_MM))
	cam.ortho = 2.0 * d.length() * tan(deg_to_rad(cam.fov_deg) * 0.5)
	view.set_iso(cam)
	print("NA12 plate eye=%s tgt=%s yaw=%.1f pitch=%.1f fov=%.1f" % [eye, tgt, cam.yaw_deg, cam.pitch_deg, cam.fov_deg])
	if _lit:
		view.layer(&"network").visible = false
		var m := StandardMaterial3D.new()
		m.vertex_color_use_as_albedo = true
		m.albedo_color = Color(0.6, 0.6, 0.6)
		for n in view.layer(&"ground").find_children("*", "MeshInstance3D", true, false):
			var gm := n as MeshInstance3D
			if not gm.name.begins_with("Ground") and gm.mesh != null:
				print("NA12 mesh %s visible=%s aabb=%s" % [gm.get_path(), gm.is_visible_in_tree(), gm.global_transform * gm.get_aabb()])
			gm.material_override = m
		for n in view.find_children("*", "MeshInstance3D", true, false):
			var mi := n as MeshInstance3D
			if mi.material_override == view._ground_mat or mi.name == "OuterLand":
				mi.material_override = m


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.resize(SHOT.x, SHOT.y, Image.INTERPOLATE_BILINEAR)
	img.save_png(_out.path_join(name_ + ".png"))


## The 3D view's own frame (no HUD over it), written as a PNG at the view's size.
func _view_shot(view: CityView3D, name_: String) -> void:
	await RenderingServer.frame_post_draw
	view.get_texture().get_image().save_png(_out.path_join(name_ + ".png"))


## Prints and writes the median luminance of the void, the sea and the land in the whole-city view: lots on a grid
## (land / sea by the plan; the void is the ring past the water's extent), sampled where they project into the view.
func _values(view: CityView3D, plan: CityPlan, tag: String) -> void:
	var img := view.get_texture().get_image()
	var cfg := view.cfg
	var land: Array[float] = []
	var sea: Array[float] = []
	var voids: Array[float] = []
	var r := plan.rect.grow(cfg.water_extend_lots + 4)
	var x := r.position.x
	while x < r.end.x:
		var y := r.position.y
		while y < r.end.y:
			var p := view.iso.project(CityIsoCamera.lot_to_world(cfg, Vector2(x + 0.5, y + 0.5)))
			if p.x >= 8 and p.y >= 8 and p.x < img.get_width() - 8 and p.y < img.get_height() - 8:
				var c := img.get_pixelv(Vector2i(p))
				var lum := 0.2126 * c.r + 0.7152 * c.g + 0.0722 * c.b
				if plan.is_water(x, y):
					sea.append(lum)
				elif not plan.rect.has_point(Vector2i(x, y)):
					voids.append(lum)
				else:
					land.append(lum)
			y += SAMPLE_STEP
		x += SAMPLE_STEP
	print("NA12 VALUES %s void=%.4f (n=%d) sea=%.4f (n=%d) land=%.4f (n=%d)" % [tag, _median(voids), voids.size(), _median(sea), sea.size(), _median(land), land.size()])


func _median(a: Array[float]) -> float:
	if a.is_empty():
		return -1.0
	var b := a.duplicate()
	b.sort_custom(func(x: float, y: float) -> bool: return x < y)
	return b[b.size() / 2]
