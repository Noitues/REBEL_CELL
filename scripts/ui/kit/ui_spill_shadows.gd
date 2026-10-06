class_name UiSpillShadows
extends Control
## B1a (M14 integration review D19 "Light spill is missing on panels and stickers over the city";
## round 3 combined_v2; ART_BIBLE v2 §1.2 "World": light spill from glowing elements): the UI's
## light and shade on the world under it. Panels cast a soft drop shadow onto the city
## (`shadow_alpha` black, `shadow_soft_px` soft, dropped by `shadow_offset_px`: the concepts'
## panels sit *on* the world), and emissive UI elements (a neon sign, the pink verb sticker, the
## TARGET pencil) cast an additive spill of `spill_strength` of their colour on the city round
## them, out to `spill_radius_scale` x the element's radius. Numbers: `content/config/
## ui_scrim_look.tres` (UiScrimLook).
##
## It lives inside a UiScrimPools layer (its `spill`), drawn over the pools and under the UI, and
## takes the marks that layer owns (see UiScrimPools for the ownership rule):
##   UiScrimPools.mark_panel(panel)                       # its drop shadow (and its pool)
##   UiSpillShadows.mark_spill(sticker, Palette.CELL_PINK) # spills its colour
##   scrim.spill.add_spill_source(rects_fn, colour)        # () -> Array of Rect2 / polylines
##                                                         # in the layer's canvas global px
##                                                         # (a pencil stroke, a drawn word)
## A spill's strength follows its Control's own `modulate.a` (a sticker fading in spills as it
## shows). Two full-screen quads (shadows in multiply, spill additive), no screen read, uniforms
## set only when something moves; each hidden while it has nothing. City quality tier 0 drops both
## (UiScrimLook tier_spill / tier_shadows). Static: nothing animates (reduce effects and MotionSkip
## have nothing to stop). View only.

const LOOK: UiScrimLook = preload("res://content/config/ui_scrim_look.tres")
const SHADOW_SHADER := preload("res://shaders/kit/ui_panel_shadows.gdshader")
const SPILL_SHADER := preload("res://shaders/kit/ui_light_spill.gdshader")
## The shaders' array sizes (MAX_SHADOWS, MAX_SPILLS).
const MAX_SHADOWS := 24
const MAX_SPILLS := 16
const NODE_NAME := "SpillShadows"
const SPILL_GROUP := &"ui_scrim_spill"
const META_COLOR := &"ui_spill_color"
const META_STRENGTH := &"ui_spill_strength"

## This frame's shadows [{centre, half, soft, alpha}] and spills [{kind, centre, half, reach,
## color, strength}], in the layer's own px (a box: kind 0, its centre and half size; a stroke
## segment: kind 1, its two ends in `centre` and `half`).
var shadows: Array[Dictionary] = []
var spills: Array[Dictionary] = []

var _shadow_quad: ColorRect
var _spill_quad: ColorRect
var _shadow_mat: ShaderMaterial
var _spill_mat: ShaderMaterial
var _sources: Array[Dictionary] = []
var _shadow_sig: int = 0
var _spill_sig: int = 0


func _init() -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_shadow_mat = ShaderMaterial.new()
	_shadow_mat.shader = SHADOW_SHADER
	_spill_mat = ShaderMaterial.new()
	_spill_mat.shader = SPILL_SHADER
	_shadow_quad = _quad("Shadows", _shadow_mat)
	_spill_quad = _quad("Spill", _spill_mat)


func _quad(n: String, mat: ShaderMaterial) -> ColorRect:
	var q := ColorRect.new()
	q.name = n
	q.mouse_filter = Control.MOUSE_FILTER_IGNORE
	q.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	q.material = mat
	q.visible = false
	add_child(q)
	return q


## Marks `c` as emissive: it spills `color` on the world round it, at `strength` (< 0: the look's
## spill_strength).
static func mark_spill(c: Control, color: Color, strength: float = -1.0) -> void:
	c.set_meta(META_COLOR, color)
	c.set_meta(META_STRENGTH, strength)
	c.add_to_group(SPILL_GROUP)


