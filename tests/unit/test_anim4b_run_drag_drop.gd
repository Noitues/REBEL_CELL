extends GutTest
## Animation pass ANIM-4b (drag and drop in the run): every drag makes exactly the state
## change its button path makes (Modem cards, microchips, Daemons, slice upgrades on the
## page and in the UPGRADE viewer, the shredder in the REMOVE viewer, loot, event rewards,
## raid interlude assets); a refused or cancelled drop changes nothing and the item glides
## home; keys and the pad reach every target; a click picks up and a click drops; reduce
## effects and headless show the end state at once; the views never change game state; the
## new pieces keep the layout at 1.0 / 1.3 / 1.6.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const RICH := 999

var _reduce: bool
var _speed: float
var _scale: float
var _pad: bool


func before_each() -> void:
	_reduce = Settings.reduce_effects
	_speed = Motion.speed
	_scale = Settings.text_scale
	_pad = Settings.pad_active
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_anim4b"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if Settings.reduce_effects != _reduce:
		Settings.set_reduce_effects(_reduce)
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	if Settings.pad_active != _pad:
		Settings.set_pad_active(_pad)
	Fx.apply_settings()
	Motion.force_live = false
	Motion.speed = _speed
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


## A netrun scene in a 1280x720 holder, a fresh campaign (seed 1) and its first run.
func _netrun() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.new_campaign(1)
	scene.start_run(1)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)
	RunManager.reset()


func _shop(scene: Control, cycles: int = RICH) -> void:
	RunManager.netrun.run.cycles = cycles
	RunManager.netrun._open_shop()
	scene._show_current()
	await _frames(4)


func _loot(scene: Control, kind: String, options: Array) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": kind, "options": options})
	run.phase = RunState.Phase.REWARD
	scene._show_current()
	await _frames(4)


## The run and the campaign, as one comparable value.
func _hash() -> String:
	var s := RunManager.netrun
	return "%d:%d" % [s.state_hash() if s != null else 0, RunManager.campaign.state_hash()]


func _live() -> void:
	Motion.force_live = true
	if Settings.reduce_effects:
		Settings.set_reduce_effects(false)
		Fx.apply_settings()


func _press(action: StringName) -> InputEventAction:
	var ev := InputEventAction.new()
	ev.action = action
	ev.pressed = true
	return ev


func _item(scene: Control, row: String, i: int) -> Control:
	return scene._panel.find_child(row, true, false).get_child(i) as Control


## Picks up `source`'s item on `layer` (as a mouse drag leaving it) and lets go over `id`.
func _drag(layer: DropLayer, source: Control, id: String) -> String:
	var data: Variant = layer.begin_drag(source, source.get_meta(DropLayer.SOURCE_META))
	assert_not_null(data, "the drag starts")
	return layer.drop_on(id)


func _ids(cls: StringName) -> Array:
	var out := []
	for id in RunManager.lookup().ids_of_class(cls):
		out.append(String(id))
	out.sort()
	return out


## The first slot (from 0) the item of `source` may go to on `layer`, or -1.
func _taking_slot(layer: DropLayer, source: Control) -> int:
	layer.begin_drag(source, source.get_meta(DropLayer.SOURCE_META))
	var k := -1
	for i in RunManager.netrun.run.operative.slot_slice_ids.size():
		if layer.takes("slot:%d" % i):
			k = i
			break
	layer.cancel()
	layer.finish_all()
	return k


# --- Each drag = its button path ---------------------------------------------------------------

func test_modem_cards_and_daemons_dropped_on_their_tags_match_buy() -> void:
	for pair in [["Stickers", "deck"], ["Daemons", "daemons"]]:
		var hashes := []
		for use_drag in [false, true]:
			var scene := _netrun()
			await _shop(scene)
			var item := _item(scene, String(pair[0]), 0) as ZineCard
			assert_not_null(item, "the Modem sells a %s" % pair[0])
			if use_drag:
				assert_eq(_drag(scene.drops, item, String(pair[1])), "dropped")
			else:
				item.pressed.emit()
			hashes.append(_hash())
			await _close(scene)
		assert_eq(hashes[1], hashes[0], "%s dropped on %s = BUY" % pair)
		assert_ne(hashes[0], "", "bought")


