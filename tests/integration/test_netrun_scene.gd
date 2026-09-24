extends GutTest
## The netrun scene drives a whole run through RunManager: new campaign, map moves,
## embedded combat, rewards/events/shops, autosave after every step, and resume.

const SCENE := "res://scenes/netrun_map/netrun_scene.tscn"
const MAX_STEPS := 400

var _scene: Control


func before_each() -> void:
	RunManager.save_slot = "gut_test"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	_scene = add_child_autofree(load(SCENE).instantiate())


func after_each() -> void:
	RunManager.delete_save()
	RunManager.reset()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.scene_switching_enabled = true


## One UI-level step toward the end of the run.
func _step() -> void:
	var s := RunManager.netrun
	match s.run.phase:
		RunState.Phase.MAP:
			_scene.enter_node(s.available_nodes()[0])
		RunState.Phase.COMBAT:
			if s.combat != null:
				s.combat.state.player.hp = s.combat.state.player.max_hp  # keep the demo operative alive
				CombatFixture.land(s.combat.state.player, 0)  # Crit every turn: fights end fast
				for i in range(s.combat.state.hand.size() - 1, -1, -1):
					if i < s.combat.state.hand.size():
						_scene.combat_scene.play_card(i)
			_scene.combat_scene.end_turn()
			if RunManager.netrun.run.phase != RunState.Phase.COMBAT:
				await wait_seconds(1.0)  # the scene lingers on the final combat frame
		RunState.Phase.REWARD:
			if s.current_reward()["kind"] == "firmware":
				_scene.skip_reward()
			else:
				_scene.choose_reward(0)
		RunState.Phase.EVENT:
			_scene.choose_event(s.current_event().choices.size() - 1)
		RunState.Phase.SHOP:
			_scene.leave_shop()


func test_new_campaign_and_run_start_from_the_scene() -> void:
	_scene.new_campaign(4)
	assert_not_null(RunManager.campaign)
	assert_eq(RunManager.campaign.roster.size(), 2, "two rookies")
	assert_true(RunManager.has_save(), "autosaved")
	_scene.start_run(1)
	assert_true(RunManager.has_active_run())
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.MAP)
	assert_true(_scene._panel is VBoxContainer, "map panel shown")


func test_a_whole_run_plays_through_the_scene_and_autosaves() -> void:
	_scene.new_campaign(8)
	_scene.start_run(1)
	var steps := 0
	while RunManager.netrun != null and not RunManager.netrun.run.is_over() and steps < MAX_STEPS:
		await _step()
		steps += 1
	assert_true(RunManager.netrun.run.is_over(), "run reached an outcome in %d steps" % steps)
	assert_eq(RunManager.netrun.run.outcome, RunState.Outcome.COMPLETED)
	assert_true(RunManager.campaign.schematics > RunManager.resolver.config.starting_schematics, "Schematics banked and converted")
	assert_eq(RunManager.campaign.get_operative(&"op_1").rank, 1)
	_scene.finish_run()
	assert_false(RunManager.has_active_run())
	assert_true(RunManager.has_save())


func test_resume_restores_the_identical_run_mid_combat() -> void:
	_scene.new_campaign(15)
	_scene.start_run(1)
	_scene.enter_node(RunManager.netrun.available_nodes()[0])
	assert_true(RunManager.netrun.in_combat())
	_scene.combat_scene.nudge(1)
	var hash_before := RunManager.netrun.state_hash()
	var campaign_before := RunManager.campaign.state_hash()
	_scene.save_and_quit()
	RunManager.reset()
	assert_null(RunManager.netrun)
	_scene.resume()
	assert_true(RunManager.has_active_run())
	assert_eq(RunManager.netrun.state_hash(), hash_before, "run identical after resume")
	assert_eq(RunManager.campaign.state_hash(), campaign_before, "campaign identical after resume")
	assert_true(RunManager.netrun.in_combat())
	assert_true(RunManager.netrun.combat.can_rewind(), "the pre-save nudge can still be rewound")
	assert_not_null(_scene.combat_scene, "combat panel re-attached")
