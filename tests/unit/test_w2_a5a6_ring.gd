extends GutTest
## Change plan 1, wave 2, W2-A5 / W2-A6, rebuilt for round 45 (designer-approved 2026-10-13): every ring segment in
## the content has a word and (but the blank) a wedge mark; the ghost wedge covers exactly the slice under the needle
## with the segment in effect there at every inner rotation (a partial cover too) and never on a blank; the word
## plate shows only on hover or aim; the ring takes 1 to 8 segments of any span; the tooltip names the modifier;
## every needle (Twin Pointer too, designer 2026-10-13) lights the segment it reads and gets its own wedge;
## the tutorial teaches the free nudge and what Q / E drive.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SEGMENT_DIR := "res://content/rings/segments"


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	# its own save slot: new_campaign autosaves, and a save in the default slot leaked into the title's tests
	RunManager.save_slot = "gut_w2_a5a6_ring"
	RunManager.delete_save()


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
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


func test_every_ring_segment_has_a_plate_word() -> void:
	var dir := DirAccess.open(SEGMENT_DIR)
	assert_not_null(dir, "the segment folder opens")
	var seen := 0
	for f in dir.get_files():
		if not f.ends_with(".tres"):
			continue
		var id := StringName(f.get_basename())
		seen += 1
		assert_true(WheelView.RING_WORDS.has(id), "%s has a word on its plate" % id)
		assert_true(WheelView.SEG_KINDS.has(id), "%s has a disc texture kind" % id)
		# round 45: every modifier but the blank one has a mark in the wedge and a tint
		assert_eq(RingMods.mod_id(id) == RingMods.NONE, id == &"seg_blank", "%s has a wedge mark unless blank" % id)
	assert_true(seen >= 7, "the segment folder lists every segment (%d)" % seen)


## The model's segment under the first needle (WheelMath, as the resolver reads it).
func _rule_segment(w: WheelState) -> int:
	return WheelMath.ring_segment(w.inner_tick_at(0))


func test_the_wedge_covers_exactly_the_active_segments_outer_slice_at_every_inner_rotation() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	for outer in [0, 2, 7]:
		w.rotation = outer
		for rot in RC.TICKS:
			w.inner_rotation = rot
			view.queue_redraw()
			await _frames(1)
			var seg := _rule_segment(w)
			assert_eq(view.shown_segment(), seg, "the shown segment is the rules' (outer %d, inner %d)" % [outer, rot])
			var st := view.wedge_state()
			var slot := view.active_slot()
			assert_eq(int(st["slot"]), slot, "the wedge is on the slice under the needle (inner %d)" % rot)
			assert_eq(StringName(st["seg_id"]), w.ring_segment_ids[seg], "the wedge shows the segment in effect (inner %d)" % rot)
			var mid := view.slice_deg(slot, float(outer))
			var half := w.ticks_per_slice() * WheelView.DEG_PER_TICK * 0.5
			assert_almost_eq(float(st["a_mid"]), mid, 0.001, "the wedge is centred on that slice")
			assert_almost_eq(float(st["half"]), half, 0.001, "the wedge spans that slice")
			assert_true(view.wedge.visible, "the wedge shows (inner %d)" % rot)
			assert_eq(view.wedge.seg_id, w.ring_segment_ids[seg], "the shader gets that modifier")
			# the shader's band: inside the slice (less the inset) and nothing past its edges or on its neighbours
			var mid_r := (RingMods.WEDGE_R_IN + RingMods.WEDGE_R_OUT) * 0.5
			assert_true(view.wedge.covers(mid_r, mid), "the wedge covers its slice's middle")
			assert_true(view.wedge.covers(mid_r, mid + half * 0.9), "and near its clockwise edge")
			assert_false(view.wedge.covers(mid_r, mid + half + 1.0), "but not the next slice")
			assert_false(view.wedge.covers(mid_r, mid - half - 1.0), "nor the previous one")
			assert_false(view.wedge.covers(WheelFace.R_IN - 1.0, mid), "nor the ring under it")


