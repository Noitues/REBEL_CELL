extends GutTest
## Animation pass ANIM-4 (HQ drag and drop): every drag applies exactly the state change
## its button path makes (raid assets, placed assets, crew posts, JACK IN, recruits,
## boosts, Rank 3 ring segments); a refused or cancelled drop changes nothing and the item
## glides home; the keyboard and pad reach every target; reduce effects and headless show
## the end state at once; the new pieces keep the layout at 1.0 / 1.3 / 1.6; the views
## never change game state; raid asset drops call the ANIM-5 landing and update the
## forecast.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

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
	RunManager.save_slot = "gut_anim4"
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


func _scene() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _close(hq: Control) -> void:
	hq.get_parent().queue_free()
	await _frames(2)


## The HQ with a campaign like --demo-raid: the first Site cleared and claimed (a firewall
## relay, two asset slots), a turret on it, two assets left in the Armory, a raid pending;
## `safehouse` also clears and claims a second Site as a safehouse (a station slot).
func _campaign(hq: Control, safehouse: bool = false) -> StringName:
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.schematics = 400
	var corp := RunManager.corporation
	var grid_data := corp.city_grid
	var first: StringName = grid_data.get_site(grid_data.home_site_id).links[0]
	CampaignRules.on_run_completed(c, corp, RunManager.config(), hq._demo_run(first))
	CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	CampaignRules.deploy_asset(c, RunManager.config(), RunManager.lookup(), 0, first)
	var second: StringName = &""
	if safehouse:
		for sd in grid_data.sites:
			if sd == null or sd.id == first or sd.id == grid_data.home_site_id or not sd.claimable:
				continue
			CampaignRules.on_run_completed(c, corp, RunManager.config(), hq._demo_run(sd.id))
			if CampaignRules.claim_error(c, corp, RunManager.config(), RunManager.lookup(), sd.id, &"safehouse", RunManager.profile) == "":
				CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), sd.id, &"safehouse", RunManager.profile)
				second = sd.id
				break
	return second


func _first(hq: Control) -> StringName:
	var grid_data: CityGridData = RunManager.corporation.city_grid
	return grid_data.get_site(grid_data.home_site_id).links[0]


func _hash() -> int:
	return RunManager.campaign.state_hash()


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


## Picks up `source`'s item on `layer` (as a mouse drag leaving it) and lets go over
## target `id`.
func _drag(layer: DropLayer, source: Control, id: String) -> String:
	var data: Variant = layer.begin_drag(source, source.get_meta(DropLayer.SOURCE_META))
	assert_not_null(data, "the drag starts")
	return layer.drop_on(id)


# --- Each drag = its button path ---------------------------------------------------------------

func test_asset_drop_on_a_node_matches_picking_the_node_then_the_card() -> void:
	var hq := _scene()
	_campaign(hq)
	var home: StringName = RunManager.campaign.grid.home_site_id
	hq.show_raid()
	await _frames(4)
	# The button path: pick CORE as the target, then press the TURRET's card.
	hq.select_target(home)
	await _frames(2)
	var card := hq._panel.find_child("AssetCards", true, false).get_child(0) as AssetCard
	card.pressed.emit()
	var button_hash := _hash()
	await _close(hq)
	RunManager.reset()
	hq = _scene()
	_campaign(hq)
	hq.show_raid()
	await _frames(4)
	var before_verdict := (hq._panel.find_child("Projection", true, false) as ForecastStamp).verdict
	card = hq._panel.find_child("AssetCards", true, false).get_child(0) as AssetCard
	assert_eq(_drag(hq.drops, card, "node:%s" % home), "dropped")
	assert_eq(_hash(), button_hash, "the drop made the button path's change")
	assert_eq(StringName(String(hq.city_overlay._drop.get("site", ""))), home, "the ANIM-5 landing plays on the node")
	var stamp := hq._panel.find_child("Projection", true, false) as ForecastStamp
	assert_eq(stamp.verdict, hq.raid_verdict(RunManager.project_raid()), "the forecast stamp shows the new projection")
	assert_true(before_verdict != "", "a forecast before too")
	assert_eq(hq.selected_site, home, "the node dropped on is the target now")
	await _close(hq)


