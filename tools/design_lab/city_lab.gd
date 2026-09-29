extends Control
## City lab (art pass W7, ART_BIBLE §9): one city backdrop with its state set from the
## command line, captured to PNG once its bake has landed. Real display only, through
## tools/run_windowed.py (with a private APPDATA):
##
##   python tools/run_windowed.py --log out.log -- --resolution 1280x720 \
##       res://tools/design_lab/city_lab.tscn -- --out=C:/tmp/city.png [options]
##
## Options:
##   --net                  the net city (WireframeBackground) instead of the HQ window's
##   --corp=<id>            the district and target corp (default solace)
##   --context=<c>          title | hq | net | combat (default: the background's)
##   --heat=<n>             Heat (the band from the config)
##   --progress=<f>         campaign progress 0..1
##   --claims=<n>           claim n Sites round the corp's HQ (territory, with its influence)
##   --wash                 also show the spread's lasting wash (the old khaki with --legacy)
##   --map                  map mode, with a few mock map nodes drawn over the city
##   --nodes                the mock map nodes without map mode (the before of --map)
##   --calm                 a mock glass panel with text, marked as a calm zone
##   --reduce               reduce effects (this run only)
##   --reduce-motion        reduce motion (this run only)
##   --silhouette           never land a bake: the silhouette pre-render stays
##   --legacy               the pre-W7 look (CityAtmosphere.enabled off)
##   --dim=<f>              the city's own veil (NeonCity.dim)
##   --frames=<n> --interval=<s>   capture n frames `interval` seconds apart (out_0.png ...)
##   --settle=<s>           seconds to wait after the bake landed (default 1.0)

const LEGACY_SILHOUETTE := preload("res://tools/design_lab/legacy_silhouette.gd")

var _out: String = "user://city_lab.png"
var _frames: int = 1
var _interval: float = 0.5
var _settle: float = 1.0
var _bg: Control
var _city: NeonCity
var _map_nodes: Array[Vector2] = []
var _map_layer: Control


func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	var opt := {}
	for a in args:
		if a.begins_with("--"):
			var kv := a.trim_prefix("--").split("=", true, 1)
			opt[kv[0]] = kv[1] if kv.size() > 1 else "1"
	_out = String(opt.get("out", _out))
	_frames = int(opt.get("frames", "1"))
	_interval = float(opt.get("interval", "0.5"))
	_settle = float(opt.get("settle", "1.0"))
	if opt.has("reduce"):
		Settings.reduce_effects = true
		Settings.changed.emit()
	if opt.has("reduce-motion"):
		Settings.reduce_motion = true
		Settings.changed.emit()
	if opt.has("legacy"):
		CityAtmosphere.enabled = false
	if opt.has("silhouette"):
		CityBakeCache.simulate = true
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var corp := StringName(opt.get("corp", "solace"))
	if opt.has("net"):
		var wf := WireframeBackground.new()
		_bg = wf
		_city = wf.city
	else:
		var cb := CyberdeckBackground.new()
		_bg = cb
		_city = cb.city
	_city.follow_campaign = false
	add_child(_bg)
	_city.district = corp
	if opt.has("dim"):
		_city.dim = float(opt["dim"])
	if opt.has("silhouette") and opt.has("legacy"):
		# The pre-W7 placeholder (flat lifted blocks), for the before/after.
		_city._sil.draw.disconnect(_city._draw_sil)
		_city._sil.draw.connect(_draw_legacy_sil)
	var atm := _city.atmosphere()
	atm.follow_campaign(false)
	if opt.has("context"):
		atm.set_context(StringName(opt["context"]))
		if opt["context"] == "title":
			_city.pan = true
	atm.set_heat(int(opt.get("heat", "0")))
	atm.set_campaign_progress(float(opt.get("progress", "0")), corp)
	var hq := NeonCity.hq_of(corp) + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
	var spots: Array[Vector2] = [Vector2(-9, 3), Vector2(3, -10), Vector2(11, 6), Vector2(-4, 12), Vector2(-14, -7)]
	var claims := PackedVector2Array()
	for i in mini(int(opt.get("claims", "0")), spots.size()):
		claims.append(hq + spots[i])
	var sites := PackedVector2Array()
	for s in spots:
		sites.append(hq + s)
	if not claims.is_empty():
		var sources: Array[Dictionary] = []
		for i in claims.size():
			sources.append({"id": StringName("lab_%d" % i), "at": claims[i], "w": CityInfluence.WEIGHT_CLAIMED})
		_city.set_influence({"corp": corp, "sway": 0.0, "sources": sources, "sites": sites})
		atm.set_territory(claims)
		if opt.has("wash"):
			_city._spread_origins = claims
			_city._spread_color = Palette.CELL_TURF
			_city._show_tint(Motion.amplitude(&"influence_tint"))
	if opt.has("map") or opt.has("nodes"):
		atm.set_map_mode(opt.has("map"))
		_map_nodes = [hq] as Array[Vector2]
		for s in spots:
			_map_nodes.append(hq + s)
		_map_layer = Control.new()
		_map_layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		_map_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_map_layer.draw.connect(_draw_map)
		add_child(_map_layer)
	if opt.has("calm"):
		var panel := PanelContainer.new()
		panel.position = Vector2(64, 120)
		panel.custom_minimum_size = Vector2(420, 260)
		var label := Label.new()
		label.text = "SITE: CLINIC ANNEX\nOBJECTIVE: EXTRACT\nINTEGRITY 30 / 30\n\nA glass panel over the city:\nthe city behind it is calm."
		panel.add_child(label)
		add_child(panel)
		atm.set_calm_controls([panel] as Array[Control])
	_capture.call_deferred()


