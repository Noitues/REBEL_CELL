extends GutTest
## M14 FIX-2 (DECISIONS "M14 FIX-2"): (1) after the campaign is lost, the HQ's last Heat shows no
## crossing banner and no "A raid is queued" note, and the RansomLock stands on its own canvas layer
## over the subtitles' (DISPATCH's last line is read through the takeover, never drawn untinted over
## it); (2) the corp memo's routing line (TO / FROM / REF) wraps, then folds, to the memo's width at
## 1.0 / 1.6 / 2.0 for every corp, never smaller than at 1.0, and the memo's words start under it.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCALES: Array[float] = [1.0, 1.6, 2.0]
## The corp memo's width on the event screen (NetrunScene.EVENT_MEMO_W).
const MEMO_W := 470.0
const MARKS: Array[int] = [25, 50, 75]

var _scale: float
var _reduce: bool


func before_each() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_m14_fix2"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
		Fx.apply_settings()
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 1) -> void:
	for i in n:
		await get_tree().process_frame


# --- 1. No raid toast after the campaign is lost; the subtitle under the lock -----------------

func test_a_heat_crossing_after_the_campaign_is_lost_shows_no_raid_note() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var p := HeatPoster.new(true)
	holder.add_child(p)
	p.position = Vector2(40, 100)
	p.size = p.custom_minimum_size
	# The control: while the campaign runs, the crossing's note shows (the toast).
	p.set_heat(10, 100, MARKS)
	p.set_heat(80, 100, MARKS)
	p.complete_motion()
	await _frames()
	assert_true(p.note_showing(), "campaign running: the crossing's note shows")
	assert_string_contains(p.note_text(), "queued")
	# Lost now: a note still holding goes on its next frame, and no new crossing stamps one.
	DemoSetup.end_campaign(c, CampaignState.Outcome.LOST)
	p._banner_frame(0.0)
	assert_false(p.note_showing(), "lost: the note still holding goes")
	p.complete_motion()
	p._end_banner()
	p.set_heat(10, 100, MARKS)
	p.set_heat(90, 100, MARKS)
	p.complete_motion()
	await _frames(2)
	assert_eq(p.banner_alpha, 0.0, "lost: no crossing banner")
	assert_false(p.note_showing(), "lost: no 'A raid is queued' note")
	assert_eq(p.shown_heat, 90.0, "the Heat itself still shows its value")
	p.free()


func test_the_hq_on_campaign_lost_raises_no_raid_toast_and_the_lock_stands_over_the_subtitles() -> void:
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	Motion.force_live = true
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	c.heat = 10
	var before_hash := 0
	var hq: Control = load(HQ).instantiate()
	add_child_autofree(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(2)
	# The final raid's Heat: over two thresholds, as the playout leaves it (hud_heat_shown reset).
	c.heat = 80
	DemoSetup.end_campaign(c, CampaignState.Outcome.LOST)
	before_hash = c.state_hash()
	hq.hud_heat_shown = -1
	hq.show_end()
	hq._refresh_status()
	await _frames(3)
	var gauge: HeatPoster = hq.hud.heat_gauge
	gauge.complete_motion()
	await _frames()
	assert_eq(gauge.banner_alpha, 0.0, "no Heat crossing banner after the loss")
	assert_false(gauge.note_showing(), "no 'A raid is queued' toast after the loss")
	var lock: RansomLock = hq.end_lock
	assert_not_null(lock, "the lock plays")
	var layer := lock.get_parent() as CanvasLayer
	assert_not_null(layer, "the lock stands on its own canvas layer")
	if layer != null:
		assert_gt(layer.layer, Dialogue.layer, "over the subtitles' layer: DISPATCH's line is read through the takeover")
		assert_eq(layer.get_parent(), hq, "the HQ's own layer")
	assert_not_null(lock.glass.get_node_or_null(NodePath(ScreenCopy.NODE_NAME)) if lock.glass != null else null,
		"the takeover reads the screen as drawn under it (the subtitles too)")
	if Dialogue.is_showing():
		assert_false(Dialogue.default_rect.intersects(lock.notice_rect_on(hq.get_global_rect())),
			"the subtitle band is clear of the notice")
	lock.complete_motion()
	lock.cut()
	await BoundedWait.until(get_tree(), func() -> bool: return hq.panel_name == "end", 5.0, 240)
	assert_eq(hq.panel_name, "end", "the cut shows the dossier")
	await _frames()
	assert_null(hq.get_node_or_null(^"EndLockLayer"), "the lock's layer goes with it (END_LOCK_LAYER_NAME)")
	assert_eq(c.state_hash(), before_hash, "the end screens change nothing")


# --- 2. The memo's routing line at 1.0 / 1.6 / 2.0 ---------------------------------------------

## The routing line's words (any run of spaces as one).
func _words(s: String) -> PackedStringArray:
	return s.split(" ", false)


func _assert_routing_fits(memo: CorpMemo, tag: String) -> void:
	var f := Palette.paper()
	var ms := memo.meta_px()
	assert_gte(ms, CorpMemo.META_PX, "%s: never smaller than at 1.0" % tag)
	assert_eq(ms, roundi(CorpMemo.META_PX * memo.text_scale), "%s: the text size's own lettering (never shrunk)" % tag)
	var lines := memo.routing_lines()
	var room := memo.size.x - CorpMemo.PAD.x * 2.0 * memo.text_scale
	for line in lines:
		var w := f.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, ms).x
		assert_lte(w, room + 0.5, "%s: '%s' in the memo (%.0f in %.0f)" % [tag, line, w, room])
	assert_eq(_words(" ".join(lines)), _words(memo.routing_text()), "%s: every word, in order (%s)" % [tag, lines])
	# The words start under the last routing line.
	var s := memo.text_scale
	var paper := Palette.paper_bold()
	var ts := roundi(CorpMemo.TITLE_PX * s)
	var y := memo.head_h() + 6.0 * s + paper.get_ascent(ts) + paper.get_descent(ts) + f.get_ascent(ms) + 4.0 * s
	var bottom := y + f.get_height(ms) * float(lines.size() - 1) + f.get_descent(ms)
	assert_lte(bottom, float(memo.margins.get_theme_constant(&"margin_top")) + 0.5, "%s: the story starts under the routing line" % tag)
	assert_lte(memo.margins.position.y + memo.body.position.y, memo.size.y, "%s: the body is on the memo" % tag)


