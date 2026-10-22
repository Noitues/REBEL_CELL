extends Control
## NA-23 lab (windowed only, through tools/run_windowed.py): the street netrun view on the game's city for a started run.
## User args:
##   --seed=<n>           campaign seed (default 1)
##   --shots=<dir>        output folder (one sub-folder per shot: beauty.png, id.png, ui.png, capture.json)
##   --states=a,b,c       OVERVIEW / DECISION / HOVER shots: overview, decision, hover (default all three)
##   --walk=none|first|mid|last   the run's position: none (at the street), or a fixture walk of the graph (default none)
##   --hover=<n>          the option (0-based) the pointer is on in the hover shot (default 0)
##   --size=WxH           window size (default 1920x1080)
##   --settle=<frames>    frames to wait after a state change (default 90)
##   --perf=<frames>      after the shots, time this many frames of the overview and print the GPU / CPU frame ms
##   --fog=0|1            fog volume on (default 1)
##   --export=<dir>       writes city.json, net.json, run_graph.json and derive_street.json of the street (STREET-CAM, plate inputs)
##                        and prints the street's frontage tops (NA23 frontage: count, median, min, max BU)
##   --export_only=1      quit after the export (CITY-A2 step 2: runs headless too)
##   --plate_dir=<dir>    parity harness (tools/netrun_art/parity_sheet.py): the camera of the overview / decision shot is replaced
##                        by the plate's pose in <dir>/street_<state>_capture.json: our focus and yaw (street frame) with the plate's
##                        pitch, dist, lens and shift; --plate_abs=1 uses the plate's world pose as is (Blender world, not this city)
##   --reduce-effects=1   LOOK-TOOLBOX: frozen shader time and the static look (refactor proofs: two captures of the
##                        same code match to the pixel); the lab's own settings file, so the player's is untouched
##   --dump-materials=<file>  LOOK-TOOLBOX: append every set shader parameter vs its text default at each shot
##                        (RcLookMaterialAudit)
##   --bloom=<front>      LOOK Solace THE BLOOM (A Necrosis): the Bloom look at a front of <front> route layers (fractional; the concept's
##                        CREEPING / CLOSE / CATCHING are -0.5 / 0.75 / 1.4 with the operative on layer 2, gaps 2.5 / 1.25 / 0.6);
##                        --bloom-op=<layer> (default 2) the operative's layer (the band is the gap's), --bloom-strength=<0..1> (default 1)
## Prints NA23 lines.

const SETTLE_DEFAULT := 90

