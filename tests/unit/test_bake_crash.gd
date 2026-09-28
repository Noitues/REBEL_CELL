extends GutTest
## Animation pass, bake crash (DECISIONS "Animation pass - bake crash"): a view freed during
## the tree's process_frame emission must not leave a callback that emission still calls.
## A GDScript lambda using self holds a raw pointer to its object; a one-shot connection is
## dropped from the object's list before the emission calls it, so the object's destructor
## cannot disconnect it, and the emission then read freed memory (signal 11 in the suite,
## right after test_anim_r2_city's route/raid test freed its HQ). Method callables hold the
## object's id and are skipped once it is gone.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
## Fresh overlays made where the freed one lay (a reused block is what the old lambda ran on).
const CHURN := 64
## Scene open / free cycles in the stress test.
const CYCLES := 6


func before_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_bake_crash"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.simulate = false
	CityBakeCache.shutdown()
	Motion.use_config(null)
	Fx._set_jacking(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


## Asks `overlay` for a node and label redraw that must wait for the next frame (its layers
## drew this frame): called deferred, so its process_frame slot comes after the test's own.
func _ask_later(overlay: CityMapOverlay) -> void:
	if not is_instance_valid(overlay):
		return
	overlay._top_frame = Engine.get_process_frames()
	overlay._tags_frame = Engine.get_process_frames()
	overlay._queue_top()


func test_an_overlay_freed_mid_frame_leaves_no_callback_behind() -> void:
	var hits := 0
	for round in 8:
		var holder := Control.new()
		add_child(holder)
		var overlay := CityMapOverlay.new()
		holder.add_child(overlay)
		await get_tree().process_frame
		_ask_later.call_deferred(overlay)
		await get_tree().process_frame
		# Resumed inside process_frame's emission, ahead of the overlay's slot (connected after
		# this await's): its redraw still waits. Free it now, as GUT's autofree does.
		assert_true(overlay._top_later and overlay._tags_later, "round %d: the redraw waits for this frame's emission" % round)
		holder.free()
		var fresh: Array[CityMapOverlay] = []
		for k in CHURN:
			var o := CityMapOverlay.new()
			o._top_later = true
			o._tags_later = true
			fresh.append(o)
		await get_tree().process_frame
		for o in fresh:
			if not o._top_later or not o._tags_later:
				hits += 1
			o.free()
	assert_eq(hits, 0, "a freed overlay's deferred redraw never runs on another object")


func test_the_map_scenes_open_and_free_mid_frame_repeatedly() -> void:
	# The test_anim_r2_city route / raid setup case, over and over: both maps drawn, then freed
	# with free() inside a process_frame emission (as GUT's autofree does).
	CityBakeCache.simulate = true
	for k in CYCLES:
		var holder := Control.new()
		holder.size = SCREEN.size
		add_child(holder)
		var nr: Control = load(NETRUN).instantiate()
		holder.add_child(nr)
		nr.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		await get_tree().process_frame
		nr.new_campaign(1)
		nr.start_run(1)
		await get_tree().process_frame
		var hq: Control = load(HQ).instantiate()
		holder.add_child(hq)
		hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		await get_tree().process_frame
		hq.new_campaign(1)
		hq.show_grid()
		await get_tree().process_frame
		assert_true(hq.city_overlay.nodes.size() > 0, "cycle %d: the Grid is drawn" % k)
		var c := RunManager.campaign
		c.schematics = 100
		var first: StringName = RunManager.corporation.city_grid.get_site(c.grid.home_site_id).links[0]
		CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
		CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
		hq.show_raid()
		await get_tree().process_frame
		holder.free()
		CityBakeCache.shutdown()
	await get_tree().process_frame
	assert_eq(CityBakeCache.busy(), 0, "nothing left running")
