extends GutTest
## Change plan 1, wave 2, W2-A5 / W2-A6: the inner ring's plates name their segment and never overlap, every ring
## segment in the content has a word, and the tutorial teaches the free nudge and what Q / E drive.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const SEGMENT_DIR := "res://content/rings/segments"
## Longest plate (px) the ring can carry: plates sit 120 degrees apart on the plate radius.
const MAX_PLATE_W := 60.0


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
	assert_true(seen >= 7, "the segment folder lists every segment (%d)" % seen)


func test_the_three_plates_never_overlap_at_any_inner_rotation() -> void:
	var scene := await _combat()
	var view: WheelView = scene._player_view
	var w := view.combatant.wheel
	w.ring_segment_ids = [&"seg_accelerator", &"seg_corrupt", &"seg_pierce"]  # the three longest words
	var k := view.art_scale()
	var center := view._center()
	for rot in RC.TICKS:
		w.inner_rotation = rot
		var rects: Array[Rect2] = []
		for seg in RC.RING_SEGMENTS:
			var r := view.ring_plate_rect(center, k, seg)
			assert_true(r.size.x <= MAX_PLATE_W, "plate %d fits (%.0f px)" % [seg, r.size.x])
			rects.append(r)
		for i in rects.size():
			for j in range(i + 1, rects.size()):
				assert_false(rects[i].intersects(rects[j]), "plates %d and %d overlap at inner rotation %d" % [i, j, rot])


func test_the_tutorial_teaches_the_free_nudge_and_what_the_nudge_keys_drive() -> void:
	var nudge := TutorialOverlay.step_text(1)
	assert_string_contains(nudge, "FREE NUDGE")
	assert_string_contains(nudge, "costs RAM")
	assert_string_contains(nudge, "OUTER or INNER")
	assert_string_contains(nudge, Settings.key_text(&"nudge_left"))
