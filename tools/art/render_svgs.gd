extends SceneTree
## Art pass W8a: rasterises the baked SVG art the way the game does (Image.load_svg_from_string)
## into PNGs for review. Headless:
##   godot --headless --path . -s tools/art/render_svgs.gd -- --out=<dir> [--scale=2]

const FILES := ["res://assets/art/logo_rebel_cell.svg", "res://assets/art/scrawl_never_sleep.svg",
	"res://assets/art/scrawl_trust_no_one.svg", "res://assets/art/landmarks/solace.svg",
	"res://assets/art/landmarks/meridian.svg", "res://assets/art/landmarks/halcyon.svg",
	"res://assets/art/landmarks/orbital.svg", "res://assets/art/landmarks/rebel_cell.svg"]


func _init() -> void:
	var out := "user://svg_render"
	var s := 2.0
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--scale="):
			s = a.trim_prefix("--scale=").to_float()
	DirAccess.make_dir_recursive_absolute(out)
	for f in FILES:
		var img := Image.new()
		var err := img.load_svg_from_string(FileAccess.get_file_as_string(f), s)
		var name: String = String(f).get_file().get_basename()
		if err != OK:
			printerr("failed ", f)
			continue
		img.save_png(out.path_join(name + ".png"))
		print("rendered ", name, " ", img.get_size())
	quit(0)
