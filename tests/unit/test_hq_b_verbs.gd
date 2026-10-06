extends GutTest
## HQ-B (d) (M14, designer ruling Q11, final: `q11_a_claim.png`, `q11_b_repair.png`,
## `q11_c_upgrade_patch_chips_vs_stickers.png`): the one pink sticker slot holds the selected
## thing's verb, so it is never empty while a node is selected: JACK IN for a runnable Site,
## CLAIM for a cleared Site of the Cell's (the picked node tile sets the price), REPAIR for a
## DOWN node, UPGRADE for an active node, PATCH for a damaged CORE; the price is a gold tag
## under the sticker (never on it), and it is the rules' own number (the purchase charges it).
## A Site's card shows IF CLEARED (the rules' preview); PATROL IT INSTEAD where the verb is not
## JACK IN.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	AudioDirector.muted = true
	RunManager.save_slot = "gut_hq_b_verbs"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	# Two nodes of the Cell's and a third Site cleared, still to claim.
	for t: StringName in [&"firewall_relay", &"safehouse", &""]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		if t != &"":
			CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	c.pending_raids.clear()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
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


func _hq() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	return scene


func _slot(hq: Control) -> Control:
	return hq._panel.get_node("VerbSlot")


func _price(hq: Control) -> int:
	var tag := _slot(hq).get_node_or_null("VerbPrice") as PriceTag
	assert_not_null(tag, "a gold price tag under the sticker")
	return int(tag.text.split(" ")[0]) if tag != null else -1


func _cleared() -> StringName:
	var c := RunManager.campaign
	for s in RunManager.corporation.city_grid.sites:
		if s != null and c.grid.is_cleared(s.id) and s.claimable:
			return s.id
	return &""


func _node(type_id: StringName) -> StringName:
	var c := RunManager.campaign
	for id in c.grid.claimed_ids():
		if c.grid.node_type_of(id) == type_id:
			return id
	return &""


func test_claim_is_a_sticker_its_tiles_set_the_price_and_the_purchase_charges_it() -> void:
	var c := RunManager.campaign
	var hq := await _hq()
	var site := _cleared()
	assert_ne(site, &"", "a cleared Site to claim")
	hq.select_site(site)
	await _frames(2)
	var sticker := _slot(hq).get_node_or_null("Claim") as VerbSticker
	assert_true(sticker != null and sticker.fill == VerbSticker.Fill.PINK, "CLAIM is the pink sticker")
	assert_false(sticker.text.contains("SCHEM"), "the price is never on the sticker")
	assert_not_null(hq._panel.find_child("PatrolHere", true, false), "PATROL IT INSTEAD on the card")
	# A tile picks the node: the tag follows.
	var tiles := hq._panel.find_child("NodeTiles", true, false) as Control
	assert_not_null(tiles, "the node tiles")
	var pick: MenuChip = null
	for t in tiles.get_children():
		if not (t as MenuChip).disabled and not (t as MenuChip).selected:
			pick = t
			break
	if pick != null:
		var pick_name := String(pick.name)
		pick.pressed.emit()
		await _frames(2)
		assert_true((hq._panel.find_child(pick_name, true, false) as MenuChip).selected, "the picked tile")
	var node := RunManager.lookup().get_content(hq.claim_choice()) as NetworkNodeData
	var price := _price(hq)
	assert_eq(price, node.install_cost, "the tag is the node's install")
	var sch := c.schematics
	(_slot(hq).get_node("Claim") as VerbSticker).pressed.emit()
	await _frames(2)
	assert_true(c.grid.is_claimed(site), "claimed")
	assert_eq(c.grid.node_type_of(site), node.id, "with the picked node")
	assert_eq(c.schematics, sch - price, "preview == result")


func test_repair_is_the_down_nodes_sticker_at_the_rules_price() -> void:
	var c := RunManager.campaign
	var node := _node(&"firewall_relay")
	c.grid.sites[node]["integrity"] = 0
	c.grid.sites[node]["condition"] = GridState.Condition.DOWN
	var hq := await _hq()
	hq.select_site(node)
	await _frames(2)
	assert_not_null(_slot(hq).get_node_or_null("Repair"), "REPAIR is the sticker")
	var price := _price(hq)
	assert_eq(price, CampaignRules.repair_cost(c, RunManager.config(), RunManager.lookup(), node))
	var sch := c.schematics
	(_slot(hq).get_node("Repair") as VerbSticker).pressed.emit()
	await _frames(2)
	assert_true(c.grid.is_active_node(node), "back online")
	assert_eq(c.schematics, sch - price, "preview == result")


