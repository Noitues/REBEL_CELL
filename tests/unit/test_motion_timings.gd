extends GutTest
## MOTION-TIMINGS: the combat effects' inline fractions (CombatFxLayer, WheelView) live in
## `ui_motion.tres` as shares (amplitude), each a required, always-on id; the computed
## seconds equal the old inline expressions.

## id -> the literal it replaced.
const OLD: Dictionary = {
	&"hit_blocked_wall_lead": 0.25, &"wall_stagger_share": 0.5, &"wall_travel_share": 0.6,
	&"corrupt_apply_stagger": 0.2, &"corrupt_apply_travel": 0.3, &"corrupt_tick_free_share": 0.5,
	&"drone_destroyed_stagger": 0.1, &"drone_destroyed_travel": 0.8, &"nudge_resist_stagger": 0.3,
	&"nudge_resist_travel": 0.7, &"trigger_lens_share": 0.4, &"trigger_bits_lead": 0.15,
	&"temp_label_stagger": 0.4, &"temp_label_travel": 0.6, &"defeat_shock_share": 0.5,
	&"defeat_bits_stagger": 0.5, &"defeat_bits_travel": 0.45, &"defeat_word_lead": 0.3,
	&"precision_word_hold": 0.62,
}
const SOURCES: Array[String] = ["res://scripts/ui/kit/combat_fx_layer.gd", "res://scripts/ui/wheel_view.gd"]


func test_every_moved_share_is_required_always_on_and_equal_to_the_old_literal() -> void:
	for id: StringName in OLD:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(UiMotionData.ALWAYS_ON.has(id), "%s is a tuning (never switched off)" % id)
		assert_true(Motion.has(id), "%s is in the table" % id)
		assert_almost_eq(Motion.amplitude(id), float(OLD[id]), 0.000001, "%s keeps its old value" % id)


func test_computed_durations_equal_the_old_expressions_within_a_millisecond() -> void:
	for secs: float in [0.1, 0.35, 0.5, 0.8]:
		assert_almost_eq(secs * Motion.amplitude(&"defeat_bits_travel"), secs * 0.45, 0.001)
		assert_almost_eq(secs * Motion.amplitude(&"drone_destroyed_travel"), secs * 0.8, 0.001)
		assert_almost_eq(secs * Motion.amplitude(&"hit_blocked_wall_lead"), secs * 0.25, 0.001)


func test_no_inline_fraction_of_a_duration_remains() -> void:
	var re := RegEx.new()
	re.compile("\\b(dur|secs|delay)\\s*\\*\\s*0\\.\\d")
	for path in SOURCES:
		var f := FileAccess.open(path, FileAccess.READ)
		assert_not_null(f, path)
		if f == null:
			continue
		var n := 0
		for line in f.get_as_text().split("\n"):
			if re.search(line) != null:
				n += 1
				gut.p("%s: %s" % [path, line.strip_edges()])
		assert_eq(n, 0, "%s has no inline duration fraction" % path)


func test_a_share_is_unchanged_with_reduce_effects_on() -> void:
	var was := Settings.reduce_effects
	Settings.reduce_effects = true
	assert_almost_eq(Motion.amplitude(&"defeat_bits_travel"), 0.45, 0.000001, "a share does not depend on the switch")
	Settings.reduce_effects = was
