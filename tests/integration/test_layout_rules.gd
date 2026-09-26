extends GutTest
## Style rules (M4 acceptance): the combat, Grid and HQ screens follow STYLE_GUIDE
## component rules that can be checked automatically: zine elements never cover the
## wheels; player wheel cell_pink, enemy wheels corp colour; the three worlds are
## present per screen; performance budget for the core.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


## Instantiates `path` inside a 1280x720 holder (the design canvas, TECH_SPEC 10).
func _open(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	return scene


func _layout(_scene: Control) -> void:
	await wait_process_frames(2)


func test_combat_zine_elements_never_cover_the_wheels() -> void:
	var scene := _open(COMBAT)
	await _layout(scene)
	assert_eq(scene.layout_violations(), [], "no zine element or card over a wheel")
	assert_eq(scene.player_wheel_color(), Palette.CELL_PINK, "player wheel is cell_pink")
	for c in scene.enemy_wheel_colors():
		assert_eq(c, Palette.CORP_SOLACE, "enemy wheels use the corporation colour")
	assert_true(scene.background is WireframeBackground, "combat arena is wireframe")
	for name in ["Polaroid", "RamTally", "HeatPoster", "SendIt"]:
		assert_not_null(scene.find_child(name, true, false), "%s present" % name)
	# Combat pass (owner's direction): no log strip or preview wall on screen; what will
	# resolve is a tag over each spinner; actions are stickers around the player spinner;
	# SEND IT is drip lettering, not a stamp.
	assert_false(scene.log_note.is_visible_in_tree(), "no log strip")
	assert_false(scene.preview_note.is_visible_in_tree(), "no preview wall")
	assert_ne(String(scene._player_view.intent.get("text", "")), "", "player spinner shows what resolves")
	for v in scene._enemy_views.values():
		assert_ne(String(v.intent.get("text", "")), "", "enemy spinner shows what resolves")
	for key in ["nudge_l", "nudge_r", "respin", "undo"]:
		assert_true(scene._stickers[key] is StickerButton and scene._stickers[key].is_visible_in_tree(), "%s sticker" % key)
	assert_false(scene.controls_row.is_visible_in_tree(), "no dropdown row")
	assert_true(scene._end_turn_button is DripButton, "SEND IT in drip lettering")
	assert_true(scene._hand_box.get_child_count() > 0 and scene._hand_box.get_child(0) is ZineCard, "cards are zine stickers")
	# Everything fits the 1280x720 canvas: the controls row and the left column never push
	# the preview/log strips or the cards off-screen.
	assert_true(scene.controls_row.get_combined_minimum_size().x <= 1280, "controls row %.0f px" % scene.controls_row.get_combined_minimum_size().x)
	assert_true(scene.get_combined_minimum_size().y <= 720 - 80, "scene min height %.0f px leaves room for the netrun bars" % scene.get_combined_minimum_size().y)
	# Fight a bigger board (satellites) and re-check.
	scene.start_fight(&"collections_agent", 3)
	await _layout(scene)
	assert_eq(scene.layout_violations(), [])


func test_hq_is_a_cyberdeck_and_the_grid_is_wireframe() -> void:
	var hq := _open(HQ)
	await _layout(hq)
	hq.new_campaign(2)
	assert_true(hq.background.visible, "HQ shows the cyberdeck")
	assert_false(hq.wireframe.visible)
	assert_not_null(hq._panel.find_child("", true, false) if false else hq._panel, "HQ panel")
	var found_poster := false
	var found_polaroid := false
	var found_stamp := false
	for n in _descendants(hq._panel):
		found_poster = found_poster or n is HeatPoster
		found_polaroid = found_polaroid or n is Polaroid
		found_stamp = found_stamp or (n is ZineStamp and n.stamp_text == "JACK IN")
	assert_true(found_poster, "wanted poster (Heat)")
	assert_true(found_polaroid, "Polaroid roster")
	assert_true(found_stamp, "JACK IN stamp")
	hq.show_grid()
	assert_true(hq.wireframe.visible, "the Grid is wireframe")
	assert_false(hq.background.visible)
	assert_not_null(hq.grid_view)
	var plan := false
	for n in _descendants(hq._panel):
		plan = plan or (n is ZineNote and n.title == "THE PLAN")
	assert_true(plan, "zine sidebar THE PLAN")


func _descendants(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_descendants(c))
	return out


func test_core_resolution_stays_well_under_a_millisecond_per_turn() -> void:
	# TECH_SPEC 10: resolution logic must run well under 1 ms per turn.
	var resolver := CombatFixture.resolver()
	var s := CombatSession.start(resolver, &"breaker", [&"claims_adjuster"], 4, &"rank:1")
	var turns := 0
	var start := Time.get_ticks_usec()
	while turns < 200:
		if s.state.is_over():
			s = CombatSession.start(resolver, &"breaker", [&"claims_adjuster"], 4 + turns, &"rank:1")
		s.apply(CombatAction.end_turn())
		turns += 1
	var per_turn_ms := (Time.get_ticks_usec() - start) / 1000.0 / turns
	assert_true(per_turn_ms < 1.0, "%.3f ms per turn (apply incl. preview-grade duplication)" % per_turn_ms)


func test_system_log_strip_shows_only_when_toggled_in_options() -> void:
	var was: bool = Settings.system_log
	Settings.system_log = false
	var scene := _open(HQ)
	await _layout(scene)
	assert_false(scene._log.is_visible_in_tree(), "log strip hidden by default")
	Settings.set_system_log(true)
	assert_true(scene._log.is_visible_in_tree(), "log strip shown when turned on")
	Settings.set_system_log(was)
