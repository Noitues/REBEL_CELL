extends GutTest
## Animation pass ANIM-6 (ANIMATION_HANDOFF 4.13, 4.17-4.24; STYLE_GUIDE 5.3): screens, menus
## and ambience. Reduce effects and headless show every end state at once; a screen enters
## (glass slides, paper drops) and focus lands on its first control when it ends, and the
## pad walks on from there; a press mid-entrance completes it; subtitles type in but read
## whole at once headless, with the instant setting, and page as before; a top bar tag
## bumps only when its value changed; a Modem purchase and a loot pick fly to their icon and
## the state is the purchase's; motion never changes game state; the end-state layout is
## the instant layout at text scale 1.0, 1.3 and 1.6; a settings change animates nothing.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SLOT := "gut_test_anim6"
## Longer than any entrance or flight (s).
const SETTLE_WAIT := 0.8
## Wall-clock ceiling for `_until` (a motion that never ends fails its assert after it).
const WAIT_LIMIT_MS := 10000

var _scale_before: float = 1.0
var _reduce_before: bool = false
var _typing_before: bool = true


func before_all() -> void:
	_scale_before = Settings.text_scale
	_reduce_before = Settings.reduce_effects
	_typing_before = Settings.subtitle_typing


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false
	DripButton.reset_growth()


func after_each() -> void:
	Motion.force_live = false
	if Settings.reduce_effects != _reduce_before:
		Settings.set_reduce_effects(_reduce_before)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale_before):
		Settings.set_text_scale(_scale_before)
	if Settings.subtitle_typing != _typing_before:
		Settings.set_subtitle_typing(_typing_before)
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## Awaits frames until `done` holds (at most WAIT_LIMIT_MS of wall time) and returns the
## game time that took, less its longest frame. Test suite optimization: fixed waits of a
## motion's length plus a margin failed on a busy machine, where one long frame can carry
## the timer past the margin before the tween's last step; this measures the motion
## itself, so the timing asserts keep their margins and a stalled frame cannot fail them.
func _until(done: Callable) -> float:
	var total := 0.0
	var longest := 0.0
	var start := Time.get_ticks_msec()
	while not done.call() and Time.get_ticks_msec() - start < WAIT_LIMIT_MS:
		await get_tree().process_frame
		var d := get_process_delta_time()
		total += d
		longest = maxf(longest, d)
	return total - longest


## A motion measured by `_until` ended within its own length plus the same again and a
## tenth of a second: slack derived from the motion's value, so a slow machine's uneven
## frames pass and a motion that runs several times too long still fails.
func _assert_in_time(took: float, seconds: float, what: String) -> void:
	assert_lt(took, seconds * 2.0 + 0.1, "%s ends in its time (%.2f s for %.2f s)" % [what, took, seconds])


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Motion.force_live = true


func _press(keycode: Key) -> void:
	var down := InputEventKey.new()
	down.keycode = keycode
	down.physical_keycode = keycode
	down.pressed = true
	get_viewport().push_input(down)
	var up := down.duplicate() as InputEventKey
	up.pressed = false
	get_viewport().push_input(up)


