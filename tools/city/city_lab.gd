extends Control
## ART-5 5a: the city lab (windowed only, through tools/run_windowed.py). ONE launch walks a
## list of states (corporation x zoom) on the real CityView3D and writes a frame per state,
## or measures frame times. User args:
##   --shots=<dir>            a PNG per state (after --settle frames each), then quits
##   --states=a,b,...         states (default: every corp at grid, raid, netrun + city):
##                            <corp>:<grid|raid|netrun|close|city>
##   --perf=<seconds>         frame-time probe per state (PERF lines), then quits
##   --quality=0..2           Settings.city_quality for this run (-1 = default)
##   --size=WxH               window size; --settle=<frames>; --freeze=1 (stills)
##   --network=1              a sample network round each state's corp HQ (the decal)
## Prints CITYLAB lines; grep the log for ERROR.

const CONFIG := preload("res://content/config/city_config.tres")
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
## "gridpage": the Grid page's fitted frame (ortho ~220) holding the GRID band, as the game does.
const ZOOMS := {"grid": 440.0, "gridpage": 220.0, "raid": 300.0, "netrun": 160.0, "close": 70.0, "city": 1300.0}
const SETTLE_DEFAULT := 40

var cfg: CityConfig = CONFIG
var view: CityView3D
var _rect: TextureRect
var _args: Dictionary = {}
var _states: Array[String] = []
var _state: int = -1
var _frame: int = 0
var _perf: Dictionary = {}
var _t0: int = 0


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	if _args.has("quality"):
		Settings.city_quality = int(_args["quality"])
	if _args.has("size"):
		var wh := String(_args["size"]).split("x")
		DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	if _args.has("states"):
		for s in String(_args["states"]).split(","):
			_states.append(s)
	else:
		for c in CORPS:
			for z in ["grid", "raid", "netrun"]:
				_states.append("%s:%s" % [c, z])
		_states.append("halcyon:city")
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	view = CityView3D.new()
	view.size = DisplayServer.window_get_size()
	add_child(view)
	_rect = TextureRect.new()
	_rect.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_rect.texture = view.get_texture()
	_rect.stretch_mode = TextureRect.STRETCH_SCALE
	add_child(_rect)
	_t0 = Time.get_ticks_msec()
	view.model_ready.connect(_on_ready, CONNECT_ONE_SHOT)
	print("CITYLAB start states=%d quality=%s" % [_states.size(), str(view.quality)])


func _on_ready() -> void:
	print("CITYLAB model ready in %d ms: prisms=%d buildings=%d chunks=%d" % [Time.get_ticks_msec() - _t0,
		view.model.prisms.size(), view.model.buildings, view.chunks_built()])
	var bl := view.layer(&"buildings")
	if bl.get_child_count() > 0 and bl.get_child(0).get_child_count() > 0:
		var mi := bl.get_child(0).get_child(0) as MultiMeshInstance3D
		if mi != null:
			print("CITYLAB chunk0 fam0 instances=%d buffer=%d surfaces=%d aabb=%s visible=%s" % [mi.multimesh.instance_count,
				mi.multimesh.buffer.size(), mi.multimesh.mesh.get_surface_count(), str(mi.get_aabb()), str(mi.is_visible_in_tree())])
	_next_state()


func _next_state() -> void:
	_state += 1
	_frame = 0
	_perf = {}
	if _state >= _states.size():
		get_tree().quit()
		return
	var parts := _states[_state].split(":")
	var corp := StringName(parts[0])
	var zoom := String(parts[1]) if parts.size() > 1 else "grid"
	var at := NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS * 0.5, NeonCity.HQ_LOTS * 0.5) - CityLayout.RIGHT * 11.0
	if zoom == "city":
		at = Vector2(cfg.city_rect.get_center())
	var size := Vector2(DisplayServer.window_get_size())
	if Vector2i(size) != view.size:
		view.set_view_size(Vector2i(size))
	view.band_lock = CityLod.Band.GRID if zoom == "gridpage" else -1
	view.set_iso(CityIsoCamera.make(cfg, view.lot_world(at), float(ZOOMS.get(zoom, 440.0)), size))
	if _args.get("network", "1") == "1":
		view.set_network(_sample_network(corp))
	else:
		view.set_network(null)
	print("CITYLAB state %s band=%d lod=%d" % [_states[_state], view.band, view.building_lod])