## Marks every pink VerbSticker under `root` (the screen's one pink verb: JACK IN, START
## DEFENSE...) as spilling the Cell's pink.
static func mark_verb_stickers_in(root: Node) -> void:
	for v in root.find_children("*", "VerbSticker", true, false):
		if (v as VerbSticker).fill == VerbSticker.Fill.PINK:
			mark_spill(v as Control, Palette.CELL_PINK)


## Adds a spill source that is not a Control: `rects` () -> Array of Rect2 (a box) or
## PackedVector2Array (a pencil stroke: it lights `line_glow_px` round the line), in the layer's
## canvas global px (empty: nothing now), each spilling `color` at `strength` (< 0: the look's).
func add_spill_source(rects: Callable, color: Color, strength: float = -1.0) -> void:
	_sources.append({"rects": rects, "color": color, "strength": strength})


## True when the city quality tier draws the spill / the shadows.
static func spill_on() -> bool:
	return UiScrimLook.flag_at(LOOK.tier_spill, CityView3D.CONFIG.tier_for(Settings.city_quality))


static func shadows_on() -> bool:
	return UiScrimLook.flag_at(LOOK.tier_shadows, CityView3D.CONFIG.tier_for(Settings.city_quality))


func _scrim() -> UiScrimPools:
	return get_parent() as UiScrimPools


func _process(_delta: float) -> void:
	refresh()


## Reads the marked rects now and updates both shaders (each frame; tests call it directly).
func refresh() -> void:
	var scrim := _scrim()
	shadows = _gather_shadows(scrim) if scrim != null and shadows_on() else ([] as Array[Dictionary])
	spills = _gather_spills(scrim) if scrim != null and spill_on() else ([] as Array[Dictionary])
	_push_shadows()
	_push_spills()


func _gather_shadows(scrim: UiScrimPools) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	var drop := Vector2(scrim.px(LOOK.shadow_offset_px.x), scrim.px(LOOK.shadow_offset_px.y))
	for c in scrim.owned(UiScrimPools.PANEL_GROUP):
		if not bool(c.get_meta(UiScrimPools.META_SHADOW, true)):
			continue
		var r := scrim.local_rect(c)
		out.append({"centre": r.get_center() + drop, "half": r.size * 0.5, "soft": scrim.px(LOOK.shadow_soft_px),
			"alpha": LOOK.shadow_alpha})
		if out.size() >= MAX_SHADOWS:
			break
	return out


func _gather_spills(scrim: UiScrimPools) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for c in scrim.owned(SPILL_GROUP):
		var st := float(c.get_meta(META_STRENGTH, -1.0))
		out.append(_spill(scrim.local_rect(c), c.get_meta(META_COLOR, Palette.CELL_PINK), (LOOK.spill_strength if st < 0.0 else st) * c.modulate.a))
	if not _sources.is_empty() and scrim.is_inside_tree():
		var inv := scrim.get_global_transform().affine_inverse()
		for s in _sources:
			var fn: Callable = s["rects"]
			if not fn.is_valid():
				continue
			var st := LOOK.spill_strength if float(s["strength"]) < 0.0 else float(s["strength"])
			for item in fn.call():
				if item is Rect2:
					out.append(_spill(inv * (item as Rect2), s["color"], st))
				elif item is PackedVector2Array:
					out.append_array(_line_spills(inv * (item as PackedVector2Array), s["color"], st, scrim.px(LOOK.line_glow_px)))
	if out.size() > MAX_SPILLS:
		out.resize(MAX_SPILLS)
	return out


## A spill of `color` round element `r`: it reaches (spill_radius_scale - 1) x the element's radius
## (half its diagonal) past the element's edge.
static func _spill(r: Rect2, color: Color, strength: float) -> Dictionary:
	var radius := r.size.length() * 0.5
	return {"kind": 0, "centre": r.get_center(), "half": r.size * 0.5, "reach": maxf(radius * (LOOK.spill_radius_scale - 1.0), 0.001),
		"color": color, "strength": clampf(strength, 0.0, 1.0)}


