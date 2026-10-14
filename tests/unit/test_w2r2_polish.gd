extends GutTest
## Plan 1 wave 2 review R2 polish: the keyline rule for ring modifiers (dark tint or thin stroke gets the ink
## keyline), the word plate keeping clear of the needle tags, the precision tags and the HP gauge (one and two
## needles, a needle at the bottom included), and the cream clockwise end cap of a partly covered segment.

const COMBAT := "res://scenes/combat/combat_scene.tscn"


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _combat() -> Control:
	RunManager.new_campaign(1)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.start_fight(&"collections_agent", 5)
	await _frames()
	return scene


func test_any_dark_or_thin_modifier_gets_the_keyline() -> void:
	for id in RingMods.MODS:
		var m: Dictionary = RingMods.MODS[id]
		var k := RingMods.keyline_of(id)
		var dark := RingMods.luminance(m["tint"]) < RingMods.KEYLINE_LUM_MIN
		var thin := float(m["stroke"]) * RingMods.PX_PER_UNIT_1_0 < RingMods.KEYLINE_STROKE_MIN_PX
		if dark or thin:
			assert_true(k >= RingMods.KEYLINE_W, "%s (dark %s, thin %s) wears the keyline" % [id, dark, thin])
		assert_true(k >= float(m["keyline"]), "%s keeps at least its declared keyline" % id)
	# a future modifier is covered by the rule, not by its table row
	var dim := {"tint": Color(0.3, 0.1, 0.4), "stroke": 20.0, "keyline": 0.0}
	var fine := {"tint": Color(1, 1, 1), "stroke": 20.0, "keyline": 0.0}
	var fine_thin := {"tint": Color(1, 1, 1), "stroke": 3.0, "keyline": 0.0}
	assert_eq(RingMods.keyline_for(dim), RingMods.KEYLINE_W, "a dark tint gets it")
	assert_eq(RingMods.keyline_for(fine), 0.0, "a bright thick mark does not")
	assert_eq(RingMods.keyline_for(fine_thin), RingMods.KEYLINE_W, "a thin stroke gets it")
	# the three marks the designer named, at the PIERCE size ratio, keyline 2 at 38 %
	for id in [&"seg_anchor", &"seg_accelerator", &"seg_echo"]:
		assert_eq(float(RingMods.of(id)["size"]), 80.0, "%s is 1.4x (57 -> 80)" % id)
		assert_eq(RingMods.keyline_of(id), 2.0, "%s wears a 2 px keyline" % id)
	assert_eq(RingMods.keyline_of(&"seg_pierce"), 2.0, "PIERCE keeps its keyline")
	assert_eq(RingMods.keyline_of(&"seg_blank"), 0.0, "no modifier, no keyline")


func _clear_of_everything(view: WheelView, rect: Rect2) -> bool:
	for obstacle in view._plate_obstacles():
		if rect.intersects(obstacle):
			return false
	return true


func test_the_word_plate_keeps_clear_of_tags_and_the_hp_gauge() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	var p0 := int(w.pointer_ticks[0])
	var checked := 0
	for pointers in [PackedInt32Array([p0]), PackedInt32Array([p0, p0 + 15])]:
		for off in RC.TICKS:
			w.pointer_ticks = PackedInt32Array([int(pointers[0]) + off] if pointers.size() == 1 else [int(pointers[0]) + off, int(pointers[1]) + off])
			w.inner_rotation = 0
			view.hover_zone = {"kind": "hub"}
			view.queue_redraw()
			await _frames(1)
			for i in view.word_plate_pointers():
				var rect := view.word_plate_rect(i)
				checked += 1
				assert_true(_clear_of_everything(view, rect), "plate of needle %d clear of tags and gauge (%d needles, shift %d)" % [i, pointers.size(), off])
	assert_true(checked > 0, "plates were checked")
	# the bottom needle (180 degrees): one needle and two
	var bottom := int(roundf(-180.0 / WheelView.DEG_PER_TICK))
	for set in [PackedInt32Array([bottom]), PackedInt32Array([bottom, bottom + 15])]:
		w.pointer_ticks = set
		view.hover_zone = {"kind": "hub"}
		view.queue_redraw()
		await _frames(1)
		var rects: Array[Rect2] = []
		for i in view.word_plate_pointers():
			rects.append(view.word_plate_rect(i))
			assert_true(_clear_of_everything(view, rects[-1]), "bottom case: plate %d clear (%d needles)" % [i, set.size()])
		if rects.size() == 2:
			assert_false(rects[0].intersects(rects[1]), "bottom case: the two plates keep apart")
	w.pointer_ticks = PackedInt32Array([p0])
	view.hover_zone = {}


func test_a_partial_cover_draws_the_clockwise_end_cap_cream() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	var p0 := int(w.pointer_ticks[0])
	w.rotation = -p0
	w.inner_rotation = -4 - p0
	view.queue_redraw()
	await _frames(1)
	assert_almost_eq(float(view.wedge_state()["cover"]), 0.7, 0.001, "70 % cover")
	assert_eq(int(view.disc.mat.get_shader_parameter(&"seg_partial")), 1 << int(view.wedge_state()["seg"]), "the partly covered segment is marked")
	assert_eq(float(view.disc.mat.get_shader_parameter(&"seg_cap_partial_w")), 3.0, "cream cap 3 wide")
	w.inner_rotation = -p0
	view.queue_redraw()
	await _frames(1)
	assert_eq(int(view.disc.mat.get_shader_parameter(&"seg_partial")), 0, "a whole cover marks nothing")
