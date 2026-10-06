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
	assert_eq(v.peel_back, 1.0, "the corner curls")
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
	assert_almost_eq(float(drawn._mat.get_shader_parameter(&"rainbow")), 0.55, 0.001, "the scheduled sweep is the band, additive 0.55")
	drawn.complete_motion()
	assert_eq(drawn._mat.get_shader_parameter(&"rainbow"), 0.0)
	assert_eq(StickerSweepQueue.sweeping(), 0)


func test_the_sweep_is_one_narrow_45_degree_band_from_config() -> void:
	var e := Motion.entry(&"sticker_gloss_sweep")
	assert_between(e.delay, 0.20, 0.25, "the band is 20 to 25 % of the sticker's width")
	assert_almost_eq(e.amplitude, 0.55, 0.001, "additive about 0.55")
	assert_between(e.duration, 0.8, 1.0, "crossing in about 0.9 s")
	assert_eq(VinylSticker.SWEEP_BAND_DEG, 45.0, "a diagonal")
	var v := _vinyl("RESUME", VinylSticker.Fill.PINK)
	assert_gt(v.sweep(), 0.0)
	assert_eq(v.band_share(), e.delay)
	assert_eq(v._mat.get_shader_parameter(&"band_deg"), 45.0)
	assert_almost_eq(float(v._mat.get_shader_parameter(&"band_alpha")), 0.55, 0.001)
	assert_eq(v.gloss_k, VinylSticker.GLOSS_REST, "the rest of the sticker keeps its gloss: no flood")


func test_the_peel_back_fold_is_fixed_in_px_and_scales_with_the_text_size() -> void:
	Settings.set_text_scale(1.0)
	var screen_h := 1080.0
	assert_almost_eq(VinylSticker.peel_leg(600.0, screen_h), 34.0, 0.01, "34 px at 1080p")
	assert_almost_eq(VinylSticker.peel_leg(100.0, screen_h), 24.0, 0.01, "24 px on short words")
	Settings.set_text_scale(1.6)
	assert_almost_eq(VinylSticker.peel_leg(960.0, screen_h), 54.4, 0.1, "about 54 px at 1.6")
	var v := _vinyl("OPTIONS")
	v.set_state(VinylSticker.State.HOVER)
	v.complete_motion()
	assert_gt(v.peel_px(), 10.0, "the sticker's own fold is not a few px")
	assert_eq(float(v._mat.get_shader_parameter(&"peel_px")), v.peel_px())


func test_every_destructive_and_quit_confirm_is_calm() -> void:
	# slot DELETE (title_scene builds exactly this AbandonDialog), abandon run, abandon campaign, quit (ExitDialogs)
	var builders: Dictionary = {
		"slot delete": func() -> ConfirmDialog:
			return AbandonDialog.new("Delete the campaign in slot 1?", "DELETE", "DELETE SLOT", "Lost for good:", [["Runs", 1]], "",
				"Your stats and achievements stay.", "erase slot 1 [A]", "keep going [B]"),
		"abandon run": func() -> ConfirmDialog: return ExitDialogs.abandon_run({"operative": "BREAKER", "cycles": 3}),
		"abandon campaign": func() -> ConfirmDialog: return ExitDialogs.abandon_campaign({"runs": 2}, "Solace"),
		"quit": func() -> ConfirmDialog: return ExitDialogs.quit(true),
	}
	for key in builders:
		var v := _vinyl("GO", VinylSticker.Fill.PINK)
		var d: ConfirmDialog = (builders[key] as Callable).call()
		assert_true(d is ConfirmDialog, "%s is a ConfirmDialog" % key)
		add_child_autofree(d)
		await get_tree().process_frame
		assert_true(StickerSweepQueue.is_calm(), "%s open: calm" % key)
		assert_false(StickerSweepQueue.take_turn(v, 1 << 40), "%s open: no sweep takes a turn" % key)
		for s: Object in [v, d.yes_button, d.no_button]:
			assert_eq(StickerSweepQueue.sweeping(), 0, "%s: nothing sweeps" % key)
		remove_child(d)
		d.free()
		v.queue_free()
		await get_tree().process_frame
		assert_false(StickerSweepQueue.is_calm(), "%s closed: not calm" % key)


func test_the_curl_cover_is_a_triangle_inside_the_die_cut_and_the_flap_a_triangle() -> void:
	var body := Rect2(Vector2(10.0, 20.0), Vector2(300.0, 80.0))
	var c := 30.0
	var r := 14.0
	var edge := func(y_rel: float) -> float: return VerbSticker.rounded_right_edge(body, r, y_rel)
	var cover := VerbSticker.corner_cover(body, c, edge)
	var flap := VerbSticker.curl_flap(body, c)
	var tr := body.position + Vector2(body.size.x, 0.0)
	assert_eq(flap.size(), 3, "the flap is a triangle")
	assert_false(cover.is_empty())
	# the cover lies inside the rounded die-cut shape: no square patch past the rounded corner
	for p in cover:
		var y_rel: float = p.y - body.position.y
		assert_lte(p.x, VerbSticker.rounded_right_edge(body, r, y_rel) + 0.001, "cover point %s inside the die-cut" % p)
	assert_false(cover.has(tr), "the square corner itself is not painted: it is outside the rounded shape")
	# and it covers every point of the corner triangle that is inside the die-cut shape (below the fold line)
	var steps := 12
	var covered := 0
	for i in steps + 1:
		for j in steps + 1:
			var p := tr + Vector2(-c * float(i) / steps, c * float(j) / steps)
			var y_rel := p.y - body.position.y
			var inside_triangle := (p.x - (tr.x - c)) >= y_rel and p.x > tr.x - c + y_rel - 0.001
			var inside_shape := p.x <= VerbSticker.rounded_right_edge(body, r, y_rel) - 0.01 and y_rel <= c
			if inside_triangle and inside_shape:
				covered += 1
				assert_true(Geometry2D.is_point_in_polygon(p, cover), "corner point %s is covered" % p)
	assert_gt(covered, 10)


func test_no_scheduled_sweep_while_a_confirm_dialog_is_open() -> void:
	var v := _vinyl("GO", VinylSticker.Fill.PINK)
	var d := ConfirmDialog.new("Sure?", "YES", "CANCEL", "ARE YOU SURE?", "", true)
	add_child_autofree(d)
	await get_tree().process_frame
	assert_true(StickerSweepQueue.is_calm(), "a confirm is open")
	assert_false(StickerSweepQueue.take_turn(v, 1 << 40), "no sweep on any sticker meanwhile")
	remove_child(d)
	d.free()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_false(StickerSweepQueue.is_calm())
	assert_true(StickerSweepQueue.sweeping() == v.get_instance_id() or StickerSweepQueue.take_turn(v, 1 << 40), "and it sweeps again after")
