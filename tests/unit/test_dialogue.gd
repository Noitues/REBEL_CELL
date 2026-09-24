extends GutTest
## Dialogue and the line database (GDD 8.2, 8.6, 9.6): every Solace Site has a DISPATCH
## briefing, every raid a warning, thresholds and the breach have lines, the Breaker has
## barks for every trigger, the DJ talks; lines are chosen deterministically, DISPATCH
## drifts with the profile, and the subtitle bar honours the subtitles setting.

var _corp: CorporationData


func before_all() -> void:
	_corp = ContentRegistry.get_content(&"solace") as CorporationData


func before_each() -> void:
	Dialogue.clear()
	Dialogue.history.clear()
	Settings.subtitles = true


func test_every_site_raid_and_threshold_has_a_line() -> void:
	for s in _corp.city_grid.sites:
		if s.id == _corp.city_grid.home_site_id:
			continue
		assert_not_null(Dialogue.line("site:%s" % s.id, RC.Voice.DISPATCH, &"solace"), "briefing for %s" % s.id)
	for r in _corp.raids:
		assert_not_null(Dialogue.line("raid:%s" % r.id, RC.Voice.CORPO, &"solace"), "Solace warning for %s" % r.id)
	for heat in [25, 50, 75, 100]:
		assert_not_null(Dialogue.line("threshold:%d" % heat, RC.Voice.DISPATCH, &"solace"))
	for key in ["boss", "win", "loss", "run_start", "run_complete", "run_died", "rack"]:
		assert_not_null(Dialogue.line(key, RC.Voice.DISPATCH, &"solace"), key)
	for trigger in ["perfect", "miss", "hurt", "victory", "defeat", "deploy", "jack_in", "boss"]:
		assert_not_null(Dialogue.line("bark:%s" % trigger, RC.Voice.STREET_MERC, &"", &"breaker"), trigger)
	assert_not_null(Dialogue.line("dj"))


func test_line_choice_is_deterministic_and_salted() -> void:
	var a := Dialogue.line("bark:perfect", RC.Voice.STREET_MERC, &"", &"breaker", 1)
	var b := Dialogue.line("bark:perfect", RC.Voice.STREET_MERC, &"", &"breaker", 1)
	assert_eq(a.text, b.text, "same salt, same line")
	var seen := {}
	for salt in 12:
		seen[Dialogue.line("bark:perfect", RC.Voice.STREET_MERC, &"", &"breaker", salt).text] = true
	assert_true(seen.size() > 1, "different salts reach different lines")


func test_dispatch_drifts_with_the_profile() -> void:
	var started := RunManager.profile.campaigns_started
	RunManager.profile.campaigns_started = 0
	assert_eq(Dialogue.drift_stage(), 0)
	var human := Dialogue.line("run_start", RC.Voice.DISPATCH, &"solace")
	assert_eq(human.drift_stage, 0)
	RunManager.profile.campaigns_started = 6
	assert_eq(Dialogue.drift_stage(), 2)
	var machine := Dialogue.line("run_start", RC.Voice.DISPATCH, &"solace")
	assert_eq(machine.drift_stage, 2, "the highest unlocked stage replaces the human line")
	assert_true(machine.dispatch_clue)
	RunManager.profile.campaigns_started = started


func test_say_queues_shows_and_honours_the_subtitles_setting() -> void:
	watch_signals(Dialogue)
	Dialogue.say(RC.Voice.DISPATCH, "First line.")
	assert_true(Dialogue.is_showing())
	assert_eq(Dialogue.current_text(), "First line.")
	assert_eq(Dialogue.speaker_label.text, "DISPATCH")
	assert_signal_emitted(Dialogue, "line_spoken")
	Dialogue.say(RC.Voice.STREET_MERC, "Second line.")
	assert_eq(Dialogue.current_text(), "First line.", "the second waits its turn")
	assert_eq(Dialogue.history.size(), 2)
	Dialogue.clear()
	assert_false(Dialogue.is_showing())
	Settings.subtitles = false
	Dialogue.say(RC.Voice.DISPATCH, "Silent line.")
	assert_false(Dialogue.is_showing(), "no bar without subtitles")
	assert_eq(Dialogue.history[Dialogue.history.size() - 1]["text"], "Silent line.", "still logged for voice-over")
	Settings.subtitles = true
	Dialogue.clear()


func test_briefing_and_bark_helpers_speak() -> void:
	var text := Dialogue.briefing(&"solace", &"t1_a")
	assert_true(text.contains("Billing"))
	assert_eq(Dialogue.current_text(), text)
	assert_eq(Dialogue.raid_warning(&"solace", &"raid_heat_25"), Dialogue.line("raid:raid_heat_25", -1, &"solace").text)
	assert_ne(Dialogue.bark(&"breaker", "perfect", 3), "")
	assert_ne(Dialogue.bark(&"ghost", "perfect", 3), "", "M6 classes bark too")
	assert_eq(Dialogue.bark(&"no_such_class", "perfect", 3), "", "no barks for an unknown class")
	assert_eq(Dialogue.threshold_line(&"solace", 50), Dialogue.line("threshold:50", -1, &"solace").text)
