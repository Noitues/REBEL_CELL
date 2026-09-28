extends GutTest
## Animation pass ANIM-R1 (the first fix batch), campaign and screens: a second JACK IN,
## drop or scene press during a jack does nothing (one run, one scene change; the rules
## refuse a launch over a run under way); a motion entry switched off is its end state at
## once (the jack, the Heat pulse and creep, SAVED, the map ring); the raid playout reads
## at fight scale and still ends on the resolved campaign; territory changes leave a
## lasting mark; the Heat pulse is small and the number and banner carry it; the route's
## choice labels follow the move; the jack lands on a built screen; the event's choices
## wait for its words; nothing is cut; the Modem keeps its tiles in place after a buy.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _reduce: bool
var _speed: float
var _scale: float
var _cfg: CampaignConfigData
var _lookup: ContentLookup
var _scene_asks: Array[String] = []


func before_all() -> void:
	_cfg = CombatFixture.config()
	_lookup = GridFixture.lookup()


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_speed = Motion.speed
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim_r1"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	_scene_asks.clear()
	SignalBus.scene_change_requested.connect(_on_scene_ask)


func after_each() -> void:
	SignalBus.scene_change_requested.disconnect(_on_scene_ask)
	Motion.use_config(null)
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	Fx.apply_settings()
	Motion.force_live = false
	Motion.speed = _speed
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _on_scene_ask(path: String) -> void:
	_scene_asks.append(path)


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _seconds(s: float) -> void:
	await get_tree().create_timer(s).timeout