## A pencil stroke's spill: the polyline cut into at most `line_segments` segments, each lighting
## the world out to `reach` px from the line.
static func _line_spills(pts: PackedVector2Array, color: Color, strength: float, reach: float) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if pts.size() < 2:
		return out
	var n := mini(maxi(LOOK.line_segments, 1), pts.size() - 1)
	for i in n:
		var a := pts[int(float(i) * float(pts.size() - 1) / float(n))]
		var b := pts[int(float(i + 1) * float(pts.size() - 1) / float(n))]
		out.append({"kind": 1, "centre": a, "half": b, "reach": maxf(reach, 0.001), "color": color, "strength": clampf(strength, 0.0, 1.0)})
	return out


func _push_shadows() -> void:
	var sig := hash(shadows)
	_shadow_quad.visible = not shadows.is_empty()
	if sig == _shadow_sig:
		return
	_shadow_sig = sig
	var rects := PackedVector4Array()
	var params := PackedVector4Array()
	rects.resize(MAX_SHADOWS)
	params.resize(MAX_SHADOWS)
	for i in shadows.size():
		var s: Dictionary = shadows[i]
		var c: Vector2 = s["centre"]
		var h: Vector2 = s["half"]
		rects[i] = Vector4(c.x, c.y, h.x, h.y)
		params[i] = Vector4(0.0, float(s["soft"]), float(s["alpha"]), 0.0)
	_shadow_mat.set_shader_parameter(&"count", shadows.size())
	_shadow_mat.set_shader_parameter(&"shadow_rect", rects)
	_shadow_mat.set_shader_parameter(&"shadow_params", params)


func _push_spills() -> void:
	var sig := hash(spills)
	_spill_quad.visible = not spills.is_empty()
	if sig == _spill_sig:
		return
	_spill_sig = sig
	var rects := PackedVector4Array()
	var cols := PackedVector4Array()
	var params := PackedVector4Array()
	rects.resize(MAX_SPILLS)
	cols.resize(MAX_SPILLS)
	params.resize(MAX_SPILLS)
	for i in spills.size():
		var s: Dictionary = spills[i]
		var c: Vector2 = s["centre"]
		var h: Vector2 = s["half"]
		var col: Color = s["color"]
		rects[i] = Vector4(c.x, c.y, h.x, h.y)
		cols[i] = Vector4(col.r, col.g, col.b, float(s["strength"]))
		params[i] = Vector4(float(s["reach"]), 0.0, float(s["kind"]), 0.0)
	_spill_mat.set_shader_parameter(&"count", spills.size())
	_spill_mat.set_shader_parameter(&"spill_rect", rects)
	_spill_mat.set_shader_parameter(&"spill_color", cols)
	_spill_mat.set_shader_parameter(&"spill_params", params)


## What the shadows leave of the world at `p` (the layer's own px), as the shader computes it.
func shadow_at(p: Vector2) -> float:
	var s := 0.0
	for sh in shadows:
		var d := maxf(UiScrimPools.sd_box(p - (sh["centre"] as Vector2), sh["half"], 0.0), 0.0)
		var k := clampf(1.0 - d / maxf(float(sh["soft"]), 0.001), 0.0, 1.0)
		s = maxf(s, float(sh["alpha"]) * k * k)
	return 1.0 - s


## The light the spill adds at `p` (the layer's own px), as the shader computes it.
func spill_at(p: Vector2) -> Color:
	var add := Vector3.ZERO
	for sp in spills:
		var d: float
		var m := 0.0
		if int(sp["kind"]) == 1:
			d = p.distance_to(Geometry2D.get_closest_point_to_segment(p, sp["centre"], sp["half"]))
		else:
			var half: Vector2 = sp["half"]
			m = minf(half.x, half.y)
			d = UiScrimPools.sd_box(p - (sp["centre"] as Vector2), half, m)
		var k := clampf(1.0 - (d + m) / maxf(float(sp["reach"]) + m, 0.001), 0.0, 1.0)
		var c: Color = sp["color"]
		var w := float(sp["strength"]) * k * k
		add = (add + Vector3(c.r, c.g, c.b) * w).min(Vector3.ONE)
	return Color(add.x, add.y, add.z)
