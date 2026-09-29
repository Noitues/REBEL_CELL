extends Node
## Design lab: the portrait options (PortraitArt styles) for every kind of subject, one
## sheet per style or all styles side by side. Renders off-screen and saves PNGs.
## Run: godot --path . res://tools/design_lab/portrait_concepts.tscn -- --out=/path/dir
##
## Art pass W5 sheets (`--sheet=<name>`, windowed through tools/run_windowed.py):
## - classes: the eight classes x four expressions in NEON BUST, a row in each other look
##   and a row of per-operative variation (classes.png);
## - enemies: every corp's enemies as busts (NEON BUST) plus hologram busts (enemies.png);
## - boss: the boss hologram behind a stand-in wheel at 1280x720 (boss_hologram.png) and
##   the five bosses (bosses.png);
## - intro: the boss intro reveal as a strip, then the reduce-effects cross-fade
##   (boss_intro_strip.png).

const CELL := 150.0
const GAP := 14.0
## W5 sheets: cell side, caption band, the sheet backdrop and the lettering.
const W5_CELL := 128.0
const W5_BAND := 24.0
const W5_LEFT := 150.0
const W5_TITLE := 26
const W5_TEXT := 15
const W5_BACK := Palette.NIGHT_SKY
## Stand-in wheel for the boss composition (1280x720): centre, radius, slice count.
const WHEEL_AT := Vector2(820, 380)
const WHEEL_R := 150.0
const WHEEL_SLICES := 6
## Intro strip: frames of the reveal, and of the reduce-effects cross-fade.
const INTRO_FRAMES := 6
const FADE_FRAMES := 4
const STRIP_CELL := 200.0

## Sample subjects: operatives (per class), corporate agents, machines, bosses, corp faces.
static func subjects() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for c in PortraitArt.CLASS_IDS:
		var sub := PortraitArt.operative_subject(c, &"", String(c).capitalize())
		sub["group"] = "OPERATIVES"
		out.append(sub)
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
		out.append({"kind": PortraitArt.Kind.CORP, "key": String(c), "tint": Palette.corp_color(c), "name": String(c).capitalize(), "group": "CORPORATIONS",
			"corp": c, "pattern": Palette.corp_pattern_id(c)})
	return out


## Every content enemy grouped by corp (agents, then machines, then bosses; by id).
static func enemies_by_corp() -> Dictionary:
	var out := {}
	var files := DirAccess.get_files_at("res://content/enemies")
	files.sort()
	for f in files:
		if not f.ends_with(".tres"):
			continue
		var e := load("res://content/enemies/" + f) as EnemyData
		if e == null or e.corporation_id == &"":
			continue
		if not out.has(e.corporation_id):
			out[e.corporation_id] = []
		out[e.corporation_id].append(e)
	for c in out:
		(out[c] as Array).sort_custom(func(a: EnemyData, b: EnemyData) -> bool:
			var ka: int = PortraitArt.enemy_data_subject(a)["kind"]
			var kb: int = PortraitArt.enemy_data_subject(b)["kind"]
			return ka < kb if ka != kb else String(a.id) < String(b.id))
	return out


func _ready() -> void:
	var out_dir := "user://"
	var sheet := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.trim_prefix("--out=")
		if a.begins_with("--sheet="):
			sheet = a.trim_prefix("--sheet=")
	match sheet:
		"classes":
			await _save(_classes_sheet(), out_dir.path_join("classes.png"))
		"enemies":
			await _save(_enemies_sheet(), out_dir.path_join("enemies.png"))
		"boss":
			await _save(_boss_sheet(), out_dir.path_join("boss_hologram.png"))
			await _save(_bosses_sheet(), out_dir.path_join("bosses.png"))
		"intro":
			await _save(_intro_sheet(), out_dir.path_join("boss_intro_strip.png"))
		_:
			await _style_sheets(out_dir)
	print("PORTRAITS SAVED ", out_dir)
	get_tree().quit()


func _style_sheets(out_dir: String) -> void:
	var subs := subjects()
	var groups := ["OPERATIVES", "ENEMIES", "BOSSES", "CORPORATIONS"]
	var cols := 8
	var w := int(GAP + cols * (CELL + GAP)) + 140
	var h := int(60 + groups.size() * (CELL + 60 + GAP))
	for st in PortraitArt.STYLE_NAMES.size():
		var art := Control.new()
		art.size = Vector2(w, h)
		var style := st
		art.draw.connect(func() -> void: _draw_sheet(art, style, subs, groups, cols))
		await _save(art, out_dir.path_join("portraits_%d.png" % st))


