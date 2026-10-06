class_name UiScrimPools
extends Control
## B1a (M14 integration review D1, section d "World darkening under the UI"; ART_BIBLE v2 §3.1,
## §4.1): the one layer between the world (the 3D city, a backdrop still, the 2D city) and the UI
## that darkens the world under the UI. The concepts drop the city round the wheels, the hand and
## the panels and lay darker bands under the bars; this layer does it for every screen over the
## city: soft pools round the registered wheels (`wheel_pool_multiply`, a soft disc of
## `wheel_pool_reach` x the disc radius, its edge `wheel_pool_soft` of that wide) and panels (`panel_pool_multiply`, fading over
## `panel_pool_margin_px` past the edge), and bands under the registered bars (`band_multiply`,
## fading over `band_reach_top_px` / `band_reach_bottom_px`). Numbers: `content/config/
## ui_scrim_look.tres` (UiScrimLook). Its child `spill` (UiSpillShadows) draws the panels' drop
## shadows and the emissive elements' light spill on the same world, above the pools.
##
## How a screen uses it (the API other screens use; DECISIONS "B1a"):
##   var scrim := UiScrimPools.attach_after(background)   # right after the world node
##   scrim.add_wheels(_views)                              # combat: () -> Array of WheelViews
##   UiScrimPools.mark_panel(site_card)                    # pool + drop shadow under a panel
##   UiScrimPools.mark_panel(sheet, false)                 # drop shadow only (no pool)
##   UiScrimPools.mark_band(hud, SIDE_TOP)                 # a dark band under a bar
##   UiSpillShadows.mark_spill(jack_in, Palette.CELL_PINK) # an emissive element lights the city
## Marks live on the Control (groups + metas), so a page marks its parts where it builds them,
## without holding the layer; a mark is taken by the nearest layer whose host (its parent) holds
## the Control and that is drawn before it (a fight inside a netrun page belongs to the fight's
## own layer, not the run's). Each frame the layer reads the rects of the visible marked Controls
## (bounding boxes in its own space, any CanvasLayer), so pages that move, scroll, slide in or
## hide need nothing more; a freed Control simply drops out.
##
## Cost: one full-screen quad in multiply (no screen read), its uniforms set only when a rect
## changes; hidden while nothing is registered. Static: nothing animates, so reduce effects and
## MotionSkip have nothing to stop (its end state is its only state); VfxTier T0 (backdrop
## coverage, no flash). City quality tier 0 keeps the pools (they carry the UI's contrast) and
## drops the spill and the shadows (UiScrimLook tier flags). View only: it never changes a
## Control it reads, nor any state.

const LOOK: UiScrimLook = preload("res://content/config/ui_scrim_look.tres")
const SHADER := preload("res://shaders/kit/ui_scrim_pools.gdshader")
## Shapes the shader takes (its MAX_SHAPES).
const MAX_SHAPES := 32
const NODE_NAME := "UiScrimPools"
## Marks (groups on the marked Controls) and their metas.
const PANEL_GROUP := &"ui_scrim_panel"
const BAND_GROUP := &"ui_scrim_band"
const META_POOL := &"ui_scrim_pool"
const META_SHADOW := &"ui_scrim_shadow"
const META_SIDE := &"ui_scrim_side"
## The meta on a layer's host naming its layer (instance id).
const HOST_META := &"ui_scrim_host"

## Shape kinds (the shader's params.x).
enum Kind { DISC, RECT, BAND }

## The light spill and panel shadows over the pools.
var spill: UiSpillShadows
## The shapes this frame, in this layer's own px: [{kind, centre, half, corner, reach, removal}]
## (a disc's `corner` holds its edge's softness, a share of its reach).
var shapes: Array[Dictionary] = []

var _quad: ColorRect
var _mat: ShaderMaterial
var _wheel_sources: Array[Callable] = []
var _sig: int = 0


func _init() -> void:
	name = NODE_NAME
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	focus_mode = Control.FOCUS_NONE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_mat = ShaderMaterial.new()
	_mat.shader = SHADER
	_mat.set_shader_parameter(&"falloff", LOOK.pool_falloff)
	_quad = ColorRect.new()
	_quad.name = "Pools"
	_quad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_quad.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_quad.material = _mat
	_quad.visible = false
	add_child(_quad)
	spill = UiSpillShadows.new()
	add_child(spill)


func _enter_tree() -> void:
	get_parent().set_meta(HOST_META, get_instance_id())


func _exit_tree() -> void:
	var host := get_parent()
	if host != null and host.has_meta(HOST_META) and int(host.get_meta(HOST_META)) == get_instance_id():
		host.remove_meta(HOST_META)


