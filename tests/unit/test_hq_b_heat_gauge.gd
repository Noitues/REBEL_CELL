extends GutTest
## HQ-B (a) (M14, HQ redesign direction B; designer rulings Q1 / Q2 2026-10-05): the HEAT
## gauge is the top bar's first slot (a shared kit piece, HeatGauge + HeatGaugeLook); at the
## HQ it is a button with a caret that drops the Heat terminal (rules in force, next
## thresholds, sinks, SCRUB HEAT at its price); read-only it has no SCRUB. The WANTED poster
## and CELL STATUS are gone from the HQ; their motion plays on the tag (it is a HeatPoster).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	RunManager.save_slot = "gut_test_hq_b_heat"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	HeatPoster._seen_heat.clear()


func after_each() -> void:
	Motion.force_live = false
	Settings.set_text_scale(_text_scale_before)
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _hq() -> Control:
	var hq: Control = add_child_autofree(load(HQ).instantiate())
	await _frames()
	return hq


func test_the_gauge_takes_the_top_bars_first_slot_at_the_hq() -> void:
	var c := RunManager.campaign
	c.heat = 58
	var hq := await _hq()
	var bar: HudBar = hq.hud
	var gauge := bar.heat_gauge
	assert_true(gauge.is_visible_in_tree(), "the gauge shows at the HQ")
	assert_eq(gauge.get_index(), 0, "first in the bar's row")
	assert_false(bar.title_box.visible, "no title at the HQ (Q6): the slot is the gauge's")
	assert_true(gauge.interactive, "at the HQ it is a button (caret)")
	assert_eq(gauge.heat, 58)
	assert_eq(gauge.marks, HeatRules.band_levels(c, RunManager.config()), "the band levels of this campaign")
	assert_eq(gauge.band_word(), tr(HeatPoster.BAND_WORDS[HeatPoster.band_of(58, gauge.marks)]).to_upper(), "the band word is printed")
	for it in bar.stats.items:
		assert_ne(String(it[0]), TextDb.mark("HEAT"), "no second Heat tag in the bar")
	assert_lt(gauge.get_global_rect().position.x, bar.stats.get_global_rect().position.x, "left of the stat tags")


func test_no_wanted_poster_and_no_cell_status_at_the_hq() -> void:
	var hq := await _hq()
	for n in hq._panel.find_children("*", "", true, false):
		assert_false(n is HeatPoster, "no WANTED poster on the page (Q1)")
	assert_null(hq._panel.find_child("CellStatus", true, false), "no CELL STATUS badges (Q1)")
	assert_null(hq._panel.find_child("ScrubHeat", true, false), "SCRUB HEAT left the deck menu for the Heat terminal")


func test_pressing_the_gauge_drops_the_heat_terminal_and_scrub_matches_its_preview() -> void:
	var c := RunManager.campaign
	var cfg := RunManager.config()
	c.heat = 58
	c.schematics = 200
	var hq := await _hq()
	hq.hud.heat_gauge.pressed.emit()
	await _frames()
	var term: HeatTerminal = hq.heat_terminal
	assert_not_null(term, "the terminal drops")
	for row in ["InForce", "Next", "Sinks"]:
		assert_not_null(term.find_child(row, true, false), "row %s" % row)
	var in_force := (term.find_child("InForce", true, false).get_node("Value") as Label).text
	for m in HeatRules.active_modifiers(c, cfg):
		assert_string_contains(in_force, HeatTerminal.modifier_text(m), "every rule in force is listed")
	assert_true(term.get_global_rect().position.y >= hq.hud.heat_gauge.get_global_rect().end.y, "it drops under the tag")
	assert_not_null(term.scrub, "SCRUB HEAT at the HQ")
	var amount := HeatRules.scaled_delta(c, -cfg.heat_purchase_amount, cfg)
	var price := CampaignRules.heat_purchase_price(c, cfg)
	assert_string_contains(term.scrub.text, TextDb.signed(amount), "the amount shown")
	assert_string_contains(term.scrub.line, str(price), "the price shown")
	var heat_before := c.heat
	var sch_before := c.schematics
	term.scrub.pressed.emit()
	await _frames()
	assert_eq(c.heat, heat_before + amount, "preview == result: Heat")
	assert_eq(c.schematics, sch_before - price, "preview == result: price")
	assert_not_null(hq.heat_terminal, "the terminal opens again on the new numbers")
	assert_true(is_instance_valid(hq.heat_terminal) and hq.heat_terminal.scrub != null)
	hq.toggle_heat_terminal()
	await _frames()
	assert_null(hq.heat_terminal, "pressed again it folds away")