var view: StreetRouteView
var _args: Dictionary = {}
var _states: PackedStringArray = []
var _i := -1
var _frame := 0
var _phase := ""
var _data: StreetRouteData
var _walk := {"current": "", "visited": [], "options": []}


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	# --cfg.<field>.<key>[.<key>...]=<json>: a tuning override of the shipped shader config (CityShaderConfigData field) for this run only.
	for k: String in _args:
		if k.begins_with("cfg."):
			var parts := k.split(".")
			var node: Variant = CityShaderConfigData.shipped().get(parts[1])
			for i in range(2, parts.size() - 1):
				node = (node as Dictionary)[parts[i]]
			(node as Dictionary)[parts[parts.size() - 1]] = JSON.parse_string(String(_args[k]))
		elif k.begins_with("street."):
			var parts := k.split(".")
			var node: Variant = StreetRouteConfigData.shipped().get(parts[1])
			for i in range(2, parts.size() - 1):
				node = (node as Dictionary)[parts[i]]
			(node as Dictionary)[parts[parts.size() - 1]] = JSON.parse_string(String(_args[k]))
	if _args.has("reduce-effects"):
		Settings.path = "user://na23_lab_settings.json"
		Settings.reduce_effects = _args["reduce-effects"] == "1"
		RenderingServer.global_shader_parameter_set(Fx.REDUCE_GLOBAL, 1.0 if Settings.reduce_effects else 0.0)
	var wh := String(_args.get("size", "1920x1080")).split("x")
	DisplayServer.window_set_size(Vector2i(int(wh[0]), int(wh[1])))
	get_window().size = Vector2i(int(wh[0]), int(wh[1]))
	_states = String(_args.get("states", "overview,decision,hover")).split(",")
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.save_slot = "lab_na23"
	RunManager.new_campaign(int(_args.get("seed", "1")))
	var s := RunManager.start_run()
	if s == null:
		print("NA23 FAIL no run")
		get_tree().quit(1)
		return
	var t0 := Time.get_ticks_msec()
	_data = StreetRouteView.build_data(s, RunManager.corporation)
	print("NA23 data %d ms error='%s'" % [Time.get_ticks_msec() - t0, _data.error])
	if _data.error != "":
		get_tree().quit(1)
		return
	if _args.has("export"):
		_export_contract(String(_args["export"]))
		if String(_args.get("export_only", "0")) == "1":
			get_tree().quit()
			return
	var walks := NetrunPoseBuilder.fixture_walks(_data.run_graph)
	var w := String(_args.get("walk", "none"))
	if w != "none" and walks.has(w) and not (walks[w] as Array).is_empty():
		var path: Array = walks[w]
		_walk = {"current": String(path[-1]), "visited": path.slice(0, path.size() - 1), "options": NetrunPoseBuilder.successors(_data.run_graph, String(path[-1]))}
	else:
		_walk = {"current": "", "visited": [], "options": NetrunPoseBuilder.successors(_data.run_graph, "")}
	var cfg := CityView3D.CONFIG
	view = StreetRouteView.new()
	view.size = Vector2(int(wh[0]), int(wh[1]))
	add_child(view)
	view.setup(_data, CityModel.shared(cfg, CityPlan.current_seed()), String(_walk["current"]), _walk["visited"], _walk["options"])
	if String(_args.get("fog", "1")) == "0":
		for n in view.rig._extras:
			n.visible = false
	if String(_args.get("noroom", "0")) == "1":
		for id: String in view.rig._rooms:
			(view.rig._rooms[id] as MeshInstance3D).visible = false
	for k: String in ["haze_k", "wash_gain", "win_emit", "win_share", "facade_light", "plinth_off", "sec_side", "edge_gain", "band_emit", "ledge_bu"]:
		if _args.has(k):
			view.rig.view.building_material().set_shader_parameter(StringName(k), float(_args[k]))
	for k: String in ["rain_alpha", "ink_alpha", "ink_wobble_px", "ink_fade"]:
		if _args.has(k):
			view.rig.view._post.set_shader_parameter(StringName(k), float(_args[k]))
	if _args.has("wpx"):
		var wp := float(_args["wpx"])
		view.rig.view.building_material().set_shader_parameter(&"window_pitch", Vector2(wp, 1.9))
		view.rig.view.building_material().set_shader_parameter(&"window_size", Vector2(wp * 0.5, 0.7))
	if _args.has("exposure"):
		view.rig.exposure_override = float(_args["exposure"])
		view.rig.view.set_aaa_exposure(float(_args["exposure"]))
	view.ready_to_show.connect(_on_ready, CONNECT_ONE_SHOT)
	if _args.has("bloom"):
		_apply_bloom()


## LOOK Solace THE BLOOM: the look at --bloom's front on the street's layout, through the same mapper the game's call uses.
func _apply_bloom() -> void:
	var cc := load("res://content/config/campaign_config.tres") as CampaignConfigData
	var front := float(_args["bloom"])
	var gap_milli := roundi((float(_args.get("bloom-op", "2")) - front) * 1000.0)
	var band := int(BloomRules.band_for_gap(gap_milli, cc))
	var look := BloomLook.at_front(front, band, BloomLook.street_layout(_data.derive), &"", float(_args.get("bloom-strength", "1")))
	view.rig.view.set_bloom(look)
	print("NA23 bloom front=%.3f band=%s frame x=%.2f boxes=%d" % [front, BloomLook.BAND_NAMES[band], float(look["front"]), int(look["uniforms"].get(&"bl_box_n", 0))])


