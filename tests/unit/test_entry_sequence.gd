extends GutTest
## NA-25: the street entry's beat table (the animatic's times, order, reverse), its REVEAL / MARK staging, the skip rule and the
## instant end state. EntryCover runs over a stub view that records the calls; the street view itself is covered by the NA-23 tests.

const FRAME := 1.0 / 60.0


## A StreetRouteView that only records what the cover asks of it.
class StubView extends StreetRouteView:
	var calls: Array[String] = []
	var last_u := -1.0

	func entry_begin() -> void:
		calls.append("begin")

	func entry_dive(u: float) -> void:
		_note("dive", u)

	func entry_reveal(s: float, total: float) -> void:
		_note("reveal", s / maxf(total, 0.0001))

	func entry_mark(s: float) -> void:
		_note("mark", s)

	func entry_zoom(u: float) -> void:
		_note("zoom", u)

	func entry_end() -> void:
		calls.append("end")

	func _note(what: String, u: float) -> void:
		if calls.is_empty() or calls[calls.size() - 1] != what:
			calls.append(what)
		last_u = u


var _live_before := false


func before_each() -> void:
	_live_before = Motion.force_live
	Motion.force_live = true


func after_each() -> void:
	Motion.force_live = _live_before


func _cover(reverse: bool) -> Array:
	var view := StubView.new()
	add_child_autofree(view)
	var cover := EntryCover.new()
	add_child_autofree(cover)
	watch_signals(cover)
	cover.start(view, reverse)
	return [cover, view]


func _run(cover: EntryCover, seconds: float) -> void:
	var t := 0.0
	while t < seconds and cover.playing:
		cover._process(0.05)
		t += 0.05


# --- The table ----------------------------------------------------------------------------------------------

func test_beats_match_the_animatic_within_a_frame() -> void:
	var tbl := EntryBeats.table(EntryBeats.HQ_BEATS + EntryBeats.STREET_BEATS, false, false)
	# PIPELINE_SPEC 10, animatic seconds relative to the JACK IN press (7.35): beat -> [start, end].
	var want := {&"terminal": [0.0, 1.40], &"rain": [1.40, 2.65], &"collapse": [2.65, 3.10], &"dive": [3.10, 6.10],
		&"reveal": [6.10, 9.74], &"mark": [9.74, 10.74], &"mark_hold": [10.74, 11.54], &"zoom": [11.54, 12.54], &"zoom_settle": [12.54, 13.04]}
	assert_eq(tbl.size(), want.size())
	for row in tbl:
		var w: Array = want[row["beat"]]
		assert_almost_eq(float(row["start"]), float(w[0]), FRAME, "%s starts on the animatic" % row["beat"])
		assert_almost_eq(float(row["end"]), float(w[1]), FRAME, "%s ends on the animatic" % row["beat"])


func test_dive_lasts_three_seconds_and_the_order_is_fixed() -> void:
	var tbl := EntryBeats.table(EntryBeats.STREET_BEATS, false, false)
	var ids: Array = []
	for row in tbl:
		ids.append(row["beat"])
	assert_eq(ids, [&"dive", &"reveal", &"mark", &"mark_hold", &"zoom", &"zoom_settle"])
	assert_almost_eq(float(tbl[0]["end"]) - float(tbl[0]["start"]), 3.0, FRAME)


func test_reverse_plays_the_same_beats_backwards_in_the_same_total_time() -> void:
	var fwd := EntryBeats.table(EntryBeats.STREET_BEATS, false, false)
	var rev := EntryBeats.table(EntryBeats.STREET_BEATS, true, false)
	assert_almost_eq(EntryBeats.total(rev), EntryBeats.total(fwd), 0.0001)
	assert_eq(rev[0]["beat"], &"zoom_settle")
	assert_eq(rev[rev.size() - 1]["beat"], &"dive")
	for i in fwd.size():
		var mirror: Dictionary = rev[fwd.size() - 1 - i]
		assert_eq(mirror["beat"], fwd[i]["beat"])
		assert_almost_eq(float(mirror["end"]) - float(mirror["start"]), float(fwd[i]["end"]) - float(fwd[i]["start"]), 0.0001)
	var total := EntryBeats.total(fwd)
	assert_almost_eq(EntryBeats.forward_time(total, 0.0, true), total, 0.0001, "reverse starts on the end state")
	assert_almost_eq(EntryBeats.forward_time(total, total, true), 0.0, 0.0001, "and ends on the HQ page")
	assert_almost_eq(EntryBeats.forward_time(total, 2.0, false), 2.0, 0.0001)


func test_at_finds_the_beat_and_its_share() -> void:
	var tbl := EntryBeats.table(EntryBeats.STREET_BEATS, false, false)
	var s := EntryBeats.at(tbl, 1.5)
	assert_eq(s["beat"], &"dive")
	assert_almost_eq(float(s["u"]), 0.5, 0.0001)
	assert_true(bool(EntryBeats.at(tbl, 99.0)["done"]))
	var empty: Array[Dictionary] = []
	assert_true(bool(EntryBeats.at(empty, 0.0)["done"]), "an empty table is done")


func test_nothing_animates_headless_so_every_beat_takes_no_time() -> void:
	Motion.force_live = false
	if DisplayServer.get_name() != "headless":
		pending("only meaningful headless")
		return
	var tbl := EntryBeats.table(EntryBeats.STREET_BEATS)
	assert_eq(EntryBeats.total(tbl), 0.0)


# --- REVEAL and MARK staging --------------------------------------------------------------------------------

