extends Node
## G1 parity capture: the live raid city (HQ page, seeded Solace campaign, no net layer) at the golden plates' camera, saved as PNG frames.
## Windowed only: python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://tools/look_parity/parity_capture.tscn -- --out=<abs dir> [--still] [--name=<stem>] [--frames=N] [--perf]
## The plate camera is STYLE_CONTRACT 2: zoom 1.5 about plate px (722, 500), ortho 394.59 BU. --still is the reduce-effects mode the plate base was taken in.
## --perf measures wall-clock frame times over --frames frames instead of saving images.

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1920, 1080)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 30
const START_HEAT := 80
const SEED := 7
const ZOOM := 1.5
const CEN := Vector2(722.0, 500.0)
## Sanity runs on other seeds and cameras: --seed=N, --zoom=Z, --cen=x,y (view px to bring to the screen centre).
var _seed := SEED
var _zoom := ZOOM
var _cen := CEN
const PERF_WARMUP := 60

var _out := ""
var _name := "godot"
var _still := false
var _perf := false
var _frames := 1
var _quality := ""
var _debug := 0
var _off := 0
var _level := -1
var _opaque := false
var _post_set: Array[String] = []
var _no_finish := false
var _grade_path := ""
var _hq: Control = null


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--name="):
			_name = a.trim_prefix("--name=")
		elif a.begins_with("--frames="):
			_frames = int(a.trim_prefix("--frames="))
		elif a.begins_with("--quality="):
			_quality = a.trim_prefix("--quality=")
		elif a.begins_with("--g1-debug="):
			_debug = int(a.trim_prefix("--g1-debug="))
		elif a.begins_with("--g1-off="):
			_off = int(a.trim_prefix("--g1-off="))
		elif a.begins_with("--g1-level="):
			_level = int(a.trim_prefix("--g1-level="))
		elif a.begins_with("--grade="):
			_grade_path = a.trim_prefix("--grade=")
		elif a == "--no-finish":
			_no_finish = true
		elif a.begins_with("--post="):
			_post_set.append(a.trim_prefix("--post="))
		elif a.begins_with("--seed="):
			_seed = int(a.trim_prefix("--seed="))
		elif a.begins_with("--zoom="):
			_zoom = float(a.trim_prefix("--zoom="))
		elif a.begins_with("--cen="):
			var xy := a.trim_prefix("--cen=").split(",")
			_cen = Vector2(float(xy[0]), float(xy[1]))
		elif a == "--opaque":
			_opaque = true
		elif a == "--still":
			_still = true
		elif a == "--perf":
			_perf = true
	DirAccess.make_dir_recursive_absolute(_out)
	if _grade_path != "":
		CityGradeLook.use(load(_grade_path) as CityGradeConfig)
	Settings.path = "user://look_parity_settings.json"
	Settings.reduce_effects = _still
	Settings.reduce_motion = _still
	SaveService.save_dir = "user://saves/look_parity"
	RunManager.save_slot = "gut_look_parity"
	RunManager.scene_switching_enabled = false
	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	await _run()
	print("PARITY DONE")
	RunManager.delete_save()
	get_tree().quit(0)


