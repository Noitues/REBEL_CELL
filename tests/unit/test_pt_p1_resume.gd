extends GutTest
## PB-SOL-1 I2 / B-14: Quit and Continue in the middle of a fight. The resumed fight shows what the saved one
## showed: the same state, the same staged plays (the THIS TURN queue), the same RAM readout, the same
## end-of-turn preview (LETHAL or not), and the next play costs and previews the same.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Vector2(1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_pt_p1_resume"
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


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _has_combat(net: Control) -> bool:
	return net.combat_scene != null


func _net() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var net: Control = load(NETRUN).instantiate()
	holder.add_child(net)
	net.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return net


## What the fight shows and what the next play would do.
func _snap(combat: Control) -> Dictionary:
	var st: CombatState = combat.engine.state()
	var rows: Array[String] = []
	for r in combat.queue_rows():
		rows.append("%s | %s" % [r["left"], r["right"]])
	var fc: CombatResult = combat.engine.preview_end_turn()
	var after_turn: CombatState = fc.state if fc != null else null
	return {
		"hash": combat.engine.session.state_hash(),
		"ram": st.ram, "free_nudges": st.free_nudges, "hp": st.player.hp, "turn": st.turn,
		"ram_bar": "%d/%d" % [combat.ram_note.ram, combat.ram_note.max_ram],
		"pending": combat.ram_note.pending, "next_turn": combat.ram_note.next_turn,
		"rows": rows,
		"can_rewind": combat.engine.can_rewind(), "can_unstage": combat.can_unstage(),
		"preview_hp": after_turn.player.hp if after_turn != null else -1,
		"preview_over": after_turn.is_over() if after_turn != null else false,
		"queue_resolved_hp": combat._queue_resolved.player.hp if combat._queue_resolved != null else -1,
		"nudge_forecast_ok": combat.engine.forecast(CombatAction.nudge(st.player.id, 1, RC.RingScope.OUTER)).ok(),
	}


func test_a_fight_resumed_mid_turn_shows_what_the_saved_one_showed() -> void:
	var net := _net()
	net.new_campaign(1)
	net.start_run(1)
	await _frames()
	net.enter_node(RunManager.netrun.available_nodes()[0])
	await BoundedWait.until(get_tree(), _has_combat.bind(net), 5.0)
	var combat: Control = net.combat_scene
	assert_not_null(combat, "a fight shows")
	combat.skip_motion()
	await _frames(3)
	# Stage a nudge and the first playable card without a random part.
	combat.nudge(1)
	combat.skip_motion()
	await _frames(2)
	var st: CombatState = combat.engine.state()
	for i in st.hand.size():
		if not CardTargeting.options(combat.engine.resolver, st, i).is_empty():
			combat.play_card(i)
			break
	combat.skip_motion()
	await _frames(3)
	var before := _snap(combat)
	assert_gt((before["rows"] as Array).size(), 0, "plays are staged")
	assert_eq(RunManager.autosave(), OK, "saved mid-fight")
	# Quit and Continue.
	net.get_parent().queue_free()
	await _frames(3)
	RunManager.reset()
	assert_true(RunManager.resume(), "resumed")
	var net2 := _net()
	net2.resume()
	await BoundedWait.until(get_tree(), _has_combat.bind(net2), 5.0)
	var combat2: Control = net2.combat_scene
	assert_not_null(combat2, "the fight is back")
	combat2.skip_motion()
	await _frames(4)
	var after := _snap(combat2)
	print("PT-P1 resume before: ", before)
	print("PT-P1 resume after:  ", after)
	for k in before:
		assert_eq(after[k], before[k], "resume: %s" % k)