func test_a_partial_cover_still_puts_the_wedge_on_the_whole_slice_and_the_tooltip_says_so() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	var p0 := int(w.pointer_ticks[0])
	w.rotation = -p0
	# DOUBLE's clockwise end 1 tick past the needle: it spans 3.5 of the slice's 5 ticks (round 45's 70 %)
	w.inner_rotation = -4 - p0
	view.queue_redraw()
	await _frames(1)
	var st := view.wedge_state()
	assert_eq(StringName(st["seg_id"]), &"seg_x2", "DOUBLE is in effect")
	assert_almost_eq(float(st["cover"]), 0.7, 0.001, "it covers 70 % of the slice")
	assert_almost_eq(float(st["half"]), w.ticks_per_slice() * WheelView.DEG_PER_TICK * 0.5, 0.001, "the wedge is the whole slice")
	var tip := view._slice_label(int(st["slot"]))
	assert_string_contains(tip, "70%", "the tooltip names the partial cover")
	assert_string_contains(tip, view.plate_words(&"seg_x2"), "the tooltip names the modifier")
	assert_string_contains(tip, view.plate_words(&"seg_pierce"), "and the segment a clockwise turn brings next")
	# a whole cover says nothing about it; another slice says nothing about the ring
	w.inner_rotation = -p0
	view.queue_redraw()
	await _frames(1)
	st = view.wedge_state()
	assert_almost_eq(float(st["cover"]), 1.0, 0.001, "centred, DOUBLE covers the whole slice")
	assert_false(view._slice_label(int(st["slot"])).contains("Covers"), "no cover line on a whole cover")
	assert_false(view._slice_label((int(st["slot"]) + 2) % w.slice_count).contains(view.plate_words(&"seg_x2")),
		"a slice off the needle names no ring modifier")


func test_no_wedge_on_a_blank_segment() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_blank", &"seg_pierce", &"seg_blank"]
	for rot in RC.TICKS:
		w.inner_rotation = rot
		view.queue_redraw()
		await _frames(1)
		var blank := w.ring_segment_ids[_rule_segment(w)] == &"seg_blank"
		assert_eq(view.wedge_state().is_empty(), blank, "a wedge only off blank (inner %d)" % rot)
		assert_eq(view.wedge.visible, not blank, "the wedge node hides on blank (inner %d)" % rot)
		assert_true(view.ring_tip(view.active_slot()) == "" if blank else view.ring_tip(view.active_slot()) != "",
			"the tooltip's ring lines follow the wedge (inner %d)" % rot)


func test_the_word_plate_shows_only_on_hover_or_aim() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	w.inner_rotation = 0
	view.hover_zone = {}
	view.queue_redraw()
	await _frames(1)
	assert_false(view.word_plate_shown(), "no words at rest")
	assert_false(view.word_plate_rect().has_area(), "no plate at rest")
	# the mouse on the wedge (the slice under the needle)
	var spot := view.global_position + WheelFace.at(view._center(), view.art_scale(), WheelFace.READ_R, float(view.wedge_state()["a_mid"]))
	var move := InputEventMouseMotion.new()
	move.global_position = spot
	move.position = spot - view.global_position
	view._gui_input(move)
	assert_true(view.word_plate_shown(), "the mouse on the wedge shows its plate")
	var rect := view.word_plate_rect()
	assert_true(rect.has_area(), "the plate has a place")
	assert_true(get_viewport().get_visible_rect().has_point(view.global_position + rect.end - Vector2.ONE), "the plate stays on screen")
	# the mouse on another slice hides it
	var other := view.global_position + WheelFace.at(view._center(), view.art_scale(), WheelFace.READ_R, float(view.wedge_state()["a_mid"]) + 180.0)
	move.global_position = other
	move.position = other - view.global_position
	view._gui_input(move)
	assert_false(view.word_plate_shown(), "off the wedge, no plate")
	# aiming at the wheel shows it
	view.hover_zone = {"kind": "slot", "slot": (view.active_slot() + 3) % w.slice_count}
	assert_true(view.word_plate_shown(), "aiming at the wheel shows its plate")
	view.hover_zone = {}
	# a blank segment under the needle: no plate even when aimed at
	w.ring_segment_ids = [&"seg_blank", &"seg_blank", &"seg_blank"]
	view.hover_zone = {"kind": "hub"}
	view.queue_redraw()
	await _frames(1)
	assert_false(view.word_plate_shown(), "no plate without a modifier")
	view.hover_zone = {}


