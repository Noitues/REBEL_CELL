extends GutTest
## Balance tooling (gap analysis V4): the combat bot plays fairly and wins a normal fight;
## a simulated netrun is deterministic for a seed.

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func test_bot_wins_a_normal_fight_without_random_cards() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 21, &"rank:1")
	var turns := 0
	while not s.state.is_over() and turns < 40:
		turns += 1
		CombatBot.play_turn(s, s.apply)
	assert_eq(s.state.outcome, CombatState.Outcome.VICTORY, "won in %d turns" % turns)
	var replay := CombatSession.replay(_resolver, s.setup, s.combat_seed, s.history)
	assert_eq(replay.state_hash(), s.state_hash(), "the bot's game replays exactly")


func test_bot_never_plays_random_cards() -> void:
	var respin := CombatFixture.card(&"sim_respin", [CombatFixture.effect(RC.EffectType.RESPIN, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.WHOLE_WHEEL)])
	assert_true(CombatBot._is_random(respin))
	assert_true(CombatBot._is_random(ContentRegistry.get_content(&"pull") as CardData), "draws can reshuffle")
	assert_false(CombatBot._is_random(ContentRegistry.get_content(&"jolt") as CardData))


func test_one_simulated_netrun_is_deterministic() -> void:
	var sim := CampaignSimulator.new(_resolver)
	var a := sim.run_campaign(77, 0, 1)
	var b := sim.run_campaign(77, 0, 1)
	assert_eq(int(a["runs"]), 1)
	assert_eq(a["hash"], b["hash"], "same seed, same campaign")
	assert_eq(int(a["stuck"]), 0, "no fight hit the turn cap")
	assert_true(int(a["fights"]) >= 1)
