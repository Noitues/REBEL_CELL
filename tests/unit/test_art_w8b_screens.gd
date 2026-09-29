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
