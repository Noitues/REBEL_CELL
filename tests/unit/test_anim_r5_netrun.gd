extends GutTest
## Animation pass ANIM-R5 (the fifth fix batch), netrun screens (DECISIONS "Animation pass —
## ANIM-R5 netrun screens"): the event's paper as tall as its words while they type (B1), the
## subtitle paged for its band, two lines on the event and the run's end, never under its
## readable floor (B2), the run's end over the city with a verdict stamp, the operative's
## fate and why Heat rose (B3), typing within its cap and the page's focus after the words
## (B4), flights that can be followed and land with a pulse (B5), a route move whose page
## takes no press (B6), the route demo through the session (B7), the raid playout's title
## (B8), "then:" words (B9), a raid framing that stops off the tree (B10), the Modem's socket
## list that says what it is for (B11).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const EVENT := &"ev_leash_on_the_floor"
const SCALES: Array[float] = [1.0, 1.3, 1.6]
const LONG_LINE := "Keep the Heat down and bank at the first Rack. The collectors are already on their way, and they bill by the hour, so do not let them find you standing still."

var _scale: float = 1.0
var _reduce: bool = false
var _typing: bool = true


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects
	_typing = Settings.subtitle_typing


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r5"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	Engine.time_scale = 1.0
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.subtitle_typing != _typing:
		Settings.set_subtitle_typing(_typing)
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


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	Motion.force_live = true
	Settings.set_subtitle_typing(true)