## STREET-CAM: writes the street derive's inputs and output as contract text into `dir` (city.json, net.json, run_graph.json,
## derive_street.json), the files art-pass re-renders the plates from.
func _export_contract(dir: String) -> void:
	DirAccess.make_dir_recursive_absolute(dir)
	var files := {"city.json": _data.city, "net.json": _data.net, "run_graph.json": _data.run_graph, "derive_street.json": _data.derive}
	for fn: String in files:
		var f := FileAccess.open("%s/%s" % [dir, fn], FileAccess.WRITE)
		f.store_string(NetrunArtExport.canonical(files[fn]))
		f.close()
	print("NA23 exported ", dir)
	# CITY-A2 step 2 (A-039): the netrun street's frontage tops on both sides (r2 layout_pass: median about 24 BU).
	var bases := NetrunArtLayout.merged_buildings(_data.city)
	var tops: Array = []
	for side: int in [1, -1]:
		for b: Dictionary in NetrunStreetDeriver.frontage(bases, _data.derive["street"]["a"], _data.derive["street"]["c"], side):
			tops.append(float(b["h"]))
	tops.sort()
	if not tops.is_empty():
		print("NA23 frontage n=%d median=%.1f min=%.1f max=%.1f" % [tops.size(), tops[tops.size() / 2], tops[0], tops[-1]])


func _on_ready() -> void:
	print("NA23 city ready")
	var rig := view.rig
	var bm := rig.view.building_material()
	var nroute := 0
	var rb: Array = _data.route_bids()
	print("NA23 geom of first ", rig._prism_geom.get(rb[0], []), " bid_prisms ", _data.bid_prisms.get(rb[0]))
	print("NA23 type ", typeof(rb[0]), " has ", _data.bid_prisms.has(rb[0]), " has str ", _data.bid_prisms.has("-59:21"), " geomhas ", rig._prism_geom.has(rb[0]), " ", rig._prism_geom.has("-59:21"), " ", _data.bid_prisms.keys().filter(func(k): return String(k).begins_with("-59")))
	print("NA23 bid_prisms ", _data.bid_prisms.size(), " route bids ", _data.route_bids(), " geom ", rig._prism_geom.size(), " sample ", _data.bid_prisms.keys().slice(0, 5))
	for bid: String in _data.route_bids():
		for g: Array in rig._prism_geom.get(bid, []):
			nroute += 1
			print("NA23 route prism ", bid, " ", g, " w=", rig.view.prism_w(int(g[0])), " unpack=", NetrunInstancePack.unpack(rig.view.prism_w(int(g[0]))))
	print("NA23 room_n=", bm.get_shader_parameter(&"room_n"), " route prisms ", nroute, " rooms ", rig.room_ids().size(), " view size ", rig.view.size, " rig size ", rig.size, " window ", get_window().size)
	print("NA23 room box0 ", (bm.get_shader_parameter(&"room_box") as PackedVector4Array)[0], " z0 ", (bm.get_shader_parameter(&"room_z") as PackedVector2Array)[0])
	_next()


func _next() -> void:
	_i += 1
	_frame = 0
	if _i >= _states.size():
		_phase = "perf" if _args.has("perf") else ""
		if _phase == "":
			get_tree().quit()
		return
	var st := _states[_i]
	match st:
		"overview":
			view.hover_id = ""
			view.selected_id = ""
			view.set_base_view(StreetRouteRules.View.OVERVIEW)
		"decision":
			view.hover_id = ""
			view.selected_id = ""
			view.set_base_view(StreetRouteRules.View.DECISION)
		"hover":
			view.set_base_view(StreetRouteRules.View.DECISION)
			var opts: Array = _walk["options"]
			view._set_hover(String(opts[clampi(int(_args.get("hover", "0")), 0, opts.size() - 1)]))
	if _args.has("plate_dir") and st != "hover":
		var pj := FileAccess.get_file_as_string("%s/street_%s_capture.json" % [String(_args["plate_dir"]), st])
		var cam: Variant = (JSON.parse_string(pj) as Dictionary).get("camera", null) if pj != "" else null
		if cam is Dictionary:
			var pp := NetrunPose.from_json(cam)
			if String(_args.get("plate_abs", "0")) != "1":
				# The plate's world is Blender's own street (art seed 1), not this city: keep OUR focus and yaw (the street frame)
				# and take the plate's pitch, distance, lens and shift.
				var ours := view.rig.pose
				pp = NetrunPose.make(ours.F, ours.yaw, pp.pitch, pp.dist * float(_args.get("dist-k", "1")), pp.lens, pp.sx, pp.sy)
			view.rig.set_pose(pp)
	_phase = "settle"


