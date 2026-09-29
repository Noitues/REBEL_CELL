extends GutTest
## Art pass W8b (ART_BIBLE §5, §6.9, §6.10, §11): the HQ, new campaign, City Grid, raid,
## map and top bar screens. Presentation only: these check the looks the bible asks for.

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SLOT := "gut_w8b_screens"
const CANVAS := Vector2(1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]

var _text_scale_before: float = 1.0
var _pad_before: bool = false


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
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	Settings.set_pad_active(_pad_before)
	Dialogue.clear()
	Dialogue.enter_screen("")
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


## A campaign with two claimed Sites (one with a turret), an Armory and a raid pending.
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


# --- Item 1: the top bar and the subtitle band (§5.2, §6.9) ------------------------------------

func test_the_top_bar_never_wraps_and_keeps_a_height_set_by_the_text_scale() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.reset()
		RunManager.new_campaign(1)
		_raid_campaign()
		var hq := _open(HQ)
		await _frames()
		var heights := []
		for screen in ["hq", "grid", "raid"]:
			match screen:
				"grid":
					hq.show_grid()
				"raid":
					hq.show_raid()
			await _frames()
			var st: HudStats = hq.hud.stats
			assert_eq(st.rows, 1, "%s at %.1f: one row" % [screen, scale])
			heights.append(st.get_combined_minimum_size().y)
			assert_almost_eq(st.get_combined_minimum_size().y, HudStats.row_height(scale), 0.5, "%s at %.1f: the height is the scale's" % [screen, scale])
			var rects := st.tag_rects()
			for i in rects.size():
				assert_true(rects[i].end.x <= st.size.x + 0.5, "%s at %.1f: tag %d stays in the row" % [screen, scale, i])
				assert_almost_eq(rects[i].position.y, rects[0].position.y, 0.01, "%s at %.1f: one line" % [screen, scale])
				assert_almost_eq(rects[i].size.x, rects[0].size.x, 0.01, "%s at %.1f: tags share the width evenly" % [screen, scale])
			assert_true(st.value_font_size() >= roundi(UiTheme.CAPTION * scale), "values never under caption")
			assert_true(st.label_font_size() >= roundi(UiTheme.CAPTION * scale), "labels never under caption")
			assert_eq(st.compact, scale >= HudStats.FOLD_SCALE, "labels fold only at big text (%.1f)" % scale)
			if st.compact:
				assert_ne(st._get_tooltip(rects[0].get_center()), "", "a folded tag keeps its words in the tooltip")
			assert_true(hq.hud.get_combined_minimum_size().x <= CANVAS.x + 0.5, "%s at %.1f: the bar fits the screen" % [screen, scale])
		assert_eq(heights[0], heights[1], "the bar keeps its height across pages")
		await _close(hq)


func test_a_long_value_steps_down_and_never_grows_its_tag() -> void:
	var st: HudStats = add_child_autofree(HudStats.new())
	st.size = Vector2(700, 60)
	st.items = [["HEAT", "12", "/100"], ["CYCLES", "3", ""]]
	await _frames(1)
	var before := st.tag_rects()
	var px := st.value_font_size()
	st.items = [["HEAT", "123456789", "/100"], ["CYCLES", "3", ""]]
	assert_eq(st.tag_rects(), before, "the tags keep their rects")
	assert_true(st.value_font_size() <= px, "the value steps down instead")


func test_a_drop_target_tag_shows_focus_brackets_while_carrying() -> void:
	var bar: HudBar = add_child_autofree(HudBar.new())
	bar.size = Vector2(1280, 60)
	bar.set_stats([["HEAT", "1", ""], ["CARDS", "10", ""]])
	await _frames(2)
	var layer: DropLayer = add_child_autofree(DropLayer.new())
	var st := bar.stats
	var card_rect := func() -> Rect2:
		var r: Rect2 = st.tag_rects()[1]
		return Rect2(st.get_global_transform() * r.position, r.size)
	layer.add_target("deck", ["card"], "deck", null, card_rect)
	bar.watch_drops(layer)
	var src: Button = add_child_autofree(Button.new())
	src.size = Vector2(40, 40)
	layer.add_source(src, {"kind": "card"})
	layer.start_carry(src, false)
	assert_true(st.hot_kinds.has(StatIcon.CARDS), "CARDS takes the carried card: brackets on it")
	assert_false(st.hot_kinds.has(StatIcon.HEAT), "HEAT is no target")
	layer.cancel()
	assert_true(st.hot_kinds.is_empty(), "the brackets go when the carry ends")


func test_the_subtitle_band_is_one_line_at_1_and_two_above() -> void:
	var strip := SubtitleStrip.new()
	assert_eq(strip.lines_at(1.0), 1)
	assert_eq(strip.lines_at(1.6), 2)
	assert_eq(strip.lines_at(2.0), 2)
	strip.free()