func test_the_ring_renders_one_to_eight_segments_of_any_span() -> void:
	var kinds := WheelView.SEG_KINDS
	var ids: Array[StringName] = [&"seg_x2", &"seg_pierce", &"seg_corrupt", &"seg_anchor", &"seg_accelerator", &"seg_echo", &"seg_blank", &"seg_x2"]
	var spans := [37.0, 90.0, 11.0, 64.0, 23.0, 45.0, 30.0, 60.0]
	for n in range(1, WheelDisc.MAX_SEGMENTS + 1):
		# n segments of uneven spans that close the circle, from an arbitrary start
		var total := 0.0
		for i in n:
			total += spans[i]
		var segs: Array[Dictionary] = []
		var a := 17.0 * n
		for i in n:
			var sp: float = spans[i] * 360.0 / total
			segs.append({"id": ids[i], "a0": a, "a1": a + sp})
			a += sp
		var p := WheelDisc.ring_params(segs, kinds)
		assert_eq(int(p[&"seg_n"]), n, "%d segments go to the shader" % n)
		assert_eq((p[&"seg_a0"] as PackedFloat32Array).size(), WheelDisc.MAX_SEGMENTS, "the arrays are padded")
		for i in n:
			var s: Dictionary = segs[i]
			var mid := (float(s["a0"]) + float(s["a1"])) * 0.5
			assert_eq(WheelDisc.segment_at(mid, p), i, "%d segments: the middle of %d is %d" % [n, i, i])
			assert_eq(WheelDisc.segment_at(float(s["a0"]) + 0.01, p), i, "%d segments: %d starts at its a0" % [n, i])
			assert_eq(WheelDisc.segment_at(fposmod(float(s["a1"]) - 0.01, 360.0), p), i, "%d segments: %d ends at its a1" % [n, i])
			var tint: Color = (p[&"seg_tint"] as PackedColorArray)[i]
			assert_eq(tint.a > 0.0, ids[i] != &"seg_blank", "%d segments: %d's notch tint" % [n, i])
		# a gap in the ring (one segment short of the circle) reads as no segment
		var gap := WheelDisc.ring_params(segs.slice(0, n - 1), kinds) if n > 1 else WheelDisc.ring_params([] as Array[Dictionary], kinds)
		var last: Dictionary = segs[n - 1]
		assert_eq(WheelDisc.segment_at((float(last["a0"]) + float(last["a1"])) * 0.5, gap), -1, "%d segments: a gap is empty" % n)
	# the disc takes them
	var disc := WheelDisc.new()
	var three: Array[Dictionary] = [{"id": &"seg_x2", "a0": 0.0, "a1": 200.0}, {"id": &"seg_blank", "a0": 200.0, "a1": 360.0}]
	disc.set_ring(three, [1] as Array[int], 30.0, kinds)
	assert_eq(int(disc.mat.get_shader_parameter(&"seg_n")), 2, "the disc gets the segments")
	assert_eq(int(disc.mat.get_shader_parameter(&"seg_lit")), 2, "and the one in effect")
	disc.set_ring(three, [0, 1, 1, 5] as Array[int], 30.0, kinds)
	assert_eq(int(disc.mat.get_shader_parameter(&"seg_lit")), 3, "two needles light two segments (past the ring dropped)")
	disc.free()