func _scene(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _live() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()


## A copy of the motion table with entry `id` switched off (the loaded table never changes).
func _switch_off(ids: Array) -> void:
	var dup: UiMotionData = Motion.config().duplicate(true)
	for id in ids:
		dup.find(StringName(id)).enabled = false
	Motion.use_config(dup)


## The HQ with a campaign like --demo-raid: the first Site cleared and claimed, an asset on
## it, a raid pending.
func _hq_raid() -> Control:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var grid_data := RunManager.corporation.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	return hq


# --- M1: one jack, one run, one scene change -----------------------------------------------------

func test_the_rules_refuse_a_launch_while_a_run_is_under_way() -> void:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var op := c.living_operatives()[0]
	var cls := RunManager.lookup().get_content(op.class_id) as ClassData
	var site := RunManager.launchable_sites()[0]
	assert_eq(CampaignRules.launch_error(c, corp, RunManager.config(), op, cls, site), "", "free to launch")
	assert_eq(CampaignRules.launch_error(c, corp, RunManager.config(), op, cls, site, true), CampaignRules.RUN_IN_PROGRESS,
		"refused while a run is under way (pure rule)")
	assert_true(hq.launch(site.id, op.id), "the first JACK IN starts the run")
	var run := RunManager.netrun
	var after := c.state_hash()
	assert_ne(RunManager.launch_error(op.id, site.id), "", "RunManager passes the run under way")
	assert_false(hq.launch(site.id, op.id), "a second JACK IN starts nothing")
	assert_same(RunManager.netrun, run, "the first run stays")
	assert_eq(c.state_hash(), after, "the campaign is unchanged by the second press")
	await _close(hq)


func test_a_second_press_during_the_jack_does_nothing() -> void:
	_live()
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var c := RunManager.campaign
	var op := c.living_operatives()[0]
	var site := RunManager.launchable_sites()[0]
	var switched := [0]
	var second := [0]
	Fx.jack_in(func() -> void: switched[0] += 1)
	assert_true(Fx.transitioning(), "the jack runs")
	assert_true(RunManager.scene_change_pending())
	assert_eq(Fx.jack_cover.mouse_filter, Control.MOUSE_FILTER_STOP, "the cover takes the mouse while jacking")
	var before := c.state_hash()
	var asks := _scene_asks.size()
	assert_false(hq.launch(site.id, op.id), "JACK IN during the jack does nothing")
	assert_null(RunManager.netrun, "no run started")
	RunManager.go_to_netrun()
	RunManager.go_to_hq()
	RunManager.go_to_title()
	assert_eq(_scene_asks.size(), asks, "no second scene change is asked for")
	Fx.jack_in(func() -> void: second[0] += 1)
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	Fx._input(click)
	assert_true(get_viewport().is_input_handled(), "a press during the jack reaches no screen")
	while Fx.transitioning():
		await get_tree().process_frame
	assert_eq(switched[0], 1, "the jack switched once")
	assert_eq(second[0], 0, "the jack asked for during it never switches")
	assert_eq(c.state_hash(), before, "the campaign is unchanged")
	assert_eq(Fx.jack_cover.mouse_filter, Control.MOUSE_FILTER_IGNORE, "input comes back after")
	await _close(hq)


func test_netrun_leave_buttons_ask_once_during_the_jack() -> void:
	_live()
	var run := _scene(NETRUN)
	run.new_campaign(1)
	run.start_run(1)
	Fx.jack_out(func() -> void: pass)
	var asks := _scene_asks.size()
	var saved := RunManager.netrun
	run.save_and_quit()
	run.finish_run()
	assert_eq(_scene_asks.size(), asks, "Save & quit / Go to HQ during the jack ask for nothing")
	assert_same(RunManager.netrun, saved, "the run is not cleared by a press during the jack")
	while Fx.transitioning():
		await get_tree().process_frame
	await _close(run)


func test_a_saved_run_is_resumed_from_the_hq_jack_in() -> void:
	var hq := _scene(HQ)
	hq.new_campaign(1)
	var op := RunManager.campaign.living_operatives()[0]
	var site := RunManager.launchable_sites()[0]
	assert_true(hq.launch(site.id, op.id))
	var run := RunManager.netrun
	hq.show_hq()
	await _frames(2)
	var asks := _scene_asks.size()
	var jack := hq._panel.find_child("JackIn", true, false) as BaseButton
	jack.pressed.emit()
	assert_eq(_scene_asks.size(), asks + 1, "JACK IN goes back into the run left")
	assert_eq(_scene_asks[_scene_asks.size() - 1], RunManager.NETRUN_SCENE)
	assert_same(RunManager.netrun, run, "the same run")
	await _close(hq)


# --- M3: an entry switched off is its end state at once --------------------------------------------

func test_jack_in_switched_off_switches_at_once() -> void:
	_live()
	_switch_off([&"jack_in"])
	var seen := []
	Fx.jack_in(func() -> void: seen.append(Fx.jack_cover.visible))
	assert_eq(seen, [false], "switched at once, no cover")
	assert_false(Fx.transitioning())


func test_heat_pulse_creep_and_ring_switched_off_show_nothing() -> void:
	_live()
	_switch_off([&"heat_pulse", &"net_creep", &"select_ring_pulse"])
	var n := Fx.heat_pulses
	Fx.heat_pulse(-1.0, Palette.CORP_SOLACE)
	assert_eq(Fx.heat_pulses, n + 1, "still counted")
	assert_false(Fx.distortion.visible, "no distortion")
	assert_false(Fx.creep_rect.visible, "no creep")
	var overlay := CityMapOverlay.new()
	assert_eq(overlay.pulse_amplitude(), 0.0, "the selection ring holds still")
	overlay.free()


func test_saved_switched_off_shows_still_then_goes_at_once() -> void:
	_live()
	_switch_off([&"saved_stamp"])
	await Fx.show_saved()
	assert_eq(Fx.saved_label.modulate.a, 1.0, "SAVED shows")
	await _seconds(Motion.delay_of(&"saved_stamp") * 0.5)
	assert_eq(Fx.saved_label.modulate.a, 1.0, "no fade: it holds still")
	await _seconds(Motion.delay_of(&"saved_stamp") + Motion.seconds(&"saved_stamp") + 0.2)
	assert_eq(Fx.saved_label.modulate.a, 0.0, "then goes at once")


func test_no_inline_fractions_are_left_in_fx() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/autoload/fx.gd")
	for inline in ["else 0.0) * 0.5", "seconds(CREEP_MOTION) * 0.5", "seconds * 0.5", "JACK_ARRIVE_SHARE"]:
		assert_false(src.contains(inline), "no inline share of an entry's time in Fx: %s" % inline)
	var fx_layer := FileAccess.get_file_as_string("res://scripts/ui/kit/raid_fx_layer.gd")
	assert_false(fx_layer.contains("dur * 0.5"), "the raid hit is timed by the table, not half a trace")
	var overlay := FileAccess.get_file_as_string("res://scripts/ui/kit/city_map_overlay.gd")
	assert_false(overlay.contains("PULSE_AMPLITUDE") or overlay.contains("PULSE_SPEED"), "the ring's pulse is in the table")
	for id in [&"net_creep_recede", &"jack_arrive", &"jack_arrival_wait", &"select_ring_pulse"]:
		assert_true(UiMotionData.REQUIRED_IDS.has(id), "%s is required" % id)
		assert_true(Motion.has(id), "%s is in the table" % id)
