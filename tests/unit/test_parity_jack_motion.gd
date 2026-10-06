extends GutTest
## Parity fix (designer group ruling 2026-10-05): JACK-01 (the CONNECTING TO line keeps main's
## large destination line; its layout holds at every text size), DAEMON-01 (the Daemon tray's
## card shows the name once, its text only) and MOTION-06 (`panel_in`'s scan band: plays from
## its entry, ends with a skip, absent under reduce effects).

const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale: float = 1.0
var _reduce: bool = false


func before_all() -> void:
	_scale = Settings.text_scale
	_reduce = Settings.reduce_effects


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.scene_switching_enabled = false
	Motion.force_live = false


func after_each() -> void:
	Settings.set_text_scale(_scale)
	Settings.set_reduce_effects(_reduce)
	Fx.apply_settings()
	Motion.force_live = false


func _live() -> void:
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
	Fx.apply_settings()
	Motion.force_live = true


# --- JACK-01 ---------------------------------------------------------------------------------------

func test_the_connecting_line_lays_out_at_every_text_size() -> void:
	for s in SCALES:
		Settings.set_text_scale(s)
		Fx._destination = "Solace Biosystems"
		Fx._destination_tier = 3
		Fx._show_connect()
		var vp := Fx.get_viewport().get_visible_rect()
		var label := Fx.connect_label.get_global_rect()
		var dest := Fx.connect_dest.get_global_rect()
		assert_string_contains(Fx.connect_words(), "CONNECTING TO SOLACE BIOSYSTEMS")
		assert_lte(label.end.y, dest.position.y + 1.0, "CONNECTING TO above the name at %.1f" % s)
		assert_lte(dest.end.y, Fx.connect_bar.position.y + 0.5, "the name above the bar at %.1f" % s)
		assert_true(vp.grow(1.0).encloses(dest), "the name on screen at %.1f (%s)" % [s, dest])
		assert_true(vp.grow(1.0).encloses(Fx.connect_site.get_global_rect()), "the tier icon on screen at %.1f" % s)
		assert_gte(label.position.y, vp.position.y, "the line starts on screen at %.1f" % s)
		# The name and its icon are centred as a pair (the icon's side + gap before the name).
		var pair := Rect2(Fx.connect_site.get_global_rect().position, Vector2.ZERO).expand(dest.end)
		assert_almost_eq(pair.get_center().x, vp.get_center().x, 1.5, "centred at %.1f" % s)
		Fx._hide_connect()


# --- DAEMON-01 -------------------------------------------------------------------------------------

func test_the_daemon_card_says_the_name_once_at_every_text_size() -> void:
	RunManager.reset()
	var lookup := RunManager.lookup()
	var ids: Array[StringName] = [&"cascade"]
	var d := lookup.get_content(&"cascade") as DaemonData
	assert_not_null(d)
	for s in SCALES:
		Settings.set_text_scale(s)
		var tray := DaemonTray.new(ids, lookup, 1270.0, "Spark")
		add_child_autofree(tray)
		tray.show_card(&"cascade", false)
		await get_tree().process_frame
		await get_tree().process_frame
		var card := tray._card
		var text := card.find_child("DaemonText", true, false) as Label
		assert_eq(text.text, TextDb.t(d, "description"), "the Daemon's own words only at %.1f" % s)
		assert_false(text.text.contains("Daemon " + d.display_name), "no 'Daemon <name>' line at %.1f" % s)
		var head := card.find_child("DaemonHead", true, false) as Control
		assert_gte(head.custom_minimum_size.y, DaemonTray.HEAD_H * s - 0.5, "the head grows with the text at %.1f" % s)
		var screen := tray.get_viewport().get_visible_rect()
		assert_true(screen.grow(1.0).encloses(card.get_global_rect()), "the card on screen at %.1f (%s)" % [s, card.get_global_rect()])
		tray.queue_free()
		await get_tree().process_frame


# --- MOTION-06 -------------------------------------------------------------------------------------

func _glass_page() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var page := Control.new()
	page.size = Vector2(400, 300)
	page.position = Vector2(100, 100)
	holder.add_child(page)
	return page


func test_panel_in_plays_a_scan_band_over_its_own_entry() -> void:
	_live()
	var page := _glass_page()
	var pt := PageTransition.enter(page, PageTransition.Look.GLASS, Callable())
	assert_not_null(pt)
	var limit := BoundedWait.motion_limit([&"panel_in", &"panel_crt_roll"])
	var seen := await BoundedWait.until(get_tree(), func() -> bool:
		var b := page.get_node_or_null(^"ScanBand") as Control
		return b != null and b.visible, limit)
	assert_true(seen, "the band shows once the glass is shown")
	if seen:
		var band := page.get_node_or_null(^"ScanBand") as Control
		assert_gte(pt.progress(), PageTransition.FADE_SHARE - 0.0001, "only after the fade")
		assert_true(band.top_level)
		assert_eq(band.mouse_filter, Control.MOUSE_FILTER_IGNORE)
	await BoundedWait.until(get_tree(), func() -> bool: return not PageTransition.running(page), limit)
	await get_tree().process_frame
	assert_null(page.get_node_or_null(^"ScanBand"), "gone with the entrance")


func test_a_skip_removes_the_scan_band() -> void:
	_live()
	var page := _glass_page()
	var pt := PageTransition.enter(page, PageTransition.Look.GLASS, Callable())
	await BoundedWait.until(get_tree(), func() -> bool:
		var b := page.get_node_or_null(^"ScanBand") as Control
		return b != null and b.visible, BoundedWait.motion_limit([&"panel_in"]))
	pt.complete_motion()
	await get_tree().process_frame
	await get_tree().process_frame
	assert_null(page.get_node_or_null(^"ScanBand"), "a press ends the entrance and its band")
	assert_eq(page.modulate.a, 1.0)


func test_no_scan_band_under_reduce_effects() -> void:
	Settings.set_reduce_effects(true)
	Fx.apply_settings()
	Motion.force_live = false
	var page := _glass_page()
	var pt := PageTransition.enter(page, PageTransition.Look.GLASS, Callable())
	assert_null(pt, "reduce effects: no entrance helper (the end state at once)")
	await get_tree().process_frame
	assert_null(page.get_node_or_null(^"ScanBand"), "no band")