func test_a_microchip_dropped_on_a_slot_matches_the_socket_list_and_buy() -> void:
	var hashes := []
	var slot := -1
	for use_drag in [false, true]:
		var scene := _netrun()
		await _shop(scene)
		var chip := _item(scene, "Chips", 0) as ZineCard
		if slot < 0:
			slot = _taking_slot(scene.drops, chip)
			assert_true(slot >= 0, "a slot takes the chip")
		var before := RunManager.netrun.run.operative.slot_firmware_ids.duplicate()
		if use_drag:
			assert_eq(_drag(scene.drops, chip, "slot:%d" % slot), "dropped")
		else:
			(scene._panel.find_child("SocketPick", true, false) as OptionButton).select(slot)
			chip.pressed.emit()
		assert_ne(RunManager.netrun.run.operative.slot_firmware_ids, before, "socketed")
		hashes.append(_hash())
		await _close(scene)
	assert_eq(hashes[1], hashes[0], "the chip dropped on slot %d = Socket into Slot %d + BUY" % [slot + 1, slot + 1])


func test_a_slice_upgrade_dropped_on_a_slot_matches_the_upgrade_viewer() -> void:
	var hashes := []
	for way in ["viewer", "page", "viewer_drag"]:
		var scene := _netrun()
		await _shop(scene)
		match way:
			"viewer":
				(_item(scene, "Slices", 0) as ZineCard).pressed.emit()
				await _frames(2)
				var view := scene.get_node("SpinnerView") as SpinnerView
				view.select(1)
				view.confirm()
			"page":
				assert_eq(_drag(scene.drops, _item(scene, "Slices", 0), "slot:1"), "dropped")
			"viewer_drag":
				scene.open_overwrite(0)
				await _frames(2)
				var view := scene.get_node("SpinnerView") as SpinnerView
				var chip := view.find_child("InstallSlice", true, false) as Control
				assert_not_null(chip, "the slice to install sits beside the wheel")
				assert_eq(_drag(scene.modal_drops, chip, "slot:1"), "dropped")
				await _frames(2)
				assert_null(scene.get_node_or_null("SpinnerView"), "the viewer closed as UPGRADE closes it")
		hashes.append(_hash())
		await _close(scene)
	assert_eq(hashes[1], hashes[0], "the slice dropped on the Modem's spinner = UPGRADE")
	assert_eq(hashes[2], hashes[0], "the slice dropped on the viewer's slot = UPGRADE")


func test_a_deck_card_dropped_on_the_shredder_matches_select_and_remove() -> void:
	var hashes := []
	for use_drag in [false, true]:
		var scene := _netrun()
		await _shop(scene)
		scene.open_remove()
		await _frames(2)
		var view := scene.get_node("DeckView") as DeckView
		if use_drag:
			assert_not_null(view.shred_tile, "REMOVE mode shows the SHRED tile")
			assert_eq(_drag(scene.modal_drops, view.card(2), "shred"), "dropped")
		else:
			view.select(2)
			view.confirm()
		await _frames(2)
		assert_null(scene.get_node_or_null("DeckView"), "the viewer closed")
		hashes.append(_hash())
		await _close(scene)
	assert_eq(hashes[1], hashes[0], "the card dropped on SHRED = select + REMOVE")


