extends GutTest
## Art pass W8c (ART_BIBLE §11 Route / Loot / Modem / Events / Raid interlude / Run failed,
## §6.4–§6.8, §8 T4, §12): the netrun's pages. The route leads with the map and a compact
## list; the loot modal is 70% of the screen with a graffiti title that fits; the Modem's
## sign is baked art, its chips at `body`, slot tiles for the sockets, one Cycles readout;
## the event's story on paper with the speaker once and no subtitle repeat; the raid
## interlude with tile pickers; FLATLINED staged over a grey city with a hero stamp and a
## receipt; tips that follow the device; every page fitting at text scale 2.0.

const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "gut_art_w8c"
const CANVAS := Vector2(1280, 720)

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _reduce_motion_before: bool = false
var _hc_before: bool = false


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active
	_reduce_motion_before = Settings.reduce_motion
	_hc_before = Settings.high_contrast


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	if Settings.reduce_motion != _reduce_motion_before:
		Settings.set_reduce_motion(_reduce_motion_before)
	if Settings.high_contrast != _hc_before:
		Settings.set_high_contrast(_hc_before)
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


func _open() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var scene: Control = load(NETRUN).instantiate()
	holder.add_child(scene)
	return scene


func _netrun() -> Control:
	var scene := _open()
	scene.start_run(1)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _shop(scene: Control, cycles: int = 120) -> void:
	var s := RunManager.netrun
	s.run.cycles = cycles
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


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