func _netrun(scale: float = 1.0) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	await _frames()
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _event(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.event_id = EVENT
	run.phase = RunState.Phase.EVENT
	scene._show_current()


func _key(k: Key) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = k
	e.physical_keycode = k
	e.pressed = true
	return e


# --- B1: the event's paper ------------------------------------------------------------------------

func test_the_event_paper_holds_its_words_while_they_type_at_every_text_size() -> void:
	for scale in SCALES:
		var scene := await _netrun(scale)
		_live()
		_event(scene)
		# Typing ON: the story is still typing after the layout's frames (the clock held).
		await BoundedWait.frozen_frames(get_tree(), 3)
		var panel := scene._panel.find_child("EventPanel", true, false) as ZinePanel
		var text := scene._panel.find_child("EventText", true, false) as RichTextLabel
		assert_not_null(panel, "%.1f: the paper" % scale)
		assert_true(Typing.typing(text), "%.1f: the story is typing" % scale)
		var typing_h := text.size.y
		assert_gte(panel.size.y + 0.5, panel.content.get_combined_minimum_size().y, "%.1f: the paper is as tall as its content" % scale)
		assert_true(panel.get_global_rect().grow(1.0).encloses(text.get_global_rect()), "%.1f: the words are on the paper (%s in %s)" % [scale, text.get_global_rect(), panel.get_global_rect()])
		assert_true(Rect2(Vector2.ZERO, panel.size).grow(1.0).encloses(panel.title_rect()), "%.1f: the title is on the paper" % scale)
		assert_gt(panel.size.y, panel.title_rect().end.y + text.get_line_height(0) * 2.0, "%.1f: not a sliver: the title and two lines of words at least" % scale)
		Typing.finish_all(get_tree())
		await _frames(2)
		assert_almost_eq(typing_h, text.size.y, 1.0, "%.1f: the words kept their height while they typed" % scale)
		Settings.set_subtitle_typing(true)
		Motion.force_live = false
		await _close(scene)


# --- B2: the subtitle ------------------------------------------------------------------------------

func test_the_event_subtitle_has_two_lines_at_a_readable_size() -> void:
	for scale in SCALES:
		var scene := await _netrun(scale)
		_event(scene)
		await _frames(4)
		assert_eq(scene.subtitle_strip.lines, 2, "%.1f: the event's band holds two lines" % scale)
		assert_eq(Dialogue.dock_lines, 2, "%.1f: the dock pages two lines" % scale)
		assert_true(Dialogue.is_showing(), "%.1f: the story is said" % scale)
		var fs := Dialogue.text_label.get_theme_font_size("normal_font_size")
		assert_gte(fs, Dialogue.min_font_size(), "%.1f: the subtitle is readable (%d px; it shrank to 7)" % [scale, fs])
		assert_eq(fs, roundi(Dialogue.TEXT_FONT_SIZE * scale), "%.1f: at the text size's own font" % scale)
		assert_gte(Dialogue.min_font_size(), roundi(12 * scale), "the floor is 12 px x the text size")
		RunManager.netrun.run.phase = RunState.Phase.MAP
		scene._show_current()
		await _frames(4)
		assert_eq(scene.subtitle_strip.lines, 1, "%.1f: the route's band is one line" % scale)
		await _close(scene)


func test_a_line_paged_for_another_dock_is_paged_again_not_squeezed() -> void:
	Dialogue.clear()
	Dialogue.dock_at(Rect2(8, 2, 964, 90), 4)
	Dialogue.say(RC.Voice.DISPATCH, LONG_LINE)
	await _frames(2)
	var tall := Dialogue.current_text()
	Dialogue.dock_at(Rect2(8, 2, 964, Dialogue.band_height(1)), 1)
	await _frames(2)
	assert_eq(Dialogue.text_label.get_theme_font_size("normal_font_size"), Dialogue.TEXT_FONT_SIZE, "the page is paged again at its own size (it was squeezed into the band)")
	assert_true(tall.begins_with(Dialogue.current_text().trim_suffix(Dialogue.CONTINUED_MARK).strip_edges()) or Dialogue.current_text().length() < tall.length(), "the band shows the line's first page again")
	# Past the floor a page clips: it never shrinks under it.
	Dialogue.dock_at(Rect2(8, 2, 120, 8), 1)
	await _frames(2)
	assert_gte(Dialogue.text_label.get_theme_font_size("normal_font_size"), Dialogue.min_font_size(), "never under the floor")


# --- B3: the run's end -----------------------------------------------------------------------------

func test_the_run_end_is_a_window_over_the_city_with_a_verdict_and_reasons() -> void:
	for scale in [1.0, 1.6]:
		var scene := await _netrun(scale)
		scene.background.visible = false  # as a fight leaves it
		var s := RunManager.netrun
		s.call(&"_die")
		scene._report(s.last_events)
		scene._show_current()
		await _frames(4)
		assert_true(scene.background.visible, "%.1f: the city shows behind the run's end (it was black)" % scale)
		assert_ne(scene._panel_host.theme_type_variation, &"GlassPanel", "%.1f: no dark sheet over the city" % scale)
		var stamp := scene._panel.find_child("ResultStamp", true, false) as ForecastStamp
		assert_not_null(stamp, "%.1f: a verdict stamp" % scale)
		assert_eq(stamp.verdict, "FLATLINED")
		assert_true(stamp.resolved, "a solid ring: a result")
		assert_eq(stamp.focus_mode, Control.FOCUS_NONE)
		var fate := scene._panel.find_child("RunFate", true, false) as Label
		assert_string_contains(fate.text, "permadeath", "the loss is said to be for good")
		assert_string_contains(fate.text, s.run.operative.name)
		var why := scene._panel.find_child("HeatReasonText", true, false) as Label
		assert_string_contains(why.text, "Heat %s" % TextDb.signed(s.run.heat_gained), "the reason names the HEAT tag's number")
		assert_string_contains(why.text, "flatlined")
		var win := scene._panel.find_child("RunReport", true, false) as Control
		var r := win.get_global_rect()
		assert_almost_eq(r.get_center().x, SCREEN.get_center().x, 2.0, "%.1f: in the middle of the screen" % scale)
		assert_true(SCREEN.encloses(r), "%.1f: on screen: %s" % [scale, r])
		assert_gt(r.get_center().y, SCREEN.size.y * 0.35, "%.1f: not stuck in the top 250 px" % scale)
		assert_eq(scene.subtitle_strip.lines, 2, "the run's end says its line on two lines")
		var owner := get_viewport().gui_get_focus_owner()
		assert_true(owner is Button and win.is_ancestor_of(owner), "Back to HQ has the focus")
		await _close(scene)


func test_the_heat_reason_splits_the_flatline_from_the_route() -> void:
	RunManager.new_campaign(1)
	RunManager.start_run()
	var s := RunManager.netrun
	var script: GDScript = load("res://scripts/ui/netrun_scene.gd")
	s.run.heat_gained = 0
	assert_string_contains(script.heat_reason(s), "no Heat")
	s.call(&"_die")
	var death := s.run.heat_gained
	assert_eq(script.heat_reason(s), "Heat %s: flatlined on a run." % TextDb.signed(death))
	s.run.heat_gained = death + 2
	assert_string_contains(script.heat_reason(s), "+2 from the route")
	assert_eq(script.end_verdict(RunState.Outcome.COMPLETED), "JACKED OUT")
	assert_eq(script.end_verdict(RunState.Outcome.DIED), "FLATLINED")


# --- B4: typing within its cap; the page settles after the words -------------------------------

func test_a_subtitle_page_types_within_its_cap() -> void:
	_live()
	assert_gt(Motion.amplitude(&"dispatch_type"), 0.0, "the subtitle has a cap")
	assert_lte(Motion.amplitude(&"dispatch_type"), 1.0, "a page is whole within a second")
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, LONG_LINE)
	await _frames(1)
	var secs := Dialogue._type_page(0)
	assert_gt(secs, 0.0, "it types")
	assert_lte(secs, Motion.amplitude(&"dispatch_type") + 0.001, "within the cap (a char at a time it took %.1f s)" % (LONG_LINE.length() * Motion.seconds(&"dispatch_type")))
	Dialogue.finish_typing()