func test_loot_dropped_where_it_goes_matches_taking_it() -> void:
	var daemons := _ids(&"DaemonData")
	var chips := _ids(&"FirmwareData")
	for case in [["card", ["twist", "jam", "cache"], "deck"], ["daemon", daemons.slice(0, 2), "daemons"], ["firmware", chips.slice(0, 2), "slot"]]:
		var hashes := []
		var slot := -1
		for use_drag in [false, true]:
			var scene := _netrun()
			await _frames(2)
			await _loot(scene, String(case[0]), case[1])
			var sticker := _item(scene, "Stickers", 1) as ZineCard
			var target := String(case[2])
			if target == "slot":
				if slot < 0:
					slot = _taking_slot(scene.drops, sticker)
					assert_true(slot >= 0, "a slot takes the loot chip")
				target = "slot:%d" % slot
				assert_not_null(scene._panel.find_child("SpinnerMini", true, false), "the spinner shows beside a chip offer")
			if use_drag:
				assert_eq(_drag(scene.drops, sticker, target), "dropped", "%s onto %s" % [case[0], target])
			else:
				if slot >= 0:
					(scene._panel.find_child("SlotPick", true, false) as SlotPicker).choose(slot)  # art pass W8c: slot tiles
				sticker.pressed.emit()
			hashes.append(_hash())
			await _close(scene)
		assert_eq(hashes[1], hashes[0], "loot %s dropped = taken with its press" % case[0])


## An event whose choice `i` hands over a card: [event id, choice index].
func _card_event() -> Array:
	var lookup := RunManager.lookup()
	for id in _ids(&"TerminalEventData"):
		var ev := lookup.get_content(StringName(id)) as TerminalEventData
		for i in ev.choices.size():
			var c := ev.choices[i]
			if c.reward is CardData and c.hp_cost == 0:
				return [StringName(id), i]
	return []


func test_an_event_reward_dropped_on_the_deck_matches_the_choice() -> void:
	var pick := _card_event()
	assert_false(pick.is_empty(), "an event hands over a card")
	var hashes := []
	for use_drag in [false, true]:
		var scene := _netrun()
		await _frames(2)
		var run := RunManager.netrun.run
		run.cycles = RICH
		run.event_id = pick[0]
		run.phase = RunState.Phase.EVENT
		scene._show_current()
		await _frames(4)
		var choice := scene._panel.find_child("Choice%d" % (int(pick[1]) + 1), true, false) as Button
		assert_true(choice.has_meta(DropLayer.SOURCE_META), "the card's choice drags")
		if use_drag:
			assert_eq(_drag(scene.drops, choice, "deck"), "dropped")
		else:
			choice.pressed.emit()
		hashes.append(_hash())
		await _close(scene)
	assert_eq(hashes[1], hashes[0], "the choice dropped on the CARDS tag = pressing it")


## A netrun in its raid interlude: six claimed firewall relays with a turret each, the
## Armory stocked, a turret in the run's pack.
func _raid() -> Control:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var claimed := 0
	for sd in grid_data.sites:
		if sd.tier == 1 and sd.id != grid_data.home_site_id and sd.objective == RC.SiteObjective.NONE and claimed < 3:
			var s := c.grid.site(sd.id)
			s["status"] = GridState.SiteStatus.CLAIMED
			s["node_type"] = "firewall_relay"
			s["integrity"] = 30
			s["max_integrity"] = 30
			s["assets"] = ["turret"]
			claimed += 1
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_run(1)
	HeatRules.add_heat(c, 26, RunManager.config(), "test")
	RunManager.netrun.run.unbanked_assets.append(&"turret")
	RunManager.netrun._maybe_raid_interlude()
	scene._show_current()
	return scene


## The first node (claimed order) other than `not_site` that takes `source`'s item.
func _taking_node(layer: DropLayer, source: Control, not_site: StringName = &"") -> StringName:
	layer.begin_drag(source, source.get_meta(DropLayer.SOURCE_META))
	var out: StringName = &""
	for t in layer.targets:
		if String(t["kind"]) == "node" and t["value"] != not_site and layer.takes(t["id"]):
			out = t["value"]
			break
	layer.cancel()
	layer.finish_all()
	return out


