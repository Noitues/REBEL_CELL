extends GutTest
## HQ-B (f) (M14, designer rulings Q7, Q8, Q9, Q13 2026-10-05): the pirate radio is one ON AIR
## line; the story so far is a STORY section in the Codex (the pause menu's) and a corp-news
## toast when a beat is revealed; Codex / Options / Save live in the pause menu only (the game
## autosaves; Save & quit stays there); the Rank 3 inner-ring swaps live in the Loadout's
## SPINNER tab (no dossier lists).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_hq_b_story"
	RunManager.scene_switching_enabled = false
	RunManager.delete_save()
	RunManager.reset()
	RunManager.new_campaign(1)


func after_each() -> void:
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


func test_a_beat_revealed_since_the_hq_showed_is_told_as_corp_news_and_lands_in_the_codex() -> void:
	var c := RunManager.campaign
	var hq := await _hq()
	var beats := CampaignRules.revealed_beats(c, RunManager.corporation)
	assert_eq(hq.tell_new_beats().size(), 0, "nothing new since the HQ showed")
	var path := CampaignRules.story_path(c, RunManager.corporation)
	if path == null or path.beats.size() <= beats.size():
		pending("no beat left to reveal on this story path")
		return
	c.story_beats_revealed += 1
	var told: PackedStringArray = hq.tell_new_beats()
	assert_eq(told.size(), 1, "the new beat is told once")
	var now := CampaignRules.revealed_beats(c, RunManager.corporation)
	assert_eq(told[0], TextDb.t(now[now.size() - 1], "title"), "its title")
	assert_eq(hq.tell_new_beats().size(), 0, "and not again")
	var story: Array = Codex.entries(RunManager.lookup(), RunManager.profile).get(Codex.STORY, [])
	assert_eq(story.size(), now.size(), "the Codex's STORY holds every revealed beat")
	assert_eq(Codex.entries(RunManager.lookup(), RunManager.profile).keys()[0], Codex.STORY, "first in the Codex")


func test_codex_options_and_save_are_the_pause_menus_only() -> void:
	var hq := await _hq()
	for gone in ["CityGrid", "SaveButton", "SettingsButton", "CodexButton"]:
		assert_null(hq._panel.find_child(gone, true, false), "%s is not on the HQ page" % gone)
	for n in hq._panel.find_children("*", "Button", true, false):
		var t := String((n as Button).text).to_lower()
		assert_false(t == "codex" or t == "settings" or t == "save", "no '%s' button on the page" % t)
	hq.open_settings()
	await _frames(2)
	var menu: PauseMenu = hq._settings_panel
	# The pause menu's rows (ABANDON-QUIT's cells): Options, Codex, and the quit that saves.
	for want in ["Options", "Codex", "QuitMain"]:
		assert_not_null(menu.find_child(want, true, false), "the pause menu has %s" % want)
	hq.open_settings()


func test_the_radio_is_one_on_air_line() -> void:
	var hq := await _hq()
	var ticker := hq._panel.find_child("OnAir", true, false) as OnAirTicker
	assert_not_null(ticker, "ON AIR (Q7)")
	assert_eq(ticker.get_global_rect().end.y, hq._panel.get_global_rect().end.y, "one line along the page's foot")
	assert_null(hq._panel.find_child("PirateRadio", true, false), "no radio panel")


func test_the_inner_ring_swaps_live_in_the_loadouts_spinner_tab() -> void:
	var c := RunManager.campaign
	var op := c.living_operatives()[0]
	op.rank = 3
	var hq := await _hq()
	for n in hq._panel.find_children("*", "OptionButton", true, false):
		fail_test("no OptionButton on the HQ page (the dossiers' segment lists went): %s" % n.name)
	hq.open_loadout(op)
	await _frames(2)
	var view := hq.get_node("LoadoutView") as LoadoutView
	view.show_spinner()
	await _frames(2)
	var options := CampaignRules.ring_segment_options(op, RunManager.lookup().get_content(op.class_id) as ClassData)
	if options.is_empty():
		pending("this class has no Rank 3 segment options")
		return
	assert_not_null(view.find_child("Swap_%s" % options[0], true, false), "the SPINNER tab offers the swap (Q13)")
	# The drop (mouse drag or the pad's pick-up then the segment) is the rules' swap.
	hq._on_dropped({"kind": "segment", "op": op.id, "segment": options[0]}, {"kind": "ring", "value": 1})
	await _frames(2)
	assert_eq(c.get_operative(op.id).ring_segment_ids[1], options[0], "swapped through the rules")
