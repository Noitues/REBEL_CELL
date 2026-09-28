extends GutTest
## H23 screens (DECISIONS "H23 screens"): the SAVED stamp covers no control; a subtitle
## names its speaker once and says when it goes on; one raid legend listing what its map
## shows, clear of the tags, and the nodes framed inside the map; every raid number
## explained; the HQ poster's band word and the whole Pirate Radio note; the route's own
## key; shop items with a price, words and a buy button; zero outcomes without numbers; the
## event title clear of the subtitle band; pad prompts; the Scrub Heat price; voice lines and
## drawn words translated; event subtitles translated once; the forecast stamp laid out.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "gut_s23_screens"
const CANVAS := Vector2(1280, 720)
## Frames the raid map takes to frame its nodes (a few settled passes).
const RAID_SETTLE := 40
const CORPS: Array[StringName] = [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]

var _text_scale_before: float = 1.0
var _pad_before: bool = false
var _legend_before: bool = true
var _pseudo_before: bool = false
var _locale_before: String = "en"
var _translation: Translation = null


func before_all() -> void:
	_text_scale_before = Settings.text_scale
	_pad_before = Settings.pad_active
	_legend_before = Settings.map_legend


func before_each() -> void:
	AudioDirector.muted = true
	_pseudo_before = TranslationServer.pseudolocalization_enabled
	_locale_before = TranslationServer.get_locale()
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
	if _translation != null:
		TranslationServer.remove_translation(_translation)
		_translation = null
	TranslationServer.set_locale(_locale_before)
	if TranslationServer.pseudolocalization_enabled != _pseudo_before:
		TranslationServer.pseudolocalization_enabled = _pseudo_before
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	if Settings.map_legend != _legend_before:
		Settings.set_map_legend(_legend_before)
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


func _open(path: String) -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = CANVAS
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _close(scene: Control) -> void:
	scene.get_parent().queue_free()
	await _frames(2)


func _all(node: Node) -> Array[Node]:
	var out: Array[Node] = []
	for c in node.get_children():
		out.append(c)
		out.append_array(_all(c))
	return out


## `c`'s rect clipped to the scroll views above it.
func _shown_rect(c: Control) -> Rect2:
	var r := c.get_global_rect()
	var p := c.get_parent()
	while p != null:
		if p is ScrollContainer:
			r = r.intersection((p as Control).get_global_rect())
		p = p.get_parent()
	return r


## Every visible, usable control under `root`, and the map legends, as far as they show.
func _controls(root: Node) -> Array[Control]:
	var out: Array[Control] = []
	for n in _all(root):
		if not (n is Control) or not (n as Control).is_visible_in_tree():
			continue
		var usable := (n is BaseButton and not (n as BaseButton).disabled and (n as Control).mouse_filter != Control.MOUSE_FILTER_IGNORE) or n is LineEdit or (n is Range and not (n is ScrollBar))
		if usable or n is MapLegend or n is RouteLegend:
			if _shown_rect(n as Control).has_area():
				out.append(n)
	return out


func _translate(pairs: Dictionary) -> void:
	_translation = Translation.new()
	_translation.locale = "xx"
	for k in pairs:
		_translation.add_message(k, pairs[k])
	TranslationServer.add_translation(_translation)
	TranslationServer.set_locale("xx")


## Two claimed nodes beside the home server, an Armory and a pending raid (the campaign's
## own corporation).
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
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25, "corporation": String(c.corporation_id)})
	return c


func _raid(scale: float) -> Control:
	Settings.set_text_scale(scale)
	RunManager.new_campaign(1)
	_raid_campaign()
	var hq := _open(HQ)
	await _frames()
	hq.show_raid()
	await _frames(RAID_SETTLE)
	return hq


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


func _loot(scene: Control) -> void:
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	scene._show_current()


# --- S1 the SAVED stamp -----------------------------------------------------------------------

