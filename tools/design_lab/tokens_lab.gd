extends Control
## Design lab (not part of the game): the ART_BIBLE §3-§5 token sheet. Every Palette colour
## token as a labelled swatch, the five corps with their CorpPattern fills and threat
## lines, the §7.1 class accents, the HP and Heat scales, the §4.2 type scale at text
## scale 1.0 / 1.6 / 2.0 in every face, an MSDF-vs-raster outline check, and the §5.1
## spacing tokens. The sheet renders in a SubViewport at reference pixels (1:1).
##
## View: python tools/run_windowed.py --log lab.log -- res://tools/design_lab/tokens_lab.tscn
## Save a PNG and quit: add `-- --out=C:/path/tokens.png` (the review sheet in
## docs/art_review/W1/tokens.png).

const SHEET := Vector2i(1640, 3340)
const MARGIN := 32.0
const SWATCH := Vector2(148, 52)
const SWATCH_GAP := Vector2(12, 40)
const SECTION_GAP := 36.0
const TEXT_SCALES: Array[float] = [1.0, 1.6, 2.0]
## Frames to wait before saving (the SubViewport draws on the next frame).
const SAVE_AFTER_FRAMES := 4

const BRAND := [
	["CELL_PINK", Palette.CELL_PINK], ["CELL_ACID", Palette.CELL_ACID], ["CELL_TURF", Palette.CELL_TURF],
	["PAPER", Palette.PAPER], ["PAPER_ALT", Palette.PAPER_ALT], ["NOTE_PAPER", Palette.NOTE_PAPER],
	["NOTE_PINK", Palette.NOTE_PINK], ["NOTE_YELLOW", Palette.NOTE_YELLOW], ["STICKER_PINK", Palette.STICKER_PINK],
	["INK", Palette.INK], ["NET_CYAN", Palette.NET_CYAN], ["NEON_VIOLET", Palette.NEON_VIOLET],
	["CRT_AMBER", Palette.CRT_AMBER], ["RESIST_GOLD", Palette.RESIST_GOLD], ["DESK_DARK", Palette.DESK_DARK],
	["DESK_METAL", Palette.DESK_METAL], ["TERMINAL_BG", Palette.TERMINAL_BG], ["TERMINAL_BG_HOT", Palette.TERMINAL_BG_HOT],
	["TERMINAL_EDGE", Palette.TERMINAL_EDGE], ["TERMINAL_TEXT", Palette.TERMINAL_TEXT], ["NIGHT_SKY", Palette.NIGHT_SKY],
	["NIGHT_BLOCK", Palette.NIGHT_BLOCK], ["NIGHT_BLOCK_LIT", Palette.NIGHT_BLOCK_LIT], ["NIGHT_STREET", Palette.NIGHT_STREET],
	["NET_BG_INNER", Palette.NET_BG_INNER], ["NET_BG_OUTER", Palette.NET_BG_OUTER], ["TAPE", Palette.TAPE],
	["NOTE_TAPE", Palette.NOTE_TAPE], ["SHADOW", Palette.SHADOW],
]
const SEMANTIC := [
	["HARM", Palette.HARM], ["GAIN", Palette.GAIN], ["PROTECT", Palette.PROTECT], ["WARN", Palette.WARN],
	["FOCUS", Palette.FOCUS], ["DISABLED", Palette.DISABLED], ["TEXT_HI", Palette.TEXT_HI], ["TEXT_MID", Palette.TEXT_MID],
	["TEXT_LO", Palette.TEXT_LO], ["SCRIM", Palette.SCRIM], ["HEAT_FLAGGED", Palette.HEAT_FLAGGED],
]
const SLICES := [
	["ATTACK/CRIT", Palette.CELL_PINK], ["DEFEND/SHIELD", Palette.NET_CYAN], ["SLICE_HEAL", Palette.SLICE_HEAL],
	["SLICE_AFFLICT", Palette.SLICE_AFFLICT], ["SLICE_DEPLOY", Palette.SLICE_DEPLOY], ["SLICE_MISS", Palette.SLICE_MISS],
]
const CORPS := [
	[&"solace", "SOLACE", "CORP_SOLACE"], [&"meridian", "MERIDIAN", "CORP_MERIDIAN"], [&"halcyon", "HALCYON", "CORP_HALCYON"],
	[&"orbital", "ORBITAL", "CORP_ORBITAL"], [&"rebel_cell", "REBEL_CELL", "CORP_REBEL_CELL"],
]
const CLASSES := [&"breaker", &"wrecker", &"ghost", &"phantom", &"rigger", &"overclocker", &"botnet", &"hivemind"]
const STEP_NAMES := {
	UiTheme.CAPTION: "CAPTION", UiTheme.BODY: "BODY", UiTheme.LABEL: "LABEL", UiTheme.TITLE: "TITLE",
	UiTheme.HEADING: "HEADING", UiTheme.DISPLAY: "DISPLAY", UiTheme.HERO: "HERO",
}
const SPACING_NAMES := [
	["SP_XS", UiTheme.SP_XS], ["SP_S", UiTheme.SP_S], ["SP_M", UiTheme.SP_M], ["SP_L", UiTheme.SP_L],
	["SP_XL", UiTheme.SP_XL], ["SP_XXL", UiTheme.SP_XXL], ["SAFE_MARGIN", UiTheme.SAFE_MARGIN],
	["PANEL_PAD_H", UiTheme.PANEL_PAD_H], ["PANEL_PAD_V", UiTheme.PANEL_PAD_V], ["GUTTER", UiTheme.GUTTER],
]

