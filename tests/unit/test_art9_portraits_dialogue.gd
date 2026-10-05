extends GutTest
## ART-9 4B (ART_BIBLE v2 §4.11 dialogue, §4.12 portraits; DECISIONS "Art direction — ART-9
## 4B dialogue and portraits"): every class x state renders from its bust set; an
## operative's face is chosen by class and id (never game RNG) and is the same everywhere;
## the feed's motions honour their entries (reduce effects and headless show the end state,
## nothing waits); DISPATCH gets a red voice feed and never a face; a speaking operative's
## bust talks in the subtitle bar, inside the bar, at every text size.

const CLASSES: Array[StringName] = [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]
const MODES: Array[int] = [PortraitFeed.Mode.IDLE, PortraitFeed.Mode.TALK, PortraitFeed.Mode.HURT, PortraitFeed.Mode.STATIONED,
	PortraitFeed.Mode.DEAD, PortraitFeed.Mode.RECRUIT, PortraitFeed.Mode.PRINT]

var _reduce := false
var _scale := 1.0
var _subtitles := true


func before_all() -> void:
	_reduce = Settings.reduce_effects
	_scale = Settings.text_scale
	_subtitles = Settings.subtitles


func after_each() -> void:
	Motion.force_live = false
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Settings.subtitles = _subtitles
	Dialogue.clear()
	Dialogue.release_default_rect(self)
	Dialogue.dock_default()


func test_every_class_has_a_bust_set_and_prints() -> void:
	for cls in CLASSES:
		assert_true(ContentRegistry.get_content(cls) is ClassData, "%s is a class" % cls)
		var sheet := PortraitBust.sheet(cls)
		assert_not_null(sheet, "%s has a bust atlas" % cls)
		if sheet == null:
			continue
		assert_eq(sheet.get_size(), Vector2(PortraitBust.CELL.x * PortraitBust.FRAMES, PortraitBust.CELL.y * PortraitBust.VARIANTS), "%s atlas layout" % cls)
		var prints := PortraitBust.print_sheet(cls)
		assert_not_null(prints, "%s has its corp prints" % cls)
		if prints != null:
			assert_eq(prints.get_size(), Vector2(PortraitBust.CELL.x, PortraitBust.CELL.y * PortraitBust.VARIANTS), "%s print layout" % cls)
		for v in PortraitBust.VARIANTS:
			assert_not_null(PortraitBust.print_texture(cls, v))
			for f in PortraitBust.FRAMES:
				var tex := PortraitBust.texture(cls, v, f) as AtlasTexture
				assert_not_null(tex)
				assert_true(Rect2(Vector2.ZERO, sheet.get_size()).encloses(tex.region), "%s %d/%d inside its atlas" % [cls, v, f])
	assert_false(PortraitBust.has_class(&"no_such_class"), "an unknown class has no set (the drawn fallback)")


func test_a_face_is_chosen_by_class_and_id() -> void:
	assert_eq(PortraitBust.variant_for(&"rigger", &""), 0, "the class's own face")
	var seen := {}
	for i in 12:
		var id := StringName("op_%d" % i)
		var v := PortraitBust.variant_for(&"rigger", id)
		assert_eq(v, PortraitBust.variant_for(&"rigger", id), "deterministic")
		assert_between(v, 0, PortraitBust.VARIANTS - 1)
		seen[v] = true
	assert_gt(seen.size(), 1, "rookies of one class wear different faces")
	var subj := PortraitArt.operative_subject(&"ghost", &"op_3", "WREN")
	assert_eq(subj["class_id"], &"ghost")
	assert_eq(subj["variant"], PortraitBust.variant_for(&"ghost", &"op_3"), "the paper views draw the same rookie as the feed")
	assert_eq(subj["tint"], Palette.class_accent(&"ghost"))
	var feed := PortraitFeed.new(&"ghost", &"op_3", "WREN")
	assert_eq(feed.variant, subj["variant"], "one face on every screen")
	feed.free()


func test_every_class_by_state_renders() -> void:
	for cls in CLASSES:
		for m in MODES:
			var f := PortraitFeed.new(cls, &"op_1", "TEST", m)
			f.size = Vector2(200, 222)
			add_child_autofree(f)
			assert_true(f.has_bust(), "%s %d shows its bust" % [cls, m])
			var mat := (f.get_node("Screen") as ColorRect).material as ShaderMaterial
			assert_eq(int(mat.get_shader_parameter(&"mode")), m)
			assert_eq(mat.get_shader_parameter(&"bust"), PortraitBust.sheet(cls))
			assert_eq(f.frame(), f.rest_frame(), "headless: the end state")
	await get_tree().process_frame
	var dead := PortraitFeed.new(&"rigger", &"", "", PortraitFeed.Mode.DEAD)
	assert_eq(dead.rest_frame(), PortraitBust.Frame.BLINK, "flatlined: dead eyes")
	var talk := PortraitFeed.new(&"rigger", &"", "", PortraitFeed.Mode.TALK)
	assert_eq(talk.rest_frame(), PortraitBust.Frame.TALK, "talking still: the mouth open")
	var hurt := PortraitFeed.new(&"rigger", &"", "", PortraitFeed.Mode.HURT)
	assert_eq(hurt.rest_frame(), PortraitBust.Frame.HURT, "hurt: the grimace")
	for f in [dead, talk, hurt]:
		f.free()


func test_hurt_follows_hp() -> void:
	var f := PortraitFeed.new(&"rigger", &"op_1", "SPROCKET")
	add_child_autofree(f)
	f.set_hp(12, 55)
	assert_eq(f.mode, PortraitFeed.Mode.HURT, "a quarter HP or less: hurt")
	f.set_hp(40, 55)
	assert_eq(f.mode, PortraitFeed.Mode.IDLE, "healed: live again")
	f.set_mode(PortraitFeed.Mode.DEAD)
	f.set_hp(1, 55)
	assert_eq(f.mode, PortraitFeed.Mode.DEAD, "the flatlined stay flatlined")


