extends Node
## Design lab (round 6 restyle): exports the game's city layout as JSON, the same city
## NeonCity draws (same seed, districts, streets, HQs and fist), framed like
## city_restyle_before.tscn: every building's extrusions, the HQs' parts and decoration,
## streets, plazas, fist roads, traffic trails, beacons and window lights.
## Run (headless, nothing is drawn):
##   godot --headless --path . res://tools/design_lab/city_export.tscn -- --out=<abs.json> [--w=3840 --h=2160 --zoom=0.633]

const Probe := preload("res://tools/design_lab/city_export_probe.gd")


func _ready() -> void:
	var out := "user://city_layout.json"
	var w := 3840
	var h := 2160
	var zoom := 0.633
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--w="):
			w = int(a.trim_prefix("--w="))
		elif a.begins_with("--h="):
			h = int(a.trim_prefix("--h="))
		elif a.begins_with("--zoom="):
			zoom = float(a.trim_prefix("--zoom="))
	var city: NeonCity = Probe.new()
	city.dim = 0.0
	city.use_bake = false
	city.size = Vector2(w, h) / zoom
	city.record()
	var data: Dictionary = city.export_dict()
	data["view"] = {"w": w, "h": h, "zoom": zoom}
	var f := FileAccess.open(out, FileAccess.WRITE)
	f.store_string(JSON.stringify(data))
	f.close()
	print("CITY EXPORT SAVED ", out, " prims=", data["prims"].size(), " streets=", data["streets"].size())
	city.free()
	get_tree().quit()