func test_reveal_writes_links_then_raises_rooms_layer_by_layer() -> void:
	var total := Motion.seconds(&"entry_reveal")
	var layers := 5
	assert_eq(EntryBeats.write_k(1, layers, total, 0.0), 0.0, "nothing before the first wall")
	assert_eq(EntryBeats.up_k(layers, layers, total, total), 1.0, "the last layer is up when the beat ends")
	var prev_start := -1.0
	for layer in range(1, layers + 1):
		var lt := EntryBeats.layer_times(layer, layers, total)
		assert_gt(float(lt["write_start"]), prev_start, "layers follow in order")
		assert_almost_eq(float(lt["up_start"]), float(lt["write_end"]), 0.0001, "rooms rise after the links write on")
		prev_start = float(lt["write_start"])
	assert_almost_eq(float(EntryBeats.layer_times(1, layers, total)["write_start"]), Motion.seconds(&"entry_reveal_lead"), 0.0001)
	assert_almost_eq(float(EntryBeats.layer_times(layers, layers, total)["up_end"]), total, 0.0001)


func test_mark_slaps_in_order_then_rings_numbers_and_target() -> void:
	assert_eq(EntryBeats.slap_scale(3, 0.0), 0.0, "a later sticker is not there yet")
	assert_almost_eq(EntryBeats.slap_scale(0, 0.0), Motion.amplitude(&"entry_mark_slap"), 0.0001, "the first slaps on at its start scale")
	assert_almost_eq(EntryBeats.slap_scale(0, 5.0), 1.0, 0.0001, "and settles at 1")
	assert_false(EntryBeats.rings_on(0.0))
	assert_true(EntryBeats.rings_on(0.2))
	assert_false(EntryBeats.numbers_on(0.2))
	assert_true(EntryBeats.numbers_on(0.5))
	assert_false(EntryBeats.target_on(0.5))
	assert_true(EntryBeats.target_on(0.7), "the red TARGET circle is last")


# --- The cover ----------------------------------------------------------------------------------------------

func test_the_cover_plays_the_beats_in_order_and_ends_on_choose() -> void:
	var made := _cover(false)
	var cover: EntryCover = made[0]
	var view: StubView = made[1]
	assert_true(cover.playing)
	_run(cover, 60.0)
	assert_false(cover.playing)
	assert_eq(view.calls, ["begin", "dive", "reveal", "mark", "zoom", "end"] as Array[String])
	assert_signal_emitted(cover, "entry_finished")
	assert_signal_not_emitted(cover, "entry_skipped")
	assert_almost_eq(cover.total_seconds(), EntryBeats.total(EntryBeats.table(EntryBeats.STREET_BEATS, false, false)), FRAME)


func test_one_press_reaches_the_same_end_state_at_once_at_any_beat() -> void:
	for at in [0.5, 4.0, 8.0, 9.5]:
		var made := _cover(false)
		var cover: EntryCover = made[0]
		var view: StubView = made[1]
		_run(cover, at)
		assert_true(cover.playing, "still playing at %s s" % at)
		cover.skip()
		assert_false(cover.playing, "a skip ends it in the same frame")
		assert_eq(view.calls[view.calls.size() - 1], "end", "the end state is entered")
		assert_eq(view.calls.count("end"), 1)
		assert_signal_emitted(cover, "entry_skipped")
		assert_signal_emitted(cover, "entry_finished")


func test_a_press_through_motion_skip_ends_it_too() -> void:
	var made := _cover(false)
	var cover: EntryCover = made[0]
	assert_true(cover.is_in_group(MotionSkip.GROUP), "the cover is registered with MotionSkip")
	assert_true(MotionSkip.running(cover).has(cover))
	MotionSkip.complete_all(cover)
	assert_false(cover.playing)


func test_jack_out_reads_the_timeline_backwards_then_holds_the_select_state() -> void:
	var made := _cover(true)
	var cover: EntryCover = made[0]
	var view: StubView = made[1]
	_run(cover, 60.0)
	assert_eq(view.calls, ["begin", "zoom", "mark", "reveal", "dive"] as Array[String], "the beats in reverse; no CHOOSE state on the way out")
	assert_signal_emitted(cover, "entry_finished")
	assert_almost_eq(cover.elapsed(), cover.total_seconds() + Motion.seconds(&"entry_select_hold"), FRAME * 3.0, "the select hold follows")


func test_a_skip_during_the_jack_out_also_skips_the_hold() -> void:
	var made := _cover(true)
	var cover: EntryCover = made[0]
	_run(cover, cover.total_seconds() + 0.1)
	assert_true(cover.playing, "inside the select hold")
	cover.skip()
	assert_false(cover.playing)
	assert_signal_emitted(cover, "entry_skipped")
	assert_signal_emitted(cover, "entry_finished")


func test_with_no_animation_the_entry_ends_at_once_with_nothing_pending() -> void:
	Motion.force_live = false
	if DisplayServer.get_name() != "headless":
		pending("headless only")
		return
	var made := _cover(false)
	var cover: EntryCover = made[0]
	var view: StubView = made[1]
	assert_false(cover.playing, "no timer: the end state at once")
	assert_eq(view.calls, ["begin", "end"] as Array[String])
	assert_signal_emitted(cover, "entry_finished")


func test_the_skip_key_is_space_behind_the_input_map() -> void:
	assert_eq(Settings.RUNTIME_ACTIONS[&"route_skip"], KEY_SPACE)
	Settings.add_runtime_actions()
	assert_true(InputMap.has_action(&"route_skip"))
	assert_eq(Settings.key_for(&"route_skip"), KEY_SPACE)