func test_asset_drop_on_its_node_row_hits_the_row_and_matches() -> void:
	var hq := _scene()
	_campaign(hq)
	var first := _first(hq)
	hq.show_raid()
	await _frames(4)
	var card := hq._panel.find_child("AssetCards", true, false).get_child(1) as AssetCard
	var src: Dictionary = card.get_meta(DropLayer.SOURCE_META)
	hq.drops.begin_drag(card, src)
	var row: Rect2 = hq.drops.locate(hq.drops.target("row:%s" % first))
	assert_true(row.has_area(), "YOUR NODES row is a target on screen")
	var expect := RunManager.campaign.duplicate_state()
	CampaignRules.deploy_asset(expect, RunManager.config(), RunManager.lookup(), int(src["index"]), first)
	assert_eq(hq.drops.release_at(row.get_center()), "dropped", "letting go over the row drops there")
	assert_eq(_hash(), expect.state_hash(), "the same change as deploy_asset(index, node)")
	await _close(hq)


func test_placed_asset_moves_and_withdraws_like_its_buttons() -> void:
	for to_armory in [true, false]:
		var hq := _scene()
		_campaign(hq)
		var first := _first(hq)
		var home: StringName = RunManager.campaign.grid.home_site_id
		hq.select_target(first)
		await _frames(4)
		var expect := RunManager.campaign.duplicate_state()
		CampaignRules.move_asset(expect, RunManager.config(), RunManager.lookup(), first, 0, &"" if to_armory else home)
		var badge := hq._panel.find_child("Placed_%s_0" % first, true, false) as Control
		assert_not_null(badge, "the placed TURRET's badge")
		var outcome := _drag(hq.drops, badge, "armory" if to_armory else "node:%s" % home)
		assert_eq(outcome, "dropped")
		assert_eq(_hash(), expect.state_hash(), "the same change as %s" % ("Withdraw" if to_armory else "TURRET > CORE"))
		await _close(hq)
		RunManager.reset()


func test_the_node_an_asset_sits_on_is_not_offered_and_the_target_node_drags_its_asset() -> void:
	var hq := _scene()
	_campaign(hq)
	var first := _first(hq)
	hq.select_target(first)
	await _frames(4)
	var badge := hq._panel.find_child("Placed_%s_0" % first, true, false) as Control
	hq.drops.begin_drag(badge, badge.get_meta(DropLayer.SOURCE_META))
	assert_false(hq.drops.offered("node:%s" % first), "where it already is is no target")
	assert_true(hq.drops.takes("armory"), "the Armory takes it back")
	hq.drops.cancel()
	# The map: a press on the picked node keeps the page (it can go on into a drag).
	var panel: Control = hq._panel
	hq.select_target(first)
	assert_eq(hq._panel, panel, "picking the picked node again rebuilds nothing")
	await _close(hq)


func test_crew_station_and_recall_match_their_buttons() -> void:
	var hq := _scene()
	var safe := _campaign(hq, true)
	assert_ne(safe, &"", "a safehouse is claimed")
	hq.show_hq()
	await _frames(4)
	var op: OperativeState = RunManager.campaign.living_operatives()[0]
	var expect := RunManager.campaign.duplicate_state()
	CampaignRules.station(expect, RunManager.lookup(), op.id, safe)
	var dossier := hq._panel.find_child("Crew_%s" % op.id, true, false) as Control
	assert_eq(_drag(hq.drops, dossier, "station:%s" % safe), "dropped")
	assert_eq(_hash(), expect.state_hash(), "the same change as Station on it")
	await _frames(2)
	CampaignRules.recall(expect, op.id)
	dossier = hq._panel.find_child("Crew_%s" % op.id, true, false) as Control
	var home: StringName = RunManager.campaign.grid.home_site_id
	assert_eq(_drag(hq.drops, dossier, "recall:%s" % home), "dropped", "CORE takes a stationed operative back")
	assert_eq(_hash(), expect.state_hash(), "the same change as Recall")
	await _frames(2)
	dossier = hq._panel.find_child("Crew_%s" % op.id, true, false) as Control
	var before := _hash()
	assert_eq(_drag(hq.drops, dossier, "recall:%s" % home), "refused", "an operative at HQ can't be recalled")
	assert_eq(_hash(), before, "a refusal changes nothing")
	await _close(hq)


