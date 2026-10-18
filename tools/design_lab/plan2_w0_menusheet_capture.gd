extends Node
## Plan 2 W0 MENUSHEET capture (dev tool, windowed only through tools/run_windowed.py, 1920x1080, text 1.0).
## `--out=<abs dir>`: one PNG per merged B-MENU + C-SCREENS change, driven from fixtures (never by playing):
##   1_PAUSE.png   C6   the pause menu, Abandon run set apart from the two Quit rows
##   2_UNLOCK.png  C7   New Campaign: a locked tile "UNLOCKS · 60 SCHEMATICS" and the currency line
##   3_TAKEN.png   C8   a loot card pick, the toast naming what was taken
##   4_SOCKET.png  G14  Firmware into an occupied socket: the confirm naming both chips
##   5_HEAT.png    C4   the Heat tooltip with the next threshold's effect
## Runs unchanged on the tree before the merge (it calls no new function): the same states, the old look.
## tools/design_lab/plan2_w0_menusheet_sheet.py stitches before | after.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const HQ := preload("res://scenes/hq/hq_scene.tscn")

var _out := ""
var _holder: Control = null


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _fresh() -> Control:
	if _holder != null:
		_holder.queue_free()
		await _frames(3)
	_holder = Control.new()
	_holder.size = get_viewport().get_visible_rect().size
	add_child(_holder)
	return _holder


func _shot(name: String) -> void:
	await _frames(16)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [_out, name])
	print("shot ", name)


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(_out)
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	await _frames(6)
	RunManager.save_slot = "plan2_w0_menusheet"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.profile.unlocks.clear()
	await _pause()
	await _unlock()
	await _taken()
	await _socket()
	await _heat()
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	get_tree().quit()


func _pause() -> void:
	# W0 SCREENSFIX: the real flow (the scene's own Esc handler, `open_settings`), not a bare PauseMenu.
	RunManager.reset()
	RunManager.new_campaign(1)
	var h := await _fresh()
	var scene: Control = load(NETRUN).instantiate()
	h.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(3)
	scene.open_settings()
	await _frames(4)
	await _shot("1_PAUSE")


func _unlock() -> void:
	RunManager.reset()
	RunManager.new_campaign(1)
	RunManager.campaign.schematics = 37
	var h := await _fresh()
	var hq: Control = HQ.instantiate()
	h.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hq.show_start()
	await _shot("2_UNLOCK")


func _netrun(offers: Array) -> Control:
	RunManager.reset()
	RunManager.new_campaign(1)
	var h := await _fresh()
	var scene: Control = load(NETRUN).instantiate()
	h.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	await _frames(3)
	var s := RunManager.netrun
	for o in offers:
		s.run.pending_rewards.append(o)
	s.run.phase = RunState.Phase.REWARD
	scene._show_current()
	scene.open_reward(0)
	PageTransition.settle(scene)
	await _frames(4)
	return scene


func _fitting_slot(s: NetrunSession, id: StringName) -> int:
	for i in s.run.operative.slot_slice_ids.size():
		if s.firmware_slot_error(id, i) == "":
			return i
	return -1


func _taken() -> void:
	var scene := await _netrun([{"kind": "card", "options": ["twist", "jam", "cache"]},
			{"kind": "firmware", "options": ["barbed_wire", "bulkhead", "burner"]}])
	scene.choose_reward(0)
	PageTransition.settle(scene)
	await _frames(80)
	await _shot("3_TAKEN")


func _socket() -> void:
	var scene := await _netrun([{"kind": "firmware", "options": ["barbed_wire", "bulkhead", "burner"]},
			{"kind": "card", "options": ["twist", "jam", "cache"]}])
	var s := RunManager.netrun
	var slot := _fitting_slot(s, &"barbed_wire")
	s.run.operative.slot_firmware_ids[slot] = &"burner"
	scene.choose_reward(0, slot)
	await _frames(80)
	var dlg := scene.get_node_or_null("SocketOverwriteConfirm") as Control
	if dlg != null:
		print("dialog rect ", dlg.get_global_rect(), " panel ", dlg.panel.get_global_rect(), " view ", get_viewport().get_visible_rect().size)
	await _shot("4_SOCKET")


func _heat() -> void:
	RunManager.reset()
	RunManager.new_campaign(1)
	RunManager.campaign.heat = 12
	var h := await _fresh()
	var hq: Control = HQ.instantiate()
	h.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hq.show_hq()
	await _frames(20)
	var g: Control = hq.hud.heat_gauge
	var tip := g._make_custom_tooltip(g.tooltip_text) as Control
	if tip == null:
		push_error("ERROR: no heat tooltip")
	else:
		var back := ColorRect.new()
		back.color = Color(Palette.NIGHT_SKY, 0.95)
		h.add_child(back)
		back.add_child(tip)
		tip.reset_size()
		back.size = tip.size + Vector2(12, 8)
		tip.position = Vector2(6, 4)
		back.global_position = g.get_global_rect().position + Vector2(0, g.size.y + 6.0)
		print("tip ", g.tooltip_text)
	await _shot("5_HEAT")
