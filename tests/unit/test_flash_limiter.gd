extends GutTest
## Flash limiter (M4 acceptance): never more than 3 flashes per second, checked on a
## real combat event stream.


func test_at_most_three_flashes_in_any_rolling_second() -> void:
	var limiter := FlashLimiter.new(3)
	var shown: Array[float] = []
	for i in 100:
		var t := i * 0.05  # 20 requests per second
		if limiter.request(t):
			shown.append(t)
	assert_true(FlashLimiter.stream_is_safe(shown), "no window holds more than 3")
	assert_eq(limiter.suppressed_count, 100 - shown.size())
	assert_true(shown.size() >= 12 and shown.size() <= 16, "about 3 per second over 5 s (%d)" % shown.size())
	assert_eq(shown.slice(0, 3), [0.0, 0.05, 0.1], "the first three pass")
	assert_true(shown[3] >= 1.0, "the fourth waits for the window")


func test_sparse_flashes_all_pass() -> void:
	var limiter := FlashLimiter.new(3)
	for i in 10:
		assert_true(limiter.request(i * 0.4), "flash %d" % i)


func test_disabled_limiter_passes_everything() -> void:
	var limiter := FlashLimiter.new(3)
	limiter.enabled = false
	for i in 10:
		assert_true(limiter.request(0.0))


func test_stream_is_safe_detects_violations() -> void:
	assert_true(FlashLimiter.stream_is_safe([0.0, 0.5, 0.9, 1.0]))
	assert_false(FlashLimiter.stream_is_safe([0.0, 0.2, 0.4, 0.6]))
	assert_true(FlashLimiter.stream_is_safe([0.0, 0.2, 0.4, 1.4]))


func test_combat_event_stream_never_flashes_more_than_three_times_per_second() -> void:
	# A fast, flash-heavy fight: every turn is a Perfect (retrigger flash) against a
	# boss that changes phases; events are spaced 0.1 s apart.
	var resolver := CombatFixture.resolver()
	var s := CombatSession.start(resolver, &"breaker", [&"renewal_engine"], 2, &"rank:1")
	var events: Array[Dictionary] = []
	for turn in 12:
		CombatFixture.land(s.state.player, 0, 0)
		var boss := s.state.get_combatant(&"enemy_0")
		if turn == 2:
			boss.hp = 150
		if turn == 5:
			boss.hp = 60
		var r := s.apply(CombatAction.end_turn())
		events.append_array(r.events)
		if s.state.is_over():
			break
	var raw := 0
	for e in events:
		if FlashLimiter.FLASH_EVENT_TYPES.has(String(e.get("type", ""))):
			raw += 1
	assert_true(raw > 6, "the stream would flash %d times unfiltered" % raw)
	# Events 10 ms apart: a turn's worth of events plays in well under a second.
	var shown := FlashLimiter.filter_event_stream(events, 0.01)
	assert_true(FlashLimiter.stream_is_safe(shown), "limited stream is safe (%d shown of %d)" % [shown.size(), raw])
	assert_true(shown.size() < raw, "some flashes were suppressed")