## Renders `art` (a Control sized to the sheet) in its own viewport and saves it.
func _save(art: Control, path: String) -> void:
	var vp := SubViewport.new()
	vp.size = Vector2i(art.size)
	vp.transparent_bg = false
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(vp)
	vp.add_child(art)
	for i in 4:
		await get_tree().process_frame
	await RenderingServer.frame_post_draw
	vp.get_texture().get_image().save_png(path)
	vp.queue_free()


func _draw_sheet(art: Control, st: int, subs: Array[Dictionary], groups: Array, cols: int) -> void:
	art.draw_rect(Rect2(Vector2.ZERO, art.size), W5_BACK)
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


# --- W5 sheets ---------------------------------------------------------------------------------

## One Polaroid-framed portrait at `at` in `style`, captioned.
static func _polaroid(art: Control, at: Vector2, subj: Dictionary, style: int, caption: String) -> void:
	var frame := Rect2(at, Vector2(W5_CELL, W5_CELL + W5_BAND))
	art.draw_rect(frame, Palette.PAPER)
	PortraitArt.style = style
	PortraitArt.draw(art, Rect2(at + Vector2(6, 6), Vector2(W5_CELL - 12, W5_CELL - 12)), subj)
	PortraitArt.style = 0
	art.draw_string(Palette.mono(), at + Vector2(6, W5_CELL + W5_BAND - 7), caption, HORIZONTAL_ALIGNMENT_LEFT, W5_CELL - 12, W5_TEXT, Palette.INK)


func _classes_sheet() -> Control:
	var rows: Array = []
	for e in PortraitArt.EXPRESSION_NAMES.size():
		rows.append(["NEON " + PortraitArt.EXPRESSION_NAMES[e], 0, e, &""])
	for st in range(1, PortraitArt.STYLE_NAMES.size()):
		rows.append([PortraitArt.STYLE_NAMES[st], st, PortraitArt.Expr.NEUTRAL, &""])
	for k in 2:
		rows.append(["NEON op_%d" % (k + 3), 0, PortraitArt.Expr.NEUTRAL, StringName("op_%d" % (k + 3))])
	var step := W5_CELL + GAP
	var art := Control.new()
	art.size = Vector2(W5_LEFT + PortraitArt.CLASS_IDS.size() * step + GAP, 70 + rows.size() * (W5_CELL + W5_BAND + GAP))
	art.draw.connect(func() -> void:
		art.draw_rect(Rect2(Vector2.ZERO, art.size), W5_BACK)
		art.draw_string(Palette.display(), Vector2(GAP, 38), "W5 CLASSES // 8 SILHOUETTES x 4 EXPRESSIONS + LOOKS + VARIATION", HORIZONTAL_ALIGNMENT_LEFT, -1, W5_TITLE, Palette.CELL_ACID)
		for i in PortraitArt.CLASS_IDS.size():
			var c: StringName = PortraitArt.CLASS_IDS[i]
			art.draw_string(Palette.mono(), Vector2(W5_LEFT + i * step, 62), String(c).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, W5_CELL, W5_TEXT, Palette.class_accent(c))
		for ri in rows.size():
			var row: Array = rows[ri]
			var y := 70.0 + ri * (W5_CELL + W5_BAND + GAP)
			art.draw_string(Palette.mono(), Vector2(GAP, y + W5_CELL * 0.5), row[0], HORIZONTAL_ALIGNMENT_LEFT, W5_LEFT - GAP, W5_TEXT, Palette.TEXT_HI)
			for i in PortraitArt.CLASS_IDS.size():
				var c: StringName = PortraitArt.CLASS_IDS[i]
				var subj := PortraitArt.operative_subject(c, row[3], String(c).capitalize(), row[2])
				_polaroid(art, Vector2(W5_LEFT + i * step, y), subj, row[1], String(c).capitalize()))
	return art


