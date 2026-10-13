extends GutTest
## ART-5 acceptance (MILESTONES "Each corporation's Grid capture vs the reference"; DECISIONS
## 2026-10-11 "M14 ART-2/ART-5 acceptance"; sheet docs/art_review/ART-5/GRID_PER_CORP.jpg): the
## defect the per-corporation captures found. The selected Site's decrypted file (SiteHoloCard)
## draws its header lines with draw_string, which cuts a line wider than its room: Meridian's
## "MERIDIAN FREIGHT SYSTEMS  //  SITE FILE 331" lost its file number at 1.0. The sub line now
## carries the corp's letterhead name, a line wider than the card wraps at a word and the header grows
## to hold it: on every corporation's Grid at 1.0 / 1.6 / 2.0 every header line fits whole, the file
## number included.

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)
const SCALES: Array[float] = [1.0, 1.6, 2.0]
const CORPS: Array[StringName] = [&"halcyon", &"meridian", &"orbital", &"rebel_cell", &"solace"]
const UNLOCKS: Array[StringName] = [&"unlock_meridian", &"unlock_halcyon", &"unlock_orbital"]

var _settings: Dictionary = {}


func before_all() -> void:
	_settings = Settings.snapshot()


func after_all() -> void:
	Settings.restore(_settings)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_art5_grid_per_corp"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()


func after_each() -> void:
	Motion.force_live = false
	Settings.restore(_settings)
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


## The HQ against `corp` (every corporation unlocked), on its Grid.
func _grid(corp: StringName) -> Control:
	var p := RunManager.profile
	for u in UNLOCKS:
		if not p.unlocks.has(u):
			p.unlocks.append(u)
	for id in ["solace", "meridian", "halcyon", "orbital"]:
		p.best_ice_by_corp[id] = 10  # REBEL_CELL opens once the others are beaten (the review pack's profile)
	RunManager.new_campaign(1, corp)
	var holder: Control = add_child_autofree(Control.new())
	holder.size = SCREEN.size
	var scene: Control = load(HQ).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _frames(4)
	scene.show_grid()
	await _frames(4)
	return scene


func test_the_site_file_header_fits_whole_on_every_corporations_grid() -> void:
	for corp in CORPS:
		for scale in TestScope.scales(SCALES):
			Settings.set_text_scale(scale)
			var hq := await _grid(corp)
			assert_eq(RunManager.campaign.corporation_id, corp, "the campaign is against %s" % corp)
			var card := hq._panel.find_child("SelectedSite", true, false) as SiteHoloCard
			assert_not_null(card, "%s x%.1f: a corporate Site's file is selected" % [corp, scale])
			if card != null:
				await _frames(2)
				var lay := card.header_lines()
				var what := "%s x%.1f: %s / %s" % [corp, scale, card.title, card.sub]
				assert_lte(float(lay["widest"]), float(lay["room"]) + 0.5, "%s: every header line fits its room %s" % [what, lay])
				var sub_lines: PackedStringArray = lay["sub"]
				assert_true(sub_lines[sub_lines.size() - 1].right(3).is_valid_int(), "%s: the file line ends on its file number %s" % [what, sub_lines])
				var box := card.get_theme_stylebox(&"panel") as StyleBoxEmpty
				assert_almost_eq(box.content_margin_top, float(lay["height"]), 0.5, "%s: the header's room holds its lines" % what)
			hq.get_parent().queue_free()
			await _frames(2)
