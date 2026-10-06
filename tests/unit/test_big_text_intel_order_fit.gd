extends GutTest
## M14 BIG-TEXT: THREAT INTEL (the decrypted holo) and the raid setup's work order fit their rooms at
## text scales 1.0 / 1.6 / 2.0 (the layout is 1280x720 at 1080p too: the stretch keeps it). Every line
## of each is whole inside its panel and inside what the page shows of it; the scale never falls
## below HqLayout.FIT_FLOOR of the player's; the MORE tab shows only when the order is folded and the
## two pages together carry every row. Views never change state.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
## A tilted sheet's corners leave its rect by a pixel or two.
const TILT_SLACK := 6.0
const ROWS: Array[String] = ["RaidTarget", "RaidUnits", "RaidStrength", "HomeForecast", "ThreatsStopped"]

var _scale: float


func before_each() -> void:
	_scale = Settings.text_scale
	Motion.force_live = false
	AudioDirector.muted = true
	RunManager.save_slot = "gut_big_text_fit"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	CityBakeCache.shutdown()


func after_each() -> void:
	CityBakeCache.shutdown()
	Motion.force_live = false
	if not is_equal_approx(Settings.text_scale, _scale):
		Settings.set_text_scale(_scale)
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _raid_campaign() -> void:
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	c.schematics = 400
	for t: StringName in [&"firewall_relay", &"safehouse"]:
		var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
		if open.is_empty():
			break
		var run := RunState.new()
		run.site_id = open[0].id
		CampaignRules.on_run_completed(c, corp, RunManager.config(), run)
		CampaignRules.claim(c, corp, RunManager.config(), RunManager.lookup(), open[0].id, t)
	c.armory = [&"turret", &"ice_lock", &"honeypot_node"]
	if c.pending_raids.is_empty():
		CampaignRules.queue_raid(c, corp, RC.RaidTriggerSource.STORY, &"", "test")


## 0: the review pack's raid (two entry routes, one node); 1: two nodes and a wider network.
func _campaign(kind: int) -> void:
	if kind == 1:
		_raid_campaign()
		return
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var grid := RunManager.corporation.city_grid
	var first: StringName = grid.get_site(grid.home_site_id).links[0]
	c.schematics = 400
	CampaignRules.claim(c, RunManager.corporation, RunManager.config(), RunManager.lookup(), first, &"firewall_relay")
	c.armory = [&"turret", &"ice_lock", &"decoy"]
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})


func _hq(scale: float) -> Control:
	Settings.set_text_scale(scale)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	scene.show_raid()
	await _frames(8)
	return scene


## Every visible text Control under `root` (Labels and RichTextLabels).
func _texts(root: Node, out: Array[Control]) -> void:
	for ch in root.get_children():
		if ch is Control and not (ch as Control).is_visible_in_tree():
			continue
		if ch is Label or ch is RichTextLabel:
			out.append(ch)
		_texts(ch, out)


## Asserts every line under `panel` is whole: inside `panel` and inside `shown`, and its box is as
## tall as its text needs.
func _assert_whole(panel: Control, shown: Rect2, tag: String, slack: float = 1.0) -> int:
	var texts: Array[Control] = []
	_texts(panel, texts)
	var inside := panel.get_global_rect().grow(slack)
	for t in texts:
		var r := t.get_global_rect()
		if r.size.x <= 0.0 or (t is Label and (t as Label).text == ""):
			continue
		assert_true(inside.encloses(r), "%s: '%s' inside its panel (%s in %s)" % [tag, (t as Label).text if t is Label else t.name, r, inside])
		assert_true(shown.grow(slack).encloses(r), "%s: '%s' inside what the page shows (%s in %s)" % [tag, (t as Label).text if t is Label else t.name, r, shown])
		assert_gte(r.size.y + 1.0, t.get_combined_minimum_size().y, "%s: '%s' is as tall as its text (%s)" % [tag, t.name, r.size.y])
	return texts.size()


func _intel_body(kind: int) -> void:
	_campaign(kind)
	for scale in SCALES:
		var hq := await _hq(scale)
		var page: Control = hq._panel
		var tag := "x%.1f" % scale
		var column := page.get_node("CardColumn") as Control
		var fit := page.find_child("ThreatIntelFit", true, false) as FitBuildBox
		var intel := page.find_child("ThreatIntel", true, false) as Control
		assert_not_null(intel, tag)
		assert_gte(fit.mul, HqLayout.INTEL_FIT_FLOOR - 0.001, "%s: THREAT INTEL's scale stays at the floor or above (%.2f)" % [tag, fit.mul])
		assert_false(fit.overflow, "%s: THREAT INTEL fits its room (mul %.2f detail %d min %s column %s)" % [tag, fit.mul, fit.detail, fit.get_combined_minimum_size(), column.size])
		var shown := column.get_global_rect()
		assert_true(shown.grow(1.0).encloses(intel.get_global_rect()), "%s: THREAT INTEL whole in the column (%s in %s)" % [tag, intel.get_global_rect(), shown])
		var lines := _assert_whole(intel, shown, tag)
		assert_gt(lines, 1, "%s: its lines were checked" % tag)
		if scale <= 1.0:
			assert_almost_eq(fit.mul, 1.0, 0.001, "%s: no shrink at the base size" % tag)
		hq.get_parent().queue_free()
		await _frames(1)


