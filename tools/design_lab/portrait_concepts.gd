extends Node
## Design lab: the portrait options (PortraitArt styles) for every kind of subject, one
## sheet per style or all styles side by side. Renders off-screen and saves PNGs.
## Run: godot --path . res://tools/design_lab/portrait_concepts.tscn -- --out=/path/dir

const CELL := 150.0
const GAP := 14.0

## Sample subjects: operatives (per class), corporate agents, machines, bosses, corp faces.
static func subjects() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var tints := [Palette.CELL_PINK, Palette.NET_CYAN, Palette.NEON_VIOLET, Palette.CRT_AMBER, Palette.CORP_SOLACE]
	var classes := ["breaker", "ghost", "rigger", "botnet", "wrecker", "phantom"]
	for i in classes.size():
		out.append({"kind": PortraitArt.Kind.OPERATIVE, "key": classes[i], "tint": tints[i % tints.size()], "name": classes[i].capitalize(), "group": "OPERATIVES"})
	for e in [["account_manager", "Account Manager", &"solace"], ["compliance_officer", "Compliance Officer", &"solace"], ["city_manager", "City Manager", &"halcyon"],
			["billing_daemon", "Billing Daemon", &"solace"], ["courier_drone", "Courier Drone", &"meridian"], ["weather_satellite", "Weather Satellite", &"orbital"]]:
		var sub := PortraitArt.enemy_subject(StringName(e[0]), e[1], e[2], false)
		sub["group"] = "ENEMIES"
		out.append(sub)
	for e in [["the_manifest", "Priority Routing", &"meridian"], ["civic_core", "Emergency Powers", &"halcyon"], ["the_handler", "The Handler", &"rebel_cell"]]:
		var sub := PortraitArt.enemy_subject(StringName(e[0]), e[1], e[2], true)
		sub["group"] = "BOSSES"
		out.append(sub)
	for c in [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]:
		out.append({"kind": PortraitArt.Kind.CORP, "key": String(c), "tint": Palette.corp_color(c), "name": String(c).capitalize(), "group": "CORPORATIONS"})
	return out


func _ready() -> void:
	var out_dir := "user://"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
	var subs := subjects()
	var groups := ["OPERATIVES", "ENEMIES", "BOSSES", "CORPORATIONS"]
	var cols := 6
	var w := int(GAP + cols * (CELL + GAP)) + 140
	var h := int(60 + groups.size() * (CELL + 60 + GAP))
	for st in PortraitArt.STYLE_NAMES.size():
		var vp := SubViewport.new()
		vp.size = Vector2i(w, h)
		vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
		add_child(vp)
		var art := Control.new()
		art.size = Vector2(w, h)
		var style := st
		art.draw.connect(func() -> void: _draw_sheet(art, style, subs, groups, cols))
		vp.add_child(art)
		for i in 3:
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		vp.get_texture().get_image().save_png(out_dir.path_join("portraits_%d.png" % st))
		vp.queue_free()
	print("PORTRAITS SAVED ", out_dir)
	get_tree().quit()


func _draw_sheet(art: Control, st: int, subs: Array[Dictionary], groups: Array, cols: int) -> void:
	art.draw_rect(Rect2(Vector2.ZERO, art.size), Color("#0B0E18"))
	PortraitArt.style = st
	art.draw_string(Palette.display(), Vector2(GAP, 40), "PORTRAITS // %d %s" % [st, PortraitArt.STYLE_NAMES[st]], HORIZONTAL_ALIGNMENT_LEFT, -1, 30, Palette.CELL_ACID)
	for g in groups.size():
		var y := 60.0 + g * (CELL + 60 + GAP)
		art.draw_string(Palette.mono(), Vector2(GAP, y + 18), groups[g], HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Palette.PAPER)
		var n := 0
		for sub in subs:
			if sub["group"] != groups[g]:
				continue
			var x := GAP + n * (CELL + GAP)
			# In a Polaroid frame, as the game shows them.
			var frame := Rect2(x, y + 26, CELL, CELL + 26)
			art.draw_rect(frame, Palette.PAPER)
			var img := Rect2(frame.position + Vector2(7, 7), Vector2(CELL - 14, CELL - 14))
			PortraitArt.draw(art, img, sub)
			art.draw_string(Palette.marker(), frame.position + Vector2(8, frame.size.y - 8), String(sub["name"]), HORIZONTAL_ALIGNMENT_LEFT, CELL - 16, 13, Palette.INK)
			n += 1