## ANIM-R1 (designer ruling 2026-09-27: "Drag and drop to start is not intuitive - prefer
## select, then jack in"): a chip dropped on JACK IN only picks the operative in the list;
## the run starts when JACK IN is pressed, the same run as picking them and pressing it.
func test_a_crew_chip_on_jack_in_picks_them_and_only_the_press_starts_the_run() -> void:
	var results := []
	for use_drag in [false, true]:
		var hq := _scene()
		_campaign(hq)
		var c := RunManager.campaign
		c.recruit(RunManager.lookup().get_content(&"ghost") as ClassData)
		var sites := RunManager.launchable_sites()
		assert_false(sites.is_empty(), "a Site to run")
		hq.selected_site = sites[0].id
		hq.show_grid()
		await _frames(4)
		var living := c.living_operatives()
		var who := living[living.size() - 1]
		var pick := hq._panel.find_child("OperativePick", true, false) as OptionButton
		if use_drag:
			var chip := hq._panel.find_child("Chip_%s" % who.id, true, false) as Control
			assert_not_null(chip, "the Site card shows the crew as chips")
			var before := _hash()
			assert_eq(_drag(hq.drops, chip, "jack"), "dropped")
			assert_false(RunManager.has_active_run(), "the drop alone starts no run")
			assert_eq(_hash(), before, "and changes nothing in the campaign")
			assert_eq(pick.selected, living.size() - 1, "it picks the operative in the list")
		else:
			pick.select(living.size() - 1)
		(hq._panel.find_child("Launch", true, false) as Button).pressed.emit()
		assert_true(RunManager.has_active_run(), "the press on JACK IN starts the run")
		results.append([_hash(), RunManager.netrun.run.operative.id if RunManager.netrun != null else &""])
		await _close(hq)
		RunManager.reset()
	assert_eq(results[1], results[0], "the chip's pick then JACK IN starts the same run as the list and the button")


func test_recruit_and_boost_drops_match_their_buttons() -> void:
	for kind in ["recruit", "boost"]:
		var hashes := []
		for use_drag in [false, true]:
			var hq := _scene()
			_campaign(hq)
			hq.show_hq()
			await _frames(4)
			var cfg := RunManager.config()
			var button: Button
			if kind == "recruit":
				button = hq._panel.find_child("Recruit_%s" % RunManager.DEFAULT_CLASS, true, false) as Button
			else:
				button = hq._panel.find_child("Boost_%s" % cfg.netrun_boosts[0].id, true, false) as Button
			if use_drag:
				assert_eq(_drag(hq.drops, button, "roster" if kind == "recruit" else "queue"), "dropped")
			else:
				button.pressed.emit()
			hashes.append(_hash())
			await _close(hq)
			RunManager.reset()
		assert_eq(hashes[1], hashes[0], "a %s dropped on its target = its button" % kind)


func test_a_ring_segment_dropped_on_the_ring_matches_the_segment_list() -> void:
	var hashes := []
	for use_drag in [false, true]:
		var hq := _scene()
		_campaign(hq)
		var op: OperativeState = RunManager.campaign.living_operatives()[0]
		op.rank = 3
		var options := CampaignRules.ring_segment_options(op, RunManager.lookup().get_content(op.class_id) as ClassData)
		assert_false(options.is_empty(), "Rank 3 has segment swaps")
		if use_drag:
			hq.open_loadout(op)
			await _frames(2)
			var view := hq.get_node("LoadoutView") as LoadoutView
			view.show_spinner()
			await _frames(3)
			var chip := view.find_child("Swap_%s" % options[1], true, false) as Control
			assert_not_null(chip, "the swaps sit beside the wheel")
			assert_true(view.drops.targets.size() >= 3, "every inner ring segment is a target")
			assert_eq(_drag(view.drops, chip, "ring:1"), "dropped")
			var shown := view.find_child("RingPad1", true, false)
			assert_not_null(shown, "the spinner shows again")
		else:
			hq.show_hq()
			await _frames(2)
			hq.swap_segment(op.id, 1, options[1])  # the dossier's "seg 1" list
		hashes.append(_hash())
		await _close(hq)
		RunManager.reset()
	assert_eq(hashes[1], hashes[0], "the same swap as the dossier's segment list")


