extends Node
## HQ netrun set piece capture (art/hq-netrun): the live r43 city (seed 7) with the Solace HQ set piece (CityHqNet) staged in it, seen by the netrun camera.
## Windowed only: bash tools/look_parity/hq_net.sh <out dir> <log name> [--poses=hero,alt_dusk,...] [--hq] [--probe] [--perf --frames=N] [--fly=N] [--set=key=value ...]
## Poses are defined in CityHqNet.pose(); --hq switches the set piece on (CityConfig.hq_on), --nozr leaves the zoom-rule look off.

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1920, 1080)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 30
const START_HEAT := 80
const SEED := 7
const PERF_WARMUP := 60

var _out := ""
var _name := "hq"
var _poses: Array[String] = ["hero"]
var _hq_on := false
var _zr := true
var _probe := false
var _perf := false
var _frames := 500
var _fly := 0
var _settle_n := 60
var _freeze := true
var _hide: Array[String] = []
var _tree := false
var _px: Array[Vector2] = []
var _hq: Control = null


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--name="):
			_name = a.trim_prefix("--name=")
		elif a.begins_with("--poses="):
			_poses.clear()
			for s in a.trim_prefix("--poses=").split(","):
				_poses.append(s)
		elif a == "--hq":
			_hq_on = true
		elif a == "--nozr":
			_zr = false
		elif a == "--probe":
			_probe = true
		elif a == "--perf":
			_perf = true
		elif a.begins_with("--px="):
			var pp := a.trim_prefix("--px=").split(",")
			_px.append(Vector2(float(pp[0]), float(pp[1])))
		elif a == "--tree":
			_tree = true
		elif a == "--live":
			_freeze = false
		elif a.begins_with("--frames="):
			_frames = int(a.trim_prefix("--frames="))
		elif a.begins_with("--fly="):
			_fly = int(a.trim_prefix("--fly="))
		elif a.begins_with("--settle="):
			_settle_n = int(a.trim_prefix("--settle="))
		elif a.begins_with("--hide="):
			for hn in a.trim_prefix("--hide=").split(","):
				_hide.append(hn)
		elif a.begins_with("--set="):
			var kvs := a.trim_prefix("--set=").split("=")
			var v: Variant = kvs[1]
			if kvs[1] == "true" or kvs[1] == "false":
				v = kvs[1] == "true"
			elif kvs[1].begins_with("("):
				v = str_to_var("Vector3" + kvs[1]) if kvs[1].count(",") == 2 else str_to_var("Vector2" + kvs[1])
			else:
				v = float(kvs[1])
			(load("res://content/config/city_config.tres") as Resource).set(kvs[0], v)
	if _hq_on:
		(load("res://content/config/city_config.tres") as Resource).set("hq_on", true)
	DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://hq_net_settings.json"
	Settings.reduce_effects = false
	Settings.reduce_motion = _freeze
	SaveService.save_dir = "user://saves/hq_net"
	RunManager.save_slot = "gut_hq_net"
	RunManager.scene_switching_enabled = false
	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	await _run()
	print("HQNET DONE")
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
	_hq = HQ.instantiate()
	get_tree().root.add_child(_hq)
	_hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	_hq.new_campaign(SEED)
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
	if _freeze:
		v.set_zoom_freeze(true)
		v.post_material().set_shader_parameter("time_scale", 0.0)
	var net := v.layer(&"network")
	if net != null:
		net.visible = false
	await _settle(10)
	if _probe:
		_do_probe(v)
		_hq.queue_free()
		return
	v.set_zoom_rules(_zr)
	if _hq_on and v.has_method(&"set_hq_netrun"):
		v.call(&"set_hq_netrun", true)
	await _settle(30)
	for hn in _hide:
		for nd in v.find_children(hn, "Node3D", true, false):
			(nd as Node3D).visible = false
	if _tree:
		_print_tree(v, 0)
	if _perf:
		await _run_perf(v)
	elif _fly > 0:
		await _run_fly(v)
	else:
		for p in _poses:
			v.set_iso(CityHqNet.pose(v, p))
			await _settle(_settle_n)
			_report(v, p)
			for q in _px:
				var g := v.unproject(q, v.hq_net._o.y if v.hq_net != null else 0.0)
				var fr := CityHqNet.frame_of(v)
				var dd: Vector3 = g - (fr["o"] as Vector3)
				print("HQNET px %s -> u=%.1f v=%.1f" % [str(q), dd.dot(fr["a"] as Vector3), dd.dot(fr["s"] as Vector3)])
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(_out.path_join("%s_%s.png" % [_name, p]))
			await _settle(2)
	_hq.queue_free()