func test_raid_interlude_asset_drags_match_their_buttons() -> void:
	for case in ["run", "armory", "withdraw", "move"]:
		var hashes := []
		var site: StringName = &""
		var from: StringName = &""
		for use_drag in [false, true]:
			var scene := _raid()
			await _frames(4)
			assert_eq(RunManager.netrun.run.phase, RunState.Phase.RAID, "the raid interlude is open")
			var c := RunManager.campaign
			if from == &"":
				from = c.grid.claimed_ids()[0] if c.grid.claimed_ids()[0] != c.grid.home_site_id else c.grid.claimed_ids()[1]
			var src: Control
			match case:
				"run":
					src = scene._panel.find_child("RunAsset_0", true, false) as Control
				"armory":
					src = scene._panel.find_child("Armory_0", true, false) as Control
				_:
					src = scene._panel.find_child("Withdraw_%s_0" % from, true, false) as Control
			assert_not_null(src, "%s: the item to drag" % case)
			if site == &"" and case != "withdraw":
				site = _taking_node(scene.drops, src, from if case == "move" else &"")
				assert_ne(site, &"", "%s: a node takes it" % case)
			var target := "armory" if case == "withdraw" else "node:%s" % site
			if use_drag:
				assert_eq(_drag(scene.drops, src, target), "dropped", case)
			else:
				match case:
					"run":
						scene.raid_deploy_run_asset(0, site)
					"armory":
						scene.raid_deploy_armory(0, site)
					"withdraw":
						scene.raid_move(from, 0, &"")
					"move":
						scene.raid_move(from, 0, site)
			hashes.append(_hash())
			await _close(scene)
		assert_eq(hashes[1], hashes[0], "raid %s: the drag = its button" % case)


# --- Refusals and cancels ------------------------------------------------------------------------

func test_refusals_and_cancels_change_nothing_and_glide_home() -> void:
	var scene := _netrun()
	await _shop(scene, 5)
	_live()
	var card := _item(scene, "Stickers", 0) as ZineCard
	var before := _hash()
	scene.drops.begin_drag(card, card.get_meta(DropLayer.SOURCE_META))
	assert_string_contains(String(scene.drops.reasons["deck"]), "Not enough Cycles", "the rules' own reason")
	assert_almost_eq(card.modulate.a, DropLayer.SOURCE_DIM, 0.001, "the card has left its slot")
	assert_eq(scene.drops.drop_on("deck"), "refused")
	assert_eq(_hash(), before, "nothing changed")
	assert_false(scene.drops.flights.filter(func(f: Dictionary) -> bool: return f["kind"] == "home").is_empty(), "the card glides home")
	assert_false(scene.drops.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "mark").is_empty(), "the no-entry mark on the tag")
	assert_not_null(scene.get_node_or_null("Toast"), "the reason shows as a toast")
	scene.drops.finish_all()
	assert_eq(card.modulate.a, 1.0, "home: the card shows again")
	# A drop on nothing: back home, nothing changed.
	scene.drops.begin_drag(card, card.get_meta(DropLayer.SOURCE_META))
	assert_eq(scene.drops.release_at(Vector2(-50, -50)), "cancel")
	assert_eq(_hash(), before, "a cancel changes nothing")
	scene.drops.finish_all()
	assert_eq(card.modulate.a, 1.0)
	# The shredder refuses too when the Cycles are short, and the viewer stays open.
	scene.open_remove()
	await _frames(2)
	var view := scene.get_node("DeckView") as DeckView
	assert_eq(_drag(scene.modal_drops, view.card(0), "shred"), "refused")
	assert_eq(_hash(), before)
	assert_not_null(scene.get_node_or_null("DeckView"), "a refusal keeps the viewer open")
	scene.modal_drops.finish_all()
	await _close(scene)