# --- Refusals and cancels ------------------------------------------------------------------------

func test_invalid_drops_change_nothing_and_glide_home() -> void:
	var hq := _scene()
	_campaign(hq)
	var first := _first(hq)
	# Fill the relay's second slot: a third asset there is refused.
	CampaignRules.deploy_asset(RunManager.campaign, RunManager.config(), RunManager.lookup(), 0, first)
	hq.show_raid()
	await _frames(4)
	_live()
	var card := hq._panel.find_child("AssetCards", true, false).get_child(0) as AssetCard
	var before := _hash()
	hq.drops.begin_drag(card, card.get_meta(DropLayer.SOURCE_META))
	assert_ne(String(hq.drops.reasons["node:%s" % first]), "", "the full relay refuses")
	assert_almost_eq(card.modulate.a, DropLayer.SOURCE_DIM, 0.001, "the card has left its slot")
	assert_eq(hq.drops.drop_on("node:%s" % first), "refused")
	assert_eq(_hash(), before, "nothing changed")
	assert_false(hq.drops.flights.filter(func(f: Dictionary) -> bool: return f["kind"] == "home").is_empty(), "the card glides home")
	assert_false(hq.drops.sprites.filter(func(s: Dictionary) -> bool: return s["kind"] == "mark").is_empty(), "the no-entry mark on the node")
	assert_not_null(hq.get_node_or_null("Toast"), "the rules' reason shows")
	hq.drops.finish_all()
	assert_eq(card.modulate.a, 1.0, "home: the card shows again")
	# A drop on nothing: back home, nothing changed.
	hq.drops.begin_drag(card, card.get_meta(DropLayer.SOURCE_META))
	assert_eq(hq.drops.release_at(Vector2(-50, -50)), "cancel")
	assert_eq(_hash(), before, "a cancel changes nothing")
	hq.drops.finish_all()
	assert_eq(card.modulate.a, 1.0)
	await _close(hq)


# --- Keys and pad ----------------------------------------------------------------------------

## Carries `source` on `layer` and steps the aim through every target; returns the values
## aimed (and checks the reticle follows).
func _walk(layer: DropLayer, source: Control) -> Array:
	layer.start_carry(source)
	assert_eq(layer.mode, DropLayer.Mode.CARRY, "picked up")
	var seen := []
	for k in layer.aim_list.size():
		var t := layer.aimed()
		assert_false(t.is_empty(), "a target is aimed")
		assert_true(layer.reticle_visible, "the reticle shows")
		assert_eq(layer.reticle_pos, layer.locate(t).get_center(), "on the aimed target (end state at once headless)")
		if not seen.has(t["value"]):
			seen.append(t["value"])
		layer._input(_press(&"ui_right"))
	return seen


func _offered_values(layer: DropLayer) -> Array:
	var out := []
	for t in layer.targets:
		if layer.offered(t["id"]) and not out.has(t["value"]):
			out.append(t["value"])
	return out


