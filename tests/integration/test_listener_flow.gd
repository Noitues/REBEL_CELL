extends GutTest
## Plan 2 N6 flow (acceptance 10): the enemy listener chip. A hovered nudge whose listener
## hits the operative shows "REACTS: N DMG" with N the preview's HP loss, equal to the loss
## the committed nudge deals; a block-only listener shows its fire count; no fires (or an
## undo back to no fires) clears the chip.

const L = preload("res://tests/helpers/listener_fixture.gd")


func _view() -> Control:
	var v := Control.new()
	v.size = Vector2(400, 400)
	add_child_autofree(v)
	return v


func test_chip_shows_on_nudge_and_matches_preview() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(4), L.block(1)])], {"factor": 1.3})
	L.stage(s)
	var v := _view()
	var nudge := CombatAction.nudge(&"player", 1)
	var pv := s.preview(nudge)
	var st := ListenerChip.state_for(pv.events, &"enemy_0")
	ListenerChip.sync(v, st)
	var chip := v.get_node_or_null(ListenerChip.NODE_NAME) as Badge
	assert_not_null(chip)
	var hp := s.state.player.hp
	s.apply(nudge)
	var dealt := hp - s.state.player.hp
	assert_eq(dealt, 5, "round(4 x 1.3)")
	assert_eq(int(st["damage"]), dealt, "the chip number is the real HP loss")
	assert_eq(chip.text, "REACTS: %d DMG" % dealt)
	assert_true(chip.tooltip_text.contains("on nudge"), chip.tooltip_text)
	assert_true(Rect2(Vector2.ZERO, v.size).encloses(Rect2(chip.position, chip.size)), "the chip sits on the wheel")


func test_block_only_listener_shows_fire_count() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_RAM_SPENT, [L.block(1)]), L.listener(RC.Trigger.ON_CARD_PLAYED, [L.block(1)])])
	L.stage(s, [L.ZAP], 6)
	var st := ListenerChip.state_for(s.preview(CombatAction.play_card(0)).events, &"enemy_0")
	assert_eq(ListenerChip.label(st), "REACTS x2")


func test_undo_clears_chip() -> void:
	var s := L.session([L.listener(RC.Trigger.ON_NUDGE, [L.hit(2)])])
	L.stage(s)
	var v := _view()
	var r := s.apply(CombatAction.nudge(&"player", 1))
	ListenerChip.sync(v, ListenerChip.state_for(r.events, &"enemy_0"))
	assert_not_null(v.get_node_or_null(ListenerChip.NODE_NAME))
	var back := s.rewind()
	ListenerChip.sync(v, ListenerChip.state_for(back.events, &"enemy_0"))
	var chip := v.get_node_or_null(ListenerChip.NODE_NAME)
	assert_true(chip == null or chip.is_queued_for_deletion(), "no fires: no chip")
