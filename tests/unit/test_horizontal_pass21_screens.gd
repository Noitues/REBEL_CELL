extends GutTest
## H21 screens (GAP_ANALYSIS H21 #10-15, #19, #21; DECISIONS "H21 screens"): an icon on
## every stat tag and the same icon wherever the resource shows; subtitles in a band of
## their own that covers no control and no stat tag; the Modem's wallet and price tags
## (the RAM circle keeps the card's RAM cost); slot names in the socket lists; event
## choice outcomes as icons; icons on menus and Skip / Leave; route buttons that differ
## and say what the node is on every device; big text that reaches the cards, tags and
## notes and columns that scroll; TextDb for content text; one name for JACK IN.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const TITLE := "res://scenes/menu/title_scene.tscn"
const SLOT := "gut_s21_screens"
const CANVAS := Vector2(1280, 720)
const LONG_LINE := "Runner, the compliance office has flagged your cell for audit. Keep the needle off the Miss slice, bank the Rack before the auditors land, and do not let the Heat climb past the next threshold or the whole district locks down for a week."

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _translation: Translation = null
var _locale_before: String = "en"
## A locale of the test's own (the shipped "en" strings would answer first).
const TEST_LOCALE := "xx"


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if _translation != null:
		TranslationServer.set_locale(_locale_before)
		TranslationServer.remove_translation(_translation)
		_translation = null
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	Dialogue.clear()
	Dialogue.dock_default()
	AudioDirector.muted = false
	get_tree().paused = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 4) -> void:
	for i in n:
		await get_tree().process_frame


