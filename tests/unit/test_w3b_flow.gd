extends GutTest
## Change plan 1, wave 3b (PT-002 B3 / B5 / B9): the tutorial stays out of netrun fights, a mutual zero reads as the
## defeat it counts as, and a raid never plays without START DEFENSE.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const COMBAT := "res://scenes/combat/combat_scene.tscn"

var _tutorial_done: bool


func before_each() -> void:
	RaidModelFixture.use_resolver()  # Phase 2b: Solace is the resolver's carrier here (raid views of the tide are Phase 3)
	_tutorial_done = Settings.tutorial_done
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w3b_flow"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.pending_tutorial = false


func after_each() -> void:
	RaidModelFixture.restore()
	Settings.tutorial_done = _tutorial_done
	RunManager.pending_tutorial = false
	Motion.force_live = false
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


## B3: a first campaign (tutorial never finished, no run completed) opened its netrun fight with the tutorial box up.
func test_b3_netrun_fight_has_no_tutorial_overlay() -> void:
	Settings.tutorial_done = false
	RunManager.new_campaign(1)
	assert_eq(RunManager.profile.runs_completed, 0, "a first campaign")
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(2)
	scene._show_combat()
	await _frames(4)
	var cs: Control = scene.combat_scene
	assert_not_null(cs, "the fight is up")
	assert_null(cs.tutorial, "B3: no tutorial overlay in a netrun fight")
	assert_eq(cs.find_children("*", "TutorialOverlay", true, false).size(), 0, "B3: none in the tree")
	assert_false(RunManager.pending_tutorial, "B3: nothing left pending for a later scene")


## B3: real play (animated playback) on a first campaign: the netrun's scene (auto_start off) never asks for it, the
## stand-alone scene does. Headless playback is always instant, so the rule is tested through its seam.
func test_b3_unprompted_tutorial_is_stand_alone_only() -> void:
	Settings.tutorial_done = false
	RunManager.new_campaign(1)
	var scene: Control = load(COMBAT).instantiate()
	autofree(scene)
	scene.auto_start = false
	assert_false(scene.opens_tutorial_unprompted(false), "B3: a netrun's fight never opens it")
	scene.auto_start = true
	assert_true(scene.opens_tutorial_unprompted(false), "the stand-alone first launch does")
	Settings.tutorial_done = true
	assert_false(scene.opens_tutorial_unprompted(false), "and not once it is done")


## B3: the stand-alone tutorial (title SIMULATE) still runs.
func test_b3_standalone_tutorial_still_starts() -> void:
	RunManager.new_campaign(1)
	RunManager.pending_tutorial = true
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	await _frames(2)
	assert_not_null(scene.tutorial, "SIMULATE opens the tutorial")
	assert_false(RunManager.pending_tutorial, "and consumes the request")


## B5: both sides at zero is a defeat (the operative is checked first; the GDD is silent, DECISIONS W3B) and the
## log line says so instead of the bare "flatlined" beside a DELETED enemy.
func test_b5_mutual_zero_is_a_defeat_and_says_so() -> void:
	var s := CombatState.new()
	var p := CombatantState.new()
	p.id = &"player"
	p.is_player = true
	p.hp = 0
	p.max_hp = 10
	var e := CombatantState.new()
	e.id = &"enemy_0"
	e.hp = 0
	e.max_hp = 38
	s.player = p
	s.enemies = [e]
	var events: Array[Dictionary] = []
	CombatResolver.new(null, null)._check_outcome(s, events)
	assert_eq(s.outcome, CombatState.Outcome.DEFEAT, "B5: a mutual zero is a defeat")
	assert_true(bool(events[0].get("mutual_zero", false)), "B5: the event says both sides reached zero")
	assert_string_contains(String(events[0]["text"]), "both")
	# a plain flatline is not a mutual zero
	e.hp = 5
	s.outcome = CombatState.Outcome.NONE
	events = []
	CombatResolver.new(null, null)._check_outcome(s, events)
	assert_false(bool(events[0].get("mutual_zero", false)))


## B9: a claimed Site brings a raid; the setup page waits for START DEFENSE (GDD 7.1 setup phase). Nothing resolves it
## on its own: not frames, not a stray Enter / Space, only the sticker.
func test_b9_raid_waits_for_start_defense() -> void:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var hq: Control = load("res://scenes/hq/hq_scene.tscn").instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(1)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 100
	var first: StringName = RunManager.corporation.city_grid.get_site(c.grid.home_site_id).links[0]
	CampaignRules.on_run_completed(c, RunManager.corporation, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	var before := RunManager.campaign.pending_raids.size()
	assert_gt(before, 0, "the claim brings a raid")
	hq.show_raid()
	await _frames(30)
	assert_eq(hq.panel_name, "raid", "B9: the setup page is up")
	assert_not_null(hq._panel.find_child("RunRaid", true, false), "START DEFENSE is on the page first")
	for code in [KEY_ENTER, KEY_SPACE]:
		for down in [true, false]:
			var e := InputEventKey.new()
			e.keycode = code as Key
			e.physical_keycode = code as Key
			e.pressed = down
			Input.parse_input_event(e)
			await _frames(2)
	await _frames(60)
	assert_eq(RunManager.campaign.pending_raids.size(), before, "B9: no raid resolved without START DEFENSE")
	hq.show_raid()  # a stray Enter may leave the page (focus on its back control); it never plays the raid
	await _frames(10)
	var start := hq._panel.find_child("RunRaid", true, false) as Control
	assert_not_null(start, "START DEFENSE is on the page")
	start.pressed.emit()
	await _frames(3)
	# Ruling 4 (2026-10-14): with 0 stationed, START DEFENSE asks first; its YES is still the sticker's path.
	if hq._defense_confirm != null and is_instance_valid(hq._defense_confirm):
		hq._defense_confirm.yes_button.pressed.emit()
		await _frames(3)
	assert_eq(RunManager.campaign.pending_raids.size(), before - 1, "only the sticker plays the raid")