func test_the_memo_routing_line_wraps_then_folds_for_every_corp_at_every_size() -> void:
	var wrapped_at_2 := false
	for scale in SCALES:
		Settings.set_text_scale(scale)
		for id: StringName in RaidSkin.CORPS:
			var corp := RunManager.lookup().get_content(id) as CorporationData
			var memo := CorpMemo.new(TextDb.t(corp, "display_name"), Palette.corp_color(id), scale, CorpPaperPanel.letterhead_of(corp))
			add_child_autofree(memo)
			memo.custom_minimum_size = Vector2(MEMO_W, 0)
			memo.size = Vector2(MEMO_W, 300.0)
			var story := Label.new()
			story.text = "The story."
			memo.body.add_child(story)
			await _frames(2)
			memo.size = Vector2(MEMO_W, memo.get_combined_minimum_size().y)
			await _frames()
			_assert_routing_fits(memo, "x%.1f %s" % [scale, id])
			assert_string_contains(" ".join(memo.routing_lines()), TextDb.t(corp, "display_name").to_upper(), "the full name on the routing line")
			if is_equal_approx(scale, 2.0) and memo.routing_lines().size() > 1:
				wrapped_at_2 = true
			memo.queue_free()
		# DISPATCH's voice transcript on the same paper.
		var tr_memo := CorpMemo.new("DISPATCH", Palette.CORP_SOLACE, scale).as_transcript()
		add_child_autofree(tr_memo)
		tr_memo.custom_minimum_size = Vector2(MEMO_W, 0)
		tr_memo.size = Vector2(MEMO_W, 300.0)
		await _frames()
		_assert_routing_fits(tr_memo, "x%.1f transcript" % scale)
		tr_memo.queue_free()
	assert_true(wrapped_at_2, "at 2.0 the routing line no longer fits one line: it wraps (it was clipped)")


func test_wrap_routing_packs_fields_then_folds_a_long_field_at_its_words() -> void:
	var f := Palette.paper()
	var px := 12
	var text := "TO: A    FROM: MERIDIAN FREIGHT SYSTEMS    REF: X"
	var wide := CorpMemo.wrap_routing(f, text, px, 4000.0)
	assert_eq(Array(wide), [text], "room enough: one line as written")
	var field_w := f.get_string_size("FROM: MERIDIAN FREIGHT SYSTEMS", HORIZONTAL_ALIGNMENT_LEFT, -1, px).x
	var by_field := CorpMemo.wrap_routing(f, text, px, field_w + 1.0)
	assert_eq(Array(by_field), ["TO: A", "FROM: MERIDIAN FREIGHT SYSTEMS", "REF: X"], "wraps at the fields first")
	var folded := CorpMemo.wrap_routing(f, text, px, field_w * 0.6)
	assert_gt(folded.size(), 3, "a field wider than the room folds at its words")
	assert_eq(_words(" ".join(folded)), _words(text), "never a word lost")
	for line in folded:
		assert_lte(f.get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, field_w * 0.6 + 0.5, "'%s' in its room" % line)
