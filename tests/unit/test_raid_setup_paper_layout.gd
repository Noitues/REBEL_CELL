extends GutTest
## A-073 fix (RAID_SETUP R2): the forecast chip takes no room from the corp work order. The paper keeps
## its pre-chip layout at 1280x720, text 1.0 (whole rows, no MORE tab, the INTERCEPTED stamp), and the
## chip stands clear of the paper, the tabs column and the card column.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Vector2(1280, 720)
## The pre-chip paper (13f0c7de) at this size: it filled its room, so it is at least this tall.
const PAPER_MIN_H := 330.0


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_raid_paper"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	Settings.text_scale = 1.0


func after_each() -> void:
	Settings.text_scale = 1.0


func _raid() -> Control:
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN
	var hq: Control = load(HQ).instantiate()
	holder.add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	hq.new_campaign(1)
	var c := RunManager.campaign
	c.pending_raids.append({"raid_id": "raid_heat_25", "source": RC.RaidTriggerSource.HEAT_THRESHOLD, "heat": 25})
	hq.show_raid()
	for i in 6:
		await get_tree().process_frame
	return hq


func _paper(page: Control) -> RaidPaper:
	var card: RaidPaper = null
	for n in page.find_children("*", "RaidPaper", true, false):
		card = n
	return card


func test_the_paper_keeps_its_rows_and_stamp() -> void:
	var hq := await _raid()
	var page: Control = hq._panel
	var card := _paper(page)
	assert_not_null(card, "the work order paper is built")
	var more := page.find_child("OrderMore", true, false) as Control
	assert_true(more == null or not more.visible, "the order is whole: no MORE tab")
	for row in ["ThreatsStopped", "InfectionForecast"]:
		var l := card.find_child(row, true, false) as Control
		assert_not_null(l, row)
		assert_true(l.is_visible_in_tree(), "%s shows" % row)
	assert_true(card.stamp_rect().has_area(), "the INTERCEPTED stamp stands on the paper")
	assert_eq(card.title_label.get_line_count(), 1, "the title does not wrap")
	assert_gte(card.get_global_rect().size.y, PAPER_MIN_H, "the paper keeps its height")
	assert_gte(card.get_global_rect().size.x, 228.0, "the paper keeps its width")


func test_the_chip_is_clear_of_the_paper_and_the_columns() -> void:
	var hq := await _raid()
	var page: Control = hq._panel
	var chip := page.get_node_or_null("Projection") as Control
	assert_not_null(chip, "the forecast chip is a page child, not in the work order")
	var r := chip.get_global_rect()
	assert_false(r.intersects(_paper(page).get_global_rect()), "chip clear of the paper")
	for name in ["HandTabs", "CardColumn", "VerbSlot"]:
		assert_false(r.intersects((page.get_node(name) as Control).get_global_rect()), "chip clear of %s" % name)
	assert_lte(r.end.y, (page.get_node("HandTabs") as Control).get_global_rect().position.y, "chip stands over the hand row")
	assert_true(Rect2(Vector2.ZERO, SCREEN).encloses(r), "chip on screen")
