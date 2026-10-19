extends GutTest
## Plan 2 Q19 flow: the chip. A hovered respin shows "?" (no odds) and a ghosted needle on the
## wheel it would turn, without moving it or drawing any RNG; a hovered compound card shows its
## known damage exactly plus a "?" chip on the wheel its random part hits; leaving clears both.

const SCENE := "res://scenes/combat/combat_scene.tscn"

var _scene: Control


func before_each() -> void:
	_scene = add_child_autofree(load(SCENE).instantiate())
	_scene.start_fight(&"collections_agent", 21)


func _kinds(id: StringName) -> Array:
	var out := []
	for c in _scene.result_chips(id):
		out.append(StringName(c["kind"]))
	return out


func test_respin_hover_shows_question_mark_and_ghost_needle() -> void:
	var engine: CombatEngine = _scene.engine
	var rot := engine.state().player.wheel.rotation
	var rng_before := engine.session.rng.state
	var hash_before := engine.state().state_hash()
	_scene._show_respin_odds()
	assert_true(_scene._player_view.unknown_ghost, "the ghosted needle is up")
	assert_true(_kinds(engine.state().player.id).has(ResultChipModel.ODDS), "the chip is a ?")
	var tip := String(_scene._player_view.intent.get("tooltip", ""))
	assert_false(tip.contains("%"), "no odds in the tooltip: " + tip)
	assert_eq(engine.state().player.wheel.rotation, rot, "the needle does not move")
	assert_eq(engine.session.rng.state, rng_before, "0 draws")
	assert_eq(engine.state().state_hash(), hash_before, "no mutation")
	_scene._clear_ghost()
	assert_false(_scene._player_view.unknown_ghost, "leaving clears the ghost")


func test_compound_card_hover_is_exact_but_for_the_question_mark() -> void:
	var engine: CombatEngine = _scene.engine
	var dmg := CombatFixture.effect(RC.EffectType.DEAL_DAMAGE, RC.EffectTarget.TARGET_WHEEL, 3)
	var st := CombatFixture.effect(RC.EffectType.APPLY_STATUS, RC.EffectTarget.TARGET_WHEEL, 0, RC.RingScope.OUTER, 1.0, RC.Status.OVERCLOCKED, RC.SlicePick.RANDOM_NON_NULL)
	st.stacks = 1
	var card := CombatFixture.card(&"puf_combo", [dmg, st], 0)
	engine.resolver.lookup.add(card)
	var hand: Array[StringName] = [&"puf_combo"]
	engine.session.state.hand = hand
	var enemy := engine.state().target_id
	var fc := engine.forecast(CombatAction.play_card(0, enemy))
	assert_true(fc.is_unknown(PreviewResult.RANDOM_SLICE, enemy))
	var hash_before := engine.state().state_hash()
	_scene._preview_card(0)
	assert_true(_kinds(enemy).has(ResultChipModel.ODDS), "the random part is a ?")
	var hp_lost := engine.state().get_combatant(enemy).hp - fc.state().get_combatant(enemy).hp
	if hp_lost > 0:
		var shown := 0
		for c in _scene.result_chips(enemy):
			if StringName(c["kind"]) == ResultChipModel.DAMAGE:
				shown = int(c["value"])
		assert_eq(shown, hp_lost, "the known damage is exact")
	assert_eq(engine.state().state_hash(), hash_before)
