extends GutTest
## HQ-B (e) (M14, the HQ redesign's `jack_in_flow.jpg` / `.gif`): JACK IN is every netrun's
## start: a Site selected on the HQ's own city, the runner preselected (the lifted card), the
## pink sticker, and the 4.6 jack along the link on this same city (RunManager.jack_link reads
## the HQ's map: the owned end and the Site, both on screen). A saved run's resume plays the
## same jack from that run's Site (no deck-CRT push: the HQ has no deck monitor any more).

const HQ := "res://scenes/hq/hq_scene.tscn"
const SCREEN := Rect2(0, 0, 1280, 720)


func before_each() -> void:
	AudioDirector.muted = true
	RunManager.save_slot = "gut_hq_b_jack"
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


func test_the_jack_runs_along_the_link_on_the_hqs_own_city() -> void:
	# jack_link reads the maps of the scene on screen: the HQ is it in the game (a root child).
	var hq: Control = load(HQ).instantiate()
	get_tree().root.add_child(hq)
	autofree(hq)
	await _frames(14)
	var site: StringName = hq.selected_site
	var was := get_tree().current_scene
	get_tree().current_scene = hq
	var link := RunManager.jack_link(site, hq.selected_operative)
	get_tree().current_scene = was
	assert_false(link.is_empty(), "a link to jack along")
	assert_eq((link["points"] as PackedVector2Array).size(), 2, "both ends on the HQ's map (the owned end and the Site)")
	var p: Vector2 = (link["points"] as PackedVector2Array)[1]
	var at: Vector2 = hq.city_overlay.get_global_transform_with_canvas() * hq.city_overlay.icon_at(site)
	assert_almost_eq(p.x, at.x, 1.0, "the link ends on the selected Site")
	assert_almost_eq(p.y, at.y, 1.0)
	assert_string_contains((hq._panel.find_child("SystemWord", true, false) as Label).text, String(link["to"]), "the system word names the jack's ends")


func test_jack_in_starts_the_run_through_the_one_netrun_start() -> void:
	var hq := await _hq()
	var site: StringName = hq.selected_site
	var op: OperativeState = hq.selected_op()
	(hq._panel.find_child("Launch", true, false) as VerbSticker).pressed.emit()
	await _frames(2)
	assert_not_null(RunManager.netrun, "RunManager.launch's path: go_to_netrun, then the run")
	assert_eq(RunManager.netrun.run.site_id, site)
	assert_eq(RunManager.netrun.run.operative.id, op.id, "the lifted card runs it")


func test_a_saved_run_resumes_with_the_same_jack_from_its_site() -> void:
	var hq := await _hq()
	var site: StringName = hq.selected_site
	(hq._panel.find_child("Launch", true, false) as VerbSticker).pressed.emit()
	await _frames(2)
	assert_true(RunManager.has_active_run())
	hq.show_hq()
	await _frames(3)
	var jack := hq._panel.find_child("Launch", true, false) as VerbSticker
	assert_not_null(jack, "JACK IN while a run waits: the resume")
	assert_eq(hq.resume_site(), site, "the resume jacks from the run's own Site")
	assert_eq((hq._panel.find_child("SystemWord", true, false) as Label).text, hq.jack_system_word(CampaignRules.site_data(RunManager.corporation, site)), "the same system word")
	assert_null(hq._panel.find_child("JackIn", true, false), "no deck-monitor JACK IN stamp")
	for n in get_tree().get_nodes_in_group(Fx.JACK_FOCUS_GROUP):
		if hq.is_ancestor_of(n):
			assert_eq(n, jack, "the only jack focus on the HQ is the sticker")