func test_keys_and_pad_reach_every_target_and_drop_like_the_mouse() -> void:
	var hq := _scene()
	var safe := _campaign(hq, true)
	# Raid setup: the Armory card picked up with the pick-up key (X / Space).
	hq.show_raid()
	await _frames(4)
	var card := hq._panel.find_child("AssetCards", true, false).get_child(0) as AssetCard
	card.grab_focus()
	hq.drops._input(_press(&"end_turn"))
	assert_eq(hq.drops.mode, DropLayer.Mode.CARRY, "the pick-up key takes the focused card")
	hq.drops.cancel()
	var values := _walk(hq.drops, card)
	var offered := _offered_values(hq.drops)
	values.sort()
	offered.sort()
	assert_eq(values, offered, "the D-pad reaches every node that takes an asset")
	var aimed: Dictionary = hq.drops.aimed()
	var expect := RunManager.campaign.duplicate_state()
	var outcome := ""
	if hq.drops.takes(aimed["id"]):
		CampaignRules.deploy_asset(expect, RunManager.config(), RunManager.lookup(), 0, aimed["value"])
		outcome = "dropped"
	hq.drops._input(_press(&"ui_accept"))
	assert_eq(hq.drops.last_outcome, outcome if outcome != "" else "refused", "A drops on the aimed node")
	assert_eq(_hash(), expect.state_hash(), "the same change as the mouse")
	await _frames(2)
	# B cancels.
	card = hq._panel.find_child("AssetCards", true, false).get_child(0) as AssetCard
	hq.drops.start_carry(card)
	var before := _hash()
	hq.drops._input(_press(&"ui_cancel"))
	assert_eq(hq.drops.mode, DropLayer.Mode.IDLE, "B puts it back")
	assert_eq(_hash(), before)
	# HQ: a dossier's orders take the pick-up key for their operative; every post is reached.
	hq.show_hq()
	await _frames(4)
	var op: OperativeState = RunManager.campaign.living_operatives()[0]
	var dossier := hq._panel.find_child("Crew_%s" % op.id, true, false) as Control
	(dossier.find_child("Loadout", true, false) as Button).grab_focus()
	hq.drops._input(_press(&"end_turn"))
	assert_eq(hq.drops.mode, DropLayer.Mode.CARRY, "X on a dossier's order carries the operative")
	assert_eq(String(hq.drops.payload.get("op", "")), String(op.id))
	hq.drops.cancel()
	values = _walk(hq.drops, dossier)
	offered = _offered_values(hq.drops)
	assert_eq(values.size(), offered.size(), "every post on the mini-map is reached")
	assert_true(values.has(safe), "the safehouse among them")
	hq.drops.cancel()
	# The pad prompts follow the carry.
	Settings.set_pad_active(true)
	hq.drops.start_carry(dossier)
	assert_string_contains(" | ".join(hq.pad_prompts.texts()), "Drop")
	hq.drops.cancel()
	assert_string_contains(" | ".join(hq.pad_prompts.texts()), "Pick up")
	await _close(hq)


func test_a_click_picks_up_a_chip_and_a_click_on_the_target_drops_it() -> void:
	var hq := _scene()
	_campaign(hq)
	hq.selected_site = RunManager.launchable_sites()[0].id
	hq.show_grid()
	await _frames(4)
	var chip: CrewChip = hq._grid_chips[0]
	chip.pressed.emit()  # a click (or A) on an item that only moves picks it up
	assert_eq(hq.drops.mode, DropLayer.Mode.CARRY)
	assert_eq(hq.drops.aimed().get("id", ""), "jack", "JACK IN is aimed")
	var jack: Rect2 = hq.drops.locate(hq.drops.target("jack"))
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	click.global_position = jack.get_center()
	click.position = jack.get_center()
	hq.drops._input(click)
	assert_eq(hq.drops.last_outcome, "dropped", "a click on JACK IN drops the operative there")
	assert_false(RunManager.has_active_run(), "ANIM-R1 ruling: the drop picks them; no run starts")
	await _close(hq)


# --- End states, layout and state ----------------------------------------------------------------

