extends Node
## P1: depth + class id + beauty of the Solace raid city at the raid camera (default scenario, seed 7), via IdCapture.
## python tools/run_windowed.py --log <f> -- res://tools/raid_tide/p1_depth_capture.tscn -- --out=<abs dir> --still
const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1920, 1080)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 30
const START_HEAT := 80
const SEED := 7
const ZOOM := 1.5
const CEN := Vector2(722.0, 500.0)
var _out := ""
var _hq: Control = null


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
	DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://p1_depth_settings.json"
	Settings.reduce_effects = true
	Settings.reduce_motion = true
	SaveService.save_dir = "user://saves/p1_depth"
	RunManager.save_slot = "gut_p1_depth"
	RunManager.scene_switching_enabled = false
	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	await _run()
	print("CAPTURE DONE")
	RunManager.delete_save()
	get_tree().quit(0)


func _setup() -> void:
	RunManager.new_campaign(SEED)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	c.schematics = 300
	var ring: Array[StringName] = []
	for l in corp.city_grid.get_site(corp.city_grid.home_site_id).links:
		ring.append(l)
	ring.sort_custom(func(a: StringName, b: StringName) -> bool: return String(a) < String(b))
	for id in ring.slice(0, 4):
		var run := RunState.new()
		run.site_id = id
		CampaignRules.on_run_completed(c, corp, cfg, run)
		CampaignRules.claim(c, corp, cfg, RunManager.lookup(), id, &"relay")
	c.pending_raids.clear()
	c.heat = START_HEAT
	c.raids_won = 0
	c.raids_lost = 0
	c.grid.site(ring[0])["condition"] = GridState.Condition.DOWN
	c.grid.home_integrity -= 6
	c.grid.site(c.grid.home_site_id)["integrity"] = c.grid.home_integrity
	c.pending_raids.append({"raid_id": "raid_claim", "source": RC.RaidTriggerSource.TERRITORY_CLAIM, "site_id": "", "corporation": "solace", "model": "tide"})


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _holds_city(n: Node) -> bool:
	var city: Node = _hq.wireframe.city
	return n == city or n.is_ancestor_of(city) or city.is_ancestor_of(n)


func _run() -> void:
	var hq: Control = HQ.instantiate()
	_hq = hq
	get_tree().root.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	hq.new_campaign(SEED)
	_setup()
	hq.show_raid()
	var city: NeonCity = hq.wireframe.city
	for i in MODEL_WAIT_FRAMES:
		var view: CityView3D = city.view3d
		if view != null and view.model != null and view._pending.is_empty() and view.chunks_built() > 0:
			break
		await get_tree().process_frame
	await _settle(SETTLE_FRAMES * 2)
	var s: TideRaidScreen = hq.tide_screen
	var hidden: Array[CanvasItem] = []
	for c in s.get_children():
		if c is CanvasItem and (c as CanvasItem).visible:
			hidden.append(c)
	for c in _hq.get_children():
		if c is CanvasItem and (c as CanvasItem).visible and c != s and not _holds_city(c):
			hidden.append(c)
	var tm := _hq.find_child("TerritoryMarks", true, false)
	if tm is CanvasItem and (tm as CanvasItem).visible:
		hidden.append(tm)
	if s.overlay != null and s.overlay.visible:
		hidden.append(s.overlay)
	for c in hidden:
		c.visible = false
	var v: CityView3D = _hq.wireframe.city.view3d
	var net := v.layer(&"network")
	if net != null:
		net.visible = false
	await _settle(10)
	if ZOOM != 1.0:
		var iso: CityIsoCamera = v.iso.copy()
		var a: Vector3 = v.unproject(CEN, 0.0)
		var b: Vector3 = v.unproject(Vector2(960, 540), 0.0)
		iso.target += a - b
		iso.ortho = iso.ortho / ZOOM
		v.set_iso(iso)
		await _settle(60)
	var cap: IdCapture = IdCapture.new(get_tree(), v)
	var r: Dictionary = await cap.write(_out, {"kind": "city", "view": "raid", "time": "night"})
	print("CAPTURE idcapture ok=%s counts=%s viewsize=%s" % [r.get("ok"), r.get("counts"), v.size])
	# own depth pass: depth_scale 20 (the IdCapture default 100 saturates: the eye stands ~2600 BU back). R/G bytes = q = BU * 20.
	cap.begin_id()
	var quad := IdCapture.make_depth_quad()
	(quad.material_override as ShaderMaterial).set_shader_parameter(&"depth_scale", 20.0)
	v.camera.add_child(quad)
	for i in 4:
		await get_tree().process_frame
	v.get_texture().get_image().save_png(_out.path_join("depth20_rg.png"))
	quad.queue_free()
	cap.end_id()
	await _settle(4)
	var cam: Camera3D = v.camera
	print("CAPTURE camera ortho=%s xf=%s near=%s far=%s" % [cam.size, cam.global_transform, cam.near, cam.far])
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(_out.path_join("window_nonet.png"))
	hq.queue_free()
