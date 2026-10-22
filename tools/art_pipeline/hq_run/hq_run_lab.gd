extends Control
## ART-8 8w review lab (windowed only; headless has no renderer): walks a list of states in ONE
## launch and writes a frame per state, with the city's GPU time:
##   run_<corp>       the HQ run's page (HqRunView) on the corp's compound (today's breach run)
##   full_<corp>      the same page with a full run map (GDD 4.2) half walked (layout review)
##   gate_<corp>      the Central Server's gate over the page (all three Exploits)
##   pov_<corp> / pod_<corp>   LOOK Solace HQ: the compound alone (no page chrome) at the golden plate's overview / decision camera,
##                    read from `--plates=<dir holding hq_<corp>_overview_capture.json / _decision_>`
##   hq_<corp> / site_<corp> / won_<corp>   the combat backdrop's city close-up (D17): the boss
##                    fight's HQ, a regular fight's Site, the Site fight won
##   python tools/run_windowed.py --log <f> -- --resolution 1920x1080
##     res://tools/art_pipeline/hq_run/hq_run_lab.tscn -- --out=<dir> --states=run_meridian,gate_solace
##     [--tier=1] [--settle=30] [--perf=60] [--raw=160x90 (S-ARENA: also <state>_raw.png, the
##     backdrop city's own render before its grade, at that size)] [--scale=2.0 (S-HQRUN: the
##     text size)] [--reduce-effects=1 (LOOK-TOOLBOX: frozen shader time and the static look, so two
##     captures of the same code match for a before / after; not saved, restored at quit)]
##     [--try=spill,air (LOOK-TOOLBOX lab only, pov / pod: the helix as a toon spill source, Solace green, at
##     --spill-y=<BU over the plinth> with radius --spill-r=<x city_sol_plinth_r_bu> and --spill-i=<intensity>; the
##     rc_look air pass, night preset, with --air-density / --air-start overrides)]
## Prints "HQRUN <state> gpu_ms=<city viewport GPU ms> frame_ms=<frame ms>" per state.

const MAX_WAIT := 900

var _args: Dictionary = {}
var _states: PackedStringArray = PackedStringArray()
var _step: int = 0
var _frame: int = 0
var _host: Control = null
var _city: CityView3D = null
var _backdrop: CombatBackdrop = null
var _perf: Array[float] = []
var _frame_ms: Array[float] = []
var _ready_at: int = -1
var _scale_was: float = -1.0
var _reduce_was: int = -1
## LOOK-TOOLBOX lab only (--try=spill): the spill sources set on the city every frame.
var _try_spill: Array = []
## B4: the HQ-run page on show (its landmark share is printed).
var _view: HqRunView = null


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_states = PackedStringArray(String(_args.get("states", "run_meridian")).split(","))
	if _args.has("tier"):
		Settings.city_quality = int(_args["tier"])
	if _args.has("reduce-effects"):
		_reduce_was = int(Settings.reduce_effects)
		Settings.reduce_effects = _args["reduce-effects"] == "1"
		RenderingServer.global_shader_parameter_set(Fx.REDUCE_GLOBAL, 1.0 if Settings.reduce_effects else 0.0)
	if _args.has("scale"):
		# Parity S-HQRUN: the pages and the gate at a text size (1.0 / 1.6 / 2.0); restored at quit.
		_scale_was = Settings.text_scale
		Settings.text_scale = float(_args["scale"])
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_load(_states[0])


func _corp_of(state: String) -> StringName:
	return StringName(state.split("_", true, 1)[1])



## LOOK-TOOLBOX: every state starts the same campaign (seed 11, `corp`), so the city (CityPlan.current_seed) is the
## same whatever ran before in this launch or what the lab's save slot last held.
func _campaign(corp: StringName) -> void:
	RunManager.save_slot = "lab_hq_run"
	# Parity S-HQRUN: every corporation's own campaign (its boss on the gate), not the locked
	# corporations' fallback to Solace: the lab's profile (its own APPDATA) holds the unlock.
	var u := CampaignRules.unlock_for(RunManager.lookup(), RunManager.lookup().get_content(corp))
	var added := u != null and not RunManager.profile.unlocks.has(u.id)
	if added:
		RunManager.profile.unlocks.append(u.id)
	RunManager.new_campaign(11, corp)
	if added:
		RunManager.profile.unlocks.erase(u.id)


func _session(corp: StringName) -> NetrunSession:
	_campaign(corp)
	var c := RunManager.campaign
	for e in [RC.ExploitType.INTEL, RC.ExploitType.BREACH, RC.ExploitType.VIRUS]:
		if not c.exploits.has(e):
			c.exploits.append(e)
	var cd := RunManager.corporation
	var site: StringName = &""
	for sd in cd.city_grid.sites:
		if sd != null and sd.objective == RC.SiteObjective.CENTRAL_SERVER:
			site = sd.id
	return NetrunSession.start_special(RunManager.resolver, c, c.living_operatives()[0].id, "boss", site, 4, 5, cd.final_boss.id,
		CampaignRules.boss_overrides(c, cd), cd)