## The screens themselves (raid setup, route, Modem at 1.0 and 1.6) are checked where the
## stamp really lands after each autosave, keyboard and pad: test_horizontal_pass24_screens
## test_the_saved_stamp_is_placed_on_the_page_it_lands_on (Test suite optimization).
func test_a_control_in_the_corner_moves_the_saved_stamp() -> void:
	var spot := Fx.saved_spot(Vector2(50, 20), Rect2(Vector2.ZERO, CANVAS), [Rect2(1150, 660, 130, 60)] as Array[Rect2])
	assert_false(Rect2(spot, Vector2(50, 20)).intersects(Rect2(1150, 660, 130, 60)), "a control in the corner moves the stamp")


# --- S2 / S3 subtitles ------------------------------------------------------------------------

func test_a_line_that_names_its_speaker_is_not_named_twice() -> void:
	assert_eq(Array(Dialogue.own_speaker("SOLACE", "SOLACE COLLECTIONS: This is a notice.")), ["SOLACE COLLECTIONS", "This is a notice."])
	assert_eq(Array(Dialogue.own_speaker("SOLACE", "Billing Farm. Quiet in.")), ["SOLACE", "Billing Farm. Quiet in."], "no tag: the speaker's name")
	assert_eq(Array(Dialogue.own_speaker("DISPATCH", "Note: keep low.")), ["DISPATCH", "Note: keep low."], "a colon inside the words is not a tag")
	var hq := _open(HQ)
	await _frames()
	Dialogue.clear()
	var said := Dialogue.raid_warning(&"solace", &"raid_heat_25")
	assert_true(said.begins_with("SOLACE COLLECTIONS:"), "the line names its sender: %s" % said)
	await _frames(2)
	var shown := Dialogue.text_label.get_parsed_text()
	assert_false(shown.contains("SOLACE: SOLACE"), "the speaker once: '%s'" % shown)
	assert_true(shown.begins_with("SOLACE COLLECTIONS:"), "the line's own sender leads: '%s'" % shown)
	await _close(hq)


func test_a_long_subtitle_pages_and_says_it_goes_on() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var hq: Control = await _raid(scale)
		var band := (hq.subtitle_strip as Control).get_global_rect()
		Dialogue.clear()
		Dialogue.raid_warning(&"solace", &"raid_heat_25")
		var words := PackedStringArray()
		var pages := 0
		while Dialogue.is_showing() and pages < 20:
			await _frames(2)
			var tl := Dialogue.text_label
			var shown := tl.get_parsed_text()
			var last := Dialogue._queue.is_empty()
			if last:
				assert_false(shown.ends_with(Dialogue.CONTINUED_MARK), "the last page has no mark: '%s'" % shown)
			else:
				assert_true(shown.ends_with(Dialogue.CONTINUED_MARK), "a page that goes on ends in '…' (text %.1f): '%s'" % [scale, shown])
			assert_true(tl.get_content_height() <= tl.size.y + 1.0, "page %d fits (content %.1f in %.1f, text %.1f): '%s'" % [pages, tl.get_content_height(), tl.size.y, scale, shown])
			var bar := Rect2(Dialogue.bar.global_position, Dialogue.bar.size)
			assert_true(bar.end.y <= band.end.y + 0.5, "the bar stays in its band")
			words.append(Dialogue.current_text())
			pages += 1
			if last:
				break
			Dialogue._next()
		assert_true(pages >= 1)
		var whole := " ".join(words)
		assert_string_contains(whole, "Collectors have been dispatched.", "every page shown, the end included (text %.1f)" % scale)
		await _close(hq)


# --- S4 / S14 the raid map ----------------------------------------------------------------------

func test_one_raid_legend_listing_what_the_map_shows_clear_of_the_tags() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var hq: Control = await _raid(scale)
		var legends := 0
		for n in _all(hq):
			if n is MapLegend and (n as Control).is_visible_in_tree():
				legends += 1
		assert_eq(legends, 1, "one legend on the raid setup (text %.1f)" % scale)
		var legend: MapLegend = hq.raid_legend
		var keys := MapLegend.keys_of(hq.raid_graph(RunManager.project_raid(), {}), RunManager.campaign.grid)
		assert_eq(legend.only, keys, "the legend lists what the map shows")
		assert_false(keys.has(CityMapOverlay.KIND_BOSS) and not _graph_has_kind(hq, CityMapOverlay.KIND_BOSS), "no row for what is not there")
		var lr := legend.get_global_rect()
		for r in LegendSpot.node_rects(hq.city_overlay, true):
			assert_false(lr.intersects(r), "the legend %s covers a node, tag or label at %s (text %.1f)" % [lr, r, scale])
		await _close(hq)