## Makes a layer and puts it right after `world` (same parent: drawn over the world, under every
## UI sibling after it). Returns it.
static func attach_after(world: Node) -> UiScrimPools:
	var s := UiScrimPools.new()
	var host := world.get_parent()
	host.add_child(s)
	host.move_child(s, world.get_index() + 1)
	return s


## Registers the wheels `source` returns (() -> Array of WheelViews, or anything with
## `global_center()` and `disc_radius()` in its canvas' global px); each visible one with a
## combatant gets a pool.
func add_wheels(source: Callable) -> void:
	if source.is_valid() and not _wheel_sources.has(source):
		_wheel_sources.append(source)


## Marks `c` as a panel over the world: a pool under it (`pool`) and a drop shadow (`shadow`).
static func mark_panel(c: Control, pool: bool = true, shadow: bool = true) -> void:
	c.set_meta(META_POOL, pool)
	c.set_meta(META_SHADOW, shadow)
	c.add_to_group(PANEL_GROUP)


## Marks `c` as a bar with a dark band under it, reaching to the screen's `side` edge
## (SIDE_TOP or SIDE_BOTTOM).
static func mark_band(c: Control, side: Side) -> void:
	c.set_meta(META_SIDE, side)
	c.add_to_group(BAND_GROUP)


## Marks every Control under `root` (itself included) that is one of `classes` (class names) as a
## panel (see mark_panel), the outermost only: a window inside a marked window is not marked
## again. For a page built of shared windows: one line marks them all.
static func mark_panels_in(root: Node, classes: Array[String], pool: bool = true, shadow: bool = true) -> void:
	var found: Array[Node] = []
	for cls in classes:
		if root is Control and _is_class(root, cls):
			found.append(root)
		found.append_array(root.find_children("*", cls, true, false))
	for n in found:
		var nested := false
		for m in found:
			if m != n and m.is_ancestor_of(n):
				nested = true
				break
		if not nested and n is Control:
			mark_panel(n as Control, pool, shadow)


static func _is_class(n: Node, cls: String) -> bool:
	if n.is_class(cls):
		return true
	var s := n.get_script() as Script
	while s != null:
		if s.get_global_name() == StringName(cls):
			return true
		s = s.get_base_script()
	return false


## Takes every mark off `c`.
static func unmark(c: Control) -> void:
	for g in [PANEL_GROUP, BAND_GROUP, UiSpillShadows.SPILL_GROUP]:
		if c.is_in_group(g):
			c.remove_from_group(g)


## True when this layer takes `n`'s mark: `n` is shown, drawn after this layer, and this layer's
## host is the nearest layer host above it.
func owns(n: Node) -> bool:
	if not is_inside_tree() or not n.is_inside_tree() or n == self:
		return false
	if n is CanvasItem and not (n as CanvasItem).is_visible_in_tree():
		return false
	if not n.is_greater_than(self):
		return false
	var p := n.get_parent()
	while p != null:
		if p.has_meta(HOST_META):
			return int(p.get_meta(HOST_META)) == get_instance_id()
		p = p.get_parent()
	return false


## The marked Controls this layer takes in `group`, in tree order.
func owned(group: StringName) -> Array[Control]:
	var out: Array[Control] = []
	if not is_inside_tree():
		return out
	for n in get_tree().get_nodes_in_group(group):
		if n is Control and owns(n):
			out.append(n as Control)
	return out


## `c`'s rect in this layer's own px (its bounding box: a tilted sticker's whole reach).
func local_rect(c: Control) -> Rect2:
	var xf := get_global_transform_with_canvas().affine_inverse() * c.get_global_transform_with_canvas()
	return xf * Rect2(Vector2.ZERO, c.size)


## px at the look's reference height -> this layer's px.
func px(length: float) -> float:
	return length * size.y / maxf(LOOK.reference_height, 1.0)


func _process(_delta: float) -> void:
	refresh()


## Reads the registered rects now and updates the shader (each frame; tests call it directly).
func refresh() -> void:
	shapes = _gather()
	var sig := hash(shapes)
	if sig == _sig and _quad.visible == not shapes.is_empty():
		return
	_sig = sig
	_quad.visible = not shapes.is_empty()
	var rects := PackedVector4Array()
	var params := PackedVector4Array()
	rects.resize(MAX_SHAPES)
	params.resize(MAX_SHAPES)
	for i in shapes.size():
		var s: Dictionary = shapes[i]
		var c: Vector2 = s["centre"]
		var h: Vector2 = s["half"]
		rects[i] = Vector4(c.x, c.y, h.x, h.y)
		params[i] = Vector4(float(s["kind"]), float(s["corner"]), float(s["reach"]), float(s["removal"]))
	_mat.set_shader_parameter(&"count", shapes.size())
	_mat.set_shader_parameter(&"shape_rect", rects)
	_mat.set_shader_parameter(&"shape_params", params)