func test_the_view_hands_the_disc_its_ring_and_the_standing_plates_are_gone() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	for rot in [0, 5, 13, 29]:
		w.inner_rotation = rot
		view.queue_redraw()
		await _frames(1)
		var p := WheelDisc.ring_params(view.ring_segments(), WheelView.SEG_KINDS)
		var needle := fposmod(-view.shown_pointers()[0] * WheelView.DEG_PER_TICK, 360.0)
		var ring_frame := fposmod(needle - rot * WheelView.DEG_PER_TICK, 360.0)
		# the disc's segment under the needle is the rules' one (away from a groove)
		if absf(fposmod(ring_frame + 60.0, 120.0) - 60.0) < 59.0:
			assert_eq(WheelDisc.segment_at(ring_frame, p), _rule_segment(w), "the disc draws the rules' segment under the needle (inner %d)" % rot)
		assert_eq(int(view.disc.mat.get_shader_parameter(&"seg_lit")), 1 << _rule_segment(w), "the raised plate is the segment in effect (inner %d)" % rot)
	assert_false(view.has_method("ring_plate_rect"), "A6's standing plates are gone")


func test_every_needle_lights_its_segment_and_gets_its_own_wedge() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_x2", &"seg_pierce", &"seg_corrupt"]
	var p0 := int(w.pointer_ticks[0])
	for pointers in [PackedInt32Array([p0]), PackedInt32Array([p0, p0 + 15]), PackedInt32Array([p0, p0 + 7])]:
		w.pointer_ticks = pointers
		for rot in RC.TICKS:
			w.inner_rotation = rot
			view.queue_redraw()
			await _frames(1)
			var mask := 0
			for k in pointers.size():
				var seg := WheelMath.ring_segment(w.inner_tick_at(k))
				mask |= 1 << seg
				assert_eq(view.shown_segment(k), seg, "needle %d reads the rules' segment (%d needles, inner %d)" % [k, pointers.size(), rot])
				var st := view.wedge_state(k)
				var slot := w.slice_at(k)
				assert_eq(int(st["slot"]), slot, "needle %d's wedge is on its own slice" % k)
				assert_eq(StringName(st["seg_id"]), w.ring_segment_ids[seg], "needle %d's wedge shows its segment" % k)
				assert_true(view.wedges[k].visible, "needle %d's wedge shows" % k)
				assert_eq(view.wedges[k].seg_id, w.ring_segment_ids[seg], "needle %d's shader gets its modifier" % k)
				assert_eq(view.wedge_pointer_at(slot), k, "the slice under needle %d is its wedge's" % k)
				assert_string_contains(view.ring_tip(slot), view.plate_words(w.ring_segment_ids[seg]), "the tooltip names needle %d's modifier" % k)
			assert_eq(int(view.disc.mat.get_shader_parameter(&"seg_lit")), mask, "every needle's segment is raised (inner %d)" % rot)
			for k in range(pointers.size(), WheelView.WEDGE_MAX):
				assert_false(view.wedges[k].visible, "no wedge without needle %d" % k)
	# two needles: aiming shows both plates; hovering one wedge shows only its own
	w.pointer_ticks = PackedInt32Array([p0, p0 + 15])
	w.inner_rotation = 0
	view.hover_zone = {"kind": "hub"}
	view.queue_redraw()
	await _frames(1)
	assert_eq(view.word_plate_pointers(), [0, 1] as Array[int], "aiming shows a plate per wedge")
	assert_false(view.word_plate_rect(0).intersects(view.word_plate_rect(1)), "the two plates keep apart")
	view.hover_zone = {}
	view._wedge_hot = 1
	assert_eq(view.word_plate_pointers(), [1] as Array[int], "hovering the second wedge shows its plate alone")
	view._wedge_hot = -1
	w.pointer_ticks = PackedInt32Array([p0])


func test_the_tutorial_teaches_the_free_nudge_and_what_the_nudge_keys_drive() -> void:
	var nudge := TutorialOverlay.step_text(1)
	assert_string_contains(nudge, "FREE NUDGE")
	assert_string_contains(nudge, "costs RAM")
	assert_string_contains(nudge, "OUTER or INNER")
	assert_string_contains(nudge, Settings.key_text(&"nudge_left"))