func _enemies_sheet() -> Control:
	var by_corp := enemies_by_corp()
	var corps := [&"solace", &"meridian", &"halcyon", &"orbital", &"rebel_cell"]
	var cols := 8
	var holo_cols := 2
	var step := W5_CELL + GAP
	var art := Control.new()
	art.size = Vector2(W5_LEFT + (cols + holo_cols) * step + GAP * 2, 70 + corps.size() * (W5_CELL + W5_BAND + GAP))
	for ci in corps.size():
		var list: Array = by_corp.get(corps[ci], [])
		var y := 70.0 + ci * (W5_CELL + W5_BAND + GAP)
		# Hologram busts: the first machine and the first agent (or boss) of the corp.
		var picks: Array = []
		for kind in [PortraitArt.Kind.MACHINE, PortraitArt.Kind.AGENT, PortraitArt.Kind.BOSS]:
			for e in list:
				if PortraitArt.enemy_data_subject(e)["kind"] == kind and picks.size() < holo_cols:
					picks.append(e)
					break
		for k in picks.size():
			var h := Hologram.for_enemy(picks[k])
			h.mode = Hologram.Mode.BUST
			h.dim = 1.0
			h.position = Vector2(W5_LEFT + cols * step + GAP + k * step, y)
			h.size = Vector2(W5_CELL, W5_CELL)
			art.add_child(h)
	art.draw.connect(func() -> void:
		art.draw_rect(Rect2(Vector2.ZERO, art.size), W5_BACK)
		art.draw_string(Palette.display(), Vector2(GAP, 38), "W5 ENEMIES // CORP HUE + PATTERN (BUSTS, THEN HOLOGRAM BUSTS)", HORIZONTAL_ALIGNMENT_LEFT, -1, W5_TITLE, Palette.CELL_ACID)
		for ci in corps.size():
			var list: Array = by_corp.get(corps[ci], [])
			var y := 70.0 + ci * (W5_CELL + W5_BAND + GAP)
			art.draw_string(Palette.mono(), Vector2(GAP, y + W5_CELL * 0.5), String(corps[ci]).to_upper(), HORIZONTAL_ALIGNMENT_LEFT, W5_LEFT - GAP, W5_TEXT, Palette.corp_color(corps[ci]))
			var shown: Array = []
			for kind in [PortraitArt.Kind.AGENT, PortraitArt.Kind.MACHINE, PortraitArt.Kind.BOSS]:
				var n := 0
				for e in list:
					if PortraitArt.enemy_data_subject(e)["kind"] == kind and n < (3 if kind != PortraitArt.Kind.BOSS else 2):
						shown.append(e)
						n += 1
			for i in mini(cols, shown.size()):
				var e: EnemyData = shown[i]
				_polaroid(art, Vector2(W5_LEFT + i * step, y), PortraitArt.enemy_data_subject(e), 0, e.display_name))
	return art


func _boss_sheet() -> Control:
	var art := Control.new()
	art.size = Vector2(1280, 720)
	var boss := Hologram.new(PortraitArt.enemy_subject(&"the_manifest", "The Manifest", &"meridian", true), Hologram.Mode.BOSS)
	boss.size = Hologram.boss_size(art.size.y)
	boss.position = WHEEL_AT - Vector2(boss.size.x * 0.5, boss.size.y + WHEEL_R * 0.35)
	art.add_child(boss)
	var wheel := Control.new()
	wheel.size = art.size
	wheel.draw.connect(func() -> void: _stand_in_wheel(wheel))
	art.add_child(wheel)
	art.draw.connect(func() -> void:
		art.draw_rect(Rect2(Vector2.ZERO, art.size), W5_BACK)
		art.draw_string(Palette.display(), Vector2(40, 60), "BOSS HOLOGRAM // 40% HEIGHT, DIMMED BEHIND ITS WHEEL", HORIZONTAL_ALIGNMENT_LEFT, -1, W5_TITLE, Palette.CELL_ACID)
		art.draw_string(Palette.mono(), Vector2(40, 96), "the wheel is a stand-in; W3 places the hologram so it never covers slice values", HORIZONTAL_ALIGNMENT_LEFT, -1, W5_TEXT, Palette.TEXT_MID))
	return art


