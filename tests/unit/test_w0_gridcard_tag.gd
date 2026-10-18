extends GutTest
## W0 GRIDCARD: a hovered node's tag clears the selection ring and the lit node's own ring (and
## its ticks) by at least CityMapOverlay.RING_TAG_CLEAR px, so a ring never cuts the word
## ("Site" read "ite"). The HQ Grid at 1280x720 (the canvas the 1920x1080 window scales: the
## layout is the same) at text 1.0. The selected-Site card shows on the first select.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Vector2(1280, 720)
const SETTLE := 12
## Nodes lit one after another (the first N labelled ones).
const LIT_MAX := 8

var _text_scale_before: float = 1.0


func before_all() -> void:
	_text_scale_before = Settings.text_scale


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_w0_gridcard"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	if not is_equal_approx(Settings.text_scale, _text_scale_before):
		Settings.set_text_scale(_text_scale_before)
	AudioDirector.muted = false
	RunManager.delete_save()
	DirAccess.remove_absolute(RunManager.profile_path())
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	RunManager.reset()
	RunManager.scene_switching_enabled = true


func _frames(n: int = 3) -> void:
	for i in n:
		await get_tree().process_frame


func _gap(rect: Rect2, c: Vector2) -> float:
	var q := Vector2(clampf(c.x, rect.position.x, rect.end.x), clampf(c.y, rect.position.y, rect.end.y))
	return q.distance_to(c)


func test_hover_tag_clears_the_selection_ring_and_the_lit_ring() -> void:
	Settings.set_text_scale(1.0)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	RunManager.new_campaign(1)
	hq.show_grid()
	await _frames(SETTLE)
	var open := CampaignRules.launchable_sites(RunManager.campaign, RunManager.corporation, RunManager.config())
	assert_false(open.is_empty(), "a launchable Site")
	hq.select_site(open[0].id)
	await _frames(SETTLE)
	# The selected-Site card is in the tree and shown on the first select.
	var card := hq.find_child("SelectedSite", true, false) as Control
	assert_not_null(card, "the selected Site's card exists after the first select")
	if card != null:
		assert_true(card.is_visible_in_tree(), "and is visible")
	var overlay: CityMapOverlay = hq.city_overlay
	var k := Settings.text_scale
	var clear := CityMapOverlay.RING_TAG_CLEAR * k
	var lit := 0
	for n in overlay.nodes:
		if lit >= LIT_MAX:
			break
		overlay.hover_id = n["id"]
		var rects := overlay.label_rects()
		if not rects.has(String(n["id"])):
			continue
		lit += 1
		var r: Rect2 = rects[String(n["id"])]
		var sc := overlay.ring_centre()
		if sc.x != INF:
			assert_gte(_gap(r, sc), overlay.ring_radius() + clear - 0.01, "%s's tag clears the selection ring by %s px" % [n["id"], clear])
		var hc := overlay.hover_centre()
		if hc.x != INF:
			assert_gte(_gap(r, hc), overlay.hover_ring_radius() + clear - 0.01, "%s's tag clears its own lit ring by %s px" % [n["id"], clear])
	assert_gt(lit, 0, "some hovered node was labelled")
	overlay.hover_id = &""
