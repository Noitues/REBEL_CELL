extends GutTest
## M14 LEAK (DECISIONS "M14 LEAK"): a line said in one campaign never shows in the next. The
## campaign end's DISPATCH line (Solace's "Home server lost ...") has no screen scope, so it played
## out over the NEW CAMPAIGN page and the new campaign's HQ; a cleared Dialogue stays cleared (its
## old page timer, a repage or a screen change bring nothing back).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _subtitles: bool
var _screen: String


func before_each() -> void:
	_subtitles = Settings.subtitles
	_screen = Dialogue.screen
	Settings.subtitles = true
	AudioDirector.muted = true
	RunManager.save_slot = "gut_m14_leak"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Dialogue.clear()
	Dialogue.history.clear()


func after_each() -> void:
	Dialogue.clear()
	Dialogue.history.clear()
	Settings.subtitles = _subtitles
	Dialogue.screen = _screen
	Dialogue.dock_default()
	RunManager.delete_save()
	RunManager.reset()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


## Every word the Dialogue shows or still has queued, as one list.
func _pending() -> Array[String]:
	var out: Array[String] = []
	if Dialogue.is_showing():
		out.append(Dialogue.current_text())
	for l in Dialogue._queue:
		out.append(String(l["text"]))
	return out


## Asserts nothing shown or queued comes from `said` (a page of a line is part of its words).
func _assert_none_of(said: Array[String], where: String) -> void:
	for p in _pending():
		for s in said:
			assert_false(p.strip_edges() != "" and (s.contains(p.strip_edges()) or p.contains(s)),
				"%s: '%s' is from the previous campaign" % [where, p])


func _said() -> Array[String]:
	var out: Array[String] = []
	for h in Dialogue.history:
		out.append(String(h["text"]))
	return out


func test_a_lost_campaigns_end_line_does_not_reach_the_next_campaign() -> void:
	RunManager.new_campaign(7, &"solace")
	DemoSetup.end_campaign(RunManager.campaign, CampaignState.Outcome.LOST)
	var hq := _scene(HQ)
	await _frames(2)
	assert_eq(hq.panel_name, "end", "the lost campaign opens on its end (headless: the dossier)")
	assert_true(Dialogue.is_showing(), "DISPATCH says the loss")
	var said := _said()
	assert_false(said.is_empty())
	var loss := Dialogue.voice_text(Dialogue.line("loss", RC.Voice.DISPATCH, &"solace", &"", RunManager.campaign.campaign_seed))
	assert_has(said, loss, "the campaign's end line")
	# NEW CAMPAIGN on the dossier: the start page shows nothing from the lost campaign.
	hq._on_end_new_campaign()
	await _frames(2)
	assert_eq(hq.panel_name, "start")
	_assert_none_of(said, "new campaign page")
	# START: the new campaign's HQ neither.
	hq.new_campaign(8, 0, RunManager.DEFAULT_HOME, RunManager.DEFAULT_CLASS, &"solace")
	await _frames(2)
	_assert_none_of(said, "new campaign's HQ")


func test_a_new_campaign_starts_with_an_empty_subtitle_bar() -> void:
	RunManager.new_campaign(7, &"solace")
	Dialogue.speak("loss", RC.Voice.DISPATCH, &"solace", &"", 7)
	Dialogue.speak("win", RC.Voice.DISPATCH, &"solace", &"", 7)
	var said := _said()
	assert_eq(said.size(), 2)
	assert_true(Dialogue.is_showing())
	RunManager.new_campaign(8, &"solace")
	assert_false(Dialogue.is_showing(), "the bar is down")
	assert_true(Dialogue._queue.is_empty(), "nothing queued from the previous campaign")
	_assert_none_of(said, "after new_campaign")


func test_a_cleared_dialogue_brings_nothing_back() -> void:
	# A long line in a one-line dock: several pages, the rest queued behind the first.
	Dialogue.dock_at(Rect2(8, 2, 400, 40), 1)
	Dialogue.say(RC.Voice.DISPATCH, "Home server lost. Reconstitution scheduled. The Cell is not the point; the outcome is. " +
		"Home server lost. Reconstitution scheduled. The Cell is not the point; the outcome is.", 0.0, &"solace")
	var timer: SceneTreeTimer = Dialogue._timer
	assert_not_null(timer)
	assert_false(Dialogue._queue.is_empty(), "the line's later pages wait in the queue")
	Dialogue.clear()
	assert_false(Dialogue.is_showing())
	assert_eq(Dialogue.current_text(), "")
	assert_eq(Dialogue.shown_scope(), "")
	assert_true(Dialogue._shown_line.is_empty(), "the shown line is forgotten")
	# The old page's timer ends: it does not page on.
	timer.timeout.emit()
	assert_false(Dialogue.is_showing(), "the old page timer shows nothing")
	# A screen change and a dock change (which pages the shown line again) bring nothing back.
	Dialogue.enter_screen("hq_leak_probe")
	Dialogue.dock_at(Rect2(8, 2, 900, 60), 2)
	Dialogue.dock_default()
	assert_false(Dialogue.is_showing(), "nothing re-shown")
	assert_true(Dialogue._queue.is_empty())
	await _frames(2)
	assert_false(Dialogue.is_showing())
