class_name GlyphIcon
extends Control
## ART-1 1C: one glyph from the atlas (content/config/glyph_table.tres), drawn by the
## glyph shader (assets/glyphs/glyph_sdf.gdshader): white fill and the #0C0A16 outline from
## Palette, crisp from 16 px to 64 px and at text scale 2.0. `box_px` is the glyph's box on
## screen (bible 3.5 "px = box size"); the control is the whole cell, so the outline fits.
## View only: it never changes game state.

const SHADER_PATH := "res://assets/glyphs/glyph_sdf.gdshader"

## The atlas name to draw (GlyphTableData.glyph_names), e.g. &"slice_shim".
@export var glyph: StringName = &"":
	set(v):
		glyph = v
		queue_redraw()
## The glyph's box on screen (px).
@export var box_px: float = 32.0:
	set(v):
		box_px = v
		_fit()
## Fill colour (Palette token).
@export var fill: Color = Palette.GLYPH_FILL:
	set(v):
		fill = v
		_apply_material()
## Outline colour (Palette token).
@export var ink: Color = Palette.GLYPH_INK:
	set(v):
		ink = v
		_apply_material()

static var _table: GlyphTableData
static var _materials: Dictionary = {}


## The shipped glyph table, loaded once.
static func table() -> GlyphTableData:
	if _table == null:
		_table = GlyphTableData.shipped()
	return _table


## The glyph shader material for this fill and outline (shared per colour pair).
static func material_for(p_fill: Color, p_ink: Color) -> ShaderMaterial:
	var key := p_fill.to_html() + "|" + p_ink.to_html()
	if not _materials.has(key):
		var t := table()
		var m := ShaderMaterial.new()
		m.shader = load(SHADER_PATH)
		m.set_shader_parameter(&"fill_color", p_fill)
		m.set_shader_parameter(&"outline_color", p_ink)
		m.set_shader_parameter(&"outline_width", t.outline_width)
		m.set_shader_parameter(&"box_px", float(t.box_px))
		m.set_shader_parameter(&"spread_px", float(t.spread_px))
		_materials[key] = m
	return _materials[key]


## A GlyphIcon for atlas name `p_glyph` with a box of `p_box_px` on screen.
static func make(p_glyph: StringName, p_box_px: float) -> GlyphIcon:
	var g := GlyphIcon.new()
	g.glyph = p_glyph
	g.box_px = p_box_px
	return g


## The control size that holds a glyph box of `p_box_px` (the cell, with its margin).
static func cell_size_for(p_box_px: float) -> Vector2:
	var t := table()
	var s := p_box_px * float(t.cell_px) / float(t.box_px)
	return Vector2(s, s)


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	_fit()
	_apply_material()


func _notification(what: int) -> void:
	if what == NOTIFICATION_ENTER_TREE:
		size = custom_minimum_size


func _fit() -> void:
	custom_minimum_size = cell_size_for(box_px)
	if is_inside_tree():
		size = custom_minimum_size
	queue_redraw()


func _apply_material() -> void:
	material = material_for(fill, ink)
	queue_redraw()


func _draw() -> void:
	var t := table()
	var region := t.cell_region(glyph)
	if region.size == Vector2.ZERO or t.atlas == null:
		return
	var cell := cell_size_for(box_px)
	draw_texture_rect_region(t.atlas, Rect2((size - cell) * 0.5, cell), region)
