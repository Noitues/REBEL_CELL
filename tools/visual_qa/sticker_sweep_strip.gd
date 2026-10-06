extends Node
## B1d: a frame strip of the sticker sweep scheduler (windowed, via tools/run_windowed.py). Three stickers (a pink
## kit verb, a holo word, a baked one) sit on the CRT backdrop; the scheduler sweeps the primary one only. The
## strip is `--frames` shots of the sweep, one every `--step` seconds, plus one focus shot (peel-back, no rainbow).
## usage: godot --path . res://tools/visual_qa/sticker_sweep_strip.tscn -- --out=<abs dir> [--frames=8] [--step=0.2]

var _out := ""
var _frames := 8
var _step := 0.2


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			_out = a.trim_prefix("--out=")
		elif a.begins_with("--frames="):
			_frames = int(a.trim_prefix("--frames="))
		elif a.begins_with("--step="):
			_step = float(a.trim_prefix("--step="))
	_run.call_deferred()


func _wait(sec: float) -> void:
	await get_tree().create_timer(sec).timeout


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(_out)
	var bg := ColorRect.new()
	bg.color = Color(0.1, 0.1, 0.14)
	bg.size = Vector2(800, 450)
	add_child(bg)
	var row := HBoxContainer.new()
	row.position = Vector2(60, 150)
	row.add_theme_constant_override(&"separation", 40)
	add_child(row)
	var pink := VerbSticker.new("RESUME", VerbSticker.Fill.PINK, 34.0)
	var holo := HoloSticker.word("OPTIONS", VinylSticker.Fill.YELLOW, 1.0, 22)
	var art := VerbSticker.new("CANCEL", VerbSticker.Fill.YELLOW, 50.0, 0.0, "")
	art.art_key = "dialog_cancel"
	art._load_art()
	art._fit()
	for c: Control in [pink, holo, art]:
		row.add_child(c)
	await _wait(0.5)
	# The first shot at once the scheduler is running: wait for the primary's sweep to start.
	var guard := 0
	while StickerSweepQueue.sweeping() == 0 and guard < 800:
		await get_tree().process_frame
		guard += 1
	for i in _frames:
		get_viewport().get_texture().get_image().save_png("%s/sweep_%02d.png" % [_out, i])
		print("frame %d sweeping=%d t=%d" % [i, StickerSweepQueue.sweeping(), Time.get_ticks_msec()])
		await _wait(_step)
	await _wait(2.0)
	holo.grab_focus()
	await _wait(0.6)
	get_viewport().get_texture().get_image().save_png("%s/focus.png" % _out)
	print("focus rainbow=%s sweeping=%d" % [str(holo.sticker.rainbow), StickerSweepQueue.sweeping()])
	get_tree().quit()
