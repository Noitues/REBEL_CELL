extends Node
## Plan 2 Q19 review capture (dev tool, windowed only through tools/run_windowed.py).
## `--out=<abs dir>`: 1_NUDGE.png (a hovered nudge, exact), 2_RESPIN.png (a hovered respin: "?" over the
## ghosted needle), 3_COMPOUND.png (a hovered damage + random status card: exact damage, "?" on the
## random part). tools/design_lab/plan2_q19_sheet.py joins them.

const COMBAT := "res://scenes/combat/combat_scene.tscn"


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(out: String, name: String) -> void:
	await _frames(14)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, name])


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = "plan2_q19"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.reset()
	RunManager.new_campaign(1)
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_fight(&"triage_unit", 7)
	scene.skip_motion()
	await _frames(30)
	# 1 a nudge: every number exact.
	scene._preview_nudge(&"player", {"direction": 1, "ring": RC.RingScope.OUTER})
	await _shot(out, "1_NUDGE")
	# 2 a respin: the landing is "?" over the ghosted needle.
	scene._show_respin_odds()
	await _shot(out, "2_RESPIN")
	# 3 a compound card: 3 damage and a status on a random slice.
	scene._clear_ghost()
	var dmg := EffectData.new()
	dmg.type = RC.EffectType.DEAL_DAMAGE
	dmg.target = RC.EffectTarget.TARGET_WHEEL
	dmg.amount = 8
	var blk := EffectData.new()
	blk.type = RC.EffectType.GAIN_BLOCK
	blk.target = RC.EffectTarget.SELF
	blk.amount = 4
	var st := EffectData.new()
	st.type = RC.EffectType.APPLY_STATUS
	st.target = RC.EffectTarget.TARGET_WHEEL
	st.status = RC.Status.OVERCLOCKED
	st.stacks = 1
	st.slice_pick = RC.SlicePick.RANDOM_NON_NULL
	var card := CardData.new()
	card.id = &"q19_combo"
	card.display_name = "Q19 COMBO"
	card.ram_cost = 1
	card.wheel_target = RC.WheelTarget.ENEMY
	card.effects = [dmg, blk, st]
	scene.engine.resolver.lookup.add(card)
	var hand: Array[StringName] = [&"q19_combo"]
	scene.engine.session.state.hand = hand
	scene.engine.state_changed.emit(scene.engine.state(), [] as Array[Dictionary])
	await _frames(20)
	scene._preview_card(0)
	await _shot(out, "3_COMPOUND")
	RunManager.delete_save()
	get_tree().quit()