func test_reduce_effects_and_headless_show_the_end_state_at_once() -> void:
	for reduce in [false, true]:
		var hq := _scene()
		_campaign(hq)
		hq.show_raid()
		await _frames(4)
		if reduce:
			Motion.force_live = true
			Settings.set_reduce_effects(true)
			Fx.apply_settings()
		var card := hq._panel.find_child("AssetCards", true, false).get_child(1) as AssetCard
		hq.drops.begin_drag(card, card.get_meta(DropLayer.SOURCE_META))
		assert_eq(hq.drops.pulse, 1.0, "targets lit, not pulsing")
		assert_null(hq.drops._pulse_tween, "no pulse runs")
		hq.drops.drop_on("node:%s" % RunManager.campaign.grid.home_site_id)
		assert_true(hq.drops.flights.is_empty(), "no flight: the end state at once (%s)" % ("reduce effects" if reduce else "headless"))
		assert_true(hq.drops.sprites.is_empty(), "no stamp or mark")
		assert_false(hq.drops.busy())
		# A click purchase: bought and shown at once.
		hq.show_hq()
		await _frames(3)
		var rb := hq._panel.find_child("Recruit_%s" % RunManager.DEFAULT_CLASS, true, false) as Button
		rb.pressed.emit()
		assert_true(hq.drops.flights.is_empty(), "no purchase flight")
		var c := RunManager.campaign
		var newest := hq._panel.find_child("Crew_%s" % c.roster[c.roster.size() - 1].id, true, false) as Control
		assert_eq(newest.modulate.a, 1.0, "the new operative shows")
		await _close(hq)
		RunManager.reset()
		Motion.force_live = false


func test_motion_plays_live_and_input_completes_it() -> void:
	var hq := _scene()
	_campaign(hq)
	hq.show_hq()
	await _frames(4)
	_live()
	var rb := hq._panel.find_child("Recruit_%s" % RunManager.DEFAULT_CLASS, true, false) as Button
	rb.pressed.emit()
	assert_eq(hq.drops.flights.size(), 1, "the new operative flies from the Black Market to the crew")
	var c := RunManager.campaign
	var newest := hq._panel.find_child("Crew_%s" % c.roster[c.roster.size() - 1].id, true, false) as Control
	assert_eq(newest.modulate.a, 0.0, "the dossier waits for its copy")
	var key := InputEventKey.new()
	key.keycode = KEY_A
	key.pressed = true
	hq.drops._input(key)
	assert_true(hq.drops.flights.is_empty(), "a press during the flight completes it")
	assert_eq(newest.modulate.a, 1.0, "and the dossier shows")
	await _close(hq)


