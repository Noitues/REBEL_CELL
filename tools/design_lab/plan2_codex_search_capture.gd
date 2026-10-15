extends Node
## Plan 2 Codex search review capture (dev tool, windowed only through tools/run_windowed.py).
## `--out=<abs dir>`: saves search.png (the field with "nud" typed, the results page).


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _ready() -> void:
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out)
	AudioDirector.muted = true
	var bg := ColorRect.new()
	bg.color = Color(0.02, 0.03, 0.06)
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	var book := CodexBook.new(Codex.entries(RunManager.lookup()), 700.0, 1200.0)
	book.position = Vector2(40, 10)
	add_child(book)
	await _frames(10)
	book.search.text = "nud"
	book.search.text_changed.emit("nud")
	await _frames(15)
	get_viewport().get_texture().get_image().save_png("%s/search.png" % out)
	get_tree().quit()
