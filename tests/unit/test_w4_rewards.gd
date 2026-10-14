extends GutTest
## Change plan 1, W4-REWARDS (D-UX1, F12): one rewards screen. The rows are the payout's offers; taking a row, skipping
## a row and PROCEED give the end state of the old one-after-another flow; SKIP skips only its pick; PROCEED with picks
## left asks first.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Vector2(1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w4_rewards"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Motion.force_live = false


func after_each() -> void:
	Motion.force_live = false
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


## A session on a reward phase with a card offer, a Daemon offer and a card offer again, from `seed`.
func _session(seed: int) -> NetrunSession:
	RunManager.new_campaign(seed)
	var s := RunManager.start_run()
	var rng := RandomNumberGenerator.new()
	rng.seed = seed
	s._offer(&"card", s._card_pool(), 3, rng)
	s._offer(&"daemon", s._pools["daemons"], 2, rng)
	s._offer(&"card", s._card_pool(), 3, rng)
	s.run.phase = RunState.Phase.REWARD
	return s


func _state(s: NetrunSession) -> Dictionary:
	return {"deck": s.run.operative.deck.duplicate(), "daemons": s.run.operative.daemon_ids.duplicate(),
		"phase": s.run.phase, "left": s.run.pending_rewards.size()}


func test_rows_are_the_payout_offers_in_order() -> void:
	for seed in [3, 11, 29]:
		var s := _session(seed)
		assert_eq(s.run.pending_rewards.size(), 3, "seed %d: three rows" % seed)
		for i in 3:
			assert_eq(s.reward_at(i), s.run.pending_rewards[i], "seed %d: row %d is the payout's offer" % [seed, i])
		assert_eq(s.reward_at(0), s.current_reward())
		assert_true(s.reward_at(3).is_empty() and s.reward_at(-1).is_empty())


func test_taking_each_row_in_listed_order_equals_the_old_flow() -> void:
	for seed in [3, 11]:
		var old := _session(seed)
		old.choose_reward(1)
		old.choose_reward(0)
		old.skip_reward()
		var old_state := _state(old)
		var now := _session(seed)
		now.choose_reward(1, -1, 0)
		now.choose_reward(0, -1, 0)
		now.skip_reward(0)
		assert_eq(_state(now), old_state, "seed %d: same end state" % seed)
		assert_eq(now.run.phase, RunState.Phase.MAP)


func test_a_row_taken_out_of_order_gives_the_same_pick() -> void:
	var s := _session(5)
	var daemon_id := String(s.reward_at(1)["options"][0])
	s.choose_reward(0, -1, 1)
	assert_true(s.run.operative.daemon_ids.has(StringName(daemon_id)), "the Daemon row's pick was granted")
	assert_eq(s.run.pending_rewards.size(), 2, "the other two rows stay")
	assert_eq(s.run.phase, RunState.Phase.REWARD)


func test_skip_skips_only_its_pick_and_proceed_gives_up_the_rest() -> void:
	var s := _session(5)
	var deck := s.run.operative.deck.size()
	var keep := s.reward_at(2).duplicate(true)
	s.skip_reward(1)
	assert_eq(s.run.pending_rewards.size(), 2)
	assert_eq(s.reward_at(1), keep, "SKIP on one pick leaves the others")
	s.proceed_rewards()
	var proceed_state := _state(s)
	var all_skipped := _session(5)
	all_skipped.skip_reward()
	all_skipped.skip_reward()
	all_skipped.skip_reward()
	assert_eq(s.run.phase, RunState.Phase.MAP)
	assert_eq(s.run.operative.deck.size(), deck, "nothing granted by leaving")
	assert_eq(proceed_state, _state(all_skipped), "PROCEED = skipping each")


func test_bad_row_indices_are_refused() -> void:
	var s := _session(5)
	s.choose_reward(0, -1, 7)
	assert_eq(s.run.pending_rewards.size(), 3)
	s.skip_reward(-2)
	assert_eq(s.run.pending_rewards.size(), 3)


func test_screen_lists_rows_marks_taken_and_proceed_asks() -> void:
	RunManager.new_campaign(9)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await get_tree().process_frame
	var s := RunManager.netrun
	var rng := RandomNumberGenerator.new()
	rng.seed = 9
	s._offer(&"card", s._card_pool(), 3, rng)
	s._offer(&"daemon", s._pools["daemons"], 2, rng)
	s.run.phase = RunState.Phase.REWARD
	scene._show_current()
	PageTransition.settle(scene)
	for i in 4:
		await get_tree().process_frame
	assert_true(scene.rewards_list_on(), "two picks: the list shows")
	var panel: Node = scene._panel
	assert_not_null(panel.find_child("Reward1", true, false))
	assert_not_null(panel.find_child("Reward2", true, false))
	assert_not_null(panel.find_child("Proceed", true, false), "PROCEED")
	# open row 1: its pick page, with BACK
	scene.open_reward(0)
	PageTransition.settle(scene)
	for i in 4:
		await get_tree().process_frame
	assert_false(scene.rewards_list_on())
	assert_not_null(scene._panel.find_child("RewardsBack", true, false))
	assert_not_null(scene._panel.find_child("Stickers", true, false), "the pick page")
	# SKIP on the opened pick skips that pick only and returns to the list, the row marked
	scene.skip_reward()
	PageTransition.settle(scene)
	for i in 4:
		await get_tree().process_frame
	assert_eq(s.run.pending_rewards.size(), 1)
	assert_true(scene.rewards_list_on(), "one settled: the list stays")
	assert_not_null(scene._panel.find_child("RewardDone", true, false), "the skipped row is marked")
	# PROCEED with a pick left asks first
	scene.proceed_rewards()
	await get_tree().process_frame
	assert_not_null(scene.get_node_or_null("ProceedConfirm"), "asks")
	assert_eq(s.run.phase, RunState.Phase.REWARD)
	scene.proceed_rewards(true)
	assert_eq(s.run.phase, RunState.Phase.MAP)