func test_the_new_pieces_keep_the_layout_at_each_text_size() -> void:
	for scale in [1.0, 1.3, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		var hq := _scene()
		_campaign(hq)
		RunManager.campaign.recruit(RunManager.lookup().get_content(&"ghost") as ClassData)
		RunManager.campaign.recruit(RunManager.lookup().get_content(&"rigger") as ClassData)
		hq.selected_site = RunManager.launchable_sites()[0].id
		hq.show_grid()
		await _frames(6)
		var card := hq._panel.find_child("SelectedSite", true, false) as Control
		var chips := hq._panel.find_child("CrewChips", true, false) as Control
		var launch := hq._panel.find_child("Launch", true, false) as Control
		assert_true(card.get_global_rect().grow(0.5).encloses(chips.get_global_rect()), "the chips sit inside the Site card at %.1f" % scale)
		assert_true(SCREEN.encloses(chips.get_global_rect()), "on screen at %.1f" % scale)
		for chip in chips.get_children():
			assert_false((chip as Control).get_global_rect().intersects(launch.get_global_rect()), "a chip covers no JACK IN at %.1f" % scale)
		hq.show_hq()
		await _frames(6)
		var queue := hq._panel.find_child("QueuedBoosts", true, false) as Control
		var market := hq._panel.find_child("BlackMarket", true, false) as Control
		assert_true(market.get_global_rect().grow(0.5).encloses(queue.get_global_rect()), "the next run's kit sits in the Black Market at %.1f" % scale)
		assert_true(hq._panel.get_combined_minimum_size().x <= SCREEN.size.x, "the HQ page stays inside the screen width at %.1f" % scale)
		var op: OperativeState = RunManager.campaign.living_operatives()[0]
		op.rank = 3
		hq.open_loadout(op)
		await _frames(2)
		var view := hq.get_node("LoadoutView") as LoadoutView
		view.show_spinner()
		await _frames(4)
		var side := view.find_child("Side", true, false) as Control
		var window: Control = (view._view as SpinnerView).window
		assert_true(window.get_global_rect().grow(0.5).encloses(side.get_global_rect()), "the swaps sit inside the spinner window at %.1f" % scale)
		for pad in view.find_children("*", "Button", true, false):
			if String(pad.name).begins_with("RingPad") or String(pad.name).begins_with("HubPad"):
				assert_false(side.get_global_rect().intersects((pad as Control).get_global_rect()), "the swaps cover no ring pad at %.1f" % scale)
		# After a drop, nothing of the layer stays on screen.
		var chip := view.find_child("Swap_default", true, false) as Control
		view.drops.begin_drag(chip, chip.get_meta(DropLayer.SOURCE_META))
		view.drops.drop_on("ring:0")
		assert_false(view.drops.busy(), "the end state leaves no flight or mark")
		assert_eq(view.drops.mode, DropLayer.Mode.IDLE)
		await _close(hq)
		RunManager.reset()


func test_views_never_change_game_state() -> void:
	var hq := _scene()
	var safe := _campaign(hq, true)
	hq.show_raid()
	await _frames(4)
	_live()
	var before := _hash()
	var profile := JSON.stringify(RunManager.profile.to_dict())
	var card := hq._panel.find_child("AssetCards", true, false).get_child(0) as AssetCard
	hq.drops.begin_drag(card, card.get_meta(DropLayer.SOURCE_META))
	for t in hq.drops.targets:
		hq.drops._can_drop_data(hq.drops.get_global_transform().affine_inverse() * hq.drops.locate(t).get_center(), {"drop_layer": hq.drops.get_instance_id()})
	hq.drops.cancel()
	hq.drops.start_carry(card)
	for k in 6:
		hq.drops.step_aim(1)
	hq.drops.cancel()
	await get_tree().create_timer(0.3).timeout  # fixed-wait-ok: any point mid-motion; finish_all then shows the end state
	hq.drops.finish_all()
	hq.show_hq()
	await _frames(3)
	var op: OperativeState = RunManager.campaign.living_operatives()[0]
	var dossier := hq._panel.find_child("Crew_%s" % op.id, true, false) as Control
	hq.drops.start_carry(dossier)
	assert_true(hq.drops.offered("station:%s" % safe), "the safehouse is checked (a dry run)")
	hq.drops.cancel()
	var rb := hq._panel.find_child("Recruit_%s" % RunManager.DEFAULT_CLASS, true, false) as Button
	hq.drops.begin_drag(rb, rb.get_meta(DropLayer.SOURCE_META))
	hq.drops.cancel()
	hq.drops.finish_all()
	assert_eq(_hash(), before, "picking up, aiming, checking and putting back left the campaign as it was")
	assert_eq(JSON.stringify(RunManager.profile.to_dict()), profile, "and the profile")
	await _close(hq)


func test_tooltips_and_focus_work_after_a_drop() -> void:
	var hq := _scene()
	_campaign(hq)
	var home: StringName = RunManager.campaign.grid.home_site_id
	hq.show_raid()
	await _frames(4)
	var card := hq._panel.find_child("AssetCards", true, false).get_child(1) as AssetCard
	hq.drops.start_carry(card)
	while hq.drops.aimed().get("value") != home:
		hq.drops.step_aim(1)
	hq.drops.confirm()
	await _frames(3)
	var focused := hq.get_viewport().gui_get_focus_owner()
	assert_not_null(focused, "something has focus after a pad drop")
	assert_eq(String(focused.name), "Target_%s" % home, "the node dropped on")
	for c in hq._panel.find_child("AssetCards", true, false).get_children():
		if c is AssetCard:
			assert_ne((c as AssetCard).tooltip_text, "", "the cards keep their tooltips")
	assert_eq(hq.drops.mouse_filter, Control.MOUSE_FILTER_IGNORE, "the layer lets the mouse through again")
	await _close(hq)
