extends GutTest
## Plan 1 W1-R1 R1-STICKER: every verb sticker that folds (CONTINUE on the tutorial win, the loot sheet and the
## raid result; BACK TO HQ on the run end) keeps its fold room (no glyph under the focus fold's square) and stands
## inside the B5c safe margin, at text 1.0 / 1.6 / 2.0, on the real screens.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _scale := 1.0
var _tutorial_done := true


func before_each() -> void:
	_scale = Settings.text_scale
	_tutorial_done = Settings.tutorial_done
	AudioDirector.muted = true
	Motion.force_live = false
	RunManager.save_slot = "gut_w1r1_sticker"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Settings.set_text_scale(_scale)
	Settings.set_tutorial_done(_tutorial_done)
	Motion.force_live = false
	RunManager.pending_tutorial = false
	AudioDirector.muted = false
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _mount(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


## The VinylSticker that draws a verb sticker's lettering.
func _vinyl(c: Node) -> VinylSticker:
	if c is HoloSticker:
		return (c as HoloSticker).sticker
	if c is VinylButton:
		return (c as VinylButton).sticker
	if c is SendItSticker:
		return (c as SendItSticker).art
	return c as VinylSticker


## The letters of `v` whose rect touches the fold's square.
func _glyphs_on_fold(v: VinylSticker) -> Array:
	var px: int = v.get(&"_px")
	var font: Font = v.get(&"_font")
	var peel := v.peel_px()
	var fold := Rect2(Vector2(v.body_rect.end.x - peel, v.body_rect.position.y), Vector2(peel, peel))
	var hit: Array = []
	for g in v.get(&"_glyphs"):
		if String(g[0]).strip_edges() == "" or String(g[0]) == " ":
			continue
		var gp: Vector2 = g[1]
		var gr := Rect2(Vector2(gp.x, gp.y - float(g[4])), Vector2(font.get_string_size(g[0], HORIZONTAL_ALIGNMENT_LEFT, -1, px).x, float(g[4])))
		if gr.intersects(fold):
			hit.append(String(g[0]))
	return hit


func _check(c: Node, what: String, scale: float) -> void:
	assert_not_null(c, "%s x%.1f: the sticker exists" % [what, scale])
	if c == null:
		return
	var v := _vinyl(c)
	assert_not_null(v, "%s x%.1f: has a vinyl" % [what, scale])
	if v == null:
		return
	assert_true((c as Control).is_visible_in_tree(), "%s x%.1f: shown" % [what, scale])
	assert_eq(_glyphs_on_fold(v), [], "%s x%.1f: no letter under the fold" % [what, scale])
	var r := Fx.sticker_rect(v)
	assert_true(Fx.sticker_safe_rect(SCREEN).grow(0.5).encloses(r), "%s x%.1f: inside the safe margin (%s)" % [what, scale, r])


func test_tutorial_win_continue() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		Settings.set_tutorial_done(false)
		RunManager.new_campaign(1)
		RunManager.pending_tutorial = true
		var scene := _mount(COMBAT)
		scene.auto_start = false
		scene.start_fight(&"collections_agent", 5)
		await _frames(3)
		for s in 40:
			scene.start_fight(&"collections_agent", 100 + s)
			scene.skip_motion()
			scene.engine.state().enemies[0].hp = 1
			if scene.engine.preview_end_turn().state.outcome == CombatState.Outcome.VICTORY:
				break
		scene.end_turn()
		scene.skip_motion()
		await _frames(6)
		_check(scene._continue_button, "tutorial win CONTINUE", scale)
		scene.get_parent().queue_free()
		await _frames(2)
		RunManager.pending_tutorial = false
		RunManager.reset()


func test_loot_continue() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		for kind in ["card", "firmware"]:
			var scene := _mount(NETRUN)
			RunManager.new_campaign(1)
			scene.start_run(1)
			await _frames(2)
			var run := RunManager.netrun.run
			run.pending_rewards.append({"kind": kind, "options": ["twist", "jam", "cache"] if kind == "card" else ["barbed_wire", "bulkhead", "burner"]})
			run.phase = RunState.Phase.REWARD
			scene._show_current()
			PageTransition.settle(scene)
			await _frames(4)
			_check(scene._panel.find_child("Continue", true, false), "loot (%s) CONTINUE" % kind, scale)
			scene.get_parent().queue_free()
			await _frames(1)
			RunManager.reset()


func test_run_end_back_to_hq() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		var scene := _mount(NETRUN)
		RunManager.new_campaign(1)
		scene.start_run(1)
		await _frames(2)
		DemoSetup.end_run(RunManager.netrun, "completed")
		scene._show_end()
		PageTransition.settle(scene)
		await _frames(4)
		_check(scene._panel.find_child("BackToHq", true, false), "run end BACK TO HQ", scale)
		scene.get_parent().queue_free()
		await _frames(1)
		RunManager.reset()


func test_raid_result_continue() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(7)
		var c := RunManager.campaign
		var g := RunManager.corporation.city_grid
		var first: StringName = g.get_site(g.home_site_id).links[0]
		DemoSetup.set_schematics(c, 100)
		CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
		var armory: Array[StringName] = [&"turret", &"ice_lock", &"decoy"]
		DemoSetup.set_armory(c, armory)
		c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
		CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
		var hq := _mount(HQ)
		await _frames(2)
		hq.show_raid()
		await _frames(2)
		Motion.force_live = true  # headless goes straight to the report; the playout page is the one under test
		hq.fight_raid()
		await _frames(4)
		var cont: Node = hq._panel.find_child("Continue", true, false) if hq._panel != null else null
		if cont != null and hq.playout != null and is_instance_valid(hq.playout):
			hq.playout.skip_to_end()
			await _frames(4)
			cont.modulate.a = 1.0
		_check(cont, "raid result CONTINUE", scale)
		hq.get_parent().queue_free()
		await _frames(2)
		RunManager.reset()