func _draw_legacy_sil() -> void:
	LEGACY_SILHOUETTE.draw(_city, _city._sil)
	_city.silhouette_done = true


func _draw_map() -> void:
	var font := Palette.mono()
	for i in _map_nodes.size():
		var g := _map_nodes[i]
		var p := _city.get_global_transform_with_canvas() * _city.grid_to_local(g.x + 0.5, g.y + 0.5)
		if i > 0:
			var q := _city.get_global_transform_with_canvas() * _city.grid_to_local(_map_nodes[0].x + 0.5, _map_nodes[0].y + 0.5)
			_map_layer.draw_line(p, q, Palette.NET_CYAN, 3.0)
	for i in _map_nodes.size():
		var g := _map_nodes[i]
		var p := _city.get_global_transform_with_canvas() * _city.grid_to_local(g.x + 0.5, g.y + 0.5)
		_map_layer.draw_circle(p, 16.0, Palette.TERMINAL_BG)
		_map_layer.draw_arc(p, 16.0, 0.0, TAU, 32, Palette.CELL_ACID if i == 0 else Palette.NET_CYAN, 3.0)
		_map_layer.draw_string(font, p + Vector2(22, 6), "SITE %d" % i, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.CAPTION), Palette.TEXT_HI)


func _capture() -> void:
	# Wait for the city's own bake (or, with --silhouette, for the silhouette to finish).
	var waited := 0.0
	while waited < 60.0:
		await get_tree().process_frame
		waited += get_process_delta_time()
		if CityBakeCache.simulate:
			if _city.silhouette_done and waited > 1.0:
				break
		elif _city.view_covered() and _city.bake_fade >= 1.0 and CityBakeCache.busy() == 0:
			break
	await get_tree().create_timer(_settle).timeout
	if _map_layer != null:
		_map_layer.queue_redraw()
	var vm := _city._view.material as ShaderMaterial
	print("city_lab: state %s band %s | lights: search %s rim %s (flicker from %s) leaks %s calm %s | map_dim %s" % [
		_city.atmosphere().state.context, _city.atmosphere().state.band_name(), vm.get_shader_parameter("search_count"),
		vm.get_shader_parameter("rim_count"), vm.get_shader_parameter("flicker_from"), vm.get_shader_parameter("leak_count"),
		vm.get_shader_parameter("calm_count"), vm.get_shader_parameter("g_map_dim")])
	print("city_lab: search ", vm.get_shader_parameter("search"))
	for f in _frames:
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		var path := _out if _frames == 1 else _out.get_basename() + "_%d.png" % f
		img.save_png(path)
		print("city_lab: saved ", path)
		if f < _frames - 1:
			await get_tree().create_timer(_interval).timeout
	get_tree().quit()
