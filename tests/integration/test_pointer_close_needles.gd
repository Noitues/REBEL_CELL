extends GutTest
## Plan 2 N11 (ruling Q27: needles may stand 1 tick apart and each shows): on the combat
## screen, two needles 1 tick apart both wear a tag; the tags never overlap and their centres
## stay at least 24 px apart, at 1920x1080 and 1280x720, text scale 1.0. Flow test only.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const MIN_APART := 24.0


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.save_slot = "gut_n11_needles"
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


func _check_screen(screen: Vector2) -> void:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = screen
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames()
	var st: CombatState = scene.engine.state()
	var e: CombatantState = st.enemies[0]
	var views: Array = [[scene._enemy_views[e.id], e], [scene._player_view, st.player]]
	for pair in views:
		var view: WheelView = pair[0]
		var c: CombatantState = pair[1]
		view.intent = {}
		for first in [0, 7, 14, 22, 29]:
			c.wheel.pointer_ticks = PackedInt32Array([first, (first + 1) % RC.TICKS])
			view.show_combatant(c, st.satellites_of(c.id), scene.engine.readouts(c), view.lookup)
			assert_eq(view.pointer_tag_model().size(), 2, "%s: both needles wear a tag" % screen)
			var a := view.pointer_tag_rect(0)
			var b := view.pointer_tag_rect(1)
			assert_true(a.has_area() and b.has_area(), "%s ticks %d/%d: both tags drawn" % [screen, first, first + 1])
			assert_false(a.intersects(b), "%s ticks %d/%d: tags do not overlap" % [screen, first, first + 1])
			assert_gte(a.get_center().distance_to(b.get_center()), MIN_APART, "%s ticks %d/%d: tags %d px apart" % [screen, first, first + 1, MIN_APART])
	scene.get_parent().queue_free()
	await _frames(2)


func test_adjacent_needles_keep_separate_tags_at_1080p() -> void:
	await _check_screen(Vector2(1920, 1080))


func test_adjacent_needles_keep_separate_tags_at_720p() -> void:
	await _check_screen(Vector2(1280, 720))
