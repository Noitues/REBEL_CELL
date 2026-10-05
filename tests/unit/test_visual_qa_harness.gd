extends GutTest
## ART-0 D: the review-pack harness (tools/visual_qa/review_pack.gd, ported from art-pass
## W10 / W9F) stays reachable headless: it compiles against main's scripts, every listed
## screen has its method, names are unique, and the accessibility axes are gated on the
## Settings properties existing (ART-0 C ports them), so the harness works before and after.
## No screen is captured here (that needs a renderer: tools/visual_qa/capture_pack.py).

const HARNESS := "res://tools/visual_qa/review_pack.gd"


func _harness() -> GDScript:
	var s := load(HARNESS) as GDScript
	assert_not_null(s, "%s loads" % HARNESS)
	return s


func test_harness_compiles_and_every_screen_has_its_method() -> void:
	var s := _harness()
	assert_true(s.can_instantiate(), "the harness compiles against main's scripts")
	var n: Node = s.new()
	var names := {}
	for row in s.get_script_constant_map()["SCREENS"]:
		var screen: String = row[0]
		assert_false(names.has(screen), "screen %s is listed once" % screen)
		names[screen] = true
		assert_true(n.has_method(row[1]), "screen %s has its method %s" % [screen, row[1]])
		assert_ne(String(row[2]), "", "screen %s says what it shows" % screen)
	assert_gt(names.size(), 40, "the harness covers main's screens")
	n.free()


func test_settings_axes_are_gated_on_the_setting_existing() -> void:
	var s := _harness()
	var axes: Dictionary = s.call(&"settings_axes")
	for name in s.get_script_constant_map()["AXIS_SETTINGS"]:
		assert_true(axes.has(String(name)), "axis %s is reported" % name)
		assert_eq(axes[String(name)], name in Settings, "axis %s is on only when Settings has it" % name)
