extends Node
## ART-5 5e: the city integration's windowed capture (one launch). Per corporation it opens
## the game's City Grid page and writes: the Grid as fitted (`grid_<corp>.png`, its ortho and
## band printed: round 39 frames at ~440), the Site landmark close at raid zoom with the roof
## props (`site_<corp>.png`), the map panned off the Central Server (`target_<corp>.png`: the
## red TARGET arrow on the edge); for the REBEL_CELL campaign the Cell's district through its
## blackout reveal (`reveal_<q>.png`, DISPATCH's fist); and, once, the street traffic under
## reduce motion (its clock runs at 40 %). Prints CAPTURE lines; frames 800x450. Run:
##   python tools/run_windowed.py --log <f> -- --resolution 1280x720 res://tools/city/city_integration_capture.tscn
##       -- --out=<abs dir> [--corps=a,b] [--heat=N]

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const CORPS: Array[String] = ["solace", "halcyon", "orbital", "meridian", "rebel_cell"]
const SIZE := Vector2i(1280, 720)
const SHOT := Vector2i(800, 450)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 40
## The close look at a Site landmark (ortho BU: the RAID band, roof props on).
const CLOSE_ORTHO := 180.0
## The roof props' close look (ortho BU) and its offset from the Site landmark (lots).
const PROPS_ORTHO := 70.0
const PROPS_OFFSET := Vector2(8, 8)
## Lots the TARGET shot pans away from the Central Server.
const PAN_AWAY := Vector2(-60, 0)
const REVEALS: Array[float] = [0.0, 0.5, 1.0]

var _out := ""
var _heat := -1


func _ready() -> void:
	var corps: Array[String] = CORPS.duplicate()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--corps="):
			corps.assign(a.trim_prefix("--corps=").split(",", false))
		elif a.begins_with("--heat="):
			_heat = int(a.trim_prefix("--heat="))
	DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://city_integration_capture_settings.json"
	SaveService.save_dir = "user://saves/city_integration_capture"
	RunManager.save_slot = "gut_city_integration_capture"
	RunManager.scene_switching_enabled = false

	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	for corp in corps:
		await _corp(corp)
	print("CAPTURE DONE")
	RunManager.delete_save()
	get_tree().quit(0)


func _corp(corp: String) -> void:
	var hq: Control = HQ.instantiate()
	get_tree().root.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	hq.new_campaign(1)
	# Any corporation, locked or not (the tests' way): the campaign made against it directly.
	var cd := RunManager.lookup().get_content(StringName(corp)) as CorporationData
	var home := RunManager.lookup().get_content(RunManager.DEFAULT_HOME) as HomeServerVariantData
	RunManager.corporation = cd
	RunManager.campaign = CampaignRules.new_campaign(cd, RunManager.config(), RunManager.lookup(), 1,
		RunManager.lookup().get_content(RunManager.DEFAULT_CLASS) as ClassData, home.core, 0, home)
	if _heat >= 0:
		RunManager.campaign.heat = _heat
	hq.show_grid()
	var city: NeonCity = hq.wireframe.city
	var view: CityView3D = null
	for i in MODEL_WAIT_FRAMES:
		view = city.view3d
		if view != null and view.model != null and view._pending.is_empty() and view.chunks_built() > 0:
			break
		await get_tree().process_frame
	if view == null:
		print("CAPTURE FAIL %s no view" % corp)
		hq.queue_free()
		return
	await _settle()
	var life := city.city_life
	print("CAPTURE grid corp=%s campaign=%s ortho=%.0f band=%d landmarks=%d site=%s dispatch=%s heat_band=%d hardened=%d reveal=%.2f" % [corp,
		RunManager.corporation.id, view.iso.ortho, view.band, view.layer(&"landmarks").get_child_count(), str(view.site_landmark),
		view.cell_dispatch, int(life.get("heat_band", -1)), (life.get("hardened", []) as Array).size(), view.cell_reveal])
	await _shot("grid_%s" % corp)
	var gt: TargetEdgeMarker = hq.grid_target
	print("CAPTURE target-on-grid corp=%s showing=%s" % [corp, gt.showing() if gt != null else false])
	# The Site landmark close (raid zoom: the roof props show).
	var lot: Vector2 = life.get("site_lot", Vector2.INF)
	if lot == Vector2.INF:
		lot = Vector2(life.get("home_lot", Vector2.ZERO))
	var zoom := float(hq.size.x) / (CLOSE_ORTHO * NeonCity.px_per_bu())
	hq._frame_city(zoom, lot, Vector2(0.5, 0.5))
	await _settle()
	print("CAPTURE site corp=%s ortho=%.0f band=%d props=%s" % [corp, view.iso.ortho, view.band, str(view.roof_prop_counts())])
	await _shot("site_%s" % corp)
	# Closer still: the roof props on their roofs.
	hq._frame_city(float(hq.size.x) / (PROPS_ORTHO * NeonCity.px_per_bu()), lot + PROPS_OFFSET, Vector2(0.5, 0.5))
	await _settle()
	await _shot("props_%s" % corp)
	# Off the Central Server: the TARGET arrow on the edge.
	var boss := Vector2.INF
	for n: Dictionary in hq.city_overlay.nodes:
		if n.has("marker") and n["marker"].get("kind") == SiteMarker.KIND_CENTRAL_SERVER:
			boss = Vector2(hq.city_overlay.lot_of(n["id"]))
	if boss != Vector2.INF:
		hq._frame_city(float(hq.size.x) / (view.cfg.grid_ortho * NeonCity.px_per_bu()), boss + PAN_AWAY, Vector2(0.5, 0.5))
		await _settle()
		print("CAPTURE target corp=%s showing=%s tip=%s" % [corp, gt.showing() if gt != null else false, str(gt.tip() if gt != null else Vector2.INF)])
		await _shot("target_%s" % corp)
	if corp == "rebel_cell":
		var centre := NeonCity.hq_of(&"rebel_cell") + Vector2(NeonCity.HQ_LOTS, NeonCity.HQ_LOTS) * 0.5
		hq._frame_city(float(hq.size.x) / (view.cfg.grid_ortho * 0.8 * NeonCity.px_per_bu()), centre, Vector2(0.5, 0.5))
		await _settle()
		for q in REVEALS:
			Motion.settle(view, ^"cell_reveal")
			view.cell_reveal = q
			await _settle(8)
			await _shot("reveal_%03d" % roundi(q * 100.0))
		print("CAPTURE reveal dispatch=%s" % view.cell_dispatch)
	if corp == CORPS[0] or corp == "solace":
		var layers := city.city_motion.layers if city.city_motion != null else null
		if layers != null:
			var was := Settings.reduce_motion
			Settings.reduce_motion = true
			Settings.changed.emit()
			var t0 := layers.layer_time(CityMotionClock.Layer.STREET_CARS)
			var s0 := Time.get_ticks_msec()
			await _settle(60)
			var dt := (Time.get_ticks_msec() - s0) / 1000.0
			var t1 := layers.layer_time(CityMotionClock.Layer.STREET_CARS)
			print("CAPTURE reduce_motion street_rate=%.2f (wall %.2f s, layer %.2f s) sky_cars=%s host_ambient=%.1f" % [(t1 - t0) / maxf(dt, 0.001),
				dt, t1 - t0, layers.sky_cars_visible(), layers.host_ambient])
			Settings.reduce_motion = was
			Settings.changed.emit()
	hq.queue_free()
	await get_tree().process_frame
	await get_tree().process_frame


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.resize(SHOT.x, SHOT.y, Image.INTERPOLATE_BILINEAR)
	img.save_png(_out.path_join(name_ + ".png"))
