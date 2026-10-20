extends GutTest
## Plan 2 EV-02 hosts, the screen's one flow test: a hub event (kind "event") shows on the netrun scene's
## existing event page, a choice resolves through the session, and the end of the event goes back to the HQ
## (no run-end page).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Vector2(1280, 720)

var _requested: Array[String] = []


func _on_scene_requested(path: String) -> void:
	_requested.append(path)


func before_each() -> void:
	_requested = []
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_ev02_flow"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()
	SignalBus.scene_change_requested.connect(_on_scene_requested)


func after_each() -> void:
	SignalBus.scene_change_requested.disconnect(_on_scene_requested)
	CityBakeCache.shutdown()
	Fx._set_jacking(false)
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func test_a_hub_event_shows_on_the_event_page_and_ends_at_the_hq() -> void:
	RunManager.new_campaign(1)
	RunManager.campaign.venue_event_due = TerminalEventData.Venue.HQ_VIEW
	var s := RunManager.start_venue_event()
	assert_not_null(s)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(2)
	scene._show_current()
	PageTransition.settle(scene)
	await _frames(4)
	assert_not_null(scene._panel.find_child("EventPanel", true, false), "the existing event page")
	var ev := s.current_event()
	assert_eq(ev.id, &"ev_hq_dead_letter_crate")
	for i in ev.choices.size():
		assert_not_null(scene._panel.find_child("Choice%d" % (i + 1), true, false), "choice %d is on the page" % (i + 1))
	assert_eq(_requested, [], "the page stays until a choice is made")
	scene.choose_event(2)  # leave it on the loading dock
	await _frames(4)
	assert_true(s.run.is_over())
	assert_true(_requested.has(RunManager.HQ_SCENE), "back to the HQ, no run-end page")
	holder.queue_free()
	await _frames(1)
