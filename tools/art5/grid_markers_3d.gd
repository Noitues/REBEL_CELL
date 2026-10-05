extends Node
## ART-5 5d: the Site markers v4 on 5a's real-time 3D city (CityView3D): one windowed launch
## walks the corporations x text scales 1.0 / 1.6 / 2.0 x the Grid zoom and x1.7, with the
## markers placed through the GridMarkerProjection seam (SiteMarkerLayer), the v4 map key,
## and the fight-won lights in the city's `fx` layer. Writes one PNG per state. Dev tool,
## never exported; run only through tools/run_windowed.py:
##   res://tools/art5/grid_markers_3d.tscn -- --out=<abs dir> [--corps=a,b]

const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital"]
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const ZOOMS: Array[float] = [1.0, 1.7]
const SIZE := Vector2i(1280, 720)
## Runs completed before the picture, and frames the city gets to build and settle.
const RUNS := 4
const MODEL_WAIT_FRAMES := 1800
const SETTLE_FRAMES := 45
const DEMO_SCHEMATICS := 100

var out_dir := ""


func _ready() -> void:
	var corps := CORPS.duplicate()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		elif a.begins_with("--corps="):
			corps.clear()
			for c in a.trim_prefix("--corps=").split(",", false):
				corps.append(StringName(c))
	DirAccess.make_dir_recursive_absolute(out_dir)
	Settings.path = "user://grid_markers_3d_settings.json"
	SaveService.save_dir = "user://saves/grid_markers_3d"
	RunManager.save_slot = "gut_grid_markers_3d"
	RunManager.scene_switching_enabled = false
	for u in [&"unlock_meridian", &"unlock_halcyon", &"unlock_orbital"]:
		if not RunManager.profile.unlocks.has(u):
			RunManager.profile.unlocks.append(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10
	var count := 0
	for corp in corps:
		count += await _corp_frames(corp)
	print("GRID MARKERS 3D DONE %d frames in %s" % [count, out_dir])
	RunManager.delete_save()
	get_tree().quit()


func _corp_frames(corp_id: StringName) -> int:
	var c := RunManager.new_campaign(1, corp_id)
	var corp := RunManager.corporation
	var cfg := RunManager.config()
	for i in RUNS:
		var open := RunManager.launchable_sites().filter(func(s: SiteData) -> bool: return s.objective != RC.SiteObjective.CENTRAL_SERVER)
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		run.kind = CampaignRules.run_kind_for(c, open[0])
		CampaignRules.on_run_completed(c, corp, cfg, run, RunManager.lookup())
	DemoSetup.set_schematics(c, DEMO_SCHEMATICS)
	var cleared: Array[StringName] = []
	for sd in corp.city_grid.sites:
		if sd != null and c.grid.is_cleared(sd.id):
			cleared.append(sd.id)
	if cleared.size() >= 2:
		CampaignRules.claim(c, corp, cfg, RunManager.lookup(), cleared[0], &"firewall_relay")
		c.grid.sites[cleared[0]]["condition"] = GridState.Condition.DOWN
		c.grid.sites[cleared[1]]["status"] = GridState.SiteStatus.TAKEN
	var root := Control.new()
	root.size = Vector2(SIZE)
	get_tree().root.add_child.call_deferred(root)
	await get_tree().process_frame
	var host := SubViewportContainer.new()
	host.stretch = true
	host.size = Vector2(SIZE)
	root.add_child(host)
	var view := CityView3D.new()
	view.size = SIZE
	host.add_child(view)
	for i in MODEL_WAIT_FRAMES:
		if view.model != null and view._pending.is_empty():
			break
		await get_tree().process_frame
	var g := CityLayout.grid_graph(c, corp, CityLayout.threat_paths(c, corp), &"", true)
	var specs := {}
	var labels := {}
	var won := {}
	var lots := CityLayout.site_points(corp)
	for n in g["nodes"]:
		specs[n["id"]] = n["marker"]
		labels[n["id"]] = String(n["label"])
		if bool(n["marker"]["won"]):
			won[n["id"]] = lots[n["id"]]
	if view.model != null:
		var lights := SiteWonLights.new()
		lights.build(view.model, won)
		view.add_to_layer(&"fx", lights)
	var proj := GridMarkerProjection.from_view(view, corp)
	var layer := SiteMarkerLayer.new()
	layer.size = Vector2(SIZE)
	root.add_child(layer)
	var legend := MapLegend.pin_to(root, corp_id, true).use_site_markers()
	var frames := 0
	for zoom in ZOOMS:
		var cam := CityIsoCamera.make(view.cfg, Vector3.ZERO, view.cfg.grid_ortho / zoom, Vector2(SIZE))
		proj.camera = cam
		proj.aim_at_sites()
		view.set_iso(cam)
		layer.attach(proj, specs, labels)
		for scale in SCALES:
			Settings.text_scale = scale
			Settings.changed.emit()
			legend.set_strip_width(float(SIZE.x) * 0.6)
			layer.replace()
			for i in SETTLE_FRAMES:
				await get_tree().process_frame
			await RenderingServer.frame_post_draw
			var img := get_viewport().get_texture().get_image()
			img.save_png(out_dir.path_join("%s_z%s_s%s.png" % [corp_id, str(zoom).replace(".", ""), str(scale).replace(".", "")]))
			frames += 1
	root.queue_free()
	await get_tree().process_frame
	return frames