func test_feed_motion_honours_its_entries() -> void:
	for id in [&"portrait_feed", &"portrait_blink", &"portrait_talk", &"dispatch_trace"]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s required" % id)
		assert_true(Motion.has(id), "%s in ui_motion.tres" % id)
	var f := PortraitFeed.new(&"rigger", &"", "", PortraitFeed.Mode.TALK)
	add_child_autofree(f)
	assert_false(f.animating(), "headless: no motion, nothing waits")
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	Motion.force_live = true
	assert_true(f.animating())
	var step := Motion.seconds(&"portrait_talk")
	var frames := {}
	for k in 8:
		frames[f.frame_at(step * (k + 0.5))] = true
	assert_true(frames.has(PortraitBust.Frame.TALK) and frames.has(PortraitBust.Frame.IDLE), "the mouth swaps while talking")
	var idle := PortraitFeed.new(&"rigger", &"", "", PortraitFeed.Mode.IDLE)
	add_child_autofree(idle)
	var period := Motion.amplitude(&"portrait_blink")
	var blinks := 0
	var samples := 400
	for k in samples:
		if idle.frame_at(period * 2.0 * k / samples) == PortraitBust.Frame.BLINK:
			blinks += 1
	assert_gt(blinks, 0, "a live feed blinks")
	assert_lt(blinks, samples / 4, "and mostly has its eyes open")
	# Reduce effects: the end state at once.
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	assert_false(f.animating(), "reduce effects: a still")
	assert_eq(f.frame_at(step * 1.5), PortraitBust.Frame.TALK, "the still keeps the talking frame")
	assert_eq(idle.frame_at(0.0), PortraitBust.Frame.IDLE)


func test_dispatch_never_gets_a_face() -> void:
	var d := PortraitFeed.dispatch()
	add_child_autofree(d)
	assert_eq(d.mode, PortraitFeed.Mode.VOICE)
	assert_false(d.has_bust(), "voice only")
	assert_eq(d.accent(), PortraitFeed.dispatch_red())
	assert_false(bool(((d.get_node("Screen") as ColorRect).material as ShaderMaterial).get_shader_parameter(&"has_bust")))
	Settings.subtitles = true
	Dialogue.dock_at(Rect2(20, 40, 700, 90), 2)
	Dialogue.say(RC.Voice.DISPATCH, "Cell, the depot's yours.", 5.0)
	assert_true(Dialogue.feed.visible, "DISPATCH's feed shows")
	assert_eq(Dialogue.feed.mode, PortraitFeed.Mode.VOICE, "its voice trace, never a bust")
	var sb := Dialogue.bar.get_theme_stylebox("panel") as StyleBoxFlat
	assert_eq(sb.border_color, PortraitFeed.dispatch_red(), "a red CRT terminal feed")
	assert_ne(sb.bg_color, PaperInk.opaque(Color(Palette.NOTE_PAPER, 0.97), Palette.NIGHT_SKY), "never paper")


func test_a_bark_shows_its_class_bust_in_the_bar() -> void:
	Settings.subtitles = true
	Dialogue.dock_at(Rect2(20, 40, 700, 90), 2)
	var text := Dialogue.bark(&"wrecker", "perfect", 1)
	assert_ne(text, "", "the Wrecker barks (its base class's lines)")
	assert_true(Dialogue.feed.visible)
	assert_eq(Dialogue.feed.class_id, &"wrecker", "with its own face, not its base class's")
	assert_eq(Dialogue.feed.mode, PortraitFeed.Mode.TALK, "the speaker is live")
	Dialogue.clear()
	Dialogue.say(RC.Voice.NARRATOR, "the grid is listening", 5.0)
	assert_false(Dialogue.feed.visible, "no feed for a voice without one")


func test_the_feed_stays_inside_the_bar_at_every_text_size() -> void:
	Settings.subtitles = true
	for ts in [1.0, 1.6, 2.0]:
		Settings.set_text_scale(ts)
		for speaker in [[RC.Voice.DISPATCH, &""], [RC.Voice.STREET_MERC, &"ghost"]]:
			Dialogue.clear()
			var strip := Rect2(8, 60, 964, Dialogue.band_height(1))
			Dialogue.set_default_rect(strip, self)
			Dialogue.dock_default()
			Dialogue.say(speaker[0], "Cell, the depot's yours. Keep it quiet and get out before the sweep comes round.", 5.0, &"", false, "", speaker[1])
			await get_tree().process_frame
			var bar := Rect2(Dialogue.bar.global_position, Dialogue.bar.size)
			var feed := Rect2(Dialogue.feed.global_position, Dialogue.feed.size)
			assert_true(Dialogue.feed.visible)
			assert_true(bar.grow(0.5).encloses(feed), "x%.1f %d: the feed inside the bar (%s in %s)" % [ts, speaker[0], feed, bar])
			var sb := Dialogue.bar.get_theme_stylebox("panel")
			assert_true(Dialogue.text_label.global_position.x >= feed.end.x, "x%.1f: the words start right of the feed" % ts)
			assert_lte(bar.size.y, strip.size.y + 1.0, "x%.1f: the bar keeps its strip" % ts)
			assert_gt(sb.get_margin(SIDE_LEFT), feed.size.x, "the paging leaves the feed's room")
		Dialogue.release_default_rect(self)


func test_polaroid_kia_defaults_off() -> void:
	var p := Polaroid.new("SWARM KIA")
	assert_false(p.kia)
	p.free()
