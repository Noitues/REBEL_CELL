extends SceneTree
## Phase timers for one built-in-bot campaign (BALANCE_SIM S4b): where the seconds go.
##   godot --headless --path . -s tools/balance/profile_campaign.gd -- [seed=1000]
## Times CombatBot's three parts (candidate list, resolver.apply, score) inside a copy of its turn loop.

var t_cand := 0
var t_apply := 0
var t_score := 0
var t_act := 0
var n_apply := 0
var n_score := 0
var n_turns := 0
var t_dup := 0
var t_res := 0


func _init() -> void:
	process_frame.connect(_run, CONNECT_ONE_SHOT)


func _score2(session: CombatSession, state: CombatState, rng: RandomNumberGenerator) -> float:
	var t0 := Time.get_ticks_usec()
	var s := state.duplicate_state()
	t_dup += Time.get_ticks_usec() - t0
	t0 = Time.get_ticks_usec()
	session.resolver.resolve_turn(s, rng, [] as Array[Dictionary])
	t_res += Time.get_ticks_usec() - t0
	return 0.0


func _turn(s: NetrunSession) -> bool:
	var session := s.combat
	n_turns += 1
	var taken := 0
	CombatBot._retarget(session, s.combat_action)
	while taken < CombatBot.MAX_ACTIONS_PER_TURN and not session.state.is_over():
		var best: CombatAction = null
		var t0 := Time.get_ticks_usec()
		var best_score := CombatBot._score(session, session.state, CombatResolver.clone_rng(session.rng))
		t_score += Time.get_ticks_usec() - t0
		n_score += 1
		t0 = Time.get_ticks_usec()
		var cands := CombatBot._candidates(session)
		t_cand += Time.get_ticks_usec() - t0
		for a in cands:
			t0 = Time.get_ticks_usec()
			var r := session.resolver.apply(session.state, a, CombatResolver.clone_rng(session.rng))
			t_apply += Time.get_ticks_usec() - t0
			n_apply += 1
			if not r.ok():
				continue
			t0 = Time.get_ticks_usec()
			var sc := CombatBot._score(session, r.state, CombatResolver.clone_rng(session.rng))
			_score2(session, r.state, CombatResolver.clone_rng(session.rng))
			t_score += Time.get_ticks_usec() - t0
			n_score += 1
			if sc > best_score + 0.01:
				best_score = sc
				best = a
		if best == null:
			break
		var t1 := Time.get_ticks_usec()
		var result: CombatResult = s.combat_action(best)
		t_act += Time.get_ticks_usec() - t1
		if result == null or not result.ok():
			break
		taken += 1
	if not session.state.is_over():
		var t2 := Time.get_ticks_usec()
		s.combat_action(CombatAction.end_turn())
		t_act += Time.get_ticks_usec() - t2
	return true


func _run() -> void:
	var seed_arg := 1000
	for a in OS.get_cmdline_user_args():
		if a.begins_with("seed="):
			seed_arg = int(a.trim_prefix("seed="))
	var registry: Node = root.get_node(^"ContentRegistry")
	var lookup := ContentLookup.new().add_registry(registry)
	var sim := CampaignSimulator.new(CombatResolver.new(registry.config, lookup))
	sim.turn_override = Callable(self, "_turn")
	var t0 := Time.get_ticks_msec()
	var r := sim.run_campaign(seed_arg, 0)
	var total := Time.get_ticks_msec() - t0
	print("PROFILE seed %d: %d ms total, %d fights, %d turns, outcome %s hash %d" % [seed_arg, total, r["fights"], n_turns, r["outcome"], r["hash"]])
	print("  (extra pass) duplicate_state %d ms, resolve_turn %d ms" % [t_dup / 1000, t_res / 1000])
	print("  candidates %d ms | apply %d ms (%d calls) | score %d ms (%d calls) | real actions+end turns %d ms | rest %d ms" % [
		t_cand / 1000, t_apply / 1000, n_apply, t_score / 1000, n_score, t_act / 1000,
		total - (t_cand + t_apply + t_score + t_act) / 1000])
	quit(0)