func _report(v: CityView3D, p: String) -> void:
	var i := v.iso
	print("HQNET post g1_black=%s zr_on=%s zr_far=%s" % [str(v.post_material().get_shader_parameter(&"g1_black")), str(v.post_material().get_shader_parameter(&"zr_on")), str(v.building_material().get_shader_parameter(&"zr_far"))])
	print("HQNET pose=%s eye=%s yaw=%.1f pitch=%.1f fov=%.1f ppb=%.1f band=%d" % [p, str(i.eye()), i.yaw_deg, i.pitch_deg, i.fov_deg, CityZoomLayers.focus_ppb(i), v.zoom_street.band if v.zoom_street != null else -1])


func _run_fly(v: CityView3D) -> void:
	await _settle(30)
	for f in _fly:
		var t := float(f) / float(maxi(_fly - 1, 1))
		v.set_iso(CityHqNet.fly_pose(v, t))
		await _settle(6)
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png(_out.path_join("%s_fly_%02d.png" % [_name, f]))
		print("HQNET fly %d t=%.3f ppb=%.1f" % [f, t, CityZoomLayers.focus_ppb(v.iso)])


func _run_perf(v: CityView3D) -> void:
	var rids: Array[RID] = [v.get_viewport_rid(), get_tree().root.get_viewport_rid()]
	for r in rids:
		RenderingServer.viewport_set_measure_render_time(r, true)
	for p in _poses:
		v.set_iso(CityHqNet.pose(v, p))
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
		print("PERF pose=%s frames=%d wall %s" % [p, times.size(), _stats(times)])
		print("PERF pose=%s gpu_city %s" % [p, _stats(gpu_city)])
		print("PERF pose=%s gpu_window %s" % [p, _stats(gpu_all)])


func _stats(a: Array[float]) -> String:
	var t := a.duplicate()
	t.sort_custom(func(x: float, y: float) -> bool: return x < y)  # frame times, ascending (not ids)
	var n := t.size()
	var sum := 0.0
	for x in t:
		sum += x
	return "mean_ms=%.2f p50_ms=%.2f p95_ms=%.2f p99_ms=%.2f max_ms=%.2f" % [sum / float(maxi(n, 1)), t[n / 2], t[mini(n - 1, int(float(n) * 0.95))], t[mini(n - 1, int(float(n) * 0.99))], t[n - 1]]


## --probe: where the Solace HQ stands and what the prisms look like along the four axes.
func _do_probe(v: CityView3D) -> void:
	var r: Rect2i = v.model.hqs.get(&"solace", Rect2i())
	var m := HqCompoundStage.manifest(&"solace")
	var at := HqCompoundStage.place(v.cfg, &"solace", m, r)
	print("HQNET probe hq_rect=%s at=%s ground=%.2f lot_bu=%.2f city_rect=%s" % [str(r), str(at.origin), v.model.ground_at(CityIsoCamera.world_to_lot(v.cfg, at.origin)), v.cfg.lot_bu, str(v.cfg.city_rect)])
	for dn in ["E", "W", "N", "S"]:
		var d := Vector2(1, 0) if dn == "E" else (Vector2(-1, 0) if dn == "W" else (Vector2(0, -1) if dn == "N" else Vector2(0, 1)))
		var line := ""
		for k in range(0, 40):
			var w := at.origin + Vector3(d.x, 0, d.y) * float(k) * 8.0
			var tall := 0.0
			for pr: Dictionary in v.model.prisms:
				var c: Vector2 = pr["centre"]
				if absf(c.x - w.x) < 5.0 and absf(c.y - w.z) < 5.0:
					tall = maxf(tall, float(pr["h"]))
			line += "%d " % int(tall)
		print("HQNET probe ray %s heights every 8 BU: %s" % [dn, line])


func _print_tree(n: Node, depth: int) -> void:
	if depth > 3:
		return
	var extra := ""
	if n is MeshInstance3D:
		extra = " aabb=%s" % str((n as MeshInstance3D).get_aabb().size)
	elif n is MultiMeshInstance3D:
		extra = " mm=%d" % (n as MultiMeshInstance3D).multimesh.instance_count
	print("TREE %s%s (%s)%s" % ["  ".repeat(depth), n.name, n.get_class(), extra])
	for c in n.get_children():
		_print_tree(c, depth + 1)