## A stand-in boss wheel (slices, values, hub) so the sheet shows readability over the
## hologram; the real wheel is W3's.
func _stand_in_wheel(ci: Control) -> void:
	var types := [RC.SliceType.ATTACK, RC.SliceType.DEFEND, RC.SliceType.CRIT, RC.SliceType.ATTACK, RC.SliceType.MISS, RC.SliceType.SHIELD]
	var values := ["14", "12", "24", "14", "", "8"]
	for k in WHEEL_SLICES:
		var a0 := -PI * 0.5 + TAU * k / WHEEL_SLICES
		var a1 := a0 + TAU / WHEEL_SLICES
		var pts := PackedVector2Array([WHEEL_AT])
		for q in 13:
			var a := lerpf(a0, a1, q / 12.0)
			pts.append(WHEEL_AT + Vector2(cos(a), sin(a)) * WHEEL_R)
		ci.draw_colored_polygon(pts, Color(Palette.slice_color(types[k]), 0.75))
		var mid := (a0 + a1) * 0.5
		ci.draw_string(Palette.display(), WHEEL_AT + Vector2(cos(mid), sin(mid)) * (WHEEL_R + 26) + Vector2(-24, 12), values[k], HORIZONTAL_ALIGNMENT_CENTER, 48, UiTheme.HEADING, Palette.TEXT_HI)
	ci.draw_circle(WHEEL_AT, WHEEL_R * 0.55, Palette.NIGHT_SKY)
	ci.draw_arc(WHEEL_AT, WHEEL_R, 0, TAU, 64, Palette.CORP_MERIDIAN, 6.0, true)
	CorpPattern.dashed_line(ci, WHEEL_AT + Vector2(-WHEEL_R, WHEEL_R + 30), WHEEL_AT + Vector2(WHEEL_R, WHEEL_R + 30), CorpPattern.Kind.CONTAINER_STRIPES, Palette.CORP_MERIDIAN, 3.0)
	ci.draw_string(Palette.display(), WHEEL_AT + Vector2(-80, 10), "THE MANIFEST", HORIZONTAL_ALIGNMENT_CENTER, 160, UiTheme.LABEL, Palette.CORP_MERIDIAN)


func _bosses_sheet() -> Control:
	var bosses: Array = []
	for list in enemies_by_corp().values():
		for e in list:
			if (e as EnemyData).is_boss:
				bosses.append(e)
	var side := 230.0
	var art := Control.new()
	art.size = Vector2(GAP + bosses.size() * (side + GAP), 80 + (side + 40) * 2)
	for i in bosses.size():
		for row in 2:
			var h := Hologram.for_enemy(bosses[i])
			h.dim = 1.0 if row == 0 else Hologram.BOSS_DIM
			h.position = Vector2(GAP + i * (side + GAP), 80 + row * (side + 40))
			h.custom_minimum_size = Vector2.ZERO
			h.size = Vector2(side, side)
			art.add_child(h)
	art.draw.connect(func() -> void:
		art.draw_rect(Rect2(Vector2.ZERO, art.size), W5_BACK)
		art.draw_string(Palette.display(), Vector2(GAP, 40), "BOSSES // FULL (TOP) AND AS DIMMED BEHIND THEIR WHEEL (BOTTOM)", HORIZONTAL_ALIGNMENT_LEFT, -1, W5_TITLE, Palette.CELL_ACID)
		for i in bosses.size():
			var e: EnemyData = bosses[i]
			art.draw_string(Palette.mono(), Vector2(GAP + i * (side + GAP), 72), "%s (%s)" % [e.display_name, e.corporation_id], HORIZONTAL_ALIGNMENT_LEFT, side, W5_TEXT, Palette.corp_color(e.corporation_id)))
	return art


func _intro_sheet() -> Control:
	var total := INTRO_FRAMES + FADE_FRAMES
	var art := Control.new()
	art.size = Vector2(GAP + total * (STRIP_CELL + GAP), STRIP_CELL + 110)
	var subj := PortraitArt.enemy_subject(&"civic_core", "The Civic Core", &"halcyon", true)
	for i in total:
		var h := Hologram.new(subj, Hologram.Mode.BOSS)
		h.dim = 1.0
		h.custom_minimum_size = Vector2.ZERO
		h.size = Vector2(STRIP_CELL, STRIP_CELL)
		h.position = Vector2(GAP + i * (STRIP_CELL + GAP), 80)
		if i < INTRO_FRAMES:
			h.reveal = float(i) / (INTRO_FRAMES - 1)
		else:
			h.modulate.a = float(i - INTRO_FRAMES + 1) / FADE_FRAMES
		art.add_child(h)
	art.draw.connect(func() -> void:
		art.draw_rect(Rect2(Vector2.ZERO, art.size), W5_BACK)
		art.draw_string(Palette.display(), Vector2(GAP, 40), "BOSS INTRO // T4 REVEAL (hologram_intro), THEN THE REDUCE-EFFECTS CROSS-FADE", HORIZONTAL_ALIGNMENT_LEFT, -1, W5_TITLE, Palette.CELL_ACID)
		for i in total:
			var label := "reveal %.1f" % (float(i) / (INTRO_FRAMES - 1)) if i < INTRO_FRAMES else "RE fade %.2f" % (float(i - INTRO_FRAMES + 1) / FADE_FRAMES)
			art.draw_string(Palette.mono(), Vector2(GAP + i * (STRIP_CELL + GAP), 72), label, HORIZONTAL_ALIGNMENT_LEFT, STRIP_CELL, W5_TEXT, Palette.TEXT_MID))
	return art