var viewport: SubViewport
var sheet: Control
var _raster: Dictionary = {}


func _ready() -> void:
	UiTheme.apply(self)
	viewport = SubViewport.new()
	viewport.size = SHEET
	viewport.transparent_bg = false
	viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	add_child(viewport)
	sheet = Control.new()
	sheet.size = Vector2(SHEET)
	sheet.draw.connect(_draw_sheet.bind(sheet))
	viewport.add_child(sheet)
	var scroll := ScrollContainer.new()
	scroll.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(scroll)
	var view := TextureRect.new()
	view.texture = viewport.get_texture()
	scroll.add_child(view)
	var out := ""
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out = a.trim_prefix("--out=")
	if out != "":
		for i in SAVE_AFTER_FRAMES:
			await RenderingServer.frame_post_draw
		var err := viewport.get_texture().get_image().save_png(out)
		print("tokens_lab: saved %s (%s)" % [out, error_string(err)])
		get_tree().quit(0 if err == OK else 1)


## A raster (non-MSDF) copy of a face, built from its bytes (the loaded font is untouched).
func raster(path: String) -> Font:
	if not _raster.has(path):
		var src := load(path) as FontFile
		var f := FontFile.new()
		f.data = src.data
		f.multichannel_signed_distance_field = false
		_raster[path] = f
	return _raster[path]


func _draw_sheet(ci: Control) -> void:
	ci.draw_rect(Rect2(Vector2.ZERO, Vector2(SHEET)), Palette.NIGHT_SKY)
	var y := MARGIN
	y = _title(ci, y, "REBEL_CELL TOKENS  //  ART_BIBLE §3-§5  (W1)", "reference px, 1:1")
	y = _swatches(ci, y, "§3.2 BRAND AND NEUTRAL", BRAND)
	y = _swatches(ci, y, "§3.3 SEMANTIC", SEMANTIC)
	y = _swatches(ci, y, "§3.4 SLICES", SLICES)
	y = _corps(ci, y)
	y = _classes(ci, y)
	y = _scales(ci, y)
	y = _type_scale(ci, y)
	y = _msdf_check(ci, y)
	y = _spacing(ci, y)


func _caption(ci: CanvasItem, at: Vector2, text: String, col: Color = Palette.TEXT_MID, px: int = UiTheme.CAPTION) -> void:
	ci.draw_string(Palette.mono(), at, text, HORIZONTAL_ALIGNMENT_LEFT, -1, px, col)


