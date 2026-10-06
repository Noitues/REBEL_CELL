extends Node
## ART-7 3B capture walk (dev tool, never exported): ONE windowed launch that steps the netrun
## route through its states and writes a PNG per state, for reading next to the references
## (docs/art_reference/netrun/). Run only through tools/run_windowed.py:
##   res://tools/design_lab/netrun_states.tscn -- --out=<abs dir> [--states=a,b] [--size=1280x720]
## States: start, underway, show_all, heat, meridian_16, halcyon_20, orbital, rebel_cell,
## close (ART-7 7w: the route zoomed in to a close-up, the CLOSE car tier), event, jack.
## `--perf=<s>`: after each route state, a frame-time probe (PERF lines: the frame and the 3D
## city's own GPU / CPU time). Every state prints its camera (CAM lines: ortho, band, car tier).
## Sets the run up the way the motion lab and DemoSetup do (a dev tool may write a demo
## campaign; the screens never do). Saves to its own slot; restores the text size.

const NETRUN := preload("res://scenes/netrun_map/netrun_scene.tscn")
const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SLOT := "gut_netrun_states"
const SETTLE := 20
const BAKE_FRAMES := 600
const ALL_STATES := ["start", "underway", "show_all", "heat", "meridian_16", "halcyon_20", "orbital", "rebel_cell", "close",
	"event", "jack"]
## ART-7 7w: the close-up's ortho (BU; round 40 cars_lod shows CLOSE at a netrun close-up).
const CLOSE_ORTHO := 60.0
## Seconds into the jack-in at which frames are written.
const JACK_TIMES: Array[float] = [0.6, 1.4, 2.2, 3.0, 3.6, 4.2, 4.8, 5.6, 6.6, 8.0]

var _out := ""
var _perf_s := 0.0
var _scene: Node = null


func _ready() -> void:
	var states: Array = ALL_STATES.duplicate()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--perf="):
			_perf_s = float(a.trim_prefix("--perf="))
		elif a.begins_with("--states="):
			states = a.trim_prefix("--states=").split(",", false)
		elif a.begins_with("--size="):
			# The quiet window ignores --resolution: size it here (e.g. 1920x1080 for the perf budget).
			var wh := a.trim_prefix("--size=").split("x")
			DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	_run.call_deferred(states)


func _run(states: Array) -> void:
	var scale0 := Settings.text_scale
	for st in states:
		print("netrun_states: ", st)
		await _state(String(st))
	Settings.text_scale = scale0
	Settings.changed.emit()
	RunManager.delete_save()
	print("netrun_states: done")
	get_tree().quit()


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _open_netrun(corp: StringName, scale: float, heat: int = 0) -> Node:
	if _scene != null and is_instance_valid(_scene):
		_scene.queue_free()
		await _frames(2)
	Settings.text_scale = scale
	Settings.changed.emit()
	RunManager.reset()
	_unlock_all_corps()
	RunManager.new_campaign(1, corp)
	RunManager.campaign.heat = heat
	_scene = NETRUN.instantiate()
	add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(2)
	_scene.start_run(1)
	return _scene