# --- Item 2: the HQ in its DECK frame (§2 DECK, §11 HQ) ------------------------------------------

func test_the_hq_sits_in_its_deck_frame_with_a_crt_monitor_and_a_three_column_crew() -> void:
	var c := _raid_campaign()
	c.recruit(RunManager.lookup().get_content(&"ghost") as ClassData)
	var hq := _open(HQ)
	await _frames(6)
	var frame: DeckFrame = hq.deck_frame
	assert_true(frame.visible, "the HQ page shows the deck frame")
	var page := hq._panel as Control
	assert_eq(page.name, &"DeckPage", "the page sits inside the frame")
	var kb := Rect2(frame.get_global_transform() * frame.keyboard_rect().position, frame.keyboard_rect().size)
	var scroll := hq._panel_host.get_parent() as ScrollContainer
	for n in _all(page):
		if n is BaseButton and (n as Control).is_visible_in_tree():
			var r := (n as Control).get_global_rect()
			if r.end.y <= scroll.get_global_rect().end.y:
				assert_false(r.intersects(kb.grow(-1.0)), "%s clear of the keyboard edge" % n.name)
			assert_true(r.position.x >= frame.frame_rect().position.x + DeckFrame.BEZEL - 0.5, "%s clear of the bezel" % n.name)
	var monitor := page.find_child("GridMonitor", true, false) as DeckMonitor
	assert_not_null(monitor, "the Grid monitor is a DECK CRT")
	assert_eq(monitor.title_label.get_theme_color(&"font_color"), Palette.CRT_AMBER, "amber readouts")
	assert_true(monitor.screen.get_child(0) is GridMapView and monitor.screen.get_child(0).material != null, "the map shows through the CRT shader")
	var roster := page.find_child("Roster", true, false) as GridContainer
	assert_eq(roster.columns, 3, "three crew columns at 1.0 (three operatives)")
	var raid := page.find_child("RaidPending", true, false) as Button
	assert_eq(raid.autowrap_mode, TextServer.AUTOWRAP_OFF, "the pending raid keeps one line")
	assert_string_contains(raid.tooltip_text, "RAID PENDING", "its words in the tooltip")
	var jack := page.find_child("JackIn", true, false) as Control
	assert_true(jack.size.x >= float(hq.get_script().get_script_constant_map()["JACK_SIDE"]) - 0.5, "JACK IN is the page's big stamp")
	var mini := monitor.screen.get_child(0) as GridMapView
	for l in mini.drawn_labels:
		assert_true(int(l["size"]) >= UiTheme.CAPTION, "mini-map label %s at caption or larger" % l["text"])
	await _close(hq)


func test_other_pages_drop_the_frame_and_maps_dim_the_city() -> void:
	var hq := _open(HQ)
	await _frames()
	hq.show_grid()
	await _frames()
	assert_false(hq.deck_frame.visible, "the net pages are not the deck (§2)")
	assert_true(hq.wireframe.city.atmosphere().state.map_mode, "map mode on the Grid (§9.5)")
	await _close(hq)


# --- Item 3: the Black Market (§11 HQ, §3.7; critique 06/09, scr/05) -----------------------------

func test_the_black_market_is_grouped_with_icons_prices_and_readable_locks() -> void:
	var c := RunManager.campaign
	c.schematics = 1  # nothing affordable
	var hq := _open(HQ)
	await _frames(4)
	var market := hq._panel.find_child("BlackMarket", true, false) as Control
	var order := []
	for n in _all(market):
		if n.name in [&"RecruitsHeader", &"BoostsHeader", &"UnlocksHeader"]:
			order.append(String(n.name))
	assert_eq(order, ["RecruitsHeader", "BoostsHeader", "UnlocksHeader"], "three headed groups in order")
	var items := market.find_children("*_*", "Button", true, false)
	var checked := 0
	for b: Button in items:
		if not (String(b.name).begins_with("Recruit_") or String(b.name).begins_with("Boost_") or String(b.name).begins_with("Unlock_")):
			continue
		checked += 1
		assert_not_null(b.get_node_or_null(^"IconMark"), "%s carries its icon" % b.name)
		assert_true(b.has_meta(&"price_kind"), "%s carries a price tag" % b.name)
		assert_true(b.disabled, "%s can't be bought with 1 Schematic" % b.name)
		var why := b.get_parent().get_node(^"Why") as Label
		assert_true(why.visible and why.text != "", "%s says why (%s)" % [b.name, why.text])
		assert_eq(b.modulate.a, 1.0, "never faded")
		var bg := Palette.over(Palette.NIGHT_SKY, Palette.TERMINAL_BG)
		assert_true(Palette.contrast(b.get_theme_color(&"font_disabled_color"), bg) >= 4.5, "%s label 4.5:1 when disabled" % b.name)
		assert_true(Palette.contrast(why.get_theme_color(&"font_color"), bg) >= 4.5, "%s reason 4.5:1" % b.name)
	assert_true(checked >= 3, "items checked (%d)" % checked)
	var locked := 0
	for id in RunManager.lookup().ids_of_class(&"ClassData"):
		var cls := RunManager.lookup().get_content(id) as ClassData
		if cls != null and not CampaignRules.class_available(RunManager.profile, RunManager.lookup(), cls):
			var rb := market.find_child("Recruit_%s" % id, true, false) as Button
			assert_not_null(rb, "a locked class shows in the market (%s)" % id)
			assert_true(rb.get_meta(&"market_locked", false), "with its lock")
			locked += 1
	assert_true(locked > 0, "a fresh profile has locked classes")
	await _close(hq)


