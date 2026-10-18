extends Node
## W0 ARTFIX Site-names capture (dev tool, windowed only through tools/run_windowed.py, 1920x1080).
## `--out=<abs dir>`: 1_grid (a Site selected: its card; a second Site hovered: its tooltip plate drawn the
## way the engine would, native tooltips never open in the quiet window) and 4_reward (the new header).

const HQ := "res://scenes/hq/hq_scene.tscn"
const NETRUN := "res://scenes/netrun_map/netrun_scene.tscn"
const SIZE := Vector2(1920, 1080)

var out: String = ""


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(shot_name: String) -> void:
	await _frames(12)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, shot_name])


func _mount(path: String) -> Control:
	var holder := Control.new()
	holder.size = get_viewport().get_visible_rect().size
	add_child(holder)
	var scene: Control = load(path).instantiate()
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	return scene


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	await _frames(6)
	RunManager.save_slot = "w0_artfix"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.reset()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var corp := RunManager.corporation
	var hq := _mount(HQ)
	await _frames(60)
	var open := CampaignRules.launchable_sites(c, corp, RunManager.config())
	if open.is_empty():
		push_error("ERROR: no launchable Site")
	else:
		hq.select_site(open[0].id)
	await _frames(10)
	PageTransition.settle(hq)
	await _frames(60)
	var card := hq.find_child("SelectedSite", true, false) as Control
	print("card ", card.get_global_rect() if card != null else "NONE", " panel ", hq.panel_name)
	if card != null:
		print("card vis ", card.is_visible_in_tree(), " mod ", card.modulate, " selfmod ", card.self_modulate, " parent ", card.get_parent().name, " pvis ", card.get_parent().is_visible_in_tree(), " z ", card.z_index)
		for ch in card.find_children("*", "CanvasItem", true, false):
			var ci := ch as CanvasItem
			if ci.modulate.a < 0.99 or not ci.visible or ci.material != null:
				print("cardchild ", ci.name, " ", ci.get_class(), " vis ", ci.visible, " a ", ci.modulate.a, " mat ", ci.material)
		print("card script ", card.get_script().resource_path, " size ", card.size, " mat ", card.material, " clip ", card.clip_children)
		for ch in hq.get_children():
			print("hqchild ", ch.name, " ", ch.get_class(), " vis ", (ch as CanvasItem).visible if ch is CanvasItem else true, " z ", (ch as CanvasItem).z_index if ch is CanvasItem else 0)
		var q: Node = card
		while q != null:
			print("chain ", q.name, " mod ", (q as CanvasItem).modulate if q is CanvasItem else Color.WHITE, " sm ", (q as CanvasItem).self_modulate if q is CanvasItem else Color.WHITE, " ", q.get_class(), " z ", (q as CanvasItem).z_index if q is CanvasItem else -1, " clip ", (q as Control).clip_contents if q is Control else false, " rect ", (q as Control).get_global_rect() if q is Control else Rect2())
			q = q.get_parent()
		q = card
		while q != null and q != hq:
			if q is CanvasItem and not (q as CanvasItem).visible:
				print("hidden ancestor ", q.name)
			q = q.get_parent()
	if card != null and OS.get_cmdline_user_args().has("--lift"):
		var gp := card.get_global_rect().position
		card.get_parent().remove_child(card)
		hq.add_child(card)
		card.top_level = true
		card.global_position = gp
		card.z_index = 50
	# Hover: another Site of the Grid (the overlay's own hover tag).
	if hq.city_overlay != null and open.size() > 1:
		hq.city_overlay.hover_id = open[1].id
		print("hover ", open[1].id, " selected ", open[0].id)
	else:
		push_error("ERROR: no overlay / second Site to hover")
	await _shot("1_grid")
	hq.get_parent().queue_free()
	await _frames(3)
	RunManager.reset()
	RunManager.new_campaign(1)
	var nr := _mount(NETRUN)
	nr.start_run(1)
	await _frames(60)
	var run := RunManager.netrun.run
	run.pending_rewards.append({"kind": "card", "options": ["twist", "jam", "cache"]})
	run.phase = RunState.Phase.REWARD
	nr._show_current()
	await _frames(60)
	await _shot("4_reward")
	RunManager.delete_save()
	get_tree().quit()
