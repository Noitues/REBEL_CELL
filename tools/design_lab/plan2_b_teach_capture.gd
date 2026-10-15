extends Node
## Plan 2 B-TEACH review capture (dev tool, windowed only through tools/run_windowed.py).
## `--out=<abs dir>`: one 1280x720 PNG per tutorial beat (THE TAGS, AIM, FREE NUDGE, STAGED, RAM FORECAST, UNDO) plus
## the Codex Lexicon (codex.png), and titles.txt (the tree's step titles). The same script runs on both trees; a beat
## the tree has no step for writes no PNG. tools/design_lab/plan2_b_teach_sheet.py joins the two runs.

const COMBAT := "res://scenes/combat/combat_scene.tscn"
const BEATS: Array[String] = ["THE TAGS", "AIM", "FREE NUDGE", "STAGED", "RAM FORECAST", "UNDO"]


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _shot(out: String, name: String) -> void:
	await _frames(12)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [out, name])


## Shows the step titled `title` (false when this tree has none).
func _go_to(scene: Control, title: String) -> bool:
	var t: TutorialOverlay = scene.tutorial
	var at := -1
	for i in TutorialOverlay.STEPS.size():
		if String(TutorialOverlay.STEPS[i]["title"]) == title:
			at = i
	if at < 0:
		return false
	t.step = at
	t.page = 0
	t._show()
	t.step_changed.emit()
	return true


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	RunManager.save_slot = "plan2_b_teach"
	RunManager.scene_switching_enabled = false
	AudioDirector.muted = true
	RunManager.reset()
	RunManager.new_campaign(1)
	var titles := PackedStringArray()
	for s in TutorialOverlay.STEPS:
		titles.append(String(s["title"]))
	var f := FileAccess.open("%s/titles.txt" % out, FileAccess.WRITE)
	f.store_string("\n".join(titles))
	f.close()
	var holder := Control.new()
	holder.size = Vector2(1280, 720)
	add_child(holder)
	var scene: Control = load(COMBAT).instantiate()
	scene.auto_start = false
	holder.add_child(scene)
	scene.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scene.start_fight(&"triage_unit", 7)
	scene.start_tutorial()
	scene.skip_motion()
	await _frames(30)
	var log_lines := PackedStringArray()
	# 1 THE TAGS, 2 AIM (a fresh wheel: the tag does not read PERFECT yet)
	if _go_to(scene, "THE TAGS"):
		await _shot(out, "1_THE_TAGS")
	if _go_to(scene, "AIM"):
		# One nudge off the start aim: the tag no longer reads PERFECT.
		scene.nudge(1)
		await _frames(12)
		await _shot(out, "2_AIM")
		# The nudge back reads PERFECT again; the tutorial moves on from AIM by itself (the step then shown is logged).
		scene.nudge(-1)
		await _frames(12)
		var perfect = scene.player_aim_is_perfect(scene.engine.state()) if scene.has_method("player_aim_is_perfect") else "n/a"
		log_lines.append("after the nudge back: perfect=%s, step=%s" % [perfect, TutorialOverlay.STEPS[scene.tutorial.step]["title"]])
		await _shot(out, "3_AIM_PERFECT")
	if _go_to(scene, "FREE NUDGE"):
		await _shot(out, "4_FREE_NUDGE")
	# A staged play, then STAGED / RAM FORECAST (the first card hovered) / UNDO.
	scene.play_card(0)
	await _frames(30)
	if _go_to(scene, "STAGED"):
		await _shot(out, "5_STAGED")
	if _go_to(scene, "RAM FORECAST"):
		scene._spread_hand(-1)
		await _frames(20)
		for c in scene._hand_box.get_children():
			if c is ZineCard:
				(c as ZineCard).grow_hover(true)
				(c as ZineCard)._set_lift(true)
				scene._spread_hand(c.get_index())
				break
		scene._preview_card(0)  # what a pointer over the card does: the preview and the (-N) next to RAM
		await _frames(30)
		await _shot(out, "6_RAM_FORECAST")
	if _go_to(scene, "UNDO"):
		await _shot(out, "7_UNDO")
	# The Codex: the Lexicon, scrolled to the Nudge entry when the tree has one.
	scene.queue_free()
	await _frames(5)
	var book := CodexBook.new(Codex.entries(RunManager.lookup()), 640.0, 1200.0)
	holder.add_child(book)
	book.position = Vector2(40, 40)
	book.show_section("Lexicon")
	await _frames(20)
	await _shot(out, "8_CODEX")
	var g := FileAccess.open("%s/log.txt" % out, FileAccess.WRITE)
	g.store_string("\n".join(log_lines))
	g.close()
	RunManager.delete_save()
	get_tree().quit()
