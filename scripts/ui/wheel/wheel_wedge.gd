class_name WheelWedge
extends ColorRect
## Round 45 (designer-approved 2026-10-13): the inner ring's ghost wedge, one quad per wheel over the disc and
## under the view's own drawing (read blocks, the notch tick, the word plate) and the firmware sockets,
## running `shaders/wheel/wheel_wedge.gdshader`. It covers the outer slice under the needle with the modifier
## its active ring segment puts there; on a blank segment (or a wheel without a ring) it hides. The view calls
## `show_mod()` / `hide_mod()` with what it shows; this node never reads game state.

const SHADER := preload("res://shaders/wheel/wheel_wedge.gdshader")

var mat: ShaderMaterial = null
## What the wedge shows now: the segment id (&"" = none), the slice's centre and half span (degrees).
var seg_id: StringName = &""
var a_mid: float = 0.0
var half_span: float = 0.0
## The disc whose screens' clock (`wheel_screen_loop`, 0 under reduce effects) drives PIERCE and CORRUPT.
var clock_source: WheelDisc = null


func _process(_delta: float) -> void:
	if clock_source == null or not visible:
		set_process(false)
		return
	mat.set_shader_parameter(&"time", clock_source.clock())


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	show_behind_parent = true
	color = Palette.AUTO
	mat = ShaderMaterial.new()
	mat.shader = SHADER
	material = mat
	visible = false
	_constants()


## Places the quad like the disc: on `center` (local to the parent) for a slice rim of `radius` px.
func place(center: Vector2, radius: float) -> void:
	var k := radius / WheelDisc.R_OUT
	var h := WheelDisc.EXT * k
	position = center - Vector2(h, h)
	size = Vector2(h, h) * 2.0
	pivot_offset = size * 0.5
	mat.set_shader_parameter(&"ext", WheelDisc.EXT)
	mat.set_shader_parameter(&"px", 1.0 / maxf(k, 0.001))


## Shows segment `p_seg`'s modifier on the slice centred at `mid` degrees, `half` degrees each side; a blank
## segment hides the wedge. `clock` drives PIERCE's stream and CORRUPT's re-roll (0 holds them: reduce effects).
func show_mod(p_seg: StringName, mid: float, half: float, clock: float) -> void:
	var m := RingMods.of(p_seg)
	if m.is_empty():
		hide_mod()
		return
	seg_id = p_seg
	a_mid = mid
	half_span = half
	visible = true
	mat.set_shader_parameter(&"mod", int(m["mod"]))
	mat.set_shader_parameter(&"tint", m["tint"])
	mat.set_shader_parameter(&"a_mid", mid)
	mat.set_shader_parameter(&"half_span", half)
	mat.set_shader_parameter(&"kind", int(m["kind"]))
	mat.set_shader_parameter(&"mark_size", float(m["size"]))
	mat.set_shader_parameter(&"mark_row", float(m["row"]))
	mat.set_shader_parameter(&"mark_arc", float(m["arc"]))
	mat.set_shader_parameter(&"keyline", RingMods.keyline_of(p_seg))
	mat.set_shader_parameter(&"time", clock)
	if int(m["kind"]) == RingMods.Kind.GLYPH:
		_set_cell(StringName(m["glyph"]))
	# only PIERCE and CORRUPT move, and only while the screens' loop runs
	set_process(int(m["kind"]) != RingMods.Kind.GLYPH and clock_source != null and clock_source.is_processing())


## No wedge (a blank segment, no ring, a beaten wheel).
func hide_mod() -> void:
	seg_id = &""
	visible = false
	set_process(false)
	mat.set_shader_parameter(&"mod", RingMods.NONE)


## Whether the wedge covers the compass angle `deg` (degrees) at master radius `r`: the shader's band test
## (r_in..r_out, the radial edges inset), so tests can check what it covers.
func covers(r: float, deg: float) -> bool:
	if not visible or seg_id == &"":
		return false
	var d := absf(wrapf(deg - a_mid, -180.0, 180.0))
	return r >= RingMods.WEDGE_R_IN and r <= RingMods.WEDGE_R_OUT \
		and deg_to_rad(d) * r <= deg_to_rad(half_span) * r - RingMods.WEDGE_INSET


func _set_cell(glyph_key: StringName) -> void:
	var t := WheelGlyphs.table()
	var region := t.cell_region(t.glyph_for(glyph_key))
	if t.atlas == null or not region.has_area():
		return
	var asz := Vector2(t.atlas.get_size())
	mat.set_shader_parameter(&"atlas", t.atlas)
	mat.set_shader_parameter(&"cell", Vector4(region.position.x / asz.x, region.position.y / asz.y, region.size.x / asz.x, region.size.y / asz.y))
	mat.set_shader_parameter(&"box_share", float(t.box_px) / float(maxi(1, t.cell_px)))
	mat.set_shader_parameter(&"spread", float(t.spread_px) / float(maxi(1, t.cell_px)))


func _constants() -> void:
	mat.set_shader_parameter(&"r_in", RingMods.WEDGE_R_IN)
	mat.set_shader_parameter(&"r_out", RingMods.WEDGE_R_OUT)
	mat.set_shader_parameter(&"inset", RingMods.WEDGE_INSET)
	mat.set_shader_parameter(&"shade", RingMods.SHADE)
	mat.set_shader_parameter(&"wash", RingMods.WASH)
	mat.set_shader_parameter(&"halo", RingMods.HALO)
	mat.set_shader_parameter(&"pattern", RingMods.PATTERN)
	mat.set_shader_parameter(&"halo_grow", RingMods.HALO_GROW)
	mat.set_shader_parameter(&"halo_blur", RingMods.HALO_BLUR)
	mat.set_shader_parameter(&"read_r", WheelFace.READ_R)
	mat.set_shader_parameter(&"read_radii", RingMods.READ_RADII)
	mat.set_shader_parameter(&"read_feather", RingMods.READ_FEATHER)
	mat.set_shader_parameter(&"read_clear", RingMods.READ_CLEAR)
	mat.set_shader_parameter(&"edge_w", RingMods.EDGE_W)
	mat.set_shader_parameter(&"edge_a", RingMods.EDGE_A)
	mat.set_shader_parameter(&"glow_a", RingMods.EDGE_GLOW_A)
	mat.set_shader_parameter(&"glow_blur", RingMods.EDGE_GLOW_BLUR)
	mat.set_shader_parameter(&"row_lead", RingMods.ROW_LEAD)
	mat.set_shader_parameter(&"pierce_rate", RingMods.PIERCE_ROWS_PER_S)
	mat.set_shader_parameter(&"glitch_rate", RingMods.GLITCH_RATE)
	mat.set_shader_parameter(&"glitch_fill", RingMods.GLITCH_FILL_AT)
	mat.set_shader_parameter(&"glitch_pink_at", RingMods.GLITCH_PINK_AT)
	mat.set_shader_parameter(&"glitch_pink", RingMods.GLITCH_PINK)
	mat.set_shader_parameter(&"seed", RingMods.GLITCH_SEED)
