extends Control
## ART-8 8w review lab (windowed only; headless has no renderer): walks a list of states in ONE
## launch and writes a frame per state, with the city's GPU time:
##   run_<corp>       the HQ run's page (HqRunView) on the corp's compound (today's breach run)
##   full_<corp>      the same page with a full run map (GDD 4.2) half walked (layout review)
##   gate_<corp>      the Central Server's gate over the page (all three Exploits)
##   hq_<corp> / site_<corp> / won_<corp>   the combat backdrop's city close-up (D17): the boss
##                    fight's HQ, a regular fight's Site, the Site fight won
##   python tools/run_windowed.py --log <f> -- --resolution 1920x1080
##     res://tools/art_pipeline/hq_run/hq_run_lab.tscn -- --out=<dir> --states=run_meridian,gate_solace
##     [--tier=1] [--settle=30] [--perf=60] [--raw=160x90 (S-ARENA: also <state>_raw.png, the
##     backdrop city's own render before its grade, at that size)]
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


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_states = PackedStringArray(String(_args.get("states", "run_meridian")).split(","))
	if _args.has("tier"):
		Settings.city_quality = int(_args["tier"])
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var bg := ColorRect.new()
	bg.color = Palette.NIGHT_SKY
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_load(_states[0])


func _corp_of(state: String) -> StringName:
	return StringName(state.split("_", true, 1)[1])


func _session(corp: StringName) -> NetrunSession:
	RunManager.save_slot = "lab_hq_run"
	RunManager.new_campaign(11, corp)
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
				g.setup(corp, String(corp).capitalize(), HqCompoundStage.server_name(HqCompoundStage.manifest(corp)), 4, held, 3,
					s.breach_preview(), RunManager.lookup())
				_host.add_child(g)
		"hq", "site", "won":
			_backdrop = CombatBackdrop.new()
			_host.add_child(_backdrop)
			var cd := RunManager.lookup().get_content(corp) as CorporationData
			var site: StringName = &""
			for sd in cd.city_grid.sites:
				if sd != null and sd.tier == 1 and site == &"":
					site = sd.id
			_backdrop.show_place(BackdropCatalog.place(corp, kind == "hq", false, site))
			_city = _backdrop.city


func _process(delta: float) -> void:
	_frame += 1
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
	var out := String(_args.get("out", "user://hq_run_lab"))
	DirAccess.make_dir_recursive_absolute(out)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, state])
	if _args.has("raw") and _backdrop != null and _backdrop.on_city():
		# S-ARENA: the close-up's own render before the backdrop's grade (test fixtures).
		var raw := _backdrop.city.get_texture().get_image()
		var wh := String(_args["raw"]).split("x")
		raw.resize(int(wh[0]), int(wh[1]), Image.INTERPOLATE_NEAREST)  # point samples: no averaging bias
		raw.save_png("%s/%s_raw.png" % [out, state])
	print("HQRUN %s ready=%s gpu_ms=%.2f frame_ms=%.2f ortho=%.1f" % [state, _ready_at >= 0, _avg(_perf), _avg(_frame_ms), _city.iso.ortho if _city != null and _city.iso != null else -1.0])
	_step += 1
	if _step >= _states.size():
		RunManager.delete_save()
		get_tree().quit()
		return
	_load(_states[_step])


static func _avg(a: Array[float]) -> float:
	if a.is_empty():
		return -1.0
	var t := 0.0
	for x in a:
		t += x
	return t / a.size()