func _graph_has_kind(hq: Control, kind: String) -> bool:
	for n in hq.raid_graph(RunManager.project_raid(), {})["nodes"]:
		if String(n.get("kind", "")) == kind:
			return true
	return false


func test_raid_nodes_sit_inside_the_map_for_every_corporation() -> void:
	for u in [&"unlock_halcyon", &"unlock_meridian", &"unlock_orbital"]:
		RunManager.profile.add_unlock(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		RunManager.profile.best_ice_by_corp[id] = 10
	for corp in CORPS:
		for scale in [1.0, Settings.TEXT_SCALE_MAX]:
			Settings.set_text_scale(scale)
			RunManager.new_campaign(1, corp)
			assert_eq(RunManager.campaign.corporation_id, corp, "%s opens" % corp)
			_raid_campaign()
			var hq := _open(HQ)
			await _frames()
			hq.show_raid()
			await _frames(RAID_SETTLE)
			var area_ctl := hq._panel.find_child("RaidMapArea", true, false) as Control
			var area := area_ctl.get_global_rect().intersection(Rect2(Vector2.ZERO, CANVAS)).grow(1.0)
			var rects := LegendSpot.node_rects(hq.city_overlay, false)
			assert_false(rects.is_empty(), "%s: the raid map has nodes" % corp)
			for r in rects:
				assert_true(area.encloses(r), "%s at %.1f: node %s inside the map area %s" % [corp, scale, r, area])
			await _close(hq)


# --- S5 raid words ---------------------------------------------------------------------------------

func test_every_raid_number_says_what_it_is() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		var hq: Control = await _raid(scale)
		var intro := hq._panel.find_child("RaidIntro", true, false) as Label
		assert_not_null(intro, "one plain sentence opens the setup")
		assert_eq(intro.text, TextDb.ui_text("ui.raid_intro"))
		assert_string_contains(intro.text, "START DEFENSE")  # H24 S14: the button was renamed
		var letters := RegEx.create_from_string("[A-Za-z]{2,}")
		var digits := RegEx.create_from_string("[0-9]")
		for n in _all(hq._panel):
			if n is Badge:
				var b := n as Badge
				assert_ne(b.tooltip_text, "", "badge '%s' has a tooltip" % b.text)
				if digits.search(b.text) != null:
					assert_not_null(letters.search(b.text), "badge '%s' names what its number is" % b.text)
			if n is AssetCard:
				var card := n as AssetCard
				assert_string_contains(card.integrity_text(), "HP")
				assert_string_contains(card.count_text(), "LEFT")
				assert_string_contains(card.tooltip_text, "HP %d" % card.integrity)
				assert_string_contains(card.tooltip_text, "%d LEFT" % card.count)
		for n in hq.city_overlay.nodes:
			if n.has("result"):
				var tip: String = hq.city_overlay.tip_of(n["id"])
				assert_string_contains(tip, "integrity (HP)", "the map tag's numbers explained")
				assert_true(tip.contains("HOLDS:") or tip.contains(": the node falls"), "and its word: %s" % tip)
		await _close(hq)


# --- S6 / S13 HQ ------------------------------------------------------------------------------------

func test_the_poster_word_shows_and_the_radio_note_is_whole() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var hq := _open(HQ)
		await _frames(6)
		var poster: HeatPoster = null
		for n in _all(hq._panel):
			if n is HeatPoster:
				poster = n
		assert_not_null(poster)
		var word := poster.band_label_rect()
		word.position += poster.global_position
		var pr := poster.get_global_rect()
		assert_true(pr.encloses(word), "the band word %s inside the poster %s (text %.1f)" % [word, pr, scale])
		var radio := hq._panel.find_child("PirateRadio", true, false) as ZineNote
		assert_false(radio.get_global_rect().intersects(word), "the radio note leaves the word alone")
		assert_true(radio.label.get_content_height() <= radio.label.size.y + 1.0, "the radio's words are whole (%.1f in %.1f, text %.1f)" % [radio.label.get_content_height(), radio.label.size.y, scale])
		assert_true(radio.get_global_rect().encloses(radio.label.get_global_rect()), "the words stay on the note")
		await _close(hq)


func test_scrub_heat_says_its_price_is_schematics() -> void:
	var hq := _open(HQ)
	await _frames(4)
	var b := hq._panel.find_child("ScrubHeat", true, false) as Button
	assert_not_null(b)
	var price := CampaignRules.heat_purchase_price(RunManager.campaign, RunManager.config())
	assert_string_contains(b.text, "pay %d" % price)
	assert_eq(b.get_meta(&"price_kind", &""), StatIcon.SCHEMATICS, "the Schematics icon after the price")
	var mark := b.get_node_or_null(^"PriceIcon") as IconMark
	assert_not_null(mark)
	assert_true(Rect2(Vector2.ZERO, b.size).grow(1.0).encloses(Rect2(mark.position, mark.size)), "the icon sits on the button")
	assert_string_contains(b.tooltip_text, "%d Schematics" % price)
	await _close(hq)


# --- S7 the route key -------------------------------------------------------------------------------

func test_the_route_key_lists_the_routes_node_kinds_clear_of_the_nodes() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames(10)
		for n in _all(scene._panel):
			assert_false(n is MapLegend, "not the campaign map's key")
		var legend: RouteLegend = scene.route_legend
		assert_not_null(legend)
		var nodes: Array = scene.route_graph()["nodes"]
		var want := {}
		for n in nodes:
			want[String(n["kind"])] = true
		for k in want:
			assert_true(legend.kinds.has(k), "the key has %s" % k)
			assert_not_null(legend.body.find_child("Kind_%s" % k, true, false), "a row for %s" % k)
		for k in legend.kinds:
			assert_true(want.has(k), "the key lists only kinds on the route (%s)" % k)
		assert_true(legend.is_visible_in_tree())
		var lr := legend.get_global_rect()
		assert_true(Rect2(Vector2.ZERO, CANVAS).encloses(lr), "on screen: %s" % lr)
		for r in LegendSpot.node_rects(scene.city_overlay, false):
			assert_false(lr.intersects(r), "the key %s covers a node at %s (text %.1f)" % [lr, r, scale])
		for n in nodes:
			var tip: String = scene.city_overlay.tip_of(n["id"])
			assert_true(tip.begins_with(String(RouteLegend.MEANINGS[String(n["kind"])])), "the node says what it is and does: %s" % tip)
		await _close(scene)


# --- S8 the Modem -------------------------------------------------------------------------------------

func test_every_shop_item_has_a_price_words_and_a_buy_button() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		_shop(scene)
		await _frames()
		var items := 0
		for n in _all(scene._panel):
			if not (n is ZineCard):
				continue
			var card := n as ZineCard
			items += 1
			assert_true(card.price >= 0, "%s has a price" % card.card_title)
			assert_ne(card.price_words(), "", "%s: the price in words" % card.card_title)
			assert_false(card.price_words().ends_with("+"), "%s: a real price, not 'N+'" % card.card_title)
			assert_ne(card.tooltip_text, "", "%s: a tooltip" % card.card_title)
			assert_true(card.focus_mode == Control.FOCUS_ALL, "%s: a focus stop" % card.card_title)
			var buy := card.buy_button
			assert_not_null(buy, "%s: a buy button" % card.card_title)
			assert_true(buy is Button, "the buy control is a Button")
			assert_string_contains(buy.label_text(), card.price_words())
			assert_true(Rect2(Vector2.ZERO, card.size).grow(1.0).encloses(Rect2(buy.position, buy.size)), "%s: the button sits on its item" % card.card_title)
			assert_eq(buy.disabled, card.disabled, "the button is off when the item is")
			if card.look == ZineCard.Look.CHIP:
				assert_ne(card.tile_description(), "", "%s: the chip says what it does" % card.card_title)
				assert_true(card.chip_lines_shown() >= 1, "%s: its effect is on the tile (text %.1f)" % [card.card_title, scale])
		assert_true(items >= 5, "cards, chips, slices, daemons and the shredder")
		await _close(scene)


func test_the_buy_button_presses_its_item_and_shows_the_pad_button() -> void:
	var scene := _netrun()
	RunManager.netrun.run.cycles = 999
	RunManager.netrun._open_shop()
	scene._show_current()
	await _frames()
	var stickers: Node = scene._panel.find_child("Stickers", true, false)
	var card := stickers.get_child(0) as ZineCard
	var deck_before := RunManager.netrun.run.operative.deck.size()
	Settings.set_pad_active(true)
	card.grab_focus()
	await _frames()
	assert_string_contains(card.buy_button.label_text(), Settings.key_text(&"ui_accept"), "the pad button while focused")
	var tip := FocusTip.tip_of(card)
	assert_not_null(tip, "the whole text shows on focus")
	if tip != null:
		var words := ""
		for n in _all(tip):
			if n is Label:
				words += (n as Label).text + "\n"
		assert_string_contains(words.replace("\n", " "), TextDb.t(RunManager.lookup().get_content(StringName(String(RunManager.netrun.run.shop["cards"][0]))), "display_name"), "the tip carries the card")
	card.buy_button.pressed.emit()
	await _frames()
	assert_eq(RunManager.netrun.run.operative.deck.size(), deck_before + 1, "the buy button bought the card")
	await _close(scene)


# --- S9 outcomes -----------------------------------------------------------------------------------------

func test_a_change_that_is_none_shows_no_number() -> void:
	var scene := _netrun()
	await _frames()
	var s := RunManager.netrun
	var op := s.run.operative
	op.hp = op.max_hp
	var heal := EventChoiceData.new()
	var e := EffectData.new()
	e.type = RC.EffectType.HEAL
	e.amount = 5
	heal.effects = [e] as Array[EffectData]
	var items := OutcomeRow.of_choice(s, heal)
	assert_eq(OutcomeRow.shown(items).size(), 0, "no +0 HP")
	assert_eq(OutcomeRow.words(items), "", "no words for nothing")
	assert_string_contains(OutcomeRow.describe(items), "no change", "the tooltip still says why")
	s.campaign.heat = 0
	_event(scene)
	await _frames()
	var ev := s.current_event()
	for i in ev.choices.size():
		var b := scene._panel.find_child("Choice%d" % (i + 1), true, false) as Button
		assert_false(b.text.contains("+0") or b.text.contains("-0"), "choice %d shows no zero: '%s'" % [i, b.text])
		var row := b.find_child("OutcomeRow", false, false) as OutcomeRow
		if row != null:
			for it in row.items:
				# H24 S9: a choice that changes nothing shows the neutral "no change" mark.
				if StringName(it["kind"]) != OutcomeRow.NO_CHANGE:
					assert_ne(int(it["amount"]), 0, "choice %d's row has no zero" % i)
	await _close(scene)


# --- S10 the event title and the subtitle band --------------------------------------------------------------

func test_the_event_title_is_clear_of_the_subtitle_band_and_an_empty_band_hides() -> void:
	for scale in [1.0, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		RunManager.new_campaign(1)
		var scene := _netrun()
		await _frames()
		Dialogue.clear()
		_event(scene)
		await _frames(4)
		Dialogue.clear()
		assert_false(Dialogue.bar.visible, "no line: no bar (text %.1f)" % scale)
		var band := (scene.subtitle_strip as Control).get_global_rect()
		var panel: Node = scene._panel.find_child("EventPanel", true, false)
		if panel is ZinePanel:
			var zp := panel as ZinePanel
			var title := zp.title_rect()
			title.position += zp.global_position
			assert_true(title.position.y >= band.end.y, "the title %s under the band %s (text %.1f)" % [title, band, scale])
			assert_true(zp.global_position.y - ZinePanel.TAPE_OVERHANG >= band.end.y - 0.5, "the tape too")
			assert_eq(zp.title_size, roundi(ZinePanel.TITLE_SIZE * scale), "the title follows the text size")
			Dialogue.say(RC.Voice.DISPATCH, "A short line.")
			await _frames(2)
			var bar := Rect2(Dialogue.bar.global_position, Dialogue.bar.size)
			assert_true(Dialogue.bar.visible and Dialogue.text_label.size.y > 0.0, "a line shows in the bar")
			assert_false(bar.intersects(title), "the bar %s never covers the title %s" % [bar, title])
		Dialogue.clear()
		_shop(scene)
		await _frames()
		assert_false(Dialogue.bar.visible, "no empty strip on the Modem")
		await _close(scene)


# --- S11 pad prompts ---------------------------------------------------------------------------------------------

func _prompts(scene: Control) -> String:
	return " | ".join((scene.pad_prompts as PadPrompts).texts())


func test_pad_prompts_on_hq_raid_route_shop_and_loot() -> void:
	var a := ""
	var b := ""
	Settings.set_pad_active(true)
	a = Settings.key_text(&"ui_accept")
	b = Settings.key_text(&"ui_cancel")
	assert_eq(a, "A")
	assert_eq(b, "B")
	Settings.set_pad_active(false)
	var hq := _open(HQ)
	await _frames()
	assert_false((hq.pad_prompts as PadPrompts).visible, "no prompts without a pad")
	Settings.set_pad_active(true)
	await _frames()
	assert_true((hq.pad_prompts as PadPrompts).visible, "prompts follow the device")
	assert_string_contains(_prompts(hq), "A  Select")
	assert_string_contains(_prompts(hq), "Menu  Settings")
	_raid_campaign()
	hq.show_raid()
	await _frames()
	assert_string_contains(_prompts(hq), "B  Back")
	# B goes back to the HQ.
	var ev := InputEventJoypadButton.new()
	ev.button_index = JOY_BUTTON_B
	ev.pressed = true
	hq._unhandled_input(ev)
	await _frames()
	assert_eq(hq.panel_name, "hq", "B leaves the raid setup")
	await _close(hq)
	RunManager.new_campaign(1)  # no raid pending: the run starts
	var scene := _netrun()
	await _frames()
	assert_string_contains(_prompts(scene), "A  Go")
	_shop(scene)
	await _frames()
	assert_string_contains(_prompts(scene), "A  Buy")
	assert_string_contains(_prompts(scene), "B  Leave")
	scene._unhandled_input(ev)
	await _frames()
	assert_ne(RunManager.netrun.run.phase, RunState.Phase.SHOP, "B leaves the Modem")
	_loot(scene)
	await _frames()
	assert_string_contains(_prompts(scene), "A  Take")
	var row := (scene.pad_prompts as PadPrompts).get_global_rect()
	for c in _controls(scene._panel):
		assert_false(row.intersects(_shown_rect(c)), "the prompts cover no control")
	Settings.set_pad_active(false)
	await _frames()
	assert_false((scene.pad_prompts as PadPrompts).visible, "gone with the pad")
	await _close(scene)


# --- S15 / S16 / S17 translation ------------------------------------------------------------------------------

func test_voice_lines_have_keys_and_speak_translated() -> void:
	var rows := TextDb.collect(RunManager.lookup())
	var keys := {}
	for r in rows:
		keys[r[0]] = r[1]
	var set: LineSetData = null
	var index := -1
	for id in RunManager.lookup().ids_of_class(&"LineSetData"):
		var ls := RunManager.lookup().get_content(id) as LineSetData
		for i in ls.lines.size():
			if ls.lines[i].key == "raid:raid_heat_25" and ls.corporation_id == &"solace":
				set = ls
				index = i
	assert_not_null(set, "the Solace raid line's set")
	var key := TextDb.voice_key(set, index)
	assert_eq(key, "LineSetData.%s.lines.%d" % [set.id, index])
	assert_true(keys.has(key), "the export has the voice line")
	assert_eq(keys[key], set.lines[index].text)
	assert_true(keys.has("ui.raid_intro"), "and the screen sentences")
	var file := FileAccess.get_file_as_string("res://assets/text/strings.csv")
	assert_string_contains(file, key, "strings.csv carries the voice lines (tools/export_text.gd ran)")
	_translate({key: "SOLACE COLLECTIONS: Premier avis.", "CorporationData.solace.display_name": "Zolace Biosystemes"})
	assert_eq(Dialogue.speaker_name(RC.Voice.CORPO, &"solace"), "ZOLACE", "the corporate name is translated")
	Dialogue.clear()
	var said := Dialogue.raid_warning(&"solace", &"raid_heat_25")
	assert_eq(said, "SOLACE COLLECTIONS: Premier avis.", "the line in the player's language")
	await _frames(2)
	assert_string_contains(Dialogue.text_label.get_parsed_text(), "Premier avis.")


func test_drawn_words_are_translated() -> void:
	_translate({"HOME HIT": "XX_HOME_HIT", "IF THE RAID\nRUNS NOW:": "XX_IF", "HEAT": "XX_HEAT", "HP": "XX_HP", "LEFT": "XX_LEFT", "RESPIN": "XX_RESPIN"})
	var stamp: ForecastStamp = add_child_autofree(ForecastStamp.new("IF THE RAID\nRUNS NOW:", "HOME HIT"))
	stamp.size = Vector2(124, 124)
	assert_eq(stamp.shown_verdict(), "XX_HOME_HIT")
	assert_eq(stamp.shown_caption(), "XX_IF")
	var tags: HudStats = add_child_autofree(HudStats.new())
	tags.items = [["HEAT", "3", "/100", "Heat."]]
	assert_eq(tags.tag_name(0), "XX_HEAT")
	var card: AssetCard = add_child_autofree(AssetCard.new(&"turret", "Turret", 10, 1))
	assert_eq(card.integrity_text(), "XX_HP 10")
	assert_eq(card.count_text(), "1 XX_LEFT")
	var sticker: StickerButton = add_child_autofree(StickerButton.new("RESPIN"))
	assert_eq(sticker.shown_text(), "XX_RESPIN")
	sticker.refit()
	var w := Palette.marker().get_string_size("XX_RESPIN", HORIZONTAL_ALIGNMENT_LEFT, -1, StickerButton.font_px()).x
	assert_true(sticker.custom_minimum_size.x >= w, "measured as translated")


func test_event_subtitles_are_translated_once() -> void:
	var scene := _netrun()
	await _frames()
	TranslationServer.pseudolocalization_enabled = true
	await _frames()
	Dialogue.clear()
	scene._spoken_events.clear()
	_event(scene)
	await _frames(2)
	var ev := RunManager.netrun.current_event()
	var once := TextDb.t(ev, "text")
	var shown := Dialogue.current_text().strip_edges()
	assert_ne(shown, "", "the event speaks")
	assert_true(once.begins_with(shown), "the page is the text translated once: '%s' vs '%s'" % [shown, once])
	assert_eq(Dialogue.history[-1]["text"], once)
	TranslationServer.pseudolocalization_enabled = false
	await _close(scene)


# --- S18 the forecast stamp ----------------------------------------------------------------------------------------

func test_the_forecast_stamps_parts_never_overlap() -> void:
	for scale in [1.0, 1.3, Settings.TEXT_SCALE_MAX]:
		Settings.set_text_scale(scale)
		var stamp: ForecastStamp = add_child_autofree(ForecastStamp.new("IF THE RAID\nRUNS NOW:", "HOME HIT", Palette.CELL_PINK, StatIcon.HOME))
		stamp.size = Vector2(124, 124) * (1.0 + (scale - 1.0) * 0.3)
		var l := stamp.layout()
		var icon: Rect2 = l["icon"]
		var cap: Rect2 = l["caption"]
		var ver: Rect2 = l["verdict"]
		assert_true(icon.has_area(), "the icon shows")
		assert_false(icon.intersects(cap), "icon %s over caption %s at %.1f" % [icon, cap, scale])
		assert_false(cap.intersects(ver), "caption %s over verdict %s at %.1f" % [cap, ver, scale])
		var inside := Rect2(Vector2.ZERO, stamp.size)
		for r in [icon, cap, ver]:
			assert_true(inside.encloses(r), "%s inside the stamp %s at %.1f" % [r, inside, scale])
