extends GutTest
## Plan 2 B-MENU + C-SCREENS (PB-PT-003b C6 / C7 / C8 / C4, G14):
## - C6: the pause menu's Abandon row stands apart from the quit rows (and asks first: test_abandon_quit);
## - C7: the New Campaign page names the unlock currency, shows the balance held and how it is earned;
## - C8: a loot pick says on screen what was taken;
## - G14: a Firmware chip into an occupied socket asks first, naming the chip it destroys; an empty
##   socket never asks (the rule `firmware_replaced_at` is the one source of both).

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const NetrunScript := preload("res://scripts/ui/netrun_scene.gd")
const HqScript := preload("res://scripts/ui/hq_scene.gd")
const HQ := preload("res://scenes/hq/hq_scene.tscn")

var _scale_before := 1.0


func before_each() -> void:
	_scale_before = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_plan2_bmenu"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.profile.unlocks.clear()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale_before):
		Settings.set_text_scale(_scale_before)
	CityBakeCache.shutdown()
	Dialogue.clear()
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func test_abandon_row_stands_apart_from_the_quit_rows() -> void:
	RunManager.new_campaign(45)
	RunManager.start_run()
	var menu: PauseMenu = add_child_autofree(PauseMenu.new())
	await _frames(2)
	var gap := menu.find_child("AbandonGap", true, false) as Control
	assert_not_null(gap, "a gap sits under the Abandon row")
	assert_true(menu.abandon_run_button.get_parent().is_ancestor_of(gap), "inside the Abandon cell, so the quit rows follow it")
	assert_gte(gap.custom_minimum_size.y, float(UiTheme.SP_XL))


func test_new_campaign_names_the_unlock_currency_and_the_balance() -> void:
	RunManager.new_campaign(1)
	RunManager.campaign.schematics = 37
	var hq: Control = add_child_autofree(HQ.instantiate())
	hq.show_start()
	await _frames()
	var note := hq._panel.find_child("UnlockCurrencyNote", true, false) as Label
	assert_not_null(note, "the page carries the currency line")
	assert_true(note.text.contains("Schematics"), "it names the currency: %s" % note.text)
	assert_true(note.text.contains("37"), "it shows the balance held, the campaign's own")
	assert_eq(note.text, HqScript.unlock_balance_line(RunManager.campaign.schematics), "the balance shown is the rule's")
	assert_true(HqScript.unlock_price_words(60).contains("SCHEMATICS"), "the price names the currency")
	assert_true(HqScript.unlock_price_words(60).contains("60"))


func _netrun_with_firmware_offer() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = Vector2(1280, 720)
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	scene.start_run(1)
	await _frames(2)
	RunManager.netrun.run.pending_rewards.append({"kind": "firmware", "options": ["barbed_wire", "bulkhead", "burner"]})
	RunManager.netrun.run.phase = RunState.Phase.REWARD
	scene._show_current()
	scene.open_reward(0)
	PageTransition.settle(scene)
	await _frames(3)
	return scene


func _fitting_slot(s: NetrunSession, id: StringName) -> int:
	for i in s.run.operative.slot_slice_ids.size():
		if s.firmware_slot_error(id, i) == "":
			return i
	return -1


func test_firmware_replaced_at_is_the_chip_the_socket_holds() -> void:
	RunManager.new_campaign(1)
	RunManager.start_run()
	var s := RunManager.netrun
	var slot := _fitting_slot(s, &"barbed_wire")
	assert_gte(slot, 0, "some slot fits")
	s.run.operative.slot_firmware_ids[slot] = &""
	assert_eq(s.firmware_replaced_at(slot), &"", "an empty socket destroys nothing")
	s.run.operative.slot_firmware_ids[slot] = &"burner"
	assert_eq(s.firmware_replaced_at(slot), &"burner")
	assert_eq(s.firmware_replaced_at(-1), &"", "no such slot")


func test_firmware_into_an_occupied_socket_asks_first_and_names_the_chip() -> void:
	var scene := await _netrun_with_firmware_offer()
	var s := RunManager.netrun
	var slot := _fitting_slot(s, &"barbed_wire")
	s.run.operative.slot_firmware_ids[slot] = &"burner"
	scene.choose_reward(0, slot)
	await _frames(2)
	var d := scene.get_node_or_null(^"SocketOverwriteConfirm")
	assert_not_null(d, "the occupied socket asks")
	assert_eq(s.run.pending_rewards.size(), 1, "nothing was taken yet")
	assert_eq(s.run.operative.slot_firmware_ids[slot], &"burner", "the old chip still stands")
	var old_name := TextDb.t(s.lookup.get_content(&"burner"), "display_name")
	assert_true(NetrunScript.socket_overwrite_question("A", old_name, slot + 1).contains(old_name), "the question names the destroyed chip")
	d.confirmed.emit()
	await _frames(2)
	assert_eq(s.run.operative.slot_firmware_ids[slot], &"barbed_wire", "YES sockets it")
	assert_not_null(scene.get_node_or_null(^"Toast"), "and the pick is said on screen")


func test_firmware_into_an_empty_socket_does_not_ask() -> void:
	var scene := await _netrun_with_firmware_offer()
	var s := RunManager.netrun
	var slot := _fitting_slot(s, &"barbed_wire")
	s.run.operative.slot_firmware_ids[slot] = &""
	scene.choose_reward(0, slot)
	await _frames(2)
	assert_null(scene.get_node_or_null(^"SocketOverwriteConfirm"), "an empty socket needs no confirm")
	assert_eq(s.run.operative.slot_firmware_ids[slot], &"barbed_wire")


func test_taken_line_says_what_and_where() -> void:
	assert_true(NetrunScript.taken_line("card", "Jolt", 0).contains("Jolt"))
	assert_true(NetrunScript.taken_line("card", "Jolt", 0).contains("deck"))
	var fw := NetrunScript.taken_line("firmware", "Burner", 3)
	assert_true(fw.contains("Burner") and fw.contains("3"), fw)
