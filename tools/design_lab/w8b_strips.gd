extends Control
## Art pass W8b review strips: plays one HQ motion in the real HQ scene and saves a frame
## every `--step` seconds (real time) to `--out` (a folder), for the strips in
## docs/art_review/W8b. Run windowed through run_windowed.py:
##   python tools/run_windowed.py --log s.log -- res://tools/design_lab/w8b_strips.tscn -- --mode=ring_swap --out=C:/tmp/f
## Modes: ring_swap (a Rank 3 ring segment swap on the SPINNER tab: the segment fills,
## recolours and pulses), crew_stamp (an operative picked on the Grid's site card: the chip's
## JACK IN stamp and the rider beside the button). Nothing here changes a rule beyond the
## scene's own public calls; it plays in its own save slot, deleted at the end.

const SCENE := "res://scenes/hq/hq_scene.tscn"
const SLOT := "w8b_strips"
const SETTLE_FRAMES := 30

var _out := ""
var _step := 0.1
var _frames := 10


func _ready() -> void:
	var mode := "ring_swap"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--mode="):
			mode = a.trim_prefix("--mode=")
		elif a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--step="):
			_step = float(a.trim_prefix("--step="))
		elif a.begins_with("--frames="):
			_frames = int(a.trim_prefix("--frames="))
	DirAccess.make_dir_recursive_absolute(_out)
	AudioDirector.muted = true
	RunManager.save_slot = SLOT
	RunManager.scene_switching_enabled = false
	RunManager.reset()
	RunManager.new_campaign(1)
	var c := RunManager.campaign
	var op := c.roster[0]
	if mode == "crew_stamp":
		c.recruit(RunManager.lookup().get_content(&"ghost") as ClassData)
	else:
		op.rank = 3
	var hq: Control = load(SCENE).instantiate()
	add_child(hq)
	hq.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	await _wait(SETTLE_FRAMES)
	match mode:
		"ring_swap":
			hq.open_loadout(op, true)
			await _wait(SETTLE_FRAMES)
			var view := hq.get_node("LoadoutView") as LoadoutView
			var options := CampaignRules.ring_segment_options(op, RunManager.lookup().get_content(op.class_id) as ClassData)
			hq.swap_segment(op.id, 1, options[0])
			view.show_spinner()
			await _wait(SETTLE_FRAMES)
			view.focus_ring(1)
		"crew_stamp":
			hq.selected_site = RunManager.launchable_sites()[0].id
			hq.show_grid()
			await _wait(SETTLE_FRAMES)
			var second := c.living_operatives()[1]
			(hq.find_child("Chip_%s" % second.id, true, false) as CrewChip).pressed.emit()
	var start := Time.get_ticks_msec()
	var next := 0.0
	var k := 0
	while k < _frames:
		await RenderingServer.frame_post_draw
		var elapsed := (Time.get_ticks_msec() - start) / 1000.0
		if elapsed + 0.0001 >= next:
			get_viewport().get_texture().get_image().save_png("%s/f%03d.png" % [_out, k])
			k += 1
			next += _step
	print("w8b_strips: saved %d frames to %s" % [k, _out])
	RunManager.delete_save()
	RunManager.save_slot = RunManager.DEFAULT_SLOT
	get_tree().quit()


func _wait(n: int) -> void:
	for i in n:
		await get_tree().process_frame