func test_a_chip_on_a_slot_it_does_not_fit_is_refused_with_the_rule_in_names() -> void:
	var scene := _netrun()
	await _shop(scene)
	var s := RunManager.netrun
	var chip := _item(scene, "Chips", 0) as ZineCard
	scene.drops.begin_drag(chip, chip.get_meta(DropLayer.SOURCE_META))
	var id := String(s.run.shop["firmware"][0])
	var fw := RunManager.lookup().get_content(StringName(id)) as FirmwareData
	var refused := 0
	for k in s.run.operative.slot_slice_ids.size():
		var reason := String(scene.drops.reasons["slot:%d" % k])
		assert_false(reason.contains(id), "no raw id in '%s'" % reason)
		if reason != "":
			refused += 1
			assert_string_contains(reason, TextDb.t(fw, "display_name"), "the chip named as the Modem names it")
			var before := _hash()
			assert_eq(scene.drops.drop_on("slot:%d" % k), "refused")
			assert_eq(_hash(), before, "a refused slot changes nothing")
			scene.drops.begin_drag(chip, chip.get_meta(DropLayer.SOURCE_META))
	if fw.allowed_slice_types.is_empty():
		assert_eq(refused, 0, "a chip for any slice fits every slot")
	scene.drops.cancel()
	await _close(scene)


# --- Keys, pad and clicks --------------------------------------------------------------------

## Carries `source` on `layer` and steps the aim through every target; returns the values
## aimed (and checks the reticle follows).
func _walk(layer: DropLayer, source: Control) -> Array:
	layer.start_carry(source)
	assert_eq(layer.mode, DropLayer.Mode.CARRY, "picked up")
	var seen := []
	for k in layer.aim_list.size():
		var t := layer.aimed()
		assert_false(t.is_empty(), "a target is aimed")
		assert_eq(layer.reticle_pos, layer.locate(t).get_center(), "the reticle on it (end state at once headless)")
		if not seen.has(t["id"]):
			seen.append(t["id"])
		layer._input(_press(&"ui_right"))
	return seen


func _offered(layer: DropLayer) -> Array:
	var out := []
	for t in layer.targets:
		if layer.offered(t["id"]) and bool(t["aimable"]) and layer.locate(t).has_area():
			out.append(t["id"])
	return out


func test_keys_and_pad_reach_every_target_and_drop_like_the_mouse() -> void:
	var scene := _netrun()
	await _shop(scene)
	# X / Space picks up the focused chip; the aim starts on the socket list's slot.
	var chip := _item(scene, "Chips", 0) as ZineCard
	var pick := scene._panel.find_child("SocketPick", true, false) as OptionButton
	var slot := _taking_slot(scene.drops, chip)
	pick.select(slot)
	scene._show_current()
	await _frames(3)
	chip = _item(scene, "Chips", 0) as ZineCard
	chip.grab_focus()
	scene.drops._input(_press(&"end_turn"))
	assert_eq(scene.drops.mode, DropLayer.Mode.CARRY, "the pick-up key takes the focused chip")
	scene.drops.cancel()
	# Every slot is reached with the D-pad.
	var seen := _walk(scene.drops, chip)
	var offered := _offered(scene.drops)
	seen.sort()
	offered.sort()
	assert_eq(seen, offered, "the D-pad reaches every slot")
	scene.drops.cancel()
	# The pad prompts follow the carry.
	Settings.set_pad_active(true)
	scene.set_page_prompts(scene.prompts_for(RunManager.netrun))
	assert_string_contains(" | ".join(scene.pad_prompts.texts()), "Pick up")
	scene.drops.start_carry(chip)
	assert_eq(int(scene.drops.aimed().get("value", -1)), slot, "the aim starts on the socket list's slot")
	assert_string_contains(" | ".join(scene.pad_prompts.texts()), "Drop")
	# A drops on the aimed slot: the same change as the mouse.
	var expect: NetrunSession = scene.dry_session()
	expect.buy("firmware", 0, slot)
	scene.drops._input(_press(&"ui_accept"))
	assert_eq(scene.drops.last_outcome, "dropped", "A drops")
	assert_eq(RunManager.netrun.state_hash(), expect.state_hash(), "the same run as a mouse drop")
	assert_string_contains(" | ".join(scene.pad_prompts.texts()), "Pick up")
	await _frames(2)
	# B cancels.
	var card := _item(scene, "Stickers", 0) as ZineCard
	scene.drops.start_carry(card)
	var before := _hash()
	scene.drops._input(_press(&"ui_cancel"))
	assert_eq(scene.drops.mode, DropLayer.Mode.IDLE, "B puts it back")
	assert_eq(_hash(), before)
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.SHOP, "and does not leave the Modem")
	await _close(scene)


