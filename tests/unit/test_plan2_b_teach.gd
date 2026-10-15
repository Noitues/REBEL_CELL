extends GutTest
## Plan 2 B-TEACH (PB-PT-002 C2 / C3 / C9, PB-PT-003b C1 / C3 / B8 / D1): the tutorial teaches aiming for a PERFECT as the
## core skill, with the player doing it: the tags, the aim beat (ends on a PERFECT tag), the free nudge and what extra
## nudges cost, the switches; its steps are short and NEXT reads as live.

const SCENE := "res://scenes/combat/combat_scene.tscn"
const TEACHING_ORDER: Array[String] = ["THE WHEEL", "THE TAGS", "AIM", "FREE NUDGE", "SWITCHES", "RESISTANCE", "CARDS", "STAGED", "RAM FORECAST", "UNDO", "SEND IT"]
## One idea per step: no step's text runs past this many words (CARDS carries the card controls).
const MAX_WORDS := 45

var _saved: Dictionary


func before_each() -> void:
	_saved = Settings.to_dict()
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	Settings.from_dict(_saved)
	AudioDirector.muted = false
	RunManager.scene_switching_enabled = true
	RunManager.reset()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _tutorial_scene() -> Control:
	var scene: Control = add_child_autofree(load(SCENE).instantiate())
	scene.auto_start = false
	scene.start_fight(&"triage_unit", 7)
	scene.start_tutorial()
	await _frames()
	return scene


func _titles() -> Array[String]:
	var out: Array[String] = []
	for s in TutorialOverlay.STEPS:
		out.append(String(s["title"]))
	return out


func test_the_teaching_beats_come_in_order() -> void:
	var titles := _titles()
	var at := -1
	for beat in TEACHING_ORDER:
		var i := titles.find(beat)
		assert_gt(i, at, "%s comes after the beat before it" % beat)
		at = i


func test_the_aim_and_free_nudge_beats_need_the_player_to_act() -> void:
	var by_title := {}
	for s in TutorialOverlay.STEPS:
		by_title[String(s["title"])] = String(s["until"])
	assert_eq(by_title["AIM"], TutorialOverlay.AIM_PERFECT, "the aim beat ends on a PERFECT tag")
	assert_eq(by_title["FREE NUDGE"], "nudge", "the free-nudge beat ends on a nudge")
	assert_eq(by_title["CARDS"], "card")
	assert_eq(by_title["SEND IT"], "turn_start", "and the last beat is SEND IT")
	var all := ""
	for i in TutorialOverlay.STEPS.size():
		all += TutorialOverlay.step_text(i) + " "
	for word in ["NULL", "WEAK", "GOOD", "PERFECT", "FREE NUDGE", "RAM", "staged", "THIS PLAY", "AT SEND IT"]:
		assert_string_contains(all, word, "the tutorial names %s" % word)
	assert_false(all.to_lower().contains("debt"), "there is no RAM debt")


func test_aim_step_advances_only_on_a_perfect_tag() -> void:
	var scene := await _tutorial_scene()
	var t: TutorialOverlay = scene.tutorial
	t.step = _titles().find("AIM")
	t.page = 0
	var st: CombatState = scene.engine.state()
	CombatFixture.land(st.player, 1, 1)  # one tick off center
	scene._refresh(st)
	assert_false(scene.player_aim_is_perfect(st), "one tick off is GOOD, not PERFECT")
	var off: int = int(scene.engine.resolver.pointer_readouts(st, st.player)[0]["offset"])
	scene.nudge(-1 if off > 0 else 1)
	scene.skip_motion()
	await _frames()
	assert_true(scene.player_aim_is_perfect(scene.engine.state()), "the nudge reached PERFECT")
	assert_eq(t.current_title(), "FREE NUDGE", "a PERFECT tag after your play ends the aim beat")


func test_a_nudge_that_stays_off_center_does_not_end_the_aim_beat() -> void:
	var scene := await _tutorial_scene()
	var t: TutorialOverlay = scene.tutorial
	t.step = _titles().find("AIM")
	t.page = 0
	var st: CombatState = scene.engine.state()
	CombatFixture.land(st.player, 1, 2)
	scene._refresh(st)
	var off: int = int(scene.engine.resolver.pointer_readouts(st, st.player)[0]["offset"])
	scene.nudge(-1 if off > 0 else 1)  # 2 off to 1 off: GOOD, still not PERFECT
	scene.skip_motion()
	await _frames()
	assert_eq(t.current_title(), "AIM", "still aiming")


func test_next_reads_as_live_on_every_step() -> void:
	var scene := await _tutorial_scene()
	var t: TutorialOverlay = scene.tutorial
	for i in TutorialOverlay.STEPS.size():
		t.step = i
		t.page = 0
		t.fit(t.size)
		assert_false(t.next_button.disabled, "step %d: NEXT is enabled" % i)
		assert_eq(t.next_button.modulate.a, 1.0, "step %d: NEXT is not dimmed" % i)
		assert_eq(t.next_button.get_theme_color(&"font_color"), HudSkin.TERMINAL_HI, "step %d: NEXT wears the lit color" % i)


func test_every_step_is_short_and_fits_the_box_at_text_1_0() -> void:
	Settings.set_text_scale(1.0)
	var scene := await _tutorial_scene()
	var t: TutorialOverlay = scene.tutorial
	for i in TutorialOverlay.STEPS.size():
		var words := TutorialOverlay.step_text(i).split(" ", false).size()
		assert_lte(words, MAX_WORDS, "step %d (%s): %d words, one idea" % [i, TutorialOverlay.STEPS[i]["title"], words])
		t.step = i
		t.page = 0
		t.fit(t.size)
		assert_true(t.page_fits(), "step %d: the page fits the note" % i)
	assert_eq(scene.layout_violations(), [] as Array[String], "the tutorial breaks no layout rule")
