extends Control
## ART-1 1D spike (b): the district as Blender-baked layers with 2D motion on top. The
## finished bake of a view (blender/bake_district.py + post_bake.py, one image per view and
## zoom) fills the screen; the sky-lane traffic (CityTraffic, the same lanes and seeded
## cars as the 3D path) is projected with CityIsoCamera and drawn in 2D by car tier.
## Windowed only. User args: --view=grid|raid|netrun|close --bake=<dir with <view>_final.png>
##   --shot=<png> [--settle=N] [--freeze=1] | --perf=<seconds>

const CONFIG := preload("res://tools/spike/city/city_spike_config.tres")
const SETTLE_DEFAULT := 30

var cfg: CitySpikeConfig = CONFIG
var traffic: CityTraffic
var iso: CityIsoCamera
var view_name: String = "grid"
var _tex: ImageTexture
var _args: Dictionary = {}
var _frame: int = 0
var _time: float = 0.0
var _tier: int = -1
var _perf: Dictionary = {}


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	view_name = String(_args.get("view", "grid"))
	set_anchors_preset(Control.PRESET_FULL_RECT)
	var img := Image.load_from_file(String(_args.get("bake", "")).path_join(view_name + "_final.png"))
	_tex = ImageTexture.create_from_image(img)
	var district := CityDistrict.from_layout(cfg)
	traffic = CityTraffic.build(cfg, district, cfg.city_seed)
	iso = CityIsoCamera.for_view(cfg, view_name, Vector2(img.get_width(), img.get_height()))
	_tier = CityLod.car_tier(cfg, iso.ortho)
	print("SPIKEBAKED view=%s image=%dx%d cars=%d tier=%d" % [view_name, img.get_width(), img.get_height(), traffic.cars.size(), _tier])


func _process(delta: float) -> void:
	_frame += 1
	if _args.has("size") and _frame <= 3:
		var wh := String(_args["size"]).split("x")
		var want := Vector2i(int(wh[0]), int(wh[1]))
		if DisplayServer.window_get_size() != want:
			DisplayServer.window_set_size(want)
	if not _args.has("freeze"):
		_time += delta
	queue_redraw()
	var settle := int(_args.get("settle", str(SETTLE_DEFAULT)))
	if _args.has("shot") and _frame == settle:
		var img := get_viewport().get_texture().get_image()
		img.save_png(String(_args["shot"]))
		print("SPIKEBAKED shot %s %dx%d" % [_args["shot"], img.get_width(), img.get_height()])
		get_tree().quit()
	if _args.has("perf"):
		_probe(settle)


func _draw() -> void:
	draw_texture_rect(_tex, Rect2(Vector2.ZERO, size), false)
	var k := size.x / iso.viewport.x
	var city := CityLod.city_share(cfg, CityIsoCamera.lod_of(cfg, iso.ortho))
	var gain := lerpf(cfg.sky_lane_management, 1.0, city)
	var streak := (cfg.car_length.x + cfg.car_length.y) * 0.5
	for c in traffic.cars.size():
		var car: Dictionary = traffic.cars[c]
		var ln: Dictionary = traffic.lanes[car["lane"]]
		var p := traffic.position_at(c, _time)
		var dir := ((ln["b"] as Vector3) - (ln["a"] as Vector3)).normalized() * float(car["dir"])
		var head := iso.project(p) * k
		var tail := iso.project(p - dir * streak) * k
		if not Rect2(Vector2.ZERO, size).grow(40).has_point(head):
			continue
		var col: Color = car["color"]
		var lc := Color(col.r * gain, col.g * gain, col.b * gain)
		match _tier:
			CityLod.CarTier.FAR:
				draw_line(tail, head, lc, 1.5)
				draw_circle(head, 1.6, Color(1, 0.97, 0.9))
			CityLod.CarTier.MEDIUM:
				draw_line(tail, head, lc, 1.2)
				var s := 1.2 / iso.bu_per_px() * k
				draw_rect(Rect2(head - Vector2(s, s * 0.6), Vector2(s * 2.0, s * 1.2)), Color(lc, cfg.car_box_alpha))
			_:
				draw_line(tail, head, lc, maxf(2.0, 0.6 / iso.bu_per_px() * k))
				var s := 1.5 / iso.bu_per_px() * k
				draw_rect(Rect2(head - Vector2(s, s * 0.5), Vector2(s * 2.0, s)), Color(0.12, 0.1, 0.16))
				draw_circle(head + (head - tail).normalized() * s, s * 0.25, Color(1, 0.97, 0.9))


func _probe(settle: int) -> void:
	var rid := get_viewport().get_viewport_rid()
	if _frame == 2:
		RenderingServer.viewport_set_measure_render_time(rid, true)
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		Engine.max_fps = 0
	if _frame <= settle:
		_perf = {"t0": Time.get_ticks_usec(), "n": 0, "cpu": 0.0, "gpu": 0.0, "last": Time.get_ticks_usec(), "max": 0.0}
		return
	var now := Time.get_ticks_usec()
	_perf["max"] = maxf(float(_perf["max"]), (now - int(_perf["last"])) / 1000.0)
	_perf["last"] = now
	_perf["n"] = int(_perf["n"]) + 1
	_perf["cpu"] = float(_perf["cpu"]) + RenderingServer.viewport_get_measured_render_time_cpu(rid) + RenderingServer.get_frame_setup_time_cpu()
	_perf["gpu"] = float(_perf["gpu"]) + RenderingServer.viewport_get_measured_render_time_gpu(rid)
	if now - int(_perf["t0"]) >= int(float(_args["perf"]) * 1000000.0):
		var n := float(_perf["n"])
		print("PERF baked view=%s frames=%d frame_avg_ms=%.2f frame_max_ms=%.2f cpu_ms=%.2f gpu_ms=%.2f draws=%.0f tex_mb=%.1f" % [
			view_name, int(n), (now - int(_perf["t0"])) / 1000.0 / n, float(_perf["max"]), float(_perf["cpu"]) / n,
			float(_perf["gpu"]) / n, Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
			Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0])
		get_tree().quit()