func test_a_page_takes_focus_once_its_words_are_whole_and_a_press_completes_them() -> void:
	var scene := await _netrun()
	_live()
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, LONG_LINE, 0.0, &"", false, "route")
	get_viewport().gui_release_focus()
	scene._show_map()
	assert_true(Dialogue.typing(), "the route's line types")
	assert_true(scene.page_settling(), "the page waits for the words before its focus lands")
	var owner := get_viewport().gui_get_focus_owner()
	assert_false(owner != null and scene._panel.is_ancestor_of(owner), "no choice has focus while the line types")
	# The one press: every word whole, then the focus lands.
	get_viewport().push_input(_key(KEY_SEMICOLON))
	assert_false(Dialogue.typing(), "a press shows the line whole")
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return not scene.page_settling(), BoundedWait.SLACK), "the page settles")
	# The focus is given deferred (UiFocus.focus_first): it lands within a few frames.
	await BoundedWait.until(get_tree(), func() -> bool:
		var o := get_viewport().gui_get_focus_owner()
		return o != null and scene._panel.is_ancestor_of(o), BoundedWait.SLACK)
	owner = get_viewport().gui_get_focus_owner()
	assert_true(owner != null and scene._panel.is_ancestor_of(owner), "the focus lands on the page")
	# Unpressed, the wait ends by itself within the cap.
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, LONG_LINE, 0.0, &"", false, "route")
	scene._show_map()
	assert_true(scene.page_settling())
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return not scene.page_settling(), BoundedWait.motion_limit([&"dispatch_type"], Motion.amplitude(&"dispatch_type"))), "settled once the line is typed")
	await _close(scene)


# --- B5: flights ----------------------------------------------------------------------------------

func test_a_bought_card_flies_long_enough_and_lands_with_a_pulse() -> void:
	assert_gte(Motion.seconds(&"buy_fly"), 0.6, "a flight lasts long enough to follow")
	assert_gte(Motion.seconds(&"loot_pick"), 0.6)
	assert_gte(Motion.amplitude(&"buy_fly"), 0.5, "it arrives large enough to see")
	assert_gt(Motion.amplitude(&"flight_land_pulse"), Motion.amplitude(&"sticky_bump"), "the landing pulse is bigger than a value's bump")
	var scene := await _netrun()
	RunManager.netrun.run.cycles = 300
	RunManager.netrun._open_shop()
	scene._show_current()
	await _frames(3)
	_live()
	scene.buy("cards", 0)
	assert_gt(FlightFx.active_count(scene), 0, "the card flies")
	assert_true(scene.hud.stats.landing().is_empty(), "no pulse before it lands")
	assert_true(await BoundedWait.until(get_tree(), func() -> bool: return FlightFx.active_count(scene) == 0, BoundedWait.motion_limit([&"buy_fly", &"sold_stamp"])), "it lands")
	assert_true(scene.hud.stats.landing().has("CARDS"), "CARDS pulses where the card went")
	await _close(scene)


# --- B6: the route move ---------------------------------------------------------------------------

func test_a_press_during_a_route_move_ends_it_and_is_never_refused() -> void:
	var scene := await _netrun()
	_live()
	var s := RunManager.netrun
	var to: StringName = s.available_nodes()[0]
	scene.enter_node(to)
	if not scene._travelling:
		fail_test("the move did not play on the route map")
		await _close(scene)
		return
	var owner := get_viewport().gui_get_focus_owner()
	assert_false(owner != null and scene._panel.is_ancestor_of(owner), "no route choice has focus during the move")
	# A choice on the page (the new ones are shown) pressed with accept: kept by the move.
	var row: Node = scene._panel.find_child("RouteNodes", true, false)
	var b: Button = null
	for c in row.get_children():
		if c is Button and (c as Button).visible and not c.is_queued_for_deletion():
			b = c as Button
			break
	assert_not_null(b, "the new choices are listed")
	b.grab_focus()
	var phase := s.run.phase
	get_viewport().push_input(_key(KEY_ENTER))
	await _frames(2)
	assert_false(scene._travelling, "the press ends the move")
	for e in s.last_events:
		assert_ne(String(e.get("type", "")), "refused", "the press never reached the session: %s" % e)
	assert_eq(s.run.phase, phase, "and did nothing else")
	assert_eq(s.run.current_node_id, to)
	assert_true(scene.route_keep().is_empty() or not scene._travelling, "the keep list only matters mid-move")
	await _close(scene)


