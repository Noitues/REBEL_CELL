extends GutTest
## LOOK-TOOLBOX module 19 (full tier; art-pass ruling): the street's look overrides hold live. RouteRig re-applies look.building
## (and the zoom haze), look.ground and look.post on every frame_pre_draw, so CityView3D re-running _whole_building
## (set_night_share, as CityViewMotion does) or setup_post (set_aaa_exposure) never loses them. Unfrozen: the motion runs.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCRIPT := preload("res://scripts/ui/netrun_scene.gd")
## How long the unfrozen motion runs before the check.
const LIVE_S := 2.0

var _scene: Control = null


func before_each() -> void:
	Motion.force_live = true
	AudioDirector.muted = true
	RunManager.save_slot = "gut_street_hold"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()
	SCRIPT.force_street_error = ""
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	_scene = load(NETRUN).instantiate()
	holder.add_child(_scene)
	_scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	_scene.start_run(1)
	await get_tree().process_frame
	await get_tree().process_frame


func after_each() -> void:
	Motion.force_live = false
	CityBakeCache.shutdown()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _drift(rig: RouteRig) -> PackedStringArray:
	var out := PackedStringArray()
	for pair: Array in rig.street_overrides():
		var m: ShaderMaterial = pair[0]
		var d: Dictionary = pair[1]
		for k: String in d:
			if m.get_shader_parameter(StringName(k)) != d[k]:
				out.append("%s = %s, wants %s" % [k, m.get_shader_parameter(StringName(k)), d[k]])
	return out


func test_the_street_overrides_hold_under_live_motion_and_view_resets() -> void:
	var v: StreetRouteView = _scene.street_view
	assert_not_null(v, "the street page is up")
	var rig := v.rig
	assert_gt(rig.street_overrides().size(), 0, "the rig has overrides")
	assert_eq(_drift(rig).size(), 0, "at rest: %s" % str(_drift(rig)))
	var motion := CityViewMotion.make(rig.view, null, Vector2.ZERO)
	rig.view.add_child(motion)
	# What CityViewMotion and a look change do to the view: the view's own defaults come back over the street's.
	rig.view.set_night_share(0.4, CityViewMotion.day_look(CityMotionConfigData.shipped()))
	rig.view.set_aaa_exposure(1.3)
	assert_gt(_drift(rig).size(), 0, "the resets do overwrite the street look (the hold is needed)")
	var t := 0.0
	while t < LIVE_S:
		await get_tree().process_frame
		t += get_process_delta_time()
	assert_eq(_drift(rig).size(), 0, "after %s s of live motion: %s" % [LIVE_S, str(_drift(rig))])
	rig.view.set_night_share(0.9, CityViewMotion.day_look(CityMotionConfigData.shipped()))
	await get_tree().process_frame
	await get_tree().process_frame
	assert_eq(_drift(rig).size(), 0, "a night share change mid-play is held by the next frame: %s" % str(_drift(rig)))