## As the review pack: every corporation playable in this run's own profile.
func _unlock_all_corps() -> void:
	var p := RunManager.profile
	for u in [&"unlock_meridian", &"unlock_halcyon", &"unlock_orbital"]:
		if not p.unlocks.has(u):
			p.unlocks.append(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		p.best_ice_by_corp[id] = 10


func _settle(net: Node) -> void:
	for f in BAKE_FRAMES:
		var city: NeonCity = net.background.city
		var v := city.view3d
		var built := v == null or (v.model != null and v.chunks_built() >= v.model.keys().size())
		if net.arrival_ready() and city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0 and built:
			break
		await get_tree().process_frame
	await _frames(SETTLE)


## ART-7 7w: the 3D city's camera now (a CAM line), and with --perf a frame-time probe.
func _probe(net: Node, st: String) -> void:
	var v: CityView3D = net.background.city.view3d
	if v == null:
		print("CAM state=%s 2d" % st)
		return
	var m := v.get_node_or_null(^"CityMotion") as CityViewMotion
	var tier := m.layers.car_tier if m != null and m.layers != null else -1
	var cars := m.layers.sky_cars_visible() if m != null and m.layers != null else false
	print("CAM state=%s ortho=%.1f band=%d car_tier=%d sky_cars=%s size=%s" % [st, v.iso.ortho, v.band, tier, cars, str(v.size)])
	if _perf_s <= 0.0:
		return
	# As city_lab / city_perf_probe: vsync off while measuring (a vsynced GPU clocks down and
	# reports its idle-clock time, ~4x the real cost).
	var vs := DisplayServer.window_get_vsync_mode()
	var fps0 := Engine.max_fps
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	var vrid := v.get_viewport_rid()
	var root := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(vrid, true)
	RenderingServer.viewport_set_measure_render_time(root, true)
	await _frames(10)
	var t0 := Time.get_ticks_usec()
	var last := t0
	var n := 0
	var gpu := 0.0
	var cpu := 0.0
	var all_gpu := 0.0
	var worst := 0.0
	while Time.get_ticks_usec() - t0 < int(_perf_s * 1000000.0):
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		worst = maxf(worst, (now - last) / 1000.0)
		last = now
		n += 1
		gpu += RenderingServer.viewport_get_measured_render_time_gpu(vrid)
		cpu += RenderingServer.viewport_get_measured_render_time_cpu(vrid)
		all_gpu += RenderingServer.viewport_get_measured_render_time_gpu(root)
	print("PERF state=%s frames=%d frame_avg_ms=%.2f frame_max_ms=%.2f city_gpu_ms=%.2f city_cpu_ms=%.2f screen_gpu_ms=%.2f" % [
		st, n, (Time.get_ticks_usec() - t0) / 1000.0 / maxf(1.0, n), worst, gpu / maxf(1.0, n), cpu / maxf(1.0, n), all_gpu / maxf(1.0, n)])
	DisplayServer.window_set_vsync_mode(vs)
	Engine.max_fps = fps0


func _underway(net: Node) -> void:
	var s := RunManager.netrun
	var first: StringName = s.available_nodes()[0]
	s.run.current_node_id = first
	s.run.visited.append(first)
	net._show_map()


func _shot(name_: String) -> void:
	if _scene != null and is_instance_valid(_scene) and not name_.begins_with("jack"):
		await _probe(_scene, name_)
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(_out.path_join(name_ + ".png"))


func _state(st: String) -> void:
	match st:
		"start":
			var net := await _open_netrun(&"solace", 1.0)
			await _settle(net)
			await _shot(st)
		"underway", "show_all":
			var net := await _open_netrun(&"solace", 1.0)
			await _settle(net)
			_underway(net)
			# A second step: the walked path shows as a lime line.
			var s := RunManager.netrun
			var nxt: StringName = s.run.current_node()["next"][0]
			s.run.current_node_id = nxt
			s.run.visited.append(nxt)
			net._show_map()
			await _settle(net)
			if st == "show_all":
				(net.city_overlay as RouteOverlay).show_all = true
				await _frames(SETTLE)
			await _shot(st)
		"heat":
			var net := await _open_netrun(&"meridian", 1.0, 60)
			await _settle(net)
			_underway(net)
			await _settle(net)
			await _shot(st)
		"meridian_16":
			var net := await _open_netrun(&"meridian", 1.6)
			await _settle(net)
			_underway(net)
			await _settle(net)
			await _shot(st)
		"halcyon_20":
			var net := await _open_netrun(&"halcyon", 2.0)
			await _settle(net)
			await _shot(st)
		"orbital", "rebel_cell":
			var net := await _open_netrun(StringName(st), 1.0)
			await _settle(net)
			await _shot(st)
		"close":
			# ART-7 7w: the player's wheel zooms the route in about "you are here".
			var net := await _open_netrun(&"solace", 1.0)
			await _settle(net)
			_underway(net)
			await _settle(net)
			var ov: CityMapOverlay = net.city_overlay
			var at: Vector2 = ov.get_global_transform_with_canvas() * ov.here_point()
			for i in 30:
				var v: CityView3D = net.background.city.view3d
				if v == null or v.iso == null or v.iso.ortho <= CLOSE_ORTHO:
					break
				net.route_controls.zoom_at(net.get_global_transform_with_canvas().affine_inverse() * at, -1.0)
				await _frames(2)
			await _frames(SETTLE * 3)
			await _shot(st)
		"event":
			# The node's dressed room behind its event page.
			var net := await _open_netrun(&"meridian", 1.0)
			await _settle(net)
			_underway(net)
			DemoSetup.open_event(RunManager.netrun, &"ev_leash_on_the_floor")
			net._show_current()
			# ART-7 7w: its first frames, off the 3D route (its 2D city baked ahead behind it).
			await _frames(3)
			await _shot("event_first")
			await _settle(net)
			await _shot(st)
		"jack":
			await _jack()


## The jack-in from the HQ's City Grid onto the route, frames at JACK_TIMES.
func _jack() -> void:
	if _scene != null and is_instance_valid(_scene):
		_scene.queue_free()
		await _frames(2)
	Settings.text_scale = 1.0
	Settings.changed.emit()
	RunManager.reset()
	RunManager.scene_switching_enabled = true
	# The HQ as the current scene beside this walker (a scene change frees only the HQ).
	var hq := HQ.instantiate()
	get_tree().root.add_child(hq)
	get_tree().current_scene = hq
	await _frames(4)
	hq.new_campaign(1)
	await _frames(4)
	hq.show_grid()
	for f in BAKE_FRAMES:
		var city: NeonCity = hq.wireframe.city if not hq.background.visible else hq.background.city
		if city.showing_current_look() and city.camera_settled() and city.bake_fade >= 1.0:
			break
		await get_tree().process_frame
	await _frames(SETTLE)
	var site: StringName = RunManager.launchable_sites()[0].id
	hq.select_site(site)
	await _frames(SETTLE)
	var op := RunManager.campaign.living_operatives()[0]
	var t0 := Time.get_ticks_msec()
	hq.launch(site, op.id)
	for t in JACK_TIMES:
		while (Time.get_ticks_msec() - t0) / 1000.0 < t:
			await get_tree().process_frame
		await _shot("jack_%04d" % roundi(t * 1000.0))