func _order_body(kind: int) -> void:
	_campaign(kind)
	for scale in SCALES:
		var hq := await _hq(scale)
		var page: Control = hq._panel
		var tag := "x%.1f" % scale
		var order := page.get_node("WorkOrder") as Control
		var scroll := page.find_child("WorkOrderPaper", true, false) as Control
		var fit := page.find_child("WorkOrderFit", true, false) as FitBuildBox
		var more := page.find_child("OrderMore", true, false) as Control
		assert_not_null(fit, tag)
		assert_gte(fit.mul, fit.floor_for(fit.detail) - 0.001, "%s: the order scale stays at its floor or above (%.2f)" % [tag, fit.mul])
		assert_eq(more.visible, fit.detail != 0, "%s: the MORE tab shows only when the order is folded" % tag)
		var tab_top := (page.find_child("Tab_CREW", true, false) as Control).get_global_rect().position.y
		assert_lte(order.get_global_rect().end.y, tab_top + 1.0, "%s: the order ends above the tabs" % tag)
		var seen: Array[String] = []
		var shown := scroll.get_global_rect()
		var paper := page.find_child("RaidCard", true, false) as Control
		assert_true(shown.grow(TILT_SLACK).encloses(paper.get_global_rect()), "%s: the paper is whole in its room (%s in %s)" % [tag, paper.get_global_rect(), shown])
		_assert_whole(paper, shown, tag, TILT_SLACK)
		for n in ROWS:
			var l := paper.find_child(n, true, false) as Control
			if l != null and l.is_visible_in_tree():
				seen.append(n)
		if fit.detail == 0:
			assert_eq(seen.size(), ROWS.size(), "%s: every row shows on the whole order" % tag)
		else:
			assert_eq(seen, ["RaidTarget", "RaidUnits"] as Array[String], "%s: the fold keeps TARGET and UNITS" % tag)
			var title := paper.find_child("PaperTitle", true, false) as Control
			assert_true(title.is_visible_in_tree(), "%s: and the title" % tag)
			# MORE: the rest on its own page, every row whole.
			more.pressed.emit()
			await _frames(6)
			assert_true(more.visible, "%s: BACK shows" % tag)
			paper = page.find_child("RaidCard", true, false) as Control
			shown = scroll.get_global_rect()
			assert_true(shown.grow(TILT_SLACK).encloses(paper.get_global_rect()), "%s: page 2 whole in its room (%s in %s)" % [tag, paper.get_global_rect(), shown])
			_assert_whole(paper, shown, tag + " p2", TILT_SLACK)
			for n in ROWS:
				var l := paper.find_child(n, true, false) as Control
				if l != null and l.is_visible_in_tree() and not seen.has(n):
					seen.append(n)
			assert_eq(seen.size(), ROWS.size(), "%s: the two pages together carry every row (%s)" % [tag, seen])
			more.pressed.emit()
			await _frames(6)
			assert_eq((page.find_child("WorkOrderFit", true, false) as FitBuildBox).detail, 1, "%s: BACK returns to the fold" % tag)
		hq.get_parent().queue_free()
		await _frames(1)


func test_the_fit_box_shrinks_to_the_floor_then_folds() -> void:
	var box := FitBuildBox.new()
	add_child_autofree(box)
	box.builder = func(m: float, d: int) -> Control:
		var l := Label.new()
		l.text = "line"
		l.custom_minimum_size.y = 100.0 * m * (1.0 if d == 0 else 0.2)
		return l
	box.details = [0, 1]
	box.fit(100.0, 1000.0)
	assert_almost_eq(box.mul, 1.0, 0.001, "roomy: no shrink")
	box.fit(100.0, 90.0)
	assert_lte(box.mul, 0.91, "tight: smaller")
	assert_gte(box.mul, HqLayout.FIT_FLOOR - 0.001, "never below the floor")
	assert_eq(box.detail, 0, "it fit whole")
	box.fit(100.0, 50.0)
	assert_eq(box.detail, 1, "folded when the floor is still too tall")
	assert_false(box.overflow, "and the fold fits")
	box.fit(100.0, 5.0)
	assert_true(box.overflow, "nothing fits: flagged, at the floor")
	assert_almost_eq(box.mul, HqLayout.FIT_FLOOR, 0.001, "at the floor")


func test_threat_intel_is_whole_at_every_text_size_review_raid() -> void:
	await _intel_body(0)


func test_threat_intel_is_whole_at_every_text_size_wide_network() -> void:
	await _intel_body(1)


func test_the_work_order_is_whole_or_folded_at_every_text_size_review_raid() -> void:
	await _order_body(0)


func test_the_work_order_is_whole_or_folded_at_every_text_size_wide_network() -> void:
	await _order_body(1)
