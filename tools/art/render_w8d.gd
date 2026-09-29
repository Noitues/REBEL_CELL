extends SceneTree
## Art pass W8d: rasterises the campaign end's baked SVG art the way the game does
## (Image.load_svg_from_string) into PNGs for review (tools/art/w8d_sheet.py tints and lays
## them out). Headless:
##   godot --headless --path . -s tools/art/render_w8d.gd -- --out=<dir> [--scale=2]

const DIR := "res://assets/art/campaign_end/"


func _init() -> void:
	var out := "user://w8d_render"
	var s := 2.0
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--scale="):
			s = a.trim_prefix("--scale=").to_float()
	DirAccess.make_dir_recursive_absolute(out)
	var failed := 0
	for f in DirAccess.get_files_at(DIR):
		if not f.ends_with(".svg"):
			continue
		var img := Image.new()
		var err := img.load_svg_from_string(FileAccess.get_file_as_string(DIR + f), s)
		if err != OK:
			printerr("failed ", f)
			failed += 1
			continue
		img.save_png(out.path_join(f.get_basename() + ".png"))
		print("rendered ", f, " ", img.get_size())
	quit(1 if failed > 0 else 0)