# --- Item 4: the new campaign's planning table (§11 New campaign, §6.5; critique 03, 04) ----------

## The primary (HotButton) buttons visible under `root`.
func _primaries(root: Node) -> Array[Button]:
	var out: Array[Button] = []
	for n in _all(root):
		if n is Button and (n as Button).is_visible_in_tree() and (n as Button).theme_type_variation == UiTheme.PRIMARY:
			out.append(n)
	return out


func test_the_new_campaign_is_a_planning_table_with_one_primary() -> void:
	RunManager.reset()
	var hq := _open(HQ)
	hq.show_start()
	await _frames(4)
	var corp := hq._panel.find_child("CorporationPicker", true, false) as PlanningPicker
	assert_not_null(corp, "the target is a row of dossier tiles")
	var locked := 0
	for i in corp.tiles.size():
		assert_true(corp.tiles[i].has("corp"), "each tile is a corporation dossier")
		if corp.is_locked(i):
			locked += 1
			assert_ne(String(corp.tiles[i].get("unlock", "")), "", "a locked corp says how it unlocks")
	assert_true(locked > 0, "a fresh profile sees its locked corporations")
	assert_true(hq._panel.find_child("IceSpin", true, false) is Stepper, "ICE is a stepper")
	assert_true(hq._panel.find_child("HomePicker", true, false) is TilePicker, "the home server as tiles")
	var classes := hq._panel.find_child("ClassPicker", true, false) as PlanningPicker
	assert_true(classes.tiles[0].has("class"), "the crew as Polaroids")
	assert_false(hq.codes_open(), "the seed and codes drawer starts folded")
	assert_true(hq._panel.find_child("CodeEdit", true, false).get_parent() is CodeField, "the share code in a CodeField")
	var prim := _primaries(hq._panel)
	assert_eq(prim.size(), 1, "one primary: START")
	assert_eq(prim[0].name, &"StartCampaign")
	assert_true(Rect2(Vector2.ZERO, CANVAS).encloses(prim[0].get_global_rect()), "START on the first screen")
	for n in _all(hq._panel):
		assert_false(n is OptionButton or n is SpinBox, "no native dropdown or spin box: %s" % n.name)
	var records := hq._panel.find_child("ProfileRecords", true, false) as Control
	assert_eq(records.size_flags_horizontal & Control.SIZE_EXPAND, 0, "the records panel sizes to its words")
	# A pick flows through to the campaign.
	classes.choose(0)
	corp.choose(0)
	(hq._panel.find_child("SeedSpin", true, false) as Stepper).value = 77
	prim[0].pressed.emit()
	assert_eq(RunManager.campaign.campaign_seed, 77, "START starts the planned campaign")
	await _close(hq)


func test_planning_tiles_fit_their_words_at_every_scale() -> void:
	for scale in SCALES:
		Settings.set_text_scale(scale)
		RunManager.reset()
		var hq := _open(HQ)
		hq.show_start()
		await _frames(3)
		for pick_name in ["CorporationPicker", "HomePicker", "ClassPicker"]:
			var p := hq._panel.find_child(pick_name, true, false) as PlanningPicker
			var px := p.common_name_px()
			assert_true(px >= roundi(UiTheme.CAPTION * scale), "%s names at caption or larger (%d at %.1f)" % [pick_name, px, scale])
			for i in p.tiles.size():
				var lay: Array = p.name_layout(i, p.name_width(i), px)
				assert_true((lay[0] as PackedStringArray).size() <= PlanningPicker.NAME_LINES, "%s tile %d in two lines at %.1f" % [pick_name, i, scale])
				for line in (lay[0] as PackedStringArray):
					assert_true(Palette.mono().get_string_size(line, HORIZONTAL_ALIGNMENT_LEFT, -1, px).x <= p.name_width(i) + 0.5, "%s: '%s' fits" % [pick_name, line])
			assert_true(p.get_combined_minimum_size().x <= CANVAS.x, "%s fits the screen at %.1f" % [pick_name, scale])
		await _close(hq)
