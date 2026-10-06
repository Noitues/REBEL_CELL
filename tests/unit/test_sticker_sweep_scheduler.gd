extends GutTest
## M14 B1d (designer 2026-10-06, art-pass review D22): the rainbow gloss sweep is a scheduler's: one sweep at
## a time on the screen's primary verb sticker, every 4 to 6 s (seeded period from the `sticker_sweep_period`
## entry); focus and hover show only the peel-back. Reduce effects: no sweep; MotionSkip ends a running one.

var _saved: Dictionary
var _live: bool = false


func before_each() -> void:
	_saved = Settings.to_dict()
	_live = Motion.force_live
	Motion.force_live = true
	StickerSweepQueue.reset()


func after_each() -> void:
	Settings.restore(_saved)
	Motion.force_live = _live
	StickerSweepQueue.reset()


func _vinyl(text: String, fill: int = VinylSticker.Fill.WHITE) -> VinylSticker:
	var v := VinylSticker.new()
	v.shape = VinylSticker.Shape.WORD
	v.text = text
	v.fill = fill
	v.ambient_sweep = true
	add_child_autofree(v)
	return v


func test_only_the_primary_sticker_sweeps_named_then_pink_then_first() -> void:
	var a := _vinyl("A")
	var pink := _vinyl("B", VinylSticker.Fill.PINK)
	var c := _vinyl("C")
	assert_eq(StickerSweepQueue.primary(), pink, "the first pink verb is the default primary")
	assert_false(StickerSweepQueue.take_turn(a, 0))
	assert_false(StickerSweepQueue.take_turn(c, 0))
	c.sweep_primary = true
	assert_eq(StickerSweepQueue.primary(), c, "a named primary wins")
	c.visible = false
	assert_eq(StickerSweepQueue.primary(), pink, "a hidden sticker (another screen) does not take part")
	pink.visible = false
	assert_eq(StickerSweepQueue.primary(), a, "else the first to join")


func test_at_most_one_sweep_runs_at_a_time() -> void:
	var a := _vinyl("A", VinylSticker.Fill.PINK)
	var b := _vinyl("B", VinylSticker.Fill.PINK)
	assert_true(StickerSweepQueue.take_turn(a, 0))
	assert_eq(StickerSweepQueue.sweeping(), a.get_instance_id())
	assert_false(StickerSweepQueue.take_turn(b, 0), "never two at once")
	assert_false(StickerSweepQueue.take_turn(a, 0), "not twice either")
	assert_gt(a.sweep(), 0.0)
	var running := 0
	for v: VinylSticker in [a, b]:
		if v.sweep_running():
			running += 1
	assert_eq(running, 1)
	assert_eq(a.rainbow, 1.0, "the sweep is the rainbow one")
	assert_false(b.sweep_running())


func test_the_period_is_four_to_six_seconds_from_the_config() -> void:
	var lo := Motion.delay_of(StickerSweepQueue.PERIOD)
	var hi := Motion.seconds(StickerSweepQueue.PERIOD)
	assert_between(lo, 4.0 / maxf(Motion.speed, 0.01) - 0.001, 6.0, "the entry's shortest period")
	assert_lte(hi, 6.0 / maxf(Motion.speed, 0.01) + 0.001)
	var first := StickerSweepQueue.next_period()
	for i in 200:
		var p := StickerSweepQueue.next_period()
		assert_between(p, lo - 0.0001, hi + 0.0001, "period %d inside the range" % i)
	# Seeded, never global: the same seed gives the same cycle.
	StickerSweepQueue.reset()
	assert_eq(StickerSweepQueue.next_period(), first, "same seed, same first period")


func test_the_next_sweep_comes_one_period_after_the_start() -> void:
	var a := _vinyl("A", VinylSticker.Fill.PINK)
	assert_true(StickerSweepQueue.take_turn(a, 1000))
	StickerSweepQueue.done(a, 2400, 1.4)
	assert_false(StickerSweepQueue.take_turn(a, 2400 + 2000), "not before the 4 s mark")
	assert_true(StickerSweepQueue.take_turn(a, 1000 + 6000 + 1), "by the 6 s mark")


func test_focus_and_hover_are_the_peel_back_with_no_rainbow_and_no_sweep() -> void:
	var v := _vinyl("GO", VinylSticker.Fill.PINK)
	v.set_state(VinylSticker.State.HOVER)
	v.complete_motion()
	assert_gte(v.fold, VinylSticker.HOVER_CURL, "the corner curls")
	assert_gt(v.lift, 0.0, "and lifts")
	assert_eq(v.rainbow, 0.0)
	assert_false(v.sweep_running())
	assert_eq(StickerSweepQueue.sweeping(), 0, "focus does not take the sweep's turn")


func test_reduce_effects_has_no_sweep() -> void:
	Settings.set_reduce_effects(true)
	var v := _vinyl("GO", VinylSticker.Fill.PINK)
	assert_true(StickerSweepQueue.take_turn(v, 0))
	assert_eq(v.sweep(), 0.0, "no sweep")
	assert_eq(v.rainbow, 0.0)
	assert_eq(v.gloss_k, VinylSticker.GLOSS_REST, "the rest gloss stands as the static sheen")
	assert_eq(StickerSweepQueue.sweeping(), 0, "the turn is handed back")


func test_motion_skip_completes_a_running_sweep() -> void:
	var v := _vinyl("GO", VinylSticker.Fill.PINK)
	assert_true(StickerSweepQueue.take_turn(v, 0))
	assert_gt(v.sweep(), 0.0)
	assert_true(v.motion_running())
	v.complete_motion()
	assert_false(v.motion_running())
	assert_eq(v.rainbow, 0.0)
	assert_eq(v.gloss_k, VinylSticker.GLOSS_REST)
	assert_eq(StickerSweepQueue.sweeping(), 0)


func test_the_drawn_verb_sticker_sweeps_by_the_queue_and_focus_is_only_the_curl() -> void:
	var drawn := VerbSticker.new("OVERTHROW", VerbSticker.Fill.BLUE, 40.0)
	add_child_autofree(drawn)
	var kit := VerbSticker.new("RESUME", VerbSticker.Fill.PINK, 34.0)
	add_child_autofree(kit)
	await get_tree().process_frame
	assert_eq(StickerSweepQueue.primary(), kit.vinyl, "the pink kit verb is the screen's primary")
	drawn.grab_focus()
	await get_tree().process_frame
	assert_ne(drawn._mat.get_shader_parameter(&"rainbow"), 1.0, "focus: no rainbow")
	assert_true(bool(drawn.get("_focused")), "focus: the curl")
	assert_false(drawn.sweep_running(), "no sweep on focus")
	kit.vinyl.complete_motion()  # (the queue may already have started the pink verb's sweep)
	kit.sweep_primary = false
	drawn.sweep_primary = true
	assert_eq(StickerSweepQueue.primary(), drawn, "named primary on a drawn sticker")
	assert_true(StickerSweepQueue.take_turn(drawn, 1 << 40))
	assert_gt(drawn.run_sweep(), 0.0)
	assert_eq(drawn._mat.get_shader_parameter(&"rainbow"), 1.0, "the scheduled sweep is the rainbow")
	drawn.complete_motion()
	assert_eq(drawn._mat.get_shader_parameter(&"rainbow"), 0.0)
	assert_eq(StickerSweepQueue.sweeping(), 0)