## Every visible text control under `root`.
func _texts(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if (n is Label or n is Button or n is RichTextLabel) and (n as Control).is_visible_in_tree():
			out.append(n as Control)
	return out


# --- 1. Route -------------------------------------------------------------------------------------

func test_route_list_is_compact_icons_and_short_words() -> void:
	var scene := _netrun()
	await _frames(6)
	var s := RunManager.netrun
	var open := s.available_nodes()
	assert_true(open.size() > 0)
	for i in open.size():
		var b := scene._panel.find_child("Node%d" % (i + 1), true, false) as Button
		var node := s.run.map.get_node(open[i])
		assert_eq(String(b.get_meta(&"route_base")), scene.node_word(node), "choice %d's button says only what the node is" % (i + 1))
		assert_false(b.text.contains(">"), "no '>' in the button: %s" % b.text)
		assert_false(b.text.contains("("), "no '(same as' in the button: %s" % b.text)
		var row := scene._panel.find_child("Ahead%d" % (i + 1), true, false) as Control
		for k in scene.next_kinds(s.run.map, node):
			var pair := row.find_child("Next_%s" % k, true, false)
			assert_not_null(pair, "choice %d: where it leads, as an icon and its word" % (i + 1))
			assert_not_null(pair.get_node_or_null(^"Icon"))
			assert_ne((pair.get_node(^"Word") as Label).text, "")
		for n in _all(row):
			if n is Label:
				assert_false((n as Label).text.contains("then:"), "no bare 'then:' word")
	assert_eq((scene._panel.find_child("GridZoom", true, false) as Button).theme_type_variation, UiTheme.TERTIARY, "the view switch recedes")
	assert_eq((scene._panel.find_child("SaveQuit", true, false) as Button).theme_type_variation, UiTheme.TERTIARY, "Save & quit recedes")
	await _close(scene)


func test_route_dims_the_city_as_a_map_and_other_pages_do_not() -> void:
	var scene := _netrun()
	await _frames(4)
	var atmo: CityAtmosphere = scene.background.city.atmosphere()
	assert_true(atmo.state.map_mode, "the route is a map over the city (§9.5)")
	_shop(scene)
	await _frames(2)
	assert_false(atmo.state.map_mode, "the Modem is not a map")
	await _close(scene)


func test_route_cuts_to_its_framing_under_reduce_motion() -> void:
	Settings.set_reduce_motion(true)
	var scene := _netrun()
	await _frames(6)
	assert_false(scene.background.camera_easing(), "no held frame or camera ease under reduce motion")
	await _close(scene)


# --- 2. Loot --------------------------------------------------------------------------------------

func test_loot_modal_is_seventy_percent_wide_with_cards_at_hover_size() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(1)
		var scene := _netrun()
		_loot(scene)
		await _frames(4)
		var win := scene._panel.find_child("LootWindow", true, false) as Control
		assert_almost_eq(win.size.x, CANVAS.x * scene.LOOT_MODAL_SHARE, 2.0, "the loot modal is 70%% of the screen at %.1f" % scale)
		var tag := scene._panel.find_child("LootTag", true, false) as GraffitiTag
		assert_true(win.get_global_rect().encloses(tag.get_global_rect()), "the LOOT graffiti fits inside the modal at %.1f" % scale)
		var slack: float = tag.words_width() * scene.LOOT_TAG_SLACK + GraffitiTag.LEFT + GraffitiTag.MASCOT_ROOM
		assert_true(slack <= win.size.x, "the graffiti keeps 140%% width slack at %.1f (%.0f > %.0f)" % [scale, slack, win.size.x])
		var stickers: Node = scene._panel.find_child("Stickers", true, false)
		for c in stickers.get_children():
			var card := c as ZineCard
			assert_true(card.size.x >= scene.LOOT_CARD.x * ZineCard.HOVER_SCALE - 0.5, "offers at hover size or more (%.0f)" % card.size.x)
			assert_true(win.get_global_rect().grow(1.0).encloses(card.get_global_rect()), "an offer inside the modal at %.1f" % scale)
			assert_false(card.get_global_rect().intersects(tag.get_global_rect()), "the LOOT drips keep off the cards at %.1f" % scale)
			# Tooltips never fold one word per line (§6.8: 26-36 columns).
			var lines := card.tooltip_text.split("\n")
			var widest := 0
			for l in lines:
				widest = maxi(widest, l.length())
			assert_true(widest <= UiTip.COLUMNS, "the tip keeps within 36 columns")
			assert_true(lines.size() <= 2 or widest >= UiTip.MIN_COLUMNS - 10, "the tip is not a one-word column")
		await _close(scene)


func test_firmware_loot_picks_its_slot_on_tiles_not_a_dropdown() -> void:
	var scene := _netrun()
	_loot(scene, "firmware", [String(RunManager.lookup().ids_of_class(&"FirmwareData")[0])])
	await _frames(3)
	var pick: Node = scene._panel.find_child("SlotPick", true, false)
	assert_true(pick is SlotPicker, "the slot is picked on tiles")
	assert_eq((pick as SlotPicker).tiles.size(), RunManager.netrun.run.operative.slot_slice_ids.size(), "one tile per slot")
	for n in _all(scene._panel):
		assert_false(n is OptionButton, "no native dropdown on the loot page")
	await _close(scene)


func test_the_picked_loot_is_stamped_before_it_flies() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd")
	assert_true(src.contains("&\"loot_pick\", tr(LOOT_PICK_STAMP)"), "the pick flies with its TAKEN stamp (T2)")
	assert_true(ZineStamp.word_count(tr("TAKEN")) <= ZineStamp.MAX_WORDS)



# --- 3. Modem -------------------------------------------------------------------------------------

func test_modem_sign_is_baked_art_not_live_text() -> void:
	var scene := _netrun()
	_shop(scene)
	await _frames(3)
	var sign := scene._panel.find_child("ModemSign", true, false) as ModemSign
	assert_true(sign.is_baked(), "the sign is a texture")
	assert_true(ModemSign.ART is Texture2D)
	assert_eq(ModemSign.ART.resource_path, "res://assets/art/netrun/modem_sign.svg")
	assert_eq(sign.subtitle(), "", "no subtitle in English (the art says it)")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/modem_sign.gd")
	assert_false(src.contains("CyberType.draw_text"), "no drawn letters")
	assert_false(src.contains("_sticky("), "no decorative BUY / SHRED notes on the sign")
	# The warm-up flicker stays (T0), and holds lit under reduce effects / headless.
	sign.warm = 0.0
	var dark := 0
	for i in ModemSign.BANDS.size():
		if sign.band_light(i) < 1.0:
			dark += 1
	assert_true(dark > 0, "a tube is dark at the warm-up's start")
	sign.settle()
	assert_false(sign.warming())
	await _close(scene)


func test_modem_has_no_native_dropdown_and_slot_tiles_for_sockets() -> void:
	var seeds_with_firmware := 0
	for seed in range(1, 12):
		RunManager.reset()
		RunManager.new_campaign(seed)
		var scene := _netrun()
		_shop(scene)
		await _frames(2)
		for n in _all(scene._panel):
			assert_false(n is OptionButton or n is SpinBox, "no native control on the Modem (%s)" % n.name)
		var pick: Node = scene._panel.find_child("SocketPick", true, false)
		if not RunManager.netrun.run.shop.get("firmware", []).is_empty():
			seeds_with_firmware += 1
			assert_true(pick is SlotPicker, "the socket is picked on slot tiles")
			assert_true(pick.is_visible_in_tree())
		await _close(scene)
		if seeds_with_firmware > 0:
			break
	assert_true(seeds_with_firmware > 0, "a seed stocks Firmware")


func test_microchip_text_is_body_at_every_text_size() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(7)
		var scene := _netrun()
		_shop(scene)
		await _frames(3)
		var chips := 0
		for n in _all(scene._panel):
			var t := n as ZineCard
			if t == null or t.look != ZineCard.Look.CHIP or t.sold_stub:
				continue
			chips += 1
			var parts := t.tile_parts()
			assert_true(int(parts["dfs"]) >= UiTheme.font_px(UiTheme.BODY), "%s: effect text %d px >= body %d at %.1f" % [t.card_title, parts["dfs"], UiTheme.font_px(UiTheme.BODY), scale])
			assert_true(int(parts["fs"]) >= UiTheme.font_px(UiTheme.BODY), "%s: name at body at %.1f" % [t.card_title, scale])
			assert_true(int(parts["rows"]) >= (parts["desc_lines"] as PackedStringArray).size(), "%s: every line of its effect shows at %.1f" % [t.card_title, scale])
		assert_true(chips > 0, "chips or Daemons in stock at %.1f" % scale)
		await _close(scene)


func test_one_cycles_readout_the_top_bar() -> void:
	var scene := _netrun()
	_shop(scene)
	await _frames(3)
	assert_null(scene._panel.find_child("Wallet", true, false), "no wallet in the REMOVE window")
	for n in _all(scene._panel):
		if n is HudStats:
			for i in (n as HudStats).items.size():
				assert_ne((n as HudStats).icon_of(i), StatIcon.CYCLES, "no second CYCLES readout on the page")
	assert_ne(scene.hud.stats.icon_point(StatIcon.CYCLES), Vector2.INF, "the top bar says the Cycles")
	await _close(scene)


func test_out_of_reach_items_are_locked_with_need_and_have() -> void:
	var scene := _netrun()
	_shop(scene, 5)
	await _frames(3)
	var locked := 0
	for n in _all(scene._panel):
		var t := n as ZineCard
		if t == null or t.sold_stub or t.buy_button == null or not t.disabled:
			continue
		locked += 1
		var b := t.buy_button
		if b.short_of_money():
			assert_eq(b.label_text(), tr("NEED %d · HAVE %d") % [t.price, 5], "%s says why" % t.card_title)
	assert_true(locked > 0, "items out of reach")
	var src := FileAccess.get_file_as_string("res://scripts/ui/kit/buy_button.gd")
	assert_false(src.contains("NOTE_PINK"), "never a paler pink")
	assert_true(src.contains("draw_lock_badge"), "W2's lock badge")
	await _close(scene)


func test_the_pad_glyph_is_its_own_element_not_in_the_price() -> void:
	var scene := _netrun()
	_shop(scene, 999)
	await _frames(3)
	var card := scene._panel.find_child("Stickers", true, false).get_child(0) as ZineCard
	Settings.set_pad_active(true)
	card.grab_focus()
	await _frames(2)
	var b := card.buy_button
	assert_false(b.label_text().contains(Settings.key_text(&"ui_accept") + " ") or b.label_text().ends_with(" " + Settings.key_text(&"ui_accept")), "no pad letter in '%s'" % b.label_text())
	assert_true(b.glyph.visible, "the pad glyph shows beside the sticker")
	assert_false(Rect2(Vector2.ZERO, b.size).intersects(Rect2(b.glyph.position, b.glyph.size)), "beside, not on, the price")
	card.release_focus()
	await _frames(1)
	assert_false(b.glyph.visible, "gone when the item loses focus")
	await _close(scene)


func test_shred_keeps_a_ghost_gap_until_the_drop() -> void:
	var scene := _netrun()
	_shop(scene, 999)
	await _frames(3)
	scene.open_remove()
	await _frames(3)
	var view := scene.get_node("DeckView") as DeckView
	var before: Array[Rect2] = []
	for i in 4:
		before.append(view.card(i).get_global_rect())
	scene.modal_drops.start_carry(view.card(0), false)
	await _frames(2)
	for i in 4:
		assert_eq(view.card(i).get_global_rect(), before[i], "card %d stays put while one is carried (no reflow)" % i)
	assert_true(view.card(0).modulate.a < 1.0 and view.card(0).visible, "the carried card leaves a ghost in its place")
	scene.modal_drops.cancel()
	scene.modal_drops.finish_all()
	await _close(scene)


# --- 4. Events ------------------------------------------------------------------------------------

func test_event_story_on_paper_sized_to_its_words_in_plex() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(1)
		var scene := _netrun()
		_event(scene)
		await _frames(5)
		Typing.finish_all(get_tree())
		await _frames(3)
		var paper := scene._panel.find_child("EventPanel", true, false) as ZinePanel
		assert_not_null(paper, "a street event is paper")
		var text := paper.find_child("EventText", true, false) as RichTextLabel
		assert_eq(text.theme_type_variation, UiTheme.BODY_TEXT, "the story is Plex body text")
		var body_w := Palette.body().get_string_size("n".repeat(scene.EVENT_BODY_COLUMNS), HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.font_px(UiTheme.BODY)).x
		assert_true(text.size.x <= body_w + 1.0, "≤ 70 characters a line at %.1f (%.0f > %.0f)" % [scale, text.size.x, body_w])
		assert_true(paper.size.y >= paper.content.get_combined_minimum_size().y - 1.0, "the paper holds its words at %.1f" % scale)
		assert_true(paper.size.y <= paper.content.get_combined_minimum_size().y + 2.0, "and is no taller at %.1f" % scale)
		assert_true(paper.get_global_rect().end.x <= CANVAS.x, "on screen at %.1f" % scale)
		await _close(scene)


func test_event_speaker_once_and_no_subtitle_repeat() -> void:
	for id in [&"ev_leash_on_the_floor", &"ev_dispatch_early_reply"]:
		RunManager.reset()
		RunManager.new_campaign(1)
		Dialogue.clear()
		var scene := _netrun()
		_event(scene, id)
		await _frames(4)
		var ev := RunManager.netrun.current_event()
		var who: String = Dialogue.speaker_name(ev.speaker, RunManager.campaign.corporation_id)
		var seen := 0
		for c in _texts(scene._panel):
			var t := String(c.get("text"))
			if t.to_lower().begins_with(who.to_lower()):  # a plate or a "WHO:" prefix
				seen += 1
		var paper: Node = scene._panel.find_child("EventPanel", true, false)
		if paper is ZinePanel and (paper as ZinePanel).title.to_lower().contains(who.to_lower()):
			seen += 1
		assert_eq(seen, 1, "%s: the speaker is named once on the page" % id)
		var story := TextDb.t(ev, "text")
		assert_false(Dialogue.is_showing() and story.begins_with(Dialogue.current_text().trim_suffix("…").strip_edges().left(20)), "%s: the subtitle band doesn't repeat the story" % id)
		await _close(scene)
	assert_eq(load("res://scripts/ui/netrun_scene.gd").event_title("DISPATCH: Early Reply", "DISPATCH"), "Early Reply")


func test_event_choices_show_numbers_once_with_good_and_bad_glyphs() -> void:
	var scene := _netrun()
	_event(scene)
	await _frames(4)
	var ev := RunManager.netrun.current_event()
	for i in ev.choices.size():
		var b := scene._panel.find_child("Choice%d" % (i + 1), true, false) as Button
		var row := b.get_node(^"OutcomeRow") as OutcomeRow
		assert_true(row is EventOutcomeRow, "choice %d's outcome carries ▲ / ▼" % (i + 1))
		for it in row.items:
			if int(it.get("amount", 0)) != 0:
				assert_false(b.text.contains(String(it["text"])), "choice %d: the number %s shows once (in its chip)" % [i + 1, it["text"]])
	var good := EventOutcomeRow.new([{"kind": StatIcon.CYCLES, "amount": 5, "text": "+5", "good": true, "name": ""}])
	var bad := EventOutcomeRow.new([{"kind": StatIcon.HEAT, "amount": 2, "text": "+2", "good": false, "name": ""}])
	assert_true(EventOutcomeRow.is_good(good.items[0]) and not EventOutcomeRow.is_good(bad.items[0]), "the shape follows good and bad")
	good.free()
	bad.free()
	await _close(scene)


func test_a_chosen_event_leaves_no_bar_over_the_next_page() -> void:
	var scene := _netrun()
	_event(scene)
	await _frames(4)
	Typing.finish_all(get_tree())
	await _frames(2)
	Motion.force_live = true
	scene.choose_event(0)
	var layer := FlightFx.existing(scene)
	if layer != null:
		for f in layer.flights:
			for n in _all(f["node"]):
				assert_false(n is TextureRect, "the stamp carries no picture of the note")
		layer.finish()
	Motion.force_live = false
	await _frames(2)
	assert_eq(FlightFx.active_count(scene), 0, "nothing left over the next page")
	await _close(scene)


func test_event_paper_is_a_calm_zone_and_not_a_map() -> void:
	var scene := _netrun()
	_event(scene)
	await _frames(3)
	var atmo: CityAtmosphere = scene.background.city.atmosphere()
	assert_false(atmo.state.map_mode, "the event is not a map")
	assert_true(atmo._calm_controls.has(scene._panel.find_child("EventPanel", true, false)), "the story's paper is a calm zone")
	await _close(scene)


# --- 5. Raid interlude ----------------------------------------------------------------------------

func _raid(scene: Control) -> void:
	HeatRules.add_heat(RunManager.campaign, RunManager.config().major_heat_levels()[0] + 1, RunManager.config(), "test")
	RunManager.netrun._maybe_raid_interlude()
	scene._show_current()


func test_raid_interlude_has_tile_pickers_no_empty_labels_and_a_primary() -> void:
	var scene := _netrun()
	await _frames(2)
	_raid(scene)
	await _frames(4)
	assert_eq(RunManager.netrun.run.phase, RunState.Phase.RAID, "the interlude is up")
	for n in _all(scene._panel):
		assert_false(n is OptionButton or n is SpinBox, "no native control on the interlude (%s)" % n.name)
		if n is Label and (n as Label).is_visible_in_tree():
			assert_false((n as Label).text in [tr("RUN ASSETS:"), tr("ARMORY:")] and (n.get_parent().get_child_count() <= 1), "no empty '%s' label" % (n as Label).text)
	var start: Node = scene._panel.find_child("StartDefense", true, false)
	assert_eq((start as Button).theme_type_variation, UiTheme.PRIMARY, "START DEFENSE is the primary")
	var s := RunManager.netrun
	if s.run_assets().is_empty() and RunManager.campaign.armory.is_empty():
		assert_not_null(scene._panel.find_child("NoAssets", true, false), "a designed empty state")
	else:
		assert_true(scene._panel.find_child("DeployPick", true, false) is TilePicker, "the asset is picked on tiles")
	assert_true(scene.background.city.atmosphere().state.map_mode, "the raid's map dims the city (§9.5)")
	await _close(scene)


func test_raid_interlude_deploys_the_picked_asset_like_the_old_lists() -> void:
	var scene := _netrun()
	await _frames(2)
	RunManager.campaign.armory.append(RunManager.lookup().ids_of_class(&"DefenseAssetData")[0])
	_raid(scene)
	await _frames(4)
	var pick: Node = scene._panel.find_child("DeployPick", true, false)
	assert_true(pick is TilePicker)
	var home := RunManager.campaign.grid.home_site_id
	var before := RunManager.campaign.grid.assets_on(home).size()
	(pick as TilePicker).choose((pick as TilePicker).tiles.size() - 1)
	var deploy: Node = scene._panel.find_child("Deploy_%s" % home, true, false)
	assert_not_null(deploy, "the home row deploys")
	(deploy as Button).pressed.emit()
	await _frames(2)
	assert_eq(RunManager.campaign.grid.assets_on(home).size(), before + 1, "the picked Armory asset is on the node")
	await _close(scene)


func test_raid_cameras_cut_under_reduce_motion() -> void:
	Settings.set_reduce_motion(true)
	var scene := _netrun()
	await _frames(2)
	_raid(scene)
	await _frames(6)
	assert_false(scene.background.camera_easing(), "the interlude's map frames without a camera move")
	var src := FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd")
	assert_true(src.contains("if not Motion.camera_moves_allowed():\n\t\tbackground.settle_camera()\n\t\treturn 0.0"), "the playout's fight frame cuts in")
	await _close(scene)


func test_no_native_controls_are_built_on_netrun_pages() -> void:
	var src := FileAccess.get_file_as_string("res://scripts/ui/netrun_scene.gd")
	assert_false(src.contains("OptionButton.new()"), "netrun_scene builds no OptionButton")
	assert_false(src.contains("SpinBox.new()"), "netrun_scene builds no SpinBox")
	var scene := _open()
	await _frames(2)
	scene._show_start()
	await _frames(2)
	assert_not_null(scene._panel.find_child("SeedField", true, false) as CodeField, "the seed is a code field")
	assert_eq(scene.seed_digits("12a3"), "123")
	await _close(scene)


# --- 6. FLATLINED run end -------------------------------------------------------------------------

func _end(scene: Control, outcome: int) -> void:
	RunManager.netrun.run.outcome = outcome
	RunManager.netrun.run.phase = RunState.Phase.ENDED
	scene._show_current()


func test_flatlined_is_a_hero_stamp_over_a_grey_city_with_a_flatlined_portrait() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames(2)
		_end(scene, RunState.Outcome.DIED)
		await _frames(4)
		var stage := scene._panel as RunEndStage
		assert_not_null(stage, "the run's end is staged")
		stage.finish_now()
		await _frames(2)
		var stamp := stage.stamp
		assert_eq(stamp.shown_word(), tr("FLATLINED"))
		assert_eq(stamp.font_px, VerdictStamp.hero_px(), "the stamp at hero size at %.1f" % scale)
		assert_true(stamp.font_px >= mini(UiTheme.font_px(UiTheme.HERO), UiTheme.HERO_MAX), "hero step")
		assert_eq(stage.polaroid.expression, PortraitArt.Expr.FLATLINED, "the portrait flatlines")
		assert_almost_eq(stage.grade_amount(), RunEndStage.GREY_AMOUNT, 0.01, "the city is graded grey")
		assert_true(scene.background.visible and scene.background.city.is_visible_in_tree(), "the city shows: never a black void")
		var screen := Rect2(Vector2.ZERO, CANVAS).grow(1.0)
		var page_scroll := scene._panel_host.get_parent() as ScrollContainer
		for c in [stamp, stage.receipt, stage.fate_label, stage.back_button]:
			var r := (c as Control).get_global_rect()
			assert_true(r.position.x >= -1.0 and r.end.x <= CANVAS.x + 1.0, "%s within the screen's width at %.1f: %s" % [(c as Control).name, scale, r])
		page_scroll.ensure_control_visible(stage.back_button)
		await _frames(2)
		assert_true(screen.encloses(stage.back_button.get_global_rect()), "Back to HQ reachable at %.1f" % scale)
		var fate := stage.fate_label
		assert_true(fate.get_line_count() <= fate.get_visible_line_count() or fate.get_visible_line_count() < 0, "the fate line is whole (never 'Recruit, regr')")
		await _close(scene)


func test_run_end_verdicts_share_the_template() -> void:
	for o in [RunState.Outcome.COMPLETED, RunState.Outcome.ABORTED, RunState.Outcome.DIED]:
		RunManager.reset()
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames(2)
		_end(scene, o)
		await _frames(3)
		var stage := scene._panel as RunEndStage
		stage.finish_now()
		assert_eq(stage.stamp.shown_word(), tr(RunEndStage.verdict_of(o)))
		if o == RunState.Outcome.COMPLETED:
			assert_eq(stage.grade_amount(), 0.0, "a clean exit keeps the city's colour")
			assert_eq(stage.polaroid.expression, PortraitArt.Expr.TRIUMPHANT)
		else:
			assert_true(stage.grade_amount() > 0.9, "a loss greys the city")
		await _close(scene)
	for w in ["FLATLINED", "JACKED OUT", "HOME FELL"]:
		assert_true(ZineStamp.word_count(w) <= ZineStamp.MAX_WORDS, "a stamp says one thing (§6.6)")


func test_flatlined_is_a_skippable_t4_and_ends_at_once_under_reduce_effects() -> void:
	var e := Motion.entry(RunEndStage.MOTION)
	assert_eq(e.tier, 4, "a T4 moment")
	assert_lte(e.duration, 2.5, "within T4's 2.5 s")
	var scene := _netrun()
	await _frames(2)
	Motion.force_live = true
	_end(scene, RunState.Outcome.DIED)
	var stage := scene._panel as RunEndStage
	stage.play()
	assert_true(stage.running(), "the sequence plays")
	var ev := InputEventKey.new()
	ev.keycode = KEY_SPACE
	ev.pressed = true
	stage._input(ev)
	assert_false(stage.running(), "a press skips it")
	assert_eq(stage.polaroid.expression, PortraitArt.Expr.FLATLINED, "to its end state")
	stage.play()
	PageTransition.settle(stage)
	await _frames(2)
	assert_false(stage.running(), "a page settle ends it too")
	Motion.force_live = false
	Settings.set_reduce_effects(true)
	stage.play()
	assert_false(stage.running(), "reduce effects: the end state at once (the page cross-fades in)")
	assert_eq(stage.stamp.modulate.a, 1.0)
	Settings.set_reduce_effects(false)
	await _close(scene)


# --- 7. Words and input ---------------------------------------------------------------------------

func _tips(root: Node) -> PackedStringArray:
	var out := PackedStringArray()
	for n in _all(root):
		if n is Control and (n as Control).tooltip_text != "":
			out.append((n as Control).tooltip_text)
	return out


func test_tips_never_say_click_or_drag_to_a_pad_player() -> void:
	var scene := _netrun()
	_shop(scene, 999)
	await _frames(3)
	var mouse_said := false
	for t in _tips(scene._panel):
		mouse_said = mouse_said or UiTip.has_mouse_words(t)
	assert_true(mouse_said, "a mouse player reads the drag line")
	Settings.set_pad_active(true)
	await _frames(2)
	for t in _tips(scene._panel):
		assert_false(UiTip.has_mouse_words(t), "no mouse words for a pad: '%s'" % t.replace("\n", " "))
	_loot(scene)
	await _frames(3)
	for t in _tips(scene._panel):
		assert_false(UiTip.has_mouse_words(t), "loot, pad: '%s'" % t.replace("\n", " "))
	for k in scene.DRAG_TIPS_PAD:
		assert_false(UiTip.has_mouse_words(String(scene.DRAG_TIPS_PAD[k])), "the pad words for %s" % k)
	await _close(scene)


func test_the_daemon_tray_card_never_repeats_its_title() -> void:
	var scene := _netrun()
	await _frames(2)
	var op := RunManager.netrun.run.operative
	op.daemon_ids.append(&"twin_pointer")
	scene._refresh_status()
	scene.open_daemons()
	await _frames(2)
	var tray := scene.get_node("DaemonTray") as DaemonTray
	tray.show_card(&"twin_pointer", true)
	await _frames(1)
	var d := RunManager.lookup().get_content(&"twin_pointer") as DaemonData
	var text := (tray.find_child("DaemonText", true, false) as Label).text
	assert_false(text.to_lower().contains(TextDb.t(d, "display_name").to_lower()), "the card's words don't repeat the title: '%s'" % text)
	tray.close()
	await _close(scene)


func test_no_status_glyph_fonts_in_w8c_files() -> void:
	for p in ["res://scripts/ui/netrun_scene.gd", "res://scripts/ui/kit/buy_button.gd", "res://scripts/ui/kit/modem_sign.gd",
			"res://scripts/ui/kit/daemon_row.gd", "res://scripts/ui/kit/daemon_tray.gd", "res://scripts/ui/kit/event_held_mark.gd",
			"res://scripts/ui/kit/flight_fx.gd"]:
		assert_false(FileAccess.get_file_as_string(p).contains("STATUS_GLYPHS"), "%s draws status icons with StatIcon" % p)


# --- 8. Every page fits at text scale 2.0 ---------------------------------------------------------

## Opens `page` on a fresh run at the current text size.
func _page(page: String) -> Control:
	RunManager.reset()
	RunManager.new_campaign(1)
	var scene := _netrun()
	await _frames(2)
	match page:
		"loot":
			_loot(scene)
		"loot_firmware":
			_loot(scene, "firmware", RunManager.lookup().ids_of_class(&"FirmwareData").slice(0, 3).map(func(x: Variant) -> String: return String(x)))
		"modem":
			_shop(scene)
		"event":
			_event(scene)
		"dispatch":
			_event(scene, &"ev_dispatch_early_reply")
		"raid":
			_raid(scene)
		"run_end":
			_end(scene, RunState.Outcome.DIED)
	await _frames(5)
	Typing.finish_all(get_tree())
	if scene._panel is RunEndStage:
		(scene._panel as RunEndStage).finish_now()
	await _frames(3)
	return scene


func test_every_page_fits_at_every_text_scale() -> void:
	for scale in [1.0, 1.6, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		for page in ["route", "loot", "loot_firmware", "modem", "event", "dispatch", "raid", "run_end"]:
			var scene: Control = await _page(page)
			var tag := "%s at %.1f" % [page, scale]
			assert_true(scene._panel.get_combined_minimum_size().x <= CANVAS.x + 0.5, "%s: the page fits the screen's width (%.0f)" % [tag, scene._panel.get_combined_minimum_size().x])
			var texts := _texts(scene._panel)
			for c in texts:
				var r := c.get_global_rect()
				assert_true(r.position.x >= -0.5 and r.end.x <= CANVAS.x + 0.5, "%s: '%s' within the width %s" % [tag, String(c.get("text")).left(24), r])
				if c is Label:
					var fs := (c as Label).get_theme_font_size(&"font_size")
					assert_true(fs >= UiTheme.font_px(UiTheme.CAPTION), "%s: '%s' at %d px >= caption" % [tag, (c as Label).text.left(24), fs])
					var l := c as Label
					if l.autowrap_mode != TextServer.AUTOWRAP_OFF and l.text != "":
						assert_true(l.get_line_count() <= maxi(1, l.get_visible_line_count()) or l.max_lines_visible < 0, "%s: '%s' shows every line" % [tag, l.text.left(24)])
			# No two text controls overlap (a control inside another is its part).
			for i in texts.size():
				for j in range(i + 1, texts.size()):
					var a := texts[i]
					var b := texts[j]
					if a.is_ancestor_of(b) or b.is_ancestor_of(a) or a.get_parent() is Button or b.get_parent() is Button:
						continue
					var ov := a.get_global_rect().intersection(b.get_global_rect())
					assert_false(ov.size.x > 3.0 and ov.size.y > 3.0, "%s: '%s' overlaps '%s'" % [tag, String(a.get("text")).left(20), String(b.get("text")).left(20)])
			await _close(scene)