func _setup() -> void:
	RunManager.new_campaign(_seed)
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
	_hq = HQ.instantiate()
	get_tree().root.add_child(_hq)
	_hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	_hq.new_campaign(_seed)
	_setup()
	_hq.show_raid()
	var city: NeonCity = _hq.wireframe.city
	for i in MODEL_WAIT_FRAMES:
		var view: CityView3D = city.view3d
		if view != null and view.model != null and view._pending.is_empty() and view.chunks_built() > 0:
			break
		await get_tree().process_frame
	await _settle(SETTLE_FRAMES * 2)
	var s: TideRaidScreen = _hq.tide_screen
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
	var v: CityView3D = city.view3d
	var net := v.layer(&"network")
	if net != null:
		net.visible = false
	await _settle(10)
	var iso: CityIsoCamera = v.iso.copy()
	var a: Vector3 = v.unproject(_cen, 0.0)
	var b: Vector3 = v.unproject(Vector2(960, 540), 0.0)
	iso.target += a - b
	iso.ortho = iso.ortho / _zoom
	v.set_iso(iso)
	await _settle(60)
	if _no_finish:
		# Look-dev only: the 2D finish off, so the post output can be compared stage by stage with the plates Python (which finishes last).
		city._view.material = null
		v.set_finish_2d(false)
		v.post_material().set_shader_parameter(&"g1_finish_2d", true)
	for kv in _post_set:
		# Look-dev: --post=name=number (or a,b,c for a vector) sets a city_post uniform.
		var parts := kv.split("=")
		var vs := parts[1].split(",")
		var val: Variant = float(vs[0]) if vs.size() == 1 else (Vector3(float(vs[0]), float(vs[1]), float(vs[2])) if vs.size() == 3 else Vector2(float(vs[0]), float(vs[1])))
		v.post_material().set_shader_parameter(StringName(parts[0]), val)
	if _opaque:
		# Look-dev: opaque buildings in the legacy post too, for the plate-target base capture.
		v.post_material().set_shader_parameter(&"opacity", 1.0)
		v.post_material().set_shader_parameter(&"has_ground", false)
	if _level >= 0:
		v.post_material().set_shader_parameter(&"g1_level", _level)
	if _off > 0:
		v.post_material().set_shader_parameter(&"g1_off", _off)
	if _debug > 0:
		v.post_material().set_shader_parameter(&"g1_debug", _debug)
		await _settle(10)
	print("PARITY facades=%s seed=%s" % [v.facades.get_child_count() if v.facades != null else -1, v.city_seed])
	print("PARITY camera ortho=%s still=%s view=%s map_look=%s band_lock=%s" % [v.camera.size, _still, v.size, v.map_look(), v.band_lock])
	if _perf:
		await _run_perf()
	else:
		for i in _frames:
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(_out.path_join("%s_%02d.png" % [_name, i]) if _frames > 1 else _out.path_join(_name + ".png"))
			await _settle(2)
	_hq.queue_free()


## Frame times over `_frames` frames after a warm-up. The window runs at its 60 Hz cap under run_windowed (vsync cannot be lifted), so wall clock only shows
## the p95 headroom; the GPU time of the city view and of the window is the number that counts (RenderingServer measured render time).
func _run_perf() -> void:
	var v: CityView3D = _hq.wireframe.city.view3d
	var rids: Array[RID] = [v.get_viewport_rid(), get_tree().root.get_viewport_rid()]
	for r in rids:
		RenderingServer.viewport_set_measure_render_time(r, true)
	await _settle(PERF_WARMUP)
	var times: Array[float] = []
	var gpu_city: Array[float] = []
	var gpu_all: Array[float] = []
	var last := Time.get_ticks_usec()
	for i in _frames:
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		times.append(float(now - last) / 1000.0)
		last = now
		gpu_city.append(RenderingServer.viewport_get_measured_render_time_gpu(rids[0]))
		gpu_all.append(RenderingServer.viewport_get_measured_render_time_gpu(rids[1]))
	print("PERF name=%s still=%s frames=%d wall %s" % [_name, _still, times.size(), _stats(times)])
	print("PERF name=%s gpu_city %s" % [_name, _stats(gpu_city)])
	print("PERF name=%s gpu_window %s" % [_name, _stats(gpu_all)])


func _stats(a: Array[float]) -> String:
	var t := a.duplicate()
	t.sort()
	var n := t.size()
	var sum := 0.0
	for x in t:
		sum += x
	return "mean_ms=%.2f p50_ms=%.2f p95_ms=%.2f p99_ms=%.2f max_ms=%.2f" % [sum / float(maxi(n, 1)), t[n / 2], t[mini(n - 1, int(float(n) * 0.95))], t[mini(n - 1, int(float(n) * 0.99))], t[n - 1]]
