extends GutTest
## Plan 2 N1 (R2): an enemy Hub's FLAT HEAL now scales with the tier damage factor (it
## ignored `output_scale` before); a PERCENT one reads max HP and is not rescaled; a Hub
## Breach stops both; preview == result.

const TIER_FACTORS: Array[float] = [1.0, 1.3, 1.69, 2.2]

var _resolver: CombatResolver


func before_all() -> void:
	_resolver = CombatFixture.resolver()


func _renewal(factor: float) -> CombatSession:
	var s := CombatSession.start(_resolver, &"breaker", [&"renewal_engine"], 5, &"rank:1", 0, {"enemy_output_scale": factor})
	CombatFixture.land(s.state.player, 5)
	return s


func _hub_heal(r: CombatResult, enemy_id: StringName) -> int:
	# The boss's own wheel is parked on NULL, so every heal on it is the Hub's turn-start one.
	var total := 0
	for e in CombatFixture.events_of(r, "heal"):
		if e["target"] == enemy_id:
			total += int(e["amount"])
	return total


## The Hub heal is a turn-start effect: the End Turn preview (RESOLVE only) never shows it,
## so its forecast is `fx.effect_amount` on the pre-turn state, held here to the real heal.
## Also: the End Turn preview still equals the real resolved state.
func _forecast_and_real(s: CombatSession, enemy_id: StringName) -> Array:
	var b := s.state.get_combatant(enemy_id)
	var forecast := 0
	for te in s.resolver.fx.hub_of(b.wheel).passive_effects:
		for e in te.effects:
			if e.type == RC.EffectType.HEAL:
				forecast += s.resolver.fx.effect_amount(e, b)
	var pv := s.preview_end_turn()
	var r := s.apply(CombatAction.end_turn())
	assert_eq(pv.state.state_hash(), r.resolved_state.state_hash(), "End Turn preview == resolved state")
	return [forecast, _hub_heal(r, enemy_id)]


func _auto_renew_amount(factor: float) -> Array:
	var s := _renewal(factor)
	var b := s.state.get_combatant(&"enemy_0")
	b.hp = 300
	CombatFixture.land(b, 5)
	return _forecast_and_real(s, &"enemy_0")


func test_hub_heal_flat_scales_by_tier() -> void:
	var base := 0
	var hub := (load("res://content/enemies/renewal_engine.tres") as EnemyData).wheel.hub
	for te in hub.passive_effects:
		for e in te.effects:
			if e.type == RC.EffectType.HEAL:
				base += e.amount
	assert_eq(base, 10, "Auto-Renew authors HEAL 10")
	var got := []
	for f in TIER_FACTORS:
		var pair := _auto_renew_amount(f)
		assert_eq(pair[0], pair[1], "preview == result at factor %s" % f)
		got.append(pair[1])
	assert_eq(got, [10, 13, 17, 22], "round(10 x factor); T1 unchanged")


func test_hub_heal_percent_not_rescaled() -> void:
	var heal := CombatFixture.effect(RC.EffectType.HEAL, RC.EffectTarget.SELF, 2)
	heal.amount_mode = RC.AmountMode.PERCENT
	var hub := CombatFixture.hub(&"amh_hub", 0, [CombatFixture.triggered(RC.Trigger.ON_TURN_START, [heal])])
	var enemy := CombatFixture.enemy(&"amh_enemy", 300, CombatFixture.null_wheel(0, hub))
	var resolver := CombatFixture.resolver([enemy])
	for f in TIER_FACTORS:
		var s := CombatSession.start(resolver, &"breaker", [enemy.id], 5, &"", 0, {"enemy_output_scale": f})
		CombatFixture.land(s.state.player, 5)
		s.state.get_combatant(&"enemy_0").hp = 100
		var pair := _forecast_and_real(s, &"enemy_0")
		assert_eq(pair[1], 6, "2 %% of 300 at factor %s" % f)
		assert_eq(pair[0], pair[1], "forecast == result")


func test_hub_heal_disabled_by_hub_breach() -> void:
	var s := _renewal(TIER_FACTORS[3])
	var b := s.state.get_combatant(&"enemy_0")
	b.hp = 300
	var events: Array[Dictionary] = []
	_resolver.fx.hub_breach(b, 1, events)
	CombatFixture.land(b, 5)
	var r := s.apply(CombatAction.end_turn())
	assert_eq(_hub_heal(r, &"enemy_0"), 0, "breached: no heal at any tier")