func test_the_shredder_and_the_viewer_slots_are_reached_with_keys() -> void:
	var scene := _netrun()
	await _shop(scene)
	scene.open_remove()
	await _frames(2)
	var view := scene.get_node("DeckView") as DeckView
	view.card(1).grab_focus()
	scene.modal_drops._input(_press(&"end_turn"))
	assert_eq(scene.modal_drops.mode, DropLayer.Mode.CARRY, "X picks up the focused deck card")
	assert_eq(scene.modal_drops.aimed().get("id", ""), "shred", "the shredder is aimed")
	scene.modal_drops._input(_press(&"ui_cancel"))
	assert_eq(scene.modal_drops.mode, DropLayer.Mode.IDLE)
	assert_not_null(scene.get_node_or_null("DeckView"), "B while carrying puts the card back, the viewer stays")
	view.close()
	await _frames(2)
	scene.open_overwrite(0)
	await _frames(2)
	var chip := scene.get_node("SpinnerView").find_child("InstallSlice", true, false) as ZineCard
	chip.pressed.emit()  # a press (A or a click) on an item that only moves picks it up
	assert_eq(scene.modal_drops.mode, DropLayer.Mode.CARRY)
	var seen := []
	for k in scene.modal_drops.aim_list.size():
		seen.append(scene.modal_drops.aimed()["id"])
		scene.modal_drops.step_aim(1)
	seen.sort()
	var offered := _offered(scene.modal_drops)
	offered.sort()
	assert_eq(seen, offered, "every slot of the viewer's wheel is reached")
	scene.modal_drops.cancel()
	await _close(scene)


func test_a_click_picks_up_a_raid_chip_and_a_click_on_a_row_drops_it() -> void:
	var scene := _raid()
	await _frames(4)
	var chip := scene._panel.find_child("Armory_0", true, false) as Button
	var site := _taking_node(scene.drops, chip)
	var expect: NetrunSession = scene.dry_session()
	expect.raid_deploy_armory(0, site)
	chip.pressed.emit()
	assert_eq(scene.drops.mode, DropLayer.Mode.CARRY, "a click on the chip picks it up")
	var row: Rect2 = scene.drops.locate(scene.drops.target("node:%s" % site))
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.global_position = row.get_center()
	click.position = row.get_center()
	scene.drops._input(click)
	assert_eq(scene.drops.last_outcome, "dropped", "a click on the row drops it there")
	assert_eq(RunManager.campaign.state_hash(), expect.campaign.state_hash(), "deployed as by Deploy armory asset")
	await _close(scene)


# --- End states, motion, layout and state -------------------------------------------------------

func test_reduce_effects_and_headless_show_the_end_state_at_once() -> void:
	for reduce in [false, true]:
		var scene := _netrun()
		await _shop(scene)
		if reduce:
			Motion.force_live = true
			Settings.set_reduce_effects(true)
			Fx.apply_settings()
		var card := _item(scene, "Stickers", 0) as ZineCard
		scene.drops.begin_drag(card, card.get_meta(DropLayer.SOURCE_META))
		assert_eq(scene.drops.pulse, 1.0, "targets lit, not pulsing")
		assert_null(scene.drops._pulse_tween, "no pulse runs")
		assert_eq(scene.drops.drop_on("deck"), "dropped")
		assert_false(scene.drops.busy(), "no flight, stamp or mark: the end state at once (%s)" % ("reduce effects" if reduce else "headless"))
		assert_eq(FlightFx.active_count(scene), 0, "and no click flight either")
		scene.open_remove()
		await _frames(2)
		var view := scene.get_node("DeckView") as DeckView
		var layer: DropLayer = scene.modal_drops
		assert_eq(_drag(layer, view.card(0), "shred"), "dropped")
		assert_false(layer.busy(), "the shred shows its end state at once")
		await _frames(2)
		assert_false(is_instance_valid(layer), "the viewer's layer is gone with it")
		await _close(scene)
		Motion.force_live = false


