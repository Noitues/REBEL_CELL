extends Control
## NA-ID lab (windowed only, through tools/run_windowed.py): the general id capture (IdCapture) on HQ, landmark and city frames.
##   python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://tools/netrun_art/id_capture_lab.tscn -- --out=<dir>
##     [--frames=hq:meridian,landmark:solace,city:grid]   kind:arg per frame (default hq:meridian,landmark:solace,city:grid)
##     [--settle=60] [--seed=11] [--mover=1]  (--mover tags the first landmark mesh `id_mover` to exercise class 6)
## Writes <out>/<kind>_<arg>/{beauty,id,depth}.png + capture.json and prints "NAID <frame> counts {...}".
## hq: the HQ-run page's city (HqRunView, the compound staged, the run camera). landmark: the corp's landmark close-up. city: the Grid.

const MAX_WAIT := 900

var _args: Dictionary = {}
var _frames: PackedStringArray = PackedStringArray()
var _step := -1
var _tick := 0
var _city: CityView3D = null
var _host: Control = null
var _meta: Dictionary = {}
var _busy := false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--") and a.contains("="):
			var kv := a.trim_prefix("--").split("=", true, 1)
			_args[kv[0]] = kv[1]
	_frames = PackedStringArray(String(_args.get("frames", "hq:meridian,landmark:solace,city:grid")).split(","))
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_next()


func _next() -> void:
	_step += 1
	_tick = 0
	if _step >= _frames.size():
		RunManager.delete_save()
		get_tree().quit()
		return
	if _host != null:
		_host.queue_free()
	_host = Control.new()
	_host.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_host)
	var parts := _frames[_step].split(":")
	var corp := StringName(parts[1])
	match parts[0]:
		"hq":
			_load_hq(corp)
		"landmark":
			_load_city(CityIsoCamera.make(CityView3D.CONFIG, Vector3.ZERO, float(_args.get("ortho", "150")), size), corp)
		"city":
			_load_city(CityIsoCamera.make(CityView3D.CONFIG, Vector3.ZERO, CityView3D.CONFIG.grid_ortho, size), &"")


func _load_hq(corp: StringName) -> void:
	RunManager.save_slot = "lab_naid"
	RunManager.new_campaign(int(_args.get("seed", "11")), corp)
	var c := RunManager.campaign
	var cd := RunManager.corporation
	var site: StringName = &""
	for sd in cd.city_grid.sites:
		if sd != null and sd.objective == RC.SiteObjective.CENTRAL_SERVER:
			site = sd.id
	var s := NetrunSession.start_special(RunManager.resolver, c, c.living_operatives()[0].id, "boss", site, 4, 5, cd.final_boss.id,
		CampaignRules.boss_overrides(c, cd), cd)
	var v := HqRunView.new()
	v.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_host.add_child(v)
	v.show_run(corp, s.run.map, &"", [], s.available_nodes(), HqCompoundStage.server_name(HqCompoundStage.manifest(corp)))
	_city = v.city
	_meta = {"kind": "hq", "view": "overview", "look": "mainline", "corp": String(corp), "run": "naid_hq_%s" % corp,
		"exempt": {"hover_cut": false, "red_seq": false, "flash": false}}


func _load_city(iso: CityIsoCamera, corp: StringName) -> void:
	var c := CityView3D.new()
	c.band_lock = CityLod.Band.GRID
	c.set_iso(iso)
	_host.add_child(c)
	c.set_view_size(Vector2i(size))
	_city = c
	_meta = {"kind": "city", "view": "city", "look": "mainline", "corp": String(corp), "run": "naid_city",
		"exempt": {"hover_cut": false, "red_seq": false, "flash": false}}


func _aim() -> void:
	var corp := StringName(_frames[_step].split(":")[1])
	if _frames[_step].begins_with("landmark") and _city.landmarks.has(corp):
		var iso := _city.iso.copy()
		iso.target = (_city.landmarks[corp] as Node3D).global_position
		_city.set_iso(iso)
	# Smoke for class 6 (no shipped landmark moves yet): every other mesh of the frame's landmark / compound is tagged a mover.
	var node: Node = _city.compounds.get(corp, null)
	if node == null:
		node = _city.landmarks.get(corp, null)
	if _args.has("mover") and node != null:
		var meshes := node.find_children("*", "MeshInstance3D", true, false)
		for i in range(0, meshes.size(), 2):
			(meshes[i] as Node).add_to_group(IdCaptureClasses.GROUP_MOVER)


func _process(_delta: float) -> void:
	if _step < 0 or _step >= _frames.size() or _busy or _city == null:
		return
	_tick += 1
	var ready := _city.model != null and not _city.is_processing()
	if not ready and _tick < MAX_WAIT:
		return
	_busy = true
	_shoot()


func _shoot() -> void:
	_aim()
	for _i in int(_args.get("settle", "60")):
		await get_tree().process_frame
	var name := _frames[_step].replace(":", "_")
	var dir := "%s/%s" % [String(_args.get("out", "user://naid")), name]
	var res: Dictionary = await IdCapture.new(get_tree(), _city).write(dir, _meta)
	print("NAID %s ok=%s counts %s" % [name, res["ok"], res.get("counts", {})])
	_busy = false
	_city = null
	_next()