## A netrun scene in a 1280x720 holder with a campaign and a run on the route.
func _netrun(scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	return scene


func _to_shop(scene: Control) -> void:
	RunManager.netrun.run.cycles = 120
	RunManager.netrun._open_shop()
	scene._show_current()


func _to_loot(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()


func _to_event(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.event_id = &"ev_leash_on_the_floor"
	run.phase = RunState.Phase.EVENT
	scene._show_current()


func _focus_owner() -> Control:
	return get_viewport().gui_get_focus_owner()


func _state() -> Array:
	return [RunManager.campaign.to_dict() if RunManager.campaign != null else null,
		RunManager.netrun.run.to_dict() if RunManager.netrun != null else null, RngService.to_dict()]


# --- Reduce effects and headless: the end state at once -------------------------------------------

func _assert_instant(why: String) -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	# A page: no entrance, on_done at once.
	var page := TerminalWindow.new("PAGE")
	holder.add_child(page)
	var done := [false]
	assert_null(PageTransition.enter(page, PageTransition.Look.GLASS, func() -> void: done[0] = true), "%s: no entrance" % why)
	assert_true(done[0], "%s: focus given at once" % why)
	assert_eq(page.modulate.a, 1.0)
	# A menu: no typing, no slide.
	var box := VBoxContainer.new()
	holder.add_child(box)
	for t in ["Continue", "Campaigns", "Codex"]:
		var b := Button.new()
		b.text = t
		box.add_child(b)
	var mm := MenuMotion.attach(box)
	(box.get_child(0) as Button).grab_focus()
	(box.get_child(1) as Button).grab_focus()
	assert_false(mm.typing() or mm.sliding(), "%s: the line shows whole" % why)
	assert_eq((box.get_child(1) as Button).text, "Campaigns")
	# The top bar: no bump, the new value.
	var stats := HudStats.new()
	holder.add_child(stats)
	stats.items = [["CYCLES", "10", ""]]
	stats.items = [["CYCLES", "50", ""]]
	assert_eq(stats.bumping().size(), 0, "%s: no bump" % why)
	assert_eq(stats.shown_value(0), "50")
	# Drips, the Modem sign, loot, flights, subtitles.
	var drip := DripButton.new("GUT DRIP", "", DripButton.DRIP_PINK, 32, DripButton.SEND_IT_DRIPS)
	holder.add_child(drip)
	drip.grow_in()
	assert_eq(drip.grow, 1.0, "%s: drips full" % why)
	var sign := ModemSign.new()
	holder.add_child(sign)
	sign.warm_up()
	assert_false(sign.warming(), "%s: the sign is lit" % why)
	var card := ZineCard.new("LOOT", 1, "", 0)
	holder.add_child(card)
	card.fan_in(Vector2(640, 700), 8.0, 0.0)
	assert_eq(card.draw_offset, Vector2.ZERO, "%s: loot in its slot" % why)
	assert_eq(card.modulate.a, 1.0)
	assert_null(FlightFx.fly(holder, card, Vector2(10, 10), &"buy_fly", "SOLD"), "%s: nothing flies" % why)
	assert_null(FlightFx.stamp_on(holder, card, ""), "%s: nothing stamps" % why)
	Dialogue.say(RC.Voice.DISPATCH, "Gut line that would type in.")
	assert_false(Dialogue.typing(), "%s: the subtitle is whole" % why)
	assert_eq(Dialogue.text_label.visible_characters, -1)
	var stamp := ZineStamp.new("JACK IN")
	holder.add_child(stamp)
	stamp.breathe()
	assert_false(stamp.breathing(), "%s: JACK IN rests" % why)
	assert_null(CrtHum.attach(page), "%s: no hum" % why)


func test_headless_shows_every_end_state_at_once() -> void:
	_assert_instant("headless")


func test_reduce_effects_shows_every_end_state_at_once() -> void:
	Motion.force_live = true
	Settings.set_reduce_effects(true)
	_assert_instant("reduce effects")


# --- Transitions -----------------------------------------------------------------------------------

func test_a_screen_enters_and_focus_lands_on_its_first_control() -> void:
	var scene := await _netrun()
	_live()
	_to_shop(scene)
	var page: Control = scene._panel
	assert_true(PageTransition.running(page), "the Modem slides in")
	assert_eq(PageTransition.look_of(page), PageTransition.Look.GLASS)
	assert_false(page.is_ancestor_of(_focus_owner()) if _focus_owner() != null else false, "focus waits for the entrance")
	var took := await _until(func() -> bool: return not PageTransition.running(page))
	_assert_in_time(took, PageTransition.seconds_for(PageTransition.Look.GLASS), "the entrance")
	await _frames()
	assert_false(PageTransition.running(page), "the entrance ended")
	assert_eq(_focus_owner(), UiFocus.first_focusable(page), "focus on the page's first control")
	var first := _focus_owner()
	_press(KEY_RIGHT)
	await _frames()
	assert_ne(_focus_owner(), first, "the pad walks on from there")
	assert_true(page.is_ancestor_of(_focus_owner()), "and stays on the page")


func test_a_press_mid_entrance_completes_it() -> void:
	var scene := await _netrun()
	_live()
	_to_loot(scene)
	var page: Control = scene._panel
	await _frames(2)
	assert_true(PageTransition.running(page), "the loot comes in")
	var cards := page.find_child("Stickers", true, false)
	_press(KEY_SPACE)
	assert_false(PageTransition.running(page), "a press ends it at once")
	assert_eq(page.modulate.a, 1.0)
	for c in cards.get_children():
		assert_false((c as ZineCard).dealing(), "the fan completes too")
		assert_eq((c as ZineCard).draw_offset, Vector2.ZERO)
	await _frames()
	assert_eq(_focus_owner(), UiFocus.first_focusable(page), "focus lands")
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.REWARD, "the press did nothing else")


func test_paper_drops_and_a_refresh_does_not_reenter() -> void:
	var scene := await _netrun()
	_live()
	_to_event(scene)
	assert_eq(PageTransition.look_of(scene._panel), PageTransition.Look.PAPER, "the event's note is paper")
	assert_true(PageTransition.running(scene._panel))
	PageTransition.settle(scene)
	# The same screen rebuilt (as the Modem after a purchase) just shows.
	scene._show_current()
	assert_false(PageTransition.running(scene._panel), "a refresh does not slide in again")


# --- Menus -----------------------------------------------------------------------------------------

func test_menu_lines_type_in_and_the_highlight_slides() -> void:
	_live()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var box := VBoxContainer.new()
	holder.add_child(box)
	for t in ["Continue", "Campaigns", "Tutorial"]:
		var b := Button.new()
		b.text = t
		b.theme_type_variation = &"MenuItem"
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		box.add_child(b)
	var mm := MenuMotion.attach(box)
	await _frames()
	var first := box.get_child(0) as Button
	var second := box.get_child(1) as Button
	var w := second.size
	first.grab_focus()
	assert_false(mm.typing(), "the first focus (a page opening) shows at once")
	second.grab_focus()
	assert_true(mm.typing(), "a focus move types the line in")
	assert_true(mm.sliding(), "and slides the highlight")
	assert_true(second.text.length() < "Campaigns".length())
	await _frames()
	assert_eq(second.size, w, "the line keeps its size while it types")
	_press(KEY_A)
	assert_false(mm.typing(), "a key press completes it")
	assert_eq(second.text, "Campaigns")
	var took := await _until(func() -> bool: return not mm.sliding())
	_assert_in_time(took, Motion.seconds(&"menu_highlight"), "the highlight slide")
	assert_false(mm.sliding())
	assert_true(mm.caret_rect().has_area(), "the caret sits after the words")


# --- Subtitles -------------------------------------------------------------------------------------

func test_subtitles_read_whole_headless_and_with_the_instant_setting() -> void:
	var line := "Headless reads the whole line at once."
	Dialogue.say(RC.Voice.DISPATCH, line)
	assert_eq(Dialogue.current_text(), line)
	assert_eq(Dialogue.text_label.visible_characters, -1, "headless: all drawn")
	Dialogue.clear()
	_live()
	Settings.set_subtitle_typing(false)
	Dialogue.say(RC.Voice.DISPATCH, line)
	assert_false(Dialogue.typing(), "instant: no typing")
	assert_eq(Dialogue.text_label.visible_characters, -1)
	Dialogue.clear()
	Settings.set_subtitle_typing(true)
	Dialogue.say(RC.Voice.DISPATCH, line)
	assert_true(Dialogue.typing(), "typing: the line types in")
	assert_true(Dialogue.text_label.visible_characters < Dialogue.text_label.get_total_character_count())
	assert_eq(Dialogue.current_text(), line, "the words are all there to read")
	_press(KEY_A)
	assert_false(Dialogue.typing(), "a press shows it whole")


func test_paging_waits_for_the_typed_page() -> void:
	_live()
	Dialogue.clear()
	Dialogue.dock_at(Rect2(8, 2, 420, 30), 1)
	var long := "A long line that cannot fit one strip of the dock and so goes on over several pages of words."
	Dialogue.say(RC.Voice.DISPATCH, long)
	var first := Dialogue.current_text()
	assert_true(first.length() < long.length(), "the line pages")
	assert_true(Dialogue.typing(), "the first page types")
	assert_true(Dialogue._timer.time_left > Dialogue.MIN_SECONDS, "its time starts after the typing")
	Dialogue.finish_typing()
	Dialogue._next()
	assert_ne(Dialogue.current_text(), first, "the next page follows")


# --- Top bar -------------------------------------------------------------------------------------

func test_a_tag_bumps_only_when_its_value_changed() -> void:
	_live()
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var stats := HudStats.new()
	stats.size = Vector2(900, 60)
	holder.add_child(stats)
	stats.items = [["HEAT", "12", "/100"], ["CYCLES", "40", ""], ["CARDS", "10", ""]]
	assert_eq(stats.bumping().size(), 0, "the first set bumps nothing")
	stats.items = [["HEAT", "12", "/100"], ["CYCLES", "90", ""], ["CARDS", "10", ""]]
	assert_eq(Array(stats.bumping()), ["CYCLES"], "only the changed tag bumps")
	assert_eq(stats.shown_value(1), "40", "its number rolls from the old value")
	stats.items = [["HEAT", "12", "/100"], ["CYCLES", "90", ""], ["CARDS", "10", ""]]
	assert_eq(Array(stats.bumping()), ["CYCLES"], "the same values start nothing new")
	var took := await _until(func() -> bool: return stats.bumping().is_empty())
	_assert_in_time(took, Motion.seconds(&"count_up"), "the count roll")
	assert_eq(stats.bumping().size(), 0)
	assert_eq(stats.shown_value(1), "90", "it ends on the value")
	var rects := stats.tag_rects()
	stats.items = [["HEAT", "13", "/100"], ["CYCLES", "90", ""], ["CARDS", "10", ""]]
	assert_eq(stats.tag_rects(), rects, "a bump never moves the tags")


# --- Modem and loot flights ------------------------------------------------------------------------

func test_a_modem_purchase_flies_and_the_state_is_the_purchase() -> void:
	var scene := await _netrun()
	_live()
	_to_shop(scene)
	PageTransition.settle(scene)
	await _frames()
	var s := RunManager.netrun
	var price := int(s.run.shop["card_prices"][0])
	var card_id := StringName(String(s.run.shop["cards"][0]))
	var deck := s.run.operative.deck.size()
	var cycles := s.run.cycles
	scene.buy("cards", 0)
	assert_eq(FlightFx.active_count(scene), 1, "the card flies")
	var flight: Dictionary = FlightFx.existing(scene).flights[0]
	assert_eq(flight["to"], scene.item_target("card"), "to the CARDS tag")
	assert_true(flight["node"].find_child("Stamp", true, false) != null, "SOLD stamps on it")
	var after := _state()
	assert_eq(s.run.cycles, cycles - price, "paid")
	assert_eq(s.run.operative.deck.size(), deck + 1, "the card is in the deck")
	assert_true(s.run.operative.deck.has(card_id))
	assert_true(scene._panel.find_child("ModemSign", true, false).warming() == false, "the Modem does not warm up again")
	var took := await _until(func() -> bool: return FlightFx.active_count(scene) == 0)
	_assert_in_time(took, SETTLE_WAIT, "the flight")
	assert_eq(FlightFx.active_count(scene), 0, "the flight ends")
	assert_eq(_state(), after, "the flight changed nothing")


func test_a_loot_pick_ends_in_the_deck() -> void:
	var scene := await _netrun()
	_live()
	_to_loot(scene)
	PageTransition.settle(scene)
	await _frames()
	var deck := RunManager.netrun.run.operative.deck.size()
	scene.choose_reward(1)
	# ANIM-R1 M11 (expectation changed on purpose): the two offers not taken fall away too.
	var picks := FlightFx.existing(scene).flights.filter(func(f: Dictionary) -> bool: return f["id"] == &"loot_pick")
	var rejects := FlightFx.existing(scene).flights.filter(func(f: Dictionary) -> bool: return f["id"] == &"loot_reject")
	assert_eq(picks.size(), 1, "the card lifts and flies")
	assert_eq(rejects.size(), 2, "the others fall away")
	var flight: Dictionary = picks[0]
	assert_eq(flight["to"], scene.hud.stats.icon_point(StatIcon.CARDS), "to the deck (CARDS) icon")
	assert_eq(RunManager.netrun.run.operative.deck.size(), deck + 1)
	assert_true(RunManager.netrun.run.operative.deck.has(&"jam"), "the picked card is in the deck")
	var took := await _until(func() -> bool: return FlightFx.active_count(scene) == 0)
	_assert_in_time(took, SETTLE_WAIT, "the loot flight")
	assert_eq(FlightFx.active_count(scene), 0, "it lands")


func test_an_event_choice_stamps_its_outcome() -> void:
	var scene := await _netrun()
	_live()
	_to_event(scene)
	PageTransition.settle(scene)
	await _frames()
	var row := scene._panel.find_child("Choice1", true, false).get_node("OutcomeRow") as Control
	# The row's own size (its global rect is scaled while an entrance pop still runs, and
	# with fast frames one frame after the page settles it can still run).
	var rest_size := row.size
	scene._panel.find_child("Choice1", true, false).mouse_entered.emit()
	assert_true(row.has_meta(&"motion_scale"), "hover pops the icons")
	var took := await _until(func() -> bool: return row.scale == Vector2.ONE)
	_assert_in_time(took, Motion.seconds(&"event_outcome_pop"), "the pop")
	assert_eq(row.scale, Vector2.ONE, "and they settle")
	scene.choose_event(0)
	assert_eq(FlightFx.active_count(scene), 1, "the chosen outcome stamps")
	assert_almost_eq((FlightFx.existing(scene).flights[0]["node"] as Control).size, rest_size, Vector2.ONE, "over the chosen outcome")
	FlightFx.finish_all(scene)
	assert_eq(FlightFx.active_count(scene), 0)


# --- Game state, layout, settings ------------------------------------------------------------------

func test_screen_motion_never_changes_game_state() -> void:
	var scene := await _netrun()
	_to_shop(scene)
	var before := _state()
	_live()
	# Replay every screen motion over the same state.
	scene._shown_screen = ""
	scene._show_current()
	(scene._panel.find_child("ModemSign", true, false) as ModemSign).warm_up()
	scene.hud.stats.items = [["CYCLES", "1", ""]]
	scene._refresh_status()
	Dialogue.say(RC.Voice.DISPATCH, "No state changes here.")
	await wait_seconds(SETTLE_WAIT)
	PageTransition.settle(scene)
	assert_eq(_state(), before, "campaign, run and RNG untouched")
	for path in ["res://scripts/ui/kit/page_transition.gd", "res://scripts/ui/kit/menu_motion.gd", "res://scripts/ui/kit/flight_fx.gd",
			"res://scripts/ui/kit/typing.gd", "res://scripts/ui/kit/crt_hum.gd"]:
		var src := FileAccess.get_file_as_string(path)
		for banned in ["RunManager", "RngService", "SaveService", "randi(", "randf(", "randomize("]:
			assert_false(src.contains(banned), "%s never uses %s" % [path, banned])


## Every visible button on the page, in tree order: [text, global rect].
func _button_rects(page: Control) -> Array:
	var out := []
	for b in page.find_children("*", "BaseButton", true, false):
		if (b as Control).is_visible_in_tree():
			out.append([String((b as BaseButton).get("text")), (b as Control).get_global_rect()])
	return out


func test_end_state_layout_is_the_instant_layout_at_every_text_size() -> void:
	for scale in [1.0, 1.3, 1.6]:
		for screen in ["shop", "loot", "event"]:
			var scene := await _netrun(scale)
			match screen:
				"shop":
					_to_shop(scene)
				"loot":
					_to_loot(scene)
				_:
					_to_event(scene)
			await _frames(4)
			var instant := _button_rects(scene._panel)
			_live()
			scene._shown_screen = ""
			scene._show_current()
			await wait_seconds(SETTLE_WAIT)
			await _frames(2)
			PageTransition.settle(scene)
			await _frames(2)
			var live := _button_rects(scene._panel)
			assert_eq(live.size(), instant.size(), "%s at %.1f: the same controls" % [screen, scale])
			var screen_rect := Rect2(Vector2.ZERO, Vector2(1280, 720)).grow(1.0)
			for i in mini(live.size(), instant.size()):
				var want: Rect2 = instant[i][1]
				var got: Rect2 = live[i][1]
				assert_eq(live[i][0], instant[i][0], "%s at %.1f: control %d" % [screen, scale, i])
				assert_almost_eq(got.position, want.position, Vector2.ONE, "%s at %.1f: '%s' rests where it would at once" % [screen, scale, instant[i][0]])
				assert_true(screen_rect.encloses(got), "%s at %.1f: '%s' on screen" % [screen, scale, instant[i][0]])
			Motion.force_live = false
			scene.get_parent().queue_free()
			await _frames()


func test_a_settings_change_animates_nothing() -> void:
	var scene := await _netrun()
	_live()
	_to_shop(scene)
	PageTransition.settle(scene)
	await _frames()
	Settings.set_text_scale(1.3)
	await _frames()
	assert_false(PageTransition.running(scene._panel), "no page re-enters")
	assert_eq(FlightFx.active_count(scene), 0, "nothing flies")
	assert_eq(scene.hud.stats.bumping().size(), 0, "no tag bumps")
	Settings.set_language(Settings.language)
	await _frames()
	assert_false(PageTransition.running(scene._panel))


# --- HQ idle ---------------------------------------------------------------------------------------

func test_hq_idle_runs_live_and_rests_headless() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.new_campaign(1)
	await _frames()
	var jack := hq._panel.find_child("JackIn", true, false) as ZineStamp
	assert_false(jack.breathing(), "headless: JACK IN rests")
	assert_eq(jack.ring_scale, 1.0)
	_live()
	hq.panel_name = ""
	hq.show_hq()
	await _frames()
	jack = hq._panel.find_child("JackIn", true, false) as ZineStamp
	assert_true(jack.breathing(), "live: JACK IN breathes")
	var radio := hq._panel.find_child("PirateRadio", true, false) as ZineNote
	assert_true(Typing.typing(radio.label), "the pirate radio types in")
	assert_eq(radio.label.get_parsed_text().strip_edges() != "", true, "its words are all there")
	var crew := hq._panel.find_child("Roster", true, false).get_child(0) as CrewCard
	var rest := crew.polaroid.rotation_degrees
	crew.tilt_polaroid(true)
	var want := rest + Motion.amplitude(&"polaroid_tilt")
	var took := await _until(func() -> bool: return is_equal_approx(crew.polaroid.rotation_degrees, want))
	_assert_in_time(took, Motion.seconds(&"polaroid_tilt"), "the tilt")
	assert_almost_eq(crew.polaroid.rotation_degrees, rest + Motion.amplitude(&"polaroid_tilt"), 0.01, "the Polaroid tilts on hover")
	crew.tilt_polaroid(false)
	PageTransition.settle(hq)
