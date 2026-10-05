class_name WheelGlyphs
extends RefCounted
## The one place the wheel stack picks a glyph (ART-2 2A; ART_BIBLE v2 3.3-3.5, 3.10, 6.2), on 1C's
## production atlas (`content/config/glyph_table.tres`, `assets/glyphs/glyph_atlas.png`). The view
## draws many glyphs in one `_draw` (read blocks, badges, plates), so each atlas cell is decoded once
## from its distance field into a small coverage texture with the bible's ink outline baked in
## (fill at the 0.5 edge, outline 0.075 of the box: the same edges as `glyph_sdf.gdshader`), then
## drawn modulated by its fill colour. Corp crests are not in the atlas yet: they come from
## `assets/wheel/glyphs_interim/crest_<corp>.png` (round 15/18 recipes, `tools/art/bake_wheel_glyphs.py`).
## Ids are table keys (`type_shim`, `slice_<id>`, `status_<s>`, `hub_<core>`, `seg_<id>`) or `crest_<corp>`.

const INTERIM := "res://assets/wheel/glyphs_interim/%s.png"
## ART_BIBLE 3.5: the dark rounded outline is 0.075 of the glyph box.
const OUTLINE_SHARE := 0.075

static var _cache: Dictionary = {}
static var _table: GlyphTableData = null
static var _atlas: Image = null


## The table (1C's shipped one).
static func table() -> GlyphTableData:
	if _table == null:
		_table = GlyphTableData.shipped()
	return _table


## The outlined coverage texture for `id` (a table key or `crest_<corp>`), or null. Its box is
## `box_share()` of the texture (the margin holds the outline).
static func texture(id: StringName) -> Texture2D:
	if id == &"":
		return null
	if _cache.has(id):
		return _cache[id]
	var tex: Texture2D = null
	if String(id).begins_with("crest_"):
		var path := INTERIM % id
		tex = load(path) as Texture2D if ResourceLoader.exists(path) else null
	else:
		tex = _decode(table().glyph_for(id))
	_cache[id] = tex
	return tex


## The glyph box's share of a texture's side (1C: a 96 px box in a 128 px cell; the interim crests
## fill their texture).
static func box_share(id: StringName) -> float:
	if String(id).begins_with("crest_"):
		return 1.0
	var t := table()
	return float(t.box_px) / float(maxi(1, t.cell_px))


## Whether `id` has a glyph (the pending stand-in counts as none).
static func has(id: StringName) -> bool:
	return texture(id) != null


## The key of a slice's glyph: its own when special, else its type's.
static func slice_id(slice: SliceData) -> StringName:
	if slice == null:
		return GlyphTableData.key_for_slice_type(RC.SliceType.NULL)
	var own := StringName("slice_" + String(slice.id))
	return own if table().glyph_for(own) != &"" else GlyphTableData.key_for_slice_type(slice.slice_type)


## The key of a status's glyph (empty for NONE).
static func status_id(status: int) -> StringName:
	return GlyphTableData.key_for_status(status) if status != RC.Status.NONE else &""


## The key of a hub core's emblem (3.3).
static func hub_id(core_id: StringName) -> StringName:
	return StringName("hub_" + String(core_id)) if core_id != &"" else &""


## The key of an inner-ring segment's glyph.
static func segment_id(seg: StringName) -> StringName:
	return seg if String(seg).begins_with("seg_") else StringName("seg_" + String(seg))


## Draws glyph `id` centred at `at` with a `size` px box, its fill `fill` over the baked ink outline.
## Returns whether it drew.
static func draw(ci: CanvasItem, id: StringName, at: Vector2, size: float, fill: Color, _outline: Color = Palette.GLYPH_INK) -> bool:
	var tex := texture(id)
	if tex == null or size <= 0.0:
		return false
	var side := size / box_share(id)
	if String(id).begins_with("crest_"):
		# the interim crests have no outline baked in: a ring of ink copies under the fill
		var w := maxf(1.0, size * 0.075)
		for k in 8:
			var a := TAU * k / 8.0
			ci.draw_texture_rect(tex, Rect2(at - Vector2(side, side) * 0.5 + Vector2(cos(a), sin(a)) * w, Vector2(side, side)), false, Color(Palette.GLYPH_INK, fill.a))
	ci.draw_texture_rect(tex, Rect2(at - Vector2(side, side) * 0.5, Vector2(side, side)), false, fill)
	return true


## Decodes atlas cell `glyph` into white fill + GLYPH_INK outline (alpha = coverage).
static func _decode(glyph: StringName) -> Texture2D:
	var t := table()
	if glyph == &"" or glyph == GlyphTableData.PENDING:
		return null
	var region := t.cell_region(glyph)
	if not region.has_area() or t.atlas == null:
		return null
	if _atlas == null:
		_atlas = t.atlas.get_image()
		if _atlas == null:
			return null
		if _atlas.is_compressed():
			_atlas.decompress()
	var cell := _atlas.get_region(Rect2i(region))
	var n := cell.get_width()
	var out := Image.create(n, n, false, Image.FORMAT_RGBA8)
	var spread := float(t.spread_px)
	var edge := 0.5 - t.outline_width * t.box_px / (2.0 * spread)
	var aa := 0.75 / (2.0 * spread)
	var fill_c := Palette.GLYPH_FILL
	var ink := Palette.GLYPH_INK
	for y in n:
		for x in n:
			var v := cell.get_pixel(x, y).r
			var fill := smoothstep(0.5 - aa, 0.5 + aa, v)
			var outer := smoothstep(edge - aa, edge + aa, v)
			var c := ink.lerp(fill_c, fill)
			c.a = outer
			out.set_pixel(x, y, c)
	return ImageTexture.create_from_image(out)