func _title(ci: CanvasItem, y: float, text: String, note: String) -> float:
	ci.draw_string(Palette.display(), Vector2(MARGIN, y + UiTheme.HEADING), text, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.HEADING, Palette.TEXT_HI)
	_caption(ci, Vector2(MARGIN, y + UiTheme.HEADING + 22), note)
	return y + UiTheme.HEADING + 22 + SECTION_GAP


func _heading(ci: CanvasItem, y: float, text: String) -> float:
	ci.draw_string(Palette.mono(), Vector2(MARGIN, y + UiTheme.TITLE), text, HORIZONTAL_ALIGNMENT_LEFT, -1, UiTheme.TITLE, Palette.CELL_ACID)
	ci.draw_line(Vector2(MARGIN, y + UiTheme.TITLE + 8), Vector2(SHEET.x - MARGIN, y + UiTheme.TITLE + 8), Palette.CELL_PINK, 1.0)
	return y + UiTheme.TITLE + 22


func _checker(ci: CanvasItem, r: Rect2) -> void:
	var cell := 8.0
	var yy := r.position.y
	var row := 0
	while yy < r.end.y:
		var xx := r.position.x
		var col := row
		while xx < r.end.x:
			var c := Color(0.8, 0.8, 0.8) if col % 2 == 0 else Color(0.35, 0.35, 0.35)
			ci.draw_rect(Rect2(Vector2(xx, yy), Vector2(minf(cell, r.end.x - xx), minf(cell, r.end.y - yy))), c)
			xx += cell
			col += 1
		yy += cell
		row += 1


func _swatch(ci: CanvasItem, at: Vector2, name: String, col: Color) -> void:
	var r := Rect2(at, SWATCH)
	if col.a < 1.0:
		_checker(ci, r)
	ci.draw_rect(r, col)
	ci.draw_rect(r, Color(Palette.TEXT_LO, 0.6), false, 1.0)
	var opaque := Palette.over(Palette.NIGHT_SKY, col)
	var ink := Palette.INK if Palette.contrast(Palette.INK, opaque) > Palette.contrast(Palette.TEXT_HI, opaque) else Palette.TEXT_HI
	_caption(ci, at + Vector2(6, SWATCH.y - 8), "#" + col.to_html(col.a < 1.0).to_upper(), ink)
	_caption(ci, at + Vector2(0, SWATCH.y + 16), name, Palette.TEXT_HI)


func _swatches(ci: CanvasItem, y: float, heading: String, items: Array) -> float:
	y = _heading(ci, y, heading)
	var per_row := int((SHEET.x - MARGIN * 2 + SWATCH_GAP.x) / (SWATCH.x + SWATCH_GAP.x))
	for i in items.size():
		var at := Vector2(MARGIN + (i % per_row) * (SWATCH.x + SWATCH_GAP.x), y + (i / per_row) * (SWATCH.y + SWATCH_GAP.y))
		_swatch(ci, at, items[i][0], items[i][1])
	var rows := ceili(items.size() / float(per_row))
	return y + rows * (SWATCH.y + SWATCH_GAP.y) + SECTION_GAP * 0.5