# --- B7: the route demo ---------------------------------------------------------------------------

func test_the_route_demo_reaches_its_first_node_through_the_session() -> void:
	RunManager.new_campaign(1)
	RunManager.start_run()
	var s := RunManager.netrun
	var first: StringName = s.available_nodes()[0]
	var script: GDScript = load("res://scripts/ui/netrun_scene.gd")
	assert_true(script.demo_first_node(s), "the demo run stands on its first node, the map open")
	assert_eq(s.run.current_node_id, first)
	assert_eq(s.run.visited, [first] as Array[StringName])
	assert_eq(s.run.phase, RunState.Phase.MAP)
	var src := FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd")
	assert_false(src.contains("s.run.current_node_id = "), "the view never sets the run's node")
	assert_false(src.contains("s.run.visited.append"), "nor its visited list")


# --- B8-B11 ---------------------------------------------------------------------------------------

func test_the_raid_playout_has_its_own_title_and_screen() -> void:
	var scene := await _netrun()
	var page := Control.new()
	scene._set_panel(page, false, scene.RAID_PLAYOUT_SCREEN)
	assert_eq(scene.hud._title, tr("NETRUN // RAID"), "not NETRUN // ROUTE")
	scene._show_current()
	assert_true(scene.entering, "the route after the playout enters as a new screen")
	assert_eq(scene.hud._title, tr("NETRUN // ROUTE"))
	await _close(scene)


func test_then_icons_carry_their_words() -> void:
	var scene := await _netrun()
	var row: Control = scene._ahead_row(0, [StatIcon.SHOP, StatIcon.ELITE], 0)
	add_child_autofree(row)
	var shop := row.find_child("Ahead_%s" % StatIcon.SHOP, true, false)
	assert_not_null(shop)
	assert_eq((shop.get_node("Word") as Label).text, tr("Shop"), "then: [bag] Shop")
	assert_eq((row.find_child("Ahead_%s" % StatIcon.ELITE, true, false).get_node("Word") as Label).text, tr("Elite fight"))
	assert_true(row is HFlowContainer, "a long row wraps in its window")
	var csv := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	for key in ["Chips go into:", "JACKED OUT", "HOME FELL", "Heat %s: flatlined on a run."]:
		assert_true(csv.contains(key), "%s is exported for translation" % key)
	await _close(scene)


func test_the_raid_framing_stops_when_the_scene_left_the_tree() -> void:
	var scene := await _netrun()
	var holder := scene.get_parent()
	scene._raid_map_area = Control.new()
	scene.add_child(scene._raid_map_area)
	var anchor: Vector2 = scene.background.city.focus_anchor
	scene._frame_raid_map()
	assert_true(scene._raid_map_framing)
	holder.remove_child(scene)
	await _frames(2)
	assert_false(scene._raid_map_framing, "the wait ended")
	assert_eq(scene.background.city.focus_anchor, anchor, "and framed nothing off the tree")
	holder.add_child(scene)
	await _close(scene)


func test_the_socket_list_says_what_it_is_for() -> void:
	for scale in [1.0, 1.6]:
		var scene := await _netrun(scale)
		RunManager.netrun._open_shop()
		scene._show_current()
		await _frames(3)
		var row := scene._panel.find_child("SocketRow", true, false) as Control
		if RunManager.netrun.run.shop.get("firmware", []).is_empty():
			assert_null(row)
			await _close(scene)
			continue
		assert_not_null(row, "the socket list has a row")
		assert_eq((row.find_child("SocketWord", true, false) as Label).text, tr("Chips go into:"))
		var pick := row.find_child("SocketPick", true, false) as OptionButton
		assert_true(pick.get_item_text(0).begins_with(tr("Slot %d: %s%s").split(" ")[0]), "items name the slot: %s" % pick.get_item_text(0))
		assert_string_contains(pick.tooltip_text, "slot", "its tooltip explains it")
		var win := row.get_parent()
		while win != null and not (win is TerminalWindow):
			win = win.get_parent()
		assert_true((win as Control).get_global_rect().grow(1.0).encloses(row.get_global_rect()), "%.1f: inside MICROCHIPS" % scale)
		await _close(scene)