func test_the_heat_key_and_the_pads_view_open_it_and_esc_closes_it() -> void:
	var hq := await _hq()
	var key := InputEventAction.new()
	key.action = HeatGauge.OPEN_ACTION
	key.pressed = true
	hq._unhandled_input(key)
	assert_not_null(hq.heat_terminal, "H opens it")
	var esc := InputEventAction.new()
	esc.action = &"ui_cancel"
	esc.pressed = true
	hq.heat_terminal._input(esc)
	await _frames()
	assert_null(hq.heat_terminal, "Esc / B closes it")
	var view := InputEventJoypadButton.new()
	view.button_index = JOY_BUTTON_BACK
	view.pressed = true
	hq._unhandled_input(view)
	assert_not_null(hq.heat_terminal, "the pad's View opens it")
	hq.close_heat_terminal()


func test_a_read_only_terminal_has_no_scrub() -> void:
	var c := RunManager.campaign
	var t := HeatTerminal.new(c, RunManager.config(), true)
	add_child_autofree(t)
	assert_null(t.scrub, "in a run the terminal only reads (Q2)")
	assert_null(t.find_child("ScrubHeat", true, false))
	assert_not_null(t.find_child("ReadOnly", true, false), "it says where Heat is scrubbed")


func test_the_gauge_fits_and_stays_a_drawn_object_at_every_text_scale() -> void:
	for s in SCALES:
		Settings.set_text_scale(s)
		var hq := await _hq()
		var g: HeatGauge = hq.hud.heat_gauge
		var want := (HeatGauge.LOOK.size * clampf(s, 1.0, HeatGauge.LOOK.scale_max)).ceil()
		assert_eq(g.custom_minimum_size, want, "x%.1f: grows with the text up to x%.1f" % [s, HeatGauge.LOOK.scale_max])
		assert_true(hq.get_global_rect().encloses(g.get_global_rect()), "x%.1f: on screen" % s)
		assert_true(hq.hud.get_global_rect().encloses(g.get_global_rect()), "x%.1f: inside the bar" % s)
		assert_false(g.get_global_rect().intersects(hq.hud.stats.get_global_rect()), "x%.1f: clear of the stat tags" % s)
		var r := g.band_label_rect()
		assert_true(Rect2(Vector2.ZERO, g.size).encloses(r), "x%.1f: the band word inside the tag" % s)
		hq.toggle_heat_terminal()
		await _frames()
		assert_true(hq.get_global_rect().encloses(hq.heat_terminal.get_global_rect()), "x%.1f: the terminal on screen (%s in %s)" % [s, hq.heat_terminal.get_global_rect(), hq.get_global_rect()])
		hq.close_heat_terminal()
		hq.free()


func test_the_posters_motion_plays_on_the_tag_and_completes_with_one_press() -> void:
	Motion.force_live = true
	var g := HeatGauge.new()
	add_child_autofree(g)
	g.size = g.custom_minimum_size
	assert_true(g.is_in_group(MotionSkip.GROUP), "the tag joins the one press rule")
	var marks: Array[int] = [25, 50, 75, 100]
	g.set_heat(10, 100, marks)
	g.set_heat(60, 100, marks)
	await BoundedWait.frozen_frames(get_tree(), 1)
	assert_true(g.motion_running(), "the number rolls through its thresholds on the tag")
	g.complete_motion()
	assert_false(g.motion_running())
	assert_eq(roundi(g.shown_heat), 60)
	assert_eq(g._banner_at, 50, "the crossing's banner shows on the tag")
	assert_true(Rect2(Vector2.ZERO, g.size).grow(1.0).encloses(g.banner_rect()), "the banner sits in the tag")


func test_under_reduce_effects_the_tag_is_at_its_end_state() -> void:
	Settings.set_reduce_effects(true)
	var g := HeatGauge.new()
	add_child_autofree(g)
	var marks: Array[int] = [25, 50, 75, 100]
	g.set_heat(10, 100, marks)
	g.set_heat(60, 100, marks)
	await _frames(2)
	assert_eq(roundi(g.shown_heat), 60, "the number at once")
	assert_eq(g.number_scale, 1.0)
	Settings.set_reduce_effects(false)