func _corps(ci: CanvasItem, y: float) -> float:
	y = _heading(ci, y, "§3.6 CORPORATIONS  //  hue + pattern (CorpPattern) + threat line")
	var w := (SHEET.x - MARGIN * 2 - 4 * UiTheme.GUTTER) / 5.0
	for i in CORPS.size():
		var id: StringName = CORPS[i][0]
		var col := Palette.corp_color(id)
		var kind := Palette.corp_pattern_id(id)
		var x := MARGIN + i * (w + UiTheme.GUTTER)
		ci.draw_rect(Rect2(x, y, w, 26), col)
		_caption(ci, Vector2(x + 6, y + 18), "%s  #%s" % [CORPS[i][1], col.to_html(false).to_upper()], Palette.INK)
		var box := Rect2(x, y + 34, w, 110)
		ci.draw_rect(box, Palette.NIGHT_BLOCK)
		CorpPattern.fill_rect(ci, box, kind, col)
		ci.draw_rect(box, Color(col, 0.8), false, 1.0)
		var c := Vector2(x + w * 0.3, y + 34 + 110 + 70)
		ci.draw_circle(c, 58, Palette.NIGHT_BLOCK)
		CorpPattern.fill_ring(ci, c, 38, 58, kind, col)
		ci.draw_arc(c, 58, 0, TAU, 48, col, 1.5, true)
		ci.draw_arc(c, 38, 0, TAU, 48, col, 1.5, true)
		var tri := PackedVector2Array([Vector2(x + w * 0.62, y + 160), Vector2(x + w - 4, y + 190), Vector2(x + w * 0.66, y + 250)])
		ci.draw_colored_polygon(tri, Palette.NIGHT_BLOCK)
		CorpPattern.fill_polygon(ci, tri, kind, col)
		CorpPattern.dashed_line(ci, Vector2(x, y + 290), Vector2(x + w, y + 290), kind, col, 2.5)
		_caption(ci, Vector2(x, y + 312), CorpPattern.KIND_NAMES[kind] + " : " + CORPS[i][2])
	return y + 330 + SECTION_GAP * 0.5


func _classes(ci: CanvasItem, y: float) -> float:
	y = _heading(ci, y, "§7.1 CLASS ACCENTS  //  Palette.class_accent(id)")
	var items := []
	for id in CLASSES:
		items.append([String(id).to_upper(), Palette.class_accent(id)])
	for i in items.size():
		_swatch(ci, Vector2(MARGIN + i * (SWATCH.x + SWATCH_GAP.x), y), items[i][0], items[i][1])
	return y + SWATCH.y + SWATCH_GAP.y + SECTION_GAP * 0.5


func _scales(ci: CanvasItem, y: float) -> float:
	y = _heading(ci, y, "§3.5 HP (hp_color) AND HEAT (heat_color, config MAJOR levels)")
	var w := SHEET.x - MARGIN * 2 - 120
	_caption(ci, Vector2(MARGIN, y + 22), "HP %", Palette.TEXT_HI, UiTheme.BODY)
	for i in 100:
		var frac := (i + 0.5) / 100.0
		ci.draw_rect(Rect2(MARGIN + 120 + w * i / 100.0, y, w / 100.0 + 0.5, 30), Palette.hp_color(frac))
	for mark in [0.25, 0.5]:
		ci.draw_line(Vector2(MARGIN + 120 + w * mark, y - 4), Vector2(MARGIN + 120 + w * mark, y + 34), Palette.TEXT_HI, 2.0)
		_caption(ci, Vector2(MARGIN + 120 + w * mark + 4, y + 48), "%d%%" % roundi(mark * 100), Palette.TEXT_HI)
	y += 64
	_caption(ci, Vector2(MARGIN, y + 22), "HEAT", Palette.TEXT_HI, UiTheme.BODY)
	var cfg := load(ContentRegistry.CONFIG_PATH) as CampaignConfigData
	var heat_max := cfg.heat_max
	for h in heat_max + 1:
		ci.draw_rect(Rect2(MARGIN + 120 + w * h / float(heat_max + 1), y, w / float(heat_max + 1) + 0.5, 30), Palette.heat_color(h))
	var names := ["COOL", "NOTICED", "FLAGGED", "HUNTED"]
	var levels := cfg.major_heat_levels()
	_caption(ci, Vector2(MARGIN + 124, y + 48), names[0], Palette.TEXT_HI)
	for i in levels.size():
		var x := MARGIN + 120 + w * levels[i] / float(heat_max + 1)
		ci.draw_line(Vector2(x, y - 4), Vector2(x, y + 34), Palette.TEXT_HI, 2.0)
		_caption(ci, Vector2(x + 4, y + 48), "%s %d+" % [names[mini(i + 1, 3)], levels[i]], Palette.TEXT_HI)
	return y + 64 + SECTION_GAP * 0.5


