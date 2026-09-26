extends Node
## Design lab: renders the whole themed city into one large PNG (off-screen viewport).
## Run: godot --path . res://tools/design_lab/city_poster.tscn -- --out=/path/city.png [--w=5760 --h=3240 --zoom=0.4]

func _ready() -> void:
	var out := "user://city_poster.png"
	var w := 5760
	var h := 3240
	var zoom := 0.95
	var texture := NeonCity.DEFAULT_TEXTURE
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
		elif a.begins_with("--w="):
			w = int(a.trim_prefix("--w="))
		elif a.begins_with("--h="):
			h = int(a.trim_prefix("--h="))
		elif a.begins_with("--texture="):
			texture = int(a.trim_prefix("--texture="))
		elif a.begins_with("--zoom="):
			zoom = float(a.trim_prefix("--zoom="))
	var vp := SubViewport.new()
	vp.size = Vector2i(w, h)
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	var holder := Control.new()
	holder.size = Vector2(w, h)
	vp.add_child(holder)
	var city := NeonCity.new()
	city.dim = 0.0
	city.territory_labels = true
	city.territory_label_px = 70.0
	city.cultures = {&"solace": "arabic", &"meridian": "chinese", &"halcyon": "egyptian", &"orbital": "english"}
	city.face_texture = texture
	holder.add_child(city)
	city.set_anchors_preset(Control.PRESET_TOP_LEFT)
	city.scale = Vector2(zoom, zoom)
	city.position = Vector2.ZERO
	city.size = Vector2(w, h) / zoom
	for i in 6:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	vp.get_texture().get_image().save_png(out)
	print("POSTER SAVED ", out)
	get_tree().quit()