## `path` inside a 1280x720 holder (the design canvas).
func _open(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	return scene


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


## Every visible, usable control under `root` (buttons, fields, sliders).
func _controls(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		if (n is BaseButton and not (n as BaseButton).disabled and (n as Control).mouse_filter != Control.MOUSE_FILTER_IGNORE) or n is LineEdit or (n is Range and not (n is ScrollBar)):
			out.append(n)
	return out


## The global rect of every stat tag under `root`.
func _tag_rects(root: Node) -> Array[Rect2]:
	var out: Array[Rect2] = []
	for n in _all(root):
		if n is HudStats and (n as HudStats).is_visible_in_tree():
			var st := n as HudStats
			for r in st.tag_rects():
				out.append(Rect2(st.get_global_rect().position + r.position, r.size).grow(2.0))
	return out


## Two claimed nodes beside the home server, an Armory, and a pending raid.
func _raid_campaign() -> CampaignState:
	var c := RunManager.campaign
	var grid_data := RunManager.corporation.city_grid
	var claimed := 0
	for sd in grid_data.sites:
		if sd.tier == 1 and sd.id != grid_data.home_site_id and sd.objective == RC.SiteObjective.NONE and claimed < 2:
			var s := c.grid.site(sd.id)
			s["status"] = GridState.SiteStatus.CLAIMED
			s["node_type"] = "firewall_relay"
			s["integrity"] = 30
			s["max_integrity"] = 30
			s["assets"] = ["turret"] if claimed == 0 else []
			claimed += 1
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	return c


func _netrun() -> Control:
	var scene := _open(NETRUN)
	scene.start_run(1)
	return scene


func _shop(scene: Control) -> void:
	var s := RunManager.netrun
	s.run.cycles = 120
	s._open_shop()
	scene._show_current()


func _event(scene: Control, id: StringName = &"ev_leash_on_the_floor") -> void:
	var run := RunManager.netrun.run
	run.event_id = id
	run.phase = RunState.Phase.EVENT
	scene._show_current()


func _loot(scene: Control, kind: String = "card", options: Array = ["twist", "jam", "cache"]) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": kind, "options": options})
	run.phase = RunState.Phase.REWARD
	scene._show_current()


func _raw_ids(op: OperativeState) -> PackedStringArray:
	var out := PackedStringArray()
	for id in op.slot_slice_ids:
		out.append(String(id))
	for id in op.slot_firmware_ids:
		if id != &"":
			out.append(String(id))
	return out


# --- #10 an icon on every stat tag, the same icon everywhere ------------------------------

func test_every_stat_tag_has_its_icon_on_every_screen() -> void:
	var hq := _open(HQ)
	await _frames()
	var st: HudStats = hq.hud.stats
	assert_eq(st.items.size(), 7, "HEAT SCHEMATICS HOME EXPLOITS RAIDS ICE CREW")
	for i in st.items.size():
		assert_true(StatIcon.ALL.has(st.icon_of(i)), "HQ tag %s has an icon" % st.items[i][0])
		assert_ne(st._get_tooltip(st.tag_rects()[i].get_center()), "", "HQ tag %s says what it means" % st.items[i][0])
	var scene := _netrun()
	await _frames()
	var run_tags: HudStats = scene.hud.stats
	var names := PackedStringArray()
	for i in run_tags.items.size():
		names.append(String(run_tags.items[i][0]))
		assert_true(StatIcon.ALL.has(run_tags.icon_of(i)), "run tag %s has an icon" % run_tags.items[i][0])
		assert_ne(run_tags._get_tooltip(run_tags.tag_rects()[i].get_center()), "", "run tag %s has a tooltip" % run_tags.items[i][0])
	for want in ["HP", "CYCLES", "CARDS", "RANK", "BANKED"]:
		assert_true(names.has(want), "the run's %s tag" % want)
	assert_eq(run_tags.icon_of(names.find("CYCLES")), StatIcon.CYCLES)
	assert_eq(run_tags.icon_of(names.find("HP")), StatIcon.HP)
	RunManager.netrun.run.outcome = RunState.Outcome.COMPLETED
	RunManager.netrun.run.phase = RunState.Phase.ENDED
	scene._show_end()
	await _frames()
	var end_tags := scene._panel.find_child("RunTags", true, false) as HudStats
	for i in end_tags.items.size():
		assert_true(StatIcon.ALL.has(end_tags.icon_of(i)), "run end tag %s has an icon" % end_tags.items[i][0])
	var title := _open(TITLE)
	await _frames()
	var profile := title._panel.find_child("Tags", true, false) as HudStats
	for i in profile.items.size():
		assert_true(StatIcon.ALL.has(profile.icon_of(i)), "profile tag %s has an icon" % profile.items[i][0])


func test_every_icon_draws() -> void:
	var canvas: Control = add_child_autofree(Control.new())
	canvas.size = Vector2(64, 64)
	var drawn := []
	canvas.draw.connect(func() -> void:
		for k in StatIcon.ALL:
			StatIcon.draw(canvas, Vector2(32, 32), 12.0, k, Palette.PAPER)
		drawn.append(true))
	canvas.queue_redraw()
	await _frames(3)
	assert_false(drawn.is_empty(), "every StatIcon kind drew")
	for tag in StatIcon.TAG_KINDS:
		assert_true(StatIcon.ALL.has(StatIcon.kind_for(tag)), "%s maps to an icon" % tag)


func test_cell_status_badges_are_labelled_and_share_the_tag_icons() -> void:
	var c := RunManager.campaign
	c.armory = [&"turret", &"turret", &"decoy"]
	var hq := _open(HQ)
	await _frames()
	var badges: Node = hq._panel.find_child("CellBadges", true, false)
	var home := badges.find_child("HomeBadge", false, false) as Badge
	var exploits := badges.find_child("ExploitsBadge", false, false) as Badge
	var armory := badges.find_child("ArmoryBadge", false, false) as Badge
	assert_true(home.text.begins_with("HOME"), "house 50/50 is HOME")
	assert_true(exploits.text.begins_with("EXPLOITS"), "diamond 0/3 is EXPLOITS")
	assert_true(armory.text.begins_with("ARMORY"), "the Armory count is ARMORY")
	assert_eq(home.icon_kind, StatIcon.kind_for("HOME"), "same icon as the HOME tag")
	assert_eq(exploits.icon_kind, StatIcon.kind_for("EXPLOITS"), "same icon as the EXPLOITS tag")
	assert_eq(armory.icon_kind, StatIcon.ARMORY)
	for b in badges.get_children():
		var badge := b as Badge
		assert_ne(badge.tooltip_text, "", "%s has a tooltip" % badge.text)
		if badge.asset_id != &"":
			var name := TextDb.t(RunManager.lookup().get_content(badge.asset_id), "display_name")
			assert_true(badge.text.begins_with(name), "the asset icon is named: '%s'" % badge.text)
			assert_false(badge.text.begins_with("x"), "no bare x1")


# --- #11 subtitles clear of controls and stat tags; the wallet ------------------------------

func _assert_clear(root: Node, label: String) -> void:
	Dialogue.clear()
	Dialogue.say(RC.Voice.DISPATCH, LONG_LINE)
	await _frames(3)
	assert_true(Dialogue.is_showing(), "%s: a subtitle is up" % label)
	var bar := Rect2(Dialogue.bar.global_position, Dialogue.bar.size)
	assert_true(bar.end.x <= CANVAS.x + 0.5 and bar.end.y <= CANVAS.y + 0.5, "%s: the subtitle is on screen (%s)" % [label, bar])
	for c in _controls(root):
		var r := c.get_global_rect()
		assert_false(bar.intersects(r), "%s: the subtitle (%s) covers %s '%s' at %s (text %.1f)" % [label, bar, c.get_class(), c.get("text"), r, Settings.text_scale])
	for r in _tag_rects(root):
		assert_false(bar.intersects(r), "%s: the subtitle (%s) covers a stat tag at %s (text %.1f)" % [label, bar, r, Settings.text_scale])
	var strip: Node = null
	for n in _all(root):
		if n is SubtitleStrip and (n as Control).is_visible_in_tree():
			strip = n
	assert_not_null(strip, "%s: the screen has its subtitle band" % label)
	if strip != null:
		var band := (strip as Control).get_global_rect()
		assert_true(bar.position.y >= band.position.y - 0.5 and bar.end.y <= band.end.y + 0.5, "%s: the bar (%s) stays in its band (%s)" % [label, bar, band])
	Dialogue.clear()


func test_subtitles_cover_no_control_and_no_stat_tag_on_any_screen() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		_raid_campaign()
		var hq := _open(HQ)
		await _frames()
		await _assert_clear(hq, "HQ")
		hq.show_grid()
		await _frames()
		await _assert_clear(hq, "Grid")
		hq.show_raid()
		await _frames()
		await _assert_clear(hq, "raid setup")
		hq.get_parent().queue_free()
		await _frames(2)
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames()
		await _assert_clear(scene, "route")
		_shop(scene)
		await _frames()
		await _assert_clear(scene, "Modem")
		_event(scene)
		await _frames()
		await _assert_clear(scene, "event")
		_loot(scene)
		await _frames()
		await _assert_clear(scene, "loot")
		scene.get_parent().queue_free()
		await _frames(2)
		var title := _open(TITLE)
		await _frames()
		await _assert_clear(title, "title")
		title.get_parent().queue_free()
		await _frames(2)


func test_a_fight_gets_its_height_back_and_its_own_dock() -> void:
	var scene := _netrun()
	await _frames()
	assert_true(scene.subtitle_strip.visible, "the route has the band")
	scene.enter_node(RunManager.netrun.available_nodes()[0])
	await _frames()
	if scene.combat_scene != null:
		assert_false(scene.subtitle_strip.visible, "a fight docks its own subtitles and keeps the height")
		assert_true(scene.hud.stats.get_combined_minimum_size().y <= HudBar.BAND_HEIGHT + 0.5, "the tags keep the top bar's height in a fight")


func test_the_modem_shows_the_wallet() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		_shop(scene)
		await _frames()
		var wallet := scene._panel.find_child("Wallet", true, false) as HudStats
		assert_not_null(wallet, "the Modem has its wallet")
		assert_eq(String(wallet.items[0][1]), str(RunManager.netrun.run.cycles), "the Cycles you have")
		assert_eq(wallet.icon_of(0), StatIcon.CYCLES, "with the coin")
		assert_ne(wallet._get_tooltip(wallet.tag_rects()[0].get_center()), "", "and says what it is")
		var r := wallet.get_global_rect()
		assert_true(wallet.is_visible_in_tree() and r.end.y <= CANVAS.y and r.end.x <= CANVAS.x, "on screen at text %.1f: %s" % [scale, r])
		scene.get_parent().queue_free()
		await _frames(2)


# --- #12 price tags, RAM circles, slot names ------------------------------------------------

func test_modem_prices_hang_on_tags_and_the_circle_keeps_the_ram_cost() -> void:
	var scene := _netrun()
	_shop(scene)
	await _frames()
	var s := RunManager.netrun
	var stickers: Node = scene._panel.find_child("Stickers", true, false)
	for i in stickers.get_child_count():
		var card := stickers.get_child(i) as ZineCard
		var data := s.lookup.get_content(StringName(String(s.run.shop["cards"][i]))) as CardData
		assert_eq(card.price, int(s.run.shop["card_prices"][i]), "%s: the price is on its tag" % data.id)
		assert_eq(card.cost, data.ram_cost, "%s: the circle is the RAM cost" % data.id)
		assert_false(card.pictos.is_empty() and not ZineCard.pictos_of(data).is_empty(), "%s: pictograms (with_card)" % data.id)
		var tag := card.price_tag_rect()
		assert_true(Rect2(Vector2.ZERO, card.size).encloses(tag), "%s: the tag sits on the card" % data.id)
	for n in _all(scene._panel):
		if n is ZineCard and (n as ZineCard).look != ZineCard.Look.STICKER:
			assert_true((n as ZineCard).price >= 0, "%s: every tile shows its price" % (n as ZineCard).card_title)
			assert_eq((n as ZineCard).cost, -1, "%s: no price in a cost circle" % (n as ZineCard).card_title)
	var shred := scene._panel.find_child("RemoveCard", true, false) as ZineCard
	assert_eq(shred.price, s.card_removal_price())


func test_socket_lists_name_slots_not_ids() -> void:
	var scene := _netrun()
	_shop(scene)
	await _frames()
	var op := RunManager.netrun.run.operative
	op.slot_firmware_ids[0] = &"barbed_wire" if RunManager.lookup().get_content(&"barbed_wire") != null else op.slot_firmware_ids[0]
	scene._show_current()
	await _frames()
	var raw := _raw_ids(op)
	var pick := scene._panel.find_child("SocketPick", true, false) as OptionButton
	if pick != null:
		for i in pick.item_count:
			var t := pick.get_item_text(i)
			assert_string_contains(t, "Slot %d" % (i + 1))
			for id in raw:
				assert_false(t.contains(id), "no raw id '%s' in '%s'" % [id, t])
	for k in op.slot_slice_ids.size():
		var t: String = scene.slot_name(op, k)
		for id in raw:
			assert_false(t.contains(id), "slot name without '%s': %s" % [id, t])
	_loot(scene, "firmware", [String(RunManager.lookup().ids_of_class(&"FirmwareData")[0])])
	await _frames()
	var slot_pick := scene._panel.find_child("SlotPick", true, false) as OptionButton
	assert_not_null(slot_pick, "the loot's socket list")
	for i in slot_pick.item_count:
		for id in raw:
			assert_false(slot_pick.get_item_text(i).contains(id), "loot socket list without '%s'" % id)


# --- #13 event outcomes as icons; icons on menus ---------------------------------------------

func test_event_choice_outcomes_match_the_data() -> void:
	var c := RunManager.campaign
	c.ice_level = 20  # Heat scaling in force where the ladder adds it
	var scene := _netrun()
	await _frames()
	var s := RunManager.netrun
	var checked := 0
	for id in s.lookup.ids_of_class(&"TerminalEventData"):
		var ev := s.lookup.get_content(id) as TerminalEventData
		for choice in ev.choices:
			var items := OutcomeRow.of_choice(s, choice)
			var expect: Array[Dictionary] = []
			if choice.cycle_cost > 0:
				expect.append({"kind": StatIcon.CYCLES, "amount": -choice.cycle_cost})
			if s.choice_hp_loss(choice) > 0:
				expect.append({"kind": StatIcon.HP, "amount": -s.choice_hp_loss(choice)})
			# H22 #12 (updated on purpose): heal and Heat as they will apply (capped).
			var hp := maxi(0, s.run.operative.hp - choice.hp_cost)
			var heat := c.heat
			for e in choice.effects:
				if e == null:
					continue
				if e.type == RC.EffectType.GAIN_CYCLES and e.amount != 0:
					expect.append({"kind": StatIcon.CYCLES, "amount": e.amount})
				elif e.type == RC.EffectType.MODIFY_HEAT:
					var dh := clampi(heat + HeatRules.scaled_delta(c, e.amount, s.config), 0, s.config.heat_max) - heat
					heat += dh
					expect.append({"kind": StatIcon.HEAT, "amount": dh})
				elif e.type == RC.EffectType.DEAL_DAMAGE:
					hp = maxi(0, hp - e.amount)
				elif e.type == RC.EffectType.HEAL:
					var healed := mini(e.amount, s.run.operative.max_hp - hp)
					hp += healed
					expect.append({"kind": StatIcon.HP, "amount": healed})
				elif e.type == RC.EffectType.GAIN_SCHEMATICS:
					expect.append({"kind": StatIcon.SCHEMATICS, "amount": e.amount})
			if choice.reward != null:
				expect.append({"kind": items[items.size() - 1]["kind"], "amount": 1})
				assert_true([StatIcon.CARDS, StatIcon.FIRMWARE, StatIcon.DAEMON, StatIcon.ARMORY, StatIcon.OPERATIVE].has(items[items.size() - 1]["kind"]), "%s: the reward's icon" % id)
			assert_eq(items.size(), expect.size(), "%s '%s': one icon per outcome" % [id, choice.label])
			for k in mini(items.size(), expect.size()):
				assert_eq(items[k]["kind"], expect[k]["kind"], "%s '%s' item %d" % [id, choice.label, k])
				assert_eq(int(items[k]["amount"]), int(expect[k]["amount"]), "%s '%s' item %d amount" % [id, choice.label, k])
			checked += 1
	assert_true(checked > 0, "events checked")
	# On screen: each choice carries its row, with the same items.
	_event(scene)
	await _frames()
	var ev := s.current_event()
	for i in ev.choices.size():
		var b := scene._panel.find_child("Choice%d" % (i + 1), true, false) as Button
		var row := b.find_child("OutcomeRow", false, false) as OutcomeRow
		# H23 S9 (updated on purpose): the row shows the amounts that change something.
		var want := OutcomeRow.shown(OutcomeRow.of_choice(s, ev.choices[i]))
		if want.is_empty():
			continue
		assert_not_null(row, "choice %d shows its outcome" % i)
		assert_eq(row.items.size(), want.size())
		assert_ne(b.tooltip_text, "", "choice %d has a tooltip" % i)
		assert_true(Rect2(Vector2.ZERO, b.size).grow(1.0).encloses(Rect2(row.position, row.size)), "the icons sit inside the choice")


func test_menus_and_skip_leave_carry_icons() -> void:
	var title := _open(TITLE)
	await _frames()
	for b in _all(title._panel):
		if b is Button and (b as Button).theme_type_variation == &"MenuItem":
			assert_ne(IconMark.kind_of(b), &"", "title item '%s' has an icon" % (b as Button).text)
			assert_ne((b as Button).tooltip_text, "", "title item '%s' has a tooltip" % (b as Button).text)
	var hq := _open(HQ)
	await _frames()
	var menu_items := 0
	for b in _all(hq._panel):
		if b is Button and (b as Button).theme_type_variation == &"MenuItem":
			menu_items += 1
			assert_ne(IconMark.kind_of(b), &"", "CYBERDECK item '%s' has an icon" % (b as Button).text)
			assert_ne((b as Button).tooltip_text, "", "CYBERDECK item '%s' has a tooltip" % (b as Button).text)
	assert_true(menu_items >= 5, "the HQ menu")
	var scene := _netrun()
	await _frames()
	for id in ["GridZoom", "SaveQuit"]:
		var b := scene._panel.find_child(id, true, false) as Button
		assert_ne(IconMark.kind_of(b), &"", "%s has an icon" % id)
		assert_ne(b.tooltip_text, "", "%s has a tooltip" % id)
	_loot(scene)
	await _frames()
	assert_eq(IconMark.kind_of(scene._panel.find_child("Skip", true, false)), StatIcon.SKIP, "Skip has its icon")
	RunManager.netrun.run.pending_rewards.clear()
	_shop(scene)
	await _frames()
	var leave := scene._panel.find_child("LeaveIcon", true, false) as IconMark
	assert_not_null(leave, "LEAVE THE MODEM has its icon")
	assert_eq(leave.kind, StatIcon.EXIT)
	assert_ne(leave.tooltip_text, "", "and a tooltip")


# --- #14 route buttons ---------------------------------------------------------------------

func test_route_buttons_differ_and_say_what_the_node_is_on_both_devices() -> void:
	var scene := _netrun()
	await _frames()
	var s := RunManager.netrun
	var available := s.available_nodes()
	for pad in [false, true]:
		Settings.set_pad_active(pad)
		await _frames()
		var seen := {}
		for i in available.size():
			var b := scene._panel.find_child("Node%d" % (i + 1), true, false) as Button
			var node := s.run.map.get_node(available[i])
			assert_false(seen.has(b.text), "route buttons differ (%s): '%s'" % ["pad" if pad else "keys", b.text])
			seen[b.text] = true
			assert_string_contains(b.text, scene.node_word(node), "the button says what the node is")
			assert_true(b.text.begins_with(scene.route_index_text(i)), "an index on every device: '%s'" % b.text)
			assert_eq(IconMark.kind_of(b), scene.node_icon(node), "the node type's icon")
			assert_ne(b.tooltip_text, "", "a tooltip")
		if pad:
			assert_eq(scene.route_index_text(0), "1", "pad: the number")
		else:
			assert_eq(scene.route_index_text(0), Settings.hint(&"card_1"), "keyboard: the key")
		var g: Dictionary = scene.route_graph()
		for n in g["nodes"]:
			var idx := available.find(n["id"])
			if idx >= 0:
				assert_true(String(n["label"]).begins_with(scene.route_index_text(idx)), "the map label carries the same index")
				assert_eq(n["kind"], scene.node_icon(s.run.map.get_node(n["id"])))
	var elite := {"type": RC.InfilNodeType.ROUTER, "elite": true}
	assert_eq(scene.node_word(elite), "Elite fight")
	assert_eq(scene.node_icon(elite), StatIcon.ELITE)
	for t in [RC.InfilNodeType.ROUTER, RC.InfilNodeType.TERMINAL, RC.InfilNodeType.MODEM, RC.InfilNodeType.SERVER_RACK]:
		var node := {"type": t, "elite": false}
		assert_ne(scene.node_word(node), "?")
		assert_true(StatIcon.ALL.has(scene.node_icon(node)))


# --- #15 big text ----------------------------------------------------------------------------

func test_big_text_reaches_cards_tags_notes_and_crew() -> void:
	Settings.set_text_scale(LayoutScales.VERIFIED_MAX)
	_raid_campaign()
	var hq := _open(HQ)
	await _frames()
	assert_true(hq._panel.get_combined_minimum_size().x <= CANVAS.x, "the HQ never runs off the side at 1.6 (a raid pending)")
	assert_true(hq.hud.stats.tag_scale > 1.2, "the stat tags grow (%.2f)" % hq.hud.stats.tag_scale)
	var crew := hq._panel.find_child("Crew_%s" % RunManager.campaign.roster[0].id, true, false) as CrewCard
	var name_label: Label = null
	for n in _all(crew):
		if n is Label and (n as Label).text == RunManager.campaign.roster[0].name.to_upper():
			name_label = n
	assert_eq(name_label.get_theme_font_size(&"font_size"), roundi(CrewCard.NAME_SIZE * LayoutScales.VERIFIED_MAX), "the dossier's name grows")
	var radio := hq._panel.find_child("PirateRadio", true, false) as ZineNote
	# Art pass W1: MSDF faces report fractional heights (no hinting); a RichTextLabel lays
	# each line on whole pixels, so one shown line is the height rounded up.
	var line_h := ceilf(Palette.mono().get_height(roundi(UiTheme.BASE_SIZE * Settings.text_scale)))
	var lines := radio.label.size.y / line_h
	assert_almost_eq(lines, roundf(lines), 0.05, "the radio shows whole lines (%.2f)" % lines)
	hq.open_loadout()
	await _frames()
	var deck := (hq.get_node("LoadoutView") as LoadoutView)._view as DeckView
	for n in _all(deck):
		if n is ZineCard and (n as ZineCard).focus_mode != Control.FOCUS_NONE:
			assert_almost_eq((n as ZineCard).text_scale, LayoutScales.VERIFIED_MAX, 0.01, "deck view cards grow")
			assert_false((n as ZineCard).pictos.is_empty(), "deck view cards show pictograms")
			break
	var scene := _netrun()
	_shop(scene)
	await _frames()
	var stickers: Node = scene._panel.find_child("Stickers", true, false)
	var card := stickers.get_child(0) as ZineCard
	assert_true(card.text_scale > 1.2, "Modem cards grow (%.2f)" % card.text_scale)
	var cards_win := stickers.get_parent().get_parent() as Control
	assert_true(cards_win.get_global_rect().grow(1.0).encloses(card.get_global_rect()), "and stay in their quadrant")
	for n in _all(scene._panel):
		if n is ZineCard and (n as ZineCard).look != ZineCard.Look.STICKER:
			assert_almost_eq((n as ZineCard).text_scale, LayoutScales.VERIFIED_MAX, 0.01, "tile lettering grows")
	for id in ["LeaveModem", "Wallet"]:
		var r := (scene._panel.find_child(id, true, false) as Control).get_global_rect()
		assert_true(r.end.y <= CANVAS.y, "%s on screen at 1.6: %s" % [id, r])
	_loot(scene)
	await _frames()
	var loot: Node = scene._panel.find_child("Stickers", true, false)
	assert_true((loot.get_child(0) as ZineCard).text_scale > 1.2, "loot cards grow")
	assert_false((loot.get_child(0) as ZineCard).pictos.is_empty(), "loot cards show pictograms")
	var skip := (scene._panel.find_child("Skip", true, false) as Control).get_global_rect()
	assert_true(skip.end.y <= CANVAS.y, "Skip on screen at 1.6: %s" % skip)
	var title := _open(TITLE)
	await _frames()
	var plan := title._panel.find_child("PlanNote", true, false) as ZineNote
	assert_true(plan.label.get_content_height() <= plan.label.size.y + 1.0, "the plan note shows 1. BREACH at 1.6 (%d > %d)" % [plan.label.get_content_height(), plan.label.size.y])


func test_grid_side_column_scrolls_and_the_hq_says_there_is_more_below() -> void:
	for scale in [1.0, LayoutScales.VERIFIED_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		_raid_campaign()
		var hq := _open(HQ)
		await _frames()
		var page := hq.get_node("PageScroll") as ScrollContainer if hq.has_node("PageScroll") else null
		if page == null:
			for n in _all(hq):
				if n is ScrollContainer and n.name == "PageScroll":
					page = n
		assert_not_null(page)
		var bar := page.get_v_scroll_bar()
		if bar.max_value - bar.page > 1.0:
			assert_true(hq.more_hint.visible, "MORE BELOW while the Black Market is below the fold (text %.1f)" % scale)
			assert_ne(hq.more_hint.tooltip_text, "")
			hq.more_hint.scroll_on()
			await _frames()
			assert_true(page.scroll_vertical > 0, "pressing it scrolls on")
		hq.show_grid()
		await _frames()
		var side := hq._panel.find_child("GridSideScroll", true, false) as ScrollContainer
		assert_not_null(side, "the side column scrolls")
		assert_true(side.follow_focus, "the pad scrolls it by focus")
		assert_ne(side.mouse_filter, Control.MOUSE_FILTER_IGNORE, "the wheel reaches it")
		assert_true(side.get_global_rect().end.y <= CANVAS.y + 0.5, "the column ends on screen (text %.1f): %s" % [scale, side.get_global_rect()])
		var runs := hq._panel.find_child("RunsOpen", true, false) as Control
		assert_true(side.is_ancestor_of(runs), "RUNS OPEN NOW is inside the scrolling column")
		side.ensure_control_visible(runs)
		await _frames()
		var first_run: Control = null
		for n in _all(runs):
			if n is Button:
				first_run = n
				break
		side.ensure_control_visible(first_run)
		await _frames()
		assert_true(side.get_global_rect().grow(1.0).encloses(first_run.get_global_rect()), "a run button scrolls into view (text %.1f)" % scale)
		hq.get_parent().queue_free()
		await _frames(2)


# --- #19 TextDb, #21 naming ------------------------------------------------------------------

func test_new_hq_code_reads_content_text_through_textdb() -> void:
	var c := _raid_campaign()
	var lookup := RunManager.lookup()
	var cls := RunManager.available_classes()[0]
	var boost := RunManager.config().netrun_boosts[0]
	var raid := CampaignRules.raid_data(c.pending_raids[0], lookup)
	var asset := lookup.get_content(&"decoy")
	_translation = Translation.new()
	_translation.locale = TEST_LOCALE
	_translation.add_message(TextDb.key_for(cls, "display_name"), "XL_CLASS")
	_translation.add_message(TextDb.key_for(boost, "display_name"), "XL_BOOST")
	_translation.add_message(TextDb.key_for(raid, "display_name"), "XL_RAID")
	_translation.add_message(TextDb.key_for(asset, "display_name"), "XL_ASSET")
	TranslationServer.add_translation(_translation)
	_locale_before = TranslationServer.get_locale()
	TranslationServer.set_locale(TEST_LOCALE)
	var hq := _open(HQ)
	await _frames()
	var recruit := hq._panel.find_child("Recruit_%s" % cls.id, true, false) as Button
	assert_string_contains(recruit.text, "XL_CLASS", "recruit button")
	var boost_btn := hq._panel.find_child("Boost_%s" % boost.id, true, false) as Button
	assert_string_contains(boost_btn.text, "XL_BOOST", "boost button")
	var raid_btn := hq._panel.find_child("RaidPending", true, false) as Button
	assert_string_contains(raid_btn.text, "XL_RAID", "raid pending button")
	var asset_named := false
	for b in hq._panel.find_child("CellBadges", true, false).get_children():
		asset_named = asset_named or (b as Badge).text.begins_with("XL_ASSET")
	assert_true(asset_named, "asset badge")
	hq.show_raid()
	await _frames()
	var card := hq._panel.find_child("RaidCard", true, false) as TerminalWindow
	assert_string_contains(card.title, "XL_RAID", "raid card title")


func test_one_name_for_jack_in_and_names_on_the_title() -> void:
	var hq := _open(HQ)
	await _frames()
	var jack := hq._panel.find_child("JackIn", true, false) as ZineStamp
	assert_string_contains(jack.tooltip_text, "Site", "the HQ JACK IN says: pick a Site")
	var jack_text := jack.stamp_text
	hq.show_grid()
	await _frames()
	var go := hq._panel.find_child("Launch", true, false) as Button
	assert_eq(go.text, jack_text, "the Site card's button is JACK IN too")
	assert_eq(IconMark.kind_of(go), StatIcon.JACK_IN)
	var title := _open(TITLE)
	await _frames()
	var corp := RunManager.lookup().get_content(RunManager.DEFAULT_CORPORATION) as CorporationData
	var line: String = title._describe({"corporation": String(corp.id), "heat": 14, "ice": 0, "runs": 0, "state": "active", "in_run": false})
	assert_true(line.begins_with(TextDb.t(corp, "display_name")), "the Continue line names the corporation: %s" % line)
	var tags := title._panel.find_child("Tags", true, false) as HudStats
	for it in tags.items:
		assert_ne(String(it[1]), "none", "a number or a dash, never 'none'")
	assert_eq(HudStats.ice_value(-1), HudStats.NO_VALUE)
	assert_eq(HudStats.ice_value(3), "3")