func _load(state: String) -> void:
	if _host != null:
		_host.queue_free()
	_host = Control.new()
	_host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_host)
	_city = null
	_view = null
	_backdrop = null
	_perf.clear()
	_frame_ms.clear()
	_ready_at = -1
	_frame = 0
	var kind := state.split("_", true, 1)[0]
	var corp := _corp_of(state)
	match kind:
		"run", "full", "gate":
			var s := _session(corp)
			var v := HqRunView.new()
			_view = v
			v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			_host.add_child(v)
			var graph := s.run.map
			var visited: Array[StringName] = []
			var avail := s.available_nodes()
			var current: StringName = &""
			if kind == "full":
				graph = MapGenerator.generate(4, RunManager.config(), RngStreams.make_stream(9, &"map"))
				var at: StringName = graph.first_layer_ids()[0]
				for i in 3:
					visited.append(at)
					var nx: Array = graph.get_node(at).get("next", [])
					if nx.is_empty():
						break
					current = at
					at = nx[0]
				avail.clear()
				for n in graph.get_node(current).get("next", []):
					avail.append(n)
			v.show_run(corp, graph, current, visited, avail, HqCompoundStage.server_name(HqCompoundStage.manifest(corp)))
			_city = v.city
			if kind == "gate":
				var g := CentralServerGate.new()
				var held: Array[int] = []
				held.assign(CentralServerGate.KINDS)
				g.setup(corp, TextDb.t(RunManager.corporation, "display_name"),HqCompoundStage.server_name(HqCompoundStage.manifest(corp)), 4, held, 3,
					s.breach_preview(), RunManager.lookup())
				_host.add_child(g)
		"pov", "pod":
			var cj: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("%s/hq_%s_%s_capture.json" % [String(_args.get("plates", "")),
				corp, "overview" if kind == "pov" else "decision"]))
			var cm: Dictionary = cj["camera"]
			var size := Vector2(get_viewport().get_visible_rect().size)
			var m := HqCompoundStage.manifest(corp)
			var at := HqCompoundStage.place(CityView3D.CONFIG, corp, m)
			var iso := _plate_camera(cm, size, at, m)
			var c := CityView3D.new()
			c.band_lock = CityLod.Band.GRID
			c.set_iso(iso)
			c.stage_compound(corp)
			_host.add_child(c)
			c.set_view_size(Vector2i(size))
			var tr := TextureRect.new()
			tr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
			tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			tr.texture = c.get_texture()
			_host.add_child(tr)
			_city = c
			_try_look(c, at.origin)
		"hq", "site", "won":
			_campaign(corp)
			_backdrop = CombatBackdrop.new()
			_host.add_child(_backdrop)
			var cd := RunManager.lookup().get_content(corp) as CorporationData
			# LOOK-TOOLBOX: the Site that carries the corp's Site landmark when there is one (the statue, dishes,
			# SOLACE GENERAL), else the first T1 Site.
			var site: StringName = CityLandmarks.site_of(CityView3D.CONFIG, corp) if kind != "hq" else &""
			for sd in cd.city_grid.sites:
				if sd != null and sd.tier == 1 and site == &"":
					site = sd.id
			_backdrop.show_place(BackdropCatalog.place(corp, kind == "hq", false, site))
			_city = _backdrop.city


## LOOK-TOOLBOX lab only: the --try looks on a plate view (see the header).
func _try_look(c: CityView3D, at: Vector3) -> void:
	var tries := String(_args.get("try", "")).split(",", false)
	if tries.has("spill"):
		var camp := load("res://content/config/campaign_config.tres") as CampaignConfigData
		var r := camp.city_sol_plinth_r_bu * float(_args.get("spill-r", "1.0"))
		_try_spill = [{"position": at + Vector3(0.0, float(_args.get("spill-y", "20.0")), 0.0), "radius": r,
			"color": Palette.CORP_SOLACE, "intensity": float(_args.get("spill-i", "1.0"))}]
	if tries.has("air"):
		var o := {}
		if _args.has("air-density"):
			o["density"] = float(_args["air-density"])
		if _args.has("air-start"):
			o["start"] = float(_args["air-start"])
		c.add_child(RcLookAir.pass_node(RcLookAir.preset(&"night"), at.y, o))