func _gather() -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	if not is_inside_tree():
		return out
	var inv := get_global_transform_with_canvas().affine_inverse()
	for source in _wheel_sources:
		if not source.is_valid():
			continue
		for v in source.call():
			if not (v is CanvasItem) or not is_instance_valid(v) or not (v as CanvasItem).is_visible_in_tree():
				continue
			if "combatant" in v and v.combatant == null:
				continue
			var xf := inv * (v as CanvasItem).get_canvas_transform()
			var r := float(v.disc_radius()) * xf.get_scale().x
			out.append(_shape(Kind.DISC, xf * (v.global_center() as Vector2), Vector2.ZERO, LOOK.wheel_pool_soft,
				r * LOOK.wheel_pool_reach, 1.0 - LOOK.wheel_pool_multiply))
	for c in owned(PANEL_GROUP):
		if not bool(c.get_meta(META_POOL, true)):
			continue
		var r := local_rect(c)
		out.append(_shape(Kind.RECT, r.get_center(), r.size * 0.5, 0.0, px(LOOK.panel_pool_margin_px),
			1.0 - LOOK.panel_pool_multiply))
	for c in owned(BAND_GROUP):
		var r := local_rect(c)
		var top := int(c.get_meta(META_SIDE, SIDE_TOP)) == SIDE_TOP
		var y0 := minf(0.0, r.position.y) if top else r.position.y
		var y1 := r.end.y if top else maxf(size.y, r.end.y)
		var reach := px(LOOK.band_reach_top_px if top else LOOK.band_reach_bottom_px)
		# Full width and past the sides, so only its inner edge fades.
		out.append(_shape(Kind.BAND, Vector2(size.x * 0.5, (y0 + y1) * 0.5), Vector2(size.x * 0.5 + reach * 2.0, (y1 - y0) * 0.5),
			0.0, reach, 1.0 - LOOK.band_multiply))
	if out.size() > MAX_SHAPES:
		out.resize(MAX_SHAPES)
	return out


static func _shape(kind: Kind, centre: Vector2, half: Vector2, corner: float, reach: float, removal: float) -> Dictionary:
	return {"kind": kind, "centre": centre, "half": half, "corner": corner, "reach": maxf(reach, 0.001), "removal": clampf(removal, 0.0, 1.0)}


## What the layer leaves of the world at `p` (its own px), as the shader computes it: 1.0 where
## nothing is registered.
func factor_at(p: Vector2) -> float:
	var pool := 0.0
	var band := 0.0
	for s in shapes:
		var m: float
		var reach := float(s["reach"])
		if int(s["kind"]) == Kind.DISC:
			m = disc_mask((p - (s["centre"] as Vector2)).length(), reach, float(s["corner"]))
		else:
			var d := maxf(sd_box(p - (s["centre"] as Vector2), s["half"], float(s["corner"])), 0.0)
			m = exp(-pow(d / reach, LOOK.pool_falloff))
		if int(s["kind"]) == Kind.BAND:
			band = maxf(band, float(s["removal"]) * m)
		else:
			pool = maxf(pool, float(s["removal"]) * m)
	return (1.0 - pool) * (1.0 - band)


## What a wheel's pool leaves of the world `d` disc radii from its centre (the look's numbers;
## the combat contrast checks read it).
static func wheel_factor(d: float) -> float:
	var m := disc_mask(d, LOOK.wheel_pool_reach, LOOK.wheel_pool_soft)
	return 1.0 - (1.0 - LOOK.wheel_pool_multiply) * m


## A soft disc of radius `reach`: 1 inside, 0 outside, its edge `soft` x reach wide on each side
## (the shader's disc pool).
static func disc_mask(d: float, reach: float, soft: float) -> float:
	return 1.0 - smoothstep(reach * (1.0 - soft), reach * (1.0 + soft), d)


## The signed distance from `p` to a rounded box of half size `b` and corner `r` (the shaders').
static func sd_box(p: Vector2, b: Vector2, r: float) -> float:
	var q := p.abs() - b + Vector2(r, r)
	return Vector2(maxf(q.x, 0.0), maxf(q.y, 0.0)).length() + minf(maxf(q.x, q.y), 0.0) - r