## A sample network round `corp`'s Grid origin: the Sites' points laid out like CityLayout
## (a ring of nodes, links along the lot grid in L shapes).
func _sample_network(corp: StringName) -> CityNetworkData:
	var origin := NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS * 0.5, NeonCity.HQ_LOTS * 0.5) - CityLayout.RIGHT * 11.0 + CityLayout.DOWN * 2.5
	var nodes: Array[Dictionary] = []
	var lots := {}
	var cols: Array[Color] = [Palette.corp_color(corp), Palette.NET_CYAN, Palette.CELL_TURF, Palette.CELL_TURF, Palette.corp_color(corp),
		Palette.corp_color(corp), Palette.RESIST_GOLD, Palette.corp_color(corp)]
	for k in 8:
		var uv := Vector2(cos(TAU * k / 8.0), sin(TAU * k / 8.0))
		var p := origin + CityLayout.RIGHT * uv.x * 7.5 + CityLayout.DOWN * uv.y * 5.0
		var id := StringName("s%d" % k)
		lots[id] = Vector2i(roundi(p.x), roundi(p.y))
		nodes.append({"id": id, "color": cols[k], "tier": 1 + k % 3, "mark": CityMapOverlay.MARK_SPRAY if k in [2, 3] else "",
			"kind": CityMapOverlay.KIND_HOME if k == 2 else CityMapOverlay.KIND_TIER, "big": k == 2})
	var edges: Array[Dictionary] = []
	var routes: Array[PackedVector2Array] = []
	for k in 8:
		var a: Vector2i = lots[StringName("s%d" % k)]
		var b: Vector2i = lots[StringName("s%d" % ((k + 1) % 8))]
		var ours := k in [1, 2]
		edges.append({"a": StringName("s%d" % k), "b": StringName("s%d" % ((k + 1) % 8)), "color": Palette.CELL_TURF if ours else Palette.NET_CYAN,
			"width": 3.5 if ours else 2.0, "flow": ours, "dashed": k == 5})
		routes.append(PackedVector2Array([Vector2(a) + Vector2(0.5, 0.5), Vector2(b.x, a.y) + Vector2(0.5, 0.5), Vector2(b) + Vector2(0.5, 0.5)]))
	return CityNetworkData.from_graph(cfg, nodes, edges, func(id: StringName) -> Vector2i: return lots[id],
		func(k: int) -> PackedVector2Array: return routes[k])


func _process(_delta: float) -> void:
	if _state < 0 or _state >= _states.size():
		return
	_frame += 1
	var settle := int(_args.get("settle", str(SETTLE_DEFAULT)))
	if _args.has("perf"):
		_probe(settle)
		return
	if _frame == settle:
		if _args.has("shots"):
			var img := view.get_texture().get_image()
			var path := "%s/%02d_%s.png" % [String(_args["shots"]), _state, _states[_state].replace(":", "_")]
			img.save_png(path)
			print("CITYLAB shot %s %dx%d" % [path, img.get_width(), img.get_height()])
		_next_state()


func _probe(settle: int) -> void:
	var rid := get_viewport().get_viewport_rid()
	var vrid := view.get_viewport_rid()
	if _frame == 2:
		RenderingServer.viewport_set_measure_render_time(rid, true)
		RenderingServer.viewport_set_measure_render_time(vrid, true)
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
	if _frame <= settle:
		_perf = {"t0": Time.get_ticks_usec(), "n": 0, "gpu": 0.0, "cpu": 0.0, "max": 0.0, "last": Time.get_ticks_usec(),
			"draws": 0.0, "prims": 0.0}
		return
	var now := Time.get_ticks_usec()
	var dt := (now - int(_perf["last"])) / 1000.0
	_perf["last"] = now
	_perf["n"] = int(_perf["n"]) + 1
	_perf["max"] = maxf(float(_perf["max"]), dt)
	_perf["gpu"] = float(_perf["gpu"]) + RenderingServer.viewport_get_measured_render_time_gpu(vrid)
	_perf["cpu"] = float(_perf["cpu"]) + RenderingServer.viewport_get_measured_render_time_cpu(vrid)
	_perf["draws"] = float(_perf["draws"]) + Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	_perf["prims"] = float(_perf["prims"]) + Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)
	if now - int(_perf["t0"]) >= int(float(_args["perf"]) * 1000000.0):
		var n := float(_perf["n"])
		print("PERF state=%s tier=%d size=%s frames=%d frame_avg_ms=%.2f frame_max_ms=%.2f city_gpu_ms=%.2f city_cpu_ms=%.2f draws=%.0f prims=%.0f tex_mb=%.1f vmem_mb=%.1f" % [
			_states[_state], int(view.quality["tier"]), str(view.size), int(n), (now - int(_perf["t0"])) / 1000.0 / n,
			float(_perf["max"]), float(_perf["gpu"]) / n, float(_perf["cpu"]) / n, float(_perf["draws"]) / n,
			float(_perf["prims"]) / n, Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0,
			Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0])
		_next_state()
