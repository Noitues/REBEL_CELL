extends Node
## LOOK_PORT L5 (city night view): the whole city under the A2 golden plate's hero pose (CityConfig `whole_pose_*`,
## designer 2026-10-19), night and day, the 3D view's own frame (no HUD, no map marks) at the plate's aspect. Writes
## `city_a2_night.png` and `city_a2_day.png` into --out and prints PARITY lines (centre lot, pose, frame size).
## Windowed only (tools/run_windowed.py, from a worktree or a copy):
##   python tools/run_windowed.py --log <f> -- --resolution 1920x1080 res://tools/netrun_art/city_a2_parity_lab.tscn
##       -- --out=<abs dir> [--seed=1]

const HQ := preload("res://scenes/hq/hq_scene.tscn")
const SIZE := Vector2i(1920, 1080)
const MODEL_WAIT_FRAMES := 2400
const SETTLE_FRAMES := 90

var _out := ""
## --look=<0..1>: the night shot's look blend (0 the city look, 1 the AAA-2 netrun look); the day shot is always 0.
var _look := 0.0


func _ready() -> void:
	var seed_ := 1
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--seed="):
			seed_ = int(a.trim_prefix("--seed="))
		elif a.begins_with("--look="):
			_look = float(a.trim_prefix("--look="))
	DirAccess.make_dir_recursive_absolute(_out)
	Settings.path = "user://city_a2_parity_settings.json"
	SaveService.save_dir = "user://saves/city_a2_parity"
	RunManager.save_slot = "gut_city_a2_parity"
	RunManager.scene_switching_enabled = false
	DisplayServer.window_set_size(SIZE)
	await get_tree().process_frame
	await _capture(seed_)
	print("PARITY DONE")
	RunManager.delete_save()
	get_tree().quit(0)


func _capture(campaign_seed: int) -> void:
	var hq: Control = HQ.instantiate()
	get_tree().root.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await get_tree().process_frame
	hq.new_campaign(campaign_seed)
	hq.show_grid()
	var city: NeonCity = hq.wireframe.city
	city.follow_city_seed()
	var view: CityView3D = null
	for i in MODEL_WAIT_FRAMES:
		view = city.view3d
		if view != null and view.model != null and view._pending.is_empty() and view.chunks_built() > 0:
			break
		await get_tree().process_frame
	if view == null or view.model == null:
		print("PARITY FAIL no view")
		return
	var plan := CityPlan.current()
	var centre := plan.a2.lot_of(Vector2.ZERO) if plan.a2 != null else Vector2(plan.rect.get_center())
	hq._frame_city(1.0, centre, Vector2(0.5, 0.5))
	city.whole_pose_centre = centre
	if _look > 0.0:
		view.set_look_blend(_look)
	await _settle()
	var cfg := view.cfg
	print("PARITY seed=%d centre=%s yaw=%.1f pitch=%.1f fov=%.2f dist=%.0f eye=%s view=%s band_lock=%d look=%.2f" % [campaign_seed,
		centre, cfg.whole_pose_yaw_deg, cfg.whole_pose_pitch_deg, cfg.whole_pose_fov_deg, cfg.whole_pose_dist_bu, view.iso.eye(),
		view.size, view.band_lock, view.look_blend])
	await _view_shot(view, "city_a2_night")
	var lay := city.city_motion.layers if city.city_motion != null else null
	if lay != null:
		view.set_look_blend(0.0)  # AAA-2 is the night look; the day keeps the city look
		lay.set_light(CityMotionLayers.Daylight.DAY, false)
		await _settle(roundi(Motion.seconds(CityMotionLayers.LIGHT_FADE) * 60.0) + SETTLE_FRAMES)
		await _view_shot(view, "city_a2_day")
	hq.queue_free()
	RunManager.reset()
	await get_tree().process_frame


func _settle(n: int = SETTLE_FRAMES) -> void:
	for i in n:
		await get_tree().process_frame


func _view_shot(view: CityView3D, name_: String) -> void:
	await RenderingServer.frame_post_draw
	var img := view.get_texture().get_image()
	print("PARITY shot %s %dx%d" % [name_, img.get_width(), img.get_height()])
	img.save_png(_out.path_join(name_ + ".png"))