func test_motion_plays_live_and_input_completes_it() -> void:
	var scene := _netrun()
	await _shop(scene)
	_live()
	var card := _item(scene, "Stickers", 0) as ZineCard
	assert_eq(_drag(scene.drops, card, "deck"), "dropped")
	var lands: Array = scene.drops.flights.filter(func(f: Dictionary) -> bool: return f["kind"] == "land")
	assert_eq(lands.size(), 1, "the card's copy lands on the CARDS tag")
	assert_not_null((lands[0]["node"] as Node).find_child("Stamp", false, false), "stamped SOLD")
	assert_eq(FlightFx.active_count(scene), 0, "the click's flight does not play as well")
	var key := InputEventKey.new()
	key.keycode = KEY_A
	key.pressed = true
	scene.drops._input(key)
	assert_false(scene.drops.busy(), "a press during the landing completes it")
	# The shredder: the card feeds into its mouth, strips run out.
	scene.open_remove()
	await _frames(2)
	var view := scene.get_node("DeckView") as DeckView
	var layer: DropLayer = scene.modal_drops
	assert_eq(_drag(layer, view.card(0), "shred"), "dropped")
	assert_eq(layer.flights.size(), 1, "the card's copy goes into the shredder")
	assert_eq(RunManager.netrun.run.card_removals, 1, "the state is final at once")
	assert_not_null(scene.get_node_or_null("DeckView"), "the viewer holds while the shred plays")
	# Wait for the strips themselves (they start once the feed is under way), not a fixed
	# share of the feed: a slow frame could run past them (Test suite: bounded waits).
	await BoundedWait.until(get_tree(), func() -> bool: return is_instance_valid(layer) and not layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "strips").is_empty(), BoundedWait.motion_limit([&"loadout_swap", &"shred_feed"]))
	assert_false(layer.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "strips").is_empty(), "paper strips run out")
	layer._input(key)
	assert_false(layer.busy(), "a press completes it")
	await _frames(2)
	assert_null(scene.get_node_or_null("DeckView"), "and the viewer closes, as REMOVE closes it")
	assert_false(is_instance_valid(layer), "the layer frees itself")
	assert_not_null(scene.get_viewport().gui_get_focus_owner(), "focus is back on the Modem")
	await _close(scene)


func test_views_never_change_game_state() -> void:
	var scene := _netrun()
	await _shop(scene)
	_live()
	var before := _hash()
	var profile := JSON.stringify(RunManager.profile.to_dict())
	for row in ["Stickers", "Chips", "Daemons", "Slices"]:
		var item := _item(scene, row, 0)
		scene.drops.begin_drag(item, item.get_meta(DropLayer.SOURCE_META))
		for t in scene.drops.targets:
			scene.drops._can_drop_data(scene.drops.get_global_transform().affine_inverse() * scene.drops.locate(t).get_center(), {"drop_layer": scene.drops.get_instance_id()})
		scene.drops.cancel()
		scene.drops.start_carry(item)
		for k in 8:
			scene.drops.step_aim(1)
		scene.drops.cancel()
	scene.open_remove()
	await _frames(2)
	var view := scene.get_node("DeckView") as DeckView
	scene.modal_drops.start_carry(view.card(0))
	scene.modal_drops.cancel()
	view.close()
	await get_tree().create_timer(0.3).timeout  # fixed-wait-ok: any point mid-motion; finish_all then shows the end state
	scene.drops.finish_all()
	assert_eq(_hash(), before, "picking up, aiming, checking and putting back left the run and the campaign as they were")
	assert_eq(JSON.stringify(RunManager.profile.to_dict()), profile, "and the profile")
	# The dry run is a copy: using it touches nothing real.
	var dry: NetrunSession = scene.dry_session()
	assert_eq(dry.state_hash(), RunManager.netrun.state_hash(), "the dry run starts as the run")
	dry.buy("cards", 0)
	dry.campaign.heat += 10
	assert_eq(_hash(), before, "and changing it changes nothing real")
	await _close(scene)


