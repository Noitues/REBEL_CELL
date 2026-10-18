extends GutTest
## W0 TEACH (plan 2 B-TEACH follow-ups): the tutorial box never covers the THIS TURN list at
## 1280x720 and 1920x1080 (text 1.0); Next stays readable at the pulse's low point.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SIZES: Array[Vector2] = [Vector2(1280, 720), Vector2(1920, 1080)]
## Lowest alpha Next may dip to (the entry's amplitude is that alpha).
const MIN_PULSE_ALPHA := 0.75

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func test_the_tutorial_box_stands_clear_of_the_this_turn_list() -> void:
	Settings.set_text_scale(1.0)
	for sz in SIZES:
		RunManager.new_campaign(1)
		var holder: Control = add_child_autofree(Control.new())
		holder.size = sz
		var scene: Control = load(COMBAT).instantiate()
		scene.auto_start = false
		holder.add_child(scene)
		scene.start_fight(&"triage_unit", 7)
		scene.start_tutorial()
		scene.skip_motion()
		await _frames(10)
		scene.nudge(1)
		scene.nudge(-1)
		scene.play_card(0)
		scene.play_card(0)
		await _frames(12)
		var t: Control = scene.tutorial
		var q: Control = scene._queue_panel
		assert_not_null(t)
		assert_true(q.visible, "%s: the list shows" % sz)
		var tr_ := t.get_global_rect()
		var qr := q.get_global_rect()
		assert_false(tr_.intersects(qr), "%s: box %s clear of list %s" % [sz, tr_, qr])
		assert_eq(scene.layout_violations(), [] as Array[String], "%s: no layout rule broken" % sz)
		holder.queue_free()
		await _frames(2)


func test_next_never_dips_below_a_readable_alpha() -> void:
	assert_gte(Motion.amplitude(&"tutorial_next_pulse"), MIN_PULSE_ALPHA, "the pulse's low point stays readable")
