extends GutTest
## Plan 2 N13 view flow: a move aimed at a satellite (a nudge, or a card refused with
## CombatResolver.SATELLITE_FIXED) answers with a toast saying why; the Undock card still moves
## the satellite; a replace on an occupied slice plays through the combat scene.

const COMBAT := "res://scenes/combat/combat_scene.tscn"


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = "gut_n13_flow"
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## The combat scene running the fixture session `s`.
func _scene(s: CombatSession) -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1920, 1080)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.engine.resolver = s.resolver
	scene.engine.session = s
	scene.engine.state_changed.emit(s.state, s.last_events)
	await _frames()
	scene.skip_motion()
	return scene


func test_a_nudge_aimed_at_a_satellite_toasts_the_reason() -> void:
	var s := SatelliteFixture.session([SatelliteFixture.move_card(&"sf_nudge", RC.EffectType.NUDGE)])
	var scene := await _scene(s)
	var sat := SatelliteFixture.sat_of(s)
	s.state.target_id = sat.id
	scene._nudge_wheel_option.select(1)
	var slot := sat.dock_slot
	scene.nudge(1)
	await _frames()
	assert_true(scene.toast.visible, "the refusal shows a toast")
	assert_eq(scene.toast.label.text, CombatResolver.SATELLITE_FIXED)
	assert_eq(sat.dock_slot, slot, "the satellite stays")


func test_a_card_that_would_move_a_satellite_toasts_the_reason() -> void:
	var card := SatelliteFixture.move_card(&"sf_sat_nudge", RC.EffectType.NUDGE)
	card.wheel_target = RC.WheelTarget.SATELLITE
	var s := SatelliteFixture.session([card])
	var scene := await _scene(s)
	var sat := SatelliteFixture.sat_of(s)
	s.state.target_id = sat.id
	scene.select_card(0)
	await _frames()
	assert_true(scene.toast.visible, "the refused card shows a toast")
	assert_eq(scene.toast.label.text, CombatResolver.SATELLITE_FIXED)
	assert_eq(sat.dock_slot, SatelliteFixture.DOCK_SLOT)


func test_the_undock_card_still_moves_the_satellite() -> void:
	var s := SatelliteFixture.session([ContentRegistry.get_content(&"undock") as CardData])
	var scene := await _scene(s)
	var action := CombatAction.play_card(0, SatelliteFixture.sat_of(s).id)
	assert_eq(s.resolver.validate_action(s.state, action), "")
	assert_true(scene.engine.submit(action))
	await _frames()
	assert_eq(absi(SatelliteFixture.sat_of(s).dock_slot - SatelliteFixture.DOCK_SLOT), 1, "one slice over")
	assert_false(scene.toast.visible, "no refusal toast")


func test_a_replace_on_an_occupied_slice_plays_through() -> void:
	var template := SatelliteFixture.satellite(&"sf_new", 4)
	var s := SatelliteFixture.session([], [], null, [template])
	var scene := await _scene(s)
	var host := s.state.get_combatant(&"enemy_0")
	var old := SatelliteFixture.sat_of(s)
	var events: Array[Dictionary] = []
	var fresh := s.resolver.fx.deploy_drone(s.state, host, template, SatelliteFixture.DOCK_SLOT, events)
	scene.engine.state_changed.emit(s.state, events)
	await _frames()
	var view: WheelView = scene._enemy_views[host.id]
	var ids: Array[StringName] = []
	for sat in view.satellites:
		ids.append(sat.id)
	assert_true(ids.has(fresh.id), "the new satellite is on the wheel")
	assert_false(ids.has(old.id), "the replaced one is gone")
	assert_eq(ids.size(), 1, "one per slice")