func _process(_delta: float) -> void:
	if _phase == "settle":
		_frame += 1
		if _frame == int(_args.get("settle", str(SETTLE_DEFAULT))):
			_shoot()
	elif _phase == "perf":
		_frame += 1
		if _frame == 1:
			view.set_base_view(StreetRouteRules.View.DECISION if String(_args.get("perfstate", "overview")) == "decision" else StreetRouteRules.View.OVERVIEW)
			RenderingServer.viewport_set_measure_render_time(view.rig.view.get_viewport_rid(), true)
			_perf_cpu = []
			_perf_gpu = []
		elif _frame > 30:
			var rid := view.rig.view.get_viewport_rid()
			_perf_cpu.append(RenderingServer.viewport_get_measured_render_time_cpu(rid))
			_perf_gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
			if _frame >= 30 + int(_args.get("perf", "120")):
				_perf_report()
				get_tree().quit()


var _perf_cpu: Array = []
var _perf_gpu: Array = []


func _perf_report() -> void:
	var g := _perf_gpu.duplicate()
	IdSort.sort_ids(g)
	var c := _perf_cpu.duplicate()
	IdSort.sort_ids(c)
	var sum_g := 0.0
	for v in g:
		sum_g += float(v)
	print("NA23 perf city viewport gpu ms: mean %.2f median %.2f p95 %.2f max %.2f | cpu ms median %.2f" % [sum_g / g.size(), g[g.size() / 2], g[int(g.size() * 0.95)], g[-1], c[c.size() / 2]])
	print("NA23 perf frame fps %.1f" % Engine.get_frames_per_second())


func _shoot() -> void:
	var name := "%s_seed%s" % [_states[_i], String(_args.get("seed", "1"))]
	var dir := "%s/%s" % [String(_args.get("shots", "user://na23")), name]
	DirAccess.make_dir_recursive_absolute(dir)
	var rig := view.rig
	get_viewport().get_texture().get_image().save_png("%s/ui.png" % dir)
	if _args.has("dump-materials"):
		RcLookMaterialAudit.dump(get_tree().root, String(_args["dump-materials"]))
	# NA-ID: beauty.png, id.png, depth.png and capture.json come from the general id capture (the same contract as HQ / city frames).
	var meta := {"kind": "street", "view": "hover" if _states[_i] == "hover" else _states[_i], "look": "aaa2", "look_blend": 1.0, "corp": "",
		"run": String(_data.derive["run"]), "camera": rig.pose.to_json(), "exempt": {"hover_cut": _states[_i] == "hover", "red_seq": false, "flash": false}}
	var res: Dictionary = await IdCapture.new(get_tree(), rig.view, rig).write(dir, meta)
	var beauty: Image = res["beauty"]
	print("NA23 id classes ", res["counts"])
	var cam := rig.view.camera
	print("NA23 cam proj=", cam.projection, " size=", cam.size, " off=", cam.frustum_offset, " near=", cam.near, " pos=", cam.global_position, " keep=", cam.keep_aspect, " pose loc=", rig.pose.loc(), " lens=", rig.pose.lens, " expect size=", NetrunFrustum.frustum_size(rig.pose, 0.5))
	var rid0: String = rig.room_ids()[0]
	var fr: Array = _data.rooms()[rid0]["front"]
	for q: Array in fr:
		var w3 := NetrunFrustum.to_world([q[0], q[1], q[2]])
		print("NA23 corner ", q, " unproject ", cam.unproject_position(w3), " pose.proj ", rig.pose.proj(q), " vp ", rig.view.size, " vpsize ", rig.view.get_visible_rect())
	print("NA23 shot %s %dx%d share=%.2f arrow=%s" % [dir, beauty.get_width(), beauty.get_height(), view.overlay.last_share(), str(view.overlay.arrow_showing())])
	_phase = ""
	await get_tree().process_frame
	_next()