func test_upgrade_and_patch_are_stickers_too() -> void:
	var c := RunManager.campaign
	var node := _node(&"safehouse")
	var hq := await _hq()
	hq.select_site(node)
	await _frames(2)
	assert_not_null(_slot(hq).get_node_or_null("Upgrade"), "UPGRADE is the sticker (Q11 final)")
	var price := _price(hq)
	assert_eq(price, CampaignRules.upgrade_cost(c, RunManager.config(), node))
	var sch := c.schematics
	var level := c.grid.upgrade_level_of(node)
	(_slot(hq).get_node("Upgrade") as VerbSticker).pressed.emit()
	await _frames(2)
	assert_eq(c.grid.upgrade_level_of(node), level + 1)
	assert_eq(c.schematics, sch - price, "preview == result")
	c.grid.home_integrity = c.grid.home_max_integrity - 7
	hq.select_site(c.grid.home_site_id)
	await _frames(2)
	assert_not_null(_slot(hq).get_node_or_null("Patch"), "PATCH is the sticker (Q11 final)")
	price = _price(hq)
	sch = c.schematics
	(_slot(hq).get_node("Patch") as VerbSticker).pressed.emit()
	await _frames(2)
	assert_eq(c.grid.home_integrity, c.grid.home_max_integrity)
	assert_eq(c.schematics, sch - price, "preview == result")
	# A full CORE has nothing to do: no sticker, the card says why.
	hq.select_site(c.grid.home_site_id)
	await _frames(2)
	assert_eq(_slot(hq).get_child_count(), 0, "nothing to do on a full CORE")
	assert_not_null(hq._panel.find_child("WhyNot", true, false))


func test_a_runnable_site_shows_if_cleared_with_the_rules_preview() -> void:
	var hq := await _hq()
	var site: SiteData = RunManager.launchable_sites()[0]
	hq.select_site(site.id)
	await _frames(2)
	var gains := hq._panel.find_child("IfCleared", true, false) as Control
	assert_not_null(gains, "IF CLEARED on the card")
	var want: Array = hq.run_gains(site, CampaignRules.clear_preview(RunManager.campaign, RunManager.corporation, RunManager.config(), site, RunManager.lookup()))
	var badges := 0
	for k in gains.get_children():
		if k is Badge:
			badges += 1
	assert_eq(badges, want.size(), "one badge per gain of the rules' preview")
	for b in want:
		(b as Node).free()  # made for the count only (never in the tree)
	assert_not_null(_slot(hq).get_node_or_null("Launch"), "JACK IN for a runnable Site")
	assert_null(_slot(hq).get_node_or_null("VerbPrice"), "JACK IN has no price")


func test_the_verb_is_reachable_by_pad_and_fits_at_big_text() -> void:
	for s in [1.0, 2.0]:
		Settings.set_text_scale(s)
		var hq := await _hq()
		hq.select_site(_node(&"safehouse"))
		await _frames(3)
		var sticker := _slot(hq).get_node("Upgrade") as Control
		var tag := _slot(hq).get_node("VerbPrice") as Control
		var screen: Rect2 = hq._panel.get_global_rect().grow(1.0)
		assert_true(screen.encloses(sticker.get_global_rect()) and screen.encloses(tag.get_global_rect()), "x%.1f: the sticker and its tag on screen" % s)
		assert_false(sticker.get_global_rect().intersects(tag.get_global_rect().grow(-1.0)), "x%.1f: the tag under the sticker, never on it" % s)
		var seen := {}
		var queue: Array[Control] = [hq._panel.get_node("MapCursor")]
		while not queue.is_empty():
			var n: Control = queue.pop_front()
			if seen.has(n):
				continue
			seen[n] = true
			for side in [SIDE_LEFT, SIDE_TOP, SIDE_RIGHT, SIDE_BOTTOM]:
				var nb := n.find_valid_focus_neighbor(side)
				if nb != null and not seen.has(nb):
					queue.append(nb)
		assert_true(seen.has(sticker), "x%.1f: the verb reachable by pad" % s)
		hq.get_parent().free()