func _type_scale(ci: CanvasItem, y: float) -> float:
	y = _heading(ci, y, "§4.2 TYPE SCALE  //  UiTheme.font_px_at(step, scale) in every face (MSDF)")
	var faces := [["ANTON", Palette.display(), true], ["MARKER", Palette.marker(), true], ["MONO", Palette.mono(), false],
		["PLEX", Palette.body(), false], ["PLEX MED", Palette.body_medium(), false]]
	var col_x := [MARGIN + 170.0, MARGIN + 450.0, MARGIN + 730.0, MARGIN + 1010.0, MARGIN + 1290.0]
	for s in TEXT_SCALES:
		_caption(ci, Vector2(MARGIN, y + 16), "TEXT SCALE %.1f" % s, Palette.CELL_ACID, UiTheme.BODY)
		for f in faces.size():
			_caption(ci, Vector2(col_x[f], y + 16), faces[f][0])
		y += 26
		for step in UiTheme.STEPS:
			var px := UiTheme.font_px_at(step, s)
			var line := px * UiTheme.line_height(step)
			_caption(ci, Vector2(MARGIN, y + line * 0.75), "%s %d -> %dpx" % [STEP_NAMES[step], step, px])
			for f in faces.size():
				var sample := "AG" if faces[f][2] else "Ag"
				ci.draw_string(faces[f][1], Vector2(col_x[f], y + line * 0.8), sample, HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.TEXT_HI)
			y += line
		y += 12
	return y + SECTION_GAP * 0.5


func _msdf_check(ci: CanvasItem, y: float) -> float:
	y = _heading(ci, y, "§4.1/§13 MSDF CHECK  //  outline 6 and 8 px: MSDF (left) vs raster copy (right)")
	var faces := [["ANTON", Palette.FONT_DISPLAY], ["MARKER", Palette.FONT_MARKER], ["MONO", Palette.FONT_MONO], ["PLEX", Palette.FONT_BODY]]
	for f in faces.size():
		var x := MARGIN + f * 400.0
		_caption(ci, Vector2(x, y + 12), faces[f][0])
		var k := 0
		for px in [UiTheme.BODY, UiTheme.HEADING]:
			for outline in [6, 8]:
				var at := Vector2(x, y + 44 + k * 44)
				var msdf := load(faces[f][1]) as Font
				ci.draw_string_outline(msdf, at, "-12 OK", HORIZONTAL_ALIGNMENT_LEFT, -1, px, outline, Palette.CELL_PINK)
				ci.draw_string(msdf, at, "-12 OK", HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.INK)
				var r := raster(faces[f][1])
				ci.draw_string_outline(r, at + Vector2(170, 0), "-12 OK", HORIZONTAL_ALIGNMENT_LEFT, -1, px, outline, Palette.CELL_PINK)
				ci.draw_string(r, at + Vector2(170, 0), "-12 OK", HORIZONTAL_ALIGNMENT_LEFT, -1, px, Palette.INK)
				_caption(ci, at + Vector2(310, 0), "%dpx o%d" % [px, outline])
				k += 1
	return y + 44 + 4 * 44 + SECTION_GAP * 0.5


func _spacing(ci: CanvasItem, y: float) -> float:
	y = _heading(ci, y, "§5.1 SPACING (4 px grid)")
	var x := MARGIN
	for item in SPACING_NAMES:
		var v: int = item[1]
		ci.draw_rect(Rect2(x, y, v, 48), Palette.NET_CYAN)
		_caption(ci, Vector2(x, y + 66), "%s" % item[0], Palette.TEXT_HI)
		_caption(ci, Vector2(x, y + 82), "%d" % v)
		x += maxf(v, 96) + UiTheme.SP_M
	return y + 90 + SECTION_GAP * 0.5
