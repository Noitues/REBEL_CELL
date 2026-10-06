extends Node
## ART-5 5e: the "every host shows buildings" windowed check. One launch builds the 3D city
## in each way the game and the tools host it, waits for the model, then measures what the
## window shows with the buildings layer on and off: a host whose buildings do not reach the
## screen shows (almost) no difference. Prints one HOSTCHECK line per host and a verdict
## line; with --out writes a PNG per host (800x450). Windowed only (run_windowed.py):
##   res://tools/city/city_hosts_check.tscn -- [--out=<abs dir>] [--hosts=a,b]
## Hosts: lab (a Control + TextureRect, 5a's city lab), container (a stretched
## SubViewportContainer, 5c's capture), campaign (a campaign made while the city builds, then
## a container, 5d's capture), gridpage (the game's City Grid page), lab_motion (the lab
## with 5c's motion and 5e's landmarks).

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const HOSTS: Array[String] = ["lab", "container", "campaign", "gridpage", "lab_motion"]
const SIZE := Vector2i(1280, 720)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 30
## Mean absolute RGB difference (0..1) the buildings must make on the screen.
const MIN_DIFF := 0.02
## The capture's size on disk.
const SHOT := Vector2i(800, 450)

var _out := ""
var _fails: Array[String] = []


func _ready() -> void:
	var hosts: Array[String] = HOSTS.duplicate()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--hosts="):
			hosts.assign(a.trim_prefix("--hosts=").split(",", false))
	if _out != "":
		DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://city_hosts_check_settings.json"
	SaveService.save_dir = "user://saves/city_hosts_check"
	RunManager.save_slot = "gut_city_hosts_check"
	RunManager.scene_switching_enabled = false
	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	for h in hosts:
		await _host(h)
	print("HOSTCHECK verdict %s %s" % ["PASS" if _fails.is_empty() else "FAIL", ",".join(_fails)])
	RunManager.delete_save()
	get_tree().quit(0 if _fails.is_empty() else 1)


func _host(h: String) -> void:
	var root := Control.new()
	root.name = "Host_" + h
	root.size = Vector2(SIZE)
	get_tree().root.add_child(root)
	var view: CityView3D = null
	var hq: Node = null
	match h:
		"lab", "lab_motion":
			view = CityView3D.new()
			view.size = SIZE
			root.add_child(view)
			var rect := TextureRect.new()
			rect.size = Vector2(SIZE)
			rect.texture = view.get_texture()
			rect.stretch_mode = TextureRect.STRETCH_SCALE
			root.add_child(rect)
			if h == "lab_motion":
				view.add_child(CityViewMotion.make(view))
		"container", "campaign":
			if h == "campaign":
				RunManager.new_campaign(1, &"solace")
			var box := SubViewportContainer.new()
			box.stretch = true
			box.size = Vector2(SIZE)
			root.add_child(box)
			view = CityView3D.new()
			view.size = SIZE
			box.add_child(view)
		"gridpage":
			hq = HQ.instantiate()
			get_tree().root.add_child(hq)
			await get_tree().process_frame
			hq.new_campaign(1)
			hq.show_grid()
			for i in MODEL_WAIT_FRAMES:
				var city: NeonCity = hq.wireframe.city if hq.wireframe != null else null
				if city != null and city.view3d != null:
					view = city.view3d
					break
				await get_tree().process_frame
	if view == null:
		_fail(h, "no CityView3D")
		root.queue_free()
		if hq != null:
			hq.queue_free()
		return
	for i in MODEL_WAIT_FRAMES:
		if view.model != null and view._pending.is_empty() and view.chunks_built() > 0:
			break
		await get_tree().process_frame
	if h != "gridpage":
		var at := NeonCity.hq_of(&"solace") + Vector2(NeonCity.HQ_LOTS * 0.5, NeonCity.HQ_LOTS * 0.5) - CityLayout.RIGHT * 11.0
		view.set_iso(CityIsoCamera.make(view.cfg, view.lot_world(at), view.cfg.grid_ortho, Vector2(view.size)))
	for i in SETTLE_FRAMES:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var on := get_viewport().get_texture().get_image()
	var bl := view.layer(&"buildings")
	bl.visible = false
	for i in 3:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	var off := get_viewport().get_texture().get_image()
	bl.visible = true
	var diff := _diff(on, off)
	var inst := 0
	for chunk in bl.get_children():
		for mi in chunk.get_children():
			if mi is MultiMeshInstance3D:
				inst += (mi as MultiMeshInstance3D).multimesh.instance_count
	var lm := view.layer(&"landmarks").get_child_count()
	print("HOSTCHECK host=%s prisms=%d chunks=%d instances=%d landmarks=%d view=%s window=%s ortho=%.0f band=%d lod=%d diff=%.4f" % [h,
		view.model.prisms.size() if view.model != null else -1, view.chunks_built(), inst, lm, str(view.size),
		str(on.get_size()), view.iso.ortho if view.iso != null else -1.0, view.band, view.building_lod, diff])
	if diff < MIN_DIFF:
		_fail(h, "buildings make %.4f of the screen (< %.2f)" % [diff, MIN_DIFF])
	if _out != "":
		on.resize(SHOT.x, SHOT.y, Image.INTERPOLATE_BILINEAR)
		on.save_png(_out.path_join("host_%s.png" % h))
	root.queue_free()
	if hq != null:
		hq.queue_free()
	await get_tree().process_frame
	await get_tree().process_frame


func _fail(h: String, why: String) -> void:
	_fails.append(h)
	push_warning("HOSTCHECK %s: %s" % [h, why])
	print("HOSTCHECK FAIL host=%s %s" % [h, why])


## Mean absolute RGB difference of two same-size images, sampled on a coarse grid.
static func _diff(a: Image, b: Image) -> float:
	if a.get_size() != b.get_size():
		return 1.0
	var sum := 0.0
	var n := 0
	var step := 4
	for y in range(0, a.get_height(), step):
		for x in range(0, a.get_width(), step):
			var p := a.get_pixel(x, y)
			var q := b.get_pixel(x, y)
			sum += (absf(p.r - q.r) + absf(p.g - q.g) + absf(p.b - q.b)) / 3.0
			n += 1
	return sum / maxf(1.0, float(n))
