extends Control
## Design lab (ART-1 1C): every glyph of the atlas through the glyph shader, at 64 / 32 / 16 px
## (pages "1.0") and at text scale 2.0 (16 and 32 px doubled, pages "2.0"), on a dark and a mid
## plate so the #0C0A16 outline reads. Compare with docs/art_reference/wheel/round34_slice_names/
## glyph_set_v3.jpg. The page turns every PAGE_FRAMES frames, so one Movie Maker run captures them all:
##   python tools/run_windowed.py --log <log> -- res://tools/design_lab/glyph_sheet.tscn \
##       --write-movie <dir>/f.png --fixed-fps 10 --quit-after 24
## `-- --page=N` holds page N.

const PAGE_FRAMES := 2
const SIZES_1 := [64.0, 32.0, 16.0]
const SIZES_2 := [16.0, 32.0]
const TEXT_SCALE := 2.0
const MARGIN := Vector2(16, 44)
const GAP := 6.0
const LABEL_PX := 11

var _pages: Array[Dictionary] = []
var _page := -1
var _hold := -1
var _frames := 0
var _body: Control


func _ready() -> void:
	UiTheme.apply(self)
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--page="):
			_hold = int(a.get_slice("=", 1))
	var bg := ColorRect.new()
	bg.color = Palette.NET_BG_OUTER
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(bg)
	_body = Control.new()
	_body.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(_body)
	_plan()
	_show(maxi(_hold, 0))


## Splits the atlas into pages for each scale.
func _plan() -> void:
	var names := GlyphIcon.table().glyph_names
	for spec in [[1.0, SIZES_1], [TEXT_SCALE, SIZES_2]]:
		var tile := _tile_size(spec[0], spec[1])
		var vp := get_viewport_rect().size
		var cols := maxi(1, int((vp.x - MARGIN.x * 2.0) / tile.x))
		var rows := maxi(1, int((vp.y - MARGIN.y - 8.0) / tile.y))
		var per := cols * rows
		var i := 0
		while i < names.size():
			_pages.append({"scale": spec[0], "sizes": spec[1], "from": i, "to": mini(i + per, names.size()), "cols": cols, "tile": tile})
			i += per


func _tile_size(scale: float, sizes: Array) -> Vector2:
	var w := 0.0
	var h := 0.0
	for s in sizes:
		var c := GlyphIcon.cell_size_for(float(s) * scale)
		w += c.x + GAP
		h = maxf(h, c.y)
	return Vector2(maxf(w, 120.0), h + LABEL_PX + 10.0)


func _show(p: int) -> void:
	_page = clampi(p, 0, _pages.size() - 1)
	for c in _body.get_children():
		c.queue_free()
	var pg: Dictionary = _pages[_page]
	var t := GlyphIcon.table()
	var title := Label.new()
	title.text = "GLYPH ATLAS  //  page %d / %d  //  text scale %.1f  //  sizes %s px  //  %d glyphs, 128 px SDF cells" % [
		_page + 1, _pages.size(), pg["scale"], str(pg["sizes"]), t.glyph_names.size()]
	title.position = Vector2(MARGIN.x, 10)
	title.add_theme_color_override(&"font_color", Palette.TEXT_HI)
	title.add_theme_font_size_override(&"font_size", 15)
	_body.add_child(title)
	var tile: Vector2 = pg["tile"]
	for i in range(int(pg["from"]), int(pg["to"])):
		var k := i - int(pg["from"])
		var at := MARGIN + Vector2((k % int(pg["cols"])) * tile.x, (k / int(pg["cols"])) * tile.y)
		var plate := ColorRect.new()
		plate.color = Palette.DESK_METAL if (k % 2) == 0 else Palette.NIGHT_BLOCK
		plate.position = at
		plate.size = tile - Vector2(4, 4)
		_body.add_child(plate)
		var x := at.x + 2.0
		for s in pg["sizes"]:
			var g := GlyphIcon.make(StringName(t.glyph_names[i]), float(s) * float(pg["scale"]))
			g.position = Vector2(x, at.y + 1.0)
			_body.add_child(g)
			x += g.custom_minimum_size.x + GAP
		var l := Label.new()
		l.text = "%d %s" % [i, t.glyph_names[i]]
		l.position = Vector2(at.x + 3, at.y + tile.y - LABEL_PX - 12)
		l.add_theme_font_size_override(&"font_size", LABEL_PX)
		l.add_theme_color_override(&"font_color", Palette.TEXT_MID)
		_body.add_child(l)


func _process(_delta: float) -> void:
	if _hold >= 0:
		return
	_frames += 1
	if _frames % PAGE_FRAMES == 0 and _page + 1 < _pages.size():
		_show(_page + 1)