func _process(delta: float) -> void:
	_frame += 1
	if not _try_spill.is_empty() and _city != null:
		_city.set_spill(_try_spill)
	if _city == null and _backdrop != null:
		_city = _backdrop.city
	var ready := _city == null or (_city.model != null and not _city.is_processing())
	if _backdrop != null:
		ready = ready and (_backdrop.on_city() or _backdrop.city == null)
	if ready and _ready_at < 0:
		_ready_at = _frame
		if _city != null:
			RenderingServer.viewport_set_measure_render_time(_city.get_viewport_rid(), true)
		if _backdrop != null and _states[_step].begins_with("won_"):
			_backdrop.play_won(true)
	if _ready_at < 0 and _frame < MAX_WAIT:
		return
	var since := _frame - maxi(_ready_at, 0)
	var settle := int(_args.get("settle", "30"))
	var perf := int(_args.get("perf", "60"))
	if since > settle and _city != null:
		_perf.append(RenderingServer.viewport_get_measured_render_time_gpu(_city.get_viewport_rid()))
		_frame_ms.append(delta * 1000.0)
	if since < settle + perf:
		return
	var state := _states[_step]
	var out :=String(_args.get("out", "user://hq_run_lab"))
	DirAccess.make_dir_recursive_absolute(out)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, state])
	if _args.has("raw") and _backdrop != null and _backdrop.on_city():
		# S-ARENA: the close-up's own render before the backdrop's grade (test fixtures).
		var raw := _backdrop.city.get_texture().get_image()
		var wh := String(_args["raw"]).split("x")
		raw.resize(int(wh[0]), int(wh[1]), Image.INTERPOLATE_NEAREST)  # point samples: no averaging bias
		raw.save_png("%s/%s_raw.png" % [out, state])
	var share := -1.0
	if _view != null and _view.iso != null:
		share = _view.landmark_share()
	print("HQRUN %s ready=%s gpu_ms=%.2f frame_ms=%.2f ortho=%.1f landmark=%.2f" % [state, _ready_at >= 0, _avg(_perf), _avg(_frame_ms),
		_city.iso.ortho if _city != null and _city.iso != null else -1.0, share])
	_step += 1
	if _step >= _states.size():
		RunManager.delete_save()
		if _reduce_was >= 0:
			Settings.reduce_effects = _reduce_was == 1
		if _scale_was > 0.0:
			Settings.text_scale = _scale_was
		get_tree().quit()
		return
	_load(_states[_step])


## A golden plate's Blender camera (capture.json `camera`: loc / tgt in Blender BU, lens mm on a 36 mm sensor, lens shift) as the city's
## perspective iso camera on the compound placed at `at`: Godot yaw = 90 - the rig yaw, fov = the horizontal angle, `ortho` the width at the
## target; the lens shift moves the aim across the target plane.
static func _plate_camera(cm: Dictionary, size: Vector2, at: Transform3D, m: Dictionary) -> CityIsoCamera:
	var loc: Array = cm["loc"]
	var tgt: Array = cm["tgt"]
	var k := HqSolaceMaterials.unit_k(m)  # the plate's Blender BU are plate (kit) units; the compound is exported in city BU
	var t_g := at * (Vector3(float(tgt[0]), float(tgt[2]), -float(tgt[1])) * k)
	var l_g := at * (Vector3(float(loc[0]), float(loc[2]), -float(loc[1])) * k)
	var dir := (t_g - l_g)
	var cam := CityIsoCamera.new()
	cam.viewport = size
	cam.fov_deg = rad_to_deg(2.0 * atan(18.0 / float(cm["lens"])))
	cam.pitch_deg = float(cm["pitch"])
	cam.yaw_deg = 90.0 - float(cm["yaw"])
	# The Godot yaw differs from the plate on purpose: it looks inland (HqCompoundStage.inland_yaw), the plate's pitch, distance and lens stay.
	var inland := HqCompoundStage.inland_yaw(CityView3D.CONFIG, m, at, CityPlan.current_seed())
	if not is_nan(inland):
		cam.yaw_deg = inland
		if OS.get_cmdline_user_args().has("--dbg_inland"):
			var plan := CityPlan.for_seed(CityPlan.current_seed())
			var c := CityIsoCamera.world_to_lot(CityView3D.CONFIG, at.origin)
			var row := ""
			for deg in range(0, 360, 30):
				var d := Vector2(cos(deg_to_rad(deg)), -sin(deg_to_rad(deg)))
				var land := 0
				for r in range(10, 71, 2):
					var q := c + d * r
					if plan.rect.has_point(Vector2i(floori(q.x), floori(q.y))) and not plan.is_water(floori(q.x), floori(q.y)):
						land += 1
				row += " %d:%d" % [deg, land]
			print("INLAND yaw=%.1f lot=%s rect=%s land/31 by yaw:%s" % [inland, c, plan.rect, row])
	cam.ortho = 2.0 * dir.length() * tan(deg_to_rad(cam.fov_deg) * 0.5)
	cam.target = t_g + cam.right() * float(cm["shift_x"]) * cam.ortho + cam.up() * float(cm["shift_y"]) * cam.ortho
	return cam


static func _avg(a: Array[float]) -> float:
	if a.is_empty():
		return -1.0
	var t := 0.0
	for x in a:
		t += x
	return t / a.size()
