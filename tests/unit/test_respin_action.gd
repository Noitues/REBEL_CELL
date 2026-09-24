extends GutTest
## The RAM respin (GDD 2.5, 11.3): 4 RAM, own wheel, a random event (checkpoint);
## preview equals the real result.

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func test_respin_costs_4_ram_and_moves_the_wheel() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 8, &"rank:1")
	var before := s.state.player.wheel.rotation
	var preview := s.preview(CombatAction.respin())
	var r := s.apply(CombatAction.respin())
	assert_true(r.ok(), r.error)
	assert_eq(s.state.ram, 6 - _resolver.config.respin_ram_cost)
	assert_ne(s.state.player.wheel.rotation, before)
	assert_eq(preview.state.player.wheel.rotation, s.state.player.wheel.rotation, "preview equals the result")
	assert_false(s.can_rewind(), "random event: new checkpoint")
	assert_eq(CombatFixture.events_of(r, "respin").size(), 1)


func test_respin_is_refused_without_ram() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 8, &"rank:1")
	s.state.ram = 3
	var r := s.apply(CombatAction.respin())
	assert_false(r.ok())
	assert_true(r.error.contains("RAM"))


func test_respin_replays_deterministically() -> void:
	var s := CombatSession.start(_resolver, &"breaker", [&"triage_unit"], 8, &"rank:1")
	s.apply(CombatAction.respin())
	s.apply(CombatAction.end_turn())
	var replayed := CombatSession.replay(_resolver, s.setup, s.combat_seed, s.history)
	assert_eq(replayed.state_hash(), s.state_hash())