func test_the_new_pieces_keep_the_layout_at_each_text_size() -> void:
	for scale in [1.0, 1.3, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		var scene := _netrun()
		await _shop(scene)
		await _frames(3)
		var mini := scene._panel.find_child("SpinnerMini", true, false) as Control
		var remove_win := scene._panel.find_child("RemoveCard", true, false).get_parent().get_parent().get_parent() as Control
		assert_true(remove_win.get_global_rect().grow(0.5).encloses(mini.get_global_rect()), "the spinner sits in the REMOVE A CARD window at %.1f" % scale)
		assert_true(SCREEN.encloses(mini.get_global_rect()), "on screen at %.1f" % scale)
		for id in ["LeaveModem", "LeaveIcon", "Wallet", "RemoveCard"]:
			var other := (scene._panel.find_child(id, true, false) as Control).get_global_rect()
			assert_false(mini.get_global_rect().intersects(other), "the spinner covers no %s at %.1f" % [id, scale])
		for k in 6:
			var pad := (mini as SpinnerMini).pad(k)
			if pad != null:
				assert_true(mini.get_global_rect().grow(0.5).encloses(pad.get_global_rect()), "slot %d's pad on the wheel at %.1f" % [k, scale])
		# The deck viewer keeps its window on the canvas with the SHRED tile.
		scene.open_remove()
		await _frames(3)
		var view := scene.get_node("DeckView") as DeckView
		assert_true(view.window.get_global_rect().grow(0.5).encloses(view.shred_tile.get_global_rect()), "SHRED in the viewer at %.1f" % scale)
		assert_true(view.window.get_global_rect().end.y <= SCREEN.end.y + 0.5, "the viewer fits the canvas at %.1f: %s" % [scale, view.window.get_global_rect()])
		view.close()
		await _frames(2)
		# The UPGRADE viewer: the slice to install beside the wheel, over no slot.
		scene.open_overwrite(0)
		await _frames(3)
		var sv := scene.get_node("SpinnerView") as SpinnerView
		var chip := sv.find_child("InstallSlice", true, false) as Control
		assert_true(sv.window.get_global_rect().grow(0.5).encloses(chip.get_global_rect()), "the slice in the viewer at %.1f" % scale)
		for k in 6:
			var pad := sv.slot_pad(k)
			if pad != null:
				assert_false(chip.get_global_rect().intersects(pad.get_global_rect()), "the slice covers no slot at %.1f" % scale)
		sv.close()
		await _frames(2)
		# A Firmware offer: the spinner beside the stickers, all in the window, Skip on screen.
		await _loot(scene, "firmware", _ids(&"FirmwareData").slice(0, 3))
		await _frames(3)
		var loot_mini := scene._panel.find_child("SpinnerMini", true, false) as Control
		var win := scene._panel.find_child("LootRow", true, false) as Control
		assert_true(win.get_global_rect().grow(0.5).encloses(loot_mini.get_global_rect()), "the loot's spinner in its row at %.1f" % scale)
		assert_true(SCREEN.encloses(loot_mini.get_global_rect()), "on screen at %.1f" % scale)
		var skip := (scene._panel.find_child("Skip", true, false) as Control).get_global_rect()
		assert_true(skip.end.y <= SCREEN.end.y and skip.end.x <= SCREEN.end.x, "Skip on screen at %.1f: %s" % [scale, skip])
		assert_true(scene._panel.get_combined_minimum_size().x <= SCREEN.size.x, "the loot page fits the width at %.1f" % scale)
		await _close(scene)
		# The raid interlude with its chips stays inside the screen's width.
		var raid := _raid()
		await _frames(4)
		assert_true(raid._panel.get_combined_minimum_size().x <= SCREEN.size.x, "the raid interlude fits the width at %.1f" % scale)
		await _close(raid)
